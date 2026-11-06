#!/usr/bin/env python3
"""구조화한 안내 내용으로 오프라인 HTML을 생성한다."""
from pathlib import Path
import html
import json

ROOT = Path(__file__).resolve().parent


def load(name):
    return json.loads((ROOT / name).read_text())


def esc(text):
    return html.escape(str(text))


def templ(text):
    return f'<span data-template="{esc(text)}">{esc(text)}</span>'


def promptbox(text, primary=False, title='Codex에 보낼 요청문', target='', kind='prompt'):
    if not text:
        return '<div class="notice">이 단계는 파일 앱에서 직접 합니다. 채팅에 입력할 내용은 없습니다.</div>'
    marker = ' data-primary' if primary else ''
    destination = f'<p class="input-target">{esc(target)}</p>' if target else ''
    return (f'<div class="prompt" data-kind="{kind}"><div class="prompt-bar"><b>{esc(title)}</b>'
            '<button class="copy" type="button">복사</button></div>' + destination
            + f'<pre tabindex="0"{marker} data-template="{esc(text)}">{esc(text)}</pre></div>')


def commandboxes(entry):
    return ''.join(promptbox(item['text'], title=item['title'], target=item['note'],
                             kind=item['kind']) for item in entry.get('commands', []))


def extra_prompts(entry):
    return ''.join(promptbox(item['text'], title=item['title'], target=item['target'])
                   for item in entry.get('extra_prompts', []))


def variant(step, scenario):
    number = step['id']
    settings = ''.join(f'<tr><th scope="row">{esc(a)}</th><td>{templ(b)}</td></tr>'
                       for a, b in step['settings'])
    actions = ''.join(f'<li>{templ(x)}</li>' for x in step['actions'])
    checks = ''.join(f'<label><input type="checkbox" data-check="{number}-{i}">'
                     f'{templ(x)}</label>' for i, x in enumerate(step['checks']))
    screen = ''.join(f'<div>{templ(x)}</div>' for x in step['screen'])
    destination = step['window']
    notice = (f'<div class="notice"><strong>어디에 입력하나요?</strong>'
              '<p>자연어 요청은 Codex 입력칸, 쉘 명령은 Codex가 실행되지 않은 칸에 넣습니다.</p></div>'
              if step['prompt'] else '')
    print_destination = '<p class="print-destination">아래 요청문은 Codex 대화 입력칸에 보냅니다. 쉘 명령과 구분하세요.</p>' if step['prompt'] else ''
    state = step['session']
    session_info = (f'<div class="session-card"><b>세션 · {esc(state["kind"])}</b>'
                    f'<p>{esc(state["text"])}</p></div>')
    rows = ''.join(f'<tr><th scope="row"><code>{esc(path)}</code></th><td>{esc(owner)}</td><td>{esc(purpose)}</td></tr>'
                   for path, owner, purpose in step.get('documents', []))
    documents = ('<section class="document-card"><h3>이 단계에서 읽고 남길 파일</h3>'
                 '<div class="table-wrap"><table><thead><tr><th>파일</th><th>누가</th><th>남기는 내용</th></tr></thead>'
                 f'<tbody>{rows}</tbody></table></div></section>') if rows else ''
    explanation = f'<p class="plain-explanation"><b>쉽게 이해하기</b> {esc(step["explain"])}</p>'
    dialogue = ('<div class="dialogue"><h3>AI와 이렇게 주고받으세요 · 설명용 예시</h3><p>'
                + esc(step['dialog']).replace('\n', '<br>') + '</p></div>'
                if step.get('dialog') else '')
    return f'''<div class="scenario" data-scenario="{scenario}"{' hidden' if scenario == 'project' else ''}>
<header class="step-head"><div class="num">{esc(step['label'])}</div><div>
<div class="eyebrow">열 창 · {esc(step['window'])}</div>
<h2 tabindex="-1">{esc(step['title'])}</h2><p>{esc(step['goal'])}</p></div></header>{session_info}{explanation}
<div class="step-grid"><div><h3>① 이 순서로 누르세요</h3><ol>{actions}</ol>
<h3>② 이렇게 설정하세요</h3><table>{settings}</table></div><aside>
<div class="mock-caption">설명용 도식 · 실제 앱 스크린샷 아님</div><div class="mock">{screen}</div>{notice}</aside></div>
{documents}<h3>③ 표시된 입력칸에 복사하세요</h3>{commandboxes(step)}{print_destination}{promptbox(step['prompt'], primary=True, target=destination)}{extra_prompts(step)}{dialogue}
<div class="step-grid"><div class="check-card"><h3>④ 직접 확인한 항목만 체크</h3>{checks}</div>
<div class="failure"><h3>막히면 이렇게 하세요</h3><p>{templ(step['fail'])}</p></div></div>
<p class="next">{esc(step['next'])}</p></div>'''


def main():
    development = load('development-steps.json')
    planning = load('planning-steps.json')
    overrides = load('project-steps.json')
    entries = load('entrypoints.json')
    for s in development:
        s['kind'] = 'development'
    for s in planning:
        s['kind'] = 'planning'
    steps = development[:1] + planning + development[1:]
    ids = [s['id'] for s in steps]
    if len(ids) != len(set(ids)):
        raise ValueError('단계 ID가 중복되었습니다.')
    if any(int(key) not in ids for key in overrides):
        raise ValueError('존재하지 않는 단계의 내 기획 내용입니다.')
    routes = {
        14: '<a data-goto="13" href="#step-13">근거 부족 → P3</a><a data-goto="11" href="#step-11">문제 재정의 → P1</a><a data-goto="15" href="#step-15">직접 개발 → P5</a><a data-extra="planning-finish" href="#planning-finish">개발하지 않고 결정 기록</a>',
        0: '<a data-goto="11" href="#step-11">아이디어부터 → P1</a><a data-goto="1" href="#step-1">최종 기획이 이미 있음 → 01</a>',
        15: '<button type="button" data-project-start>내 기획으로 새 개발 세션 → 01</button>',
        7: '<a data-goto="10" href="#step-10">로컬 완료 → 10 기록</a><a data-goto="8" href="#step-8">GitHub에 보관 → 08</a>',
        8: '<a data-goto="10" href="#step-10">보관만 하고 마침 → 10</a><a data-goto="9" href="#step-9">배포 준비 → 09</a>',
    }
    body = []
    for step in steps:
        number = step['id']
        project = {**step, **overrides.get(str(number), {})}
        kind = ' planning-step' if step['kind'] == 'planning' else ''
        choices = f'<nav class="route-choices" aria-label="{esc(step["label"])} 단계의 다음 행동">{routes[number]}</nav>' if number in routes else ''
        body.append(f'<article id="step-{number}" class="step{kind}" data-step="{number}">'
                    + variant(step, 'exercise') + variant(project, 'project') + choices + '</article>')
    extra_html = ''
    for entry in entries:
        action = commandboxes(entry) + promptbox(entry['prompt'], target='표시한 역할의 Codex 대화 입력칸')
        extra_html += (f'<details id="{entry["id"]}"><summary>{esc(entry["title"])}</summary>'
                       f'<p>{esc(entry["desc"])}</p>{action}</details>')
    flow = ''
    for letter, title in [('A', '준비하기'), ('B', '만들기'), ('C', '확인하기'), ('D', '보관·마무리')]:
        flow += f'<section class="phase"><h3><span>{letter}</span>{title}</h3>'
        for index, step in enumerate(s for s in development if s['phase'] == letter):
            if index:
                flow += '<div class="arrow" aria-hidden="true">↓</div>'
            number = step['id']
            optional = ' optional' if number in [8, 9] else ''
            project_window = overrides.get(str(number), {}).get('window', step['window'])
            flow += (f'<a class="node{optional}" href="#step-{number}" data-goto="{number}">'
                     f'<span class="node-num">{step["label"]}</span><span><b>{esc(step["short"])}</b>'
                     f'<small data-exercise="{esc(step["window"])}" data-project="{esc(project_window)}">{esc(step["window"])}</small></span><span class="node-status" id="status-{number}"></span></a>')
        if letter == 'C':
            flow += '<p class="branch">실패 ↺ 05 → 06 → 07<br>로컬 완료 → 10 · 원격 보관 → 08</p>'
        if letter == 'D':
            flow += '<p class="branch">08 보관 후 → 10<br>배포 선택 시에만 09 → 10</p>'
        flow += '</section>'
    planning_flow = '<section class="planning-map" aria-label="개발 전 기획과 리서치"><h2>먼저, 무엇을 만들지 함께 알아봅니다</h2><div class="planning-nodes">'
    for step in planning:
        number = step['id']
        planning_flow += (f'<a class="node" href="#step-{number}" data-goto="{number}">'
                          f'<span class="node-num">{step["label"]}</span><span><b>{esc(step["short"])}</b>'
                          '<small>기획 A · 같은 세션</small></span>'
                          f'<span class="node-status" id="status-{number}"></span></a>')
    planning_flow += ('</div><p class="branch">P2 → P1 문제 좁히기 · P3 → P2 조사 범위 조정 · P4 → P3 추가 근거 / P1 재정의<br>'
                      '직접 개발 → P5 최종 문서 → 01 새 개발 세션 · 기존 도구 사용/보류 → 기록 후 종료</p>'
                      '<p class="branch"><a href="#step-0" data-goto="0">00에서 분할 터미널·문서 폴더를 먼저 준비</a>합니다. 승인된 기획이 이미 있으면 P1~P5를 다시 할 필요는 없습니다.</p></section>')
    config = {'steps': [{'id': s['id'], 'label': s['label'], 'kind': s['kind']} for s in steps],
              'choiceSteps': [14, 7, 8]}
    config_json = json.dumps(config, ensure_ascii=False).replace('<', '\\u003c')
    replacements = {'CSS': (ROOT / 'style.css').read_text(), 'JS': (ROOT / 'viewer.js').read_text(),
                    'BODY': ''.join(body), 'FLOW': flow, 'PLANNING_FLOW': planning_flow,
                    'EXTRAHTML': extra_html, 'CONFIG': config_json,
                    'HANDBOOK': (ROOT / 'handbook.html').read_text()}
    page = (ROOT / 'template.html').read_text()
    for key, value in replacements.items():
        page = page.replace(f'@@{key}@@', value)
    if '@@' in page:
        raise ValueError('미처리 템플릿 항목이 있습니다.')
    (ROOT / 'index.html').write_text(page)
    (ROOT / 'steps.json').write_text(json.dumps({'steps': steps, 'extras': entries}, ensure_ascii=False, indent=2) + '\n')
    print(f'안내서 생성: {len(steps)}단계, 예제·내 기획 2경로, {len(entries)}개 별도 입구')


if __name__ == '__main__':
    main()
