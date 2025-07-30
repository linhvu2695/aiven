"""
Aiven MCP (Model Context Protocol) Server

This package provides MCP server functionality that exposes the Aiven application APIs
as tools and resources for AI agents to interact with.
"""

from mcp_server.server import create_mcp_server

__version__ = "1.0.0"
__all__ = ["create_mcp_server"]