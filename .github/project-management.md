# GitHub 기준 기록과 적용 현황

## 2.1.0 전문가 기획 협업

[전문가 설계·리뷰·평가 도입 #24](https://github.com/krdn/gon-development-os/issues/24)를 Project #18과 연결한다. 2026-11-09 현재 대화에서 사용자가 도입 판단을 위임하고 main 병합·push를 요청했다. 이는 에이전트가 옮긴 범위 기록이며 GitHub 사용자 직접 승인 리뷰가 아니다. 구성은 기존 협업자 상한 2명과 역할별 파일 소유권을 유지한다. 소스·문서 생성·실제 Herdr 시험·완료 경계 리뷰·PR CI·main 통합을 나누어 기록하고 해당 이슈·PR/Actions에서 원격 상태를 재조회한다. 기존 아래 단계 기록은 당시 작업의 근거로 보존한다.

## 1.6.0 기준 기록

확인일: 2026-11-08. 기준 작업 [#9](https://github.com/krdn/gon-development-os/issues/9), 설계/협의 [#10](https://github.com/krdn/gon-development-os/discussions/10), [Project #18](https://github.com/users/krdn/projects/18), [1.6.0 Milestone](https://github.com/krdn/gon-development-os/milestone/1).

OS는 공통 운영 표준, `krdn/gon-skills`는 스킬 원본입니다. 개별 제품의 설계·작업·협의는 해당 저장소에 남깁니다. OCR 원본과 사용자 자료를 이번 작업으로 원격 이전하지 않습니다.

## 현재 단계와 사용자 검토

- [S1 결과·S2 구성 v1 승인](https://github.com/krdn/gon-development-os/issues/9#issuecomment-6714630379): 2026-11-08 08:43:21 KST, 사용자 답변 “설계와 S2 구성 승인”. Codex가 옮긴 대리 기록입니다.
- [S2 구현 #11](https://github.com/krdn/gon-development-os/issues/11): Codex 조정자 + Astra/high 작업자 1명. 결과·검사 근거를 GitHub에 저장했습니다.
- [위임 기록](https://github.com/krdn/gon-development-os/issues/9#issuecomment-6714860018): 09:07:58 KST 사용자 답변 “너가 판단해서 진행해”. 이번 잔여 작업의 판단을 위임했으며 직접 결과 수용으로 기록하지 않습니다.
- [S3 검증·리뷰 #12](https://github.com/krdn/gon-development-os/issues/12): Codex + Opus 5.5/high 외부 리뷰 1회와 지적 수정. [S4 #13](https://github.com/krdn/gon-development-os/issues/13)은 Codex가 최종 CI·통합·설치·원격 상태를 확인합니다.
- #11/#12/#13은 #9의 native sub-issue이며 선행 관계도 API 생성 후 재조회했습니다. [로컬 검사 표현](../evidence/stage-review.json)은 위임 전 S2 snapshot입니다. 최신 위임 판정을 사용자 수용으로 바꾸어 JSON에 삽입하지 않습니다.

Project의 `단계`, `구성 검토`, `결과 검토`를 별도 관리합니다. 결과 검토대기는 `In Progress`를 유지합니다. `위임 진행`·`위임 수용`은 이번 명시적 판단 위임용이며 직접 사용자 승인을 뜻하지 않습니다. `Done`은 해당 AC와 실제 사용자 수용 또는 그 작업에 한정된 명시적 위임에 따른 조정자 판정을 확인한 뒤 사용합니다. 후자는 직접 사용자 수용과 구분합니다. 구성/결과 revision과 답변 원문·출처는 이슈와 검사 기록에 보존합니다. PR merge 자동 종료만으로 사용자 검토를 대체하지 않습니다.

## 기능별 상태

`used`: 실제 사용·재조회, `pending`: 준비 또는 미검증, `unavailable`: 현재 접근/플랜 차단, `not_applicable`: 이번 범위에 해당 없음. 설정 상태와 실제 거부·탐지·사용자 기능 검증은 구분합니다.

| 영역 | 상태와 근거 | 남은 범위·대체 기록 |
| --- | --- | --- |
| Code·README·ADR·계약 | used: 기존 main과 검토용 브랜치, [결정 기록](../docs/adr/0001-github-stage-review.md) | 최종 main/설치 SHA와 재조회는 #13 |
| Issues·Forms | used: #9/#11/#12/#13. Forms 원본·YAML/필드 ID 검증 완료 | 로그인한 새 이슈 화면은 후속 #16 |
| Sub-issues·dependencies | used: #9 → #11/#12/#13, #13은 #12, #12는 #11에 차단됨 | 사용자 수용 전 상위/단계 이슈를 닫지 않음 |
| Milestones·Labels·Assignees | used: 1.6.0 Milestone·기존 documentation/enhancement 라벨 | 실제 담당은 계약의 역할. 사람에게 임의 배정하지 않음 |
| Projects | used: 비공개 Project #18·항목·구성/결과 검토 필드 재조회 | 보드·로드맵 view 생성/API 재조회 완료. 로드맵 날짜/화면·charts 설정은 pending. 활성 workflow 6개를 조회했지만 설정 변경은 미실행. Done 전환으로 #11 자동 종료를 관찰. 나머지 자동 조건/화면은 [후속 #16](https://github.com/krdn/gon-development-os/issues/16). 자동 상태 변경은 구성/결과 필드의 승인 근거를 대신하지 않음 |
| Discussions | used: #10 설계 및 [실제 협의](https://github.com/krdn/gon-development-os/discussions/10#discussioncomment-19465829) | General 토론 양식 원본 포함, 로그인 화면은 후속 #16 |
| Wiki | pending: `has_wiki=true`이나 `.wiki.git` 조회는 Repository not found | 초기 페이지 생성·내용 동기화 미실행. 브라우저 연결 불가. docs/README가 기준 |
| Branch·PR·CODEOWNERS | used: skills PR5·OS PR15와 PR/CODEOWNERS 양식 원본 | 같은 계정의 담당 표시를 인간 승인 증명으로 쓰지 않음 |
| Actions·checks·artifacts | used: 기존 Validate and build와 SHA별 기록. 새 CLI 테스트는 기존 discover 경로로 실행 | 최종 main 적용·설치는 #13에서 확인. artifact 보존 30일, 장기 근거는 repo 요약·해시 |
| Rulesets·접근 | used: [main 규칙](https://github.com/krdn/gon-development-os/rules/26778583) active 재조회 | PR + 최신 base의 GitHub Actions `validate`, 대화 해결, force push/삭제 방지. bypass 없음. 사람 리뷰수 0은 동일 계정 한계; 사용자 수용은 별도 절차. 실제 거부 실험 미실행 |
| Security·Dependabot | used: secret scanning·push protection·비공개 제보·취약점 알림·자동 보안 수정 설정 후 재조회 | S2 당시 pypdf 경보 98건(두 매니페스트 합계), 자동 PR #14는 산출물 미갱신으로 CI 실패. 이번 PR #15에서 두 파일을 6.21.4로 맞추고 전체 재생성·검사하며, 병합 후 실제 경보 상태를 #13에 기록. 비밀값 탐지·신고 실험은 미실행. SECURITY.md·npm/Actions 정기 갱신 원본 포함, pip는 두 경로 보안 갱신만 유지(정기 버전 PR은 재생성 자동화 전 중지). 코드 스캔은 pending(미구성) |
| Tags·Releases·assets | pending: S4 전달 범위에서 초안과 실제 태그/asset을 검토 | 아직 릴리스 발행 없음. 현재 산출물은 저장소·Actions |
| Environments·Deployments | not_applicable: 이번 S2는 제품 배포 없음 | 실제 배포가 있는 제품에서 기존 파이프라인 기록 사용 |
| Pages·Packages | not_applicable: 이번 단계에 사이트·패키지 발행 없음 | HTML/PDF는 저장소/Actions로 전달. 공개 사이트는 별도 전달 범위 확정 |
| Insights·API·검색 | used: API로 단계·차단·검토대기·원격 상태 재조회 | 임의 진척률 없음. Project charts·로드맵 날짜/화면은 pending |
| 조직 전용·유료·외부 연동 | not_applicable: 개인 저장소 운영, 새 유료 기능·계정·webhook 없음 | 필요 시 비용·권한·대안과 구성 검토를 먼저 제시 |

## 공개 상태와 한계

S1 조회에서는 OS가 private이고 Rulesets가 403이었습니다. S2 재조회에서 public·Wiki 활성화를 관찰했습니다. 최초 사용자 요청에 “필요하다면 레포지토리를 public으로 해도 좋아”라는 공개 허용이 있습니다. 이 실행에서는 visibility를 변경하지 않았고 변경 주체를 확인하지 못했습니다. 공개 상태에서 Rulesets 조회·설정을 진행했습니다. `gon-skills`와 Project #18은 private입니다. 공개 문서의 private 링크는 접근 권한이 있는 사용자만 열 수 있습니다.

기존 `archive/2026-10-31/`과 이력에는 과거 대화·이미지가 있으며 공개 적합성 전수검토는 미실행입니다. 이 관찰을 공개 안전성 승인으로 해석하지 않습니다. 현재 공개를 위해 새 자료를 추가로 복제하거나 기존 이력을 정리하지 않았습니다.

사용자 승인 기록과 계정 권한은 구분합니다. 현재 사람과 AI가 같은 계정을 쓰므로 GitHub 계정·CI·JSON의 `actor: user`만으로 인간의 의사를 증명할 수 없습니다. 실제 답변 출처와 승인 범위를 조정자가 확인하는 절차상 통제입니다.

근거: [Issues API](https://docs.github.com/en/rest/issues/sub-issues), [Dependencies](https://docs.github.com/en/rest/issues/issue-dependencies), [Rulesets API](https://docs.github.com/en/rest/repos/rules), [Issue Forms](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms). 실제 호출과 한계는 단계 이슈에 연결합니다.
