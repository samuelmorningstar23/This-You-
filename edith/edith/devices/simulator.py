"""A scripted stand-in for a pair of glasses.

This exists so the whole runtime — gating, budgets, tool loop, memory, identity
resolution — can be developed, tested, and demonstrated on a laptop or in CI,
with no hardware and no camera. It replays a timeline of scenes and utterances
at controllable speed and collects everything the assistant tried to say or
display, so tests can assert on behaviour rather than on mocks.

The thumbnails are synthesised rather than captured, which is exactly what makes
the gate testable: a scene has a brightness and a texture, a "turn" between
scenes produces genuinely different pixels, and holding still produces
genuinely similar ones. That is all the gate reasons about, so the simulator
exercises the real code path rather than a stub of it.
"""

from __future__ import annotations

import asyncio
import hashlib
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from ..identity import Advertisement
from ..types import Card, Frame, Utterance

THUMB_W = THUMB_H = 16
THUMB_LEN = THUMB_W * THUMB_H


def synth_thumb(scene: str, jitter: int = 0) -> bytes:
    """Deterministic 16x16 grayscale thumbnail for a named scene.

    Same scene, same bytes (plus a little sensor-like jitter); different scene,
    thoroughly different bytes. Jitter is small so that holding still stays
    below the change threshold, which is the property the gate depends on.
    """
    seed = hashlib.sha256(scene.encode()).digest()
    out = bytearray(THUMB_LEN)
    for i in range(THUMB_LEN):
        v = seed[i % len(seed)]
        out[i] = (v + jitter) % 256
    return bytes(out)


@dataclass
class Scene:
    """A stretch of time in which the wearer is looking at one thing."""

    name: str
    #: Seconds of simulated time this scene lasts.
    duration_s: float = 3.0
    #: What a vision call would report if made during this scene.
    describes: str = ""


@dataclass
class ScriptEvent:
    """Something that happens at a point in the timeline."""

    at_s: float
    say: str | None = None
    directed: bool = True
    peer_handle: str | None = None
    peer_range_m: float | None = None


@dataclass
class SimulatedDevice:
    """Replays a scripted timeline as if it were sensor input."""

    scenes: list[Scene] = field(default_factory=list)
    script: list[ScriptEvent] = field(default_factory=list)
    #: Simulated seconds per real second.
    #:
    #: Deliberately not 0 ("run flat out"). The camera, microphone, and radio
    #: are three independent async streams, and with zero pacing their
    #: interleaving is decided by task-scheduling order rather than by the
    #: timeline — so an advertisement scheduled *before* a question could be
    #: delivered after it.
    #:
    #: 50 means one simulated second costs 20 ms, which keeps a 25-second
    #: scenario under half a second while leaving every gap in the timeline
    #: comfortably above the event loop's timer resolution. An earlier value of
    #: 500 was too aggressive: it compressed a 0.2 s and a 1.0 s gap to 0.4 ms
    #: and 2 ms, close enough to the scheduler's granularity that the two
    #: streams occasionally swapped order and a test failed intermittently.
    speed: float = 50.0
    frame_interval_s: float = 0.5

    name: str = "simulator"
    spoken: list[str] = field(default_factory=list)
    displayed: list[Card] = field(default_factory=list)
    vision_calls: int = 0

    _clock: float = 0.0
    _scene_idx: int = 0
    _origin: float | None = None

    # -- helpers ---------------------------------------------------------

    def _scene_at(self, t: float) -> Scene | None:
        acc = 0.0
        for s in self.scenes:
            if t < acc + s.duration_s:
                return s
            acc += s.duration_s
        return self.scenes[-1] if self.scenes else None

    def _total_s(self) -> float:
        return sum(s.duration_s for s in self.scenes) or 1.0

    async def _wait_until(self, sim_t: float) -> None:
        """Sleep until simulated time ``sim_t``, on a clock shared by all streams.

        Absolute rather than relative: each stream sleeps toward a deadline
        measured from one common origin, so per-hop scheduling jitter cannot
        accumulate and reorder events that the timeline says are ordered.
        Sleeping ``gap / speed`` per hop instead lets three independent streams
        drift apart, which is how the ordering bug this replaces was born.
        """
        if self.speed <= 0:
            await asyncio.sleep(0)
            return
        loop = asyncio.get_running_loop()
        if self._origin is None:
            self._origin = loop.time()
        deadline = self._origin + sim_t / self.speed
        remaining = deadline - loop.time()
        await asyncio.sleep(max(0.0, remaining))

    # -- Device protocol -------------------------------------------------

    async def frames(self) -> AsyncIterator[Frame]:
        t = 0.0
        total = self._total_s()
        prev_scene: str | None = None
        step = 0
        while t <= total:
            scene = self._scene_at(t)
            if scene is None:
                break
            # A scene change looks like a head turn: one frame of large motion,
            # then a settled view. That is what the gate is built to survive.
            if prev_scene is not None and scene.name != prev_scene:
                yield Frame(
                    thumb=synth_thumb(f"{prev_scene}->{scene.name}"),
                    width=THUMB_W,
                    height=THUMB_H,
                    ts=t,
                )
                prev_scene = scene.name
                t += self.frame_interval_s
                await self._wait_until(t)
                continue
            prev_scene = scene.name
            yield Frame(
                thumb=synth_thumb(scene.name, jitter=step % 3),
                width=THUMB_W,
                height=THUMB_H,
                ts=t,
            )
            step += 1
            t += self.frame_interval_s
            await self._wait_until(t)

    async def speech(self) -> AsyncIterator[Utterance]:
        for ev in sorted(self.script, key=lambda e: e.at_s):
            if ev.say is None:
                continue
            await self._wait_until(ev.at_s)
            self._clock = ev.at_s
            yield Utterance(text=ev.say, directed=ev.directed, ts=ev.at_s)

    async def peers(self) -> AsyncIterator[Advertisement]:
        for ev in sorted(self.script, key=lambda e: e.at_s):
            if ev.peer_handle is None:
                continue
            await self._wait_until(ev.at_s)
            yield Advertisement(
                handle=ev.peer_handle, ranged_m=ev.peer_range_m, ts=ev.at_s
            )

    async def capture(self) -> Frame | None:
        self.vision_calls += 1
        scene = self._scene_at(self._clock)
        if scene is None:
            return None
        return Frame(
            thumb=synth_thumb(scene.name),
            width=THUMB_W,
            height=THUMB_H,
            jpeg=b"<simulated jpeg>",
            ts=self._clock,
        )

    def describe_now(self) -> str:
        scene = self._scene_at(self._clock)
        return scene.describes if scene else ""

    async def speak(self, text: str) -> None:
        self.spoken.append(text)

    async def show(self, card: Card) -> None:
        self.displayed.append(card)
