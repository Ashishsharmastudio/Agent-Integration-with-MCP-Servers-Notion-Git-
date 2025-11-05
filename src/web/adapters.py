# src/web/adapters.py
from typing import Any, Dict, List

def best_notion_results(raw: Any, limit: int = 3) -> List[Dict[str, str]]:
    """
    Normalize Notion MCP search output to [{'title', 'url'}].
    """
    out: List[Dict[str, str]] = []
    if isinstance(raw, list):
        for it in raw[:limit]:
            title = ""
            url = ""
            if isinstance(it, dict):
                title = it.get("title") or it.get("name") or ""
                url = it.get("url") or it.get("uri") or it.get("link") or ""
            else:
                title = getattr(it, "title", "") or getattr(it, "name", "")
                url = getattr(it, "url", "") or getattr(it, "uri", "") or getattr(it, "link", "")
            if url:
                out.append({"title": title or "(untitled)", "url": url})
    elif isinstance(raw, dict) and "results" in raw:
        for it in raw["results"][:limit]:
            title = it.get("title") or it.get("name") or ""
            url = it.get("url") or it.get("uri") or it.get("link") or ""
            if url:
                out.append({"title": title or "(untitled)", "url": url})
    return out[:limit]

def gh_blob_link(owner_repo: str, ref: str, path: str) -> str:
    owner, repo = owner_repo.split("/", 1)
    return f"https://github.com/{owner}/{repo}/blob/{ref}/{path}"
