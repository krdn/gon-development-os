#!/usr/bin/env python3
"""Create missing project guidance files; preserve and report existing content."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import sys
from pathlib import Path

TOPICS = {
    "architecture": "신규 프로젝트·기술 선택·공통 구조",
    "frontend": "React·TypeScript·UI·라우팅·브라우저 SDK",
    "backend-data": "Rust 서버·인증·API·DB·SQL·마이그레이션",
    "verification": "코드 변경·버그 분석·검증·업그레이드",
}


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def inspect_destination(root: Path, relative: str) -> Path:
    """Reject symlinks and invalid ancestors without creating anything."""
    parts = Path(relative).parts
    if not parts or Path(relative).is_absolute() or ".." in parts:
        raise ValueError(f"Invalid relative destination: {relative}")
    current = root
    for index, part in enumerate(parts):
        current = current / part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode):
            raise ValueError(f"Symlink destination is not supported: {relative}")
        if index < len(parts) - 1:
            if not stat.S_ISDIR(mode):
                raise ValueError(f"Destination parent is not a directory: {relative}")
        elif not stat.S_ISREG(mode):
            raise ValueError(f"Destination is not a regular file: {relative}")
    return current


def agents_content(topics: list[str]) -> bytes:
    rows = "\n".join(
        f"| {TOPICS[topic]} | `docs/ai/{topic}.md` |" for topic in topics
    )
    text = f"""# 프로젝트 개발 안내

- 설계·수정 전에 `docs/ai/project-context.md`의 확인된 결정과 관련 기존 지침을 읽는다.
- 현재 사용자의 요구와 프로젝트의 확정된 기술·계약·운영 제약을 따른다.
- 신규 프로젝트 기본안을 기존 프로젝트의 기술 교체 근거로 사용하지 않는다.
- 아래 경로는 이 파일이 있는 프로젝트 루트 기준이다.

## 필요한 상세 지침

| 작업 | 읽을 문서 |
| --- | --- |
{rows}

- 관련 작업을 시작하기 전에 해당 문서만 읽는다. 여러 영역이면 필요한 문서를 함께 읽는다.
- 관련 없는 문서를 일괄 로딩하지 않는다. 단순 문서 오타는 대상 문서만 확인한다.
- 필요한 지침이 현재 문맥에 있고 바뀌지 않았다면 재사용한다.
- 누락된 경로는 이동 여부를 확인하고, 해결되지 않으면 누락 사실을 알린다.
- 실행 명령은 README·매니페스트·CI에서 확인하고 검증 결과를 사실대로 보고한다.
"""
    return text.encode("utf-8")


def context_content(topics: list[str], sources: dict[str, bytes]) -> bytes:
    text = """# 프로젝트 결정과 실행 정보

상태: 초기 안내만 생성됨. 아래 내용은 실제 프로젝트를 확인한 뒤 기록한다.
스킬의 기본안이나 생성한 문서만으로 프로젝트의 기술·검증 결과가 확정되지는 않는다.

## 확인한 기술과 선택 이유

- 프런트엔드·렌더링: 미기록
- 백엔드: 미기록
- 데이터 저장소: 미기록
- 선택 이유와 기존 시스템 제약: 미기록

## 버전 확인 위치

매니페스트·잠금 파일·툴체인 등 실제 파일 위치: 미기록

## 실제 실행 명령

설치·개발 실행·빌드·타입 검사·테스트·API 생성 명령: 미기록
존재하지 않는 명령이나 실행하지 않은 결과를 작성하지 않는다.

## 계약과 운영 제약

인증·권한·API 호환성·마이그레이션·배포 제약: 미기록

## 적용한 공통 문서

초기 출처: gon-web-engineering. 이 프로젝트에 복사된 내용은 프로젝트에서 관리한다.
"""
    text += "\n".join(
        f"- `docs/ai/{topic}.md` — 초기 원본 SHA-256: `{hashlib.sha256(sources[topic]).hexdigest()}`"
        for topic in topics
    ) + "\n"
    return text.encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    result = {"status": "error", "files": [], "review_required": []}
    try:
        parser = Parser(description=__doc__)
        parser.add_argument("--project", required=True, help="Existing project directory")
        parser.add_argument("--topics", nargs="+", choices=TOPICS, required=True)
        parser.add_argument("--apply", action="store_true", help="Create missing files")
        args = parser.parse_args(argv)
        supplied_root = Path(args.project).expanduser()
        if supplied_root.is_symlink():
            raise ValueError("The project root must not be a symlink")
        root = supplied_root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("The project root must be an existing directory")
        if root == Path(root.anchor) or root == Path.home().resolve():
            raise ValueError("Choose a project directory, not a filesystem root or home")
        topics = list(dict.fromkeys(args.topics))
        result.update(
            mode="apply" if args.apply else "plan", project=str(root), topics=topics
        )
        skill_root = Path(__file__).resolve().parent.parent
        sources = {
            topic: (skill_root / "references" / f"{topic}.md").read_bytes()
            for topic in topics
        }
        contents = {
            "AGENTS.md": agents_content(topics),
            "docs/ai/project-context.md": context_content(topics, sources),
            **{f"docs/ai/{topic}.md": sources[topic] for topic in topics},
        }

        root_claude = inspect_destination(root, "CLAUDE.md")
        nested_claude = inspect_destination(root, ".claude/CLAUDE.md")
        if nested_claude.exists():
            result["review_required"].append({
                "path": ".claude/CLAUDE.md",
                "reason": "Preserved existing entry; review merging @../AGENTS.md.",
            })
        if root_claude.exists() or not nested_claude.exists():
            contents["CLAUDE.md"] = b"@AGENTS.md\n"
        override = inspect_destination(root, "AGENTS.override.md")
        if override.exists():
            result["review_required"].append({
                "path": "AGENTS.override.md",
                "reason": "An override may take precedence; review active guidance.",
            })

        # Complete the preflight before creating any directory or file.
        for relative, proposed in contents.items():
            destination = inspect_destination(root, relative)
            if destination.exists():
                action = "unchanged" if destination.read_bytes() == proposed else "preserved"
            else:
                action = "create"
            result["files"].append({"path": relative, "action": action})
            if action == "preserved":
                result["review_required"].append({
                    "path": relative,
                    "reason": "Existing content differs; read and merge only if appropriate.",
                })

        if args.apply:
            for record in result["files"]:
                if record["action"] != "create":
                    continue
                relative = record["path"]
                destination = inspect_destination(root, relative)
                destination.parent.mkdir(parents=True, exist_ok=True)
                inspect_destination(root, relative)
                try:
                    with destination.open("xb") as handle:
                        handle.write(contents[relative])
                    record["action"] = "created"
                except FileExistsError:
                    record["action"] = "preserved"
                    result["review_required"].append({
                        "path": relative,
                        "reason": "A file appeared after planning; it was not overwritten.",
                    })
        result["status"] = "applied" if args.apply else "planned"
        result["next_step"] = (
            "Read review_required entries, merge necessary guidance, and record "
            "verified project decisions and commands in docs/ai/project-context.md."
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        result["error"] = str(exc)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
