"""DA « pixel.fc » : rendu pixel-art pour TOUS les formats de la chaîne (tactique, storytime style Rennes, quiz…).
Principe : la scène est dessinée comme d'habitude, puis PIXELISÉE (réduction ×1/S en moyenne, palette fixe de 32 couleurs
façon PICO-8 étendue, agrandissement « plus proche voisin ») ; les textes d'interface (sous-titres, étiquettes, bandeaux, compteurs)
sont dessinés APRÈS, en police pixel nette (Press Start 2P / Silkscreen, sans anticrénelage, agrandie par facteur entier).
Activation : variable d'environnement PIXEL=1 (lue par engine/tactique.py, engine/karaoke.py, episodes/rennes/rstyle.py).
  pixelate(img)            -> image pixel-art (même taille)
  ptext_img(txt, px, col)  -> sprite de texte pixel (ombre portée 1 pixel-art)
  plabel(txt, px, fg, bg)  -> étiquette pixel (cadre 2 px, ombre décalée), style « boîte de dialogue » de jeu vidéo"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ON = os.environ.get("PIXEL", "0") == "1"
S = int(os.environ.get("PIXEL_SCALE", "4"))                       # taille d'un « gros pixel » à l'écran (1080/4 = 270 px de large)
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts")
PICO = ["000000", "1D2B53", "7E2553", "008751", "AB5236", "5F574F", "C2C3C7", "FFF1E8", "FF004D", "FFA300", "FFEC27", "00E436",
        "29ADFF", "83769C", "FF77A8", "FFCCAA", "291814", "111D35", "422136", "125359", "742F29", "49333B", "A28879", "F3EF7D",
        "BE1250", "FF6C24", "A8E72E", "00B543", "065AB5", "754665", "FF6E59", "FF9D81"]
PAL = [tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for h in PICO]
BLACK, NAVY, WINE, GREEN, BROWN, GREY, LIGHT, WHITE, RED, ORANGE, YELLOW, LIME, SKY, LAVENDER, PINK, PEACH = PAL[:16]
DNAVY, DGREEN, DRED, BLUE = PAL[17], PAL[19], PAL[24], PAL[28]
_pimg = None
def _palimg():
    global _pimg
    if _pimg is None:
        p = Image.new("P", (1, 1)); flat = sum(PAL, ()); p.putpalette(flat + flat[:3]*(256 - len(PAL))); _pimg = p
    return _pimg
def pixelate(img, s=None, dither=False, smooth=True):
    """Réduit, quantifie sur la palette, réagrandit en gros pixels nets. smooth : filtre « mode » 3×3 qui efface le grain
    (textures papier, bruit de photo) pour garder de vrais aplats de pixel-art."""
    from PIL import ImageFilter
    s = s or S; w, h = img.size; rgb = img.convert("RGB")
    small = rgb.resize((max(1, w//s), max(1, h//s)), Image.BOX)
    q = small.quantize(palette=_palimg(), dither=Image.Dither.ORDERED if dither else Image.Dither.NONE).convert("RGB")
    if smooth: q = q.filter(ImageFilter.ModeFilter(3))
    return q.resize((w//s*s, h//s*s), Image.NEAREST).crop((0, 0, w, h)) if (w % s or h % s) else q.resize((w, h), Image.NEAREST)
def near(c):
    """Couleur de la palette la plus proche (pour que les textes restent dans la palette)."""
    c = np.array(c[:3]); return PAL[int(np.argmin(((np.array(PAL) - c)**2).sum(1)))]
_f = {}
def pfont(px, name="PressStart2P-Regular.ttf"):
    k = (px, name)
    if k not in _f: _f[k] = ImageFont.truetype(os.path.join(FONTS, name), px)
    return _f[k]
_c = {}
def ptext_img(txt, px=8, col=WHITE, shadow=BLACK, outline=BLACK, s=None, font="Silkscreen-Bold.ttf"):
    """Texte en police pixel dessiné à 1:1 (pas d'anticrénelage) puis agrandi ×s : contour 1 px + ombre 1 px."""
    s = s or S; k = (txt, px, col, shadow, outline, s, font)
    if k in _c: return _c[k]
    f = pfont(px, font); w = int(f.getlength(txt)) + 4; h = px + 6
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.fontmode = "1"
    if shadow: d.text((2, 3), txt, font=f, fill=shadow)
    if outline:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)): d.text((1 + dx, 1 + dy), txt, font=f, fill=outline)
    d.text((1, 1), txt, font=f, fill=near(col))
    im = im.resize((w*s, h*s), Image.NEAREST); im.info["anchor"] = (im.width/2, im.height/2); _c[k] = im
    return im
def plabel(txt, px=8, fg=WHITE, bg=NAVY, border=WHITE, s=None, font="Silkscreen-Bold.ttf", pad=3):
    """Étiquette « boîte de dialogue » : fond plein, cadre clair 1 px, coin coupé, ombre portée 1 px (en gros pixels)."""
    s = s or S; k = ("lab", txt, px, fg, bg, border, s, font, pad)
    if k in _c: return _c[k]
    f = pfont(px, font); tw = int(f.getlength(txt)); w, h = tw + 2*pad + 4, px + 2*pad + 4
    im = Image.new("RGBA", (w + 1, h + 1), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.fontmode = "1"
    d.rectangle([1, 1, w, h], fill=BLACK)                               # ombre
    d.rectangle([0, 0, w - 1, h - 1], fill=near(bg)); d.rectangle([0, 0, w - 1, h - 1], outline=near(border))
    for x, y in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)): d.point((x, y), fill=(0, 0, 0, 0))   # coins coupés
    d.text((pad + 2, pad + 2), txt, font=f, fill=near(fg))
    im = im.resize(((w + 1)*s, (h + 1)*s), Image.NEAREST); im.info["anchor"] = (im.width/2, im.height/2); _c[k] = im
    return im
def put(cv, im, x, y, sc=1.0, a=1.0):
    """Colle un sprite pixel centré ; l'échelle est arrondie à un multiple entier de pixel (jamais de flou)."""
    if sc <= .05 or a <= .05: return
    if abs(sc - 1) > .01:
        k = max(1, round(sc*4))/4; im = im.resize((max(1, int(im.width*k)), max(1, int(im.height*k))), Image.NEAREST)
    if a < .99: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v*a)))
    x0 = int(round((x - im.width/2)/S))*S; y0 = int(round((y - im.height/2)/S))*S             # calé sur la grille de gros pixels
    cv.alpha_composite(im, (x0, y0)) if cv.mode == "RGBA" else cv.paste(im, (x0, y0), im)
def scanlines(cv, a=18):
    """Lignes de balayage très discrètes (écran rétro) : une ligne sombre par gros pixel."""
    ov = Image.new("RGBA", cv.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for y in range(S - 1, cv.height, S): d.line([(0, y), (cv.width, y)], fill=(0, 0, 0, a))
    cv.alpha_composite(ov) if cv.mode == "RGBA" else cv.paste(ov, (0, 0), ov)
