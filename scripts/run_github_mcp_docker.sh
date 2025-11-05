#!/usr/bin/env bash
set -euo pipefail
# Run the official MCP server via Docker with PAT + toolsets.  :contentReference[oaicite:13]{index=13}
if [[ -z "${GITHUB_PERSONAL_ACCESS_TOKEN:-}" ]]; then
  echo "Set GITHUB_PERSONAL_ACCESS_TOKEN first"; exit 1
fi
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN="${GITHUB_PERSONAL_ACCESS_TOKEN}" \
  -e GITHUB_TOOLSETS="${GITHUB_TOOLSETS:-repos}" \
  ghcr.io/github/github-mcp-server
