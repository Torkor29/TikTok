"""RENNES — l'histoire du club le plus maudit de France (≈ 70 s), selon SCRIPT.md.
Micro-scène par phrase, fil rouge « ANNÉES SANS TROPHÉE », CTA quiz au milieu (réponse jamais donnée), question finale « meilleur club breton ».
Assets : lille_v5/gfx.py + rgfx.py ; sons : lille_v5/sfx + rennes/sfx (synthèse maison) + banque (foule, but, sifflet).
Voix : voix/voix.mp3 (Léo, resserrée), timings mots.json (faster-whisper local).

  python3 episodes/rennes/rennes.py --stills [scene]
  python3 episodes/rennes/rennes.py output/rennes
"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "brest_ldc"))
sys.path.insert(0, os.path.join(ROOT, "episodes", "lille_v5")); sys.path.insert(0, HERE)
from quiz import *
import foot, fx
from brest_ldc import marker
from rgfx import *
from PIL import ImageChops
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

TITLE = "~/histoires $ ./rennes"
SLUG = "rennes"
VOIX = os.path.join(HERE, "voix", "voix_hook.mp3")   # « Voici l'histoire du club le plus maudit de France » placé en tête
TEXTE = open(os.path.join(HERE, "TEXTE.md")).read()
# temps clés (s, voix) relevés dans mots.json
K = dict(sixzero=1.5, attendu=2.6, ans48=3.0, trophee=4.1, voici=4.6, maudit=5.8, y1901=6.9, etudiants=7.7, stade=9.0, premier=9.7,
         sz2=10.2, adv=11.3, y1929=11.9, claque=13.2, porte=13.6, pendant3=14.4, amicaux=15.9, centaine=16.6, an70=17.2, ivoirien=18.9,
         pokou=19.4, pele=21.1, gagne=22.3, y65=23.5, y71=24.5, rien=25.2, p48=25.9, question=26.8, quel=27.9, gardien=28.4, chelsea=29.5,
         rq=30.4, reponds=30.9, abonne=31.9, like=32.5, chaine=33.7, y2009=34.5, finale09=35.2, guin1=36.2, l2=37.2, y2014=37.8,
         refinale=38.6, reguin=39.4, pendantce=40.1, centre=40.8, gamin=42.0, camp=42.6, maison=43.6, brule=43.9, pro=45.4, seize=45.8,
         eduardo=46.3, cama=46.6, avril=47.6, y2019=47.9, finale19=48.7, psg=49.4, neymar=50.3, mbappe=50.9, paris=51.5, deuxzero=51.8,
         revient=52.6, deuxdeux=53.2, mbappe2=53.6, expulse=54.2, tab=54.6, benarfa=55.6, placard=56.7, psg2=57.3, marque=58.5,
         nkunku=59.0, rate=59.4, ans48b=59.9, maled=60.6, termine=61.4, auj=61.8, bretagne=62.4, trois=62.9, l1=63.5, rennesb=64.0,
         brest=64.4, lorient=64.8, guinb=65.4, l2b=66.0, alors=66.3, meilleur=67.4, breton=67.8, dis=68.3, comm=68.6, club0=5.3, plus0=5.7, france0=6.2)
def m(t):
    """Temps de voix.mp3 -> temps de voix_hook.mp3 (segment « Voici… maudit de France » [4,55-6,80] déplacé en tête)."""
    if 4.5 <= t < 6.8: return t - 4.55
    if t < 4.5: return t + 2.25
    return t - 6.80 + 6.75
K0 = dict(K); K = {k: m(v) for k, v in K.items()}
# ------------------------------------------------------------------ outils communs
def ease(u): u = clamp(u); return u*u*(3 - 2*u)
def eob(u, s=1.9): return ease_out_back(clamp(u), s)
def spring(t, t0, d=.5): return 0 if t < t0 else eob((t - t0)/d)
def wob(t, t0, amp=12, f=9, damp=5):                      # oscillation amortie (rotation d'un objet qui atterrit)
    return 0 if t < t0 else amp*math.sin((t - t0)*f)*math.exp(-(t - t0)*damp)
def put(L, spr, x, y, s=1.0, rot=0.0, a=1.0):
    if s > .01 and a > .01: blit_sxy(L, spr, x, y, s, s, rot, a)
_sh = {}
def shadowed(spr, key=None):
    k = key or id(spr)
    if k not in _sh:
        im = Image.new("RGBA", (spr.width + 40, spr.height + 40), (0, 0, 0, 0)); a = spr.getchannel("A").point(lambda v: v*110//255)
        sh = Image.new("RGBA", spr.size, (30, 20, 14, 0)); sh.putalpha(a); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (34, 38))
        im.alpha_composite(spr, (20, 20)); ax, ay = spr.info["anchor"]; im.info["anchor"] = (ax + 20, ay + 20); _sh[k] = im
    return _sh[k]
LOGO = {n: shadowed(sticker(n, h), ("L", n, h)) for n, h in (("lille", 620), ("psg", 300), ("ucl", 520), ("ligue2", 260))}
def logo(n, h):
    k = ("logo", n, h)
    if k not in _sh: _sh[k] = shadowed(sticker(n, h), k)
    return _sh[k]
def kword(txt, bg=NOIR, fg=BLANC, size=118): return LBL(txt, f"v5k{txt}{bg}{size}", font("title", size), fg, bg, padx=24, pady=6, rough=3)
def stampl(txt, col=ROUGE, size=150): return LBL(txt, f"v5s{txt}{size}", font("title", size), col, CREME, padx=34, pady=6, rough=2)
def tag(txt, size=60, bg=BLANC, fg=NOIR): return LBL(txt, f"v5t{txt}{size}{bg}", font("title", size), fg, bg, padx=24, pady=8, rough=2)
def mono(txt, size=64, bg=NOIR, fg=BLANC): return LBL(txt, f"v5m{txt}{size}{bg}", font("mono", size), fg, bg, padx=18, pady=6, rough=2)
def slam_in(L, fr, lab, t, t0, x, y, rot=0, d=.2):
    if t >= t0: lab.draw(L, fr, x, y, 1 + .5*(1 - eob((t - t0)/d, 2.2)) if t - t0 < d else 1, rot + wob(t, t0, 4, 14, 8))
_tex = {}
def paper_fill(L, col, key):
    """Papier texturé de la taille du calque (gouache + grain), mis en cache."""
    k = (key, L.size, col)
    if k not in _tex:
        w_, h_ = L.size; rng = np.random.default_rng(abs(hash(key)) % 999)
        g = np.asarray(Image.fromarray((rng.random((h_//24 + 2, w_//24 + 2))*255).astype(np.uint8)).resize((w_, h_), Image.BICUBIC), np.float32)/255
        a = np.zeros((h_, w_, 3), np.float32); a[:] = col; a *= (.93 + .12*g)[..., None]
        sp = rng.random((h_, w_)).astype(np.float32); a += ((sp > .965)*14 - (sp < .03)*12)[..., None]
        _tex[k] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    L.paste(_tex[k], (0, 0))
def vgrad(L, y0, y1, c0, c1):
    d = ImageDraw.Draw(L)
    for y in range(int(y0), int(y1), 6):
        u = (y - y0)/(y1 - y0); d.rectangle([0, y, L.width, y + 6], fill=tuple(int(lerp(a, b, u)) for a, b in zip(c0, c1)))
def dark(L, a):
    if a > .01: L.alpha_composite(Image.new("RGBA", L.size, (8, 6, 14, int(255*clamp(a)))))
def marker_line(L, p0, p1, u, col=ROUGE, wd=14):
    if u <= 0: return
    ImageDraw.Draw(L).line([p0, (lerp(p0[0], p1[0], clamp(u)), lerp(p0[1], p1[1], clamp(u)))], fill=col, width=wd)
def marker_circle(L, cx, cy, rx, ry, u, col=ROUGE, wd=12):
    if u <= 0: return
    n = int(60*clamp(u)); pts = [(cx + rx*math.cos(-1.3 + 2.25*math.pi*k/60), cy + ry*math.sin(-1.3 + 2.25*math.pi*k/60)) for k in range(n + 1)]
    if len(pts) > 1: ImageDraw.Draw(L).line(pts, fill=col, width=wd)

# personnages papier (génériques, pas de visages réels)
foot.KITS["lille"] = dict(kind="plain", c1=(214, 16, 40), sleeve=(214, 16, 40), shorts=(18, 30, 78), socks=(214, 16, 40), trim=(250, 250, 246))
foot.KITS["lille_gk"] = dict(kind="plain", c1=(46, 170, 96), sleeve=(46, 170, 96), shorts=(30, 30, 34), socks=(46, 170, 96), trim=(250, 250, 246))
foot.KITS["coach_navy"] = dict(kind="plain", c1=(24, 34, 70), sleeve=(24, 34, 70), shorts=(24, 34, 70), socks=(24, 34, 70), trim=(214, 16, 40), pants=True)
HZ = foot.Player("v5hazard", hair=(84, 54, 32))
VAHID = foot.Player("v5vahid", hair=(214, 214, 218))
RUDI = foot.Player("v5rudi", hair=(160, 160, 166))
MAIGNAN = foot.Player("v5maignan", hair=(26, 22, 20), skin=(112, 74, 52))
YILMAZ = foot.Player("v5yilmaz", hair=(38, 30, 26), beard_col=(38, 30, 26))
GALTIER = foot.Player("v5galtier", hair=(130, 130, 136), hair_style="bald")
LOSCP = foot.Player("v5loscp", hair=(60, 40, 28))
PSGP = foot.Player("v5psgp", hair=(36, 28, 24))
def player_rot(L, fr, pl, x, y, rot, s=1.0, **kw):
    """Joueur dessiné sur un calque puis tourné (plongeon, chute). (x, y) = pieds avant rotation, pivot = bassin."""
    lay = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); pl.draw(lay, fr, 450, 700, s=s, **kw)
    lay.info["anchor"] = (450, 700 - 230*s); blit_sxy(L, lay, x, y - 230*s, 1, 1, rot)

# ------------------------------------------------------------------ caméra par scène
def camk(keys, t):
    """keys = [(t, cx, cy, z)] interpolés (ease) ; renvoie cx, cy, z."""
    if t <= keys[0][0]: return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            u = ease((t - a[0])/(b[0] - a[0])); return tuple(lerp(p, q, u) for p, q in zip(a[1:], b[1:]))
    return keys[-1][1:]
def apply_cam(L, cx, cy, z, rot=0.0):
    """Recadre le calque de scène (taille quelconque) autour de (cx, cy) au zoom z -> image W x H."""
    z = max(z, max(W/L.width, H/L.height)); bw, bh = W/z, H/z
    x0 = min(max(cx - bw/2, 0), L.width - bw); y0 = min(max(cy - bh/2, 0), L.height - bh)
    im = L.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.BICUBIC)
    if abs(rot) > .05: im = im.rotate(rot, resample=Image.BICUBIC, fillcolor=im.getpixel((2, 2)))
    return im
PUNCH = []
def punch(t): return 1 + sum(.06*math.exp(-((t - p)/.11)**2) for p in PUNCH if p - .4 < t < p + .5)

# ================================================================== SCÈNES (t = temps voix)
SC = []
def scene(t0, size=(W, H), trans="cut", td=.3):
    def deco_(fn): SC.append(dict(t0=t0, fn=fn, size=size, trans=trans, td=td, name=fn.__name__)); return fn
    return deco_

# ------------------------------------------------------------------ fil rouge : années sans trophée + date
def drought(t):
    if t < K["y71"]: return None
    if t < K["rien"]: return None
    if t < K["p48"]: return max(1, int(48*ease((t - K["rien"])/.7)))
    if t < K["termine"]: return 48
    return 0
DATES = [(0, "RENNES")] + [(m(a), b) for a, b in ((6.9, "1901"), (11.9, "1929"), (17.2, "1974"), (22.3, "1965"), (24.5, "1971"), (26.8, "QUIZ"), (34.5, "2009"),
         (37.8, "2014"), (40.1, "2005"), (47.6, "2019"), (61.8, "2026"))]
def fil_rouge(cv, fr, t):
    if t < 1.5: return
    lab = [d for d in DATES if t >= d[0]][-1][1]
    mono(lab, 46, NOIR).draw(cv, fr, 160, 262, 1.0, -3)
    n = drought(t)
    if n is not None and not (K["question"] - .2 < t < K["y2009"]) and t < K["auj"] + .5:
        col = ROUGE if n else (40, 150, 70)
        txt = f"{n} ANS SANS TROPHÉE" if n else "MALÉDICTION BRISÉE ✓"
        LBL(txt, f"rdr{txt}", font("title", 38) if n else fsans(32), BLANC, col, padx=14, pady=5, rough=2).draw(cv, fr, 620, 258, 1, 2)

# ================================================================== SCÈNES
RB = (190, 20, 30)
def stripes_bg(L, a=(196, 22, 32), b=(26, 24, 28), w_=140, key="rs"):
    paper_fill(L, a, key); d = ImageDraw.Draw(L)
    for x in range(-H, L.width, 2*w_): d.polygon([(x, 0), (x + w_, 0), (x + w_ + H*.35, L.height), (x + H*.35, L.height)], fill=b)

# 0. HOOK : 6-0 et 48 ans
@scene(m(0.0), trans="whip", td=.25)
def s_hook(L, fr, t):
    stripes_bg(L, key="hook"); dark(L, .25)
    fx.kinetic(L, fr, t, [("RENNES", -.5)], CX, 620, lambda x, i: kword(x, NOIR, BLANC, 190))
    put(L, shadowed(badge(360), "bdg360"), 860, 1560 + 6*math.sin(t*3), .8, 8 + wob(t, K["sixzero"], 6, 18, 5))
    if t < K["attendu"] - .1:
        put(L, board_base(860, 330, "RENNES", "ADVERSAIRE"), CX, 1060, 1.0)
        board_score(L, CX, 1090, t, [(0, 0, 0)] + [(K["sixzero"] + i*.1, 0, i + 1) for i in range(6)], 150)
        if t > K["sixzero"] + .65: slam_in(L, fr, stampl("PREMIER MATCH", ROUGE, 70), t, K["sixzero"] + .65, CX, 1340, -6)
    else:
        u = clamp((t - K["attendu"])/1.2)
        put(L, shadowed(scale_stand(), "stand"), CX, 1300, 1.1)
        cobweb(L, CX - 120, 760, 260*u, 1); cobweb(L, 120, 620, 300*u, 1)
        LBL("?", "rq?", font("title", 220), (120, 110, 100), None).draw(L, fr, CX, 820, 1, 0)
        n = int(48*ease((t - K["ans48"] + .1)/.5)) if t > K["ans48"] - .1 else 0
        if n: slam_in(L, fr, kword(f"{n} ANS", JAUNE, NOIR, 170), t, K["ans48"] - .1, CX, 1480, -4)
CAM_HOOK = [(0, CX, 960, 1.1), (1.4, CX, 1000, 1.0), (1.6, CX, 1080, 1.12), (2.5, CX, 1060, 1.0), (4.6, CX, 1100, 1.08)]

# 1. LE CLUB LE PLUS MAUDIT : chat noir
@scene(0.0)
def s_cat(L, fr, t):
    paper_fill(L, (34, 30, 40), "night"); rays(L, (CX, 1000), t, .9, 14, 1700, (120, 20, 30), .1, .3)
    put(L, shadowed(badge(480), "bdg480"), CX, 900, 1.0, wob(t, K["maudit"], 3, 30, 3))
    if t > K["maudit"]:
        d = ImageDraw.Draw(L); u = clamp((t - K["maudit"])/.25)
        d.line([(CX - 60, 700), (CX, 860), (CX - 40, 980), (CX + 30, 1110)][:2 + int(2*u)], fill=(240, 240, 240), width=8)
    xc = lerp(-100, W + 300, clamp((t + .1)/2.3)); put(L, black_cat(), xc, 1500 + 10*abs(math.sin(t*10)), .9)
    fx.kinetic(L, fr, t, [("LE CLUB", -.5), ("LE PLUS", -.4), ("MAUDIT", -.3), ("DE FRANCE", K["france0"] - .05)], CX, 600,
               lambda x, i: kword(x, ROUGE if x == "MAUDIT" else NOIR, BLANC, 140 if x == "MAUDIT" else 112), maxw=980)
CAM_CAT = [(4.6, CX, 960, 1.0), (5.8, CX, 900, 1.12), (6.9, CX, 960, 1.0)]

# 2. 1901 : étudiants + premier match 6-0
@scene(K["y1901"], trans="tear", td=.3)
def s_1901(L, fr, t):
    paper_fill(L, (214, 190, 146), "sep")
    slam_in(L, fr, stampl("1901", (110, 70, 40), 200), t, K["y1901"] + .02, CX, 660, -4)
    if t < K["premier"] - .1:
        for i, x in enumerate((300, 780)):
            if t > K["etudiants"] - .05 + i*.15:
                foot.Player(f"etu{i}", hair=(70, 50, 30)).draw(L, fr, x, 1650, s=.75, kit="suit", arms=(15, 40 if i == 0 else 15), mood="happy", t=t)
                put(L, boater(), x, 1650 - 590*.75 - 10, .8, 0)
        if t > K["stade"] - .1: put(L, shadowed(badge(360), "bdg360"), CX, 1080, eob((t - K["stade"] + .1)/.35, 2.2), 0)
    else:
        put(L, board_base(860, 330, "RENNES", "FC RENNAIS"), CX, 1100, 1.0)
        board_score(L, CX, 1130, t, [(0, 0, 0)] + [(K["sz2"] - .1 + i*.12, 0, i + 1) for i in range(6)], 150)
        foot.draw_goal(L, fr, CX, 1550, 600, 300, clamp((t - K["sz2"])/.8) % 1 if t > K["sz2"] else 0, 1, t)
        for i in range(6):
            ti = K["sz2"] - .1 + i*.12
            if ti < t < ti + .35: foot.draw_ball(L, fr, CX + (i - 2.5)*70, lerp(1900, 1450, (t - ti)/.35), .6, t*500)
        if t > K["adv"]: slam_in(L, fr, stampl("POUR L'ADVERSAIRE", ROUGE, 66), t, K["adv"], CX, 1820 - 400, -6)
CAM_1901 = [(6.9, CX, 960, 1.0), (8.0, CX, 1100, 1.08), (9.6, CX, 1000, 1.0), (10.3, CX, 1250, 1.12), (11.9, CX, 1100, 1.0)]

# 3. 1929 : porte qui claque, 100 matchs amicaux
@scene(K["y1929"], trans="whip", td=.25)
def s_1929(L, fr, t):
    paper_fill(L, (226, 214, 188), "1929")
    slam_in(L, fr, stampl("1929", NOIR, 170), t, K["y1929"] + .02, CX, 640, -3)
    if t < K["pendant3"] - .05:
        u = clamp((t - K["claque"])/.4); ang = lerp(70, 0, u*u)
        dr = door("LIGUE"); put(L, dr, CX, 1200, 1.0) if u >= 1 else put(L, dr.resize((max(1, int(dr.width*math.cos(math.radians(ang)))), dr.height)) if ang < 89 else dr, CX, 1200, 1.0)
        if 0 < t - K["porte"] < .6:
            for k in range(14):
                a = k/14*math.pi; r_ = 300 + 500*(t - K["porte"]); ImageDraw.Draw(L).ellipse([CX + r_*math.cos(a) - 14, 1580 - 80*math.sin(a)*(t - K["porte"])*3 - 14, CX + r_*math.cos(a) + 14, 1580 - 80*math.sin(a)*(t - K["porte"])*3 + 14], fill=(200, 186, 160))
    else:
        n = min(100, int(100*clamp((t - K["pendant3"])/2.0)))
        d = ImageDraw.Draw(L)
        for i in range(n):
            g, j = divmod(i, 5); gx = 130 + (g % 5)*170; gy = 820 + (g//5)*150
            if j < 4: d.line([(gx + j*28, gy), (gx + j*28, gy + 100)], fill=NOIR, width=9)
            else: d.line([(gx - 12, gy + 80), (gx + 100, gy + 16)], fill=ROUGE, width=9)
        kword(f"{n} MATCHS AMICAUX", NOIR, BLANC, 76).draw(L, fr, CX, 760, 1, 2)
        if t > K["centaine"]: slam_in(L, fr, stampl("UNE CENTAINE !", ROUGE, 110), t, K["centaine"], CX, 1450, -8)
CAM_1929 = [(11.9, CX, 960, 1.0), (13.4, CX, 1150, 1.12), (14.3, CX, 1000, 1.0), (16.5, CX, 1050, 1.05), (17.2, CX, 1000, 1.0)]

# 4. POKOU encensé par Pelé
POKOU = foot.Player("rpokou", hair=(24, 20, 18), skin=(96, 62, 44))
foot.KITS["rennes"] = dict(kind="plain", c1=(214, 26, 34), sleeve=(214, 26, 34), shorts=(24, 22, 26), socks=(24, 22, 26), trim=(250, 250, 246))
@scene(K["an70"], trans="flash", td=.15)
def s_pokou(L, fr, t):
    vgrad(L, 0, H, (16, 18, 40), (40, 40, 70)); rays(L, (CX, -200), t, .7, 5, 2400, (255, 250, 210), .05, .2)
    paper_fill_band = ImageDraw.Draw(L); paper_fill_band.rectangle([0, 1600, W, H], fill=(40, 110, 60))
    kick = math.sin(t*7)
    POKOU.draw(L, fr, CX, 1640, s=1.25, kit="rennes", legs=(0, -30*max(0, kick)), arms=(30, 30), mood="happy", t=t)
    foot.draw_ball(L, fr, CX + 60, 1500 - 220*abs(math.sin(t*3.5)), .8, t*300)
    if t > K["ivoirien"] - .1: flag_civ(L, 760, 620, t, eob((t - K["ivoirien"] + .1)/.3))
    if t > K["pokou"] - .05: put(L, pin_tag("LAURENT POKOU", 64), 330, 980, eob((t - K["pokou"] + .05)/.25), -3)
    if t > K["pele"] - .1:
        u = clamp((t - K["pele"] + .1)/.4); put(L, crown(), CX, lerp(300, 1640 - 1.25*640 - 30, ease(u)), .9, 0)
        fx.wipe(L, fr, marker("ENCENSÉ PAR PELÉ", "rpele", 84), CX, 640, t, K["pele"], -2)
        for k in range(8):
            a = k*math.pi/4 + t; put(L, spark(40), CX + 260*math.cos(a), 900 + 160*math.sin(a), .8 + .3*math.sin(t*9 + k), t*90)
CAM_POKOU = [(17.2, CX, 1000, 1.0), (19.3, CX, 1100, 1.1), (21.0, CX, 900, 1.15), (22.3, CX, 960, 1.0)]

# 5. Coupes 65 / 71, puis plus rien
@scene(K["gagne"], trans="whip", td=.25)
def s_cups(L, fr, t):
    paper_fill(L, (60, 30, 32), "wall2")
    put(L, shelf("TROPHÉES"), CX, 1250, 1.15)
    for x, yr, t0 in ((330, "1965", K["y65"] - .1), (740, "1971", K["y71"] - .1)):
        if t < t0: continue
        u = clamp((t - t0)/.22); put(L, cup_gold(380), x, lerp(500, 1222, u*u), 1.0, wob(t, t0 + .22, 4, 12, 6))
        tag(yr, 50, CREME).draw(L, fr, x, 1390, eob((t - t0 - .1)/.25), -2)
    if t > K["rien"] - .05:
        u = clamp((t - K["rien"])/1.4); dark(L, .45*u)
        cobweb(L, 0, 0, 520*u, 1); cobweb(L, W, 0, 0, 0)
        d = ImageDraw.Draw(L)
        for k in range(int(40*u)): d.ellipse([(k*97) % W, 1180 + (k*13) % 40, (k*97) % W + 6, 1186 + (k*13) % 40], fill=(150, 140, 130))
        slam_in(L, fr, kword("PUIS… PLUS RIEN.", NOIR, BLANC, 110), t, K["rien"] - .05, CX, 660, -3)
    else: fx.kinetic(L, fr, t, [("COUPE DE FRANCE", K["gagne"] + .4)], CX, 660, lambda x, i: kword(x, JAUNE, NOIR, 100))
CAM_CUPS = [(22.3, CX, 1000, 1.0), (23.5, 360, 1050, 1.15), (24.5, 720, 1050, 1.15), (25.3, CX, 1000, 1.0), (26.8, CX, 960, 1.08)]

# 6. CTA QUIZ (réponse jamais donnée)
@scene(K["question"], trans="glitch", td=.18)
def s_quiz(L, fr, t):
    paper_fill(L, (20, 30, 76), "quiz"); rays(L, (CX, 1050), t, .6, 16, 1700, (34, 48, 110), .1, .3)
    if not (K["quel"] - .1 < t < K["abonne"] - .2): mono(fx.typed_cursor("QUESTION POUR LES VRAIS", t, K["question"], 30), 54, ROUGE).draw(L, fr, CX, 520, 1, -2)
    if t < K["abonne"] - .2:
        lay = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); foot.Player("rgk", hair=(40, 30, 20)).draw(lay, fr, 450, 860, s=1.1, kit="gk", arms=(110, 110), t=t)
        a = lay.getchannel("A"); sil = Image.new("RGBA", lay.size, (8, 8, 12, 255)); sil.putalpha(a); sil.info["anchor"] = (450, 860)
        put(L, sil, CX, 1560, 1.0)
        put(L, qmark(), CX, 900 + 10*math.sin(t*4), .55, 6*math.sin(t*3))
        fx.kinetic(L, fr, t, [("QUEL FUTUR", K["quel"] - .02), ("GARDIEN", K["gardien"] - .02), ("DE CHELSEA", K["chelsea"] - .05), ("A JOUÉ À RENNES ?", K["rq"] - .1)],
                   CX, 640, lambda x, i: kword(x, BLANC if i != 2 else JAUNE, NOIR, 80), maxw=1000)
        if t > K["reponds"] - .05:
            fx.wipe(L, fr, marker("RÉPONDS EN COMMENTAIRE", "rrep", 70), CX, 1430, t, K["reponds"] - .05, 2)
            y = 1530 + 16*abs(math.sin(t*6)); ImageDraw.Draw(L).polygon([(CX - 46, y), (CX + 46, y), (CX, y + 56)], fill=ROUGE)
    else:
        pressed = t > K["abonne"] + .25
        put(L, sub_button(pressed), CX, 900, 1.0 if not pressed else .96)
        fu = clamp((t - K["abonne"])/.25); put(L, finger(), CX + 80, lerp(1250, 1000, fu) if t < K["abonne"] + .4 else 1000 + 200*clamp((t - K["abonne"] - .4)/.3), 1.0, 0)
        if t > K["like"] - .1:
            put(L, heart(150), CX, 1350, eob((t - K["like"] + .1)/.3, 2.6), 0)
            for k in range(10):
                u = (t - K["like"])*.9 - k*.05
                if 0 < u < 1: put(L, heart(28 + (k % 3)*10, (255, 90, 130)), CX + 300*math.sin(k*1.7)*u, 1350 - 600*u, 1 - u*.5, 20*math.sin(k))
        if t > K["chaine"] - .1: slam_in(L, fr, kword("MERCI !", JAUNE, NOIR, 120), t, K["chaine"] - .1, CX, 620, -3)
CAM_QUIZ = [(26.8, CX, 960, 1.0), (30.8, CX, 1050, 1.05), (31.8, CX, 950, 1.12), (32.6, CX, 1200, 1.12), (34.5, CX, 1000, 1.0)]

# 7. GUINGAMP ×2
@scene(K["y2009"], trans="whip", td=.25)
def s_guingamp(L, fr, t):
    paper_fill(L, (238, 230, 212), "gbg")
    second = t > K["y2014"] - .1; fl = clamp((t - K["y2014"] + .1)/.3)
    sx = abs(math.cos(math.pi*fl)) if 0 < fl < 1 else 1
    tk = ticket("FINALE 2014" if fl > .5 else "FINALE 2009", "STADE DE FRANCE", ROUGE, 640)
    blit_sxy(L, tk, CX, 620, max(.02, sx), 1, -3)
    put(L, board_base(860, 330, "RENNES", "GUINGAMP"), CX, 1080, 1.0)
    seq = [(0, 0, 0), (K["guin1"] - .3, 0, 1), (K["guin1"], 1, 1), (K["guin1"] + .3, 1, 2)] if not second else [(0, 0, 0), (K["refinale"], 0, 1), (K["refinale"] + .4, 0, 2)]
    board_score(L, CX, 1110, t, seq, 150)
    if not second and t > K["l2"] - .05: slam_in(L, fr, stampl("UN CLUB DE LIGUE 2 !", ROUGE, 80), t, K["l2"] - .05, CX, 1400, -6)
    if second and t > K["reguin"] - .05: slam_in(L, fr, stampl("RE-GUINGAMP…", NOIR, 96), t, K["reguin"] - .05, CX, 1400, 5)
    if second: put(L, black_cat(), lerp(W + 300, -300, clamp((t - K["refinale"])/1.5)), 1640, .8)
    if t > K["reguin"]: put(L, tractor(), lerp(-300, W + 300, clamp((t - K["reguin"])/1.2)), 1760, .7)
CAM_GUIN = [(34.5, CX, 960, 1.0), (36.0, CX, 1100, 1.1), (37.3, CX, 1250, 1.05), (37.8, CX, 900, 1.08), (39.3, CX, 1300, 1.0), (40.1, CX, 1100, 1.0)]

# 8. CAMAVINGA
@scene(K["pendantce"], trans="tear", td=.3)
def s_cama(L, fr, t):
    paper_fill(L, (58, 140, 76), "cpitch"); d = ImageDraw.Draw(L)
    for k in range(0, H, 220): d.rectangle([0, k, W, k + 110], fill=(70, 156, 88))
    if t < K["eduardo"] - .1:
        mono(fx.typed_cursor("CENTRE DE FORMATION", t, K["centre"], 26), 54).draw(L, fr, CX, 640, 1, -2)
        if t > K["camp"] - .1: put(L, tent(), 280, 1150, eob((t - K["camp"] + .1)/.3), -3)
        if t > K["maison"] - .1:
            put(L, house(), 760, 1150, eob((t - K["maison"] + .1)/.3), 2)
            if t > K["brule"]: flames(L, 760, 960, t, 1.0 + .4*clamp((t - K["brule"])/.5)); dark(L, .15)
        foot.Player("rcamak", hair=(20, 16, 14), skin=(96, 62, 44)).draw(L, fr, CX, 1640, s=.95, age=.45, kit="rennes", arms=(20, 20), mood="sad" if K["brule"] < t < K["pro"] else "happy", t=t)
        if t > K["pro"] - .05: slam_in(L, fr, stampl("PRO À 16 ANS", ROUGE, 110), t, K["pro"] - .05, CX, 1380, -6)
    else:
        put(L, shadowed(photo_card(*CAMA, 820), "camac"), CX, 1050, 1 + .5*(1 - eob((t - K["eduardo"] + .1)/.25)), -3)
        fx.wipe(L, fr, marker("EDUARDO CAMAVINGA", "rcam", 88), CX, 1560 - 100, t, K["cama"], 2)
CAM_CAMA = [(40.1, CX, 960, 1.0), (42.5, 330, 1100, 1.12), (43.6, 740, 1050, 1.12), (45.3, CX, 1200, 1.05), (46.3, CX, 1050, 1.1), (47.6, CX, 1000, 1.0)]

# 9. FINALE 2019 : 0-2 -> 2-2, Mbappé expulsé
@scene(K["avril"], trans="whip", td=.25)
def s_final(L, fr, t):
    vgrad(L, 0, H, (10, 14, 40), (30, 36, 80)); d = ImageDraw.Draw(L)
    for k in range(50): d.ellipse([(k*67) % W, 1650 + (k*31) % 250, (k*67) % W + 8, 1658 + (k*31) % 250], fill=(255, 240, 180) if (k + fr//4) % 6 == 0 else (60, 60, 90))
    slam_in(L, fr, kword("FINALE 2019", JAUNE, NOIR, 110), t, K["y2019"] - .05, CX, 640, -3)
    put(L, board_base(900, 360, "RENNES", "PSG"), CX, 1000, 1.05)
    board_score(L, CX, 1030, t, [(0, 0, 0), (K["deuxzero"] - .15, 0, 1), (K["deuxzero"] + .15, 0, 2), (K["revient"], 1, 2), (K["deuxdeux"], 2, 2)], 160)
    for nm, x, t0, r in (("NEYMAR", 300, K["neymar"], -4), ("MBAPPÉ", 780, K["mbappe"], 3)):
        if t > t0 - .05: put(L, pin_tag(nm, 60), x, 1330, eob((t - t0 + .05)/.25), r)
    if t > K["expulse"] - .2:
        u = clamp((t - K["expulse"] + .2)/.2); put(L, red_card(), 780, lerp(2200, 1380, u), 1.0, lerp(40, 12, u))
        if t > K["expulse"]: slam_in(L, fr, stampl("EXPULSÉ", ROUGE, 90), t, K["expulse"], 780, 1640 - 120, -8)
    camera_flashes(L, fr, "rfl", t - K["avril"] - .4, 2.0, 12, (60, 1650, 1020, 1880))
CAM_FINAL = [(47.6, CX, 960, 1.0), (51.4, CX, 1000, 1.15), (53.4, CX, 1000, 1.18), (53.8, 760, 1350, 1.15), (54.6, CX, 1100, 1.0)]

# 10. TIRS AU BUT : Ben Arfa, Nkunku
PEN_R = [(K["tab"] + .3 + i*.55, "ok") for i in range(6)]
PEN_P = [(K["tab"] + .55 + i*.55, "ok") for i in range(5)] + [(K["rate"], "ko")]
@scene(K["tab"], trans="flash", td=.15)
def s_pens(L, fr, t):
    vgrad(L, 0, H, (10, 14, 40), (30, 36, 80))
    kword("TIRS AU BUT", BLANC, NOIR, 100).draw(L, fr, CX, 520, 1, -2)
    for y, nm, res in ((680, "RENNES", PEN_R), (820, "PSG", PEN_P)):
        mono(nm, 40, NOIR).draw(L, fr, 120, y, 1, 0); pen_dots(L, 600, y, t, 0, res, r=40, gap=100)
    if t < K["nkunku"] - .1:
        put(L, closet(), CX + 220, 1300, 1.0)
        op = clamp((t - K["placard"] + .3)/.4); out_ = clamp((t - K["placard"])/.4)
        put(L, shadowed(photo_card(*BENARFA, 560), "bac"), lerp(CX + 220, CX - 150, ease(out_)), 1300, .3 + .7*out_ if t > K["placard"] - .3 else 0, -4*out_)
        if t > K["benarfa"] - .05: fx.wipe(L, fr, marker("HATEM BEN ARFA", "rba", 80), CX - 120, 960, t, K["benarfa"] - .05, -2)
        if t > K["marque"] - .05: slam_in(L, fr, stampl("MARQUE ✓", (40, 150, 70), 100), t, K["marque"] - .05, CX - 150, 1700 - 150, -8)
    else:
        foot.draw_goal(L, fr, CX, 1250, 700, 360, 0, 1, t)
        u = clamp((t - K["nkunku"])/.5); foot.draw_ball(L, fr, CX + lerp(0, 380, u), lerp(1700, 700, u) - 300*math.sin(math.pi*u), .8, t*700)
        put(L, pin_tag("NKUNKU", 60), CX, 1700 - 120, eob((t - K["nkunku"])/.25), 3)
        if K["rate"] < t < K["ans48b"] - .1: slam_in(L, fr, stampl("RATÉ !", ROUGE, 140), t, K["rate"], CX, 1050, -10)
    if t > K["ans48b"] - .1:
        dark(L, .35); u = clamp((t - K["termine"] + .05)/.35)
        lb = kword("48 ANS DE MALÉDICTION", NOIR, BLANC, 84)
        if u <= 0: lb.draw(L, fr, CX, 1100, 1, -2)
        else:
            sp = lb.v[0]; hw = sp.width//2
            for side, part in ((-1, sp.crop((0, 0, hw, sp.height))), (1, sp.crop((hw, 0, sp.width, sp.height)))):
                part.info["anchor"] = (part.width/2, part.height/2); put(L, part, CX + side*(hw/2 + 300*u), 1100 + 500*u*u, 1, side*30*u, 1 - u*.6)
            slam_in(L, fr, kword("TERMINÉS !", JAUNE, NOIR, 150), t, K["termine"], CX, 1300, -4)
            confetti(L, fr, "rcf", t - K["termine"], 110, 3, [ROUGE, NOIR, BLANC, JAUNE])
CAM_PENS = [(54.6, CX, 960, 1.0), (55.5, 500, 1150, 1.08), (58.4, 400, 1300, 1.1), (59.0, CX, 1200, 1.05), (60.0, CX, 1100, 1.0), (61.8, CX, 1150, 1.05)]

# 11. BRETAGNE : 4 clubs pros, meilleur club breton ?
CL = [("RENNES", "L1", K["rennesb"], ROUGE), ("BREST", "L1", K["brest"], ROUGE), ("LORIENT", "L1", K["lorient"], (240, 120, 30)), ("GUINGAMP", "L2", K["guinb"], NOIR)]
@scene(K["auj"], trans="tear", td=.3)
def s_bzh(L, fr, t):
    paper_fill(L, (40, 90, 150), "sea2"); d = ImageDraw.Draw(L)
    for k in range(12): d.arc([-200 + k*140, 1700 + 30*math.sin(t + k), k*140 + 100, 1800], 200, 340, fill=(80, 130, 190), width=6)
    mx, my = CX + 10, 1120
    put(L, bzh_map(), mx, my, 1.0)
    if t < K["alors"]: fx.kinetic(L, fr, t, [("3 CLUBS", K["trois"] - .05), ("EN LIGUE 1", K["l1"] - .05)], CX, 600, lambda x, i: kword(x, JAUNE if i else NOIR, NOIR if i else BLANC, 100))
    for i, (nm, lg, t0, col) in enumerate(CL):
        if t < t0 - .05: continue
        cx_, cy_ = CITIES[nm]; x, y = mx - 500 + cx_, my - 370 + cy_
        u = clamp((t - t0 + .05)/.2); ImageDraw.Draw(L).line([(x, y - 60*(1 - u)), (x, y - 70)], fill=(60, 60, 60), width=6)
        d.ellipse([x - 22, y - 92 - 400*(1 - u), x + 22, y - 48 - 400*(1 - u)], fill=ROUGE, outline=NOIR, width=3)
        blink = 1.15 if t > K["alors"] and int((t - K["alors"])*3) % 4 == i else 1.0
        tag(f"{nm} · {lg}", 44, col if col != NOIR else NOIR, BLANC).draw(L, fr, x + (90 if nm != "RENNES" else -60), y + 60 + (i % 2)*20, eob((t - t0)/.25)*blink, (-3, 2, -2, 3)[i])
    if t > K["alors"]:
        fx.kinetic(L, fr, t, [("LE MEILLEUR", K["meilleur"] - .05), ("CLUB BRETON ?", K["breton"] - .05)], CX, 600, lambda x, i: kword(x, JAUNE if i else NOIR, NOIR if i else BLANC, 104))
    if t > K["dis"] - .05:
        fx.wipe(L, fr, marker("DIS-LE EN COMMENTAIRE", "rcom", 76), CX, 1520, t, K["dis"] - .05, 2)
CAM_BZH = [(61.8, CX, 1000, 1.0), (63.9, 800, 1050, 1.12), (64.4, 260, 1050, 1.12), (65.4, 520, 1000, 1.12), (66.3, CX, 1000, 1.0), (72, CX, 1000, 1.04)]

SC.sort(key=lambda s: s["t0"])
CAMS = {"s_hook": CAM_HOOK, "s_cat": CAM_CAT, "s_1901": CAM_1901, "s_1929": CAM_1929, "s_pokou": CAM_POKOU, "s_cups": CAM_CUPS,
        "s_quiz": CAM_QUIZ, "s_guingamp": CAM_GUIN, "s_cama": CAM_CAMA, "s_final": CAM_FINAL, "s_pens": CAM_PENS, "s_bzh": CAM_BZH}
PUNCH += [K["sixzero"] + .5, K["ans48"], K["maudit"], K["sz2"] + .6, K["porte"], K["centaine"], K["pele"], K["y71"], K["abonne"] + .25, K["like"],
          K["guin1"] + .3, K["l2"], K["brule"], K["eduardo"], K["deuxdeux"], K["expulse"], K["marque"], K["rate"], K["termine"]]
SHAKES = PUNCH
CAMS = {k: [(m(a[0]),) + tuple(a[1:]) for a in v] for k, v in CAMS.items()}
CAMS["s_cat"] = [(0, CX, 960, 1.08), (K["maudit"], CX, 900, 1.12), (2.25, CX, 960, 1.0)]
# ------------------------------------------------------------------ rendu d'une scène + transitions
def render_scene(i, fr, t):
    s = SC[i]; L = Image.new("RGBA", s["size"], (0, 0, 0, 255)); s["fn"](L, fr, t)
    cx, cy, z = camk(CAMS[s["name"]], t); z *= punch(t)
    return apply_cam(L, cx + 4*math.sin(t*.9), cy + 3*math.cos(t*.7), z, .35*math.sin(t*.6)).convert("RGB")
def scene_at(t):
    k = 0
    for i, s in enumerate(SC):
        if t >= s["t0"]: k = i
    return k
def frame(fr, t):
    k = scene_at(t); s = SC[k]; cur = render_scene(k, fr, t)
    u = (t - s["t0"])/s["td"] if k else 1
    if u < 1:
        prev = render_scene(k - 1, fr, t); tr = s["trans"]; e = ease(u)
        if tr in ("whip", "whip_up"):
            vert = tr == "whip_up"; off = int((W if not vert else H)*e)
            out = Image.new("RGB", (W, H))
            if vert: out.paste(prev, (0, off)); out.paste(cur, (0, off - H))
            else: out.paste(prev, (-off, 0)); out.paste(cur, (W - off, 0))
            fx.whip_blur(out, 0 if vert else -90*math.sin(math.pi*u), 90*math.sin(math.pi*u) if vert else 0, 6); cur = out
        elif tr == "zoom_through":
            z = 1 + 2.2*e; bw, bh = W/z, H/z
            p2 = prev.crop((int(CX - bw/2), int(1110 - bh/2), int(CX + bw/2), int(1110 + bh/2))).resize((W, H), Image.BICUBIC)
            cur = Image.blend(p2, cur, clamp((u - .35)/.65))
        elif tr == "tear": tear_transition(cur, prev, u, "tear_v", k);
        elif tr == "fade": cur = Image.blend(prev, cur, e)
        elif tr == "flash":
            cur = Image.blend(prev, cur, 1.0 if u > .5 else 0.0); cur = Image.blend(cur, Image.new("RGB", (W, H), (255, 250, 236)), max(0, 1 - abs(u - .5)*2.2))
        elif tr == "glitch":
            cur = (cur if u > .5 else prev).copy(); rgb_split(cur, 20*(1 - abs(u - .5)*2), fr, 8)
    pass
    for p in SHAKES:
        if p < t < p + .3:
            a = 14*(1 - (t - p)/.3); cur = ImageChops.offset(cur, int(a*math.sin(t*90)), int(a*math.cos(t*70)))
    fx.dust(cur, t, 24)
    cur = cur.convert("RGBA"); fx.vignette(cur, 90); fil_rouge(cur, fr, t)
    return cur.convert("RGB")

def draw(cv, fr, t, T):
    tv = max(0.0, t - PAD_IN); cv.paste(frame(fr, tv), (0, 0))


# ------------------------------------------------------------------ sons
P = PAD_IN
V5S = os.path.join(ROOT, "episodes", "lille_v5", "sfx"); RS = os.path.join(HERE, "sfx"); BANK = os.path.join(ROOT, "assets", "sfx")
def X(t, name, g): return (P + m(t), name, g)            # temps de voix.mp3 -> voix_hook.mp3
def XN(t, name, g): return (P + t, name, g)
SFX = [X(0, "braam", .75)] + [X(K0["sixzero"] + i*.1, "flap", .5) for i in range(6)] + [X(K0["sixzero"] + .65, "stamp", .65),
       X(K0["attendu"], "wind", .45), X(K0["ans48"], "tictac", .35), XN(2.23, "whoosh1", .5), XN(.05, "paws", .45), X(K0["maudit"], "thunder", .5),
       X(6.88, "page_tear", .5), X(6.92, "stamp", .55), X(K0["etudiants"], "typewriter", .35), X(K0["stade"], "pop", .5)] + \
      [X(K0["sz2"] - .1 + i*.12, "tok", .45) for i in range(6)] + [X(K0["adv"], "groan", .4), X(11.88, "whoosh2", .5), X(11.92, "stamp", .55),
       X(K0["claque"], "doorslam", .85), X(K0["pendant3"], "tictac", .4), X(15.2, "tictac", .35), X(K0["centaine"], "stamp", .75),
       X(K0["an70"] - .05, "flashfx", .45), X(17.4, "crowd", .35)] + [X(17.6 + k*.9, "touch", .45) for k in range(5)] + [
       X(K0["ivoirien"], "pop", .45), X(K0["pokou"], "pin", .5), X(K0["pele"], "shimmer", .6), X(K0["pele"] + .3, "sparkle", .45),
       X(22.28, "whoosh3", .5), X(K0["y65"] + .12, "tok", .65), X(K0["y71"] + .12, "tok", .65), X(K0["rien"], "wind", .5), X(K0["p48"], "heart", .4),
       X(26.8, "glitch", .45), X(26.85, "typewriter", .35), X(K0["quel"], "riser", .4), X(K0["rq"], "stamp", .45), X(K0["reponds"], "marker", .45),
       X(K0["abonne"] + .25, "pop", .6), X(K0["abonne"] + .3, "ding", .4), X(K0["like"], "sparkle", .5), X(K0["like"] + .05, "pop", .5), X(K0["chaine"], "notif", .45),
       X(34.48, "whoosh1", .5)] + [X(K0["guin1"] + d_, "flap", .45) for d_ in (-.3, 0, .3)] + [X(K0["l2"], "stamp", .65), X(K0["y2014"] - .1, "page_tear", .45),
       X(K0["refinale"], "flap", .45), X(K0["refinale"] + .4, "flap", .45), X(K0["reguin"], "tractor", .45), X(K0["reguin"] - .05, "stamp", .55),
       X(40.08, "page_tear", .5), X(K0["centre"], "typewriter", .35), X(K0["camp"], "pop", .4), X(K0["maison"], "pop", .4), X(K0["brule"], "fire", .55),
       X(K0["pro"], "stamp", .7), X(K0["eduardo"] - .1, "camera", .6), X(K0["cama"], "marker", .4),
       X(47.58, "whoosh3", .5), X(K0["y2019"], "stamp", .5), X(48.0, "crowd", .4), X(K0["neymar"], "pin", .45), X(K0["mbappe"], "pin", .45),
       X(K0["deuxzero"] - .15, "flap", .5), X(K0["deuxzero"] + .15, "flap", .5), X(K0["revient"], "flap", .55), X(K0["revient"] + .05, "crowd", .4),
       X(K0["deuxdeux"], "flap", .6), X(K0["deuxdeux"] + .05, "goal_roar", .5), X(K0["expulse"] - .2, "whistle", .5), X(K0["expulse"], "stamp", .7),
       X(K0["tab"] - .02, "flashfx", .45)] + [XN(t0, "kick", .4) for t0, _ in PEN_R + PEN_P[:5]] + [
       X(K0["placard"] - .3, "creak", .5), X(K0["benarfa"], "camera", .5), X(K0["marque"], "net", .55), X(K0["marque"] + .05, "crowd", .4),
       X(K0["nkunku"], "kick", .7), X(K0["rate"], "groan", .5), X(K0["rate"] + .05, "stamp", .7), X(K0["termine"] - .05, "page_tear", .7),
       X(K0["termine"], "boom", .8), X(K0["termine"] + .05, "goal_roar", .6), X(K0["termine"] + .3, "champagne", .45),
       X(61.78, "page_tear", .5), X(K0["trois"], "stamp", .45)] + [XN(t0, "pin", .55) for _, _, t0, _ in CL] + [
       X(K0["alors"], "riser", .4), X(K0["breton"], "stamp", .5), X(K0["dis"], "notif", .55), X(K0["comm"] + .6, "bell", .4)]
SFX_DIR = "/tmp/claude-0/sfx_rennes"
os.makedirs(SFX_DIR, exist_ok=True)
for nm in set(n for _, n, _ in SFX):
    src = next((p for p in (os.path.join(RS, nm + ".mp3"), os.path.join(V5S, nm + ".mp3"), os.path.join(BANK, nm + ".mp3")) if os.path.exists(p)), None)
    if nm in ("crowd", "whistle"): src = os.path.join(BANK, nm + ".mp3")
    dst = os.path.join(SFX_DIR, nm + ".mp3")
    if src and not os.path.lexists(dst): os.symlink(src, dst)
SFX = [s for s in SFX if os.path.exists(os.path.join(SFX_DIR, s[1] + ".mp3"))]
SFX = fx.sfx_variants(SFX, SFX_DIR, SFX_DIR + "_v")
SCENES = [Scene("rennes", TEXTE, draw, SFX, pad_in=P, pad_out=1.6)]

def stills(out, only=None):
    os.makedirs(out, exist_ok=True); ts = []
    for i, s in enumerate(SC):
        if only and s["name"] != only: continue
        t1 = SC[i + 1]["t0"] if i + 1 < len(SC) else 69.5; n = 4 if not only else 8
        ts += [s["t0"] + (t1 - s["t0"])*(k + .5)/n for k in range(n)]
    ims = []
    for t in ts:
        cv = Image.new("RGB", (W, H)); cv.paste(frame(int(t*FPS), t)); ims.append(cv.resize((216, 384)))
    cols = 10; rows = (len(ims) + cols - 1)//cols; sheet = Image.new("RGB", (216*cols, 414*rows), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        x, y = (k % cols)*216, (k//cols)*414; sheet.paste(im, (x, y + 30)); dd.text((x + 6, y + 4), f"{ts[k]:.2f}s", font=font("mono", 22), fill=(230, 230, 230))
    p = os.path.join(out, f"rsheet{'_' + only if only else ''}.jpg"); sheet.save(p, quality=82); return p

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--stills" in args:
        only = args[args.index("--stills") + 1] if len(args) > args.index("--stills") + 1 else None
        print(stills("/tmp/claude-0/aud", only)); sys.exit()
    out = args[0] if args else os.path.join(ROOT, "output", SLUG); os.makedirs(out, exist_ok=True)
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=[VOIX], sfx_dir=SFX_DIR + "_v", sfx_db=6.0, lufs=-14.0, crf=22, limit=True))
