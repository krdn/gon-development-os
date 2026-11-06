# Herdr + Codex CLI 실행 워크플로우 1.3.0

`index.html`을 브라우저로 열고 **00 준비 → P1~P5 → 01 개발** 순서로 따라갑니다.

- 기획 탭 A는 같은 Codex 세션을 유지합니다. B의 독립 조사 세션은 선택이며, C는 파일 확인용 쉘입니다.
- P5에서 최종 문서를 확인한 뒤 개발 탭의 새 Codex가 문서를 읽고 시작합니다.
- 각 단계에 입력할 위치, 세션 선택, 저장할 파일, 복사할 요청문, 직접 확인 항목을 표시합니다.
- 분할 터미널 배치·세션 선택·문서 흐름 도움말을 펼치면 예시와 설명을 볼 수 있습니다.
- `example-project/README.md`부터 읽으면 채워진 P1~P5와 최종 문서를 확인할 수 있습니다. 예시는 실제 조사·승인·제품 구현 결과가 아닙니다.
- `guide.pdf`는 할 일 앱 예제, `project-guide.pdf`는 내 기획용입니다. PDF 쪽수와 요청문 보존 결과는 `pdf-validation.json`에 있습니다.

이 안내서는 실제 프로젝트를 자동 실행하지 않습니다. 명령은 쉘, 자연어 요청과 `/status` 같은 Codex 명령은 Codex 입력칸에 구분해 넣습니다. 체크는 사용자 자신의 확인 기록이며 실제 검사·배포를 수행하지 않습니다.

## 편집·검증

`development-steps.json`은 개발 예제, `project-steps.json`은 내 기획에서 달라지는 내용, `planning-steps.json`은 관리 저장소의 공통 P1~P5 사본입니다. `handbook.html`은 분할 터미널·세션·문서 설명, `template.html`·`style.css`·`viewer.js`는 화면과 동작입니다.

Node.js 22 이상, Python 3.11 이상, 한국어 글꼴이 필요합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
npm ci
npx playwright install chromium
npm run build
npm test
python3 validate-guide.py --pdf --manual-planning /실제/관리저장소/manual/planning-steps.json
python3 package-guide.py
```

기존 브라우저는 `CHROMIUM_PATH=/실제/브라우저`로 지정합니다. 흐름도 변경은 Archify의 전체 검증을 다시 수행해 `*-validation.json`을 갱신합니다. 패키징 전에 현재 파일 목록·해시·검증 결과로 `verification.json`을 갱신해야 합니다. 과거 검증을 새 버전의 성공으로 사용하지 않습니다. 설치 스킬·앱 설정·GitHub 저장소·실제 제품 배포는 별도입니다.

## 통합 저장소에서 재생성

저장소 전체를 받았다면 루트의 전체 재생성 안내 `docs/05-rebuild-workflow.md`를 따릅니다. `npm run build:all`은 두 안내서의 현재 브라우저·PDF 검사를 실행하고 검증 기록과 ZIP을 새로 만듭니다. preview 이미지·evidence 하위 자료·외부 리뷰 기록은 이전 확인 자료이며 이번 검사로 새로 관찰한 결과와 구분합니다.
