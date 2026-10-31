const toast = document.getElementById('toast');
function showToast(text) { toast.textContent=text; toast.hidden=false; clearTimeout(window.toastTimer); window.toastTimer=setTimeout(()=>toast.hidden=true,2400); }
document.querySelectorAll('.copy').forEach(btn=>btn.addEventListener('click',async()=>{
  const text=btn.closest('.prompt').querySelector('pre').textContent;
  try { await navigator.clipboard.writeText(text); showToast('요청문을 복사했습니다.'); }
  catch { const pre=btn.closest('.prompt').querySelector('pre'); const range=document.createRange(); range.selectNodeContents(pre); const selection=window.getSelection(); selection.removeAllRanges(); selection.addRange(range); showToast('요청문을 선택했습니다. Ctrl+C로 복사하세요.'); }
}));
document.getElementById('print').addEventListener('click',()=>window.print());
const observer=new IntersectionObserver(entries=>{for(const e of entries){if(e.isIntersecting){document.querySelectorAll('nav a').forEach(a=>a.setAttribute('aria-current',String(a.hash==='#'+e.target.id)));}}},{rootMargin:'-5% 0px -70% 0px',threshold:0});
document.querySelectorAll('.chapter').forEach(s=>observer.observe(s));
