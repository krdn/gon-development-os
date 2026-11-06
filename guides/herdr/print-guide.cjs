const { chromium } = require('playwright');
const { pathToFileURL } = require('node:url');
const path = require('node:path');

(async () => {
  const options = { headless: true };
  if (process.env.CHROMIUM_PATH) options.executablePath = process.env.CHROMIUM_PATH;
  const browser = await chromium.launch(options);
  try {
    for (const scenario of ['exercise', 'project']) {
      const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
      await page.goto(pathToFileURL(path.join(__dirname, 'index.html')).href);
      await page.selectOption('#scenario', scenario);
      if (scenario === 'project') {
        await page.fill('#project-name', '내 프로젝트');
        await page.fill('#project-path', '/home/내계정/dev/apps/내프로젝트');
        await page.click('#apply');
      }
      await page.evaluate(async () => {
        await document.fonts.ready;
        document.querySelectorAll('details').forEach(detail => { detail.open = true; });
      });
      const label = scenario === 'exercise' ? '할 일 앱 예제' : '내 기획 문서';
      const file = scenario === 'exercise' ? 'guide.pdf' : 'project-guide.pdf';
      await page.pdf({
        path: path.join(__dirname, file), format: 'A4', preferCSSPageSize: true,
        printBackground: true, displayHeaderFooter: true, headerTemplate: '<span></span>',
        footerTemplate: `<div style="font-size:8px;width:100%;text-align:center;color:#53676a">Gon 개발 워크플로우 · ${label} · <span class="pageNumber"></span> / <span class="totalPages"></span></div>`,
      });
      await page.close();
      console.log(`PDF 생성: ${file}`);
    }
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
