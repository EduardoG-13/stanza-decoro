"""EXT-003 - Sofá modular cinza (catálogo `sofa-modular`, portfólio `projeto-3`).
Reference: sofas/SOFA-3.jpg (single photographed angle, front-RIGHT, elevated; the piece runs
from the near right arm to the far left arm).

Parametric EXTERIOR-ONLY source. Regenerates in ONE pass (never edit the .blend/GLBs by hand):
    LD_LIBRARY_PATH=<gl libs> .agents/venv/bin/python assets/models-3d/stanza-modular-01/source/build.py
writes models/stanza-modular-01.glb, models/stanza-modular-01-mobile.glb,
source/stanza-modular-01.blend and source/metrics.json.

Axes (Blender): X width, -Y FRONT, Z up; origin = centre of the footprint on the floor.
All dimensions are ESTIMATES from one photo (camera/proportion fit to 17 correspondences with
the seat-block height fixed at 0.40 m, see docs/sofa-3d-review/ext003-sofa-modular.md).

Construction read from the photo: a MODULAR block sofa standing directly on the floor (no
visible feet or plinth): two tall square arm blocks, three wide monolithic seat blocks and three
back blocks behind them (the back is taller than the arms), every module a separate upholstered
box with soft rounded edges and a narrow visible joint to its neighbours. No loose seat/back
cushions; seven loose decorative pillows (four plain dusty blue, three printed with nested
diamonds) lean on the back.

Material regions (`stanza_region`):
  body        fabric_main                       (arms, seat blocks, back blocks)
  decorative  pillow_blue, pillow_blue_seam,    (seven decorative pillows, fixed)
              pillow_print, pillow_print_seam
  (no contrast and no visible exterior structure in the photo)
"""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE.parent
sys.path.insert(0, str(MODEL_DIR.parent / 'lib'))
import bpy
import stanza3d as S

MODEL_ID = 'stanza-modular-01'
REVISION = '1.0.0'
EMBEDDED = {'fabricId': 'sarja', 'colorId': 'grafite-quente'}
REGIONS = {'body': ['fabric_main'], 'decorative': ['pillow_blue', 'pillow_blue_seam', 'pillow_print', 'pillow_print_seam']}

# ---------------------------------------------------------------- proportions (estimated, m)
HS = 0.40         # seat block height (ASSUMPTION that fixes the scale)
W = 4.24          # overall width (fit 4.24)
D = 1.17          # overall depth (fit 1.17)
AW = 0.34         # arm block width (fit 0.34)
HA = 0.76         # arm height (fit 0.76)
HB = 0.96         # back block height (fit 0.96; the back stands above the arms)
BT = 0.22         # back block thickness (not constrained by the photo; assumed)
GAP = 0.004       # visible joint between neighbouring modules
SEAT_R, ARM_R, BACK_R = 0.05, 0.04, 0.04
INNER = W/2-AW
SW = (2*INNER-2*GAP)/3          # module width (seat and back blocks), ~1.18 m
BACK_Y0 = D/2-BT                # front face of the back blocks (Blender +Y = back)

# decorative pillows, left -> right as in the photo: (name, kind, x, half size, roll deg, layer)
# layer 0 = big pillows against the back; layer 1 = smaller ones leaning on layer 0.
PILLOWS = [
    ('pillow_1', 'blue', -1.43, (.330, .320), -4, 0),
    ('pillow_2', 'blue', -0.98, (.260, .245), 6, 1),
    ('pillow_3', 'print', -0.62, (.255, .250), -10, 1),
    ('pillow_4', 'blue', -0.20, (.330, .320), 4, 0),
    ('pillow_5', 'print', 0.42, (.255, .250), 16, 1),
    ('pillow_6', 'print', 0.88, (.245, .240), 24, 1),
    ('pillow_7', 'blue', 1.40, (.340, .330), -8, 0),
]

def srgb(*c):
    return tuple(((v/255+.055)/1.055)**2.4 if v/255 > .04045 else v/255/12.92 for v in c)

def build(mobile=False, placements=None):
    S.reset()
    P = placements or {}
    Q = .55 if mobile else 1.0
    def m(v): return max(1, int(round(v*Q)))
    root = S.empty('model_root', None, modelId=MODEL_ID, revision=REVISION, construction='exterior-only',
                   dimensions_estimated=True, reference='sofas/SOFA-3.jpg', catalogId='sofa-modular', queue='EXT-003',
                   materialRegions=REGIONS, embeddedFinish=EMBEDDED, bodyUvMeters=S.BODY_UV_METERS)
    groups = {n: S.empty(n, root) for n in ('upholstery', 'legs', 'cushions')}
    # ------------------------------------------------------------ materials
    fmaps = S.library_maps('sarja', tint='grafite-quente', base=512 if mobile else 1024, normal=256 if mobile else 1024, rough=256)
    cloth = S.textured('fabric_main', fmaps, 'body', .9, .10, .8)
    weave = {k: fmaps[k] for k in ('normal', 'roughness')}     # pillows share the cloth relief (no extra image)
    blue = srgb(127, 158, 172)
    pblue = S.textured('pillow_blue', weave, 'decorative', .8, .12, .8, color=blue)
    pblue_s = S.textured('pillow_blue_seam', weave, 'decorative', .8, .12, .8, color=blue)
    pmaps = S.library_maps('decor-losango', base=512 if mobile else 1024, normal=256, rough=256)
    pmaps['normal'] = fmaps['normal']; pmaps['roughness'] = fmaps['roughness']
    pprint = S.textured('pillow_print', pmaps, 'decorative', .8, .12, .8)
    pprint_s = S.textured('pillow_print_seam', weave, 'decorative', .8, .12, .8, color=srgb(228, 231, 232))
    # ------------------------------------------------------------ modules (body)
    up = groups['upholstery']; body = {}
    e = 4 if not mobile else 3
    for side, sx in (('l', -1), ('r', 1)):
        rb = S.RoundedBox((sx*(W/2-AW/2), 0, HA/2), (AW, D, HA), ARM_R, mid=(m(4), m(14), m(9)), edge=e,
                          crown={'+z': .004, '-y': .004, '+x' if sx > 0 else '-x': .004, '-x' if sx > 0 else '+x': .001}, wrinkle=.0008, seed=3+sx)
        rb.build(f'arm_{side}', up, cloth); body[f'arm_{side}'] = rb
    seats, backs = [], []
    for k in range(3):
        cx = -INNER+SW/2+k*(SW+GAP)
        sb = S.RoundedBox((cx, (-D/2+BACK_Y0-GAP)/2, HS/2), (SW-GAP, BACK_Y0-GAP+D/2, HS), SEAT_R, mid=(m(14), m(12), m(5)), edge=e,
                          crown={'+z': .012, '-y': .008, '+x': .0012, '-x': .0012}, wrinkle=.0012, seed=11+k)
        sb.build(f'seat_block_{k+1}', up, cloth); seats.append(sb)
        bb = S.RoundedBox((cx, (BACK_Y0+D/2)/2, HB/2), (SW-GAP, BT, HB), BACK_R, mid=(m(14), m(3), m(10)), edge=e,
                          crown={'-y': .0025, '+z': .004, '+y': .002}, wrinkle=.0010, seed=21+k)
        bb.build(f'back_block_{k+1}', up, cloth); backs.append(bb)
    # ------------------------------------------------------------ decorative pillows (fixed)
    seat_col = [s.collider() for s in seats]; back_col = [b.collider() for b in backs]
    arm_col = [body['arm_l'].collider(), body['arm_r'].collider()]
    soft = lambda bvhs, c: [(b, c) for b in bvhs]
    n_p = m(24) if not mobile else 16
    placed = {}
    for layer in (0, 1):
        for name, kind, x, half, roll, lay in PILLOWS:
            if lay != layer: continue
            y0 = BACK_Y0-(.20 if layer == 0 else .40)
            lc = S.LooseCushion(name, (x, y0, HS+half[1]+.06), (-24 if layer == 0 else -30, roll, 0),
                                dict(n=n_p, size=half, seed=31+len(placed), loft=.085 if layer == 0 else .078))
            behind = back_col+([placed[p].collider() for p in placed] if layer == 1 else [])
            if name in P: lc.pos = tuple(P[name]['pos'])
            else: lc.solve(seat_col, [((0, 0, -1), .008)]); lc.solve(behind, [((0, 1, 0), .010)])
            lc.settle(soft(seat_col+back_col+arm_col, -.0012)+(soft([placed[p].collider() for p in placed], -.0008) if layer == 1 else []))
            lc.kind = kind; placed[name] = lc
    # big pillows re-settled around the smaller ones leaning on them (mutual soft contact)
    front = [placed[n].collider() for n, _k, _x, _h, _r, lay in PILLOWS if lay == 1]
    for name, kind, _x, _h, _r, lay in PILLOWS:
        lc = placed[name]
        if lay == 0: lc.settle(soft(seat_col+back_col+arm_col, -.0012)+soft(front, -.0008))
        cov, sm = (pblue, pblue_s) if kind == 'blue' else (pprint, pprint_s)
        lc.build(groups['cushions'], cov, sm, .0020)
    # ------------------------------------------------------------ export
    bpy.context.view_layer.update()
    tris, per = S.triangle_count(True)
    name = MODEL_ID+('-mobile' if mobile else '')
    dest = MODEL_DIR/'models'/(name+'.glb')
    S.export_variant(dest, None if mobile else HERE/(MODEL_ID+'.blend'))
    placements = {c.name: {'pos': [round(v, 4) for v in c.pos], 'rot': list(c.rot)} for c in placed.values()}
    print('EXPORTED', dest, 'tris', tris)
    return {'triangles_blender': tris, 'trianglesByObject': per, 'placements': placements}

if __name__ == '__main__':
    out = {}
    # main first: solves the pillow placements (and saves the .blend); the mobile variant REUSES
    # them so both variants keep the same composition and contacts.
    out['main'] = build(False)
    out['mobile'] = build(True, out['main']['placements'])
    for v, path in (('main', MODEL_ID+'.glb'), ('mobile', MODEL_ID+'-mobile.glb')):
        out[v].update(S.glb_metrics(MODEL_DIR/'models'/path))
    (HERE/'metrics.json').write_text(json.dumps(out, indent=2)+'\n', encoding='utf-8')
    for v in out: print(v, out[v]['triangles'], out[v]['bytes'], out[v]['boundsMeters']['dimensions'])
