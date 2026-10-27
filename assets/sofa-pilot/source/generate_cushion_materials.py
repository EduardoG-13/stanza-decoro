"""Original procedural maps for the FIXED decorative cushion materials (EXT-001, rev 2.0.0).

Run (from the repo root, any numpy>=1.26 + Pillow):
    python assets/sofa-pilot/source/generate_cushion_materials.py
Writes ONLY under assets/sofa-pilot/materials/cushions/. It never touches the body fabric
families (generate_materials.py stays untouched and is not run).

Families
- olive-weave: chunky 2/2 basket/twill weave of olive cords over a lighter cream-olive weft,
  ~1.4 cm cells (10 cells per 0.14 m UV repeat). Own algorithm; SOFA-2.jpg was only looked at
  for the general look (scale, olive + cream yarns) and average colour, never sampled as texture.
  Maps: basecolor (sRGB) and normal (tangent-space OpenGL +Y, linear data). Roughness is a constant
  factor (0.92) in the material: a roughness map added ~160 kB to the GLB for no visible gain.
- light-boucle: light grey-beige base colour for the three light cushions = the project's own
  neutral bouclé base colour (materials/boucle/basecolor.jpg, CC0, generate_materials.py) times a
  fixed tint. Normal/roughness are SHARED with the body bouclé (no new maps, no extra bytes).
- olive-reverse: plain cream reverse face of the olive cushions (same neutral bouclé base times a
  cream tint); also shares the body bouclé normal/roughness.
Main maps are 512 px, mobile maps 256 px, all covering the same 0.14 m repeat.
Licence: original procedural output, CC0-1.0 to the extent rights exist.
"""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'materials' / 'cushions'
REPEAT_M = 0.14
N = 512
CELLS = 10                       # cells per repeat -> 14 mm cords
LIGHT_TINT = (188, 182, 174)     # light grey-beige cushions (cooler than body areia #d8c9b2)
REVERSE_TINT = (226, 220, 207)   # cream reverse of the olive cushions
OLIVE_CORD = np.array([72, 70, 44]) / 255     # olive warp cords
OLIVE_LIGHT = np.array([134, 127, 94]) / 255  # lighter cream-olive weft
GAP = np.array([34, 32, 20]) / 255


def periodic_noise(rng, n, sigma):
    f = np.fft.fftfreq(n)
    k = np.exp(-2 * np.pi ** 2 * sigma ** 2 * (f[None, :] ** 2 + f[:, None] ** 2))
    out = np.fft.ifft2(np.fft.fft2(rng.standard_normal((n, n))) * k).real
    return out / max(out.std(), 1e-8)


def normals(height, n):
    step = REPEAT_M / n
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) / (2 * step)
    dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) / (2 * step)
    nrm = np.stack([-dx, dy, np.ones_like(dx)], -1)      # image rows run down; +v runs up
    return nrm / np.linalg.norm(nrm, axis=-1, keepdims=True)


def weave(n, seed=2051):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:n, 0:n].astype(np.float64) / n * CELLS     # cell coordinates
    i, j = np.floor(x), np.floor(y)
    fx, fy = x - i, y - j                                        # 0..1 inside a cell
    jitter = periodic_noise(rng, n, n / 90) * .035
    # Cord cross-sections: wide olive warp cords (rows) and narrower cream-olive weft (columns).
    dw = np.clip(np.abs(fy - .5 + jitter) / .47, 0, 1)
    dv = np.clip(np.abs(fx - .5 - jitter) / .26, 0, 1)
    warp_prof = np.sqrt(1 - dw ** 2); weft_prof = np.sqrt(1 - dv ** 2)
    # 2/2 twill: warp row j floats over x in [j, j+2) (mod 4), weft column i over y in
    # [i-3, i-1); the float/dip follows a continuous cosine ALONG each cord (no cell steps).
    warp_lift = .5 + .5 * np.cos(2 * np.pi * (x - (j + 1)) / 4)
    weft_lift = .5 + .5 * np.cos(2 * np.pi * (y - (i - 2)) / 4)
    # Plied-yarn twist only (no pixel-scale noise: it costs PNG bytes and is invisible at 14 mm cords).
    ply = .10 * np.sin(2 * np.pi * (x * 2.6 + y * 1.3))
    hw = warp_prof ** .7 * (.35 + .65 * warp_lift) + ply * warp_prof
    hv = weft_prof ** .7 * (.35 + .65 * weft_lift) + ply * weft_prof
    top_warp = hw >= hv
    height = np.maximum(hw, hv)
    height = np.where(np.maximum(warp_prof, weft_prof) > 0, height, 0)
    height_m = height * .0032                                  # ~3 mm cord relief
    cord_var = .08 * periodic_noise(rng, n, n / 40)
    fleck = np.clip(periodic_noise(rng, n, 1.6) - 1.2, 0, 1) * .5
    base_w = OLIVE_CORD[None, None, :] * (1 + cord_var[..., None]) + fleck[..., None] * (OLIVE_LIGHT - OLIVE_CORD)
    base_v = OLIVE_LIGHT[None, None, :] * (1 + .6 * cord_var[..., None])
    color = np.where(top_warp[..., None], base_w, base_v)
    cover = np.clip(height / .55, 0, 1)[..., None]               # gaps between cords read darker
    color = GAP + (color - GAP) * (.35 + .65 * cover)
    return np.clip(color, 0, 1), height_m


def save_family(folder, color, height_m, n):
    folder.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.uint8(np.round(color * 255))).save(folder / 'basecolor.jpg', quality=90, subsampling=0, optimize=True)
    nrm = normals(height_m, n)
    Image.fromarray(np.uint8(np.round((nrm * .5 + .5) * 255))).save(folder / 'normal.png', optimize=True)


def tinted(neutral, tint, n, folder):
    folder.mkdir(parents=True, exist_ok=True)
    im = neutral.resize((n, n), Image.Resampling.LANCZOS)
    a = np.asarray(im.convert('RGB')).astype(np.float64) / 255
    a = a / a.mean() * .97                                    # neutral map normalised around ~1
    out = np.clip(a * (np.array(tint) / 255), 0, 1)
    Image.fromarray(np.uint8(np.round(out * 255))).save(folder / 'basecolor.jpg', quality=90, subsampling=0, optimize=True)


if __name__ == '__main__':
    neutral = Image.open(ROOT / 'materials' / 'boucle' / 'basecolor.jpg')
    for size, sub in ((N, ''), (N // 2, 'mobile')):
        c, h = weave(size)
        save_family(OUT / 'olive-weave' / sub, c, h, size)
        tinted(neutral, LIGHT_TINT, size, OUT / 'light-boucle' / sub)
        tinted(neutral, REVERSE_TINT, size // 2, OUT / 'olive-reverse' / sub)
    print('written', sorted(str(p.relative_to(ROOT)) for p in OUT.rglob('*.*')))
