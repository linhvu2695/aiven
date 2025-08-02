from app.classes.tool import ToolInfo, SearchToolsResponse

TOOL_COLLECTION = [
    ToolInfo(
        id="agent-management",
        name="Agent Management",
        description="Tools for managing AI agents - create, update, search, and delete agents with different models and personas",
        emoji="🤖",
        mcp_functions=["get_agent", "create_or_update_agent", "search_agents", "delete_agent"]
    ),
    ToolInfo(
        id="knowledge-base",
        name="Knowledge Base",
        description="Tools for managing articles and knowledge content - create, update, search, and organize knowledge articles",
        emoji="📚",
        mcp_functions=["get_article", "create_or_update_article", "search_articles", "delete_article"]
    ),
    ToolInfo(
        id="chat",
        name="Chat",
        description="Tools for interacting with AI agents - send messages, get responses, and manage chat models",
        emoji="💬",
        mcp_functions=["chat_with_agent", "get_chat_models"]
    ),
    ToolInfo(
        id="system-health",
        name="System Health",
        description="Tools for monitoring system health and API status - check if services are running properly",
        emoji="❤️",
        mcp_functions=["ping_health"]
    ),
    ToolInfo(
        id="file-storage",
        name="File Storage",
        description="Tools for managing file storage - get presigned URLs for secure file access and storage operations",
        emoji="🗄️",
        mcp_functions=["get_presigned_url"]
    ),
]


class ToolService:
    """Service for managing and retrieving available MCP tools"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(ToolService, cls).__new__(cls)
        return cls._instance

    async def search_tools(self) -> SearchToolsResponse:
        """Get all available tools"""
        return SearchToolsResponse(tools=TOOL_COLLECTION)
    
    def get_mcp_functions_for_tools(self, tool_ids: list[str]) -> set[str]:
        mcp_functions = set()
        
        # Create a lookup map for faster access
        tool_map = {tool.id: tool for tool in TOOL_COLLECTION}
        
        for tool_id in tool_ids:
            if tool_id in tool_map:
                mcp_functions.update(tool_map[tool_id].mcp_functions)
            else:
                # Log warning for unknown tool ID but don't fail
                print(f"Warning: Unknown tool ID '{tool_id}' - no MCP functions found")
        
        return mcp_functions