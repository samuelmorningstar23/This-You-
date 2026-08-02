"""An E.D.I.T.H.-class assistant, built out of things that actually exist.

See ../EDITH.md for the research this is built on, and README.md for what runs.
"""

from .brain import Brain, Reply
from .gate import GateConfig, VisionGate
from .identity import Advertisement, Contact, Roster, SharedSecretSigner
from .memory import Memory
from .policy import PROHIBITIONS, PolicyViolation, enforce
from .runtime import Assistant, ClaudeLooker, RuntimeConfig, ScriptedLooker
from .tools import ToolContext, ToolRegistry, default_registry
from .types import Assurance, Card, Frame, Peer, Speak, Turn, Utterance

__version__ = "0.1.0"

__all__ = [
    "Assistant",
    "Advertisement",
    "Assurance",
    "Brain",
    "Card",
    "ClaudeLooker",
    "Contact",
    "Frame",
    "GateConfig",
    "Memory",
    "PROHIBITIONS",
    "Peer",
    "PolicyViolation",
    "Reply",
    "Roster",
    "RuntimeConfig",
    "ScriptedLooker",
    "SharedSecretSigner",
    "Speak",
    "ToolContext",
    "ToolRegistry",
    "Turn",
    "Utterance",
    "VisionGate",
    "default_registry",
    "enforce",
]
