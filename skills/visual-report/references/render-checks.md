# render checks

## setup

requires Node 20 or newer and Chrome or Chromium. the helper uses the pinned `playwright-core` package without downloading a browser. from this skill directory, install with:

```bash
npm ci --prefix scripts --ignore-scripts --no-audit --no-fund
```

## run

```bash
scripts/check-render.sh reports/report.html
scripts/check-render.sh reports/report.html --geometry --widths 375,1280
```

`--output-dir DIR` changes the artifact directory. `--browser PATH` or `CHROME_PATH` selects the browser. `--timeout MS` sets the render deadline, from 100 to 600000 milliseconds. the default is 60000. browser launch has a separate timeout capped at 15000 milliseconds.

the default widths are 820 and 500 pixels, each with a fixed 900px viewport height. `--widths` adds responsive cases. every width is measured in light and dark with reduced motion. screenshots use dark mode by default; `--theme light` selects light mode. `--theme both` is available for explicit diagnostics, not routine model review. the source loads at its original file URL. relative assets retain their meaning but fail the self-containment check. network requests are blocked and reported. ordinary source links remain valid.

## outputs and exit status

each invocation creates a separate `<name>.render-*` directory. the `json:` output names that run's immutable `result.json`. use this path for review and automation. `<name>.render.json` and `<name>.render-latest` point to the latest published result.

explicit `<name>.wide-light.png`, `.wide-dark.png`, `.narrow-light.png`, and `.narrow-dark.png` paths point through the latest result. `.wide.png` and `.narrow.png` alias the selected screenshot theme, or light when `--theme both` is requested. unselected themes have no screenshot artifacts. a failed run can leave an alias without a target. inspect the manifest rather than trusting an old filename.

- exit 0: mechanical checks passed. visual review is still required.
- exit 1: a confirmed defect, such as overflow, missing assets, or a page script error.
- exit 2: the checker could not complete, including invalid measurements, timeout, missing dependencies, or a changed source file.

the manifest records the source path and SHA-256 hash, browser version, timing, individual checks, errors, views, and images. each view records its theme, viewport and page dimensions, default or expanded state, and scroll-container geometry. `captureThemes` identifies the selected screenshot theme; views in the other theme have an empty image list. image records identify full captures, readable tiles, warning crops, or scroll positions.

long pages receive 900px tiles so the full-page image is not the only review surface. ordinary details are expanded in a second capture state. named exclusive details groups require separate manual inspection and are marked unsupported. scroll containers receive captures at each position covering their content.

capture limits are explicit errors: 50000px page height, 10000px page width, 20 scroll containers, or 40 positions in one container. split excessive content or inspect unsupported states manually; do not call an incomplete run clean.

## automatic theme checks

the pinned axe-core dependency checks supported text contrast in both themes, including expanded sections. confirmed contrast failures return exit 1 with element selectors and measured colors. uncertain cases, such as text over images or gradients, are recorded as unsupported. unsupported does not mean contrast passed. prefer theme variables and solid backgrounds for report text.

the checker compares element positions and sizes across themes. a theme-specific layout change returns exit 1. colors should change without changing layout. review wide and narrow screenshots once in the selected theme; do not ask the model to inspect both palettes routinely.

[axe contrast API](https://www.deque.com/axe/core-documentation/api-documentation/) and [contrast thresholds](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum) define the automated text check. raster image content and unsupported SVG paints are outside a complete contrast guarantee.

## experimental geometry

`--geometry` warns about SVG text outside its viewport, overlapping label rectangles, and straight stroked connectors intersecting labels. normal text inside a node is not a collision. warnings include element descriptions and coordinates, with a crop in the selected screenshot theme. decorative SVGs marked `aria-hidden="true"`, hidden text, and definitions are excluded.

straight `line`, `polyline`, `polygon`, and `M/L/H/V/Z` path segments are supported, including relative commands and transforms. curved paths are reported as unsupported. bounding rectangles do not establish curved-stroke intersections. rotations, glyph shapes, marker tips, masks, ancestor clipping, and intentional overlaps still require visual review. missing HTML bars are outside these SVG checks.

to suppress a known intentional geometry relationship, add `data-render-ignore="reason"` to that element or its group. use a specific reason and inspect the rendered result. suppression does not skip overflow, resource, or typography checks.

## signature footer

```bash
python3 scripts/stamp-signature.py reports/report.html --model "PRIMARY MODEL" --effort high --contributor "REVIEW MODEL" audited high --session-tokens 120000 --context-tokens 45000
```

the numbers in this example are placeholders. supply available counters or rough estimates from the current session. omit unknown values. do not perform report-specific token attribution. the footer uses one line per model, with the creator first, its role, and recorded effort. counts use k/m, such as `45k` and `11.4m`. the date appears on its own line, such as `14 sep 2026 · 18:24 CEST`. use readable model names and `unknown` for unrecorded effort. legacy `--also-model` arguments remain supported with an unknown effort level. it stays below the quote when flair is reapplied and remains present when flair is off.

## acceptance tests

set `ACCEPTANCE_OUTPUT` to a scratch directory, then run `node tests/acceptance.mjs`. for footer tests, set `SIGNATURE_TEST_DIR` to a scratch directory and run `python3 tests/test_signature.py`.
