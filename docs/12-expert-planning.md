# 프로젝트별 전문가 설계와 P1~P5 협업

새 아이디어의 문제·제약에 맞는 전문가를 설계하고, 별도 리뷰어가 명세와 실제 답변을 확인한 뒤 협업에 투입한다. “상위 0.1%”는 높은 전문성을 지향하는 목표다. 역할 문구나 내부 점수를 외부 백분위 인증으로 사용하지 않는다.

## 실행 흐름

1. P1의 실제 사용자 답변에서 문제·제약·미정을 확인한다.
2. 총괄이 전문 분야·담당 질문·역량·방법·자료·도구·산출물 명세를 작성한다.
3. 리뷰어 실행·후보 평가·합격 후 본 조사의 구성과 한도를 기존 승인·위임에 연결한다.
4. 별도 리뷰어가 명세를 검토하고 후보가 고정된 실무 과제를 수행한다.
5. 현재 구성에 유효한 합격 역할이 P3 조사와 P4 반론·응답에 참여한다.
6. P5에서 결과를 독립 검토하고 요구·AC·첫 작업을 개발 세션에 인계한다.

총괄도 검토 대상이다. 리뷰어는 오류와 기대 판정이 알려진 과제로 확인한다. 주 모델 외 실행·대기 중 세션 상한 2명을 유지하고 역할을 교대로 투입한다. 모든 프로젝트에 같은 고정 팀을 만들지 않는다. 사용자가 단독 기획을 선택했거나 기존 위임이 명확히 허용하면 A가 직접 조사하고 선발 not_applicable 근거를 STATE에 남긴다. 실패한 선발을 피하려고 임의로 전환하지 않으며 독립 자격을 받은 것으로 쓰지 않는다.

정상·모호·상충 근거의 3종 과제와 핵심 과제의 새 세션 재실행을 사용한다. 각 결과의 90/100 이상·항목별 4/5 이상·치명적 실패 0건을 확인한다. 이는 운영 기준이며 측정된 성능이 아니다. 출처 조작·사용자 결정 날조·미실행 PASS·허용 밖 수정은 탈락이다. 도구 실패·평가 자료 오류도 별도로 확인한다.

실행 중인 에이전트는 [실행 계약](../templates/herdr-project/HERDR-PROJECT.md), [명세·평가·협의 절차](../templates/herdr-project/HERDR-OPERATIONS.md), [TEAM 양식](../templates/herdr-project/docs/ai/TEAM.md)을 사용한다. 기존 동등 문서와 유효한 평가는 재사용한다. 작은 수정·명확한 기존 작업에는 선발을 새로 붙이지 않는다.

## GitHub 연구와 선택 이유

확인일은 2026-11-09다. 공식 저장소 README·관련 소스·메타데이터를 조사했다. 아래 비교는 소스에서 확인한 구조와 현재 Herdr 계약을 결합한 설계 판단이다. 프레임워크 설치·실행·성능 비교 결과가 아니다.

| 프로젝트 | 확인한 구현 | 적용한 패턴과 보완 |
| --- | --- | --- |
| AutoAgent | Agent Former가 목적·입출력·도구·지침 명세를 만들고 Creator가 생성·조정한다. | 실행 전에 명세 작성. 별도 설계 리뷰·분야 실무 평가를 추가한다. |
| GPT Researcher | 주제별 역할 생성과 조사·리뷰·수정·보고서 출력 흐름이 있다. | 조사·검토·최종 작성의 책임을 분리한다. |
| MetaGPT | 고정 역할의 PRD·시스템 설계, 메시지 전달·문서 의존 관계가 있다. | 필요한 역할·문서만 골라 입력·출력을 연결한다. |
| CrewAI | 역할·목표·도구와 Task의 기대 출력·선행 context·파일·검토 필드가 있다. | 전문가 명세와 과제 계약을 구분한다. 필드 존재를 역량 증명으로 쓰지 않는다. |
| Microsoft Agent Framework | 전문가·검증자·명료화·반론 역할의 실제 그룹 대화와 종료 조건을 제공한다. | 실제 반론·응답·수정을 회수한다. 대화 종료와 합의를 구분한다. |

코드 근거:

- AutoAgent: [명세 생성](https://github.com/HKUDS/AutoAgent/blob/16c12b052ef2330a198063c62a07a7f9723031e3/autoagent/agents/meta_agent/agent_former.py), [생성·실행](https://github.com/HKUDS/AutoAgent/blob/16c12b052ef2330a198063c62a07a7f9723031e3/autoagent/agents/meta_agent/agent_creator.py).
- GPT Researcher: [역할 생성](https://github.com/assafelovic/gpt-researcher/blob/597a99e2ef879606229754ec0d575a89eb587464/gpt_researcher/actions/agent_creator.py), [조사·리뷰 그래프](https://github.com/assafelovic/gpt-researcher/blob/597a99e2ef879606229754ec0d575a89eb587464/multi_agents/agents/editor.py), [파일 출력](https://github.com/assafelovic/gpt-researcher/blob/597a99e2ef879606229754ec0d575a89eb587464/multi_agents/agents/publisher.py).
- MetaGPT: [팀 구성](https://github.com/FoundationAgents/MetaGPT/blob/11cdf466d042aece04fc6cfd13b28e1a70341b1f/metagpt/software_company.py), [메시지 전달](https://github.com/FoundationAgents/MetaGPT/blob/11cdf466d042aece04fc6cfd13b28e1a70341b1f/metagpt/environment/base_env.py), [PRD 출력](https://github.com/FoundationAgents/MetaGPT/blob/11cdf466d042aece04fc6cfd13b28e1a70341b1f/metagpt/actions/write_prd.py).
- CrewAI: [에이전트 속성](https://github.com/crewAIInc/crewAI/blob/83d7407aa50b94d5b9f110c10ca295d3e0f360ee/docs/edge/en/concepts/agents.mdx), [Task 계약](https://github.com/crewAIInc/crewAI/blob/83d7407aa50b94d5b9f110c10ca295d3e0f360ee/lib/crewai/src/crewai/task.py).
- Microsoft Agent Framework: [그룹 대화](https://github.com/microsoft/agent-framework/blob/13956ad8c0c52538dc8fb5abae549019fbf2dc83/python/samples/03-workflows/orchestrations/group_chat_simple_selector.py), [사용자 계획 검토](https://github.com/microsoft/agent-framework/blob/13956ad8c0c52538dc8fb5abae549019fbf2dc83/python/samples/03-workflows/orchestrations/magentic_human_plan_review.py).

GPT Researcher에는 수정 한도 초과를 `accept`로 라우팅하는 경로가 있다. 반복 종료 정책을 품질 통과·사용자 수용과 같은 뜻으로 사용하지 않는다. 이 실행 계약은 한도 도달을 `unresolved`로 남긴다. [해당 코드](https://github.com/assafelovic/gpt-researcher/blob/597a99e2ef879606229754ec0d575a89eb587464/multi_agents/agents/editor.py#L151-L164)

AutoAgent·MetaGPT의 조사 시점 최근 push는 각각 2025-10-16·2026-01-21이었다. GPT Researcher·CrewAI·Microsoft Agent Framework는 2026-11-09 push를 확인했다. 이는 릴리스·운영 품질의 증거가 아니다. AutoGen README는 유지 종료와 Agent Framework 이동을 안내하므로 후속 프로젝트를 조사했다. [AutoAgent 메타데이터](https://api.github.com/repos/HKUDS/AutoAgent), [MetaGPT 메타데이터](https://api.github.com/repos/FoundationAgents/MetaGPT), [AutoGen 안내](https://github.com/microsoft/autogen/blob/main/README.md)

현재 Herdr의 탭·분할 터미널·명시적 메시지 전달·결과 파일을 재사용한다. 별도 런타임 편입은 모델 호출·상태·인증·화면 경로를 추가한다. 기존 방식의 실제 시험에서 부족함이 확인될 때 프레임워크 편입을 다시 판단한다.

## 분야별 구성 예

| 아이디어 | 필요한 역량 | 대표 평가와 산출물 |
| --- | --- | --- |
| 수학 시험지 OCR·편집 문서 | 수식 구조·읽기 순서 평가, 문서 형식·편집성 | 대표 이미지와 독립 정답 비교, 누락·수식 구조·편집성 검사 계획 |
| 개인용 오프라인 할 일 앱 | 사용자 흐름·브라우저 저장·데이터 유실 조건 | 새로고침·중복·빈값·저장 실패 기준, 사용자 흐름·R/AC·첫 작업 |

예시는 구성을 설명한다. 실제 사용자의 선택·수요·제품 성능·평가 성공을 뜻하지 않는다. 두 아이디어에 같은 전문 분야·평가 입력을 그대로 붙이지 않는다.

## 확인할 완료 조건

- 현재 명세 버전의 독립 검토·실무 결과·구성 승인 또는 위임이 연결된다.
- 상대의 실제 주장을 읽고 반론·응답·수정한 결과를 회수한다.
- 근거 부족·한도 도달을 합격·합의로 전환하지 않는다.
- Q → S/U → D → R → AC → 첫 작업이 최종 문서에 연결된다.
- 새 개발 세션이 문서를 읽고 첫 작업·검사를 회신한다.

이 기능은 모델이 읽는 실행 계약이다. Herdr 명령 자체에 자격 차단 장치를 설치하지 않는다. 문서·구조 검사와 실제 모델 준수·전문성 평가를 구분한다. 현재 검증 결과와 한계는 [실행 양식 검증 범위](../templates/herdr-project/VERIFICATION.md)에서 확인한다.
