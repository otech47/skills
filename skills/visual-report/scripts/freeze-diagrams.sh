#!/usr/bin/env bash
# Render every mermaid block in an HTML report to static inline SVG, then drop
# the mermaid runtime. You author diagrams in mermaid (fast, readable) and ship
# a small self-contained file with no javascript and no network dependency.
#
#   freeze-diagrams.sh report.src.html report.html
#
# Input: an HTML file with <pre class="mermaid"> blocks and mermaid loaded from
# a local file or CDN. Output: same page, diagrams baked to SVG, scripts removed.
#
# Why this exists: inlining mermaid.min.js makes a 20KB report weigh 3MB. The
# runtime is ~3.2MB and the rendered diagram is ~8KB, so freezing is ~400x smaller
# and cannot break offline or when the file is moved.
set -euo pipefail

SRC="${1:?usage: freeze-diagrams.sh <src.html> [out.html]}"
OUT="${2:-${SRC%.src.html}.html}"
[ "$OUT" = "$SRC" ] && OUT="${SRC%.html}.frozen.html"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || CHROME="$(command -v chromium || command -v google-chrome || true)"
if [ -z "${CHROME:-}" ] || [ ! -x "$CHROME" ]; then
  echo "no chrome/chromium found; hand-author the SVG instead (see references/information-hierarchy.md)" >&2
  exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Let the page run so mermaid replaces each block with rendered <svg>.
"$CHROME" --headless --disable-gpu --virtual-time-budget=15000 \
  --dump-dom "file://$(cd "$(dirname "$SRC")" && pwd)/$(basename "$SRC")" \
  2>/dev/null > "$TMP/dumped.html"

python3 - "$TMP/dumped.html" "$OUT" <<'PY'
import re, sys, pathlib

dumped, out = sys.argv[1], sys.argv[2]
s = pathlib.Path(dumped).read_text(encoding="utf-8", errors="replace")

before = len(s)
# Drop every script block; the diagrams are already baked into the DOM as SVG.
s = re.sub(r"<script\b[^>]*>.*?</script>", "", s, flags=re.S | re.I)
# Mermaid parks a hidden measurement sandbox in the body; it renders as dead space.
s = re.sub(r'<div[^>]*id="d?mermaid[^"]*"[^>]*>.*?</div>', "", s, flags=re.S | re.I)

svgs = len(re.findall(r"<svg", s, re.I))
pathlib.Path(out).write_text(s, encoding="utf-8")
print(f"froze {svgs} diagram(s): {before//1024}KB -> {len(s)//1024}KB  ->  {out}")
if re.search(r"<script", s, re.I):
    print("warning: a script tag survived, check the output", file=sys.stderr)
PY
