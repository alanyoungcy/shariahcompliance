#!/usr/bin/env bash
# Stop the complete local Shariah Compliance Copilot stack without deleting its database volume.
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose is required to stop the local services." >&2
  exit 1
fi

echo "Stopping Shariah Compliance Copilot…"
docker compose down --remove-orphans
echo "Stopped. The local database volume was kept."
