# review and delivery

Review the actual encoded file that will be delivered. Record its hash, duration, dimensions, frame rate, audio streams, caption file, and the checks that ran. Separate automated media checks from judgments that need vision or hearing.

## content and visuals

- The opening names the subject and useful answer without relying on the conversation.
- The viewer can follow the decision or mechanism. Essential conditions remain visible where they apply.
- Source facts, narration, UI labels, and diagrams agree. Prototype or illustrative behavior is identified where necessary.
- Important text and callouts are readable at the intended player size. Color has another cue such as a label, shape, or position.
- Motion reveals a useful change and has a clear focal point. Text remains visible long enough to read after movement settles.
- Scene boundaries, the opening, the ending, and dense details are inspected in rendered frames. Contact sheets cover the sequence; close samples cover fast transitions.

## sound, captions, and playback

```bash
python3 "$HOME/.agents/skills/explain-with-video/scripts/check-media.py"   "$RUN/files/video.mp4" --captions "$RUN/files/audio/captions.vtt"   --output "$RUN/files/media-check.json"
```

Use `--help` for the current options. Use `--silent` only for an explicitly silent video, omitting `--captions` when none exist. For the default export, require `--width 1920 --height 1080` and compare the measured frame rate with the project timeline. Decode the full file, check the expected streams and duration, measure loudness and peak level, and validate captions. Correct failures before calling the export complete. Missing, skipped, and unsupported checks are not passes.

Watch the final file to check pacing, continuity, audio synchronization, and caption placement. Listen for names, numbers, pronunciation, clipped words, unintended silence, and distracting music. If the environment cannot provide direct listening or continuous visual playback, say exactly which review is unavailable. Frame inspection, decoding, speech timestamps, and signal measurements do not establish voice naturalness or full playback quality.

WebVTT captions must match the final narration. Verify key terminology and numbers manually. Supply a descriptive transcript with the essential visual information. If captions cannot be loaded reliably in the intended player, also export a captioned MP4.

## handoff

Provide the finished MP4 first, followed by captions, transcript, source notes, and an editable project without build caches. A local player is optional when it improves caption access. Do not generate a full HTML report unless requested. Keep publication, uploads, and external messages within the user's authorization.

Record the actual runtime revision, voice settings, render timings, corrections, and available agent usage counters in the scratch manifest. Do not infer total production cost from rendering speed. Stop task-owned render commands and services that are no longer needed, using exact identities. Keep resources required by other work and record ownership.
