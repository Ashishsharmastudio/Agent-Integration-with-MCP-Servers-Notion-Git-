# src/integrations/mcp_manager.py
import os
import asyncio
import threading
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional, Tuple
import json

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Env vars — GitHub MCP server expects GITHUB_PERSONAL_ACCESS_TOKEN; limit via GITHUB_TOOLSETS.  :contentReference[oaicite:4]{index=4}
GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN") or os.getenv("GITHUB_TOKEN")
GITHUB_TOOLSETS = os.getenv("GITHUB_TOOLSETS", "repos")
GITHUB_REPO = os.getenv("GITHUB_REPO")  # "owner/repo"
GITHUB_DEFAULT_REF = os.getenv("GITHUB_DEFAULT_REF", "master")

# Notion MCP — official server expects NOTION_TOKEN (or hosted MCP). Tool names: notion-search / notion-fetch.  :contentReference[oaicite:5]{index=5}
NOTION_TOKEN = os.getenv("NOTION_TOKEN") or os.getenv("NOTION_API_KEY")


class MCPServerHandle:
    def __init__(self, name: str, params: StdioServerParameters):
        self.name = name
        self.params = params
        self.stack: Optional[AsyncExitStack] = None
        self.session: Optional[ClientSession] = None


class MCPClientManager:
    """
    Long-lived stdio connections to GitHub & Notion MCP servers on a background event loop.
    """

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()
        self._handles: Dict[str, MCPServerHandle] = {}

    # ---------- low-level ----------
    def _run_coro(self, coro, timeout: float = 60.0):
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result(timeout=timeout)

    async def _start_server(self, key: str, params: StdioServerParameters):
        handle = MCPServerHandle(key, params)
        handle.stack = AsyncExitStack()
        read, write = await handle.stack.enter_async_context(stdio_client(params))
        handle.session = await handle.stack.enter_async_context(ClientSession(read, write))
        await handle.session.initialize()
        self._handles[key] = handle

    async def _list_tools(self, key: str) -> List[str]:
        handle = self._handles[key]
        if handle.session is None:
            return []
        sess = handle.session
        res = await sess.list_tools()
        return [t.name for t in res.tools]

    def list_tools(self, key: str) -> List[str]:
        return self._run_coro(self._list_tools(key))

    async def _call_tool(self, key: str, tool: str, args: Dict[str, Any]):
        handle = self._handles[key]
        if handle.session is None:
            raise RuntimeError("Session not initialized")
        sess = handle.session
        res = await sess.call_tool(tool, args)
        # Prefer structuredData if present
        if getattr(res, "structuredContent", None):
            return res.structuredContent
        out_text = []
        for part in res.content:
            if isinstance(part, types.TextContent):
                out_text.append(part.text)
            elif isinstance(part, types.TextResourceContents):
                return part.text
            elif hasattr(part, 'json'):
                return part.json
            elif isinstance(part, types.EmbeddedResource):
                # Some servers embed resource content for files (text)  :contentReference[oaicite:6]{index=6}
                resource = part.resource
                if isinstance(resource, types.TextResourceContents) and resource.text is not None:
                    out_text.append(resource.text or "")
                elif isinstance(resource, types.BlobResourceContents):
                    # BlobResourceContents doesn't have a text attribute
                    pass
        return "\n".join(out_text).strip()

    def call_tool(self, key: str, tool: str, args: Dict[str, Any]):
        return self._run_coro(self._call_tool(key, tool, args))

    def _resolve_tool(self, key: str, candidates: List[str]) -> Optional[str]:
        tools = set(self.list_tools(key))
        for name in candidates:
            if name in tools:
                return name
        return None

    # ---------- startup ----------
    def start_github(self):
        if not GITHUB_TOKEN:
            raise RuntimeError("Set GITHUB_PERSONAL_ACCESS_TOKEN (or GITHUB_TOKEN).")
        # Use local binary by default; support Docker via env override
        cmd = os.getenv("GITHUB_MCP_COMMAND", "github-mcp-server")
        args = os.getenv("GITHUB_MCP_ARGS", "stdio").split()
        params = StdioServerParameters(
            command=cmd,
            args=args,
            env={
                "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_TOKEN,
                "GITHUB_TOOLSETS": GITHUB_TOOLSETS,
            },
        )
        self._run_coro(self._start_server("github", params))

    def start_notion(self):
        if not NOTION_TOKEN:
            raise RuntimeError("Set NOTION_TOKEN (or NOTION_API_KEY).")
        params = StdioServerParameters(
            command="npx",
            args=["-y", "@notionhq/notion-mcp-server"],
            env={"NOTION_TOKEN": NOTION_TOKEN},
        )
        self._run_coro(self._start_server("notion", params))

    # ---------- Notion helpers ----------
    def notion_search(self, query: str):
        # Tool may appear as 'notion-search' or 'search' in OpenAI hosts.  :contentReference[oaicite:7]{index=7}
        # For OpenAI clients, tools are auto-aliased to search and fetch
        tool = self._resolve_tool("notion", ["notion-search", "search", "API-post-search"])
        if not tool:
            # List available tools for debugging
            available_tools = self.list_tools("notion")
            print(f"Available Notion tools: {available_tools}")
            raise RuntimeError("Notion search tool not found.")
        return self.call_tool("notion", tool, {"query": query})

    def notion_fetch(self, url_or_id: str) -> str:
        # Try to find appropriate fetch tool
        tool = self._resolve_tool("notion", ["notion-fetch", "fetch", "API-retrieve-a-page", "API-get-page"])
        if not tool:
            # If no fetch tool found, try to use search results directly or fallback
            available_tools = self.list_tools("notion")
            print(f"Available Notion tools: {available_tools}")
            raise RuntimeError("Notion fetch tool not found.")
        try:
            return str(self.call_tool("notion", tool, {"url": url_or_id}) or "")
        except Exception:
            return str(self.call_tool("notion", tool, {"id": url_or_id}) or "")

    # ---------- GitHub helpers ----------
    @staticmethod
    def _split_owner_repo(slug: str) -> Tuple[str, str]:
        if not slug or "/" not in slug:
            raise RuntimeError("GITHUB_REPO must be 'owner/repo'.")
        return tuple(slug.split("/", 1))  # type: ignore

    def github_get_file(self, path: str, ref: Optional[str] = None):
        """
        Use get_file_contents to fetch file contents, or directory listing when path is a directory.
        Inputs: owner, repo, path, ref/branch.  :contentReference[oaicite:8]{index=8}
        """
        if GITHUB_REPO is None:
            raise RuntimeError("GITHUB_REPO environment variable not set")
        owner, repo = self._split_owner_repo(GITHUB_REPO)
        tool = self._resolve_tool("github", ["get_file_contents", "repos/get_file_contents"])
        if not tool:
            raise RuntimeError("GitHub get_file_contents tool not found.")
        args = {"owner": owner, "repo": repo, "path": path, "ref": ref or GITHUB_DEFAULT_REF}
        return self.call_tool("github", tool, args)

    def github_list_dir(self, path: str = "", ref: Optional[str] = None) -> List[Dict[str, Any]]:
        data = self.github_get_file(path, ref=ref)
        if isinstance(data, list):
            return data  # server returns array of entries for directories when supported  :contentReference[oaicite:9]{index=9}
        if isinstance(data, dict) and "entries" in data:
            return data["entries"]
        return []

    def github_list_commits(self, ref: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List commits in the repository.
        """
        if GITHUB_REPO is None:
            raise RuntimeError("GITHUB_REPO environment variable not set")
        owner, repo = self._split_owner_repo(GITHUB_REPO)
        tool = self._resolve_tool("github", ["list_commits"])
        if not tool:
            raise RuntimeError("GitHub list_commits tool not found.")
        args = {"owner": owner, "repo": repo}
        if ref:
            args["sha"] = ref
        result = self.call_tool("github", tool, args)
        if isinstance(result, str):
            try:
                parsed_result = json.loads(result)
                if isinstance(parsed_result, list):
                    return parsed_result
                elif isinstance(parsed_result, dict) and "commits" in parsed_result:
                    return parsed_result["commits"]
                else:
                    return [parsed_result] if parsed_result else []
            except json.JSONDecodeError:
                return []
        elif isinstance(result, list):
            return result
        elif isinstance(result, dict) and "commits" in result:
            return result["commits"]
        elif isinstance(result, dict):
            # Handle case where the result is a single dict with commit data
            return [result]
        return []

    def get_tool_schemas(self) -> Dict[str, Any]:
        """
        Get tool schemas for all available tools from both GitHub and Notion.
        Returns a dictionary with tool information that can be used by the LLM.
        """
        tools_info = {}
        
        # Get GitHub tools
        try:
            handle = self._handles.get("github")
            if handle and handle.session is not None:
                import asyncio
                async def get_github_tools():
                    res = await handle.session.list_tools()  # type: ignore
                    return res.tools
                
                github_tools = asyncio.run_coroutine_threadsafe(get_github_tools(), self.loop).result(timeout=30)
                for tool in github_tools:
                    tools_info[f"github_{tool.name}"] = {
                        "name": f"github_{tool.name}",
                        "description": tool.description,
                        "schema": tool.inputSchema if hasattr(tool, 'inputSchema') else {},
                        "source": "github"
                    }
        except Exception as e:
            print(f"Error getting GitHub tool schemas: {e}")
        
        # Get Notion tools
        try:
            handle = self._handles.get("notion")
            if handle and handle.session is not None:
                import asyncio
                async def get_notion_tools():
                    res = await handle.session.list_tools()  # type: ignore
                    return res.tools
                
                notion_tools = asyncio.run_coroutine_threadsafe(get_notion_tools(), self.loop).result(timeout=30)
                for tool in notion_tools:
                    tools_info[f"notion_{tool.name}"] = {
                        "name": f"notion_{tool.name}",
                        "description": tool.description,
                        "schema": tool.inputSchema if hasattr(tool, 'inputSchema') else {},
                        "source": "notion"
                    }
        except Exception as e:
            print(f"Error getting Notion tool schemas: {e}")
            
        return tools_info

# Singleton accessor (created in app startup to avoid auto-spawning during tests)
_mgr: Optional[MCPClientManager] = None

def get_mcp_manager() -> MCPClientManager:
    global _mgr
    if _mgr is None:
        _mgr = MCPClientManager()
    return _mgr
