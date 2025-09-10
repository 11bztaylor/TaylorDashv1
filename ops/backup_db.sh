#!/usr/bin/env bash
set -euo pipefail
# Docker-aware PostgreSQL backup to MinIO with versioning
# Usage: ./ops/backup_db.sh [database_name]

DATABASE="${1:-taylordash}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
GIT_TAG=$(git describe --tags --exact-match HEAD 2>/dev/null || echo "untagged")
BACKUP_KEY="db-backups/${GIT_TAG}_${TIMESTAMP}.dump"

echo "=== TaylorDash Database Backup ==="
echo "Database: $DATABASE"
echo "Timestamp: $TIMESTAMP"  
echo "Git Tag: $GIT_TAG"
echo "MinIO Key: $BACKUP_KEY"
echo

# Check if running in Docker environment
if docker compose ps postgres >/dev/null 2>&1; then
  echo "Using Docker Compose PostgreSQL container..."
  BACKUP_CMD="docker compose exec -T postgres pg_dump -U postgres -d $DATABASE -Fc"
else
  echo "Using local PostgreSQL..."
  BACKUP_CMD="pg_dump -h localhost -U postgres -d $DATABASE -Fc"
fi

# Create backup and stream to MinIO
echo "Creating logical backup..."
TEMP_FILE="/tmp/backup_${TIMESTAMP}.dump"

$BACKUP_CMD > "$TEMP_FILE"

echo "Uploading to MinIO..."
if command -v mc >/dev/null 2>&1; then
  # Upload to MinIO and capture version ID
  mc cp "$TEMP_FILE" "taylordash/$BACKUP_KEY"
  
  # Get the version ID of the uploaded object
  VERSION_ID=$(mc stat "taylordash/$BACKUP_KEY" --json | jq -r '.versionID // "N/A"')
  
  echo "✅ Backup complete!"
  echo "   MinIO Path: taylordash/$BACKUP_KEY"
  echo "   Version ID: $VERSION_ID"
  echo "   Local Size: $(du -h "$TEMP_FILE" | cut -f1)"
else
  echo "WARNING: mc command not found. Backup saved locally only."
  echo "   Local File: $TEMP_FILE"
fi

# Generate checksum
echo "Generating SHA256 checksum..."
CHECKSUM=$(sha256sum "$TEMP_FILE" | cut -d' ' -f1)
echo "   SHA256: $CHECKSUM"

# Clean up temp file unless mc failed
if command -v mc >/dev/null 2>&1; then
  rm -f "$TEMP_FILE"
  echo "   Temporary file cleaned up"
else
  echo "   Temporary file preserved: $TEMP_FILE"
fi

echo
echo "Restore command:"
echo "  pg_restore -h localhost -U postgres -d ${DATABASE}_restored /path/to/backup.dump"