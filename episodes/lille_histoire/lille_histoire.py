"""HISTOIRE DU LOSC (≈ 57 s) : de la vente en catastrophe (déc. 2020) au titre 2021 devant le PSG de Neymar et Mbappé.
Collage papier : écussons autocollants (logos/lille, psg, ligue1, ligue2, ucl), carte Hazard (assets/lille/hazard_card.png).

  python3 episodes/lille_histoire/lille_histoire.py output/lille_histoire --stills
  python3 episodes/lille_histoire/lille_histoire.py output/lille_histoire
"""
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "brest_ldc"))
from quiz import *
from brest_ldc import _img, paper_bg, shake, flash, glitch, big, marker, typed, slide, CREME, NOIR, BLANC, JAUNE

TITLE = "~/histoires $ ./losc"
SLUG = "lille_histoire"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
VOIX = os.path.join(HERE, "voix", "voix_complete.mp3")
TEXTE = open(os.path.join(HERE, "texte.txt")).read()
_W = json.load(open(os.path.join(HERE, "mots.json")))
def w(txt, n=1):
    k = 0
    for x in _W:
        if x["text"].strip(".,…!?:«» ").lower() == txt.lower():
            k += 1
            if k == n: return x["start"]
    raise KeyError(f"{txt} #{n}")
ROUGE = (220, 18, 38); NAVY = (16, 26, 70); NOIR_D = (14, 12, 16); OR = (236, 190, 60)

def put(cv, name, x, y, h, s=1.0, rot=0.0):
    if s <= .02: return
    p = os.path.join(ROOT, "assets", "logos", f"{name}_sticker.png")
    if not os.path.exists(p): p = os.path.join(ROOT, "assets", "lille", f"{name}.png")
    im, sh = _img(p, h)
    blit_sxy(cv, sh, x + 14*s, y + 20*s, s, s, rot); blit_sxy(cv, im, x, y, s, s, rot)
def dim(cv, a):
    if a <= 0: return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, int(a))); cv.alpha_composite(ov) if cv.mode == "RGBA" else cv.paste(ov, (0, 0), ov)
def year(cv, fr, t, txt, t0, y=230, size=96, key=""):
    if t > t0:
        s_ = typed(txt, t, t0, 18)
        LBL(s_, f"lh{key}{s_}", font("mono", size), NOIR, BLANC, padx=24, pady=6, rough=2).draw(cv, fr, CX, y, 1, -2)
def coins(cv, fr, t, t0, n=10):   # billets qui s'envolent
    for k in range(n):
        u = prog(t, t0 + k*.07, 1.3)
        if 0 < u < 1:
            x = 100 + (k*173) % 880 + 60*math.sin(u*6 + k); y = 1950 - 1700*u
            LBL("100", f"lheur{k%3}", font("title", 54), NOIR, (120, 200, 120), padx=14, pady=2, rough=2).draw(cv, fr, x, y, .9, 25*math.sin(k + u*5))

# ------------------------------------------------------------------ plans
def s0(cv, fr, t):   # HOOK : ruiné -> champion
    if t < w("six") - .05:
        paper_bg(cv, fr, NOIR_D); rays(cv, (CX, 900), t, .6, 14, 1500, (40, 30, 34), .08, .3)
        year(cv, fr, t, "DÉCEMBRE 2020", .3, 1760, 70, "0y")
        if t < w("dettes") - .1:
            big("RUINÉ…", "lh0z", 190, BLANC, ROUGE, rough=4).draw(cv, fr, CX, 300, slam(t, 0, .15), -4)
            marker("PUIS CHAMPION ?!", "lh0y", 80).draw(cv, fr, CX, 1450, slam(t, .25, .15), 3)
        put(cv, "lille_sticker" if False else "lille", CX, 860, 620, slam(t, .0, .2)*(1 - .03*t), -4*math.sin(t*3))
        if t > w("dettes") - .1: STAMP("RUINÉ", "lh0a", ROUGE, 200).draw(cv, fr, CX, 880, slam(t, w("dettes") - .1, .2), -12)
        coins(cv, fr, t, w("dettes"))
        if t > w("vendre") - .1: big("À VENDRE EN URGENCE", "lh0b", 86, BLANC, ROUGE).draw(cv, fr, CX, 1500, slam(t, w("vendre") - .1, .16), 3)
    elif t < w("comment") - .05:
        paper_bg(cv, fr, ROUGE); rays(cv, (CX, 860), t, 1.0, 18, 1700, (236, 50, 66), .1, .5)
        big("6 MOIS PLUS TARD", "lh0c", 92, BLANC, NOIR).draw(cv, fr, CX, 190, slam(t, w("six") - .05, .16), -3)
        put(cv, "lille", CX, 720, 620, slam(t, w("lille", 2) - .05, .22)*(1 + .03*(t - w("lille", 2))), 3)
        if t > w("champion") - .05: big("CHAMPION DE FRANCE", "lh0d", 104, NOIR, JAUNE, rough=4).draw(cv, fr, CX, 1150, slam(t, w("champion") - .05, .18), -3)
        if t > w("devant") - .05:
            put(cv, "psg", 300, 1530, 330, slam(t, w("psg") - .05, .2), -10)
            big("NEYMAR", "lh0e", 74, BLANC, NAVY).draw(cv, fr, 750, 1460, slam(t, w("neymar") - .05, .16), 4)
            big("MBAPPÉ", "lh0f", 74, BLANC, NAVY).draw(cv, fr, 750, 1600, slam(t, w("mbappé") - .05, .16), -3)
            if t > w("mbappé") + .3: STAMP("BATTUS", "lh0g", NOIR, 110).draw(cv, fr, 520, 1760, slam(t, w("mbappé") + .3, .18), -8)
        confetti(cv, fr, "lh0cf", t - w("champion"), 60, 3, [JAUNE, BLANC, NAVY])
    else:
        paper_bg(cv, fr, NOIR_D)
        ransom_line(cv, "COMMENT", 760, 170, seed=4)
        ransom_line(cv, "C'EST POSSIBLE ?", 1000, 120, seed=9)
        put(cv, "lille", CX, 1450, 300, slam(t, w("comment") + .3, .2), 6)

def s1(cv, fr, t):   # 1944 : fusion, les Dogues
    paper_bg(cv, fr, CREME)
    big("1944", "lh1a", 230, NOIR, BLANC, rough=4).draw(cv, fr, CX, 260, slam(t, w("tout") - .05, .18), -4)
    if t < w("dogues") - .05:
        a = slam(t, w("deux") - .05 if False else w("quarante-quatre") + .3, .2)
        mv = clamp((t - w("fusionnent") + .1)/.5)
        big("OLYMPIQUE LILLOIS", "lh1b", 96, BLANC, ROUGE).draw(cv, fr, CX - 60*(1 - mv) * (1 if a else 0) - 0, 760 - 150*(1 - mv), a, -5)
        big("SC FIVES", "lh1c", 110, BLANC, NAVY).draw(cv, fr, CX + 120*(1 - mv), 1000 + 150*(1 - mv) - 240*mv, a, 5)
        if t > w("rivaux") - .05: STAMP("RIVAUX", "lh1d", NOIR, 110).draw(cv, fr, CX, 1300, slam(t, w("rivaux") - .05, .18), 8)
        if t > w("fusionnent") + .3: big("= FUSION", "lh1e", 90, NOIR, JAUNE).draw(cv, fr, CX, 1500, slam(t, w("fusionnent") + .3, .16), -2)
    else:
        put(cv, "lille", CX, 900, 640, slam(t, w("dogues") - .1, .22), -3)
        ransom_line(cv, "LES DOGUES", 1430, 150, seed=7)
        marker("SONT NÉS", "lh1f", 90).draw(cv, fr, CX, 1640, slam(t, w("nés") - .05 if False else w("dogues") + .4, .16), 2)

def s2(cv, fr, t):   # 1946 doublé puis chute en D2
    if t < w("puis") - .05:
        paper_bg(cv, fr, ROUGE); rays(cv, (CX, 900), t, .9, 16, 1600, (236, 50, 66), .1, .4)
        big("1946", "lh2a", 200, NOIR, BLANC, rough=4).draw(cv, fr, CX, 260, slam(t, w("doublé") - 1.0, .18), 4)
        if t > w("doublé") - .05: big("DOUBLÉ !", "lh2b", 180, NOIR, JAUNE, rough=4).draw(cv, fr, CX, 760, slam(t, w("doublé") - .05, .2), -6)
        if t > w("coupe") - .05: big("COUPE", "lh2c", 90, BLANC, NOIR).draw(cv, fr, 330, 1150, slam(t, w("coupe") - .05, .16), -4)
        if t > w("championnat") - .1: big("+ CHAMPIONNAT", "lh2d", 90, BLANC, NOIR).draw(cv, fr, 640, 1330, slam(t, w("championnat") - .1, .16), 3)
        put(cv, "lille", CX, 1680, 300, 1, 5)
        confetti(cv, fr, "lh2cf", t - w("doublé"), 50, 2.5, [JAUNE, BLANC])
        return
    paper_bg(cv, fr, CREME); dk = clamp((t - w("puis"))/1.2)
    fall = 700*ease_out_back(clamp((t - w("sombre") + .1)/.6)) if t > w("sombre") - .1 else 0
    put(cv, "lille", CX, 600 + fall, 520, 1, 8*math.sin(t*2) + fall*.03)
    dim(cv, 170*dk)
    big("LE CLUB SOMBRE…", "lh2e", 90, BLANC, NOIR).draw(cv, fr, CX, 230, slam(t, w("sombre") - .05, .16), -2)
    if t > w("deuxième") - .05:
        put(cv, "ligue2", CX, 1600, 340, slam(t, w("deuxième") - .05, .2), -6)
        STAMP("DEUXIÈME DIVISION", "lh2f", ROUGE, 80).draw(cv, fr, CX, 1830, slam(t, w("division") - .05, .18), 4)

def s3(cv, fr, t):   # 2000 Halilhodzic, 2001 LDC
    if t < w("et", 4) - .05:
        paper_bg(cv, fr, CREME)
        year(cv, fr, t, "2000", w("en", 3) - .05, 230, 150, "3y")
        if t > w("vahid") - .05:
            marker("VAHID HALILHODZIC", "lh3a", 96).draw(cv, fr, CX, 820, slam(t, w("vahid") - .05, .18), -3)
            big("NOUVEAU COACH", "lh3b", 60, BLANC, NOIR).draw(cv, fr, CX, 960, slam(t, w("vahid") + .3, .16), 2)
        if t > w("remonter") - .1:
            u = ease_out_back(clamp((t - w("remonter") + .1)/.6))
            put(cv, "lille", CX, 1700 - 400*u, 420, 1, -4)
            big("REMONTÉE !", "lh3c", 90, BLANC, ROUGE).draw(cv, fr, CX, 1780, slam(t, w("remonter"), .16), 3)
        return
    paper_bg(cv, fr, NAVY); rays(cv, (CX, 900), t, 1.0, 18, 1700, (32, 46, 110), .1, .4)
    big("UN AN APRÈS", "lh3d", 100, NOIR, JAUNE).draw(cv, fr, CX, 220, slam(t, w("et", 4) - .05, .16), -3)
    put(cv, "lille", 300, 600, 340, slam(t, w("lille", 3) - .05, .2), -8)
    put(cv, "ucl", CX + 80, 1050, 640, slam(t, w("ligue") - .05, .22), 3)
    if t > w("champions") - .05: marker("LIGUE DES CHAMPIONS !", "lh3e", 84).draw(cv, fr, CX, 1560, slam(t, w("champions") - .05, .16), -2)

def s4(cv, fr, t):   # Hazard
    paper_bg(cv, fr, CREME)
    big("CENTRE DE FORMATION", "lh4a", 74, BLANC, NOIR).draw(cv, fr, CX, 200, slam(t, w("au") - .05, .16), -2)
    if t < w("eden") - .1:
        big("UN GAMIN BELGE", "lh4b", 110, NOIR, JAUNE, rough=4).draw(cv, fr, CX, 760, slam(t, w("gamin") - .05, .18), 3)
        if t > w("quatorze") - .05: big("14 ANS", "lh4c", 260, BLANC, ROUGE, rough=4).draw(cv, fr, CX, 1150, slam(t, w("quatorze") - .05, .2), -5)
        if t > w("quatorze") + .3:
            big("?", "lh4q", 200, NOIR, BLANC).draw(cv, fr, CX, 1580, slam(t, w("quatorze") + .3, .16)*(1 + .05*math.sin(t*12)), 8)
        return
    put(cv, "hazard_card", CX + slide(t, w("eden") - .1, .3, 1000), 960, 1060, 1 + .015*(t - w("eden")), -3)
    marker("EDEN HAZARD", "lh4d", 120).draw(cv, fr, CX, 1640, slam(t, w("hazard") - .05, .16), 2)

def s5(cv, fr, t):   # 2011 doublé, 65 ans
    paper_bg(cv, fr, ROUGE); rays(cv, (CX, 900), t, 1.1, 18, 1700, (236, 50, 66), .1, .5)
    year(cv, fr, t, "2011", w("en", 4) - .05, 220, 150, "5y")
    put(cv, "hazard_card", 820, 760, 520, slam(t, w("en", 4), .2), 8)
    if t > w("rudi") - .05: big("RUDI GARCIA", "lh5a", 76, BLANC, NOIR).draw(cv, fr, 320, 620, slam(t, w("rudi") - .05, .16), -5)
    if t > w("doublé", 2) - .05: big("DOUBLÉ", "lh5b", 200, NOIR, JAUNE, rough=4).draw(cv, fr, CX, 1200, slam(t, w("doublé", 2) - .05, .2), -4)
    if t > w("soixante-cinq") - .05:
        n = min(65, int(65*clamp((t - w("soixante-cinq") + .05)/.5)))
        big(f"1er DEPUIS {n} ANS", f"lh5c{n}", 84, BLANC, NOIR).draw(cv, fr, CX, 1470, slam(t, w("soixante-cinq") - .05, .16), 3)
    put(cv, "ligue1", 240, 1730, 260, slam(t, w("doublé", 2), .2), -8)
    confetti(cv, fr, "lh5cf", t - w("doublé", 2), 60, 3, [JAUNE, BLANC, NAVY])

def s6(cv, fr, t):   # dettes, vente en catastrophe
    paper_bg(cv, fr, NOIR_D)
    big("MAIS…", "lh6a", 110, BLANC, ROUGE).draw(cv, fr, CX, 210, slam(t, w("mais") - .05, .16), -3)
    put(cv, "lille", CX, 860, 560, 1, 4*math.sin(t*14) if t > w("explosent") else 0)
    if t > w("explosent") - .1: big("DETTES XXL", "lh6b", 120, NOIR, JAUNE, rough=4).draw(cv, fr, CX, 1300, slam(t, w("explosent") - .1, .18)*(1 + .04*math.sin(t*20)), -4)
    coins(cv, fr, t, w("explosent"), 14)
    if t > w("fin") - .05: year(cv, fr, t, "FIN 2020", w("fin") - .05, 1520, 80, "6y")
    if t > w("vendu") - .05: STAMP("VENDU", "lh6c", ROUGE, 220).draw(cv, fr, CX, 860, slam(t, w("vendu") - .05, .2), -14)
    if t > w("catastrophe") - .05: big("EN CATASTROPHE", "lh6d", 80, BLANC, NOIR).draw(cv, fr, CX, 1740, slam(t, w("catastrophe") - .05, .16), 3)

def s7(cv, fr, t):   # l'impossible : l'équipe 2021
    if t < w("maignan") - .05:
        paper_bg(cv, fr, NOIR_D)
        ransom_line(cv, "L'IMPOSSIBLE", 900, 150, seed=11)
        big("ARRIVE", "lh7a", 110, NOIR, JAUNE).draw(cv, fr, CX, 1120, slam(t, w("arrive") - .05 if False else w("l'impossible") + .4, .16), -3)
        return
    paper_bg(cv, fr, CREME)
    big("2020-21", "lh7b", 120, BLANC, ROUGE).draw(cv, fr, CX, 200, 1, -3)
    for k, (nm, sub, word, x, y, r) in enumerate([("MAIGNAN", "DANS LES CAGES", "maignan", 330, 560, -5),
                                                   ("BURAK YILMAZ", "DEVANT", "burak", 700, 950, 4),
                                                   ("GALTIER", "SUR LE BANC", "galtier", 360, 1340, -3)]):
        if t > w(word) - .05:
            big(nm, f"lh7n{k}", 96, BLANC, NAVY).draw(cv, fr, x, y, slam(t, w(word) - .05, .16), r)
            marker(sub, f"lh7s{k}", 56).draw(cv, fr, x + 40, y + 110, slam(t, w(word) + .3, .16), -r)
    put(cv, "lille", 860, 1650, 330, slam(t, w("maignan"), .2), 8)

def s8(cv, fr, t):   # David contre Goliath -> champions
    if t < w("champions", 2) - .05:
        paper_bg(cv, fr, NAVY); rays(cv, (CX, 900), t, .8, 16, 1600, (30, 44, 104), .1, .3)
        big("BUDGET", "lh8a", 90, BLANC, NOIR).draw(cv, fr, CX, 210, slam(t, w("budget") - .1, .16), -2)
        grow = 1 + 1.0*clamp((t - w("quatre") + .1)/.5)
        put(cv, "psg", 760, 760, int(260), slam(t, w("psg", 2) - .05, .2)*grow, 6)
        put(cv, "lille", 230, 1000, 230, slam(t, w("face") - .05, .2), -6)
        if t > w("quatre") - .05: big("×4", "lh8b", 230, NOIR, JAUNE, rough=4).draw(cv, fr, 300, 600, slam(t, w("quatre") - .05, .2), -8)
        if t > w("dogues", 2) - .05:
            marker("LES DOGUES TIENNENT", "lh8c", 84).draw(cv, fr, CX, 1420, slam(t, w("dogues", 2) - .05, .16), 2)
            big("JUSQU'AU BOUT", "lh8d", 84, BLANC, ROUGE).draw(cv, fr, CX, 1560, slam(t, w("dogues", 2) + .5, .16), -2)
        return
    paper_bg(cv, fr, ROUGE); rays(cv, (CX, 860), t, 1.4, 22, 1800, (240, 56, 70), .12, .6)
    put(cv, "lille", CX, 760, 680, slam(t, w("champions", 2) - .05, .24)*(1 + .03*math.sin(t*6)), -3)
    big("CHAMPIONS", "lh8e", 170, NOIR, JAUNE, rough=4).draw(cv, fr, CX, 1300, slam(t, w("champions", 2), .18), -4)
    big("DE FRANCE 2021", "lh8f", 96, BLANC, NOIR).draw(cv, fr, CX, 1480, slam(t, w("champions", 2) + .3, .16), 3)
    confetti(cv, fr, "lh8cf", t - w("champions", 2), 90, 4, [JAUNE, BLANC, NAVY])

def s9(cv, fr, t):   # CTA
    paper_bg(cv, fr, CREME)
    put(cv, "lille", CX, 640, 520, 1, 3*math.sin(t*3))
    big("TU T'EN SOUVIENS ?", "lh9a", 96, BLANC, ROUGE).draw(cv, fr, CX, 1100, slam(t, w("et", 3) - .05 if False else w("toi") - .05, .16), -3)
    if t > w("dis-moi") - .05:
        marker("PROCHAIN CLUB ?", "lh9b", 100).draw(cv, fr, CX, 1320, slam(t, w("dis-moi") - .05, .16), 2)
        big("DIS-LE EN COMMENTAIRE", "lh9c", 64, BLANC, NOIR).draw(cv, fr, CX, 1480, slam(t, w("commentaire") - .05, .16), -2)

CUTS = [0, w("tout"), w("deux", 4) if False else w("doublé") - 1.0, w("en", 3), w("au"), w("en", 4), w("mais"), w("et", 5), w("face"), w("toi") - .3]
SHOTS = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9]
IMPACTS = [0, w("dettes"), w("six"), w("champion"), w("psg"), w("comment"), w("dogues"), w("doublé"), w("sombre"), w("deuxième"), w("remonter"), w("ligue"),
           w("quatorze"), w("eden"), w("doublé", 2), w("explosent"), w("vendu"), w("l'impossible"), w("maignan"), w("burak"), w("galtier"), w("quatre"), w("champions", 2)]
INNER = [w("six"), w("comment"), w("dogues"), w("puis"), w("et", 4), w("eden"), w("maignan"), w("champions", 2)]
def shot_of(t):
    k = 0
    for i, c in enumerate(CUTS):
        if t >= c - .04: k = i
    return k
def draw(cv, fr, t, T):
    tv = t - PAD_IN; k = shot_of(tv); SHOTS[k](cv, fr, max(0.0, tv))
    for c in CUTS[1:] + INNER:
        punch(cv, tv, c, 1.06, .25); glitch(cv, tv, c); flash(cv, tv, c - .02, .1)
    for ti in IMPACTS: shake(cv, tv, ti, 16)
    drift(cv, t, T, .015)

P = PAD_IN
def S(word, n, name, g, dt=-.05): return (P + w(word, n) + dt, name, g)
SFX = [(0.0, "braam", .7), (0.0, "typewriter", .4), S("dettes", 1, "stamp", .8), S("dettes", 1, "cash", .4, .1), S("vendre", 1, "siren", .25),
       S("six", 1, "rewind", .5), S("champion", 1, "goal_roar", .5), S("champion", 1, "boom", .6), S("psg", 1, "whoosh", .4), S("mbappé", 1, "stamp", .6, .35),
       S("comment", 1, "scratch", .6), S("tout", 1, "projector", .4), S("tout", 1, "typewriter", .4), S("rivaux", 1, "stamp", .6), S("fusionnent", 1, "crash", .4, .25),
       S("dogues", 1, "boom", .7), S("dogues", 1, "crowd", .4), S("doublé", 1, "fanfare", .45), S("puis", 1, "groan", .35), S("sombre", 1, "whoosh", .5),
       S("deuxième", 1, "stamp", .7), S("en", 3, "typewriter", .4), S("vahid", 1, "camera", .5), S("remonter", 1, "riser", .45), S("ligue", 1, "goal_roar", .45),
       S("gamin", 1, "sparkle", .5), S("quatorze", 1, "stamp", .6), S("eden", 1, "whoosh", .5), S("hazard", 1, "camera", .55), S("en", 4, "typewriter", .4),
       S("doublé", 2, "fanfare", .45), S("doublé", 2, "crowd", .45), S("mais", 1, "thunder", .45), S("explosent", 1, "cash", .5), S("vendu", 1, "gavel", .7),
       S("catastrophe", 1, "crumple", .5), S("l'impossible", 1, "riser", .5), S("maignan", 1, "camera", .5), S("burak", 1, "camera", .5), S("galtier", 1, "camera", .5),
       S("quatre", 1, "stamp", .6), S("dogues", 2, "drumroll", .35), S("champions", 2, "boom", .8), S("champions", 2, "goal_roar", .6), S("champions", 2, "champagne", .4, .4),
       S("toi", 1, "notif", .5), S("commentaire", 1, "bell", .4)]
SCENES = [Scene("losc", TEXTE, draw, SFX, pad_in=P, pad_out=1.4)]

def cover(path):
    cv = background(0, TITLE); stage_fill(cv, 0, ROUGE, "lhcv")
    rays(cv, (CX, 960), .5, 1.0, 18, 1700, (240, 56, 70), .12, .5)
    big("RUINÉ…", "lhcv1", 150, BLANC, NOIR, rough=4).draw(cv, 0, CX, 400, 1, -4)
    put(cv, "lille", CX, 900, 600, 1, -3)
    big("PUIS CHAMPION", "lhcv2", 120, NOIR, JAUNE, rough=4).draw(cv, 0, CX, 1360, 1, 3)
    big("L'HISTOIRE FOLLE DU LOSC", "lhcv3", 60, BLANC, NOIR).draw(cv, 0, CX, 1530, 1, -2)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

def stills(out):
    scene_timing(SCENES, [VOIX]); sc = SCENES[0]; os.makedirs(out, exist_ok=True)
    ts = [P + x for x in (.3, 3.0, 6.5, 9.0, 10.3, 13.5, 15.5, 17.5, 20.0, 23.0, 25.8, 28.9, 30.5, 34.9, 38.8, 40.5, 44.0, 47.5, 50.0, 53.5)]
    ims = []
    for t in ts:
        f = int(t*FPS); cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T); finish(cv, TITLE); ims.append(cv.resize((216, 384)))
    sheet = Image.new("RGB", (216*10, 2*414), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        x, y = (k % 10)*216, (k//10)*414; sheet.paste(im, (x, y + 30)); dd.text((x + 6, y + 4), f"{ts[k]-P:.1f}s", font=font("mono", 22), fill=(230, 230, 230))
    p = os.path.join(out, "sheet.jpg"); sheet.save(p, quality=82); return p

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", SLUG)
    if "--stills" in args: print(stills(f"/tmp/{SLUG}_stills")); sys.exit()
    os.makedirs(out, exist_ok=True); cover(os.path.join(out, f"{SLUG}_couverture.jpg"))
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=[VOIX], sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25, limit=True))
