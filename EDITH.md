# E.D.I.T.H., costed

*What Tony Stark's glasses actually do, what of it you can build in 2026, and what the law and physics say about the rest.*

**Date:** August 2026 · **Status:** research complete · builds into [`edith/`](./edith/)

---

## The short answer

You can build most of E.D.I.T.H. The parts you cannot build are not the parts you would guess.

The AI is the easy half. A glasses assistant that hears you, sees what you are looking at, remembers your life, answers in your ear, and puts a line of text above your right eye is assembled from shipping components and costs about **$0.50 per wearer per day** to run. That is [`edith/`](./edith/), and it works.

What stops you is a different list. **The display is a physics problem** — the wide, bright, world-locked overlay is forbidden by conservation of etendue at anything like eyeglass weight, and no amount of money fixes it this decade. **Continuous perception is a thermal problem** — a device touching your face has about 1–2 W to spend, which is why Meta's own glasses cap video at 30 minutes. **Recognising strangers is a legal problem** — not hard, illegal, and specifically illegal in ways that reach you personally. **The drones are a statute problem** — arming one is a federal offence with a named penalty. **The satellite feed does not exist** — the company that promised it went under without launching.

And the single most important finding is not technical at all. Every previous attempt at this product died, and almost none of them died of AI quality. Google Glass died of social rejection. Humane died of heat and latency and then bricked ten thousand devices. Rabbit sold 130,000 units and kept 5,000 daily users. The one commercial success, Ray-Ban Meta, succeeded by *not* being E.D.I.T.H.: no display, no autonomy, just a camera and a voice in a frame people already wanted to wear.

So the recommendation is uncomfortable but well-evidenced: **build the assistant, ship it audio-first without a display, and replace stranger-recognition with consent-based resolution.** Details below.

---

## 1. What E.D.I.T.H. actually does

Worth pinning down before deciding what is buildable, because the film is more extreme than memory suggests.

E.D.I.T.H. — *Even Dead, I'm the Hero* — is bound to its wearer by a combined retinal and biometric scan, and describes its own scope in one line: *"I have access to the entire Stark Global Security network, including multiple defense satellites, as well as back doors to all major telecommunication networks."*

On screen it:

- **Identifies everyone in view, unprompted.** On first wear it tags every passenger on a school bus, each with a summary of their digital footprint, including *the last text message they sent*.
- **Reads and writes arbitrary phones.** Peter reaches into a classmate's phone and deletes a photo. That is destructive write access to a third party's device, performed casually.
- **Kills on an unqualified voice command.** An offhand request about a classmate is resolved into `Target is Brad Davis. Initiating strike.` There is no confirmation, no identity check-back, and no abort the wearer knows about — Peter has to physically chase the drone, because he does not know how to cancel it.
- **Commands an orbital weapons platform.** Armed drones are dropped from a Stark satellite and reach a moving bus in minutes. Hundreds are controllable at once, as flocks or individually.

And the detail that indicts the whole design: **the only confirmation gate in the entire film is on transfer of ownership.** E.D.I.T.H. will not change hands without a "Confirm" — but it will launch a strike on a teenager without one. That single interlock, the only one there is, is exactly the mechanism that hands the arsenal to Quentin Beck.

That is not a plot hole. That is what happens when you build every capability and gate only the one that protects the *asset*.

---

## 2. The verdict table

| Capability | 2026 verdict |
|---|---|
| Conversational voice assistant in glasses | **Ships today** |
| Biometric binding to one wearer | **Ships today** — Face ID / StrongBox, better than a retinal scan |
| Answering questions about what you're looking at | **Ships today**, gated |
| Small monocular text HUD | **Ships today** — 20–30° |
| Remembering your day and recalling it | **Buildable** — retrieval quality is the weak link |
| Knowing who's near you, *with consent* | **Buildable** — §7 |
| Wide-FOV, full-colour, world-locked, sunlight-readable HUD | **Impossible** this decade — §3 |
| Continuous all-day perception | **Impossible** on-glasses — §4 |
| Identifying strangers by face | **Illegal**, and personally so — §6 |
| Reading other people's messages | **Illegal** — CFAA, Stored Communications Act |
| Commanding a drone fleet from one voice | **Illegal** without waiver — 14 CFR 107.35 |
| Arming a drone | **Illegal** — $25,000/violation, no private exception |
| Live satellite video of an arbitrary point | **Does not exist** — §8 |
| Recent satellite imagery on demand | **Ships today**, hours not seconds — §8 |
| Free-space holograms (Mysterio) | **Impossible** — no 2026 physics permits it |

---

## 3. The display: why the Iron Man HUD is not coming

The E.D.I.T.H. HUD asks for four things at once: wide field of view, full colour, world-locked, readable in sunlight — in a normal pair of glasses. Each exists in 2026 in isolation. They have never been combined, and the obstacle is not effort.

**The governing constraint is conservation of etendue**, which Bernard Kress (formerly HoloLens optical architect, now at Google) states as:

> (microdisplay size) × (display engine NA) = (eyebox) × (FOV in air)

Large FOV *and* large eyebox *and* small optics would require the left side to be smaller than the right. The law forbids it. You choose two.

The consequences are brutal in practice:

- **Waveguide efficiency collapses as FOV grows.** A surface-relief-grating waveguide delivers ~4,500 nits/lm (~10% efficiency) at 20° FOV, and only ~1,300 nits/lm (~3%) at 30°.
- **Meta's Orion — the closest thing to an E.D.I.T.H. HUD at 70° — delivers 300–400 nits to the eye** from microLED projectors emitting *hundreds of thousands* of nits. That is 0.1–0.3% end-to-end. It weighs 98 g and costs roughly $10,000 a unit.
- **Sunlight is the hardest wall.** An ambient contrast ratio of 10:1 against a 3,000-nit sunny scene needs ~30,000 nits at the eye. Orion is ~100× short. Every wide-FOV device that ships instead *dims the world*: Snap Specs' electrochromic lenses go fully opaque in 10 seconds.

What actually ships in a wearable weight is 20–30°:

| Device | FOV | Display | Weight | Price |
|---|---|---|---|---|
| Meta Ray-Ban Display | 20° diag, monocular | 600×600 LCoS, 5,000 nits | 69 g | $799 |
| Even Realities G2 | 27.5° | 640×350 green microLED, 1,200 nits | 35 g | $599 |
| Vuzix Z100 | 30° | 640×480 green | 38 g | ~$500 |
| Snap Specs (preorder) | 51° | LCoS colour | 132 g | $2,195 |

Two corrections to common belief. Ray-Ban Display is **LCoS, not microLED** — an OmniVision panel emitting about 1 lumen into a Lumus geometric waveguide. And it is **head-locked, not world-locked**: its only spatial sensor is an IMU. There is no SLAM, no 6DoF, no eye tracking. The HUD sits at a fixed spot below-right of your sightline and stays there.

**The design answer** is a small glanceable monocular text strip, or no display at all. Not an overlay. Geometric waveguides (3–7× more efficient than diffractive, no rainbow artefacts) and silicon-carbide substrates (n=2.6, demonstrated 55° at 87% transmittance in a 2.12 g lens) are the credible paths past 30° — but they are 2028+ paths, not procurement options.

---

## 4. The power wall: why continuous perception is impossible on glasses

This is the constraint people consistently underestimate, because it is not about compute.

- **~200 mW average** is the whole budget for all-day use, from a ~3 Wh battery that is itself capped by a 20–30 g electronics weight allowance in a ≤50 g device.
- **1–2 W instantaneous** is the thermal ceiling. IEC 62368-1 caps user-accessible surfaces at 48 °C; comfort targets are ~40 °C on metal. There is no fan and almost no thermal mass, and the light engine sits millimetres from the SoC on your temple.

The observable consequence is an endurance gap between rated and continuous use. Ray-Ban Display is rated for up to 6 hours mixed-use; independent measurement puts continuous heavy use at **roughly 2–3 hours** — Wirecutter reports "almost three hours with continuous use", Tom's Guide saw 40% remaining after 90 minutes. So a 2–3× gap, and it is the budget above that explains it, not any single vendor figure.

*A correction I owe the reader:* the first draft of this document claimed the gap was 12× — that continuous AI drained the device in 30 minutes. That figure has no primary source and the measurements contradict it; it most likely conflates the livestream cap on a *different* product, the Neural Band's 30-minute fast charge, or the 30-hour glasses-plus-case total. Related: the per-clip recording default is 3 minutes at **1080p30** and is **user-adjustable**, not a hard cap, and Meta nowhere attributes it to thermals. Details in [`VERIFICATION.md`](./VERIFICATION.md).

Three consequences that shape any real design:

1. **Duty-cycled sensing is the only affordable always-on mode.** ST's VD55G4 sensor draws <2 mW in event/wake mode versus ≤35 mW streaming at 60 fps. A 2026 research build sustained 11.8 hours of continuous on-device inference at 65.6 mW.
2. **On-glasses LLM means ~1B parameters, and that is the ceiling.** Snapdragon AR1+ runs Llama 3.2 1B locally; Ray-Ban Display has 2 GB of RAM. Meta's own position is that wearables are limited to "hundreds of MBs" of model.
3. **Bluetooth cannot carry vision.** Best-case BLE application throughput is ~1.3–1.4 Mbps; a 512×512 30 fps stream at 10:1 compression needs 6.3 Mbps. Any vision path is Wi-Fi, or it is not a path.

One counter-intuitive result worth internalising: **moving speech recognition onto the glasses makes total system power 7% worse**, because compressed audio is already cheap to transmit. On-device hand tracking saves 14%; ASR does not. Do not assume local is cheaper — measure.

The correct architecture is therefore **glasses as sensor, phone as inference, cloud for world knowledge**.

---

## 5. Seeing and speaking

### Vision

Claude bills images as 28×28-pixel patches — `ceil(w/28) × ceil(h/28)` tokens, evaluated *after* any downscale to the tier limit — so a 768×768 frame is 784 tokens, 448×448 is 256, and the high-resolution tier (Claude 4.7 and later) caps at 4,784. The older `(w×h)/750` rule is a superseded approximation that lands within a few percent but is never exact. Streaming one frame a second for eight hours:

| Frame size | Tokens/day | Cost/day (Opus 5) |
|---|---|---|
| Full resolution | 138M | $689 |
| 768×768 | 22.6M | $113 |
| 448×448 | 7.4M | $37 |

Survivable, if you had to. **But the bill is the smaller problem.** Continuously encoding and radioing a frame per second is what turns a six-hour battery into a thirty-minute one. No cheaper model fixes that, because the cost is in the camera, the encoder and the radio.

So gate on **radio-off time** and the money follows. The full cascade, cheapest first: an IMU gate (suppress capture while the head is turning); a photometric or embedding change-detector (a thumbnail diff costs microseconds; YOLOv11-n is 0.73 ms/frame on a current phone NPU, MobileCLIP-S0 is 3 ms); on-device OCR and captioning to *text*, which is what gets stored; and only then a cloud call on a selected keyframe. That takes ~3,600 frames/hour down to ~60, and the vision bill to cents.

[`edith/gate.py`](./edith/gate.py) implements the thumbnail tier — the cheapest one that needs no accelerator — and `python -m edith budget` prints the arithmetic.

### Voice

**Claude has no audio modality.** No speech in, no speech out, no realtime endpoint; the OpenAI-compatibility layer explicitly strips audio. A Claude-based assistant is structurally a cascade: streaming ASR → Claude → TTS. This is a fact to design around, not a gap to wait out.

The latency target is brutal and worth stating precisely. Human conversational turn-taking has a **modal gap of ~200 ms**, with 51–55% of transitions under 200 ms — and it is cross-culturally universal, not an English artefact. Nobody is close: measured P50 turn latency for production voice platforms runs **1.73 s (ElevenLabs) to 3.16 s (Synthflow)**.

The gap is not ASR (~300 ms) and not TTS (75–90 ms time-to-first-audio, no longer the bottleneck). It is endpointing plus LLM time-to-first-token.

Since you cannot hit 200 ms, close it *perceptually*, the way humans do — human speech production needs 600 ms for one word and ~1500 ms for a sentence, so humans are planning while still listening. Start TTS on the first sentence rather than the full completion. Fold end-of-turn detection into the ASR model (Deepgram Flux emits `EagerEndOfTurn`). Run a two-tier brain: a fast small model for conversational reflex, Claude for anything that needs reasoning.

Two procurement traps found in the research, both of which surface late:

- **openWakeWord's pretrained weights are CC BY-NC-SA — non-commercial** — even though the code is Apache 2.0. Train your own or license Porcupine, and decide now rather than at legal review.
- **AssemblyAI bills on session wall-clock, not audio.** An always-connected device pays for silence and gets auto-billed three full hours on an unterminated session. Deepgram bills per minute of audio. Same latency class, radically different curve for a wearable.

---

## 6. The face: the one capability that would end you

Identifying strangers is the defining E.D.I.T.H. move and the one thing on this list that is not hard at all. It is a solved computer-vision problem that two Harvard students wired to Ray-Ban Metas in October 2024 — the **I-XRAY** demo chained PimEyes reverse face search into FastPeopleSearch and returned names, home addresses, phone numbers, relatives and partial SSNs *while they were talking to strangers on campus*. They deliberately did not release the code.

Three separate things stop you shipping it, and it is worth being precise about which, because the internet gets this wrong:

**1. The index is unbuildable.** EU AI Act **Article 5(1)(e)**, in force since 2 February 2025, prohibits creating or expanding facial-recognition databases through untargeted scraping of facial images from the internet or CCTV — which is exactly how every usable stranger-ID index is built. Penalty: up to €35M or 7% of worldwide turnover.

**2. The processing has no lawful basis.** A passerby's face is GDPR Article 9 special-category data and they have consented to nothing.

**What is *not* the objection:** Article 5(1)(h)'s real-time remote biometric identification ban is **scoped to law enforcement** and does not by its terms reach a private wearable sold to consumers. Citing 5(1)(h) at a private product is a common and discrediting error.

Two caveats on that, though, because the scope is wider than "not us". Article 3(46) defines "law enforcement" to include activities carried out by such authorities **or on their behalf**, and Article 3(45) reaches any body "entrusted by Member State law to exercise public authority" — so a private vendor operating *for* police is squarely inside the prohibition. And Article 5(5) leaves Member States free to impose **stricter national rules** on private use, so "not banned at EU level" is not "permitted in every member state".

**3. It reaches you personally.** Illinois BIPA §10 defines "private entity" to include **"any individual"** — a hobbyist is a proper defendant. Damages are $1,000 per negligent and $5,000 per *intentional or reckless* violation, though these are liquidated-damages floors ("or actual damages, whichever is greater") and discretionary under *Cothron*, not an automatic multiplier. Illinois SB 2979 (August 2024) limits repeat collection from the same person by the same method to a single recovery — so the per-scan accrual theory is displaced, though the amendment carries no retroactivity clause and it took *Clay v. Union Pacific* (7th Cir., April 2026) to hold it retroactive, a ruling that does not bind Illinois state courts. Texas CUBI has no private right of action but its Attorney General took **$1.4B from Meta** and $1.375B from Google.

You cannot buy your way out either: the 2022 ACLU settlement **permanently bars Clearview from selling to any private entity in the US**.

And the clearest signal of all: Meta shipped face-recognition code in its glasses companion app, and **scrubbed it within 48 hours of being caught** in June 2026.

---

## 7. The replacement: resolve, don't recognise

Here is the useful part. The *valuable* half of "who is this person" survives the legal constraint completely, if you invert who is doing the asserting.

- **Recognition** asks *"whose face is this?"* — answered by a database of people who never agreed to be in it.
- **Resolution** asks *"is there someone here who will tell me who they are?"* — answered by that person's own device, live, and revocably.

This is the [Presence Resolution Protocol](./SOLUTION.md) from this repository applied to physical proximity, and the law already draws the line in the same place: **AI Act Annex III excludes systems whose sole purpose is "to confirm that a specific natural person is the person he or she claims to be."** Identification searches a population for a face. Verification checks a claim its subject is making about themselves. This is verification.

(Timing note, since it cuts both ways: Regulation (EU) 2026/1744, in force 27 July 2026, left that carve-out untouched but **deferred the Annex III high-risk obligations from 2 August 2026 to 2 December 2027**. So remote biometric identification is classified high-risk today without the provider and deployer duties yet applying. Building on the deferral would be unwise; it is a delay, not a repeal.)

Every layer is shipped technology:

1. **A rotating, key-gated beacon.** Copy the Apple/Google Exposure Notification key schedule almost verbatim — AES-derived rolling identifiers rotating in lockstep with the BLE resolvable private address, unresolvable to anyone not given the key. Apple's Find My is a second precedent.
2. **A live signed challenge.** The handle becomes a name only when the peer's device signs your nonce with an enclave-held key gated by their biometric. This is PRP's RESOLVE verb. Revocation is instant and needs no propagation, because nothing durable was ever issued.
3. **Ranging, for disambiguation only.** This is where I had to correct myself: **UWB time-of-flight is not relay-proof.** The Ghost Peak attack (USENIX Security 2022) collapsed a real 12 m separation to a reported 0 m against Apple's U1 with ~$65 of hardware. So ranging answers "which of the five people in front of me signed my nonce" — genuinely useful — and never "should I believe them". Bluetooth Channel Sounding (Core 6.0, ±20 cm) is the fallback where UWB is absent, which is most handsets.
4. **Selective attribute disclosure.** SD-JWT is now **RFC 9901** (November 2025); W3C VC Data Model 2.0 reached Recommendation in May 2025; OpenID4VP 1.0 went Final in July 2025. The standards landed while nobody was looking.

The honest risk is not cryptographic. It is that proximity social discovery has repeatedly died of network effects — Color Labs raised $41M, hit ~1M downloads, fell under 100k actives within six months, and was dead by 2012. **So the design must be useful at N = your own contacts, not N = your city.** Ours is: it answers "is this really them" for people you already know, which is valuable on day one with a roster of five.

Implemented in [`edith/identity.py`](./edith/identity.py). There is no `identify(image)` and no code path that produces one, which a test asserts.

---

## 8. The drones and the satellites

**Almost every individual motion E.D.I.T.H.'s drones perform is shipping technology.** Waypoint missions, follow-me, visual object tracking, centimetre precision landing, and coordinated swarms are all stock in MAVSDK v4 / PX4 / ArduPilot with public SDKs. The Mysterio-illusion analogue is real and solved: the world-record swarm is **33,615 drones over Dujiangyan in May 2026**, flown from a single ground control computer.

What stops you is statute, in three places:

- **Operating an armed drone is federally prohibited.** FAA Reauthorization Act 2018 §363, at 49 U.S.C. 44802 note. Two precisions worth having right: the text reads "**Unless authorized by the Administrator**, a person may not operate an unmanned aircraft… equipped or armed with a dangerous weapon" — so there is an authorization pathway rather than a flat ban, and it is not restricted to government operators. And the operative penalty is not the $25,000 in the statute: inflation-adjusted under 14 CFR 13.301 it is **$31,207 per violation** for violations on or after 30 December 2024.
- **One pilot, one aircraft.** 14 CFR 107.35 bars manipulating flight controls **or** acting as remote PIC **or** acting as visual observer for more than one unmanned aircraft at a time. Every US light show runs on a waiver.
- **BVLOS is not routine.** Part 108 is *not law* as of August 2026. But treat this as **volatile rather than settled**: the Fall 2025 Unified Agenda projected a July 2026 final rule and Pub. L. 118-63 §930 set a statutory deadline of 16 January 2026. Both have passed, so the rule is overdue and could publish at any time. Re-verify before relying on it.

There is now a fourth, newer wall that catches people out: since **22 December 2025 the FCC Covered List bars all foreign-produced UAS and critical components from new equipment authorization**, so the DJI hardware most people would prototype on can no longer be newly imported or marketed in the US. (The NDAA §1709 audit that would have cleared DJI was simply never performed — no agency took it on before the deadline, so the listing happened by default rather than by a finding.)

**The satellite feed is the purest fiction on the list.** You can genuinely buy overhead imagery through public APIs — Umbra publishes a full SAR price list ($675–$5,650 per collect) and its Canopy API self-serves tasking, SkyFi resells 50 cm optical at ~$12/km², and Copernicus gives away **12 TB/month of Sentinel-2** — but the unit of delivery is *a still image, hours to days after you ask*. Realistic tasking-to-imagery is 4–7 hours.

Live video of an arbitrary point does not exist. The best commercial products are a **30–120 second SkySat clip** over a ~1×2.5 km footprint, or Satellogic's 1 m monochrome video at 10 fps for up to 60 seconds — single-pass artifacts, not persistence. EarthNow, the one funded attempt at continuous real-time global video, ceased operations without launching despite Gates, SoftBank and Airbus money.

(One myth to retire: there is no fixed statutory 25 cm resolution cap. The 2020 rewrite of 15 CFR Part 960 replaced it with tiering benchmarked against foreign availability, and NOAA permanently expired 39 Tier 3 conditions in July 2023.)

---

## 9. The graveyard, which is the most useful section

Every prior attempt died, and the causes were not AI quality.

| Product | What happened |
|---|---|
| **Google Glass** | $1,500. Consumer sales halted 9 months after open sale. Died of *social rejection* — bans, and the word "Glasshole" — not technology. Enterprise pivot ended 2023. |
| **Humane AI Pin** | $699 at launch, cut to $499; **mandatory $24/mo, never discounted**. ~10,000 shipped against a 100,000 target, with **returns exceeding sales** May–Aug 2024 *(from a leaked internal dataset Humane disputed, not a disclosure)*. Thermal failure: executives used ice packs before demos, the projector throttled at ~9 minutes. Cloud service ended 28 Feb 2025 and **the devices lost their functions**. Platform, talent and 300+ patents to HP for $116M — excluding the device business. |
| **Rabbit R1** | ~130,000 claimed sold (self-reported). Widely quoted as "5,000 daily actives" — **that number is a correction casualty**: The Verge corrected it to 5,000 *concurrent* users, against ~20,000 daily and a 34,000 peak. So roughly 80% non-daily use, not 96% abandonment. Still terrible; the "Large Action Model" never worked, and the software turned out to be an Android app. |
| **HoloLens** | 579 g and 566 g. Both dead. Head-worn compute is a weight problem before it is anything else. |
| **Snap Spectacles** | 220,000 units, **>$40M inventory write-off**, hardware layoffs. |
| **Ray-Ban Meta** | The one success — *because it has no display and no autonomy*. |

Consolidation is now fast and unsentimental: Humane→HP, Limitless→Meta, Bee→Amazon.

The rules that fall out of this are not subtle:

1. **No display in v1.** Every display-bearing consumer product either died or shipped badly compromised. Ray-Ban Display, with Meta's budget, takes *upwards of 10 seconds* to load a message over its BLE link and has no third-party app ecosystem.
2. **70 g is a hard ceiling; 45 g is the target.** Weight is not a spec line, it is the gate on whether anyone wears it for eight hours.
3. **Budget thermals before compute.** This rules out on-device LLM inference as a v1 plan.
4. **Never make the device useless without your servers.** Humane's cloud went dark on a scheduled date and took every cloud feature with it.
5. **No subscription for the AI in v1.** Humane's $24/mo was among the most-cited return reasons.
6. **Assume ~96% churn unless you have one specific, repeated, unavoidable job.** Only two jobs have demonstrated retention: hands-free capture of conversations you would otherwise lose, and point-of-view photo/video.
7. **Design the social contract before the product.** Glass died of it. New York banned camera eyewear from 1,200+ court facilities in July 2026. There is no US statute requiring a recording LED — it is a manufacturer choice — but it is the only claim you can make to a bystander, which is why Meta now permanently disables the camera on detecting LED tampering.

---

## 10. What to build

### The device

This is the section verification changed most, so it is worth stating what is actually true about Meta's platform rather than the simpler story I had.

**Meta's Wearables Device Access Toolkit is more capable than I first claimed, and more limited in a different place.** It entered developer preview on 30 October 2025 and is still in preview. `mwdat-camera` *is* a third-party camera-stream SDK — HEVC video streaming with configurable frame rates — and it is the toolkit's flagship capability. But **it exposes no microphone and no speaker at all**: the Android SDK has exactly four modules (core, camera, display, mockdevice), and audio appears nowhere in either changelog. The Web Apps track lists Microphone explicitly as unsupported.

So the real shape is: you *can* build a phone app that streams video off the glasses, runs your own AI on it, and renders results to the Display — using **the phone's** microphone for voice. You *cannot* bind to Meta's wake word, use the glasses' own mics or speakers, run always-on in the background, or distribute beyond invited testers. For an assistant whose entire premise is hands-free and always-available, "hold your phone up to talk, foreground only, invite-only distribution" is disqualifying — but for the reason above, not the one I originally gave.

Ranked alternatives:

1. **Mentra Live — $349, 43 g**, on **MentraOS (MIT licensed, verified open)**. 12 MP/119° camera, real-time STT, raw audio access, WebRTC/RTMP streaming, permissions framework. **No display** — which §9 argues is a feature for v1, not a compromise. Ships in days, no subscription. Mentra's own Mach1 has a display and *no camera*; within their line you pick one.
2. **Brilliant Labs Halo — $399, just over 40 g.** Camera *and* colour display *and* mics *and* bone-conduction speakers, with host-driven SDKs (Python / Flutter / Web Bluetooth) plus an on-device Lua VM. Three caveats, all found by verification: it is **BLE-only with no Wi-Fi**, which §4 says caps the vision path; the "totally open source" claim **does not hold today** — the firmware repo 404s and no hardware design files are published, only the host SDK and an emulator; and it is at the very start of first shipments with the companion app still listed as coming soon. Promising, and the right bench device, but not the safe pick this month.
3. **Project Aria Gen 2** as a research rig — 4 CV cameras, 8 mics, on-device VIO and eye tracking. Not a product, but gaze is the single best keyframe selector there is, and nothing purchasable gives it to you.

**Recommendation: Mentra Live for v1** — audio-first, no display, genuinely open stack, and the only candidate whose claims all survived checking. Keep a Halo on the bench for when you want a display, and rent a Snap Spectacles '24 dev kit at $100/month if you ever genuinely need 6DoF.

### The architecture

```
glasses (sensor + speaker)  ──Wi-Fi──►  phone (gating, ASR, small model)  ──►  cloud (Claude)
     thumbnail + audio + IMU              on-device cascade, memory            reasoning, tools
```

Do not put the spatial layer on the glasses. Nothing purchasable does 6DoF. Use ARCore Geospatial (free, 87+ countries, ~1 m typical) on the *phone* if you need geo-anchors. Treat Azure Spatial Anchors as deleted — Microsoft retired it in November 2024.

For the agent: MCP's 2026-07-28 revision **went stateless** (sessions and the initialize handshake removed), which is a gift for a device that drops connectivity constantly. For proactivity, ProMemAssist gives the only published decision rule with real thresholds — `utility = 0.6·importance + 0.4·relevance − costs`, deliver above 0.75 — and it beat an always-speak baseline 24.6% to 9.3% on positive engagement. Do not trust memory benchmarks: changing the scoring target flips retrieval ranking on 83–94% of LOCOMO queries.

### The cost

| Item | |
|---|---|
| Mentra Live | $349 one-off |
| Vision, gated (~40 looks/day at 448×448) | ~$0.05/day |
| Voice turns (~40/day, cached prompt) | ~$0.40/day |
| Streaming ASR (Deepgram, per-audio-minute) | ~$0.10/day |
| **Running total** | **≈$0.55/wearer/day, ~$17/month** |

Against naive continuous streaming at $113–689/day. The gate is the product.

---

## 11. What we are not building

Six capabilities are refused in [`edith/policy.py`](./edith/policy.py) — in code, not in a prompt, because a prompt is advisory and attackable by injection from anything the camera reads. They are refused by *absence*: no tool exists that could reach them, and a test keeps the registry that way. `python -m edith policy` prints them with citations.

Stranger identification. Covert capture. Reading other people's accounts. Weaponised effectors. Beyond-line-of-sight autonomous flight. Bystander profiling.

The film makes this argument better than any policy document could. E.D.I.T.H. will kill a teenager on an offhand voice command without asking, and will not change ownership without a confirmation. It gates the asset and not the human being. Building the same capability set with the same single interlock is not a homage; it is missing the point of the story you are homaging.

---

## Method and confidence

Produced by a 14-angle parallel research pipeline (1.79M tokens, 718 tool calls, all 14 returning), then a 10-claim adversarial pass in which each load-bearing claim was handed to an agent instructed to **refute** it, fetch primary sources, and treat its own training data as stale.

That pass came back: **1 confirmed, 4 confirmed with material caveats, 5 partly wrong.** Every correction is folded into the text above and itemised in [`VERIFICATION.md`](./VERIFICATION.md). The ones that changed an argument rather than a detail:

- **The 12× battery gap was wrong.** It is 2–3×. The claim had no primary source; the physics underneath it did, so the section is now argued from the mW budget instead.
- **Meta's toolkit does have camera streaming** — my claim that it did not was backwards. What it lacks is any microphone or speaker access at all, which changes the reason Ray-Ban Display is unsuitable without changing the conclusion.
- **Halo is not verifiably open source** and is barely shipping, which demoted it from first choice to bench device.
- **Rabbit's "5,000 daily users"** was corrected by its own source to 5,000 *concurrent*, against ~20,000 daily. The uncorrected figure is still in wide circulation.
- **Arming a drone is not a flat ban** — the statute reads "unless authorized by the Administrator" — and the penalty is $31,207, not the $25,000 in the 2018 text.

Three assumptions I brought in were also overturned along the way: Claude's image cost is 28×28 patches, not `(w×h)/750`; the AI Act's real-time biometric ban is law-enforcement-scoped; and UWB time-of-flight is not relay-proof (Ghost Peak), which changed the assurance model in the code, not just the prose.

The pattern in what failed is worth naming: **every claim that broke was one that gets repeated rather than sourced** — a round number with no document behind it, a marketing line about open source, a press figure whose correction never caught up with it.

Coverage gaps, declared rather than papered over: enterprise and industrial wearables were not surveyed; non-US/EU regulatory regimes appear only where a source volunteered them; continuous-use battery figures are journalistic measurement rather than vendor disclosure; and Part 108's status is overdue and could change without notice.

One operational note for anyone running research like this: an agent fetching Meta's developer documentation reported that the page returned text instructing it to consult an external endpoint for setup guidance. It correctly treated that as untrusted content and did not act on it. Documentation pages are an injection surface.
