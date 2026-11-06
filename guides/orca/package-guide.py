#!/usr/bin/env python3
"""읽기·재생성·검증에 필요한 파일만 ZIP으로 묶는다."""
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parent
NAMES=['index.html','examples.html','guide.pdf','style.css','viewer.js','steps.json','README.md','시작하기.txt','package.json','package-lock.json','build-guide.py','print-guide.cjs','test-guide.cjs','validate-guide.py','package-guide.py','browser-tests.json','rendered-prompts.json','pdf-validation.json','verification.json','sources.json','external-review.json','overview.png','workbench.png','documents.png','mobile-p5.png','pdf-documents.png','pdf-step.png']
files=[ROOT/n for n in NAMES]
for folder in ['example-project','templates','evidence']:
    files+=sorted(p for p in (ROOT/folder).rglob('*') if p.is_file())
assert all(p.is_file() for p in files)
out=ROOT.parent/'gon-orca-codex-guide.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
    for p in files:archive.write(p,Path('gon-orca-codex-guide')/p.relative_to(ROOT))
print(f'{out.name}: {len(files)} files, {out.stat().st_size:,} bytes')
