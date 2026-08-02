"""The hardware seam.

The single most useful thing you can do when building for smart glasses in 2026
is to not depend on any particular pair of them. The category is churning: the
open platforms are small, the big platforms are locked, and the device you
target today may not have a developer story in eighteen months. Every previous
generation of this product died attached to hardware.

So the runtime talks to this Protocol and nothing else. Four inputs, two
outputs, all of which every candidate device can supply in some form:

  frames()  — camera, with a cheap thumbnail for gating
  speech()  — segmented, transcribed, and flagged as directed-at-me or not
  peers()   — short-range presence advertisements
  capture() — a full frame on demand, when the gate has said yes

  speak()   — open-ear or bone-conduction audio
  show()    — a narrow monocular text strip

Note what is *not* in this interface: no 6DoF pose, no world anchors, no depth,
no hands. Almost nothing shipping in this form factor has them, and designing
around them is how you end up with software that runs on no available hardware.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from ..identity import Advertisement
from ..types import Card, Frame, Utterance


@runtime_checkable
class Device(Protocol):
    """What the assistant needs from a pair of glasses."""

    name: str

    def frames(self) -> AsyncIterator[Frame]:
        """Low-rate frames carrying a thumbnail; ``jpeg`` may be None."""
        ...

    def speech(self) -> AsyncIterator[Utterance]:
        """Segmented, transcribed speech with a directed-at-me flag."""
        ...

    def peers(self) -> AsyncIterator[Advertisement]:
        """Short-range presence advertisements from nearby devices."""
        ...

    async def capture(self) -> Frame | None:
        """A full frame right now, for a gated vision call."""
        ...

    async def speak(self, text: str) -> None: ...

    async def show(self, card: Card) -> None: ...


class NullDevice:
    """A device that senses nothing and displays nothing. Useful for tests."""

    name = "null"

    async def _empty(self):  # pragma: no cover - trivial
        return
        yield  # unreachable; present so this is an async generator

    def frames(self):
        return self._empty()

    def speech(self):
        return self._empty()

    def peers(self):
        return self._empty()

    async def capture(self) -> Frame | None:
        return None

    async def speak(self, text: str) -> None:
        return None

    async def show(self, card: Card) -> None:
        return None
