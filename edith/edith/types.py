"""Core value types passed between sensors, gates, the agent, and outputs.

Everything here is a plain immutable dataclass. The runtime moves these over
asyncio queues, so they must be cheap to construct and safe to share.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Literal


def _now() -> float:
    return time.monotonic()


def _uid() -> str:
    return uuid.uuid4().hex[:12]


# --------------------------------------------------------------------------
# Sensor input
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class AudioChunk:
    """A short window of mono PCM audio from the glasses' microphone array."""

    pcm: bytes
    sample_rate: int
    ts: float = field(default_factory=_now)

    @property
    def duration_s(self) -> float:
        # 16-bit mono
        return len(self.pcm) / 2 / self.sample_rate


@dataclass(frozen=True)
class Utterance:
    """Speech that has been segmented and transcribed.

    ``directed`` means the speech was aimed at the assistant (wake word, gaze +
    voice, or an explicit tap) rather than overheard conversation. Overheard
    speech never triggers a turn on its own; it is context only, and only when
    the wearer has enabled ambient capture.
    """

    text: str
    directed: bool
    confidence: float = 1.0
    speaker: str | None = None
    ts: float = field(default_factory=_now)


@dataclass(frozen=True)
class Frame:
    """A single camera frame plus a cheap perceptual signature.

    ``thumb`` is a tiny grayscale thumbnail (default 16x16) produced by the
    device. The vision gate works on ``thumb`` alone, which is what keeps the
    system from paying to look at a wall for eight hours. ``jpeg`` is the full
    frame and is only materialised when the gate decides a frame is worth
    sending — on real hardware the device can defer the JPEG encode entirely.
    """

    thumb: bytes
    width: int
    height: int
    jpeg: bytes | None = None
    ts: float = field(default_factory=_now)


@dataclass(frozen=True)
class Fix:
    """A coarse location fix. Deliberately coarse: street-level, not metre-level."""

    lat: float
    lon: float
    accuracy_m: float
    label: str | None = None
    ts: float = field(default_factory=_now)


# --------------------------------------------------------------------------
# Identity (see edith/identity.py — resolution, never recognition)
# --------------------------------------------------------------------------


class Assurance(StrEnum):
    """How strongly a nearby peer's claimed identity is backed.

    The jump that matters is PROXIMITY -> ATTESTED. Everything below ATTESTED is
    an unverified claim: a distance bound narrows down *which* nearby person a
    signature will belong to, but it is not itself evidence of anything, because
    time-of-flight ranging is attackable (see identity.py on Ghost Peak).
    """

    NONE = "none"  # an advertisement, with nothing behind it
    PROXIMITY = "proximity"  # + a distance bound: useful for disambiguation only
    ATTESTED = "attested"  # + a live signature over our nonce — the first real tier
    NAMED = "named"  # + an attribute they chose to disclose to you


@dataclass(frozen=True)
class Peer:
    """Someone nearby who is broadcasting a resolvable, revocable presence.

    This is the consent-based replacement for E.D.I.T.H.'s stranger
    facial-recognition. A person who has not opted in does not appear here at
    all — there is no code path that turns an unenrolled face into an identity.
    """

    handle: str  # rotating pseudonym, not a stable identifier
    assurance: Assurance
    distance_m: float | None = None
    display_name: str | None = None
    disclosed: dict[str, str] = field(default_factory=dict)
    ts: float = field(default_factory=_now)


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------


Priority = Literal["ambient", "normal", "urgent"]


@dataclass(frozen=True)
class Speak:
    """Text destined for the bone-conduction / open-ear speaker."""

    text: str
    priority: Priority = "normal"
    interruptible: bool = True


@dataclass(frozen=True)
class Card:
    """A glanceable heads-up display card.

    Kept deliberately small: a title and at most a few short lines. Every
    shipping monocular display in 2026 is a narrow text strip, so the output
    contract is text, not a world-locked hologram.
    """

    title: str
    lines: tuple[str, ...] = ()
    ttl_s: float = 6.0
    priority: Priority = "normal"
    id: str = field(default_factory=_uid)

    def __post_init__(self) -> None:
        if len(self.lines) > 4:
            raise ValueError("a HUD card holds at most 4 lines; summarise further")


@dataclass(frozen=True)
class Turn:
    """One completed interaction, for the episodic log."""

    prompt: str
    reply: str
    trigger: str
    tools_used: tuple[str, ...] = ()
    saw_frame: bool = False
    latency_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    ts: float = field(default_factory=_now)


@dataclass(frozen=True)
class ToolCall:
    name: str
    args: dict[str, Any]
    id: str = field(default_factory=_uid)


@dataclass(frozen=True)
class ToolResult:
    call_id: str
    content: str
    is_error: bool = False
