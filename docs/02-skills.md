# 스킬 설치와 사용

## 두 스킬의 역할

| 스킬 | 사용하는 상황 | 포함된 자료 |
| --- | --- | --- |
| [gon-project-lifecycle](../skills/gon-project-lifecycle/SKILL.md) | GitHub 기준 신규 시작, 기존 도입, 작업 재개, 검증·전달 | 단계별/공통 지침, 문서 틀, 비파괴 생성기·GitHub 점검기·단계 검토 검사와 테스트 |
| [gon-web-engineering](../skills/gon-web-engineering/SKILL.md) | 웹 프로젝트 기술 선택·구현·검증 | 웹 지침 5개, 설정 도구와 테스트 |

일반 작업은 lifecycle로 시작합니다. 웹 구현이 포함되면 web-engineering을 함께 적용합니다. 이미 정해진 기술·문서·배포 방식은 프로젝트 지침을 우선합니다.

1.1부터 [GitHub 관리 절차](../skills/gon-project-lifecycle/references/github-management.md)에 따라 관리 기록을 연결합니다. 저장소 문서·Issues/Projects·PR/CI·릴리스/배포에 각 기록을 두고 해당 단계의 원격 상태를 다시 조회합니다. 로컬 PLAN/STATE는 URL을 가진 요약입니다. 기능 15개 영역의 사용/미적용/불가/미완료와 대체 기록은 프로젝트 관리 문서에 남깁니다. web-engineering도 같은 기준에 UI·API·DB 증거를 연결합니다. 새 원격 기능·권한·릴리스·배포가 자동 승인되는 것은 아닙니다.

## 실행할 컴퓨터에 설치·업데이트

[gon-skills 설치 안내](https://github.com/krdn/gon-skills#갱신)를 따릅니다. Herdr 원격 Space에서는 **Codex가 실행되는 컴퓨터**의 설치를 확인하세요. 처음에는 비공개 원본을 계속 사용할 경로에 복제합니다. 이미 동기화 중이면 기존 체크아웃에서 진행합니다.

```sh
# 최초 1회
mkdir -p "$HOME/dev"
git clone https://github.com/krdn/gon-skills.git "$HOME/dev/gon-skills"
```

원본 폴더에서 Python 3.11 이상과 PyYAML을 준비합니다. 기존 환경이 없다면 가상환경을 만들 수 있습니다.

```sh
cd "$HOME/dev/gon-skills"
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

다음 날 새 셸에서 업데이트할 때도 기존 원본 폴더로 이동합니다. 위 가상환경을 사용했다면 `. .venv/bin/activate`로 다시 활성화하세요. 깨끗한 `main`에서 업데이트합니다. 동기화기는 Codex·Claude Code·Gemini CLI·Hermes 경로를 함께 관리합니다. 먼저 대상과 변경 목록을 살펴보세요.

```sh
git pull --ff-only && python3 scripts/sync-skills.py --dry-run
```

미리보기의 변경을 반영하려면 같은 원본 폴더에서 실행합니다.

```sh
python3 scripts/sync-skills.py --apply && python3 scripts/sync-skills.py --check
```

구버전 OS에서 수동 복사한 설치본과 충돌하면 미리보기가 중단됩니다. 해당 파일을 원본과 비교하고 보관할 로컬 수정을 백업·병합하세요. 미관리 설치를 처음 인수하기로 결정한 경우에만 원본 안내의 `--adopt-existing` 절차를 사용합니다. 이미 관리 중인 파일은 원본과 차이를 해소한 뒤 재실행합니다.

새 Codex 세션의 스킬 선택 목록에서 두 이름을 확인하고, [Herdr 첫 요청](06-herdr-cli-start.md)을 사용하세요. 실행 문서는 시작·P5 인계·재개에 lifecycle, 웹 작업에 web-engineering을 적용하도록 지시합니다. 실제 경로·참조·작업 근거를 STATE에 남기고 새 세션과 작업자에게 필요한 스킬을 전달합니다. 별도 스킬 `$gon-task-execute`는 사용자가 해당 과제에 명시했을 때만 적용하며 두 전문 스킬은 이미 정한 목표·수용 기준을 이어받습니다.

이 저장소의 `skills/`는 [고정된 버전](../skills.lock)의 오프라인 열람·테스트용 사본입니다. CLI 설치는 위 동기화기를 사용합니다. [최초 가져오기 기록](../evidence/imported-skills.json)과 [1.1 당시 검증](../evidence/github-management-validation.json)은 과거 시점의 자료입니다.
