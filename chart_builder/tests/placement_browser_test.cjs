// Run with NODE_PATH pointing to an installed playwright-core package if needed.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { chromium } = require('playwright-core');

(async () => {
  // Verify custom data precedence and saved-config compatibility independently
  // of whichever chart happens to be saved on the running server.
  const sourceText = fs.readFileSync(path.join(__dirname, '../web/builder_prototype.js'), 'utf8');
  const adapterSource = sourceText.slice(
    sourceText.indexOf('  function buildRuntimePayload()'),
    sourceText.indexOf('  function detectPresetCode('));
  const original = {
    layout: { areas: [{ area: 'main', title: '사용자 제목' }] },
    data: { 'sample.trend': [], custom: [{ value: 99 }] },
    components: [{ componentType: 'adaptive_model_structure_view', config: {
      primary_series_field: 'old_primary', secondary_series_field: 'old_secondary',
      value_field: 'custom_primary', secondary_value_field: 'custom_secondary'
    } }]
  };
  const before = JSON.stringify(original);
  const runtime = vm.runInNewContext(adapterSource + '\nbuildRuntimePayload()', {
    payload: original, clone: value => JSON.parse(JSON.stringify(value)),
    sampleData: { trend: [{ value: 1 }], referenceCurrent: [], pValues: [], adaptiveModelStructure: [{ time: 1 }] }
  });
  assert.equal(JSON.stringify(original), before);
  assert.equal(runtime.data['sample.trend'].length, 0);
  assert.equal(runtime.data.custom[0].value, 99);
  assert.equal(runtime.components[0].config.value_field, 'custom_primary');
  assert.equal(runtime.components[0].config.secondary_value_field, 'custom_secondary');
  assert.equal(runtime.layout.areas[0].title, '사용자 제목');
  assert.equal(runtime.data['sample.adaptiveModelStructure'].length, 1);
  console.log('PASS custom data, explicit field mappings, custom titles and saved payload preservation');
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome',
    args: ['--no-sandbox', '--disable-dev-shm-usage']
  });
  try {
    for (const width of [1600, 1280]) {
      const page = await browser.newPage({ viewport: { width, height: 1000 } });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.route('**/api/**', route =>
        ['GET', 'HEAD'].includes(route.request().method()) ? route.continue() : route.abort());
      await page.goto(process.env.BUILDER_URL || 'http://127.0.0.1:8766/builder_prototype.html');
      await page.waitForFunction(() => document.querySelector('#payloadViewer').value.includes('chartId'));
      await page.locator('#newChartButton').click();
      const palette = code => page.locator(`[data-component-type="${code}"]`);
      const area = name => page.locator(`.chart-area[data-area="${name}"]`);
      const payload = () => page.locator('#payloadViewer').inputValue().then(JSON.parse);
      await palette('adaptive_model_structure_view').click();
      await area('top_left').click();
      assert.equal((await payload()).components.length, 1);
      assert.equal(await area('top_left').locator('svg').count(), 1);
      assert.equal(await area('top_left').textContent().then(text => text.includes('component summary')), false);
      const adapted = await page.evaluate(() =>
        document.querySelector('#chartContainer').__chartRuntimePayload);
      assert.equal(adapted.components[0].config.value_field, 'primary_score');
      assert.equal(adapted.components[0].config.secondary_value_field, 'secondary_score');
      assert.equal(adapted.data['sample.adaptiveModelStructure'].length, 10);
      assert.equal((await payload()).components[0].config.value_field, undefined);
      assert.equal(await page.locator('.area-label').count(), 0);
      assert.equal(await area('top_left').locator('.area-head h2').textContent(), 'top_left');
      // Clicking the rendered component selects it without adding a duplicate.
      await area('top_left').locator('svg').click();
      assert.equal((await payload()).components.length, 1);
      await palette('threshold_line').click();
      // The area heading is a placement target outside the existing component.
      await area('top_left').locator('.area-head h2').click();
      assert.equal((await payload()).components.filter(item => item.isOverlay).length, 1);
      await palette('bar_chart').scrollIntoViewIfNeeded();
      const source = await palette('bar_chart').boundingBox();
      const target = await area('top_right').boundingBox();
      await page.mouse.move(source.x + source.width / 2, source.y + source.height / 2);
      await page.mouse.down();
      await page.mouse.move(target.x + target.width / 2, target.y + target.height / 2, { steps: 12 });
      await page.mouse.up();
      assert.equal((await payload()).components.length, 3);
      await page.locator('#buildButton').click();
      assert.equal((await payload()).components.length, 3);
      assert.equal(await area('top_right').locator('svg').count(), 1);
      await palette('trend_line').click();
      await area('top_right').locator('.area-head h2').click();
      const replaced = (await payload()).components.filter(item => item.area === 'top_right');
      assert.equal(replaced.length, 1);
      assert.equal(replaced[0].componentType, 'trend_line');
      assert.deepEqual(errors, []);
      console.log(`PASS ${width}px: click, selection, drag, overlay, sample/config adaptation, labels, preview`);
      await page.close();
    }
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
