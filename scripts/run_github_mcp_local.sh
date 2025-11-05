#!/usr/bin/env bash
set -euo pipefail
# Requires github-mcp-server binary on PATH.  :contentReference[oaicite:12]{index=12}
if [[ -z "${GITHUB_PERSONAL_ACCESS_TOKEN:-}" ]]; then
  echo "Set GITHUB_PERSONAL_ACCESS_TOKEN first"; exit 1
fi
: "${GITHUB_TOOLSETS:=repos}"
exec github-mcp-server stdio
