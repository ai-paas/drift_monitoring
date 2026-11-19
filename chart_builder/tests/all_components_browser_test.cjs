const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright-core');

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome',
    args: ['--no-sandbox', '--disable-dev-shm-usage']
  });
  const overlayCodes = ['annotation_callout', 'event_marker', 'threshold_line', 'uncertainty_band'];
  const expectedText = {
    annotation_callout: 'one-sided drift band', comparison_table: '-0.05',
    contribution_view: '-0.14', decision_card: '0.86', distance_metric_view: '0.42',
    distribution_summary_plot: 'med=', domain_specific_visual: 'gap 0.13',
    histogram_view: 'reference', matrix_view: 'KS', p_value_view: '0.032',
    performance_metric_view: 'AUC', proportion_view: '-11pp', quantile_view: 'q95',
    reference_current_comparison: '+0.16', small_multiples: 'income', control_chart: 'UCL'
  };
  const snapshots = [];
  const results = [];
  try {
    for (const width of [1600, 1280]) {
      const page = await browser.newPage({ viewport: { width, height: 1000 } });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.route('**/api/**', route =>
        ['GET', 'HEAD'].includes(route.request().method()) ? route.continue() : route.abort());
      await page.goto(process.env.BUILDER_URL || 'http://127.0.0.1:8766/builder_prototype.html');
      await page.waitForFunction(() => document.querySelector('#payloadViewer').value.includes('chartId'));
      const codes = await page.locator('.palette-item').evaluateAll(items => items.map(item => item.dataset.componentType));
      assert.equal(codes.length, 32);
      for (const code of codes) {
        await page.locator('#newChartButton').click();
        const area = page.locator('.chart-area').first();
        if (overlayCodes.includes(code)) {
          await page.locator('[data-component-type="trend_line"]').click();
          await area.click();
        }
        await page.locator(`[data-component-type="${code}"]`).click();
        await area.locator('.area-head h2').click();
        await page.locator('#buildButton').click();
        await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
        const result = await area.evaluate((element, code) => {
          const payload = JSON.parse(document.querySelector('#payloadViewer').value);
          const instance = payload.components.find(item => item.componentType === code);
          const wrapper = [...element.querySelectorAll('[data-instance-id]')]
            .find(item => item.dataset.instanceId === instance.componentInstanceId);
          return {
            code, text: wrapper.textContent, svg: wrapper.querySelectorAll('svg').length,
            shapes: wrapper.querySelectorAll('path,polyline,circle,rect,line').length,
            invalid: /NaN|Infinity|undefined|component summary|missing .*data|Unknown component/.test(wrapper.innerHTML),
            width: wrapper.getBoundingClientRect().width, height: wrapper.getBoundingClientRect().height
          };
        }, code);
        assert.equal(result.invalid, false, `${width} ${code}: invalid output`);
        assert.ok(result.svg > 0 && result.shapes > 0, `${width} ${code}: no graphics`);
        assert.ok(result.width > 0 && result.height > 0, `${width} ${code}: invisible`);
        // Compact mode deliberately omits some numeric labels and legends.
        if (width === 1600 && expectedText[code]) assert.ok(result.text.includes(expectedText[code]), `${code}: missing ${expectedText[code]}`);
        results.push({ width, ...result });
        if (width === 1600 && process.env.BUILDER_ARTIFACT_DIR) {
          snapshots.push({ code, data: (await area.screenshot()).toString('base64') });
        }
        const zoom = area.locator('.area-zoom-link');
        if (await zoom.count()) {
          const countBefore = await page.locator('#payloadViewer').inputValue().then(value => JSON.parse(value).components.length);
          await zoom.click();
          await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
          await page.locator('#componentZoomPopup').waitFor({ state: 'visible' });
          assert.equal(await page.locator('#payloadViewer').inputValue().then(value => JSON.parse(value).components.length), countBefore, 'zoom added a component');
          const zoomText = await page.locator('#componentZoomChart').textContent();
          assert.ok(!zoomText.includes('component summary'), `${code}: zoom placeholder`);
          if (width === 1600 && expectedText[code]) assert.ok(zoomText.includes(expectedText[code]), `${code}: zoom lost data`);
          await page.locator('.component-zoom-close').click();
        }
      }
      // A saved report uses Runtime-specific mappings, not palette defaults.
      await page.locator('#savedChartSelect').selectOption({ label: 'CHART-ADAPT-001' });
      await page.waitForFunction(() => JSON.parse(document.querySelector('#payloadViewer').value).chartId === 'CHART-ADAPT-001');
      const imported = await page.locator('[data-instance-id]').evaluateAll(wrappers =>
        wrappers.find(item => item.dataset.instanceId.includes('accuracy'))?.textContent || '');
      assert.ok(imported.includes('time') && imported.includes('online accuracy'), 'saved report renderer changed');
      assert.deepEqual(errors, []);
      console.log(`PASS ${width}px: ${codes.length} components, 4 overlays, preview/zoom, data evidence, saved report, no JS errors`);
      await page.close();
    }
    if (process.env.BUILDER_ARTIFACT_DIR) {
      fs.mkdirSync(process.env.BUILDER_ARTIFACT_DIR, { recursive: true });
      fs.writeFileSync(path.join(process.env.BUILDER_ARTIFACT_DIR, 'all-components-results.json'), JSON.stringify(results, null, 2));
      const overview = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
      await overview.setContent(`<style>body{font:14px sans-serif;background:#eee}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.card{background:white;padding:8px}img{width:100%}</style><h1>Builder: 32 components</h1><div class="grid">${snapshots.map(item => `<div class="card"><b>${item.code}</b><img src="data:image/png;base64,${item.data}"></div>`).join('')}</div>`);
      await overview.screenshot({ path: path.join(process.env.BUILDER_ARTIFACT_DIR, 'all-components.png'), fullPage: true });
      await overview.close();
    }
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
