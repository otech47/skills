# zoom canvas

a pan and zoom box for one wide diagram. it is plain css and js with no dependencies. inline both files into the report so it stays one self-contained html file.

## when to use

use it for a diagram wider than the text column that must stay readable. the box opens at a fit scale that keeps labels legible, and the reader zooms or pans to see the rest. do not use it for a diagram that reflows or fits the column. that one stays a plain figure. do not shrink a dense diagram to fit instead.

## markup

```html
<div class="zoom" data-w="1460" data-h="620">
  <div class="zoom-bar">
    <button type="button" data-z="in" aria-label="zoom in">+</button>
    <button type="button" data-z="out" aria-label="zoom out">&minus;</button>
    <button type="button" data-z="fit">fit</button>
    <output class="zoom-level"></output>
    <span>drag to pan, pinch or ctrl and scroll to zoom, double click to zoom in</span>
  </div>
  <div class="zoom-view"><div class="zoom-inner"><svg viewBox="0 0 1460 620" width="1460" height="620">...</svg></div></div>
</div>
```

for an image, put `<img src="data:..." width="1460" height="620" alt="...">` in `.zoom-inner`. give the svg or image a fixed pixel width and height that match `data-w` and `data-h`.

## legend and text fit

put the colour legend in html under the box, not inside the svg. a legend drawn on the canvas collides with whatever the layout grows into, and it scales with the zoom. the markup is `<ul class="zlegend"><li><i style="background:var(--accent)"></i>person</li>...</ul>` right after the `.zoom` div.

size every card to its text. compute the wrapped line count first and set the card height from it, then size each row from its tallest card. never draw a fixed-height card around a free-length subtitle. after the build, measure in the browser: for each card group compare every `<text>` bounding box with the card rect and fail the build on any text within 10px of the right edge or 8px of the bottom.

## attributes

- `data-w`, `data-h`: the natural size of the content in pixels. required.
- `data-max`: the largest scale. default 4.
- `data-min`: the smallest scale. default 0.2, so the reader can zoom out past the fit state.
- `data-min-fit`: the floor for the fit scale. default 0 on a wide screen, so fit shows the whole diagram, and 0.6 below 700px, where labels would otherwise be unreadable and the reader pans instead.
- `data-pad`: space around the diagram at fit. default 14px. the margin tells the reader nothing is hidden past the edge.
- `.zoom-level` is optional. it shows the current scale.
- the fit button gets `aria-pressed="true"` while the box is at the fit state.

## interaction

- panning needs a click and hold: drag with the mouse, one finger on touch once zoomed, or the arrow keys with focus. a plain wheel or two finger scroll is never a pan. it always reaches the page untouched, whatever the zoom, so the box never traps or stutters page scrolling. at fit the whole diagram sits inside the box with `data-pad` of space around it.
- ctrl or meta wheel, trackpad pinch, and touch pinch zoom at the pointer.
- double click zooms in at the cursor. shift double click zooms out.
- when the box has focus: arrows pan, shift arrows pan further, plus and minus zoom, 0 fits.
- panning is clamped softly: the content can leave the box on any side, but a quarter of the box always stays covered, so there is never a dead end and the reader can always drag back.
- transforms are batched in requestAnimationFrame and the box rect is cached between reads, so a drag does not force layout on every pointer event.
- transitions turn off under `prefers-reduced-motion`.

## build

read `zoom-canvas.css` into the report's `<style>` and `zoom-canvas.js` into a `<script>` after the last `.zoom` element. the css uses the template variables `--line`, `--surface`, `--surface-2`, `--ink`, `--ink-faint`, `--accent`, `--bg` and `--radius`.
