# AI Engineering OS 연결

재사용 원본은 `krdn/ai-engineering-os`다. 이 스킬은 원본 코드·계약·모델 registry의 사본을 내장하지 않는다.
작성 시 로컬 원본 HEAD `6b98898648b0579be1b421b010cd9247aba4c5c7`의 README·온보딩·계약·CLI를 대조했다. 실제 프로젝트의 현재 파일과 `--help`가 아래 예시보다 우선한다. 이 기록은 최신 원격 상태나 모델 지원의 증명이 아니다.

## 도입 경계를 확인한다

- 기존 AEOS 프로젝트는 현재 루트의 `README.md`, `PROJECT.md`, `AGENTS.md`, `ARCHITECT.md`와 해당 TASK/CONTEXT를 읽는다.
- 새 프로젝트가 원본 템플릿 사용을 요청하면 사용자 지정 대상에 템플릿을 적용한다. GitHub 저장소 생성은 요청된 범위·이름·공개 여부를 확인한다. 로컬 구성이면 원본을 읽어 필요한 파일만 복사하며 원본 저장소에 제품 코드를 쓰지 않는다.
- 기존 프로젝트 도입은 원본 `docs/03-adopting-existing-project.md`를 읽고 동등 문서와 기준 경로를 먼저 매핑한다. 부분 `.ai`만 보이면 누락된 계약·도구 의존성을 확인하고 완전한 도입으로 표현하지 않는다.
- `examples/stock-forecast`, 예제 생성기와 예제 테스트는 도입 필수가 아니다. 포함/제외 시 참조 의존성을 함께 확인한다. 기존 프로젝트에서 예제를 제거하는 일은 별도 요청 없이 하지 않는다.
- 원본이 로컬에 없고 연결 도구로도 읽을 수 없다면 계약·CLI를 추측해 복원하지 않는다. 일반 문서 방식으로 가능한 작업을 진행하고 AEOS 연결의 제한을 밝힌다.

## 한 가지 Core를 유지한다

| 내용 | 기존 AEOS 기준 |
| --- | --- |
| 제품 목적·범위 | `PROJECT.md` |
| 행동·검증 규칙 | `AGENTS.md` |
| 구조 경계 | `ARCHITECT.md` |
| 작업 계약 | `.ai/contracts/{TASK,CONTEXT,RESULT,EVAL,REVIEW,DECISION}.md` |
| 작업별 기록 | `.ai/tasks/TASK-<id>/` |
| 현재 계획·상태 | 기존 이슈/문서. 없으면 필요한 요약만 추가 |
| 모델 선택·이력 | `.ai/models/registry.json`과 참조 guide/evidence |

PROJECT/ARCHITECT에는 보일러플레이트 자체 설명을 제품 목적과 경계로 조정한다. 제품과 관련된 Core 불변식은 보존한다. WORK/STATE 문서를 추가하더라도 TASK 결과를 이중 관리하지 않는다.

## CLI를 사용할 때

Python 3.11+와 현재 CLI·계약·registry 의존성이 갖춰졌는지 확인한다. 저장소의 스크립트는 실행 전 필요한 부분을 읽는다. 루트에서 현재 help를 먼저 확인한다.

```text
python3 scripts/aeos.py --help
python3 scripts/aeos.py validate
python3 scripts/aeos.py new-task TASK-001
```

위 ID는 예시다. `.ai/tasks`를 확인해 사용하지 않은 유효 ID를 고른다. 현재 구현은 `TASK-` 뒤 영문·숫자·하이픈을 허용하고 기존 ID를 거부한다. `new-task`도 registry validation을 먼저 수행하며 여섯 계약 틀을 생성한다. TASK/CONTEXT를 먼저 채우고 RESULT/EVAL/REVIEW/DECISION은 결과가 생겼을 때만 작성한다.

`validate`는 registry·이력·증거 구조의 무결성을 검사한다. 제품 동작·모델 접속·모델 성능을 검사하지 않는다. registry 오류를 우회하려고 자동 승격하거나 이력을 재작성하지 않는다. 수동 계약 사용으로 가능한 범위를 진행하고 오류를 별도로 남긴다.

선택적으로 packet을 만들 수 있다.

```text
python3 scripts/aeos.py packet TASK-001 --runtime standalone --allow-unverified
```

이는 `DRAFT ONLY` 문서를 표준 출력에 만든다. 모델을 실행하거나 현재 세션 모델을 바꾸지 않는다. 실행용 packet은 활성 모델·완성된 계약 등 현재 CLI 조건을 충족해야 한다. 패킷 출력과 저장 경로에 비밀값을 넣지 않는다.

## 결과와 승인을 구분한다

구현자는 RESULT/EVAL에 실제 변경·검사를 쓴다. REVIEW와 최종 DECISION은 독립 검토자 또는 사람이 담당한다. 외부 리뷰 내용을 기록할 때 실제 검토자·모델·대상 revision과 한계를 보존하고, 최종 승인 주체를 꾸며 쓰지 않는다.

현재 AI로 문서를 수동 수행하는 것과 registry가 선택한 모델로 실행하는 것은 다르다. 등록된 candidate를 검증 완료·실사용 모델이라고 표현하지 않는다. 오래된 registry·역할표를 이유로 사용자 지정 모델이나 전역 리뷰 설정을 자동 교체하지 않는다. 실제 충돌은 명시한다.

Standalone과 Orca는 같은 Core 계약을 소비한다. 여러 작업자 실행은 별도 요청과 현재 설치된 런타임 가이드가 있을 때 연결한다. packet 생성·enqueue·`worker_done`만으로 통합/배포 완료를 선언하지 않는다.
