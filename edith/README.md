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
python -m pytest          # 61 tests, no network or API key required
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

**Vision is gated, not streamed — and the reason is battery, not the bill.**
One frame per second for an eight-hour day is $113 on Opus 5 at 768×768, or
$689 at full resolution. Gated, the same day is about **$0.47** in model tokens (see `../EDITH.md` for the all-in figure, which is $18–49/month once speech-to-text and storage are counted). But the cloud
bill is the *smaller* problem: glasses have roughly 200 mW to spend on average
if they are to last a day, against a 1–2 W thermal ceiling set by what you can
dissipate against skin. Continuous capture does not fit, which is why measured
continuous use on shipping glasses runs 2–3× shorter than rated endurance. No
cheaper model fixes that, because the cost is in the camera, the encoder, and
the radio.

So `gate.py` optimises for radio-off time and the cost saving follows for free.
It works on a 16×16 grayscale thumbnail — cheap enough to run on every frame,
and something an image sensor can produce in a low-power mode without waking the
main SoC. Run `python -m edith budget` for the arithmetic.

**The proactive path is off by default.** The runtime can decide on its own to
speak up, and there is a cheap Haiku-based judge for exactly that. It ships
disabled. Every wearable-assistant post-mortem in the research says the same
thing: an assistant that volunteers observations gets muted, and a muted
assistant has no value at all. Turning it on is a product decision with a
running cost and a mute-rate consequence; make it deliberately.

**Identity is resolved, not recognised.** E.D.I.T.H. looks at a stranger and
returns their name. Doing that in 2026 runs into an index you cannot lawfully
build (EU AI Act Art. 5(1)(e)), processing with no lawful basis (GDPR Art. 9),
and a statute that reaches you personally — Illinois BIPA defines "private
entity" to include "any individual". So this system inverts the question. Instead of *"whose face is this?"* — answered
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
not obvious — the short version is Mentra Live on MentraOS, because Meta's
toolkit exposes no microphone or speaker at all and Brilliant Labs Halo's
open-source claim does not currently hold up. Both findings are from
[`../VERIFICATION.md`](../VERIFICATION.md).

Two seams are stubbed and marked as such:

* `SharedSecretSigner` is symmetric HMAC. Production keys belong in the secure
  enclave as Ed25519, gated by a local biometric, so the roster holds only
  public keys. The `Signer` protocol is where that swaps in.
* `ClaudeLooker` sends a downscaled JPEG. The downscale is load-bearing: Claude
  bills images as 28×28-pixel patches, so 448×448 is 256 tokens against 784 at
  768×768 and 4,784 at full resolution — and 448×448 still reads signage.
