"""EXT-030 - Puff quadrado (catálogo `puff-quadrado`, portfólio `projeto-14`).
Reference: pufs/pufs-10.jpg (1024x683, office/TV room, warm light). Modelled: ONE free-standing
soft rounded-cube puff (the yellow one in the centre foreground). NOT modelled: the other puffs,
the bench with storage cubes, TV, glass boards, floor, room.

Parametric EXTERIOR-ONLY source. Regenerates in ONE pass (never edit the .blend/GLBs by hand):
    LD_LIBRARY_PATH=<gl libs> .agents/venv/bin/python assets/models-3d/stanza-puff-square-01/source/build.py
writes models/stanza-puff-square-01.glb, models/stanza-puff-square-01-mobile.glb,
source/stanza-puff-square-01.blend and source/metrics.json.

Axes (Blender): X width, -Y FRONT, Z up; origin = floor, centre of the puff. Dimensions are
ESTIMATES from one photo (no shop measurements): near-cube, the visible front face is ~1.05x
wider than tall; scale set by a typical 0.45 m upholstered puff (see the EXT-030 report).

Material regions (`stanza_region`):
  body      fabric_main, fabric_seam   (whole cover + the faint top/bottom boxing seams)
No legs, plinth, piping of another colour or decorative cushions: nothing fixed is invented.
"""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE.parent
sys.path.insert(0, str(MODEL_DIR.parent / 'lib'))
import bpy
import stanza3d as S

MODEL_ID = 'stanza-puff-square-01'
REVISION = '1.0.0'
EMBEDDED = {'fabricId': 'sarja', 'colorId': 'mostarda'}
REGIONS = {'body': ['fabric_main', 'fabric_seam']}

# ---------------------------------------------------------------- proportions (estimated, m)
import os
W = float(os.environ.get('PUFF_W', .45))   # width = depth (square plan)
H = float(os.environ.get('PUFF_H', .40))   # height (photo outline ~1:1 at ~26 deg elevation, top/front ~0.5)
R = float(os.environ.get('PUFF_R', .085))  # very soft edge radius (the photo shows no crisp edge anywhere)
CROWN_TOP = .018   # slightly domed top
CROWN_SIDE = .010  # slightly domed sides (each face bulges a little)
SEAM_R = .0016     # faint boxing seams (same cloth, barely raised)

def build(mobile=False):
    S.reset()
    Q = .55 if mobile else 1.0
    def m(v): return max(2, int(round(v*Q)))
    root = S.empty('model_root', None, modelId=MODEL_ID, revision=REVISION, construction='exterior-only',
                   dimensions_estimated=True, reference='pufs/pufs-10.jpg', catalogId='puff-quadrado', queue='EXT-030',
                   materialRegions=REGIONS, embeddedFinish=EMBEDDED, bodyUvMeters=S.BODY_UV_METERS)
    groups = {n: S.empty(n, root) for n in ('upholstery', 'legs', 'cushions')}
    fmaps = S.library_maps('sarja', tint='mostarda', base=512 if mobile else 1024, normal=512 if mobile else 1024, rough=256)
    cloth = S.textured('fabric_main', fmaps, 'body', .9, .10, .8)
    seam = S.textured('fabric_seam', fmaps, 'body', .9, .10, .8)
    up = groups['upholstery']
    # Flat bottom (sits directly on the floor, no legs); domed top and sides; shallow folds near the edges.
    rb = S.RoundedBox((0, 0, H/2), (W, W, H), R, mid=(m(26), m(26), m(24)), edge=m(9),
                      crown={'+z': CROWN_TOP, '-y': CROWN_SIDE, '+y': CROWN_SIDE, '-x': CROWN_SIDE, '+x': CROWN_SIDE},
                      wrinkle=.0007, seed=30)
    rb.build('puff_cover', up, cloth)
    S.tube('puff_seam_top', rb.seam_loop('+z', samples=m(220), lift=.0009), SEAM_R, up, seam, sides=4)
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
