// Render dist/index.html and save one PNG per section/screen.
//   node tools/screenshot.js [outDir] [scale]
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const out = path.resolve(process.argv[2] || 'shots');
  const scale = Number(process.argv[3] || 1);
  require('fs').mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1480, height: 900 }, deviceScaleFactor: scale });
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + path.resolve(__dirname, '../dist/index.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(800);
  await (await p.$('#poster')).screenshot({ path: path.join(out, 'poster.png') });
  const figs = await p.$$('.screens figure .phone');
  for (let i = 0; i < figs.length; i++) await figs[i].screenshot({ path: path.join(out, `screen-${String.fromCharCode(97 + i)}.png`) });
  await (await p.$$('.sec'))[2].screenshot({ path: path.join(out, 'widgets.png') });
  await (await p.$('.sheet')).screenshot({ path: path.join(out, 'components.png') });
  await p.screenshot({ path: path.join(out, 'header.png') });
  console.log('screens', figs.length, 'errors', errs, 'scrollWidth', await p.evaluate(() => document.documentElement.scrollWidth));
  await p.setViewportSize({ width: 390, height: 844 });
  await p.waitForTimeout(300);
  console.log('mobile scrollWidth', await p.evaluate(() => document.documentElement.scrollWidth));
  await b.close();
})();
