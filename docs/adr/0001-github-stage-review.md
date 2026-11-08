# 0001 — GitHub 기록과 단계별 사용자 검토

상태: 2026-11-08 사용자 S1 설계 수용. 09:07:58 KST 사용자 판단 위임으로 이번 S3/S4를 진행. 직접 사용자 결과 수용과 구분하며 향후 단계별 검토 규칙은 유지.

기존 운영은 기술 검사·AI 판단으로 다음 단계에 진행할 수 있었습니다. 사용자는 각 단계 결과를 검토해 추가 요청을 반영하고, 에이전트 구성도 실행 전에 검토받기를 요청했습니다.

결정: 실제 단계마다 구성 승인과 결과 수용을 분리합니다. 구성은 단계 계약 revision·역할·모델/effort·소유 파일·동시 인원·권한/비용에, 결과는 산출물 revision·검사·미검증에 연결합니다. 변경된 대상에 이전 승인을 재사용하지 않습니다. 작은 편집을 새 단계로 만들거나 승인된 일상 작업을 매번 재승인하지 않습니다.

협의는 Discussion, 실행·추가 요청은 Issues/Projects, 확정 결정·계약은 Code/ADR, 검사는 PR/Actions, 승인된 전달은 Releases/Deployments에 연결합니다. 기능별 미적용·불가·미검증과 대체 기록도 남깁니다.

버전 문자열만 비교하면 버전을 바꾸지 않은 구성/결과 변경을 놓칠 수 있어 내용 digest도 사용합니다. 로컬 검사기는 승인 기록을 생성하지 않으며 사람의 진위·원격 저장·실제 실행 강제를 증명하지 않습니다. 같은 계정으로 사람과 에이전트가 동작하는 한계는 절차상 통제로 공개합니다.

근거: [사용자 설계·구성 승인](https://github.com/krdn/gon-development-os/issues/9#issuecomment-6714630379), [설계](https://github.com/krdn/gon-development-os/discussions/10), [실제 S2 협의](https://github.com/krdn/gon-development-os/discussions/10#discussioncomment-19465829), [기능별 적용 현황](../../.github/project-management.md).
