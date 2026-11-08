# GitHub 기준 프로젝트 관리

이 문서의 원격 생성·갱신은 요청 또는 프로젝트에서 허용한 범위에만 적용한다. 그 밖에는 로컬 초안을 `pending_sync`로 남긴다.

## 범위와 기준 저장소

프로젝트 관리·구현을 맡았을 때 적용한다. 설명·감사 요청만으로 원격 글을 만들지 않는다. 신규 표준의 기본은 GitHub이며, 기존에 지정된 다른 추적기가 있으면 강제 이전하지 말고 예외·연결을 명시한다.

1. 실제 remote, host, 소유자/저장소, 기본 branch와 fork/upstream 관계를 확인한다. 관리 대상은 사용자 요청과 저장소 지침으로 정한다. 다른 저장소로 자동 전환하지 않는다.
2. 기존 `.github/project-management.md` 또는 동등 문서에서 기능별 기준 URL·ID·상태 매핑을 읽는다. 없으면 필요한 범위의 문서를 추가하고 빈 항목은 `pending`으로 남긴다.
3. 연결 도구의 기능을 먼저 확인한다. 부족하면 현재 `gh --help`·인증된 API/브라우저를 사용한다. repo 접근이 Projects 권한을 증명하지는 않는다. 403/404를 기능 없음으로 단정하지 않는다.
4. 현재 요청이 허용하는 원격 기록만 생성/갱신한다. 새 저장소의 공개 범위·계정·조직, 알림/멘션, 유료 기능·runner, 외부 연동·webhook·권한/보호 설정은 기존 권한을 확인한다. 기록 정책 자체가 이 권한을 주지 않는다.

오프라인·권한 부족이면 로컬 초안으로 가능한 작업을 계속하고 `pending_sync`, 실패한 기능, 남은 조건을 기록한다. 원격 저장 완료와 구분한다. GitHub 밖의 추적기가 명시된 경우도 GitHub에 남길 요약/연결 범위를 정하고 예외를 보고한다.

## 기능별로 적용·예외를 기록한다

아래 관리 영역을 모두 검토해 `used`, `not_applicable`, `unavailable`, `pending` 중 하나로 매핑한다. 미사용은 이유를, 사용 불가는 이유와 대체 GitHub 기록을 남긴다. 모든 기능을 켜거나 동일 내용을 여러 곳에 복제하는 의미는 아니다. 기능이 추가되거나 조직 전용 기능이 있으면 목록을 확장한다.

| 키 | GitHub 기능과 기준 기록 | 적용 기준/대체 |
| --- | --- | --- |
| `documents` | Code의 README·제품/구조 문서·ADR·AEOS 계약 | 원격 commit/blob 경로를 기준으로 사용 |
| `issues` | Issues·Issue Forms·sub-issues·dependencies | 수용 기준·범위·업무 분해·실패/인수인계. 작은 수정은 기존 이슈/PR에 연결 |
| `projects` | Projects의 표/보드/로드맵·필드·iteration·내장 workflow | 기존 상태/우선순위/기한/규모를 매핑. 불가하면 Issues+Milestones+Labels로 GitHub 안에서 추적 |
| `milestones` | Milestones | 출시/날짜 목표가 있는 작업 묶음. 범위 없는 임의 날짜를 만들지 않음 |
| `labels_assignees` | Labels·담당자·조직 Issue Types | 기존 분류·실제 담당자 재사용. 사람에게 임의 배정/멘션하지 않음 |
| `discussions` | Discussions·답변/제안 | 탐색·질의·아이디어에 적용, 확정 결정은 ADR/이슈와 연결. 비활성 시 문서/이슈 |
| `wiki` | Wiki | 기존 운영/사용자 지식의 기준이 Wiki일 때 갱신. 없으면 저장소 docs를 기준으로 명시 |
| `pull_requests` | Branch·PR·리뷰·CODEOWNERS | 이슈→branch→PR→검토→merge 연결. 단순 변경도 원격 commit/PR 근거 보존 |
| `actions` | Actions·checks·logs·artifacts | 실제 명령/수용 기준과 해당 SHA의 CI. cache는 수용 증거로 사용하지 않음 |
| `releases` | Tags·Releases·release notes·assets | 실제 버전 전달이 요청됐을 때. draft/발행·태그 commit·첨부물 상태를 구분 |
| `deployments` | Environments·Deployments·승인/보호·배포 workflow | 배포 대상·revision·로그·실제 운영 확인. 외부 배포는 이슈/PR에 실행 링크 |
| `security` | Security policy·Dependabot·코드/secret scanning·advisories·supply chain | 위험/플랜/권한에 맞게 확인. 민감 취약점은 비공개 보안 채널 사용 |
| `packages_pages` | Packages·Pages | 패키지/사이트 전달이 있는 경우에만 적용. 발행·공개 전환은 권한 확인 |
| `rules_access` | Rulesets·branch 보호·저장소 기능·접근/연동 설정 | 현재 규칙을 읽고 보존. 설정 변경은 명시된 범위에서만 수행 |
| `insights` | Insights·Project charts·현황 요약 | 운영 의사결정에 필요하면 사용. 실제 데이터 없이 진척/성과 수치를 만들지 않음 |

Projects는 저장소 바깥의 사용자/조직 소유일 수 있다. 원래 owner/Project ID를 기록하고 repo의 `has_projects`만으로 최신 Projects 접근을 판정하지 않는다. views/필드/자동화가 API나 설치 CLI에서 지원되지 않으면 현재 브라우저 도구를 사용하거나 미구성 상태와 대체 기록을 남긴다.

## 사용자 검토와 협의를 연결한다

Gon 방식으로 정의한 각 단계는 [단계 검토 절차](stage-review.md)를 따른다. 구성·사용자 답변·결과 revision·추가 요청은 단계 이슈에, 실제 에이전트 협의의 제안·반론·근거·미해결·조정 결론은 Discussion 또는 기존 이슈에 연결한다. Projects 필드에는 구성 승인/결과 검토·대상 revision을 매핑하고, 원격에서 다시 확인한다. 같은 계정의 에이전트 전사는 사용자 본인의 GitHub 승인 리뷰가 아니다. 단계 결과 수용 전 Done/다음 단계로 자동 전환하도록 구성하지 않는다. 기존 자동화가 Status/이슈 상태를 바꾸면 이를 승인 근거로 쓰지 않고 별도 구성/결과 검토 필드와 실제 답변을 기준으로 진행을 판단한다. 특정 작업의 명시적 판단 위임은 stage-review.md의 별도 위임 기록으로 구분한다.

## 단계별로 실행한다

### 시작·계획

- 기존 이슈·Project·Milestone·라벨·Discussion을 읽고 해당 작업을 재사용한다. 원격 목록은 페이지네이션을 끝까지 처리하며 일부 결과만 보고 신규 생성하지 않는다.
- 새 작업에는 목표/수용 기준, 허용·금지 변경, 선행 조건, 필요한 검증, 실제 소유권을 담는다. 관련 이슈 번호와 Project 항목 ID를 고정한다. 독립된 업무는 sub-issue, 선행 차단은 dependency로 연결한다. 지원 불가 시 이슈 본문의 명시적 링크로 대체하고 native 관계가 만들어졌다고 표현하지 않는다.
- Project의 실제 필드/옵션 ID와 현재 상태를 읽어 예정→진행→검토→완료 의미에 매핑한다. 기존 이름·옵션·자동화와 충돌하는 새 상태를 만들지 않는다.
- 제품 목적/구조·ADR은 저장소 문서로 기록한다. 미확정 토론은 Discussion 또는 이슈에 두고 결정 문서에서 출처를 연결한다.

### 구현·검증

- 이슈와 branch/PR을 연결하고 의미 있는 단계 전환 때 상태·다음 행동을 갱신한다. 전체 대화·내부 추론·비밀값·불필요한 개인정보를 전송하지 않는다.
- PR에는 이슈/계약 경로, 수용 기준별 구현·검사, 실제 대상 SHA, CI/화면/API/DB 증거 URL과 미검증을 남긴다. 외부 모델 리뷰는 reviewer·반환 모델·대상 SHA·지적 처리를 기록하며 GitHub 승인 리뷰를 가장하지 않는다.
- 소유자/저장소·resource ID를 확인한 연결 도구 또는 [CLI 절차](github-cli.md)로 생성/갱신한다. 다른 사람이 쓴 본문/댓글은 그대로 보존한다.

### 통합·전달·재개

- 필요한 CI/리뷰를 해당 SHA에서 확인한다. draft PR·미실행 CI·모델의 PASS는 merge/배포 완료가 아니다.
- 이슈/Project Done은 수용 기준을 만족한 시점이다. 배포가 기준이면 merge 자동 종료와 분리하고 실제 배포/운영 확인까지 남긴다. release draft, 태그 생성, 배포 실행은 각각 별도 상태다.
- 배포 기록 생성도 workflow를 유발할 수 있다. 기록을 남기기 위해 임의 Deployment를 만들지 말고 기존 파이프라인의 실행/Deployment를 연결한다.
- 마지막에 이슈·Project·PR·commit·CI·Release/배포 중 해당 단계의 기록을 다시 읽고 예상 body/상태/ID/SHA/첨부물·URL이 맞는지 확인한다. CLI 종료코드·생성 receipt만으로 대체하지 않는다.
- 다음 세션은 이 원격 기록부터 읽고 로컬 요약을 대조한다. 만료될 artifact는 정제된 장기 요약·해시를 repo 문서/허용된 Release asset에 보존한다.

## 중복·동시 편집·실패를 처리한다

- 생성 전 stable task key/이슈 번호·기존 문서 경로·태그·항목 ID로 전체 목록을 확인한다. 제목 검색 결과만으로 중복이 없다고 단정하지 않는다. 처음 생성한 URL/ID는 관리 기록에 남긴다.
- 요청이 timeout된 경우 같은 POST를 바로 재전송하지 않는다. 원격을 재조회해 생성 여부와 동일 항목을 먼저 확인한다. 두 번째 생성자가 발견되면 임의 삭제/병합 없이 기준과 중복을 보고한다.
- 다른 사람의 본문·상태·리뷰/필드를 직전에 읽고 내 관리 영역만 변경한다. 파일은 blob SHA/branch 기준을 맞춘다. API에 조건부 갱신이 없으면 다시 읽고 범위를 줄이며 충돌을 보고한다. 기존 내용 전체를 오래된 사본으로 덮어쓰지 않는다.
- 인증/권한 오류는 토큰·scope를 자동 확대하거나 다른 계정으로 우회하지 않는다. 안전한 사용자 인증 절차가 필요할 때만 해당 지침을 읽고 진행한다. 동일 차단이면 중단 조건과 미동기화 항목을 남긴다.

## 확인 도구와 완료 근거

`scripts/github_control.py inspect --repo OWNER/REPO`는 `gh`의 **GET만** 사용해 기능 접근을 점검한다. 기본은 github.com이고 다른 host는 `--hostname`으로 명시한다. 사용자/조직 소유 Projects는 별도 CLI/API 조회가 필요하다고 보고한다. 기능 읽기 성공은 쓰기 권한·설정 완료·제품 성공 증거가 아니다.

필요하면 `template --repo OWNER/REPO --task-key TASK-001`로 기능별 검증 기록의 JSON 틀을 출력한다. 파일을 실제 정보로 채운 뒤 `validate --file <receipt.json>`으로 구조·누락·기본 원격 주소 범위를 확인한다. 이 검사는 원격 사실을 조회하지 않으며 출력에도 `remote_verified: false`라고 표시한다. 실제 원격 재조회는 별도로 수행하고 이슈/PR 또는 저장소 작업 기록에 근거를 보존한다. 새 기록 파일을 만들기 위한 형식만 맞춘 성공을 보고하지 않는다.

공식 근거: [Projects API](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects), [sub-issues](https://docs.github.com/en/rest/issues/sub-issues), [dependencies](https://docs.github.com/en/rest/issues/issue-dependencies), [Deployments 이벤트](https://docs.github.com/en/rest/deployments/deployments).
