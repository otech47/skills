#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if ! command -v node >/dev/null 2>&1; then
  echo 'ERROR: node 20 or newer is required' >&2
  exit 2
fi
exec node "$SCRIPT_DIR/check-render.cjs" "$@"
