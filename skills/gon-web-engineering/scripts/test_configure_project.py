"""Regression checks: python3 -m unittest discover -s scripts -p 'test_*.py'."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('configure_project.py')


class ConfigureProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        self.root.mkdir()

    def run_config(self, *args, topics=('frontend', 'verification'), code=0):
        command = [sys.executable, str(SCRIPT), '--project', str(self.root)]
        if topics:
            command += ['--topics', *topics]
        result = subprocess.run(command + list(args), capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_plan_does_not_write(self):
        result = self.run_config()
        self.assertEqual(result['status'], 'planned')
        self.assertEqual(list(self.root.iterdir()), [])

    def test_topics_required(self):
        self.run_config('--apply', topics=(), code=1)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_selected_topics_and_provenance(self):
        self.run_config('--apply')
        self.assertFalse((self.root / 'docs/ai/backend-data.md').exists())
        content = (self.root / 'docs/ai/frontend.md').read_bytes()
        self.assertIn(hashlib.sha256(content).hexdigest(), (self.root / 'docs/ai/project-context.md').read_text())
        self.assertEqual((self.root / 'CLAUDE.md').read_text(), '@AGENTS.md\n')

    def test_all_topics(self):
        result = self.run_config('--apply', topics=('architecture', 'frontend', 'backend-data', 'verification'))
        self.assertEqual(len(result['files']), 7)
        self.assertTrue(all(f['action'] == 'created' for f in result['files']))

    def test_rerun_is_unchanged(self):
        self.run_config('--apply')
        result = self.run_config('--apply')
        self.assertTrue(all(f['action'] == 'unchanged' for f in result['files']))

    def test_existing_content_preserved(self):
        file = self.root / 'AGENTS.md'
        file.write_bytes(b'Existing rules\r\n')
        result = self.run_config('--apply')
        self.assertEqual(file.read_bytes(), b'Existing rules\r\n')
        self.assertIn('AGENTS.md', [r['path'] for r in result['review_required']])

    def test_nested_claude_preserved(self):
        nested = self.root / '.claude/CLAUDE.md'
        nested.parent.mkdir()
        nested.write_text('Existing Claude rules')
        result = self.run_config('--apply')
        self.assertFalse((self.root / 'CLAUDE.md').exists())
        self.assertIn('.claude/CLAUDE.md', [r['path'] for r in result['review_required']])
        self.assertEqual(nested.read_text(), 'Existing Claude rules')

    def test_both_claude_entries_reported(self):
        (self.root / '.claude').mkdir()
        (self.root / '.claude/CLAUDE.md').write_text('Nested rules')
        (self.root / 'CLAUDE.md').write_text('Root rules')
        result = self.run_config('--apply')
        paths = [r['path'] for r in result['review_required']]
        self.assertIn('CLAUDE.md', paths)
        self.assertIn('.claude/CLAUDE.md', paths)

    def test_override_reported(self):
        (self.root / 'AGENTS.override.md').write_text('Override')
        result = self.run_config('--apply')
        self.assertIn('AGENTS.override.md', [r['path'] for r in result['review_required']])

    def test_symlink_preflight_prevents_all_writes(self):
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        (self.root / 'docs').symlink_to(outside, target_is_directory=True)
        self.run_config('--apply', code=1)
        self.assertFalse((self.root / 'AGENTS.md').exists())
        self.assertEqual(list(outside.iterdir()), [])

    def test_non_directory_parent_prevents_all_writes(self):
        (self.root / 'docs').write_text('Keep')
        self.run_config('--apply', code=1)
        self.assertFalse((self.root / 'AGENTS.md').exists())

    def test_duplicate_topics_deduplicated(self):
        result = self.run_config('--apply', topics=('verification', 'verification'))
        self.assertEqual(result['topics'], ['verification'])
        self.assertEqual(len(result['files']), 4)

    def test_invalid_topic_prevents_writes(self):
        self.run_config('--apply', topics=('unknown',), code=1)
        self.assertEqual(list(self.root.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
