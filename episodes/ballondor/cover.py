"""Couverture 1080x1920 : « TON BALLON D'OR ? » + trophée papier + 5 favoris."""
import sys, os
sys.argv = [sys.argv[0], "--noop"]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ballondor as B
from ballondor import *
L = Image.new("RGBA", (W, H)); gala_bg(L, 1.0)
for i, (n, x, s) in enumerate((("yamal", 120, 700), ("kane", 330, 600), ("dembele", 750, 640), ("mbappe", 960, 560))):
    put(L, CUT(n, s), x, 1920, 1, (-4, -2, 2, 4)[i])
put(L, CUT("rodri", 520), CX, 1930, 1, 0)
put(L, gold_ball(150), CX, 860, 1, 0)
sparks_burst(L, .2, 0, CX, 800, 16, (255, 230, 120), 330)
LBL("LE VOTE DES SUPPORTERS", "cv1", font("mono", 46), GOLD, NOIR, padx=20, pady=8, rough=1.5).draw(L, 0, CX, 150, 1, 0)
KW("TON", NOIR, BLANC, 110).draw(L, 0, CX, 290, 1, -3)
KW("BALLON D'OR ?", GOLD, NOIR, 96).draw(L, 0, CX, 430, 1, 2)
stampl("VOTE EN COMMENTAIRE", ROUGE, 64).draw(L, 0, CX, 1200, 1, -4)
out = os.path.join(ROOT, "output", "ballon_dor_supporters", "ballon_dor_supporters_couverture.jpg")
L.convert("RGB").save(out, quality=92); print(out)
