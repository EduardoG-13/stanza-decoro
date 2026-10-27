"""Pure-Python GLB helpers for the models3d pipeline (no Blender, no numpy).

    python scripts/models3d/glbtools.py <file.glb> [...]        # print metrics as JSON

metrics(): bytes, sha256, triangles, world bounds (glTF axes, node transforms applied),
embedded images (bytes, users), materials with their `stanza_region` extras, root extras.
"""
import hashlib, json, math, struct, sys
from pathlib import Path


def load(path):
    data = Path(path).read_bytes()
    assert data[:4] == b'glTF', f'{path}: not a GLB'
    version, length = struct.unpack_from('<II', data, 4)
    assert version == 2 and length == len(data), f'{path}: bad header'
    jlen = struct.unpack_from('<I', data, 12)[0]
    g = json.loads(data[20:20+jlen])
    off = 20+jlen; binary = b''
    if off < len(data):
        blen = struct.unpack_from('<I', data, off)[0]; binary = data[off+8:off+8+blen]
    return data, g, binary


def _mat(n):
    if 'matrix' in n:
        m = n['matrix']; return [[m[c*4+r] for c in range(4)] for r in range(4)]
    tx, ty, tz = n.get('translation', (0, 0, 0)); x, y, z, w = n.get('rotation', (0, 0, 0, 1)); sx, sy, sz = n.get('scale', (1, 1, 1))
    r = [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]
    return [[r[0][0]*sx, r[0][1]*sy, r[0][2]*sz, tx], [r[1][0]*sx, r[1][1]*sy, r[1][2]*sz, ty], [r[2][0]*sx, r[2][1]*sy, r[2][2]*sz, tz], [0, 0, 0, 1]]


def _mul(a, b): return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def metrics(path):
    data, g, _bin = load(path)
    tris = 0
    for m in g.get('meshes', []):
        for p in m['primitives']:
            if p.get('mode', 4) != 4: continue
            acc = g['accessors'][p['indices']] if 'indices' in p else g['accessors'][p['attributes']['POSITION']]
            tris += acc['count']//3
    lo = [math.inf]*3; hi = [-math.inf]*3
    ident = [[1 if i == j else 0 for j in range(4)] for i in range(4)]
    def walk(i, parent):
        n = g['nodes'][i]; M = _mul(parent, _mat(n))
        if 'mesh' in n:
            for p in g['meshes'][n['mesh']]['primitives']:
                a = g['accessors'][p['attributes']['POSITION']]
                for cx in (a['min'][0], a['max'][0]):
                    for cy in (a['min'][1], a['max'][1]):
                        for cz in (a['min'][2], a['max'][2]):
                            w = [M[r][0]*cx+M[r][1]*cy+M[r][2]*cz+M[r][3] for r in range(3)]
                            for k in range(3): lo[k] = min(lo[k], w[k]); hi[k] = max(hi[k], w[k])
        for c in n.get('children', []): walk(c, M)
    for i in g['scenes'][g.get('scene', 0)]['nodes']: walk(i, ident)
    images = []
    for i, im in enumerate(g.get('images', [])):
        bv = g['bufferViews'][im['bufferView']]
        users = sorted({m['name'] for m in g['materials'] for slot in (m.get('normalTexture'), m.get('pbrMetallicRoughness', {}).get('baseColorTexture'), m.get('pbrMetallicRoughness', {}).get('metallicRoughnessTexture')) if slot and g['textures'][slot['index']]['source'] == i})
        images.append({'index': i, 'name': im.get('name'), 'mimeType': im.get('mimeType'), 'bytes': bv['byteLength'], 'usedBy': users})
    r5 = lambda v: round(v, 5)
    root = next((n for n in g['nodes'] if n.get('name') in ('model_root', 'sofa_root')), {})
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'triangles': tris,
            'boundsMeters': {'min': [r5(v) for v in lo], 'max': [r5(v) for v in hi], 'dimensions': [r5(hi[k]-lo[k]) for k in range(3)]},
            'textures': images, 'materials': [{'name': m['name'], 'region': (m.get('extras') or {}).get('stanza_region')} for m in g.get('materials', [])],
            'meshes': sorted(n['name'] for n in g['nodes'] if 'mesh' in n), 'rootExtras': root.get('extras', {})}


if __name__ == '__main__':
    print(json.dumps({p: metrics(p) for p in sys.argv[1:]}, indent=2, ensure_ascii=False))
