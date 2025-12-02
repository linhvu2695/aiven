from fastapi import APIRouter
from app.classes.tool import SearchToolsResponse, MCPToolsResponse, MCPToolInfo
from app.services.tool.tool_service import ToolService
from mcp_server.server import get_mcp_server

router = APIRouter()

@router.get("/search", response_model=SearchToolsResponse)
async def search_tools():
    """Get all available MCP tools"""
    return await ToolService().search_tools()

@router.get("/mcp", response_model=MCPToolsResponse)
async def list_mcp_tools():
    """Get all registered MCP tools from the MCP server"""
    mcp = get_mcp_server()
    tools = await mcp.list_tools()
    
    return MCPToolsResponse(
        total=len(tools),
        tools=[
            MCPToolInfo(
                name=tool.name,
                description=tool.description,
                inputSchema=tool.inputSchema if tool.inputSchema else None,
                outputSchema=tool.outputSchema if tool.outputSchema else None
            )
            for tool in tools
        ]
    )