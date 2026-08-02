"""Wiring: sensors in, gates in the middle, speech and glass out.

The shape of this loop is the argument of the whole project. E.D.I.T.H. is
depicted as a system that continuously perceives everything and volunteers what
it notices. Built that way with 2026 components you get a device that costs
hundreds of dollars a day per wearer, runs for ninety minutes, and gets muted by
lunchtime.

So the loop inverts the default. Sensing is continuous and nearly free — a
16x16 thumbnail and a voice-activity flag. *Spending* is rare and always has a
reason: a question was asked, or a cheap judge decided this specific thing was
worth interrupting a human being for. Everything expensive sits behind a gate
that can say no, and by default the proactive path is switched off entirely,
because "an assistant that comments on things" is the single most reliable way
to make someone stop wearing it.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import time
from dataclasses import dataclass, field
from typing import Any

from .brain import Brain
from .devices.base import Device
from .gate import GateDecision, VisionGate
from .identity import Advertisement, Roster, Signer
from .memory import Memory
from .tools import ToolContext
from .types import Assurance, Card, Frame, Turn, Utterance


@dataclass
class RuntimeConfig:
    #: Let the assistant look and speak without being asked. Off by default.
    #: Turning this on is a product decision with a running cost; make it
    #: deliberately, and measure the mute rate.
    proactive: bool = False
    #: Speak replies aloud as well as recording them.
    speak_replies: bool = True
    #: Drop resolved peers from context after this long without a fresh ad.
    peer_ttl_s: float = 60.0


class ScriptedLooker:
    """Vision for the simulator: reports what the script says is in view."""

    def __init__(self, device: Any) -> None:
        self.device = device
        self.calls: list[str] = []

    async def look(self, question: str) -> str:
        self.calls.append(question)
        frame = await self.device.capture()
        if frame is None:
            return "The camera returned nothing."
        described = getattr(self.device, "describe_now", lambda: "")()
        return described or "Nothing identifiable in view."


class ClaudeLooker:
    """Vision for real hardware: one gated frame, downscaled, to the model.

    The downscale is not incidental. A full-resolution frame on a current
    Opus-class model can cost ~4.8K input tokens; the same frame at a size that
    still reads signage and labels costs closer to 1.1K. Over a day of use that
    ratio is the difference between a viable unit economic and an unviable one.
    """

    def __init__(
        self,
        client: Any,
        device: Device,
        gate: VisionGate,
        *,
        model: str = "claude-opus-5",
        max_tokens: int = 1024,
    ) -> None:
        self.client = client
        self.device = device
        self.gate = gate
        self.model = model
        self.max_tokens = max_tokens

    async def look(self, question: str) -> str:
        frame = await self.device.capture()
        if frame is None or frame.jpeg is None:
            return "The camera is not available right now."
        self.gate.note_capture()
        b64 = base64.standard_b64encode(frame.jpeg).decode()
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                f"{question}\n\nAnswer in one sentence. Do not "
                                f"speculate about the identity of any person."
                            ),
                        },
                    ],
                }
            ],
        )
        parts = [
            getattr(b, "text", "")
            for b in getattr(resp, "content", []) or []
            if getattr(b, "type", None) == "text"
        ]
        return "".join(parts).strip() or "I couldn't make that out."


@dataclass
class Assistant:
    device: Any
    brain: Brain
    memory: Memory
    roster: Roster = field(default_factory=Roster)
    gate: VisionGate = field(default_factory=VisionGate)
    config: RuntimeConfig = field(default_factory=RuntimeConfig)
    looker: Any | None = None

    #: Signers for paired contacts, keyed by handle. On real hardware this is a
    #: live radio round trip to the peer's device; here it is injected so tests
    #: can model a device that answers, and one that has been revoked.
    responders: dict[str, Signer] = field(default_factory=dict)

    #: handle -> (observed_at_monotonic, Peer). The observation time is tracked
    #: here rather than read off the Peer, because handle derivation runs on
    #: wall-clock (both devices must agree on the rotation window) while expiry
    #: must run on a monotonic clock that an NTP step cannot move.
    _peers: dict[str, tuple[float, Any]] = field(default_factory=dict, repr=False)
    _last_gate: GateDecision | None = field(default=None, repr=False)
    _turns: list[Turn] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        if self.looker is None:
            self.looker = ScriptedLooker(self.device)

    # -- context ---------------------------------------------------------

    def live_peers(self) -> list[Any]:
        now = time.monotonic()
        return [
            peer
            for seen_at, peer in self._peers.values()
            if now - seen_at <= self.config.peer_ttl_s
        ]

    def _context(self) -> ToolContext:
        return ToolContext(
            memory=self.memory, looker=self.looker, peers=self.live_peers()
        )

    # -- sensor loops ----------------------------------------------------

    async def _watch_frames(self) -> None:
        async for frame in self.device.frames():
            self._last_gate = self.gate.consider(frame)
            if self._last_gate.look and self.config.proactive:
                await self._consider_speaking(frame)

    async def _watch_speech(self) -> None:
        async for utt in self.device.speech():
            if utt.directed:
                await self.handle(utt)
            # Undirected speech is context only, and only when the wearer has
            # opted into ambient capture. It never starts a turn by itself.

    async def _watch_peers(self) -> None:
        async for ad in self.device.peers():
            self._resolve(ad)

    def _resolve(self, ad: Advertisement) -> None:
        peer = self.roster.resolve(
            ad, challenge_responder=self.responders.get(ad.handle)
        )
        self._peers[ad.handle] = (time.monotonic(), peer)

    # -- turns -----------------------------------------------------------

    async def handle(self, utt: Utterance) -> Turn:
        """Run one directed turn end to end."""
        ctx = self._context()
        reply = await self.brain.respond(utt.text, ctx)

        if reply.text and self.config.speak_replies:
            await self.device.speak(reply.text)
        for card in ctx.cards:
            await self.device.show(card)

        turn = Turn(
            prompt=utt.text,
            reply=reply.text,
            trigger="directed",
            tools_used=reply.tools_used,
            saw_frame="look" in reply.tools_used,
            latency_ms=reply.latency_ms,
            input_tokens=reply.input_tokens,
            output_tokens=reply.output_tokens,
        )
        self.memory.record_turn(turn)
        self._turns.append(turn)
        return turn

    async def _consider_speaking(self, frame: Frame) -> None:
        """The proactive path: cheap judge first, expensive model only if it says yes."""
        situation = self._situation()
        if not situation:
            return
        speak, what = await asyncio.to_thread(self.brain.should_interrupt, situation)
        if not speak:
            return
        self.gate.note_capture()
        await self.device.speak(what)
        turn = Turn(prompt=situation, reply=what, trigger="proactive")
        self.memory.record_turn(turn)
        self._turns.append(turn)

    def _situation(self) -> str:
        """A one-line description of what is going on, for the reflex judge.

        Deliberately built from cheap signals only — no vision call is made to
        decide whether to make a vision call.
        """
        bits = []
        if self._last_gate is not None:
            bits.append(f"view: {self._last_gate.reason}")
        named = [
            p.display_name
            for p in self.live_peers()
            if p.assurance in (Assurance.NAMED, Assurance.ATTESTED) and p.display_name
        ]
        if named:
            bits.append("with: " + ", ".join(named))
        return "; ".join(bits)

    # -- lifecycle -------------------------------------------------------

    async def run(self) -> list[Turn]:
        """Run every sensor loop until the device's streams are exhausted."""
        tasks = [
            asyncio.create_task(self._watch_peers()),
            asyncio.create_task(self._watch_frames()),
            asyncio.create_task(self._watch_speech()),
        ]
        try:
            await asyncio.gather(*tasks)
        finally:
            for t in tasks:
                if not t.done():
                    t.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await t
        return list(self._turns)

    # -- reporting -------------------------------------------------------

    def cost_report(self) -> dict[str, Any]:
        tin = sum(t.input_tokens for t in self._turns)
        tout = sum(t.output_tokens for t in self._turns)
        looks = sum(1 for t in self._turns if t.saw_frame)
        return {
            "turns": len(self._turns),
            "vision_calls": looks,
            "input_tokens": tin,
            "output_tokens": tout,
            # Opus 5 list pricing, $5/MTok in and $25/MTok out.
            "usd": round(tin / 1e6 * 5.0 + tout / 1e6 * 25.0, 5),
        }


__all__ = [
    "Assistant",
    "RuntimeConfig",
    "ClaudeLooker",
    "ScriptedLooker",
    "Card",
]
