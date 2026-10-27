// models3d capture harness: renders a REGISTERED model through the REAL product viewer module
// (/assets/sofa-pilot/viewer/sofa-viewer.js -> createSofaViewer, same lights/materials as the site)
// served from the built dist/ via Playwright page.route (no web server needed).
//
//   node scripts/models3d/capture.mjs <config.json>
//
// config: {
//   "dist": "dist", "out": "<dir>", "modelId": "stanza-straight-01",
//   "views": [{"name":"front","preset":"front"} | {"name":"x","cam":[x,y,z],"target":[x,y,z],"fov":36}],
//   "runs": [{"label":"main","variant":"main","width":1200,"height":900,
//             "finishes":[{"label":"initial"},{"label":"grafite","finish":{"colorId":"grafite"}}],
//             "masks": true}]          // masks: also render a flat region mask per view
// }
// Mask colours: body #ff0000, decorative #00ff00, contrast #ffff00, exterior-structure #0000ff,
// other region #ff00ff, untagged meshes (the viewer floor) and background black.
//
// Requirements (free, no paid deps): playwright-core (npm i --no-save playwright-core@1.56 or set
// PLAYWRIGHT_CORE=/abs/path/to/playwright-core/index.mjs) and a Chromium/Chrome-for-Testing binary
// (CHROME_PATH; default: the sandbox's headless shell). WebGL runs on SwiftShader when no GPU.
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const { chromium } = await import(process.env.PLAYWRIGHT_CORE ? pathToFileURL(process.env.PLAYWRIGHT_CORE).href : 'playwright-core');
export const CHROME = process.env.CHROME_PATH || '/inner_container/opt/playwright/chromium_headless_shell-1232/chrome-headless-shell-linux64/chrome-headless-shell';
export const MIME = { '.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.json':'application/json','.glb':'model/gltf-binary','.jpg':'image/jpeg','.png':'image/png','.webp':'image/webp','.svg':'image/svg+xml','.woff2':'font/woff2','.webmanifest':'application/manifest+json' };

export function serveDist(page, dist, opts = {}) {
  const requests = [];
  const abortOnce = new Set(opts.abortOnce || []);
  page.route('**/*', route => {
    const m = route.request().url().match(/^https?:\/\/[^/]+(\/[^?#]*)/); let p = decodeURIComponent(m ? m[1] : '/');
    if (p.endsWith('/')) p += 'index.html';
    requests.push(p);
    if (opts.virtual && opts.virtual[p]) return route.fulfill({ status: 200, headers: { 'content-type': 'text/html' }, body: opts.virtual[p]() });
    for (const pat of abortOnce) if (p.endsWith(pat)) { abortOnce.delete(pat); return route.abort('failed'); }
    const f = path.join(dist, p);
    if (!fs.existsSync(f) || !fs.statSync(f).isFile()) return route.fulfill({ status: 404, body: 'not found ' + p });
    return route.fulfill({ status: 200, headers: { 'content-type': MIME[path.extname(f)] || 'application/octet-stream' }, body: fs.readFileSync(f) });
  });
  return { requests, abortOnce };
}

export function launch() {
  return chromium.launch({ executablePath: CHROME, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox', '--ignore-gpu-blocklist'] });
}

export const harness = (W, H) => `<!doctype html><html><head><meta charset=utf-8>
<style>html,body{margin:0;background:#e9e6e0}#stage{width:${W}px;height:${H}px;position:relative}</style>
<script type="importmap">{"imports":{"three":"/assets/sofa-pilot/viewer/vendor/three/three.module.min.js"}}</script>
</head><body><div id=stage></div><script type=module>
import * as THREE from 'three';
import { OrbitControls } from '/assets/sofa-pilot/viewer/vendor/three/addons/controls/OrbitControls.js';
const ou = OrbitControls.prototype.update;
OrbitControls.prototype.update = function(...a){ window.__controls = this; return ou.apply(this,a); };
THREE.Scene.prototype.onBeforeRender = function(r,s,c){ window.__renderer=r; window.__scene=s; window.__cam=c; };
window.THREE = THREE;
const { createSofaViewer } = await import('/assets/sofa-pilot/viewer/sofa-viewer.js');
const registry = await (await fetch('/assets/models-3d.json')).json();
const p = new URLSearchParams(location.search);
const model = registry.models.find(m => m.modelId === p.get('model'));
try {
  window.__viewer = await createSofaViewer(document.getElementById('stage'), { variant:p.get('variant'), preserveDrawingBuffer:true,
    baseUrl:model.assets.viewerBase, modelUrls:{main:model.assets.main,mobile:model.assets.mobile}, model, materialUrls:registry.materialLibrary });
  window.__ready = true;
} catch(e) { window.__ready = 'ERR '+e; }
</script></body></html>`;

async function applyView(page, v, mask) {
  await page.evaluate(async ({ v, mask }) => {
    const V = window.__viewer, c = window.__controls, cam = window.__cam, T = window.THREE, sc = window.__scene, R = window.__renderer;
    if (v.preset) V.setView(v.preset);
    if (v.cam) { c.minDistance = .05; cam.position.fromArray(v.cam); c.target.fromArray(v.target); c.update(); }
    if (v.fov) { cam.fov = v.fov; cam.updateProjectionMatrix(); }
    if (!window.__orig) { window.__orig = new Map(); sc.traverse(n => { if (n.isMesh) window.__orig.set(n, n.material); }); window.__bg = sc.background.clone(); }
    const COL = { body:'#ff0000', decorative:'#00ff00', contrast:'#ffff00', 'exterior-structure':'#0000ff' };
    sc.traverse(n => {
      if (!n.isMesh) return;
      const orig = window.__orig.get(n);
      if (!mask) { n.material = orig; return; }
      if (!orig) { n.material = new T.MeshBasicMaterial({ color:'#000000' }); return; }   // floor
      const region = orig.userData?.stanzaRegion; n.material = new T.MeshBasicMaterial({ color: region ? (COL[region] || '#ff00ff') : '#000000' });
    });
    sc.background = mask ? new T.Color('#000000') : window.__bg;
    R.toneMapping = mask ? T.NoToneMapping : T.ACESFilmicToneMapping;
    R.render(sc, cam);
  }, { v, mask });
  await page.waitForTimeout(120);
}

export async function capture(cfg) {
  const dist = path.resolve(cfg.dist || 'dist'); const OUT = path.resolve(cfg.out); fs.mkdirSync(OUT, { recursive: true });
  const browser = await launch(); const log = { modelId: cfg.modelId, runs: [] };
  for (const run of cfg.runs) {
    const W = run.width || 1200, H = run.height || 900;
    const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: run.dpr || 1 });
    const page = await ctx.newPage(); const errors = [];
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('pageerror', e => errors.push('PAGEERROR ' + e.message));
    serveDist(page, dist, { virtual: { '/__capture.html': () => harness(W, H) } });
    await page.goto(`https://local.test/__capture.html?model=${encodeURIComponent(cfg.modelId)}&variant=${run.variant}`);
    await page.waitForFunction(() => window.__ready && (window.__ready !== true || window.__cam), null, { timeout: 120000 }).catch(() => {});
    const ready = await page.evaluate(() => window.__ready);
    const rec = { label: run.label, variant: run.variant, ready, shots: [] };
    if (ready !== true) { rec.errors = errors; log.runs.push(rec); await ctx.close(); continue; }
    for (const pass of run.finishes || [{ label: 'initial' }]) {
      if (pass.finish) rec[`selection_${pass.label}`] = await page.evaluate(f => window.__viewer.setFinish(f), pass.finish);
      for (const v of cfg.views) {
        if (v.variants && !v.variants.includes(run.variant)) continue;
        if (pass.views && !pass.views.includes(v.name)) continue;
        await applyView(page, v, false);
        const name = `${run.label}__${pass.label}__${v.name}.png`;
        await page.locator('#stage canvas').screenshot({ path: path.join(OUT, name) }); rec.shots.push(name);
        if (run.masks && !pass.noMask) {
          await applyView(page, v, true);
          const mname = `${run.label}__${pass.label}__${v.name}__mask.png`;
          await page.locator('#stage canvas').screenshot({ path: path.join(OUT, mname) }); rec.shots.push(mname);
          await applyView(page, v, false);
        }
      }
    }
    rec.selection = await page.evaluate(() => window.__viewer.getSelection());
    rec.inspect = await page.evaluate(() => { const i = window.__viewer.inspect(); return { modelId: i.modelId, revision: i.revision, variant: i.variant, bounds: i.bounds, views: i.views, options: i.options, construction: i.construction, meshes: i.meshes.length, materialRegions: i.materialRegions.map(m => [m.name, m.region, m.stanzaFabric]), texturesLoaded: i.texturesLoaded }; });
    rec.errors = errors; log.runs.push(rec); await ctx.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(OUT, 'capture-log.json'), JSON.stringify(log, null, 2));
  return log;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const log = await capture(cfg);
  console.log(JSON.stringify(log.runs.map(r => ({ label: r.label, ready: r.ready, shots: r.shots.length, errors: r.errors })), null, 1));
}
