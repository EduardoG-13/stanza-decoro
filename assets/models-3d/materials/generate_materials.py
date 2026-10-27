"""Shared PBR finish library for the Stanza 3D collection (models3d pipeline).

Run from the repo root (numpy>=1.26 + Pillow, no network, no third-party art):
    python assets/models-3d/materials/generate_materials.py

Writes ONLY assets/models-3d/materials/<family>/ and materials.json. Families authored here:

  boucle-mescla  heathered (mescla) bouclé: dense irregular loops ~4-7 mm with white and grey
                 fibre loops mixed, as seen on SOFA-5.jpg (EXT-002). Neutral (untinted) maps,
                 repeat 0.30 m per UV unit (= the pipeline BODY_UV_METERS convention).
  wood-wenge     dark stained wood with soft long grain for plinths/feet (exterior structure).

The pre-existing fabric families boucle / linen / velvet live in assets/sofa-pilot/materials/
(EXT-001) and are REUSED by reference (data/models-3d.json `materialLibrary`), not copied.

Base colours hold fibre/dye variation only, never baked lighting. Normals are tangent space
OpenGL (+Y) from metre heights. Roughness uses identical RGB channels. All sampling periodic.
`embedded/` holds the reduced, pre-tinted maps that a model embeds in its GLB for its INITIAL
finish (tint = the viewer COLORS value, so embedded and external paths look the same).
Original procedural output: CC0-1.0, to the extent rights exist.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
N = 1024
# Tints used for embedded initial finishes. MUST equal COLORS in assets/sofa-pilot/viewer/sofa-viewer.js.
TINTS = {'gelo': (186, 188, 192)}


def noise(rng, sx, sy=None, n=N):
    """Exactly periodic, normalized filtered noise; sigma in pixels."""
    sy = sx if sy is None else sy
    fx = np.fft.fftfreq(n)[None, :]
    fy = np.fft.fftfreq(n)[:, None]
    smooth = np.exp(-2 * np.pi**2 * (sx*sx*fx*fx + sy*sy*fy*fy))
    out = np.fft.ifft2(np.fft.fft2(rng.standard_normal((n, n))) * smooth).real
    return out / max(out.std(), 1e-8)


def normals(height, repeat_m):
    n = height.shape[0]
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) / (2*repeat_m/n)
    dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) / (2*repeat_m/n)
    v = np.stack([-dx, dy, np.ones_like(dx)], -1)
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def save_normal(vectors, path, size=None):
    if size and size != vectors.shape[0]:
        f = vectors.shape[0] // size
        vectors = vectors.reshape(size, f, size, f, 3).mean(axis=(1, 3))
        vectors /= np.maximum(np.linalg.norm(vectors, axis=-1, keepdims=True), 1e-12)
    Image.fromarray(np.uint8(np.round((vectors*.5+.5)*255))).save(path, optimize=True)


def save_gray(arr, path, quality=92, size=None):
    im = Image.fromarray(np.uint8(np.round(np.clip(arr, 0, 1)*255))).convert('RGB')
    if size: im = im.resize((size, size), Image.Resampling.BOX)
    im.save(path, quality=quality, subsampling=0, optimize=True)


def write_family(fid, height, color, rough, repeat_m, meta, rgb=None):
    folder = HERE / fid
    (folder / 'embedded').mkdir(parents=True, exist_ok=True)
    nrm = normals(height, repeat_m)
    col = rgb if rgb is not None else np.repeat(np.clip(color, 0, 1)[..., None], 3, -1)
    Image.fromarray(np.uint8(np.round(np.clip(col, 0, 1)*255))).save(folder/'basecolor.jpg', quality=92, subsampling=0, optimize=True)
    save_normal(nrm, folder/'normal.png')
    save_gray(rough, folder/'roughness.jpg', 93)
    light = np.array([-.65, .35, .72]); light /= np.linalg.norm(light)
    lit = np.clip(nrm@light, 0, 1)[..., None]
    thumb = np.clip(col*(.58+.47*lit), 0, 1)
    Image.fromarray(np.uint8(thumb*255)).crop((256, 256, 768, 768)).resize((256, 256), Image.Resampling.LANCZOS).save(folder/'thumbnail.jpg', quality=90, optimize=True)
    # reduced maps for GLB embedding (mobile + optional main)
    for s in (512, 256):
        save_normal(nrm, folder/'embedded'/f'normal-{s}.png', s)
        save_gray(rough, folder/'embedded'/f'roughness-{s}.jpg', 93, s)
    meta.update({'id': fid, 'repeatMeters': repeat_m, 'textureSize': [N, N], 'baseColorSpace': 'sRGB',
                 'normalConvention': 'OpenGL +Y', 'metalness': 0, 'license': 'CC0-1.0',
                 'source': 'assets/models-3d/materials/generate_materials.py',
                 'maps': {k: f'{fid}/{v}' for k, v in {'baseColor': 'basecolor.jpg', 'normal': 'normal.png', 'roughness': 'roughness.jpg', 'thumbnail': 'thumbnail.jpg'}.items()},
                 'validation': {'baseColorMean': float(np.mean(col)), 'roughnessMean': float(rough.mean())}})
    return meta, col, nrm


def tinted(fid, col, tint_id, sizes=(1024, 512)):
    tint = np.array(TINTS[tint_id]) / 255.0
    im = Image.fromarray(np.uint8(np.round(np.clip(col*tint, 0, 1)*255)))
    out = []
    for s in sizes:
        p = HERE/fid/'embedded'/f'basecolor-{tint_id}-{s}.jpg'
        (im if s == N else im.resize((s, s), Image.Resampling.BOX)).save(p, quality=90, subsampling=0, optimize=True)
        out.append(p.name)
    return out


def boucle_mescla():
    """Heathered bouclé, 0.30 m repeat over 1024 px (0.29 mm/px). Two layers of irregular
    loops: a dense base of small grey-white loops and a sparser layer of larger, whiter loop
    crests that give the speckled 'poodle' look of SOFA-5.jpg."""
    rng = np.random.default_rng(705)
    repeat_m = .30
    height = np.zeros((N, N)); dye = np.zeros((N, N)); wsum = np.zeros((N, N))
    def layer(count, rmin, rmax, amp, white_p, grey, radius):
        for iy in range(count):
            for ix in range(count):
                cx = (ix+rng.uniform(0, 1))*N/count; cy = (iy+rng.uniform(0, 1))*N/count
                rx = rng.uniform(rmin, rmax); ry = rx*rng.uniform(.75, 1.35); th = rng.uniform(0, 2*np.pi)
                xx, yy = np.meshgrid(np.arange(int(cx)-radius, int(cx)+radius+1), np.arange(int(cy)-radius, int(cy)+radius+1))
                dx = xx-cx; dy = yy-cy
                u = (dx*np.cos(th)+dy*np.sin(th))/rx; v = (-dx*np.sin(th)+dy*np.cos(th))/ry
                rr = np.sqrt(u*u+v*v); ang = np.arctan2(v, u)
                ring = np.exp(-((rr-(.70+.12*np.sin(ang*2+th)))/.36)**2)
                nest = .55*np.exp(-rr*rr/1.0)
                prof = (ring+nest)*rng.uniform(.7, 1.2)
                # max-blend: loops sit ON each other instead of summing into a flat plateau
                hy, hx = yy % N, xx % N
                height[hy, hx] += prof*amp
                tone = 1.0 if rng.uniform() < white_p else grey*rng.uniform(.96, 1.04)
                w = np.exp(-rr*rr/1.4)*prof
                dye[hy, hx] += w*tone; wsum[hy, hx] += w
    layer(96, 3.5, 6.0, .00030, .40, .72, 14)    # dense base loops (~2-3.5 mm radius)
    layer(52, 6.0, 9.5, .00045, .75, .80, 22)    # larger, whiter crests (~4-6 mm)
    # soft saturation: overlapping loops pile up but never form flat plateaus
    height[:] = .0011*(1-np.exp(-height/.0006))
    fuzz = noise(rng, .7)
    height += fuzz*.000012 + noise(rng, 2.0)*.00002
    ground = .72
    tone = np.where(wsum > 1e-6, dye/np.maximum(wsum, 1e-6), ground)
    cover = np.clip(wsum/(np.percentile(wsum, 45)+1e-9), 0, 1)**.7
    color = ground*(1-cover) + tone*cover
    # EXT-002 review: per-loop tones merged into ~1-2 cm blotches that read as camouflage in
    # close-ups; compress the dye contrast around the mean and add fibre-scale variation so the
    # mescla reads as fine speckle (SOFA-5.jpg) while the loop relief comes from the normal map.
    mean = color.mean()
    color = mean + (color-mean)*.55
    color = np.clip(color*.985 + .03*fuzz*np.clip(height/height.max(), 0, 1) + .012*noise(rng, .9), 0, 1)
    rough = np.clip(.93+.03*fuzz+.02*noise(rng, 3), 0, 1)
    meta = {'label': 'Bouclé mescla', 'family': 'heathered_loop_boucle_study', 'seed': 705, 'normalScale': 1.5,
            'roughness': 1.0, 'sheen': .12, 'sheenRoughness': .95,
            'description': 'Bouclé mesclado de laços irregulares (aprox. 4-7 mm), fios brancos e cinza misturados. Estudo visual próprio a partir de SOFA-5.jpg; sem código comercial.',
            'createdFor': 'EXT-002 (sofas/SOFA-5.jpg)'}
    meta, col, _ = write_family('boucle-mescla', height, color, rough, repeat_m, meta)
    meta['embedded'] = {'gelo': tinted('boucle-mescla', col, 'gelo'),
                        'normal': ['embedded/normal-512.png', 'embedded/normal-256.png'],
                        'roughness': ['embedded/roughness-512.jpg', 'embedded/roughness-256.jpg']}
    return meta


def wood_wenge():
    """Dark stained wood (wenge-like) for plinths and block feet. 0.60 m repeat along U (grain
    along U). Colour is the final fixed finish (exterior structure is never recoloured)."""
    rng = np.random.default_rng(706)
    repeat_m = .60
    Y, X = np.mgrid[0:N, 0:N].astype(np.float64)
    warp = 6*noise(rng, 40, 160)
    rings = np.sin(2*np.pi*(Y/N*38 + warp*.08))
    streak = noise(rng, 120, 1.2)
    pores = noise(rng, 5, .8)
    g = .55*rings + .35*streak + .1*pores
    base = np.array([58, 38, 34]) / 255.0          # dark red-brown, read from SOFA-5.jpg plinth
    dark = np.array([38, 24, 22]) / 255.0
    t = np.clip(.5+.25*g, 0, 1)[..., None]
    rgb = dark*(1-t) + base*t
    height = .00003*g - .00002*np.clip(-pores, 0, None)
    rough = np.clip(.55+.06*streak+.05*np.clip(-pores, 0, None), 0, 1)
    meta = {'label': 'Madeira escura (wengué)', 'family': 'dark_stained_wood_study', 'seed': 706, 'normalScale': .4,
            'description': 'Madeira tingida escura com veio longo suave; acabamento fixo de bases e pés.',
            'createdFor': 'EXT-002 (plinto e pés de SOFA-5.jpg)'}
    meta, col, _ = write_family('wood-wenge', height, None, rough, repeat_m, meta, rgb=rgb)
    for s in (512, 256):
        Image.fromarray(np.uint8(np.round(np.clip(col, 0, 1)*255))).resize((s, s), Image.Resampling.BOX).save(HERE/'wood-wenge'/'embedded'/f'basecolor-{s}.jpg', quality=90, subsampling=0, optimize=True)
    return meta


if __name__ == '__main__':
    fams = [boucle_mescla(), wood_wenge()]
    index = {'contract': 'stanza-material-library/v1',
             'note': 'Biblioteca compartilhada de acabamentos da coleção 3D. Estudos visuais originais (CC0), não catálogo homologado; a tela não substitui amostra física.',
             'bodyUvMeters': .30,
             'families': fams,
             'reusedFamilies': {k: f'/assets/sofa-pilot/materials/{k}/' for k in ('boucle', 'linen', 'velvet')},
             'tints': {k: '#%02x%02x%02x' % v for k, v in TINTS.items()}}
    (HERE/'materials.json').write_text(json.dumps(index, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    for f in sorted(HERE.rglob('*')):
        if f.is_file() and f.suffix in ('.jpg', '.png'): print(f.relative_to(HERE), f.stat().st_size)
