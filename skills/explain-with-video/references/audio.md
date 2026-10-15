# narration and captions

The local default is Kokoro with the stock `af_heart` voice. It produces speech files and word timestamps through its captioned-speech endpoint. Use a different provider or voice when the request requires it. Keep paid providers and external transfers within the user's authorization. Do not silently switch provider or voice after a failure.

## local service

Check `tts kokoro status`. If it is stopped, `tts kokoro start` starts the existing on-demand service. Record whether this task started it and retain the exact cleanup command, `tts kokoro stop`. Leave its idle policy and launch configuration unchanged. Stop it after generation if this task owns the running service and no other work needs it. Do not stop a service that was already running for someone else. Verify the stopped state after cleanup; use native approval if the sandbox denies the service operation.

The service listens at `http://127.0.0.1:8880`. Its `/dev/captioned_speech` endpoint returns audio and word timestamps. The ordinary `tts` readout command plays and deletes audio; use the exporter to retain narration files.

```bash
python3 "$HOME/.agents/skills/explain-with-video/scripts/narrate.py"   "$RUN/files/scene-plan.json" --output "$RUN/files/audio" --voice af_heart --fframes-captions
```

Use the script's `--help` for timing options. Set `--fps` to the video frame rate, which defaults to 30. The exporter pads scene ends with silence to whole frames without cutting speech. It writes scene WAVs, a complete narration WAV, `words.json`, `captions.vtt`, `transcript.md`, and `timing.json`. Scene clips include their holds. Place each clip once at its recorded start, or place the complete WAV once at zero. Do not add the holds again in scene code. Consume `timing.json` only when its status is `complete` and its `source_sha256` matches the current scene plan. A failed generation invalidates that timing file.

The `--fframes-captions` option also writes `captions-fframes.vtt`, recorded as `captions_fframes` in the timing file. It uses the same cue times and text as the standard sidecar. The pinned renderer requires total-minute timestamps and one physical line per cue, with `<br>` between display lines. Use this derived file for FFrames ingestion. Deliver and validate the standard `captions.vtt`.

## timing and reuse

Use measured audio duration and returned word timestamps. Never spread words uniformly across an estimated duration and call that alignment. If a provider cannot return usable timestamps, use a verified alignment tool or report the missing caption step. Compare important names and numbers against the final script. The exporter records narrow corrections for timestamps at Kokoro's trimmed audio boundaries and preserves their original values. Inspect those records before accepting an adjustment.

The exporter caches unchanged speech by input and voice settings. Keep that cache with the working project so revisions regenerate only changed text. If a voice model changes behind the same endpoint, invalidate the affected cache before comparing or shipping output.

Check the caption text against the spoken script and keep each cue short enough to read. Captions must match the final audio, with ordered intervals inside the video duration. Reserve space so captions do not cover meaningful UI. Deliver a separate WebVTT file and a captioned export when the chosen player cannot expose it reliably.

Keep narration intelligible. Music and sound effects are optional. If used, lower music during speech and time cues from the same event timings as the animation. Read the upstream FFrames audio guide for mixing and ducking. Measure loudness and peaks, then listen for pronunciation, abrupt edits, pauses, and balance. Measurements alone do not establish audible quality.
