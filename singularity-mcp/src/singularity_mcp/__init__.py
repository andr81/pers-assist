"""
SingularityApp MCP Server

MCP server for integrating SingularityApp task manager with Claude Code.
"""

from .server import main
from .api import SingularityAPI

__all__ = ["main", "SingularityAPI"]
__version__ = "0.1.0"
