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
제외할 기능: 회원가입, 유료 결제, 서버 배포
완료 목표: 샘플 PDF 한 개를 로컬에서 변환하고 결과에서 지정한 단어를 실제로 찾는다.
```

기본 목표는 로컬 동작 검증과 인계입니다. GitHub 저장도 원하면 **GitHub 대상 및 허용 행동**에 저장소와 범위를 적으세요. 예를 들어 “지정한 비공개 저장소에 브랜치 push와 PR 생성까지”입니다. `nano`에서 **Ctrl+O → Enter → Ctrl+X**로 저장하고 나옵니다. `HERDR-OPERATIONS.md`는 주 모델이 협업할 때 읽습니다.

## 5. Herdr 탭의 셸에서 Codex 실행하기

```sh
pwd
codex --no-daemon -C "$PWD" -m gpt-6-astra -c 'model_reasoning_effort="xhigh"'
```

`-C "$PWD"`로 현재 프로젝트를 지정하고, `--no-daemon`으로 Herdr 터미널 안에서 실행합니다. Astra와 xhigh는 실행 양식의 기본 후보입니다. 모델 지원 오류가 나면 같은 컴퓨터에서 `codex debug models`로 지원 목록을 확인하세요.

## 6. Codex 대화 입력칸에 첫 요청 보내기

Codex가 열리면 다음 문장을 **Codex 대화 입력칸**에 붙여넣고 Enter를 누르세요.

```text
현재 프로젝트의 HERDR-PROJECT.md와 HERDR-OPERATIONS.md를 실제로 읽고 실행해.

현재 컴퓨터와 프로젝트 절대경로, 내가 적은 아이디어, 완료 목표를 확인해.
네 도구 환경에서 herdr-app ls와 herdr-app status를 실행하고,
현재 Herdr 터미널을 식별하면 herdr-core get으로 조회해. 확인한 접근 범위를 알려줘.

너는 주 실행 책임자야. 완료 조건을 한 문장으로 정리하고 docs/STATE.md에
현재 단계와 다음 행동을 기록한 뒤 첫 작업을 시작해. 기획, 조사, 개발 인계,
구현, 실제 동작 검증을 문서의 순서와 허용 범위에 맞춰 진행해.
독립 작업에 도움이 될 때만 Herdr 작업자를 열고, 결과 파일을 직접 읽어 검증해.
사용자만 결정할 사항은 모아서 질문하고 그 답과 관계없는 작업은 계속해.
완료 목표에 도달하면 실행 방법, 검증 결과, 남은 제한을 알려줘.
```

**시작 확인**은 첫 답변과 상태 파일로 합니다. 주 모델이 말한 컴퓨터·폴더·아이디어가 맞는지, `docs/STATE.md`에 현재 단계와 다음 행동이 기록됐는지 확인하세요. 작은 작업은 주 모델 혼자 시작할 수 있습니다.

## 접근이 막히거나 다음 날 이어갈 때

**Herdr 소켓에서 permission denied가 나올 때**는 주 모델에게 실패한 명령과 오류를 확인시킵니다. 필요한 권한을 해당 환경의 공식 절차로 마련한 뒤 Codex 안에서 같은 조회를 다시 실행하세요. 실제 협업은 작업자가 지시를 받고 지정한 결과 파일을 저장한 뒤 주 모델이 그 내용을 확인한 시점에 검증할 수 있습니다.

**재개할 때**는 같은 컴퓨터의 같은 프로젝트 폴더에서 5단계로 Codex를 열고 아래 요청을 입력합니다.

```text
HERDR-PROJECT.md, HERDR-OPERATIONS.md와 docs/STATE.md를 읽고 중단 지점부터 재개해.
현재 Git 변경, 기존 Herdr 작업자, 저장된 결과 파일을 먼저 대조해.
마지막으로 확인된 완료 조건과 다음 행동을 알려주고 첫 미완료 작업을 수행해.
```

[프로젝트 입력 양식](../templates/herdr-project/HERDR-PROJECT.md) · [협업 운영 설명서](../templates/herdr-project/HERDR-OPERATIONS.md)
