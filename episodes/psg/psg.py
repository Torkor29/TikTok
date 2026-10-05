"""Épisode « Légendes du foot » #8 : l'histoire du PSG, format court (~1 min 15), CTA « like + abonne-toi pour plus d'épisodes ».
« PSG » + tour Eiffel dès la 1re image, barre chrono : envoyé en 3e division deux ans après sa naissance… double champion d'Europe ;
1970 : plus de 20 000 « oui », la fusion ; 1972 : le divorce avec le Paris FC (l'écusson se déchire), la D3, la remontée au Parc ;
1986 1er titre, 1996 le boulet de N'Gotty ; 2011 le Qatar, Ibra / Neymar 222 M€ / Mbappé / Messi, la machine ; pause like + abonne-toi ;
la C1 qui coince (remontada, finale 2020, départ de Mbappé) ; sans lui : 5-0 contre l'Inter (2025) puis Arsenal aux tirs au but (2026) ;
fin : deux coupes, 54 ans après la D3, « une troisième ? », like + abonne-toi.

  python3 episodes/psg/psg.py output/psg --stills [3,4]
  python3 episodes/psg/psg.py output/psg --cover
  python3 episodes/psg/psg.py output/psg
Avant les vraies voix : LEGENDES_PROVISOIRE=<dossier> (voir scripts/minutage_provisoire.py).
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from story import *
import engine

TITLE = "~/légendes $ ./psg"
SLUG = "psg_legende"
SRC = os.environ.get("LEGENDES_PROVISOIRE") or HERE
VOICE = [os.path.join(SRC, "voix", f"scene_{i}.mp3") for i in range(1, 10)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
ALIGN = os.path.join(SRC, "alignement.json")
PAD = 0.12
WS, TEXTS = load_words(ALIGN)
def w(i, word, n=1, end=False):
    """Temps local (dans la scène i) où la voix prononce `word`."""
    return PAD + WS[i-1](word, n, end)

NAVY = (16, 40, 86); NAVY_D = (10, 24, 54); ROUGE = (210, 36, 42); BLANC = (250, 250, 246); GOLD = (236, 186, 48)
GRIS = (120, 120, 126); MAROON = (138, 21, 56); NOIR = (30, 28, 28)

PSGP = Player("psgp8", hair=(70, 50, 36), skin=(230, 186, 150))
PSGP2 = Player("psgp8b", hair=(24, 20, 18), skin=(140, 96, 70))
IBRA = Player("ibra", hair=(40, 30, 24), beard_col=(46, 34, 28), skin=(226, 184, 150), hair_style="mullet")
NEY = Player("ney8", hair=(48, 34, 26), skin=(196, 146, 108), hair_style="quiff")
MBAP = Player("mbap8", hair=(24, 20, 18), skin=(126, 86, 62), hair_style="bald")
MESSI = Player("messi8", hair=(110, 72, 44), beard_col=(100, 66, 40), skin=(230, 186, 150))
NGOT = Player("ngotty", hair=(24, 20, 18), skin=(104, 70, 50))

# ------------------------------------------------------------------ objets
def _eiffel(d, a):
    ax, ay = a; c = (60, 64, 90)
    d.polygon([(ax-150, ay+300), (ax-40, ay-40), (ax-18, ay-300), (ax+18, ay-300), (ax+40, ay-40), (ax+150, ay+300), (ax+90, ay+300),
               (ax+10, ay+60), (ax-10, ay+60), (ax-90, ay+300)], fill=c)
    d.rectangle([ax-70, ay+40, ax+70, ay+60], fill=c); d.rectangle([ax-44, ay-60, ax+44, ay-44], fill=c)
EIFFEL = Paper(rect_pts(20, 20), (34, 50, 96), "pseiffel", rough=1, pad=320, shadow=False).add(_eiffel)

PSG_T = Label("PSG", "pstitle", font("title", 260), BLANC, ROUGE, padx=60, pady=4, rough=4)

SHIELD_PTS = [(-110, -130), (110, -130), (110, 10), (60, 100), (0, 140), (-60, 100), (-110, 10)]
def _shield(key, col, col2, txt, size=52, band=False):
    def dec(d, a):
        ax, ay = a
        if band: d.rectangle([ax-30, ay-130, ax+30, ay+140], fill=BLANC); d.rectangle([ax-20, ay-130, ax+20, ay+140], fill=ROUGE)
        else: d.polygon([(ax-110, ay-130), (ax, ay-130), (ax, ay+140), (ax-60, ay+100), (ax-110, ay+10)], fill=col2)
        d.text((ax, ay-10), txt, font=font("title", size), fill=BLANC, anchor="mm", stroke_width=5, stroke_fill=NOIR)
    return Paper(poly_pts(SHIELD_PTS), col, key, rough=1.6, hatch=True).add(dec)
SH_PFC = _shield("pspfc", (30, 60, 140), (60, 120, 200), "PARIS\nFC", 48)
SH_SG = _shield("pssg", (40, 120, 70), BLANC, "ST-\nGERMAIN", 40)
SH_PSG = _shield("pspsg", NAVY, NAVY, "PSG", 70, band=True)
_torn = {}
def torn_shield():
    if "ab" not in _torn:
        spr = SH_PSG.v[0]; A, B, _ = tear_split(spr, "v", 7, rough=16)
        for P in (A, B): P.info["anchor"] = spr.info["anchor"]
        _torn["ab"] = (A, B)
    return _torn["ab"]

OUI = Paper(rect_pts(150, 90), BLANC, "psoui", rough=1.4).add(
    lambda d, a: d.text((a[0], a[1]), "OUI", font=font("title", 54), fill=NAVY, anchor="mm"))
def oui_rain(cv, fr, t, t0, n=26, key="psoui"):
    if t < t0: return
    rnd = random.Random(key)
    for i in range(n):
        tt = t - t0 - rnd.uniform(0, 1.0)
        if tt < 0: continue
        x = rnd.uniform(80, 1000) + 40*math.sin(tt*2 + i); y = rnd.uniform(-150, 700) + tt*rnd.uniform(500, 800)
        if y < 1950: OUI.draw(cv, fr, x, y, rnd.uniform(.8, 1.2), 30*math.sin(tt*3 + i))

def _parc(d, a):
    ax, ay = a
    for k in range(-8, 9):   # les « peignes » de béton du Parc des Princes
        x = ax + k*50; d.line([(x, ay-150 + abs(k)*6), (x - 10, ay+120)], fill=(150, 154, 166), width=10)
    d.rectangle([ax-200, ay+80, ax+200, ay+140], fill=(60, 64, 80))
    d.text((ax, ay+110), "PARC DES PRINCES", font=font("title", 40), fill=BLANC, anchor="mm")
PARC = Paper(ellipse_pts(900, 380, 60), (214, 218, 226), "psparc", rough=1.6, hatch=True).add(_parc)

def qatar_flag(cv, x, y, w=320, h=200, t=0.0, a=1.0, rot=0.0):
    """Drapeau bordeaux à bande blanche dentelée (9 pointes), qui ondule."""
    if a <= .01: return
    L = layer(int(w+40), int(h+60), (w/2+20, h/2+30)); d = ImageDraw.Draw(L); n = 26
    for k in range(n):
        off = 10*math.sin(k/n*math.pi*2 - t*5)*(k/n)
        x0 = 20 + k*w/n; d.rectangle([x0, 30+off, x0 + w/n + 1, 30+h+off], fill=BLANC if k < n*.3 else MAROON)
    xb = 20 + w*.3
    pts = [(xb - 2, 30)]
    for k in range(9):
        pts += [(xb + w*.08, 30 + (k + .5)*h/9), (xb - 2, 30 + (k + 1)*h/9)]
    d.polygon(pts + [(xb + w*.1, 30 + h), (xb + w*.1, 30)], fill=MAROON)
    blit(cv, L, x, y, a, rot, 1)

def gear(cv, x, y, r, rot, col=(150, 156, 170)):
    d = ImageDraw.Draw(cv); pts = []
    for k in range(24):
        an = rot + k*math.pi/12; rr = r if k % 2 == 0 else r*.8
        pts += [(x + rr*math.cos(an - .1), y + rr*math.sin(an - .1)), (x + rr*math.cos(an + .1), y + rr*math.sin(an + .1))]
    d.polygon(pts, fill=col); d.ellipse([x - r*.35, y - r*.35, x + r*.35, y + r*.35], fill=NAVY_D)

def chains(cv, x, y, s=1.0):
    """Chaînes + cadenas sur la coupe (« ça coince »)."""
    d = ImageDraw.Draw(cv)
    for sg in (-1, 1):
        for k in range(9):
            cx = x - 220*s + k*55*s; cy = y + sg*40*s + (k - 4)*sg*14*s
            d.ellipse([cx - 26*s, cy - 14*s, cx + 26*s, cy + 14*s], outline=(170, 174, 186), width=max(3, int(9*s)))
    d.rounded_rectangle([x - 50*s, y - 10*s, x + 50*s, y + 80*s], int(10*s), fill=(200, 160, 50), outline=NOIR, width=4)
    d.arc([x - 34*s, y - 60*s, x + 34*s, y + 10*s], 180, 360, fill=(170, 174, 186), width=max(4, int(12*s)))
    d.ellipse([x - 9*s, y + 22*s, x + 9*s, y + 40*s], fill=NOIR)

def suitcase(cv, x, y, s=1.0):
    d = ImageDraw.Draw(cv)
    d.rounded_rectangle([x-70*s, y, x+70*s, y+110*s], int(12*s), fill=(150, 96, 56), outline=(90, 56, 30), width=max(2, int(5*s)))
    d.rectangle([x-70*s, y+46*s, x+70*s, y+58*s], fill=(110, 70, 40)); d.arc([x-26*s, y-30*s, x+26*s, y+10*s], 180, 360, fill=(90, 56, 30), width=max(3, int(8*s)))

HEART = Paper(heart_pts(7), BLANC, "psheart", rough=1.2, shadow=False)
def like_button(cv, fr, x, y, s, t, t_tap):
    """Gros bouton « j'aime » rond : il s'enfonce au tap, des petits cœurs s'envolent, le compteur grimpe."""
    if s <= .02: return
    press = 1 - .15*math.sin(prog(t, t_tap, .25)*math.pi)
    d = ImageDraw.Draw(cv); r = 150*s*press
    d.ellipse([x - r, y - r, x + r, y + r], fill=(240, 50, 80), outline=BLANC, width=max(3, int(10*s)))
    HEART.draw(cv, fr, x, y + 6*s, s*press, 0)
    if t > t_tap:
        for k in range(7):
            u = prog(t, t_tap + k*.06, .9)
            if 0 < u < 1: HEART.draw(cv, fr, x + 140*math.sin(k*2.1)*u, y - 380*u, .28*(1 - u*.5), 0, 1 - u)
        v = counter(12840, 12841 + int(800*prog(t, t_tap, 1.6)), 1)
        LBL(v, "pslikes", font("title", 64), BLANC, NOIR, padx=16, pady=2, rough=2).draw(cv, fr, x, y + 220*s, 1, 0)
    if t_tap - .05 < t < t_tap + .35:   # le doigt qui tape
        a = 1 - prog(t, t_tap, .35); d.ellipse([x + 60 - 40, y + 60 - 40, x + 60 + 40, y + 60 + 40], outline=BLANC, width=6)

SCOREBOARD = scoreboard_sprite(820, 330, "psscore")
def score2(cv, fr, x, y, la, lb, a, b, sub="", s=1.0):
    if s <= .02: return
    L = layer(900, 420, (450, 210)); SCOREBOARD.draw(L, fr, 450, 210, 1, 0, 1)
    d = ImageDraw.Draw(L)
    for x_, lab in ((180, la), (720, lb)): d.text((x_, 130), lab, font=font("mono", 64 if len(lab) <= 5 else 48), fill=(200, 196, 190), anchor="mm")
    d.text((450, 220), f"{a} - {b}", font=font("title", 150), fill=(255, 204, 70), anchor="mm")
    if sub: d.text((450, 330), sub, font=font("mono", 38), fill=(170, 166, 160), anchor="mm")
    blit(cv, L, x, y, s)

def stripes(d, col, n=12):
    sx0, sy0, sx1, sy1 = STAGE; wd = (sx1 - sx0)/n
    for k in range(0, n, 2): d.rectangle([sx0 + k*wd, sy0, sx0 + (k+1)*wd, sy1], fill=col)

def band_bg(cv, fr, key):
    """Fond « maillot » : bleu nuit avec la bande rouge et blanche au centre."""
    stage_fill(cv, fr, NAVY, key); d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    d.rectangle([CX - 150, sy0, CX + 150, sy1], fill=BLANC); d.rectangle([CX - 110, sy0, CX + 110, sy1], fill=ROUGE)

def walk(t, speed=9, amp=22):
    ph = math.sin(t*speed); return (amp*ph, -amp*ph), abs(math.sin(t*speed))*8

def stadium(cv, fr, key, t=0.0, sky=(18, 22, 46), grass=(46, 112, 64), horizon=1060, pal=None):
    stage_fill(cv, fr, sky, key); d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    rnd = random.Random(key)
    pal = pal or [NAVY, ROUGE, BLANC, (60, 80, 140), (200, 196, 190), (120, 30, 40)]
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

def spin(cv, fr, pl, x, y, s, t, t0, kit_a, kit_b, dur=.4, **kw):
    su = prog(t, t0, dur)
    if 0 < su < 1:
        L = pl.render_layer(fr, s, age=kw.get("age", 1), kit=kit_a if su < .25 else kit_b, mood=kw.get("mood", "happy"))
        blit_sxy(cv, L, x, y, max(.04, abs(math.cos(su*math.pi*2))), 1)
    else:
        pl.draw(cv, fr, x, y, s, kit=kit_b if su >= 1 else kit_a, t=t, **kw)

def trophy_lift(cv, fr, pl, x, y, s, kit, t, trophy=UCL, mood="cheer"):
    pl.draw(cv, fr, x, y, s, age=1, kit=kit, mood=mood, arms=(160, 160), legs=(12, 12), t=t)
    trophy.draw(cv, fr, x, y - 850*s + 8*math.sin(t*6), .9*s, 3*math.sin(t*4))

def shaft(cv, fr, t, speed=0.0, key="psshaft"):
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
    an = u*math.pi*2; d.line([(x, y), (x+80*s*math.sin(an), y-80*s*math.cos(an))], fill=ROUGE, width=max(3, int(8*s)))
    d.ellipse([x-10*s, y-10*s, x+10*s, y+10*s], fill=PAL["ink"])

_sil = {}
def ucl_silhouette():
    if "s" not in _sil:
        L = layer(300, 420, (150, 210)); UCL.draw(L, 0, 150, 210, 1.2, 0)
        a = L.getchannel("A").point(lambda v: 255 if v > 60 else 0)
        S = Image.new("RGBA", L.size, (24, 22, 30, 0)); S.putalpha(a); S.info["anchor"] = (150, 210); _sil["s"] = S
    return _sil["s"]

# ------------------------------------------------------------------ labels
K1a = KW("3e DIVISION", "psk1a", ROUGE, size=120); T1a = TAG("2 ans après sa naissance", "pst1a", PAL["paper"], size=54)
K1b = KW("DOUBLE CHAMPION D'EUROPE", "psk1b", GOLD, PAL["ink"], 74)
K1c = STAMP("L'HISTOIRE DU PSG", "psk1c", NAVY, 100); K1d = KW("EN 1 MINUTE", "psk1d", ROUGE, size=110)
K2a = KW("1970", "psk2a", PAL["ink"], size=170); T2a = TAG("aucun club parisien en 1re division", "pst2a", PAL["paper"], size=48)
K2b = KW("+ DE 20 000 « OUI » !", "psk2b", NAVY, size=92); K2c = STAMP("PARIS SAINT-GERMAIN", "psk2c", ROUGE, 84)
T2b = TAG("une fusion", "pst2b", PAL["paper"], size=54)
K3a = KW("1972 : LE DIVORCE", "psk3a", PAL["ink"], size=100); K3b = KW("3e DIVISION !", "psk3b", ROUGE, size=120)
K3c = KW("1974", "psk3c", PAL["ink"], size=150); T3a = TAG("déjà de retour en D1", "pst3a", PAL["paper"], size=54)
K4a = KW("1986", "psk4a", PAL["ink"], size=170); K4b = STAMP("1er TITRE DE CHAMPION", "psk4b", NAVY, 86)
K4c = KW("1996", "psk4c", PAL["ink"], size=150); K4d = STAMP("1re COUPE D'EUROPE", "psk4d", ROUGE, 92)
T4a = TAG("le boulet de Bruno N'Gotty", "pst4a", PAL["paper"], size=52); T4b = TAG("Coupe des coupes", "pst4b", GOLD, size=54)
K5a = KW("2011", "psk5a", PAL["ink"], size=170); K5b = STAMP("LE QATAR RACHÈTE", "psk5b", MAROON, 100)
NAMES5 = [Label(n, "psn5"+n, font("title", 50), BLANC, NAVY, padx=16, pady=4, rough=2) for n in ("IBRA", "NEYMAR", "MBAPPÉ", "MESSI")]
K5c = KW("222 000 000 €", "psk5c", GOLD, PAL["ink"], 96); K5d = KW("UNE MACHINE", "psk5d", ROUGE, size=130)
K6a = KW("PETITE PAUSE !", "psk6a", PAL["ink"], size=84); T6a = TAG("si tu kiffes…", "pst6a", PAL["paper"], size=56)
K6b = KW("LÂCHE UN LIKE", "psk6b", PAL["ink"], size=76); T6b = TAG("pour plus d'épisodes !", "pst6b", PAL["paper"], size=56)
K6c = KW("ON REPREND !", "psk6c", PAL["ink"], size=84)
BTN_SUB = Label("+ ABONNE-TOI", "psbsub", font("title", 96), (255, 255, 255), (230, 40, 80), padx=40, pady=14, rough=2.5)
K7a = KW("LIGUE DES CHAMPIONS…", "psk7a", PAL["ink"], size=84); T7a = TAG("ça coince", "pst7a", PAL["paper"], size=60)
K7b = STAMP("REMONTADA", "psk7b", ROUGE, 130); T7b = TAG("2017", "pst7b", PAL["paper"], size=60)
K7c = KW("FINALE 2020", "psk7c", PAL["ink"], size=110); T7c = TAG("perdue contre le Bayern", "pst7c", PAL["paper"], size=52)
K7d = KW("MBAPPÉ S'EN VA", "psk7d", PAL["ink"], size=100); T7d = TAG("2024, direction Madrid", "pst7d", PAL["paper"], size=52)
K8a = KW("SANS LUI…", "psk8a", PAL["ink"], size=130); K8b = KW("5 - 0 !", "psk8b", ROUGE, size=220)
T8a = TAG("finale 2025 contre l'Inter", "pst8a", PAL["paper"], size=52); T8b = TAG("le plus gros écart de l'histoire en finale", "pst8b", GOLD, size=44)
K8c = KW("2026", "psk8c", PAL["ink"], size=150); K8d = STAMP("ENCORE !", "psk8d", ROUGE, 140); T8c = TAG("contre Arsenal, aux tirs au but", "pst8c", PAL["paper"], size=50)
K9a = KW("DOUBLE CHAMPION D'EUROPE", "psk9a", GOLD, PAL["ink"], 74); T9a = TAG("54 ans après la 3e division !", "pst9a", PAL["paper"], size=54)
K9b = KW("UNE 3e ?", "psk9b", ROUGE, size=120); K9c = KW("+ D'ÉPISODES", "psk9c", PAL["ink"], size=84)
X2 = Label("×2", "psx2", font("title", 200), GOLD, None, stroke=8, stroke_fill=PAL["ink"])
QM = Label("?", "psqm", font("title", 200), GOLD, None, stroke=8, stroke_fill=PAL["ink"])

# ------------------------------------------------------------------ SCÈNE 1 — envoyé en D3… double champion d'Europe
def s1a(cv, fr, t):
    stage_fill(cv, fr, NAVY, "pss1a")
    rays(cv, (CX, 1100), t, .6, 14, 1500, (40, 70, 130), .12, .15)
    te = w(1, "envoyé") - .05; td = w(1, "division")
    EIFFEL.draw(cv, fr, 850, 1160, 1)
    PSGP.draw(cv, fr, 400, 1760, 1.05, age=1, kit="psg", mood="surprised" if t > te else "happy", t=t)
    floor_panel(cv, fr, 400, 780, "D1", t, True, 1.3, 1)
    PSG_T.draw(cv, fr, CX, 400, lerp(1.35, 1.0, ease_out_cubic(prog(t, 0, .25))), -3)
    elevator_drop(cv, t, te, td - te)
    if t > td:
        shaft(cv, fr, t)
        PSGP.draw(cv, fr, CX, 1740, 1.05, age=1, kit="psg", mood="sad", t=t, look=(0, 1))
        floor_panel(cv, fr, CX, 640, "D3", t, True, 1.8, 1)
        kw(cv, fr, K1a, t, td, None, CX, 920, 3)
        show(cv, fr, T1a, t, w(1, "deux") - .05, None, CX, 1080, -2)

def s1b(cv, fr, t):
    stage_fill(cv, fr, NAVY_D, "pss1b")
    rays(cv, (CX, 1050), t, 1.0, 16, 1500, (230, 190, 80))
    t0 = w(1, "Aujourd'hui") - .1
    for k, x in enumerate((330, 750)):
        UCL.draw(cv, fr, x, 1080 + 10*math.sin(t*5 + k), 1.5*slam(t, t0 + .1 + k*.25, .22), (-6, 6)[k])
    X2.draw(cv, fr, CX, 1460, pop_in(t, w(1, "double") - .05), -6)
    kw(cv, fr, K1b, t, w(1, "double") - .05, None, CX, 440, -3)
    confetti(cv, fr, "psc1", t - w(1, "champion"), 80, 3, [GOLD, BLANC, ROUGE])
    camera_flashes(cv, fr, "pscf1", t - t0, 1.4, 10)

def s1c(cv, fr, t):
    band_bg(cv, fr, "pss1c")
    t0 = w(1, "L'histoire") - .1
    for P, x, k in ((PSGP2, 220, 0), (PSGP, 860, 1)):
        P.draw(cv, fr, x, 1780 - 60*abs(math.sin(t*6 + k)), .82, age=1, kit="psg", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
    show_stamp(cv, fr, K1c, t, t0 + .05, CX, 420, -4)
    kw(cv, fr, K1d, t, w(1, "minute") - .1, None, CX, 600, 3)
    stopwatch(cv, CX, 900, 1.1, prog(t, t0, 1.2))

def s1(cv, fr, t, T):
    shots(cv, fr, t, [(0, s1a), (w(1, "Aujourd'hui") - .1, s1b), (w(1, "L'histoire") - .1, s1c)], d=.24)
    impact(cv, t, .02, 18); impact(cv, t, w(1, "division") + .02, 24); flashes(cv, t, w(1, "division"), .1, .5)
    impact(cv, t, w(1, "double"), 18); punch(cv, t, w(1, "L'histoire") - .1, 1.1); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 2 — 1970 : plus de 20 000 « oui », la fusion
def s2a(cv, fr, t):
    stage_fill(cv, fr, (176, 206, 232), "pss2a"); d = ImageDraw.Draw(cv)
    EIFFEL.draw(cv, fr, CX, 1230, 1.5)
    d.rectangle([STAGE[0], 1560, STAGE[2], STAGE[3]], fill=(120, 130, 150))
    kw(cv, fr, K2a, t, w(2, "Mille") - .05, None, CX, 420, -3)
    show(cv, fr, T2a, t, w(2, "Paris") - .05, None, CX, 600, 2)
    if t > w(2, "première"): QM.draw(cv, fr, 820, 900 + 10*math.sin(t*5), pop_in(t, w(2, "première")), 8)

def s2b(cv, fr, t):
    stage_fill(cv, fr, NAVY, "pss2b")
    t0 = w(2, "Plus", 2) - .1
    oui_rain(cv, fr, t, t0, 30)
    v = counter(0, 20000, ease_out_cubic(prog(t, t0, 1.0)))
    LBL(v, "ps20k", font("title", 200), GOLD, PAL["ink"], padx=30, pady=0, rough=3).draw(cv, fr, CX, 1000, pop_in(t, t0), -3)
    kw(cv, fr, K2b, t, w(2, "oui") - .05, None, CX, 440, -3)

def s2c(cv, fr, t):
    stage_fill(cv, fr, (236, 228, 210), "pss2c")
    tf = w(2, "fusion") - .3; u = ease_io(prog(t, tf, .35))
    if u < 1:
        SH_PFC.draw(cv, fr, lerp(280, CX - 40, u), 1050, 1.25*pop_in(t, w(2, "et"), .3), lerp(-8, 8, u))
        SH_SG.draw(cv, fr, lerp(800, CX + 40, u), 1050, 1.25*pop_in(t, w(2, "et") + .15, .3), lerp(8, -8, u))
    else:
        rays(cv, (CX, 1050), t, prog(t, tf + .35, .3), 14, 900, (230, 200, 120))
        SH_PSG.draw(cv, fr, CX, 1050, 1.6*slam(t, tf + .35, .2), -3)
        particles(cv, fr, "psp2", (CX, 1050), prog(t, tf + .35, .6), 18, 300, [NAVY, ROUGE, BLANC], 16)
    show_stamp(cv, fr, K2c, t, w(2, "Paris", 2) - .05, CX, 440, -4)
    show(cv, fr, T2b, t, tf + .3, None, CX, 620, 2)

def s2(cv, fr, t, T):
    shots(cv, fr, t, [(0, s2a), (w(2, "Plus", 2) - .1, s2b), (w(2, "et") - .1, s2c)], d=.24)
    impact(cv, t, w(2, "Mille"), 12); impact(cv, t, w(2, "oui"), 16); impact(cv, t, w(2, "fusion") + .05, 18)
    flashes(cv, t, w(2, "fusion") + .05, .1, .5); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 3 — 1972 : le divorce, la D3… et 1974 au Parc
def s3a(cv, fr, t):
    stage_fill(cv, fr, (236, 228, 210), "pss3a")
    tdv, tp = w(3, "divorce"), w(3, "Paris")
    if t < tdv:
        SH_PSG.draw(cv, fr, CX, 1050, 1.6, -3)
    else:
        A, B = torn_shield(); u = ease_out_cubic(prog(t, tdv, .5))
        blit(cv, A, CX - 260*u, 1050 - 120*u*prog(t, tp, .4), 1.6, -3 - 18*u)
        blit(cv, B, CX + 260*u, 1050 + 380*u*prog(t, tp, .6), 1.6, -3 + 25*u)
        floor_panel(cv, fr, 270, 640, "D1", t, False, 1.0, pop_in(t, tp))
        LBL("PARIS FC", "pspfcl", font("title", 60), BLANC, (30, 60, 140), padx=18, pady=4, rough=2).draw(cv, fr, 270, 800, pop_in(t, tp), -4)
    kw(cv, fr, K3a, t, .03, None, CX, 400, -3)

def s3b(cv, fr, t):
    te = w(3, "repart") - .1; td = w(3, "division", 2)
    stage_fill(cv, fr, (120, 30, 40), "pss3b")
    PSGP.draw(cv, fr, CX, 1740, 1.05, age=1, kit="psg", mood="surprised", t=t)
    floor_panel(cv, fr, CX, 660, "D1", t, True, 1.6, 1)
    elevator_drop(cv, t, te, td - te)
    if t > td:
        shaft(cv, fr, t, 0, "pss3shaft")
        PSGP.draw(cv, fr, CX, 1740, 1.05, age=1, kit="psg", mood="sad", t=t, look=(0, 1))
        floor_panel(cv, fr, CX, 660, "D3", t, True, 1.8, 1)
        kw(cv, fr, K3b, t, td, None, CX, 960, 3)

def s3c(cv, fr, t):
    t0 = w(3, "Mais") - .1; tq = w(3, "soixante-quatorze")
    if t < tq + .3:
        shaft(cv, fr, t, 900 + 2200*prog(t, t0, tq + .3 - t0))
        lab = ("D3", "D2", "D1")[min(2, int(prog(t, t0 + .1, tq - t0)*2.99))]
        floor_panel(cv, fr, CX, 640, lab, t, False, 1.8, 1)
        PSGP.draw(cv, fr, CX, 1740, 1.05, age=1, kit="psg", mood="surprised", arms=(40, 40), t=t)
    else:
        stage_fill(cv, fr, (24, 30, 60), "pss3c"); rays(cv, (CX, 1000), t, .8, 16, 1500, (50, 70, 130))
        PARC.draw(cv, fr, CX, 1000, 1.05*slam(t, w(3, "Parc") - .1, .22), 0)
        PSGP.draw(cv, fr, CX, 1780, .85, age=1, kit="psg", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
        show(cv, fr, T3a, t, w(3, "remonté") - .05, None, CX, 640, 2)
    kw(cv, fr, K3c, t, tq - .05, None, CX, 420, -3)

def s3(cv, fr, t, T):
    shots(cv, fr, t, [(0, s3a), (w(3, "et") - .1, s3b), (w(3, "Mais") - .1, s3c)], d=.24)
    impact(cv, t, w(3, "divorce"), 20); impact(cv, t, w(3, "division", 2) + .02, 24); impact(cv, t, w(3, "Parc"), 14); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 4 — 1986 1er titre, 1996 le boulet de N'Gotty
def s4a(cv, fr, t):
    band_bg(cv, fr, "pss4a")
    trophy_lift(cv, fr, PSGP, CX, 1780, .85, "psg", t, CUP)
    kw(cv, fr, K4a, t, w(4, "quatre-vingt-six") - .1, None, CX, 400, -3)
    show_stamp(cv, fr, K4b, t, w(4, "titre") - .05, CX, 600, 4)
    confetti(cv, fr, "psc4", t - w(4, "titre"), 70, 3, [BLANC, ROUGE, GOLD])

def s4b(cv, fr, t):
    stadium(cv, fr, "pss4stad", t, horizon=1060)
    tb = w(4, "boulet"); tg = tb + .45
    draw_goal(cv, fr, 760, 1290, 400, 240, prog(t, tg, .5), 1, t)
    NGOT.draw(cv, fr, 260, 1760, 1.0, age=1, kit="psg", mood="cheer" if t > tg else "determined", t=t,
              legs=(0, 60*math.sin(prog(t, tb - .1, .3)*math.pi)), arms=(150, 150) if t > tg + .1 else (20, 20))
    if tb - .05 < t < tg + .05:
        u = prog(t, tb, .45); p = lerp_pt((330, 1730), (780, 1190), u); draw_ball(cv, fr, p[0], p[1], .55, t*900)
        speed_lines(cv, fr, (p[0], p[1]), .35, n=18, seed=4, inner=120)
    kw(cv, fr, K4c, t, w(4, "quatre-vingt-seize") - .1, None, CX, 400, -3)
    show(cv, fr, T4a, t, tb - .05, None, CX, 580, 2)
    if t > tg:
        show_stamp(cv, fr, K4d, t, w(4, "coupe") - .05, CX, 760, -4)
        show(cv, fr, T4b, t, w(4, "coupe") + .3, None, CX, 920, 3)
        confetti(cv, fr, "psc4b", t - tg, 80, 3, [NAVY, ROUGE, BLANC])

def s4(cv, fr, t, T):
    shots(cv, fr, t, [(0, s4a), (w(4, "Et") - .1, s4b)], d=.24)
    impact(cv, t, w(4, "titre"), 16); impact(cv, t, w(4, "boulet") + .45, 22); flashes(cv, t, w(4, "boulet") + .45, .12, .6); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 5 — 2011 le Qatar, les stars, la machine
def s5a(cv, fr, t):
    stage_fill(cv, fr, (236, 228, 210), "pss5a")
    qatar_flag(cv, CX, 1050, 520, 330, t, pop_in(t, w(5, "Qatar") - .1, .3), -4)
    kw(cv, fr, K5a, t, w(5, "onze") - .15, None, CX, 400, -3)
    show_stamp(cv, fr, K5b, t, w(5, "rachète") - .05, CX, 620, 4)
    if t > w(5, "rachète"):
        for i in range(10):
            tt = t - w(5, "rachète") - i*.06
            if tt > 0: LBL("€", "pseur", font("title", 90), GOLD, None, stroke=4, stroke_fill=PAL["ink"]).draw(cv, fr, 120 + (i*97) % 860, 1300 + tt*700 - 400, 1, (i*37) % 40 - 20)

def s5b(cv, fr, t):
    stage_fill(cv, fr, NAVY, "pss5b"); d = ImageDraw.Draw(cv)
    stripes(d, (22, 50, 104), 8)
    for i, (P, word, x, extra) in enumerate(((IBRA, "Ibrahimović", 160, dict(beard=True)), (NEY, "Neymar", 400, {}),
                                            (MBAP, "Mbappé", 650, {}), (MESSI, "Messi", 900, dict(beard=True)))):
        ti = w(5, word) - .1
        if t < ti: continue
        a = pop_in(t, ti, .3)
        P.draw(cv, fr, x, 1720, (.78 if i == 0 else .66)*a, age=1, kit="psg", mood="cheer", arms=(150, 150), t=t, **extra)
        NAMES5[i].draw(cv, fr, x, (1000, 1110, 1000, 1110)[i], a, (-5, 4, -3, 5)[i])
    kw(cv, fr, K5c, t, w(5, "deux", 2) - .05, w(5, "Mbappé") - .1, CX, 440, -3)
    bill = w(5, "deux", 2)
    if bill < t < w(5, "Mbappé"): camera_flashes(cv, fr, "pscf5", t - bill, 1.0, 8)

def s5c(cv, fr, t):
    stage_fill(cv, fr, NAVY_D, "pss5c")
    for x, y, r, sp in ((300, 1050, 230, 1), (640, 900, 170, -1.4), (760, 1280, 200, 1.2), (220, 1450, 140, -1.6)):
        gear(cv, x, y, r, t*sp*2)
    for k in range(6):
        CUP.draw(cv, fr, 160 + k*150, 1700 - 20*abs(math.sin(t*6 + k)), .55*pop_in(t, w(5, "machine") - .1 + k*.07), 0)
    kw(cv, fr, K5d, t, w(5, "machine") - .1, None, CX, 440, -3)

def s5(cv, fr, t, T):
    shots(cv, fr, t, [(0, s5a), (w(5, "Ibrahimović") - .15, s5b), (w(5, "Paris") - .1, s5c)], d=.24)
    impact(cv, t, w(5, "rachète"), 16)
    for word in ("Ibrahimović", "Neymar", "Mbappé", "Messi"): impact(cv, t, w(5, word), 10)
    impact(cv, t, w(5, "machine"), 16); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 6 — PAUSE : like + abonne-toi pour plus d'épisodes
def s6(cv, fr, t, T):
    stage_fill(cv, fr, (240, 50, 80), "pss6"); d = ImageDraw.Draw(cv)
    rays(cv, (CX, 1050), t, .5, 14, 1400, (250, 110, 130))
    kw(cv, fr, K6a, t, .05, None, 760, 300, 4)
    tk, tl, ta = w(6, "kiffes"), w(6, "like"), w(6, "abonne-toi")
    show(cv, fr, T6a, t, tk - .15, None, 760, 470, -3)
    like_button(cv, fr, CX, 1010, .9*pop_in(t, tk, .3), t, tl)
    kw(cv, fr, K6b, t, tl - .05, None, 750, 650, 3)
    if t > ta - .1:
        press = 1 - .12*math.sin(prog(t, ta + .25, .25)*math.pi)
        BTN_SUB.draw(cv, fr, CX, 1370, pop_in(t, ta - .1)*press, -2)
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

# ------------------------------------------------------------------ SCÈNE 7 — la C1 qui coince : remontada, finale 2020, Mbappé s'en va
def s7a(cv, fr, t):
    stage_fill(cv, fr, (40, 44, 60), "pss7a")
    UCL.draw(cv, fr, CX, 1050, 1.7*pop_in(t, .05, .3), 0)
    tc = w(7, "coince")
    if t > tc - .1: chains(cv, CX, 1050, 1.3*pop_in(t, tc - .1, .25))
    kw(cv, fr, K7a, t, w(7, "Ligue") - .1, None, CX, 420, -3)
    show(cv, fr, T7a, t, tc - .05, None, CX, 600, 3)

def s7b(cv, fr, t):
    stadium(cv, fr, "pss7stad", t, horizon=1060, pal=[(0, 77, 152), (165, 0, 68), (230, 200, 60), (200, 196, 190)])
    score2(cv, fr, CX, 760, "BARÇA", "PSG", 6, 1, "8e retour", .7)
    PSGP.draw(cv, fr, CX, 1780, .95, age=1, kit="psg", mood="sad", t=t, look=(0, 1))
    show_stamp(cv, fr, K7b, t, w(7, "remontada") - .05, CX, 420, -5)
    show(cv, fr, T7b, t, w(7, "dix-sept") - .05, None, 820, 560, 4)
    glitch(cv, fr, t, w(7, "remontada"), .35, 16)

def s7c(cv, fr, t):
    stadium(cv, fr, "pss7c", t, horizon=1060, pal=[(200, 20, 40), BLANC, (230, 200, 60), (120, 120, 130)])
    score2(cv, fr, CX, 760, "PSG", "BAYERN", 0, 1, "finale", .7)
    PSGP2.draw(cv, fr, CX, 1780, .95, age=1, kit="psg", mood="sad", t=t, tears=t)
    kw(cv, fr, K7c, t, w(7, "finale") - .05, None, CX, 420, -3)
    show(cv, fr, T7c, t, w(7, "perdue") - .05, None, CX, 1000, 2)
    grayscale(cv, .6)

def s7d(cv, fr, t):
    stage_fill(cv, fr, (236, 228, 210), "pss7d"); d = ImageDraw.Draw(cv)
    t0 = w(7, "Mbappé") - .1
    x = lerp(CX, 1180, ease_in_cubic(prog(t, t0 + .3, 1.4))); lg, bob = walk(t, 11, 22)
    LBL("MADRID", "psmad", font("title", 70), BLANC, (90, 90, 96), padx=24, pady=6, rough=2).draw(cv, fr, 820, 1100, 1, 0)
    arrow(d, (700, 1220), (980, 1220), 1, PAL["ink"], 12, 6, 44, 0)
    MBAP.draw(cv, fr, x, 1760 - bob, 1.0, age=1, kit="psg", mood="normal", legs=lg, arms=(14, 20), t=t, look=(1, 0))
    hx = x + 84*.93 + 199*math.sin(math.radians(20)); hy = 1760 - bob - 498 + 199*math.cos(math.radians(20))
    suitcase(cv, hx + 10, hy - 10, 1.0)
    kw(cv, fr, K7d, t, t0 + .05, None, CX, 420, -3)
    show(cv, fr, T7d, t, w(7, "partir") - .1, None, CX, 600, 2)

def s7(cv, fr, t, T):
    shots(cv, fr, t, [(0, s7a), (w(7, "remontada") - .15, s7b), (w(7, "finale") - .15, s7c), (w(7, "et") - .1, s7d)], d=.24)
    impact(cv, t, w(7, "coince"), 14); impact(cv, t, w(7, "remontada"), 18); impact(cv, t, w(7, "perdue"), 12); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 8 — sans lui : 5-0 contre l'Inter, puis Arsenal
def s8a(cv, fr, t):
    stage_fill(cv, fr, NAVY_D, "pss8a")
    te = w(8, "explose")
    if t > te - .1:
        rays(cv, (CX, 1050), t, pop_in(t, te - .1, .2), 18, 1600, (250, 210, 100))
        particles(cv, fr, "psboom", (CX, 1050), prog(t, te - .1, .7), 30, 520, [GOLD, ROUGE, BLANC], 22)
    PSGP.draw(cv, fr, CX, 1780, 1.0, age=1, kit="psg", mood="cheer" if t > te else "determined", arms=(160, 160) if t > te else (20, 20), t=t)
    kw(cv, fr, K8a, t, .03, None, CX, 420, -3)

def s8b(cv, fr, t):
    stadium(cv, fr, "pss8stad", t, horizon=1060)
    t0 = w(8, "vingt-cinq") - .1; t5 = w(8, "cinq-zéro")
    g = min(5, int(prog(t, t0, t5 - t0 + .1)*5.99))
    score2(cv, fr, CX, 760, "PSG", "INTER", g, 0, "finale 2025", .75*(1 + .08*math.sin(t*20)*(1 - prog(t, t5, .4))))
    if t > t5:
        kw(cv, fr, K8b, t, t5, None, CX, 420, -4)
        confetti(cv, fr, "psc8", t - t5, 100, 4, [NAVY, ROUGE, GOLD])
    else:
        show(cv, fr, T8a, t, t0 + .05, None, CX, 430, -2)
    show(cv, fr, T8b, t, w(8, "finale") - .05, None, CX, 1010, 2)
    trophy_lift(cv, fr, PSGP2, CX, 1790, .8, "psg", t) if t > t5 + .2 else PSGP2.draw(cv, fr, CX, 1790, .8, age=1, kit="psg", mood="cheer", arms=(150, 150), t=t)

def s8c(cv, fr, t):
    stage_fill(cv, fr, (24, 30, 60), "pss8c")
    t0 = w(8, "Et", 2) - .1; ta = w(8, "Arsenal")
    kw(cv, fr, K8c, t, t0 + .05, None, CX, 400, -3)
    score2(cv, fr, CX, 760, "PSG", "ARSENAL", 1, 1, "4-3 aux tirs au but" if t > ta - .1 else "finale 2026", .75*pop_in(t, t0 + .1, .3))
    if t > ta - .1:
        show_stamp(cv, fr, K8d, t, ta - .1, CX, 1020, -5)
        UCL.draw(cv, fr, CX, 1420, 1.2*pop_in(t, ta, .3), 0)
        confetti(cv, fr, "psc8c", t - ta, 90, 3, [NAVY, ROUGE, GOLD])
    show(cv, fr, T8c, t, w(8, "recommence") - .05, None, CX, 560, 2)

def s8(cv, fr, t, T):
    shots(cv, fr, t, [(0, s8a), (w(8, "vingt-cinq") - .15, s8b), (w(8, "Et", 2) - .1, s8c)], d=.24)
    impact(cv, t, w(8, "explose"), 22); flashes(cv, t, w(8, "explose"), .12, .7); impact(cv, t, w(8, "cinq-zéro"), 24)
    impact(cv, t, w(8, "Arsenal"), 18); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 9 — double champion d'Europe, 54 ans après la D3 ; like + abonne-toi
def s9(cv, fr, t, T):
    band_bg(cv, fr, "pss9")
    rays(cv, (CX, 1000), t, .5, 16, 1500, (60, 90, 160))
    tu, tl, ta = w(9, "Une"), w(9, "Like"), w(9, "abonne-toi")
    a1 = 1 - prog(t, tu - .1, .25)
    for k, x in enumerate((300, 780)):
        UCL.draw(cv, fr, x, 1000 + 8*math.sin(t*5 + k), 1.3*a1 + .55*(1 - a1), (-5, 5)[k])
    if t > tu - .1:
        blit(cv, ucl_silhouette(), CX, 1000, 1.3*pop_in(t, tu - .1, .3))
        QM.draw(cv, fr, CX, 1000, pop_in(t, tu, .3), 6)
    kw(cv, fr, K9a, t, .03, tu - .15, CX, 400, -3)
    show(cv, fr, T9a, t, w(9, "cinquante-quatre") - .05, tu - .15, CX, 580, 2)
    kw(cv, fr, K9b, t, tu - .05, None, CX, 420, -4)
    if t > tl - .1:
        like_button(cv, fr, 260, 1440, .75*pop_in(t, tl - .1, .3), t, tl)
        press = 1 - .12*math.sin(prog(t, ta + .25, .25)*math.pi)
        BTN_SUB.draw(cv, fr, 700, 1440, .8*pop_in(t, ta - .1)*press, -2)
        kw(cv, fr, K9c, t, w(9, "d'épisodes") - .1, None, 700, 1600, 3)
        confetti(cv, fr, "psc9", t - ta, 80, 5, [NAVY, ROUGE, GOLD, BLANC])
    impact(cv, t, tu, 12); impact(cv, t, tl, 12); impact(cv, t, ta, 12); drift(cv, t, T, .05)

# ------------------------------------------------------------------ scènes + bruitages
def with_bar(fn):
    def g(cv, fr, t, T):
        fn(cv, fr, t, T); chrono_bar(cv, fr, SCENES)
    return g
def SC(name, n, fn, sfx, trans=None, trans_dur=.25, pad_out=.25):
    return Scene(name, TEXTS[n-1], with_bar(fn), sfx, pad_in=PAD, pad_out=pad_out, trans=trans, trans_dur=trans_dur)
W_ = w
SCENES = [
    SC("d3", 1, s1, [(.0, "boom", .9), (.0, "stamp", .8), (.05, "riser", .4), (W_(1, "envoyé") - .05, "elevator", .9), (W_(1, "division"), "boom", .7),
                     (W_(1, "deux"), "pop"), (W_(1, "Aujourd'hui") - .1, "whoosh_up", .7), (W_(1, "Aujourd'hui") + .1, "stamp", .6),
                     (W_(1, "Aujourd'hui") + .35, "stamp", .6), (W_(1, "double"), "crowd_long", .9), (W_(1, "champion"), "sparkle"),
                     (W_(1, "L'histoire") - .1, "whoosh", .5), (W_(1, "L'histoire"), "stamp", .7), (W_(1, "minute") - .1, "tick", .9)]),
    SC("1970", 2, s2, [(.0, "boom", .5), (W_(2, "Mille"), "stamp", .6), (W_(2, "Paris"), "pop"), (W_(2, "première"), "pop2"),
                       (W_(2, "Plus", 2) - .1, "whoosh", .5), (W_(2, "Plus", 2), "tick", .8), (W_(2, "oui"), "crowd", .8), (W_(2, "oui"), "stamp", .6),
                       (W_(2, "et") - .1, "whoosh", .5), (W_(2, "et"), "pop"), (W_(2, "et") + .15, "pop2"), (W_(2, "fusion") - .3, "swish"),
                       (W_(2, "fusion") + .05, "stamp"), (W_(2, "fusion") + .05, "sparkle", .6)], trans="punch", trans_dur=.3),
    SC("divorce", 3, s3, [(.03, "stamp", .6), (W_(3, "divorce"), "rip"), (W_(3, "Paris"), "pop"), (W_(3, "et") - .1, "whoosh", .5),
                          (W_(3, "repart") - .1, "elevator", .9), (W_(3, "division", 2), "boom", .7), (W_(3, "division", 2) + .1, "groan", .6),
                          (W_(3, "Mais") - .1, "whoosh_up", .8), (W_(3, "soixante-quatorze"), "stamp", .6), (W_(3, "Parc") - .1, "boom", .5),
                          (W_(3, "Parc"), "crowd_long", .8), (W_(3, "remonté"), "pop")], trans="whip"),
    SC("ngotty", 4, s4, [(.0, "boom", .5), (W_(4, "quatre-vingt-six") - .1, "stamp", .6), (W_(4, "titre"), "stamp"), (W_(4, "titre"), "crowd", .8),
                         (W_(4, "Et") - .1, "whoosh", .5), (W_(4, "quatre-vingt-seize") - .1, "stamp", .6), (W_(4, "boulet") - .05, "kick"),
                         (W_(4, "boulet") + .45, "boom", .7), (W_(4, "boulet") + .45, "crowd_long", 1.0), (W_(4, "coupe"), "stamp"),
                         (W_(4, "coupe") + .1, "sparkle")], trans="tear_h", trans_dur=.5),
    SC("qatar", 5, s5, [(.0, "boom", .5), (W_(5, "onze") - .15, "stamp", .6), (W_(5, "Qatar") - .1, "whoosh_up", .6), (W_(5, "rachète"), "cash"),
                        (W_(5, "rachète"), "stamp", .6), (W_(5, "Ibrahimović") - .15, "whoosh", .5)] +
                       [(W_(5, wd) - .1, snd) for wd, snd in (("Ibrahimović", "pop"), ("Neymar", "pop2"), ("Mbappé", "pop"), ("Messi", "pop2"))] +
                       [(W_(5, "deux", 2), "cash"), (W_(5, "deux", 2) + .1, "flash", .5), (W_(5, "Paris") - .1, "whoosh", .5),
                        (W_(5, "machine") - .1, "stamp"), (W_(5, "machine"), "clink", .8)], trans="whip"),
    SC("pause", 6, s6, [(0, "scratch", 1.0, .9), (.3, "pop"), (W_(6, "kiffes") - .1, "pop2"), (W_(6, "like"), "pop"), (W_(6, "like") + .05, "notif"),
                        (W_(6, "like") + .1, "sparkle", .6), (W_(6, "abonne-toi"), "pop2"), (W_(6, "abonne-toi") + .25, "notif"),
                        (W_(6, "Allez"), "whoosh"), (W_(6, "Allez"), "boom", .5)], trans="polaroid", pad_out=.3),
    SC("c1", 7, s7, [(.0, "boom", .5), (W_(7, "Ligue") - .1, "stamp", .5), (W_(7, "coince") - .1, "jail", .8), (W_(7, "remontada") - .15, "whoosh", .5),
                     (W_(7, "remontada"), "glitch", .7, .35), (W_(7, "remontada"), "stamp"), (W_(7, "finale") - .15, "whoosh", .5),
                     (W_(7, "perdue"), "groan", .6), (W_(7, "et") - .1, "whoosh", .5), (W_(7, "Mbappé"), "plane", .5)], trans="tear_d", trans_dur=.5),
    SC("sacre", 8, s8, [(.03, "stamp", .6), (W_(8, "explose") - .1, "riser", .6), (W_(8, "explose"), "boom"), (W_(8, "vingt-cinq") - .15, "whoosh", .5)] +
                       [(W_(8, "vingt-cinq") - .1 + k*(W_(8, "cinq-zéro") - W_(8, "vingt-cinq") + .2)/6, "kick", .6) for k in range(1, 6)] +
                       [(W_(8, "cinq-zéro"), "crowd_long", 1.0), (W_(8, "cinq-zéro"), "stamp"), (W_(8, "Et", 2) - .1, "whoosh", .5),
                        (W_(8, "recommence"), "whistle", .5), (W_(8, "Arsenal") - .1, "stamp"), (W_(8, "Arsenal"), "crowd", .9),
                        (W_(8, "Arsenal"), "sparkle")], trans="whip"),
    SC("fin", 9, s9, [(.0, "boom", .6), (.03, "stamp", .6), (W_(9, "cinquante-quatre"), "pop"), (W_(9, "Une") - .1, "whoosh", .5), (W_(9, "Une"), "stamp", .6),
                      (W_(9, "Like"), "pop"), (W_(9, "Like") + .05, "notif"), (W_(9, "abonne-toi"), "pop2"), (W_(9, "abonne-toi") + .25, "notif"),
                      (W_(9, "abonne-toi") + .1, "crowd", .7), (W_(9, "d'épisodes") - .1, "sparkle")], trans="punch", trans_dur=.3, pad_out=1.2),
]
SCENES[5].trans_dur = 99      # la photo figée reste épinglée pendant toute la pause
SCENES[5].post = s6_post

# ------------------------------------------------------------------ couverture
# Couverture « débat » (différente du gabarit habituel titre + joueur + bandeau) : question en lettres découpées façon lettre anonyme,
# nuit + projecteur, joueur couronné sur la 1re marche d'un podium « PSG », 2e et 3e marches avec « ? » (qui d'autre ?).
def _crown(d, a):
    ax, ay = a
    for k, c in enumerate((ROUGE, (40, 90, 200), ROUGE)):
        x = ax - 60 + k*60; d.ellipse([x - 13, ay + 22, x + 13, ay + 48], fill=c, outline=NOIR, width=2)
    d.line([(ax - 104, ay + 8), (ax + 104, ay + 8)], fill=(190, 138, 20), width=5)
CROWN = Paper(poly_pts([(-110, 60), (-110, -40), (-62, 4), (-30, -66), (0, -16), (30, -66), (62, 4), (110, -40), (110, 60)]),
              GOLD, "pscrown", rough=1.4, hatch=True).add(_crown)
POD1 = Paper(rect_pts(500, 260), BLANC, "pspod1", rough=1.8, hatch=True).add(
    lambda d, a: (d.rectangle([a[0] - 250, a[1] - 130, a[0] + 250, a[1] - 100], fill=ROUGE),
                  d.text((a[0], a[1] + 30), "PSG", font=font("title", 190), fill=NAVY, anchor="mm")))
def _pod(n, w_, h_):
    return Paper(rect_pts(w_, h_), (150, 156, 172), f"pspod{n}", rough=1.8, hatch=True).add(
        lambda d, a: d.text((a[0], a[1]), "?", font=font("title", 130), fill=BLANC, anchor="mm", stroke_width=6, stroke_fill=NAVY_D))
POD2, POD3 = _pod(2, 250, 190), _pod(3, 250, 130)

def cover(path, l1="LE PLUS GRAND", l2="CLUB DE FRANCE ?", strip="…ET D'EUROPE ?!"):
    cv = background(0, TITLE); stage_fill(cv, 0, NAVY_D, "pscovn"); d = ImageDraw.Draw(cv)
    beam(cv, (CX, -80), [(CX + 360, 1440), (CX - 360, 1440)], .13)                 # projecteur sur le n° 1
    L = Image.new("RGBA", cv.size, (0, 0, 0, 0)); ImageDraw.Draw(L).ellipse([CX - 420, 1380, CX + 420, 1500], fill=(255, 244, 200, 60))
    cv.paste(L, (0, 0), L)
    confetti(cv, 0, "pscovc", 1.6, 70, 4, [GOLD, BLANC, ROUGE])
    POD2.draw(cv, 0, CX - 375, 1540 + 30, 1, 0); POD3.draw(cv, 0, CX + 375, 1540 + 60, 1, 0)
    POD1.draw(cv, 0, CX, 1540, 1, 0)
    for k, x in enumerate((CX - 175, CX + 175)): UCL.draw(cv, 0, x, 1410 - 105*.75 + 8, .75, (-6, 6)[k])
    PSGP.draw(cv, 0, CX, 1418, .92, age=1, kit="psg", mood="cheer", arms=(150, 150), legs=(10, 10), t=1)
    CROWN.draw(cv, 0, CX + 4, 1418 - 668*.92, .78, -6)
    ransom_line(cv, l1, 320, 138, seed=8)
    ransom_line(cv, l2, 490, 138, seed=21)
    Label(strip, "pscvq", font("title", 76), NOIR, GOLD, maxw=1040, padx=30, pady=8, rough=5).draw(cv, 0, CX, 655, 1, -3)
    sw = Label("EN 1 MIN", "pscv1m", font("title", 44), BLANC, ROUGE, padx=18, pady=6, rough=3)
    sw.draw(cv, 0, 880, 960, 1, 10)
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
        p = os.path.join(out, f"ps_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", "psg")
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/psg_stills"), only=only)); sys.exit()
    if os.environ.get("LEGENDES_PROVISOIRE") and "--apercu" not in args:
        sys.exit("Minutage provisoire : pas de rendu final sans les vraies voix (--apercu pour un aperçu muet).")
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25))
