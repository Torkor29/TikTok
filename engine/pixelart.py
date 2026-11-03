"""pixel.fc v2 — VRAI pixel-art dessiné à la main (style des vidéos de référence « De zéro à champion du monde ») :
on dessine directement sur un petit canevas (LW×LH = 135×240 « gros pixels »), agrandi ×8 sans flou (1080×1920).
Sprites procéduraux avec contour sombre et ombrage 2 tons : joueurs (face / dos, poses : debout, marche, frappe, bras levés,
triste), femme, homme en costume, ballon, cages, foule de tribune qui bouge, pelouse rayée, rue de nuit, chambre, vestiaire,
documents (contrat, liste, enveloppe), cartes « FIFA » (note + poste), coupe, tableau d'affichage, étiquettes en police pixel.
L'interface haute définition (gros sous-titres en haut, en-tête d'épisode) est dessinée APRÈS l'agrandissement : voir hud().
Toutes les fonctions dessinent sur un canevas logique (Image RGBA LW×LH) : x, y en gros pixels."""
import os, math, random
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
LW, LH, SC = 135, 240, 8
W, H = LW*SC, LH*SC
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FONTS = os.path.join(ROOT, "assets", "fonts")
OUT = (28, 20, 30)                                                   # contour
SKINS = [(246, 204, 164), (226, 172, 128), (186, 126, 86), (140, 92, 62), (102, 66, 46)]
HAIRS = [(40, 30, 26), (92, 60, 36), (168, 120, 70), (214, 178, 110), (20, 18, 20)]
KITS = {
    "psg": dict(shirt=(30, 44, 110), band=(214, 36, 48), band2=(250, 250, 246), shorts=(30, 44, 110), socks=(30, 44, 110), num=(250, 250, 246)),
    "om": dict(shirt=(250, 250, 246), band=(40, 170, 225), band2=None, shorts=(250, 250, 246), socks=(250, 250, 246), num=(40, 170, 225)),
    "juve": dict(shirt=(250, 250, 246), stripes=(30, 28, 32), shorts=(30, 28, 32), socks=(30, 28, 32), num=(30, 28, 32)),
    "milan": dict(shirt=(206, 24, 36), stripes=(30, 28, 32), shorts=(250, 250, 246), socks=(30, 28, 32), num=(250, 250, 246)),
    "france": dict(shirt=(28, 44, 120), band=None, shorts=(250, 250, 246), socks=(214, 36, 48), num=(250, 250, 246)),
    "real": dict(shirt=(250, 250, 246), band=None, shorts=(250, 250, 246), socks=(250, 250, 246), num=(120, 60, 160)),
    "rennes": dict(shirt=(214, 26, 34), band=None, shorts=(30, 28, 32), socks=(214, 26, 34), num=(250, 250, 246)),
    "suit": dict(shirt=(46, 48, 60), band=None, shorts=(46, 48, 60), socks=(46, 48, 60), num=None, tie=(200, 30, 40)),
    "training": dict(shirt=(70, 80, 96), band=None, shorts=(50, 56, 70), socks=(50, 56, 70), num=None),
}
def dark(c, k=.72): return tuple(int(v*k) for v in c[:3])
def light(c, k=1.18): return tuple(min(255, int(v*k + 12)) for v in c[:3])
DIG = {"0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"], "2": ["111", "001", "111", "100", "111"],
       "3": ["111", "001", "011", "001", "111"], "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"],
       "6": ["111", "100", "111", "101", "111"], "7": ["111", "001", "010", "010", "010"], "8": ["111", "101", "111", "101", "111"],
       "9": ["111", "101", "111", "001", "111"]}
def digits(d, x, y, txt, col):
    for k, ch in enumerate(str(txt)):
        for r, row in enumerate(DIG.get(ch, DIG["0"])):
            for c, v in enumerate(row):
                if v == "1": d.point((x + k*4 + c, y + r), fill=col)
def outline(im, col=OUT):
    """Contour 1 px autour de tout pixel opaque."""
    a = np.asarray(im.getchannel("A")) > 0; o = np.zeros_like(a)
    o[1:, :] |= a[:-1, :]; o[:-1, :] |= a[1:, :]; o[:, 1:] |= a[:, :-1]; o[:, :-1] |= a[:, 1:]
    o &= ~a; arr = np.asarray(im).copy(); arr[o] = col + (255,); return Image.fromarray(arr)
# ------------------------------------------------------------------ personnages
@lru_cache(maxsize=4096)
def person(kit="psg", skin=2, hair=0, hstyle="short", pose="stand", back=False, num=None, frame=0, mood="happy", gender="m"):
    """Sprite 18×30 (marge 1 px pour le contour). Ancre conseillée : bas-centre (9, 29)."""
    K = KITS[kit]; sk = SKINS[skin]; hc = HAIRS[hair]; im = Image.new("RGBA", (18, 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ox = 1
    # jambes
    if pose in ("walk",):
        lx = (-1, 1) if frame % 2 == 0 else (1, -1)
    elif pose == "kick": lx = (0, 3)
    else: lx = (0, 0)
    legc = K["socks"]
    for side, dx in ((0, lx[0]), (1, lx[1])):
        x0 = ox + (4 if side == 0 else 9) + dx
        if gender == "f": d.rectangle([x0, 21, x0 + 2, 24], fill=sk); d.rectangle([x0, 25, x0 + 2, 26], fill=sk)
        else: d.rectangle([x0, 21, x0 + 2, 22], fill=sk); d.rectangle([x0, 23, x0 + 2, 26], fill=legc); d.point((x0, 23), fill=light(legc))
        d.rectangle([x0 - (1 if side == 0 else 0), 27, x0 + 2 + (1 if side == 1 else 0), 28], fill=(40, 36, 40))
    # short / jupe
    sh = K["shorts"]
    if gender == "f": d.rectangle([ox + 3, 17, ox + 12, 21], fill=K["shirt"]); d.rectangle([ox + 3, 21, ox + 12, 21], fill=dark(K["shirt"]))
    else: d.rectangle([ox + 4, 17, ox + 11, 20], fill=sh); d.line([(ox + 7, 19), (ox + 8, 19)], fill=dark(sh)); d.rectangle([ox + 4, 17, ox + 11, 17], fill=dark(sh))
    # torse
    sc = K["shirt"]; d.rectangle([ox + 3, 10, ox + 12, 17], fill=sc); d.rectangle([ox + 11, 10, ox + 12, 17], fill=dark(sc))
    if K.get("stripes"):
        for x in (ox + 4, ox + 7, ox + 10): d.rectangle([x, 10, x, 17], fill=K["stripes"])
    if K.get("band") and not back:
        d.rectangle([ox + 7, 10, ox + 8, 17], fill=K["band"])
        if K.get("band2"): d.rectangle([ox + 6, 10, ox + 6, 17], fill=K["band2"]); d.rectangle([ox + 9, 10, ox + 9, 17], fill=K["band2"])
    if kit == "suit" and not back:
        d.polygon([(ox + 6, 10), (ox + 9, 10), (ox + 7.5, 14)], fill=(244, 242, 236)); d.rectangle([ox + 7, 11, ox + 8, 15], fill=K["tie"])
    if back and num is not None and K.get("num"): digits(d, ox + 8 - 2*len(str(num)), 11, num, K["num"])
    elif num is not None and K.get("num"): digits(d, ox + 10 - 0, 11, str(num)[:1], K["num"]) if False else None
    # bras
    arm_up = pose in ("cheer",); arm_out = pose in ("kick", "shrug")
    for side in (0, 1):
        x0 = ox + (1 if side == 0 else 13)
        if arm_up:
            d.rectangle([x0, 3, x0 + 1, 11], fill=sk); d.rectangle([x0, 9, x0 + 1, 11], fill=sc)
        elif arm_out:
            xx = x0 - 1 if side == 0 else x0 + 1; d.rectangle([xx, 10, xx + 1, 12], fill=sc); d.rectangle([xx + (-1 if side == 0 else 1), 13, xx + 1 + (-1 if side == 0 else 1), 15], fill=sk)
        else:
            sw = (1 if frame % 2 else -1) if pose == "walk" else 0; sw = sw if side == 0 else -sw
            d.rectangle([x0, 10 + max(0, sw), x0 + 1, 12], fill=sc); d.rectangle([x0, 13, x0 + 1, 16 + min(0, sw)], fill=sk)
    # tête
    d.rectangle([ox + 6, 8, ox + 9, 9], fill=dark(sk, .85))                      # cou
    d.rectangle([ox + 4, 1, ox + 11, 8], fill=sk); d.rectangle([ox + 11, 2, ox + 11, 8], fill=dark(sk, .88))
    if back:
        d.rectangle([ox + 4, 0, ox + 11, 6], fill=hc); d.rectangle([ox + 4, 0, ox + 11, 0], fill=light(hc))
        if hstyle in ("long", "longf"): d.rectangle([ox + 3, 1, ox + 12, 10], fill=hc)
    else:
        if hstyle == "bald": d.rectangle([ox + 4, 1, ox + 11, 1], fill=dark(sk))
        else:
            d.rectangle([ox + 4, 0, ox + 11, 2], fill=hc); d.point((ox + 4, 3), fill=hc); d.point((ox + 11, 3), fill=hc)
            if hstyle == "long": d.rectangle([ox + 3, 1, ox + 4, 7], fill=hc); d.rectangle([ox + 11, 1, ox + 12, 7], fill=hc); d.rectangle([ox + 4, 1, ox + 11, 1], fill=(250, 250, 246))  # bandeau
            if hstyle == "longf": d.rectangle([ox + 3, 1, ox + 4, 11], fill=hc); d.rectangle([ox + 11, 1, ox + 12, 11], fill=hc)
            if hstyle == "curly":
                for x in range(ox + 3, ox + 13, 2): d.point((x, 0), fill=dark(hc))
        ey = 5; d.point((ox + 6, ey), fill=OUT); d.point((ox + 9, ey), fill=OUT)
        if mood == "sad": d.line([(ox + 6, 7), (ox + 9, 7)], fill=dark(sk, .6)); d.point((ox + 6, 6), fill=(120, 170, 230))
        elif mood == "angry": d.line([(ox + 5, 4), (ox + 7, 4)], fill=OUT); d.line([(ox + 8, 4), (ox + 10, 4)], fill=OUT); d.line([(ox + 7, 7), (ox + 8, 7)], fill=OUT)
        else: d.line([(ox + 7, 7), (ox + 8, 7)], fill=(150, 60, 60)); d.point((ox + 6, 6), fill=dark(sk, .8)); d.point((ox + 9, 6), fill=dark(sk, .8))
    return outline(im)
def blit(L, spr, x, y, scale=1, flip=False, anchor="bottom"):
    """Colle un sprite (x, y = bas-centre par défaut), échelle entière."""
    if flip: spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
    if scale != 1: spr = spr.resize((spr.width*scale, spr.height*scale), Image.NEAREST)
    x0 = int(round(x - spr.width/2)); y0 = int(round(y - spr.height)) if anchor == "bottom" else int(round(y - spr.height/2))
    L.alpha_composite(spr, (x0, y0)) if 0 <= x0 and 0 <= y0 and x0 + spr.width <= L.width and y0 + spr.height <= L.height else _safe(L, spr, x0, y0)
def _safe(L, spr, x0, y0):
    big = Image.new("RGBA", L.size, (0, 0, 0, 0)); big.paste(spr, (x0, y0), spr); L.alpha_composite(big)
def shadow(L, x, y, w=10):
    ov = Image.new("RGBA", L.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse([x - w//2, y - 1, x + w//2, y + 1], fill=(0, 0, 0, 80)); L.alpha_composite(ov)
@lru_cache(maxsize=64)
def ball_spr(f=0):
    im = Image.new("RGBA", (7, 7), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.ellipse([1, 1, 5, 5], fill=(250, 250, 246))
    for (x, y) in ((3, 3), (2 + f % 2, 2), (4, 4 - f % 2)): d.point((x, y), fill=(40, 40, 44))
    return outline(im)
# ------------------------------------------------------------------ décors
def fill(L, col): L.paste(col + (255,), (0, 0, L.width, L.height))
def vgrad(L, y0, y1, c0, c1, step=2):
    d = ImageDraw.Draw(L)
    for y in range(int(y0), int(y1), step):
        u = (y - y0)/max(1, y1 - y0); d.rectangle([0, y, L.width, y + step - 1], fill=tuple(int(a + (b - a)*u) for a, b in zip(c0, c1)))
def pitch(L, y0=120, col=(52, 150, 62), col2=(60, 166, 72), lines=True):
    d = ImageDraw.Draw(L)
    for k, y in enumerate(range(y0, L.height, 12)): d.rectangle([0, y, L.width, y + 11], fill=col if k % 2 else col2)
    if lines: d.line([(0, y0 + 6), (L.width, y0 + 6)], fill=(236, 244, 236))
def crowd(L, t, y0=40, y1=112, pal=None, cheer=0.0, seed=1, boo=False):
    """Tribune : rangées de supporters 4×5 px (tête + maillot), qui sautent quand cheer > 0."""
    d = ImageDraw.Draw(L); rnd = random.Random(seed); pal = pal or [(30, 44, 110), (214, 36, 48), (250, 250, 246), (240, 140, 40), (60, 120, 200)]
    d.rectangle([0, y0 - 4, L.width, y1 + 4], fill=(24, 28, 52))
    for r, y in enumerate(range(y0, y1, 9)):
        d.rectangle([0, y + 6, L.width, y + 8], fill=(40, 46, 80))
        for x in range(1 - (r % 2)*3, L.width, 6):
            jump = 1 if cheer > 0 and math.sin(t*14 + x*.7 + r) > (1 - cheer*1.6) else 0
            c = rnd.choice(pal); s = rnd.choice(SKINS); hc = rnd.choice(HAIRS)
            d.rectangle([x, y + 2 - jump, x + 3, y + 5 - jump], fill=c); d.rectangle([x + 1, y - 1 - jump, x + 2, y + 1 - jump], fill=s); d.point((x + 1, y - 1 - jump), fill=hc); d.point((x + 2, y - 1 - jump), fill=hc)
            if cheer > .5 and jump: d.point((x, y - 2), fill=s); d.point((x + 3, y - 2), fill=s)
    d.rectangle([0, y1 + 2, L.width, y1 + 7], fill=(30, 44, 110))
    for x in range(0, L.width, 22): d.rectangle([x + 3, y1 + 3, x + 14, y1 + 5], fill=(250, 250, 246) if (x//22) % 2 else (214, 36, 48))
def stadium(L, t, pal=None, cheer=0.0, sky=((14, 18, 44), (40, 50, 100)), y_pitch=120, seed=1):
    vgrad(L, 0, 40, *sky); crowd(L, t, 36, y_pitch - 8, pal, cheer, seed); pitch(L, y_pitch)
    d = ImageDraw.Draw(L)
    for x in (12, 122):
        for k in range(3): d.rectangle([x - 3 + k*2, 6, x - 2 + k*2, 7], fill=(255, 250, 220))
        d.line([(x, 8), (x, 30)], fill=(90, 96, 120))
def goal(L, x, y, w=44, h=20):
    d = ImageDraw.Draw(L)
    for gx in range(x - w//2, x + w//2 + 1, 3): d.line([(gx, y - h), (gx, y)], fill=(200, 210, 210))
    for gy in range(y - h, y + 1, 3): d.line([(x - w//2, gy), (x + w//2, gy)], fill=(200, 210, 210))
    d.rectangle([x - w//2 - 1, y - h - 1, x + w//2 + 1, y - h], fill=(250, 250, 250)); d.rectangle([x - w//2 - 1, y - h, x - w//2, y], fill=(250, 250, 250)); d.rectangle([x + w//2, y - h, x + w//2 + 1, y], fill=(250, 250, 250))
def night_city(L, t, seed=3, y_ground=170):
    vgrad(L, 0, y_ground, (12, 14, 40), (34, 40, 84)); d = ImageDraw.Draw(L); rnd = random.Random(seed)
    for k in range(18): x, y = rnd.randrange(L.width), rnd.randrange(60); d.point((x, y), fill=(220, 220, 255) if (int(t*3) + k) % 7 else (120, 120, 160))
    x = -4
    while x < L.width:
        w = rnd.randint(16, 30); h = rnd.randint(50, 110); c = rnd.choice([(30, 36, 70), (40, 44, 82), (26, 30, 60)])
        d.rectangle([x, y_ground - h, x + w, y_ground], fill=c)
        for wy in range(y_ground - h + 5, y_ground - 6, 8):
            for wx in range(x + 3, x + w - 3, 6):
                if rnd.random() < .45: d.rectangle([wx, wy, wx + 2, wy + 3], fill=(250, 214, 110) if rnd.random() < .8 else (255, 240, 180))
        x += w + 1
    d.rectangle([0, y_ground, L.width, L.height], fill=(46, 48, 58)); d.rectangle([0, y_ground, L.width, y_ground + 2], fill=(90, 92, 104))
def room(L, wall=(64, 52, 72), floor=(120, 78, 50), y_floor=176, window=True, t=0.0):
    fill(L, wall); d = ImageDraw.Draw(L)
    for y in range(20, y_floor, 16): d.line([(0, y), (L.width, y)], fill=dark(wall, .9))
    d.rectangle([0, y_floor, L.width, L.height], fill=floor)
    for y in range(y_floor + 6, L.height, 8): d.line([(0, y), (L.width, y)], fill=dark(floor, .8))
    for x in range(0, L.width, 22): d.line([(x, y_floor), (x, L.height)], fill=dark(floor, .85))
    if window:
        d.rectangle([84, 40, 122, 86], fill=(26, 30, 66)); d.rectangle([84, 40, 122, 86], outline=(170, 140, 100)); d.line([(103, 40), (103, 86)], fill=(170, 140, 100)); d.line([(84, 63), (122, 63)], fill=(170, 140, 100))
        for k in range(6): d.point((88 + k*6, 46 + (k*5) % 14), fill=(240, 230, 160))
def lockers(L, y_floor=180):
    fill(L, (60, 66, 80)); d = ImageDraw.Draw(L)
    for x in range(4, L.width, 22):
        d.rectangle([x, 50, x + 19, y_floor], fill=(84, 92, 112)); d.rectangle([x, 50, x + 19, y_floor], outline=(40, 44, 56))
        for k in range(3): d.line([(x + 6, 58 + k*3), (x + 13, 58 + k*3)], fill=(50, 56, 70))
        d.rectangle([x + 15, 110, x + 16, 116], fill=(200, 200, 210))
    d.rectangle([0, y_floor, L.width, L.height], fill=(120, 120, 130)); d.rectangle([10, y_floor - 12, 125, y_floor - 8], fill=(150, 100, 60))
def bench(L, x, y, w=60):
    d = ImageDraw.Draw(L); d.rectangle([x - w//2, y - 14, x + w//2, y - 4], fill=(30, 44, 110)); d.rectangle([x - w//2, y - 14, x + w//2, y - 13], fill=(60, 80, 160))
    d.rectangle([x - w//2 + 2, y - 4, x - w//2 + 3, y], fill=(80, 84, 96)); d.rectangle([x + w//2 - 3, y - 4, x + w//2 - 2, y], fill=(80, 84, 96))
# ------------------------------------------------------------------ objets / UI pixel
def pfont(px=8, name="Silkscreen-Regular.ttf"): return ImageFont.truetype(os.path.join(FONTS, name), px)
def ptext(L, txt, x, y, col=(250, 250, 246), px=8, name="Silkscreen-Regular.ttf", anchor="mm", shadow=None):
    d = ImageDraw.Draw(L); d.fontmode = "1"; f = pfont(px, name)
    if shadow: d.text((x + 1, y + 1), txt, font=f, fill=shadow, anchor=anchor)
    d.text((x, y), txt, font=f, fill=col, anchor=anchor)
def plabel(L, txt, x, y, fg=(255, 214, 64), bg=(18, 22, 40), border=None, px=8, name="Silkscreen-Regular.ttf"):
    d = ImageDraw.Draw(L); d.fontmode = "1"; f = pfont(px, name); w = int(f.getlength(txt)) + 6; h = px + 4
    x0, y0 = int(x - w/2), int(y - h/2); d.rectangle([x0 + 1, y0 + 1, x0 + w + 1, y0 + h + 1], fill=(0, 0, 0, 120))
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=bg)
    if border: d.rectangle([x0, y0, x0 + w, y0 + h], outline=border)
    d.text((x0 + 3, y0 + 2), txt, font=f, fill=fg)
def paper_doc(L, x, y, title, lines=4, w=56, h=70, stamp=None, col=(250, 246, 236), head=(200, 40, 50), t=0.0):
    d = ImageDraw.Draw(L); x0, y0 = int(x - w/2), int(y - h/2)
    d.rectangle([x0 + 2, y0 + 2, x0 + w + 2, y0 + h + 2], fill=(0, 0, 0, 90)); d.rectangle([x0, y0, x0 + w, y0 + h], fill=col); d.rectangle([x0, y0, x0 + w, y0 + 8], fill=head)
    d.fontmode = "1"; d.text((x, y0 + 4), title, font=pfont(8), fill=(250, 250, 246), anchor="mm")
    for k in range(lines): d.line([(x0 + 5, y0 + 16 + k*9), (x0 + w - 6 - (k % 2)*10, y0 + 16 + k*9)], fill=(190, 186, 176))
    d.rectangle([x0, y0, x0 + w, y0 + h], outline=dark(col, .8))
    if stamp: ptext(L, stamp[0], x, y + h//4, stamp[1], 8, "Silkscreen-Bold.ttf")
def envelope(L, x, y, t=0.0):
    d = ImageDraw.Draw(L); d.rectangle([x - 14, y - 9, x + 14, y + 9], fill=(250, 246, 236)); d.rectangle([x - 14, y - 9, x + 14, y + 9], outline=(150, 140, 130))
    d.line([(x - 14, y - 9), (x, y + 1), (x + 14, y - 9)], fill=(150, 140, 130)); ptext(L, "@", x, y + 4, (214, 36, 48), 8, "Silkscreen-Bold.ttf")
def laptop(L, x, y, glow=1.0):
    d = ImageDraw.Draw(L); d.rectangle([x - 18, y - 22, x + 18, y], fill=(40, 40, 50)); d.rectangle([x - 16, y - 20, x + 16, y - 2], fill=tuple(int(c*glow) for c in (110, 170, 240)))
    d.rectangle([x - 22, y, x + 22, y + 3], fill=(150, 150, 160))
def cup(L, x, y, s=1):
    im = Image.new("RGBA", (22, 26), (0, 0, 0, 0)); d = ImageDraw.Draw(im); g, gd, gl = (240, 190, 50), (190, 140, 30), (255, 236, 140)
    d.rectangle([5, 1, 16, 11], fill=g); d.rectangle([6, 1, 8, 10], fill=gl); d.rectangle([14, 1, 16, 11], fill=gd); d.rectangle([7, 12, 14, 13], fill=g)
    d.rectangle([9, 14, 12, 18], fill=gd); d.rectangle([6, 19, 15, 21], fill=g); d.rectangle([5, 22, 16, 24], fill=(120, 80, 40))
    for k in range(5): d.point((3, 3 + k*2), fill=g); d.point((18, 3 + k*2), fill=g)
    blit(L, outline(im), x, y, s)
def card(L, x, y, rating, label, kit="psg", col=(240, 190, 50), skin=2, hair=0, hstyle="short", num=None, s=1, t=0.0):
    """Carte « FIFA » : fond coloré dégradé + cadre, note en haut à gauche, joueur, poste en bas."""
    w, h = 40*s, 56*s; x0, y0 = int(x - w/2), int(y - h/2); d = ImageDraw.Draw(L)
    d.rectangle([x0 + 2, y0 + 2, x0 + w + 2, y0 + h + 2], fill=(0, 0, 0, 100))
    for k in range(h): d.line([(x0, y0 + k), (x0 + w, y0 + k)], fill=tuple(int(c*(1 - .35*k/h)) for c in col))
    d.rectangle([x0, y0, x0 + w, y0 + h], outline=light(col)); d.rectangle([x0 + 1, y0 + 1, x0 + w - 1, y0 + h - 1], outline=dark(col))
    ptext(L, str(rating), x0 + 4*s, y0 + 6*s, (250, 250, 246), 8*s if s > 1 else 8, "Silkscreen-Bold.ttf", "lm")
    blit(L, person(kit, skin, hair, hstyle, "stand", False, num), x, y0 + int(h*.78), s)
    d.rectangle([x0 + 2, y0 + h - 12*s, x0 + w - 2, y0 + h - 2], fill=(18, 22, 40)); ptext(L, label, x, y0 + h - 7*s, (250, 250, 246), 8, "Silkscreen-Bold.ttf")
def scoreboard(L, x, y, a, b, la, lb, sub=None):
    d = ImageDraw.Draw(L); d.rectangle([x - 46, y - 16, x + 46, y + 16], fill=(16, 18, 30)); d.rectangle([x - 46, y - 16, x + 46, y + 16], outline=(70, 76, 100))
    ptext(L, la, x - 30, y - 9, (200, 204, 220)); ptext(L, lb, x + 30, y - 9, (200, 204, 220))
    ptext(L, f"{a} - {b}", x, y + 4, (255, 214, 64), 16, "Silkscreen-Bold.ttf")
    if sub: ptext(L, sub, x, y + 22, (170, 176, 200))
def sparkle(L, x, y, t, col=(255, 250, 200)):
    k = int(t*8) % 4; d = ImageDraw.Draw(L)
    if k < 3: d.line([(x - 2 - k//2, y), (x + 2 + k//2, y)], fill=col); d.line([(x, y - 2 - k//2), (x, y + 2 + k//2)], fill=col)
def heart(L, x, y, col=(240, 50, 80)):
    d = ImageDraw.Draw(L)
    for r, row in enumerate(["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]):
        for c, v in enumerate(row):
            if v == "1": d.point((x - 3 + c, y - 3 + r), fill=col)
def dust_cloud(L, x, y, t, r=26):
    d = ImageDraw.Draw(L); rnd = random.Random(int(t*10))
    for k in range(10):
        a = k/10*2*math.pi + t*4; rr = r + 4*math.sin(t*12 + k); cx, cy = x + rr*math.cos(a), y + rr*.55*math.sin(a)
        d.ellipse([cx - 10, cy - 7, cx + 10, cy + 7], fill=(226, 220, 208), outline=(150, 140, 130))
    d.ellipse([x - 22, y - 12, x + 22, y + 12], fill=(236, 230, 218))
    for k in range(3): sparkle(L, x + rnd.randint(-26, 26), y + rnd.randint(-16, 10), t + k, (255, 220, 80))
# ------------------------------------------------------------------ agrandissement + interface HD
_hf = {}
def hfont(px, name="LilitaOne-Regular.ttf"):
    k = (px, name)
    if k not in _hf:
        p = os.path.join(FONTS, name)
        if not os.path.exists(p): p = os.path.join("/tmp/edu-assets/fonts", name)
        _hf[k] = ImageFont.truetype(p, px)
    return _hf[k]
def upscale(L): return L.convert("RGB").resize((W, H), Image.NEAREST)
def glow(im, x, y, r, col, a=.35):
    """Halo lumineux doux (projecteur, lampe) par-dessus l'image agrandie."""
    ov = Image.new("RGBA", (r*2, r*2), (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse([0, 0, r*2, r*2], fill=col + (int(255*a),))
    ov = ov.filter(ImageFilter.GaussianBlur(r//3)); im.paste(ov, (int(x - r), int(y - r)), ov)
def header(im, txt_a, txt_b, y=110):
    """En-tête d'épisode (petit, en police pixel) : « ÉP. 1 · DE ZÉRO À » + partie en jaune."""
    d = ImageDraw.Draw(im); f = hfont(34, "Silkscreen-Regular.ttf"); wa = f.getlength(txt_a + " "); wb = f.getlength(txt_b); x = W/2 - (wa + wb)/2
    d.text((x + 3, y + 3), txt_a, font=f, fill=(0, 0, 0)); d.text((x, y), txt_a, font=f, fill=(230, 232, 240))
    d.text((x + wa + 3, y + 3), txt_b, font=f, fill=(0, 0, 0)); d.text((x + wa, y), txt_b, font=f, fill=(255, 214, 64))
def caption_top(im, WD, t, y=230, emph=None, size=104, maxw=980):
    """Gros sous-titre en haut (2 lignes max), mots qui apparaissent au fil de la voix ; mots-clés en couleur (emph : mot -> couleur)."""
    if not hasattr(WD, "_cht"): WD._cht = WD.chunks(4)
    cur = [c for c in WD._cht if c[0] <= t < c[1]]
    if not cur: return
    t0, t1, toks = cur[-1]; f = hfont(size); d = ImageDraw.Draw(im); emph = emph or {}
    words = [tk[1].upper() for tk in toks]; ws = [f.getlength(w + " ") for w in words]
    lines, cl, cw = [], [], 0
    for i, w in enumerate(ws):
        if cl and cw + w > maxw: lines.append(cl); cl, cw = [], 0
        cl.append(i); cw += w
    lines.append(cl)
    import karaoke as KA
    for li, ids in enumerate(lines):
        tw = sum(ws[i] for i in ids); x = W/2 - tw/2; yy = y + li*int(size*1.05)
        for i in ids:
            tk = toks[i]
            if tk[3] <= t + .02:
                col = emph.get(KA.norm(tk[1]), (255, 255, 255)); pop = int(10*math.exp(-(t - tk[3])*16))
                d.text((x + 6, yy + 7 - pop), words[i], font=f, fill=(10, 10, 20)); d.text((x, yy - pop), words[i], font=f, fill=col)
            x += ws[i]
