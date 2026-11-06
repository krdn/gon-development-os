#!/usr/bin/env python3
"""현재 문서 링크와 두 스킬의 실제 동작 검사를 수행한다."""
from html.parser import HTMLParser
from pathlib import Path
from planning import read_sections
from diagram_proof import check_workflow
from urllib.parse import unquote, urlsplit
import json
import hashlib
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def check_skill_snapshot():
    revision, *expected = (ROOT / 'skills.lock').read_text().splitlines()
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('skills.lock의 gon-skills 커밋 SHA를 확인하세요.')

    def git(*args):
        return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

    # 트리 해시는 Git이 배포하는 파일명, 내용과 실행 비트를 함께 식별한다.
    if git('diff', '--name-only', '--', 'skills') or git('ls-files', '--others', '--exclude-standard', '--', 'skills'):
        raise ValueError('오프라인 스킬이 변경됐습니다. 원본에서 가져온 파일과 Git 인덱스를 확인하세요.')
    tree = git('write-tree', '--prefix=skills/')
    if git('ls-tree', tree).splitlines() != expected:
        raise ValueError('오프라인 스킬 사본이 skills.lock과 다릅니다. docs/03-maintenance.md를 확인하세요.')


def check_artifacts():
    check_skill_snapshot()
    check_workflow(ROOT)
    record = json.loads((ROOT / 'evidence/build.json').read_text())
    sources = [p for folder in ['manual', 'scripts', 'diagrams']
               for p in (ROOT / folder).iterdir() if p.is_file()]
    sources += [ROOT / name for name in ['VERSION', 'package.json', 'package-lock.json',
                                       'requirements.txt']]
    expected = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sources}
    if record.get('sources') != expected:
        raise ValueError('원본 변경이 빌드 기록과 다릅니다. npm run build를 실행하세요.')
    if record['version'] != (ROOT / 'VERSION').read_text().strip():
        raise ValueError('빌드 기록의 버전이 다릅니다.')
    for name in ['dist/01-project-workflow-manual.html', 'dist/01-project-workflow-manual.pdf',
                 'dist/02-workflow-map.html', 'docs/01-manual.md']:
        digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        if record['artifacts'].get(name, {}).get('sha256') != digest:
            raise ValueError(f'생성 결과가 빌드 기록과 다릅니다: {name}')
    print('원본·생성 결과와 빌드 기록 해시 일치')


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if 'id' in values:
            self.ids.add(values['id'])
        if tag == 'a' and 'href' in values:
            self.links.append(values['href'])


def main():
    check_artifacts()
    if '--artifacts-only' in sys.argv:
        return
    sections = read_sections(ROOT)
    ids = [s['id'] for s in sections]
    if len(ids) != len(set(ids)):
        raise ValueError('중복된 매뉴얼 항목 ID')
    page = ROOT / 'dist/01-project-workflow-manual.html'
    parser = Links()
    parser.feed(page.read_text())
    errors = []
    version = (ROOT / 'VERSION').read_text().strip()
    for path in ['package.json', 'package-lock.json']:
        if json.loads((ROOT / path).read_text())['version'] != version:
            errors.append(f'{path}: VERSION 불일치')
    for href in parser.links:
        target = urlsplit(href)
        if target.scheme or target.netloc:
            continue
        if not target.path:
            if target.fragment not in parser.ids:
                errors.append(href)
        elif not (page.parent / unquote(target.path)).is_file():
            errors.append(href)
    markdown_files = [ROOT / 'README.md', ROOT / 'AGENTS.md', *sorted((ROOT / 'docs').glob('*.md'))]
    for document in markdown_files:
        content = document.read_text()
        hrefs = re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)', content)
        embedded = Links()
        embedded.feed(content)
        for href in hrefs + embedded.links:
            target = urlsplit(href)
            if not target.scheme and not target.netloc and target.path:
                if not (document.parent / unquote(target.path)).is_file():
                    errors.append(f'{document.relative_to(ROOT)}: {href}')
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT / 'scripts'),
                    '-p', 'test_*.py', '-v'], check=True)
    skills = [p for p in sorted((ROOT / 'skills').iterdir()) if p.is_dir()]
    for skill in skills:
        if not (skill / 'SKILL.md').is_file():
            errors.append(f'{skill.name}: SKILL.md 누락')
            continue
        text = (skill / 'SKILL.md').read_text()
        if not text.startswith('---\n'):
            errors.append(f'{skill.name}: frontmatter 누락')
        for ref in re.findall(r'\]\(([^)]+)\)', text):
            if not urlsplit(ref).scheme and not (skill / ref.split('#')[0]).is_file():
                errors.append(f'{skill.name}: {ref}')
        result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(skill / 'scripts'), '-p', 'test_*.py', '-v'], cwd=skill)
        if result.returncode:
            errors.append(f'{skill.name}: 테스트 실패')
    if errors:
        raise ValueError('\n'.join(errors))
    print(json.dumps({'status': 'PASS', 'sections': len(sections), 'html_links': len(parser.links), 'skills': len(skills)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
