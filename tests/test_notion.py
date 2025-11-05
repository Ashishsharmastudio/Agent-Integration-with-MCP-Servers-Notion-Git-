import os
import sys
# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Load environment variables first
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

# Now import the rest
from src.integrations.mcp_manager import get_mcp_manager

def test_notion_integration():
    print("Testing Notion MCP integration...")
    
    # Check environment variables
    notion_token = os.getenv('NOTION_TOKEN') or os.getenv('NOTION_API_KEY')
    print(f"NOTION_TOKEN: {notion_token[:10] + '...' if notion_token else 'Not found'}")
    
    # Get the manager
    mgr = get_mcp_manager()
    
    try:
        # Start the Notion server
        print("Starting Notion MCP server...")
        mgr.start_notion()
        print("Notion MCP server started successfully!")
        
        # List available tools
        print("Listing available tools...")
        tools = mgr.list_tools('notion')
        print(f"Available Notion tools: {tools}")
        
        # Look for search-related tools
        search_tools = [tool for tool in tools if 'search' in tool.lower()]
        print(f"Search-related tools: {search_tools}")
        
        # Try using the API-post-search tool directly
        if 'API-post-search' in tools:
            print("Performing a test search using API-post-search...")
            results = mgr.call_tool('notion', 'API-post-search', {'query': 'test'})
            print(f"Search results: {results}")
        else:
            print("No search tool found")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_notion_integration()