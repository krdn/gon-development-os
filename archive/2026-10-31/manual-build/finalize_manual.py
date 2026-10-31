from pathlib import Path
from html.parser import HTMLParser
from pypdf import PdfReader, PdfWriter
import json, re, hashlib, zipfile

ROOT=Path('/home/gon/문서/ChatGPT/사용법')
OUT=ROOT/'workflow-manual'
pdf=OUT/'01-project-workflow-manual.pdf'
sections=json.loads((OUT/'manual-content.json').read_text())
r=PdfReader(pdf)
texts=[re.sub(r'\s+','',p.extract_text() or '') for p in r.pages]
w=PdfWriter();w.clone_document_from_reader(r)
bookmarks=[]
for s in sections:
    key=re.sub(r'\s+','',s['title'])
    hits=[i for i,t in enumerate(texts) if key in t]
    if not hits:raise ValueError('Missing heading '+s['title'])
    w.add_outline_item(s['title'],hits[0]);bookmarks.append({'title':s['title'],'page':hits[0]+1})
w.add_metadata({'/Title':'Gon 프로젝트 워크플로우 실행 매뉴얼','/Subject':'기획, 구현, 검증, 배포와 재개를 잇는 10단계 매뉴얼'})
tmp=OUT/'manual-bookmarked.pdf'
with tmp.open('wb') as f:w.write(f)
tmp.replace(pdf)
(OUT/'pdf-contents.json').write_text(json.dumps(bookmarks,ensure_ascii=False,indent=2))

class Links(HTMLParser):
    def __init__(self):super().__init__();self.ids=set();self.hrefs=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        if tag=='a' and 'href' in a:self.hrefs.append(a['href'])
parser=Links();parser.feed((OUT/'01-project-workflow-manual.html').read_text())
broken=[]
for h in parser.hrefs:
    if h.startswith('#'):
        if h[1:] not in parser.ids:broken.append(h)
    elif not h.startswith(('http:','https:')):
        p=Path(h) if h.startswith('/') else OUT/h
        if not p.exists():broken.append(h)
assert not broken,broken

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
arch=ROOT/'.archify/workflow-gon-manual-20261031-202000'
assert sha(arch/'workflow-map.html')==sha(OUT/'02-workflow-map.html')
old=json.loads((ROOT/'gon-project-lifecycle-verification.json').read_text())
assert all(sha(Path('/home/gon/.agents/skills/gon-project-lifecycle')/k)==v for k,v in old['sha256'].items())
receipt={
    'date':'2026-10-31','title':'Gon 프로젝트 워크플로우 실행 매뉴얼',
    'sections':len(sections),'steps':10,'prompt_blocks':19,'pdf_pages':len(r.pages),'pdf_bookmarks':len(bookmarks),
    'checks':{'internal_and_local_links':'PASS','pdf_all_section_headings':'PASS','pdf_page_size':'A4','pdf_visual_inspection':'대표 페이지 및 전체 페이지 배치 확인','html_desktop_width':1440,'html_mobile_width':390,'horizontal_page_overflow':False,'prompt_copy':'실제 클릭 복사 성공 및 선택 복사 대체 동작 확인','navigation':'목차와 단계 링크 확인','a11y_automated_violations':0,'a11y_incomplete':'화살표 3개의 대비 자동 판정 보류; 화면 확인','diagram_finalize':'validate/deliver/check/browser-check PASS','diagram_visual_inspection':'1440x900 밝은 테마와 연결·실패 복귀선 확인','diagram_copy_hash_matches':True,'skill_receipt_hashes_match':'14/14'},
    'sources':{'project_chats':['1.ChatGPT Codex Work 비교 Guide','2.개발 워크플로우 정리','3.Gon AI Development OS 표준 확인 경로 찾기','gon-project-lifecycle 스킬 생성','스킬 저장 위치가 다른 이유 찾기'],'local_skill':str(Path('/home/gon/.agents/skills/gon-project-lifecycle/SKILL.md')),'local_web_skill':'/home/gon/.agents/skills/gon-web-engineering/SKILL.md','prior_verification':str(ROOT/'gon-project-lifecycle-verification.json'),'official_docs':['https://learn.chatgpt.com/docs/skills-and-plugins','https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills','https://learn.chatgpt.com/guides/best-practices#use-scheduled-tasks-for-repeated-work']},
    'limits':['긴 비교 Guide 대화의 끝부분은 조회 도구 길이 제한으로 일부 생략됨. 현재 스킬 원문으로 실행 절차를 대조함.','기존 스킬 테스트 20개는 이전 검증 기록의 결과이며 이번 작업에서 전체 재실행하지 않음.','실제 새 제품의 전체 수명주기와 운영 배포를 이번 매뉴얼 작업에서 수행한 것은 아님.'],
    'artifacts':{n:{'sha256':sha(OUT/n),'bytes':(OUT/n).stat().st_size} for n in ['01-project-workflow-manual.html','01-project-workflow-manual.pdf','02-workflow-map.html']}
}
(OUT/'verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
with zipfile.ZipFile(OUT/'gon-project-workflow-manual.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
    for n in ['01-project-workflow-manual.html','01-project-workflow-manual.pdf','02-workflow-map.html','verification.json','pdf-contents.json']:
        z.write(OUT/n,n)
    z.write(arch/'workflow-map.finalize-summary.json','diagram-finalize-summary.json')
print(json.dumps({'pdf_pages':len(r.pages),'sections':len(sections),'prompts':19,'links_checked':len(parser.hrefs),'broken_links':broken,'zip_integrity':zipfile.ZipFile(OUT/'gon-project-workflow-manual.zip').testzip()},ensure_ascii=False))
