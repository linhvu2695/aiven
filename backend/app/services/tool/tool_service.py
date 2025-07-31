from app.classes.tool import ToolInfo, SearchToolsResponse

TOOL_COLLECTION = [
    ToolInfo(
        id="agent-management",
        name="Agent Management",
        description="Tools for managing AI agents - create, update, search, and delete agents with different models and personas",
        emoji="🤖"
    ),
    ToolInfo(
        id="knowledge-base",
        name="Knowledge Base",
        description="Tools for managing articles and knowledge content - create, update, search, and organize knowledge articles",
        emoji="📚"
    ),
    ToolInfo(
        id="chat",
        name="Chat",
        description="Tools for interacting with AI agents - send messages, get responses, and manage chat models",
        emoji="💬"
    ),
    ToolInfo(
        id="system-health",
        name="System Health",
        description="Tools for monitoring system health and API status - check if services are running properly",
        emoji="❤️"
    ),
    ToolInfo(
        id="file-storage",
        name="File Storage",
        description="Tools for managing file storage - get presigned URLs for secure file access and storage operations",
        emoji="🗄️"
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