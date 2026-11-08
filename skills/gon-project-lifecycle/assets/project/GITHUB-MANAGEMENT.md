# {{PROJECT_NAME}} GitHub 관리 기준

- GitHub host·소유자/저장소·기본 branch: 미정
- 기준 Project URL·owner·번호/ID·필드/상태 매핑: 미정
- 현재 작업의 Issue/PR·계약 경로: 미정
- 이슈 종료 기준(구현/merge/배포 중 실제 조건): 미정
- 기록 담당·허용된 원격 작업·다른 추적기 예외: 미정
- 단계 구성·결과 검토 Issue / 실제 협의 Discussion / 검토 JSON 경로: 해당 시 지정
- 사용자 답변 출처·시각·정확범위 / 단계·계약 revision·구성 버전·결과 revision: 검토 전
- 원격 재조회 시점·revision·동기화 상태: pending_sync — 연결 확인 전

## 기능별 적용

상태는 used / not_applicable / unavailable / pending으로 기록한다. 미사용/불가에는 이유와 대체 GitHub 기록을 연결한다.

| 기능 | 상태 | 기준 URL·ID / 사유·대체 기록 |
| --- | --- | --- |
| 저장소 문서·ADR·계약 | pending | 미정 |
| Issues·Forms·sub-issues·dependencies | pending | 미정 |
| Projects·views·필드·iteration·workflow | pending | 미정 |
| Milestones | pending | 미정 |
| Labels·담당자·Issue Types | pending | 미정 |
| Discussions | pending | 미정 |
| Wiki | pending | 미정 |
| Branch·PR·리뷰·CODEOWNERS | pending | 미정 |
| Actions·checks·logs·artifacts | pending | 미정 |
| Tags·Releases·assets | pending | 미정 |
| Environments·Deployments | pending | 미정 |
| Security·Dependabot·scanning·advisories | pending | 미정 |
| Packages·Pages | pending | 미정 |
| Rulesets·보호·접근/연동 설정 | pending | 미정 |
| Insights·Project charts | pending | 미정 |

## 기록과 완료

목적·설계·ADR·계약은 저장소 파일, 실행 작업·상태는 Issues/Projects, 변경·검증은 PR/CI, 전달은 Release/배포에 연결한다. PLAN/STATE와 로컬 목록은 기준 URL을 가진 요약이다.

생성/갱신 전 기존 항목·전체 목록과 직전 상태를 읽어 중복·다른 사람의 편집을 보존한다. timeout은 재생성 전에 원격 존재를 확인한다. 해당 단계의 URL·본문·상태·SHA를 원격에서 다시 조회한 뒤 저장 완료로 기록한다. 실패는 pending_sync로 남긴다.

원격 기록 정책은 공개 전환·멘션/외부 메시지·권한/보호 변경·유료 실행·릴리스 발행·배포 권한을 추가하지 않는다. 민감 자료는 비공개 보안 경로를 사용한다.

정의된 단계는 구성 승인 → 실행·협의 → 사용자 결과 검토 → 추가 요청 반영·재검증 → 수용 후 다음 단계 순서로 관리한다. AI 합의·CI·침묵은 사용자 승인/수용이 아니며, 동일 계정 에이전트의 답변 전사는 사용자 본인의 GitHub 승인 리뷰와 구분한다. JSON 검사는 로컬 구조·대상 일치만 확인하며 인간 진위·원격 저장·실제 모델 준수를 입증하지 않는다.
