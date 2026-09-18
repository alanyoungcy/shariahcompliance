#!/usr/bin/env bash
# Start the complete local Shariah Compliance Copilot stack.
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Install and start Docker Desktop, then run this script again." >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose is required. Start Docker Desktop, then run this script again." >&2
  exit 1
fi

echo "Starting Shariah Compliance Copilot…"
docker compose up -d --build --remove-orphans

printf "Waiting for the API"
for _ in $(seq 1 60); do
  if curl --fail --silent http://127.0.0.1:8000/health >/dev/null; then
    printf " ready\n\n"
    echo "Open the demo: http://127.0.0.1:5173"
    echo "Stop it later: ./scripts/stop.sh"
    exit 0
  fi
  printf "."
  sleep 1
done

printf "\nThe services started but the API did not become ready in 60 seconds.\n" >&2
docker compose ps >&2
echo "Inspect logs with: docker compose logs --tail=100 api" >&2
exit 1
