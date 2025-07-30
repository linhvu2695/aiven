"""
Storage tools for the Aiven MCP Server
"""

from mcp.server.fastmcp import FastMCP
from mcp_server.client import AivenAPIClient


def register_storage_tools(mcp: FastMCP, client: AivenAPIClient):
    """Register storage-related tools with the MCP server"""
    
    @mcp.tool()
    async def get_presigned_url(filepath: str, expiration: int = 60) -> str:
        """Get a presigned URL for accessing a file in storage
        
        Args:
            filepath: Path to the file in storage
            expiration: URL expiration time in seconds (default: 60)
        """
        result = await client.request("GET", f"/api/storage/url/{filepath}", {"expiration": expiration})
        return client.format_response(result)