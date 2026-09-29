"""Épisode « Légendes du foot » #3 : Zinédine Zidane.
Accroche « cold open » : le coup de tête de 2006 en ouverture, arrêt sur image, puis rembobinage VHS jusqu'en 1972.
Appel à commenter au milieu (arrêt sur image), montage nerveux : plusieurs plans par scène, mots clés calés sur la voix.

  python3 episodes/zidane/zidane.py output/zidane --stills [3,4]
  python3 episodes/zidane/zidane.py output/zidane --cover
  python3 episodes/zidane/zidane.py output/zidane
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from story import *
import engine

TITLE = "~/légendes $ ./zinedine_zidane"
SLUG = "zidane_legende"
VOICE = [os.path.join(HERE, "voix", f"scene_{i}.mp3") for i in range(1, 13)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
ALIGN = os.path.join(HERE, "alignement.json")
PAD = 0.15
WS, TEXTS = load_words(ALIGN)
def w(i, word, n=1, end=False):
    """Temps local (dans la scène i) où la voix prononce `word`."""
    return PAD + WS[i-1](word, n, end)

KITS["work"] = dict(kind="plain", c1=(62, 92, 140), sleeve=(62, 92, 140), shorts=(62, 92, 140), socks=(62, 92, 140), trim=(250, 250, 246), pants=True)

ZZ = Player("zz", hair=(46, 36, 30), skin=(210, 164, 126), hair_style="bald")
MATE = Player("mate", hair=(30, 26, 24), beard_col=(40, 34, 30), skin=(226, 180, 144))
DAD = Player("zdad", hair=(40, 34, 30), skin=(200, 152, 116))
PRES = Player("pres", hair=(214, 212, 206), skin=(236, 190, 156))
GK = Player("gk", hair=(60, 46, 36), skin=(232, 186, 150))
BRA = Player("bra", hair=(28, 24, 22), skin=(150, 104, 76))
SAU = Player("sau", hair=(26, 24, 22), skin=(190, 142, 104))
MATES = [Player("fr1", hair=(30, 26, 24), skin=(120, 84, 62)), Player("fr2", hair=(120, 84, 50), skin=(232, 186, 150))]
DESCH98 = Player("desch98", hair=(58, 44, 34), skin=(232, 188, 152))
DESCH18 = Player("desch18", hair=(206, 202, 196), skin=(232, 188, 152))
GOLD = (236, 186, 48)
BLEU, BLANC, ROUGE = (24, 44, 120), (250, 250, 246), (206, 32, 44)

# ------------------------------------------------------------------ objets
QM = Label("?", "zqm", font("title", 300), PAL["mustard"], None, stroke=7, stroke_fill=PAL["ink"])
REDCARD = Paper(rect_pts(150, 210), (214, 28, 40), "redcard", rough=1.2)
SLEEVE = Paper(rect_pts(84, 560), (34, 32, 32), "refsleeve", rough=1.4)
def red_card(cv, fr, t, t0, x=820, y=700, s=1.0):
    """Bras de l'arbitre qui brandit le carton rouge (monte depuis le bas)."""
    if t < t0: return
    u = ease_out_back(prog(t, t0, .25), 1.6); yy = lerp(y + 1000, y, u)
    SLEEVE.draw(cv, fr, x + 40*s, yy + 400*s, s, 6)
    REDCARD.draw(cv, fr, x, yy, s, -8)
    ImageDraw.Draw(cv).ellipse([x - 30*s, yy + 70*s, x + 60*s, yy + 150*s], fill=SKIN)

def stadium(cv, fr, key, t=0.0, sky=(18, 22, 46), grass=(46, 112, 64), horizon=1060):
    """Stade de nuit : tribunes (têtes qui bougent, flashs), projecteurs, pelouse rayée."""
    stage_fill(cv, fr, sky, key); d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    rnd = random.Random(key)
    for row in range(7):
        ry = 560 + row*68; n = 18 + row
        for k in range(n):
            x = 50 + k*(980/(n-1)); jump = 5*abs(math.sin(t*6 + k*1.3 + row))
            col = rnd.choice([(90, 96, 120), (130, 120, 110), (200, 196, 190), (60, 64, 90), (160, 60, 60), (70, 90, 150)])
            d.ellipse([x-17, ry-17-jump, x+17, ry+17-jump], fill=col)
    for fx in (150, 930):
        for r, c in ((70, (70, 70, 60)), (46, (200, 196, 150)), (26, (255, 252, 230))): d.ellipse([fx-r, 300-r, fx+r, 300+r], fill=c)
    for k in range(8):
        y0 = horizon + k*(sy1-horizon)/8
        d.rectangle([sx0, y0, sx1, y0 + (sy1-horizon)/8 + 1], fill=grass if k % 2 == 0 else tuple(int(c*.9) for c in grass))
    d.line([(sx0, horizon), (sx1, horizon)], fill=(230, 236, 226), width=6)
    if int(t*24) % 7 == 0:   # petit flash dans la tribune
        x, y = rnd.uniform(80, 1000), rnd.uniform(540, 980); d.ellipse([x-9, y-9, x+9, y+9], fill=(255, 255, 250))

def duel(cv, fr, t, t_hit, zx=400, mx=610, s=1.0, zkit="france_w", zmood="determined", mood_m="happy", stars=True):
    """Zidane met un coup de tête (lean + plongeon), Materazzi tombe à la renverse."""
    u_in = prog(t, t_hit - .14, .14); u_out = prog(t, t_hit + .4, .4)
    lean = 80*ease_in_cubic(u_in)*(1 - ease_out_cubic(u_out)); dip = 34*u_in*(1 - u_out)
    fall = ease_out_cubic(prog(t, t_hit, .45))
    if fall <= 0:
        MATE.draw(cv, fr, mx, 1560, s*1.06, age=1, kit="italy", mood=mood_m, t=t, beard=True, look=(-1, 0))
    else:
        L = MATE.render_layer(fr, s*1.06, age=1, kit="italy", mood="surprised", beard=True)
        blit(cv, L, mx + 110*fall, 1560, 1, -82*fall)
    ZZ.draw(cv, fr, zx, 1560 + dip, s, age=1, kit=zkit, mood=zmood, t=t, lean=lean, look=(1, 0))
    if stars and t_hit <= t < t_hit + .35:   # étoiles d'impact
        u = prog(t, t_hit, .35)
        for k in range(6):
            a = k*math.pi/3 + .3; r = 40 + 110*u
            draw_star(cv, zx + 130*s + r*math.cos(a), 1560 - 520*s + r*math.sin(a), 26*(1-u), 1, t*6, (255, 236, 150))

def beam(cv, apex, pts, a=.35, col=(255, 244, 200)):
    """Faisceau lumineux semi-transparent (projecteur)."""
    L = Image.new("RGBA", cv.size, (0, 0, 0, 0)); ImageDraw.Draw(L).polygon([apex] + pts, fill=(*col, int(255*a)))
    cv.paste(L, (0, 0), L)

def _building_decor(cols, rows, lit):
    def dec(d, a):
        ax, ay = a; rnd = random.Random(cols*rows)
        for i in range(cols):
            for j in range(rows):
                x = ax - (cols-1)*38 + i*76; y = ay - (rows-1)*44 + j*88
                d.rectangle([x-22, y-26, x+22, y+26], fill=(250, 214, 120) if rnd.random() < lit else (70, 90, 120))
                d.line([(x-30, y+32), (x+30, y+32)], fill=(120, 110, 100), width=4)
    return dec
def building(key, cols, rows, col, lit=.25):
    return Paper(rect_pts(cols*76 + 40, rows*88 + 40), col, key, rough=1.6, hatch=True).add(_building_decor(cols, rows, lit))
HLM = [building("hlm1", 3, 10, (226, 200, 170)), building("hlm2", 4, 12, (206, 186, 160)), building("hlm3", 3, 8, (234, 214, 186))]
HLM_N = [building("hlm1n", 3, 10, (120, 100, 110), .5), building("hlm2n", 4, 12, (104, 90, 104), .5), building("hlm3n", 3, 8, (130, 110, 120), .5)]

def _basilica_decor(d, a):
    ax, ay = a
    d.ellipse([ax-12, ay-300, ax+12, ay-270], fill=GOLD); d.rectangle([ax-5, ay-274, ax+5, ay-250], fill=GOLD)
    for k in range(3): d.rectangle([ax-100+k*80, ay-70, ax-80+k*80, ay-30], fill=(150, 120, 100))
    d.rectangle([ax-8, ay-230, ax+8, ay-200], fill=(150, 120, 100))
BASILICA = Paper(poly_pts([(-120, 0), (-120, -90), (-40, -90), (-40, -170), (-22, -170), (-22, -250), (22, -250), (22, -170), (40, -170), (40, -90), (120, -90), (120, 0)]),
                 (236, 220, 196), "basilica", rough=1.4, hatch=True, pad=70).add(_basilica_decor)
HILL = Paper(poly_pts([(-420, 120), (-360, 10), (-220, -60), (-60, -90), (80, -70), (240, -20), (380, 60), (420, 120)]), (150, 150, 96), "hill", rough=4, hatch=True)
SUN = Paper(ellipse_pts(200, 200, 40), PAL["mustard"], "zsun", rough=2)
BOX = Paper(rect_pts(170, 130), (196, 150, 100), "zbox", rough=1.6, hatch=True).add(
    lambda d, a: [d.rectangle([a[0]-12, a[1]-65, a[0]+12, a[1]+65], fill=(226, 200, 150)), d.line([(a[0]-85, a[1]-30), (a[0]+85, a[1]-30)], fill=(160, 120, 80), width=3)])
SHELF = Paper(rect_pts(1000, 26), (120, 86, 60), "zshelf", rough=1.4)
def _palm_decor(d, a):
    ax, ay = a; top = (ax, ay-330)
    for k in range(7):
        an = math.pi*(1.05 + k*.15)
        tip = (top[0] + 190*math.cos(an), top[1] + 150*math.sin(an) + 60*abs(math.cos(an)))
        mid = ((top[0]+tip[0])/2, (top[1]+tip[1])/2 - 30)
        d.polygon([top, (mid[0]-18, mid[1]-10), tip, (mid[0]+18, mid[1]+14)], fill=(52, 130, 70))
PALM = Paper(poly_pts([(-16, 0), (16, 0), (10, -170), (2, -340), (-10, -340), (-8, -170)]), (150, 106, 64), "palm", rough=1.4, hatch=True, pad=200).add(_palm_decor)
CANNES = Paper(rect_pts(560, 140), (200, 30, 40), "cannesban", rough=2.4, hatch=True).add(
    lambda d, a: d.text((a[0], a[1]), "CANNES", font=font("title", 96), fill=(250, 250, 246), anchor="mm", stroke_width=5, stroke_fill=(150, 20, 30)))
SUITCASE = Paper(rect_pts(120, 90), (150, 96, 60), "zsuitcase", rough=1.6, hatch=True).add(
    lambda d, a: [d.rectangle([a[0]-24, a[1]-62, a[0]+24, a[1]-44], outline=(90, 56, 36), width=8), d.line([(a[0]-60, a[1]), (a[0]+60, a[1])], fill=(110, 70, 44), width=5)])
DESK = Paper(rect_pts(600, 250), (120, 80, 52), "zdesk", rough=1.6, hatch=True).add(
    lambda d, a: d.rectangle([a[0]-280, a[1]-125, a[0]+280, a[1]-105], fill=(150, 104, 70)))
WINDOW = Paper(rect_pts(320, 380), (150, 200, 230), "zwin", rough=2).add(
    lambda d, a: [d.rectangle([a[0]-160, a[1]-190, a[0]+160, a[1]+190], outline=(250, 250, 246), width=16), d.line([(a[0], a[1]-190), (a[0], a[1]+190)], fill=(250, 250, 246), width=10)])

def _clio_decor(d, a):
    ax, ay = a
    d.polygon([(ax-70, ay-98), (ax+64, ay-100), (ax+124, ay-46), (ax-114, ay-42)], fill=(170, 210, 230))
    d.line([(ax-4, ay-100), (ax-4, ay+40)], fill=(150, 18, 28), width=6)
    d.line([(ax-110, ay-42), (ax-110, ay+36)], fill=(150, 18, 28), width=4)
    d.ellipse([ax+206, ay-22, ax+236, ay+2], fill=(255, 240, 180)); d.rectangle([ax-244, ay+26, ax+246, ay+40], fill=(60, 58, 62))
CLIO = Paper(poly_pts([(-240, 46), (-246, -4), (-222, -32), (-130, -44), (-78, -110), (70, -114), (150, -50), (236, -30), (248, 46)]),
             (206, 26, 38), "clio", rough=1.6, hatch=True, pad=40).add(_clio_decor)
def draw_clio(cv, fr, x, y, s=1.0, t=0.0, bow=True):
    CLIO.draw(cv, fr, x, y, s); d = ImageDraw.Draw(cv)
    for wx in (-150, 150):
        cx, cy, r = x + wx*s, y + 52*s, 48*s
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(34, 32, 36)); d.ellipse([cx-r*.45, cy-r*.45, cx+r*.45, cy+r*.45], fill=(190, 190, 196))
        an = -t*14; d.line([(cx, cy), (cx + r*.4*math.cos(an), cy + r*.4*math.sin(an))], fill=(60, 60, 66), width=max(2, int(5*s)))
    if bow:
        bx, by = x - 4*s, y - 118*s
        d.polygon([(bx, by), (bx-60*s, by-34*s), (bx-60*s, by+26*s)], fill=GOLD); d.polygon([(bx, by), (bx+60*s, by-34*s), (bx+60*s, by+26*s)], fill=GOLD)
        d.ellipse([bx-16*s, by-16*s, bx+16*s, by+16*s], fill=(250, 214, 90))

def _arc_decor(d, a):
    ax, ay = a; night = (22, 26, 58); stone = (164, 150, 124)
    d.rectangle([ax-80, ay+20, ax+80, ay+300], fill=night); d.ellipse([ax-80, ay-60, ax+80, ay+100], fill=night)
    d.rectangle([ax-270, ay-240, ax+270, ay-214], fill=stone); d.line([(ax-262, ay-170), (ax+262, ay-170)], fill=stone, width=6)
    for sg in (-1, 1): d.rectangle([ax+sg*180-50, ay+40, ax+sg*180+50, ay+180], outline=stone, width=4)
ARC = Paper(rect_pts(540, 600), (206, 192, 164), "arc", rough=2, hatch=True, pad=30).add(_arc_decor)

def _boot_decor(d, a):
    ax, ay = a
    for k in range(3): d.line([(ax-10+k*14, ay-10), (ax+8+k*14, ay+30)], fill=(250, 250, 246), width=5)
    for k in range(4): d.rectangle([ax-30+k*30, ay+60, ax-22+k*30, ay+72], fill=(200, 200, 200))
BOOT = Paper(poly_pts([(-34, -70), (18, -70), (22, 16), (84, 28), (96, 60), (-38, 60)]), (30, 28, 30), "boot", rough=1.2, pad=30).add(_boot_decor)

def _doc_decor(d, a):
    ax, ay = a
    d.text((ax, ay-200), "CONTRAT", font=font("title", 60), fill=PAL["ink"], anchor="mm")
    for k in range(7): d.line([(ax-160, ay-120+k*42), (ax+(160 if k % 3 else 90), ay-120+k*42)], fill=(170, 164, 150), width=5)
    d.line([(ax-160, ay+200), (ax+20, ay+200)], fill=(120, 116, 110), width=3)
DOC = Paper(rect_pts(420, 520), (250, 248, 238), "zdoc", rough=1.6).add(_doc_decor)
PEDESTAL = Paper(rect_pts(260, 300), (60, 58, 64), "pedestal", rough=1.6, hatch=True)
JB10 = jersey_back("france", "ZIDANE", 10, key="jbzz10"); JBW = jersey_back("france_w", "ZIDANE", 10, key="jbzzw")

def zz_back(cv, fr, x, y, s=1.0, bob=0.0):
    """Zidane vu de dos (tireur du penalty) : maillot blanc floqué + crâne rasé."""
    JBW.draw(cv, fr, x, y + bob, s)
    hx, hy = x, y + bob - 236*s - 70*s
    ZZ.neck.draw(cv, fr, hx, hy + 60*s, s*1.3)
    ZZ.head.draw(cv, fr, hx, hy, s*1.35)
    ImageDraw.Draw(cv).chord([hx-70*s, hy-40*s, hx+70*s, hy+84*s], 20, 160, fill=ZZ.hair_col)

SCOREBOARD = scoreboard_sprite(820, 330, "zscore")
def score2(cv, fr, x, y, la, lb, a, b, sub="", s=1.0):
    if s <= .02: return
    L = layer(900, 420, (450, 210)); SCOREBOARD.draw(L, fr, 450, 210, 1, 0, 1)
    d = ImageDraw.Draw(L)
    d.text((180, 130), la, font=font("mono", 64), fill=(200, 196, 190), anchor="mm"); d.text((720, 130), lb, font=font("mono", 64), fill=(200, 196, 190), anchor="mm")
    d.text((450, 220), f"{a} - {b}", font=font("title", 150), fill=(255, 204, 70), anchor="mm")
    if sub: d.text((450, 330), sub, font=font("mono", 40), fill=(170, 166, 160), anchor="mm")
    blit(cv, L, x, y, s)

def walk(t, speed=9, amp=22):
    ph = math.sin(t*speed); return (amp*ph, -amp*ph), abs(math.sin(t*speed))*8

def mustache(cv, eyes, s, col=(40, 34, 30)):
    if not eyes: return
    (x1, y1), (x2, y2) = eyes; hx = (x1+x2)/2; hy = (y1+y2)/2 - 8*s
    ImageDraw.Draw(cv).polygon([(hx-30*s, hy+34*s), (hx-20*s, hy+22*s), (hx, hy+24*s), (hx+20*s, hy+22*s), (hx+30*s, hy+34*s), (hx, hy+30*s)], fill=col)

# ------------------------------------------------------------------ labels
H1 = HL("FINALE · COUPE DU MONDE", "zh1", PAL["mustard"], PAL["ink"], 72)
K1a = KW("2006", "zk1a", ROUGE, size=170); K1b = KW("SON DERNIER MATCH", "zk1b", PAL["ink"], size=84)
K1c = STAMP("CARTON ROUGE", "zk1c", ROUGE, 120); K1d = KW("COMMENT ?!", "zk1d", PAL["mustard"], PAL["ink"], 120)
K2a = KW("MARSEILLE", "zk2a", (30, 110, 160), size=130); K2b = KW("1972", "zk2b", PAL["mustard"], PAL["ink"], 150)
N2 = STAMP("ZINÉDINE ZIDANE", "zn2", BLEU, 104)
T2a = TAG("la Castellane", "zt2a", PAL["paper"]); T2b = TAG("quartiers nord", "zt2b", PAL["mustard"])
K2c = KW("SON PÈRE", "zk2c", PAL["ink"], size=110); T2c = TAG("arrivé de Kabylie (Algérie)", "zt2c", PAL["paper"], size=50)
K2d = KW("MAGASINIER", "zk2d", (62, 92, 140), size=110)
K2e = KW("TOUTE LA JOURNÉE", "zk2e", PAL["ink"], size=90); T2d = TAG("au pied des immeubles", "zt2d", PAL["paper"], size=50)
K3a = KW("14 ANS", "zk3a", PAL["ink"], size=130); T3a = TAG("centre de formation", "zt3a", PAL["paper"])
T3b = TAG("loin de sa famille", "zt3b", PAL["mustard"])
T3c = TAG("le président du club", "zt3c", PAL["paper"]); K3b = KW("UNE VOITURE ?!", "zk3b", ROUGE, size=100)
K3c = KW("1991", "zk3c", PAL["mustard"], PAL["ink"], 170); K3d = KW("SON 1er BUT !", "zk3d", PAL["ink"], size=100)
K3e = KW("CLIO ROUGE", "zk3e", ROUGE, size=130); T3d = TAG("toute neuve !", "zt3d", PAL["mustard"], size=60)
K4a = KW("1998", "zk4a", ROUGE, size=200); K4b = KW("COUPE DU MONDE", "zk4b", PAL["cream"], BLEU, 96); T4a = TAG("à la maison !", "zt4a", PAL["mustard"], size=60)
T4b = TAG("contre l'Arabie saoudite", "zt4b", PAL["paper"]); K4c = KW("IL PÈTE LES PLOMBS", "zk4c", PAL["ink"], size=84)
K4d = STAMP("CARTON ROUGE", "zk4d", ROUGE, 120); T4c = TAG("2 matchs de suspension", "zt4c", PAL["paper"], size=52)
K5a = STAMP("FINALE", "zk5a", PAL["ink"], 130); K5b = KW("DE LA TÊTE !", "zk5b", PAL["ink"], size=110); K5c = KW("2 BUTS !", "zk5c", ROUGE, size=130)
K5d = STAMP("CHAMPIONS DU MONDE !", "zk5d", BLEU, 74)
K5e = KW("ZIDANE PRÉSIDENT", "zk5e", None, (255, 240, 190), 104); T5a = TAG("sur l'Arc de Triomphe", "zt5a", PAL["paper"], size=52)
K6a = KW("ATTENDS !", "zk6a", PAL["ink"], size=90); K6b = KW("LE PROCHAIN ?", "zk6b", ROUGE, size=78)
T6a = TAG("avant la suite…", "zt6a", PAL["paper"], size=56)
NAMES = [LBL(n, f"znm{n}", font("hand", 46), PAL["ink"], None) for n in ("Mbappé ?", "Henry ?", "Kaká ?", "Neymar ?")]
K6c = KW("EN COMMENTAIRE", "zk6c", PAL["teal"], size=84); K6d = KW("ON CONTINUE !", "zk6d", PAL["ink"], size=84)
CARD = Paper(rect_pts(200, 250), PAL["paper"], "zcard", rough=2)
K7a = KW("2001", "zk7a", GOLD, PAL["ink"], 150); T7a = TAG("plus de", "zt7a", PAL["paper"], size=50)
K7b = STAMP("RECORD DU MONDE", "zk7b", (190, 150, 20), 100)
K7c = KW("LIGUE DES CHAMPIONS", "zk7c", PAL["ink"], size=80); T7b = TAG("finale 2002, Glasgow", "zt7b", PAL["paper"], size=50)
K7d = KW("DU GAUCHE !", "zk7d", PAL["mustard"], PAL["ink"], 110); K7e = STAMP("LÉGENDAIRE", "zk7e", ROUGE, 110)
T8a = TAG("2004 : il arrête les Bleus", "zt8a", PAL["paper"], size=54); K8a = KW("IL REVIENT !", "zk8a", ROUGE, size=120)
T8b = TAG("2005", "zt8b", PAL["mustard"], size=60); K8b = KW("FINALE 2006", "zk8b", PAL["ink"], size=110)
K8c = KW("PANENKA", "zk8c", PAL["mustard"], PAL["ink"], 130); K8d = KW("BUT !", "zk8d", ROUGE, size=150)
T8c = TAG("la barre… et dedans !", "zt8c", PAL["paper"], size=50)
K9a = KW("110e MINUTE", "zk9a", PAL["ink"], size=110); T9a = TAG("Marco Materazzi", "zt9a", PAL["paper"], size=50)
T9b = TAG("il parle de sa sœur", "zt9b", PAL["mustard"], size=56); K9b = STAMP("CARTON ROUGE", "zk9b", ROUGE, 120)
T9c = TAG("sans la regarder", "zt9c", PAL["paper"], size=58); K9c = KW("LA FRANCE PERD", "zk9c", PAL["ink"], size=100)
K10a = KW("IL RACCROCHE", "zk10a", PAL["ink"], size=110); T10a = TAG("2006", "zt10a", PAL["paper"], size=56)
K10b = KW("ENTRAÎNEUR", "zk10b", PAL["mustard"], PAL["ink"], 120)
K10c = KW("REAL MADRID", "zk10c", PAL["ink"], size=100); K10d = KW("3 D'AFFILÉE", "zk10d", GOLD, PAL["ink"], 120)
K10e = STAMP("DU JAMAIS VU", "zk10e", ROUGE, 110)
YEARS10 = [LBL(str(y), f"zy{y}", font("title", 50), PAL["ink"], PAL["paper"], padx=14, pady=4) for y in (2016, 2017, 2018)]
K11a = KW("2026", "zk11a", ROUGE, size=150); K11b = STAMP("SÉLECTIONNEUR", "zk11b", BLEU, 104)
T11a = TAG("de l'équipe de France", "zt11a", PAL["paper"], size=54); K11c = STAMP("JUSQU'EN 2030", "zk11c", ROUGE, 64)
K12a = KW("DESCHAMPS", "zk12a", BLEU, size=110); T12a = TAG("champion du monde…", "zt12a", PAL["paper"], size=52)
K12b = KW("ET ZIZOU ?", "zk12b", ROUGE, size=120)
L12 = {k: LBL(k, "zl12"+k, font("hand", 44), PAL["ink"], PAL["paper"], padx=14, pady=6) for k in
       ("joueur · 1998", "sélectionneur · 2018", "sélectionneur · 20??")}
BTN_OUI = Label("OUI", "zboui", font("title", 110), PAL["cream"], PAL["teal"], padx=60, pady=10, rough=3)
BTN_NON = Label("NON", "zbnon", font("title", 110), PAL["cream"], PAL["coral"], padx=60, pady=10, rough=3)
BTN_SUB = Label("+ ABONNE-TOI", "zbsub", font("title", 96), (255, 255, 255), (230, 40, 80), padx=40, pady=14, rough=2.5)
K12c = KW("PROCHAINE LÉGENDE ?", "zk12c", PAL["ink"], size=80)

# ------------------------------------------------------------------ SCÈNE 1 — cold open : le coup de tête, puis rembobinage
def s1_world(cv, fr, t, overlays=True):
    stadium(cv, fr, "s1stad", t)
    t_hit = w(1, "tête") - .05
    duel(cv, fr, t, t_hit)
    red_card(cv, fr, t, w(1, "Carton"))
    if not overlays: return
    tx = w(1, "il") - .1
    hl(cv, fr, H1, t, -.25, tx)
    kw(cv, fr, K1a, t, w(1, "deux"), tx, CX, 520, -3)
    kw(cv, fr, K1b, t, w(1, "dernier"), tx, CX, 690, 2)
    show_stamp(cv, fr, K1c, t, w(1, "Carton"), CX, 460, -5, t_out=w(1, "Comment") - .28)

def s1(cv, fr, t, T):
    tc = w(1, "Comment"); tr = w(1, "On")
    if t < tc:
        s1_world(cv, fr, t)
        zoom_punch(cv, 1 + .07*ease_io(prog(t, w(1, "Et"), 1.2)))
        t_hit = w(1, "tête") - .05
        impact(cv, t, t_hit, 26); flashes(cv, t, t_hit, .15, .9); impact(cv, t, w(1, "Carton"), 14)
    elif t < tr:   # arrêt sur image, passage au noir et blanc
        s1_world(cv, fr, tc)
        grayscale(cv, prog(t, tc, .3)); red_card(cv, fr, t, w(1, "Carton"))   # seul le carton reste en couleur
        zoom_punch(cv, 1.07 + .03*prog(t, tc, 1.5))
        kw(cv, fr, K1d, t, tc, None, CX, 460, -4)
        QM.draw(cv, fr, 250, 700 + 10*math.sin(t*5), pop_in(t, w(1, "ça")), -10)
        glitch(cv, fr, t, tc, .3, 14)
    else:          # rembobinage VHS : le film repart à l'envers jusqu'en 1972
        tt = max(0.0, tc - (t - tr)*3.2)
        s1_world(cv, fr, tt, overlays=False); grayscale(cv, .6)
        u = prog(t, tr + .1, T - tr - .25)
        yr = int(round(lerp(2006, 1972, ease_in_cubic(u) if u < 1 else 1)))
        vhs(cv, fr, t, 1.0, "REW", stamp=None)
        LBL(str(yr), "zyr", font("title", 230), (250, 250, 246), None, stroke=8, stroke_fill=(20, 20, 30)).draw(cv, fr, CX, 820, pop_in(t, tr, .2), -2)

# ------------------------------------------------------------------ SCÈNE 2 — Marseille, la Castellane, le père
def s2a(cv, fr, t):
    stage_fill(cv, fr, (250, 196, 140), "zs2sky"); d = ImageDraw.Draw(cv)
    SUN.draw(cv, fr, 820, 560, 1)
    d.rectangle([30, 1180, 1050, 1890], fill=(56, 124, 168))
    for k in range(8):
        yy = 1220 + k*80
        pencil_line(d, [(60+j*48, yy+8*math.sin(j*.8+t*2+k)) for j in range(22)], 1, (110, 170, 200), 4, k, .6)
    HILL.draw(cv, fr, 340, 1110, 1.1); BASILICA.draw(cv, fr, 330, 1030, .9)
    kw(cv, fr, K2a, t, .05, None, CX, 440, -3)
    kw(cv, fr, K2b, t, w(2, "mille"), None, 760, 640, 4)

def s2b(cv, fr, t):
    stage_fill(cv, fr, (170, 206, 226), "zs2b"); d = ImageDraw.Draw(cv)
    for P, x, y in zip(HLM, (190, 540, 890), (1520, 1520, 1520)):
        P.draw(cv, fr, x, y - (P.v[0].height/2 - 30), 1)
    d.rectangle([30, 1500, 1050, 1890], fill=(150, 146, 140))
    ZZ.draw(cv, fr, CX, 1690, 1.05, age=0, kit="street", mood="happy", t=t)
    show_stamp(cv, fr, N2, t, w(2, "Zinédine"), CX, 400, -4)
    show(cv, fr, T2a, t, w(2, "Castellane"), None, 300, 600, -3)
    show(cv, fr, T2b, t, w(2, "quartiers"), None, 740, 720, 3)

def s2c(cv, fr, t):
    stage_fill(cv, fr, (150, 140, 128), "zs2c")
    for k in range(3): SHELF.draw(cv, fr, CX, 760 + k*300, 1)
    for k in range(3):
        for j in range(4):
            if (k + j) % 3: BOX.draw(cv, fr, 170 + j*240, 680 + k*300, .9, (j - 1.5)*2)
    tp = w(2, "père"); x = lerp(1250, 620, ease_out_cubic(prog(t, tp - .5, .8))); lg, bob = walk(t, 8, 18)
    eyes = DAD.draw(cv, fr, x, 1640 - bob, 1.05, age=1, kit="work", mood="happy", t=t, legs=lg, arms=(-10, -10))
    mustache(cv, eyes, 1.05)
    BOX.draw(cv, fr, x, 1640 - bob - 360, 1.0)
    kw(cv, fr, K2c, t, tp, None, CX, 420, -3)
    show(cv, fr, T2c, t, w(2, "Kabylie"), None, CX, 560, 2)
    kw(cv, fr, K2d, t, w(2, "magasinier"), None, 330, 740, -5)

def s2d(cv, fr, t):
    stage_fill(cv, fr, (246, 160, 110), "zs2d"); d = ImageDraw.Draw(cv)
    for P, x in zip(HLM_N, (160, 540, 920)): P.draw(cv, fr, x, 1500 - (P.v[0].height/2 - 30), 1)
    d.rectangle([30, 1480, 1050, 1890], fill=(130, 120, 116))
    t0 = w(2, "Et") - .1; ph = ((t - t0)*2.2) % 1.0
    kick = max(0.0, math.cos(ph*math.pi*2))**6
    ZZ.draw(cv, fr, 470, 1680, 1.1, age=0, kit="street", mood="happy", t=t, legs=(0, -35*kick), look=(1, -1))
    bx, by = 560, 1560 - 520*4*ph*(1 - ph)
    draw_ball(cv, fr, bx, by, .5, t*400)
    n = 8 + int((t - t0)*2.2)
    LBL(f"x{n}", "zjug", font("title", 110), PAL["ink"], PAL["mustard"], padx=20, pady=4, rough=2).draw(cv, fr, 820, 980, pop_in(t, t0 + .3), 6)
    kw(cv, fr, K2e, t, w(2, "journées"), None, CX, 440, -3)
    show(cv, fr, T2d, t, w(2, "pied"), None, CX, 600, 2)

def s2(cv, fr, t, T):
    shots(cv, fr, t, [(0, s2a), (w(2, "Zinédine") - .1, s2b), (w(2, "Son") - .1, s2c), (w(2, "Et") - .1, s2d)])
    impact(cv, t, w(2, "Zinédine"), 14); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 3 — Cannes, la promesse, la Clio
def s3a(cv, fr, t):
    stage_fill(cv, fr, (160, 206, 232), "zs3a"); d = ImageDraw.Draw(cv)
    d.rectangle([30, 1100, 1050, 1300], fill=(60, 140, 180)); d.rectangle([30, 1300, 1050, 1890], fill=(236, 214, 170))
    PALM.draw(cv, fr, 150, 1330, 1.1); PALM.draw(cv, fr, 950, 1300, .95)
    tc = w(3, "Cannes")
    CANNES.draw(cv, fr, CX, 820, pop_in(t, tc - .1), -3)
    x = lerp(-150, 560, ease_out_cubic(prog(t, .05, 1.8))); lg, bob = walk(t) if t < 1.9 else ((0, 0), 0)
    su = prog(t, tc, .45)
    if 0 < su < 1:
        L = ZZ.render_layer(fr, .85, age=.35, kit="street" if su < .25 else "cannes", mood="happy")
        blit_sxy(cv, L, x, 1600, max(.04, abs(math.cos(su*math.pi*2))), 1)
    else:
        ZZ.draw(cv, fr, x, 1600 - bob, .85, age=.35, kit="cannes" if su >= 1 else "street", legs=lg, mood="normal" if t < tc else "happy", t=t)
    if su < .2: SUITCASE.draw(cv, fr, x + 125, 1370 - bob, .9, 4)
    kw(cv, fr, K3a, t, w(3, "quatorze"), None, 300, 420, -4)
    show(cv, fr, T3a, t, w(3, "centre"), None, 740, 540, 3)
    show(cv, fr, T3b, t, w(3, "loin"), None, 330, 620, -2)

def s3b(cv, fr, t):
    stage_fill(cv, fr, (232, 214, 186), "zs3b")
    WINDOW.draw(cv, fr, 220, 760, 1)
    PRES.draw(cv, fr, 700, 1560, 1.0, age=1, kit="suit", mood="happy", t=t, arms=(20, 60 + 20*math.sin(t*6)))
    DESK.draw(cv, fr, 700, 1480, 1)
    ZZ.draw(cv, fr, 250, 1640, .9, age=.5, kit="cannes", mood="surprised" if t > w(3, "voiture") else "normal", t=t, look=(1, 0))
    show(cv, fr, T3c, t, w(3, "président"), w(3, "voiture") - .1, CX, 440, -2)
    tp = w(3, "promet")
    if t > tp:
        txt = typewriter("Ton 1er but… et je t'offre une voiture !", prog(t, tp + .1, 1.6)) or " "
        speech_bubble(cv, fr, "zpromise", txt, 560, 700, pop_in(t, tp), (1, 1), 54)
    kw(cv, fr, K3b, t, w(3, "voiture"), None, CX, 440, -4)

def s3c(cv, fr, t):
    pitch(cv, fr, "zp3")
    tm = w(3, "marque")
    draw_goal(cv, fr, 790, 1260, 400, 240, prog(t, tm, .5), 1, t)
    kick = math.sin(prog(t, tm - .4, .3)*math.pi)
    ZZ.draw(cv, fr, 330, 1600, 1.0, age=.75, kit="cannes", kid_hair=True, mood="cheer" if t > tm else "determined", t=t,
            legs=(0, 50*kick), arms=(150, 150) if t > tm + .1 else (20, 20))
    if t < tm + .1:
        u = prog(t, tm - .3, .3); p = bezier((400, 1570), (600, 1300), (760, 1160), u)
        draw_ball(cv, fr, p[0], p[1], .55, t*800)
    kw(cv, fr, K3c, t, w(3, "mille"), None, CX, 440, -4)
    kw(cv, fr, K3d, t, tm, None, CX, 640, 3)
    if t > tm: confetti(cv, fr, "zc3", t - tm, 40, 3)

def s3d(cv, fr, t):
    stage_fill(cv, fr, (170, 214, 236), "zs3d"); d = ImageDraw.Draw(cv)
    PALM.draw(cv, fr, 900, 1330, 1.0)
    d.rectangle([30, 1330, 1050, 1890], fill=(96, 96, 104))
    for k in range(6): d.rectangle([60 + k*190, 1560, 160 + k*190, 1578], fill=(240, 236, 220))
    tc = w(3, "Clio")
    x = lerp(1400, 600, ease_out_cubic(prog(t, tc - .7, .8)))
    draw_clio(cv, fr, x, 1400, 1.2, t if t < tc + .1 else tc + .1)
    if t > tc:
        for k in range(5):
            a = k*1.3 + t*2; draw_star(cv, 600 + 330*math.cos(a), 1320 + 150*math.sin(a), 22, pop_in(t, tc + k*.08), t*3)
    ZZ.draw(cv, fr, 230, 1640, .95, age=.75, kit="street", kid_hair=True, mood="cheer" if t > tc else "surprised", t=t,
            arms=(150, 150) if t > tc else (20, 20))
    kw(cv, fr, K3e, t, tc, None, CX, 440, -4)
    show(cv, fr, T3d, t, w(3, "toute"), None, CX, 620, 3)

def s3(cv, fr, t, T):
    shots(cv, fr, t, [(0, s3a), (w(3, "Le") - .1, s3b), (w(3, "En") - .1, s3c), (w(3, "et", 2) - .1, s3d)])
    impact(cv, t, w(3, "marque"), 16); punch(cv, t, w(3, "Clio"), 1.07); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 4 — 1998, carton rouge
def s4a(cv, fr, t):
    stage_fill(cv, fr, BLEU, "zs4a")
    rays(cv, (CX, 1100), t, .6, 14, 1400, (60, 90, 170))
    fr_flag(cv, CX, 1080, 720, 440, 1, t)
    ZZ.draw(cv, fr, CX, 1650, 1.05, age=1, kit="france", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
    kw(cv, fr, K4a, t, .05, None, CX, 420, -4)
    kw(cv, fr, K4b, t, w(4, "Coupe"), None, CX, 620, 3)
    show(cv, fr, T4a, t, w(4, "maison"), None, 760, 760, 4)

def s4b(cv, fr, t):
    pitch(cv, fr, "zp4")
    tp = w(4, "pète"); ts = w(4, "plombs")
    L = SAU.render_layer(fr, .9, age=1, kit="saudi", mood="sad")
    blit(cv, L, 860, 1570, 1, 88)
    raise_ = math.sin(prog(t, tp - .1, ts - tp + .1)*math.pi) if t < ts else 0
    ZZ.draw(cv, fr, 600, 1580, 1.0, age=1, kit="france", mood="determined" if t > tp - .2 else "normal", t=t, legs=(0, 45*raise_), look=(-1, 1))
    show(cv, fr, T4b, t, w(4, "Contre"), tp - .1, CX, 450, -2)
    kw(cv, fr, K4c, t, tp, w(4, "carton") - .05, CX, 620, 3)
    red_card(cv, fr, t, w(4, "carton"), 250, 860)
    show_stamp(cv, fr, K4d, t, w(4, "carton"), CX, 460, -5)
    show(cv, fr, T4c, t, w(4, "deux"), None, 640, 640, 3)

def s4(cv, fr, t, T):
    shots(cv, fr, t, [(0, s4a), (w(4, "Contre") - .1, s4b)])
    impact(cv, t, .05, 14); impact(cv, t, w(4, "plombs"), 20); glitch(cv, fr, t, w(4, "plombs"), .35, 18)
    impact(cv, t, w(4, "carton"), 16); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 5 — finale 98 : deux têtes, l'Arc de Triomphe
def s5a(cv, fr, t):
    stadium(cv, fr, "zs5stad", t, sky=(28, 34, 70))
    show_stamp(cv, fr, K5a, t, w(5, "finale"), CX, 460, -4)
    score2(cv, fr, CX, 820, "FRA", "BRA", 0, 0, "finale", pop_in(t, w(5, "Brésil") - .2))

def s5b(cv, fr, t):
    stadium(cv, fr, "zs5b", t, sky=(28, 34, 70), horizon=1000)
    t1 = w(5, "coups") + .1; t2 = w(5, "deux", 2) + .1
    hop = 0
    for th in (t1, t2): hop = max(hop, 130*math.sin(clamp((t - th + .3)/.6)*math.pi))
    draw_goal(cv, fr, 860, 1300, 330, 220, max(prog(t, t1 + .25, .5), prog(t, t2 + .25, .5)) if t > t1 + .25 else 0, 1, t)
    BRA.draw(cv, fr, 640, 1640 - hop*.5, .95, age=1, kit="brazil", mood="surprised", t=t, arms=(40, 40))
    zx, zy = 420, 1640 - hop
    ZZ.draw(cv, fr, zx, zy, 1.0, age=1, kit="france", mood="determined", t=t, arms=(40, 40), look=(-1, -1))
    hx, hy = zx, zy - 600
    for th, src, ctrl, goal in ((t1, (60, 300), (220, 200), (830, 1170)), (t2, (1020, 300), (820, 200), (900, 1160))):
        if th - .55 < t < th:
            p = bezier(src, ctrl, (hx + 20, hy - 20), prog(t, th - .55, .55)); draw_ball(cv, fr, p[0], p[1], .5, t*500)
        elif th <= t < th + .28:
            p = lerp_pt((hx + 20, hy - 20), goal, prog(t, th, .28)); draw_ball(cv, fr, p[0], p[1], .5, t*800)
            speed_lines(cv, fr, (hx, hy), .6, seed=int(th*10), inner=200)
    a = 1 if t > t2 + .28 else 0; b = 1 if t > t1 + .28 else 0
    score2(cv, fr, CX, 640, "FRA", "BRA", a + b, 0, "", .55)
    kw(cv, fr, K5b, t, w(5, "tête"), w(5, "buts") - .05, CX, 420, -4)
    kw(cv, fr, K5c, t, w(5, "buts"), None, CX, 420, 3)

def s5c(cv, fr, t):
    stage_fill(cv, fr, BLEU, "zs5c")
    tc = w(5, "championne")
    rays(cv, (CX, 900), t, 1.0, 16, 1400, (240, 200, 90))
    WC_TROPHY.draw(cv, fr, CX, 760, 1.3*pop_in(t, w(5, "France") - .15), 3*math.sin(t*3))
    ZZ.draw(cv, fr, CX, 1820, .8, age=1, kit="france", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
    show_stamp(cv, fr, K5d, t, tc, CX, 1150, -4)
    confetti(cv, fr, "zc5", t - tc, 80, 4)

def s5d(cv, fr, t):
    stage_fill(cv, fr, (22, 26, 58), "zs5night"); d = ImageDraw.Draw(cv)
    rnd = random.Random(55)
    for k in range(40):
        x, y = rnd.uniform(50, 1030), rnd.uniform(140, 800); r = 2 + 2*abs(math.sin(t*3 + k))
        d.ellipse([x-r, y-r, x+r, y+r], fill=(230, 230, 250))
    ARC.draw(cv, fr, CX, 1190, 1)
    ta = w(5, "s'affiche")
    if t > ta - .2:
        a = prog(t, ta - .2, .3)
        beam(cv, (130, 1880), [(CX - 170, 880), (CX + 150, 1140)], .3*a)
        s = 1.55*a
        ZZ.head.draw(cv, fr, CX, 1010, s); ZZ.hair_adult.draw(cv, fr, CX, 1010, s)
        if a > .9: ZZ.face(cv, CX, 1010, s, "happy", (0, 0), False, t, 0)
    for k in range(14):   # foule en liesse, drapeaux
        x = 60 + k*75; jump = 14*abs(math.sin(t*7 + k*1.9))
        d.ellipse([x-30, 1600-jump, x+30, 1660-jump], fill=(40, 40, 60)); d.rectangle([x-36, 1650-jump, x+36, 1890], fill=(40, 40, 60))
        if k % 3 == 1: fr_flag(cv, x + 30, 1470 - jump, 110, 70, 1, t + k)
    kw(cv, fr, K5e, t, ta, None, CX, 520, -3)
    show(cv, fr, T5a, t, w(5, "l'Arc"), None, CX, 680, 2)

def s5(cv, fr, t, T):
    shots(cv, fr, t, [(0, s5a), (w(5, "deux") - .1, s5b), (w(5, "La") - .1, s5c), (w(5, "son") - .1, s5d)])
    for th in (w(5, "coups") + .1, w(5, "deux", 2) + .1): impact(cv, t, th, 14)
    for tg in (w(5, "coups") + .38, w(5, "deux", 2) + .38): flashes(cv, t, tg, .12, .6)
    impact(cv, t, w(5, "championne"), 14); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 6 — PAUSE : le prochain joueur ?
def s6(cv, fr, t, T):
    stage_fill(cv, fr, PAL["teal"], "zs6"); d = ImageDraw.Draw(cv)
    kw(cv, fr, K6a, t, .05, None, 740, 330, 4)
    tp = w(6, "prochain")
    show(cv, fr, T6a, t, w(6, "Avant"), tp - .05, 730, 540, 3)
    kw(cv, fr, K6b, t, tp, None, 730, 540, -3)
    if t < tp + .1: QM.draw(cv, fr, CX, 1020 + 12*math.sin(t*5), win(t, w(6, "c'est"), tp - .05), 8)
    for i in range(4):
        a = pop_in(t, tp + i*.14)
        if a <= 0: continue
        x = 180 + i*240; y = 1010 + 10*math.sin(t*4 + i)
        CARD.draw(cv, fr, x, y, a, (-4, 3, -2, 5)[i])
        LBL("?", "zqmS", font("title", 130), (60, 56, 64), None).draw(cv, fr, x, y - 30, a)
        NAMES[i].draw(cv, fr, x, y + 90, a)
    te = w(6, "Écris")
    if t > te:
        a = pop_in(t, te)
        speech_bubble(cv, fr, "zcta_b", typewriter("Mbappé stp !!", prog(t, te + .2, .9)) or " ", 520, 1300, a, (-1, 1), 64)
        bx = 880 + 18*math.sin(t*8)
        arrow(d, (760, 1320), (bx + 80, 1180), prog(t, te + .2, .3), PAL["ink"], 10, 7, 34, -.2)
    kw(cv, fr, K6c, t, w(6, "commentaire"), None, 560, 1470, 2)
    kw(cv, fr, K6d, t, w(6, "Allez"), None, 730, 740, -5)
    impact(cv, t, w(6, "Allez"), 14)

def s6_post(cv, fr, t, T):
    """Par-dessus la photo figée : icône PAUSE."""
    a = pop_in(t, .25)
    if a <= 0: return
    d = ImageDraw.Draw(cv); cx, cy, s = 250, 470, a
    d.ellipse([cx-70*s, cy-70*s, cx+70*s, cy+70*s], fill=(34, 32, 36))
    for dx in (-22, 22): d.rectangle([cx+dx*s-12*s, cy-34*s, cx+dx*s+12*s, cy+34*s], fill=(250, 248, 240))

# ------------------------------------------------------------------ SCÈNE 7 — Real Madrid, la volée de Glasgow
def s7a(cv, fr, t):
    stage_fill(cv, fr, (246, 240, 226), "zs7a")
    rays(cv, (CX, 1000), t, .9, 16, 1400, (240, 210, 130))
    kw(cv, fr, K7a, t, .05, None, CX, 360, -3)
    tr = w(7, "Real"); su = prog(t, tr, .45)
    if 0 < su < 1:
        L = ZZ.render_layer(fr, 1.0, age=1, kit="juventus" if su < .25 else "real", mood="happy")
        blit_sxy(cv, L, CX, 1560, max(.04, abs(math.cos(su*math.pi*2))), 1)
    else:
        ZZ.draw(cv, fr, CX, 1560, 1.0, age=1, kit="real" if su >= 1 else "juventus", mood="happy", t=t, arms=(20, 20))
    tm = w(7, "soixante-dix")
    show(cv, fr, T7a, t, w(7, "plus"), None, 300, 500, -4)
    if t > tm:
        LBL(f"{counter(0, 70000000, prog(t, tm, 1.0))} €", "zp70", font("title", 100), GOLD, None, stroke=6, stroke_fill=PAL["ink"]).draw(cv, fr, CX, 600, pop_in(t, tm), -2)
    show_stamp(cv, fr, K7b, t, w(7, "Record"), CX, 780, -6)
    camera_flashes(cv, fr, "zcf7", t - w(7, "Record"), 1.2, 12)

def s7b(cv, fr, t):
    stadium(cv, fr, "zs7stad", t, sky=(16, 20, 40))
    th = w(7, "volée") + .05
    draw_goal(cv, fr, 850, 1250, 330, 220, prog(t, th + .22, .5), 1, t)
    kick = math.sin(prog(t, th - .22, .5)*math.pi)
    ZZ.draw(cv, fr, 380, 1570, 1.0, age=1, kit="real", mood="determined", t=t, legs=(-78*kick, 0), lean=-12*kick, arms=(60, 40), look=(-1, -1))
    t0 = th - 1.3
    if t0 < t < th:     # ralenti : le ballon tombe du ciel
        p = bezier((60, 260), (380, 120), (600, 1370), ease_out_cubic(prog(t, t0, 1.3))); draw_ball(cv, fr, p[0], p[1], .5, t*200)
    elif th <= t < th + .22:
        p = lerp_pt((600, 1370), (975, 1060), prog(t, th, .22)); draw_ball(cv, fr, p[0], p[1], .5, t*900)
        speed_lines(cv, fr, (700, 1250), .8, seed=7, inner=220)
    elif t >= th + .22:
        draw_ball(cv, fr, 960, 1090, .45, 0)
    show(cv, fr, T7b, t, w(7, "an"), None, 330, 560, -3)
    kw(cv, fr, K7c, t, w(7, "finale"), w(7, "gauche") - .05, CX, 420, 3)
    kw(cv, fr, K7d, t, w(7, "gauche"), None, CX, 420, -4)
    show_stamp(cv, fr, K7e, t, w(7, "légende"), CX, 720, -6)

def s7(cv, fr, t, T):
    th = w(7, "volée") + .05
    shots(cv, fr, t, [(0, s7a), (w(7, "Et") - .1, s7b)])
    impact(cv, t, w(7, "Record"), 18); flashes(cv, t, w(7, "Record"), .12, .6)
    flashes(cv, t, th, .12, .8); punch(cv, t, th, 1.1); impact(cv, t, th + .22, 16); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 8 — le retour, la panenka de 2006
def s8a1(cv, fr, t):
    stage_fill(cv, fr, BLEU, "zs8a"); d = ImageDraw.Draw(cv)
    d.ellipse([CX-14, 560, CX+14, 588], fill=(200, 196, 190))
    sw = 3*math.sin(t*2.5)
    d.line([(CX, 574), (CX-150, 720)], fill=(200, 196, 190), width=6); d.line([(CX, 574), (CX+150, 720)], fill=(200, 196, 190), width=6)
    JB10.draw(cv, fr, CX, 960, .9, sw)
    show(cv, fr, T8a, t, w(8, "arrêté") - .1, None, CX, 440, -2)
    if t > w(8, "Bleus"): pencil_cross(d, CX, 980, 5)

def s8a2(cv, fr, t):
    pitch(cv, fr, "zp8a")
    tr = w(8, "revient")
    for i, (P, x) in enumerate(zip(MATES, (200, 880))):
        lg, bob = walk(t + i, 11, 18); P.draw(cv, fr, x, 1600 - bob, .8, age=1, kit="france", legs=lg, mood="happy", t=t)
    ZZ.draw(cv, fr, CX, 1640, 1.05, age=1, kit="france", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
    kw(cv, fr, K8a, t, tr, w(8, "finale") - .08, CX, 440, -4)
    show(cv, fr, T8b, t, tr + .2, w(8, "finale") - .08, CX, 600, 3)
    kw(cv, fr, K8b, t, w(8, "finale"), None, CX, 440, 3)
    if t > w(8, "Mondial"): WC_TROPHY.draw(cv, fr, 880, 640, .5*pop_in(t, w(8, "Mondial")), 5)

def s8b(cv, fr, t):
    stage_fill(cv, fr, (40, 44, 70), "zs8b"); d = ImageDraw.Draw(cv)
    for k in range(6):
        ry = 300 + k*70
        for j in range(20): d.ellipse([60 + j*50 - 16, ry - 16, 60 + j*50 + 16, ry + 16], fill=(80 + (j*37 + k*11) % 90, 80, 110))
    for k in range(8):
        y0 = 740 + k*145; d.rectangle([30, y0, 1050, y0 + 146], fill=(60, 140, 76) if k % 2 == 0 else (54, 128, 70))
    tk = w(8, "panenka"); tb = w(8, "barre"); tin = w(8, "rentre")
    draw_goal(cv, fr, CX, 1000, 640, 360, 0, 1, t)
    d.line([(CX-340, 1000), (CX+340, 1000)], fill=(240, 240, 232), width=6)
    dv = ease_out_cubic(prog(t, tk + .08, .45))
    if dv <= 0: GK.draw(cv, fr, CX, 1000, .62, age=1, kit="gk", mood="determined", t=t, arms=(60, 60), legs=(14, 14))
    else:
        L = GK.render_layer(fr, .62, age=1, kit="gk", mood="surprised", arms=(150, 150))
        blit(cv, L, CX - 230*dv, 1000 - 40*math.sin(dv*math.pi), 1, 72*dv)
    if t < tk + .05: p, s = (CX + 30, 1640), 1.0
    elif t < tb:
        u = prog(t, tk + .05, tb - tk - .05); p = bezier((CX + 30, 1640), (CX + 40, 300), (CX + 30, 650), u); s = lerp(1.0, .42, u)
    elif t < tin:
        u = prog(t, tb, tin - tb); p = (CX + 30 - 10*u, lerp(650, 950, u*u)); s = .42
    else:
        u = prog(t, tin, .5); p = (CX + 20 + 40*u, 950 + 80*math.sin(u*math.pi)*.6); s = .42
    draw_ball(cv, fr, p[0], p[1], s, t*200)
    bob = -20*math.sin(prog(t, tk - .25, .35)*math.pi)
    zz_back(cv, fr, 250, 1720, .72, bob)
    kw(cv, fr, K8c, t, tk, tin - .05, CX, 1260, -3)
    kw(cv, fr, K8d, t, tin, None, CX, 1260, 4)
    show(cv, fr, T8c, t, tin + .15, None, 780, 1420, 3)
    if t > tin: pencil_check(d, CX + 20, 880, 2.0, (250, 250, 246))

def s8(cv, fr, t, T):
    shots(cv, fr, t, [(0, s8a1), (w(8, "revient") - .12, s8a2), (w(8, "Il", 3) - .1, s8b)])
    impact(cv, t, w(8, "barre"), 18); flashes(cv, t, w(8, "rentre"), .15, .6); punch(cv, t, w(8, "rentre"), 1.08); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 9 — 110e minute : le coup de tête
def s9a(cv, fr, t):
    stadium(cv, fr, "zs9stad", t)
    lg, bob = walk(t, 7, 16)
    ZZ.draw(cv, fr, lerp(460, 360, prog(t, 0, 3.3)), 1560 - bob, 1.0, age=1, kit="france_w", mood="normal", t=t, legs=lg, look=(-1, 0))
    tp = w(9, "parle")
    MATE.draw(cv, fr, lerp(740, 620, prog(t, 0, 3.3)), 1560, 1.06, age=1, kit="italy", beard=True, mood="happy" if t > tp else "normal", t=t, look=(-1, 0))
    kw(cv, fr, K9a, t, w(9, "cent-dixième"), w(9, "Materazzi") - .05, CX, 420, -3)
    show(cv, fr, T9a, t, w(9, "Materazzi"), None, 740, 560, 3)
    if t > tp:
        speech_bubble(cv, fr, "zinsult", "#@!%&*", 820, 760, pop_in(t, tp), (-1, 1), 60)
    show(cv, fr, T9b, t, w(9, "sœur"), None, 380, 680, -3)

def s9b(cv, fr, t):
    stadium(cv, fr, "zs9stad", t)
    tr = w(9, "retourne"); th = w(9, "coup") + .12
    su = prog(t, tr - .1, .35)
    if su < 1:
        L = ZZ.render_layer(fr, 1.0, age=1, kit="france_w", mood="determined")
        MATE.draw(cv, fr, 620, 1560, 1.06, age=1, kit="italy", beard=True, mood="happy", t=t, look=(-1, 0))
        blit_sxy(cv, L, 360, 1560, max(.04, abs(math.cos(su*math.pi))), 1)
    else:
        duel(cv, fr, t, th, zx=lerp(360, 410, prog(t, tr + .2, th - tr - .35)), mx=620)
    red_card(cv, fr, t, w(9, "Carton"), 830, 760)
    show_stamp(cv, fr, K9b, t, w(9, "Carton"), CX, 460, -5)
    if t > th: grayscale(cv, .5*prog(t, th, .3))

def s9c(cv, fr, t):
    stage_fill(cv, fr, (120, 120, 124), "zs9c"); d = ImageDraw.Draw(cv)
    d.rectangle([30, 1300, 1050, 1890], fill=(90, 110, 90))
    t0 = w(9, "Il") - .1; lg, bob = walk(t, 6, 14)
    ZZ.draw(cv, fr, lerp(1000, 120, prog(t, t0, w(9, "La", 4) - t0)), 1500 - bob, .85, age=1, kit="france_w", mood="sad", t=t, legs=lg, look=(0, 1))
    PEDESTAL.draw(cv, fr, 560, 1540, 1)
    WC_TROPHY.draw(cv, fr, 560, 1180, 1.25)
    show(cv, fr, T9c, t, w(9, "sans"), None, CX, 520, -2)
    grayscale(cv, 1.0)

def s9d(cv, fr, t):
    stage_fill(cv, fr, (54, 58, 68), "zs9d"); d = ImageDraw.Draw(cv)
    rnd = random.Random(99)
    for k in range(70):   # pluie
        x = rnd.uniform(40, 1040); y = (rnd.uniform(0, 1800) + t*1400) % 1760 + 130
        d.line([(x, y), (x - 10, y + 40)], fill=(150, 160, 180), width=3)
    score2(cv, fr, CX, 900, "ITA", "FRA", 5, 3, "tirs au but", pop_in(t, w(9, "La", 4) + .05))
    kw(cv, fr, K9c, t, w(9, "perd"), None, CX, 480, -3)

def s9(cv, fr, t, T):
    shots(cv, fr, t, [(0, s9a), (w(9, "Zidane") - .1, s9b), (w(9, "Il") - .1, s9c), (w(9, "La", 4) - .1, s9d)])
    th = w(9, "coup") + .12
    impact(cv, t, th, 26); flashes(cv, t, th, .15, .9); glitch(cv, fr, t, w(9, "Carton"), .4, 18); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 10 — entraîneur : 3 Ligues des champions d'affilée
def s10a(cv, fr, t):
    stage_fill(cv, fr, (86, 80, 74), "zs10a"); d = ImageDraw.Draw(cv)
    nx, ny = 300, 620
    d.ellipse([nx-12, ny-12, nx+12, ny+12], fill=(200, 196, 190))
    for k, dx in enumerate((-80, 80)):
        sw = 8*math.sin(t*2.2 + k)
        bx, by = nx + dx + sw*3, ny + 260
        d.line([(nx, ny), (bx, by - 70)], fill=(250, 250, 246), width=4)
        BOOT.draw(cv, fr, bx, by + 40, 1.6, sw)
    td = w(10, "devient")
    x = lerp(1250, 720, ease_out_cubic(prog(t, td - .5, .8))); lg, bob = walk(t) if t < td + .3 else ((0, 0), 0)
    ZZ.draw(cv, fr, x, 1600 - bob, 1.05, age=1, kit="suit", mood="determined", t=t, legs=lg, arms=(12, 12))
    kw(cv, fr, K10a, t, w(10, "raccroche"), td - .1, CX, 420, -3)
    show(cv, fr, T10a, t, w(10, "raccroche") + .3, td - .1, 300, 1130, -3)
    kw(cv, fr, K10b, t, w(10, "entraîneur"), None, CX, 420, 3)

def s10b(cv, fr, t):
    stage_fill(cv, fr, (246, 240, 226), "zs10b")
    rays(cv, (CX, 900), t, .9, 16, 1400, (240, 210, 130))
    kw(cv, fr, K10c, t, w(10, "Real"), None, CX, 400, -3)
    tt = w(10, "trois")
    ZZ.draw(cv, fr, CX, 1800, .7, age=1, kit="suit", mood="happy" if t < tt else "cheer", t=t,
            arms=(150, 150) if t > tt else (12, 12), legs=(10, 10))
    for i in range(3):
        a = pop_in(t, tt + i*.16)
        if a <= 0: continue
        x = 250 + i*290
        UCL.draw(cv, fr, x, 770, 1.0*a, 4*math.sin(t*3 + i)); YEARS10[i].draw(cv, fr, x, 970, a)
    kw(cv, fr, K10d, t, w(10, "d'affilée"), None, CX, 1110, 3)
    show_stamp(cv, fr, K10e, t, w(10, "jamais"), CX, 1260, -6)
    confetti(cv, fr, "zc10", t - w(10, "jamais"), 60, 3)

def s10(cv, fr, t, T):
    shots(cv, fr, t, [(0, s10a), (w(10, "Et") - .1, s10b)])
    impact(cv, t, w(10, "jamais"), 16); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 11 — sélectionneur
def s11(cv, fr, t, T):
    stage_fill(cv, fr, BLEU, "zs11"); d = ImageDraw.Draw(cv)
    rays(cv, (330, 1100), t, .5, 14, 1400, (60, 90, 170))
    fr_flag(cv, 790, 470, 360, 230, pop_in(t, .05), t, 4)
    kw(cv, fr, K11a, t, w(11, "deux"), None, 290, 440, -4)
    ZZ.draw(cv, fr, 300, 1620, 1.05, age=1, kit="suit", mood="happy", t=t, arms=(12, 40 + 10*math.sin(t*4)))
    ts = w(11, "sélectionneur")
    show_stamp(cv, fr, K11b, t, ts, CX, 740, -4)
    camera_flashes(cv, fr, "zcf11", t - ts, 1.4, 12)
    show(cv, fr, T11a, t, w(11, "l'équipe"), None, CX, 880, 2)
    tc = w(11, "Contrat")
    a = pop_in(t, tc - .1)
    if a > 0:
        DOC.draw(cv, fr, 700, 1240, .78*a, 4)
        if a > .9:
            u = prog(t, tc + .2, .8)
            pts = [(620 + k*6, 1400 - 22*math.sin(k*.7) - k*.8) for k in range(30)]
            pencil_line(d, pts, u, PAL["ink"], 5, 3, 1.2)
    show_stamp(cv, fr, K11c, t, w(11, "trente"), 690, 1290, -8)
    impact(cv, t, ts, 14); impact(cv, t, w(11, "trente"), 12); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 12 — Deschamps l'a fait deux fois… et Zizou ?
def duo(cv, fr, t, pl_a, pl_b, kit_a, kit_b, lab_a, lab_b, ta, tb, check_b=True):
    d = ImageDraw.Draw(cv)
    for (pl, kit, lab, t0, x, chk) in ((pl_a, kit_a, lab_a, ta, 290, True), (pl_b, kit_b, lab_b, tb, 790, check_b)):
        a = pop_in(t, t0)
        if a <= 0: continue
        pl.draw(cv, fr, x, 1260, .72*a, age=1, kit=kit, mood="happy", t=t, arms=(20, 150) if chk else (10, 10))
        (WC_TROPHY if chk else WC_SIL).draw(cv, fr, x + 150, 1180, .42*a, 5)
        L12[lab].draw(cv, fr, x, 1340, a, -2)
        if chk and t > t0 + .2: pencil_check(d, x, 1450, 2.2)
        if not chk: QM.draw(cv, fr, x, 1470 + 8*math.sin(t*5), .5*pop_in(t, t0 + .2), 8)

def s12a(cv, fr, t):
    stage_fill(cv, fr, (246, 238, 220), "zs12a")
    kw(cv, fr, K12a, t, .05, None, CX, 400, -3)
    show(cv, fr, T12a, t, w(12, "champion"), None, CX, 560, 2)
    a = win(t, .1, w(12, "joueur") - .15)
    if a > .01:   # portrait
        s = 2.4*a; DESCH18.head.draw(cv, fr, CX, 1020, s); DESCH18.hair_adult.draw(cv, fr, CX, 1020, s)
        if a > .9: DESCH18.face(cv, CX, 1020, s, "happy", (0, 0), False, t, 0)
    duo(cv, fr, t, DESCH98, DESCH18, "france", "suit", "joueur · 1998", "sélectionneur · 2018", w(12, "joueur"), w(12, "sélectionneur"))

def s12b(cv, fr, t):
    stage_fill(cv, fr, (240, 206, 90), "zs12b")
    kw(cv, fr, K12b, t, w(12, "Zizou") - .1, None, CX, 420, -3)
    duo(cv, fr, t, ZZ, ZZ, "france", "suit", "joueur · 1998", "sélectionneur · 20??", w(12, "Tu") - .05, w(12, "pareil"), check_b=False)

def s12c(cv, fr, t):
    stage_fill(cv, fr, (246, 238, 220), "zs12c"); d = ImageDraw.Draw(cv)
    tp = w(12, "Dis-le") - .1
    BTN_OUI.draw(cv, fr, 330, 560, pop_in(t, tp), -4); BTN_NON.draw(cv, fr, 750, 560, pop_in(t, tp + .15), 4)
    tc = w(12, "commentaire")
    if t > tc:
        arrow(d, (620, 900), (960, 1120), prog(t, tc, .3), PAL["ink"], 10, 12, 36, .2)
        LBL("en commentaire", "zencom", font("hand", 60), PAL["ink"], PAL["paper"], padx=18, pady=6).draw(cv, fr, 480, 880, pop_in(t, tc), -3)
    tb = w(12, "abonne-toi")
    if t > tb:
        press = 1 - .12*math.sin(prog(t, tb + .5, .25)*math.pi)
        BTN_SUB.draw(cv, fr, CX, 1080, pop_in(t, tb)*press, -2)
    tl = w(12, "prochaine")
    kw(cv, fr, K12c, t, tl, None, CX, 1230, 3)
    if t > tl:
        ZZ.draw(cv, fr, CX, 1780, .62, age=1, kit="suit", mood="cheer", arms=(150, 150), legs=(14, 14), t=t)
        confetti(cv, fr, "zc12", t - tl, 70, 5)

def s12(cv, fr, t, T):
    shots(cv, fr, t, [(0, s12a), (w(12, "Tu") - .1, s12b), (w(12, "Dis-le") - .1, s12c)])
    impact(cv, t, w(12, "pareil"), 12); drift(cv, t, T)

# ------------------------------------------------------------------ scènes + bruitages
def SC(name, n, fn, sfx, trans=None, trans_dur=.3, pad_out=.3):
    return Scene(name, TEXTS[n-1], fn, sfx, pad_in=PAD, pad_out=pad_out, trans=trans, trans_dur=trans_dur)
W_ = w
SCENES = [
    SC("cold_open", 1, s1, [(.0, "crowd_long", .7), (.05, "whistle", .5), (W_(1, "deux"), "stamp", .6), (W_(1, "dernier"), "pop2"),
                            (W_(1, "Et"), "heart", .9), (W_(1, "tête") - .05, "boom"), (W_(1, "tête") - .05, "thud"), (W_(1, "tête"), "gasp", .9),
                            (W_(1, "Carton") - .05, "whistle", .8), (W_(1, "Carton"), "stamp"), (W_(1, "Comment"), "scratch", .8, .6),
                            (W_(1, "Comment"), "glitch", .6, .3), (W_(1, "ça"), "pop"), (W_(1, "On") - .05, "rewind", 1.0)]),
    SC("marseille", 2, s2, [(.0, "boom", .6), (.05, "whoosh_up", .6), (W_(2, "mille"), "pop"), (W_(2, "Zinédine") - .1, "whoosh", .5),
                            (W_(2, "Zinédine"), "stamp"), (W_(2, "Castellane"), "pop"), (W_(2, "quartiers"), "pop2"), (W_(2, "Son") - .1, "whoosh", .5),
                            (W_(2, "père"), "pop"), (W_(2, "Kabylie"), "pop2"), (W_(2, "magasinier"), "stamp", .6), (W_(2, "magasinier") + .2, "thud", .5),
                            (W_(2, "Et") - .1, "whoosh", .5), (W_(2, "journées"), "pop")] +
                           [(W_(2, "Et") - .1 + k/2.2, "kick", .35) for k in range(6)] + [(W_(2, "pied"), "pop2")], trans="punch", trans_dur=.35),
    SC("cannes", 3, s3, [(W_(3, "quatorze"), "stamp", .6), (W_(3, "centre"), "pop"), (W_(3, "Cannes") - .1, "whoosh", .5), (W_(3, "Cannes"), "pop2"),
                         (W_(3, "loin"), "pop"), (W_(3, "Le") - .1, "whoosh", .5), (W_(3, "président"), "pop"), (W_(3, "promet") + .1, "scribble", .5),
                         (W_(3, "voiture"), "stamp", .7), (W_(3, "En") - .1, "whoosh", .5), (W_(3, "mille"), "stamp", .6),
                         (W_(3, "marque") - .4, "kick"), (W_(3, "marque"), "crowd", .7), (W_(3, "et", 2) - .1, "whoosh", .5),
                         (W_(3, "Clio") - .5, "horn", .8), (W_(3, "Clio"), "sparkle"), (W_(3, "toute"), "pop2")], trans="whip"),
    SC("france98", 4, s4, [(.05, "stamp"), (.05, "crowd_long", .8), (W_(4, "Coupe"), "pop2"), (W_(4, "maison"), "pop"), (W_(4, "Contre") - .1, "whoosh", .5),
                           (W_(4, "Contre"), "pop"), (W_(4, "pète"), "whoosh", .5), (W_(4, "plombs"), "thud"), (W_(4, "plombs"), "glitch", .7, .4),
                           (W_(4, "plombs") + .1, "gasp", .8), (W_(4, "carton") - .05, "whistle", .8), (W_(4, "carton"), "stamp"), (W_(4, "deux"), "pop2")],
       trans="tear_h", trans_dur=.6),
    SC("finale98", 5, s5, [(W_(5, "finale"), "stamp"), (W_(5, "Brésil") - .2, "pop"), (W_(5, "deux") - .1, "whoosh", .5), (W_(5, "coups") - .45, "kick", .5),
                           (W_(5, "coups") + .1, "thud"), (W_(5, "coups") + .38, "crowd", .8), (W_(5, "tête"), "pop2"), (W_(5, "deux", 2) - .45, "kick", .5),
                           (W_(5, "deux", 2) + .1, "thud"), (W_(5, "deux", 2) + .38, "crowd_long", .9), (W_(5, "buts"), "stamp", .7),
                           (W_(5, "La") - .1, "whoosh", .5), (W_(5, "championne"), "stamp"), (W_(5, "championne"), "sparkle"), (W_(5, "son") - .1, "whoosh", .5),
                           (W_(5, "s'affiche") - .2, "whoosh_up", .7), (W_(5, "s'affiche"), "flash", .7), (W_(5, "l'Arc"), "pop")], trans="punch", trans_dur=.35),
    SC("pause", 6, s6, [(0, "scratch", 1.0, .9), (.3, "pop"), (W_(6, "prochain"), "stamp", .6)] + [(W_(6, "prochain") + i*.14, "notif", .7) for i in range(4)] +
                       [(W_(6, "Écris"), "notif"), (W_(6, "Écris") + .2, "scribble", .5), (W_(6, "commentaire"), "pop2"), (W_(6, "Allez"), "whoosh"),
                        (W_(6, "Allez"), "boom", .5)], trans="polaroid", pad_out=.35),
    SC("real", 7, s7, [(0, "boom", .8), (.05, "stamp", .7), (W_(7, "Real"), "whoosh", .6), (W_(7, "soixante-dix"), "cash"), (W_(7, "Record"), "stamp"),
                       (W_(7, "Record"), "flash"), (W_(7, "Et") - .1, "whoosh", .6), (W_(7, "an"), "pop"), (W_(7, "finale"), "pop2"),
                       (W_(7, "volée") - 1.1, "riser", .7), (W_(7, "volée") + .05, "kick"), (W_(7, "volée") + .05, "whoosh", .6),
                       (W_(7, "volée") + .27, "crowd_long", 1.0), (W_(7, "gauche"), "pop2"), (W_(7, "légende"), "stamp")], trans="whip"),
    SC("retour", 8, s8, [(W_(8, "arrêté") - .1, "pop"), (W_(8, "Bleus"), "scribble", .6), (W_(8, "revient") - .12, "whoosh", .6), (W_(8, "revient"), "stamp", .7),
                         (W_(8, "revient"), "crowd", .7), (W_(8, "finale"), "pop2"), (W_(8, "Mondial"), "sparkle", .6), (W_(8, "Il", 3) - .1, "whoosh", .5),
                         (W_(8, "panenka") - .05, "kick", .7), (W_(8, "panenka"), "pop2"), (W_(8, "barre"), "bar", 1.0), (W_(8, "rentre"), "crowd_long", 1.0),
                         (W_(8, "rentre"), "boom", .6), (W_(8, "rentre") + .15, "pop")], trans="tear_d", trans_dur=.6),
    SC("coup_de_tete", 9, s9, [(.0, "boom", .7), (W_(9, "cent-dixième"), "stamp", .6), (W_(9, "Materazzi"), "pop"), (W_(9, "parle"), "pop2"),
                               (W_(9, "sœur"), "glitch", .5, .3), (W_(9, "retourne") - .1, "swish"), (W_(9, "coup") + .12, "boom"), (W_(9, "coup") + .12, "thud"),
                               (W_(9, "coup") + .2, "gasp", .9), (W_(9, "Carton") - .05, "whistle", .8), (W_(9, "Carton"), "stamp"),
                               (W_(9, "Carton"), "glitch", .6, .4), (W_(9, "Il") - .1, "whoosh", .4), (W_(9, "La", 4) - .1, "whoosh", .4), (W_(9, "perd"), "groan", .6)],
       trans="punch", trans_dur=.35),
    SC("coach", 10, s10, [(W_(10, "raccroche"), "stamp", .6), (W_(10, "raccroche") + .2, "thud", .5), (W_(10, "devient") - .4, "whoosh", .5),
                          (W_(10, "entraîneur"), "pop2"), (W_(10, "Et") - .1, "whoosh", .6), (W_(10, "Real"), "pop")] +
                         [(W_(10, "trois") + i*.16, "pop") for i in range(3)] + [(W_(10, "d'affilée"), "sparkle"), (W_(10, "jamais"), "stamp"),
                          (W_(10, "jamais"), "crowd", .7)], trans="tear_v", trans_dur=.6),
    SC("selection", 11, s11, [(.05, "whoosh_up", .6), (W_(11, "deux"), "pop2"), (W_(11, "sélectionneur"), "stamp"), (W_(11, "sélectionneur"), "flash", .8),
                              (W_(11, "l'équipe"), "pop"), (W_(11, "Contrat") - .1, "paper"), (W_(11, "Contrat") + .2, "scribble", .7), (W_(11, "trente"), "stamp", .8)],
       trans="whip"),
    SC("fin", 12, s12, [(.05, "stamp", .6), (W_(12, "champion"), "pop"), (W_(12, "joueur"), "pop2"), (W_(12, "joueur") + .2, "scribble", .5),
                        (W_(12, "sélectionneur"), "pop2"), (W_(12, "sélectionneur") + .2, "scribble", .5), (W_(12, "Tu") - .1, "whoosh", .6),
                        (W_(12, "Zizou") - .1, "stamp", .7), (W_(12, "pareil"), "pop"), (W_(12, "pareil") + .2, "riser", .5),
                        (W_(12, "Dis-le") - .1, "whoosh", .6), (W_(12, "Dis-le"), "pop"), (W_(12, "Dis-le") + .15, "pop"), (W_(12, "commentaire"), "notif"),
                        (W_(12, "abonne-toi"), "pop2"), (W_(12, "abonne-toi") + .5, "notif"), (W_(12, "prochaine"), "crowd_long", .8),
                        (W_(12, "prochaine"), "sparkle")], trans="punch", trans_dur=.35, pad_out=1.3),
]
SCENES[5].trans_dur = 99      # la photo figée reste épinglée pendant toute la pause
SCENES[5].post = s6_post

# ------------------------------------------------------------------ couverture
def cover(path):
    cv = background(0, TITLE); stadium(cv, 0, "zcov", .4); d = ImageDraw.Draw(cv)
    rays(cv, (CX, 1050), 0.2, .5, 16, 1500, (120, 110, 150))
    Label("CARTON ROUGE", "zcv1", font("title", 126), PAL["cream"], ROUGE, maxw=1000, padx=36, pady=10, rough=5).draw(cv, 0, CX, 300, 1, -3)
    Label("À SON DERNIER MATCH ?!", "zcv2", font("title", 84), PAL["ink"], PAL["mustard"], maxw=1000, padx=30, pady=10, rough=5).draw(cv, 0, CX, 470, 1, 2)
    duel(cv, 0, 1.0, .95, zx=440, mx=660, stars=False)
    red_card(cv, 0, 1.0, 0, 200, 800)
    Label("L'HISTOIRE FOLLE DE ZIZOU", "zcv3", font("title", 66), PAL["cream"], PAL["ink"], padx=30, pady=12).draw(cv, 0, CX, 1690, 1, 1)
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
        p = os.path.join(out, f"z_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", "zidane")
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/zidane_stills"), only=only)); sys.exit()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25))
