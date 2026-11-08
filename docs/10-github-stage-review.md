# GitHub 기록과 단계별 사용자 검토

각 실제 단계에서 **구성 승인 → 실행·협의 → 결과 검토 → 추가 요청 반영·재검증 → 사용자 수용**을 진행합니다. 현재 결과와 다음 구성을 함께 검토할 수 있습니다. 작은 수정에는 새 단계를 만들지 않습니다.

| 검토 대상 | 사용자에게 보여줄 것 | 변경되면 |
| --- | --- | --- |
| 에이전트 구성 | 단계 계약 revision·구성 버전, 역할·모델/effort·소유권·동시 인원·권한·비용 | 구성 재검토 |
| 단계 결과 | 산출물 revision·링크, AC별 검사, 미검증·미결정과 다음 구성 | 수정·재검사 후 결과 재검토 |
| 사용자 답변 | 실제 답변, 출처·시각·대상과 승인 범위 | 새 답변을 덧붙여 이전 판단 보존 |

계약 revision은 범위·입력 계약이 바뀔 때 갱신합니다. 같은 계약·구성으로 구현을 수정할 때는 결과 revision만 갱신합니다. 수정 요청은 같은 단계 이슈에서 추적하고, 보류된 단계나 미수용 결과에 의존하는 다음 단계는 실행하지 않습니다.

[실행 계약](../templates/herdr-project/HERDR-PROJECT.md)과 [기록 양식](../templates/herdr-project/HERDR-OPERATIONS.md)을 사용하세요. 설치된 lifecycle의 [단계 검토 지침](../skills/gon-project-lifecycle/references/stage-review.md)과 `scripts/stage_review.py`가 JSON 구조·전환 조건을 검사합니다. 사람이 답했는지, 답변이 올바르게 옮겨졌는지, GitHub에 저장됐는지는 별도로 확인해야 합니다. 같은 계정으로 AI도 GitHub를 조작하므로 계정 이름·CI만으로 인간 승인을 증명할 수 없습니다.

```sh
python3 skills/gon-project-lifecycle/scripts/stage_review.py template --project my-project --stage S1 --stage S2
python3 skills/gon-project-lifecycle/scripts/stage_review.py validate --file docs/stage-review.json
python3 skills/gon-project-lifecycle/scripts/stage_review.py check --file docs/stage-review.json --stage S2 --action enter
```

템플릿은 승인받기 전의 초안입니다. 실제 답변 없이 승인 필드를 채우지 않습니다. 검토 요청용 이슈 양식도 승인을 생성하지 않습니다.

협의는 Discussion에 라운드·실제 참여자·입력 revision·제안·반론·근거·미해결·조정 결론을 남깁니다. 실행할 일은 Issues, 확정 결정은 저장소 ADR, 변경은 PR, 검사는 Actions에 연결합니다. 내부 추론 원문과 비밀값은 저장하지 않습니다. 원격을 다시 읽고 내용·상태·ID·revision이 맞을 때만 저장 완료로 보고합니다.

이번 적용은 [상위 이슈 #9](https://github.com/krdn/gon-development-os/issues/9), [설계·협의 #10](https://github.com/krdn/gon-development-os/discussions/10), [S2 #11](https://github.com/krdn/gon-development-os/issues/11), [Project #18](https://github.com/users/krdn/projects/18)에 연결됩니다. 사용자는 2026-11-08 S1 설계와 S2 구성 v1만 승인했습니다. S3 검증·Opus 리뷰 및 S4 통합은 해당 단계의 사용자 검토를 기다립니다.

기능별 실제 사용·예정·불가·해당 없음과 한계는 [저장소 관리 기록](../.github/project-management.md)에 있습니다. 이 문서·양식이 브랜치에 저장된 상태와 기본 브랜치 적용·설치 완료를 구분합니다.
