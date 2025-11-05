# Dockerfile
FROM python:3.11-slim

# Install Node for Notion MCP server (npx)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs npm git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Optional: prefetch Notion server package for speed
RUN npm install -g @notionhq/notion-mcp-server

# Download and install GitHub MCP server binary
RUN curl -L https://github.com/github/github-mcp-server/releases/download/v0.20.1/github-mcp-server_Linux_x86_64.tar.gz -o github-mcp-server.tar.gz && \
    tar -xzf github-mcp-server.tar.gz && \
    mv github-mcp-server /usr/local/bin/ && \
    chmod +x /usr/local/bin/github-mcp-server && \
    rm github-mcp-server.tar.gz

COPY . .

ENV PYTHONUNBUFFERED=1 \
    GUNICORN_CMD_ARGS="--bind=0.0.0.0:8080 --workers=2 --timeout=120" \
    GITHUB_MCP_COMMAND=github-mcp-server \
    GITHUB_MCP_ARGS=stdio

EXPOSE 8080

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]