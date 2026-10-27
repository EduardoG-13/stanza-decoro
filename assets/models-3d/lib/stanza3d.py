"""stanza3d - shared generator library for the Stanza Decoro exterior 3D collection.

Run inside Blender's Python (bpy 5.0.1 module or Blender >= 5.0 --background --python).
Each model keeps its own parametric source (assets/models-3d/<modelId>/source/build.py) and
imports this module for the reusable parts:

  scene/mesh   reset(), empty(), mesh(), tube(), triangle_count()
  upholstery   RoundedBox (bevelled/subdivided box with soft crowns, wrinkles, seam loops)
  loose parts  pillow_shape() knife-edge cushion, collider(), solve_rest(), settle_contacts()
               (ported from assets/sofa-pilot/source/build_sofa.py, EXT-001, unchanged maths)
  structure    block() bevelled wood/metal block, plinth() apron frame + block feet
  materials    material(), textured(), library maps in assets/models-3d/materials/
               and the reused EXT-001 families in assets/sofa-pilot/materials/
  export       export_variant(): GLB (+ derived .blend for the main variant)
  metadata     glb_metrics(): bytes, sha256, triangles, bounds, embedded images

Conventions (same as EXT-001): metres; Blender X = width, -Y = FRONT, Z = up; the glTF
exporter writes Y-up, +Z front. Body fabric UVs: 1 UV unit = BODY_UV_METERS (0.30 m) so every
body fabric family can be swapped by the viewer with texture.repeat = BODY_UV_METERS/repeat.
Material regions: custom property `stanza_region` (body | decorative | contrast |
exterior-structure) exported as glTF material extras; the viewer customizes ONLY `body`.
Exterior only: never model hidden frames, foam, webbing or batting.
"""
import bpy, bmesh, math, json, hashlib, struct
from pathlib import Path
from math import sin, cos, pi, sqrt, exp
from mathutils import Vector, Matrix, Euler

BODY_UV_METERS = .30
REPO = Path(__file__).resolve().parents[3]
LIB_MATERIALS = REPO / 'assets' / 'models-3d' / 'materials'
PILOT_MATERIALS = REPO / 'assets' / 'sofa-pilot' / 'materials'
REGIONS = ('body', 'decorative', 'contrast', 'exterior-structure')

# --------------------------------------------------------------------------- scene / mesh
_IMAGES = {}

def reset():
    for ob in list(bpy.data.objects): bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for item in list(coll): coll.remove(item)
    _IMAGES.clear()

def empty(name, parent=None, **props):
    o = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(o); o.parent = parent
    o['asset_id'] = name
    for k, v in props.items(): o[k] = json.dumps(v) if isinstance(v, (dict, list)) else v
    return o

def mesh(name, verts, faces, parent, mats, uv=None, face_mats=None, smooth=True, uv_fn=None, recalc=True):
    """verts/faces -> object. uv: per-vertex list; uv_fn(co: Vector, face_normal: Vector) -> (u,v)
    per face corner (lets projected UVs split only in UV space, keeping smooth shared normals)."""
    me = bpy.data.meshes.new(name+'_mesh'); me.from_pydata([tuple(v) for v in verts], [], faces); me.update()
    if recalc:
        bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob); ob.parent = parent
    for m in (mats if isinstance(mats, (list, tuple)) else [mats]): me.materials.append(m)
    if face_mats:
        for p in me.polygons: p.material_index = face_mats[p.index]
    for p in me.polygons: p.use_smooth = smooth
    layer = me.uv_layers.new(name='UV')
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            if uv_fn: layer.data[li].uv = uv_fn(Vector(verts[vi]), poly.normal)
            elif uv: layer.data[li].uv = uv[vi]
            else: layer.data[li].uv = (verts[vi][0]/BODY_UV_METERS, verts[vi][2]/BODY_UV_METERS)
    ob['asset_id'] = name
    return ob

def box_uv(tile=BODY_UV_METERS, grain=None):
    """Planar projection by dominant face normal. grain='x'|'y'|'z' puts that axis on U when it
    lies in the projection plane (wood grain runs along U)."""
    def fn(co, n):
        a = max(range(3), key=lambda k: abs(n[k]))
        plane = [k for k in range(3) if k != a]
        if grain is not None and 'xyz'.index(grain) in plane:
            g = 'xyz'.index(grain); plane = [g] + [k for k in plane if k != g]
        return (co[plane[0]]/tile, co[plane[1]]/tile)
    return fn

def tube(name, pts, radius, parent, mat, sides=5, closed=True, tile=BODY_UV_METERS):
    """Welt / seam tube along a polyline (EXT-001 tube(), generalised up-vector handling)."""
    vs = []; uv = []; fs = []; length = 0; n = len(pts)
    for i, p in enumerate(pts):
        p = Vector(p)
        if i: length += (p-Vector(pts[i-1])).length
        a = Vector(pts[(i+1) % n] if closed or i < n-1 else pts[i]); b = Vector(pts[(i-1) % n] if closed or i > 0 else pts[i])
        tangent = (a-b).normalized()
        normal = tangent.cross(Vector((0, 0, 1)))
        if normal.length < .01: normal = tangent.cross(Vector((0, 1, 0)))
        normal.normalize(); bn = tangent.cross(normal).normalized()
        for j in range(sides):
            an = 2*pi*j/sides; vs.append(tuple(p+radius*(normal*cos(an)+bn*sin(an)))); uv.append((length/tile, j/sides*.01/tile))
    for i in range(n if closed else n-1):
        for j in range(sides):
            fs.append((i*sides+j, i*sides+(j+1) % sides, ((i+1) % n)*sides+(j+1) % sides, ((i+1) % n)*sides+j))
    if not closed:
        for end in (0, n-1):
            c = len(vs); ring = vs[end*sides:(end+1)*sides]
            vs.append(tuple(sum(v[k] for v in ring)/sides for k in range(3))); uv.append((0, 0))
            for j in range(sides): fs.append((c, end*sides+j, end*sides+(j+1) % sides))
    return mesh(name, vs, fs, parent, mat, uv)

def triangle_count(per_object=False):
    dg = bpy.context.evaluated_depsgraph_get(); total = 0; per = {}
    for ob in bpy.context.scene.objects:
        if ob.type == 'MESH':
            me = ob.evaluated_get(dg).to_mesh(); n = sum(len(p.vertices)-2 for p in me.polygons); ob.evaluated_get(dg).to_mesh_clear()
            total += n; per[ob.name] = n
    return (total, per) if per_object else total

# --------------------------------------------------------------------------- upholstery
def _axis_samples(h, r, mid, edge):
    """Cube coordinates along one axis: `edge` samples inside each rounded band [h-r, h]
    (denser near the tangent line) and `mid` segments over the flat part."""
    inner = h-r
    band = [inner + r*(k/edge)**.85 for k in range(1, edge+1)]
    flat = [-inner + 2*inner*k/mid for k in range(mid+1)] if inner > 1e-9 else [0.0]
    return [-b for b in reversed(band)] + flat + band

class RoundedBox:
    """Upholstered rounded box (cushion, arm, base band, back panel...).

    center/size in metres (full size), radius = soft edge radius. Built from a subdivided cube
    whose points are projected onto the rounded box (inner box + radius * direction), then
    deformed: `crown` {'+z': m, '-y': m, ...} domes each face (0 at its edges), `wrinkle`
    adds shallow folds near edges/corners, `seed` varies them. seam_loop() returns a welt line
    exactly on the 45-degree line of the rounded edges around a face (where a boxed cover is
    sewn), following every deformation."""
    def __init__(self, center, size, radius, mid=(8, 8, 8), edge=4, crown=None, wrinkle=0.0, seed=0, taper=None):
        self.c = Vector(center); self.h = Vector(size)/2; self.r = min(radius, *[x*.999 for x in self.h])
        self.mid = mid; self.edge = edge; self.crown = crown or {}; self.wrinkle = wrinkle; self.seed = seed
        self.taper = taper    # optional (axis, along, amount): shrinks `axis` linearly along `along`

    def point(self, q):
        """q: cube point (on the box surface of half size h). Returns (world point, normal)."""
        h, r = self.h, self.r
        inner = Vector([max(-(h[k]-r), min(h[k]-r, q[k])) for k in range(3)])
        d = Vector(q)-inner; L = d.length
        n = d/L if L > 1e-12 else Vector((0, 0, 1))
        p = inner+n*r
        uvw = [inner[k]/(h[k]-r) if h[k]-r > 1e-9 else 0 for k in range(3)]
        for key, amt in self.crown.items():
            s = 1 if key[0] == '+' else -1; a = 'xyz'.index(key[1])
            w = max(0.0, n[a]*s)**1.5
            if w <= 0: continue
            f = 1.0
            for k in range(3):
                if k != a: f *= max(0.0, 1-uvw[k]**2)
            p[a] += s*amt*f*w
        if self.wrinkle:
            a = max(range(3), key=lambda k: abs(n[k])); o = [k for k in range(3) if k != a]
            edge = max(abs(uvw[o[0]]), abs(uvw[o[1]]))**6
            sd = self.seed
            wv = sin(41*p[o[0]]+23*p[o[1]]+sd)*sin(17*p[o[1]]-29*p[o[0]]+1.7*sd)+.5*sin(83*p[o[0]]-61*p[o[1]]+.3*sd)
            p += n*(self.wrinkle*edge*wv)
        if self.taper:
            ax, al, amt = self.taper; a = 'xyz'.index(ax); b = 'xyz'.index(al)
            t = (q[b]/h[b]+1)/2; p[a] *= 1-amt*t
        return self.c+p, n

    def build(self, name, parent, mat, tile=BODY_UV_METERS, smooth=True, uv_fn=None):
        h, r = self.h, self.r
        X = [_axis_samples(h[k], r, max(1, self.mid[k]), self.edge) for k in range(3)]
        X = [[max(-h[k], min(h[k], v)) for v in X[k]] for k in range(3)]
        for k in range(3): X[k][0] = -h[k]; X[k][-1] = h[k]
        index = {}; verts = []; faces = []
        def vid(i, j, k):
            key = (i, j, k)
            if key not in index:
                p, _n = self.point((X[0][i], X[1][j], X[2][k])); index[key] = len(verts); verts.append(tuple(p))
            return index[key]
        nx, ny, nz = [len(X[k])-1 for k in range(3)]
        for (a, b, c, last) in ((0, 1, 2, nz), (0, 2, 1, ny), (1, 2, 0, nx)):
            na, nb = [len(X[a])-1, len(X[b])-1]
            for side in (0, last):
                for i in range(na):
                    for j in range(nb):
                        quad = []
                        for (di, dj) in ((0, 0), (1, 0), (1, 1), (0, 1)):
                            idx = [0, 0, 0]; idx[a] = i+di; idx[b] = j+dj; idx[c] = side; quad.append(vid(*idx))
                        faces.append(tuple(quad))
        self.object = mesh(name, verts, faces, parent, mat, smooth=smooth, uv_fn=uv_fn or box_uv(tile))
        return self.object

    def seam_loop(self, face='+z', samples=160, lift=.0012):
        """Points on the rounded edge (45 deg) around a face, slightly lifted along the normal."""
        s = 1 if face[0] == '+' else -1; a = 'xyz'.index(face[1]); o = [k for k in range(3) if k != a]
        h = self.h; pts = []
        corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        per = [2*h[o[0]], 2*h[o[1]], 2*h[o[0]], 2*h[o[1]]]; total = sum(per)
        for e in range(4):
            c0, c1 = corners[e], corners[(e+1) % 4]; m = max(4, int(samples*per[e]/total))
            for t in range(m):
                f = t/m; q = [0, 0, 0]; q[a] = s*h[a]
                q[o[0]] = h[o[0]]*(c0[0]+(c1[0]-c0[0])*f); q[o[1]] = h[o[1]]*(c0[1]+(c1[1]-c0[1])*f)
                p, n = self.point(q); pts.append(tuple(p+n*lift))
        return pts

    def collider(self):
        ob = self.object
        M = ob.matrix_world
        return collider([tuple(M @ v.co) for v in ob.data.vertices], [tuple(p.vertices) for p in ob.data.polygons])

def oriented_box(name, size, radius, pos, rot_deg, parent, mat, welts=(), welt_mat=None, welt_r=.002,
                 samples=150, lift=.0011, mid=(8, 8, 8), edge=4, crown=None, wrinkle=0.0, seed=0, sides=4):
    """Boxed (RoundedBox) cushion built in its local frame (centred at the origin) under an
    empty `name` placed at `pos` with XYZ Euler `rot_deg` (EXT-005: tilted boxed back cushions
    with piping). welts: faces ('+z', '-y', ...) that get a seam_loop() welt tube in welt_mat.
    Returns (RoundedBox, holder); RoundedBox.collider() is in WORLD space (matrix applied)."""
    holder = empty(name, parent); holder.location = tuple(pos); holder.rotation_euler = tuple(math.radians(r) for r in rot_deg)
    rb = RoundedBox((0, 0, 0), size, radius, mid=mid, edge=edge, crown=crown, wrinkle=wrinkle, seed=seed)
    rb.build(name+'_cover', holder, mat)
    for f in welts:
        tube(f'{name}_welt_{f[0].replace("+", "p").replace("-", "n")}{f[1]}', rb.seam_loop(f, samples=samples, lift=lift), welt_r, holder, welt_mat or mat, sides=sides)
    bpy.context.view_layer.update()
    return rb, holder

def rest_rigid(holder, ob, colliders, direction, overlap=.003, travel=.15, samples=2):
    """Translate `holder` (and everything under it) along `direction` until the deepest
    penetration of `ob`'s vertices into `colliders` equals `overlap` (bisection; marches back
    out of a too-deep start). For rigid boxed cushions placed by oriented_box()."""
    bpy.context.view_layer.update()
    d = Vector(direction).normalized(); M0 = ob.matrix_world.copy(); base = Vector(holder.location)
    local = [v.co.copy() for v in ob.data.vertices][::samples]
    def depth(t):
        off = d*t; return penetration([M0@p + off for p in local], colliders)
    lo, hi = None, None; steps = 30; dt = travel/steps
    if depth(0) < overlap:
        lo = 0.0
        for k in range(1, steps+1):
            if depth(k*dt) >= overlap: hi = k*dt; break
            lo = k*dt
    else:
        hi = 0.0
        for k in range(1, steps+1):
            if depth(-k*dt) < overlap: lo = -k*dt; break
            hi = -k*dt
    if lo is None or hi is None: return 0.0
    for _ in range(22):
        mid = (lo+hi)/2
        if depth(mid) < overlap: lo = mid
        else: hi = mid
    holder.location = tuple(base + d*lo); bpy.context.view_layer.update()
    return lo

# --------------------------------------------------------------------------- loose cushions (EXT-001 port)
def pillow_shape(n, size, seed, loft, tile=BODY_UV_METERS, concave=(.075, .07), pinch=.35, gathers=.0045, wrinkle=.0042, base=.007, edge_round=0.0):
    """Undeformed knife-edge cushion in its local frame (X width, Z height, Y thickness),
    from build_sofa.pillow_shape (EXT-001 r2). concave: seam edges drawn in (dog-ear corners);
    pinch: corner thinning; gathers/wrinkle: soft folds near the seam and fanning from corners;
    base: half thickness at the seam; edge_round > 0 rounds the fill near the seam (blunter,
    boxier cushion, e.g. loose back cushions). Returns verts, uv, faces, perimeter."""
    vs = []; uv = []; fs = []; a, b = size
    for side in (-1, 1):
        for j in range(n+1):
            v = j/n*2-1
            for i in range(n+1):
                u = i/n*2-1
                x = a*u*(1-concave[0]*(1-v*v)); z = b*v*(1-concave[1]*(1-u*u))
                fill = max(0, (1-u*u)*(1-v*v))
                belly = .45*fill**.35+.55*fill**.85
                if edge_round: belly = (1-edge_round)*belly + edge_round*fill**.18
                cu, cv = 1-abs(u), 1-abs(v); rc = sqrt(cu*cu+cv*cv)
                pin = 1-pinch*exp(-(rc/.22)**2)
                edge = min(cu, cv)
                gat = gathers*sin(34*u+9*v+seed)*exp(-edge*9)*sin(pi*max(0, edge)/.28)
                ang = math.atan2(cv, cu)
                wr = wrinkle*sin(7*ang+seed*1.7+side)*exp(-rc/.28)*(1-exp(-(rc/.06)**2))*sin(pi*min(1, rc/.9))
                d = base+loft*belly*pin+gat+wr*(.4+belly)
                vs.append((x, side*d, z)); uv.append((x/tile+.37*seed, z/tile))
    block = (n+1)**2
    for s in range(2):
        for j in range(n):
            for i in range(n):
                k = s*block+j*(n+1)+i; fs.append((k, k+1, k+n+2, k+n+1))
    perimeter = list(range(n+1))+[j*(n+1)+n for j in range(1, n+1)]+[n*(n+1)+i for i in range(n-1, -1, -1)]+[j*(n+1) for j in range(n-1, 0, -1)]
    for i, k in enumerate(perimeter):
        k2 = perimeter[(i+1) % len(perimeter)]; fs.append((k, k2, k2+block, k+block))
    return vs, uv, fs, perimeter

def matrix(pos, rot_deg):
    return Matrix.Translation(Vector(pos)) @ Euler(tuple(math.radians(r) for r in rot_deg), 'XYZ').to_matrix().to_4x4()

def collider(verts, faces):
    """BVH of a closed shell with outward normals (signed distances)."""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new(); bv = [bm.verts.new(Vector(v)) for v in verts]
    for f in faces: bm.faces.new([bv[k] for k in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.normal_update()
    t = BVHTree.FromBMesh(bm); bm.free()
    return t

def signed(bvh, p, reach=.12):
    loc, nrm, _i, _d = bvh.find_nearest(p, reach)
    if loc is None: return None, None
    return (p-loc).dot(nrm), nrm

def penetration(points, colliders, reach=.3):
    """Deepest penetration (m, >0 = inside) of points into any collider."""
    worst = -1.0
    for p in points:
        for bvh in colliders:
            s, _n = signed(bvh, p, reach)
            if s is not None: worst = max(worst, -s)
    return worst

def solve_rest(local_verts, pos, rot, colliders, direction, overlap=.01, travel=.4, step_samples=None):
    """Translate a rigid cushion along `direction` until its deepest penetration into
    `colliders` equals `overlap` (bisection). Returns the solved position. The overlap is
    later turned into soft local compression by settle_contacts()."""
    d = Vector(direction).normalized(); pts = local_verts if step_samples is None else local_verts[::step_samples]
    def depth(t):
        M = matrix(Vector(pos)+d*t, rot); return penetration([M@Vector(v) for v in pts], colliders)
    # march from the start pose: forwards along +direction until first contact, or backwards
    # (against direction) out of a too-deep start; then bisect the bracket.
    steps = 40; dt = travel/steps
    if depth(0.0) < overlap:
        lo, hi = 0.0, None
        for k in range(1, steps+1):
            if depth(k*dt) >= overlap: hi = k*dt; break
            lo = k*dt
        if hi is None: return tuple(Vector(pos)+d*travel)
    else:
        lo, hi = None, 0.0
        for k in range(1, steps+1):
            if depth(-k*dt) < overlap: lo = -k*dt; break
            hi = -k*dt
        if lo is None: return tuple(Vector(pos)-d*travel)
    for _ in range(24):
        mid = (lo+hi)/2
        if depth(mid) < overlap: lo = mid
        else: hi = mid
    return tuple(Vector(pos)+d*lo)

def settle_contacts(pts, faces, colliders, radius=.045, bulge=.45, iterations=10):
    """Localized soft contact deformation (EXT-001 FEAT-002 rev2, world space).
    colliders: [(bvh, clearance)], clearance<0 = allowed compression depth. Penetrating vertices
    are pushed out along the collider normal, the displacement is Gaussian-smoothed over the
    cushion (soft patch), a ring bulge displaces fill around it, and a final projection
    guarantees no vertex passes the allowance."""
    from mathutils.kdtree import KDTree
    V = len(pts); P0 = [Vector(p) for p in pts]
    bm = bmesh.new(); bv = [bm.verts.new(p) for p in P0]
    for f in faces: bm.faces.new([bv[k] for k in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.normal_update()
    N = [v.normal.copy() for v in bm.verts]; bm.free()
    kd = KDTree(V)
    for k, p in enumerate(P0): kd.insert(p, k)
    kd.balance()
    s2 = (radius/2)**2
    W = [[(idx, exp(-d*d/(2*s2))) for _c, idx, d in kd.find_range(p, radius)] for p in P0]
    def smooth(D):
        out = []
        for k in range(V):
            acc = Vector(); ws = 0
            for idx, w in W[k]: acc += D[idx]*w; ws += w
            out.append(acc/ws)
        return out
    def project(D):
        hit = False
        for k in range(V):
            p = P0[k]+D[k]
            for bvh, clr in colliders:
                s, nrm = signed(bvh, p)
                if s is not None and s < clr: D[k] = D[k]+nrm*(clr-s); p = P0[k]+D[k]; hit = True
        return hit
    D = [Vector() for _ in range(V)]
    for it in range(iterations):
        if not project(D) and it: break
        D = smooth(D)
    M = [d.length for d in D]
    wide = [sum(M[idx]*w for idx, w in W[k])/sum(w for _i, w in W[k]) for k in range(V)]
    wide = [sum(wide[idx]*w for idx, w in W[k])/sum(w for _i, w in W[k]) for k in range(V)]
    for k in range(V): D[k] = D[k]+N[k]*(bulge*max(0, wide[k]-M[k]))
    for _ in range(3): project(D)
    return [P0[k]+D[k] for k in range(V)]

class LooseCushion:
    """Knife-edge loose cushion placed by solve_rest() and settled by settle_contacts().
    shape: kwargs of pillow_shape (n, size, seed, loft, ...). rests: [(direction, overlap)]
    applied in order against `colliders` (rigid BVHs). Build after what it rests on."""
    def __init__(self, name, pos, rot, shape):
        self.name = name; self.pos = tuple(pos); self.rot = tuple(rot); self.shape = shape
    def solve(self, rigid, rests):
        vs, _uv, _fs, _per = pillow_shape(**self.shape)
        for direction, overlap in rests:
            self.pos = solve_rest(vs, self.pos, self.rot, rigid, direction, overlap, step_samples=3)
        return self.pos
    def settle(self, colliders):
        vs, uv, fs, per = pillow_shape(**self.shape)
        M = matrix(self.pos, self.rot); Mi = M.inverted()
        world = settle_contacts([M@Vector(v) for v in vs], fs, colliders)
        block = (self.shape['n']+1)**2; line = []
        for k in per:
            p = (world[k]+world[k+block])/2
            for _ in range(2):
                for bvh, _c in colliders:
                    s, nrm = signed(bvh, p, .03)
                    if s is not None and s < .0008: p = p+nrm*(.0008-s)
            line.append(tuple(Mi@p))
        self.geo = ([tuple(Mi@p) for p in world], uv, fs, per, line, world)
        return self.geo
    def collider(self):
        return collider(self.geo[5], self.geo[2])
    def build(self, parent, cover, seam, welt_radius=.0016, face_mats=None, mats=None):
        vs, uv, fs, per, line, _w = self.geo
        holder = empty(self.name, parent); holder.location = self.pos; holder.rotation_euler = tuple(math.radians(r) for r in self.rot)
        ob = mesh(self.name+'_cover', vs, fs, holder, mats or cover, uv, face_mats=face_mats)
        tube(self.name+'_welt', line, welt_radius, holder, seam, sides=4)
        return ob

# --------------------------------------------------------------------------- structure
def block(name, center, size, parent, mat, bevel=.004, grain='x', tile=.60, edge=2):
    """Bevelled solid block (wood/metal): plinth rails, block feet. Grain along `grain`."""
    rb = RoundedBox(center, size, bevel, mid=(1, 1, 1), edge=edge)
    return rb.build(name, parent, mat, uv_fn=box_uv(tile, grain))

def plinth(prefix, parent, mat, x0, x1, y0, y1, height, apron_h, apron_t, leg, bevel=.004, legs_only=False):
    """Wooden plinth: rectangular apron frame (top at `height`, `apron_h` tall, `apron_t`
    thick) on four square block feet `leg` wide, flush with the apron's outer faces. Returns
    the created objects. Front = y0 (Blender -Y)."""
    obs = []; zc = height-apron_h/2
    if not legs_only:
        obs.append(block(prefix+'_apron_front', ((x0+x1)/2, y0+apron_t/2, zc), (x1-x0-2*leg+.002, apron_t, apron_h), parent, mat, bevel, 'x'))
        obs.append(block(prefix+'_apron_back', ((x0+x1)/2, y1-apron_t/2, zc), (x1-x0-2*leg+.002, apron_t, apron_h), parent, mat, bevel, 'x'))
        for k, x in enumerate((x0+apron_t/2, x1-apron_t/2)):
            obs.append(block(prefix+'_apron_side_'+'lr'[k], (x, (y0+y1)/2, zc), (apron_t, y1-y0-2*leg+.002, apron_h), parent, mat, bevel, 'y'))
    for k, (x, y) in enumerate(((x0+leg/2, y0+leg/2), (x1-leg/2, y0+leg/2), (x0+leg/2, y1-leg/2), (x1-leg/2, y1-leg/2))):
        obs.append(block(f'foot_{k+1}', (x, y, height/2), (leg, leg, height), parent, mat, bevel, 'z'))
    return obs

# --------------------------------------------------------------------------- materials
def material(name, color, roughness=1.0, region=None, metallic=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1); bs.inputs['Roughness'].default_value = roughness; bs.inputs['Metallic'].default_value = metallic
    m.use_backface_culling = True   # closed exterior shells: glTF doubleSided = false
    if region:
        assert region in REGIONS, region
        m['stanza_region'] = region
    return m

def image(path, kind):
    key = str(path)
    if key not in _IMAGES:
        assert Path(path).is_file(), path
        im = bpy.data.images.load(key, check_existing=False)
        im.colorspace_settings.name = 'sRGB' if kind == 'basecolor' else 'Non-Color'; im.pack(); _IMAGES[key] = im
    return _IMAGES[key]

def textured(name, maps, region, normal_strength=1.0, sheen=0.0, sheen_roughness=.9, color=(1, 1, 1), roughness=None):
    """PBR material from maps {'basecolor','normal','roughness'} (any subset). One Blender
    image per file, so materials sharing a map share ONE glTF image (no extra bytes).
    color multiplies the base colour map (glTF baseColorFactor)."""
    m = material(name, color, 1.0 if roughness is None else roughness, region)
    nodes = m.node_tree.nodes; links = m.node_tree.links; bs = nodes.get('Principled BSDF')
    for kind, socket in (('basecolor', 'Base Color'), ('roughness', 'Roughness'), ('normal', 'Normal')):
        if kind not in maps: continue
        tex = nodes.new('ShaderNodeTexImage'); tex.image = image(maps[kind], kind); tex.extension = 'REPEAT'
        if kind == 'normal':
            nm = nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = normal_strength
            links.new(tex.outputs['Color'], nm.inputs['Color']); links.new(nm.outputs['Normal'], bs.inputs[socket])
        elif kind == 'basecolor' and tuple(color) != (1, 1, 1):
            mix = nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs['Factor'].default_value = 1
            links.new(tex.outputs['Color'], mix.inputs[6]); mix.inputs[7].default_value = (*color, 1)
            links.new(mix.outputs[2], bs.inputs[socket])
        else: links.new(tex.outputs['Color'], bs.inputs[socket])
    bs.inputs['Sheen Weight'].default_value = sheen; bs.inputs['Sheen Roughness'].default_value = sheen_roughness
    return m

def library_maps(family, tint=None, base=1024, normal=1024, rough=512):
    """Embedded maps of a shared library family at the given sizes (1024 = the full map,
    512/256 = the reduced `embedded/` variants). tint selects the pre-tinted base colour.
    Note: the glTF exporter re-encodes roughness as a lossless PNG (G channel), so keep the
    roughness map small; it is nearly uniform on fabrics."""
    f = LIB_MATERIALS/family; e = f/'embedded'
    pick = lambda kind, size, ext: f/f'{kind}.{ext}' if size == 1024 else e/f'{kind}-{size}.{ext}'
    out = {'normal': pick('normal', normal, 'png'), 'roughness': pick('roughness', rough, 'jpg')}
    if tint: out['basecolor'] = e/f'basecolor-{tint}-{base}.jpg'
    else: out['basecolor'] = pick('basecolor', base, 'jpg')
    return out

# --------------------------------------------------------------------------- export / metadata
def export_variant(dest_glb, blend_path=None):
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='SELECT')
    Path(dest_glb).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(dest_glb), export_format='GLB', use_selection=True, export_apply=True, export_yup=True,
                              export_texcoords=True, export_normals=True, export_tangents=True, export_materials='EXPORT',
                              export_extras=True, export_cameras=False, export_lights=False, export_image_format='AUTO')
    if blend_path:
        bpy.context.scene.unit_settings.system = 'METRIC'
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), compress=True)

def glb_metrics(path):
    """bytes, sha256, triangles, bounds, images, regions of a GLB (scripts/models3d/glbtools.py)."""
    import sys
    sys.path.insert(0, str(REPO/'scripts'/'models3d'))
    import glbtools
    return glbtools.metrics(path)
