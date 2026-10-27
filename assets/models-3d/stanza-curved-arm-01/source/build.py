"""EXT-007 - Sofá verde de braços curvos (catálogo `sofa-curvo`, portfólio `projeto-9`).
References: sofas/SOFA-9.png (532x450) and sofas/SOFA-9.2.png (532x332). SOFA-9.2 is the SAME
viewpoint as SOFA-9 (pixel-registered: SOFA-9 rows 72..403, median difference 2/255, local
retouching only), so the camera is fitted once and the second photo is checked with the same
camera cropped (see docs/sofa-3d-review/ext007-sofa-curvo.md).

Parametric EXTERIOR-ONLY source. Regenerates in ONE pass (never edit the .blend/GLBs by hand):
    LD_LIBRARY_PATH=<gl libs> .agents/venv/bin/python assets/models-3d/stanza-curved-arm-01/source/build.py
writes models/stanza-curved-arm-01.glb, models/stanza-curved-arm-01-mobile.glb,
source/stanza-curved-arm-01.blend and source/metrics.json.

Axes (Blender): X width, -Y FRONT, Z up; origin = centre of the footprint on the floor.
All dimensions are ESTIMATES (camera/proportion fit to 11 correspondences, f 600 px, seat pad
top at the front fixed at 0.43 m; depth is NOT constrained by the near-frontal view).

Construction read from the photos: a low upholstered hull on a slim wooden base (four legs
and a rail at their top, visible next to the legs); each end is a thick ARM whose front-view
profile is a real curve - vertical outer face, rounded outer shoulder, and an elliptical
convex sweep down to the seat; a low back panel. A quilted (tufted) velvet pad lies on the
seat, against the back and over both arms (hanging down their outsides). Six square
knife-edge velvet pillows stand along the back.

Material regions (`stanza_region`):
  body               fabric_main, fabric_seam   (hull, arms, back, quilted seat/back/arm pads + seams)
  decorative         pillow_velvet, pillow_seam (six loose knife-edge pillows: QUEUE rule, fixed)
  exterior-structure base_wood                  (legs + rail, wood-wenge, fixed)
"""
import sys, json, math, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE.parent
REPO = MODEL_DIR.parents[2]
sys.path.insert(0, str(MODEL_DIR.parent / 'lib'))
import bpy
import numpy as np
from PIL import Image
import stanza3d as S
from mathutils import Vector
from mathutils.kdtree import KDTree

MODEL_ID = 'stanza-curved-arm-01'
REVISION = '1.0.0'
EMBEDDED = {'fabricId': 'velvet', 'colorId': 'musgo'}
_hex = json.loads((REPO/'assets'/'models-3d'/'materials'/'materials.json').read_text())['tints']['musgo']
TINT = tuple(int(_hex[i:i+2], 16) for i in (1, 3, 5))   # = COLORS.musgo in sofa-viewer.js
REGIONS = {'body': ['fabric_main', 'fabric_seam'], 'decorative': ['pillow_velvet', 'pillow_seam'], 'exterior-structure': ['base_wood']}
VELVET = REPO/'assets'/'sofa-pilot'/'materials'/'velvet'
TILES = 2          # embedded velvet pre-tiled 2x per body UV unit (as EXT-014)

# ---------------------------------------------------------------- proportions (estimated, m)
W = 2.07          # outer faces of the arms (fit 2.13 at the silhouette, which includes the pads hanging outside)
D = 0.95          # depth (ASSUMED: the near-frontal view does not constrain it)
HL = 0.21         # underside of the hull = top of the wooden base (fit 0.207)
DECK = 0.37       # top of the hull between the arms
PT = 0.068        # quilted pad thickness (seat top at the front edge ~0.43)
ZT = 0.715        # arm top (fit 0.71)
XO = W/2          # arm outer face
XI = 0.70         # arm inner foot at the deck, FRONT (fit: seat front corners at +-0.71)
XI_BACK = 0.88    # ... at the back: the arms' inner sweep recedes outward in plan (pillow edges at -0.85 in SOFA-9)
AR = 0.075        # arm edge radius
UNDER = 0.075     # inward curl of the arm's outer face at the base
NEXP = 1.8        # power of the arm shoulder sweep: flat rounded top, ~60 deg rise at the foot (SOFA-9 rim)
BACK_T = 0.15     # back panel thickness at the deck
BACK_TOP = 0.64      # low back: hidden behind the pillows in SOFA-9 (pillow tops ~0.70)
BACK_LEAN = math.radians(9)
LEG = 0.042; LEG_X = 0.925; LEG_Y = 0.375; RAIL_H = 0.032; RAIL_T = 0.024
HANG = {'l': 0.58, 'r': 0.50}   # bottom of the pad hanging outside each arm (right hangs lower in SOFA-9)
PILLOWS = [  # x, behind?, rot (lean, roll, yaw): read from SOFA-9 (centres -0.66 -0.35 -0.06 0.30 0.56 0.78)
    (-0.63, False, (-20, -8, 7)), (-0.38, True, (-17, 2, -3)), (0.0, False, (-20, 1, 2)),
    (0.29, False, (-20, -2, -4)), (0.57, True, (-17, 3, 5)), (0.70, False, (-21, 12, -6))]
PH = (0.18, 0.16)   # pillow half size (0.36 x 0.32 m; SOFA-9 widths ~0.35, tops ~0.70)

def smooth(t): t = max(0.0, min(1.0, t)); return t*t*(3-2*t)

def xi(y):
    """Inner foot of the arm sweep at depth y: the arms curve outward towards the back (plan)."""
    return XI+(XI_BACK-XI)*smooth((y+D/2)/(D*.62))

def ztop(ax, y=-D/2):
    """Arm top height at |x| = ax, depth y: power-curve shoulder sweep from the deck (xi) to the top."""
    c = XO-AR; x0 = xi(y)
    if ax >= c: return ZT
    if ax <= x0: return DECK
    u = (c-ax)/(c-x0)
    return DECK+(ZT-DECK)*(1-u**NEXP)

def arm_warp(p):
    """Box column -> curved arm: every column is scaled so its top follows ztop(|x|)."""
    ax = abs(p.x); zt = ztop(ax, p.y); z = HL+(p.z-HL)*(zt-HL)/(ZT-HL)
    # the outer face curves in towards the base (C profile in front view, SOFA-9)
    tuck = UNDER*max(0.0, 1-(z-HL)/.22)**2*smooth((ax-(XO-.26))/.26)
    return Vector((p.x-math.copysign(tuck, p.x), p.y, z))

def back_y(z): return D/2-BACK_T+math.tan(BACK_LEAN)*max(0.0, z-DECK)   # inner face of the back

def back_warp(p):
    return Vector((p.x, p.y+math.tan(BACK_LEAN)*max(0.0, p.z-DECK), p.z))

def tuft(u, v, pitch=(.20, .19), dip=.010, line=.0025):
    """Quilting relief at surface coords (u, v): round tuft dimples on a grid + shallow stitched channels."""
    gu, gv = u/pitch[0], v/pitch[1]
    du = (gu-round(gu))*pitch[0]; dv = (gv-round(gv))*pitch[1]
    return dip*math.exp(-(du*du+dv*dv)/.028**2)+line*(math.exp(-(du/.010)**2)+math.exp(-(dv/.010)**2))*.5

def arm_contour(sx, hang, y, n=160):
    """Polyline (x, z) on the arm surface from the inner foot over the shoulder and down the
    outer face to `hang`, with arc length and outward normals (sx = -1 left, +1 right)."""
    pts = []
    for k in range(n+1):
        x0 = xi(y); ax = x0-.02+(XO-AR-(x0-.02))*k/n; pts.append((ax, ztop(ax, y) if ax > x0 else DECK-(x0-ax)*.6))
    for k in range(1, 25):
        a = k/24*math.pi/2; pts.append((XO-AR+AR*math.sin(a), ZT-AR+AR*math.cos(a)))
    zz = ZT-AR
    while zz > hang+1e-6:
        zz = max(hang, zz-.02); pts.append((XO, zz))
    P = np.array(pts); P[:, 0] *= sx
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)])
    T = np.gradient(P, s, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]
    # outward normal: tangent rotated CCW on the right arm, CW on the (mirrored) left arm
    N = np.stack([-T[:, 1], T[:, 0]], 1) if sx > 0 else np.stack([T[:, 1], -T[:, 0]], 1)
    return P, s, N

def contour_warp(C, L, y0, gap):
    """Local box (x = arc length 0..L, y = depth, z = thickness 0..PT) -> pad lying on the arm
    contours C [(y, P, s, N)] (normalised arc parameter, interpolated in depth)."""
    ys = [c[0] for c in C]
    def at(c, tn):
        _y, P, s, N = c; t = tn*s[-1]; i = int(np.searchsorted(s, t)); i = min(max(i, 1), len(s)-1)
        a = (t-s[i-1])/(s[i]-s[i-1]); return P[i-1]*(1-a)+P[i]*a, N[i-1]*(1-a)+N[i]*a
    def f(p):
        tn = min(max(p.x/L, 0.0), 1.0); t = tn*L
        j = int(np.searchsorted(ys, p.y)); j = min(max(j, 1), len(ys)-1); b = min(max((p.y-ys[j-1])/(ys[j]-ys[j-1]), 0.0), 1.0)
        (c0, n0), (c1, n1) = at(C[j-1], tn), at(C[j], tn)
        c = c0*(1-b)+c1*b; n = n0*(1-b)+n1*b; n /= np.linalg.norm(n)
        th = p.z+gap
        if p.z > PT*.55: th -= tuft(t, p.y-y0)*smooth((p.z-PT*.55)/(PT*.45))
        return Vector((c[0]+n[0]*th, p.y, c[1]+n[1]*th))
    return f

def soften(ob, colliders, radius, bulge=.45):
    """Local soft compression of a placed cover against `colliders` [(bvh, clearance)] (as EXT-014)."""
    bpy.context.view_layer.update()
    M = ob.matrix_world; Mi = M.inverted()
    P0 = [M@v.co for v in ob.data.vertices]
    P1 = S.settle_contacts(P0, [tuple(f.vertices) for f in ob.data.polygons], colliders, radius=radius, bulge=bulge, iterations=14)
    for v, p in zip(ob.data.vertices, P1): v.co = Mi@p
    ob.data.update(); bpy.context.view_layer.update()
    kd = KDTree(len(P0))
    for i, p in enumerate(P0): kd.insert(p, i)
    kd.balance()
    def follow(pts):
        out = []
        for p in pts:
            p = Vector(p); acc = Vector(); ws = 0
            for _c, i, dist in kd.find_n(p, 6):
                wgt = 1/(dist+1e-4); acc += (P1[i]-P0[i])*wgt; ws += wgt
            out.append(p+acc/ws)
        return out
    return follow, max((a-b).length for a, b in zip(P0, P1))

def seam_on(name, rb, face, ob, follow, parent, mat, samples, sides, r=.0026):
    pts = rb.seam_loop(face, samples=samples, lift=0)
    bvh = S.collider([tuple(ob.matrix_world@v.co) for v in ob.data.vertices], [tuple(f.vertices) for f in ob.data.polygons])
    pts = S.snap(follow(pts), [bvh], lift=.0011, reach=.05)
    S.tube(name, pts, r, parent, mat, sides=sides)

def velvet_maps(tmp, base, normal, rough):
    """Embedded maps of the shared velvet family (by reference), base colour pre-tinted with
    TINT (map x tint, like generate_materials.tinted) and pre-tiled TILES x TILES (as EXT-014)."""
    def tiled(im, size):
        t = im.resize((size//TILES, size//TILES), Image.Resampling.BOX); o = Image.new(im.mode, (size, size))
        for i in range(TILES):
            for j in range(TILES): o.paste(t, (i*size//TILES, j*size//TILES))
        return o
    col = np.asarray(Image.open(VELVET/'basecolor.jpg').convert('RGB')).astype(float)/255
    im = Image.fromarray(np.uint8(np.round(np.clip(col*np.array(TINT)/255, 0, 1)*255)))
    out = {}
    p = tmp/f'basecolor-musgo-{base}.jpg'; tiled(im, base).save(p, quality=90, subsampling=0, optimize=True); out['basecolor'] = p
    for kind, size, ext in (('normal', normal, 'png'), ('roughness', rough, 'jpg')):
        p = tmp/f'{kind}-{size}.{ext}'; tiled(Image.open(VELVET/f'{kind}.{ext}').convert('RGB'), size).save(p, **({'quality': 90} if ext == 'jpg' else {}))
        out[kind] = p
    return out

class Warped(S.RoundedBox):
    """RoundedBox mapped through `fn` (seam_loop welts follow)."""
    def __init__(self, *a, fn=None, **k): super().__init__(*a, **k); self.fn = fn
    def point(self, q):
        p, n = super().point(q)
        return self.fn(p), n

def build(mobile=False, placements=None):
    S.reset()
    P_ = placements or {}
    Q = .45 if mobile else 1.0
    def m(v): return max(1, int(round(v*Q)))
    root = S.empty('model_root', None, modelId=MODEL_ID, revision=REVISION, construction='exterior-only',
                   dimensions_estimated=True, reference='sofas/SOFA-9.png', catalogId='sofa-curvo', queue='EXT-007',
                   materialRegions=REGIONS, embeddedFinish=EMBEDDED, embeddedTiles=TILES, bodyUvMeters=S.BODY_UV_METERS)
    groups = {n: S.empty(n, root) for n in ('upholstery', 'legs', 'cushions')}
    tmp = Path(tempfile.mkdtemp())
    fmaps = velvet_maps(tmp, 512 if mobile else 1024, 256 if mobile else 1024, 256)
    cloth = S.textured('fabric_main', fmaps, 'body', .38, .72, .55)
    seam = S.textured('fabric_seam', fmaps, 'body', .38, .72, .55)
    # pillows: the same velvet as in the photo, FIXED (never recoloured; QUEUE rule for loose pillows)
    pillow = S.textured('pillow_velvet', fmaps, 'decorative', .38, .72, .55)
    pseam = S.textured('pillow_seam', fmaps, 'decorative', .38, .72, .55)
    wood = S.textured('base_wood', S.library_maps('wood-wenge', base=256 if mobile else 512, normal=256, rough=256), 'exterior-structure', .4, roughness=None)
    up = groups['upholstery']; e = 3 if not mobile else 2; sides = 4
    # ------------------------------------------------------------ wooden base: 4 legs + rail at their top
    S.plinth('wood_base', groups['legs'], wood, -LEG_X-LEG/2, LEG_X+LEG/2, -LEG_Y-LEG/2, LEG_Y+LEG/2, HL+.004, RAIL_H, RAIL_T, LEG)
    # ------------------------------------------------------------ hull + curved arms + back
    hull = S.RoundedBox((0, 0, (HL+DECK)/2), (2*(XO-.12), D, DECK-HL), .05, mid=(m(24), m(6), 2), edge=e,
                        crown={'-y': .008}, wrinkle=.0006, seed=3)
    hull.build('hull', up, cloth)
    arms = {}
    for side, sx in (('l', -1), ('r', 1)):
        cx = sx*(XO+XI-.03)/2
        rb = Warped((cx, 0, (HL+ZT)/2), (XO-XI+.03, D, ZT-HL), AR, mid=(m(18), m(8), m(12)), edge=e,
                    crown={'-y': .004, '+y': .004}, wrinkle=.0006, seed=5+sx, fn=arm_warp)
        rb.build(f'arm_{side}', up, cloth); arms[side] = rb
    back = Warped((0, D/2-BACK_T/2, (HL+BACK_TOP)/2), (2*(XO-.03), BACK_T, BACK_TOP-HL), .06, mid=(m(24), 2, m(5)), edge=e,
                  crown={'+z': .004, '-y': .004}, wrinkle=.0006, seed=7, fn=back_warp)
    back.build('back_panel', up, cloth)
    rigid = [(hull.collider(), -.0025), (arms['l'].collider(), -.0025), (arms['r'].collider(), -.0025), (back.collider(), -.0025)]
    # ------------------------------------------------------------ quilted pads (body)
    yb = back_y(DECK+PT)
    sp_f = -D/2-.012
    seat = Warped((0, (sp_f+yb)/2, DECK+PT/2-.002), (2*XI+.01, yb-sp_f+.004, PT), .03, mid=(m(40), m(20), 1), edge=e,
                  crown={'+z': .010, '-y': .006}, wrinkle=.0010, seed=11,
                  fn=lambda p: Vector((p.x*(xi(p.y)+.005)/(XI+.005), p.y, p.z-(tuft(p.x+.10, p.y-sp_f-.11) if p.z > DECK+PT*.6 else 0)*smooth((p.z-DECK-PT*.6)/(PT*.4)))))
    seat.build('seat_pad', up, cloth)
    fs, ds = soften(seat.object, rigid, radius=.06); print('SOFT seat', round(ds, 4))
    seam_on('seat_pad_seam', seat, '+z', seat.object, fs, up, seam, m(180), sides)
    bp_h = BACK_TOP+.03-(DECK+PT)
    def bp_warp(p):
        z = p.z; y = back_y(z)-(D/2-BACK_T-p.y)
        if p.y < D/2-BACK_T-PT*.55: y += tuft(p.x+.10, z-DECK-.02, pitch=(.20, .17))*smooth((D/2-BACK_T-PT*.55-p.y)/(PT*.45))
        return Vector((p.x, y, z))
    bpad = Warped((0, D/2-BACK_T-PT/2+.002, DECK+PT+bp_h/2-.01), (2*XI_BACK-.02, PT, bp_h), .03, mid=(m(40), 1, m(9)), edge=e,
                  crown={'-y': .010, '+z': .004}, wrinkle=.0010, seed=13, fn=bp_warp)
    bpad.build('back_pad', up, cloth)
    fb, db = soften(bpad.object, rigid+[(seat.collider(), -.002)], radius=.06); print('SOFT back pad', round(db, 4))
    seam_on('back_pad_seam', bpad, '-y', bpad.object, fb, up, seam, m(170), sides)
    apads = {}
    for side, sx in (('l', -1), ('r', 1)):
        y0 = -D/2+.02; y1 = back_y(DECK)+.012
        C = [(y,)+arm_contour(sx, HANG[side], y) for y in np.linspace(y0-.03, y1+.03, 14)]
        L = float(np.mean([c[2][-1] for c in C]))
        rb = Warped((L/2, (y0+y1)/2, PT/2), (L, y1-y0, PT), .028, mid=(m(30), m(18), 1), edge=e,
                    crown={'+z': .008}, wrinkle=.0010, seed=17+sx, fn=contour_warp(C, L, y0, -.003))
        rb.build(f'arm_pad_{side}', up, cloth); apads[side] = rb
        fa, da = soften(rb.object, rigid+[(seat.collider(), -.002), (bpad.collider(), -.002)], radius=.06); print('SOFT arm pad', side, round(da, 4))
        seam_on(f'arm_pad_{side}_seam', rb, '+z', rb.object, fa, up, seam, m(200), sides)
    # ------------------------------------------------------------ six loose pillows (decorative)
    soft = lambda bvhs, c: [(b, c) for b in bvhs]
    base_col = [seat.collider(), bpad.collider(), apads['l'].collider(), apads['r'].collider()]
    n_p = 20 if not mobile else 12
    pls = []
    order = [k for k, p in enumerate(PILLOWS) if p[1]]+[k for k, p in enumerate(PILLOWS) if not p[1]]
    placed = {}
    for k in order:
        x, behind, rot = PILLOWS[k]
        lc = S.LooseCushion(f'pillow_{k+1}', (x, yb-.30, 1.05), rot,
                            dict(n=n_p, size=PH, seed=31+k, loft=.100, concave=(.06, .06)))
        neigh = [placed[j].collider() for j in placed if abs(j-k) == 1 and PILLOWS[j][1] and abs(PILLOWS[j][0]-x) < 2*PH[0]]   # overlapping (in x) pillows behind
        if lc.name in P_: lc.pos = tuple(P_[lc.name]['pos'])
        else:
            lc.pos = S.solve_rest(S.pillow_shape(**lc.shape)[0], lc.pos, lc.rot, [base_col[0]]+base_col[2:], (0, 0, -1), .010, travel=.7, step_samples=3)
            lc.solve([base_col[1]]+neigh, [((0, 1, 0), .010)])   # back pad (+ the pillows behind) only: the seat contact is already solved
        touch = [placed[j].collider() for j in placed if abs(j-k) == 1]   # every placed neighbour: mutual soft contact
        lc.settle(soft(base_col, -.0015)+soft(touch, -.0008))
        placed[k] = lc
    for k in range(len(PILLOWS)):
        placed[k].build(groups['cushions'], pillow, pseam, .0018); pls.append(placed[k])
    # ------------------------------------------------------------ export
    bpy.context.view_layer.update()
    tris, per = S.triangle_count(True)
    name = MODEL_ID+('-mobile' if mobile else '')
    dest = MODEL_DIR/'models'/(name+'.glb')
    S.export_variant(dest, None if mobile else HERE/(MODEL_ID+'.blend'))
    placements = {c.name: {'pos': [round(v, 4) for v in c.pos], 'rot': list(c.rot)} for c in pls}
    print('EXPORTED', dest, 'tris', tris)
    return {'triangles_blender': tris, 'trianglesByObject': per, 'placements': placements}

if __name__ == '__main__':
    out = {'main': build(False)}
    out['mobile'] = build(True, out['main']['placements'])
    for v, path in (('main', MODEL_ID+'.glb'), ('mobile', MODEL_ID+'-mobile.glb')):
        out[v].update(S.glb_metrics(MODEL_DIR/'models'/path))
    (HERE/'metrics.json').write_text(json.dumps(out, indent=2)+'\n', encoding='utf-8')
    for v in out: print(v, out[v]['triangles'], out[v]['bytes'], out[v]['boundsMeters']['dimensions'])
