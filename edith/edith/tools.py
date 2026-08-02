"""The assistant's tool surface.

Two rules shape this list.

**Every tool is cheap or explicitly consented.** The wearable's scarce resources
are the wearer's attention, the battery, and vision tokens. ``look`` is the only
expensive tool and it exists so that looking is a decision the model makes out
loud, once, rather than a background stream nobody can audit.

**The prohibited capabilities are absent, not guarded.** There is no
``identify_face`` tool with a permission check in front of it, because a tool
that exists can be reached by prompt injection from anything the camera reads.
The refusals in policy.py are enforced by the shape of this registry: the
effector simply does not exist.
"""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, Protocol

from .memory import Memory
from .types import Assurance, Card, Peer

Handler = Callable[..., Any] | Callable[..., Awaitable[Any]]


class Looker(Protocol):
    """Something that can produce a description of the current view."""

    async def look(self, question: str) -> str: ...


@dataclass
class ToolContext:
    """What tools are allowed to touch."""

    memory: Memory
    looker: Looker | None = None
    peers: list[Peer] = field(default_factory=list)
    cards: list[Card] = field(default_factory=list)
    reminders: list[tuple[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    schema: dict[str, Any]
    handler: Handler

    def to_api(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.schema,
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def add(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def __contains__(self, name: object) -> bool:
        return name in self._tools

    def __len__(self) -> int:
        return len(self._tools)

    def names(self) -> list[str]:
        return sorted(self._tools)

    def to_api(self) -> list[dict[str, Any]]:
        return [self._tools[n].to_api() for n in sorted(self._tools)]

    async def invoke(self, name: str, args: dict[str, Any], ctx: ToolContext) -> str:
        tool = self._tools.get(name)
        if tool is None:
            return f"No such tool: {name}"
        result = tool.handler(ctx, **args)
        if inspect.isawaitable(result):
            result = await result
        return str(result)


# --------------------------------------------------------------------------
# Handlers
# --------------------------------------------------------------------------


async def _look(ctx: ToolContext, question: str) -> str:
    if ctx.looker is None:
        return "No camera is available on this device right now."
    return await ctx.looker.look(question)


def _recall(ctx: ToolContext, query: str, limit: int = 5) -> str:
    hits = ctx.memory.recall(query, limit=limit)
    if not hits:
        return "Nothing in memory matches that."
    return "\n".join(f"[{h.age_phrase()}] {h.body}" for h in hits)


def _remember(ctx: ToolContext, topic: str, body: str) -> str:
    ctx.memory.remember(topic, body)
    return f"Saved under '{topic}'."


def _who_is_near(ctx: ToolContext) -> str:
    """Only ever reports people who are actively answering for themselves.

    A peer at PROXIMITY or NONE assurance is deliberately reported as an
    unresolved presence rather than a guess. Guessing is the failure mode this
    whole design exists to avoid.
    """
    if not ctx.peers:
        return "Nobody nearby is broadcasting a resolvable presence."
    lines = []
    for p in ctx.peers:
        if p.assurance in (Assurance.NAMED, Assurance.ATTESTED) and p.display_name:
            extra = ""
            if p.disclosed:
                shown = ", ".join(f"{k}: {v}" for k, v in p.disclosed.items())
                extra = f" ({shown})"
            dist = f", ~{p.distance_m:.1f}m" if p.distance_m is not None else ""
            lines.append(f"{p.display_name}{extra} — resolved live{dist}")
        else:
            lines.append(
                "An unresolved presence nearby. Someone is broadcasting but did not "
                "answer, so I cannot say who it is — and I should not guess."
            )
    return "\n".join(lines)


def _show_card(ctx: ToolContext, title: str, lines: list[str] | None = None) -> str:
    trimmed = tuple((lines or [])[:4])
    ctx.cards.append(Card(title=title[:48], lines=trimmed))
    return "Shown on the display."


def _set_reminder(ctx: ToolContext, when: str, what: str) -> str:
    ctx.reminders.append((when, what))
    return f"Reminder set for {when}: {what}"


# --------------------------------------------------------------------------


def default_registry() -> ToolRegistry:
    reg = ToolRegistry()

    reg.add(
        Tool(
            name="look",
            description=(
                "Look through the wearer's camera and answer a question about what "
                "is in front of them right now. Use this only when the answer "
                "genuinely depends on the current view — reading a label, a sign, a "
                "screen, a menu, or identifying an object the wearer is pointing at. "
                "Each call costs real money and battery, so do not use it to check "
                "something you were already told."
            ),
            schema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "What to determine from the current view.",
                    }
                },
                "required": ["question"],
            },
            handler=_look,
        )
    )

    reg.add(
        Tool(
            name="recall",
            description=(
                "Search the wearer's own past interactions and saved notes. Use for "
                "'what did I say about', 'where did I leave', 'who did I meet'."
            ),
            schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 10},
                },
                "required": ["query"],
            },
            handler=_recall,
        )
    )

    reg.add(
        Tool(
            name="remember",
            description=(
                "Save a durable fact the wearer wants kept. Use when they say "
                "'remember that', or when you learn a stable preference worth "
                "keeping. Never store anything about a bystander."
            ),
            schema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["topic", "body"],
            },
            handler=_remember,
        )
    )

    reg.add(
        Tool(
            name="who_is_near",
            description=(
                "List people nearby who are broadcasting a resolvable presence and "
                "have answered a live challenge. This only ever returns people the "
                "wearer has paired with who are consenting right now. It cannot "
                "identify a stranger, and there is no other tool that can."
            ),
            schema={"type": "object", "properties": {}},
            handler=_who_is_near,
        )
    )

    reg.add(
        Tool(
            name="show_card",
            description=(
                "Put a short card on the heads-up display. The display is a narrow "
                "text strip: a title plus at most 4 short lines. Use it for things "
                "the wearer needs to read rather than hear — a number, an address, "
                "a list of three options. Speak instead when prose would do."
            ),
            schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "lines": {
                        "type": "array",
                        "items": {"type": "string"},
                        "maxItems": 4,
                    },
                },
                "required": ["title"],
            },
            handler=_show_card,
        )
    )

    reg.add(
        Tool(
            name="set_reminder",
            description="Set a time- or place-based reminder for the wearer.",
            schema={
                "type": "object",
                "properties": {
                    "when": {"type": "string"},
                    "what": {"type": "string"},
                },
                "required": ["when", "what"],
            },
            handler=_set_reminder,
        )
    )

    return reg
