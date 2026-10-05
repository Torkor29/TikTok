"""Épisode « Légendes du foot » #9 : présentation de Liverpool, format court (~1 min 15), CTA « like + abonne-toi pour plus d'épisodes ».
« LIVERPOOL » dès la 1re image : un club né d'une dispute de loyer (1892, Anfield, Everton s'en va) devenu 6 fois champion d'Europe.
1892 Houlding crée le club ; 1901 1er titre, 1954 D2, 1959 Shankly, 1962 retour en D1 ; années 70-80 : 4 Coupes d'Europe, You'll Never Walk Alone ;
2005 Istanbul (3-0 puis 3-3, tirs au but) ; pause like + abonne-toi ; 2015 Klopp, 2019 Madrid (6e C1), 2020 1er titre en 30 ans ;
2025 20e titre (record égalé avec Manchester United), 2026 Slot remercié, Iraola ; fin : « Liverpool ou Manchester United ? ».

  python3 episodes/liverpool/liverpool.py output/liverpool --stills [3,4]
  python3 episodes/liverpool/liverpool.py output/liverpool --cover
  python3 episodes/liverpool/liverpool.py output/liverpool
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from story import *
from quiz import like_button, sub_button
import engine

TITLE = "~/légendes $ ./liverpool"
SLUG = "liverpool_legende"
SRC = os.environ.get("LEGENDES_PROVISOIRE") or HERE
VOICE = [os.path.join(SRC, "voix", f"scene_{i}.mp3") for i in range(1, 10)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
ALIGN = os.path.join(SRC, "alignement.json")
PAD = 0.12
WS, TEXTS = load_words(ALIGN)
def w(i, word, n=1, end=False):
    """Temps local (dans la scène i) où la voix prononce `word`."""
    return PAD + WS[i-1](word, n, end)

RED = (200, 16, 46); RED_D = (120, 10, 28); RED_DD = (62, 8, 18); BLANC = (250, 250, 246); CREME = (236, 228, 210); GOLD = (236, 186, 48)
NOIR = (30, 28, 28); BLEU = (0, 60, 170); BLEU_D = (10, 26, 70); GRIS = (120, 120, 126); NUIT = (20, 22, 42)

HERO = Player("lfc9", hair=(70, 50, 36), skin=(230, 186, 150))
HERO2 = Player("lfc9b", hair=(24, 20, 18), skin=(140, 96, 70))
EVE = Player("evt9", hair=(150, 110, 60), skin=(230, 186, 150))
EVE2 = Player("evt9b", hair=(30, 24, 20), skin=(206, 160, 124))
HOUL = Player("houl9", hair=(160, 160, 160), beard_col=(170, 170, 170), skin=(226, 176, 140), hair_style="mullet")
SHANK = Player("shank9", hair=(60, 60, 64), skin=(226, 176, 140))
KLOPP = Player("klopp9", hair=(150, 120, 84), beard_col=(120, 96, 70), skin=(226, 176, 140))
SLOT = Player("slot9", hair=(30, 30, 30), skin=(230, 186, 150), hair_style="bald")
IRAO = Player("irao9", hair=(30, 24, 20), beard_col=(40, 30, 26), skin=(214, 168, 130))
MILAN = Player("mil9", hair=(24, 20, 18), skin=(206, 160, 124))

# ------------------------------------------------------------------ objets
def _facture(d, a):
    ax, ay = a
    d.text((ax, ay - 190), "FACTURE", font=font("title", 70), fill=NOIR, anchor="mm")
    d.line([(ax - 250, ay - 140), (ax + 250, ay - 140)], fill=(150, 140, 120), width=4)
    d.text((ax, ay - 95), "loyer d'Anfield", font=font("hand", 50), fill=(90, 80, 70), anchor="mm")
    d.text((ax - 20, ay - 20), "1884 :   100 £", font=font("title", 62), fill=(110, 100, 90), anchor="mm")
    d.text((ax - 20, ay + 80), "1892 :   250 £", font=font("title", 88), fill=RED, anchor="mm")
FACTURE = Paper(rect_pts(640, 560), (248, 242, 226), "lfacture", rough=2.2, hatch=True).add(_facture)

SHIELD = [(-110, -130), (110, -130), (110, 10), (60, 100), (0, 140), (-60, 100), (-110, 10)]
def _shield(key, col, col2, txt, size=46):
    def dec(d, a):
        ax, ay = a
        d.polygon([(ax - 110, ay - 130), (ax, ay - 130), (ax, ay + 140), (ax - 60, ay + 100), (ax - 110, ay + 10)], fill=col2)
        d.text((ax, ay - 10), txt, font=font("title", size), fill=BLANC, anchor="mm", stroke_width=5, stroke_fill=NOIR)
    return Paper(poly_pts(SHIELD), col, key, rough=1.6, hatch=True).add(dec)
SH_LIV = _shield("lsliv", RED, RED_D, "LIVER-\nPOOL", 44)
SH_EVE = _shield("lseve", BLEU, (60, 110, 210), "EVERTON", 32)
SH_MU = _shield("lsmu", (170, 20, 30), (110, 12, 20), "MAN\nUNITED", 36)

def _anfield(d, a):
    ax, ay = a
    for k in range(-8, 9):
        x = ax + k*50; d.line([(x, ay - 150 + abs(k)*6), (x - 10, ay + 120)], fill=(176, 40, 52), width=10)
    d.rectangle([ax - 200, ay + 80, ax + 200, ay + 140], fill=RED_D)
    d.text((ax, ay + 110), "ANFIELD", font=font("title", 44), fill=BLANC, anchor="mm")
ANFIELD = Paper(ellipse_pts(900, 380, 60), (226, 150, 156), "lanfield", rough=1.6, hatch=True).add(_anfield)

def _scarf(d, a):
    ax, ay = a
    for k in range(5): d.rectangle([ax - 430 + k*22, ay - 85, ax - 430 + k*22 + 10, ay + 85], fill=BLANC)
    for k in range(5): d.rectangle([ax + 430 - k*22 - 10, ay - 85, ax + 430 - k*22, ay + 85], fill=BLANC)
    d.text((ax, ay), "YOU'LL NEVER WALK ALONE", font=font("title", 62), fill=GOLD, anchor="mm", stroke_width=4, stroke_fill=RED_DD)
    for k in range(18):
        for sx in (-1, 1): d.line([(ax + sx*430 + sx*2, ay - 80 + k*9.4), (ax + sx*462, ay - 80 + k*9.4 + 4)], fill=BLANC, width=3)
SCARF = Paper(rect_pts(900, 175), RED, "lscarf", rough=1.4, hatch=True, pad=60).add(_scarf)

def stadium(cv, fr, key, t=0.0, sky=NUIT, grass=(46, 112, 64), horizon=1060, pal=None):
    stage_fill(cv, fr, sky, key); d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    rnd = random.Random(key); pal = pal or [RED, BLANC, RED_D, (230, 120, 130), (200, 196, 190), (150, 20, 40)]
    for row in range(7):
        ry = 560 + row*68; n = 18 + row
        for k in range(n):
            x = 50 + k*(980/(n-1)); jump = 6*abs(math.sin(t*7 + k*1.3 + row))
            d.ellipse([x-17, ry-17-jump, x+17, ry+17-jump], fill=rnd.choice(pal))
    for fx in (150, 930):
        for r, c in ((70, (70, 70, 60)), (46, (200, 196, 150)), (26, (255, 252, 230))): d.ellipse([fx-r, 300-r, fx+r, 300+r], fill=c)
    for k in range(8):
        y0 = horizon + k*(sy1-horizon)/8
        d.rectangle([sx0, y0, sx1, y0 + (sy1-horizon)/8 + 1], fill=grass if k % 2 == 0 else tuple(int(c*.9) for c in grass))
    d.line([(sx0, horizon), (sx1, horizon)], fill=(230, 236, 226), width=6)

SCOREBOARD = scoreboard_sprite(820, 330, "lscore")
def score2(cv, fr, x, y, la, lb, a, b, sub="", s=1.0):
    if s <= .02: return
    L = layer(900, 420, (450, 210)); SCOREBOARD.draw(L, fr, 450, 210, 1, 0, 1)
    d = ImageDraw.Draw(L)
    for x_, lab in ((180, la), (720, lb)): d.text((x_, 130), lab, font=font("mono", 64 if len(lab) <= 5 else 44), fill=(200, 196, 190), anchor="mm")
    d.text((450, 220), f"{a} - {b}", font=font("title", 150), fill=(255, 204, 70), anchor="mm")
    if sub: d.text((450, 330), sub, font=font("mono", 38), fill=(170, 166, 160), anchor="mm")
    blit(cv, L, x, y, s)

def trophy_lift(cv, fr, pl, x, y, s, kit, t, trophy=UCL, mood="cheer", **kw):
    pl.draw(cv, fr, x, y, s, age=1, kit=kit, mood=mood, arms=(160, 160), legs=(12, 12), t=t, **kw)
    trophy.draw(cv, fr, x, y - 850*s + 8*math.sin(t*6), .9*s, 3*math.sin(t*4))

def shaft(cv, fr, t, speed=0.0, key="lshaft"):
    stage_fill(cv, fr, (34, 32, 40), key); d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    for j in range(8):
        y = (j*260 + t*speed) % 2080 - 80
        d.rectangle([sx0, y, sx1, y + 16], fill=(70, 66, 80)); d.line([(sx0, y + 30), (sx1, y + 30)], fill=(56, 52, 64), width=4)

def stopwatch(cv, x, y, s, u):
    d = ImageDraw.Draw(cv)
    d.rectangle([x-18*s, y-150*s, x+18*s, y-118*s], fill=(80, 80, 88)); d.ellipse([x-120*s, y-120*s, x+120*s, y+120*s], fill=(80, 80, 88))
    d.ellipse([x-104*s, y-104*s, x+104*s, y+104*s], fill=(250, 250, 246))
    for k in range(12):
        an = k*math.pi/6; d.line([(x+88*s*math.sin(an), y-88*s*math.cos(an)), (x+100*s*math.sin(an), y-100*s*math.cos(an))], fill=PAL["ink"], width=max(2, int(5*s)))
    an = u*math.pi*2; d.line([(x, y), (x+80*s*math.sin(an), y-80*s*math.cos(an))], fill=RED, width=max(3, int(8*s)))
    d.ellipse([x-10*s, y-10*s, x+10*s, y+10*s], fill=PAL["ink"])

def suitcase(cv, x, y, s=1.0):
    d = ImageDraw.Draw(cv)
    d.rounded_rectangle([x-70*s, y, x+70*s, y+110*s], int(12*s), fill=(150, 96, 56), outline=(90, 56, 30), width=max(2, int(5*s)))
    d.rectangle([x-70*s, y+46*s, x+70*s, y+58*s], fill=(110, 70, 40)); d.arc([x-26*s, y-30*s, x+26*s, y+10*s], 180, 360, fill=(90, 56, 30), width=max(3, int(8*s)))

# ------------------------------------------------------------------ labels
K1a = KW("DISPUTE DE LOYER", "lk1a", PAL["ink"], size=92); T1a = TAG("1884 : 100 £  →  1892 : 250 £", "lt1a", PAL["paper"], size=46)
K1b = KW("6 COUPES D'EUROPE", "lk1b", GOLD, PAL["ink"], 84); X6 = Label("×6", "lx6", font("title", 220), GOLD, None, stroke=8, stroke_fill=PAL["ink"])
K1c = STAMP("L'HISTOIRE DE LIVERPOOL", "lk1c", RED_D, 78); K1d = KW("EN 1 MINUTE", "lk1d", RED, size=110)
STAMP_IMP = STAMP("IMPAYÉ", "lstimp", RED, 130)
K2a = KW("1892", "lk2a", PAL["ink"], size=170); K2b = STAMP("EVERTON S'EN VA", "lk2b", BLEU, 84); T2a = TAG("à cause du loyer d'Anfield", "lt2a", PAL["paper"], size=50)
T2b = TAG("John Houlding, le propriétaire", "lt2b", PAL["paper"], size=48); K2c = STAMP("LIVERPOOL FC", "lk2c", RED, 100); T2c = TAG("un stade vide… alors il crée son club", "lt2c", PAL["paper"], size=46)
K3a = KW("1901", "lk3a", PAL["ink"], size=170); K3b = STAMP("1er TITRE", "lk3b", RED, 120)
K3c = KW("1954", "lk3c", PAL["ink"], size=150); K3d = KW("2e DIVISION", "lk3d", RED, size=120)
K3e = KW("1959", "lk3e", PAL["ink"], size=150); T3a = TAG("Bill Shankly arrive", "lt3a", GOLD, size=56)
K3f = KW("1962", "lk3f", PAL["ink"], size=150); T3b = TAG("de retour en D1 !", "lt3b", PAL["paper"], size=56)
K4a = KW("L'ÂGE D'OR", "lk4a", GOLD, PAL["ink"], 110); T4a = TAG("années 70 et 80", "lt4a", PAL["paper"], size=56)
K4b = KW("4 EN 8 ANS", "lk4b", PAL["ink"], size=130); YEARS4 = [Label(y, "ly4"+y, font("title", 84), PAL["ink"], GOLD, padx=20, pady=4, rough=2.5) for y in ("1977", "1978", "1981", "1984")]
K4c = KW("TOUT ANFIELD CHANTE", "lk4c", RED_D, size=84)
K5a = KW("2005", "lk5a", PAL["ink"], size=170); K5b = STAMP("ISTANBUL", "lk5b", RED, 120)
K5c = KW("MENÉS 3 - 0", "lk5c", PAL["ink"], size=110); T5a = TAG("à la mi-temps contre le Milan AC", "lt5a", PAL["paper"], size=46)
K5d = KW("3 - 3 !", "lk5d", RED, size=190); T5b = TAG("en 6 minutes", "lt5b", GOLD, size=62)
K5e = STAMP("AUX TIRS AU BUT !", "lk5e", RED, 96); T5c = TAG("le miracle d'Istanbul", "lt5c", PAL["paper"], size=56)
K6a = KW("PETITE PAUSE !", "lk6a", PAL["paper"], PAL["ink"], 84); T6a = TAG("si tu kiffes…", "lt6a", PAL["paper"], size=56)
K6b = KW("LÂCHE UN LIKE", "lk6b", PAL["paper"], PAL["ink"], 76); T6b = TAG("pour plus d'épisodes !", "lt6b", PAL["paper"], size=56)
K6c = KW("ON REPREND !", "lk6c", PAL["paper"], PAL["ink"], 84)
K7a = KW("2015", "lk7a", PAL["ink"], size=170); T7a = TAG("Jürgen Klopp arrive", "lt7a", GOLD, size=58)
K7b = KW("2019 : MADRID", "lk7b", PAL["ink"], size=100); K7c = STAMP("6e LIGUE DES CHAMPIONS", "lk7c", RED, 74)
K7d = KW("2020", "lk7d", PAL["ink"], size=170); K7e = KW("1er TITRE EN 30 ANS", "lk7e", RED, size=88); T7b = TAG("depuis 1990", "lt7b", PAL["paper"], size=56)
K8a = KW("2025", "lk8a", PAL["ink"], size=170); K8b = STAMP("20e TITRE", "lk8b", RED, 130); T8a = TAG("Arne Slot, champion dès sa 1re saison", "lt8a", PAL["paper"], size=44)
K8c = KW("= MANCHESTER UNITED", "lk8c", GOLD, PAL["ink"], 70); L20 = Label("20", "ll20", font("title", 260), BLANC, RED, padx=36, pady=4, rough=3)
K8d = KW("2026", "lk8d", PAL["ink"], size=170); K8e = STAMP("SLOT REMERCIÉ", "lk8e", RED_D, 100); K8f = KW("IRAOLA ARRIVE", "lk8f", RED, size=110); T8b = TAG("nouvel entraîneur", "lt8b", PAL["paper"], size=56)
K9a = KW("6 COUPES D'EUROPE", "lk9a", GOLD, PAL["ink"], 84); K9b = STAMP("20 TITRES", "lk9b", RED, 120); T9a = TAG("tout ça… né d'une dispute de loyer", "lt9a", PAL["paper"], size=46)
K9c = KW("LE PLUS GRAND ?", "lk9c", PAL["ink"], size=100); VS = Label("VS", "lvs", font("title", 150), GOLD, None, stroke=8, stroke_fill=PAL["ink"])
K9d = KW("COMMENTE !", "lk9d", RED, size=100); K9e = KW("+ D'ÉPISODES", "lk9e", PAL["ink"], size=84)

# ------------------------------------------------------------------ SCÈNE 1 — né d'une dispute de loyer… six Coupes d'Europe
def s1a(cv, fr, t):
    stage_fill(cv, fr, CREME, "ls1a"); d = ImageDraw.Draw(cv)
    for k in range(-2, 12): d.polygon([(k*130 + 130, 0), (k*130 + 195, 0), (k*130 - 405, 1920), (k*130 - 470, 1920)], fill=(226, 214, 192))
    LIVER = Label("LIVERPOOL", "ls1t", font("title", 170), BLANC, RED, padx=36, pady=6, rough=4, maxw=1000)
    LIVER.draw(cv, fr, CX, 360, lerp(1.2, 1.0, ease_out_cubic(prog(t, 0, .25))), -3)
    ti = w(1, "dispute") - .1
    FACTURE.draw(cv, fr, CX, 1020, .95*slam(t, ti, .22) if t >= ti else 0, -5)
    if t > w(1, "loyer"): show_stamp(cv, fr, STAMP_IMP, t, w(1, "loyer") - .02, 700, 1240, 14)
    kw(cv, fr, K1a, t, ti + .05, None, CX, 640, -3)
    show(cv, fr, T1a, t, w(1, "loyer") + .2, None, CX, 1480, 2)
    if t < ti + .3:
        HERO.draw(cv, fr, CX + 250, 1800, 1.0, age=1, kit="liverpool", mood="cheer", arms=(150 + 8*math.sin(t*6), 150), legs=(12, 12), t=t)
        SH_LIV.draw(cv, fr, CX - 230, 1180, 1.9*(1 - prog(t, ti, .3)), -4)
        if t < ti - .05: TAG("1892 : le début de l'histoire", "lt1z", PAL["paper"], size=50).draw(cv, fr, CX, 640, 1, 2)

def s1b(cv, fr, t):
    stage_fill(cv, fr, RED_DD, "ls1b"); rays(cv, (CX, 1050), t, 1.0, 16, 1500, (150, 30, 40))
    t0 = w(1, "Aujourd'hui") - .1
    for k in range(6):
        x = 170 + (k % 3)*370; y = 880 + (k // 3)*330
        UCL.draw(cv, fr, x, y + 8*math.sin(t*5 + k), .95*slam(t, w(1, "six") + k*.1, .2), ((-6, 5, -4, 6, -5, 4))[k])
    kw(cv, fr, K1b, t, w(1, "six") - .05, None, CX, 440, -3)
    X6.draw(cv, fr, CX, 1560, pop_in(t, w(1, "Coupes") - .05), -6)
    confetti(cv, fr, "lc1", t - w(1, "Coupes"), 80, 3, [GOLD, BLANC, RED])
    camera_flashes(cv, fr, "lf1", t - t0, 1.4, 10)

def s1c(cv, fr, t):
    stage_fill(cv, fr, RED, "ls1c"); d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    d.rectangle([CX - 150, sy0, CX + 150, sy1], fill=BLANC); d.rectangle([CX - 110, sy0, CX + 110, sy1], fill=RED_D)
    t0 = w(1, "L'histoire") - .1
    for P, x, k in ((HERO2, 220, 0), (HERO, 860, 1)):
        P.draw(cv, fr, x, 1780 - 60*abs(math.sin(t*6 + k)), .82, age=1, kit="liverpool", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
    show_stamp(cv, fr, K1c, t, t0 + .05, CX, 420, -4)
    kw(cv, fr, K1d, t, w(1, "minute") - .1, None, CX, 600, 3)
    stopwatch(cv, CX, 900, 1.1, prog(t, t0, 1.2))

def s1(cv, fr, t, T):
    shots(cv, fr, t, [(0, s1a), (w(1, "Aujourd'hui") - .1, s1b), (w(1, "L'histoire") - .1, s1c)], d=.24)
    impact(cv, t, .02, 18); impact(cv, t, w(1, "loyer"), 22); flashes(cv, t, w(1, "loyer"), .1, .5)
    impact(cv, t, w(1, "six"), 16); punch(cv, t, w(1, "L'histoire") - .1, 1.1); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 2 — 1892 : Everton quitte Anfield, Houlding crée Liverpool
def s2a(cv, fr, t):
    stage_fill(cv, fr, (176, 206, 232), "ls2a"); d = ImageDraw.Draw(cv)
    ANFIELD.draw(cv, fr, CX, 1230, 1.5, 0)
    d.rectangle([STAGE[0], 1560, STAGE[2], STAGE[3]], fill=(120, 130, 150))
    kw(cv, fr, K2a, t, w(2, "Mille") - .05, None, CX, 420, -3)
    te = w(2, "Everton")
    for k, (P, x) in enumerate(((EVE, 250), (EVE2, 390))):
        u = prog(t, w(2, "quitte") - .1, 1.5)
        xx = x - 330*u if t > w(2, "quitte") - .1 else x
        P.draw(cv, fr, xx, 1780, .75*pop_in(t, te - .05 + k*.1, .3), age=1, kit="everton", mood="sad" if t > te + .3 else "normal", t=t, legs=(20*math.sin(t*9), -20*math.sin(t*9)) if u > 0 and u < 1 else (0, 0))
    if t > te: SH_EVE.draw(cv, fr, 780, 880, .8*pop_in(t, te, .3), 5)
    show_stamp(cv, fr, K2b, t, w(2, "quitte") - .05, CX, 620, 4)
    show(cv, fr, T2a, t, w(2, "dispute") - .05, None, CX, 780, -2)

def s2b(cv, fr, t):
    stage_fill(cv, fr, CREME, "ls2b")
    t0 = w(2, "Le") - .1
    FACTURE.draw(cv, fr, CX - 90, 1050, .9*pop_in(t, t0 + .05, .3), -6)
    HOUL.draw(cv, fr, 820, 1800, .78*pop_in(t, w(2, "propriétaire") - .1, .3), age=1, kit="suit", beard=True, mood="happy", t=t)
    show(cv, fr, T2b, t, w(2, "John") - .05, None, CX, 520, -2)
    if t > w(2, "loyer.") if False else t > t0 + .3: show_stamp(cv, fr, STAMP_IMP, t, t0 + .4, 420, 1330, -12)

def s2c(cv, fr, t):
    stage_fill(cv, fr, RED_D, "ls2c"); tc = w(2, "crée")
    rays(cv, (CX, 1050), t, prog(t, tc, .3), 14, 1000, (230, 160, 160))
    ANFIELD.draw(cv, fr, CX, 1500, 1.3, 0)
    SH_LIV.draw(cv, fr, CX, 980, 1.7*slam(t, w(2, "club"), .2), -3)
    particles(cv, fr, "lp2", (CX, 980), prog(t, w(2, "club"), .6), 20, 320, [RED, BLANC, GOLD], 16)
    show_stamp(cv, fr, K2c, t, w(2, "Liverpool") - .05, CX, 420, -4)
    show(cv, fr, T2c, t, tc, None, CX, 600, 2)

def s2(cv, fr, t, T):
    shots(cv, fr, t, [(0, s2a), (w(2, "Le") - .1, s2b), (w(2, "crée") - .15, s2c)], d=.24)
    impact(cv, t, w(2, "Mille"), 12); impact(cv, t, w(2, "quitte"), 14); impact(cv, t, w(2, "club") + .02, 20)
    flashes(cv, t, w(2, "club"), .1, .5); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 3 — 1901 1er titre, 1954 la D2, 1959 Shankly, 1962 retour
def s3a(cv, fr, t):
    stage_fill(cv, fr, CREME, "ls3a"); d = ImageDraw.Draw(cv)
    for k in range(-2, 12): d.polygon([(k*130 + 130, 0), (k*130 + 195, 0), (k*130 - 405, 1920), (k*130 - 470, 1920)], fill=(226, 214, 192))
    trophy_lift(cv, fr, HERO, CX, 1780, .85, "liverpool", t, CUP)
    kw(cv, fr, K3a, t, w(3, "mille") - .1, None, CX, 400, -3)
    show_stamp(cv, fr, K3b, t, w(3, "titre") - .05, CX, 600, 4)
    confetti(cv, fr, "lc3", t - w(3, "titre"), 70, 3, [BLANC, RED, GOLD])

def s3b(cv, fr, t):
    te = w(3, "tombe") - .1; td = w(3, "division")
    stage_fill(cv, fr, RED_D, "ls3b")
    HERO.draw(cv, fr, CX, 1740, 1.05, age=1, kit="liverpool", mood="surprised", t=t)
    floor_panel(cv, fr, CX, 660, "D1", t, True, 1.6, 1)
    elevator_drop(cv, t, te, td - te)
    kw(cv, fr, K3c, t, w(3, "cinquante-quatre") - .05, None, CX, 400, -3)
    if t > td:
        shaft(cv, fr, t, 0, "ls3shaft")
        HERO.draw(cv, fr, CX, 1740, 1.05, age=1, kit="liverpool", mood="sad", t=t, look=(0, 1))
        floor_panel(cv, fr, CX, 660, "D2", t, True, 1.8, 1)
        kw(cv, fr, K3d, t, td, None, CX, 960, 3)

def s3c(cv, fr, t):
    t0 = w(3, "En", 2) - .1; tq = w(3, "soixante-deux")
    if t < tq + .3:
        shaft(cv, fr, t, 900 + 2200*prog(t, w(3, "et") - .1, tq + .3 - w(3, "et") + .1) if t > w(3, "et") - .1 else 0)
        lab = "D2" if t < w(3, "et") else ("D2", "D1")[int(prog(t, w(3, "et"), tq - w(3, "et")) > .55)]
        floor_panel(cv, fr, CX, 640, lab, t, False, 1.8, 1)
        SHANK.draw(cv, fr, CX, 1740, 1.05*pop_in(t, w(3, "Bill") - .15, .3), age=1, kit="suit", mood="cheer" if t > w(3, "arrive") else "happy",
                   arms=(150, 150) if t > w(3, "arrive") else (20, 20), t=t)
        kw(cv, fr, K3e, t, t0 + .05, None, CX, 420, -3)
        show(cv, fr, T3a, t, w(3, "Bill") - .05, None, CX, 880, 2)
    else:
        stage_fill(cv, fr, RED_DD, "ls3c"); rays(cv, (CX, 1000), t, .8, 16, 1500, (150, 30, 40))
        ANFIELD.draw(cv, fr, CX, 1000, 1.05*slam(t, tq, .22), 0)
        HERO.draw(cv, fr, CX, 1780, .85, age=1, kit="liverpool", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
        show(cv, fr, T3b, t, tq + .1, None, CX, 640, 2)
    kw(cv, fr, K3f, t, tq - .05, None, CX, 420, -3)

def s3(cv, fr, t, T):
    shots(cv, fr, t, [(0, s3a), (w(3, "Mais") - .1, s3b), (w(3, "En", 2) - .1, s3c)], d=.24)
    impact(cv, t, w(3, "titre"), 16); impact(cv, t, w(3, "division") + .02, 24); impact(cv, t, w(3, "soixante-deux"), 16); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 4 — l'âge d'or : 4 Coupes d'Europe, You'll Never Walk Alone
def s4a(cv, fr, t):
    stage_fill(cv, fr, RED, "ls4a"); rays(cv, (CX, 1100), t, .6, 16, 1500, (230, 90, 100), .12, .15)
    for P, x, k in ((HERO2, 260, 0), (HERO, 820, 1)):
        P.draw(cv, fr, x, 1780 - 50*abs(math.sin(t*6 + k)), .9, age=1, kit="liverpool", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
    kw(cv, fr, K4a, t, w(4, "d'or") - .25, None, CX, 440, -3)
    show(cv, fr, T4a, t, w(4, "Années") - .02, None, CX, 620, 2)

def s4b(cv, fr, t):
    stage_fill(cv, fr, RED_DD, "ls4b"); rays(cv, (CX, 1000), t, 1.0, 16, 1500, (150, 30, 40))
    for k in range(4):
        tk = w(4, "Quatre", 2) + k*.4 - .05
        x = 290 + (k % 2)*500; y = 760 + (k // 2)*520
        UCL.draw(cv, fr, x, y + 8*math.sin(t*5 + k), 1.15*slam(t, tk, .2), (-6, 6, 5, -5)[k])
        YEARS4[k].draw(cv, fr, x, y + 150, pop_in(t, tk + .1, .3), (4, -4, -3, 4)[k])
    kw(cv, fr, K4b, t, w(4, "huit") - .1, None, CX, 440, -3)
    confetti(cv, fr, "lc4", t - w(4, "ans"), 60, 3, [GOLD, BLANC, RED])

def s4c(cv, fr, t):
    stadium(cv, fr, "ls4stad", t, horizon=1180)
    ts = w(4, "hymne")
    for k in range(7):
        sw = math.sin(t*5 + k*1.1)
        L = layer(120, 360, (60, 300)); ImageDraw.Draw(L).rectangle([40, 0, 80, 300], fill=RED if k % 2 else BLANC)
        ImageDraw.Draw(L).rectangle([40, 0, 80, 40], fill=BLANC if k % 2 else RED)
        blit(cv, L, 110 + k*140, 780 + 20*abs(sw), 1, 18*sw, pop_in(t, w(4, "stade") + k*.05, .25))
    SCARF.draw(cv, fr, CX, 1000, 1.05*slam(t, ts - .15, .22), -3 + 2*math.sin(t*4))
    kw(cv, fr, K4c, t, w(4, "tout") - .05, ts - .2, CX, 400, -3)
    HERO.draw(cv, fr, CX, 1840, .6, age=1, kit="liverpool", mood="cheer", arms=(150, 150), t=t)

def s4(cv, fr, t, T):
    shots(cv, fr, t, [(0, s4a), (w(4, "Quatre", 2) - .15, s4b), (w(4, "Et", 2) - .1, s4c)], d=.24)
    impact(cv, t, w(4, "d'or"), 16)
    for k in range(4): impact(cv, t, w(4, "Quatre", 2) + k*.4 - .05, 10)
    impact(cv, t, w(4, "hymne"), 14); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 5 — 2005 Istanbul : 3-0, 3-3, tirs au but
def s5a(cv, fr, t):
    stadium(cv, fr, "ls5stad", t, horizon=1180, sky=(16, 18, 40))
    kw(cv, fr, K5a, t, w(5, "mille") - .1, None, CX, 420, -3)
    show_stamp(cv, fr, K5b, t, w(5, "Istanbul") - .05, CX, 640, 4)
    UCL.draw(cv, fr, CX, 1280, 1.2*pop_in(t, w(5, "Istanbul"), .3), 0)

def s5b(cv, fr, t):
    stage_fill(cv, fr, (24, 26, 34), "ls5b")
    for k, x in enumerate((220, 560, 860)):
        MILAN.draw(cv, fr, x, 1780, .66*pop_in(t, w(5, "menée") + k*.1, .3), age=1, kit="milan", mood="cheer", arms=(150, 150), t=t)
    score2(cv, fr, CX, 760, "MILAN", "LIVERPOOL", 3, 0, "mi-temps", .9*pop_in(t, w(5, "trois") - .1, .3))
    kw(cv, fr, K5c, t, w(5, "menée") - .05, None, CX, 440, -3)
    show(cv, fr, T5a, t, w(5, "Milan") - .05, None, CX, 1040, 2)
    if t > w(5, "zéro"): glitch(cv, fr, t, w(5, "zéro"), .3, 16)

def s5c(cv, fr, t):
    stage_fill(cv, fr, RED_DD, "ls5c"); rays(cv, (CX, 1000), t, .8, 16, 1500, (150, 30, 40))
    t0 = w(5, "revient"); t1 = w(5, "trois", 2); t2 = w(5, "partout")
    g = 1 if t < t1 else (2 if t < t2 else 3)
    score2(cv, fr, CX, 700, "MILAN", "LIVERPOOL", 3, g, "", .9)
    HERO.draw(cv, fr, CX, 1780, .95, age=1, kit="liverpool", mood="cheer" if g == 3 else "determined", arms=(150, 150) if g == 3 else (20, 20), t=t)
    if t > t2: show_stamp(cv, fr, K5d, t, t2 - .05, CX, 1030, -4); show(cv, fr, T5b, t, t2 + .2, None, CX, 1200, 2)
    for tg in (t0, t1, t2):
        if tg <= t < tg + .5: speed_lines(cv, fr, (CX + 190, 700), .4*(1 - (t - tg)/.5), n=20, seed=int(tg*10), inner=200)

def s5d(cv, fr, t):
    stage_fill(cv, fr, NUIT, "ls5d"); rays(cv, (CX, 1000), t, .9, 16, 1500, (60, 70, 130))
    tb = w(5, "tirs") - .1
    show_stamp(cv, fr, K5e, t, tb, CX, 420, -4)
    trophy_lift(cv, fr, HERO, CX, 1780, .85, "liverpool", t)
    show(cv, fr, T5c, t, w(5, "but") - .05, None, CX, 640, 3)
    confetti(cv, fr, "lc5", t - w(5, "but"), 90, 3, [RED, BLANC, GOLD])

def s5(cv, fr, t, T):
    shots(cv, fr, t, [(0, s5a), (w(5, "menée") - .15, s5b), (w(5, "Liverpool") - .1, s5c), (w(5, "et") - .1, s5d)], d=.24)
    impact(cv, t, w(5, "Istanbul"), 14); impact(cv, t, w(5, "zéro"), 24)
    for wd in ("revient",): impact(cv, t, w(5, wd), 10)
    impact(cv, t, w(5, "partout"), 20); flashes(cv, t, w(5, "partout"), .1, .5); impact(cv, t, w(5, "but"), 20); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 6 — PAUSE : like + abonne-toi pour plus d'épisodes
def s6(cv, fr, t, T):
    stage_fill(cv, fr, (74, 12, 28), "ls6"); rays(cv, (CX, 1050), t, .5, 14, 1400, (190, 30, 56))
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

# ------------------------------------------------------------------ SCÈNE 7 — Klopp, Madrid 2019, le titre 2020 après 30 ans
def s7a(cv, fr, t):
    stage_fill(cv, fr, (240, 226, 200), "ls7a"); rays(cv, (CX, 1100), t, .5, 16, 1500, (226, 120, 120), .12, .15)
    KLOPP.draw(cv, fr, CX, 1780, 1.0*pop_in(t, w(7, "Klopp") - .2, .3), age=1, kit="suit", beard=True, mood="cheer",
               arms=(160 + 8*math.sin(t*9), 20), t=t)
    kw(cv, fr, K7a, t, .05, None, CX, 400, -3)
    show(cv, fr, T7a, t, w(7, "Klopp") - .05, None, CX, 600, 2)

def s7b(cv, fr, t):
    stage_fill(cv, fr, (18, 22, 52), "ls7b"); rays(cv, (CX, 1050), t, 1.0, 16, 1500, (60, 80, 150))
    tm = w(7, "Madrid", 1) - .1; ts = w(7, "sixième")
    kw(cv, fr, K7b, t, w(7, "Deux", 2) - .1, None, CX, 420, -3)
    UCL.draw(cv, fr, CX, 1130, 1.7*slam(t, tm + .1, .22), 0)
    show_stamp(cv, fr, K7c, t, ts - .05, CX, 640, 4)
    confetti(cv, fr, "lc7", t - ts, 80, 3, [RED, BLANC, GOLD])

def s7c(cv, fr, t):
    stage_fill(cv, fr, RED, "ls7c"); rays(cv, (CX, 1000), t, .6, 16, 1500, (230, 100, 110), .12, .2)
    t0 = w(7, "Et") - .05; tv = w(7, "trente")
    kw(cv, fr, K7d, t, w(7, "vingt") - .1, None, CX, 380, -3)
    u = prog(t, w(7, "premier") - .1, w(7, "ans") - w(7, "premier") + .2)
    LBL(counter(1990, 2020, u, ""), "lyc7", font("title", 230), GOLD, NOIR, padx=34, pady=0, rough=3).draw(cv, fr, CX, 900, pop_in(t, t0, .3), -2)
    show_stamp(cv, fr, K7e, t, tv - .05, CX, 1190, -3)
    show(cv, fr, T7b, t, tv + .25, None, CX, 1290, 2)
    trophy_lift(cv, fr, KLOPP, CX, 1840, .55, "suit", t, CUP, beard=True) if t > tv else None
    if t > tv: confetti(cv, fr, "lc7b", t - tv, 80, 3, [BLANC, GOLD, NOIR])

def s7(cv, fr, t, T):
    shots(cv, fr, t, [(0, s7a), (w(7, "Deux", 2) - .15, s7b), (w(7, "Et") - .1, s7c)], d=.24)
    impact(cv, t, w(7, "Klopp"), 12); impact(cv, t, w(7, "sixième"), 20); flashes(cv, t, w(7, "sixième"), .1, .5)
    impact(cv, t, w(7, "trente"), 22); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 8 — 2025 20e titre ; 2026 Slot remercié, Iraola
def s8a(cv, fr, t):
    stage_fill(cv, fr, RED_DD, "ls8a"); rays(cv, (CX, 1050), t, .9, 16, 1500, (180, 30, 50))
    kw(cv, fr, K8a, t, .05, None, CX, 380, -3)
    show_stamp(cv, fr, K8b, t, w(8, "vingtième") - .05, CX, 560, 4)
    L20.draw(cv, fr, 300, 900, pop_in(t, w(8, "vingtième"), .3), -4)
    tm = w(8, "comme")
    if t > tm - .05:
        SH_MU.draw(cv, fr, 780, 900, 1.0*pop_in(t, tm, .3), 4)
        LBL("=", "leq", font("title", 190), GOLD, None, stroke=8, stroke_fill=NOIR).draw(cv, fr, CX, 900, pop_in(t, tm + .15, .3), 0)
        show_stamp(cv, fr, K8c, t, w(8, "Manchester") - .05, CX, 1180, -3)
    trophy_lift(cv, fr, SLOT, CX, 1830, .55, "suit", t, CUP)
    confetti(cv, fr, "lc8", t - w(8, "offre"), 90, 3, [RED, BLANC, GOLD])

def s8b(cv, fr, t):
    stage_fill(cv, fr, (40, 44, 60), "ls8b"); d = ImageDraw.Draw(cv)
    tr = w(8, "remercié")
    kw(cv, fr, K8d, t, w(8, "Mais") - .05, None, CX, 380, -3)
    u = prog(t, tr, 1.2)
    SLOT.draw(cv, fr, 560 - 380*ease_in_cubic(u), 1760, .98, age=1, kit="suit", mood="sad", t=t, look=(-1, 1),
              legs=(18*math.sin(t*9), -18*math.sin(t*9)) if 0 < u < 1 else (0, 0))
    if t > tr - .1: suitcase(cv, 700 - 380*ease_in_cubic(u), 1660, .9)
    show_stamp(cv, fr, K8e, t, tr - .05, CX, 640, -5)
    for k in range(40):   # pluie
        x = (k*83 + t*140) % 1080; y = (k*211 + t*900) % 1700 + 100
        d.line([(x, y), (x - 10, y + 36)], fill=(150, 170, 210), width=3)

def s8c(cv, fr, t):
    stage_fill(cv, fr, CREME, "ls8c"); rays(cv, (CX, 1000), t, .8, 16, 1500, (230, 130, 130), .12, .15)
    ti = w(8, "Iraola") - .1
    IRAO.draw(cv, fr, CX, 1780, 1.05*pop_in(t, ti, .3), age=1, kit="suit", beard=True, mood="happy", arms=(150, 150) if t > ti + .4 else (20, 20), t=t)
    kw(cv, fr, K8f, t, ti, None, CX, 420, -3)
    show(cv, fr, T8b, t, ti + .3, None, CX, 600, 2)
    particles(cv, fr, "lp8", (CX, 1100), prog(t, ti, .7), 18, 300, [RED, BLANC, GOLD], 16)

def s8(cv, fr, t, T):
    shots(cv, fr, t, [(0, s8a), (w(8, "Mais") - .1, s8b), (w(8, "et") - .12, s8c)], d=.24)
    impact(cv, t, w(8, "vingtième"), 22); flashes(cv, t, w(8, "vingtième"), .1, .5); impact(cv, t, w(8, "remercié"), 16)
    impact(cv, t, w(8, "Iraola"), 12); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 9 — bilan, « Liverpool ou Manchester United ? », like + abonne-toi
def s9a(cv, fr, t):
    stage_fill(cv, fr, CREME, "ls9a"); d = ImageDraw.Draw(cv)
    for k in range(-2, 12): d.polygon([(k*130 + 130, 0), (k*130 + 195, 0), (k*130 - 405, 1920), (k*130 - 470, 1920)], fill=(226, 214, 192))
    FACTURE.draw(cv, fr, CX, 1010, .95, -5)
    tc, tt = w(9, "Coupes") - .05, w(9, "titres") - .1
    show_stamp(cv, fr, K9a, t, tc, 560, 700, -8)
    show_stamp(cv, fr, K9b, t, tt, 560, 1320, 7)
    show(cv, fr, T9a, t, w(9, "loyer") - .3, None, CX, 1560, 2)
    kw(cv, fr, KW("LIVERPOOL", "lk9t", RED, BLANC, 120), t, .02, None, CX, 380, -3)

def s9b(cv, fr, t):
    stage_fill(cv, fr, (30, 16, 24), "ls9b"); rays(cv, (CX, 1000), t, .7, 16, 1500, (110, 20, 40))
    SH_LIV.draw(cv, fr, 270, 1000, 1.45*pop_in(t, w(9, "Liverpool") - .1, .3), -4)
    SH_MU.draw(cv, fr, 810, 1000, 1.45*pop_in(t, w(9, "Manchester") - .1, .3), 4)
    VS.draw(cv, fr, CX, 1000, pop_in(t, w(9, "Manchester") + .2, .3), 0)
    kw(cv, fr, K9c, t, w(9, "le") - .05, None, CX, 540, -3)

def s9c(cv, fr, t):
    stage_fill(cv, fr, RED, "ls9c"); rays(cv, (CX, 1000), t, .6, 16, 1500, (240, 100, 110))
    tl, ta = w(9, "like"), w(9, "abonne-toi")
    kw(cv, fr, K9d, t, w(9, "Dis-le") - .05, None, CX, 460, -3)
    like_button(cv, fr, 200, 1100, .75*pop_in(t, tl - .1, .3), t, tl)
    sub_button(cv, fr, 730, 1100, t, ta - .1, ta + .25)
    kw(cv, fr, K9e, t, w(9, "d'épisodes") - .1, None, 700, 1360, 3)
    confetti(cv, fr, "lc9", t - ta, 90, 5, [BLANC, GOLD, RED_D])

def s9(cv, fr, t, T):
    shots(cv, fr, t, [(0, s9a), (w(9, "Liverpool") - .1, s9b), (w(9, "Dis-le") - .1, s9c)], d=.24)
    impact(cv, t, w(9, "Coupes"), 14); impact(cv, t, w(9, "titres"), 16); impact(cv, t, w(9, "like"), 12); impact(cv, t, w(9, "abonne-toi"), 12); drift(cv, t, T, .05)

# ------------------------------------------------------------------ scènes + bruitages
def with_bar(fn):
    def g(cv, fr, t, T):
        fn(cv, fr, t, T); chrono_bar(cv, fr, SCENES)
    return g
def SC(name, n, fn, sfx, trans=None, trans_dur=.25, pad_out=.25):
    return Scene(name, TEXTS[n-1], with_bar(fn), sfx, pad_in=PAD, pad_out=pad_out, trans=trans, trans_dur=trans_dur)
W_ = w
SCENES = [
    SC("loyer", 1, s1, [(.0, "boom", .9), (.0, "stamp", .8), (.05, "riser", .4), (W_(1, "dispute") - .05, "whoosh", .5), (W_(1, "dispute"), "stamp", .6),
                        (W_(1, "loyer"), "stamp", .9), (W_(1, "loyer"), "boom", .6), (W_(1, "Aujourd'hui") - .1, "whoosh_up", .7), (W_(1, "six"), "stamp", .6),
                        (W_(1, "six") + .1, "pop"), (W_(1, "Coupes"), "crowd_long", .9), (W_(1, "Coupes"), "sparkle"),
                        (W_(1, "L'histoire") - .1, "whoosh", .5), (W_(1, "L'histoire"), "stamp", .7), (W_(1, "minute") - .1, "tick", .9)]),
    SC("1892", 2, s2, [(.0, "boom", .5), (W_(2, "Mille"), "stamp", .6), (W_(2, "Everton"), "pop"), (W_(2, "quitte"), "whoosh", .5), (W_(2, "dispute"), "pop2"),
                       (W_(2, "Le") - .1, "whoosh", .5), (W_(2, "Le"), "stamp", .5), (W_(2, "John"), "pop"), (W_(2, "crée") - .15, "whoosh_up", .6),
                       (W_(2, "club"), "stamp", .8), (W_(2, "club"), "sparkle", .7), (W_(2, "Liverpool"), "crowd", .8)], trans="punch", trans_dur=.3),
    SC("shankly", 3, s3, [(.03, "stamp", .6), (W_(3, "titre"), "crowd", .8), (W_(3, "titre"), "stamp", .6), (W_(3, "Mais") - .1, "whoosh", .5),
                          (W_(3, "tombe") - .1, "elevator", .9), (W_(3, "division"), "boom", .7), (W_(3, "division") + .1, "groan", .6),
                          (W_(3, "En", 2) - .1, "whoosh_up", .8), (W_(3, "Bill"), "pop"), (W_(3, "et") - .1, "elevator", .5), (W_(3, "soixante-deux"), "stamp", .6),
                          (W_(3, "soixante-deux"), "crowd_long", .8)], trans="whip"),
    SC("or", 4, s4, [(.0, "boom", .5), (W_(4, "d'or") - .2, "stamp", .6), (W_(4, "Quatre", 2) - .15, "whoosh", .5)] +
                    [(W_(4, "Quatre", 2) + k*.4 - .05, snd) for k, snd in enumerate(("stamp", "stamp", "stamp", "stamp"))] +
                    [(W_(4, "Quatre", 2) + .4*k, "sparkle", .5) for k in (1, 3)] +
                    [(W_(4, "Et", 2) - .1, "whoosh", .5), (W_(4, "stade"), "crowd_long", 1.0), (W_(4, "hymne"), "stamp", .6), (W_(4, "hymne"), "sparkle")],
       trans="tear_h", trans_dur=.5),
    SC("istanbul", 5, s5, [(.0, "boom", .5), (W_(5, "mille") - .1, "stamp", .6), (W_(5, "Istanbul"), "stamp"), (W_(5, "menée") - .15, "whoosh", .5),
                           (W_(5, "zéro"), "groan", .7), (W_(5, "zéro"), "stamp", .6), (W_(5, "Liverpool") - .1, "whoosh", .5), (W_(5, "revient"), "kick", .6),
                           (W_(5, "trois", 2), "kick", .6), (W_(5, "partout"), "boom", .8), (W_(5, "partout"), "crowd_long", 1.0), (W_(5, "partout"), "stamp"),
                           (W_(5, "et") - .1, "whoosh", .5), (W_(5, "tirs"), "stamp"), (W_(5, "but"), "crowd_long", 1.0), (W_(5, "but"), "sparkle")], trans="whip"),
    SC("pause", 6, s6, [(0, "scratch", 1.0, .9), (.3, "pop"), (W_(6, "kiffes") - .1, "pop2"), (W_(6, "like"), "pop"), (W_(6, "like") + .05, "notif"),
                        (W_(6, "like") + .1, "sparkle", .6), (W_(6, "abonne-toi"), "pop2"), (W_(6, "abonne-toi") + .25, "notif"),
                        (W_(6, "Allez"), "whoosh"), (W_(6, "Allez"), "boom", .5)], trans="polaroid", pad_out=.3),
    SC("klopp", 7, s7, [(.0, "boom", .5), (W_(7, "Klopp") - .1, "stamp", .5), (W_(7, "Klopp"), "crowd", .7), (W_(7, "Deux", 2) - .15, "whoosh", .5),
                        (W_(7, "Madrid"), "stamp", .6), (W_(7, "sixième"), "stamp"), (W_(7, "sixième"), "crowd_long", .9), (W_(7, "Et") - .1, "whoosh", .5),
                        (W_(7, "vingt") - .1, "stamp", .6), (W_(7, "premier") - .1, "tick", .9), (W_(7, "trente"), "boom", .7), (W_(7, "trente"), "crowd_long", 1.0),
                        (W_(7, "trente"), "sparkle")], trans="tear_d", trans_dur=.5),
    SC("slot", 8, s8, [(.03, "stamp", .6), (W_(8, "vingtième") - .1, "riser", .6), (W_(8, "vingtième"), "boom"), (W_(8, "vingtième"), "crowd_long", 1.0),
                       (W_(8, "comme"), "pop"), (W_(8, "Manchester"), "stamp", .6), (W_(8, "Mais") - .1, "whoosh", .5), (W_(8, "Mais"), "groan", .6),
                       (W_(8, "remercié"), "stamp", .8), (W_(8, "et") - .12, "whoosh", .5), (W_(8, "Iraola"), "pop"), (W_(8, "Iraola"), "sparkle", .6)], trans="whip"),
    SC("fin", 9, s9, [(.0, "boom", .6), (.03, "stamp", .6), (W_(9, "Coupes"), "stamp", .7), (W_(9, "titres"), "stamp", .7), (W_(9, "Liverpool") - .1, "whoosh", .5),
                      (W_(9, "Liverpool"), "pop"), (W_(9, "Manchester"), "pop2"), (W_(9, "Manchester") + .2, "boom", .5), (W_(9, "Dis-le") - .1, "whoosh", .5),
                      (W_(9, "like"), "pop"), (W_(9, "like") + .05, "notif"), (W_(9, "abonne-toi"), "pop2"), (W_(9, "abonne-toi") + .25, "notif"),
                      (W_(9, "abonne-toi") + .1, "crowd", .7), (W_(9, "d'épisodes") - .1, "sparkle")], trans="punch", trans_dur=.3, pad_out=1.2),
]
SCENES[5].trans_dur = 99      # la photo figée reste épinglée pendant toute la pause
SCENES[5].post = s6_post

# ------------------------------------------------------------------ couverture
def cover(path):
    cv = background(0, TITLE); stage_fill(cv, 0, CREME, "lscov"); d = ImageDraw.Draw(cv)
    for k in range(-2, 12): d.polygon([(k*130 + 130, 0), (k*130 + 195, 0), (k*130 - 405, 1920), (k*130 - 470, 1920)], fill=(226, 214, 192))
    Label("LIVERPOOL", "lcv1", font("title", 190), BLANC, RED, padx=40, pady=6, rough=4, maxw=980).draw(cv, 0, CX, 340, 1, -3)
    Label("NÉ D'UNE DISPUTE DE LOYER…", "lcv2", font("title", 62), BLANC, NOIR, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 560, 1, 2)
    FACTURE.draw(cv, 0, CX - 40, 930, .88, -5)
    STAMP_IMP.draw(cv, 0, 800, 1130, .7, 14)
    Label("…6 FOIS CHAMPION D'EUROPE ?!", "lcv3", font("title", 62), PAL["ink"], GOLD, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 1330, 1, -2)
    for k in range(6): UCL.draw(cv, 0, 150 + k*156, 1520, .62, (-5, 4, -3, 5, -4, 3)[k])
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

# ------------------------------------------------------------------ planches de contrôle (avec transitions)
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
        p = os.path.join(out, f"lv_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", "liverpool")
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/liverpool_stills"), only=only)); sys.exit()
    if os.environ.get("LEGENDES_PROVISOIRE") and "--apercu" not in args:
        sys.exit("Minutage provisoire : pas de rendu final sans les vraies voix (--apercu pour un aperçu muet).")
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25))
