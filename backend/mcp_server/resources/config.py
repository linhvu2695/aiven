"""
Configuration resource for the Aiven MCP Server
"""

import json
from mcp.server.fastmcp import FastMCP
from mcp_server.config import config as mcp_config


def register_config_resource(mcp: FastMCP):
    """Register configuration resource with the MCP server"""
    
    @mcp.resource("aiven://api/config")
    def get_api_config() -> str:
        """Get current API configuration"""
        return json.dumps({
            "base_url": mcp_config.api_url,
            "version": mcp_config.version,
            "description": "Aiven Application API",
            "server_name": mcp_config.server_name,
            "available_models": [
                "gpt-4", "gpt-4o", "claude-3-sonnet", "gemini-pro"
            ]
        }, indent=2)