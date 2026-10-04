"""Épisode « Légendes du foot » #7 : l'histoire du Dijon FCO, format court et nerveux (~1 min 15).
« DIJON » + pot de moutarde dès la 1re image, barre « chrono » en haut (« l'histoire en une minute »), un plan toutes les ~1,5 s :
moutarde -> Dijon bat le PSG de Mbappé -> chute en 3e division ; 1998 rouge et blanc, stade Gaston-Gérard et son poulet ;
Rudi Garcia, demi-finale de Coupe de France depuis la 3e division ; Ligue 1 en 2011 puis 2016 (il s'accroche) ;
le dernier bat le premier (2-1 contre le PSG) ; pause « quel club ? » ; 2021 dernier de L1, National ; Tavares rappelé,
champion du National 2026, retour en Ligue 2 ; fin « prochaine étape : la Ligue 1 ? ».

  python3 episodes/dijon/dijon.py output/dijon --stills [3,4]
  python3 episodes/dijon/dijon.py output/dijon --cover
  python3 episodes/dijon/dijon.py output/dijon
Variable LEGENDES_PROVISOIRE=<dossier avec voix/ et alignement.json> : minutage provisoire (avant les vraies voix).
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from story import *
import engine

TITLE = "~/légendes $ ./dijon_fco"
SLUG = "dijon_legende"
SRC = os.environ.get("LEGENDES_PROVISOIRE") or HERE
VOICE = [os.path.join(SRC, "voix", f"scene_{i}.mp3") for i in range(1, 10)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
ALIGN = os.path.join(SRC, "alignement.json")
PAD = 0.12
WS, TEXTS = load_words(ALIGN)
def w(i, word, n=1, end=False):
    """Temps local (dans la scène i) où la voix prononce `word`."""
    return PAD + WS[i-1](word, n, end)

ROUGE = (214, 26, 42); ROUGE_D = (130, 18, 30); BLANC = (250, 250, 246); MOUT = (222, 176, 34); MOUT_D = (170, 128, 20)
NAVY = (16, 40, 86); GOLD = (236, 186, 48); GRIS = (120, 120, 126); NOIR = (30, 28, 28)

DJ = Player("djp", hair=(60, 40, 30), skin=(226, 180, 140))
DJ2 = Player("djp2", hair=(24, 20, 18), skin=(150, 100, 72))
MBAP = Player("mbap", hair=(24, 20, 18), skin=(126, 86, 62), hair_style="bald")
PSGP = Player("psgp", hair=(70, 50, 36), skin=(230, 186, 150))
GARC = Player("garc", hair=(54, 40, 32), skin=(226, 182, 146))
MAIRE = Player("maire", hair=(90, 84, 80), skin=(232, 196, 166), hair_style="bald")
TAVA = Player("tava", hair=(24, 20, 18), beard_col=(30, 24, 20), skin=(108, 72, 52), hair_style="bald")

# ------------------------------------------------------------------ objets
def _jar_decor(d, a):
    ax, ay = a
    d.rectangle([ax-150, ay-210, ax+150, ay-160], fill=(236, 236, 230)); d.rectangle([ax-150, ay-210, ax+150, ay-196], fill=(200, 200, 196))
    d.rounded_rectangle([ax-128, ay-60, ax+128, ay+110], 14, fill=(250, 246, 230), outline=ROUGE_D, width=6)
    d.text((ax, ay-8), "MOUTARDE", font=font("title", 44), fill=ROUGE_D, anchor="mm")
    d.text((ax, ay+62), "de Dijon", font=font("hand", 50), fill=PAL["ink"], anchor="mm")
JAR = Paper(poly_pts([(-150, -210), (150, -210), (150, -160), (170, -130), (170, 180), (150, 210), (-150, 210), (-170, 180), (-170, -130), (-150, -160)]),
            MOUT, "djjar", rough=1.6, hatch=True, pad=40).add(_jar_decor)

def _owl_decor(d, a):
    ax, ay = a
    for dx in (-44, 44):
        d.ellipse([ax+dx-40, ay-86, ax+dx+40, ay-6], fill=(250, 246, 230)); d.ellipse([ax+dx-18, ay-64, ax+dx+18, ay-28], fill=PAL["ink"])
        d.ellipse([ax+dx-6, ay-58, ax+dx+4, ay-48], fill=BLANC)
    d.polygon([(ax-14, ay-10), (ax+14, ay-10), (ax, ay+20)], fill=(236, 160, 40))
    for k in range(4): d.arc([ax-60 + k*30, ay+40, ax-30 + k*30, ay+70], 0, 180, fill=(110, 84, 60), width=5)
OWL = Paper(poly_pts([(-100, -100), (-78, -150), (-50, -110), (50, -110), (78, -150), (100, -100), (110, 40), (70, 120), (-70, 120), (-110, 40)]),
            (150, 116, 80), "djowl", rough=1.6, hatch=True, pad=30).add(_owl_decor)

def _chicken_decor(d, a):
    ax, ay = a
    d.ellipse([ax-110, ay-80, ax+60, ay-20], fill=(226, 156, 84))                       # reflet doré
    for sg in (-1, 1):                                                                 # pilons dressés + os
        d.polygon([(ax+sg*70, ay-40), (ax+sg*150, ay-60), (ax+sg*190, ay-150), (ax+sg*140, ay-170), (ax+sg*80, ay-110)], fill=(150, 80, 30))
        d.rectangle([ax+sg*165-10, ay-205, ax+sg*165+10, ay-150], fill=(250, 246, 230))
        d.ellipse([ax+sg*165-22, ay-230, ax+sg*165-2, ay-200], fill=(250, 246, 230)); d.ellipse([ax+sg*165+2, ay-230, ax+sg*165+22, ay-200], fill=(250, 246, 230))
CHICKEN = Paper(ellipse_pts(360, 220, 40), (176, 96, 40), "djchicken", rough=2, hatch=True, pad=130).add(_chicken_decor)
def cloche(cv, x, y, u):
    """Cloche de service qui se soulève (u : 0 = posée, 1 = partie en l'air)."""
    if u >= 1: return
    L = layer(560, 360, (280, 330)); d = ImageDraw.Draw(L)
    d.chord([20, 40, 540, 600], 180, 360, fill=(200, 204, 214), outline=(120, 124, 136), width=6)
    d.arc([80, 90, 300, 400], 200, 250, fill=(240, 242, 248), width=10); d.ellipse([250, 10, 310, 60], fill=(150, 154, 166))
    blit(cv, L, x + 260*u, y - 900*ease_in_cubic(u), 1, -40*u)
PLATE = Paper(ellipse_pts(620, 220, 50), (250, 250, 246), "djplate", rough=1.2)

def _sign_decor(d, a):
    ax, ay = a
    d.text((ax, ay-34), "STADE", font=font("title", 60), fill=BLANC, anchor="mm")
    d.text((ax, ay+40), "GASTON-GÉRARD", font=font("title", 76), fill=BLANC, anchor="mm")
SIGN = Paper(rect_pts(700, 220), ROUGE, "djsign", rough=2, hatch=True).add(_sign_decor)

def _phone_decor(d, a):
    ax, ay = a
    d.rounded_rectangle([ax-70, ay-130, ax+70, ay+120], 22, fill=(40, 44, 56)); d.rectangle([ax-56, ay-104, ax+56, ay+84], fill=(120, 200, 140))
    d.text((ax, ay-50), "DFCO", font=font("title", 40), fill=PAL["ink"], anchor="mm"); d.text((ax, ay), "appel…", font=font("hand", 36), fill=PAL["ink"], anchor="mm")
    d.ellipse([ax-40, ay+30, ax-10, ay+60], fill=(60, 170, 80)); d.ellipse([ax+10, ay+30, ax+40, ay+60], fill=(220, 60, 60))
PHONE = Paper(rect_pts(170, 280), (70, 74, 86), "djphone", rough=1.2).add(_phone_decor)

def mustache(cv, eyes, s, col=(70, 60, 54)):
    if not eyes: return
    (x1, y1), (x2, y2) = eyes; hx = (x1+x2)/2; hy = (y1+y2)/2 - 8*s
    ImageDraw.Draw(cv).polygon([(hx-34*s, hy+36*s), (hx-22*s, hy+20*s), (hx, hy+24*s), (hx+22*s, hy+20*s), (hx+34*s, hy+36*s), (hx, hy+30*s)], fill=col)

def sash(cv, x, y, s):
    """Écharpe tricolore du maire, en travers du torse."""
    d = ImageDraw.Draw(cv); x0, y0 = x - 70*s, y - 500*s; x1, y1 = x + 70*s, y - 320*s
    for k, c in enumerate(((24, 44, 120), BLANC, (206, 32, 44))):
        o = (k - 1)*16*s; d.polygon([(x0 + o, y0), (x0 + o + 22*s, y0), (x1 + o + 22*s, y1), (x1 + o, y1)], fill=c)

def splat(cv, x, y, r, t, seed=0, col=MOUT):
    """Éclaboussure de moutarde (impact)."""
    if r <= 2: return
    d = ImageDraw.Draw(cv); rnd = random.Random(seed)
    d.ellipse([x-r, y-r*.8, x+r, y+r*.8], fill=col)
    for k in range(9):
        an = rnd.uniform(0, 2*math.pi); rr = r*rnd.uniform(1.1, 1.8); s = r*rnd.uniform(.12, .3)
        d.ellipse([x + rr*math.cos(an) - s, y + rr*math.sin(an)*.8 - s, x + rr*math.cos(an) + s, y + rr*math.sin(an)*.8 + s], fill=col)

def stopwatch(cv, x, y, s, u):
    d = ImageDraw.Draw(cv)
    d.rectangle([x-18*s, y-150*s, x+18*s, y-118*s], fill=(80, 80, 88)); d.ellipse([x-120*s, y-120*s, x+120*s, y+120*s], fill=(80, 80, 88))
    d.ellipse([x-104*s, y-104*s, x+104*s, y+104*s], fill=(250, 250, 246))
    for k in range(12):
        an = k*math.pi/6; d.line([(x+88*s*math.sin(an), y-88*s*math.cos(an)), (x+100*s*math.sin(an), y-100*s*math.cos(an))], fill=PAL["ink"], width=max(2, int(5*s)))
    an = u*math.pi*2; d.line([(x, y), (x+80*s*math.sin(an), y-80*s*math.cos(an))], fill=ROUGE, width=max(3, int(8*s)))
    d.ellipse([x-10*s, y-10*s, x+10*s, y+10*s], fill=PAL["ink"])

SCOREBOARD = scoreboard_sprite(820, 330, "djscore")
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

def checks(d, col=ROUGE, n=10, y0=None):
    """Nappe à carreaux rouges et blancs."""
    sx0, sy0, sx1, sy1 = STAGE; y0 = sy0 if y0 is None else y0; c = (sx1 - sx0)/n
    for i in range(n):
        for j in range(int((sy1 - y0)/c) + 1):
            if (i + j) % 2 == 0: d.rectangle([sx0 + i*c, y0 + j*c, sx0 + (i+1)*c, y0 + (j+1)*c], fill=col)

def walk(t, speed=9, amp=22):
    ph = math.sin(t*speed); return (amp*ph, -amp*ph), abs(math.sin(t*speed))*8

def stadium(cv, fr, key, t=0.0, sky=(18, 22, 46), grass=(46, 112, 64), horizon=1060, pal=None):
    stage_fill(cv, fr, sky, key); d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    rnd = random.Random(key)
    pal = pal or [ROUGE, BLANC, (200, 196, 190), (160, 40, 40), (250, 230, 120), (70, 60, 60)]
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

def trophy_lift(cv, fr, pl, x, y, s, kit, t, trophy=CUP, mood="cheer"):
    pl.draw(cv, fr, x, y, s, age=1, kit=kit, mood=mood, arms=(160, 160), legs=(12, 12), t=t)
    trophy.draw(cv, fr, x, y - 850*s + 8*math.sin(t*6), .9*s, 3*math.sin(t*4))

def shaft(cv, fr, t, speed=0.0, key="djshaft"):
    stage_fill(cv, fr, (34, 32, 40), key); d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    for j in range(8):
        y = (j*260 + t*speed) % 2080 - 80
        d.rectangle([sx0, y, sx1, y + 16], fill=(70, 66, 80)); d.line([(sx0, y + 30), (sx1, y + 30)], fill=(56, 52, 64), width=4)

def calendar(cv, fr, x, y, txt, s=1.0, rot=0.0, a=1.0, top=""):
    if a <= .01 or s < .05: return
    L = layer(int(300*s), int(320*s), (150*s, 160*s)); d = ImageDraw.Draw(L)
    d.rectangle([10*s, 30*s, 290*s, 310*s], fill=(250, 248, 238), outline=PAL["ink"], width=max(2, int(5*s)))
    d.rectangle([10*s, 30*s, 290*s, 100*s], fill=ROUGE)
    if top: d.text((150*s, 66*s), top, font=font("title", int(40*s)), fill=BLANC, anchor="mm")
    for k in (80, 220): d.rectangle([(k-8)*s, 10*s, (k+8)*s, 50*s], fill=(80, 80, 88))
    d.text((150*s, 205*s), txt, font=font("title", int(96*s)), fill=PAL["ink"], anchor="mm")
    blit(cv, L, x, y, 1, rot, a)

def rain(cv, t, n=60, col=(140, 150, 170)):
    d = ImageDraw.Draw(cv)
    for k in range(n):
        x = (k*89) % 1060 + 10; y = (k*173 + t*1300) % 1800 + 120; d.line([(x, y), (x - 8, y + 36)], fill=col, width=3)

def ledge(cv, fr, y, t, s=.9, key="djledge"):
    """Joueur suspendu à une poutre « LIGUE 1 » (il s'accroche), les jambes qui battent."""
    d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    d.rectangle([sx0, y - 40, sx1, y + 40], fill=(120, 124, 136), outline=PAL["ink"], width=6)
    LBL("LIGUE 1", "djl1", font("title", 60), BLANC, None).draw(cv, fr, 220, y, 1, 0)
    L = DJ.render_layer(fr, s, age=1, kit="dijon", mood="determined", arms=(172, 172), legs=(22*math.sin(t*9), -22*math.sin(t*9)))
    hy = y + 20 + 20*math.sin(t*3)   # les mains agrippées sous la poutre
    blit(cv, L, CX + 10*math.sin(t*3), hy + 695*s, 1, 4*math.sin(t*3))

_TOTAL = {}
def chrono_bar(cv, fr):
    """Barre « chrono » en haut de l'écran (l'histoire en une minute) : se remplit sur toute la vidéo."""
    if "T" not in _TOTAL:
        tot = sum(getattr(sc, "T", 0) for sc in SCENES)
        if tot <= 0: return
        _TOTAL["T"] = tot
    u = clamp(fr/FPS/_TOTAL["T"]); d = ImageDraw.Draw(cv)
    x0, x1, y = 60, W - 60, 176
    d.rounded_rectangle([x0, y - 9, x1, y + 9], 9, fill=(30, 28, 32))
    if u > 0: d.rounded_rectangle([x0, y - 9, x0 + 18 + (x1 - x0 - 18)*u, y + 9], 9, fill=MOUT)
    cx = x0 + 9 + (x1 - x0 - 18)*u; d.ellipse([cx - 16, y - 16, cx + 16, y + 16], fill=ROUGE, outline=BLANC, width=4)

def row(cv, fr, y, txt, hl_, a=1.0, key="djrow"):
    if a <= .01: return
    LBL(txt, key + ("h" if hl_ else "n"), font("title", 64), BLANC if hl_ else PAL["ink"], ROUGE if hl_ else PAL["paper"], padx=24, pady=6, rough=2, maxw=860).draw(cv, fr, CX, y, a, 0)

# ------------------------------------------------------------------ labels
DIJON = Label("DIJON", "djtitle", font("title", 230), BLANC, ROUGE, padx=50, pady=6, rough=4)
T1a = TAG("connue dans le monde entier", "djt1a", PAL["paper"], size=54)
K1a = KW("LE PSG DE MBAPPÉ", "djk1a", NAVY, size=96); K1b = KW("3e DIVISION", "djk1b", ROUGE, size=120)
K1c = STAMP("L'HISTOIRE DU DFCO", "djk1c", ROUGE, 96); K1d = KW("EN 1 MINUTE", "djk1d", PAL["ink"], MOUT, 110)
K2a = KW("1998", "djk2a", PAL["ink"], size=170); N2 = STAMP("DFCO", "djn2", ROUGE, 160); T2a = TAG("né d'une fusion de 2 clubs dijonnais", "djt2a", PAL["paper"], size=46)
SW_R = Label("ROUGE", "djswr", font("title", 96), BLANC, ROUGE, padx=40, pady=16, rough=4)
SW_B = Label("BLANC", "djswb", font("title", 96), PAL["ink"], BLANC, padx=40, pady=16, rough=4)
T2b = TAG("ancien maire de Dijon", "djt2b", PAL["paper"], size=54)
K2b = KW("POULET GASTON GÉRARD", "djk2b", MOUT, PAL["ink"], 86); T2c = TAG("à la moutarde, évidemment", "djt2c", PAL["paper"], size=50)
K3a = KW("2002", "djk3a", PAL["ink"], size=170); N3 = STAMP("RUDI GARCIA", "djn3", ROUGE, 120)
T3a = TAG("futur champion de France avec Lille", "djt3a", PAL["paper"], size=46)
K3b = KW("DEMI-FINALE !", "djk3b", ROUGE, size=120); T3b = TAG("Coupe de France 2004", "djt3b", PAL["paper"], size=54)
T3c = TAG("depuis la 3e division !", "djt3c", PAL["mustard"], size=54); K3c = STAMP("LIGUE 2 !", "djk3c", ROUGE, 150)
K4a = KW("2011", "djk4a", PAL["ink"], size=170); K4b = STAMP("LIGUE 1 !", "djk4b", ROUGE, 150); T4a = TAG("une 1re dans son histoire", "djt4a", PAL["paper"], size=54)
K4c = KW("1 AN SEULEMENT", "djk4c", PAL["ink"], size=110); K4d = KW("2016", "djk4d", PAL["ink"], size=150)
K4e = STAMP("IL S'ACCROCHE !", "djk4e", ROUGE, 120); T4b = TAG("5 saisons en Ligue 1", "djt4b", PAL["paper"], size=54)
K5a = KW("1er NOVEMBRE 2019", "djk5a", PAL["ink"], size=96)
RK_D = Label("20e", "djrkd", font("title", 90), BLANC, ROUGE, padx=24, pady=4, rough=2); RK_P = Label("1er", "djrkp", font("title", 110), BLANC, NAVY, padx=28, pady=4, rough=2)
K5b = KW("MBAPPÉ", "djk5b", NAVY, size=120); K5c = KW("2 - 1 !", "djk5c", ROUGE, size=220)
K5d = STAMP("LE DERNIER BAT LE PREMIER !", "djk5d", ROUGE, 66)
K6a = KW("PETITE PAUSE !", "djk6a", PAL["ink"], size=84)
K6b = Label("QUEL CLUB APRÈS ?", "djk6b", font("title", 74), PAL["cream"], ROUGE, maxw=460, padx=30, pady=8, rough=3.5)
NAMES6 = [LBL(n, f"djnm{n}", font("hand", 46), PAL["ink"], None) for n in ("Auxerre ?", "Lens ?", "Sochaux ?", "Nancy ?")]
K6c = KW("EN COMMENTAIRE", "djk6c", PAL["ink"], size=84); K6d = KW("ON REPREND !", "djk6d", PAL["ink"], size=84)
CARD = Paper(rect_pts(200, 250), PAL["paper"], "djcard", rough=2)
K7a = KW("2021", "djk7a", PAL["ink"], size=170); K7b = STAMP("DERNIER", "djk7b", ROUGE, 140)
K7c = KW("15 MATCHS SANS GAGNER", "djk7c", PAL["ink"], size=84); K7d = STAMP("NATIONAL", "djk7d", GRIS, 140)
T7a = TAG("hors du foot pro", "djt7a", PAL["paper"], size=56)
T8x = TAG("il rappelle sa légende…", "djt8x", PAL["paper"], size=56)
N8 = STAMP("JULIO TAVARES", "djn8", ROUGE, 110); T8a = TAG("80 buts : record du club", "djt8a", PAL["mustard"], size=54)
K8a = KW("2026", "djk8a", PAL["ink"], size=170); K8b = STAMP("CHAMPION DU NATIONAL", "djk8b", ROUGE, 86)
T8b = TAG("meilleure attaque + meilleure défense", "djt8b", PAL["paper"], size=46); K8c = KW("RETOUR EN LIGUE 2 !", "djk8c", PAL["ink"], MOUT, 92)
K9a = KW("PROCHAINE ÉTAPE : LA LIGUE 1 ?", "djk9a", PAL["ink"], size=58)
BTN_O = Label("OUI", "djbo", font("title", 110), PAL["ink"], MOUT, padx=40, pady=10, rough=3)
BTN_N = Label("NON", "djbn", font("title", 110), BLANC, (90, 90, 96), padx=40, pady=10, rough=3)
K9b = KW("DEMANDE TON CLUB !", "djk9b", ROUGE, size=86)
BTN_SUB = Label("+ ABONNE-TOI", "djbsub", font("title", 96), (255, 255, 255), (230, 40, 80), padx=40, pady=14, rough=2.5)

# ------------------------------------------------------------------ SCÈNE 1 — DIJON : la moutarde… le PSG… la 3e division
def s1a(cv, fr, t):
    stage_fill(cv, fr, MOUT, "djs1a")
    rays(cv, (CX, 1060), t, 1.0, 16, 1500, (250, 214, 90))
    tm = w(1, "moutarde")
    JAR.draw(cv, fr, CX, 1080 + 10*math.sin(t*5), 1.55*ease_out_back(prog(t, 0, .3)) if t > 0 else .3, 4*math.sin(t*3))
    OWL.draw(cv, fr, 840, 1500 + 8*math.sin(t*6), pop_in(t, tm - .1, .35)*.95, -8)
    if t > tm: splat(cv, 230, 1500, 70*pop_in(t, tm, .25), t, 3)
    DIJON.draw(cv, fr, CX, 380, lerp(1.35, 1.0, ease_out_cubic(prog(t, 0, .25))), -3)
    show(cv, fr, T1a, t, w(1, "monde") - .1, None, CX, 620, 2)
    if t > w(1, "monde"):
        for k in range(6):
            an = k*1.05 + t*2; draw_star(cv, CX + 330*math.cos(an), 1080 + 300*math.sin(an), 26*(.5 + .5*math.sin(t*9 + k)), 1, t*3)

def s1b(cv, fr, t):
    stadium(cv, fr, "djs1stad", t, horizon=1100)
    tb = w(1, "battu")
    score2(cv, fr, CX, 820, "DIJON", "PSG", 2 if t > tb else 0, 1 if t > tb else 0, "", .8*pop_in(t, w(1, "mais") - .05, .3))
    DJ.draw(cv, fr, 300, 1760, 1.0, age=1, kit="dijon", mood="cheer", arms=(160, 160), legs=(12, 12), t=t)
    MBAP.draw(cv, fr, 790, 1760, 1.0, age=1, kit="psg", mood="surprised" if t > tb else "normal", t=t, look=(-1, 0))
    kw(cv, fr, K1a, t, w(1, "PSG") - .05, None, CX, 430, -3)

def s1c(cv, fr, t):
    te = w(1, "tombé") - .1; td = w(1, "division")
    stage_fill(cv, fr, ROUGE_D, "djs1c")
    DJ.draw(cv, fr, CX, 1740, 1.05, age=1, kit="dijon", mood="surprised", t=t)
    floor_panel(cv, fr, CX, 660, "L1", t, True, 1.6, 1)
    elevator_drop(cv, t, te, td - te)
    if t > td:
        shaft(cv, fr, t)
        DJ.draw(cv, fr, CX, 1740, 1.05, age=1, kit="dijon", mood="sad", t=t, look=(0, 1))
        floor_panel(cv, fr, CX, 660, "D3", t, True, 1.8, 1)
        kw(cv, fr, K1b, t, td, None, CX, 960, 3)

def s1d(cv, fr, t):
    stage_fill(cv, fr, ROUGE, "djs1d"); d = ImageDraw.Draw(cv)
    stripes(d, (236, 60, 70), 10)
    t0 = w(1, "L'histoire") - .1
    for P, x, k in ((DJ2, 240, 0), (DJ, CX, 1), (DJ2, 840, 2)):
        hop = 60*abs(math.sin(t*6 + k))
        P.draw(cv, fr, x, 1760 - hop, .8 if k != 1 else .95, age=1, kit="dijon", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
    show_stamp(cv, fr, K1c, t, t0 + .05, CX, 420, -4)
    kw(cv, fr, K1d, t, w(1, "minute") - .1, None, CX, 600, 3)
    stopwatch(cv, CX, 900, 1.1, prog(t, t0, 1.2))

def s1(cv, fr, t, T):
    shots(cv, fr, t, [(0, s1a), (w(1, "mais") - .1, s1b), (w(1, "puis") - .1, s1c), (w(1, "L'histoire") - .1, s1d)], d=.24)
    impact(cv, t, .02, 18); impact(cv, t, w(1, "moutarde"), 12); impact(cv, t, w(1, "battu"), 18); flashes(cv, t, w(1, "battu"), .1, .6)
    impact(cv, t, w(1, "division") + .02, 24); punch(cv, t, w(1, "L'histoire") - .1, 1.1); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 2 — 1998, rouge et blanc, stade Gaston-Gérard… et son poulet
def s2a(cv, fr, t):
    stage_fill(cv, fr, (240, 232, 214), "djs2a"); d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    tr, tb = w(2, "rouge"), w(2, "blanc")
    ar = pop_in(t, tr - .05, .3)
    if ar > 0: d.rectangle([sx0, sy0, sx0 + (CX - sx0)*ar, sy1], fill=ROUGE)
    spin(cv, fr, DJ, CX, 1760, 1.05, t, tr - .15, "street", "dijon", mood="happy")
    SW_R.draw(cv, fr, 290, 860, ar, -6); SW_B.draw(cv, fr, 790, 860, pop_in(t, tb - .05, .3), 5)
    kw(cv, fr, K2a, t, w(2, "mille") - .05, None, CX, 400, -3)
    show_stamp(cv, fr, N2, t, w(2, "DFCO") - .05, 300, 620, -6, t_out=w(2, "mille") - .1)
    show(cv, fr, T2a, t, w(2, "quatre-vingt-dix-huit"), None, CX, 600, 2)

def s2b(cv, fr, t):
    stage_fill(cv, fr, (176, 212, 236), "djs2b")
    ts, tm = w(2, "stade"), w(2, "maire")
    SIGN.draw(cv, fr, CX, 520, slam(t, ts - .1, .22), -2)
    a = pop_in(t, ts + .1, .35)
    eyes = MAIRE.draw(cv, fr, CX, 1780, 1.1*a, age=1, kit="suit", mood="happy", t=t, arms=(12, 30))
    if a > .9: mustache(cv, eyes, 1.1); sash(cv, CX, 1780, 1.1)
    show(cv, fr, T2b, t, tm - .1, None, CX, 760, -2)

def s2c(cv, fr, t):
    stage_fill(cv, fr, BLANC, "djs2c"); d = ImageDraw.Draw(cv)
    checks(d, (226, 60, 70), 9, 1000)
    tq, tp = w(2, "qui"), w(2, "poulet")
    PLATE.draw(cv, fr, CX, 1220, 1.1, 0)
    tr = w(2, "recette") - .1
    hop = 80*abs(math.sin((t - tp)*9)) if tp < t < tp + .9 else 0
    if t > tr: CHICKEN.draw(cv, fr, CX - 30, 1170 - hop, 1.0, 4*math.sin(t*12) if hop else 0)
    cloche(cv, CX - 20, 1230, prog(t, tr, .45))
    if tr < t < tr + .6:
        for k in range(8):
            an = k*math.pi/4 + t; r = 200 + 260*prog(t, tr, .6)
            draw_star(cv, CX + r*math.cos(an), 1080 + r*math.sin(an)*.6, 24*(1 - prog(t, tr, .6)), 1, t*4)
    JAR.draw(cv, fr, 860, 1150, .55*pop_in(t, tq, .3), 8)
    kw(cv, fr, K2b, t, tp - .05, None, CX, 430, -3)
    show(cv, fr, T2c, t, tp + .4, None, CX, 620, 2)
    if t > tp: splat(cv, 300, 860, 60*pop_in(t, tp, .2), t, 5)

def s2(cv, fr, t, T):
    shots(cv, fr, t, [(0, s2a), (w(2, "Son") - .1, s2b), (w(2, "qui") - .1, s2c)], d=.24)
    impact(cv, t, w(2, "mille"), 14); impact(cv, t, w(2, "stade"), 12); impact(cv, t, w(2, "poulet"), 16)
    punch(cv, t, w(2, "poulet"), 1.1); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 3 — Rudi Garcia, demi-finale de Coupe de France, Ligue 2
def s3a(cv, fr, t):
    stage_fill(cv, fr, (40, 46, 60), "djs3a"); d = ImageDraw.Draw(cv)
    stripes(d, (50, 58, 74), 8)
    tr = w(3, "Rudi")
    x = lerp(-160, CX, ease_out_cubic(prog(t, .1, tr - .1))); lg, bob = walk(t, 10, 20) if t < tr else ((0, 0), 0)
    GARC.draw(cv, fr, x, 1760 - bob, 1.05, age=1, kit="suit", mood="happy" if t > tr else "determined", legs=lg, arms=(14, 14) if t < tr else (14, 120), t=t)
    kw(cv, fr, K3a, t, w(3, "deux") - .05, None, CX, 400, -3)
    show_stamp(cv, fr, N3, t, tr - .05, CX, 620, -4)
    show(cv, fr, T3a, t, tr + .5, None, CX, 790, 2)

def s3b(cv, fr, t):
    stage_fill(cv, fr, (24, 50, 120), "djs3b")
    rays(cv, (CX, 1050), t, .9, 16, 1500, (60, 100, 190))
    td = w(3, "demi-finale")
    floor_panel(cv, fr, 250, 400, "D3", t, True, .9, pop_in(t, w(3, "troisième") - .1))
    show(cv, fr, T3c, t, w(3, "troisième") - .05, None, 680, 400, 3)
    CUP.draw(cv, fr, CX, 1000 + 8*math.sin(t*5), 1.6*slam(t, w(3, "Dijon") - .1, .25), 3*math.sin(t*3))
    kw(cv, fr, K3b, t, td - .05, None, CX, 640, -3)
    show(cv, fr, T3b, t, w(3, "Coupe") - .05, None, CX, 1330, 2)
    for P, x, k in ((DJ2, 230, 0), (DJ, 850, 1)):
        P.draw(cv, fr, x, 1780 - 50*abs(math.sin(t*6 + k)), .78, age=1, kit="dijon", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)

def s3c(cv, fr, t):
    t0 = w(3, "et") - .1; tl = w(3, "Ligue")
    if t < tl:
        shaft(cv, fr, t, 900 + 2000*prog(t, t0, tl - t0))
        floor_panel(cv, fr, CX, 640, "D3", t, False, 1.8, 1)
    else:
        stage_fill(cv, fr, ROUGE, "djs3l2"); rays(cv, (CX, 1000), t, 1.0, 16, 1500, (250, 120, 120))
        floor_panel(cv, fr, CX, 640, "L2", t, False, 1.8, 1)
        show_stamp(cv, fr, K3c, t, tl, CX, 960, -4)
        confetti(cv, fr, "djc3", t - tl, 70, 3, [BLANC, MOUT])
    DJ.draw(cv, fr, CX, 1760, 1.0, age=1, kit="dijon", mood="cheer" if t > tl else "surprised", arms=(150, 150) if t > tl else (40, 40), t=t)

def s3(cv, fr, t, T):
    shots(cv, fr, t, [(0, s3a), (w(3, "Deux", 3) - .1, s3b), (w(3, "et") - .1, s3c)], d=.24)
    impact(cv, t, w(3, "Rudi"), 14); impact(cv, t, w(3, "demi-finale"), 18); impact(cv, t, w(3, "Ligue"), 18)
    flashes(cv, t, w(3, "Ligue"), .1, .5); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 4 — Ligue 1 en 2011, un an, retour en 2016 : il s'accroche
def s4a(cv, fr, t):
    stage_fill(cv, fr, ROUGE, "djs4a"); rays(cv, (CX, 1000), t, 1.0, 16, 1500, (250, 110, 110))
    tl = w(4, "Ligue")
    for P, x, k in ((DJ2, 260, 0), (DJ, 800, 1)):
        hop = 70*abs(math.sin(t*6 + k)) if t > tl else 0
        P.draw(cv, fr, x, 1760 - hop, .95, age=1, kit="dijon", mood="cheer" if t > tl else "happy", arms=(150, 150) if t > tl else (20, 20), t=t)
    kw(cv, fr, K4a, t, .03, None, CX, 400, -3)
    show_stamp(cv, fr, K4b, t, tl - .05, CX, 640, 4)
    show(cv, fr, T4a, t, w(4, "histoire") - .1, None, CX, 830, -2)
    confetti(cv, fr, "djc4", t - tl, 80, 3, [BLANC, MOUT])

def s4b(cv, fr, t):
    te = w(4, "Elle") + .15; td = w(4, "an") + .1
    stage_fill(cv, fr, ROUGE_D, "djs4b")
    DJ.draw(cv, fr, CX, 1740, 1.05, age=1, kit="dijon", mood="surprised", t=t)
    floor_panel(cv, fr, CX, 680, "L1", t, True, 1.5, 1)
    elevator_drop(cv, t, te, td - te)
    if t > td:
        shaft(cv, fr, t, 0, "djs4shaft"); DJ.draw(cv, fr, CX, 1740, 1.05, age=1, kit="dijon", mood="sad", t=t, look=(0, 1))
        floor_panel(cv, fr, CX, 680, "L2", t, True, 1.5, 1)
    kw(cv, fr, K4c, t, w(4, "dure") - .05, None, CX, 400, -3)

def s4c(cv, fr, t):
    stage_fill(cv, fr, (176, 212, 236), "djs4c")
    ta = w(4, "s'accroche")
    kw(cv, fr, K4d, t, w(4, "seize") - .05, ta - .1, CX, 400, -3)
    if t < ta - .05:
        DJ.draw(cv, fr, CX, 1760, 1.05, age=1, kit="dijon", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
        show(cv, fr, T4b, t, w(4, "revient"), None, CX, 620, 2)
    else:
        ledge(cv, fr, 760, t)
        show_stamp(cv, fr, K4e, t, ta - .05, CX, 400, -4)
        show(cv, fr, T4b, t, ta + .3, None, CX, 570, 2)

def s4(cv, fr, t, T):
    shots(cv, fr, t, [(0, s4a), (w(4, "Elle") - .1, s4b), (w(4, "mais") - .1, s4c)], d=.24)
    impact(cv, t, w(4, "Ligue"), 18); flashes(cv, t, w(4, "Ligue"), .1, .5); impact(cv, t, w(4, "an") + .1, 18)
    impact(cv, t, w(4, "s'accroche"), 14); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 5 — le dernier bat le premier : Dijon 2-1 PSG
def s5a(cv, fr, t):
    stage_fill(cv, fr, (240, 232, 214), "djs5a"); d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    d.polygon([(CX + 80, sy0), (sx1, sy0), (sx1, sy1), (CX - 80, sy1)], fill=NAVY)
    td, tp = w(5, "dernier"), w(5, "PSG")
    kw(cv, fr, K5a, t, .03, None, CX, 400, -3)
    td0 = w(5, "Dijon") - .1
    calendar(cv, fr, CX, 900, "2019", 1.6*pop_in(t, .05, .3), -4, 1 - prog(t, td0, .25), top="1er NOV.")
    a = pop_in(t, td0, .3)
    DJ.draw(cv, fr, 280, 1760, .55*a, age=1, kit="dijon", mood="determined", t=t)
    RK_D.draw(cv, fr, 280, 1300, pop_in(t, td - .05), -6)
    b = pop_in(t, tp - .15, .3)
    PSGP.draw(cv, fr, 760, 1840, 1.3*b, age=1, kit="psg", mood="happy", arms=(30, 30), t=t)
    RK_P.draw(cv, fr, 800, 640, pop_in(t, w(5, "leader") - .05), 5)

def s5b(cv, fr, t):
    stadium(cv, fr, "djs5stad", t, horizon=1060)
    tm = w(5, "Mbappé"); tg = tm + .8
    draw_goal(cv, fr, 760, 1290, 400, 240, prog(t, tg, .5), 1, t)
    x = lerp(240, 470, ease_out_cubic(prog(t, tm - .1, .6)))
    MBAP.draw(cv, fr, x, 1760, 1.0, age=1, kit="psg", mood="cheer" if t > tg else "determined", t=t,
              legs=(0, 50*math.sin(prog(t, tg - .3, .3)*math.pi)), arms=(150, 150) if t > tg + .1 else (20, 20))
    if t < tg + .05:
        u = prog(t, tg - .3, .35); p = bezier((x + 60, 1730), (620, 1300), (760, 1200), u); draw_ball(cv, fr, p[0], p[1], .55, t*800)
    score2(cv, fr, CX, 640, "DIJON", "PSG", 0, 1 if t > tg else 0, "", .6)
    kw(cv, fr, K5b, t, tm - .05, None, CX, 400, -3)

def s5c(cv, fr, t):
    stadium(cv, fr, "djs5c", t, horizon=1060)
    tg = w(5, "gagne"); t2 = w(5, "deux", 2); tb = w(5, "dernier", 2)
    goals = 1 + (1 if t > t2 else 0)
    score2(cv, fr, CX, 640, "DIJON", "PSG", goals, 1, "", .6*(1 + .15*pop_in(t, t2, .2)*(1 - prog(t, t2 + .2, .2))))
    if t > t2:
        rays(cv, (CX, 1000), t, prog(t, t2, .3)*.8, 16, 1400, (250, 200, 120))
        kw(cv, fr, K5c, t, t2, tb - .15, CX, 960, -4)
        confetti(cv, fr, "djc5", t - t2, 100, 4, [ROUGE, BLANC, MOUT])
    for P, x, k in ((DJ2, 240, 0), (DJ, 520, 1)):
        hop = 70*abs(math.sin(t*6 + k)) if t > t2 else 0
        P.draw(cv, fr, x, 1760 - hop, .9, age=1, kit="dijon", mood="cheer" if t > tg else "determined", arms=(150, 150) if t > tg else (20, 20), t=t)
    MBAP.draw(cv, fr, 860, 1760, .9, age=1, kit="psg", mood="sad" if t > t2 else "surprised", t=t, look=(0, 1))
    show_stamp(cv, fr, K5d, t, tb - .1, CX, 960, -4)
    camera_flashes(cv, fr, "djcf5", t - t2, 1.4, 12)

def s5(cv, fr, t, T):
    shots(cv, fr, t, [(0, s5a), (w(5, "Mbappé") - .1, s5b), (w(5, "mais") - .1, s5c)], d=.24)
    impact(cv, t, w(5, "PSG"), 14); impact(cv, t, w(5, "Mbappé") + .8, 16); impact(cv, t, w(5, "deux", 2), 24)
    flashes(cv, t, w(5, "deux", 2), .12, .7); punch(cv, t, w(5, "dernier", 2) - .1, 1.08); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 6 — PAUSE : quel club après ?
def s6(cv, fr, t, T):
    stage_fill(cv, fr, MOUT, "djs6"); d = ImageDraw.Draw(cv)
    kw(cv, fr, K6a, t, .05, None, 760, 300, 4)
    tq = w(6, "Quel")
    kw(cv, fr, K6b, t, tq - .05, None, 760, 560, -3)
    tpch = w(6, "prochain")
    for i in range(4):
        a = pop_in(t, tq + .2 + i*.1)
        if a <= 0: continue
        x = 180 + i*240; y = 1010 + 10*math.sin(t*4 + i)
        CARD.draw(cv, fr, x, y, a, (-4, 3, -2, 5)[i])
        LBL("?", "djqmS", font("title", 120), (60, 56, 64), None).draw(cv, fr, x, y - 30, a)
        NAMES6[i].draw(cv, fr, x, y + 80, a)
    te = w(6, "Dis-le")
    if t > te - .2:
        a = pop_in(t, te - .2)
        speech_bubble(cv, fr, "djcta_b", typewriter("Fais Auxerre stp !!", prog(t, te, .6)) or " ", 500, 1300, a, (-1, 1), 60)
        bx = 880 + 18*math.sin(t*8)
        arrow(d, (740, 1320), (bx + 80, 1200), prog(t, te, .3), PAL["ink"], 10, 7, 34, -.2)
    kw(cv, fr, K6c, t, w(6, "commentaire"), None, 540, 1470, 2)
    kw(cv, fr, K6d, t, w(6, "allez"), None, 760, 780, -5)
    impact(cv, t, w(6, "allez"), 14)

def s6_post(cv, fr, t, T):
    a = pop_in(t, .25)
    if a > 0:
        d = ImageDraw.Draw(cv); cx, cy, s = 250, 470, a
        d.ellipse([cx-70*s, cy-70*s, cx+70*s, cy+70*s], fill=(34, 32, 36))
        for dx in (-22, 22): d.rectangle([cx+dx*s-12*s, cy-34*s, cx+dx*s+12*s, cy+34*s], fill=(250, 248, 240))
    chrono_bar(cv, fr)

# ------------------------------------------------------------------ SCÈNE 7 — 2021 : dernier, 15 matchs sans gagner… National
def s7a(cv, fr, t):
    stage_fill(cv, fr, (60, 64, 76), "djs7a"); rain(cv, t)
    tq = w(7, "quinze")
    kw(cv, fr, K7a, t, w(7, "vingt") - .1, None, CX, 400, -3)
    show_stamp(cv, fr, K7b, t, w(7, "dernier") - .05, CX, 600, -5)
    d = ImageDraw.Draw(cv)
    for k in range(15):
        a = pop_in(t, tq - .05 + k*.06, .2)
        if a <= 0: continue
        x = 190 + (k % 5)*175; y = 820 + (k // 5)*150; r = 56*a
        d.rectangle([x - r, y - r, x + r, y + r], fill=PAL["paper"], outline=PAL["ink"], width=5)
        pencil_cross(d, x, y, 1.6*a)
    kw(cv, fr, K7c, t, w(7, "matchs") - .05, None, CX, 1300, 3)
    tch = w(7, "chute")
    if t < tch - .05: DJ.draw(cv, fr, CX, 1840, .7, age=1, kit="dijon", mood="surprised", t=t)
    else:
        u = ease_out_cubic(prog(t, tch - .05, .35)); ang = -88*u; h2 = 220   # bascule autour du centre du corps
        L = DJ.render_layer(fr, .7, age=1, kit="dijon", mood="sad")
        blit(cv, L, CX + h2*math.sin(math.radians(ang)) + h2*0, 1840 - h2 + h2*math.cos(math.radians(ang)), 1, ang)
    grayscale(cv, .35)

def s7b(cv, fr, t):
    te = w(7, "relégué") - .2; td = w(7, "National")
    stage_fill(cv, fr, (90, 96, 110), "djs7b"); rain(cv, t, 40)
    DJ.draw(cv, fr, CX, 1740, 1.05, age=1, kit="dijon", mood="surprised", t=t)
    floor_panel(cv, fr, CX, 660, "L2", t, True, 1.6, 1)
    elevator_drop(cv, t, te, td - te)
    if t > td:
        shaft(cv, fr, t, 0, "djs7shaft")
        DJ.draw(cv, fr, CX, 1740, 1.05, age=1, kit="dijon", mood="sad", t=t, look=(0, 1), tears=t - td)
        floor_panel(cv, fr, CX, 660, "NAT", t, True, 1.8, 1)
        show_stamp(cv, fr, K7d, t, td, CX, 960, -5)
        show(cv, fr, T7a, t, td + .3, None, CX, 1120, 2)
        grayscale(cv, .6)

def s7(cv, fr, t, T):
    shots(cv, fr, t, [(0, s7a), (w(7, "Et", 2) - .1, s7b)], d=.24)
    impact(cv, t, w(7, "chute"), 18); glitch(cv, fr, t, w(7, "chute"), .3, 14); impact(cv, t, w(7, "National") + .02, 24); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 8 — Tavares rappelé, champion du National, retour en Ligue 2
def s8a(cv, fr, t):
    stage_fill(cv, fr, (40, 46, 60), "djs8a")
    tr, tj = w(8, "rappelle"), w(8, "Julio")
    if t < tj - .1:
        sh = 10*math.sin(t*60) if t > tr - .1 else 0
        PHONE.draw(cv, fr, CX + sh, 1000, 1.5*pop_in(t, .05, .3), 6*math.sin(t*40) if sh else 0)
        if t > tr - .1:
            d = ImageDraw.Draw(cv)
            for k in range(3):
                r = 160 + 70*k + 40*((t*3) % 1); d.arc([CX - r, 1000 - r, CX + r, 1000 + r], -50, 50, fill=MOUT, width=8); d.arc([CX - r, 1000 - r, CX + r, 1000 + r], 130, 230, fill=MOUT, width=8)
        show(cv, fr, T8x, t, tr - .1, None, CX, 450, -2)
    else:
        rays(cv, (CX, 1000), t, prog(t, tj - .1, .3), 16, 1500, (90, 80, 60))
        TAVA.draw(cv, fr, CX, 1760, 1.1*slam(t, tj - .1, .25), age=1, kit="dijon", beard=True, mood="cheer", arms=(150, 150), t=t)
        show_stamp(cv, fr, N8, t, tj - .05, CX, 420, -4)
        show(cv, fr, T8a, t, w(8, "meilleur") - .1, None, CX, 600, 3)

def s8b(cv, fr, t):
    stage_fill(cv, fr, ROUGE, "djs8b"); rays(cv, (CX, 1000), t, 1.0, 16, 1500, (250, 120, 120))
    tc = w(8, "champion")
    trophy_lift(cv, fr, TAVA, CX, 1780, .85, "dijon", t)
    kw(cv, fr, K8a, t, w(8, "vingt-six") - .15, None, CX, 400, -3)
    show_stamp(cv, fr, K8b, t, tc - .05, CX, 600, 4)
    show(cv, fr, T8b, t, tc + .5, None, CX, 760, -2)
    confetti(cv, fr, "djc8", t - tc, 100, 4, [BLANC, MOUT])

def s8c(cv, fr, t):
    t0 = w(8, "Retour") - .1
    shaft(cv, fr, t, 2400)
    u = prog(t, t0 + .1, .5)
    floor_panel(cv, fr, CX, 640, "NAT" if u < 1 else "L2", t, False, 1.8, 1)
    DJ.draw(cv, fr, CX, 1760, 1.05, age=1, kit="dijon", mood="cheer", arms=(160, 160), legs=(12, 12), t=t)
    kw(cv, fr, K8c, t, t0 + .1, None, CX, 960, -3)

def s8(cv, fr, t, T):
    shots(cv, fr, t, [(0, s8a), (w(8, "Et") - .1, s8b), (w(8, "Retour") - .1, s8c)], d=.24)
    impact(cv, t, w(8, "Julio"), 16); impact(cv, t, w(8, "champion"), 18); flashes(cv, t, w(8, "champion"), .12, .6); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 9 — prochaine étape : la Ligue 1 ?
def s9(cv, fr, t, T):
    sx0, sy0, sx1, sy1 = STAGE
    stage_fill(cv, fr, BLANC, "djs9"); d = ImageDraw.Draw(cv)
    d.polygon([(sx0, sy0), (CX + 60, sy0), (CX - 60, sy1), (sx0, sy1)], fill=ROUGE)
    tl, tc, tab, tcl = w(9, "Ligue"), w(9, "commentaire"), w(9, "abonne-toi"), w(9, "club")
    kw(cv, fr, K9a, t, .03, None, CX, 400, -3)
    floor_panel(cv, fr, 270, 640, "L2", t, False, 1.1, 1)
    floor_panel(cv, fr, 740, 640, "L1?", t, False, 1.1, pop_in(t, tl - .1, .3))
    if t > tl: arrow(d, (450, 640), (560, 640), prog(t, tl, .25), PAL["ink"], 12, 3, 40, -.3)
    BTN_O.draw(cv, fr, 300, 880, pop_in(t, tl + .2)*(1 + .05*math.sin(t*8)), -5)
    BTN_N.draw(cv, fr, 780, 880, pop_in(t, tl + .35)*(1 + .05*math.sin(t*8 + 1)), 5)
    if t > tc: arrow(d, (640, 1060), (960, 1180), prog(t, tc, .3), PAL["ink"], 12, 12, 40, .2)
    if t > tab:
        press = 1 - .12*math.sin(prog(t, tab + .5, .25)*math.pi)
        BTN_SUB.draw(cv, fr, CX, 1120, pop_in(t, tab)*press, -2)
        confetti(cv, fr, "djc9", t - tab, 80, 5, [ROUGE, BLANC, MOUT])
    kw(cv, fr, K9b, t, tcl - .1, None, CX, 1270, 3)
    JAR.draw(cv, fr, 900, 1640, .55, 10)
    DJ.draw(cv, fr, 300, 1840, .7, age=1, kit="dijon", mood="cheer" if t > tab else "happy",
            arms=(150, 150) if t > tab else ((150, 20) if int(t*2) % 2 else (20, 150)), t=t)
    impact(cv, t, tl, 12); impact(cv, t, tab, 12); drift(cv, t, T, .05)

# ------------------------------------------------------------------ scènes + bruitages
def with_bar(fn):
    def g(cv, fr, t, T):
        fn(cv, fr, t, T); chrono_bar(cv, fr)
    return g
def SC(name, n, fn, sfx, trans=None, trans_dur=.25, pad_out=.25):
    return Scene(name, TEXTS[n-1], with_bar(fn), sfx, pad_in=PAD, pad_out=pad_out, trans=trans, trans_dur=trans_dur)
W_ = w
SCENES = [
    SC("moutarde", 1, s1, [(.0, "boom", .9), (.0, "stamp", .8), (.05, "riser", .4), (W_(1, "moutarde"), "pop"), (W_(1, "moutarde") + .05, "poof", .7),
                           (W_(1, "monde"), "sparkle", .6), (W_(1, "mais") - .1, "whoosh", .5), (W_(1, "battu"), "crowd", .9), (W_(1, "battu"), "stamp", .6),
                           (W_(1, "PSG"), "gasp", .6), (W_(1, "puis") - .1, "whoosh", .5), (W_(1, "tombé") - .1, "elevator", .9), (W_(1, "division"), "boom", .7),
                           (W_(1, "L'histoire") - .1, "whoosh_up", .6), (W_(1, "L'histoire"), "stamp", .7), (W_(1, "minute") - .1, "tick", .9)]),
    SC("1998", 2, s2, [(.0, "boom", .5), (W_(2, "DFCO"), "stamp", .6), (W_(2, "mille"), "stamp", .6), (W_(2, "rouge") - .15, "swish"),
                       (W_(2, "rouge"), "pop"), (W_(2, "blanc"), "pop2"), (W_(2, "Son") - .1, "whoosh", .5), (W_(2, "stade") - .1, "stamp", .7),
                       (W_(2, "maire") - .2, "pop"), (W_(2, "qui") - .1, "whoosh", .5), (W_(2, "recette") - .1, "whoosh_up", .7), (W_(2, "recette"), "sparkle", .6),
                       (W_(2, "poulet"), "cluck"), (W_(2, "poulet") + .3, "laugh", .5)], trans="punch", trans_dur=.3),
    SC("garcia", 3, s3, [(.1, "whoosh_up", .4), (W_(3, "deux") - .05, "stamp", .6), (W_(3, "Rudi"), "stamp"), (W_(3, "Rudi") + .5, "pop"),
                         (W_(3, "Deux", 3) - .1, "whoosh", .5), (W_(3, "troisième") - .1, "pop2"), (W_(3, "Dijon") - .1, "boom", .6),
                         (W_(3, "demi-finale"), "crowd", .8), (W_(3, "demi-finale"), "stamp", .6), (W_(3, "Coupe"), "pop"),
                         (W_(3, "et") - .1, "whoosh_up", .7), (W_(3, "Ligue"), "stamp"), (W_(3, "Ligue"), "crowd_long", .8)], trans="whip"),
    SC("ligue1", 4, s4, [(.0, "boom", .6), (.03, "stamp", .6), (W_(4, "Ligue"), "stamp"), (W_(4, "Ligue"), "crowd_long", .9), (W_(4, "histoire"), "pop"),
                         (W_(4, "Elle") - .1, "whoosh", .5), (W_(4, "Elle") + .15, "elevator", .8), (W_(4, "an") + .1, "boom", .6),
                         (W_(4, "mais") - .1, "whoosh", .5), (W_(4, "seize"), "stamp", .6), (W_(4, "revient"), "pop"),
                         (W_(4, "s'accroche") - .05, "thud", .8), (W_(4, "s'accroche"), "stamp", .7)], trans="tear_h", trans_dur=.5),
    SC("psg", 5, s5, [(.03, "stamp", .6), (W_(5, "Dijon") - .1, "pop"), (W_(5, "dernier"), "pop2"), (W_(5, "PSG") - .15, "boom", .7),
                      (W_(5, "leader"), "stamp", .5), (W_(5, "Mbappé") - .1, "whoosh", .5), (W_(5, "Mbappé") + .5, "kick"),
                      (W_(5, "Mbappé") + .8, "crowd", .7), (W_(5, "mais") - .1, "whoosh", .5), (W_(5, "gagne"), "kick", .7),
                      (W_(5, "deux", 2), "crowd_long", 1.0), (W_(5, "deux", 2), "boom"), (W_(5, "dernier", 2) - .1, "stamp")], trans="whip"),
    SC("pause", 6, s6, [(0, "scratch", 1.0, .9), (.3, "pop"), (W_(6, "Quel"), "stamp", .6)] + [(W_(6, "Quel") + .2 + i*.1, "notif", .6) for i in range(4)] +
                       [(W_(6, "Dis-le") - .2, "notif"), (W_(6, "Dis-le"), "scribble", .5), (W_(6, "commentaire"), "pop2"),
                        (W_(6, "allez"), "whoosh"), (W_(6, "allez"), "boom", .5)], trans="polaroid", pad_out=.3),
    SC("chute", 7, s7, [(.0, "boom", .6), (W_(7, "vingt") - .1, "stamp", .6), (W_(7, "chute"), "glitch", .7, .35), (W_(7, "chute"), "thud", .9), (W_(7, "dernier"), "stamp"),
                        (W_(7, "dernier") + .1, "groan", .6)] + [(W_(7, "quinze") - .05 + k*.06, "pop", .4) for k in range(0, 15, 2)] +
                       [(W_(7, "matchs"), "stamp", .5), (W_(7, "Et", 2) - .1, "whoosh", .5), (W_(7, "relégué") - .2, "elevator", .9),
                        (W_(7, "National"), "boom", .8)], trans="tear_d", trans_dur=.5),
    SC("remontee", 8, s8, [(.05, "phone", .7, 1.6), (W_(8, "rappelle") - .1, "phone", .6, 1.2), (W_(8, "Julio") - .1, "boom", .7),
                           (W_(8, "Julio"), "crowd", .8), (W_(8, "Julio"), "stamp", .6), (W_(8, "meilleur"), "pop"), (W_(8, "Et") - .1, "whoosh", .5),
                           (W_(8, "vingt-six") - .15, "stamp", .6), (W_(8, "champion"), "stamp"), (W_(8, "champion"), "crowd_long", 1.0),
                           (W_(8, "champion"), "sparkle"), (W_(8, "Retour") - .1, "whoosh_up", .8), (W_(8, "Retour"), "ding", .7)], trans="whip"),
    SC("fin", 9, s9, [(.0, "boom", .6), (.03, "stamp", .6), (W_(9, "Ligue") - .1, "pop"), (W_(9, "Ligue") + .2, "pop2"), (W_(9, "Ligue") + .35, "pop"),
                      (W_(9, "commentaire"), "notif"), (W_(9, "abonne-toi"), "pop2"), (W_(9, "abonne-toi") + .5, "notif"),
                      (W_(9, "abonne-toi") + .1, "crowd", .7), (W_(9, "club") - .1, "stamp", .6)], trans="punch", trans_dur=.3, pad_out=1.2),
]
SCENES[5].trans_dur = 99      # la photo figée reste épinglée pendant toute la pause
SCENES[5].post = s6_post

# ------------------------------------------------------------------ couverture
def cover(path):
    cv = background(0, TITLE); stage_fill(cv, 0, MOUT, "djcov"); d = ImageDraw.Draw(cv)
    rays(cv, (CX, 1150), 0.3, 1.0, 16, 1500, (250, 214, 90))
    DIJON.draw(cv, 0, CX, 330, 1.05, -3)
    Label("A BATTU LE PSG…", "djcv1", font("title", 100), PAL["ink"], BLANC, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 560, 1, 2)
    Label("PUIS LA 3e DIVISION ?!", "djcv2", font("title", 92), BLANC, NAVY, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 720, 1, -2)
    JAR.draw(cv, 0, 800, 1250, 1.05, 8)
    splat(cv, 900, 1460, 60, 0, 7)
    DJ.draw(cv, 0, 370, 1640, 1.1, age=1, kit="dijon", mood="cheer", arms=(150, 150), legs=(14, 14), t=1)
    Label("L'HISTOIRE DU DFCO EN 1 MINUTE", "djcv3", font("title", 56), PAL["cream"], ROUGE, maxw=1040, padx=30, pady=12).draw(cv, 0, CX, 1690, 1, 1)
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
        p = os.path.join(out, f"dj_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", "dijon")
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/dijon_stills"), only=only)); sys.exit()
    if os.environ.get("LEGENDES_PROVISOIRE") and "--apercu" not in args:
        sys.exit("Minutage provisoire : pas de rendu final sans les vraies voix (--apercu pour un aperçu muet).")
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25))
