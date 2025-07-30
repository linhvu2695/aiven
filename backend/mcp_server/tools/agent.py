"""
Agent management tools for the Aiven MCP Server
"""

from typing import Optional
from mcp.server.fastmcp import FastMCP
from mcp_server.client import AivenAPIClient


def register_agent_tools(mcp: FastMCP, client: AivenAPIClient):
    """Register agent management tools with the MCP server"""
    
    @mcp.tool()
    async def get_agent(agent_id: str) -> str:
        """Retrieve an agent by its ID
        
        Args:
            agent_id: The ID of the agent to retrieve
        """
        result = await client.request("GET", f"/api/agent/id={agent_id}")
        return client.format_response(result)

    @mcp.tool()
    async def create_or_update_agent(name: str, persona: str, model: str, agent_id: Optional[str] = None) -> str:
        """Create a new agent or update an existing one
        
        Args:
            name: Name of the agent
            persona: Persona/system prompt for the agent
            model: LLM model to use for this agent
            agent_id: Optional ID for updating existing agent
        """
        data = {
            "name": name,
            "persona": persona,
            "model": model
        }
        if agent_id:
            data["id"] = agent_id
            
        result = await client.request("POST", "/api/agent/", data)
        return client.format_response(result)

    @mcp.tool()
    async def search_agents() -> str:
        """Search for available agents"""
        result = await client.request("GET", "/api/agent/search")
        return client.format_response(result)

    @mcp.tool()
    async def delete_agent(agent_id: str) -> str:
        """Delete an agent by ID
        
        Args:
            agent_id: The ID of the agent to delete
        """
        result = await client.request("POST", "/api/agent/delete", {"id": agent_id})
        return client.format_response(result)