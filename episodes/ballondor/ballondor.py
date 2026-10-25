"""BALLON D'OR DES SUPPORTERS (vote en commentaire, ≈ 34 s), DA papier 3D. Remake de la base asse3.py.
(ancien en-tête :) SAINT-ÉTIENNE v3 — « le club le plus fou de France » (≈ 79 s), process Rennes (TEXTE.md, SCRIPT.md), DA papercraft 3D.
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

TITLE = "~/vote $ ./ballon-dor"
SLUG = "ballon_dor_supporters"
VOIX = os.path.join(HERE, "voix", "voix.mp3")            # Léo, blancs coupés
TEXTE = open(os.path.join(HERE, "TEXTE.md")).read()
K = dict(toi=.3, decider=.9, merite=1.56, ballon=2.02, annee=2.58, demain=3.2, officiel=4.42, remis=5.08, elu=5.46, journ=6.28,
         mais=7.02, vrai=7.36, supp=8.3, ecris=9.14, nom=9.54, comm=10.3, cinq=11.04, fav=11.3, yamal=11.96, champ=12.62, a19=13.62,
         kane=14.44, b61=14.98, saison=15.94, mbappe=16.54, meill=17.26, mondial=18.04, ldc=18.88, rodri=19.76, elu2=20.42, cdm=21.64,
         dembele=22.52, tenant=23.54, derriere=24.6, kvara=25.36, messi=26.7, a39=27.42, abonne=28.18, mardi=28.98, gagne=30.38,
         supp2=31.36, alors=32.08, ton=32.86, bdo=33.08, END=34.3)
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
def punch(t): return 1 + sum(.06*math.exp(-((t - p)/.11)**2) for p in PUNCH if p - .4 < t < p + .5)

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


GOLD, GOLD2, NAVY2 = (240, 196, 60), (190, 140, 30), (14, 18, 44)
PH = os.path.join(ROOT, "assets", "photos", "bdo")
_cut = {}
def CUT(n, h=900):
    k = (n, h)
    if k not in _cut:
        p = os.path.join(PH, n + ".png"); _cut[k] = paper_player(p, (0, 0) + Image.open(p).size, h)
    return _cut[k]
def gold_ball(r=200):
    k = ("gb", r)
    if k not in _fc:
        im = Image.new("RGBA", (2*r + 40, 2*r + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = r + 20
        for i in range(r, 0, -4):
            u = i/r; col = tuple(int(lerp(a, b, u)) for a, b in zip((255, 236, 150), GOLD2)); d.ellipse([c - i - r*.18*(1 - u), c - i - r*.25*(1 - u), c + i - r*.18*(1 - u), c + i - r*.25*(1 - u)], fill=col)
        for k_ in range(5):
            a = k_*2*math.pi/5 - math.pi/2; px, py = c + r*.55*math.cos(a), c + r*.55*math.sin(a)
            pts = [(px + r*.2*math.cos(a + j*2*math.pi/5), py + r*.2*math.sin(a + j*2*math.pi/5)) for j in range(5)]; d.polygon(pts, outline=(150, 100, 20), width=6)
        pts = [(c + r*.22*math.cos(-math.pi/2 + j*2*math.pi/5), c + r*.22*math.sin(-math.pi/2 + j*2*math.pi/5)) for j in range(5)]; d.polygon(pts, outline=(150, 100, 20), width=6)
        d.ellipse([c - r, c - r, c + r, c + r], outline=(120, 80, 10), width=8); d.ellipse([c - r*.6, c - r*.75, c - r*.25, c - r*.45], fill=(255, 250, 220))
        im.info["anchor"] = (c, c); _fc[k] = shadowed(im, k)
    return _fc[k]
def gala_bg(L, t, key="gala"):
    vgrad(L, 0, H, (10, 12, 34), (34, 26, 70)); rays(L, (CX, 1000), t, .5, 16, 1800, (60, 50, 110), .08, .25)
    d = ImageDraw.Draw(L)
    for k in range(50): d.ellipse([(k*137) % W, (k*71) % 1700 + 150, (k*137) % W + 5, (k*71) % 1700 + 155], fill=(255, 230, 150) if (k + int(t*6)) % 7 == 0 else (90, 80, 140))
def podium(L, x, y, s, col=GOLD):
    d = ImageDraw.Draw(L); w_ = 360*s; h_ = 200*s
    d.polygon([(x - w_/2, y), (x + w_/2, y), (x + w_/2 + 20*s, y + h_), (x - w_/2 - 20*s, y + h_)], fill=(40, 40, 70), outline=col)
    d.rectangle([x - w_/2, y - 26*s, x + w_/2, y], fill=col)
def ballot(L, x, y, s, rot):
    im = Image.new("RGBA", (180, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.rectangle([4, 4, 175, 115], fill=BLANC, outline=NOIR, width=4)
    d.line([(4, 4), (90, 70), (175, 4)], fill=NOIR, width=4); d.line([(120, 80), (138, 98), (166, 64)], fill=(40, 160, 70), width=8)
    im.info["anchor"] = (90, 60); put(L, im, x, y, s, rot)
def urn(L, x, y, s=1.0):
    d = ImageDraw.Draw(L); w_, h_ = 520*s, 520*s
    d.rectangle([x - w_/2, y - h_, x + w_/2, y], fill=(200, 220, 240), outline=BLANC, width=8); d.rectangle([x - w_/2 - 20, y - h_ - 40, x + w_/2 + 20, y - h_], fill=BLANC, outline=NOIR, width=4)
    d.rectangle([x - 120, y - h_ - 26, x + 120, y - h_ - 12], fill=NOIR)
    for k in range(9): d.rectangle([x - w_/2 + 30 + (k % 3)*150, y - 80 - (k//3)*60, x - w_/2 + 160 + (k % 3)*150, y - 30 - (k//3)*60], fill=BLANC, outline=(120, 120, 140))

def fil_rouge(cv, fr, t):
    LBL("BALLON D'OR · LE VOTE DES SUPPORTERS", "bhdr", font("mono", 34), GOLD, NOIR, padx=16, pady=6, rough=1.5).draw(cv, fr, CX, 170, 1, 0)

# --- 0. HOOK
E_H = words(lambda w, i: KW(w, GOLD if w == "TOI" else NOIR, NOIR if w == "TOI" else BLANC, 150 if w == "TOI" else 100),
            [("C'EST", -.3), ("TOI", K["toi"] - .1), ("QUI DÉCIDES", K["decider"] - .1)], CX, 600, maxw=900, out=K["demain"] - .15) + \
      [El(KW("LE BALLON D'OR 2026", GOLD, NOIR, 90), CX, 1640, K["ballon"] - .1, K["demain"] - .15, "stamp", "fly", rot=-3),
       El(LBL("@toi", "btoi", font("title", 70), BLANC, (40, 90, 220), padx=24, pady=6, rough=1), 260, 1300, K["toi"], K["demain"] - .15, "pop", "fly", rot=-6)]
@scene(0.0)
def s_hook(L, fr, t):
    gala_bg(L, t)
    u = M.spring(t + .25, .5, 11); y = lerp(1700, 1080, u) + 14*math.sin(t*3)
    d = ImageDraw.Draw(L); d.rectangle([CX - 70, y + 150, CX + 70, H], fill=(60, 60, 80)); d.ellipse([CX - 150, y + 90, CX + 150, y + 230], fill=(224, 178, 140), outline=NOIR, width=5)
    put(L, gold_ball(230), CX, y, 1 + .03*math.sin(t*6), 4*math.sin(t*2))
    sparks_burst(L, t, K["ballon"], CX, y, 16, (255, 230, 120), 420)
    M.draw_all(L, fr, t, E_H)
CAM_HOOK = [(0, CX, 1000, 1.06), (K["merite"], CX, 1050, 1.1), (K["annee"], CX, 1000, 1.0)]

# --- 1. Demain : jury de journalistes
E_J = [El(KW("DEMAIN SOIR", JAUNE, NOIR, 110), CX, 520, K["demain"], K["mais"] - .15, "stamp", "fly", rot=-3),
       El(tag("LE BALLON D'OR OFFICIEL", 60, BLANC), CX, 680, K["officiel"] - .1, K["mais"] - .15, "pop", "fly", rot=2),
       El(stampl("ÉLU PAR DES JOURNALISTES", ROUGE, 70), CX, 1700, K["elu"] - .05, K["mais"] - .15, "stamp", "fly", rot=-5)]
JRN = [foot.Player(f"bj{i}", hair=((40, 30, 20), (120, 120, 120), (80, 60, 40))[i % 3]) for i in range(5)]
@scene(K["demain"], trans="whip", td=.25)
def s_jury(L, fr, t):
    paper_fill(L, (20, 14, 30), "stage"); d = ImageDraw.Draw(L)
    op = M.ease_io(clamp((t - K["demain"] - .1)/.8))
    for side in (-1, 1):
        x0 = CX + side*(60 + 520*op)
        for k in range(6): xx = x0 + side*k*80; d.rectangle([min(xx, xx + side*80), 760, max(xx, xx + side*80), 1500], fill=(170 - 12*(k % 2), 20, 36))
    put(L, gold_ball(120), CX, 1180, M.spring(t - K["remis"] + .2, .45, 12), 0)
    d.rectangle([CX - 80, 1300, CX + 80, 1500], fill=(60, 50, 90), outline=GOLD, width=5)
    if t > K["elu"] - .2:
        for i, p in enumerate(JRN):
            v = M.spring(t - K["elu"] + .2 - i*.06, .45, 12); x = 130 + i*205
            p.draw(L, fr, x, lerp(2400, 1660, v), s=.55, kit="suit", arms=(60, 20 + 10*math.sin(t*8 + i)), mood="normal", t=t)
            if v > .9: d.rectangle([x + 30, 1450 + 5*math.sin(t*9 + i), x + 90, 1530], fill=BLANC, outline=NOIR, width=3)
    M.draw_all(L, fr, t, E_J)
CAM_J = [(K["demain"], CX, 1000, 1.0), (K["remis"], CX, 1150, 1.1), (K["elu"], CX, 1300, 1.02)]

# --- 2. Le vrai : celui des supporters + urne
E_V = [El(KW("MAIS LE VRAI…", NOIR, BLANC, 110), CX, 520, K["mais"], K["ecris"] - .2, "stamp", "fly", rot=-3),
       El(stampl("C'EST CELUI DES SUPPORTERS", (40, 150, 70), 66), CX, 680, K["supp"] - .1, K["ecris"] - .2, "stamp", "fly", rot=3),
       El(KW("ÉCRIS LE NOM", JAUNE, NOIR, 110), CX, 520, K["ecris"] - .05, None, "stamp", rot=-3),
       El(tag("DE TON JOUEUR EN COMMENTAIRE", 56, BLANC), CX, 670, K["nom"], None, "pop", rot=2)]
@scene(K["mais"], trans="flash", td=.15)
def s_vrai(L, fr, t):
    gala_bg(L, t)
    if t < K["ecris"] - .1:
        u = M.spring(t - K["vrai"], .5, 11)
        for k in range(3): put(L, shadowed(scale_stand(), "stand"), 180 + k*360, lerp(2400, 1500, u), .9)
        if t > K["supp"]: confetti(L, fr, "bcf", t - K["supp"], 70, 2, [GOLD, BLANC, ROUGE])
        put(L, gold_ball(140), CX, 1050 + 10*math.sin(t*4), M.spring(t - K["supp"] + .1, .45, 12), 0)
    else:
        u = M.spring(t - K["ecris"] + .1, .5, 11); urn(L, CX, lerp(2400, 1700, u), 1.1)
        for k in range(8):
            tt = t - K["ecris"] - k*.17
            if 0 < tt < .7: ballot(L, CX + 80*math.sin(k*1.9)*(1 - tt/.7), lerp(700, 1080, M.ease_in(tt/.7)), .9, 30*math.sin(k + tt*6))
        if t > K["comm"] - .2:
            v = M.spring(t - K["comm"] + .2, .4, 14); LBL("@toi : ????  ⬇", "bbub", font("title", 64), NOIR, BLANC, padx=30, pady=14, rough=1).draw(L, fr, CX, 860, v, -2)
    M.draw_all(L, fr, t, E_V)
CAM_V = [(K["mais"], CX, 1000, 1.0), (K["supp"], CX, 1100, 1.06), (K["ecris"], CX, 1100, 1.0), (K["comm"], CX, 1050, 1.06)]

# --- 3. 5 favoris : un joueur par réplique
FAV = [("yamal", "barca", "YAMAL", "CHAMPION DU MONDE À 19 ANS", K["yamal"], K["champ"]),
       ("kane", "bayern", "KANE", "61 BUTS CETTE SAISON", K["kane"], K["b61"]),
       ("mbappe", "real", "MBAPPÉ", "MEILLEUR BUTEUR MONDIAL + LDC", K["mbappe"], K["meill"]),
       ("rodri", "city", "RODRI", "MEILLEUR JOUEUR DU MONDIAL", K["rodri"], K["elu2"]),
       ("dembele", "psg", "DEMBÉLÉ", "TENANT DU TITRE", K["dembele"], K["tenant"])]
E_5 = [El(KW("5 FAVORIS", GOLD, NOIR, 140), CX, 560, K["cinq"] - .05, K["yamal"] - .15, "stamp", "fly", rot=-3)]
for i, (n, club, nm, stat, t0, ts) in enumerate(FAV):
    t1 = FAV[i + 1][4] if i + 1 < len(FAV) else K["derriere"]
    E_5 += [El(KW(nm, BLANC, NOIR, 130), CX, 470, t0 - .05, t1 - .15, "stamp", "fly", rot=(-3, 3)[i % 2]),
            El(stampl(stat, (ROUGE, (40, 150, 70), NAVY, (60, 140, 210), ROUGE)[i], 64), CX, 640, ts - .05, t1 - .15, "stamp", "fly", rot=(4, -4)[i % 2])]
@scene(K["cinq"], trans="whip", td=.25)
def s_fav(L, fr, t):
    gala_bg(L, t)
    cur = max([i for i, f in enumerate(FAV) if t >= f[4] - .15] or [-1])
    for i in range(5):                                         # mini-podiums en bas : rempli au fur et à mesure
        x = 140 + i*200; podium(L, x, 1800, .45, GOLD if i == cur else (120, 110, 160))
        if i <= cur: put(L, logo(FAV[i][1], 90), x, 1760, M.spring(t - FAV[i][4], .35, 14), 0)
    if cur < 0:
        for i in range(5): put(L, qmark(), 140 + i*200, 1650, .3*M.spring(t - K["cinq"] - i*.08, .35, 14), 0)
    else:
        n, club, nm, stat, t0, ts = FAV[cur]; u = M.spring(t - t0 + .15, .45, 12)
        rays(L, (CX, 1200), t, .9, 14, 1500, (90, 80, 150), .1, .3)
        put(L, logo(club, 260), 870, 900, M.spring(t - t0, .45, 14), 8)
        put(L, CUT(n, 1000), lerp(-600 if cur % 2 == 0 else W + 600, CX, u), 1740, 1, (-2, 2)[cur % 2])
        if n == "kane" and t > ts:
            k = min(61, int(61*M.ease_out(clamp((t - ts)/.7)))); LBL(f"{k}", f"bk{k}", font("title", 170), NOIR, GOLD, padx=30, pady=6, rough=2).draw(L, fr, 220, 900, 1, -6)
        if n == "dembele" and t > ts: put(L, gold_ball(110), 220, 920, M.spring(t - ts, .4, 14), 0)
        if n == "yamal" and t > K["a19"]: LBL("19 ANS", "b19", font("title", 110), NOIR, GOLD, padx=26, pady=6, rough=2).draw(L, fr, 220, 900, M.spring(t - K["a19"], .4, 14), -6)
    M.draw_all(L, fr, t, E_5)
CAM_5 = [(K["cinq"], CX, 1000, 1.0)] + sum([[(f[4], CX, 1100, 1.06), (f[5] + .4, CX, 1000, 1.0)] for f in FAV], [])

# --- 4. Outsiders : Kvara + Messi
E_O = [El(KW("DERRIÈRE EUX…", NOIR, BLANC, 110), CX, 470, K["derriere"], None, "stamp", rot=-3),
       El(pin_tag("KVARATSKHELIA", 54), 290, 760, K["kvara"], None, "drop", rot=-4, dist=500),
       El(pin_tag("MESSI", 64), 800, 760, K["messi"] - .05, None, "drop", rot=4, dist=500),
       El(stampl("39 ANS !", ROUGE, 110), 800, 1000, K["a39"] - .05, None, "stamp", rot=-8)]
@scene(K["derriere"], trans="flash", td=.15)
def s_out(L, fr, t):
    gala_bg(L, t)
    put(L, CUT("kvara", 1000), lerp(-500, 290, M.spring(t - K["kvara"] + .2, .45, 12)), 1900, 1, -2)
    put(L, CUT("messi", 900), lerp(W + 500, 800, M.spring(t - K["messi"] + .2, .45, 12)), 1900, 1, 2)
    M.draw_all(L, fr, t, E_O)
CAM_O = [(K["derriere"], CX, 1000, 1.0), (K["kvara"], 400, 1150, 1.08), (K["messi"], 700, 1100, 1.08), (K["a39"], CX, 1000, 1.0)]

# --- 5. CTA abonne-toi / mardi
E_C = [El(KW("MARDI", GOLD, NOIR, 150), CX, 520, K["mardi"] - .05, None, "stamp", rot=-3),
       El(tag("LE RÉSULTAT DU VOTE DES SUPPORTERS", 50, BLANC), CX, 680, K["gagne"] - .1, None, "pop", rot=2)]
@scene(K["abonne"], trans="glitch", td=.18)
def s_cta(L, fr, t):
    gala_bg(L, t); tc = K["abonne"] + .3; pressed = t > tc
    bs = M.spring(t - K["abonne"], .45, 14)
    if pressed: b = t - tc; q = .12*math.exp(-b*12)*math.cos(b*30); bsx, bsy = 1 + q, 1 - q
    else: bsx = bsy = 1
    blit_sxy(L, sub_button(pressed), CX, 1100, bs*bsx, bs*bsy, -2)
    if pressed: sparks_burst(L, t, tc, CX, 1100, 14, (255, 230, 120), 340)
    cu = M.ease_io((t - K["abonne"])/.3); cx_, cy_ = lerp(980, CX + 60, cu), lerp(1600, 1120, cu)
    if pressed: cx_ += 160*M.ease_in((t - tc - .25)/.4); cy_ += 500*M.ease_in((t - tc - .25)/.4)
    put(L, cursor(), cx_, cy_, .9)
    if t > K["gagne"]: put(L, gold_ball(150), CX, 1480, M.spring(t - K["gagne"], .45, 12), 0)
    M.draw_all(L, fr, t, E_C)
CAM_C = [(K["abonne"], CX, 1100, 1.06), (K["mardi"], CX, 1000, 1.0), (K["gagne"], CX, 1150, 1.04)]

# --- 6. FIN : c'est qui ton Ballon d'or ?
E_F = [El(KW("C'EST QUI", NOIR, BLANC, 120), CX, 520, K["alors"], None, "stamp", rot=-3),
       El(KW("TON BALLON D'OR ?", GOLD, NOIR, 92), CX, 700, K["ton"] - .1, None, "stamp", rot=3),
       El(marker("ÉCRIS-LE EN COMMENTAIRE", "bcom", 70), CX, 1500, K["alors"] + .3, None, "slide_l", rot=-2)]
@scene(K["alors"], trans="whip", td=.25)
def s_fin(L, fr, t):
    gala_bg(L, t)
    put(L, gold_ball(200), CX, 1000 + 12*math.sin(t*4), M.spring(t - K["alors"], .45, 12), 5*math.sin(t*2))
    for i, f in enumerate(FAV): put(L, logo(f[1], 120), 140 + i*200, 1300, M.spring(t - K["alors"] - .1 - i*.06, .35, 14), 0)
    y = 1640 + 16*abs(math.sin(t*6)); ImageDraw.Draw(L).polygon([(CX - 46, y), (CX + 46, y), (CX, y + 56)], fill=ROUGE)
    M.draw_all(L, fr, t, E_F)
CAM_F = [(K["alors"], CX, 1000, 1.0), (K["bdo"], CX, 1100, 1.05)]

SC.sort(key=lambda s: s["t0"])
CAMS = {"s_hook": CAM_HOOK, "s_jury": CAM_J, "s_vrai": CAM_V, "s_fav": CAM_5, "s_out": CAM_O, "s_cta": CAM_C, "s_fin": CAM_F}
IMPACTS = [K["toi"], K["ballon"], K["elu"], K["supp"], K["ecris"], K["cinq"], K["champ"], K["b61"], K["meill"], K["elu2"], K["tenant"], K["a39"], K["abonne"] + .3, K["mardi"], K["ton"]]
PUNCH += IMPACTS

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
    cur = cur.convert("RGBA"); fx.vignette(cur, 90); fil_rouge(cur, fr, t)
    return cur.convert("RGB")
def draw(cv, fr, t, T):
    tv = max(0.0, t - PAD_IN); cv.paste(frame(fr, tv), (0, 0))
# ------------------------------------------------------------------ sons
P = PAD_IN
V5S = os.path.join(ROOT, "episodes", "lille_v5", "sfx"); RS = os.path.join(RENNES, "sfx"); BANK = os.path.join(ROOT, "assets", "sfx")
def X(t, name, g): return (P + t, name, g)
SFX = [X(0, "braam", .75), X(K["toi"], "stamp", .55), X(K["ballon"], "shimmer", .55), X(K["ballon"] + .1, "sparkle", .45),
       X(K["demain"] - .02, "whoosh1", .5), X(K["demain"] + .1, "drumroll", .3), X(K["remis"], "pop", .5), X(K["elu"], "stamp", .65), X(K["journ"], "typewriter", .4),
       X(K["mais"] - .05, "flashfx", .45), X(K["vrai"], "stamp", .5), X(K["supp"], "crowd", .55), X(K["supp"] + .05, "stamp", .6),
       X(K["ecris"], "stamp", .5)] + [X(K["ecris"] + k*.17 + .6, "rustle", .35) for k in range(5)] + [X(K["comm"], "notif", .5),
       X(K["cinq"] - .02, "whoosh2", .5), X(K["cinq"], "stamp", .6)] + \
      sum([[X(f[4] - .1, "whoosh3", .45), X(f[4], "stamp", .55), X(f[5], "stamp", .6), X(f[5] + .05, "crowd", .3)] for f in FAV], []) + \
      [X(K["derriere"] - .05, "flashfx", .45), X(K["kvara"], "pin", .5), X(K["messi"], "pin", .5), X(K["a39"], "stamp", .65),
       X(K["abonne"], "glitch", .45), X(K["abonne"] + .35, "pop", .6), X(K["abonne"] + .4, "ding", .45), X(K["mardi"], "stamp", .6), X(K["gagne"], "shimmer", .5),
       X(K["alors"] - .02, "whoosh1", .5), X(K["alors"], "stamp", .5), X(K["ton"], "stamp", .6), X(K["bdo"], "sparkle", .5), X(K["bdo"] + .4, "bell", .4)]
SFX_DIR = "/tmp/claude-0/sfx_bdo"
os.makedirs(SFX_DIR, exist_ok=True)
for nm in set(n for _, n, _ in SFX):
    src = next((p for p in (os.path.join(RS, nm + ".mp3"), os.path.join(V5S, nm + ".mp3"), os.path.join(BANK, nm + ".mp3")) if os.path.exists(p)), None)
    if nm in ("crowd", "whistle"): src = os.path.join(BANK, nm + ".mp3")
    dst = os.path.join(SFX_DIR, nm + ".mp3")
    if src and not os.path.lexists(dst): os.symlink(src, dst)
SFX = [s for s in SFX if os.path.exists(os.path.join(SFX_DIR, s[1] + ".mp3"))]
SFX = fx.sfx_variants(SFX, SFX_DIR, SFX_DIR + "_v")
SCENES = [Scene("bdo", TEXTE, draw, SFX, pad_in=P, pad_out=1.6)]

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
    p = os.path.join(out, f"bdosheet{'_' + only if only else ''}.jpg"); sheet.save(p, quality=82); return p

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--stills" in args:
        only = args[args.index("--stills") + 1] if len(args) > args.index("--stills") + 1 else None
        print(stills("/tmp/claude-0/aud", only)); sys.exit()
    out = args[0] if args else os.path.join(ROOT, "output", SLUG); os.makedirs(out, exist_ok=True)
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=[VOIX], sfx_dir=SFX_DIR + "_v", sfx_db=6.0, lufs=-14.0, crf=22, limit=True))
