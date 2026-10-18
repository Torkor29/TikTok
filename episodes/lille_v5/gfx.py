"""Assets graphiques papier de LOSC v5 (tous faits main en PIL, aucun ElevenLabs).
Chaque fonction renvoie un sprite RGBA (ancre = info["anchor"]) mis en cache. Audit : python3 gfx.py -> planche."""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from engine import paper_sprite, rect_pts, ellipse_pts, poly_pts, font, W, H, lerp, clamp
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np

NOIR = (28, 26, 30); BLANC = (250, 250, 246); ROUGE = (214, 16, 40); NAVY = (18, 30, 78); JAUNE = (255, 216, 58)
CREME = (244, 236, 216); SEPIA = (214, 190, 146); BOIS = (150, 98, 58); BOIS2 = (118, 74, 42); ARGENT = (204, 210, 218)
OR = (236, 186, 54); VERT = (58, 140, 76); VERT2 = (70, 156, 88); CIEL = (40, 70, 140)
A = lambda *p: os.path.join(ROOT, "assets", *p)

_C = {}
def cached(fn):
    def g(*a):
        k = (fn.__name__, a)
        if k not in _C: _C[k] = fn(*a)
        return _C[k]
    g.__name__ = fn.__name__
    return g

def seed_of(*a): return abs(hash(a)) % 9999
def pp(pts, fill, *key, **kw): return paper_sprite(pts, fill, seed=seed_of(*key), **kw)
def deco(spr, fn):
    """Dessine sur le sprite en coordonnées locales (0,0 = ancre)."""
    d = ImageDraw.Draw(spr); ax, ay = spr.info["anchor"]; fn(d, ax, ay); return spr
def center(spr, ax=None, ay=None):
    spr.info["anchor"] = (spr.width/2 if ax is None else ax, spr.height/2 if ay is None else ay); return spr
def text_c(d, x, y, txt, f, fill, anchor="mm"): d.text((x, y), txt, font=f, fill=fill, anchor=anchor)
def fsans(sz): return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", sz)

def sticker(name, h):
    p = A("logos", f"{name}_sticker.png")
    im = Image.open(p).convert("RGBA"); im = im.resize((int(im.width*h/im.height), h), Image.LANCZOS); return center(im)

# ------------------------------------------------------------------ fil rouge
@cached
def gauge_base():
    """Baromètre demi-lune 340x220 ; pivot = ancre."""
    R = 150; pts = [(R*math.cos(math.pi + math.pi*k/40), R*math.sin(math.pi + math.pi*k/40)) for k in range(41)] + [(R, 34), (-R, 34)]
    s = pp(pts, CREME, "gauge", rough=1.6)
    def f(d, ax, ay):
        cols = [(214, 40, 40), (232, 100, 44), (246, 180, 40), (170, 196, 60), (60, 160, 80)]
        for i, c in enumerate(cols):
            a0 = 180 + 36*i; d.arc([ax - 124, ay - 124, ax + 124, ay + 124], a0 + 1, a0 + 35, fill=c, width=30)
        for k in range(11):
            a = math.pi + math.pi*k/10; r0, r1 = 88, (100 if k % 5 else 108)
            d.line([(ax + r0*math.cos(a), ay + r0*math.sin(a)), (ax + r1*math.cos(a), ay + r1*math.sin(a))], fill=NOIR, width=4)
        text_c(d, ax, ay + 14, "SANTÉ DU CLUB", font("title", 26), NOIR)
    return deco(s, f)
@cached
def gauge_needle():
    im = Image.new("RGBA", (40, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(20, 6), (29, 112), (20, 124), (11, 112)], fill=NOIR)
    d.ellipse([6, 106, 34, 134], fill=ROUGE, outline=NOIR, width=3)
    im.info["anchor"] = (20, 120); return im

# ------------------------------------------------------------------ argent
@cached
def bill(v=0):
    s = pp(rect_pts(210, 100), (124, 190, 120), "bill", v, rough=1.2, pad=10)
    def f(d, ax, ay):
        d.rectangle([ax - 96, ay - 42, ax + 96, ay + 42], outline=(60, 120, 60), width=3)
        d.ellipse([ax - 30, ay - 30, ax + 30, ay + 30], outline=(60, 120, 60), width=4)
        text_c(d, ax, ay + 2, "€", fsans(40), (50, 110, 50))
        for sx in (-1, 1): text_c(d, ax + sx*70, ay - 22, "100", font("title", 26), (40, 96, 40))
    return deco(s, f)
@cached
def money_bag(h, label):
    w = h*.86
    pts = [(-w*.18, -h*.5), (w*.18, -h*.5), (w*.1, -h*.36), (w*.42, -h*.12), (w*.5, h*.18), (w*.4, h*.44), (0, h*.5), (-w*.4, h*.44), (-w*.5, h*.18), (-w*.42, -h*.12), (-w*.1, -h*.36)]
    s = pp(pts, (196, 160, 104), "bag", h, label, rough=1.8, hatch=True)
    def f(d, ax, ay):
        d.line([(ax - w*.16, ay - h*.36), (ax + w*.16, ay - h*.36)], fill=(120, 80, 40), width=max(3, int(h*.03)))
        text_c(d, ax, ay + h*.12, "€", fsans(int(h*.36)), (90, 60, 30))
        if label: text_c(d, ax, ay - h*.16, label, font("title", int(h*.12)), (90, 60, 30))
    return deco(s, f)

# ------------------------------------------------------------------ calendrier
@cached
def cal_back():
    s = pp(rect_pts(560, 600), (60, 56, 64), "calb", rough=1.2)
    def f(d, ax, ay):
        for i in range(7):
            x = ax - 210 + i*70; d.ellipse([x - 10, ay - 290, x + 10, ay - 270], fill=(30, 28, 32))
    return deco(s, f)
@cached
def cal_page(month, year, red=False):
    s = pp(rect_pts(520, 540), BLANC, "calp", month, year, rough=1.0, shadow=False)
    def f(d, ax, ay):
        d.rectangle([ax - 260, ay - 270, ax + 260, ay - 150], fill=ROUGE if red else NAVY)
        text_c(d, ax, ay - 210, month, font("title", 84), BLANC)
        text_c(d, ax, ay + 20, year, font("title", 190), NOIR)
        for i in range(7):
            x = ax - 210 + i*70; d.ellipse([x - 9, ay - 262, x + 9, ay - 244], fill=(60, 56, 64))
        for r in range(2):
            for c in range(7):
                x, y = ax - 210 + c*70, ay + 170 + r*44; d.rectangle([x - 22, y - 14, x + 22, y + 14], outline=(200, 200, 200), width=2)
    return deco(s, f)

# ------------------------------------------------------------------ trophées
@cached
def trophy_league(h=520):
    """Grand trophée argent stylisé (coupe à facettes sur double socle) — générique, pas une reproduction."""
    k = h/520; W_, H_ = int(380*k), int(560*k); im = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); cx = W_//2
    def paste(sp, x, y): ax, ay = sp.info["anchor"]; im.alpha_composite(sp, (int(x - ax), int(y - ay)))
    base2 = pp(rect_pts(250*k, 50*k), (44, 44, 52), "tb2", h, rough=.8)
    base1 = pp(rect_pts(190*k, 60*k), (70, 70, 80), "tb1", h, rough=.8)
    stem = pp([(-26*k, -70*k), (26*k, -70*k), (44*k, 70*k), (-44*k, 70*k)], (176, 182, 194), "tst", h, rough=.8)
    knot = pp(ellipse_pts(110*k, 40*k, 24), (196, 202, 212), "tkn", h, rough=.6)
    bowl = pp([(-150*k, -150*k), (-120*k, -168*k), (120*k, -168*k), (150*k, -150*k), (128*k, -20*k), (70*k, 80*k), (-70*k, 80*k), (-128*k, -20*k)],
              ARGENT, "tbw", h, rough=.8)
    paste(base2, cx, 520*k); paste(base1, cx, 468*k); paste(stem, cx, 370*k); paste(knot, cx, 300*k); paste(bowl, cx, 200*k)
    d = ImageDraw.Draw(im); y0 = 200*k
    d.polygon([(cx - 100*k, y0 - 150*k), (cx - 62*k, y0 - 150*k), (cx - 40*k, y0 + 60*k), (cx - 66*k, y0 + 50*k)], fill=(240, 244, 250))
    d.polygon([(cx + 60*k, y0 - 150*k), (cx + 130*k, y0 - 150*k), (cx + 110*k, y0 - 10*k), (cx + 56*k, y0 + 70*k)], fill=(160, 166, 180))
    d.line([(cx - 148*k, y0 - 150*k), (cx + 148*k, y0 - 150*k)], fill=(240, 244, 250), width=int(8*k))
    for sx in (-1, 1): d.arc([cx + sx*150*k - 46*k, y0 - 120*k, cx + sx*150*k + 46*k, y0 + 10*k], 270 if sx > 0 else 90, 90 if sx > 0 else 270, fill=(170, 176, 190), width=int(14*k))
    text_c(d, cx, 468*k, "CHAMPION", font("title", int(28*k)), (230, 230, 236))
    return center(im, cx, H_ - 8)
@cached
def cup_gold(h=420):
    k = h/420; W_, H_ = int(380*k), int(440*k); im = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); cx = W_//2
    bowl = pp([(-120*k, -150*k), (120*k, -150*k), (100*k, 0), (50*k, 50*k), (-50*k, 50*k), (-100*k, 0)], OR, "cup", h, rough=1.0)
    stem = pp(rect_pts(40*k, 90*k), (210, 160, 40), "cstem", h, rough=1.0)
    base = pp(rect_pts(190*k, 60*k), (120, 80, 40), "cbase", h, rough=1.0)
    def paste(sp, x, y): ax, ay = sp.info["anchor"]; im.alpha_composite(sp, (int(x - ax), int(y - ay)))
    d = ImageDraw.Draw(im)
    for sx in (-1, 1):
        d.arc([cx + sx*120*k - 60*k, 70*k, cx + sx*120*k + 60*k, 200*k], 90 if sx < 0 else 270, 270 if sx < 0 else 90, fill=(200, 150, 30), width=int(16*k))
    paste(stem, cx, 290*k); paste(base, cx, 380*k); paste(bowl, cx, 170*k)
    d = ImageDraw.Draw(im)
    d.polygon([(cx - 80*k, 40*k), (cx - 50*k, 40*k), (cx - 30*k, 200*k), (cx - 55*k, 190*k)], fill=(252, 226, 130))
    text_c(d, cx, 380*k, "COUPE", font("title", int(32*k)), (250, 220, 150))
    return center(im, cx, H_ - 20)

# ------------------------------------------------------------------ classement / étiquettes
@cached
def table_row(rank, name, pts, col, logo):
    s = pp(rect_pts(800, 128), BLANC, "row", name, rough=1.2)
    def f(d, ax, ay):
        d.rectangle([ax - 400, ay - 64, ax - 290, ay + 64], fill=col)
        if rank: text_c(d, ax - 345, ay, str(rank), font("title", 84), BLANC)
        text_c(d, ax - 60, ay, name, font("title", 76), NOIR)
        d.rectangle([ax + 230, ay - 50, ax + 380, ay + 50], fill=(236, 230, 214))
        if pts: text_c(d, ax + 305, ay, str(pts), font("title", 72), NOIR)
    s = deco(s, f); lg = sticker(logo, 96); ax, ay = s.info["anchor"]
    s.alpha_composite(lg, (int(ax - 230 - lg.width/2), int(ay - lg.height/2))); return s
@cached
def pin_tag(txt, size=58):
    f_ = font("title", size); tw = f_.getlength(txt)
    s = pp(rect_pts(tw + 60, size*1.5), BLANC, "pin", txt, rough=1.4)
    def f(d, ax, ay):
        text_c(d, ax, ay + 4, txt, f_, NOIR)
        d.ellipse([ax - 16, ay - size*.75 - 22, ax + 16, ay - size*.75 + 10], fill=ROUGE, outline=(120, 10, 20), width=3)
        d.ellipse([ax - 7, ay - size*.75 - 14, ax + 1, ay - size*.75 - 6], fill=(255, 160, 170))
    return deco(s, f)

# ------------------------------------------------------------------ 1944
@cached
def pennant(txt, col, flip=False):
    L = 560; pts = [(0, -130), (L, 0), (0, 130)]
    s = pp(pts, col, "pen", txt, rough=1.6, hatch=True)
    s = deco(s, lambda d, ax, ay: d.rectangle([ax - 22, ay - 160, ax - 4, ay + 260], fill=BOIS2))
    if flip:
        ax, ay = s.info["anchor"]; s = s.transpose(Image.FLIP_LEFT_RIGHT); s.info["anchor"] = (s.width - ax, ay)
    sg = -1 if flip else 1
    def f(d, ax, ay):
        lines = txt.split("\n")
        for i, l in enumerate(lines): text_c(d, ax + sg*190, ay - 30*(len(lines) - 1) + 60*i, l, font("title", 50), BLANC)
    return deco(s, f)
@cached
def bolt():
    pts = [(30, -170), (-60, 10), (0, 10), (-40, 170), (70, -30), (8, -30), (60, -170)]
    return pp(pts, JAUNE, "bolt", rough=1.2)
@cached
def paw():
    im = Image.new("RGBA", (120, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = (60, 30, 30)
    d.ellipse([30, 52, 90, 108], fill=c)
    for x, y in ((22, 30), (46, 14), (74, 14), (98, 30)): d.ellipse([x - 13, y - 13, x + 13, y + 15], fill=c)
    return center(im)

# ------------------------------------------------------------------ étagère
@cached
def shelf(txt="1946"):
    s = pp(rect_pts(860, 50), BOIS, "shelf", rough=1.2, hatch=True)
    def f(d, ax, ay):
        for sx in (-1, 1): d.polygon([(ax + sx*300, ay + 22), (ax + sx*300, ay + 120), (ax + sx*250, ay + 22)], fill=BOIS2)
        d.rectangle([ax - 90, ay + 30, ax + 90, ay + 84], fill=OR, outline=(150, 110, 30), width=3)
        text_c(d, ax, ay + 57, txt, font("title", 40), (90, 60, 20))
    return deco(s, f)

# ------------------------------------------------------------------ naufrage
def wave_strip(cv, y, t, col, amp=22, period=170, speed=60, phase=0.0, bottom=None):
    bottom = H + 20 if bottom is None else bottom
    d = ImageDraw.Draw(cv); pts = [(-20, bottom)]
    for x in range(-20, W + 40, 10):
        pts.append((x, y + amp*math.sin((x + t*speed)/period*2*math.pi + phase) + 6*math.sin(x/37 + phase)))
    pts.append((W + 40, bottom)); d.polygon(pts, fill=col)
    d.line(pts[1:-1], fill=tuple(min(255, c + 40) for c in col), width=5)
@cached
def boat():
    hull = [(-230, -20), (230, -20), (160, 90), (-160, 90)]
    s = pp(hull, BLANC, "hull", rough=1.4)
    sail = pp([(0, -300), (170, -30), (-10, -30)], (236, 232, 222), "sail", rough=1.4)
    im = Image.new("RGBA", (520, 460), (0, 0, 0, 0))
    def paste(sp, x, y): ax, ay = sp.info["anchor"]; im.alpha_composite(sp, (int(x - ax), int(y - ay)))
    paste(sail, 250, 330); paste(s, 260, 350)
    lg = sticker("lille", 120); im.alpha_composite(lg, (int(260 - lg.width/2), int(370 - lg.height/2)))
    return center(im, 260, 420)
@cached
def sign(txt, w_=380):
    s = pp(rect_pts(w_, 130), BOIS, "sign", txt, rough=1.6, hatch=True)
    def f(d, ax, ay):
        d.rectangle([ax - 14, ay + 60, ax + 14, ay + 260], fill=BOIS2)
        text_c(d, ax, ay, txt, font("title", 58), (250, 236, 210))
    return deco(s, f)

# ------------------------------------------------------------------ manivelle / projecteurs
@cached
def winch():
    """Treuil en bois : deux montants en A + tambour (la manivelle est dessinée à part : winch_handle)."""
    im = Image.new("RGBA", (340, 330), (0, 0, 0, 0)); cx = 170
    def paste(sp, x, y): ax, ay = sp.info["anchor"]; im.alpha_composite(sp, (int(x - ax), int(y - ay)))
    for sx in (-1, 1):
        paste(pp([(-14, -120), (14, -120), (50, 130), (24, 130), (0, -60), (-24, 130), (-50, 130)], BOIS, "wl", sx, rough=1.2, hatch=True), cx + sx*120, 180)
    drum = pp(rect_pts(250, 90), (170, 120, 70), "wd", rough=1.0, hatch=True)
    paste(drum, cx, 90)
    d = ImageDraw.Draw(im)
    for k in range(7): d.line([(cx - 110, 58 + k*11), (cx + 110, 58 + k*11)], fill=(200, 180, 140), width=4)
    return center(im, cx, 90)
@cached
def winch_handle():
    im = Image.new("RGBA", (40, 220), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([12, 10, 28, 120], 6, fill=(80, 82, 92)); d.rounded_rectangle([4, 110, 36, 210], 12, fill=ROUGE, outline=(120, 10, 20), width=3)
    im.info["anchor"] = (20, 14); return im

# ------------------------------------------------------------------ formation
@cached
def cone():
    s = pp([(-34, 40), (-8, -50), (8, -50), (34, 40)], (250, 130, 30), "cone", rough=1.0)
    def f(d, ax, ay): d.polygon([(ax - 22, ay), (ax + 22, ay), (ax + 18, ay - 14), (ax - 18, ay - 14)], fill=BLANC)
    return deco(s, f)
def flag_belgium(cv, x, y, t, s=1.0):
    """Drapeau belge qui flotte (bandes verticales noir/jaune/rouge), mât à gauche."""
    d = ImageDraw.Draw(cv); w_, h_ = 210*s, 140*s
    d.rectangle([x - 10*s, y - 10*s, x, y + 330*s], fill=(80, 70, 60))
    cols = [(30, 28, 28), (250, 210, 40), (220, 30, 40)]
    for i, c in enumerate(cols):
        x0, x1 = x + i*w_/3, x + (i + 1)*w_/3; pts = []
        for xx in np.linspace(x0, x1, 8): pts.append((xx, y + 10*s*math.sin(t*6 + xx/40) * (xx - x)/w_))
        for xx in np.linspace(x1, x0, 8): pts.append((xx, y + h_ + 10*s*math.sin(t*6 + xx/40) * (xx - x)/w_))
        d.polygon(pts, fill=c)

# ------------------------------------------------------------------ cadeau / ballon / vente
@cached
def gift_box():
    s = pp(rect_pts(300, 220), ROUGE, "gift", rough=1.2)
    def f(d, ax, ay): d.rectangle([ax - 22, ay - 110, ax + 22, ay + 110], fill=JAUNE)
    return deco(s, f)
@cached
def gift_lid():
    s = pp(rect_pts(330, 70), (190, 10, 30), "lid", rough=1.2, pad=110)
    def f(d, ax, ay):
        d.rectangle([ax - 24, ay - 35, ax + 24, ay + 35], fill=JAUNE)
        for sx in (-1, 1): d.ellipse([ax + sx*60 - 50, ay - 90, ax + sx*60 + 50, ay - 30], outline=JAUNE, width=16)
    return deco(s, f)
@cached
def balloon():
    s = pp(ellipse_pts(400, 470, 48), (220, 30, 44), "balloon", rough=.6)
    def f(d, ax, ay):
        d.ellipse([ax - 130, ay - 180, ax - 60, ay - 70], fill=(250, 120, 130))
        d.polygon([(ax - 18, ay + 236), (ax + 18, ay + 236), (ax, ay + 212)], fill=(170, 20, 30))
        text_c(d, ax, ay + 10, "DETTES", font("title", 92), BLANC)
    return deco(s, f)
@cached
def hammer():
    im = Image.new("RGBA", (260, 320), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([118, 70, 142, 310], 8, fill=(170, 120, 70), outline=(110, 70, 40), width=3)
    d.rounded_rectangle([40, 20, 220, 90], 10, fill=(90, 94, 104), outline=(50, 52, 60), width=4)
    im.info["anchor"] = (130, 300); return im
@cached
def beacon():
    s = pp(ellipse_pts(150, 130, 30), (230, 40, 40), "beacon", rough=.8)
    def f(d, ax, ay): d.rectangle([ax - 90, ay + 40, ax + 90, ay + 70], fill=(50, 50, 56))
    return deco(s, f)

# ------------------------------------------------------------------ terrain / banc / balance
@cached
def bench():
    """Banc de touche : dossier + assise bleus, pieds métal (ancre = milieu de l'assise)."""
    im = Image.new("RGBA", (640, 300), (0, 0, 0, 0)); cx = 320
    def paste(sp, x, y): ax, ay = sp.info["anchor"]; im.alpha_composite(sp, (int(x - ax), int(y - ay)))
    d = ImageDraw.Draw(im)
    for sx in (-1, 1): d.rectangle([cx + sx*250 - 9, 60, cx + sx*250 + 9, 280], fill=(70, 72, 80))
    paste(pp(rect_pts(580, 70), (34, 70, 150), "bback", rough=1.0, hatch=True), cx, 70)
    paste(pp(rect_pts(600, 50), (44, 86, 176), "bseat", rough=1.0, hatch=True), cx, 190)
    d = ImageDraw.Draw(im); d.text((cx, 70), "LOSC", font=font("title", 44), fill=(220, 230, 250), anchor="mm")
    return center(im, cx, 190)
@cached
def clipboard():
    s = pp(rect_pts(110, 150), (200, 160, 110), "clip", rough=1.0)
    def f(d, ax, ay):
        d.rectangle([ax - 40, ay - 50, ax + 40, ay + 60], fill=BLANC)
        for k in range(4): d.line([(ax - 30, ay - 30 + k*24), (ax + 30, ay - 30 + k*24)], fill=(120, 120, 140), width=3)
        d.rectangle([ax - 22, ay - 82, ax + 22, ay - 64], fill=(90, 90, 100))
    return deco(s, f)
@cached
def scale_stand():
    s = pp([(-30, -330), (30, -330), (30, 120), (140, 160), (140, 190), (-140, 190), (-140, 160), (-30, 120)], (120, 80, 50), "stand", rough=1.2, hatch=True)
    return s
@cached
def scale_beam():
    s = pp(rect_pts(760, 34), (150, 104, 60), "beam", rough=1.0)
    def f(d, ax, ay): d.ellipse([ax - 26, ay - 26, ax + 26, ay + 26], fill=OR, outline=(140, 100, 30), width=4)
    return deco(s, f)
@cached
def scale_pan():
    s = pp([(-150, 0), (150, 0), (110, 46), (-110, 46)], (200, 170, 90), "pan", rough=1.0)
    return s

# ------------------------------------------------------------------ fin
@cached
def bubble():
    s = pp([(-300, -110), (300, -110), (300, 110), (-120, 110), (-200, 190), (-190, 110), (-300, 110)], BLANC, "bubble", rough=1.0)
    return s
@cached
def spark(r=120):
    pts = []
    for k in range(16):
        a = k*math.pi/8; rr = r if k % 2 == 0 else r*.32; pts.append((rr*math.cos(a), rr*math.sin(a)))
    return pp(pts, (255, 236, 150), "spark", r, rough=.8)
@cached
def qmark():
    im = Image.new("RGBA", (420, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = font("title", 520)
    d.text((216, 300), "?", font=f, fill=(20, 16, 18), anchor="mm"); d.text((204, 286), "?", font=f, fill=JAUNE, anchor="mm")
    return center(im)

# ------------------------------------------------------------------ audit
if __name__ == "__main__":
    items = [("gauge", gauge_base()), ("needle", gauge_needle()), ("bill", bill()), ("bag PSG", money_bag(300, "PSG")), ("bag LOSC", money_bag(150, "LOSC")),
             ("cal back", cal_back()), ("cal DÉC", cal_page("DÉC.", "2020", True)), ("cal MAI", cal_page("MAI", "2021")),
             ("trophée L1", trophy_league(420)), ("coupe", cup_gold(360)), ("row LOSC", table_row(1, "LOSC", 83, ROUGE, "lille")),
             ("row PSG", table_row(2, "PSG", 82, NAVY, "psg")), ("pin", pin_tag("NEYMAR")), ("fanion OL", pennant("OLYMPIQUE\nLILLOIS", ROUGE)),
             ("fanion Fives", pennant("SC FIVES", NAVY, True)), ("éclair", bolt()), ("patte", paw()), ("étagère", shelf()), ("bateau", boat()),
             ("panneau D2", sign("DIVISION 2")), ("treuil", winch()), ("manivelle", winch_handle()), ("plot", cone()), ("cadeau", gift_box()), ("couvercle", gift_lid()),
             ("ballon", balloon()), ("marteau", hammer()), ("à vendre", sign("À VENDRE", 420)), ("gyrophare", beacon()), ("banc", bench()),
             ("plaquette", clipboard()), ("pied balance", scale_stand()), ("fléau", scale_beam()), ("plateau", scale_pan()), ("bulle", bubble()),
             ("étincelle", spark()), ("?", qmark())]
    cols = 6; cw, ch = 600, 640; rows = (len(items) + cols - 1)//cols
    for bgname, bg in (("clair", (238, 230, 212)), ("fonce", (24, 22, 30))):
        sheet = Image.new("RGB", (cols*cw, rows*ch), bg); d = ImageDraw.Draw(sheet)
        for i, (nm, sp) in enumerate(items):
            x, y = (i % cols)*cw, (i//cols)*ch; k = min(1, (cw - 40)/sp.width, (ch - 90)/sp.height)
            im = sp.resize((max(1, int(sp.width*k)), max(1, int(sp.height*k))), Image.LANCZOS)
            sheet.paste(im, (x + (cw - im.width)//2, y + 60 + (ch - 90 - im.height)//2), im)
            d.text((x + 14, y + 10), nm, font=fsans(34), fill=(200, 60, 60))
        out = f"/tmp/claude-0/aud/gfx_{bgname}.jpg"; sheet.resize((sheet.width//2, sheet.height//2)).save(out, quality=85); print(out)
