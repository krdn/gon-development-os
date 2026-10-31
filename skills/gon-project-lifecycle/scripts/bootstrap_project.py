#!/usr/bin/env python3
"""선택한 프로젝트 문서의 생성 계획을 출력하고, --apply일 때 없는 파일만 쓴다."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from urllib.parse import quote


ASSETS = Path(__file__).resolve().parents[1] / 'assets' / 'project'
DOCUMENTS = {
    'product': ('PRODUCT.md', 'docs/PRODUCT.md', [
        'PROJECT.md', 'PRODUCT.md', 'docs/product.md',
    ]),
    'architecture': ('ARCHITECTURE.md', 'docs/ARCHITECTURE.md', [
        'ARCHITECT.md', 'ARCHITECTURE.md', 'docs/architecture.md',
    ]),
    'plan': ('PLAN.md', 'docs/PLAN.md', ['PLAN.md', 'docs/plan.md']),
    'state': ('STATE.md', 'docs/STATE.md', ['STATE.md', 'docs/state.md']),
    'agents': ('AGENTS.md', 'AGENTS.md', ['AGENTS.override.md']),
    'readme': ('README.md', 'README.md', ['README.rst', 'README']),
}
LABELS = {
    'product': '제품 범위', 'architecture': '구조', 'plan': '다음 작업',
    'state': '현재 상태', 'agents': '작업 지침', 'readme': '시작 안내',
}
CHOICES = ('product', 'architecture', 'plan', 'state', 'entrypoints')


def check_path(path, directory=False):
    """기존 경로의 링크와 파일/폴더 충돌을 쓰기 전 확인한다."""
    for ancestor in reversed((path, *path.parents)):
        if ancestor.is_symlink():
            raise ValueError(f'심볼릭 링크 경로는 직접 확인이 필요합니다: {ancestor}')
        if ancestor.exists() and ancestor != path and not ancestor.is_dir():
            raise ValueError(f'상위 경로가 폴더가 아닙니다: {ancestor}')
    if path.exists():
        valid = path.is_dir() if directory else path.is_file()
        if not valid:
            raise ValueError(f'파일/폴더 경로가 충돌합니다: {path}')


def find_existing(root, key):
    _, target, alternatives = DOCUMENTS[key]
    found = []
    for relative in [*alternatives, target]:
        path = root / relative
        check_path(path)
        if path.is_file() and relative not in found:
            found.append(relative)
    return found


def render(template, name, links):
    content = (ASSETS / template).read_text(encoding='utf-8')
    return content.replace('{{DOCUMENT_LINKS}}', links).replace('{{PROJECT_NAME}}', name)


def make_plan(root, name, selected):
    check_path(root, directory=True)
    for marker in ('.ai/contracts', '.ai/tasks', 'scripts/aeos.py'):
        path = root / marker
        check_path(path, directory=marker.startswith('.ai/'))
        if path.exists():
            raise ValueError(
                f'AEOS 구성요소를 발견했습니다: {marker}. '
                'references/aeos.md에 따라 부분 도입 여부와 기존 문서를 확인하세요.'
            )

    keys = set(selected) - {'entrypoints'}
    if 'entrypoints' in selected:
        keys.update(('agents', 'readme'))
    inspected = DOCUMENTS if 'entrypoints' in selected else keys
    existing = {key: find_existing(root, key) for key in inspected}
    resolved = {}
    for key, (_, target, _) in DOCUMENTS.items():
        found = existing.get(key, [])
        if found or key in keys:
            resolved[key] = found[0] if found else target

    files, contents, reviews = [], {}, []
    if 'entrypoints' in selected:
        for relative in ('CLAUDE.md', '.claude/CLAUDE.md'):
            path = root / relative
            check_path(path)
            if path.is_file():
                reviews.append({
                    'paths': [relative], 'reason': '기존 Claude 지침을 읽고 진입점과 충돌·중복 확인',
                })
    for key, (template, target, _) in DOCUMENTS.items():
        if key not in keys:
            continue
        relative = resolved[key]
        action = 'preserve' if existing[key] else 'create'
        item = {'document': key, 'path': relative, 'action': action}
        if action == 'preserve':
            reviews.append({'paths': existing[key], 'reason': '기존 내용을 읽고 필요한 연결만 병합'})
        else:
            links = '\n'.join(
                f'- [{LABELS[other]}]({quote(path, safe="/")})'
                for other, path in resolved.items() if other != key
            ) or '기준 문서: 미정 — 기존 프로젝트 문서를 확인해 연결한다.'
            contents[relative] = render(template, name, links)
            item['sha256'] = hashlib.sha256(contents[relative].encode('utf-8')).hexdigest()
        files.append(item)
    return {
        'status': 'planned', 'project': str(root), 'scaffold_only': True,
        'files': files, 'review_required': reviews,
    }, contents


def apply_plan(root, report, contents):
    report['status'] = 'applied'
    try:
        for item in report['files']:
            if item['action'] != 'create':
                continue
            path = root / item['path']
            check_path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            check_path(path)
            try:
                # 다른 프로세스가 생성한 파일도 덮어쓰지 않는다.
                with path.open('x', encoding='utf-8', newline='\n') as stream:
                    item['action'] = 'writing'
                    stream.write(contents[item['path']])
            except FileExistsError:
                item['action'] = 'preserve'
                item.pop('sha256', None)
                report['review_required'].append({
                    'paths': [item['path']], 'reason': '계획 후 생성된 기존 파일 보존',
                })
            else:
                item['action'] = 'created'
    except (OSError, ValueError) as error:
        report['status'] = 'partial'
        report['error'] = str(error)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True, help='대상 프로젝트 경로')
    parser.add_argument('--name', help='표시할 프로젝트 이름. 기본은 폴더 이름')
    parser.add_argument('--documents', nargs='+', choices=CHOICES, required=True,
                        help='필요한 문서만 선택. entrypoints는 AGENTS와 README')
    parser.add_argument('--apply', action='store_true', help='없는 문서만 실제 생성')
    args = parser.parse_args(argv)
    root = Path(os.path.abspath(args.project.expanduser()))
    name = args.name if args.name is not None else root.name
    try:
        if not name.strip() or any(ord(char) < 32 for char in name):
            raise ValueError('프로젝트 이름은 비어 있지 않은 한 줄이어야 합니다.')
        report, contents = make_plan(root, name, args.documents)
        if args.apply:
            report = apply_plan(root, report, contents)
    except (OSError, ValueError) as error:
        report = {'status': 'blocked', 'project': str(root), 'error': str(error)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report['status'] in ('blocked', 'partial') else 0


if __name__ == '__main__':
    sys.exit(main())
