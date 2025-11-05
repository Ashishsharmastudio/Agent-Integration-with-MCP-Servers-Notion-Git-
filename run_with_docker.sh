#!/bin/bash

# Script to build and run the MCP Agent with Docker

# Check if Docker is installed
if ! command -v docker &> /dev/null
then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null
then
    echo "❌ Docker daemon is not running. Please start Docker Desktop or Docker daemon."
    exit 1
fi

echo "🐳 Building MCP Agent Docker image..."
docker build -t mcp-agent .

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one with your API keys."
    echo "   You can copy .env.example to .env and fill in your values."
fi

echo "🚀 Running MCP Agent container..."
echo "   Make sure your .env file contains all required environment variables:"
echo "   - OPENAI_API_KEY"
echo "   - GITHUB_PERSONAL_ACCESS_TOKEN"
echo "   - GITHUB_REPO (in owner/repo format)"
echo "   - NOTION_TOKEN"

docker run -it --rm \
  -p 5000:8080 \
  --env-file .env \
  mcp-agent

echo "✅ Container stopped"