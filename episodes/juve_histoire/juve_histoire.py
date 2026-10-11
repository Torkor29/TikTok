"""L'histoire de la Juventus (~1 min 12) — format « caméra dans la maquette » (engine/diorama.py) + Lasseter.
Structure rétention : hook (Serie B -> 9 titres) / QUESTION ouverte (pourquoi noir et blanc ?) / histoire chronologique /
réponse à la question en fin de vidéo / CTA commentaire + abonnement. Frise 1897 -> 2025 fixe en haut.

  python3 episodes/juve_histoire/juve_histoire.py output/juve_histoire --stills [2,3]
  python3 episodes/juve_histoire/juve_histoire.py output/juve_histoire --cover
  python3 episodes/juve_histoire/juve_histoire.py output/juve_histoire
"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from story import *
from quiz import sub_button
from lasseter import ease, ease_out, settle, stagger, arc, squash, draw_sxy, enter, stamp, hop, wave
from diorama import Diorama, Frise, cut_punch, K, note
import engine

TITLE = "~/légendes $ ./juve"
SLUG = "juve_histoire"
N = 12
VOICE = [os.path.join(HERE, "voix", f"scene_{i}.mp3") for i in range(1, N + 1)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
PADS = [.45] + [.1]*(N - 1)
WS, TEXTS = load_words(os.path.join(HERE, "alignement.json"))
def w(i, word, n=1, end=False):
    return PADS[i-1] + WS[i-1](word, n, end)

NOIR = (24, 22, 24); BLANC = (250, 250, 246); GOLD = (250, 196, 30); ROUGE = (206, 30, 46); VERT = (40, 150, 80)
ROSE = (240, 140, 180); GRIS = (90, 90, 96)
D = Diorama(os.path.join(HERE, "img"))
cam = D.cam
FR = Frise(1897, 2025, (1897, 1930, 1960, 1990, 2025), "JUVE", NOIR, NOIR, BLANC)
frise = FR.draw

# ------------------------------------------------------------------ 1 — hook : Serie B 2006 -> 9 titres d'affilée
def s1(cv, fr, t, T):
    ts = w(1, "Six") - .12
    if t < ts:
        cam(cv, "calciopoli", t, [(0, (.8, .7, 1.7)), (ts, (.75, .6, 1.25))], gray=.5)
        enter(cv, fr, K("2006", "j1a", NOIR, size=150), t, .05, CX, 620, -3, frm=(-500, -100), d=.3)
        stamp(cv, fr, K("DEUXIÈME DIVISION", "j1b", ROUGE, size=86), t, w(1, "deuxième") - .1, CX, 1150, -6, 1)
    else:
        cam(cv, "neuf", t, [(ts, (.5, .5, 1.5)), (T, (.5, .5, 1.05))]); cut_punch(cv, t, ts, .08)
        tn = w(1, "neuf") - .05
        if t > tn:
            u = ease_out(prog(t, tn, .3))
            K("× 9", "j1x", GOLD, NOIR, 230).draw(cv, fr, CX, 760, lerp(.3, 1, u)*(1 + .2*settle(t, tn + .3, .5)), -5)
        stamp(cv, fr, K("TITRES D'AFFILÉE", "j1c", NOIR, size=88), t, w(1, "daffil") - .2, CX, 1010, 3, 1)
        enter(cv, fr, K("L'HISTOIRE DE LA JUVENTUS", "j1d", BLANC, NOIR, 74), t, w(1, "lhistoire") - .1, CX, 1500, -2, frm=(0, 400), d=.35)
        if t > tn: confetti(cv, fr, "jc1", t - tn, 70, 3, [BLANC, NOIR, GOLD])
    frise(cv, fr, t, 2006, 2020, ts)

# ------------------------------------------------------------------ 2 — la QUESTION (boucle ouverte)
def s2(cv, fr, t, T):
    cam(cv, "neuf", t, [(0, (.2, .3, 1.8)), (T, (.8, .3, 1.8))]); tint(cv, .62)
    enter(cv, fr, K("QUESTION", "j2a", GOLD, NOIR, 100), t, w(2, "question") - .1, CX, 560, -4, frm=(0, -300), d=.3, h=0)
    tq = w(2, "pourquoi") - .1
    if t > tq:                                     # gros « ? » qui saute (anticipation + écrasement)
        dy, sx, sy = hop(t, tq + .15, 120, .45)
        draw_sxy(cv, fr, K("?", "j2q", BLANC, NOIR, 340), CX, 980 + dy, sx, sy, 6*wave(t, 0, 1, .8))
    enter(cv, fr, K("POURQUOI NOIR ET BLANC ?", "j2b", BLANC, NOIR, 76), t, w(2, "noir") - .15, CX, 1290, 2, frm=(500, 0), d=.3)
    stamp(cv, fr, note("réponse à la fin…", "j2c", 62, GOLD), t, w(2, "Reste") - .05, CX, 1500, -4, 1)
    frise(cv, fr, t, 2020, 2020, 99)

# ------------------------------------------------------------------ 3 — 1897, Turin, des lycéens
def s3(cv, fr, t, T):
    cam(cv, "1897", t, [(0, (.75, .4, 1.5)), (w(3, "lycéens"), (.4, .55, 1.3)), (T, (.3, .55, 1.15))], sep=.45)
    old_film(cv, fr, t, .5)
    enter(cv, fr, K("1897 · TURIN", "j3a", NOIR, size=110), t, .05, CX, 600, -3, frm=(-600, 0), d=.32)
    enter(cv, fr, note("des lycéens fondent le club", "j3b", 58), t, w(3, "lycéens") - .1, CX, 1180, 2, frm=(0, 400), d=.3)
    tj = w(3, "jeunesse") - .15
    if t > w(3, "Juventus") - .1:
        K("JUVENTUS", "j3c", BLANC, NOIR, 110).draw(cv, fr, CX, 1380, 1 + .15*settle(t, w(3, "Juventus"), .6), -2)
    stamp(cv, fr, K("= « JEUNESSE »", "j3d", GOLD, NOIR, 80), t, tj, CX + 60, 1530, 4, .95)
    frise(cv, fr, t, 2020, 1897, .05, .6)

# ------------------------------------------------------------------ 4 — 1923, famille Agnelli (Fiat)
def s4(cv, fr, t, T):
    cam(cv, "agnelli", t, [(0, (.75, .5, 1.5)), (w(4, "Agnelli"), (.45, .45, 1.35)), (T, (.35, .45, 1.15))], sep=.2)
    enter(cv, fr, K("1923", "j4a", NOIR, size=150), t, .05, CX, 600, -3, frm=(600, 0), d=.3)
    stamp(cv, fr, K("FAMILLE AGNELLI", "j4b", BLANC, NOIR, 92), t, w(4, "Agnelli") - .1, CX, 1180, -4, 1)
    enter(cv, fr, note("les patrons de Fiat", "j4c", 58, GOLD), t, w(4, "Fiat") - .15, CX, 1330, 3, frm=(-500, 100), d=.3)
    tc = w(4, "Cent") - .1
    if t > tc:
        n = counter(0, 100, prog(t, tc, .8))
        K(f"{n} ANS", "j4n" + n, GOLD, NOIR, 140).draw(cv, fr, CX, 1560, 1 + .2*settle(t, tc + .8, .5), -3)
    frise(cv, fr, t, 1897, 1923, .05, .5)

# ------------------------------------------------------------------ 5 — années 30 : 5 titres de suite, la Vieille Dame
def s5(cv, fr, t, T):
    cam(cv, "annees30", t, [(0, (.3, .55, 1.6)), (T, (.6, .5, 1.2))], sep=.35)
    enter(cv, fr, K("ANNÉES 30", "j5a", NOIR, size=120), t, .05, CX, 600, -3, frm=(-600, 0), d=.3)
    tc = w(5, "cinq") - .05
    for k in range(5):                              # 5 titres : chaque étoile saute à son tour
        t0 = tc + stagger(k, .12)
        if t > t0:
            dy, sx, sy = hop(t, t0, 80, .35)
            draw_star(cv, 220 + k*160, 1000 + dy, 60*(1 + .25*settle(t, t0 + .35, .5)), 1, k, GOLD)
    if t > tc + .3: K("5 TITRES DE SUITE", "j5b", BLANC, NOIR, 88).draw(cv, fr, CX, 1160, 1, 2)
    stamp(cv, fr, K("« LA VIEILLE DAME »", "j5c", GOLD, NOIR, 88), t, w(5, "Vieille") - .1, CX, 1450, -4, 1)
    frise(cv, fr, t, 1923, 1935, .05, .5, "1931-35")

# ------------------------------------------------------------------ 6 — Platini, 3 Ballons d'or d'affilée
def s6(cv, fr, t, T):
    cam(cv, "platini", t, [(0, (.5, .8, 1.7)), (w(6, "trois"), (.5, .45, 1.3)), (T, (.5, .35, 1.1))])
    stamp(cv, fr, K("UN FRANÇAIS", "j6a", (16, 44, 110), size=90), t, w(6, "Français") - .1, CX, 600, -4, 1)
    enter(cv, fr, K("MICHEL PLATINI", "j6b", BLANC, NOIR, 100), t, w(6, "Michel") - .1, CX, 760, 2, frm=(0, -400), d=.3, h=0)
    tb = w(6, "trois") - .05
    for k, yr in enumerate((1983, 1984, 1985)):
        t0 = tb + stagger(k, .18)
        if t > t0:
            dy, sx, sy = hop(t, t0, 140, .45)
            draw_ballon_or(cv, fr, 250 + k*290, 1250 + dy, .7)
            K(str(yr), f"j6y{yr}", GOLD, NOIR, 52).draw(cv, fr, 250 + k*290, 1440, 1, (k - 1)*4)
    stamp(cv, fr, K("3 BALLONS D'OR", "j6c", GOLD, NOIR, 96), t, w(6, "daffil") - .15, CX, 1620, -3, 1)
    frise(cv, fr, t, 1935, 1985, .05, .6, "1982-87")

# ------------------------------------------------------------------ 7 — 1996 C1… mais 7 finales perdues
def s7(cv, fr, t, T):
    tm = w(7, "Mais") - .1
    cam(cv, "1996", t, [(0, (.5, .7, 1.6)), (tm, (.5, .3, 1.25)), (T, (.5, .35, 1.1))], gray=.75 if t > tm + .2 else 0)
    enter(cv, fr, K("1996", "j7a", NOIR, size=150), t, .05, CX, 580, -3, frm=(-600, 0), d=.3)
    stamp(cv, fr, K("LIGUE DES CHAMPIONS !", "j7b", GOLD, NOIR, 84), t, w(7, "Ligue") - .1, CX, 760, 3, 1)
    if t > w(7, "Ligue"): camera_flashes(cv, fr, "jf7", t - w(7, "Ligue"), 1.5, 8)
    if t > tm:
        tint(cv, .35)
        ts7 = w(7, "sept") - .05
        for k, yr in enumerate((1973, 1983, 1997, 1998, 2003, 2015, 2017)):     # 7 finales perdues : croix rouges
            t0 = ts7 + stagger(k, .09)
            x = 150 + (k % 4)*260; y = 1080 + (k//4)*170
            if t > t0:
                K(str(yr), f"j7y{yr}", BLANC, NOIR, 56).draw(cv, fr, x, y, 1, 0)
                stamp(cv, fr, K("X", "j7x", ROUGE, BLANC, 56, 2), t, t0 + .08, x + 70, y - 30, -8, .7, False)
        stamp(cv, fr, K("7 FINALES PERDUES : RECORD", "j7c", ROUGE, size=72), t, w(7, "record") - .1, CX, 1520, -3, 1)
    frise(cv, fr, t, 1985, 1996, .05, .5)

# ------------------------------------------------------------------ 8 — 2006 Calciopoli : titres retirés, Serie B
def s8(cv, fr, t, T):
    cam(cv, "calciopoli", t, [(0, (.2, .4, 1.5)), (w(8, "titres"), (.6, .5, 1.3)), (w(8, "Serie"), (.85, .7, 1.5)), (T, (.85, .7, 1.7))])
    tc = w(8, "Calciopoli") - .1
    if tc < t < tc + .45: flash(cv, .85*(1 - prog(t, tc, .25)), (235, 235, 255)); shake(cv, t - tc, 18*(1 - prog(t, tc, .45)))
    enter(cv, fr, K("2006", "j8a", NOIR, size=140), t, .05, CX, 560, -3, frm=(600, 0), d=.3)
    stamp(cv, fr, K("CALCIOPOLI", "j8b", ROUGE, size=120), t, tc, CX, 760, -5, 1)
    stamp(cv, fr, K("2 TITRES RETIRÉS", "j8c", BLANC, NOIR, 84), t, w(8, "titres") - .1, CX, 1150, 4, 1)
    stamp(cv, fr, K("SERIE B", "j8d", ROUGE, size=170), t, w(8, "Serie") - .05, CX, 1400, -6, 1.1)
    enter(cv, fr, note("1re fois de son histoire", "j8e", 56, GOLD), t, w(8, "première") - .1, CX, 1620, 2, frm=(0, 300), d=.3)
    if t > w(8, "Serie"): siren_lights(cv, t, .18)
    frise(cv, fr, t, 1996, 2006, .05, .5)

# ------------------------------------------------------------------ 9 — les fidèles restent, remontée 2007
NAMES9 = [("Buffon", "BUFFON"), ("Del", "DEL PIERO"), ("Ned", "NEDVED"), ("Trezeguet", "TREZEGUET")]
def s9(cv, fr, t, T):
    cam(cv, "fideles", t, [(0, (.5, .3, 1.5)), (T, (.5, .55, 1.15))])
    pos = [(290, 760), (790, 900), (290, 1040), (790, 1180)]
    for k, (wd, nm) in enumerate(NAMES9):
        x, y = pos[k]
        enter(cv, fr, K(nm, f"j9n{k}", BLANC, NOIR, 72), t, w(9, wd) - .12, x, y, (-4, 3, 2, -3)[k], frm=(-500 if x < CX else 500, 100), d=.3)
    stamp(cv, fr, K("ILS RESTENT", "j9a", GOLD, NOIR, 100), t, w(9, "restent") - .1, CX, 1400, -4, 1)
    tr = w(9, "remonte") - .15
    if t > tr:
        u = ease_out(prog(t, tr, .4)); y = lerp(1900, 1600, u)
        K("↑ 2007 : RETOUR EN SERIE A", "j9b", VERT, size=70).draw(cv, fr, CX, y, 1 + .15*settle(t, tr + .4, .5), 2)
    frise(cv, fr, t, 2006, 2007, w(9, "remonte") - .1, .45)

# ------------------------------------------------------------------ 10 — 9 titres d'affilée, puis Ronaldo
def s10(cv, fr, t, T):
    tr = w(10, "Cristiano") - .4
    if t < tr:
        cam(cv, "neuf", t, [(0, (.1, .5, 1.6)), (tr, (.9, .5, 1.6))])
        t1, t2 = w(10, "deux") - .05, w(10, "vingt") + .1
        for k in range(9):
            tk = lerp(t1, t2, k/8)
            if t > tk:
                dy, sx, sy = hop(t, tk, 60, .3)
                K(str(2012 + k), f"j10y{k}", GOLD, NOIR, 48).draw(cv, fr, 120 + (k % 5)*210, 1100 + (k//5)*120 + dy, 1, (k % 2)*4 - 2)
        if t > t2:
            u = ease_out(prog(t, t2, .3)); K("× 9", "j10x", BLANC, NOIR, 200).draw(cv, fr, CX, 640, lerp(.3, 1, u)*(1 + .2*settle(t, t2 + .3, .5)), -4)
        stamp(cv, fr, note("record des 5 grands championnats", "j10r", 54, GOLD), t, w(10, "record") - .1, CX, 1480, -2, 1)
    else:
        cam(cv, "ronaldo", t, [(tr, (.5, .6, 1.6)), (T, (.5, .4, 1.1))]); cut_punch(cv, t, tr, .1)
        camera_flashes(cv, fr, "jf10", t - tr, 2.5, 14)
        enter(cv, fr, K("2018", "j10a", NOIR, size=130), t, tr + .05, CX, 600, -3, frm=(-600, 0), d=.3)
        stamp(cv, fr, K("CRISTIANO RONALDO", "j10b", BLANC, NOIR, 88), t, w(10, "Cristiano") - .05, CX, 1380, -3, 1)
    frise(cv, fr, t, 2007, 2020 if t < tr else 2018, .05 if t < tr else tr, .6, "2012-20" if t < tr else None)

# ------------------------------------------------------------------ 11 — RÉPONSE : la Juve jouait en rose
def s11(cv, fr, t, T):
    tn = w(11, "Notts") - .2
    cam(cv, "rose", t, [(0, (.3, .5, 1.6)), (w(11, "Anglais"), (.35, .5, 1.25)), (tn, (.8, .7, 1.5)), (T, (.82, .75, 1.7))], sep=.15)
    stamp(cv, fr, K("LA RÉPONSE", "j11a", GOLD, NOIR, 96), t, .05, CX, 560, -4, 1)
    stamp(cv, fr, K("EN ROSE !", "j11b", ROSE, NOIR, 150), t, w(11, "rose") - .05, CX, 800, 5, 1.05)
    enter(cv, fr, note("les maillots déteignaient…", "j11c", 58), t, w(11, "maillots") - .1, CX, 1180, -2, frm=(-500, 100), d=.3)
    enter(cv, fr, K("1903 · un Anglais", "j11d", BLANC, NOIR, 70), t, w(11, "Anglais") - .1, CX, 1330, 2, frm=(500, 100), d=.3)
    stamp(cv, fr, K("NOTTS COUNTY", "j11e", BLANC, NOIR, 120), t, tn + .1, CX, 1560, -4, 1)
    frise(cv, fr, t, 2018, 1903, .05, .6)

# ------------------------------------------------------------------ 12 — CTA : question + abonnement
def s12(cv, fr, t, T):
    cam(cv, "1996", t, [(0, (.5, .35, 1.4)), (T, (.5, .35, 1.15))]); tint(cv, .45)
    enter(cv, fr, K("PLUS GRAND CLUB", "j12a", BLANC, NOIR, 100), t, .05, CX, 600, -3, frm=(0, -300), d=.3, h=0)
    enter(cv, fr, K("D'ITALIE ?", "j12b", GOLD, NOIR, 120), t, w(12, "dItalie") - .15, CX, 760, 3, frm=(0, -300), d=.3, h=0)
    tc = w(12, "commentaire") - .15
    if t > tc:
        speech_bubble(cv, fr, "j12c", "Évidemment !", 330, 1050, ease_out(prog(t, tc, .3)), (1, 1), 62)
        speech_bubble(cv, fr, "j12d", "L'Inter ou le Milan…", 730, 1210, ease_out(prog(t, tc + .25, .3)), (-1, 1), 56)
    ta = w(12, "abonne")
    sub_button(cv, fr, CX, 1480, t, ta - .1, ta + .25)
    frise(cv, fr, t, 1897, 2025, .05, 1.2, "1897-2025")

# ------------------------------------------------------------------ scènes + bruitages
def SC(name, n, fn, sfx, trans=None, trans_dur=.25, pad_out=.2):
    return Scene(name, TEXTS[n-1], fn, sfx, pad_in=PADS[n-1], pad_out=pad_out, trans=trans, trans_dur=trans_dur)
SCENES = [
    SC("hook", 1, s1, [(.0, "braam", 1.0), (.05, "gavel", .8), (w(1, "deuxième"), "stamp", .9), (w(1, "deuxième") + .1, "boo", .5),
                       (w(1, "Six") - .15, "whoosh_up", .7), (w(1, "neuf"), "fanfare", .8), (w(1, "neuf") + .1, "goal_roar", .7),
                       (w(1, "daffil") - .2, "stamp", .8)]),
    SC("question", 2, s2, [(.0, "whoosh", .5), (w(2, "question") - .1, "pop2", .6), (w(2, "pourquoi"), "drumroll", .7), (w(2, "Reste"), "tictac", .5)], trans="punch", trans_dur=.3),
    SC("1897", 3, s3, [(.0, "projector", .8), (w(3, "lycéens"), "paper", .6), (w(3, "Juventus"), "sparkle", .6), (w(3, "jeunesse") - .15, "stamp", .8)], trans="tear_v", trans_dur=.4),
    SC("agnelli", 4, s4, [(.0, "oldcar", .8), (w(4, "Agnelli") - .1, "stamp", .9), (w(4, "Fiat"), "typewriter", .4), (w(4, "Cent"), "coin", .5)], trans="whip"),
    SC("30s", 5, s5, [(.0, "radio", .8)] + [(w(5, "cinq") - .05 + stagger(k, .12), "pop", .5) for k in range(5)] + [(w(5, "Vieille") - .1, "stamp", .9)], trans="tear_h", trans_dur=.4),
    SC("platini", 6, s6, [(.0, "crowd_long", .5), (w(6, "Français") - .1, "stamp", .8)] + [(w(6, "trois") - .05 + stagger(k, .18), "sparkle", .6) for k in range(3)]
       + [(w(6, "daffil") - .15, "fanfare", .7)], trans="whip"),
    SC("1996", 7, s7, [(.0, "goal_roar", .7), (w(7, "Ligue") - .1, "champagne", .7), (w(7, "Ligue"), "camera", .7), (w(7, "Mais") - .1, "scratch", .8)]
       + [(w(7, "sept") - .05 + stagger(k, .09) + .08, "buzzer", .25) for k in range(7)] + [(w(7, "record") - .1, "stamp", .9)], trans="punch", trans_dur=.3),
    SC("calciopoli", 8, s8, [(.0, "monitor", .4), (w(8, "Calciopoli") - .1, "thunder", 1.0), (w(8, "titres") - .1, "gavel", .9), (w(8, "Serie") - .05, "stamp", 1.0),
                             (w(8, "Serie"), "boo", .7), (w(8, "Serie") + .1, "siren", .25, 2.0)], trans="tear_v", trans_dur=.4),
    SC("fideles", 9, s9, [(.0, "heart", .6)] + [(w(9, wd) - .12, "kick", .5) for wd, _ in NAMES9] + [(w(9, "restent") - .1, "stamp", .8), (w(9, "remonte") - .15, "whoosh_up", .7), (w(9, "remonte") + .25, "crowd", .7)], trans="whip"),
    SC("neuf", 10, s10, [(.0, "elevator", .5)] + [(lerp(w(10, "deux") - .05, w(10, "vingt") + .1, k/8), "coin", .4) for k in range(9)]
       + [(w(10, "vingt") + .1, "fanfare", .7), (w(10, "Cristiano") - .4, "whoosh", .6), (w(10, "Cristiano") - .3, "camera", 1.0), (w(10, "Cristiano"), "siuu", 1.0)], trans="tear_d", trans_dur=.4),
    SC("rose", 11, s11, [(.0, "riser", .6), (.1, "stamp", .8), (w(11, "rose") - .05, "laugh", .5), (w(11, "maillots"), "crumple", .6), (w(11, "Anglais"), "plane", .4),
                         (w(11, "Notts") - .1, "stamp", .9)], trans="punch", trans_dur=.3),
    SC("fin", 12, s12, [(.0, "whoosh", .5), (w(12, "dItalie") - .15, "pop2", .6), (w(12, "commentaire"), "notif", .9), (w(12, "abonne"), "pop2", .7), (w(12, "abonne") + .25, "notif", .8)], trans="whip", pad_out=1.3),
]

def cover(path):
    cv = background(0, TITLE)
    cam(cv, "calciopoli", 0, [(0, (.75, .55, 1.15))], gray=.3); tint(cv, .3)
    K("EN SERIE B…", "cv1", ROUGE, size=120).draw(cv, 0, CX, 560, 1, -4)
    K("…PUIS 9 TITRES", "cv2", GOLD, NOIR, 110).draw(cv, 0, CX, 1180, 1, 3)
    K("D'AFFILÉE ?!", "cv3", GOLD, NOIR, 110).draw(cv, 0, CX, 1340, 1, -2)
    K("L'HISTOIRE DE LA JUVE", "cv4", BLANC, NOIR, 78).draw(cv, 0, CX, 1570, 1, 2)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

def stills(out, fracs=(.05, .18, .32, .46, .6, .74, .88, .98), only=None):
    scene_timing(SCENES, VOICE); starts = np.cumsum([0] + [sc.T for sc in SCENES])
    os.makedirs(out, exist_ok=True); sheets = []
    for i, sc in enumerate(SCENES):
        if only and (i + 1) not in only: continue
        prev = engine._last_frame(SCENES, i - 1, starts, TITLE) if (i > 0 and sc.trans) else None
        ims = []
        for fr_ in fracs:
            t = fr_*sc.T; f = int((starts[i] + t)*FPS)
            cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T)
            if prev is not None and t < sc.trans_dur: engine.TRANSITIONS[sc.trans](cv, prev, t, sc.trans_dur, i)
            finish(cv, TITLE); ims.append(cv.resize((300, 533)))
        sheet = Image.new("RGB", (300*len(ims), 575), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            sheet.paste(im, (k*300, 42)); dd.text((k*300 + 8, 6), f"S{i+1} {fracs[k]*sc.T:.1f}/{sc.T:.1f}", font=font("mono", 24), fill=(230, 230, 230))
        p = os.path.join(out, f"jh_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", SLUG)
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", f"/tmp/{SLUG}_stills"), only=only)); sys.exit()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25, limit=True))
