// Render dist/index.html and save PNGs of every section and screen, in both modes.
//   node tools/screenshot.js [outDir] [scale]
// Writes <outDir>/dark/*.png and <outDir>/light/*.png plus keyart.png.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const out = path.resolve(process.argv[2] || 'shots');
  const scale = Number(process.argv[3] || 1);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1480, height: 900 }, deviceScaleFactor: scale, reducedMotion: 'reduce' });
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + path.resolve(__dirname, '../dist/index.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(800);
  await p.addStyleTag({ content: '#theme-switch{display:none!important} *{animation:none!important}' });
  fs.mkdirSync(out, { recursive: true });
  await (await p.$('.ka-pair')).screenshot({ path: path.join(out, 'keyart.png') });

  for (const mode of ['dark', 'light']) {
    const dir = path.join(out, mode);
    fs.mkdirSync(dir, { recursive: true });
    await p.evaluate(m => document.documentElement.setAttribute('data-theme', m), mode);
    await p.waitForTimeout(300);
    const figs = await p.$$('.screens figure .phone');
    for (const fig of figs) {
      const letter = await fig.evaluate(el => el.closest('figure').querySelector('figcaption b').textContent.trim()[0].toLowerCase());
      await fig.screenshot({ path: path.join(dir, `screen-${letter}.png`) });
    }
    await (await p.$$('.sec'))[2].screenshot({ path: path.join(dir, 'widgets.png') });
    await (await p.$('.sheet')).screenshot({ path: path.join(dir, 'components.png') });
    const insts = await p.$$('.insts');
    await insts[0].screenshot({ path: path.join(dir, 'instruments.png') });
    if (insts[1]) await insts[1].screenshot({ path: path.join(dir, 'patterns.png') });
    await (await p.$('.xp-grid')).screenshot({ path: path.join(dir, 'posters.png') });
    await (await p.$('.con')).screenshot({ path: path.join(dir, 'console.png') });
    await p.evaluate(() => window.scrollTo(0, 0));
    await p.screenshot({ path: path.join(dir, 'header.png') });
    console.log(mode, 'screens', figs.length);
  }
  console.log('errors', errs, 'scrollWidth', await p.evaluate(() => document.documentElement.scrollWidth));
  await p.setViewportSize({ width: 390, height: 844 });
  await p.waitForTimeout(300);
  console.log('mobile scrollWidth', await p.evaluate(() => document.documentElement.scrollWidth));
  await b.close();
})();
