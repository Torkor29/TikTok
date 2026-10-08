"""Épisode « Légendes du foot » : l'histoire de l'AS Saint-Étienne, format court (~1 min 10).
Accroche : « Ce club a perdu une finale européenne… à cause de deux poteaux carrés. Et 37 ans plus tard, il les a rachetés ! »
sur un son de hook (scratch + impact) avant la voix ; le ballon claque sur un poteau carré dès la 1re image.
Puis : 1919, des employés des magasins Casino, le vert de l'enseigne ; Geoffroy-Guichard, le Chaudron ; 4 titres de suite (1967-70) ;
1976, Kiev renversé (0-2, 3-0 a.p.) ; pause « tu savais ? » + like ; finale de Glasgow perdue 1-0 (deux tirs sur les poteaux carrés) ;
le défilé sur les Champs-Élysées ; Platini, 10e titre en 1981 ; la chute, puis la Coupe de la Ligue 2013 ; aujourd'hui en L2, abonne-toi.

  python3 episodes/asse/asse.py output/asse --stills [3,4]
  python3 episodes/asse/asse.py output/asse --cover
  python3 episodes/asse/asse.py output/asse
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "liverpool"))
from story import *
from quiz import like_button, sub_button
from liverpool import score2, trophy_lift, shaft, stadium
import engine, foot

TITLE = "~/légendes $ ./asse"
SLUG = "asse_legende"
VOICE = [os.path.join(HERE, "voix", f"scene_{i}.mp3") for i in range(1, 12)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
ALIGN = os.path.join(HERE, "alignement.json")
PADS = [.55] + [.12]*10          # scène 1 : le son de hook passe seul avant la voix (0,55 s, skill viral)
WS, TEXTS = load_words(ALIGN)
def w(i, word, n=1, end=False):
    return PADS[i-1] + WS[i-1](word, n, end)

VERT = (0, 132, 72); VERT_D = (0, 86, 48); VERT_DD = (0, 44, 26); VERT_L = (120, 200, 140)
NOIR = (30, 28, 28); BLANC = (250, 250, 246); OR = (250, 196, 30); ROUGE = (206, 20, 40); NUIT = (16, 22, 30)
INK = PAL["ink"]

VP = Player("assep", hair=(40, 30, 24), skin=(226, 182, 146))
VP2 = Player("assep2", hair=(120, 84, 50), skin=(232, 190, 156), hair_style="mullet")
VP3 = Player("assep3", hair=(24, 20, 18), skin=(150, 104, 76))
EMP = Player("asseemp", hair=(70, 50, 36), skin=(230, 186, 150))
BAY = Player("bayp", hair=(160, 120, 70), skin=(234, 194, 160))
KIEVP = Player("kievp", hair=(60, 44, 34), skin=(232, 190, 156))
PLAT = Player("platini", hair=(70, 46, 30), skin=(228, 184, 146), hair_style="mullet")

# ------------------------------------------------------------------ décors
def green_bg(cv, fr, key, c1=VERT_D, c2=VERT, t=0.0):
    """Fond vert à grandes bandes diagonales qui glissent."""
    stage_fill(cv, fr, c1, key); d = ImageDraw.Draw(cv); off = (t*60) % 240
    for k in range(-4, 13):
        x = k*240 + off
        d.polygon([(x, 0), (x + 120, 0), (x + 120 - 700, 1920), (x - 700, 1920)], fill=c2)

def square_goal(cv, x, y, s=1.0, hit=0.0, gray=False):
    """Cage aux POTEAUX CARRÉS (Hampden Park) vue de face : poteaux à arêtes vives, face éclairée + flanc ombré.
    (x, y) = milieu de la ligne de but ; hit > 0 fait vibrer le poteau droit."""
    d = ImageDraw.Draw(cv); wd, h, p = 760*s, 420*s, 56*s
    for i in range(1, 12):           # filet
        xx = x - wd/2 + i*wd/12; d.line([(xx, y - h), (xx, y)], fill=(190, 190, 184), width=2)
    for j in range(1, 7):
        yy = y - h + j*h/7; d.line([(x - wd/2, yy), (x + wd/2, yy)], fill=(190, 190, 184), width=2)
    vib = 6*s*math.sin(hit*60)*(1 - hit) if 0 < hit < 1 else 0
    face, side = (BLANC, (176, 176, 170))
    for sx in (-1, 1):
        px = x + sx*wd/2 + (vib if sx == 1 else 0)
        d.rectangle([px - p/2, y - h, px + p/2, y], fill=face, outline=NOIR, width=4)
        d.rectangle([px + (p/2 if sx < 0 else -p/2 - p*.45), y - h, px + (p/2 + p*.45 if sx < 0 else -p/2), y], fill=side, outline=NOIR, width=3)
    d.rectangle([x - wd/2 - p/2, y - h - p, x + wd/2 + p/2 + vib, y - h], fill=face, outline=NOIR, width=4)
    d.rectangle([x - wd/2 - p/2, y - h - p*.45, x + wd/2 + p/2 + vib, y - h], fill=side)

def ball_to_post(cv, fr, t, t0, x0, y0, xp, yp, dur=.35):
    """Le ballon part de (x0, y0), frappe le poteau en (xp, yp) à t0, puis rebondit vers l'extérieur."""
    if t < t0 - dur: draw_ball(cv, fr, x0, y0, .55, 0); return
    if t < t0:
        u = ease_in_cubic(prog(t, t0 - dur, dur)); draw_ball(cv, fr, lerp(x0, xp, u), lerp(y0, yp, u), lerp(.55, .38, u), t*900); return
    u = prog(t, t0, .6)
    if u < 1: draw_ball(cv, fr, xp + 340*u, yp + 300*u*u - 120*u, .38 + .15*u, -t*900)

def bong(cv, fr, t, t0, x, y, key="bong"):
    a = pop_in(t, t0, .12)*(1 - prog(t, t0 + .5, .3))
    if a > .01:
        LBL("BOÏNG !", key, font("title", 110), OR, NOIR, padx=26, pady=4, rough=3).draw(cv, fr, x, y, a, -8)
        d = ImageDraw.Draw(cv)
        for k in range(10):
            ang = k*math.pi/5; r0, r1 = 70, 70 + 120*prog(t, t0, .3)
            d.line([(x + r0*math.cos(ang), y + 160 + r0*math.sin(ang)), (x + r1*math.cos(ang), y + 160 + r1*math.sin(ang))], fill=OR, width=8)

def cauldron(cv, x, y, s=1.0, t=0.0, a=1.0):
    """Le Chaudron : grosse marmite noire, liquide vert qui bouillonne, vapeur."""
    if a <= .01: return
    s *= a; d = ImageDraw.Draw(cv)
    d.ellipse([x - 300*s, y - 120*s, x + 300*s, y + 260*s], fill=(28, 28, 32), outline=NOIR, width=6)
    d.rectangle([x - 300*s, y - 60*s, x + 300*s, y + 60*s], fill=(28, 28, 32))
    d.ellipse([x - 300*s, y - 120*s, x + 300*s, y], fill=VERT, outline=(40, 40, 46), width=int(14*s))
    for k in range(9):               # bulles
        u = (t*1.3 + k*.37) % 1.0; bx = x + (-240 + k*60)*s; by = y - 60*s - 40*s*u
        r = (10 + 16*math.sin(u*math.pi))*s; d.ellipse([bx - r, by - r, bx + r, by + r], fill=VERT_L, outline=VERT_D, width=3)
    for sx in (-1, 1): d.ellipse([x + sx*330*s - 34*s, y - 10*s, x + sx*330*s + 34*s, y + 50*s], outline=(28, 28, 32), width=int(14*s))
    for k in range(3):               # vapeur
        u = (t*.5 + k/3) % 1.0; vx = x + (-140 + k*140)*s + 30*math.sin(t*2 + k); vy = y - 140*s - 380*s*u
        r = (50 + 60*u)*s; L = Image.new("RGBA", (int(2*r) + 2, int(2*r) + 2)); ImageDraw.Draw(L).ellipse([0, 0, 2*r, 2*r], fill=(220, 240, 226, int(120*(1 - u))))
        cv.paste(L, (int(vx - r), int(vy - r)), L)

def shopfront(cv, x, y, s=1.0, painted=0.0):
    """Petite épicerie 1919 : store à rayures (gris → vert quand painted=1)."""
    d = ImageDraw.Draw(cv); col = tuple(int(lerp(a, b, painted)) for a, b in zip((150, 146, 136), VERT))
    d.rectangle([x - 380*s, y - 520*s, x + 380*s, y], fill=(214, 200, 170), outline=NOIR, width=5)
    d.rectangle([x - 400*s, y - 600*s, x + 400*s, y - 500*s], fill=(80, 60, 44), outline=NOIR, width=5)
    d.text((x, y - 550*s), "ÉPICERIE", font=font("title", int(70*s)), fill=(240, 226, 190), anchor="mm")
    for k in range(10):
        x0 = x - 400*s + k*80*s
        d.polygon([(x0, y - 500*s), (x0 + 80*s, y - 500*s), (x0 + 90*s, y - 400*s), (x0 + 10*s, y - 400*s)], fill=col if k % 2 == 0 else BLANC, outline=NOIR)
    for sx in (-1, 1): d.rectangle([x + sx*210*s - 130*s, y - 360*s, x + sx*210*s + 130*s, y - 120*s], fill=(170, 206, 220), outline=NOIR, width=5)
    d.rectangle([x - 60*s, y - 330*s, x + 60*s, y], fill=(90, 66, 46), outline=NOIR, width=5)

def arc_triomphe(cv, x, y, s=1.0):
    d = ImageDraw.Draw(cv); c = (226, 214, 186); c2 = (176, 162, 132)
    d.rectangle([x - 300*s, y - 560*s, x + 300*s, y], fill=c, outline=NOIR, width=5)
    d.rectangle([x - 320*s, y - 640*s, x + 320*s, y - 560*s], fill=c2, outline=NOIR, width=5)
    d.rectangle([x - 110*s, y - 330*s, x + 110*s, y], fill=(60, 70, 96)); d.pieslice([x - 110*s, y - 440*s, x + 110*s, y - 220*s], 180, 360, fill=(60, 70, 96))
    for sx in (-1, 1): d.rectangle([x + sx*210*s - 40*s, y - 480*s, x + sx*210*s + 40*s, y - 360*s], fill=c2)

def flag_wave(cv, x, y, t, col=VERT, s=1.0, ph=0.0):
    d = ImageDraw.Draw(cv); d.line([(x, y), (x, y - 240*s)], fill=(90, 70, 50), width=int(8*s))
    pts = [(x + k*16*s, y - 240*s + 14*s*math.sin(t*7 + k*.6 + ph)) for k in range(11)]
    pts2 = [(px, py + 110*s) for px, py in reversed(pts)]
    d.polygon(pts + pts2, fill=col, outline=NOIR)

def stars_row(cv, n, y, t, t0, dt=.08, col=OR):
    for k in range(n):
        a = pop_in(t, t0 + k*dt, .25)
        if a > .01: draw_star(cv, CX - (n - 1)*45 + k*90, y, 34*a, 1, t*.8 + k, col)

# ------------------------------------------------------------------ labels
K1a = KW("PERDU À CAUSE…", "ak1a", BLANC, NOIR, 104); K1b = STAMP("POTEAUX CARRÉS ?!", "ak1b", ROUGE, 96)
K1c = KW("37 ANS PLUS TARD", "ak1c", INK, size=104); K1d = STAMP("RACHETÉS !", "ak1d", VERT_D, 130)
K2a = KW("1919", "ak2a", INK, size=170); T2a = TAG("des employés des magasins Casino", "at2a", PAL["paper"], size=56)
K2b = KW("LE VERT !", "ak2b", VERT, BLANC, 140); T2b = TAG("la couleur de l'enseigne", "at2b", PAL["paper"], size=56)
K3a = KW("GEOFFROY-GUICHARD", "ak3a", INK, size=96); T3a = TAG("le nom du patron", "at3a", PAL["paper"], size=56)
K3b = STAMP("LE CHAUDRON", "ak3b", VERT_D, 130)
K4a = KW("LES VERTS", "ak4a", VERT, BLANC, 140); K4b = STAMP("4 TITRES DE SUITE", "ak4b", VERT_D, 96)
K5a = KW("1976", "ak5a", INK, size=170); K5b = STAMP("REMONTADA !", "ak5b", VERT_D, 120); T5a = TAG("après prolongation", "at5a", OR, size=58)
K6a = KW("TU SAVAIS ?", "ak6a", BLANC, NOIR, 120)
K7a = KW("GLASGOW · 12 MAI 1976", "ak7a", INK, size=80); K7b = STAMP("CARRÉS…", "ak7b", ROUGE, 140)
K8a = KW("LE LENDEMAIN…", "ak8a", INK, size=110); K8b = STAMP("COMME DES CHAMPIONS", "ak8b", VERT_D, 80)
T8a = TAG("Champs-Élysées", "at8a", PAL["paper"], size=60)
K9a = KW("MICHEL PLATINI", "ak9a", INK, size=110); K9b = KW("1981", "ak9b", INK, size=170); K9c = STAMP("10e TITRE !", "ak9c", VERT_D, 120)
T9a = TAG("record de France pendant 40 ans", "at9a", OR, size=56)
K10a = KW("LA CHUTE", "ak10a", BLANC, NOIR, 130); T10a = TAG("plusieurs fois", "at10a", PAL["paper"], size=58)
K10b = KW("2013", "ak10b", INK, size=170); K10c = STAMP("COUPE DE LA LIGUE !", "ak10c", VERT_D, 96)
K11a = KW("AUJOURD'HUI", "ak11a", INK, size=110); K11b = STAMP("LE CHAUDRON ATTEND", "ak11b", VERT_D, 92)
PTAG = price_tag("VENDUS !", "aptag", OR)
SAINTE = Label("SAINT-ÉTIENNE", "asainte", font("title", 118), BLANC, VERT, padx=30, pady=10, rough=4, maxw=1040)

# ------------------------------------------------------------------ SCÈNE 1 — hook : poteaux carrés… rachetés 37 ans plus tard
GX, GY = CX, 1300
def s1a(cv, fr, t):
    stadium(cv, fr, "as1stad", t, horizon=1200, sky=NUIT, pal=[VERT, BLANC, VERT_D, (90, 170, 110), BLANC])
    beam(cv, (CX, 0), [(CX - 420, 1920), (CX + 420, 1920)], .18)
    square_goal(cv, GX, GY, 1.15, prog(t, .45, .8))
    ball_to_post(cv, fr, t, .45, CX - 120, 1820, GX + 437, GY - 300)
    bong(cv, fr, t, .45, GX + 260, 930)
    ransom_line(cv, "SAINT-ÉTIENNE", 330, 130, seed=5, fr=fr, scale=slam(t, -.12, .22))      # le mot-clé lisible dès l'image 0
    kw(cv, fr, K1a, t, w(1, "perdu") - .1, None, CX, 520, -3)
    show_stamp(cv, fr, K1b, t, w(1, "poteaux") - .05, CX, 690, 4)

def s1b(cv, fr, t):
    green_bg(cv, fr, "as1b", VERT_DD, VERT_D, t)
    rays(cv, (CX, 1100), t, .8, 16, 1500, (40, 150, 90))
    kw(cv, fr, K1c, t, w(1, "Trente-sept") - .1, None, CX, 330, -2)
    tr = w(1, "rachetés") - .05
    square_goal(cv, CX, 1240, .8*pop_in(t, w(1, "trente-sept"), .3) if t < tr else .8)
    if t > tr:
        PTAG.draw(cv, fr, CX + 300, 1120, slam(t, tr, .2), 14)
        show_stamp(cv, fr, K1d, t, tr, CX, 620, -6)
        confetti(cv, fr, "ac1", t - tr, 60, 2.5, [VERT, BLANC, OR])

def s1(cv, fr, t, T):
    shots(cv, fr, t, [(0, s1a), (w(1, "Trente-sept") - .1, s1b)], d=.24)
    impact(cv, t, .45, 22); flashes(cv, t, .45, .12, .55); punch(cv, t, .45, 1.08)        # l'impact du son de hook = le ballon sur le poteau
    impact(cv, t, w(1, "carrés"), 14); impact(cv, t, w(1, "rachetés"), 16); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 2 — 1919 : employés des magasins Casino, le vert
def s2(cv, fr, t, T):
    tv = w(2, "vert") - .1; pv = prog(t, tv, .4)
    stage_fill(cv, fr, (200, 186, 156), "as2"); d = ImageDraw.Draw(cv)
    if pv > 0:                       # la peinture verte envahit le fond
        r = 1400*ease_out_cubic(pv); d.ellipse([CX - r, 1100 - r, CX + r, 1100 + r], fill=VERT_D)
    shopfront(cv, CX, 1300, .95, pv)
    for k, x in enumerate((230, 420, 660, 850)):
        a = pop_in(t, w(2, "employés") - .1 + .08*k, .3)
        if a > .01: EMP.draw(cv, fr, x, 1820, .62*a, age=1, kit="asse" if pv > .5 else "street", mood="happy", t=t, arms=(20 + 130*(pv > .5), 20 + 130*(pv > .5)))
    if t > w(2, "foot") - .1: draw_ball(cv, fr, CX, 1780 - 200*abs(math.sin((t - w(2, "foot"))*5)), .5, t*400)
    if pv < .5: old_film(cv, fr, t, .85)
    kw(cv, fr, K2a, t, .03, None, CX, 330, -3)
    show(cv, fr, T2a, t, w(2, "employés") - .1, tv - .05, CX, 500, -2)
    kw(cv, fr, K2b, t, tv, None, CX, 500, 3)
    show(cv, fr, T2b, t, w(2, "celui") - .1, None, CX, 640, -2)
    impact(cv, t, tv + .1, 14); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 3 — Geoffroy-Guichard, le Chaudron
def s3(cv, fr, t, T):
    tc = w(3, "Chaudron") - .1
    stadium(cv, fr, "as3stad", t, horizon=1250, sky=NUIT, pal=[VERT, BLANC, VERT_D, VERT_L, (40, 40, 40)])
    kw(cv, fr, K3a, t, w(3, "Geoffroy-Guichard") - .15, None, CX, 330, -2)
    show(cv, fr, T3a, t, w(3, "patron") - .1, None, CX, 470, 2)
    if t > w(3, "supporters") - .1: flares(cv, fr, "as3fl", t, (60, 520, 1020, 1000), 12, prog(t, w(3, "supporters") - .1, .5))
    cauldron(cv, CX, 1240, 1.2, t, pop_in(t, tc, .35))
    show_stamp(cv, fr, K3b, t, tc + .05, CX, 760, -5)
    if t > tc: shake(cv, t - tc, 6)
    impact(cv, t, tc + .05, 20); flashes(cv, t, tc + .05, .1, .3); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 4 — fin des années 60 : 4 titres de suite
def s4(cv, fr, t, T):
    green_bg(cv, fr, "as4", VERT_D, VERT, t); rays(cv, (CX, 1000), t, 1.0, 16, 1500, (120, 220, 150))
    kw(cv, fr, K4a, t, w(4, "Verts") - .1, None, CX, 330, -3)
    tq = w(4, "quatre") - .05
    for k, yr in enumerate(("1967", "1968", "1969", "1970")):
        a = slam(t, tq + k*.18, .2)
        if a > 0: LBL(yr, f"ay{yr}", font("title", 84), NOIR, OR, padx=20, pady=2, rough=2).draw(cv, fr, 165 + k*250, 520, a, (-6, 4, -3, 6)[k])
    show_stamp(cv, fr, K4b, t, w(4, "champion") - .05, CX, 690, -4)
    trophy_lift(cv, fr, VP, CX, 1840, .78, "asse", t, CUP)
    for k, x in enumerate((180, 900)): VP3.draw(cv, fr, x, 1880, .5, age=1, kit="asse", mood="cheer", arms=(150, 150), t=t + k)
    if t > tq: confetti(cv, fr, "ac4", t - tq, 90, 3, [VERT, BLANC, OR])
    impact(cv, t, w(4, "écrasent"), 12); impact(cv, t, w(4, "champion"), 18); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 5 — 1976 : Kiev, 0-2 puis 3-0 a.p.
def s5a(cv, fr, t):
    stage_fill(cv, fr, (40, 46, 70), "as5a"); d = ImageDraw.Draw(cv)
    for k in range(40):              # neige de Kiev
        rnd = random.Random(k); x = rnd.uniform(0, W); y = (rnd.uniform(0, H) + t*160) % H; d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(230, 236, 246))
    kw(cv, fr, K5a, t, .03, None, CX, 330, -3)
    score2(cv, fr, CX, 760, "KIEV", "ASSE", 2, 0, "quart, aller", .85*pop_in(t, w(5, "perdent") - .1, .3))
    VP.draw(cv, fr, 330, 1820, .72, age=1, kit="asse", mood="sad", t=t, look=(0, 1))
    KIEVP.draw(cv, fr, 760, 1820, .72, age=1, kit="kiev", mood="cheer", arms=(150, 150), t=t)

def s5b(cv, fr, t):
    stadium(cv, fr, "as5stad", t, horizon=1250, sky=NUIT, pal=[VERT, BLANC, VERT_D, VERT_L, OR])
    flares(cv, fr, "as5fl", t, (60, 520, 1020, 1000), 14, 1.0)
    te = w(5, "explose") - .1; tt = w(5, "trois") - .05
    n = 0 if t < tt else min(3, 1 + int((t - tt)/.35))
    score2(cv, fr, CX, 520, "ASSE", "KIEV", n, 0, "retour · Geoffroy-Guichard", .85)
    show_stamp(cv, fr, K5b, t, w(5, "prolongation") - .1, CX, 840, -5)
    show(cv, fr, T5a, t, w(5, "après") - .05, None, CX, 990, 3)
    VP.draw(cv, fr, CX, 1840, .8, age=1, kit="asse", mood="cheer" if t > tt else "determined", arms=(150, 150) if t > tt else (25, 25), t=t)
    if t > te: shake(cv, t - te, 8)
    if t > tt: confetti(cv, fr, "ac5", t - tt, 90, 3, [VERT, BLANC, OR]); camera_flashes(cv, fr, "af5", t - tt, 1.4, 10)

def s5(cv, fr, t, T):
    shots(cv, fr, t, [(0, s5a), (w(5, "Au") - .1, s5b)], d=.24)
    impact(cv, t, w(5, "zéro"), 10)
    for k in range(3): impact(cv, t, w(5, "trois") - .05 + k*.35, 12)
    impact(cv, t, w(5, "prolongation"), 18); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 6 — pause : « tu savais pour les poteaux carrés ? » + like
def s6(cv, fr, t, T):
    green_bg(cv, fr, "as6", VERT_DD, VERT_D, t)
    kw(cv, fr, K6a, t, .05, None, CX, 920, 3)
    square_goal(cv, 760, 700, .42*pop_in(t, w(6, "poteaux") - .1, .3))
    sb = pop_in(t, w(6, "commentaire") - .2, .3)
    if sb > .01:
        speech_bubble(cv, fr, "abub6", "Je savais !", CX - 80, 1120, sb, (1, 1), 72)
        d = ImageDraw.Draw(cv); arrow(d, (CX + 120, 1150), (985, 1240), prog(t, w(6, "commentaire"), .4), OR, 14, 3, 44, .25)
    like_button(cv, fr, CX, 1420, .75*pop_in(t, w(6, "like") - .15, .3), t, w(6, "like"))
    impact(cv, t, w(6, "like"), 12); drift(cv, t, T, .03)

# ------------------------------------------------------------------ SCÈNE 7 — finale de Glasgow : 2 tirs sur les poteaux carrés, 0-1
def s7(cv, fr, t, T):
    stadium(cv, fr, "as7stad", t, horizon=1150, sky=NUIT, pal=[VERT, BLANC, ROUGE, VERT_D, BLANC])
    t1, t2 = w(7, "poteaux") - .05, w(7, "carrés") - .05
    hit = max(prog(t, t1, .8) if t < t2 else 0, prog(t, t2, .8) if t >= t2 else 0)
    square_goal(cv, CX, 1500, .95, hit)
    ball_to_post(cv, fr, t, t1, CX - 200, 1840, CX + 360, 1260)
    if t > t1 + .35: ball_to_post(cv, fr, t, t2, CX + 100, 1840, CX - 360, 1180)
    bong(cv, fr, t, t1, CX + 230, 900, "abong1"); bong(cv, fr, t, t2, CX - 230, 860, "abong2")
    kw(cv, fr, K7a, t, .05, None, CX, 300, -2)
    score2(cv, fr, CX, 560, "BAYERN", "ASSE", 0 if t < w(7, "Défaite") - .1 else 1, 0, "finale C1", .75*pop_in(t, w(7, "Bayern") - .1, .3))
    show_stamp(cv, fr, K7b, t, t2 + .1, CX, 1000, -6)
    if t > w(7, "Défaite") - .1: grayscale(cv, prog(t, w(7, "Défaite") - .1, .4)*.85)
    impact(cv, t, t1, 16); impact(cv, t, t2, 20); impact(cv, t, w(7, "Défaite"), 14); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 8 — le défilé sur les Champs-Élysées
def s8(cv, fr, t, T):
    stage_fill(cv, fr, (120, 180, 230), "as8"); d = ImageDraw.Draw(cv)
    arc_triomphe(cv, CX, 1240, .95)
    d.polygon([(0, 1240), (W, 1240), (W, H), (0, H)], fill=(120, 116, 112))
    for k in range(6): d.rectangle([CX - 12, 1300 + k*110, CX + 12, 1360 + k*110], fill=BLANC)
    tc = w(8, "champions") - .1; td = w(8, "défilent") - .1
    for k in range(5):                # foule + drapeaux verts sur les côtés
        flag_wave(cv, 70 + k*55, 1700 - (k % 2)*60, t, VERT if k % 2 else BLANC, .9, k)
        flag_wave(cv, 790 + k*55, 1700 - (k % 2)*60, t, BLANC if k % 2 else VERT, .9, k + 3)
    xoff = 200*(1 - ease_out_cubic(prog(t, td, 1.2)))
    for k, (x, P) in enumerate(((CX - 170, VP), (CX, VP2), (CX + 170, VP3))):
        P.draw(cv, fr, x, 1860 + xoff, .62, age=1, kit="asse", mood="cheer", arms=(150 + 10*math.sin(t*5 + k), 150), t=t + k)
    kw(cv, fr, K8a, t, .05, None, CX, 330, -3)
    show(cv, fr, T8a, t, w(8, "Champs-Élysées") - .1, None, CX, 480, 2)
    show_stamp(cv, fr, K8b, t, tc, CX, 640, -4)
    confetti(cv, fr, "ac8", t - td, 110, 4, [VERT, BLANC, OR])
    impact(cv, t, tc + .1, 16); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 9 — Platini, 10e titre en 1981, record pendant 40 ans
JB = jersey_back("asse", "PLATINI", 10, "ajb10")
def s9a(cv, fr, t):
    green_bg(cv, fr, "as9a", VERT_D, VERT, t); rays(cv, (CX, 1000), t, .6, 16, 1500, (60, 170, 100))
    kw(cv, fr, K9a, t, w(9, "Michel") - .1, None, CX, 330, -2)
    JB.draw(cv, fr, CX, 1000, 1.25*slam(t, w(9, "Michel") - .1, .25), 3*math.sin(t*2))

def s9b(cv, fr, t):
    stage_fill(cv, fr, VERT_DD, "as9b"); rays(cv, (CX, 1000), t, 1.0, 16, 1500, (230, 190, 70))
    kw(cv, fr, K9b, t, w(9, "quatre-vingt-un") - .1, None, CX, 330, -3)
    td = w(9, "dixième") - .1
    for k in range(10):
        a = pop_in(t, td + k*.06, .2)
        if a > .01: draw_star(cv, 140 + (k % 5)*200, 500 + (k // 5)*120, 46*a, 1, t + k, OR)
    show_stamp(cv, fr, K9c, t, w(9, "titre") - .05, CX, 760, -4)
    show(cv, fr, T9a, t, w(9, "record") - .05, None, CX, 900, 2)
    trophy_lift(cv, fr, PLAT, CX, 1850, .7, "asse", t, CUP)
    if t > td: confetti(cv, fr, "ac9", t - td, 80, 3, [VERT, BLANC, OR])

def s9(cv, fr, t, T):
    shots(cv, fr, t, [(0, s9a), (w(9, "En") - .1, s9b)], d=.24)
    impact(cv, t, w(9, "Platini"), 14); impact(cv, t, w(9, "titre"), 18); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 10 — la chute (D2), puis la Coupe de la Ligue 2013
def s10a(cv, fr, t):
    tl = w(10, "deuxième") - .1
    stage_fill(cv, fr, (40, 40, 46), "as10a")
    if t > tl: shaft(cv, fr, t, 0, "as10shaft")
    VP.draw(cv, fr, CX, 1740, 1.0, age=1, kit="asse", mood="surprised" if t < tl else "sad", t=t, look=(0, 1) if t > tl else (0, 0))
    floor_panel(cv, fr, CX, 700, "D1" if t < tl else "D2", t, True, 1.7, 1)
    kw(cv, fr, K10a, t, .03, None, CX, 330, -3)
    show(cv, fr, T10a, t, w(10, "plusieurs") - .1, None, CX, 1000, 3)
    elevator_drop(cv, t, w(10, "chute"), .6)
    if t > w(10, "chute") + .6:      # après la chute : on redessine la cage en D2
        shaft(cv, fr, t, 0, "as10shaft")
        VP.draw(cv, fr, CX, 1740, 1.0, age=1, kit="asse", mood="sad", t=t, look=(0, 1))
        floor_panel(cv, fr, CX, 700, "D2", t, True, 1.7, 1)
        kw(cv, fr, K10a, t, .03, None, CX, 330, -3)
        show(cv, fr, T10a, t, w(10, "plusieurs") - .1, None, CX, 1000, 3)
    grayscale(cv, .6)

def s10b(cv, fr, t):
    green_bg(cv, fr, "as10b", VERT_D, VERT, t); rays(cv, (CX, 1000), t, 1.0, 16, 1500, (230, 190, 70))
    tc = w(10, "trophée") - .05
    kw(cv, fr, K10b, t, w(10, "deux") - .1, None, CX, 330, -3)
    show_stamp(cv, fr, K10c, t, w(10, "Coupe") - .05, CX, 520, 4)
    trophy_lift(cv, fr, VP3, CX, 1840, .82, "asse", t, CUP)
    if t > tc: confetti(cv, fr, "ac10", t - tc, 110, 3, [VERT, BLANC, OR]); camera_flashes(cv, fr, "af10", t - tc, 1.2, 8)

def s10(cv, fr, t, T):
    shots(cv, fr, t, [(0, s10a), (w(10, "Mais") - .1, s10b)], d=.24)
    impact(cv, t, w(10, "deuxième"), 18); impact(cv, t, w(10, "trophée"), 18); flashes(cv, t, w(10, "Coupe"), .1, .4); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 11 — aujourd'hui en L2, le Chaudron attend ; abonne-toi
def s11(cv, fr, t, T):
    stadium(cv, fr, "as11stad", t, horizon=1250, sky=NUIT, pal=[VERT, BLANC, VERT_D, VERT_L, OR])
    flares(cv, fr, "as11fl", t, (60, 520, 1020, 1000), 10, .8)
    ta = w(11, "Abonne-toi")
    kw(cv, fr, K11a, t, .05, None, CX, 300, -2)
    floor_panel(cv, fr, CX, 560, "L2", t, False, 1.2, pop_in(t, w(11, "Ligue") - .1, .3))
    show_stamp(cv, fr, K11b, t, w(11, "Chaudron") - .05, CX, 800, -4)
    sub_button(cv, fr, CX, 1060, t, ta - .1, ta + .25)
    sb = pop_in(t, w(11, "commentaire") - .1, .3)
    if sb > .01: speech_bubble(cv, fr, "abub11", "Quel club après ?", CX - 60, 1290, sb, (1, 1), 64)
    VP.draw(cv, fr, 200, 1880, .55, age=1, kit="asse", mood="determined", arms=(30, 30), t=t)
    confetti(cv, fr, "ac11", t - ta, 90, 5, [VERT, BLANC, OR])
    impact(cv, t, w(11, "Chaudron"), 12); impact(cv, t, ta, 12); drift(cv, t, T, .04)

# ------------------------------------------------------------------ scènes + bruitages
def SC(name, n, fn, sfx, trans=None, trans_dur=.25, pad_out=.25):
    return Scene(name, TEXTS[n-1], fn, sfx, pad_in=PADS[n-1], pad_out=pad_out, trans=trans, trans_dur=trans_dur)
W_ = w
SCENES = [
    SC("hook", 1, s1, [(.0, "hook", 1.3), (.45, "bar", .9), (W_(1, "perdu"), "pop", .5), (W_(1, "poteaux"), "stamp", .8), (W_(1, "Trente-sept") - .1, "whoosh", .5),
                       (W_(1, "trente-sept"), "pop2", .6), (W_(1, "rachetés"), "cash", .7), (W_(1, "rachetés"), "stamp", .8),
                       (W_(1, "rachetés") + .1, "crowd", .6)]),
    SC("1919", 2, s2, [(.0, "rip", .5), (.03, "stamp", .6), (W_(2, "employés") - .1, "pop", .5), (W_(2, "foot"), "kick", .5),
                       (W_(2, "vert") - .1, "whoosh_up", .6), (W_(2, "vert"), "stamp", .8)], trans="tear_v", trans_dur=.45),
    SC("chaudron", 3, s3, [(.0, "crowd_long", .6), (W_(3, "Geoffroy-Guichard") - .1, "stamp", .6), (W_(3, "supporters"), "crowd", .7),
                           (W_(3, "Chaudron"), "boom", .9), (W_(3, "Chaudron"), "stamp", .8), (W_(3, "Chaudron"), "crowd_long", 1.0)], trans="whip"),
    SC("4_titres", 4, s4, [(.0, "whoosh", .5), (W_(4, "Verts"), "stamp", .6)] + [(W_(4, "quatre") - .05 + k*.18, "pop", .5) for k in range(4)]
       + [(W_(4, "champion"), "stamp", .9), (W_(4, "champion"), "crowd_long", .9), (W_(4, "champion"), "sparkle", .6)], trans="punch", trans_dur=.3),
    SC("kiev", 5, s5, [(.0, "rip", .5), (.03, "stamp", .6), (W_(5, "perdent"), "groan", .6), (W_(5, "Au") - .1, "whoosh", .5),
                       (W_(5, "explose"), "crowd_long", 1.0)] + [(W_(5, "trois") - .05 + k*.35, "kick", .6) for k in range(3)]
       + [(W_(5, "prolongation"), "stamp", .9), (W_(5, "prolongation"), "boom", .7)], trans="tear_h", trans_dur=.5),
    SC("pause", 6, s6, [(.0, "scratch", .8), (W_(6, "poteaux"), "pop", .5), (W_(6, "commentaire"), "notif", .9), (W_(6, "like"), "pop2", .7),
                        (W_(6, "like") + .05, "heart", .6)], trans="polaroid", trans_dur=99, pad_out=.3),
    SC("glasgow", 7, s7, [(.0, "whoosh", .5), (.05, "stamp", .5), (W_(7, "Bayern"), "pop", .5), (W_(7, "poteaux") - .05, "bar", 1.0),
                          (W_(7, "carrés") - .05, "bar", 1.0), (W_(7, "carrés") + .1, "gasp", .8), (W_(7, "Défaite"), "groan", .8)], trans="punch", trans_dur=.3),
    SC("champs", 8, s8, [(.0, "crowd_long", .8), (.05, "stamp", .5), (W_(8, "défilent"), "horn", .6), (W_(8, "Champs-Élysées"), "pop", .5),
                         (W_(8, "champions"), "stamp", .9), (W_(8, "champions"), "crowd_long", 1.0)], trans="tear_d", trans_dur=.5),
    SC("platini", 9, s9, [(.0, "whoosh", .5), (W_(9, "Michel"), "stamp", .6), (W_(9, "Platini"), "boom", .6), (W_(9, "En") - .1, "whoosh", .5)]
       + [(W_(9, "dixième") - .1 + k*.06, "pop", .3) for k in range(0, 10, 2)] + [(W_(9, "titre"), "stamp", .9), (W_(9, "titre"), "crowd_long", .9)],
       trans="whip"),
    SC("chute_2013", 10, s10, [(.03, "stamp", .5), (W_(10, "chute"), "elevator", .9), (W_(10, "deuxième"), "boom", .7), (W_(10, "Mais") - .1, "whoosh_up", .6),
                               (W_(10, "deux"), "stamp", .6), (W_(10, "Coupe"), "stamp", 1.0), (W_(10, "trophée"), "crowd_long", 1.0), (W_(10, "trophée"), "sparkle", .7)],
       trans="tear_v", trans_dur=.45),
    SC("fin", 11, s11, [(.0, "crowd_long", .6), (.05, "stamp", .5), (W_(11, "Ligue"), "pop", .5), (W_(11, "Chaudron"), "stamp", .8),
                        (W_(11, "Abonne-toi"), "pop2", .7), (W_(11, "Abonne-toi") + .25, "notif", .8), (W_(11, "commentaire"), "pop", .6),
                        (W_(11, "commentaire") + .05, "notif", .7)], trans="whip", pad_out=1.3),
]

# ------------------------------------------------------------------ couverture : « PERDU À CAUSE DE POTEAUX CARRÉS ?! »
def cover(path):
    cv = background(0, TITLE)
    stadium(cv, 0, "acovstad", 0, horizon=1200, sky=NUIT, pal=[VERT, BLANC, VERT_D, VERT_L, BLANC])
    beam(cv, (CX, 0), [(CX - 420, 1920), (CX + 420, 1920)], .2)
    ransom_line(cv, "SAINT-ÉTIENNE", 330, 130, seed=5, fr=0)
    Label("A PERDU UNE FINALE EUROPÉENNE…", "acv2", font("title", 64), BLANC, NOIR, maxw=1000, padx=30, pady=10, rough=5).draw(cv, 0, CX, 520, 1, -2)
    Label("…À CAUSE DE POTEAUX CARRÉS ?!", "acv3", font("title", 76), NOIR, OR, maxw=1000, padx=30, pady=10, rough=5).draw(cv, 0, CX, 760, 1, 2)
    square_goal(cv, CX, 1420, 1.0)
    draw_ball(cv, 0, CX + 330, 1150, .45, 20)
    LBL("BOÏNG !", "acvbong", font("title", 110), OR, NOIR, padx=26, pady=4, rough=3).draw(cv, 0, CX + 200, 975, 1, -8)
    VP.draw(cv, 0, CX - 230, 1700, .62, age=1, kit="asse", mood="surprised", arms=(150, 150), t=0)
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
            finish(cv, TITLE); ims.append(cv.resize((300, 533)))
        sheet = Image.new("RGB", (300*len(ims), 575), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            sheet.paste(im, (k*300, 42)); dd.text((k*300+8, 6), f"S{i+1} {fracs[k]*sc.T:.1f}/{sc.T:.1f}", font=font("mono", 24), fill=(230, 230, 230))
        p = os.path.join(out, f"as_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", "asse")
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/asse_stills"), only=only)); sys.exit()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25, limit=True))
