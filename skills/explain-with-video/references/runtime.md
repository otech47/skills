# local runtime

The reusable runtime is `$HOME/tools/video-explainers`. Its `run-video` helper uses a shared Cargo target and writable dependency caches. Each video keeps its editable source and media in a separate project.

The verified environment is Apple silicon macOS, native arm64 Rust 1.97.0-nightly, FFmpeg 8.1.2, and the Metal renderer. FFrames is pinned to `44f5431ce63080135dc2e422b2c71e5bbfdecd91`. The bundled lockfile pins Rust dependencies. The first build can take several minutes and download native dependencies; later projects reuse the cache.

## prepare a project

Use `scratch new` to obtain a run directory, then copy this skill's `assets/starter` into its `files/video/` directory. Keep the supplied font licenses. Set `VIDEO_PROJECT` to that project's absolute path and `VIDEO_RUN` to the scratch run. Use absolute output paths so artifacts stay in that run.

If the runtime helper is absent, copy `assets/run-video` into `$HOME/tools/video-explainers/run-video` and make it executable. Check that native `cargo`, `ffmpeg`, and `ffprobe` are available. Diagnose a missing dependency before changing the toolchain or installing packages.

The helper sets these paths without changing the global shell environment:

```text
CARGO_HOME=$HOME/tools/video-explainers/.cargo-home
CARGO_TARGET_DIR=$HOME/tools/video-explainers/target
FFMPEG_BINARIES_CACHE=$HOME/tools/video-explainers/.ffmpeg-cache
```

The writable FFmpeg cache permits upstream prebuilt downloads. Without it, a sandbox can deny the default cache and cause a slower source build.

## inspect and render

```bash
"$HOME/tools/video-explainers/run-video" "$VIDEO_PROJECT" timeline
"$HOME/tools/video-explainers/run-video" "$VIDEO_PROJECT" inspect --fail-on warning
"$HOME/tools/video-explainers/run-video" "$VIDEO_PROJECT" strip -n 12 -o "$VIDEO_RUN/screenshots/story.png"
"$HOME/tools/video-explainers/run-video" "$VIDEO_PROJECT" frame 3s -o "$VIDEO_RUN/screenshots/detail"
"$HOME/tools/video-explainers/run-video" "$VIDEO_PROJECT" render 0s..15s --draft -o "$VIDEO_RUN/files/preview.mp4"
"$HOME/tools/video-explainers/run-video" "$VIDEO_PROJECT" render -o "$VIDEO_RUN/files/render.mp4"
```

Adjust the representative preview range to the actual timeline. The helper runs Cargo with `--release --locked`. Keep build caches outside the deliverable.

Metal device creation can require native sandbox escalation on this host, including during CLI initialization for inspection commands. Submit the same local render through the normal approval mechanism. The CLI also exposes `--renderer skia-cpu`; validate a frame before relying on that fallback. The `preview` command opens a native window, so use encoded previews when foreground focus must stay unchanged.

Load the pinned upstream guides from `vendor/fframes` when present. Its `fframes-revision` file is stored at the runtime root. An archive does not have Git metadata; compare that revision record with the manifest pin. Otherwise read the guides at the pinned public source URL in `fframes.md`.

## final audio

Measure the encoded narration before adjusting levels. Use one mastering stage. A quiet recording with peaks near zero needs compression or limiting, not a large uniform gain increase. FFmpeg's `loudnorm` filter can target `I=-16:TP=-1.5:LRA=11` while copying the rendered video. Recheck the final AAC stream for loudness, true peak, duration, and synchronization.

Copy the narration exporter's `captions-fframes.vtt` to the project's `media/captions.vtt`. The starter's `--captions` flag draws that text directly in FFrames, including two-line cues. Use `run-video "$VIDEO_PROJECT" --captions render -o "$VIDEO_RUN/files/captioned-render.mp4"`, with the full helper path when it is not on PATH. This works without FFmpeg's optional subtitle filters.

Keep the clean MP4 and standard WebVTT file. Export a captioned copy when direct playback cannot load the sidecar. Preserve the mastered audio when adding captions, and review frames with two caption lines in the reserved bottom area.
