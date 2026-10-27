"""Pixel mask check: body colour changes must leave decorative / structure pixels unchanged.

    python scripts/models3d/mask_check.py <capture_dir> <run_label> <view> <reference_pass> <pass> [<pass> ...]

Uses the region masks written by capture.mjs (`<run>__<pass>__<view>__mask.png`; body red,
decorative green, contrast yellow, exterior-structure blue). Each mask is eroded by 2 px so anti-aliased
silhouettes are excluded. Prints JSON: per pass, mean/max absolute RGB difference against
the reference pass inside each region, and the pixel count of each region.
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

COLS = {'body': (255, 0, 0), 'decorative': (0, 255, 0), 'contrast': (255, 255, 0), 'exterior-structure': (0, 0, 255)}

def region_masks(path):
    m = np.asarray(Image.open(path).convert('RGB')).astype(int)
    out = {}
    for name, c in COLS.items():
        mask = (np.abs(m - np.array(c)).sum(-1) < 60)
        er = Image.fromarray(np.uint8(mask*255)).filter(ImageFilter.MinFilter(5))
        out[name] = np.asarray(er) > 0
    return out

def check(d, run, view, ref, passes):
    d = Path(d)
    img = lambda p: np.asarray(Image.open(d/f'{run}__{p}__{view}.png').convert('RGB')).astype(int)
    masks = region_masks(d/f'{run}__{ref}__{view}__mask.png')
    base = img(ref); res = {'view': view, 'reference': ref, 'pixels': {k: int(v.sum()) for k, v in masks.items()}, 'passes': {}}
    for p in passes:
        diff = np.abs(img(p)-base).max(-1)
        mp = d/f'{run}__{p}__{view}__mask.png'
        same_mask = bool(mp.is_file() and (np.asarray(Image.open(mp).convert('RGB')) == np.asarray(Image.open(d/f'{run}__{ref}__{view}__mask.png').convert('RGB'))).all())
        res['passes'][p] = {'maskIdentical': same_mask, **{k: {'meanAbs': round(float(diff[m].mean()), 3) if m.any() else None, 'max': int(diff[m].max()) if m.any() else None} for k, m in masks.items()}}
    return res

if __name__ == '__main__':
    d, run, view, ref, *passes = sys.argv[1:]
    print(json.dumps(check(d, run, view, ref, passes), indent=1))
