# Gon Development OS

앱·웹서비스·스킬·에이전트 프로젝트를 목표 설정부터 구현·검증·전달까지 진행하는 개인 개발 표준입니다. 매뉴얼, 실제 스킬, 편집 원본, 생성 도구와 과거 검증 기록을 함께 관리합니다.

현재 버전: [VERSION](VERSION) · 최초 통합: **2026-10-31** · 비공개 저장소

## GitHub 원본에서 다시 만들기

[전체 재생성 안내와 AI 요청문](docs/05-rebuild-workflow.md)을 기준으로 `npm run build:all` → `npm test` → `npm run verify:all`을 수행합니다. 의존성·글꼴·브라우저 준비 방법도 같은 문서에 있습니다.

- [Herdr CLI에서 프로젝트 처음 시작하기](docs/06-herdr-cli-start.md) · 첫 요청 뒤 단계별 전문 스킬 적용과 새 세션 인계
- [Herdr 단계별 안내](guides/herdr/README.md) · [Orca 단계별 안내](guides/orca/README.md)
- [아이디어 입력용 실행 양식](templates/herdr-project/README.md) · [시험지 OCR 프로젝트 예시](examples/exam-ocr/README.md)

안내서·실행 양식·예시의 편집 원본이 모두 이 저장소에 있습니다. 과거 앱 시험의 차단·미검증은 예시의 RUN-RESULT에 남기며 문서 빌드 성공을 실제 협업·제품 성공으로 간주하지 않습니다.

## 처음 읽을 순서

1. [실행 매뉴얼](docs/01-manual.md): Herdr + Codex CLI의 기획·리서치 5단계 + 개발 10단계, 문답·조사·의사결정·인계 및 신규·기존·재개·AEOS 경로
2. [스킬 설치와 사용](docs/02-skills.md): 두 스킬의 역할, 설치, 기존 설치본 보호, 실제 인식 확인
3. [수정·검증·업데이트](docs/03-maintenance.md): 무엇을 고칠지, 재생성, CI, 버전·이력 관리
4. [자료 출처와 검증 범위](docs/04-provenance.md): 원본·보관본·현재 검증의 구분

## 바로 사용할 파일

- [PDF 매뉴얼](dist/01-project-workflow-manual.pdf)
- [HTML 매뉴얼](dist/01-project-workflow-manual.html)
- [상호작용형 전체 흐름도](dist/02-workflow-map.html)
- [저장소 전체 내려받기](https://github.com/krdn/gon-development-os/archive/refs/heads/main.zip)
- [자동 검증과 빌드 묶음](https://github.com/krdn/gon-development-os/actions/workflows/validate.yml)
- [현재 빌드 검증 기록](evidence/build.json)
- [변경 이력](CHANGELOG.md)

GitHub는 HTML의 상호작용 기능을 직접 실행하지 않습니다. 저장소를 내려받아 `dist/01-project-workflow-manual.html`을 브라우저로 열거나 PDF를 사용하세요. 상대 링크를 유지하려면 HTML 한 파일보다 저장소 또는 오프라인 묶음 전체를 받으세요.

새 빌드 ZIP은 Git 이력에 중복 저장하지 않고 Actions 실행의 artifact로 제공합니다. 날짜별 최초 보관본의 기존 ZIP은 그대로 유지합니다.

## 관리 구조

| 경로 | 역할 | 수정 여부 |
| --- | --- | --- |
| `manual/sections.json` | 일반 단계별 매뉴얼 내용과 요청문 | 내용 변경의 원본 |
| `manual/planning-steps.json` | 기획 단계의 공통 내용·요청문과 매뉴얼 표시 차이 | 기획 변경의 원본 |
| `manual/style.css`, `manual/viewer.js` | 화면·인쇄 스타일과 복사·탐색 동작 | 화면 변경 시 |
| `skills/gon-project-lifecycle/` | GitHub 기준 시작·도입·재개·검증·전달과 원격 기록 확인 | 원본 커밋을 갱신할 때 |
| `skills/gon-web-engineering/` | 웹 기술·구현·검증 스킬 | 원본 커밋을 갱신할 때 |
| `diagrams/workflow.json` | Archify 흐름도 편집 원본 | 흐름 변경 시 |
| `scripts/` | 매뉴얼과 전체 안내서 생성·PDF·검증 도구 | 생성 방식 변경 시 |
| `guides/herdr/`, `guides/orca/` | 별도 실행 안내서 원본·생성기·HTML/PDF·검사 | 해당 환경 안내 변경 시 |
| `templates/herdr-project/` | 프로젝트 아이디어 입력·협업·재개 실행 양식 | 실행 계약 변경 시 |
| `examples/exam-ocr/` | 채워진 OCR 프로젝트 문서와 과거 시험 결과 요약 | 예시 범위·근거 변경 시 |
| `docs/01-manual.md`, `dist/01-*.html`, `dist/01-*.pdf` | 매뉴얼 자동 생성 결과 | 직접 편집하지 않음 |
| `dist/02-workflow-map.html` | 별도 Archify 생성 결과 | 흐름도 변경 후 재생성 |
| `archive/2026-10-31/` | 최초 대화·파일·이미지·검증 기록 | 당시 기록으로 보존 |
| `evidence/` | 가져온 파일 해시와 이번 검증 | 새 검증과 구분해 기록 |

실행 스킬은 [gon-skills](https://github.com/krdn/gon-skills)에서 수정하고 설치합니다. 이 매뉴얼은 [skills.lock](skills.lock)에 기록된 커밋의 두 전문 스킬을 오프라인에서도 읽을 수 있게 포함합니다. [설치와 업데이트](docs/02-skills.md) · [매뉴얼 사본 갱신](docs/03-maintenance.md)

## 첫 요청 예시

```text
$gon-project-lifecycle
[프로젝트 경로]에서 [목표]를 진행해줘.
현재 상태·기존 지침·미커밋 변경을 먼저 확인하고,
이번 범위와 실제 완료 기준을 정한 뒤 필요한 단계만 수행해줘.
기준 GitHub 이슈·Project·PR/CI에 실행한 검증·남은 제한·다음 작업을 연결해줘.
원격 내용을 다시 조회하고, 로컬 상태 문서는 URL을 가진 요약으로 유지해줘.
```

이 저장소는 개별 제품을 자동 생성·배포하는 플랫폼이 아닙니다. 실제 작업은 선택한 실행 환경의 도구·권한·사용자 요청 범위 안에서 진행합니다. [기존 `ai-engineering-os`](https://github.com/krdn/ai-engineering-os)는 별도 보일러플레이트이며, 이 저장소의 이름과 구분합니다.
