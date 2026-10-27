// models3d pipeline: registry consistency for EVERY registered model (files, sha256, revision across
// registry/manifest/GLB extras, regions, options, catalog/portfolio relation), multi-model viewer
// options and the absence of layer controls. Structural checks only; visual review is separate.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { createHash } from 'node:crypto';
import { readFileSync, existsSync } from 'node:fs';

const root = new URL('../', import.meta.url);
const read = path => readFileSync(new URL(path.replace(/^\//, ''), root));
const json = path => JSON.parse(read(path).toString('utf8'));
const registry = json('data/models-3d.json');
const catalog = json('data/catalog.json');
const portfolio = json('data/portfolio.json');
const studies = json('data/sofa-pilot.json');
const viewerSrc = read('assets/sofa-pilot/viewer/sofa-viewer.js').toString('utf8');
const contract = json('assets/sofa-pilot/viewer/contract.json');

function viewerConstants() {
  const end = viewerSrc.indexOf('/** Create an independent viewer');
  const prefix = viewerSrc.slice(0, end).replace(/^import[^\n]*\n/gm, '').replace(/\bexport const\b/g, 'const').replace(/\bexport function\b/g, 'function');
  const sandbox = {};
  vm.runInNewContext(prefix + '\nthis.out={IDENTITY,COLORS,FABRICS,CAMERAS,MATERIAL_REGIONS,REGION_NAMES,DEFAULT_MODEL_OPTIONS,framedCameras,regionOf};', sandbox);
  return sandbox.out;
}
const V = viewerConstants();
const norm = x => JSON.parse(JSON.stringify(x));
function glb(path) {
  const data = read(path);
  assert.equal(data.toString('ascii', 0, 4), 'glTF', path);
  assert.equal(data.readUInt32LE(8), data.length, path + ' length');
  const length = data.readUInt32LE(12);
  return { data, g: JSON.parse(data.toString('utf8', 20, 20 + length)) };
}
const rootNode = g => g.nodes.find(n => n.name === 'model_root' || n.name === 'sofa_root');
const extra = v => (typeof v === 'string' ? JSON.parse(v) : v);
const verified = new Set(registry.verifiedStatuses);

test('registry: unique ids, catalog/portfolio relation, one verified study per catalog item', () => {
  const ids = registry.models.map(m => m.modelId);
  assert.equal(new Set(ids).size, ids.length);
  assert.ok(ids.includes(registry.defaultModelId));
  const catalogIds = new Set(catalog.map(c => c.id)), portfolioIds = new Set(portfolio.map(p => p.id));
  const perCatalog = {};
  for (const m of registry.models) {
    assert.ok(catalogIds.has(m.catalogId), `${m.modelId}: catalogId ${m.catalogId}`);
    if (m.portfolioId) assert.ok(portfolioIds.has(m.portfolioId), `${m.modelId}: portfolioId`);
    // same reference photo on both sides of the relation
    const item = catalog.find(c => c.id === m.catalogId);
    assert.equal(item.source, m.reference, `${m.modelId}: reference == catalog source`);
    if (m.portfolioId) assert.equal(portfolio.find(p => p.id === m.portfolioId).source, m.reference, `${m.modelId}: portfolio source`);
    if (verified.has(m.status)) perCatalog[m.catalogId] = (perCatalog[m.catalogId] || 0) + 1;
    assert.match(m.queue, /^EXT-\d{3}$/);
  }
  for (const [id, n] of Object.entries(perCatalog)) assert.equal(n, 1, id);
});

test('registry: files exist and sha256/bytes/revision agree across registry, manifest and GLB extras', () => {
  for (const m of registry.models) {
    for (const key of ['main', 'mobile', 'poster', 'manifest']) assert.ok(existsSync(new URL(m.assets[key].replace(/^\//, ''), root)), `${m.modelId}: ${key}`);
    const manifest = json(m.assets.manifest);
    assert.equal(manifest.revision, m.revision, `${m.modelId}: manifest revision`);
    for (const variant of ['main', 'mobile']) {
      const { data, g } = glb(m.assets[variant]);
      const entry = manifest.models[variant];
      assert.equal(createHash('sha256').update(data).digest('hex'), entry.sha256, `${m.modelId} ${variant} sha256`);
      assert.equal(data.length, entry.bytes, `${m.modelId} ${variant} bytes`);
      const ex = rootNode(g).extras;
      assert.equal(ex.modelId, m.modelId, `${m.modelId} ${variant} extras.modelId`);
      assert.equal(ex.revision, m.revision, `${m.modelId} ${variant} extras.revision`);
      assert.equal(ex.construction, 'exterior-only', `${m.modelId} ${variant}`);
    }
  }
});

test('registry: material regions are declared, valid and match the GLB material extras', () => {
  for (const m of registry.models) {
    assert.ok(m.materialRegions.body?.length, `${m.modelId}: body region`);
    for (const region of Object.keys(m.materialRegions)) assert.ok(V.REGION_NAMES.includes(region), `${m.modelId}: ${region}`);
    for (const variant of ['main', 'mobile']) {
      const { g } = glb(m.assets[variant]);
      const declared = Object.entries(m.materialRegions).flatMap(([r, names]) => names.map(n => [n, r]));
      const actual = Object.fromEntries(g.materials.map(x => [x.name, x.extras?.stanza_region]));
      assert.deepEqual(Object.keys(actual).sort(), declared.map(([n]) => n).sort(), `${m.modelId} ${variant}: material set`);
      for (const [name, region] of declared) {
        assert.equal(actual[name], region, `${m.modelId} ${variant}: ${name}`);
        assert.equal(V.regionOf({ name, userData: { stanza_region: actual[name] } }, m.materialRegions), region);
      }
    }
  }
});

test('registry: options use valid, implemented IDs; defaults are exposed; EXT-001 keeps its palette', () => {
  for (const m of registry.models) {
    const o = m.options;
    assert.equal(o.appliesTo, 'body');
    for (const f of o.fabrics) { assert.ok(Object.hasOwn(V.FABRICS, f), `${m.modelId}: fabric ${f}`); assert.ok(studies.fabrics[f], `label ${f}`); }
    for (const c of o.colors) { assert.ok(Object.hasOwn(V.COLORS, c), `${m.modelId}: color ${c}`); assert.ok(studies.colors[c], `label ${c}`); }
    assert.ok(o.fabrics.includes(o.default.fabricId) && o.colors.includes(o.default.colorId), m.modelId);
    // every exposed fabric has loadable maps (shared library or the model's viewer base)
    for (const f of o.fabrics) {
      const folder = registry.materialLibrary[f] || m.assets.viewerBase + 'materials/' + f + '/';
      for (const name of ['basecolor.jpg', 'normal.png', 'roughness.jpg']) assert.ok(existsSync(new URL((folder + name).replace(/^\//, ''), root)), `${m.modelId}: ${f}/${name}`);
    }
  }
  const ext001 = registry.models.find(m => m.modelId === 'stanza-organic-01');
  assert.deepEqual(ext001.options.fabrics, ['boucle', 'linen', 'velvet']);
  assert.deepEqual(ext001.options.colors, ['areia', 'oliva', 'terracota', 'grafite']);
  assert.deepEqual(norm(V.DEFAULT_MODEL_OPTIONS), { fabrics: ext001.options.fabrics, colors: ext001.options.colors, default: ext001.options.default });
  // palette is append-only: the original IDs keep their values
  assert.deepEqual(Object.keys(V.COLORS).slice(0, 4), ['areia', 'oliva', 'terracota', 'grafite']);
  assert.deepEqual(Object.keys(V.FABRICS).slice(0, 3), ['linen', 'boucle', 'velvet']);
  assert.deepEqual(norm(V.COLORS), contract.COLORS);
  assert.deepEqual(norm(V.FABRICS), contract.FABRICS);
  assert.deepEqual(norm(V.REGION_NAMES), contract.REGION_NAMES);
});

test('viewer: embedded initial finish == model default, embedded tint == COLORS value (no double tint)', () => {
  const lib = json('assets/models-3d/materials/materials.json');
  for (const m of registry.models.filter(x => x.modelId !== 'stanza-organic-01')) {
    assert.deepEqual(m.options.embedded, m.options.default, m.modelId);
    const { g } = glb(m.assets.main);
    assert.deepEqual(extra(rootNode(g).extras.embeddedFinish), m.options.embedded, m.modelId);
    const tint = lib.tints[m.options.embedded.colorId];
    assert.equal(tint, V.COLORS[m.options.embedded.colorId], `${m.modelId}: library tint == viewer colour`);
    // embedded maps are authored at the body UV unit: either the family repeat IS the unit, or the
    // embedded maps pre-tile the family an integer number of times (root extra embeddedTiles, EXT-014
    // velvet 0.14 m -> 2 tiles = 0.15 m, within 10%).
    const tiles = extra(rootNode(g).extras.embeddedTiles) || 1, rep = V.FABRICS[m.options.embedded.fabricId].repeatMeters;
    assert.ok(Number.isInteger(tiles) && Math.abs(lib.bodyUvMeters / tiles - rep) / rep <= .1, `${m.modelId}: embedded family authored at the body UV unit`);
  }
  assert.match(viewerSrc, /candidate\.fabricId === embedded\.fabricId && candidate\.colorId === embedded\.colorId/);
  assert.match(viewerSrc, /allowedFabrics\.includes\(candidate\.fabricId\) \|\| !allowedColors\.includes\(candidate\.colorId\)/);
  assert.match(viewerSrc, /options\.materialUrls\?\.\[fabricId\]/);
});

test('viewer: framedCameras gives all presets from bounds; EXT-001 keeps its fixed CAMERAS', () => {
  const cams = V.framedCameras([-1.165, 0, -0.435], [1.165, 0.99, 0.435]);
  for (const id of ['threequarter', 'front', 'side', 'back', 'detail', 'photo']) {
    assert.ok(cams[id], id);
    assert.equal(cams[id].position.length, 3); assert.equal(cams[id].target.length, 3);
    const d = Math.hypot(...cams[id].position.map((v, k) => v - cams[id].target[k]));
    assert.ok(d > .5 && d < 9, `${id} distance ${d}`);
  }
  assert.ok(cams.front.position[2] > 2 && Math.abs(cams.front.position[0]) < 1e-9);
  assert.ok(cams.back.position[2] < 0);
  assert.deepEqual(norm(V.CAMERAS), contract.CAMERAS);
  assert.match(viewerSrc, /identity\.modelId !== IDENTITY\.modelId/);
});

test('configurator: ?modelo selects only verified registered models; product pages get the 3D entry only then', () => {
  const adapter = read('assets/sofa-experience.js').toString('utf8');
  assert.match(adapter, /get\('modelo'\)/);
  assert.match(adapter, /verified\.includes\(entry\.status\)/);
  assert.match(adapter, /model, materialUrls: registry\.materialLibrary/);
  assert.match(adapter, /referencia: model\?\.catalogId/);
  assert.doesNotMatch(adapter, /registry\.models\.find\(entry => entry\.modelId === registry\.defaultModelId\)/, 'unknown model must not fall back to another piece');
  const build = read('scripts/build.py').toString('utf8');
  assert.match(build, /def model_experience\(item\)/);
  assert.match(build, /VERIFIED_3D\.get\(item\['id'\]\)/);
  const explore = read('pages/explore.html').toString('utf8');
  for (const m of registry.models) for (const id of [...m.options.fabrics, ...m.options.colors]) assert.match(explore, new RegExp(`value="${id}"`), `explore input ${id}`);
});

test('quote: studies map each registered 3D study to its catalog reference', () => {
  for (const m of registry.models) assert.equal(studies.studies[m.modelId], m.catalogId, m.modelId);
  for (const file of ['assets/app.js', 'assets/quote-redirect.js']) assert.match(read(file).toString('utf8'), /studies/, file);
});

test('no layer controls in any registered model page or GLB', () => {
  const explore = read('pages/explore.html').toString('utf8');
  assert.doesNotMatch(explore, /sofa-progress|data-progress|sofa-layers|setProgress/);
  for (const m of registry.models) for (const variant of ['main', 'mobile']) {
    const { g } = glb(m.assets[variant]);
    const names = g.nodes.map(n => n.name);
    assert.deepEqual(names.filter(n => /^(padding|frame|suspension|foam|batting|webbing)/.test(n)), [], `${m.modelId} ${variant}`);
  }
});
