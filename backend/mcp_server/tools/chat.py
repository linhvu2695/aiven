"""
Chat-related tools for the Aiven MCP Server
"""

from typing import List, Dict
from mcp.server.fastmcp import FastMCP
from mcp_server.client import AivenAPIClient


def register_chat_tools(mcp: FastMCP, client: AivenAPIClient):
    """Register chat-related tools with the MCP server"""
    
    @mcp.tool()
    async def chat_with_agent(messages: List[Dict[str, str]], agent: str) -> str:
        """Send a chat message to an agent and get a response
        
        Args:
            messages: Array of chat messages with role and content
            agent: ID of the agent to chat with
        """
        data = {
            "messages": messages,
            "agent": agent
        }
        result = await client.request("POST", "/api/chat/", data)
        return client.format_response(result)

    @mcp.tool()
    async def get_chat_models() -> str:
        """Get list of available chat models"""
        result = await client.request("GET", "/api/chat/models")
        return client.format_response(result)