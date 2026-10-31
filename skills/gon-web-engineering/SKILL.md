---
name: gon-web-engineering
description: Configure Gon’s defaults for new web projects and apply scoped guidance when implementing, debugging, reviewing, or upgrading React/TypeScript frontends and Rust/Axum/SQLx backends. Use for 신규 웹 프로젝트 구성, React 화면 수정, Rust API·DB 작업, or requests to apply Gon’s project guidance to AGENTS.md and CLAUDE.md. Preserve existing project choices. Exclude unrelated native apps, ordinary prose edits, and automatic rewrites of other stacks.
---

# Gon 웹 개발

## 먼저 적용 범위를 결정한다

- 사용자 요구, 현재 작업 경로, 프로젝트 지침, 매니페스트·잠금 파일·CI를 확인한다.
- 기존 프로젝트의 기술·API·데이터·운영 제약을 따른다. 이 스킬의 기본안에 맞추기 위한 재작성을 시작하지 않는다.
- 기술이 미정인 신규 웹 프로젝트는 React/TypeScript + Rust(Axum/Tokio) + PostgreSQL(SQLx)를 기본안으로 사용한다. 공개 콘텐츠의 SSR, Microsoft 연계 등 실제 요구에 맞춰 조정한다.
- 분석·비교·설명 요청에는 분석으로 답한다. 신규 프로젝트 생성·구성 요청 또는 지침 적용 요청에서만 지침 파일을 생성·수정한다.
- 기존 기능의 버그 수정만 요청받았다면 관련 코드와 필요한 검증을 수행한다. 지침 파일을 새로 배치하는 작업을 추가하지 않는다.
- 가역적인 통상 구현 선택은 진행한다. 사용자 확인은 요구사항의 중요한 불확실성이나 실제 권한 제한이 있을 때만 한다.

## 관련 문서만 읽는다

아래 경로는 이 `SKILL.md`가 있는 폴더 기준이다. 파일 읽기 도구로 실제 내용을 확인한다. 프로젝트에 해당 주제의 구체적인 지침이 있으면 그것을 우선 적용한다. 공통 참고 문서가 필요할 때만 아래에서 추가로 선택한다.

| 작업 | 읽을 문서 |
| --- | --- |
| 신규 웹 프로젝트·기술 선택·공통 아키텍처 | [references/architecture.md](references/architecture.md) |
| 프로젝트 생성·개발 지침 설치·구조 구성 | [references/project-setup.md](references/project-setup.md) |
| React·TypeScript·UI·라우팅·브라우저 SDK | [references/frontend.md](references/frontend.md) |
| Rust 서버·인증·API·DB·SQL·마이그레이션 | [references/backend-data.md](references/backend-data.md) |
| 코드 변경·버그 분석·테스트·업그레이드 | [references/verification.md](references/verification.md) |

- 여러 영역을 변경하면 해당 문서를 함께 읽는다. 호출됐다는 이유로 모든 문서를 읽지 않는다.
- 버그 분석·수정에는 검증 지침과 실제로 관련된 기술 지침을 선택한다.
- TypeScript 화면만 바꾸면 Rust 지침을 추가로 읽지 않는다. API 계약을 바꾸면 서버·API 지침도 읽는다.
- 다른 스택에서 명시적으로 이 스킬을 호출하면 해당 스택을 유지하고 적용 가능한 일반 원칙만 사용한다.
- 필요한 내용이 현재 문맥에 있고 파일이 바뀌지 않았다면 재사용한다. 누락된 문서는 추측하지 않는다.

## 신규 프로젝트 또는 지침 적용을 수행한다

1. `references/project-setup.md`에 따라 프로젝트 루트, 기존 문서와 필요한 주제를 확인한다. 기존 문서 경로가 있으면 직접 병합하고, 새 문서를 배치할 때만 `scripts/configure_project.py`에 `--topics`를 명시한다. 기본은 계획 출력이며 `--apply`는 없는 파일만 생성한다.
2. 생성 결과의 `review_required`를 처리하고 실제 결정·명령·제약을 프로젝트 문서에 기록한다. 파일 생성 성공을 지침 병합 완료로 간주하지 않는다.
3. 애플리케이션 구현까지 요청받았다면 구현·연결·검증까지 계속한다. 검증은 `references/verification.md`와 프로젝트의 실제 명령을 따른다.

## 지침을 유지한다

- 전역 파일에 이 스킬의 본문이나 모든 참조 문서를 자동 가져오도록 추가하지 않는다. 필요하면 전역 파일에는 이 스킬을 선택할 작업 조건만 짧게 남긴다.
- 프로젝트에 채택된 정책과 결정은 그 프로젝트에서 관리한다. 이 스킬이 업데이트됐다는 이유로 기존 프로젝트의 정책·의존성을 자동 교체하지 않는다.
- 스킬 선택은 모델의 판단이며 항상 실행되는 훅이 아니다. 품질을 강제해야 하는 검사는 해당 프로젝트의 실제 검사 도구와 CI에 둔다.
- 설치·배포·클라우드 실행의 완료 범위는 실제 확인한 환경에 한정해 보고한다.
