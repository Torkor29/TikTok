"""CARROUSEL (mode photo TikTok) : « Mon top 6 des légendes des Bleus… le n°1 va faire débat » — 8 slides 1080x1920, 0 crédit.
Portraits papier déjà générés (assets/tu_gardes_qui1, assets/bordeaux), logo FFF en autocollant. Format EN TEST (skill viral §9).

  python3 episodes/carrousel_top6_bleus/carrousel_top6_bleus.py output/carrousel_top6_bleus
"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from quiz import *
from PIL import ImageFilter

TITLE = "~/top $ ./bleus"
NAVY = (18, 34, 92); NAVY_D = (10, 20, 56); NOIR = (30, 28, 28); BLANC = (250, 250, 246); ROUGE = (210, 36, 42)
A = lambda *p: os.path.join(ROOT, "assets", *p)

# (rang, nom, portrait, stat qui justifie, fond)
TOP = [
    (6, "GRIEZMANN", A("tu_gardes_qui1", "d3B.png"), "Meilleur joueur et meilleur buteur de l'Euro 2016", (30, 60, 140)),
    (5, "KANTÉ", A("tu_gardes_qui1", "d4A.png"), "Champion du monde 2018, partout sur le terrain", (120, 30, 50)),
    (4, "PLATINI", A("tu_gardes_qui1", "d1B.png"), "3 Ballons d'or d'affilée (1983, 84, 85)", (24, 80, 70)),
    (3, "HENRY", A("tu_gardes_qui1", "d2A.png"), "51 buts avec les Bleus", (70, 40, 110)),
    (2, "MBAPPÉ", A("tu_gardes_qui1", "d3A.png"), "Triplé en finale de Coupe du monde 2022", (140, 70, 20)),
    (1, "ZIDANE", A("tu_gardes_qui1", "d1A.png"), "2 buts de la tête en finale 98", (18, 34, 92)),
]

def sticker(cv, path, x, y, h, rot=0.0):
    im = Image.open(path).convert("RGBA"); im = im.resize((int(im.width*h/im.height), h), Image.LANCZOS)
    im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda v: v*100//255)); sh = sh.filter(ImageFilter.GaussianBlur(10))
    x0, y0 = int(x - im.width/2), int(y - im.height/2)
    cv.paste(sh, (x0 + 14, y0 + 18), sh); cv.paste(im, (x0, y0), im)

def base(bg, seed):
    cv = background(0, TITLE); stage_fill(cv, 0, bg, f"ctb{seed}")
    rays(cv, (CX, 1100), .3 + seed*.1, .7, 16, 1500, tuple(min(255, c + 35) for c in bg), .11)
    return cv

def swipe(cv, txt="swipe >>"):
    TAG(txt, "ctsw" + txt, PAL["paper"], NOIR, 48).draw(cv, 0, 860, 1790, 1, -4)

def page(cv, i, n):
    d = ImageDraw.Draw(cv)
    for k in range(n):
        x = CX + (k - (n - 1)/2)*34; r = 10 if k == i else 7
        d.ellipse([x - r, 1870 - r, x + r, 1870 + r], fill=BLANC if k == i else (150, 150, 160))

def slides():
    out = []; N = 8
    # 1) hook
    cv = base(NAVY, 0)
    ransom_line(cv, "MON TOP 6", 300, 150, seed=3)
    ransom_line(cv, "DES LÉGENDES", 470, 110, seed=7)
    ransom_line(cv, "DES BLEUS", 610, 130, seed=11)
    for k, (_, _, p, _, _) in enumerate(TOP[:5]):
        sticker(cv, p, 160 + k*190, 1180 + (k % 2)*110, 380, (-8, 5, -4, 7, -6)[k])
    sticker(cv, A("logos", "fff_bleu_sticker.png"), 900, 760, 230, 8)
    LBL("le n°1 va faire débat…", "ct1d", font("title", 70), NOIR, GOLD, padx=26, pady=8, rough=4).draw(cv, 0, CX, 1680, 1, -3)
    swipe(cv); page(cv, 0, N); out.append(cv)
    # 2-7) du 6 au 1
    for i, (rk, nm, p, stat, bg) in enumerate(TOP):
        cv = base(bg, i + 1)
        LBL(f"N°{rk}", f"ctr{rk}", font("title", 230 if rk > 1 else 260), NOIR, GOLD, padx=30, pady=0, rough=3).draw(cv, 0, CX, 330, 1, -5)
        if rk == 1: confetti(cv, 0, "ctcf", 1.2, 80, 3.5, [GOLD, BLANC, ROUGE])
        sticker(cv, p, CX, 960, 780, (-4, 3, -3, 4, -2, 0)[i])
        LBL(nm, f"ctn{rk}", font("title", 120), BLANC, ROUGE if rk == 1 else NOIR, padx=30, pady=6, rough=3).draw(cv, 0, CX, 1430, 1, 3)
        TAG(stat, f"cts{rk}", PAL["paper"], NOIR, 54, maxw=900).draw(cv, 0, CX, 1590, 1, -2)
        swipe(cv, "d'accord ? swipe >>" if rk > 1 else "t'es d'accord ?")
        page(cv, i + 1, N); out.append(cv)
    # 8) question pour les commentaires
    cv = base(NAVY_D, 9)
    ransom_line(cv, "ET TOI ?", 360, 170, seed=5)
    LBL("TON TOP 3 EN COMMENTAIRE", "ct8a", font("title", 78), NOIR, GOLD, padx=28, pady=8, rough=4, maxw=1000).draw(cv, 0, CX, 620, 1, -3)
    speech_bubble(cv, 0, "ct8b", "1. Zidane 2. Mbappé 3. ... ?", CX, 860, 1, (-1, 1), 60)
    LBL("QUI MANQUE ?", "ct8c", font("title", 96), BLANC, ROUGE, padx=26, pady=6, rough=3).draw(cv, 0, CX, 1110, 1, 4)
    for k, (_, _, p, _, _) in enumerate(TOP):
        sticker(cv, p, 130 + k*165, 1460 + (k % 2)*70, 260, (-6, 4, -3, 6, -5, 3)[k])
    BTN_SUB.draw(cv, 0, CX, 1720, .9, -2)
    page(cv, 7, N); out.append(cv)
    return out

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "output", "carrousel_top6_bleus")
    os.makedirs(out, exist_ok=True); paths = []
    for k, cv in enumerate(slides()):
        finish(cv, TITLE); p = os.path.join(out, f"slide_{k+1:02d}.png"); cv.convert("RGB").save(p); paths.append(p)
    print(paths)
