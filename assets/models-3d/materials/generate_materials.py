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
TINTS = {'gelo': (186, 188, 192), 'grafite-quente': (84, 80, 80), 'cru': (226, 221, 210), 'cinza-malva': (138, 130, 134)}


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


def blur(a, s):
    """Periodic gaussian blur (sigma in px)."""
    n = a.shape[0]; fx = np.fft.fftfreq(n)[None, :]; fy = np.fft.fftfreq(n)[:, None]
    return np.fft.ifft2(np.fft.fft2(a)*np.exp(-2*np.pi**2*s*s*(fx*fx+fy*fy))).real


def weave(rng, threads, pattern, thick=.08, slub=0.0, slub_len=60, profile=.8):
    """Periodic woven height field (0..1) + per-pixel warp-on-top mask + per-thread tone.
    threads: threads per tile on each axis (must divide N). pattern(i, j) -> bool array, True =
    warp (vertical yarn) on top at weft row i / warp column j. thick: random yarn thickness
    variation; slub: amplitude of elongated thickness swellings along each yarn (linen slubs)."""
    p = N // threads
    Y, X = np.mgrid[0:N, 0:N]
    i = Y // p; j = X // p; fy = (Y % p + .5)/p; fx = (X % p + .5)/p
    warp_top = pattern(i, j)
    tw = 1 + thick*rng.standard_normal(threads)[j]; tf = 1 + thick*rng.standard_normal(threads)[i]
    if slub:
        # elongated swellings along each yarn: noise long along the yarn, one yarn wide across
        along_w = noise(rng, p*.35, slub_len)        # long in Y (warp runs along Y)
        along_f = noise(rng, slub_len, p*.35)        # long in X (weft runs along X)
        tw = tw*(1+slub*np.clip(along_w, 0, None)**1.5); tf = tf*(1+slub*np.clip(along_f, 0, None)**1.5)
    hw = np.cos(np.pi*(fx-.5))**profile*tw          # warp yarn cross-section (across X)
    hf = np.cos(np.pi*(fy-.5))**profile*tf          # weft yarn cross-section (across Y)
    # yarn crimp: the top yarn dips where it goes under at the next crossing
    h = np.where(warp_top, .55+.45*hw, .55+.45*hf)*np.where(warp_top, tw, tf)**.5
    h = blur(h, .6)
    tone = np.where(warp_top, rng.normal(0, 1, threads)[j], rng.normal(0, 1, threads)[i])
    return h, warp_top, tone


def write_decor(fid, rgb, height, rough, repeat_m, meta):
    """Decorative (fixed) print/jacquard family: basecolor holds the printed design (never a
    photo). Also writes embedded/basecolor-512/256.jpg for GLB embedding."""
    meta, col, _ = write_family(fid, height, None, rough, repeat_m, meta, rgb=rgb)
    for s in (512, 256):
        Image.fromarray(np.uint8(np.round(np.clip(col, 0, 1)*255))).resize((s, s), Image.Resampling.BOX).save(HERE/fid/'embedded'/f'basecolor-{s}.jpg', quality=90, subsampling=0, optimize=True)
    meta['decorative'] = True
    return meta


def sarja():
    """Flat 2/2 twill upholstery cloth (EXT-003, SOFA-3.jpg): tight, matte, very even; 256
    yarns per 0.30 m tile (1.17 mm pitch), soft diagonal rib, faint heather from yarn tone."""
    rng = np.random.default_rng(707)
    repeat_m = .30
    h, top, tone = weave(rng, 256, lambda i, j: ((i+j) % 4) < 2, thick=.02)
    fuzz = noise(rng, .8)
    height = .00016*h + .000006*fuzz + .000012*noise(rng, 40)
    color = np.clip(.80 + .007*tone + .012*fuzz + .006*noise(rng, 30) - .05*(1-h), 0, 1)
    rough = np.clip(.88 + .03*(1-h) + .02*noise(rng, 2), 0, 1)
    meta = {'label': 'Sarja', 'family': 'flat_twill_upholstery_study', 'seed': 707, 'normalScale': .9,
            'roughness': 1.0, 'sheen': .10, 'sheenRoughness': .8,
            'description': 'Sarja 2/2 de trama fechada e fosca (fios de ~1,2 mm, diagonal suave). Estudo visual próprio a partir de SOFA-3.jpg; sem código comercial.',
            'createdFor': 'EXT-003 (sofas/SOFA-3.jpg); reutilizada no EXT-005 (acervo/sofa-com-vivo.webp)'}
    meta, col, _ = write_family('sarja', height, color, rough, repeat_m, meta)
    meta['embedded'] = {t: tinted('sarja', col, t) for t in ('grafite-quente', 'cinza-malva')}
    meta['embedded'].update({'normal': ['embedded/normal-512.png', 'embedded/normal-256.png'],
                             'roughness': ['embedded/roughness-512.jpg', 'embedded/roughness-256.jpg']})
    return meta


def decor_losango():
    """Printed nested-diamond (losango) cushion design for the fixed decorative pillows of
    EXT-003: white ground, dusty light blue and grey-blue concentric diamonds, period 0.15 m
    (2 per 0.30 m tile). Drawn procedurally; the woven relief comes from the cloth normal."""
    rng = np.random.default_rng(708)
    repeat_m = .30
    Y, X = np.mgrid[0:N, 0:N].astype(np.float64)
    cell = N/2
    u = ((X % cell)/cell - .5)*2; v = ((Y % cell)/cell - .5)*2
    d = np.abs(u)+np.abs(v)                 # 0 centre .. 1 diamond edge .. 2 cell corner
    d2 = np.abs(((X+cell/2) % cell)/cell*2-1)+np.abs(((Y+cell/2) % cell)/cell*2-1)   # offset lattice
    d = np.minimum(d, d2)
    white = np.array([232, 234, 234])/255; blue = np.array([150, 182, 198])/255; grey = np.array([118, 140, 156])/255; pale = np.array([196, 212, 220])/255
    wob = .006*noise(rng, 6)                 # slightly irregular print edges
    dd = d + wob
    rgb = np.empty((N, N, 3)); rgb[:] = white
    for lo, hi, c in ((0, .09, grey), (.09, .15, white), (.15, .38, blue), (.38, .44, white), (.44, .64, pale), (.64, .69, white), (.69, .90, grey), (.90, 1.1, white)):
        m = (dd >= lo) & (dd < hi); rgb[m] = c
    rgb = np.stack([blur(rgb[..., k], .8) for k in range(3)], -1)
    h, _t, tone = weave(rng, 256, lambda i, j: ((i+j) % 2) == 0, thick=.05)
    rgb = np.clip(rgb*(1+.02*tone[..., None]-.04*(1-h[..., None])), 0, 1)
    height = .00012*h
    rough = np.clip(.9+.02*noise(rng, 2), 0, 1)
    meta = {'label': 'Estampa losangos azul (decorativa)', 'family': 'printed_cushion_design', 'seed': 708, 'normalScale': .8,
            'description': 'Estampa de losangos concêntricos azul claro e cinza-azulado sobre fundo branco, desenhada proceduralmente a partir da leitura de SOFA-3.jpg (não é a foto). Somente almofadas decorativas fixas.',
            'createdFor': 'EXT-003 (almofadas estampadas de SOFA-3.jpg)'}
    return write_decor('decor-losango', rgb, height, rough, repeat_m, meta)


def linho_rustico():
    """Slubbed plain-weave linen-look upholstery (EXT-004, acervo/sofa-dois-assentos.webp):
    256 yarns per 0.30 m tile, elongated slubs (thicker, slightly lighter yarn swellings) and a
    faint irregular yarn tone, matte. Neutral maps; the colour comes from the tint."""
    rng = np.random.default_rng(709)
    repeat_m = .30
    h, top, tone = weave(rng, 256, lambda i, j: ((i+j) % 2) == 0, thick=.03, slub=.35, slub_len=40)
    fuzz = noise(rng, .8)
    sl = blur(np.clip(h-1.0, 0, None), 1.0)          # where slubs swell above the regular yarn crest
    height = .00018*h + .00006*sl + .000006*fuzz
    color = np.clip(.80 + .010*tone + .03*sl + .012*fuzz + .005*noise(rng, 30) - .06*(1-np.clip(h, 0, 1)), 0, 1)
    rough = np.clip(.92 + .03*(1-np.clip(h, 0, 1)) + .015*noise(rng, 2), 0, 1)
    meta = {'label': 'Linho rústico', 'family': 'slub_plain_weave_study', 'seed': 709, 'normalScale': 1.0,
            'roughness': 1.0, 'sheen': .10, 'sheenRoughness': .85,
            'description': 'Tela de aspecto linho, trama simples com flamê (engrossamentos alongados dos fios), fosca. Estudo visual próprio a partir de sofa-dois-assentos.webp; sem código comercial.',
            'createdFor': 'EXT-004 (acervo/sofa-dois-assentos.webp)'}
    meta, col, _ = write_family('linho-rustico', height, color, rough, repeat_m, meta)
    meta['embedded'] = {'cru': tinted('linho-rustico', col, 'cru'),
                        'normal': ['embedded/normal-512.png', 'embedded/normal-256.png'],
                        'roughness': ['embedded/roughness-512.jpg', 'embedded/roughness-256.jpg']}
    return meta


def decor_quadrados():
    """Cut-velvet style lumbar-pillow design for the fixed decorative pillow of EXT-004: a dark
    brown pile ground holding staggered rows of light rosy-beige rectangles (some merged into
    short bars), each with a small darker centre; period 0.05 m (6 per 0.30 m tile). The dark
    pile is raised."""
    rng = np.random.default_rng(710)
    repeat_m = .30
    n = 6                                    # even row count keeps the half-cell stagger periodic
    Y, X = np.mgrid[0:N, 0:N].astype(np.float64)
    cy = (Y/(N/n)); row = np.floor(cy).astype(int) % n
    cx = X/(N/n) + .5*(row % 2)
    col = np.floor(cx).astype(int) % n
    u = (cx % 1)-.5; v = (cy % 1)-.5
    rs = (.37+.03*rng.standard_normal((n, n))).clip(.32, .42); asp = (1+.10*rng.standard_normal((n, n))).clip(.88, 1.15); bar = rng.uniform(size=(n, n)) < .25
    hs = rs[row, col]
    ax = np.where(bar[row, col], .48, np.minimum(hs*asp[row, col], .43)); ay = hs
    outer = np.maximum(np.abs(u)/ax, np.abs(v)/ay)
    light = blur((outer < 1.0).astype(float), 1.3)
    centre = blur((outer < .30).astype(float), 1.3)
    ground = np.array([214, 196, 186])/255; ink = np.array([46, 30, 27])/255; mid = np.array([128, 96, 84])/255
    rgb = ink*(1-light[..., None]) + ground*light[..., None]
    rgb = rgb*(1-.8*centre[..., None]) + mid*(.8*centre[..., None])
    pile = noise(rng, .7)
    rgb = np.clip(rgb*(1+.04*pile[..., None]), 0, 1)
    dark = 1-light
    height = .0006*dark + .00002*pile
    rough = np.clip(.95 - .10*dark + .02*noise(rng, 2), 0, 1)
    meta = {'label': 'Quadrados marrons (decorativa)', 'family': 'cut_velvet_cushion_design', 'seed': 710, 'normalScale': 1.0,
            'description': 'Fundo marrom-escuro em relevo (aspecto veludo cortado) com retângulos bege rosado em fileiras desencontradas, procedural a partir da leitura de sofa-dois-assentos.webp (não é a foto). Somente a almofada decorativa fixa.',
            'createdFor': 'EXT-004 (almofada lombar de sofa-dois-assentos.webp)'}
    return write_decor('decor-quadrados', rgb, height, rough, repeat_m, meta)


if __name__ == '__main__':
    fams = [boucle_mescla(), wood_wenge(), sarja(), decor_losango(), linho_rustico(), decor_quadrados()]
    index = {'contract': 'stanza-material-library/v1',
             'note': 'Biblioteca compartilhada de acabamentos da coleção 3D. Estudos visuais originais (CC0), não catálogo homologado; a tela não substitui amostra física.',
             'bodyUvMeters': .30,
             'families': fams,
             'reusedFamilies': {k: f'/assets/sofa-pilot/materials/{k}/' for k in ('boucle', 'linen', 'velvet')},
             'tints': {k: '#%02x%02x%02x' % v for k, v in TINTS.items()}}
    (HERE/'materials.json').write_text(json.dumps(index, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    for f in sorted(HERE.rglob('*')):
        if f.is_file() and f.suffix in ('.jpg', '.png'): print(f.relative_to(HERE), f.stat().st_size)
