# Verification pass

Ten load-bearing claims from [`EDITH.md`](./EDITH.md) — the ones the build plan
and the legal advice actually rest on — each assigned to an agent instructed to
**refute** it, fetch primary sources, and treat its own training data as stale.

The result is not flattering to the first draft, which is the point:

| | |
|---|---|
| Confirmed outright | **1** |
| Confirmed with material caveats | **4** |
| **Partly wrong** | **5** |
| Refuted outright | 0 |

Everything below is corrected in `EDITH.md` and in the code. This file records
what was wrong so the corrections are auditable rather than silent.

---

### 1. Claude has no audio modality — **CONFIRMED**

Checked against Anthropic's models overview ("All current Claude models support
text and image input, text output, multilingual capabilities, and vision"), the
Messages API content-block union, the complete endpoint inventory including
betas, and the Files API MIME table. No audio input block, no audio output, no
realtime or websocket voice endpoint, no audio beta header. A Claude voice
assistant is structurally a cascade.

### 2. Image tokenization is 28×28 patches — **CONFIRMED WITH CAVEAT**

The formula is documented verbatim and reproduces every worked example in
Anthropic's own table exactly, where `(w×h)/750` misses each by 2–25%.

Caveats: the standard tier caps visual **tokens** at 1568, not just the long
edge at 1568 px. The high-resolution tier is "Claude 4.7 and later" — so Sonnet
5, Opus 4.8 and Fable 5 qualify too, not only Opus 5. And the patch count is
evaluated *after* any downscale to the tier limit. Also fairer to `(w×h)/750`:
it is a superseded approximation that lands within a few percent, not a
fabrication.

### 3. Meta's toolkit blocks a custom assistant — **PARTLY WRONG**

My central technical claim was backwards. **`mwdat-camera` is a third-party
camera-stream SDK and it is the toolkit's flagship capability** — HEVC video
streaming, configurable frame rates (30/24/15/7/2 fps), `StreamSession`,
`capturePhoto()`. Saying there is no camera-stream SDK was simply false, and the
claim contradicted itself by granting camera access in the same breath.

The dates were wrong too: the toolkit entered developer preview on **30 Oct
2025** (v0.1.0); 14 May 2026 was v0.7.0, which added the *Display* capability;
it is still labelled developer preview at v0.8.0 (25 Jun 2026).

But a bigger constraint than the one I claimed turned out to be real: **the
toolkit does not expose the glasses' microphones or speakers at all.** The
Android SDK has exactly four modules — core, camera, display, mockdevice — and
neither changelog mentions audio at any version. "Microphones and speakers"
appears only in marketing prose on the landing page. The Web Apps track lists
Microphone explicitly as unsupported.

Corrected consequence: you **can** build a phone app that streams video off the
glasses, runs your own AI on it, and renders results to the Display — using the
*phone's* microphone for voice. You **cannot** bind to Meta's wake word, use the
glasses' own mics or speakers, run always-on in the background, or distribute
beyond invited testers. The 100-tester cap is also undocumented; limits are
configured per app.

> **Incidental finding worth recording:** the agent reported that Meta's
> `/docs/develop/dat` page returned text instructing the reader to "consult the
> Wearables MCP endpoint" for setup guidance, and correctly treated it as
> untrusted fetched content rather than acting on it. Documentation pages are an
> injection surface for any agent doing this kind of research.

### 4. Ray-Ban Display drains in ~30 minutes of continuous AI — **PARTLY WRONG**

**This was the worst number in the draft and I had built an argument on it.**

The 6-hour mixed-use rating is confirmed from Meta's own help page. The
"~30 minutes continuous" figure has **no primary source** and every actual
measurement contradicts it: NYT Wirecutter reports "almost three hours with
continuous use"; Tom's Guide observed 40% remaining after 90 minutes. The real
endurance gap is roughly **2–3×, not 12×**.

The 30-minute figure most likely conflates one of three unrelated thirties: the
livestream cap on *Ray-Ban Meta* camera glasses, the Neural Band's 30-minute
fast charge, or the 30-hour glasses-plus-case total.

Also corrected: per-clip recording defaults to 3 minutes at **1080p30, not
720p30**, and it is a **user-adjustable setting**, not a hard cap. And Meta
nowhere attributes these limits to thermals — that was my inference, and it is
undercut by the limit being configurable and model-dependent.

What survives: the underlying physics was never in question. The ~200 mW all-day
average budget, the 1–2 W thermal ceiling, and the IEC 62368-1 touch-temperature
limits all came from a different angle and stand. The wall is real; my headline
number for it was not.

### 5. EU AI Act scope — **CONFIRMED WITH CAVEAT**

All three propositions survive against the authentic text, with three
refinements that matter:

- Art. 5(1)(h) is scoped to law enforcement — **but** Art. 3(46) defines "law
  enforcement" to include activities carried out by such authorities *or on
  their behalf*, and Art. 3(45) reaches any body "entrusted by Member State law
  to exercise public authority". A private vendor operating for police **is**
  caught. Art. 5(5) also leaves Member States free to impose stricter national
  rules on private use.
- Art. 5(1)(e) is **actor-neutral**, not a private-actor provision, and it
  catches only untargeted scraping that creates or expands a database — not live
  identification as such. Arts. 5(1)(f) and (g) are further biometric
  prohibitions binding private actors.
- The Annex III verification carve-out is quoted accurately and was left
  unchanged by Regulation (EU) 2026/1744 — **but that regulation, in force 27
  July 2026, moved the Annex III high-risk obligations from 2 Aug 2026 to 2
  December 2027.** So the classification stands while the compliance duties do
  not yet apply. Annex III point 1 is also conditioned on its chapeau ("in so
  far as their use is permitted under relevant Union or national law").

### 6. Illinois BIPA — **CONFIRMED WITH CAVEAT**

"Private entity means any individual…" is verbatim, with carve-outs only for
government and courts — an individual hobbyist is facially a proper defendant.
SB 2979 is P.A. 103-0769, effective 2 Aug 2024, and the single-violation
language is as described.

Four refinements: the second tier is "intentionally **or recklessly**"; the
$1,000/$5,000 figures are liquidated-damages **floors** ("or actual damages,
whichever is greater") and discretionary under *Cothron*; the amendment has **no
retroactivity clause** and district courts split until *Clay v. Union Pacific*
(7th Cir., 1 Apr 2026) held it procedural and retroactive — which does not bind
Illinois state courts; and the single-violation rule reaches only §15(b)
collection and §15(d) disclosure, leaving §§15(a), (c) and (e) unlimited.

### 7. Arming a drone — **PARTLY WRONG**

The citation is exact and the prohibition is real, but two elements failed.

**"No private-party exception" is wrong on the face of the statute.** The text
reads "**Unless authorized by the Administrator**, a person may not operate an
unmanned aircraft… equipped or armed with a dangerous weapon" — an
authorization pathway that is not limited to government operators.

And **$25,000 is the unadjusted 2018 figure.** The operative maximum under 14
CFR 13.301 is **$31,207 per violation** for violations on or after 30 December
2024.

Two precision points: the section bans *operating* an armed UAS rather than
*arming* one, and it applies to any "person", not only civil operators.

### 8. Part 108 is not law — **CONFIRMED WITH CAVEAT**

Confirmed against the Federal Register API: RIN 2120-AL82 exists only as a
proposed rule, and no final rule on Part 108 appears in FAA rules published
since June 2026 or on the public-inspection list.

Two caveats. 14 CFR 107.35 is **broader** than I paraphrased — it bars
manipulating flight controls **or** acting as remote PIC **or** visual observer
for more than one unmanned aircraft, and the operative sentence says "unmanned
aircraft", not "small". And the status is **volatile, not merely pending**: the
Fall 2025 Unified Agenda projected a July 2026 final rule and Pub. L. 118-63
§930 set a statutory deadline of 16 January 2026. Both have passed. The rule is
overdue and could publish at any time — re-verify before relying on this.

### 9. Brilliant Labs Halo is shipping and fully open — **PARTLY WRONG**

The hardware specs and the BLE-only limitation all check out: colour microOLED,
640×480 global-shutter sensor, 2 mics, 2 bone-conduction speakers, Alif B1 with
Ethos-U55 NPU, just over 40 g, Bluetooth LE 5.3 with no Wi-Fi anywhere in the
spec, and Python / Flutter / Web Bluetooth hosts plus an on-device Lua 5.3 VM.

But **the openness claim is false as stated.** Marketing says "totally open
source, design files and code are on Github"; the hardware doc links a "Halo
codebase repository (coming soon)" with an empty href,
`github.com/brilliantlabsAR/halo-codebase` returns 404, and no Halo firmware or
hardware-design repo exists in the 18-repo org. Only the host-side SDK, an
emulator, and docs are public. (Frame, by contrast, does have a public codebase.)

And it is **barely shipping**: the product page says units are "rolling off the
production line now, with shipments beginning in early August", and the
companion app is still "coming soon" on both stores. It is $399 single-variant —
there is no $299 tier. The ~14 h battery figure is homepage marketing against a
300 mAh cell, not a measured or documented spec.

### 10. Prior-art failure numbers — **PARTLY WRONG**

The most quotable number in the section was a metric error that the source
outlet publicly corrected.

**Rabbit R1 "5,000 daily active users" is wrong.** The Verge corrected its 25
Sep 2024 story on 7 Oct 2024 under the headline "Only 5,000 people are using the
Rabbit R1 at any given time, not in a day": 5,000 was **concurrent**, with
roughly **20,000 daily actives** and a 34,000 peak. Against the 100,000 figure
used in that story that is roughly **80% non-daily-use, not 96% abandonment**.
The 130,000 denominator is also from a different source and date (Forbes, June
2024, the CEO's own unaudited claim).

Humane holds up better but needs dating: **$699 at launch, cut to $499 in
October 2024**, with the mandatory $24/month plan never discounted. The ~10,000
shipped, returns-exceeding-sales, and ~$9M revenue figures all trace to **a
single leaked internal dataset** given to The Verge in Aug 2024 that Humane
disputed without specifying what was wrong — they are leaked estimates, not
disclosures. Servers went dark at **12 p.m. PST on 28 Feb 2025** (not midnight),
disabling cloud features while offline functions survived; HP acquired the
Cosmos platform, talent and 300+ patents for $116M, **excluding the Pin device
business**.

---

## What this changed

Two things in the first draft were argued *from* a number that turned out to be
wrong, and both arguments needed rebuilding rather than patching:

- The power-wall section led with a 12× endurance gap that is really 2–3×. The
  physics underneath it was independently sourced and stands, so the conclusion
  survives — but it is now argued from the mW budget and the thermal ceiling
  rather than from a figure nobody can source.
- The device recommendation rested on Meta being unusable and Halo being open.
  Meta is usable, with different limits than I gave; Halo's openness is
  unverifiable today. Mentra Live plus MIT-licensed MentraOS moved from second
  choice to first on the strength of being the one option whose claims all held.

The general lesson is the boring one: the claims that failed were the ones that
were *repeated* rather than *sourced* — a round number with no primary document
behind it, a marketing line about open source, a corrected press figure that
kept circulating in its uncorrected form.
