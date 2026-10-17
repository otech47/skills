---
name: visual-report
description: >-
  Produce a designed, self-contained local HTML report for an explanation, investigation, audit, architecture walkthrough, comparison, plan, or research summary that needs sustained reading. Use on explicit visual-report or HTML-report requests, or when several related parts, diagrams, or tables make a terminal answer hard to understand. Keep genuinely short answers and live debugging in chat. Supports legacy mode and independent mode comparisons on request.
user-invocable: true
---

# visual report

Build a visual explanation for an identified reader. Keep the report local unless this request authorizes publication.

## choose the output

For an explicit video explainer, narrated walkthrough, or request to turn a report into a video, read `../explain-with-video/SKILL.md`. Video-only requests use its compact HTML player page. When a report includes video, embed a playable `<video>` directly in that report and follow both formats' checks. Share the factual brief and link the HTML first. An MP4 link or a link to a separate player does not satisfy embedding in a report. Ordinary visual-report requests and requests to explain something visually retain HTML output without video production.

## choose one mode before drafting

| request | route |
| --- | --- |
| visual report, with no mode specified, or questions mode | **questions**, the default: read `references/questions.md`, `references/visual-forms.md`, and `references/delivery.md` completely. |
| explicit request for legacy mode, sequence mode, original mode, or the old way | **sequence**: read `references/legacy.md` and follow its loading instructions. |
| both versions, compare modes, or blind evaluation | read `references/comparison.md` before selecting questions, outlining, or drafting. Freeze the common inputs and give each mode to a separate fresh-context agent. Do not create the second report in the first author's context. |

read only the selected route and the dependencies it directs you to use. a normal questions-mode report does not load legacy or mode-comparison instructions. do not scan every reference or combine the two composition methods.

mode selection applies to this report only. `questions` remains the default for later requests. "make a visual report in legacy mode" and "make both versions" need no global settings change.

## common output contract

- One self-contained HTML report with inline assets, supported claims, meaningful source links, and readable light and dark palettes.
- Visuals explain the subject, not the author's workflow. A colored paragraph card is not a relationship diagram.
- The reader can identify the subject and main answer from the first screen without this conversation.
- Keep material qualifications with the claims they affect. Optional detail cannot conceal a contradiction in the headline or diagram.
- Verify the final rendered bytes, including wide and narrow screenshot review. A successful HTML write is not a completed report.
- Hand off the local link and a brief gist. Do not repeat the report in chat.

Mode-specific instructions define content selection and composition. Render helpers, style toggles, and permission boundaries remain shared. Backup and evaluation provenance belong in the scratch manifest or evaluation record, not the report body.
