# 스킬 저장 위치가 다른 이유 찾기

2026-10-31 조회 보관본. 과거 제안·경로·지원 정보는 당시 기록이며 현재 실행 지침이 아닙니다. 긴 응답의 생략은 표시합니다. 도구 출력·인증 정보는 포함하지 않습니다.

## 사용자 요청

gon-project-lifecycle , gon-web-engineering 스킬 저장위치가 다른이유가 뭐야


## 작성된 답변

**기능상 구분이 아니라, 만들 때 적용한 저장 경로 기준이 달랐기 때문입니다.**

| 스킬 | 실제 저장 위치 |
|---|---|
| gon-project-lifecycle | [/home/gon/.codex/skills/gon-project-lifecycle](/home/gon/.codex/skills/gon-project-lifecycle/SKILL.md) |
| gon-web-engineering | [/home/gon/.agents/skills/gon-web-engineering](/home/gon/.agents/skills/gon-web-engineering/SKILL.md) |

`gon-project-lifecycle`은 앞선 생성 작업에서 **설치된 `skill-creator`의 기본 지침**인 `$CODEX_HOME/skills`를 따랐습니다. 현재 `CODEX_HOME`이 지정되지 않아 `~/.codex/skills`에 생성됐습니다. [해당 지침](/home/gon/.codex/skills/.system/skill-creator/SKILL.md:151)

반면 `gon-web-engineering`이 있는 **`~/.agents/skills`는 현재 공식 문서에서 안내하는 개인 스킬 경로**입니다. [OpenAI 공식 문서](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

즉, **설치된 생성 도구의 기본값과 공식 안내 경로가 달라 일관되지 않게 배치된 상태**입니다. 현재 세션에서는 둘 다 인식됩니다. 두 스킬의 역할 때문에 경로를 나눌 필요는 없고, 개인 스킬 관리 기준은 `~/.agents/skills`로 통일하는 편이 명확합니다.

