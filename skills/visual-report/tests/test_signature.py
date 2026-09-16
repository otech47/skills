import contextlib
from datetime import datetime, timezone
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


signature = load("stamp-signature")
flair = load("roll-flair")
REPORT = '<!doctype html><html><head><title>fixture</title></head><body><main><h1>fixture</h1>\n</main></body></html>'
FINALIZED = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)


class SignatureTests(unittest.TestCase):
    def test_idempotent_and_updates_metadata(self):
        first = signature.stamp(REPORT, "fixture-primary", finalized_at=FINALIZED)
        self.assertEqual(first, signature.stamp(first, "fixture-primary", finalized_at=FINALIZED))
        changed = signature.stamp(first, "fixture-replacement", finalized_at=FINALIZED)
        self.assertEqual(changed.count('id="report-signature"'), 1)
        self.assertNotIn("fixture-primary", changed)
        self.assertIn("fixture-replacement", changed)

    def test_primary_first_and_duplicates_removed(self):
        result = signature.stamp(REPORT, "fixture-primary", ["fixture-helper", "fixture-primary", "fixture-helper"], finalized_at=FINALIZED)
        self.assertLess(result.index("fixture-primary"), result.index("fixture-helper"))
        self.assertEqual(result.count("fixture-primary"), 1)
        self.assertEqual(result.count("fixture-helper"), 1)
        attributed = signature.stamp(REPORT, "fixture-primary", effort="high", contributors=[("fixture-reviewer", "audited", "xhigh")], finalized_at=FINALIZED)
        self.assertIn("created by <strong>fixture-primary</strong> &middot; high effort", attributed)
        self.assertIn("audited by <strong>fixture-reviewer</strong> &middot; xhigh effort", attributed)

    def test_metadata_is_escaped(self):
        result = signature.stamp(REPORT, '<script>alert("fixture")</script>', ["a & b"], finalized_at=FINALIZED)
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)
        self.assertIn("a &amp; b", result)

    def test_estimates_and_timestamp(self):
        result = signature.stamp(REPORT, session_tokens=123456, context_tokens=45000, finalized_at=FINALIZED)
        self.assertIn("session: ~123.5k tokens", result)
        self.assertIn("context: ~45k tokens", result)
        self.assertIn('<time datetime="2026-09-14T10:00+00:00">14 sep 2026 &middot; 10:00 UTC</time>', result)

        for count, label in [(999, "~999 tokens"), (1000, "~1k tokens"), (999950, "~1m tokens"), (11400000, "~11.4m tokens")]:
            self.assertEqual(signature.estimate(count), label)

    def test_unknown_metadata(self):
        result = signature.stamp(REPORT, finalized_at=FINALIZED)
        self.assertIn("created by <strong>unknown</strong>", result)
        self.assertIn("session: unknown", result)
        self.assertIn("context: unknown", result)
        self.assertNotIn("~", result)

    def test_real_main_boundary_required(self):
        source = '<html><head><script>const x = "</main>";</script></head><body></body></html>'
        with self.assertRaisesRegex(ValueError, "no </main>"):
            signature.stamp(source)
        result = signature.stamp(REPORT.replace("</main>", "</MAIN>"), finalized_at=FINALIZED)
        self.assertLess(result.index(signature.START), result.index("</MAIN>"))

    def test_flair_on_off_and_reapplication_preserve_signature(self):
        with tempfile.TemporaryDirectory(dir=os.environ["SIGNATURE_TEST_DIR"]) as directory:
            path = Path(directory) / "report.html"
            stamped = signature.stamp(REPORT, "fixture-primary", finalized_at=FINALIZED)
            path.write_text(stamped, encoding="utf-8")
            self.assertNotIn('class="colophon"', stamped)
            for _ in range(2):
                with contextlib.redirect_stdout(io.StringIO()):
                    flair.apply_to(path, "fixture quote", "fixture author")
                result = path.read_text(encoding="utf-8")
                self.assertEqual(result.count('class="colophon"'), 1)
                self.assertEqual(result.count('id="report-signature"'), 1)
                self.assertLess(result.index('class="colophon"'), result.index(signature.START))
                self.assertIn("fixture-primary", result)
            self.assertEqual(flair.strip_flair(result), stamped)
            restamped = signature.stamp(result, "fixture-primary", finalized_at=FINALIZED)
            self.assertEqual(restamped, result)

    def test_cli_rejects_negative_estimates_without_writing(self):
        with tempfile.TemporaryDirectory(dir=os.environ["SIGNATURE_TEST_DIR"]) as directory:
            path = Path(directory) / "report.html"
            path.write_text(REPORT, encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPTS / "stamp-signature.py"), str(path), "--session-tokens", "-1"], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("nonnegative", result.stderr)
            self.assertEqual(path.read_text(encoding="utf-8"), REPORT)

    def test_cli_stamps_local_timestamp_and_supplied_metadata(self):
        with tempfile.TemporaryDirectory(dir=os.environ["SIGNATURE_TEST_DIR"]) as directory:
            path = Path(directory) / "report.html"
            path.write_text(REPORT, encoding="utf-8")
            started = datetime.now().astimezone().replace(second=0, microsecond=0)
            result = subprocess.run([sys.executable, str(SCRIPTS / "stamp-signature.py"), str(path), "--model", "fixture-primary", "--also-model", "fixture-helper", "--effort", "high", "--contributor", "fixture-auditor", "audited", "xhigh", "--session-tokens", "1000", "--context-tokens", "500"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            rendered = path.read_text(encoding="utf-8")
            self.assertIn("created by <strong>fixture-primary</strong>", rendered)
            self.assertIn("assisted by <strong>fixture-helper</strong>", rendered)
            self.assertIn("audited by <strong>fixture-auditor</strong> &middot; xhigh effort", rendered)
            self.assertIn("session: ~1k tokens", rendered)
            self.assertIn("context: ~500 tokens", rendered)
            timestamp = rendered.split('<time datetime="', 1)[1].split('"', 1)[0]
            finalized = datetime.fromisoformat(timestamp)
            self.assertIsNotNone(finalized.utcoffset())
            self.assertLessEqual(started, finalized)
            self.assertLessEqual(finalized, datetime.now().astimezone())


if __name__ == "__main__":
    unittest.main()
