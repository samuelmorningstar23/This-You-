"""The agent loop and the end-to-end runtime, exercised without a network."""

from __future__ import annotations

import asyncio

import pytest

from edith.brain import Brain
from edith.devices.simulator import Scene, ScriptEvent, SimulatedDevice
from edith.identity import ROTATION_S, Roster, SharedSecretSigner, derive_handle
from edith.memory import Memory
from edith.runtime import Assistant, RuntimeConfig
from edith.tools import ToolContext, default_registry
from edith.types import Utterance

from .fakes import FakeClient, refusal, text, tool


def make_brain(responses, **kw):
    return Brain(client=FakeClient(responses), registry=default_registry(), **kw)


def run(coro):
    return asyncio.run(coro)


# -- brain -----------------------------------------------------------------


def test_a_plain_answer_makes_one_request():
    mem = Memory()
    brain = make_brain([text("Twelve minutes.")])
    reply = run(brain.respond("how long is the pasta", ToolContext(memory=mem)))
    assert reply.text == "Twelve minutes."
    assert reply.tools_used == ()
    assert len(brain.client.calls) == 1


def test_a_tool_call_round_trips_and_is_reported():
    mem = Memory()
    brain = make_brain(
        [tool("remember", topic="parking", body="level 3, bay 44"), text("Got it.")]
    )
    reply = run(brain.respond("remember where I parked", ToolContext(memory=mem)))
    assert reply.text == "Got it."
    assert reply.tools_used == ("remember",)
    assert mem.stats()["notes"] == 1


def test_tool_results_are_returned_in_a_single_user_message():
    """Splitting results across messages trains the model out of parallel calls."""
    mem = Memory()
    brain = make_brain([tool("recall", query="parking"), text("Level 3.")])
    run(brain.respond("where did I park", ToolContext(memory=mem)))
    tool_result_messages = [
        m
        for m in brain.history
        if m["role"] == "user"
        and isinstance(m["content"], list)
        and any(b.get("type") == "tool_result" for b in m["content"])
    ]
    assert len(tool_result_messages) == 1


def test_a_failing_tool_is_reported_to_the_model_rather_than_crashing():
    mem = Memory()
    brain = make_brain([tool("look", question="what is this"), text("No camera.")])
    ctx = ToolContext(memory=mem, looker=None)
    reply = run(brain.respond("what am I looking at", ctx))
    assert reply.text == "No camera."


def test_an_unknown_tool_does_not_crash_the_turn():
    mem = Memory()
    brain = make_brain([tool("launch_drone", target="x"), text("I can't do that.")])
    reply = run(brain.respond("take it out", ToolContext(memory=mem)))
    assert reply.text == "I can't do that."


def test_a_refusal_is_surfaced_as_speech_not_an_exception():
    mem = Memory()
    brain = make_brain([refusal("cyber")])
    reply = run(brain.respond("something declined", ToolContext(memory=mem)))
    assert reply.refused is True
    assert reply.refusal_category == "cyber"
    assert reply.text  # there is always something to say out loud


def test_the_tool_loop_is_bounded():
    """A model that keeps calling tools must not spin forever on someone's face."""
    mem = Memory()
    brain = make_brain([tool("recall", query="x") for _ in range(20)], max_tool_rounds=3)
    reply = run(brain.respond("go", ToolContext(memory=mem)))
    assert len(brain.client.calls) == 3
    assert reply.text


def test_the_stable_system_prompt_is_cached_and_carries_nothing_volatile():
    mem = Memory()
    brain = make_brain([text("ok")])
    run(brain.respond("hi", ToolContext(memory=mem)))
    system = brain.client.calls[0]["system"]
    assert system[0]["cache_control"] == {"type": "ephemeral"}
    # A timestamp or location here would silently destroy the cache every turn.
    assert "202" not in system[0]["text"]


def test_max_tokens_budgets_thinking_not_just_the_spoken_sentence():
    mem = Memory()
    brain = make_brain([text("ok")])
    run(brain.respond("hi", ToolContext(memory=mem)))
    assert brain.client.calls[0]["max_tokens"] >= 4000


def test_it_falls_back_to_the_plain_endpoint_when_beta_is_unavailable():
    mem = Memory()
    client = FakeClient([text("ok")], supports_beta=False)
    brain = Brain(client=client, registry=default_registry())
    reply = run(brain.respond("hi", ToolContext(memory=mem)))
    assert reply.text == "ok"
    assert client.beta_calls == []
    assert len(client.calls) == 1


def test_history_is_trimmed_without_orphaning_a_tool_use():
    mem = Memory()
    brain = make_brain([text("ok")] * 40, max_history_turns=2)
    for i in range(12):
        run(brain.respond(f"question {i}", ToolContext(memory=mem)))
    assert len(brain.history) <= 5
    assert brain.history[0]["role"] == "user"


# -- runtime ---------------------------------------------------------------


def build_assistant(responses, **cfg):
    device = SimulatedDevice(
        scenes=[Scene("kitchen", 4.0, describes="a pan of pasta on the hob")],
        script=[ScriptEvent(at_s=1.0, say="how long left")],
    )
    mem = Memory()
    brain = make_brain(responses)
    return device, Assistant(
        device=device,
        brain=brain,
        memory=mem,
        config=RuntimeConfig(**cfg),
    )


def test_a_directed_utterance_produces_speech_and_an_episodic_record():
    device, a = build_assistant([text("About four minutes.")])
    turn = run(a.handle(Utterance(text="how long left", directed=True)))
    assert device.spoken == ["About four minutes."]
    assert turn.reply == "About four minutes."
    assert a.memory.stats()["turns"] == 1


def test_a_look_reaches_the_camera_and_is_recorded_on_the_turn():
    device, a = build_assistant(
        [tool("look", question="what is on the hob"), text("Pasta, nearly done.")]
    )
    turn = run(a.handle(Utterance(text="what am I looking at", directed=True)))
    assert device.vision_calls == 1
    assert turn.saw_frame is True
    assert "Pasta" in turn.reply


def test_a_card_reaches_the_display():
    device, a = build_assistant(
        [tool("show_card", title="Platform 4", lines=["09:42", "3 min"]), text("There.")]
    )
    run(a.handle(Utterance(text="which platform", directed=True)))
    assert len(device.displayed) == 1
    assert device.displayed[0].title == "Platform 4"


def test_overheard_speech_never_starts_a_turn():
    """Ambient conversation is context at most. It must not trigger the model."""
    device = SimulatedDevice(
        scenes=[Scene("cafe", 3.0)],
        script=[
            ScriptEvent(at_s=0.5, say="I think the meeting is Thursday", directed=False),
            ScriptEvent(at_s=1.0, say="did you catch that", directed=True),
        ],
    )
    mem = Memory()
    brain = make_brain([text("Thursday.")])
    a = Assistant(device=device, brain=brain, memory=mem)
    turns = run(a.run())
    assert len(turns) == 1
    assert turns[0].prompt == "did you catch that"


def test_the_proactive_path_is_off_by_default():
    """An assistant that volunteers observations gets muted; default to silence."""
    device = SimulatedDevice(
        scenes=[Scene("desk", 2.0), Scene("street", 2.0), Scene("shop", 2.0)],
        script=[],
    )
    mem = Memory()
    brain = make_brain([text("should never be reached")] * 10)
    a = Assistant(device=device, brain=brain, memory=mem)
    turns = run(a.run())
    assert turns == []
    assert device.spoken == []
    assert brain.client.calls == []


def test_a_resolved_peer_appears_in_tool_context_and_a_stranger_does_not():
    roster = Roster()
    contact = roster.pair("mj", "MJ", disclosed={"team": "robotics"})
    import time as _t

    handle = derive_handle(contact.secret, int(_t.time() // ROTATION_S))

    device = SimulatedDevice(
        scenes=[Scene("lab", 3.0)],
        script=[
            ScriptEvent(at_s=0.2, peer_handle=handle, peer_range_m=1.4),
            ScriptEvent(at_s=0.3, peer_handle="00ff00ff00ff00ff", peer_range_m=2.0),
            ScriptEvent(at_s=1.0, say="who's here"),
        ],
    )
    mem = Memory()
    brain = make_brain([tool("who_is_near"), text("MJ is here.")])
    a = Assistant(
        device=device,
        brain=brain,
        memory=mem,
        roster=roster,
        responders={handle: SharedSecretSigner(contact.secret)},
    )
    run(a.run())

    tool_results = [
        b
        for m in brain.history
        if m["role"] == "user" and isinstance(m["content"], list)
        for b in m["content"]
        if b.get("type") == "tool_result"
    ]
    assert tool_results, "who_is_near should have produced a result"
    body = tool_results[0]["content"]
    assert "MJ" in body
    assert "unresolved presence" in body  # the stranger, named as unknowable


def test_the_cost_report_prices_a_session():
    _device, a = build_assistant([text("ok")])
    run(a.handle(Utterance(text="hi", directed=True)))
    report = a.cost_report()
    assert report["turns"] == 1
    assert report["usd"] > 0


@pytest.mark.parametrize("proactive", [False, True])
def test_runtime_completes_regardless_of_proactive_setting(proactive):
    device = SimulatedDevice(scenes=[Scene("a", 1.0), Scene("b", 1.0)], script=[])
    mem = Memory()
    brain = make_brain([text("x")] * 5)
    brain.client.responses = [text("NO: nothing worth saying")] * 20
    a = Assistant(
        device=device,
        brain=brain,
        memory=mem,
        config=RuntimeConfig(proactive=proactive),
    )
    assert run(a.run()) == []
