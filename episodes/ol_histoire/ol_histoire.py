"""L'histoire de l'Olympique lyonnais (chronologique, ~1 min) — animée selon les principes de John Lasseter (engine/lasseter.py) :
anticipation avant chaque action, écrasement / étirement, arcs, slow in / slow out, dépassement amorti (follow-through),
entrées décalées (overlapping), actions secondaires (poussière, confettis, oscillations), une seule idée lisible par plan.
DA : papier découpé ; « un poil d'images » : 5 photos de maquette en papier (IA) épinglées comme des polaroïds.

  python3 episodes/ol_histoire/ol_histoire.py output/ol_histoire --stills [2,3]
  python3 episodes/ol_histoire/ol_histoire.py output/ol_histoire --cover
  python3 episodes/ol_histoire/ol_histoire.py output/ol_histoire
"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from story import *
from quiz import sub_button
from lasseter import ease, ease_out, settle, stagger, arc, keys, squash, draw_sxy, enter, stamp, puff, hop, wave
from PIL import ImageFilter
import engine

TITLE = "~/légendes $ ./ol"
SLUG = "ol_histoire"
VOICE = [os.path.join(HERE, "voix", f"scene_{i}.mp3") for i in range(1, 12)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
IMG = os.path.join(ROOT, "episodes", "ol_anecdotes", "img")
PADS = [.55] + [.12]*10
WS, TEXTS = load_words(os.path.join(HERE, "alignement.json"))
def w(i, word, n=1, end=False):
    return PADS[i-1] + WS[i-1](word, n, end)

ROUGE = (206, 30, 46); BLEU = (16, 44, 110); BLEU_D = (8, 22, 60); BLANC = (250, 250, 246); NOIR = (30, 28, 28)
GOLD = (250, 196, 30); VERT = (40, 150, 80); INK = PAL["ink"]

OLP = Player("olp", hair=(50, 36, 28), skin=(226, 182, 146))
AUL = Player("aulas", hair=(150, 146, 140), skin=(232, 196, 166))
DOM = Player("domenech", hair=(70, 52, 40), skin=(230, 190, 156))
KIDS = [Player(f"olk{k}", hair=h, skin=s) for k, (h, s) in enumerate((((26, 22, 20), (176, 124, 92)), ((24, 20, 18), (120, 82, 60)), ((30, 24, 20), (196, 150, 116)), ((90, 64, 40), (232, 196, 166))))]

def bg_stripes(cv, fr, key, c1, c2, t):
    stage_fill(cv, fr, c1, key); d = ImageDraw.Draw(cv); off = (t*50) % 240
    for k in range(-4, 13):
        x = k*240 + off; d.polygon([(x, 0), (x + 120, 0), (x + 120 - 700, 1920), (x - 700, 1920)], fill=c2)

# ------------------------------------------------------------------ polaroïd : entrée en arc + dépassement + respiration
_pol = {}
def polaroid_sprite(key, wd=860):
    if key not in _pol:
        im = Image.open(os.path.join(IMG, f"{key}.png")).convert("RGB"); hh = int(wd*im.height/im.width)
        b = 22; card = Image.new("RGBA", (wd + 2*b, hh + 2*b + 46), (250, 248, 240, 255))
        card.paste(im.resize((wd, hh), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.4, 50, 2)), (b, b))
        d = ImageDraw.Draw(card); d.rectangle([card.width/2 - 70, -10, card.width/2 + 70, 26], fill=(236, 224, 170, 230))   # scotch
        card.info["anchor"] = (card.width/2, card.height/2); _pol[key] = card
    return _pol[key]

def polaroid(cv, fr, key, t, t0, x, y, rot=-3, frm=(-700, 240)):
    """Entrée en ARC depuis le côté (étirement dans la vitesse), atterrissage écrasé, rotation qui dépasse puis se pose
    (follow-through), légère respiration ensuite (action secondaire)."""
    spr = polaroid_sprite(key)
    if t < t0 - .08: return
    enter(cv, fr, spr, t, t0, x, y + 2*wave(t, 0, 1, .4), rot + .6*wave(t, 1, 1, .3), frm=frm, d=.42, h=-160)

# ------------------------------------------------------------------ personnage : saut avec anticipation + écrasement
def player_hop(cv, fr, P, x, y, s, kit, t, th=None, h=170, arms=None, mood="happy", **kw):
    dy, sx, sy = hop(t, th, h) if th is not None else (0, 1, 1)
    up = th is not None and th - .02 < t < th + .55
    L = P.render_layer(fr, s, age=1, kit=kit, mood="cheer" if up else mood, arms=arms or ((160, 160) if up else (25, 25)), t=t, **kw)
    blit_sxy(cv, L, x, y + dy, sx, sy)

# ------------------------------------------------------------------ labels
LYON = Label("LYON", "hlyon", font("title", 230), BLANC, ROUGE, padx=40, pady=0, rough=4)
K1a = STAMP("RUINÉ", "hk1a", ROUGE, 130); K1b = STAMP("7 FOIS DE SUITE !", "hk1b", VERT, 100)
K2a = KW("1950", "hk2a", INK, size=170); K2b = TAG("Coupe de France 1964 · 1967 · 1973", "hk2b", PAL["paper"], INK, 50)
K2c = STAMP("0 TITRE DE CHAMPION", "hk2c", ROUGE, 84)
K3a = KW("1987", "hk3a", INK, size=170); K3b = STAMP("DEUXIÈME DIVISION", "hk3b", ROUGE, 84); K3c = TAG("criblé de dettes", "hk3c", PAL["paper"], INK, 56)
K3d = Label("JEAN-MICHEL AULAS", "hk3d", font("title", 80), BLANC, BLEU, padx=26, pady=6, rough=3)
K4a = KW("PLAN « OL-EUROPE »", "hk4a", BLANC, BLEU, 90); K4b = Label("RAYMOND DOMENECH", "hk4b", font("title", 70), BLANC, ROUGE, padx=22, pady=4, rough=3)
K5a = KW("2002", "hk5a", INK, size=170); K5b = STAMP("1er TITRE !", "hk5b", VERT, 130)
K6a = KW("JUNINHO", "hk6a", BLANC, ROUGE, 130); K6b = TAG("coups francs directs", "hk6b", GOLD, INK, 60)
K7a = KW("7 TITRES D'AFFILÉE", "hk7a", INK, size=90); K7b = STAMP("RECORD DE FRANCE", "hk7b", ROUGE, 100)
K8a = KW("CENTRE DE FORMATION", "hk8a", BLANC, BLEU, 80)
K9a = KW("LES LYONNAISES", "hk9a", BLANC, BLEU, 100); K9b = STAMP("RECORD D'EUROPE", "hk9b", ROUGE, 100)
K10a = KW("JUIN 2025", "hk10a", INK, size=130); K10b = STAMP("RÉTROGRADÉ EN L2", "hk10b", ROUGE, 100); K10c = STAMP("SAUVÉ !", "hk10c", VERT, 180)
K11a = KW("TON AVIS ?", "hk11a", BLANC, NOIR, 130)

# ------------------------------------------------------------------ SCÈNE 1 — hook : ruiné en D2… 7 fois champion
def s1(cv, fr, t, T):
    tq = w(1, "Quinze") - .1
    up = prog(t, tq, .5)                                    # le fond passe du gris (ruine) au bleu (sommet)
    stage_fill(cv, fr, (60, 60, 66), "hs1a")
    if up > 0: bg_stripes(cv, fr, "hs1b", BLEU_D, BLEU, t); grayscale(cv, 1 - ease(up))
    # « LYON » : anticipation (tassé) puis étiré en montant, écrasé à l'arrivée, rotation qui dépasse
    enter(cv, fr, LYON, t, .02, CX, 330, -3, frm=(0, -260), d=.32, h=0)
    floor_panel(cv, fr, CX, 760, "D2" if t < tq + .3 else "L1", t, t < tq, 1.6, 1)
    stamp(cv, fr, K1a, t, w(1, "ruiné") - .05, CX + 250, 620, -10, .9)
    sad = t < tq
    player_hop(cv, fr, OLP, CX, 1700, .95, "ol", t, th=tq + .25 if not sad else None, mood="sad" if sad else "happy", look=(0, 1) if sad else (0, 0))
    ts = w(1, "sept") - .05                                 # 7 étoiles qui jaillissent en ARC, décalées (overlapping)
    for k in range(7):
        t0 = ts + stagger(k, .06)
        if t > t0:
            u = ease_out(prog(t, t0, .45)); px, py = arc((CX, 1250), (150 + k*130, 1000), u, -260)
            draw_star(cv, px, py, 46*(.4 + .6*u)*(1 + .25*settle(t, t0 + .45, .5)), 1, t*1.5 + k, GOLD)
    stamp(cv, fr, K1b, t, w(1, "suite") - .1, CX, 1430, -4)
    if t > ts: confetti(cv, fr, "hc1", t - ts, 80, 3, [ROUGE, BLEU, BLANC, GOLD])
    impact(cv, t, .45, 18); drift(cv, t, T, .03)

# ------------------------------------------------------------------ SCÈNE 2 — 1950 : naissance, des Coupes mais 0 titre
def s2(cv, fr, t, T):
    stage_fill(cv, fr, (200, 186, 156), "hs2")
    enter(cv, fr, K2a, t, .05, CX, 330, -3, frm=(-500, 0), h=-120)
    tb = w(2, "naissance") - .1
    # le petit joueur jongle : le ballon suit un ARC, s'écrase sur le pied (squash), le joueur se tasse à chaque contact
    x0 = CX - 200; per = .62; k = int(max(0, t - tb)//per); ph = ((t - tb) % per)/per if t > tb else 0
    dy, sx, sy = (0, 1, 1)
    if t > tb and ph < .12: sx, sy = 1.06, .94                 # tassement au contact
    L = OLP.render_layer(fr, .8, age=.6, kit="ol", mood="happy", arms=(30, 30), t=t, kid_hair=True)
    blit_sxy(cv, L, x0, 1720, sx, sy)
    if t > tb:
        bx, by = arc((x0 + 40, 1600), (x0 + 40, 1600), ph, -320); bsx, bsy = (1.15, .85) if ph < .08 or ph > .92 else (.92, 1.1)
        draw_ball(cv, fr, bx + 20*math.sin(k), by, .5*bsy, t*400)
    tc = w(2, "Coupes") - .1
    for k in range(3):                                        # 3 Coupes de France : entrées décalées, chacune écrasée à l'arrivée
        t0 = tc + stagger(k, .12)
        if t > t0 - .08:
            u = ease_out(prog(t, t0, .35)); sxk, syk = squash(t, t0 + .35, .25)
            blit_sxy(cv, CUP.v[0] if hasattr(CUP, "v") else CUP, 640 + k*150, lerp(1200, 1080, u), .55*sxk, .55*syk*u)
    show(cv, fr, K2b, t, tc + .4, None, CX + 120, 1260, 2)
    stamp(cv, fr, K2c, t, w(2, "jamais") - .05, CX, 600, -5)
    old_film(cv, fr, t, .8); drift(cv, t, T, .03)

# ------------------------------------------------------------------ SCÈNE 3 — 1987 : D2, dettes ; Aulas rachète
def s3(cv, fr, t, T):
    bg_stripes(cv, fr, "hs3", (50, 50, 56), (64, 64, 70), t)
    ta = w(3, "Aulas") - .5
    polaroid(cv, fr, "p5", t, .05, CX, 760, -3, frm=(-760, 300))
    enter(cv, fr, K3a, t, .1, 230, 300, -6, frm=(-300, -200))
    stamp(cv, fr, K3b, t, w(3, "deuxième") - .05, CX, 1150, 4)
    show(cv, fr, K3c, t, w(3, "dettes") - .1, None, CX + 120, 1270, -2)
    if t < ta + .1: grayscale(cv, .75)
    tr = w(3, "rachète") - .1                                 # Aulas entre en sautant (anticipation + arc + écrasement)
    if t > tr - .15:
        u = ease_out(prog(t, tr, .5)); x = lerp(1300, 820, u)
        dy, sx, sy = hop(t, tr, 150, .5)
        L = AUL.render_layer(fr, .8, age=1, kit="suit", mood="determined" if t < tr + .5 else "happy", arms=(20, 150) if t > tr + .5 else (25, 25), t=t)
        blit_sxy(cv, L, x, 1820 + dy, sx, sy)
    if t > ta: enter(cv, fr, K3d, t, ta + .35, CX - 60, 1420, -2, frm=(0, 220))
    drift(cv, t, T, .03)

# ------------------------------------------------------------------ SCÈNE 4 — plan OL-Europe : D2 → D1 → Europe ; Domenech
def s4(cv, fr, t, T):
    stage_fill(cv, fr, (236, 228, 206), "hs4"); d = ImageDraw.Draw(cv)
    for k in range(14): d.line([(0, 200 + k*120), (W, 200 + k*120)], fill=(200, 210, 230), width=3)    # papier quadrillé
    enter(cv, fr, K4a, t, .05, CX, 300, -2, frm=(0, -250), h=0)
    pts = [(220, 1180), (540, 860), (860, 540)]
    lab = [("D2", ROUGE), ("D1", BLEU), ("EUROPE", GOLD)]
    for k, ((x, y), (txt, c)) in enumerate(zip(pts, lab)):
        t0 = w(4, "remonter") - .2 + stagger(k, .55) if k < 2 else w(4, "Coupe") - .1
        if k > 0 and t > t0 - .35:                          # la flèche se dessine (slow in / slow out)
            u = ease(prog(t, t0 - .35, .35)); p0 = pts[k - 1]
            pencil_line(d, [arc(p0, (x, y), v/10*u, -90) for v in range(11)], 1, NOIR, 8, k, 1.0)
        LBLk = LBL(txt, f"h4p{k}", font("title", 70 if k < 2 else 60), BLANC if k < 2 else NOIR, c, padx=18, pady=4, rough=3)
        enter(cv, fr, LBLk, t, t0, x, y, (-4, 3, -2)[k], frm=(0, 200))
    if t > w(4, "Coupe"): draw_star(cv, 860, 430, 50*(1 + .3*settle(t, w(4, "Coupe"), .6)), 1, t, GOLD)
    td = w(4, "Domenech") - .4
    if t > td - .1:
        player_hop(cv, fr, DOM, 300, 1760, .78, "coach", t, th=td, h=120, arms=(20, 130))
        enter(cv, fr, K4b, t, td + .2, 650, 1480, 3, frm=(300, 0))
    drift(cv, t, T, .03)

# ------------------------------------------------------------------ SCÈNE 5 — 2002 : premier titre
def s5(cv, fr, t, T):
    stadium_like(cv, fr, t)
    enter(cv, fr, K5a, t, .05, CX, 300, -3, frm=(-400, 0))
    tp = w(5, "premier") - .2
    # le joueur saute (anticipation : tassement 0,12 s) ; la coupe suit avec un léger retard (overlapping action)
    dy, sx, sy = hop(t, tp, 200, .6)
    L = OLP.render_layer(fr, .85, age=1, kit="ol", mood="cheer" if t > tp - .1 else "determined", arms=(165, 165) if t > tp - .1 else (40, 40), t=t)
    blit_sxy(cv, L, CX, 1800 + dy, sx, sy)
    lag = hop(t - .06, tp, 200, .6)[0]
    CUP.draw(cv, fr, CX, 1800 + lag - 850*.85 + 6*wave(t, 2, 1, 1.2), .8, 3*wave(t, 3, 1, .8))
    stamp(cv, fr, K5b, t, w(5, "champion") - .05, CX, 560, -5)
    show(cv, fr, TAG("et ce n'est que le début…", "h5t", GOLD, INK, 56), t, w(5, "début") - .3, None, CX, 720, 2)
    if t > tp: confetti(cv, fr, "hc5", t - tp, 100, 3, [ROUGE, BLEU, BLANC, GOLD]); camera_flashes(cv, fr, "hf5", t - tp, 1.2, 8)
    drift(cv, t, T, .03)

def stadium_like(cv, fr, t):
    stage_fill(cv, fr, BLEU_D, "hstad"); d = ImageDraw.Draw(cv)
    for row in range(7):
        ry = 520 + row*66
        for k in range(18 + row):
            x = 50 + k*(980/(17 + row)); j = 5*abs(math.sin(t*6 + k*1.3 + row))
            d.ellipse([x - 16, ry - 16 - j, x + 16, ry + 16 - j], fill=(ROUGE, BLANC, BLEU)[(k + row) % 3])
    d.rectangle([0, 1080, W, H], fill=(46, 120, 70)); d.line([(0, 1080), (W, 1080)], fill=BLANC, width=6)

# ------------------------------------------------------------------ SCÈNE 6 — Juninho : 44 coups francs
def s6(cv, fr, t, T):
    bg_stripes(cv, fr, "hs6", BLEU_D, BLEU, t)
    polaroid(cv, fr, "p4", t, .02, CX, 780, 3, frm=(760, 260))
    enter(cv, fr, K6a, t, w(6, "Juninho") - .15, CX, 300, -3, frm=(0, -250), h=0)
    tq = w(6, "quarante-quatre") - .05
    if t > tq - .08:                                        # le compteur arrive en arc puis compte (slow in / slow out)
        n = int(round(44*ease(prog(t, tq, .9))))
        enter(cv, fr, LBL(str(n), "h6n", font("title", 220), NOIR, GOLD, padx=30, pady=0, rough=3), t, tq, 320, 1340, -5, frm=(-300, 200))
        enter(cv, fr, K6b, t, tq + .2, 700, 1340, 3, frm=(300, 200))
    tm = w(6, "machine") - .1
    if t > tm:                                              # le ballon file en ARC à travers l'écran, étiré par la vitesse
        u = prog(t, tm, .5)
        if u < 1:
            bx, by = arc((-60, 1600), (1140, 1450), ease(u), -420); st = 1 + .4*math.sin(u*math.pi)
            blit_sxy(cv, BALL.v[0] if hasattr(BALL, "v") else BALL, bx, by, .7*st, .7/st, -40)
    drift(cv, t, T, .03)

# ------------------------------------------------------------------ SCÈNE 7 — 7 titres d'affilée
def s7(cv, fr, t, T):
    bg_stripes(cv, fr, "hs7", BLEU_D, BLEU, t)
    polaroid(cv, fr, "p3", t, .02, CX, 760, -2, frm=(-760, 260))
    enter(cv, fr, K7a, t, .05, CX, 300, -2, frm=(0, -250), h=0)
    ty = w(7, "deux") - .15
    for k, yr in enumerate(range(2002, 2009)):              # les 7 années tombent en arc, décalées, s'écrasent et se posent
        t0 = ty + stagger(k, .16)
        x, y = 150 + (k % 4)*260, 1230 + (k // 4)*110
        enter(cv, fr, LBL(str(yr), f"h7y{yr}", font("title", 64), NOIR, GOLD, padx=12, pady=0, rough=2), t, t0, x, y,
              (-5, 3, -2, 4, 5, -3, 2)[k], frm=(0, -500), d=.3, h=0)
    stamp(cv, fr, K7b, t, w(7, "record") - .05, CX, 1500, -4)
    if t > ty: confetti(cv, fr, "hc7", t - ty, 70, 3, [ROUGE, BLEU, BLANC, GOLD])
    drift(cv, t, T, .03)

# ------------------------------------------------------------------ SCÈNE 8 — centre de formation : 4 pépites
NAMES8 = ["BENZEMA", "LACAZETTE", "FEKIR", "TOLISSO"]
def s8(cv, fr, t, T):
    stage_fill(cv, fr, (120, 170, 120), "hs8"); d = ImageDraw.Draw(cv)
    d.rectangle([140, 820, 940, 1200], fill=(236, 226, 200), outline=NOIR, width=6)
    for k in range(6): d.rectangle([190 + k*125, 880, 270 + k*125, 980], fill=(170, 206, 220), outline=NOIR, width=4)
    d.rectangle([0, 1200, W, H], fill=(70, 150, 84))
    enter(cv, fr, K8a, t, .05, CX, 300, -2, frm=(0, -250), h=0)
    for k, nm in enumerate(NAMES8):                          # chaque pépite sort en sautant, décalée (overlapping)
        tn = w(8, nm.capitalize()[:5]) - .25
        x = 180 + k*240
        if t > tn - .15:
            u = ease_out(prog(t, tn, .45)); dy, sx, sy = hop(t, tn, 220, .45)
            L = KIDS[k].render_layer(fr, .62, age=1, kit="ol", mood="cheer", arms=(150, 150) if t > tn else (30, 30), t=t + k)
            blit_sxy(cv, L, lerp(CX, x, u), 1640 + dy, sx, sy)
            enter(cv, fr, LBL(nm, f"h8n{k}", font("title", 50), BLANC, ROUGE if k % 2 else BLEU, padx=12, pady=2, rough=2), t, tn + .25, x, 1700, (-3, 3, -2, 2)[k], frm=(0, 160))
    show(cv, fr, TAG("tous formés à Lyon", "h8t", GOLD, INK, 60), t, w(8, "formés") - .1, None, CX, 600, 2)
    drift(cv, t, T, .03)

# ------------------------------------------------------------------ SCÈNE 9 — les Lyonnaises : 8 Ligues des champions
def s9(cv, fr, t, T):
    bg_stripes(cv, fr, "hs9", BLEU_D, BLEU, t)
    polaroid(cv, fr, "p2", t, .02, CX, 760, 2, frm=(760, 260))
    enter(cv, fr, K9a, t, w(9, "Lyonnaises") - .2, CX, 300, -3, frm=(0, -250), h=0)
    th = w(9, "huit") - .05
    if t > th - .08:
        n = int(round(8*ease(prog(t, th, .6))))
        enter(cv, fr, LBL(str(n), "h9n", font("title", 220), NOIR, GOLD, padx=30, pady=0, rough=3), t, th, 260, 1330, -5, frm=(-300, 200))
        enter(cv, fr, LBL("LIGUES DES CHAMPIONS", "h9c", font("title", 56), BLANC, NOIR, padx=16, pady=4, rough=3), t, th + .2, 680, 1330, 3, frm=(300, 200))
    stamp(cv, fr, K9b, t, w(9, "Record") - .05, CX, 1530, -4)
    if t > th: confetti(cv, fr, "hc9", t - th, 80, 3, [ROUGE, BLEU, BLANC, GOLD])
    drift(cv, t, T, .03)

# ------------------------------------------------------------------ SCÈNE 10 — juin 2025 : rétrogradé… sauvé
def s10(cv, fr, t, T):
    ts = w(10, "sauvé") - .1; tr = w(10, "rétrograde") - .05
    bg_stripes(cv, fr, "hs10", (40, 40, 46), (54, 54, 60), t)
    polaroid(cv, fr, "p1", t, .02, CX, 760, -3, frm=(-760, 260))
    enter(cv, fr, K10a, t, w(10, "juin") - .1, CX, 300, -3, frm=(0, -250), h=0)
    if t < ts:
        grayscale(cv, .7)
        if t > w(10, "tonnerre") - .1: siren_lights(cv, t, .16)
        stamp(cv, fr, K10b, t, tr, CX, 1250, -6)
        show(cv, fr, TAG("15 jours plus tard, en appel…", "h10t", PAL["paper"], INK, 54), t, w(10, "Quinze") - .1, None, CX, 1400, 2)
    else:
        stamp(cv, fr, K10c, t, ts, CX, 1280, -8, 1.1)
        confetti(cv, fr, "hc10", t - ts, 100, 3, [ROUGE, BLEU, BLANC, GOLD])
    impact(cv, t, tr + .1, 18); impact(cv, t, ts + .1, 20); drift(cv, t, T, .03)

# ------------------------------------------------------------------ SCÈNE 11 — ruine → sommet → gouffre ; ton avis
def s11(cv, fr, t, T):
    bg_stripes(cv, fr, "hs11", BLEU_D, BLEU, t); d = ImageDraw.Draw(cv)
    steps = [("RUINE", (200, 1000), ROUGE, w(11, "ruine")), ("SOMMET", (CX, 640), GOLD, w(11, "sommet")), ("GOUFFRE", (880, 1060), NOIR, w(11, "gouffre"))]
    for k, (txt, (x, y), c, t0) in enumerate(steps):
        if k > 0 and t > t0 - .3:
            u = ease(prog(t, t0 - .3, .3)); p0 = steps[k - 1][1]
            pencil_line(d, [arc(p0, (x, y), v/10*u, -120) for v in range(11)], 1, BLANC, 9, k, 1.0)
        enter(cv, fr, LBL(txt, f"h11s{k}", font("title", 78), BLANC if c != GOLD else NOIR, c, padx=20, pady=4, rough=3), t, t0 - .1, x, y, (-4, 2, 5)[k], frm=(0, 220))
    enter(cv, fr, K11a, t, w(11, "Quel") - .1, CX, 300, -3, frm=(0, -250), h=0)
    tc = w(11, "commentaire") - .15
    if t > tc:
        speech_bubble(cv, fr, "h11b", "Aucun, que l'OL !", 520, 1290, ease_out(prog(t, tc, .3)), (1, 1), 64)
        arrow(d, (760, 1320), (985, 1400), prog(t, tc + .1, .4), GOLD, 14, 3, 44, .25)
    ta = w(11, "abonne-toi")
    sub_button(cv, fr, CX, 1520, t, ta - .1, ta + .25)
    drift(cv, t, T, .03)

# ------------------------------------------------------------------ scènes + bruitages (accents sur les impacts)
def SC(name, n, fn, sfx, trans=None, trans_dur=.25, pad_out=.25):
    return Scene(name, TEXTS[n-1], fn, sfx, pad_in=PADS[n-1], pad_out=pad_out, trans=trans, trans_dur=trans_dur)
SCENES = [
    SC("hook", 1, s1, [(.0, "hook", 1.3), (w(1, "ruiné"), "stamp", .9), (w(1, "Quinze") - .1, "whoosh_up", .7), (w(1, "Quinze") + .25, "boom", .5)]
       + [(w(1, "sept") + .06*k, "pop", .35) for k in range(7)] + [(w(1, "suite"), "stamp", .9), (w(1, "suite"), "crowd", .7)]),
    SC("1950", 2, s2, [(.0, "rip", .5), (.05, "stamp", .5), (w(2, "naissance"), "kick", .4)] + [(w(2, "Coupes") + .12*k + .35, "thud", .5) for k in range(3)]
       + [(w(2, "jamais"), "stamp", .9)], trans="tear_v", trans_dur=.4),
    SC("1987", 3, s3, [(.0, "whoosh", .5), (.4, "thud", .5), (w(3, "deuxième"), "stamp", .8), (w(3, "dettes"), "coin", .5),
                       (w(3, "rachète"), "whoosh_up", .5), (w(3, "rachète") + .5, "thud", .6), (w(3, "Aulas"), "pop2", .6)], trans="whip"),
    SC("ol_europe", 4, s4, [(.0, "paper", .5), (w(4, "remonter"), "scribble", .5), (w(4, "Coupe"), "sparkle", .6), (w(4, "Domenech"), "pop2", .6)], trans="tear_h", trans_dur=.45),
    SC("2002", 5, s5, [(.0, "crowd_long", .7), (w(5, "premier") - .2, "whoosh_up", .5), (w(5, "champion"), "stamp", 1.0), (w(5, "champion"), "crowd_long", 1.0)], trans="punch", trans_dur=.3),
    SC("juninho", 6, s6, [(.0, "whoosh", .5), (.4, "thud", .5), (w(6, "Juninho"), "kick", .7), (w(6, "quarante-quatre"), "coin", .5), (w(6, "machine"), "whoosh", .7)], trans="whip"),
    SC("7_titres", 7, s7, [(.0, "whoosh", .5), (.4, "thud", .5)] + [(w(7, "deux") - .15 + .16*k + .3, "pop", .4) for k in range(7)]
       + [(w(7, "record"), "stamp", .9), (w(7, "record"), "crowd_long", .8)], trans="punch", trans_dur=.3),
    SC("formation", 8, s8, [(.0, "whoosh", .5)] + [(w(8, n.capitalize()[:5]) - .25, "pop2", .5) for n in NAMES8] + [(w(8, "formés"), "sparkle", .5)], trans="tear_d", trans_dur=.45),
    SC("lyonnaises", 9, s9, [(.0, "whoosh", .5), (.4, "thud", .5), (w(9, "huit"), "sparkle", .6), (w(9, "Record"), "stamp", .9), (w(9, "Record"), "crowd_long", .9)], trans="whip"),
    SC("dncg", 10, s10, [(.0, "whoosh", .5), (.4, "thud", .5), (w(10, "tonnerre"), "boom", .7), (w(10, "tonnerre"), "siren", .35, 2.5),
                         (w(10, "rétrograde"), "gavel", .9), (w(10, "sauvé"), "stamp", 1.0), (w(10, "sauvé"), "crowd_long", 1.0)], trans="tear_v", trans_dur=.4),
    SC("fin", 11, s11, [(.0, "whoosh", .5), (w(11, "ruine"), "thud", .5), (w(11, "sommet"), "sparkle", .5), (w(11, "gouffre"), "groan", .4),
                        (w(11, "commentaire"), "notif", .9), (w(11, "abonne-toi"), "pop2", .7), (w(11, "abonne-toi") + .25, "notif", .8)], trans="whip", pad_out=1.4),
]

def cover(path):
    cv = background(0, TITLE); bg_stripes(cv, 0, "hcov", BLEU_D, BLEU, 0)
    LYON.draw(cv, 0, CX, 330, 1.05, -3)
    Label("RUINÉ EN 1987…", "hcv1", font("title", 76), BLANC, NOIR, padx=26, pady=6, rough=4).draw(cv, 0, CX, 560, 1, -2)
    blit(cv, polaroid_sprite("p3"), CX, 900, .95, -3)
    Label("…7 FOIS CHAMPION DE SUITE ?!", "hcv2", font("title", 72), NOIR, GOLD, padx=26, pady=6, rough=4, maxw=1000).draw(cv, 0, CX, 1300, 1, 2)
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
