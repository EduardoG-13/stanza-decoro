"""EXT-005 - Sofá cinza com vivo claro (catálogo `sofa-com-vivo`, portfólio `projeto-48`).
Reference: acervo/sofa-com-vivo.webp (2560x1920, single angle, front-LEFT, elevated, strong
window light from the back-left; the piece recedes from the near left arm to the far right arm).

Parametric EXTERIOR-ONLY source. Regenerates in ONE pass (never edit the .blend/GLBs by hand):
    LD_LIBRARY_PATH=<gl libs> .agents/venv/bin/python assets/models-3d/stanza-piped-01/source/build.py
writes models/stanza-piped-01.glb, models/stanza-piped-01-mobile.glb,
source/stanza-piped-01.blend and source/metrics.json.

Axes (Blender): X width, -Y FRONT, Z up; origin = centre of the footprint on the floor.
All dimensions are ESTIMATES from one photo (camera/proportion fit to 8 correspondences with
the seat height fixed at 0.45 m and the depth constrained to ~1.0 m, see
docs/sofa-3d-review/ext005-sofa-com-vivo.md).

Construction read from the photo: a long two-seater upholstered down to the floor (no feet
confirmed): two square box arms with a LIGHT CONTRAST welt around the front panel; a tall
upholstered base band; two wide, thin boxed seat cushions with light welts on the top and
bottom edges; a back panel behind two large BOXED back cushions (welts around the front and
back faces) leaning back. No decorative pillows.

Material regions (`stanza_region`):
  body      fabric_main    (arms, base band, back panel, seat and back cushions)
  contrast  piping_light   (every light welt: arm fronts, seat and back cushion edges) - FIXED
"""
import sys, json, math
from pathlib import Path
HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE.parent
sys.path.insert(0, str(MODEL_DIR.parent / 'lib'))
import bpy
import stanza3d as S

MODEL_ID = 'stanza-piped-01'
REVISION = '1.0.0'
EMBEDDED = {'fabricId': 'sarja', 'colorId': 'cinza-malva'}
REGIONS = {'body': ['fabric_main'], 'contrast': ['piping_light']}

# ---------------------------------------------------------------- proportions (estimated, m)
HS = 0.45         # seat height (ASSUMPTION that fixes the scale)
W = 3.46          # overall width (fit 3.46)
D = 1.00          # overall depth (constrained ~1.0: the rear is not measurable in the photo)
AW = 0.23         # arm width (fit 0.233)
HA = 0.665        # arm height (fit 0.665)
ST = 0.13         # seat cushion thickness (fit 0.128)
BASE_TOP = HS-ST  # top of the upholstered base band = 0.32
BT = 0.17         # back panel thickness (assumed)
HB = 0.84         # back panel height (hidden behind the back cushions; assumed)
GAP = 0.006
INNER = W/2-AW
BACK_Y0 = D/2-BT
BACK = dict(h=0.64, t=0.20, lean=14.0)     # boxed back cushion height / thickness / lean (deg)
WELT_R = 0.0032                            # contrast piping radius (reads clearly in the photo)

def srgb(*c):
    return tuple(((v/255+.055)/1.055)**2.4 if v/255 > .04045 else v/255/12.92 for v in c)

def build(mobile=False):
    S.reset()
    Q = .55 if mobile else 1.0
    def m(v): return max(1, int(round(v*Q)))
    root = S.empty('model_root', None, modelId=MODEL_ID, revision=REVISION, construction='exterior-only',
                   dimensions_estimated=True, reference='acervo/sofa-com-vivo.webp', catalogId='sofa-com-vivo', queue='EXT-005',
                   materialRegions=REGIONS, embeddedFinish=EMBEDDED, bodyUvMeters=S.BODY_UV_METERS)
    groups = {n: S.empty(n, root) for n in ('upholstery', 'legs', 'cushions')}
    # ------------------------------------------------------------ materials
    fmaps = S.library_maps('sarja', tint='cinza-malva', base=512 if mobile else 1024, normal=256 if mobile else 1024, rough=256)
    cloth = S.textured('fabric_main', fmaps, 'body', .9, .10, .8)
    # fixed light piping: same cloth relief, own light colour, never recoloured
    pipe = S.textured('piping_light', {k: fmaps[k] for k in ('normal', 'roughness')}, 'contrast', .9, .10, .8, color=srgb(226, 226, 229))
    up = groups['upholstery']; e = 4 if not mobile else 3
    seam_n = lambda n: m(n) if not mobile else max(48, m(n))
    # ------------------------------------------------------------ arms with contrast front welt
    arms = {}
    for side, sx in (('l', -1), ('r', 1)):
        rb = S.RoundedBox((sx*(W/2-AW/2), 0, HA/2), (AW, D, HA), .03, mid=(m(4), m(16), m(8)), edge=e,
                          crown={'+z': .005, '-y': .004, '+x' if sx > 0 else '-x': .004}, wrinkle=.0008, seed=3+sx)
        rb.build(f'arm_{side}', up, cloth); arms[side] = rb
        S.tube(f'arm_{side}_front_welt', rb.seam_loop('-y', samples=seam_n(110), lift=.0012), WELT_R, up, pipe, sides=5 if not mobile else 4)
    # ------------------------------------------------------------ base band + back panel (body)
    base = S.RoundedBox((0, (-D/2+.004+BACK_Y0+.05)/2, BASE_TOP/2), (2*INNER+.03, BACK_Y0+.05+D/2-.004, BASE_TOP), .025,
                        mid=(m(30), m(10), m(3)), edge=e, crown={'-y': .005}, wrinkle=.0006, seed=5)
    base.build('base_band', up, cloth)
    backp = S.RoundedBox((0, (BACK_Y0+D/2)/2, HB/2), (2*INNER+.03, BT, HB), .035,
                         mid=(m(30), m(3), m(8)), edge=e, crown={'-y': .002, '+z': .004}, wrinkle=.0007, seed=7)
    backp.build('back_panel', up, cloth)
    # ------------------------------------------------------------ seat cushions with contrast welts
    OVER = 0.02       # seat cushion front overhangs the base band (photo: the cushion front sits proud of the base)
    sw = INNER-GAP*1.5; sd = BACK_Y0-(-D/2)-GAP+OVER
    seats = []
    for k, sx in enumerate((-1, 1)):
        rb = S.RoundedBox((sx*(GAP/2+sw/2), -D/2-OVER+sd/2, BASE_TOP+ST/2+.0005), (sw, sd, ST), .04,
                          mid=(m(20), m(14), m(2)), edge=e, crown={'+z': .016, '-y': .016, '+x': .002, '-x': .002}, wrinkle=.0014, seed=11+k)
        rb.build(f'seat_cushion_{k+1}', up, cloth); seats.append(rb)
        for f in ('+z', '-z'):
            S.tube(f'seat_cushion_{k+1}_welt_{"top" if f == "+z" else "bottom"}', rb.seam_loop(f, samples=seam_n(170), lift=.0012), WELT_R, up, pipe, sides=5 if not mobile else 4)
    # ------------------------------------------------------------ boxed back cushions (tilted), welts front + back
    lean = math.radians(BACK['lean']); h, t = BACK['h'], BACK['t']
    seat_top = BASE_TOP+ST+.004          # seat cushion top near its back edge (crown fades there)
    for k, sx in enumerate((-1, 1)):
        # local frame: X width, Y thickness (front -Y), Z height; rotate about X so the top goes back (+Y).
        # Bottom-back edge rests on the seat in front of the back panel; back face leans on the panel.
        # local up u = (0, sin, cos), back normal n = (0, cos, -sin). Lowest point = bottom-back
        # edge, sunk 8 mm into the seat crown; the back face passes 6 mm behind the panel's front
        # top edge (soft lean on the panel top, like a loose boxed cushion).
        cz = seat_top - .008 + math.cos(lean)*h/2 + math.sin(lean)*t/2
        cy = BACK_Y0 - .003 - (t/2 + (HB - cz)*math.sin(lean))/math.cos(lean)
        bc, holder = S.oriented_box(f'back_cushion_{k+1}', (sw, t, h), .05, (sx*(GAP/2+sw/2), cy, cz), (-BACK['lean'], 0, 0), up, cloth,
                       welts=('-y', '+y'), welt_mat=pipe, welt_r=WELT_R, samples=seam_n(170), mid=(m(20), 4, 10), edge=e,
                       crown={'-y': .03, '+y': .012, '+z': .006}, wrinkle=.0018, seed=21+k, sides=5 if not mobile else 4)
        # soft rigid rest: drop onto the seat cushion (3 mm), then lean back onto the panel (3 mm)
        S.rest_rigid(holder, bc.object, [seats[k].collider()], (0, 0, -1), .003)
        S.rest_rigid(holder, bc.object, [backp.collider()], (0, 1, 0), .003)
    # ------------------------------------------------------------ export
    bpy.context.view_layer.update()
    tris, per = S.triangle_count(True)
    name = MODEL_ID+('-mobile' if mobile else '')
    dest = MODEL_DIR/'models'/(name+'.glb')
    S.export_variant(dest, None if mobile else HERE/(MODEL_ID+'.blend'))
    print('EXPORTED', dest, 'tris', tris)
    return {'triangles_blender': tris, 'trianglesByObject': per}

if __name__ == '__main__':
    out = {'main': build(False), 'mobile': build(True)}
    for v, path in (('main', MODEL_ID+'.glb'), ('mobile', MODEL_ID+'-mobile.glb')):
        out[v].update(S.glb_metrics(MODEL_DIR/'models'/path))
    (HERE/'metrics.json').write_text(json.dumps(out, indent=2)+'\n', encoding='utf-8')
    for v in out: print(v, out[v]['triangles'], out[v]['bytes'], out[v]['boundsMeters']['dimensions'])
