# 수정·검증·업데이트

## 편집 위치 선택

| 바꿀 내용 | 편집할 파일 | 확인할 결과 |
| --- | --- | --- |
| 단계·요청문·완료 기준 | `manual/sections.json` | HTML, GitHub 매뉴얼, PDF |
| 화면·인쇄 배치 | `manual/style.css` | PC·모바일, PDF 페이지 배치 |
| 복사·목차 동작 | `manual/viewer.js` | 브라우저 실제 동작 |
| 프로젝트 실행 절차 | `skills/gon-project-lifecycle/` | 기존 동작 테스트, 관련 문서 |
| 웹 구현 규칙 | `skills/gon-web-engineering/` | 기존 동작 테스트, 관련 문서 |
| 전체 흐름 | `diagrams/workflow.json` | Archify 결과와 실제 화면 |

`archive/2026-10-31/`의 원본 생성기는 당시 경로를 포함한 보관본입니다. 현재 빌드는 `scripts/`만 사용합니다. `evidence/imported-skills.json`은 가져온 순간의 해시이므로 스킬을 수정할 때 새 해시로 덮어쓰지 않습니다.

## 빌드 환경 준비

수정·재생성은 `git clone`한 저장소에서 진행합니다. Node.js 22 이상, npm, Python 3.11 이상과 한국어 글꼴을 준비합니다. Linux에서 PDF 글자가 깨지면 Noto CJK 같은 한국어 글꼴 설치 여부를 확인합니다. 의존성 버전은 lockfile과 `requirements.txt`로 고정합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
npm ci
npx playwright install chromium
```

Linux 브라우저 실행에 필요한 시스템 라이브러리가 없으면 환경 관리 절차에 따라 설치합니다. CI에서는 Playwright의 `--with-deps` 설치를 사용합니다. 기존 Chromium을 사용할 때는 `CHROMIUM_PATH`로 실행 파일을 지정할 수 있습니다.

## 한 번의 업데이트 순서

```bash
git pull --ff-only
git switch -c docs/describe-change
# 원본과 CHANGELOG.md 수정
# 새 파일을 추가했다면 의도한 파일만 git add로 먼저 추적
npm run build
npm test
git diff --check
git status --short
```

1. 변경 이유와 완료 기준을 한 문장으로 정합니다. 다른 작업의 미커밋 변경을 보존합니다.
2. 원본을 수정하고 관련 스킬·매뉴얼·흐름도 설명이 어긋나지 않는지 확인합니다.
3. `npm run build`는 HTML·GitHub 매뉴얼 → PDF → 북마크·해시·오프라인 묶음 순서로 생성합니다. 묶음은 Git이 추적하는 파일과 지정된 생성 결과만 포함합니다. 새 원본 파일은 먼저 의도한 파일만 `git add`하고 빌드합니다. 흐름도 자체는 별도 절차로 갱신합니다.
4. `npm test`는 원본·생성 결과 해시, 현재 매뉴얼의 상대·내부 링크, Markdown 링크, 스킬 참조와 두 스킬의 동작 테스트를 검사합니다. `npm run verify:artifacts`는 빌드하기 전 기존 PDF·문서·빌드 기록이 현재 원본과 맞는지만 검사합니다. 외부 웹페이지의 현재 내용·로그인 상태·운영 배포까지 검증하지는 않습니다.
5. 화면 변경은 브라우저에서 PC·모바일·복사·키보드 동작을 확인합니다. 인쇄 변경은 PDF를 실제로 열어 잘림·빈 페이지·목차를 확인합니다. 자동 빌드는 가로 넘침과 PDF 텍스트·북마크를 검사하지만 시각 검토 전체를 대신하지 않습니다.
6. 새 전달 버전이면 `VERSION`, `package.json`의 버전을 함께 바꾸고 `npm install --package-lock-only`로 lockfile을 맞춥니다. 호환되지 않는 절차 변경은 major, 호환되는 확장은 minor, 수정은 patch를 사용합니다. 버전 변경 후 다시 빌드합니다.
7. 필요한 완료 경계 리뷰를 한 번 수행하고, 지적 수정분을 확인합니다. 외부 모델과 실행 방식은 작업 환경의 실제 정책을 따릅니다.
8. 관련 원본·생성 결과·검증 기록을 함께 커밋하고 브랜치를 올립니다. PR의 **Validate and build** 검사가 통과한 커밋을 확인한 뒤 통합합니다.
9. 설치본 적용은 [별도 업데이트 절차](02-skills.md)에 따라 진행합니다. GitHub 커밋과 설치 적용을 같은 상태로 보고하지 않습니다.

```bash
git add manual skills diagrams scripts docs dist evidence README.md CHANGELOG.md VERSION package.json package-lock.json
git diff --cached --stat
git commit -m "docs: 프로젝트 전달 절차 보완"
git push -u origin HEAD
```

여러 사람이 수정했다면 같은 원본의 충돌을 먼저 해결하고 생성 결과를 다시 만듭니다. `dist`의 충돌만 손으로 합치지 않습니다. PDF와 ZIP은 글꼴·브라우저·생성 시각 때문에 바이트가 달라질 수 있습니다. CI는 먼저 커밋된 원본·PDF·문서와 빌드 기록의 해시가 일치하는지 확인합니다. 이후 원격에서 재생성한 HTML과 GitHub 읽기용 문서는 커밋과 같아야 합니다. 새 ZIP은 Git에 커밋하지 않고 로컬 파일과 CI artifact로 제공합니다.

## 흐름도 수정

현재 그림은 Archify 3.0.1로 생성한 결과와 검증 기록을 보존합니다. 이 저장소는 제3자 Archify 스킬 전체를 포함하지 않습니다. 설치된 Archify 스킬의 지침을 읽고 해당 버전·경로를 확인합니다. 저장소 루트에서 다음 형식으로 생성합니다.

```bash
node /실제/archify/bin/archify.mjs finalize workflow diagrams/workflow.json dist/02-workflow-map.html --quality showcase --json
```

검증 실패를 통과로 기록하지 않습니다. 완료 기록과 브라우저 검증 범위를 `evidence/`에 남기고, 매뉴얼을 다시 빌드해 오프라인 묶음과 해시를 갱신합니다. Archify 버전 변경은 별도 변경으로 기록합니다.

## CI와 배포 범위

`.github/workflows/validate.yml`은 main push·PR·수동 실행에서 기존 산출물 일치 검사, 스킬 테스트, 문서 재생성, PDF 및 ZIP 생성을 수행합니다. 결과는 30일간 workflow artifact로 보관합니다. 이 동작은 웹사이트 공개, 릴리스 발행, 개인 설치본 변경, 제품 배포를 수행하지 않습니다.

되돌릴 때는 현재 변경을 보존한 후 `git revert <문제 커밋>`으로 수정 이력을 남기고 다시 검증합니다. 설치본은 보관한 이전 버전으로 복구하고 새 채팅에서 확인합니다.
