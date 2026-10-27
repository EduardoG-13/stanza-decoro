// Framing check on the REAL configurator page (dist/explorar-sofa.html[?modelo=<id>]).
//   node scripts/models3d/framing.mjs <outDir> [--dist dist] [--viewer <alt sofa-viewer.js>] [--models a,b] [--views]
// For every registered model and two viewports (desktop 1440x900, phone 390x844) it clicks the
// start button, waits for the viewer and, WITHOUT pressing any view, measures where the piece lands:
// every mesh vertex is projected with the live camera; the normalised screen bbox (0..1) tells
// whether the piece is cropped (outside 0..1), off-centre or too small. With --views it also
// clicks every view button. --viewer serves another viewer module (e.g. the previous revision)
// to document the "before" behaviour. Writes <out>/framing.json and stage screenshots.
import fs from 'node:fs';
import path from 'node:path';
import { launch, MIME } from './capture.mjs';

const args = process.argv.slice(2);
const OUT = path.resolve(args[0] || 'framing-out');
const opt = k => args.includes(k) ? args[args.indexOf(k) + 1] : null;
const dist = path.resolve(opt('--dist') || 'dist');
const altViewer = opt('--viewer');
const withViews = args.includes('--views');
fs.mkdirSync(OUT, { recursive: true });
const registry = JSON.parse(fs.readFileSync(path.join(dist, 'assets/models-3d.json'), 'utf8'));
const only = opt('--models')?.split(',');
const models = registry.models.filter(m => !only || only.includes(m.modelId));
const SIZES = { desktop: { width: 1440, height: 900 }, phone: { width: 390, height: 844 } };
// Expose the live camera and model root to the page (measurement only, never shipped).
const hook = src => src.replace('return api;', 'window.__framing = { camera, root: loadedRoot, THREE }; return api;');

const browser = await launch();
const results = [];
async function measure(page) {
  return page.evaluate(() => {
    const { camera, root, THREE } = window.__framing; root.updateMatrixWorld(true); camera.updateMatrixWorld();
    const v = new THREE.Vector3(); let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
    root.traverse(n => {
      if (!n.isMesh) return; const pos = n.geometry.attributes.position;
      for (let i = 0; i < pos.count; i += 3) {
        v.fromBufferAttribute(pos, i).applyMatrix4(n.matrixWorld).project(camera);
        x0 = Math.min(x0, v.x); x1 = Math.max(x1, v.x); y0 = Math.min(y0, v.y); y1 = Math.max(y1, v.y);
      }
    });
    // screen space 0..1, y down
    const box = { left: (x0 + 1) / 2, right: (x1 + 1) / 2, top: (1 - y1) / 2, bottom: (1 - y0) / 2 };
    const r = k => +k.toFixed(3);
    return { left: r(box.left), right: r(box.right), top: r(box.top), bottom: r(box.bottom),
      width: r(box.right - box.left), height: r(box.bottom - box.top), cx: r((box.left + box.right) / 2), cy: r((box.top + box.bottom) / 2),
      dist: r(camera.position.distanceTo(new THREE.Vector3())), fov: r(camera.fov), aspect: r(camera.aspect) };
  });
}
const verdict = m => {
  const cropped = m.left < 0 || m.right > 1 || m.top < 0 || m.bottom > 1;
  const tiny = Math.max(m.width, m.height) < .5;
  const offCentre = Math.abs(m.cx - .5) > .12 || Math.abs(m.cy - .5) > .18;
  return { ok: !cropped && !tiny && !offCentre, cropped, tiny, offCentre };
};
for (const model of models) {
  for (const [size, viewport] of Object.entries(SIZES)) {
    const ctx = await browser.newContext({ viewport, deviceScaleFactor: 1 });
    const page = await ctx.newPage(); const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.route('**/*', route => {
      const m = route.request().url().match(/^https?:\/\/[^/]+(\/[^?#]*)/); let p = decodeURIComponent(m ? m[1] : '/');
      if (p.endsWith('/')) p += 'index.html';
      const f = p.endsWith('/sofa-viewer.js') && altViewer ? path.resolve(altViewer) : path.join(dist, p);
      if (!fs.existsSync(f) || !fs.statSync(f).isFile()) return route.fulfill({ status: 404, body: 'not found' });
      let body = fs.readFileSync(f); if (p.endsWith('/sofa-viewer.js')) body = hook(body.toString());
      return route.fulfill({ status: 200, headers: { 'content-type': MIME[path.extname(f)] || 'application/octet-stream' }, body });
    });
    const isDefault = model.modelId === registry.defaultModelId;
    await page.goto('https://local.test/explorar-sofa.html' + (isDefault ? '' : '?modelo=' + model.modelId), { waitUntil: 'load' });
    await page.click('#start-sofa');
    await page.waitForFunction(() => document.querySelector('#sofa-stage').classList.contains('is-ready'), null, { timeout: 120000 });
    await page.waitForTimeout(400);
    const tag = `${model.modelId}_${size}`;
    const entry = { modelId: model.modelId, size, initial: await measure(page), views: {}, errors };
    entry.initial.verdict = verdict(entry.initial);
    await page.locator('#sofa-stage').screenshot({ path: path.join(OUT, `${tag}_initial.png`) });
    if (withViews) {
      for (const view of await page.$$eval('[data-view]', b => b.map(x => x.dataset.view))) {
        await page.click(`[data-view="${view}"]`); await page.waitForTimeout(250);
        const m = await measure(page); m.verdict = view === 'detail' ? { ok: true, note: 'close-up by design' } : verdict(m);
        entry.views[view] = m;
        await page.locator('#sofa-stage').screenshot({ path: path.join(OUT, `${tag}_${view}.png`) });
      }
      // keyboard Home restores the three-quarter view
      await page.focus('#sofa-stage canvas'); await page.keyboard.press('ArrowLeft'); await page.keyboard.press('Home'); await page.waitForTimeout(200);
      const home = await measure(page); entry.home = { ...home, sameAsThreequarter: JSON.stringify(home) === JSON.stringify((({ verdict, ...rest }) => rest)(entry.views.threequarter || {})) };
    }
    results.push(entry);
    const bad = [['initial', entry.initial], ...Object.entries(entry.views)].filter(([, m]) => !m.verdict.ok).map(([k, m]) => `${k}:${JSON.stringify(m.verdict)}`);
    console.log(tag, JSON.stringify((({ verdict, ...m }) => m)(entry.initial)), bad.length ? 'ISSUES ' + bad.join(' ') : 'ok', errors.length ? 'ERRORS ' + errors : '');
    await ctx.close();
  }
}
fs.writeFileSync(path.join(OUT, 'framing.json'), JSON.stringify(results, null, 1));
await browser.close();
