// FEAT-004/006 3D-behaviour tests. These assert the layer-opening CONTRACT is internally
// consistent across the three representations and that the exploded-view math does not drift
// after an open/close cycle. They verify structure and numeric invariants only; they do NOT
// replace visual inspection in a real WebGL viewer (see docs/sofa-3d-review/).
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync } from 'node:fs';

const viewerSrc = readFileSync(new URL('../assets/sofa-pilot/viewer/sofa-viewer.js', import.meta.url), 'utf8');
const contract = JSON.parse(readFileSync(new URL('../assets/sofa-pilot/viewer/contract.json', import.meta.url), 'utf8'));
const manifest = JSON.parse(readFileSync(new URL('../assets/sofa-pilot/manifest.json', import.meta.url), 'utf8'));

// Extract the top-of-module constants (which do not touch THREE) from the viewer source,
// up to and including the LAYER_STAGES declaration, and evaluate them in an isolated VM.
function extractViewerConstants() {
  const marker = 'const groups = ';
  const end = viewerSrc.indexOf(marker);
  assert.ok(end > 0, 'could not locate end marker in viewer source');
  let prefix = viewerSrc.slice(0, end);
  // Drop the ESM `import ... from 'three'` lines; they are not needed for the constants.
  prefix = prefix.replace(/^import[^\n]*\n/gm, '');
  // Strip `export ` so the declarations become plain consts captured on the sandbox.
  prefix = prefix.replace(/\bexport const\b/g, 'const');
  const sandbox = { matchMedia: () => ({ matches: false }) };
  vm.runInNewContext(prefix + '\nthis.__LS = LAYER_STAGES; this.__CAM = CAMERAS;', sandbox);
  return { LAYER_STAGES: sandbox.__LS, CAMERAS: sandbox.__CAM };
}

// Normalise through JSON so frozen/shared-reference arrays compare purely by value.
const norm = x => JSON.parse(JSON.stringify(x));
const { LAYER_STAGES } = extractViewerConstants();

test('LAYER_STAGES (module) == contract.json.LAYER_STAGES', () => {
  assert.deepEqual(norm(LAYER_STAGES), norm(contract.LAYER_STAGES));
});

test('contract.json.LAYER_STAGES == manifest.json.layerSequence.stages', () => {
  assert.deepEqual(norm(contract.LAYER_STAGES), norm(manifest.layerSequence.stages));
});

test('setProgress contract: 0 and 1 are assembled (all offsets zero) and identical', () => {
  const first = LAYER_STAGES[0], last = LAYER_STAGES[LAYER_STAGES.length - 1];
  assert.equal(first.progress, 0);
  assert.equal(last.progress, 1);
  for (const stage of [first, last]) {
    for (const g of Object.keys(stage.offsets)) assert.deepEqual(norm(stage.offsets[g]), [0, 0, 0]);
    for (const s of Object.keys(stage.subOffsets || {})) assert.deepEqual(norm(stage.subOffsets[s]), [0, 0, 0]);
  }
  assert.deepEqual(norm(first.offsets), norm(last.offsets));
  assert.deepEqual(norm(first.subOffsets), norm(last.subOffsets));
});

test('setProgress contract: ~.5 separated and ~.7 structure are non-trivial and ordered', () => {
  const byP = Object.fromEntries(LAYER_STAGES.map(s => [s.progress, s]));
  // At .5 the fabric (upholstery) is already lifted; at .7 it is lifted at least as much,
  // and the frame/structure become exposed (padding group itself starts to move at .7).
  assert.ok(byP[0.5].offsets.upholstery[1] > 0, 'fabric lifted at .5');
  assert.ok(byP[0.7].offsets.upholstery[1] >= byP[0.5].offsets.upholstery[1], 'fabric does not sink from .5 to .7');
  assert.equal(byP[0.5].offsets.padding[1], 0, 'foam core still seated at .5');
  assert.ok(byP[0.7].offsets.padding[1] > 0, 'foam core lifts to expose structure at .7');
});

// Replicate the viewer's setProgress position math (no THREE) to prove no drift.
function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
function ease(t) { return t * t * (3 - 2 * t); }
const GROUPS = ['upholstery', 'padding', 'frame', 'legs', 'cushions', 'suspension'];
const SUBS = ['seat_batting', 'back_batting', 'seat_foam', 'back_foam'];
const origin = Object.fromEntries([...GROUPS, ...SUBS].map((n, i) => [n, [i * 0.1, i * 0.2 - 1, i * 0.3]]));

function positionsAt(progress) {
  progress = clamp(progress, 0, 1);
  let after = LAYER_STAGES.findIndex(s => s.progress >= progress);
  if (after <= 0) after = 1;
  const a = LAYER_STAGES[after - 1], b = LAYER_STAGES[after];
  const t = ease((progress - a.progress) / (b.progress - a.progress));
  const out = {};
  for (const g of GROUPS) {
    out[g] = origin[g].map((o, i) => o + (a.offsets[g][i] + (b.offsets[g][i] - a.offsets[g][i]) * t));
  }
  for (const s of SUBS) {
    const sa = (a.subOffsets && a.subOffsets[s]) || [0, 0, 0];
    const sb = (b.subOffsets && b.subOffsets[s]) || [0, 0, 0];
    out[s] = origin[s].map((o, i) => o + (sa[i] + (sb[i] - sa[i]) * t));
  }
  return out;
}

test('no drift: positions at 0 and at 1 (after a .5/.7/.35 cycle) equal the base positions', () => {
  const p0 = positionsAt(0);
  // simulate an open/close cycle (positions are recomputed from base each call, so history
  // should not matter)
  positionsAt(0.5); positionsAt(0.7); positionsAt(0.35);
  const p1 = positionsAt(1);
  for (const n of [...GROUPS, ...SUBS]) {
    assert.deepEqual(p0[n], origin[n], `${n} at p0 equals base`);
    assert.deepEqual(p1[n], origin[n], `${n} at p1 equals base`);
    assert.deepEqual(p0[n], p1[n], `${n} identical at p0 and p1`);
  }
});

test('all stage cameras are defined with position+target triples', () => {
  for (const stage of LAYER_STAGES) {
    assert.equal(stage.camera.position.length, 3);
    assert.equal(stage.camera.target.length, 3);
  }
});
