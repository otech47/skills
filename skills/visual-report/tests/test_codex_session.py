import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from datetime import datetime, timezone

spec = importlib.util.spec_from_file_location("codex_session", Path(__file__).parents[1] / "scripts/read-codex-session.py")
codex_session = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codex_session)

META = {"type": "session_meta", "timestamp": "2026-09-15T09:00:00Z",
        "payload": {"id": "abc", "parent_thread_id": None, "cwd": "/tmp/proj"}}


def turn(model, effort, timestamp="2026-09-15T10:00:00Z"):
    return {"type": "turn_context", "timestamp": timestamp,
            "payload": {"model": model, "effort": effort}}


def usage_record(thread_input, cached, output, total, context, timestamp="2026-09-15T10:00:00Z"):
    return {"type": "token_usage_record", "timestamp": timestamp,
            "payload": {"thread_token_usage": {"input_tokens": thread_input, "cached_input_tokens": cached,
                                               "cache_write_input_tokens": 0, "output_tokens": output,
                                               "total_tokens": total},
                        "usage": {"total_tokens": context}}}


class CodexSessionTest(unittest.TestCase):
    def read(self, rows, before=None):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "rollout.jsonl"
            path.write_text("\n".join(json.dumps(row) for row in rows) + '\n{"unfinished":')
            return codex_session.read_session(path, before)

    def test_fresh_excludes_cache_reads(self):
        result = self.read([META, turn("gpt-x", "high"),
                            usage_record(1000, 700, 100, 1100, 500),
                            usage_record(3000, 2100, 300, 3300, 900)])
        self.assertEqual(result["session_tokens"], 1200)
        self.assertEqual(result["processed_tokens"], 3300)
        self.assertEqual(result["context_tokens"], 900)

    def test_models_and_efforts_deduped_in_order(self):
        result = self.read([META, turn("gpt-x", "high"), turn("gpt-x", "high"), turn("gpt-y", "low")])
        self.assertEqual(result["models"], [{"model": "gpt-x", "efforts": ["high"]},
                                            {"model": "gpt-y", "efforts": ["low"]}])

    def test_before_filters_later_rows(self):
        before = datetime(2026, 9, 15, 12, tzinfo=timezone.utc)
        result = self.read([META, turn("gpt-x", "high"),
                            usage_record(1000, 700, 100, 1100, 500),
                            turn("gpt-x", "low", "2026-09-16T10:00:00Z"),
                            usage_record(9000, 8000, 500, 9500, 2000, "2026-09-16T10:00:00Z")], before)
        self.assertEqual(result["models"], [{"model": "gpt-x", "efforts": ["high"]}])
        self.assertEqual(result["session_tokens"], 400)

    def test_legacy_token_count_event(self):
        event = {"type": "event_msg", "timestamp": "2026-09-15T10:00:00Z",
                 "payload": {"type": "token_count",
                             "info": {"total_token_usage": {"input_tokens": 1000, "cached_input_tokens": 700,
                                                            "cache_write_input_tokens": 0, "output_tokens": 100,
                                                            "total_tokens": 1100},
                                      "last_token_usage": {"total_tokens": 500},
                                      "model_context_window": 258400}}}
        result = self.read([META, event])
        self.assertEqual(result["session_tokens"], 400)
        self.assertEqual(result["processed_tokens"], 1100)
        self.assertEqual(result["model_context_window"], 258400)


if __name__ == "__main__":
    unittest.main()
