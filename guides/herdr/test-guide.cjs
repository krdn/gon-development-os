const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const url = pathToFileURL(path.join(__dirname, 'index.html')).href;
const results = [];

(async () => {
  const options = { headless: true };
  if (process.env.CHROMIUM_PATH) options.executablePath = process.env.CHROMIUM_PATH;
  const browser = await chromium.launch(options);
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const test = async (name, action) => {
    await action();
    results.push({ name, status: 'PASS' });
    console.log(`PASS: ${name}`);
  };
  const visible = () => page.locator('.step:visible');
  const go = number => page.locator(`.node[data-goto="${number}"]`).click();
  try {
    await page.goto(url);
    await test('다음 단계·새로고침·주소 없이 재방문 시 현재 단계 복원', async () => {
      await go(3);
      await page.click('#next');
      await page.click('#next');
      assert.equal(await visible().getAttribute('id'), 'step-5');
      await page.reload();
      assert.equal(await visible().getAttribute('id'), 'step-5');
      await page.goto(url);
      assert.equal(await visible().getAttribute('id'), 'step-5');
    });
    await test('예제 03 주 요청문과 내 기획 03 주 요청문의 복사 대상 구분', async () => {
      await page.evaluate(() => {
        Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: async text => { window.copiedText = text; } } });
      });
      await go(3);
      await page.click('#copy-current');
      assert.match(await page.evaluate(() => window.copiedText), /할 일 앱 학습 예제/);
      await page.selectOption('#scenario', 'project');
      await page.fill('#project-name', '서버가 있는 가계부');
      await page.click('#apply');
      await page.click('#copy-current');
      assert.match(await page.evaluate(() => window.copiedText), /기술이 미정이면 후보/);
      await page.fill('#project-path', '/tmp/서버가 있는 가계부');
      await page.click('#apply');
      for (const number of [3, 4, 5, 6, 7, 8, 9]) {
        await go(number);
        assert.doesNotMatch(await page.locator(`#step-${number} .scenario:visible`).textContent(), /우유 사기|localStorage|gon-todo-practice|React|정적 웹앱/);
      }
      await page.fill('#project-path', '/home/gon/dev/apps/gon-todo-practice');
      await page.click('#apply');
    });
    await test('체크 기록이 프로젝트 폴더·경로별로 분리되고 새로고침 후 유지', async () => {
      await go(3);
      await page.locator('#step-3 .scenario:visible input').first().check();
      await page.reload();
      assert.equal(await page.locator('#step-3 .scenario:visible input').first().isChecked(), true);
      await page.fill('#project-path', '/tmp/다른 프로젝트');
      await page.click('#apply');
      assert.equal(await page.locator('#step-3 .scenario:visible input').first().isChecked(), false);
      await page.fill('#project-path', '/home/gon/dev/apps/gon-todo-practice');
      await page.click('#apply');
      assert.equal(await page.locator('#step-3 .scenario:visible input').first().isChecked(), true);
      await page.selectOption('#scenario', 'exercise');
      assert.equal(await page.locator('#step-3 .scenario:visible input').first().isChecked(), false);
    });
    await test('비개발 종료·로컬 완료·보관만 완료 분기', async () => {
      await go(14);
      assert.equal(await page.locator('#next').isVisible(), false);
      await page.click('[data-extra="planning-finish"]');
      assert.equal(await page.locator('#planning-finish').getAttribute('open'), '');
      assert.match(await page.locator('#planning-finish pre').textContent(), /재검토 날짜 또는 조건/);
      await go(7);
      await page.click('#step-7 .route-choices [data-goto="10"]');
      assert.equal(await visible().getAttribute('id'), 'step-10');
      await go(8);
      await page.click('#step-8 .route-choices [data-goto="10"]');
      assert.equal(await visible().getAttribute('id'), 'step-10');
    });
    await test('P5에서 새 개발 세션으로 이동하고 준비 단계는 쉘 명령으로 구분', async () => {
      await go(15);
      await page.click('[data-project-start]');
      assert.equal(await page.inputValue('#scenario'), 'project');
      assert.equal(await visible().getAttribute('id'), 'step-1');
      await go(0);
      assert.equal(await page.locator('#copy-current').isDisabled(), false);
      assert.ok(await page.locator('#step-0 .scenario:visible .prompt[data-kind="shell"]').count() > 0);
      assert.match(await page.locator('#step-0 .scenario:visible').textContent(), /쉘/);
    });
    await test('두 경로·16단계·PC/모바일 모두 단일 단계 표시와 가로 넘침 없음', async () => {
      const order = JSON.parse(await page.locator('#guide-config').textContent()).steps;
      for (const width of [1440, 390]) {
        await page.setViewportSize({ width, height: 1000 });
        for (const scenario of ['exercise', 'project']) {
          await page.selectOption('#scenario', scenario);
          for (const step of order) {
            await go(step.id);
            assert.equal(await visible().count(), 1);
            assert.equal(await page.locator('.step:visible .scenario:visible').count(), 1);
            assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
          }
        }
      }
    });
    await test('클립보드 거절 시 원문 선택과 수동 복사 안내', async () => {
      await page.evaluate(() => {
        Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: async () => { throw new Error('거절 테스트'); } } });
      });
      await go(3);
      await page.click('#copy-current');
      assert.equal(await page.evaluate(() => getSelection().toString()), await page.locator('#step-3 .scenario:visible pre[data-primary]').textContent());
      assert.match(await page.locator('#toast').textContent(), /Ctrl\+C/);
    });
    await test('null·문자열·배열·깨진 저장 기록으로도 안내 정상 초기화', async () => {
      for (const data of ['null', '"문자열"', '[]', '{']) {
        const isolated = await browser.newContext();
        const fixture = await isolated.newPage();
        const fixtureErrors = [];
        fixture.on('pageerror', error => fixtureErrors.push(error.message));
        await fixture.addInitScript(value => localStorage.setItem('gon-herdr-cli-guide-v1', value), data);
        await fixture.goto(url);
        assert.equal(await fixture.locator('.step:visible').count(), 1);
        assert.equal(await fixture.locator('#current-label').textContent(), '00 단계 보는 중');
        assert.deepEqual(fixtureErrors, []);
        await isolated.close();
      }
    });
    await test('저장소 사용 불가·잘못된 URL 조각에도 화면과 탐색 유지', async () => {
      const isolated = await browser.newContext();
      const fixture = await isolated.newPage();
      const fixtureErrors = [];
      fixture.on('pageerror', error => fixtureErrors.push(error.message));
      await fixture.addInitScript(() => Object.defineProperty(window, 'localStorage', { get() { throw new Error('저장 불가 테스트'); } }));
      await fixture.goto(url + '#[');
      await fixture.click('#next');
      assert.equal(await fixture.locator('#current-label').textContent(), 'P1 단계 보는 중');
      assert.deepEqual(fixtureErrors, []);
      await isolated.close();
    });
    await test('분할 터미널 배치 전환과 문서·세션 도움말 이동', async () => {
      await page.click('.entrylinks a[href="#workbench"]');
      await page.click('[data-workbench="development"]');
      assert.equal(await page.locator('[data-workbench-view="development"]').isVisible(), true);
      assert.equal(await page.locator('[data-workbench-view="planning"]').isVisible(), false);
      await page.click('[data-workbench="planning"]');
      assert.equal(await page.locator('[data-workbench-view="planning"]').isVisible(), true);
      for (const id of ['sessions', 'documents']) {
        await page.click(`.entrylinks a[href="#${id}"]`);
        assert.equal(await page.locator(`#${id}`).getAttribute('open'), '');
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      }
    });
    await test('상대경로·물결표 경로는 반영과 복사를 막고 절대경로는 안전하게 인용', async () => {
      await page.setViewportSize({ width: 1440, height: 1000 });
      await go(0);
      await page.evaluate(() => {
        Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: async text => { window.copiedText = text; } } });
        window.copiedText = 'unchanged';
      });
      for (const value of ['~/dev/project', 'relative/project', '']) {
        await page.fill('#project-path', value);
        await page.locator('#step-0 .scenario:visible .prompt[data-kind="shell"] .copy').first().click();
        assert.equal(await page.getAttribute('#project-path', 'aria-invalid'), 'true');
        assert.equal(await page.evaluate(() => window.copiedText), 'unchanged');
      }
      await page.fill('#project-path', "/tmp/O'Brien 문서");
      await page.click('#apply');
      assert.equal(await page.getAttribute('#project-path', 'aria-invalid'), null);
      const command = await page.locator('#step-0 .scenario:visible .prompt[data-kind="shell"] pre').first().textContent();
      assert.ok(command.includes("'" + "/tmp/O'Brien 문서".replaceAll("'", "'\\''") + "'"));
      await page.fill('#project-path', '/home/gon/dev/apps/gon-todo-practice');
      await page.click('#apply');
    });
    await test('기획 체크는 두 경로에 공통이고 개발 체크는 경로별 유지', async () => {
      await page.selectOption('#scenario', 'exercise');
      await go(11);
      await page.locator('#step-11 .scenario:visible input').first().check();
      await page.selectOption('#scenario', 'project');
      assert.equal(await page.locator('#step-11 .scenario:visible input').first().isChecked(), true);
      await page.fill('#project-path', '/tmp/다른 기획');
      await page.click('#apply');
      assert.equal(await page.locator('#step-11 .scenario:visible input').first().isChecked(), false);
      await page.fill('#project-path', '/home/gon/dev/apps/gon-todo-practice');
      await page.click('#apply');
    });
    await test('개발 배치를 선택한 뒤 인쇄해도 두 캡션이 올바른 뷰를 가리킴', async () => {
      await page.click('.entrylinks a[href="#workbench"]');
      await page.click('[data-workbench="development"]');
      await page.emulateMedia({ media: 'print' });
      const captions = await page.evaluate(() => ['planning', 'development'].map(kind => getComputedStyle(document.querySelector(`[data-workbench-view="${kind}"] .bench-caption`), '::before').content));
      assert.equal(captions[0], 'none');
      assert.match(captions[1], /개발 탭/);
      await page.emulateMedia({ media: 'screen' });
    });
    await test('실행 중 브라우저 오류 없음', async () => assert.deepEqual(errors, []));
    const report = { timestamp: new Date().toISOString(), engine: 'Chromium / Playwright', document_sha256: require('node:crypto').createHash('sha256').update(fs.readFileSync(path.join(__dirname, 'index.html'))).digest('hex'), viewports: [1440, 390], cases: results };
    fs.writeFileSync(path.join(__dirname, 'browser-tests.json'), JSON.stringify(report, null, 2) + '\n');
    console.log(`브라우저 회귀 검사 ${results.length}개 PASS`);
  } finally {
    await context.close();
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
