#!/usr/bin/env python3
"""내용 원본에서 오프라인 Orca 실행 안내서를 생성한다."""
from pathlib import Path
import html
import json

ROOT = Path(__file__).resolve().parent

def e(value):
    return html.escape(str(value))

def box(text, title='주 조정 Codex에 보낼 요청문', kind='prompt', note=''):
    return (f'<div class="copybox" data-kind="{e(kind)}"><div class="copyhead"><b>{e(title)}</b>'
            f'<button type="button" class="copy">복사</button></div>'
            f'<pre tabindex="0" data-template="{e(text)}">{e(text)}</pre>'
            + (f'<p class="copy-note">{e(note)}</p>' if note else '') + '</div>')

def table(headers, rows):
    return f'<div class="tablewrap" tabindex="0" role="region" aria-label="{e(headers[0])} 표 · 가로로 이동해 전체 내용 읽기"><table><thead><tr>'+''.join(f'<th scope="col">{e(x)}</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{e(x)}</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'

def render_step(s):
    checks=''.join(f'<label><input type="checkbox" data-check="{e(s["id"])}-{i}"><span>{e(v)}</span></label>' for i,v in enumerate(s['checks']))
    commands=''.join(box(c['text'],c['label'],c.get('kind','shell'),c.get('note','')) for c in s.get('commands',[]))
    extras=''.join(box(c['text'],c['label']) for c in s.get('extras',[]))
    return f'''<details class="step" id="step-{e(s['id'])}" {'open' if s['id']=='S0' else ''}>
<summary><span class="stepno">{e(s['id'])}</span><span><strong>{e(s['title'])}</strong><small>{e(s['goal'])}</small></span><span class="expand" aria-hidden="true">＋</span></summary>
<div class="stepbody"><div class="context"><p><b>열 창</b> {e(s['where'])}</p><p><b>세션</b> {e(s['session'])}</p></div>
<h3>1. 이 순서로 진행하세요</h3><ol>{''.join(f'<li>{e(v)}</li>' for v in s['actions'])}</ol>
<div class="twocol"><div><h3>읽을 것</h3><ul>{''.join(f'<li>{e(v)}</li>' for v in s['reads'])}</ul></div><div><h3>남길 것</h3><ul>{''.join(f'<li>{e(v)}</li>' for v in s['writes'])}</ul></div></div>
<h3>2. 표시된 입력 위치에 복사하세요</h3>{commands}{box(s['prompt'])}{extras}
<h3>3. 실제로 확인한 항목만 체크하세요</h3><div class="checks">{checks}</div>
<div class="notice"><b>막히면</b><p>{e(s['fail'])}</p></div><p class="next">다음 · {e(s['next'])}</p></div></details>'''

steps=json.loads((ROOT/'steps.json').read_text())
assert len({s['id'] for s in steps})==len(steps)
by_id={s['id']:s for s in steps}
lanes=[('준비','폴더와 입력 위치',['S0']),('기획·기준 저장','같은 주 조정 세션',['P1','P2','P3','P4','P5','G1']),('개발','새 개발 조정 세션',['D1','D2','D3','D4']),('전달','원격·실제 동작 확인',['G2','D5'])]
short={'S0':'Orca · Codex CLI 열기','P1':'문제와 내 답변 저장','P2':'조사 질문 · 파일 분담','P3':'작업자 조사 → 근거표','P4':'대안 비교 · 실제 선택','P5':'최종 개발 문서 3종','G1':'GitHub에 기준 저장','D1':'새 개발 세션에 인계','D2':'이슈 · Task · 파일 연결','D3':'개발 작업자 실행','D4':'결과 검수 · 통합 시험','G2':'PR · CI · 이슈 확인','D5':'실제 전달 · 재개 기록'}
map_html=''
for i,(name,sub,ids) in enumerate(lanes):
    nodes=''.join(f'<a class="mapnode" href="#step-{id}"><b>{id}</b><span>{short[id]}</span></a>'+('<span class="down" aria-hidden="true">↓</span>' if n<len(ids)-1 else '') for n,id in enumerate(ids))
    map_html+=f'<div class="lane"><div class="lanehead"><span>0{i+1}</span><h3>{name}</h3><p>{sub}</p></div>{nodes}</div>'
resume_prompt='''현재 docs/STATE.md와 최종 문서·TASKS를 읽고 실제 파일·Git 상태·미커밋 변경을 대조해줘.
STATE의 Orca Run/Task/Dispatch를 현재 상태와 비교하고, 이전 조정자가 살아 있는지 먼저 확인해.
이전 조정자가 종료된 것이 확인되고 내가 그 작업을 이어받는 경우에만 설치 가이드에 따라 기존 Run을 다시 연결해. 아직 실행 중인 작업자를 중복 시작하지 마.
완료·실패·미검증·다음 행동 하나를 요약한 뒤 같은 승인 범위의 작업을 이어가.'''
save_prompt='''중단 전에 docs/STATE.md를 갱신해줘. 현재 단계, 최종 문서 버전, 실제 파일·미커밋 변경, 기준/현재 커밋, GitHub 이슈·PR, Run·Task·Dispatch, 활성 작업자, 남은 문제, 다음 행동을 적어.
아직 실행 중인 작업자가 있으면 현재 조정 세션을 종료해도 되는지 실제 상태와 설치 가이드 기준으로 알려줘. 종료를 확인하지 못하면 종료됐다고 쓰지 마.
저장한 파일을 다시 읽어 경로와 다음에 보낼 재개 요청을 알려줘.'''
session_rows=[
['P1 → P2 → P3 → P4 → P5','같은 기획 세션','단계마다 /new를 누르지 않음. 파일로 합의를 고정.'],
['독립 조사·구현을 맡김','새 작업자 세션','주 조정자가 worker-start. 동일 대화를 동시에 resume하지 않음.'],
['작업자가 일하는 중','주 조정자 유지','응답은 끝내고 Orca 알림을 기다림. 탭·CLI는 종료하지 않음.'],
['내일 같은 일을 이어서 함','기존 세션 resume','같은 프로젝트·같은 Codex 설정 홈에서 이름/ID 확인.'],
['P5·Git 기준 저장 → 개발','새 개발 조정 세션','최종 문서 3종을 읽고 시작. 활성 기획 작업은 먼저 정리.'],
['첫 출시 안의 수정·검증','같은 개발 세션','작은 구현·검증을 반복하고 관련 작업자에게 send.'],
['첫 출시 완료 → 독립 새 기능','새 세션·새 작업 묶음','최신 문서·이슈에서 시작. 이전 결과를 인계.'],
['대안만 따로 탐색','필요하면 fork','대화 분기이며 Git 브랜치/worktree 분리와 다름.'],
['대화가 길어짐','문서 저장 후 compact','맥락 요약일 뿐 파일·GitHub·Run 상태 저장을 대신하지 않음.']]
terms=[['Codex 세션','AI와 이어지는 한 대화','기획과 개발을 구분하는 단위'],['Orca 작업공간','폴더 또는 Git checkout과 탭이 모인 자리','같은 폴더의 여러 AI는 파일을 공유함'],['Git worktree','같은 저장소를 다른 폴더에서 다루는 별도 작업 사본','병렬 코드 수정 충돌을 줄이나 통합은 별도 필요'],['Run','이번 목표를 묶는 작업판','예: 첫 출시 개발'],['Task','목표 안의 작업 항목','예: 저장 기능 구현'],['Dispatch','Task를 실제 작업자에게 맡긴 실행 1회','재시도는 같은 Task의 다른 실행이 될 수 있음'],['GitHub Issue','해결할 문제와 완료 기준의 원격 기록','Orca Task ID와 다른 번호'],['PR / CI','변경 검토·병합 요청 / 서버의 자동 검사','실제 제품 사용 확인과 구분']]
files_rows=[
['P1','research/01-problem.md','질문·내 답변·문제·제약·미정','주 조정자'],
['P2','research/02-research-plan.md','Q번호·조사 방법·담당·종료 기준','주 조정자'],
['P3 전','research/notes/*.md','작업자별 원문 조사와 한계','각 작업자 자기 파일'],
['P3','research/03-evidence.md','Q에 답하는 S/U 근거·날짜·해석·빈틈','주 조정자 통합'],
['P4','research/04-decision.md','D번호·선택·이유·근거·보류·재검토','주 조정자 + 내 실제 선택'],
['P5','PROJECT-BRIEF.md','무엇을 만들고 무엇으로 확인할지','주 조정자'],
['P5 → D2','TASKS.md','어떤 순서·담당 파일·R/AC로 실행할지','주 조정자'],
['모든 단계','STATE.md','지금 어디까지 했고 다음에 무엇을 할지','주 조정자']]
commands_reference='''# 아래는 AI가 실제 ID·브랜치를 채워 사용할 참고 형식입니다.
# 이 상자는 그대로 실행하지 않습니다. 중괄호 값은 실제 조회 결과로 대체합니다.

# 조사: 같은 작업공간, 분리된 파일. --spec은 필요 시 Run을 자동 생성합니다.
orca-ide terminal create --worktree current --title research-a --command 'codex --yolo' --json
orca-ide terminal wait --terminal {TERMINAL_HANDLE} --for tui-idle --timeout-ms 60000 --json
orca-ide orchestration worker-start --spec-file {지시서_절대경로} --worktree current --terminal {TERMINAL_HANDLE} --json

# 선행 관계가 있는 계획: Run 생성 후 Task와 의존성 기록
orca-ide orchestration run-create --objective "첫 출시 개발" --json
orca-ide orchestration task-create --spec-file docs/tasks/base.md --json
orca-ide orchestration task-create --spec-file docs/tasks/feature.md --deps '["{실제_선행_TASK_ID}"]' --json
orca-ide orchestration task-list --ready --brief

# 코드 작업: 실제 저장소·기준 브랜치에서 새 worktree
orca-ide worktree create --repo id:{REPO_ID} --name feature-one --base-branch {기준_브랜치} --json
orca-ide terminal create --worktree {WORKTREE_SELECTOR} --title feature-one --command 'codex --yolo' --json
orca-ide terminal wait --terminal {TERMINAL_HANDLE} --for tui-idle --timeout-ms 60000 --json
orca-ide orchestration worker-start --task {TASK_ID} --worktree {WORKTREE_SELECTOR} --terminal {TERMINAL_HANDLE} --json

# 추가 지시 / 결과 확인
orca-ide orchestration send --to dispatch:{DISPATCH_ID} --subject "검증 보완" --body "AC04의 새로고침 확인 결과를 추가해줘" --json
orca-ide orchestration worker-read --dispatch {DISPATCH_ID} --source auto --limit 80 --json

# 질문에 답하기 (사용자의 기존 범위 안에서)
orca-ide orchestration reply --id {MESSAGE_ID} --body "확정된 답변" --json

# 재개 시 상태 확인. 실제 소유권 확인 전 run-use를 무조건 실행하지 않음.
orca-ide orchestration run-list --json
orca-ide orchestration worker-list --run {RUN_ID} --include-remote --json
orca-ide orchestration run-use --id {RUN_ID} --json

# GitHub 전체 URL을 실제 작업공간에 연결
orca-ide reference add {ISSUE_URL} {PR_URL} --worktree {WORKTREE_SELECTOR} --json
'''
resume_command = 'cd {{shell_path}}\ncodex resume --search'
example=(ROOT/'example-project/docs/PROJECT-BRIEF.md').read_text()
html_doc=f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Orca + Codex CLI · Gon 개발 실행 안내서</title><link rel="stylesheet" href="style.css"></head>
<body><a class="skip" href="#main">본문으로 이동</a>
<header class="hero"><div class="eyebrow">GON AI DEVELOPMENT OS · ORCA EDITION 1.0</div><h1>어떤 창에서, 무엇을 입력하고,<br>어디에 남길까요?</h1><p class="lead">Orca + Codex CLI로 아이디어를 조사하고, 작업자를 조정하고,<br>GitHub에 연결해 실제 개발까지 이어가는 실행 안내서.</p><div class="chips"><span>P1~P5 전체 Codex CLI</span><span>세션 유지·재개·새 시작</span><span>문서 → 작업자 → PR</span></div><p class="meta">확인 기준 2026-11-02 · Orca CLI 1.4.246 · Codex CLI 0.166.0<br>설치 가이드·도움말과 공식 문서를 대조한 교육용 안내서입니다.</p></header>
<nav class="topnav" aria-label="안내서 목차"><a href="#map">전체 흐름</a><a href="#workbench">화면 배치</a><a href="#sessions">세션 판단</a><a href="#documents">문서 연결</a><a href="#steps">실행 단계</a><a href="#examples">예시·양식</a><a href="#trouble">막혔을 때</a></nav>
<main id="main">
<section class="panel" id="start"><div class="section-label">먼저 2분</div><h2>이 안내서는 이렇게 사용하세요</h2><ol><li>아래 프로젝트명과 폴더를 내 값으로 바꿉니다. 아직 GitHub 이름을 정하지 않았다면 비워 두고 G1 전에 입력합니다.</li><li>흐름도에서 <b>S0</b>를 누릅니다. 단계의 “열 창 → 순서 → 요청문 → 확인”을 따라갑니다.</li><li>자연어 요청문은 <b>Codex 입력칸</b>에, 명령은 <b>일반 터미널</b>에 붙여 넣습니다. 복사 버튼은 명령을 실행하지 않습니다.</li></ol>
<form id="config"><div><label for="project-name">프로젝트명</label><input id="project-name" value="내 프로젝트" required maxlength="80"></div><div><label for="project-path">프로젝트 폴더 · 절대 경로</label><input id="project-path" value="/home/gon/dev/apps/my-project" required spellcheck="false"></div><div><label for="repo-name">GitHub 소유자/저장소 · G1 전 입력</label><input id="repo-name" placeholder="예: my-account/my-project" spellcheck="false"></div><button type="submit">요청문에 반영</button></form><p class="small">처음 보이는 폴더는 예시입니다. 실제 폴더를 만든 뒤 그 경로로 바꾸세요. 설정·확인 체크는 현재 브라우저에 저장됩니다. 다른 기기나 PDF에는 자동 동기화되지 않습니다.</p><p id="config-status" role="status">내 프로젝트의 값을 입력하세요.</p><div class="actionbar"><button id="expand-all" type="button">모든 단계 펼치기</button><button id="print" type="button">현재 설정으로 인쇄 / PDF</button><a class="button" href="guide.pdf">기본 PDF 열기</a><span id="progress" role="status"></span></div></section>
<section class="panel" id="map"><div class="section-label">전체 흐름 · 단계를 누르면 상세 설명이 열립니다</div><h2>기획은 같은 대화, 개발은 문서를 읽는 새 대화</h2><div class="flowmap">{map_html}</div><div class="branch"><b>P4 선택</b><a href="#step-P3">근거 부족 → P3</a><a href="#step-P1">문제가 달라짐 → P1</a><span>기존 도구 사용·보류 → 결정과 STATE 저장 후 종료</span></div><p class="small">G1까지는 같은 기획 주 조정자가 마무리합니다. 활성 조사 작업과 문서 저장을 정리한 뒤 D1에서 새 개발 세션을 엽니다.</p></section>
<section class="panel" id="workbench"><div class="section-label">화면 배치</div><h2>사용자는 주 조정자와 대화하고, 주 조정자가 작업자를 관리합니다</h2><div class="workspace"><aside><b>Orca 작업공간</b><p>내 프로젝트</p><span>기획 또는 개발 탭</span><span>명령·확인 터미널</span><span>파일 목록 / 변경 보기</span><span>작업자별 worktree</span></aside><div class="workspace-main"><div class="tabs"><b>주 조정 Codex · CLI</b><span>명령·확인</span><span>문서 보기</span></div><div class="coordinator"><strong>나 ↔ 주 조정자</strong><p>목표·선택·질문·진행·검수·통합</p></div><div class="arrow-note">↓ 작업 지시와 담당 파일 전달　 ↑ 결과·질문·실패 보고</div><div class="workers"><div><b>조사 A / 개발 A</b><p>지정 파일만 작성</p><small>독립 Codex 세션</small></div><div><b>조사 B / 개발 B</b><p>다른 파일 또는 worktree</p><small>독립 Codex 세션</small></div></div></div></div><p class="small">설명용 배치도이며 실제 Orca 화면 캡처가 아닙니다. 탭·분할 방식은 기존 사용자 설정을 따릅니다.</p><div class="twocol"><div><h3>기획할 때</h3><p>주 조정자와 조사 작업자가 같은 폴더를 쓸 수 있습니다. 결과 파일을 다르게 지정하고 통합 문서는 주 조정자만 수정합니다.</p></div><div><h3>코드를 병렬로 고칠 때</h3><p>충돌 가능한 작업은 Orca가 만든 별도 worktree에 배치합니다. 작업자는 자신의 커밋과 PR을 보고하고 주 조정자가 결과를 통합합니다.</p></div></div><p class="notice"><b>CLI 모드 확인:</b> 주 조정자는 agent launch의 <code>--surface terminal</code>로 CLI를 선택할 수 있습니다. worker-start에는 같은 옵션이 없으며 사용자의 새 에이전트 Chat | CLI 설정을 따릅니다. CLI를 원하면 Settings → Agents → Choose per agent에서 Codex를 Terminal로 맞추고 시작 결과를 확인하세요. 다른 형태로 시작되어도 조정은 같은 orchestration 명령을 사용합니다.</p></section>
<section class="panel" id="sessions"><div class="section-label">세션 판단표</div><h2>지금 대화를 이어갈까요, 새로 시작할까요?</h2>{table(['상황','선택','실제로 할 일'],session_rows)}<p class="source">근거: <a href="https://learn.chatgpt.com/docs/developer-commands#built-in-slash-commands">Codex 공식 명령 설명</a> · <a href="https://learn.chatgpt.com/docs/developer-commands#codex-resume">resume 동작</a> · 설치 Orca orchestration 가이드. “P5 후 새 개발 세션”은 이 안내서의 운영 권장 방식입니다.</p>
<details class="extra"><summary>오늘 멈추고 내일 재개하는 정확한 순서</summary><ol><li>현재 주 조정자에게 아래 “중단 전 저장” 요청을 보냅니다. 활성 작업자가 있으면 그대로 종료하지 말고 상태를 확인합니다.</li><li>기록이 저장되고 종료 가능한 상태이면 현재 Codex에 <code>/quit</code>를 한 줄로 입력합니다.</li><li>다음에 Orca에서 같은 작업공간·같은 실행 환경을 엽니다. 기존 Codex 탭이 살아 있다면 그 탭을 계속 씁니다.</li><li>종료된 경우 일반 터미널에서 아래 resume 명령으로 세션 목록을 열고 프로젝트-기획 또는 프로젝트-개발 이름과 경로를 확인해 선택합니다. 작업자 대화를 잘못 선택하지 않습니다.</li><li>재개 요청을 보냅니다. Codex 대화 복구와 Orca Run 연결은 별도입니다. 이전 조정자가 살아 있다면 같은 Run을 다른 조정자가 빼앗아 관리하지 않습니다.</li></ol>{box(save_prompt,'현재 주 조정자 · 중단 전 저장')}{box('/quit','현재 Codex 입력칸 · 한 줄','slash')}{box(resume_command,'종료된 경우 · Orca 일반 터미널에서 목록 열기','shell','최근 세션 --last는 작업자와 혼동하기 쉬우므로 이름·경로로 선택합니다.')}{box(resume_prompt,'재개한 주 조정 Codex 입력칸')}<p>목록에 대화가 없으면 실행한 사용자·프로젝트 경로·Codex 설정 홈을 확인합니다. Orca가 별도 런타임이나 계정 환경을 썼다면 외부 터미널의 Codex 목록과 다를 수 있습니다. 인증 파일을 옮겨 해결하려 하지 않습니다.</p></details>
<details class="extra"><summary>/new · /fork · /compact를 언제 쓰나요?</summary><p><code>/new</code>는 현재 CLI 안에서 새 대화를 시작합니다. <code>/fork</code>는 이전 대화 맥락을 가진 별도 대화로 분기합니다. 둘 다 Git 변경을 자동 분리하지 않습니다. <code>/compact</code>는 긴 대화를 요약합니다. 작업자가 진행 중인 주 조정자에서는 대화를 바꾸기 전에 조정 상태를 확인하세요.</p><p>기획에서 개발로 넘어갈 때는 새 탭과 명확한 이름을 써서 역할을 구분하는 편을 권합니다. fork는 별도 대안 검토용이며 필수 단계가 아닙니다.</p></details></section>
<section class="panel" id="documents"><div class="section-label">문서 연결 · 모든 경로는 프로젝트의 docs/ 아래</div><h2>리서치 4개 파일을 개발 기준 3종으로 정제합니다</h2><div class="docflow"><div><b>내 말과 조사</b><p>P1 질문·답변<br>P2 Q번호·계획<br>P3 S/U 근거<br>P4 D번호·결정</p></div><span class="bigarrow" aria-hidden="true">→</span><div class="doc-final"><b>P5 최종 문서 3종</b><p>PROJECT-BRIEF · 무엇을 / 완료 기준<br>TASKS · 순서 / 담당 / 검증<br>STATE · 현재 상태 / 다음 행동</p></div><span class="bigarrow" aria-hidden="true">→</span><div><b>개발과 GitHub</b><p>이슈에 R/AC 연결<br>Orca Task에 파일 책임<br>PR에 변경·실제 검증<br>새 세션은 3종부터 읽기</p></div></div>{table(['단계','저장 파일','무엇을 남기는가','누가 쓰는가'],files_rows)}<p class="notice"><b>복사·합치기의 뜻:</b> 원본 4개를 지우고 큰 파일 하나로 만드는 것이 아닙니다. 최종 문서에는 선택된 결론과 실행 기준만 적고, “왜?”에 답할 때 원래 근거로 돌아갈 링크를 둡니다.</p>
<h3>한 요구가 끝까지 이어지는 예</h3>{table(['Q 질문','S/U 근거','D 결정','R 요구','AC 완료 기준','작업 / GitHub'],[['Q02/03 저장 범위·완료 기준','U02 필요하다는 답변 · U03 범위 확인','D02 같은 브라우저 저장','R04 새로고침 유지','AC04 새로고침 후 항목·완료 상태 일치','K03 → 실제 이슈 → 구현 PR']])}<p class="small">설명용 가상 연결입니다. 실제 관찰·승인·GitHub 이슈를 만들었다는 뜻이 아닙니다. 저장 API의 한계가 미확인이면 구현 전에 확인하는 조건으로 유지합니다.</p>
<h3>새 개발 세션에 전달하는 최소 묶음</h3><pre class="tree">프로젝트/\n└─ docs/\n   ├─ PROJECT-BRIEF.md  ← 무엇을 만들고 무엇으로 확인하나\n   ├─ TASKS.md          ← 순서·선행 관계·담당 파일\n   ├─ STATE.md          ← 지금 상태·다음 행동·GitHub·Orca ID\n   ├─ tasks/           ← 작업자별 지시서\n   └─ research/\n      ├─ 01-problem.md\n      ├─ 02-research-plan.md\n      ├─ 03-evidence.md\n      ├─ 04-decision.md\n      └─ notes/        ← 작업자별 조사 메모</pre></section>
<section id="steps"><div class="section-label">실행 단계 · 위에서 아래로</div><h2>창을 열고, 요청하고, 결과를 확인하세요</h2><p>단계가 접혀 있으면 제목을 누르세요. 요청문의 대괄호 부분은 내 사실로 바꿔 보냅니다. AI가 완료라고 말한 뒤에는 파일과 결과를 직접 확인합니다.</p>{''.join(render_step(s) for s in steps)}</section>
<section class="panel" id="gon-documents"><div class="section-label">개발 시작 시 문서 인계</div><h2>P5 문서를 Gon OS의 개발 기준으로 이어갑니다</h2><h3>P5 이후, Gon OS의 개발 문서와 연결하기</h3><p>P5의 PROJECT-BRIEF는 기획 인계 기준입니다. D1에서 개발 중 유지할 제품·구조 문서와 연결합니다. 기존 문서가 우선이며, 필요한 새 프로젝트에서는 PRODUCT.md가 목표·R/AC를, ARCHITECTURE.md가 확정 기술·데이터·구성·제약을 맡습니다. AEOS의 PROJECT.md·ARCHITECT.md가 있으면 그 경로를 유지합니다.</p><p>GitHub 연결 후 진행 상태의 기준은 Issues/기존 Projects입니다. TASKS·STATE는 실제 URL과 Orca ID를 담은 요약입니다. 로컬과 원격에 서로 다른 할 일 목록을 만들지 않습니다.</p><div class="notice"><b>파일을 다시 쓰는 이유:</b> 기획에서 고른 범위를 개발 중 쓰는 제품·구조 문서에 반영하고 원문 결정과 연결하기 위해서입니다. 모든 파일에 같은 내용을 복제하지 않습니다. D1의 두 번째 요청문이 이 작업을 담당합니다.</div></section><section class="panel" id="examples"><div class="section-label">읽고 따라 쓸 수 있는 자료</div><h2>최종 개발 문서의 완성 모양과 빈 양식</h2><p>예시는 “개인 할 일 앱을 학습용으로 만드는 경우”입니다. 실제로 수행한 조사·개발·승인 기록이 아닙니다. 내 프로젝트에는 빈 양식과 실제 답변을 사용하세요.</p><div class="downloads"><a href="example-project/docs/PROJECT-BRIEF.md">최종 문서 예시</a><a href="example-project/docs/TASKS.md">작업 계획 예시</a><a href="example-project/docs/STATE.md">인계 상태 예시</a><a href="templates/PROJECT-BRIEF.md">최종 문서 빈 양식</a><a href="templates/TASKS.md">작업 계획 빈 양식</a><a href="templates/STATE.md">상태 빈 양식</a><a href="templates/WORKER-SPEC.md">작업자 지시서 빈 양식</a><a href="examples.html">P1~P5 모든 예시 읽기</a></div><details class="extra"><summary>완성된 PROJECT-BRIEF 예시를 여기서 펼쳐 읽기</summary><pre>{e(example)}</pre></details><p class="small">Markdown(.md)은 글을 저장한 일반 텍스트 파일입니다. 앱이 열리지 않으면 “모든 예시 읽기”에서 브라우저로 확인할 수 있습니다.</p></section>
<section class="panel" id="trouble"><div class="section-label">막혔을 때</div><h2>헷갈리는 상태를 이렇게 구분하세요</h2>{table(['보이는 상황','의미','다음 행동'],[['작업자를 시작했다 / ready','실행 준비 또는 시작 확인','완료 보고와 파일·검증을 기다림'],['주 조정자의 답변이 끝났다','Orca 알림 대기일 수 있음','주 조정 CLI를 닫지 않고 유지'],['worker_done이 왔다','작업자 보고 도착·Task 정리','보고한 성공/실패와 실제 증거 확인'],['작업자 무응답 / timeout','종료 여부 불명일 수 있음','worker-show/read와 recovery 안내로 상태 확인'],['Codex resume 성공','대화 기록을 다시 열었음','Run/Task·실제 파일은 별도로 대조'],['PR을 만들었다','변경 검토 요청이 존재함','최신 CI·리뷰·병합 상태 확인'],['CI가 초록색이다','자동 검사 범위가 통과함','실제 AC 동작·배포 버전 별도 확인']])}<p>자동 재시도 제한에 걸리면 같은 작업을 새 Run/Task로 위장해 반복하지 않습니다. 실제 실패와 남은 자원을 확인해 사용자에게 필요한 선택을 알려야 합니다. 원격 작업자는 로컬과 후속 처리 조건이 다르므로 설치된 placement/recovery 가이드를 읽습니다.</p>
<details class="extra"><summary>Orca 명령의 실제 형태 · AI가 참고할 부록</summary><p>초보자는 실행 단계의 자연어 요청문을 사용하면 됩니다. 아래는 주 조정자가 설치 가이드를 읽고 실제 ID를 대체해 사용할 참고입니다. 그대로 복사 실행할 명령 묶음이 아닙니다.</p><pre>{e(commands_reference)}</pre><p>이 가이드의 직접 명령은 확인한 Linux 실행 파일 <code>orca-ide</code> 기준입니다. Orca 관리 환경의 AI는 ORCA_CLI_COMMAND 등 설치 스킬의 선택 규칙으로 실행 파일을 정하고 계속 같은 것을 사용합니다. CLI별 승인 생략 옵션으로 연 터미널을 worker-start --terminal로 연결합니다. 터미널 생성 응답의 handle과 worktree 생성 응답의 실제 selector를 사용합니다. timeout·연결 실패 시 기존 handle을 기록하고 상태를 먼저 확인합니다. 재시도도 같은 Task와 배치에 승인 생략 CLI 터미널을 연결하고, 복구 가이드의 liveness·next·release 조건을 따릅니다. worker-start 실행 후에는 응답을 끝내 알림을 기다리고, wake에 포함된 check와 반환된 next를 따릅니다.</p></details>
<details class="extra"><summary>용어를 일상적인 말로 이해하기</summary>{table(['용어','쉽게 말하면','주의할 차이'],terms)}</details></section>
<section class="panel" id="sources"><div class="section-label">확인 범위와 근거</div><h2>이 안내서가 확인한 것</h2><p>설치된 Orca 1.4.246의 프로젝트 추가·에이전트 설정 화면 문구와 orca-cli·orchestration 가이드, coordinator-loop·placement·recovery 참고, agent launch·worker-start·task-create·run-use와 terminal create/wait·worktree create 도움말과 Codex CLI 0.166.0의 resume/fork 도움말을 읽어 작성했습니다. 화면 메뉴명은 설치 리소스에서 확인했으며 GUI 클릭·저장 동작 자체는 시험하지 않았습니다. 실제 사용자의 프로젝트에 작업자를 실행하거나 GitHub 저장소를 만들고 병합한 결과는 아닙니다.</p><ul><li><a href="https://learn.chatgpt.com/docs/developer-commands">OpenAI · Codex 명령과 세션</a></li><li><a href="https://cli.github.com/manual/gh_repo_create">GitHub CLI · 저장소 생성</a> · <a href="https://cli.github.com/manual/gh_auth_login">브라우저 인증</a></li><li><a href="https://cli.github.com/manual/gh_pr_create">GitHub CLI · PR 생성</a> · <a href="https://cli.github.com/manual/gh_pr_checks">PR 자동 검사 확인</a></li><li><a href="https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue">GitHub · PR과 이슈 연결·자동 종료 조건</a></li></ul><p>Orca는 설치 버전의 스킬 가이드를 기준으로 합니다. 업데이트 후 명령이 달라졌다면 AI에게 현재 가이드를 다시 읽게 하세요. 이 안내서의 “같은 기획 → 새 개발”과 파일 이름은 이해를 돕는 권장 운영 방식이며 제품의 강제 규칙이 아닙니다.</p><p class="small">기존 Herdr 안내서는 별도로 보존되어 있습니다. 이 판은 Orca 오케스트레이션 기준입니다.</p></section>
</main><footer>Gon AI Development OS · Orca + Codex CLI · 1.0.0 · 2026-11-02</footer><div id="toast" role="status" aria-live="polite"></div><script src="viewer.js"></script></body></html>'''
(ROOT/'index.html').write_text(html_doc)
# 마크다운 원본을 손실 없이 읽는 별도 예시 뷰어.
example_sections=[]
for name in ['README.md','docs/research/01-problem.md','docs/research/02-research-plan.md','docs/research/03-evidence.md','docs/research/04-decision.md','docs/PROJECT-BRIEF.md','docs/TASKS.md','docs/STATE.md']:
    p=ROOT/'example-project'/name
    example_sections.append(f'<section class="panel"><h2>{e(name)}</h2><a href="example-project/{e(name)}">원본 파일 열기</a><pre>{e(p.read_text())}</pre></section>')
(ROOT/'examples.html').write_text('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Orca 안내서 · 기획 문서 전체 예시</title><link rel="stylesheet" href="style.css"></head><body><main><a href="index.html#examples">← 실행 안내서로</a><h1>문답에서 최종 문서까지</h1><p>전부 설명용 가상 예시입니다. 실제 조사·승인·구현 결과가 아닙니다.</p>'+''.join(example_sections)+'</main></body></html>')
print(f'HTML 생성: {len(steps)}단계, 예시 8개')
