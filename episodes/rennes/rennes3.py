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
import pc_over; pc_over.install(globals())
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

TITLE = "~/histoires $ ./rennes"
SLUG = "rennes_v3"
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

# ================================================================== v2 : système de mouvement (engine/motion.py, MOTION.md)
import motion as M
from motion import El, words, walk, arc, ground_shadow
CREST = lambda h: shadowed(sticker("rennes", h), ("crest", h))
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

pc_over.install(globals())
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

# ================================================================== SCÈNES v2
def stripes_bg(L, a=(196, 22, 32), b=(26, 24, 28), w_=140, key="rs", t=0):
    paper_fill(L, a, key); d = ImageDraw.Draw(L); off = (t*40) % (2*w_)
    for x in range(-H - 2*w_, L.width + 2*w_, 2*w_): d.polygon([(x + off, 0), (x + w_ + off, 0), (x + w_ + H*.35 + off, L.height), (x + H*.35 + off, L.height)], fill=b)
H0 = 2.25                                                       # fin du hook
# --- 0. HOOK : le club le plus maudit
E_CAT = [El(CREST(520), CX, 1180, -.3, H0 - .15, "pop", "shrink", 1, -3, .6)] + \
    words(lambda w, i: KW(w, ROUGE if w == "MAUDIT" else NOIR, BLANC, 150 if w == "MAUDIT" else 112),
          [("LE CLUB", -.5), ("LE PLUS", -.4), ("MAUDIT", -.25), ("DE FRANCE", K["france0"] - .06)], CX, 540, maxw=760, out=H0 - .2)
@scene(0.0)
def s_cat(L, fr, t):
    paper_fill(L, (30, 26, 36), "night"); rays(L, (CX, 1060), t, .9, 14, 1700, (110, 20, 30), .1, .3)
    M.draw_all(L, fr, t, E_CAT[:1])
    if t > K["maudit"] - .05:                                   # fissure qui se propage dans l'écusson
        u = M.ease_out((t - K["maudit"] + .05)/.3); pts = [(CX - 70, 940), (CX - 10, 1070), (CX - 60, 1180), (CX + 20, 1310), (CX - 10, 1420)]
        n = 1 + u*(len(pts) - 1); seg = pts[:int(n) + 1]
        if int(n) < len(pts) - 1: a_, b_ = pts[int(n)], pts[int(n) + 1]; f = n - int(n); seg = pts[:int(n) + 1] + [(lerp(a_[0], b_[0], f), lerp(a_[1], b_[1], f))]
        ImageDraw.Draw(L).line(seg, fill=(250, 250, 246), width=10, joint="curve")
        sparks_burst(L, t, K["maudit"], CX - 40, 1070, 10, (250, 250, 246), 160)
    draw_cat(L, lerp(-260, W + 260, clamp((t + .25)/2.4)), 1560, t, .95)
    M.draw_all(L, fr, t, E_CAT[1:])
CAM_CAT = [(0, CX, 980, 1.06), (K["maudit"], CX, 940, 1.12), (H0, CX, 980, 1.02)]

# --- 1. 6-0 puis 48 ans
E_HOOK = words(lambda w, i: KW(w, NOIR, BLANC, 150), [("RENNES", H0 + .05)], CX, 520, out=K["attendu"] - .15) + \
    [El(stampl("PREMIER MATCH", ROUGE, 70), CX, 1340, m(1.0), K["attendu"] - .15, "stamp", "fly", 1, -5)] + \
    [El(KW("48 ANS", JAUNE, NOIR, 190), CX, 1480, K["ans48"] - .05, None, "stamp", rot=-4),
     El(tag("POUR UN TROPHÉE", 64, BLANC), CX, 1660, K["trophee"] - .25, None, "pop", rot=3)]
@scene(H0, trans="whip", td=.25)
def s_hook(L, fr, t):
    stripes_bg(L, key="hook", t=t); dark(L, .2)
    if t < K["attendu"] + .1:
        scoreboard(L, CX, 1060, t, [(0, 0, 0)] + [(K["sixzero"] + i*.09, 0, i + 1) for i in range(6)], "RENNES", "ADVERSAIRE", 150,
                   board_in(t, H0 + .15, K["attendu"] - .15))
    else:
        u = M.spring(t - K["attendu"], .55, 11); put(L, shadowed(scale_stand(), "stand"), CX, lerp(2300, 1250, u), 1.1)
        c = M.ease_out((t - K["attendu"] - .2)/1.2); cobweb(L, CX - 30, 760, 240*c, 1); cobweb(L, 0, 300, 380*c, 1)
        for k in range(18):                                     # poussière qui tombe dans la lumière
            yy = (t*60 + k*97) % 1500 + 300; ImageDraw.Draw(L).ellipse([(k*61) % W, yy, (k*61) % W + 5, yy + 5], fill=(230, 210, 200))
    M.draw_all(L, fr, t, E_HOOK)
CAM_HOOK = [(H0, CX, 980, 1.0), (K["sixzero"] - .1, CX, 1060, 1.14), (K["attendu"], CX, 1000, 1.0), (K["ans48"], CX, 1200, 1.08), (K["y1901"], CX, 1100, 1.0)]

# --- 2. 1901 : étudiants, écusson, 6-0
foot.KITS["rennes"] = dict(kind="plain", c1=(214, 26, 34), sleeve=(214, 26, 34), shorts=(24, 22, 26), socks=(24, 22, 26), trim=(250, 250, 246))
STU = [foot.Player("etu0", hair=(70, 50, 30)), foot.Player("etu1", hair=(40, 30, 20))]
for _p in STU: _p.hat = "boater"
E_1901 = [El(stampl("1901", (110, 70, 40), 200), CX, 620, K["y1901"], K["premier"] - .2, "stamp", "fly", 1, -4),
          El(CREST(380), CX, 1060, K["stade"] - .08, K["premier"] - .2, "pop", "shrink", 1, 0),
          El(stampl("POUR L'ADVERSAIRE", ROUGE, 70), CX, 1420, K["adv"], None, "stamp", rot=-6),
          El(tag("1er MATCH DE L'HISTOIRE", 54, CREME), CX, 620, K["premier"], None, "pop", rot=2)]
@scene(K["y1901"], trans="tear", td=.3)
def s_1901(L, fr, t):
    paper_fill(L, (214, 190, 146), "sep")
    for k in range(10):
        yy = (t*30 + k*173) % H; ImageDraw.Draw(L).ellipse([(k*101) % W, yy, (k*101) % W + 4, yy + 4], fill=(240, 226, 196))
    if t < K["premier"] + .1:
        for i, (x0, x1) in enumerate(((-200, 310), (W + 200, 770))):
            t0 = K["etudiants"] - .1 + i*.12; u = clamp((t - t0)/.9); xs = lerp(x0, x1, M.ease_out(u))
            if t > K["premier"] - .2: xs += (-1 if i == 0 else 1)*900*M.ease_in((t - K["premier"] + .2)/.3)
            mv = 0 < u < 1; legs, arms, bob = walk(t, 9, 22) if mv else ((0, 0), (14, 14), 0)
            if t > t0: STU[i].draw(L, fr, xs, 1660 + bob, s=.78, kit="suit", legs=legs, arms=arms, mood="happy", t=t, look=(1 if i == 0 else -1, 0))
    if t > K["premier"] - .1:
        v = board_in(t, K["premier"] - .1)
        foot.draw_goal(L, fr, CX, 1640, 640, 300, 0, 1, t)
        for i in range(6):
            ti = K["sz2"] - .25 + i*.13
            if ti < t < ti + .3:
                u = (t - ti)/.3; bx, by = arc((CX + (i - 2.5)*90, 1900), (CX + (i - 2.5)*70, 1520), 160, u); ball(L, fr, bx, by, .7, t, 1700)
        scoreboard(L, CX, 1080, t, [(0, 0, 0)] + [(K["sz2"] + i*.13, 0, i + 1) for i in range(6)], "RENNES", "FC RENNAIS", 150, v)
    M.draw_all(L, fr, t, E_1901)
CAM_1901 = [(K["y1901"], CX, 960, 1.0), (K["etudiants"], CX, 1150, 1.08), (K["stade"], CX, 1060, 1.12), (K["premier"], CX, 1050, 1.0),
            (K["sz2"], CX, 1250, 1.1), (K["adv"], CX, 1200, 1.04)]

# --- 3. 1929 : la porte claque, 100 matchs amicaux
E_1929 = [El(stampl("1929", NOIR, 170), CX, 620, K["y1929"], K["pendant3"] - .15, "stamp", "fly", 1, -3),
          El(stampl("UNE CENTAINE !", ROUGE, 110), CX, 1470, K["centaine"], None, "stamp", rot=-8)]
@scene(K["y1929"], trans="whip", td=.25)
def s_1929(L, fr, t):
    paper_fill(L, (226, 214, 188), "1929")
    if t < K["pendant3"] + .2:
        dr = door("LIGUE"); ex = M.ease_in((t - K["pendant3"] + .15)/.3) if t > K["pendant3"] - .15 else 0
        op = 1 - M.spring(t - K["claque"], .3, 22) if t > K["claque"] else 1          # ouverte -> claque (rebond)
        sxv = max(.08, 1 - .85*clamp(op))
        dx = -dr.width/2*(1 - sxv)                                     # charnière à gauche
        if ex < .02: ImageDraw.Draw(L).rectangle([CX - dr.width/2 + 20, 1200 - 360, CX + dr.width/2 - 20, 1200 + 380], fill=(30, 24, 20))
        blit_sxy(L, dr, CX + dx, 1200 + 900*ex*ex, sxv, 1, 0)
        puffs(L, t, K["porte"], CX, 1590, 12)
    else:
        n = min(100, int(100*M.ease_io((t - K["pendant3"] - .1)/2.0)))
        d = ImageDraw.Draw(L); grow = lambda i: clamp((t - K["pendant3"] - .1 - 2.0*i/100)/.08)
        for i in range(100):
            g_ = grow(i)
            if g_ <= 0: break
            g, j = divmod(i, 5); gx = 140 + (g % 5)*170; gy = 820 + (g//5)*150
            if j < 4: d.line([(gx + j*28, gy), (gx + j*28, gy + 100*g_)], fill=NOIR, width=9)
            else: d.line([(gx - 12, gy + 80), (gx - 12 + 112*g_, gy + 80 - 64*g_)], fill=ROUGE, width=9)
        kword(f"{n} MATCHS AMICAUX", NOIR, BLANC, 76).draw(L, fr, CX, 680, .6 + .4*M.spring(t - K["pendant3"], .5, 14), 2)
    M.draw_all(L, fr, t, E_1929)
CAM_1929 = [(K["y1929"], CX, 980, 1.0), (K["claque"] - .2, CX, 1150, 1.1), (K["pendant3"], CX, 1050, 1.0), (K["centaine"], CX, 1150, 1.06)]

# --- 4. POKOU, encensé par Pelé
POKOU = foot.Player("rpokou", hair=(24, 20, 18), skin=(96, 62, 44))
E_POK = [El(pin_tag("LAURENT POKOU", 64), 330, 860, K["pokou"] - .05, None, "drop", rot=-3, dist=600),
         El(tag("ANNÉES 70", 54, CREME), CX, 520, K["an70"] + .05, K["pele"] - .2, "pop", "shrink", rot=2)]
@scene(K["an70"], trans="flash", td=.15)
def s_pokou(L, fr, t):
    vgrad(L, 0, H, (16, 18, 40), (40, 40, 70))
    for k in range(2): rays(L, (CX + (-1)**k*500, 1900), t*(.6 + .2*k), .55, 3, 2400, (255, 250, 210), .05, .5*(-1)**k)
    d = ImageDraw.Draw(L); d.rectangle([0, 1640, W, H], fill=(40, 110, 60))
    per = .7; ph = (t % per)/per; kick = math.exp(-((ph - .02)/.06)**2)
    POKOU.draw(L, fr, CX, 1660, s=1.2, kit="rennes", legs=(0, -45*kick), arms=(28 + 8*math.sin(t*9), 28 - 8*math.sin(t*9)), mood="happy", t=t, look=(0, -1))
    bx, by = arc((CX + 70, 1590), (CX + 70, 1590), 360, ph); ball(L, fr, bx, by, .8, t, 1650)
    if t > K["ivoirien"] - .1:
        u = M.spring(t - K["ivoirien"] + .1, .5, 10); flag_civ(L, 800, lerp(1300, 640, u), t, .9)
    if t > K["pele"] - .15:
        u = (t - K["pele"] + .15)/.3; hy = 1660 - 1.2*560*.955
        if u < 1: put(L, crown(), CX, lerp(200, hy, u*u), .55, 10*(1 - u))
        else: b = u - 1; q = .15*math.exp(-b*4)*math.cos(b*9); blit_sxy(L, crown(), CX, hy + 4*math.sin(t*3), .55*(1 + q), .55*(1 - q), 0)
        fx.wipe(L, fr, marker("ENCENSÉ PAR PELÉ", "rpele", 84), CX, 540, t, K["pele"], -2)
        for k in range(8):
            a = k*math.pi/4 + t*1.5; put(L, spark(36), CX + 230*math.cos(a), hy + 40 + 120*math.sin(a), .7 + .3*math.sin(t*9 + k), t*90)
    M.draw_all(L, fr, t, E_POK)
CAM_POKOU = [(K["an70"], CX, 1000, 1.0), (K["ivoirien"], 650, 1000, 1.06), (K["pokou"], CX, 1100, 1.1), (K["pele"] - .1, CX, 900, 1.16), (K["gagne"], CX, 960, 1.0)]

# --- 5. Coupes 65 / 71, puis plus rien
E_CUP = [El(KW("COUPE DE FRANCE", JAUNE, NOIR, 100), CX, 640, K["gagne"] + .3, K["rien"] - .2, "stamp", "fly", rot=-2),
         El(KW("PUIS… PLUS RIEN.", NOIR, BLANC, 110), CX, 640, K["rien"], None, "stamp", rot=-3),
         El(shelf("TROPHÉES"), CX, 1250, K["gagne"], None, "slide_r", s=1.15, idle=.2),
         El(cup_gold(380), 330, 1222, K["y65"] - .1, None, "drop", idle=.4, dist=800), El(tag("1965", 50, CREME), 330, 1390, K["y65"] + .1, None, "pop", rot=-2),
         El(cup_gold(380), 740, 1222, K["y71"] - .1, None, "drop", idle=.4, dist=800), El(tag("1971", 50, CREME), 740, 1390, K["y71"] + .1, None, "pop", rot=2)]
@scene(K["gagne"], trans="whip", td=.25)
def s_cups(L, fr, t):
    paper_fill(L, (60, 30, 32), "wall2")
    M.draw_all(L, fr, t, E_CUP[2:])
    if t > K["rien"] - .05:
        u = M.ease_out((t - K["rien"])/1.3); dark(L, .5*u); cobweb(L, 0, 0, 520*u, 1)
        d = ImageDraw.Draw(L)
        for k in range(30):
            yy = (t*50 + k*67) % 1300 + 500; d.ellipse([(k*97) % W, yy, (k*97) % W + 5, yy + 5], fill=(170, 160, 150))
    M.draw_all(L, fr, t, E_CUP[:2])
CAM_CUPS = [(K["gagne"], CX, 1000, 1.0), (K["y65"] - .2, 360, 1080, 1.14), (K["y71"] - .2, 720, 1080, 1.14), (K["rien"], CX, 1000, 1.0), (K["question"], CX, 960, 1.06)]

# --- 6. CTA QUIZ
QOUT = K["abonne"] - .25
E_Q = [El(mono("QUESTION POUR LES VRAIS", 54, ROUGE), CX, 520, K["question"], K["quel"] - .15, "pop", "fly", rot=-2)] + \
    words(lambda w, i: KW(w, JAUNE if i == 2 else BLANC, NOIR, 82), [("QUEL FUTUR", K["quel"] - .03), ("GARDIEN", K["gardien"] - .03),
          ("DE CHELSEA", K["chelsea"] - .05), ("A JOUÉ À RENNES ?", K["rq"] - .1)], CX, 600, maxw=1000, out=QOUT) + \
    [El(marker("RÉPONDS EN COMMENTAIRE", "rrep", 70), CX, 1430, K["reponds"] - .05, QOUT, "slide_l", "slide_r", rot=2)] + \
    [El(KW("MERCI !", JAUNE, NOIR, 130), CX, 560, K["chaine"] - .1, None, "stamp", rot=-3)]
@scene(K["question"], trans="glitch", td=.18)
def s_quiz(L, fr, t):
    paper_fill(L, (20, 30, 76), "quiz"); rays(L, (CX, 1050), t, .6, 16, 1700, (34, 48, 110), .1, .3)
    if t < QOUT + .25:
        ex = M.ease_in((t - QOUT)/.25) if t > QOUT else 0
        lay = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); foot.Player("rgk", hair=(40, 30, 20)).draw(lay, fr, 450, 860, s=1.1, kit="gk", arms=(100 + 10*math.sin(t*3), 100 - 10*math.sin(t*3)), t=t)
        a = lay.getchannel("A"); rim = Image.new("RGBA", lay.size, (140, 150, 200, 255)); rim.putalpha(a.filter(ImageFilter.MaxFilter(9)))
        sil = Image.new("RGBA", lay.size, (8, 8, 12, 255)); sil.putalpha(a); rim.alpha_composite(sil); rim.info["anchor"] = (450, 860)
        put(L, rim, CX, 1580 + 900*ex*ex, M.spring(t - K["question"] - .1, .5, 12))
        put(L, qmark(), CX, 960 + 12*math.sin(t*4) + 900*ex*ex, .55*M.spring(t - K["question"] - .25, .4, 14), 6*math.sin(t*3))
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
CAM_QUIZ = [(K["question"], CX, 980, 1.0), (K["reponds"], CX, 1100, 1.05), (QOUT, CX, 940, 1.1), (K["like"], CX, 1200, 1.1), (K["y2009"], CX, 1000, 1.0)]

# --- 7. GUINGAMP ×2
E_G = [El(stampl("UN CLUB DE LIGUE 2 !", ROUGE, 80), CX, 1420, K["l2"] - .05, K["y2014"] - .2, "stamp", "fly", rot=-6),
       El(stampl("RE-GUINGAMP…", NOIR, 72), CX, 1420, K["reguin"] - .05, None, "stamp", rot=5)]
@scene(K["y2009"], trans="whip", td=.25)
def s_guingamp(L, fr, t):
    paper_fill(L, (238, 230, 212), "gbg")
    fl = clamp((t - K["y2014"] + .15)/.35); sx = abs(math.cos(math.pi*fl)); face = "FINALE 2014" if fl > .5 else "FINALE 2009"
    tin = M.spring(t - K["y2009"] - .05, .45, 13)
    blit_sxy(L, ticket(face, "STADE DE FRANCE", ROUGE, 660), CX, 640 - 30*math.sin(math.pi*fl), max(.03, sx)*tin, tin*(1 + .06*math.sin(math.pi*fl)), -3)
    second = t > K["y2014"]
    seq = [(0, 0, 0), (K["guin1"] - .35, 0, 1), (K["guin1"] - .05, 1, 1), (K["guin1"] + .25, 1, 2)] if not second else [(0, 0, 0), (K["guin1"] - .35, 0, 1), (K["guin1"] - .05, 1, 1), (K["guin1"] + .25, 1, 2), (K["y2014"] + .05, 0, 0), (K["refinale"] + .1, 0, 1), (K["refinale"] + .45, 0, 2)]
    scoreboard(L, CX, 1100, t, seq, "RENNES", "GUINGAMP", 150, board_in(t, K["y2009"] + .2))
    if second: draw_cat(L, lerp(W + 280, -280, clamp((t - K["refinale"])/1.6)), 1700, t, .7, face=-1)
    if t > K["reguin"]:
        u = clamp((t - K["reguin"])/1.4); tx = lerp(-320, W + 320, u); put(L, tractor(), tx, 1830 + 4*math.sin(t*30), .7, 2*math.sin(t*20))
        for k in range(4):
            pu = ((t*3 + k*.25) % 1); ImageDraw.Draw(L).ellipse([tx - 120 - 40*pu, 1660 - 160*pu, tx - 120 + 40*pu, 1660 - 160*pu + 80*pu], fill=(150, 150, 150))
    M.draw_all(L, fr, t, E_G)
CAM_GUIN = [(K["y2009"], CX, 960, 1.0), (K["guin1"] - .3, CX, 1100, 1.12), (K["l2"], CX, 1250, 1.05), (K["y2014"] - .1, CX, 800, 1.12),
            (K["refinale"] + .1, CX, 1100, 1.08), (K["reguin"], CX, 1350, 1.0)]

# --- 8. CAMAVINGA
E_C = [El(mono("CENTRE DE FORMATION", 56), CX, 620, K["centre"], K["camp"] - .1, "pop", "fly", rot=-2),
       El(tent(), 280, 1180, K["camp"] - .1, K["pro"] - .1, "drop", "slide_l", dist=700, idle=.3),
       El(tag("NÉ DANS UN CAMP DE RÉFUGIÉS", 50, CREME), CX, 620, K["camp"] + .1, K["maison"] - .1, "pop", "fly", rot=2),
       El(house(), 760, 1180, K["maison"] - .1, K["pro"] - .1, "drop", "slide_r", dist=700, idle=.3),
       El(tag("SA MAISON BRÛLE", 54, ROUGE, BLANC), CX, 620, K["brule"] + .05, K["pro"] - .1, "stamp", "fly", rot=-2),
       El(stampl("PRO À 16 ANS", ROUGE, 120), CX, 1380, K["pro"] - .05, K["eduardo"] - .15, "stamp", "shrink", rot=-6),
       El(shadowed(photo_card(*CAMA, 820), "camac"), CX, 1050, K["eduardo"] - .08, None, "rise", rot=-3, dist=1400),
       El(marker("EDUARDO CAMAVINGA", "rcam", 88), CX, 1470, K["cama"], None, "slide_l", rot=2)]
CAMAK = foot.Player("rcamak", hair=(20, 16, 14), skin=(96, 62, 44))
@scene(K["pendantce"], trans="tear", td=.3)
def s_cama(L, fr, t):
    paper_fill(L, (58, 140, 76), "cpitch"); d = ImageDraw.Draw(L)
    for k in range(0, H, 220): d.rectangle([0, k, W, k + 110], fill=(70, 156, 88))
    M.draw_all(L, fr, t, E_C[:4])
    if K["brule"] < t < K["pro"] + .1:
        g = clamp((t - K["brule"])/.5); a_ = 1 - M.ease_in((t - K["pro"] + .1)/.2) if t > K["pro"] - .1 else 1
        if a_ > .05:
            flames(L, 760, 1000, t, (.6 + .6*g)*a_)
            for k in range(5):
                pu = ((t*.8 + k*.2) % 1); r_ = 30 + 60*pu; ImageDraw.Draw(L).ellipse([760 - 80 + 40*k - r_, 900 - 300*pu - r_, 760 - 80 + 40*k + r_, 900 - 300*pu + r_], fill=(90, 90, 96))
    if t < K["eduardo"] - .1:
        age = .45 if t < K["pro"] - .05 else lerp(.45, .75, M.spring(t - K["pro"] + .05, .5, 10))
        ex = M.ease_in((t - K["eduardo"] + .3)/.2) if t > K["eduardo"] - .3 else 0
        kin = M.spring(t - K["gamin"] + .1, .5, 12)
        CAMAK.draw(L, fr, CX, 1680 + 900*ex, s=.95*kin, age=age, kit="rennes", arms=(20, 20), mood="sad" if K["brule"] < t < K["pro"] else "happy", t=t)
    M.draw_all(L, fr, t, E_C[4:])
CAM_CAMA = [(K["pendantce"], CX, 980, 1.0), (K["camp"], 330, 1150, 1.12), (K["maison"], 740, 1100, 1.12), (K["pro"], CX, 1250, 1.05),
            (K["eduardo"], CX, 1050, 1.08), (K["avril"], CX, 1000, 1.0)]

# --- 9. FINALE 2019
E_F = [El(KW("FINALE 2019", JAUNE, NOIR, 110), CX, 620, K["y2019"] - .05, None, "stamp", rot=-3),
       El(logo("psg", 200), CX, 1600 - 100, K["psg"] - .05, K["revient"] - .1, "pop", "shrink", rot=6),
       El(tag("4 FOIS TENANT DU TITRE", 60, NAVY, BLANC), CX, 1360 + 0, K["finale19"] + .1, K["neymar"] - .15, "pop", "fly", rot=-2),
       El(pin_tag("NEYMAR", 60), 300, 1360, K["neymar"] - .05, None, "drop", rot=-4, dist=500),
       El(pin_tag("MBAPPÉ", 60), 780, 1360, K["mbappe"] - .05, K["expulse"] + .25, "drop", "drop_out", rot=3, dist=500),
       El(stampl("EXPULSÉ", ROUGE, 96), 760, 1560 - 80, K["expulse"] + .05, None, "stamp", rot=-8)]
@scene(K["avril"], trans="whip", td=.25)
def s_final(L, fr, t):
    vgrad(L, 0, H, (10, 14, 40), (30, 36, 80)); d = ImageDraw.Draw(L)
    for k in range(60): d.ellipse([(k*67) % W, 1640 + (k*31) % 260, (k*67) % W + 9, 1649 + (k*31) % 260], fill=(255, 240, 180) if (k + fr//4) % 6 == 0 else (60, 60, 90))
    scoreboard(L, CX, 1030, t, [(0, 0, 0), (K["deuxzero"] - .15, 0, 1), (K["deuxzero"] + .15, 0, 2), (K["revient"], 1, 2), (K["deuxdeux"], 2, 2)],
               "RENNES", "PSG", 160, board_in(t, K["y2019"] + .1))
    for g in (K["revient"], K["deuxdeux"]):
        fx.shockwave(L, t, g, CX - 210, 1030, .4, 500, (255, 236, 150))
    if t > K["expulse"] - .25:
        u = clamp((t - K["expulse"] + .25)/.25)
        if u < 1: put(L, red_card(), 780, lerp(2200, 1260, M.ease_out(u)), 1 + .6*(1 - u), lerp(160, 12, M.ease_out(u)))
        else: b = t - K["expulse"]; q = .12*math.exp(-b*14)*math.cos(b*36); blit_sxy(L, red_card(), 780, 1260, 1 + q, 1 - q, 12)
    camera_flashes(L, fr, "rfl", t - K["avril"] - .4, 6.0, 30, (60, 1650, 1020, 1880))
    M.draw_all(L, fr, t, E_F)
CAM_FINAL = [(K["avril"], CX, 960, 1.0), (K["neymar"] - .1, CX, 1150, 1.08), (K["deuxzero"] - .2, CX, 1030, 1.16), (K["revient"], CX, 1030, 1.1),
             (K["deuxdeux"], CX, 1030, 1.18), (K["mbappe2"], 760, 1300, 1.14), (K["tab"], CX, 1100, 1.0)]

# --- 10. TIRS AU BUT
PEN_R = [(K["tab"] + .3 + i*.55, "ok") for i in range(6)]
PEN_P = [(K["tab"] + .55 + i*.55, "ok") for i in range(5)] + [(K["rate"], "ko")]
TB = K["ans48b"] - .1
E_P = [El(KW("TIRS AU BUT", BLANC, NOIR, 100), CX, 520, K["tab"], TB, "stamp", "fly", rot=-2),
       El(closet(), CX + 230, 1300, K["tab"] + .3, K["nkunku"] - .25, "pop", "slide_r", idle=.2),
       El(marker("HATEM BEN ARFA", "rba", 80), CX - 130, 960, K["benarfa"] - .05, K["nkunku"] - .25, "slide_l", "slide_l", rot=-2),
       El(stampl("MARQUE !", (40, 150, 70), 100), CX - 150, 1560, K["marque"] - .05, K["nkunku"] - .25, "stamp", "shrink", rot=-8),
       El(pin_tag("NKUNKU", 60), CX, 1580, K["nkunku"] - .1, TB, "drop", "shrink", rot=3, dist=600),
       El(stampl("RATÉ !", ROUGE, 150), CX, 1080, K["rate"] + .05, TB, "stamp", "shrink", rot=-10),
       El(KW("TERMINÉS !", JAUNE, NOIR, 170), CX, 1300, K["termine"] + .05, None, "stamp", rot=-4),
       El(CREST(420), CX, 860, K["termine"] + .25, None, "pop", rot=0)]
@scene(K["tab"], trans="flash", td=.15)
def s_pens(L, fr, t):
    vgrad(L, 0, H, (10, 14, 40), (30, 36, 80))
    rows_a = 1 - M.ease_in((t - TB)/.25) if t > TB else 1
    if rows_a > .02:
        for y, nm, res in ((680, "RENNES", PEN_R), (820, "PSG", PEN_P)):
            mono(nm, 40, NOIR).draw(L, fr, 120, y, rows_a, 0)
            if rows_a > .9: pen_dots(L, 600, y, t, 0, res, r=40, gap=100)
    M.draw_all(L, fr, t, E_P[1:2])
    if K["placard"] - .3 < t < K["nkunku"]:                    # la carte sort du placard
        u = M.spring(t - K["placard"] + .15, .55, 9); ex = M.ease_in((t - K["nkunku"] + .25)/.25) if t > K["nkunku"] - .25 else 0
        put(L, shadowed(photo_card(*BENARFA, 560), "bac"), lerp(CX + 230, CX - 150, u) - 1200*ex, 1300 - 40*math.sin(math.pi*clamp(u)), .35 + .65*clamp(u), lerp(8, -4, clamp(u)))
    if K["nkunku"] - .2 < t < TB + .3:
        a = M.spring(t - K["nkunku"] + .2, .5, 12)*(1 - (M.ease_in((t - TB)/.25) if t > TB else 0))
        if a > .05:
            foot.draw_goal(L, fr, CX, 1300, int(700*a), int(360*a), 0, 1, t)
            u = clamp((t - K["nkunku"] - .05)/.55)
            if 0 < u < 1: bx, by = arc((CX, 1760), (1260, 980), 330, u); ball(L, fr, bx, by, .95 - .45*u, t)
    if t > TB:                                                   # bannière déchirée
        lb = KW("48 ANS DE MALÉDICTION", NOIR, BLANC, 84); sp = lb.v[0]; hw = sp.width//2
        v = M.spring(t - TB, .5, 13); u = M.ease_in((t - K["termine"])/.5) if t > K["termine"] else 0
        if u <= 0: blit_sxy(L, sp, CX, 1080, v, v, -2)
        else:
            for side, part in ((-1, sp.crop((0, 0, hw, sp.height))), (1, sp.crop((hw, 0, sp.width, sp.height)))):
                part.info["anchor"] = (part.width/2 if side < 0 else part.width/2, part.height/2)
                put(L, part, CX + side*(hw/2 + 520*u), 1080 + 900*u*u, 1, side*40*u, 1 - u)
            confetti(L, fr, "rcf", t - K["termine"], 120, 3, [ROUGE, NOIR, BLANC, JAUNE])
            fx.shockwave(L, t, K["termine"], CX, 1080, .5, 1000)
    M.draw_all(L, fr, t, E_P[:1] + E_P[2:])
CAM_PENS = [(K["tab"], CX, 960, 1.0), (K["placard"] - .2, 700, 1250, 1.08), (K["benarfa"], 500, 1200, 1.1), (K["nkunku"], CX, 1300, 1.06),
            (K["rate"], CX, 1150, 1.1), (TB, CX, 1080, 1.0), (K["termine"], CX, 1100, 1.08)]

# --- 11. BRETAGNE
CL = [("RENNES", "L1", K["rennesb"], ROUGE), ("BREST", "L1", K["brest"], ROUGE), ("LORIENT", "L1", K["lorient"], (240, 120, 30)), ("GUINGAMP", "L2", K["guinb"], NOIR)]
MX, MY = CX + 10, 1120
E_B = words(lambda w, i: KW(w, JAUNE if i else NOIR, NOIR if i else BLANC, 100), [("3 CLUBS", K["trois"] - .05), ("EN LIGUE 1", K["l1"] - .05)], CX, 600, out=K["alors"] - .2) + \
      words(lambda w, i: KW(w, JAUNE if i else NOIR, NOIR if i else BLANC, 104), [("LE MEILLEUR", K["meilleur"] - .05), ("CLUB BRETON ?", K["breton"] - .05)], CX, 600) + \
      [El(bzh_map(), MX, MY, K["auj"] + .05, None, "rise", idle=.3, dist=1200),
       El(marker("DIS-LE EN COMMENTAIRE", "rcom", 76), CX, 1540, K["dis"] - .05, None, "slide_l", rot=2)]
@scene(K["auj"], trans="tear", td=.3)
def s_bzh(L, fr, t):
    paper_fill(L, (40, 90, 150), "sea2"); d = ImageDraw.Draw(L)
    for k in range(14): d.arc([-200 + k*120 + 30*math.sin(t + k), 1700 + 20*math.sin(t*1.3 + k), k*120 + 100, 1800], 200, 340, fill=(80, 130, 190), width=6)
    M.draw_all(L, fr, t, E_B[-2:-1])
    mv = E_B[-2].state(t); ox, oy = (mv[0] - MX, mv[1] - MY) if mv else (0, 2000)
    for i, (nm, lg, t0, col) in enumerate(CL):
        if t < t0 - .05: continue
        cx_, cy_ = CITIES[nm]; x, y = MX - 500 + cx_ + ox, MY - 370 + cy_ + oy
        a = t - t0 + .05; fall = .22
        py = y - 70 - (600*(1 - (a/fall)**2) if a < fall else 0); q = .25*math.exp(-(a - fall)*14)*math.cos((a - fall)*30) if a >= fall else 0
        d.line([(x, py + 20), (x, py + 70)], fill=(60, 60, 60), width=6)
        d.ellipse([x - 24*(1 + q), py - 22*(1 - q), x + 24*(1 + q), py + 22*(1 - q)], fill=ROUGE, outline=NOIR, width=3)
        hi = t > K["alors"] and int((t - K["alors"])*2.5) % 4 == i
        tag(f"{nm} · {lg}", 44, col, BLANC).draw(L, fr, x + (90 if nm != "RENNES" else -70), y + 60 + (i % 2)*20, M.spring(a - .1, .45, 14)*(1.18 if hi else 1), (-3, 2, -2, 3)[i])
        if nm == "RENNES" and t > t0 + .2: put(L, CREST(150), x + 40, y - 150, M.spring(t - t0 - .2, .45, 14), 6)
    if t > K["dis"]:
        y = 1640 + 16*abs(math.sin(t*6)); d.polygon([(CX - 46, y), (CX + 46, y), (CX, y + 56)], fill=ROUGE)
    M.draw_all(L, fr, t, E_B[:-2] + E_B[-1:])
CAM_BZH = [(K["auj"], CX, 1000, 1.0), (K["rennesb"] - .1, 800, 1060, 1.12), (K["brest"] - .1, 260, 1060, 1.12), (K["guinb"] - .1, 520, 1000, 1.1),
           (K["alors"], CX, 1000, 1.0), (K["dis"], CX, 1100, 1.04)]

SC.sort(key=lambda s: s["t0"])
CAMS = {"s_hook": CAM_HOOK, "s_cat": CAM_CAT, "s_1901": CAM_1901, "s_1929": CAM_1929, "s_pokou": CAM_POKOU, "s_cups": CAM_CUPS,
        "s_quiz": CAM_QUIZ, "s_guingamp": CAM_GUIN, "s_cama": CAM_CAMA, "s_final": CAM_FINAL, "s_pens": CAM_PENS, "s_bzh": CAM_BZH}
IMPACTS = [K["maudit"], K["sixzero"] + .5, K["ans48"], K["sz2"] + .7, K["porte"], K["centaine"], K["pele"], K["y65"], K["y71"], K["abonne"] + .18,
           K["like"], K["guin1"] + .25, K["l2"], K["brule"], K["pro"], K["eduardo"], K["deuxdeux"], K["expulse"], K["marque"], K["rate"], K["termine"]]
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
    p = os.path.join(out, f"r2sheet{'_' + only if only else ''}.jpg"); sheet.save(p, quality=82); return p

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--stills" in args:
        only = args[args.index("--stills") + 1] if len(args) > args.index("--stills") + 1 else None
        print(stills("/tmp/claude-0/aud", only)); sys.exit()
    out = args[0] if args else os.path.join(ROOT, "output", SLUG); os.makedirs(out, exist_ok=True)
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=[VOIX], sfx_dir=SFX_DIR + "_v", sfx_db=6.0, lufs=-14.0, crf=22, limit=True))
