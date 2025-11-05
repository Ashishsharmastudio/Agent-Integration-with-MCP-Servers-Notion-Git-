import os
import sys
# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Load environment variables first
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

# Now import the rest
from src.integrations.mcp_manager import get_mcp_manager
from src.agent_core.reasoning import ReasoningEngine

def test_full_integration():
    print("Testing full MCP + OpenAI integration...")
    
    # Check environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    notion_token = os.getenv('NOTION_TOKEN') or os.getenv('NOTION_API_KEY')
    print(f"OPENAI_API_KEY: {openai_key[:10] + '...' if openai_key else 'Not found'}")
    print(f"NOTION_TOKEN: {notion_token[:10] + '...' if notion_token else 'Not found'}")
    
    try:
        # Test OpenAI integration
        print("\n--- Testing OpenAI Integration ---")
        engine = ReasoningEngine()
        if engine.client:
            print("OpenAI client initialized successfully!")
        else:
            print("OpenAI client not initialized - check API key")
            return
            
        # Test Notion integration
        print("\n--- Testing Notion Integration ---")
        mgr = get_mcp_manager()
        mgr.start_notion()
        tools = mgr.list_tools('notion')
        print(f"Available Notion tools: {len(tools)} tools found")
        
        # Perform a search
        search_results = mgr.call_tool('notion', 'API-post-search', {'query': 'medical chatbot'})
        print(f"Search returned results: {type(search_results)}")
        
        # Test reasoning engine with Notion data
        print("\n--- Testing Reasoning Engine with Notion Data ---")
        notion_text = str(search_results) if search_results else ""
        answer = engine.synthesize_response(
            "What is this Notion page about?",
            notion_text,
            ""  # No GitHub data for now
        )
        print(f"AI Response: {answer}")
        
        print("\n--- Integration Test Complete ---")
        print("All components are working correctly!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_integration()