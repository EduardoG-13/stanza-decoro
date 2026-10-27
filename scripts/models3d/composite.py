"""Composite builder for models3d evidence (Pillow only).

    python scripts/models3d/composite.py spec.json

spec: {"out": "file.jpg", "cell": [w, h], "quality": 84, "title": "...",
       "rows": [[{"img": "path.png", "label": "texto", "crop": [x0,y0,x1,y1]?, "overlay": "ref.jpg"?}, ...], ...]}
Each cell is fitted (contain) into cell size; labels are drawn under it. "overlay" blends a
reference over the image at 50 % (silhouette/proportion check)."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def font(size):
    for f in ('/usr/share/fonts/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf', '/usr/share/fonts/google-noto/NotoSans-Regular.ttf'):
        if Path(f).is_file(): return ImageFont.truetype(f, size)
    return ImageFont.load_default()

def cell_image(c, W, H):
    im = Image.open(c['img']).convert('RGB')
    if c.get('crop'): im = im.crop(tuple(c['crop']))
    if c.get('overlay'):
        ref = Image.open(c['overlay']).convert('RGB').resize(im.size)
        im = Image.blend(im, ref, c.get('alpha', .5))
    im.thumbnail((W, H), Image.Resampling.LANCZOS)
    canvas = Image.new('RGB', (W, H), (245, 243, 238)); canvas.paste(im, ((W-im.width)//2, (H-im.height)//2))
    return canvas

def build(spec):
    W, H = spec.get('cell', [640, 480]); lab = 30; pad = 8
    rows = spec['rows']; ncol = max(len(r) for r in rows)
    top = 40 if spec.get('title') else 0
    out = Image.new('RGB', (pad+ncol*(W+pad), top+pad+len(rows)*(H+lab+pad)), (255, 255, 255))
    d = ImageDraw.Draw(out); f = font(17)
    if spec.get('title'): d.text((pad, 10), spec['title'], fill=(30, 30, 30), font=font(20))
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            x = pad+c*(W+pad); y = top+pad+r*(H+lab+pad)
            out.paste(cell_image(cell, W, H), (x, y))
            d.text((x+4, y+H+5), cell.get('label', ''), fill=(40, 40, 40), font=f)
    Path(spec['out']).parent.mkdir(parents=True, exist_ok=True)
    out.save(spec['out'], quality=spec.get('quality', 84), optimize=True)
    print(spec['out'], out.size, Path(spec['out']).stat().st_size)

if __name__ == '__main__':
    build(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')))
