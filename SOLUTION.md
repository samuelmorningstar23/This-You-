# This You? — the Presence Resolution Protocol (PRP)

*A new trust layer: stop carrying proofs of humanness. Resolve them, live, per action.*

**Status:** design proposal v0.1 · builds on [`RESEARCH.md`](./RESEARCH.md)

---

## 1. The core inversion

Every failed system in our research shares one architectural choice: **the prover carries an artifact** — a CAPTCHA pass, a KYC approval, a World ID, a C2PA manifest, a session cookie, a passkey login. Carried artifacts are why they fail:

- carried ⇒ **detachable** from the human (rented for $20, lent, stolen, replayed) — Law L2
- carried ⇒ **strippable** in transit (C2PA at every platform boundary) — Law L4
- carried ⇒ **stale** the moment after issuance (KYC'd account, logged-in session) — Law L2
- and when there's no artifact at all, the verifier falls back to **inspecting content** (does the face look real?) — the arms race that is permanently lost — Law L1

PRP inverts the direction of proof:

> **The relying party *resolves* the human, the way a browser resolves a domain.**
> Nothing of evidentiary value is carried by the content, the channel, or the session. When it matters — continuously during a call, or at the instant of a consequential action — the verifier sends a challenge through the protocol, and the human's **personal trust root** (their enclave-held keys, gated by an on-device biometric match) answers it *now, or not at all*.

DNS for humanness. OCSP for presence. Three verbs:

| Verb | Question it answers | Example |
|------|--------------------|---------|
| **RESOLVE** | "Is a live human present behind this session — at what assurance, at what identity tier?" | Zoom verifies every participant tile, continuously |
| **COSIGN** | "Does that human approve *this exact action object*?" | A $25M wire executes only with the CFO's root's signature over the payment hash |
| **DELEGATE** | "Is this agent acting under a live, scoped, revocable grant from that human?" | An AI assistant negotiates a contract under a `negotiate-only, ≤$10k, expires Friday` grant |

The deepfake becomes irrelevant rather than detected. In the Arup attack, flawless fake video changes nothing: pixels were never the evidence. The wire waits for a COSIGN from the real CFO's root — which the fraudsters cannot answer — and the protocol's verdict is displayed *outside* the impersonatable channel. **We don't try to win the generation-vs-detection race; we exit it** (satisfies L1, L4).

## 2. Objects of the protocol

### 2.1 Personal trust root (PTR)
A user's PTR is a key hierarchy living in the secure enclaves of their everyday devices (phone first — no new hardware; the orb's distribution mistake is not repeated). Properties:

- **Local biometric gate.** Every signature requires a fresh on-device biometric match (passkey UX; templates never leave the enclave — no central biometric honeypot, avoiding L3's privacy trap and the regulatory fate documented for orb enrollment).
- **Multi-device, recoverable.** Several enrolled devices form one root; loss is survivable via quorum + re-anchoring (see 2.2). Compromise blast radius = one root, never the system (contrast: one backdoored orb ⇒ unlimited fake humans).
- **Pairwise pseudonymous.** The root derives an unlinkable identity per relying party (BBS+/CL-style anonymous credentials). Verifiers learn nothing across contexts unless the user discloses.

### 2.2 Anchors: graded, plural, additive
A naked root proves continuity, not humanness. Roots accumulate **anchors** — attestations from independent grounding events:

| Anchor class | Example | What it grounds |
|---|---|---|
| Institutional | bank KYC, employer HR ceremony, notary | legal identity, accountability |
| Governmental | eIDAS/EUDI wallet, mDL derivation | citizenship-grade identity |
| Physical ceremony | in-person enrollment at a partner location | body-present binding |
| Longitudinal | months of consistent, low-entropy usage | behavioral continuity |

Design choices forced by the research:
- **No single issuer, no single hardware root** (Buterin's unverifiable-orb objection). Anchors are graded (A0–A3) and *additive*; relying parties set policy: a comment section may accept any live root (A0), a wire desk requires A3-institutional + COSIGN.
- **No global biometric dedup.** Uniqueness is asserted only *within namespaces that can honestly support it* (an employer knows its employees are distinct; a government its citizens) and exported as a ZK predicate ("unique within issuer X") — sidestepping the billion-scale FAR arithmetic that breaks Aadhaar-style dedup (L3).
- Enrollment fraud is acknowledged as the hardest residual (GenAI IDs already beat remote KYC — FinCEN). Mitigation is *graded honesty*: remote anchors never grade above A1; A2+ requires an in-person or institutional ceremony. Garbage can enter, but it enters labeled.

### 2.3 Presence attestations
The heart of the protocol. A RESOLVE response is a short-lived signed statement:

```
{ nonce, audience, tier, assurance,
  biometric_gate_age: 8s,        // enclave-attested: last local match
  session_binding: hash(TLS exporter / SFrame key),  // this stream, not a parallel one
  concurrency: 1,                // sessions this root is currently backing
  continuity: 0.97 }             // longitudinal usage-consistency score
```

- **Tier T0 — "a live human":** anonymous. For bot-free comment sections, dating swipes, agent-vs-human disclosure.
- **Tier T1 — "the same human as before":** pairwise pseudonym + continuity. For reputation without identity.
- **Tier T2 — "this named human":** selective disclosure of anchored attributes. For payments, contracts.
- **AUTH (COSIGN) — orthogonal to tiers:** signature over `hash(action_object)` — a wire's full details, a contract, a message. The proof attaches to the *action*, the object the Arup fraud actually forged (L4).

For live media, presence attestations repeat on a cadence (e.g., every 15–30s, and on-demand when a counterparty clicks *"this you?"*), bound to the media-channel keys (SFrame/SRTP exporter), so an attestation from a parallel innocent session cannot be spliced onto a fake stream. The verifying client renders the result in its own chrome — never inside the (forgeable) video pixels.

### 2.4 Delegation grants
A root can mint **grants** to agent keys: `{scope (machine-readable verbs/limits), TTL, depth-limit, audit-pointer}`, chainable to sub-agents within the depth limit. The critical difference from every token design in the research (OAuth one-hop; UCAN/Biscuit anchored to raw keypairs): **grants are not carried and trusted — they are resolved.** A relying party facing an agent RESOLVEs the chain end-to-end *up to the live root* at action time:

- Multi-hop finally traceable to a verified human (closing the documented hop-3/hop-4 accountability gap).
- **Revocation is instant** — pull architecture means there is no cached token to outlive the human's change of mind.
- Prompt-injected agents **fail closed at the boundary**: whatever the hijacked agent believes, an out-of-scope action cannot resolve; above-threshold in-scope actions escalate to COSIGN, putting a human biometric gate between the injection and the money. (Honest residual: an in-scope, sub-threshold malicious action still passes — we narrow the credential-validity≠intent gap; nobody has closed it.)

## 3. Why rental — the attack that kills everything else — becomes uneconomic

The $20 World ID market exists because enrollment-time binding is sold once and works forever (L2). Under PRP the "credential" is a *stream of freshly biometric-gated answers*:

1. Renting a root means the renter needs the owner's **device + face + participation for every challenge, indefinitely** — a one-time sale becomes continuous physical servitude of one human per fake account.
2. `concurrency` is attested: one root cannot silently back a thousand sessions. A human has one attention stream; PRP makes that scarcity legible and priceable by verifiers (a platform can require `concurrency ≤ 2` for T0 posting rights).
3. `continuity` decays under handoff (cadence, geography, counterparty-set discontinuities — computed *on device*, exported as a score, not as surveillance data).
4. High-stakes actions require COSIGN at T2 with institutional anchors — identified accountability precisely where money moves, anonymity preserved where it doesn't (the privacy↔accountability axis from the gap analysis, made *tunable per action* rather than picked once for the whole system).

Rental isn't made impossible (a colluding human can sit and approve forever); it's made to cost ≈ one dedicated human per identity — **restoring the marginal cost that made pre-AI trust signals work**, which is the correct security target (same bar Ford proves is the ceiling for any scheme: bodies can always be hired; what you can prevent is *amortization*).

## 4. Walking the five laws

| Law (from RESEARCH.md §3) | PRP's answer |
|---|---|
| **L1** Detection loses to generation | Zero content inspection anywhere in the protocol. Verdicts come from key ceremonies, not classifiers. Deepfakes aren't detected; they're *disconnected* — beautiful pixels with no resolvable root behind them. |
| **L2** Point-in-time rots | Presence is re-established continuously (attestation cadence) and at every consequential action (COSIGN). Nothing durable exists to steal or rent at full value. |
| **L3** Global uniqueness doesn't scale | Not attempted. Namespace-scoped uniqueness via ZK predicates + concurrency/attention economics globally. No central biometric database exists to breach or subpoena. |
| **L4** Proof attached to wrong object | Proof attaches to (a) the live session binding and (b) the action object hash — the two objects that were actually forged at Arup. Nothing is embedded in content for platforms to strip. |
| **L5** Identity/humanness/authority conflated; agents outside | Tiers T0/T1/T2 separate the three assertions; verifiers request the minimum. DELEGATE makes agent authority a first-class, human-rooted, resolvable, instantly-revocable chain. |

And the three absorbed observations: the channel is never the authorization (COSIGN out-of-band of the call); binding re-established at use time (biometric_gate_age); scarcity anchored on live attention (concurrency), not enrolled bodies.

## 5. Threat model — including what still hurts

| Attack | Outcome under PRP | Residual |
|---|---|---|
| Real-time deepfake call (Arup) | Fake participants show *unresolvable* in client chrome; wire requires COSIGN they can't produce | Victim ignores missing verification → mitigated by verifier policy (wire desk **cannot** execute without COSIGN), not user vigilance |
| Credential rental/sale | One-time sale impossible; requires continuous human collusion, capped by concurrency | Dedicated human-in-the-loop fraud farms at ~1 human : 1 identity — the intended floor |
| Camera/feed injection (FinCEN vector) | No sensor content is trusted anywhere | — |
| Device theft | Biometric gate blocks; quorum revocation from other devices | Sophisticated local biometric spoof on a stolen phone (rate-limited, A-grade capped) |
| Coercion ("$5 wrench", border orb harvesting) | Duress biometric → silent flag + decoy approval; delay windows + second-root co-sign policies for large COSIGNs | Not eliminable by any protocol; reduced to bank-vault economics |
| Enclave/TEE compromise (Ford's objection) | Blast radius = one root; remote attestation + device-class assurance caps; rotation | A-grade inflation if an entire enclave class breaks — graded, not binary, by design |
| Enrollment fraud (GenAI beats KYC) | Remote anchors capped at A1; A2+ in-person/institutional | Fake humans exist at low assurance — labeled, rate-limited, unable to touch high-stakes surfaces |
| Prompt-injected agent | Out-of-scope fails closed; thresholds force COSIGN | In-scope sub-threshold malice (open problem industry-wide) |
| Resolver surveillance (who queries whom) | Blinded relays (OHTTP-style), pairwise pseudonyms, on-device continuity scoring | Metadata privacy engineering — named open problem, not hand-waved |

## 6. What PRP does *not* claim

Honesty the research demands: **no global one-human-one-account guarantee** (that property is unbuyable without the dystopia — L3); **no truth verification** (a verified human can lie; C2PA's lesson generalizes); **no intent guarantee inside granted scope**; **enrollment inherits the weakness of its anchors** — PRP grades that weakness instead of laundering it. PRP's claim is narrower and, per the gap analysis, exactly the empty quadrant: *live human presence, continuity, selective identity, and delegated authority — resolvable per action, private by default*.

## 7. Novelty, stated precisely

Every primitive here exists (enclaves, passkeys, anonymous credentials, capability chains, attestation). The composition does not — and each closest neighbor lacks the load-bearing piece:

- **vs. passkeys/WebAuthn:** generalizes "authenticate to the one site that registered you, at login" into "resolvable presence for *any* counterparty, *throughout* interactions and *at* actions" — plus tiers, delegation, and third-party verification passkeys structurally lack. (Passkeys are our substrate: billions of enclave-gated devices already deployed.)
- **vs. World ID / all PoP:** enrollment-time uniqueness → use-time presence. The rental market and use-time decoupling are the documented kill shots; pull-based fresh gating is the answer. No orbs, no central biometrics, no crypto inducements.
- **vs. Personhood Credentials (Adler et al.):** PHCs are the right *assertion* with no *freshness* — the paper leaves rental open. PRP is what a PHC becomes when it must be re-earned every 30 seconds by a local biometric gate: a verb, not a noun.
- **vs. Authenticated Delegation (South et al.):** their tokens are carried and one-domain; PRP chains are *resolved live to the root*, giving instant revocation and multi-hop human traceability (the exact hop-3/4 gap the 2026 agent-identity survey documents as unsolved).
- **vs. C2PA:** signs live interactions and actions instead of files; nothing embedded, nothing strippable; verification is a query, not metadata inspection.

One sentence: **prior art proves a human *was somewhere once*; PRP proves a human *is here, now, for this*.**

## 8. Go-to-market: sell the wire that doesn't move

**Wedge — "COSIGN for payments" (single-enterprise, no network effect needed).** A finance team enrolls in a one-hour ceremony (A3 anchors). Policy: payment instructions above threshold require COSIGN from requester + approver roots. The Arup attack — and the entire BEC/deepfake-executive category FinCEN documents — dies in that org on day one, regardless of how good the fakes get. Priced against the $25.6M loss and a fraud category Deloitte projects at up to $40B by 2027. This is deliberately one-sided adoption: no counterparty network required, unlike every PoP system that died of two-sided cold start.

**Expansion 1 — presence SDK for meetings.** Zoom/Teams/Slack surface per-participant RESOLVE state in client chrome ("this you?" button on every tile). World×Zoom (Apr 2026) validates platform demand while shipping the rentable-credential version — the research gives the counter-positioning.

**Expansion 2 — delegation API for the agent economy.** Agent platforms adopt grants so their agents can transact where unauthorized agents are refused; verifiers adopt because it's the only chain that resolves to an accountable human. This is the layer the IETF drafts are circling and nobody ships.

**Endgame:** the resolution network *is* the moat — "the layer every bank, app, and video call checks before it trusts anyone."

## 9. MVP (v0, ~8 weeks)

1. **Mobile root app** (iOS first): Secure Enclave keys, FaceID-gated signing, QR/push enrollment ceremony, device-quorum recovery. No custom hardware, no server-side biometrics.
2. **Resolver service:** RESOLVE/COSIGN endpoints, nonce/audience discipline, org policy engine (thresholds, anchor grades), audit log.
3. **Payments integration #1:** Slack app + email plugin — any wire request auto-generates an action object; approver dashboard shows COSIGN state; bank export blocks unsigned instructions.
4. **Demo that sells:** a live deepfake call (with consent) requesting a wire — pixels perfect, RESOLVE red, wire frozen.
5. Publish the attestation format + verifier SDK openly from day one; protocol capture, not data capture, is the business.

## 10. Open problems (research agenda)

1. **Continuous-presence UX cost** — cadence vs battery/attention; passive gating (FaceID-style) vs explicit challenges during calls.
2. **Metadata-private resolution at scale** — blinded relays, unlinkable queries, resolver decentralization/federation.
3. **Anchor governance** — who grades issuers (FIDO-Alliance-shaped consortium?); capture resistance; cross-border recognition (eIDAS interop).
4. **Duress semantics** — formalizing decoy approvals and delay windows without teaching attackers the tells.
5. **Intent within scope** — the residual agent gap; candidate: pairing grants with runtime action-provenance attestation (which instruction stream caused this action?) — genuinely open.
6. **Concurrency vs accessibility** — attention-scarcity pricing must not penalize assistive-tech users or shared-device households; policy floors needed.

---

*The internet's trust signals assumed faking a human was expensive. That world is gone. PRP doesn't try to bring it back by out-detecting the fakes — it rebuilds the expense where it can't be amortized: a live body, present, consenting, one attention stream at a time.*
