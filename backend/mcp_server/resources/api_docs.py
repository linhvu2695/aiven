"""
API documentation resource for the Aiven MCP Server
"""

from mcp.server.fastmcp import FastMCP


def register_api_docs_resource(mcp: FastMCP):
    """Register API documentation resource with the MCP server"""
    
    @mcp.resource("aiven://api/docs")
    def get_api_docs() -> str:
        """Get documentation for the Aiven API endpoints"""
        return """
# Aiven API Documentation

## Agent API  
- GET /api/agent/id={id} - Get agent by ID
- POST /api/agent/ - Create/update agent
- GET /api/agent/search - Search agents
- POST /api/agent/delete?id={id} - Delete agent
- POST /api/agent/avatar - Update agent avatar

## Article API
- GET /api/article/id={id} - Get article by ID  
- POST /api/article/ - Create/update article
- GET /api/article/search - Search articles
- POST /api/article/delete?id={id} - Delete article

## Health API
- GET /api/ping - Health check
"""