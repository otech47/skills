# report delivery

## files and local scope

Use `scratch new <slug> "<task>"`. Put the HTML in `reports/`, planning records and structured appendices in `files/`, and screenshots in `screenshots/` or the renderer's documented output directory. Complete the manifest with artifacts, checks, and outcome. If scratch is unavailable, use `~/.agent-scratch/<slug>-report.html` and report the fallback.

Keep one self-contained HTML file with inline CSS and visuals. Aim for tens of KB, normally under 150 KB before video payloads. Requested video can exceed this size target. Large embedded runtimes are defects. Meaningful external source links are allowed; rendering must not depend on network assets.

Publication requires authorization for this artifact in the current request. Opening, showing, or finishing means the local file. Do not infer permission from an earlier report's deployment.

## requested video

When video is requested, read `../../explain-with-video/references/browser-delivery.md`. Embed the finished video directly in the report with native playback controls. Include the video bytes and available captions in the HTML so the page remains portable. An MP4 download or a link to another player is supplementary. Verify play, pause, seeking, and captions inside the final page before handing off its HTML link. Ordinary reports do not require video production.

## prose and claims

Apply the `prose-style` skill. Use lowercase prose, short direct sentences, no em or en dashes, no mannered prose, and no narration of the session.

Read the active local style guide on every report: `references/google-devdocs.md`, otherwise `references/ast100.md`. A `.off` file is inactive. If both exist, use Google; if neither exists, use the house prose style. Do not fetch a style guide. `report-style` owns the toggle; do not edit the skill to switch styles.

The reader was not in this conversation. State the subject, define unfamiliar terms, link sources, and include dates that affect interpretation. Do not record promises kept, writer confidence, rejected drafts, or decisions about producing the artifact. A report about an actual design proposal can explain that design and its limits without narrating the author's session.

Re-read the title, thesis, diagrams, and body together. The body must not retract the opening. Keep material caveats beside claims. Distinguish proposed behavior, observed tests, and deployed state. An estimate is not a measurement. A merged change is not proof of live availability.

Keep anything required for the visible conclusion visible. Search and print behavior for collapsed content varies; do not rely on those mechanisms to reveal essential facts. A fold needs a reader and a question, and a report without folds can be complete.

## flair and signature

If `references/flair-chrome.md` exists, read it and apply its helper after content is final. Do not hand-author or hand-edit generated flair. Its `.off` form disables it. Flair carries no information and must not obstruct content.

Stamp the creator, recorded effort, and available whole-session counters after content and flair are final:

```bash
python3 scripts/stamp-signature.py REPORT --model MODEL --effort EFFORT --session-tokens SESSION_TOKENS --context-tokens CONTEXT_TOKENS
```

Repeat `--contributor MODEL ROLE EFFORT` for other models. Keep the creator first and one model per line. Use readable names. Do not infer model or effort from task difficulty or assign report-specific token usage.

Read only exact current or contributor transcripts:

```bash
python3 scripts/read-session-effort.py /path/to/claude-session.jsonl
python3 scripts/read-codex-session.py /path/to/codex-rollout.jsonl
```

Claude's non-null `perTurnEffort` overrides `effort`. Codex's `turn_context` holds effective model and effort. The readers expose `session_tokens`, which excludes cache reads and writes, and `processed_tokens`, which includes both. Neither count is report-specific or a billing total. Available context counts are separate. Use `session_tokens` in the footer. For other harnesses, use explicit session metadata. Preserve changed effort levels rather than selecting one retrospectively.

Use `unknown` only when the exact evidence is unavailable and record why in the manifest. Do not scan unrelated sessions or substitute a nearby transcript. Omit unavailable counters. In questions mode, this rule takes precedence over the shared render reference's allowance for rough estimates. For historical restamping, preserve the original timestamp and timezone with `--finalized-at`. Pass the same cutoff through the readers' `--before` option so later turns do not alter historical counters or effort. Use the rollout live at finalization, not a later resume or review thread.

Blind review copies can omit provenance only under `references/comparison.md`. Preserve raw signed outputs and their attribution separately.

## render loop

Read `references/render-checks.md` for setup, output fields, and unsupported checks. Run after the final signature:

```bash
scripts/check-render.sh REPORT --widths 375,1280
```

The checker includes 820px and 500px views, measures both palettes, and captures dark screenshots by default. `--theme light` selects light for review. Review wide and narrow once in the selected theme; automated checks cover both palettes.

- Use the immutable `result.json` named by the run. Verify its source hash matches the final report.
- Inspect readable tiles when a page exceeds about 1,500px. Do not use a shrunken full-page image to claim text or label review.
- Inspect expanded sections and relevant scroll-container positions. Check named exclusive details groups manually when reported unsupported.
- Fix overflow, failed resources, script errors, contrast failures, and label collisions. Unsupported checks are not passes. The optional `--geometry` check covers limited SVG relationships; visual review still applies.
- After changes, rerun and inspect affected views. A cached unchanged hash reuses already reviewed screenshots; do not reread them without a reason.
- Confirm the opening, visual explanations, qualifications, and optional details work for the intended reader. A green mechanical result alone is not completion.

Use theme variables and solid text backgrounds so contrast can be measured. Record unsupported cases and their actual review in the manifest. Do not claim unrun or skipped assertions passed.

## handoff

Open the final local HTML with `open REPORT` when interactive. For a background run, return the path without opening a browser. Use `tailopen` when cross-machine access is useful. Stop temporary resources owned by the report task and verify their completion.

Give a brief gist and a clickable report path. Keep methodology, implementation changes, or remaining evaluation limits in the reply or manifest, not the report body.
