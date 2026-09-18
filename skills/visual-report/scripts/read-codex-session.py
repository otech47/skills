#!/usr/bin/env python3
import argparse
from datetime import datetime
import json
from pathlib import Path


SESSIONS_ROOT = Path.home() / ".codex" / "sessions"


def parse_time(value):
    if not value:
        return None
    moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if moment.tzinfo is None:
        raise ValueError("timestamp needs a timezone")
    return moment


def read_session(path, before=None):
    models = {}
    meta = {}
    session_tokens = None
    processed_tokens = None
    context_tokens = None
    context_window = None
    with path.open(encoding="utf-8") as transcript:
        for line in transcript:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict):
                continue
            if before:
                moment = parse_time(row.get("timestamp"))
                if not moment or moment > before:
                    continue
            payload = row.get("payload")
            if not isinstance(payload, dict):
                continue
            kind = row.get("type")
            if kind == "session_meta":
                meta = payload
                continue
            if kind == "turn_context":
                model = payload.get("model")
                if not model:
                    continue
                level = payload.get("effort")
                if not isinstance(level, str):
                    level = "unknown"
                levels = models.setdefault(model, [])
                if level not in levels:
                    levels.append(level)
                continue
            usage = None
            if kind == "token_usage_record":
                thread = payload.get("thread_token_usage") or {}
                processed_tokens = thread.get("total_tokens", processed_tokens)
                usage = payload.get("usage")
            elif kind == "event_msg" and payload.get("type") == "token_count":
                info = payload.get("info") or {}
                thread = info.get("total_token_usage") or {}
                processed_tokens = thread.get("total_tokens", processed_tokens)
                usage = info.get("last_token_usage")
                context_window = info.get("model_context_window", context_window)
            else:
                thread = None
            if thread:
                fresh = (thread.get("input_tokens", 0) - thread.get("cached_input_tokens", 0)
                         - thread.get("cache_write_input_tokens", 0) + thread.get("output_tokens", 0))
                if thread.get("total_tokens") is not None:
                    session_tokens = fresh
            if usage and usage.get("total_tokens") is not None:
                context_tokens = usage["total_tokens"]
    return {
        "session_id": meta.get("id"),
        "parent_thread_id": meta.get("parent_thread_id"),
        "cwd": meta.get("cwd"),
        "models": [{"model": model, "efforts": levels} for model, levels in models.items()],
        "session_tokens": session_tokens,
        "processed_tokens": processed_tokens,
        "context_tokens": context_tokens,
        "model_context_window": context_window,
    }


def find_rollout(cwd):
    target = str(Path(cwd).resolve())
    candidates = sorted(SESSIONS_ROOT.glob("**/rollout-*.jsonl"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    for candidate in candidates:
        try:
            with candidate.open(encoding="utf-8") as transcript:
                row = json.loads(transcript.readline())
        except (OSError, json.JSONDecodeError):
            continue
        payload = row.get("payload") or {}
        if row.get("type") != "session_meta":
            continue
        if payload.get("source", {}).get("subagent") if isinstance(payload.get("source"), dict) else False:
            continue
        if payload.get("cwd") == target:
            return candidate
    return None


def main():
    parser = argparse.ArgumentParser(description="Read recorded Codex model, effort, and token use without printing conversation content.")
    parser.add_argument("transcript", type=Path, nargs="?", help="the session's rollout JSONL file")
    parser.add_argument("--find", metavar="CWD", help="locate the newest non-subagent rollout for a working directory")
    parser.add_argument("--before", help="report finalization timestamp, including timezone")
    args = parser.parse_args()
    try:
        before = parse_time(args.before) if args.before else None
        if args.find:
            found = find_rollout(args.find)
            if found is None:
                parser.exit(1, f"read-codex-session: no rollout found for {args.find}\n")
            print(found)
            return
        if not args.transcript:
            parser.error("give a rollout JSONL path or --find CWD")
        result = read_session(args.transcript, before)
    except (OSError, ValueError, TypeError) as error:
        parser.exit(1, f"read-codex-session: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
