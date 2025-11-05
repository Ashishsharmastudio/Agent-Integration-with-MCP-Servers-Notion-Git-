# src/web/routes.py
import os
from typing import Any, Dict, List

from flask import Flask, jsonify, request, Response

from src.agent_core.reasoning import ReasoningEngine
from src.integrations.mcp_manager import (
    get_mcp_manager,
    GITHUB_REPO,
    GITHUB_DEFAULT_REF,
)
from src.web.adapters import best_notion_results, gh_blob_link
from src.integrations.feature_diff import (
    compare_feature_sets,
    summarize_feature_diff,
)

def _walk_repo_paths(mcp_mgr, keywords: List[str], max_files: int = 12, max_depth: int = 4) -> List[str]:
    """
    Walk the repo tree via GitHub MCP by listing directories (no Search API).
    """
    visited = set()
    queue: List[tuple[str, int]] = [("", 0)]
    all_files: List[str] = []
    while queue and len(all_files) < 1000:
        base, depth = queue.pop(0)
        if depth > max_depth:
            continue
        entries = mcp_mgr.github_list_dir(base, ref=GITHUB_DEFAULT_REF)
        for e in entries:
            etype = e.get("type") or e.get("kind") or ""
            path = e.get("path") or e.get("name") or ""
            if not path:
                continue
            if etype.startswith("dir") or etype == "tree":
                if path not in visited:
                    visited.add(path)
                    queue.append((path, depth + 1))
            elif etype == "file" or etype == "blob":
                all_files.append(path)

    GOOD_EXTS = (".md", ".py", ".js", ".ts", ".tsx", ".json", ".yml", ".yaml", ".toml", ".ipynb", ".txt")
    kw = [k.lower() for k in keywords if k and k.strip()]
    def score(p: str) -> int:
        pl = p.lower()
        base = sum(1 for k in kw if k in pl)
        ext_bonus = 1 if pl.endswith(GOOD_EXTS) else 0
        return base * 10 + ext_bonus

    picks = sorted(all_files, key=lambda p: (-score(p), len(p)))
    picks = [p for p in picks if score(p) > 0][:max_files] or [p for p in picks[:max_files]]
    return picks

def _query_llm(prompt: str) -> str:
    # lightweight proxy so feature_diff can call it
    from openai import OpenAI
    from src.agent_core.config import OPENAI_API_KEY
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    if not client:
        return "LLM unavailable."
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You synthesize concise, actionable diffs from Notion docs and GitHub code."},
                {"role": "user", "content": prompt},
            ],
        )
        content = r.choices[0].message.content
        return content.strip() if content is not None else ""
    except Exception:
        return "LLM error."

def create_app() -> Flask:
    app = Flask(__name__)
    re_engine = ReasoningEngine()

    # Start MCP servers once (long-lived sessions)
    mcp_mgr = get_mcp_manager()
    mcp_mgr.start_github()  # uses github-mcp-server stdio + env token  :contentReference[oaicite:10]{index=10}
    try:
        mcp_mgr.start_notion()  # uses Notion stdio via npx + NOTION_TOKEN  :contentReference[oaicite:11]{index=11}
    except Exception as e:
        print(f"Failed to start Notion MCP server: {e}")

    @app.get("/agent")
    def agent():
        query_param = request.args.get("query", "")
        q = query_param.strip() if query_param is not None else ""
        if not q:
            return jsonify({"error": "No query provided"}), 400

        # Step 1: split query and determine tools
        re_engine = ReasoningEngine()
        # Get available tools
        try:
            tool_schemas = mcp_mgr.get_tool_schemas()
        except Exception as e:
            print(f"Error getting tool schemas: {e}")
            tool_schemas = {}
        
        sub = re_engine.analyze_query(q, tool_schemas)
        notion_query = str(sub.get("notion_query", q))
        git_query = str(sub.get("git_query", q))
        selected_tools = sub.get("tools", [])

        # Handle direct tool execution for specific cases
        tool_results = {}
        for tool_name in selected_tools:
            try:
                if tool_name == "github_list_commits":
                    commits = mcp_mgr.github_list_commits()
                    commit_count = len(commits)
                    answer_text = f"The repository has {commit_count} commits."
                    return jsonify({
                        "answer": answer_text,
                        "sources": [],
                        "confidence": 0.95
                    })
                elif tool_name == "github_list_branches":
                    # We would implement branch listing here
                    pass
                # Add more tool handlers as needed
            except Exception as e:
                print(f"Error executing tool {tool_name}: {e}")
                # Continue with other tools or fall through to regular processing

        # Step 2: Notion search + fetch
        notion_text = ""
        notion_sources: List[str] = []
        try:
            notion_search_results = mcp_mgr.notion_search(notion_query)
            notion_pages = best_notion_results(notion_search_results, limit=2)
            
            for page in notion_pages:
                notion_text += f"# {page['title']}\n"
                try:
                    # Try to fetch the full page content
                    page_content = mcp_mgr.notion_fetch(page["url"])
                    notion_text += page_content + "\n"
                except Exception as fetch_error:
                    # If we can't fetch the page, use the search result data
                    print(f"Could not fetch page content: {fetch_error}")
                    notion_text += "Content unavailable.\n"
                notion_sources.append(f"Notion: [{page['title']}]({page['url']})")
                
            # If we couldn't get any page content, use the raw search results
            if not notion_text.strip():
                notion_text = str(notion_search_results) if notion_search_results else ""
        except Exception as e:
            print(f"Error with Notion integration: {e}")
            # Even if we have errors, we might still have some data

        # Step 3: GitHub walk + read top files
        github_text = ""
        gh_sources: List[str] = []
        try:
            keywords = git_query.split()
            file_paths = _walk_repo_paths(mcp_mgr, keywords, max_files=12)
            for pth in file_paths:
                try:
                    content = mcp_mgr.github_get_file(pth, ref=GITHUB_DEFAULT_REF)
                    if isinstance(content, (dict, list)):
                        continue  # directory or structured content
                    if isinstance(content, str) and content:
                        github_text += f"{pth}:\n{content}\n"
                        if GITHUB_REPO is not None:
                            gh_sources.append(f"GitHub: [{pth}]({gh_blob_link(GITHUB_REPO, GITHUB_DEFAULT_REF, pth)})")
                        else:
                            gh_sources.append(f"GitHub: {pth}")
                except Exception as e:
                    print(f"Error fetching GitHub file {pth}: {e}")
        except Exception as e:
            print(f"Error with GitHub integration: {e}")

        # Step 4: diff or synthesize
        lower_q = q.lower()
        
        # Handle feature comparison
        if any(w in lower_q for w in ("compare", "difference", "diff", "different")) and "feature" in lower_q:
            only_n, only_c, overlap = compare_feature_sets(notion_text, github_text)
            answer_text = summarize_feature_diff(_query_llm, only_n, only_c, overlap)
            return jsonify({
                "answer": answer_text,
                "diff": {
                    "only_in_notion": sorted(list(only_n)),
                    "only_in_code": sorted(list(only_c)),
                    "overlap": sorted(list(overlap)),
                },
                "sources": notion_sources + gh_sources,
                "confidence": 0.85 if overlap else 0.7,
            })

        answer_text = re_engine.synthesize_response(q, notion_text, github_text)
        return jsonify({"answer": answer_text, "sources": notion_sources + gh_sources, "confidence": 0.9})

    @app.get("/healthz")
    def health() -> Response:
        return jsonify({"ok": True})

    return app
