# visual construction

Make relationships perceptible. After selecting the audience, questions, altitude, depth, and order, design how the reader will see each important answer.

## visual-first representation pass

For each selected answer, name the relationship the reader otherwise has to reconstruct. Prefer a visual when it makes that relationship clearer. Record the form and its explanatory purpose in the content plan before implementing it.

| relationship | candidate representation |
| --- | --- |
| information, money, or work moves between actors | flow or sequence with labeled transfers and boundaries |
| one object changes state | lifecycle with triggers, exits, and relevant failure paths |
| parts have ownership, dependencies, or containment | system map, tree, or nested structure |
| alternatives differ on shared criteria | aligned comparison table, paired views, or decision branches |
| change affects an experience | before/after of the same user task or interface |
| quantities vary across categories or time | chart with truthful scale, units, denominators, and uncertainty |
| a concept depends on a concrete case | worked visual example with matched labels and annotated transitions |
| exact mappings or records need lookup | compact table, with prose for the conclusion |
| one fact or one uncomplicated instruction | a sentence or short list; no decorative diagram required |

These are candidates, not one-to-one rules. A lens can use different forms at different altitudes. Mechanism does not always mean a flowchart, and impact does not require a statistic.

Do not stop at one opening diagram. Inspect every main section and useful detail block for a relationship that warrants drawing. Multi-step and multi-part explanations usually need a primary model plus focused visuals for the harder relationships. Do not impose a diagram quota or draw redundant versions of the same idea.

A prose card, icon, border, or ornament does not by itself explain a relationship. Use position, connections, alignment, containment, sequence, and labels deliberately. If removing the visual leaves the explanation equally clear, simplify it or replace it.

Test the opening visual at the selected altitude: can the reader explain its governing relationship without unexplained labels or prior knowledge this reader lacks? If not, replace its organizing model or defer it. A reader should not need to inspect every row of a dense comparison to discover the main relationship. Fewer boxes, smaller text, and shorter labels do not by themselves make a model more abstract. A detailed diagram can be excellent later or inside a useful disclosure.

For a conceptual comparison, make the shared behavior and meaningful differences visible together. For a responsibility map, show what each part owns and how the parts relate. A row of unrelated definition cards does neither. Do not require a comparison or a fixed number of elements when another form answers the reader's question better.

## guide attention within the explanation

Give each visual a clear reading order. Use position, scale, text weight, selective color, and space to distinguish the governing rule, the key difference, and supporting labels. Emphasize the relationship the reader needs to notice, not every noun equally. A shared rule can appear once across two variants, with only their meaningful differences highlighted.

Keep the meaning of visual emphasis consistent across the report. Pair color with labels, shape, or position, and preserve readable contrast in both palettes. Color should carry a distinction, not decorate interchangeable cards.

Choose each section's composition for its question. Repeating the same heading, paragraph, table, and callout pattern can hide where the reader should look. Vary composition when the relationship changes, while keeping typography and visual conventions consistent. Do not add novelty or a new diagram when the same clear form fits.

## connect pictures and claims

- Every arrow, boundary, grouping, and state is a claim. Support it with source facts or label it illustrative.
- Label what flows or changes. Distinguish ownership, permission, data flow, and chronological order instead of using identical unlabeled arrows.
- Put conditions on the branch or transition they qualify. Preserve uncertainty in the visual, not only in a footnote.
- Introduce terms before using them in labels. Match diagram names to prose names.
- Let a diagram carry the relationship; use adjacent prose for the implication and limits. Do not duplicate the whole diagram as a paragraph.
- Highlight the finding, not the lowest altitude or the largest count. Large figures are appropriate only when the number is the finding.
- Do not count visuals as proof of quality. The test is whether the intended reader understands a useful relationship with less effort.

## implementation

Prefer self-contained inline SVG for diagrams and HTML/CSS for layouts, comparisons, timelines, and trees. Use semantic HTML where its natural layout is clearer. For complex Mermaid graphs, use `scripts/freeze-diagrams.sh` to produce inline static SVG. Do not ship a diagram runtime or external fonts, styles, scripts, or images.

The template provides `.node`, `.node-accent`, `.edge`, `.arrowhead`, `.svg-lbl`, and `.svg-lbl-soft`. Define SVG marker colors in CSS. Keep labels inside the viewBox with margins. Route connectors clear of text and stop arrowheads before labels. Use unique marker IDs when several diagrams share a page.

Keep prose at a readable measure. Let diagrams, comparisons, and tables use `.breakout` or `.wide` where useful. Avoid CSS margin shorthand that overrides breakout centering. Place a wide table inside `.t-scroll`, not `display:block` on the table.

On narrow screens, reflow a diagram when its relationships remain clear. Otherwise use a labeled scroll container at readable label size. Never scale a dense diagram down to illegible text. Review every necessary scroll position.

Use accessible text equivalents, meaningful figure labels, and redundant cues for color. Preserve contrast in both palettes. Decorative flair is separate from information design and never counts as a visual answer.

## visual acceptance

Before handoff, answer these from the rendered report:

- Does the opening answer this reader's first question and explain an initial relationship when needed?
- Can the reader recognize the main relationship before reading a detailed inventory or evidence matrix?
- Do the hard relationships receive visual treatment throughout, including useful lower-level explanations?
- Are the distinctions visible without reconstructing a long paragraph or matching unexplained labels?
- Do emphasis and layout direct attention to meaningful distinctions without depending on color alone?
- With disclosures closed, are the answer and its essential conditions understandable? When opened, do details add a subordinate answer without repeating the entire visible explanation?
- Do the visuals agree with the evidence, headline, and qualifications?
- Are wide and narrow labels readable, connections unambiguous, and expanded details usable?

Use `references/delivery.md` for the required render loop. Mechanical checks do not establish whether a diagram teaches the right relationship.
