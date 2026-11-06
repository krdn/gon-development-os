const { chromium } = require('playwright');
const { pathToFileURL } = require('node:url');
const path = require('node:path');
(async () => {
  const browser = await chromium.launch({ headless: true, ...(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}) });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
    await page.goto(pathToFileURL(path.join(__dirname, 'index.html')).href);
    await page.evaluate(async () => {
      await document.fonts.ready;
      document.querySelectorAll('details').forEach(n => { n.open = true; });
    });
    await page.pdf({
      path: path.join(__dirname, 'guide.pdf'), format: 'A4', preferCSSPageSize: true,
      printBackground: true, displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#53676a">Gon · Orca + Codex CLI · <span class="pageNumber"></span> / <span class="totalPages"></span></div>',
    });
    console.log('guide.pdf 생성 완료');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
