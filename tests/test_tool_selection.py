#!/usr/bin/env python3
"""
Test script to verify LLM tool selection based on schemas
"""

import os
import sys

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Load environment variables first
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

from src.agent_core.reasoning import ReasoningEngine
from src.integrations.mcp_manager import get_mcp_manager

def test_tool_selection():
    """Test LLM tool selection based on schemas"""
    print("Testing LLM tool selection based on schemas...")
    
    try:
        # Initialize components
        print("Initializing components...")
        engine = ReasoningEngine()
        mgr = get_mcp_manager()
        
        # Start MCP servers
        print("Starting MCP servers...")
        mgr.start_github()
        mgr.start_notion()
        
        # Get tool schemas
        print("Getting tool schemas...")
        tool_schemas = mgr.get_tool_schemas()
        print(f"Available tools: {list(tool_schemas.keys())}")
        
        # Test various queries
        test_queries = [
            "How many commits are in the repository?",
            "What is this project about?",
            "Search for documentation about the API",
            "List the branches in the repository",
            "Get the latest release information"
        ]
        
        for query in test_queries:
            print(f"\nTesting query: '{query}'")
            result = engine.analyze_query(query, tool_schemas)
            print(f"  Notion query: {result.get('notion_query')}")
            print(f"  Git query: {result.get('git_query')}")
            print(f"  Selected tools: {result.get('tools')}")
            
    except Exception as e:
        print(f"Error during tool selection test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tool_selection()