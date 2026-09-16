import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir, realpath, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { inflateSync } from 'node:zlib';

const here = path.dirname(fileURLToPath(import.meta.url));
const candidate = path.dirname(here);
const outputRoot = process.env.ACCEPTANCE_OUTPUT || path.resolve(candidate, '../test-output');
const entry = process.env.CHECK_RENDER_ENTRY || path.join(candidate, 'scripts/check-render.sh');
const fixtures = path.join(here, 'fixtures');
const results = [];
const runs = [];
let serial = 0;
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const describeChecks = result => JSON.stringify(result.checks || []);
const imagePath = (run, image) => path.isAbsolute(image.path) ? image.path : path.resolve(run.output, image.path);

async function assertion(name, fn) {
  try {
    await fn();
    results.push({ name, status: 'pass' });
    process.stdout.write(`PASS ${name}\n`);
  } catch (error) {
    results.push({ name, status: 'fail', error: error.message });
    process.stdout.write(`FAIL ${name}: ${error.message}\n`);
  }
}

async function runFixture(name, options = [], sharedOutput) {
  const source = path.join(fixtures, name);
  const original = await readFile(source);
  const output = sharedOutput || path.join(outputRoot, `${String(++serial).padStart(2, '0')}-${path.parse(name).name}`);
  await mkdir(output, { recursive: true });
  const started = Date.now();
  const processResult = await new Promise((resolve, reject) => {
    const child = spawn('bash', [entry, source, '--output-dir', output, ...options], { cwd: candidate, stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => { child.kill('SIGKILL'); }, 120000);
    child.stdout.on('data', data => { stdout += data; });
    child.stderr.on('data', data => { stderr += data; });
    child.on('error', error => { clearTimeout(timer); reject(error); });
    child.on('close', (code, signal) => { clearTimeout(timer); resolve({ code, signal, stdout, stderr }); });
  });
  const latest = path.join(output, `${path.parse(name).name}.render.json`);
  let result;
  let resultPath;
  let readError;
  try {
    const reported = processResult.stdout.match(/^json:\s*(.+)$/m)?.[1]?.trim();
    resultPath = await realpath(reported || latest);
    result = JSON.parse(await readFile(resultPath, 'utf8'));
  } catch (error) { readError = error.message; }
  const run = { name, source, output, started, durationMs: Date.now() - started, resultPath, result, readError, ...processResult, originalHash: hash(original), afterHash: hash(await readFile(source)) };
  runs.push(run);
  await writeFile(path.join(output, `process-${started}-${Math.random().toString(16).slice(2)}.json`), JSON.stringify({ name, options, ...processResult }, null, 2));
  return run;
}

async function contract(run) {
  await assertion(`${run.name}: JSON emitted with process exit contract`, () => {
    assert.ok(run.result, `${run.readError || 'missing JSON'}; stderr=${run.stderr.slice(-800)}`);
    assert.ok([0, 1, 2].includes(run.code), `exit ${run.code}; signal ${run.signal}`);
    assert.equal(run.result.exitCode, run.code);
    assert.equal(run.result.status, ['pass', 'fail', 'error'][run.code]);
    assert.ok(Array.isArray(run.result.checks));
    assert.ok(Array.isArray(run.result.errors));
    for (const check of run.result.checks) assert.ok(['pass', 'fail', 'warn', 'unsupported'].includes(check.status));
  });
  await assertion(`${run.name}: source hash and contents preserved`, () => {
    assert.equal(run.afterHash, run.originalHash);
    assert.equal(run.result?.source?.sha256, run.originalHash);
    assert.equal(run.result?.source?.path, run.source);
  });
  if (run.result?.views?.length) await assertion(`${run.name}: real positive viewport and document measurements`, () => {
    for (const view of run.result.views) {
      for (const key of ['width', 'height', 'pageWidth', 'pageHeight']) assert.ok(Number.isFinite(view[key]) && view[key] > 0, `${view.name}.${key}=${view[key]}`);
      assert.ok(['light', 'dark'].includes(view.theme));
      assert.ok(['default', 'expanded'].includes(view.state));
    }
  });
}

async function png(file) {
  const bytes = await readFile(file);
  assert.equal(bytes.subarray(0, 8).toString('hex'), '89504e470d0a1a0a');
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  const bitDepth = bytes[24];
  const colorType = bytes[25];
  let offset = 8;
  const data = [];
  while (offset < bytes.length) {
    const length = bytes.readUInt32BE(offset);
    const type = bytes.toString('ascii', offset + 4, offset + 8);
    if (type === 'IDAT') data.push(bytes.subarray(offset + 8, offset + 8 + length));
    offset += length + 12;
  }
  assert.equal(bitDepth, 8);
  assert.ok([2, 6].includes(colorType), `unsupported PNG color type ${colorType}`);
  const raw = inflateSync(Buffer.concat(data));
  return { width, height, firstPixel: [...raw.subarray(1, 4)] };
}

async function test(name, options, fn) {
  const run = await runFixture(name, options);
  await contract(run);
  await fn(run);
  return run;
}

await mkdir(outputRoot, { recursive: true });
try {
  await test('clean.html', [], async run => {
    await assertion('clean local report exits 0', () => assert.equal(run.code, 0, describeChecks(run.result)));
    await assertion('selected-theme legacy screenshot aliases resolve to existing PNG files', async () => {
      for (const alias of ['clean.wide.png', 'clean.narrow.png']) assert.ok((await stat(path.join(run.output, alias))).size > 0);
    });
  });
  for (const name of ['overflow.html', 'missing-body.html', 'relative-style.html']) {
    await test(name, [], async run => {
      await assertion(`${name}: overflow returns confirmed defect`, () => assert.equal(run.code, 1));
      await assertion(`${name}: actual narrow dimensions prove overflow`, () => assert.ok(run.result?.views?.some(view => view.width === 500 && view.pageWidth >= (name === 'relative-style.html' ? 1450 : 1600))));
      if (name === 'relative-style.html') await assertion('relative stylesheet dependency is reported', () => assert.match(describeChecks(run.result), /layout\.css/));
    });
  }
  await test('navigation.html', [], async run => {
    await assertion('navigational script and stylesheet links remain clean', () => assert.equal(run.code, 0, describeChecks(run.result)));
  });
  await test('assets.html', [], async run => {
    await assertion('loaded file dependencies produce a nonzero result', () => assert.ok([1, 2].includes(run.code)));
    for (const asset of ['assets.css', 'asset.js', 'picture.svg', 'import.css', 'background.svg', 'broken.woff2']) {
      await assertion(`resource dependency recorded: ${asset}`, () => assert.ok(JSON.stringify(run.result).includes(asset)));
    }
  });
  for (const name of ['missing-image.html', 'script-error.html']) {
    await test(name, [], async run => {
      await assertion(`${name}: failure is explicit and nonzero`, () => {
        assert.ok([1, 2].includes(run.code));
        assert.match(JSON.stringify(run.result), name === 'script-error.html' ? /acceptance-script-error/ : /absent\.png/);
      });
    });
  }
  await test('clean.html', ['--browser', '/nonexistent/acceptance-browser'], async run => {
    await assertion('missing browser exits 2 with a recorded execution error', () => {
      assert.equal(run.code, 2);
      assert.ok(run.result?.errors?.length > 0);
      assert.match(JSON.stringify(run.result.errors), /browser|chrome|executable/i);
    });
  });
  await test('timeout.html', ['--timeout', '1000'], async run => {
    await assertion('blocked page times out with exit 2 within 20 seconds', () => {
      assert.equal(run.code, 2);
      assert.ok(run.durationMs < 20000, `duration ${run.durationMs}ms`);
      assert.match(JSON.stringify(run.result?.errors), /timeout|timed out/i);
    });
  });
  await test('long-theme.html', ['--widths', '375,1280', '--theme', 'both'], async run => {
    await assertion('long responsive document remains mechanically clean', () => assert.equal(run.code, 0));
    for (const [name, width, theme, pixel] of [['wide-light', 820, 'light', 250], ['wide-dark', 820, 'dark', 17], ['narrow-light', 500, 'light', 250], ['narrow-dark', 500, 'dark', 17], ['width-375-light', 375, 'light', 250], ['width-375-dark', 375, 'dark', 17], ['width-1280-light', 1280, 'light', 250], ['width-1280-dark', 1280, 'dark', 17]]) {
      await assertion(`${name}: fixed 900px viewport, complete 2700px PNG, actual theme pixel`, async () => {
        const view = run.result?.views?.find(view => view.name === name && view.state === 'default');
        assert.ok(view, `missing ${name}`);
        assert.equal(view.width, width);
        assert.equal(view.height, 900);
        assert.equal(view.theme, theme);
        assert.equal(view.pageHeight, 2700);
        const full = view.images.find(image => image.kind === 'full');
        assert.ok(full, 'full image missing');
        const info = await png(imagePath(run, full));
        assert.equal(info.width, width);
        assert.equal(info.height, 2700);
        assert.deepEqual(info.firstPixel, [pixel, pixel, pixel]);
        const detail = view.images.filter(image => image.kind === 'tile');
        assert.ok(detail.length >= 3, 'readable full-page coverage requires at least three 900px tiles');
        for (const image of detail) assert.ok((await png(imagePath(run, image))).height <= 1800);
      });
    }
  });
  await test('expanded.html', [], async run => {
    await assertion('expanded details are measured and hidden overflow becomes a defect', () => {
      assert.equal(run.code, 1);
      assert.ok(run.result?.views?.some(view => view.state === 'expanded' && view.width === 500 && view.pageWidth >= 1400));
    });
  });
  await test('scroll-diagram.html', [], async run => {
    await assertion('scroll-container keeps page width bounded and captures offscreen content', () => {
      assert.equal(run.code, 0, describeChecks(run.result));
      const narrow = run.result?.views?.filter(view => view.width === 500);
      assert.ok(narrow?.length > 0);
      assert.ok(narrow.every(view => view.pageWidth <= 500));
      assert.ok(narrow.some(view => view.images.some(image => image.kind === 'scroll')));
    });
  });
    await assertion('expanded capture resets document scroll and preserves fixed marker position', async () => {
      const run = runs.find(run => run.name === 'scroll-diagram.html');
      const result = JSON.parse(await readFile(run.resultPath, 'utf8'));
      assert.equal(result.views.filter(view => view.state === 'expanded').length, 4);
      for (const view of result.views.filter(view => view.images.length)) {
        const full = view.images.find(image => image.kind === 'full');
        assert.deepEqual((await png(full.path)).firstPixel, [255, 0, 0], view.name + ' ' + view.state);
      }
    });
  await test('light-contrast.html', [], async run => {
    await assertion('default capture is dark only but light-only contrast failure returns exit 1', () => {
      assert.equal(run.code, 1);
      assert.deepEqual(run.result.captureThemes, ['dark']);
      assert.equal(run.result.views.filter(view => view.images.length).length, 2);
      assert.ok(run.result.views.filter(view => view.theme === 'light').every(view => view.images.length === 0));
      assert.ok(run.result.checks.some(c => c.name === 'color-contrast' && c.status === 'fail' && c.view.endsWith('light')));
      assert.ok(!run.result.checks.some(c => c.name === 'color-contrast' && c.status === 'fail' && c.view.endsWith('dark')));
    });
  });
  await test('dark-contrast.html', ['--theme', 'light'], async run => {
    await assertion('light capture still detects dark-only contrast failure without dark screenshots', () => {
      assert.equal(run.code, 1);
      assert.deepEqual(run.result.captureThemes, ['light']);
      assert.ok(run.result.views.filter(view => view.theme === 'dark').every(view => view.images.length === 0));
      assert.ok(run.result.checks.some(c => c.name === 'color-contrast' && c.status === 'fail' && c.view.endsWith('dark')));
    });
  });
  await test('theme-layout.html', [], async run => {
    await assertion('theme-specific font and layout change is a deterministic failure', () => {
      assert.equal(run.code, 1);
      assert.ok(run.result.checks.some(c => c.name === 'theme-layout' && c.status === 'fail'));
    });
  });
  await test('report with spaces.html', [], async run => {
    await assertion('source path containing spaces is captured successfully', () => assert.equal(run.code, 0));
  });
  for (const [name, pattern] of [['placeholder.html', /placeholder/i], ['dash-entity.html', /dash/i], ['oversize.html', /size|150/i]]) {
    await test(name, [], async run => {
      await assertion(`${name}: retained static check returns defect`, () => {
        assert.equal(run.code, 1);
        assert.ok(run.result?.checks?.some(check => check.status === 'fail' && pattern.test(JSON.stringify(check))));
      });
    });
  }
  for (const [name, pattern] of [['clipped-label.html', /clip/i], ['straight-crossing.html', /cross|intersect|connector|edge/i], ['straight-path.html', /cross|intersect|connector|edge/i], ['label-overlap.html', /overlap|collision|intersect/i]]) {
    await test(name, ['--geometry'], async run => {
      await assertion(`${name}: supported geometry warning includes evidence image`, async () => {
        assert.equal(run.code, 0, describeChecks(run.result));
        assert.ok(run.result?.checks?.some(check => check.status === 'warn' && pattern.test(JSON.stringify(check))), describeChecks(run.result));
        const images = run.result?.views?.flatMap(view => view.images).filter(image => image.kind === 'warning');
        assert.ok(images?.length > 0, 'warning crop missing');
        for (const image of images) assert.ok((await stat(imagePath(run, image))).size > 0);
      });
    });
  }
  for (const name of ['node-label.html', 'intentional-overlap.html', 'hidden-edge.html']) {
    await test(name, ['--geometry'], async run => {
      await assertion(`${name}: intended containment or overlap has no false positive`, () => {
        assert.equal(run.code, 0);
        assert.ok(!run.result?.checks?.some(check => check.status === 'warn'), describeChecks(run.result));
      });
    });
  }
  await test('curved-edge.html', ['--geometry'], async run => {
    await assertion('curved-edge bounding rectangle does not produce a crossing claim', () => {
      assert.equal(run.code, 0);
      assert.ok(!run.result?.checks?.some(check => check.status === 'warn' && /cross|intersect|collision/i.test(JSON.stringify(check))), describeChecks(run.result));
      assert.ok(run.result?.checks?.some(check => check.status === 'unsupported' && /curve|path/i.test(JSON.stringify(check))), describeChecks(run.result));
    });
  });
  const concurrentOutput = path.join(outputRoot, 'concurrent');
  const concurrent = await Promise.all([runFixture('clean.html', [], concurrentOutput), runFixture('clean.html', [], concurrentOutput)]);
  for (let index = 0; index < concurrent.length; index++) await contract(concurrent[index]);
  await assertion('concurrent runs preserve distinct immutable image files', async () => {
    assert.ok(concurrent.every(run => run.code === 0));
    const first = concurrent[0].result.views.flatMap(view => view.images).map(image => imagePath(concurrent[0], image));
    const second = concurrent[1].result.views.flatMap(view => view.images).map(image => imagePath(concurrent[1], image));
    assert.ok(first.length >= 2 && second.length >= 2);
    assert.notEqual(concurrent[0].resultPath, concurrent[1].resultPath, 'two runs point to the same JSON artifact');
    assert.ok(!first.some(image => second.includes(image)), 'two runs point to the same image artifacts');
    for (const image of [...first, ...second]) assert.ok((await stat(image)).size > 0);
  });
  await assertion('concurrent source hash agrees with current source', async () => {
    const expected = hash(await readFile(path.join(fixtures, 'clean.html')));
    for (const run of concurrent) assert.equal(run.result.source.sha256, expected);
  });
} catch (error) {
  results.push({ name: 'acceptance runner completed', status: 'fail', error: error.stack });
  process.stderr.write(`${error.stack}\n`);
} finally {
  const report = { entry, createdAt: new Date().toISOString(), assertions: results, runs: runs.map(({ stdout, stderr, result, ...run }) => ({ ...run, status: result?.status })) };
  await writeFile(path.join(outputRoot, 'acceptance-results.json'), JSON.stringify(report, null, 2));
  const failed = results.filter(result => result.status === 'fail');
  process.stdout.write(`${results.length - failed.length}/${results.length} assertions passed; ${runs.length} checker invocations\n`);
  process.exitCode = failed.length ? 1 : 0;
}
