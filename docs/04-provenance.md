# 자료 출처와 검증 범위

기준일: 2026-10-31. 이 저장소는 「사용법」 프로젝트에서 작성한 개발 방식과 스킬, 실행 매뉴얼을 계속 수정할 수 있도록 통합한 기록입니다.

## 포함한 자료

- 현재 매뉴얼: 20개 장, 개발 10단계, 요청문 19개. `manual/`에서 편집합니다.
- 두 설치 스킬의 원문·참조·생성기·테스트·문서 틀. 최초 가져온 내용의 SHA-256은 `evidence/imported-skills.json`에 있습니다.
- Archify 흐름도 JSON 원본, 상호작용 HTML과 당시 검증·화면 캡처.
- 최초 21쪽 PDF, HTML, ZIP, 검증 기록, 목차, 미리보기 이미지와 당시 생성 스크립트.
- 관련 대화의 사용자 요청과 작성 답변 조회본 5개. 도구 실행 로그와 인증값은 수록하지 않습니다.

## 원본 대화 읽기

1. [ChatGPT·Codex·Work 비교](../archive/2026-10-31/conversations/01-guide.md)
2. [개발 워크플로우 정리](../archive/2026-10-31/conversations/02-workflow.md)
3. [표준 확인 경로와 구성 제안](../archive/2026-10-31/conversations/03-standard.md)
4. [스킬 생성과 이동](../archive/2026-10-31/conversations/04-skill-created.md)
5. [스킬 저장 위치 설명](../archive/2026-10-31/conversations/05-skill-location.md)

긴 비교 Guide 답변의 끝부분은 원본 조회 길이 제한으로 일부 생략됐습니다. 조회 가능한 기록 전체를 보존하되, 원본 채팅 전체의 무손실 백업이라고 주장하지 않습니다. 과거 답변의 내부 인용 표기나 개인 PC 경로는 당시 기록 그대로이며 GitHub에서 접근할 수 없는 항목이 있습니다. 현재 실행 지침은 README·현재 매뉴얼과 [gon-skills 원본](https://github.com/krdn/gon-skills)을 따릅니다. 동봉된 스킬 버전은 [skills.lock](../skills.lock)에 있습니다.

## 검증을 해석하는 방법

| 기록 | 증명하는 범위 | 증명하지 않는 범위 |
| --- | --- | --- |
| `archive/2026-10-31/gon-project-lifecycle-verification.json` | 당시 스킬 테스트·리뷰·CLI 로더·이동 확인 | 이후 변경·다른 환경의 성공 |
| `archive/2026-10-31/workflow-manual/verification.json` | 최초 HTML·PDF·링크·화면 검사 | 모든 원본 대화 수록·제품 운영 배포 |
| `evidence/imported-skills.json` | 가져온 스킬 파일의 내용 식별 | 이후 수정본 또는 설치본의 동일성 |
| `evidence/build.json` | 해당 빌드의 파일 해시·PDF 목차·장 수 | 외부 링크 현재 내용·시각 품질 전체 |
| GitHub Actions 실행 기록 | 해당 커밋의 원격 빌드·테스트 | 개인 스킬 설치·실제 사용자 프로젝트 배포 |

기존 `ai-engineering-os`는 별도 저장소입니다. 해당 보일러플레이트의 원문은 복제하지 않고 매뉴얼과 스킬에서 관련 문서·확인 커밋을 참조합니다. 초기 제안에 나온 추가 전문 스킬·플러그인 패키지는 아직 구현된 것으로 표시하지 않습니다.

보관본에는 개인 PC의 기존 경로와 당시 생성 정보가 있어 비공개 저장소로 시작합니다. 공개가 필요하면 대화·경로·기록·권리 관계를 확인하는 별도 작업으로 진행합니다. 새 작업의 비밀번호·토큰·개인 계정 자료를 이 기록에 추가하지 않습니다.
