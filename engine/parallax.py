"""
parallax.py — animer des images fixes en 2,5D (effet « parallaxe ») et monter des clips vidéo dans le moteur PIL.

Pour chaque image : un personnage détouré (PNG avec transparence, ex. BiRefNet) et l'image d'origine.
- `prep_layers()` fabrique deux couches en 1080×1920 : le fond, où le personnage est effacé puis rebouché (remplissage
  « push-pull » : on devine la couleur à partir des alentours) et légèrement flouté, et le personnage seul, net.
- `still()` renvoie une fonction de dessin : la caméra avance (zoom) et glisse, le fond bouge moins vite que le personnage
  (profondeur), le personnage « respire » et peut avoir son propre mouvement (s'éloigner, être soulevé…).
- `prep_clip()` / `clip()` : clip vidéo (ex. Veo) découpé en images JPEG 1080×1920 puis lu image par image.
- Ambiance : `light_leak()` (halo de lumière qui dérive), `motes()` (poussière dans la lumière), `grade()` (couleurs),
  `post_fx()` (vignettage + grain photo, à brancher sur Scene.post).
Les couches sont mises en cache sur disque (CACHE) : les processus de rendu les relisent à la demande.
"""
import os, math, random, subprocess
import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter
from engine import W, H, FPS, CX, clamp, lerp

CACHE = os.environ.get("PARALLAX_CACHE", "/tmp/parallax_cache")

# ------------------------------------------------------------------ préparation des couches
def _pushpull(rgb, known):
    """Remplit les zones inconnues (known=0) en propageant les couleurs voisines (pyramide « push-pull »)."""
    levels = []
    c, a = rgb*known[..., None], known.copy()
    while min(a.shape) > 2:
        levels.append((c, a))
        h, w = a.shape; h2, w2 = (h + 1)//2, (w + 1)//2
        cp = np.zeros((h2*2, w2*2, 3), np.float32); ap = np.zeros((h2*2, w2*2), np.float32)
        cp[:h, :w] = c; ap[:h, :w] = a
        c = cp.reshape(h2, 2, w2, 2, 3).sum((1, 3)); a = ap.reshape(h2, 2, w2, 2).sum((1, 3))
        n = np.maximum(a, 1e-6); c = c/n[..., None]*np.minimum(a, 1)[..., None]; a = np.minimum(a, 1)
    out = c/np.maximum(a, 1e-6)[..., None]
    for c, a in reversed(levels):
        h, w = a.shape
        up = np.stack([np.asarray(Image.fromarray(out[..., k]).resize((w, h), Image.BILINEAR)) for k in range(3)], -1)
        col = c/np.maximum(a, 1e-6)[..., None]
        out = col*a[..., None] + up*(1 - a[..., None])
    return out

def prep_layers(key, img_path, cut_path, blur=2.2, sharpen=True, force=False):
    """Écrit CACHE/key_bg.jpg (fond rebouché, flouté) et CACHE/key_fg.png (personnage) en W×H."""
    os.makedirs(CACHE, exist_ok=True)
    bgp, fgp = f"{CACHE}/{key}_bg.jpg", f"{CACHE}/{key}_fg.png"
    if not force and os.path.exists(bgp) and os.path.exists(fgp): return
    im = Image.open(img_path).convert("RGB")
    al = Image.open(cut_path).convert("RGBA").getchannel("A").resize(im.size, Image.BILINEAR)
    hole = al.point(lambda v: 255 if v > 24 else 0).filter(ImageFilter.MaxFilter(9))
    known = 1 - np.asarray(hole, np.float32)/255
    fill = _pushpull(np.asarray(im, np.float32), known)
    bg = Image.fromarray(np.clip(fill, 0, 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    bg.filter(ImageFilter.GaussianBlur(blur)).save(bgp, quality=95)
    up = im.resize((W, H), Image.LANCZOS)
    if sharpen: up = up.filter(ImageFilter.UnsharpMask(1.8, 60, 2))
    a = al.resize((W, H), Image.LANCZOS).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.8))
    fg = up.convert("RGBA"); fg.putalpha(a); fg.save(fgp)

def prep_plain(key, img_path, sharpen=True, force=False):
    """Image sans détourage : une seule couche (fond)."""
    os.makedirs(CACHE, exist_ok=True); p = f"{CACHE}/{key}_bg.jpg"
    if not force and os.path.exists(p): return
    up = Image.open(img_path).convert("RGB").resize((W, H), Image.LANCZOS)
    if sharpen: up = up.filter(ImageFilter.UnsharpMask(1.8, 60, 2))
    up.save(p, quality=95)

def prep_clip(key, mp4, force=False):
    """Découpe un clip en images JPEG W×H (mise à l'échelle Lanczos + léger renfort de netteté)."""
    d = f"{CACHE}/clip_{key}"
    if not force and os.path.isdir(d) and os.listdir(d): return
    os.makedirs(d, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf",
                    f"scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6", "-q:v", "2", f"{d}/%03d.jpg"], check=True)

# ------------------------------------------------------------------ lecture (cache mémoire par processus)
_mem = {}
def _get(path, mode):
    if path not in _mem:
        if len(_mem) > 24: _mem.pop(next(iter(_mem)))
        _mem[path] = Image.open(path).convert(mode)
    return _mem[path]
def layers(key):
    bg = _get(f"{CACHE}/{key}_bg.jpg", "RGB")
    fp = f"{CACHE}/{key}_fg.png"
    return bg, (_get(fp, "RGBA") if os.path.exists(fp) else None)
def clip_frame(key, t, speed=1.0, t_start=0.0):
    d = f"{CACHE}/clip_{key}"; n = len(os.listdir(d))
    k = int(clamp(int((t_start + t*speed)*FPS), 0, n - 1))
    return _get(f"{d}/{k + 1:03d}.jpg", "RGB")

# ------------------------------------------------------------------ caméra
def _xf(z, ox, oy, c, ds=1.0, cs=None, dx=0.0, dy=0.0):
    """Coefficients PIL AFFINE (sortie -> source) : caméra (zoom z autour de c, décalage o) appliquée après un
    mouvement propre du calque (échelle ds autour de cs, décalage d)."""
    cx, cy = c; sx, sy = cs or c
    a = 1/(z*ds)
    return (a, 0, ((-cx - ox)/z + cx - sx - dx)/ds + sx, 0, a, ((-cy - oy)/z + cy - sy - dy)/ds + sy)

def _cover(z, ox, oy, c):
    """Zoom minimal pour que le calque couvre tout l'écran malgré le décalage."""
    cx, cy = c
    return max(z, (cx + ox)/cx, (W - cx - ox)/(W - cx), (cy + oy)/cy, (H - cy - oy)/(H - cy))

def still(key, t0, t1, c=(CX, 900), z=(1.04, 1.12), pan=((0, 0), (0, 0)), par=.4, breath=.006, move=None, fx=None, post=None):
    """Plan fixe animé en 2,5D entre t0 et t1 (temps de la scène).
    z : zoom du personnage au début / à la fin ; le fond zoome `par` fois moins (profondeur).
    pan : décalage caméra (px) début -> fin ; le fond se décale `par` fois moins.
    move(tl, u) -> (dx, dy, ds, cs) : mouvement propre du personnage (tl = temps local, u = avancement 0..1).
    fx(cv, fr, tl, u) : effets sous le personnage (sur le fond) ; post(cv, fr, tl, u) : effets par-dessus."""
    def fn(cv, fr, t):
        tl = t - t0; u = tl/max(.1, t1 - t0)
        e = clamp(u, -.2, 1.2)
        zf = lerp(z[0], z[1], e); ox, oy = lerp(pan[0][0], pan[1][0], e), lerp(pan[0][1], pan[1][1], e)
        bg, fg = layers(key)
        zb = _cover(1 + (zf - 1)*par + .025, ox*par, oy*par, c)
        cv.paste(bg.transform((W, H), Image.AFFINE, _xf(zb, ox*par, oy*par, c), Image.BICUBIC), (0, 0))
        if fx: fx(cv, fr, tl, u)
        if fg is not None:
            dx, dy, ds, cs = move(tl, u) if move else (0, 0, 1.0, None)
            ds *= 1 + breath*math.sin(tl*2*math.pi/3.4)
            if cs is None: cs = (c[0], H)       # respiration : depuis le bas du cadre (le buste reste coupé net)
            L = fg.transform((W, H), Image.AFFINE, _xf(_cover(zf, ox, oy, c), ox, oy, c, ds, cs, dx, dy), Image.BICUBIC)
            cv.paste(L, (0, 0), L)
        if post: post(cv, fr, tl, u)
    return fn

def clip(key, t0, t1, speed=1.0, t_start=0.0, z=(1.0, 1.04), c=(CX, H//2), post=None):
    """Plan vidéo : image du clip à l'instant (t - t0)*speed + t_start, avec une légère poussée de caméra."""
    def fn(cv, fr, t):
        tl = t - t0; u = clamp(tl/max(.1, t1 - t0), -.2, 1.2)
        im = clip_frame(key, max(0, tl), speed, t_start); zz = lerp(z[0], z[1], u)
        if zz > 1.001: im = im.transform((W, H), Image.AFFINE, _xf(zz, 0, 0, c), Image.BICUBIC)
        cv.paste(im, (0, 0))
        if post: post(cv, fr, tl, u)
    return fn

def cuts(cv, fr, t, plan, trans):
    """Enchaîne des plans : plan = [(t_debut, fn)], trans = [(nom, durée)] pour chaque raccord (len(plan) - 1).
    nom : clé de engine.TRANSITIONS, ou "fade" (fondu), "flash" (fondu au blanc), "cut" (coupe sèche)."""
    import engine
    k = 0
    for i, (b, _) in enumerate(plan):
        if t >= b: k = i
    for i in range(1, len(plan)):
        b = plan[i][0]; name, d = trans[i - 1]
        if name != "cut" and b - d/2 <= t < b + d/2:
            prev = cv.copy(); plan[i - 1][1](prev, fr, t); plan[i][1](cv, fr, t)
            u = (t - (b - d/2))/d
            if name == "fade": cv.paste(Image.blend(prev, cv, u))
            elif name == "flash":
                src = prev if u < .5 else cv; a = 1 - abs(u - .5)*2
                cv.paste(Image.blend(src, Image.new("RGB", (W, H), (255, 250, 238)), .85*a))
            else: engine.TRANSITIONS[name](cv, prev, u*d, d, i)
            return
    plan[k][1](cv, fr, t)

# ------------------------------------------------------------------ lumière, poussière, couleurs, grain
_spr = {}
def _blob(r):
    if r not in _spr:
        g = Image.radial_gradient("L").resize((2*r, 2*r), Image.BILINEAR)
        _spr[r] = ImageChops.invert(g).point(lambda v: int(255*(v/255)**2.2))
    return _spr[r]

def light_leak(cv, x, y, r, color, a):
    """Halo de lumière (mode « écran ») centré en x, y."""
    if a <= .01: return
    r = int(r); m = _blob(r).point(lambda v: int(v*clamp(a)))
    box = (int(x - r), int(y - r))
    reg = Image.new("RGB", (2*r, 2*r), (0, 0, 0)); reg.paste(cv.crop((box[0], box[1], box[0] + 2*r, box[1] + 2*r)))
    lit = ImageChops.screen(reg, Image.new("RGB", reg.size, color))
    reg.paste(lit, (0, 0), m); cv.paste(reg, box)

def motes(cv, t, n=26, seed=1, color=(255, 240, 210), area=(0, 200, W, 1700), a=1.0, size=(4, 11)):
    """Poussière / particules de papier en suspension qui dérivent lentement dans la lumière."""
    rnd = random.Random(seed)
    for i in range(n):
        x = (rnd.uniform(area[0], area[2]) + t*rnd.uniform(-18, 18) + 14*math.sin(t*rnd.uniform(.4, 1.1) + i)) % W
        y = area[1] + (rnd.uniform(0, area[3] - area[1]) - t*rnd.uniform(6, 28)) % (area[3] - area[1])
        r = int(rnd.uniform(*size)); tw = .55 + .45*math.sin(t*rnd.uniform(1.5, 3.5) + i)
        m = _blob(r).point(lambda v, k=a*tw: int(v*k))
        cv.paste(Image.new("RGB", (2*r, 2*r), color), (int(x - r), int(y - r)), m)

def grade(cv, sat=1.0, warm=0.0, bright=1.0, contrast=1.0):
    """Étalonnage : saturation, chaleur (+ orangé / - bleuté), luminosité, contraste."""
    im = cv
    if abs(sat - 1) > .01: im = ImageEnhance.Color(im).enhance(sat)
    if abs(contrast - 1) > .01: im = ImageEnhance.Contrast(im).enhance(contrast)
    if abs(bright - 1) > .01: im = ImageEnhance.Brightness(im).enhance(bright)
    if abs(warm) > .01:
        col = (255, 170, 80) if warm > 0 else (70, 120, 210)
        im = Image.blend(im, ImageChops.multiply(im, Image.new("RGB", im.size, col)).point(lambda v: min(255, int(v*1.6))), min(.5, abs(warm)))
    if im is not cv: cv.paste(im)

_vig = None; _grain = None
def post_fx(cv, fr, vig=.38, grain=7):
    """Vignettage doux + grain photo qui change à chaque image."""
    global _vig, _grain
    if _vig is None:
        g = Image.radial_gradient("L").resize((W, int(H*1.08)), Image.BILINEAR).crop((0, int(H*.04), W, int(H*.04) + H))
        _vig = g.point(lambda v: int(255*(1 - vig*(v/255)**2.4)))
        rnd = np.random.default_rng(7)
        _grain = [Image.fromarray(rnd.integers(0, 2*grain + 1, (H//2, W//2), np.uint8)).resize((W, H), Image.BILINEAR).convert("RGB")
                  for _ in range(6)]
    cv.paste(ImageChops.multiply(cv, Image.merge("RGB", (_vig, _vig, _vig))))
    cv.paste(ImageChops.add(cv, _grain[fr % 6], 1.0, -grain))
