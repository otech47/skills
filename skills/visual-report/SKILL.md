---
name: visual-report
description: Produce a designed, self-contained local HTML report instead of a long terminal answer, ordered so the reader meets the big-picture concepts and a visual mental model first and the technical detail last. Use it when the honest answer is something the user has to sit and read: how a system works end to end, an architecture or auth-flow walkthrough, an incident or forensic writeup, investigation or audit findings, a migration or option comparison that turns on real tradeoffs, a plan with rationale and open questions, or a research summary. Decide by the size and shape of the answer, not by the verb in the request: build the report when the reply needs several sections, more than one table, a diagram, or holds parts the reader must keep in their head at once, or when it would run past roughly two screens of terminal text. Also on explicit cues like "give me an html report", "make this a webpage", "put this in a report", "visualize this", "don't just dump it in the terminal". Prefer it proactively even when the user never says HTML. Do NOT use it when the answer is genuinely short even though the request sounds explanatory: a definitional "what is the difference between X and Y" about two well-known things, one fact, one command, a single snippet, a quick why-is-this-failing, or live back-and-forth debugging. If the whole answer fits in a few paragraphs, just say it in the terminal.
user-invocable: true
---

# Visual report

## Why this exists

The person reading you is in a terminal. A terminal is a bad place to absorb a big idea: everything is the same size, the same color, scrolling one line at a time, no way for the eye to see the shape of the thing before reading the parts. So when the honest answer to a question is long and structured, the terminal flattens it into a wall, and the reader has to rebuild the hierarchy in their own head while reading. That rebuild is the tax this skill removes.

An HTML page can do what the terminal cannot: show a picture of the whole idea first, use size and weight and color to say what matters most, and hide detail until the reader wants it. Rendered well, the same information lands in a fraction of the effort. This skill is for producing that page, and for producing it with a deliberate information hierarchy rather than just prettier text.

## The core idea: descend by altitude

The failure mode this skill exists to prevent is opening with detail. If the reader's first screen is specific, context-heavy, or jargon-dense, their brain has nowhere to put it and the report has already failed, no matter how good the styling is.

So every report descends through altitudes, highest first. The reader should be able to stop at any altitude and have understood something whole.

1. **Orientation (one breath).** A single sentence a smart person who just walked in would understand. What is this about, and why would the reader care. No jargon, nothing that assumes the conversation you just had.
2. **The mental model (one picture).** A diagram, mind map, or analogy that holds the whole shape at once, so every later detail has a place to land. This is where a visual earns its keep.
3. **The main parts (the map).** The three-to-seven major pieces and how they relate. Still conceptual, no code yet.
4. **The details (the ground), only if there are any.** Specifics, code, numbers, edge cases, tradeoffs, folded so a reader who does not need them is not made to scroll past them. This altitude is optional, and a report with no folds is finished rather than lazy. Filling it for its own sake is how a report goes bad after the first screen, so see "every fold has to earn its place" below.
5. **The exit (so what).** The decision, the next step, or the one thing to remember.

The test for whether you got it right: read only the first screen, as if you had no other context. If you would not know what this is or why it matters, add altitude, do not add detail. This is the single most important rule in the skill, because it is the thing the user most often finds broken.

Two corollaries that cold readers catch constantly:

**Name the thing before you use its parts.** Somewhere in the first screen, one clause has to say what the system or product actually *is*. Reports routinely explain a subsystem in perfect detail while never once saying "this is an occupational-health testing product" or "this is a bitcoin wallet," so the reader reverse-engineers the domain from scattered nouns. Related: gloss every proper noun and acronym on first use, in four words. The worst offenders hide in **diagram labels**, where a term gets introduced with no prose around it to define it. The element you built to orient a newcomer is the last place you can afford an undefined token.

**The title states the finding, not the topic.** "PR 4766 analysis" is a label and wastes the most valuable line on the page. "The hotfix is safe, the feature riding along with it is the risk" is a claim a reader can act on. Keep it one tight claim the eye takes in at a glance. The pull is to cram the finding and its mechanism into the headline with a colon ("SQS over Temporal: kill the ops pain at a third of the cost and make handlers idempotent"), which stacks to three lines and reads slower than it should. The mechanism half belongs in the thesis one line below, where it has room. State the finding in the h1, explain it in the thesis.

Full method, diagram patterns, and worked failure-and-fix examples: `references/information-hierarchy.md`. Read it before writing the report the first few times.

## Workflow

1. **Decide it is worth a report.** See the triggering guidance in the description. A rough gauge: if your answer has more than two screens of terminal text, or more than one table, or a set of parts the reader has to hold in their head at once, it is a report. A three-line answer is not. When in doubt on a genuinely borderline case, a one-line "want this as a visual report?" is fine, but lean toward just building it, since the reader can always glance and move on.

2. **Get a scratch home.** Run `scratch new <slug> "<what this report is>"` to get a run dir under `~/.agent-scratch/<project>/`. Write the report to `reports/` inside it. This keeps it out of /tmp and the repo, and leaves a manifest the next reader (or the otech extractor) can find. If `scratch` is unavailable, fall back to `~/.agent-scratch/<slug>-report.html` and say where it landed.

3. **Start from the template.** Copy `assets/report-template.html`. It is a self-contained scaffold: no external requests, works in light and dark, readable measure, and the altitude structure is already marked out in comments with styled components for each (`.thesis`, `.hero`, `.card`/`.grid`, `.callout`, `details`, `.exit`). Fill it in, deleting any altitude that genuinely does not apply. Keep it one file with inlined CSS, so it opens anywhere and survives being moved or emailed.

4. **Write the content by descending the altitudes, not by transcribing your terminal answer.** The report is not your draft answer with tags around it. Re-shape it: lead with the picture, push the specifics down into collapsible detail, cut the process narration.

5. **Open it.** `open <path>` on macOS puts it in the default browser, which is the runnable end state the reader wants. In a background or non-interactive run, skip the open and just print the `file://` path.

6. **Hand off in the terminal briefly.** In your terminal reply, give the reader the two-to-four-sentence version plus the path. Do not also paste the full report as text. The point was to get them out of the wall of text; reproducing the wall defeats it. Terminal gets the gist and the link, the page gets the depth.

## Building the visual

The mental-model picture at altitude 2 does more work than anything else on the page, so spend real effort there. Options, cheapest first:

- **Inline SVG**, hand-authored, for the hero diagram: a system shape, a pipeline, a layered stack, a mind map with a few branches. The template ships CSS classes (`.node`, `.node-accent`, `.edge`, `.lbl`) so a hand-drawn SVG picks up the theme and stays legible in dark mode. This is the default because it is self-contained and needs no dependency.
- **HTML + CSS structures** for anything that is really a layout: comparison columns, a timeline, a decision tree, a before/after. Often clearer and less fiddly than SVG.
- **Mermaid** when the graph is genuinely complex (dense flowcharts, sequence diagrams, state machines). Author in mermaid, then **freeze it**: run `scripts/freeze-diagrams.sh <src.html> <out.html>`, which renders every diagram to static inline SVG and strips the runtime. Never ship the mermaid library inlined. Measured on real reports: the runtime is ~3.2MB against ~15KB of actual content, so 99.5% of the file is a library, the page shows raw `flowchart TD` source until the JS parses, and a half-finished build leaves a `<!--MERMAID-LIB-HERE-->` placeholder that throws a ReferenceError and dumps diagram source into the page. Freezing gives the same picture at ~8KB with no JavaScript at all.

**Size budget: a finished report is tens of KB, not megabytes.** If yours is over ~150KB you have inlined a library, and that is a defect, not a tradeoff.

For any real data chart (bars, lines, distributions), follow the `dataviz` skill for color and form rather than improvising, and keep the same restrained palette the template uses.

### Numbers are not a slot to fill

The template ships no stat row, and most reports should not add one. A row of big figures at the top is the easiest thing on the page to fake, so an empty slot up there gets filled with whatever happens to be countable. An auth-flow walkthrough that opens with `6 digits`, `15 min`, `30 days`, `5 tries` has handed its loudest position to four constants that belonged in a sentence, and pushed the actual finding below them.

A figure earns large type only when the number **is** the finding. "38% of EU checkouts failed" is a finding. "12 files reviewed" is a description of the work. If the sentence around the number is what carries the meaning, leave it in the sentence.

When one or two genuinely qualify, set them at altitude 3 beside the part they measure, not stacked above the thesis. By then the reader has the context to know what the number means. The `.stats` and `.stat` classes are in the template's CSS for that, with `.accent` or `.warn` on the one carrying the weight. Reaching for a third or a fourth to balance the row is the signal to drop the row.

### Keep drawing as you descend

The altitude-2 hero holds the whole shape, but it should not be the last visual on the page. Reports tend to go picture, then text, then table, then folds of more text, as if drawing were a high-altitude tool only. It is not. As you descend, watch for the point where a table or a paragraph is really describing a relationship: a sequence of calls, a state machine, a before and after, a decision tree, how two structures line up. Drawn, those land in one look. Written, the reader rebuilds them row by row. A low-altitude diagram can carry more technical load than the hero and lean on more context, because the reader is oriented by the time they reach it, so a second or third diagram inline or inside a `details` fold usually beats another block of text. The bar does not change. It earns its place by showing a relationship the eye reads faster than the words would, not by making the page look busier.

Diagram pattern catalogue with copy-ready SVG starting points, including the lower-altitude sequence and state patterns: `references/information-hierarchy.md`.

## Every fold has to earn its place

Before a fold ships, name two things: **the question it answers, and the person who is asking.** The second half is the one that gets skipped, and skipping it is what produces a fold that opens onto a wall of identifiers or config values reading as noise.

That material is usually not padding. In a migration plan, the list of zone ids and bucket names is real and someone genuinely needs it, because whoever executes phase one has to write those imports. The mistake is that it serves a **different reader than the rest of the page**. The person reviewing the plan and the person executing it want different things, and a report that gives both the same affordance makes the executing reader's checklist look like an explanatory aside. So sort by audience first:

- **Written for the reader of this report.** Keep it, and make the summary name the question (below).
- **Written for whoever executes the work later.** Keep it but mark it, so nobody reads it as explanation. Label it an appendix in the summary itself, or better, write it to `files/` in the scratch run dir and link to it. A generated mapping or an import list rendered as a paragraph of inline code serves nobody: too dense to read, too unstructured to paste into a script.
- **Written for neither.** Cut it. Watch for this one, because it is the failure this skill causes: it scaffolds a place for depth, and dumping something enumerable into the empty slot is the path of least resistance.

### The summary names the question, not the contents

A summary that names a category of data ("import inventory and identifiers, by phase", "cloudformation stack disposition") tells the reader what is in the box but gives them no reason to open it. A summary that names a question does both at once, because the question implies who is asking.

| instead of | write |
| --- | --- |
| cloudformation stack disposition | which existing stacks get deleted, which get adopted, and what that costs |
| service dependency edges, for the module design | why the module boundaries fall where they do, and the one dependency we could not enumerate |
| the account today, compressed | what is actually running right now, if you need to sanity check the plan against reality |
| import inventory and identifiers, by phase | appendix: the exact resources phase 1 imports, for whoever runs it |

Some material needs no help: "the new repo layout" over a file tree is already self-evident, and "what this borrows from another repo, and what it deliberately skips" already names its question. So this is not a rule that every fold gets a subtitle. A mandatory label just produces "read this to understand the import inventory," which is circular and adds noise. The test is whether a reader can tell why they would open it, by whatever means gets there.

## It is a standalone artifact, not a reply

The report gets forwarded, reopened weeks later, and read by people who were never in your conversation. Write it for them, which means a few habits have to go:

- No second person aimed at one participant, and no correcting a belief the reader never held. "One correction before you check this against your understanding" and "the coverage gap you predicted" are addressed to someone who is not there.
- No undefined "today", "currently", or "the plan we built". Stamp the date and what the report was made from. A forensic or status document with no date is not usable later.
- Link the things you reference. Reports routinely cite PR numbers, issue ids, and file paths as inert text while asking the reader to go verify them. Make them real links.

## The thesis has to survive the body

The most damaging failure is not a missing detail, it is a headline the body quietly retracts. Real examples from shipped reports: a page whose hero promised "exactly one place it stops for you" while the body described four separate escalation paths; a page headlining "the hotfix is safe" whose detail section conceded the fix had zero test coverage; a diagram marking the failure at step 5 while its own evidence table indicted step 4.

A reader who catches one of these stops trusting everything above it. So after writing the detail, re-read the thesis and the diagram captions and make them true. If the honest claim is more qualified, the qualified version is almost always the better claim anyway.

## What good looks like

- The first screen orients a stranger, and no proper noun on it is undefined.
- There is one picture that shows the whole shape, near the top, and every label in it is a term the reader already has.
- The visuals do not stop at the hero. Where a table or a paragraph is really a sequence, a state change, a before and after, or a decision, a small labeled diagram carries it better, down in the detail and inside folds too.
- Importance is visible: the eye is pulled to the thesis and the key callout before the body text, by size and weight and color, not by the reader having to read everything.
- Detail is present but not forced, and every fold answers a question a named reader would ask. Fold dense material rather than prose, but cut it instead if nothing is asking for it. Never cite folded content from above the fold, and keep anything that must be searchable or printable out of a fold, since collapsed sections are invisible to Ctrl+F and to print.
- It reads in light and dark, and the hero diagram is legible on a phone. Diagrams scroll on narrow screens rather than shrinking to unreadable type.
- The template reads a notch larger than browser default, so nobody reaches for cmd-+. Prose holds a narrow, readable measure, while wide tables, the card grid, diagrams, and code break out past it to fill a large screen, capped so they never sprawl or scroll sideways. Breakout is automatic at the top level. Add class `breakout` (or `wide`) to opt anything else in, like a `<details>` holding a wide table, and do not widen the prose column to match.
- The prose follows the `prose-style` skill: no em dashes, lowercase to match his voice, no narration of the conversation that produced it. Lowercase covers the headings, the thesis, the kicker and every sentence start, not just the body copy, and it holds whether or not a style guide is switched on. Run that audit on the report text before finishing.
- One prose style guide may be switched on for reports, and it lives in this skill's `references/` directory. Look for `google-devdocs.md` (Google developer documentation style, the default) or `ast100.md` (ASD-STE100 Simplified Technical English). Whichever one is present is on, so read it fresh and run its rules in the same audit pass. A file renamed to `.off` is off. If both are off, write in the normal voice above and skip this entirely. If both are somehow present, apply `google-devdocs.md`. The knob is `report-style google|ast100|off|status`; never edit the files to switch it.

## Self-audit before you hand it over

Own the render loop rather than trusting the markup. Run:

```bash
scripts/check-render.sh reports/your-report.html
```

It checks the mechanical failures that actually ship (oversized file, external assets, unresolved build placeholders, em and en dashes including the HTML-entity forms `&ndash;` and `&mdash;` that hide in a time or number range, sideways page scroll, a hero diagram that shrinks instead of scrolling) and writes a wide and a narrow screenshot.

Then read both screenshots, because the part that matters is not mechanical. Ask the question the reader will ask: **if I knew nothing about this, would the first screen tell me what it is and why I should care?** Every proper noun on that screen needs to already be defined. If you cannot answer yes, the report is not done, and the fix is more altitude rather than more detail.

## What to avoid

- Do not open with context-specific detail. The most common and most fatal error. Re-read the altitude-1 test above.
- Do not turn every answer into a report. A quick fact, a yes/no, a single command, or a live debugging exchange is faster and kinder in the terminal. Over-triggering trains the reader to distrust the judgment and is its own friction.
- Do not decorate without structuring. Prettier text that is still detail-first has not solved the problem. The value is the hierarchy, the picture, and the progressive disclosure, not the font.
- Do not depend on the network. External CSS, fonts, or script CDNs make the report fragile the moment it is moved or opened offline. Inline everything.
- Do not also dump the full content into the terminal. Gist plus link.

## Promotion

The report lives in scratch, which is not its final home. If the reader wants to keep or share it, `surge-deploy` puts it at a public URL, and `gh-upload` gets an image of it onto a PR or issue. Offer that only if it is worth keeping; most reports are read once and pruned by the scratch retention window.
