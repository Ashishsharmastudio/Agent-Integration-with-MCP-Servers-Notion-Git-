#!/usr/bin/env python3
"""
Test script to check GitHub commit functionality and tool schemas
"""

import os
import sys

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Load environment variables first
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

from src.integrations.mcp_manager import get_mcp_manager

def test_github_tools():
    """Test GitHub tool schemas"""
    print("Testing GitHub tool schemas...")
    
    try:
        # Initialize the MCP manager
        print("Initializing MCP manager...")
        mgr = get_mcp_manager()
        
        # Start GitHub MCP server
        print("Starting GitHub MCP server...")
        mgr.start_github()
        print("GitHub MCP server started")
        
        # List available tools with details
        print("Getting tool details...")
        handle = mgr._handles["github"]
        if handle.session is not None:
            import asyncio
            async def get_tool_details():
                if handle.session is not None:
                    res = await handle.session.list_tools()
                    return res.tools
                return []
            
            tools = asyncio.run_coroutine_threadsafe(get_tool_details(), mgr.loop).result(timeout=30)
            print(f"Available tools with details:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                    print(f"    Schema: {tool.inputSchema}")
                print()
        else:
            print("No session available")
            
    except Exception as e:
        print(f"Error during GitHub tool test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_github_tools()