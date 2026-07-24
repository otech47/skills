# Information hierarchy and diagram patterns

The reference behind the altitude model in SKILL.md. Read this when building a report until the moves are automatic.

## Contents
- The altitude descent, expanded
- The altitude-1 gate, with a worked failure and fix
- Diagram patterns, with copy-ready SVG
- Visual encoding: how the eye reads a page
- Common failure modes and their fixes

## The altitude descent, expanded

The reader arrives cold. Their brain builds understanding top-down: it needs a frame before it can place a fact. Give a fact before the frame and the fact bounces off. So the report is a controlled descent, and each altitude is written for a reader who will stop there.

**Altitude 1, orientation.** One sentence, sometimes two. It answers "what is this and why do I care" for someone who was not in the conversation. The enemy is the assumed antecedent: "the migration" (which migration?), "this bug" (what bug?), "the coordinator" (the what?). Name the thing in words a smart outsider owns. If the topic is genuinely niche, give the one analogy that makes it ordinary before you use its real name.

**Altitude 2, the mental model.** One picture. Its job is to give every later detail a place to land. A reader who has seen the shape can file "oh, that is the part on the left" instead of holding an unplaced fact. This is the altitude a terminal cannot do at all, so it is where the report earns its existence. Spend effort here.

**Altitude 3, the map.** The major parts and their relationships, in words and cards, still conceptual. Three to seven parts; if there are more, you have not found the right grouping yet. Group first, then the reader can hold the group and expand it.

**Altitude 4, the ground.** Now the specifics: code, numbers, config, edge cases, the tradeoff you actually weighed. This is real content, not filler, but most readers do not need all of it on the first pass, so it belongs in collapsible `details` blocks or clearly-marked sections they can skip. Depth available, not depth imposed. Draw here too. A detail that is a sequence of calls, a state machine, or a before and after reads faster as a small diagram than as a table or a paragraph, and the reader now has the frame to take in a denser picture than the hero could carry. A folded mechanism is often exactly the thing a diagram explains best.

**Altitude 5, the exit.** The reader is leaving with something. The decision to make, the next action, the one sentence to remember. Do not end on the last technical detail; end on the so-what.

## The altitude-1 gate, with a worked failure and fix

After the report is written, read only the first screen, cold, as if you had no other context. If you would not know what this is or why it matters, it failed. Fix by adding altitude, never by adding detail.

**Failed opening** (opens at altitude 4, assumes everything):

> The SessionEnd hook was dropped from settings.json during the permission-tuning rewrite, so daily.py --quiet stopped running and the ledger store went stale while the pre/post density split kept reading the old cutoff.

A stranger gets nothing: what hook, what store, what split, why care.

**Fixed opening** (altitude 1, then 2, then the detail survives lower down):

> This report is about a background system on your machine that quietly learns how you like your coding assistant to work. It stopped updating three weeks ago and nobody noticed, because it fails silently. Here is what broke, how we found it, and what it means for the numbers it reports.

Same facts, but now the reader has a frame. The `settings.json` and `daily.py` specifics still appear, at altitude 4, where they now have somewhere to land.

## Diagram patterns, with copy-ready SVG

Use the template's classes so diagrams inherit the theme and stay legible in dark mode: `.node` (plain box), `.node-accent` (highlighted box), `.edge` (connector), `.svg-lbl` (label text), `.svg-lbl-soft` (secondary text), `.arrowhead` (marker). Put the hero diagram inside the `.hero` figure at altitude 2. Reuse the same classes for diagrams lower down, dropped inline between paragraphs, set beside or in place of a table, or tucked inside a `details` fold. Most reports want more than one: the hero for the whole shape, then smaller diagrams that each pin a single mechanism as the reader reaches it. The patterns below run high altitude to low, and the last two, sequence and state, are the ones that most often replace a wall of text or a dense table down in the detail.

Two rules that decide whether the diagram survives contact with a real reader:

**It must scroll on a phone, not shrink.** A `viewBox="0 0 900 340"` diagram with only `max-width: 100%` scales to about a third on a 375px screen, dropping 12px labels to roughly 4px. The template sets `min-width: 640px` below an 800px viewport so the `.hero` scroll container actually engages. Keep that, and keep your smallest label at 11px or larger in viewBox units.

**Every label must be a term the reader already has.** The diagram usually arrives before the prose that would define its nouns, so an unglossed token here is worse than anywhere else on the page. If a box has to be called `gatewayd`, give it a four-word sublabel saying what that is.

### Hero flow / pipeline
For a process, a data path, or a sequence of stages. Left to right.

```html
<svg viewBox="0 0 640 120" role="img" aria-label="three stage flow">
  <rect class="node-accent" x="20"  y="35" width="150" height="50" rx="10"/>
  <text class="svg-lbl" x="95"  y="65" text-anchor="middle">Ingest</text>
  <path class="edge" d="M170 60 H210" marker-end="url(#a)"/>
  <rect class="node" x="245" y="35" width="150" height="50" rx="10"/>
  <text class="svg-lbl" x="320" y="65" text-anchor="middle">Compress</text>
  <path class="edge" d="M395 60 H435" marker-end="url(#a)"/>
  <rect class="node" x="470" y="35" width="150" height="50" rx="10"/>
  <text class="svg-lbl" x="545" y="65" text-anchor="middle">Aggregate</text>
  <defs>
    <marker id="a" class="arrowhead" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
      <path d="M0 0 L7 3 L0 6 z"/>
    </marker>
  </defs>
</svg>
```

Style the arrowhead through the `.arrowhead path` rule in the template, never with `fill="var(--accent)"` directly on the path. A `var()` inside an SVG presentation attribute is not reliably substituted across engines, and when it fails the arrowhead falls back to black, which disappears against a dark background.

### Mind map / concept branches
For one central idea with a few facets. Center node, branches out.

```html
<svg viewBox="0 0 560 260" role="img" aria-label="concept with four branches">
  <path class="edge" d="M280 130 C200 130 180 60 120 60"/>
  <path class="edge" d="M280 130 C200 130 180 200 120 200"/>
  <path class="edge" d="M280 130 C360 130 380 60 440 60"/>
  <path class="edge" d="M280 130 C360 130 380 200 440 200"/>
  <rect class="node-accent" x="210" y="105" width="140" height="50" rx="25"/>
  <text class="svg-lbl" x="280" y="135" text-anchor="middle">Core idea</text>
  <rect class="node" x="20"  y="38"  width="150" height="44" rx="10"/>
  <text class="svg-lbl" x="95"  y="65"  text-anchor="middle">Facet one</text>
  <rect class="node" x="20"  y="178" width="150" height="44" rx="10"/>
  <text class="svg-lbl" x="95"  y="205" text-anchor="middle">Facet two</text>
  <rect class="node" x="390" y="38"  width="150" height="44" rx="10"/>
  <text class="svg-lbl" x="465" y="65"  text-anchor="middle">Facet three</text>
  <rect class="node" x="390" y="178" width="150" height="44" rx="10"/>
  <text class="svg-lbl" x="465" y="205" text-anchor="middle">Facet four</text>
</svg>
```

### Layered stack
For levels of abstraction, a tech stack, or a containment relationship. Top is highest-level.

```html
<svg viewBox="0 0 420 220" role="img" aria-label="four layers">
  <rect class="node-accent" x="60" y="20"  width="300" height="40" rx="8"/>
  <text class="svg-lbl" x="210" y="45"  text-anchor="middle">What the user sees</text>
  <rect class="node" x="60" y="68"  width="300" height="40" rx="8"/>
  <text class="svg-lbl" x="210" y="93"  text-anchor="middle">Coordination</text>
  <rect class="node" x="60" y="116" width="300" height="40" rx="8"/>
  <text class="svg-lbl" x="210" y="141" text-anchor="middle">Storage</text>
  <rect class="node" x="60" y="164" width="300" height="40" rx="8"/>
  <text class="svg-lbl" x="210" y="189" text-anchor="middle">Raw data</text>
</svg>
```

### Comparison and decision
Two or three options side by side are usually clearest as an HTML `.grid` of `.card`s or a table, not SVG. A decision ("use A when..., use B when...") reads well as a short table with a "use it when" column. Reach for SVG only when the branching itself is the point.

### Sequence over time
Low altitude. For an interaction between a few actors, message by message: who calls whom, in what order. Actor headers across the top, lifelines dropping down, messages as horizontal arrows read top to bottom. This is the diagram that most often beats a paragraph narrating a call flow.

```html
<svg viewBox="0 0 520 220" role="img" aria-label="client pays through a gateway that debits the ledger">
  <rect class="node-accent" x="20"  y="16" width="120" height="38" rx="8"/>
  <text class="svg-lbl" x="80"  y="40" text-anchor="middle">Client</text>
  <rect class="node" x="200" y="16" width="120" height="38" rx="8"/>
  <text class="svg-lbl" x="260" y="40" text-anchor="middle">Gateway</text>
  <rect class="node" x="380" y="16" width="120" height="38" rx="8"/>
  <text class="svg-lbl" x="440" y="40" text-anchor="middle">Ledger</text>
  <path class="edge" d="M80 54 V206"/>
  <path class="edge" d="M260 54 V206"/>
  <path class="edge" d="M440 54 V206"/>
  <text class="svg-lbl-soft" x="170" y="86" text-anchor="middle">pay(invoice)</text>
  <path class="edge" d="M80 92 H256" marker-end="url(#a)"/>
  <text class="svg-lbl-soft" x="350" y="126" text-anchor="middle">debit</text>
  <path class="edge" d="M260 132 H436" marker-end="url(#a)"/>
  <text class="svg-lbl-soft" x="262" y="166" text-anchor="middle">settled</text>
  <path class="edge" d="M440 172 H84" marker-end="url(#a)"/>
  <defs>
    <marker id="a" class="arrowhead" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
      <path d="M0 0 L7 3 L0 6 z"/>
    </marker>
  </defs>
</svg>
```

### State machine / lifecycle
Low altitude. For a thing that moves through states: nodes are states, edges are transitions labeled with what triggers them. Loops and back-edges are the payoff, since a table cannot show them without the reader tracing rows.

```html
<svg viewBox="0 0 520 170" role="img" aria-label="idle to running to settled, with a retry back to idle">
  <rect class="node-accent" x="16"  y="52" width="120" height="44" rx="22"/>
  <text class="svg-lbl" x="76"  y="79" text-anchor="middle">idle</text>
  <rect class="node" x="200" y="52" width="120" height="44" rx="22"/>
  <text class="svg-lbl" x="260" y="79" text-anchor="middle">running</text>
  <rect class="node" x="384" y="52" width="120" height="44" rx="22"/>
  <text class="svg-lbl" x="444" y="79" text-anchor="middle">settled</text>
  <path class="edge" d="M136 74 H196" marker-end="url(#a)"/>
  <text class="svg-lbl-soft" x="166" y="66" text-anchor="middle">start</text>
  <path class="edge" d="M320 74 H380" marker-end="url(#a)"/>
  <text class="svg-lbl-soft" x="350" y="66" text-anchor="middle">done</text>
  <path class="edge" d="M260 96 C260 140 76 140 76 98" marker-end="url(#a)"/>
  <text class="svg-lbl-soft" x="168" y="150" text-anchor="middle">retry on failure</text>
  <defs>
    <marker id="a" class="arrowhead" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
      <path d="M0 0 L7 3 L0 6 z"/>
    </marker>
  </defs>
</svg>
```

## Visual encoding: how the eye reads a page

The eye lands on the biggest, boldest, most saturated thing first, then follows contrast down. That order should match your altitude order, so importance is doing the navigating, not the reader's patience.

- **One accent color, used sparingly.** The template's accent marks the eyebrow, the thesis emphasis, the highlighted node, the one callout. If everything is accented, nothing is. Reserve it for "look here."
- **Size encodes altitude.** The title is biggest, the thesis large, body text plain, captions small. A reader skimming only the large type should still get the arc.
- **Whitespace groups.** Space between sections says "new idea"; tight spacing says "these belong together." Do not fear empty space; it is how the eye finds structure.
- **One key callout per report.** The single `.callout` is the thing to remember. More than one and the reader cannot tell which mattered.
- **Contrast and color are not the only channel.** Anything shown by color is also shown by position, label, or shape, so it survives color-blindness and grayscale printing.

## Common failure modes and their fixes

- **Opens with detail.** The cardinal sin. Fix: add altitudes 1 and 2 above it; demote the detail.
- **Decorated wall.** Prettier fonts, same undifferentiated dump. Fix: this is a structure problem, not a style problem. Find the picture and the parts; push specifics into `details`.
- **No picture.** All prose. Fix: if the reader has to hold more than about three things in relation, draw the relation.
- **Everything expanded.** Every detail forced onscreen. Fix: collapse altitude-4 material; let the reader open what they want.
- **Ends on a footnote.** Trails off in the last edge case. Fix: add the exit; end on the decision or takeaway.
- **Transcribed the terminal answer.** Same linear order, now in a page. Fix: re-shape by altitude; the report is not the draft with tags around it.
- **Rainbow of accents.** Color used for decoration. Fix: one accent, spent only on what matters.
