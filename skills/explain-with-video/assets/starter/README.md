# video explainer starter

For an agent authoring a local explainer, this project provides a ten-second stage in two chapters, a bundled font, and FFrames inspection and rendering commands.

`src/lib.rs` is shaped the way `references/motion.md` asks: the video draws persistent actors with global time, and the scenes are chapters that only add their heading. The starter's actors are a vector screen that pushes to a second screen after a tap, a pointer that travels and presses, a row that lifts out of the screen as the same drawing and returns, a bar that grows against a fixed line while its number counts, and a station path whose token advances as the viewer acts. Replace the actors and chapters with the planned explanation and keep the structure: one `fn actor(t)` per actor, keyed to video seconds, and one entrance and exit per chapter heading.

Copy the project into a scratch run. Keep the bottom 102 pixels free for two caption lines. Media files belong in `media/`. Licenses and notes stay outside that directory.

`src/main.rs` loads media at runtime, preserves stereo audio, uses the Metal renderer, and encodes H.264 at CRF 18. The command line also accepts `--renderer skia-cpu` when a GPU is unavailable. No native preview opens unless the `preview` command is requested.

The starter is silent. Its sample captions demonstrate the reserved area. Replace `media/captions.vtt` with the renderer copy of the narration captions, then pass `--captions` to burn them into the video. The pinned FFrames parser requires minute-based timestamps such as `01:03.632` and one physical line per cue. Use `<br>` between two caption lines. Keep the standard WebVTT sidecar separately. Add narration with `AudioTrack` in each chapter's `audio()`, then derive chapter lengths from the measured audio and use the word timestamps as the clock for every actor. The `explain-with-video` skill describes script, narration, timing, motion, and review.

From this project directory:

```bash
cargo run --release --locked -- timeline
cargo run --release --locked -- inspect --fail-on warning
cargo run --release --locked -- strip -n 10 -o strip.png
cargo run --release --locked -- frame 3s -o frames
cargo run --release --locked -- render -o explainer.mp4
cargo run --release --locked -- --captions render -o captioned.mp4
```

The runtime at `~/tools/video-explainers/run-video` provides the same commands with a shared Cargo target and writable dependency caches. Pass the absolute project path as its first argument. Output paths are relative to the shell's working directory unless absolute paths are supplied.

FFrames is pinned to Git revision `44f5431ce63080135dc2e422b2c71e5bbfdecd91`. The lockfile pins transitive Rust dependencies. The renderer and CLI structure are adapted from FFrames under its MIT license, included in `licenses/FFrames-MIT.txt`. DM Sans is distributed under the SIL Open Font License in `licenses/DMSans-OFL.txt`.
