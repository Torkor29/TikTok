"""DA « aquarelle » : la scène (style Rennes / papier) est repeinte comme une aquarelle sur papier grain fin.
Étapes (à demi-résolution, puis agrandie) : stylisation douce (cv2.stylization = lavis à plats fondus), bords légèrement ondulés
(déplacement par bruit basse fréquence), « bord mouillé » (pigment plus sombre le long des contours), tons pastel, granulation du
pigment et texture de papier aquarelle, vignette claire. Les textes d'interface (sous-titres au pinceau) sont posés APRÈS.
Activation : AQUA=1 (lu par episodes/rennes/rstyle.py et engine/karaoke.py)."""
import os, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
ON = os.environ.get("AQUA", "0") == "1"
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts")
_c = {}
def _noise(w, h, scale, seed):
    rng = np.random.default_rng(seed); s = rng.random((max(2, h//scale), max(2, w//scale))).astype(np.float32)
    return cv2.resize(s, (w, h), interpolation=cv2.INTER_CUBIC)
def _maps(w, h, b):
    k = (w, h, b)
    if k in _c: return _c[k]
    dx = (_noise(w, h, 40, 11 + b) - .5)*5; dy = (_noise(w, h, 40, 23 + b) - .5)*5     # ondulation des bords (≈ 2 px)
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    paper = .9 + .07*_noise(w, h, 60, 5) + .03*_noise(w, h, 3, 7)                     # papier : taches larges + grain fin
    gran = _noise(w, h, 2, 9 + b)                                                       # granulation du pigment
    yy, xx = np.mgrid[0:h, 0:w]; vig = np.clip(((xx - w/2)/(w*.62))**2 + ((yy - h/2)/(h*.62))**2, 0, 1)
    _c[k] = (gx + dx, gy + dy, paper.astype(np.float32), gran.astype(np.float32), vig.astype(np.float32)); return _c[k]
def paint(img, fr=0):
    """img PIL 1080×1920 -> aquarelle : lavis simplifiés (mean-shift), bords qui « bavent » (flou + ondulation), fin liseré de
    pigment au bord des taches, variations de pigment dans les aplats, transparence (on éclaircit sans délaver la teinte), grain du papier."""
    W, H = img.size; w, h = W//2, H//2; b = (fr//4) % 2
    q = cv2.resize(np.asarray(img.convert("RGB")), (W//4, H//4), interpolation=cv2.INTER_AREA)
    q = cv2.pyrMeanShiftFiltering(q, 6, 22)                                            # lavis : grandes taches de couleur
    a = cv2.resize(q, (w, h), interpolation=cv2.INTER_CUBIC)
    a = cv2.GaussianBlur(a, (0, 0), 1.4)                                               # l'eau fait baver les bords
    mx, my, paper, gran, vig = _maps(w, h, b)
    a = cv2.remap(a, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    g = cv2.cvtColor(a.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    e = cv2.morphologyEx(g, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)); e = np.clip(e/40, 0, 1)
    a *= (1 - .14*e)[..., None]                                                         # liseré de pigment (bord mouillé), fin
    pool = _noise(w, h, 70, 31) * .6 + _noise(w, h, 18, 37) * .4                        # le pigment se dépose inégalement (même teinte)
    bloom = np.clip((_noise(w, h, 26, 41 + b) - .72)*5, 0, 1)                           # auréoles : l'eau repousse le pigment
    k = (.84 + .26*pool)*(1 + .18*bloom); a = 255 - (255 - a)*(2 - k)[..., None]
    a = 255 - (255 - a)*.78                                                             # transparence : le blanc du papier remonte
    a *= (1 - .06*(gran - .5)*2*(1 - g/255))[..., None]                                 # granulation
    a *= paper[..., None]; a = a*(1 - .22*vig[..., None]) + 250*.22*vig[..., None]
    return Image.fromarray(cv2.resize(np.clip(a, 0, 255).astype(np.uint8), (W, H), interpolation=cv2.INTER_CUBIC))
_f = {}
def font(px, name="CaveatBrush-Regular.ttf"):
    k = (px, name)
    if k not in _f:
        p = os.path.join(FONTS, name)
        if not os.path.exists(p): p = os.path.join("/tmp/edu-assets/fonts", name)
        _f[k] = ImageFont.truetype(p, px)
    return _f[k]
INK = (40, 46, 70); HI = (200, 60, 70)
def caption(cv, W, t, y, emph=None, size=110):
    """Sous-titre « au pinceau » (Caveat Brush) : encre bleu nuit, mot dit en rouge carmin, petite tache d'eau derrière."""
    import karaoke as KA
    if not hasattr(W, "_cha"): W._cha = W.chunks(3)
    cur = [c for c in W._cha if c[0] <= t < c[1]]
    if not cur: return
    t0, t1, toks = cur[-1]; f = font(size); d = ImageDraw.Draw(cv)
    words = [tk[1] for tk in toks]; ws = [f.getlength(w + " ") for w in words]; x = cv.width/2 - sum(ws)/2
    for tk, w, wd in zip(toks, words, ws):
        if tk[3] <= t:
            col = HI if tk[3] <= t < tk[4] + .05 else INK
            d.text((x + 3, y + 4), w, font=f, fill=(255, 255, 255)); d.text((x, y), w, font=f, fill=col)
        x += wd
