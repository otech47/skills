# fframes rendering

FFrames draws coded SVG scenes and encodes video. The upstream `fframes-video` guides supply motion design, API usage, audio mixing, and inspection commands. Keep those as backend references instead of installing another broadly triggered skill.

The pinned backend revision is `44f5431ce63080135dc2e422b2c71e5bbfdecd91`. Read `runtime.md` for the local runtime and cache commands. The public source is [FFrames](https://github.com/dmtrKovalenko/fframes/tree/44f5431ce63080135dc2e422b2c71e5bbfdecd91).

## load only the relevant guidance

- Before designing, read this skill's `motion.md`, then the pinned `skills/fframes-video/references/design.md` for pacing, layout, typography, easing presets, and recipes.
- When writing scenes, read `skills/fframes-video/references/api.md` and apply the local `write-rust` skill.
- When placing or mixing audio, read `skills/fframes-video/references/audio.md`.
- Use the upstream `skills/fframes-video/SKILL.md` for CLI commands and troubleshooting.

An existing checkout under `$HOME/tools/video-explainers/vendor/fframes` makes these available locally. Check its recorded revision before relying on it. The upstream guides are also available at the pinned source link. Do not execute a downloaded installer without inspecting it.

## project and build

Copy `assets/starter` from this skill into the run's `files/video/` directory. Its `src/lib.rs` is already shaped as one stage: persistent actors drawn by the video with global timelines, chapters as scenes layered on top, a pointer that taps, a screen that pushes, a detail that lifts out, and a quantity that crosses a threshold. Replace its actors and chapters with the planned explanation; keep the structure. Keep the project source, fonts and licenses, input media, scene plan, and audio timing together. Keep the Cargo target cache outside the deliverable. Use the tested environment and commands in `runtime.md`.

Give actors global timelines in `Video::render_frame`, where `frame.seconds()` is video time. Scene code receives scene-relative time; use it for text entrances and the beats inside the chapter. Scene audio placed at the scene's start stays aligned with captions as long as scenes keep their measured durations and no `Overlap`; if you use `Overlap` for cross-fades, move the narration to the video's `audio()` at zero so it does not shift.

Prefer the Metal backend on supported macOS hardware. If GPU rendering is unavailable, validate a frame with the CLI's `skia-cpu` alternative and record the backend actually used. FFrames needs Rust and native media dependencies. Diagnose the actual missing prerequisite before adding packages or changing a global toolchain.

Use the project's existing scene, timeline, easing, and audio APIs. Load media before frame rendering. Frame rendering must not perform file reads or expensive setup. Use measured text layout, embedded fonts, and deterministic timing. Do not replace FFrames with a separate homemade animation engine.

## inspect and export

Run the project's CLI in release mode. Use `timeline` to inspect scene boundaries, `inspect` to detect missing assets and invalid geometry, `strip` for scene coverage, `frame` for dense labels, and `onion` or closely spaced frames for important motion. Read the actual PNGs. Automated inspection cannot establish text fit inside every box or explain whether a diagram teaches the right relationship.

Use a short draft range for the representative scene. A request for a finished video authorizes the final render; do not insert a new approval step for export. Launch an interactive preview only when it is useful and authorized, keeping the user's foreground application unchanged. Complete the requested local export instead of handing back commands to run.

Render the final delivery file, then run the media checker and the review contract. A successful compile or clean scene inspection is not a completed video.
