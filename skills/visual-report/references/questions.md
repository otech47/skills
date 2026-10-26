# questions mode

Choose the reader's useful questions before arranging the page. Then use visuals to make their answers understandable. A report is not ten headings filled from a transcript.

## audience and purpose

Name the intended reader in a phrase before writing. The requester may supply the task without being the recipient. Infer the reader from explicit recipients, sharing destination, purpose, and relevant context. Ask only when unresolved ambiguity would materially change the artifact.

Establish the reader's purpose, domain knowledge, implementation knowledge, technical fluency, sharing limits, and attention. Do not substitute a job title for those facts. A public architecture explanation may need mechanisms; a maintainer's status check may need one sentence. Keep meaningful assumptions in the planning record.

Name any specific concept the reader already knows that can explain the unfamiliar subject. Distinguish supplied familiarity from an assumption. Technical fluency does not establish familiarity with this feature. If that knowledge is uncertain, give a short grounding explanation rather than requiring it. A familiar comparison is useful only when its shared rule and meaningful differences are supported.

For mixed audiences, choose the primary reading task. Keep shared answers visible and label useful specialist material. Use separate versions when disclosure requirements are incompatible.

## separate the dimensions

| dimension | decision |
| --- | --- |
| lens | which kind of question needs an answer? |
| altitude | what unit does the answer explain: a whole system or principle, a workflow or relationship, or one instance or operation? |
| depth | how much context, reasoning, and illustration does this reader need at that altitude? |
| importance | what would change the reader's understanding, conclusion, or ability to act? |
| order | what must the reader encounter before this answer becomes usable? |
| form | what visual or textual representation makes the answer clearest? |

Higher altitude groups particulars into a whole. Lower altitude unpacks that unit into relationships, instances, or execution. Altitude is relative to the subject: a report about one operation treats that operation as its whole subject.

A complete map is not necessarily a high-altitude model. Abstract by naming the rule, relationship, or purpose that makes the parts understandable. Do not merely compress every part into fewer boxes. Preserve consequential boundaries while leaving execution details for the questions that need them.

Digits, jargon, length, and importance do not determine altitude. A system-wide total can be high altitude. A short command can be low altitude. Decisions can concern strategy or one operational choice. The same mechanism can need a broad model and a concrete sequence.

Page order need not descend monotonically. Put the main answer early, define necessary context, explain prerequisites before dependent claims, and place qualifications beside their claims. A strategic conclusion can follow a concrete example.

## ten candidate lenses

Consider all ten against the available material. These are candidate questions, not ranked altitudes or mandatory sections. One section can answer several lenses. One lens can recur at different altitudes if each treatment adds understanding.

| lens | reader question | added understanding and inclusion test | boundary and omission test |
| --- | --- | --- | --- |
| scope | what is this, and what does the answer cover? | identify the subject, necessary terms, and boundaries when the reader could misidentify them. | omit a separate treatment if the opening suffices. scope identifies the subject; limits qualify a claim. |
| state | what exists, what changed, and when? | distinguish proposed, completed, blocked, and historical states when the distinction matters. | omit for a timeless concept without relevant change. sequence does not establish cause. |
| structure | what are the parts, and how do they relate? | explain responsibilities, dependencies, ownership, or shared and separate records. | omit inventories that change nothing for this reader. arrangement is distinct from behavior. |
| mechanism | how does this work, or why did this happen? | explain a process, causal rule, or supported diagnosis when behavior matters. | omit irrelevant internals. label inferred causes and keep unknown causes unknown. |
| impact | what changes for whom, and why does it matter? | show relevant consequences, benefits, costs, or exposure. | omit inflated restatements and unsupported effects. keep projections conditional. |
| evidence | what supports this conclusion? | distinguish observation, measurement, assumption, and inference; make claims traceable. | a citation or inline qualification can suffice without a section. absent evidence is not evidence of absence. |
| limits | under what conditions does this answer hold? | expose prerequisites, exceptions, constraints, or failure conditions that change the conclusion. | omit generic caution. keep consequential limits beside the qualified answer, never only in a fold. |
| comparison | what is shared, and what meaningfully differs? | relate an unfamiliar subject to a known one, compare before and after, or distinguish real alternatives on useful criteria. | omit unsupported familiarity, decorative analogies, and invented alternatives. a comparison need not imply a choice. |
| decision | what should be chosen, by whom, and why? | supply a recommendation, criteria, or what would settle a real unresolved choice. | omit fabricated decisions for explanatory tasks. a decision may be strategic or operational. |
| action | what happens next, and what counts as complete? | give useful steps, ownership, and completion checks when someone needs to act. | omit compulsory next steps when understanding completes the task. test results belong with state or evidence. |

All claims need support and material qualifications, even when evidence and limits have no separate sections. A positive explanation needs no invented problem. An uncomplicated feature needs no fabricated internals, options, or appendix.

## make a compact content plan

Before HTML, save a short `files/report-plan.md` beside the report run. This is an authoring record, not another reader-facing report. For a small task, a few lines suffice.

1. Record the audience, purpose, and relevant prior knowledge once, with consequential assumptions.
2. For each useful answer, record its question or lenses, takeaway, source, altitude, depth boundary, and reader benefit.
3. Classify benefit as essential, useful, or none for this reader's task. Essential prevents a material misunderstanding of the answer, not an incomplete inventory of the subject. Useful adds a relevant distinction. None repeats, distracts, or exceeds the evidence.
4. Keep essential answers; merge or size useful answers; omit answers with no added benefit. For each answer with technical depth, distinguish the visible takeaway from optional subordinate questions. Evidence supporting an essential answer need not all remain expanded.
5. Order the main answer and its prerequisites. Identify the initial model this reader needs, if any, before tracing execution. Record consequential omissions, not a ten-row rejection ritual.
6. Only then choose visual forms using `references/visual-forms.md`. Add the visual relationship and its reader benefit to each selected answer, or a brief reason prose is clearer.

Do not expose private reasoning. The plan records decisions, supporting facts, and concise reasons. It does not require a chain-of-thought transcript or numerical benefit scores.

Stop gathering or adding detail when the reader has a supported answer. One or two lenses can complete a simple explanation. All ten are available for a complex subject, but complexity alone does not make every lens useful.

## build the report

Use `assets/questions-template.html` after the plan. It provides styles and components, not a section sequence. Remove unused components. Use reader-facing headings that answer the actual questions, not automatic lens labels.

The opening identifies the subject in ordinary language and states the supported finding or central explanation. Define necessary unfamiliar names where they become useful. If the opening needs a glossary of implementation terms, reconsider its abstraction before adding glossary cards. Keep the title to one clear claim; put its explanation in the thesis.

The first visual should make the main relationship understandable before asking the reader to evaluate its supporting detail. An evidence matrix can be accurate yet require too much synthesis at the opening. Use a compact table first when comparing familiar items or looking up exact values is the reader's immediate task. Otherwise establish the model before the inventory or detailed comparison.

For an unfamiliar feature, a useful initial model may explain the shared purpose and what changes from a familiar feature. A responsibility map may instead explain who does what. Select the relationship that answers this reader's first question, not the number of pull requests or components in the sources. Do not force an overview before an already-understood subject or a simple direct answer.

Construct the primary visual near the opening when the subject has a meaningful relationship. Continue visual explanation at the points where the reader needs it. A process, dependency, branch, comparison, state change, or layout should normally be shown, not narrated across paragraphs. Exact visual selection happens after content selection, but visual construction is a central part of the work.

### the opening and the folded sections

The opening is the visible page: eyebrow, title, thesis, one or two visuals, and the callout when one line must be remembered. It carries the main answer and the conditions that change it. With every fold closed, the page ends within two screens at 1280 by 900, and the render check fails a longer page. Shorten the opening by folding sections, never by removing a qualification from the claim it affects or by shrinking type.

Every section after the opening is a section fold: `<details class="section">` with the section headline in its `<summary>`. Closed, the page below the opening reads as a list of headlines. Open, the section reads as an ordinary part of the document at full width, with its prose, cards, figures, tables and diagrams, and it takes the space it needs. Do not move a section's content into a detail fold to shorten it. A section stays open in the authored state only when the opening cannot stand without it, and then its content belongs in the opening, within the limit.

A detail fold is a plain `<details>` card inside a section, with the compact card style. It holds optional depth beside the visible answer it extends: execution steps, validation rules, recovery branches, source audits. Place each beside the answer it extends, so readers choose depth within a section. Use a linked appendix for material that needs a separate reference. Preserve useful diagrams inside both kinds of fold. A technical investigation that needs implementation detail on its main path puts it in the first section fold, not in the opening.

Every fold headline, section or detail, states what the reader gets: the section's claim or the question it answers, in the reader's words, unique on the page. A lens name, "details", "evidence", "more", a two-word label, or a headline repeated from another fold fails the render check. The reader decides from the headline alone whether to open it. A brevity word in the request changes nothing, because this is already the shape.

For each fold, identify its question and reader. Delete material that serves neither. With every fold closed, the explanation must remain coherent and correct. With one section fold open, the reader should get a complete section, not an unstructured remainder. Do not add detail merely to populate a fold.

Separate qualifications from audit metadata. Keep a condition that changes the answer beside the claim, stated briefly. Commit lists, test inventories, and deployment checks belong in optional evidence unless they are the requested subject. Missing deployment evidence means availability is unknown, not that nothing is live.

Finish with the supported takeaway, decision, or action when useful. The ending may follow the section folds and counts toward the closed page. No new decisive fact should appear only in the ending. Then follow `references/delivery.md` for prose, provenance, rendering, and handoff.
