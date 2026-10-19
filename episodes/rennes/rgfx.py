"""Assets papier spécifiques à l'épisode Rennes (en plus de lille_v5/gfx.py). python3 rgfx.py -> planche d'audit."""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "lille_v5"))
from gfx import *
from engine import blit_sxy

RR = (214, 26, 34); RN = (24, 22, 26)

@cached
def badge(h=520):
    """Badge papier maison (PAS l'écusson officiel) : bouclier noir, bandeau rouge, hermine bretonne, 1901."""
    k = h/520
    pts = [(-200*k, -240*k), (200*k, -240*k), (200*k, 60*k), (0, 250*k), (-200*k, 60*k)]
    s = pp(pts, RN, "badge", h, rough=1.0)
    def f(d, ax, ay):
        d.polygon([(ax - 186*k, ay - 226*k), (ax + 186*k, ay - 226*k), (ax + 186*k, ay - 120*k), (ax - 186*k, ay - 120*k)], fill=RR)
        text_c(d, ax, ay - 173*k, "STADE RENNAIS", font("title", int(46*k)), BLANC)
        # hermine (motif breton) stylisée
        cx, cy = ax, ay - 10*k
        d.ellipse([cx - 16*k, cy - 70*k, cx + 16*k, cy - 38*k], fill=BLANC)
        for sx in (-1, 1): d.ellipse([cx + sx*34*k - 12*k, cy - 54*k, cx + sx*34*k + 12*k, cy - 30*k], fill=BLANC)
        d.polygon([(cx, cy - 40*k), (cx + 40*k, cy + 70*k), (cx, cy + 50*k), (cx - 40*k, cy + 70*k)], fill=BLANC)
        text_c(d, ax, ay + 120*k, "1901", font("title", int(56*k)), RR)
    return deco(s, f)

# ------------------------------------------------------------------ tableau d'affichage à palettes
@cached
def board_base(w=860, h=330, left="RENNES", right="PSG"):
    s = pp(rect_pts(w, h), (36, 36, 42), "board", left, right, rough=.8)
    def f(d, ax, ay):
        for x, nm in ((ax - w*.3, left), (ax + w*.3, right)): text_c(d, x, ay - h*.32, nm, font("title", 54), (250, 220, 120))
    return deco(s, f)
def flip_digit(cv, x, y, val, t, t_change, prev, size=150):
    """Chiffre à palette : la moitié haute bascule (0,18 s) lors d'un changement."""
    w_, h_ = size*.8, size*1.1; d = ImageDraw.Draw(cv)
    u = clamp((t - t_change)/.18) if t >= t_change else 1
    shown = val if t >= t_change + .09 else prev
    d.rounded_rectangle([x - w_/2, y - h_/2, x + w_/2, y + h_/2], 12, fill=(16, 16, 20))
    text_c(d, x, y, str(shown), font("title", size), (252, 252, 246))
    d.line([(x - w_/2, y), (x + w_/2, y)], fill=(50, 50, 56), width=4)
    if u < 1:
        ph = abs(math.cos(math.pi*u)); top = y - h_/2*ph
        d.rectangle([x - w_/2, top, x + w_/2, y], fill=(30, 30, 36))
def board_score(cv, x, y, t, seq, size=150):
    """seq = [(t, gauche, droite)] ; dessine les deux chiffres avec bascule."""
    L, R, pL, pR, tl, tr = 0, 0, 0, 0, -9, -9
    for (ti, a, b) in seq:
        if t >= ti:
            if a != L: pL, L, tl = L, a, ti
            if b != R: pR, R, tr = R, b, ti
    flip_digit(cv, x - 210, y, L, t, tl, pL, size); flip_digit(cv, x + 210, y, R, t, tr, pR, size)
    ImageDraw.Draw(cv).rectangle([x - 34, y - 10, x + 34, y + 10], fill=(250, 220, 120))

# ------------------------------------------------------------------ malédiction
def cobweb(cv, x, y, r, u, col=(236, 236, 236)):
    """Toile d'araignée qui se tisse (u 0->1) depuis un coin (x, y)."""
    if u <= 0: return
    d = ImageDraw.Draw(cv); n = 7; rr = r*u
    for k in range(n):
        a = math.pi/2*k/(n - 1); d.line([(x, y), (x + rr*math.cos(a), y + rr*math.sin(a))], fill=col, width=3)
    for ring in range(1, 6):
        rk = rr*ring/5; pts = [(x + rk*math.cos(math.pi/2*k/(n - 1)), y + rk*math.sin(math.pi/2*k/(n - 1))) for k in range(n)]
        d.line(pts, fill=col, width=2)
@cached
def black_cat():
    im = Image.new("RGBA", (420, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = (18, 16, 20)
    d.ellipse([90, 120, 330, 230], fill=c)                              # corps
    d.ellipse([280, 70, 390, 170], fill=c)                              # tête
    d.polygon([(292, 92), (300, 30), (330, 80)], fill=c); d.polygon([(350, 78), (378, 28), (384, 100)], fill=c)
    for x in (130, 170, 250, 290): d.rounded_rectangle([x, 200, x + 22, 290], 10, fill=c)
    d.line([(100, 160), (40, 120), (20, 40), (50, 20)], fill=c, width=22, joint="curve")
    for x in (318, 356): d.ellipse([x, 108, x + 18, 126], fill=(250, 220, 60)); d.ellipse([x + 6, 110, x + 12, 124], fill=c)
    im.info["anchor"] = (210, 290); return im
@cached
def door(txt="LIGUE"):
    s = pp(rect_pts(420, 760), (150, 98, 58), "door", txt, rough=1.0, hatch=True)
    def f(d, ax, ay):
        for yy in (-250, 60): d.rectangle([ax - 160, ay + yy - 120, ax + 160, ay + yy + 120], outline=(110, 70, 40), width=8)
        d.ellipse([ax + 140, ay + 10, ax + 176, ay + 46], fill=OR)
        d.rectangle([ax - 140, ay - 300, ax + 140, ay - 210], fill=BLANC); text_c(d, ax, ay - 255, txt, font("title", 64), NOIR)
    return deco(s, f)
@cached
def crown():
    pts = [(-120, 60), (-120, -20), (-70, 20), (0, -70), (70, 20), (120, -20), (120, 60)]
    s = pp(pts, OR, "crown", rough=.8)
    def f(d, ax, ay):
        for x in (-60, 0, 60): d.ellipse([ax + x - 12, ay + 22, ax + x + 12, ay + 46], fill=ROUGE)
    return deco(s, f)
def flag_civ(cv, x, y, t, s=1.0):
    d = ImageDraw.Draw(cv); w_, h_ = 210*s, 140*s
    d.rectangle([x - 10*s, y - 10*s, x, y + 330*s], fill=(80, 70, 60))
    for i, c in enumerate([(247, 127, 0), (250, 250, 246), (0, 158, 96)]):
        x0, x1 = x + i*w_/3, x + (i + 1)*w_/3; pts = []
        for xx in np.linspace(x0, x1, 8): pts.append((xx, y + 10*s*math.sin(t*6 + xx/40)*(xx - x)/w_))
        for xx in np.linspace(x1, x0, 8): pts.append((xx, y + h_ + 10*s*math.sin(t*6 + xx/40)*(xx - x)/w_))
        d.polygon(pts, fill=c)
@cached
def boater():
    """Canotier (chapeau de paille) des étudiants de 1901."""
    s = pp(ellipse_pts(200, 46, 30), (226, 196, 120), "boater", rough=.8)
    def f(d, ax, ay):
        d.rectangle([ax - 64, ay - 60, ax + 64, ay - 4], fill=(226, 196, 120)); d.rectangle([ax - 64, ay - 26, ax + 64, ay - 8], fill=RR)
    return deco(s, f)

# ------------------------------------------------------------------ CTA
@cached
def sub_button(pressed=False):
    s = pp(rect_pts(560, 150), (230, 30, 70) if not pressed else (150, 150, 160), "sub", pressed, rough=1.0)
    def f(d, ax, ay): text_c(d, ax, ay + 4, "S'ABONNER" if not pressed else "ABONNÉ ✓", font("title", 72) if not pressed else fsans(60), BLANC)
    return deco(s, f)
@cached
def heart(r=120, col=(240, 40, 80)):
    pts = []
    for k in range(60):
        a = 2*math.pi*k/60; x = 16*math.sin(a)**3; y = -(13*math.cos(a) - 5*math.cos(2*a) - 2*math.cos(3*a) - math.cos(4*a))
        pts.append((x*r/16, y*r/16))
    return pp(pts, col, "heart", r, col, rough=.8)
@cached
def finger():
    s = pp([(-30, -110), (30, -110), (34, 40), (80, 60), (80, 160), (-80, 160), (-80, 40), (-34, 40)], (240, 200, 170), "finger", rough=1.0)
    return s

# ------------------------------------------------------------------ Guingamp / Camavinga / finale
@cached
def tractor():
    im = Image.new("RGBA", (460, 320), (0, 0, 0, 0))
    def paste(sp, x, y): ax, ay = sp.info["anchor"]; im.alpha_composite(sp, (int(x - ax), int(y - ay)))
    paste(pp(rect_pts(260, 120), RR, "tbody", rough=1.0), 200, 160); paste(pp(rect_pts(120, 130), RN, "tcab", rough=1.0), 290, 90)
    d = ImageDraw.Draw(im)
    d.ellipse([60, 170, 200, 310], fill=RN); d.ellipse([105, 215, 155, 265], fill=(150, 150, 150))
    d.ellipse([300, 220, 390, 310], fill=RN); d.ellipse([330, 250, 360, 280], fill=(150, 150, 150))
    d.rectangle([110, 60, 126, 110], fill=(60, 60, 60))
    im.info["anchor"] = (230, 310); return im
@cached
def tent():
    s = pp([(0, -200), (230, 120), (-230, 120)], (120, 140, 120), "tent", rough=1.4, hatch=True)
    def f(d, ax, ay): d.polygon([(ax, ay - 120), (ax + 60, ay + 120), (ax - 60, ay + 120)], fill=(60, 70, 60))
    return deco(s, f)
@cached
def house():
    s = pp([(-200, -40), (0, -220), (200, -40), (200, 220), (-200, 220)], (236, 222, 196), "house", rough=1.0)
    def f(d, ax, ay):
        d.polygon([(ax - 220, ay - 30), (ax, ay - 240), (ax + 220, ay - 30)], fill=(170, 70, 50))
        d.rectangle([ax - 140, ay + 20, ax - 60, ay + 100], fill=(120, 180, 220)); d.rectangle([ax + 60, ay + 20, ax + 140, ay + 100], fill=(120, 180, 220))
        d.rectangle([ax - 36, ay + 100, ax + 36, ay + 220], fill=(120, 80, 50))
    return deco(s, f)
def flames(cv, x, y, t, s=1.0, n=7):
    d = ImageDraw.Draw(cv)
    for k in range(n):
        ph = t*9 + k*1.7; h_ = (120 + 60*math.sin(ph))*s; xx = x + (k - n/2)*50*s
        for col, sc in (((255, 120, 20), 1.0), ((255, 210, 60), .6)):
            d.polygon([(xx - 36*s*sc, y), (xx + 36*s*sc, y), (xx + 8*s*math.sin(ph), y - h_*sc)], fill=col)
@cached
def red_card():
    s = pp(rect_pts(220, 300), (220, 20, 30), "redcard", rough=.6)
    return s
@cached
def closet():
    s = pp(rect_pts(380, 620), (120, 86, 60), "closet", rough=1.0, hatch=True)
    def f(d, ax, ay):
        d.rectangle([ax - 170, ay - 290, ax + 170, ay + 290], outline=(80, 56, 36), width=8)
        d.rectangle([ax - 120, ay - 240, ax + 120, ay - 180], fill=BLANC); text_c(d, ax, ay - 210, "PLACARD", font("title", 46), NOIR)
    return deco(s, f)
def pen_dots(cv, x, y, t, t0, res, step=.62, r=46, gap=118):
    """Rangée de tirs au but : res = [(t_i, 'ok'|'ko')] ; ronds qui se remplissent."""
    d = ImageDraw.Draw(cv)
    for i, (ti, rs) in enumerate(res):
        cx = x + (i - (len(res) - 1)/2)*gap
        d.ellipse([cx - r, y - r, cx + r, y + r], outline=BLANC, width=5)
        if t >= ti:
            u = eob_((t - ti)/.2); rr = r*u
            col = (60, 190, 90) if rs == "ok" else (220, 30, 40)
            d.ellipse([cx - rr, y - rr, cx + rr, y + rr], fill=col)
            if rs == "ko" and u > .8:
                d.line([(cx - 26, y - 26), (cx + 26, y + 26)], fill=BLANC, width=10); d.line([(cx - 26, y + 26), (cx + 26, y - 26)], fill=BLANC, width=10)
            elif u > .8: d.line([(cx - 24, y), (cx - 6, y + 20), (cx + 26, y - 20)], fill=BLANC, width=10)
def eob_(u):
    u = clamp(u); s = 1.9; u -= 1; return 1 + (s + 1)*u**3 + s*u**2

# ------------------------------------------------------------------ Bretagne
BZH = [(30, 250), (60, 200), (120, 170), (200, 150), (280, 120), (360, 140), (420, 110), (480, 150), (540, 190), (560, 230), (600, 200),
       (660, 170), (720, 180), (800, 170), (880, 190), (920, 260), (950, 360), (960, 460), (920, 560), (820, 600), (740, 610), (660, 600),
       (620, 620), (560, 600), (520, 640), (505, 670), (490, 600), (430, 580), (380, 570), (320, 560), (260, 540), (200, 520), (150, 470),
       (120, 480), (90, 430), (140, 400), (110, 370), (60, 360), (100, 330), (40, 300)]
CITIES = {"BREST": (120, 300), "GUINGAMP": (450, 230), "LORIENT": (400, 555), "RENNES": (800, 370)}
@cached
def bzh_map():
    s = pp([(x - 500, y - 370) for x, y in BZH], (236, 228, 206), "bzh", rough=1.6, hatch=True)
    def f(d, ax, ay):
        text_c(d, ax + 120, ay + 20, "BREIZH", font("title", 90), (214, 200, 170))
    return deco(s, f)

# ------------------------------------------------------------------ cartes photo
@cached
def photo_card(path, box, h=760, rot=0):
    """Photo fournie -> carte papier : recadrée, bord blanc déchiré, ombre (jamais brute)."""
    im = Image.open(path).convert("RGB").crop(box); k = (h - 60)/im.height; im = im.resize((int(im.width*k), int(im.height*k)), Image.LANCZOS)
    s = pp(rect_pts(im.width + 50, im.height + 50), BLANC, "card", path, rough=2.0)
    ax, ay = s.info["anchor"]; s.paste(im, (int(ax - im.width/2), int(ay - im.height/2)))
    return s

@cached
def ticket(t1, t2, col, wd=640):
    hg = int(wd*.36); s = pp(rect_pts(wd, hg), col, "ticket", t1, rough=1.0)
    def f(d, ax, ay):
        sx = ax + wd*.26
        for y in range(int(ay - hg/2) + 12, int(ay + hg/2) - 10, 22): d.line([(sx, y), (sx, y + 10)], fill=BLANC, width=4)
        text_c(d, ax - wd*.12, ay - hg*.12, t1, font("title", int(hg*.3)), BLANC)
        text_c(d, ax - wd*.12, ay + hg*.24, t2, font("mono", int(hg*.12)), (255, 236, 200))
        text_c(d, sx + wd*.12, ay, "N°19", font("mono", int(hg*.14)), BLANC)
    return deco(s, f)

UP = "/root/.claude/uploads/0adb781c-170c-5099-95c1-9e411610d456"
BENARFA = (os.path.join(UP, "6062cc1e-image.png"), (190, 905, 1000, 1660))
CAMA = (os.path.join(UP, "4d332df9-image.png"), (400, 850, 1100, 1715))

if __name__ == "__main__":
    cv = Image.new("RGBA", (2400, 2400), (238, 230, 212, 255)); d = ImageDraw.Draw(cv)
    items = [("badge", badge(), 300, 330), ("board", board_base(), 900, 250), ("chat", black_cat(), 1700, 330), ("porte", door(), 2150, 450),
             ("couronne", crown(), 300, 800), ("canotier", boater(), 650, 800), ("bouton", sub_button(), 1150, 800), ("bouton2", sub_button(True), 1150, 1000),
             ("coeur", heart(), 1700, 850), ("doigt", finger(), 2050, 850), ("tracteur", tractor(), 330, 1350), ("tente", tent(), 850, 1350),
             ("maison", house(), 1350, 1350), ("carton", red_card(), 1800, 1300), ("placard", closet(), 2150, 1500), ("bzh", bzh_map(), 600, 1950),
             ("ben arfa", photo_card(*BENARFA, 520), 1300, 2000), ("cama", photo_card(*CAMA, 520), 1800, 2000)]
    for nm, sp, x, y in items:
        blit_sxy(cv, sp, x, y, 1, 1, 0); d.text((x - 100, y - 280), nm, font=fsans(30), fill=(200, 40, 40))
    board_score(cv, 900, 300, 1.0, [(0, 2, 2)], 110); cobweb(cv, 1300, 120, 220, 1); flames(cv, 1350, 1200, 1.0)
    flag_civ(cv, 2250, 50, .5, .8); pen_dots(cv, 1700, 650, 9, 0, [(0, "ok")]*5 + [(0, "ko")])
    for c, (x, y) in CITIES.items(): d.ellipse([600 - 500 + x - 10, 1950 - 370 + y - 10, 600 - 500 + x + 10, 1950 - 370 + y + 10], fill=(200, 0, 0))
    out = "/tmp/claude-0/aud/rgfx.jpg"; cv.convert("RGB").resize((1200, 1200)).save(out, quality=85); print(out)
