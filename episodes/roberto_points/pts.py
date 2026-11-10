"""Moteur « nuage de points » (DA foot-nuage-de-points) en numpy : ~30 000 points qui se réorganisent d'un plan à l'autre.
Chaque plan = liste de « parts » (poids, générateur(k, lt) -> x, y, couleur, alpha). Le moteur répartit les points, interpole
depuis le plan précédent (morph décalé par point + tourbillon), applique la caméra (coup de zoom + poussée lente), ajoute le
champ d'étoiles, le bloom, le grain, le vignettage, et un léger flou de mouvement (2 sous-images)."""
import math, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 30
N = 30000
CX, CY = 540, 1060
INKBG = np.array([7, 9, 22], np.float32)
COL = {"cream": (243, 236, 220), "gold": (232, 182, 90), "blue": (63, 143, 255), "pink": (255, 70, 190), "green": (70, 170, 110),
       "red": (235, 70, 70), "yellow": (250, 215, 60), "dim": (120, 130, 160), "violet": (150, 90, 255), "teal": (40, 220, 200), "orange": (255, 130, 50)}
CNAMES = list(COL); CARR = np.array([COL[c] for c in CNAMES], np.float32)/255.0
def ci(name): return CNAMES.index(name)
RNG = np.random.default_rng(7); R1, R2, R3, R4 = (RNG.random(N) for _ in range(4))
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "fonts")
def font(name, px):
    p = os.path.join(FONTS, name)
    if not os.path.exists(p): p = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
    return ImageFont.truetype(p, px)
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
# ------------------------------------------------------------------ échantillonnage de formes
_mc = {}
def mask_pts(key, draw_fn, size, k, seed=1):
    """Points dans un masque dessiné (PIL, mode L) : ordre fixe par clé -> les points ne « sautent » pas d'une frame à l'autre."""
    if key not in _mc:
        m = Image.new("L", size, 0); draw_fn(ImageDraw.Draw(m)); a = np.asarray(m)
        ys, xs = np.nonzero(a > 100); r = np.random.default_rng(seed).permutation(len(xs))
        _mc[key] = (xs[r].astype(np.float32), ys[r].astype(np.float32))
        if len(_mc) > 400: _mc.pop(next(iter(_mc)))
    xs, ys = _mc[key]
    if len(xs) == 0: return np.zeros(k, np.float32), np.zeros(k, np.float32)
    idx = (np.arange(k)*len(xs)//max(1, k)) % len(xs)
    j = np.random.default_rng(seed + 3).random((2, k)).astype(np.float32) - .5
    return xs[idx] + j[0], ys[idx] + j[1]
def text_pts(txt, px, k, cx, cy, fnt="Anton-Regular.ttf", seed=2):
    f = font(fnt, px) if not fnt.startswith("/") else ImageFont.truetype(fnt, px)
    bb = f.getbbox(txt); w, h = bb[2] - bb[0] + 20, bb[3] - bb[1] + 20
    xs, ys = mask_pts(("t", txt, px, fnt), lambda d: d.text((10 - bb[0], 10 - bb[1]), txt, font=f, fill=255), (w, h), k, seed)
    return xs - w/2 + cx, ys - h/2 + cy
def seg(p0, p1, k, jit=0.0, seed=0):
    u = (np.arange(k) + .5)/max(1, k); x = p0[0] + (p1[0] - p0[0])*u; y = p0[1] + (p1[1] - p0[1])*u
    if jit: r = np.random.default_rng(seed).normal(0, jit, (2, k)); x, y = x + r[0], y + r[1]
    return x, y
def poly(pts, k, jit=0.0, seed=0, closed=False):
    pts = list(pts) + ([pts[0]] if closed else []); L = [math.dist(a, b) for a, b in zip(pts, pts[1:])]; T = sum(L) or 1
    xs, ys = [], []; ks = [max(1, int(k*l/T)) for l in L]; ks[-1] += k - sum(ks)
    for (a, b), kk in zip(zip(pts, pts[1:]), ks):
        if kk > 0: x, y = seg(a, b, kk, jit, seed); xs.append(x); ys.append(y)
    return np.concatenate(xs)[:k], np.concatenate(ys)[:k]
def ring(cx, cy, rx, ry, k, a0=0, a1=2*math.pi, jit=0.0, seed=0):
    a = a0 + (a1 - a0)*(np.arange(k) + .5)/max(1, k); x, y = cx + rx*np.cos(a), cy + ry*np.sin(a)
    if jit: r = np.random.default_rng(seed).normal(0, jit, (2, k)); x, y = x + r[0], y + r[1]
    return x, y
def disc(cx, cy, r, k, seed=0):
    g = np.random.default_rng(seed); a = g.random(k)*2*math.pi; rr = r*np.sqrt(g.random(k)); return cx + rr*np.cos(a), cy + rr*np.sin(a)
def scatter(k, seed, x0=0, y0=0, x1=W, y1=H):
    g = np.random.default_rng(seed); return x0 + g.random(k)*(x1 - x0), y0 + g.random(k)*(y1 - y0)
# ------------------------------------------------------------------ silhouettes « pictogramme » (jamais de photo de joueur)
POSES = {   # articulations (x, y) dans un repère 0..1 (hauteur), tête en haut
    "stand":  dict(head=(0, .1), neck=(0, .2), hip=(0, .52), la=[(-.14, .33), (-.18, .5)], ra=[(.14, .33), (.18, .5)], ll=[(-.07, .75), (-.08, .98)], rl=[(.07, .75), (.08, .98)]),
    "keeper": dict(head=(0, .12), neck=(0, .22), hip=(0, .54), la=[(-.2, .3), (-.34, .2)], ra=[(.2, .3), (.34, .2)], ll=[(-.12, .76), (-.17, .98)], rl=[(.12, .76), (.17, .98)]),
    "kick":   dict(head=(-.06, .1), neck=(-.04, .2), hip=(0, .52), la=[(-.24, .3), (-.38, .38)], ra=[(.16, .26), (.3, .2)], ll=[(-.06, .76), (-.06, .98)], rl=[(.2, .68), (.38, .62)]),
    "run":    dict(head=(.04, .1), neck=(.03, .2), hip=(0, .52), la=[(-.12, .34), (-.02, .46)], ra=[(.14, .3), (.22, .2)], ll=[(-.14, .74), (-.24, .94)], rl=[(.12, .72), (.08, .96)]),
    "duck":   dict(head=(.0, .52), neck=(0, .58), hip=(0, .8), la=[(-.16, .5), (-.1, .42)], ra=[(.16, .5), (.1, .42)], ll=[(-.16, .9), (-.14, .99)], rl=[(.16, .9), (.14, .99)]),
    "wall":   dict(head=(0, .1), neck=(0, .2), hip=(0, .52), la=[(-.1, .34), (-.04, .5)], ra=[(.1, .34), (.04, .5)], ll=[(-.06, .76), (-.07, .98)], rl=[(.06, .76), (.07, .98)]),
    "arms":   dict(head=(0, .1), neck=(0, .2), hip=(0, .52), la=[(-.2, .16), (-.3, .02)], ra=[(.2, .16), (.3, .02)], ll=[(-.1, .76), (-.14, .98)], rl=[(.1, .76), (.14, .98)]),
}
def lerp_pose(a, b, u):
    A, B = POSES[a], POSES[b]; out = {}
    for k in A:
        if isinstance(A[k], list): out[k] = [(p[0] + (q[0] - p[0])*u, p[1] + (q[1] - p[1])*u) for p, q in zip(A[k], B[k])]
        else: out[k] = (A[k][0] + (B[k][0] - A[k][0])*u, A[k][1] + (B[k][1] - A[k][1])*u)
    return out
def figure(pose, k, cx, foot_y, height, seed=5, flip=False):
    """Silhouette pleine en points (style pictogramme) : tête ronde + membres épais."""
    P = POSES[pose] if isinstance(pose, str) else pose; S = 400
    key = ("fig", str(sorted((kk, str(v)) for kk, v in P.items())))
    def dr(d):
        def pt(p): return (S/2 + p[0]*S, p[1]*S)
        d.ellipse([pt(P["head"])[0] - S*.075, pt(P["head"])[1] - S*.075, pt(P["head"])[0] + S*.075, pt(P["head"])[1] + S*.075], fill=255)
        d.line([pt(P["neck"]), pt(P["hip"])], fill=255, width=int(S*.15))
        for limb, root, wd in (("la", "neck", .07), ("ra", "neck", .07), ("ll", "hip", .09), ("rl", "hip", .09)):
            d.line([pt(P[root])] + [pt(q) for q in P[limb]], fill=255, width=int(S*wd), joint="curve")
            for q in P[limb]: d.ellipse([pt(q)[0] - S*wd/2, pt(q)[1] - S*wd/2, pt(q)[0] + S*wd/2, pt(q)[1] + S*wd/2], fill=255)
    xs, ys = mask_pts(key, dr, (S, S), k, seed); sc = height/S
    if flip: xs = S - xs
    return cx + (xs - S/2)*sc, foot_y - (S - ys)*sc
# ------------------------------------------------------------------ plans
class Shot:
    def __init__(self, t0, parts, cont=False, zoom=True, ring=True, glitch=0.0, sub=True):
        self.t0, self.parts, self.cont, self.zoom, self.ring, self.glitch, self.sub = t0, parts, cont, zoom, ring, glitch, sub
        self.t1 = None
    def target(self, lt):
        ws = np.array([p[0] for p in self.parts], np.float64); ks = np.floor(ws/ws.sum()*N).astype(int); ks[np.argmax(ks)] += N - ks.sum()
        X, Y, C, A = [], [], [], []
        for (w, gen), k in zip(self.parts, ks):
            if k <= 0: continue
            x, y, c, a = gen(int(k), lt)
            X.append(np.asarray(x, np.float32)[:k]); Y.append(np.asarray(y, np.float32)[:k])
            c = np.asarray(c); C.append(c[:k].astype(np.float32) if c.ndim == 2 else CARR[np.broadcast_to(c.astype(np.int32), (k,))]); A.append(np.broadcast_to(np.asarray(a, np.float32), (k,)))
        return np.concatenate(X), np.concatenate(Y), np.concatenate(C), np.concatenate(A)
def ease(u): return u*u*(3 - 2*u)
def state(shots, t):
    i = max(j for j, s in enumerate(shots) if s.t0 <= t + 1e-9) if t >= shots[0].t0 else 0
    s = shots[i]; lt = t - s.t0; dur = (s.t1 - s.t0)
    x, y, c, a = s.target(lt)
    if i > 0 and not s.cont:
        p = shots[i - 1]; px, py, pc, pa = p.target(p.t1 - p.t0)
        d = min(.62, .45*dur); dsp = min(.2, .12*dur)
        u = np.clip((lt - R1*dsp)/d, 0, 1); e = ease(u)
        dx, dy = x - px, y - py; L = np.hypot(dx, dy) + 1e-3
        sw = np.sin(math.pi*e)*(R2 - .5)*.35*np.minimum(L, 900)
        x2 = px + dx*e - dy/L*sw; y2 = py + dy*e + dx/L*sw
        col = pc*(1 - e)[:, None] + c*e[:, None]; al = pa*(1 - e) + a*e
        return x2, y2, col, al, s, lt, dur, i
    return x, y, c, a, s, lt, dur, i
def camera(x, y, s, lt, dur, t):
    if s.cont or not s.zoom: cam = 1.05
    else: cam = (1 + .11*math.exp(-4.2*lt))*(1 + .07*lt/max(.3, dur))
    r = .012*math.sin(.45*t); cs, sn = math.cos(r), math.sin(r)
    xx, yy = (x - CX)*cam, (y - CY)*cam
    return CX + xx*cs - yy*sn, CY + xx*sn + yy*cs
# ------------------------------------------------------------------ rendu
STAR = np.random.default_rng(11); SA = STAR.random(420)*2*math.pi; SZ0 = STAR.random(420); SV = .5 + STAR.random(420)
def warp(t, starts): return .035*t + sum(.05*(1 - math.exp(-3.5*(t - s))) for s in starts if t > s)
def splat(buf, x, y, col, inten):
    ok = (x > 1) & (x < W - 2) & (y > 1) & (y < H - 2) & (inten > .002)
    x, y, col, inten = x[ok], y[ok], col[ok], inten[ok]
    ix, iy = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64); fx, fy = x - ix, y - iy
    for ox, oy, w in ((0, 0, (1 - fx)*(1 - fy)), (1, 0, fx*(1 - fy)), (0, 1, (1 - fx)*fy), (1, 1, fx*fy)):
        idx = (iy + oy)*W + (ix + ox); ww = w*inten
        for ch in range(3): buf[ch] += np.bincount(idx, ww*col[:, ch], minlength=W*H)
_grain = np.random.default_rng(3).normal(0, 1, (4, H//2, W//2)).astype(np.float32)
_vig = None
def render(shots, t, beat=0.0):
    global _vig
    starts = [s.t0 for s in shots]; buf = np.zeros((3, W*H), np.float32)
    for sub in (-.16/FPS, .16/FPS):
        tt = max(0.0, t + sub); x, y, col, al, s, lt, dur, i = state(shots, tt); x, y = camera(x, y, s, lt, dur, tt)
        z = 1 + .02*beat; x, y = CX + (x - CX)*z, CY + (y - CY)*z
        splat(buf, x, y, col, al*.62*(.55 + .9*R3)*(1 + .2*beat))
        wv = warp(tt, starts); zz = (SZ0 - wv*SV) % 1.0 + .03; rr = 60/zz            # étoiles qui foncent vers nous
        sx, sy = CX + np.cos(SA)*rr, CY + np.sin(SA)*rr*1.1; si = np.clip((1 - zz)**2, 0, 1)*.5
        splat(buf, sx, sy, CARR[np.array([0, 0, 1, 2, 0] * 84)], si)
    img = buf.reshape(3, H, W).transpose(1, 2, 0)
    img = cv2.GaussianBlur(img, (0, 0), .6)*2.2
    small = cv2.resize(img, (W//4, H//4), interpolation=cv2.INTER_AREA); small = cv2.GaussianBlur(small, (0, 0), 5)
    img = img + cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)*(.34 + .34*beat)*3
    img = 1 - np.exp(-img*1.6)
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W]; d = ((xx - W/2)/(W*.7))**2 + ((yy - H/2)/(H*.62))**2; _vig = np.clip(1 - .55*d, .25, 1).astype(np.float32)[..., None]
        def lf(seed, sc):
            g = np.random.default_rng(seed).random((H//sc + 2, W//sc + 2)).astype(np.float32); return cv2.GaussianBlur(cv2.resize(g, (W, H), interpolation=cv2.INTER_CUBIC), (0, 0), 140)
        n1, n2, n3 = lf(1, 420), lf(2, 520), lf(3, 360); gy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
        neb = np.array([.03, .06, .16])*np.clip(n1*2.0 - .5, 0, 1)[..., None] + np.array([.02, .04, .10])*np.clip(n2*2.2 - .9, 0, 1)[..., None]
        _vig = (_vig, (INKBG/255.0)*(1.1 - .4*gy[..., None]) + neb.astype(np.float32))
    vg, bgc = _vig
    out = (bgc + img*(1 - bgc))*vg
    g = cv2.resize(_grain[int(t*FPS) % 4], (W, H), interpolation=cv2.INTER_NEAREST)[..., None]*.035
    out = np.clip(out + g*.6, 0, 1)
    return (out*255).astype(np.uint8), state(shots, t)
def glitch(arr, amt, seed):
    if amt <= 0: return arr
    o = int(6 + 18*amt); r = np.random.default_rng(seed); a = arr.copy()
    a[..., 0] = np.roll(arr[..., 0], o, axis=1); a[..., 2] = np.roll(arr[..., 2], -o, axis=1)
    for _ in range(int(3*amt) + 1):
        y0 = r.integers(0, H - 80); h = r.integers(10, 60); a[y0:y0 + h] = np.roll(a[y0:y0 + h], r.integers(-40, 40), axis=1)
    return a
_ic = {}
def img_pts(path, k, cx, cy, h, gamma=2.0, seed=4):
    """Statue -> points pondérés par la luminance (autocontraste, gamma, recadrage sur le sujet, bas estompé)."""
    key = (path, k)
    if key not in _ic:
        a = np.asarray(Image.open(path).convert("L"), np.float32)/255.0
        ys, xs = np.nonzero(a > .12); a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        lo, hi = np.percentile(a, 2), np.percentile(a, 99.5); a = np.clip((a - lo)/(hi - lo + 1e-6), 0, 1)**gamma
        fade = np.clip((a.shape[0] - np.arange(a.shape[0]))/(a.shape[0]*.08), 0, 1)[:, None]; a = a*fade
        p = a.ravel()/a.sum(); g = np.random.default_rng(seed); idx = g.choice(len(p), k, p=p)
        yy, xx = np.divmod(idx, a.shape[1]); j = g.random((2, k)) - .5
        rgb = np.asarray(Image.open(path).convert("RGB"), np.float32)/255.0; rgb = rgb[ys.min():ys.max() + 1, xs.min():xs.max() + 1].reshape(-1, 3)[idx]
        mx = rgb.max(1, keepdims=True); rgb = np.clip(rgb/np.maximum(mx, .35)*1.0, 0, 1)
        _ic[key] = ((xx + j[0])/a.shape[0], (yy + j[1])/a.shape[0], a.ravel()[idx], a.shape[1]/a.shape[0], rgb)
    nx, ny, lum, asp, rgb = _ic[key]
    return cx + (nx - asp/2)*h, cy + (ny - .5)*h, lum, rgb
