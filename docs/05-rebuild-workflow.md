# GitHub 원본으로 워크플로우 문서 다시 만들기

이 저장소에는 관리 매뉴얼, Herdr 안내서의 편집 원본과 생성기, 프로젝트 실행 양식, 시험문제지 OCR 예시가 함께 들어 있습니다. 저장소를 새로 받아 설치·빌드·검증하면 HTML·PDF·오프라인 묶음을 다시 만들 수 있습니다. 이 빌드는 문서를 생성하며 실제 프로젝트를 구현하거나 앱의 작업자를 실행하지 않습니다.

## 무엇을 사용할지 선택

| 목적 | 시작 파일 | 편집 기준 |
| --- | --- | --- |
| 전체 절차·GitHub 기록 | [관리 매뉴얼](01-manual.md) | `manual/sections.json`, 공통 `manual/planning-steps.json` |
| Herdr에서 직접 따라 하기 | [Herdr 안내](../guides/herdr/README.md) | 해당 폴더의 development/project JSON, template, handbook, style, viewer |
| 아이디어를 넣고 모델에게 실행 맡기기 | [Herdr 실행 양식](../templates/herdr-project/README.md) | HERDR-PROJECT.md, HERDR-OPERATIONS.md |
| 채워진 프로젝트 문서 참고 | [시험지 OCR 예시](../examples/exam-ocr/README.md) | 기획·설계·계획·검증·실행 지시와 과거 시험 결과 |

현재 실행 안내는 Herdr + Codex CLI를 기준으로 합니다. 모델의 내부 하위 에이전트와 Herdr 분할 터미널을 같은 기능으로 가정하지 않습니다. 각 안내가 기록한 도구 버전·확인 날짜와 실제 환경을 대조합니다.

## 새 체크아웃에서 재생성

Node.js 22+, Python 3.11+, npm, 한국어 글꼴, PDF 텍스트 검사 도구 `pdftotext`가 필요합니다. Ubuntu에서는 Noto CJK 글꼴과 poppler-utils로 준비할 수 있습니다. 시스템 설치는 해당 환경의 권한 절차를 따릅니다.

```sh
git clone https://github.com/krdn/gon-development-os.git
cd gon-development-os
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
npm ci
npx playwright install chromium
npm run build:all
npm test
npm run verify:all
```

비공개 저장소 접근에는 본인의 GitHub 인증이 필요합니다. Linux 브라우저 시스템 의존성은 환경 관리 절차로 설치합니다. 기존 Chrome/Chromium을 사용하려면 `CHROMIUM_PATH`에 그 실행 파일의 절대경로를 지정합니다. 파일 내용을 새로 바꿨다면 의도한 새 파일을 먼저 Git에 추적한 뒤 빌드합니다. 전체 ZIP의 포함 대상은 Git 추적 파일입니다.

`build:all`은 공통 P1~P5 원본을 Herdr 안내에 동기화하고 Herdr 안내서의 HTML·브라우저 회귀·PDF 내용 검사를 수행합니다. 이어 Herdr 안내서 ZIP과 관리 매뉴얼·저장소 전체 ZIP을 만듭니다. 루트의 npm 의존성이 안내서 생성기에도 사용되며, 안내서 폴더만 따로 사용할 때는 그 폴더의 npm ci를 수행합니다.

출력은 `dist/`의 관리 매뉴얼·전체 ZIP, `guides/herdr/`의 HTML·두 PDF, `guides/gon-beginner-workflow.zip`입니다. CI artifact에도 전체 ZIP과 Herdr 안내서 ZIP이 포함됩니다. 보존 기한이 끝나면 같은 커밋에서 다시 빌드합니다.

기존 흐름도는 편집 JSON·검증된 HTML·해시 연결 기록을 함께 보존하며 위 빌드는 그 일치만 확인합니다. **흐름도 내용을 수정할 때**는 [Archify 재생성 절차](03-maintenance.md)를 따릅니다. Archify 자체는 별도 도구이며 이 저장소에 포함되지 않습니다.

## AI에게 문서 갱신을 맡기는 요청문

```text
이 GitHub 저장소를 현재 체크아웃 기준으로 읽고 작업 워크플로우 문서를 갱신해.
먼저 AGENTS.md, README.md, docs/03-maintenance.md, docs/05-rebuild-workflow.md를 읽어.
목표: [만들거나 개선할 프로젝트 워크플로우]
실행 환경: Herdr + Codex CLI
사용자와 입력: [프로젝트 아이디어 또는 기존 요구 문서]
최종 전달 범위: [문서만 / 로컬 구현·검증 / 허용한 원격 전달·배포]

편집 원본을 수정하고 생성 HTML/PDF만 고치지 마.
P1 문제 정의 → P2 조사 설계 → P3 근거 → P4 결정 → P5 개발 인계 →
구현 → 실제 사용자 흐름 검증 → 필요한 리뷰 → 허용된 전달 → 상태 저장을 연결해.
사용자 결정, AI 제안, 실제 실험, 미확인을 구분하고 승인·완료를 만들어내지 마.
모델·effort는 사용자 지정과 현재 운영 정책을 보존하고 실제 지원 여부를 확인해.
협업은 파일 소유권·결과 경로·보고 대상·재개 조건을 정하고 실행 결과를 읽어 검증해.
Herdr는 주 모델 내부의 앱/core 접근부터 확인하고 에이전트 생성 시 실행 계약의 CLI별 승인 생략 옵션을 사용해.
기존 미커밋 변경과 사용자 세션을 보존하고 관련 새 파일만 Git 추적에 추가해.
npm run build:all, npm test, npm run verify:all을 실행해.
원격 전달도 요청한 경우에만 GitHub 반영·원격 SHA·CI·artifact를 확인해.
문서 저장, 재생성, 실제 앱 동작을 구분해 보고해.
```

프로젝트 실행 문서를 새로 채우려면 `templates/herdr-project`를 별도 프로젝트 폴더에 복사합니다. `examples/exam-ocr`는 참고할 완성된 문서 예시이며, 제품 구현 완료본이나 현재 PC의 실행 상태가 아닙니다. 앱/모델 버전·정책·terminal ID·권한은 새 실행 때 확인합니다.

## 검증 기록 읽기

현재 전체 빌드 판정은 `evidence/workflow-bundle.json`의 상태와 파일 해시를 기준으로 합니다. `RUNNING`·`FAIL`이면 하위 안내서에 남은 과거 PASS를 현재 성공으로 쓰지 않습니다. 최종 매뉴얼·묶음 검사까지 끝나야 PASS를 공개합니다. 기록 파일은 임시 파일에서 원자적으로 교체합니다. 중단 상태에서는 원인을 확인하고 다시 빌드합니다.

- `evidence/build.json`: 관리 매뉴얼의 원본·PDF·HTML·목차·링크와 해시.
- `evidence/workflow-bundle.json`: 현재 Herdr 안내서 재생성 명령·파일 해시·문서 링크 검사.
- `guides/*/browser-tests.json`, `pdf-validation.json`: 안내서 자체의 회귀·PDF 검사.
- `evidence/imported-guides/`: 가져오기 전 과거 검증 기록. 현재 실행 증거로 해석하지 않습니다.
- `examples/exam-ocr/RUN-RESULT.md`: 과거 Herdr 인수 시험의 성공·차단 범위. 현재 실행 성공 보장이 아닙니다.

검사 PASS는 기록된 범위에만 적용됩니다. 완벽한 자동 실행을 문서만으로 보장하지 않으며, 도구 접근·사용자 답변·실제 제품 수용 검사를 별도로 확인합니다.
