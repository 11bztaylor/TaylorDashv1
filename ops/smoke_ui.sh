#!/usr/bin/env bash
set -euo pipefail
curl -k -I https://tracker.local/health/ready | head -n 1
curl -k -s -o /dev/null -w "%{http_code}\n" https://tracker.local/api/v1/projects || true
curl -k -I https://tracker.local/plugins/midnight-hud | head -n 1 || true