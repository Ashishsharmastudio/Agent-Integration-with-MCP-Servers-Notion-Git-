@echo off
REM Script to build and run the MCP Agent with Docker on Windows

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

echo 🐳 Building MCP Agent Docker image...
docker build -t mcp-agent .

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Please create one with your API keys.
    echo    You can copy .env.example to .env and fill in your values.
)

echo 🚀 Running MCP Agent container...
echo    Make sure your .env file contains all required environment variables:
echo    - OPENAI_API_KEY
echo    - GITHUB_PERSONAL_ACCESS_TOKEN
echo    - GITHUB_REPO (in owner/repo format)
echo    - NOTION_TOKEN

docker run -it --rm ^
  -p 5000:8080 ^
  --env-file .env ^
  mcp-agent

echo ✅ Container stopped