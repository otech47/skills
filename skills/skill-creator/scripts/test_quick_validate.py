import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.package_skill import package_skill
from scripts.quick_validate import validate_skill


class ValidationTargetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / 'example'
        self.skill.mkdir()

    def write_skill(self, extra='', name='name: example\n'):
        (self.skill / 'SKILL.md').write_text(
            f'---\n{name}description: Example skill.\n{extra}---\n\n# Example\n'
        )

    def test_portable_metadata_passes_both_targets(self):
        self.write_skill('license: MIT\ncompatibility: Python 3\nmetadata:\n  author: example\nallowed-tools: Read\n')
        for target in ('portable', 'claude-code'):
            with self.subTest(target=target):
                self.assertTrue(validate_skill(self.skill, target)[0])

    def test_claude_extensions_are_target_specific(self):
        fields = {
            'when_to_use': 'On request', 'argument-hint': '[file]',
            'arguments': '[file, format]', 'disable-model-invocation': 'true',
            'user-invocable': 'true', 'disallowed-tools': 'AskUserQuestion',
            'model': 'inherit', 'effort': 'high', 'context': 'fork',
            'agent': 'Explore', 'background': 'false', 'hooks': '{}',
            'paths': '[src/**]', 'shell': 'bash',
        }
        for field, value in fields.items():
            with self.subTest(field=field):
                self.write_skill(f'{field}: {value}\n')
                self.assertTrue(validate_skill(self.skill, 'claude-code')[0])
                valid, message = validate_skill(self.skill)
                self.assertFalse(valid)
                self.assertIn('--target claude-code', message)

    def test_invocation_false_is_valid_metadata(self):
        self.write_skill('user-invocable: false\n')
        self.assertTrue(validate_skill(self.skill, 'claude-code')[0])

    def test_typos_still_fail(self):
        self.write_skill('user-invokable: true\n')
        for target in ('portable', 'claude-code'):
            with self.subTest(target=target):
                valid, message = validate_skill(self.skill, target)
                self.assertFalse(valid)
                self.assertIn('user-invokable', message)
                self.assertNotIn('use --target', message)

    def test_shared_required_fields_remain_required(self):
        self.write_skill(name='')
        for target in ('portable', 'claude-code'):
            with self.subTest(target=target):
                self.assertEqual(validate_skill(self.skill, target), (False, "Missing 'name' in frontmatter"))

    def test_invalid_yaml_still_fails(self):
        self.write_skill('user-invocable: [\n')
        self.assertFalse(validate_skill(self.skill, 'claude-code')[0])

    def test_cli_selects_target(self):
        self.write_skill('user-invocable: true\n')
        script = Path(__file__).with_name('quick_validate.py')
        for flags, expected in (([], 1), (['--target', 'claude-code'], 0), (['--target', 'unknown'], 2)):
            with self.subTest(flags=flags):
                result = subprocess.run([sys.executable, str(script), str(self.skill), *flags], capture_output=True)
                self.assertEqual(result.returncode, expected)

    def test_packager_preserves_portable_restriction(self):
        self.write_skill()
        with contextlib.redirect_stdout(io.StringIO()):
            archive = package_skill(self.skill, self.root / 'portable')
        self.assertTrue(archive.is_file())
        self.write_skill('user-invocable: true\n')
        with contextlib.redirect_stdout(io.StringIO()):
            rejected = package_skill(self.skill, self.root / 'claude')
        self.assertIsNone(rejected)
        self.assertFalse((self.root / 'claude').exists())


if __name__ == '__main__':
    unittest.main()
