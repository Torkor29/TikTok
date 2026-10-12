"""Mascotte « Ballon » v2 : ballon au visage expressif « humain » (style cartoon), dessiné en 2x puis réduit.
Paupières (regard détendu / blasé), sourcils épais, bouche à formes multiples synchronisée sur la voix, ombrage 3D,
gants à 4 doigts, baskets, inclinaison de tête. Animation Lasseter : respiration, rebond avec écrasement, clignements.

  from mascotte import Ballon, envelope
  B = Ballon(); env = envelope("voix.mp3")
  B.draw(cv, fr, x, y, s, t, mood="neutre", talk=env(t - pad_in), look=(1, 0), hop_t=None, wave=False)
    (x, y) = centre du ballon ; s = échelle (s=1 -> 300 px de diamètre)
  moods : neutre, blase, malin (sourire en coin, sourcil levé), rire (yeux plissés), stress, choc, triste, fier
"""
import math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import FPS, blit_sxy
from lasseter import hop

INK = (34, 30, 30); WHITE = (250, 247, 238); RED = (214, 46, 58)
SKIN_LID = (236, 232, 222); MOUTH = (92, 26, 36); TONGUE = (226, 96, 104); CHEEK = (244, 160, 150)

def envelope(path, fps=FPS):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", "24000", "-"],
                         capture_output=True).stdout
    a = np.abs(np.frombuffer(raw, np.float32)); n = 24000//fps
    v = np.array([a[i:i+n].mean() for i in range(0, len(a), n)]) if len(a) else np.zeros(1)
    v = np.convolve(v, np.ones(2)/2, "same"); v = np.clip(v/(np.percentile(v, 95) + 1e-6), 0, 1)
    def at(t):
        k = int(t*fps)
        return float(v[k]) if 0 <= k < len(v) else 0.0
    return at

def _pent(cx, cy, r, rot=0.0):
    return [(cx + r*math.cos(rot + k*2*math.pi/5 - math.pi/2), cy + r*math.sin(rot + k*2*math.pi/5 - math.pi/2)) for k in range(5)]

class Ballon:
    R = 150
    SS = 2

    def __init__(self):
        self._body = {}

    def _body_img(self, s):
        key = round(s, 2)
        if key in self._body: return self._body[key]
        k = s*self.SS; R = int(self.R*k); W = 2*R + 8
        im = Image.new("RGBA", (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = W/2
        d.ellipse([c - R, c - R, c + R, c + R], fill=WHITE)
        for (dx, dy, r, rot) in ((0, -.78, .23, 0), (-.82, -.28, .18, .3), (.82, -.28, .18, -.3), (-.62, .7, .17, .5), (.62, .7, .17, -.5)):
            d.polygon(_pent(c + dx*R, c + dy*R, r*R, rot), fill=(52, 48, 50))
        yy, xx = np.mgrid[0:W, 0:W]; nx, ny = (xx - c)/R, (yy - c)/R
        shade = np.clip((nx*.45 + ny*.75 + .25), 0, 1)**1.6*110
        hl = np.clip(1 - ((nx + .38)**2 + (ny + .45)**2)/.09, 0, 1)*60
        a = np.array(im).astype(np.float32); m = a[..., 3] > 0
        for ch in range(3): a[..., ch] = np.where(m, np.clip(a[..., ch] - shade + hl, 0, 255), a[..., ch])
        im = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(im)
        d.ellipse([c - R, c - R, c + R, c + R], outline=INK, width=int(6*k))
        self._body[key] = im; return im

    def draw(self, cv, fr, x, y, s=1.0, t=0.0, mood="neutre", talk=0.0, look=(0, 0), hop_t=None, alpha=1.0, wave=False, tilt=None):
        S = self.SS; k = s*S; R = self.R*k
        bob = 5*s*math.sin(t*2.6)
        dy, sx, sy = hop(t, hop_t, 120*s, .5) if hop_t is not None else (0, 1, 1)
        W, H = int(2*R + 300*k), int(2*R + 260*k)
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        ox, oy = W/2, R + 70*k
        lw = max(2, int(7*k))
        def limb(p0, p1, w):
            d.line([p0, p1], fill=INK, width=int(w + 9*k)); d.line([p0, p1], fill=WHITE, width=int(w))
        for side in (-1, 1):
            hx, hy = ox + side*48*k, oy + R*.86; fx, fy = ox + side*60*k, oy + R + 46*k
            limb((hx, hy), (fx, fy - 10*k), 12*k)
            d.rounded_rectangle([fx - 36*k + side*12*k, fy - 18*k, fx + 36*k + side*12*k, fy + 16*k], int(14*k), fill=RED, outline=INK, width=lw)
            d.rectangle([fx - 32*k + side*12*k, fy + 5*k, fx + 32*k + side*12*k, fy + 12*k], fill=WHITE)
        B = self._body_img(s); L.alpha_composite(B, (int(ox - B.width/2), int(oy - B.height/2)))
        gest = math.sin(t*5.5)*min(1, talk*1.5)
        for side in (-1, 1):
            up = (hop_t is not None and hop_t - .1 < t < hop_t + 1.2 and mood in ("choc", "rire", "fier"))
            if wave and side == 1: ang = -65 + 22*math.sin(t*9)
            elif up: ang = -60 if side == 1 else -120
            elif mood == "blase": ang = 75 if side == 1 else 105
            elif mood == "fier": ang = 125 if side == 1 else 55
            else: ang = (30 + 18*gest) if side == 1 else (150 - 18*gest)
            a = math.radians(ang); sx0, sy0 = ox + side*R*.93, oy + 18*k
            ln = 70*k if mood == "fier" else 105*k
            ex, ey = sx0 + ln*math.cos(a), sy0 + ln*math.sin(a)
            limb((sx0, sy0), (ex, ey), 12*k)
            g = 26*k
            for f in (-1, 0, 1):
                fa = a + f*.5; fx, fy = ex + g*.95*math.cos(fa), ey + g*.95*math.sin(fa)
                d.ellipse([fx - g*.42, fy - g*.42, fx + g*.42, fy + g*.42], fill=WHITE, outline=INK, width=max(2, int(4*k)))
            d.ellipse([ex - g, ey - g, ex + g, ey + g], fill=WHITE, outline=INK, width=lw)
        # visage
        lx, ly = look
        if mood == "stress": lx = .8*math.sin(t*7)
        blink = (t % 3.7) < .12 and mood != "rire"
        lid = {"neutre": .3, "blase": .55, "malin": .4, "stress": .08, "choc": 0, "triste": .35, "fier": .45, "rire": 0}.get(mood, .3)
        ew, eh = 30*k, (44 if mood == "choc" else 38)*k
        for side in (-1, 1):
            ex, ey = ox + side*56*k, oy - 6*k
            if mood == "rire" or blink:
                if mood == "rire": d.arc([ex - ew, ey - eh*.3, ex + ew, ey + eh*1.1], 200, 340, fill=INK, width=int(9*k))
                else: d.line([(ex - ew, ey + 6*k), (ex + ew, ey + 6*k)], fill=INK, width=int(8*k))
            else:
                d.ellipse([ex - ew, ey - eh, ex + ew, ey + eh], fill=(255, 255, 255))
                pr = (19 if mood != "choc" else 14)*k
                px = ex + lx*9*k; py = ey + ly*9*k + (9*k if mood in ("blase", "triste") else 4*k)
                d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(80, 52, 36))
                d.ellipse([px - pr*.55, py - pr*.55, px + pr*.55, py + pr*.55], fill=INK)
                d.ellipse([px - pr*.65 + 3*k, py - pr*.75, px - pr*.1 + 3*k, py - pr*.2], fill=(255, 255, 255))
                ll = lid*(1.2 if (mood == "malin" and side == -1) else 1)
                if ll > 0:
                    cut = ey - eh + 2*eh*ll
                    mask = Image.new("L", L.size, 0); ImageDraw.Draw(mask).ellipse([ex - ew, ey - eh, ex + ew, ey + eh], fill=255)
                    lidim = Image.new("RGBA", L.size, (0, 0, 0, 0)); ImageDraw.Draw(lidim).rectangle([ex - ew - 4, ey - eh - 4, ex + ew + 4, cut], fill=SKIN_LID + (255,))
                    L.paste(lidim, (0, 0), Image.composite(lidim.split()[3], Image.new("L", L.size, 0), mask))
                    d.line([(ex - ew*.98, cut), (ex + ew*.98, cut)], fill=INK, width=int(7*k))
                d.ellipse([ex - ew, ey - eh, ex + ew, ey + eh], outline=INK, width=lw)
            bt = {"stress": 14, "triste": 16, "choc": -2, "blase": -3, "fier": -8, "rire": -4}.get(mood, 0)
            lift = {"choc": 22, "stress": 10}.get(mood, 0)*k
            if mood == "malin": bt, lift = ((-12, 20*k) if side == 1 else (5, -4*k))
            if mood == "blase": lift = -4*k
            by = ey - eh - 18*k - lift
            inner, outer = (ex - side*32*k), (ex + side*32*k)
            d.line([(inner, by + bt*k*.6), (outer, by - bt*k*.6)], fill=INK, width=int(12*k))
        ch = Image.new("RGBA", L.size, (0, 0, 0, 0)); cd = ImageDraw.Draw(ch)
        for side in (-1, 1):
            cxk = ox + side*88*k; cyk = oy + 40*k
            cd.ellipse([cxk - 24*k, cyk - 12*k, cxk + 24*k, cyk + 12*k], fill=CHEEK + (140,))
        L.alpha_composite(ch.filter(ImageFilter.GaussianBlur(4*k))); d = ImageDraw.Draw(L)
        mx, my = ox, oy + 66*k; op = talk if talk > .08 else 0
        if mood == "choc": op = max(op, .85)
        if op > 0:
            mw, mh = (32 + 12*op)*k, (6 + 30*op)*k
            sk = 10*k if mood == "malin" else 0
            d.chord([mx - mw + sk, my - mh*.5, mx + mw + sk, my + mh*1.5], 0, 180, fill=MOUTH, outline=INK, width=lw)
            d.rectangle([mx - mw*.68 + sk, my + mh*.5 + 2, mx + mw*.68 + sk, my + mh*.5 + 8*k], fill=(255, 255, 255))
            if op > .35: d.ellipse([mx - mw*.45 + sk, my + mh*.8, mx + mw*.45 + sk, my + mh*1.4], fill=TONGUE)
        elif mood == "blase":
            d.line([(mx - 30*k, my + 10*k), (mx + 26*k, my + 5*k)], fill=INK, width=int(8*k))
        elif mood == "malin":
            d.line([(mx - 30*k, my + 12*k), (mx + 6*k, my + 12*k)], fill=INK, width=int(8*k))
            d.arc([mx - 14*k, my - 22*k, mx + 40*k, my + 14*k], 20, 110, fill=INK, width=int(8*k))
        elif mood == "triste":
            d.arc([mx - 30*k, my + 8*k, mx + 30*k, my + 40*k], 205, 335, fill=INK, width=int(8*k))
        elif mood == "stress":
            pts = [(mx - 34*k + i*11*k, my + 10*k + (6*k if i % 2 else -2*k)) for i in range(7)]
            d.line(pts, fill=INK, width=int(7*k), joint="curve")
        elif mood in ("rire", "fier"):
            d.chord([mx - 40*k, my - 10*k, mx + 40*k, my + 42*k], 0, 180, fill=MOUTH, outline=INK, width=lw)
            d.rectangle([mx - 28*k, my + 16*k, mx + 28*k, my + 23*k], fill=(255, 255, 255))
        else:
            d.arc([mx - 32*k, my - 20*k, mx + 32*k, my + 20*k], 25, 155, fill=INK, width=int(8*k))
        if mood == "stress":
            gx, gy = ox + R*.78, oy - R*.42 + (t*50 % 36)*k
            d.ellipse([gx - 11*k, gy - 2*k, gx + 11*k, gy + 26*k], fill=(140, 200, 245), outline=INK, width=max(2, int(4*k)))
        out = L.resize((W//S, H//S), Image.LANCZOS)
        out.info["anchor"] = (ox/S, oy/S)
        rot = tilt if tilt is not None else {"blase": -6, "malin": 5, "triste": -4}.get(mood, 0) + 2*math.sin(t*1.3)
        blit_sxy(cv, out, x, y + bob + dy, sx, sy, rot, alpha)
