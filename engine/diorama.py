"""Format « caméra dans la maquette » (introduit sur ol_histoire v2) rendu réutilisable :
  * cam()      : la caméra parcourt une image IA 16:9 de maquette papier, plein écran, de pose en pose
                 (slow in / slow out, principes de Lasseter) ; options gris / sépia ;
  * cut_punch(): à chaque coupe la caméra arrive un poil trop près puis se pose (follow-through) ;
  * Frise      : frise chronologique fixe en haut de l'écran, le pion du club saute d'une date à l'autre
                 (anticipation, arc, écrasement) ;
  * K(), note(): étiquettes papier (titre / écriture main).
Usage : from diorama import Diorama, Frise, K, note ; D = Diorama(dossier_images) ; D.cam(cv, "cle", t, poses).
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine
from engine import W, H, CX, PAL, Label, Paper, font, clamp, lerp, rect_pts, blit_sxy
from lasseter import ease, settle, arc, keys, squash

class Diorama:
    def __init__(self, img_dir):
        self.dir = img_dir; self._base = {}; self._vig = None

    def img(self, key):
        if key not in self._base:
            im = Image.open(os.path.join(self.dir, f"{key}.png")).convert("RGB")
            bw = int(im.width*H/im.height)
            self._base[key] = im.resize((bw, H), Image.BICUBIC).filter(ImageFilter.UnsharpMask(2.2, 70, 2))
        return self._base[key]

    def vignette(self):
        if self._vig is None:
            yy, xx = np.mgrid[0:H, 0:W]; r = ((xx/W - .5)**2*1.6 + (yy/H - .5)**2)
            v = np.zeros((H, W, 4), np.uint8); v[..., 3] = np.clip((r - .12)*340, 0, 150).astype(np.uint8)
            self._vig = Image.fromarray(v, "RGBA")
        return self._vig

    def cam(self, cv, key, t, ks, gray=0.0, sep=0.0):
        """ks = [(t, (cx, cy, zoom)), …] : centre en fraction de l'image, zoom >= 1 (1 = hauteur pleine)."""
        im = self.img(key); cx, cy, z = keys(t, ks); cw, ch = W/z, H/z
        x0 = clamp(cx*im.width - cw/2, 0, im.width - cw); y0 = clamp(cy*im.height - ch/2, 0, im.height - ch)
        fr = im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        if gray > 0: fr = Image.blend(fr, fr.convert("L").convert("RGB"), clamp(gray))
        if sep > 0:
            g = fr.convert("L")
            s = Image.merge("RGB", (g.point(lambda v: min(255, int(v*1.08 + 18))), g.point(lambda v: int(v*.95 + 8)), g.point(lambda v: int(v*.78))))
            fr = Image.blend(fr, s, clamp(sep))
        cv.paste(fr, (0, 0))
        if cv.mode == "RGBA": cv.alpha_composite(self.vignette())
        else: cv.paste(self.vignette(), (0, 0), self.vignette())

def cut_punch(cv, t, t0, z=.06):
    if t >= t0: engine.zoom_punch(cv, 1 + abs(settle(t, t0, z, 2.2, 6)))

class Frise:
    """Frise y_min → y_max en haut d'écran ; pion = disque `col` avec `txt` ; drapeau d'année au-dessus."""
    def __init__(self, y_min, y_max, ticks, txt="OL", col=(206, 30, 46), bar=None, fg=(250, 250, 246), y=236):
        self.a, self.b, self.ticks, self.txt, self.col, self.bar, self.fg, self.y = y_min, y_max, ticks, txt, col, bar or col, fg, y
        self.x0, self.x1 = 110, W - 110
        self.rib = Paper(rect_pts(self.x1 - self.x0 + 70, 30), PAL["cream"], f"rib{txt}", rough=2.0)
        r = 30; k = Image.new("RGBA", (2*r + 8, 2*r + 8), (0, 0, 0, 0)); kd = ImageDraw.Draw(k)
        kd.ellipse([4, 4, 2*r + 4, 2*r + 4], fill=col, outline=fg, width=5)
        kd.text((r + 4, r + 4), txt, font=font("title", 26 if len(txt) > 2 else 30), fill=fg, anchor="mm")
        k.info["anchor"] = (r + 4, 2*r + 8); self.knob = k

    def x(self, yr): return self.x0 + (self.x1 - self.x0)*(yr - self.a)/(self.b - self.a)

    def draw(self, cv, fr, t, y0, y1, t0, d=.55, lab=None):
        FY = self.y; self.rib.draw(cv, fr, CX, FY, 1, 0)
        dd = ImageDraw.Draw(cv); f = font("mono", 26); ink = PAL["ink"]
        for yr in self.ticks:
            x = self.x(yr); dd.line([x, FY - 12, x, FY + 12], fill=ink, width=4)
            dd.text((x, FY + 34), str(yr), font=f, fill=(250, 250, 246), anchor="mm", stroke_width=4, stroke_fill=(30, 28, 28))
        if t < t0 - .1: x, yy, sx, sy, yr = self.x(y0), FY, 1, 1, y0
        elif t < t0:     x, yy, sx, sy, yr = self.x(y0), FY, 1.18, .8, y0          # anticipation : tassement
        elif t < t0 + d:                                                            # arc + étirement
            u = ease((t - t0)/d); x, yy = arc((self.x(y0), FY), (self.x(y1), FY), u, -90 - .3*abs(self.x(y1) - self.x(y0)))
            sx, sy = .88, 1.14; yr = round(lerp(y0, y1, u))
        else:
            x, yy, yr = self.x(y1), FY, y1; sx, sy = squash(t, t0 + d, .25)          # écrasement à l'arrivée
        dd.rounded_rectangle([self.x0, FY - 6, x, FY + 6], 6, fill=self.bar)
        blit_sxy(cv, self.knob, x, yy + 34, sx, sy)
        txt = lab or str(yr)
        Label(txt, f"fr{self.txt}{txt}", font("title", 54), (30, 28, 28), (250, 196, 30), padx=16, pady=2, rough=2).draw(cv, fr, x, yy - 78, 1, -3)

def K(txt, key, bg, fg=(250, 250, 246), size=96, rough=4):
    return Label(txt, key, font("title", size), fg, bg, padx=26, pady=6, rough=rough, maxw=980)

def note(txt, key, size=54, bg=None, fg=None):
    return Label(txt, key, font("hand", size), fg or PAL["ink"], bg or PAL["cream"], padx=22, pady=8, rough=3, maxw=900)
