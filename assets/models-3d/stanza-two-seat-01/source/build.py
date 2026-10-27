"""EXT-004 - Sofá claro de dois assentos (catálogo `sofa-dois-assentos`, portfólio `projeto-47`).
Reference: acervo/sofa-dois-assentos.webp (2560x1920, single angle, front-RIGHT, elevated; the
piece recedes from the near right arm to the far left arm).

Parametric EXTERIOR-ONLY source. Regenerates in ONE pass (never edit the .blend/GLBs by hand):
    LD_LIBRARY_PATH=<gl libs> .agents/venv/bin/python assets/models-3d/stanza-two-seat-01/source/build.py
writes models/stanza-two-seat-01.glb, models/stanza-two-seat-01-mobile.glb,
source/stanza-two-seat-01.blend and source/metrics.json.

Axes (Blender): X width, -Y FRONT, Z up; origin = centre of the footprint on the floor.
All dimensions are ESTIMATES from one photo (camera/proportion fit to 12 correspondences with
the seat height fixed at 0.45 m, see docs/sofa-3d-review/ext004-sofa-dois-assentos.md).

Construction read from the photo: a deep two-seater upholstered down to the floor (no visible
feet or plinth on the shag rug): two square box arms, LOWER than the back; an upholstered base
band under two thick boxed seat cushions whose fronts bulge slightly past the arms; a back
panel taller than the arms (visible above the right arm) and two tall loose back cushions with
rounded boxy fill. No piping in contrast (seams are the same cloth). One lumbar decorative
pillow with a dark brown square pattern.

Material regions (`stanza_region`):
  body        fabric_main                              (arms, base, back panel, seat and back cushions, their seams)
  decorative  pillow_squares, pillow_squares_seam      (lumbar pillow, fixed)
"""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE.parent
sys.path.insert(0, str(MODEL_DIR.parent / 'lib'))
import bpy
import stanza3d as S

MODEL_ID = 'stanza-two-seat-01'
REVISION = '1.0.0'
EMBEDDED = {'fabricId': 'linho-rustico', 'colorId': 'cru'}
REGIONS = {'body': ['fabric_main'], 'decorative': ['pillow_squares', 'pillow_squares_seam']}

# ---------------------------------------------------------------- proportions (estimated, m)
HS = 0.45         # seat height at the cushion front edge (ASSUMPTION that fixes the scale)
W = 2.63          # overall width (fit 2.63)
D = 1.20          # overall depth (fit 1.25, one rear point only -> rounded down)
AW = 0.23         # arm width (fit 0.234)
HA = 0.65         # arm height (fit 0.651)
ST = 0.17         # seat cushion thickness (fit 0.170)
BASE_TOP = HS-ST  # top of the upholstered base band = 0.28
BT = 0.20         # back panel thickness (assumed)
HB = 0.78         # back panel height (read above the right arm, ~0.80)
GAP = 0.006       # between the two seat cushions / to the arms
INNER = W/2-AW
BACK_Y0 = D/2-BT
BACK_CUSHION = dict(half=(.525, .245), loft=.09, lean=-10.0)
PILLOW = dict(x=-0.17, half=(.34, .19), loft=.08, rot=(-34, 4, 4))

def srgb(*c):
    return tuple(((v/255+.055)/1.055)**2.4 if v/255 > .04045 else v/255/12.92 for v in c)

def build(mobile=False, placements=None):
    S.reset()
    P = placements or {}
    Q = .55 if mobile else 1.0
    def m(v): return max(1, int(round(v*Q)))
    root = S.empty('model_root', None, modelId=MODEL_ID, revision=REVISION, construction='exterior-only',
                   dimensions_estimated=True, reference='acervo/sofa-dois-assentos.webp', catalogId='sofa-dois-assentos', queue='EXT-004',
                   materialRegions=REGIONS, embeddedFinish=EMBEDDED, bodyUvMeters=S.BODY_UV_METERS)
    groups = {n: S.empty(n, root) for n in ('upholstery', 'legs', 'cushions')}
    # ------------------------------------------------------------ materials
    fmaps = S.library_maps('linho-rustico', tint='cru', base=512 if mobile else 1024, normal=256 if mobile else 1024, rough=256)
    cloth = S.textured('fabric_main', fmaps, 'body', 1.0, .10, .85)
    pmaps = S.library_maps('decor-quadrados', base=512 if mobile else 1024, normal=256 if mobile else 512, rough=256)
    pillow = S.textured('pillow_squares', pmaps, 'decorative', 1.0, .30, .6)
    pseam = S.textured('pillow_squares_seam', {k: fmaps[k] for k in ('normal', 'roughness')}, 'decorative', 1.0, .2, .7, color=srgb(196, 176, 164))
    # ------------------------------------------------------------ body frame
    up = groups['upholstery']; body = {}
    e = 4 if not mobile else 3
    for side, sx in (('l', -1), ('r', 1)):
        rb = S.RoundedBox((sx*(W/2-AW/2), 0, HA/2), (AW, D, HA), .032, mid=(m(4), m(18), m(8)), edge=e,
                          crown={'+z': .005, '-y': .004, '+x' if sx > 0 else '-x': .005}, wrinkle=.0008, seed=3+sx)
        rb.build(f'arm_{side}', up, cloth); body[f'arm_{side}'] = rb
    base = S.RoundedBox((0, (-D/2+.004+BACK_Y0+.05)/2, BASE_TOP/2), (2*INNER+.03, BACK_Y0+.05+D/2-.004, BASE_TOP), .028,
                        mid=(m(26), m(12), m(3)), edge=e, crown={'-y': .006}, wrinkle=.0007, seed=5)
    base.build('base_band', up, cloth); body['base'] = base
    backp = S.RoundedBox((0, (BACK_Y0+D/2)/2, HB/2), (2*INNER+.03, BT, HB), .035,
                         mid=(m(26), m(3), m(9)), edge=e, crown={'-y': .002, '+z': .004}, wrinkle=.0008, seed=7)
    backp.build('back_panel', up, cloth); body['back'] = backp
    # ------------------------------------------------------------ seat cushions (body)
    sw = INNER-GAP*1.5; sd = BACK_Y0-(-D/2)-GAP
    seats = []
    for k, sx in enumerate((-1, 1)):
        rb = S.RoundedBox((sx*(GAP/2+sw/2), -D/2+sd/2, BASE_TOP+ST/2+.0005), (sw, sd, ST), .055,
                          mid=(m(16), m(16), m(3)), edge=e,
                          crown={'+z': .020, '-y': .024, '+x': .003, '-x': .003}, wrinkle=.0016, seed=11+k)
        rb.build(f'seat_cushion_{k+1}', up, cloth); seats.append(rb)
    # ------------------------------------------------------------ loose back cushions (body)
    rigid = [body['arm_l'].collider(), body['arm_r'].collider(), backp.collider()]
    seat_col = [s.collider() for s in seats]
    soft = lambda bvhs, c: [(b, c) for b in bvhs]
    n_back = m(30) if not mobile else 16
    backs = []
    for k, sx in enumerate((-1, 1)):
        a, b = BACK_CUSHION['half']
        lc = S.LooseCushion(f'back_cushion_{k+1}', (sx*(INNER/2-.002), BACK_Y0-.12, HS+b+.03), (BACK_CUSHION['lean'], 0, 0),
                            dict(n=n_back, size=(a, b), seed=21+k, loft=BACK_CUSHION['loft'], concave=(.02, .025), pinch=.10,
                                 gathers=.002, wrinkle=.003, base=.03, edge_round=.6))
        if lc.name in P: lc.pos = tuple(P[lc.name]['pos'])
        else: lc.solve([seat_col[k]], [((0, 0, -1), .010)]); lc.solve(rigid, [((0, 1, 0), .010)])
        lc.settle(soft(rigid+[seat_col[k]], -.0012)); backs.append(lc)
    back_col = [c.collider() for c in backs]
    # ------------------------------------------------------------ lumbar decorative pillow (fixed)
    n_p = m(26) if not mobile else 18
    pl = S.LooseCushion('pillow_1', (PILLOW['x'], BACK_Y0-.42, HS+.25), PILLOW['rot'],
                        dict(n=n_p, size=PILLOW['half'], seed=31, loft=PILLOW['loft'], concave=(.05, .06), pinch=.3))
    if pl.name in P: pl.pos = tuple(P[pl.name]['pos'])
    else: pl.solve(seat_col, [((0, 0, -1), .008)]); pl.solve(back_col, [((0, 1, 0), .010)])
    pl.settle(soft(seat_col+[backp.collider()], -.0012)+soft(back_col, -.0008))
    pl.build(groups['cushions'], pillow, pseam, .0020)
    for k, lc in enumerate(backs):
        lc.settle(soft(rigid+[seat_col[k]], -.0012)+soft([pl.collider()], -.0008))
        lc.build(up, cloth, cloth, .0016)
    # ------------------------------------------------------------ export
    bpy.context.view_layer.update()
    tris, per = S.triangle_count(True)
    name = MODEL_ID+('-mobile' if mobile else '')
    dest = MODEL_DIR/'models'/(name+'.glb')
    S.export_variant(dest, None if mobile else HERE/(MODEL_ID+'.blend'))
    placements = {c.name: {'pos': [round(v, 4) for v in c.pos], 'rot': list(c.rot)} for c in backs+[pl]}
    print('EXPORTED', dest, 'tris', tris)
    return {'triangles_blender': tris, 'trianglesByObject': per, 'placements': placements}

if __name__ == '__main__':
    out = {}
    out['main'] = build(False)
    out['mobile'] = build(True, out['main']['placements'])
    for v, path in (('main', MODEL_ID+'.glb'), ('mobile', MODEL_ID+'-mobile.glb')):
        out[v].update(S.glb_metrics(MODEL_DIR/'models'/path))
    (HERE/'metrics.json').write_text(json.dumps(out, indent=2)+'\n', encoding='utf-8')
    for v in out: print(v, out[v]['triangles'], out[v]['bytes'], out[v]['boundsMeters']['dimensions'])
