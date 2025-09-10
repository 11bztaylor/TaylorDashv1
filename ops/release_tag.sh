#!/usr/bin/env bash
set -euo pipefail
# Creates semantic version tags with changelog skeleton
# Usage: ./ops/release_tag.sh [major|minor|patch] [description]

BUMP_TYPE="${1:-patch}"
DESCRIPTION="${2:-}"

if [[ ! "$BUMP_TYPE" =~ ^(major|minor|patch)$ ]]; then
  echo "Usage: $0 [major|minor|patch] [description]"
  echo "Example: $0 minor 'MQTT implementation complete'"
  exit 1
fi

echo "=== TaylorDash Release Tagging ==="

# Get current version (latest tag)
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
echo "Current version: $CURRENT_VERSION"

# Parse semantic version
if [[ $CURRENT_VERSION =~ ^v([0-9]+)\.([0-9]+)\.([0-9]+) ]]; then
  MAJOR=${BASH_REMATCH[1]}
  MINOR=${BASH_REMATCH[2]}
  PATCH=${BASH_REMATCH[3]}
else
  echo "WARNING: Current tag '$CURRENT_VERSION' is not semantic version"
  MAJOR=0
  MINOR=0
  PATCH=0
fi

# Calculate new version
case $BUMP_TYPE in
  major)
    NEW_MAJOR=$((MAJOR + 1))
    NEW_MINOR=0
    NEW_PATCH=0
    ;;
  minor)
    NEW_MAJOR=$MAJOR
    NEW_MINOR=$((MINOR + 1))
    NEW_PATCH=0
    ;;
  patch)
    NEW_MAJOR=$MAJOR
    NEW_MINOR=$MINOR
    NEW_PATCH=$((PATCH + 1))
    ;;
esac

NEW_VERSION="v${NEW_MAJOR}.${NEW_MINOR}.${NEW_PATCH}"
echo "New version: $NEW_VERSION"

# Get commits since last tag
COMMITS_SINCE_TAG=$(git log ${CURRENT_VERSION}..HEAD --oneline 2>/dev/null || git log --oneline)

# Generate changelog skeleton
CHANGELOG_MSG="Release $NEW_VERSION"
if [ -n "$DESCRIPTION" ]; then
  CHANGELOG_MSG="$CHANGELOG_MSG - $DESCRIPTION"
fi

CHANGELOG_MSG="$CHANGELOG_MSG

## Changes since $CURRENT_VERSION

### Features
$(echo "$COMMITS_SINCE_TAG" | grep "^[a-f0-9]* feat" || echo "- No new features")

### Fixes  
$(echo "$COMMITS_SINCE_TAG" | grep "^[a-f0-9]* fix" || echo "- No bug fixes")

### Other
$(echo "$COMMITS_SINCE_TAG" | grep -v "^[a-f0-9]* \(feat\|fix\)" || echo "- No other changes")

## Validation
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Security scan clean
- [ ] Performance benchmarks met"

echo
echo "Generated changelog:"
echo "=================="
echo "$CHANGELOG_MSG"
echo "=================="
echo

# Confirm release
read -p "Create release $NEW_VERSION? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 1
fi

# Run validation
echo "Running validation..."
if [ -x "./ops/validate_p1.sh" ]; then
  ./ops/validate_p1.sh
else
  echo "WARNING: validate_p1.sh not found"
fi

# Create signed tag
echo "Creating signed tag $NEW_VERSION..."
git tag -s "$NEW_VERSION" -m "$CHANGELOG_MSG" || {
  echo "ERROR: Failed to create signed tag"
  exit 1
}

echo
echo "✅ Release tag created: $NEW_VERSION"
echo
echo "Next steps:"
echo "  1. Review tag: git show $NEW_VERSION"
echo "  2. Push tag: git push origin $NEW_VERSION"
echo "  3. Create GitHub release from tag"
echo "  4. Update documentation with new version"