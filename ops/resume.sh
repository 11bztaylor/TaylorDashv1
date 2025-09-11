#!/usr/bin/env bash
set -euo pipefail
echo "== TaylorDash resume =="
docker compose up -d traefik mosquitto postgres victoriametrics minio keycloak backend frontend
echo "== Health =="
curl -k -f https://tracker.local/health/ready >/dev/null && echo "health: OK"
echo "== Metrics head =="
curl -k https://tracker.local/metrics | head -n 5 || true
echo "Open: https://tracker.local (Status/Canvas/Projects/Plugins)"