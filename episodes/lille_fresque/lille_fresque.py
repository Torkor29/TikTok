"""LOSC — version PLAN-SÉQUENCE (test A/B de lille_histoire, même voix, 0 crédit). Voir SCRIPT.md.
Une seule fresque géante (kraft + papiers déchirés colorés), une caméra qui glisse de station en station, aucune coupe.

  python3 episodes/lille_fresque/lille_fresque.py --stills
  python3 episodes/lille_fresque/lille_fresque.py output/lille_fresque
"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "brest_ldc"))
from quiz import *
from brest_ldc import _img, shake, big, marker, typed, CREME, NOIR, BLANC, JAUNE
sys.path.insert(0, os.path.join(ROOT, "episodes", "lille_scrapbook"))
from lille_scrapbook import polaroid, clipping, ticket, postit, fiche, facture, medal, billet, tape, ROSE
A_ = lambda *p: os.path.join(ROOT, "assets", *p)

TITLE = "~/histoires $ ./losc"
SLUG = "lille_fresque"
SRC = os.path.join(ROOT, "episodes", "lille_histoire")
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
VOIX = os.path.join(SRC, "voix", "voix_complete.mp3")
TEXTE = open(os.path.join(SRC, "texte.txt")).read()
_W = json.load(open(os.path.join(SRC, "mots.json")))
def w(txt, n=1):
    k = 0
    for x in _W:
        if x["text"].strip(".,…!?:«» ").lower() == txt.lower():
            k += 1
            if k == n: return x["start"]
    raise KeyError(f"{txt} #{n}")
ROUGE = (220, 18, 38); NAVY = (16, 26, 70); NOIR_D = (20, 18, 22); KRAFT = (178, 140, 98); GRIS = (58, 56, 62); KRAFT2 = (222, 196, 150)

# ------------------------------------------------------------------ fresque (monde)
ST = {"H": (0, 0, NOIR_D, "DÉC. 2020"), "C": (1500, 0, ROUGE, "2021"), "S1": (-200, 2000, CREME, "1944"), "S2": (1300, 3100, ROUGE, "1946"),
      "S3": (-200, 4200, GRIS, "1960s"), "S4": (1300, 5300, CREME, "2000"), "S5": (-200, 6400, NAVY, "2001"), "S6": (1300, 7500, KRAFT2, "2005"),
      "S7": (-200, 8600, ROUGE, "2011"), "S8": (0, -1900, CREME, "2020-21"), "S9": (1500, -1900, NAVY, "MAI 2021")}
ROPE = [ST[k][:2] for k in ("S1", "S2", "S3", "S4", "S5", "S6", "S7")] + [(-1100, 8600), (-1100, 0)] + [ST[k][:2] for k in ("H", "S8", "S9", "C")]
def torn(cx, cy, w_, h_, seed):
    r = random.Random(seed); pts = []
    for (x0, y0, x1, y1) in ((-1, -1, 1, -1), (1, -1, 1, 1), (1, 1, -1, 1), (-1, 1, -1, -1)):
        for k in range(14):
            u = k/14; pts.append((cx + (x0 + (x1 - x0)*u)*w_/2 + r.uniform(-14, 14), cy + (y0 + (y1 - y0)*u)*h_/2 + r.uniform(-14, 14)))
    return pts
PATCH = {k: torn(v[0], v[1], 1000, 1760, i*7 + 3) for i, (k, v) in enumerate(ST.items())}
ROT = {"H": -1.2, "C": 1.5, "S1": 1, "S2": -1.5, "S3": 1.2, "S4": -1, "S5": 1.4, "S6": -1.2, "S7": 1, "S8": -1, "S9": 1.2}

# ------------------------------------------------------------------ caméra
def K(t, st, z=.9, dx=0, dy=0):
    x, y = ST[st][:2] if isinstance(st, str) else st; return (t, x + dx, y + dy, z)
OV = (650, 3300)
CAM = [K(0, "H", 1.0, 0, -40), K(3.95, "H", .94), K(4.4, "C", .9), K(9.45, "C", .93), K(10.15, OV, .16), K(10.7, OV, .17),
       K(11.3, "S1", .9), K(15.55, "S1", .93), K(15.95, "S2"), K(17.85, "S2", .93), K(18.25, "S3"), K(20.35, "S3", .93), K(20.75, "S4"),
       K(23.25, "S4", .93), K(23.65, "S5"), K(25.95, "S5", .93), K(26.35, "S6"), K(30.35, "S6", .93), K(30.75, "S7"), K(35.05, "S7", .92),
       K(35.7, (-500, 4300), .2), K(36.35, "H", .9), K(39.65, "H", .94), K(40.1, "S8"), K(44.45, "S8", .93), K(44.85, "S9"),
       K(48.55, "S9", .94), K(48.95, "C", .9), K(50.0, "C", .94), K(50.9, OV, .16), K(60, OV, .18)]
def ease(u): return u*u*(3 - 2*u)
def cam(t):
    for a, b in zip(CAM, CAM[1:]):
        if t <= b[0]:
            u = ease(clamp((t - a[0])/(b[0] - a[0])))
            z = math.exp(lerp(math.log(a[3]), math.log(b[3]), u))
            if b[3] < .5 or a[3] < .5:          # dézoom : on passe par un zoom bas pour voir le trajet
                pass
            return lerp(a[1], b[1], u), lerp(a[2], b[2], u), z, (b[0] - a[0] < 1.0 and 0 < u < 1)
    return CAM[-1][1], CAM[-1][2], CAM[-1][3], False
PUNCH = []
def zoom_punch(t): return 1 + sum(.06*math.exp(-((t - p)/.12)**2) for p in PUNCH if t > p - .4)

# ------------------------------------------------------------------ éléments de la fresque
ITEMS = []   # (station, dx, dy, t0, t1, fn(cv, fr, t, X, Y, z, s, rot))
def add(st, dx, dy, t0, fn, t1=99, rot=0): ITEMS.append((st, dx, dy, t0, t1, fn, rot))
def B(txt, size, fg, bg, key, rough=3): return lambda cv, fr, t, X, Y, z, s, r: big(txt, key, size, fg, bg, rough=rough).draw(cv, fr, X, Y, s*z, r)
def M(txt, size, key): return lambda cv, fr, t, X, Y, z, s, r: marker(txt, key, size).draw(cv, fr, X, Y, s*z, r)
def S(txt, size, col, key): return lambda cv, fr, t, X, Y, z, s, r: STAMP(txt, key, col, size).draw(cv, fr, X, Y, s*z, r)
def put(name, h):
    def f(cv, fr, t, X, Y, z, s, r):
        p = os.path.join(ROOT, "assets", "logos", f"{name}_sticker.png")
        if not os.path.exists(p): p = os.path.join(ROOT, "assets", "lille", f"{name}.png")
        im, sh = _img(p, h); k = s*z
        if k > .02: blit_sxy(cv, sh, X + 14*k, Y + 20*k, k, k, r); blit_sxy(cv, im, X, Y, k, k, r)
    return f
def moving(fn, path):   # path(t) -> (dx, dy, extra scale)
    def f(cv, fr, t, X, Y, z, s, r):
        dx, dy, e = path(t); fn(cv, fr, t, X + dx*z, Y + dy*z, z, s*e, r)
    return f

# objets du scrapbook posés sur la fresque (tombent avec un rebond + ombre, à l'échelle de la caméra)
def O(sp, t0, d=.22):
    def f(cv, fr, t, X, Y, z, s, r):
        lift = 1 - ease_out_cubic(clamp((t - t0)/d)); im, sh = sp; k = z*(1 + .35*lift); off = (12 + 60*lift)*z
        blit_sxy(cv, sh, X + off*.6, Y + off, k*1.03, k*1.03, r); blit_sxy(cv, im, X, Y, k, k, r)
    return f
def addO(st, dx, dy, t0, sp, rot=0, t1=99, d=.22): add(st, dx, dy, t0, O(sp, t0, d), t1, rot)
def addT(st, dx, dy, t0, rot, wd=170): addO(st, dx, dy, t0 + .12, tape(wd), rot, d=.1)
def addR(st, t0, pts, wd=12, d=.35):          # trait de feutre rouge (coordonnées locales)
    def f(cv, fr, t, X, Y, z, s, r):
        u = clamp((t - t0)/d); n = len(pts) - 1; m = u*n; dr = ImageDraw.Draw(cv)
        P_ = [(X + px*z, Y + py*z) for px, py in pts]
        for k in range(int(math.ceil(m))):
            a_, b_ = P_[k], P_[k + 1]; v = min(1, m - k); dr.line([a_, (lerp(a_[0], b_[0], v), lerp(a_[1], b_[1], v))], fill=ROUGE, width=max(2, int(wd*z)))
    add(st, 0, 0, t0, f)
def pile(n_fn, logo, t0):
    def f(cv, fr, t, X, Y, z, s, r):
        n = n_fn(t); im = billet(220)[0]
        for k in range(n): blit_sxy(cv, im, X + (k % 2)*6*z, Y - k*26*z, z, z, (k % 3) - 1)
        L_ = _img(os.path.join(ROOT, "assets", "logos", f"{logo}_sticker.png"), 190)[0]; blit_sxy(cv, L_, X, Y - (n*26 + 100)*z, z*s, z*s, 0)
    return f
LOSC = A_("logos", "lille_sticker.png"); HZ = A_("lille", "hazard_card.png")

# H : déc. 2020 (papier noir)
add("H", 0, -690, 0, B("RUINÉ…", 160, BLANC, ROUGE, "lfh0", 4), rot=-4)
addO("H", 110, 80, 0, facture(560), -6, d=.01); addT("H", 110, -290, -1, 4)
addO("H", -210, -160, 0, polaroid(LOSC, "LOSC", 380), -9, d=.01); addT("H", -210, -390, -1, -12)
addO("H", 230, 610, .25, postit("PUIS CHAMPION ?!", JAUNE, 360, 70), 7, t1=w("vendre") - .1)
add("H", 140, 300, w("dettes") - .1, S("IMPAYÉ", 110, ROUGE, "lfh2"), rot=-14)
addO("H", -230, 600, w("vendre") - .1, postit("À VENDRE EN URGENCE", ROSE, 340, 62), -6)
add("H", 0, -480, max(w("explosent"), 36.2), B("DETTES ++", 110, NOIR, JAUNE, "lfh4", 4), rot=-3)
addO("H", 240, 610, w("fin") + .1, postit("FIN 2020", JAUNE, 300, 80), 7)
add("H", 40, 60, w("vendu") - .05, S("VENDU", 190, ROUGE, "lfh6"), rot=10)
add("H", 0, 800, w("catastrophe") - .05, B("EN CATASTROPHE", 56, BLANC, NOIR, "lfh5"), rot=2)
# C : 2021 (papier rouge)
add("C", 0, -770, w("six") - .05, B("6 MOIS PLUS TARD…", 80, BLANC, NOIR, "lfc0"), rot=-3)
addO("C", 0, -380, w("champion") - .1, clipping("LILLE CHAMPION DE FRANCE !", 820, 100, "— MAI 2021 —"), 2)
addO("C", -250, 120, w("lille", 2) - .05, polaroid(LOSC, "les Dogues", 340), -7)
addO("C", 280, 60, w("champion") + .25, medal(120), 12)
addO("C", -10, 470, w("psg") - .1, ticket("PSG", "NEYMAR • MBAPPÉ", NAVY, 680), -4)
addR("C", w("mbappé") + .1, [(-300, 360), (180, 590)], 16, .2); addR("C", w("mbappé") + .25, [(180, 360), (-300, 590)], 16, .2)
add("C", 270, 700, w("mbappé") + .4, S("BATTUS", 100, NOIR, "lfc4"), rot=10)
add("C", 0, 130, w("champions", 2), S("CHAMPIONS 2021 !", 110, NOIR, "lfc5"), rot=-10)
# S1 : 1944 (crème)
addO("S1", 0, -640, w("tout") + .2, clipping("1944", 520, 150, "— LILLE —"), -3)
addO("S1", -150, -300, w("clubs") - .2, ticket("OLYMPIQUE LILLOIS", "CLUB N°1", ROUGE, 520), -7)
addO("S1", 130, -150, w("rivaux") - .2, ticket("SC FIVES", "CLUB N°2", NAVY, 520), 6)
add("S1", 300, -430, w("rivaux"), S("RIVAUX", 70, NOIR, "lf13"), rot=14)
addT("S1", -10, -230, w("fusionnent") - .1, -30, 220); addT("S1", 10, -190, w("fusionnent"), 35, 220)
addO("S1", -280, 80, w("fusionnent") + .2, postit("= FUSION", JAUNE, 280, 70), -8)
addO("S1", 170, 300, w("dogues") - .15, polaroid(LOSC, "les Dogues", 400), 5); addT("S1", 170, 60, w("dogues") - .15, 8)
addO("S1", -250, 580, w("dogues") + .35, postit("LES DOGUES SONT NÉS", ROSE, 320, 62), -6)
# S2 : 1946 (rouge)
addO("S2", 0, -560, w("doublé") - .1, clipping("1946 : DOUBLÉ !", 860, 100, "— ÉDITION SPÉCIALE —"), -2)
addO("S2", -60, -60, w("coupe") - .1, ticket("COUPE DE FRANCE", "FINALE 1946", NAVY, 640), -5)
addO("S2", 220, 320, w("championnat") - .15, postit("+ CHAMPIONNAT", JAUNE, 340, 66), 6)
add("S2", -240, 520, w("doublé") + .4, put("lille", 260), rot=-8)
# S3 : la chute (gris)
addO("S3", 90, -600, w("sombre") - .1, clipping("LILLE SOMBRE…", 600, 92, "— CHUTE —"), 3)
fall = lambda t: (40*clamp((t - w("sombre") + .1)/.7), 380*ease_out_back(clamp((t - w("sombre") + .1)/.7)), 1)
add("S3", -170, -250, w("puis") - .05, moving(O(polaroid(LOSC, "LOSC", 380), w("puis") - .05), fall), rot=-14)
addR("S3", w("sombre") + .1, [(330, -330), (330, 160), (270, 80), (330, 160), (390, 80)], 14, .4)
add("S3", 230, 400, w("deuxième") - .05, put("ligue2", 280), rot=8)
add("S3", 0, 720, w("division") - .05, S("DEUXIÈME DIVISION", 70, ROUGE, "lf31"), rot=-4)
# S4 : 2000 (crème)
addO("S4", 0, -660, w("en", 3) + .05, clipping("2000", 480, 150, "— LE RETOUR —"), 3)
addO("S4", 0, -300, w("vahid") - .1, fiche("VAHID HALILHODZIC", "nouveau coach", 720), -3)
addR("S4", w("remonter") - .1, [(-300, 720), (-300, 200), (-370, 290), (-300, 200), (-230, 290)], 14, .35)
rise = lambda t: (0, -300*ease_out_back(clamp((t - w("remonter") + .1)/.6)), 1)
add("S4", -80, 640, w("remonter") - .1, moving(put("lille", 260), rise), rot=-4)
addO("S4", 230, 330, w("remonter") + .1, postit("REMONTÉE !", JAUNE, 320, 76), 6)
# S5 : 2001 (bleu nuit)
addO("S5", -240, -640, w("et", 4) - .05, postit("UN AN APRÈS…", JAUNE, 320, 70), -6)
add("S5", 280, -640, w("lille", 3) - .05, put("lille", 220), rot=8)
addO("S5", 0, -200, w("ligue") - .15, ticket("LIGUE DES CHAMPIONS", "SAISON 2001-02", ROUGE, 820), 3)
add("S5", 0, 360, w("champions") - .05, put("ucl", 440), rot=-4)
# S6 : Hazard (kraft clair)
addO("S6", 0, -670, w("au") - .05, clipping("CENTRE DE FORMATION", 720, 70, "— DOMAINE DE LUCHIN —"), -2)
addO("S6", -230, -340, w("gamin") - .1, postit("UN GAMIN BELGE…", JAUNE, 320, 62), -6)
addO("S6", 240, -330, w("quatorze") - .1, postit("14 ANS", ROSE, 270, 100), 7)
addR("S6", w("quatorze") + .15, [(240 + 175*math.cos(-1.4 + 2.2*math.pi*k/30), -320 + 165*math.sin(-1.4 + 2.2*math.pi*k/30)) for k in range(31)], 10, .35)
addO("S6", 0, 380, w("eden") - .15, polaroid(HZ, "EDEN HAZARD", 600), -3); addT("S6", 0, 40, w("eden") - .15, 3, 220)
# S7 : 2011 (rouge)
addO("S7", -200, -640, w("en", 4) + .05, clipping("2011", 460, 150, "— LILLE —"), -4)
addO("S7", 250, -600, w("en", 4) + .5, polaroid(HZ, "Eden", 300), 8)
addO("S7", 0, -290, w("rudi") - .1, fiche("RUDI GARCIA", "l'entraîneur", 560), -2)
add("S7", 0, 60, w("doublé", 2) - .05, B("DOUBLÉ !", 150, NOIR, JAUNE, "lf72", 4), rot=-4)
def cnt(cv, fr, t, X, Y, z, s, r):
    n = min(65, int(65*clamp((t - w("soixante-cinq") + .05)/.5)))
    big(f"1er DEPUIS {n} ANS", f"lf73{n}", 72, BLANC, NOIR).draw(cv, fr, X, Y, s*z, r)
add("S7", 0, 260, w("soixante-cinq") - .05, cnt, rot=3)
addO("S7", -230, 570, w("doublé", 2) + .3, medal(110), -10)
add("S7", 230, 600, w("doublé", 2) + .45, put("ligue1", 230), rot=8)
# S8 : 2020-21 (crème)
add("S8", 0, -720, w("l'impossible") - .05, B("L'IMPOSSIBLE", 110, BLANC, ROUGE, "lf80", 4), rot=-3)
add("S8", 0, -580, w("l'impossible") + .45, M("ARRIVE", 76, "lf81"), rot=3)
for k, (nm, role, word, x, y, r) in enumerate([("MAIGNAN", "dans les cages", "maignan", -110, -300, -5),
                                               ("BURAK YILMAZ", "devant", "burak", 120, 40, 4), ("GALTIER", "sur le banc", "galtier", -110, 380, -3)]):
    addO("S8", x, y, w(word) - .1, fiche(nm, role, 560), r); addT("S8", x - 210, y - 130, w(word) - .1, -30, 140)
add("S8", 300, 680, w("maignan") + .2, put("lille", 220), rot=8)
# S9 : budget (bleu nuit)
addO("S9", -250, -660, w("budget") - .15, postit("BUDGET", JAUNE, 300, 80), -6)
addO("S9", 250, -620, w("quatre") - .05, postit("×4", ROSE, 250, 150), 8)
add("S9", -230, 420, w("face"), pile(lambda t: 4, "lille", 0))
add("S9", 230, 420, w("psg", 2) - .05, pile(lambda t: 4 + int(12*clamp((t - w("quatre") + .1)/.5)) if t > w("quatre") - .1 else 4, "psg", 0))
add("S9", 0, 640, w("dogues", 2) - .05, M("LES DOGUES TIENNENT", 70, "lf92"), rot=2)
add("S9", 0, 780, w("dogues", 2) + .5, B("JUSQU'AU BOUT", 66, BLANC, ROUGE, "lf93"), rot=-2)

PUNCH += [0, w("dettes"), w("champion"), w("mbappé") + .3, w("dogues"), w("doublé"), w("deuxième"), w("remonter"), w("ligue"), w("quatorze"),
          w("eden"), w("doublé", 2), w("vendu"), w("maignan"), w("burak"), w("galtier"), w("quatre"), w("champions", 2)]

# ------------------------------------------------------------------ rendu
def flag(cv, fr, txt, X, Y, z, key):
    LBL(txt, "lfflag" + key, font("mono", 58), BLANC, NOIR, padx=18, pady=4, rough=2).draw(cv, fr, X, Y, z, -6)

def draw_world(cv, fr, t, cx, cy, z):
    d = ImageDraw.Draw(cv)
    S_ = lambda x, y: (CX + (x - cx)*z, H/2 + (y - cy)*z)
    # fond kraft + trame de points qui défile (sensation de mouvement)
    d.rectangle([0, 0, W, H], fill=KRAFT)
    step = 180
    gx0 = math.floor((cx - CX/z)/step); gx1 = math.ceil((cx + CX/z)/step); gy0 = math.floor((cy - H/2/z)/step); gy1 = math.ceil((cy + H/2/z)/step)
    if (gx1 - gx0)*(gy1 - gy0) < 4000:
        r = max(1.5, 5*z)
        for gx in range(gx0, gx1 + 1):
            for gy in range(gy0, gy1 + 1):
                X, Y = S_(gx*step, gy*step); d.ellipse([X - r, Y - r, X + r, Y + r], fill=(160, 124, 84))
    # ruban
    pts = [S_(*p) for p in ROPE]
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b); n = max(1, int(L/(40*z)))
        for k in range(0, n, 2):
            u0, u1 = k/n, min(1, (k + 1)/n)
            d.line([(lerp(a[0], b[0], u0), lerp(a[1], b[1], u0)), (lerp(a[0], b[0], u1), lerp(a[1], b[1], u1))], fill=ROUGE, width=max(2, int(16*z)))
    # papiers des stations
    for k, (x, y, col, lab) in ST.items():
        X, Y = S_(x, y)
        if X < -700*z - 200 or X > W + 700*z + 200 or Y < -1000*z - 200 or Y > H + 1000*z + 200: continue
        poly = [S_(*p) for p in PATCH[k]]
        d.polygon([(px + 16*z, py + 22*z) for px, py in poly], fill=(110, 84, 56))
        d.polygon(poly, fill=col)
        # scotch
        for sx_ in (-1, 1):
            tx, ty = S_(x + sx_*440, y - 880)
            d.polygon([(tx - 80*z, ty - 26*z), (tx + 80*z, ty - 14*z), (tx + 76*z, ty + 30*z), (tx - 84*z, ty + 18*z)], fill=(236, 226, 190))
    if z < .5 and t < 12:                                # dates : seulement au 1er dézoom (frise encore vide)
        for k, (x, y, col, lab) in ST.items():
            X, Y = S_(x, y); flag(cv, fr, lab, X, Y, z*4.5, k)
    # éléments
    for st, dx, dy, t0, t1, fn, rot in ITEMS:
        if t < t0 or t > t1: continue
        x, y = ST[st][:2]; X, Y = S_(x + dx, y + dy)
        if X < -700 or X > W + 700 or Y < -700 or Y > H + 700: continue
        fn(cv, fr, t, X, Y, z, slam(t, t0, .18), rot)

def bills(cv, fr, t, t0, n=10):
    for k in range(n):
        u = prog(t, t0 + k*.07, 1.3)
        if 0 < u < 1:
            LBL("100", f"lfeur{k%3}", font("title", 54), NOIR, (120, 200, 120), padx=14, pady=2, rough=2).draw(
                cv, fr, 100 + (k*173) % 880 + 60*math.sin(u*6 + k), 1950 - 1700*u, .9, 25*math.sin(k + u*5))

def draw(cv, fr, t, T):
    tv = max(0.0, t - PAD_IN)
    cx, cy, z, moving_ = cam(tv); z *= zoom_punch(tv)
    draw_world(cv, fr, tv, cx, cy, z)
    if moving_:                                          # traits de vitesse
        d = ImageDraw.Draw(cv); r = random.Random(fr)
        for _ in range(6):
            y = r.uniform(0, H); x = r.uniform(0, W); d.line([(x, y), (x + r.uniform(200, 500), y)], fill=(250, 246, 230), width=4)
    if tv < 6: bills(cv, fr, tv, w("dettes"))
    if 36 < tv < 38.5: bills(cv, fr, tv, w("explosent"), 14)
    if w("comment") - .1 < tv < w("tout") - .1:
        ransom_line(cv, "COMMENT", 820, 170, seed=4); ransom_line(cv, "C'EST POSSIBLE ?", 1060, 120, seed=9)
    if tv > w("doublé") and tv < w("doublé") + 3: confetti(cv, fr, "lfcf1", tv - w("doublé"), 50, 2.5, [JAUNE, BLANC])
    if tv > w("champion") and tv < w("champion") + 3.5: confetti(cv, fr, "lfcf0", tv - w("champion"), 60, 3, [JAUNE, BLANC, NAVY])
    if tv > w("champions", 2): confetti(cv, fr, "lfcf2", tv - w("champions", 2), 90, 4, [JAUNE, BLANC, NAVY])
    if tv > w("toi") - .05:
        big("TU T'EN SOUVIENS ?", "lfcta1", 100, BLANC, ROUGE).draw(cv, fr, CX, 380, slam(tv, w("toi") - .05, .16), -3)
        if tv > w("dis-moi") - .05:
            marker("PROCHAIN CLUB ?", "lfcta2", 100).draw(cv, fr, CX, 1500, slam(tv, w("dis-moi") - .05, .16), 2)
            big("DIS-LE EN COMMENTAIRE", "lfcta3", 64, BLANC, NOIR).draw(cv, fr, CX, 1660, slam(tv, w("commentaire") - .05, .16), -2)
    for ti in PUNCH: shake(cv, tv, ti, 12)

P = PAD_IN
def X_(word, n, name, g, dt=-.05): return (P + w(word, n) + dt, name, g)
MOVES = [4.0, 9.5, 10.75, 15.6, 17.9, 20.4, 23.3, 26.0, 30.4, 35.1, 39.7, 44.5, 48.6, 50.0]
WH = ["whoosh", "rewind", "plane", "whoosh", "whoosh", "whoosh", "whoosh", "whoosh", "whoosh", "plane", "whoosh", "whoosh", "whoosh", "rewind"]
SFX = [(0.0, "braam", .7), (0.0, "typewriter", .35), X_("dettes", 1, "stamp", .8), X_("dettes", 1, "cash", .4, .1), X_("vendre", 1, "siren", .2),
       X_("champion", 1, "goal_roar", .5), X_("champion", 1, "boom", .6), X_("mbappé", 1, "stamp", .6, .35), X_("comment", 1, "scratch", .55),
       X_("tout", 1, "projector", .4), X_("rivaux", 1, "stamp", .5), X_("dogues", 1, "boom", .6), X_("dogues", 1, "crowd", .4),
       X_("doublé", 1, "fanfare", .45), X_("puis", 1, "groan", .35), X_("deuxième", 1, "stamp", .6), X_("vahid", 1, "camera", .5),
       X_("remonter", 1, "riser", .45), X_("ligue", 1, "goal_roar", .45), X_("gamin", 1, "sparkle", .5), X_("quatorze", 1, "stamp", .5),
       X_("hazard", 1, "camera", .55), X_("doublé", 2, "fanfare", .45), X_("doublé", 2, "crowd", .4), X_("mais", 1, "thunder", .45),
       X_("explosent", 1, "cash", .5, .4), X_("vendu", 1, "gavel", .7), X_("catastrophe", 1, "crumple", .5), X_("l'impossible", 1, "riser", .45),
       X_("maignan", 1, "camera", .5), X_("burak", 1, "camera", .5), X_("galtier", 1, "camera", .5), X_("quatre", 1, "stamp", .6),
       X_("dogues", 2, "drumroll", .35), X_("champions", 2, "boom", .8), X_("champions", 2, "goal_roar", .6), X_("champions", 2, "champagne", .4, .4),
       X_("toi", 1, "notif", .5), X_("commentaire", 1, "bell", .4)]
SFX += [(P + m, WH[i], .35 if WH[i] == "whoosh" else .4) for i, m in enumerate(MOVES)]
SCENES = [Scene("fresque", TEXTE, draw, SFX, pad_in=P, pad_out=1.6)]

def cover(path):
    cv = background(0, TITLE); draw_world(cv, 0, 60, OV[0], OV[1], .16)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 110)); cv.alpha_composite(ov) if cv.mode == "RGBA" else cv.paste(ov, (0, 0), ov)
    big("RUINÉ…", "lfcv1", 150, BLANC, ROUGE, rough=4).draw(cv, 0, CX, 420, 1, -4)
    blit_sxy(cv, _img(os.path.join(ROOT, "assets", "logos", "lille_sticker.png"), 520)[0], CX, 900, 1, 1, -3)
    big("PUIS CHAMPION", "lfcv2", 120, NOIR, JAUNE, rough=4).draw(cv, 0, CX, 1360, 1, 3)
    big("L'HISTOIRE FOLLE DU LOSC", "lfcv3", 60, BLANC, NOIR).draw(cv, 0, CX, 1530, 1, -2)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

def stills(out):
    scene_timing(SCENES, [VOIX]); sc = SCENES[0]; os.makedirs(out, exist_ok=True)
    ts = [P + x for x in (.3, 3.2, 4.2, 8.9, 10.3, 11.0, 14.8, 17.5, 20.0, 23.0, 25.8, 29.9, 34.9, 35.5, 38.8, 43.5, 47.5, 50.0, 51.5, 54.0)]
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
