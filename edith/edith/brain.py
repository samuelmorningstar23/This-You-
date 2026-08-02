"""The Claude side of the assistant.

Three decisions here are worth explaining, because they are the ones that make
the difference between a demo and something wearable.

**Two tiers, chosen by cost of being wrong.** Deciding whether to interrupt
someone is a cheap judgement made constantly, so it runs on Haiku. Answering a
question the wearer actually asked runs on Opus 5. Routing by consequence rather
than by "complexity" is what keeps the always-on part of an always-on assistant
from costing more than the useful part.

**Effort is the latency dial, not thinking on/off.** Opus 5 thinks by default,
and disabling thinking on it has two documented failure modes — tool calls
occasionally emitted as plain text (the call silently never runs) and internal
tags leaking into the spoken response. Both are unacceptable when the output
goes straight to a speaker. So thinking stays on and `effort` comes down to
`low`/`medium`, which on this model gives most of the latency saving without
either failure mode.

**max_tokens is sized for thinking, not for speech.** The spoken answer is two
sentences, but `max_tokens` caps thinking *plus* response. Sizing it to the
answer is how you get a reply truncated mid-word after a long think.

The client is injected, so the whole loop is testable without a network or a
key — see tests/test_brain.py.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Protocol

from . import prompts
from .tools import ToolContext, ToolRegistry

#: Answering the wearer. Reasoning quality matters; they are waiting.
DELIBERATE_MODEL = "claude-opus-5"
#: Constant background judgement. Must be nearly free.
REFLEX_MODEL = "claude-haiku-4-5"

#: Generous on purpose — this budgets thinking, not the spoken sentence.
DELIBERATE_MAX_TOKENS = 8_000
REFLEX_MAX_TOKENS = 128


class MessagesAPI(Protocol):
    def create(self, **kwargs: Any) -> Any: ...


class ClientLike(Protocol):
    @property
    def beta(self) -> Any: ...

    @property
    def messages(self) -> MessagesAPI: ...


@dataclass
class Reply:
    text: str
    tools_used: tuple[str, ...] = ()
    cards: tuple[Any, ...] = ()
    latency_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    refused: bool = False
    refusal_category: str | None = None


@dataclass
class Brain:
    client: Any
    registry: ToolRegistry
    model: str = DELIBERATE_MODEL
    reflex_model: str = REFLEX_MODEL
    effort: str = "medium"
    max_tool_rounds: int = 4

    #: Conversation carried across turns. Trimmed aggressively: a wearable
    #: conversation is a series of short exchanges, not a long thread, and
    #: unbounded history is a latency bug that grows all day.
    history: list[dict[str, Any]] = field(default_factory=list)
    max_history_turns: int = 8

    def _system(self) -> list[dict[str, Any]]:
        # One cache breakpoint on the stable core. Nothing volatile above it.
        return [
            {
                "type": "text",
                "text": prompts.CORE,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    def _trim(self) -> None:
        # Keep whole user/assistant pairs; never leave a dangling tool_use.
        limit = self.max_history_turns * 2
        if len(self.history) > limit:
            drop = len(self.history) - limit
            while drop < len(self.history) and self.history[drop]["role"] != "user":
                drop += 1
            self.history = self.history[drop:]

    def _call(self, **kwargs: Any) -> Any:
        """One request, with server-side refusal fallback where available.

        Opus 5's safety classifiers can decline with a 200 and
        ``stop_reason == "refusal"``. On a wearable that must not surface as a
        crash, so we opt into the server-side fallback and degrade to a plain
        call if this client predates it.
        """
        try:
            return self.client.beta.messages.create(
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                **kwargs,
            )
        except TypeError:
            return self.client.messages.create(**kwargs)
        except Exception as exc:  # noqa: BLE001 - beta may be unavailable
            if _is_beta_unavailable(exc):
                return self.client.messages.create(**kwargs)
            raise

    async def respond(self, user_text: str, ctx: ToolContext) -> Reply:
        """Run one turn to completion, including any tool round trips."""
        started = time.monotonic()
        self.history.append({"role": "user", "content": user_text})
        self._trim()

        tools_used: list[str] = []
        in_tokens = out_tokens = 0
        cards_before = len(ctx.cards)

        for _round in range(self.max_tool_rounds):
            resp = self._call(
                model=self.model,
                max_tokens=DELIBERATE_MAX_TOKENS,
                system=self._system(),
                output_config={"effort": self.effort},
                tools=self.registry.to_api(),
                messages=self.history,
            )

            usage = getattr(resp, "usage", None)
            if usage is not None:
                in_tokens += int(getattr(usage, "input_tokens", 0) or 0)
                out_tokens += int(getattr(usage, "output_tokens", 0) or 0)

            stop = getattr(resp, "stop_reason", None)
            if stop == "refusal":
                details = getattr(resp, "stop_details", None)
                return Reply(
                    text="I can't help with that one.",
                    refused=True,
                    refusal_category=getattr(details, "category", None),
                    latency_ms=int((time.monotonic() - started) * 1000),
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                )

            content = list(getattr(resp, "content", []) or [])
            self.history.append({"role": "assistant", "content": content})

            calls = [b for b in content if getattr(b, "type", None) == "tool_use"]
            if not calls:
                text = _text_of(content)
                return Reply(
                    text=text,
                    tools_used=tuple(tools_used),
                    cards=tuple(ctx.cards[cards_before:]),
                    latency_ms=int((time.monotonic() - started) * 1000),
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                )

            results = []
            for call in calls:
                name = getattr(call, "name", "")
                args = dict(getattr(call, "input", {}) or {})
                tools_used.append(name)
                try:
                    out = await self.registry.invoke(name, args, ctx)
                    is_error = False
                except Exception as exc:  # noqa: BLE001 - surface to the model
                    out, is_error = f"{type(exc).__name__}: {exc}", True
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": getattr(call, "id", ""),
                        "content": out,
                        "is_error": is_error,
                    }
                )
            # All results go back in one user message; splitting them teaches
            # the model to stop making parallel calls.
            self.history.append({"role": "user", "content": results})

        return Reply(
            text="That turned into more steps than I can do while you're walking.",
            tools_used=tuple(tools_used),
            latency_ms=int((time.monotonic() - started) * 1000),
            input_tokens=in_tokens,
            output_tokens=out_tokens,
        )

    def should_interrupt(self, situation: str) -> tuple[bool, str]:
        """Cheap always-on judgement: is this worth speaking up about?

        Runs on the small model with a tight token cap. The bar is set in the
        prompt, and it is set high: an assistant that volunteers observations
        gets muted, and a muted assistant has no value at all.
        """
        resp = self.client.messages.create(
            model=self.reflex_model,
            max_tokens=REFLEX_MAX_TOKENS,
            system=prompts.REFLEX,
            messages=[{"role": "user", "content": situation}],
        )
        text = _text_of(getattr(resp, "content", []) or []).strip()
        if not text.upper().startswith("YES"):
            return False, ""
        _, _, rest = text.partition(":")
        return True, rest.strip()


def _text_of(content: list[Any]) -> str:
    parts = []
    for block in content:
        if getattr(block, "type", None) == "text":
            parts.append(getattr(block, "text", ""))
    return "".join(parts).strip()


def _is_beta_unavailable(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(
        s in msg
        for s in ("beta", "unknown parameter", "unsupported", "fallbacks", "not found")
    )
