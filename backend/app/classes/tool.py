from pydantic import BaseModel

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