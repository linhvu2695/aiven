# Aiven MCP Server

This directory contains a Model Context Protocol (MCP) server that exposes the Aiven application APIs as tools and resources for AI agents to use.

## What is MCP?

The Model Context Protocol (MCP) is a protocol developed by Anthropic that allows AI assistants to securely access external systems and data. This MCP server acts as a bridge between AI agents and your Aiven application APIs.

## Features

### Tools (AI Agent Actions)
- **Health Check**: Check if the API server is responding
- **Agent Management**: Create, read, update, and delete agents
- **Article Management**: Create, read, update, and delete articles

### Resources (Information Access)
- **API Documentation**: Complete documentation of available endpoints
- **API Configuration**: Current server configuration and available models

## Setup

1. **Install Dependencies** (if not already installed):
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Ensure FastAPI Server is Running**:
   The MCP server connects to your FastAPI backend, so make sure it's running on `http://localhost:8000`:
   ```bash
   # In the backend directory
   python main.py
   # or
   uvicorn main:app --reload
   ```

## Running the MCP Server

### Option 1: Direct Execution
```bash
cd backend
python -m mcp_server.server
```

### Option 2: Using the Run Script
```bash
cd backend  
python -m mcp_server.run
```

### Option 3: Development Mode (using mcp CLI)
```bash
cd backend
uv run mcp dev mcp_server/server.py
```

### Option 4: Using Makefile
```bash
cd backend
make run-mcp        # Production mode
make run-mcp-dev    # Development mode
```

## Using with Claude Desktop

To use this MCP server with Claude Desktop, you can install it using the MCP CLI:

```bash
cd backend
uv run mcp install mcp_server/server.py --name "Aiven API Server"
```

This will add the server to your Claude Desktop configuration.

## Example Usage

Once connected, an AI agent can:

1. **Check system health**:
   - Use the `ping_health` tool

2. **Manage agents**:
   - Use `search_agents` to list all agents
   - Use `create_or_update_agent` to create a new agent
   - Use `get_agent` to retrieve agent details
   - Use `delete_agent` to remove an agent

3. **Manage articles**:
   - Use `search_articles` to list articles
   - Use `create_or_update_article` to create content
   - Use `get_article` to retrieve specific articles

4. **Access documentation**:
   - Read the `aiven://api/docs` resource for API documentation
   - Read the `aiven://api/config` resource for configuration info

## Configuration

The MCP server is configured to connect to your FastAPI backend at `http://localhost:8000`. You can modify the `base_url` in the `AivenMCPServer` class if your API runs on a different port or host.

## Architecture

```
AI Agent (Claude/etc.)
       ↓ 
   MCP Protocol
       ↓
   MCP Server (this)
       ↓
   HTTP Requests  
       ↓
   FastAPI Backend (your app)
       ↓
   MongoDB/Storage
```

## Troubleshooting

1. **Connection Errors**: Ensure your FastAPI server is running and accessible
2. **Tool Errors**: Check the FastAPI logs for API endpoint issues
3. **MCP Protocol Issues**: Run in development mode with `mcp dev` for detailed logs

## Security

The MCP server acts as a proxy to your APIs. Make sure:
- Your FastAPI server has proper authentication/authorization
- The MCP server only exposes the APIs you want agents to access
- Consider running the MCP server in a controlled environment

## Next Steps

- Add authentication to the MCP server if needed
- Implement rate limiting for tool calls
- Add more sophisticated error handling
- Create custom prompts for common workflows 