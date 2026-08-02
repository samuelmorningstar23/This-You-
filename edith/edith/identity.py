"""Resolving who is in front of you — by consent, not by recognition.

E.D.I.T.H.'s defining move is looking at a stranger and pulling up their name,
their school records, and their phone. That single capability is the reason the
film's own characters treat the glasses as dangerous, and in 2026 it is the
capability that would end a company — see policy.py for the citations.

The interesting part is that the *useful* half of that capability survives the
legal constraint completely intact, if you invert who is doing the asserting.

Recognition asks: "whose face is this?" — a question answered by a database
built from people who never agreed to be in it.

Resolution asks: "is there someone here who will tell me who they are?" — a
question answered by that person's own device, live, and revocably.

That inversion is not a workaround; the law already draws the line in the same
place. EU AI Act Annex III classes remote biometric *identification* as
high-risk while explicitly excluding systems "intended to be used for biometric
verification the sole purpose of which is to confirm that a specific natural
person is the person he or she claims to be". Identification searches a
population for a face. Verification checks a claim its subject is making about
themselves. Everything below is verification, which is why it lands on the
permitted side of a line that was drawn without us in mind.

This module implements resolution, and it is a direct application of the
Presence Resolution Protocol in this repository's SOLUTION.md. The properties
that matter carry over one for one:

* **Nothing is carried.** A peer's broadcast handle rotates on a short interval
  and is meaningless to anyone who has not been paired with them. There is no
  durable identifier to scrape, correlate, or subpoena.
* **Resolution is live.** A handle only becomes a name when the peer's device
  answers a fresh challenge. Revocation is therefore instant and needs no
  propagation: a device that stops answering stops being resolvable, now.
* **Assurance is graded, not binary.** Seeing an advertisement is weak. A
  distance bound narrows it. A signature over our nonce is the first thing that
  actually means something. Callers ask for the minimum they need.
* **Ranging disambiguates; it does not authorise.** It is tempting to treat
  ultra-wideband time-of-flight as unspoofable, and that is wrong: the Ghost
  Peak attack (Leu et al., USENIX Security 2022) is an over-the-air
  distance-reduction attack on 802.15.4z that collapsed a real 12 m separation
  to a reported 0 m against Apple's U1, with roughly $65 of hardware. So ranging
  answers "which of the five people in front of me signed my nonce", which is a
  genuinely useful question. It never answers "should I believe them". Only the
  signature does that, which is why ATTESTED is the first tier that carries any
  weight and PROXIMITY carries none.

Cryptography note, stated honestly: pairing here establishes a shared secret and
challenges are answered with HMAC-SHA256. That is sound for a mutually-paired
relationship and keeps this module dependency-free, but it is symmetric — a
stolen roster lets you impersonate the peers in it. Production keys belong in
the device's secure enclave as Ed25519 keypairs, gated by a local biometric, so
that the roster holds only public keys. The ``Signer`` seam below is where that
substitution happens; nothing else in the system changes.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from dataclasses import dataclass, field
from typing import Protocol

from .types import Assurance, Peer

#: How often a peer's broadcast handle rotates. Short enough that a passive
#: observer cannot use it to track someone across a day.
ROTATION_S = 900.0

#: Clock skew tolerance, expressed in rotation windows.
_SKEW_WINDOWS = 1


class Signer(Protocol):
    """A peer's ability to answer a live challenge.

    In production this is backed by the peer's secure enclave and gated by their
    on-device biometric, so an answer means "this person is present and
    consenting right now" rather than "this key exists somewhere".
    """

    def sign(self, challenge: bytes) -> bytes: ...


@dataclass(frozen=True)
class SharedSecretSigner:
    """Reference signer for tests and the simulator. See the module note."""

    secret: bytes

    def sign(self, challenge: bytes) -> bytes:
        return hmac.new(self.secret, challenge, hashlib.sha256).digest()


@dataclass
class Contact:
    """Someone the wearer has paired with, and what they agreed to share."""

    display_name: str
    secret: bytes
    #: Attributes this contact chose to disclose to *this* wearer. Selective
    #: disclosure is per-relationship: your colleague may share their team, your
    #: doctor their credential, a stranger at a conference only a first name.
    disclosed: dict[str, str] = field(default_factory=dict)
    revoked: bool = False

    def handles(self, now: float) -> set[str]:
        """The handles this contact could legitimately be broadcasting."""
        window = int(now // ROTATION_S)
        out = set()
        for w in range(window - _SKEW_WINDOWS, window + _SKEW_WINDOWS + 1):
            out.add(derive_handle(self.secret, w))
        return out


def derive_handle(secret: bytes, window: int) -> str:
    """Rotating pseudonym for a pairing, in the style of Exposure Notification RPIs."""
    mac = hmac.new(secret, b"edith-handle|%d" % window, hashlib.sha256).digest()
    return mac[:8].hex()


@dataclass(frozen=True)
class Advertisement:
    """What the radio actually hears: a rotating handle and a range estimate."""

    handle: str
    #: Metres, from UWB time-of-flight. ``None`` means we only have RSSI, which
    #: we deliberately refuse to treat as a distance bound.
    ranged_m: float | None = None
    ts: float = field(default_factory=time.time)


class Roster:
    """The wearer's paired contacts, and the resolution logic over them.

    The whole surface is deliberately small. There is no ``identify(image)`` and
    there is no path that produces one: an unenrolled person yields, at most, an
    unresolvable handle, and usually nothing at all.
    """

    def __init__(self) -> None:
        self._contacts: dict[str, Contact] = {}

    # -- pairing ---------------------------------------------------------

    def pair(
        self,
        contact_id: str,
        display_name: str,
        *,
        secret: bytes | None = None,
        disclosed: dict[str, str] | None = None,
    ) -> Contact:
        """Establish a mutual pairing. In the real flow this is an in-person
        ceremony — a QR scan or an NFC tap — so that pairing itself requires
        physical co-presence and cannot be done to someone remotely."""
        contact = Contact(
            display_name=display_name,
            secret=secret or os.urandom(32),
            disclosed=dict(disclosed or {}),
        )
        self._contacts[contact_id] = contact
        return contact

    def revoke(self, contact_id: str) -> bool:
        """Stop resolving this contact, immediately and locally.

        Revocation needs no network round trip and no cache expiry, because
        nothing durable was ever issued. This is the property that carried
        credentials — the $20 resold World ID in RESEARCH.md — cannot have.
        """
        c = self._contacts.get(contact_id)
        if c is None:
            return False
        c.revoked = True
        return True

    def __len__(self) -> int:
        return sum(1 for c in self._contacts.values() if not c.revoked)

    # -- resolution ------------------------------------------------------

    def resolve(
        self,
        ad: Advertisement,
        *,
        challenge_responder: Signer | None = None,
        now: float | None = None,
        max_range_m: float = 8.0,
    ) -> Peer:
        """Turn a radio advertisement into a graded, possibly-named Peer.

        ``challenge_responder`` stands in for the live round trip to the peer's
        device. Passing ``None`` models a device that did not answer — which is
        exactly what revocation, a flat battery, or a relay attack all look
        like, and all three correctly fail to produce a name.
        """
        now = time.time() if now is None else now

        match_id: str | None = None
        for cid, contact in self._contacts.items():
            if contact.revoked:
                continue
            if ad.handle in contact.handles(now):
                match_id = cid
                break

        # Assurance from the radio alone. Note this tops out at PROXIMITY no
        # matter how good the ranging is: a distance bound tells you where to
        # look, not whom to believe.
        if ad.ranged_m is not None and ad.ranged_m <= max_range_m:
            assurance = Assurance.PROXIMITY
        else:
            # RSSI-only, out of range, or unranged: an advertisement is just a
            # claim. It never rises above NONE on its own.
            assurance = Assurance.NONE

        if match_id is None:
            # Not someone we are paired with. This is where E.D.I.T.H. would
            # reach for a face database. We stop here, on purpose.
            return Peer(handle=ad.handle, assurance=assurance, distance_m=ad.ranged_m)

        contact = self._contacts[match_id]

        if challenge_responder is None:
            return Peer(handle=ad.handle, assurance=assurance, distance_m=ad.ranged_m)

        nonce = os.urandom(16)
        challenge = b"edith-resolve|" + ad.handle.encode() + b"|" + nonce
        expected = hmac.new(contact.secret, challenge, hashlib.sha256).digest()
        answer = challenge_responder.sign(challenge)
        if not hmac.compare_digest(expected, answer):
            # Someone is replaying or relaying. Refuse to name them.
            return Peer(
                handle=ad.handle,
                assurance=Assurance.NONE,
                distance_m=ad.ranged_m,
            )

        # A live answer. Only now does a handle become a person, and only the
        # attributes they chose to disclose to this wearer.
        return Peer(
            handle=ad.handle,
            assurance=Assurance.NAMED if contact.disclosed else Assurance.ATTESTED,
            distance_m=ad.ranged_m,
            display_name=contact.display_name,
            disclosed=dict(contact.disclosed),
        )
