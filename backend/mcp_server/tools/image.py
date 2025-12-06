"""
Image generation tools for the Aiven MCP Server
"""

from urllib.parse import urlencode
from mcp.server.fastmcp import FastMCP
from app.services.image.image_constants import ImageGenModel
from app.services.image.image_gen.image_gen_aspect_ratio import ImageGenAspectRatio
from mcp_server.client import AivenAPIClient


def register_image_tools(mcp: FastMCP, client: AivenAPIClient):
    """Register image generation tools with the MCP server"""
    
    @mcp.tool()
    async def generate_image(prompt: str) -> str:
        """Generate an image using AI based on a text prompt
        
        Args:
            prompt: The text description of the image to generate
        """
        # Set default values
        model = ImageGenModel.GEMINI_2_5_FLASH_IMAGE.value
        aspect_ratio = ImageGenAspectRatio.RATIO_1_1.value
        
        # Build query parameters with proper URL encoding
        params = {
            "prompt": prompt,
            "model": model,
            "aspect_ratio": aspect_ratio,
        }
        
        result = await client.request(
            "POST", 
            f"/api/image/generate?{urlencode(params)}"
        )
        return client.format_response(result)

