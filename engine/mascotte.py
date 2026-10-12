"""Mascotte « Ballon » : un ballon en papier découpé avec un visage (yeux, sourcils, bouche synchronisée sur la voix),
petits bras et baskets. Animée selon Lasseter (rebond avec écrasement, anticipation, dépassement).

  from mascotte import Ballon, envelope
  B = Ballon(); env = envelope("voix.mp3")
  B.draw(cv, fr, x, y, s, t, mood="happy", talk=env(t - pad_in), look=(1, 0), hop_t=None)
    (x, y) = centre du ballon ; s = échelle (s=1 -> ballon de 300 px de diamètre)
  moods : happy, talk, nervous (sueur + yeux qui bougent), wow (grands yeux), smug (paupières mi-closes), sad
"""
import math, subprocess
import numpy as np
from PIL import Image, ImageDraw
from engine import FPS, Paper, ellipse_pts, blit_sxy, layer
import foot
from lasseter import hop, settle, squash

INK = (30, 28, 28); WHITE = (252, 250, 244); RED = (220, 50, 60)

def envelope(path, fps=FPS):
    """Amplitude de la voix par image (0..1), lissée : sert à ouvrir la bouche."""
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", "24000", "-"],
                         capture_output=True).stdout
    a = np.abs(np.frombuffer(raw, np.float32)); n = 24000//fps
    v = np.array([a[i:i+n].mean() for i in range(0, len(a), n)]) if len(a) else np.zeros(1)
    v = np.convolve(v, np.ones(2)/2, "same"); v = np.clip(v/(np.percentile(v, 95) + 1e-6), 0, 1)
    def at(t):
        k = int(t*fps)
        return float(v[k]) if 0 <= k < len(v) else 0.0
    return at

class Ballon:
    R = 150                                    # rayon à s=1
    def __init__(self):
        self.body = Paper(ellipse_pts(300, 300, 48), WHITE, "mascotte_ballon", rough=1.4).add(self._decor)

    @staticmethod
    def _decor(d, a):                         # pentagones du ballon, décalés vers le haut pour laisser la place au visage
        ax, ay = a
        def pent(cx, cy, r, rot=0):
            return [(cx + r*math.cos(rot + k*2*math.pi/5 - math.pi/2), cy + r*math.sin(rot + k*2*math.pi/5 - math.pi/2)) for k in range(5)]
        d.polygon(pent(ax, ay - 112, 34), fill=INK)
        for k, (dx, dy) in enumerate(((-118, -46), (118, -46), (-96, 92), (96, 92))):
            d.polygon(pent(ax + dx, ay + dy, 26, .3*k), fill=INK)

    def draw(self, cv, fr, x, y, s=1.0, t=0.0, mood="happy", talk=0.0, look=(0, 0), hop_t=None, alpha=1.0, wave=False):
        bob = 6*s*math.sin(t*3.2)                                   # respiration (action secondaire)
        dy, sx, sy = hop(t, hop_t, 140*s, .5) if hop_t is not None else (0, 1, 1)
        R = self.R*s; cy = y + bob + dy
        L = layer(int(2*R + 260*s), int(2*R + 220*s), (R + 130*s, R + 60*s)); d = ImageDraw.Draw(L)
        ox, oy = R + 130*s, R + 60*s                                # centre du ballon dans le calque
        lw = max(3, int(8*s))
        # baskets + jambes (derrière)
        for side in (-1, 1):
            fx = ox + side*55*s; fy = oy + R + 40*s
            d.line([(ox + side*40*s, oy + R*.8), (fx, fy - 12*s)], fill=INK, width=lw + int(8*s))
            d.line([(ox + side*40*s, oy + R*.8), (fx, fy - 12*s)], fill=WHITE, width=lw)
            d.rounded_rectangle([fx - 34*s + side*10*s, fy - 18*s, fx + 34*s + side*10*s, fy + 14*s], int(12*s), fill=RED, outline=INK, width=max(2, int(4*s)))
        blit_sxy(L, self.body.v[fr % 3] if isinstance(self.body.v, list) else self.body.v, ox, oy, s, s)
        # bras (pendant la parole : gestes)
        ga = math.sin(t*6)*talk*25
        for side in (-1, 1):
            up = (mood in ("wow", "happy") and hop_t is not None and t > hop_t - .1) or (wave and side == 1)
            ang = math.radians((-55 if up else 35 + ga*side) if side == 1 else (-125 if up else 145 - ga*side))
            if wave and side == 1: ang = math.radians(-60 + 25*math.sin(t*10))
            sx0, sy0 = ox + side*R*.92, oy + 10*s
            ex, ey = sx0 + 110*s*math.cos(ang), sy0 + 110*s*math.sin(ang)
            d.line([(sx0, sy0), (ex, ey)], fill=INK, width=lw + int(8*s))
            d.line([(sx0, sy0), (ex, ey)], fill=WHITE, width=lw)
            d.ellipse([ex - 24*s, ey - 24*s, ex + 24*s, ey + 24*s], fill=WHITE, outline=INK, width=max(2, int(4*s)))
        # visage
        lx, ly = look
        if mood == "nervous": lx = math.sin(t*9)                    # yeux qui bougent
        ew, eh = 34*s, (46 if mood == "wow" else 40)*s
        for side in (-1, 1):
            ex, ey = ox + side*52*s, oy - 10*s
            d.ellipse([ex - ew, ey - eh, ex + ew, ey + eh], fill=WHITE, outline=INK, width=max(2, int(5*s)))
            pr = (15 if mood == "wow" else 13)*s
            px, py = ex + lx*12*s, ey + ly*12*s + 6*s
            d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=INK)
            d.ellipse([px - pr*.35 + 4*s, py - pr*.6, px + pr*.25 + 4*s, py - pr*.05], fill=WHITE)
            if mood == "smug": d.rectangle([ex - ew, ey - eh, ex + ew, ey - 4*s], fill=WHITE); d.line([(ex - ew, ey - 4*s), (ex + ew, ey - 4*s)], fill=INK, width=lw)
            if mood == "blink" or (int(t*10) % 37 == 0): d.rectangle([ex - ew, ey - eh, ex + ew, ey + eh], fill=WHITE); d.line([(ex - ew, ey), (ex + ew, ey)], fill=INK, width=lw)
            # sourcils
            tilt = {"nervous": 10, "sad": 14, "smug": -8, "wow": -4}.get(mood, 0)*side
            byy = ey - eh - 16*s - (10*s if mood == "wow" else 0)
            d.line([(ex - 30*s, byy - tilt*s*.6), (ex + 30*s, byy + tilt*s*.6)], fill=INK, width=max(3, int(9*s)))
        # bouche : ouverture selon l'amplitude de la voix
        mx, my = ox, oy + 62*s; op = max(talk, .9 if mood == "wow" else 0)
        if op > .08:
            mw, mh = (40 + 10*op)*s, (8 + 34*op)*s
            d.ellipse([mx - mw, my - mh, mx + mw, my + mh], fill=(70, 20, 30), outline=INK, width=max(2, int(5*s)))
            d.ellipse([mx - mw*.55, my + mh*.2, mx + mw*.55, my + mh*.95], fill=(230, 90, 100))
        elif mood == "sad":
            d.arc([mx - 40*s, my, mx + 40*s, my + 40*s], 200, 340, fill=INK, width=lw)
        else:
            d.arc([mx - 44*s, my - 30*s, mx + 44*s, my + 22*s], 20, 160, fill=INK, width=lw)
        if mood == "nervous":                                       # goutte de sueur
            gx, gy = ox + R*.75, oy - R*.45 + (t*60 % 40)*s
            d.ellipse([gx - 12*s, gy - 4*s, gx + 12*s, gy + 26*s], fill=(120, 190, 240), outline=INK, width=max(2, int(3*s)))
        d.ellipse([ox - 98*s, oy + 28*s, ox - 62*s, oy + 50*s], fill=(250, 170, 170))   # joues
        d.ellipse([ox + 62*s, oy + 28*s, ox + 98*s, oy + 50*s], fill=(250, 170, 170))
        blit_sxy(cv, L, x, cy, sx, sy, 0, alpha)
