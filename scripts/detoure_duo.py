"""Coupe une image « deux bustes papier sur fond blanc » en 2 PNG détourés (gauche, droite).
Fond retiré par remplissage depuis les bords (pixels presque blancs), puis recadrage serré.
  python3 scripts/detoure_duo.py image.png sortie_gauche.png sortie_droite.png"""
import sys, numpy as np
from PIL import Image, ImageFilter
from collections import deque

def bg_mask(a, thr=232):
    h, w = a.shape[:2]; white = (a[..., :3].min(2) >= thr); m = np.zeros((h, w), bool); q = deque()
    for x in range(w): q.extend([(0, x), (h - 1, x)])
    for y in range(h): q.extend([(y, 0), (y, w - 1)])
    while q:
        y, x = q.popleft()
        if 0 <= y < h and 0 <= x < w and white[y, x] and not m[y, x]:
            m[y, x] = True; q.extend([(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)])
    return m

def main(src, outl, outr):
    im = Image.open(src).convert("RGB"); a = np.array(im)
    m = bg_mask(a); fg = ~m
    cols = fg.sum(0); w = len(cols); mid = w//4 + int(np.argmin(cols[w//4: 3*w//4]))    # coupe au creux entre les deux bustes
    alpha = Image.fromarray((fg*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    rgba = im.convert("RGBA"); rgba.putalpha(alpha)
    for out, box in ((outl, (0, 0, mid, a.shape[0])), (outr, (mid, 0, w, a.shape[0]))):
        p = rgba.crop(box); bb = p.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox(); p.crop(bb).save(out)
        print(out, p.crop(bb).size)

if __name__ == "__main__": main(*sys.argv[1:4])
