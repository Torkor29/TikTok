"""Moteur « tableau tactique néon » (concepts « Le 3-5-2 expliqué comme à mes joueurs » / « Qu'est-ce qui fait un grand DC ? ») :
terrain vertical aux lignes cyan lumineuses sur fond nuit, joueurs = pastilles numérotées (jaune = nous, rouge = adversaire) qui glissent
d'une position à l'autre, zones qui s'allument, flèches qui se tracent, anneau « patron », étiquettes néon, gros numéros 01-04,
caméra qui zoome sur une zone, sous-titres karaoké (engine/karaoke.py). Coordonnées terrain : x 0 (gauche) → 1 (droite),
y 0 (but adverse, en haut) → 1 (notre but, en bas).
Une vidéo = un objet Tac : on y ajoute des clés (positions, flèches, zones, étiquettes) puis Tac.render(...)."""
import os, math, subprocess
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import karaoke as KA
W, H, FPS = 1080, 1920, 30
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FONTS = os.path.join(ROOT, "assets", "fonts")
BG = (7, 13, 28); LINE = (70, 225, 225); YEL = (255, 204, 60); RED = (240, 64, 92); WHITE = (240, 246, 250); DIM = (30, 60, 80)
PX0, PY0, PX1, PY1 = 110, 330, 970, 1620                         # rectangle du terrain à l'écran (avant caméra)
def P(x, y): return PX0 + (PX1 - PX0)*x, PY0 + (PY1 - PY0)*y
def clamp(u, a=0.0, b=1.0): return max(a, min(b, u))
def ease(u): u = clamp(u); return u*u*(3 - 2*u)
def eob(u, s=1.7): u = clamp(u) - 1; return 1 + (s + 1)*u**3 + s*u**2
_f = {}
def font(size, name="Anton-Regular.ttf"):
    k = (size, name)
    if k not in _f: _f[k] = ImageFont.truetype(os.path.join(FONTS, name), size)
    return _f[k]
def glow_layer(draw_fn, blur=10, k=1.6):
    """Dessin net + halo flou additionné (effet néon)."""
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(L))
    g = L.filter(ImageFilter.GaussianBlur(blur)); a = np.asarray(g).astype(np.float32); a[..., 3] = np.clip(a[..., 3]*k, 0, 255)
    out = Image.fromarray(a.astype(np.uint8)); out.alpha_composite(L); return out
_cache = {}
def pitch_img():
    if "pitch" in _cache: return _cache["pitch"]
    bg = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(bg)
    for x in range(0, W, 54): d.line([(x, 0), (x, H)], fill=(12, 22, 42), width=1)
    for y in range(0, H, 54): d.line([(0, y), (W, y)], fill=(12, 22, 42), width=1)
    for k in range(0, 10, 2):                                     # bandes de tonte très discrètes
        y0 = PY0 + (PY1 - PY0)*k/10; d.rectangle([PX0, y0, PX1, y0 + (PY1 - PY0)/10], fill=(10, 20, 38))
    def lines(d):
        c = LINE + (230,); w = 5
        d.rectangle([PX0, PY0, PX1, PY1], outline=c, width=w); my = (PY0 + PY1)/2; d.line([(PX0, my), (PX1, my)], fill=c, width=w)
        r = (PX1 - PX0)*.13; cx = (PX0 + PX1)/2; d.ellipse([cx - r, my - r, cx + r, my + r], outline=c, width=w); d.ellipse([cx - 7, my - 7, cx + 7, my + 7], fill=c)
        for top in (True, False):
            bw, bh = (PX1 - PX0)*.6, (PY1 - PY0)*.16; sw, sh = (PX1 - PX0)*.28, (PY1 - PY0)*.06
            y0 = PY0 if top else PY1 - bh; d.rectangle([cx - bw/2, y0, cx + bw/2, y0 + bh], outline=c, width=w)
            y1 = PY0 if top else PY1 - sh; d.rectangle([cx - sw/2, y1, cx + sw/2, y1 + sh], outline=c, width=w)
            ay = PY0 + bh if top else PY1 - bh; d.arc([cx - r*.75, ay - r*.75, cx + r*.75, ay + r*.75], 20 if top else 200, 160 if top else 340, fill=c, width=w)
    bg.alpha_composite(glow_layer(lines, 9, 1.4)); _cache["pitch"] = bg; return bg
def hud(cv, title):
    d = ImageDraw.Draw(cv); c = (60, 160, 170)
    for (x, y, sx, sy) in ((40, 190, 1, 1), (W - 40, 190, -1, 1), (40, H - 120, 1, -1), (W - 40, H - 120, -1, -1)):
        d.line([(x, y), (x + 50*sx, y)], fill=c, width=4); d.line([(x, y), (x, y + 50*sy)], fill=c, width=4)
    d.text((70, 214), title, font=font(30, "BebasNeue-Regular.ttf"), fill=(120, 200, 210))
    d.text((W - 70, 214), "● REC SÉQUENCE", font=font(30, "BebasNeue-Regular.ttf"), fill=(230, 80, 100), anchor="ra")
def tag_img(txt, size=46, col=YEL, fill=(10, 18, 34)):
    k = ("tag", txt, size, col)
    if k in _cache: return _cache[k]
    f = font(size); w = int(f.getlength(txt)) + 56; h = size + 34
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([20, 20, 20 + w, 20 + h], fill=fill + (235,), outline=col + (255,), width=4)
    g = im.filter(ImageFilter.GaussianBlur(7)); g.alpha_composite(im); d = ImageDraw.Draw(g)
    d.text((20 + w/2, 20 + h/2 + 2), txt, font=f, fill=col, anchor="mm"); _cache[k] = g; return g
def put(cv, im, x, y, s=1.0, a=1.0):
    if s <= .02 or a <= .02: return
    if abs(s - 1) > .01: im = im.resize((max(1, int(im.width*s)), max(1, int(im.height*s))), Image.BILINEAR)
    if a < .99: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v*a)))
    cv.alpha_composite(im, (int(x - im.width/2), int(y - im.height/2)))
def dot_img(num, col, r=34):
    k = ("dot", num, col, r)
    if k in _cache: return _cache[k]
    s = r*2 + 60; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = s/2
    d.ellipse([c - r, c - r, c + r, c + r], fill=(10, 16, 30, 255), outline=col + (255,), width=6)
    g = im.filter(ImageFilter.GaussianBlur(8)); g.alpha_composite(im); d = ImageDraw.Draw(g)
    if num: d.text((c, c + 2), str(num), font=font(int(r*.95), "BebasNeue-Regular.ttf"), fill=col, anchor="mm")
    _cache[k] = g; return g
class Tac:
    def __init__(self, title, lines, voice=None, slug="tac"):
        self.title, self.slug = title, slug; self.W = KA.Words(lines, voice); self.voice = voice if self.W.real else None
        self.pl = {}                                                # nom -> dict(num, col, keys=[(t, x, y)], t_in, t_out, label)
        self.arrows, self.zones, self.tags, self.rings, self.bigs, self.ball, self.cam, self.sfx, self.extras = [], [], [], [], [], [], [], [], []
        self.T = self.W.end + 2.0
    def t(self, i, w, n=1, end=False): return self.W.t(i, w, n, end)
    # --- construction
    def player(self, name, num, col, x, y, t_in=0.0, t_out=None, label=None):
        self.pl[name] = dict(num=num, col=col, keys=[(t_in, x, y)], t_in=t_in, t_out=t_out, label=label); return self
    def move(self, name, t, x, y, d=.5): self.pl[name]["keys"].append((t, x, y, d)); return self
    def arrow(self, t, p0, p1, col=YEL, d=.35, t_out=None, dash=False, curve=0.0): self.arrows.append((t, p0, p1, col, d, t_out, dash, curve))
    def zone(self, t, rect, col=YEL, t_out=None, label=None): self.zones.append((t, rect, col, t_out, label))
    def tag(self, t, txt, y=300, col=YEL, t_out=None, size=46, x=W/2): self.tags.append((t, txt, x, y, col, t_out, size))
    def ring(self, t, name, t_out=None, col=YEL, label=None): self.rings.append((t, name, t_out, col, label))
    def big(self, t, txt, t_out, col=YEL, sub=None): self.bigs.append((t, txt, t_out, col, sub))
    def camera(self, t, cx, cy, z, d=.6): self.cam.append((t, cx, cy, z, d))
    def sound(self, t, name, g=.35): self.sfx.append((t, name, g))
    # --- état
    def pos(self, p, t):
        keys = p["keys"]; x, y = keys[0][1], keys[0][2]
        for k in keys[1:]:
            tk, kx, ky, d = k
            if t <= tk: break
            u = ease((t - tk)/d); x, y = x + (kx - x)*u, y + (ky - y)*u
        return x, y
    def cam_at(self, t):
        cx, cy, z = W/2, H/2, 1.0
        for (tk, kx, ky, kz, d) in self.cam:
            if t <= tk: break
            u = ease((t - tk)/d); cx, cy, z = cx + (kx - cx)*u, cy + (ky - cy)*u, z + (kz - z)*u
        return cx, cy, z
    # --- dessin
    def draw_field(self, L, t, fr):
        L.alpha_composite(pitch_img())
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for (t0, (x0, y0, x1, y1), col, t1, lab) in self.zones:
            if t < t0 or (t1 and t > t1 + .25): continue
            a = clamp((t - t0)/.25)*(1 - (clamp((t - t1)/.25) if t1 and t > t1 else 0)); p0, p1 = P(x0, y0), P(x1, y1)
            pul = .75 + .25*math.sin(t*5)
            d.rectangle([p0[0], p0[1], p1[0], p1[1]], fill=col + (int(70*a*pul),), outline=col + (int(220*a),), width=4)
        L.alpha_composite(ov)
        for (t0, (x0, y0, x1, y1), col, t1, lab) in self.zones:
            if lab and t >= t0 and not (t1 and t > t1): p1 = P((x0 + x1)/2, y1); put(L, tag_img(lab, 30, col), p1[0], p1[1] - 34, eob((t - t0)/.3))
        for a_ in self.arrows: self._arrow(L, t, *a_)
        for (t0, name, t1, col, lab) in self.rings:
            if t < t0 or (t1 and t > t1): continue
            x, y = P(*self.pos(self.pl[name], t)); d = ImageDraw.Draw(L)
            for k in range(3):
                u = ((t - t0)*1.2 + k/3) % 1; r = 40 + 70*u; d.ellipse([x - r, y - r, x + r, y + r], outline=col + (int(200*(1 - u)),), width=5)
            if lab: put(L, tag_img(lab, 28, col), x, y - 92, eob((t - t0)/.3))
        for name, p in self.pl.items():
            if t < p["t_in"] or (p["t_out"] and t > p["t_out"] + .2): continue
            s = eob((t - p["t_in"])/.35)*(1 - (clamp((t - p["t_out"])/.2) if p["t_out"] and t > p["t_out"] else 0))
            x, y = P(*self.pos(p, t)); put(L, dot_img(p["num"], p["col"]), x, y, s)
            if p["label"] and t > p["t_in"] + .2: put(L, tag_img(p["label"], 26, p["col"]), x, y + 62, eob((t - p["t_in"] - .2)/.3))
        if self.ball:
            bx, by = self._ball(t)
            if bx is not None:
                x, y = P(bx, by); d = ImageDraw.Draw(L); d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=WHITE, outline=(20, 20, 20), width=3)
    def _ball(self, t):
        if t < self.ball[0][0]: return None, None
        x, y = self.ball[0][1], self.ball[0][2]
        for (tk, kx, ky, d) in self.ball[1:]:
            if t <= tk: break
            u = ease((t - tk)/d); x, y = x + (kx - x)*u, y + (ky - y)*u
        return x, y
    def _arrow(self, L, t, t0, p0, p1, col, d, t1, dash, curve):
        if t < t0 or (t1 and t > t1 + .2): return
        u = ease((t - t0)/d); a = 1 - (clamp((t - t1)/.2) if t1 and t > t1 else 0)
        (x0, y0), (x1, y1) = P(*p0), P(*p1); mx, my = (x0 + x1)/2 - curve*(y1 - y0), (y0 + y1)/2 + curve*(x1 - x0)
        pts = [((1 - s)**2*x0 + 2*(1 - s)*s*mx + s*s*x1, (1 - s)**2*y0 + 2*(1 - s)*s*my + s*s*y1) for s in np.linspace(0, u, 24)]
        def dr(dd):
            c = col + (int(255*a),)
            if dash:
                for k in range(0, len(pts) - 1, 2): dd.line([pts[k], pts[k + 1]], fill=c, width=8)
            else: dd.line(pts, fill=c, width=8, joint="curve")
            if u > .95 and len(pts) > 2:
                (ax, ay), (bx, by) = pts[-3], pts[-1]; ang = math.atan2(by - ay, bx - ax); s = 30
                dd.polygon([(bx + s*math.cos(ang), by + s*math.sin(ang)), (bx + s*.8*math.cos(ang + 2.4), by + s*.8*math.sin(ang + 2.4)), (bx + s*.8*math.cos(ang - 2.4), by + s*.8*math.sin(ang - 2.4))], fill=c)
        L.alpha_composite(glow_layer(dr, 7, 1.3))
    def frame(self, fr):
        t = fr/FPS; L = Image.new("RGBA", (W, H), BG + (255,)); self.draw_field(L, t, fr)
        cx, cy, z = self.cam_at(t)
        if abs(z - 1) > .005 or abs(cx - W/2) > 1 or abs(cy - H/2) > 1:
            bw, bh = W/z, H/z; x0 = min(max(cx - bw/2, 0), W - bw); y0 = min(max(cy - bh/2, 0), H - bh)
            L = L.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.BICUBIC)
        for e in self.extras: e(L, t, fr)
        hud(L, self.title)
        for (t0, txt, x, y, col, t1, size) in self.tags:
            if t < t0 or (t1 and t > t1 + .2): continue
            a = 1 - (clamp((t - t1)/.2) if t1 and t > t1 else 0); put(L, tag_img(txt, size, col), x, y + (1 - ease((t - t0)/.25))*-30, eob((t - t0)/.3), a)
        for (t0, txt, t1, col, sub) in self.bigs:                   # gros numéro / titre plein écran
            if t < t0 or t > t1 + .2: continue
            a = 1 - clamp((t - t1)/.2) if t > t1 else 1; d = ImageDraw.Draw(L)
            base = min(200, int(200*940/max(1, font(200).getlength(txt)))); s = eob((t - t0)/.35); f = font(int(base*s) if s > .05 else 10)
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov); od.rectangle([0, 790, W, 1140], fill=(20, 36, 82, int(225*a)))
            L.alpha_composite(ov)
            g = glow_layer(lambda dd: dd.text((W/2, 930), txt, font=f, fill=col + (int(255*a),), anchor="mm"), 14, 1.5); L.alpha_composite(g)
            if sub: put(L, tag_img(sub, 48, WHITE), W/2, 1080, eob((t - t0 - .15)/.3), a)
        KA.caption(L, self.W, t, 1745, 88)
        return np.asarray(L.convert("RGB")).tobytes()
    # --- son + rendu
    def build_audio(self, wav):
        A = os.path.join(ROOT, "assets", "sfx"); evs = []
        if self.voice: evs.append((self.voice, 0.0, 1.0))
        for (t, n, g) in self.sfx: evs.append((os.path.join(A, n + ".mp3"), t, g*.6))
        ins = ["-f", "lavfi", "-t", f"{self.T:.2f}", "-i", "anullsrc=r=48000:cl=stereo"] + sum([["-i", p] for p, _, _ in evs], []); fc = ""
        for i, (_, ts, g) in enumerate(evs): fc += f"[{i + 1}:a]aresample=48000,adelay={int(ts*1000)}|{int(ts*1000)},volume={g}[e{i}];"
        fc += "[0:a]" + "".join(f"[e{i}]" for i in range(len(evs))) + f"amix=inputs={1 + len(evs)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.89[a]"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-filter_complex", fc, "-map", "[a]", "-ar", "48000", wav], check=True)
    def render(self, out_dir):
        os.makedirs(out_dir, exist_ok=True); v, a = out_dir + "/_v.mp4", out_dir + "/_a.wav"; self.build_audio(a)
        pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", v], stdin=subprocess.PIPE)
        global _CUR; _CUR = self
        with Pool(os.cpu_count()) as pool:
            for b in pool.imap(_frame, range(int(self.T*FPS)), chunksize=8): pr.stdin.write(b)
        pr.stdin.close(); pr.wait(); out = f"{out_dir}/{self.slug}{'' if self.voice else '_provisoire'}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
        os.remove(v); os.remove(a); return out
    def stills(self, path, n=24):
        ts = [0.0] + [self.T*(k + .5)/n for k in range(n - 1)]; sh = Image.new("RGB", (180*12, 320*((len(ts) + 11)//12)))
        for k, t in enumerate(ts): sh.paste(Image.frombytes("RGB", (W, H), self.frame(int(t*FPS))).resize((180, 320)), ((k % 12)*180, (k//12)*320))
        sh.save(path, quality=85); return path
_CUR = None
def _frame(fr): return _CUR.frame(fr)

# ================================================================== THÈME « PAPIER » (notre DA, demande utilisateur 03/11)
# Terrain en papier vert déchiré + lignes à la craie (stop-motion), pastilles en papier découpé, flèches au feutre, étiquettes en bandes
# de papier (typo d'édit), gros numéros en tampon, fond kraft. Les couleurs « néon » des épisodes sont traduites ici (pcol).
import random, sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as _E
KRAFT = (236, 226, 204); GRASS = (66, 134, 80); GRASS2 = (74, 146, 88); CHALK = (248, 246, 236); NAVY_ = (20, 36, 82); RED_ = (206, 36, 44)
MUST = (250, 202, 60); INK_ = (24, 22, 28)
def pcol(c):
    return {YEL: MUST, RED: RED_, LINE: CHALK, WHITE: CHALK}.get(tuple(c), tuple(c))
_pc = {}
def p_pitch(fr):
    b = (fr//3) % 3; k = ("ppitch", b)
    if k in _pc: return _pc[k]
    rng = np.random.default_rng(1); a = np.zeros((H, W, 3), np.float32); a[:] = KRAFT
    a *= (.95 + .08*_E._lowfreq(W, H, 3, 60))[..., None]; sp = rng.random((H, W)); a += ((sp > .985)*-22 + (sp < .01)*14)[..., None]
    bg = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    pw, ph = PX1 - PX0, PY1 - PY0
    def stripes(d, ox, oy):
        for j in range(0, 10, 2): d.rectangle([ox - pw/2, oy - ph/2 + ph*j/10, ox + pw/2, oy - ph/2 + ph*(j + 1)/10], fill=GRASS2)
    spr = _E.paper_sprite(_E.rect_pts(pw + 60, ph + 60), GRASS, seed=11 + b, rough=4, pattern=stripes)
    ax, ay = spr.info["anchor"]; bg.alpha_composite(spr, (int((PX0 + PX1)/2 - ax), int((PY0 + PY1)/2 - ay)))
    d = ImageDraw.Draw(bg); rnd = random.Random(b)
    def chalk(pts, w=6):
        q = [(x + rnd.uniform(-1.5, 1.5), y + rnd.uniform(-1.5, 1.5)) for x, y in pts]; d.line(q, fill=CHALK, width=w, joint="curve")
    def seg(x0, y0, x1, y1): chalk([(x0 + (x1 - x0)*u, y0 + (y1 - y0)*u) for u in np.linspace(0, 1, 12)])
    def rect(x0, y0, x1, y1): seg(x0, y0, x1, y0); seg(x1, y0, x1, y1); seg(x1, y1, x0, y1); seg(x0, y1, x0, y0)
    rect(PX0, PY0, PX1, PY1); my = (PY0 + PY1)/2; seg(PX0, my, PX1, my); cx = (PX0 + PX1)/2; r = pw*.13
    chalk([(cx + r*math.cos(u), my + r*math.sin(u)) for u in np.linspace(0, 2*math.pi, 40)]); d.ellipse([cx - 7, my - 7, cx + 7, my + 7], fill=CHALK)
    for top in (True, False):
        bw, bh, sw, sh = pw*.6, ph*.16, pw*.28, ph*.06
        y0 = PY0 if top else PY1 - bh; rect(cx - bw/2, y0, cx + bw/2, y0 + bh); y1 = PY0 if top else PY1 - sh; rect(cx - sw/2, y1, cx + sw/2, y1 + sh)
        ay_ = PY0 + bh if top else PY1 - bh; a0, a1 = (.35, 2.8) if top else (3.5, 5.95)
        chalk([(cx + r*.75*math.cos(u), ay_ + r*.75*math.sin(u)) for u in np.linspace(a0, a1, 16)])
    _pc[k] = bg; return bg
def p_dot(num, col, r=34):
    k = ("pdot", num, col)
    if k in _pc: return _pc[k]
    ours = tuple(col) == YEL; fill = NAVY_ if ours else (RED_ if tuple(col) == RED else pcol(col))
    spr = _E.paper_sprite(_E.ellipse_pts(2*r + 8, 2*r + 8, 30), fill, seed=(num or 0) + (7 if ours else 3), rough=1.4)
    ax, ay = spr.info["anchor"]; d = ImageDraw.Draw(spr)
    if ours: d.ellipse([ax - r + 6, ay - r + 6, ax + r - 6, ay + r - 6], outline=RED_, width=5)
    if num: d.text((ax, ay + 2), str(num), font=font(int(r*.95), "BebasNeue-Regular.ttf"), fill=(250, 248, 240), anchor="mm")
    out = Image.new("RGBA", (spr.width + 20, spr.height + 20), (0, 0, 0, 0)); out.alpha_composite(spr, (int(out.width/2 - ax), int(out.height/2 - ay)))
    _pc[k] = out; return out
def p_tag(txt, size=46, col=YEL, fill=None):
    k = ("ptag", txt, size, col)
    if k in _pc: return _pc[k]
    c = pcol(col); fg = INK_ if c in (MUST, CHALK) else (250, 248, 240)
    lab = _E.Label(txt, f"tq{txt}{size}{c}", font(size), fg, c, padx=22, pady=6, rough=2.5).v[0]
    out = Image.new("RGBA", (lab.width + 20, lab.height + 20), (0, 0, 0, 0)); ax, ay = lab.info["anchor"]; out.alpha_composite(lab, (int(out.width/2 - ax), int(out.height/2 - ay)))
    _pc[k] = out; return out
def p_layer(draw_fn, blur=0, k=0):
    """Trait au feutre : pas de halo, juste le dessin (les couleurs néon sont traduites)."""
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); draw_fn(_PD(ImageDraw.Draw(L))); return L
class _PD:
    """ImageDraw qui traduit les couleurs néon -> palette papier."""
    def __init__(self, d): self.d = d
    def _c(self, kw):
        for key in ("fill", "outline"):
            v = kw.get(key)
            if isinstance(v, tuple) and len(v) in (3, 4): kw[key] = pcol(v[:3]) + tuple(v[3:])
        return kw
    def __getattr__(self, n):
        f = getattr(self.d, n)
        return lambda *a, **kw: f(*a, **self._c(kw))
def p_hud(cv, title):
    _E.Label("TACTIQUE", "tqhud0", font(40, "BebasNeue-Regular.ttf"), (250, 248, 240), INK_, padx=16, pady=4, rough=2).draw(cv, 0, 150, 215, 1, -3)
    _E.Label(title.split("·")[-1].strip(), "tqhud1", font(40), (250, 248, 240), RED_, padx=16, pady=4, rough=2).draw(cv, 0, 470, 215, 1, 2)
def use_paper():
    g = globals(); g["pitch_img"] = lambda: p_pitch(_FR[0]); g["dot_img"] = p_dot; g["tag_img"] = p_tag; g["glow_layer"] = p_layer; g["hud"] = p_hud
    g["BG"] = KRAFT
_FR = [0]
_frame_neon = Tac.frame
def _frame_paper(self, fr):
    _FR[0] = fr
    if not getattr(self, "_paper_zones", False):                   # zones : teintes papier
        self.zones = [(t0, r, pcol(c), t1, lab) for (t0, r, c, t1, lab) in self.zones]
        self.rings = [(t0, n, t1, pcol(c), lab) for (t0, n, t1, c, lab) in self.rings]
        self.bigs = [(t0, txt, t1, MUST if tuple(c) == YEL else pcol(c), sub) for (t0, txt, t1, c, sub) in self.bigs]; self._paper_zones = True
    return _frame_neon(self, fr)
Tac.frame = _frame_paper
use_paper()
