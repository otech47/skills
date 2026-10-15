# independent report comparisons

This procedure compares `sequence` and `questions` without one author's first report becoming context for the second. The reader evaluates outputs without seeing the assignments.

this route controls experimental isolation and presentation. it does not authorize extra external writes or bypass harness permissions. if fresh contexts or a requested model are unavailable, explain the limitation instead of presenting a sequential rewrite as a blind comparison.

## freeze before composition

Stop the parent at the evidence-ready boundary, before selecting lenses, choosing altitudes, outlining, or drafting either report. The parent prepares inputs and coordinates runs; it does not supply its preferred answer or structure.

Freeze the original request, audience information actually provided, source artifacts, source dates, commit IDs or response hashes, and consequential evidence limits. Use raw sources where practical. If research has already produced notes, remove proposed headings, lens choices, report critiques, and unrelated session history. Preserve factual uncertainties and provenance. Do not use an earlier completed report as the common input unless reconstruction of that report is explicitly the test.

Distinguish two experiments:

- **composition comparison:** both authors research and explain the same frozen evidence. Differences include their interpretation and composition, but not different source availability.
- **end-to-end comparison:** each author researches independently from identical starting links. Retrieval can differ; record those differences and do not attribute all outcome differences to report composition.

Default to a composition comparison when testing these modes. For mutable sources, pin the same snapshot for every cell. Missing evidence is a reported limit, not permission to browse different versions quietly.

## prepare and launch

For a composition comparison, use `scripts/prepare-comparison.py` with a task file and evidence directory. The helper creates separate author directories, mode-specific guide copies, identical inputs, randomized review labels, and a private coordinator manifest. Run `--help` for its arguments. The helper permits one model for two cells or two models for four cells. Its runner intentionally forbids live research. For an explicitly requested end-to-end comparison, prepare separate contexts manually with equal starting links and retrieval permissions instead.

Each author gets only its assigned guide and dependencies, the shared task and evidence, and a dedicated output directory. Each starts with no parent conversation. Never use resume, continuation, a full-history fork, or one author for both modes. Do not send an author's plan, report, review, or errors to another author.

Keep model, recorded effort, tools, source access, permissions, and stopping conditions equal within a pair. Use exact requested model IDs, not aliases that can change. Verify the actual serving model and effort from run metadata. If unavailable or substituted, mark the cell invalid and ask for the needed choice. Do not silently replace a model.

When two models are requested, create four cells: each model writes one report per mode. Prefer launching cells together. If capacity requires scheduling, keep their contexts independent and record start times. One run per cell is a demonstration, not a reliable estimate of mode or model quality.

Preserve normal safety controls and hook trust. A neutral startup prompt can point to task and guide files without injecting the parent's subject discussion. Inspect initialization and transcripts for automatic skills, subject memories, prior reports, or cross-cell reads. Record preserved harness instructions and any differences. Fresh context is not a claim of filesystem or provider isolation.

For this controlled comparison, freeze shared style files and use the same nonrandom palette. Disable decorative flair in both copied guides only, without changing the user's global toggle. Keep raw signed outputs. Render validation applies to every output equally.

## retain evidence and review blind

Record the exact model, effort, CLI version, prompt bytes, source and guide hashes, start/end times, output paths and hashes, available token counters, checks, and any deviations. Keep missing counters null. Do not infer token savings or comprehension from file size, diagram count, or one pair.

Preserve first outputs and continuations. Allow the same mechanical repair policy for every author, such as fixing a render failure in its own context. Record repairs and prompts. Do not coach one report toward the other, choose a better attempt without disclosure, or revise the skill during the four-cell run.

Create review copies under neutral labels. Remove only attribution that reveals model or mode, such as the signature footer and identifying metadata. Preserve raw signed originals and document the exact masking. Do not alter content or styling to favor a report. Recheck the rendered review copies.

Use the skill-creator review viewer when available. Keep assignments, provenance, model scores, and mode names out of the initial review surface. Neutral labels conceal assignments, not stylistic clues or the possibility of inference. The private manifest supplies the reveal after feedback is recorded.

Capture the reader's judgments about understanding, useful visual explanation, unnecessary detail, missing context, and factual errors. Do not prefill preferences or report a winner before the reader judges. A machine check can establish render or source consistency; it cannot substitute for that judgment.

After feedback, associate it with the frozen cell records. Additional trials use a new run directory and fresh authors. Keep previous outputs unchanged so quality can be compared over time.
