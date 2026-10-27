"""Contact / penetration check between named meshes of an exported GLB (models3d pipeline).

    LD_LIBRARY_PATH=<gl libs> .agents/venv/bin/python scripts/models3d/contacts.py <file.glb> <out.json> [A:B ...]

Imports the GLB with Blender's glTF importer (bpy 5.0.1 module), builds a BVH of every closed
mesh (normals recalculated outward) and, for each pair A:B (default: every pair of cover/body
meshes whose bounding boxes touch), reports
  penetration_mm  deepest vertex of A inside B (signed distance < 0), in millimetres
  gap_mm          smallest distance of A's vertices to B's surface when not penetrating
  verts_inside    count of A's vertices inside B
Welts/seams (names with 'welt'/'seam') are thin tubes and are only checked as A.
A soft contact is a few mm of penetration of a LOOSE cushion into what it rests on (the
generator's settle_contacts() compresses ~1 mm); rigid parts should not cross by > 1 cm.
"""
import sys, json
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    out = {}
    for ob in bpy.context.scene.objects:
        if ob.type != 'MESH': continue
        me = ob.data; M = ob.matrix_world
        verts = [M @ v.co for v in me.vertices]
        bm = bmesh.new(); bm.from_mesh(me); bm.transform(M)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.normal_update()
        bvh = BVHTree.FromBMesh(bm); bm.free()
        lo = Vector([min(v[k] for v in verts) for k in range(3)]); hi = Vector([max(v[k] for v in verts) for k in range(3)])
        out[ob.name] = {'verts': verts, 'bvh': bvh, 'lo': lo, 'hi': hi}
    return out

def pair(A, B, reach=.05):
    worst = 0.0; inside = 0; gap = None
    for p in A['verts']:
        loc, nrm, _i, d = B['bvh'].find_nearest(p, reach)
        if loc is None: continue
        s = (p-loc).dot(nrm)
        if s < 0: inside += 1; worst = max(worst, -s)
        else: gap = s if gap is None else min(gap, s)
    return {'penetration_mm': round(worst*1000, 2), 'verts_inside': inside, 'gap_mm': None if gap is None else round(gap*1000, 2)}

def touching(a, b, pad=.01):
    return all(a['lo'][k]-pad <= b['hi'][k] and b['lo'][k]-pad <= a['hi'][k] for k in range(3))

if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    glb, out = args[0], args[1]; meshes = load(glb)
    pairs = [tuple(p.split(':')) for p in args[2:]]
    if not pairs:
        names = sorted(meshes)
        solid = [n for n in names if 'welt' not in n and 'seam' not in n]
        pairs = [(a, b) for a in names for b in solid if a != b and touching(meshes[a], meshes[b])]
    res = {f'{a}:{b}': pair(meshes[a], meshes[b]) for a, b in pairs if a in meshes and b in meshes}
    Path = __import__('pathlib').Path; Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps({'glb': glb, 'pairs': res}, indent=1)+'\n', encoding='utf-8')
    worst = sorted(res.items(), key=lambda kv: -kv[1]['penetration_mm'])[:12]
    for k, v in worst: print(k, v)
