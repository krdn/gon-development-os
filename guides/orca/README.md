# Orca + Codex CLI 실행 안내서 1.0.0

`index.html`을 브라우저로 열고 프로젝트명·폴더를 바꾼 뒤 **S0**부터 따라갑니다. 읽는 데 설치나 로그인은 필요하지 않습니다. 요청문을 실제 Codex에 보내는 시점부터 해당 작업이 실행됩니다.

- `guide.pdf`: 기본값으로 인쇄한 전체 안내서. 내 값으로 바꾸려면 HTML의 인쇄/PDF 버튼을 사용합니다.
- `examples.html`: P1~P5와 최종 문서·작업 계획·STATE의 전체 예시.
- `example-project/`: 설명용 가상 문서 8개. 실제 조사·승인·앱 구현·Orca 작업자·GitHub 실행 결과가 아닙니다.
- `templates/`: P1~P4, PROJECT-BRIEF, TASKS, STATE, 작업자 지시서의 빈 양식 8개.
- `verification.json`: 안내서의 검사 범위와 제한.

기획 P1~P5는 같은 세션에서 진행하고 Git 기준 문서를 저장한 뒤 새 개발 주 조정 세션으로 넘깁니다. 이는 권장 운영 방식이며 제품의 강제 규칙이 아닙니다. 작업자가 실행 중일 때는 기존 조정 세션을 유지합니다.

Orca CLI 1.4.246·Codex CLI 0.166.0의 설치 가이드/도움말, 설치 화면 리소스의 메뉴명, 공식 OpenAI·GitHub 문서를 2026-11-02에 대조했습니다. 실제 UI 클릭·설정 저장이나 사용자 프로젝트의 원격 작업은 시험하지 않았습니다. 기존 Herdr판은 보존했습니다.

## 수정·재생성

내용 원본은 `steps.json`과 `build-guide.py`이며, 화면 동작은 `viewer.js`, 스타일은 `style.css`입니다. 생성된 HTML만 고치지 않습니다.

읽기에는 필요 없지만, 다시 만들려면 Python 3와 Node.js 22+, npm을 사용합니다.

```sh
npm ci
npm run build
npm run pdf
npm test
python3 validate-guide.py --pdf
```

Playwright용 Chromium이 없으면 `npx playwright install chromium`을 실행하거나, 기존 Chrome의 절대 경로를 `CHROMIUM_PATH` 환경변수로 지정합니다. PDF 내용 검사에는 `pdftotext`가 필요합니다. 검사는 이 안내서의 로컬 화면·파일만 사용하며 실제 Orca 작업자나 GitHub 변경은 실행하지 않습니다.

패키징은 `python3 package-guide.py`로 수행합니다. 브라우저 설정과 체크는 이 안내서의 브라우저 저장소에만 남으므로 프로젝트의 실제 완료 기록은 STATE.md에 저장해야 합니다.

## 통합 저장소에서 재생성

저장소 전체를 받았다면 루트의 전체 재생성 안내 `docs/05-rebuild-workflow.md`를 따릅니다. `npm run build:all`은 두 안내서의 현재 브라우저·PDF 검사를 실행하고 검증 기록과 ZIP을 새로 만듭니다. preview 이미지·evidence 하위 자료·외부 리뷰 기록은 이전 확인 자료이며 이번 검사로 새로 관찰한 결과와 구분합니다.
