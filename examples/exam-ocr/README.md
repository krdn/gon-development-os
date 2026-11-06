# 시험문제지 OCR PDF 프로젝트

시험지 스캔 PDF 또는 JPG/PNG를 받아 원본의 문제·선택지·수식·그림 배치를 보존한 **검색 가능한 PDF**를 만드는 로컬 도구의 실행 문서다. 현재는 문서와 Herdr 협업 동작 확인용이며 제품 구현 완료본이 아니다.

## 지금 사용할 문서

1. [HERDR-PROJECT.md](HERDR-PROJECT.md): 채워진 아이디어·권한·모델 협업·전체 진행 규칙.
2. [PROJECT-BRIEF.md](docs/PROJECT-BRIEF.md): 무엇을 만들고 무엇이면 완료인지.
3. [PLAN.md](docs/PLAN.md): 선행 관계와 작업 분담.
4. [STATE.md](docs/STATE.md): 실제 완료·미완료·다음 행동.

설계 세부사항은 [ARCHITECTURE.md](docs/ARCHITECTURE.md), 검증은 [TEST-PLAN.md](docs/TEST-PLAN.md), 조사 근거는 [03-evidence.md](docs/research/03-evidence.md), Herdr 명령은 [HERDR-OPERATIONS.md](HERDR-OPERATIONS.md)에 있다.

## 전체 개발 시작 요청

먼저 [실제 Herdr 시험 결과](RUN-RESULT.md)를 확인한다. 이번 환경에서는 주 모델의 샌드박스가 Herdr 소켓 접근을 차단했다. **주 모델 자신의 도구 실행 환경에서** `herdr-app ls`, `herdr-app status`, `herdr-core get`이 성공하는지 확인해야 한다. 일반 쉘에서 성공하는 것만으로 충분하지 않다. 차단되면 해당 세션의 공식 권한 요청·설정 경로로 필요한 접근을 해결한 뒤 재시험한다. 새 Codex 세션은 아래의 `--yolo` 시작 옵션을 사용하고 협업 작업자도 실행 계약의 CLI별 승인 생략 옵션을 사용한다.

이 폴더를 실제 개발 작업 폴더로 사용할 수 있다. 다른 경로에 복사하면 주 모델은 현재 폴더의 절대경로를 다시 확인한다. Herdr의 해당 폴더에서 주 모델을 실행한 뒤 아래를 **대화 입력칸**에 넣는다.

```text
$gon-project-lifecycle
HERDR-PROJECT.md와 HERDR-OPERATIONS.md, docs/STATE.md를 읽어.
단계별 전문 스킬 적용 규칙을 따르고 실제 경로와 적용 근거를 상태에 남겨.
이번 범위는 로컬 CLI이므로 웹 스킬은 not_applicable로 기록해.
문서 확인 시험을 마치고 이제 시험문제지 OCR PDF 도구의 전체 개발을 시작해.
docs/PROJECT-BRIEF.md의 범위와 AC를 기준으로 PLAN의 첫 미완료 작업부터 진행해.
필요한 독립 작업은 Herdr 협업 모델에게 맡기고 결과 파일을 읽어 통합해.
원본이 아직 없으면 합성 시험지로 구현·검증을 진행하고 원본 수용 검사는 별도로 남겨.
계획 설명만으로 끝내지 말고 허용된 로컬 구현·동작 검증·인계까지 계속해.
원문을 외부 API에 보내거나 과금·공개·원격 배포하지 마.
```

주 모델 실행 예시(현재 프로젝트 폴더의 쉘):

```sh
codex --yolo --no-daemon -m gpt-6-astra -c model_reasoning_effort='"xhigh"'
```

모델/effort 지원은 시작 시 확인한다. 도구 실행 승인은 --yolo로 생략한다. 계정 로그인·OS 권한 요청은 실제 화면을 확인해 해당 절차로 처리한다.

## 문서 연결만 다시 시험하기

```text
PILOT.md를 읽고 그 범위만 수행해. 제품 구현과 설치는 하지 마.
```

## 중단 후 재개

```text
$gon-project-lifecycle
HERDR-PROJECT.md, HERDR-OPERATIONS.md와 docs/STATE.md를 읽고 현재 모드와 권한을 유지해 재개해.
현재 세션의 스킬 경로를 확인하고 단계별 적용 규칙을 따라.
구버전 실행 문서에 해당 절이 없으면 갱신 필요를 알리고, 시작·재개에는 lifecycle,
웹 작업에는 web-engineering의 실제 지침을 읽어 적용해.
기존 Herdr 작업자와 결과 파일을 조회해 중복 생성하지 마.
실제 Git 변경·검증 근거를 확인한 뒤 첫 미완료 작업을 진행해.
```

## 나중에 준비할 실제 시험지

원본 PDF 또는 순서가 정해진 JPG/PNG, 인쇄 언어, 검색해서 확인할 문구를 준비한다. 입력은 프로젝트의 `data/input/` 같은 별도 폴더에 두고 원본은 수정하지 않는다. 학생 개인정보가 없는 시험지를 우선한다. 현재 묶음에는 사용자 시험지나 답안이 없다.

결과 PDF는 원본 이미지 위에 검색용 텍스트를 추가하는 방식이다. 편집 가능한 새 시험지처럼 다시 조판하는 PDF가 필요하면 개발 전에 범위를 수정한다.
