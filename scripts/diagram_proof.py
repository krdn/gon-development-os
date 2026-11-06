"""흐름도 원본과 HTML을 실제 Archify 검증 결과에 묶어 확인한다."""
from pathlib import Path
import hashlib
import json


def validate_diagram(specification, artifact, receipt):
    record = json.loads(Path(receipt).read_text())
    if record.get('ok') is not True or record.get('gates') != {
        'validate': 'pass', 'deliver': 'pass', 'check': 'pass', 'browser-check': 'pass',
    }:
        raise ValueError('흐름도 검증이 통과하지 않았습니다.')
    for key, path in [('specification', specification), ('artifact', artifact)]:
        digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        if record.get(key, {}).get('sha256') != digest:
            raise ValueError(f'흐름도 {key}가 검증 기록과 다릅니다. Archify finalize가 필요합니다.')
    return record


def check_workflow(root):
    return validate_diagram(root / 'diagrams/workflow.json', root / 'dist/02-workflow-map.html',
                            root / 'evidence/workflow-validation.json')
