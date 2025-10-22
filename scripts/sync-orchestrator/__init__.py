"""
Sync Orchestrator Package

Bidirectionally synchronize slash commands and skills using Thoughtbox reasoning.
"""

from .discovery import discover, SyncDiscovery
from .thoughtbox_client import ThoughtboxClient, Intent
from .command_generator import generate_command_from_skill
from .skill_generator import generate_skill_from_command
from .sync_orchestrator import SyncOrchestrator, SyncResult

__version__ = "1.0.0"

__all__ = [
    "discover",
    "SyncDiscovery",
    "ThoughtboxClient",
    "Intent",
    "generate_command_from_skill",
    "generate_skill_from_command",
    "SyncOrchestrator",
    "SyncResult",
]
