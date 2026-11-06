"""공통 기획 원본을 관리 매뉴얼의 번호와 문맥으로 표시한다."""
from html import escape
import json


def prompt(text, title='Herdr 기획 A의 Codex 대화 입력칸에 붙여 넣기'):
    return ('<div class="prompt"><div class="prompt-head"><b>' + escape(title)
            + '</b><button class="copy" type="button">요청문 복사</button></div><pre>'
            + escape(text) + '</pre></div>')


def render(step):
    step = {**step, **step.get('manual', {})}
    actions = ''.join('<li>' + escape(item) + '</li>' for item in step['actions'])
    settings = ''.join('<tr><td>' + escape(key) + '</td><td>' + escape(value) + '</td></tr>'
                       for key, value in step['settings'])
    checks = ''.join('<li>' + escape(item) + '</li>' for item in step['checks'])
    decision = prompt(step['decision_prompt'], '개발하지 않을 때 · 결정 기록') if step.get('decision_prompt') else ''
    documents = ''.join('<li><code>' + escape(path) + '</code> · ' + escape(owner)
                        + ' · ' + escape(purpose) + '</li>'
                        for path, owner, purpose in step.get('documents', []))
    commands = ''.join(prompt(item['text'], item['title'] + ' · ' + item['note'])
                       for item in step.get('commands', []))
    extras = ''.join(prompt(item['text'], item['title'] + ' · ' + item['target'])
                     for item in step.get('extra_prompts', []))
    session = step['session']['text']
    if session.startswith('00에서 '):
        session = 'Herdr 준비 단계에서 ' + session[len('00에서 '):]
    return (f'<div class="place"><b>열 창</b>{escape(step["window"])}</div>'
            + f'<p><b>세션</b> {escape(session)}</p>'
            + f'<p>{escape(step["explain"])}</p><h3>저장·확인할 파일</h3><ul>{documents}</ul>'
            f'<h3>사용자가 진행할 순서</h3><ol>{actions}</ol>'
            '<div class="table-wrap"><table><thead><tr><th>정할 항목</th><th>내용</th></tr></thead>'
            f'<tbody>{settings}</tbody></table></div>' + commands + prompt(step['prompt']) + extras
            + '<div class="example"><b>AI와 주고받는 예시 · 실제 조사 결과 아님</b><p>'
            + escape(step['dialog']).replace('\n', '<br>') + '</p></div>'
            + f'<div class="pair"><div><h3>확인할 결과</h3><ul>{checks}</ul></div>'
            + f'<div class="gate"><h3>다음 행동</h3><p>{escape(step["next"])}</p></div></div>'
            + f'<p class="failure"><b>막히면</b> {escape(step["fail"])}</p>' + decision).replace('{{shell_path}}', "'[실제 프로젝트 경로]'").replace(
                '{{path}}', '[실제 프로젝트 경로]').replace('{{name}}', '[프로젝트 이름]')


def read_sections(root):
    sections = json.loads((root / 'manual/sections.json').read_text())
    planning = json.loads((root / 'manual/planning-steps.json').read_text())
    by_label = {step['label']: step for step in planning}
    if len(by_label) != len(planning):
        raise ValueError('기획 단계 라벨이 중복되었습니다.')
    for section in sections:
        if 'planning_label' not in section:
            continue
        step = by_label[section['planning_label']]
        section['title'] = f'{step["label"]} {step["title"]}'
        section['intro'] = step['goal']
        section['body'] = render(step)
    return sections
