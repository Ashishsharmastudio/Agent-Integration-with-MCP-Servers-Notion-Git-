#!/usr/bin/env python3
"""
Test script for GitHub MCP integration
"""

import os
import sys

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Load environment variables first
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

# Import our components
from src.integrations.mcp_manager import get_mcp_manager

def test_github_integration():
    print("Testing GitHub MCP integration...")
    
    # Check environment variables
    github_token = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN') or os.getenv('GITHUB_TOKEN')
    github_repo = os.getenv('GITHUB_REPO')
    print(f"GITHUB_TOKEN: {github_token[:10] + '...' if github_token else 'Not found'}")
    print(f"GITHUB_REPO: {github_repo if github_repo else 'Not found'}")
    
    if not github_token:
        print("❌ GITHUB_PERSONAL_ACCESS_TOKEN not set")
        return
        
    if not github_repo:
        print("❌ GITHUB_REPO not set")
        return
    
    try:
        # Initialize the MCP manager
        print("\n🔧 Initializing MCP manager...")
        mgr = get_mcp_manager()
        
        # Start GitHub MCP server
        print("🚀 Starting GitHub MCP server...")
        mgr.start_github()
        print("✅ GitHub MCP server started")
        
        # List available tools
        print("\n📚 Listing available GitHub tools...")
        tools = mgr.list_tools('github')
        print(f"Available GitHub tools: {tools}")
        
        # Check if we have the file read tool
        file_read_tools = [tool for tool in tools if 'file' in tool.lower() or 'get' in tool.lower()]
        print(f"File read tools: {file_read_tools}")
        
        # Try to read a file
        print("\n📖 Trying to read README.md...")
        try:
            content = mgr.github_get_file("README.md")
            print(f"✅ Successfully read README.md ({len(str(content))} characters)")
            print(f"Content preview: {str(content)[:200]}...")
        except Exception as e:
            print(f"⚠️  Error reading README.md: {e}")
            
    except Exception as e:
        print(f"❌ Error during GitHub test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_github_integration()