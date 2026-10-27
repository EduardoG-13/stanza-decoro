"""Refresh the COMPUTED part of a model manifest from the real GLB bytes (models3d pipeline).

    python scripts/models3d/update_manifest.py assets/models-3d/<modelId>

Keeps every authored field of <modelDir>/manifest.json (identity, references, regions table,
options, limitations...) and rewrites only: models.{main,mobile} (uri, bytes, sha256,
triangles, bounds, embedded textures, materials), dimensions (from the main bounds) and
budgets.measured. Fails if the GLB root extras disagree with the manifest identity.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import glbtools

def main(model_dir):
    d = Path(model_dir); mp = d/'manifest.json'
    man = json.loads(mp.read_text(encoding='utf-8'))
    mid = man['modelId']
    out = {}
    for variant, name in (('main', f'{mid}.glb'), ('mobile', f'{mid}-mobile.glb')):
        m = glbtools.metrics(d/'models'/name)
        ex = m.pop('rootExtras')
        assert ex.get('modelId') == mid and ex.get('revision') == man['revision'], (variant, ex.get('modelId'), ex.get('revision'))
        m.pop('meshes')
        out[variant] = {'uri': f'models/{name}', **m}
    man['models'] = out
    dims = out['main']['boundsMeters']['dimensions']
    man['dimensions'] = {'width': round(dims[0], 3), 'height': round(dims[1], 3), 'depth': round(dims[2], 3), 'unit': 'm', 'estimated': True,
                         'basis': man.get('dimensions', {}).get('basis', 'single photograph; no measured shop dimensions')}
    b = man.setdefault('budgets', {})
    b['measured'] = {'mainBytes': out['main']['bytes'], 'mainTriangles': out['main']['triangles'],
                     'mobileBytes': out['mobile']['bytes'], 'mobileTriangles': out['mobile']['triangles']}
    lim = b.get('limits', {'mainBytes': 5_000_000, 'mainTriangles': 60_000, 'mobileTriangles': 25_000})
    b['limits'] = lim
    b['withinBudget'] = (out['main']['bytes'] <= lim['mainBytes'] and out['main']['triangles'] <= lim['mainTriangles']
                         and out['mobile']['triangles'] <= lim['mobileTriangles'])
    mp.write_text(json.dumps(man, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(b, indent=1))

if __name__ == '__main__':
    main(sys.argv[1])
