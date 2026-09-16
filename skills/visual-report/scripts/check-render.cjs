#!/usr/bin/env node
const fs = require('node:fs/promises');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { createHash } = require('node:crypto');
const inspectPage = require('./render-page.cjs');

const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const options = { timeout: 60000, geometry: false, widths: [], theme: 'dark' };
let source, output, basename, browser, run, axeSource;
const result = { source: {}, checks: [], views: [], errors: [], status: 'error', exitCode: 2, reviewRequired: true };
const started = Date.now();
const add = (name, status, detail, extra = {}) => result.checks.push({ name, status, detail, ...extra });

function argumentsFor(args) {
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--help' || arg === '-h') return false;
    if (arg === '--geometry') { options.geometry = true; continue; }
    if (['--output-dir', '--timeout', '--browser', '--widths', '--theme'].includes(arg)) {
      const value = args[++i];
      if (!value || value.startsWith('--')) throw new Error(`missing value for ${arg}`);
      options[arg.slice(2)] = value;
    } else if (arg.startsWith('-') || source) throw new Error(`unexpected argument: ${arg}`);
    else source = path.resolve(arg);
  }
  if (!source) throw new Error('a report path is required');
  if (!['dark', 'light', 'both'].includes(options.theme)) throw new Error('--theme must be dark, light, or both');
  result.captureThemes = options.theme === 'both' ? ['light', 'dark'] : [options.theme];
  options.timeout = Number(options.timeout);
  if (!Number.isInteger(options.timeout) || options.timeout < 100 || options.timeout > 600000) throw new Error('--timeout must be 100 to 600000 milliseconds');
  options.widths = typeof options.widths === 'string' ? options.widths.split(',').map(Number) : [];
  if (options.widths.some(w => !Number.isInteger(w) || w < 240 || w > 3840)) throw new Error('--widths must contain comma-separated widths from 240 to 3840');
  return true;
}

async function atomicLink(target, destination) {
  const temporary = `${destination}.${path.basename(run)}.link`;
  await fs.symlink(target, temporary);
  await fs.rename(temporary, destination);
}

async function finish() {
  result.durationMs = Date.now() - started;
  result.finishedAt = new Date().toISOString();
  result.status = result.errors.length ? 'error' : result.checks.some(c => c.status === 'fail') ? 'fail' : 'pass';
  result.exitCode = result.status === 'error' ? 2 : result.status === 'fail' ? 1 : 0;
  if (run) {
    result.outputDirectory = run;
    const json = path.join(run, 'result.json');
    await fs.writeFile(json, JSON.stringify(result, null, 2) + '\n');
    const latest = path.join(output, `${basename}.render-latest`);
    // one shared pointer keeps concurrent screenshot and JSON aliases coherent.
    await atomicLink(path.basename(run), latest);
    await atomicLink(`${basename}.render-latest/result.json`, path.join(output, `${basename}.render.json`));
    for (const view of result.views.filter(v => v.state === 'default')) {
      const full = view.images.find(i => i.kind === 'full');
      if (!full) continue;
      await atomicLink(`${basename}.render-latest/${path.basename(full.path)}`, path.join(output, `${basename}.${view.name}.png`));
      if (view.theme === (options.theme === 'dark' ? 'dark' : 'light') && ['wide', 'narrow'].includes(view.name.split('-')[0])) await atomicLink(`${basename}.render-latest/${path.basename(full.path)}`, path.join(output, `${basename}.${view.name.split('-')[0]}.png`));
    }
    const unique = new Map(result.checks.filter(c => ['fail', 'warn'].includes(c.status)).map(c => [`${c.name}:${c.detail}`, c]));
    for (const c of unique.values()) console.log(`${c.status.toUpperCase()}: ${c.name}: ${c.detail}`);
    for (const error of result.errors) console.error(`ERROR: ${error}`);
    console.log(`${result.status}: ${result.views.length} measured views; ${result.views.filter(v => v.images.length).length} captured views; visual review required in ${result.captureThemes.join(" and ")}`);
    for (const view of result.views) {
      const image = view.images.find(i => i.kind === 'full');
      if (image) console.log(`${view.name} ${view.state}: ${image.path}`);
    }
    console.log(`json: ${json}`);
  } else console.error(`ERROR: ${result.errors.join('; ')}`);
  process.exitCode = result.exitCode;
}

async function findBrowser() {
  if (options.browser || process.env.CHROME_PATH) return options.browser || process.env.CHROME_PATH;
  const candidates = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', ...String(process.env.PATH).split(path.delimiter).flatMap(p => ['chromium', 'chromium-browser', 'google-chrome'].map(name => path.join(p, name)))];
  for (const candidate of candidates) {
    try { await fs.access(candidate, fs.constants.X_OK); return candidate; } catch {}
  }
  throw new Error('Chrome not found; use --browser PATH or CHROME_PATH');
}

async function settle(page) {
  await page.evaluate(async () => {
    document.querySelectorAll('img[loading="lazy"]').forEach(e => e.loading = 'eager');
    document.querySelectorAll('video,audio').forEach(e => e.pause());
    document.getAnimations().forEach(a => a.pause());
    await document.fonts.ready;
    await Promise.all([...document.images].map(e => e.decode().catch(() => {})));
  });
  let previous, stable = 0;
  for (let i = 0; i < 30; i++) {
    const current = await page.evaluate(() => JSON.stringify({ width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight, rects: [...document.querySelectorAll('main, .hero, h1, details')].map(e => { const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }) }));
    stable = current === previous ? stable + 1 : 0;
    if (stable >= 2) return;
    previous = current;
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error('layout did not stabilize within 3 seconds');
}

async function image(page, view, name, kind, settings = {}) {
  const destination = path.join(run, `${name}.png`);
  await page.screenshot({ path: destination, animations: 'disabled', timeout: Math.min(15000, options.timeout), ...settings });
  const bytes = await fs.readFile(destination);
  if (bytes.toString('hex', 0, 8) !== '89504e470d0a1a0a') throw new Error(`invalid screenshot: ${destination}`);
  const dimensions = { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) };
  view.images.push({ path: destination, kind, ...dimensions, ...(settings.clip ? { clip: settings.clip } : {}) });
  return dimensions;
}

async function capture(page, name, state) {
  await page.evaluate(() => window.scrollTo(0, 0));
  await settle(page);
  const measured = await page.evaluate(inspectPage, { geometry: options.geometry });
  const expected = page.viewportSize();
  if (measured.width !== expected.width || measured.height !== expected.height) throw new Error(`viewport mismatch: ${JSON.stringify(measured)}`);
  const view = { name, state, ...measured, images: [] };
  delete view.checks;
  result.views.push(view);
  for (const check of measured.checks) result.checks.push({ ...check, view: name, state });
  const contrast = await page.evaluate(async () => {
    const audit = await axe.run(document, { runOnly: ['color-contrast'], resultTypes: ['violations', 'incomplete'], preload: false });
    return { violations: audit.violations, incomplete: audit.incomplete, passed: audit.passes.length };
  });
  for (const [key, status] of [['violations', 'fail'], ['incomplete', 'unsupported']]) {
    for (const rule of contrast[key]) for (const node of rule.nodes) {
      const data = [...node.any, ...node.all, ...node.none].map(c => c.data);
      const outcome = data.some(d => d?.messageKey === 'equalRatio') ? 'fail' : status;
      add('color-contrast', outcome, node.failureSummary || rule.description, { view: name, state, elements: node.target, data });
    }
  }
  if (contrast.passed) add('color-contrast', 'pass', 'supported text contrast checked automatically', { view: name, state });
  if (!contrast.passed && !contrast.violations.length && !contrast.incomplete.length) add('color-contrast', 'unsupported', 'no supported text contrast cases', { view: name, state });
  if (!result.captureThemes.includes(view.theme)) return;
  const stem = `${name}${state === 'default' ? '' : `-${state}`}`;
  if (measured.pageHeight > 50000 || measured.pageWidth > 10000) throw new Error('page exceeds capture limit (50000px high or 10000px wide); split the report before reviewing');
  const full = await image(page, view, stem, 'full', { fullPage: true });
  if (full.height !== measured.pageHeight || full.width !== measured.pageWidth) throw new Error(`full-page capture dimensions differ from measured page: ${stem}`);
  const after = await page.evaluate(() => ({ width: innerWidth, height: innerHeight, pageHeight: document.documentElement.scrollHeight }));
  if (after.width !== expected.width || after.height !== expected.height || after.pageHeight !== measured.pageHeight) throw new Error(`capture changed the viewport or layout: ${stem}`);
  if (measured.pageHeight > 1800) {
    for (let y = 0; y < measured.pageHeight; y += 900) {
      await image(page, view, `${stem}-y${y}`, 'tile', { fullPage: true, clip: { x: 0, y, width: measured.width, height: Math.min(900, measured.pageHeight - y) } });
    }
  }
  const warningRegions = new Map(measured.checks.filter(c => c.status === 'warn' && c.region).map(c => [JSON.stringify(c.region), c.region]));
  let warningIndex = 0;
  for (const region of warningRegions.values()) {
    const x = Math.max(0, Math.floor(region.x - 8)), y = Math.max(0, Math.floor(region.y - 8));
    const width = Math.min(measured.pageWidth - x, Math.ceil(region.width + 16));
    const height = Math.min(measured.pageHeight - y, Math.ceil(region.height + 16));
    if (width > 0 && height > 0) {
      await image(page, view, `${stem}-warning-${warningIndex++}`, 'warning', { fullPage: true, clip: { x, y, width, height } });
      const screenshot = view.images.at(-1).path;
      result.checks.filter(c => c.view === name && c.state === state && JSON.stringify(c.region) === JSON.stringify(region)).forEach(c => c.screenshot = screenshot);
    }
  }
  if (measured.scrollables.length > 20) throw new Error('more than 20 scroll containers; inspect additional states manually');
  for (const scroll of measured.scrollables) {
    const target = page.locator(`[data-render-scroll-index="${scroll.index}"]`);
    const offsets = (size, total) => {
      if (size <= 0) throw new Error('invalid scroll-container dimensions');
      const values = [0];
      for (let at = size; at < total; at += size) values.push(Math.min(at, total - size));
      return [...new Set(values)];
    };
    const xs = scroll.horizontal ? offsets(scroll.width, scroll.scrollWidth) : [0];
    const ys = scroll.vertical ? offsets(scroll.height, scroll.scrollHeight) : [0];
    if (xs.length * ys.length > 40) throw new Error('scroll container exceeds 40 capture positions');
    for (const y of ys) for (const x of xs) {
      await target.evaluate((e, p) => { e.scrollTo(p.x, p.y); }, { x, y });
      const destination = path.join(run, `${stem}-scroll-${scroll.index}-${x}-${y}.png`);
      await target.screenshot({ path: destination, animations: 'disabled', timeout: Math.min(15000, options.timeout) });
      const actual = await target.evaluate(e => ({ x: e.scrollLeft, y: e.scrollTop }));
      view.images.push({ path: destination, kind: 'scroll', element: scroll.element, scroll: actual });
    }
    await target.evaluate(e => e.scrollTo(0, 0));
  }
}

async function inspectViews() {
  const viewportWidths = [...new Set([820, 500, ...options.widths])];
  for (const width of viewportWidths) for (const theme of ['light', 'dark']) {
    const name = `${width === 820 ? 'wide' : width === 500 ? 'narrow' : `width-${width}`}-${theme}`;
    const context = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: theme, reducedMotion: 'reduce', serviceWorkers: 'block', deviceScaleFactor: 1 });
    context.setDefaultTimeout(Math.min(15000, options.timeout));
    const page = await context.newPage();
    const resources = new Set(), failures = new Set(), scriptErrors = new Set();
    const mainUrl = pathToFileURL(source).href;
    await context.route('**/*', async route => {
      const request = route.request();
      if (request.url() !== mainUrl && !/^(data:|blob:)/.test(request.url())) resources.add(request.url());
      if (/^(file:|data:|blob:)/.test(request.url())) await route.continue();
      else await route.abort('blockedbyclient');
    });
    page.on('request', request => { if (request.url() !== mainUrl && !/^(data:|blob:)/.test(request.url())) resources.add(request.url()); });
    page.on('requestfailed', request => failures.add(`${request.url()}: ${request.failure()?.errorText}`));
    page.on('pageerror', error => scriptErrors.add(error.message));
    page.on('dialog', dialog => { scriptErrors.add(`unexpected ${dialog.type()} dialog`); void dialog.dismiss(); });
    try {
      await page.goto(mainUrl, { waitUntil: 'load' });
      await page.evaluate(axeSource);
      await page.addStyleTag({ content: '*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}' });
      await capture(page, name, 'default');
      const details = await page.locator('details:not([open])').count();
      if (details) {
        const exclusive = await page.locator('details[name]').count();
        if (exclusive) add('exclusive-details', 'unsupported', 'named details groups need separate manual inspection', { view: name });
        await page.locator('details:not([name])').evaluateAll(es => es.forEach(e => e.open = true));
        await capture(page, name, 'expanded');
      }
      add('loaded-assets', resources.size ? 'fail' : 'pass', resources.size ? [...resources].join('\n') : 'no non-inline resources loaded', { view: name });
      add('resource-loads', failures.size ? 'fail' : 'pass', failures.size ? [...failures].join('\n') : 'no failed resource requests', { view: name });
      add('page-scripts', scriptErrors.size ? 'fail' : 'pass', scriptErrors.size ? [...scriptErrors].join('\n') : 'no uncaught page errors', { view: name });
    } finally { await context.close(); }
  }
}

(async () => {
  try {
    if (!argumentsFor(process.argv.slice(2))) {
      console.log('usage: check-render.sh REPORT [--output-dir DIR] [--timeout MS] [--browser PATH] [--widths 375,1280] [--theme dark|light|both] [--geometry]');
      return;
    }
    output = path.resolve(options['output-dir'] || path.dirname(source));
    basename = path.basename(source, path.extname(source));
    await fs.mkdir(output, { recursive: true });
    run = await fs.mkdtemp(path.join(output, `${basename}.render-`));
    const bytes = await fs.readFile(source);
    result.source = { path: source, sha256: hash(bytes), bytes: bytes.length };
    result.startedAt = new Date(started).toISOString();
    const text = bytes.toString('utf8');
    add('file-size', bytes.length > 150 * 1024 ? 'fail' : 'pass', `${bytes.length} bytes; limit 153600`);
    add('build-placeholders', /MERMAID-LIB-HERE|MERMAID_PLACEHOLDER/.test(text) ? 'fail' : 'pass', 'unresolved diagram placeholders');
    add('source-dashes', /[\u2013\u2014]|&(?:m|n)dash;|&#0*(?:8211|8212);|&#x0*(?:2013|2014);/i.test(text) ? 'fail' : 'pass', 'source bytes and encoded dash entities');
    let chromium;
    try { ({ chromium } = require('playwright-core')); axeSource = require('axe-core').source; }
    catch { throw new Error(`missing dependency; run npm ci --prefix ${__dirname} --ignore-scripts --no-audit --no-fund`); }
    result.browserPath = await findBrowser();
    browser = await chromium.launch({ executablePath: result.browserPath, headless: true, timeout: Math.min(15000, options.timeout) });
    result.browserVersion = browser.version();
    let timer;
    try {
      await Promise.race([inspectViews(), new Promise((_, reject) => { timer = setTimeout(() => reject(new Error(`render timeout: deadline exceeded (${options.timeout}ms)`)), options.timeout); })]);
    } finally { clearTimeout(timer); await browser.close(); browser = null; }
    for (const light of result.views.filter(v => v.theme === 'light')) {
      const dark = result.views.find(v => v.theme === 'dark' && v.width === light.width && v.state === light.state);
      const equal = dark && JSON.stringify(light.layout) === JSON.stringify(dark.layout);
      add('theme-layout', equal ? 'pass' : 'fail', `light and dark layout ${equal ? 'matches' : 'differs'} at ${light.width}px (${light.state})`);
    }
    const finalHash = hash(await fs.readFile(source));
    if (finalHash !== result.source.sha256) throw new Error('source changed during verification; rerun against the final version');
  } catch (error) { result.errors.push(error.message); }
  finally { if (browser) await browser.close().catch(() => {}); }
  await finish();
})().catch(error => { console.error(`ERROR: ${error.message}`); process.exitCode = 2; });
