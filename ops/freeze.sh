#!/usr/bin/env bash
set -euo pipefail
TS="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p state/freeze
{
  echo "{"
  echo "  \"timestamp\":\"$TS\","
  echo "  \"git_rev\":\"$(git rev-parse HEAD 2>/dev/null || echo unknown)\","
  echo "  \"compose_sha256\":\"$(sha256sum docker-compose.yml | awk '{print $1}')\","
  echo "  \"images\": ["
  docker compose images --format json 2>/dev/null || echo ""
  echo "  ]"
  echo "}"
} > "state/freeze/$TS.json"
echo "Wrote state/freeze/$TS.json"