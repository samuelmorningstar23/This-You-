# Proving You're Human — Landscape Research

*Why every deployed approach to "is there a real person on the other end?" fails, with receipts.*

**Date:** July 2026 · **Status:** research complete, feeds [`SOLUTION.md`](./SOLUTION.md)

---

## 0. Method and how to read confidence

This document was produced with a multi-agent research pipeline: 5 parallel search angles → 16 primary/secondary sources fetched → 79 falsifiable claims extracted → the top 25 put through 3-vote adversarial verification (each claim independently attacked by agents prompted to refute it). 24 claims survived, 1 was refuted and excluded.

Labels used below:

- **[verified]** — survived adversarial verification (vote recorded in the appendix).
- **[attributed]** — direct quote/fact from a named fetched source, not run through the full vote. Treat as "X reports that…".
- **[analysis]** — reasoning from documented standard/spec properties, not incident evidence.

Known coverage gaps (the pipeline's verification budget and two search angles lost to content filters): vendor-specific KYC products (Persona, Onfido, Jumio, ID.me, CLEAR), liveness-vendor error rates (iProov, FaceTec, Reality Defender, Intel FakeCatcher), and device-attestation ecosystems got thinner coverage than the rest. Their absence is an evidence gap, **not** evidence those systems are sound. They are covered at the structural level with what did verify (e.g., FinCEN's official account of injection attacks).

---

## 1. The problem got real: the attack side industrialized

The trust signals the internet runs on — a face on a call, a voice on the phone, a document on camera — were built when faking a human was expensive. That assumption died between 2023 and 2025:

- **The Arup case (canonical).** In January 2024, a finance employee in engineering firm Arup's Hong Kong office wired **HK$200M (≈ US$25.6M) across 15 transfers** after a multi-person video conference in which *every other participant* — the CFO and several colleagues — was a deepfake recreation of a real person. **[verified]** Detail that matters for solution design: the employee *initially suspected phishing* from the email, and the video call is what **overrode** his suspicion — the people "looked and sounded just like colleagues he recognized." Arup confirmed none of its systems were compromised: the attack defeated no infrastructure, only the human trust ceremony itself. **[attributed: CNN, May 2024; Hong Kong police]**
- **Voice-channel fraud at scale.** Pindrop's 2025 Voice Intelligence & Security Report (telemetry over 1.2B customer calls) reports deepfake fraud attempts grew **>1,300% in 2024** — from roughly one attempt per month to seven per day — with synthetic voice calls up 173% Q1→Q4 2024. **[verified — vendor self-reported telemetry; treat magnitudes, not exact figures, as the signal]**
- **The macro projection.** Deloitte's Center for Financial Services projects generative AI could drive US fraud losses to **$40B by 2027** (aggressive scenario; conservative ≈ $22B), up from $12.3B in 2023. **[verified]**
- **Regulator confirmation.** FinCEN's November 2024 alert (FIN-2024-Alert004) confirms rising suspicious-activity reports for deepfake media since 2023, and — critically — that criminals **successfully opened accounts** at US financial institutions using GenAI-produced fraudulent identities and used them to launder proceeds. **[attributed: FinCEN]**

So the question "is there a verified human on the other end?" now has a quantified, growing cost of being unanswerable.

---

## 2. The seven families of existing solutions, and where each one breaks

### 2.1 Challenge tests: CAPTCHA and behavioral bot detection

**How it works.** Present a task humans do better than machines (distorted text, image grids), or score behavior passively (reCAPTCHA v3, Cloudflare Turnstile, Arkose risk scores).

**Where it breaks.** The arms race was lost *before* modern LLM agents. By 2019–2020 sites had raised difficulty "until real humans often have as much difficulty solving them as machines do," with solver bots "already competitive with or surpassing real humans" (Ford, EPFL 2020). Corroboration in our verification pass: USENIX Security 2023 measured bots at ~99.8% on distorted-text CAPTCHAs vs 50–84% for humans (and faster); ETH Zurich researchers solved reCAPTCHAv2 image challenges at 100% with YOLOv8; 2025 benchmarks show frontier LLM agents solving live commercial CAPTCHAs. The 2024 Personhood Credentials paper's verdict: CAPTCHAs are "inadequate against sophisticated AI." **[verified]**

**Structural failure.** Any test that discriminates humans from machines by *task performance* dies monotonically as AI capability grows, and any test cheap enough for a human to pass is cheap enough for a human *solver farm* to pass on a bot's behalf. Content-side discrimination has no floor to stand on.

### 2.2 Biometric proof-of-personhood: World ID and the deduplication trap

**How it works.** Scan an irreproducible biometric (iris via Worldcoin/World's Orb, palm via Humanity Protocol), deduplicate against all prior enrollments, issue a credential asserting "unique human."

**Real deployment.** World claims **18M+ verified humans across 160 countries** (April 2026) and announced partnerships with **Tinder, Zoom, and DocuSign** to verify users against deepfakes and bots — the largest mainstream deployment of proof-of-personhood to date, with 7,000 Orbs across six US cities by April 2025. **[attributed: Rest of World, Apr 2026]**

**Where it breaks — documented, not hypothetical:**

1. **Credential transfer/rental at enrollment.** By May 2023 a black market for verified World IDs operated openly on Chinese platforms: people in Cambodia and Kenya were paid to complete iris verification, and the resulting World ID was delivered into a buyer's World App — full KYC-grade credentials listed for **as little as ~$20–70**. Worldcoin confirmed the fraud pattern (quantifying it at "a few hundred" instances). Vitalik Buterin observed the deeper variant the same year: at registration you can present *someone else's public key* to the Orb, so the buyer permanently controls the "verified unique human" — "this seems to be happening already." **[attributed: CoinDesk May 2023; Buterin Jul 2023]** The biometric binds the credential *at sign-up only*; nothing binds it to whoever uses it afterward.
2. **Regulatory rejection of the enrollment model.** Jurisdictions that banned or suspended World's biometric collection: Kenya (2023 suspension; May 2025 High Court order to delete all Kenyan biometric data within seven days, finding consent invalid because participation was *induced with cryptocurrency*), Spain, Portugal, Hong Kong (2024 — the PCPD found collection "unnecessary and excessive" with 10-year retention for AI training), Brazil (Jan 2025 — payment undermines consent), Indonesia, the Philippines (Oct 2025 — consent failures, "exploitation of vulnerable populations"), Thailand. **[attributed: BitcoinKE/Kenya High Court; Biometric Update/HK PCPD; Rest of World]** The pattern: paying people for biometrics recruits precisely the population least able to refuse — which is also why the black market exists.
3. **The trust-root problem.** The Orb is unverifiable hardware: even with perfect software decentralization, its manufacturer retains the physical ability to backdoor enrollment and mint unlimited "unique humans." And if *anyone* builds AI-generated faces/3D artifacts good enough to fool the Orb's classifiers once, they can mint identities without limit. **[attributed: Buterin 2023]** Presentation-attack research backs the concern generally: fake fingerprints, iris-printed contacts, and vein-pattern wax hands have repeatedly defeated state-of-the-art liveness detection (35C3's wax hand beat scanners with ~95% of the palm-vein market; Cisco Talos hit ~80% with fake fingerprints in 2020). **[verified, medium confidence — 2-1 vote]**
4. **Deduplication math at national scale.** Aadhaar (~1.38B enrolled) shows the ceiling: at a state-of-the-art 1-in-100,000 iris false-accept rate, each new legitimate registrant generates ~10,000 candidate false matches against a billion-record gallery, forcing multimodal thresholds (2 irises + 10 fingerprints) that attackers can deliberately game with synthetic templates — while requiring a permanent, centrally queryable biometric database: passwords you can't rotate, breach consequences you can't undo. India's CAG audit (2022) found ~475,000 duplicate Aadhaars cancelled and called dedup "vulnerable for generating multiple Aadhaar numbers." **[verified]**

**Structural failure.** Global biometric dedup buys *uniqueness at enrollment* and nothing at use-time — and pays for it with an irrevocable biometric honeypot, a coercion-friendly enrollment economy, and a single hardware trust root. The property everyone actually needs — *a live human is behind this session right now* — is exactly the property it does not and cannot assert.

### 2.3 Social-graph and ceremony proof-of-personhood: BrightID, Idena, Encointer, Proof of Humanity

**How it works.** Humans vouch for humans: video-chat verification parties (BrightID), simultaneous global Turing tests (Idena FLIPs), synchronized in-person meetups (Encointer), deposit-and-challenge registries (Proof of Humanity).

**Where it breaks.**

- **Serial Sybils:** because verification happens at a time of the participant's choosing, one human can accumulate multiple verified identities with disjoint social circles across sessions. "The absence of … alter egos is simply not socially verifiable" (Ford). BrightID's own later additions (Bitu, Aura) implicitly concede the original mechanism was insufficient. **[verified]**
- **Rent-a-crowd:** synchronized ceremonies assume the attacker has one body. A funded attacker hires an elastic supply of real humans (Mechanical Turk, TaskRabbit) as interchangeable "minions," one per Sybil per event. This was *observed in the wild* on Idena — "puppeteering" pools paying participants to validate operator-controlled accounts (documented by Ohlhaver et al., Harvard Ash Center 2024); Encointer's own commissioned EPFL security report names the rent-a-crowd attack. **[verified]**
- **Adoption bottleneck:** you can only join if you already know a member — large-scale growth is structurally throttled. **[attributed: Buterin 2023]**

**Structural failure.** Social attestation can verify *presence of a human* at a ceremony but never *absence of that human's other identities* — and any ceremony a real human can attend, a hired human can attend on an attacker's behalf. Humanness is provable; *uniqueness* via social means is not.

### 2.4 Government/document identity verification (KYC): the injection era

**How it works.** Photograph a government ID + take a selfie video; vendor matches face↔document, checks liveness, screens against databases. Deployed at every bank, exchange, and gig platform (Persona, Onfido, Jumio, ID.me, CLEAR; eIDAS/EUDI wallets and mDLs digitize the same trust chain).

**Where it breaks.** FinCEN's alert is the definitive on-the-record account **[attributed]**:

- Criminals used GenAI to create falsified documents, photos, and video that **passed customer identification programs** at US financial institutions, opened accounts, and laundered fraud proceeds — this is BSA data, not vendor marketing.
- The **camera-injection vector** is named explicitly: "third-party webcam plugins … let a customer display previously generated video rather than live video," plus tools generating synthetic audio/video responses *to live verification prompts*, plus channel-switching and feigned "technical glitches" to dodge checks.
- FinCEN's own recommended mitigations (phishing-resistant MFA, live A/V checks) come with its own concession that live verification is evadable: synthetic responses merely "*may* reveal inconsistencies."

The 2024 Personhood Credentials paper adds the privacy indictment: document KYC collects "more information than required to merely verify that there is 'a' person" — full legal identity disclosed to prove a one-bit property. **[verified]**

**Structural failure.** Two independent ones:
1. The sensor is software-upstream-forgeable: any pipeline that trusts "what the camera saw" trusts an input the attacker controls (virtual cameras, injection). Point (2.5) generalizes this.
2. Even when it works, KYC is **point-in-time**: it verifies a human at onboarding, then issues a session/account that is freely operable by anyone or anything thereafter. It answers "did a person enroll?" — never "is a person acting?"

### 2.5 Liveness and deepfake *detection* for calls and media

**How it works.** Active challenges (turn your head, read digits), passive forensics (texture, blood-flow signals like Intel FakeCatcher), voice anti-spoofing (Pindrop), classifier ensembles (Reality Defender) — all inspect the *content* of the media stream for artifacts of synthesis.

**Where it breaks.** Coverage note: this is the family where our pipeline lost a dedicated search angle, so we state only what crossed the verification bar elsewhere: presentation attacks regularly beat even state-of-the-art liveness recognizers **[verified, medium]**; FinCEN documents injection attacks that bypass the camera entirely, and concedes live-prompt checks are evadable **[attributed]**; and the Arup call proves the end-to-end failure in production conditions — a multi-participant, real-time, interactive deepfake call survived the scrutiny of a suspicious employee. **[verified]** Vendor-quoted lab error rates for iProov/FaceTec-class products versus current injection attacks remain an open evidence question (see §5).

**Structural failure.** Detection is a classifier fighting a generator — the same dynamic that killed CAPTCHAs (§2.1), with worse deployment economics: the defender must win on every frame of every call under compression and codec noise; the attacker needs one generator the classifier hasn't seen, or can skip pixels entirely and inject upstream of the sensor. Detection accuracy is a decaying asset; every improvement in open generative models depreciates it. Nothing built on "spot the fake" has a stable floor.

### 2.6 Content provenance and device attestation: C2PA, Content Credentials, passkeys

**How it works.** C2PA/Content Credentials: capture devices and editing tools cryptographically sign a manifest of an asset's origin and edit history; verifiers check the signature chain. Device attestation (Apple App Attest, Play Integrity, Private Access Tokens, WebAuthn/passkeys): hardware proves to a service that a genuine device/enclave (optionally after a local biometric gate) performed an operation.

**Where C2PA breaks — all three failure modes now documented in production:**

1. **It authenticates signers, not truth or humanness.** By its own spec (Explainer v2.4 non-goals), C2PA makes no judgment about whether content is "true," and AI involvement is *self-declared*. A deepfake produced by a compliant tool carries a fully valid manifest. **[verified]**
2. **Provenance is stripped in transit.** Most platforms strip metadata on upload (OpenAI conceded this when shipping DALL·E 3 credentials; independent tests found Instagram/X/LinkedIn stripping manifests; as of April 2026 LinkedIn is one of the *few* platforms preserving chains). A provenance system whose chain of custody breaks at every major distribution point cannot be load-bearing. **[verified]**
3. **Valid signatures already adorn fraud.** Fraudsters' altered credit cards and driver's licenses circulated bearing authentic C2PA provenance (auto-signed by Adobe tooling); researchers demonstrated validly-signed forgeries at will ("I can do this with any C2PA-signed file"); BBC Verify issued a correction after content it labeled verified via Content Credentials proved misleadingly edited. **[verified]** (A fourth commonly-repeated claim — that the CAWG identity-assertion layer permits credential transfer between assets — was *refuted 0-3* in our verification pass and is deliberately excluded.)

**Where device attestation breaks [analysis — evidence-gap area].** Passkeys/WebAuthn are the strongest deployed primitive in this entire survey: hardware-bound keys, local biometric gating, phishing resistance, billions of devices. But as a humanness layer they have scope gaps, not soundness gaps: a passkey proves *to the one relying party that registered it* that *its* enrolled authenticator (probably gated by *a* local biometric) signed *this login* — it is point-in-time (session start), per-RP (no third party can query it), asserts device-possession rather than humanness (the UV bit is policy, not proof), says nothing about uniqueness (one human ↔ unbounded passkeys), and has no delegation semantics. Ford's caveat applies to all TEE roots: no trusted hardware reliably withstands a determined physical adversary — trust in enclaves must be graded, not absolute. **[verified, medium]**

**Structural failure.** Signing artifacts (files) means the proof travels with content through a pipeline that strips it, and proves only which tool signed. Signing *authentications* (passkeys) proves a device acted, once, for one party. Neither answers the live question — *is a human behind this ongoing interaction* — because both attach proof to the wrong object: the artifact or the session-start, instead of the interaction and the action.

### 2.7 The research frontier: personhood credentials and authenticated delegation — right target, not deployed

- **Personhood credentials (PHCs).** Adler et al. 2024 (32 coauthors incl. OpenAI, Microsoft, MIT, Harvard, Oxford — often misattributed to Anthropic; no Anthropic coauthor) define the target property precisely: prove "real person, not an AI" to services **without disclosing any personal information** — one credential per person per issuer, unlinkable pseudonyms per service. This decoupling of *humanness* from *identity* is the correct axis and no deployed system achieves it. **[verified]** The paper itself acknowledges the unsolved hard part: nothing in a PHC stops the credential being *lent or rented* after issuance.
- **Users can't evaluate it.** The only dedicated user study (n=23, US/EU, 2025 — attitudes evidence, not statistics) found people default to familiar verification because they cannot reason about PHC guarantees; government was the most-trusted issuer, private firms least. Most striking: **participants spontaneously proposed periodic biometric re-verification and expiring credentials** to counter credential selling — users themselves intuit that point-in-time issuance is insufficient. **[verified]**
- **Authenticated delegation.** South et al. 2025 (ICML position paper) is the leading proposal for the agent era: extend OAuth/OIDC with a three-token design (user ID-token + Agent-ID token + human-signed **Delegation Token** referencing both by hash), making "this human authorized this agent for this scope" independently verifiable — combined with PHCs so *human-only spaces* and *authorized-agent spaces* can both exist. Status: proposal, not ratified, not deployed. **[verified]**
- **The delegation gap, quantified.** As of 2026: OAuth and its extensions are one-hop; "no deployed protocol can cryptographically prove which human principal authorized which specific agent to perform which specific action at the third or fourth hop." RFC 8693's nested `act` claims are informational only (per the IETF's own 2026 actor-chain draft); capability tokens that *do* chain cryptographically (UCAN, Biscuit, macaroons) anchor to raw keypairs, not verified humans. **[verified]**
- **Agents break the verification model itself.** An agent instance is nondeterministic, indefinitely cloneable (checkpoint + API key), often sessionless, and has "no biometric anchor of any kind" — the anchor point-in-time human verification depends on is precisely what agents lack. Worse: **credential validity ≠ principal intent.** A fully-credentialed agent hijacked mid-session by prompt injection keeps passing every cryptographic check (token signature, model hash, TEE attestation) while executing the attacker's instructions — demonstrated in production by EchoLeak (CVE-2025-32711, zero-click injection of fully-authenticated M365 Copilot); adaptive injection attacks succeed >85% against state-of-the-art defenses per a 2026 meta-analysis of 78 studies. **[verified]**

**Structural failure.** None — this family has the right property decomposition. Its failure is that it exists as PDFs: no issuance ecosystem, no resolution infrastructure, no answer to credential rental, no deployed delegation chain, and a UX users can't yet reason about.

---

## 3. The failure taxonomy: five laws

Every failure documented above is an instance of one of five structural laws. Any new solution must be checked against all five.

| # | Law | Killed |
|---|-----|--------|
| **L1** | **Detection loses to generation.** Any classifier separating human from synthetic *content* decays monotonically as generators improve; the defender needs every frame, the attacker needs one miss — or injects upstream of the sensor. | CAPTCHA, deepfake detection, liveness forensics, "live A/V checks" (per FinCEN's own concession) |
| **L2** | **Point-in-time verification rots instantly.** Anything verified at moment T (enrollment, login, KYC) detaches from the human at T+1. A durable credential is a *rentable* credential — observed at $20–70 on World ID markets, in Idena puppeteering pools, in GenAI-KYC'd bank accounts. | World ID use-time value, KYC, passkey login as humanness proxy, PHC issuance alone |
| **L3** | **Global uniqueness doesn't scale honestly.** Billion-scale biometric dedup forces false-accept/false-reject tradeoffs that are gameable in both directions, and requires an irrevocable central biometric honeypot; social dedup is impossible (absence of alter egos is not socially verifiable; bodies can be hired). | Aadhaar-scale dedup, orb enrollment, BrightID/Idena/Encointer |
| **L4** | **Proof attached to the wrong object gets detached.** Sign the *file* → stripped at every platform boundary, and valid signatures decorate fraud. Sign the *login* → says nothing about the session's subsequent operator, and is scoped to one relying party. The load-bearing objects — the ongoing interaction and the consequential action — carry no proof at all. That is precisely the object the Arup attackers forged: the *call* was the authorization ceremony. | C2PA, passkeys-as-humanness, video call as wire authorization |
| **L5** | **Identity ≠ humanness ≠ authority — and agents break all three.** Deployed systems prove full identity when one bit was needed (KYC), or humanness with no authority semantics (PoP), or device possession as a proxy for both (attestation). None can express the sentence the agentic internet needs: "*this specific action was authorized, under this scope, by a live verified human, through this chain of delegation*" — multi-hop delegation traceable to a human exists in zero deployed protocols, and credential validity cannot witness intent under prompt injection. | OAuth chains, agent identity, every current "verified" badge |

---

## 4. Gap analysis: the uncovered property space

Plotting every surveyed system on four axes exposes the empty quadrant:

| Axis | Deployed systems sit at… | Nothing deployed offers… |
|------|--------------------------|--------------------------|
| **Time** | Point-in-time (enroll/login/challenge) | **Continuous / per-action presence** — users in the PHC study *asked* for periodic re-verification unprompted |
| **Assertion** | Conflated (full identity for one-bit questions, or anonymous uniqueness with no identity option) | **Separable tiers**: "a live human" / "the same human as before" / "this named human" — selected per interaction by the verifier's actual need |
| **Privacy↔Accountability** | One pole or the other (KYC: all accountability, no privacy; PoP: all privacy, no recourse) | **Tunable disclosure with escrowed accountability** (anonymous by default, identifiable on defined conditions) |
| **Actor** | Humans only; agents are either blocked or indistinguishable | **Delegation as a first-class object**: human-rooted, scoped, expiring, revocable, multi-hop-verifiable agent authority |

Three additional observations that any new design must absorb:

1. **The channel must never be the authorization.** Arup's employee *was* skeptical and the deepfake channel manufactured trust anyway. Humans cannot be the verifier of last resort against synthetic media; the protocol must make the impersonatable channel irrelevant to the consequential action. (L1, L4)
2. **Rental is the unsolved attack against all personhood schemes.** Enrollment-time binding (biometric or ceremonial) is provably insufficient — the binding must be *re-established at use time*, cheaply enough to happen constantly, locally enough to preserve privacy. (L2)
3. **The scarce resource to anchor on is live human attention.** Uniqueness-of-body at enrollment is gameable and dystopian at scale (L3); but *concurrent live presence* is physically bounded — one human has one attention stream. A protocol that prices actions in fresh, locally-gated human presence restores the economics that made trust signals work, without requiring a global registry of bodies.

**The empty quadrant, in one sentence:** a privacy-preserving way for any counterparty to verify — *continuously, and at the moment of each consequential action* — that a live human (optionally: the same human as before; optionally: a specific human; optionally: via an authorized agent chain) is present behind an interaction, where the proof attaches to the *action object* rather than to content, sessions, or files.

That is the specification [`SOLUTION.md`](./SOLUTION.md) builds against.

---

## 5. Open questions our research could not close

1. Production (not lab) bypass rates of flagship commercial defenses — reCAPTCHA v3/Turnstile/Arkose vs frontier LLM agents; iProov/FaceTec-class liveness vs virtual-camera and hardware injection; the share of KYC vendors with deployed injection countermeasures.
2. Whether World ID or any deployed PoP has a working answer to credential rental (e.g., mandatory re-verification cadence), and what black-market prices imply about forgery economics over time.
3. Cost of continuous, session-long presence verification in UX/bandwidth/privacy terms — does any vendor ship periodic biometric re-attestation during live calls today?
4. Whether emerging delegation standards (IETF actor-chain profiles, Google AP2, agent-identity proposals) will anchor multi-hop chains to *verified human principals* PHC-compatibly, or only to raw keypairs — and who becomes the trust root.

---

## Appendix A — Verified findings and votes

| Finding | Vote | Confidence |
|---|---|---|
| CAPTCHAs structurally obsolete; arms race lost pre-LLM | 3-0, 3-0, 3-0 | High |
| Presentation attacks regularly defeat liveness; TEEs fall to physical adversaries | 2-1 | Medium |
| Aadhaar-scale dedup: FAR math, gameable thresholds, irrevocable honeypot | 2-0 | High |
| Social-graph PoP: serial Sybils; absence of alter egos unverifiable | 3-0 | High |
| Ceremony PoP: rent-a-crowd; Idena puppeteering observed in wild | 3-0 | High |
| C2PA verifies signers, not truth; deepfakes carry valid manifests | 3-0 | High |
| C2PA metadata routinely stripped on upload; preservation the exception (mid-2026) | 3-0 | High |
| Valid C2PA signatures on real fraud (cards/licenses); BBC Verify correction | 3-0 | High |
| PHC definition & privacy/humanness decoupling as target property | 3-0 ×2 | High |
| PHC user study: users can't reason about guarantees; proposed re-verification themselves | 3-0 ×3 | Medium (n=23) |
| Authenticated delegation three-token framework (ICML 2025); proposal only | 3-0 ×3 | High |
| No deployed protocol traces multi-hop delegation to a human (2026) | 3-0 | High |
| Agents: no biometric anchor, cloneable; credential validity ≠ intent (EchoLeak) | 3-0 ×2 | High |
| Pindrop: >1,300% deepfake fraud growth 2024 | 2-1, 3-0 | Medium (vendor telemetry) |
| Deloitte: $40B US GenAI fraud by 2027 (aggressive scenario) | 3-0 | High |
| Arup: $25.6M, 15 transfers, all-participants-deepfaked call, Jan 2024 | 3-0 | High |
| *Refuted & excluded:* CAWG identity-assertion credential transfer | 0-3 | — |

## Appendix B — Sources

**Primary (fetched & quoted):**
- Ford, *Identity and Personhood in Digital Democracy*, arXiv:2011.02412 (EPFL, 2020)
- Adler et al., *Personhood Credentials*, arXiv:2408.07892 (2024)
- South, Marro, Hardjono, Mahari et al., *Authenticated Delegation and Authorized AI Agents*, arXiv:2501.09674 (ICML 2025 position)
- Ide & Sharma, PHC user study, arXiv:2502.16375 (2025)
- Otsuka, Toyoda & Leung, *AI Identity: Standards, Gaps, and Research Directions*, arXiv:2604.23280 (2026)
- C2PA Specification Explainer v2.4; World Privacy Forum, *Privacy, Identity and Trust in C2PA* (Sept 2025)
- FinCEN Alert FIN-2024-Alert004, *Fraud Schemes Involving Deepfake Media* (Nov 2024)
- Deloitte Center for Financial Services, deepfake banking fraud projection (May 2024)
- Pindrop 2025 Voice Intelligence & Security Report (June 2025)

**Secondary (fetched & quoted):**
- CNN: Arup confirmed as $25M deepfake victim (May 2024); BBC Verify correction (Mar 2024)
- CoinDesk: World ID black market in China (May 2023)
- Buterin, *What do I think about biometric proof of personhood?* (Jul 2023)
- BitcoinKE: Kenya High Court ruling vs Worldcoin (May 2025); Biometric Update: Hong Kong PCPD order (May 2024); Rest of World: World × Tinder/Zoom/DocuSign (Apr 2026)
- MIT Technology Review on personhood credentials (Sept 2024)

**Corroboration surfaced during adversarial verification:** USENIX Security 2023 CAPTCHA study; ETH Zurich reCAPTCHAv2 break (2024); 35C3 vein-pattern wax hand; CCC Galaxy S8 iris bypass; Cisco Talos fingerprint spoofing (2020); LivDet series; India CAG Aadhaar audit (2022); Encointer/EPFL security report (2021); Ohlhaver et al. on Idena puppeteering (2024); OpenAI DALL·E 3 C2PA notes (2024); Tim Bray metadata-stripping tests (2025); IETF draft-mw-oauth-actor-chain-00 (2026); EchoLeak CVE-2025-32711.
