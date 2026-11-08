# Herdr CLI에서 프로젝트 워크플로우 시작하기

Herdr에서 작업할 컴퓨터를 고르고, 그 컴퓨터의 프로젝트 폴더에 실행 문서 두 개를 넣습니다. 같은 폴더에서 Codex를 열고 첫 요청을 보내면 주 모델이 아이디어를 읽고 작업을 시작합니다.

## 1. 일반 터미널에서 Herdr 열기

```sh
herdr-app
```

Herdr 창이 열리면 일반 터미널에서 아래 두 방법 중 하나를 선택하세요. 첫 명령이 실행 중이면 일반 터미널 탭을 하나 더 엽니다.

**현재 PC에서 개발할 때**

```sh
herdr-app do space.new --name "프로젝트 개발" --tab "주 모델"
```

**Lenovo에서 Herdr를 보고 ASUS에서 개발할 때**

```sh
hc machine ls
```

목록에서 ASUS 연결 이름과 상태를 확인하세요. 연결 이름이 `home-server`이고 상태가 `connected`이면 다음 명령을 실행합니다. 다른 이름을 등록했다면 해당 이름을 사용하세요.

```sh
herdr-app do space.new --machine home-server --name "ASUS 프로젝트 개발" --tab "주 모델"
```

이제 **Herdr 창의 ‘주 모델’ 탭**을 클릭하고 다음을 입력합니다. 이후 셸 명령은 모두 이 탭에서 실행합니다.

```sh
hostname
pwd
command -v codex
```

첫 줄에서 의도한 컴퓨터 이름을, 마지막 줄에서 Codex 실행 파일 경로를 확인하세요. 원격 Space에서는 파일과 Codex가 모두 ASUS에 있어야 합니다.

## 2. 프로젝트 폴더로 이동하기

새 프로젝트라면 `my-first-project`를 원하는 이름으로 바꾸세요.

```sh
PROJECT="$HOME/projects/my-first-project"
mkdir -p "$PROJECT" && cd "$PROJECT"
pwd
```

기존 프로젝트라면 위 명령 대신 해당 프로젝트의 루트로 이동합니다. 예를 들어 `cd "$HOME/dev/test/test-ocr"`입니다. 다음 단계에서 실행 문서를 복사할 위치가 맞는지 `pwd`로 확인하세요.

## 3. 실행 문서 두 개 가져오기

현재 프로젝트 폴더에서 실행하세요. 임시 폴더에 비공개 저장소를 내려받으므로, 작업하는 컴퓨터의 Git에 저장소 읽기 권한이 필요합니다.

```sh
WORKFLOW_SRC="$(mktemp -d)"
git clone --depth 1 https://github.com/krdn/gon-development-os.git "$WORKFLOW_SRC" &&
  cp -i "$WORKFLOW_SRC/templates/herdr-project/HERDR-PROJECT.md" \
        "$WORKFLOW_SRC/templates/herdr-project/HERDR-OPERATIONS.md" .
ls -l HERDR-PROJECT.md HERDR-OPERATIONS.md
```

같은 파일이 있으면 덮어쓸지 묻습니다. 기존 입력을 보존하려면 `n`을 선택하고 두 내용을 비교하세요. 복사가 성공하고 두 파일이 보이면 다음으로 진행합니다.

## 4. 만들고 싶은 것 적기

```sh
nano HERDR-PROJECT.md
```

**사용자 입력**에서 아이디어의 대괄호 안내문을 바꿉니다. 아이디어가 필수이고, 사용 예와 완료 목표를 함께 쓰면 주 모델이 결과를 검사하기 쉽습니다. 예를 들어 다음처럼 작성합니다.

```text
프로젝트 아이디어: 스캔한 시험문제지 PDF를 검색 가능한 PDF로 변환하는 도구
누가 어떤 문제를 해결하는가: 교사가 스캔본에서 문제의 단어를 검색하고 싶다.
꼭 필요한 기능 또는 사용 예: PDF 한 개를 입력하고 결과 PDF에서 한글 단어를 검색한다.
제외할 기능: 웹 화면, 회원가입, 유료 결제, 서버 배포
기술·기한·비용·데이터 제약: 로컬 CLI로 실행
완료 목표: 샘플 PDF 한 개를 로컬에서 변환하고 결과에서 지정한 단어를 실제로 찾는다.
```

기본 목표는 로컬 동작 검증과 인계입니다. GitHub 저장도 원하면 **GitHub 대상 및 허용 행동**에 저장소와 범위를 적으세요. 예를 들어 “지정한 비공개 저장소에 브랜치 push와 PR 생성까지”입니다. `nano`에서 **Ctrl+O → Enter → Ctrl+X**로 저장하고 나옵니다. `HERDR-OPERATIONS.md`는 주 모델이 협업할 때 읽습니다.

## 5. Herdr 탭의 셸에서 Codex 실행하기

```sh
pwd
codex --yolo --no-daemon -C "$PWD" -m gpt-6-astra -c 'model_reasoning_effort="medium"'
```

`--yolo`로 도구 실행 승인을 생략하고, `-C "$PWD"`로 현재 프로젝트를 지정하고, `--no-daemon`으로 Herdr 터미널 안에서 실행합니다. Astra와 medium은 일반 작업의 시작값입니다. 단순·저위험은 low, 복잡하거나 영향이 큰 작업은 high, 극난도·핵심 위험은 xhigh를 선택하며 명시한 값을 우선합니다. 모델 지원 오류가 나면 같은 컴퓨터에서 `codex debug models`로 지원 목록을 확인하세요.

## 6. 주 모델이 사용할 스킬 확인하기

Herdr 안에서 실행한 **Codex가 실행 문서의 단계별 규칙에 따라 스킬을 읽고 적용합니다**. 3단계의 `HERDR-PROJECT.md`에는 스킬을 선택할 단계가, `HERDR-OPERATIONS.md`에는 다음 세션에 전달할 요청문과 기록 양식이 있습니다. 전문 스킬은 실행할 컴퓨터에 설치합니다.

| 언제 | Codex에서 사용할 스킬 | 결과로 확인할 것 |
| --- | --- | --- |
| 시작·P5 개발 인계 | `$gon-project-lifecycle` | 아이디어를 완료 조건으로 정리하고, P5에서 `docs/PROJECT-BRIEF.md`의 요구·수용 기준을 첫 개발 작업에 연결합니다. |
| 웹 화면·API·DB 구현 시 | `$gon-web-engineering` | 기존 기술을 확인한 뒤 해당 기능을 구현하고 사용자 동작과 관련 오류를 검사합니다. |
| 검증 결과 기록·인계·다음 날 재개 | `$gon-project-lifecycle` | 검증 결과와 남은 일을 `docs/STATE.md`에 정리하고, 허용한 GitHub 작업이 있으면 이슈·PR·CI와 연결합니다. |

Codex 입력칸에 `$`를 입력해 스킬 선택 목록에서 이름을 찾습니다. 아래 첫 요청은 lifecycle을 지정하고, 두 실행 문서의 규칙에 따라 웹 단계에서 web-engineering을 적용하도록 맡깁니다. 같은 작업의 단계가 바뀔 때마다 사용자가 스킬 이름을 다시 입력할 필요는 없습니다. 필요한 이름이 보이지 않으면 [설치·업데이트 안내](02-skills.md)에 따라 **현재 Space에서 Codex를 실행한 컴퓨터**의 설치를 확인한 뒤 새 Codex 세션을 여세요. ASUS 원격 Space라면 ASUS에서 확인합니다.

## 7. Codex 대화 입력칸에 첫 요청 보내기

Codex가 열리면 다음 문장을 **Codex 대화 입력칸**에 붙여넣고 Enter를 누르세요.

```text
$gon-project-lifecycle
현재 프로젝트의 HERDR-PROJECT.md와 HERDR-OPERATIONS.md를 실제로 읽고 실행해.
문서의 단계별 전문 스킬 적용 규칙을 따라 시작·인계·재개는 lifecycle을 적용하고,
웹 화면·API·DB 작업에 진입하면 gon-web-engineering의 실제 지침을 읽고 적용해.
P5 인계 문서가 이미 있으면 docs/PROJECT-BRIEF.md의 수용 기준과 현재 상태를 읽고
첫 미완료 작업부터 이어가. 기존 기획 답변과 제품 명세를 재사용해.

현재 컴퓨터와 프로젝트 절대경로, 내가 적은 아이디어, 완료 목표를 확인해.
네 도구 환경에서 herdr-app ls와 herdr-app status를 실행하고,
현재 Herdr 터미널을 식별하면 herdr-core get으로 조회해. 확인한 접근 범위를 알려줘.

각 단계 결과와 다음 구성안을 내게 제시하고 실제 수용·승인 뒤에 다음 단계로 넘어가.
협의·추가 요청·검사 근거를 GitHub 이슈·Discussion에 저장하고 다시 조회해.
너는 주 실행 책임자야. 완료 조건을 한 문장으로 정리하고 docs/STATE.md에
현재 단계와 다음 행동을 기록한 뒤 첫 작업을 시작해. 기획, 조사, 개발 인계,
구현, 실제 동작 검증을 문서의 순서와 허용 범위에 맞춰 진행해.
새 개발 세션과 작업자에게도 실행 문서·현재 단계·해당 작업의 스킬을 전달해.
생성할 때 Codex·Gemini는 --yolo, Claude·Opus·Fable은 --dangerously-skip-permissions를 넣어.
읽은 스킬 경로와 적용한 작업·검사 근거를 같은 상태 기록에 남겨.
독립 작업에 도움이 될 때만 Herdr 작업자를 열고, 결과 파일을 직접 읽어 검증해.
사용자만 결정할 사항은 모아서 질문하고 그 답과 관계없는 작업은 계속해.
완료 목표에 도달하면 실행 방법, 검증 결과, 남은 제한을 알려줘.
```

**시작 확인**은 첫 답변과 상태 파일로 합니다. 컴퓨터·폴더·아이디어, 현재 단계·다음 행동과 lifecycle의 실제 파일 경로를 확인하세요. 작업이 진행되면 STATE의 스킬 기록에 적용한 작업·검사 근거가 붙어야 합니다. 웹 작업이 없으면 web-engineering은 `not_applicable`, 필요한 스킬이 없으면 `missing`으로 남깁니다.

이 연결은 실행 중인 모델이 따를 지침입니다. 모델의 실제 준수는 기록과 결과로 확인합니다. 새 세션에서는 두 실행 문서와 STATE를 다시 읽고 스킬을 확인합니다. 기존 프로젝트는 3단계에서 받은 새 템플릿과 두 문서를 비교합니다. 아이디어·허용 범위·진행 기록을 보존하면서 새 [스킬 적용 절](../templates/herdr-project/HERDR-PROJECT.md#단계별-전문-스킬-적용)과 [인계·결과 양식](../templates/herdr-project/HERDR-OPERATIONS.md#새-개발-세션에-인계)을 병합하세요.

## 웹 기능을 개발할 때

처음부터 웹 개발이 목표에 포함됐다면 주 모델이 해당 단계에서 web-engineering을 적용합니다. P5 뒤의 새 개발 세션에는 `HERDR-OPERATIONS.md`의 인계 요청을 전달합니다. 사용자가 직접 열어야 한다면 같은 Space·컴퓨터에서 새 탭을 열고 동일 프로젝트 폴더로 이동해 5단계로 Codex를 실행한 뒤, STATE의 “다음 주 모델의 첫 요청”을 붙여넣으세요. 인수 회신과 쓰기 책임 전환은 실행 문서의 인계 순서를 따릅니다.

위 PDF 예시처럼 CLI만 만들던 프로젝트에 **웹 업로드·다운로드 기능을 새로 요청할 때**는 아래 요청을 사용할 수 있습니다. 새 목표와 수용 기준도 함께 정합니다.

```text
$gon-project-lifecycle
$gon-web-engineering
HERDR-PROJECT.md, HERDR-OPERATIONS.md와 docs/STATE.md를 읽고 현재 주 모델인지 확인해.
다른 주 모델이 실행 중이면 인수 회신과 책임 전환부터 수행해.
로컬 CLI에 웹 업로드·다운로드 기능을 추가하고 싶어. 목표가 바뀐 부분을 P1·P4에서 확인하고,
PROJECT-BRIEF의 새 요구 R번호·수용 기준 AC번호와 STATE의 첫 작업에 반영한 뒤 구현해.
기존 CLI 언어·코드·데이터를 재사용할 방법부터 확인하고 필요한 웹 기술 선택을 결정 기록에 남겨.
기존 웹 스택과 API를 먼저 확인해. 샘플 PDF를 브라우저에서 올리고, 변환된 PDF를
내려받아 지정한 한글 단어를 찾을 수 있는지 확인해. 손상된 PDF의 오류 표시도 검사해.
실행한 검사는 해당 AC와 연결하고 결과·남은 제한·다음 행동은 STATE에 요약해.
```

웹 검증 결과는 lifecycle이 인계할 때 그대로 사용합니다. 새 개발 세션은 실행 문서에 기록된 GitHub 저장·배포 범위를 따릅니다. 대상이나 허용 행동이 비어 있으면 로컬 검증까지 진행합니다.

## 접근이 막히거나 다음 날 이어갈 때

**Herdr 소켓에서 permission denied가 나올 때**는 주 모델에게 실패한 명령과 오류를 확인시킵니다. 필요한 권한을 해당 환경의 공식 절차로 마련한 뒤 Codex 안에서 같은 조회를 다시 실행하세요. 실제 협업은 작업자가 지시를 받고 지정한 결과 파일을 저장한 뒤 주 모델이 그 내용을 확인한 시점에 검증할 수 있습니다.

**재개할 때**는 같은 컴퓨터의 같은 프로젝트 폴더에서 5단계로 Codex를 열고 아래 요청을 입력합니다.

```text
$gon-project-lifecycle
HERDR-PROJECT.md, HERDR-OPERATIONS.md와 docs/STATE.md를 읽고 중단 지점부터 재개해.
단계별 전문 스킬 적용 규칙을 따르고 현재 세션의 스킬 경로·활성 상태를 다시 확인해.
구버전 실행 문서에 해당 절이 없으면 템플릿 갱신 필요를 알리고, 이번 요청의 배정대로
시작·재개에는 lifecycle, 웹 작업에는 gon-web-engineering의 실제 지침을 읽어 적용해.
현재 Git 변경, 기존 Herdr 작업자, 저장된 결과 파일을 먼저 대조해.
마지막으로 확인된 완료 조건과 다음 행동을 알려주고 첫 미완료 작업을 수행해.
```

[프로젝트 입력 양식](../templates/herdr-project/HERDR-PROJECT.md) · [협업 운영 설명서](../templates/herdr-project/HERDR-OPERATIONS.md)

시작 전에 과제의 난이도와 실패 영향을 판단해 effort를 고릅니다. 위 medium 예시는 일반 작업용이며, 복잡한 동시성 버그는 high, 핵심 데이터 손실 위험은 xhigh처럼 바꿉니다. 사용자가 명시한 effort가 있으면 그 값을 유지합니다.
