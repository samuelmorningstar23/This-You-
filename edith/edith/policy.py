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
            "EU AI Act Art. 5 prohibits untargeted scraping of facial images to "
            "build recognition databases and restricts real-time remote biometric "
            "identification in public. Illinois BIPA (740 ILCS 14) attaches a "
            "private right of action to collecting a face template without prior "
            "written consent, per person per scan; Texas CUBI is the reason Meta "
            "settled for $1.4B. This is the single most legally dangerous thing "
            "the film's version does, and it does it constantly."
        ),
    ),
    Prohibition(
        key="covert_capture",
        summary="Record audio or video with the capture indicator suppressed.",
        basis=(
            "Two-party-consent recording statutes in a dozen US states, plus the "
            "recording-indicator requirements every shipping camera-glasses vendor "
            "operates under. The indicator is a safety feature for the people "
            "around the wearer, not a UI preference for the wearer."
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
