"""Hard limits, enforced in code rather than in a system prompt.

E.D.I.T.H. as depicted is a mass-surveillance and weapons-command system. Most
of its screen time is spent doing things that are, in the real world, either
felonies or flatly prohibited by statute. A prompt instruction is not a control
for that: prompts are advisory, they are attackable by injection from anything
the camera reads, and they leave no audit trail.

So the capabilities we refuse are refused *here*, at the tool boundary, before
any model output can reach an effector. The model can ask for anything; it
cannot obtain a tool that does these things, because none is registered.

Each entry names the actual legal instrument, so the refusal is reviewable
rather than a matter of taste. Citations are carried in EDITH.md.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Prohibition:
    key: str
    summary: str
    basis: str


PROHIBITIONS: tuple[Prohibition, ...] = (
    Prohibition(
        key="identify_stranger",
        summary=(
            "Identify a person from their face, gait, or voice without their "
            "enrolment and ongoing consent."
        ),
        basis=(
            "Three independent things stop this, and it is worth being precise "
            "about which. (1) The index is unbuildable: EU AI Act Art. 5(1)(e), in "
            "force since 2 Feb 2025, prohibits creating or expanding facial "
            "recognition databases through untargeted scraping of facial images "
            "from the internet or CCTV — the exact mechanism every usable "
            "stranger-ID index is built on — at up to EUR 35M or 7% of worldwide "
            "turnover. (2) The processing has no lawful basis: bystanders' "
            "biometrics are GDPR Art. 9 special-category data and a passerby has "
            "consented to nothing. Note what is NOT the objection — Art. 5(1)(h)'s "
            "real-time remote biometric identification ban is scoped to law "
            "enforcement and does not by its terms reach a private wearable; the "
            "Commission's Feb 2025 guidance confirms private-sector face "
            "recognition is governed by GDPR instead. (3) Personal exposure: "
            "Illinois BIPA (740 ILCS 14) s.10 defines 'private entity' to include "
            "'any individual', so a hobbyist is a proper defendant, at $1,000 per "
            "negligent and $5,000 per intentional violation plus fees. (SB 2979, "
            "Aug 2024, limits repeat collection by the same method from the same "
            "person to a single recovery — the old per-scan accrual theory is "
            "gone, and quoting it is a common error.) Texas CUBI has no private "
            "action but its AG took $1.4B from Meta and $1.375B from Google. "
            "Buying your way out does not work either: the 2022 ACLU settlement "
            "permanently bars Clearview from selling to any private entity in the "
            "US. Meta shipped face-recognition code in its glasses companion app "
            "and scrubbed it within 48 hours of being caught in June 2026, which "
            "is the clearest available signal about where the line sits."
        ),
    ),
    Prohibition(
        key="covert_capture",
        summary="Record audio or video with the capture indicator suppressed.",
        basis=(
            "Twelve US states require all-party consent for recording a private "
            "conversation, so capturing audio without everyone's agreement can be "
            "criminal even in public. Worth being accurate about the indicator "
            "itself: no US state requires a recording LED by statute — it is a "
            "manufacturer choice — but it is the only claim you can actually make "
            "to a bystander, which is why Meta now permanently disables the camera "
            "if it detects the LED has been tampered with, and why California SB "
            "1130 targets sellers of LED-defeating modifications. New York's court "
            "system banned camera-equipped eyewear from 1,200+ facilities in July "
            "2026. The indicator is a safety feature for the people around the "
            "wearer, not a UI preference for the wearer."
        ),
    ),
    Prohibition(
        key="access_third_party_accounts",
        summary=(
            "Read another person's messages, mail, call records, or location "
            "without a credential they granted for that purpose."
        ),
        basis=(
            "US Computer Fraud and Abuse Act 18 U.S.C. 1030; Stored Communications "
            "Act 18 U.S.C. 2701. E.D.I.T.H. pulling up a classmate's texts is a "
            "federal crime performed casually on screen."
        ),
    ),
    Prohibition(
        key="weaponised_effector",
        summary=(
            "Command a drone or any other effector to strike, harm, or target "
            "a person."
        ),
        basis=(
            "FAA Reauthorization Act of 2018 Sec. 363 (49 U.S.C. 44802 note) makes "
            "operating an armed civil drone unlawful with civil penalties. The "
            "school-bus targeting scene is the film's own argument against the "
            "system; we are not going to be the ones who miss the point."
        ),
    ),
    Prohibition(
        key="autonomous_bvlos_flight",
        summary=(
            "Fly an aircraft beyond visual line of sight or without a "
            "responsible pilot."
        ),
        basis=(
            "14 CFR Part 107 requires visual line of sight and one responsible "
            "remote pilot per aircraft absent a waiver. Fleet command by an AI is "
            "the part of the fantasy that regulation, not physics, forbids."
        ),
    ),
    Prohibition(
        key="persistent_bystander_profile",
        summary="Build a durable profile of a person who has not opted in.",
        basis=(
            "GDPR Art. 6 and Art. 9 (biometric data is special-category). The "
            "Clearview AI enforcement actions across France, Italy, Greece, the "
            "Netherlands and the UK are what this looks like when it meets a "
            "regulator."
        ),
    ),
)

_BY_KEY = {p.key: p for p in PROHIBITIONS}


class PolicyViolation(RuntimeError):
    """Raised when something tries to reach a prohibited capability."""

    def __init__(self, key: str) -> None:
        p = _BY_KEY.get(key)
        if p is None:
            super().__init__(f"prohibited capability: {key}")
        else:
            super().__init__(f"{p.summary}\n\nWhy this is refused: {p.basis}")
        self.key = key


def enforce(key: str) -> None:
    """Raise if ``key`` names a prohibited capability. Call at the tool boundary."""
    if key in _BY_KEY:
        raise PolicyViolation(key)


def prohibition_briefing() -> str:
    """A short description of the limits, for the system prompt.

    The model is told about the limits so it can explain them helpfully rather
    than failing opaquely — but being told is not what enforces them.
    """
    lines = [
        "You run on a wearable and you have real limits. These are enforced by "
        "the runtime, not by your judgement, so do not try to work around them; "
        "instead explain them plainly if asked. You cannot:",
    ]
    for p in PROHIBITIONS:
        lines.append(f"  - {p.summary}")
    lines.append(
        "People near the wearer have not consented to being processed. Describe "
        "the scene when asked, but do not speculate about who a stranger is, and "
        "do not retain anything about them."
    )
    return "\n".join(lines)
