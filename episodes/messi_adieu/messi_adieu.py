"""Hommage « Légendes du foot » : Lionel Messi dit adieu à l'Argentine (dernier match le 6 octobre 2026), ~45 s, version « ultra détaillée ».
Création originale (plans, textes, montage) : gros plans papier détaillés (engine/portrait.py) aux trois âges (2005, 2016, 2026),
stades de nuit avec foule détaillée, profondeur de champ (fond flou), lumière latérale. Aucun logo de marque ni écusson.
Déroulé : 21 ans en 3 visages → 2005 rouge après 47 s → 2006 1er but en CM → 3 finales perdues, penalty raté, retraite… retour
→ 2021 Copa, 2022 champion du monde → 2026 finale perdue, « tout donné pour ce maillot » → 6 octobre, Monumental → merci Leo.

  python3 episodes/messi_adieu/messi_adieu.py output/messi_adieu --stills [2,3]
  python3 episodes/messi_adieu/messi_adieu.py output/messi_adieu --cover
  python3 episodes/messi_adieu/messi_adieu.py output/messi_adieu
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "liverpool"))
from story import *
from portrait import Portrait, HAIR_P, BEARD_P
from quiz import like_button, sub_button
_prov = os.environ.pop("LEGENDES_PROVISOIRE", None)   # liverpool.py lit cette variable pour ses propres voix
from liverpool import score2, trophy_lift
if _prov: os.environ["LEGENDES_PROVISOIRE"] = _prov
import engine

TITLE = "~/légendes $ ./merci_leo"
SLUG = "messi_adieu"
SRC = os.environ.get("LEGENDES_PROVISOIRE") or HERE
VOICE = [os.path.join(SRC, "voix", f"scene_{i}.mp3") for i in range(1, 9)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
PAD = 0.12
WS, TEXTS = load_words(os.path.join(SRC, "alignement.json"))
def w(i, word, n=1, end=False):
    return PAD + WS[i-1](word, n, end)

CIEL = (116, 174, 226); BLANC = (250, 250, 246); GOLD = (236, 186, 48); NOIR = (30, 28, 28); RED = (206, 30, 44)
NUIT = (12, 18, 40); INK = PAL["ink"]
SKINS = [(236, 196, 160), (220, 176, 136), (196, 146, 108), (160, 112, 80), (118, 82, 60)]
HAIRS = [(40, 30, 24), (80, 56, 36), (24, 22, 20), (140, 100, 60), (60, 44, 34)]

# ------------------------------------------------------------------ personnages
YOUNG = Portrait("leo05", style="young", armband=False)
MID = Portrait("leo16", style="mid")
ADULT = Portrait("leo22", style="adult", grey=.06)
OLD = Portrait("leo26", style="adult", grey=.3)
PLY = Player("leoY", hair=HAIR_P, hair_style="shaggy")                 # 2005-2006
PLA = Player("leoA", hair=HAIR_P, beard_col=BEARD_P)                    # 2016-2026 (avec barbe)
REF = Player("ref05", hair=(30, 28, 26), skin=(226, 180, 146), hair_style="bald")
GK = Player("gk16", hair=(26, 22, 20), skin=(196, 146, 108))
TEAM = [Player(f"arg{k}", hair=HAIRS[k], skin=SKINS[(k*2) % 5]) for k in range(5)]
ESP = [Player(f"esp{k}", hair=HAIRS[(k+2) % 5], skin=SKINS[(k+1) % 5]) for k in range(2)]
BAND = Paper(rect_pts(46, 26), BLANC, "capband", rough=1)

def leo(cv, fr, pl, x, y, s, armband=True, **kw):
    """Joueur en pied + brassard de capitaine sur le bras gauche."""
    arms = kw.get("arms", (8, 8))
    pl.draw(cv, fr, x, y, s, **kw)
    if armband:
        r = -arms[0]; a = math.radians(r)
        sx, sy = x - SHOULDER_DX*s*.93, y + (NECK_Y + 14)*s
        BAND.draw(cv, fr, sx + 70*s*math.sin(a), sy + 70*s*math.cos(a), s, r, 1, .6)

# ------------------------------------------------------------------ stades de nuit (foule détaillée, mis en cache, flou = profondeur de champ)
BG = {
    "arg": dict(pal=[CIEL, BLANC, CIEL, BLANC, (40, 60, 120), GOLD], horizon=1240, flags=7),
    "bud": dict(pal=[RED, BLANC, (30, 130, 70), RED, (60, 60, 70)], horizon=1260, flags=0),
    "wc06": dict(pal=[CIEL, BLANC, (250, 214, 40), (40, 60, 120), RED, BLANC], horizon=1160, flags=4),
    "fin16": dict(pal=[CIEL, BLANC, RED, (40, 50, 110), BLANC], horizon=1250, flags=3),
    "fin26": dict(pal=[RED, (250, 200, 30), CIEL, BLANC, RED, (40, 50, 110)], horizon=1240, flags=2),
    "mon": dict(pal=[CIEL, BLANC, CIEL, BLANC, CIEL, GOLD], horizon=1300, flags=12, banner="GRACIAS LEO"),
}
_bgc = {}
def _flag(d, fx, fy, fw):
    fh = fw*.62
    for b, c in enumerate((CIEL, BLANC, CIEL)):
        d.rectangle([fx - fw/2, fy - fh/2 + b*fh/3, fx + fw/2, fy - fh/2 + (b+1)*fh/3], fill=c)
    d.ellipse([fx - fh*.11, fy - fh*.11, fx + fh*.11, fy + fh*.11], fill=GOLD)
    d.line([(fx - fw/2, fy - fh/2), (fx - fw/2, fy + fh*1.3)], fill=(90, 80, 70), width=4)

def crowd_bg(key, blur=0):
    if (key, blur) in _bgc: return _bgc[(key, blur)]
    if (key, 0) not in _bgc:
        c = BG[key]; hz = c["horizon"]; rnd = random.Random(key)
        im = Image.new("RGB", (W, H), NUIT); d = ImageDraw.Draw(im)
        for y in range(0, 520, 4):
            u = y/520; d.rectangle([0, y, W, y + 4], fill=tuple(int(lerp(a*.55, a*1.4, u)) for a in NUIT))
        glow = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(glow)
        for fx in (140, 940): gd.ellipse([fx - 210, 250 - 190, fx + 210, 250 + 190], fill=170)
        glow = glow.filter(ImageFilter.GaussianBlur(80))
        im = Image.composite(Image.new("RGB", (W, H), (255, 244, 210)), im, glow.point(lambda v: int(v*.75))); d = ImageDraw.Draw(im)
        d.polygon([(0, 420), (W, 400), (W, 470), (0, 490)], fill=(26, 26, 36))
        for fx in (140, 940):
            d.rectangle([fx - 70, 212, fx + 70, 292], fill=(56, 56, 66))
            for i in range(4):
                for j in range(2): d.ellipse([fx - 60 + i*34, 222 + j*36, fx - 36 + i*34, 246 + j*36], fill=(255, 252, 236))
            d.line([(fx, 292), (fx, 420)], fill=(56, 56, 66), width=10)
        y = 490
        while y < hz - 60:
            sz = lerp(12, 30, (y - 490)/max(1, hz - 550)); step = sz*1.85; x = -rnd.uniform(0, step)
            while x < W + step:
                col = rnd.choice(c["pal"]); sk = rnd.choice(SKINS); jy = rnd.uniform(-sz*.2, sz*.2)
                d.rounded_rectangle([x - sz*.8, y + jy, x + sz*.8, y + jy + sz*1.7], radius=max(1, int(sz*.3)), fill=col)
                if col == CIEL and rnd.random() < .5:   # rayures des maillots
                    d.rectangle([x - sz*.2, y + jy, x + sz*.2, y + jy + sz*1.7], fill=BLANC)
                d.ellipse([x - sz*.48, y + jy - sz*.95, x + sz*.48, y + jy + sz*.05], fill=sk)
                if rnd.random() < .6: d.chord([x - sz*.5, y + jy - sz*1.0, x + sz*.5, y + jy - sz*.25], 180, 360, fill=rnd.choice(HAIRS))
                if rnd.random() < .08: d.line([(x + sz*.6, y + jy + sz*.3), (x + sz*1.1, y + jy - sz*1.3)], fill=sk, width=max(2, int(sz*.32)))
                x += step*rnd.uniform(.9, 1.12)
            y += sz*1.75
        for _ in range(c["flags"]): _flag(d, rnd.uniform(70, W - 70), rnd.uniform(560, hz - 170), rnd.uniform(90, 150))
        if c.get("banner"):
            by = hz - 260
            d.polygon([(70, by - 50), (W - 70, by - 64), (W - 60, by + 56), (80, by + 66)], fill=BLANC)
            d.rectangle([70, by - 50, W - 70, by - 28], fill=CIEL); d.rectangle([80, by + 40, W - 60, by + 62], fill=CIEL)
            d.text((CX, by + 4), c["banner"], font=font("title", 104), fill=(40, 70, 140), anchor="mm")
        d.rectangle([0, hz - 46, W, hz - 4], fill=(22, 26, 40))
        for k in range(10):
            y0 = hz + k*(H - hz)/10
            d.rectangle([0, y0, W, y0 + (H - hz)/10 + 1], fill=(44, 112, 62) if k % 2 == 0 else (40, 100, 56))
        d.line([(0, hz), (W, hz)], fill=(232, 236, 226), width=6)
        _bgc[(key, 0)] = im
    if blur: _bgc[(key, blur)] = _bgc[(key, 0)].filter(ImageFilter.GaussianBlur(blur))
    return _bgc[(key, blur)]

def bg(cv, key, t, blur=0, lights=True, dim=0.0):
    cv.paste(crowd_bg(key, blur), (0, 0))
    if lights:   # flashs de téléphones qui scintillent dans la tribune
        d = ImageDraw.Draw(cv); rnd = random.Random(key + "ph"); hz = BG[key]["horizon"]
        for i in range(70):
            x, y, ph = rnd.uniform(20, W - 20), rnd.uniform(520, hz - 80), rnd.uniform(0, 6.3)
            v = .5 + .5*math.sin(t*5 + ph)
            if v > .55:
                r = (2 + 3*v)*(1 + blur/10); d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 252, 230))
    if dim > 0: tint(cv, dim, (8, 10, 24))

def bokeh(cv, t, a=1.0, cols=(CIEL, BLANC, GOLD), n=14, seed=1):
    """Petites taches de lumière floues qui dérivent devant (gros plans)."""
    L = Image.new("RGBA", cv.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(L); rnd = random.Random(seed)
    for i in range(n):
        x = (rnd.uniform(0, W) + t*rnd.uniform(-20, 20)) % W; y = rnd.uniform(200, 1700) - t*rnd.uniform(5, 25)
        r = rnd.uniform(18, 46); c = rnd.choice(cols)
        dl.ellipse([x - r, y - r, x + r, y + r], fill=(*c, int(70*a)))
    cv.paste(L, (0, 0), L.filter(ImageFilter.GaussianBlur(6)))

def fireworks(cv, key, t, cols=(CIEL, BLANC, GOLD), n=5, area=(80, 260, 1000, 760)):
    d = ImageDraw.Draw(cv); rnd = random.Random(key)
    for i in range(n):
        t0 = i*.45 + rnd.uniform(0, .3); u = (t - t0) % 2.2
        if u > 1.1: continue
        x, y = rnd.uniform(area[0], area[2]), rnd.uniform(area[1], area[3]); c = rnd.choice(cols); R = 150*ease_out_cubic(u/1.1)
        for k in range(14):
            an = k*math.pi*2/14; x1, y1 = x + R*math.cos(an), y + R*math.sin(an) + 40*u*u
            d.line([(x + .7*R*math.cos(an), y + .7*R*math.sin(an) + 30*u*u), (x1, y1)], fill=c, width=4)
            d.ellipse([x1 - 5, y1 - 5, x1 + 5, y1 + 5], fill=BLANC)

# ------------------------------------------------------------------ labels
K1a = STAMP("21 ANS", "mk1a", CIEL, 130, NOIR); K1b = KW("+ DE 200 MATCHS", "mk1b", BLANC, NOIR, 92)
K2a = KW("2005", "mk2a", INK, size=170); T2a = TAG("1er match · Hongrie - Argentine", "mt2a", PAL["paper"], size=54)
K2b = STAMP("CARTON ROUGE !", "mk2b", RED, 104); T2c = KW("IL SORT EN LARMES", "mt2c", PAL["paper"], NOIR, 84)
SUB = Paper(rect_pts(250, 150), (30, 30, 34), "subboard", rough=1.4).add(lambda d, a: [
    d.rectangle([a[0] - 112, a[1] - 62, a[0] + 112, a[1] + 62], fill=(14, 14, 16)),
    d.polygon([(a[0] - 70, a[1] + 20), (a[0] - 40, a[1] - 30), (a[0] - 10, a[1] + 20)], fill=(60, 220, 90)),
    d.text((a[0] + 46, a[1] - 4), "IN", font=font("title", 70), fill=(60, 220, 90), anchor="mm")])
CARD = Paper(rect_pts(96, 136), (226, 30, 40), "redcard", rough=1.2)
K3a = KW("2006", "mk3a", INK, size=170); K3b = STAMP("18 ANS", "mk3b", CIEL, 120, NOIR); T3a = TAG("1er but en Coupe du monde", "mt3a", GOLD, size=60)
K4a = KW("3 FINALES PERDUES", "mk4a", INK, size=100); PERDUE = STAMP("PERDUE", "mk4p", RED, 70)
K4b = KW("2016", "mk4b", INK, size=170); K4c = STAMP("RATÉ", "mk4c", RED, 150)
K4d = STAMP("IL QUITTE LA SÉLECTION", "mk4d", RED, 84); T4e = TAG("… avant de revenir !", "mt4e", GOLD, size=64)
def _ticket(year, comp, key):
    def dec(d, a):
        ax, ay = a
        for yy in range(int(ay - 80), int(ay + 80), 16): d.ellipse([ax - 228, yy, ax - 220, yy + 8], fill=(150, 140, 120))
        d.text((ax + 30, ay - 34), f"FINALE {year}", font=font("title", 66), fill=NOIR, anchor="mm")
        d.text((ax + 30, ay + 40), comp, font=font("hand", 46), fill=(70, 70, 80), anchor="mm")
    return Paper(rect_pts(500, 180), (244, 236, 214), key, rough=2, hatch=True).add(dec)
TICKETS = [_ticket(2014, "Coupe du monde", "tk14"), _ticket(2015, "Copa América", "tk15"), _ticket(2016, "Copa América", "tk16")]
K5a = KW("2021", "mk5a", INK, size=170); K5b = STAMP("COPA AMÉRICA", "mk5b", CIEL, 110, NOIR)
K5c = KW("2022 · QATAR", "mk5c", INK, size=130); K5d = STAMP("CHAMPION DU MONDE !", "mk5d", GOLD, 96, NOIR)
K6a = KW("2026", "mk6a", INK, size=170); T6a = TAG("dernière finale", "mt6a", PAL["paper"], size=60)
NOTIF = Label("août 2026 · Messi annonce sa\nretraite internationale", "mnotif", font("hand", 50), NOIR, BLANC, maxw=900, padx=36, pady=20, rough=2)
K6b = KW("IL A TOUJOURS TOUT DONNÉ", "mk6b", BLANC, NOIR, 66); K6c = KW("POUR CE MAILLOT", "mk6c", CIEL, NOIR, 96)
K7a = KW("6 OCTOBRE 2026", "mk7a", INK, size=110); T7a = TAG("Monumental · Buenos Aires", "mt7a", PAL["paper"], size=58)
K7b = STAMP("DERNIER MATCH", "mk7b", CIEL, 110, NOIR)
T8a = TAG("Ton plus beau souvenir de Messi ?", "mt8a", GOLD, size=62)
K8b = KW("TON PLUS BEAU SOUVENIR ?", "mk8b", BLANC, NOIR, 76); K8c = KW("COMMENTE !", "mk8c", RED, size=100)

# ------------------------------------------------------------------ SCÈNE 1 — 21 ans en trois visages… adieu
def s1a(cv, fr, t):
    bg(cv, "arg", t, blur=10, dim=.25)
    tL = w(1, "Lionel") - .1; u = clamp(t/tL)
    k = 0 if u < .34 else (1 if u < .68 else 2)
    P, mood = ((YOUNG, "neutral"), (MID, "determined"), (OLD, "emotional"))[k]
    P.draw(cv, fr, CX, 900, 1.25 + .04*u, mood=mood, t=t, tilt=(-2, 1, -1)[k])
    for b in (.34, .68): flashes(cv, t, b*tL, .12, .7)
    year = int(round(lerp(2005, 2026, ease_io(u))))
    LBL(str(year), "myear", font("title", 150), NOIR, PAL["paper"], padx=30, pady=6, rough=3).draw(cv, fr, CX, 1460, 1, -2)
    show_stamp(cv, fr, K1a, t, w(1, "Vingt") - .05, CX, 330, -4)
    kw(cv, fr, K1b, t, w(1, "Plus") - .05, None, CX, 505, 3)

def s1b(cv, fr, t):
    bg(cv, "arg", t, blur=12, dim=.15)
    tl = w(1, "Lionel") - .1
    bokeh(cv, t, .9)
    OLD.draw(cv, fr, CX, 960, 1.3 + .05*prog(t, tl, 2.5), mood="emotional", t=t, tears=max(0, t - w(1, "adieu")), tilt=-1.5)
    ransom_line(cv, "MESSI DIT ADIEU", 330, 112, seed=3, fr=fr, scale=pop_in(t, w(1, "Messi") - .1, .3))
    ransom_line(cv, "À L'ARGENTINE", 480, 100, seed=5, fr=fr, scale=pop_in(t, w(1, "l'Argentine") - .1, .3))

def s1(cv, fr, t, T):
    shots(cv, fr, t, [(0, s1a), (w(1, "Lionel") - .1, s1b)], d=.24)
    impact(cv, t, w(1, "Vingt"), 14); impact(cv, t, w(1, "Plus"), 10); punch(cv, t, w(1, "Lionel") - .1, 1.06); drift(cv, t, T, .04)

# ------------------------------------------------------------------ SCÈNE 2 — 2005 : 1er match, rouge après 47 secondes, larmes
def s2a(cv, fr, t):
    bg(cv, "bud", t, blur=3)
    kw(cv, fr, K2a, t, .03, None, CX, 330, -3)
    show(cv, fr, T2a, t, w(2, "premier") - .05, None, CX, 490, 2)
    leo(cv, fr, PLY, 360, 1790, .95, armband=False, age=1, kit="arg", mood="determined", t=t, kid_hair=False)
    REF.draw(cv, fr, 760, 1790, .9, age=1, kit="ref", arms=(8, 150), t=t)
    SUB.draw(cv, fr, 905, 1790 - 870*.9, .95*pop_in(t, .35, .3), 4)

def s2b(cv, fr, t):
    bg(cv, "bud", t, blur=2)
    te, tr = w(2, "entre"), w(2, "rouge")
    run = prog(t, te - .2, .9); x = lerp(160, 420, ease_out_cubic(run)); ph = math.sin(t*16)
    leo(cv, fr, PLY, x, 1790, .95, armband=False, age=1, kit="arg", mood="surprised" if t > tr else "determined", legs=(18*ph, -18*ph),
        arms=(30 - 20*ph, 30 + 20*ph), t=t, kid_hair=False)
    if t > w(2, "carton") - .15:
        REF.draw(cv, fr, 800, 1790, .9, age=1, kit="ref", arms=(8, 170), mood="determined", t=t)
        CARD.draw(cv, fr, 905, 1075, 1.2*pop_in(t, w(2, "carton") - .1, .2), 8)
    sec = int(47*prog(t, te, w(2, "secondes", end=True) - te))
    LBL(f"0:{sec:02d}", "mtimer", font("title", 130), (255, 70, 60), (24, 22, 26), padx=34, pady=4, rough=2).draw(cv, fr, CX, 520, 1, 0)
    show_stamp(cv, fr, K2b, t, tr - .05, CX, 330, -5)
    if t > tr: tint(cv, .12*(1 - prog(t, tr, .6)), (220, 20, 30))

def s2c(cv, fr, t):
    stage_fill(cv, fr, (20, 20, 26), "ms2tun"); d = ImageDraw.Draw(cv)
    d.rounded_rectangle([200, 260, 880, 1500], 300, fill=(46, 46, 56)); d.rounded_rectangle([300, 420, 780, 1400], 220, fill=(214, 206, 180))
    cv.paste(cv.filter(ImageFilter.GaussianBlur(14)), (0, 0))
    ts = w(2, "Il", 2) - .1
    YOUNG.draw(cv, fr, CX, 980, 1.3, mood="cry", tears=t - ts, t=t, tilt=-4, look=(0, 1))
    kw(cv, fr, T2c, t, w(2, "sort") - .1, None, CX, 330, -2)

def s2(cv, fr, t, T):
    shots(cv, fr, t, [(0, s2a), (w(2, "Il") - .1, s2b), (w(2, "Il", 2) - .1, s2c)], d=.24)
    impact(cv, t, w(2, "rouge"), 22); flashes(cv, t, w(2, "rouge"), .1, .5); drift(cv, t, T, .04)

# ------------------------------------------------------------------ SCÈNE 3 — 2006 : 18 ans, 1er but en Coupe du monde
def s3(cv, fr, t, T):
    bg(cv, "wc06", t, blur=2)
    tb = w(3, "but")
    draw_goal(cv, fr, CX, 1160, 760, 420, net_u=prog(t, tb, .6), t=t)
    if t < tb:
        u = prog(t, tb - .45, .45); draw_ball(cv, fr, lerp(600, 640, u), lerp(1850, 1060, u) - 120*math.sin(u*math.pi), lerp(1.1, .7, u), t*600)
    else:
        draw_ball(cv, fr, 640, 1060 - 12*math.sin(prog(t, tb, .4)*math.pi), .7, 0)
    leo(cv, fr, PLY, CX - 60, 1880, 1.0, armband=False, age=1, kit="arg", mood="cheer" if t > tb else "determined",
        arms=(165, 165) if t > tb else (30, 30), legs=(12, 12) if t > tb else (0, -40*math.sin(prog(t, tb - .6, .25)*math.pi)), t=t, kid_hair=False)
    kw(cv, fr, K3a, t, .03, None, CX, 330, -3)
    show_stamp(cv, fr, K3b, t, w(3, "dix-huit") - .05, 760, 560, 6)
    show(cv, fr, T3a, t, w(3, "premier") - .05, None, CX, 730, -2)
    if t > tb:
        confetti(cv, fr, "mc3", t - tb, 80, 3, [CIEL, BLANC, GOLD]); camera_flashes(cv, fr, "mf3", t - tb, 1.2, 8)
    impact(cv, t, tb, 18); punch(cv, t, tb, 1.07); drift(cv, t, T, .05)

# ------------------------------------------------------------------ SCÈNE 4 — 3 finales perdues, penalty raté en 2016, retraite… retour
def s4a(cv, fr, t):
    stage_fill(cv, fr, (54, 62, 80), "ms4a"); rays(cv, (CX, 1000), t, .25, 14, 1500, (70, 80, 100))
    MID.draw(cv, fr, CX, 1100, 1.5, mood="sad", t=t, look=(0, 1), alpha=.3, light=False)
    kw(cv, fr, K4a, t, w(4, "Puis") - .05, None, CX, 330, -3)
    ts = (w(4, "trois"), w(4, "finales"), w(4, "perdues"))
    for k, (Tk, y) in enumerate(zip(TICKETS, (680, 960, 1240))):
        Tk.draw(cv, fr, CX + (-30, 30, -20)[k], y, 1.3*slam(t, ts[k] - .1), (-4, 3, -2)[k])
        show_stamp(cv, fr, PERDUE, t, w(4, "perdues") + k*.18, CX + 250, y + 78, (-10, -6, -12)[k])
    grayscale(cv, .5)

def s4b(cv, fr, t):
    bg(cv, "fin16", t, blur=4, dim=.15)
    tp = w(4, "rate") - .1
    draw_goal(cv, fr, CX, 1250, 780, 440)
    dive = prog(t, tp + .15, .4)
    GK.draw(cv, fr, CX + 160*dive, 1260 - 40*math.sin(dive*math.pi), .78, age=1, kit="gk", arms=(60 + 60*dive, 60 + 60*dive), lean=-60*dive, t=t)
    u = prog(t, tp, 1.0)
    bx, by = lerp(560, 800, u), lerp(1800, 610, u) - 90*math.sin(u*math.pi)
    draw_ball(cv, fr, bx, by, lerp(1.6, .45, u), t*800)
    kw(cv, fr, K4b, t, w(4, "En", 2) - .1, None, CX, 330, -3)
    show_stamp(cv, fr, K4c, t, w(4, "penalty"), CX, 1440, -8)

def s4c(cv, fr, t):
    bg(cv, "fin16", t, blur=14, dim=.35)
    tq, ta = w(4, "quitte") - .1, w(4, "Avant") - .1
    back = t > ta
    MID.draw(cv, fr, CX, 960, 1.3, mood="determined" if back else "sad", tears=0 if back else t - tq + .6, t=t, tilt=0 if back else -5,
             look=(0, 0) if back else (0, 1))
    grayscale(cv, 1 - prog(t, ta, .4))
    show_stamp(cv, fr, K4d, t, tq, CX, 330, -4, t_out=ta)
    if back:
        flashes(cv, t, ta, .12, .6)
        show(cv, fr, T4e, t, ta, None, CX, 340, -2)

def s4(cv, fr, t, T):
    shots(cv, fr, t, [(0, s4a), (w(4, "En", 2) - .1, s4b), (w(4, "et") - .1, s4c)], d=.24)
    for k in ("trois", "finales", "perdues"): impact(cv, t, w(4, k), 10)
    impact(cv, t, w(4, "penalty"), 18); drift(cv, t, T, .04)

# ------------------------------------------------------------------ SCÈNE 5 — 2021 Copa América, 2022 champion du monde
def s5a(cv, fr, t):
    stage_fill(cv, fr, NUIT, "ms5a"); fireworks(cv, "mfw5", t)
    d = ImageDraw.Draw(cv)
    for k in range(10): d.rectangle([0, 1300 + k*62, W, 1362 + k*62], fill=(44, 112, 62) if k % 2 == 0 else (40, 100, 56))
    for k, x in enumerate((170, 380, 700, 910)):
        TEAM[k].draw(cv, fr, x, 1880, .66, age=1, kit="arg", mood="cheer", arms=(165, 165), legs=(10, 10), t=t + k)
    hop = abs(math.sin(t*3.4))
    trophy_lift(cv, fr, PLA, CX, 1500 - 260*hop, .7, "arg", t, CUP, beard=True)
    kw(cv, fr, K5a, t, .03, None, CX, 330, -3)
    show_stamp(cv, fr, K5b, t, w(5, "Copa") - .05, CX, 490, 4)
    confetti(cv, fr, "mc5a", t - w(5, "Copa"), 70, 3, [CIEL, BLANC, GOLD])

def s5b(cv, fr, t):
    stage_fill(cv, fr, (40, 26, 10), "ms5b"); rays(cv, (CX, 760), t, 1.0, 18, 1600, (236, 186, 70))
    tc = w(5, "champion")
    if t < tc - .1:
        trophy_lift(cv, fr, PLA, CX, 1860, .95, "arg", t, WC_TROPHY, beard=True)
        kw(cv, fr, K5c, t, w(5, "deux", 2) - .1, None, CX, 330, -3)
    else:
        ADULT.draw(cv, fr, CX, 980, 1.3, mood="cheer", t=t, tears=t - tc + .3, tilt=2)
        WC_TROPHY.draw(cv, fr, 790, 1500, 1.5 + .05*math.sin(t*4), 8)
        show_stamp(cv, fr, K5d, t, tc - .05, CX, 330, -4)
        camera_flashes(cv, fr, "mf5", t - tc, 2.0, 10)
    confetti(cv, fr, "mc5b", t - w(5, "deux", 2), 110, 4, [GOLD, BLANC, CIEL, (250, 220, 120)])

def s5(cv, fr, t, T):
    shots(cv, fr, t, [(0, s5a), (w(5, "Et", 2) - .1, s5b)], d=.24)
    impact(cv, t, w(5, "Copa"), 16); impact(cv, t, w(5, "champion"), 24); flashes(cv, t, w(5, "champion"), .12, .6); drift(cv, t, T, .04)

# ------------------------------------------------------------------ SCÈNE 6 — 2026 : finale perdue contre l'Espagne, « tout donné pour ce maillot »
def s6a(cv, fr, t):
    bg(cv, "fin26", t, blur=4, dim=.3)
    kw(cv, fr, K6a, t, .03, None, CX, 330, -3)
    show(cv, fr, T6a, t, w(6, "dernière") - .05, None, CX, 480, 2)
    score2(cv, fr, CX, 720, "ARGENTINE", "ESPAGNE", 0, 1, "finale 2026", .85*pop_in(t, w(6, "perdue") - .1, .3))
    for k, x in enumerate((760, 940)):
        ESP[k].draw(cv, fr, x, 1840, .72, age=1, kit="spain", mood="cheer", arms=(160, 160), t=t + k*.7)
    leo(cv, fr, PLA, 330, 1860, .95, age=1, kit="arg", beard=True, mood="sad", look=(0, 1), arms=(-6, -6), t=t)
    confetti(cv, fr, "mc6", t - w(6, "perdue"), 90, 4, [RED, (250, 200, 30), RED])

def s6b(cv, fr, t):
    bg(cv, "fin26", t, blur=14, dim=.4)
    tm, tt, tmy = w(6, "message"), w(6, "toujours"), w(6, "maillot")
    OLD.draw(cv, fr, CX, 1000, 1.3, mood="emotional", t=t, tears=max(0, t - tt), hand=prog(t, tmy - .5, .6), tilt=-1)
    a = win(t, tm - .15, tt - .1)
    if a > .01: NOTIF.draw(cv, fr, CX, 560 - 60*(1 - a), a, 0)
    kw(cv, fr, K6b, t, tt - .05, None, CX, 330, -2)
    kw(cv, fr, K6c, t, tmy - .1, None, CX, 470, 3)

def s6(cv, fr, t, T):
    shots(cv, fr, t, [(0, s6a), (w(6, "Puis") - .1, s6b)], d=.24)
    impact(cv, t, w(6, "perdue"), 14); drift(cv, t, T, .04)

# ------------------------------------------------------------------ SCÈNE 7 — 6 octobre, Monumental : le tout dernier match
def s7a(cv, fr, t):
    bg(cv, "mon", t, blur=1)
    for k, x in enumerate((140, 940)): beam(cv, (x, 250), [(x - 120 + 300*(k - .5), 1900), (x + 120 + 300*(k - .5), 1900)], .10)
    walk = math.sin(t*7)
    leo(cv, fr, PLA, CX, 1800 + 6*abs(walk), .9, age=1, kit="arg", beard=True, mood="happy" if t > w(7, "dernier") else "normal",
        arms=(20, 150 if t > w(7, "son") else 20 + 10*walk), legs=(10*walk, -10*walk), t=t)
    kw(cv, fr, K7a, t, w(7, "Six") - .05, None, CX, 330, -3)
    show(cv, fr, T7a, t, w(7, "Monumental") - .05, None, CX, 470, 2)
    show_stamp(cv, fr, K7b, t, w(7, "dernier") - .05, CX, 620, -4)

def s7b(cv, fr, t):
    bg(cv, "mon", t, blur=12, dim=.1)
    bokeh(cv, t, 1.0, (CIEL, BLANC, GOLD), 18, 7)
    OLD.draw(cv, fr, CX, 1000, 1.3, mood="smile", t=t, tilt=2, look=(-1, -1))
    kw(cv, fr, K7a, t, 0, None, CX, 330, -3)
    show_stamp(cv, fr, K7b, t, w(7, "dernier") - .05, CX, 500, -4)
    camera_flashes(cv, fr, "mf7", t - w(7, "dernier"), 3.0, 14, area=(40, 500, 1040, 1150))

def s7(cv, fr, t, T):
    shots(cv, fr, t, [(0, s7a), (w(7, "son") - .1, s7b)], d=.24)
    impact(cv, t, w(7, "dernier"), 12); drift(cv, t, T, .06)

# ------------------------------------------------------------------ SCÈNE 8 — merci Leo, commente, abonne-toi
def s8a(cv, fr, t):
    bg(cv, "mon", t, blur=14, dim=.2); rays(cv, (CX, 900), t, .35, 16, 1500, (250, 220, 150))
    bokeh(cv, t, 1.0, (GOLD, BLANC, CIEL), 16, 4)
    OLD.draw(cv, fr, CX, 960, 1.3, mood="proud", t=t, hand=1, tilt=1)
    ransom_line(cv, "MERCI LEO", 340, 150, seed=8, fr=fr, scale=pop_in(t, w(8, "Merci") - .1, .3))
    show(cv, fr, T8a, t, w(8, "Ton") - .05, None, CX, 1450, -2)

def s8b(cv, fr, t):
    bg(cv, "mon", t, blur=10, dim=.35)
    tc, ta = w(8, "commentaire"), w(8, "abonne-toi")
    kw(cv, fr, K8b, t, w(8, "Dis-le") - .2, None, CX, 330, -2)
    kw(cv, fr, K8c, t, w(8, "Dis-le") - .05, None, CX, 500, 3)
    like_button(cv, fr, CX, 880, .8*pop_in(t, tc - .1, .3), t, tc)      # empilés au centre : rien sous les icônes TikTok (x > 940)
    sub_button(cv, fr, CX, 1210, t, ta - .1, ta + .25)
    ransom_line(cv, "MERCI LEO", 1420, 96, seed=8, fr=fr, scale=pop_in(t, ta + .3, .3))
    confetti(cv, fr, "mc8", t - ta, 90, 4, [CIEL, BLANC, GOLD])

def s8(cv, fr, t, T):
    shots(cv, fr, t, [(0, s8a), (w(8, "Dis-le") - .1, s8b)], d=.24)
    impact(cv, t, w(8, "Merci"), 10); drift(cv, t, T, .04)

# ------------------------------------------------------------------ scènes + bruitages
def SC(name, n, fn, sfx, trans=None, trans_dur=.25, pad_out=.25):
    return Scene(name, TEXTS[n-1], fn, sfx, pad_in=PAD, pad_out=pad_out, trans=trans, trans_dur=trans_dur)
W_ = w
SCENES = [
    SC("21ans", 1, s1, [(.0, "boom", .8), (.0, "heart", .7), (.05, "riser", .4), (W_(1, "Vingt"), "stamp", .8), (W_(1, "Plus"), "stamp", .6),
                        (.34*(W_(1, "Lionel") - .1), "flash", .5), (.68*(W_(1, "Lionel") - .1), "flash", .5), (W_(1, "Lionel") - .1, "whoosh", .5),
                        (W_(1, "Messi"), "crowd_long", .7), (W_(1, "adieu"), "sparkle", .6)]),
    SC("2005", 2, s2, [(.0, "crowd", .6), (.03, "stamp", .6), (W_(2, "match"), "pop"), (W_(2, "Il") - .1, "whoosh", .5), (W_(2, "entre"), "tictac", .7),
                       (W_(2, "carton"), "whistle", .9), (W_(2, "rouge"), "stamp", .9), (W_(2, "rouge"), "gasp", .7),
                       (W_(2, "Il", 2) - .1, "whoosh", .4), (W_(2, "larmes"), "groan", .5)], trans="punch", trans_dur=.3),
    SC("2006", 3, s3, [(.03, "stamp", .6), (W_(3, "dix-huit"), "stamp", .7), (W_(3, "but") - .6, "kick", .8), (W_(3, "but"), "boom", .8),
                       (W_(3, "but"), "crowd_long", 1.0), (W_(3, "but"), "flash", .5), (W_(3, "Coupe"), "sparkle", .6)], trans="whip"),
    SC("finales", 4, s4, [(.0, "rip", .6), (W_(4, "Puis"), "stamp", .5), (W_(4, "trois"), "stamp", .6), (W_(4, "finales"), "stamp", .6), (W_(4, "perdues"), "stamp", .7),
                          (W_(4, "En", 2) - .1, "whoosh", .5), (W_(4, "rate") - .1, "kick", .8), (W_(4, "penalty"), "gasp", .8), (W_(4, "penalty"), "groan", .6),
                          (W_(4, "quitte"), "boom", .5), (W_(4, "Avant") - .1, "riser", .5), (W_(4, "revenir"), "stamp", .7), (W_(4, "revenir"), "crowd", .7)],
       trans="tear_h", trans_dur=.5),
    SC("titres", 5, s5, [(.0, "boom", .7), (.03, "stamp", .6), (W_(5, "Copa"), "stamp", .8), (W_(5, "Copa"), "crowd_long", .9), (W_(5, "Copa") + .2, "horn", .5),
                         (W_(5, "Et", 2) - .1, "whoosh", .5), (W_(5, "deux", 2), "stamp", .6), (W_(5, "Qatar"), "riser", .5),
                         (W_(5, "champion"), "boom", .9), (W_(5, "champion"), "crowd_long", 1.0), (W_(5, "champion"), "sparkle", .8), (W_(5, "champion"), "flash", .5)],
       trans="punch", trans_dur=.3),
    SC("2026", 6, s6, [(.0, "whistle", .7), (.03, "stamp", .6), (W_(6, "perdue"), "groan", .7), (W_(6, "perdue"), "boom", .5),
                       (W_(6, "Puis") - .1, "whoosh", .4), (W_(6, "message"), "notif", .8), (W_(6, "toujours"), "heart", .7), (W_(6, "maillot"), "sparkle", .6)],
       trans="tear_d", trans_dur=.5),
    SC("monumental", 7, s7, [(.0, "crowd_long", 1.0), (W_(7, "Six"), "stamp", .6), (W_(7, "Monumental"), "pop"), (W_(7, "dernier"), "stamp", .9),
                             (W_(7, "dernier"), "flash", .6), (W_(7, "dernier") + .1, "crowd_long", .9)], trans="whip"),
    SC("merci", 8, s8, [(.0, "sparkle", .6), (W_(8, "Merci"), "stamp", .7), (W_(8, "Merci"), "heart", .6), (W_(8, "Dis-le") - .1, "whoosh", .5),
                        (W_(8, "Dis-le"), "pop2"), (W_(8, "commentaire"), "pop"), (W_(8, "commentaire") + .05, "notif"),
                        (W_(8, "abonne-toi"), "pop2"), (W_(8, "abonne-toi") + .25, "notif"), (W_(8, "abonne-toi") + .2, "crowd_long", .8)],
       trans="punch", trans_dur=.3, pad_out=1.3),
]

# ------------------------------------------------------------------ couverture : « 21 ans… et c'est fini ? »
def cover(path):
    cv = background(0, TITLE); bg(cv, "mon", 1.0, blur=12, dim=.25, lights=False)
    OLD.draw(cv, 0, CX, 1060, 1.42, mood="emotional", t=1.0, tears=1.1, tilt=-1.5, blink=False)
    ransom_line(cv, "ADIEU LEO", 330, 150, seed=11, fr=0)
    Label("21 ANS AVEC L'ARGENTINE…", "mcv2", font("title", 70), NOIR, BLANC, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 500, 1, -2)
    Label("LE PLUS GRAND DE L'HISTOIRE ?", "mcv3", font("title", 70), NOIR, GOLD, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 1560, 1, 2)
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
        p = os.path.join(out, f"ma_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", "messi_adieu")
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/messi_adieu_stills"), only=only)); sys.exit()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=23))
