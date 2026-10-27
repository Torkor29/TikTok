"""SAINT-ÉTIENNE v3 — « le club le plus fou de France » (≈ 79 s), process Rennes (TEXTE.md, SCRIPT.md), DA papercraft 3D.
Hook caisse noire, fil rouge « ★ TITRES » + date, CTA quiz au milieu (réponse jamais donnée), question finale « Sainté ou Lyon ».
Moteur/assets repris de episodes/rennes/rennes3.py ; photos fournies (assets/photos/asse) en papier découpé.

  python3 episodes/asse3/asse3.py --stills [scene]
  python3 episodes/asse3/asse3.py
"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RENNES = os.path.join(ROOT, "episodes", "rennes")
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "brest_ldc"))
sys.path.insert(0, os.path.join(ROOT, "episodes", "lille_v5")); sys.path.insert(0, RENNES)
from quiz import *
import foot, fx
from brest_ldc import marker
from rgfx import *
from PIL import ImageChops
import pc_over; pc_over.install(globals())
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
from paper_cut import paper_player

TITLE = "~/histoires $ ./saint-etienne"
SLUG = "asse_v4"
VOIX = os.path.join(HERE, "voix_clone", "voix.mp3")            # voix Léo, blancs coupés (scripts/trim_blancs.py)
TEXTE = open(os.path.join(HERE, "TEXTE.md")).read()
# temps clés (s) relevés dans mots.json
K = dict(president=.24, joueurs=1.2, cachette=1.58, condamne=2.92, justice=3.78, voici=4.48, fou=5.92, france0=6.3, saint=6.92,
         y1919=8.24, employes=9.26, casino=10.2, maillot=11.76, vert=12.46, magasin=13.56,
         y1958=14.24, mekh=15.9, disparait=16.86, nuit=17.68, secret=18.7, fln=19.56, ans4=20.7, revient=21.7, titres=22.98,
         y1967=24.4, keita=25.52, mali=26.52, personne=27.0, aeroport=27.98, taxi=29.22, km=30.64, club=32.42, paye=32.86,
         question=33.72, quel=35.06, buteur=35.48, arsenal=36.04, barca=36.68, explose=37.28, reponds=38.88, abonne=40.04, like=40.78, chaine=42.44,
         y1976=43.4, zd=44.4, kiev=45.06, retour=45.68, explose2=46.58, tz=47.56, devient=49.28, chaudron=49.74,
         y1981=50.72, dixieme=51.82, platini=53.3, personne2=54.54,
         y1982=56.12, scandale=57.14, caisse=58.0, m20=58.88, caches=59.96, payer=60.5, president2=61.82, rocher=62.16, tombe=62.86, club2=63.76,
         y2022=64.72, descente=65.82, tab=66.8, supporters=67.7, envahissent=68.0, fumi=69.48, sanction=71.34,
         y2024=72.28, milliard=73.34, canadien=73.82, rachete=74.32, toi=75.4, stet=76.0, lyon=76.66, vrai=77.6, region=78.36, dis=78.92, END=80.8)
# v4 : voix clonée de l'utilisateur + musique 129 BPM (premier temps à 0,07 s) -> on cale les CHANGEMENTS DE SCÈNE sur le temps le plus proche
MUS_BPM, MUS_T0 = 129.2, .07
def snap(t): b = 60/MUS_BPM; return MUS_T0 + round((t - MUS_T0)/b)*b
for _k in ("voici", "y1919", "y1958", "y1967", "question", "y1976", "y1981", "y1982", "y2022", "y2024", "toi"): K[_k] = snap(K[_k] - .1)
def m(t): return t
K0 = dict(K)
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
LOGO = {}
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
def punch(t): return 1 + sum((.06 if p in IMPACT_SET else .03)*math.exp(-((t - p)/.09)**2) for p in PUNCH if p - .4 < t < p + .5)
IMPACT_SET = set()

# ================================================================== SCÈNES (t = temps voix)
SC = []
def scene(t0, size=(W, H), trans="cut", td=.3):
    def deco_(fn): SC.append(dict(t0=t0, fn=fn, size=size, trans=trans, td=td, name=fn.__name__)); return fn
    return deco_

# ------------------------------------------------------------------ fil rouge : années sans trophée + date

# ================================================================== v2 : système de mouvement (engine/motion.py, MOTION.md)
import motion as M
from motion import El, words, walk, arc, ground_shadow

def KW(txt, bg=NOIR, fg=BLANC, size=118): return kword(txt, bg, fg, size)

# ------------------------------------------------------------------ fil rouge : compteur « ANS SANS TROPHÉE »
def drought(t):
    if t < K["rien"]: return None
    if t < K["p48"]: return max(1, int(48*M.ease_out((t - K["rien"])/.7)))
    if t < K["termine"]: return 48
    return 0
DATES = [(0, "")] + [(m(a), b) for a, b in ((6.9, "1901"), (11.9, "1929"), (17.2, "1974"), (22.3, "1965"), (24.5, "1971"), (34.5, "2009"),
         (37.8, "2014"), (40.1, "2005"), (47.6, "2019"), (61.8, "2026"))]
def fil_rouge(cv, fr, t):
    if K["question"] - .2 < t < K["y2009"]: return
    cur = [d for d in DATES if t >= d[0]][-1]
    if cur[1]:
        s = .6 + .4*M.spring(t - cur[0], .45, 16)
        mono(cur[1], 46, NOIR).draw(cv, fr, 150, 262, s, -3)
    n = drought(t)
    if n is not None and t < K["auj"] + .6:
        if n: LBL(f"{n} ANS SANS TROPHÉE", f"rdr{n}", font("title", 38), BLANC, ROUGE, padx=14, pady=5, rough=2).draw(cv, fr, 560, 262, 1, 2)
        else:
            s = M.spring(t - K["termine"], .4, 14)
            LBL("MALÉDICTION BRISÉE", "rdrok", font("title", 38), BLANC, (40, 150, 70), padx=14, pady=5, rough=2).draw(cv, fr, 560, 262, max(.05, s), 2)

# ------------------------------------------------------------------ assets animés
def draw_cat(L, x, y, t, s=1.0, moving=True, face=1):
    """Chat noir en papier avec vrai cycle de marche (4 pattes en opposition), queue qui ondule, liseré clair (lisible sur fond sombre)."""
    c, rim = (16, 14, 18), (120, 110, 130)
    lay = Image.new("RGBA", (520, 360), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); ox, oy = 260, 300
    ph = t*11 if moving else 0; bob = -5*abs(math.sin(ph)) if moving else 2*math.sin(t*2)
    def leg(hx, phase):
        a = math.radians(26*math.sin(ph + phase)) if moving else 0
        x2, y2 = hx + 70*math.sin(a), oy - 10 + bob*0 + 70*math.cos(a) - 70
        for col, w_ in ((rim, 26), (c, 20)): d.line([(hx, oy - 80 + bob), (x2, oy - 10)], fill=col, width=w_)
    for hx, phs in ((ox - 90, 0), (ox + 70, math.pi)): leg(hx, phs + .4)                      # pattes arrière-plan
    tail = [(ox - 120 + -26*k, oy - 110 + bob - 18*k + 14*math.sin(t*5 + k*.8)) for k in range(6)]
    for col, w_ in ((rim, 26), (c, 20)): d.line(tail, fill=col, width=w_, joint="curve")
    for col, g in ((rim, 4), (c, 0)):
        d.ellipse([ox - 140 - g, oy - 170 + bob - g, ox + 110 + g, oy - 70 + bob + g], fill=col)
        hx, hy = ox + 120, oy - 190 + bob
        d.ellipse([hx - 58 - g, hy - 52 - g, hx + 58 + g, hy + 52 + g], fill=col)
        d.polygon([(hx - 50, hy - 30), (hx - 40 - g, hy - 92 - g), (hx - 8, hy - 44)], fill=col); d.polygon([(hx + 50, hy - 30), (hx + 40 + g, hy - 92 - g), (hx + 8, hy - 44)], fill=col)
    for hx_, phs in ((ox - 70, math.pi), (ox + 90, 0)): leg(hx_, phs)                         # pattes avant-plan
    blink = (int(t*10) % 37) == 0
    for ex in (hx - 22, hx + 22):
        if blink: d.line([(ex - 10, hy - 4), (ex + 10, hy - 4)], fill=(250, 220, 60), width=4)
        else: d.ellipse([ex - 11, hy - 15, ex + 11, hy + 7], fill=(250, 220, 60)); d.ellipse([ex - 3, hy - 13, ex + 3, hy + 5], fill=c)
    lay.info["anchor"] = (ox, oy)
    if face < 0: lay = lay.transpose(Image.FLIP_LEFT_RIGHT); lay.info["anchor"] = (520 - ox, oy)
    blit_sxy(L, lay, x, y, s, s, 0)

pc_over.install(globals()); pc_over.install_v4(globals())
_fc = {}
def flip_card(v, size):
    k = (v, size)
    if k not in _fc:
        w_, h_ = int(size*.82), int(size*1.12); im = Image.new("RGBA", (w_, h_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, w_ - 1, h_ - 1], 14, fill=(18, 18, 22)); d.rounded_rectangle([0, 0, w_ - 1, h_//2], 14, fill=(26, 26, 32))
        text_c(d, w_/2, h_/2, str(v), font("title", size), (252, 252, 246)); d.line([(0, h_//2), (w_, h_//2)], fill=(8, 8, 10), width=5)
        _fc[k] = im
    return _fc[k]
def flip_digit(L, x, y, v, t, tc, prev, size=150):
    """Vraie palette : la moitié haute de l'ancien chiffre bascule vers le bas et découvre le nouveau (0,22 s)."""
    new, old = flip_card(v, size), flip_card(prev, size); w_, h_ = new.size; x0, y0 = int(x - w_/2), int(y - h_/2)
    u = clamp((t - tc)/.22) if t >= tc else 1
    if u >= 1: L.alpha_composite(new, (x0, y0)); return
    L.alpha_composite(new.crop((0, 0, w_, h_//2)), (x0, y0)); L.alpha_composite(old.crop((0, h_//2, w_, h_)), (x0, y0 + h_//2))
    if u < .5:
        f = old.crop((0, 0, w_, h_//2)); hh = max(1, int(h_//2*math.cos(math.pi*u))); f = f.resize((w_, hh))
        L.alpha_composite(f, (x0, y0 + h_//2 - hh))
    else:
        f = new.crop((0, h_//2, w_, h_)); hh = max(1, int(h_//2*-math.cos(math.pi*u))); f = f.resize((w_, hh))
        L.alpha_composite(f, (x0, y0 + h_//2))
def scoreboard(L, x, y, t, seq, left, right, size=150, s_in=1.0):
    if s_in <= .02: return
    put(L, board_base(860, 330, left, right), x, y - 30, s_in)
    if s_in < .95: return
    A, B, pA, pB, tA, tB = 0, 0, 0, 0, -9, -9
    for (ti, a, b) in seq:
        if t >= ti:
            if a != A: pA, A, tA = A, a, ti
            if b != B: pB, B, tB = B, b, ti
    flip_digit(L, x - 210, y, A, t, tA, pA, size); flip_digit(L, x + 210, y, B, t, tB, pB, size)
    ImageDraw.Draw(L).rounded_rectangle([x - 36, y - 10, x + 36, y + 10], 6, fill=(250, 220, 120))
def board_in(t, t0, t1=None):
    v = M.spring(t - t0, .5, 12)
    if t1 is not None and t > t1: v *= 1 - M.ease_in((t - t1)/.2)
    return v
def ball(L, fr, x, y, s, t, ground=None):
    if ground is not None: ground_shadow(L, x, ground, 40*s*max(.3, 1 - (ground - y)/900), .3)
    foot.draw_ball(L, fr, x, y, s, t*520)
def cursor():
    if "cur" not in _fc:
        im = Image.new("RGBA", (140, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        pts = [(10, 10), (10, 150), (48, 112), (74, 176), (100, 164), (74, 102), (124, 102)]
        d.polygon([(x + 6, y + 6) for x, y in pts], fill=(0, 0, 0, 90)); d.polygon(pts, fill=BLANC, outline=NOIR); d.line(pts + [pts[0]], fill=NOIR, width=6)
        im.info["anchor"] = (10, 10); _fc["cur"] = im
    return _fc["cur"]
def puffs(L, t, t0, x, y, n=10, col=(210, 196, 170), spread=260, dur=.6):
    u = (t - t0)/dur
    if not 0 < u < 1: return
    d = ImageDraw.Draw(L)
    for k in range(n):
        a = math.pi*(k + .5)/n; r_ = spread*M.ease_out(u); rr = 26*(1 - u) + 6
        d.ellipse([x + r_*math.cos(a) - rr, y - r_*.35*math.sin(a) - rr, x + r_*math.cos(a) + rr, y - r_*.35*math.sin(a) + rr], fill=col)
def sparks_burst(L, t, t0, x, y, n=12, col=(255, 230, 120), dist=220):
    u = (t - t0)/.45
    if not 0 < u < 1: return
    d = ImageDraw.Draw(L)
    for k in range(n):
        a = 2*math.pi*k/n; r0, r1 = dist*M.ease_out(u)*.6, dist*M.ease_out(u)
        d.line([(x + r0*math.cos(a), y + r0*math.sin(a)), (x + r1*math.cos(a), y + r1*math.sin(a))], fill=col, width=max(2, int(10*(1 - u))))

CREST = lambda h: shadowed(sticker("asse", h), ("crest", h))
VERT, VERT2, VFONCE = (22, 120, 62), (40, 150, 80), (10, 52, 30)
PH = os.path.join(ROOT, "assets", "photos", "asse")
_cut = {}
def CUT(n, h=900):
    k = (n, h)
    if k not in _cut: _cut[k] = paper_player(os.path.join(PH, n + ".png"), (0, 0, 1086, 1448), h)
    return _cut[k]
def bnote():
    """Billet de banque papier (francs)."""
    if "bn" not in _fc:
        im = Image.new("RGBA", (260, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([4, 4, 255, 135], 10, fill=(196, 214, 170), outline=(70, 100, 60), width=5)
        d.ellipse([90, 30, 170, 110], outline=(70, 100, 60), width=5); text_c(d, 130, 70, "F", font("title", 56), (70, 100, 60))
        text_c(d, 40, 30, "500", font("mono", 22), (70, 100, 60)); text_c(d, 220, 110, "500", font("mono", 22), (70, 100, 60))
        im.info["anchor"] = (130, 70); _fc["bn"] = im
    return _fc["bn"]
def money_rain(L, t, t0, n=22, dur=9.0, y0=-200, speed=520):
    if t < t0: return
    for k in range(n):
        tt = t - t0 - k*.11
        if tt < 0: continue
        x = (k*173 + 90) % W + 60*math.sin(tt*2 + k); y = y0 + speed*tt*(.8 + (k % 4)*.12)
        if y < H + 200: put(L, bnote(), x, y, .75 + (k % 3)*.15, 30*math.sin(tt*3 + k))
def smoke(L, t, x, y, col, n=8, spread=260, rise=420, a=150):
    ov = Image.new("RGBA", L.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for k in range(n):
        u = ((t*.35 + k/n) % 1); r_ = 80 + 220*u; xx = x + spread*math.sin(k*2.1 + t*.5)*u; yy = y - rise*u
        d.ellipse([xx - r_, yy - r_, xx + r_, yy + r_], fill=col + (int(a*(1 - u)),))
    L.alpha_composite(ov.filter(ImageFilter.GaussianBlur(18)))
def shop():
    if "shop" not in _fc:
        w_, h_ = 760, 620; im = Image.new("RGBA", (w_, h_ + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle([20, 120, w_ - 20, h_], fill=(232, 220, 196), outline=NOIR, width=6)
        d.rectangle([0, 40, w_, 150], fill=VERT, outline=NOIR, width=6); text_c(d, w_/2, 95, "CASINO", font("title", 92), BLANC)
        for k in range(8): d.polygon([(k*w_/8, 150), ((k + 1)*w_/8, 150), ((k + .5)*w_/8, 220)], fill=VERT if k % 2 else BLANC, outline=NOIR)
        d.rectangle([90, 290, 330, h_ - 10], fill=(150, 196, 214), outline=NOIR, width=6); d.rectangle([430, 290, 670, h_], fill=(110, 70, 40), outline=NOIR, width=6)
        d.text((110, 300), "ÉPICERIE", font=font("mono", 30), fill=NOIR)
        im.info["anchor"] = (w_/2, h_); _fc["shop"] = shadowed(im, "shopS")
    return _fc["shop"]
def flag_dz(L, x, y, t, s=1.0):
    w_, h_ = int(420*s), int(280*s); im = Image.new("RGBA", (w_, h_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w_//2, h_], fill=(0, 122, 61)); d.rectangle([w_//2, 0, w_, h_], fill=BLANC)
    cx, cy, r = w_/2, h_/2, h_*.3; d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(210, 16, 52)); d.ellipse([cx - r*.68, cy - r*.8, cx + r*1.0, cy + r*.8], fill=None)
    d.ellipse([cx - r*.55, cy - r*.85, cx + r*1.05, cy + r*.85], fill=(0, 122, 61)); d.rectangle([w_//2, 0, w_, h_], fill=None)
    d.ellipse([cx - r*.55 + 0, cy - r*.85, cx + r*1.05, cy + r*.85], fill=None)
    # croissant : on repeint la moitié droite du masque en blanc
    mask = Image.new("L", (w_, h_), 0); md = ImageDraw.Draw(mask); md.ellipse([cx - r*.55, cy - r*.85, cx + r*1.05, cy + r*.85], fill=255); md.rectangle([0, 0, w_//2, h_], fill=0)
    im.paste((255, 255, 255, 255), (0, 0), mask)
    pts = [(cx + r*.55 + r*.28*math.cos(math.pi/2 + k*4*math.pi/5), cy - r*.28*math.sin(math.pi/2 + k*4*math.pi/5)) for k in range(5)]; d.polygon(pts, fill=(210, 16, 52))
    d.rectangle([0, 0, w_ - 1, h_ - 1], outline=NOIR, width=5); im.info["anchor"] = (0, h_/2)
    d2 = ImageDraw.Draw(L); d2.line([(x, y - 40), (x, y + 560*s)], fill=(90, 70, 50), width=int(14*s))
    blit_sxy(L, im, x, y + h_/2, 1, 1 + .03*math.sin(t*5), 2*math.sin(t*3))
def flag_ca(L, x, y, t, s=1.0):
    w_, h_ = int(440*s), int(220*s); im = Image.new("RGBA", (w_, h_), (0, 0, 0, 0)); d = ImageDraw.Draw(im); R = (216, 30, 40)
    d.rectangle([0, 0, w_, h_], fill=BLANC); d.rectangle([0, 0, w_//4, h_], fill=R); d.rectangle([3*w_//4, 0, w_, h_], fill=R)
    cx, cy, k_ = w_/2, h_/2, h_/230
    leaf = [(0, -95), (14, -62), (34, -70), (28, -18), (60, -48), (66, -32), (92, -38), (80, -4), (96, 6), (52, 40), (58, 60), (8, 52), (6, 95), (-6, 95), (-8, 52), (-58, 60), (-52, 40), (-96, 6), (-80, -4), (-92, -38), (-66, -32), (-60, -48), (-28, -18), (-34, -70), (-14, -62)]
    d.polygon([(cx + px*k_, cy + py*k_) for px, py in leaf], fill=R); d.rectangle([0, 0, w_ - 1, h_ - 1], outline=NOIR, width=5)
    im.info["anchor"] = (w_/2, h_/2); blit_sxy(L, im, x, y, 1, 1 + .03*math.sin(t*5), 2*math.sin(t*3))
def taxi(L, x, y, s=1.0, t=0):
    w_, h_ = 520, 260; im = Image.new("RGBA", (w_, h_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 100, w_ - 10, 200], 30, fill=(30, 30, 34), outline=NOIR, width=6)
    d.polygon([(110, 104), (170, 30), (360, 30), (420, 104)], fill=(30, 30, 34), outline=NOIR); d.polygon([(140, 100), (186, 46), (258, 46), (258, 100)], fill=(170, 206, 226)); d.polygon([(272, 100), (272, 46), (346, 46), (392, 100)], fill=(170, 206, 226))
    d.rounded_rectangle([220, 6, 310, 34], 6, fill=(250, 220, 60), outline=NOIR, width=3); text_c(d, 265, 20, "TAXI", font("mono", 20), NOIR)
    d.rectangle([w_ - 40, 120, w_ - 14, 140], fill=(255, 230, 140)); d.rectangle([14, 120, 34, 140], fill=(220, 40, 40))
    for wx in (120, 400):
        d.ellipse([wx - 46, 154, wx + 46, 246], fill=NOIR); d.ellipse([wx - 20, 180, wx + 20, 220], fill=(170, 170, 170))
        a = t*14; d.line([(wx, 200), (wx + 18*math.cos(a), 200 + 18*math.sin(a))], fill=NOIR, width=5)
    im.info["anchor"] = (w_/2, 246); blit_sxy(L, im, x, y, s, s, 1.5*math.sin(t*18))
def safe_box(L, x, y, s, t, open_=0):
    w_, h_ = 520, 440; im = Image.new("RGBA", (w_, h_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w_ - 1, h_ - 1], 24, fill=(22, 22, 26), outline=(90, 90, 100), width=8)
    d.rounded_rectangle([40, 40, w_ - 40, h_ - 40], 16, outline=(70, 70, 80), width=6)
    d.ellipse([w_/2 - 70, h_/2 - 70, w_/2 + 70, h_/2 + 70], fill=(60, 60, 70), outline=(140, 140, 150), width=6)
    for k in range(8): a = t*.8 + k*math.pi/4; d.line([(w_/2, h_/2), (w_/2 + 60*math.cos(a), h_/2 + 60*math.sin(a))], fill=(140, 140, 150), width=4)
    text_c(d, w_/2, h_ - 20, "", font("mono", 10), BLANC); im.info["anchor"] = (w_/2, h_/2)
    put(L, shadowed(im, ("safe", int(t*20) % 9)), x, y, s, 2*math.sin(t*2))
def photo(path, h=760):
    k = ("ph", path, h)
    if k not in _fc:
        im = Image.open(path).convert("RGB"); im.thumbnail((h*2, h)); _fc[k] = shadowed(photo_card(path, (0, 0, Image.open(path).width, Image.open(path).height), h), k)
    return _fc[k]
import pc_lib as _PL
_PL.KITS["asse"] = dict(c1=(22, 120, 62), sleeve=(22, 120, 62), shorts=(250, 248, 240), socks=(22, 120, 62), trim=(250, 248, 240), kind="plain")
foot.KITS["asse"] = dict(kind="plain", c1=VERT, sleeve=VERT, shorts=(250, 250, 246), socks=VERT, trim=(250, 250, 246))
foot.KITS["kiev"] = dict(kind="plain", c1=(250, 250, 246), sleeve=(250, 250, 246), shorts=(30, 70, 160), socks=(250, 250, 246), trim=(30, 70, 160))

# ------------------------------------------------------------------ fil rouge : date + titres
DATES = [(0, ""), (K["y1919"], "1919"), (K["y1958"], "1958"), (K["y1967"], "1967"), (K["y1976"], "1976"), (K["y1981"], "1981"), (K["y1982"], "1982"),
         (K["y2022"], "2022"), (K["y2024"], "2024"), (K["toi"], "")]
TIT = {"1919": 0, "1958": 1, "1967": 3, "1976": 9, "1981": 10, "1982": 10, "2022": 10, "2024": 10}
def fil_rouge(cv, fr, t):
    if K["question"] - .2 < t < K["y1976"] or t < K["y1919"]: return
    cur = [d for d in DATES if t >= d[0]][-1]
    if not cur[1]: return
    s = .6 + .4*M.spring(t - cur[0], .45, 16)
    mono(cur[1], 46, NOIR).draw(cv, fr, 150, 262, s, -3)
    n = TIT[cur[1]]
    if cur[1] == "1981": n = 9 if t < K["dixieme"] else 10
    LBL(f"★ {n} TITRE{'S' if n > 1 else ''}", f"atit{n}", font("title", 38), BLANC, VERT, padx=14, pady=5, rough=2).draw(cv, fr, 470, 262, 1, 2)

def stripes_bg(L, a=(196, 22, 32), b=(26, 24, 28), w_=140, key="rs", t=0):
    paper_fill(L, a, key); d = ImageDraw.Draw(L); off = (t*40) % (2*w_)
    for x in range(-H - 2*w_, L.width + 2*w_, 2*w_): d.polygon([(x + off, 0), (x + w_ + off, 0), (x + w_ + H*.35 + off, L.height), (x + H*.35 + off, L.height)], fill=b)
def green_bg(L, key, t, a=VERT, b=VFONCE):
    stripes_bg(L, a, b, 150, key, t)

# --- 0. HOOK : il payait ses joueurs en cachette
E_H = words(lambda w, i: KW(w, ROUGE if w == "EN CACHETTE" else NOIR, BLANC, 104), [("IL PAYAIT", -.3), ("SES JOUEURS", K["joueurs"] - .05),
            ("EN CACHETTE", K["cachette"] - .05)], CX, 560, maxw=900, out=K["voici"] - .15) + \
      [El(stampl("CONDAMNÉ", ROUGE, 150), CX, 1500, K["condamne"] - .05, K["voici"] - .15, "stamp", "fly", rot=-8)]
@scene(0.0)
def s_hook(L, fr, t):
    paper_fill(L, (14, 30, 20), "hook"); rays(L, (CX, 1100), t, .9, 14, 1700, (30, 80, 46), .1, .3)
    money_rain(L, t, -.4, 16, speed=600)
    u = M.spring(t + .2, .5, 11); put(L, CUT("rocher", 1050), CX + 40, lerp(2600, 1920, u), 1, -2 + 1.5*math.sin(t*2))
    if t > K["cachette"] - .1:                                   # enveloppe glissée en douce
        v = clamp((t - K["cachette"] + .1)/.5); put(L, bnote(), lerp(CX - 300, CX + 260, M.ease_io(v)), 1400 - 120*math.sin(math.pi*v), 1.3, -10)
    if t > K["condamne"] - .1:                                   # barreaux de prison qui tombent
        u = M.ease_out(clamp((t - K["condamne"] + .1)/.25)); d = ImageDraw.Draw(L)
        for k in range(7): x = 110 + k*145; d.rectangle([x - 14, -40 + (u - 1)*1600, x + 14, (u - 1)*1600 + H], fill=(40, 40, 46), outline=(110, 110, 120), width=3)
    M.draw_all(L, fr, t, E_H)
CAM_HOOK = [(0, CX, 1000, 1.06), (K["cachette"], CX, 1150, 1.1), (K["condamne"], CX, 1000, 1.0)]

# --- 1. Titre : le club le plus fou de France
E_T = words(lambda w, i: KW(w, JAUNE if w == "FOU" else NOIR, NOIR if w == "FOU" else BLANC, 170 if w == "FOU" else 110),
            [("LE CLUB", K["voici"] + .7), ("LE PLUS", K["fou"] - .3), ("FOU", K["fou"] - .05), ("DE FRANCE", K["france0"] - .05)], CX, 560, maxw=900, out=K["y1919"] - .15) + \
      [El(CREST(560), CX, 1150, K["voici"] - .05, K["y1919"] - .15, "pop", "shrink", 1, -3, .6),
       El(KW("SAINT-ÉTIENNE", VERT, BLANC, 120), CX, 1580, K["saint"] - .05, K["y1919"] - .15, "stamp", "fly", rot=-3)]
@scene(K["voici"], trans="whip", td=.25)
def s_titre(L, fr, t):
    green_bg(L, "titre", t); dark(L, .15)
    sparks_burst(L, t, K["fou"], CX, 1150, 14, (255, 230, 120), 420)
    M.draw_all(L, fr, t, E_T)
CAM_TITRE = [(K["voici"], CX, 980, 1.0), (K["fou"], CX, 900, 1.1), (K["saint"], CX, 1200, 1.04)]

# --- 2. 1919 : le magasin Casino, maillot vert
CASP = foot.Player("acas", hair=(70, 50, 30))
E_19 = [El(stampl("1919", (110, 70, 40), 200), CX, 520, K["y1919"], K["maillot"] - .2, "stamp", "fly", 1, -4),
        El(shop(), CX, 1300, K["y1919"] + .2, K["maillot"] - .2, "rise", "slide_l", dist=1200, idle=.2),
        El(tag("DES EMPLOYÉS DE CASINO", 56, CREME), CX, 1450, K["casino"] - .1, K["maillot"] - .2, "pop", "fly", rot=2),
        El(KW("VERT", VERT, BLANC, 170), CX, 560, K["vert"] - .05, None, "stamp", rot=-4),
        El(tag("= LA COULEUR DU MAGASIN", 58, BLANC), CX, 1680, K["magasin"] - .3, None, "pop", rot=2)]
@scene(K["y1919"], trans="tear", td=.3)
def s_1919(L, fr, t):
    paper_fill(L, (214, 190, 146), "sep")
    M.draw_all(L, fr, t, E_19[1:2])
    if K["employes"] - .2 < t < K["maillot"]:
        for i in range(3):
            t0 = K["employes"] - .2 + i*.15; u = clamp((t - t0)/.8); xs = lerp(-200 - i*120, 260 + i*230, M.ease_out(u))
            if t > K["maillot"] - .3: xs += 1300*M.ease_in((t - K["maillot"] + .3)/.3)
            legs, arms, bob = walk(t, 9, 22) if u < 1 else ((0, 0), (14, 14), 0)
            CASP.draw(L, fr, xs, 1700 + bob, s=.7, kit="suit", legs=legs, arms=arms, mood="happy", t=t)
    if t > K["maillot"] - .1:
        u = M.spring(t - K["maillot"] + .1, .5, 11); rays(L, (CX, 1150), t, .7, 14, 1500, (240, 226, 190), .1, .3)
        CASP.draw(L, fr, CX, lerp(2500, 1640, u), s=1.25, kit="asse", arms=(30 + 8*math.sin(t*6), 30 - 8*math.sin(t*6)), mood="happy", t=t)
        if t > K["magasin"] - .2: put(L, shop(), 860, 1190, .32*M.spring(t - K["magasin"] + .2, .4, 14), 8)
    M.draw_all(L, fr, t, E_19[:1] + E_19[2:])
CAM_1919 = [(K["y1919"], CX, 980, 1.0), (K["casino"], CX, 1250, 1.08), (K["maillot"], CX, 1000, 1.0), (K["vert"], CX, 1150, 1.08), (K["magasin"], CX, 1100, 1.02)]

# --- 3. 1958 : Mekhloufi disparaît (FLN), revient
E_58 = [El(stampl("1958", BLANC, 180), CX, 520, K["y1958"], K["mekh"] - .1, "stamp", "fly", 1, -4),
        El(marker("RACHID MEKHLOUFI", "amek", 74), CX, 520, K["mekh"] - .05, K["secret"] - .2, "slide_l", "fly", rot=-2),
        El(KW("DISPARAÎT EN PLEINE NUIT", NOIR, BLANC, 72), CX, 1640, K["disparait"] - .05, K["secret"] - .2, "stamp", "fly", rot=2),
        El(KW("EN SECRET", ROUGE, BLANC, 110), CX, 520, K["secret"] - .05, K["ans4"] - .2, "stamp", "fly", rot=-3),
        El(tag("L'ÉQUIPE DU FLN ALGÉRIEN", 60, BLANC), CX, 1640, K["fln"] - .1, K["ans4"] - .2, "pop", "fly", rot=2),
        El(stampl("4 ANS PLUS TARD…", NOIR, 100), CX, 520, K["ans4"], None, "stamp", rot=-3),
        El(KW("IL REVIENT !", VERT, BLANC, 110), CX, 1600, K["revient"] - .05, None, "stamp", rot=3)]
@scene(K["y1958"], trans="flash", td=.15)
def s_mekh(L, fr, t):
    night = t < K["ans4"]
    if night:
        vgrad(L, 0, H, (10, 14, 34), (30, 34, 64)); d = ImageDraw.Draw(L)
        d.ellipse([720, 330, 900, 510], fill=(250, 244, 210)); d.ellipse([680, 310, 860, 490], fill=(12, 16, 38))
        for k in range(40): d.ellipse([(k*137) % W, (k*71) % 900 + 600, (k*137) % W + 4, (k*71) % 900 + 604], fill=(220, 220, 240))
    else: green_bg(L, "mek2", t)
    if t < K["secret"] - .1:
        u = M.spring(t - K["mekh"] + .2, .5, 11); a = 1 - M.ease_in((t - K["nuit"] + .2)/.5) if t > K["nuit"] - .2 else 1
        if a > .02: put(L, CUT("mekhloufi", 1000), CX, lerp(2600, 1900, u), 1, -2, a)
        if t > K["disparait"]: puffs(L, t, K["nuit"] - .1, CX, 1500, 12, (120, 120, 150), 340, .8)
    elif t < K["ans4"]:
        flag_dz(L, 140, 760, t, 1.5)
        u = clamp((t - K["secret"])/1.6); put(L, CUT("mekhloufi", 760), lerp(1300, 700, M.ease_out(u)), 1900, 1, 3, 1)
    else:
        u = M.spring(t - K["revient"] + .2, .55, 10); put(L, CUT("mekhloufi", 1000), lerp(-500, CX, u), 1900, 1, -2)
        if t > K["titres"] - .1:
            for i, x in enumerate((180, 900)):
                put(L, cup_gold(300), x, 1300, M.spring(t - K["titres"] + .1 - i*.12, .4, 14), (-1)**i*6)
            confetti(L, fr, "amc", t - K["titres"], 60, 2, [VERT, BLANC, JAUNE])
    M.draw_all(L, fr, t, E_58)
CAM_MEKH = [(K["y1958"], CX, 980, 1.0), (K["mekh"], CX, 1200, 1.06), (K["nuit"], CX, 1300, 1.1), (K["secret"], CX, 1000, 1.0),
            (K["fln"], 500, 1050, 1.08), (K["ans4"], CX, 1000, 1.0), (K["titres"], CX, 1150, 1.05)]

# --- 4. 1967 : Keita, taxi 500 km
E_67 = [El(stampl("1967", NOIR, 180), CX, 520, K["y1967"], K["keita"] - .1, "stamp", "fly", 1, -4),
        El(marker("SALIF KEITA", "akei", 80), CX, 520, K["keita"] - .05, K["personne"] - .2, "slide_l", "fly", rot=-2),
        El(tag("DU MALI", 64, (250, 210, 40), NOIR), CX, 1640, K["mali"] - .2, K["personne"] - .2, "pop", "fly", rot=2),
        El(KW("PERSONNE NE L'ATTEND", NOIR, BLANC, 80), CX, 520, K["personne"] - .05, K["taxi"] - .3, "stamp", "fly", rot=-2),
        El(KW("ALORS… TAXI !", JAUNE, NOIR, 110), CX, 520, K["taxi"] - .2, K["club"] - .2, "stamp", "fly", rot=-3),
        El(stampl("C'EST LE CLUB QUI PAYE !", ROUGE, 76), CX, 560, K["club"] - .1, None, "stamp", rot=-4)]
@scene(K["y1967"], trans="whip", td=.25)
def s_keita(L, fr, t):
    if t < K["taxi"] - .3:
        paper_fill(L, (200, 214, 226), "aero"); d = ImageDraw.Draw(L)
        if t > K["personne"] - .2:
            d.rectangle([0, 1720, W, H], fill=(150, 150, 150))
            put(L, tag("ARRIVÉES ✈", 60, (30, 40, 90), BLANC).v[0] if False else shadowed(LBL("ARRIVÉES · ORLY", "aorly", font("mono", 56), BLANC, (30, 40, 90), padx=30, pady=12, rough=1).v[0], "orly"), CX, 820, 1, 0)
            for k, x in enumerate((140, 940)): d.ellipse([x - 50, 1680, x + 50, 1720], fill=(130, 130, 130))
        u = M.spring(t - K["keita"] + .2, .5, 11); put(L, CUT("keita", 980 if t < K["personne"] else 800), CX, lerp(2600, 1900, u), 1, -2 + 2*math.sin(t*1.5))
        if t > K["personne"]:
            q = 1 + .2*math.sin(t*6); put(L, qmark(), 860, 1050, .35*q, 10)
    else:
        paper_fill(L, (140, 196, 230), "sky"); d = ImageDraw.Draw(L)
        for k in range(5): xh = ((k*300 - t*260) % (W + 600)) - 300; d.polygon([(xh, 1500), (xh + 300, 1180 - 40*(k % 2)), (xh + 600, 1500)], fill=(90, 140, 90))
        d.rectangle([0, 1500, W, H], fill=(80, 80, 86))
        for k in range(8): xx = ((k*180 - t*900) % (W + 200)) - 100; d.rectangle([xx, 1640, xx + 90, 1656], fill=(250, 240, 200))
        u = clamp((t - K["taxi"] + .3)/1.0); taxi(L, lerp(-400, CX, M.ease_out(u)), 1700, 1.25, t)
        put(L, CUT("keita", 260), lerp(-400, CX, M.ease_out(u)) + 40, 1560, 1, 0)
        km = int(500*M.ease_io(clamp((t - K["taxi"])/(K["km"] + .3 - K["taxi"]))))
        LBL(f"{km} KM", f"akm{km}", font("title", 150), NOIR, JAUNE, padx=30, pady=8, rough=2).draw(L, fr, CX, 1000, M.spring(t - K["taxi"], .45, 14), -3)
        if t > K["club"] - .3: money_rain(L, t, K["club"] - .3, 14, speed=700)
    M.draw_all(L, fr, t, E_67)
CAM_KEITA = [(K["y1967"], CX, 980, 1.0), (K["keita"], CX, 1200, 1.06), (K["personne"], CX, 1100, 1.02), (K["taxi"], CX, 1300, 1.06),
             (K["km"], CX, 1050, 1.12), (K["club"], CX, 1000, 1.0)]

# --- 5. CTA QUIZ (réponse jamais donnée)
QOUT = K["abonne"] - .25
E_Q = [El(mono("QUESTION POUR LES VRAIS", 54, ROUGE), CX, 520, K["question"], K["quel"] - .15, "pop", "fly", rot=-2)] + \
    words(lambda w, i: KW(w, JAUNE if i == 1 else BLANC, NOIR, 82), [("QUEL FUTUR", K["quel"] - .03), ("BUTEUR", K["buteur"] - .03),
          ("D'ARSENAL ET DU BARÇA", K["arsenal"] - .05), ("A EXPLOSÉ À SAINTÉ ?", K["explose"] - .1)], CX, 600, maxw=1000, out=QOUT) + \
    [El(marker("RÉPONDS EN COMMENTAIRE", "arep", 70), CX, 1430, K["reponds"] - .05, QOUT, "slide_l", "slide_r", rot=2)] + \
    [El(KW("MERCI !", JAUNE, NOIR, 130), CX, 560, K["chaine"] - .1, None, "stamp", rot=-3)]
@scene(K["question"], trans="glitch", td=.18)
def s_quiz(L, fr, t):
    paper_fill(L, (12, 46, 28), "quiz"); rays(L, (CX, 1050), t, .6, 16, 1700, (24, 80, 46), .1, .3)
    if t < QOUT + .25:
        ex = M.ease_in((t - QOUT)/.25) if t > QOUT else 0
        lay = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); foot.Player("aq", hair=(40, 30, 20)).draw(lay, fr, 450, 860, s=1.1, kit="asse", arms=(100 + 10*math.sin(t*3), 100 - 10*math.sin(t*3)), t=t)
        a = lay.getchannel("A"); rim = Image.new("RGBA", lay.size, (140, 200, 160, 255)); rim.putalpha(a.filter(ImageFilter.MaxFilter(9)))
        sil = Image.new("RGBA", lay.size, (8, 12, 10, 255)); sil.putalpha(a); rim.alpha_composite(sil); rim.info["anchor"] = (450, 860)
        put(L, rim, CX, 1580 + 900*ex*ex, M.spring(t - K["question"] - .1, .5, 12))
        put(L, qmark(), CX, 960 + 12*math.sin(t*4) + 900*ex*ex, .55*M.spring(t - K["question"] - .25, .4, 14), 6*math.sin(t*3))
        if t > K["arsenal"]: put(L, logo("arsenal", 150) if os.path.exists(os.path.join(ROOT, "assets", "logos", "arsenal_sticker.png")) else qmark(), 230, 1250 + 900*ex*ex, .0 if not os.path.exists(os.path.join(ROOT, "assets", "logos", "arsenal_sticker.png")) else M.spring(t - K["arsenal"], .4, 14), -8)
        if t > K["barca"]: put(L, logo("barca", 150), 850, 1250 + 900*ex*ex, M.spring(t - K["barca"], .4, 14), 8)
        if K["reponds"] < t < QOUT:
            y = 1530 + 18*abs(math.sin(t*6)); ImageDraw.Draw(L).polygon([(CX - 46, y), (CX + 46, y), (CX, y + 56)], fill=ROUGE)
    else:
        tc = K["abonne"] + .18; pressed = t > tc
        bs = M.spring(t - QOUT - .1, .45, 14)
        if pressed: b = t - tc; q = .12*math.exp(-b*12)*math.cos(b*30); bsx, bsy = 1 + q, 1 - q - (.08 if b < .08 else 0)
        else: bsx = bsy = 1
        blit_sxy(L, sub_button(pressed), CX, 900, bs*bsx, bs*bsy, -2)
        if pressed: sparks_burst(L, t, tc, CX, 900, 14, (255, 230, 120), 340)
        cu = M.ease_io((t - QOUT)/.4); cx_, cy_ = lerp(980, CX + 60, cu), lerp(1500, 920, cu)
        if pressed: cx_ += 160*M.ease_in((t - tc - .25)/.4); cy_ += 500*M.ease_in((t - tc - .25)/.4)
        put(L, cursor(), cx_, cy_ + (8 if abs(t - tc) < .06 else 0), .9)
        if t > K["like"] - .1:
            b = t - K["like"] + .1; beat = 1 + .08*math.exp(-((b % .6) - .05)**2/.004)
            put(L, heart(150), CX, 1330, M.spring(b, .35, 16)*beat, 0)
            for k in range(12):
                u = (b*.9 - k*.05)
                if 0 < u < 1: put(L, heart(26 + (k % 3)*10, (255, 90, 130)), CX + 320*math.sin(k*1.7)*M.ease_out(u), 1330 - 650*u, 1 - u*.6, 20*math.sin(k + t*3), 1 - u**2)
    M.draw_all(L, fr, t, E_Q)
CAM_QUIZ = [(K["question"], CX, 980, 1.0), (K["reponds"], CX, 1100, 1.05), (QOUT, CX, 940, 1.1), (K["like"], CX, 1200, 1.1), (K["y1976"], CX, 1000, 1.0)]

# --- 6. 1976 : Kiev, 0-2 puis 3-0, naissance du Chaudron
E_76 = [El(stampl("1976", NOIR, 180), CX, 520, K["y1976"], K["zd"] - .1, "stamp", "fly", 1, -4),
        El(tag("ALLER · À KIEV", 60, BLANC), CX, 520, K["zd"] - .05, K["retour"] - .15, "pop", "fly", rot=-2),
        El(tag("RETOUR · À SAINTÉ", 60, VERT, BLANC), CX, 520, K["retour"], K["devient"] - .2, "pop", "fly", rot=2),
        El(KW("LE CHAUDRON", ROUGE, BLANC, 150), CX, 560, K["chaudron"] - .1, None, "stamp", rot=-4)]
@scene(K["y1976"], trans="whip", td=.25)
def s_kiev(L, fr, t):
    vgrad(L, 0, H, (10, 30, 20), (20, 60, 36)); d = ImageDraw.Draw(L)
    for k in range(60): d.ellipse([(k*67) % W, 1640 + (k*31) % 260, (k*67) % W + 9, 1649 + (k*31) % 260], fill=(255, 240, 180) if (k + fr//4) % 6 == 0 else (40, 80, 50))
    if t < K["devient"] - .1:
        ret = t > K["retour"]
        seq = [(0, 0, 0), (K["zd"] + .1, 0, 1), (K["zd"] + .4, 0, 2)] if not ret else [(0, 0, 0), (K["tz"] - .3, 1, 0), (K["tz"], 2, 0), (K["tz"] + .3, 3, 0)]
        scoreboard(L, CX, 1050, t, seq, "ST-ÉTIENNE", "KIEV", 160, board_in(t, K["y1976"] + .1))
        if ret and t > K["explose2"] - .2:
            for g in (K["tz"] - .3, K["tz"], K["tz"] + .3): fx.shockwave(L, t, g, CX - 210, 1050, .4, 500, (255, 236, 150))
            camera_flashes(L, fr, "akf", t - K["explose2"], 3.0, 30, (60, 1650, 1020, 1880))
    else:
        u = M.spring(t - K["devient"] + .1, .5, 11)
        smoke(L, t, CX, 1500, (40, 160, 80), 8, 400, 600, 130)
        for k in range(5): flames(L, 140 + k*200, 1720, t + k*.3, 1.6*u, 4)
        put(L, CREST(520), CX, lerp(2300, 1200, u), 1 + .04*math.sin(t*8), -3)
    M.draw_all(L, fr, t, E_76)
CAM_KIEV = [(K["y1976"], CX, 980, 1.0), (K["zd"], CX, 1050, 1.14), (K["retour"], CX, 1000, 1.0), (K["tz"], CX, 1050, 1.16), (K["devient"], CX, 1000, 1.0), (K["chaudron"], CX, 1150, 1.08)]

# --- 7. 1981 : 10e titre, Platini
E_81 = [El(stampl("1981", NOIR, 180), CX, 520, K["y1981"], K["dixieme"] - .1, "stamp", "fly", 1, -4),
        El(KW("10e TITRE", JAUNE, NOIR, 140), CX, 520, K["dixieme"] - .05, None, "stamp", rot=-3),
        El(marker("MICHEL PLATINI", "apla", 80), CX, 1640, K["platini"] - .05, None, "slide_l", rot=2),
        El(stampl("RECORD DE FRANCE", ROUGE, 80), CX, 720, K["personne2"] - .05, None, "stamp", rot=-6)]
@scene(K["y1981"], trans="flash", td=.15)
def s_platini(L, fr, t):
    green_bg(L, "pla", t); dark(L, .1)
    for i in range(10):                                         # 10 étoiles qui se posent
        x = 120 + (i % 5)*210; y = 900 + (i//5)*0 - 120*(i < 5) + 0
        ti = K["y1981"] + .2 + i*.08 + (.5 if i == 9 else 0)
        if t > ti: put(L, spark(60), x, 820 + (i//5)*130 + 6*math.sin(t*3 + i), M.spring(t - ti, .35, 14)*(1.4 if i == 9 else 1), t*40)
    u = M.spring(t - K["platini"] + .3, .55, 10); put(L, CUT("platini", 1000), CX, lerp(2600, 1900, u), 1, 2*math.sin(t*1.5))
    if t > K["dixieme"]: confetti(L, fr, "apc", t - K["dixieme"], 80, 2, [VERT, BLANC, JAUNE])
    M.draw_all(L, fr, t, E_81)
CAM_PLA = [(K["y1981"], CX, 980, 1.0), (K["dixieme"], CX, 900, 1.08), (K["platini"], CX, 1300, 1.06), (K["personne2"], CX, 1000, 1.02)]

# --- 8. 1982 : la caisse noire
E_82 = [El(KW("1982 : SCANDALE", ROUGE, BLANC, 110), CX, 560, K["y1982"] + .1, K["m20"] - .2, "stamp", "fly", 1, -3),
        El(KW("LA CAISSE NOIRE", NOIR, BLANC, 120), CX, 1560, K["caisse"] - .05, K["president2"] - .2, "stamp", "fly", rot=3),
        El(KW("20 MILLIONS DE FRANCS", JAUNE, NOIR, 84), CX, 560, K["m20"] - .05, K["president2"] - .2, "stamp", "fly", rot=-2),
        El(tag("POUR PAYER LES JOUEURS EN DOUCE", 50, BLANC), CX, 620, K["payer"] - .1, K["president2"] - .2, "pop", "fly", rot=2),
        El(marker("ROGER ROCHER", "aroc", 80), CX, 560, K["rocher"] - .1, None, "slide_l", rot=-2),
        El(stampl("IL TOMBE…", ROUGE, 110), CX, 720, K["tombe"], None, "stamp", rot=-6)]
@scene(K["y1982"], trans="glitch", td=.18)
def s_caisse(L, fr, t):
    paper_fill(L, (20, 18, 24), "noir"); rays(L, (CX, 1100), t, .7, 14, 1700, (50, 20, 24), .1, .3)
    if t < K["president2"]:
        op = M.spring(t - K["caisse"] + .1, .5, 11)
        safe_box(L, CX, 1100, op, t)
        if t > K["m20"] - .2: money_rain(L, t, K["m20"] - .2, 22, speed=640)
        if t > K["caches"] - .1:
            for k in range(6): put(L, bnote(), CX - 200 + k*80, 1120 - 30*math.sin(k + t*2), .9*M.spring(t - K["caches"] + .1 - k*.05, .4, 14), 20*math.sin(k))
    else:
        tb = K["tombe"]; u = M.spring(t - K["president2"], .5, 11)
        rot = 0 if t < tb else -78*M.ease_in(clamp((t - tb)/.45)); fall = 0 if t < tb else 500*M.ease_in(clamp((t - tb)/.6))
        put(L, CUT("rocher", 1000), CX, lerp(2600, 1950, u) + fall, 1, rot)
        if t > K["club2"] - .1:                                   # l'écusson se fissure
            v = M.spring(t - K["club2"] + .1, .4, 14); put(L, CREST(300), 870, 1150, v, 8)
            uu = M.ease_out((t - K["club2"])/.3); pts = [(850, 1030), (880, 1100), (845, 1170), (885, 1260)]
            n = 1 + uu*(len(pts) - 1); ImageDraw.Draw(L).line(pts[:max(2, int(n) + 1)], fill=BLANC, width=9)
    M.draw_all(L, fr, t, E_82)
CAM_CAISSE = [(K["y1982"], CX, 980, 1.0), (K["caisse"], CX, 1100, 1.1), (K["m20"], CX, 1000, 1.02), (K["president2"], CX, 1100, 1.04), (K["tombe"], CX, 1200, 1.1), (K["club2"], 800, 1150, 1.08)]

# --- 9. 2022 : descente, envahissement
E_22 = [El(KW("2022", NOIR, BLANC, 150), CX, 560, K["y2022"], K["supporters"] - .2, "stamp", "fly", rot=-3),
        El(stampl("DESCENTE EN LIGUE 2", ROUGE, 80), CX, 1560, K["descente"] - .05, K["supporters"] - .2, "stamp", "fly", rot=-5),
        El(tag("AUX TIRS AU BUT", 60, BLANC), CX, 620, K["tab"] - .1, K["supporters"] - .2, "pop", "fly", rot=2),
        El(KW("ENVAHISSEMENT", ROUGE, BLANC, 110), CX, 560, K["envahissent"] - .05, None, "stamp", rot=-3),
        El(stampl("SANCTIONNÉ", NOIR, 130), CX, 1620, K["sanction"] - .05, None, "stamp", rot=-7)]
@scene(K["y2022"], trans="whip", td=.25)
def s_2022(L, fr, t):
    vgrad(L, 0, H, (16, 20, 22), (40, 46, 50))
    if t < K["supporters"] - .1:
        scoreboard(L, CX, 1050, t, [(0, 1, 1)], "ST-ÉTIENNE", "AUXERRE", 160, board_in(t, K["y2022"] + .1))
        if t > K["tab"]: pen_dots(L, 300, 1330, t, K["tab"], [(K["tab"] + .1 + i*.18, "ok" if i != 4 else "ko") for i in range(5)], r=40, gap=110)
    else:
        u = M.spring(t - K["supporters"] + .1, .5, 11); sh = 10*math.sin(t*40)*math.exp(-(t - K["envahissent"])*3) if t > K["envahissent"] else 0
        put(L, photo(os.path.join(PH, "envahissement_2022.png"), 820), CX + sh, lerp(2400, 1080, u), 1, -2)
        smoke(L, t, 300, 1450, (230, 60, 50), 7, 300, 600, 140); smoke(L, t + 1.3, 820, 1450, (50, 190, 90), 7, 300, 600, 140)
        if t > K["fumi"] - .2:
            for k in range(4):
                tt = t - K["fumi"] + .2 - k*.25
                if 0 < tt < .9: x0, x1 = (120, 960)[k % 2], (900, 160)[k % 2]; bx, by = arc((x0, 1800), (x1, 900), 500, tt/.9); d = ImageDraw.Draw(L); d.ellipse([bx - 18, by - 18, bx + 18, by + 18], fill=(255, 120, 60)); smoke(L, t, bx, by, (230, 90, 60), 3, 40, 120, 160)
        if t > K["sanction"]: LBL("−3 PTS · HUIS CLOS", "ahc", font("mono", 52), BLANC, ROUGE, padx=20, pady=8, rough=2).draw(L, fr, CX, 1760, M.spring(t - K["sanction"] - .2, .4, 14), 3)
    M.draw_all(L, fr, t, E_22)
CAM_2022 = [(K["y2022"], CX, 980, 1.0), (K["tab"], CX, 1150, 1.06), (K["supporters"], CX, 1000, 1.0), (K["fumi"], CX, 1050, 1.1), (K["sanction"], CX, 1150, 1.04)]

# --- 10. 2024 : milliardaire canadien
E_24 = [El(KW("2024", NOIR, BLANC, 150), CX, 560, K["y2024"], None, "stamp", rot=-3),
        El(KW("UN MILLIARDAIRE", JAUNE, NOIR, 110), CX, 720, K["milliard"] - .1, None, "stamp", rot=2),
        El(tag("CANADIEN", 70, ROUGE, BLANC), CX, 860, K["canadien"] - .05, None, "pop", rot=-2),
        El(stampl("RACHÈTE LES VERTS", VERT, 90), CX, 1640, K["rachete"] - .05, None, "stamp", rot=-5)]
@scene(K["y2024"], trans="tear", td=.3)
def s_2024(L, fr, t):
    paper_fill(L, (236, 228, 210), "ca")
    if t > K["canadien"] - .2: flag_ca(L, CX, 1080, t, 1.6*M.spring(t - K["canadien"] + .2, .5, 12))
    money_rain(L, t, K["milliard"] - .2, 18, speed=560)
    if t > K["rachete"] - .2: put(L, CREST(380), CX, 1260, M.spring(t - K["rachete"] + .2, .45, 13), -4)
    M.draw_all(L, fr, t, E_24)
CAM_2024 = [(K["y2024"], CX, 980, 1.0), (K["milliard"], CX, 800, 1.06), (K["canadien"], CX, 1050, 1.04), (K["rachete"], CX, 1200, 1.06)]

# --- 11. FIN : Saint-Étienne ou Lyon ?
E_F = [El(KW("ET TOI ?", NOIR, BLANC, 130), CX, 560, K["toi"] - .05, None, "stamp", rot=-3),
       El(CREST(400), 290, 1050, K["stet"] - .05, None, "pop", rot=-6),
       El(logo("ol", 380), 790, 1050, K["lyon"] - .05, None, "pop", rot=6),
       El(KW("VS", JAUNE, NOIR, 110), CX, 1050, K["lyon"] + .1, None, "stamp", rot=-4),
       El(KW("LE VRAI CLUB DE LA RÉGION ?", BLANC, NOIR, 72), CX, 1420, K["vrai"] - .05, None, "stamp", rot=2),
       El(marker("DIS-LE EN COMMENTAIRE", "acom", 76), CX, 1600, K["dis"] - .05, None, "slide_l", rot=-2)]
@scene(K["toi"], trans="whip", td=.25)
def s_fin(L, fr, t):
    d = ImageDraw.Draw(L); paper_fill(L, (30, 50, 120), "lyon")
    off = 30*math.sin(t*3); d.polygon([(0, 0), (CX + 140 + off, 0), (CX - 140 + off, H), (0, H)], fill=VERT)
    if t > K["lyon"] + .1: sparks_burst(L, t, K["lyon"] + .1, CX, 1050, 14, (255, 230, 120), 360)
    if t > K["dis"]:
        y = 1700 + 16*abs(math.sin(t*6)); d.polygon([(CX - 46, y), (CX + 46, y), (CX, y + 56)], fill=ROUGE)
    M.draw_all(L, fr, t, E_F)
CAM_FIN = [(K["toi"], CX, 980, 1.0), (K["stet"], 400, 1050, 1.08), (K["lyon"], 700, 1050, 1.08), (K["vrai"], CX, 1100, 1.0), (K["dis"], CX, 1200, 1.04)]

SC.sort(key=lambda s: s["t0"])
CAMS = {"s_hook": CAM_HOOK, "s_titre": CAM_TITRE, "s_1919": CAM_1919, "s_mekh": CAM_MEKH, "s_keita": CAM_KEITA, "s_quiz": CAM_QUIZ,
        "s_kiev": CAM_KIEV, "s_platini": CAM_PLA, "s_caisse": CAM_CAISSE, "s_2022": CAM_2022, "s_2024": CAM_2024, "s_fin": CAM_FIN}
IMPACTS = [K["condamne"], K["fou"], K["vert"], K["nuit"], K["secret"], K["revient"], K["km"], K["club"], K["abonne"] + .18, K["like"],
           K["zd"] + .4, K["tz"], K["chaudron"], K["dixieme"], K["caisse"], K["tombe"], K["descente"], K["envahissent"], K["sanction"], K["rachete"], K["lyon"] + .1]
PUNCH += IMPACTS
IMPACT_SET.update(IMPACTS)
BEATS = [MUS_T0 + k*60/MUS_BPM for k in range(int(K['END']*MUS_BPM/60) + 2)]
PUNCH += BEATS
# ------------------------------------------------------------------ rendu + transitions
def render_scene(i, fr, t):
    s = SC[i]; L = Image.new("RGBA", s["size"], (0, 0, 0, 255)); s["fn"](L, fr, t)
    cx, cy, z = M.cam_spring(CAMS[s["name"]], t); z *= punch(t)
    sx_, sy_, sr = M.trauma_offset(t, IMPACTS)
    return apply_cam(L, cx + 4*math.sin(t*.9) + sx_, cy + 3*math.cos(t*.7) + sy_, z, .3*math.sin(t*.6) + sr).convert("RGB")
def scene_at(t):
    k = 0
    for i, s in enumerate(SC):
        if t >= s["t0"]: k = i
    return k
def frame(fr, t):
    k = scene_at(t); s = SC[k]; cur = render_scene(k, fr, t)
    u = (t - s["t0"])/s["td"] if k else 1
    if u < 1:
        prev = render_scene(k - 1, fr, t); tr = s["trans"]; e = M.ease_io(u)
        if tr in ("whip", "whip_up"):
            vert = tr == "whip_up"; off = int((W if not vert else H)*e); out = Image.new("RGB", (W, H))
            if vert: out.paste(prev, (0, off)); out.paste(cur, (0, off - H))
            else: out.paste(prev, (-off, 0)); out.paste(cur, (W - off, 0))
            fx.whip_blur(out, 0 if vert else -110*math.sin(math.pi*u), 110*math.sin(math.pi*u) if vert else 0, 7); cur = out
        elif tr == "tear": tear_transition(cur, prev, u, "tear_v", k)
        elif tr == "fade": cur = Image.blend(prev, cur, e)
        elif tr == "flash":
            cur = Image.blend(prev, cur, 1.0 if u > .5 else 0.0); cur = Image.blend(cur, Image.new("RGB", (W, H), (255, 250, 236)), max(0, 1 - abs(u - .5)*2.2))
        elif tr == "glitch":
            cur = (cur if u > .5 else prev).copy(); rgb_split(cur, 22*(1 - abs(u - .5)*2), fr, 9)
    fx.dust(cur, t, 22)
    bp = ((t - MUS_T0)*MUS_BPM/60); ph = bp - math.floor(bp)              # phase dans le temps (0 = sur le temps)
    if int(math.floor(bp)) % 4 == 0 and ph < .12:                         # temps fort (1 par mesure) : flash + aberration chromatique
        a_ = 1 - ph/.12; cur = Image.blend(cur, Image.new("RGB", (W, H), (255, 248, 230)), .18*a_)
        r_, g_, b_ = cur.split(); o = int(10*a_); cur = Image.merge("RGB", (ImageChops.offset(r_, o, 0), g_, ImageChops.offset(b_, -o, 0)))
    cur = cur.convert("RGBA"); fx.vignette(cur, 90); fil_rouge(cur, fr, t)
    return cur.convert("RGB")
def draw(cv, fr, t, T):
    tv = max(0.0, t - PAD_IN); cv.paste(frame(fr, tv), (0, 0))
# ------------------------------------------------------------------ sons
P = PAD_IN
V5S = os.path.join(ROOT, "episodes", "lille_v5", "sfx"); RS = os.path.join(RENNES, "sfx"); BANK = os.path.join(ROOT, "assets", "sfx")
def X(t, name, g): return (P + t, name, g)
SFX = [X(0, "braam", .75), X(.05, "cash", .5), X(K["cachette"], "swish", .5), X(K["condamne"] - .05, "jail", .7), X(K["condamne"], "gavel", .6),
       X(K["voici"] - .02, "whoosh1", .5), X(K["voici"] + .05, "pop", .5), X(K["fou"], "stamp", .6), X(K["saint"], "stamp", .6),
       X(K["y1919"] - .02, "page_tear", .5), X(K["y1919"], "stamp", .55), X(K["casino"], "typewriter", .35), X(K["maillot"], "pop", .5), X(K["vert"], "stamp", .65),
       X(K["y1958"] - .05, "flashfx", .45), X(K["y1958"], "stamp", .5), X(K["mekh"], "marker", .45), X(K["disparait"], "wind", .5), X(K["nuit"] - .1, "swish", .55),
       X(K["secret"], "stamp", .55), X(K["fln"], "pop", .45), X(K["ans4"], "tictac", .4), X(K["revient"], "whoosh2", .5), X(K["titres"], "fanfare", .35),
       X(K["y1967"] - .02, "whoosh3", .5), X(K["y1967"], "stamp", .5), X(K["keita"], "marker", .45), X(K["mali"], "pop", .45), X(K["personne"], "plane", .35),
       X(K["taxi"] - .2, "oldcar", .55), X(K["km"], "stamp", .55), X(K["club"], "cash", .65), X(K["paye"], "coins", .45),
       X(K["question"], "glitch", .45), X(K["question"] + .05, "typewriter", .35), X(K["quel"], "riser", .4), X(K["explose"], "stamp", .45), X(K["reponds"], "marker", .45),
       X(K["abonne"] + .25, "pop", .6), X(K["abonne"] + .3, "ding", .4), X(K["like"], "sparkle", .5), X(K["like"] + .05, "pop", .5), X(K["chaine"], "notif", .45),
       X(K["y1976"] - .02, "whoosh1", .5), X(K["y1976"], "stamp", .5), X(K["zd"] + .1, "flap", .5), X(K["zd"] + .4, "flap", .5), X(K["zd"] + .5, "groan", .35),
       X(K["retour"], "crowd", .45), X(K["tz"] - .3, "flap", .5), X(K["tz"], "flap", .55), X(K["tz"] + .3, "flap", .6), X(K["tz"] + .05, "goal_roar", .55),
       X(K["devient"], "fire", .55), X(K["chaudron"], "stamp", .7), X(K["chaudron"] + .1, "crowd", .5),
       X(K["y1981"] - .05, "flashfx", .45), X(K["y1981"], "stamp", .5), X(K["dixieme"], "stamp", .65), X(K["dixieme"] + .1, "champagne", .4), X(K["platini"], "camera", .5), X(K["personne2"], "stamp", .55),
       X(K["y1982"], "glitch", .5), X(K["y1982"] + .1, "thunder", .5), X(K["caisse"], "stamp", .6), X(K["m20"], "cash", .6), X(K["caches"], "coins", .45), X(K["rocher"], "camera", .5),
       X(K["tombe"], "fall", .55), X(K["tombe"] + .45, "thud", .6), X(K["club2"], "crash", .4),
       X(K["y2022"] - .02, "whoosh2", .5), X(K["y2022"], "stamp", .5), X(K["descente"], "stamp", .6), X(K["tab"] + .1, "kick", .4), X(K["tab"] + .8, "groan", .45),
       X(K["supporters"], "crowd", .55), X(K["envahissent"], "siren", .35), X(K["fumi"], "boom", .45), X(K["sanction"], "gavel", .6),
       X(K["y2024"] - .02, "page_tear", .5), X(K["y2024"], "stamp", .5), X(K["milliard"], "cash", .55), X(K["canadien"], "pop", .45), X(K["rachete"], "stamp", .6),
       X(K["toi"] - .02, "whoosh3", .5), X(K["stet"], "pop", .5), X(K["lyon"], "pop", .5), X(K["lyon"] + .1, "bang", .5), X(K["vrai"], "stamp", .5), X(K["dis"], "notif", .55), X(K["dis"] + .8, "bell", .4)]
SFX_DIR = "/tmp/claude-0/sfx_asse3"
os.makedirs(SFX_DIR, exist_ok=True)
for nm in set(n for _, n, _ in SFX):
    src = next((p for p in (os.path.join(RS, nm + ".mp3"), os.path.join(V5S, nm + ".mp3"), os.path.join(BANK, nm + ".mp3")) if os.path.exists(p)), None)
    if nm in ("crowd", "whistle"): src = os.path.join(BANK, nm + ".mp3")
    dst = os.path.join(SFX_DIR, nm + ".mp3")
    if src and not os.path.lexists(dst): os.symlink(src, dst)
SFX = [s for s in SFX if os.path.exists(os.path.join(SFX_DIR, s[1] + ".mp3"))]
SFX = fx.sfx_variants(SFX, SFX_DIR, SFX_DIR + "_v")
SCENES = [Scene("asse", TEXTE, draw, SFX, pad_in=P, pad_out=1.6)]

def stills(out, only=None):
    os.makedirs(out, exist_ok=True); ts = []
    for i, s in enumerate(SC):
        if only and s["name"] != only: continue
        t1 = SC[i + 1]["t0"] if i + 1 < len(SC) else K["END"]; n = 4 if not only else 8
        ts += [s["t0"] + (t1 - s["t0"])*(k + .5)/n for k in range(n)]
    ims = []
    for t in ts:
        cv = Image.new("RGB", (W, H)); cv.paste(frame(int(t*FPS), t)); ims.append(cv.resize((216, 384)))
    cols = 8; rows = (len(ims) + cols - 1)//cols; sheet = Image.new("RGB", (216*cols, 414*rows), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        x, y = (k % cols)*216, (k//cols)*414; sheet.paste(im, (x, y + 30)); dd.text((x + 6, y + 4), f"{ts[k]:.2f}s", font=font("mono", 22), fill=(230, 230, 230))
    p = os.path.join(out, f"asse3sheet{'_' + only if only else ''}.jpg"); sheet.save(p, quality=82); return p

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--stills" in args:
        only = args[args.index("--stills") + 1] if len(args) > args.index("--stills") + 1 else None
        print(stills("/tmp/claude-0/aud", only)); sys.exit()
    out = args[0] if args else os.path.join(ROOT, "output", SLUG); os.makedirs(out, exist_ok=True)
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=[VOIX], sfx_dir=SFX_DIR + "_v", sfx_db=6.0, lufs=-14.0, crf=22, limit=True))
