"""Carrousel TikTok (mode photo) « Toulouse FC en 7 dates » : 8 images 1080×1920, à poster juste avant la vidéo.
Même gabarit que episodes/liverpool/carrousel.py (accroche, une date par slide, question + CTA ; contenu entre y 180 et 1 420).
  python3 episodes/toulouse/carrousel.py output/toulouse/carrousel
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "engine"))
from toulouse import *
from quiz import like_button, sub_button
N = 8

def new(key, bg, rays_col=None, brick=False):
    cv = background(0, TITLE)
    if brick: bricks(cv, 0, key)
    else: stage_fill(cv, 0, bg, key)
    if rays_col: rays(cv, (CX, 1000), .3, .8, 16, 1500, rays_col, .12, 0)
    return cv

def swipe(cv, i, txt="GLISSE"):
    d = ImageDraw.Draw(cv); x, y = 690, 1490
    lab = Label(txt, f"tcsw{txt}", font("title", 54), PAL["ink"], GOLD, padx=26, pady=6, rough=3); lab.draw(cv, 0, x, y, 1, -3)
    ax = x + lab.v[0].width/2 + 8
    d.polygon([(ax, y - 32), (ax + 66, y), (ax, y + 32)], fill=GOLD, outline=NOIR)
    LBL(f"{i}/{N}", "tcn", font("title", 46), BLANC, NOIR, padx=16, pady=2, rough=2).draw(cv, 0, 150, y, 1, 2)

def save(cv, out, i):
    finish(cv, TITLE); p = os.path.join(out, f"slide_{i}.jpg"); cv.convert("RGB").save(p, quality=94); return p
def T(txt, key, bg=PAL["paper"], size=52): return TAG(txt, key, bg, PAL["ink"], size)
def big(txt, key, y, bg=PAL["ink"], fg=PAL["cream"], size=170, rot=-3, cv=None): kw(cv, 0, KW(txt, key, bg, fg, size), 9, 0, None, CX, y, rot)

def slide1(out):
    cv = new("tc1", None, brick=True)
    Label("TOULOUSE", "tcv1", font("title", 180), BLANC, VIO, padx=40, pady=6, rough=4, maxw=980).draw(cv, 0, CX, 330, 1, -3)
    Label("EN FAILLITE EN 2001…", "tcv2", font("title", 72), BLANC, NOIR, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 530, 1, 2)
    SH_TFC.draw(cv, 0, 290, 820, 1.2, -6); K1a.draw(cv, 0, 330, 860, .7, -14); SH_LIV.draw(cv, 0, 800, 820, 1.0, 6)
    score2(cv, 0, CX, 1080, "TOULOUSE", "LIVERPOOL", 3, 2, "", .8)
    Label("…ET IL BAT LIVERPOOL ?!", "tcv3", font("title", 72), PAL["ink"], GOLD, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 1320, 1, -2)
    swipe(cv, 1, "GLISSE : 7 DATES"); return save(cv, out, 1)

def slide2(out):
    cv = new("tc2", None, brick=True)
    big("1970", "tc2a", 340, cv=cv); T("un nouveau club naît à Toulouse", "tc2b", size=54).draw(cv, 0, CX, 520, 1, 2)
    SH_TFC70.draw(cv, 0, 300, 870, 1.25, -5); SH_TFC.draw(cv, 0, 780, 870, 1.25, 5)
    d = ImageDraw.Draw(cv); d.polygon([(470, 840), (590, 870), (470, 900)], fill=VIO, outline=NOIR)
    show_stamp(cv, 0, STAMP("1979 : TOULOUSE FC", "tc2c", VIO, 84), 9, 0, CX, 1180, -3)
    T("le « Téfécé »", "tc2d", GOLD, 58).draw(cv, 0, CX, 1340, 1, 2)
    swipe(cv, 2); return save(cv, out, 2)

def slide3(out):
    cv = new("tc3", (34, 32, 40)); d = ImageDraw.Draw(cv)
    for j in range(8): d.rectangle([0, j*260 + 40, W, j*260 + 56], fill=(70, 66, 80))
    big("2001", "tc3a", 340, cv=cv); show_stamp(cv, 0, STAMP("FAILLITE", "tc3b", RED, 120), 9, 0, CX, 540, -6)
    floor_panel(cv, 0, 290, 800, "D3", 9, True, 1.4, 1); floor_panel(cv, 0, 790, 800, "L1", 9, False, 1.4, 1)
    d.polygon([(450, 770), (570, 800), (450, 830)], fill=GOLD, outline=NOIR)
    HERO.draw(cv, 0, CX, 1300, .7, age=1, kit="toulouse", mood="cheer", arms=(150, 150), t=1)
    T("repart en 3e division… en L1 dès 2003", "tc3c", GOLD, 48).draw(cv, 0, CX, 1390, 1, -2)
    swipe(cv, 3); return save(cv, out, 3)

def slide4(out):
    cv = new("tc4", VIO, (140, 90, 180))
    big("2007", "tc4a", 340, cv=cv); show_stamp(cv, 0, STAMP("3e DE LIGUE 1", "tc4b", VIO_D, 100), 9, 0, CX, 530, 3)
    UCL.draw(cv, 0, CX, 790, 1.0, 0); T("1re Ligue des champions", "tc4c", GOLD, 54).draw(cv, 0, CX, 990, 1, -2)
    score2(cv, 0, CX, 1200, "TOULOUSE", "LIVERPOOL", 0, 5, "score cumulé", .75)
    T("éliminé par Liverpool", "tc4d", size=52).draw(cv, 0, CX, 1390, 1, 2)
    swipe(cv, 4); return save(cv, out, 4)

def slide5(out):
    cv = new("tc5", VIO_DD, (90, 50, 130))
    big("2020", "tc5a", 340, cv=cv); kw(cv, 0, K5b, 9, 0, None, CX, 520, -4)
    floor_panel(cv, 0, 290, 760, "L1", 9, True, 1.4, 1); floor_panel(cv, 0, 790, 760, "L2", 9, True, 1.4, 1)
    big("2022", "tc5b", 980, size=130, cv=cv); show_stamp(cv, 0, STAMP("CHAMPION DE LIGUE 2", "tc5c", VIO, 76), 9, 0, CX, 1140, 3)
    CUP.draw(cv, 0, CX, 1320, .9, 0)
    swipe(cv, 5); return save(cv, out, 5)

def slide6(out):
    cv = new("tc6", VIO_D, (130, 80, 170))
    big("2023", "tc6a", 340, cv=cv); show_stamp(cv, 0, STAMP("COUPE DE FRANCE", "tc6b", VIO, 96), 9, 0, CX, 530, 3)
    score2(cv, 0, CX, 790, "TOULOUSE", "NANTES", 5, 1, "finale", .85)
    CUP.draw(cv, 0, CX, 1110, 1.3, 0); show_stamp(cv, 0, STAMP("1er GRAND TROPHÉE", "tc6c", GOLD, 70), 9, 0, CX, 1350, -3)
    swipe(cv, 6); return save(cv, out, 6)

def slide7(out):
    cv = new("tc7", VIO_DD, (110, 60, 150))
    kw(cv, 0, KW("LIGUE EUROPA", "tc7a", PAL["ink"], PAL["cream"], 110), 9, 0, None, CX, 340, -3)
    T("9 novembre 2023", "tc7b", size=54).draw(cv, 0, CX, 500, 1, 2)
    SH_TFC.draw(cv, 0, 270, 760, 1.1, -4); SH_LIV.draw(cv, 0, 810, 760, 1.1, 4)
    score2(cv, 0, CX, 1040, "TOULOUSE", "LIVERPOOL", 3, 2, "", .85)
    show_stamp(cv, 0, STAMP("LA REVANCHE !", "tc7c", RED, 110), 9, 0, CX, 1270, -4)
    T("16 ans après 2007", "tc7d", GOLD, 52).draw(cv, 0, CX, 1400, 1, 2)
    swipe(cv, 7); return save(cv, out, 7)

def slide8(out):
    cv = new("tc8", VIO, (140, 90, 180))
    kw(cv, 0, K9a, 9, 0, None, CX, 330, -3); kw(cv, 0, K9b, 9, 0, None, CX, 470, 2)
    for k, lab in enumerate(WORDS9): lab.draw(cv, 0, (300, 780, 300, 780)[k], (680, 760, 880, 960)[k], 1, (-6, 5, 4, -5)[k])
    kw(cv, 0, KW("OUI OU NON ? COMMENTE !", "tc8a", RED, BLANC, 64), 9, 0, None, CX, 1120, -2)
    like_button(cv, 0, 190, 1290, .5, 5, 0); sub_button(cv, 0, 690, 1290, 5, 0, -9)
    T("la vidéo complète est sur le profil", "tc8b", GOLD, 46).draw(cv, 0, CX, 1485, 1, -2)
    return save(cv, out, 8)

def grille(out, files):
    ims = [Image.open(f).resize((270, 480)) for f in files]
    sheet = Image.new("RGB", (4*270 + 5*14, 2*480 + 3*14), (20, 20, 20))
    for k, im in enumerate(ims): sheet.paste(im, (14 + (k % 4)*(270 + 14), 14 + (k // 4)*(480 + 14)))
    p = os.path.join(out, "apercu_grille.jpg"); sheet.save(p, quality=90); return p

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "output", "toulouse", "carrousel")
    os.makedirs(out, exist_ok=True)
    print(grille(out, [f(out) for f in (slide1, slide2, slide3, slide4, slide5, slide6, slide7, slide8)]))
