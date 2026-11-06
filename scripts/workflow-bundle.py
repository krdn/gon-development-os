#!/usr/bin/env python3
"""저장소의 두 안내서와 실행 문서 묶음을 재생성하고 내용 해시를 검증한다."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit
import re
import zipfile


ROOT = Path(__file__).resolve().parents[1]
FOLDERS = ('guides/herdr', 'guides/orca', 'templates/herdr-project', 'examples/exam-ocr')
RECORD = ROOT / 'evidence/workflow-bundle.json'
IGNORED = {'node_modules', '.venv', '__pycache__', '.git'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files_in(folder):
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(folder.relative_to(ROOT))], cwd=ROOT)
    return [ROOT / name for name in tracked.decode().split('\0') if name]


def verify_archive(folder, path):
    with zipfile.ZipFile(path) as archive:
        expected = {str(p.relative_to(folder)): digest(p) for p in files_in(folder)}
        actual = {str(Path(n).relative_to(path.stem)): hashlib.sha256(archive.read(n)).hexdigest()
                  for n in archive.namelist()}
        if actual != expected or len(actual) != len(archive.namelist()):
            raise ValueError(f'안내서 ZIP과 Git 원본 불일치: {path.name}')


def hashes():
    result = {}
    for name in FOLDERS:
        folder = ROOT / name
        if not folder.is_dir():
            raise ValueError(f'필수 원본 폴더 누락: {name}')
        for path in files_in(folder):
            if path.is_symlink():
                raise ValueError(f'외부 파일 링크를 원본으로 사용하지 않습니다: {path}')
            result[str(path.relative_to(ROOT))] = digest(path)
    return result


def check_document_links():
    count = 0
    for name in FOLDERS:
        for path in files_in(ROOT / name):
            if path.suffix != '.md':
                continue
            text = path.read_text()
            if text.count('```') % 2:
                raise ValueError(f'닫히지 않은 코드 블록: {path.relative_to(ROOT)}')
            for href in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)', text):
                parsed = urlsplit(href.strip('<>'))
                if not parsed.scheme and not parsed.netloc and parsed.path:
                    target = (path.parent / unquote(parsed.path)).resolve()
                    if not target.is_relative_to(ROOT) or not target.is_file():
                        raise ValueError(f'저장소 안에서 열 수 없는 링크: {path.relative_to(ROOT)}: {href}')
                    count += 1
    return count


def verify():
    record = json.loads(RECORD.read_text())
    if record.get('schema_version') != 1 or record.get('status') != 'PASS':
        raise ValueError('전체 안내서 빌드 기록이 없습니다. npm run build:all을 실행하세요.')
    if record.get('files') != hashes():
        raise ValueError('안내서·실행 문서가 빌드 기록과 다릅니다. npm run build:all을 실행하세요.')
    if (ROOT / 'manual/planning-steps.json').read_bytes() != (ROOT / 'guides/herdr/planning-steps.json').read_bytes():
        raise ValueError('공통 기획 원본과 Herdr 안내서가 다릅니다.')
    for name, stem in [('herdr', 'gon-beginner-workflow'), ('orca', 'gon-orca-codex-guide')]:
        path = ROOT / 'guides' / (stem + '.zip')
        if path.exists():
            verify_archive(ROOT / 'guides' / name, path)
    count = check_document_links()
    print(json.dumps({'workflow_bundle': 'PASS', 'files': len(record['files']),
                      'markdown_links': count, 'scope': '문서와 검사 기록; 실제 에이전트 실행 아님'}, ensure_ascii=False))


def run(args, cwd, commands):
    print('+ ' + ' '.join(str(x) for x in args), flush=True)
    subprocess.run(args, cwd=cwd, check=True)
    commands.append({'cwd': str(cwd.relative_to(ROOT)) or '.',
                     'command': [str(x) if x != sys.executable else 'python3' for x in args],
                     'result': 'PASS'})


def build():
    commands = []
    source = ROOT / 'manual/planning-steps.json'
    copy = ROOT / 'guides/herdr/planning-steps.json'
    if copy.exists() and digest(source) != digest(copy):
        if not RECORD.exists() or json.loads(RECORD.read_text()).get('files', {}).get(str(copy.relative_to(ROOT))) != digest(copy):
            raise ValueError('Herdr 기획 사본에 별도 변경이 있습니다. 공통 원본과 먼저 대조하세요.')
    shutil.copyfile(source, copy)
    for name in ('herdr', 'orca'):
        folder = ROOT / 'guides' / name
        run([sys.executable, 'build-guide.py'], folder, commands)
        run(['node', 'test-guide.cjs'], folder, commands)
        run(['node', 'print-guide.cjs'], folder, commands)
        validation = [sys.executable, 'validate-guide.py', '--pdf']
        if name == 'herdr':
            validation += ['--manual-planning', '../../manual/planning-steps.json']
        run(validation, folder, commands)
        current = {
            'built_at_utc': datetime.now(timezone.utc).isoformat(),
            'scope': '이번 재생성의 브라우저 회귀·PDF 내용·링크 검사. 실제 Herdr/Orca 실행·배포 아님.',
            'historical_evidence': 'preview 이미지, evidence/ 및 외부 리뷰 기록은 이전 확인 자료이며 이번 실행 증거가 아님.',
            'browser_tests': json.loads((folder / 'browser-tests.json').read_text()),
            'pdf_validation': json.loads((folder / 'pdf-validation.json').read_text()),
            'sha256': {str(p.relative_to(folder)): digest(p) for p in files_in(folder)
                       if p.name != 'verification.json'},
        }
        (folder / 'verification.json').write_text(json.dumps(current, ensure_ascii=False, indent=2) + '\n')
        run([sys.executable, 'package-guide.py'], folder, commands)
    count = check_document_links()
    record = {'schema_version': 1, 'status': 'PASS',
              'built_at_utc': datetime.now(timezone.utc).isoformat(),
              'scope': '문서 재생성·브라우저 회귀·PDF·링크·파일 무결성. 실제 앱 협업·제품 OCR·배포는 별도.',
              'markdown_links': count, 'commands': commands, 'files': hashes()}
    RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    # 마지막에 관리 매뉴얼과 전체 ZIP을 생성해야 새 안내서·검증 기록도 포함된다.
    try:
        run(['npm', 'run', 'build'], ROOT, commands)
        verify()
    except BaseException:
        RECORD.unlink(missing_ok=True)
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'verify'])
    args = parser.parse_args()
    if args.command == 'build':
        build()
    else:
        verify()
