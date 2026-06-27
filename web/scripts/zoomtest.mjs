import puppeteer from 'puppeteer-core';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const URL = 'http://localhost:4321/paintings/the-harvesters';

const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new', args: ['--no-sandbox'] });
const page = await browser.newPage();
await page.setViewport({ width: 1200, height: 900 });

const logs = [];
page.on('console', (m) => logs.push(`[console.${m.type()}] ${m.text()}`));
page.on('pageerror', (e) => logs.push(`[pageerror] ${e.message}`));
page.on('requestfailed', (r) => logs.push(`[requestfailed] ${r.url()} — ${r.failure()?.errorText}`));

await page.goto(URL, { waitUntil: 'networkidle2' });

const hasBtn = await page.$('[data-open-zoom]');
console.log('open-zoom button present:', !!hasBtn);

await page.click('[data-open-zoom]');
await new Promise((r) => setTimeout(r, 4000));

const state = await page.evaluate(() => {
  const dlg = document.querySelector('[data-zoom]');
  const osd = document.querySelector('[data-osd]');
  const canvas = osd?.querySelector('canvas');
  return {
    dialogOpen: dlg?.open ?? null,
    osdRect: osd ? { w: osd.clientWidth, h: osd.clientHeight } : null,
    canvasCount: osd ? osd.querySelectorAll('canvas').length : 0,
    canvasRect: canvas ? { w: canvas.width, h: canvas.height } : null,
    osdChildren: osd ? osd.children.length : 0,
  };
});
console.log('state:', JSON.stringify(state));
console.log('--- browser logs ---');
console.log(logs.join('\n') || '(none)');

await page.screenshot({ path: '/tmp/zoomtest.png' });
console.log('screenshot -> /tmp/zoomtest.png');
await browser.close();
