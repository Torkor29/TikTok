"""CARROUSEL « ÉLECTION DU PLUS BEAU BUT » — Man City 2-4 PSG (LDC, 2e journée, 14/10/2026). 8 slides, 0 crédit.
Pas d'images de match : grosse icône ronde du buteur (photos fournies -> scripts/icone_joueur.py, assets/psg_city), écussons autocollants.
Buts (footmercato.net + eurosport.fr) : 13' Doué, 15' Dembélé (tête), 32' Vitinha, 53' Haaland, 63' Akliouche, 75' Haaland.

  python3 episodes/carrousel_buts_city_psg/carrousel_buts_city_psg.py output/carrousel_buts_city_psg
"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from quiz import *
from PIL import ImageFilter

TITLE = "~/vote $ ./plus_beau_but"
NOIR = (28, 26, 30); BLANC = (250, 250, 246); ROUGE = (210, 36, 42); JAUNE = (255, 222, 64)
PSG_BG = (16, 34, 80); CITY_BG = (92, 160, 214); GAZON = (58, 128, 74); GAZON2 = (66, 140, 82)
A = lambda *p: os.path.join(ROOT, "assets", *p)

# (n°, minute, buteur, club, score après, description courte, tir (x, y) sur le schéma, type de frappe)
BUTS = [
    (1, "13'", "DOUÉ", "psg", "0-1", "Frappe rasante aux 20 mètres, au premier poteau", (320, 370), "sol"),
    (2, "15'", "DEMBÉLÉ", "psg", "0-2", "De la tête au deuxième poteau", (690, 300), "tete"),
    (3, "32'", "VITINHA", "psg", "0-3", "Frappe après une talonnade de Zaïre-Emery", (760, 520), "air"),
    (4, "53'", "HAALAND", "city", "1-3", "City se réveille : Haaland réduit l'écart", (480, 330), "sol"),
    (5, "63'", "AKLIOUCHE", "psg", "1-4", "Le 4e but parisien, sur un service de Dembélé", (380, 470), "air"),
    (6, "75'", "HAALAND", "city", "2-4", "Doublé du pied droit, sur un service de Bouaddi", (560, 290), "sol"),
]

def sticker(cv, path, x, y, h, rot=0.0):
    im = Image.open(path).convert("RGBA"); im = im.resize((int(im.width*h/im.height), h), Image.LANCZOS)
    im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda v: v*100//255)); sh = sh.filter(ImageFilter.GaussianBlur(10))
    x0, y0 = int(x - im.width/2), int(y - im.height/2)
    cv.paste(sh, (x0 + 14, y0 + 18), sh); cv.paste(im, (x0, y0), im)
def crest(club): return A("logos", f"{club}_sticker.png")

def base(bg, seed):
    cv = background(0, TITLE); stage_fill(cv, 0, bg, f"cbp{seed}")
    rays(cv, (CX, 1000), .3 + seed*.1, .7, 16, 1600, tuple(min(255, c + 30) for c in bg), .1)
    return cv
def big(txt, key, size=110, fg=BLANC, bg=NOIR, rough=3, maxw=1000): return LBL(txt, key, font("title", size), fg, bg, padx=26, pady=6, rough=rough, maxw=maxw)
def page(cv, i, n):
    d = ImageDraw.Draw(cv)
    for k in range(n):
        x = CX + (k - (n - 1)/2)*34; r = 10 if k == i else 7
        d.ellipse([x - r, 1870 - r, x + r, 1870 + r], fill=BLANC if k == i else (150, 150, 160))

def schema(cv, shot, kind, key):
    """Carte papier : demi-terrain vu du dessus (but en haut), point de frappe, trajectoire en pointillés jusqu'au but."""
    Wc, Hc = 900, 700; card = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, Wc - 1, Hc - 1], 26, fill=GAZON)
    for k in range(7):
        if k % 2: d.rectangle([20, 20 + k*94, Wc - 20, 20 + (k + 1)*94], fill=GAZON2)
    L = BLANC; d.rectangle([20, 20, Wc - 20, Hc - 20], outline=L, width=6)
    d.rectangle([200, 20, Wc - 200, 300], outline=L, width=6); d.rectangle([330, 20, Wc - 330, 110], outline=L, width=6)
    d.arc([330, 200, Wc - 330, 400], 20, 160, fill=L, width=6); d.ellipse([444, 214, 456, 226], fill=L)
    d.rectangle([380, 2, Wc - 380, 22], fill=BLANC, outline=NOIR, width=4)                 # le but
    sx, sy = shot; gx = 405 if sx < 450 else 495                                          # vise le poteau le plus proche
    if kind == "tete": gx = 405 if sx > 450 else 495                                      # tête : deuxième poteau
    n = 22
    for k in range(n):
        if k % 2: continue
        u0, u1 = k/n, (k + 1)/n
        bow = 60 if kind == "air" else 0
        p0 = (lerp(sx, gx, u0), lerp(sy, 14, u0) - bow*math.sin(u0*math.pi))
        p1 = (lerp(sx, gx, u1), lerp(sy, 14, u1) - bow*math.sin(u1*math.pi))
        d.line([p0, p1], fill=JAUNE, width=10)
    d.ellipse([sx - 22, sy - 22, sx + 22, sy + 22], fill=BLANC, outline=NOIR, width=5)
    d.ellipse([gx - 16, 4, gx + 16, 36], fill=JAUNE, outline=NOIR, width=4)
    card = card.rotate(-2, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0)); sh.putalpha(card.getchannel("A").point(lambda v: v*90//255)); sh = sh.filter(ImageFilter.GaussianBlur(12))
    return card, sh

def slides():
    out = []; N = 8
    # 1) hook / règle du vote
    cv = base(PSG_BG, 0)
    ransom_line(cv, "LE PLUS BEAU", 260, 150, seed=3)
    ransom_line(cv, "BUT ?", 430, 190, seed=8)
    sticker(cv, crest("city"), 170, 830, 280, -8); sticker(cv, crest("psg"), 910, 830, 280, 8)
    big("2 - 4", "cbs", 180, NOIR, BLANC).draw(cv, 0, CX, 830, 1, 0)
    big("6 BUTS. 1 SEUL GAGNANT.", "cb1a", 70, NOIR, JAUNE).draw(cv, 0, CX, 1150, 1, -2)
    TAG("Swipe, puis vote en commentaire : 1, 2, 3, 4, 5 ou 6", "cb1b", PAL["paper"], NOIR, 52, maxw=900).draw(cv, 0, CX, 1350, 1, 2)
    big("LDC • 14 OCT.", "cb1c", 54, BLANC, NOIR).draw(cv, 0, CX, 1560, 1, -2)
    TAG("swipe >>", "cbsw", PAL["paper"], NOIR, 48).draw(cv, 0, 860, 1780, 1, -4)
    page(cv, 0, N); out.append(cv)
    # 2-7) un but par slide
    for i, (n, mn, who, club, sc, desc, shot, kind) in enumerate(BUTS):
        cv = base(PSG_BG if club == "psg" else CITY_BG, i + 1)
        big(f"BUT N°{n}", f"cbn{n}", 150, NOIR, JAUNE, rough=4).draw(cv, 0, CX, 190, 1, -4)
        sticker(cv, crest(club), 170, 470, 230, -8)
        big(who, f"cbw{n}", 120, BLANC, ROUGE if club == "psg" else NOIR).draw(cv, 0, 600, 430, 1, 3)
        big(f"{mn}  •  {sc}", f"cbm{n}", 64, NOIR, BLANC).draw(cv, 0, 600, 570, 1, -2)
        icon = {"DOUÉ": "doue", "DEMBÉLÉ": "dembele", "VITINHA": "vitinha", "HAALAND": "haaland", "AKLIOUCHE": "akliouche"}[who]
        sticker(cv, A("psg_city", f"{icon}.png"), CX, 1060, 800, (-3, 2, -2, 3, -2, 2)[i])
        TAG(desc, f"cbd{n}", PAL["paper"], NOIR, 54, maxw=920).draw(cv, 0, CX, 1530, 1, -2)
        STAMP(f"TON VOTE : {n} ?", f"cbv{n}", ROUGE, 70).draw(cv, 0, CX, 1720, 1, 4)
        page(cv, i + 1, N); out.append(cv)
    # 8) vote final
    cv = base(PSG_BG, 9)
    ransom_line(cv, "À TOI", 300, 190, seed=5)
    ransom_line(cv, "DE VOTER", 480, 150, seed=12)
    for k, (n, mn, who, club, *_r) in enumerate(BUTS):
        y = 720 + k*135
        big(str(n), f"cbf{n}", 80, NOIR, JAUNE).draw(cv, 0, 220, y, 1, -3)
        big(f"{who} {mn}", f"cbg{n}", 70, BLANC, ROUGE if club == "psg" else NOIR).draw(cv, 0, 600, y, 1, 2)
    big("LE CHIFFRE EN COMMENTAIRE", "cb8a", 66, NOIR, JAUNE).draw(cv, 0, CX, 1580, 1, -2)
    BTN_SUB.draw(cv, 0, CX, 1740, .8, -2)
    page(cv, 7, N); out.append(cv)
    return out

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "output", "carrousel_buts_city_psg")
    os.makedirs(out, exist_ok=True); paths = []
    for k, cv in enumerate(slides()):
        finish(cv, TITLE); p = os.path.join(out, f"slide_{k+1:02d}.png"); cv.convert("RGB").save(p); paths.append(p)
    print(paths)
