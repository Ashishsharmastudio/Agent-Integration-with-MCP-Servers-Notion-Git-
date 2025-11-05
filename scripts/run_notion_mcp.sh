#!/usr/bin/env bash
set -euo pipefail
# Uses official Notion MCP via npx; requires NOTION_TOKEN.  :contentReference[oaicite:14]{index=14}
if [[ -z "${NOTION_TOKEN:-}" ]]; then
  echo "Set NOTION_TOKEN first"; exit 1
fi
exec npx -y @notionhq/notion-mcp-server
