const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { spawnSync } = require('node:child_process');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');
const root = __dirname;
const cases = [];
const pass = name => cases.push({ name, status: 'PASS' });
(async () => {
  const browser = await chromium.launch({ headless: true, ...(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, permissions: ['clipboard-read', 'clipboard-write'] });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    const url = pathToFileURL(path.join(root, 'index.html')).href;
    await page.goto(url);
    await page.evaluate(() => { document.documentElement.style.scrollBehavior = 'auto'; });
    fs.writeFileSync(path.join(root, 'rendered-prompts.json'), JSON.stringify(await page.locator('.copybox pre').allTextContents(), null, 2));
    assert.equal(await page.locator('details.step').count(), 13);
    for (const id of ['S0', 'P1', 'P2', 'P3', 'P4', 'P5', 'G1', 'D1', 'D2', 'D3', 'D4', 'G2', 'D5']) {
      await page.locator(`.mapnode[href="#step-${id}"]`).click();
      assert.equal(await page.locator(`#step-${id}`).getAttribute('open'), '');
    }
    pass('흐름도의 13개 단계가 올바른 상세 설명을 연다');
    await page.locator('#project-name').fill('검증용 프로젝트');
    await page.locator('#project-path').fill("/tmp/내 프로젝트's 폴더");
    await page.locator('#repo-name').fill('example-owner/my-project');
    await page.locator('#config button').click();
    const launch = await page.locator('#step-S0 [data-kind=shell] pre').nth(1).textContent();
    const parsed = spawnSync('python3', ['-c', 'import shlex,sys,json; print(json.dumps(shlex.split(sys.stdin.read())))'], { input: launch, encoding: 'utf8' });
    assert.equal(parsed.status, 0);
    assert.equal(JSON.parse(parsed.stdout)[6], "path:/tmp/내 프로젝트's 폴더");
    assert.ok(await page.locator('#step-P1 .copybox pre').textContent().then(t => t.includes('검증용 프로젝트')));
    pass('프로젝트 값이 반영되고 공백·작은따옴표 경로가 하나의 명령 인수로 유지된다');
    const copyButton = page.locator('#step-P5 .copy');
    await copyButton.click();
    const copied = await page.evaluate(() => navigator.clipboard.readText());
    assert.equal(copied, await page.locator('#step-P5 .copybox pre').textContent());
    pass('P5 실제 복사 버튼의 클립보드 값이 표시한 요청문과 일치한다');
    await page.locator('#project-path').fill('relative/path');
    await page.locator('#step-P5 .copy').click();
    assert.match(await page.locator('#config-status').textContent(), /절대 경로/);
    assert.equal(await page.evaluate(() => navigator.clipboard.readText()), copied);
    pass('잘못된 경로는 반영·복사를 막고 이전 클립보드를 보존한다');
    await page.locator('#project-path').fill("/tmp/내 프로젝트's 폴더");
    await page.locator('#repo-name').fill('');
    await page.locator('#step-G1 .copybox[data-kind=prompt] .copy').nth(1).click();
    assert.match(await page.locator('#toast').textContent(), /GitHub 소유자/);
    assert.equal(await page.evaluate(() => navigator.clipboard.readText()), copied);
    pass('GitHub 이름 없이 원격 변경 요청문을 복사하지 않는다');
    await page.locator('#repo-name').fill('example-owner/my-project');
    await page.locator('#config button').click();
    await page.locator('[data-check="P5-0"]').check();
    await page.reload();
    await page.locator('.mapnode[href="#step-P5"]').click();
    assert.equal(await page.locator('#project-name').inputValue(), '검증용 프로젝트');
    assert.equal(await page.locator('[data-check="P5-0"]').isChecked(), true);
    pass('새로고침 후 설정과 확인 항목이 유지된다');
    await page.locator('#project-path').fill('/tmp/another-project');
    await page.locator('#config button').click();
    assert.equal(await page.locator('[data-check="P5-0"]').isChecked(), false);
    pass('다른 프로젝트 경로로 바꾸면 이전 완료 체크를 가져오지 않는다');
    await page.locator('#project-name').fill('<img src=x onerror=alert(1)>');
    await page.locator('#config button').click();
    assert.equal(await page.locator('.copybox img').count(), 0);
    assert.ok((await page.locator('#step-P1 .copybox pre').textContent()).includes('<img src=x'));
    pass('입력한 특수 문자는 HTML로 실행되지 않고 텍스트로 표시된다');
    await page.locator('#expand-all').click();
    assert.equal(await page.locator('details.step[open]').count(), 13);
    await page.locator('#expand-all').click();
    assert.equal(await page.locator('details.step[open]').count(), 0);
    pass('모든 단계 펼치기·접기가 작동한다');
    await page.setViewportSize({ width: 390, height: 844 });
    await page.locator('.mapnode[href="#step-P5"]').click();
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true);
    pass('390px 화면에서 단계·설정이 화면 밖으로 넘치지 않는다');
    const before = await page.locator('details[open]').count();
    await page.evaluate(() => window.dispatchEvent(new Event('beforeprint')));
    assert.equal(await page.locator('details[open]').count(), await page.locator('details').count());
    await page.evaluate(() => window.dispatchEvent(new Event('afterprint')));
    assert.equal(await page.locator('details[open]').count(), before);
    pass('인쇄 시 접힌 내용을 모두 열고 이후 원래 상태로 복구한다');
    await page.goto(pathToFileURL(path.join(root, 'examples.html')).href);
    assert.equal(await page.locator('section.panel').count(), 8);
    assert.ok((await page.locator('body').textContent()).includes('실제 조사·승인·구현 결과가 아닙니다'));
    pass('별도 예시 뷰어에서 8개 문서를 설치 없이 읽는다');
    assert.deepEqual(errors, []);
    pass('페이지 실행 중 JavaScript 오류가 없다');
    fs.writeFileSync(path.join(root, 'browser-tests.json'), JSON.stringify({
      date: '2026-11-02', viewports: [1440, 390], clipboard_length: copied.length,
      document_sha256: crypto.createHash('sha256').update(fs.readFileSync(path.join(root, 'index.html'))).digest('hex'),
      cases,
    }, null, 2) + '\n');
    console.log(`${cases.length}개 브라우저 검사 PASS`);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
