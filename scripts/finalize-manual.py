#!/usr/bin/env python3
"""PDF 목차와 빌드 기록, 상대 경로를 보존한 오프라인 묶음을 만든다."""
from datetime import datetime, timezone
from pathlib import Path
from planning import read_sections
from diagram_proof import check_workflow
from urllib.parse import unquote, urlsplit
import hashlib
import json
import os
import re
import subprocess
import zipfile

from pypdf import PdfReader, PdfWriter
from pypdf.generic import TextStringObject

ROOT = Path(__file__).resolve().parents[1]


def compact(text):
    return re.sub(r'\s+', '', text)


def main():
    check_workflow(ROOT)
    sections = read_sections(ROOT)
    pdf = ROOT / 'dist/01-project-workflow-manual.pdf'
    reader = PdfReader(pdf)
    page_text = [compact(page.extract_text() or '') for page in reader.pages]
    writer = PdfWriter()
    writer.append(reader, import_outline=False)
    contents = []
    previous_page = -1
    for section in sections:
        title = compact(section['title'])
        destination = reader.named_destinations.get('/' + section['id'])
        if destination is None:
            raise ValueError(f'PDF에서 장의 이동 대상을 찾지 못했습니다: {section["id"]}')
        found = reader.get_destination_page_number(destination)
        if not 0 <= found < len(page_text) or found < previous_page or title not in page_text[found]:
            raise ValueError(f'PDF 제목·페이지 순서가 맞지 않습니다: {section["title"]}')
        previous_page = found
        writer.add_outline_item(section['title'], found)
        contents.append({'id': section['id'], 'title': section['title'], 'page': found + 1})
    for page in writer.pages:
        for ref in page.get('/Annots', []):
            action = ref.get_object().get('/A')
            if action is None:
                continue
            action = action.get_object()
            uri = str(action.get('/URI', ''))
            parsed = urlsplit(uri)
            if parsed.scheme == 'file':
                target = Path(unquote(parsed.path)).resolve()
                if target.is_relative_to(ROOT):
                    relative = os.path.relpath(target, pdf.parent)
                    if parsed.fragment:
                        relative += '#' + parsed.fragment
                    action.update({'/URI': TextStringObject(relative)})
    temp = pdf.with_suffix('.tmp.pdf')
    with temp.open('wb') as handle:
        writer.write(handle)
    temp.replace(pdf)
    result = PdfReader(pdf)
    if len(result.outline) != len(sections):
        raise ValueError('PDF 목차 항목 수 불일치')
    destinations = result.named_destinations
    internal_links = 0
    for page in result.pages:
        for ref in page.get('/Annots', []):
            destination = ref.get_object().get('/Dest')
            if isinstance(destination, str):
                internal_links += 1
                if destination not in destinations:
                    raise ValueError(f'PDF 내부 링크 대상 누락: {destination}')
    evidence = ROOT / 'evidence/build.json'
    artifacts = ['dist/01-project-workflow-manual.html',
                 'dist/01-project-workflow-manual.pdf', 'dist/02-workflow-map.html',
                 'docs/01-manual.md']
    source_files = [p for folder in ['manual', 'scripts', 'diagrams']
                    for p in (ROOT / folder).iterdir() if p.is_file()]
    source_files += [ROOT / name for name in ['VERSION', 'package.json', 'package-lock.json',
                                             'requirements.txt']]
    record = {
        'version': (ROOT / 'VERSION').read_text().strip(),
        'built_at_utc': datetime.now(timezone.utc).isoformat(),
        'checks': {'pdf_pages': len(result.pages), 'bookmarks': len(result.outline),
                   'all_section_titles_found': True, 'internal_links': internal_links,
                   'named_destinations': len(destinations)},
        'scope': 'PDF 제목·목차와 파일 내용 식별. 스킬 테스트·CI·시각 품질은 별도 기록.',
        'contents': contents,
        'sources': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(source_files)},
        'artifacts': {name: {'sha256': hashlib.sha256((ROOT / name).read_bytes()).hexdigest(),
                             'bytes': (ROOT / name).stat().st_size} for name in artifacts},
    }
    evidence.parent.mkdir(exist_ok=True)
    evidence.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    output = ROOT / 'dist/gon-development-os.zip'
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    files = [ROOT / name for name in tracked if name and (ROOT / name).is_file()
             and ROOT / name != output]
    if not files:
        raise ValueError('묶음을 만들려면 Git 저장소에서 의도한 원본 파일을 먼저 추적하세요.')
    files += [ROOT / name for name in artifacts] + [evidence]
    if any(file.is_symlink() for file in files):
        raise ValueError('묶음에 심볼릭 링크를 포함하지 않습니다. 실제 원본 파일을 확인하세요.')
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
        for file in sorted(set(files)):
            bundle.write(file, file.relative_to(ROOT))
    with zipfile.ZipFile(output) as bundle:
        if bundle.testzip() is not None:
            raise ValueError('ZIP 무결성 검사 실패')
    print(json.dumps({'pdf_pages': len(result.pages), 'bookmarks': len(result.outline),
                      'zip_files': len(set(files)), 'zip_integrity': 'PASS'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
