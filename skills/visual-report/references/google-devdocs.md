# Google developer documentation style

This file is the whole rule set, transcribed from developers.google.com/style. It is offline and self-contained. Do not fetch that site, and do not search for the guide: the table below is what applies, and a network call would only slow the report down.

Applies to the prose in a visual report: the thesis, body copy, callouts, captions, table cells, headings, and summaries. It does not apply to code, commands, config values, log lines, proper nouns, or numbers. Those stay verbatim.

**Toggle:** this file's presence is the whole switch. Run `report-style google|ast100|off|status` (`~/.local/bin/report-style`). It renames this file to `google-devdocs.md.off` and back, and guarantees at most one style file is active. If you are reading this file, Google style is on for this report. Apply the table below. If it is missing from the visual-report skill directory, it is off, so write in the report's normal voice per the rest of this skill and skip this file entirely.

## Rules to apply while drafting

| Rule | Do | Don't |
|---|---|---|
| Second person | Address the reader as "you". Name the actor for anyone else | "the user", "we", "one", an unnamed actor |
| Active voice | "The guardians count the signatures." | "The signatures are counted." Passive with no actor |
| Passive only on purpose | Passive when the object is the point ("the file is saved") or the actor is irrelevant ("the database was purged in january") | Passive to soften who broke what |
| Present tense | "The job fails when the token expires." | "The job will fail" / "had failed" for a standing fact |
| Conditions first | "To withdraw exact sats, use door 2." "If the key is missing, restore from seed." | Instruction first, condition trailing after the comma |
| Sentence length | Under 26 words. Break walls of text so the page scans | Nested exceptions and stacked subordinate clauses |
| No double negatives | "You can continue without a path." | "A missing path won't prevent you from continuing." |
| Plain words | start, use, before, about | commence, utilize, prior to, a number of, phrasal verbs like "makes use of" |
| One term per thing | Pick the noun and reuse it everywhere, same capitalization | Rotating synonyms so the reader wonders if two things are meant |
| Keep the helper words | "if the vm has started and if you can connect", "if not found, then the default is returned" | Dropping "that", "then", or a repeated "if" to save a word |
| Antecedents | Name the thing again when "it" could point at two nouns | "make sure that it's targeted" |
| Modifier placement | "request only one token", "a cloud-native pipeline in a hybrid environment" | "only request one token", stacked modifiers that regroup ("a hybrid cloud-native pipeline") |
| Sentence case headings | "why exact sats need new machinery" | Title Case Or ALL CAPS headings |
| Numbered vs bulleted | Numbered list for a sequence of steps. Bulleted list for everything else. Parallel grammar within a list | A sequence buried in a paragraph. Mixed sentence shapes down one list |
| Serial comma | "guardians, members, and the server" | "guardians, members and the server" |
| Code font | Code font for identifiers, commands, paths, values, and field names | Code font as emphasis. Bare identifiers in running prose |
| Placeholders | Uppercase with underscores: `FEDERATION_ID` | `<your-federation-id>`, `foo` |
| UI elements in bold | "click **Save**" | "click the save button", "click the bell icon" with no label |
| No directional language | "in the preceding diagram", "the following table", "earlier in this report" | "above", "below", "on the right-hand side" |
| Link text carries meaning | Link the thing named: "see the aggregate-key report" | "click here", "read this document" |
| Unambiguous dates | 2026-08-17, or 17 august 2026 | 08/17/26 |
| Global audience | Literal words in their primary sense. Diverse, neutral examples | Idioms, humor, seasonal or culture-specific references, pop-culture nods |
| No difficulty claims | State the steps and let them speak | "simply", "just", "easy", "obviously", "of course" |
| Conversational, not frivolous | Direct and friendly, like explaining it at a desk | Buzzwords, cliches, exclamation marks, figurative language, "please note", dry legalese |
| No "please" in instructions | "To view the document, click **View**." | "Please click **View**." |

## What to leave untouched

- Code, commands, config values, log lines: verbatim.
- Proper nouns, product names, error strings: verbatim.
- Numbers, dates, metrics: as measured.

## Where this yields to the house style

The `prose-style` skill still wins on voice: lowercase to match his writing, no em dashes, no narration of the conversation that produced the report. So sentence case headings become his lowercase, and any Google example that reads corporate gets said plainly instead. Google style governs sentence construction here, not capitalization of the report's voice.

## How to apply it

1. Draft the point first. Then check it against the table, sentence by sentence.
2. Fix a violation without losing a fact, a condition, or an exception.
3. If a sentence already complies, leave it. Do not rewrite a sentence that is already clear.

Run this pass together with the `prose-style` audit already required before a report ships, not as a separate pass.
