"""Original procedural maps for the FIXED decorative cushion materials (EXT-001, rev 2.0.0).

Run (from the repo root, any numpy>=1.26 + Pillow):
    python assets/sofa-pilot/source/generate_cushion_materials.py
Writes ONLY under assets/sofa-pilot/materials/cushions/. It never touches the body fabric
families (generate_materials.py stays untouched and is not run).

Families
- olive-weave (2.1.0): fine basket weave - checkerboard of ~11.7 mm units (12 per 0.14 m UV
  repeat), each a pair of olive cords plied with cream yarn (small slanted cream flecks). 2.0.0
  used a 2/2 twill with 14 mm cells that read as big diagonal stripes. Own algorithm; SOFA-2.jpg was only looked at
  for the general look (scale, olive + cream yarns) and average colour, never sampled as texture.
  Maps: basecolor (sRGB) and normal (tangent-space OpenGL +Y, linear data). Roughness is a constant
  factor (0.92) in the material: a roughness map added ~160 kB to the GLB for no visible gain.
- light-boucle: light grey-beige base colour for the three light cushions = the project's own
  neutral bouclé base colour (materials/boucle/basecolor.jpg, CC0, generate_materials.py) times a
  fixed tint. Normal/roughness are SHARED with the body bouclé (no new maps, no extra bytes).
- olive-reverse: plain cream reverse face of the olive cushions (same neutral bouclé base times a
  cream tint); also shares the body bouclé normal/roughness.
Main base colours are 512 px, mobile 256 px; the olive NORMAL is half that (256 / 128 px, 2.1.0:
the ~2 mm cord relief needs fewer texels than the colour flecks, and it keeps the 5 MB initial
budget). All are powers of two and cover the same 0.14 m repeat.
Licence: original procedural output, CC0-1.0 to the extent rights exist.
"""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'materials' / 'cushions'
REPEAT_M = 0.14
N = 512                          # base colour 512 px main / 256 px mobile (~43 px per woven unit)
UNITS = 12                       # basket units per repeat -> ~11.7 mm woven units (2.0.0: 10 twill cells)
CORDS = 2                        # parallel cords per unit (basket pair)
TWISTS = 2.2                     # ply twists per unit along a cord
LIGHT_TINT = (186, 182, 175)     # light grey-beige cushions, a touch lighter/cooler than body areia #b6b0a8 (2.0.0: 188,182,174)
REVERSE_TINT = (226, 220, 207)   # cream reverse of the olive cushions
OLIVE_CORD = np.array([50, 48, 22]) / 255     # olive yarn (visual estimate from SOFA-2.jpg, not sampled)
CREAM = np.array([222, 212, 168]) / 255       # cream yarn plied with the olive
GAP = np.array([22, 22, 12]) / 255


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
    """EXT-001 r2 (2.1.0) basket weave. 2.0.0 used a 2/2 twill of long cosine floats; at viewing
    distance its float progression read as big DIAGONAL STRIPES. SOFA-2.jpg shows a fine basket
    weave of small woven units: here a checkerboard of square units (UNITS per 0.14 m repeat,
    ~11.7 mm each, ~43 units across a 50 cm cushion), each unit = a PAIR of parallel plied cords,
    horizontal and vertical units alternating. Every cord is olive plied with a cream yarn; the
    ply twist leaves small slanted cream flecks whose slant flips with the unit orientation, which
    gives the fine chevron sparkle of the photo instead of long lines. Own algorithm, CC0."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:n, 0:n].astype(np.float64) / n * UNITS        # unit coordinates
    i, j = np.floor(x), np.floor(y)
    fx, fy = x - i, y - j
    horiz = ((i + j) % 2) == 0
    jit = periodic_noise(rng, n, n / 60) * .02
    # across = position across the cords (2 cords per unit), along = along the cord
    across = np.where(horiz, fy, fx) + jit
    along = np.where(horiz, fx, fy)
    k = np.floor(np.clip(across, 0, .9999) * CORDS)
    t = np.clip(across, 0, .9999) * CORDS - k                        # 0..1 inside one cord
    prof = np.sqrt(np.clip(1 - (2 * t - 1) ** 2 / .92, 0, 1))       # round cord section
    dip = .45 + .55 * np.sin(np.pi * np.clip(along, 0, 1)) ** .5     # cord dives under at unit ends
    # Ply twist: two-yarn ply, cream strand where the twist phase is high; slant flips per unit.
    slant = np.where(horiz, 1.0, -1.0)
    unit_phase = .25 * ((i + j) % 2) + .04 * periodic_noise(rng, n, n / 60)   # regular rows, slight irregularity
    twist = np.sin(2 * np.pi * (along * TWISTS + slant * t * .85 + k * .5 + unit_phase))
    cream = np.clip((twist - .48) / .26, 0, 1) * np.clip((prof - .3) / .3, 0, 1)
    height = prof ** .8 * dip * (1 + .08 * twist)
    height_m = height * .0021                                       # ~2 mm cord relief
    unit_var = (rng.random((UNITS, UNITS)) - .5)[j.astype(int) % UNITS, i.astype(int) % UNITS] * .14
    low = periodic_noise(rng, n, n / 30) * .05
    olive = OLIVE_CORD[None, None, :] * (1 + unit_var[..., None] + low[..., None])
    color = olive + cream[..., None] * (CREAM[None, None, :] - olive) * .85
    shade = .30 + .70 * np.clip(height / .75, 0, 1) ** .8               # dark gaps between cords
    color = GAP + (color - GAP) * shade[..., None]
    return np.clip(color, 0, 1), height_m


def save_family(folder, color, height_m, n):
    folder.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.uint8(np.round(color * 255))).save(folder / 'basecolor.jpg', quality=88, subsampling=0, optimize=True)
    h = height_m.reshape(n // 2, 2, n // 2, 2).mean(axis=(1, 3))      # box-downsample the height, then derive normals
    nrm = normals(h, n // 2)
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
