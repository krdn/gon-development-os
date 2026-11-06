#!/usr/bin/env python3
"""단계·링크·흐름도 해시와 PDF의 실제 요청문 보존을 검사한다."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if 'id' in values:
            self.ids.append(values['id'])
        if tag == 'a' and 'href' in values:
            self.links.append(values['href'])


def compact(text):
    return re.sub(r'\s+', '', text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', action='store_true')
    parser.add_argument('--manual-planning', type=Path)
    args = parser.parse_args()
    data = json.loads((ROOT / 'steps.json').read_text())
    overrides = json.loads((ROOT / 'project-steps.json').read_text())
    ids = [step['id'] for step in data['steps']]
    assert len(ids) == len(set(ids)), '중복 단계 ID'
    for step in data['steps']:
        if 3 <= step['id'] <= 9:
            project = {**step, **overrides.get(str(step['id']), {})}
            assert not re.search(r'우유 사기|localStorage|gon-todo-practice|React|정적 웹앱',
                                 json.dumps(project, ensure_ascii=False)), f'내 기획 경로에 예제 내용: {step["id"]}'
        for command in step.get('commands', []):
            if command['kind'] == 'slash':
                assert '\n' not in command['text'], 'Codex 명령은 한 줄씩 복사해야 합니다.'
    page = Page()
    page.feed((ROOT / 'index.html').read_text())
    assert len(page.ids) == len(set(page.ids)), '중복 HTML ID'
    for href in page.links:
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc:
            continue
        if parsed.path:
            assert (ROOT / unquote(parsed.path)).is_file(), f'누락된 연결 파일: {href}'
        elif parsed.fragment:
            assert unquote(parsed.fragment) in page.ids, f'잘못된 이동 대상: {href}'
    for source, artifact, proof in [('planning-map-source.json', 'planning-map.html', 'planning-map-validation.json'),
                                     ('workflow-source.json', 'workflow-map.html', 'workflow-validation.json')]:
        record = json.loads((ROOT / proof).read_text())
        assert record['ok'] and all(record['gates'].get(key) == 'pass'
                                   for key in ['validate', 'deliver', 'check', 'browser-check'])
        for key, file in [('specification', source), ('artifact', artifact)]:
            assert record[key]['sha256'] == hashlib.sha256((ROOT / file).read_bytes()).hexdigest(), f'낡은 흐름도: {file}'
    if args.manual_planning:
        assert args.manual_planning.read_bytes() == (ROOT / 'planning-steps.json').read_bytes(), '관리 매뉴얼과 기획 원본 불일치'
    report = {'steps': len(ids), 'links': len(page.links), 'diagram_bindings': 'PASS', 'pdf': {}}
    if args.pdf:
        from pypdf import PdfReader
        for scenario, file in [('exercise', 'guide.pdf'), ('project', 'project-guide.pdf')]:
            reader = PdfReader(ROOT / file)
            pages = [page.extract_text() or '' for page in reader.pages]
            text = compact('\n'.join(pages))
            if scenario == 'exercise':
                values = {'{{path}}': '/home/gon/dev/apps/gon-todo-practice', '{{name}}': '개인 할 일 앱'}
            else:
                values = {'{{path}}': '/home/내계정/dev/apps/내프로젝트', '{{name}}': '내 프로젝트'}
            expected = ['00에서 문서 폴더부터 준비합니다.', '자신의 홈 경로로 바꾸세요.',
                        '같은 세션·새 세션·resume·fork를 고르는 기준',
                        'P1~P5의 기록이 최종 개발 문서가 되는 과정',
                        'A · 주 기획 Codex', 'A · 개발 Codex']
            prompts = []
            for step in data['steps']:
                entry = {**step, **(overrides.get(str(step['id']), {}) if scenario == 'project' else {})}
                expected.append(entry['title'])
                if entry['prompt']:
                    prompts.append(entry['prompt'])
                prompts.extend(item['text'] for item in entry.get('commands', []))
                prompts.extend(item['text'] for item in entry.get('extra_prompts', []))
            for entry in data['extras']:
                expected.append(entry['title'])
                if entry['prompt']:
                    prompts.append(entry['prompt'])
                prompts.extend(item['text'] for item in entry.get('commands', []))
            for item in expected + prompts:
                values['{{shell_path}}'] = "'" + values['{{path}}'].replace("'", "'\\''") + "'"
                for key, value in values.items():
                    item = item.replace(key, value)
                assert compact(item) in text, f'{file} 내용 누락: {item[:90]}'
            assert all(len(compact(text)) > 50 for text in pages), f'{file} 빈 페이지'
            report['pdf'][file] = {'pages': len(pages), 'complete_prompts': len(prompts), 'all_titles_and_full_prompts': 'PASS'}
        (ROOT / 'pdf-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
