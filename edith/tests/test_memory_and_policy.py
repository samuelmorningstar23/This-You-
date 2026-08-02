from __future__ import annotations

import pytest

from edith.memory import Memory
from edith.policy import PROHIBITIONS, PolicyViolation, enforce, prohibition_briefing
from edith.tools import ToolContext, default_registry
from edith.types import Card, Turn


def turn(prompt: str, reply: str) -> Turn:
    return Turn(prompt=prompt, reply=reply, trigger="directed")


def test_recall_finds_an_earlier_turn():
    m = Memory()
    m.record_turn(turn("where did I park", "Level 3, bay 44"))
    m.record_turn(turn("what's for dinner", "You said pasta"))
    hits = m.recall("park")
    assert hits
    assert "bay 44" in hits[0].body


def test_notes_are_recallable_and_survive_alongside_turns():
    m = Memory()
    m.remember("passport", "renewed March, expires 2036")
    m.record_turn(turn("hi", "hello"))
    hits = m.recall("passport")
    assert hits and "2036" in hits[0].body
    assert m.stats() == {"turns": 1, "notes": 1}


def test_recall_of_something_never_mentioned_returns_nothing():
    m = Memory()
    m.record_turn(turn("where did I park", "Level 3"))
    assert m.recall("quantum chromodynamics") == []


def test_recall_ignores_noise_words():
    m = Memory()
    assert m.recall("a of the") == []


def test_recall_finds_short_names():
    """Two-letter names must be searchable; dropping them loses real queries."""
    m = Memory()
    m.record_turn(turn("who was that", "MJ, from the robotics team"))
    hits = m.recall("MJ")
    assert hits and "robotics" in hits[0].body


def test_memory_persists_across_reopen(tmp_path):
    p = tmp_path / "memory.db"
    m = Memory(p)
    m.remember("keys", "in the blue coat")
    m.close()

    again = Memory(p)
    hits = again.recall("keys")
    assert hits and "blue coat" in hits[0].body


def test_age_phrase_is_human():
    import time

    m = Memory()
    m.remember("bike lock", "combination is on the fridge")
    rec = m.recall("bike lock")[0]
    assert rec.age_phrase(time.time()) == "just now"
    assert "hours ago" in rec.age_phrase(rec.ts + 7200)
    assert "days ago" in rec.age_phrase(rec.ts + 86400 * 3)


# -- policy ---------------------------------------------------------------


def test_every_prohibition_cites_its_legal_basis():
    assert len(PROHIBITIONS) >= 6
    for p in PROHIBITIONS:
        assert len(p.basis) > 80, f"{p.key} needs a real citation, not a gesture"
        assert p.summary


def test_enforce_raises_with_an_explanation():
    with pytest.raises(PolicyViolation) as exc:
        enforce("identify_stranger")
    assert "consent" in str(exc.value).lower()
    assert "BIPA" in str(exc.value)


def test_enforce_is_silent_for_anything_not_prohibited():
    enforce("read_a_menu")  # must not raise


def test_the_briefing_is_included_in_the_system_prompt():
    from edith import prompts

    assert prohibition_briefing() in prompts.CORE


def test_no_tool_exists_for_any_prohibited_capability():
    """The real control: the effector is absent, not merely guarded.

    A tool that exists can be reached by prompt injection from anything the
    camera happens to read. The registry is the enforcement point.
    """
    names = " ".join(default_registry().names())
    for banned in (
        "identify",
        "recognise",
        "recognize",
        "face",
        "drone",
        "fly",
        "strike",
        "target",
        "intercept",
        "wiretap",
        "messages_of",
    ):
        assert banned not in names, f"{banned} must not be reachable as a tool"


def test_who_is_near_reports_nothing_when_nobody_has_opted_in():
    reg = default_registry()
    import asyncio

    out = asyncio.run(reg.invoke("who_is_near", {}, ToolContext(memory=Memory())))
    assert "resolvable" in out


def test_a_card_is_capped_at_four_lines():
    """The display is a narrow strip. Overflowing it is a bug, not a truncation."""
    with pytest.raises(ValueError):
        Card(title="too much", lines=("a", "b", "c", "d", "e"))


def test_show_card_trims_rather_than_failing():
    reg = default_registry()
    import asyncio

    ctx = ToolContext(memory=Memory())
    asyncio.run(
        reg.invoke("show_card", {"title": "x", "lines": ["1", "2", "3", "4", "5"]}, ctx)
    )
    assert len(ctx.cards[0].lines) == 4
