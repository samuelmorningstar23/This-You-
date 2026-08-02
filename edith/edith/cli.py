"""Command line entry points.

    python -m edith demo     replay a scripted day and show what the assistant did
    python -m edith budget   the unit economics, with the arithmetic shown
    python -m edith policy   what this system refuses to do, and under what law

``demo`` runs against the real API when ANTHROPIC_API_KEY is set, and against a
scripted transcript otherwise, so the loop can be demonstrated on a plane.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time

from .brain import Brain
from .devices.simulator import Scene, ScriptEvent, SimulatedDevice
from .identity import ROTATION_S, Roster, SharedSecretSigner, derive_handle
from .memory import Memory
from .policy import PROHIBITIONS
from .runtime import Assistant, RuntimeConfig
from .tools import default_registry


def _scenario() -> tuple[SimulatedDevice, Roster, dict]:
    roster = Roster()
    mj = roster.pair("mj", "MJ", disclosed={"team": "robotics"})
    handle = derive_handle(mj.secret, int(time.time() // ROTATION_S))

    device = SimulatedDevice(
        speed=800.0,
        scenes=[
            Scene("kitchen", 6.0, describes="a pan of pasta at a rolling boil"),
            Scene("hallway", 3.0, describes="a coat rack and a front door"),
            Scene("street", 6.0, describes="a bus stop; the 38 is due in 4 minutes"),
            Scene("lab", 8.0, describes="a workbench with a partly assembled drone"),
        ],
        script=[
            ScriptEvent(at_s=2.0, say="how long has this been boiling"),
            ScriptEvent(at_s=7.5, say="remember I left my keys in the blue coat"),
            ScriptEvent(at_s=10.0, say="did you catch what she said", directed=False),
            ScriptEvent(at_s=12.0, say="when's the next 38"),
            ScriptEvent(at_s=16.0, peer_handle=handle, peer_range_m=1.3),
            ScriptEvent(at_s=16.5, peer_handle="9f3c1a77b2e40d81", peer_range_m=2.6),
            ScriptEvent(at_s=18.0, say="who's in here with me"),
            ScriptEvent(at_s=20.0, say="where did I leave my keys"),
        ],
    )
    return device, roster, {handle: SharedSecretSigner(mj.secret)}


def _scripted_client():
    """Canned responses so the demo runs with no key and no network."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tests"))
    from fakes import FakeClient, text, tool  # type: ignore

    return FakeClient(
        [
            tool("look", question="how far along is the pasta"),
            text("Rolling boil — about four minutes in."),
            tool("remember", topic="keys", body="left in the blue coat"),
            text("Noted."),
            tool("look", question="when is the next 38 bus"),
            text("Four minutes."),
            tool("who_is_near"),
            text("MJ is here, from the robotics team."),
            tool("recall", query="keys"),
            text("Blue coat."),
        ]
    )


def _real_client():
    import anthropic

    return anthropic.Anthropic()


async def _run_demo(live: bool) -> int:
    device, roster, responders = _scenario()
    memory = Memory()
    client = _real_client() if live else _scripted_client()
    brain = Brain(client=client, registry=default_registry())
    assistant = Assistant(
        device=device,
        brain=brain,
        memory=memory,
        roster=roster,
        responders=responders,
        config=RuntimeConfig(proactive=False),
    )

    mode = "live Claude" if live else "scripted (no API key found)"
    print(f"Running a scripted day against {mode}.\n")

    turns = await assistant.run()

    for t in turns:
        used = f"  [{', '.join(t.tools_used)}]" if t.tools_used else ""
        print(f'  you: "{t.prompt}"')
        print(f"edith: {t.reply}{used}")
        print()

    if device.displayed:
        print("On the display:")
        for card in device.displayed:
            print(f"  {card.title} — {' | '.join(card.lines)}")
        print()

    report = assistant.cost_report()
    print(
        f"{report['turns']} turns, {report['vision_calls']} vision calls, "
        f"{report['input_tokens']} in / {report['output_tokens']} out "
        f"= ${report['usd']:.4f}"
    )
    if not live:
        print("(token counts are from the scripted client, not real usage)")
    return 0


def _budget() -> int:
    """The arithmetic that decides whether this is a product or a science project."""
    price_in, price_out = 5.0, 25.0  # $/MTok, Claude Opus 5 list
    # Claude bills images as 28x28-pixel patches: ceil(w/28) * ceil(h/28).
    full = 4_784  # full-resolution cap (2576px long edge)
    detail = 784  # 768x768
    ambient = 256  # 448x448 — still reads signage

    hours = 8
    frames_naive = 3600 * hours

    print("If it streamed vision the way the film implies (1 fps, 8 hours):\n")
    for label, tok in (("full-res", full), ("768x768", detail), ("448x448", ambient)):
        t = tok * frames_naive
        print(
            f"  {label:>9}: {tok:,} tok/frame -> {t/1e6:6.1f}M tokens"
            f" = ${t/1e6*price_in:6.2f}/wearer/day"
        )

    print("\nGated, the way this runtime does it:\n")
    looks, turns = 40, 40
    text_in, text_out = 1_500, 120
    vis = looks * ambient
    tin, tout = turns * text_in, turns * text_out
    daily = (vis + tin) / 1e6 * price_in + tout / 1e6 * price_out
    print(f"  {looks} gated looks at {ambient} tok = {vis:,} tokens")
    print(f"  {turns} spoken turns at ~{text_in:,} in / {text_out} out")
    print(f"  = ${daily:.2f}/wearer/day, about ${daily*30:.0f}/month")
    print(
        "\n  Prompt caching on the stable system prompt takes the text input to"
        "\n  roughly a tenth of that on every turn after the first."
    )

    print(
        "\nBut the bill is the smaller problem. The binding constraint is power:"
        "\ncontinuously encoding and radioing a frame per second is what turns a"
        "\nsix-hour battery into a thirty-minute one on shipping hardware. The"
        "\ngate optimises for radio-off time; the cost saving comes along for free."
    )
    return 0


def _policy() -> int:
    print("This system will not do the following, and has no tool that could:\n")
    for p in PROHIBITIONS:
        print(f"  {p.key}")
        print(f"    {p.summary}")
        print(f"    {p.basis}\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="edith", description=__doc__)
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("demo", help="replay a scripted day")
    sub.add_parser("budget", help="show the unit economics")
    sub.add_parser("policy", help="show what is refused, and why")
    args = parser.parse_args(argv)

    if args.cmd == "budget":
        return _budget()
    if args.cmd == "policy":
        return _policy()
    if args.cmd == "demo":
        live = bool(os.environ.get("ANTHROPIC_API_KEY"))
        return asyncio.run(_run_demo(live))

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
