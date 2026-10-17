# browser delivery

The HTML page is the viewing surface. A video link that opens an MP4 or a separate player leaves the reader outside the report.

## place the player

- For a report with video, embed the finished video directly in that report near its explanation. Preserve the report's useful content.
- For video only, create a compact HTML page with the subject, a brief description, and the player. A full written report is unnecessary.
- For an existing finished video, reuse its media and captions. Packaging does not require new narration or a render.
- Link the HTML first in the final response. Keep an MP4 download available as a secondary action.

Use a native `<video controls playsinline preload="metadata">`. Keep playback paused until the viewer starts it. Include an accessible name and a representative poster frame. Fit the player to the page width while preserving the video aspect ratio. Keep controls, captions, and surrounding text usable on narrow screens. Fullscreen gives dense scenes more space.

## package the media

Keep the HTML self-contained. Encode the final MP4, poster, and available WebVTT captions as data URLs. Generate those strings from files with a script; do not print them into the conversation. Video payloads are exempt from the report's small-file target. Avoid external players, network dependencies, and absolute local media paths. A page should keep playing after the HTML is moved by itself.

Use the standard `captions.vtt`, with its normal timestamps and line breaks. `captions-fframes.vtt` is only for the renderer. Set the caption language and label to match the narration. Omit the track for a silent video without captions.

```html
<style>video::cue { font-size: clamp(13px, 1.8vw, 24px); }</style>
<video controls playsinline preload="metadata"
       aria-label="VIDEO_TITLE" poster="POSTER_DATA_URL"
       style="display:block;width:100%;height:auto;max-height:75vh;background:#000">
  <source src="VIDEO_DATA_URL" type="video/mp4">
  <track kind="captions" src="CAPTIONS_DATA_URL"
         srclang="en" label="English" default>
  Your browser cannot play this video.
</video>
```

Replace every placeholder, including the caption language. Use `data:video/mp4;base64,` and `data:text/vtt;base64,` for the corresponding bytes. Match the poster MIME type to its image format. Adjust caption sizing after inspecting narrow playback. Supply a descriptive transcript, source notes, and the editable project with the deliverable. If caption tracks fail in the intended browser, embed the captioned MP4 and retain the transcript.

## verify the page

Open the final HTML through the same local path or authorized URL that the reader receives. Verify the player itself, not an MP4 opened in a separate tab.

1. Confirm that metadata loads with the expected duration and dimensions and that no media error occurs.
2. Start playback through the page. Confirm time advances, pause works, and seeking reaches a later scene.
3. Check that the caption track loads and shows a cue at its expected time. Inspect caption placement in the player. For burned-in captions, inspect the encoded frame instead.
4. Run `~/.agents/skills/visual-report/scripts/check-render.sh REPORT --widths 375,1280`. Review wide and narrow screenshots in the selected theme. The checker tests both palettes but does not establish playback.
5. Move a copy of only the HTML to another directory and repeat loading, playback, and caption checks with network access blocked. Check that no media request depends on the source directory or a temporary server.

Keep browser test evidence and any unavailable checks in the scratch manifest. A passing media decoder or render checker does not replace an embedded playback check. Direct listening and full video review follow `review.md`.
