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
upholstered base band; two wide boxed seat cushions with light welts on the top and
bottom edges; a back panel behind two large BOXED back cushions (welts around the front and
back faces) leaning back. No decorative pillows.

1.1.0 (cushions): the cushions read FILLED, not as rigid slabs: seat 0.13 -> 0.165 m with a
domed top and a soft front roll; back cushions with a full belly (front crown 65 mm), rounded
sagging top outline with a slight wave and a forward slump (SoftBox). After the rigid rest
(`rest_rigid`) each contact becomes LOCAL SOFT COMPRESSION (`soften` = S.settle_contacts):
the seat dents under the back-cushion bottom, the back cushion flattens on the dented seat and
on the back panel's front; the welts are carried by the same deformation and re-snapped onto
the deformed covers.

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
from mathutils import Vector
from mathutils.kdtree import KDTree

class SoftBox(S.RoundedBox):
    """RoundedBox + filled-cushion shaping (1.1.0), in the box's local frame and applied to every
    point, so seam_loop() welts follow it: `droop` lowers the top corners (rounded, sagging top
    outline), `wave` ripples the top edge, `slump` leans the upper part forward over the belly,
    `belly` fills the lower front, `roll` rolls the front-top edge of a seat cushion forward.
    `wrinkle` is re-implemented CONTINUOUSLY here (the library's picks its axes from the dominant
    normal, which jumps at the 45-degree seam line and creased dense rounded bands)."""
    def __init__(self, *a, droop=0.0, wave=0.0, slump=0.0, belly=0.0, roll=0.0, wrinkle=0.0, **k):
        super().__init__(*a, wrinkle=0.0, **k); self.soft = (droop, wave, slump, belly, roll); self.wr = wrinkle
    def point(self, q):
        p, n = super().point(q)
        droop, wave, slump, belly, roll = self.soft; h, r = self.h, self.r
        l = p-self.c; u, v, w = l.x/h[0], l.y/h[1], l.z/h[2]     # from the ROUNDED point (smooth across bands)
        d = Vector()
        if self.wr:
            uvw = sorted(abs(max(-(h[k]-r), min(h[k]-r, q[k])))/(h[k]-r) if h[k]-r > 1e-9 else 0 for k in range(3))
            x, y, z = p.x, p.y, p.z; sd = self.seed
            wv = math.sin(41*x+23*y+31*z+sd)*math.sin(17*y-29*x+13*z+1.7*sd)+.5*math.sin(83*x-61*y+47*z+.3*sd)
            d += n*(self.wr*uvw[1]**6*wv)
        tz = max(0.0, w)
        d.z -= droop*tz**2*u**4
        d.z += wave*math.sin(2.6*math.pi*u+.7*self.seed)*tz**4
        d.y -= slump*tz**2
        d.y -= belly*max(0.0, -v)*(1-u*u)*math.exp(-((w+.3)/.5)**2)
        d.y -= roll*max(0.0, -v)**2*(1-u**6)*max(0.0, w+.2)/1.2
        return p+d, n

def soften(ob, colliders, radius, bulge=.45):
    """Local soft compression of a placed cushion cover against `colliders` [(bvh, clearance)]
    (S.settle_contacts on the world-space vertices; written back to the mesh). Returns a
    follow(points_world) function that carries welt points along with the deformation."""
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

class PanelFront:
    """Duck-typed collider (find_nearest like a BVHTree) for the FRONT PLANE of the back panel
    below its top: signed distance along -Y only. Used instead of the panel's closed-shell BVH
    so the soft lean of a back cushion is not fooled by the nearest-feature sign flip at the
    panel's rounded top edge (spikes)."""
    def __init__(self, y0, z_top, half_w): self.y0, self.zt, self.hw = y0, z_top, half_w
    def find_nearest(self, p, reach=.12):
        if p.z > self.zt or abs(p.x) > self.hw or abs(p.y-self.y0) > reach: return None, None, None, None
        return Vector((p.x, self.y0, p.z)), Vector((0, -1, 0)), 0, abs(p.y-self.y0)

def welt_on(name, rb, face, ob, follow, holder, parent, mat, samples, sides):
    """Welt along rb's seam around `face`, carried by the soft deformation and re-snapped onto
    the deformed cover (lift 1.2 mm, like seam_loop), built under `holder` (local) or world."""
    M = holder.matrix_world if holder else None
    pts = rb.seam_loop(face, samples=samples, lift=0)
    if M: pts = [M@Vector(p) for p in pts]
    bvh = S.collider([tuple(ob.matrix_world@v.co) for v in ob.data.vertices], [tuple(f.vertices) for f in ob.data.polygons])
    pts = S.snap(follow(pts), [bvh], lift=.0012, reach=.05)
    if M: Mi = M.inverted(); pts = [tuple(Mi@Vector(p)) for p in pts]
    S.tube(name, pts, WELT_R, holder or parent, mat, sides=sides)

MODEL_ID = 'stanza-piped-01'
REVISION = '1.1.0'
EMBEDDED = {'fabricId': 'sarja', 'colorId': 'cinza-malva'}
REGIONS = {'body': ['fabric_main'], 'contrast': ['piping_light']}

# ---------------------------------------------------------------- proportions (estimated, m)
HS = 0.45         # seat height (ASSUMPTION that fixes the scale)
W = 3.46          # overall width (fit 3.46)
D = 1.00          # overall depth (constrained ~1.0: the rear is not measurable in the photo)
AW = 0.23         # arm width (fit 0.233)
HA = 0.665        # arm height (fit 0.665)
ST = 0.165        # seat cushion thickness (1.1.0: re-read 0.16-0.17, the cushion front is ~0.6x the visible base band)
BASE_TOP = HS-ST  # top of the upholstered base band = 0.285
BT = 0.17         # back panel thickness (assumed)
HB = 0.84         # back panel height (hidden behind the back cushions; assumed)
GAP = 0.006
INNER = W/2-AW
BACK_Y0 = D/2-BT
BACK = dict(h=0.66, t=0.17, lean=15.0)     # boxed back cushion height / box thickness (+ ~8 cm of crowns) / lean (deg); centre sides crown 2 mm (6 mm gap)
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
    # ------------------------------------------------------------ seat cushions (plump boxed, welts top + bottom)
    OVER = 0.02       # seat cushion front overhangs the base band (photo: the cushion front sits proud of the base)
    sw = INNER-GAP*1.5; sd = BACK_Y0-(-D/2)-GAP+OVER
    sides = 5 if not mobile else 4; ec = 5 if not mobile else 4     # denser rounded bands on the soft cushions (no facet creases)
    seats = []
    for k, sx in enumerate((-1, 1)):
        rb = SoftBox((sx*(GAP/2+sw/2), -D/2-OVER+sd/2, BASE_TOP+ST/2+.0005), (sw, sd, ST), .045,
                     mid=(m(26), m(22), m(5)), edge=ec, crown={'+z': .03, '-y': .01, '+x': .003, '-x': .003, '-z': .0015},
                     wrinkle=.0016, seed=11+k, roll=.016)
        rb.build(f'seat_cushion_{k+1}', up, cloth); seats.append(rb)
    # ------------------------------------------------------------ boxed back cushions (tilted, puffy), welts front + back
    lean = math.radians(BACK['lean']); h, t = BACK['h'], BACK['t']
    seat_top = BASE_TOP+ST+.004          # seat cushion top near its back edge (crown fades there)
    backs = []
    for k, sx in enumerate((-1, 1)):
        # local frame: X width, Y thickness (front -Y), Z height; rotated about X so the top goes back (+Y).
        cz = seat_top - .008 + math.cos(lean)*h/2 + math.sin(lean)*t/2
        cy = BACK_Y0 - .003 - (t/2 + (HB - cz)*math.sin(lean))/math.cos(lean)
        holder = S.empty(f'back_cushion_{k+1}', up); holder.location = (sx*(GAP/2+sw/2), cy, cz)
        holder.rotation_euler = (math.radians(-BACK['lean']), 0, 0)
        bc = SoftBox((0, 0, 0), (sw, t, h), .05, mid=(m(26), 6, m(18)), edge=ec,
                     crown={'-y': .065, '+y': .016, '+z': .008, '-z': .004, ('+x' if sx < 0 else '-x'): .002, ('-x' if sx < 0 else '+x'): .005}, wrinkle=.0022, seed=21+k,
                     droop=.03, wave=.006, slump=.018, belly=.014)
        bc.build(f'back_cushion_{k+1}_cover', holder, cloth); bpy.context.view_layer.update()
        # rigid placement first (sink 18 mm into the seat, lean 7 mm onto the panel top) ...
        S.rest_rigid(holder, bc.object, [seats[k].collider()], (0, 0, -1), .018)
        S.rest_rigid(holder, bc.object, [backp.collider()], (0, 1, 0), .007)
        backs.append((bc, holder))
    # ... then local soft compression: the seat dents under the back cushion bottom (6 mm left
    # as shared squash), the back cushion flattens on the dented seat and on the panel top.
    for k in range(2):
        bc, holder = backs[k]
        fseat, ds = soften(seats[k].object, [(bc.collider(), -.006)], radius=.10)
        fback, db = soften(bc.object, [(seats[k].collider(), -.003), (PanelFront(BACK_Y0, HB, INNER+.015), -.004)], radius=.09)
        print('SOFT', k, 'seat dent', round(ds, 4), 'back squash', round(db, 4))
        for f in ('+z', '-z'):
            welt_on(f'seat_cushion_{k+1}_welt_{"top" if f == "+z" else "bottom"}', seats[k], f, seats[k].object, fseat, None, up, pipe, seam_n(190), sides)
        for f in ('-y', '+y'):
            welt_on(f'back_cushion_{k+1}_welt_{f[0].replace("+", "p").replace("-", "n")}{f[1]}', bc, f, bc.object, fback, holder, up, pipe, seam_n(190), sides)
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
