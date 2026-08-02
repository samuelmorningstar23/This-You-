"""Identity resolution: the consent-based replacement for stranger face search.

These tests exist to pin down the properties that make this lawful and safe, not
just working. Each one corresponds to a failure mode from the research.
"""

from __future__ import annotations

import time

import pytest

from edith.identity import (
    ROTATION_S,
    Advertisement,
    Roster,
    SharedSecretSigner,
    derive_handle,
)
from edith.types import Assurance


def paired(disclosed=None):
    roster = Roster()
    contact = roster.pair("mj", "MJ", disclosed=disclosed or {})
    now = time.time()
    handle = derive_handle(contact.secret, int(now // ROTATION_S))
    return roster, contact, handle


def test_an_unpaired_stranger_is_never_named():
    """The whole point. A stranger yields a handle and nothing else."""
    roster = Roster()
    peer = roster.resolve(Advertisement(handle="deadbeefdeadbeef", ranged_m=1.2))
    assert peer.display_name is None
    assert peer.disclosed == {}
    assert peer.assurance is Assurance.PROXIMITY


def test_no_api_exists_to_identify_a_face():
    """There is no image-based identification path, by construction."""
    roster = Roster()
    surface = [m for m in dir(roster) if not m.startswith("_")]
    assert surface == ["pair", "resolve", "revoke"]
    for banned in ("identify", "recognise", "recognize", "search", "match_face"):
        assert not any(banned in m for m in surface)


def test_a_paired_contact_who_answers_is_named():
    roster, contact, handle = paired({"team": "robotics"})
    peer = roster.resolve(
        Advertisement(handle=handle, ranged_m=1.0),
        challenge_responder=SharedSecretSigner(contact.secret),
    )
    assert peer.display_name == "MJ"
    assert peer.assurance is Assurance.NAMED
    assert peer.disclosed == {"team": "robotics"}


def test_a_contact_who_does_not_answer_is_not_named():
    """Flat battery, out of range, or revoked all look the same, and all fail closed."""
    roster, _contact, handle = paired()
    peer = roster.resolve(Advertisement(handle=handle, ranged_m=1.0))
    assert peer.display_name is None
    assert peer.assurance is Assurance.PROXIMITY


def test_revocation_takes_effect_immediately_with_no_propagation():
    roster, contact, handle = paired({"team": "robotics"})
    signer = SharedSecretSigner(contact.secret)
    assert roster.resolve(
        Advertisement(handle=handle, ranged_m=1.0), challenge_responder=signer
    ).display_name == "MJ"

    assert roster.revoke("mj") is True

    after = roster.resolve(
        Advertisement(handle=handle, ranged_m=1.0), challenge_responder=signer
    )
    assert after.display_name is None
    assert len(roster) == 0


def test_a_wrong_signature_is_treated_as_an_attack_not_a_near_miss():
    roster, _contact, handle = paired()
    impostor = SharedSecretSigner(b"not-the-right-secret")
    peer = roster.resolve(
        Advertisement(handle=handle, ranged_m=1.0), challenge_responder=impostor
    )
    assert peer.display_name is None
    assert peer.assurance is Assurance.NONE


def test_an_unranged_advertisement_can_still_be_attested_by_signature():
    """The signature is what carries weight; ranging only narrows down who."""
    roster, contact, handle = paired()
    peer = roster.resolve(
        Advertisement(handle=handle, ranged_m=None),
        challenge_responder=SharedSecretSigner(contact.secret),
    )
    assert peer.assurance in (Assurance.ATTESTED, Assurance.NAMED)
    unpaired = roster.resolve(Advertisement(handle="ffffffffffffffff", ranged_m=None))
    assert unpaired.assurance is Assurance.NONE


def test_ranging_alone_never_authorises_anything():
    """Time-of-flight ranging is attackable (Ghost Peak, USENIX Sec '22).

    A perfect distance bound on a paired contact must still not produce a name
    without a signature — otherwise a relay is enough to impersonate someone.
    """
    roster, _contact, handle = paired({"team": "robotics"})
    peer = roster.resolve(Advertisement(handle=handle, ranged_m=0.3))
    assert peer.assurance is Assurance.PROXIMITY
    assert peer.display_name is None
    assert peer.disclosed == {}


def test_a_peer_beyond_range_is_not_treated_as_present():
    roster, _c, handle = paired()
    peer = roster.resolve(Advertisement(handle=handle, ranged_m=50.0))
    assert peer.assurance is Assurance.NONE


def test_handles_rotate_so_a_passive_observer_cannot_track_someone():
    _roster, contact, _handle = paired()
    now = time.time()
    w = int(now // ROTATION_S)
    seen = {derive_handle(contact.secret, w + i) for i in range(8)}
    assert len(seen) == 8, "each rotation window must produce a distinct handle"


def test_handle_matching_tolerates_modest_clock_skew():
    roster = Roster()
    contact = roster.pair("ned", "Ned")
    now = time.time()
    previous_window = derive_handle(contact.secret, int(now // ROTATION_S) - 1)
    peer = roster.resolve(
        Advertisement(handle=previous_window, ranged_m=1.0),
        challenge_responder=SharedSecretSigner(contact.secret),
    )
    assert peer.display_name == "Ned"


@pytest.mark.parametrize("disclosed", [{}, {"role": "colleague"}])
def test_disclosure_is_per_relationship(disclosed):
    roster, contact, handle = paired(disclosed)
    peer = roster.resolve(
        Advertisement(handle=handle, ranged_m=1.0),
        challenge_responder=SharedSecretSigner(contact.secret),
    )
    assert peer.disclosed == disclosed
    expected = Assurance.NAMED if disclosed else Assurance.ATTESTED
    assert peer.assurance is expected
