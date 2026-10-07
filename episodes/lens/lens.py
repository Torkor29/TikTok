"""Épisode « Légendes du foot » : l'histoire du RC Lens, format court (~1 min), accroche « vrai supporter » + question piège.
Accroche : « Lensois ? T'es sûr d'être un vrai supporter ? » sur un son de hook (scratch + impact, 1,2 s) avant la voix.
Vers 9 s : QUESTION PIÈGE (A-D) avec chrono de 3 s… et on ne donne PAS la réponse (« ta réponse en commentaire »).
Puis : 1906 jeunes mineurs + étudiants ; Bollaert construit par 180 mineurs, plus de places que d'habitants ; Les Corons ;
1998 champion à la dernière journée ; Wembley (1er club français à y gagner) ; la chute ; 2020 retour, 2023 2e à 1 point du PSG,
Arsenal battu à Bollaert ; mai 2026 1re Coupe de France ; fin : « t'es un vrai Lensois ? ta réponse en commentaire ».

  python3 episodes/lens/lens.py output/lens --stills [3,4]
  python3 episodes/lens/lens.py output/lens --cover
  python3 episodes/lens/lens.py output/lens
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "liverpool"))
from story import *
import quiz
from quiz import like_button, sub_button
from liverpool import score2, trophy_lift, shaft, stadium
import engine, foot

TITLE = "~/légendes $ ./rc_lens"
SLUG = "lens_legende"
VOICE = [os.path.join(HERE, "voix", f"scene_{i}.mp3") for i in range(1, 12)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
ALIGN = os.path.join(HERE, "alignement.json")
PADS = [.85] + [.12]*10          # scène 1 : le son de hook passe seul avant la voix
WS, TEXTS = load_words(ALIGN)
def w(i, word, n=1, end=False):
    return PADS[i-1] + WS[i-1](word, n, end)

SANG = (196, 22, 36); SANG_D = (120, 14, 24); SANG_DD = (58, 8, 14); OR = (250, 196, 30); OR_D = (190, 136, 16)
NOIR = (30, 28, 28); BLANC = (250, 250, 246); GRIS = (120, 120, 126); NUIT = (20, 18, 30); CHARBON = (40, 38, 44)
BRIQUE = (176, 84, 56); BRIQUE_D = (120, 54, 36)
INK = PAL["ink"]

FAN = Player("lensfan", hair=(60, 44, 34), skin=(232, 190, 156))
LENSP = Player("lensp", hair=(30, 24, 20), skin=(150, 104, 76))
LENSP2 = Player("lensp2", hair=(110, 80, 50), skin=(230, 186, 150))
MIN1 = Player("mineur1", hair=(50, 36, 28), skin=(226, 182, 146))
MIN2 = Player("mineur2", hair=(26, 22, 20), skin=(214, 168, 130))
ETU = Player("etudiant", hair=(120, 86, 54), skin=(234, 194, 160))
ARS = Player("arsp", hair=(24, 20, 18), skin=(120, 82, 60))
HEAD_DY = foot.NECK_Y - 58      # centre de la tête = pieds + HEAD_DY*s (adulte)

def miner_helmet(cv, x, y_feet, s):
    """Casque de mineur + lampe frontale, posé sur la tête d'un joueur (adulte) dont les pieds sont en (x, y_feet)."""
    hx, hy = x, y_feet + HEAD_DY*s; d = ImageDraw.Draw(cv)
    d.chord([hx - 64*s, hy - 92*s, hx + 64*s, hy + 22*s], 180, 360, fill=(54, 54, 60), outline=NOIR, width=max(2, int(4*s)))
    d.rectangle([hx - 76*s, hy - 38*s, hx + 76*s, hy - 26*s], fill=(54, 54, 60))
    d.ellipse([hx - 18*s, hy - 82*s, hx + 18*s, hy - 46*s], fill=(255, 226, 120), outline=NOIR, width=max(2, int(3*s)))

def stripes_bg(cv, fr, key, c1=SANG, c2=OR, n=9, t=0.0):
    """Fond « sang et or » : grandes bandes diagonales qui glissent."""
    stage_fill(cv, fr, c1, key); d = ImageDraw.Draw(cv); off = (t*60) % 240
    for k in range(-4, n + 4):
        x = k*240 + off
        d.polygon([(x, 0), (x + 120, 0), (x + 120 - 700, 1920), (x - 700, 1920)], fill=c2)

def mine_bg(cv, fr, key, t=0.0):
    """Carreau de mine : ciel gris, terrils, chevalement."""
    stage_fill(cv, fr, (176, 170, 160), key); d = ImageDraw.Draw(cv)
    d.polygon([(-60, 1240), (300, 700), (640, 1240)], fill=(74, 70, 72)); d.polygon([(560, 1240), (930, 640), (1300, 1240)], fill=(60, 58, 62))
    x0 = 700; d.rectangle([x0 - 8, 520, x0 + 8, 1240], fill=CHARBON); d.rectangle([x0 + 172, 520, x0 + 188, 1240], fill=CHARBON)
    for k in range(6):
        y = 560 + k*110; d.line([(x0, y), (x0 + 180, y + 110)], fill=CHARBON, width=8); d.line([(x0 + 180, y), (x0, y + 110)], fill=CHARBON, width=8)
    rot = t*2.2
    for cx in (x0 + 40, x0 + 140):
        d.ellipse([cx - 70, 400, cx + 70, 540], outline=CHARBON, width=12)
        for k in range(4):
            a = rot + k*math.pi/4; d.line([(cx - 64*math.cos(a), 470 - 64*math.sin(a)), (cx + 64*math.cos(a), 470 + 64*math.sin(a))], fill=CHARBON, width=6)
    d.rectangle([0, 1240, W, H], fill=(96, 86, 74))

def music_notes(cv, t, n=10, area=(80, 600, 1000, 1150), col=OR, seed=4):
    d = ImageDraw.Draw(cv); rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(area[0], area[2]); ph = rnd.uniform(0, 1); s0 = 1.6
        u = (t*.45 + ph) % 1.0; x = x0 + 30*math.sin(u*6 + i); y = area[3] - u*(area[3] - area[1]); s = s0*rnd.uniform(.8, 1.3)
        d.ellipse([x - 20*s, y - 14*s, x + 20*s, y + 14*s], fill=col, outline=NOIR, width=3)
        d.line([(x + 17*s, y), (x + 17*s, y - 80*s)], fill=NOIR, width=int(7*s)); d.line([(x + 17*s, y - 80*s), (x + 46*s, y - 58*s)], fill=NOIR, width=int(7*s))

def wembley(cv, x, y, s=1.0):
    """Les deux tours blanches de l'ancien Wembley."""
    d = ImageDraw.Draw(cv)
    d.rectangle([x - 420*s, y - 120*s, x + 420*s, y + 60*s], fill=(226, 224, 216), outline=NOIR, width=5)
    for k in range(12): d.rectangle([x - 400*s + k*68*s, y - 80*s, x - 370*s + k*68*s, y + 20*s], fill=(150, 148, 144))
    for sx in (-1, 1):
        tx = x + sx*210*s
        d.rectangle([tx - 70*s, y - 420*s, tx + 70*s, y - 120*s], fill=(244, 242, 236), outline=NOIR, width=5)
        for k in range(3): d.rectangle([tx - 40*s, y - 390*s + k*90*s, tx + 40*s, y - 330*s + k*90*s], fill=(150, 160, 176))
        d.chord([tx - 74*s, y - 520*s, tx + 74*s, y - 340*s], 180, 360, fill=(244, 242, 236), outline=NOIR, width=5)
        d.line([(tx, y - 520*s), (tx, y - 610*s)], fill=NOIR, width=5)
        d.polygon([(tx, y - 610*s), (tx + 60*s, y - 590*s), (tx, y - 570*s)], fill=SANG)

def arena_icon(cv, x, y, s=1.0, t=0.0):
    """Stade vu du dessus (tribunes + pelouse) ; les points de la foule clignotent."""
    d = ImageDraw.Draw(cv)
    d.ellipse([x - 230*s, y - 170*s, x + 230*s, y + 170*s], fill=SANG, outline=NOIR, width=6)
    d.ellipse([x - 196*s, y - 140*s, x + 196*s, y + 140*s], fill=OR)
    d.rectangle([x - 130*s, y - 84*s, x + 130*s, y + 84*s], fill=(46, 130, 70), outline=BLANC, width=4)
    d.line([(x, y - 84*s), (x, y + 84*s)], fill=BLANC, width=3); d.ellipse([x - 26*s, y - 26*s, x + 26*s, y + 26*s], outline=BLANC, width=3)
    rnd = random.Random(7)
    for k in range(70):
        a = rnd.uniform(0, 2*math.pi); r = rnd.uniform(.88, 1.0)
        px, py = x + 214*s*r*math.cos(a), y + 156*s*r*math.sin(a)
        if math.sin(t*6 + k) > -.3: d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(SANG_DD if k % 2 else BLANC))

def corons(cv, x, y, s=1.0, rows=3, cols=4):
    """Maisons de corons (briques) en rangées."""
    d = ImageDraw.Draw(cv)
    for r in range(rows):
        for c in range(cols):
            hx = x + (c - (cols - 1)/2)*110*s + (28*s if r % 2 else 0); hy = y + r*120*s
            d.rectangle([hx - 50*s, hy - 40*s, hx + 50*s, hy + 40*s], fill=BRIQUE, outline=BRIQUE_D, width=3)
            d.polygon([(hx - 58*s, hy - 40*s), (hx, hy - 86*s), (hx + 58*s, hy - 40*s)], fill=(70, 66, 70))
            d.rectangle([hx - 12*s, hy, hx + 12*s, hy + 40*s], fill=(60, 44, 36)); d.rectangle([hx + 20*s, hy - 22*s, hx + 40*s, hy - 4*s], fill=(250, 220, 140))

def cliff(cv, t):
    """Bord de falaise : roche à gauche, gouffre noir à droite."""
    d = ImageDraw.Draw(cv); stage_fill(cv, 0, (70, 72, 84), "lcliffsky")
    d.rectangle([0, 1260, W, H], fill=(12, 12, 16))
    d.polygon([(0, 1180), (560, 1180), (600, 1240), (640, 1920), (0, 1920)], fill=(92, 84, 80))
    for k in range(6): d.line([(40 + k*90, 1260 + 30*(k % 3)), (120 + k*90, 1400 + 50*(k % 2))], fill=(70, 64, 60), width=6)

def rain(cv, t, n=60, col=(170, 176, 190)):
    d = ImageDraw.Draw(cv); rnd = random.Random(3)
    for i in range(n):
        x = rnd.uniform(0, W); y = (rnd.uniform(0, H) + t*1400) % H
        d.line([(x, y), (x - 10, y + 44)], fill=col, width=3)

def ranking(cv, fr, y, rows, hl, a=1.0):
    """Mini classement : rows = [(rang, club, points)], hl = index de la ligne surlignée."""
    for k, (rk, club, pts) in enumerate(rows):
        on = k == hl
        lab = LBL(f"{rk}.  {club}   {pts} pts", f"lrank{k}{on}", font("title", 70), (NOIR if on else BLANC), (OR if on else CHARBON), padx=40, pady=10, rough=2)
        lab.draw(cv, fr, CX, y + k*150, a*(1.06 if on else 1), (-1.5 if on else 1))

# ------------------------------------------------------------------ question piège (A-D) : réponses avec pastilles de couleurs
QA = [("Sang et or", SANG, OR), ("Bleu et blanc", (40, 90, 190), BLANC), ("Noir et vert", NOIR, (0, 140, 70)), ("Rouge et noir", SANG, NOIR)]
QX, QY0, QDY = quiz.AX, quiz.ANS_Y0, quiz.ANS_DY
def _qbox(k):
    txt, c1, c2 = QA[k]; letter = "ABCD"[k]; f = font("title", 58)
    def dec(d, a):
        ax, ay = a
        d.ellipse([ax - 418, ay - 42, ax - 334, ay + 42], fill=SANG_D)
        d.text((ax - 376, ay + 2), letter, font=font("title", 60), fill=BLANC, anchor="mm")
        d.text((ax - 306, ay + 2), txt, font=f, fill=INK, anchor="lm")
        x0, y0 = ax + 270, ay - 36
        d.polygon([(x0, y0), (x0 + 120, y0), (x0, y0 + 72)], fill=c1); d.polygon([(x0 + 120, y0), (x0 + 120, y0 + 72), (x0, y0 + 72)], fill=c2)
        d.rectangle([x0, y0, x0 + 120, y0 + 72], outline=INK, width=4)
    return Paper(rect_pts(860, 108), BLANC, f"lqa{k}", rough=1.8).add(dec)
QBOX = [_qbox(k) for k in range(4)]
QHEAD = Label("QUESTION PIÈGE", "lqhead", font("title", 74), BLANC, SANG, padx=34, pady=8, rough=3)
QCARD = Label("En 1906, le tout 1er maillot de Lens était de quelles couleurs ?", "lqcard", font("title", 62), INK, PAL["cream"], maxw=880, padx=34, pady=16, rough=3)
MYST = jersey_front("mystere", "lmyst").add(lambda d, a: d.text((a[0], a[1] + 20), "?", font=font("title", 300), fill=BLANC, anchor="mm", stroke_width=10, stroke_fill=INK))
QM = Label("?", "lqm", font("title", 300), OR, None, stroke=10, stroke_fill=INK)
SECRET = STAMP("TOP SECRET", "lsecret", SANG, 130)
COMM = STAMP("RÉPONSE EN COMMENTAIRE", "lcomm", SANG, 76)

def board(cv, fr, t, t_in=None, chrono_ts=None):
    """La carte question : en-tête, question, réponses A-D (t_in : début des apparitions, None = déjà là)."""
    stage_fill(cv, fr, SANG_DD, "lqbg"); rays(cv, (CX, 860), t, .35, 14, 1500, (110, 30, 40), .1, .08)
    a = (lambda d0: pop_in(t, t_in + d0, .3)) if t_in is not None else (lambda d0: 1.0)
    QHEAD.draw(cv, fr, CX, 248, a(0), -2)
    s = slam(t, t_in + .08, .2) if t_in is not None else 1.0
    if s > 0: QCARD.draw(cv, fr, CX, quiz.CARD_Y, s, -1.2)
    for k in range(4):
        sk = a(.45 + k*.12)
        if sk > .01: QBOX[k].draw(cv, fr, QX + 3*math.sin(t*2.5 + k), QY0 + k*QDY, sk, .6*math.sin(t*3 + k))
    if chrono_ts is not None: quiz.chrono(cv, fr, t, chrono_ts)

# ------------------------------------------------------------------ labels
LENSOIS_Y = 400
K1a = STAMP("VRAI SUPPORTER ?", "lk1a", SANG, 104); K1b = KW("TU CONNAIS L'HISTOIRE", "lk1b", INK, size=80); K1c = KW("DE TON CLUB ?", "lk1c", OR, NOIR, 100)
BOOK = Paper(rect_pts(520, 660), SANG_D, "lbook", rough=2, hatch=True).add(lambda d, a: [
    d.rectangle([a[0] - 230, a[1] - 300, a[0] + 230, a[1] + 300], outline=OR, width=8),
    d.text((a[0], a[1] - 150), "RC LENS", font=font("title", 110), fill=OR, anchor="mm"),
    d.text((a[0], a[1] - 30), "L'HISTOIRE", font=font("title", 64), fill=BLANC, anchor="mm"),
    d.text((a[0], a[1] + 110), "1906 - 2026", font=font("title", 70), fill=OR, anchor="mm")])
K2a = KW("1906", "lk2a", INK, size=170); T2a = TAG("des jeunes mineurs…", "lt2a", PAL["paper"], size=58); T2b = TAG("…et des étudiants", "lt2b", PAL["paper"], size=58)
K2b = STAMP("RACING CLUB DE LENS", "lk2b", SANG, 92)
K5a = KW("BOLLAERT", "lk5a", INK, size=150); T5a = TAG("construit par 180 mineurs", "lt5a", OR, size=60)
K5b = STAMP("PLUS DE PLACES QUE D'HABITANTS !", "lk5b", SANG, 80)
K6a = KW("LES CORONS", "lk6a", OR, NOIR, 130); T6a = TAG("chantés à chaque mi-temps", "lt6a", PAL["paper"], size=58)
K6b = KW("1998", "lk6b", INK, size=170); K6c = STAMP("CHAMPION DE FRANCE", "lk6c", SANG, 96); T6b = TAG("à la dernière journée", "lt6b", OR, size=60)
K7a = KW("WEMBLEY", "lk7a", INK, size=150); T7a = TAG("6 mois plus tard · novembre 1998", "lt7a", PAL["paper"], size=58)
K7b = STAMP("1er CLUB FRANÇAIS À Y GAGNER", "lk7b", SANG, 70)
K8a = KW("LA CHUTE", "lk8a", BLANC, NOIR, 130); K8b = KW("CAISSES VIDES", "lk8b", SANG, size=110); K8c = KW("AU BORD DU GOUFFRE", "lk8c", BLANC, NOIR, 84)
K9a = KW("2020", "lk9a", INK, size=170); T9a = TAG("retour en Ligue 1", "lt9a", OR, size=62)
K9b = KW("2023", "lk9b", INK, size=170); K9c = STAMP("À 1 POINT DU TITRE !", "lk9c", SANG, 90)
T9c = TAG("Ligue des champions · oct. 2023", "lt9c", OR, size=56)
K10a = KW("MAI 2026", "lk10a", INK, size=150); K10b = STAMP("1re COUPE DE FRANCE !", "lk10b", SANG, 92); T10a = TAG("3-1 contre Nice", "lt10a", OR, size=62)
K11a = KW("T'ES UN VRAI LENSOIS ?", "lk11a", BLANC, NOIR, 80); K11b = KW("RÉPONDS EN COMMENTAIRE !", "lk11b", OR, NOIR, 70)
MINI = Label("1906 : le 1er maillot ?", "lmini", font("title", 64), INK, PAL["cream"], padx=30, pady=10, rough=3)

# ------------------------------------------------------------------ SCÈNE 1 — LENSOIS ? T'es sûr d'être un vrai supporter ?
def s1a(cv, fr, t):
    stripes_bg(cv, fr, "ls1a", SANG_D, SANG, t=t)
    beam(cv, (CX, 0), [(CX - 380, 1920), (CX + 380, 1920)], .22)
    ransom_line(cv, "LENSOIS ?", LENSOIS_Y, 190, seed=17, fr=fr, scale=slam(t, -.12, .22))
    tv = w(1, "vrai") - .05
    FAN.draw(cv, fr, CX, 1790, 1.18, age=1, kit="lens", mood="surprised" if t > tv else "normal", arms=(30, 30), t=t, look=(0, -1))
    if t > tv:
        rnd = random.Random(2); d = ImageDraw.Draw(cv)
        for k in range(3):        # gouttes de sueur
            u = ((t - tv)*1.4 + k/3) % 1.0; x = CX + (-100, 115, 80)[k]; y = 1790 + HEAD_DY*1.18 - 40 + 120*u
            d.ellipse([x - 9, y - 14, x + 9, y + 10], fill=(150, 200, 240))
    show_stamp(cv, fr, K1a, t, tv, CX, 640, -5)

def s1b(cv, fr, t):
    stage_fill(cv, fr, SANG_DD, "ls1b"); rays(cv, (CX, 1050), t, .9, 16, 1500, (150, 40, 50))
    t0 = w(1, "Tu") - .1
    kw(cv, fr, K1b, t, t0 + .05, None, CX, 330, -2)
    kw(cv, fr, K1c, t, w(1, "club") - .1, None, CX, 470, 3)
    BOOK.draw(cv, fr, CX, 1060, .95*slam(t, w(1, "l'histoire") - .1, .25), -4 + 2*math.sin(t*3))
    for k in range(3):
        a = pop_in(t, w(1, "l'histoire") + .1*k, .3)
        if a > .01: QM.draw(cv, fr, (210, 880, 860)[k], (900, 760, 1460)[k], .55*a, (-12, 10, 6)[k] + 6*math.sin(t*4 + k))

def s1(cv, fr, t, T):
    shots(cv, fr, t, [(0, s1a), (w(1, "Tu") - .1, s1b)], d=.24)
    impact(cv, t, .45, 22); flashes(cv, t, .45, .12, .55); punch(cv, t, .45, 1.08)        # le « DUN » du son de hook
    impact(cv, t, w(1, "vrai"), 14); impact(cv, t, w(1, "l'histoire"), 12); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 2 — 1906 : jeunes mineurs + étudiants
def s2(cv, fr, t, T):
    mine_bg(cv, fr, "ls2", t)
    tm, te, tf = w(2, "mineurs") - .1, w(2, "étudiants") - .1, w(2, "fondent") - .1
    for k, x in enumerate((210, 420)):
        a = pop_in(t, tm + .08*k, .3)
        if a > .01:
            P = (MIN1, MIN2)[k]; s = 1.0*a
            P.draw(cv, fr, x, 1790, s, age=.75, kit="mine", mood="happy", t=t, kid_hair=True)
            miner_helmet(cv, x, 1790 + 112*s*(1 - .75), s*.97)
    for k, x in enumerate((680, 880)):
        a = pop_in(t, te + .08*k, .3)
        if a > .01: ETU.draw(cv, fr, x, 1790, 1.0*a, age=.85, kit="street", mood="happy", t=t)
    if t > tf: draw_ball(cv, fr, CX, 1760 - 260*abs(math.sin((t - tf)*5)), .7, t*400)
    old_film(cv, fr, t, .9)
    kw(cv, fr, K2a, t, .03, None, CX, 330, -3)
    show(cv, fr, T2a, t, tm, te - .05, CX, 520, -2)
    show(cv, fr, T2b, t, te, None, CX, 520, 2)
    show_stamp(cv, fr, K2b, t, w(2, "Racing") - .05, CX, 700, -4)
    impact(cv, t, w(2, "Racing"), 14); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNES 3 et 4 — QUESTION PIÈGE, sans la réponse
quiz.CHRONO = 3.0
def s3(cv, fr, t, T):
    ts = w(3, "couleurs", end=True) + .15
    board(cv, fr, t, 0.0, ts)
    a = pop_in(t, w(3, "maillot") - .15, .35)
    if a > .01: MYST.draw(cv, fr, CX, 870, .5*a, 3*math.sin(t*3))
    if t > ts + 3.0: QM.draw(cv, fr, CX, 870, slam(t, ts + 3.0, .2)*.9, -6)
    flashes(cv, t, ts + 3.0, .12, .4); drift(cv, t, T, .02)

def s4(cv, fr, t, T):
    board(cv, fr, t + 6)
    QM.draw(cv, fr, 220, 880, .62 + .05*math.sin(t*6), -8 + 6*math.sin(t*3))
    show_stamp(cv, fr, COMM, t, w(4, "réponse") - .1, CX, 740, -4)
    sb = pop_in(t, w(4, "commentaire") - .1, .3)
    if sb > .01:
        speech_bubble(cv, fr, "lbub", "…", 560, 900, sb, (1, 1), 90)
        d = ImageDraw.Draw(cv); arrow(d, (700, 900), (985, 960), prog(t, w(4, "commentaire"), .4), OR, 14, 3, 44, .25)
    show_stamp(cv, fr, SECRET, t, w(4, "non") - .05, QX, 1280, -10)
    impact(cv, t, w(4, "non"), 16)

# ------------------------------------------------------------------ SCÈNE 5 — Bollaert : 180 mineurs, plus de places que d'habitants
def s5a(cv, fr, t):
    stage_fill(cv, fr, (22, 20, 26), "ls5a"); rays(cv, (CX, 1050), t, .4, 14, 1400, (60, 50, 40)); d = ImageDraw.Draw(cv)
    kw(cv, fr, K5a, t, w(5, "Bollaert") - .1, None, CX, 330, -3)
    show(cv, fr, T5a, t, w(5, "cent") - .1, None, CX, 500, 2)
    tc = w(5, "cent") - .05; n = int(180*prog(t, tc, w(5, "mineurs", end=True) - tc))
    for k in range(n):             # 180 casques de mineurs, lampe allumée
        r, c = divmod(k, 12); x = 150 + c*71; y = 680 + r*56
        d.ellipse([x - 22, y - 30, x + 22, y + 6], fill=(70, 60, 30)); d.chord([x - 28, y - 22, x + 28, y + 30], 180, 360, fill=(84, 84, 92))
        d.ellipse([x - 10, y - 18, x + 10, y + 2], fill=(255, 230, 130))
    LBL(f"{n} MINEURS", "lmin180", font("title", 104), NOIR, OR, padx=30, pady=6, rough=2).draw(cv, fr, CX, 1560, pop_in(t, tc, .3), 3)

def s5b(cv, fr, t):
    stripes_bg(cv, fr, "ls5b", SANG_DD, SANG_D, t=t)
    tp, th = w(5, "trente-huit") - .1, w(5, "trente-trois") - .1
    arena_icon(cv, 280, 760, 1.05*pop_in(t, tp - .2, .3), t)
    p = counter(0, 38223, ease_out_cubic(prog(t, tp, .9)))
    LBL(p, "lplc", font("title", 104), NOIR, OR, padx=24, pady=4, rough=2).draw(cv, fr, 280, 1020, pop_in(t, tp, .3), -3)
    LBL("PLACES", "lplc2", font("title", 66), BLANC, None).draw(cv, fr, 280, 1125, pop_in(t, tp, .3), 0)
    if t > th - .2:
        corons(cv, 790, 650, .95*pop_in(t, th - .2, .3))
        hb = counter(0, 32697, ease_out_cubic(prog(t, th, .9)))
        LBL(hb, "lhab", font("title", 104), NOIR, BLANC, padx=24, pady=4, rough=2).draw(cv, fr, 790, 1020, pop_in(t, th, .3), 3)
        LBL("HABITANTS", "lhab2", font("title", 66), BLANC, None).draw(cv, fr, 790, 1125, pop_in(t, th, .3), 0)
    show_stamp(cv, fr, K5b, t, w(5, "habitants") + .1, CX, 1380, -4)
    if t > w(5, "habitants") + .1: confetti(cv, fr, "lc5", t - w(5, "habitants"), 70, 3, [SANG, OR, BLANC])

def s5(cv, fr, t, T):
    shots(cv, fr, t, [(0, s5a), (w(5, "Aujourd'hui") - .1, s5b)], d=.24)
    impact(cv, t, w(5, "mineurs"), 12); impact(cv, t, w(5, "habitants") + .1, 18); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 6 — Les Corons… 1998 champion à la dernière journée
def s6a(cv, fr, t):
    stadium(cv, fr, "ls6stad", t, horizon=1240, sky=NUIT, pal=[SANG, OR, SANG_D, BLANC, OR_D])
    music_notes(cv, t)
    kw(cv, fr, K6a, t, w(6, "Corons") - .15, None, CX, 330, -3)
    show(cv, fr, T6a, t, w(6, "mi-temps") - .05, None, CX, 490, 2)
    for k, x in enumerate((230, 540, 850)):
        LENSP2.draw(cv, fr, x, 1840, .62, age=1, kit="lens", mood="happy", arms=(150 + 10*math.sin(t*5 + k), 150 + 10*math.sin(t*5 + k + 1)), t=t)

def s6b(cv, fr, t):
    stage_fill(cv, fr, SANG_D, "ls6b"); rays(cv, (CX, 1000), t, 1.0, 16, 1500, (230, 170, 60))
    tc = w(6, "champion") - .05
    kw(cv, fr, K6b, t, w(6, "quatre-vingt-dix-huit") - .1, None, CX, 330, -3)
    show_stamp(cv, fr, K6c, t, tc, CX, 520, 4)
    show(cv, fr, T6b, t, w(6, "dernière") - .1, None, CX, 670, -2)
    trophy_lift(cv, fr, LENSP, CX, 1820, .85, "lens", t, CUP)
    confetti(cv, fr, "lc6", t - tc, 90, 3, [SANG, OR, BLANC])

def s6(cv, fr, t, T):
    shots(cv, fr, t, [(0, s6a), (w(6, "Et") - .1, s6b)], d=.24)
    impact(cv, t, w(6, "champion"), 20); flashes(cv, t, w(6, "champion"), .1, .4); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 7 — Wembley : 1er club français à y gagner, contre Arsenal
def s7(cv, fr, t, T):
    stage_fill(cv, fr, NUIT, "ls7"); rays(cv, (CX, 900), t, .5, 14, 1400, (60, 60, 110))
    tc = w(7, "Contre") - .1
    wembley(cv, CX, 1240, .95)
    d = ImageDraw.Draw(cv); d.rectangle([0, 1300, W, H], fill=(46, 112, 64))
    kw(cv, fr, K7a, t, .05, None, CX, 300, -3)
    show(cv, fr, T7a, t, .15, w(7, "premier") - .15, CX, 470, 2)
    show_stamp(cv, fr, K7b, t, w(7, "premier") - .05, CX, 480, 3)
    if t > tc:
        score2(cv, fr, CX, 860, "ARSENAL", "LENS", 0, 1, "25 nov. 1998", .85*pop_in(t, tc, .3))
    LENSP.draw(cv, fr, 290, 1860, .66, age=1, kit="lens", mood="cheer" if t > tc else "happy", arms=(150, 150) if t > tc else (20, 20), t=t)
    ARS.draw(cv, fr, 800, 1860, .66, age=1, kit="arsenal", mood="sad" if t > tc else "normal", t=t, look=(0, 1) if t > tc else (0, 0))
    if t > tc: confetti(cv, fr, "lc7", t - tc, 70, 3, [SANG, OR, BLANC])
    impact(cv, t, w(7, "premier"), 12); impact(cv, t, w(7, "Arsenal"), 18); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 8 — la chute : Ligue 2, caisses vides, au bord du gouffre
def s8a(cv, fr, t):
    tl = w(8, "Ligue") - .1
    stage_fill(cv, fr, CHARBON, "ls8a")
    LENSP.draw(cv, fr, CX, 1740, 1.0, age=1, kit="lens", mood="surprised" if t < tl else "sad", t=t)
    floor_panel(cv, fr, CX, 700, "L1", t, True, 1.6, 1)
    kw(cv, fr, K8a, t, .03, None, CX, 330, -3)
    elevator_drop(cv, t, w(8, "chute"), .6)
    if t > tl:
        shaft(cv, fr, t, 0, "ls8shaft")
        LENSP.draw(cv, fr, CX, 1740, 1.0, age=1, kit="lens", mood="sad", t=t, look=(0, 1))
        floor_panel(cv, fr, CX, 700, "L2", t, True, 1.8, 1)
    kw(cv, fr, K8b, t, w(8, "caisses") - .1, None, CX, 1000, 3)
    if t > w(8, "vides"):
        d = ImageDraw.Draw(cv); u = prog(t, w(8, "vides"), .8)
        d.ellipse([CX - 40 + 320*u, 1180 + 60*u, CX + 40 + 320*u, 1260 + 60*u], fill=OR, outline=NOIR, width=4)   # la dernière pièce roule…

def s8b(cv, fr, t):
    cliff(cv, t)
    wob = math.sin(t*9)
    LENSP.draw(cv, fr, 520, 1180, .72, age=1, kit="lens", mood="surprised", arms=(120 + 40*wob, 120 - 40*wob), legs=(6, -6), lean=10*wob, t=t)
    kw(cv, fr, K8c, t, w(8, "bord") - .1, None, CX, 420, -3)
    rain(cv, t)

def s8(cv, fr, t, T):
    shots(cv, fr, t, [(0, s8a), (w(8, "le", 2) - .1, s8b)], d=.24)
    grayscale(cv, .55)
    impact(cv, t, w(8, "Ligue") + .1, 18); impact(cv, t, w(8, "gouffre"), 14); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 9 — 2020 retour ; 2023 2e à 1 point ; Arsenal battu à Bollaert
def s9a(cv, fr, t):
    t0 = .1; tl = w(9, "Ligue") + .55
    shaft(cv, fr, t, 900 + 2000*prog(t, t0, tl - t0))
    floor_panel(cv, fr, CX, 700, "L2" if t < tl - .3 else "L1", t, False, 1.8, 1)
    LENSP.draw(cv, fr, CX, 1740, 1.0, age=1, kit="lens", mood="cheer" if t > tl - .3 else "determined", arms=(150, 150) if t > tl - .3 else (30, 30), t=t)
    kw(cv, fr, K9a, t, w(9, "deux") - .1, None, CX, 330, -3)
    show(cv, fr, T9a, t, w(9, "Ligue") - .05, None, CX, 500, 2)

def s9b(cv, fr, t):
    stripes_bg(cv, fr, "ls9b", SANG_DD, SANG_D, t=t)
    kw(cv, fr, K9b, t, w(9, "Trois") - .05, None, CX, 330, -3)
    ranking(cv, fr, 640, [(1, "PSG", 85), (2, "LENS", 84)], 1, 1.25*pop_in(t, w(9, "deuxième") - .15, .3))
    show_stamp(cv, fr, K9c, t, w(9, "point") - .05, CX, 1060, -4)
    LENSP2.draw(cv, fr, CX, 1840, .78, age=1, kit="lens", mood="determined" if t < w(9, "point") else "surprised", t=t)

def s9c(cv, fr, t):
    stadium(cv, fr, "ls9stad", t, horizon=1240, sky=NUIT, pal=[SANG, OR, SANG_D, BLANC, OR_D])
    for k in range(8):
        a = k*math.pi/4 + t*.6; draw_star(cv, CX + 300*math.cos(a), 1000 + 120*math.sin(a), 30, 1, t*2, BLANC)
    tb = w(9, "battu") - .1
    show(cv, fr, T9c, t, w(9, "et") - .05, None, CX, 330, -2)
    score2(cv, fr, CX, 640, "LENS", "ARSENAL", 2, 1, "Bollaert", .85*pop_in(t, w(9, "Arsenal") - .1, .3))
    LENSP.draw(cv, fr, 300, 1840, .62, age=1, kit="lens", mood="cheer" if t > tb else "determined", arms=(150, 150) if t > tb else (20, 20), t=t)
    ARS.draw(cv, fr, 800, 1840, .62, age=1, kit="arsenal", mood="sad" if t > tb else "normal", t=t, look=(0, 1) if t > tb else (0, 0))
    if t > tb: camera_flashes(cv, fr, "lf9", t - tb, 1.4, 10); confetti(cv, fr, "lc9", t - tb, 70, 3, [SANG, OR, BLANC])

def s9(cv, fr, t, T):
    shots(cv, fr, t, [(0, s9a), (w(9, "Trois") - .1, s9b), (w(9, "et") - .1, s9c)], d=.24)
    impact(cv, t, w(9, "Ligue") + .55, 14); impact(cv, t, w(9, "point"), 16); impact(cv, t, w(9, "battu"), 20); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 10 — mai 2026 : 1re Coupe de France
def s10(cv, fr, t, T):
    stage_fill(cv, fr, SANG_D, "ls10"); rays(cv, (CX, 1000), t, 1.0, 16, 1500, (240, 190, 70))
    tp = w(10, "première") - .1
    kw(cv, fr, K10a, t, w(10, "mai") - .1, None, CX, 330, -3)
    show_stamp(cv, fr, K10b, t, tp, CX, 520, 4)
    show(cv, fr, T10a, t, w(10, "Coupe") - .05, None, CX, 670, -2)
    trophy_lift(cv, fr, LENSP2, CX, 1820, .85, "lens", t, CUP)
    if t > tp: confetti(cv, fr, "lc10", t - tp, 110, 3, [SANG, OR, BLANC]); camera_flashes(cv, fr, "lf10", t - tp, 1.2, 8)
    impact(cv, t, tp + .05, 20); flashes(cv, t, tp + .05, .1, .45); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 11 — t'es un vrai Lensois ? réponds en commentaire + abonne-toi
def s11(cv, fr, t, T):
    stripes_bg(cv, fr, "ls11", SANG_D, SANG, t=t)
    tr, ta = w(11, "Ta") - .1, w(11, "abonne-toi")
    kw(cv, fr, K11a, t, .05, None, CX, 330, -2)
    a = pop_in(t, .3, .3)
    if a > .01:
        MINI.draw(cv, fr, CX, 520, a, 2)
        d = ImageDraw.Draw(cv)
        for k, (txt, c1, c2) in enumerate(QA):          # les 4 propositions en pastilles, toujours sans la réponse
            x = 210 + k*220; y = 680; s = pop_in(t, .4 + .08*k, .3)
            if s < .02: continue
            d.rounded_rectangle([x - 90*s, y - 60*s, x + 90*s, y + 60*s], int(16*s), fill=BLANC, outline=INK, width=5)
            d.polygon([(x - 70*s, y - 40*s), (x + 70*s, y - 40*s), (x - 70*s, y + 40*s)], fill=c1); d.polygon([(x + 70*s, y - 40*s), (x + 70*s, y + 40*s), (x - 70*s, y + 40*s)], fill=c2)
            d.text((x, y), "ABCD"[k], font=font("title", int(64*s)), fill=BLANC, anchor="mm", stroke_width=5, stroke_fill=INK)
    kw(cv, fr, K11b, t, tr, None, CX, 840, 3)
    like_button(cv, fr, CX, 1080, .75*pop_in(t, w(11, "commentaire") - .1, .3), t, w(11, "commentaire"))     # empilés au centre (x < 940)
    sub_button(cv, fr, CX, 1340, t, ta - .1, ta + .25)
    confetti(cv, fr, "lc11", t - ta, 90, 5, [SANG, OR, BLANC])
    impact(cv, t, w(11, "commentaire"), 10); impact(cv, t, ta, 12); drift(cv, t, T, .04)

# ------------------------------------------------------------------ scènes + bruitages
def SC(name, n, fn, sfx, trans=None, trans_dur=.25, pad_out=.25):
    return Scene(name, TEXTS[n-1], fn, sfx, pad_in=PADS[n-1], pad_out=pad_out, trans=trans, trans_dur=trans_dur)
W_ = w
TS3 = w(3, "couleurs", end=True) + .15
SCENES = [
    SC("hook", 1, s1, [(.0, "hook", 1.3), (W_(1, "Lensois"), "pop", .5), (W_(1, "vrai"), "stamp", .8), (W_(1, "Tu") - .1, "whoosh", .5),
                       (W_(1, "l'histoire") - .05, "boom", .5), (W_(1, "club"), "pop2", .6)]),
    SC("1906", 2, s2, [(.0, "rip", .5), (.03, "stamp", .6), (W_(2, "mineurs") - .1, "dig", .6, .8), (W_(2, "étudiants") - .1, "pop", .5),
                       (W_(2, "Racing"), "stamp", .9), (W_(2, "Racing"), "crowd", .6)], trans="tear_v", trans_dur=.45),
    SC("question", 3, s3, [(.0, "whoosh", .45), (.1, "stamp", .6)] + [(.45 + k*.12, "pop", .45) for k in range(4)] + [(W_(3, "maillot") - .1, "pop2", .6)]
       + [(TS3 + k, "tictac", .75 if k < 2 else 1.0, .45) for k in range(3)] + [(TS3 + 3.0, "boom", .7), (TS3 + 3.0, "gasp", .6)],
       trans="punch", trans_dur=.3, pad_out=TS3 - W_(3, "couleurs", end=True) + 3.25),
    SC("pas_de_reponse", 4, s4, [(W_(4, "réponse") - .1, "stamp", .8), (W_(4, "commentaire"), "notif", .9), (W_(4, "non"), "stamp", 1.0), (W_(4, "non") + .05, "laugh", .5, 1.2)]),
    SC("bollaert", 5, s5, [(.0, "rip", .5), (W_(5, "Bollaert"), "stamp", .6), (W_(5, "cent"), "dig", .5, 1.2), (W_(5, "Aujourd'hui") - .1, "whoosh", .5),
                           (W_(5, "trente-huit"), "coin", .5), (W_(5, "trente-trois"), "coin", .5), (W_(5, "habitants") + .1, "stamp", .9),
                           (W_(5, "habitants") + .1, "crowd", .7)], trans="tear_h", trans_dur=.5),
    SC("corons_1998", 6, s6, [(.0, "crowd_long", .8), (W_(6, "Corons") - .15, "stamp", .6), (W_(6, "Et") - .1, "whoosh", .5), (W_(6, "quatre-vingt-dix-huit"), "stamp", .6),
                              (W_(6, "champion"), "stamp", .9), (W_(6, "champion"), "crowd_long", 1.0), (W_(6, "champion"), "sparkle", .6)], trans="whip"),
    SC("wembley", 7, s7, [(.0, "boom", .5), (W_(7, "Wembley") - .15, "stamp", .6), (W_(7, "premier"), "stamp", .8), (W_(7, "Contre"), "kick", .6),
                          (W_(7, "Arsenal"), "boom", .7), (W_(7, "Arsenal"), "crowd_long", .9)], trans="punch", trans_dur=.3),
    SC("chute", 8, s8, [(.03, "stamp", .5), (W_(8, "chute"), "elevator", .9), (W_(8, "Ligue") + .1, "boom", .7), (W_(8, "caisses"), "stamp", .6),
                        (W_(8, "vides"), "coin", .6), (W_(8, "le", 2) - .1, "whoosh", .5), (W_(8, "gouffre"), "groan", .6)], trans="tear_d", trans_dur=.5),
    SC("renaissance", 9, s9, [(.0, "whoosh_up", .8), (W_(9, "Ligue") + .55, "stamp", .7), (W_(9, "Ligue") + .55, "crowd", .7),
                              (W_(9, "Trois") - .1, "whoosh", .5), (W_(9, "deuxième"), "pop", .6), (W_(9, "point"), "stamp", .9),
                              (W_(9, "et") - .1, "whoosh", .5), (W_(9, "battu"), "boom", .8), (W_(9, "battu"), "crowd_long", 1.0)], trans="whip"),
    SC("coupe", 10, s10, [(.0, "boom", .5), (W_(10, "mai"), "stamp", .6), (W_(10, "première"), "stamp", 1.0), (W_(10, "première"), "crowd_long", 1.0),
                          (W_(10, "première"), "sparkle", .8), (W_(10, "Coupe"), "flash", .5)], trans="punch", trans_dur=.3),
    SC("fin", 11, s11, [(.0, "whoosh", .5), (.05, "stamp", .6), (.3, "pop", .5)] + [(.4 + .08*k, "pop", .4) for k in range(4)]
       + [(W_(11, "Ta") - .1, "pop2", .6), (W_(11, "commentaire"), "pop", .6), (W_(11, "commentaire") + .05, "notif", .8),
          (W_(11, "abonne-toi"), "pop2", .7), (W_(11, "abonne-toi") + .25, "notif", .8), (W_(11, "abonne-toi") + .2, "crowd", .6)],
       trans="whip", pad_out=1.3),
]

# ------------------------------------------------------------------ couverture : « LENSOIS ? T'es sûr d'être un vrai supporter ? »
def cover(path):
    cv = background(0, TITLE); stripes_bg(cv, 0, "lcov", SANG_D, SANG)
    beam(cv, (CX, 0), [(CX - 420, 1920), (CX + 420, 1920)], .2)
    ransom_line(cv, "LENSOIS ?", 400, 200, seed=17, fr=0)
    Label("T'ES SÛR D'ÊTRE UN VRAI SUPPORTER ?", "lcv2", font("title", 66), BLANC, NOIR, maxw=1000, padx=30, pady=10, rough=5).draw(cv, 0, CX, 620, 1, -2)
    MYST.draw(cv, 0, CX, 990, .62, -4)
    Label("1906 : QUELLES COULEURS ?", "lcv3", font("title", 72), INK, OR, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 1330, 1, 2)
    d = ImageDraw.Draw(cv)
    for k, (txt, c1, c2) in enumerate(QA):
        x = 210 + k*220; y = 1520
        d.rounded_rectangle([x - 90, y - 60, x + 90, y + 60], 16, fill=BLANC, outline=INK, width=5)
        d.polygon([(x - 70, y - 40), (x + 70, y - 40), (x - 70, y + 40)], fill=c1); d.polygon([(x + 70, y - 40), (x + 70, y + 40), (x - 70, y + 40)], fill=c2)
        d.text((x, y), "ABCD"[k], font=font("title", 64), fill=BLANC, anchor="mm", stroke_width=5, stroke_fill=INK)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

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
            finish(cv, TITLE); ims.append(cv.resize((300, 533)))
        sheet = Image.new("RGB", (300*len(ims), 575), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            sheet.paste(im, (k*300, 42)); dd.text((k*300+8, 6), f"S{i+1} {fracs[k]*sc.T:.1f}/{sc.T:.1f}", font=font("mono", 24), fill=(230, 230, 230))
        p = os.path.join(out, f"ln_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", "lens")
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/lens_stills"), only=only)); sys.exit()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25, limit=True))
