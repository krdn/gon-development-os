"""배포 문서 검증이 변경·누락·저장소 밖 의존성을 잡는지 확인한다."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


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


if __name__ == '__main__':
    unittest.main()
