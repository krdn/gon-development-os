# GitHub CLI/API 실행 절차

연결 도구로 필요한 기능을 수행할 수 없을 때만 읽는다. 아래는 명령 **형식**이다. 꺾쇠 변수는 실제 확인한 값으로 대체하고 현재 `gh <command> --help`로 지원 옵션을 먼저 확인한다. 새 버전 전용 옵션을 추측하지 않는다. Enterprise는 명시된 host를 유지하고 토큰 값을 조회/출력하지 않는다.

## 읽기와 대상 고정

```text
gh repo view OWNER/REPO --json nameWithOwner,url,defaultBranchRef,isPrivate,viewerPermission
gh api --hostname HOST --method GET repos/OWNER/REPO
gh issue list --repo OWNER/REPO --state all --limit N --json number,title,state,url
gh api --hostname HOST --method GET --paginate 'repos/OWNER/REPO/issues?state=all&per_page=100'
gh api --hostname HOST --method GET --paginate 'repos/OWNER/REPO/milestones?state=all&per_page=100'
gh api --hostname HOST --method GET --paginate 'repos/OWNER/REPO/labels?per_page=100'
gh project list --owner OWNER --format json --limit N
gh project view PROJECT_NUMBER --owner OWNER --format json
gh project field-list PROJECT_NUMBER --owner OWNER --format json --limit N
gh project item-list PROJECT_NUMBER --owner OWNER --format json --limit N
```

`--limit`은 전체 목록을 보장하지 않는다. totalCount와 반환 수를 대조하고, 더 있으면 `gh api graphql --paginate`의 `pageInfo {hasNextPage endCursor}`/`$endCursor` 패턴 또는 현재 API cursor를 사용한다. GraphQL을 `gh api`로 호출할 때는 JSON 요청이라 POST지만 query만 실행하며 mutation 여부를 명시적으로 확인한다. inspect 도구는 GET만 사용한다.

API 목록 조회는 `--method GET`을 명시한다. `gh api -f/-F`는 method를 지정하지 않으면 POST가 될 수 있다. Projects의 GraphQL node ID, REST issue database ID, issue 번호, Project 번호와 항목 ID는 서로 다르다.

## 이슈·라벨·Milestone과 관계

본문·댓글·PR 설명은 정확한 UTF-8 파일로 준비하고 `--body-file` 또는 API JSON `--input`을 사용한다. 변수 값을 셸 문자열에 끼워 JSON을 조립하지 않는다. 인증값을 파일/argv에 넣지 않는다.

```text
gh issue create --repo OWNER/REPO --title TITLE --body-file BODY_PATH
gh issue edit ISSUE_NUMBER --repo OWNER/REPO --body-file BODY_PATH
gh issue edit ISSUE_NUMBER --repo OWNER/REPO --add-label EXISTING_LABEL --add-assignee VERIFIED_LOGIN --milestone EXISTING_MILESTONE
gh issue view ISSUE_NUMBER --repo OWNER/REPO --json number,title,body,state,labels,assignees,milestone,url
gh label create LABEL --repo OWNER/REPO --color HEX --description DESCRIPTION
gh api --hostname HOST --method POST repos/OWNER/REPO/milestones --input MILESTONE_JSON
```

새 라벨/Milestone 생성은 전체 기존 목록을 대조한 뒤 필요한 경우에만 한다. `--force`로 기존 라벨 정의를 덮어쓰지 않는다. 담당자/리뷰 요청은 실제 담당과 권한이 정해진 경우에만 한다.

sub-issue는 현재 REST의 `issues/PARENT_NUMBER/sub_issues`에 `issue_id`를, 차단 관계는 `issues/NUMBER/dependencies/blocked_by`에 `issue_id`를 쓰는 방식이다. 호출 전 해당 host의 현재 API 문서·기존 관계·방향을 확인하고 추가 후 GET으로 재검증한다. 지원 불가면 본문 링크로 대체한다. 번호를 database ID 대신 전송하지 않는다.

## Projects 상태

```text
gh project item-add PROJECT_NUMBER --owner OWNER --url ISSUE_URL --format json
gh project item-edit --id ITEM_ID --project-id PROJECT_ID --field-id STATUS_FIELD_ID --single-select-option-id STATUS_OPTION_ID --format json
```

field-list에서 **실제** 옵션 ID를 읽는다. 예시 상태 이름을 하드코딩하지 않는다. 현재 설치된 구버전 CLI에는 이름 기반 `--field/--value`가 없을 수 있다. 항목 존재 여부를 먼저 확인하고 add 후 item-list/GraphQL로 이슈 URL·항목 ID·필드 값이 일치하는지 읽는다. automation이 덮어쓴 경우 원인을 확인하고 같은 상태 쓰기를 반복하지 않는다. 인증 확대는 자동 수행하지 않는다.

Discussions/Wiki·Project view/iteration/workflow는 연결 API 또는 현재 브라우저 도구로 처리한다. `gh discussion`이나 확장이 설치됐다고 가정하지 않는다. Wiki를 사용할 때는 별도 `.wiki.git` 저장소의 내용/원격도 확인한다. 지원되지 않으면 저장소 docs/이슈를 대체 기준으로 기록한다.

## PR·CI·릴리스·배포

```text
gh pr create --repo OWNER/REPO --base BASE --head BRANCH --draft --title TITLE --body-file BODY_PATH
gh pr view PR_NUMBER --repo OWNER/REPO --json url,body,headRefOid,state,isDraft,reviewDecision,statusCheckRollup
gh pr checks PR_NUMBER --repo OWNER/REPO
gh run view RUN_ID --repo OWNER/REPO --json headSha,status,conclusion,url
gh release create TAG --repo OWNER/REPO --verify-tag --draft --title TITLE --notes-file NOTES_PATH
gh release view TAG --repo OWNER/REPO --json tagName,isDraft,url,assets
gh api --hostname HOST --method GET 'repos/OWNER/REPO/deployments?sha=TESTED_SHA&per_page=100'
```

draft PR은 통합 전 상태다. 필요한 CI·리뷰를 확인하고 허용된 범위에서 ready/merge한다. 기록을 남길 목적으로 릴리스 발행이나 Deployment 생성을 실행하지 않는다.

태그는 실제 커밋을 확인한 뒤 생성하고 `--verify-tag`로 없는 태그의 자동 생성을 막는다. draft Release와 발행 완료를 구분한다. release asset을 덮어쓰는 `--clobber`, 보호 우회·관리자 merge·강제 push는 일반 관리 기록 절차에 포함하지 않는다. 배포 요청 생성은 실제 동작을 유발할 수 있으므로 기존 workflow가 남긴 기록을 우선 조회한다.

최종 재조회에서 요청한 body·상태·Project 필드·SHA·첨부물과 실제 결과를 대조한다. 결과를 확인할 수 없으면 해당 항목은 `pending_sync`/미검증으로 남긴다.

공식 근거: [gh api](https://cli.github.com/manual/gh_api), [Projects item edit](https://cli.github.com/manual/gh_project_item-edit), [Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).
