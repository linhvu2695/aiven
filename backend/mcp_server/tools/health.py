"""
Health check tools for the Aiven MCP Server
"""

from mcp.server.fastmcp import FastMCP
from mcp_server.client import AivenAPIClient


def register_health_tools(mcp: FastMCP, client: AivenAPIClient):
    """Register health-related tools with the MCP server"""
    
    @mcp.tool()
    async def ping_health() -> str:
        """Check if the API server is healthy and responding"""
        result = await client.request("GET", "/api/ping")
        return client.format_response(result)