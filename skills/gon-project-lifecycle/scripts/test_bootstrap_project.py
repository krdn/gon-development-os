"""문서 생성기의 무변경 계획·기존 작업 보존·경로 경계를 검증한다."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import bootstrap_project as bootstrap


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='gon-lifecycle-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / '한글 프로젝트'

    def run_cli(self, *extra, documents=None):
        documents = documents or list(bootstrap.CHOICES)
        result = subprocess.run([
            sys.executable, str(Path(bootstrap.__file__)),
            '--project', str(self.project), '--documents', *documents, *extra,
        ], capture_output=True, text=True, check=False)
        self.assertTrue(result.stdout, result.stderr)
        return result.returncode, json.loads(result.stdout)

    def snapshot(self):
        return {
            str(path.relative_to(self.base)): path.read_bytes()
            for path in self.base.rglob('*') if path.is_file() and not path.is_symlink()
        }

    def test_plan_does_not_create_project_or_directories(self):
        before = list(self.base.iterdir())
        code, report = self.run_cli()
        self.assertEqual(code, 0)
        self.assertEqual(report['status'], 'planned')
        self.assertEqual(len(report['files']), 7)
        self.assertEqual(list(self.base.iterdir()), before)

    def test_apply_creates_requested_documents_and_working_links(self):
        code, report = self.run_cli('--apply')
        self.assertEqual(code, 0)
        self.assertEqual(report['status'], 'applied')
        self.assertTrue(report['scaffold_only'])
        self.assertEqual(set(item['action'] for item in report['files']), {'created'})
        self.assertEqual(len(self.snapshot()), 7)
        for item in report['files']:
            content = (self.project / item['path']).read_text()
            self.assertIn('한글 프로젝트', content)
            self.assertNotIn('{{', content)
            for link in re.findall(r'\]\(([^)]+)\)', content):
                self.assertTrue((self.project / link).is_file(), link)

    def test_repeated_apply_preserves_every_byte(self):
        self.run_cli('--apply')
        state = self.project / 'docs/STATE.md'
        state.write_text('사용자가 갱신한 현재 상태\n검증 FAIL\n')
        before = self.snapshot()
        code, report = self.run_cli('--apply')
        self.assertEqual(code, 0)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(set(item['action'] for item in report['files']), {'preserve'})

    def test_existing_documents_and_unrelated_code_are_preserved(self):
        self.project.mkdir()
        (self.project / 'AGENTS.md').write_text('기존 지침\n')
        (self.project / 'README.md').write_text('기존 소개\n')
        (self.project / 'app.py').write_text('print("original")\n')
        before = self.snapshot()
        code, report = self.run_cli('--apply')
        self.assertEqual(code, 0)
        for relative, content in before.items():
            self.assertEqual((self.base / relative).read_bytes(), content)
        self.assertEqual(len(report['review_required']), 2)

    def test_only_selected_document_is_created(self):
        code, report = self.run_cli('--apply', documents=['state'])
        self.assertEqual(code, 0)
        self.assertEqual(len(report['files']), 1)
        self.assertEqual(list(self.snapshot()), ['한글 프로젝트/docs/STATE.md'])

    def test_github_only_creates_management_document_without_other_project_files(self):
        code, report = self.run_cli('--apply', documents=['github'])
        self.assertEqual(code, 0)
        self.assertEqual(list(self.snapshot()), ['한글 프로젝트/.github/project-management.md'])
        self.assertTrue(report['scaffold_only'])
        self.assertFalse((self.project / '.git').exists())

    def test_existing_github_mapping_is_preserved_and_linked_from_entrypoints(self):
        (self.project / 'docs').mkdir(parents=True)
        existing = self.project / 'docs/github-management.md'
        existing.write_text('기존 관리 기준\nhttps://github.com/owner/repo/issues/1\n')
        before = existing.read_bytes()
        code, report = self.run_cli('--apply', documents=['github', 'entrypoints'])
        self.assertEqual(code, 0)
        self.assertEqual(existing.read_bytes(), before)
        self.assertFalse((self.project / '.github/project-management.md').exists())
        self.assertIn('(docs/github-management.md)', (self.project / 'AGENTS.md').read_text())
        self.assertTrue(report['review_required'])

    def test_known_equivalent_paths_are_reused_without_duplicate_documents(self):
        self.project.mkdir()
        (self.project / 'PROJECT.md').write_text('기존 목적')
        (self.project / 'ARCHITECT.md').write_text('기존 구조')
        code, report = self.run_cli('--apply')
        self.assertEqual(code, 0)
        self.assertFalse((self.project / 'docs/PRODUCT.md').exists())
        self.assertFalse((self.project / 'docs/ARCHITECTURE.md').exists())
        readme = (self.project / 'README.md').read_text()
        self.assertIn('(PROJECT.md)', readme)
        self.assertIn('(ARCHITECT.md)', readme)
        self.assertEqual(len(report['review_required']), 2)

    def test_herdr_brief_is_preserved_and_linked_when_product_spec_is_absent(self):
        (self.project / 'docs').mkdir(parents=True)
        brief = self.project / 'docs/PROJECT-BRIEF.md'
        brief.write_text('AC01: 기존 요구')
        code, report = self.run_cli('--apply', documents=['product', 'entrypoints'])
        self.assertEqual(code, 0)
        self.assertEqual(report['files'][0]['action'], 'preserve')
        self.assertEqual(brief.read_text(), 'AC01: 기존 요구')
        self.assertFalse((self.project / 'docs/PRODUCT.md').exists())
        self.assertIn('(docs/PROJECT-BRIEF.md)', (self.project / 'AGENTS.md').read_text())

        (self.project / 'docs/PRODUCT.md').write_text('기존 기준 명세')
        code, report = self.run_cli(documents=['product'])
        self.assertEqual(code, 0)
        self.assertEqual(report['files'][0]['path'], 'docs/PRODUCT.md')
        self.assertIn('docs/PROJECT-BRIEF.md', report['review_required'][0]['paths'])

    def test_override_is_preserved_and_active_entrypoint_requires_merge(self):
        self.project.mkdir()
        override = self.project / 'AGENTS.override.md'
        override.write_text('활성 지침')
        code, report = self.run_cli('--apply')
        self.assertEqual(code, 0)
        self.assertFalse((self.project / 'AGENTS.md').exists())
        self.assertEqual(override.read_text(), '활성 지침')
        self.assertIn('AGENTS.override.md', report['review_required'][0]['paths'])
        self.assertIn('(AGENTS.override.md)', (self.project / 'README.md').read_text())

    def test_entrypoints_only_do_not_link_to_nonexistent_documents(self):
        code, _ = self.run_cli('--apply', documents=['entrypoints'])
        self.assertEqual(code, 0)
        self.assertEqual(len(self.snapshot()), 2)
        self.assertIn('(README.md)', (self.project / 'AGENTS.md').read_text())
        self.assertNotIn('docs/', (self.project / 'AGENTS.md').read_text())

    def test_aeos_is_blocked_before_any_write(self):
        (self.project / '.ai/contracts').mkdir(parents=True)
        (self.project / '.ai/contracts/TASK.md').write_text('기존 계약')
        before = self.snapshot()
        code, report = self.run_cli('--apply')
        self.assertEqual(code, 1)
        self.assertEqual(report['status'], 'blocked')
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.project / 'docs').exists())

    def test_partial_aeos_markers_block_all_writes(self):
        for marker in ('.ai/tasks', 'scripts/aeos.py'):
            with self.subTest(marker=marker):
                target = self.project / marker
                if marker.endswith('.py'):
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text('# 부분 도입된 AEOS 도구\n')
                else:
                    target.mkdir(parents=True)
                code, report = self.run_cli('--apply')
                self.assertEqual(code, 1)
                self.assertEqual(report['status'], 'blocked')
                self.assertFalse((self.project / 'docs').exists())
                self.assertFalse((self.project / 'AGENTS.md').exists())
                if target.is_file():
                    target.unlink()
                else:
                    target.rmdir()

    def test_existing_claude_guidance_is_preserved_and_reported(self):
        for relative in ('CLAUDE.md', '.claude/CLAUDE.md'):
            path = self.project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('기존 프로젝트별 Claude 지침\n')
        before = self.snapshot()
        code, report = self.run_cli('--apply')
        self.assertEqual(code, 0)
        for relative, content in before.items():
            self.assertEqual((self.base / relative).read_bytes(), content)
        reported = {path for review in report['review_required'] for path in review['paths']}
        self.assertIn('CLAUDE.md', reported)
        self.assertIn('.claude/CLAUDE.md', reported)

    def test_path_collision_blocks_all_writes(self):
        self.project.mkdir()
        (self.project / 'docs').write_text('폴더 자리에 파일')
        before = self.snapshot()
        code, report = self.run_cli('--apply')
        self.assertEqual(code, 1)
        self.assertEqual(report['status'], 'blocked')
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.project / 'AGENTS.md').exists())

    def test_directory_in_place_of_document_blocks_all_writes(self):
        (self.project / 'README.md').mkdir(parents=True)
        code, report = self.run_cli('--apply')
        self.assertEqual(code, 1)
        self.assertEqual(report['status'], 'blocked')
        self.assertFalse((self.project / 'docs').exists())

    def test_linked_output_directory_cannot_write_outside_project(self):
        self.project.mkdir()
        external = self.base / 'external'
        external.mkdir()
        (self.project / 'docs').symlink_to(external, target_is_directory=True)
        code, report = self.run_cli('--apply')
        self.assertEqual(code, 1)
        self.assertEqual(report['status'], 'blocked')
        self.assertEqual(list(external.iterdir()), [])
        self.assertFalse((self.project / 'AGENTS.md').exists())

    def test_broken_symlink_and_linked_project_are_blocked(self):
        self.project.mkdir()
        (self.project / 'AGENTS.md').symlink_to(self.base / 'missing')
        code, _ = self.run_cli('--apply')
        self.assertEqual(code, 1)
        self.assertFalse((self.project / 'docs').exists())
        linked = self.base / 'alias'
        linked.symlink_to(self.project, target_is_directory=True)
        with self.assertRaises(ValueError):
            bootstrap.make_plan(linked, 'alias', ['state'])

    def test_unselected_document_link_does_not_block_single_state_creation(self):
        self.project.mkdir()
        (self.project / 'AGENTS.md').symlink_to(self.base / 'missing')
        code, report = self.run_cli('--apply', documents=['state'])
        self.assertEqual(code, 0)
        self.assertEqual(report['status'], 'applied')
        self.assertTrue((self.project / 'docs/STATE.md').is_file())

    def test_concurrent_file_creation_is_preserved(self):
        report, contents = bootstrap.make_plan(self.project, 'sample', ['state'])
        (self.project / 'docs').mkdir(parents=True)
        state = self.project / 'docs/STATE.md'
        state.write_text('다른 작업자의 갱신')
        result = bootstrap.apply_plan(self.project, report, contents)
        self.assertEqual(result['status'], 'applied')
        self.assertEqual(result['files'][0]['action'], 'preserve')
        self.assertEqual(state.read_text(), '다른 작업자의 갱신')
        self.assertTrue(result['review_required'])

    def test_failure_reports_partial_and_retains_created_files(self):
        report, contents = bootstrap.make_plan(self.project, 'sample', ['product', 'state'])
        original_check = bootstrap.check_path

        def fail_state(path, directory=False):
            if path.name == 'STATE.md':
                raise OSError('쓰기 실패 재현')
            return original_check(path, directory)

        with patch.object(bootstrap, 'check_path', side_effect=fail_state):
            result = bootstrap.apply_plan(self.project, report, contents)
        self.assertEqual(result['status'], 'partial')
        self.assertTrue((self.project / 'docs/PRODUCT.md').is_file())
        self.assertFalse((self.project / 'docs/STATE.md').exists())
        self.assertEqual(result['files'][0]['action'], 'created')

    def test_invalid_project_name_does_not_create_files(self):
        for name in ('', 'line\nline', 'bad\x01name'):
            with self.subTest(name=repr(name)):
                code, report = self.run_cli('--name', name, '--apply')
                self.assertEqual(code, 1)
                self.assertEqual(report['status'], 'blocked')
        self.assertFalse(self.project.exists())

    def test_missing_template_is_blocked_without_writes(self):
        output = io.StringIO()
        with patch.object(bootstrap, 'ASSETS', self.base / 'missing-assets'):
            with redirect_stdout(output):
                code = bootstrap.main([
                    '--project', str(self.project), '--documents', 'state', '--apply',
                ])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output.getvalue())['status'], 'blocked')
        self.assertFalse(self.project.exists())


if __name__ == '__main__':
    unittest.main()
