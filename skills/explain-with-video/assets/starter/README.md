# video explainer starter

For an agent authoring a local explainer, this project provides one eight-second scene, a bundled font, and FFrames inspection and rendering commands.

Copy the project into a scratch run. Replace the scene in `src/lib.rs` with the audience's decision, relevant evidence, and visible outcome. Keep the bottom 102 pixels free for two caption lines. Media files belong in `media/`; licenses and notes stay outside that directory.

`src/main.rs` loads media at runtime, preserves stereo audio, uses the Metal renderer, and encodes H.264 at CRF 18. The command line also accepts `--renderer skia-cpu` when a GPU is unavailable. No native preview opens unless the `preview` command is requested.

The initial scene is silent. Its sample captions demonstrate the reserved area. Replace `media/captions.vtt` with the renderer copy of the narration captions, then pass `--captions` to burn them into the video. The pinned FFrames parser requires minute-based timestamps such as `01:03.632` and one physical line per cue. Use `<br>` between two caption lines. Keep the standard WebVTT sidecar separately. Add narration with `AudioTrack`, then derive scene lengths and captions from the measured audio. The `explain-with-video` skill describes script, narration, timing, and review.

From this project directory:

```bash
cargo run --release --locked -- timeline
cargo run --release --locked -- inspect --fail-on warning
cargo run --release --locked -- strip -n 8 -o strip.png
cargo run --release --locked -- frame 3s -o frames
cargo run --release --locked -- render -o explainer.mp4
cargo run --release --locked -- --captions render -o captioned.mp4
```

The runtime at `~/tools/video-explainers/run-video` provides the same commands with a shared Cargo target and writable dependency caches. Pass the absolute project path as its first argument. Output paths are relative to the shell's working directory unless absolute paths are supplied.

FFrames is pinned to Git revision `44f5431ce63080135dc2e422b2c71e5bbfdecd91`. The lockfile pins transitive Rust dependencies. The renderer and CLI structure are adapted from FFrames under its MIT license, included in `licenses/FFrames-MIT.txt`. DM Sans is distributed under the SIL Open Font License in `licenses/DMSans-OFL.txt`.
