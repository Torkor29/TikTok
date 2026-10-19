"""Moteur « papercraft » low-poly : vrais volumes 3D à facettes en papier, rendus en sprites PIL.
Chaque pièce = enveloppe convexe d'un nuage de points (facettes pliées), peinte de façon procédurale
(rayures, taches, mouchetis) dans SES coordonnées locales -> la peinture reste collée quand la pièce bouge.
Éclairage Lambert par facette + léger écart de teinte par facette + grain papier + ombre de contact."""
import math
import numpy as np
from PIL import Image, ImageFilter
from scipy.spatial import ConvexHull

def rot(ax, a):
    c, s = math.cos(a), math.sin(a)
    if ax == "x": return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if ax == "y": return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

# ------------------------------------------------------------------ primitives (nuages de points)
def cbox(sx, sy, sz, ch=.18, top=1.0):
    """Boîte chanfreinée (ch = fraction coupée aux arêtes), top = rétrécissement du haut (tronc de pyramide)."""
    P = []
    for X in (-1, 1):
        for Y in (-1, 1):
            for Z in (-1, 1):
                k = top if Y > 0 else 1
                for a in range(3):
                    v = [X*sx/2*k, Y*sy/2, Z*sz/2*k]
                    v[a] *= 1 - ch
                    P.append(v)
    return np.array(P, float)
def pyramid(base, h, tip=(0, 0)):
    """Pyramide sur polygone de base (liste (x, z)) à y=0, sommet en (tip, h)."""
    return np.array([[x, 0, z] for x, z in base] + [[tip[0], h, tip[1]]], float)
def prism(poly, depth):
    return np.array([[x, y, z] for x, y in poly for z in (-depth/2, depth/2)], float)

class Part:
    def __init__(self, pts, color, paint=None, pos=(0, 0, 0), R=None, pivot=(0, 0, 0), name=""):
        self.pts = np.asarray(pts, float); self.color = np.array(color, float)/255; self.paint = paint
        self.pos = np.array(pos, float); self.R = np.eye(3) if R is None else R; self.pivot = np.array(pivot, float); self.name = name
        h = ConvexHull(self.pts); self.tris = h.simplices; self.nrm = h.equations[:, :3]
        rng = np.random.default_rng(abs(hash(name)) % 2**32 if name else len(self.pts))
        self.jit = 1 + rng.normal(0, .035, len(self.tris))           # chaque facette = un pli de papier légèrement différent
    def world(self, Rextra=None):
        R = self.R if Rextra is None else self.R @ Rextra
        return (self.pts - self.pivot) @ R.T + self.pivot + self.pos, self.nrm @ R.T

def _noise(shape, seed, blur):
    g = np.random.default_rng(seed).random(shape).astype(np.float32)
    im = Image.fromarray((g*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im, np.float32)/255

def render(parts, size=600, yaw=-.6, pitch=.28, scale=180, center=(0, 1, 0), light=(-.55, .75, .55), ss=2, anim=None,
           shadow=True, ground=0.0, seed=3, anchor=(0, 0, 0), shadow_a=120):
    """anim = {nom_de_pièce: matrice de rotation (autour du pivot)}. Renvoie un sprite RGBA (size x size)."""
    S = size*ss; anim = anim or {}
    Cam = rot("x", pitch) @ rot("y", yaw)
    L = np.array(light, float); L /= np.linalg.norm(L)
    zb = np.full((S, S), -1e9, np.float32); col = np.zeros((S, S, 3), np.float32)
    pid = np.full((S, S), -1, np.int32); loc = np.zeros((S, S, 3), np.float32); shade = np.zeros((S, S), np.float32)
    c0 = np.array(center, float)
    for k, p in enumerate(parts):
        W, N = p.world(anim.get(p.name))
        V = (W - c0) @ Cam.T; NV = N @ Cam.T
        sx = S/2 + V[:, 0]*scale*ss; sy = S/2 - V[:, 1]*scale*ss; sz = V[:, 2]
        lam = np.clip(N @ L, 0, 1)                                   # éclairage en espace monde
        for t, (a, b, c) in enumerate(p.tris):
            if NV[t, 2] <= 1e-4: continue
            xs, ys = sx[[a, b, c]], sy[[a, b, c]]
            x0, x1 = int(max(0, xs.min())), int(min(S - 1, xs.max() + 1)); y0, y1 = int(max(0, ys.min())), int(min(S - 1, ys.max() + 1))
            if x1 < x0 or y1 < y0: continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + .5, np.arange(y0, y1 + 1) + .5)
            d = (ys[1] - ys[2])*(xs[0] - xs[2]) + (xs[2] - xs[1])*(ys[0] - ys[2])
            if abs(d) < 1e-9: continue
            w0 = ((ys[1] - ys[2])*(gx - xs[2]) + (xs[2] - xs[1])*(gy - ys[2]))/d
            w1 = ((ys[2] - ys[0])*(gx - xs[2]) + (xs[0] - xs[2])*(gy - ys[2]))/d
            w2 = 1 - w0 - w1
            m = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4)
            if not m.any(): continue
            z = w0*sz[a] + w1*sz[b] + w2*sz[c]
            sub = zb[y0:y1 + 1, x0:x1 + 1]; m &= z > sub
            if not m.any(): continue
            sub[m] = z[m]
            pid[y0:y1 + 1, x0:x1 + 1][m] = k
            P3 = p.pts
            lp = loc[y0:y1 + 1, x0:x1 + 1]
            for i in range(3): lp[..., i][m] = (w0*P3[a, i] + w1*P3[b, i] + w2*P3[c, i])[m]
            shade[y0:y1 + 1, x0:x1 + 1][m] = (.42 + .72*lam[t])*p.jit[t]
    for k, p in enumerate(parts):                                    # peinture procédurale en coordonnées locales
        m = pid == k
        if not m.any(): continue
        rgb = np.tile(p.color, (m.sum(), 1))
        if p.paint: rgb = p.paint(loc[m], rgb)
        col[m] = rgb
    grain = .93 + .1*_noise((S, S), seed, 1.2)
    out = np.clip(col*shade[..., None]*grain[..., None], 0, 1)
    a = (pid >= 0).astype(np.float32)
    img = np.dstack([out*255, a*255]).astype(np.uint8)
    im = Image.fromarray(img, "RGBA")
    if shadow:                                                       # ombre de contact douce sous le volume
        gy = S/2 - ((np.array([0, ground, 0]) - c0) @ Cam.T)[1]*scale*ss
        sh = Image.new("L", (S, S), 0)
        ys_, xs_ = np.nonzero(pid >= 0)
        if len(xs_):
            from PIL import ImageDraw
            w = (xs_.max() - xs_.min())*.55
            ImageDraw.Draw(sh).ellipse([xs_.mean() - w, gy - w*.16, xs_.mean() + w, gy + w*.16], fill=shadow_a)
            sh = sh.filter(ImageFilter.GaussianBlur(14*ss))
            base = Image.new("RGBA", (S, S), (25, 18, 14, 0)); base.putalpha(sh)
            base.alpha_composite(im); im = base
    im = im.resize((size, size), Image.LANCZOS)
    av = (np.array(anchor, float) - c0) @ Cam.T
    im.info["anchor"] = (size/2 + av[0]*scale, size/2 - av[1]*scale)
    return im

def project(pt, yaw=-.6, pitch=.28, scale=180, center=(0, 1, 0), size=600):
    v = (np.array(pt, float) - np.array(center, float)) @ (rot("x", pitch) @ rot("y", yaw)).T
    return size/2 + v[0]*scale, size/2 - v[1]*scale

def lathe(profile, n=8, phase=0.0):
    """Solide de révolution à n pans : profile = [(rayon, y)] (enveloppe convexe -> profil convexe)."""
    return np.array([[r*math.cos(2*math.pi*k/n + phase), y, r*math.sin(2*math.pi*k/n + phase)] for r, y in profile for k in range(n)], float)

def icosphere(r=1.0, sub=1):
    t = (1 + 5**.5)/2
    V = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    V = [np.array(v)/np.linalg.norm(v) for v in V]
    pts = list(V)
    if sub:
        for i in range(12):
            for j in range(i + 1, 12):
                if np.dot(V[i], V[j]) > .4: m = V[i] + V[j]; pts.append(m/np.linalg.norm(m))
    return np.array(pts)*r, np.array(V)

# ------------------------------------------------------------------ outils de peinture
def capsule(u, v, a, b, r):
    """Trait de pinceau à bouts ronds dans le plan (u, v) : segment a-b, rayon r (léger tremblé)."""
    a, b = np.array(a, float), np.array(b, float); d = b - a; L2 = max(d @ d, 1e-9)
    k = np.clip(((u - a[0])*d[0] + (v - a[1])*d[1])/L2, 0, 1)
    du, dv = u - a[0] - k*d[0], v - a[1] - k*d[1]
    rr = r*(1 + .08*np.sin(k*17 + a[0]*9))*(1 - .25*np.abs(2*k - 1)**3)
    return du*du + dv*dv < rr*rr
def speckle(P, rgb, dens=.025, dark=(40, 34, 30), seed=1):
    h = np.sin(np.floor(P[:, 0]*140)*12.9898 + np.floor(P[:, 1]*140)*78.233 + np.floor(P[:, 2]*140)*37.719 + seed)*43758.5453
    m = (h - np.floor(h)) < dens
    rgb[m] = np.array(dark)/255; return rgb
