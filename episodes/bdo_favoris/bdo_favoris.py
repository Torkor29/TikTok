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

TITLE = "~/ballon-dor $ ./pour-contre"
SLUG = "bdo_favoris"
VOIX = os.path.join(HERE, "voix", "voix.mp3")
TEXTE = open(os.path.join(HERE, "TEXTE.md")).read()
K = dict(ballon=.24, impossible=.92, predire=1.74, chaque=2.64, gagner=4.28, perdre=5.48,
         yamal=6.08, champ=6.7, a19=7.42, espagne=8.74, ymais=9.92, yldc=10.44,
         kane=11.28, b61=11.8, carriere=13.94, kmais=14.58, kcdm=16.1,
         mbappe=16.92, meill=17.56, mondial=19.54, mmais=20.2, liga=21.54,
         dembele=23.26, tenant=24.06, regagne=24.82, dmais=26.72, france=26.94,
         rodri=28.26, rchamp=29.14, elu=30.22, rmais=31.92, city=32.18,
         soir=34.74, seul=35.48, abonne=36.7, dis=38.2, qui=39.4, END=40.6)
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
REAL = True
_cut = {}
def CUT(n, h=900):
    k = (n, h)
    if k not in _cut:
        p = os.path.join(PH, n + ".png"); _cut[k] = paper_player(p, (0, 0) + Image.open(p).size, h, real=REAL)
    return _cut[k]
import pc_lib as _PL
def gold_ball(r=200, yq=0):
    """Trophée Ballon d'Or papier 3D (pc_lib.bdo_sprite), hauteur ≈ 3,2 r, ancré au centre."""
    k = ("gb", r, yq)
    if k not in _fc:
        sp = _PL.bdo_sprite(yq, 700); bb = sp.getchannel("A").getbbox(); sp = sp.crop(bb)
        h = int(3.2*r); sp = sp.resize((int(sp.width*h/sp.height), h), Image.LANCZOS); sp.info["anchor"] = (sp.width/2, sp.height/2)
        _fc[k] = shadowed(sp, k)
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
    LBL("BALLON D'OR · LE VOTE DES SUPPORTERS", "bhdr", font("mono", 30), GOLD, NOIR, padx=14, pady=5, rough=1.5).draw(cv, fr, CX, 140, 1, 0)


# ================================================================== EFFETS « AURA » (motion design, lumière additive)
import numpy as _np
_aur = {}
def _sil(sp, grow, blur):
    k = (id(sp), grow, blur)
    if k not in _aur:
        a0 = sp.getchannel("A").point(lambda v: 255 if v > 90 else 0)
        a = Image.new("L", (a0.width + 240, a0.height + 240), 0); a.paste(a0, (120, 120))   # marge : la lueur ne doit pas être coupée en rectangle
        if grow: a = a.filter(ImageFilter.MaxFilter(grow*2 + 1))
        _aur[k] = a.filter(ImageFilter.GaussianBlur(blur))
    return _aur[k]
def add_light(L, im, x, y):
    """Composite ADDITIF (lumière) d'une image RGB/RGBA sur L, centrée en (x, y)."""
    if im.mode == "RGBA":
        bg = Image.new("RGB", im.size, (0, 0, 0)); bg.paste(im, (0, 0), im); im = bg
    x0, y0 = int(x - im.width/2), int(y - im.height/2)
    box = (max(0, x0), max(0, y0), min(L.width, x0 + im.width), min(L.height, y0 + im.height))
    if box[2] <= box[0] or box[3] <= box[1]: return
    crop = im.crop((box[0] - x0, box[1] - y0, box[2] - x0, box[3] - y0))
    base = L.crop(box).convert("RGB"); L.paste(ImageChops.add(base, crop).convert("RGBA"), box[:2])
def aura(L, sp, x, y, t, col, power=1.0, seed=0):
    """Aura « super saiyan » : 3 couches de flammes lumineuses qui montent et ondulent autour de la silhouette (ancre pieds en x, y)."""
    if power <= .02: return
    ax, ay = sp.info["anchor"]; cx, cy = x - ax + sp.width/2, y - ay + sp.height/2
    for li, (grow, blur, stretch, amp) in enumerate(((10, 10, 1.05, .9), (26, 24, 1.12, .7), (50, 46, 1.22, .45))):
        m = _sil(sp, grow, blur)
        fl = 1 + .05*math.sin(t*23 + li*2 + seed) + .04*math.sin(t*37 + seed)
        sh = m.resize((int(m.width*(1 + .02*li)*fl), int(m.height*stretch*fl)))
        # ondulation des flammes : décalage horizontal sinusoïdal par bandes
        arr = _np.asarray(sh, _np.float32)
        hgt = arr.shape[0]; out = _np.zeros_like(arr)
        for yb in range(0, hgt, 12):
            d = int((10 + 8*li)*math.sin(yb*.035 - t*9 - li + seed)*(1 - yb/hgt))
            out[yb:yb + 12] = _np.roll(arr[yb:yb + 12], d, axis=1)
        k = amp*power*(.85 + .15*math.sin(t*17 + li + seed))
        rgb = _np.clip(out[..., None]/255*_np.array(col, _np.float32)*k*1.4, 0, 255).astype(_np.uint8)
        add_light(L, Image.fromarray(rgb, "RGB"), cx, cy + m.height/2 - sh.height/2 - 60 - 10*li)
def particles(L, x, y, w, h, t, col, n=40, seed=0, power=1.0):
    """Étincelles d'énergie qui montent (traînées lumineuses, additif)."""
    if power <= .02: return
    lay = Image.new("RGB", L.size, (0, 0, 0)); d = ImageDraw.Draw(lay); rng = random.Random(seed)
    for i in range(n):
        sp_ = 300 + 500*rng.random(); ph = rng.random(); px = x + (rng.random() - .5)*w
        yy = y - ((t*sp_ + ph*h) % h); ln = 18 + 40*rng.random(); wv = 6*math.sin(t*6 + i)
        c = tuple(int(v*power*(.6 + .4*rng.random())) for v in col)
        d.line([(px + wv, yy), (px + wv, yy + ln)], fill=c, width=3 + (i % 3))
    lay = ImageChops.add(lay.filter(ImageFilter.GaussianBlur(3)), lay)
    L.paste(ImageChops.add(L.convert("RGB"), lay).convert("RGBA"))
def bolt(L, x, y, t, col, seed, length=520, power=1.0):
    """Éclair qui crépite par intermittence (3 images sur 10)."""
    if power <= .02 or (int(t*30) + seed) % 10 > 2: return
    rng = random.Random(int(t*30)*7 + seed); pts = [(x, y)]; a = rng.uniform(-2.6, -.5)
    for k in range(9): px, py = pts[-1]; pts.append((px + math.cos(a + rng.uniform(-.7, .7))*length/9, py + math.sin(a + rng.uniform(-.7, .7))*length/9))
    lay = Image.new("RGB", L.size, (0, 0, 0)); d = ImageDraw.Draw(lay)
    d.line(pts, fill=tuple(int(v*power) for v in col), width=14); lay = lay.filter(ImageFilter.GaussianBlur(10))
    d = ImageDraw.Draw(lay); d.line(pts, fill=(int(255*power),)*3, width=4)
    L.paste(ImageChops.add(L.convert("RGB"), lay).convert("RGBA"))
_glow = {}
def glow_spot(L, x, y, r, col, a=1.0):
    k = (r, col)
    if k not in _glow:
        g = Image.new("L", (2*r, 2*r), 0); ImageDraw.Draw(g).ellipse([r*.3, r*.3, r*1.7, r*1.7], fill=255); g = g.filter(ImageFilter.GaussianBlur(r*.35))
        _glow[k] = Image.merge("RGB", [g.point(lambda v, c=c: v*c//255) for c in col])
    im = _glow[k] if a >= .99 else Image.eval(_glow[k], lambda v: int(v*a))
    add_light(L, im, x, y)
def flare(L, x, y, t, col, a=1.0):
    glow_spot(L, x, y, 160, col, .8*a)
    lay = Image.new("RGB", (900, 900), (0, 0, 0)); d = ImageDraw.Draw(lay)
    for ang in (0, 90):
        r_ = math.radians(ang + 8*math.sin(t*2)); dx, dy = 440*math.cos(r_), 440*math.sin(r_)
        d.line([(450 - dx, 450 - dy), (450 + dx, 450 + dy)], fill=tuple(int(c*a) for c in col), width=5)
    add_light(L, lay.filter(ImageFilter.GaussianBlur(2)), x, y)
def shock(L, t, t0, x, y, col, rmax=900):
    u = (t - t0)/.5
    if not 0 < u < 1: return
    lay = Image.new("RGB", L.size, (0, 0, 0)); d = ImageDraw.Draw(lay); r_ = rmax*M.ease_out(u)
    d.ellipse([x - r_, y - r_*.35, x + r_, y + r_*.35], outline=tuple(int(c*(1 - u)) for c in col), width=int(24*(1 - u)) + 2)
    L.paste(ImageChops.add(L.convert("RGB"), lay.filter(ImageFilter.GaussianBlur(4))).convert("RGBA"))
def grey(sp, k):
    """Désature + assombrit un sprite (perte de puissance au « mais »)."""
    if k <= .01: return sp
    key = (id(sp), round(k, 1))
    if key not in _aur:
        g = sp.convert("LA").convert("RGBA"); out = Image.blend(sp, g, k*.8); out = Image.eval(out.convert("RGB"), lambda v: int(v*(1 - .25*k))).convert("RGBA")
        out.putalpha(sp.getchannel("A")); out.info["anchor"] = sp.info["anchor"]; _aur[key] = out
    return _aur[key]
def dark_bg(L, t, col, key):
    vgrad(L, 0, H, tuple(int(c*.18) for c in col), (6, 6, 14)); d = ImageDraw.Draw(L)
    for k in range(40): d.ellipse([(k*137) % W, (k*71) % 1700 + 150, (k*137) % W + 4, (k*71) % 1700 + 154], fill=tuple(int(c*.5) for c in col))
def card(txt, ok, size=56):
    col = (30, 160, 80) if ok else (210, 30, 40)
    return LBL(("✔ " if ok else "✘ ") + txt, f"cd{txt}{ok}{size}", font("title", size), BLANC, col, padx=26, pady=12, rough=2)

def fil_rouge(cv, fr, t):
    LBL("BALLON D'OR 2026 · POUR / CONTRE", "fhdr", font("mono", 30), GOLD, NOIR, padx=14, pady=5, rough=1.5).draw(cv, fr, CX, 140, 1, 0)

# ================================================================== SCÈNES
FAVS = [  # nom, club, couleur d'aura, t0, t_pour, [pour], t_mais, contre, t_fin
    ("yamal", "barca", (255, 200, 60), K["yamal"], [(K["champ"], "CHAMPION DU MONDE À 19 ANS"), (K["espagne"] - .3, "CHAMPION D'ESPAGNE")], K["ymais"], "PAS DE LIGUE DES CHAMPIONS"),
    ("kane", "bayern", (255, 70, 60), K["kane"], [(K["b61"], "61 BUTS, RECORD PERSO")], K["kmais"], "NI LDC, NI COUPE DU MONDE"),
    ("mbappe", "real", (140, 200, 255), K["mbappe"], [(K["meill"], "MEILLEUR BUTEUR LDC + MONDIAL")], K["mmais"], "REAL : NI LIGA, NI LDC"),
    ("dembele", "psg", (90, 140, 255), K["dembele"], [(K["tenant"] - .2, "TENANT DU TITRE"), (K["regagne"], "RE-CHAMPION D'EUROPE")], K["dmais"], "LA FRANCE PERD LE MONDIAL"),
    ("rodri", "city", (120, 220, 255), K["rodri"], [(K["rchamp"], "CHAMPION DU MONDE"), (K["elu"], "MEILLEUR JOUEUR DU MONDIAL")], K["rmais"], "CITY : NI PL, NI LDC")]
NAMES = {"yamal": "YAMAL", "kane": "KANE", "mbappe": "MBAPPÉ", "dembele": "DEMBÉLÉ", "rodri": "RODRI"}

# --- 0. HOOK : les 5 favoris, auras, trophée
E_H = [El(KW("BALLON D'OR 2026", GOLD, NOIR, 96), CX, 410, -.3, K["yamal"] - .15, "stamp", "fly", rot=-2),
       El(KW("IMPOSSIBLE À PRÉDIRE", NOIR, BLANC, 76), CX, 550, K["impossible"] - .1, K["yamal"] - .15, "stamp", "fly", rot=2),
       El(card("UNE RAISON DE GAGNER", True, 60), CX, 1200, K["gagner"] - .25, K["yamal"] - .15, "stamp", "fly", rot=-3),
       El(card("UNE RAISON DE PERDRE", False, 60), CX, 1330, K["perdre"] - .3, K["yamal"] - .15, "stamp", "fly", rot=3)]
LINE = [("yamal", 150, 640, (255, 200, 60)), ("kane", 340, 600, (255, 70, 60)), ("dembele", 740, 640, (90, 140, 255)), ("mbappe", 940, 600, (140, 200, 255)), ("rodri", CX, 560, (120, 220, 255))]
@scene(0.0)
def s_hook(L, fr, t):
    dark_bg(L, t, (200, 160, 60), "h"); rays(L, (CX, 900), t, .6, 16, 1800, (70, 56, 20), .08, .25)
    glow_spot(L, CX, 860, 420, (120, 90, 20))
    put(L, gold_ball(140, round((t*.8) % 6.28/.3)*.3 % 6.28), CX, 860 + 10*math.sin(t*3), 1, 0)
    for i, (n, x, h, col) in enumerate(LINE):
        sp = CUT(n, h); y = 1930 + 30*(1 - M.spring(t + .3 - i*.05, .45, 12))
        aura(L, sp, x, y, t, col, .45, i); put(L, sp, x, y, 1, 0)
    particles(L, CX, 1900, W, 1400, t, (255, 220, 120), 40, 1)
    if t > K["perdre"] - .3: bolt(L, CX, 860, t, (255, 80, 60), 3)
    flare(L, CX - 60, 780, t, (255, 230, 160), .7)
    M.draw_all(L, fr, t, E_H)
CAM_HOOK = [(0, CX, 1000, 1.04), (K["gagner"], CX, 1050, 1.08), (K["perdre"], CX, 1000, 1.02)]

def make_player_scene(i, f):
    n, club, col, t0, pours, tm, contre = f
    t1 = FAVS[i + 1][3] if i + 1 < len(FAVS) else K["soir"]
    E = [El(KW(NAMES[n], col if n != "yamal" else GOLD, NOIR, 150), CX, 420, t0 - .05, t1 - .15, "stamp", "fly", rot=(-3, 3)[i % 2])] + \
        [El(card(tx, True, 52), CX, 590 + 110*j, tp - .1, tm - .05, "stamp", "shrink", rot=(-2, 2)[j % 2]) for j, (tp, tx) in enumerate(pours)] + \
        [El(card(contre, False, 60), CX, 610, tm, t1 - .15, "stamp", "fly", rot=-3)]
    def fn(L, fr, t):
        lost = M.ease_io(clamp((t - tm)/.35)); power = (1.25 if t > pours[0][0] else .7)*(1 - .85*lost)
        dark_bg(L, t, col, n); rays(L, (CX, 1150), t, .7, 16, 1800, tuple(int(c*.25*(1 - .6*lost)) for c in col), .1, .3)
        glow_spot(L, CX, 1250, 520, tuple(int(c*.45*(1 - .7*lost)) for c in col))
        put(L, logo(club, 220), 900, 860, M.spring(t - t0, .45, 14)*(1 - .3*lost), 8)
        sp = CUT(n, 1180); u = M.spring(t - t0 + .15, .45, 12)
        x = lerp(-600 if i % 2 == 0 else W + 600, CX, u); y = 1960 + (12*math.sin(t*40)*math.exp(-(t - tm)*5) if t > tm else 0)
        for (tp, _) in pours: shock(L, t, tp, CX, 1900, col)
        aura(L, sp, x, y, t, col, power, i)
        put(L, grey(sp, lost), x, y, 1, 0)
        particles(L, x, 1950, 700, 1500, t, col, 34, i, power)
        if t > pours[0][0]: bolt(L, x - 200, 1100, t, col, i, 480, power); bolt(L, x + 200, 900, t + .37, col, i + 5, 420, power)
        if t < tm: flare(L, x + 40, 1960 - 1180 + 120, t, tuple(min(255, c + 60) for c in col), .6*clamp((t - pours[0][0])/.3))
        if n == "kane" and pours[0][0] < t < tm:
            k = min(61, int(61*M.ease_out(clamp((t - pours[0][0])/.7)))); LBL(f"{k}", f"bk{k}", font("title", 190), NOIR, GOLD, padx=30, pady=6, rough=2).draw(L, fr, 210, 900, 1, -6)
        if t > tm: dark(L, .25*lost)
        M.draw_all(L, fr, t, E)
    fn.__name__ = f"s_{n}"
    scene(t0, trans=("whip", "flash")[i % 2], td=(.25, .15)[i % 2])(fn)
    return [(t0, CX, 1050, 1.0), (pours[0][0], CX, 1100, 1.08), (tm, CX, 1000, 1.0), (tm + .4, CX, 1150, 1.06)]
CAMS = {"s_hook": CAM_HOOK}
for i, f in enumerate(FAVS): CAMS[f"s_{f[0]}"] = make_player_scene(i, f)

# --- FIN
E_F = [El(KW("UN SEUL CE SOIR", GOLD, NOIR, 110), CX, 420, K["seul"] - .1, None, "stamp", rot=-3),
       El(KW("ABONNE-TOI POUR LE RÉSULTAT", NOIR, BLANC, 60), CX, 560, K["abonne"] - .05, None, "stamp", rot=2),
       El(marker("C'EST QUI ? EN COMMENTAIRE", "fcom", 52), CX, 1540, K["dis"] - .05, None, "slide_l", rot=-2)]
@scene(K["soir"], trans="flash", td=.15)
def s_fin(L, fr, t):
    dark_bg(L, t, (220, 170, 60), "f"); rays(L, (CX, 1000), t, .8, 18, 1800, (80, 60, 20), .1, .3)
    glow_spot(L, CX, 1000, 520, (160, 120, 30))
    put(L, gold_ball(200), CX, 1000 + 8*math.sin(t*3), M.spring(t - K["soir"], .45, 12), 0)
    particles(L, CX, 1700, 900, 1300, t, (255, 220, 120), 50, 4)
    bolt(L, CX - 160, 900, t, (255, 220, 120), 1, 400); bolt(L, CX + 160, 950, t + .4, (255, 220, 120), 2, 400)
    flare(L, CX - 70, 900, t, (255, 236, 170), .9)
    for i, f in enumerate(FAVS): put(L, logo(f[1], 120), 140 + i*200, 1360, M.spring(t - K["seul"] - i*.06, .35, 14), 0)
    if t > K["dis"]:
        y = 1660 + 16*abs(math.sin(t*6)); ImageDraw.Draw(L).polygon([(CX - 46, y), (CX + 46, y), (CX, y + 56)], fill=ROUGE)
    M.draw_all(L, fr, t, E_F)
CAMS["s_fin"] = [(K["soir"], CX, 1000, 1.06), (K["seul"], CX, 1000, 1.0), (K["dis"], CX, 1100, 1.04)]

SC.sort(key=lambda s: s["t0"])
IMPACTS = [K["gagner"], K["perdre"]] + sum([[f[4][0][0], f[5]] for f in FAVS], []) + [K["seul"]]
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
SFX = [X(0, "braam", .8), X(0, "riser", .35), X(K["impossible"], "stamp", .5), X(K["gagner"] - .2, "stamp", .6), X(K["perdre"] - .25, "thunder", .5), X(K["perdre"] - .2, "stamp", .6)] + \
      sum([[X(f[3] - .1, "whoosh3", .5), X(f[3], "boom", .45)] + [X(tp - .1, "zap", .5) for tp, _ in f[4]] + [X(tp, "stamp", .55) for tp, _ in f[4]] +
           [X(f[4][0][0], "shimmer", .45), X(f[5], "buzzer", .45), X(f[5] + .02, "stamp", .65), X(f[5] + .1, "groan", .3)] for f in FAVS], []) + \
      [X(K["soir"] - .05, "flashfx", .5), X(K["soir"], "riser", .4), X(K["seul"], "boom", .55), X(K["seul"] + .05, "sparkle", .5), X(K["abonne"], "pop", .5),
       X(K["dis"], "notif", .55), X(K["qui"] + .3, "bell", .4)]
SFX_DIR = "/tmp/claude-0/sfx_bdof"
os.makedirs(SFX_DIR, exist_ok=True)
for nm in set(n for _, n, _ in SFX):
    src = next((p for p in (os.path.join(RS, nm + ".mp3"), os.path.join(V5S, nm + ".mp3"), os.path.join(BANK, nm + ".mp3")) if os.path.exists(p)), None)
    if nm in ("crowd", "whistle"): src = os.path.join(BANK, nm + ".mp3")
    dst = os.path.join(SFX_DIR, nm + ".mp3")
    if src and not os.path.lexists(dst): os.symlink(src, dst)
SFX = [s for s in SFX if os.path.exists(os.path.join(SFX_DIR, s[1] + ".mp3"))]
SFX = fx.sfx_variants(SFX, SFX_DIR, SFX_DIR + "_v")
SCENES = [Scene("bdof", TEXTE, draw, SFX, pad_in=P, pad_out=1.6)]

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
    p = os.path.join(out, f"bdofsheet{'_' + only if only else ''}.jpg"); sheet.save(p, quality=82); return p

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--stills" in args:
        only = args[args.index("--stills") + 1] if len(args) > args.index("--stills") + 1 else None
        print(stills("/tmp/claude-0/aud", only)); sys.exit()
    out = args[0] if args else os.path.join(ROOT, "output", SLUG); os.makedirs(out, exist_ok=True)
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=[VOIX], sfx_dir=SFX_DIR + "_v", sfx_db=6.0, lufs=-14.0, crf=22, limit=True))
