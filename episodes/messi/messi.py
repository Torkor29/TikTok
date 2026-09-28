"""Épisode « Légendes du foot » #1 : Lionel Messi.
Fil rouge : « trop petit » à 10 ans -> le joueur le plus titré de l'histoire.
9 scènes, voix off ElevenLabs (Léo) dans voix/scene_N.mp3, bruitages ElevenLabs dans assets/sfx/.

Lancer (depuis la racine du repo) :
  python3 episodes/messi/messi.py output/messi --stills        # planches de contrôle
  python3 episodes/messi/messi.py output/messi --cover         # couverture
  python3 episodes/messi/messi.py output/messi                 # rendu complet
"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "scripts"))   # repo / skill installé
from foot import *

TITLE = "~/légendes $ ./lionel_messi"
SLUG = "messi_legende"
VOICE = [os.path.join(HERE, "voix", f"scene_{i}.mp3") for i in range(1, 10)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
PAD = 0.25                                   # silence avant la voix dans chaque scène
def tv(v): return PAD + v                    # temps local d'un mot, à partir de son temps dans le fichier voix
M = Mascot(); MX, MY = 165, 1470             # mascotte : position de repos (coin bas gauche)
PL = Player("messi"); GR = Granny()
COACH = Player("coach", hair=(58, 48, 42)); REX = Player("rexach", hair=(176, 174, 170))

F_T = font("title", 92); F_L = font("hand", 60); F_S = font("hand", 50); F_XS = font("hand", 40)
def HL(txt, key, bg, fg=PAL["cream"], size=84):
    return Label(txt, key, font("title", size), fg, bg, maxw=940, padx=34, pady=18, rough=4)
def TAG(txt, key, bg=PAL["paper"], fg=PAL["ink"], f=None, maxw=820):
    return Label(txt, key, f or F_L, fg, bg, maxw=maxw, padx=26, pady=12)
def STAMP(txt, key, col=PAL["red"], size=120):
    return Label(txt, key, font("title", size), col, PAL["cream"], padx=34, pady=6, rough=2)

_lc = {}
def LBL(txt, key, *a, **k):
    """Label mis en cache (pour les compteurs qui changent de texte)."""
    kk = (key, txt)
    if kk not in _lc: _lc[kk] = Label(txt, key+txt, *a, **k)
    return _lc[kk]
TAG3 = price_tag("", "tag3"); TAG4 = price_tag("", "tag4", PAL["gold"])

def win(t, t_in, t_out=None, d_in=.4, d_out=.3):
    """Facteur d'apparition : pop à t_in, disparition à t_out."""
    a = pop_in(t, t_in, d_in)
    if t_out is not None: a *= 1 - ease_in_cubic(prog(t, t_out, d_out))
    return a
def slam(t, t0, d=.2):
    """Tampon qui s'écrase : échelle 2.2 -> 1."""
    u = prog(t, t0, d)
    return 0 if t < t0 else lerp(2.2, 1.0, ease_out_cubic(u))
def show(cv, fr, lab, t, t_in, t_out, x, y, rot=0, amp=1.0):
    a = win(t, t_in, t_out)
    if a > .01: lab.draw(cv, fr, x, y, a, rot, min(1, a*1.5), amp)
def show_stamp(cv, fr, lab, t, t0, x, y, rot=-6, t_out=None):
    s = slam(t, t0)
    if s <= 0: return
    a = 1 - (ease_in_cubic(prog(t, t_out, .3)) if t_out else 0)
    lab.draw(cv, fr, x, y, s*(1 if a > .99 else a), rot, min(1, prog(t, t0, .08))*a)
def hl(cv, fr, lab, t, t_in, t_out=None, y=330, rot=-1.5):
    """Titre de scène : pop à t_in, s'envole vers le haut à t_out."""
    s = pop_in(t, t_in, .5)
    if s <= 0: return
    o = prog(t, t_out, .35) if t_out is not None else 0
    if o >= 1: return
    lab.draw(cv, fr, CX, y - 260*ease_in_cubic(o), s*(1-.3*o), rot, 1-o)
def impact(cv, t, t0, amp=16, dur=.3):
    if t0 <= t < t0+dur: shake(cv, t, amp*(1-(t-t0)/dur))
def punch(cv, t, t0, z=1.07, dur=.35, center=None):
    if t0 <= t < t0+dur: zoom_punch(cv, 1+(z-1)*(1-(t-t0)/dur), center)
def flashes(cv, t, t0, dur=.18, a=.75):
    if t0 <= t < t0+dur: flash(cv, a*(1-(t-t0)/dur))
def mascot(cv, fr, t, mood="normal", hop=0.0, look=(1, -1), x=MX, y=MY):
    M.draw(cv, fr, x, y, look=look, mood=mood, hop=hop, t=t)

# ------------------------------------------------------------------ objets propres à l'épisode
def _bill_decor(d, a):
    ax, ay = a
    d.rectangle([ax-70, ay-34, ax+70, ay+34], outline=PAL["cream"], width=3)
    d.ellipse([ax-58, ay-26, ax-8, ay+26], fill=PAL["cream"])
    d.text((ax-33, ay), "€", font=font("title", 44), fill=PAL["teal"], anchor="mm")
    d.text((ax+36, ay-2), "500", font=font("title", 38), fill=PAL["cream"], anchor="mm")
BILL = Paper(rect_pts(160, 80), (70, 150, 120), "bill", rough=1.4, hatch=True).add(_bill_decor)
def bill_rain(cv, fr, t, t0, dur=3.0, n=18, key="bills"):
    if t < t0 or t > t0+dur+2: return
    rnd = random.Random(key)
    for i in range(n):
        dl = rnd.uniform(0, dur*.6); tt = t - t0 - dl
        if tt < 0: continue
        x = rnd.uniform(90, 990) + 50*math.sin(tt*2+i); y = 150 + tt*rnd.uniform(420, 620)
        if y > 1950: continue
        BILL.draw(cv, fr, x, y, rnd.uniform(.8, 1.1), 30*math.sin(tt*3+i), 1)

SA = Paper([(-60, -270), (20, -265), (90, -230), (150, -150), (160, -90), (120, -30), (90, 40), (40, 110), (0, 190), (-30, 270),
            (-60, 265), (-70, 180), (-80, 80), (-110, 0), (-150, -90), (-140, -170), (-110, -230)], PAL["teal"], "southam", rough=5, hatch=True)
IBERIA = Paper([(-130, -80), (-40, -100), (60, -95), (120, -70), (130, -20), (90, 40), (40, 90), (-40, 95), (-110, 70), (-140, 10)],
               PAL["sand"], "iberia", rough=5, hatch=True)
PLANE = Paper([(-46, -18), (50, 0), (-46, 18), (-26, 0)], PAL["white"], "plane", rough=1).add(
    lambda d, a: d.line([(a[0]-26, a[1]), (a[0]+48, a[1])], fill=(170, 164, 150), width=3))
OCEAN = Paper(rect_pts(960, 930), (190, 218, 222), "ocean", rough=3, hatch=False)

def _napkin_decor(d, a):
    ax, ay = a; r = 250
    for k in range(40):   # bord gaufré
        for side in range(4):
            p = -r+20 + k*(2*r-40)/39
            x, y = [(ax+p, ay-r+14), (ax+r-14, ay+p), (ax+p, ay+r-14), (ax-r+14, ay+p)][side]
            d.ellipse([x-4, y-4, x+4, y+4], fill=(226, 222, 212))
    d.line([(ax-r+30, ay+r-30), (ax+r-30, ay-r+30)], fill=(236, 232, 222), width=3)
NAPKIN = Paper(rect_pts(500, 500), (250, 250, 246), "napkin", rough=3.5).add(_napkin_decor)
NAPKIN_LINES = ["Barcelona, 14 de diciembre", "del 2000 ... Carles Rexach", "se compromete ... a fichar", "al jugador Lionel Messi ..."]
INKB = (36, 62, 150)
def draw_napkin(cv, fr, x, y, s=1.0, rot=0.0, text_u=1.0, sign_u=1.0, alpha=1.0):
    if s <= .02: return
    if rot == 0 and s == 1.0:
        NAPKIN.draw(cv, fr, x, y, 1, 0, alpha)
        d = ImageDraw.Draw(cv); f = font("hand", 42)
        total = sum(len(l) for l in NAPKIN_LINES); n = int(total*text_u)
        for i, line in enumerate(NAPKIN_LINES):
            k = min(len(line), max(0, n)); n -= len(line)
            if k > 0: d.text((x-205, y-170+i*62), line[:k], font=f, fill=INKB)
        if sign_u > 0:
            pts = [(x-60+k*9, y+150+22*math.sin(k*.9)+(k % 3)*4) for k in range(26)]
            pencil_line(d, pts, sign_u, INKB, 5, 8, 1.2)
            if sign_u >= 1: pencil_line(d, [(x-80, y+185), (x+170, y+178)], 1, INKB, 4, 9, 1)
    else:   # version réduite / tournée : composer dans un calque
        L = layer(560, 560, (280, 280))
        draw_napkin(L, fr, 280, 280, 1.0, 0, text_u, sign_u)
        blit(cv, L, x, y, s, rot, alpha)

HAMMER_H = Paper(rect_pts(26, 230), PAL["clay"], "gavelh", rough=1.2)
HAMMER = Paper(rect_pts(150, 70), (120, 70, 40), "gavel", rough=1.5, hatch=True)
def draw_gavel(cv, fr, x, y, ang, alpha=1.0):
    """Marteau d'enchères : pivot au bout du manche (x, y), ang en degrés (0 = manche vertical, tête en haut)."""
    a = math.radians(ang)
    hx, hy = x + math.sin(a)*200, y - math.cos(a)*200
    HAMMER_H.draw(cv, fr, (x+hx)/2, (y+hy)/2, 1, -ang, alpha)
    HAMMER.draw(cv, fr, hx, hy, 1, -ang, alpha)

SYRINGE = Paper([(-90, -20), (90, -20), (90, 20), (-90, 20)], (226, 238, 244), "syr", rough=1).add(
    lambda d, a: [d.line([(a[0]-60+k*25, a[1]-20), (a[0]-60+k*25, a[1]-6)], fill=(90, 110, 130), width=3) for k in range(6)])
def draw_syringe(cv, fr, x, y, rot=0.0, s=1.0, push=0.0, alpha=1.0):
    L = layer(420, 120, (210, 60)); d = ImageDraw.Draw(L)
    d.rectangle([210-160-40*push, 50, 210-90, 70], fill=(150, 156, 160))
    d.rectangle([210-170-40*push, 36, 210-156-40*push, 84], fill=(120, 126, 130))
    SYRINGE.draw(L, fr, 210, 60, 1, 0, 1, .5)
    d.rectangle([210+10, 46, 210+80-60*push, 74], fill=(150, 200, 220))
    d.line([(210+90, 60), (210+170, 60)], fill=(120, 126, 130), width=4)
    blit(cv, L, x, y, s, rot, alpha)

def _moon_pts(r=70, off=34):
    out = [(r*math.cos(math.radians(a)), r*math.sin(math.radians(a))) for a in range(50, 311, 10)]
    r2 = math.sqrt(r*r - 0) ; inner = []
    for a in range(300, 59, -10):
        ang = math.radians(a); inner.append((off + (r-6)*math.cos(ang)*.95, (r-6)*math.sin(ang)*.95))
    return out + inner
MOON = Paper(_moon_pts(), (250, 240, 196), "moon", rough=1.5)

def _card_decor(d, a):
    ax, ay = a
    d.rectangle([ax-200, ay-100, ax-150, ay-50], fill=PAL["red"])
    d.rectangle([ax-190, ay-86, ax-160, ay-64], fill=PAL["white"]); d.rectangle([ax-182, ay-94, ax-168, ay-56], fill=PAL["white"])
    d.text((ax-130, ay-76), "DIAGNOSTIC", font=font("title", 44), fill=PAL["charcoal"], anchor="lm")
    for k in range(3): d.line([(ax-200, ay+74+k*14), (ax+120-k*60, ay+74+k*14)], fill=(210, 204, 190), width=4)
MED_CARD = Paper(rect_pts(460, 250), PAL["white"], "medcard", rough=2).add(_card_decor)
MED_TXT = Label("déficit d'hormone\nde croissance", "medtxt", font("hand", 46), PAL["red"], None)

def house(key, col, w, h, roof):
    P = Paper([(-w/2, 0), (w/2, 0), (w/2, -h), (-w/2, -h)], col, key, rough=2, hatch=True)
    def dec(d, a):
        ax, ay = a
        d.polygon([(ax-w/2-12, ay-h), (ax, ay-h-roof), (ax+w/2+12, ay-h)], fill=(150, 70, 50))
        for k in range(2): d.rectangle([ax-w/2+22+k*(w/2), ay-h+34, ax-w/2+52+k*(w/2), ay-h+70], fill=(80, 110, 130))
        d.rectangle([ax-16, ay-60, ax+16, ay], fill=(110, 70, 50))
    return P.add(dec)
HOUSES = [(house("h1", PAL["coral"], 190, 170, 70), 150), (house("h2", PAL["mustard"], 170, 210, 60), 360),
          (house("h3", (116, 174, 226), 200, 160, 80), 580), (house("h4", PAL["teal"], 180, 190, 64), 800), (house("h5", PAL["sand"], 150, 150, 60), 990)]
GROUND = Paper(rect_pts(1100, 520), (196, 150, 104), "ground", rough=4, hatch=True)
def bunting(d, t, y=560, u=1.0):
    pts = [(40+k*40, y + 30*math.sin(k/25*math.pi)) for k in range(26)]
    n = int(len(pts)*u)
    if n < 2: return
    d.line(pts[:n], fill=PAL["charcoal"], width=3)
    for k, (x, yy) in enumerate(pts[:n-1]):
        if k % 2: continue
        col = (116, 174, 226) if (k//2) % 2 == 0 else (252, 250, 244)
        sw = 3*math.sin(t*3+k)
        d.polygon([(x, yy), (x+34, yy+2), (x+17+sw, yy+44)], fill=col, outline=(150, 146, 140))

STAR = None
def draw_star(cv, x, y, r, a=1.0, rot=0.0, col=(255, 236, 150)):
    if a <= .01: return
    d = ImageDraw.Draw(cv); d.polygon(star_shape(x, y, r*a, 5, .45, rot-math.pi/2), fill=col)

def _paper_decor(d, a):
    ax, ay = a
    d.text((ax, ay-360), "LA PRESSE", font=font("title", 74), fill=PAL["ink"], anchor="mm")
    d.line([(ax-300, ay-312), (ax+300, ay-312)], fill=PAL["ink"], width=5)
    d.text((ax-300, ay-290), "31 janvier 2021", font=font("hand", 34), fill=(90, 86, 80))
    d.text((ax, ay-200), "LE CONTRAT DE MESSI", font=font("title", 62), fill=PAL["ink"], anchor="mm")
    for c in range(2):
        for k in range(9):
            x0 = ax-300+c*320; d.line([(x0, ay+90+k*28), (x0+280-(k % 3)*40, ay+90+k*28)], fill=(190, 184, 170), width=6)
NEWS = Paper(rect_pts(680, 840), (244, 240, 228), "news", rough=2.5).add(_paper_decor)

PIG = Paper(ellipse_pts(330, 240, 40), (240, 160, 176), "pig", rough=2, hatch=True)
def draw_pig(cv, fr, x, y, s=1.0, alpha=1.0):
    d = ImageDraw.Draw(cv)
    for dx in (-100, -40, 50, 110):
        d.rectangle([x+dx*s-16*s, y+70*s, x+dx*s+16*s, y+140*s], fill=(220, 136, 154))
    PIG.draw(cv, fr, x, y, s, 0, alpha)
    d.ellipse([x+150*s, y-30*s, x+206*s, y+26*s], fill=(226, 140, 158)); d.ellipse([x+166*s, y-10*s, x+174*s, y+2*s], fill=INK)
    d.ellipse([x+184*s, y-10*s, x+192*s, y+2*s], fill=INK)
    d.polygon([(x+70*s, y-100*s), (x+120*s, y-150*s), (x+120*s, y-90*s)], fill=(226, 140, 158))
    d.ellipse([x+96*s, y-50*s, x+110*s, y-36*s], fill=INK)
    d.rectangle([x-40*s, y-118*s, x+40*s, y-108*s], fill=(120, 60, 70))
    d.text((x-30*s, y+10*s), "BARÇA", font=font("title", int(54*s)), fill=(150, 30, 70), anchor="mm")
def moth(cv, x, y, t, s=1.0):
    d = ImageDraw.Draw(cv); f = abs(math.sin(t*18))
    d.polygon([(x, y), (x-30*s, y-30*s*f-6), (x-34*s, y+12*s)], fill=(160, 150, 140))
    d.polygon([(x, y), (x+30*s, y-30*s*f-6), (x+34*s, y+12*s)], fill=(160, 150, 140))
    d.ellipse([x-5*s, y-12*s, x+5*s, y+14*s], fill=(90, 84, 78))

def _contract_decor(d, a):
    ax, ay = a
    d.text((ax, ay-220), "CONTRAT", font=font("title", 70), fill=PAL["ink"], anchor="mm")
    d.text((ax-170, ay-130), "Salaire :", font=font("hand", 48), fill=PAL["ink"])
    d.text((ax-170, ay-66), "100 %", font=font("title", 64), fill=PAL["ink"])
    for k in range(5): d.line([(ax-170, ay+50+k*30), (ax+170-(k % 2)*70, ay+50+k*30)], fill=(200, 194, 180), width=6)
    pencil_line(d, [(ax+30+k*8, ay+230+10*math.sin(k)) for k in range(16)], 1, INKB, 4, 2, 1)
CONTRACT = Paper(rect_pts(440, 560), (250, 248, 240), "contract", rough=2).add(_contract_decor)
_contract_halves = {}
def contract_halves():
    if not _contract_halves:
        spr = CONTRACT.v[0]; A, B, _ = tear_split(spr, "v", 7, rough=20)
        _contract_halves["ab"] = (A, B, spr.info["anchor"])
    return _contract_halves["ab"]

EIFFEL = Paper([(-150, 0), (-90, 0), (-40, -120), (40, -120), (90, 0), (150, 0), (70, -200), (30, -380), (12, -520), (0, -600), (-12, -520), (-30, -380), (-70, -200)],
               (58, 56, 60), "eiffel", rough=1.5, hatch=True)
EIFFEL.add(lambda d, a: [d.line([(a[0]-56, a[1]-200), (a[0]+56, a[1]-200)], fill=(90, 88, 92), width=6),
                         d.line([(a[0]-30, a[1]-380), (a[0]+30, a[1]-380)], fill=(90, 88, 92), width=5)])

def palm(key):
    P = Paper([(-16, 0), (16, 0), (30, -200), (46, -420), (24, -424), (6, -210)], (150, 100, 60), key+"t", rough=2, hatch=True)
    L = Paper(poly_pts([(0, 0), (80, -40), (170, -20), (230, 40), (150, 10), (70, 20)]), (50, 150, 100), key+"l", rough=2.5, hatch=True)
    return P, L
PALM = palm("palm")
def draw_palm(cv, fr, x, y, s=1.0, t=0.0, flip=1):
    P, L = PALM
    P.draw(cv, fr, x, y, s)
    tx, ty = x + 36*s*flip, y - 422*s
    for k, ang in enumerate((-10, 30, 75, 130, 170, 210)):
        L.draw(cv, fr, tx, ty, s, -ang + 4*math.sin(t*2+k), 1)

TV = Paper(rect_pts(300, 200), (46, 44, 42), "tv", rough=1.6).add(lambda d, a: [
    d.rectangle([a[0]-130, a[1]-80, a[0]+130, a[1]+80], fill=(90, 150, 200)),
    d.polygon([(a[0]-30, a[1]-40), (a[0]+44, a[1]), (a[0]-30, a[1]+40)], fill=PAL["white"])])
BAG = Paper([(-110, -90), (110, -90), (130, 120), (-130, 120)], PAL["sand"], "bag", rough=2, hatch=True).add(lambda d, a: [
    d.arc([a[0]-60, a[1]-160, a[0]+60, a[1]-40], 180, 360, fill=(120, 90, 60), width=10),
    d.text((a[0], a[1]+20), "%", font=font("title", 110), fill=(150, 110, 60), anchor="mm")])

BOARD = Paper(rect_pts(820, 560), PAL["paper"], "rankboard", rough=2.5).add(lambda d, a: [
    d.text((a[0], a[1]-220), "MEILLEURS BUTEURS", font=font("title", 60), fill=PAL["ink"], anchor="mm"),
    d.text((a[0], a[1]-160), "de l'histoire de la Coupe du monde", font=font("hand", 44), fill=(90, 86, 80), anchor="mm"),
    d.line([(a[0]-360, a[1]-120), (a[0]+360, a[1]-120)], fill=PAL["ink"], width=4)])

SCORE = scoreboard_sprite(820, 330)
LED = (255, 204, 70)
def draw_score(cv, fr, x, y, a, b, s=1.0, minute="", alpha=1.0):
    if s <= .02: return
    L = layer(900, 420, (450, 210)); SCORE.draw(L, fr, 450, 210, 1, 0, 1)
    d = ImageDraw.Draw(L); fm = font("mono", 64); fb = font("title", 150)
    d.text((450-270, 130), "ARG", font=fm, fill=(200, 196, 190), anchor="mm"); d.text((450+270, 130), "FRA", font=fm, fill=(200, 196, 190), anchor="mm")
    d.text((450, 220), f"{a} - {b}", font=fb, fill=LED, anchor="mm")
    if minute: d.text((450, 330), minute, font=font("mono", 40), fill=(170, 166, 160), anchor="mm")
    blit(cv, L, x, y, s, 0, alpha)

TROPHY_SPOTS = [(190, 960, CUP, .7), (890, 960, CUP, .7), (190, 1240, None, .55), (900, 1330, WC_TROPHY, .5)]

# ------------------------------------------------------------------ labels
S1_STAMPS = [STAMP("TROP PETIT", "s1a"), STAMP("TROP FRAGILE", "s1b"), STAMP("TROP CHER", "s1c")]
H1 = HL("LE PLUS TITRÉ DE L'HISTOIRE", "h1", PAL["mustard"], PAL["ink"], 84)
T1a = TAG("Argentine, années 90", "t1a", f=F_S)
N1a = Label("l'histoire folle de", "n1a", font("hand", 64), PAL["ink"], PAL["paper"], padx=30, pady=8)
N1b = HL("LIONEL MESSI", "n1b", PAL["coral"], PAL["cream"], 130)

H2 = HL("ROSARIO, 1987", "h2", PAL["teal"])
T2a = TAG("né le 24 juin 1987", "t2a", f=F_S)
T2b = TAG("Celia, sa grand-mère", "t2b", PAL["mustard"])
T2c = TAG("elle convainc l'entraîneur", "t2c", f=F_S)
T2d = TAG("le plus petit du terrain", "t2d", PAL["coral"], PAL["cream"], f=F_S)
T2e = TAG("chaque but : pour elle", "t2e", PAL["teal"], PAL["cream"])

H3 = HL("10 ANS : 1,27 M", "h3", PAL["coral"])
T3a = Label("1,27 m", "t3a", font("title", 72), PAL["red"], PAL["cream"], padx=20, pady=6)
T3b = TAG("1 piqûre chaque soir", "t3b", PAL["paper"])
T3c = TAG("365 par an", "t3c", PAL["mustard"], f=F_S)
S3 = STAMP("TROP CHER", "s3", size=96)
TAG3_TXT = font("title", 64)

H4 = HL("DIRECTION BARCELONE", "h4", PAL["mustard"], PAL["ink"])
H4b = HL("UN CONTRAT SUR UNE SERVIETTE", "h4b", PAL["coral"], size=80)
T4a = TAG("13 ans, septembre 2000", "t4a", f=F_S)
T4b = TAG("Carles Rexach\ndirecteur sportif du Barça", "t4b", f=font("hand", 44))
T4c = TAG("14 décembre 2000", "t4c", PAL["mustard"], f=F_S)
T4d = TAG("le Barça paie son traitement", "t4d", PAL["teal"], PAL["cream"], f=F_S)
T4e = TAG("vente Bonhams, mai 2024", "t4e", f=F_XS)
QMS = [Label("?", f"qm{i}", font("title", 150), PAL["coral"], None) for i in range(3)]
EXCL = Label("!", "excl", font("title", 140), PAL["red"], None)
LBL_R = Label("Rosario", "lr", font("hand", 44), PAL["ink"], PAL["paper"], padx=14, pady=4)
LBL_B = Label("Barcelone", "lb", font("hand", 44), PAL["ink"], PAL["paper"], padx=14, pady=4)

H5 = HL("LE TRAITEMENT MARCHE", "h5", PAL["teal"])
H5b = HL("17 ANS : PREMIERS PAS", "h5b", PAL["mustard"], PAL["ink"])
T5a = TAG("débuts pros : 16 oct. 2004", "t5a", f=F_S)
T5b = TAG("passe lobée de Ronaldinho", "t5b", PAL["mustard"], f=F_S)
T5c = TAG("1er but : 1er mai 2005", "t5c", PAL["coral"], PAL["cream"], f=F_S)
T5d = TAG("2008 : il hérite du n°10", "t5d", f=F_S)
T5plus = Label("+ 43 cm", "t5p", font("title", 70), PAL["teal"], PAL["cream"], padx=20, pady=6)

H6a = HL("2009", "h6a", PAL["coral"], size=120)
H6b = HL("2012", "h6b", PAL["teal"], size=120)
H6c = HL("8 BALLONS D'OR", "h6c", PAL["mustard"], PAL["ink"])
T6a = Label("6 / 6", "t6a", font("title", 140), PAL["cream"], PAL["coral"], padx=30, pady=6, rough=4)
T6b = TAG("6 titres sur 6 en une année", "t6b", f=F_S)
T6c = TAG("buts en 12 mois", "t6c", f=F_L)
S6 = STAMP("RECORD DU MONDE", "s6", size=90)
S6b = STAMP("RECORD ABSOLU", "s6b", col=(200, 140, 20), size=96)
T6d = Label("2009 · 2010 · 2011 · 2012 · 2015 · 2019 · 2021 · 2023", "t6d", font("hand", 38), PAL["ink"], PAL["paper"], padx=16, pady=6)

H7 = HL("HORS NORME", "h7", PAL["teal"], size=110)
H7b = HL("DIRECTION PARIS", "h7b", (16, 40, 86))
T7a = TAG("révélé par El Mundo", "t7a", f=F_S)
T7b = TAG("sur 4 saisons (2017-2021)", "t7b", PAL["mustard"], f=F_S)
S7 = STAMP("RECORD", "s7", size=110)
T7c = TAG("plus d'1 milliard d'euros de dettes", "t7c", PAL["coral"], PAL["cream"], f=F_S)
T7d = Label("-50 %", "t7d", font("title", 110), PAL["red"], None)
T7e = TAG("août 2021 : PSG", "t7e", f=F_S)

H8 = HL("LA COUPE DU MONDE", "h8", PAL["gold"], PAL["ink"])
H8b = HL("QATAR 2022", "h8b", (140, 20, 50))
T8a = TAG("2016 : finale de Copa América", "t8a", f=F_S)
T8b = TAG("il quitte la sélection…", "t8b", f=F_S)
T8c = TAG("… puis il revient !", "t8c", PAL["mustard"], f=F_S)
T8d = TAG("doublé de Messi", "t8d", (116, 174, 226), PAL["ink"])
T8e = Label("tirs au but : 4 - 2", "t8e", font("title", 60), PAL["cream"], PAL["teal"], padx=24, pady=8)
S8 = STAMP("ENFIN !", "s8", col=(200, 140, 20), size=150)

H9 = HL("MIAMI, EN ROSE", "h9", (246, 170, 200), PAL["ink"])
H9b = HL("MONDIAL 2026", "h9b", PAL["teal"])
H9c = HL("LE PLUS GRAND", "h9c", PAL["gold"], PAL["ink"], 110)
T9y = Label("2023", "t9y", font("title", 120), PAL["ink"], PAL["paper"], padx=30, pady=6)
T9a = TAG("une part des abonnements\nApple TV", "t9a", f=font("hand", 44))
T9b = TAG("une part des ventes\nAdidas", "t9b", f=font("hand", 44))
T9c = Label("1. MESSI", "t9c", font("title", 96), PAL["ink"], PAL["gold"], padx=30, pady=8, rough=3)
T9d = Label("ancien record : Klose, 16 buts", "t9d", font("hand", 50), (110, 106, 100), None)
T9e = TAG("Abonne-toi pour la prochaine légende !", "t9e", PAL["coral"], PAL["cream"], f=F_S)
T9f = TAG("Ronaldo ? Zidane ? Mbappé ? Dis-le en commentaire", "t9f", f=font("hand", 40))

# ------------------------------------------------------------------ SCÈNE 1 — accroche : « trop petit »
S1_T = [tv(.15), tv(.81), tv(1.57)]; S1_POS = [(540, 520, -7), (560, 690, 5), (520, 860, -3)]
def s1(cv, fr, t, T):
    d = ImageDraw.Draw(cv)
    tw = tv(4.59)                                  # « Aujourd'hui… » : bascule
    if t < tw + .9:
        T1a.draw(cv, fr, CX, 330, win(t, tv(2.65), tw), -1)
    if t >= tw:
        rays(cv, (CX, 1050), t, clamp((t-tw)/.4)); confetti(cv, fr, "c1", t-tw-.2, 50, 5)
    # le gamin -> la légende (tour sur lui-même)
    su = clamp((t-tw)/.6)
    if su <= 0:
        mood = "normal" if t < S1_T[0] else "sad"
        PL.draw(cv, fr, CX, 1450, 1.0, age=0, kit="newells", mood=mood, look=(0, 1 if t > S1_T[0] else 0), t=t)
        draw_ball(cv, fr, CX+150, 1400, .7, 0)
    elif su < 1:
        sx = math.cos(su*math.pi*2)
        if su < .25: L = PL.render_layer(fr, 1.0, age=0, kit="newells", mood="sad")
        else: L = PL.render_layer(fr, 1.0, age=1, kit="arg", beard=True, mood="cheer", arms=(160, 160))
        blit_sxy(cv, L, CX, 1450, max(.04, abs(sx)), 1.0)
    else:
        PL.draw(cv, fr, CX, 1450, 1.0, age=1, kit="arg", beard=True, mood="cheer", arms=(160+6*math.sin(t*6), 160+6*math.sin(t*6+1)), t=t)
    # trophées qui pleuvent autour
    for i, (x, y, obj, sc) in enumerate(TROPHY_SPOTS):
        a = pop_in(t, tw+.35+i*.18, .45)
        if a <= 0: continue
        yy = y - 500*(1-ease_out_cubic(prog(t, tw+.35+i*.18, .35)))
        if obj is None: draw_ballon_or(cv, fr, x, yy, sc*a)
        else: obj.draw(cv, fr, x, yy, sc*a, 6*math.sin(t*2+i))
    # tampons
    for i, lab in enumerate(S1_STAMPS):
        if t >= tw:
            u = ease_in_cubic(prog(t, tw+i*.06, .45)); x, y, r = S1_POS[i]
            if u < 1: lab.draw(cv, fr, x + (i-1)*400*u, y - 900*u, 1, r + 90*u*(1 if i % 2 else -1), 1)
        else:
            x, y, r = S1_POS[i]; show_stamp(cv, fr, lab, t, S1_T[i], x, y, r)
    hl(cv, fr, H1, t, tw+.3, tv(7.2), y=330)
    N1a.draw(cv, fr, CX, 300, win(t, tv(7.31)), -2); N1b.draw(cv, fr, CX, 440, win(t, tv(7.9), None, .5), 2)
    mascot(cv, fr, t, "surprised" if S1_T[0] < t < tw else ("happy" if t > tw else "normal"), hop=abs(math.sin(t*9))*40 if tw < t < tw+1 else 0)
    for t0 in S1_T: impact(cv, t, t0, 18)
    flashes(cv, t, tw, .25, .8)

# ------------------------------------------------------------------ SCÈNE 2 — Rosario, la grand-mère
def s2(cv, fr, t, T):
    d = ImageDraw.Draw(cv)
    GROUND.draw(cv, fr, CX, 1690)
    for P, x in HOUSES: P.draw(cv, fr, x, 1440 - 40*(1-ease_out_cubic(prog(t, .1, .5))), 1, 0, 1, .8)
    bunting(d, t, 560, prog(t, .3, .8))
    hl(cv, fr, H2, t, .15)
    show(cv, fr, T2a, t, tv(1.0), tv(3.0), CX, 680, 2)
    # grand-mère + le petit qui arrivent en se tenant la main
    tg = tv(3.19); walk = ease_out_cubic(prog(t, tg-.2, 1.3))
    gx = lerp(-160, 330, walk); bob = abs(math.sin(t*9))*8 if 0 < walk < 1 else 0
    t_goal = tv(8.52); t_sky = tv(9.7)
    ghost = 1 - prog(t, t_sky, 1.2)
    point = ease_out_cubic(prog(t, tv(5.62), .4))
    if walk > 0:
        GR.draw(cv, fr, gx, 1460-bob, 1.2, arms=(10, lerp(40, 100, point) if point > 0 else 40), alpha=ghost, t=t)
    # l'entraîneur
    ca = win(t, tv(5.62), t_goal-.2)
    if ca > .01:
        cx_ = lerp(1200, 860, ease_out_cubic(prog(t, tv(5.5), .5)))
        COACH.draw(cv, fr, cx_, 1460, 1.1, age=1, kit="coach", mood="surprised" if t < tv(7.2) else "happy", alpha=min(1, ca), t=t,
                   arms=(8, 8))
        if tv(5.9) < t < tv(6.6): d.ellipse([cx_-14, 1460-560*1.1+30, cx_+14, 1460-560*1.1+58], fill=(170, 170, 170))
    # le gamin : tenu par la main, puis dribble, frappe et pointe le ciel
    kx = gx + 140 if t < tv(6.8) else lerp(gx+140, 520, ease_io(prog(t, tv(6.8), .8)))
    sky = ease_out_cubic(prog(t, t_sky, .5))
    arms = (lerp(40, 168, sky), lerp(8, 168, sky)) if sky > 0 else ((40, 8) if t < tv(6.8) else (20, 20))
    kick = math.sin(prog(t, t_goal-.15, .3)*math.pi)*40
    if walk > 0:
        PL.draw(cv, fr, kx, 1460-bob*.6, .8, age=0, kit="street", mood="happy" if sky > 0 or t > t_goal else "normal",
                arms=arms, legs=(0, kick), look=(1, -1) if sky > 0 else (1, 0), t=t, kid_hair=True)
    # ballon
    gx_goal = 900
    if tv(6.8) < t < t_goal:
        bx = kx + 80; by = 1430 - abs(math.sin(t*7))*70
        draw_ball(cv, fr, bx, by, .6, t*200)
    if t >= t_goal:
        u = prog(t, t_goal, .45)
        p = bezier((kx+80, 1430), ((kx+gx_goal)/2, 1150), (gx_goal, 1360), ease_out_cubic(u))
        draw_goal(cv, fr, gx_goal, 1460, 260, 180, prog(t, t_goal+.4, .5), 1, t)
        draw_ball(cv, fr, p[0], p[1], .6, t*500)
    elif t > tv(6.8): draw_goal(cv, fr, gx_goal, 1460, 260, 180, 0, 1, t)
    # l'étoile dans le ciel
    if sky > 0:
        rays(cv, (CX, 760), t, .6*sky, 12, 500, (255, 236, 160))
        draw_star(cv, CX, 760, 70, sky, t*.5)
        for k in range(6):
            draw_star(cv, 160+k*150, 640+60*math.sin(k*2.1), 16, sky*abs(math.sin(t*2+k)), 0, (255, 246, 200))
    show(cv, fr, T2b, t, tv(3.4), tv(5.5), 360, 760, -2)
    show(cv, fr, T2c, t, tv(5.8), tv(7.3), 560, 700, 1)
    show(cv, fr, T2d, t, tv(7.3), tv(8.9), 560, 700, -1)
    show(cv, fr, T2e, t, tv(11.1), None, CX, 960, -1.5)
    mascot(cv, fr, t, "happy" if t > t_sky else "normal")
    flashes(cv, t, t_sky, .2, .5)

# ------------------------------------------------------------------ SCÈNE 3 — le diagnostic
TOISE = toise_sprite(483, [])
PX_M = 483; FLOOR = 1480
def s3(cv, fr, t, T):
    d = ImageDraw.Draw(cv)
    night = ease_io(prog(t, tv(5.31), .7))
    hl(cv, fr, H3, t, .15)
    TOISE.draw(cv, fr, lerp(-120, 250, ease_out_cubic(prog(t, 0, .5))), FLOOR)
    sad = t > tv(9.59)
    PL.draw(cv, fr, 540, FLOOR, 1.3, age=0, kit="newells", mood="sad" if sad else ("surprised" if tv(2.74) < t < tv(5.3) else "normal"),
            look=(-1, 0) if t < tv(2.6) else (0, 0), t=t)
    # trait de mesure à 1,27 m
    y127 = FLOOR - 1.27*PX_M
    mu = prog(t, tv(.9), .6)
    if mu > 0:
        pencil_line(d, [(300, y127), (680, y127)], mu, PAL["red"], 6, 3, 1)
        T3a.draw(cv, fr, 800, y127, pop_in(t, tv(1.3)), -3)
    # fiche médicale
    ca = win(t, tv(2.74), tv(5.31))
    if ca > .01:
        MED_CARD.draw(cv, fr, 700, 560, ca, 2)
        if t > tv(3.65): MED_TXT.draw(cv, fr, 690, 610, pop_in(t, tv(3.65))*ca, -3)
    # la nuit : lune, étoiles, piqûre
    if night > 0:
        tint(cv, .35*night)
        MOON.draw(cv, fr, 860, 560, night, -20)
        for k in range(7):
            draw_star(cv, 380+k*70, 470+40*math.sin(k*1.7), 10, night*abs(math.sin(t*2+k)), 0, (255, 246, 200))
        sa = win(t, tv(6.04), tv(9.4))
        if sa > .01:
            push = prog(t, tv(7.31), .5)
            poke = 30*(1-prog(t, tv(7.31), .3)) if t > tv(7.0) else 30
            draw_syringe(cv, fr, 720+poke, 1250, -25, sa, push)
        show(cv, fr, T3b, t, tv(6.1), tv(9.4), 540, 480, -1)
        show(cv, fr, T3c, t, tv(7.5), tv(9.4), 540, 590, 2)
    # l'étiquette de prix
    pa = pop_in(t, tv(8.06), .5)
    if pa > 0:
        sw = 8*math.sin(t*3)*(1-prog(t, tv(8.06), 2))
        TAG3.draw(cv, fr, 690, 1020, pa, sw)
        L = f"{counter(0, 1000, prog(t, tv(8.2), .8))} $"
        d.text((690+88*pa, 1000), L, font=font("title", int(60*pa)), fill=PAL["ink"], anchor="mm")
        d.text((690+88*pa, 1058), "par mois", font=font("hand", int(40*pa)), fill=PAL["ink"], anchor="mm")
        show_stamp(cv, fr, S3, t, tv(9.6), 700, 1170, -8)
    mascot(cv, fr, t, "surprised" if t > tv(2.74) else "normal", look=(1, 0))
    impact(cv, t, tv(9.6), 16)

# ------------------------------------------------------------------ SCÈNE 4 — la serviette
TORN_JERSEY = {}
def s4(cv, fr, t, T):
    d = ImageDraw.Draw(cv)
    t_club = tv(3.04); t_nap = tv(6.02); t_pay = tv(10.09); t_sold = tv(12.66); hit = tv(12.9)
    hl(cv, fr, H4, t, .15, tv(8.4))
    hl(cv, fr, H4b, t, tv(8.53), tv(10.0))
    # carte : l'océan
    mo = ease_in_cubic(prog(t, t_club-.3, .5))
    if mo < 1:
        oy = 960 + 1100*mo
        OCEAN.draw(cv, fr, CX, oy, 1, 0, 1, .6)
        for k in range(6):
            yy = oy - 380 + k*140
            pencil_line(d, [(150+j*40, yy+8*math.sin(j*.8+t*2)) for j in range(20)], 1, (150, 190, 196), 3, k, .5)
        SA.draw(cv, fr, 260, oy+160, 1, 0, 1, 1); IBERIA.draw(cv, fr, 800, oy-280, 1, 0, 1, 1)
        R, B = (270, oy+250), (905, oy-320)
        d.ellipse([R[0]-12, R[1]-12, R[0]+12, R[1]+12], fill=PAL["red"]); d.ellipse([B[0]-12, B[1]-12, B[0]+12, B[1]+12], fill=PAL["red"])
        LBL_R.draw(cv, fr, R[0]+20, R[1]+60, pop_in(t, .3)); LBL_B.draw(cv, fr, B[0]-60, B[1]+60, pop_in(t, .5))
        pu = ease_io(prog(t, tv(.3), 2.3)); ctrl = (420, oy-420)
        pts = [bezier(R, ctrl, B, k/40) for k in range(41)]
        n = int(40*pu)
        for k in range(0, n, 2): d.line([pts[k], pts[k+1]], fill=PAL["charcoal"], width=5)
        if 0 < pu < 1:
            p = bezier(R, ctrl, B, pu); p2 = bezier(R, ctrl, B, min(1, pu+.02))
            PLANE.draw(cv, fr, p[0], p[1]-20, 1.3, -math.degrees(math.atan2(p2[1]-p[1], p2[0]-p[0])))
        show(cv, fr, T4a, t, tv(.4), t_club-.3, CX, 1460, -2)
    # l'essai : le gamin jongle, le directeur sportif est bluffé
    ka = ease_out_cubic(prog(t, t_club-.1, .5)); ko = ease_in_cubic(prog(t, t_nap-.2, .4))
    if ka > 0 and ko < 1:
        kx = lerp(-200, 330, ka) - 700*ko
        PL.draw(cv, fr, kx, 1450, 1.1, age=.2, kit="newells", mood="determined", legs=(0, 25*abs(math.sin(t*6))), t=t)
        draw_ball(cv, fr, kx+80, 1300 - abs(math.sin(t*6))*180, .6, t*300)
        rx = lerp(1250, 790, ka) + 700*ko
        REX.draw(cv, fr, rx, 1450, 1.05, age=1, kit="suit", mood="surprised" if t < tv(4.77) else "normal", look=(-1, 0), t=t,
                 arms=(8, 8) if t < tv(4.77) else (8, -40))
        EXCL.draw(cv, fr, rx+90, 700, win(t, tv(3.6), tv(4.77)), 10)
        show(cv, fr, T4b, t, tv(3.3), tv(4.77), 700, 620, 2)
        for i, q in enumerate(QMS):
            a = win(t, tv(4.77)+i*.15, t_nap-.3)
            if a > .01: q.draw(cv, fr, 560+i*130, 640 + 20*math.sin(t*4+i), a, (-10, 5, 12)[i])
    # la serviette
    na = ease_out_back(prog(t, t_nap, .6), 1.2); nx, ny, ns, nr = CX, 900, 1.0, 0
    if t > t_pay:
        u = ease_io(prog(t, t_pay, .6)); nx, ny, ns = lerp(CX, 250, u), lerp(900, 640, u), lerp(1, .42, u)
    if t > tv(11.63):
        u = ease_io(prog(t, tv(11.63), .6)); nx, ny, ns = lerp(250, 470, u), lerp(640, 860, u), lerp(.42, .85, u)
    if na > 0:
        if t < t_pay:
            nr = lerp(-200, 0, ease_out_cubic(prog(t, t_nap, .6)))
            if nr != 0 or na < .999: draw_napkin(cv, fr, CX, lerp(-300, 900, clamp(na)), max(.1, na), nr, 0, 0)
            else:
                draw_napkin(cv, fr, CX, 900, 1.0, 0, prog(t, t_nap+.4, 2.0), prog(t, tv(8.0), .6))
        else:
            if t > tv(11.63): rays(cv, (nx, ny), t, .7*prog(t, tv(11.63), .5), 12, 700)
            draw_napkin(cv, fr, nx, ny, ns, -4 if t < tv(11.63) else 0, 1, 1)
    show(cv, fr, T4c, t, tv(8.8), t_pay, CX, 1260, -2)
    # le Barça paiera : le maillot de Newell's se déchire, le maillot du Barça apparaît
    pa = ease_out_cubic(prog(t, t_pay, .5)); po = ease_in_cubic(prog(t, tv(11.4), .4))
    if pa > 0 and po < 1:
        px = lerp(1250, 640, pa) + 700*po; tr = tv(10.5)
        PL.draw(cv, fr, px, 1450, 1.15, age=.2, kit="barca" if t > tr else "newells", mood="happy" if t > tr else "normal", t=t,
                arms=(8, 8) if t < tr else (60, 60))
        if t > tr:
            if "ab" not in TORN_JERSEY:
                spr = jersey_front("newells").v[0]; A, B, _ = tear_split(spr, "v", 3, rough=14); TORN_JERSEY["ab"] = (A, B, spr.info["anchor"])
            A, B, anc = TORN_JERSEY["ab"]; u = ease_in_cubic(prog(t, tr, .7))
            bs = 1.15*lerp(.7, 1, .2); jy = 1450 + (NECK_Y+95)*bs
            for P, sg in ((A, -1), (B, 1)):
                if u < 1:
                    P.info["anchor"] = anc; blit(cv, P, px + sg*(8+520*u), jy + 300*u*u, .4*bs/0.85, sg*-50*u, 1-u*.3)
        show(cv, fr, T4d, t, tr+.3, tv(11.4), 640, 790, -1.5)
    # vendue aux enchères
    if t > t_sold - .5:
        ga = win(t, t_sold-.4, None, .3)
        ang = lerp(-60, 10, ease_in_cubic(prog(t, hit-.3, .3))) if t < hit + .1 else lerp(10, -30, ease_out_cubic(prog(t, hit+.1, .5)))
        draw_gavel(cv, fr, 860, 1330, ang, min(1, ga))
        pa2 = pop_in(t, tv(13.1), .5)
        if pa2 > 0:
            TAG4.draw(cv, fr, 470, 1330, pa2, -3)
            d.text((470+100*pa2, 1330), f"{counter(0, 965000, prog(t, tv(13.2), 1.1))} $", font=font("title", int(52*pa2)), fill=PAL["ink"], anchor="mm")
        show(cv, fr, T4e, t, tv(13.6), None, 590, 1460, 1)
    mascot(cv, fr, t, "surprised" if tv(8.53) < t < tv(9.8) or t > hit else "normal")
    punch(cv, t, tv(8.53), 1.08); impact(cv, t, tv(12.9), 14)

# ------------------------------------------------------------------ SCÈNE 5 — il grandit, débuts, premier but
JB30 = jersey_back("barca", "MESSI", 30); JB10 = jersey_back("barca", "MESSI", 10)
def s5(cv, fr, t, T):
    d = ImageDraw.Draw(cv)
    tg0, tg1 = tv(1.31), tv(2.9); t_deb = tv(3.52); t_goal = tv(6.42); t_lob = tv(7.23); t_shot = tv(8.35); t_ten = tv(9.03); t_run = tv(10.3)
    hl(cv, fr, H5, t, .1, t_deb)
    hl(cv, fr, H5b, t, t_deb+.1, t_run)
    age = ease_io(prog(t, tg0, tg1-tg0))
    # la toise et la croissance
    to = ease_in_cubic(prog(t, t_deb, .5))
    if to < 1:
        TOISE.draw(cv, fr, lerp(-120, 250, ease_out_cubic(prog(t, 0, .5))) - 500*to, FLOOR)
        top = FLOOR - (lerp(1.27, 1.70, age))*PX_M
        pencil_line(d, [(300-500*to, top), (680-500*to, top)], 1, PAL["red"], 6, 3, 1)
        lab = LBL(f"{lerp(1.27, 1.70, age):.2f} m".replace(".", ","), "gr", font("title", 72), PAL["red"], PAL["cream"], padx=20, pady=6)
        lab.draw(cv, fr, 830-500*to, top, pop_in(t, .3), -3)
        T5plus.draw(cv, fr, 830-500*to, top+110, win(t, tg1-.1, t_deb), 4)
    # le joueur
    px = 540 if t < t_deb else lerp(540, 330, ease_io(prog(t, t_deb, .6)))
    ps = 1.3 if t < t_deb else lerp(1.3, 1.0, ease_io(prog(t, t_deb, .6)))
    if t >= t_run:   # et tout s'accélère : il file vers la droite
        u = prog(t, t_run, 1.5); px = lerp(330, 1350, u*u)
    shot = math.sin(prog(t, t_shot-.15, .35)*math.pi)
    run = math.sin(t*14)*25 if t > t_run else 0
    bounce = 1 + .04*math.sin(prog(t, tg1, .3)*math.pi)
    PL.draw(cv, fr, px, FLOOR, ps*bounce, age=age, kit="barca", mood="happy" if tg1 < t < t_deb or t > t_shot else "determined",
            legs=(run, -run + 45*shot), arms=(20+run, 20-run), t=t, look=(1, -1) if t_lob < t < t_shot else (0, 0))
    if tg0 < t < tg1: particles(cv, fr, "grow", (540, FLOOR-700), prog(t, tg1-.2, .6), 20, 260)
    # le maillot n°30
    ja = win(t, t_deb+.3, t_goal-.2)
    if ja > .01: JB30.draw(cv, fr, 770, 900, .6*ja, 5)
    show(cv, fr, T5a, t, t_deb+.5, t_goal-.2, CX, 480, -1.5)
    # premier but : passe lobée de Ronaldinho
    if t > t_goal - .2:
        ga = ease_out_cubic(prog(t, t_goal-.2, .5)); go = ease_in_cubic(prog(t, t_ten-.3, .4))
        gx = lerp(1300, 820, ga) + 600*go
        draw_goal(cv, fr, gx, FLOOR, 360, 220, prog(t, t_shot+.35, .6), 1, t)
        show(cv, fr, T5b, t, t_lob, t_shot+.5, 380, 560, 2)
        if t_lob < t < t_shot:
            p = bezier((80, 560), (300, 380), (px+60, FLOOR-160), ease_io(prog(t, t_lob, t_shot-t_lob)))
            draw_ball(cv, fr, p[0], p[1], .6, t*300)
        elif t_shot <= t < t_ten:
            u = prog(t, t_shot, .45)
            p = bezier((px+60, FLOOR-160), ((px+gx)/2, FLOOR-520), (gx, FLOOR-110), ease_out_cubic(u))
            draw_ball(cv, fr, p[0], p[1], .6, t*600)
        show(cv, fr, T5c, t, t_shot+.4, t_ten-.2, CX, 700, -1)
    # le n°10
    if t > t_ten - .2:
        fa = win(t, t_ten-.2, t_run+.2); fu = prog(t, t_ten+.4, .5)
        sx = math.cos(fu*math.pi)
        J = JB30 if fu < .5 else JB10
        if fa > .01: blit_sxy(cv, J.v[boil(fr)], 700, 900, .62*fa*max(.04, abs(sx)), .62*fa, 3)
        if fu > .5: particles(cv, fr, "ten", (700, 900), prog(t, t_ten+.65, .6), 22, 300, [PAL["gold"], PAL["mustard"], PAL["cream"]])
        show(cv, fr, T5d, t, t_ten+.7, t_run+.2, 700, 1260, -2)
    if t > t_run:
        speed_lines(cv, fr, (CX, 1000), prog(t, t_run, .3), seed=5)
        draw_ball(cv, fr, px+90, FLOOR-40, .6, t*900)
    mascot(cv, fr, t, "happy" if t > tg1 else "normal", hop=abs(math.sin(t*9))*35 if tg1 < t < tg1+.8 else 0)
    punch(cv, t, t_shot+.35, 1.06); flashes(cv, t, t_shot+.35, .15, .5); punch(cv, t, t_run, 1.05, .5)

# ------------------------------------------------------------------ SCÈNE 6 — la machine à records
CUP_POS = [(260, 760), (540, 760), (820, 760), (260, 1090), (540, 1090), (820, 1090)]
BDO_POS = [(315, 1200), (465, 1200), (615, 1200), (765, 1200), (390, 1060), (540, 1060), (690, 1060), (540, 920)]
def s6(cv, fr, t, T):
    d = ImageDraw.Draw(cv)
    t12 = tv(3.43); t91 = tv(4.29); tbo = tv(6.62); tno = tv(8.54)
    # 6 trophées sur 6
    co = ease_in_cubic(prog(t, t12, .45))
    for i, (x, y) in enumerate(CUP_POS):
        a = pop_in(t, tv(1.07)+i*.2, .4)
        if a > 0 and co < 1: CUP.draw(cv, fr, x, y - 900*co, .8*a, 4*math.sin(t*2+i))
    T6a.draw(cv, fr, CX, 1330 + 700*co, win(t, tv(2.3), t12), -3)
    show(cv, fr, T6b, t, tv(2.6), t12, CX, 1480, 1)
    # 91 buts
    if t12 < t < tbo + .5:
        na = win(t, t91-.2, tbo)
        n = counter(0, 91, prog(t, t91, 1.8))
        if na > .01:
            L = LBL(n, "n91", font("title", 300), PAL["coral"], None)
            L.draw(cv, fr, CX, 860, na, -2)
            show(cv, fr, T6c, t, t91+.2, tbo, CX, 1080, 1)
        for k in range(14):
            tk = t91 + k*.13
            if tk < t < tk + .5:
                u = prog(t, tk, .5); p = bezier((100 + (k % 3)*80, 1500), (300+k*30, 1100), (980, 560 + (k % 4)*90), u)
                draw_ball(cv, fr, p[0], p[1], .45, t*500)
        show_stamp(cv, fr, S6, t, tv(5.6), CX, 1300, -6, tbo)
    # 8 Ballons d'Or
    if t > tbo - .2:
        rays(cv, (CX, 1120), t, .8*prog(t, tbo, .6), 14, 900)
        for i, (x, y) in enumerate(BDO_POS):
            ti = tbo + .3 + i*.14
            if t < ti: continue
            u = ease_out_cubic(prog(t, ti, .3)); BALLON_OR.draw(cv, fr, x, y - 700*(1-u), .92)
        show(cv, fr, T6d, t, tbo+1.4, None, 580, 1330, -1)
        camera_flashes(cv, fr, "cf6", t-tbo-.2, 2.2, 16)
        show_stamp(cv, fr, S6b, t, tno, CX, 700, -5)
        confetti(cv, fr, "c6", t-tno, 60, 4)
    hl(cv, fr, H6a, t, .1, t12)
    hl(cv, fr, H6b, t, t12+.05, tbo)
    hl(cv, fr, H6c, t, tbo+.05)
    mascot(cv, fr, t, "happy" if t > tno else "surprised", hop=abs(math.sin(t*8))*35 if t > tno else 0)
    impact(cv, t, tv(5.6), 14); impact(cv, t, tno, 14)

# ------------------------------------------------------------------ SCÈNE 7 — l'argent, le départ
def s7(cv, fr, t, T):
    d = ImageDraw.Draw(cv)
    t_news = tv(2.08); t_num = tv(4.5); t_rec = tv(6.88); t_sec = tv(8.52); t_cut = tv(9.91); t_rip = tv(12.05); t_go = tv(12.96)
    bill_rain(cv, fr, t, 0, 2.2)
    hl(cv, fr, H7, t, .1, t_go)
    hl(cv, fr, H7b, t, tv(13.6))
    # le journal qui tourne
    nu = prog(t, t_news, .6); no = ease_in_cubic(prog(t, t_sec-.1, .5))
    if nu > 0 and no < 1:
        s = lerp(.08, .9, ease_out_cubic(nu)); rot = 720*(1-ease_out_cubic(nu))
        L = layer(760, 920, (380, 460)); NEWS.draw(L, fr, 380, 460, 1, 0, 1)
        dl = ImageDraw.Draw(L)
        if t > t_num - .1:
            dl.text((380, 380), f"{counter(0, 555237619, prog(t, t_num, 1.7))} €", font=font("title", 76), fill=PAL["red"], anchor="mm")
            dl.text((380, 460), "sur 4 saisons", font=font("hand", 48), fill=PAL["ink"], anchor="mm")
        blit(cv, L, CX - 900*no, 930, s, rot - 30*no, 1)
        show(cv, fr, T7a, t, t_news+.7, t_sec-.2, CX, 1400, -1.5)
        show(cv, fr, T7b, t, t_num+1.9, t_sec-.2, CX, 1510, 1)
        show_stamp(cv, fr, S7, t, t_rec, 760, 620, -12, t_sec-.2)
    # le Barça à sec : la tirelire vide
    pa = win(t, t_sec, t_cut-.1)
    if pa > .01:
        shake_x = 10*math.sin(t*40) if t_sec+.4 < t < t_sec+1.2 else 0
        draw_pig(cv, fr, 500+shake_x, 1000, pa)
        mt = t - (t_sec+.6)
        if mt > 0: moth(cv, 560 + 120*math.sin(mt*2), 850 - 160*mt, t, 1.2)
        show(cv, fr, T7c, t, t_sec+.3, t_cut-.1, CX, 1300, -1)
    # le contrat, -50 %, déchiré
    ca = win(t, t_cut, None)
    mx_, ms = 270, .95
    if t > t_cut - .2 and t < t_go:
        PL.draw(cv, fr, mx_ - 400*(1-ease_out_cubic(prog(t, t_cut-.2, .5))), 1480, ms, age=1, kit="barca", beard=True,
                mood="normal" if t < t_rip else "sad", t=t, look=(1, 0))
    if ca > .01 and t < t_rip:
        CONTRACT.draw(cv, fr, 720, 950, .9*ca, 3)
        if t > tv(10.9):
            pencil_line(d, [(640, 820), (820, 820)], prog(t, tv(10.9), .25), PAL["red"], 10, 2, 2)
            T7d.draw(cv, fr, 740, 700, pop_in(t, tv(11.1)), -8)
    if t >= t_rip:
        A, B, anc = contract_halves(); u = ease_in_cubic(prog(t, t_rip, .9))
        if u < 1:
            for P, sg in ((A, -1), (B, 1)):
                P.info["anchor"] = anc
                blit(cv, P, 720 + sg*(10+700*u), 950 + 500*u*u, .9, sg*-35*u, 1)
    # en larmes, direction Paris
    if t >= t_go - .1:
        u = ease_io(prog(t, t_go-.1, .6)); x = lerp(mx_, CX, u)
        ts = tv(13.9); su = prog(t, ts, .6)
        ea = win(t, tv(13.9), None, .6)
        if ea > .01: EIFFEL.draw(cv, fr, 830, 1480, .9*ea)
        if su <= 0:
            PL.draw(cv, fr, x, 1480, 1.0, age=1, kit="barca", beard=True, mood="sad", tears=t-t_go, t=t, look=(0, 1))
        elif su < 1:
            L = PL.render_layer(fr, 1.0, age=1, kit="barca" if su < .25 else "psg", beard=True, mood="sad" if su < .25 else "normal")
            blit_sxy(cv, L, CX, 1480, max(.04, abs(math.cos(su*math.pi*2))), 1.0)
        else:
            PL.draw(cv, fr, CX, 1480, 1.0, age=1, kit="psg", beard=True, mood="normal", t=t)
        show(cv, fr, T7e, t, tv(14.1), None, CX, 700, -2)
    mascot(cv, fr, t, "surprised" if t_num < t < t_sec else ("normal" if t < t_rip else "normal"))
    impact(cv, t, t_rec, 14); impact(cv, t, t_rip, 10)

# ------------------------------------------------------------------ SCÈNE 8 — la Coupe du monde
GOALS_2022 = [(1, 0, "23'"), (2, 0, "36'"), (2, 1, "80'"), (2, 2, "81'"), (3, 2, "108'"), (3, 3, "118'")]
PENS = [(True, True), (True, False), (True, False), (True, True)]   # (ARG, FRA) dans l'ordre des tirs
def s8(cv, fr, t, T):
    d = ImageDraw.Draw(cv)
    t_cdm = tv(1.52); t16 = tv(2.47); t_kick = tv(3.4); t_quit = tv(5.9); t_back = tv(7.02); t_qat = tv(8.05)
    t_fin = tv(9.91); t33 = tv(11.69); t_dbl = tv(12.33); t_tab = tv(13.28); t_enfin = tv(14.64)
    hl(cv, fr, H8, t, t_cdm, t_qat)
    hl(cv, fr, H8b, t, t_qat, t_enfin-.15)
    # le trophée manquant (silhouette)
    wo = ease_io(prog(t, t16-.1, .6)); wf = 1 - prog(t, t_qat, .4)
    if wf > 0:
        x, y, s = lerp(CX, 880, wo), lerp(980, 640, wo), lerp(1.4, .5, wo)
        WC_SIL.draw(cv, fr, x, y, s*pop_in(t, .1, .5), 0, wf)
        QMS[0].draw(cv, fr, x+140*s, y-160*s, s*pop_in(t, .5)*wf, 10)
    # 2016 : le penalty raté, il quitte la sélection… puis revient
    if t16 - .2 < t < t_qat + .3:
        ga = ease_out_cubic(prog(t, t16-.2, .5)); go = ease_in_cubic(prog(t, t_qat-.1, .4))
        draw_goal(cv, fr, lerp(1300, 800, ga) + 700*go, 1450, 360, 210, 0, 1, t)
        show(cv, fr, T8a, t, t16, t_quit, CX, 470, -1.5)
        kick = math.sin(prog(t, t_kick-.15, .3)*math.pi)
        if t < t_quit: px, al, mood = lerp(-200, 330, ga), 1, ("determined" if t < t_kick+.4 else "sad")
        elif t < t_back: px, al, mood = lerp(330, 560, prog(t, t_quit, 1)), 1-prog(t, t_quit+.3, .7), "sad"
        else: px, al, mood = lerp(1250, 420, ease_out_cubic(prog(t, t_back, .6))) - 900*go, 1, "determined"
        if al > .01:
            PL.draw(cv, fr, px, 1450, 1.0, age=1, kit="arg", beard=True, mood=mood, alpha=al, legs=(0, 45*kick),
                    arms=(15, 15) if t < t_back else (30, 30), t=t, look=(0, 1) if mood == "sad" else (1, 0))
        if t < t_kick: draw_ball(cv, fr, 400, 1415, .55, 0)
        elif t < t_kick + .7:
            u = prog(t, t_kick, .6); p = bezier((400, 1415), (700, 1000), (980, 560), ease_out_cubic(u))
            draw_ball(cv, fr, p[0], p[1], .55, t*700)
        show(cv, fr, T8b, t, t_quit, t_back, CX, 700, 1)
        show(cv, fr, T8c, t, t_back+.1, t_qat, CX, 700, -1)
    # Qatar 2022 : le tableau d'affichage
    if t > t_qat:
        sa = ease_out_back(prog(t, t_qat+.2, .5)); so = 0; sfade = 1 - prog(t, t_enfin-.15, .3)
        a, b, mn = 0, 0, ""
        for k, (ga_, gb_, m_) in enumerate(GOALS_2022):
            if t > t_fin + k*.24: a, b, mn = ga_, gb_, m_
        sy = lerp(720, 520, so); ss = lerp(1.0, .6, so)
        pulse = 1 + .05*math.sin(prog(t, t33, .4)*math.pi)
        if sfade > 0: draw_score(cv, fr, CX, sy, a, b, sa*ss*pulse, mn if t < t33 else "après prolongation", sfade)
        if t33 - .3 < t < t_enfin:
            show(cv, fr, T8d, t, t_dbl, t_enfin, CX, 980, -2)
            for k in range(2):
                if t > t_dbl + .2 + k*.2: draw_ball(cv, fr, 800 + k*70, 980, .42, 0)
        if t > t_tab - .1 and t < t_enfin:
            T8e.draw(cv, fr, CX, 1130, pop_in(t, t_tab), 1)
            for r, (lab, col) in enumerate((("ARG", 0), ("FRA", 1))):
                yy = 1250 + r*100
                d.text((250, yy), lab, font=font("mono", 52), fill=PAL["charcoal"], anchor="mm")
                for k, pen in enumerate(PENS):
                    tk = t_tab + .15 + (k*2 + r)*.12
                    if t > tk:
                        x = 380 + k*120
                        (pencil_check if pen[col] else pencil_cross)(d, x, yy, 1.2)
    # ENFIN : il soulève la Coupe
    if t > t_enfin - .1:
        u = ease_out_cubic(prog(t, t_enfin-.1, .5))
        rays(cv, (CX, 900), t, u, 16, 1200, (255, 220, 120)); confetti(cv, fr, "c8", t-t_enfin, 90, 5)
        lift = ease_out_back(prog(t, t_enfin+.1, .6))
        PL.draw(cv, fr, CX, 1500 + 300*(1-u), 1.0, age=1, kit="arg", beard=True, mood="cheer", arms=(172, 172), t=t)
        WC_TROPHY.draw(cv, fr, CX, 1500 + 300*(1-u) - 815 + 60*(1-lift), .62, 3*math.sin(t*3))
        show_stamp(cv, fr, S8, t, t_enfin, CX, 380, -6)
        camera_flashes(cv, fr, "cf8", t-t_enfin-.2, 2.0, 12)
    mascot(cv, fr, t, "happy" if t > t_enfin else ("surprised" if t_kick < t < t_quit else "normal"),
           hop=abs(math.sin(t*8))*40 if t > t_enfin else 0)
    impact(cv, t, t_enfin, 20); flashes(cv, t, t_enfin, .25, .8)

# ------------------------------------------------------------------ SCÈNE 9 — Miami, 2026, le plus grand
def s9(cv, fr, t, T):
    d = ImageDraw.Draw(cv)
    t_mia = tv(1.92); t_deal = tv(3.8); t_wc = tv(6.59); t_rec = tv(8.6); t_big = tv(11.32); t_sub = tv(13.53)
    T9y.draw(cv, fr, CX, 330, win(t, .1, t_mia), -2)
    hl(cv, fr, H9, t, t_mia, t_wc)
    hl(cv, fr, H9b, t, t_wc+.05, t_big)
    hl(cv, fr, H9c, t, t_big+1.2)
    # palmiers, soleil
    pa = ease_out_cubic(prog(t, .2, .7)); po = ease_in_cubic(prog(t, t_wc-.3, .5))
    if pa > 0 and po < 1:
        draw_palm(cv, fr, lerp(-200, 120, pa) - 400*po, 1500, 1.1, t, 1)
        draw_palm(cv, fr, lerp(1300, 960, pa) + 400*po, 1500, .9, t, -1)
    # Messi : PSG -> Miami, puis Argentine pour 2026
    su = prog(t, t_mia+.1, .6)
    x = CX if t < t_deal else lerp(CX, 330, ease_io(prog(t, t_deal, .6)))
    s = 1.0 if t < t_deal else lerp(1.0, .8, ease_io(prog(t, t_deal, .6)))
    if t < t_big - .3:
        if t > t_wc: x, s = lerp(330, 870, ease_io(prog(t, t_wc, .5))), lerp(.8, .55, ease_io(prog(t, t_wc, .5)))
        kit = "psg" if su < .25 else "miami"
        if t > t_wc + .2: kit = "arg"
        if 0 < su < 1:
            L = PL.render_layer(fr, 1.0, age=1, kit=kit, beard=True, mood="happy")
            blit_sxy(cv, L, x, 1480, max(.04, abs(math.cos(su*math.pi*2))), 1.0)
        else:
            PL.draw(cv, fr, x, 1480, s, age=1, kit=kit, beard=True, mood="happy", t=t,
                    arms=(30, 150) if t_wc+.5 < t else (8, 8), alpha=1-prog(t, t_big-.6, .3))
    # le contrat unique : abonnements + ventes
    for i, (obj, lab) in enumerate(((TV, T9a), (BAG, T9b))):
        a = win(t, t_deal + .4 + i*.8, t_wc - .2)
        if a > .01:
            y = 720 + i*420
            obj.draw(cv, fr, 700, y, a, (-3, 3)[i]); lab.draw(cv, fr, 700, y + 170, a, (1, -1)[i])
            for k in range(3):
                pp = prog(t, t_deal + .9 + i*.8 + k*.15, .6)
                if 0 < pp < 1: particles(cv, fr, f"coin{i}{k}", (700, y), pp, 8, 200, [PAL["gold"], PAL["mustard"]])
    # meilleur buteur de l'histoire du Mondial
    ba = win(t, t_wc+.2, t_big-.8)
    if ba > .01:
        BOARD.draw(cv, fr, 560, 850, ba, -1)
        ka = pop_in(t, t_wc+.8)
        if ka > 0:
            T9d.draw(cv, fr, 560, 1010, ka*ba, 0)
            if t > t_rec + .3: pencil_line(d, [(330, 1012), (790, 1008)], prog(t, t_rec+.3, .3), PAL["red"], 6, 4, 1)
        ra = ease_out_back(prog(t, t_rec, .5))
        if ra > 0: T9c.draw(cv, fr, lerp(1400, 560, clamp(ra)), 850, ba, -2)
        if t > t_rec + .2: particles(cv, fr, "rec9", (560, 850), prog(t, t_rec+.2, .8), 26, 380, [PAL["gold"], PAL["mustard"], PAL["cream"]])
    # le gamin trop petit… est devenu le plus grand
    if t > t_big - .3:
        u = ease_out_cubic(prog(t, t_big-.3, .5)); g = ease_io(prog(t, t_big+.4, 1.4))
        fin = ease_io(prog(t, t_sub-.2, .6))          # la toise s'en va, il se recentre pour l'appel à s'abonner
        rays(cv, (560, 900), t, g, 14, 1000)
        TOISE.draw(cv, fr, lerp(-120, 250, u) - 500*fin, FLOOR)
        px, ps = lerp(560, CX, fin), lerp(1.3, .95, fin)
        if g <= 0: PL.draw(cv, fr, px, FLOOR, 1.3, age=0, kit="newells", mood="normal", t=t)
        elif g < 1:   # il tourne sur lui-même en grandissant : Newell's -> Argentine
            L = PL.render_layer(fr, 1.3, age=g, kit="newells" if g < .25 else "arg", beard=True, mood="happy")
            blit_sxy(cv, L, px, FLOOR, max(.04, abs(math.cos(g*math.pi*2))), 1.0)
        else:
            up = prog(t, t_big+1.6, .5)
            PL.draw(cv, fr, px, FLOOR, ps, age=1, kit="arg", beard=True, mood="happy" if fin < 1 else "cheer",
                    t=t, arms=(lerp(8, 150, up), lerp(8, 150, up)))
        top = FLOOR - lerp(1.27, 1.70, g)*PX_M
        if fin < 1: pencil_line(d, [(300-500*fin, top), (720-500*fin, top)], u, PAL["red"], 6, 3, 1)
        confetti(cv, fr, "c9", t-t_big-1.2, 60, 5)
    T9e.draw(cv, fr, CX, 540, win(t, t_sub+.2), -2)
    T9f.draw(cv, fr, CX, 660, win(t, t_sub+.9), 1.5)
    mascot(cv, fr, t, "happy" if t > t_big else "normal", hop=abs(math.sin(t*7))*40 if t > t_sub else 0,
           look=(1, -1))
    flashes(cv, t, t_big+1.2, .2, .6); impact(cv, t, t_big+1.2, 14)

# ------------------------------------------------------------------ scènes + bruitages
def SC(name, n, fn, sfx, **kw):
    return Scene(name, VOICE_TXT[n-1], fn, sfx, pad_in=PAD, pad_out=kw.pop("pad_out", .45), **kw)
VOICE_TXT = [
    "Trop petit. Trop fragile. Trop cher à soigner. Voilà ce qu'on disait de lui en Argentine. Aujourd'hui, c'est le joueur le plus titré de l'histoire du foot. Voici l'histoire folle de Lionel Messi.",
    "Rosario, Argentine, mille neuf cent quatre-vingt-sept. C'est sa grand-mère, Celia, qui l'emmène au foot, et qui pousse l'entraîneur à faire jouer ce gamin minuscule. Aujourd'hui encore, à chaque but, il pointe le ciel. Pour elle.",
    "Mais à dix ans, il ne mesure qu'un mètre vingt-sept. Diagnostic : déficit d'hormone de croissance. Le traitement ? Une piqûre chaque soir, dans les jambes. Près de mille dollars par mois. Sa famille ne peut pas suivre.",
    "À treize ans, il traverse l'océan pour un essai à Barcelone. Le directeur sportif est bluffé, mais le club hésite. Alors, pour ne pas le perdre, il signe un accord… sur une serviette en papier ! Le Barça paiera son traitement. Et cette serviette ? Vendue aux enchères près d'un million de dollars.",
    "Et le traitement marche : il grandit jusqu'à un mètre soixante-dix. À dix-sept ans, il débute chez les pros avec le numéro trente. Son premier but ? Sur une passe lobée de Ronaldinho. Puis il hérite du numéro dix… et tout s'accélère.",
    "Deux mille neuf : six trophées sur six, en une seule année. Deux mille douze : quatre-vingt-onze buts en douze mois, record du monde. Et au total, huit Ballons d'Or. Personne n'en a autant.",
    "Côté argent aussi, c'est hors norme. En deux mille vingt et un, la presse révèle son contrat : cinq cent cinquante-cinq millions d'euros sur quatre ans. Le plus gros de l'histoire du sport ! Mais le Barça est à sec. Messi accepte de baisser son salaire de moitié… ça ne suffit pas. Il part en larmes, direction Paris.",
    "Il ne lui manque qu'un trophée : la Coupe du monde. En deux mille seize, il rate un penalty en finale de Copa América, et quitte la sélection… avant de revenir. Deux mille vingt-deux, au Qatar : finale de folie contre la France. Trois partout, doublé de Messi, victoire aux tirs au but. Enfin !",
    "Deux ans plus tard, il file à Miami, en rose, avec un contrat unique : une part des abonnements Apple et des ventes Adidas. Et au Mondial deux mille vingt-six, il devient le meilleur buteur de toute l'histoire de la Coupe du monde. Le gamin trop petit est devenu le plus grand. Abonne-toi pour la prochaine légende !",
]
SCENES = [
    SC("accroche", 1, s1, [(tv(.15)-.02, "stamp"), (tv(.15), "boom", .8), (tv(.81)-.02, "stamp"), (tv(1.57)-.02, "stamp"), (tv(1.57), "boom", .6),
                           (tv(2.7), "heart", .7), (tv(4.59)-.35, "riser", .8), (tv(4.59), "whoosh"), (tv(4.59)+.1, "crowd_long", .7),
                           (tv(4.59)+.4, "sparkle"), (tv(4.59)+.6, "pop"), (tv(4.59)+.8, "pop"), (tv(4.59)+1.0, "pop2"), (tv(7.9), "stamp", .8)]),
    SC("rosario", 2, s2, [(.15, "pop"), (tv(1.0), "pop"), (tv(3.2), "whoosh", .5), (tv(3.4), "pop"), (tv(5.9), "whistle"), (tv(5.8), "pop"),
                          (tv(7.3), "pop"), (tv(8.52)-.1, "kick"), (tv(8.52)+.4, "crowd", .6), (tv(9.7), "sparkle"), (tv(11.1), "pop2")], trans="tear_v"),
    SC("diagnostic", 3, s3, [(.15, "pop"), (tv(.9), "scribble"), (tv(1.3), "pop"), (tv(2.74), "swish"), (tv(3.65), "stamp", .6),
                             (tv(5.31), "whoosh", .4), (tv(6.04), "pop"), (tv(7.35), "pop2"), (tv(7.5), "pop"), (tv(8.06), "swish"),
                             (tv(9.0), "cash"), (tv(9.6)-.02, "stamp"), (tv(9.6), "heart", .8)], trans="tear_d"),
    SC("serviette", 4, s4, [(.15, "pop"), (tv(.3), "plane"), (tv(3.0), "whoosh", .5), (tv(3.6), "pop2"), (tv(4.77), "pop"), (tv(4.92), "pop"),
                            (tv(5.07), "pop"), (tv(6.02), "paper"), (tv(6.02), "whoosh", .5), (tv(6.5), "scribble"), (tv(8.0), "scribble"),
                            (tv(8.53), "stamp", .8), (tv(10.09), "swish"), (tv(10.5), "rip"), (tv(10.8), "sparkle", .6), (tv(11.63), "whoosh", .4),
                            (tv(12.9), "gavel"), (tv(14.3), "cash")], trans="tear_h"),
    SC("croissance", 5, s5, [(.1, "pop"), (tv(1.2), "riser", .7), (tv(2.9), "sparkle"), (tv(3.62), "whoosh", .5), (tv(3.9), "pop"),
                             (tv(6.3), "whistle", .6), (tv(7.23), "kick", .5), (tv(8.35)-.05, "kick"), (tv(8.7), "crowd_long"),
                             (tv(9.45), "swish"), (tv(9.7), "sparkle"), (tv(10.3), "whoosh")]),
    SC("records", 6, s6, [(.1, "pop")] + [(tv(1.07)+i*.2, "pop") for i in range(6)] + [(tv(2.3), "ding"), (tv(3.43), "whoosh", .5)] +
                         [(tv(4.29)+k*.13, "tick") for k in range(14)] + [(tv(5.6), "stamp"), (tv(6.62), "whoosh", .5)] +
                         [(tv(6.62)+i*.14+.3, "thud", .6) for i in range(8)] + [(tv(6.9), "flash"), (tv(7.8), "flash", .7), (tv(8.54), "stamp"),
                         (tv(8.6), "crowd_long", .6)]),
    SC("argent", 7, s7, [(.1, "cash"), (.4, "pop"), (tv(2.08), "whoosh", .6), (tv(2.6), "thud"), (tv(6.3), "cash"), (tv(6.88), "stamp"),
                         (tv(8.52), "swish"), (tv(9.0), "clink"), (tv(9.91), "paper"), (tv(10.9), "scribble"), (tv(12.05), "rip"),
                         (tv(12.96), "groan", .35), (tv(13.9), "whoosh"), (tv(14.1), "pop")], trans="tear_v"),
    SC("coupe_du_monde", 8, s8, [(.1, "pop"), (tv(1.52), "pop2"), (tv(2.47), "whistle", .6), (tv(3.4)-.05, "kick"), (tv(3.8), "groan"),
                                 (tv(5.9), "swish"), (tv(7.02), "whoosh", .5), (tv(8.05), "pop"), (tv(8.3), "whistle", .6)] +
                                [(tv(9.91)+k*.24, "kick", .6) for k in range(6)] + [(tv(10.2), "crowd", .5), (tv(11.69), "boom", .5),
                                 (tv(12.5), "pop"), (tv(13.1), "heart")] + [(tv(13.28)+.15+k*.12, "tick") for k in range(8)] +
                                [(tv(14.64)-.02, "stamp"), (tv(14.64), "boom", .8), (tv(14.64), "crowd_long", 1.0), (tv(14.9), "flash", .6),
                                 (tv(15.2), "sparkle")], trans="tear_d", pad_out=1.4),
    SC("miami", 9, s9, [(.1, "pop"), (tv(1.92), "whoosh"), (tv(2.1), "sparkle", .6), (tv(4.2), "pop"), (tv(5.0), "pop"), (tv(4.8), "cash"),
                        (tv(5.6), "cash"), (tv(6.59), "whoosh", .5), (tv(6.9), "pop"), (tv(8.6), "swish"), (tv(8.9), "ding"), (tv(9.0), "crowd", .5),
                        (tv(11.32), "riser", .7), (tv(12.5), "stamp"), (tv(12.5), "crowd_long", .7), (tv(13.53), "pop2"), (tv(14.3), "pop")],
       trans="tear_h", pad_out=1.8),
]

# ------------------------------------------------------------------ couverture
def cover(path):
    cv = background(0, TITLE); d = ImageDraw.Draw(cv)
    rays(cv, (700, 1000), 0.3, 1.0, 16, 1500)
    Label("TROP PETIT", "c1", font("title", 170), PAL["cream"], PAL["coral"], maxw=1000, padx=40, pady=10, rough=5).draw(cv, 0, CX, 290, 1, -3)
    Label("POUR LE FOOT ?", "c2", font("title", 118), PAL["ink"], PAL["mustard"], maxw=1000, padx=40, pady=10, rough=5).draw(cv, 0, CX, 475, 1, 2)
    floor = 1560; TOISE.draw(cv, 0, 150, floor)
    PL.draw(cv, 0, 330, floor, 1.3, age=0, kit="newells", mood="sad", t=1)
    y127 = floor - 1.27*PX_M
    pencil_line(d, [(190, y127), (470, y127)], 1, PAL["red"], 7, 3, 1)
    Label("1,27 m", "c5", font("title", 64), PAL["cream"], PAL["red"], padx=20, pady=6).draw(cv, 0, 330, y127-80, 1, -5)
    PL.draw(cv, 0, 750, floor, 1.1, age=1, kit="arg", beard=True, mood="cheer", arms=(172, 172), t=1)
    WC_TROPHY.draw(cv, 0, 750, floor - 1.1*(512-14) - 205 - 82, .5, 3)
    Label("L'HISTOIRE FOLLE DE MESSI", "c4", font("title", 66), PAL["cream"], PAL["teal"], padx=30, pady=12).draw(cv, 0, CX, 1680, 1, 1)
    M.draw(cv, 0, 960, 1480, look=(-1, -1), mood="surprised", scale=.6, t=1.0)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

# ------------------------------------------------------------------ planches de contrôle
def stills(out, fracs=(.08, .22, .38, .52, .66, .8, .95), only=None):
    Ts = scene_timing(SCENES, VOICE)
    os.makedirs(out, exist_ok=True); sheets = []
    for i, sc in enumerate(SCENES):
        if only and (i+1) not in only: continue
        ims = []
        for k, fr_ in enumerate(fracs):
            t = fr_*sc.T; f = int(t*FPS)
            cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T); finish(cv, TITLE)
            ims.append(cv.resize((360, 640)))
        sheet = Image.new("RGB", (360*len(ims), 690), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            sheet.paste(im, (k*360, 50)); dd.text((k*360+10, 8), f"S{i+1} t={fracs[k]*sc.T:.1f}/{sc.T:.1f}", font=font("mono", 26), fill=(230, 230, 230))
        p = os.path.join(out, f"sheet_s{i+1}.jpg"); sheet.save(p, quality=82); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", "messi")
    os.makedirs(out, exist_ok=True)
    if "--cover" in args:
        print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        only = [int(x) for x in args[args.index("--stills")+1].split(",")] if len(args) > args.index("--stills")+1 and not args[args.index("--stills")+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/messi_stills"), only=only)); sys.exit()
    if "--frame" in args:   # --frame SCENE TEMPS
        i = int(args[args.index("--frame")+1]); t = float(args[args.index("--frame")+2])
        scene_timing(SCENES, VOICE); sc = SCENES[i-1]
        render_still(sc.draw_fn, os.path.join(os.environ.get("STILLS_DIR", "/tmp/messi_stills"), f"frame_s{i}_{t:.2f}.jpg"), t, sc.T, int(t*FPS), TITLE); sys.exit()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=7.0, lufs=-14.0, crf=25))
