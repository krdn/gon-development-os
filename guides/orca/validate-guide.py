#!/usr/bin/env python3
"""로컬 링크와 PDF의 요청문·단계 내용 보존을 확인한다."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import subprocess
import unicodedata

ROOT=Path(__file__).resolve().parent
class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag in ('a','link') and 'href' in a:self.links.append(a['href'])
        if tag in ('script','img') and 'src' in a:self.links.append(a['src'])

def norm(text):
    return re.sub(r'\s+','',unicodedata.normalize('NFKC',text)).replace('\u00ad','')

parser=argparse.ArgumentParser();parser.add_argument('--pdf',action='store_true');args=parser.parse_args()
link_count=0
for name in ['index.html','examples.html']:
    p=ROOT/name;doc=Links();doc.feed(p.read_text())
    assert len(doc.ids)==len(set(doc.ids)),name
    for link in doc.links:
        u=urlsplit(link)
        if u.scheme:continue
        if not u.path:
            assert u.fragment in doc.ids,(name,link)
        else:
            assert (p.parent/unquote(u.path)).is_file(),(name,link)
        link_count+=1
for p in list((ROOT/'example-project').rglob('*.md'))+list((ROOT/'templates').rglob('*.md')):
    for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if '://' in link:continue
        assert (p.parent/link.split('#')[0]).is_file(),(p,link)
        link_count+=1
steps=json.loads((ROOT/'steps.json').read_text());assert len(steps)==13
assert 'Herdr' not in (ROOT/'steps.json').read_text()
assert len(list((ROOT/'templates').rglob('*.md')))==8
record={'date':datetime.now(timezone.utc).date().isoformat(),'local_links':link_count,'steps':len(steps),'templates':8}
if args.pdf:
    result=subprocess.run(['pdftotext','-layout',str(ROOT/'guide.pdf'),'-'],capture_output=True,text=True,check=True)
    pages=result.stdout.split('\f');pages=[p for p in pages if p.strip()]
    cleaned='\n'.join(line for line in result.stdout.splitlines() if not re.search(r'Gon · Orca \+ Codex CLI · \d+ / \d+',line))
    text=norm(cleaned)
    prompts=json.loads((ROOT/'rendered-prompts.json').read_text())
    for i,prompt in enumerate(prompts):
        assert norm(prompt) in text,('PDF 요청문 누락',i,prompt[:100])
    checked=0
    for s in steps:
        for value in [s['title'],s['goal'],s['session'],s['where'],*s['actions'],*s['checks'],s['fail'],s['next']]:
            assert norm(value) in text,('PDF 단계 내용 누락',s['id'],value[:70])
            checked+=1
    record['pdf']={'pages':len(pages),'complete_copy_boxes':len(prompts),'complete_stage_items':checked,'sha256':hashlib.sha256((ROOT/'guide.pdf').read_bytes()).hexdigest()}
    (ROOT/'pdf-validation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(record,ensure_ascii=False))
