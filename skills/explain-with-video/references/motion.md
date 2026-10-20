# motion that explains

A report shows states. A video shows how one state becomes another, and the viewer learns from the change itself: what moved, where it came from, what it caused, what it crossed. That is the only reason to spend a video's production cost instead of writing a report.

The failure to avoid is the narrated slideshow: a static layout per scene, cards fading in beside a screenshot, a screenshot swapped for the next screenshot, one arrow sliding across the screen, a voice reading over it. If one frame per second carries the whole explanation, the result is a slideshow and should have been a report. Read this file before the upstream design guide. That guide covers polish, such as easing, stagger and margins, and assumes the motion already means something.

## one stage, not slides

Design the video as one continuous stage. Persistent actors hold their place and transform: the phone, the chart, the timeline, the diagram of the system. The camera moves. Scenes are chapters of the same stage. Text changes between chapters. The subject is not redrawn.

The end state of a chapter is the start state of the next. No hard cut, no blank frame, no layout swap. When the layout must change, move the actors to their new place while the viewer watches, so the viewer never has to re-find the subject.

In FFrames, draw persistent actors in `Video::render_frame` with global time (`frame.global_index`, or `frame.seconds()` at the video level), and give each actor one global timeline per property: position, scale, which screen is loaded, scroll offset, zoom target. Draw chapter-specific text and callouts in the scenes, each with its own entrance and exit inside its time, or cross-fade with `Overlap::Previous(0.4)`. The actors persist underneath, so the phone never blinks between chapters.

## what motion carries which information

| the viewer needs to learn | the motion that teaches it |
| --- | --- |
| a state changes | the element itself changes in place: color, shape, label, position. Not a second card appearing beside the first. |
| an action the viewer performs | the action happens on the real UI: a pointer lands on the control, the control presses, the screen responds. Not a numbered list of steps. |
| a quantity against a threshold | the quantity grows or shrinks continuously while the threshold line stands still, so the crossing is visible. Counters count to the number as the voice says it. |
| a comparison or decision | both cases start from the same origin and diverge in front of the viewer; one crosses the line, one stops short. |
| a process with stages | a token travels along a path through the stages; each stage lights as the token arrives; the stage the system is waiting on keeps moving. |
| part inside whole | the camera zooms from the whole toward the part while the whole stays partly visible, then returns. |
| where something is on the screen | the same pixels fly from their place in the whole to the callout and back, with a connecting line while they are out. |
| time passing or background work | a clock or progress fills continuously at a rate the viewer can read; "you can leave" is shown by the phone leaving while the progress keeps filling. |
| cause and effect | the cause moves first, the effect follows after a short lag, and a line draws on between them. |
| substitution or replacement | the old element exits along a path and the new element arrives along the same path into the same slot. |

Pick a row for every fact the narration states. A fact with no row is spoken over a still, which is the slideshow.

## screenshots are not slides

- A UI still arrives as the app shows it. After a visible tap, the previous screen pushes out and the new screen pushes in over 300 to 450 ms with ease-out. The viewer learns where to tap by watching the tap.
- Show the tap: a pointer dot travels to the control, the control presses to 96% and a ripple expands, then the screen responds. Pointer travel is itself the "where" information.
- When the relevant row is lower on the screen, scroll the screenshot to it. The scroll is the "where" too.
- A detail leaves the screenshot as the same pixels. Clip the row from the screen image, then animate its transform from its place on the phone to the callout position and scale, and keep a connector while it is out. Return it or fade it when it has done its job. Do not draw a new card that repeats the row's text.
- The camera can zoom the stage toward a region. Scale around a point by translating by `p * (1 - s)`, over 0.8 to 1.2 s, and zoom back the same way. Keep part of the whole visible so orientation survives.

## sync to the words

Use the narration's word timestamps from `words.json` as the clock for motion. The motion for a phrase starts at its first word and settles before its last word. "Eighty-four percent" is spoken while the bar reaches 84. The viewer hears and sees the same fact at the same moment, which is what makes a video faster to learn from than a page.

Labels appear when their word is spoken, not when the scene starts. Between phrases, the actor the voice is about keeps a small informative motion: the counter settling, the timer ticking, the spinner turning, the pointer drifting toward its next target. A pure hold is at most two seconds, and only after a change has finished so the viewer can read the result.

## rates and focus

- A change the viewer must follow takes 0.6 to 1.5 s. Faster is a flash. Slower is a wait.
- One thing carries meaning at a time. Secondary motion is smaller and later.
- Objects that carry meaning never teleport. If something must jump, the viewer has lost it.
- Animate transform and opacity; animate numbers with tabular figures. Start bars at 0.5, not 0.
- Ambient motion (glow, grid drift, breathing scale) stays below notice. It does not count as motion that explains and does not satisfy the checks below.

## plan the motion before writing scenes

In the scene plan, each scene lists `motion` beats and a `carry`:

```json
{
  "id": "comparison",
  "narration": "Here, calm marmot has eighty-four percent uptime this week, so Replace is available.",
  "visual": "The guardian list on the phone, with the calm-marmot row lifted out to a readable size.",
  "motion": [
    { "at": "calm marmot", "move": "the pointer travels to the calm-marmot row; the row lifts off the phone and grows into the callout", "shows": "which row the decision is about and where it is on the screen" },
    { "at": "eighty-four percent", "move": "the row's uptime bar grows to 84 against the fixed 90 line", "shows": "the rule is failed by six points" },
    { "at": "Replace is available", "move": "the Replace button on the lifted row presses once", "shows": "the action is on this row" }
  ],
  "carry": "the lifted row returns to the phone; the phone stays in place for the next chapter"
}
```

A beat names the cue word, the movement from one state to another, and what the movement teaches. A scene whose beats teach nothing is a slide. Redesign it before writing code. `scripts/narrate.py` ignores these fields, so they cost nothing at narration time.

## the stills test

Before the full render and again on the encoded file, lay out one frame per second (`strip`, or `ffmpeg -vf fps=1,tile=`). For each scene, name what the stills do not carry: the tap, the growth, the crossing, the travel, the swap. If the answer is "nothing" for any scene, that scene is a slide and goes back to the plan.

`scripts/check-motion.py` measures how much of the video is visibly changing, finds the longest dead windows, and detects hard cuts. Run it on every render. It catches a slideshow. It cannot tell informative motion from ambient drift, so the stills test is the judgment and the script is only a minimum check.

## worked example

The project at `$HOME/tools/video-explainers/examples/guardian-replacement` applies this file: one phone actor that stays on stage across six chapters, taps and screen pushes for every action, rows lifted out of the screenshot as the same pixels, a bar that grows past a fixed threshold as the number is spoken, and a handover token that keeps moving while the phone leaves the stage. Its `README.md` maps each chapter to the beats above.
