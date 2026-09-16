#!/usr/bin/env python3
import argparse
from datetime import datetime
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re


START = "<!-- report-signature:start -->"
END = "<!-- report-signature:end -->"


class MainEnd(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.lines = source.splitlines(keepends=True)
        self.main_end = None
        self.feed(source)

    def handle_endtag(self, tag):
        if tag == "main":
            line, column = self.getpos()
            self.main_end = sum(map(len, self.lines[:line - 1])) + column


def token_count(value):
    count = int(value)
    if count < 0:
        raise argparse.ArgumentTypeError("token estimates must be nonnegative")
    return count


def estimate(value):
    if value is None:
        return "unknown"
    if value >= 999950:
        number, unit = value / 1000000, "m"
    elif value >= 1000:
        number, unit = value / 1000, "k"
    else:
        return f"~{value} tokens"
    return f"~{number:.1f}".rstrip("0").rstrip(".") + unit + " tokens"


def stamp(source, model=None, also_models=(), session_tokens=None, context_tokens=None,
          finalized_at=None, effort=None, contributors=()):
    source = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n?",
                    "", source, flags=re.S)
    insertion = MainEnd(source).main_end
    if insertion is None:
        raise ValueError("report has no </main>")
    models = [(model or "unknown", "created", effort)]
    models.extend(contributors)
    models.extend((name, "assisted", None) for name in also_models)
    seen = set()
    lines = []
    for name, role, level in models:
        if name in seen:
            continue
        seen.add(name)
        effort_label = f"{level} effort" if level else "effort unknown"
        lines.append(f"<div>{escape(role)} by <strong>{escape(name)}</strong> &middot; {escape(effort_label)}</div>")
    date = finalized_at or datetime.now().astimezone()
    timestamp = date.isoformat(timespec="minutes")
    month = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")[date.month - 1]
    human_date = f"{date.day} {month} {date.year}"
    human_time = date.strftime("%H:%M %Z").strip()
    lines.append(f'<div style="margin-top:.35rem">session: {estimate(session_tokens)} &middot; context: {estimate(context_tokens)}</div>')
    lines.append(f'<div><time datetime="{escape(timestamp, quote=True)}">{human_date} &middot; {escape(human_time)}</time></div>')
    footer = (
        f'{START}\n<footer id="report-signature" aria-label="report signature" '
        'style="margin:1.2rem auto 0;max-width:100%;text-align:center;'
        'color:var(--ink-soft,currentColor);font-size:.72rem;line-height:1.6;'
        'overflow-wrap:anywhere">\n  '
        + '\n  '.join(lines)
        + f'\n</footer>\n{END}\n'
    )
    return source[:insertion] + footer + source[insertion:]


def main():
    parser = argparse.ArgumentParser(description="Stamp a report with caller-supplied session estimates.")
    parser.add_argument("report", type=Path)
    parser.add_argument("--model", help="primary model that generated the report")
    parser.add_argument("--effort", help="recorded effort level of the primary model")
    parser.add_argument("--contributor", action="append", nargs=3, default=[], metavar=("MODEL", "ROLE", "EFFORT"), help="another model, its role (audited, reviewed, assisted), and recorded effort; repeat as needed")
    parser.add_argument("--also-model", action="append", default=[], help="another model used in the session; repeat as needed")
    parser.add_argument("--session-tokens", type=token_count, help="approximate tokens used in this session")
    parser.add_argument("--context-tokens", type=token_count, help="approximate context length at finalization")
    parser.add_argument("--finalized-at", help="original finalization timestamp, including timezone; defaults to now")
    args = parser.parse_args()
    try:
        finalized_at = None
        if args.finalized_at:
            finalized_at = datetime.fromisoformat(args.finalized_at.replace("Z", "+00:00"))
            if finalized_at.tzinfo is None:
                raise ValueError("--finalized-at needs a timezone")
            finalized_at = finalized_at.astimezone()
        source = args.report.read_text(encoding="utf-8")
        result = stamp(source, args.model, args.also_model, args.session_tokens, args.context_tokens, finalized_at=finalized_at, effort=args.effort, contributors=args.contributor)
        args.report.write_text(result, encoding="utf-8")
    except (OSError, ValueError) as error:
        parser.exit(1, f"stamp-signature: {error}\n")
    print(f"signature stamped: {args.report}")


if __name__ == "__main__":
    main()
