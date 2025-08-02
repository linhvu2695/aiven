"""
MCP Tools for Aiven API

This package contains all the MCP tools that AI agents can use to interact
with the Aiven application APIs.
"""

from .health import register_health_tools
from .agent import register_agent_tools
from .article import register_article_tools

__all__ = [
    "register_health_tools",
    "register_agent_tools",
    "register_article_tools"
]