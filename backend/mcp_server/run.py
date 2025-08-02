#!/usr/bin/env python3
"""
Script to run the Aiven MCP Server

This script starts the MCP server that exposes the Aiven APIs to AI agents.
"""

import os
import sys
from mcp_server.server import run_server


def main():
    print("🚀 Starting Aiven MCP Server...")
    print("This server exposes the Aiven application APIs as MCP tools for AI agents.")
    print()
    print("Available tools:")
    print("  🏥 Health check")
    print("  🤖 Agent management (CRUD)")
    print("  📄 Article management (CRUD)")
    print()
    print("Available resources:")
    print("  📚 API documentation")
    print("  ⚙️ API configuration")
    print()
    print("📡 Server starting...")
    
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down MCP server...")
    except Exception as e:
        print(f"❌ Error running MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()