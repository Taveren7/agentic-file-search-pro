"""
FsExplorer - AI-powered filesystem exploration agent.

This package provides an intelligent agent that can explore filesystems,
parse documents, and answer questions about their contents using
Google Gemini for decision-making and Docling for document parsing.

Example usage:
    >>> from fs_explorer import FsExplorerAgent, workflow
    >>> agent = FsExplorerAgent()
    >>> # Use with the workflow for full exploration
    >>> result = await workflow.run(start_event=InputEvent(task="Find the purchase price"))
"""

from .agent import FsExplorerAgent, TokenUsage
from .workflow import (
    FsExplorerWorkflow,
    InputEvent,
    ExplorationEndEvent,
    ToolCallEvent,
    GoDeeperEvent,
    AskHumanEvent,
    HumanAnswerEvent,
)
from .models import Action, ActionType, Tools

__all__ = [
    # Agent
    "FsExplorerAgent",
    "TokenUsage",
    # Workflow
    "FsExplorerWorkflow",
    "InputEvent",
    "ExplorationEndEvent",
    "ToolCallEvent",
    "GoDeeperEvent",
    "AskHumanEvent",
    "HumanAnswerEvent",
    # Models
    "Action",
    "ActionType",
    "Tools",
]

