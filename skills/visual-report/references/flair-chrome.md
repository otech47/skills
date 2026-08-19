# Report flair: decorative chrome

This file is the whole mechanism, and it is optional. If you are reading it, flair is on for this report. If it has been renamed to `flair-chrome.md.off`, flair is off. Skip this file entirely and build the report exactly as the rest of this skill describes, with no chrome.

**Toggle:** `report-flair on|off|status` (`~/.local/bin/report-flair`). Same rename-is-the-switch mechanism as `report-style`. Never edit this file to turn it off. Rename it instead.

## What this is, and the one rule that bounds it

One corner ornament (a ring, a pulsing gem, three twinkling sparks), a rolled accent hue, and one off-by-one quote in a colophon at the very bottom of the report. That is the entire scope. Everything here answers to one rule:

**It carries no information, so it can never be wrong, and it costs no vertical space, so it can never push the thesis, the hero diagram, or anything else down the page.**

Concretely:
- Absolutely positioned, anchored near the top of the page. Not `position: fixed`. It scrolls away with the rest of the page instead of staying pinned to the viewport, and it never occupies a row in the layout.
- No face, no eyes, no anthropomorphism. A ring, a gem, and three sparks, so there is nothing on the page that could be misread as a name, an opinion, or a reaction to anything.
- The colophon quote is a joke, not a citation. The italic quote next to a real name already signals a riff, so it needs no hedge word to say so.
- The `--good` and `--warn` colors never roll. Only `--accent` and `--accent-soft` do. A warning that changed color between reports would stop meaning "warning."
- This whole step is independent of the report's content. Do it yourself, inline, right before or after writing the report. Do not spend a subagent call on it. The fixed overhead of spinning one up (system prompt, tool schemas) is larger than the few hundred tokens this step actually costs. Save the subagent pattern for flair heavy enough to be worth parallelizing. This is not that.

## Step 1: roll real values

Run `scripts/roll-flair.sh`. It prints `KEY=VALUE` lines, one per parameter, each pulled from the OS CSPRNG (`random.SystemRandom`), each bounded to a safe range, none of them a hash of the title and none of them picked from a fixed list. Use the numbers verbatim. Do not hand-derive or round them further, and do not reuse a prior report's roll.

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
.flair-mark { position: absolute; top: 14px; right: 14px; width: 48px; height: 48px; pointer-events: none; animation: flbob BOB_DURs ease-in-out infinite; filter: drop-shadow(0 2px 6px rgba(0,0,0,.18)); }
.flair-ring { animation: flspin RING_SPIN_DURs linear infinite RING_SPIN_DIR; transform-origin: center; }
.flair-gem { animation: flpulse GEM_PULSE_DURs ease-in-out infinite; transform-origin: center; }
.flair-spark { animation-name: fltwinkle; animation-timing-function: ease-in-out; animation-iteration-count: infinite; transform-origin: center; }
@keyframes flspin { to { transform: rotate(360deg); } }
@keyframes flpulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: .6; transform: scale(.85); } }
@keyframes fltwinkle { 0%, 100% { opacity: .15; transform: scale(.7); } 50% { opacity: 1; transform: scale(1.15); } }
@keyframes flbob { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-BOB_AMPpx); } }
.colophon { display: flex; flex-direction: column; align-items: center; gap: .3rem; margin: 2.6rem 0 0; opacity: .8; text-align: center; }
.colophon .mark { color: var(--ink-soft); font-size: .85rem; font-style: italic; }
.colophon .attrib { color: var(--ink-faint); font-size: .75rem; }
```

Add right after `<body>`, before `<main>`. The four values inside each `.flair-spark` `style` attribute are the only place the per-spark timing goes:

```html
<svg class="flair-mark" viewBox="0 0 48 48" role="presentation">
  <g class="flair-ring">
    <circle cx="24" cy="24" r="15" fill="none" stroke="var(--accent)" stroke-width="RING_STROKE" stroke-dasharray="RING_DASH"></circle>
    <line x1="24" y1="3" x2="24" y2="8" stroke="var(--accent)" stroke-width="RING_STROKE"></line>
    <line x1="24" y1="40" x2="24" y2="45" stroke="var(--accent)" stroke-width="RING_STROKE"></line>
    <line x1="3" y1="24" x2="8" y2="24" stroke="var(--accent)" stroke-width="RING_STROKE"></line>
    <line x1="40" y1="24" x2="45" y2="24" stroke="var(--accent)" stroke-width="RING_STROKE"></line>
  </g>
  <rect class="flair-gem" x="GEM_X" y="GEM_X" width="GEM_WH" height="GEM_WH" rx="2" transform="rotate(45 24 24)" style="fill:var(--accent-soft); stroke:var(--accent); stroke-width:1.5"></rect>
  <g transform="rotate(SPARK_ROT 24 24)">
    <rect class="flair-spark" x="43" y="22" width="4" height="4" transform="rotate(45 45 24)" style="fill:var(--accent); animation-duration:SPARK1_DURs; animation-delay:SPARK1_DELAYs"></rect>
    <rect class="flair-spark" x="11.5" y="40.2" width="4" height="4" transform="rotate(45 13.5 42.2)" style="fill:var(--accent); animation-duration:SPARK2_DURs; animation-delay:SPARK2_DELAYs"></rect>
    <rect class="flair-spark" x="11.5" y="3.8" width="4" height="4" transform="rotate(45 13.5 5.8)" style="fill:var(--accent); animation-duration:SPARK3_DURs; animation-delay:SPARK3_DELAYs"></rect>
  </g>
</svg>
```

Every coordinate above is fixed on purpose, so there is no per-report geometry to derive by hand. Only the numbers already named `RING_*`, `GEM_*`, `SPARK*`, and `BOB_*` change.

Add the favicon to `<head>`, with the same hue:

```html
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='14' fill='hsl(HUE,60%25,52%25)'/%3E%3Ccircle cx='16' cy='16' r='5' fill='white'/%3E%3C/svg%3E">
```

Add right after the closing `</main>` tag. Nothing sits below it, so it costs no space above it either:

```html
<div class="colophon">
  <svg width="18" height="18" viewBox="0 0 18 18"><rect x="2" y="2" width="14" height="14" rx="3" transform="rotate(45 9 9)" class="node-accent"></rect></svg>
  <p class="mark">"YOUR OFF-BY-ONE QUOTE HERE"</p>
  <p class="attrib">NAME</p>
</div>
```

## Step 3: the colophon quote

Think of a real scientist, philosopher, mathematician, or artist, whoever comes to mind, not from a list. Recall the shape of one thing they are known for saying. Bend it one notch off so it lands somewhere between witty and absurd, while staying close enough that the original is still recognizable. Attribute it to the real name, plain, no hedge word: the italic quote next to a name already reads as a riff, not a citation.

Three worked examples, for calibration only. Never reuse one of these, and never reuse a thinker from a previous report:

- "i think, therefore i'm billable" / descartes
- "if i've seen further, it's because i climbed on a really tall intern" / newton
- "nothing in life is to be feared, except regex" / curie

This is the one piece of the mechanism that is genuinely nondeterministic rather than randomized. The numbers came from `roll-flair.sh`. This quote comes from you, fresh, every time.

## What this is not

Not a diagram style, not a background texture, not a headline typeface. Selecting from a small named set of those is exactly the kind of thing a reader learns to pattern-match after three reports, which defeats the point. If a future version of this reference adds either, it has to vary on continuous, combinatorial parameters the way the corner ornament already does, not a pick from a short list.
