"""
manga.py — rendu « manga en papier » pour la série : nos propres dessins papier passés en noir et blanc encré
avec trames (points), couleurs d'accent conservées (bleu ciel, or, rouge), grain de papier ; mise en page en cases.

  manga_filter(img, ox, oy)              encrage + trames + accents (sur une image déjà dessinée par nos scènes)
  panel(cv, fr, t, poly, content, cam)   une case : contenu plein cadre, caméra (centre, zoom, rotation), bordure, entrée glissée
  focus_lines / action_lines / rain      lignes de concentration, de vitesse, pluie (tristesse)
  impact_frame(cv)                       image d'impact (négatif noir et blanc)
  ono(cv, "CLAC !", …)                   onomatopée géante (contour épais, cisaillée, qui tremble)
  caption(cv, "…", …)                    cartouche de narration (boîte blanche ou noire, bordure nette)
  ink_transition(cv, prev, u)            l'encre balaie l'écran en diagonale
"""
import math, random
import numpy as np
from engine import *
from engine import _lowfreq

PAPER = (246, 242, 230)
INKC = (20, 18, 22)
SKY = (110, 176, 232); SKY_D = (64, 128, 196)
GOLDC = (240, 188, 40); GOLD_D = (190, 136, 20)
REDC = (222, 36, 44); RED_D = (160, 20, 30)

# ------------------------------------------------------------------ motifs (trames alignées sur l'écran)
_P = {}
def _patterns():
    if _P: return _P
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = (xx + yy)*0.70710678; v = (xx - yy)*0.70710678
    def dots(period, r):
        du = (u % period) - period/2; dv = (v % period) - period/2
        return (du*du + dv*dv) < r*r
    _P["d1"] = dots(9.0, 1.7)
    _P["d2"] = dots(9.0, 3.2)
    _P["hatch"] = ((xx - yy) % 6.0) < 2.4
    g = _lowfreq(W, H, 4242, 5)
    rng = np.random.default_rng(7); fib = rng.random((H, W)).astype(np.float32)
    _P["grain"] = (0.955 + 0.06*g - 0.03*(fib > .985)).astype(np.float32)
    _P["noise"] = _lowfreq(W, H, 99, 40)
    return _P

def _hue(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(2); mn = a.min(2); d = mx - mn + 1e-3
    h = np.where(mx == r, ((g - b)/d) % 6, np.where(mx == g, (b - r)/d + 2, (r - g)/d + 4))*60
    return h, (mx - mn)/(mx + 1e-3), mx

def manga_filter(img, ox=0, oy=0, levels=(160, 112, 66), edge=30, accent=True, dark=0.0):
    """Image RGB (nos dessins) -> planche manga. (ox, oy) : position de l'image à l'écran (trames continues d'une case à l'autre).
    dark > 0 : assombrit (scènes tristes, plus de trame)."""
    P = _patterns()
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    h, w = a.shape[:2]
    x0, y0 = max(0, int(ox)), max(0, int(oy)); x1, y1 = min(W, x0 + w), min(H, y0 + h)
    def sl(k):
        m = P[k][y0:y1, x0:x1]
        if m.shape != (h, w):
            out = np.zeros((h, w), m.dtype); out[:m.shape[0], :m.shape[1]] = m; return out
        return m
    L = a[..., 0]*.299 + a[..., 1]*.587 + a[..., 2]*.114
    if dark: L = L*(1 - dark)
    out = np.empty((h, w, 3), np.float32); out[:] = PAPER
    l0, l1, l2 = levels
    ink = ((L < l0) & (L >= l1) & sl("d1")) | ((L < l1) & (L >= l2) & sl("d2")) | ((L < l2) & (L >= 40) & (sl("hatch") | sl("d2"))) | (L < 40)
    out[ink] = INKC
    if accent:
        hu, s, mx = _hue(a)
        for m, c, cd in (((s > .26) & (hu > 186) & (hu < 228) & (mx > 110), SKY, SKY_D),
                         ((s > .42) & (hu > 34) & (hu < 60) & (mx > 130), GOLDC, GOLD_D),
                         ((s > .58) & ((hu < 12) | (hu > 344)) & (mx > 110), REDC, RED_D)):
            if not m.any(): continue
            shade = m & (L < np.percentile(L[m], 40))
            out[m] = c
            out[shade & sl("d2")] = cd
    gx = np.zeros_like(L); gy = np.zeros_like(L)
    gx[:, 1:-1] = np.abs(L[:, 2:] - L[:, :-2]); gy[1:-1, :] = np.abs(L[2:, :] - L[:-2, :])
    e = Image.fromarray(((gx + gy) > edge).astype(np.uint8)*255).filter(ImageFilter.MaxFilter(3))
    out[np.asarray(e) > 0] = INKC
    out *= sl("grain")[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")

_page = None
def page(cv):
    """Fond de page : papier blanc cassé avec grain."""
    global _page
    if _page is None:
        P = _patterns(); a = np.empty((H, W, 3), np.float32); a[:] = PAPER; a *= P["grain"][..., None]
        _page = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")
    cv.paste(_page, (0, 0))

# ------------------------------------------------------------------ cases
def _poly(p):
    if len(p) == 4 and not isinstance(p[0], (tuple, list)):
        x0, y0, x1, y1 = p; return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return [tuple(q) for q in p]

def circle_poly(cx, cy, r, n=48):
    return [(cx + r*math.cos(2*math.pi*k/n), cy + r*math.sin(2*math.pi*k/n)) for k in range(n)]

def panel(cv, fr, t, poly, content, cam=None, rot=0.0, border=9, post=None, enter=None, filt=True, dark=0.0, accent=True, flash_in=True):
    """Une case de manga.
    content(c, fr, t) dessine plein cadre (W x H) ; cam = (cx, cy, scale) : centre visé dans le contenu et zoom
    (1 = taille réelle) ; rot = angle caméra (plan cassé) ; enter = (t0, dx, dy) : la case glisse depuis (dx, dy) ;
    post(img, t) dessine dans la case (coordonnées de la case) après le filtre."""
    pts = _poly(poly)
    ox_, oy_ = 0.0, 0.0
    if enter:
        t0, dx, dy = enter
        if t < t0: return
        u = ease_out_cubic(prog(t, t0, .28)); ox_, oy_ = (1 - u)*dx, (1 - u)*dy
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    bx0, by0, bx1, by1 = int(math.floor(min(xs))), int(math.floor(min(ys))), int(math.ceil(max(xs))), int(math.ceil(max(ys)))
    pw, ph = max(2, bx1 - bx0), max(2, by1 - by0)
    c = Image.new("RGB", (W, H), PAPER); content(c, fr, t)
    cx, cy, sc = cam or (W/2, H/2, 1.0)
    if abs(rot) > .05: c = c.rotate(rot, center=(cx, cy), resample=Image.BILINEAR, fillcolor=PAPER)
    cw, ch = pw/sc, ph/sc
    img = c.transform((pw, ph), Image.EXTENT, (cx - cw/2, cy - ch/2, cx + cw/2, cy + ch/2), Image.BILINEAR, fillcolor=PAPER)
    if filt: img = manga_filter(img, bx0, by0, dark=dark, accent=accent)
    if post: post(img, t)
    if enter and flash_in:
        a = 1 - prog(t, enter[0], .18)
        if a > 0: img = Image.blend(img, Image.new("RGB", img.size, (255, 255, 255)), .7*a)
    m = Image.new("L", (pw, ph), 0); ImageDraw.Draw(m).polygon([(x - bx0, y - by0) for x, y in pts], fill=255)
    X, Y = int(round(bx0 + ox_)), int(round(by0 + oy_))
    cv.paste(img, (X, Y), m)
    if border:
        d = ImageDraw.Draw(cv); q = [(x + ox_, y + oy_) for x, y in pts]
        d.line(q + [q[0], q[1]], fill=INKC, width=border, joint="curve")

# ------------------------------------------------------------------ effets manga
def focus_lines(img, cx, cy, rx, ry, fr, n=130, col=INKC, seed=0, a=1.0):
    """Lignes de concentration : fuseaux noirs qui convergent vers (cx, cy), zone claire elliptique au centre."""
    if a <= .01: return
    d = ImageDraw.Draw(img); rnd = random.Random(seed*7919 + fr//2); R = max(img.size)*1.5
    for _ in range(int(n*a)):
        an = rnd.uniform(0, 2*math.pi); wd = rnd.uniform(.003, .011); r0 = rnd.uniform(1.0, 1.6)
        p0 = (cx + rx*r0*math.cos(an), cy + ry*r0*math.sin(an))
        d.polygon([p0, (cx + R*math.cos(an - wd), cy + R*math.sin(an - wd)), (cx + R*math.cos(an + wd), cy + R*math.sin(an + wd))], fill=col)

def action_lines(img, angle, fr, n=70, col=INKC, seed=0, length=(160, 620), width=(2, 7), a=1.0):
    """Lignes de vitesse parallèles (direction angle en degrés)."""
    if a <= .01: return
    d = ImageDraw.Draw(img); rnd = random.Random(seed*104729 + fr//2); w_, h_ = img.size
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    for _ in range(int(n*a)):
        x, y = rnd.uniform(-200, w_ + 200), rnd.uniform(-200, h_ + 200); L = rnd.uniform(*length)
        d.line([(x, y), (x + ca*L, y + sa*L)], fill=col, width=int(rnd.uniform(*width)))

def rain(img, fr, n=90, col=(60, 60, 70), seed=3, a=1.0):
    """Traits verticaux fins (tristesse, pluie)."""
    d = ImageDraw.Draw(img); rnd = random.Random(seed); w_, h_ = img.size
    for k in range(int(n*a)):
        x = rnd.uniform(0, w_); y = (rnd.uniform(0, h_) + fr*rnd.uniform(30, 60)) % (h_ + 300) - 150
        d.line([(x, y), (x + 4, y + rnd.uniform(80, 220))], fill=col, width=2)

def sparkles(img, fr, pts, col=(255, 255, 255), size=40, seed=1):
    d = ImageDraw.Draw(img); rnd = random.Random(seed)
    for k, (x, y) in enumerate(pts):
        s = size*(.6 + .4*math.sin(fr*.4 + k*1.7))
        if s <= 2: continue
        d.polygon(star_shape(x, y, s, 4, .18, 0), fill=col, outline=INKC)

def impact_frame(cv, a=1.0):
    """Image d'impact : négatif noir et blanc très contrasté."""
    if a <= .01: return
    g = cv.convert("L").point(lambda v: 0 if v > 150 else 255).convert("RGB")
    if a < .99: g = Image.blend(cv, g, a)
    cv.paste(g, (0, 0))

def ink_transition(cv, prev, u):
    """Une vague d'encre balaie l'écran en diagonale et révèle la nouvelle image."""
    P = _patterns()
    if not hasattr(ink_transition, "front"):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        ink_transition.front = (xx/W*.45 + yy/H*.55) + .18*(P["noise"] - .5)
    f = ink_transition.front; e = ease_io(clamp(u))*1.45 - .2
    a = np.asarray(cv, dtype=np.uint8); b = np.asarray(prev.convert("RGB"), dtype=np.uint8)
    out = np.where((f < e)[..., None], a, b).copy()
    band = (f >= e) & (f < e + .07)
    out[band] = INKC
    cv.paste(Image.fromarray(out, "RGB"), (0, 0))

# ------------------------------------------------------------------ textes manga
_ono_c = {}
def _ono_sprite(txt, size, fill, stroke, skew):
    k = (txt, size, fill, stroke, skew)
    if k not in _ono_c:
        sp = text_sprite(txt, font("title", size), fill, stroke=stroke, stroke_fill=INKC, maxw=1000)
        w_, h_ = sp.size; extra = int(abs(skew)*h_)
        sh = sp.transform((w_ + extra, h_), Image.AFFINE, (1, skew, -extra if skew > 0 else 0, 0, 1, 0), Image.BICUBIC)
        out = Image.new("RGBA", (sh.width + 24, sh.height + 24), (0, 0, 0, 0))
        shadow = Image.new("RGBA", sh.size, (*INKC, 255)); shadow.putalpha(sh.getchannel("A"))
        out.alpha_composite(shadow, (16, 16)); out.alpha_composite(sh, (4, 4))
        out.info["anchor"] = (out.width/2, out.height/2); _ono_c[k] = out
    return _ono_c[k]

def ono(cv, txt, x, y, t, t0, size=170, fill=(255, 255, 255), rot=-8, skew=-.22, t_out=None, stroke=None):
    """Onomatopée géante qui claque (zoom arrière rapide), tremble, puis repart."""
    if t < t0: return
    u = prog(t, t0, .16); s = lerp(1.7, 1.0, ease_out_back(u, 2.0))
    a = 1.0
    if t_out is not None:
        o = prog(t, t_out, .18); s *= 1 + .4*o; a = 1 - o
    if a <= .01: return
    sh = 6*(1 - prog(t, t0, .4)); jx, jy = sh*math.sin(t*90), sh*math.cos(t*77)
    blit(cv, _ono_sprite(txt, size, fill, stroke or max(6, size//11), skew), x + jx, y + jy, s, rot, a)

_cap_c = {}
def _cap_sprite(txt, size, dark, fnt, maxw, colbg):
    k = (txt, size, dark, fnt, maxw, colbg)
    if k not in _cap_c:
        fg = (255, 255, 255) if dark else INKC
        bg = colbg or (INKC if dark else (255, 255, 255))
        ts = text_sprite(txt, font(fnt, size), fg, maxw=maxw)
        w_, h_ = ts.width + 40, ts.height + 16
        im = Image.new("RGBA", (w_ + 12, h_ + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle([10, 10, w_ + 10, h_ + 10], fill=(*INKC, 255))
        d.rectangle([0, 0, w_, h_], fill=(*bg, 255), outline=(*INKC, 255), width=6)
        im.alpha_composite(ts, (20, 8)); im.info["anchor"] = (w_/2, h_/2); _cap_c[k] = im
    return _cap_c[k]

def caption(cv, txt, x, y, t, t0, size=56, dark=False, fnt="title", rot=0.0, maxw=900, t_out=None, colbg=None):
    """Cartouche de narration : boîte nette, entre d'un coup sec (petit rebond)."""
    if t < t0: return
    s = lerp(1.25, 1.0, ease_out_back(prog(t, t0, .14), 2.4)); a = 1.0
    if t_out is not None:
        o = prog(t, t_out, .15); a = 1 - o
    if a <= .01: return
    blit(cv, _cap_sprite(txt, size, dark, fnt, maxw, colbg), x, y, s, rot, a)

def smear(cv, t, t0, dur=.14, amount=40, horizontal=True):
    """Flou de mouvement bref (image « étirée ») pendant un mouvement rapide."""
    if not (t0 <= t < t0 + dur): return
    k = 1 - (t - t0)/dur; n = max(1, int(amount*k/8))
    base = cv.copy(); acc = np.asarray(base, dtype=np.float32)
    for i in range(1, n + 1):
        sh = base.transform(base.size, Image.AFFINE, (1, 0, -i*8 if horizontal else 0, 0, 1, 0 if horizontal else -i*8))
        acc += np.asarray(sh, dtype=np.float32)
    cv.paste(Image.fromarray((acc/(n + 1)).astype(np.uint8)), (0, 0))
