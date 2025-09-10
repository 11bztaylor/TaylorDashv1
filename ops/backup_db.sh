#!/usr/bin/env bash
set -euo pipefail
TAG="${1:-manual}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="pg-${TAG}-${TS}.dump"
docker compose exec -T postgres pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc > "$OUT"
SHA="$(sha256sum "$OUT" | awk '{print $1}')"
# Upload to MinIO (requires mc alias configured once by operator)
mc cp "$OUT" local/backups/db/
echo "DB_BACKUP=$OUT SHA256=$SHA"