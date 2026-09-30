"""
engine.py — moteur d'animation "papier déchiré / gouache / stop-motion" pour TikTok.
Format : 1080x1920, 24 fps. Rendu PIL -> ffmpeg (pipe), en parallèle sur plusieurs processus.

Un épisode = une liste de Scene(voice, draw, sfx, trans). La durée de chaque scène est calée
sur la durée réelle de sa voix off (+ marges), puis tout est assemblé.

Repris du skill tiktok-edu-motion, avec en plus :
  - transitions « déchirure papier » entre scènes (Scene(trans="tear_v"|"tear_h"|"tear_d")) ;
  - effets : shake, zoom_punch, flash, rays, speed_lines, confetti, camera_flashes, night ;
  - motifs sur le papier (paper_sprite(pattern=...)) pour les maillots ;
  - vrais bruitages (dossier de .mp3, ex. générés avec ElevenLabs) + ducking sous la voix ;
  - rendu multi-processus.
Voir SKILL.md et episodes/messi/messi.py.
"""
import math, os, random, re, subprocess, wave, hashlib, multiprocessing
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H, FPS = 1080, 1920, 24
SR = 44100
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.environ.get("EDU_ASSETS", "/tmp/edu-assets")

PAL = dict(
    coral=(232, 112, 88), mustard=(228, 176, 58), teal=(38, 150, 138),
    cream=(245, 235, 214), charcoal=(46, 44, 42), paper=(251, 246, 234),
    ink=(28, 26, 24), red=(205, 62, 48), sand=(214, 176, 128), clay=(196, 120, 82),
    gold=(238, 190, 60), white=(255, 252, 245), sky=(214, 230, 222),
)
# Zone de scène (à l'intérieur de la fenêtre terminal). Zone sûre TikTok : éviter y>1560 et x>930 pour le texte important.
STAGE = (30, 122, W - 30, H - 30)
CX = W // 2

# ---------------------------------------------------------------- polices
def font(kind, size):
    files = {
        "title": os.path.join(ASSETS, "fonts/LilitaOne-Regular.ttf"),
        "hand": os.path.join(ASSETS, "fonts/PatrickHand-Regular.ttf"),
        "brush": os.path.join(ASSETS, "fonts/CaveatBrush-Regular.ttf"),
        "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    }
    p = files[kind]
    if not os.path.exists(p):
        p = files["sans"]
    return ImageFont.truetype(p, size)

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, t0, dur): return clamp((t - t0) / dur) if dur > 0 else (1.0 if t >= t0 else 0.0)
def lerp(a, b, u): return a + (b - a) * u
def ease_out_cubic(u): return 1 - (1 - u) ** 3
def ease_in_cubic(u): return u ** 3
def ease_io(u): return 4 * u ** 3 if u < .5 else 1 - (-2 * u + 2) ** 3 / 2
def ease_out_back(u, s=1.9): u -= 1; return 1 + (s + 1) * u ** 3 + s * u ** 2
def ease_out_elastic(u):
    if u in (0, 1): return u
    return 2 ** (-10 * u) * math.sin((u * 10 - .75) * (2 * math.pi / 3)) + 1
def lerp_pt(a, b, u): return (lerp(a[0], b[0], u), lerp(a[1], b[1], u))
def bezier(p0, p1, p2, u):
    return ((1-u)**2*p0[0]+2*(1-u)*u*p1[0]+u*u*p2[0], (1-u)**2*p0[1]+2*(1-u)*u*p1[1]+u*u*p2[1])

def boil(frame):
    """Index de variante stop-motion : change toutes les 3 images (8 fois/s)."""
    return (frame // 3) % 3

def jit(key, b, amp=1.5):
    h = int(hashlib.md5(f"{key}{b}".encode()).hexdigest()[:8], 16)
    return ((h % 1000) / 1000 * 2 - 1) * amp, (((h // 1000) % 1000) / 1000 * 2 - 1) * amp

# ---------------------------------------------------------------- formes
def rect_pts(w, h): return [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]
def ellipse_pts(w, h, n=40): return [(w/2*math.cos(2*math.pi*i/n), h/2*math.sin(2*math.pi*i/n)) for i in range(n)]
def poly_pts(pts): return list(pts)
def pixel_square_pts(s, step):
    """Carré aux coins 'pixel' (escalier)."""
    a, k = s / 2, step
    return [(-a+k, -a), (a-k, -a), (a-k, -a+k), (a, -a+k), (a, a-k), (a-k, a-k), (a-k, a),
            (-a+k, a), (-a+k, a-k), (-a, a-k), (-a, -a+k), (-a+k, -a+k)]

def torn(pts, rough, seed, seg=10):
    rnd = random.Random(seed)
    out = []
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]; x1, y1 = pts[(i+1) % n]
        L = math.hypot(x1-x0, y1-y0); k = max(1, int(L / seg))
        nx, ny = (-(y1-y0)/L, (x1-x0)/L) if L else (0, 0)
        for j in range(k):
            u = j / k; d = rnd.uniform(-rough, rough)
            out.append((x0+(x1-x0)*u+nx*d, y0+(y1-y0)*u+ny*d))
    return out

_noise_cache = {}
def _lowfreq(w, h, seed, scale=24):
    rng = np.random.default_rng(seed)
    small = rng.random((max(2, h//scale), max(2, w//scale))).astype(np.float32)
    im = Image.fromarray((small*255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32)/255.0

def paper_sprite(pts, fill, seed=0, rough=2.2, texture=True, shadow=True, outline=True,
                 hatch=False, pad=26, pattern=None):
    """Découpe papier : bord déchiré, texture gouache + crayon, ombre carton.
    pattern(d, ox, oy) : dessine un motif (rayures de maillot…) sur l'aplat, en coordonnées locales + (ox, oy)."""
    tp = torn(pts, rough, seed)
    xs = [p[0] for p in tp]; ys = [p[1] for p in tp]
    minx, miny = min(xs), min(ys)
    w = int(max(xs)-minx) + pad*2; h = int(max(ys)-miny) + pad*2
    ox, oy = -minx + pad, -miny + pad
    poly = [(x+ox, y+oy) for x, y in tp]
    mask = Image.new("L", (w, h), 0); ImageDraw.Draw(mask).polygon(poly, fill=255)
    if pattern:
        base = Image.new("RGB", (w, h), tuple(fill)); pattern(ImageDraw.Draw(base), ox, oy)
        rgb = np.asarray(base, dtype=np.float32).copy()
    else:
        rgb = np.zeros((h, w, 3), np.float32); rgb[:] = fill
    if texture:
        g = _lowfreq(w, h, seed+7, 18)                       # gouache (lavis)
        rgb *= (0.92 + 0.14*g)[..., None]
        rng = np.random.default_rng(seed+13)                  # grain crayon
        speck = rng.random((h, w)).astype(np.float32)
        rgb += ((speck > 0.93)*18 - (speck < 0.04)*14)[..., None]
        if hatch:
            yy, xx = np.mgrid[0:h, 0:w]
            hl = (((xx + yy) % 9) < 1.2) * (_lowfreq(w, h, seed+3, 10) > .45)
            rgb -= (hl*18)[..., None]
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    body = Image.fromarray(rgb, "RGB").convert("RGBA"); body.putalpha(mask)
    if outline:
        d = ImageDraw.Draw(body)
        d.line(poly + [poly[0]], fill=(*[int(c*.62) for c in fill], 150), width=2)
    out = Image.new("RGBA", (w+14, h+16), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", (w, h), (35, 28, 22, 0)); sh.putalpha(mask.point(lambda v: int(v*.34)))
        sh = sh.filter(ImageFilter.GaussianBlur(5))
        out.alpha_composite(sh, (9, 11))
    out.alpha_composite(body, (0, 0))
    out.info["anchor"] = (ox, oy)     # position du (0,0) local dans le sprite
    return out

class Paper:
    """Élément papier avec 3 variantes 'boil'. .draw(canvas, frame, x, y, ...)"""
    def __init__(self, pts, fill, key, **kw):
        self.key = key
        self.v = [paper_sprite(pts, fill, seed=(int(hashlib.md5(key.encode()).hexdigest()[:6],16) % 9999)+i*101, **kw) for i in range(3)]
        self.decor = []      # fonctions (img, anchor) pour dessiner par-dessus
    def add(self, fn):
        for im in self.v: fn(ImageDraw.Draw(im), im.info["anchor"])
        return self
    def draw(self, cv, frame, x, y, scale=1.0, rot=0.0, alpha=1.0, amp=1.5):
        if scale <= 0.01 or alpha <= 0.01: return
        b = boil(frame); jx, jy = jit(self.key, b, amp)
        blit(cv, self.v[b], x + jx, y + jy, scale, rot + jx*0.25, alpha)

def blit(cv, spr, x, y, scale=1.0, rot=0.0, alpha=1.0):
    ax, ay = spr.info.get("anchor", (spr.width/2, spr.height/2))
    im = spr
    if abs(scale-1) > 1e-3:
        im = im.resize((max(1, int(im.width*scale)), max(1, int(im.height*scale))), Image.BILINEAR)
        ax, ay = ax*scale, ay*scale
    if abs(rot) > 0.05:
        cx0, cy0 = im.width/2, im.height/2
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
        a = math.radians(rot); dx, dy = ax-cx0, ay-cy0
        ax = im.width/2 + dx*math.cos(a) + dy*math.sin(a)
        ay = im.height/2 - dx*math.sin(a) + dy*math.cos(a)
    if alpha < 0.999:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v*alpha)))
    cv.paste(im, (int(round(x-ax)), int(round(y-ay))), im)

# ---------------------------------------------------------------- texte
def text_sprite(txt, fnt, fg, stroke=0, stroke_fill=None, maxw=None, spacing=6, align="center"):
    lines = wrap(txt, fnt, maxw) if maxw else txt.split("\n")
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bb = [d0.textbbox((0, 0), l, font=fnt, stroke_width=stroke) for l in lines]
    lh = max(b[3]-b[1] for b in bb) if bb else 10
    asc = fnt.getmetrics()[0]
    w = max(b[2]-b[0] for b in bb) + 20; h = (asc+fnt.getmetrics()[1])*len(lines) + spacing*(len(lines)-1) + 20
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = 10
    for l, b in zip(lines, bb):
        lw = b[2]-b[0]
        x = 10 + ((w-20-lw)/2 if align == "center" else 0) - b[0]
        d.text((x, y), l, font=fnt, fill=fg, stroke_width=stroke, stroke_fill=stroke_fill)
        y += asc + fnt.getmetrics()[1] + spacing
    im.info["anchor"] = (w/2, h/2)
    return im

def wrap(txt, fnt, maxw):
    out = []
    for para in txt.split("\n"):
        cur = ""
        for wd in para.split(" "):
            test = (cur+" "+wd).strip()
            if fnt.getlength(test) <= maxw or not cur: cur = test
            else: out.append(cur); cur = wd
        out.append(cur)
    return out

class Label:
    """Texte posé sur une bande de papier déchiré (boil inclus)."""
    def __init__(self, txt, key, fnt, fg, bg=None, maxw=900, padx=34, pady=18, rough=3.0, stroke=0, stroke_fill=None):
        self.key = key
        ts = text_sprite(txt, fnt, fg, stroke=stroke, stroke_fill=stroke_fill, maxw=maxw)
        self.v = []
        for i in range(3):
            if bg is not None:
                p = paper_sprite(rect_pts(ts.width-20+padx*2, ts.height-20+pady*2), bg,
                                 seed=(int(hashlib.md5(key.encode()).hexdigest()[:6],16) % 9999)+i*37, rough=rough)
                ax, ay = p.info["anchor"]
                p.alpha_composite(ts, (int(ax-ts.width/2), int(ay-ts.height/2)))
                p.info["anchor"] = (ax, ay)
            else:
                p = ts.copy(); p.info["anchor"] = ts.info["anchor"]
            self.v.append(p)
    def draw(self, cv, frame, x, y, scale=1.0, rot=0.0, alpha=1.0, amp=1.0):
        if scale <= 0.01 or alpha <= 0.01: return
        b = boil(frame); jx, jy = jit(self.key, b, amp)
        blit(cv, self.v[b], x+jx, y+jy, scale, rot, alpha)

def pop_in(t, t0, d=0.45):
    u = prog(t, t0, d); return ease_out_back(u) if u > 0 else 0.0

def headline(cv, frame, lab, t, T, y=330, t0=0.15, rot=-1.5):
    """Titre de scène : pop à l'entrée, s'envole à la sortie."""
    s = pop_in(t, t0, .5)
    out = prog(t, T-.4, .35)
    lab.draw(cv, frame, CX, y - 260*ease_in_cubic(out), s*(1-.3*out), rot, 1-out)

# ---------------------------------------------------------------- traits crayon
def pencil_line(d, pts, u=1.0, fill=PAL["ink"], width=6, seed=0, wobble=1.5):
    """Trait crayon tracé progressivement (u de 0 à 1)."""
    if u <= 0 or len(pts) < 2: return
    rnd = random.Random(seed)
    L = [0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1]+math.hypot(b[0]-a[0], b[1]-a[1]))
    tot = L[-1]*u; poly = [pts[0]]
    for i in range(1, len(pts)):
        if L[i] <= tot: poly.append(pts[i])
        else:
            r = (tot-L[i-1])/(L[i]-L[i-1]+1e-9); poly.append(lerp_pt(pts[i-1], pts[i], r)); break
    dense = []
    for a, b in zip(poly, poly[1:]):
        n = max(1, int(math.hypot(b[0]-a[0], b[1]-a[1])/14))
        for k in range(n): dense.append(lerp_pt(a, b, k/n))
    dense.append(poly[-1])
    dense = [(x+rnd.uniform(-wobble, wobble), y+rnd.uniform(-wobble, wobble)) for x, y in dense]
    d.line(dense, fill=fill, width=width, joint="curve")
    d.line([(x+1.5, y-1) for x, y in dense], fill=fill, width=max(1, width//3))

def arrow(d, a, b, u=1.0, fill=PAL["ink"], width=7, seed=0, head=26, curve=0.0):
    mid = ((a[0]+b[0])/2 - (b[1]-a[1])*curve, (a[1]+b[1])/2 + (b[0]-a[0])*curve)
    pts = [bezier(a, mid, b, k/20) for k in range(21)]
    pencil_line(d, pts, u, fill, width, seed)
    if u >= 0.98:
        p1, p2 = pts[-3], pts[-1]; ang = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
        for s in (2.6, -2.6):
            d.line([p2, (p2[0]+head*math.cos(ang+s), p2[1]+head*math.sin(ang+s))], fill=fill, width=width)

# ---------------------------------------------------------------- particules
def particles(cv, frame, key, origin, u, n=18, spread=260, colors=None, size=16, gravity=380):
    if u <= 0 or u >= 1: return
    colors = colors or [PAL["coral"], PAL["mustard"], PAL["teal"]]
    rnd = random.Random(key); d = ImageDraw.Draw(cv)
    for i in range(n):
        ang = rnd.uniform(0, 2*math.pi); sp = rnd.uniform(.4, 1)*spread
        x = origin[0] + math.cos(ang)*sp*ease_out_cubic(u)
        y = origin[1] + math.sin(ang)*sp*ease_out_cubic(u) + gravity*u*u
        s = size*(1-u)*rnd.uniform(.6, 1.2)
        if (frame//3 + i) % 2: s *= .85
        d.rectangle([x-s/2, y-s/2, x+s/2, y+s/2], fill=colors[i % len(colors)])

def regroup(cv, frame, key, src, dst, u, n=24, colors=None, size=14):
    """Particules qui se dispersent puis se regroupent vers dst (transition 'se reforme')."""
    colors = colors or [PAL["coral"], PAL["mustard"], PAL["teal"]]
    rnd = random.Random(key); d = ImageDraw.Draw(cv)
    for i in range(n):
        c = (rnd.uniform(-220, 220), rnd.uniform(-220, 220))
        p = bezier(src, (lerp(src[0], dst[0], .5)+c[0], lerp(src[1], dst[1], .5)+c[1]), dst, ease_io(u))
        s = size*(1-.6*abs(u-.5)*2)
        d.rectangle([p[0]-s/2, p[1]-s/2, p[0]+s/2, p[1]+s/2], fill=colors[i % len(colors)])

# ---------------------------------------------------------------- décor : fenêtre terminal
_bg = None
_frame_overlay = None
def frame_overlay(title):
    """Cadre terminal (tout sauf la scène) : recollé après le dessin pour 'clipper' ce qui déborde."""
    global _frame_overlay
    if _frame_overlay is None:
        base = background(0, title).convert("RGBA")
        m = Image.new("L", (W, H), 255); ImageDraw.Draw(m).rounded_rectangle(STAGE, 20, fill=0)
        base.putalpha(m); _frame_overlay = base
    return _frame_overlay
def finish(cv, title):
    ov = frame_overlay(title); cv.paste(ov, (0, 0), ov); return cv
def background(frame, title="~/savoir $ ./episode"):
    global _bg
    if _bg is None:
        _bg = []
        for i in range(3):
            im = Image.new("RGB", (W, H), (27, 25, 24))
            d = ImageDraw.Draw(im)
            x0, y0, x1, y1 = 18, 22, W-18, H-18
            d.rounded_rectangle([x0, y0, x1, y1], 30, fill=(38, 36, 34))
            d.rounded_rectangle([x0, y0, x1, 112], 30, fill=(50, 47, 44)); d.rectangle([x0, 80, x1, 112], fill=(50, 47, 44))
            for k, c in enumerate((PAL["coral"], PAL["mustard"], PAL["teal"])):
                d.ellipse([58+k*46-13, 67-13, 58+k*46+13, 67+13], fill=c)
            f = font("mono", 30); d.text((220, 50), title, font=f, fill=(170, 164, 154))
            sx0, sy0, sx1, sy1 = STAGE
            g = _lowfreq(sx1-sx0, sy1-sy0, 50+i, 40)
            rng = np.random.default_rng(90+i)
            fib = rng.random((sy1-sy0, sx1-sx0)).astype(np.float32)
            st = np.zeros((sy1-sy0, sx1-sx0, 3), np.float32); st[:] = PAL["cream"]
            st *= (0.95+0.07*g)[..., None]; st -= ((fib > .985)*16)[..., None]
            # vignette douce
            yy, xx = np.mgrid[0:sy1-sy0, 0:sx1-sx0]
            vx = (xx/(sx1-sx0)-.5); vy = (yy/(sy1-sy0)-.5)
            st *= (1-.22*(vx*vx+vy*vy)*2)[..., None]
            stage = Image.fromarray(np.clip(st, 0, 255).astype(np.uint8))
            m = Image.new("L", stage.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, stage.width-1, stage.height-1], 20, fill=255)
            im.paste(stage, (sx0, sy0), m)
            _bg.append(im)
    return _bg[boil(frame)].copy()

# ---------------------------------------------------------------- mascotte
class Mascot:
    """Pixel : carré corail, yeux noirs carrés, proportions FIXES (ne jamais les modifier)."""
    SIZE = 190
    def __init__(self):
        s = self.SIZE
        self.body = Paper(pixel_square_pts(s, 22), PAL["coral"], "mascot", rough=1.6, hatch=True)
        self.foot = Paper(rect_pts(34, 22), PAL["charcoal"], "foot", rough=1, shadow=False)
    def draw(self, cv, frame, x, y, look=(0, 0), mood="normal", hop=0.0, scale=1.0, t=0.0, arm=None, rot=0.0):
        s = self.SIZE*scale; y = y - hop
        squash = 1 + 0.06*math.sin(t*2*math.pi*1.2) if hop == 0 else 1
        for dx in (-.24, .24):
            self.foot.draw(cv, frame, x+dx*s, y+s*.55 + hop*0.0, scale, 0, 1, .8)
        self.body.draw(cv, frame, x, y, scale*squash, rot)
        d = ImageDraw.Draw(cv)
        blink = (int(t*24) % 80) < 3
        ex = s*.2; ey = -s*.08; es = s*.13
        lx, ly = look[0]*s*.07, look[1]*s*.06
        for sgn in (-1, 1):
            cx_, cy_ = x+sgn*ex+lx, y+ey+ly
            if mood == "happy":
                d.line([(cx_-es*.6, cy_+es*.2), (cx_, cy_-es*.4), (cx_+es*.6, cy_+es*.2)], fill=PAL["ink"], width=int(8*scale))
            elif blink:
                d.rectangle([cx_-es/2, cy_-3, cx_+es/2, cy_+3], fill=PAL["ink"])
            else:
                k = 1.35 if mood == "surprised" else 1
                d.rectangle([cx_-es*k/2, cy_-es*k/2, cx_+es*k/2, cy_+es*k/2], fill=PAL["ink"])
                d.rectangle([cx_-es*k/2+4, cy_-es*k/2+4, cx_-es*k/2+10, cy_-es*k/2+10], fill=(255, 255, 255))
        if mood == "surprised":
            d.rectangle([x-s*.06, y+s*.18, x+s*.06, y+s*.3], fill=PAL["ink"])
        elif mood == "happy":
            d.line([(x-s*.12, y+s*.2), (x, y+s*.27), (x+s*.12, y+s*.2)], fill=PAL["ink"], width=int(6*scale))
        if arm:  # bras pixel qui pointe : arm = (tx, ty)
            sx = x + (s*.5 if arm[0] > x else -s*.5); sy = y+s*.12
            ang = math.atan2(arm[1]-sy, arm[0]-sx)
            ex2, ey2 = sx+math.cos(ang)*s*.42, sy+math.sin(ang)*s*.42
            d.line([(sx, sy), (ex2, ey2)], fill=PAL["coral"], width=int(20*scale))
            d.rectangle([ex2-12*scale, ey2-12*scale, ex2+12*scale, ey2+12*scale], fill=PAL["coral"])

# ---------------------------------------------------------------- scènes
class Scene:
    """trans : transition d'entrée depuis la scène précédente (None = continuité gérée par les scènes,
    "tear_v" / "tear_h" / "tear_d" = la dernière image de la scène précédente se déchire et s'envole)."""
    def __init__(self, name, voice, draw, sfx=None, pad_in=0.35, pad_out=0.55, min_dur=0, trans=None, trans_dur=0.8):
        self.name, self.voice, self.draw_fn = name, voice, draw
        self.sfx = sfx or []      # [(t_local ou fonction(T), nom [, gain])]
        self.pad_in, self.pad_out, self.min_dur = pad_in, pad_out, min_dur
        self.trans, self.trans_dur = trans, trans_dur
        self.audio = None; self.T = None

# ---------------------------------------------------------------- voix off (Piper, hors-ligne)
def tts(text, out_wav, length_scale=1.12):
    model = os.path.join(ASSETS, "voice/fr-siwis-medium.onnx")
    subprocess.run(["python3", "-m", "piper", "-m", model, "-f", out_wav, "--length-scale", str(length_scale),
                    "--sentence-silence", "0.25"], input=text.encode(), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(out_wav) as w:
        sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)/32768
    t_old = np.arange(len(a))/sr; t_new = np.arange(int(len(a)*SR/sr))/SR
    return np.interp(t_new, t_old, a).astype(np.float32)

def load_audio(path):
    """Charge n'importe quel fichier audio (ElevenLabs, Google TTS, voix enregistrée…) en mono 44,1 kHz."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32)/32768

def split_audio_by_silence(path, n_scenes, min_sil=0.45):
    """Découpe une voix off d'un seul bloc en n_scenes morceaux, aux silences les plus longs."""
    a = load_audio(path); hop = int(SR*0.02)
    env = np.array([np.abs(a[i:i+hop]).max() for i in range(0, len(a), hop)])
    quiet = env < 0.02; runs = []; i = 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]: j += 1
            if (j-i)*0.02 >= min_sil and i > 0 and j < len(quiet): runs.append((j-i, (i+j)//2*hop))
            i = j
        else: i += 1
    cuts = sorted(c for _, c in sorted(runs, reverse=True)[:n_scenes-1])
    if len(cuts) != n_scenes-1:
        raise ValueError(f"{len(cuts)+1} blocs trouvés pour {n_scenes} scènes : génère plutôt 1 fichier par scène")
    b = [0]+cuts+[len(a)]
    def trim(x, thr=0.02, keep=int(0.06*SR)):
        idx = np.where(np.abs(x) > thr)[0]
        return x if len(idx) == 0 else x[max(0, idx[0]-keep):idx[-1]+keep]
    return [trim(a[b[k]:b[k+1]]) for k in range(n_scenes)]

def export_voice_script(scenes, path, title=""):
    """Écrit le script voix off prêt à coller (ElevenLabs, Google TTS…), scène par scène + un bloc."""
    L = [f"{title.upper()} — VOIX OFF", "", "Conseil : 1 fichier audio par scène (scene_1.mp3 … scene_N.mp3).", ""]
    for i, sc in enumerate(scenes, 1): L += [f"=== SCÈNE {i} ===", sc.voice, ""]
    L += ["", "----- VERSION EN UN SEUL BLOC -----", ""] + [sc.voice+"\n" for sc in scenes]
    open(path, "w").write("\n".join(L)); return path

# ---------------------------------------------------------------- bruitages synthétisés
def sfx_bank():
    rng = np.random.default_rng(3)
    def env(n, a=0.005, r=0.1):
        t = np.arange(n)/SR; return np.minimum(1, t/a)*np.exp(-t/r)
    def tone(f0, f1, dur, r):
        n = int(dur*SR); t = np.arange(n)/SR; f = np.linspace(f0, f1, n)
        return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n, .003, r)
    def noise(dur, r, lp=0.5):
        n = int(dur*SR); x = rng.standard_normal(n)
        y = np.zeros(n); a = lp
        for i in range(1, n): y[i] = a*y[i-1]+(1-a)*x[i]
        return y*env(n, .01, r)
    def mx(*xs):
        n = max(len(x) for x in xs); o = np.zeros(n)
        for x in xs: o[:len(x)] += x
        return o
    b = {}
    b["pop"] = tone(900, 350, .12, .04)*.5
    b["pop2"] = tone(600, 1200, .1, .035)*.4
    b["swish"] = noise(.35, .12, .15)*.35
    b["thud"] = mx(tone(140, 60, .3, .09)*.8, noise(.1, .02, .6)*.2)
    b["stamp"] = mx(tone(110, 50, .35, .1)*.9, noise(.15, .03, .3)*.5)
    n = int(.8*SR); t = np.arange(n)/SR
    b["clink"] = sum(np.sin(2*np.pi*f*t)*np.exp(-t/d) for f, d in ((2350, .25), (3710, .18), (5120, .1), (6800, .07)))*.12
    b["paper"] = np.concatenate([noise(.05, .02, .1)*rng.uniform(.3, .6) for _ in range(8)])*.6
    b["scribble"] = np.concatenate([noise(.09, .05, .4)*.25 for _ in range(6)])
    b["whoosh_up"] = noise(.5, .2, .3)*np.linspace(.2, 1, int(.5*SR))*.3
    b["ding"] = (np.sin(2*np.pi*1320*t)*np.exp(-t/.35)+.4*np.sin(2*np.pi*2640*t)*np.exp(-t/.2))*.18
    b["poof"] = noise(.45, .15, .7)*.35
    b["tick"] = tone(1800, 1700, .03, .01)*.3
    return {k: v.astype(np.float32) for k, v in b.items()}

# ---------------------------------------------------------------- blit non uniforme (retournements, écrasements)
def blit_sxy(cv, spr, x, y, sx=1.0, sy=1.0, rot=0.0, alpha=1.0):
    """Comme blit mais avec une échelle X/Y séparée (sx=|cos| pour un retournement de carte/maillot)."""
    if abs(sx) < 0.02 or sy < 0.02: return
    ax, ay = spr.info.get("anchor", (spr.width/2, spr.height/2))
    im = spr.resize((max(1, int(spr.width*abs(sx))), max(1, int(spr.height*sy))), Image.BILINEAR)
    if sx < 0: im = im.transpose(Image.FLIP_LEFT_RIGHT); ax = spr.width - ax
    im.info["anchor"] = (ax*abs(sx), ay*sy)
    blit(cv, im, x, y, 1.0, rot, alpha)

def layer(w, h, anchor):
    """Calque transparent pour composer un objet (joueur…) puis le transformer d'un bloc."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); im.info["anchor"] = anchor; return im

# ---------------------------------------------------------------- effets caméra (sur la zone de scène)
def _stage_box():
    return STAGE

def shake(cv, t, amp=14, freq=38, seed=0):
    """Tremblement de la scène (impact, tampon, but)."""
    if amp < 0.5: return
    dx = int(amp*math.sin(t*freq + seed)); dy = int(amp*0.7*math.cos(t*freq*1.3 + seed*2))
    st = cv.crop(STAGE); cv.paste(st, (STAGE[0]+dx, STAGE[1]+dy))

def zoom_punch(cv, z, center=None):
    """Zoom rapide sur la scène (z=1.0 : rien, 1.08 : punch)."""
    if z <= 1.002: return
    sx0, sy0, sx1, sy1 = STAGE; w, h = sx1-sx0, sy1-sy0
    cx, cy = center or ((sx0+sx1)/2, (sy0+sy1)/2)
    cw, ch = w/z, h/z
    x0 = clamp(cx-cw/2, sx0, sx1-cw); y0 = clamp(cy-ch/2, sy0, sy1-ch)
    cv.paste(cv.crop((int(x0), int(y0), int(x0+cw), int(y0+ch))).resize((w, h), Image.BILINEAR), (sx0, sy0))

def flash(cv, a, color=(255, 252, 240)):
    """Flash blanc (ou coloré) sur la scène, a de 0 à 1."""
    if a <= 0.01: return
    st = cv.crop(STAGE); ov = Image.new("RGB", st.size, color)
    cv.paste(Image.blend(st, ov, clamp(a)), STAGE[:2])

def tint(cv, a, color=(24, 34, 70)):
    """Assombrit / teinte la scène (nuit, drame)."""
    if a <= 0.01: return
    st = cv.crop(STAGE); ov = Image.new("RGB", st.size, color)
    cv.paste(Image.blend(st, ov, clamp(a)), STAGE[:2])

def rays(cv, center, t, a=1.0, n=14, r=1500, color=(250, 226, 150), width=0.11, speed=0.25):
    """Rayons de lumière qui tournent derrière un objet (trophée, révélation)."""
    if a <= 0.01: return
    ov = Image.new("RGBA", cv.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    cx, cy = center
    for k in range(n):
        an = t*speed + k*2*math.pi/n
        d.polygon([(cx, cy), (cx+r*math.cos(an-width), cy+r*math.sin(an-width)), (cx+r*math.cos(an+width), cy+r*math.sin(an+width))],
                  fill=(*color, int(150*a)))
    m = Image.new("L", cv.size, 0); ImageDraw.Draw(m).rounded_rectangle(STAGE, 20, fill=255)
    ov.putalpha(ImageChops.multiply(ov.getchannel("A"), m))
    cv.paste(ov, (0, 0), ov)

def speed_lines(cv, frame, center, a=1.0, n=46, color=(46, 44, 42), inner=380, seed=0):
    """Lignes de vitesse façon manga, redessinées toutes les 2 images."""
    if a <= 0.01: return
    rnd = random.Random(seed*1000 + frame//2); d = ImageDraw.Draw(cv); cx, cy = center
    for k in range(n):
        an = rnd.uniform(0, 2*math.pi); r0 = inner*rnd.uniform(.85, 1.4); r1 = r0 + rnd.uniform(250, 700)*a
        w = rnd.randint(3, 9)
        d.line([(cx+r0*math.cos(an), cy+r0*math.sin(an)), (cx+r1*math.cos(an), cy+r1*math.sin(an))], fill=color, width=w)

CONFETTI_COLS = None
def confetti(cv, frame, key, t, n=70, dur=4.0, colors=None, area=None):
    """Confettis en papier qui tombent en tournoyant (t = temps depuis le déclenchement)."""
    if t <= 0 or t > dur: return
    colors = colors or [PAL["coral"], PAL["mustard"], PAL["teal"], PAL["gold"], PAL["white"], (116, 172, 223)]
    x0, y0, x1, y1 = area or STAGE
    rnd = random.Random(key); d = ImageDraw.Draw(cv)
    for i in range(n):
        sx = rnd.uniform(x0, x1); delay = rnd.uniform(0, .6); sp = rnd.uniform(380, 720)
        tt = t - delay
        if tt <= 0: continue
        x = sx + 60*math.sin(tt*rnd.uniform(2, 5) + i); y = y0 - 40 + sp*tt
        if y > y1 + 40: continue
        w, h = rnd.uniform(14, 24), rnd.uniform(8, 13); an = tt*rnd.uniform(4, 9) + i
        flip = abs(math.cos(tt*rnd.uniform(3, 7) + i))
        pts = [(-w/2, -h/2*flip), (w/2, -h/2*flip), (w/2, h/2*flip), (-w/2, h/2*flip)]
        pts = [(x+px*math.cos(an)-py*math.sin(an), y+px*math.sin(an)+py*math.cos(an)) for px, py in pts]
        d.polygon(pts, fill=colors[i % len(colors)])

def star_shape(cx, cy, r, k=4, inner=0.28, rot=0.0):
    pts = []
    for i in range(k*2):
        rr = r if i % 2 == 0 else r*inner; an = rot + i*math.pi/k
        pts.append((cx+rr*math.cos(an), cy+rr*math.sin(an)))
    return pts

def camera_flashes(cv, frame, key, t, dur=1.6, n=10, area=None):
    """Flashs de photographes : éclairs blancs à des positions aléatoires, 2 images chacun."""
    if t <= 0 or t > dur: return
    x0, y0, x1, y1 = area or (STAGE[0]+60, STAGE[1]+300, STAGE[2]-60, STAGE[3]-300)
    rnd = random.Random(key); d = ImageDraw.Draw(cv)
    for i in range(n):
        ti = rnd.uniform(0, dur-.15); x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if 0 <= t - ti < 2/FPS:
            r = rnd.uniform(40, 80)
            d.ellipse([x-r*.45, y-r*.45, x+r*.45, y+r*.45], fill=(255, 255, 250))
            d.polygon(star_shape(x, y, r*1.6, 4, .12, rnd.uniform(0, 1)), fill=(255, 255, 240))

def drops(cv, key, t, origins, n=6, color=(120, 190, 235), size=12, speed=520):
    """Larmes / gouttes qui tombent depuis des points (yeux…)."""
    if t <= 0: return
    d = ImageDraw.Draw(cv); rnd = random.Random(key)
    for k in range(n):
        for (ox, oy) in origins:
            tt = (t*1.3 + k/n) % 1.0
            x = ox + rnd.uniform(-4, 4); y = oy + speed*tt*tt*.8
            s = size*(1-.3*tt)
            d.polygon([(x, y-s*1.2), (x+s*.6, y), (x, y+s*.6), (x-s*.6, y)], fill=color)
            d.ellipse([x-s*.6, y-s*.35, x+s*.6, y+s*.75], fill=color)

def counter(v0, v1, u, sep=" "):
    """Compteur qui défile : renvoie la valeur entière formatée (1 000 000)."""
    n = int(round(lerp(v0, v1, ease_out_cubic(clamp(u)))))
    return f"{n:,}".replace(",", sep)

def typewriter(txt, u):
    return txt[:int(len(txt)*clamp(u))]

# ---------------------------------------------------------------- déchirure papier
def _tear_line(w, h, kind, seed, rough=16, step=18):
    rnd = random.Random(seed)
    pts = []
    if kind == "h":
        base = h*rnd.uniform(.44, .56); slope = rnd.uniform(-.12, .12)
        for x in range(-20, w+21, step): pts.append((x, base + slope*(x-w/2) + rnd.uniform(-rough, rough)))
    else:
        base = w*rnd.uniform(.44, .56); slope = rnd.uniform(-.1, .1) if kind == "v" else rnd.choice((-.42, .42))
        for y in range(-20, h+21, step): pts.append((base + slope*(y-h/2) + rnd.uniform(-rough, rough), y))
    return pts

def tear_split(img, kind="v", seed=0, fiber=(250, 246, 236), rough=16):
    """Coupe une image RGBA en deux morceaux le long d'une déchirure irrégulière, avec le liseré blanc
    des fibres du papier. Renvoie (pièce A, pièce B, ligne) ; A = gauche/haut."""
    img = img.convert("RGBA"); w, h = img.size
    line = _tear_line(w, h, "h" if kind == "h" else ("v" if kind == "v" else "d"), seed, rough)
    if kind == "h":
        polyA = [(-30, -30), (w+30, -30)] + list(reversed(line)); polyB = [(-30, h+30), (w+30, h+30)] + list(reversed(line))
        off = (0, 1)
    else:
        polyA = [(-30, -30)] + line + [(-30, h+30)]; polyB = [(w+30, -30)] + line + [(w+30, h+30)]
        off = (1, 0)
    rnd = random.Random(seed+5)
    out = []
    for poly, sgn in ((polyA, -1), (polyB, 1)):
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).polygon(poly, fill=255)
        m = ImageChops.multiply(m, img.getchannel("A"))
        piece = img.copy(); piece.putalpha(m)
        # liseré de fibres : bande claire irrégulière le long de la déchirure, côté intérieur de la pièce
        band = Image.new("L", (w, h), 0); db = ImageDraw.Draw(band)
        for (x, y) in line:
            r = rnd.uniform(3, 9)
            cx, cy = x - sgn*off[0]*r*.8, y - sgn*off[1]*r*.8
            db.ellipse([cx-r, cy-r, cx+r, cy+r], fill=255)
        band = ImageChops.multiply(band, m)
        fib = Image.new("RGBA", (w, h), (*fiber, 255)); fib.putalpha(band)
        piece.alpha_composite(fib)
        out.append(piece)
    return out[0], out[1], line

_tear_cache = {}
def tear_transition(cv, prev, u, kind="tear_v", seed=0):
    """Transition : l'image précédente (prev, RGB plein cadre) se fissure puis ses deux moitiés s'envolent,
    révélant la nouvelle scène déjà dessinée dans cv. u de 0 à 1."""
    k = {"tear_v": "v", "tear_h": "h", "tear_d": "d"}[kind]
    key = (id(prev), kind, seed)
    if key not in _tear_cache:
        stage = prev.crop(STAGE).convert("RGBA")
        m = Image.new("L", stage.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, stage.width-1, stage.height-1], 20, fill=255)
        stage.putalpha(m)
        A, B, line = tear_split(stage, k, seed)
        shadows = []
        for P in (A, B):
            sh = Image.new("RGBA", P.size, (30, 24, 20, 0)); sh.putalpha(P.getchannel("A").point(lambda v: int(v*.45)))
            shadows.append(sh.resize((P.width//4, P.height//4)).filter(ImageFilter.GaussianBlur(4)).resize(P.size))
        _tear_cache.clear(); _tear_cache[key] = (A, B, shadows, line)
    A, B, shadows, line = _tear_cache[key]
    sx0, sy0 = STAGE[:2]; w, h = A.size
    crack = clamp(u/.28); fly = ease_in_cubic(clamp((u-.22)/.78))
    if kind == "tear_h":
        dA, dB = (0, -1), (0, 1); rA, rB = 4, -3
    elif kind == "tear_v":
        dA, dB = (-1, .08), (1, -.05); rA, rB = 7, -6
    else:
        dA, dB = (-1, -.3), (1, .3); rA, rB = 9, -8
    gap = 6*crack
    for P, S, dd, rr in ((A, shadows[0], dA, rA), (B, shadows[1], dB, rB)):
        dist = gap + fly*1250
        x = sx0 + w/2 + dd[0]*dist; y = sy0 + h/2 + dd[1]*dist + fly*fly*300
        P.info["anchor"] = (w/2, h/2); S.info["anchor"] = (w/2, h/2)
        rot = rr*fly
        if fly > 0: blit(cv, S, x+14+fly*30, y+18+fly*30, 1.0, rot, 1.0)
        blit(cv, P, x, y, 1.0, rot, 1.0)
    if 0 < crack < 1:   # fissure qui court le long de la ligne
        d = ImageDraw.Draw(cv); n = max(2, int(len(line)*crack))
        d.line([(sx0+x, sy0+y) for x, y in line[:n]], fill=(255, 250, 240), width=5)

# ---------------------------------------------------------------- bruitages externes (mp3/wav)
SFX_GAIN = dict(rip=.9, crowd=.55, whistle=.45, cash=.7, flash=.55, stamp=.95, whoosh=.45, kick=.85, boom=.9,
                gavel=.8, plane=.5, groan=.5, heart=1.0, riser=.45, sparkle=.45, crowd_long=.5,
                scratch=.8, glitch=.6, notif=.7, laser=.6, laugh=.6, monitor=.55,
                rewind=.6, bar=.8, horn=.5, gasp=.6, coin=.7, siren=.45, dig=.7, jail=.9, bell=.6, elevator=.8, crash=.8, samba=.6)

def load_sfx_dir(path):
    """Charge un dossier de bruitages : silence de tête coupé, crête normalisée (le 'top' tombe à l'instant voulu)."""
    bank = {}
    if not path or not os.path.isdir(path): return bank
    for fn in sorted(os.listdir(path)):
        name, ext = os.path.splitext(fn)
        if ext.lower() not in (".mp3", ".wav", ".ogg", ".m4a"): continue
        a = load_audio(os.path.join(path, fn)); pk = np.abs(a).max()
        if pk < 1e-4: continue
        idx = np.where(np.abs(a) > pk*0.08)[0]
        a = a[max(0, idx[0]-int(.005*SR)):] if len(idx) else a
        a = a/pk*0.9
        n = min(len(a), int(.01*SR)); a[-n:] *= np.linspace(1, 0, n)
        bank[name] = (a*SFX_GAIN.get(name, .6)).astype(np.float32)
    if "crowd" in bank:     # version longue de la foule : superposition décalée + fondu de sortie
        c = bank["crowd"]; L = int(len(c)*3.2); out = np.zeros(L, np.float32)
        for k, off in enumerate((0, .55, 1.1, 1.65, 2.2)):
            s = int(off*len(c)); seg = c[:L-s]; out[s:s+len(seg)] += seg*(.9 if k == 0 else .6)
        out *= np.concatenate([np.ones(L-int(1.2*SR)), np.linspace(1, 0, int(1.2*SR))])[:L]
        bank["crowd_long"] = (out/np.abs(out).max()*0.9*SFX_GAIN["crowd_long"]).astype(np.float32)
    return bank

# ---------------------------------------------------------------- rendu
def _last_frame(scenes, i, starts, title):
    sc = scenes[i]; f = max(0, int(round(starts[i+1]*FPS))-1)
    cv = background(f, title); sc.draw_fn(cv, f, sc.T-1e-3, sc.T); return cv

def loudnorm(src, dst, lufs=-14.0, tp=-1.5):
    """Normalisation EBU R128 en deux passes (mesure puis correction linéaire)."""
    import json
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", f"loudnorm=I={lufs}:TP={tp}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex("{"):r.rindex("}")+1])
    af = (f"loudnorm=I={lufs}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", af, "-ar", str(SR), dst], check=True)

def _render_range(scenes, starts, title, f0, f1, out_path, preview_dir=None, preview_every=None, crf=25):
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
                           "-pix_fmt", "yuv420p", out_path], stdin=subprocess.PIPE)
    last = {}
    for f in range(f0, f1):
        tg = f/FPS
        i = min(int(np.searchsorted(starts, tg, side="right"))-1, len(scenes)-1)
        sc = scenes[i]; t = tg-starts[i]
        cv = background(f, title)
        sc.draw_fn(cv, f, t, sc.T)
        if sc.trans and i > 0 and t < sc.trans_dur:
            if i-1 not in last: last.clear(); last[i-1] = _last_frame(scenes, i-1, starts, title)
            TRANSITIONS[sc.trans](cv, last[i-1], t, sc.trans_dur, i)
        if getattr(sc, "post", None): sc.post(cv, f, t, sc.T)
        finish(cv, title)
        if preview_every and f % preview_every == 0: cv.save(f"{preview_dir}/prev_{f:05d}.jpg", quality=80)
        ff.stdin.write(cv.tobytes())
        if (f-f0) % 240 == 0: print(f"  [{os.getpid()}] frame {f}/{f1}", flush=True)
    ff.stdin.close(); ff.wait()

def render_episode(scenes, out_dir, slug, title="~/savoir $ ./episode", voice_scale=1.12, preview_every=None,
                   voice_files=None, voice_block=None, sfx_dir=None, workers=None, duck=0.35, voice_gain=1.0,
                   sfx_db=9.0, lufs=-14.0, crf=25, audio_only=False):
    """voice_files : liste de fichiers audio, un par scène (ex. générés via un MCP ElevenLabs / Google TTS).
    voice_block : un seul fichier pour toute la voix off, découpé automatiquement aux silences.
    Sans les deux : voix Piper hors-ligne.
    sfx_dir : dossier de bruitages externes (nom de fichier = nom du bruitage, prioritaire sur les synthétiques).
    duck : baisse des bruitages quand la voix parle (0 = aucune). sfx_db : bruitages sous la voix (dB).
    lufs : volume final (TikTok ≈ -14). crf : qualité x264 (le grain papier coûte cher : 25 = bon compromis)."""
    os.makedirs(out_dir, exist_ok=True)
    tmp = f"/tmp/{slug}"; os.makedirs(tmp, exist_ok=True)
    export_voice_script(scenes, f"{out_dir}/{slug}_voix_off.txt", slug.replace("_", " "))
    # 1) voix + durées
    ext = split_audio_by_silence(voice_block, len(scenes)) if voice_block else None
    for i, sc in enumerate(scenes):
        if voice_files: a = load_audio(voice_files[i])
        elif ext is not None: a = ext[i]
        else: a = tts(sc.voice, f"{tmp}/v{i}.wav", voice_scale) if sc.voice else np.zeros(1, np.float32)
        sc.audio = a
        sc.T = max(sc.min_dur, sc.pad_in + len(a)/SR + sc.pad_out)
        print(f"scene {i+1} {sc.name}: {sc.T:.2f}s")
    total = sum(sc.T for sc in scenes); nfr = int(round(total*FPS))
    print(f"TOTAL {total:.1f}s, {nfr} frames")
    # 2) audio
    bank = sfx_bank(); bank.update(load_sfx_dir(sfx_dir))
    mix = np.zeros(int(total*SR)+2*SR, np.float32); mix_sfx = mix.copy()
    t0 = 0
    for sc in scenes:
        s = int((t0+sc.pad_in)*SR); mix[s:s+len(sc.audio)] += sc.audio*voice_gain
        for ev in sc.sfx:
            tt, name = ev[0], ev[1]; g = ev[2] if len(ev) > 2 else 1.0
            tt = tt(sc.T) if callable(tt) else tt
            if name not in bank: print("  ! bruitage inconnu :", name); continue
            k = max(0, int((t0+tt)*SR)); x = bank[name][:len(mix_sfx)-k]
            if len(ev) > 3:   # durée max (avec fondu de sortie)
                n = min(len(x), int(ev[3]*SR)); x = x[:n].copy(); f = min(n, int(.08*SR)); x[n-f:] *= np.linspace(1, 0, f)
            mix_sfx[k:k+len(x)] += x*g
        t0 += sc.T
    # niveaux : voix ramenée à un niveau fixe, bus bruitages calé `sfx_db` dB sous la voix
    def rms(x): return float(np.sqrt((x.astype(np.float64)**2).mean())) + 1e-9
    act = mix[np.abs(mix) > 0.02]
    mix *= 0.12/(float(np.sqrt((act.astype(np.float64)**2).mean())) if len(act) else 1)
    if np.abs(mix_sfx).max() > 0:
        mix_sfx *= rms(mix)*10**(-sfx_db/20)/rms(mix_sfx)
    if duck > 0:   # ducking : les bruitages s'effacent un peu sous la voix
        hop = int(.02*SR); env = np.array([np.abs(mix[i:i+hop]).max() for i in range(0, len(mix), hop)])
        env = np.convolve(env, np.ones(8)/8, mode="same"); g = 1 - duck*np.clip(env/0.25, 0, 1)
        mix_sfx *= np.repeat(g, hop)[:len(mix_sfx)]
    for arr, nm in ((mix+mix_sfx, "audio_full"), (mix_sfx, "audio_sfx_only")):
        a = arr[:int(total*SR)]
        a = np.where(np.abs(a) > .9, np.sign(a)*(.9 + .1*np.tanh((np.abs(a)-.9)/.1)), a)   # limiteur doux
        with wave.open(f"{tmp}/{nm}_raw.wav", "w") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1)*32767).astype(np.int16).tobytes())
        loudnorm(f"{tmp}/{nm}_raw.wav", f"{tmp}/{nm}.wav", lufs)
    if audio_only: return [f"{tmp}/audio_full.wav", f"{tmp}/audio_sfx_only.wav"]
    # 3) images, en parallèle
    starts = np.cumsum([0]+[sc.T for sc in scenes])
    workers = workers or max(1, (os.cpu_count() or 2))
    bounds = [int(nfr*k/workers) for k in range(workers+1)]
    ctx = multiprocessing.get_context("fork"); procs = []
    for k in range(workers):
        p = ctx.Process(target=_render_range, args=(scenes, starts, title, bounds[k], bounds[k+1], f"{tmp}/chunk_{k}.mp4",
                                                    tmp, preview_every, crf))
        p.start(); procs.append(p)
    for p in procs:
        p.join()
        if p.exitcode != 0: raise RuntimeError("un processus de rendu a échoué")
    with open(f"{tmp}/chunks.txt", "w") as fl:
        for k in range(workers): fl.write(f"file 'chunk_{k}.mp4'\n")
    silent = f"{tmp}/video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/chunks.txt", "-c", "copy", silent], check=True)
    # 4) mux
    for nm, aud in ((f"{slug}.mp4", "audio_full"), (f"{slug}_sans_voix.mp4", "audio_sfx_only")):
        # son stéréo 48 kHz : le format le plus compatible (TikTok, iPhone, Android, lecteurs intégrés)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", f"{tmp}/{aud}.wav", "-map", "0:v:0", "-map", "1:a:0",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "48000", "-shortest",
                        "-movflags", "+faststart", f"{out_dir}/{nm}"], check=True)
    return [f"{out_dir}/{slug}.mp4", f"{out_dir}/{slug}_sans_voix.mp4"]

def scene_timing(scenes, voice_files):
    """Calcule T de chaque scène sans rien rendre (pour les images de contrôle)."""
    for i, sc in enumerate(scenes):
        a = load_audio(voice_files[i]) if voice_files else np.zeros(int(8*SR), np.float32)
        sc.T = max(sc.min_dur, sc.pad_in + len(a)/SR + sc.pad_out)
    return [sc.T for sc in scenes]

def render_still(scene_draw, path, t=1.0, T=5.0, frame=0, title="~/savoir $ ./episode"):
    cv = background(frame, title); scene_draw(cv, frame, t, T); finish(cv, title); cv.save(path); return path

# ---------------------------------------------------------------- alignement mot par mot (sans modèle de reconnaissance)
_VOW = "aeiouyàâäéèêëîïôöùûüœæ"
def _syll(w):
    """Estimation du nombre de syllabes d'un mot français (groupes de voyelles, e muet final ignoré)."""
    w = w.lower().strip(".,;:!?…'’\"«»()-")
    n = len(re.findall(f"[{_VOW}]+", w))
    if len(w) > 2 and w.endswith(("e", "es")) and not w.endswith(("ée", "ées")) and n > 1: n -= 1
    return max(1, n)

def align_words(audio_path, text, min_pause=0.11):
    """Minutage approximatif de chaque mot (±0,15 s) à partir du texte et de l'audio :
    les pauses de la voix sont appariées aux ponctuations (programmation dynamique), puis les mots
    sont répartis entre deux ancres selon leur nombre de syllabes, sur le temps de parole seulement.
    Renvoie [(mot, début, fin)] en secondes dans le fichier."""
    a = load_audio(audio_path); hop = int(SR*0.01)
    env = np.array([np.sqrt((a[i:i+hop]**2).mean()) for i in range(0, len(a), hop)])
    thr = max(1e-4, np.percentile(env, 95)*0.07)
    sp = env > thr
    sp = np.convolve(sp.astype(float), np.ones(5)/5, mode="same") > 0.2          # lissage
    idx = np.where(sp)[0]
    if len(idx) == 0: return []
    t0, t1 = idx[0]*0.01, (idx[-1]+1)*0.01
    pauses = []; i = idx[0]
    while i < idx[-1]:
        if not sp[i]:
            j = i
            while j < len(sp) and not sp[j]: j += 1
            if (j-i)*0.01 >= min_pause: pauses.append((i*0.01, j*0.01))
            i = j
        else: i += 1
    words = []
    for tok in text.replace("…", "… ").split():
        if words and re.fullmatch(r"[.,;:!?…»«\"]+", tok): words[-1] += tok
        else: words.append(tok)
    wts = [_syll(w) + 0.25 for w in words]
    cum = np.concatenate([[0], np.cumsum(wts)]); tot = cum[-1]
    speech_total = (t1-t0) - sum(b-a_ for a_, b in pauses)
    # temps de parole cumulé au début de chaque pause
    sp_before = []; acc = 0; prev = t0
    for (pa, pb) in pauses: acc += pa-prev; sp_before.append(acc); prev = pb
    brk = [k+1 for k, w in enumerate(words[:-1]) if re.search(r"[.,;:!?…]$", w)]
    strong = {k+1 for k, w in enumerate(words[:-1]) if re.search(r"[.;:!?…]$", w)}
    # DP : apparier pauses (dans l'ordre) et coupures du texte (dans l'ordre)
    P, B = len(pauses), len(brk)
    INF = 1e9; D = np.full((P+1, B+1), INF); D[0, :] = 0; D[:, 0] = [0]*(P+1)
    bt = {}
    D[0, 0] = 0
    for p in range(P+1):
        for b in range(B+1):
            if p == 0 and b == 0: continue
            best = INF; arg = None
            if p > 0 and b > 0:
                c = abs(cum[brk[b-1]]/tot - sp_before[p-1]/max(1e-6, speech_total))*10
                if D[p-1, b-1] + c < best: best, arg = D[p-1, b-1] + c, "m"
            if p > 0:   # pause sans ponctuation (respiration)
                dur = pauses[p-1][1]-pauses[p-1][0]
                c = 0.6 + 2.0*max(0, dur-0.25)
                if D[p-1, b] + c < best: best, arg = D[p-1, b] + c, "p"
            if b > 0:   # ponctuation sans pause
                c = 0.5 if brk[b-1] not in strong else 1.2
                if D[p, b-1] + c < best: best, arg = D[p, b-1] + c, "b"
            D[p, b] = best; bt[(p, b)] = arg
    anchors = []; p, b = P, B
    while p > 0 or b > 0:
        m = bt.get((p, b))
        if m == "m": anchors.append((brk[b-1], pauses[p-1])); p -= 1; b -= 1
        elif m == "p": p -= 1
        else: b -= 1
    anchors.reverse()
    # sections entre ancres : (mot_début, mot_fin, t_début, t_fin, pauses internes)
    cuts = [(0, t0)] + [(wi, pb) for wi, (pa, pb) in anchors]
    ends = [pa for wi, (pa, pb) in anchors] + [t1]
    out = []
    for k, (w0, ts) in enumerate(cuts):
        w1 = cuts[k+1][0] if k+1 < len(cuts) else len(words); te = ends[k]
        inner = [(pa, pb) for (pa, pb) in pauses if ts < pa and pb < te]
        seg_speech = (te-ts) - sum(pb-pa for pa, pb in inner)
        def at_speech(x):   # temps de parole -> temps réel (en sautant les pauses internes)
            tcur = ts
            for pa, pb in inner:
                if tcur + x <= pa: return tcur + x
                x -= pa - tcur; tcur = pb
            return tcur + x
        wsum = sum(wts[w0:w1]) or 1; acc = 0
        for wi in range(w0, w1):
            s = at_speech(seg_speech*acc/wsum); acc += wts[wi]; e = at_speech(seg_speech*acc/wsum)
            out.append((words[wi], round(s, 3), round(e, 3)))
    return out

class Words:
    """Accès pratique aux mots d'une scène : W("Ferguson") -> temps de début (dans le fichier voix)."""
    def __init__(self, aligned): self.a = aligned
    def __call__(self, word, n=1, end=False):
        norm = lambda x: re.sub(r"[.,;:!?…'’\"«»]", "", x.lower())
        k = 0; key = norm(word)
        for w, s, e in self.a:
            if norm(w).startswith(key):
                k += 1
                if k == n: return e if end else s
        raise KeyError(word)

# ---------------------------------------------------------------- fonds colorés, glitch, transitions rapides
_panels = {}
def stage_fill(cv, frame, color, key=None):
    """Remplit la scène avec un papier coloré texturé (pour varier les ambiances d'une scène à l'autre)."""
    key = key or str(color)
    if key not in _panels:
        sx0, sy0, sx1, sy1 = STAGE; w, h = sx1-sx0, sy1-sy0; ims = []
        for i in range(3):
            g = _lowfreq(w, h, 300+i+hash(key) % 97, 40); rng = np.random.default_rng(700+i)
            fib = rng.random((h, w)).astype(np.float32)
            st = np.zeros((h, w, 3), np.float32); st[:] = color
            st *= (0.93+0.10*g)[..., None]; st -= ((fib > .985)*14)[..., None]
            yy, xx = np.mgrid[0:h, 0:w]; vx = (xx/w-.5); vy = (yy/h-.5)
            st *= (1-.25*(vx*vx+vy*vy)*2)[..., None]
            ims.append(Image.fromarray(np.clip(st, 0, 255).astype(np.uint8)))
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w-1, h-1], 20, fill=255)
        _panels[key] = (ims, m)
    ims, m = _panels[key]
    cv.paste(ims[boil(frame)], STAGE[:2], m)

def rgb_split(cv, amount=8, frame=0, slices=0):
    """Glitch : décalage des canaux rouge / bleu (+ tranches horizontales décalées)."""
    if amount < 1 and slices == 0: return
    st = cv.crop(STAGE); r, g, b = st.split(); a = int(amount)
    r = ImageChops.offset(r, -a, 0); b = ImageChops.offset(b, a, 0)
    st = Image.merge("RGB", (r, g, b))
    if slices:
        rnd = random.Random(frame//2)
        for _ in range(slices):
            y = rnd.randint(0, st.height-60); hgt = rnd.randint(12, 60); dx = rnd.randint(-40, 40)
            band = st.crop((0, y, st.width, y+hgt)); st.paste(ImageChops.offset(band, dx, 0), (0, y))
    cv.paste(st, STAGE[:2])

def whip_transition(cv, prev, u, direction=-1):
    """Filé rapide : l'ancienne image part sur le côté avec un flou de mouvement, la nouvelle arrive."""
    sx0, sy0, sx1, sy1 = STAGE; w, h = sx1-sx0, sy1-sy0
    e = ease_io(u)
    new = cv.crop(STAGE); old = prev.crop(STAGE)
    def blur(im, k):
        if k < 2: return im
        return im.resize((max(1, w//k), h), Image.BILINEAR).resize((w, h), Image.BILINEAR)
    k = int(2 + 22*math.sin(u*math.pi))
    comp = Image.new("RGB", (w, h))
    comp.paste(blur(old, k), (int(direction*e*w), 0))
    comp.paste(blur(new, k), (int(direction*e*w - direction*w), 0))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w-1, h-1], 20, fill=255)
    cv.paste(comp, (sx0, sy0), m)

def punch_transition(cv, prev, u):
    """Coupe « punch » : flash blanc + zoom qui retombe sur la nouvelle scène."""
    zoom_punch(cv, 1 + 0.14*(1-ease_out_cubic(u)))
    flash(cv, 0.9*(1-u)**2)

_pol_cache = {}
def polaroid_transition(cv, prev, u, target=(250, 470), scale=.36, rot=-8):
    """Arrêt sur image : l'image précédente devient une photo (bord blanc, noir et blanc) qui s'épingle en haut à gauche."""
    key = id(prev)
    if key not in _pol_cache:
        st = prev.crop(STAGE).convert("L").convert("RGB")
        w, h = st.size; b = 28
        card = Image.new("RGBA", (w+2*b, h+2*b+60), (250, 248, 240, 255)); card.paste(st, (b, b))
        card.info["anchor"] = (card.width/2, card.height/2)
        _pol_cache.clear(); _pol_cache[key] = card
    card = _pol_cache[key]; e = ease_out_back(clamp(u), 1.2)
    sx0, sy0, sx1, sy1 = STAGE
    x = lerp((sx0+sx1)/2, target[0], e); y = lerp((sy0+sy1)/2, target[1], e)
    s = lerp(1.0*(sx1-sx0)/card.width, scale, e)
    blit(cv, card, x+10, y+14, s, rot*e, .25)   # ombre grossière
    blit(cv, card, x, y, s, rot*e, 1)

TRANSITIONS = {
    "tear_v": lambda cv, prev, t, d, i: tear_transition(cv, prev, t/d, "tear_v", seed=i),
    "tear_h": lambda cv, prev, t, d, i: tear_transition(cv, prev, t/d, "tear_h", seed=i),
    "tear_d": lambda cv, prev, t, d, i: tear_transition(cv, prev, t/d, "tear_d", seed=i),
    "whip":   lambda cv, prev, t, d, i: whip_transition(cv, prev, t/d, -1 if i % 2 else 1),
    "punch":  lambda cv, prev, t, d, i: punch_transition(cv, prev, t/d),
    "polaroid": lambda cv, prev, t, d, i: polaroid_transition(cv, prev, t/0.55),
}
