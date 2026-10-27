"""EXT-014 - Poltrona azul com braços (catálogo `poltrona-bracos`, portfólio `projeto-24`).
Reference: poltronas/poltronas-11.jpg (1040x780, single angle; the photo shows TWO identical
armchairs and a capitonê pouf: only ONE armchair is modelled - the near/left one; the pouf is
EXT-034, out of scope; room, rug and other objects are not modelled).

Parametric EXTERIOR-ONLY source. Regenerates in ONE pass (never edit the .blend/GLBs by hand):
    LD_LIBRARY_PATH=<gl libs> .agents/venv/bin/python assets/models-3d/stanza-armchair-01/source/build.py
writes models/stanza-armchair-01.glb, models/stanza-armchair-01-mobile.glb,
source/stanza-armchair-01.blend and source/metrics.json.

Axes (Blender): X width, -Y FRONT, Z up; origin = centre of the footprint on the floor.
All dimensions are ESTIMATES from one photo (camera/proportion fit to 12 correspondences with
the seat height fixed at 0.44 m, see docs/sofa-3d-review/ext014-poltrona-bracos.md).

Construction read from the photo: a tub (barrel) armchair upholstered down to the floor. ONE
continuous shell runs from the right arm front, around the curved back, to the left arm front
(flat vertical arm fronts, rolled arm tops); in the rear it rises to a tall rounded back that
leans back slightly. Between the arms: a loose boxed seat cushion with a convex front and
self welts on the top and bottom edges, on a recessed upholstered drum base with a convex front.
No loose pillows, no contrast piping/buttons, no visible feet or wood (the swivel base, if any,
is hidden): every surface is the body fabric (velvet).

Material regions (`stanza_region`):
  body      fabric_main, fabric_seam   (shell, drum base, seat cushion and its welts)
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

MODEL_ID = 'stanza-armchair-01'
REVISION = '1.0.0'
EMBEDDED = {'fabricId': 'velvet', 'colorId': 'petroleo'}
_hex = json.loads((REPO/'assets'/'models-3d'/'materials'/'materials.json').read_text())['tints']['petroleo']
TINT = tuple(int(_hex[i:i+2], 16) for i in (1, 3, 5))   # = COLORS.petroleo in sofa-viewer.js (#0e5668)
REGIONS = {'body': ['fabric_main', 'fabric_seam']}
VELVET = REPO/'assets'/'sofa-pilot'/'materials'/'velvet'
TILES = 2          # embedded velvet pre-tiled 2x per body UV unit (0.30 m): 0.15 m vs the family's 0.14 m

# ---------------------------------------------------------------- proportions (estimated, m)
HS = 0.44         # seat height (ASSUMPTION that fixes the scale)
W = 0.92          # overall width at the arms (fit 0.84-0.97)
D = 0.84          # footprint depth at the floor (the back leans out above the arms)
T = 0.155         # shell (arm/back) thickness (fit 0.13-0.16)
HA = 0.72         # arm top (fit 0.77; rounded top -> the visible silhouette sits ~2 cm lower)
HB = 1.04         # back top (fit 1.09-1.11 at the leaned top corners; adopted slightly lower as an estimate)
ST = 0.17         # seat cushion thickness (fit 0.146-0.159; overlay re-read: the cushion front is ~0.9x the visible drum)
BASE_TOP = HS-ST  # top of the drum base = 0.27
A = W/2-T/2       # shell centre line: half width of the arm straights / radius of the rear arc
BE = 0.78*A       # rear arc is a half ELLIPSE (semi-axes A x BE): the back reads broad and flat, not round
YC = D/2-.01-BE-T/2   # centre of the rear arc (back outer face at the floor ~0.41)
LS = YC+D/2       # straight arm length
LQ = math.pi/4*(A+BE)   # quarter-arc length (parameter, near-uniform)
RIN = A-T/2       # inner half width
BIN = BE-T/2      # inner rear semi-axis
LEAN = math.radians(5)
TH0, TH1 = math.radians(70), math.radians(85)    # back -> arm transition of the shell height (from the back centre)
WELT_R = 0.003

def smooth(t): t = max(0.0, min(1.0, t)); return t*t*(3-2*t)

def shell_h(s):
    th = abs(s)/LQ*math.pi/2 if abs(s) <= LQ else math.pi/2+(abs(s)-LQ)/A
    return HA+(HB-HA)*(1-smooth((th-TH0)/(TH1-TH0)))

def shell_warp(p):
    """Box (x = arc length s along the U centre line, y = thickness, +y outward, z = height)
    -> U-shaped tub shell; the height follows shell_h(s), the back leans out above the seat."""
    s, t, z = p.x, p.y, p.z
    h = shell_h(s); z2 = z*h/HB
    if abs(s) <= LQ:
        th = s/LQ*math.pi/2; pos = Vector((A*math.sin(th), YC+BE*math.cos(th))); nrm = Vector((math.sin(th)/A, math.cos(th)/BE)).normalized()
    else:
        sg = 1 if s > 0 else -1; pos = Vector((sg*A, YC-(abs(s)-LQ))); nrm = Vector((sg, 0))
    wb = (h-HA)/(HB-HA)
    off = t + wb*math.tan(LEAN)*max(0.0, z2-.30)**1.15 + .008*z2/HA
    q = pos+nrm*off
    return Vector((q.x, q.y, z2))

def plan_warp(bulge, front_y):
    """Seat cushion / drum base plan: convex front (bulge at the centre) and the rear rounded
    into the shell's inner arc (radius RIN about YC)."""
    def f(p):
        x, y, z = p.x, p.y, p.z
        hw = RIN+.012
        u = max(-1.0, min(1.0, x/hw))
        if y > YC:
            k = math.sqrt(max(0.0, 1-((y-YC)/(BIN+.010))**2)); x *= max(.30, k)
        wf = max(0.0, min(1.0, (YC-y)/(YC-front_y)))**3
        y -= bulge*(1-u*u)*wf
        return Vector((x, y, z))
    return f

class Warped(S.RoundedBox):
    """RoundedBox whose surface (and seam_loop welts) is mapped through `fn` (world -> world)."""
    def __init__(self, *a, fn=None, **k): super().__init__(*a, **k); self.fn = fn
    def point(self, q):
        p, n = super().point(q)
        return self.fn(p), n

def soften(ob, colliders, radius, bulge=.45):
    """Local soft compression of a placed cushion against `colliders` [(bvh, clearance)]
    (S.settle_contacts, as EXT-005). Returns follow(points) carrying welts along."""
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

def welt_on(name, rb, face, ob, follow, parent, mat, samples, sides):
    pts = rb.seam_loop(face, samples=samples, lift=0)
    bvh = S.collider([tuple(ob.matrix_world@v.co) for v in ob.data.vertices], [tuple(f.vertices) for f in ob.data.polygons])
    pts = S.snap(follow(pts), [bvh], lift=.0012, reach=.05)
    S.tube(name, pts, WELT_R, parent, mat, sides=sides)

def velvet_maps(tmp, base, normal, rough):
    """Embedded maps of the shared velvet family (assets/sofa-pilot/materials/velvet, by
    reference): base colour pre-tinted with TINT (map x tint, like generate_materials.tinted),
    so the viewer's white multiplier gives exactly velvet x petroleo. The family repeats every
    0.14 m while the body UV unit is 0.30 m: every map is pre-tiled TILES x TILES (seamless)."""
    def tiled(im, size):
        t = im.resize((size//TILES, size//TILES), Image.Resampling.BOX); o = Image.new(im.mode, (size, size))
        for i in range(TILES):
            for j in range(TILES): o.paste(t, (i*size//TILES, j*size//TILES))
        return o
    col = np.asarray(Image.open(VELVET/'basecolor.jpg').convert('RGB')).astype(float)/255
    im = Image.fromarray(np.uint8(np.round(np.clip(col*np.array(TINT)/255, 0, 1)*255)))
    out = {}
    p = tmp/f'basecolor-petroleo-{base}.jpg'; tiled(im, base).save(p, quality=90, subsampling=0, optimize=True); out['basecolor'] = p
    for kind, size, ext in (('normal', normal, 'png'), ('roughness', rough, 'jpg')):
        p = tmp/f'{kind}-{size}.{ext}'; tiled(Image.open(VELVET/f'{kind}.{ext}').convert('RGB'), size).save(p, **({'quality': 90} if ext == 'jpg' else {}))
        out[kind] = p
    return out

def build(mobile=False):
    S.reset()
    Q = .55 if mobile else 1.0
    def m(v): return max(1, int(round(v*Q)))
    root = S.empty('model_root', None, modelId=MODEL_ID, revision=REVISION, construction='exterior-only',
                   dimensions_estimated=True, reference='poltronas/poltronas-11.jpg', catalogId='poltrona-bracos', queue='EXT-014',
                   materialRegions=REGIONS, embeddedFinish=EMBEDDED, embeddedTiles=TILES, bodyUvMeters=S.BODY_UV_METERS)
    groups = {n: S.empty(n, root) for n in ('upholstery', 'legs', 'cushions')}
    tmp = Path(tempfile.mkdtemp())
    fmaps = velvet_maps(tmp, 512 if mobile else 1024, 256 if mobile else 1024, 256)
    cloth = S.textured('fabric_main', fmaps, 'body', .38, .72, .55)
    seam = S.textured('fabric_seam', fmaps, 'body', .38, .72, .55)
    up = groups['upholstery']; e = 4 if not mobile else 3
    sides = 6 if not mobile else 4
    # ------------------------------------------------------------ tub shell: arms + curved back in one piece
    L = 2*LS+2*LQ
    shell = Warped((0, 0, HB/2), (L, T, HB), .07, mid=(m(110), 3, m(26)), edge=e if not mobile else 3,
                   crown={'-y': .022, '+y': .008, '+z': .006, '-x': .004, '+x': .004}, wrinkle=.0007, seed=4, fn=shell_warp)
    shell.build('shell', up, cloth)
    # ------------------------------------------------------------ drum base (recessed, convex front)
    bf = -D/2+.035; bb = YC+BIN*.88
    base = Warped((0, (bf+bb)/2, BASE_TOP/2), (2*RIN-.004, bb-bf, BASE_TOP), .03, mid=(m(24), m(14), m(3)), edge=e,
                  crown={'-y': .004}, wrinkle=.0005, seed=6, fn=plan_warp(.075, bf))
    base.build('drum_base', up, cloth)
    # ------------------------------------------------------------ loose boxed seat cushion (filled, convex front, self welts)
    sf = -D/2-.005; sb = YC+BIN*.86
    seat = Warped((0, (sf+sb)/2, BASE_TOP+ST/2+.0005), (2*RIN+.014, sb-sf, ST), .05, mid=(m(26), m(24), m(5)), edge=5 if not mobile else 4,
                  crown={'+z': .028, '-y': .012, '-z': .002, '+x': .004, '-x': .004}, wrinkle=.0014, seed=11, fn=plan_warp(.06, sf))
    seat.build('seat_cushion', groups['cushions'], cloth)
    # soft contact: the 7 mm oversize presses into the shell's inner faces (3 mm left as shared squash)
    fseat, ds = soften(seat.object, [(shell.collider(), -.003), (base.collider(), -.0015)], radius=.07)
    print('SOFT seat squash', round(ds, 4))
    for f in ('+z', '-z'):
        welt_on(f'seat_cushion_welt_{"top" if f == "+z" else "bottom"}', seat, f, seat.object, fseat, groups['cushions'], seam, m(200) if not mobile else 110, sides)
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
