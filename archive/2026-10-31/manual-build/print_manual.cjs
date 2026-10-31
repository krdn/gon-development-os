const { chromium } = require('/home/gon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const { pathToFileURL } = require('node:url');
const path = require('node:path');
(async () => {
  const browser = await chromium.launch({executablePath:'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:1000}});
    const root = '/home/gon/문서/ChatGPT/사용법/workflow-manual';
    await page.goto(pathToFileURL(path.join(root,'01-project-workflow-manual.html')).href);
    await page.evaluate(()=>document.fonts.ready);
    await page.pdf({path:path.join(root,'01-project-workflow-manual.pdf'),format:'A4',preferCSSPageSize:true,printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="width:100%;font-size:8px;color:#546574;padding:0 15mm;display:flex;justify-content:space-between"><span>Gon 프로젝트 워크플로우 매뉴얼 · 2026.10.31</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'});
    console.log('A4 PDF generated');
  } finally { await browser.close(); }
})();
