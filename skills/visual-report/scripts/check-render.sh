#!/usr/bin/env bash
# Render a report wide and narrow, measure its layout, and flag the defects that
# actually ship. Look at the screenshots afterwards; the numbers alone will not
# tell you whether the first screen orients a stranger.
#
#   check-render.sh report.html
#
# Prints a verdict plus two screenshot paths to open.
set -euo pipefail

SRC="${1:?usage: check-render.sh <report.html>}"
[ -f "$SRC" ] || { echo "no such file: $SRC" >&2; exit 1; }
ABS="$(cd "$(dirname "$SRC")" && pwd)/$(basename "$SRC")"
OUTDIR="$(dirname "$ABS")"
BASE="$(basename "${SRC%.html}")"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || CHROME="$(command -v chromium || command -v google-chrome || true)"
[ -n "${CHROME:-}" ] && [ -x "$CHROME" ] || { echo "no chrome found" >&2; exit 1; }

KB=$(( $(wc -c < "$ABS") / 1024 ))
echo "size: ${KB}KB"
if [ "$KB" -gt 150 ]; then
  echo "  FAIL: over 150KB. Almost always an inlined js library."
  echo "        Author diagrams in mermaid and run scripts/freeze-diagrams.sh instead."
fi
if grep -qiE "<script[^>]*src=|https?://[^\"')]*\.(js|css)" "$ABS"; then
  echo "  FAIL: external asset reference. Inline it, the report must open offline."
fi
if grep -q "MERMAID-LIB-HERE\|MERMAID_PLACEHOLDER" "$ABS"; then
  echo "  FAIL: unresolved build placeholder. Diagrams will throw and dump raw source."
fi
if LC_ALL=C grep -qF -e $'\xe2\x80\x94' -e $'\xe2\x80\x93' "$ABS"; then
  echo "  FAIL: em or en dash present. Use a plain hyphen."
fi

# Measure layout: does the page scroll sideways, and does the hero diagram hold
# its size (good, it scrolls in its own box) or shrink to unreadable (bad)?
PROBE="$(mktemp -d)/probe.html"
python3 - "$ABS" "$PROBE" <<'PY'
import pathlib, sys
src, dst = sys.argv[1], sys.argv[2]
js = """<script>addEventListener('load',function(){
 var s=document.querySelector('.hero svg'), h=document.querySelector('.hero');
 var d=document.createElement('div'); d.id='PROBE';
 d.textContent=[document.documentElement.clientWidth,
   document.documentElement.scrollWidth,
   s?Math.round(s.getBoundingClientRect().width):0,
   h?h.scrollWidth:0, h?h.clientWidth:0].join(' ');
 document.body.appendChild(d);});</script>"""
t = pathlib.Path(src).read_text(encoding="utf-8", errors="replace")
pathlib.Path(dst).write_text(t.replace("</body>", js + "</body>"), encoding="utf-8")
PY

read -r VIEW PAGE SVGW HSCROLL HCLIENT < <(
  "$CHROME" --headless=new --disable-gpu --window-size=500,900 --virtual-time-budget=4000 \
    --dump-dom "file://$PROBE" 2>/dev/null |
  python3 -c "import re,sys; m=re.search(r'id=\"PROBE\">([^<]*)',sys.stdin.read()); print(m.group(1) if m else '0 0 0 0 0')"
)

echo "narrow layout (${VIEW}px viewport):"
if [ "${PAGE:-0}" -gt "${VIEW:-0}" ]; then
  echo "  FAIL: page body scrolls sideways (${PAGE} > ${VIEW}). Wide content must scroll in its own box."
else
  echo "  ok: page body does not scroll sideways"
fi
if [ "${SVGW:-0}" -gt 0 ]; then
  if [ "${SVGW}" -lt "${VIEW}" ]; then
    echo "  WARN: hero diagram shrank to ${SVGW}px. Labels scale down with it and become unreadable."
    echo "        Give the svg a min-width so .hero scrolls instead of the art shrinking."
  else
    echo "  ok: hero diagram holds ${SVGW}px and scrolls in its box"
  fi
else
  echo "  note: no .hero svg found (fine if the mental model is html/css rather than svg)"
fi

for spec in "wide 820x2000" "narrow 500x1200"; do
  set -- $spec
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --window-size="${2/x/,}" --screenshot="$OUTDIR/$BASE.$1.png" "file://$ABS" 2>/dev/null
done
echo "screenshots (read both, check the first screen orients a stranger):"
echo "  $OUTDIR/$BASE.wide.png"
echo "  $OUTDIR/$BASE.narrow.png"
