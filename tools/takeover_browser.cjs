// Browser evidence for the preserved page, including runtime requests and interactions.
const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.TCS_PLAYWRIGHT || 'playwright');
const out = process.argv[2];
if (!out) throw new Error('Usage: node tools/takeover_browser.cjs OUTPUT_DIRECTORY');
fs.mkdirSync(out, { recursive: true });
(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const results = [];
  for (const width of [1440, 390]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, deviceScaleFactor: 1 });
    const errors = [], requests = [], failed = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('request', r => requests.push(r.url()));
    page.on('response', r => { if (r.status() >= 400) failed.push({url: r.url(), status: r.status()}); });
    await page.goto((process.env.TCS_BASE_URL || 'http://127.0.0.1:8765') + '/proprietorship.html', { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(out, `proprietorship-${width}.png`), fullPage: true });
    const initial = await page.evaluate(() => {
      const selectors = ['nav', '#hero-title-proprietor', '#custom-main-card', '#custom-faq-container', '.ifcFaqCard', '#related-services', 'footer'];
      return {
        width: document.documentElement.scrollWidth,
        components: Object.fromEntries(selectors.map(s => {
          const el = document.querySelector(s); if (!el) return [s, null];
          const c = getComputedStyle(el), r = el.getBoundingClientRect();
          return [s, {color:c.color, background:c.backgroundColor, border:c.borderColor, font:c.fontSize, x:r.x, y:r.y, width:r.width, height:r.height}];
        })),
        visibleFaqs: [...document.querySelectorAll('.ifcFaqCard')].filter(x => getComputedStyle(x).display !== 'none').length,
        semanticRules: [...document.styleSheets].flatMap(sheet => {try{return [...sheet.cssRules].filter(r => r.selectorText && /\.(bg-brand|text-text|border-border)\b/.test(r.selectorText)).map(r=>r.cssText)}catch{return []}})
      };
    });
    const faq = page.locator('.ifcFaqCardBtn');
    await faq.first().click();
    const opened = await faq.first().getAttribute('aria-expanded');
    await faq.nth(1).click();
    const firstClosed = await faq.first().getAttribute('aria-expanded');
    const more = page.locator('.ifcFaqBtnPrimary');
    await more.click();
    const expandedCount = await page.locator('.ifcFaqCard:visible').count();
    const expandedLabel = await more.innerText();
    await more.click();
    const collapsedCount = await page.locator('.ifcFaqCard:visible').count();
    results.push({width, errors, requests, failed, initial, faq: {opened, firstClosed, expandedCount, expandedLabel, collapsedCount}});
    await page.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(out, 'browser.json'), JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results.map(({width,errors,failed,faq,initial})=>({width,errors,failed,faq,initial})),null,2));
})().catch(e => { console.error(e); process.exit(1); });
