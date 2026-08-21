#!/usr/bin/env bash
# Rolls and applies one report's decorative chrome (report-flair).
#
#   roll-flair.sh --apply <report.html>    roll and splice into the report
#   roll-flair.sh --strip <report.html>    remove it again
#   roll-flair.sh                          print the blocks without touching a file
#
# --apply is idempotent: it strips any previous flair before adding new.
set -euo pipefail

command -v python3 >/dev/null 2>&1 || { echo "roll-flair: python3 not found" >&2; exit 1; }
exec python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/roll-flair.py" "$@"
