import logging
from pathlib import Path
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
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
        id="system-health",
        name="System Health",
        description="Tools for monitoring system health and API status - check if services are running properly",
        emoji="❤️",
        mcp_functions=["ping_health"]
    ),
    ToolInfo(
        id="image-generation",
        name="Image Generation",
        description="Tools for generating images using AI - create images from text prompts using various AI providers",
        emoji="🎨",
        mcp_functions=["generate_image"]
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
        """Get MCP functions for tools"""
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

    async def load_mcp_functions(self, tool_names: list[str]) -> list[BaseTool]:
        """Load MCP functions from the MCP server based on tool names"""
        if not tool_names:
            return []

        try:
            # Get the path to the MCP server
            current_dir = Path(__file__).parent
            backend_dir = current_dir.parent.parent.parent
            mcp_server_path = backend_dir / "mcp_server" / "server.py"

            client = MultiServerMCPClient(
                {
                    "aiven": {
                        "command": "python",
                        "args": [str(mcp_server_path)],
                        "transport": "stdio",
                    }
                }
            )

            # Get all available tools from MCP server
            all_functions = await client.get_tools()

            allowed_mcp_functions = self.get_mcp_functions_for_tools(
                tool_names
            )

            filtered_functions: list[BaseTool] = []
            for function in all_functions:
                if function.name in allowed_mcp_functions:
                    filtered_functions.append(function)
            return filtered_functions

        except Exception as e:
            logging.getLogger("uvicorn.warning").warning(
                f"Warning: Could not load MCP tools: {e}"
            )
            return []