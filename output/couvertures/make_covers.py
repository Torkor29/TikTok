"""Couvertures 3:4 (1080x1440) et 4:3 (1440x1080) des 3 concepts : image de la vidéo + titre en bandes de papier (DA papier)."""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import engine as E
from story import ransom_line
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
OUT = os.path.dirname(os.path.abspath(__file__))
KRAFT = (236, 226, 204); NAVY = (20, 36, 82); RED = (206, 36, 44); MUST = (250, 202, 60); INK = (24, 22, 28); WHITE = (250, 248, 240)
def lab(txt, size, fg, bg, key, font="title"): return E.Label(txt, key, E.font(font, size), fg, bg, padx=28, pady=10, rough=2.5)
def kraft(w, h):
    rng = np.random.default_rng(1); a = np.zeros((h, w, 3), np.float32); a[:] = KRAFT; a *= (.95 + .08*E._lowfreq(w, h, 3, 60))[..., None]
    sp = rng.random((h, w)); a += ((sp > .985)*-22 + (sp < .01)*14)[..., None]; return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
def framed(img, w, h, rot=-2):
    """Image de la vidéo collée comme une photo papier (bord blanc déchiré, ombre)."""
    im = img.convert("RGB").resize((w, h), Image.LANCZOS); spr = E.paper_sprite(E.rect_pts(w + 36, h + 36), (250, 248, 240), seed=w, rough=3)
    ax, ay = spr.info["anchor"]; spr.paste(im, (int(ax - w/2), int(ay - h/2))); return spr
COV = [("tactique_433", [("LE 4-3-3", 150, MUST, INK), ("DU PSG", 130, WHITE, NAVY), ("EXPLIQUÉ SIMPLEMENT", 64, WHITE, RED)]),
       ("tactique_lateral", [("LE LATÉRAL", 140, MUST, INK), ("MODERNE", 130, WHITE, NAVY), ("EN 4 POINTS", 70, WHITE, RED)]),
       ("tactique_vitinha", [("LE PLUS IMPORTANT", 96, MUST, INK), ("DU PSG ?", 130, WHITE, NAVY), ("PAS DEMBÉLÉ", 80, WHITE, RED)]),
       ("quiz_psg_vrai", [("QUIZ PSG", 150, MUST, INK), ("5/5 OU FOOTIX ?", 96, WHITE, RED)]),
       ("salaire_mbappe", [("LE VRAI SALAIRE", 110, WHITE, INK), ("DE MBAPPÉ", 140, INK, MUST), ("SECONDE PAR SECONDE", 64, WHITE, RED)]),
       ("quiz_niveaux", [("CE QUIZ FOOT", 120, INK, MUST), ("DE PLUS EN PLUS DUR", 76, WHITE, RED), ("À QUEL NIVEAU TU BLOQUES ?", 58, INK, WHITE)]),
       ("rabiot", [("RABIOT", 170, WHITE, RED), ("FORMÉ AU PSG…", 80, WHITE, NAVY), ("FINI À L'OM", 80, INK, (130, 200, 235)), ("TRAÎTRE OU INCOMPRIS ?", 58, INK, MUST)])]
ONLY = sys.argv[1:]
for slug, lines in COV:
    if ONLY and slug not in ONLY: continue
    fr = Image.open(os.path.join(OUT, f"{slug}_frame.png"))
    # 3:4 : la bande centrale de la vidéo (y 240..1680) + le titre par-dessus en haut
    c = fr.crop((0, 240, 1080, 1680)).convert("RGBA"); c.alpha_composite(Image.new("RGBA", c.size, (10, 8, 16, 70)))
    y = 150
    for k, (txt, sz, fg, bg) in enumerate(lines):
        lab(txt, sz, fg, bg, f"c34{slug}{k}").draw(c, 0, 540, y, 1, (-3, 2, -2, 3)[k]); y += sz*1.05 + 30
    c.convert("RGB").save(os.path.join(OUT, f"{slug}_couverture_3x4.jpg"), quality=92)
    # 4:3 : photo de la vidéo à gauche, titre à droite, sur kraft
    L = kraft(1440, 1080); ph = framed(fr.crop((0, 240, 1080, 1680)), 600, 800); E.blit(L, ph, 360, 545, 1, -3)
    y = 300 - 40*(len(lines) - 3)
    for k, (txt, sz, fg, bg) in enumerate(lines):
        s = min(1.0, 700/max(1, E.font("title", sz).getlength(txt) + 60)); lab(txt, sz, fg, bg, f"c43{slug}{k}").draw(L, 0, 1050, y, s, (-3, 2, -2, 3)[k]); y += sz*s*1.1 + 40
    L.convert("RGB").save(os.path.join(OUT, f"{slug}_couverture_4x3.jpg"), quality=92)
    print(slug)
