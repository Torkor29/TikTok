"""Épisode « Légendes du foot » #4 : l'Olympique de Marseille (histoire d'un club).
Accroche : « champion d'Europe… puis en D2 ?! » dès la 1re image (coupe qui claque, puis chute d'ascenseur D1 -> D2),
vieux film sépia pour 1899, cyclistes du Vélodrome, rafale de buts de Skoblar, pièce d'un franc de Tapie, larmes de Bari,
pause « le plus grand joueur de l'OM ? » au milieu, tête de Boli, affaire VA-OM (enveloppe, gyrophares, argent enterré),
ascenseur vers la D2, renaissance (fumigènes, Drogba, Deschamps) et fin « team OM ou team PSG ? ».

  python3 episodes/om/om.py output/om --stills [3,4]
  python3 episodes/om/om.py output/om --cover
  python3 episodes/om/om.py output/om
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from story import *
import engine

TITLE = "~/légendes $ ./olympique_de_marseille"
SLUG = "om_legende"
VOICE = [os.path.join(HERE, "voix", f"scene_{i}.mp3") for i in range(1, 13)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
ALIGN = os.path.join(HERE, "alignement.json")
PAD = 0.15
WS, TEXTS = load_words(ALIGN)
def w(i, word, n=1, end=False):
    """Temps local (dans la scène i) où la voix prononce `word`."""
    return PAD + WS[i-1](word, n, end)

CIEL = (47, 174, 224); CIEL_D = (22, 120, 176); NAVY = (16, 40, 86); GOLD = (236, 186, 48); ROUGE = (206, 32, 44)
BLANC = (250, 250, 246)

MONT = Player("mont", hair=(70, 52, 38), skin=(232, 188, 152))
SKOB = Player("skob", hair=(66, 48, 36), skin=(226, 180, 142))
TAPIE = Player("tapie", hair=(72, 54, 42), skin=(226, 178, 140))
PAPIN = Player("papin", hair=(64, 46, 34), skin=(230, 184, 148))
WADDLE = Player("waddle", hair=(78, 58, 42), skin=(234, 190, 156), hair_style="mullet")
ABEDI = Player("abedi", hair=(24, 20, 18), skin=(110, 72, 52))
BOLI = Player("boli", hair=(22, 18, 16), skin=(96, 62, 44))
DROGBA = Player("drogba", hair=(22, 18, 16), skin=(104, 68, 50))
DESCH93 = Player("desch93", hair=(52, 40, 32), skin=(232, 188, 152))
DESCH10 = Player("desch10", hair=(96, 88, 82), skin=(232, 188, 152))
MIL = [Player("mil1", hair=(40, 32, 28), skin=(232, 188, 152)), Player("mil2", hair=(26, 22, 20), skin=(120, 82, 60), hair_style="quiff"),
       Player("mil3", hair=(150, 110, 70), skin=(236, 192, 160))]
VAP = Player("vap", hair=(60, 44, 34), skin=(230, 186, 150))
PSGP = Player("psgp", hair=(28, 24, 22), skin=(150, 104, 76))
OMP = Player("omp", hair=(40, 30, 24), skin=(214, 168, 130))

# ------------------------------------------------------------------ objets
QM = Label("?", "omqm", font("title", 300), PAL["mustard"], None, stroke=7, stroke_fill=PAL["ink"])
def _coin_decor(d, a):
    ax, ay = a; d.ellipse([ax-78, ay-78, ax+78, ay+78], outline=(200, 146, 30), width=6)
    d.text((ax, ay), "1 F", font=font("title", 80), fill=(150, 104, 20), anchor="mm")
COIN = Paper(ellipse_pts(180, 180, 40), GOLD, "coin", rough=1.2, pad=30).add(_coin_decor)
def _env_decor(d, a):
    ax, ay = a; d.polygon([(ax-170, ay-100), (ax, ay+10), (ax+170, ay-100)], outline=(170, 150, 110), fill=(226, 210, 170))
    d.text((ax, ay+50), "250 000 F", font=font("title", 52), fill=(120, 30, 30), anchor="mm")
ENVELOPE = Paper(rect_pts(340, 200), (238, 222, 184), "envelope", rough=1.4).add(_env_decor)
SHOVEL = Paper(poly_pts([(-10, -260), (10, -260), (10, -20), (46, -10), (40, 90), (0, 120), (-40, 90), (-46, -10), (-10, -20)]),
               (150, 150, 156), "shovel", rough=1.4).add(lambda d, a: d.rectangle([a[0]-10, a[1]-260, a[0]+10, a[1]-30], fill=(150, 104, 64)))
def _paper_decor(d, a):
    ax, ay = a
    d.rectangle([ax-230, ay-290, ax+230, ay-270], fill=(40, 38, 36))
    d.text((ax, ay-220), "SCANDALE !", font=font("title", 96), fill=(30, 28, 26), anchor="mm")
    d.rectangle([ax-230, ay-150, ax-20, ay+30], fill=(120, 116, 110))
    for k in range(9): d.line([(ax+10, ay-150+k*22), (ax+230, ay-150+k*22)], fill=(150, 146, 140), width=6)
    for k in range(8): d.line([(ax-230, ay+70+k*24), (ax+230, ay+70+k*24)], fill=(150, 146, 140), width=6)
NEWSPAPER = Paper(rect_pts(520, 640), (240, 236, 222), "newspaper", rough=1.6).add(_paper_decor)
def _wall_decor(d, a):
    ax, ay = a
    for j in range(8):
        for i in range(6):
            x = ax - 330 + i*120 + (60 if j % 2 else 0); y = ay - 280 + j*70
            d.rectangle([x-56, y-30, x+56, y+30], outline=(60, 56, 60), width=3)
CELL = Paper(rect_pts(700, 620), (110, 106, 112), "cellwall", rough=1.6).add(_wall_decor)
ARROW_DOWN = Paper(poly_pts([(-40, -200), (40, -200), (40, 40), (100, 40), (0, 180), (-100, 40), (-40, 40)]), ROUGE, "arrowdown", rough=2)
CLOUD = Paper(poly_pts([(-200, 40), (-210, -10), (-160, -60), (-90, -70), (-40, -120), (40, -120), (100, -70), (170, -60), (210, -10), (200, 40)]),
              (110, 110, 120), "cloud", rough=3, hatch=True)
def _hat_decor(d, a):
    ax, ay = a; d.rectangle([ax-58, ay-22, ax+58, ay-6], fill=(60, 40, 30))
HAT = Paper(poly_pts([(-110, 0), (-60, -6), (-58, -60), (58, -60), (60, -6), (110, 0), (100, 14), (-100, 14)]), (230, 206, 150), "boater", rough=1.4, pad=30).add(_hat_decor)
GOAL_NET_COL = (200, 196, 188)
SCOREBOARD = scoreboard_sprite(820, 330, "omscore")
LAMP = Paper(ellipse_pts(300, 300, 40), (255, 240, 190), "flashlight", rough=1, shadow=False)

def score2(cv, fr, x, y, la, lb, a, b, sub="", s=1.0):
    if s <= .02: return
    L = layer(900, 420, (450, 210)); SCOREBOARD.draw(L, fr, 450, 210, 1, 0, 1)
    d = ImageDraw.Draw(L)
    for x_, lab in ((180, la), (720, lb)): d.text((x_, 130), lab, font=font("mono", 64 if len(lab) <= 5 else 44), fill=(200, 196, 190), anchor="mm")
    d.text((450, 220), f"{a} - {b}", font=font("title", 150), fill=(255, 204, 70), anchor="mm")
    if sub: d.text((450, 330), sub, font=font("mono", 40), fill=(170, 166, 160), anchor="mm")
    blit(cv, L, x, y, s)

def walk(t, speed=9, amp=22):
    ph = math.sin(t*speed); return (amp*ph, -amp*ph), abs(math.sin(t*speed))*8

def mustache(cv, eyes, s, col=(60, 44, 34)):
    if not eyes: return
    (x1, y1), (x2, y2) = eyes; hx = (x1+x2)/2; hy = (y1+y2)/2 - 8*s
    ImageDraw.Draw(cv).polygon([(hx-34*s, hy+36*s), (hx-22*s, hy+20*s), (hx, hy+24*s), (hx+22*s, hy+20*s), (hx+34*s, hy+36*s), (hx, hy+30*s)], fill=col)

def om_flag(cv, x, y, w=260, h=170, t=0.0, a=1.0, rot=0.0):
    """Drapeau bleu ciel et blanc qui ondule (sans logo)."""
    if a <= .01: return
    L = layer(int(w+40), int(h+60), (w/2+20, h/2+30)); d = ImageDraw.Draw(L); n = 26
    for k in range(n):
        x0 = 20 + k*w/n; off = 10*math.sin(k/n*math.pi*2 - t*6)*(k/n)
        d.rectangle([x0, 30+off, 20+(k+1)*w/n+1, 30+h+off], fill=CIEL if (k*4//n) % 2 == 0 else BLANC)
    blit(cv, L, x, y, a, rot, 1)

def stadium(cv, fr, key, t=0.0, sky=(18, 22, 46), grass=(46, 112, 64), horizon=1060, flags=False, crowd=None):
    """Stade de nuit : tribunes animées (bleu ciel et blanc si crowd='om'), projecteurs, pelouse rayée."""
    stage_fill(cv, fr, sky, key); d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    rnd = random.Random(key)
    pal = [CIEL, BLANC, (120, 190, 230), (200, 220, 236), (70, 90, 150)] if crowd == "om" else \
          [(90, 96, 120), (130, 120, 110), (200, 196, 190), (60, 64, 90), (160, 60, 60), (70, 90, 150)]
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

def trophy_lift(cv, fr, pl, x, y, s, kit, t, trophy=UCL, mood="cheer"):
    """Joueur qui soulève une coupe au-dessus de la tête."""
    pl.draw(cv, fr, x, y, s, age=1, kit=kit, mood=mood, arms=(160, 160), legs=(12, 12), t=t)
    trophy.draw(cv, fr, x, y - 850*s + 8*math.sin(t*6), .9*s, 3*math.sin(t*4))

def draw_bike(cv, x, y, s, col, t, spd=18):
    """Cycliste de profil (piste du Vélodrome)."""
    d = ImageDraw.Draw(cv); ink = (40, 36, 34); r = 44*s
    for wx in (-62, 62):
        cx = x + wx*s; d.ellipse([cx-r, y-r, cx+r, y+r], outline=ink, width=max(3, int(6*s)))
        for k in range(3):
            an = t*spd + k*math.pi/3; d.line([(cx - r*math.cos(an), y - r*math.sin(an)), (cx + r*math.cos(an), y + r*math.sin(an))], fill=(120, 116, 110), width=2)
    seat = (x - 20*s, y - 62*s); bar = (x + 52*s, y - 64*s); crank = (x, y)
    d.line([(x-62*s, y), crank, seat, (x-62*s, y)], fill=ink, width=max(3, int(6*s)))
    d.line([crank, (x+36*s, y-58*s), (x+62*s, y)], fill=ink, width=max(3, int(6*s))); d.line([seat, (x+36*s, y-58*s)], fill=ink, width=max(3, int(6*s)))
    an = t*spd*.6; pedal = (x + 20*s*math.cos(an), y + 20*s*math.sin(an))
    hip = (seat[0] + 4*s, seat[1] - 10*s); shoulder = (x + 30*s, y - 128*s)
    d.line([hip, ((hip[0]+pedal[0])/2 + 18*s, (hip[1]+pedal[1])/2 - 6*s), pedal], fill=(230, 190, 150), width=max(4, int(13*s)))
    d.polygon([(hip[0]-12*s, hip[1]+6*s), (hip[0]+12*s, hip[1]+10*s), (shoulder[0]+10*s, shoulder[1]+14*s), (shoulder[0]-12*s, shoulder[1]-6*s)], fill=col)
    d.line([shoulder, bar], fill=(230, 190, 150), width=max(4, int(11*s)))
    d.ellipse([shoulder[0]-4*s, shoulder[1]-50*s, shoulder[0]+38*s, shoulder[1]-8*s], fill=(230, 190, 150))
    d.chord([shoulder[0]-6*s, shoulder[1]-54*s, shoulder[0]+40*s, shoulder[1]-14*s], 180, 360, fill=col)

def padlock(cv, x, y, s=1.0, closed=1.0, a=1.0):
    if a <= .01: return
    d = ImageDraw.Draw(cv); s *= a
    lift = (1 - closed)*50*s
    d.arc([x-62*s, y-150*s-lift, x+62*s, y-30*s-lift], 180, 360, fill=(170, 170, 176), width=int(22*s))
    d.line([(x+62*s-11*s, y-90*s-lift), (x+62*s-11*s, y-60*s)], fill=(170, 170, 176), width=int(22*s))
    d.line([(x-62*s+11*s, y-90*s-lift), (x-62*s+11*s, y-40*s-lift)], fill=(170, 170, 176), width=int(22*s))
    d.rounded_rectangle([x-90*s, y-60*s, x+90*s, y+90*s], int(20*s), fill=GOLD, outline=(170, 120, 20), width=int(6*s))
    d.ellipse([x-16*s, y-10*s, x+16*s, y+22*s], fill=(80, 60, 20)); d.rectangle([x-7*s, y+10*s, x+7*s, y+50*s], fill=(80, 60, 20))

def lightning(cv, x, y, s=1.0, col=GOLD):
    ImageDraw.Draw(cv).polygon([(x-30*s, y-150*s), (x+60*s, y-150*s), (x+10*s, y-20*s), (x+70*s, y-20*s), (x-50*s, y+170*s), (x-10*s, y+20*s), (x-70*s, y+20*s)], fill=col)

# ------------------------------------------------------------------ labels
H1 = HL("CHAMPION D'EUROPE…", "omh1", GOLD, PAL["ink"], 84)
H1b = HL("…PUIS EN D2 ?!", "omh1b", ROUGE, PAL["cream"], 96)
K1a = KW("1er CLUB FRANÇAIS", "omk1a", CIEL_D, size=84); K1b = KW("L'ANNÉE D'APRÈS…", "omk1b", PAL["ink"], size=84)
N1 = STAMP("OLYMPIQUE DE MARSEILLE", "omn1", CIEL_D, 76); K1c = KW("L'HISTOIRE FOLLE", "omk1c", PAL["mustard"], PAL["ink"], 100)
K2a = KW("1899", "omk2a", (120, 90, 60), (250, 240, 214), 170); T2a = TAG("René Dufaure de Montmirail", "omt2a", (240, 228, 200), size=50)
K2b = KW("FONDATEUR", "omk2b", (90, 66, 44), (250, 240, 214), 96); K2c = STAMP("DROIT AU BUT !", "omk2c", CIEL_D, 110)
K3a = KW("1937", "omk3a", PAL["ink"], size=150); K3b = STAMP("LE VÉLODROME", "omk3b", CIEL_D, 110)
K3c = KW("POURQUOI CE NOM ?", "omk3c", PAL["mustard"], PAL["ink"], 84); T3a = KW("UNE VRAIE PISTE DE VÉLO !", "omt3a", PAL["ink"], size=72)
K4a = KW("1971", "omk4a", PAL["ink"], size=150); T4a = TAG("Josip Skoblar", "omt4a", PAL["paper"], size=54)
K4b = STAMP("RECORD DE FRANCE", "omk4b", ROUGE, 96); K4c = KW("TOUJOURS PAS BATTU !", "omk4c", PAL["ink"], size=78)
K5a = KW("1986", "omk5a", PAL["ink"], size=150); K5b = KW("LE CLUB VA MAL", "omk5b", ROUGE, size=96); T5a = TAG("12e du championnat", "omt5a", PAL["paper"], size=50)
T5b = TAG("Bernard Tapie", "omt5b", PAL["paper"], size=56); K5c = STAMP("1 FRANC SYMBOLIQUE !", "omk5c", ROUGE, 86)
K5d = KW("L'OM ÉCRASE TOUT", "omk5d", CIEL_D, size=96); K5e = KW("4 TITRES D'AFFILÉE", "omk5e", GOLD, PAL["ink"], 90)
STAR_TAGS = [TAG(n, "omst"+n, PAL["paper"], size=46) for n in ("Papin", "Waddle", "Abedi Pelé")]
YEARS5 = [LBL(str(y), f"omy{y}", font("title", 44), PAL["ink"], PAL["paper"], padx=12, pady=4) for y in (1989, 1990, 1991, 1992)]
K6a = KW("BALLON D'OR", "omk6a", GOLD, PAL["ink"], 110); T6a = TAG("Jean-Pierre Papin", "omt6a", PAL["paper"], size=52)
K6b = KW("FINALE 1991", "omk6b", PAL["ink"], size=110); K6c = STAMP("DÉFAITE", "omk6c", ROUGE, 120)
K6d = KW("LES LARMES DE BARI", "omk6d", (60, 70, 100), size=84)
K7a = KW("STOP !", "omk7a", PAL["ink"], size=100); K7b = KW("LE PLUS GRAND ?", "omk7b", ROUGE, size=78)
NAMES = [LBL(n, f"omnm{n}", font("hand", 46), PAL["ink"], None) for n in ("Papin ?", "Drogba ?", "Waddle ?", "Payet ?")]
CARD = Paper(rect_pts(200, 250), PAL["paper"], "omcard", rough=2)
K7c = KW("EN COMMENTAIRE", "omk7c", PAL["ink"], size=84); K7d = KW("ON REPREND !", "omk7d", PAL["ink"], size=88)
K8a = KW("26 MAI 1993", "omk8a", PAL["ink"], size=110); T8a = TAG("Munich", "omt8a", PAL["paper"], size=56)
K8b = KW("LE GRAND MILAN", "omk8b", (200, 24, 36), size=96); K8c = KW("BOLI !", "omk8c", CIEL_D, size=150)
K8d = STAMP("CHAMPION D'EUROPE", "omk8d", GOLD, 92); K8e = STAMP("À JAMAIS LES PREMIERS", "omk8e", CIEL_D, 78)
T9a = TAG("6 jours avant la finale", "omt9a", PAL["paper"], size=52); K9a = KW("VALENCIENNES - OM", "omk9a", PAL["ink"], size=80)
K9b = KW("PAYÉS ?!", "omk9b", ROUGE, size=130); T9b = TAG("pour « lever le pied »", "omt9b", PAL["paper"], size=52)
T9c = TAG("250 000 francs", "omt9c", PAL["paper"], size=54); K9c = KW("ENTERRÉ DANS UN JARDIN !", "omk9c", PAL["mustard"], PAL["ink"], 72)
K10a = STAMP("TITRE RETIRÉ", "omk10a", ROUGE, 110); K10b = STAMP("RELÉGUÉ EN D2", "omk10b", ROUGE, 110)
T10a = TAG("Bernard Tapie", "omt10a", PAL["paper"], size=54); K10c = KW("PRISON", "omk10c", PAL["ink"], size=130)
T10b = TAG("1997", "omt10b", PAL["paper"], size=54)
K11a = KW("MARSEILLE SE RELÈVE", "omk11a", CIEL_D, size=84); K11b = KW("DROGBA", "omk11b", PAL["ink"], size=130)
T11a = TAG("2003-2004 : le Vélodrome s'enflamme", "omt11a", PAL["paper"], size=46)
K11c = KW("2010", "omk11c", GOLD, PAL["ink"], 150); T11b = TAG("l'ancien capitaine de 93", "omt11b", PAL["paper"], size=50)
K11d = STAMP("CHAMPION !", "omk11d", CIEL_D, 120)
K12a = KW("2025", "omk12a", BLANC, NAVY, 130); T12a = TAG("le PSG gagne la Ligue des champions", "omt12a", PAL["paper"], size=46)
K12b = STAMP("LES PREMIERS", "omk12b", CIEL_D, 120); T12b = TAG("pour toujours", "omt12b", PAL["paper"], size=56)
BTN_OM = Label("TEAM OM", "ombtnom", font("title", 74), BLANC, CIEL_D, padx=30, pady=10, rough=3)
BTN_PSG = Label("TEAM PSG", "ombtnpsg", font("title", 74), NAVY, BLANC, padx=30, pady=10, rough=3)
BTN_SUB = Label("+ ABONNE-TOI", "ombsub", font("title", 96), (255, 255, 255), (230, 40, 80), padx=40, pady=14, rough=2.5)
VS = Label("VS", "omvs", font("title", 200), PAL["mustard"], None, stroke=9, stroke_fill=PAL["ink"])

# ------------------------------------------------------------------ SCÈNE 1 — champion d'Europe… puis en D2 ?!
def s1a(cv, fr, t):
    tx = w(1, "Et") + .05
    stage_fill(cv, fr, (24, 30, 64), "oms1a")
    rays(cv, (CX, 1060), t, 1.0, 16, 1500, (220, 180, 80))
    camera_flashes(cv, fr, "omcf1", t % 1.6, 1.6, 10)
    shake_t = max(0.0, t - tx)
    sl = lerp(1.7, 1.0, ease_out_back(clamp(t/.3), 1.8))
    UCL.draw(cv, fr, CX + 6*math.sin(shake_t*50)*min(1, shake_t*2), 1080, 2.3*sl, 3*math.sin(t*3) + 4*math.sin(shake_t*40)*min(1, shake_t))
    if t < tx: confetti(cv, fr, "omc1", t + .8, 80, 4)
    hl(cv, fr, H1, t, -.3)
    kw(cv, fr, K1a, t, w(1, "premier"), tx - .1, CX, 560, -3)
    kw(cv, fr, K1b, t, tx, None, CX, 560, 3)
    if t > tx: grayscale(cv, prog(t, tx, .5)*.8)
    glitch(cv, fr, t, tx, .35, 14)

def s1_drop(cv, fr, t):
    te = w(1, "envoyé") - .05; td = w(1, "division")
    s1a(cv, fr, t)
    u = elevator_drop(cv, t, te, td - te)
    floor_panel(cv, fr, CX, 1300, "D1" if t < td - .05 else "D2", t, True, 1.4, pop_in(t, te, .2))
    if t > td:
        stage_fill(cv, fr, (34, 32, 40), "oms1shaft"); d = ImageDraw.Draw(cv)
        for j in range(6): d.rectangle([30, 300 + j*300, 1050, 316 + j*300], fill=(70, 66, 80))
        floor_panel(cv, fr, CX, 1150, "D2", t, True, 1.8, 1)
        UCL.draw(cv, fr, 800, 1600, 1.0, 70)   # la coupe a dégringolé
    hl(cv, fr, H1b, t, td)

def s1b(cv, fr, t):
    stage_fill(cv, fr, CIEL, "oms1b")
    rays(cv, (CX, 1000), t, .9, 16, 1500, (150, 210, 240))
    for k, x in enumerate((180, 540, 900)): om_flag(cv, x, 1400 + 20*math.sin(t*3 + k), 300, 200, t + k, 1, (-6, 0, 6)[k])
    OMP.draw(cv, fr, CX, 1780, .8, age=1, kit="om", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
    kw(cv, fr, K1c, t, w(1, "l'histoire"), None, CX, 500, -3)
    show_stamp(cv, fr, N1, t, w(1, "l'Olympique"), CX, 700, -4)
    confetti(cv, fr, "omc1b", t - w(1, "l'Olympique"), 70, 4, [CIEL, BLANC, (200, 230, 250)])

def s1(cv, fr, t, T):
    shots(cv, fr, t, [(0, s1_drop), (w(1, "Voici") - .1, s1b)])
    impact(cv, t, .02, 18); impact(cv, t, w(1, "division"), 24); flashes(cv, t, w(1, "division"), .12, .6)
    punch(cv, t, w(1, "l'Olympique"), 1.08); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 2 — 1899, Droit au but
def s2(cv, fr, t, T):
    tdr = w(2, "Droit")
    stage_fill(cv, fr, (226, 206, 170), "oms2"); d = ImageDraw.Draw(cv)
    d.rectangle([30, 1380, 1050, 1890], fill=(170, 150, 110))
    eyes = MONT.draw(cv, fr, 330, 1640, 1.15, age=1, kit="suit", mood="happy" if t > w(2, "fonde") else "normal", t=t, arms=(12, 40))
    mustache(cv, eyes, 1.15)
    HAT.draw(cv, fr, 330, 1640 - 632*1.15 + 40, 1.0)
    kw(cv, fr, K2a, t, w(2, "mille"), tdr - .1, CX, 420, -3)
    show(cv, fr, T2a, t, w(2, "René"), tdr - .1, 640, 600, 3)
    kw(cv, fr, K2b, t, w(2, "fonde"), tdr - .1, 680, 760, -4)
    if t < tdr: old_film(cv, fr, t, 1.0)
    else:
        draw_goal(cv, fr, 800, 1300, 360, 220, prog(t, tdr + .35, .5), 1, t)
        u = prog(t, tdr - .05, .35); d = ImageDraw.Draw(cv)
        arrow(d, (360, 900), (lerp(360, 790, u), lerp(900, 1180, u)), 1, CIEL_D, 30, 3, 90, 0)
        speed_lines(cv, fr, (600, 1050), prog(t, tdr, .25), seed=2, inner=200)
        sepia(cv, 1 - prog(t, tdr - .1, .3))
        show_stamp(cv, fr, K2c, t, tdr, CX, 480, -5)
    impact(cv, t, tdr, 18); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 3 — 1937, le Vélodrome
def velodrome(cv, cx, cy, s=1.0):
    d = ImageDraw.Draw(cv)
    d.ellipse([cx-470*s, cy-300*s, cx+470*s, cy+300*s], fill=(150, 150, 160))
    rnd = random.Random(37)
    for k in range(160):
        an = rnd.uniform(0, math.pi*2); rr = rnd.uniform(.82, .97)
        x, y = cx + 470*s*rr*math.cos(an), cy + 300*s*rr*math.sin(an)
        d.ellipse([x-9*s, y-9*s, x+9*s, y+9*s], fill=rnd.choice([CIEL, BLANC, (90, 90, 110), (200, 196, 190)]))
    d.ellipse([cx-380*s, cy-220*s, cx+380*s, cy+220*s], fill=(196, 110, 80))
    d.ellipse([cx-320*s, cy-170*s, cx+320*s, cy+170*s], fill=(70, 150, 84))
    d.rectangle([cx-230*s, cy-120*s, cx+230*s, cy+120*s], outline=(236, 240, 230), width=max(2, int(5*s)))
    d.line([(cx, cy-120*s), (cx, cy+120*s)], fill=(236, 240, 230), width=max(2, int(5*s)))

def s3a(cv, fr, t):
    stage_fill(cv, fr, (180, 214, 236), "oms3a")
    a = pop_in(t, .05, .5)
    velodrome(cv, CX, 1150, .95*a + .05)
    for k in range(3):   # petits cyclistes qui tournent sur la piste
        an = t*1.6 + k*2.1; x, y = CX + 350*math.cos(an), 1150 + 195*math.sin(an)
        ImageDraw.Draw(cv).ellipse([x-12, y-12, x+12, y+12], fill=(ROUGE, CIEL_D, GOLD)[k])
    kw(cv, fr, K3a, t, w(3, "mille"), None, 300, 440, -4)
    show_stamp(cv, fr, K3b, t, w(3, "Vélodrome"), CX, 640, -4)
    kw(cv, fr, K3c, t, w(3, "Pourquoi"), None, CX, 1480, 3)

def s3b(cv, fr, t):
    stage_fill(cv, fr, (170, 206, 230), "oms3b"); d = ImageDraw.Draw(cv)
    d.rectangle([30, 620, 1050, 1060], fill=(70, 150, 84))
    for k in range(6): d.rectangle([30 + k*180, 620, 120 + k*180, 1060], fill=(64, 140, 78))
    d.polygon([(30, 1060), (1050, 1060), (1050, 1500), (30, 1500)], fill=(196, 110, 80))
    for k in range(3): d.line([(30, 1120 + k*130), (1050, 1120 + k*130)], fill=(236, 226, 210), width=4)
    tp = w(3, "Parce") - .1
    for k, (col, spd, yy) in enumerate(((ROUGE, 1200, 1390), (CIEL_D, 1000, 1250), (GOLD, 1400, 1470), ((60, 150, 80), 1100, 1320))):
        x = ((t - tp)*spd + k*400) % 1700 - 320
        draw_bike(cv, x, yy, 1.3, col, t)
    kw(cv, fr, K3c, t, -1, w(3, "vraie") - .1, CX, 440, 3)
    kw(cv, fr, T3a, t, w(3, "vraie"), None, CX, 440, -2)

def s3(cv, fr, t, T):
    shots(cv, fr, t, [(0, s3a), (w(3, "Parce") - .1, s3b)])
    impact(cv, t, w(3, "Vélodrome"), 14); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 4 — Skoblar, 44 buts
def s4(cv, fr, t, T):
    pitch(cv, fr, "oms4p")
    tp = w(4, "plante"); ts = w(4, "saison"); tr = w(4, "record"); tt = w(4, "toujours")
    draw_goal(cv, fr, 820, 1300, 380, 240, ((t - tp)*4) % 1 if tp < t < ts else 0, 1, t)
    rate = 44/(ts - tp)
    kick = abs(math.sin((t - tp)*math.pi*rate/2)) if tp < t < ts else 0
    SKOB.draw(cv, fr, 300, 1650, .9, age=1, kit="om", mood="determined" if t < ts else "cheer", legs=(0, 45*kick), t=t,
              arms=(150, 150) if t > ts else (30, 30))
    if tp < t < ts + .3:
        for k in range(4):
            u = ((t - tp)*rate/4 + k/4) % 1
            if t > ts and u < .5: continue
            p = bezier((360, 1625), (620, 1220 - k*40), (800 + k*30, 1140 + (k % 2)*60), u); draw_ball(cv, fr, p[0], p[1], .5, t*900 + k)
    if t > tp:
        n = int(round(lerp(0, 44, ease_io(prog(t, tp, ts - tp)))))
        LBL(str(n), "omg44", font("title", 240), ROUGE, None, stroke=8, stroke_fill=PAL["ink"]).draw(cv, fr, 740, 540, pop_in(t, tp), -3)
        LBL("buts", "ombuts4", font("title", 76), PAL["ink"], PAL["paper"], padx=18, pady=4).draw(cv, fr, 740, 720, pop_in(t, tp + .2), 3)
    kw(cv, fr, K4a, t, .05, None, 280, 420, -4)
    show(cv, fr, T4a, t, w(4, "Josip"), None, 300, 560, -2)
    show_stamp(cv, fr, K4b, t, tr, CX, 855, -5)
    if t > tt:
        padlock(cv, 950, 560, .55, ease_out_back(prog(t, w(4, "battu"), .3)), pop_in(t, tt))
        kw(cv, fr, K4c, t, tt, None, CX, 990, 3)
    impact(cv, t, tr, 16); impact(cv, t, w(4, "battu"), 12); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 5 — Tapie, un franc symbolique, les stars, 4 titres
def s5a(cv, fr, t):
    stage_fill(cv, fr, (96, 100, 112), "oms5a"); d = ImageDraw.Draw(cv)
    CLOUD.draw(cv, fr, 760, 560 + 6*math.sin(t*2), 1)
    for k in range(40):   # pluie
        x = (k*97) % 1000 + 40; y = (k*211 + t*1300) % 1500 + 380
        d.line([(x, y), (x - 8, y + 36)], fill=(170, 180, 200), width=3)
    OMP.draw(cv, fr, 330, 1680, 1.0, age=1, kit="om", mood="sad", t=t, look=(0, 1))
    pts = [(120 + k*105, 880 + 45*k + 30*math.sin(k*2.3)) for k in range(9)]
    u = prog(t, w(5, "club") - .1, .9)
    pencil_line(d, pts, u, ROUGE, 20, 5, 1.2)
    if u > .9: ARROW_DOWN.draw(cv, fr, 930, 1380, .7, 0)
    kw(cv, fr, K5a, t, .05, None, 280, 420, -4)
    kw(cv, fr, K5b, t, w(5, "va"), None, CX, 760, 3)
    show(cv, fr, T5a, t, w(5, "mal"), None, 330, 1400, -2)

def s5b(cv, fr, t):
    stage_fill(cv, fr, (246, 226, 160), "oms5b")
    rays(cv, (CX, 900), t, .7, 14, 1300, (250, 214, 110))
    tb = w(5, "Bernard"); tf = w(5, "franc")
    x = lerp(1250, 340, ease_out_cubic(prog(t, tb - .1, .7))); lg, bob = walk(t) if t < tb + .6 else ((0, 0), 0)
    TAPIE.draw(cv, fr, x, 1640 - bob, 1.1, age=1, kit="suit", mood="happy", t=t, legs=lg, arms=(12, 60 if t > tf else 12))
    show(cv, fr, T5b, t, w(5, "Tapie"), None, 340, 820, -3)
    if t > w(5, "pour") - .2:
        u = prog(t, w(5, "pour") - .2, tf - w(5, "pour") + .5)
        cy = 900 - 380*math.sin(u*math.pi); flip = math.cos(u*math.pi*7)
        blit_sxy(cv, COIN.v[boil(fr)], 740, cy, 1.3, 1.3*max(.06, abs(flip)))
    show_stamp(cv, fr, K5c, t, w(5, "symbolique"), CX, 460, -5)

def s5c(cv, fr, t):
    stage_fill(cv, fr, CIEL, "oms5c")
    rays(cv, (CX, 1000), t, .8, 16, 1400, (150, 210, 240))
    for i, (P, key, x) in enumerate(((PAPIN, "Papin", 200), (WADDLE, "Waddle", 540), (ABEDI, "Abedi", 880))):
        t0 = w(5, key) - .08; a = pop_in(t, t0, .35)
        if a <= 0: continue
        hop = 140*math.sin(clamp((t - t0)/.45)*math.pi)
        P.draw(cv, fr, x, 1440 - hop, .95*a, age=1, kit="om", mood="happy", arms=(40, 150) if t < t0 + .6 else (20, 20), t=t)
        STAR_TAGS[i].draw(cv, fr, x, 1500, a, (-4, 3, -2)[i])
        draw_star(cv, x + 110, 700 + 20*math.sin(t*4 + i), 30, a, t*2)

def s5d(cv, fr, t):
    stage_fill(cv, fr, (246, 240, 226), "oms5d")
    rays(cv, (CX, 1000), t, .9, 16, 1400, (240, 210, 130))
    kw(cv, fr, K5d, t, w(5, "écrase"), w(5, "quatre", 2) - .05, CX, 460, -3)
    tq = w(5, "quatre", 2)
    for i in range(4):
        a = pop_in(t, tq + i*.12)
        if a <= 0: continue
        x = 180 + i*240
        CUP.draw(cv, fr, x, 900, .95*a, 4*math.sin(t*3 + i)); YEARS5[i].draw(cv, fr, x, 1100, a)
    kw(cv, fr, K5e, t, w(5, "d'affilée") - .15, None, CX, 460, 3)
    OMP.draw(cv, fr, CX, 1800, .7, age=1, kit="om", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
    confetti(cv, fr, "omc5", t - tq, 60, 4, [CIEL, BLANC, GOLD])

def s5(cv, fr, t, T):
    shots(cv, fr, t, [(0, s5a), (w(5, "Bernard") - .1, s5b), (w(5, "Il") - .1, s5c), (w(5, "et") - .1, s5d)])
    impact(cv, t, w(5, "symbolique"), 18); impact(cv, t, w(5, "écrase"), 14); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 6 — Ballon d'Or, les larmes de Bari
def s6a(cv, fr, t):
    stage_fill(cv, fr, (30, 30, 40), "oms6a")
    rays(cv, (CX, 900), t, 1.0, 16, 1400, (220, 180, 80))
    PAPIN.draw(cv, fr, 360, 1640, 1.1, age=1, kit="om", mood="cheer", arms=(20, 150), t=t)
    draw_ballon_or(cv, fr, 760, 1000 + 10*math.sin(t*4), 1.4*pop_in(t, w(6, "Ballon") - .1))
    kw(cv, fr, K6a, t, w(6, "Ballon"), None, CX, 460, -3)
    show(cv, fr, T6a, t, .1, None, 360, 620, 2)
    camera_flashes(cv, fr, "omcf6", t, 1.3, 10)

def s6b(cv, fr, t):
    stadium(cv, fr, "oms6stad", t, sky=(16, 18, 34))
    td = w(6, "défaite")
    score2(cv, fr, CX, 880, "OM", "ÉT. ROUGE", 0, 0, "tirs au but : 3 - 5" if t > td else "finale", .85*pop_in(t, w(6, "Coupe") - .1))
    kw(cv, fr, K6b, t, w(6, "finale"), td - .05, CX, 460, -3)
    show_stamp(cv, fr, K6c, t, td, CX, 460, -6)
    tl = w(6, "larmes")
    if t <= td:
        PAPIN.draw(cv, fr, 330, 1720, .9, age=1, kit="om", mood="determined", t=t)
        WADDLE.draw(cv, fr, 760, 1720, .9, age=1, kit="om", mood="determined", t=t)
    if t > td:
        PAPIN.draw(cv, fr, 330, 1720, .9, age=1, kit="om", mood="sad", t=t, look=(0, 1), tears=t - td)
        WADDLE.draw(cv, fr, 760, 1720, .9, age=1, kit="om", mood="sad", t=t, look=(0, 1), tears=t - td - .2)
        grayscale(cv, prog(t, td, .5)*.8)
        d = ImageDraw.Draw(cv)
        for k in range(50):
            x = (k*89) % 1000 + 40; y = (k*173 + t*1300) % 1500 + 380; d.line([(x, y), (x - 8, y + 36)], fill=(170, 180, 200), width=3)
    kw(cv, fr, K6d, t, tl, None, CX, 640, 3)

def s6(cv, fr, t, T):
    shots(cv, fr, t, [(0, s6a), (w(6, "Mais") - .1, s6b)])
    impact(cv, t, w(6, "défaite"), 18); glitch(cv, fr, t, w(6, "défaite"), .35, 14); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 7 — PAUSE : le plus grand joueur de l'OM ?
def s7(cv, fr, t, T):
    stage_fill(cv, fr, CIEL, "oms7"); d = ImageDraw.Draw(cv)
    kw(cv, fr, K7a, t, .05, None, 730, 330, 4)
    tp = w(7, "plus")
    kw(cv, fr, K7b, t, tp, None, 730, 540, -3)
    if t < w(7, "joueur"): QM.draw(cv, fr, CX, 1020 + 12*math.sin(t*5), win(t, w(7, "Pour"), w(7, "joueur") - .1), 8)
    for i in range(4):
        a = pop_in(t, w(7, "joueur") + i*.14)
        if a <= 0: continue
        x = 180 + i*240; y = 1010 + 10*math.sin(t*4 + i)
        CARD.draw(cv, fr, x, y, a, (-4, 3, -2, 5)[i])
        LBL("?", "omqmS", font("title", 130), (60, 56, 64), None).draw(cv, fr, x, y - 30, a)
        NAMES[i].draw(cv, fr, x, y + 90, a)
    te = w(7, "Écris")
    if t > te:
        a = pop_in(t, te)
        speech_bubble(cv, fr, "omcta_b", typewriter("Papin, obligé !!", prog(t, te + .2, .9)) or " ", 520, 1300, a, (-1, 1), 64)
        bx = 880 + 18*math.sin(t*8)
        arrow(d, (760, 1320), (bx + 80, 1180), prog(t, te + .2, .3), PAL["ink"], 10, 7, 34, -.2)
    kw(cv, fr, K7c, t, w(7, "commentaire"), None, 560, 1470, 2)
    kw(cv, fr, K7d, t, w(7, "Allez"), None, 730, 740, -5)
    impact(cv, t, w(7, "Allez"), 14)

def s7_post(cv, fr, t, T):
    """Par-dessus la photo figée : icône PAUSE."""
    a = pop_in(t, .25)
    if a <= 0: return
    d = ImageDraw.Draw(cv); cx, cy, s = 250, 470, a
    d.ellipse([cx-70*s, cy-70*s, cx+70*s, cy+70*s], fill=(34, 32, 36))
    for dx in (-22, 22): d.rectangle([cx+dx*s-12*s, cy-34*s, cx+dx*s+12*s, cy+34*s], fill=(250, 248, 240))

# ------------------------------------------------------------------ SCÈNE 8 — Munich 1993, la tête de Boli
def s8a(cv, fr, t):
    stadium(cv, fr, "oms8stad", t, crowd="om")
    kw(cv, fr, K8a, t, .05, None, CX, 420, -3)
    show(cv, fr, T8a, t, w(8, "Munich"), None, 300, 560, -3)
    tg = w(8, "grand")
    for P, x in ((DESCH93, 150), (BOLI, 340)):
        P.draw(cv, fr, x, 1680, .8, age=1, kit="om", mood="determined", t=t, look=(1, 0))
    for i, (P, x) in enumerate(zip(MIL, (590, 770, 950))):
        a = pop_in(t, tg - .1 + i*.1)
        if a > 0: P.draw(cv, fr, x, 1680, .85*a, age=1, kit="milan", mood="determined", t=t, arms=(30, 30), look=(-1, 0))
    kw(cv, fr, K8b, t, tg, None, CX, 720, 3)

def s8b(cv, fr, t):
    stadium(cv, fr, "oms8b", t, crowd="om", horizon=1000)
    th = w(8, "tête") + .05; tc = w(8, "Corner")
    hop = 150*math.sin(clamp((t - th + .3)/.6)*math.pi)
    draw_goal(cv, fr, 860, 1300, 330, 220, prog(t, th + .25, .5), 1, t)
    MIL[0].draw(cv, fr, 620, 1650 - hop*.4, .95, age=1, kit="milan", mood="surprised", t=t, arms=(40, 40))
    BOLI.draw(cv, fr, 420, 1650 - hop, 1.0, age=1, kit="om", mood="determined" if t < th + .3 else "cheer", t=t,
              arms=(40, 40) if t < th + .3 else (150, 150), look=(-1, -1))
    ABEDI.draw(cv, fr, 110, 1300, .5, age=1, kit="om", mood="determined", t=t, legs=(0, 40*math.sin(prog(t, tc, .3)*math.pi)))
    hx, hy = 420, 1650 - hop - 600
    if tc < t < th:
        p = bezier((150, 1270), (260, 300), (hx + 20, hy - 20), prog(t, tc + .05, th - tc - .05)); draw_ball(cv, fr, p[0], p[1], .5, t*400)
    elif th <= t < th + .28:
        p = lerp_pt((hx + 20, hy - 20), (840, 1170), prog(t, th, .28)); draw_ball(cv, fr, p[0], p[1], .5, t*800)
        speed_lines(cv, fr, (hx, hy), .7, seed=8, inner=200)
    elif t >= th + .28:
        draw_ball(cv, fr, 850, 1200, .45, 0)
    score2(cv, fr, CX, 640, "OM", "MILAN", 1 if t > w(8, "Un") else 0, 0, "", .55)
    kw(cv, fr, K8c, t, w(8, "Boli"), None, CX, 420, -4)

def s8c(cv, fr, t):
    stage_fill(cv, fr, (20, 30, 70), "oms8c")
    rays(cv, (CX, 900), t, 1.0, 16, 1500, (230, 200, 110))
    trophy_lift(cv, fr, DESCH93, CX, 1760, .9, "om", t)
    flares(cv, fr, "omfl8a", t, (70, 1450, 300, 1800), 3); flares(cv, fr, "omfl8b", t, (780, 1450, 1010, 1800), 3)
    show_stamp(cv, fr, K8d, t, w(8, "champion"), CX, 440, -4)
    show_stamp(cv, fr, K8e, t, w(8, "jamais") - .05, CX, 600, 4)
    confetti(cv, fr, "omc8", t, 90, 5, [CIEL, BLANC, GOLD])

def s8(cv, fr, t, T):
    shots(cv, fr, t, [(0, s8a), (w(8, "Corner") - .1, s8b), (w(8, "Marseille") - .1, s8c)])
    th = w(8, "tête") + .05
    impact(cv, t, th, 16); flashes(cv, t, th + .28, .15, .8); punch(cv, t, th + .28, 1.1)
    impact(cv, t, w(8, "jamais"), 16); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 9 — l'affaire VA-OM
def s9a(cv, fr, t):
    stage_fill(cv, fr, (40, 40, 48), "oms9a")
    score2(cv, fr, CX, 1000, "VA", "OM", 0, 1, "20 mai 1993", pop_in(t, w(9, "joué") - .1))
    VAP.draw(cv, fr, 300, 1720, .8, age=1, kit="valenciennes", mood="normal", t=t, look=(1, 0))
    OMP.draw(cv, fr, 780, 1720, .8, age=1, kit="om", mood="determined", t=t, look=(-1, 0))
    show(cv, fr, T9a, t, w(9, "avant"), None, CX, 460, -2)
    kw(cv, fr, K9a, t, w(9, "Valenciennes"), None, CX, 640, 3)
    tint(cv, .15)

def s9b(cv, fr, t):
    stage_fill(cv, fr, (26, 24, 30), "oms9b"); d = ImageDraw.Draw(cv)
    beam(cv, (CX, 140), [(CX - 330, 1500), (CX + 330, 1500)], .18)
    d.rectangle([60, 1320, 1020, 1360], fill=(90, 64, 44))   # table
    VAP.draw(cv, fr, 820, 1640, 1.0, age=1, kit="valenciennes", mood="normal", t=t, look=(-1, 0), arms=(10, -15))
    tp = w(9, "payés")
    x = lerp(160, 620, ease_io(prog(t, w(9, "joueurs") - .1, 1.0)))
    ENVELOPE.draw(cv, fr, x, 1250, .9, -4)
    d.ellipse([x - 230, 1230, x - 150, 1290], fill=(226, 178, 140))   # la main qui pousse l'enveloppe
    kw(cv, fr, K9b, t, tp, None, CX, 460, -4)
    show(cv, fr, T9b, t, w(9, "lever"), None, CX, 640, 2)

def s9c(cv, fr, t):
    stage_fill(cv, fr, (18, 22, 30), "oms9c"); d = ImageDraw.Draw(cv)
    d.rectangle([30, 1180, 1050, 1890], fill=(70, 50, 36))
    for k in range(12):   # herbe
        x = 60 + k*85; d.polygon([(x, 1180), (x + 12, 1130), (x + 24, 1180)], fill=(50, 90, 50))
    te = w(9, "enterré")
    hole = ease_out_cubic(prog(t, w(9, "L'argent"), 1.2))
    d.ellipse([CX - 220*hole, 1320 - 70*hole, CX + 220*hole, 1320 + 70*hole], fill=(40, 28, 20))
    dig = math.sin(t*9)
    SHOVEL.draw(cv, fr, CX + 220, 1180 + 40*dig, 1.1, 20 + 10*dig)
    if t > te:
        ENVELOPE.draw(cv, fr, CX, 1320 - 120*ease_out_back(prog(t, te, .4)), .8, -6)
        for k in range(6):
            a = k*1.05 + t*2; draw_star(cv, CX + 250*math.cos(a), 1250 + 110*math.sin(a), 20, pop_in(t, te + k*.06), t*3)
    LAMP.draw(cv, fr, CX + 120*math.sin(t*1.3), 1300, 1.3, 0, .18)
    siren_lights(cv, t, .22)
    show(cv, fr, T9c, t, w(9, "retrouvé"), None, CX, 640, 2)
    kw(cv, fr, K9c, t, w(9, "jardin") - .1, None, CX, 460, -3)

def s9(cv, fr, t, T):
    shots(cv, fr, t, [(0, s9a), (w(9, "Et") - .1, s9b), (w(9, "L'argent") - .1, s9c)])
    impact(cv, t, w(9, "payés"), 16); glitch(cv, fr, t, w(9, "payés"), .35, 14); impact(cv, t, w(9, "jardin"), 14); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 10 — titre retiré, D2, prison
def s10a(cv, fr, t):
    stage_fill(cv, fr, (60, 60, 70), "oms10a"); d = ImageDraw.Draw(cv)
    u = ease_out_cubic(prog(t, .05, .6))
    NEWSPAPER.draw(cv, fr, CX, 1000, lerp(.05, 1.05, u), lerp(900, -4, u))
    tp = w(10, "perd")
    if t > tp:
        CUP.draw(cv, fr, 820, 1330, .95*pop_in(t, tp - .1), 0)
        pencil_cross(d, 820, 1300, 6)
        show_stamp(cv, fr, K10a, t, w(10, "titre"), CX, 460, -5)

def s10b(cv, fr, t):
    te = w(10, "envoyé") - .05; tdv = w(10, "division")
    stage_fill(cv, fr, CIEL, "oms10b")
    OMP.draw(cv, fr, CX, 1700, 1.0, age=1, kit="om", mood="surprised", t=t)
    floor_panel(cv, fr, CX, 620, "D1", t, True, 1.6, 1)
    elevator_drop(cv, t, te, tdv - te + .1)
    if t > tdv + .1:
        stage_fill(cv, fr, (34, 32, 40), "oms10shaft"); d = ImageDraw.Draw(cv)
        for j in range(6): d.rectangle([30, 300 + j*300, 1050, 316 + j*300], fill=(70, 66, 80))
        OMP.draw(cv, fr, CX, 1720, 1.0, age=1, kit="om", mood="sad", t=t, look=(0, 1))
        floor_panel(cv, fr, CX, 760, "D2", t, True, 1.6, 1)
        show_stamp(cv, fr, K10b, t, tdv + .1, CX, 460, -5)

def s10c(cv, fr, t):
    stage_fill(cv, fr, (70, 68, 76), "oms10c"); d = ImageDraw.Draw(cv)
    CELL.draw(cv, fr, CX, 1150, 1.2)
    TAPIE.draw(cv, fr, CX, 1660, 1.05, age=1, kit="suit", mood="sad" if t > w(10, "prison") else "normal", t=t, look=(0, 1))
    show(cv, fr, T10a, t, .1, None, 320, 640, -3)
    tp = w(10, "prison")
    if t > tp - .15:
        drop = ease_out_cubic(prog(t, tp - .15, .25)); yb = lerp(-900, 0, drop)
        for k in range(8):
            x = 110 + k*125; d.rectangle([x - 16, 130 + yb, x + 16, 1880 + yb], fill=(50, 50, 56)); d.rectangle([x - 16, 130 + yb, x - 8, 1880 + yb], fill=(110, 110, 118))
        d.rectangle([30, 780 + yb, 1050, 810 + yb], fill=(50, 50, 56))
    kw(cv, fr, K10c, t, tp, None, CX, 460, -3)
    show(cv, fr, T10b, t, tp + .2, None, 780, 640, 3)
    if t > tp: grayscale(cv, prog(t, tp, .3)*.7)

def s10(cv, fr, t, T):
    shots(cv, fr, t, [(0, s10a), (w(10, "et") - .1, s10b), (w(10, "Bernard") - .1, s10c)])
    impact(cv, t, w(10, "explose"), 18); flashes(cv, t, w(10, "explose"), .12, .6); impact(cv, t, w(10, "division") + .1, 22)
    impact(cv, t, w(10, "prison"), 18); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 11 — renaissance : Drogba, Deschamps 2010
def s11a(cv, fr, t):
    stadium(cv, fr, "oms11stad", t, crowd="om", sky=(20, 24, 50))
    flares(cv, fr, "omfl11", t, (60, 700, 1020, 1000), 9, pop_in(t, .1))
    OMP.draw(cv, fr, CX, 1660 - 60*ease_out_back(prog(t, .1, .8)), 1.0, age=1, kit="om", mood="determined", arms=(20, 150), t=t)
    kw(cv, fr, K11a, t, w(11, "relève"), None, CX, 440, -3)

def s11b(cv, fr, t):
    stadium(cv, fr, "oms11b", t, crowd="om", sky=(30, 16, 24))
    flares(cv, fr, "omfl11b", t, (40, 560, 1040, 1000), 14)
    DROGBA.draw(cv, fr, CX, 1660, 1.1, age=1, kit="om", mood="cheer", arms=(150, 150), legs=(14, 14), t=t)
    kw(cv, fr, K11b, t, w(11, "Drogba"), None, CX, 440, -4)
    show(cv, fr, T11a, t, w(11, "enflamme"), None, CX, 600, 2)

def s11c(cv, fr, t):
    stage_fill(cv, fr, CIEL, "oms11c")
    rays(cv, (CX, 1000), t, .9, 16, 1400, (150, 210, 240))
    tt = w(11, "titre")
    if t > tt - .1: trophy_lift(cv, fr, DESCH10, CX, 1760, .95, "suit", t, CUP)
    else: DESCH10.draw(cv, fr, CX, 1760, .95, age=1, kit="suit", mood="happy", t=t, arms=(12, 40))
    kw(cv, fr, K11c, t, w(11, "deux"), tt - .12, 300, 440, -4)
    show(cv, fr, T11b, t, w(11, "capitaine"), None, 660, 600, 3)
    show_stamp(cv, fr, K11d, t, tt, CX, 460, -5)
    confetti(cv, fr, "omc11", t - tt, 70, 4, [CIEL, BLANC, GOLD])

def s11(cv, fr, t, T):
    shots(cv, fr, t, [(0, s11a), (w(11, "Drogba") - .1, s11b), (w(11, "et") - .1, s11c)])
    impact(cv, t, w(11, "Drogba"), 14); impact(cv, t, w(11, "titre"), 16); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 12 — les premiers ; team OM ou team PSG ?
def s12a(cv, fr, t):
    stage_fill(cv, fr, NAVY, "oms12a")
    rays(cv, (CX, 1000), t, .5, 14, 1400, (40, 70, 130))
    trophy_lift(cv, fr, PSGP, CX, 1760, .9, "psg", t, mood="happy")
    kw(cv, fr, K12a, t, w(12, "PSG") - .1, None, CX, 420, -3)
    show(cv, fr, T12a, t, w(12, "gagné"), None, CX, 580, 2)

def s12b(cv, fr, t):
    stage_fill(cv, fr, CIEL, "oms12b")
    rays(cv, (CX, 1000), t, 1.0, 16, 1500, (150, 210, 240))
    trophy_lift(cv, fr, DESCH93, CX, 1760, .9, "om", t)
    LBL("1993", "om1993", font("title", 120), PAL["ink"], PAL["mustard"], padx=24, pady=4, rough=3).draw(cv, fr, 250, 1000, pop_in(t, w(12, "Mais")), -6)
    show_stamp(cv, fr, K12b, t, w(12, "premiers"), CX, 440, -4)
    show(cv, fr, T12b, t, w(12, "toujours"), None, CX, 600, 2)
    confetti(cv, fr, "omc12b", t - w(12, "premiers"), 60, 4, [CIEL, BLANC])

def s12c(cv, fr, t):
    sx0, sy0, sx1, sy1 = STAGE; d = ImageDraw.Draw(cv)
    stage_fill(cv, fr, CIEL, "oms12c")
    d.polygon([(CX + 60, sy0), (sx1, sy0), (sx1, sy1), (CX - 60, sy1)], fill=NAVY)
    OMP.draw(cv, fr, 290, 1420, .8, age=1, kit="om", mood="cheer" if int(t*2) % 2 else "determined", arms=(150, 20), t=t)
    PSGP.draw(cv, fr, 790, 1420, .8, age=1, kit="psg", mood="determined" if int(t*2) % 2 else "cheer", arms=(20, 150), t=t)
    lightning(cv, CX, 1000, 1.2); VS.draw(cv, fr, CX, 1000 + 8*math.sin(t*6), pop_in(t, .05), -6)
    t1 = w(12, "team"); t2 = w(12, "team", 2)
    BTN_OM.draw(cv, fr, 290, 480, pop_in(t, t1)*(1 + .06*math.sin(t*8)), -4)
    BTN_PSG.draw(cv, fr, 760, 480, pop_in(t, t2)*(1 + .06*math.sin(t*8 + 1)), 4)
    tc = w(12, "commentaire")
    if t > tc:
        arrow(d, (620, 1520), (960, 1180), prog(t, tc, .3), PAL["mustard"], 12, 12, 40, .2)
    tb = w(12, "abonne-toi")
    if t > tb:
        press = 1 - .12*math.sin(prog(t, tb + .5, .25)*math.pi)
        BTN_SUB.draw(cv, fr, CX, 690, pop_in(t, tb)*press, -2)
        confetti(cv, fr, "omc12", t - tb, 70, 5, [CIEL, BLANC, GOLD])

def s12(cv, fr, t, T):
    shots(cv, fr, t, [(0, s12a), (w(12, "Mais") - .1, s12b), (w(12, "Et") - .1, s12c)])
    impact(cv, t, w(12, "premiers"), 16); impact(cv, t, w(12, "Et"), 14); drift(cv, t, T)

# ------------------------------------------------------------------ scènes + bruitages
def SC(name, n, fn, sfx, trans=None, trans_dur=.3, pad_out=.3):
    return Scene(name, TEXTS[n-1], fn, sfx, pad_in=PAD, pad_out=pad_out, trans=trans, trans_dur=trans_dur)
W_ = w
SCENES = [
    SC("accroche", 1, s1, [(.0, "boom"), (.0, "crowd_long", .8), (.02, "flash", .7), (.05, "sparkle", .7), (W_(1, "premier"), "stamp", .7),
                           (W_(1, "Et"), "glitch", .7, .4), (W_(1, "Et") + .1, "gasp", .6), (W_(1, "envoyé") - .05, "elevator", 1.0),
                           (W_(1, "division"), "boom"), (W_(1, "division") + .05, "stamp"), (W_(1, "Voici") - .1, "whoosh", .6),
                           (W_(1, "l'histoire"), "pop2"), (W_(1, "l'Olympique"), "stamp"), (W_(1, "l'Olympique"), "crowd", .8)]),
    SC("1899", 2, s2, [(.0, "scratch", .5, .5), (W_(2, "mille"), "stamp", .6), (W_(2, "René"), "pop"), (W_(2, "fonde"), "pop2"),
                       (W_(2, "Droit") - .1, "whoosh"), (W_(2, "Droit") + .3, "kick", .6), (W_(2, "but"), "stamp"), (W_(2, "but") + .1, "crowd", .6)],
       trans="tear_v", trans_dur=.6),
    SC("velodrome", 3, s3, [(W_(3, "mille"), "stamp", .6), (W_(3, "Vélodrome"), "stamp"), (W_(3, "Vélodrome") + .1, "crowd", .6),
                            (W_(3, "Pourquoi"), "pop2"), (W_(3, "Parce") - .1, "whoosh", .6), (W_(3, "vraie"), "bell", .9),
                            (W_(3, "vélo", 2), "whoosh", .5), (W_(3, "pelouse"), "bell", .7)], trans="whip"),
    SC("skoblar", 4, s4, [(.05, "stamp", .7)] + [(W_(4, "plante") + k*.3, "kick", .45) for k in range(6)] +
                         [(W_(4, "Josip"), "pop"), (W_(4, "quarante-quatre"), "crowd", .7), (W_(4, "record"), "stamp"),
                          (W_(4, "toujours"), "pop2"), (W_(4, "battu"), "clink"), (W_(4, "battu"), "thud", .6)], trans="punch", trans_dur=.35),
    SC("tapie", 5, s5, [(.05, "stamp", .7), (W_(5, "club"), "groan", .5), (W_(5, "mal"), "thud", .5), (W_(5, "Bernard") - .1, "whoosh", .6),
                        (W_(5, "pour") - .2, "coin", 1.0), (W_(5, "symbolique"), "stamp"), (W_(5, "Il") - .1, "whoosh", .6),
                        (W_(5, "Papin"), "pop"), (W_(5, "Waddle"), "pop2"), (W_(5, "Abedi"), "pop"), (W_(5, "et") - .1, "whoosh", .6),
                        (W_(5, "écrase"), "boom", .6)] + [(W_(5, "quatre", 2) + i*.12, "pop") for i in range(4)] +
                       [(W_(5, "d'affilée"), "sparkle"), (W_(5, "d'affilée"), "crowd", .6)], trans="whip"),
    SC("bari", 6, s6, [(.05, "sparkle"), (W_(6, "Ballon"), "flash", .7), (W_(6, "Ballon"), "stamp", .6), (W_(6, "Mais") - .1, "whoosh", .6),
                       (W_(6, "finale"), "whistle", .5), (W_(6, "défaite"), "glitch", .7, .4), (W_(6, "défaite"), "stamp"),
                       (W_(6, "défaite") + .1, "groan", .8), (W_(6, "larmes"), "heart", .6)], trans="tear_h", trans_dur=.6),
    SC("pause", 7, s7, [(0, "scratch", 1.0, .9), (.3, "pop"), (W_(7, "plus"), "stamp", .6)] + [(W_(7, "joueur") + i*.14, "notif", .7) for i in range(4)] +
                       [(W_(7, "Écris"), "notif"), (W_(7, "Écris") + .2, "scribble", .5), (W_(7, "commentaire"), "pop2"), (W_(7, "Allez"), "whoosh"),
                        (W_(7, "Allez"), "boom", .5)], trans="polaroid", pad_out=.35),
    SC("munich", 8, s8, [(.0, "boom", .7), (.0, "crowd_long", .7), (.05, "stamp", .6), (W_(8, "Munich"), "pop"), (W_(8, "grand"), "stamp", .7),
                         (W_(8, "Corner") - .1, "whoosh", .5), (W_(8, "Corner"), "kick", .6), (W_(8, "tête") + .05, "thud"),
                         (W_(8, "tête") + .33, "crowd_long", 1.0), (W_(8, "Boli"), "stamp"), (W_(8, "Marseille") - .1, "whoosh", .6),
                         (W_(8, "champion"), "stamp"), (W_(8, "champion"), "sparkle"), (W_(8, "jamais") - .05, "stamp"), (W_(8, "jamais"), "boom", .6)],
       trans="punch", trans_dur=.35),
    SC("va_om", 9, s9, [(.0, "heart", .8), (W_(9, "avant"), "pop"), (W_(9, "Valenciennes"), "stamp", .6), (W_(9, "Et") - .1, "whoosh", .5),
                        (W_(9, "joueurs"), "paper"), (W_(9, "payés"), "cash"), (W_(9, "payés"), "glitch", .6, .35), (W_(9, "lever"), "pop"),
                        (W_(9, "L'argent") - .1, "siren", .8), (W_(9, "L'argent"), "dig", 1.0), (W_(9, "enterré"), "sparkle"),
                        (W_(9, "jardin") - .1, "stamp")], trans="tear_d", trans_dur=.6),
    SC("d2", 10, s10, [(.0, "whoosh_up", .6), (W_(10, "explose"), "boom"), (W_(10, "explose"), "flash", .7), (W_(10, "perd"), "scribble", .6),
                       (W_(10, "titre"), "stamp"), (W_(10, "et") - .1, "whoosh", .5), (W_(10, "envoyé") - .05, "elevator", 1.0),
                       (W_(10, "division") + .1, "stamp"), (W_(10, "Bernard") - .1, "whoosh", .5), (W_(10, "prison") - .15, "jail", 1.0),
                       (W_(10, "prison"), "gasp", .5)], trans="punch", trans_dur=.35),
    SC("renaissance", 11, s11, [(.0, "whoosh_up", .7), (.1, "crowd_long", .9), (W_(11, "relève"), "stamp", .6), (W_(11, "Drogba") - .1, "whoosh", .6),
                                (W_(11, "Drogba"), "boom", .6), (W_(11, "enflamme"), "crowd", .8), (W_(11, "et") - .1, "whoosh", .6),
                                (W_(11, "deux"), "pop2"), (W_(11, "capitaine"), "pop"), (W_(11, "titre"), "stamp"), (W_(11, "titre"), "sparkle")],
       trans="whip"),
    SC("fin", 12, s12, [(W_(12, "PSG") - .1, "stamp", .6), (W_(12, "gagné"), "pop"), (W_(12, "Mais") - .1, "whoosh", .6),
                        (W_(12, "premiers"), "stamp"), (W_(12, "premiers"), "crowd_long", .8), (W_(12, "toujours"), "pop2"),
                        (W_(12, "Et") - .1, "whoosh"), (W_(12, "Et"), "boom", .6), (W_(12, "team"), "pop"), (W_(12, "team", 2), "pop"),
                        (W_(12, "commentaire"), "notif"), (W_(12, "abonne-toi"), "pop2"), (W_(12, "abonne-toi") + .5, "notif"),
                        (W_(12, "abonne-toi"), "sparkle")], trans="tear_v", trans_dur=.6, pad_out=1.3),
]
SCENES[6].trans_dur = 99      # la photo figée reste épinglée pendant toute la pause
SCENES[6].post = s7_post

# ------------------------------------------------------------------ couverture
def cover(path):
    cv = background(0, TITLE); stage_fill(cv, 0, (24, 30, 64), "omcov"); d = ImageDraw.Draw(cv)
    rays(cv, (CX, 1100), 0.3, 1.0, 16, 1500, (220, 180, 80))
    Label("CHAMPION D'EUROPE…", "omcv1", font("title", 82), PAL["ink"], GOLD, maxw=1040, padx=26, pady=10, rough=5).draw(cv, 0, CX, 290, 1, -3)
    Label("…PUIS EN D2 ?!", "omcv2", font("title", 124), PAL["cream"], ROUGE, maxw=1040, padx=36, pady=10, rough=5).draw(cv, 0, CX, 470, 1, 2)
    UCL.draw(cv, 0, 360, 1080, 2.0, 12)
    floor_panel(cv, 0, 790, 900, "D2", 0, True, 1.3, 1)
    ARROW_DOWN.draw(cv, 0, 790, 1250, .8, 0)
    OMP.draw(cv, 0, 560, 1640, .75, age=1, kit="om", mood="surprised", arms=(150, 150), t=1)
    Label("L'HISTOIRE FOLLE DE L'OM", "omcv3", font("title", 70), PAL["cream"], CIEL_D, padx=30, pady=12).draw(cv, 0, CX, 1690, 1, 1)
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
        p = os.path.join(out, f"om_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", "om")
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/om_stills"), only=only)); sys.exit()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25))
