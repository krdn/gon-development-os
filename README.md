# Gon Development OS

앱·웹서비스·스킬·에이전트 프로젝트를 목표 설정부터 구현·검증·전달까지 진행하는 개인 개발 표준입니다. 매뉴얼, 실제 스킬, 편집 원본, 생성 도구와 과거 검증 기록을 함께 관리합니다.

현재 버전: [VERSION](VERSION) · 최초 통합: **2026-10-31** · 비공개 저장소

## 처음 읽을 순서

1. [실행 매뉴얼](docs/01-manual.md): 10단계, 19개 요청문, 신규·기존·재개·AEOS 경로
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
| `manual/sections.json` | 단계별 매뉴얼 내용과 요청문 | 내용 변경의 원본 |
| `manual/style.css`, `manual/viewer.js` | 화면·인쇄 스타일과 복사·탐색 동작 | 화면 변경 시 |
| `skills/gon-project-lifecycle/` | GitHub 기준 시작·도입·재개·검증·전달과 원격 기록 확인 | 절차 변경 시 |
| `skills/gon-web-engineering/` | 웹 기술·구현·검증 스킬 | 웹 기준 변경 시 |
| `diagrams/workflow.json` | Archify 흐름도 편집 원본 | 흐름 변경 시 |
| `scripts/` | 매뉴얼 생성·PDF·검증 도구 | 생성 방식 변경 시 |
| `docs/01-manual.md`, `dist/01-*.html`, `dist/01-*.pdf` | 매뉴얼 자동 생성 결과 | 직접 편집하지 않음 |
| `dist/02-workflow-map.html` | 별도 Archify 생성 결과 | 흐름도 변경 후 재생성 |
| `archive/2026-10-31/` | 최초 대화·파일·이미지·검증 기록 | 당시 기록으로 보존 |
| `evidence/` | 가져온 파일 해시와 이번 검증 | 새 검증과 구분해 기록 |

스킬의 관리 원본은 이 저장소입니다. `~/.agents/skills/`의 설치본은 배포 사본이며 GitHub 변경이 자동으로 반영되지 않습니다. [업데이트 절차](docs/03-maintenance.md)에 따라 비교·검증한 후 설치본에 적용합니다.

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
