#!/usr/bin/env bash
set -euo pipefail
# VictoriaMetrics backup to MinIO using vmbackup
# Usage: ./ops/backup_vm.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
GIT_TAG=$(git describe --tags --exact-match HEAD 2>/dev/null || echo "untagged")
BACKUP_PATH="vm-backups/${GIT_TAG}_${TIMESTAMP}"
VM_DATA_PATH="/var/lib/victoria-metrics"

echo "=== TaylorDash VictoriaMetrics Backup ==="
echo "Timestamp: $TIMESTAMP"
echo "Git Tag: $GIT_TAG"
echo "Backup Path: $BACKUP_PATH"
echo

# Check if running in Docker environment
if docker compose ps victoriametrics >/dev/null 2>&1; then
  echo "Using Docker Compose VictoriaMetrics container..."
  
  # Create snapshot first
  echo "Creating VM snapshot..."
  SNAPSHOT_NAME=$(docker compose exec -T victoriametrics curl -s -X POST "http://localhost:8428/snapshot/create" | jq -r '.snapshot')
  echo "   Snapshot: $SNAPSHOT_NAME"
  
  # Use vmbackup from container
  VM_BACKUP_CMD="docker compose exec -T victoriametrics vmbackup"
  VM_DATA_PATH="/victoria-metrics-data"
else
  echo "Using local VictoriaMetrics..."
  
  # Create snapshot via API
  echo "Creating VM snapshot..."
  SNAPSHOT_NAME=$(curl -s -X POST "http://localhost:8428/snapshot/create" | jq -r '.snapshot')
  echo "   Snapshot: $SNAPSHOT_NAME"
  
  VM_BACKUP_CMD="vmbackup"
fi

# Construct MinIO S3 URL
MINIO_ENDPOINT="s3://minio:9000/taylordash/${BACKUP_PATH}"

# Get MinIO credentials from environment or Docker secrets
if [ -f "/run/secrets/minio_root_user" ]; then
  MINIO_USER=$(cat /run/secrets/minio_root_user)
  MINIO_PASS=$(cat /run/secrets/minio_root_password)
elif [ -n "${MINIO_ROOT_USER:-}" ]; then
  MINIO_USER="$MINIO_ROOT_USER"
  MINIO_PASS="$MINIO_ROOT_PASSWORD"
else
  echo "ERROR: MinIO credentials not found in environment or Docker secrets"
  exit 1
fi

echo "Running vmbackup to MinIO..."
$VM_BACKUP_CMD \
  -storageDataPath="$VM_DATA_PATH" \
  -dst="$MINIO_ENDPOINT" \
  -s3.accessKey="$MINIO_USER" \
  -s3.secretKey="$MINIO_PASS" \
  -snapshot="$SNAPSHOT_NAME"

echo "✅ VictoriaMetrics backup complete!"
echo "   MinIO Path: taylordash/$BACKUP_PATH"
echo "   Snapshot Used: $SNAPSHOT_NAME"

# Clean up snapshot
echo "Cleaning up snapshot..."
if docker compose ps victoriametrics >/dev/null 2>&1; then
  docker compose exec -T victoriametrics curl -s -X POST "http://localhost:8428/snapshot/delete?snapshot=$SNAPSHOT_NAME"
else
  curl -s -X POST "http://localhost:8428/snapshot/delete?snapshot=$SNAPSHOT_NAME"
fi

echo
echo "Restore command:"
echo "  vmrestore -src=\"s3://minio:9000/taylordash/${BACKUP_PATH}\" \\"
echo "    -storageDataPath=\"/path/to/restored/data\" \\"
echo "    -s3.accessKey=\"\$MINIO_ROOT_USER\" \\"
echo "    -s3.secretKey=\"\$MINIO_ROOT_PASSWORD\""