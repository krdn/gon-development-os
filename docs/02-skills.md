# 스킬 설치와 사용

## 두 스킬의 역할

| 스킬 | 사용하는 상황 | 포함된 자료 |
| --- | --- | --- |
| [gon-project-lifecycle](../skills/gon-project-lifecycle/SKILL.md) | GitHub 기준 신규 시작, 기존 도입, 작업 재개, 검증·전달 | 단계별/공통 지침 6개, 문서 틀 7개, 비파괴 생성기·읽기 전용 GitHub 점검기·검증 도구와 테스트 |
| [gon-web-engineering](../skills/gon-web-engineering/SKILL.md) | 웹 프로젝트 기술 선택·구현·검증 | 웹 지침 5개, 설정 도구와 테스트 |

일반 작업은 lifecycle로 시작합니다. 웹 구현이 포함되면 web-engineering을 함께 적용합니다. 이미 정해진 기술·문서·배포 방식은 프로젝트 지침을 우선합니다.

1.1부터 [GitHub 관리 절차](../skills/gon-project-lifecycle/references/github-management.md)에 따라 관리 기록을 연결합니다. 저장소 문서·Issues/Projects·PR/CI·릴리스/배포에 각 기록을 두고 해당 단계의 원격 상태를 다시 조회합니다. 로컬 PLAN/STATE는 URL을 가진 요약입니다. 기능 15개 영역의 사용/미적용/불가/미완료와 대체 기록은 프로젝트 관리 문서에 남깁니다. web-engineering도 같은 기준에 UI·API·DB 증거를 연결합니다. 새 원격 기능·권한·릴리스·배포가 자동 승인되는 것은 아닙니다.

## 새 컴퓨터에 설치

1. 이 비공개 저장소에 접근 가능한 계정으로 저장소를 내려받습니다.
2. 저장소 루트에서 다음을 실행합니다. 기존 설치가 있으면 여기서 멈추고 아래 업데이트 절차를 사용합니다.

```bash
mkdir -p "$HOME/.agents/skills"
python3 - <<'PY'
from pathlib import Path
import shutil

root = Path.cwd()
target = Path.home() / '.agents/skills'
names = ['gon-project-lifecycle', 'gon-web-engineering']
# 하나만 설치·업데이트할 때는 names에 해당 스킬 이름만 남깁니다.
for name in names:
    if not (root / 'skills' / name / 'SKILL.md').is_file():
        raise SystemExit('저장소 루트에서 실행하세요.')
    dest = target / name
    if dest.exists() or dest.is_symlink():
        raise SystemExit(f'기존 설치를 먼저 비교하세요: {dest}')
for name in names:
    shutil.copytree(root / 'skills' / name, target / name,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    print(f'설치 파일 복사 완료: {target / name}')
PY
```

3. 새 채팅에서 제공되는 스킬 목록과 실제 파일 경로를 확인하고 아래처럼 명시 호출합니다.

```text
$gon-project-lifecycle
이 스킬의 실제 원문 경로와 적용할 절차를 먼저 확인해줘.
[프로젝트 경로]의 현재 상태를 확인하고 [이번 목표]를 진행해줘.
```

파일 복사 완료만으로 해당 앱의 스킬 로딩·자동 선택·실제 실행 성공이 증명되지는 않습니다. 다른 컴퓨터·Cloud·Orca는 각 실행 환경의 스킬 발견 경로와 파일 접근 권한을 확인합니다. 로컬 `~/.agents/skills`가 모든 환경으로 자동 전달된다고 가정하지 않습니다.

## 기존 설치를 업데이트

1. 저장소를 `git pull --ff-only`로 갱신합니다.
2. 저장소 원본과 설치본을 비교합니다. 차이가 있으면 설치본의 수동 변경인지 먼저 판단합니다. 아래 명령의 종료코드 1은 차이가 있다는 의미입니다.

```bash
diff -ru -x __pycache__ -x '*.pyc' skills/gon-project-lifecycle "$HOME/.agents/skills/gon-project-lifecycle"
diff -ru -x __pycache__ -x '*.pyc' skills/gon-web-engineering "$HOME/.agents/skills/gon-web-engineering"
```

3. 필요한 수동 변경은 저장소 작업 브랜치에 반영하고 검증합니다.
4. 교체하기로 확정한 기존 스킬 디렉터리를 `~/.local/share/gon-development-os/backups/<날짜-시각>/` 아래로 이동해 보관합니다. 스킬 검색 경로 밖에 보관해 중복 로딩을 피합니다. 심볼릭 링크라면 실제 대상과 소유 저장소를 먼저 확인합니다.
5. 위 새 설치 절차의 `names`를 이번에 교체할 스킬만 포함하도록 바꾼 뒤 원본을 복사합니다. 예를 들어 lifecycle만 갱신하면 `names = ['gon-project-lifecycle']`로 실행합니다. 실패하면 새로 복사된 해당 디렉터리만 치우고 보관본을 원래 위치로 복구합니다.
6. 새 채팅의 인식, 명시 호출, 작은 실제 작업을 확인한 후 적용 버전·커밋과 결과를 기록합니다.

초기 1.0 가져오기 해시는 [기록](../evidence/imported-skills.json)에 보존했습니다. 1.1의 로컬 설치 적용·검증·외부 리뷰 미완료 상태는 [별도 기록](../evidence/github-management-validation.json)에서 구분합니다. 다른 PC의 설치 상태를 이 기록으로 대신하지 않습니다.
