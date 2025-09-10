#!/usr/bin/env bash
set -euo pipefail
# Creates a signed tag and pushes only when validation passes.
# Usage: ./ops/backup_git.sh v0.1.0 "checkpoint: naming the backup"

TAG="${1:-}"
MSG="${2:-"TaylorDash checkpoint"}"

if [ -z "$TAG" ]; then
  echo "Usage: $0 <tag> [message]"
  echo "Example: $0 v0.1.0 'checkpoint: MQTT implementation complete'"
  exit 1
fi

echo "=== TaylorDash Git Backup ==="
echo "Tag: $TAG"
echo "Message: $MSG"
echo

# Run local validation before any push
echo "Running validation..."
if [ -x "./ops/validate_p1.sh" ]; then
  ./ops/validate_p1.sh
else
  echo "WARNING: validate_p1.sh not found or not executable"
  read -p "Continue without validation? (y/N): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
  fi
fi

echo
echo "Fetching latest from origin..."
git fetch origin

echo "Creating signed tag..."
git tag -s "$TAG" -m "$MSG" || { 
  echo "ERROR: Signing/tag failed."
  echo "Make sure you have signing configured:"
  echo "  git config --global commit.gpgsign true"
  echo "  git config --global user.signingkey YOUR_KEY"
  exit 1
}

echo "Pushing changes to origin..."
git push origin HEAD:main

echo "Pushing tag to origin..."
git push origin "$TAG"

echo
echo "✅ Backup complete!"
echo "   - Pushed HEAD to main"
echo "   - Pushed signed tag: $TAG"
echo "   - Message: $MSG"
echo
echo "Verify with:"
echo "  git tag -v $TAG"
echo "  git ls-remote --tags origin | grep $TAG"