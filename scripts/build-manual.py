#!/usr/bin/env python3
"""편집 원본에서 HTML과 GitHub 읽기용 문서를 재생성한다."""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def build():
    sections = json.loads((ROOT / 'manual/sections.json').read_text())
    css = (ROOT / 'manual/style.css').read_text()
    js = (ROOT / 'manual/viewer.js').read_text()
    version = (ROOT / 'VERSION').read_text().strip()
    nav = ''.join(f'<a href="#{s["id"]}">{html.escape(s["title"])}</a>' for s in sections)
    body = ''
    markdown = f'# Gon 프로젝트 워크플로우 실행 매뉴얼\n\n버전 {version}. 편집 원본은 `manual/sections.json`입니다. 이 파일은 자동 생성합니다.\n\n'
    for i, section in enumerate(sections):
        sid = section['id']
        title = html.escape(section['title'])
        heading = 'h1' if i == 0 else 'h2'
        prev = f'<a href="#{sections[i-1]["id"]}">← 이전</a>' if i else '<span></span>'
        nxt = f'<a href="#{sections[i+1]["id"]}">다음 →</a>' if i + 1 < len(sections) else '<a href="#start">처음으로 ↑</a>'
        body += f'<section class="chapter" id="{sid}" aria-labelledby="title-{sid}"><div class="eyebrow">{html.escape(section["eyebrow"])}</div><{heading} id="title-{sid}">{title}</{heading}><p class="intro">{section["intro"]}</p>{section["body"]}<div class="chapter-footer">{prev}{nxt}</div></section>'
        text = re.sub(r'<button\b[^>]*>.*?</button>', '', section['body'], flags=re.S)
        text = re.sub(r' class="[^"]*"', '', text)
        text = text.replace('href="02-workflow-map.html"', 'href="../dist/02-workflow-map.html"')
        markdown += f'<a id="{sid}"></a>\n\n## {section["title"]}\n\n{section["intro"]}\n\n{text}\n\n'
    document = f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gon 프로젝트 워크플로우 실행 매뉴얼</title><style>{css}</style></head><body><aside class="sidebar"><p class="brand">Gon 프로젝트<br>워크플로우 매뉴얼</p><p>목표부터 실제 결과와 다음 작업까지<br>v{version}</p><nav aria-label="매뉴얼 목차">{nav}</nav><div class="small-tools"><button id="print" type="button">매뉴얼 인쇄</button><a class="download" href="01-project-workflow-manual.pdf">PDF 열기</a><a class="download" href="02-workflow-map.html" target="_blank" rel="noopener">전체 흐름도 ↗</a></div></aside><main>{body}</main><div class="toast" id="toast" role="status" aria-live="polite" hidden></div><script>{js}</script></body></html>'
    (ROOT / 'dist').mkdir(exist_ok=True)
    (ROOT / 'docs').mkdir(exist_ok=True)
    (ROOT / 'dist/01-project-workflow-manual.html').write_text(document)
    (ROOT / 'docs/01-manual.md').write_text(markdown.rstrip() + '\n')
    print(json.dumps({'sections': len(sections), 'version': version}, ensure_ascii=False))


if __name__ == '__main__':
    build()
