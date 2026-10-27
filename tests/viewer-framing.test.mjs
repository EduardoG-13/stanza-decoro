// Viewer framing (fix: the configurator used to open with the camera at the origin, inside the piece).
// fitDistance is pure math; the source checks guard the initial view and the setView back-off.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync } from 'node:fs';

const src = readFileSync(new URL('../assets/sofa-pilot/viewer/sofa-viewer.js', import.meta.url), 'utf8');
const prefix = src.slice(0, src.indexOf('/** Create an independent viewer')).replace(/^import[^\n]*\n/gm, '').replace(/\bexport const\b/g, 'const');
const box = {};
vm.runInNewContext(prefix + '\nthis.out={fitDistance,framedCameras,CAMERAS};', box);
const { fitDistance, framedCameras, CAMERAS } = box.out;

// Project a point with a look-at camera; returns NDC [x,y].
function project(p, pos, target, fov, aspect) {
  const sub = (a, b) => a.map((v, k) => v - b[k]), dot = (a, b) => a.reduce((s, v, k) => s + v * b[k], 0);
  const cross = (a, b) => [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
  const unit = a => { const L = Math.hypot(...a); return a.map(v => v / L); };
  const f = unit(sub(target, pos)), r = unit(cross(f, [0, 1, 0])), u = cross(r, f), v = sub(p, pos);
  const t = Math.tan(fov * Math.PI / 360), d = dot(v, f);
  return [dot(v, r) / (d * t * aspect), dot(v, u) / (d * t)];
}
const corners = (min, max) => [min[0], max[0]].flatMap(x => [min[1], max[1]].flatMap(y => [min[2], max[2]].map(z => [x, y, z])));
const place = (target, position, d) => { const o = position.map((v, k) => v - target[k]), L = Math.hypot(...o); return target.map((v, k) => v + o[k] / L * d); };

test('fitDistance: at the returned distance every box corner is inside the frustum and one touches the margin', () => {
  const cases = [
    { min: [-1.25, 0, -.55], max: [1.25, 1.13, .55], view: CAMERAS.threequarter },
    { min: [-1.8, 0, -.5], max: [1.8, 1.2, .1], view: { position: [0, 1, 4.7], target: [0, .6, 0] } },
    { min: [-.22, 0, -.22], max: [.22, .44, .22], view: { position: [1, .8, 1.2], target: [0, .2, 0] } }
  ];
  for (const { min, max, view } of cases) for (const aspect of [16 / 9, 1.3, 1.1, 390 / 844]) {
    const d = fitDistance(min, max, view.target, view.position, 36, aspect, .9);
    assert.ok(d > 0);
    const pos = place(view.target, view.position, d);
    const ndc = corners(min, max).map(c => project(c, pos, view.target, 36, aspect));
    const worst = Math.max(...ndc.flatMap(([x, y]) => [Math.abs(x), Math.abs(y)]));
    assert.ok(worst <= .9 + 1e-6, `inside margin (aspect ${aspect}): ${worst}`);
    assert.ok(worst >= .9 - 1e-3, `tight, not over-backed (aspect ${aspect}): ${worst}`);
  }
});

test('fitDistance: narrower canvases need more distance; degenerate direction returns 0', () => {
  const min = [-1.25, 0, -.55], max = [1.25, 1.13, .55], v = CAMERAS.front;
  const wide = fitDistance(min, max, v.target, v.position, 36, 1.6), narrow = fitDistance(min, max, v.target, v.position, 36, .46);
  assert.ok(narrow > wide * 2);
  assert.equal(fitDistance(min, max, [0, 0, 0], [0, 0, 0], 36, 1), 0);
});

test('framedCameras presets for a puff-sized box fit at their own distance on a 4:3 canvas', () => {
  const min = [-.22, 0, -.22], max = [.22, .44, .22], cams = framedCameras(min, max);
  for (const id of ['threequarter', 'front', 'side', 'back', 'photo']) {
    const { position, target } = cams[id], authored = Math.hypot(...position.map((p, k) => p - target[k]));
    assert.ok(fitDistance(min, max, target, position, 36, 4 / 3) <= authored * 1.25, id);
  }
});

test('viewer source: initial fitted view, setView backs off (except detail), resize refit until the user moves', () => {
  assert.match(src, /const initialView = Object\.hasOwn\(cameras, options\.initialView \|\| ''\) \? options\.initialView : 'threequarter';\s*setView\(initialView\);/);
  assert.match(src, /if \(fit && viewId !== 'detail' && modelBox\)\s*offset\.setLength\(Math\.max\(offset\.length\(\), fitDistance\(/);
  assert.match(src, /if \(!userMoved && currentView\) setView\(currentView\)/);
  assert.match(src, /controls\.addEventListener\('start', \(\) => \{ userMoved = true; \}\)/);
  assert.match(src, /if \(event\.key==='Home'\) setView\('threequarter'\)/);
  assert.match(readFileSync(new URL('../assets/home-opening.js', import.meta.url), 'utf8'), /setView\('threequarter', \{fit:false\}\)/);
});
