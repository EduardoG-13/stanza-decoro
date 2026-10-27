"""EXT-040 - Cabeceira de painéis horizontais (catálogo `cabeceira-paineis`, portfólio `projeto-21`).
Reference: cabeceiras/cabeceiras-6.jpg (899x899, single angle, room under installation; the bed is
pulled away, only a mattress corner is visible). Modelled: ONLY the upholstered wall composition
(central headboard of 3 horizontal panels, 2 vertical strips each side, 2 horizontal side panels
each side above the nightstands). NOT modelled: nightstands, lamps, switches/sockets, mattress,
bedding, the slatted wall cladding, floor, room.

Parametric EXTERIOR-ONLY source. Regenerates in ONE pass (never edit the .blend/GLBs by hand):
    LD_LIBRARY_PATH=<gl libs> .agents/venv/bin/python assets/models-3d/stanza-headboard-panels-01/source/build.py
writes models/stanza-headboard-panels-01.glb, models/stanza-headboard-panels-01-mobile.glb,
source/stanza-headboard-panels-01.blend and source/metrics.json.

Axes (Blender): X width, -Y FRONT (away from the wall), Z up; origin = floor, wall plane (y=0),
centre of the central headboard. All dimensions are ESTIMATES from one photo: camera fitted to 13
correspondences (rms ~6 px) with the central headboard width FIXED at 1.60 m (queen bed 1.58 m
+ 1 cm each side, assumption that sets the scale), see docs/sofa-3d-review/ext040-cabeceira-paineis.md.

Material regions (`stanza_region`):
  body      fabric_main   (every upholstered panel; no trim, no visible frame or legs)
"""
import sys, json, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE.parent
REPO = MODEL_DIR.parents[2]
sys.path.insert(0, str(MODEL_DIR.parent / 'lib'))
import bpy
import numpy as np
from PIL import Image
import stanza3d as S

MODEL_ID = 'stanza-headboard-panels-01'
REVISION = '1.0.0'
EMBEDDED = {'fabricId': 'velvet', 'colorId': 'areia'}
_hex = json.loads((REPO/'assets'/'models-3d'/'materials'/'materials.json').read_text())['tints']['areia']
TINT = tuple(int(_hex[i:i+2], 16) for i in (1, 3, 5))   # = COLORS.areia in sofa-viewer.js (#b6b0a8)
REGIONS = {'body': ['fabric_main']}
VELVET = REPO/'assets'/'sofa-pilot'/'materials'/'velvet'
TILES = 2          # embedded velvet pre-tiled 2x per body UV unit (0.30 m): 0.15 m vs the family's 0.14 m

# ---------------------------------------------------------------- proportions (estimated, m)
WC = 1.60          # central headboard width (ASSUMPTION: queen 1.58 m + 1 cm each side; fixes the scale)
H = 1.21           # top of every panel above the floor (fit 1.208)
H1, H2 = .64, .925 # channels of the central headboard (fit .639 / .923): panels .64 / .285 / .285
WS = .20           # vertical strip width, 2 per side (fit .201)
WP = .60           # side panel width (right one ends near the room corner; left one out of frame: symmetric)
HP = .67           # side panel bottom (fit .669; sits just above the nightstand)
HPM = .94          # side panel channel (fit .926, aligned with the central upper channel)
TC, TS, TP = .09, .07, .05   # depths: central panels / strips / side panels (from the visible side faces)
GAP = .004         # joint between neighbouring panels (each panel is a separate upholstered board)

def velvet_maps(tmp, base, normal, rough):
    """Embedded maps of the shared velvet family (by reference): base colour pre-tinted with TINT
    (map x tint), so the viewer's white multiplier gives exactly velvet x areia; pre-tiled TILES x
    TILES because the family repeats every 0.14 m and the body UV unit is 0.30 m (as EXT-014)."""
    def tiled(im, size):
        t = im.resize((size//TILES, size//TILES), Image.Resampling.BOX); o = Image.new(im.mode, (size, size))
        for i in range(TILES):
            for j in range(TILES): o.paste(t, (i*size//TILES, j*size//TILES))
        return o
    col = np.asarray(Image.open(VELVET/'basecolor.jpg').convert('RGB')).astype(float)/255
    im = Image.fromarray(np.uint8(np.round(np.clip(col*np.array(TINT)/255, 0, 1)*255)))
    out = {}
    p = tmp/f'basecolor-areia-{base}.jpg'; tiled(im, base).save(p, quality=90, subsampling=0, optimize=True); out['basecolor'] = p
    for kind, size, ext in (('normal', normal, 'png'), ('roughness', rough, 'jpg')):
        p = tmp/f'{kind}-{size}.{ext}'; tiled(Image.open(VELVET/f'{kind}.{ext}').convert('RGB'), size).save(p, **({'quality': 90} if ext == 'jpg' else {}))
        out[kind] = p
    return out

def build(mobile=False):
    S.reset()
    Q = .5 if mobile else 1.0
    def m(v): return max(1, int(round(v*Q)))
    root = S.empty('model_root', None, modelId=MODEL_ID, revision=REVISION, construction='exterior-only',
                   dimensions_estimated=True, reference='cabeceiras/cabeceiras-6.jpg', catalogId='cabeceira-paineis', queue='EXT-040',
                   mounting='wall', materialRegions=REGIONS, embeddedFinish=EMBEDDED, embeddedTiles=TILES, bodyUvMeters=S.BODY_UV_METERS)
    groups = {n: S.empty(n, root) for n in ('upholstery', 'legs', 'cushions')}
    tmp = Path(tempfile.mkdtemp())
    fmaps = velvet_maps(tmp, 512 if mobile else 1024, 256 if mobile else 1024, 256)
    cloth = S.textured('fabric_main', fmaps, 'body', .38, .72, .55)
    up = groups['upholstery']; e = 4 if not mobile else 3

    def panel(name, x0, x1, z0, z1, t, r, crown, seed, dens=(40, 16)):
        """One upholstered board against the wall (back flat on y=0, domed front face)."""
        w, h = x1-x0, z1-z0
        nx = m(max(4, dens[0]*w)); nz = m(max(3, dens[1]*h))
        rb = S.RoundedBox(((x0+x1)/2, -t/2, (z0+z1)/2), (w, t, h), r, mid=(nx, 2, nz), edge=e,
                          crown={'-y': crown, '+z': .002, '-z': .001, '+x': .001, '-x': .001}, wrinkle=.0005, seed=seed)
        rb.build(name, up, cloth)
        return rb

    g = GAP/2
    # ------------------------------------------------------------ central headboard: 3 horizontal panels
    panel('center_panel_bottom', -WC/2, WC/2, 0, H1-g, TC, .024, .012, 1, (28, 22))
    panel('center_panel_middle', -WC/2, WC/2, H1+g, H2-g, TC, .024, .009, 2, (28, 22))
    panel('center_panel_top', -WC/2, WC/2, H2+g, H, TC, .024, .009, 3, (28, 22))
    # ------------------------------------------------------------ vertical strips, 2 per side, floor to top
    for sg, side in ((-1, 'left'), (1, 'right')):
        for k in range(2):
            a = WC/2+k*WS+g; b = WC/2+(k+1)*WS-g
            x0, x1 = (a, b) if sg > 0 else (-b, -a)
            panel(f'strip_{side}_{"inner" if k == 0 else "outer"}', x0, x1, 0, H, TS, .022, .006, 10+k+(2 if sg > 0 else 0), (40, 12))
        # -------------------------------------------------------- side panels: 2 horizontal boards above the nightstand
        a = WC/2+2*WS+g; b = a+WP-g
        x0, x1 = (a, b) if sg > 0 else (-b, -a)
        panel(f'side_{side}_bottom', x0, x1, HP, HPM-g, TP, .02, .006, 20+(2 if sg > 0 else 0), (28, 22))
        panel(f'side_{side}_top', x0, x1, HPM+g, H, TP, .02, .006, 21+(2 if sg > 0 else 0), (28, 22))
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
