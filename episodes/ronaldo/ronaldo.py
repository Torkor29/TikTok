"""Épisode « Légendes du foot » #2 : Cristiano Ronaldo.
Accroche en devinette (silhouette + 3 indices), appel à commenter au milieu (arrêt sur image),
montage nerveux : plusieurs plans par scène, mots clés calés sur la voix, filés, glitch, zooms.

  python3 episodes/ronaldo/ronaldo.py output/ronaldo --stills [3,4]
  python3 episodes/ronaldo/ronaldo.py output/ronaldo --cover
  python3 episodes/ronaldo/ronaldo.py output/ronaldo
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from story import *
import engine

TITLE = "~/légendes $ ./cristiano_ronaldo"
SLUG = "ronaldo_legende"
VOICE = [os.path.join(HERE, "voix", f"scene_{i}.mp3") for i in range(1, 13)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
ALIGN = os.path.join(HERE, "alignement.json")
PAD = 0.15
WS, TEXTS = load_words(ALIGN)
def w(i, word, n=1, end=False):
    """Temps local (dans la scène i) où la voix prononce `word`."""
    return PAD + WS[i-1](word, n, end)

CR = Player("cr7", hair=(40, 30, 26), skin=(214, 164, 124), hair_style="quiff")
FERG = Player("ferg", hair=(228, 226, 222), skin=(238, 182, 152))
EDER = Player("eder", hair=(28, 24, 22), skin=(118, 80, 58))
DEF1 = Player("def1", hair=(110, 74, 48)); DEF2 = Player("def2", hair=(196, 150, 90), skin=(236, 190, 160))
TEENS = [Player("teen1", hair=(70, 50, 40)), Player("teen2", hair=(150, 110, 60), skin=(236, 196, 166)), Player("teen3", hair=(30, 26, 24), skin=(170, 120, 90))]
DAD = Player("dad", hair=(48, 38, 32), skin=(206, 160, 124))
GOLD = (236, 186, 48)

# ------------------------------------------------------------------ objets
QM = Label("?", "qm", font("title", 260), PAL["mustard"], None, stroke=6, stroke_fill=PAL["ink"])
HEART = Paper(heart_pts(9), (214, 40, 56), "heart", rough=2, hatch=True, pad=40).add(
    lambda d, a: d.ellipse([a[0]-70, a[1]-60, a[0]-30, a[1]-30], fill=(240, 120, 130)))
_sil = {}
def cr_silhouette():
    if "s" not in _sil:
        L = CR.render_layer(0, 1.0, age=1, kit="portugal", arms=(22, 22), legs=(8, 8))
        a = L.getchannel("A").point(lambda v: 255 if v > 70 else 0)
        S = Image.new("RGBA", L.size, (18, 16, 22, 0)); S.putalpha(a); S.info["anchor"] = L.info["anchor"]
        _sil["s"] = S
    return _sil["s"]

SUITCASE = Paper(rect_pts(120, 90), (150, 96, 60), "suitcase", rough=1.6, hatch=True).add(
    lambda d, a: [d.rectangle([a[0]-24, a[1]-62, a[0]+24, a[1]-44], outline=(90, 56, 36), width=8),
                  d.line([(a[0]-60, a[1]), (a[0]+60, a[1])], fill=(110, 70, 44), width=5)])
MALLET_H = Paper(rect_pts(34, 320), (160, 110, 70), "malleth", rough=1.4)
MALLET = Paper(rect_pts(250, 120), (120, 116, 112), "mallet", rough=1.6, hatch=True)
def draw_mallet(cv, fr, x, y, ang, s=1.0):
    a = math.radians(ang); hx, hy = x + math.sin(a)*300*s, y - math.cos(a)*300*s
    MALLET_H.draw(cv, fr, (x+hx)/2, (y+hy)/2, s, -ang); MALLET.draw(cv, fr, hx, hy, s, -ang)

def _clap_decor(d, a):
    ax, ay = a
    for k in range(6): d.polygon([(ax-190+k*66, ay-150), (ax-160+k*66, ay-150), (ax-190+k*66+34, ay-110), (ax-220+k*66+34, ay-110)], fill=(250, 248, 240))
    d.text((ax, ay-40), "HOLLYWOOD", font=font("mono", 40), fill=(230, 226, 216), anchor="mm")
    d.text((ax, ay+40), "SCÈNE 1985", font=font("mono", 34), fill=(180, 176, 170), anchor="mm")
CLAP = Paper(rect_pts(400, 320), (36, 34, 38), "clap", rough=1.4).add(_clap_decor)

ISLAND = Paper([(-260, 30), (-220, -60), (-120, -110), (0, -130), (140, -100), (240, -40), (270, 40), (200, 90), (40, 110), (-140, 100)],
               (70, 150, 84), "island", rough=5, hatch=True)
HOUSE = Paper(rect_pts(150, 120), (236, 214, 170), "house", rough=2, hatch=True).add(
    lambda d, a: [d.polygon([(a[0]-90, a[1]-60), (a[0], a[1]-130), (a[0]+90, a[1]-60)], fill=(170, 80, 56)),
                  d.rectangle([a[0]-18, a[1]-10, a[0]+18, a[1]+60], fill=(110, 70, 50)),
                  d.rectangle([a[0]+34, a[1]-30, a[0]+62, a[1]-4], fill=(90, 130, 160))])
BANNER = Paper(rect_pts(640, 150), (0, 128, 72), "banner", rough=2.5, hatch=True,
               pattern=lambda d, ox, oy: [d.rectangle([0, oy-75+k*30, 4000, oy-60+k*30], fill=(250, 250, 246)) for k in range(0, 5, 2)]).add(
    lambda d, a: d.text((a[0], a[1]), "SPORTING", font=font("title", 90), fill=(250, 250, 246), anchor="mm", stroke_width=6, stroke_fill=(0, 100, 56)))
MOON = Paper([(70*math.cos(math.radians(a)), 70*math.sin(math.radians(a))) for a in range(50, 311, 10)] +
             [(34 + 60*math.cos(math.radians(a))*.95, 60*math.sin(math.radians(a))*.95) for a in range(300, 59, -10)], (250, 240, 196), "moon", rough=1.4)
WINDOW = Paper(rect_pts(300, 360), (40, 56, 100), "window", rough=2).add(
    lambda d, a: [d.rectangle([a[0]-150, a[1]-180, a[0]+150, a[1]+180], outline=(120, 90, 60), width=18), d.line([(a[0], a[1]-180), (a[0], a[1]+180)], fill=(120, 90, 60), width=12)])
MONITOR = Paper(rect_pts(820, 260), (18, 30, 24), "monitor", rough=1.6)
CLOCK = Paper(ellipse_pts(230, 230, 40), (250, 246, 234), "clock", rough=1.6).add(
    lambda d, a: [d.line([(a[0]+95*math.cos(k*math.pi/6), a[1]+95*math.sin(k*math.pi/6)), (a[0]+108*math.cos(k*math.pi/6), a[1]+108*math.sin(k*math.pi/6))], fill=PAL["ink"], width=6) for k in range(12)])
HOSPITAL = Paper(rect_pts(560, 480), (246, 244, 238), "hospital", rough=2, hatch=True).add(
    lambda d, a: [d.rectangle([a[0]-40, a[1]-210, a[0]+40, a[1]-110], fill=(214, 40, 56)), d.rectangle([a[0]-90, a[1]-180, a[0]+90, a[1]-140], fill=(214, 40, 56)),
                  d.rectangle([a[0]-80, a[1]+60, a[0]+80, a[1]+240], fill=(120, 160, 190)),
                  [d.rectangle([a[0]-230+k*130, a[1]-60, a[0]-160+k*130, a[1]+10], fill=(120, 160, 190)) for k in (0, 3)]])
BUS = Paper(rect_pts(900, 380), (206, 26, 36), "bus", rough=2.4, hatch=True).add(
    lambda d, a: [d.rectangle([a[0]-450, a[1]+110, a[0]+450, a[1]+140], fill=(250, 250, 246)),
                  d.text((a[0]+150, a[1]+80), "MANCHESTER", font=font("title", 44), fill=(250, 250, 246), anchor="mm")])
FRAME = Paper(rect_pts(380, 470), (120, 86, 56), "frame", rough=2, hatch=True).add(
    lambda d, a: d.rectangle([a[0]-150, a[1]-195, a[0]+150, a[1]+195], fill=(226, 222, 212)))
GLASS = Paper([(-60, -110), (60, -110), (40, 0), (8, 20), (8, 110), (50, 126), (-50, 126), (-8, 110), (-8, 20), (-40, 0)], (230, 236, 240), "glass", rough=1.2).add(
    lambda d, a: d.polygon([(a[0]-54, a[1]-60), (a[0]+54, a[1]-60), (a[0]+38, a[1]-4), (a[0]-38, a[1]-4)], fill=(150, 30, 50)))
SILVER_CUP = Paper(poly_pts([(-72, -92), (72, -92), (60, 10), (22, 50), (16, 96), (52, 112), (52, 134), (-52, 134), (-52, 112), (-16, 96), (-22, 50), (-60, 10)]),
                   (206, 212, 222), "eurocup", rough=1.6, hatch=True, pad=60).add(
    lambda d, a: d.ellipse([a[0]-70, a[1]-100, a[0]+70, a[1]-76], fill=(240, 244, 250)))
CARD = Paper(rect_pts(190, 250), PAL["paper"], "card", rough=2)
BAR_BG = Paper(rect_pts(820, 90), (60, 56, 64), "barbg", rough=2)
DUNE = Paper(ellipse_pts(1400, 420, 60), (214, 172, 110), "dune", rough=4, hatch=True)
SUN = Paper(ellipse_pts(220, 220, 40), PAL["mustard"], "sun", rough=2)
JB28 = jersey_back("manutd", "RONALDO", 28); JB7 = jersey_back("manutd", "RONALDO", 7)
BILL = Paper(rect_pts(160, 80), (70, 150, 120), "bill2", rough=1.4, hatch=True).add(
    lambda d, a: [d.rectangle([a[0]-70, a[1]-34, a[0]+70, a[1]+34], outline=PAL["cream"], width=3), d.text((a[0], a[1]), "€", font=font("title", 50), fill=PAL["cream"], anchor="mm")])
def bill_rain(cv, fr, t, t0, dur=3.0, n=18, key="bills"):
    if t < t0: return
    rnd = random.Random(key)
    for i in range(n):
        tt = t - t0 - rnd.uniform(0, dur*.5)
        if tt < 0: continue
        x = rnd.uniform(90, 990) + 50*math.sin(tt*2+i); y = 150 + tt*rnd.uniform(420, 640)
        if y < 1950: BILL.draw(cv, fr, x, y, rnd.uniform(.8, 1.1), 30*math.sin(tt*3+i))

def score2(cv, fr, x, y, la, lb, a, b, sub="", s=1.0):
    if s <= .02: return
    L = layer(900, 420, (450, 210)); scoreboard_sprite(820, 330, "score2").draw(L, fr, 450, 210, 1, 0, 1)
    d = ImageDraw.Draw(L)
    d.text((180, 130), la, font=font("mono", 64), fill=(200, 196, 190), anchor="mm"); d.text((720, 130), lb, font=font("mono", 64), fill=(200, 196, 190), anchor="mm")
    d.text((450, 220), f"{a} - {b}", font=font("title", 150), fill=(255, 204, 70), anchor="mm")
    if sub: d.text((450, 330), sub, font=font("mono", 40), fill=(170, 166, 160), anchor="mm")
    blit(cv, L, x, y, s)

def walk(t, speed=9, amp=22):
    ph = math.sin(t*speed); return (amp*ph, -amp*ph), abs(math.sin(t*speed))*8

# ------------------------------------------------------------------ labels
H1 = HL("QUI EST-CE ?", "h1", PAL["mustard"], PAL["ink"], 100)
K1a = KW("UN PRÉSIDENT ?", "k1a", (30, 50, 110), size=76)
K1b = KW("OPÉRÉ DU CŒUR", "k1b", (190, 30, 50), size=76)
K1d = KW("TU L'AS RECONNU ?", "k1d", PAL["mustard"], PAL["ink"], 84)
N2 = STAMP("CRISTIANO RONALDO", "n2", (196, 18, 48), 100)
K2a = KW("SIUUU !", "k2a", PAL["mustard"], PAL["ink"], 120)
K2b = KW("1985", "k2b", PAL["teal"], size=150)
T2a = TAG("île de Madère", "t2a", PAL["paper"])
T2b = TAG("famille modeste", "t2b", PAL["mustard"])
K2c = KW("RONALD REAGAN", "k2c", (190, 30, 50), size=96)
T2c = TAG("l'acteur préféré de son père", "t2c", PAL["paper"], size=50)
K2d = KW("PRÉSIDENT DES USA", "k2d", (30, 50, 110), size=88)
K2e = KW("« RONALDO » ?", "k2e", PAL["mustard"], PAL["ink"], 96)
K3a = KW("12 ANS", "k3a", PAL["ink"], size=130); K3b = KW("SEUL", "k3b", (190, 30, 50), size=120)
T3a = TAG("Lisbonne", "t3a"); K3c = KW("SON ACCENT", "k3c", PAL["mustard"], PAL["ink"], 100)
HAHA = [LBL("HA HA", f"haha{i}", font("title", 64), PAL["ink"], PAL["white"], padx=20, pady=8, rough=2) for i in range(4)]
T3b = TAG("presque tous les soirs", "t3b", (40, 56, 100), PAL["cream"])
K3d = STAMP("IL NE LÂCHE RIEN", "k3d", (190, 30, 50), 100)
K4a = KW("15 ANS", "k4a", PAL["ink"], size=130); K4b = STAMP("COUP DE MASSUE", "k4b", (190, 30, 50), 96)
K4c = KW("TACHYCARDIE", "k4c", (190, 30, 50), size=100); T4a = TAG("son cœur s'emballe, même au repos", "t4a", PAL["paper"], size=46)
K4d = KW("IL FAUT L'OPÉRER", "k4d", PAL["ink"], size=88); K4e = KW("LASER", "k4e", (190, 30, 50), size=120)
T4b = TAG("opéré le matin… dehors le soir", "t4b", PAL["paper"], size=48); K4f = KW("DÉJÀ SORTI !", "k4f", PAL["teal"], size=100)
K4g = KW("REJOUER !", "k4g", PAL["mustard"], PAL["ink"], 130)
K5a = KW("2003", "k5a", PAL["cream"], (190, 30, 50), 220); T5a = TAG("match amical", "t5a")
K5b = KW("MANCHESTER UNITED", "k5b", (190, 30, 50), size=84); K5c = KW("18 ANS", "k5c", PAL["ink"], size=110)
K5d = STAMP("RIDICULISÉS !", "k5d", (190, 30, 50), 110); T5b = TAG("Sir Alex Ferguson", "t5b", PAL["paper"], size=48)
K5e = STAMP("IL FAUT LE SIGNER !", "k5e", (190, 30, 50), 92)
K6a = KW("28 ?", "k6a", PAL["ink"], size=110); K6b = KW("LE 7", "k6b", GOLD, PAL["ink"], 150)
T6a = TAG("après Best, Cantona, Beckham", "t6a", PAL["paper"], size=50)
K7a = KW("PETITE PAUSE !", "k7a", PAL["ink"], size=70); K7b = KW("QUEL JOUEUR ?", "k7b", (190, 30, 50), size=80)
NAMES = [LBL(n, f"nm{n}", font("hand", 46), PAL["ink"], None) for n in ("Zidane ?", "Mbappé ?", "Neymar ?", "Ibra ?")]
K7c = KW("EN COMMENTAIRE", "k7c", PAL["teal"], size=84); K7d = KW("ON REPREND !", "k7d", PAL["ink"], size=96)
K8a = KW("2005", "k8a", (90, 90, 96), size=130); K8b = KW("ZÉRO ALCOOL", "k8b", (190, 30, 50), size=96)
K9a = KW("2009", "k9a", GOLD, PAL["ink"], 150); K9b = STAMP("RECORD DU MONDE", "k9b", (190, 150, 20), 100)
T9a = TAG("juste pour sa présentation", "t9a", PAL["paper"], size=50); K9c = KW("BUTS", "k9c", PAL["ink"], size=90)
T9b = TAG("4 Ligues des champions", "t9b", PAL["mustard"], size=54)
K10a = KW("EURO 2016", "k10a", (196, 18, 48), size=120); K10b = STAMP("FINALE", "k10b", PAL["ink"], 110)
K10c = KW("BLESSÉ", "k10c", (190, 30, 50), size=130); T10a = TAG("il sort en larmes (25e minute)", "t10a", PAL["paper"], size=46)
T10b = TAG("au bord du terrain", "t10b"); K10d = KW("COACH CR7", "k10d", PAL["mustard"], PAL["ink"], 120)
K10e = KW("1 - 0 !", "k10e", PAL["ink"], size=140); T10c = TAG("Éder, 109e minute", "t10c", PAL["paper"], size=50)
K10f = STAMP("CHAMPIONS D'EUROPE !", "k10f", (196, 18, 48), 84)
K11a = KW("AL NASSR", "k11a", (20, 50, 150), size=110); K11b = STAMP("RECORD", "k11b", (190, 150, 20), 130)
T11a = TAG("le plus gros contrat du sport", "t11a", PAL["paper"], size=50); T11b = TAG("selon la presse", "t11b", PAL["paper"], size=44)
K12a = KW("41 ANS", "k12a", PAL["ink"], size=130); K12b = KW("6 COUPES DU MONDE", "k12b", (196, 18, 48), size=84)
K12c = KW("1000 ?", "k12c", GOLD, PAL["ink"], 150)
BTN_OUI = Label("OUI", "boui", font("title", 110), PAL["cream"], PAL["teal"], padx=60, pady=10, rough=3)
BTN_NON = Label("NON", "bnon", font("title", 110), PAL["cream"], PAL["coral"], padx=60, pady=10, rough=3)
BTN_SUB = Label("+ ABONNE-TOI", "bsub", font("title", 96), (255, 255, 255), (230, 40, 80), padx=40, pady=14, rough=2.5)
K12d = KW("PROCHAINE LÉGENDE ?", "k12d", PAL["ink"], size=80)
YEARS = [LBL(str(y), f"yr{y}", font("title", 40), PAL["ink"], PAL["paper"], padx=10, pady=4) for y in (2006, 2010, 2014, 2018, 2022, 2026)]

# ------------------------------------------------------------------ SCÈNE 1 — la devinette
def s1(cv, fr, t, T):
    stage_fill(cv, fr, (38, 36, 44), "s1bg"); d = ImageDraw.Draw(cv)
    rays(cv, (CX, 1060), t, .45, 10, 1300, (80, 76, 92), .12, .15)
    hl(cv, fr, H1, t, 0.0)
    pulse = 1 + .025*math.sin(t*7) + .06*pop_in(t, w(1, "reconnu"), .3)*(1-prog(t, w(1, "reconnu")+.3, .3))
    blit(cv, cr_silhouette(), CX, 1480, 1.0*pulse)
    QM.draw(cv, fr, CX+200, 860 + 12*math.sin(t*4), 1.0*win(t, .15), 12)
    t1 = w(1, "président"); t2 = w(1, "l'opère"); t3 = w(1, "deux"); t4 = w(1, "Tu")
    us_flag(cv, 190, 520, a=pop_in(t, t1)); kw(cv, fr, K1a, t, t1, None, 640, 520, -4)
    if t > t2:
        hb = 1 + .12*abs(math.sin((t-t2)*9)); HEART.draw(cv, fr, 880, 690, .75*pop_in(t, t2)*hb, 8)
        kw(cv, fr, K1b, t, t2, None, 450, 690, 3)
    if t > t3:
        v = counter(0, 200000000, prog(t, t3, 1.0))
        LBL(f"{v} €", "money1", font("title", 96), GOLD, None, stroke=5, stroke_fill=PAL["ink"]).draw(cv, fr, CX, 1020, pop_in(t, t3), -2)
        LBL("par an", "parAn", font("hand", 56), PAL["cream"], None).draw(cv, fr, CX, 1110, pop_in(t, t3+.3), 0)
    kw(cv, fr, K1d, t, t4, None, CX, 1290, -2)
    for tt in (t1, t2): impact(cv, t, tt, 10)
    glitch(cv, fr, t, t4, .4, 16); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 2 — révélation, Madère, Ronald Reagan
def s2a(cv, fr, t):   # SIUUU
    stage_fill(cv, fr, (196, 18, 48), "s2red")
    rays(cv, (CX, 1000), t, 1.0, 16, 1500, (230, 190, 90))
    land = w(2, "Ronaldo"); hop = 260*math.sin(clamp(t/land)*math.pi) if t < land else 0
    spin = clamp(t/land)
    if t < land:
        L = CR.render_layer(fr, 1.1, age=1, kit="portugal", arms=(160, 160), mood="cheer")
        blit_sxy(cv, L, CX, 1500-hop, max(.05, abs(math.cos(spin*math.pi*2))), 1.0)
    else:
        CR.draw(cv, fr, CX, 1500, 1.1, age=1, kit="portugal", arms=(38, 38), legs=(14, 14), mood="cheer", t=t)
    show_stamp(cv, fr, N2, t, .12, CX, 400, -4)
    kw(cv, fr, K2a, t, land, None, CX, 620, 4)
    confetti(cv, fr, "c2", t-land, 70, 4)
    impact(cv, t, land, 20); flashes(cv, t, land, .15, .8)

def s2b(cv, fr, t):   # Madère
    stage_fill(cv, fr, (150, 200, 222), "s2sea"); d = ImageDraw.Draw(cv)
    for k in range(7):
        yy = 700 + k*130
        pencil_line(d, [(80+j*45, yy+10*math.sin(j*.8+t*2+k)) for j in range(22)], 1, (120, 176, 200), 4, k, .6)
    ISLAND.draw(cv, fr, CX, 1250, 1.2)
    if t > w(2, "famille")-.1: HOUSE.draw(cv, fr, 380, 1180, pop_in(t, w(2, "famille")-.1))
    CR.draw(cv, fr, 640, 1300, .55, age=0, kit="madeira", mood="happy", t=t, legs=(0, 20*abs(math.sin(t*6))))
    draw_ball(cv, fr, 700, 1170 - abs(math.sin(t*6))*120, .45, t*300)
    kw(cv, fr, K2b, t, w(2, "mille"), None, CX, 470, -3)
    show(cv, fr, T2a, t, w(2, "l'île"), None, 700, 1000, 2)
    show(cv, fr, T2b, t, w(2, "famille"), None, 330, 980, -2)

def s2c(cv, fr, t):   # Ronald Reagan
    stage_fill(cv, fr, (110, 26, 38), "s2curtain"); d = ImageDraw.Draw(cv)
    for k in range(9):   # plis du rideau
        x = 60 + k*120; d.line([(x, 130), (x+10*math.sin(t+k), 1880)], fill=(90, 18, 30), width=14)
    rays(cv, (CX, 860), t, .5, 12, 900, (250, 220, 150))
    tp = w(2, "président"); fu = prog(t, tp-.1, .35)
    sx = math.cos(fu*math.pi)
    if fu < .5:
        blit_sxy(cv, CLAP.v[boil(fr)], CX, 860, max(.04, abs(sx))*pop_in(t, w(2, "Son")-.05), pop_in(t, w(2, "Son")-.05))
    else:
        us_flag(cv, CX, 860, 520, 330, max(.04, abs(sx)))
        camera_flashes(cv, fr, "cf2", t-tp, 1.5, 10)
    kw(cv, fr, K2e, t, w(2, "Ronaldo", 2), w(2, "Ronald", 3)-.08, CX, 500, 3)
    kw(cv, fr, K2c, t, w(2, "Ronald", 3), tp-.15, CX, 500, -3)
    draw_star(cv, 880, 420, 50, pop_in(t, w(2, "Ronald", 3)), t)
    show(cv, fr, T2c, t, w(2, "acteur"), tp-.1, CX, 1180, 2)
    kw(cv, fr, K2d, t, tp, None, CX, 500, 3)

def s2(cv, fr, t, T):
    shots(cv, fr, t, [(0, s2a), (w(2, "Né")-.1, s2b), (w(2, "Son")-.1, s2c)])
    drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 3 — seul à Lisbonne
def s3a(cv, fr, t):
    stage_fill(cv, fr, (236, 228, 208), "s3a")
    ts = w(3, "Sporting")
    BANNER.draw(cv, fr, CX, 820, pop_in(t, ts-.2), -2)
    x = lerp(-150, 520, ease_out_cubic(prog(t, .1, 1.6))); lg, bob = walk(t) if t < 1.7 else ((0, 0), 0)
    su = prog(t, ts, .45)
    if 0 < su < 1:
        L = CR.render_layer(fr, .85, age=.3, kit="madeira" if su < .25 else "sporting", mood="normal")
        blit_sxy(cv, L, x, 1480, max(.04, abs(math.cos(su*math.pi*2))), 1)
    else:
        CR.draw(cv, fr, x, 1480-bob, .85, age=.3, kit="sporting" if su >= 1 else "madeira", legs=lg, mood="normal", t=t)
    if su < .2: SUITCASE.draw(cv, fr, x+120, 1250-bob, .9, 4)
    kw(cv, fr, K3a, t, w(3, "douze"), None, 330, 450, -4)
    kw(cv, fr, K3b, t, w(3, "seul"), None, 760, 560, 5)
    show(cv, fr, T3a, t, w(3, "Lisbonne"), None, 330, 620, -2)

def s3b(cv, fr, t):
    stage_fill(cv, fr, (120, 136, 150), "s3b")
    tm = w(3, "moque")
    for i, (P, x) in enumerate(zip(TEENS, (200, 880, 330))):
        P.draw(cv, fr, x, 1500 if i < 2 else 1560, .8, age=.5, kit="sporting", mood="happy", t=t, lean=6*math.sin(t*12+i))
    CR.draw(cv, fr, 600, 1520, .85, age=.3, kit="sporting", mood="sad", t=t, look=(0, 1))
    for i, lab in enumerate(HAHA):
        a = pop_in(t, tm + i*.18)
        if a > 0: lab.draw(cv, fr, (220, 860, 300, 800)[i], (760, 820, 960, 1010)[i] + 8*math.sin(t*10+i), a, (-8, 6, 10, -5)[i])
    kw(cv, fr, K3c, t, w(3, "accent"), None, CX, 470, -3)

def s3c(cv, fr, t):
    stage_fill(cv, fr, (30, 40, 76), "s3night")
    WINDOW.draw(cv, fr, 760, 700, 1); MOON.draw(cv, fr, 780, 660, .8, -20)
    tp = w(3, "pleure")
    CR.draw(cv, fr, 440, 1500, .9, age=.3, kit="sporting", mood="sad", t=t, look=(0, 1), tears=t-tp if t > tp else 0)
    show(cv, fr, T3b, t, w(3, "presque"), None, 440, 520, -2)

def s3d(cv, fr, t):
    stage_fill(cv, fr, PAL["mustard"], "s3d")
    rays(cv, (CX, 1000), t, .8, 14, 1300, (250, 220, 120))
    CR.draw(cv, fr, CX, 1500, 1.0, age=.35, kit="sporting", mood="determined", arms=(8, 150), t=t)
    show_stamp(cv, fr, K3d, t, w(3, "lâche")-.05, CX, 520, -5)

def s3(cv, fr, t, T):
    shots(cv, fr, t, [(0, s3a), (w(3, "On")-.1, s3b), (w(3, "Il", 2)-.1, s3c), (w(3, "mais")-.08, s3d)])
    impact(cv, t, w(3, "lâche")-.05, 16); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 4 — le cœur
def ecg(d, x0, y0, w_, t, speed=2.2, fast=True):
    pts = []
    for k in range(120):
        x = x0 + k*w_/120; ph = (k/120*3.2 + t*speed) % 1.0
        y = y0 - (140 if .46 < ph < .5 else (-60 if .5 <= ph < .54 else (20*math.sin(ph*math.pi*2) if ph < .3 else 0)))
        pts.append((x, y))
    d.line(pts, fill=(90, 255, 140), width=6)

def s4a(cv, fr, t):
    stage_fill(cv, fr, (34, 32, 40), "s4a")
    tm = w(4, "massue")
    kw(cv, fr, K4a, t, w(4, "quinze"), None, CX, 450, -3)
    ang = lerp(-70, 10, ease_in_cubic(prog(t, tm-.35, .35))) if t < tm + .1 else lerp(10, -10, prog(t, tm+.1, .4))
    draw_mallet(cv, fr, 780, 1500, ang, 1.2)
    show_stamp(cv, fr, K4b, t, tm, CX, 1000, -6)
    particles(cv, fr, "m4", (CX, 1100), prog(t, tm, .6), 24, 380, [PAL["cream"], (120, 116, 112)])

def s4b(cv, fr, t):
    stage_fill(cv, fr, (90, 20, 32), "s4b"); d = ImageDraw.Draw(cv)
    hb = 1 + .14*abs(math.sin(t*10))
    HEART.draw(cv, fr, CX, 860, 1.25*hb*pop_in(t, w(4, "cœur")-.15))
    MONITOR.draw(cv, fr, CX, 1300, 1); ecg(d, 150, 1320, 780, t, 3.0)
    kw(cv, fr, K4c, t, w(4, "vite"), w(4, "Il")-.1, CX, 480, -3)
    show(cv, fr, T4a, t, w(4, "repos"), None, CX, 1560, 1)
    kw(cv, fr, K4d, t, w(4, "l'opérer"), None, CX, 480, 3)

def s4c(cv, fr, t):
    stage_fill(cv, fr, (60, 20, 30), "s4c"); d = ImageDraw.Draw(cv)
    tl = w(4, "Laser")
    HEART.draw(cv, fr, CX, 960, 1.1*(1 + .05*math.sin(t*6)))
    if tl <= t < tl + 1.2:
        wd = 14 + 8*math.sin(t*50)
        d.line([(CX, 130), (CX+10, 900)], fill=(255, 90, 90), width=int(wd*2)); d.line([(CX, 130), (CX+10, 900)], fill=(255, 230, 230), width=int(wd*.6))
        particles(cv, fr, f"sp{int(t*8)}", (CX+10, 900), (t*8) % 1, 14, 160, [(255, 220, 120), (255, 120, 90)], 10, 200)
    kw(cv, fr, K4e, t, tl, w(4, "et", 2)-.1, 300, 520, -6)
    ca = pop_in(t, w(4, "matin")-.1)
    if ca > 0:
        CLOCK.draw(cv, fr, 800, 520, ca); hand = prog(t, w(4, "matin"), 1.4)*math.pi*2*1.5
        d.line([(800, 520), (800+70*math.sin(hand), 520-70*math.cos(hand))], fill=PAL["ink"], width=8)
        d.line([(800, 520), (800+45*math.sin(hand/12), 520-45*math.cos(hand/12))], fill=PAL["ink"], width=10)
    show(cv, fr, T4b, t, w(4, "fin"), None, CX, 1480, -2)

def s4d(cv, fr, t):
    stage_fill(cv, fr, (170, 200, 214), "s4d")
    HOSPITAL.draw(cv, fr, CX, 1100, 1)
    ts = w(4, "sorti"); x = lerp(CX, 820, ease_out_cubic(prog(t, ts-.5, 1.0))); lg, bob = walk(t)
    CR.draw(cv, fr, x, 1560-bob, .75, age=.45, kit="sporting", mood="happy", t=t, legs=lg, arms=(20, 60))
    kw(cv, fr, K4f, t, ts, None, 360, 520, -4)

def s4e(cv, fr, t):
    pitch(cv, fr, "p4")
    tk = w(4, "rejouer")
    kick = math.sin(prog(t, tk-.1, .3)*math.pi)
    CR.draw(cv, fr, 400, 1500, 1.0, age=.45, kit="sporting", mood="determined", legs=(0, 50*kick), t=t)
    u = prog(t, tk, .6); p = bezier((470, 1470), (700, 1100), (1100, 700), u)
    draw_ball(cv, fr, p[0], p[1], .6, t*800)
    if t > tk: speed_lines(cv, fr, (700, 1100), prog(t, tk, .2), seed=4)
    kw(cv, fr, K4g, t, tk, None, CX, 520, -4)

def s4(cv, fr, t, T):
    shots(cv, fr, t, [(0, s4a), (w(4, "son")-.1, s4b), (w(4, "Laser")-.12, s4c), (w(4, "est")-.2, s4d), (w(4, "rejouer")-.3, s4e)])
    impact(cv, t, w(4, "massue"), 22); glitch(cv, fr, t, w(4, "massue"), .3, 18); glitch(cv, fr, t, w(4, "l'opérer"), .35, 14)
    flashes(cv, t, w(4, "Laser"), .15, .7); punch(cv, t, w(4, "rejouer"), 1.08); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 5 — Manchester United 2003
def s5a(cv, fr, t):
    stage_fill(cv, fr, (170, 20, 30), "s5a")
    kw(cv, fr, K5a, t, .05, None, CX, 900, -4)

def s5b(cv, fr, t):
    pitch(cv, fr, "p5")
    tr = w(5, "ridiculise"); du = prog(t, tr, 1.0)
    x = lerp(230, 860, ease_io(du))
    step = math.sin(t*22)*30 if 0 < du < 1 else 0
    for i, (P, dx) in enumerate(((DEF1, 540), (DEF2, 760))):
        tf = tr + .25 + i*.3; fall = ease_out_cubic(prog(t, tf, .35))
        if fall <= 0:
            P.draw(cv, fr, dx, 1480, .9, age=1, kit="manutd", mood="determined", t=t, look=(-1, 0))
        else:
            L = P.render_layer(fr, .9, age=1, kit="manutd", mood="surprised")
            blit(cv, L, dx + 60*fall, 1480, 1, -85*fall*(1 if i else -1))
    CR.draw(cv, fr, x, 1500, .95, age=.8, kit="sporting", mood="determined", legs=(step, -step), arms=(30, 30), t=t)
    draw_ball(cv, fr, x + 70 + (20*math.sin(t*22) if 0 < du < 1 else 0), 1465, .5, t*600)
    if 0 < du < 1: speed_lines(cv, fr, (x, 1200), .7, seed=5, inner=300)
    show(cv, fr, T5a, t, w(5, "amical"), None, 300, 450, -3)
    kw(cv, fr, K5b, t, w(5, "Manchester"), w(5, "Il")-.1, CX, 600, 3)
    kw(cv, fr, K5c, t, w(5, "dix-huit"), w(5, "ridiculise")-.05, CX, 600, -3)
    show_stamp(cv, fr, K5d, t, w(5, "défense"), CX, 620, -6)

def s5c(cv, fr, t):
    stage_fill(cv, fr, (96, 100, 108), "s5road"); d = ImageDraw.Draw(cv)
    for k in range(8):   # marquage de la route qui défile
        x = (k*180 - (t*900) % 180); d.rectangle([x, 1450, x+100, 1470], fill=(240, 236, 220))
    bx, by = CX, 1150 + 6*math.sin(t*20)
    BUS.draw(cv, fr, bx, by, 1)
    for k in range(5):   # fenêtres + têtes
        wx = bx - 330 + k*165
        d.rectangle([wx-60, by-140, wx+60, by-30], fill=(180, 210, 230))
        P = FERG if k == 0 else [DEF1, DEF2, TEENS[0], TEENS[2]][k-1]
        ImageDraw.Draw(cv)
        P.head.draw(cv, fr, wx, by-70, .55); (P.hair_adult).draw(cv, fr, wx, by-70, .55)
        d.ellipse([wx-12, by-76, wx-4, by-66], fill=PAL["ink"]); d.ellipse([wx+4, by-76, wx+12, by-66], fill=PAL["ink"])
    for k in range(2):
        wx = bx - 300 + k*600; ang = t*12
        d.ellipse([wx-55, by+140, wx+55, by+250], fill=(30, 30, 30)); d.line([(wx, by+195), (wx+40*math.cos(ang), by+195+40*math.sin(ang))], fill=(160, 160, 160), width=6)
    td = w(5, "disent")
    for i, k in enumerate((1, 2, 3, 4)):
        a = pop_in(t, td + i*.15)
        if a > 0: speech_bubble(cv, fr, f"sb{k}", "SIGNEZ-LE !", bx - 330 + k*165, by - 260 - (i % 2)*110, .75*a, (0, 1), 46)
    tf = w(5, "Ferguson")
    if t > tf:
        d.ellipse([bx-330-80, by-150, bx-330+80, by-10], outline=PAL["mustard"], width=8)
        show(cv, fr, T5b, t, tf, None, 300, 1560, -2)
    show_stamp(cv, fr, K5e, t, w(5, "signer")-.05, CX, 560, -5)

def s5(cv, fr, t, T):
    shots(cv, fr, t, [(0, s5a), (w(5, "Match")-.08, s5b), (w(5, "Dans")-.1, s5c)])
    impact(cv, t, .05, 16); impact(cv, t, w(5, "défense"), 14); impact(cv, t, w(5, "signer")-.05, 16); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 6 — le numéro 7
def s6(cv, fr, t, T):
    stage_fill(cv, fr, (180, 22, 34), "s6"); d = ImageDraw.Draw(cv)
    t7 = w(6, "sept")
    if t > t7: rays(cv, (CX, 920), t, prog(t, t7, .3), 16, 1300, (250, 210, 110))
    fu = prog(t, t7-.2, .4); sx = math.cos(fu*math.pi); J = JB28 if fu < .5 else JB7
    blit_sxy(cv, J.v[boil(fr)], CX, 920, .8*max(.04, abs(sx))*pop_in(t, .05), .8*pop_in(t, .05), 3)
    kw(cv, fr, K6a, t, w(6, "vingt-huit"), w(6, "Ferguson"), 300, 480, -5)
    tf = w(6, "Ferguson")
    if t > tf and t < t7 + .6:
        a = pop_in(t, tf); FERG.head.draw(cv, fr, 820, 500, 1.1*a); FERG.hair_adult.draw(cv, fr, 820, 500, 1.1*a)
        d.ellipse([806-30, 490, 806-18, 504], fill=PAL["ink"]); d.ellipse([834-18, 490, 834-6, 504], fill=PAL["ink"])
        if t > w(6, "donne")-.1 and fu < .5: pencil_cross(d, CX, 980, 4)
    kw(cv, fr, K6b, t, t7, None, CX, 480, -4)
    show(cv, fr, T6a, t, w(6, "légendes"), None, CX, 1440, 2)
    flashes(cv, t, t7, .15, .7); impact(cv, t, t7, 14); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 7 — PAUSE : quel joueur ?
def s7(cv, fr, t, T):
    stage_fill(cv, fr, PAL["mustard"], "s7"); d = ImageDraw.Draw(cv)
    kw(cv, fr, K7a, t, .05, None, 740, 330, 4)
    kw(cv, fr, K7b, t, w(7, "Quel"), None, 740, 520, -3)
    tp = w(7, "prochain")
    for i in range(4):
        a = pop_in(t, tp + i*.14)
        if a <= 0: continue
        x = 180 + i*240; y = 1010 + 10*math.sin(t*4+i)
        CARD.draw(cv, fr, x, y, a, (-4, 3, -2, 5)[i])
        QM_S = LBL("?", "qmS", font("title", 130), (60, 56, 64), None); QM_S.draw(cv, fr, x, y-30, a)
        NAMES[i].draw(cv, fr, x, y+90, a)
    te = w(7, "Écris")
    if t > te:
        a = pop_in(t, te)
        speech_bubble(cv, fr, "cta_b", typewriter("Zidane stp !!", prog(t, te+.2, .9)) or " ", 520, 1300, a, (-1, 1), 64)
        bx = 880 + 18*math.sin(t*8)
        arrow(d, (760, 1320), (bx+80, 1180), prog(t, te+.2, .3), PAL["ink"], 10, 7, 34, -.2)
    kw(cv, fr, K7c, t, w(7, "commentaire"), None, 560, 1470, 2)
    kw(cv, fr, K7d, t, w(7, "Allez"), None, 700, 720, -5)
    impact(cv, t, w(7, "Allez"), 14)

def s7_post(cv, fr, t, T):
    """Par-dessus la photo figée : icône PAUSE."""
    a = pop_in(t, .25)
    if a <= 0: return
    d = ImageDraw.Draw(cv); cx, cy, s = 250, 470, a
    d.ellipse([cx-70*s, cy-70*s, cx+70*s, cy+70*s], fill=(34, 32, 36))
    for dx in (-22, 22): d.rectangle([cx+dx*s-12*s, cy-34*s, cx+dx*s+12*s, cy+34*s], fill=(250, 248, 240))

# ------------------------------------------------------------------ SCÈNE 8 — son père
_dad = {}
def dad_photo():
    if "p" not in _dad:
        L = DAD.render_layer(0, .62, age=1, kit="suit", mood="happy")
        g = L.convert("LA").convert("RGBA"); g.info["anchor"] = L.info["anchor"]; _dad["p"] = g
    return _dad["p"]
def s8(cv, fr, t, T):
    stage_fill(cv, fr, (70, 70, 78), "s8"); d = ImageDraw.Draw(cv)
    kw(cv, fr, K8a, t, w(8, "deux"), None, CX, 380, -2)
    a = pop_in(t, w(8, "père")-.1, .5)
    if a > 0:
        FRAME.draw(cv, fr, CX, 780, a)
        if a > .9:
            blit(cv, dad_photo(), CX, 960, 1)
            d.polygon([(CX+150, 545), (CX+190, 545), (CX+190, 600)], fill=(20, 20, 20))
    tg = w(8, "l'alcool")
    if t > tg: GLASS.draw(cv, fr, 800, 1330, pop_in(t, tg), 6)
    tr = w(8, "refuse")
    if t > tr - .3:
        CR.draw(cv, fr, 330, 1560, .8, age=.85, kit="manutd", mood="determined", t=t, arms=(8, lerp(8, 95, prog(t, tr-.3, .3))))
    if t > tr:
        pencil_cross(d, 800, 1330, 3.2)
        kw(cv, fr, K8b, t, tr, None, 640, 1100, -3)
    drift(cv, t, T, .06)

# ------------------------------------------------------------------ SCÈNE 9 — Real Madrid
def s9a(cv, fr, t):
    stage_fill(cv, fr, (246, 240, 226), "s9a")
    rays(cv, (CX, 1000), t, .9, 16, 1400, (240, 210, 130))
    kw(cv, fr, K9a, t, .05, None, CX, 360, -3)
    tr = w(9, "Real"); su = prog(t, tr, .45)
    if 0 < su < 1:
        L = CR.render_layer(fr, 1.0, age=1, kit="manutd" if su < .25 else "real", mood="happy")
        blit_sxy(cv, L, CX, 1520, max(.04, abs(math.cos(su*math.pi*2))), 1)
    else:
        CR.draw(cv, fr, CX, 1520, 1.0, age=1, kit="real" if su >= 1 else "manutd", mood="happy", t=t, arms=(20, 20))
    tm = w(9, "quatre-vingt-quatorze")
    if t > tm:
        LBL(f"{counter(0, 94000000, prog(t, tm, 1.0))} €", "p94", font("title", 100), GOLD, None, stroke=6, stroke_fill=PAL["ink"]).draw(cv, fr, CX, 560, pop_in(t, tm), -2)
    show_stamp(cv, fr, K9b, t, w(9, "Record"), CX, 760, -6)
    camera_flashes(cv, fr, "cf9", t - w(9, "Record"), 1.4, 12)

def s9b(cv, fr, t):
    stage_fill(cv, fr, (22, 30, 70), "s9stad"); d = ImageDraw.Draw(cv)
    rnd = random.Random(9)
    for row in range(9):   # tribunes : têtes qui sautent
        ry = 560 + row*95; n = 16 + row
        for k in range(n):
            x = 80 + k*(920/(n-1)); jump = 10*abs(math.sin(t*9 + k*1.7 + row))
            col = rnd.choice([(250, 250, 246), (212, 170, 60), (236, 204, 170), (180, 140, 110), (120, 80, 60)])
            d.ellipse([x-20, ry-20-jump, x+20, ry+20-jump], fill=col)
    CR.draw(cv, fr, CX, 1640, .55, age=1, kit="real", mood="happy", arms=(20, 150), t=t)
    tk = w(9, "Quatre-vingt", 2)
    v = counter(0, 80000, prog(t, tk, .9))
    LBL(v, "k80", font("title", 170), (250, 250, 246), None, stroke=8, stroke_fill=(22, 30, 70)).draw(cv, fr, CX, 360, pop_in(t, tk), -3)
    LBL("fans", "kfans", font("title", 80), GOLD, None).draw(cv, fr, CX, 480, pop_in(t, tk+.2))
    show(cv, fr, T9a, t, w(9, "présentation"), None, CX, 1400, 2)
    camera_flashes(cv, fr, "cf9b", (t - tk) % 2.0, 2.0, 16)

def s9c(cv, fr, t):
    stage_fill(cv, fr, (246, 240, 226), "s9c")
    tp = w(9, "plante")
    v = counter(0, 450, prog(t, tp, 1.2))
    LBL(v, "g450", font("title", 260), (196, 18, 48), None, stroke=8, stroke_fill=PAL["ink"]).draw(cv, fr, CX, 700, pop_in(t, tp), -3)
    kw(cv, fr, K9c, t, tp+.1, None, CX, 900, 3)
    for k in range(10):
        tk = tp + k*.12
        if tk < t < tk + .5:
            u = prog(t, tk, .5); p = bezier((100 + (k % 3)*90, 1650), (300+k*40, 1200), (1000, 500 + (k % 4)*120), u)
            draw_ball(cv, fr, p[0], p[1], .45, t*500)
    tl = w(9, "Ligues")
    for i in range(4):
        a = pop_in(t, tl + i*.12)
        if a > 0: UCL.draw(cv, fr, 190 + i*233, 1250, .75*a, 4*math.sin(t*3+i))
    show(cv, fr, T9b, t, tl+.4, None, CX, 1520, -2)
    confetti(cv, fr, "c9", t - tl, 60, 4)

def s9(cv, fr, t, T):
    shots(cv, fr, t, [(0, s9a), (w(9, "Quatre-vingt", 2)-.1, s9b), (w(9, "Là-bas")-.1, s9c)])
    impact(cv, t, w(9, "Record"), 18); flashes(cv, t, w(9, "Record"), .12, .6); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 10 — Euro 2016
def s10a(cv, fr, t):
    pitch(cv, fr, "p10")
    kw(cv, fr, K10a, t, .05, None, CX, 380, -3)
    show_stamp(cv, fr, K10b, t, w(10, "finale"), CX, 560, 5)
    score2(cv, fr, CX, 950, "POR", "FRA", 0, 0, "finale", pop_in(t, w(10, "France")-.2))

def s10b(cv, fr, t):
    pitch(cv, fr, "p10b"); tb = w(10, "Blessé")
    CR.draw(cv, fr, CX, 1600, 1.05, age=1, kit="portugal", mood="sad", t=t, lean=-18, legs=(0, 20), tears=t-w(10, "larmes"), look=(0, 1))
    ImageDraw.Draw(cv).rectangle([CX+20, 1600-150, CX+80, 1600-120], fill=(250, 250, 246))
    kw(cv, fr, K10c, t, tb, None, CX, 450, -4)
    show(cv, fr, T10a, t, w(10, "larmes")-.1, None, CX, 600, 2)

def s10c(cv, fr, t):
    pitch(cv, fr, "p10c", (64, 140, 78)); d = ImageDraw.Draw(cv)
    d.rectangle([520, 130, 532, 1890], fill=(240, 240, 232))
    for i, x in enumerate((700, 860, 960)):
        lg, bob = walk(t + i, 12, 20); P = [TEENS[0], TEENS[1], EDER][i]
        P.draw(cv, fr, x, 1300 + i*80 - bob, .6, age=1, kit="portugal", legs=lg, t=t)
    wave = math.sin(t*9)
    CR.draw(cv, fr, 300, 1560, 1.0, age=1, kit="portugal", mood="cheer" if int(t*3) % 2 else "determined", t=t,
            arms=(95 + 50*wave, 95 - 50*wave))
    d.rectangle([300+22, 1560-150, 300+80, 1560-120], fill=(250, 250, 246))
    show(cv, fr, T10b, t, w(10, "bord"), None, 330, 700, -2)
    kw(cv, fr, K10d, t, w(10, "coache"), None, CX, 470, -3)

def s10d(cv, fr, t):
    pitch(cv, fr, "p10d")
    CR.draw(cv, fr, 300, 1560, 1.0, age=1, kit="portugal", mood="determined", t=t, arms=(8, 80))
    EDER.draw(cv, fr, 780, 1560, 1.02, age=1, kit="portugal", mood="surprised" if t < w(10, "marquer") else "determined", t=t, look=(-1, 0))
    a = pop_in(t, w(10, "dit"))
    if a > 0: speech_bubble(cv, fr, "tvm", "TU VAS MARQUER !", 480, 560, a, (-1, 1), 64)
    LBL("Éder", "eder", font("hand", 56), PAL["ink"], PAL["paper"], padx=16, pady=6).draw(cv, fr, 780, 820, pop_in(t, w(10, "Éder")))

def s10e(cv, fr, t):
    pitch(cv, fr, "p10e")
    tm = w(10, "marque", 2); tp = w(10, "Portugal")
    draw_goal(cv, fr, 760, 1300, 420, 240, prog(t, tm, .5), 1, t)
    kick = math.sin(prog(t, tm-.35, .3)*math.pi)
    EDER.draw(cv, fr, 280, 1600, 1.0, age=1, kit="portugal", mood="cheer" if t > tm else "determined", legs=(0, 45*kick), arms=(160, 160) if t > tp else (20, 20), t=t)
    if t < tm + .1:
        u = prog(t, tm-.25, .35); p = bezier((350, 1570), (560, 1350), (740, 1200), u)
        draw_ball(cv, fr, p[0], p[1], .55, t*800)
    kw(cv, fr, K10e, t, tm, tp-.05, CX, 520, -4)
    show(cv, fr, T10c, t, tm+.2, tp-.05, CX, 680, 2)
    if t > tp:
        rays(cv, (CX, 900), t, prog(t, tp, .4), 16, 1300, (250, 220, 120)); confetti(cv, fr, "c10", t-tp, 80, 4)
        SILVER_CUP.draw(cv, fr, CX, 950 - 60*ease_out_back(prog(t, tp, .6)), 1.3*pop_in(t, tp))
        show_stamp(cv, fr, K10f, t, tp+.2, CX, 520, -5)

def s10(cv, fr, t, T):
    shots(cv, fr, t, [(0, s10a), (w(10, "Blessé")-.12, s10b), (w(10, "Mais")-.1, s10c), (w(10, "Il", 3)-.1, s10d), (w(10, "Éder", 2)-.1, s10e)])
    glitch(cv, fr, t, w(10, "Blessé"), .35, 14); impact(cv, t, w(10, "marque", 2), 18); flashes(cv, t, w(10, "marque", 2), .15, .7)
    impact(cv, t, w(10, "Portugal"), 14); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 11 — l'argent
def s11(cv, fr, t, T):
    stage_fill(cv, fr, (236, 208, 150), "s11")
    SUN.draw(cv, fr, 820, 480, 1, 0); DUNE.draw(cv, fr, 300, 1700, 1); DUNE.draw(cv, fr, 900, 1760, .9)
    tn = w(11, "Nassr"); su = prog(t, tn, .45)
    if 0 < su < 1:
        L = CR.render_layer(fr, 1.0, age=1, kit="real" if su < .25 else "alnassr", mood="happy")
        blit_sxy(cv, L, 330, 1560, max(.04, abs(math.cos(su*math.pi*2))), 1)
    else:
        CR.draw(cv, fr, 330, 1560, 1.0, age=1, kit="alnassr" if su >= 1 else "real", mood="happy", t=t, arms=(20, 20))
    kw(cv, fr, K11a, t, tn, None, CX, 360, -3)
    bill_rain(cv, fr, t, w(11, "plus"), 1.4, 16)
    td = w(11, "deux")
    if t > td:
        LBL(f"{counter(0, 200000000, prog(t, td, 1.0))} €", "m11", font("title", 96), GOLD, None, stroke=6, stroke_fill=PAL["ink"]).draw(cv, fr, CX, 580, pop_in(t, td), -2)
        LBL("par an", "m11b", font("title", 64), PAL["ink"], None).draw(cv, fr, CX, 680, pop_in(t, td+.3), 2)
    show_stamp(cv, fr, K11b, t, w(11, "contrat"), 720, 950, -8)
    show(cv, fr, T11a, t, w(11, "gros"), None, 720, 1100, 2)
    show(cv, fr, T11b, t, w(11, "selon"), None, 720, 1210, -2)
    camera_flashes(cv, fr, "cf11", t - w(11, "contrat"), 1.3, 10)
    impact(cv, t, w(11, "contrat"), 16); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 12 — 6 Coupes du monde, 1000 buts, appel à s'abonner
def s12a(cv, fr, t):
    stage_fill(cv, fr, (30, 120, 112), "s12a"); d = ImageDraw.Draw(cv)
    kw(cv, fr, K12a, t, w(12, "quarante"), None, CX, 380, -3)
    ts = w(12, "six")
    for i in range(6):
        a = pop_in(t, w(12, "premier") + i*.15)
        if a <= 0: continue
        x = 140 + i*160
        WC_TROPHY.draw(cv, fr, x, 700, .32*a, 3*math.sin(t*3+i)); YEARS[i].draw(cv, fr, x, 850, a)
        if t > ts + i*.08: pencil_check(d, x, 930, 1.2, (250, 250, 246))
    kw(cv, fr, K12b, t, ts, None, CX, 1080, 3)
    CR.draw(cv, fr, CX, 1640, .8, age=1, kit="portugal", mood="happy", arms=(38, 38), legs=(14, 14), t=t)

def s12b(cv, fr, t):
    stage_fill(cv, fr, (240, 206, 90), "s12b"); d = ImageDraw.Draw(cv)
    ta = w(12, "approche"); tm = w(12, "mille")
    v = int(round(lerp(900, 979, ease_out_cubic(prog(t, ta, 1.5)))))
    LBL(str(v), "g979", font("title", 260), PAL["ink"], None).draw(cv, fr, CX, 640, pop_in(t, ta), -3)
    LBL("buts", "buts12", font("title", 90), (196, 18, 48), None).draw(cv, fr, CX, 820, pop_in(t, ta+.1), 2)
    BAR_BG.draw(cv, fr, CX, 1100, 1)
    fill = (v - 0)/1000
    d.rectangle([CX-390, 1070, CX-390 + 780*fill, 1130], fill=(196, 18, 48))
    if t > tm:
        rays(cv, (CX+390, 1100), t, prog(t, tm, .3), 12, 500, (255, 240, 170))
        kw(cv, fr, K12c, t, tm, None, 800, 1270, -5)
    LBL("1000", "l1000", font("title", 50), PAL["ink"], None).draw(cv, fr, CX+390, 1180, 1)

def s12c(cv, fr, t):
    stage_fill(cv, fr, (246, 238, 220), "s12c"); d = ImageDraw.Draw(cv)
    tp = w(12, "penses")
    BTN_OUI.draw(cv, fr, 330, 560, pop_in(t, tp), -4); BTN_NON.draw(cv, fr, 750, 560, pop_in(t, tp+.15), 4)
    tc = w(12, "commentaire")
    if t > tc:
        arrow(d, (620, 900), (960, 1120), prog(t, tc, .3), PAL["ink"], 10, 12, 36, .2)
        LBL("en commentaire", "encom", font("hand", 60), PAL["ink"], PAL["paper"], padx=18, pady=6).draw(cv, fr, 480, 880, pop_in(t, tc), -3)
    tb = w(12, "abonne-toi")
    if t > tb:
        press = 1 - .12*math.sin(prog(t, tb+.5, .25)*math.pi)
        BTN_SUB.draw(cv, fr, CX, 1080, pop_in(t, tb)*press, -2)
    tl = w(12, "prochaine")
    kw(cv, fr, K12d, t, tl, None, CX, 1230, 3)
    if t > tl:
        CR.draw(cv, fr, CX, 1770, .62, age=1, kit="portugal", mood="cheer", arms=(38, 38), legs=(14, 14), t=t)
        confetti(cv, fr, "c12", t-tl, 70, 5)

def s12(cv, fr, t, T):
    shots(cv, fr, t, [(0, s12a), (w(12, "Il", 2)-.1, s12b), (w(12, "Tu")-.1, s12c)])
    impact(cv, t, w(12, "six"), 12); impact(cv, t, w(12, "mille"), 14); drift(cv, t, T)

# ------------------------------------------------------------------ scènes + bruitages
def SC(name, n, fn, sfx, trans=None, trans_dur=.3, pad_out=.3):
    return Scene(name, TEXTS[n-1], fn, sfx, pad_in=PAD, pad_out=pad_out, trans=trans, trans_dur=trans_dur)
W_ = w
SCENES = [
    SC("devinette", 1, s1, [(.05, "boom", .7), (W_(1, "président"), "stamp", .8), (W_(1, "président")+.05, "pop"), (W_(1, "l'opère"), "monitor", .8, .9),
                            (W_(1, "l'opère"), "stamp", .8), (W_(1, "deux"), "cash", .7), (W_(1, "Tu")-.6, "riser", .9), (W_(1, "Tu"), "glitch", .8, .45)]),
    SC("revelation", 2, s2, [(.0, "boom"), (.05, "whoosh_up"), (W_(2, "Ronaldo"), "stamp"), (W_(2, "Ronaldo"), "crowd_long", .9), (W_(2, "Né")-.1, "whoosh", .6),
                             (W_(2, "mille"), "pop"), (W_(2, "l'île"), "pop2"), (W_(2, "famille"), "pop"), (W_(2, "Son")-.1, "whoosh", .6),
                             (W_(2, "Son"), "pop"), (W_(2, "Ronaldo", 2), "pop2"), (W_(2, "Ronald", 3), "stamp", .7), (W_(2, "Ronald", 3), "sparkle", .6), (W_(2, "acteur"), "pop"),
                             (W_(2, "président")-.1, "swish"), (W_(2, "président"), "flash", .8)], trans="punch", trans_dur=.35),
    SC("lisbonne", 3, s3, [(W_(3, "douze"), "stamp", .7), (W_(3, "seul"), "pop2"), (W_(3, "Lisbonne"), "pop"), (W_(3, "Sporting")-.2, "whoosh", .5),
                           (W_(3, "On")-.1, "whoosh", .5), (W_(3, "moque"), "laugh", .9), (W_(3, "moque")+.3, "pop"), (W_(3, "accent"), "stamp", .6),
                           (W_(3, "Il", 2)-.1, "whoosh", .4), (W_(3, "mais")-.1, "whoosh", .6), (W_(3, "lâche")-.05, "stamp"), (W_(3, "lâche"), "boom", .6)],
       trans="whip"),
    SC("coeur", 4, s4, [(W_(4, "quinze"), "stamp", .6), (W_(4, "massue")-.35, "whoosh", .6), (W_(4, "massue"), "boom"), (W_(4, "massue"), "glitch", .6, .35),
                        (W_(4, "cœur"), "monitor", .9, 1.0), (W_(4, "cœur")+.9, "heart", .9), (W_(4, "vite"), "pop2"), (W_(4, "l'opérer"), "glitch", .7, .4),
                        (W_(4, "Laser")-.1, "laser", .9), (W_(4, "matin"), "tick", 1), (W_(4, "fin"), "whoosh_up", .6), (W_(4, "sorti"), "ding"),
                        (W_(4, "rejouer")-.1, "kick"), (W_(4, "rejouer"), "whoosh", .7)], trans="tear_h", trans_dur=.6),
    SC("united", 5, s5, [(.05, "stamp"), (.05, "boom", .7), (W_(5, "Match")-.08, "whoosh", .5), (W_(5, "Manchester"), "pop2"), (W_(5, "dix-huit"), "pop"),
                         (W_(5, "ridiculise"), "whoosh", .6), (W_(5, "ridiculise")+.3, "thud", .6), (W_(5, "ridiculise")+.6, "thud", .6),
                         (W_(5, "défense"), "stamp"), (W_(5, "défense"), "crowd", .6), (W_(5, "Dans")-.1, "whoosh", .5),
                         (W_(5, "disent"), "pop"), (W_(5, "disent")+.15, "pop"), (W_(5, "disent")+.3, "pop"), (W_(5, "Ferguson"), "pop2"),
                         (W_(5, "signer")-.05, "stamp")], trans="whip"),
    SC("numero7", 6, s6, [(.05, "swish"), (W_(6, "vingt-huit"), "pop2"), (W_(6, "Ferguson"), "pop"), (W_(6, "donne"), "scribble"),
                          (W_(6, "sept")-.2, "swish"), (W_(6, "sept"), "sparkle"), (W_(6, "sept"), "boom", .6), (W_(6, "légendes"), "pop")],
       trans="punch", trans_dur=.35),
    SC("pause", 7, s7, [(0, "scratch", 1.0, .9), (.3, "pop"), (W_(7, "Quel"), "stamp", .6)] + [(W_(7, "prochain")+i*.14, "notif", .7) for i in range(4)] +
                       [(W_(7, "Écris"), "notif"), (W_(7, "Écris")+.2, "scribble", .5), (W_(7, "commentaire"), "pop2"), (W_(7, "Allez"), "whoosh"),
                        (W_(7, "Allez"), "boom", .5)], trans="polaroid", pad_out=.35),
    SC("pere", 8, s8, [(W_(8, "deux"), "pop"), (W_(8, "père")-.1, "paper"), (W_(8, "l'alcool"), "clink"), (W_(8, "refuse"), "scribble"), (W_(8, "refuse")+.1, "stamp", .6)],
       trans="whip", pad_out=.4),
    SC("real", 9, s9, [(0, "boom", .8), (.05, "stamp", .7), (W_(9, "Real"), "whoosh", .6), (W_(9, "quatre-vingt-quatorze"), "cash"), (W_(9, "Record"), "stamp"),
                       (W_(9, "Record"), "flash"), (W_(9, "Quatre-vingt", 2)-.1, "whoosh", .6), (W_(9, "Quatre-vingt", 2), "crowd_long", 1.0),
                       (W_(9, "présentation"), "flash", .7), (W_(9, "Là-bas")-.1, "whoosh", .6)] + [(W_(9, "plante")+k*.12, "tick") for k in range(10)] +
                      [(W_(9, "Ligues")+i*.12, "pop") for i in range(4)] + [(W_(9, "Ligues")+.3, "sparkle")], trans="punch", trans_dur=.35),
    SC("euro", 10, s10, [(.05, "whistle", .6), (W_(10, "finale"), "stamp"), (W_(10, "Blessé")-.1, "whoosh", .5), (W_(10, "Blessé"), "glitch", .7, .4),
                         (W_(10, "Blessé")+.2, "groan", .7), (W_(10, "Mais")-.1, "whoosh", .5), (W_(10, "coache"), "whistle", .5), (W_(10, "coache"), "pop2"),
                         (W_(10, "Il", 3)-.1, "whoosh", .5), (W_(10, "dit"), "pop"), (W_(10, "Éder", 2)-.1, "whoosh", .5), (W_(10, "marque", 2)-.35, "kick"),
                         (W_(10, "marque", 2), "crowd_long", 1.0), (W_(10, "marque", 2), "boom", .6), (W_(10, "Portugal"), "sparkle"), (W_(10, "Portugal")+.2, "stamp")],
       trans="tear_d", trans_dur=.6),
    SC("argent", 11, s11, [(W_(11, "Nassr")-.1, "whoosh", .6), (W_(11, "Nassr"), "pop2"), (W_(11, "plus"), "cash"), (W_(11, "deux"), "tick"),
                           (W_(11, "contrat"), "stamp"), (W_(11, "contrat"), "flash", .8), (W_(11, "selon"), "pop")], trans="whip"),
    SC("fin", 12, s12, [(W_(12, "quarante"), "stamp", .6)] + [(W_(12, "premier")+i*.15, "pop") for i in range(6)] + [(W_(12, "six"), "ding"),
                        (W_(12, "Il", 2)-.1, "whoosh", .6)] + [(W_(12, "approche")+k*.15, "tick") for k in range(8)] +
                       [(W_(12, "mille")-.5, "riser", .8), (W_(12, "mille"), "boom", .7), (W_(12, "Tu")-.1, "whoosh", .6), (W_(12, "penses"), "pop"),
                        (W_(12, "penses")+.15, "pop"), (W_(12, "commentaire"), "notif"), (W_(12, "abonne-toi"), "pop2"), (W_(12, "abonne-toi")+.5, "notif"),
                        (W_(12, "prochaine"), "crowd_long", .8), (W_(12, "prochaine"), "sparkle")], trans="tear_v", trans_dur=.6, pad_out=1.3),
]
SCENES[6].trans_dur = 99      # la photo figée reste épinglée pendant toute la pause
SCENES[6].post = s7_post

# ------------------------------------------------------------------ couverture
def cover(path):
    cv = background(0, TITLE); stage_fill(cv, 0, (196, 18, 48), "cov"); d = ImageDraw.Draw(cv)
    rays(cv, (CX, 1050), 0.2, 1.0, 16, 1500, (236, 190, 90))
    Label("OPÉRÉ DU CŒUR", "cv1", font("title", 128), PAL["cream"], PAL["ink"], maxw=1000, padx=36, pady=10, rough=5).draw(cv, 0, CX, 300, 1, -3)
    Label("À 15 ANS…", "cv2", font("title", 128), PAL["ink"], PAL["mustard"], maxw=1000, padx=36, pady=10, rough=5).draw(cv, 0, CX, 480, 1, 2)
    HEART.draw(cv, 0, 830, 760, 1.0, 10)
    CR.draw(cv, 0, 470, 1560, 1.2, age=1, kit="portugal", arms=(38, 38), legs=(14, 14), mood="cheer", t=1)
    Label("SIUUU", "cv4", font("title", 110), PAL["ink"], PAL["mustard"], padx=24, pady=6, rough=3).draw(cv, 0, 830, 1330, 1, 8)
    Label("L'HISTOIRE FOLLE DE CR7", "cv3", font("title", 70), PAL["cream"], PAL["ink"], padx=30, pady=12).draw(cv, 0, CX, 1690, 1, 1)
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
        p = os.path.join(out, f"r_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", "ronaldo")
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/ronaldo_stills"), only=only)); sys.exit()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25))
