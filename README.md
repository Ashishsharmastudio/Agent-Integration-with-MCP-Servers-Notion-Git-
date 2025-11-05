# MCP Agent (Flask + Notion/GitHub via MCP)

Production-ready skeleton using **official** MCP servers:
- **GitHub MCP Server** over STDIO with `GITHUB_PERSONAL_ACCESS_TOKEN` and `GITHUB_TOOLSETS`. :contentReference[oaicite:15]{index=15}
- **Notion MCP** via `@notionhq/notion-mcp-server` (tools: `notion-search`, `notion-fetch`, auto-aliased to `search`/`fetch` in some hosts). :contentReference[oaicite:16]{index=16}
- Python MCP SDK client flow: `stdio_client` → `ClientSession.initialize()` → `call_tool()`; parse `CallToolResult` (text/JSON/resources). :contentReference[oaicite:17]{index=17}

## Features

- **LLM-Powered Tool Selection**: Intelligent tool selection based on tool descriptions and JSON schemas
- **Direct Tool Execution**: Commit count queries return direct answers ("The repository has 3 commits")
- **Feature Comparison**: Compare features between Notion documentation and GitHub code
- **Multi-Source Synthesis**: AI synthesizes responses using data from both Notion and GitHub
- **Docker Support**: Run the application in Docker containers
- **Comprehensive Testing**: Full test suite for all components

## Quickstart

### Option 1: Single-Command Docker Execution (Recommended)
```bash
# Linux/macOS
./run_with_docker.sh

# Windows
run_with_docker.bat
```

### Option 2: Manual Setup
```bash
cp .env.example .env
# fill tokens
pip install -r requirements.txt
python app.py
# GET http://127.0.0.1:5000/agent?query=compare%20features%20between%20docs%20and%20code
```

## Available Tools

The MCP Agent has access to 35+ tools across GitHub and Notion:

### GitHub Tools (17 tools)
- `list_commits` - Get list of commits in a repository
- `list_branches` - List branches in a repository
- `get_file_contents` - Get file or directory contents
- `search_code` - Search code across GitHub repositories
- `search_repositories` - Find repositories by various criteria
- `get_latest_release` - Get the latest release information
- And 12 more tools for repository management

### Notion Tools (18 tools)
- `notion-search` - Search Notion pages
- `notion-fetch` - Fetch Notion page content
- `API-post-search` - Direct API search
- And 15 more tools for content management

## API Endpoints

- `GET /healthz` - Health check endpoint
- `GET /agent` - Main query endpoint
  - Parameters:
    - `query` (required) - The query string

## Example Queries

- **Commit Information**: "How many commits are in the repository?" → "The repository has 3 commits."
- **Branch Information**: "What branches are in the repo?" → List of branches
- **Feature Comparison**: "Compare features between docs and code" → Detailed feature diff
- **General Queries**: "What is this project about?" → AI-synthesized response
- **Code Search**: "Find documentation about the API" → Relevant results from GitHub

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for LLM access | ✅ |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | GitHub personal access token | ✅ |
| `GITHUB_TOOLSETS` | GitHub toolsets (default: repos) | ✅ |
| `GITHUB_REPO` | GitHub repository in `owner/repo` format | ✅ |
| `GITHUB_DEFAULT_REF` | Default branch (default: master) | ✅ |
| `NOTION_TOKEN` | Notion integration token | ✅ |
| `PORT` | Application port (default: 5000) | ❌ |
| `FLASK_ENV` | Flask environment (default: development) | ❌ |