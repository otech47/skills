# Report flair: decorative chrome

This file is the whole mechanism, and it is optional. If you are reading it, flair is on for this report. If it has been renamed to `flair-chrome.md.off`, flair is off. Skip this file entirely and build the report exactly as the rest of this skill describes, with no chrome.

**Toggle:** `report-flair on|off|status` (`~/.local/bin/report-flair`). Same rename-is-the-switch mechanism as `report-style`. Never edit this file to turn it off. Rename it instead.

## How to use it

One command, after the report is otherwise finished:

```bash
scripts/roll-flair.sh --apply reports/your-report.html
```

That rolls a fresh look and splices it in. It prints the quote it picked. Run `--strip <file>` to remove it again. `--apply` strips any previous flair first, so re-running it re-rolls rather than stacking.

Write no markup yourself, and do not hand-edit what it inserts. The point of the script is that the composition comes out of the OS CSPRNG rather than out of your idea of what a nice ornament looks like, and an agent editing the result afterwards puts the pattern back.

## What it adds

- **A rolled color scheme.** Two hues, `--accent` and `--flair2`, plus a matching `--accent-soft`. Saturation rolls freely, and lightness is fitted per hue so every rolled color clears 4.5:1 on both the light and dark background. It overrides the template's palette from a `<style id="flair">` block at the end of `<head>`, so the original values stay in the file untouched.
- **A corner ornament**, fixed to the top right of the viewport, floating there as you scroll. Built from orbit rings or arcs, an optional core glyph, and orbiting satellites, with every count, radius, shape, speed, direction and phase rolled independently.
- **A favicon** in the rolled hue, so a report is recognizable in a stack of tabs.
- **A real quote** in a colophon after `</main>`, drawn at random from a wide pool spanning science, literature, philosophy, art, sport and design.

## The rule that bounds all of it

**It carries no information, so it can never be wrong, and it costs no vertical space, so it can never push the thesis, the hero diagram, or anything else down the page.**

- The ornament is `position: fixed`, so it never occupies a row in the layout.
- No face, no eyes, no text in the ornament. Nothing on the page can be misread as a name, an opinion, or a reaction to the content.
- The quote is real and correctly attributed. It is not chosen to match the report, and it makes no claim about it.
- `--good` and `--warn` never roll, and the rolled hues stay clear of the green and red-orange bands, so a decorative color is never mistaken for a semantic one.

## Cost

The script is the whole thing: a few hundred milliseconds, no tokens spent generating markup, and nothing to review afterwards. Do not delegate this to a subagent. The fixed overhead of spinning one up is larger than the entire step.

## What this is not

Not a diagram style, not a background texture, not a headline typeface. Picking from a small named set of those is the kind of thing a reader learns to recognize after three reports, which defeats the point. Anything added here has to vary on continuous, combinatorial parameters the way the ornament already does.
