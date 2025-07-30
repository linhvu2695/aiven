"""
Configuration for the Aiven MCP Server
"""

import os
from typing import Optional


class MCPConfig:
    """Configuration settings for the MCP server"""
    
    def __init__(self):
        self.api_base_url = os.getenv("AIVEN_API_BASE_URL", "http://localhost:8000")
        self.server_name = "Aiven API Server"
        self.version = "1.0.0"
        self.timeout = 30.0
        
    @property
    def api_url(self) -> str:
        """Get the full API base URL"""
        return self.api_base_url.rstrip("/")


# Global config instance
config = MCPConfig()