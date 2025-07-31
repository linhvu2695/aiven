from fastapi import APIRouter
from app.classes.tool import SearchToolsResponse
from app.services.tool.tool_service import ToolService

router = APIRouter()

@router.get("/search", response_model=SearchToolsResponse)
async def search_tools():
    """Get all available MCP tools"""
    return await ToolService().search_tools()