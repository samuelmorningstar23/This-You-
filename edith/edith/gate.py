"""Deciding when the assistant is allowed to look.

This is the most important cost-control component in the system, and the reason
a wearable assistant is affordable at all.

Naively streaming camera frames to a multimodal model is not expensive, it is
absurd. A high-resolution frame costs up to ~4.8K input tokens on the current
Opus-class models. At one frame per second for an eight-hour day that is
roughly 138M input tokens — about $690 per wearer per day at $5/MTok. Nobody is
shipping that.

The fix is that almost every frame is worthless. The wearer is looking at a
wall, a pavement, the back of someone's head, or the same laptop screen they
were looking at ten seconds ago. So the gate answers a cheap question — "has
anything changed, and is the camera steady?" — using a 16x16 grayscale
thumbnail the device produces for free, and only escalates to a real frame when
the answer is yes.

Three rules, in order of authority:

1. An explicit ask always wins. If the wearer says "what am I looking at",
   we look, regardless of budget.
2. Motion suppresses capture. A frame taken mid-head-turn is blurred and
   useless; we wait for the scene to settle rather than paying for a smear.
3. A token budget is a hard ceiling, not a suggestion. When it is spent,
   proactive looking stops and only explicit asks get through.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .types import Frame


def thumb_distance(a: bytes, b: bytes) -> float:
    """Mean absolute difference between two equal-length grayscale thumbnails.

    Returns 0.0 (identical) to 1.0 (maximally different). Operating on a 256-byte
    thumbnail makes this a few microseconds of pure Python, so it can run on
    every frame without a budget of its own.
    """
    if not a or not b:
        return 1.0
    if len(a) != len(b):
        return 1.0
    total = 0
    for x, y in zip(a, b, strict=True):
        total += x - y if x > y else y - x
    return total / (len(a) * 255.0)


@dataclass
class GateConfig:
    #: Thumbnail distance above which the scene counts as "changed".
    change_threshold: float = 0.06
    #: Above this, the camera is moving too much for a usable frame.
    motion_threshold: float = 0.22
    #: The scene must be this stable, for this long, before we capture.
    settle_s: float = 0.4
    #: Never capture proactively more often than this.
    min_interval_s: float = 8.0
    #: Proactive captures allowed per rolling hour.
    hourly_budget: int = 40


@dataclass
class GateDecision:
    look: bool
    reason: str
    #: Estimated input tokens if this frame is sent, for budget accounting.
    est_tokens: int = 0


@dataclass
class VisionGate:
    """Stateful gate. Feed it every frame; it tells you which are worth sending."""

    config: GateConfig = field(default_factory=GateConfig)
    _last_thumb: bytes | None = field(default=None, repr=False)
    _last_sent_thumb: bytes | None = field(default=None, repr=False)
    _last_capture_at: float = 0.0
    _stable_since: float | None = None
    _captures: list[float] = field(default_factory=list)

    # Roughly what a downscaled frame costs on a current Opus-class model.
    # We downscale before sending precisely so this is ~1.1K and not ~4.8K.
    EST_TOKENS_PER_FRAME = 1_100

    def _prune(self, now: float) -> None:
        cutoff = now - 3600.0
        self._captures = [t for t in self._captures if t >= cutoff]

    def budget_remaining(self, now: float | None = None) -> int:
        now = time.monotonic() if now is None else now
        self._prune(now)
        return max(0, self.config.hourly_budget - len(self._captures))

    def note_capture(self, now: float | None = None) -> None:
        """Record a capture that happened outside :meth:`consider`.

        Used by the explicit-ask path, where the wearer's question authorises the
        frame directly and the gate only needs to know it was spent.
        """
        now = time.monotonic() if now is None else now
        self._captures.append(now)
        self._last_capture_at = now
        self._last_sent_thumb = self._last_thumb

    def _commit(self, frame: Frame, reason: str) -> GateDecision:
        """A ``look`` decision spends the budget as it is made.

        Making the caller report back with ``note_capture`` was a footgun: a
        caller that forgot left ``_last_sent_thumb`` empty, so every subsequent
        frame looked novel and a wearer staring at one desk was billed for
        dozens of identical looks. The gate is the authority on whether a frame
        is worth money, so it does its own accounting.
        """
        self._captures.append(frame.ts)
        self._last_capture_at = frame.ts
        self._last_sent_thumb = frame.thumb
        return GateDecision(True, reason, self.EST_TOKENS_PER_FRAME)

    def consider(self, frame: Frame, *, explicit: bool = False) -> GateDecision:
        """Decide whether ``frame`` is worth spending a vision call on.

        A ``look=True`` result is a commitment: the budget is debited here, so
        the caller must act on it.
        """
        cfg = self.config
        now = frame.ts
        prev, self._last_thumb = self._last_thumb, frame.thumb

        if explicit:
            # The wearer asked. Steadiness still matters — a blurred answer is a
            # wrong answer — but budget does not.
            return self._commit(frame, "explicit request")

        if prev is None:
            self._stable_since = now
            return GateDecision(False, "first frame; no baseline")

        motion = thumb_distance(prev, frame.thumb)
        if motion > cfg.motion_threshold:
            self._stable_since = None
            return GateDecision(False, f"camera moving (motion {motion:.3f})")

        if self._stable_since is None:
            self._stable_since = now
        settled_for = now - self._stable_since
        if settled_for < cfg.settle_s:
            return GateDecision(False, f"settling ({settled_for:.2f}s)")

        since_last = now - self._last_capture_at
        if since_last < cfg.min_interval_s:
            return GateDecision(False, f"rate limited ({since_last:.1f}s since last)")

        if self.budget_remaining(now) <= 0:
            return GateDecision(False, "hourly vision budget spent")

        # Compare against the last frame we actually *sent*, not the last frame
        # we saw. Otherwise a slow pan never trips the threshold on any single
        # step while ending up somewhere completely different.
        baseline = self._last_sent_thumb
        if baseline is None:
            return self._commit(frame, "no frame sent yet")

        novelty = thumb_distance(baseline, frame.thumb)
        if novelty < cfg.change_threshold:
            return GateDecision(False, f"scene unchanged (novelty {novelty:.3f})")

        return self._commit(frame, f"scene changed (novelty {novelty:.3f})")
