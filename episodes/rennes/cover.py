"""Couverture Rennes (zone sûre 3:4 : y 260..1660)."""
import sys, os
sys.argv = sys.argv[:1]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rennes3 import *
cv = Image.new("RGBA", (W, H)); stripes_bg(cv, key="cover"); dark(cv, .2)
kword("LE CLUB LE PLUS", NOIR, BLANC, 104).draw(cv, 0, CX, 380, 1, -3)
kword("MAUDIT", ROUGE, BLANC, 170).draw(cv, 0, CX, 540, 1, 2)
put(cv, shadowed(sticker("rennes", 600), "cvcrest"), CX, 1010, 1.0, -4)
draw_cat(cv, 830, 1330, 0, 1.0, moving=False, face=-1)
kword("DE FRANCE ?", JAUNE, NOIR, 120).draw(cv, 0, CX, 1420, 1, -2)
kword("L'HISTOIRE DU STADE RENNAIS", NOIR, BLANC, 54).draw(cv, 0, CX, 1580, 1, 2)
cv.convert("RGB").save(os.path.join(ROOT, "output", "rennes_v3", "rennes_v3_couverture.jpg"), quality=94); print("ok")
