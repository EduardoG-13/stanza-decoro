// models3d behaviour checks on the BUILT site (dist/ served through Playwright page.route).
//   node scripts/models3d/behaviour.mjs <modelId> <outDir> [--dist dist]
// For the given registered model (and, as regression, the default EXT-001 model) it drives the
// real configurator page (/explorar-sofa.html[?modelo=<id>]) and the viewer API directly:
// poster/options/quote before intent, no GLB before the click, only that model's GLB after it,
// UI finish change, fast switching (last request wins), texture failure + retry, return to the
// initial (embedded) finish with pixel equality, fixed decorative/structure materials, resize,
// dispose (canvas removed, poster restored), console errors; plus the product-page "Ver em 3D"
// entry, the unknown-model fallback and that the home never requests the 3D collection.
// Writes <outDir>/behaviour.json and a few screenshots. Exit code 1 if any check fails.
import fs from 'node:fs';
import path from 'node:path';
import { launch, serveDist, harness } from './capture.mjs';

const args = process.argv.slice(2);
const modelId = args[0], OUT = path.resolve(args[1] || 'behaviour-out');
const dist = path.resolve(args.includes('--dist') ? args[args.indexOf('--dist') + 1] : 'dist');
fs.mkdirSync(OUT, { recursive: true });
const registry = JSON.parse(fs.readFileSync(path.join(dist, 'assets/models-3d.json'), 'utf8'));
const browser = await launch();
const report = { modelId, checks: [], runs: {} };
const same = (a, b) => JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());
const check = (name, ok, detail) => { report.checks.push({ name, ok: !!ok, detail }); if (!ok) console.log('FAIL', name, JSON.stringify(detail)); };

async function open(url, viewport, opts = {}) {
  const ctx = await browser.newContext({ viewport, reducedMotion: opts.reducedMotion || 'no-preference' });
  const page = await ctx.newPage(); const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push('PAGEERROR ' + e.message));
  const served = serveDist(page, dist, { abortOnce: opts.abortOnce, virtual: opts.virtual });
  await page.goto('https://local.test' + url, { waitUntil: 'load' });
  return { ctx, page, errors, ...served };
}
const pick = async (page, name, value) => page.evaluate(([n, v]) => { const i = document.querySelector(`input[name="${n}"][value="${v}"]`); i.checked = true; i.dispatchEvent(new Event('change', { bubbles: true })); }, [name, value]);
const waitStatus = (page, re) => page.waitForFunction(r => new RegExp(r).test(document.querySelector('#sofa-status').textContent), re.source, { timeout: 90000 });
const canvasPng = async (page, file) => { const b = await page.locator('#sofa-stage canvas').screenshot(); if (file) fs.writeFileSync(path.join(OUT, file), b); return b; };

async function configurator(model, variant) {
  const vp = variant === 'main' ? { width: 1280, height: 900 } : { width: 390, height: 780 };
  const isDefault = model.modelId === registry.defaultModelId;
  const url = isDefault ? '/explorar-sofa.html' : '/explorar-sofa.html?modelo=' + model.modelId;
  const { ctx, page, errors, requests, abortOnce } = await open(url, vp);
  const tag = `${model.modelId}/${variant}`; const r = {};
  r.before = await page.evaluate(() => ({
    poster: document.querySelector('#sofa-stage img').getAttribute('src'), stage: document.querySelector('#sofa-stage').dataset.modelId,
    crumb: document.querySelector('[data-model-crumb]')?.textContent, product: document.querySelector('[data-model-product]')?.getAttribute('href'),
    fabrics: [...document.querySelectorAll('input[name="sofa-fabric"]')].filter(i => !i.closest('label').hidden).map(i => i.value),
    colors: [...document.querySelectorAll('input[name="sofa-color"]')].filter(i => !i.closest('label').hidden).map(i => i.value),
    checked: [document.querySelector('input[name="sofa-fabric"]:checked')?.value, document.querySelector('input[name="sofa-color"]:checked')?.value],
    quote: document.querySelector('#sofa-quote').getAttribute('href'),
    layers: document.querySelectorAll('#sofa-layers,#sofa-progress,[data-progress],.sofa-step-options,.sofa-layer-key').length }));
  check(`${tag}: poster/identity before intent`, r.before.poster === model.assets.poster && r.before.stage === model.modelId && r.before.product === (model.productPage || `/modelos/${model.catalogId}.html`), r.before);
  check(`${tag}: only the model's options are offered, default checked`, same(r.before.fabrics, model.options.fabrics) && same(r.before.colors, model.options.colors) && r.before.checked[0] === model.options.default.fabricId && r.before.checked[1] === model.options.default.colorId, r.before);
  check(`${tag}: quote referencia before intent`, r.before.quote.includes('referencia=' + model.catalogId), r.before.quote);
  check(`${tag}: no layer controls`, r.before.layers === 0, r.before.layers);
  check(`${tag}: no GLB before user intent`, requests.filter(p => p.endsWith('.glb')).length === 0, requests.filter(p => p.endsWith('.glb')));
  await page.click('#start-sofa');
  await page.waitForFunction(() => document.querySelector('#sofa-stage').classList.contains('is-ready'), null, { timeout: 120000 });
  const glbs = requests.filter(p => p.endsWith('.glb'));
  check(`${tag}: only this model's ${variant} GLB is loaded`, glbs.length === 1 && glbs[0] === model.assets[variant], glbs);
  await page.click('[data-view="photo"]'); await page.waitForTimeout(250);
  const initialPng = await canvasPng(page, `${model.modelId}_${variant}_initial_photo.png`);
  // UI finish change
  await pick(page, 'sofa-color', 'grafite'); await waitStatus(page, /atualizada/);
  const afterGrafite = await page.evaluate(() => ({ name: document.querySelector('#sofa-selection-name').textContent, quote: document.querySelector('#sofa-quote').getAttribute('href') }));
  check(`${tag}: colour change updates selection + quote`, afterGrafite.quote.includes('cor=grafite') && afterGrafite.quote.includes('referencia=' + model.catalogId) && afterGrafite.quote.includes('estudo=' + model.modelId), afterGrafite);
  await canvasPng(page, `${model.modelId}_${variant}_grafite_photo.png`);
  // fast switching: last request wins
  const seq = model.options.colors.filter(c => c !== 'grafite').slice(0, 3);
  for (const c of seq) await pick(page, 'sofa-color', c);
  await page.waitForTimeout(400); await waitStatus(page, /atualizada/);
  const last = await page.evaluate(() => document.querySelector('#sofa-quote').getAttribute('href'));
  check(`${tag}: fast switch keeps the last request`, last.includes('cor=' + seq.at(-1)), { seq, last });
  // texture failure then retry (abort the first normal map of a not-yet-loaded fabric)
  const other = model.options.fabrics.find(f => f !== model.options.default.fabricId);
  const folder = registry.materialLibrary[other] || model.assets.viewerBase + 'materials/' + other + '/';
  abortOnce.add(folder + 'normal.png');
  await pick(page, 'sofa-fabric', other);
  await page.waitForFunction(() => document.querySelector('#sofa-status').classList.contains('is-error'), null, { timeout: 60000 });
  const failed = await page.evaluate(() => ({ status: document.querySelector('#sofa-status').textContent, checked: document.querySelector('input[name="sofa-fabric"]:checked').value, quote: document.querySelector('#sofa-quote').getAttribute('href') }));
  check(`${tag}: failed texture keeps the last good selection`, failed.checked === model.options.default.fabricId && failed.quote.includes('tecido=' + model.options.default.fabricId), failed);
  await pick(page, 'sofa-fabric', other); await waitStatus(page, /atualizada/);
  const retried = await page.evaluate(() => document.querySelector('#sofa-quote').getAttribute('href'));
  check(`${tag}: retry after failure works`, retried.includes('tecido=' + other), retried);
  // return to the initial finish -> embedded maps, identical pixels
  await pick(page, 'sofa-fabric', model.options.default.fabricId); await pick(page, 'sofa-color', model.options.default.colorId); await waitStatus(page, /atualizada/);
  await page.click('[data-view="photo"]'); await page.waitForTimeout(250);
  const backPng = await canvasPng(page, `${model.modelId}_${variant}_back_initial_photo.png`);
  check(`${tag}: return to the initial finish is pixel-identical`, Buffer.compare(initialPng, backPng) === 0, { bytes: [initialPng.length, backPng.length] });
  // resize
  const c0 = await page.evaluate(() => [document.querySelector('#sofa-stage canvas').width, document.querySelector('#sofa-stage canvas').height]);
  await page.setViewportSize({ width: vp.width === 1280 ? 1000 : 360, height: vp.height }); await page.waitForTimeout(400);
  const c1 = await page.evaluate(() => [document.querySelector('#sofa-stage canvas').width, document.querySelector('#sofa-stage canvas').height]);
  check(`${tag}: canvas follows resize`, c0[0] !== c1[0], { c0, c1 });
  // the single deliberately aborted texture request logs one net::ERR_FAILED; nothing else is allowed
  const unexpected = errors.filter((e, i) => !(i === errors.findIndex(x => /net::ERR_FAILED/.test(x)) && /net::ERR_FAILED/.test(e)));
  r.errors = errors; check(`${tag}: console errors = 0 (besides the 1 intentional aborted texture)`, unexpected.length === 0, errors);
  report.runs[tag] = r; await ctx.close();
}

async function api(model) {
  // direct viewer API (same module as the site) for identity, regions, last-wins and dispose
  const { ctx, page, errors } = await open(`/__api.html?model=${model.modelId}&variant=main`, { width: 900, height: 675 }, { virtual: { '/__api.html': () => harness(900, 675) } });
  await page.waitForFunction(() => window.__ready, null, { timeout: 120000 });
  const tag = `${model.modelId}/api`;
  const res = await page.evaluate(async (m) => {
    const V = window.__viewer; const out = {};
    const i0 = V.inspect(); out.identity = [i0.modelId, i0.revision]; out.views = i0.views; out.options = i0.options; out.construction = i0.construction;
    const fixed = i => i.materialRegions.filter(x => x.region !== 'body').map(x => [x.name, x.color, x.map, x.stanzaFabric]);
    out.fixed0 = fixed(i0);
    out.body = i0.materialRegions.filter(x => x.stanzaFabric).map(x => x.name).sort();
    const colors = m.options.colors; const fabrics = m.options.fabrics;
    const pending = [V.setFinish({ colorId: colors[1] }), V.setFinish({ fabricId: fabrics[1], colorId: colors[2] }), V.setFinish({ fabricId: fabrics[0], colorId: colors.at(-1) })];
    out.results = (await Promise.allSettled(pending)).map(p => p.value);
    out.final = V.getSelection();
    out.fixed1 = fixed(V.inspect());
    try { await V.setFinish({ colorId: 'nao-existe' }); out.invalid = 'accepted'; } catch (e) { out.invalid = e.name; }
    const foreign = ['boucle', 'linen', 'velvet', 'boucle-mescla'].find(f => !fabrics.includes(f));
    if (foreign) { try { await V.setFinish({ fabricId: foreign }); out.foreign = 'accepted'; } catch (e) { out.foreign = e.name; } }
    V.dispose(); V.dispose();
    const i2 = V.inspect(); out.disposed = i2.disposed; out.canvasLeft = document.querySelectorAll('#stage canvas').length;
    try { await V.setFinish({ colorId: colors[0] }); out.afterDispose = 'accepted'; } catch (e) { out.afterDispose = e.message; }
    return out;
  }, model);
  check(`${tag}: identity matches registry`, res.identity[0] === model.modelId && res.identity[1] === model.revision, res.identity);
  check(`${tag}: exterior-only + body materials`, res.construction === 'exterior-only' && JSON.stringify(res.body) === JSON.stringify(model.materialRegions.body.slice().sort()), { c: res.construction, body: res.body });
  check(`${tag}: presets`, ['photo', 'front', 'threequarter', 'side', 'detail'].every(v => res.views.includes(v)), res.views);
  check(`${tag}: last request wins`, res.final.colorId === model.options.colors.at(-1) && res.final.fabricId === model.options.fabrics[0] && res.final.modelId === model.modelId, { final: res.final, results: res.results });
  check(`${tag}: decorative/structure materials untouched by setFinish`, JSON.stringify(res.fixed0) === JSON.stringify(res.fixed1), { fixed0: res.fixed0 });
  check(`${tag}: invalid / non-exposed option rejected`, res.invalid === 'RangeError' && (res.foreign === undefined || res.foreign === 'RangeError'), { invalid: res.invalid, foreign: res.foreign });
  check(`${tag}: dispose idempotent, canvas removed, API closed`, res.disposed === true && res.canvasLeft === 0 && /desmontado/.test(res.afterDispose), res);
  check(`${tag}: console errors = 0`, errors.length === 0, errors);
  report.runs[tag] = res; await ctx.close();
}

async function pages() {
  for (const m of registry.models) {
    const { ctx, page } = await open(`/modelos/${m.catalogId}.html`, { width: 1280, height: 900 });
    const link = await page.evaluate(() => [...document.querySelectorAll('[data-model-3d]')].map(a => [a.dataset.model3d, a.getAttribute('href'), a.textContent.trim()]));
    const photo = await page.evaluate(() => !!document.querySelector('img[data-model-image]'));
    const expected = m.modelId === registry.defaultModelId ? '/explorar-sofa.html' : '/explorar-sofa.html?modelo=' + m.modelId;
    check(`product page ${m.catalogId}: "Ver em 3D" -> ${expected}, photo kept`, link.length === 1 && link[0][1] === expected && photo, link);
    await ctx.close();
  }
  const other = (await (async () => { const c = JSON.parse(fs.readFileSync('data/catalog.json', 'utf8')); return c.find(x => !registry.models.some(m => m.catalogId === x.id)); })());
  { const { ctx, page } = await open(`/modelos/${other.id}.html`, { width: 1280, height: 900 }); check(`product page ${other.id}: no 3D entry (not registered)`, (await page.$$('[data-model-3d]')).length === 0); await ctx.close(); }
  { const { ctx, page, requests, errors } = await open('/explorar-sofa.html?modelo=nao-registrado', { width: 1280, height: 900 });
    await page.waitForTimeout(300);
    const st = await page.evaluate(() => ({ start: document.querySelector('#start-sofa').hidden, status: document.querySelector('#sofa-status').textContent, poster: document.querySelector('#sofa-stage img').hidden, quote: document.querySelector('#sofa-quote').getAttribute('href') }));
    check('unknown model: no 3D, no other piece, no GLB', st.start && st.poster && /não está disponível/.test(st.status) && st.quote === '/orcamento.html' && !requests.some(p => p.endsWith('.glb')), { st, errors });
    await ctx.close(); }
  { const { ctx, page, requests } = await open('/index.html', { width: 1280, height: 900 });
    await page.waitForTimeout(4000);
    const r3 = requests.filter(p => p.includes('/assets/models-3d'));
    const glb = requests.filter(p => p.endsWith('.glb'));
    check('home: never requests the 3D collection; only the organic sofa', r3.length === 0 && glb.every(p => p.startsWith('/assets/sofa-pilot/models/')), { r3, glb });
    await ctx.close(); }
}

const target = registry.models.find(m => m.modelId === modelId);
const def = registry.models.find(m => m.modelId === registry.defaultModelId);
for (const m of [target, ...(def.modelId !== target.modelId ? [def] : [])]) {
  for (const v of ['main', 'mobile']) await configurator(m, v);
  await api(m);
}
await pages();
await browser.close();
report.passed = report.checks.every(c => c.ok);
report.summary = { total: report.checks.length, failed: report.checks.filter(c => !c.ok).length };
fs.writeFileSync(path.join(OUT, 'behaviour.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report.summary), report.passed ? 'PASS' : 'FAIL');
process.exit(report.passed ? 0 : 1);
