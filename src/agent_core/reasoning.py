# src/agent_core/reasoning.py
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from src.agent_core.config import OPENAI_API_KEY

class ReasoningEngine:
    """
    Two-step reasoning engine:
      1) analyze_query -> returns {"notion_query": str, "git_query": str, "tools": list}
      2) synthesize_response -> grounded answer using ONLY provided context
    """

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

    def analyze_query(self, user_query: str, available_tools: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.client:
            # No API key? Just mirror the query.
            return {"notion_query": user_query, "git_query": user_query, "tools": []}
        
        # Build tool information for the LLM
        tool_descriptions = ""
        if available_tools:
            tool_descriptions = "\n\nAvailable tools:\n"
            for tool_name, tool_info in available_tools.items():
                tool_descriptions += f"- {tool_name}: {tool_info['description']}\n"
                if tool_info.get('schema'):
                    tool_descriptions += f"  Schema: {json.dumps(tool_info['schema'])}\n"
        
        try:
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                temperature=0.0,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a query analyzer that determines what tools to use and how to split the query. "
                            "Return JSON with keys 'notion_query', 'git_query', and 'tools'. "
                            "The 'tools' key should be a list of tool names to use. "
                            "Select tools based on their descriptions and schemas. "
                            "For commit-related queries, select 'github_list_commits'. "
                            "Both query values MUST be strings."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this query and determine appropriate tools: {user_query}{tool_descriptions}",
                    },
                ],
            )
            content = resp.choices[0].message.content
            if content is None:
                return {"notion_query": user_query, "git_query": user_query, "tools": []}
            data = json.loads(content)
            return {
                "notion_query": str(data.get("notion_query", user_query)),
                "git_query": str(data.get("git_query", user_query)),
                "tools": data.get("tools", []),
            }
        except Exception:
            return {"notion_query": user_query, "git_query": user_query, "tools": []}

    def synthesize_response(self, user_query: str, notion_context: str, git_context: str) -> str:
        if not self.client:
            return "Unable to generate response: OpenAI client not initialized."
        try:
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.2,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an assistant that synthesizes responses using ONLY the provided context. "
                            "Clearly cite Notion vs GitHub when you refer to specific details."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"User Query: {user_query}\n\n"
                            f"Notion Context:\n{notion_context}\n\n"
                            f"Git Context:\n{git_context}\n\n"
                            f"Provide a concise answer grounded ONLY in the context above."
                        ),
                    },
                ],
            )
            content = resp.choices[0].message.content
            return content.strip() if content is not None else ""
        except Exception:
            return "Unable to synthesize response due to an error."