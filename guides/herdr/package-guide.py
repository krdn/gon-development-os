#!/usr/bin/env python3
"""현재 원본·산출물·검증만 골라 오프라인 전달 묶음을 만든다."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
FILES = [
    'index.html', 'guide.pdf', 'project-guide.pdf', 'planning-map.html', 'workflow-map.html',
    'planning-map-source.json', 'workflow-source.json', 'planning-map-validation.json',
    'workflow-validation.json', 'build-guide.py', 'development-steps.json', 'project-steps.json',
    'planning-steps.json', 'entrypoints.json', 'steps.json', 'template.html', 'handbook.html', 'style.css',
    'viewer.js', 'print-guide.cjs', 'test-guide.cjs', 'validate-guide.py', 'package-guide.py',
    'package.json', 'package-lock.json', 'requirements.txt', 'README.md', '시작하기.txt',
    'verification.json', 'browser-tests.json', 'pdf-validation.json', 'opus-review.json',
    'preview.png', 'project-step-preview.png', 'project-mobile.png',
    'workbench-preview.png', 'documents-preview.png', 'planning-map-preview.png',
    'development-map-preview.png', 'planning-pdf-6.png',
    'example-project.zip', 'templates/PROJECT-BRIEF.md',
]
output = ROOT.parent / 'gon-beginner-workflow.zip'
files = [ROOT / name for name in FILES]
files += sorted((ROOT / 'evidence/herdr-ui').glob('*.json'))
files += sorted((ROOT / 'example-project').rglob('*.md'))
if any(not file.is_file() or file.is_symlink() for file in files):
    raise ValueError('전달 파일이 없거나 심볼릭 링크입니다.')
record = json.loads((ROOT / 'verification.json').read_text())
expected = {str(file.relative_to(ROOT)) for file in files if file.name != 'verification.json'}
if set(record['sha256']) != expected:
    raise ValueError('검증 기록의 파일 목록이 전달 파일과 다릅니다.')
for name, checksum in record['sha256'].items():
    if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != checksum:
        raise ValueError(f'검증 후 변경된 파일: {name}')
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as bundle:
    for file in files:
        bundle.write(file, Path('gon-beginner-workflow') / file.relative_to(ROOT))
with zipfile.ZipFile(output) as bundle:
    if bundle.testzip() is not None:
        raise ValueError('ZIP 무결성 검사 실패')
print(f'전달 묶음: {len(files)}파일, {output.stat().st_size}바이트, 무결성 PASS')
