import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("comparison", ROOT / "scripts/prepare-comparison.py")
comparison = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(comparison)
MODELS = ["claude-opus-5-5:xhigh", "gpt-6.1-sol:xhigh"]


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        base = os.environ.get("COMPARISON_TEST_DIR", str(ROOT.parent))
        self.temporary = tempfile.TemporaryDirectory(prefix="comparison-test-", dir=base)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.packet = self.root / "packet"
        self.packet.mkdir()
        self.put(self.packet / "facts.md", "frozen facts\n")
        self.put(self.packet / "nested/evidence.json", '{"observed": true}\n')
        self.task = self.root / "task.md"
        self.put(self.task, "explain the supplied facts for a new reader\n")
        self.stage = self.root / "stage"
        self.original = self.root / "original"
        self.output = self.root / "prepared"
        self.put(self.stage / "references/sequence.md", "original guide: references/information-hierarchy.md\n")
        self.put(self.original / "SKILL.md", "original guide: references/information-hierarchy.md\n")
        self.put(self.stage / "references/questions.md", "assigned questions guide\n")
        self.put(self.stage / "references/visual-forms.md", "visual forms\n")
        self.put(self.stage / "references/delivery.md", "delivery\n")
        self.put(self.stage / "references/render-checks.md", "render checks\n")
        self.put(self.stage / "references/prose-style.md", "frozen prose guidance\n")
        self.put(self.stage / "references/google-devdocs.md", "active style\n")
        self.put(self.stage / "references/ast100.md.off", "inactive style\n")
        self.put(self.stage / "references/flair-chrome.md", "flair instructions\n")
        self.put(self.stage / "references/comparison.md", "private comparison procedure\n")
        self.put(self.stage / "SKILL.md", "router reveals both modes\n")
        self.put(self.original / "references/information-hierarchy.md", "original hierarchy\n")
        self.put(self.stage / "references/information-hierarchy.md", "original hierarchy\n")
        template = (ROOT / "assets/report-template.html").read_bytes()
        self.put(self.original / "assets/report-template.html", template)
        self.put(self.stage / "assets/report-template.html", template)
        self.put(self.stage / "assets/questions-template.html", template)
        for name in comparison.SCRIPTS:
            self.put(self.stage / "scripts" / name, f"fixture {name}\n")
        self.put(self.stage / "scripts/package.json", '{"dependencies":{"fixture-runtime":"1.0.0"}}')
        self.put(self.stage / "scripts/node_modules/fixture-runtime/package.json", '{"version":"1.0.0"}')
        self.put(self.stage / "scripts/node_modules/fixture-runtime/cli.js", "runtime\n")
        bin_dir = self.stage / "scripts/node_modules/.bin"
        bin_dir.mkdir()
        (bin_dir / "fixture-runtime").symlink_to("../fixture-runtime/cli.js")
        self.put(self.stage / "scripts/prepare-comparison.py", "private helper\n")
        self.put(self.stage / "tests/test_comparison.py", "private tests\n")

    def put(self, path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode() if isinstance(content, str) else content)

    def prepare(self):
        path = comparison.prepare(self.packet, self.output, MODELS, self.task,
                                  skill_root=self.stage, original_root=self.original)
        return json.loads(path.read_text())

    def test_four_cells_have_identical_frozen_inputs_and_private_mapping(self):
        manifest = self.prepare()
        runs = manifest["runs"]
        self.assertEqual(len(runs), 4)
        self.assertEqual({run["label"] for run in runs}, set("ABCD"))
        self.assertEqual(len({run["id"] for run in runs}), 4)
        self.assertEqual({(run["model"], run["mode"]) for run in runs},
                         {(model.split(":")[0], mode) for model in MODELS for mode in ("sequence", "questions")})
        inputs = []
        for run in runs:
            root = Path(run["cwd"])
            self.assertRegex(run["id"], r"^[a-f0-9]{24}$")
            self.assertEqual(run["effort"], "xhigh")
            self.assertEqual(run["status"], "prepared")
            self.assertEqual(Path(run["raw_report"]), root / "outputs/report.html")
            self.assertFalse(Path(run["raw_report"]).exists())
            self.assertFalse(list(root.rglob("manifest.json")))
            self.assertFalse(list(root.rglob("comparison.md")))
            inputs.append(comparison.tree_hashes(comparison.tree_snapshot(root / "input")))
            self.assertEqual(inputs[-1], run["hashes"]["input"])
            self.assertEqual((root / "input/task.md").read_bytes(), self.task.read_bytes())
            self.assertEqual((root / "runner.md").read_text(), comparison.RUNNER)
            self.assertEqual(run["hashes"]["skill"], comparison.tree_hashes(comparison.tree_snapshot(root / "skill")))
        self.assertTrue(all(value == inputs[0] for value in inputs))
        self.put(self.packet / "facts.md", "changed after preparation")
        self.assertTrue(all((Path(run["cwd"]) / "input/packet/facts.md").read_text() == "frozen facts\n" for run in runs))
        self.assertEqual(stat.S_IMODE((self.output / "coordinator").stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE((self.output / "coordinator/manifest.json").stat().st_mode), 0o600)

    def test_each_author_has_only_its_guide_and_required_files(self):
        for run in self.prepare()["runs"]:
            skill = Path(run["cwd"]) / "skill"
            mode = run["mode"]
            self.assertEqual((skill / "guide.md").read_bytes(), (self.stage / "references" / f"{mode}.md").read_bytes())
            self.assertEqual((skill / "SKILL.md").read_bytes(), (skill / "guide.md").read_bytes())
            self.assertNotIn("router reveals both modes", (skill / "SKILL.md").read_text())
            self.assertFalse((skill / "references/sequence.md").exists())
            self.assertFalse((skill / "references/questions.md").exists())
            self.assertFalse((skill / "tests").exists())
            self.assertFalse((skill / "scripts/prepare-comparison.py").exists())
            self.assertTrue((skill / "references/google-devdocs.md").exists())
            self.assertEqual((skill / "references/prose-style.md").read_text(), "frozen prose guidance\n")
            self.assertIn("skill/references/prose-style.md", (skill.parent / "runner.md").read_text())
            self.assertFalse((skill / "references/ast100.md.off").exists())
            self.assertFalse((skill / "references/flair-chrome.md").exists())
            self.assertTrue((skill / "references/flair-chrome.md.off").exists())
            self.assertFalse(any(path.is_symlink() for path in skill.rglob("*")))
            self.assertEqual((skill / "scripts/node_modules/.bin/fixture-runtime").read_text(), "runtime\n")
            if mode == "sequence":
                self.assertEqual((skill / "assets/report-template.html").read_bytes(), (self.original / "assets/report-template.html").read_bytes())
                self.assertTrue((skill / "references/information-hierarchy.md").exists())
                self.assertFalse((skill / "references/delivery.md").exists())
                self.assertFalse((skill / "references/visual-forms.md").exists())
                self.assertFalse((skill / "assets/questions-template.html").exists())
            else:
                self.assertTrue((skill / "references/delivery.md").exists())
                self.assertTrue((skill / "references/visual-forms.md").exists())
                self.assertTrue((skill / "assets/questions-template.html").exists())
                self.assertFalse((skill / "references/information-hierarchy.md").exists())
                self.assertFalse((skill / "assets/report-template.html").exists())

    def test_one_model_prepares_both_modes(self):
        path = comparison.prepare(self.packet, self.output, MODELS[:1], self.task,
                                  skill_root=self.stage, original_root=self.original)
        runs = json.loads(path.read_text())["runs"]
        self.assertEqual(len(runs), 2)
        self.assertEqual({run["mode"] for run in runs}, {"sequence", "questions"})
        self.assertEqual({run["label"] for run in runs}, {"A", "B"})
        self.assertEqual({run["model"] for run in runs}, {"claude-opus-5-5"})

    def test_preparation_needs_no_external_original_backup(self):
        self.original.rename(self.root / "unavailable-original")
        path = comparison.prepare(self.packet, self.output, MODELS[:1], self.task, skill_root=self.stage)
        manifest = json.loads(path.read_text())
        self.assertIsNone(manifest["sources"]["original_verification_root"])
        sequence = next(run for run in manifest["runs"] if run["mode"] == "sequence")
        self.assertEqual(Path(sequence["guide"]).read_bytes(), (self.stage / "references/sequence.md").read_bytes())

    def test_optional_backup_verifies_hierarchy_and_template_bytes(self):
        for name in ("references/information-hierarchy.md", "assets/report-template.html"):
            with self.subTest(name=name):
                target = self.original / name
                original = target.read_bytes()
                self.put(target, original + b"\nchanged\n")
                try:
                    with self.assertRaisesRegex(ValueError, "preserved original"):
                        self.prepare()
                    self.assertFalse(self.output.exists())
                finally:
                    self.put(target, original)

    def test_duplicate_models_are_rejected_even_with_different_efforts(self):
        with self.assertRaisesRegex(ValueError, "distinct models"):
            comparison.prepare(self.packet, self.output,
                               ["gpt-6.1-sol:high", "gpt-6.1-sol:xhigh"], self.task,
                               skill_root=self.stage, original_root=self.original)
        self.assertFalse(self.output.exists())

    def test_refuses_nonempty_output_without_changing_it(self):
        self.output.mkdir()
        self.put(self.output / "keep.txt", "user work")
        with self.assertRaisesRegex(ValueError, "empty directory"):
            self.prepare()
        self.assertEqual(list(self.output.iterdir()), [self.output / "keep.txt"])
        self.assertEqual((self.output / "keep.txt").read_text(), "user work")

    def test_accepts_empty_output_and_refuses_second_preparation(self):
        self.output.mkdir()
        self.prepare()
        original = (self.output / "coordinator/manifest.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "empty directory"):
            self.prepare()
        self.assertEqual((self.output / "coordinator/manifest.json").read_bytes(), original)

    def test_rejects_packet_file_directory_and_dangling_symlinks(self):
        for name, target in [("file-link", self.task), ("directory-link", self.stage), ("dangling-link", self.root / "missing")]:
            with self.subTest(name=name):
                link = self.packet / name
                link.symlink_to(target)
                try:
                    with self.assertRaisesRegex(ValueError, "symlink"):
                        self.prepare()
                    self.assertFalse(self.output.exists())
                finally:
                    link.unlink()

    def test_rejects_dependency_link_outside_tree(self):
        link = self.stage / "scripts/node_modules/leak"
        link.symlink_to(self.task)
        with self.assertRaisesRegex(ValueError, "leaves its tree"):
            self.prepare()
        self.assertFalse(self.output.exists())

    def test_rejects_dependency_link_cycle(self):
        link = self.stage / "scripts/node_modules/fixture-runtime/loop"
        link.symlink_to(".")
        with self.assertRaisesRegex(ValueError, "cycle"):
            self.prepare()
        self.assertFalse(self.output.exists())

    def test_rejects_packet_root_task_and_output_symlinks(self):
        for attribute in ("packet", "task", "output"):
            with self.subTest(attribute=attribute):
                target = getattr(self, attribute)
                link = self.root / f"{attribute}-link"
                link.symlink_to(target)
                setattr(self, attribute, link)
                try:
                    with self.assertRaises(ValueError):
                        self.prepare()
                    self.assertFalse(self.output.exists())
                finally:
                    setattr(self, attribute, target)
                    link.unlink()

    def test_rejects_changed_original_guide_or_palette(self):
        guide = self.stage / "references/sequence.md"
        original_guide = guide.read_bytes()
        self.put(guide, "changed guide")
        with self.assertRaisesRegex(ValueError, "preserved original"):
            self.prepare()
        self.put(guide, original_guide)
        template = self.stage / "assets/questions-template.html"
        self.put(template, template.read_bytes().replace(b"#3b5bdb", b"#123456"))
        with self.assertRaisesRegex(ValueError, "palette differs"):
            self.prepare()
        self.assertFalse(self.output.exists())

    def test_cli_help_does_not_launch_or_prepare(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/prepare-comparison.py"), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for option in ("--packet", "--output", "--model", "--task", "--original-root"):
            self.assertIn(option, result.stdout)
        self.assertFalse(self.output.exists())

    def test_real_stage_runtime_dependencies_work_after_copy(self):
        manifest_path = comparison.prepare(self.packet, self.output, MODELS, self.task)
        manifest = json.loads(manifest_path.read_text())
        for run in manifest["runs"]:
            skill = Path(run["cwd"]) / "skill"
            self.assertFalse(any(path.is_symlink() for path in skill.rglob("*")))
            result = subprocess.run([
                "node", "-e",
                "require('./scripts/node_modules/playwright-core'); require('./scripts/node_modules/axe-core')",
            ], cwd=skill, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len({run["hashes"]["input"]["sha256"] for run in manifest["runs"]}), 1)


if __name__ == "__main__":
    unittest.main()
