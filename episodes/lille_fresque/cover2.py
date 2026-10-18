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
    big("L'HISTOIRE", "lfcv3a", 130, BLANC, NOIR, rough=4).draw(cv, 0, CX, 340, 1, -3)
    from lille_scrapbook import polaroid
    for sp, x, y, r in ((polaroid(os.path.join(ROOT, "assets", "lille", "hazard_card.png"), "Hazard", 300), 200, 760, -12),
                        (medal(100), 900, 760, 14)):
        blit_sxy(cv, sp[1], x + 12, y + 16, 1, 1, r); blit_sxy(cv, sp[0], x, y, 1, 1, r)
    lo = _img(os.path.join(ROOT, "assets", "logos", "lille_sticker.png"), 620)
    blit_sxy(cv, lo[1], CX + 18, 958, 1, 1, -3); blit_sxy(cv, lo[0], CX, 940, 1, 1, -3)
    for nm, x, y, h, r in (("ucl", 190, 1180, 210, -10), ("ligue1", 900, 1170, 200, 10)):
        st = _img(os.path.join(ROOT, "assets", "logos", f"{nm}_sticker.png"), h); blit_sxy(cv, st[0], x, y, 1, 1, r)
    big("INCROYABLE DU LOSC", "lfcv3b", 104, NOIR, JAUNE, rough=4, maxw=1060).draw(cv, 0, CX, 1420, 1, 3)
    big("DE 1944 À 2021 : TOUT CE QUE TU NE SAIS PAS", "lfcv3c", 44, BLANC, NAVY, maxw=1000).draw(cv, 0, CX, 1570, 1, -2)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

if __name__ == "__main__":
    print(cover2(os.path.join(ROOT, "output", "lille_fresque", "lille_fresque_couverture.jpg")))
