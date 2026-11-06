from pathlib import Path
import hashlib
import json
import tempfile
import unittest

from diagram_proof import validate_diagram
from planning import read_sections


class DiagramProofTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.spec = self.root / 'workflow.json'
        self.artifact = self.root / 'map.html'
        self.receipt = self.root / 'proof.json'
        self.spec.write_text('{"nodes": ["A", "B"]}')
        self.artifact.write_text('<html>A → B</html>')
        self.record = {'ok': True, 'gates': {key: 'pass' for key in ['validate', 'deliver', 'check', 'browser-check']}}
        for key, path in [('specification', self.spec), ('artifact', self.artifact)]:
            self.record[key] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        self.receipt.write_text(json.dumps(self.record))

    def tearDown(self):
        self.temp.cleanup()

    def test_changed_source_cannot_reuse_old_diagram(self):
        validate_diagram(self.spec, self.artifact, self.receipt)
        self.spec.write_text('{"nodes": ["A", "B", "C"]}')
        with self.assertRaisesRegex(ValueError, 'specification'):
            validate_diagram(self.spec, self.artifact, self.receipt)

    def test_replaced_html_requires_new_validation(self):
        self.artifact.write_text('<html>새 그림</html>')
        with self.assertRaisesRegex(ValueError, 'artifact'):
            validate_diagram(self.spec, self.artifact, self.receipt)

    def test_unrun_browser_gate_is_not_accepted(self):
        self.record['gates']['browser-check'] = 'not-run'
        self.receipt.write_text(json.dumps(self.record))
        with self.assertRaisesRegex(ValueError, '통과하지'):
            validate_diagram(self.spec, self.artifact, self.receipt)

    def test_manual_projects_shared_planning_into_its_own_step_numbers(self):
        sections = read_sections(Path(__file__).resolve().parents[1])
        p5 = next(section for section in sections if section['id'] == 'planning-5')
        self.assertIn('02에 문서 경로', p5['body'])
        self.assertNotIn('00에서', p5['body'])
        self.assertNotIn('할 일 앱 4기능', p5['body'])
        p4 = next(section for section in sections if section['id'] == 'planning-4')
        self.assertIn('docs/research/04-decision.md', p4['body'])
        self.assertNotIn('{{', p5['body'])
        self.assertIn('Codex 대화 입력칸', p5['body'])


if __name__ == '__main__':
    unittest.main()
