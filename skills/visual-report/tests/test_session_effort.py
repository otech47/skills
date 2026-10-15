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

    def usage_row(self, message_id=None, output_tokens=1, timestamp="2026-09-15T10:00:00Z"):
        message = {"model": "claude-opus-5", "usage": {
            "input_tokens": 10, "output_tokens": output_tokens,
            "cache_read_input_tokens": 100, "cache_creation_input_tokens": 20,
        }}
        if message_id is not None:
            message["id"] = message_id
        return {"type": "assistant", "timestamp": timestamp, "message": message}

    def read_usage(self, rows, before=None):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "session.jsonl"
            path.write_text("\n".join(json.dumps(row) for row in rows))
            return effort.read_usage(path, before)

    def test_usage_keeps_last_snapshot_per_message_id(self):
        rows = [self.usage_row("a"), self.usage_row("b", 3), self.usage_row("a", 5)]
        self.assertEqual(self.read_usage(rows), {"session_tokens": 28, "processed_tokens": 268})

    def test_identical_usage_snapshots_count_once(self):
        row = self.usage_row("a", 5)
        self.assertEqual(self.read_usage([row, row]), {"session_tokens": 15, "processed_tokens": 135})

    def test_legacy_usage_without_message_ids_remains_independent(self):
        rows = [self.usage_row(), self.usage_row(), self.usage_row("a"), self.usage_row("a", 5)]
        self.assertEqual(self.read_usage(rows), {"session_tokens": 37, "processed_tokens": 397})

    def test_empty_and_null_message_ids_remain_independent(self):
        null_id = self.usage_row()
        null_id["message"]["id"] = None
        self.assertEqual(self.read_usage([null_id, null_id, self.usage_row("")]),
                         {"session_tokens": 33, "processed_tokens": 393})

    def test_usage_cutoff_selects_last_snapshot_before_finalization(self):
        before = datetime(2026, 9, 15, 12, tzinfo=timezone.utc)
        rows = [self.usage_row("a"),
                self.usage_row("a", 3, "2026-09-15T11:00:00Z"),
                self.usage_row("a", 100, "2026-09-15T13:00:00Z")]
        self.assertEqual(self.read_usage(rows, before), {"session_tokens": 13, "processed_tokens": 133})

    def test_missing_usage_does_not_erase_the_last_snapshot(self):
        row = self.usage_row("a")
        del row["message"]["usage"]
        self.assertEqual(self.read_usage([self.usage_row("a", 5), row]),
                         {"session_tokens": 15, "processed_tokens": 135})

    def test_missing_usage_stays_unknown(self):
        self.assertEqual(self.read_usage([self.row()]), {"session_tokens": None, "processed_tokens": None})


if __name__ == "__main__":
    unittest.main()
