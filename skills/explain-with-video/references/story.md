# story and scenes

## establish the explanation

Name the viewer, what they need to understand or do, their relevant prior knowledge, and the main answer. Resolve conflicting source descriptions before preparing narration. Link the source behind each consequential claim. Distinguish a released product, a prototype, and an illustrative example where that affects the explanation.

Reuse the visual-report planning principles: audience, useful questions, altitude, depth, importance, order, and visual form are separate decisions. A high-altitude explanation states the governing rule, purpose, or relationship. It does not compress every implementation part into a smaller diagram. Numbers and specific UI details can be essential when they change the viewer's action.

Start with the answer or useful task. Introduce prerequisites before using them. Keep a qualification with the claim it changes. Explain the mechanism only as far as the viewer needs. A fixed-duration video has no disclosure control, so remove optional detail or put it in the companion source note.

## write the scene plan

Save a JSON object with `title` and an ordered `scenes` array. Each scene has a unique lowercase kebab-case `id`, `narration` as text or a list of short phrases, and `visual` describing the information shown. Add source links and qualifications as planning fields when useful. `scripts/narrate.py` uses the speech fields and preserves the visual descriptions in the transcript.

For each scene, define the viewer's question, its answer, exact on-screen labels, the source, and the change that motion explains. Use one main idea per scene without imposing a fixed duration. Speech, reading time, and the relationship determine its length.

Use narration to explain what the visible change means. Use the screen to show the relationship or action. Do not speak a dense paragraph while displaying the same paragraph. Make essential visual information available in the narration or descriptive transcript.

## build purposeful visuals

Use a sequence for actions, a chart for a meaningful quantity, a paired view for a decision, and a state transition for progress. A colored text card alone does not explain a relationship. Label what changes or moves. Every arrow, grouping, threshold, and causal transition needs factual support.

Keep orientation stable while attention moves. A phone or system diagram can remain in place while the relevant row, boundary, or state enlarges. Preserve original UI labels in real screenshots. Record any edited values and the behavior they illustrate. Do not present an edited prototype as evidence of deployed behavior.

Prepare screenshots, diagrams, fonts, and other assets before detailed animation. Use supplied or authorized assets. Keep provenance and licenses in the source note. Generate imagery only when it helps the subject. The framework can produce polished explainers using text, vector diagrams, and real UI alone.

Choose typography and a restrained palette for this audience. At 1080p, begin with roughly 44-60 pixel body type and larger headings, then check the actual playback size. Give the important state time to settle and be read. Use one focal movement at a time, consistent status colors, and labels or shapes that also communicate the distinction.

## review before rendering everything

Read the script aloud or synthesize a short sample. Check unfamiliar terms and pronunciation. Build a representative 15-20 second segment that includes the hardest UI detail or diagram. Inspect it before expanding the rest. Save revisions to the plan, then regenerate only affected speech and scenes.
