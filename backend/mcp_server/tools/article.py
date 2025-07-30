"""
Article management tools for the Aiven MCP Server
"""

from typing import Optional
from mcp.server.fastmcp import FastMCP
from mcp_server.client import AivenAPIClient


def register_article_tools(mcp: FastMCP, client: AivenAPIClient):
    """Register article management tools with the MCP server"""
    
    @mcp.tool()
    async def get_article(article_id: str) -> str:
        """Retrieve an article by its ID
        
        Args:
            article_id: The ID of the article to retrieve
        """
        result = await client.request("GET", f"/api/article/id={article_id}")
        return client.format_response(result)

    @mcp.tool()
    async def create_or_update_article(title: str, content: str, article_id: Optional[str] = None) -> str:
        """Create a new article or update an existing one
        
        Args:
            title: Title of the article
            content: Content of the article
            article_id: Optional ID for updating existing article
        """
        data = {
            "title": title,
            "content": content
        }
        if article_id:
            data["id"] = article_id
            
        result = await client.request("POST", "/api/article/", data)
        return client.format_response(result)

    @mcp.tool()
    async def search_articles() -> str:
        """Search for available articles"""
        result = await client.request("GET", "/api/article/search")
        return client.format_response(result)

    @mcp.tool()
    async def delete_article(article_id: str) -> str:
        """Delete an article by ID
        
        Args:
            article_id: The ID of the article to delete
        """
        result = await client.request("POST", "/api/article/delete", {"id": article_id})
        return client.format_response(result)