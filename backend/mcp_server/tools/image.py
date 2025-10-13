"""
Image generation tools for the Aiven MCP Server
"""

from mcp.server.fastmcp import FastMCP
from app.services.image.image_gen.image_gen_providers import ImageGenProvider
from mcp_server.client import AivenAPIClient


def register_image_tools(mcp: FastMCP, client: AivenAPIClient):
    """Register image generation tools with the MCP server"""
    
    @mcp.tool()
    async def generate_image(prompt: str, provider: ImageGenProvider = ImageGenProvider.GEMINI) -> str:
        """Generate an image using AI based on a text prompt
        
        Args:
            prompt: The text description of the image to generate
            provider: The AI provider to use (default: gemini)
        """
        result = await client.request(
            "POST", 
            f"/api/image/generate?prompt={prompt}&provider={provider}"
        )
        return client.format_response(result)

