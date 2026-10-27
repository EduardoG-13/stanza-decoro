"""Re-tint the EMBEDDED initial body bouclé (colour ID `areia`) - EXT-001 r2, revision 2.1.0.

Run from the repo root (any numpy>=1.26 + Pillow):
    python assets/sofa-pilot/source/generate_embedded_areia.py
Writes ONLY source/embedded-boucle-areia.jpg and source/mobile-boucle/basecolor.jpg.
It does NOT run generate_materials.py and does not touch the neutral fabric maps.

Same contract as generate_materials.embedded_variants(): neutral bouclé base colour
(materials/boucle/basecolor.jpg, CC0) times the areia tint in sRGB, box-filtered to 512 px.
The viewer's external path multiplies the same neutral map by COLORS.areia, so the tint below
MUST equal COLORS.areia in viewer/sofa-viewer.js and viewer/contract.json (tested).

2.0.0 used [216, 201, 178] (#d8c9b2), a warm cream that read plastic/yellow next to SOFA-2.jpg.
2.1.0 uses a light warm grey-beige read from the photo by eye (a VISUAL ESTIMATE of the
upholstery under the photo's light, not a measured dye or a commercial colour).
"""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
AREIA = (182, 176, 168)   # '#b6b0a8' == COLORS.areia (viewer + contract)

if __name__ == '__main__':
    neutral = np.asarray(Image.open(ROOT / 'materials' / 'boucle' / 'basecolor.jpg').convert('RGB')).astype(np.float64)
    tinted = Image.fromarray(np.uint8(np.round(np.clip(neutral * (np.array(AREIA) / 255.0), 0, 255))))
    small = tinted.resize((512, 512), Image.Resampling.BOX)
    for dest in (ROOT / 'source' / 'embedded-boucle-areia.jpg', ROOT / 'source' / 'mobile-boucle' / 'basecolor.jpg'):
        small.save(dest, quality=92, subsampling=0, optimize=True)
        print('written', dest.relative_to(ROOT))
