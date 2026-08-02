"""A fake Anthropic client.

The point is to exercise the *real* tool loop — multi-round tool calls, usage
accounting, refusal handling — without a network or a key, so the behaviour
under test is our orchestration rather than a mock of it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TextBlock:
    text: str
    type: str = "text"


@dataclass
class ToolUseBlock:
    name: str
    input: dict[str, Any]
    id: str = "toolu_fake"
    type: str = "tool_use"


@dataclass
class Usage:
    input_tokens: int = 100
    output_tokens: int = 20


@dataclass
class FakeResponse:
    content: list[Any]
    stop_reason: str = "end_turn"
    stop_details: Any = None
    usage: Usage = field(default_factory=Usage)
    model: str = "claude-opus-5"


@dataclass
class StopDetails:
    category: str = "cyber"
    explanation: str = "declined"


class _Messages:
    def __init__(self, owner: FakeClient) -> None:
        self.owner = owner

    def create(self, **kwargs: Any) -> FakeResponse:
        self.owner.calls.append(kwargs)
        scripted = self.owner.responses
        if not scripted:
            return FakeResponse([TextBlock("(no scripted response)")])
        return scripted.pop(0)


class _Beta:
    def __init__(self, owner: FakeClient) -> None:
        self.messages = _BetaMessages(owner)


class _BetaMessages:
    def __init__(self, owner: FakeClient) -> None:
        self.owner = owner

    def create(self, **kwargs: Any) -> FakeResponse:
        if not self.owner.supports_beta:
            raise TypeError("unexpected keyword argument 'fallbacks'")
        self.owner.beta_calls.append(kwargs)
        return _Messages(self.owner).create(**kwargs)


class FakeClient:
    """Returns scripted responses in order; records every request."""

    def __init__(
        self, responses: list[FakeResponse] | None = None, *, supports_beta: bool = True
    ) -> None:
        self.responses = list(responses or [])
        self.calls: list[dict[str, Any]] = []
        self.beta_calls: list[dict[str, Any]] = []
        self.supports_beta = supports_beta
        self.messages = _Messages(self)
        self.beta = _Beta(self)


def text(s: str) -> FakeResponse:
    return FakeResponse([TextBlock(s)])


def tool(name: str, **args: Any) -> FakeResponse:
    return FakeResponse([ToolUseBlock(name=name, input=args)], stop_reason="tool_use")


def refusal(category: str = "cyber") -> FakeResponse:
    return FakeResponse([], stop_reason="refusal", stop_details=StopDetails(category))
