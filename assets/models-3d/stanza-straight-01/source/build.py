"""EXT-002 - Sofá cinza de linhas retas (catálogo `sofa-reto`, portfólio `projeto-5`).
Reference: sofas/SOFA-5.jpg (single photographed angle, front-left, elevated).

Parametric EXTERIOR-ONLY source. Regenerates in ONE pass (never edit the .blend/GLBs by hand):
    LD_LIBRARY_PATH=<gl libs> .agents/venv/bin/python assets/models-3d/stanza-straight-01/source/build.py
writes models/stanza-straight-01.glb, models/stanza-straight-01-mobile.glb,
source/stanza-straight-01.blend and source/metrics.json.

Axes (Blender): X width, -Y FRONT, Z up; origin = centre of the footprint on the floor.
All dimensions are ESTIMATES from one photo (camera/proportion fit with seat height fixed at
0.44 m, see docs/sofa-3d-review/ext002-sofa-reto.md), not shop drawings.

Components (individually editable below): wooden plinth (apron + 4 block feet), two square
arms, upholstered base band, low back panel, two boxed seat cushions, two loose back
cushions, two decorative pillows, welts (seat cushion top/bottom, arm front panels, cushion
and pillow knife edges).

Material regions (`stanza_region`):
  body               fabric_main, fabric_seam  (arms, base, back panel, seat + back cushions)
  decorative         pillow_boucle, pillow_seam (two loose decorative pillows, fixed)
  exterior-structure plinth_wood               (apron + feet, fixed dark wood)
"""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE.parent
sys.path.insert(0, str(MODEL_DIR.parent / 'lib'))
import bpy
import stanza3d as S
from mathutils import Vector

MODEL_ID = 'stanza-straight-01'
REVISION = '1.0.0'
EMBEDDED = {'fabricId': 'boucle-mescla', 'colorId': 'gelo'}
REGIONS = {'body': ['fabric_main', 'fabric_seam'], 'decorative': ['pillow_boucle', 'pillow_seam'], 'exterior-structure': ['plinth_wood']}

# ---------------------------------------------------------------- proportions (estimated, m)
W = 2.32          # overall width (arm to arm)
D = 0.86          # overall depth (weakly constrained by the single view: rear points suggest 0.75-0.95)
AW = 0.24         # arm width
ARM_H = 0.575     # arm top (and back panel top) above the floor
PLINTH_H = 0.115  # top of the wooden plinth = underside of the upholstery
APRON_H = 0.048   # visible apron band height
APRON_T = 0.022   # apron thickness
LEG = 0.068       # square block foot
PLINTH_INSET_X = 0.05   # plinth outer face inset from the arm outer side
PLINTH_INSET_Y = 0.012  # plinth front face inset from the arm/base front
BASE_TOP = 0.24   # top of the upholstered base band (seat deck)
SEAT_T = 0.20     # seat cushion thickness (deck -> crown edge ~0.44)
BACK_T = 0.18     # back panel thickness
SEAT_GAP = 0.006  # gap between the two seat cushions / to the arms (soft contact, no overlap)
BACK_CUSHION = dict(half=(0.39, 0.215), loft=0.08, lean=-12.0, shift=0.055)
# shift: in SOFA-5.jpg both back cushions sit ~5 cm right of centre (back panel visible at the left arm)
EDGE_R = 0.035    # soft edge radius of arms/back panel
SEAT_R = 0.055    # seat cushion edge radius

def build(mobile=False, placements=None):
    S.reset()
    P = placements or {}
    def place(lc, solve):
        if lc.name in P: lc.pos = tuple(P[lc.name]['pos'])
        else: solve()
    Q = .55 if mobile else 1.0
    def m(v): return max(1, int(round(v*Q)))
    root = S.empty('model_root', None, modelId=MODEL_ID, revision=REVISION, construction='exterior-only',
                   dimensions_estimated=True, reference='sofas/SOFA-5.jpg', catalogId='sofa-reto', queue='EXT-002',
                   materialRegions=REGIONS, embeddedFinish=EMBEDDED, bodyUvMeters=S.BODY_UV_METERS)
    groups = {n: S.empty(n, root) for n in ('upholstery', 'legs', 'cushions')}
    # ------------------------------------------------------------ materials
    fmaps = S.library_maps('boucle-mescla', tint='gelo', base=512 if mobile else 1024, normal=256 if mobile else 1024, rough=256)
    cloth = S.textured('fabric_main', fmaps, 'body', 1.5, .12, .95)
    seam = S.textured('fabric_seam', fmaps, 'body', 1.5, .12, .95)
    # decorative pillows: same bouclé look as in the photo, a touch greyer, FIXED (never recoloured)
    pillow = S.textured('pillow_boucle', fmaps, 'decorative', 1.5, .15, .95, color=(.93, .93, .94))
    pseam = S.textured('pillow_seam', fmaps, 'decorative', 1.5, .15, .95, color=(.93, .93, .94))
    wood = S.textured('plinth_wood', S.library_maps('wood-wenge', base=256 if mobile else 512, normal=256, rough=256), 'exterior-structure', .4, roughness=None)
    # ------------------------------------------------------------ plinth (exterior structure)
    x0, x1 = -W/2+PLINTH_INSET_X, W/2-PLINTH_INSET_X
    y0, y1 = -D/2+PLINTH_INSET_Y, D/2-PLINTH_INSET_Y-.02
    S.plinth('plinth', groups['legs'], wood, x0, x1, y0, y1, PLINTH_H, APRON_H, APRON_T, LEG)
    # ------------------------------------------------------------ body frame
    up = groups['upholstery']; body = {}
    arm_mid = (m(4), m(16), m(8)); edge = 4 if not mobile else 3
    for side, sx in (('l', -1), ('r', 1)):
        cx = sx*(W/2-AW/2)
        rb = S.RoundedBox((cx, 0, (PLINTH_H+ARM_H)/2), (AW, D, ARM_H-PLINTH_H), EDGE_R, mid=arm_mid, edge=edge,
                          crown={'+z': .006, '-y': .004, '+x' if sx > 0 else '-x': .005}, wrinkle=.0012, seed=3+sx)
        rb.build(f'arm_{side}', up, cloth); body[f'arm_{side}'] = rb
        S.tube(f'arm_{side}_front_welt', rb.seam_loop('-y', samples=m(96), lift=.0010), .0022, up, seam, sides=4)
    inner = W/2-AW
    back_y0 = D/2-BACK_T
    base = S.RoundedBox((0, (-D/2+back_y0+.05)/2, (PLINTH_H+BASE_TOP)/2), (2*inner+.03, back_y0+.05+D/2, BASE_TOP-PLINTH_H), .03,
                        mid=(m(28), m(12), m(2)), edge=m(4), crown={'-y': .006}, wrinkle=.0008, seed=5)
    base.build('base_band', up, cloth); body['base'] = base
    backp = S.RoundedBox((0, (back_y0+D/2)/2, (PLINTH_H+ARM_H)/2), (2*inner+.03, BACK_T, ARM_H-PLINTH_H), EDGE_R,
                         mid=(m(28), m(3), m(8)), edge=m(4), crown={'-y': .0015, '+z': .004}, wrinkle=.001, seed=7)
    backp.build('back_panel', up, cloth); body['back'] = backp
    # ------------------------------------------------------------ seat cushions (body)
    sw = inner-SEAT_GAP*1.5; sd = back_y0-(-D/2)-SEAT_GAP-.003
    seats = []
    for k, sx in enumerate((-1, 1)):
        cx = sx*(SEAT_GAP/2+sw/2)
        rb = S.RoundedBox((cx, -D/2+.003+sd/2, BASE_TOP+SEAT_T/2+.0005), (sw, sd, SEAT_T), SEAT_R,
                          mid=(m(16), m(13), m(3)), edge=4 if not mobile else 3,
                          crown={'+z': .022, '-y': .014, '+x': .0035, '-x': .0035}, wrinkle=.0018, seed=11+k)
        rb.build(f'seat_cushion_{k+1}', up, cloth); seats.append(rb)
        for f in ('+z', '-z'):
            S.tube(f'seat_cushion_{k+1}_welt_{"top" if f == "+z" else "bottom"}', rb.seam_loop(f, samples=m(150), lift=.0011), .0024, up, seam, sides=4)
    # ------------------------------------------------------------ loose cushions
    rigid_frame = [body['arm_l'].collider(), body['arm_r'].collider(), backp.collider()]
    seat_col = [s.collider() for s in seats]
    soft = lambda bvhs, c: [(b, c) for b in bvhs]
    n_back = m(30) if not mobile else 16
    backs = []
    for k, sx in enumerate((-1, 1)):
        a, b = BACK_CUSHION['half']
        lc = S.LooseCushion(f'back_cushion_{k+1}', (sx*(inner/2-.008)+BACK_CUSHION['shift'], back_y0-.09, BASE_TOP+SEAT_T+b+.02), (BACK_CUSHION['lean'], 0, 0),
                            dict(n=n_back, size=(a, b), seed=21+k, loft=BACK_CUSHION['loft'], concave=(.025, .03), pinch=.12,
                                 gathers=.0025, wrinkle=.0035, base=.018, edge_round=.45))
        place(lc, lambda: (lc.solve([seat_col[k]], [((0, 0, -1), .010)]), lc.solve(rigid_frame, [((0, 1, 0), .010)])))
        lc.settle(soft(rigid_frame+[seat_col[k]], -.0012)); backs.append(lc)
    back_col = [c.collider() for c in backs]
    n_p = m(24) if not mobile else 18
    # left: rectangular pillow lying diagonally over the left arm and the left back cushion
    pl = S.LooseCushion('pillow_1', (-inner+.19, .02, .78), (-68, 22, -20),
                        dict(n=n_p, size=(.30, .175), seed=31, loft=.088))
    place(pl, lambda: (pl.solve([seats[0].collider(), body['arm_l'].collider()], [((0, 0, -1), .008)]), pl.solve(back_col[:1], [((.15, 1, 0), .010)])))
    pl.settle(soft([seats[0].collider(), body['arm_l'].collider(), backp.collider()], -.0012)+soft(back_col[:1], -.0008))
    pl.build(groups['cushions'], pillow, pseam, .0018)
    # right: square pillow set as a diamond, leaning on the right back cushion and arm
    pr = S.LooseCushion('pillow_2', (inner-.09, -.02, .66), (-50, 32, -30),
                        dict(n=n_p, size=(.235, .235), seed=37, loft=.075))
    place(pr, lambda: (pr.solve([seats[1].collider()], [((0, 0, -1), .008)]), pr.solve(back_col[1:], [((0, 1, 0), .010)])))
    # the rigid arm EDGE would poke between the pillow's vertices: keep the pillow 5 mm proud of the arm
    pr.settle(soft([seats[1].collider(), backp.collider()], -.0012)+soft([body['arm_r'].collider()], .005)+soft(back_col[1:], -.0008))
    pr.build(groups['cushions'], pillow, pseam, .0018)
    # mutual soft contact: the back cushions are re-settled around the pillows leaning on them
    for k, lc in enumerate(backs):
        lc.settle(soft(rigid_frame+[seat_col[k]], -.0012)+soft([(pl if k == 0 else pr).collider()], -.0008))
        lc.build(groups['upholstery'], cloth, seam, .0022)
    # ------------------------------------------------------------ export
    bpy.context.view_layer.update()
    tris, per = S.triangle_count(True)
    name = MODEL_ID+('-mobile' if mobile else '')
    dest = MODEL_DIR/'models'/(name+'.glb')
    S.export_variant(dest, None if mobile else HERE/(MODEL_ID+'.blend'))
    placements = {c.name: {'pos': [round(v, 4) for v in c.pos], 'rot': list(c.rot)} for c in backs+[pl, pr]}
    print('EXPORTED', dest, 'tris', tris)
    return {'triangles_blender': tris, 'trianglesByObject': per, 'placements': placements}

if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    out = {}
    # main first: solves the loose-cushion placements (and saves the .blend); the mobile variant
    # REUSES them so both variants keep the same composition and contacts.
    out['main'] = build(False)
    out['mobile'] = build(True, out['main']['placements'])
    for v, path in (('main', MODEL_ID+'.glb'), ('mobile', MODEL_ID+'-mobile.glb')):
        if v in out: out[v].update(S.glb_metrics(MODEL_DIR/'models'/path))
    (HERE/'metrics.json').write_text(json.dumps(out, indent=2)+'\n', encoding='utf-8')
    for v in out: print(v, out[v]['triangles'], out[v]['bytes'], out[v]['boundsMeters']['dimensions'])
