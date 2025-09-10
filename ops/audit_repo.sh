#!/usr/bin/env bash
set -euo pipefail
need=(
  ".github/pull_request_template.md"
  ".github/ISSUE_TEMPLATE/bug_report.md"
  ".github/ISSUE_TEMPLATE/feature_request.md"
  ".github/ISSUE_TEMPLATE/config.yml"
  "CONTRIBUTING.md"
  "CODEOWNERS"
  "CHANGELOG.md"
  "docs/ops/versioning.md"
  "docs/specs/ui/midnight-hud.md"
  "examples/midnight-hud/package.json"
  "frontend/src/plugins/registry.ts"
)
missing=0
for f in "${need[@]}"; do
  [[ -e "$f" ]] || { echo "MISSING: $f"; missing=1; }
done
[[ $missing -eq 0 ]] && echo "✅ Repo has required files" || { echo "❌ Repo is missing required files"; exit 1; }