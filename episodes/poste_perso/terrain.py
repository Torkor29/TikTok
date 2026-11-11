"""DA « Le Terrain » : un seul terrain de foot 3D en points aux vraies couleurs, une caméra qui s'y déplace sans coupe,
joueurs en silhouettes de points, textes PEINTS sur la pelouse. Moteur numpy (projection perspective + splat + bloom)."""
import os, sys, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "episodes", "roberto_points"))
import pts as P
W, H, FPS = 1080, 1920, 30
FOCAL = 1150.0
def rgb(*c): return np.array(c, np.float32)/255.0
# ------------------------------------------------------------------ monde statique
def _world():
    g = np.random.default_rng(1); parts = []
    n = 140000; X = g.uniform(-40, 40, n); Z = g.uniform(-60, 60, n)                      # gazon (bandes tondues, vraies couleurs)
    inside = (np.abs(X) < 34) & (np.abs(Z) < 52.5); stripe = (np.floor((Z + 52.5)/7) % 2 == 0)
    base = np.where(stripe[:, None], rgb(80, 185, 70), rgb(55, 150, 55)); base = np.where(inside[:, None], base, rgb(30, 80, 38))
    base = base*(0.85 + 0.3*g.random(n))[:, None]; parts.append((X, 0*X, Z, base, np.full(n, 1.6)))
    L = []                                                                                 # lignes
    def seg(a, b, k): u = np.linspace(0, 1, k); L.append((a[0] + (b[0] - a[0])*u, a[1] + (b[1] - a[1])*u))
    for z in (-52.5, 52.5): seg((-34, z), (34, z), 700)
    for x in (-34, 34): seg((x, -52.5), (x, 52.5), 1000)
    seg((-34, 0), (34, 0), 700)
    for s in (-1, 1):
        seg((-20.16, s*52.5), (-20.16, s*36), 170); seg((20.16, s*52.5), (20.16, s*36), 170); seg((-20.16, s*36), (20.16, s*36), 420)
        seg((-9.16, s*52.5), (-9.16, s*47), 60); seg((9.16, s*52.5), (9.16, s*47), 60); seg((-9.16, s*47), (9.16, s*47), 190)
    a = np.linspace(0, 2*math.pi, 600); L.append((9.15*np.cos(a), 9.15*np.sin(a)))
    lx = np.concatenate([l[0] for l in L]); lz = np.concatenate([l[1] for l in L]); jit = g.normal(0, .04, (2, len(lx)))
    parts.append((lx + jit[0], np.full(len(lx), .02), lz + jit[1], np.tile(rgb(245, 245, 240), (len(lx), 1)), np.full(len(lx), 1.0)))
    for s in (-1, 1):                                                                      # buts + filets
        k = 900; u = g.random(k)
        px = np.r_[np.full(k//3, -3.66), np.full(k//3, 3.66), -3.66 + 7.32*u[:k - 2*(k//3)]]; py = np.r_[2.44*u[:k//3], 2.44*u[k//3:2*(k//3)], np.full(k - 2*(k//3), 2.44)]
        parts.append((px, py, np.full(k, s*52.5), np.tile(rgb(255, 255, 255), (k, 1)), np.full(k, 1.0)))
        k = 2500; nx = np.round(g.uniform(-3.66, 3.66, k)*3)/3; ny = g.uniform(0, 2.44, k); nz = s*(52.5 + 2 - ny*.35)
        parts.append((nx, ny, nz, np.tile(rgb(200, 205, 215), (k, 1)), np.full(k, .35)))
    k = 26000; t = g.random(k)*2*math.pi; row = g.integers(0, 22, k)                      # tribunes + foule colorée
    rx, rz = 52 + row*1.6, 72 + row*1.6; X = rx*np.cos(t); Z = rz*np.sin(t); Y = 1.5 + row*1.1
    crowd = np.array([rgb(230, 230, 235), rgb(40, 90, 200), rgb(220, 50, 50), rgb(240, 200, 60), rgb(30, 30, 40)])[g.integers(0, 5, k)]
    parts.append((X, Y, Z, crowd*(.5 + .5*g.random(k))[:, None], np.full(k, 1.2)))
    for (fx, fz) in ((-50, -70), (50, -70), (-50, 70), (50, 70)):                          # projecteurs
        k = 700; r = 2.2*np.sqrt(g.random(k)); a = g.random(k)*2*math.pi
        parts.append((fx + r*np.cos(a), 38 + r*np.sin(a), np.full(k, fz), np.tile(rgb(255, 250, 225), (k, 1)), np.full(k, 1.6)))
    X = np.concatenate([p[0] for p in parts]); Y = np.concatenate([p[1] for p in parts]); Z = np.concatenate([p[2] for p in parts])
    C = np.concatenate([p[3] for p in parts]); A = np.concatenate([p[4] for p in parts])
    return X.astype(np.float32), Y.astype(np.float32), Z.astype(np.float32), C.astype(np.float32), A.astype(np.float32)
WORLD = _world()
# ------------------------------------------------------------------ caméra
class Cam:
    def __init__(self, pos, tgt): self.pos, self.tgt = np.array(pos, np.float32), np.array(tgt, np.float32)
    def basis(self):
        f = self.tgt - self.pos; f /= np.linalg.norm(f); r = np.cross(f, np.array([0, 1, 0], np.float32)); r /= np.linalg.norm(r); u = np.cross(r, f); return f, r, u
    def project(self, X, Y, Z):
        f, r, u = self.basis(); dx, dy, dz = X - self.pos[0], Y - self.pos[1], Z - self.pos[2]
        x = dx*r[0] + dy*r[1] + dz*r[2]; y = dx*u[0] + dy*u[1] + dz*u[2]; z = dx*f[0] + dy*f[1] + dz*f[2]
        zz = np.maximum(z, .3); return W/2 + FOCAL*x/zz, H*.5 - FOCAL*y/zz, z
def lerp_cam(a, b, u):
    u = u*u*(3 - 2*u); return Cam(a.pos + (b.pos - a.pos)*u, a.tgt + (b.tgt - a.tgt)*u)
# ------------------------------------------------------------------ objets dynamiques
def figure3d(pose, x, z, h=1.85, k=2600, seed=5, cam=None):
    """Silhouette en points, toujours tournée vers la caméra (panneau orienté)."""
    fx, fy = P.figure(pose, k, 0, 0, 1.0, seed=seed); rx, rz = 1.0, 0.0
    if cam is not None:
        f, r, u = cam.basis(); n = math.hypot(r[0], r[2]) or 1; rx, rz = r[0]/n, r[2]/n
    return (x + fx*h*rx).astype(np.float32), (-fy*h).astype(np.float32), (z + fx*h*rz).astype(np.float32)
_tm = {}
def ground_text(txt, cam, anchor, width_m, k=9000, seed=3):
    """Texte peint sur la pelouse, orienté pour être lisible depuis la caméra."""
    key = txt
    if key not in _tm:
        f = ImageFont.truetype(os.path.join(ROOT, "assets", "fonts", "Anton-Regular.ttf"), 200); bb = f.getbbox(txt); w, h = bb[2] - bb[0] + 20, bb[3] - bb[1] + 20
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).text((10 - bb[0], 10 - bb[1]), txt, font=f, fill=255); a = np.asarray(m)
        ys, xs = np.nonzero(a > 120); r = np.random.default_rng(seed).permutation(len(xs)); _tm[key] = (xs[r]/w - .5, ys[r]/h - .5, h/w)
    nx, ny, asp = _tm[key]; idx = np.arange(k) % len(nx); nx, ny = nx[idx], ny[idx]
    f, r, u = cam.basis(); rg = np.array([r[0], 0, r[2]]); rg /= np.linalg.norm(rg); fg = np.array([f[0], 0, f[2]]); fg /= np.linalg.norm(fg)
    X = anchor[0] + rg[0]*nx*width_m - fg[0]*ny*width_m*asp*2.2; Z = anchor[2] + rg[2]*nx*width_m - fg[2]*ny*width_m*asp*2.2
    return X.astype(np.float32), np.full(k, .03, np.float32), Z.astype(np.float32)
# ------------------------------------------------------------------ rendu
_bg = None
def dense_grass(cam, size=26.0, step=.085, ahead=-6.0, alpha=.55):
    """Gazon dense autour du point visé (réseau fixe dans le monde : les brins ne « nagent » pas)."""
    f, r, u = cam.basis(); cx, cz = (float(cam.tgt[0]) + f[0]*ahead, float(cam.tgt[2]) + f[2]*ahead) if ahead > -50 else (float(cam.pos[0]) + f[0]*22, float(cam.pos[2]) + f[2]*22)
    i0, i1 = int((cx - size)/step), int((cx + size)/step); j0, j1 = int((cz - size)/step), int((cz + size)/step)
    I, J = np.meshgrid(np.arange(i0, i1), np.arange(j0, j1)); I, J = I.ravel(), J.ravel()
    h = (I*73856093 ^ J*19349663) & 0xffffff; jx = (h & 255)/255.0; jz = ((h >> 8) & 255)/255.0; sh = ((h >> 16) & 255)/255.0
    X = (I + jx)*step; Z = (J + jz)*step; ok = (np.abs(X) < 34) & (np.abs(Z) < 52.5); X, Z, sh = X[ok], Z[ok], sh[ok]
    stripe = (np.floor((Z + 52.5)/7) % 2 == 0); col = np.where(stripe[:, None], rgb(80, 185, 70), rgb(55, 150, 55))*(.85 + .35*sh)[:, None]
    fade = np.clip((size - np.maximum(np.abs(X - cx), np.abs(Z - cz)))/(size*.35), 0, 1)
    d = np.hypot(np.hypot(X - cam.pos[0], Z - cam.pos[2]), cam.pos[1]); sp = step*1150/np.maximum(d, 1)           # écart à l'écran entre deux brins
    boost = np.clip((sp/1.3)**2, 1, 9)
    return X.astype(np.float32), (sh*.04).astype(np.float32), Z.astype(np.float32), col.astype(np.float32), (alpha*fade*boost).astype(np.float32)
def render(cam, extra, t, flash=0.0, dense=True):
    """extra : liste de (X, Y, Z, couleur Nx3 ou 3, alpha)."""
    global _bg
    X, Y, Z, C, A = WORLD
    xs, ys, zs, cs, als = [X], [Y], [Z], [C], [A]
    if dense: extra = [dense_grass(cam, size=30.0 if cam.pos[1] < 8 else 45.0, step=.07 if cam.pos[1] < 8 else .11, ahead=-99)] + list(extra)
    for (ex, ey, ez, ec, ea) in extra:
        n = len(ex); xs.append(ex); ys.append(ey); zs.append(ez); cs.append(np.broadcast_to(np.asarray(ec, np.float32), (n, 3))); als.append(np.broadcast_to(np.asarray(ea, np.float32), (n,)))
    X, Y, Z, C, A = (np.concatenate(v) for v in (xs, ys, zs, cs, als))
    sx, sy, z = cam.project(X, Y, Z); ok = z > .4
    inten = A*np.clip(22.0/np.maximum(z, 1), .55, 5.0)
    buf = np.zeros((3, W*H), np.float32); P.splat(buf, sx[ok], sy[ok], C[ok], inten[ok]*.5)
    img = buf.reshape(3, H, W).transpose(1, 2, 0)
    img = cv2.GaussianBlur(img, (0, 0), .8)*2.0
    sm = cv2.GaussianBlur(cv2.resize(img, (W//4, H//4), interpolation=cv2.INTER_AREA), (0, 0), 6)
    img = img + cv2.resize(sm, (W, H))*(.9 + 1.5*flash)
    img = 1 - np.exp(-img*1.9)
    if _bg is None:
        gy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]; _bg = (rgb(30, 60, 140)*(1 - gy)*.8 + rgb(250, 140, 70)*np.exp(-((gy - .3)/.08)**2)*.45).astype(np.float32)
        yy, xx = np.mgrid[0:H, 0:W]; d = ((xx - W/2)/(W*.75))**2 + ((yy - H/2)/(H*.65))**2; _bg = (_bg, np.clip(1 - .25*d, .6, 1).astype(np.float32)[..., None])
    bg, vg = _bg; cov = np.clip(img.max(2, keepdims=True)*2.2, 0, 1); out = (bg*(1 - cov) + img*1.15)*vg
    return (np.clip(out, 0, 1)*255).astype(np.uint8)
