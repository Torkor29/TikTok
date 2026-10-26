"""Couverture 9:16 + 3:4 : tout dans la zone sûre y 260..1660."""
import sys, os
sys.argv = [sys.argv[0], "--noop"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bdo_favoris import *
L = Image.new("RGBA", (W, H), (0, 0, 0, 255)); dark_bg(L, 1.0, (200, 160, 60), "cv"); rays(L, (CX, 900), 1.0, .6, 16, 1800, (70, 56, 20), .08, .25)
glow_spot(L, CX, 820, 380, (120, 90, 20)); put(L, gold_ball(110), CX, 820, 1, 0)
BG = L.copy()
for i, (n, x, h, col) in enumerate((("yamal", 140, 560, (255, 200, 60)), ("kane", 330, 500, (255, 70, 60)), ("dembele", 750, 540, (90, 140, 255)), ("mbappe", 950, 480, (140, 200, 255)), ("rodri", CX, 460, (120, 220, 255)))):
    sp = CUT(n, h); aura(L, sp, x, 1820, 1.3, col, .6, i); put(L, sp, x, 1820, 1, 0)
L.paste(BG.crop((0, 1660, W, H)), (0, 1660))
flare(L, CX - 50, 760, 1.0, (255, 230, 160), .7)
KW("QUI MÉRITE", NOIR, BLANC, 92).draw(L, 0, CX, 330, 1, -3)
KW("LE BALLON D'OR ?", GOLD, NOIR, 92).draw(L, 0, CX, 460, 1, 2)
card("POUR", True, 54).draw(L, 0, 300, 1080, 1, -6); card("CONTRE", False, 54).draw(L, 0, 790, 1080, 1, 6)
out = os.path.join(ROOT, "output", SLUG, SLUG + "_couverture.jpg"); os.makedirs(os.path.dirname(out), exist_ok=True)
L.convert("RGB").save(out, quality=92); L.convert("RGB").crop((0, 240, W, 1680)).save(out.replace(".jpg", "_3x4.jpg"), quality=92); print(out)
