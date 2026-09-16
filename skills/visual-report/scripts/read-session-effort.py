#!/usr/bin/env python3
import argparse
from datetime import datetime
import json
from pathlib import Path


def read_effort(path, before=None):
    models = {}
    with path.open(encoding="utf-8") as transcript:
        for line in transcript:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict) or row.get("type") != "assistant":
                continue
            if before:
                timestamp = row.get("timestamp")
                if not timestamp or datetime.fromisoformat(timestamp.replace("Z", "+00:00")) > before:
                    continue
            message = row.get("message") or {}
            model = message.get("model", "unknown")
            level = row.get("perTurnEffort") or row.get("effort") or "unknown"
            if not isinstance(level, str):
                level = "unknown"
            levels = models.setdefault(model, [])
            if level not in levels:
                levels.append(level)
    return [{"model": model, "efforts": levels} for model, levels in models.items()]


def main():
    parser = argparse.ArgumentParser(description="Read recorded Claude Code effort without printing conversation content.")
    parser.add_argument("transcript", type=Path, help="the exact session's JSONL file")
    parser.add_argument("--before", help="report finalization timestamp, including timezone")
    args = parser.parse_args()
    try:
        before = datetime.fromisoformat(args.before.replace("Z", "+00:00")) if args.before else None
        if before and before.tzinfo is None:
            raise ValueError("--before needs a timezone")
        result = read_effort(args.transcript, before)
    except (OSError, ValueError, TypeError) as error:
        parser.exit(1, f"read-session-effort: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
