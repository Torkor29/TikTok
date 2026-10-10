"""L'histoire de l'Olympique lyonnais — v2 « caméra dans la maquette » (~1 min).

Nouveau format, pour tester la rétention :
  * chaque plan est une MAQUETTE EN PAPIER (image IA 16:9) plein écran, que la caméra parcourt en pose à pose
    (panoramique + zoom, slow in / slow out, léger dépassement à l'arrivée = principes de Lasseter) ;
  * une FRISE 1950 → 2025 reste en haut de l'écran : le pion OL saute d'une date à l'autre (anticipation, arc,
    écrasement) ; le spectateur sait toujours où il en est dans l'histoire ;
  * par-dessus, les infos clés en papier découpé (entrées en arc, tampons écrasés, compteurs) ;
  * 12 bruitages réels nouveaux (projecteur, machine à écrire, coup franc, tonnerre, champagne, roulement…).

  python3 episodes/ol_histoire/ol_histoire.py output/ol_histoire --stills [2,3]
  python3 episodes/ol_histoire/ol_histoire.py output/ol_histoire --cover
  python3 episodes/ol_histoire/ol_histoire.py output/ol_histoire
"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from story import *
from quiz import sub_button
from lasseter import ease, ease_out, ease_in, settle, stagger, arc, keys, squash, draw_sxy, enter, stamp, puff, hop, wave
from PIL import ImageFilter
import engine

TITLE = "~/légendes $ ./ol"
SLUG = "ol_histoire"
VOICE = [os.path.join(HERE, "voix", f"scene_{i}.mp3") for i in range(1, 12)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
IMG = os.path.join(HERE, "img")
PADS = [.45] + [.1]*10
WS, TEXTS = load_words(os.path.join(HERE, "alignement.json"))
def w(i, word, n=1, end=False):
    return PADS[i-1] + WS[i-1](word, n, end)

ROUGE = (206, 30, 46); BLEU = (16, 44, 110); BLANC = (250, 250, 246); NOIR = (30, 28, 28)
GOLD = (250, 196, 30); VERT = (40, 150, 80); INK = PAL["ink"]

# ------------------------------------------------------------------ caméra dans la maquette (pose à pose)
_base = {}
def _img(key):
    if key not in _base:
        im = Image.open(os.path.join(IMG, f"{key}.png")).convert("RGB")
        bh = H; bw = int(im.width*bh/im.height)
        im = im.resize((bw, bh), Image.BICUBIC).filter(ImageFilter.UnsharpMask(2.2, 70, 2))
        _base[key] = im
    return _base[key]

_vig = None
def _vignette():
    global _vig
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W]; r = ((xx/W - .5)**2*1.6 + (yy/H - .5)**2)
        a = np.clip((r - .12)*340, 0, 150).astype(np.uint8)
        v = np.zeros((H, W, 4), np.uint8); v[..., 3] = a; _vig = Image.fromarray(v, "RGBA")
    return _vig

def cam(cv, key, t, ks, gray=0.0, sep=0.0):
    """ks = [(t, (cx, cy, zoom)), …] : centre de la caméra en fraction de l'image, zoom >= 1 (1 = hauteur pleine).
    Interpolation slow-in / slow-out entre les poses (Lasseter : pose to pose + slow in/out)."""
    im = _img(key); cx, cy, z = keys(t, ks)
    cw, ch = W/z, H/z
    x0 = clamp(cx*im.width - cw/2, 0, im.width - cw); y0 = clamp(cy*im.height - ch/2, 0, im.height - ch)
    fr = im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
    if gray > 0: fr = Image.blend(fr, fr.convert("L").convert("RGB"), clamp(gray))
    if sep > 0:
        g = fr.convert("L"); s = Image.merge("RGB", (g.point(lambda v: min(255, int(v*1.08 + 18))), g.point(lambda v: int(v*.95 + 8)), g.point(lambda v: int(v*.78))))
        fr = Image.blend(fr, s, clamp(sep))
    cv.paste(fr, (0, 0)); cv.alpha_composite(_vignette()) if cv.mode == "RGBA" else cv.paste(_vignette(), (0, 0), _vignette())

def cut_punch(cv, t, t0, z=.06):
    """À chaque coupe : la caméra arrive un peu trop près puis se pose (follow-through)."""
    if t >= t0: engine.zoom_punch(cv, 1 + abs(settle(t, t0, z, 2.2, 6)))

# ------------------------------------------------------------------ frise 1950 → 2025 (fil rouge de rétention)
FX0, FX1, FY = 110, W - 110, 236
def yx(y): return FX0 + (FX1 - FX0)*(y - 1950)/75
_rib = None
def _ribbon():
    global _rib
    if _rib is None:
        _rib = Paper(rect_pts(FX1 - FX0 + 70, 30), PAL["cream"], "ribbon", rough=2.0)
    return _rib

def frise(cv, fr, t, y0, y1, t0, d=.55, lab=None):
    """Le pion OL saute de y0 à y1 à partir de t0 : tassement (anticipation), ARC, écrasement à l'arrivée."""
    _ribbon().draw(cv, fr, CX, FY, 1, 0)
    dd = ImageDraw.Draw(cv); f = font("mono", 26)
    for yr in (1950, 1975, 2000, 2025):
        x = yx(yr); dd.line([x, FY - 12, x, FY + 12], fill=INK, width=4); dd.text((x, FY + 34), str(yr), font=f, fill=BLANC, anchor="mm", stroke_width=4, stroke_fill=NOIR)
    if t < t0 - .1: x, yy, sx, sy, yr = yx(y0), FY, 1, 1, y0
    elif t < t0:     x, yy, sx, sy, yr = yx(y0), FY, 1.18, .8, y0
    elif t < t0 + d:
        u = ease((t - t0)/d); x, yy = arc((yx(y0), FY), (yx(y1), FY), u, -90 - .3*abs(yx(y1) - yx(y0)))
        sx, sy = .88, 1.14; yr = round(lerp(y0, y1, u))
    else:
        x, yy, yr = yx(y1), FY, y1; sx, sy = squash(t, t0 + d, .25)
    dd.rounded_rectangle([FX0, FY - 6, x, FY + 6], 6, fill=ROUGE)
    r = 30
    knob = Image.new("RGBA", (2*r + 8, 2*r + 8), (0, 0, 0, 0)); kd = ImageDraw.Draw(knob)
    kd.ellipse([4, 4, 2*r + 4, 2*r + 4], fill=ROUGE, outline=BLANC, width=5)
    kd.text((r + 4, r + 4), "OL", font=font("title", 30), fill=BLANC, anchor="mm")
    knob.info["anchor"] = (r + 4, 2*r + 8)
    blit_sxy(cv, knob, x, yy + r + 4, sx, sy)
    Label(lab or str(yr), f"fr{lab or yr}", font("title", 54), NOIR, GOLD, padx=16, pady=2, rough=2).draw(cv, fr, x, yy - 78, 1, -3)

# ------------------------------------------------------------------ labels
def K(txt, key, bg, fg=BLANC, size=96, rough=4):
    return Label(txt, key, font("title", size), fg, bg, padx=26, pady=6, rough=rough, maxw=980)
def note(txt, key, size=54, bg=PAL["cream"], fg=INK):
    return Label(txt, key, font("hand", size), fg, bg, padx=22, pady=8, rough=3, maxw=900)

# ------------------------------------------------------------------ SCÈNE 1 — hook : ruiné en D2 … 7 titres d'affilée
K1a, K1b = K("RUINÉ", "k1a", ROUGE, size=150), K("EN D2", "k1b", NOIR, size=110)
K1c = K("7 TITRES D'AFFILÉE", "k1c", GOLD, NOIR, 92); K1d = K("L'HISTOIRE DE LYON", "k1d", BLEU, size=86)
def s1(cv, fr, t, T):
    tq = w(1, "Quinze") - .12
    if t < tq:
        cam(cv, "1987", t, [(0, (.55, .5, 1.25)), (tq, (.5, .45, 1.05))], gray=.7)
        stamp(cv, fr, K1a, t, w(1, "ruiné") - .05, CX, 760, -8, 1.1)
        enter(cv, fr, K1b, t, w(1, "deuxième") - .1, CX + 120, 940, 4, frm=(500, 120), d=.3)
    else:
        cam(cv, "titre", t, [(tq, (.25, .45, 1.3)), (T, (.75, .4, 1.05))])
        cut_punch(cv, t, tq, .08)
        ts = w(1, "sept") - .08
        for k in range(7):                                  # 7 trophées : entrées décalées (overlapping), en ARC
            t0 = ts + stagger(k, .07)
            if t > t0:
                u = ease_out(prog(t, t0, .4)); px, py = arc((CX, 1500), (150 + k*130, 1180), u, -260)
                draw_star(cv, px, py, 50*(.4 + .6*u)*(1 + .3*settle(t, t0 + .4, .5)), 1, k, GOLD)
        stamp(cv, fr, K1c, t, w(1, "daffil") - .25, CX, 980, -3, 1)
        enter(cv, fr, K1d, t, w(1, "lhistoire") - .1, CX, 1420, 2, frm=(0, 400), d=.35)
        if t > ts: confetti(cv, fr, "c1", t - ts, 70, 3, [ROUGE, BLEU, BLANC, GOLD])
    frise(cv, fr, t, 1987, 2008, tq)

# ------------------------------------------------------------------ SCÈNE 2 — 1950 : 3 Coupes, 0 titre
K2a = K("1950", "k2a", NOIR, size=170); K2c = K("0 TITRE DE CHAMPION", "k2c", ROUGE, size=84)
K2cups = [note(y, f"k2y{y}", 60, GOLD) for y in ("1964", "1967", "1973")]
def s2(cv, fr, t, T):
    cam(cv, "1950", t, [(0, (.3, .55, 1.35)), (T*.55, (.55, .5, 1.15)), (T, (.75, .45, 1.05))], sep=.75)
    old_film(cv, fr, t, .6)
    enter(cv, fr, K2a, t, .08, CX, 640, -3, frm=(-600, -100), d=.35)
    tc = w(2, "trois") - .05
    for k, lab in enumerate(K2cups):                        # 3 Coupes de France, décalées, écrasées à l'arrivée
        enter(cv, fr, lab, t, tc + stagger(k, .16), 250 + k*290, 1000, (-5, 3, -2)[k], frm=(0, 500), d=.32)
    if t > tc: note("Coupes de France", "k2n", 48).draw(cv, fr, CX, 1110, 1, -1)
    stamp(cv, fr, K2c, t, w(2, "jamais") - .05, CX, 1300, -5, 1)
    tc50 = w(2, "cinquante", 2)
    if t < tc50 - .1: frise(cv, fr, t, 2008, 1950, .02, .6)
    else: frise(cv, fr, t, 1950, 2000, tc50, 1.0, None if t < tc50 + 1 else "50 ans")

# ------------------------------------------------------------------ SCÈNE 3 — 1987 : D2, dettes, Aulas rachète
K3a = K("1987", "k3a", NOIR, size=150); K3b = K("DETTES", "k3b", ROUGE, size=120); K3c = K("JEAN-MICHEL AULAS", "k3c", BLEU, size=80)
K3d = note("patron du logiciel", "k3d", 52)
def s3(cv, fr, t, T):
    tp = w(3, "Un") - .1
    if t < tp:
        cam(cv, "1987", t, [(0, (.35, .3, 1.5)), (tp, (.55, .55, 1.2))], gray=.35)
        tint(cv, .15)
        enter(cv, fr, K3a, t, .05, CX, 640, -3, frm=(500, -80), d=.3)
        stamp(cv, fr, K3b, t, w(3, "dettes") - .05, CX, 1150, 6, 1)
    else:
        cam(cv, "aulas", t, [(tp, (.62, .65, 1.6)), (w(3, "rachète"), (.55, .55, 1.25)), (T, (.5, .5, 1.1))])
        cut_punch(cv, t, tp)
        enter(cv, fr, K3d, t, w(3, "patron") - .05, CX - 160, 1180, -4, frm=(-500, 200), d=.3)
        stamp(cv, fr, K3c, t, w(3, "Jean-Michel") - .05, CX, 1400, -3, 1)
    frise(cv, fr, t, 2000, 1987, .05, .5)

# ------------------------------------------------------------------ SCÈNE 4 — plan OL Europe : Domenech, remontée 1989
K4a = K("PLAN « OL EUROPE »", "k4a", BLEU, size=88); K4b = K("RAYMOND DOMENECH", "k4b", ROUGE, size=74)
FLOORS = [("D2", (90, 90, 96)), ("D1", BLEU), ("EUROPE", GOLD)]
def s4(cv, fr, t, T):
    cam(cv, "aulas", t, [(0, (.3, .4, 1.4)), (T, (.2, .5, 1.6))], gray=.2)
    tint(cv, .45, (10, 20, 50))
    enter(cv, fr, K4a, t, .05, CX, 560, -2, frm=(0, -300), d=.3, h=0)
    # escalier en papier : D2 -> D1 -> EUROPE, le joueur-pion saute marche par marche
    steps = [(250, 1450), (540, 1220), (830, 990)]
    for k, ((lb, col), (x, y)) in enumerate(zip(FLOORS, steps)):
        enter(cv, fr, K(lb, f"k4f{k}", col, BLANC if k < 2 else NOIR, 64), t, .25 + stagger(k, .12), x, y + 90, 0, frm=(0, 600), d=.3)
    th = [w(4, "remonte") - .15, w(4, "Europe") - .1]
    pos = 0 if t < th[0] + .5 else 1
    tj = th[0]
    p0, p1 = steps[0], steps[1]
    if t >= tj:
        u = ease(prog(t, tj, .5)); px, py = arc(p0, p1, u, -200)
    else: px, py = p0
    _, sx, sy = hop(t, tj, 0, .5)
    L = KIT_PLAYER.render_layer(fr, .62, age=1, kit="ol", mood="cheer" if t > tj else "happy", arms=(150, 150) if t > tj else (25, 25), t=t)
    blit_sxy(cv, L, px, py + 40, sx, sy)
    stamp(cv, fr, K4b, t, w(4, "Domenech") - .25, CX, 1700, -3, .95)
    if t > tj + .5: arrow(ImageDraw.Draw(cv), (600, 1120), (800, 960), prog(t, tj + .5, .4), GOLD, 12, 4, 40, .3)
    frise(cv, fr, t, 1987, 1989, w(4, "deux") - .05, .5)
KIT_PLAYER = Player("olp2", hair=(50, 36, 28), skin=(226, 182, 146))

# ------------------------------------------------------------------ SCÈNE 5 — mai 2002 : Lyon 3-1 Lens, 1er titre
K5a = K("4 MAI 2002", "k5a", NOIR, size=110); K5b = K("DERNIÈRE JOURNÉE", "k5b", ROUGE, size=70)
K5d = K("1er TITRE !", "k5d", VERT, size=150)
def s5(cv, fr, t, T):
    tv = w(5, "Victoire") - .1
    cam(cv, "titre", t, [(0, (.5, .75, 1.6)), (tv, (.5, .55, 1.3)), (T, (.55, .35, 1.08))])
    if t < tv: tint(cv, .35)
    enter(cv, fr, K5a, t, .05, CX, 600, -3, frm=(-500, 0), d=.3)
    enter(cv, fr, K5b, t, w(5, "dernière") - .05, CX, 740, 2, frm=(500, 0), d=.3)
    # tableau d'affichage : LYON 0-0 LENS, les chiffres tombent (compteur)
    sc = (3, 1) if t > tv + .2 else (0, 0)
    if t > w(5, "Lens") - .2:
        u = ease_out(prog(t, w(5, "Lens") - .2, .35)); y = lerp(1500, 1180, u)
        board = Label(f"LYON  {sc[0]} – {sc[1]}  LENS", "k5sc" + str(sc), font("title", 88), GOLD, NOIR, padx=34, pady=12, rough=3)
        sx, sy = squash(t, tv + .2, .25); draw_sxy(cv, fr, board, CX, y, sx, sy, 0)
    stamp(cv, fr, K5d, t, w(5, "premier") - .05, CX, 1450, -6, 1)
    if t > tv: camera_flashes(cv, fr, "f5", t - tv, 1.8, 10)
    if t > w(5, "premier"): confetti(cv, fr, "c5", t - w(5, "premier"), 90, 3, [ROUGE, BLEU, BLANC, GOLD])
    frise(cv, fr, t, 1989, 2002, .05, .55)

# ------------------------------------------------------------------ SCÈNE 6 — Juninho : 44 coups francs
K6a = K("JUNINHO", "k6a", ROUGE, size=130); K6c = note("coups francs marqués", "k6c", 58, GOLD)
def s6(cv, fr, t, T):
    tf = w(6, "frappe") - .1
    cam(cv, "coupfranc", t, [(0, (.3, .55, 1.55)), (tf, (.32, .5, 1.3)), (tf + .9, (.72, .42, 1.25)), (T, (.75, .45, 1.1))])
    cut_punch(cv, t, tf + .9, .07)
    enter(cv, fr, K6a, t, w(6, "Juninho") - .1, CX, 620, -4, frm=(-600, 100), d=.32)
    if t > tf + .9: flash(cv, .7*(1 - prog(t, tf + .9, .2)))
    tn = w(6, "quarante") - .1
    if t > tn:
        n = counter(0, 44, prog(t, tn, .7)); s = 1 + .25*settle(t, tn + .7, .6)
        Label(n, "k6n" + n, font("title", 260), NOIR, GOLD, padx=30, pady=0, rough=4).draw(cv, fr, CX, 1250, s, -4)
        enter(cv, fr, K6c, t, tn + .3, CX, 1460, 2, frm=(0, 300), d=.3)
    frise(cv, fr, t, 2002, 2001, .05, .4, "2001-09")

# ------------------------------------------------------------------ SCÈNE 7 — 7 titres d'affilée
K7b = K("PERSONNE N'A FAIT MIEUX", "k7b", ROUGE, size=74)
YEARS7 = list(range(2002, 2009))
def s7(cv, fr, t, T):
    cam(cv, "trophees", t, [(0, (.5, .5, 1.6)), (w(7, "deux") - .1, (.5, .47, 1.15)), (T, (.5, .45, 1.05))])
    t1 = w(7, "deux") - .05; t2 = w(7, "huit") + .1
    for k, yr in enumerate(YEARS7):                         # chaque trophée « saute » à son tour (hop + étoile)
        tk = lerp(t1, t2, k/6)
        if t > tk:
            x = 145 + k*132; dy, sx, sy = hop(t, tk, 60, .35)
            Label(str(yr), f"k7y{yr}", font("title", 44), NOIR, GOLD, padx=8, pady=2, rough=2).draw(cv, fr, x, 1230 + dy, 1, (k % 2)*4 - 2)
            if t < tk + .3: flash(cv, .12)
    if t > t2:
        u = ease_out(prog(t, t2, .3)); Label("× 7", "k7x", font("title", 220), BLANC, ROUGE, padx=26, pady=0, rough=4).draw(cv, fr, CX, 620, lerp(.3, 1, u)*(1 + .2*settle(t, t2 + .3, .5)), -5)
    stamp(cv, fr, K7b, t, w(7, "Personne") - .05, CX, 1500, -3, .95)
    frise(cv, fr, t, 2002, 2008, t1, t2 - t1)

# ------------------------------------------------------------------ SCÈNE 8 — l'académie
NAMES8 = ["Benzema", "Lacazette", "Fekir", "Tolisso"]
K8a = K("100 % FORMÉS À LYON", "k8a", BLEU, size=80)
def s8(cv, fr, t, T):
    cam(cv, "academie", t, [(0, (.15, .6, 1.45)), (T, (.8, .55, 1.25))])
    enter(cv, fr, K("L'ACADÉMIE", "k8t", NOIR, size=110), t, .05, CX, 580, -3, frm=(0, -300), d=.3, h=0)
    pos = [(300, 900), (780, 1040), (300, 1200), (780, 1360)]
    for k, nm in enumerate(NAMES8):
        tk = w(8, nm) - .12; x, y = pos[k]
        enter(cv, fr, K(nm.upper(), f"k8n{k}", (ROUGE, BLEU, ROUGE, BLEU)[k], size=72), t, tk, x, y, (-4, 3, 2, -3)[k], frm=(-500 if x < CX else 500, 100), d=.3)
        if k == 0 and t > w(8, "Ballon") - .1:
            u = ease_out(prog(t, w(8, "Ballon") - .1, .35))
            draw_ballon_or(cv, fr, x + 250, y - 40 + 20*wave(t, 0, 1, .8), .55*u)
    stamp(cv, fr, K8a, t, w(8, "Tous") - .05, CX, 1620, -3, .95)
    frise(cv, fr, t, 2008, 2005, .05, .5, "2005")

# ------------------------------------------------------------------ SCÈNE 9 — les Lyonnaises : 8 C1
K9a = K("LES LYONNAISES", "k9a", BLEU, size=110); K9c = K("RECORD ABSOLU", "k9c", ROUGE, size=96)
def s9(cv, fr, t, T):
    cam(cv, "feminines", t, [(0, (.5, .7, 1.5)), (T, (.5, .4, 1.1))])
    enter(cv, fr, K9a, t, w(9, "Lyonnaises") - .1, CX, 600, -3, frm=(0, -300), d=.3, h=0)
    th = w(9, "huit") - .1
    for k in range(8):                                     # 8 étoiles en couronne, entrées en arc décalées
        t0 = th + stagger(k, .06)
        if t > t0:
            a = -math.pi/2 + k*2*math.pi/8; tx, ty = CX + 330*math.cos(a), 1150 + 330*math.sin(a)
            u = ease_out(prog(t, t0, .4)); px, py = arc((CX, 1150), (tx, ty), u, -120)
            draw_star(cv, px, py, 48*(1 + .3*settle(t, t0 + .4, .5)), 1, k, GOLD)
    if t > th:
        u = ease_out(prog(t, th, .3)); Label("8 C1", "k9n", font("title", 170), NOIR, GOLD, padx=24, pady=0, rough=4).draw(cv, fr, CX, 1150, lerp(.3, 1, u)*(1 + .15*settle(t, th + .3, .5)), -4)
    stamp(cv, fr, K9c, t, w(9, "Record") - .05, CX, 1620, -4, 1)
    if t > w(9, "Record"): confetti(cv, fr, "c9", t - w(9, "Record"), 80, 3, [GOLD, BLANC, ROUGE])
    frise(cv, fr, t, 2005, 2022, .05, .6, "2011-22")

# ------------------------------------------------------------------ SCÈNE 10 — juin 2025 : rétrogradé… sauvé en appel
K10a = K("JUIN 2025", "k10a", NOIR, size=130); K10b = K("ENVOYÉ EN LIGUE 2", "k10b", ROUGE, size=88)
K10c = K("SAUVÉ EN APPEL !", "k10c", VERT, size=110); K10d = note("15 jours plus tard", "k10d", 58)
def s10(cv, fr, t, T):
    tt = w(10, "tonnerre") - .05; ts = w(10, "Quinze") - .1
    cam(cv, "dncg", t, [(0, (.5, .3, 1.4)), (tt, (.5, .4, 1.2)), (ts, (.45, .55, 1.3)), (T, (.5, .5, 1.05))], gray=.3 if t < ts else 0)
    if tt < t < tt + .5:
        flash(cv, .9*(1 - prog(t, tt, .25)), (235, 235, 255)); shake(cv, t - tt, 20*(1 - prog(t, tt, .5)))
    if t < ts and t > tt: siren_lights(cv, t, .25)
    enter(cv, fr, K10a, t, .05, CX, 600, -3, frm=(-600, 0), d=.3)
    if t < ts: stamp(cv, fr, K10b, t, w(10, "Ligue") - .1, CX, 1150, 5, 1)
    else:
        enter(cv, fr, K10d, t, ts, CX, 900, -2, frm=(0, -300), d=.3)
        stamp(cv, fr, K10c, t, w(10, "sauvé") - .05, CX, 1200, -5, 1.05)
        if t > w(10, "sauvé"): confetti(cv, fr, "c10", t - w(10, "sauvé"), 80, 3, [VERT, BLANC, GOLD])
    frise(cv, fr, t, 2022, 2025, .05, .5)

# ------------------------------------------------------------------ SCÈNE 11 — récap éclair + question + abonnement
RECAP = [("1987", "RUINÉ", ROUGE), ("titre", "INTOUCHABLE", GOLD), ("dncg", "AU BORD DU GOUFFRE", NOIR)]
def s11(cv, fr, t, T):
    ts = [0, w(11, "intouchable") - .1, w(11, "gouffre") - .25, w(11, "Tu") - .1]
    k = max(i for i in range(3) if t >= ts[i]) if t < ts[3] else 3
    if k < 3:
        key, txt, col = RECAP[k]
        cam(cv, key, t, [(ts[k], (.5, .5, 1.45)), (ts[k + 1], (.5, .5, 1.2))], gray=.5 if k != 1 else 0)
        cut_punch(cv, t, ts[k], .08)
        stamp(cv, fr, K(txt, f"k11r{k}", col, NOIR if col == GOLD else BLANC, 100), t, ts[k] + .05, CX, 960, (-5, 3, -3)[k], 1)
    else:
        cam(cv, "titre", t, [(ts[3], (.5, .45, 1.3)), (T, (.5, .45, 1.1))]); tint(cv, .45)
        enter(cv, fr, K("TON AVIS ?", "k11q", BLANC, NOIR, 130), t, ts[3], CX, 700, -3, frm=(0, -300), d=.3, h=0)
        tc = w(11, "commentaire") - .15
        if t > tc: speech_bubble(cv, fr, "k11b", "Aucun, à part l'OL !", 540, 1050, ease_out(prog(t, tc, .3)), (1, 1), 62)
        ta = w(11, "abonne")
        sub_button(cv, fr, CX, 1450, t, ta - .1, ta + .25)
    frise(cv, fr, t, 1950, 2025, .05, 1.2, "1950-2025")

# ------------------------------------------------------------------ scènes + bruitages (nouvelle banque, peu de répétitions)
def SC(name, n, fn, sfx, trans=None, trans_dur=.25, pad_out=.2):
    return Scene(name, TEXTS[n-1], fn, sfx, pad_in=PADS[n-1], pad_out=pad_out, trans=trans, trans_dur=trans_dur)
SCENES = [
    SC("hook", 1, s1, [(.0, "braam", 1.0), (w(1, "ruiné"), "stamp", .9), (w(1, "deuxième"), "crumple", .7), (w(1, "Quinze") - .15, "whoosh_up", .7),
                       (w(1, "Quinze") - .05, "goal_roar", .8), (w(1, "sept"), "fanfare", .7), (w(1, "daffil") - .2, "stamp", .8), (w(1, "lhistoire"), "lion", .6)]),
    SC("1950", 2, s2, [(.0, "projector", .9), (.1, "rip", .4), (w(2, "trois"), "pop", .5), (w(2, "trois") + .16, "pop", .5), (w(2, "trois") + .32, "pop", .5),
                       (w(2, "jamais"), "gavel", .8)], trans="tear_v", trans_dur=.4),
    SC("1987", 3, s3, [(.0, "thunder", .35), (.05, "typewriter", .45), (w(3, "dettes"), "stamp", .9), (w(3, "dettes") + .1, "coin", .4),
                       (w(3, "Un") - .1, "whoosh", .6), (w(3, "rachète"), "scribble", .7), (w(3, "Jean-Michel"), "camera", .9)], trans="whip"),
    SC("ol_europe", 4, s4, [(.0, "paper", .6), (.25, "pop2", .4), (.37, "pop2", .4), (.49, "pop2", .4), (w(4, "Domenech") - .2, "stamp", .8),
                            (w(4, "remonte") - .15, "whoosh_up", .6), (w(4, "remonte") + .35, "thud", .6), (w(4, "Europe"), "sparkle", .5)], trans="tear_h", trans_dur=.45),
    SC("2002", 5, s5, [(.0, "crowd_long", .5), (.05, "drumroll", .8), (w(5, "Lens") - .2, "tictac", .5), (w(5, "Victoire"), "freekick", .7),
                       (w(5, "Victoire") + .2, "goal_roar", 1.0), (w(5, "premier"), "champagne", .8), (w(5, "premier"), "stamp", .9)], trans="punch", trans_dur=.3),
    SC("juninho", 6, s6, [(.0, "whoosh", .5), (w(6, "Juninho"), "camera", .6), (w(6, "frappe") + .4, "freekick", 1.0), (w(6, "frappe") + .9, "goal_roar", .8),
                          (w(6, "quarante") - .1, "cash", .6)], trans="whip"),
    SC("7_titres", 7, s7, [(.0, "elevator", .5)] + [(lerp(w(7, "deux") - .05, w(7, "huit") + .1, k/6), "coin", .45) for k in range(7)]
       + [(w(7, "huit") + .1, "fanfare", .8), (w(7, "Personne"), "stamp", .8)], trans="tear_d", trans_dur=.4),
    SC("formation", 8, s8, [(.0, "whistle", .6)] + [(w(8, n) - .12, "kick", .5) for n in NAMES8] + [(w(8, "Ballon"), "sparkle", .7), (w(8, "Tous"), "stamp", .8)], trans="whip"),
    SC("lyonnaises", 9, s9, [(.0, "crowd_long", .5), (w(9, "huit") - .1, "riser", .5), (w(9, "huit"), "sparkle", .7), (w(9, "Record"), "stamp", .9),
                             (w(9, "Record"), "goal_roar", .8)], trans="punch", trans_dur=.3),
    SC("dncg", 10, s10, [(.0, "monitor", .4), (w(10, "tonnerre") - .05, "thunder", 1.0), (w(10, "Ligue") - .1, "gavel", .9), (w(10, "Ligue"), "siren", .3, 2.0),
                         (w(10, "Quinze") - .15, "rewind", .6), (w(10, "sauvé"), "stamp", 1.0), (w(10, "sauvé") + .05, "crowd", .8)], trans="tear_v", trans_dur=.4),
    SC("fin", 11, s11, [(.0, "braam", .6), (w(11, "intouchable") - .1, "fanfare", .5), (w(11, "gouffre") - .25, "glitch", .6), (w(11, "Tu") - .1, "whoosh", .5),
                        (w(11, "commentaire"), "notif", .9), (w(11, "abonne"), "pop2", .7), (w(11, "abonne") + .25, "notif", .8)], trans="whip", pad_out=1.3),
]

def cover(path):
    cv = background(0, TITLE)
    cam(cv, "titre", 0, [(0, (.5, .45, 1.15))])
    tint(cv, .25)
    Label("RUINÉ EN D2…", "cv1", font("title", 110), BLANC, ROUGE, padx=30, pady=8, rough=4).draw(cv, 0, CX, 560, 1, -4)
    Label("…7 FOIS CHAMPION", "cv2", font("title", 100), NOIR, GOLD, padx=30, pady=8, rough=4).draw(cv, 0, CX, 1180, 1, 3)
    Label("DE SUITE ?!", "cv3", font("title", 100), NOIR, GOLD, padx=30, pady=8, rough=4).draw(cv, 0, CX, 1330, 1, -2)
    Label("L'HISTOIRE DE LYON", "cv4", font("title", 74), BLANC, BLEU, padx=24, pady=6, rough=3).draw(cv, 0, CX, 1560, 1, 2)
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
        p = os.path.join(out, f"oh_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
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
