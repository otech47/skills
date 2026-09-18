import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from datetime import datetime, timezone

spec = importlib.util.spec_from_file_location("effort", Path(__file__).parents[1] / "scripts/read-session-effort.py")
effort = importlib.util.module_from_spec(spec)
spec.loader.exec_module(effort)


class SessionEffortTest(unittest.TestCase):
    def read(self, rows, before=None):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "session.jsonl"
            path.write_text("\n".join(json.dumps(row) for row in rows) + '\n{"unfinished":')
            return effort.read_effort(path, before)

    def row(self, level=None, override=None, timestamp="2026-09-15T10:00:00Z"):
        return {"type": "assistant", "timestamp": timestamp, "message": {"model": "claude-opus-5"},
                "effort": level, "perTurnEffort": override}

    def test_recorded_effort_and_null_override(self):
        self.assertEqual(self.read([self.row("xhigh"), self.row("xhigh")]),
                         [{"model": "claude-opus-5", "efforts": ["xhigh"]}])

    def test_override_and_changes_are_preserved(self):
        self.assertEqual(self.read([self.row("high", "max"), self.row("xhigh")])[0]["efforts"], ["max", "xhigh"])

    def test_missing_metadata_stays_unknown(self):
        self.assertEqual(self.read([self.row()])[0]["efforts"], ["unknown"])
        self.assertEqual(self.read([{"type": "user", "effort": "max"}]), [])

    def test_synthetic_rows_are_not_models(self):
        synthetic = {"type": "assistant", "timestamp": "2026-09-15T10:00:00Z",
                     "message": {"model": "<synthetic>"}, "effort": "unknown"}
        self.assertEqual(self.read([synthetic]), [])

    def test_usage_counts_fresh_and_processed(self):
        def usage_row(i, o, cr=0, cw=0, timestamp="2026-09-15T10:00:00Z"):
            return {"type": "assistant", "timestamp": timestamp,
                    "message": {"model": "claude-opus-5",
                                "usage": {"input_tokens": i, "output_tokens": o,
                                          "cache_read_input_tokens": cr,
                                          "cache_creation_input_tokens": cw}}}
        with TemporaryDirectory() as directory:
            path = Path(directory) / "session.jsonl"
            path.write_text("\n".join(json.dumps(r) for r in [usage_row(100, 50, 900, 200), usage_row(200, 80, 950, 0)]))
            result = effort.read_usage(path)
        self.assertEqual(result["session_tokens"], 430)
        self.assertEqual(result["processed_tokens"], 2480)

    def test_later_turns_do_not_rewrite_historical_effort(self):
        before = datetime(2026, 9, 15, 12, tzinfo=timezone.utc)
        self.assertEqual(self.read([self.row("high"), self.row("max", timestamp="2026-09-16T10:00:00Z")], before)[0]["efforts"], ["high"])


if __name__ == "__main__":
    unittest.main()
