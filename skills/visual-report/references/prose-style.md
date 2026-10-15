---
name: prose-style
description: For auditing prose (markdown, PR descriptions, READMEs, issue bodies). Use when you've finished editing prose and are about to stop, or when writing prose initially.
---

# Prose Style

Prose written by an LLM has a tell. Polished transitions, generic framing, summary-heavy paragraphs, code-speak narration. This skill is the audit pass that strips those tells out.

The reader is a teammate skimming a diff or a description, not a stranger reading marketing copy. Write like someone close to the work, not someone packaging it for broad consumption. Specifically: not a published essay, not an op-ed, not a release note, not an architecture memo.

## Scope

Audit one named artifact or one cohesive set that will ship together. Do not batch unrelated PRs, branches, documents, or messages into one pass.

Use the final artifact, not a remembered draft. For a PR, audit the exact title and body file immediately before publication. If this pass changes the artifact, inspect the new final form once more.

## The default is terse

Compress harder than feels comfortable. If one sentence can replace three, use one. If a bullet can replace a paragraph, use a bullet. If the title and surrounding context already say it, cut it.

## Pre-existing prose, do not overwrite on sight

Prose that was already in the file may encode tone, context, or deliberate stylistic choices the user made. Default: leave it alone. Only rewrite if your change made it factually wrong, or the section it described is gone. When in doubt, leave it.

## Delete or rewrite any prose that does any of these

Applies to prose you are writing or touching in this task.

### (a) Uses em or en dashes

Do not use em dashes (U+2014) or en dashes (U+2013) in any file content you write (markdown, PR descriptions, READMEs, code comments, commit messages, issue bodies). They are the strongest LLM tell in written artifacts. Replace with a regular hyphen-minus (`-`) or restructure. A comma, a period, or parentheses almost always reads cleaner than a dash anyway.

Chat replies carry the same rule. The global CLAUDE.md prose section enforces it there, so this audit does not re-scan conversational replies.

### (b) Uses polished LLM transitions

Words and phrases that mark the prose as machine-generated, even when the content is correct.

Cut these:

- "Furthermore", "Moreover", "Additionally", "In addition", "What's more"
- "In summary", "To summarize", "Overall", "Ultimately"
- "It's worth noting that", "It's important to note", "Note that" (as filler)
- "This change ensures that", "This approach allows for", "This enables"
- "Robust", "seamless", "leverage", "utilize" (when "use" works), "comprehensive"
- "We've", "We can", "We will" (when describing what the diff does, write it directly)

If the sentence still makes sense after deleting the transition, it didn't need the transition.

### (c) Code-speak narration

Prose that strings together identifiers instead of describing what the system does.

```md
BAD
The `availableTests` array is filtered against the `currentState` ledger,
then the resulting subset is fed into `fixturesByToken` which dispatches
to the corresponding handler.

BETTER
Each agent picks a test it hasn't run yet, claims a fixture, and runs it.
```

The reader should follow the description without recognizing a single symbol. Identifiers appear only to help the reviewer locate something in the diff, never as the load-bearing nouns of the sentence.

### (d) Summary-heavy or framing-heavy prose

```md
BAD
This PR introduces a series of changes designed to improve the testing
infrastructure. The changes span multiple files and are intended to
provide a more robust foundation for future work.

BETTER
Splits the test fixture pool so two agents can run concurrently without
clobbering each other's state.
```

Generic framing (`This PR introduces`, `a series of changes`, `designed to`, `provide a foundation for`) is content-free. Lead with the concrete change.

### (e) Restates the obvious

If the heading or surrounding context already says it, the sentence is a tax on the reader.

```md
BAD
## Testing
This section describes how the change was tested.

BETTER
## Testing
- ran the smoke suite locally, all green
- triggered CI run #12345, passed
```

### (f) Joins loosely-related clauses with heavy punctuation

Semicolons, colons, and parentheticals (and em dashes, banned above) make a structural claim: the second clause directly expands or contrasts the first. If a reader would stop and wonder "why are these together?", the joiner is lying.

When you reach for one, do one of these instead:

- break into two sentences and trust the reader to make the link
- delete the second clause (usually filler: `X, which is incorrect` becomes `X`)
- use comma + coordinator if the link is conversational (`X, and Y`)

Compound-clause prose is what makes LLM writing feel "off" even when no single sentence is wrong. Banning em dashes alone just routes the urge to the next available joiner.

### (g) Hard-wraps prose at a column limit

Markdown soft-wraps, so a paragraph split into ~80-column lines just makes diffs noisy. Write one line per paragraph.

### (h) Narrates its own production

The artifact is the deliverable, not a log of how it was produced. The reader was not in the room. Don't record what you and the user discussed, decisions already settled before you started writing, the methodology you followed, why you shaped it this way, what you sourced from, or a caption on your own edits.

**The tell:** the sentence only makes sense to someone who watched this session.

- sourcing or attribution: "per our discussion", "from the email thread", "Source: notes.md", "(moved from the open column)"
- temporal markers: "as of this week", "still broken on main", "one meeting in", "early draft, not final"
- methodology narration: "we are keeping this note even though it is out of scope", "every doc needs this section"
- retracing your steps: "rebuilt", "refreshed", "previous version", "now generic"

When a marker like that is present, cut the sentence or rewrite it as the plain fact.

The marker-free form is the common one, and it reads as a plain fact about the subject: "the default shell retains the full development environment", "all ten chapters, not three", "supersedes #12236", "prices checked 16 sep 2026", "test first, the e2e suite does not cover these paths". Markers do not catch it. Two tests do. Name the reader of this artifact in a phrase (a developer new to the repo, a client, a PR reviewer, the family), then ask of each sentence: does it point at something that reader can find in the artifact or in their own world (the referent test), and is it about the subject rather than about the writer's choice, ranking, proposal, or confidence (the subject test)? A request constraint restated as a promise kept, a decision with its losing side attached, a comparison with a version the reader never had, and a note on what is still unconfirmed all fail. Delete the sentence or state the end state. A sentence that says what the document covers, a stated limit on the evidence, or a date the reader needs to weigh a measurement passes.

```md
BAD
Field validation is out of scope for v1, since every spec needs a non-goals
section and this is just an early draft to react to, not a final call.
Source: the planning notes, as of last week.

BETTER
Field validation is out of scope for v1.
```

Incorporate the user's guidance to produce a clean result. Don't transcribe the guidance into the artifact. A design doc is not a narrative of the discussion that produced it. A PR description is not a log of the session that wrote the code. If you are explaining why the document is shaped the way it is, delete that and let the shape speak.

### (i) Mannered prose

Anthropic's own definition, from the Fable 5.1 prompting guide:

> Mannered prose substitutes metaphor and flourish for direct statement. Instead of "a parameter worth varying," the mannered writer produces "a dial worth turning." Instead of "this point still matters," they write "this point earns its keep." The phrases exist to display the writer, not to convey the idea, and readers can tell. That is why mannered prose irritates: it makes the reader work harder so the writer can perform. It is also imprecise. Metaphors drag in connotations the writer did not choose and cannot control. The fix is to say what you mean. When a literal phrase is available, use it.

The tell is a phrase whose literal paraphrase is shorter and says the same thing. "Load-bearing", "does the heavy lifting", "quietly", "earns its keep", "a dial worth turning", "the shape of the problem", "lives in", "the story here is". Each one has a literal version with fewer connotations.

```md
BAD
The retry budget is the load-bearing knob here, and it quietly earns its keep
under bursty load.

BETTER
The retry budget is the setting that matters. It prevents failures under bursty load.
```

Remove all of it. When a literal phrase is available, use it.

## Keep prose that does any of these

### Names the symptom in plain language

For reactive work (bug fix, regression, build break), lead with what the reader would observe. "When you tap the wallet tab, the wallet switcher opens instead of the wallet." Not "the `WalletTabPress` handler dispatches to the wrong route."

### Adds context the reviewer cannot derive from the diff

Hidden constraints, external decisions, why this approach over another, links to relevant issues or specs. Anything that explains *why* this change exists in the form it does.

### Cites a concrete fact

A number, a date, an error message, a link, a commit SHA, a stack trace. Concrete beats abstract every time.

## Voice

- short sentences over long ones
- specific nouns over abstract ones
- active voice over passive ("the migration runs" not "the migration is run")
- "I", "you", "we" are fine when they refer to real people doing real things, but cut "we" when it just means "the code"
- slightly rough is better than polished; sound like a hands-on engineer at standup

## The audit pass

Review each block of prose you added or touched:

1. Any em or en dashes? Replace with regular hyphens or restructure.
2. Any semicolon, colon, or parenthetical joining two clauses? Check the second is a direct expansion of the first. If not, break or delete.
3. Any polished transitions or generic framing? Cut.
4. Does the prose name behavior or does it list identifiers? Rewrite in behavioral terms.
5. Could the same point be made in fewer sentences? Compress.
6. Any paragraph hard-wrapped at a column limit? Reflow to one line.
7. Could a reader who has not seen the diff follow it? If no, rewrite.
8. Does any sentence only make sense to someone who was in this session: sourcing, decisions already made, methodology, temporal markers, or a caption on your own edits? Cut it or rewrite as the plain fact.
9. Any metaphor or flourish standing in for a literal statement? Replace it with the literal phrase.

Apply any fixes directly. Report what you removed or rewrote in one line if changes were needed. Otherwise stay silent.
