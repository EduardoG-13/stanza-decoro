// EXT-001 (revision 2.0.0) 3D contract tests. Replaces the FEAT-004/006 layer-stage tests: the
// sofa is now exterior-only, the layered opening is gone and setProgress is a deprecated no-op.
// These checks cover structure, metadata coherence and material-region classification; they do
// NOT replace visual inspection in a real WebGL viewer (see docs/sofa-3d-review/ext001-exterior.md).
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { createHash } from 'node:crypto';
import { readFileSync, existsSync, readdirSync } from 'node:fs';

const root = new URL('../', import.meta.url);
const read = path => readFileSync(new URL(path, root));
const json = path => JSON.parse(read(path).toString('utf8'));
const viewerSrc = read('assets/sofa-pilot/viewer/sofa-viewer.js').toString('utf8');
const contract = json('assets/sofa-pilot/viewer/contract.json');
const manifest = json('assets/sofa-pilot/manifest.json');
const integration = json('assets/sofa-pilot/INTEGRATION.json');
const credits = json('assets/sofa-pilot/CREDITS.json');
const pilot = json('data/sofa-pilot.json');
const registry = json('data/models-3d.json');
const norm = x => JSON.parse(JSON.stringify(x));

// Evaluate the THREE-free top of the module (constants + regionOf) in an isolated VM.
function viewerConstants() {
  const end = viewerSrc.indexOf('/** Create an independent viewer');
  assert.ok(end > 0, 'end marker not found in viewer source');
  const prefix = viewerSrc.slice(0, end).replace(/^import[^\n]*\n/gm, '').replace(/\bexport const\b/g, 'const');
  const sandbox = {};
  vm.runInNewContext(prefix + '\nthis.out={IDENTITY,DIMENSIONS,COLORS,FABRICS,CAMERAS,LAYER_STAGES,MATERIAL_REGIONS,regionOf,groups};', sandbox);
  return sandbox.out;
}
const V = viewerConstants();

function glbJson(path) {
  const data = read(path);
  assert.equal(data.toString('ascii', 0, 4), 'glTF');
  const length = data.readUInt32LE(12);
  return JSON.parse(data.toString('utf8', 20, 20 + length));
}
const GLBS = { main: 'assets/sofa-pilot/models/sofa.glb', mobile: 'assets/sofa-pilot/models/sofa-mobile.glb' };

test('revision 2.0.0 is coherent everywhere', () => {
  const rev = '2.0.0';
  assert.equal(V.IDENTITY.revision, rev);
  assert.equal(contract.IDENTITY.revision, rev);
  assert.equal(pilot.revision, rev);
  assert.equal(manifest.revision, rev);
  assert.equal(manifest.defaultSelection.revision, rev);
  assert.equal(credits.revision, rev);
  assert.equal(integration.upstreamRevision, rev);
  assert.equal(registry.models.find(m => m.modelId === V.IDENTITY.modelId).revision, rev);
  for (const path of Object.values(GLBS)) {
    const g = glbJson(path); const rootNode = g.nodes.find(n => n.name === 'sofa_root');
    assert.equal(rootNode.extras.revision, rev, path);
    assert.equal(rootNode.extras.modelId, V.IDENTITY.modelId, path);
    assert.equal(rootNode.extras.construction, 'exterior-only', path);
  }
});

test('module constants == contract.json (identity, cameras, colours, fabrics, dimensions, regions)', () => {
  assert.deepEqual(norm(V.IDENTITY), contract.IDENTITY);
  assert.deepEqual(norm(V.CAMERAS), contract.CAMERAS);
  assert.deepEqual(norm(V.COLORS), contract.COLORS);
  assert.deepEqual(norm(V.FABRICS), contract.FABRICS);
  assert.deepEqual(norm(V.DIMENSIONS), contract.DIMENSIONS);
  assert.deepEqual(norm(V.MATERIAL_REGIONS), contract.MATERIAL_REGIONS);
  assert.ok(!('layers' in V.CAMERAS), 'layers camera removed');
});

test('LAYER_STAGES is a single assembled stage (deprecated) and matches contract + manifest', () => {
  assert.equal(V.LAYER_STAGES.length, 1);
  const [stage] = V.LAYER_STAGES;
  assert.equal(stage.progress, 0);
  for (const offset of Object.values(stage.offsets)) assert.deepEqual(norm(offset), [0, 0, 0]);
  assert.deepEqual(Object.keys(stage.offsets).sort(), ['cushions', 'legs', 'upholstery']);
  assert.deepEqual(norm(V.LAYER_STAGES), contract.LAYER_STAGES);
  assert.deepEqual(contract.LAYER_STAGES, manifest.layerSequence.stages);
  assert.equal(manifest.layerSequence.deprecated, true);
  assert.equal(contract.DEPRECATED.since, '2.0.0');
});

test('setProgress is a no-op that keeps the assembled piece', () => {
  const start = viewerSrc.indexOf('function setProgress(value)');
  const body = viewerSrc.slice(start, viewerSrc.indexOf('\n  }\n', start));
  assert.ok(start > 0);
  assert.doesNotMatch(body, /position|offsets|camera|controls/, 'setProgress must not move anything');
  assert.match(body, /Number\.isFinite/);
  assert.match(viewerSrc, /setProgress,setFinish,setView,getSelection/, 'setProgress still exported for compatibility');
});

test('GLBs are exterior-only: no frame/suspension/padding groups or interior objects; exterior groups present', () => {
  const forbidden = /^(padding|frame|suspension|seat_foam|back_foam|seat_batting|back_batting|perimeter_support|front_rail|rear_rail|side_rail_|cross_support_|rear_support|suspension_band_|foot_mount_)/;
  for (const [variant, path] of Object.entries(GLBS)) {
    const g = glbJson(path); const names = g.nodes.map(n => n.name);
    assert.deepEqual(names.filter(n => forbidden.test(n)), [], variant);
    for (const group of ['upholstery', 'legs', 'cushions']) assert.ok(names.includes(group), `${variant}: ${group}`);
    for (const k of [1, 2, 3, 4]) assert.ok(names.includes(`foot_${k}`), `${variant}: foot_${k}`);
    for (const k of [1, 2, 3, 4, 5]) assert.ok(names.includes(`cushion_0${k}_cover`) && names.includes(`cushion_0${k}_welt`), `${variant}: cushion ${k}`);
    assert.ok(!g.materials.some(m => /illustrative/.test(m.name)), `${variant}: no interior materials`);
  }
  assert.deepEqual(norm(V.groups), ['upholstery', 'legs', 'cushions']);
});

test('only body materials are classified customizable (stanzaFabric); cushions are fixed decorative', () => {
  assert.match(viewerSrc, /stanzaFabric: region === 'body'/);
  for (const [variant, path] of Object.entries(GLBS)) {
    const g = glbJson(path);
    const regions = Object.fromEntries(g.materials.map(m => [m.name, V.regionOf({ name: m.name, userData: m.extras || {} })]));
    assert.deepEqual(Object.keys(regions).filter(n => regions[n] === 'body').sort(), ['fabric_main', 'fabric_seam'], variant);
    for (const name of V.MATERIAL_REGIONS.decorative) assert.equal(regions[name], 'decorative', `${variant}: ${name}`);
    assert.equal(regions.legs_dark, 'exterior-structure');
    // Region tag in the GLB agrees with the name table (a renamed/cloned material cannot slip into body).
    for (const m of g.materials) assert.equal(m.extras?.stanza_region, regions[m.name], `${variant}: extras of ${m.name}`);
    // Every cushion mesh uses decorative materials only; body meshes use body materials only.
    const meshMats = name => { const node = g.nodes.find(n => n.name === name); return g.meshes[node.mesh].primitives.map(p => g.materials[p.material].name); };
    for (const k of [1, 2, 3, 4, 5]) for (const part of ['cover', 'welt'])
      for (const mat of meshMats(`cushion_0${k}_${part}`)) assert.equal(regions[mat], 'decorative', `${variant}: cushion_0${k}_${part} uses ${mat}`);
    for (const body of ['seat_cover', 'back_cover', 'seat_panel_seam']) for (const mat of meshMats(body)) assert.equal(regions[mat], 'body', `${variant}: ${body}`);
    // Olive = 01 and 05 (with cream reverse), light = 02..04, as in SOFA-2.jpg.
    for (const k of [1, 5]) assert.deepEqual(meshMats(`cushion_0${k}_cover`).sort(), ['cushion_olive_reverse', 'cushion_olive_weave']);
    for (const k of [2, 3, 4]) assert.deepEqual(meshMats(`cushion_0${k}_cover`), ['cushion_light_boucle']);
  }
});

test('integrity: INTEGRATION and manifest sha256/bytes match the real GLB bytes; validator reports exist', () => {
  for (const [variant, path] of Object.entries(GLBS)) {
    const bytes = read(path); const digest = createHash('sha256').update(bytes).digest('hex');
    const rel = path.replace('assets/sofa-pilot/', '');
    assert.equal(integration.modelSha256[rel], digest, rel);
    assert.equal(manifest.models[variant].sha256, digest, variant);
    assert.equal(manifest.models[variant].bytes, bytes.length, variant);
    assert.ok(manifest.models[variant].triangles <= manifest.performance.geometryTargets[variant], variant);
  }
  assert.equal(integration.geometryChanged, true);
  for (const f of ['gltf-validation-sofa.json', 'gltf-validation-sofa-mobile.json']) {
    const report = json('docs/sofa-3d-review/validation/ext001/' + f);
    assert.equal(report.issues.numErrors, 0, f);
  }
});

test('model registry is consistent with the contract and its assets exist', () => {
  const ids = new Set(json('data/catalog.json').map(item => item.id));
  for (const model of registry.models) {
    assert.ok(ids.has(model.catalogId), model.modelId);
    for (const key of ['main', 'mobile', 'poster', 'manifest']) assert.ok(existsSync(new URL(model.assets[key].replace(/^\//, ''), root)), `${model.modelId}: ${key}`);
  }
  const sofa = registry.models.find(m => m.modelId === registry.defaultModelId);
  assert.deepEqual(sofa.materialRegions, contract.MATERIAL_REGIONS);
  assert.deepEqual(sofa.options.fabrics.slice().sort(), Object.keys(contract.FABRICS).sort());
  assert.deepEqual(sofa.options.colors.slice().sort(), Object.keys(contract.COLORS).sort());
  assert.deepEqual(Object.keys(pilot.fabrics).sort(), Object.keys(contract.FABRICS).sort());
  assert.deepEqual(Object.keys(pilot.colors).sort(), Object.keys(contract.COLORS).sort());
});

test('no layer/structure controls or opening calls remain in the public pages and adapters', () => {
  const pages = readdirSync(new URL('pages/', root)).filter(f => f.endsWith('.html')).map(f => 'pages/' + f);
  const files = [...pages, 'explorar-sofa.html', 'index.html', 'assets/sofa-experience.js', 'assets/home-opening.js', 'assets/sofa-experience.css'];
  for (const file of files) {
    const text = read(file).toString('utf8');
    assert.doesNotMatch(text, /sofa-progress|data-progress|sofa-layers|sofa-step|setProgress|attachScrollSequence|scroll\.js|layer-key/, file);
    assert.doesNotMatch(text, /por dentro do sofá|abra suas camadas|percintas|ordem de construção/i, file);
  }
  assert.ok(!existsSync(new URL('assets/sofa-pilot/viewer/scroll.js', root)), 'scroll adapter removed');
});
