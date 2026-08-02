"""The vision gate is the cost control, so its behaviour is the thing to pin down."""

from __future__ import annotations

from edith.devices.simulator import synth_thumb
from edith.gate import GateConfig, VisionGate, thumb_distance
from edith.types import Frame


def frame(scene: str, ts: float, jitter: int = 0) -> Frame:
    return Frame(thumb=synth_thumb(scene, jitter), width=16, height=16, ts=ts)


def test_identical_thumbnails_are_distance_zero():
    a = synth_thumb("desk")
    assert thumb_distance(a, a) == 0.0


def test_different_scenes_are_far_apart():
    assert thumb_distance(synth_thumb("desk"), synth_thumb("street")) > 0.2


def test_first_frame_establishes_a_baseline_without_looking():
    gate = VisionGate()
    d = gate.consider(frame("desk", 0.0))
    assert not d.look
    assert "baseline" in d.reason


def test_a_static_scene_never_triggers_a_look():
    gate = VisionGate()
    looks = 0
    for i in range(60):
        d = gate.consider(frame("desk", i * 0.5, jitter=i % 3))
        looks += d.look
    # Sixty frames of staring at the same desk must cost exactly one look:
    # the first one, which establishes what "this desk" looks like.
    assert looks <= 1


def test_a_scene_change_triggers_exactly_one_look():
    gate = VisionGate(GateConfig(min_interval_s=0.0))
    for i in range(10):
        gate.consider(frame("desk", i * 0.5))

    before = len(gate._captures)
    looked = [i for i in range(10, 24) if gate.consider(frame("street", i * 0.5)).look]
    # One look at the new scene, then silence — not a look per frame.
    assert len(gate._captures) - before == 1, looked


def test_motion_suppresses_capture():
    gate = VisionGate(GateConfig(min_interval_s=0.0))
    gate.consider(frame("desk", 0.0))
    # A head turn: wildly different pixels frame to frame.
    d = gate.consider(
        Frame(thumb=synth_thumb("desk->street"), width=16, height=16, ts=0.5)
    )
    assert not d.look
    assert "moving" in d.reason


def test_explicit_request_bypasses_budget_and_rate_limit():
    gate = VisionGate(GateConfig(hourly_budget=0, min_interval_s=999.0))
    gate.consider(frame("desk", 0.0))
    d = gate.consider(frame("desk", 0.1), explicit=True)
    assert d.look
    assert "explicit" in d.reason


def test_hourly_budget_is_a_hard_ceiling():
    gate = VisionGate(GateConfig(hourly_budget=3, min_interval_s=0.0, settle_s=0.0))
    ts = 0.0
    for i in range(12):
        gate.consider(frame(f"scene-{i}", ts))
        ts += 0.5
        gate.consider(frame(f"scene-{i}", ts))
        ts += 0.5
    assert len(gate._captures) <= 3
    assert gate.budget_remaining(ts) == 0


def test_slow_pan_is_caught_by_comparing_against_the_last_sent_frame():
    """A gate that only compares consecutive frames misses a slow pan entirely.

    Each step is below the change threshold, so a naive implementation never
    fires even though the view ends up somewhere completely different.
    """
    gate = VisionGate(GateConfig(min_interval_s=0.0, settle_s=0.0))
    gate.consider(frame("pan-0", 0.0))
    gate.consider(frame("pan-0", 0.25))  # commits the baseline look

    ts = 0.5
    fired = False
    for i in range(1, 12):
        # Small per-step change: same scene, drifting jitter.
        d = gate.consider(frame("pan-0", ts, jitter=i * 8))
        if d.look:
            fired = True
            break
        ts += 0.5
    assert fired, "accumulated drift should eventually trip the novelty threshold"
