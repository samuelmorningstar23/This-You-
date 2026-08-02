# edith

An E.D.I.T.H.-class glasses assistant, built out of components that exist.

This is the working half of [`../EDITH.md`](../EDITH.md), which takes the glasses
from *Spider-Man: Far From Home* capability by capability and works out what is
buildable in 2026, what is merely hard, and what is illegal. This package builds
the buildable part.

```
python -m edith demo      # replay a scripted day; runs live if ANTHROPIC_API_KEY is set
python -m edith budget    # the unit economics, with the arithmetic shown
python -m edith policy    # what it refuses to do, and under what law
python -m pytest          # 56 tests, no network or API key required
```

## What it is

A hardware-agnostic runtime for an always-available assistant that lives in your
ear and on a narrow strip of glass. Speech and camera in, speech and text out,
with a memory, a tool surface, and a way to answer "who is this person" that
does not involve a face database.

```
   camera ──► thumbnail ──► VisionGate ──┐
                                         ├──► Brain (Opus 5) ──► speech
   mic ──────► utterance ────────────────┤         │             HUD card
                             (directed?) │         ├──► tools ──► memory
   radio ────► advertisement ──► Roster ─┘         │              camera
                             (resolvable?)         └──► Haiku, for
                                                        "is this worth
                                                         interrupting?"
```

| Module | What it does |
|---|---|
| `gate.py` | Decides when the assistant is allowed to look. The cost control. |
| `brain.py` | The Claude loop: two model tiers, tool round trips, refusal handling. |
| `identity.py` | Resolves nearby people by consent. Cannot identify a stranger. |
| `memory.py` | On-device episodic log and durable notes, searchable. |
| `policy.py` | The prohibitions, each with the statute it comes from. |
| `runtime.py` | Wires the sensor loops together. |
| `devices/` | The hardware seam, plus a simulator so all of this runs in CI. |

## The three decisions that matter

**Vision is gated, not streamed.** Sending one frame per second to a
multimodal model for an eight-hour day costs roughly **$690 per wearer per day**
at current Opus pricing. The same day with change-detection gating, a settle
check, and an hourly budget costs about **$0.64**. That ratio — three orders of
magnitude — is why `gate.py` is the first file to read. It works on a 16×16
grayscale thumbnail, which is cheap enough to run on every frame and is
something a camera ISP can produce without waking the main SoC.

Run `python -m edith budget` for the arithmetic.

**The proactive path is off by default.** The runtime can decide on its own to
speak up, and there is a cheap Haiku-based judge for exactly that. It ships
disabled. Every wearable-assistant post-mortem in the research says the same
thing: an assistant that volunteers observations gets muted, and a muted
assistant has no value at all. Turning it on is a product decision with a
running cost and a mute-rate consequence; make it deliberately.

**Identity is resolved, not recognised.** E.D.I.T.H. looks at a stranger and
returns their name. Doing that in 2026 means untargeted face-database building
(EU AI Act Article 5) and per-scan statutory damages under Illinois BIPA. So
this system inverts the question. Instead of *"whose face is this?"* — answered
by a database of people who never agreed to be in it — it asks *"is there
someone here who will tell me who they are?"*, answered by that person's own
device, live, and revocably.

That is the [Presence Resolution Protocol](../SOLUTION.md) from this repository
applied to physical proximity. A paired contact broadcasts a rotating handle; it
becomes a name only when their device answers a fresh challenge. Revocation is
instant and needs no propagation, because nothing durable was ever issued. An
unpaired person yields a handle and nothing else — and there is no other code
path, which `test_no_api_exists_to_identify_a_face` pins down.

## What it will not do

Six capabilities are refused in code rather than in a prompt, because a prompt
is advisory and is attackable by injection from anything the camera reads. They
are refused by *absence*: no tool exists that could reach them, and a test
asserts the registry stays that way.

`python -m edith policy` prints all six with citations. Briefly: identifying a
stranger, recording with the indicator suppressed, reading someone else's
messages, commanding a weaponised effector, flying beyond visual line of sight,
and profiling bystanders.

The drone-strike scene is the film's own argument against the system. We are not
going to be the ones who miss the point.

## Running it on real hardware

The runtime depends on `devices/base.py:Device` and nothing else — four inputs
(frames with a thumbnail, segmented speech with a directed-at-me flag, presence
advertisements, on-demand capture) and two outputs (speak, show). Nothing in the
interface assumes 6DoF pose, world anchors, depth, or hand tracking, because
almost nothing shipping in this form factor has them.

To target a real pair of glasses, write an adapter that satisfies that Protocol.
See [`../EDITH.md`](../EDITH.md) for which device to pick and why the answer is
not obvious.

Two seams are stubbed and marked as such:

* `SharedSecretSigner` is symmetric HMAC. Production keys belong in the secure
  enclave as Ed25519, gated by a local biometric, so the roster holds only
  public keys. The `Signer` protocol is where that swaps in.
* `ClaudeLooker` sends a downscaled JPEG. The downscale is load-bearing — full
  resolution is ~4.8K input tokens per frame against ~1.1K downscaled, and that
  still reads signage.
