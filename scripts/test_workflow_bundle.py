"""배포 문서 검증이 변경·누락·저장소 밖 의존성을 잡는지 확인한다."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile


SPEC = importlib.util.spec_from_file_location('workflow_bundle', Path(__file__).with_name('workflow-bundle.py'))
bundle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bundle)


class WorkflowBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        original_root, original_record = bundle.ROOT, bundle.RECORD
        self.addCleanup(setattr, bundle, 'ROOT', original_root)
        self.addCleanup(setattr, bundle, 'RECORD', original_record)
        bundle.ROOT = self.root
        bundle.RECORD = self.root / 'evidence/workflow-bundle.json'
        bundle.RECORD.parent.mkdir()
        for folder in bundle.FOLDERS:
            path = self.root / folder
            path.mkdir(parents=True)
            (path / 'README.md').write_text('# 실행 안내\n')
        (self.root / 'manual').mkdir()
        for name in ('manual/planning-steps.json', 'guides/herdr/planning-steps.json'):
            (self.root / name).write_text('[]\n')
        subprocess.run(['git', 'init', '-q'], cwd=self.root, check=True)
        subprocess.run(['git', 'add', '.'], cwd=self.root, check=True)
        bundle.RECORD.write_text(json.dumps({'schema_version': 1, 'status': 'PASS', 'files': bundle.hashes()}))

    def verify(self):
        with contextlib.redirect_stdout(io.StringIO()):
            bundle.verify()

    def test_unchanged_checkout_passes(self):
        self.verify()

    def test_changed_document_requires_rebuild(self):
        (self.root / 'templates/herdr-project/README.md').write_text('수정된 계약')
        with self.assertRaisesRegex(ValueError, '빌드 기록과 다릅니다'):
            self.verify()

    def test_removed_source_folder_is_rejected(self):
        folder = self.root / 'examples/exam-ocr'
        (folder / 'README.md').unlink()
        folder.rmdir()
        with self.assertRaisesRegex(ValueError, '필수 원본 폴더 누락'):
            self.verify()

    def test_changed_shared_planning_is_rejected(self):
        (self.root / 'manual/planning-steps.json').write_text('[{"id":"P1"}]')
        with self.assertRaisesRegex(ValueError, '공통 기획 원본'):
            self.verify()

    def test_broken_relative_link_is_rejected(self):
        (self.root / 'guides/herdr/README.md').write_text('[빠진 파일](missing.md)')
        with self.assertRaisesRegex(ValueError, '열 수 없는 링크'):
            bundle.check_document_links()

    def test_external_file_link_is_rejected(self):
        with tempfile.NamedTemporaryFile(suffix='.md') as outside:
            (self.root / 'guides/herdr/README.md').write_text(f'[로컬에만 있는 파일]({outside.name})')
            with self.assertRaisesRegex(ValueError, '열 수 없는 링크'):
                bundle.check_document_links()

    def test_failed_rebuild_invalidates_previous_pass(self):
        with patch.object(bundle.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'build-guide.py')):
            with self.assertRaises(subprocess.CalledProcessError):
                with contextlib.redirect_stdout(io.StringIO()):
                    bundle.build()
        with self.assertRaisesRegex(ValueError, '빌드 기록'):
            self.verify()
        self.assertEqual(json.loads(bundle.RECORD.read_text())['status'], 'FAIL')

    def test_failed_rebuild_preserves_modified_planning_copy(self):
        copy = self.root / 'guides/herdr/planning-steps.json'
        copy.write_text('[{"user_edit": true}]\n')
        with self.assertRaisesRegex(ValueError, '별도 변경'):
            bundle.build()
        self.assertEqual(copy.read_text(), '[{"user_edit": true}]\n')
        with self.assertRaisesRegex(ValueError, '빌드 기록'):
            self.verify()

    def test_retry_after_failed_sync_accepts_new_source(self):
        source = self.root / 'manual/planning-steps.json'
        source.write_text('[{"revision": 1}]\n')
        with patch.object(bundle.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'build-guide.py')):
            for revision in (1, 2):
                source.write_text(json.dumps([{'revision': revision}]) + '\n')
                with self.assertRaises(subprocess.CalledProcessError):
                    with contextlib.redirect_stdout(io.StringIO()):
                        bundle.build()
                self.assertEqual((self.root / 'guides/herdr/planning-steps.json').read_bytes(), source.read_bytes())

    def prepare_guide_reports(self):
        for name in ('browser-tests.json', 'pdf-validation.json'):
            (self.root / 'guides/herdr' / name).write_text('{}\n')

    def test_final_manual_build_does_not_publish_pass_early(self):
        self.prepare_guide_reports()
        real_run = subprocess.run

        def external_command(args, **kwargs):
            if args[0] == 'git':
                return real_run(args, **kwargs)
            if args == ['npm', 'run', 'build']:
                self.assertEqual(json.loads(bundle.RECORD.read_text())['status'], 'RUNNING')
                raise subprocess.CalledProcessError(1, args)

        with patch.object(bundle.subprocess, 'run', side_effect=external_command):
            with self.assertRaises(subprocess.CalledProcessError):
                with contextlib.redirect_stdout(io.StringIO()):
                    bundle.build()
        self.assertEqual(json.loads(bundle.RECORD.read_text())['status'], 'FAIL')

    def test_completed_build_packages_the_published_record(self):
        self.prepare_guide_reports()
        archive_path = self.root / 'dist/gon-development-os.zip'
        archive_path.parent.mkdir()
        real_run = subprocess.run

        def external_command(args, **kwargs):
            if args[0] == 'git':
                return real_run(args, **kwargs)
            if args == ['npm', 'run', 'build']:
                with zipfile.ZipFile(archive_path, 'w') as archive:
                    archive.write(bundle.RECORD, 'evidence/workflow-bundle.json')
                    archive.writestr('README.md', '문서 묶음')

        with patch.object(bundle.subprocess, 'run', side_effect=external_command):
            with contextlib.redirect_stdout(io.StringIO()):
                bundle.build()
        self.assertEqual(json.loads(bundle.RECORD.read_text())['status'], 'PASS')
        with zipfile.ZipFile(archive_path) as archive:
            self.assertEqual(archive.read('evidence/workflow-bundle.json'), bundle.RECORD.read_bytes())
            self.assertEqual(archive.read('README.md').decode(), '문서 묶음')
            self.assertEqual(len(archive.namelist()), len(set(archive.namelist())))

    def test_failed_final_archive_does_not_report_pass(self):
        self.prepare_guide_reports()
        real_run = subprocess.run

        def external_command(args, **kwargs):
            if args[0] == 'git':
                return real_run(args, **kwargs)

        output = io.StringIO()
        with patch.object(bundle.subprocess, 'run', side_effect=external_command):
            with self.assertRaises(FileNotFoundError):
                with contextlib.redirect_stdout(output):
                    bundle.build()
        self.assertEqual(json.loads(bundle.RECORD.read_text())['status'], 'FAIL')
        self.assertNotIn('"workflow_bundle": "PASS"', output.getvalue())


if __name__ == '__main__':
    unittest.main()
