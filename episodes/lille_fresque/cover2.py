"""Couverture v2 LOSC : flashy, fierté des fans (titre 2021, PSG battu), zone sûre 3:4 y 260..1660."""
import sys, os
sys.argv = sys.argv[:1]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lille_fresque import *
from lille_scrapbook import medal
from brest_ldc import _img

def cover2(path):
    cv = background(0, TITLE); stage_fill(cv, 0, ROUGE, "lfcv2bg")
    rays(cv, (CX, 900), .4, 1.0, 20, 1900, (184, 8, 26), .1, .5)
    confetti(cv, 0, "lfcv2cf", 2.2, 120, 4, [JAUNE, BLANC, NAVY])
    big("RUINÉ EN DÉCEMBRE…", "lfcv2a", 86, BLANC, NOIR).draw(cv, 0, CX, 330, 1, -3)
    lo = _img(os.path.join(ROOT, "assets", "logos", "lille_sticker.png"), 700)
    blit_sxy(cv, lo[1], CX + 20, 920, 1, 1, -4); blit_sxy(cv, lo[0], CX, 900, 1, 1, -4)
    m = medal(120); blit_sxy(cv, m[1], 870, 1140, 1, 1, 14); blit_sxy(cv, m[0], 856, 1124, 1, 1, 14)
    ps = _img(os.path.join(ROOT, "assets", "logos", "psg_sticker.png"), 210)
    blit_sxy(cv, ps[0], 200, 1150, 1, 1, -10)
    d = ImageDraw.Draw(cv); d.line([(110, 1060), (290, 1240)], fill=NOIR, width=22); d.line([(290, 1060), (110, 1240)], fill=NOIR, width=22)
    big("CHAMPION EN MAI !", "lfcv2b", 104, NOIR, JAUNE, rough=4, maxw=1060).draw(cv, 0, CX, 1430, 1, 3)
    big("LE TITRE 2021 DES DOGUES", "lfcv2c", 56, BLANC, NAVY).draw(cv, 0, CX, 1580, 1, -2)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

if __name__ == "__main__":
    print(cover2(os.path.join(ROOT, "output", "lille_fresque", "lille_fresque_couverture.jpg")))
