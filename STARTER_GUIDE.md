# MCP Agent - Starter Guide

This guide walks you through setting up, running, and testing the MCP Agent application.

## Features

- **LLM-Powered Tool Selection**: Intelligent tool selection based on tool descriptions and JSON schemas
- **Direct Tool Execution**: Commit count queries return direct answers ("The repository has 3 commits")
- **Feature Comparison**: Compare features between Notion documentation and GitHub code
- **Multi-Source Synthesis**: AI synthesizes responses using data from both Notion and GitHub
- **Docker Support**: Run the application in Docker containers
- **Comprehensive Testing**: Full test suite for all components

## Prerequisites

1. **Python 3.8+** installed
2. **Docker Desktop** installed and running
3. **Node.js and npm** installed (for Notion MCP server)
4. **API Keys**:
   - OpenAI API Key
   - GitHub Personal Access Token
   - Notion Integration Token

## Step 1: Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```env
   # --- LLMs ---
   OPENAI_API_KEY=sk-...
   
   # --- GitHub MCP ---
   GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...
   GITHUB_TOOLSETS=repos
   GITHUB_REPO=owner/repo
   GITHUB_DEFAULT_REF=master
   
   # --- Notion MCP ---
   NOTION_TOKEN=secret_...
   
   # --- Flask ---
   PORT=5000
   FLASK_ENV=development
   ```

## Step 2: Run the Application

### Option A: Single-Command Docker Execution (Recommended)
```bash
# Linux/macOS
./run_with_docker.sh

# Windows
run_with_docker.bat
```

This will:
1. Automatically build the Docker image
2. Start the container with all required environment variables
3. Expose the application on `http://localhost:5000`

### Option B: Manual Docker Execution
1. Build the Docker image:
   ```bash
   docker build -t mcp-agent .
   ```

2. Run the container:
   ```bash
   docker run -it --rm \
     -p 5000:8080 \
     --env-file .env \
     mcp-agent
   ```

### Option C: Direct Python Execution
```bash
pip install -r requirements.txt
python app.py
```

The application will start on `http://localhost:5000`

## Step 3: Test the Application

### Health Check
```bash
curl http://localhost:5000/healthz
```

Expected response:
```json
{"ok": true}
```

### Query Endpoint
```bash
curl "http://localhost:5000/agent?query=medical%20chatbot"
```

### Feature Comparison
```bash
curl "http://localhost:5000/agent?query=compare%20features%20between%20docs%20and%20code"
```

### Commit Information
```bash
curl "http://localhost:5000/agent?query=how%20many%20commits%20are%20in%20the%20repository"
```

## Step 4: Run Tests

```bash
python -m pytest tests/
```

Or use the test runner:
```bash
python run_tests.py
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

## Example Queries

- **Commit Information**: "How many commits are in the repository?" → "The repository has 3 commits."
- **Branch Information**: "What branches are in the repo?" → List of branches
- **Feature Comparison**: "Compare features between docs and code" → Detailed feature diff
- **General Queries**: "What is this project about?" → AI-synthesized response
- **Code Search**: "Find documentation about the API" → Relevant results from GitHub

## Troubleshooting

### Docker Issues
- Ensure Docker Desktop is running
- Check that all environment variables are set in your `.env` file
- Verify the GitHub MCP server binary is included in the Docker image

### GitHub Integration
- Ensure `GITHUB_REPO` is in `owner/repo` format
- Check that `GITHUB_DEFAULT_REF` matches your repository's default branch
- Verify your GitHub token has appropriate permissions

### Notion Integration
- Ensure your Notion token is valid
- Verify the Notion integration has access to your pages

## API Endpoints

- `GET /healthz` - Health check endpoint
- `GET /agent` - Main query endpoint
  - Parameters:
    - `query` (required) - The query string

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