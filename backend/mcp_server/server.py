"""
Main MCP Server for Aiven Application APIs

This module creates and configures the MCP server that exposes the Aiven 
application APIs as tools and resources for AI agents.
"""

import sys
import os
from pathlib import Path

# Add backend directory to Python path for both package and direct execution
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from mcp.server.fastmcp import FastMCP

from mcp_server.config import config
from mcp_server.client import AivenAPIClient
from mcp_server.tools import (
    register_health_tools,
    register_agent_tools,
    register_article_tools
)
from mcp_server.resources import (
    register_api_docs_resource,
    register_config_resource
)


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all tools and resources"""
    
    # Create the FastMCP server
    mcp = FastMCP(config.server_name)
    
    # Create API client  
    client = AivenAPIClient()
    
    # Register all tools
    register_health_tools(mcp, client)
    register_agent_tools(mcp, client)
    register_article_tools(mcp, client)
    
    # Register all resources
    register_api_docs_resource(mcp)
    register_config_resource(mcp)
    
    return mcp


def run_server():
    """Run the MCP server"""
    server = create_mcp_server()
    server.run()


# Create the server instance that MCP CLI expects
mcp = create_mcp_server()

if __name__ == "__main__":
    run_server()