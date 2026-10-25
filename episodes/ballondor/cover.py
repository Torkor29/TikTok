"""Couverture 1080x1920 : « TON BALLON D'OR ? » + trophée papier + 5 favoris."""
import sys, os
sys.argv = [sys.argv[0], "--noop"]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ballondor as B
from ballondor import *
L = Image.new("RGBA", (W, H)); gala_bg(L, 1.0)
Y0 = 260                                                   # zone sûre TikTok : tout entre y 260 et 1660
P = Image.new("RGBA", (W, H), (0, 0, 0, 0))
for i, (n, x, s_) in enumerate((("yamal", 120, 560), ("kane", 330, 480), ("dembele", 750, 520), ("mbappe", 960, 450))):
    put(P, CUT(n, s_), x, 1800, 1, (-4, -2, 2, 4)[i])
put(P, CUT("rodri", 420), CX, 1810, 1, 0)
P.paste((0, 0, 0, 0), (0, 1660, W, H)); L.alpha_composite(P)
put(L, gold_ball(120), CX, 900, 1, 0)
sparks_burst(L, .2, 0, CX, 860, 16, (255, 230, 120), 280)
LBL("LE VOTE DES SUPPORTERS", "cv1", font("mono", 42), GOLD, NOIR, padx=20, pady=8, rough=1.5).draw(L, 0, CX, 310, 1, 0)
KW("TON", NOIR, BLANC, 100).draw(L, 0, CX, 440, 1, -3)
KW("BALLON D'OR 2026 ?", GOLD, NOIR, 84).draw(L, 0, CX, 580, 1, 2)
stampl("VOTE EN COMMENTAIRE", ROUGE, 60).draw(L, 0, CX, 1200, 1, -4)
out = os.path.join(ROOT, "output", "ballon_dor_supporters", "ballon_dor_supporters_couverture.jpg")
L.convert("RGB").save(out, quality=92); L.convert("RGB").crop((0, 240, W, 1680)).save(out.replace(".jpg", "_3x4.jpg"), quality=92); print(out)
