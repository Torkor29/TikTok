"""Épisode « Légendes du foot » #10 : l'histoire du Toulouse FC, format court (~1 min), CTA « like + abonne-toi pour plus d'épisodes ».
« TOULOUSE » dès la 1re image : en faillite en 2001… et 22 ans plus tard, il bat Liverpool (clin d'œil à l'épisode #9).
1970 nouveau club, 1979 Toulouse FC ; 2001 faillite, National, L1 dès 2003 ; 2007 3e de L1, Liverpool élimine le TFC (0-5 cumulé) ;
2020 dernier, L2, 2022 champion de L2 ; pause like + abonne-toi ; 2023 Coupe de France 5-1 contre Nantes ; 9 nov 2023 TFC 3-2 Liverpool ;
fin : « le club le plus sous-coté de France ? ».

  python3 episodes/toulouse/toulouse.py output/toulouse --stills [3,4]
  python3 episodes/toulouse/toulouse.py output/toulouse --cover
  python3 episodes/toulouse/toulouse.py output/toulouse
Voix en attente (crédits ElevenLabs) : LEGENDES_PROVISOIRE=<dossier> … --apercu (voir scripts/minutage_provisoire.py).
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "liverpool"))
from story import *
from quiz import like_button, sub_button
_prov = os.environ.pop("LEGENDES_PROVISOIRE", None)   # liverpool.py lit cette variable pour ses propres voix
from liverpool import score2, trophy_lift, shaft, stopwatch, stadium, _shield, SH_LIV
if _prov: os.environ["LEGENDES_PROVISOIRE"] = _prov
import engine

TITLE = "~/légendes $ ./toulouse"
SLUG = "toulouse_legende"
SRC = os.environ.get("LEGENDES_PROVISOIRE") or HERE
VOICE = [os.path.join(SRC, "voix", f"scene_{i}.mp3") for i in range(1, 10)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
ALIGN = os.path.join(SRC, "alignement.json")
PAD = 0.12
WS, TEXTS = load_words(ALIGN)
def w(i, word, n=1, end=False):
    return PAD + WS[i-1](word, n, end)

VIO = (98, 46, 140); VIO_D = (58, 24, 86); VIO_DD = (32, 14, 48); ROSE = (226, 150, 132); ROSE_C = (240, 206, 192)
BLANC = (250, 250, 246); GOLD = (236, 186, 48); NOIR = (30, 28, 28); RED = (200, 16, 46); CREME = (236, 228, 210); NUIT = (22, 16, 36)

HERO = Player("tfc10", hair=(60, 44, 34), skin=(230, 186, 150))
HERO2 = Player("tfc10b", hair=(24, 20, 18), skin=(140, 96, 70))
LFC = Player("lfc10", hair=(40, 30, 24), skin=(206, 160, 124))
NAN = Player("nan10", hair=(150, 110, 60), skin=(230, 186, 150))
SH_TFC = _shield("tsh", VIO, VIO_D, "TFC", 80)
SH_TFC70 = _shield("tsh70", VIO, VIO_D, "1970", 66)

def bricks(cv, fr, key):
    """Fond « ville rose » : mur de briques roses."""
    stage_fill(cv, fr, ROSE, key); d = ImageDraw.Draw(cv)
    for r in range(0, 1920, 64):
        off = 0 if (r // 64) % 2 else 60
        for x in range(-120 + off, 1080, 120):
            d.rectangle([x + 4, r + 4, x + 116, r + 60], outline=(196, 118, 104), width=3)

# ------------------------------------------------------------------ labels
K1a = STAMP("FAILLITE", "tk1a", RED, 150); T1a = TAG("en 2001", "tt1a", PAL["paper"], size=60)
K1b = KW("22 ANS PLUS TARD…", "tk1b", PAL["ink"], size=92); K1c = STAMP("L'HISTOIRE DU TFC", "tk1c", VIO, 96); K1d = KW("EN 1 MINUTE", "tk1d", RED, size=110)
K2a = KW("1970", "tk2a", PAL["ink"], size=170); T2a = TAG("un nouveau club à Toulouse", "tt2a", PAL["paper"], size=56)
K2b = KW("1979", "tk2b", PAL["ink"], size=150); K2c = STAMP("TOULOUSE FC", "tk2c", VIO, 110); T2b = TAG("le Téfécé !", "tt2b", GOLD, size=62)
K3a = KW("2001", "tk3a", PAL["ink"], size=170); K3c = KW("3e DIVISION", "tk3c", RED, size=110); K3d = KW("2003", "tk3d", PAL["ink"], size=150); T3a = TAG("déjà de retour en Ligue 1 !", "tt3a", PAL["paper"], size=54)
K4a = KW("2007", "tk4a", PAL["ink"], size=170); K4b = STAMP("3e DE LIGUE 1", "tk4b", VIO, 100); T4a = TAG("1re Ligue des champions !", "tt4a", GOLD, size=56)
K4c = KW("ÉLIMINÉ PAR LIVERPOOL", "tk4c", PAL["ink"], size=76); T4b = TAG("0-5 sur les deux matchs", "tt4b", PAL["paper"], size=54)
K5a = KW("2020", "tk5a", PAL["ink"], size=170); K5b = KW("DERNIER", "tk5b", RED, size=130)
K5c = KW("2022", "tk5c", PAL["ink"], size=170); K5d = STAMP("CHAMPION DE LIGUE 2", "tk5d", VIO, 84)
K6a = KW("PETITE PAUSE !", "tk6a", PAL["paper"], PAL["ink"], 84); T6a = TAG("si tu kiffes…", "tt6a", PAL["paper"], size=56)
K6b = KW("LÂCHE UN LIKE", "tk6b", PAL["paper"], PAL["ink"], 76); T6b = TAG("pour plus d'épisodes !", "tt6b", PAL["paper"], size=56)
K6c = KW("ON REPREND !", "tk6c", PAL["paper"], PAL["ink"], 84)
K7a = KW("2023", "tk7a", PAL["ink"], size=170); K7b = STAMP("FINALE DE LA COUPE DE FRANCE", "tk7b", VIO, 64)
K7c = KW("5 - 1 !", "tk7c", RED, size=200); K7d = STAMP("1er GRAND TROPHÉE", "tk7d", GOLD, 84)
K8a = KW("LIGUE EUROPA", "tk8a", PAL["ink"], size=110); T8a = TAG("9 novembre 2023", "tt8a", PAL["paper"], size=54)
K8b = STAMP("LA REVANCHE !", "tk8b", RED, 120); T8b = TAG("16 ans après 2007", "tt8b", GOLD, size=58)
K9a = KW("LE CLUB LE PLUS", "tk9a", PAL["paper"], PAL["ink"], 84); K9b = KW("SOUS-COTÉ DE FRANCE ?", "tk9b", GOLD, PAL["ink"], 76)
WORDS9 = [Label(x, "tw9"+x, font("title", 70), BLANC if k % 2 else PAL["ink"], (VIO if k % 2 else GOLD), padx=24, pady=6, rough=3)
          for k, x in enumerate(("FAILLITE", "LIGUE 2", "LA COUPE", "LIVERPOOL"))]
K9c = KW("COMMENTE !", "tk9c", RED, size=100); K9d = KW("+ D'ÉPISODES", "tk9d", PAL["ink"], size=84)

# ------------------------------------------------------------------ SCÈNE 1 — faillite en 2001… 22 ans plus tard il bat Liverpool
def s1a(cv, fr, t):
    bricks(cv, fr, "ts1a")
    Label("TOULOUSE", "ts1t", font("title", 180), BLANC, VIO, padx=36, pady=6, rough=4, maxw=1000).draw(cv, fr, CX, 360, lerp(1.2, 1.0, ease_out_cubic(prog(t, 0, .25))), -3)
    tf = w(1, "faillite")
    SH_TFC.draw(cv, fr, CX, 1020, 1.9, -3)
    HERO.draw(cv, fr, 830, 1780, .9, age=1, kit="toulouse", mood="sad" if t > tf else "happy", t=t)
    show_stamp(cv, fr, K1a, t, tf - .05, CX, 1050, -12)
    show(cv, fr, T1a, t, w(1, "deux") - .05, None, CX, 620, 2)

def s1b(cv, fr, t):
    stage_fill(cv, fr, VIO_DD, "ts1b"); rays(cv, (CX, 1000), t, 1.0, 16, 1500, (90, 50, 130))
    kw(cv, fr, K1b, t, w(1, "vingt-deux") - .1, None, CX, 420, -3)
    tb = w(1, "bat") - .05
    score2(cv, fr, CX, 820, "TOULOUSE", "LIVERPOOL", 3, 2, "Ligue Europa", .9*pop_in(t, tb, .3))
    if t > tb:
        HERO.draw(cv, fr, 300, 1780, .85, age=1, kit="toulouse", mood="cheer", arms=(150, 150), t=t)
        LFC.draw(cv, fr, 800, 1780, .85, age=1, kit="liverpool", mood="sad", t=t, look=(0, 1))
        confetti(cv, fr, "tc1", t - tb, 80, 3, [VIO, BLANC, GOLD])

def s1c(cv, fr, t):
    stage_fill(cv, fr, VIO, "ts1c"); d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    d.rectangle([CX - 150, sy0, CX + 150, sy1], fill=BLANC); d.rectangle([CX - 110, sy0, CX + 110, sy1], fill=VIO_D)
    t0 = w(1, "L'histoire") - .1
    for P, x, k in ((HERO2, 220, 0), (HERO, 860, 1)):
        P.draw(cv, fr, x, 1780 - 60*abs(math.sin(t*6 + k)), .82, age=1, kit="toulouse", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
    show_stamp(cv, fr, K1c, t, t0 + .05, CX, 420, -4)
    kw(cv, fr, K1d, t, w(1, "minute") - .1, None, CX, 600, 3)
    stopwatch(cv, CX, 900, 1.1, prog(t, t0, 1.2))

def s1(cv, fr, t, T):
    shots(cv, fr, t, [(0, s1a), (w(1, "vingt-deux") - .15, s1b), (w(1, "L'histoire") - .1, s1c)], d=.24)
    impact(cv, t, .02, 18); impact(cv, t, w(1, "faillite"), 24); flashes(cv, t, w(1, "faillite"), .1, .5)
    impact(cv, t, w(1, "bat"), 18); punch(cv, t, w(1, "L'histoire") - .1, 1.1); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 2 — 1970, 1979 : Toulouse FC, le Téfécé
def s2a(cv, fr, t):
    bricks(cv, fr, "ts2a")
    kw(cv, fr, K2a, t, w(2, "Mille") - .05, None, CX, 420, -3)
    show(cv, fr, T2a, t, w(2, "nouveau") - .05, None, CX, 600, 2)
    SH_TFC70.draw(cv, fr, CX, 1080, 1.7*slam(t, w(2, "un") - .05, .22), -3)
    particles(cv, fr, "tp2", (CX, 1080), prog(t, w(2, "naît"), .6), 18, 300, [VIO, BLANC, GOLD], 16)

def s2b(cv, fr, t):
    stage_fill(cv, fr, VIO_D, "ts2b"); rays(cv, (CX, 1050), t, .8, 16, 1500, (120, 70, 160))
    kw(cv, fr, K2b, t, w(2, "soixante-dix-neuf") - .1, None, CX, 400, -3)
    show_stamp(cv, fr, K2c, t, w(2, "Toulouse", 2) - .05, CX, 600, 4)
    SH_TFC.draw(cv, fr, CX, 1060, 1.6*slam(t, w(2, "Toulouse", 2), .22), 3)
    show(cv, fr, T2b, t, w(2, "Téfécé") - .05, None, CX, 1380, -3)
    HERO.draw(cv, fr, CX, 1840, .55, age=1, kit="toulouse", mood="cheer", arms=(150, 150), t=t)

def s2(cv, fr, t, T):
    shots(cv, fr, t, [(0, s2a), (w(2, "En") - .1, s2b)], d=.24)
    impact(cv, t, w(2, "naît"), 16); impact(cv, t, w(2, "Toulouse", 2), 16); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 3 — 2001 faillite, National, L1 dès 2003
def s3a(cv, fr, t):
    tf = w(3, "faillite"); tr = w(3, "redémarre")
    stage_fill(cv, fr, VIO_D, "ts3a")
    HERO.draw(cv, fr, CX, 1740, 1.05, age=1, kit="toulouse", mood="surprised" if t < tf else "sad", t=t)
    floor_panel(cv, fr, CX, 660, "L2", t, True, 1.6, 1)
    kw(cv, fr, K3a, t, .03, None, CX, 400, -3)
    show_stamp(cv, fr, K1a, t, tf - .05, CX, 1000, -10)
    elevator_drop(cv, t, tr, w(3, "division") - tr)
    if t > w(3, "division"):
        shaft(cv, fr, t, 0, "ts3shaft")
        HERO.draw(cv, fr, CX, 1740, 1.05, age=1, kit="toulouse", mood="sad", t=t, look=(0, 1))
        floor_panel(cv, fr, CX, 660, "D3", t, True, 1.8, 1)
        kw(cv, fr, K3c, t, w(3, "division"), None, CX, 960, 3)

def s3b(cv, fr, t):
    t0 = w(3, "remonte") - .1; tq = w(3, "trois", 2)
    if t < tq + .2:
        shaft(cv, fr, t, 900 + 2200*prog(t, t0, tq + .2 - t0))
        lab = ("D3", "L2", "L1")[min(2, int(prog(t, t0 + .1, tq - t0)*2.99))]
        floor_panel(cv, fr, CX, 640, lab, t, False, 1.8, 1)
        HERO.draw(cv, fr, CX, 1740, 1.05, age=1, kit="toulouse", mood="surprised", arms=(40, 40), t=t)
    else:
        stage_fill(cv, fr, VIO_DD, "ts3c"); rays(cv, (CX, 1000), t, .8, 16, 1500, (90, 50, 130))
        floor_panel(cv, fr, CX, 760, "L1", t, False, 1.8, 1)
        HERO.draw(cv, fr, CX, 1780, .9, age=1, kit="toulouse", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
        show(cv, fr, T3a, t, tq + .1, None, CX, 1000, 2)
    kw(cv, fr, K3d, t, tq - .05, None, CX, 420, -3)

def s3(cv, fr, t, T):
    shots(cv, fr, t, [(0, s3a), (w(3, "remonte") - .1, s3b)], d=.24)
    impact(cv, t, w(3, "faillite"), 22); impact(cv, t, w(3, "division") + .02, 22); impact(cv, t, w(3, "trois", 2), 14); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 4 — 2007 : 3e, la C1… Liverpool élimine le TFC
def s4a(cv, fr, t):
    stage_fill(cv, fr, VIO, "ts4a"); rays(cv, (CX, 1100), t, .7, 16, 1500, (140, 90, 180), .12, .15)
    kw(cv, fr, K4a, t, .03, None, CX, 400, -3)
    show_stamp(cv, fr, K4b, t, w(4, "troisième") - .05, CX, 600, 4)
    UCL.draw(cv, fr, CX, 1100, 1.4*slam(t, w(4, "première") - .1, .22), 0)
    show(cv, fr, T4a, t, w(4, "première") - .05, None, CX, 1420, -2)
    HERO.draw(cv, fr, CX, 1840, .55, age=1, kit="toulouse", mood="cheer", arms=(150, 150), t=t)

def s4b(cv, fr, t):
    stage_fill(cv, fr, (24, 26, 34), "ts4b")
    tl = w(4, "Liverpool")
    kw(cv, fr, K4c, t, tl - .05, None, CX, 420, -3)
    score2(cv, fr, CX, 780, "TOULOUSE", "LIVERPOOL", 0, 5, "score cumulé", .9*pop_in(t, w(4, "cinq") - .1, .3))
    HERO.draw(cv, fr, 300, 1780, .85, age=1, kit="toulouse", mood="sad", t=t, look=(0, 1))
    LFC.draw(cv, fr, 800, 1780, .85, age=1, kit="liverpool", mood="cheer", arms=(150, 150), t=t)
    show(cv, fr, T4b, t, w(4, "cinq") + .1, None, CX, 1060, 2)
    if t > w(4, "cinq"): glitch(cv, fr, t, w(4, "cinq"), .3, 14)

def s4(cv, fr, t, T):
    shots(cv, fr, t, [(0, s4a), (w(4, "mais") - .1, s4b)], d=.24)
    impact(cv, t, w(4, "troisième"), 16); impact(cv, t, w(4, "cinq"), 22); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 5 — 2020 dernier, L2… 2022 champion
def s5a(cv, fr, t):
    td = w(5, "dernier"); tr = w(5, "retour")
    stage_fill(cv, fr, VIO_D, "ts5a")
    HERO.draw(cv, fr, CX, 1740, 1.05, age=1, kit="toulouse", mood="sad" if t > td else "normal", t=t)
    floor_panel(cv, fr, CX, 660, "L1", t, True, 1.6, 1)
    kw(cv, fr, K5a, t, .03, None, CX, 400, -3)
    kw(cv, fr, K5b, t, td - .05, None, CX, 960, -4)
    elevator_drop(cv, t, tr - .1, .6)
    if t > tr + .5:
        shaft(cv, fr, t, 0, "ts5shaft")
        HERO.draw(cv, fr, CX, 1740, 1.05, age=1, kit="toulouse", mood="sad", t=t, look=(0, 1))
        floor_panel(cv, fr, CX, 660, "L2", t, True, 1.8, 1)

def s5b(cv, fr, t):
    stage_fill(cv, fr, VIO_DD, "ts5b"); rays(cv, (CX, 1000), t, .9, 16, 1500, (90, 50, 130))
    kw(cv, fr, K5c, t, w(5, "deux", 2) - .1, None, CX, 400, -3)
    show_stamp(cv, fr, K5d, t, w(5, "champion") - .05, CX, 600, 4)
    trophy_lift(cv, fr, HERO, CX, 1780, .85, "toulouse", t, CUP)
    confetti(cv, fr, "tc5", t - w(5, "champion"), 80, 3, [VIO, BLANC, GOLD])

def s5(cv, fr, t, T):
    shots(cv, fr, t, [(0, s5a), (w(5, "Mais") - .1, s5b)], d=.24)
    impact(cv, t, w(5, "dernier"), 18); impact(cv, t, w(5, "champion"), 20); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 6 — PAUSE : like + abonne-toi
def s6(cv, fr, t, T):
    stage_fill(cv, fr, VIO_DD, "ts6"); rays(cv, (CX, 1050), t, .5, 14, 1400, (110, 50, 150))
    kw(cv, fr, K6a, t, .05, None, 760, 300, 4)
    tk, tl, ta = w(6, "kiffes"), w(6, "like"), w(6, "abonne-toi")
    show(cv, fr, T6a, t, tk - .15, None, 760, 470, -3)
    like_button(cv, fr, CX, 1010, .9*pop_in(t, tk, .3), t, tl)
    kw(cv, fr, K6b, t, tl - .05, None, 750, 650, 3)
    if t > ta - .1:
        sub_button(cv, fr, CX, 1370, t, ta - .1, ta + .25)
        show(cv, fr, T6b, t, w(6, "d'épisodes") - .1, None, CX, 1500, 2)
    kw(cv, fr, K6c, t, w(6, "Allez"), None, 760, 470, -5)
    impact(cv, t, tl, 14); impact(cv, t, w(6, "Allez"), 14)

def s6_post(cv, fr, t, T):
    a = pop_in(t, .25)
    if a > 0:
        d = ImageDraw.Draw(cv); cx, cy, s = 250, 470, a
        d.ellipse([cx-70*s, cy-70*s, cx+70*s, cy+70*s], fill=(34, 32, 36))
        for dx in (-22, 22): d.rectangle([cx+dx*s-12*s, cy-34*s, cx+dx*s+12*s, cy+34*s], fill=(250, 248, 240))
    chrono_bar(cv, fr, SCENES)

# ------------------------------------------------------------------ SCÈNE 7 — 2023 : Coupe de France, 5-1 contre Nantes
def s7a(cv, fr, t):
    stadium(cv, fr, "ts7stad", t, horizon=1180, sky=NUIT, pal=[VIO, BLANC, VIO_D, (250, 206, 30), (0, 120, 70), (200, 196, 190)])
    kw(cv, fr, K7a, t, .03, None, CX, 420, -3)
    show_stamp(cv, fr, K7b, t, w(7, "finale") - .05, CX, 620, 3)

def s7b(cv, fr, t):
    stage_fill(cv, fr, VIO_D, "ts7b"); rays(cv, (CX, 1000), t, .9, 16, 1500, (130, 80, 170))
    te = w(7, "écrase")
    score2(cv, fr, CX, 640, "TOULOUSE", "NANTES", 5, 1, "finale 2023", .85)
    kw(cv, fr, K7c, t, w(7, "cinq") - .05, None, CX, 940, -4)
    for k, x in enumerate((240, 840)): NAN.draw(cv, fr, x, 1780, .6, age=1, kit="nantes", mood="sad", t=t, look=(0, 1))
    HERO.draw(cv, fr, CX, 1780, .8, age=1, kit="toulouse", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
    if t > te: camera_flashes(cv, fr, "tf7", t - te, 1.2, 8)

def s7c(cv, fr, t):
    stage_fill(cv, fr, VIO_DD, "ts7c"); rays(cv, (CX, 1000), t, 1.0, 16, 1500, (230, 190, 80))
    tp = w(7, "premier") - .1
    show_stamp(cv, fr, K7d, t, tp, CX, 440, -4)
    trophy_lift(cv, fr, HERO, CX, 1780, .9, "toulouse", t, CUP)
    confetti(cv, fr, "tc7", t - tp, 90, 3, [VIO, BLANC, GOLD])

def s7(cv, fr, t, T):
    shots(cv, fr, t, [(0, s7a), (w(7, "Toulouse") - .1, s7b), (w(7, "Le") - .1, s7c)], d=.24)
    impact(cv, t, w(7, "cinq"), 22); flashes(cv, t, w(7, "cinq"), .1, .5); impact(cv, t, w(7, "premier"), 14); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 8 — Ligue Europa : TFC 3-2 Liverpool, la revanche
def s8a(cv, fr, t):
    stadium(cv, fr, "ts8stad", t, horizon=1180, sky=NUIT, pal=[VIO, BLANC, VIO_D, (200, 196, 190), (160, 120, 200)])
    kw(cv, fr, K8a, t, w(8, "Ligue") - .1, None, CX, 420, -3)
    show(cv, fr, T8a, t, w(8, "quelques"), None, CX, 600, 2)
    SH_TFC.draw(cv, fr, 270, 950, 1.2*pop_in(t, w(8, "bat") - .2, .3), -4); SH_LIV.draw(cv, fr, 810, 950, 1.2*pop_in(t, w(8, "Liverpool") - .2, .3), 4)

def s8b(cv, fr, t):
    stage_fill(cv, fr, VIO_DD, "ts8b"); rays(cv, (CX, 1000), t, 1.0, 16, 1500, (110, 60, 150))
    tt = w(8, "trois") - .1
    g = 1 if t < tt + .25 else (2 if t < tt + .5 else 3)
    score2(cv, fr, CX, 620, "TOULOUSE", "LIVERPOOL", g, 2, "9 nov. 2023", .9)
    HERO.draw(cv, fr, 300, 1780, .85, age=1, kit="toulouse", mood="cheer", arms=(150, 150), t=t)
    LFC.draw(cv, fr, 800, 1780, .85, age=1, kit="liverpool", mood="sad", t=t, look=(0, 1))
    if t > w(8, "Seize") - .1:
        show_stamp(cv, fr, K8b, t, w(8, "revanche") - .1, CX, 900, -4)
        show(cv, fr, T8b, t, w(8, "Seize") - .05, None, CX, 1060, 2)
        confetti(cv, fr, "tc8", t - w(8, "revanche"), 90, 3, [VIO, BLANC, GOLD])

def s8(cv, fr, t, T):
    shots(cv, fr, t, [(0, s8a), (w(8, "trois") - .25, s8b)], d=.24)
    impact(cv, t, w(8, "Liverpool"), 14); impact(cv, t, w(8, "trois") + .5, 20); impact(cv, t, w(8, "revanche"), 18); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 9 — bilan, « le plus sous-coté de France ? », like + abonne-toi
def s9a(cv, fr, t):
    bricks(cv, fr, "ts9a")
    keys = ("Faillite", "Ligue", "Coupe", "Liverpool")
    for k, lab in enumerate(WORDS9):
        tk = w(9, keys[k]) - .05
        show_stamp(cv, fr, lab, t, tk, (300, 780, 300, 780)[k], (520, 700, 880, 1060)[k], (-6, 5, 4, -5)[k])
    SH_TFC.draw(cv, fr, CX, 1380, 1.2*pop_in(t, w(9, "Liverpool"), .3), -3)

def s9b(cv, fr, t):
    stage_fill(cv, fr, VIO, "ts9b"); rays(cv, (CX, 1000), t, .6, 16, 1500, (140, 90, 180))
    tl, ta = w(9, "like"), w(9, "abonne-toi")
    kw(cv, fr, K9a, t, w(9, "Toulouse") - .05, None, CX, 360, -3)
    kw(cv, fr, K9b, t, w(9, "sous-coté") - .1, None, CX, 500, 2)
    sb = 1.5*pop_in(t, w(9, "Toulouse") + .15, .3)*(1 - prog(t, w(9, "Dis-le") - .25, .2))   # l'écusson occupe le centre pendant la question
    if sb > .02: SH_TFC.draw(cv, fr, CX, 1050, sb, -3 + 2*math.sin(t*3))
    kw(cv, fr, K9c, t, w(9, "Dis-le") - .05, None, CX, 760, -3)
    like_button(cv, fr, CX, 1000, .75*pop_in(t, tl - .1, .3), t, tl)      # empilés au centre : rien sous la colonne de boutons TikTok (x > 940)
    sub_button(cv, fr, CX, 1255, t, ta - .1, ta + .25)
    kw(cv, fr, K9d, t, w(9, "d'épisodes") - .1, None, CX, 1435, 3)
    confetti(cv, fr, "tc9", t - ta, 90, 5, [BLANC, GOLD, VIO_D])

def s9(cv, fr, t, T):
    shots(cv, fr, t, [(0, s9a), (w(9, "Toulouse") - .1, s9b)], d=.24)
    for k in ("Faillite", "Ligue", "Coupe", "Liverpool"): impact(cv, t, w(9, k), 10)
    impact(cv, t, w(9, "like"), 12); impact(cv, t, w(9, "abonne-toi"), 12); drift(cv, t, T, .05)

# ------------------------------------------------------------------ scènes + bruitages
def with_bar(fn):
    def g(cv, fr, t, T):
        fn(cv, fr, t, T); chrono_bar(cv, fr, SCENES)
    return g
def SC(name, n, fn, sfx, trans=None, trans_dur=.25, pad_out=.25):
    return Scene(name, TEXTS[n-1], with_bar(fn), sfx, pad_in=PAD, pad_out=pad_out, trans=trans, trans_dur=trans_dur)
W_ = w
SCENES = [
    SC("faillite", 1, s1, [(.0, "boom", .9), (.0, "stamp", .8), (.05, "riser", .4), (W_(1, "faillite"), "stamp", .9), (W_(1, "faillite"), "groan", .6),
                           (W_(1, "vingt-deux") - .15, "whoosh_up", .7), (W_(1, "bat"), "boom", .7), (W_(1, "bat"), "crowd_long", .9), (W_(1, "Liverpool"), "sparkle"),
                           (W_(1, "L'histoire") - .1, "whoosh", .5), (W_(1, "L'histoire"), "stamp", .7), (W_(1, "minute") - .1, "tick", .9)]),
    SC("1970", 2, s2, [(.0, "boom", .5), (W_(2, "Mille"), "stamp", .6), (W_(2, "naît"), "pop"), (W_(2, "naît"), "sparkle", .6), (W_(2, "En") - .1, "whoosh", .5),
                       (W_(2, "soixante-dix-neuf"), "stamp", .6), (W_(2, "Toulouse", 2), "stamp"), (W_(2, "Téfécé"), "crowd", .8)], trans="punch", trans_dur=.3),
    SC("2001", 3, s3, [(.03, "stamp", .6), (W_(3, "faillite"), "stamp", .9), (W_(3, "faillite"), "groan", .6), (W_(3, "redémarre"), "elevator", .9),
                       (W_(3, "division"), "boom", .7), (W_(3, "remonte") - .1, "whoosh_up", .8), (W_(3, "trois", 2), "stamp", .6), (W_(3, "trois", 2), "crowd_long", .8)],
       trans="whip"),
    SC("2007", 4, s4, [(.0, "boom", .5), (W_(4, "troisième"), "stamp"), (W_(4, "troisième"), "crowd", .8), (W_(4, "première"), "sparkle"),
                       (W_(4, "mais") - .1, "whoosh", .5), (W_(4, "cinq"), "glitch", .7, .35), (W_(4, "cinq"), "groan", .6)], trans="tear_h", trans_dur=.5),
    SC("2020", 5, s5, [(.03, "stamp", .6), (W_(5, "dernier"), "stamp", .8), (W_(5, "retour") - .1, "elevator", .9), (W_(5, "retour") + .5, "boom", .6),
                       (W_(5, "Mais") - .1, "whoosh_up", .7), (W_(5, "champion"), "stamp"), (W_(5, "champion"), "crowd_long", .9), (W_(5, "champion"), "sparkle")],
       trans="whip"),
    SC("pause", 6, s6, [(0, "scratch", 1.0, .9), (.3, "pop"), (W_(6, "kiffes") - .1, "pop2"), (W_(6, "like"), "pop"), (W_(6, "like") + .05, "notif"),
                        (W_(6, "like") + .1, "sparkle", .6), (W_(6, "abonne-toi"), "pop2"), (W_(6, "abonne-toi") + .25, "notif"),
                        (W_(6, "Allez"), "whoosh"), (W_(6, "Allez"), "boom", .5)], trans="polaroid", pad_out=.3),
    SC("coupe", 7, s7, [(.0, "boom", .5), (W_(7, "finale"), "stamp", .6), (W_(7, "Toulouse") - .1, "whoosh", .5), (W_(7, "cinq"), "stamp"),
                        (W_(7, "cinq"), "crowd_long", 1.0), (W_(7, "Le") - .1, "whoosh", .5), (W_(7, "premier"), "stamp"), (W_(7, "premier"), "sparkle")],
       trans="tear_d", trans_dur=.5),
    SC("revanche", 8, s8, [(.03, "stamp", .5), (W_(8, "Ligue"), "stamp", .6), (W_(8, "bat"), "pop"), (W_(8, "Liverpool"), "pop2"), (W_(8, "trois") - .25, "whoosh", .5),
                           (W_(8, "trois") + .25, "kick", .6), (W_(8, "trois") + .5, "boom", .7), (W_(8, "trois") + .5, "crowd_long", 1.0),
                           (W_(8, "revanche"), "stamp"), (W_(8, "revanche"), "sparkle")], trans="whip"),
    SC("fin", 9, s9, [(.0, "boom", .6), (W_(9, "Faillite"), "stamp", .6), (W_(9, "Ligue"), "stamp", .6), (W_(9, "Coupe"), "stamp", .6), (W_(9, "Liverpool"), "stamp", .7),
                      (W_(9, "Toulouse") - .1, "whoosh", .5), (W_(9, "sous-coté"), "pop"), (W_(9, "Dis-le"), "pop2"),
                      (W_(9, "like"), "pop"), (W_(9, "like") + .05, "notif"), (W_(9, "abonne-toi"), "pop2"), (W_(9, "abonne-toi") + .25, "notif"),
                      (W_(9, "abonne-toi") + .1, "crowd", .7), (W_(9, "d'épisodes") - .1, "sparkle")], trans="punch", trans_dur=.3, pad_out=1.2),
]
SCENES[5].trans_dur = 99
SCENES[5].post = s6_post

# ------------------------------------------------------------------ couverture : faillite… puis Liverpool battu
def cover(path):
    cv = background(0, TITLE); bricks(cv, 0, "tscov")
    Label("TOULOUSE", "tcv1", font("title", 180), BLANC, VIO, padx=40, pady=6, rough=4, maxw=980).draw(cv, 0, CX, 330, 1, -3)
    Label("EN FAILLITE EN 2001…", "tcv2", font("title", 72), BLANC, NOIR, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 540, 1, 2)
    SH_TFC.draw(cv, 0, 290, 860, 1.3, -6); K1a.draw(cv, 0, 330, 900, .75, -14)
    SH_LIV.draw(cv, 0, 800, 860, 1.1, 6)
    score2(cv, 0, CX, 1150, "TOULOUSE", "LIVERPOOL", 3, 2, "", .9)
    Label("…ET IL BAT LIVERPOOL ?!", "tcv3", font("title", 72), PAL["ink"], GOLD, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 1420, 1, -2)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

def stills(out, fracs=(.05, .18, .32, .46, .6, .74, .88, .98), only=None):
    scene_timing(SCENES, VOICE); starts = np.cumsum([0]+[sc.T for sc in SCENES])
    os.makedirs(out, exist_ok=True); sheets = []
    for i, sc in enumerate(SCENES):
        if only and (i+1) not in only: continue
        prev = engine._last_frame(SCENES, i-1, starts, TITLE) if (i > 0 and sc.trans) else None
        ims = []
        for fr_ in fracs:
            t = fr_*sc.T; f = int((starts[i]+t)*FPS)
            cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T)
            if prev is not None and t < sc.trans_dur: engine.TRANSITIONS[sc.trans](cv, prev, t, sc.trans_dur, i)
            if getattr(sc, "post", None): sc.post(cv, f, t, sc.T)
            finish(cv, TITLE); ims.append(cv.resize((300, 533)))
        sheet = Image.new("RGB", (300*len(ims), 575), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            sheet.paste(im, (k*300, 42)); dd.text((k*300+8, 6), f"S{i+1} {fracs[k]*sc.T:.1f}/{sc.T:.1f}", font=font("mono", 24), fill=(230, 230, 230))
        p = os.path.join(out, f"tl_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", "toulouse")
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/toulouse_stills"), only=only)); sys.exit()
    if os.environ.get("LEGENDES_PROVISOIRE") and "--apercu" not in args:
        sys.exit("Minutage provisoire : pas de rendu final sans les vraies voix (--apercu pour un aperçu muet).")
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25))
