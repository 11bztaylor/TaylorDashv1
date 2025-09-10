#!/usr/bin/env bash
set -euo pipefail
TAG="${1:-manual}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
# Adjust paths to match your compose service name and storage path if needed
docker compose exec -T victoriametrics /usr/local/bin/vmbackup \
  -storageDataPath=/storage \
  -snapshot.createURL=http://localhost:8428/snapshot/create \
  -dst=s3://local/backups/vm/${TAG}-${TS}
echo "VM_BACKUP_S3=local/backups/vm/${TAG}-${TS}"