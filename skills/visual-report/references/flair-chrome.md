# Report flair: decorative chrome

This file is the whole mechanism, and it is optional. If you are reading it, flair is on for this report. If it has been renamed to `flair-chrome.md.off`, flair is off: skip this file entirely and build the report exactly as the rest of this skill describes, with no chrome.

**Toggle:** `report-flair on|off|status` (`~/.local/bin/report-flair`). Same rename-is-the-switch mechanism as `report-style`. Never edit this file to turn it off; rename it.

## What this is, and the one rule that bounds it

A corner badge, a corner mascot, a rolled accent hue, and one line of invented text in a colophon at the very bottom of the report. That is the entire scope. Everything here answers to one rule:

**It carries no information, so it can never be wrong, and it costs no vertical space, so it can never push the thesis, the hero diagram, or anything else down the page.**

Concretely:
- Fixed-position elements only (`position: fixed`), never inline in the document flow. They overlay the corner of the viewport; they do not occupy a row in the layout.
- No claim about the report's content, ever. The mascot has no name, no speech bubble, no opinion. The colophon phrase is disconnected filler, never a summary, a caption, or a reaction to anything in the report.
- The `--good` and `--warn` colors never roll. Only `--accent` and `--accent-soft` do. A warning that changed color between reports would stop meaning "warning."
- This whole step is independent of the report's content. Do it yourself, inline, right before or after writing the report. Do not spend a subagent call on it: the fixed overhead of spinning one up (system prompt, tool schemas) is larger than the few hundred tokens this step actually costs. Save the subagent pattern for flair heavy enough to be worth parallelizing; this is not that.

## Step 1: roll real values

Run `scripts/roll-flair.sh`. It prints `KEY=VALUE` lines, one per parameter, each pulled from the OS CSPRNG (`random.SystemRandom`), each bounded to a safe range, none of them a hash of the title and none of them picked from a fixed list. Use the numbers verbatim; do not hand-derive or round them further, and do not reuse a prior report's roll.

## Step 2: splice this into the report

Add to the `<style>` block, inside `:root` and its dark-mode block, replacing the plain `--accent` / `--accent-soft` lines:

```css
/* light */
--accent: hsl(HUE 60% 52%);
--accent-soft: hsl(HUE 75% 95%);
/* inside @media (prefers-color-scheme: dark) */
--accent: hsl(HUE 85% 78%);
--accent-soft: hsl(HUE 40% 20%);
```

Add these rules, once, anywhere in `<style>`:

```css
.corner-badge, .corner-mascot { position: fixed; pointer-events: none; z-index: 5; filter: drop-shadow(0 2px 6px rgba(0,0,0,.18)); }
.corner-badge { top: 14px; right: 14px; width: 40px; height: 40px; }
.corner-mascot { bottom: 14px; right: 14px; width: 44px; height: 44px; animation: bob BOB_DURs ease-in-out infinite; }
.badge-ring { animation: spin BADGE_SPIN_DURs linear infinite BADGE_SPIN_DIR; transform-origin: center; }
.badge-dot { animation: pulse BADGE_PULSEs ease-in-out infinite; transform-origin: center; }
.corner-mascot .eye { animation: blink BLINK_DURs infinite; transform-origin: center; }
.corner-mascot .eye.e2 { animation-delay: BLINK_DELAYs; }
@keyframes blink { 0%, 92%, 100% { transform: scaleY(1); } 95% { transform: scaleY(.1); } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: .55; transform: scale(.82); } }
@keyframes bob { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-BOB_AMPpx); } }
.colophon { display: flex; flex-direction: column; align-items: center; gap: .4rem; margin: 2.6rem 0 0; opacity: .8; }
.colophon .mark { color: var(--ink-faint); font-size: .78rem; font-style: italic; }
```

Add right after `<body>`, before `<main>`:

```html
<svg class="corner-badge" viewBox="0 0 40 40" role="presentation">
  <circle cx="20" cy="20" r="BADGE_RADIUS" class="node-accent"></circle>
  <g class="badge-ring" transform="rotate(BADGE_ROTATION 20 20)">
    <line x1="20" y1="2" x2="20" y2="8" class="edge" stroke-width="BADGE_STROKE" stroke-dasharray="BADGE_DASH"></line>
    <line x1="20" y1="32" x2="20" y2="38" class="edge" stroke-width="BADGE_STROKE" stroke-dasharray="BADGE_DASH"></line>
    <line x1="2" y1="20" x2="8" y2="20" class="edge" stroke-width="BADGE_STROKE" stroke-dasharray="BADGE_DASH"></line>
    <line x1="32" y1="20" x2="38" y2="20" class="edge" stroke-width="BADGE_STROKE" stroke-dasharray="BADGE_DASH"></line>
  </g>
  <circle class="badge-dot" cx="20" cy="20" r="BADGE_DOT" style="fill:var(--accent)"></circle>
</svg>

<svg class="corner-mascot" viewBox="0 0 44 44" role="presentation">
  <ellipse cx="22" cy="24" rx="MASC_RX" ry="MASC_RY" class="node-accent"></ellipse>
  <ellipse class="eye e1" cx="EYE_CX1" cy="EYE_DY" rx="EYE_R" ry="EYE_R" style="fill:var(--ink)"></ellipse>
  <ellipse class="eye e2" cx="EYE_CX2" cy="EYE_DY" rx="EYE_R" ry="EYE_R" style="fill:var(--ink)"></ellipse>
  <path d="M14,31 Q22,MOUTH_Y 30,31" class="edge"></path>
</svg>
```

`EYE_CX1` is `22 - EYE_DX`, `EYE_CX2` is `22 + EYE_DX`; compute those two once, they are the only derived values in the whole snippet.

Add the favicon to `<head>`, with the same hue:

```html
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='14' fill='hsl(HUE,60%25,52%25)'/%3E%3Ccircle cx='16' cy='16' r='5' fill='white'/%3E%3C/svg%3E">
```

Add right after the closing `</main>` tag (nothing sits below it, so it costs no space above it either):

```html
<div class="colophon">
  <svg width="20" height="20" viewBox="0 0 20 20"><rect x="3" y="3" width="14" height="14" rx="3" transform="rotate(45 10 10)" class="node-accent"></rect></svg>
  <span class="mark">YOUR PHRASE HERE</span>
</div>
```

## Step 3: the one thing you write yourself

Replace `YOUR PHRASE HERE` with three to six words you invent in the moment. It has no connection to the report's subject and makes no claim about anything, so it cannot be wrong. Don't pick it from a mental list of stock phrases and don't reuse one from a previous report; that is what makes it flair instead of a template string. This is the one piece of the mechanism that is genuinely nondeterministic rather than randomized: the numbers came from `roll-flair.sh`, this line comes from you, fresh, every time.

## What this is not

Not a diagram style, not a background texture, not a headline typeface. Selecting from a small named set of those is exactly the kind of thing a reader learns to pattern-match after three reports, which defeats the point. If a future version of this reference adds either, it has to vary on continuous, combinatorial parameters the way the badge and mascot already do, not a pick from a short list.
