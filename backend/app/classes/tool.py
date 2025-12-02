from pydantic import BaseModel
from typing import Optional, Any

class ToolInfo(BaseModel):
    """Information about an available MCP tool"""
    id: str
    name: str
    description: str
    emoji: str
    mcp_functions: list[str]

class SearchToolsResponse(BaseModel):
    """Response for tool search endpoint"""
    tools: list[ToolInfo]

class MCPToolInfo(BaseModel):
    """Information about a registered MCP tool"""
    name: str
    description: Optional[str] = None
    inputSchema: Optional[dict[str, Any]] = None
    outputSchema: Optional[dict[str, Any]] = None

class MCPToolsResponse(BaseModel):
    """Response for MCP tools list endpoint"""
    total: int
    tools: list[MCPToolInfo]