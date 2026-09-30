"""Épisode « Légendes du foot » #5 : Neymar Jr.
Accroche en devinette par les âges (4 mois : accident / 25 ans : 222 M€ / 34 ans : en larmes), révélation samba,
futsal, essai au Real, crête de Santos, trio du Barça, la remontada minute par minute, pause « prochain joueur ? »,
clause de 222 M€ déchirée, les 14 minutes au sol, or olympique et record de Pelé, Arabie saoudite, retour à Santos,
élimination au Mondial 2026 et flashback en vieux film sur son 1er but en 2010 dans le même stade, fin « génie ou gâchis ? ».

  python3 episodes/neymar/neymar.py output/neymar --stills [3,4]
  python3 episodes/neymar/neymar.py output/neymar --cover
  python3 episodes/neymar/neymar.py output/neymar
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from story import *
import engine

TITLE = "~/légendes $ ./neymar_jr"
SLUG = "neymar_legende"
VOICE = [os.path.join(HERE, "voix", f"scene_{i}.mp3") for i in range(1, 14)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
ALIGN = os.path.join(HERE, "alignement.json")
PAD = 0.15
WS, TEXTS = load_words(ALIGN)
def w(i, word, n=1, end=False):
    """Temps local (dans la scène i) où la voix prononce `word`."""
    return PAD + WS[i-1](word, n, end)

JAUNE = (252, 214, 30); VERT = (0, 150, 72); BLEU_BR = (24, 70, 160); NAVY = (16, 40, 86); GOLD = (236, 186, 48)
ROUGE = (206, 32, 44); BLANC = (250, 250, 246); GRIS = (120, 120, 126)

NEY = Player("ney", hair=(48, 34, 26), skin=(196, 146, 108), hair_style="quiff")
NEY_S = Player("neys", hair=(40, 28, 22), skin=(196, 146, 108), hair_style="mohawk")
MESSI = Player("messin", hair=(110, 72, 44), beard_col=(100, 66, 40), skin=(230, 186, 150))
SUAREZ = Player("suarez", hair=(36, 28, 24), beard_col=(40, 30, 26), skin=(222, 176, 140))
SERGI = Player("sergi", hair=(52, 38, 30), skin=(232, 188, 152))
DEF = [Player("def_a", hair=(60, 44, 34), skin=(230, 186, 150)), Player("def_b", hair=(24, 20, 18), skin=(120, 82, 60))]
KIDS = [Player("kid_a", hair=(70, 50, 36), skin=(210, 160, 120)), Player("kid_b", hair=(30, 26, 22), skin=(150, 104, 76))]
GK = Player("gk_n", hair=(200, 170, 110), skin=(236, 196, 166))

# ------------------------------------------------------------------ objets
QM = Label("?", "nyqm", font("title", 280), PAL["mustard"], None, stroke=7, stroke_fill=PAL["ink"])
def _car_decor(d, a):
    ax, ay = a
    d.polygon([(ax-70, ay-98), (ax+64, ay-100), (ax+124, ay-46), (ax-114, ay-42)], fill=(170, 210, 230))
    d.line([(ax-4, ay-100), (ax-4, ay+40)], fill=(30, 50, 90), width=6)
CAR = Paper(poly_pts([(-240, 46), (-246, -4), (-222, -32), (-130, -44), (-78, -110), (70, -114), (150, -50), (236, -30), (248, 46)]),
            (60, 110, 180), "nycar", rough=1.6, hatch=True, pad=40).add(_car_decor)
def draw_car(cv, fr, x, y, s=1.0, rot=0.0, t=0.0):
    CAR.draw(cv, fr, x, y, s, rot); d = ImageDraw.Draw(cv); a = math.radians(-rot)
    for wx in (-150, 150):
        cx = x + wx*s*math.cos(a) - 52*s*math.sin(a); cy = y + wx*s*math.sin(a) + 52*s*math.cos(a); r = 46*s
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(34, 32, 36)); d.ellipse([cx-r*.45, cy-r*.45, cx+r*.45, cy+r*.45], fill=(190, 190, 196))
def bandaid(cv, x, y, s=1.0, rot=-20):
    L = layer(int(160*s), int(80*s), (80*s, 40*s)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([6*s, 20*s, 154*s, 60*s], int(18*s), fill=(236, 196, 150), outline=(190, 150, 110), width=max(1, int(2*s)))
    d.rectangle([60*s, 22*s, 100*s, 58*s], fill=(250, 226, 196))
    for k in range(4): d.ellipse([66*s + k*9*s, 36*s, 70*s + k*9*s, 40*s], fill=(200, 160, 120))
    blit(cv, L, x, y, 1, rot)
def _house_decor(col):
    def dec(d, a):
        ax, ay = a
        d.rectangle([ax-22, ay-10, ax+22, ay+22], fill=(80, 110, 140)); d.rectangle([ax-60, ay-58, ax+60, ay-46], fill=tuple(int(c*.7) for c in col))
    return dec
HOUSES = [Paper(rect_pts(120, 100), col, f"nyhouse{i}", rough=1.6, hatch=True).add(_house_decor(col))
          for i, col in enumerate(((236, 120, 90), (250, 206, 90), (110, 190, 170), (230, 150, 190), (150, 170, 230), (240, 170, 90)))]
PLANE = Paper(poly_pts([(-220, 0), (-160, -26), (120, -30), (200, -8), (220, 8), (120, 26), (-160, 22)]), (236, 238, 242), "nyplane", rough=1.4, pad=90).add(
    lambda d, a: [d.polygon([(a[0]-30, a[1]), (a[0]+50, a[1]), (a[0]-60, a[1]+110)], fill=(200, 204, 214)),
                  d.polygon([(a[0]-150, a[1]-20), (a[0]-120, a[1]-20), (a[0]-190, a[1]-90)], fill=(200, 204, 214)),
                  [d.ellipse([a[0]-100+k*44, a[1]-14, a[0]-86+k*44, a[1]], fill=(90, 130, 170)) for k in range(6)]])
def _eiffel(d, a):
    ax, ay = a; c = (60, 64, 90)
    d.polygon([(ax-150, ay+300), (ax-40, ay-40), (ax-18, ay-300), (ax+18, ay-300), (ax+40, ay-40), (ax+150, ay+300), (ax+90, ay+300),
               (ax+10, ay+60), (ax-10, ay+60), (ax-90, ay+300)], fill=c)
    d.rectangle([ax-70, ay+40, ax+70, ay+60], fill=c); d.rectangle([ax-44, ay-60, ax+44, ay-44], fill=c)
EIFFEL = Paper(rect_pts(20, 20), (34, 50, 96), "nyeiffel", rough=1, pad=320, shadow=False).add(_eiffel)
def medal(cv, fr, x, y, s=1.0, a=1.0):
    if a <= .01: return
    d = ImageDraw.Draw(cv); s *= a
    d.polygon([(x-60*s, y-260*s), (x-10*s, y-260*s), (x+20*s, y-60*s), (x-20*s, y-60*s)], fill=VERT)
    d.polygon([(x+60*s, y-260*s), (x+10*s, y-260*s), (x-20*s, y-60*s), (x+20*s, y-60*s)], fill=JAUNE)
    d.ellipse([x-95*s, y-95*s, x+95*s, y+95*s], fill=(200, 146, 30)); d.ellipse([x-80*s, y-80*s, x+80*s, y+80*s], fill=GOLD)
    d.polygon(star_shape(x, y, 50*s, 5, .45, -math.pi/2), fill=(255, 236, 150))
def stopwatch(cv, x, y, s, u):
    d = ImageDraw.Draw(cv)
    d.rectangle([x-18*s, y-150*s, x+18*s, y-118*s], fill=(80, 80, 88)); d.ellipse([x-120*s, y-120*s, x+120*s, y+120*s], fill=(80, 80, 88))
    d.ellipse([x-104*s, y-104*s, x+104*s, y+104*s], fill=(250, 250, 246))
    for k in range(12):
        an = k*math.pi/6; d.line([(x+88*s*math.sin(an), y-88*s*math.cos(an)), (x+100*s*math.sin(an), y-100*s*math.cos(an))], fill=PAL["ink"], width=max(2, int(5*s)))
    an = u*math.pi*2*3; d.line([(x, y), (x+80*s*math.sin(an), y-80*s*math.cos(an))], fill=ROUGE, width=max(3, int(8*s)))
    d.ellipse([x-10*s, y-10*s, x+10*s, y+10*s], fill=PAL["ink"])
def _doc_decor(d, a):
    ax, ay = a
    d.text((ax, ay-190), "CLAUSE", font=font("title", 60), fill=PAL["ink"], anchor="mm")
    d.text((ax, ay-110), "222 000 000 €", font=font("title", 44), fill=ROUGE, anchor="mm")
    for k in range(6): d.line([(ax-150, ay-40+k*40), (ax+(150 if k % 3 else 80), ay-40+k*40)], fill=(170, 164, 150), width=5)
DOC = Paper(rect_pts(400, 500), (250, 248, 238), "nydoc", rough=1.6).add(_doc_decor)
_torn = {}
def torn_doc():
    if "ab" not in _torn:
        spr = DOC.v[0]; A, B, _ = tear_split(spr, "v", 11, rough=18)
        for P in (A, B): P.info["anchor"] = spr.info["anchor"]
        _torn["ab"] = (A, B)
    return _torn["ab"]
BILL = Paper(rect_pts(160, 80), (70, 150, 120), "nybill", rough=1.4, hatch=True).add(
    lambda d, a: [d.rectangle([a[0]-70, a[1]-34, a[0]+70, a[1]+34], outline=PAL["cream"], width=3), d.text((a[0], a[1]), "€", font=font("title", 50), fill=PAL["cream"], anchor="mm")])
def bill_rain(cv, fr, t, t0, dur=3.0, n=16, key="nybills"):
    if t < t0: return
    rnd = random.Random(key)
    for i in range(n):
        tt = t - t0 - rnd.uniform(0, dur*.5)
        if tt < 0: continue
        x = rnd.uniform(90, 990) + 50*math.sin(tt*2+i); y = 150 + tt*rnd.uniform(420, 640)
        if y < 1950: BILL.draw(cv, fr, x, y, rnd.uniform(.8, 1.1), 30*math.sin(tt*3+i))
DUNE = Paper(ellipse_pts(1400, 420, 60), (214, 172, 110), "nydune", rough=4, hatch=True)
SUN = Paper(ellipse_pts(220, 220, 40), PAL["mustard"], "nysun", rough=2)
LIBCUP = Paper(poly_pts([(-60, -150), (60, -150), (50, -40), (20, 10), (16, 90), (60, 110), (60, 150), (-60, 150), (-60, 110), (-16, 90), (-20, 10), (-50, -40)]),
               (206, 212, 222), "nylib", rough=1.6, hatch=True, pad=60).add(
    lambda d, a: [d.ellipse([a[0]-24, a[1]-210, a[0]+24, a[1]-160], fill=(206, 212, 222)), d.rectangle([a[0]-58, a[1]+112, a[0]+58, a[1]+130], fill=(60, 56, 52))])
SCOREBOARD = scoreboard_sprite(820, 330, "nyscore")
CARD = Paper(rect_pts(200, 250), PAL["paper"], "nycard", rough=2)

JBN = jersey_back("brazil", "NEYMAR JR", 10, key="jbney10")
def ney_back(cv, fr, x, y, s=1.0, bob=0.0):
    """Neymar vu de dos (tireur de penalty)."""
    JBN.draw(cv, fr, x, y + bob, s)
    hx, hy = x, y + bob - 236*s - 70*s
    NEY.neck.draw(cv, fr, hx, hy + 60*s, s*1.3); NEY.head.draw(cv, fr, hx, hy, s*1.35)
    ImageDraw.Draw(cv).chord([hx - 72*s, hy - 90*s, hx + 72*s, hy + 70*s], 180, 360, fill=NEY.hair_col)

def score2(cv, fr, x, y, la, lb, a, b, sub="", s=1.0):
    if s <= .02: return
    L = layer(900, 420, (450, 210)); SCOREBOARD.draw(L, fr, 450, 210, 1, 0, 1)
    d = ImageDraw.Draw(L)
    for x_, lab in ((180, la), (720, lb)): d.text((x_, 130), lab, font=font("mono", 64 if len(lab) <= 5 else 44), fill=(200, 196, 190), anchor="mm")
    d.text((450, 220), f"{a} - {b}", font=font("title", 150), fill=(255, 204, 70), anchor="mm")
    if sub: d.text((450, 330), sub, font=font("mono", 38), fill=(170, 166, 160), anchor="mm")
    blit(cv, L, x, y, s)

def walk(t, speed=9, amp=22):
    ph = math.sin(t*speed); return (amp*ph, -amp*ph), abs(math.sin(t*speed))*8

def stadium(cv, fr, key, t=0.0, sky=(18, 22, 46), grass=(46, 112, 64), horizon=1060, pal=None):
    stage_fill(cv, fr, sky, key); d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    rnd = random.Random(key)
    pal = pal or [(90, 96, 120), (130, 120, 110), (200, 196, 190), (60, 64, 90), (160, 60, 60), (70, 90, 150)]
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
    if int(t*24) % 7 == 0:
        x, y = rnd.uniform(80, 1000), rnd.uniform(540, 980); d.ellipse([x-9, y-9, x+9, y+9], fill=(255, 255, 250))

def spin(cv, fr, pl, x, y, s, t, t0, kit_a, kit_b, dur=.45, **kw):
    """Tour sur lui-même avec changement de maillot à mi-course ; sinon dessin normal."""
    su = prog(t, t0, dur)
    if 0 < su < 1:
        L = pl.render_layer(fr, s, age=kw.get("age", 1), kit=kit_a if su < .25 else kit_b, mood=kw.get("mood", "happy"))
        blit_sxy(cv, L, x, y, max(.04, abs(math.cos(su*math.pi*2))), 1)
    else:
        pl.draw(cv, fr, x, y, s, kit=kit_b if su >= 1 else kit_a, t=t, **{k: v for k, v in kw.items()})

def trophy_lift(cv, fr, pl, x, y, s, kit, t, trophy=UCL, mood="cheer", age=1):
    pl.draw(cv, fr, x, y, s, age=age, kit=kit, mood=mood, arms=(160, 160), legs=(12, 12), t=t)
    trophy.draw(cv, fr, x, y - 850*s + 8*math.sin(t*6), .9*s, 3*math.sin(t*4))

def br_flag(cv, x, y, w=300, h=200, t=0.0, a=1.0, rot=0.0):
    """Drapeau vert-jaune stylisé (losange jaune, disque bleu) qui ondule."""
    if a <= .01: return
    L = layer(int(w+40), int(h+60), (w/2+20, h/2+30)); d = ImageDraw.Draw(L)
    n = 24
    for k in range(n):
        off = 10*math.sin(k/n*math.pi*2 - t*5)*(k/n)
        d.rectangle([20 + k*w/n, 30+off, 20 + (k+1)*w/n + 1, 30+h+off], fill=VERT)
    cx, cy = 20 + w/2, 30 + h/2
    d.polygon([(cx - w*.42, cy), (cx, cy - h*.4), (cx + w*.42, cy), (cx, cy + h*.4)], fill=JAUNE)
    d.ellipse([cx - h*.24, cy - h*.24, cx + h*.24, cy + h*.24], fill=BLEU_BR)
    blit(cv, L, x, y, a, rot, 1)

# ------------------------------------------------------------------ labels
H1 = HL("QUI EST-CE ?", "nyh1", PAL["mustard"], PAL["ink"], 100)
AGE = [KW(txt, "nyage"+txt, bg, size=76) for txt, bg in (("À 4 MOIS", PAL["ink"]), ("À 25 ANS", PAL["ink"]), ("À 34 ANS", PAL["ink"]))]
T1a = TAG("accident de voiture", "nyt1a", PAL["paper"], size=44); T1b = TAG("en larmes", "nyt1b", PAL["paper"], size=48)
K1d = KW("TU L'AS RECONNU ?", "nyk1d", PAL["mustard"], PAL["ink"], 84)
N2 = STAMP("NEYMAR JR", "nyn2", VERT, 130); K2a = KW("1992", "nyk2a", PAL["ink"], size=150)
T2a = TAG("près de São Paulo", "nyt2a", PAL["paper"], size=52); T2b = TAG("famille modeste", "nyt2b", PAL["mustard"], size=52)
T2c = TAG("sous la banquette", "nyt2c", PAL["paper"], size=52); K2b = KW("UNE SIMPLE ÉGRATIGNURE", "nyk2b", PAL["mustard"], PAL["ink"], 72)
K3a = KW("FUTSAL", "nyk3a", ROUGE, size=130); K3b = KW("14 ANS", "nyk3b", PAL["ink"], size=130)
T3a = TAG("essai au Real Madrid", "nyt3a", PAL["paper"], size=54); K3c = STAMP("SANTOS LE GARDE !", "nyk3c", PAL["ink"], 92)
K4a = KW("17 ANS", "nyk4a", PAL["ink"], size=130); T4a = TAG("débuts pros avec Santos", "nyt4a", PAL["paper"], size=50)
K4b = KW("LA CRÊTE", "nyk4b", ROUGE, size=90); K4c = KW("GRIGRIS", "nyk4c", PAL["mustard"], PAL["ink"], 120)
K4d = STAMP("LE BRÉSIL DEVIENT FOU", "nyk4d", VERT, 78); K4e = KW("COPA LIBERTADORES", "nyk4e", PAL["ink"], size=80)
T4b = TAG("2011", "nyt4b", PAL["mustard"], size=60)
K5a = KW("2013", "nyk5a", (0, 77, 152), size=150); K5b = KW("TRIO MONSTRUEUX", "nyk5b", (165, 0, 68), size=90)
MSN = [LBL(c, "nymsn"+c, font("title", 150), JAUNE, None, stroke=7, stroke_fill=PAL["ink"]) for c in "MSN"]
K5c = KW("FINALE 2015", "nyk5c", PAL["ink"], size=110); K5d = STAMP("IL MARQUE !", "nyk5d", (0, 77, 152), 110)
K6a = KW("2017", "nyk6a", PAL["ink"], size=150); K6b = STAMP("SON CHEF-D'ŒUVRE", "nyk6b", GOLD, 92)
T6a = TAG("match aller : PSG 4 - 0 Barça", "nyt6a", PAL["paper"], size=50); K6c = KW("IL FAUT 4 BUTS", "nyk6c", ROUGE, size=100)
K6d = KW("BUT !", "nyk6d", PAL["mustard"], PAL["ink"], 140); K6e = KW("6 - 1 !", "nyk6e", (165, 0, 68), size=200)
K6f = STAMP("REMONTADA", "nyk6f", (0, 77, 152), 130); T6b = TAG("Sergi Roberto", "nyt6b", PAL["paper"], size=50)
MIN = {m: LBL(m, "nymin"+m, font("title", 110), BLANC, ROUGE, padx=20, pady=4, rough=2) for m in ("88'", "91'", "95'")}
K7a = KW("ATTENDS !", "nyk7a", PAL["ink"], size=90); K7b = KW("LE PROCHAIN ?", "nyk7b", ROUGE, size=78)
NAMES = [LBL(n, f"nynm{n}", font("hand", 46), PAL["ink"], None) for n in ("Vini ?", "Pelé ?", "Kaká ?", "Dinho ?")]
K7c = KW("EN COMMENTAIRE", "nyk7c", PAL["ink"], size=84); K7d = KW("ON CONTINUE !", "nyk7d", PAL["ink"], size=84)
K8a = STAMP("CLAUSE PAYÉE", "nyk8a", ROUGE, 100); K8b = STAMP("RECORD DU MONDE", "nyk8b", GOLD, 96)
T8a = TAG("encore aujourd'hui, en 2026", "nyt8a", PAL["paper"], size=50); K8c = KW("AOÛT 2017", "nyk8c", PAL["ink"], size=110)
BLESS = [LBL(txt, "nybl"+txt, font("title", 58), BLANC, ROUGE, padx=20, pady=6, rough=2) for txt in ("CHEVILLE", "MÉTATARSE", "MÉTATARSE", "CUISSE")]
K9a = KW("BLESSÉ", "nyk9a", PAL["ink"], size=130); K9b = KW("PRÈS DE 14 MIN AU SOL", "nyk9b", PAL["mustard"], PAL["ink"], 72)
T9a = TAG("Mondial 2018", "nyt9a", PAL["paper"], size=54)
MEMES = [LBL(txt, "nymm"+txt, font("title", 70), PAL["ink"], BLANC, padx=18, pady=6, rough=2) for txt in ("MDR", "LOL", "#NeymarChallenge", "ptdr")]
K10a = KW("OR OLYMPIQUE", "nyk10a", GOLD, PAL["ink"], 100); T10a = TAG("Rio 2016, tir au but décisif", "nyt10a", PAL["paper"], size=48)
K10b = STAMP("DEVANT PELÉ !", "nyk10b", VERT, 110); T10b = TAG("sélection masculine", "nyt10b", PAL["paper"], size=46)
K11e = KW("2023", "nyk11e", PAL["ink"], size=150); K11f = KW("ARABIE SAOUDITE", "nyk11f", (0, 110, 60), size=90)
K11a = KW("CONTRAT COLOSSAL", "nyk11a", BLEU_BR, size=90); T11a = TAG("≈ 100 M€ par an selon la presse", "nyt11a", PAL["paper"], size=46)
K11b = STAMP("LIGAMENTS CROISÉS", "nyk11b", ROUGE, 86); K11c = KW("7 MATCHS", "nyk11c", PAL["ink"], size=130)
K11d = KW("RETOUR À SANTOS", "nyk11d", PAL["ink"], size=96); T11b = TAG("2025", "nyt11b", PAL["paper"], size=56)
K12a = KW("MONDIAL 2026", "nyk12a", VERT, size=110); T12a = TAG("8e de finale", "nyt12a", PAL["paper"], size=54)
K12b = STAMP("ÉLIMINÉ", "nyk12b", ROUGE, 130); K12c = KW("EN LARMES", "nyk12c", (60, 70, 100), size=100)
K12d = KW("10 AOÛT 2010", "nyk12d", (120, 90, 60), (250, 240, 214), 100); T12b = TAG("1er but avec le Brésil", "nyt12b", (240, 228, 200), size=50)
K12e = STAMP("MÊME STADE", "nyk12e", (120, 90, 60), 110, (250, 240, 214))
BTN_G = Label("GÉNIE", "nybg", font("title", 110), PAL["ink"], GOLD, padx=40, pady=10, rough=3)
BTN_Q = Label("GÂCHIS", "nybq", font("title", 110), BLANC, (90, 90, 96), padx=40, pady=10, rough=3)
BTN_SUB = Label("+ ABONNE-TOI", "nybsub", font("title", 96), (255, 255, 255), (230, 40, 80), padx=40, pady=14, rough=2.5)
K13a = KW("PROCHAINE LÉGENDE ?", "nyk13a", PAL["ink"], size=80)

# ------------------------------------------------------------------ SCÈNE 1 — devinette : 4 mois, 25 ans, 34 ans
_sil = {}
def ney_silhouette():
    if "s" not in _sil:
        L = NEY.render_layer(0, .95, age=1, kit="brazil", arms=(22, 22), legs=(8, 8))
        a = L.getchannel("A").point(lambda v: 255 if v > 70 else 0)
        S = Image.new("RGBA", L.size, (18, 16, 22, 0)); S.putalpha(a); S.info["anchor"] = L.info["anchor"]; _sil["s"] = S
    return _sil["s"]

def s1(cv, fr, t, T):
    stage_fill(cv, fr, (30, 34, 40), "nys1bg")
    rays(cv, (CX, 1300), t, .45, 10, 1300, (60, 90, 70), .12, .15)
    hl(cv, fr, H1, t, -.3)
    tt = w(1, "Tu")
    pulse = 1 + .025*math.sin(t*7) + .06*pop_in(t, tt, .3)*(1 - prog(t, tt + .3, .3))
    blit(cv, ney_silhouette(), CX, 1700, pulse)
    QM.draw(cv, fr, CX + 230, 1190 + 12*math.sin(t*4), .7*win(t, .1), 12)
    t1, t2, t3 = w(1, "quatre"), w(1, "vingt-cinq"), w(1, "trente-quatre")
    kw(cv, fr, AGE[0], t, t1, None, 250, 480, -4)
    ta = w(1, "accident")
    if t > ta - .1:
        crash = ease_out_back(prog(t, ta, .25))
        draw_car(cv, fr, 740, 480, .55*pop_in(t, ta - .1), -18*crash)
        if ta < t < ta + .5:
            for k in range(6):
                an = k*1.05; r = 60 + 160*prog(t, ta, .5)
                draw_star(cv, 740 + r*math.cos(an), 460 + r*math.sin(an), 22*(1 - prog(t, ta, .5)), 1, t*5, (255, 220, 120))
        show(cv, fr, T1a, t, ta + .1, None, 740, 590, 2)
    kw(cv, fr, AGE[1], t, t2, None, 250, 720, 3)
    tc = w(1, "joueur")
    if t > tc:
        LBL(f"{counter(0, 222000000, prog(t, tc, 1.0))} €", "ny222", font("title", 60), GOLD, None, stroke=4, stroke_fill=PAL["ink"]).draw(cv, fr, 700, 720, pop_in(t, tc), -2)
    kw(cv, fr, AGE[2], t, t3, None, 250, 960, -3)
    tp = w(1, "pleure")
    if t > tp:
        drops(cv, "nytears1", t - tp, [(690, 900), (760, 900)], n=3, size=16, speed=300)
        show(cv, fr, T1b, t, tp, None, 725, 980, 3)
    kw(cv, fr, K1d, t, tt, None, CX, 1320, -2)
    for tt_ in (t1, ta, t2, t3): impact(cv, t, tt_, 10)
    glitch(cv, fr, t, tt, .4, 16); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 2 — révélation, 1992, l'accident
def s2a(cv, fr, t):
    stage_fill(cv, fr, VERT, "nys2a")
    rays(cv, (CX, 1000), t, 1.0, 16, 1500, (240, 210, 60))
    land = w(2, "Junior") + .1; hop = 240*math.sin(clamp(t/land)*math.pi) if t < land else 0
    if t < land:
        L = NEY.render_layer(fr, 1.1, age=1, kit="brazil", arms=(160, 160), mood="cheer")
        blit_sxy(cv, L, CX, 1560 - hop, max(.05, abs(math.cos(clamp(t/land)*math.pi*2))), 1.0)
    else:
        NEY.draw(cv, fr, CX, 1560, 1.1, age=1, kit="brazil", arms=(150, 150), legs=(14, 14), mood="cheer", t=t)
    show_stamp(cv, fr, N2, t, .1, CX, 420, -4)
    confetti(cv, fr, "nyc2", t - land, 80, 4, [JAUNE, VERT, BLANC, BLEU_BR])
    impact(cv, t, land, 18); flashes(cv, t, land, .15, .7)

def s2b(cv, fr, t):
    stage_fill(cv, fr, (170, 214, 236), "nys2b"); d = ImageDraw.Draw(cv)
    d.ellipse([-200, 1100, 1300, 2300], fill=(110, 170, 90))
    for i, P in enumerate(HOUSES):
        x = 180 + (i % 3)*300 + (60 if i >= 3 else 0); y = 1250 + (i // 3)*160
        P.draw(cv, fr, x, y - 20*pop_in(t, w(2, "famille") - .2 + i*.05), 1)
    kw(cv, fr, K2a, t, w(2, "mille"), None, CX, 440, -3)
    show(cv, fr, T2a, t, w(2, "près"), None, 330, 640, -3)
    show(cv, fr, T2b, t, w(2, "famille"), None, 740, 760, 3)

def s2c(cv, fr, t):
    stage_fill(cv, fr, (26, 30, 48), "nys2c"); d = ImageDraw.Draw(cv)
    d.rectangle([30, 1300, 1050, 1890], fill=(60, 60, 66))
    for k in range(6): d.rectangle([60 + k*190, 1480, 160 + k*190, 1496], fill=(220, 214, 190))
    draw_car(cv, fr, 560, 1250, 1.3, 16, t)
    particles(cv, fr, "nysmoke", (820, 1180), (t*.8) % 1, 10, 200, [(120, 120, 130), (90, 90, 100)], 26, -120)
    siren_lights(cv, t, .18)
    tr = w(2, "retrouvent")
    a = pop_in(t, tr - .1, .4)
    if a > 0:
        d.ellipse([CX - 190*a, 700 - 190*a, CX + 190*a, 700 + 190*a], fill=(250, 246, 234), outline=PAL["ink"], width=6)
        NEY.head.draw(cv, fr, CX, 720, 2.2*a); NEY.hair_kid.draw(cv, fr, CX, 720, 2.2*a)
        if a > .9:
            NEY.face(cv, CX, 720, 2.2, "happy" if t > w(2, "simple") else "surprised", (0, 0), False, t, 0)
            if t > w(2, "égratignure") - .2: bandaid(cv, CX - 60, 600, 1.2, -25)
    show(cv, fr, T2c, t, w(2, "banquette") - .1, None, 330, 470, -3)
    kw(cv, fr, K2b, t, w(2, "simple"), None, CX, 1000, 3)

def s2(cv, fr, t, T):
    shots(cv, fr, t, [(0, s2a), (w(2, "Né") - .1, s2b), (w(2, "Après") - .1, s2c)])
    drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 3 — futsal, essai au Real, Santos le garde
def s3a(cv, fr, t):
    stage_fill(cv, fr, (226, 170, 110), "nys3a"); d = ImageDraw.Draw(cv)
    for k in range(10): d.line([(30, 200 + k*170), (1050, 200 + k*170)], fill=(206, 150, 94), width=4)
    d.rectangle([90, 700, 990, 1760], outline=(250, 250, 246), width=8); d.ellipse([CX-140, 1090, CX+140, 1370], outline=(250, 250, 246), width=8)
    x = lerp(160, 880, ease_io(prog(t, .1, 2.0))); step = 22*math.sin(t*20)
    for i, (P, kx) in enumerate(zip(KIDS, (400, 660))):
        fall = ease_out_cubic(prog(t, .1 + (kx - 160)/720*2.0 - .1, .35))
        if fall <= 0: P.draw(cv, fr, kx, 1520, .75, age=.1, kit="street", mood="determined", t=t, look=(-1, 0))
        else: blit(cv, P.render_layer(fr, .75, age=.1, kit="street", mood="surprised"), kx + 40*fall, 1520, 1, 80*fall*(1 if i else -1))
    NEY.draw(cv, fr, x, 1540, .8, age=.1, kit="brazil", mood="happy", legs=(step, -step), t=t)
    draw_ball(cv, fr, x + 60 + 14*math.sin(t*20), 1510, .4, t*600)
    speed_lines(cv, fr, (x, 1300), .22, n=30, seed=3, inner=380)
    kw(cv, fr, K3a, t, w(3, "futsal") - .1, None, CX, 460, -3)

def s3b(cv, fr, t):
    stage_fill(cv, fr, (150, 200, 236), "nys3b")
    tr = w(3, "Real")
    u = prog(t, w(3, "quatorze") - .2, 1.4)
    PLANE.draw(cv, fr, lerp(-250, 1300, u), lerp(1000, 700, u), 1.0, 8)
    kw(cv, fr, K3b, t, w(3, "quatorze"), None, 300, 440, -4)
    show(cv, fr, T3a, t, tr, None, 640, 600, 3)
    NEY.draw(cv, fr, CX, 1640, .95, age=.45, kit="real", mood="happy", t=t, arms=(20, 150 if t > tr else 20))

def s3c(cv, fr, t):
    stage_fill(cv, fr, (30, 30, 34), "nys3c"); d = ImageDraw.Draw(cv)
    for k in range(6): d.rectangle([30 + k*180, 130, 120 + k*180, 1890], fill=(250, 250, 246))
    ts = w(3, "Santos")
    spin(cv, fr, NEY, CX, 1640, 1.0, t, ts - .1, "real", "santos", age=.45, mood="happy")
    bill_rain(cv, fr, t, w(3, "grand"), 1.2, 12, "nybills3")
    show_stamp(cv, fr, K3c, t, w(3, "garder") - .1, CX, 460, -5)

def s3(cv, fr, t, T):
    shots(cv, fr, t, [(0, s3a), (w(3, "À") - .1, s3b), (w(3, "mais") - .1, s3c)])
    impact(cv, t, w(3, "garder") - .1, 14); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 4 — Santos : la crête, les grigris, la Libertadores
def s4a(cv, fr, t):
    pitch(cv, fr, "nyp4a")
    x = lerp(-150, CX, ease_out_cubic(prog(t, .05, .9))); lg, bob = walk(t, 12, 26) if t < .95 else ((0, 0), 0)
    NEY_S.draw(cv, fr, x, 1640 - bob, 1.05, age=.8, kit="santos", mood="determined", legs=lg, t=t)
    kw(cv, fr, K4a, t, w(4, "dix-sept"), None, 300, 440, -4)
    show(cv, fr, T4a, t, w(4, "débute"), None, 620, 600, 3)

def s4b(cv, fr, t):
    stage_fill(cv, fr, (250, 214, 60), "nys4b")
    rays(cv, (CX, 1000), t, .8, 16, 1400, (250, 236, 150))
    tg = w(4, "grigris"); step = 40*math.sin(t*16) if t > tg else 0
    for i, (P, kx) in enumerate(zip(DEF, (230, 850))):
        rot = (t - tg)*600*(1 if i else -1) if t > tg + .2 else 0
        L = P.render_layer(fr, .85, age=1, kit="alhilal" if False else "street", mood="surprised")
        blit(cv, L, kx, 1600, 1, rot % 360 if rot else 0)
    NEY_S.draw(cv, fr, CX, 1620, 1.1, age=.8, kit="santos", mood="happy", legs=(step, -step), t=t)
    draw_ball(cv, fr, CX + 30*math.sin(t*16), 1580, .5, t*800)
    tc = w(4, "Crête")
    if t > tc:
        d = ImageDraw.Draw(cv); hy = 1620 - 570*1.1 - 60
        d.ellipse([CX - 80, hy - 80, CX + 80, hy + 40], outline=ROUGE, width=8)
        arrow(d, (820, 700), (CX + 80, hy - 30), prog(t, tc, .3), ROUGE, 10, 5, 40, -.2)
        kw(cv, fr, K4b, t, tc, tg - .1, 780, 620, 5)
    kw(cv, fr, K4c, t, tg, None, CX, 440, -4)
    show_stamp(cv, fr, K4d, t, w(4, "Brésil"), CX, 600, 3)
    camera_flashes(cv, fr, "nycf4", t - w(4, "Brésil"), 1.2, 10)

def s4c(cv, fr, t):
    stage_fill(cv, fr, (24, 24, 30), "nys4c")
    rays(cv, (CX, 900), t, 1.0, 16, 1400, (220, 220, 230))
    tl = w(4, "Copa")
    trophy_lift(cv, fr, NEY_S, CX, 1760, .9, "santos", t, LIBCUP, age=.85)
    show(cv, fr, T4b, t, w(4, "onze"), None, 300, 440, -4)
    kw(cv, fr, K4e, t, tl, None, CX, 600, -3)
    confetti(cv, fr, "nyc4", t - tl, 70, 4, [BLANC, (60, 60, 60), GOLD])

def s4(cv, fr, t, T):
    shots(cv, fr, t, [(0, s4a), (w(4, "Crête") - .1, s4b), (w(4, "Et") - .1, s4c)])
    impact(cv, t, w(4, "grigris"), 14); impact(cv, t, w(4, "Copa"), 14); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 5 — Barcelone : le trio, la finale 2015
def s5a(cv, fr, t):
    sx0, sy0, sx1, sy1 = STAGE
    stage_fill(cv, fr, (0, 77, 152), "nys5a"); d = ImageDraw.Draw(cv)
    for k in range(0, 6, 2): d.rectangle([30 + k*170, sy0, 30 + (k+1)*170, sy1], fill=(165, 0, 68))
    tb = w(5, "Barcelone")
    spin(cv, fr, NEY, CX, 1640, .9, t, tb - .1, "santos", "barca", mood="happy")
    tm, ts = w(5, "Messi"), w(5, "Suárez")
    if t > tm - .1: MESSI.draw(cv, fr, 220, 1640, .88*pop_in(t, tm - .1), age=1, kit="barca", beard=True, mood="happy", t=t)
    if t > ts - .1: SUAREZ.draw(cv, fr, 860, 1640, .9*pop_in(t, ts - .1), age=1, kit="barca", beard=True, mood="happy", t=t)
    tt = w(5, "trio")
    for i, x in enumerate((220, 860, CX)):
        a = pop_in(t, tt + i*.1)
        if a > 0: MSN[i].draw(cv, fr, x, 1000, a, (-6, 6, 0)[i])
    kw(cv, fr, K5a, t, .05, None, CX, 420, -3)
    kw(cv, fr, K5b, t, w(5, "monstrueux") - .1, None, CX, 600, 3)

def s5b(cv, fr, t):
    stadium(cv, fr, "nys5stad", t, horizon=1000)
    tm = w(5, "marque")
    draw_goal(cv, fr, 800, 1300, 380, 240, prog(t, tm + .15, .5), 1, t)
    kick = math.sin(prog(t, tm - .25, .3)*math.pi)
    DEF[0].draw(cv, fr, 560, 1640, .9, age=1, kit="juventus", mood="surprised", t=t, look=(1, 0))
    NEY.draw(cv, fr, 300, 1660, 1.0, age=1, kit="barca", mood="cheer" if t > tm + .2 else "determined", legs=(0, 50*kick), t=t,
             arms=(150, 150) if t > tm + .3 else (20, 20))
    if t < tm + .2:
        u = prog(t, tm - .1, .3); p = bezier((370, 1630), (560, 1300), (770, 1180), u); draw_ball(cv, fr, p[0], p[1], .5, t*800)
    kw(cv, fr, K5c, t, w(5, "Et", 2) + .05, None, CX, 420, -3)
    show_stamp(cv, fr, K5d, t, tm + .15, CX, 600, 4)
    if t > w(5, "champions") - .1:
        UCL.draw(cv, fr, 800, 820, .8*pop_in(t, w(5, "champions") - .1), 4*math.sin(t*3))
        confetti(cv, fr, "nyc5", t - w(5, "champions"), 60, 3, [(0, 77, 152), (165, 0, 68), GOLD])

def s5(cv, fr, t, T):
    shots(cv, fr, t, [(0, s5a), (w(5, "Et", 2) - .1, s5b)])
    impact(cv, t, w(5, "marque") + .15, 16); flashes(cv, t, w(5, "marque") + .15, .12, .6); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 6 — la remontada, minute par minute
def s6a(cv, fr, t):
    stage_fill(cv, fr, (30, 26, 40), "nys6a")
    rays(cv, (CX, 1000), t, .6, 14, 1400, (90, 60, 110))
    kw(cv, fr, K6a, t, w(6, "dix-sept"), None, 300, 420, -4)
    show_stamp(cv, fr, K6b, t, w(6, "chef-d'œuvre"), CX, 600, 3)
    score2(cv, fr, CX, 1000, "PSG", "BARÇA", 4, 0, "match aller", pop_in(t, w(6, "Barça") - .1))
    show(cv, fr, T6a, t, w(6, "remonter"), None, CX, 1260, -2)
    kw(cv, fr, K6c, t, w(6, "quatre"), None, CX, 1400, 3)

def s6b(cv, fr, t):
    stadium(cv, fr, "nys6stad", t, horizon=1000, pal=[(0, 77, 152), (165, 0, 68), (230, 200, 60), (200, 196, 190)])
    g1 = w(6, "but", 2); g2 = w(6, "but", 3)
    draw_goal(cv, fr, CX, 1300, 460, 260, max(prog(t, g1, .5), prog(t, g2, .5)) if t > g1 else 0, 1, t)
    GK.draw(cv, fr, CX + (-120*ease_out_cubic(prog(t, g1 - .15, .3)) if t < g2 - .4 else 130*ease_out_cubic(prog(t, g2 - .15, .3))),
            1300, .7, age=1, kit="psg", mood="surprised", arms=(90, 90), t=t)
    if t < g1 + .05:
        u = prog(t, w(6, "coup") - .05, g1 - w(6, "coup") + .05); p = bezier((200, 1760), (100, 900), (CX + 160, 1100), u)
        draw_ball(cv, fr, p[0], p[1], lerp(.7, .45, u), t*600)
    elif w(6, "Penalty") < t < g2 + .05:
        u = prog(t, w(6, "Penalty") + .2, g2 - w(6, "Penalty") - .15); p = lerp_pt((CX, 1760), (CX - 150, 1130), u)
        draw_ball(cv, fr, p[0], p[1], lerp(.7, .45, u), t*800)
    goals = 3 + (1 if t > g1 else 0) + (1 if t > g2 else 0)
    score2(cv, fr, 700, 560, "BARÇA", "PSG", goals, 1, f"cumul : {goals} - 5", .6)
    m = "91'" if t > w(6, "Penalty") - .1 else "88'"
    MIN[m].draw(cv, fr, 220, 520, pop_in(t, w(6, "Quatre-vingt-huitième") - .1), -4)
    for gt in (g1, g2): kw(cv, fr, K6d, t, gt, gt + .55, CX, 820, -3)

def s6c(cv, fr, t):
    stadium(cv, fr, "nys6c", t, horizon=1000, pal=[(0, 77, 152), (165, 0, 68), (230, 200, 60), (200, 196, 190)])
    tp = w(6, "passe"); t6 = w(6, "six")
    MIN["95'"].draw(cv, fr, 220, 520, 1, -4)
    draw_goal(cv, fr, 760, 1300, 420, 250, prog(t, t6 - .2, .5), 1, t)
    NEY.draw(cv, fr, 220, 1700, .9, age=1, kit="barca", mood="cheer" if t > t6 else "determined", t=t, legs=(0, 40*math.sin(prog(t, tp - .2, .3)*math.pi)),
             arms=(150, 150) if t > t6 else (20, 20))
    hop = 120*math.sin(clamp((t - t6 + .5)/.6)*math.pi)
    SERGI.draw(cv, fr, 620, 1640 - hop, .95, age=1, kit="barca", mood="cheer" if t > t6 else "determined", t=t,
               legs=(0, 50*math.sin(prog(t, t6 - .35, .3)*math.pi)), arms=(150, 150) if t > t6 else (30, 30))
    if tp < t < t6 - .2:
        u = prog(t, tp, t6 - .2 - tp); p = bezier((280, 1660), (450, 900), (650, 1560), u); draw_ball(cv, fr, p[0], p[1], .5, t*500)
    elif t6 - .2 <= t < t6 + .1:
        p = lerp_pt((650, 1560), (740, 1180), prog(t, t6 - .2, .25)); draw_ball(cv, fr, p[0], p[1], .5, t*900)
    show(cv, fr, T6b, t, w(6, "Sergi"), None, 700, 800, 3)
    if t > t6:
        rays(cv, (CX, 900), t, prog(t, t6, .3), 16, 1400, (250, 220, 120))
        kw(cv, fr, K6e, t, t6, None, CX, 720, -4)
        show_stamp(cv, fr, K6f, t, t6 + .3, CX, 950, 4)
        confetti(cv, fr, "nyc6", t - t6, 100, 4, [(0, 77, 152), (165, 0, 68), GOLD])

def s6(cv, fr, t, T):
    shots(cv, fr, t, [(0, s6a), (w(6, "Quatre-vingt-huitième") - .12, s6b), (w(6, "Et") - .1, s6c)])
    for gt in (w(6, "but", 2), w(6, "but", 3)): impact(cv, t, gt, 16); flashes(cv, t, gt, .1, .5)
    impact(cv, t, w(6, "six"), 24); flashes(cv, t, w(6, "six"), .15, .8); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 7 — PAUSE : le prochain joueur ?
def s7(cv, fr, t, T):
    stage_fill(cv, fr, VERT, "nys7"); d = ImageDraw.Draw(cv)
    kw(cv, fr, K7a, t, .05, None, 740, 330, 4)
    tp = w(7, "prochain")
    kw(cv, fr, K7b, t, tp, None, 730, 540, -3)
    if t < tp + .2: QM.draw(cv, fr, CX, 1020 + 12*math.sin(t*5), .8*win(t, w(7, "C'est"), tp + .1), 8)
    for i in range(4):
        a = pop_in(t, tp + .15 + i*.1)
        if a <= 0: continue
        x = 180 + i*240; y = 1010 + 10*math.sin(t*4 + i)
        CARD.draw(cv, fr, x, y, a, (-4, 3, -2, 5)[i])
        LBL("?", "nyqmS", font("title", 130), (60, 56, 64), None).draw(cv, fr, x, y - 30, a)
        NAMES[i].draw(cv, fr, x, y + 90, a)
    te = w(7, "Écris")
    if t > te:
        a = pop_in(t, te)
        speech_bubble(cv, fr, "nycta_b", typewriter("Ronaldinho stp !!", prog(t, te + .15, .8)) or " ", 520, 1300, a, (-1, 1), 60)
        bx = 880 + 18*math.sin(t*8)
        arrow(d, (760, 1320), (bx + 80, 1180), prog(t, te + .2, .3), PAL["ink"], 10, 7, 34, -.2)
    kw(cv, fr, K7c, t, w(7, "commentaire"), None, 560, 1470, 2)
    kw(cv, fr, K7d, t, w(7, "Allez"), None, 730, 740, -5)
    impact(cv, t, w(7, "Allez"), 14)

def s7_post(cv, fr, t, T):
    a = pop_in(t, .25)
    if a <= 0: return
    d = ImageDraw.Draw(cv); cx, cy, s = 250, 470, a
    d.ellipse([cx-70*s, cy-70*s, cx+70*s, cy+70*s], fill=(34, 32, 36))
    for dx in (-22, 22): d.rectangle([cx+dx*s-12*s, cy-34*s, cx+dx*s+12*s, cy+34*s], fill=(250, 248, 240))

# ------------------------------------------------------------------ SCÈNE 8 — 222 millions
def s8(cv, fr, t, T):
    stage_fill(cv, fr, NAVY, "nys8"); d = ImageDraw.Draw(cv)
    EIFFEL.draw(cv, fr, 840, 1120, 1)
    tpsg = w(8, "PSG"); tcl = w(8, "clause"); t222 = w(8, "deux")
    spin(cv, fr, NEY, 330, 1660, 1.0, t, tpsg - .1, "barca", "psg", mood="happy")
    kw(cv, fr, K8c, t, .05, tcl + .05, CX, 440, -3)
    if t < tcl + .1:
        DOC.draw(cv, fr, 760, 900, .75*pop_in(t, tpsg + .1), 5)
    else:
        A, B = torn_doc(); u = ease_out_cubic(prog(t, tcl + .1, .6))
        blit(cv, A, 760 - 160*u, 900 + 200*u*u, .75, 5 + 25*u, 1 - .5*u)
        blit(cv, B, 760 + 160*u, 900 + 220*u*u, .75, 5 - 30*u, 1 - .5*u)
        show_stamp(cv, fr, K8a, t, tcl + .1, CX, 440, -6, t_out=t222 - .05)
    if t > t222:
        LBL(f"{counter(0, 222000000, prog(t, t222, 1.0))} €", "ny222b", font("title", 100), GOLD, None, stroke=6, stroke_fill=PAL["ink"]).draw(cv, fr, CX, 460, pop_in(t, t222), -2)
    bill_rain(cv, fr, t, t222, 1.6, 16)
    show_stamp(cv, fr, K8b, t, w(8, "transfert"), CX, 640, 4)
    camera_flashes(cv, fr, "nycf8", t - w(8, "transfert"), 1.4, 12)
    show(cv, fr, T8a, t, w(8, "encore"), None, CX, 790, -2)
    impact(cv, t, w(8, "transfert"), 18); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 9 — les blessures, les 14 minutes au sol
def s9a(cv, fr, t):
    stage_fill(cv, fr, (210, 216, 226), "nys9a"); d = ImageDraw.Draw(cv)
    NEY.draw(cv, fr, 330, 1660, 1.05, age=1, kit="psg", mood="sad", t=t, look=(0, 1))
    d.rectangle([330 + 38*1.05 - 26, 1660 - 120, 330 + 38*1.05 + 26, 1660 - 30], fill=(250, 250, 246))   # bandage
    for k in range(3): d.line([(330 + 38*1.05 - 26, 1660 - 110 + k*28), (330 + 38*1.05 + 26, 1660 - 96 + k*28)], fill=(200, 200, 200), width=4)
    tb = w(9, "blessures")
    for i, lab in enumerate(BLESS):
        a = pop_in(t, tb + i*.28)
        if a > 0: lab.draw(cv, fr, 760, 700 + i*150, a, (-5, 4, -3, 6)[i])
    kw(cv, fr, K9a, t, w(9, "Paris"), None, 330, 460, -4)

def s9b(cv, fr, t):
    pitch(cv, fr, "nyp9b")
    t0 = w(9, "Et") - .1
    x = lerp(900, 180, prog(t, t0, 4.5)); ang = (t - t0)*300; h2 = 250; a = math.radians(ang)
    L = NEY.render_layer(fr, .8, age=1, kit="brazil", mood="surprised")
    blit(cv, L, x + h2*math.sin(a), 1420 + h2*math.cos(a), 1, ang)
    tq = w(9, "quatorze")
    stopwatch(cv, 820, 700, .9, prog(t, w(9, "étude"), 2.0))
    secs = int(round(lerp(0, 830, ease_out_cubic(prog(t, w(9, "étude"), 2.0)))))
    LBL(f"{secs // 60:02d}:{secs % 60:02d}", "nysw", font("mono", 70), PAL["ink"], PAL["paper"], padx=14, pady=4).draw(cv, fr, 820, 880, pop_in(t, w(9, "étude")), 0)
    show(cv, fr, T9a, t, w(9, "Mondial"), None, 300, 460, -3)
    kw(cv, fr, K9b, t, tq, None, CX, 1080, 3)
    ti = w(9, "Internet")
    for i, lab in enumerate(MEMES):
        a = pop_in(t, ti + i*.15)
        if a > 0: lab.draw(cv, fr, (260, 800, 380, 720)[i], (620, 1250, 1560, 460)[i] + 8*math.sin(t*9 + i), a, (-10, 8, 6, -6)[i])

def s9(cv, fr, t, T):
    shots(cv, fr, t, [(0, s9a), (w(9, "Et") - .1, s9b)])
    impact(cv, t, w(9, "blessures"), 12); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 10 — or olympique, devant Pelé
def s10a(cv, fr, t):
    stage_fill(cv, fr, (24, 70, 160), "nys10a")
    rays(cv, (CX, 900), t, 1.0, 16, 1500, (240, 210, 90))
    NEY.draw(cv, fr, CX, 1760, .9, age=1, kit="brazil", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
    medal(cv, fr, CX, 900 + 10*math.sin(t*4), 1.4, pop_in(t, w(10, "olympique") - .1))
    kw(cv, fr, K10a, t, w(10, "champion"), None, CX, 420, -3)
    show(cv, fr, T10a, t, w(10, "seize"), None, CX, 580, 2)

def s10b(cv, fr, t):
    stage_fill(cv, fr, (246, 240, 226), "nys10b"); d = ImageDraw.Draw(cv)
    tm = w(10, "meilleur")
    for i, (name, val, col, x) in enumerate((("PELÉ", 77, (150, 150, 156), 330), ("NEYMAR", 79, JAUNE, 750))):
        u = ease_out_cubic(prog(t, tm + i*.2, 1.2)); h = 690*val/80*u
        d.rectangle([x - 110, 1500 - h, x + 110, 1500], fill=col, outline=PAL["ink"], width=5)
        LBL(str(int(round(val*u))), f"nybar{name}", font("title", 110), PAL["ink"], None).draw(cv, fr, x, 1500 - h - 80, pop_in(t, tm + i*.2), 0)
        LBL(name, f"nybn{name}", font("title", 64), PAL["ink"], PAL["paper"], padx=14, pady=4).draw(cv, fr, x, 1570, 1, 0)
    show_stamp(cv, fr, K10b, t, w(10, "devant"), CX, 460, -5)
    show(cv, fr, T10b, t, w(10, "Seleção"), None, CX, 590, 2)
    if t > w(10, "Pelé"): confetti(cv, fr, "nyc10", t - w(10, "Pelé"), 50, 3, [JAUNE, VERT, BLEU_BR])

def s10(cv, fr, t, T):
    shots(cv, fr, t, [(0, s10a), (w(10, "et") - .1, s10b)])
    impact(cv, t, w(10, "devant"), 16); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 11 — Arabie saoudite, le genou, retour à Santos
def s11a(cv, fr, t):
    stage_fill(cv, fr, (236, 208, 150), "nys11a")
    SUN.draw(cv, fr, 820, 480, 1, 0); DUNE.draw(cv, fr, 300, 1700, 1); DUNE.draw(cv, fr, 900, 1760, .9)
    spin(cv, fr, NEY, 330, 1600, 1.0, t, w(11, "Arabie") - .1, "psg", "alhilal", mood="happy")
    bill_rain(cv, fr, t, w(11, "contrat"), 1.4, 14, "nybills11")
    kw(cv, fr, K11e, t, w(11, "vingt-trois") - .1, w(11, "Arabie") - .05, CX, 440, -4)
    kw(cv, fr, K11f, t, w(11, "Arabie"), w(11, "contrat") - .05, CX, 440, 3)
    kw(cv, fr, K11a, t, w(11, "contrat"), None, CX, 440, -3)
    show(cv, fr, T11a, t, w(11, "colossal"), None, 640, 600, 2)

def s11b(cv, fr, t):
    stage_fill(cv, fr, (40, 44, 56), "nys11b"); d = ImageDraw.Draw(cv)
    NEY.draw(cv, fr, CX, 1660, 1.1, age=1, kit="alhilal", mood="sad", t=t, lean=-10, legs=(0, 12))
    kx, ky = CX + 38*1.1, 1660 - 150
    r = 40 + 10*math.sin(t*12)
    d.ellipse([kx - r, ky - r, kx + r, ky + r], outline=ROUGE, width=10)
    show_stamp(cv, fr, K11b, t, w(11, "ligaments"), CX, 460, -5)
    if t > w(11, "Sept"): kw(cv, fr, K11c, t, w(11, "Sept"), None, CX, 700, 3)

def s11c(cv, fr, t):
    stage_fill(cv, fr, (30, 30, 34), "nys11c"); d = ImageDraw.Draw(cv)
    for k in range(6): d.rectangle([30 + k*180, 130, 120 + k*180, 1890], fill=(250, 250, 246))
    spin(cv, fr, NEY, CX, 1640, 1.0, t, w(11, "rentre") - .1, "alhilal", "santos", mood="happy", arms=(150, 150))
    kw(cv, fr, K11d, t, w(11, "Santos") - .1, None, CX, 440, -3)
    show(cv, fr, T11b, t, w(11, "Santos"), None, CX, 600, 2)

def s11(cv, fr, t, T):
    shots(cv, fr, t, [(0, s11a), (w(11, "mais") - .1, s11b), (w(11, "rentre") - .15, s11c)])
    impact(cv, t, w(11, "rompt"), 20); glitch(cv, fr, t, w(11, "rompt"), .4, 18); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 12 — Mondial 2026 : la fin, et le même stade qu'en 2010
def s12a(cv, fr, t):
    stadium(cv, fr, "nys12stad", t, horizon=1000, pal=[JAUNE, VERT, (200, 16, 46), (200, 196, 190), (70, 90, 150)])
    tp = w(12, "penalty"); te = w(12, "éliminé")
    draw_goal(cv, fr, CX, 1300, 460, 260, prog(t, tp + .1, .5), 1, t)
    GK.draw(cv, fr, CX + 140*ease_out_cubic(prog(t, tp - .1, .3)), 1300, .7, age=1, kit="gk", mood="surprised", arms=(90, 90), t=t)
    if w(12, "marque") - .1 < t < tp + .15:
        u = prog(t, w(12, "marque") - .1, tp - w(12, "marque") + .25); p = lerp_pt((CX, 1760), (CX - 150, 1130), u)
        draw_ball(cv, fr, p[0], p[1], lerp(.7, .45, u), t*800)
    score2(cv, fr, 700, 560, "BRÉSIL", "NORVÈGE", 1 if t > tp + .1 else 0, 2, "8e de finale", .6*pop_in(t, w(12, "Norvège") - .1))
    ney_back(cv, fr, 260, 1740, .72, -20*math.sin(prog(t, w(12, "marque") - .3, .35)*math.pi))
    kw(cv, fr, K12a, t, w(12, "Coupe") - .1, w(12, "Norvège") - .15, CX, 440, -3)
    show(cv, fr, T12a, t, w(12, "huitième"), w(12, "Norvège") - .15, CX, 600, 2)
    if t > te:
        grayscale(cv, prog(t, te, .4)*.85)
        show_stamp(cv, fr, K12b, t, te, CX, 900, -6)

def s12b(cv, fr, t):
    stage_fill(cv, fr, (40, 44, 56), "nys12b"); d = ImageDraw.Draw(cv)
    for k in range(60):
        x = (k*89) % 1000 + 40; y = (k*173 + t*1300) % 1500 + 380; d.line([(x, y), (x - 8, y + 36)], fill=(140, 150, 170), width=3)
    eyes = NEY.draw(cv, fr, CX, 2250, 1.9, age=1, kit="brazil", mood="sad", t=t, look=(0, 1), tears=t + .3)
    kw(cv, fr, K12c, t, w(12, "larmes") - .1, None, CX, 420, -3)
    tm = w(12, "maintenant")
    if t > tm - .1:
        speech_bubble(cv, fr, "nyfini", typewriter("MAINTENANT, C'EST FINI.", prog(t, tm, .8)) or " ", CX, 640, pop_in(t, tm - .1), (0, 1), 60)
    grayscale(cv, .6)

def s12c(cv, fr, t):
    stadium(cv, fr, "nys12c", t, horizon=1000)
    tb = w(12, "but") + .05
    draw_goal(cv, fr, 800, 1300, 380, 240, prog(t, tb + .2, .5), 1, t)
    hop = 130*math.sin(clamp((t - tb + .3)/.6)*math.pi)
    NEY_S.draw(cv, fr, 380, 1680 - hop, 1.0, age=.85, kit="brazil", mood="cheer" if t > tb + .3 else "determined", t=t,
               arms=(150, 150) if t > tb + .3 else (30, 30))
    hx, hy = 380, 1680 - hop - 580
    if t < tb:
        p = bezier((1000, 700), (700, 500), (hx + 20, hy - 10), prog(t, tb - .7, .7)); draw_ball(cv, fr, p[0], p[1], .5, t*500)
    elif t < tb + .25:
        p = lerp_pt((hx + 20, hy - 10), (780, 1180), prog(t, tb, .25)); draw_ball(cv, fr, p[0], p[1], .5, t*800)
    kw(cv, fr, K12d, t, w(12, "Seize") - .05, None, CX, 440, -3)
    show(cv, fr, T12b, t, w(12, "premier"), None, CX, 600, 2)
    old_film(cv, fr, t, 1.0)
    show_stamp(cv, fr, K12e, t, w(12, "même") - .05, CX, 900, -4)

def s12(cv, fr, t, T):
    shots(cv, fr, t, [(0, s12a), (w(12, "En") - .1, s12b), (w(12, "Seize") - .12, s12c)])
    impact(cv, t, w(12, "penalty") + .1, 14); impact(cv, t, w(12, "éliminé"), 18); glitch(cv, fr, t, w(12, "éliminé"), .35, 14)
    impact(cv, t, w(12, "même"), 14); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 13 — génie ou gâchis ?
def s13(cv, fr, t, T):
    sx0, sy0, sx1, sy1 = STAGE; d = ImageDraw.Draw(cv)
    stage_fill(cv, fr, GOLD, "nys13")
    d.polygon([(CX + 60, sy0), (sx1, sy0), (sx1, sy1), (CX - 60, sy1)], fill=(80, 80, 88))
    rays(cv, (280, 1000), t, .5, 12, 900, (250, 220, 120))
    NEY.draw(cv, fr, CX, 1640, 1.0, age=1, kit="brazil", mood="happy" if int(t*2) % 2 else "sad", arms=(150, 20) if int(t*2) % 2 else (20, 150), t=t)
    tg, tq = w(13, "génie"), w(13, "gâchis")
    BTN_G.draw(cv, fr, 280, 520, pop_in(t, tg)*(1 + .05*math.sin(t*8)), -5)
    BTN_Q.draw(cv, fr, 790, 520, pop_in(t, tq)*(1 + .05*math.sin(t*8 + 1)), 5)
    draw_star(cv, 280, 760, 60, pop_in(t, tg + .1), t*2)
    tc = w(13, "commentaire")
    if t > tc:
        arrow(d, (640, 1480), (960, 1180), prog(t, tc, .3), PAL["ink"], 12, 12, 40, .2)
    tb = w(13, "abonne-toi")
    if t > tb:
        press = 1 - .12*math.sin(prog(t, tb + .5, .25)*math.pi)
        BTN_SUB.draw(cv, fr, CX, 760, pop_in(t, tb)*press, -2)
    kw(cv, fr, K13a, t, w(13, "prochaine"), None, CX, 920, 3)
    if t > w(13, "prochaine"): confetti(cv, fr, "nyc13", t - w(13, "prochaine"), 70, 5, [JAUNE, VERT, BLEU_BR])
    impact(cv, t, tg, 10); impact(cv, t, tq, 10); drift(cv, t, T)

# ------------------------------------------------------------------ scènes + bruitages
def SC(name, n, fn, sfx, trans=None, trans_dur=.3, pad_out=.3):
    return Scene(name, TEXTS[n-1], fn, sfx, pad_in=PAD, pad_out=pad_out, trans=trans, trans_dur=trans_dur)
W_ = w
SCENES = [
    SC("devinette", 1, s1, [(.0, "boom", .7), (.05, "riser", .5), (W_(1, "quatre"), "stamp", .7), (W_(1, "accident") - .15, "crash", .8, 1.2),
                            (W_(1, "vingt-cinq"), "stamp", .7), (W_(1, "joueur"), "cash"), (W_(1, "trente-quatre"), "stamp", .7),
                            (W_(1, "pleure"), "heart", .6), (W_(1, "Tu") - .5, "riser", .8), (W_(1, "Tu"), "glitch", .8, .45)]),
    SC("revelation", 2, s2, [(.0, "boom"), (.0, "samba", .9), (.05, "whoosh_up", .6), (W_(2, "Junior"), "stamp"), (W_(2, "Junior") + .1, "crowd_long", .8),
                             (W_(2, "Né") - .1, "whoosh", .5), (W_(2, "mille"), "pop"), (W_(2, "près"), "pop2"), (W_(2, "famille"), "pop"),
                             (W_(2, "Après") - .1, "whoosh", .5), (W_(2, "Après"), "siren", .6), (W_(2, "retrouvent"), "pop2"),
                             (W_(2, "simple"), "stamp", .7), (W_(2, "égratignure"), "sparkle", .6)], trans="punch", trans_dur=.35),
    SC("futsal", 3, s3, [(.1, "kick", .4), (.5, "thud", .5), (1.1, "thud", .5), (W_(3, "futsal") - .1, "stamp", .6), (W_(3, "À") - .1, "whoosh", .5),
                         (W_(3, "quatorze") - .2, "plane", .7), (W_(3, "quatorze"), "stamp", .6), (W_(3, "Real"), "pop"), (W_(3, "mais") - .1, "whoosh", .6),
                         (W_(3, "Santos") - .1, "swish"), (W_(3, "grand"), "cash", .8), (W_(3, "garder") - .1, "stamp")], trans="whip"),
    SC("santos", 4, s4, [(.05, "whistle", .5), (W_(4, "dix-sept"), "stamp", .6), (W_(4, "débute"), "pop"), (W_(4, "Crête") - .1, "whoosh", .5),
                         (W_(4, "Crête"), "scribble", .6), (W_(4, "grigris"), "whoosh", .6), (W_(4, "grigris") + .3, "laugh", .5),
                         (W_(4, "Brésil"), "crowd_long", .9), (W_(4, "Brésil"), "stamp", .7), (W_(4, "Et") - .1, "whoosh", .5),
                         (W_(4, "Copa"), "sparkle"), (W_(4, "Copa"), "stamp", .6)], trans="tear_h", trans_dur=.6),
    SC("barca", 5, s5, [(.0, "boom", .6), (W_(5, "Barcelone") - .1, "swish"), (W_(5, "Messi"), "pop"), (W_(5, "Suárez"), "pop2"),
                        (W_(5, "trio"), "pop"), (W_(5, "trio") + .1, "pop"), (W_(5, "trio") + .2, "pop2"), (W_(5, "monstrueux"), "stamp", .7),
                        (W_(5, "Et", 2) - .1, "whoosh", .6), (W_(5, "marque") - .25, "kick"), (W_(5, "marque") + .15, "crowd_long", 1.0),
                        (W_(5, "champions"), "sparkle")], trans="whip"),
    SC("remontada", 6, s6, [(.0, "boom", .6), (W_(6, "chef-d'œuvre"), "stamp"), (W_(6, "Barça"), "pop"), (W_(6, "quatre"), "stamp", .6),
                            (W_(6, "quatre") + .2, "heart", .7), (W_(6, "Quatre-vingt-huitième") - .12, "whoosh", .6), (W_(6, "coup"), "kick"),
                            (W_(6, "but", 2), "crowd", .9), (W_(6, "but", 2), "boom", .5), (W_(6, "Penalty"), "whistle", .5), (W_(6, "Penalty") + .2, "kick"),
                            (W_(6, "but", 3), "crowd", .9), (W_(6, "Et") - .1, "whoosh", .6), (W_(6, "passe"), "kick", .6), (W_(6, "six") - .35, "kick"),
                            (W_(6, "six"), "crowd_long", 1.0), (W_(6, "six"), "boom"), (W_(6, "six") + .3, "stamp")], trans="punch", trans_dur=.35),
    SC("pause", 7, s7, [(0, "scratch", 1.0, .9), (.3, "pop"), (W_(7, "prochain"), "stamp", .6)] + [(W_(7, "prochain") + .15 + i*.1, "notif", .7) for i in range(4)] +
                       [(W_(7, "Écris"), "notif"), (W_(7, "Écris") + .15, "scribble", .5), (W_(7, "commentaire"), "pop2"), (W_(7, "Allez"), "whoosh"),
                        (W_(7, "Allez"), "boom", .5)], trans="polaroid", pad_out=.35),
    SC("psg", 8, s8, [(.0, "whoosh_up", .6), (W_(8, "PSG") - .1, "swish"), (W_(8, "clause") + .1, "rip"), (W_(8, "deux"), "cash"),
                      (W_(8, "deux") + .3, "tick", .8), (W_(8, "transfert"), "stamp"), (W_(8, "transfert"), "flash"), (W_(8, "encore"), "pop")], trans="whip"),
    SC("blessures", 9, s9, [(W_(9, "Paris"), "stamp", .6)] + [(W_(9, "blessures") + i*.28, "pop") for i in range(4)] +
                          [(W_(9, "Et") - .1, "whoosh", .6), (W_(9, "Mondial"), "pop2"), (W_(9, "étude"), "tick", .9), (W_(9, "quatorze"), "stamp", .7),
                           (W_(9, "Internet"), "laugh", .9), (W_(9, "Internet"), "notif", .6), (W_(9, "régale"), "notif", .5)], trans="tear_d", trans_dur=.6),
    SC("legende", 10, s10, [(.0, "boom", .6), (W_(10, "champion"), "stamp", .6), (W_(10, "olympique"), "sparkle"), (W_(10, "olympique"), "crowd", .7),
                            (W_(10, "et") - .1, "whoosh", .6), (W_(10, "meilleur"), "tick"), (W_(10, "devant"), "stamp"), (W_(10, "Pelé"), "crowd", .7)],
       trans="punch", trans_dur=.35),
    SC("arabie", 11, s11, [(W_(11, "Arabie") - .1, "swish"), (W_(11, "contrat"), "cash"), (W_(11, "colossal"), "pop"), (W_(11, "mais") - .1, "whoosh", .5),
                           (W_(11, "rompt"), "boom", .8), (W_(11, "rompt"), "glitch", .7, .4), (W_(11, "ligaments"), "stamp"), (W_(11, "Sept"), "pop2"),
                           (W_(11, "rentre") - .15, "whoosh", .6), (W_(11, "Santos"), "crowd", .8)], trans="whip"),
    SC("fin_selecao", 12, s12, [(.0, "crowd_long", .7), (W_(12, "Coupe") - .1, "stamp", .6), (W_(12, "Norvège") - .1, "pop"), (W_(12, "marque") - .1, "kick"),
                                (W_(12, "penalty") + .1, "crowd", .6), (W_(12, "éliminé") - .1, "whistle", .7), (W_(12, "éliminé"), "stamp"),
                                (W_(12, "éliminé") + .1, "groan", .7), (W_(12, "En") - .1, "whoosh", .4), (W_(12, "maintenant"), "scribble", .4),
                                (W_(12, "Seize") - .12, "scratch", .6, .5), (W_(12, "but") - .6, "kick", .5), (W_(12, "but") + .3, "crowd", .7),
                                (W_(12, "même") - .05, "stamp")], trans="tear_v", trans_dur=.6),
    SC("fin", 13, s13, [(.0, "boom", .6), (W_(13, "génie"), "stamp", .7), (W_(13, "gâchis"), "stamp", .7), (W_(13, "commentaire"), "notif"),
                        (W_(13, "abonne-toi"), "pop2"), (W_(13, "abonne-toi") + .5, "notif"), (W_(13, "prochaine"), "samba", .8), (W_(13, "prochaine"), "sparkle")],
       trans="punch", trans_dur=.35, pad_out=1.3),
]
SCENES[6].trans_dur = 99      # la photo figée reste épinglée pendant toute la pause
SCENES[6].post = s7_post

# ------------------------------------------------------------------ couverture
def cover(path):
    cv = background(0, TITLE); stage_fill(cv, 0, NAVY, "nycov"); d = ImageDraw.Draw(cv)
    rays(cv, (CX, 1100), 0.3, 1.0, 16, 1500, (60, 90, 170))
    Label("222 MILLIONS…", "nycv1", font("title", 118), PAL["ink"], GOLD, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 300, 1, -3)
    Label("GÉNIE OU GÂCHIS ?", "nycv2", font("title", 104), PAL["cream"], ROUGE, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 470, 1, 2)
    for k in range(10):
        BILL.draw(cv, 0, 120 + (k*97) % 860, 640 + (k*173) % 500, 1.0, (k*37) % 60 - 30)
    NEY.draw(cv, 0, CX, 1580, 1.25, age=1, kit="psg", mood="happy", arms=(150, 150), legs=(14, 14), t=1)
    Label("L'HISTOIRE FOLLE DE NEYMAR", "nycv3", font("title", 64), PAL["cream"], VERT, padx=30, pady=12).draw(cv, 0, CX, 1690, 1, 1)
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
        p = os.path.join(out, f"ny_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", "neymar")
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/neymar_stills"), only=only)); sys.exit()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25))
