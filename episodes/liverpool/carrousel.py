"""Carrousel TikTok (mode photo) « Liverpool en 7 dates » : 8 images 1080×1920, même style papier découpé que la vidéo.
Slide 1 = accroche (mêmes éléments que la vidéo : LIVERPOOL + facture de loyer), slides 2 à 7 = une date par image, slide 8 = question + CTA.
Zone sûre : rien d'important au-dessus de y≈180, à droite de x≈940, ni sous y≈1500 (légende TikTok).

  python3 episodes/liverpool/carrousel.py output/liverpool/carrousel
Écrit slide_1.jpg … slide_8.jpg + apercu_grille.jpg (planche de contrôle 4×2).
"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "engine"))
import liverpool as L
from liverpool import *
from quiz import like_button, sub_button

N = 8
def new(key, bg=None, stripes=False, rays_col=None):
    cv = background(0, TITLE); stage_fill(cv, 0, bg or CREME, key); d = ImageDraw.Draw(cv)
    if stripes:
        for k in range(-2, 12): d.polygon([(k*130 + 130, 0), (k*130 + 195, 0), (k*130 - 405, 1920), (k*130 - 470, 1920)], fill=(226, 214, 192))
    if rays_col: rays(cv, (CX, 1000), .3, .8, 16, 1500, rays_col, .12, 0)
    return cv

def swipe(cv, i, dark=False, txt="GLISSE"):
    """Pastille « GLISSE » + flèche (en bas, hors de la colonne d'icônes TikTok) et numéro de la slide. Le contenu s'arrête à y≈1420."""
    d = ImageDraw.Draw(cv); x, y = 690, 1490
    Label(txt, f"cwsw{dark}{txt}", font("title", 54), BLANC if not dark else NOIR, RED if not dark else GOLD, padx=26, pady=6, rough=3).draw(cv, 0, x, y, 1, -3)
    ax = x + Label(txt, f"cwsw{dark}{txt}", font("title", 54), BLANC, RED, padx=26, pady=6).v[0].width/2 + 8
    d.polygon([(ax, y - 32), (ax + 66, y), (ax, y + 32)], fill=RED if dark else GOLD, outline=NOIR)
    LBL(f"{i}/{N}", "cwn", font("title", 46), BLANC, NOIR, padx=16, pady=2, rough=2).draw(cv, 0, 150, y, 1, 2)

def save(cv, out, i):
    finish(cv, TITLE); p = os.path.join(out, f"slide_{i}.jpg"); cv.convert("RGB").save(p, quality=94); return p

def slide1(out):
    cv = new("cw1", stripes=True)
    Label("LIVERPOOL", "cw1a", font("title", 190), BLANC, RED, padx=40, pady=6, rough=4, maxw=980).draw(cv, 0, CX, 330, 1, -3)
    Label("NÉ D'UNE DISPUTE DE LOYER…", "cw1b", font("title", 62), BLANC, NOIR, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 530, 1, 2)
    FACTURE.draw(cv, 0, CX - 40, 860, .8, -5); STAMP_IMP.draw(cv, 0, 780, 1040, .65, 14)
    Label("…6 FOIS CHAMPION D'EUROPE ?!", "cw1c", font("title", 62), PAL["ink"], GOLD, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 1190, 1, -2)
    for k in range(6): UCL.draw(cv, 0, 170 + k*148, 1330, .46, (-5, 4, -3, 5, -4, 3)[k])
    swipe(cv, 1, txt="GLISSE : 7 DATES")
    return save(cv, out, 1)

def slide2(out):
    cv = new("cw2", (176, 206, 232))
    kw(cv, 0, KW("1892", "cw2a", PAL["ink"], size=190), 9, 0, None, CX, 340, -3)
    show_stamp(cv, 0, STAMP("EVERTON QUITTE ANFIELD", "cw2b", BLEU, 70), 9, 0, CX, 520, 3)
    SH_EVE.draw(cv, 0, 190, 760, .8, -8)
    ANFIELD.draw(cv, 0, CX, 1030, 1.15, 0)
    SH_LIV.draw(cv, 0, CX, 780, 1.25, -4)
    HOUL.draw(cv, 0, 910, 1250, .5, age=1, kit="suit", beard=True, mood="happy", t=1)
    TAG("le loyer passe de 100 £ à 250 £", "cw2c", PAL["paper"], PAL["ink"], 52).draw(cv, 0, CX, 1310, 1, -2)
    TAG("le propriétaire crée Liverpool", "cw2d", GOLD, PAL["ink"], 52).draw(cv, 0, CX, 1390, 1, 2)
    swipe(cv, 2, True)
    return save(cv, out, 2)

def slide3(out):
    cv = new("cw3", (34, 32, 40), rays_col=None); d = ImageDraw.Draw(cv)
    for j in range(8): d.rectangle([0, j*260 + 40, W, j*260 + 56], fill=(70, 66, 80))
    kw(cv, 0, KW("1959", "cw3a", PAL["ink"], size=190), 9, 0, None, CX, 340, -3)
    show_stamp(cv, 0, STAMP("BILL SHANKLY ARRIVE", "cw3b", RED, 80), 9, 0, CX, 540, 3)
    floor_panel(cv, 0, 290, 720, "D2", 9, False, 1.4, 1); floor_panel(cv, 0, 790, 720, "D1", 9, False, 1.4, 1)
    d.polygon([(450, 690), (570, 720), (450, 750)], fill=GOLD, outline=NOIR)
    SHANK.draw(cv, 0, CX, 1330, .75, age=1, kit="suit", mood="cheer", arms=(150, 150), t=1)
    TAG("D2 en 1954, retour en D1 en 1962", "cw3c", GOLD, PAL["ink"], 52).draw(cv, 0, CX, 1390, 1, -2)
    swipe(cv, 3)
    return save(cv, out, 3)

def slide4(out):
    cv = new("cw4", RED_DD, rays_col=(150, 30, 40))
    kw(cv, 0, KW("4 COUPES D'EUROPE", "cw4a", GOLD, PAL["ink"], 84), 9, 0, None, CX, 330, -3)
    kw(cv, 0, KW("EN 8 ANS", "cw4b", PAL["ink"], size=130), 9, 0, None, CX, 480, 2)
    for k in range(4):
        x = 290 + (k % 2)*500; y = 740 + (k // 2)*390
        UCL.draw(cv, 0, x, y, .95, (-6, 6, 5, -5)[k]); L.YEARS4[k].draw(cv, 0, x, y + 160, 1, (4, -4, -3, 4)[k])
    TAG("Anfield chante You'll Never Walk Alone", "cw4c", PAL["paper"], PAL["ink"], 50).draw(cv, 0, CX, 1380, 1, -2)
    swipe(cv, 4)
    return save(cv, out, 4)

def slide5(out):
    cv = new("cw5", (24, 26, 34), rays_col=(60, 60, 90))
    kw(cv, 0, KW("2005 : ISTANBUL", "cw5a", PAL["ink"], size=110), 9, 0, None, CX, 330, -3)
    score2(cv, 0, CX, 620, "MILAN", "LIVERPOOL", 3, 0, "mi-temps", .8)
    LBL("EN 6 MINUTES", "cw5b", font("title", 62), PAL["ink"], GOLD, padx=26, pady=6, rough=3).draw(cv, 0, CX, 820, 1, -3)
    score2(cv, 0, CX, 1010, "MILAN", "LIVERPOOL", 3, 3, "", .8)
    show_stamp(cv, 0, STAMP("AUX TIRS AU BUT !", "cw5c", RED, 82), 9, 0, CX, 1230, -3)
    UCL.draw(cv, 0, 170, 1350, .42, -6); UCL.draw(cv, 0, 910, 1350, .42, 6)
    swipe(cv, 5)
    return save(cv, out, 5)

def slide6(out):
    cv = new("cw6", (18, 22, 52), rays_col=(60, 80, 150))
    kw(cv, 0, KW("2019 : MADRID", "cw6a", PAL["ink"], size=100), 9, 0, None, CX, 330, -3)
    UCL.draw(cv, 0, 270, 640, 1.2, -5)
    show_stamp(cv, 0, STAMP("6e LIGUE DES CHAMPIONS", "cw6b", RED, 56), 9, 0, 690, 560, 4)
    kw(cv, 0, KW("2020", "cw6c", PAL["ink"], size=130), 9, 0, None, CX, 940, -3)
    CUP.draw(cv, 0, 270, 1210, 1.2, 5)
    show_stamp(cv, 0, STAMP("1er TITRE EN 30 ANS", "cw6d", RED, 60), 9, 0, 690, 1150, -4)
    TAG("depuis 1990, avec Klopp", "cw6e", GOLD, PAL["ink"], 50).draw(cv, 0, 690, 1290, 1, 2)
    swipe(cv, 6)
    return save(cv, out, 6)

def slide7(out):
    cv = new("cw7", RED_DD, rays_col=(180, 30, 50))
    kw(cv, 0, KW("2025", "cw7a", PAL["ink"], size=170), 9, 0, None, CX, 330, -3)
    show_stamp(cv, 0, STAMP("20e TITRE", "cw7b", RED, 120), 9, 0, CX, 520, 3)
    L.L20.draw(cv, 0, 300, 860, 1, -4)
    LBL("=", "cw7e", font("title", 190), GOLD, None, stroke=8, stroke_fill=NOIR).draw(cv, 0, CX, 860, 1, 0)
    SH_MU.draw(cv, 0, 780, 860, 1.0, 4)
    show_stamp(cv, 0, STAMP("RECORD ÉGALÉ", "cw7c", GOLD, 80), 9, 0, CX, 1130, -3)
    TAG("2026 : Slot remercié, Iraola arrive", "cw7d", PAL["paper"], PAL["ink"], 52).draw(cv, 0, CX, 1290, 1, 2)
    swipe(cv, 7)
    return save(cv, out, 7)

def slide8(out):
    cv = new("cw8", (30, 16, 24), rays_col=(110, 20, 40))
    kw(cv, 0, KW("LE PLUS GRAND CLUB", "cw8a", PAL["paper"], PAL["ink"], 76), 9, 0, None, CX, 310, -3)
    kw(cv, 0, KW("D'ANGLETERRE ?", "cw8b", GOLD, PAL["ink"], 76), 9, 0, None, CX, 440, 2)
    SH_LIV.draw(cv, 0, 270, 760, 1.35, -4); SH_MU.draw(cv, 0, 810, 760, 1.35, 4); VS.draw(cv, 0, CX, 760, 1, 0)
    LBL("20 TITRES", "cw8c", font("title", 56), BLANC, RED, padx=20, pady=4, rough=3).draw(cv, 0, 270, 990, 1, -3)
    LBL("20 TITRES", "cw8d", font("title", 56), BLANC, (170, 20, 30), padx=20, pady=4, rough=3).draw(cv, 0, 810, 990, 1, 3)
    kw(cv, 0, KW("COMMENTE : LFC OU MU ?", "cw8e", RED, BLANC, 66), 9, 0, None, CX, 1130, -2)
    like_button(cv, 0, 190, 1290, .5, 5, 0); sub_button(cv, 0, 690, 1290, 5, 0, -9)
    TAG("enregistre et partage à un pote de Man United", "cw8f", GOLD, PAL["ink"], 44).draw(cv, 0, CX, 1485, 1, -2)
    return save(cv, out, 8)

def grille(out, files):
    from PIL import Image
    ims = [Image.open(f).resize((270, 480)) for f in files]
    sheet = Image.new("RGB", (4*270 + 5*14, 2*480 + 3*14), (20, 20, 20))
    for k, im in enumerate(ims): sheet.paste(im, (14 + (k % 4)*(270 + 14), 14 + (k // 4)*(480 + 14)))
    p = os.path.join(out, "apercu_grille.jpg"); sheet.save(p, quality=90); return p

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "output", "liverpool", "carrousel")
    os.makedirs(out, exist_ok=True)
    files = [f(out) for f in (slide1, slide2, slide3, slide4, slide5, slide6, slide7, slide8)]
    print(grille(out, files))
