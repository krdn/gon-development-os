const { chromium } = require('playwright');
const { pathToFileURL } = require('node:url');
const path = require('node:path');
const fs = require('node:fs');

(async () => {
  const root = path.resolve(__dirname, '..');
  const options = { headless: true };
  if (process.env.CHROMIUM_PATH) options.executablePath = process.env.CHROMIUM_PATH;
  const browser = await chromium.launch(options);
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    await page.goto(pathToFileURL(path.join(root, 'dist/01-project-workflow-manual.html')).href);
    await page.evaluate(() => document.fonts.ready);
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 1000 });
      const fits = await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth);
      if (!fits) throw new Error(`매뉴얼 가로 넘침: ${width}px`);
    }
    await page.setViewportSize({ width: 1440, height: 1000 });
    const version = fs.readFileSync(path.join(root, 'VERSION'), 'utf8').trim();
    await page.pdf({
      path: path.join(root, 'dist/01-project-workflow-manual.pdf'),
      format: 'A4', preferCSSPageSize: true, printBackground: true,
      displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: `<div style="width:100%;font-size:8px;color:#546574;padding:0 15mm;display:flex;justify-content:space-between"><span>Gon 프로젝트 워크플로우 매뉴얼 · v${version}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`,
    });
    console.log('A4 PDF 생성 및 PC·모바일 가로 넘침 검사 통과');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
