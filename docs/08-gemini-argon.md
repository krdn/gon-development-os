# Gemini 4 Argon 추가 선택

2026-11-07. **명시 선택용 보조 모델로 추가했다.** 긴 코드·문서 분석의 추가 후보로 검토할 수 있지만 긴 입력의 품질·시간은 이 환경에서 미검증이다. 기본 자동 후보는 Astra/Fable, 일반 작업의 effort는 medium으로 유지한다.

조사 원본은 [gon-skills의 Argon 평가](https://github.com/krdn/gon-skills/blob/main/skills/model-router/references/gemini-argon.md)다. 공식 모델 카드·평가 방법·가격·CLI 지원과 로컬 호출 결과를 구분해 정리했다.

- Google 공개 비교에서 Argon은 DeepSWE와 긴 GraphWalks에서 강점이 있지만 FrontierSWE·터미널 작업에서는 Astra·Fable·Opus 모두 앞선다. 공급자·하네스가 섞인 평가이므로 우리 작업의 전체 순위로 사용하지 않는다.
- 통합 1M 문맥과 멀티모달은 모델 사양이다. 이번 연결은 텍스트 단발 자문이며 이미지 OCR, 대형 문서, 네이티브 협업 워커는 검증하지 않았다.
- API 가격은 입력/출력 1M토큰당 $2/$10이고 2026-12-01부터 $4/$20이다. thinking도 출력 과금에 포함된다. Antigravity 구독의 실제 지출과는 별개다. [Google 가격](https://aistudio.google.com/docs/pricing)
- `agy 1.5.2`에서 low/medium/high 목록과 가상 과제의 medium 실호출 응답을 확인했다. 저장 충돌·OCR 점수 해석·독립 작업 진행에 대한 판단은 적절했다. 응답에 추론 모델별 사용량이 없어 실제 서버 모델·effort 확인 상태는 `unverified`다. 성능·속도·비용 우월성을 확정하지 않았다.

## 선택과 실행

사용자가 Argon을 선택하면 설치된 `model-router`의 `--model argon`을 사용한다. 일반 과제는 medium, 단순·저위험은 low, 복잡·고영향은 high로 연결한다. 정확한 CLI ID는 `gemini-4-argon-low|medium|high`이며 Gemini API의 `gemini-4-argon`과 구분한다.

```text
$model-router Argon으로 첨부한 설계의 문제점을 분석해줘. 일반 난이도·보통 영향이며,
파일 수정 없이 주어진 자료만 사용하고 근거와 미확인 범위를 구분해줘.
```

기존 `gemini` 별칭은 과거 `gemini-3.1-pro-high`를 유지한다. `argon`을 명시해야 새 모델이 선택된다. 사용자 미지정, 다른 제공자 할당량 소진, UI 작업이라는 이유만으로 자동 선택하지 않는다. 명시 모델·effort 충돌과 실행 실패 시 대체하지 않으며, 기본 외부 리뷰는 기존 중앙 정책을 따른다.

기존 스킬 동기화기로 원본·설치본을 맞춘다. 이 매뉴얼은 두 전문 스킬만 오프라인 포함하므로 model-router를 별도로 복사하지 않는다. 다음 자동 후보 확대 판단은 동일 입력·하네스의 반복 과제에서 정확도, 총시간, 사용량을 비교한 뒤 수행한다.

현재 라우터 기본 제한은 300초다. 장시간 과제는 시작 전에 허용 시간을 정하고 `--timeout`으로 전달한다. 시간 초과 뒤 자동 재시도·대체는 하지 않는다.
