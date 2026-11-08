# 단계별 구성 승인과 결과 검토

Gon 방식으로 정의한 실제 단계에 적용한다. 단순 편집을 새 단계로 만들지 않는다. 승인된 범위 안의 일상 실행은 계속하고, 이미 받은 사용자 답변을 다시 요구하지 않는다.

`구성 제시 → 사용자 구성 승인 → 실행·협의 → 결과 제시 → 사용자 결과 검토 → 추가 요청 반영·재검증 → 결과 수용 후 다음 단계`

## 실행과 수용을 분리한다

- 구성안에는 단계·계약 revision·구성 버전, 역할·요청 모델/effort·파일/책임 소유권·최대 동시 인원·권한·비용 범위를 제시한다. 변경된 구성은 실행 전에 검토받는다. 실제 반환 모델은 별도 실행 근거로 남기고 요청 모델과 다르면 자동 대체하지 않는다.
- 실제 사용자 답변의 출처·시각·정확한 답변과 범위를 보존한다. 최신 명시 답변이 이미 변경을 허용했다면 그 답변을 새 대상에 연결한다. 구성 승인과 결과 수용은 따로 판정하며 한 답변이 둘을 명시한 경우 각 대상에 같은 출처를 연결할 수 있다.
- 결과에는 산출물 revision·링크, 변경 요약, 수용 기준별 검사·증거, 미검증/미결정, 사용자 선택이 필요한 질문과 다음 구성안을 담는다. 결과 수용과 다음 구성 승인이 모두 있어야 다음 단계를 실행한다.
- `changes_requested`는 같은 단계에서 추가 요청을 반영·재검증한 뒤 결과를 다시 제시한다. `held`는 해당 작업을 보류한다. 재개 답변은 실제 사용자 답변과 허용 범위를 기록한다. 최신 답변 없이 보류를 지우거나 과거 승인을 다시 최신으로 복사하지 않는다.
- 침묵·시간 경과·AI 합의·CI PASS는 사용자 승인/수용이 아니다. 같은 GitHub 계정으로 에이전트가 옮긴 답변은 사용자 본인의 GitHub 승인 리뷰가 아니다. 미검증이 남은 부분 전달은 사용자가 수용한 정확한 범위와 제품 전체의 남은 조건을 함께 남긴다.
- 도입 전 단계에 소급 구성 승인을 만들지 않는다. 기존 결과·수용 근거는 연결하고, 이번에 이 규칙을 적용하는 단계부터 기록한다. 실제 수행하지 않은 단계나 협의를 꾸며 넣지 않는다.

## 기록 위치와 에이전트 협의

단계 이슈에는 구성·결과·사용자 검토·추가 요청과 영향받는 R/AC를 연결하고, Projects에는 현재 검토 상태·revision·미해결 항목을 매핑한다. 실제 협의는 Discussion 또는 기존 이슈에 단계·구성 버전·참여자·요청/확인 모델·입력 revision·제안·반론·근거·일치/불일치·후속 확인·조정자 결론으로 남긴다. 실행 항목은 이슈, 확정 설계는 ADR로 연결한다. 내부 추론 원문·비밀값은 저장하지 않는다. 협의 기록 자체를 사용자 승인으로 취급하지 않는다.

기준 GitHub 기록을 원격에서 다시 읽고 확인한다. 아래 JSON은 그 기록을 검사할 로컬 표현이며 별도 승인 창구가 아니다. GitHub 계정·CI만으로 인간 진위를 증명할 수 없으면 절차상 통제와 미검증 한계를 유지한다.

## JSON과 CLI

스킬의 `scripts/stage_review.py`는 Python 표준 라이브러리만 사용하고 파일·원격 상태를 변경하지 않는다. 아래 `scripts/`는 이 스킬 디렉터리 기준이다.

```sh
python3 scripts/stage_review.py template --project OWNER/REPO --stage S2 --stage S3 > stage-review.json
python3 scripts/stage_review.py validate --file stage-review.json
python3 scripts/stage_review.py digest --file stage-review.json --stage S2 --target configuration
python3 scripts/stage_review.py check --file stage-review.json --stage S2 --action enter
python3 scripts/stage_review.py digest --file stage-review.json --stage S2 --target result
python3 scripts/stage_review.py check --file stage-review.json --stage S2 --action accept
python3 scripts/stage_review.py check --file stage-review.json --stage S3 --action enter
```

`template`은 승인 없는 초안을 stdout으로 출력하고 한계 안내를 stderr로 출력한다. `미정`을 실제 구성으로 채운 뒤 사용자에게 제시한다. `validate`는 구조만 확인하므로 미승인 초안도 통과한다. `digest`는 현재 검토 대상 식별값을 출력하며 승인을 생성하지 않는다. `check enter`는 목록의 모든 선행 단계 결과 수용·현재 구성 승인·현재 결과 보류 여부를, `check accept`는 선행 단계 수용과 현재 구성 승인·결과 수용을 검사한다. 불일치/누락은 종료 코드 1, 일치는 0이다. 이 도구는 실제 실행을 가로막는 보안 장치가 아니며 호출자가 거부 판정을 지켜야 한다.

| 필드 | 의미 |
| --- | --- |
| `schema_version`, `project` | 형식 버전 `1`, 프로젝트 식별자 |
| `stages` | 이 기록이 관리하는 단계의 실행 순서. 진입 시 선행 항목을 모두 검사 |
| `stage.id`, `stage.revision` | 단계 ID, 범위/입력 계약 revision. 범위가 바뀔 때 갱신하며 구현 commit마다 바꾸지 않음 |
| `configuration` | `version`, `agents`, `max_concurrency`, `permissions`, `cost_scope` |
| `configuration.agents[]` | `id`, `role`, `model`(요청 모델), `effort`, `ownership`(파일/책임 문자열 목록) |
| `configuration_reviews` | 실제 답변 시각 순서의 구성 검토 이력. 마지막 기록만 현재 판정에 사용 |
| `result` | 미제출은 `null`. 제출 시 `revision`, `summary`, `artifacts`, `checks`, `limitations` |
| `result_reviews` | 실제 답변 시각 순서의 결과 검토 이력. 마지막 기록만 현재 판정에 사용 |

`permissions`는 허용/금지 작업을 적은 비어 있지 않은 문자열 목록이다. `cost_scope`에는 승인된 호출/구독/비용 범위를 적는다. 구성원은 모두 명시하되 순차 작업이면 최대 동시 인원은 구성원 수보다 작을 수 있다. `artifacts`와 `checks`는 비어 있지 않은 문자열 목록이며 검사에는 대상 revision·수용 기준·명령/증거·PASS/FAIL/NOT_RUN을 적는다. `limitations`는 문자열 목록이며 없으면 빈 목록이다. 추가 요청과 선택 질문은 `summary` 또는 연결된 결과물에 보존한다.

구성/결과 검토 항목은 다음 형태다. 아래는 필드 설명용이며 실제 승인 자료가 아니다. `target`은 `digest` 출력의 현재 대상을 사용자에게 제시하고 그 대상에 대한 실제 답변을 받은 경우에만 옮긴다.

```json
{
  "decision": "approved",
  "target": {
    "stage_id": "S2",
    "stage_revision": "contract-v1",
    "configuration_version": "v1",
    "configuration_digest": "digest 명령이 출력한 SHA-256"
  },
  "source": {
    "kind": "chat",
    "reference": "실제 대화/메시지 식별자와 GitHub 전사 기록 URL",
    "at": "2026-11-08T08:43:21+09:00",
    "actor": "user",
    "recorded_by": "agent"
  },
  "response": "실제 사용자 답변 원문",
  "scope": "답변이 허용한 정확한 구성/작업 범위와 제외 대상"
}
```

구성 `decision`은 `approved`, `changes_requested`, `held`; 결과는 `accepted`, `changes_requested`, `held`다. 결과의 `target`에는 `result_revision`, `result_digest`도 필요하다. `source.kind`는 `chat` 또는 `github`, `recorded_by`는 `user` 또는 `agent`이며 `actor: user`는 사용자 답변이라는 **기록자의 주장**이다. 시각에는 시간대를 포함한다. 자동 해석으로 동의 문구를 만들거나 에이전트 의견을 사용자 답변으로 채우지 않는다.

단계 계약 또는 구성의 버전/내용이 바뀌면 구성 승인은 무효다. SHA-256은 정렬된 JSON 전체를 대상으로 하므로 버전 문자열을 그대로 둔 모델/소유권/권한/비용 변경도 감지한다. 승인 후 같은 범위의 구현 수정·실패 재현·재검증은 구성 승인을 재사용한다. 이때 `result.revision`과 해당 결과 내용을 갱신하고 결과만 다시 수용받는다. 결과 내용이 바뀌면 revision을 누락해도 기존 수용은 맞지 않는다. 결과가 `held`이면 실제 재개/수정 지시를 최신 `changes_requested`로 기록해야 같은 단계 실행을 재개할 수 있다. 이 상태는 결과 수용을 의미하지 않는다.

과거 검토 이력은 지우지 않고 새 답변을 추가한다. 구성 승인보다 오래된 결과 수용은 인정하지 않는다. 한 레코드의 순서/답변을 고의로 바꾸거나 결과 링크의 파일 내용을 바꾸면서 revision·해시를 그대로 두는 행위까지 검출하지는 않는다. 결과 revision에는 commit 또는 산출물 해시 등 검사한 내용을 식별할 수 있는 값을 사용하고, 원격 기록과 실제 파일을 별도로 대조한다.

모든 판정은 `scope: local_record_only`, `human_verified: false`, `remote_verified: false`, `model_compliance_verified: false`를 출력한다. JSON 구조·해시 일치·종료 코드 0은 사람의 승인 진위·GitHub 저장·모델 준수·제품 성공의 증명이 아니다.
