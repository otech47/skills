---
name: explain-with-video
description: >-
  Create a narrated video explainer from source material, a product workflow, a technical concept, or an existing report. Use when the user explicitly asks for a video explainer, a narrated walkthrough, an MP4 explanation, or to turn a report into a video. Uses FFrames for scenes and local speech for narration. Ordinary visual reports, diagrams, and requests to explain something visually do not request video. Produce both HTML and video only when both are requested.
---

# explain with video

Make a clear explanation that the intended viewer can follow at playback speed. A request for a finished video authorizes the necessary local production and export steps. Keep publication and external messages within the user's existing authorization.

## workflow

1. Read `references/story.md`. Name the viewer and their task before drafting. Establish the central answer, essential conditions, sources, visual relationships, and asset needs. Save a compact scene plan in a `scratch new` run. Reuse an existing report as evidence when useful; video does not require generating an HTML report first.
2. For narrated output, read `references/audio.md`. Generate speech and word timestamps with `scripts/narrate.py`, then use its measured scene timings. Keep the script, speech, captions, and scene code consistent. Honor an explicit silent-video request without generating speech.
3. Read `references/fframes.md`. Load the upstream design guide before designing and its API guide when writing scenes. Use the bundled starter and shared build cache. Preview one representative scene with a difficult label, meaningful movement, and narration before completing the sequence. Fix concrete problems, then render the requested deliverable.
4. Read `references/review.md`. Check the final encoded file, scene frames, transitions, captions, and audio. Use `scripts/check-media.py` for measurable media checks. State any unavailable listening or playback review accurately.
5. Deliver the MP4, captions, descriptive transcript, source notes, and editable project. Link the finished video first. Keep build caches out of the package and complete the scratch manifest. Stop task-owned resources that are no longer needed.

## scope and cost

Infer ordinary production choices from the source and audience. For an unconstrained first explainer, start with roughly 60-90 seconds, one landscape format, and one voice. Extend when the explanation requires it. Keep music, extra aspect ratios, generated footage, and alternate voices conditional on their value or the request.

Load only the references needed for the current stage. Stabilize the script before detailed animation. Reuse unchanged speech and assets. Review contact sheets for coverage, then inspect dense labels and transitions at useful resolution. Correct failures without repeatedly polishing scenes that already work.

The baseline output is a narrated 1080p MP4 with WebVTT captions. The viewer should understand the subject, decision or mechanism, essential conditions, and outcome without this conversation. Preserve distinctions that change the answer. Put optional implementation detail in source notes instead of speeding through it.
