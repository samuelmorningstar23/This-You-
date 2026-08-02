"""The real vision path: what actually gets sent when the assistant looks."""

from __future__ import annotations

import asyncio
import base64

from edith.devices.simulator import Scene, SimulatedDevice
from edith.gate import GateConfig, VisionGate
from edith.runtime import ClaudeLooker

from .fakes import FakeClient, text


def looker(**gate_cfg):
    device = SimulatedDevice(scenes=[Scene("hob", 4.0, describes="a pan of pasta")])
    gate = VisionGate(GateConfig(**gate_cfg))
    client = FakeClient([text("A pan of pasta at a rolling boil.")])
    return device, gate, client, ClaudeLooker(client, device, gate)


def test_a_look_sends_one_image_and_one_question():
    _device, _gate, client, lk = looker()
    out = asyncio.run(lk.look("what is on the hob"))
    assert out == "A pan of pasta at a rolling boil."

    (call,) = client.calls
    content = call["messages"][0]["content"]
    images = [b for b in content if b["type"] == "image"]
    texts = [b for b in content if b["type"] == "text"]
    assert len(images) == 1
    assert len(texts) == 1
    assert images[0]["source"]["media_type"] == "image/jpeg"
    assert base64.standard_b64decode(images[0]["source"]["data"])


def test_the_vision_prompt_forbids_speculating_about_people():
    """Bystanders are in frame constantly; the prompt must not invite guessing."""
    _device, _gate, client, lk = looker()
    asyncio.run(lk.look("what is on the hob"))
    content = client.calls[0]["messages"][0]["content"]
    prompt = next(b["text"] for b in content if b["type"] == "text")
    assert "identity" in prompt.lower()
    assert "not speculate" in prompt.lower()


def test_a_look_debits_the_vision_budget():
    _device, gate, _client, lk = looker(hourly_budget=5)
    before = gate.budget_remaining()
    asyncio.run(lk.look("what is this"))
    assert gate.budget_remaining() == before - 1


def test_a_look_with_no_camera_degrades_to_a_sentence():
    class NoCamera(SimulatedDevice):
        async def capture(self):
            return None

    device = NoCamera(scenes=[Scene("void", 1.0)])
    lk = ClaudeLooker(FakeClient([]), device, VisionGate())
    out = asyncio.run(lk.look("anything?"))
    assert "not available" in out
