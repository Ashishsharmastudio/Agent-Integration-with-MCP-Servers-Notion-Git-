#!/usr/bin/env python3
"""
Demo script showing the full MCP + OpenAI integration in action.
This script demonstrates:
1. Notion MCP integration for searching and fetching content
2. OpenAI integration for reasoning and synthesis
"""

import os
import sys
import json

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Load environment variables first
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

# Import our components
from src.integrations.mcp_manager import get_mcp_manager
from src.agent_core.reasoning import ReasoningEngine
from src.web.adapters import best_notion_results

def demo():
    print("🤖 MCP + OpenAI Integration Demo")
    print("=" * 50)
    
    # Initialize components
    print("🔧 Initializing components...")
    engine = ReasoningEngine()
    mgr = get_mcp_manager()
    
    if not engine.client:
        print("❌ OpenAI client not initialized - check your API key")
        return
    
    try:
        # Start Notion MCP server
        print("🚀 Starting Notion MCP server...")
        mgr.start_notion()
        print("✅ Notion MCP server started")
        
        # Example query
        query = "medical chatbot"
        print(f"\n🔍 Query: '{query}'")
        
        # Step 1: Search Notion
        print("\n📚 Searching Notion...")
        raw_results = mgr.call_tool('notion', 'API-post-search', {'query': query})
        
        # Parse the raw results to extract pages
        notion_pages = []
        try:
            data = json.loads(raw_results) if isinstance(raw_results, str) else raw_results
            if isinstance(data, dict) and 'results' in data:
                for item in data['results']:
                    if isinstance(item, dict):
                        title = ""
                        if 'properties' in item and 'title' in item['properties']:
                            title_prop = item['properties']['title']
                            if 'title' in title_prop and title_prop['title']:
                                title = title_prop['title'][0].get('plain_text', '')
                        url = item.get('url', '')
                        if url:  # Only add pages with URLs
                            notion_pages.append({'title': title or 'Untitled', 'url': url})
        except Exception as e:
            print(f"⚠️  Error parsing search results: {e}")
        
        print(f"📄 Found {len(notion_pages)} pages")
        
        # If no pages found through parsing, use a fallback
        if not notion_pages and raw_results:
            # Try to find any URL in the raw results
            import re
            urls = re.findall(r'https://www\.notion\.so/[^\s"]+', str(raw_results))
            if urls:
                notion_pages = [{'title': 'Notion Page', 'url': urls[0]}]
                print(f"📄 Found page via URL extraction")
        
        # Step 2: Fetch content from top pages
        print("\n📖 Fetching page content...")
        notion_text = ""
        for i, page in enumerate(notion_pages[:2]):  # Limit to 2 pages
            print(f"   Fetching: {page['title']}")
            try:
                content = mgr.notion_fetch(page["url"])
                notion_text += f"# {page['title']}\n{content}\n\n"
            except Exception as e:
                print(f"   ⚠️  Error fetching {page['title']}: {e}")
        
        # If we still don't have content, use the raw results
        if not notion_text and raw_results:
            notion_text = str(raw_results)
            print("   Using raw search results as content")
        
        # Step 3: Use AI to synthesize response
        print("\n🧠 Synthesizing response with AI...")
        answer = engine.synthesize_response(
            query,
            notion_text,
            ""  # No GitHub data in this demo
        )
        
        # Display results
        print("\n" + "=" * 50)
        print("✅ DEMO COMPLETE")
        print("=" * 50)
        print(f"\n💬 AI Response:\n{answer}")
        
        print(f"\n🔗 Sources:")
        for page in notion_pages[:2]:
            print(f"   • {page['title']}: {page['url']}")
            
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo()