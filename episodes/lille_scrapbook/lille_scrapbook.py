"""LOSC — version SCRAPBOOK SUR LE BUREAU (test A/B n°2, même voix que lille_histoire, 0 crédit). Voir SCRIPT.md.
Vue de dessus : bureau en bois, carnet à spirale ; les faits sont des OBJETS papier qui tombent sur la page
(facture, polaroïds, coupures, tickets, post-it, fiches, médaille) ; changement d'époque = la page se tourne.

  python3 episodes/lille_scrapbook/lille_scrapbook.py --stills
  python3 episodes/lille_scrapbook/lille_scrapbook.py output/lille_scrapbook
"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "brest_ldc"))
from quiz import *
from brest_ldc import _img, shake, big, marker, CREME, NOIR, BLANC, JAUNE
from PIL import ImageFilter

TITLE = "~/histoires $ ./losc"
SLUG = "lille_scrapbook"
SRC = os.path.join(ROOT, "episodes", "lille_histoire")
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
VOIX = os.path.join(SRC, "voix", "voix_complete.mp3")
TEXTE = open(os.path.join(SRC, "texte.txt")).read()
_W = json.load(open(os.path.join(SRC, "mots.json")))
def w(txt, n=1):
    k = 0
    for x in _W:
        if x["text"].strip(".,…!?:«» ").lower() == txt.lower():
            k += 1
            if k == n: return x["start"]
    raise KeyError(f"{txt} #{n}")
ROUGE = (220, 18, 38); NAVY = (16, 26, 70); ROSE = (255, 150, 180); NEWS = (232, 228, 214); OR = (232, 186, 52); VERT = (110, 186, 110)
A = lambda *p: os.path.join(ROOT, "assets", *p)

# ------------------------------------------------------------------ sprites papier
_cache = {}
def cached(fn):
    def g(*a):
        if (fn.__name__, a) not in _cache:
            im = fn(*a); im.info["anchor"] = (im.width/2, im.height/2)
            sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda v: v*120//255))
            sh = sh.filter(ImageFilter.GaussianBlur(9)); sh.info["anchor"] = im.info["anchor"]
            _cache[(fn.__name__, a)] = (im, sh)
        return _cache[(fn.__name__, a)]
    return g
def jag(w_, h_, seed, amp=7, n=18):
    r = random.Random(seed); pts = []
    for (x0, y0, x1, y1) in ((0, 0, w_, 0), (w_, 0, w_, h_), (w_, h_, 0, h_), (0, h_, 0, 0)):
        for k in range(n): u = k/n; pts.append((x0 + (x1 - x0)*u + r.uniform(-amp, amp), y0 + (y1 - y0)*u + r.uniform(-amp, amp)))
    return pts
def fit(path, w_, h_):
    im = Image.open(path).convert("RGBA"); k = min(w_/im.width, h_/im.height)
    return im.resize((max(1, int(im.width*k)), max(1, int(im.height*k))), Image.LANCZOS)
def text_c(d, txt, fnt, cx, y, fill, maxw):
    lines = []; cur = ""
    for wd in txt.split(" "):
        tt = (cur + " " + wd).strip()
        if fnt.getlength(tt) <= maxw or not cur: cur = tt
        else: lines.append(cur); cur = wd
    lines.append(cur); a, b = fnt.getmetrics()
    for l in lines: d.text((cx - fnt.getlength(l)/2, y), l, font=fnt, fill=fill); y += a + b
    return y

@cached
def polaroid(src, caption, wd):
    hg = int(wd*1.18); im = Image.new("RGBA", (wd, hg), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, wd - 1, hg - 1], fill=(250, 250, 244)); m = int(wd*.06); iw = wd - 2*m
    d.rectangle([m, m, m + iw, m + iw], fill=(226, 220, 204))
    ph = fit(src, iw - 20, iw - 20); im.alpha_composite(ph, (m + (iw - ph.width)//2, m + (iw - ph.height)//2))
    if caption: text_c(d, caption, font("brush", int(wd*.1)), wd/2, m + iw + int(wd*.02), (30, 30, 60), wd - 20)
    return im
@cached
def clipping(head, wd, size, kicker):
    f = font("title", size); tmp = Image.new("RGBA", (wd, 2000)); y = text_c(ImageDraw.Draw(tmp), head, f, wd/2, 70, NOIR, wd - 70)
    hg = y + 40 + 6*28 + 30; im = Image.new("RGBA", (wd, hg), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon(jag(wd, hg, hash(head) % 999), fill=NEWS)
    ks = font("mono", 24); d.text((wd/2 - ks.getlength(kicker)/2, 24), kicker, font=ks, fill=(90, 86, 80)); d.line([40, 60, wd - 40, 60], fill=(90, 86, 80), width=2)
    text_c(d, head, f, wd/2, 70, NOIR, wd - 70); r = random.Random(len(head))
    for k in range(6):
        yy = y + 40 + k*28
        for c in range(2):
            x0 = 40 + c*(wd - 80)//2 + 10; d.line([x0, yy, x0 + r.uniform(.6, .95)*((wd - 80)//2 - 30), yy], fill=(160, 156, 146), width=10)
    return im
@cached
def ticket(t1, t2, col, wd):
    hg = int(wd*.38); im = Image.new("RGBA", (wd, hg), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, wd - 1, hg - 1], 18, fill=col); sx = int(wd*.76)
    for y in range(14, hg - 10, 22): d.line([sx, y, sx, y + 10], fill=BLANC, width=4)
    for y in (0, hg): d.ellipse([sx - 22, y - 22, sx + 22, y + 22], fill=(0, 0, 0, 0))
    d.rectangle([14, 14, wd - 15, hg - 15], outline=(255, 255, 255, 120), width=3)
    text_c(d, t1, font("title", int(hg*.26)), sx/2, int(hg*.16), BLANC, sx - 40)
    text_c(d, t2, font("mono", int(hg*.12)), sx/2, int(hg*.68), (255, 240, 200), sx - 30)
    tt = font("mono", int(hg*.13)); d.text((sx + 30, hg/2 - 20), "N°44", font=tt, fill=BLANC)
    return im
@cached
def postit(txt, col, wd, size):
    im = Image.new("RGBA", (wd, wd), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, wd - 1, wd - 1], fill=col); d.rectangle([0, 0, wd - 1, int(wd*.12)], fill=tuple(max(0, c - 18) for c in col))
    sz = int(size*1.45)
    while True:
        f = font("brush", sz); tmp = text_c(ImageDraw.Draw(Image.new("RGBA", (wd, 3000))), txt, f, wd/2, 0, NOIR, wd - 50)
        if (max(f.getlength(x) for x in txt.split(" ")) <= wd - 50 and tmp <= wd - 70) or sz < 30: break
        sz -= 4
    text_c(d, txt, f, wd/2, (wd - tmp)/2 + 10, (20, 20, 30), wd - 50)
    return im
@cached
def fiche(name, role, wd):
    hg = int(wd*.5); im = Image.new("RGBA", (wd, hg), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, wd - 1, hg - 1], fill=(252, 252, 248))
    for y in range(int(hg*.42), hg, 34): d.line([0, y, wd, y], fill=(170, 196, 230), width=2)
    d.line([0, int(hg*.3), wd, int(hg*.3)], fill=ROUGE, width=3)
    text_c(d, name, font("title", int(hg*.2)), wd/2, int(hg*.04), NAVY, wd - 30)
    text_c(d, role, font("brush", int(hg*.2)), wd/2, int(hg*.45), (40, 40, 60), wd - 30)
    return im
@cached
def facture(wd):
    hg = int(wd*1.3); im = Image.new("RGBA", (wd, hg), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, wd - 1, hg - 1], fill=(250, 250, 246))
    text_c(d, "FACTURE", font("title", 86), wd/2, 40, NOIR, wd); d.text((40, 160), "Client : LOSC LILLE", font=font("mono", 30), fill=(60, 60, 60))
    for k, l in enumerate(["Salaires", "Transferts", "Emprunts", "Intérêts", "Retards"]):
        y = 250 + k*80; d.text((40, y), l, font=font("mono", 34), fill=(50, 50, 50)); d.text((wd - 200, y), "???", font=font("mono", 34), fill=(50, 50, 50))
        d.line([40, y + 56, wd - 40, y + 56], fill=(200, 200, 200), width=2)
    d.rectangle([30, hg - 200, wd - 30, hg - 60], outline=ROUGE, width=6)
    text_c(d, "TOTAL : IMPAYÉ", font("title", 64), wd/2, hg - 172, ROUGE, wd - 60)
    return im
@cached
def medal(r):
    im = Image.new("RGBA", (2*r + 40, 3*r + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im); cx = r + 20
    d.polygon([(cx - r*.6, 0), (cx - r*.05, 0), (cx + r*.1, r*1.3), (cx - r*.35, r*1.3)], fill=ROUGE)
    d.polygon([(cx + r*.05, 0), (cx + r*.6, 0), (cx + r*.35, r*1.3), (cx - r*.1, r*1.3)], fill=NAVY)
    y0 = r*1.1; d.ellipse([20, y0, 20 + 2*r, y0 + 2*r], fill=OR, outline=(170, 128, 30), width=10)
    d.ellipse([20 + r*.25, y0 + r*.25, 20 + r*1.75, y0 + r*1.75], outline=(250, 220, 120), width=6)
    text_c(d, "1er", font("title", int(r*.7)), cx, y0 + r*.48, (130, 92, 20), 2*r)
    return im
@cached
def billet(wd):
    hg = int(wd*.48); im = Image.new("RGBA", (wd, hg), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, wd - 1, hg - 1], fill=VERT, outline=(60, 120, 60), width=5); d.ellipse([wd/2 - hg*.3, hg*.2, wd/2 + hg*.3, hg*.8], outline=(60, 120, 60), width=5)
    d.text((16, 8), "100", font=font("title", int(hg*.3)), fill=(40, 90, 40)); return im
@cached
def tape(wd):
    im = Image.new("RGBA", (wd, int(wd*.32)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon(jag(wd, int(wd*.32), wd, 4, 6), fill=(240, 232, 200, 170)); return im
@cached
def sticker(name, h):
    return _img(A("logos", f"{name}_sticker.png"), h)[0].copy()

def drop(t, t0, d=.22):
    if t < t0: return None
    return 1 - ease_out_cubic(clamp((t - t0)/d))
def obj(L, t, t0, sp, x, y, rot=0.0, d=.22):
    lift = drop(t, t0, d)
    if lift is None: return False
    im, sh = sp; s = 1 + .35*lift; off = 12 + 60*lift
    blit_sxy(L, sh, x + off*.6, y + off, s*1.03, s*1.03, rot); blit_sxy(L, im, x, y, s, s, rot); return True
def lab(L, fr, t, t0, label, x, y, rot=0.0):
    lift = drop(t, t0)
    if lift is not None: label.draw(L, fr, x, y, 1 + .35*lift, rot)
def tp(L, t, t0, x, y, rot, wd=170): obj(L, t, t0 + .12, tape(wd), x, y, rot, .1)
def redline(L, t, t0, pts, wd=12, d=.35):   # feutre rouge qui se trace
    u = clamp((t - t0)/d)
    if u <= 0: return
    dr = ImageDraw.Draw(L); n = len(pts) - 1; m = u*n
    for k in range(int(math.ceil(m))):
        a, b = pts[k], pts[k + 1]; v = min(1, m - k); dr.line([a, (lerp(a[0], b[0], v), lerp(a[1], b[1], v))], fill=ROUGE, width=wd)
def circle_pts(cx, cy, rx, ry, n=30): return [(cx + rx*math.cos(-1.4 + 2.2*math.pi*k/n), cy + ry*math.sin(-1.4 + 2.2*math.pi*k/n)) for k in range(n + 1)]
def bills(L, fr, t, t0, n=10):
    for k in range(n):
        u = prog(t, t0 + k*.07, 1.3)
        if 0 < u < 1: blit_sxy(L, billet(170)[0], 100 + (k*173) % 880 + 60*math.sin(u*6 + k), 1950 - 1700*u, 1, 1, 25*math.sin(k + u*5))

# ------------------------------------------------------------------ décor
_desk = None
def desk():
    global _desk
    if _desk is None:
        im = Image.new("RGB", (W, H), (120, 80, 50)); d = ImageDraw.Draw(im); r = random.Random(5)
        for k in range(160):
            y = r.uniform(0, H); c = r.choice([(104, 68, 42), (134, 92, 58), (112, 74, 46)]); a = r.uniform(0, 6.28)
            d.line([(x, y + 14*math.sin(x/140 + a)) for x in range(0, W + 40, 40)], fill=c, width=r.randint(2, 7))
        for k in range(5): d.line([0, 380*k + 120, W, 380*k + 120], fill=(84, 54, 34), width=4)
        d.ellipse([820, 1640, 1040, 1860], outline=(96, 60, 36), width=14)      # trace de tasse
        _desk = im
    return _desk
PX0, PY0, PX1, PY1 = 70, 170, 1010, 1830
_page = None
def page_sprite():
    global _page
    if _page is None:
        wd, hg = PX1 - PX0, PY1 - PY0; im = Image.new("RGBA", (wd + 60, hg + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([30, 40, wd + 40, hg + 50], fill=(0, 0, 0, 120)); sh = sh.filter(ImageFilter.GaussianBlur(14))
        im.alpha_composite(sh); d.rectangle([20, 20, wd + 20, hg + 20], fill=(246, 240, 224))
        for y in range(150, hg, 64): d.line([20, 20 + y, wd + 20, 20 + y], fill=(176, 198, 226), width=3)
        d.line([140, 20, 140, hg + 20], fill=(226, 120, 120), width=4)
        for y in range(60, hg, 80): d.ellipse([34, 20 + y, 64, 50 + y], fill=(120, 80, 50)); d.arc([4, 8 + y, 74, 62 + y], 200, 340, fill=(160, 160, 170), width=8)
        im.info["anchor"] = (20, im.height/2); _page = im
    return _page
def blank_page(L): L.paste(page_sprite(), (PX0 - 20, PY0 - 20), page_sprite())

# ------------------------------------------------------------------ pages
def hook(L, fr, t):
    obj(L, t, 0, facture(620), 610, 980, -6, .01); tp(L, t, -1, 600, 560, 4)
    obj(L, t, 0, polaroid(A("logos", "lille_sticker.png"), "LOSC", 420), 330, 760, -9, .01); tp(L, t, -1, 330, 500, -12)
    if t < w("six") - .05: lab(L, fr, t, -1, big("RUINÉ…", "sbh0", 180, BLANC, ROUGE, rough=4), CX, 300, -4)
    if t < w("six") - .05: obj(L, t, .25, postit("PUIS CHAMPION ?!", JAUNE, 400, 76), 800, 1560, 7, .2)
    if t > w("dettes") - .1: STAMP("IMPAYÉ", "sbh1", ROUGE, 120).draw(L, fr, 640, 1120, slam(t, w("dettes") - .1, .2), -14)
    obj(L, t, w("vendre") - .1, postit("À VENDRE EN URGENCE", ROSE, 380, 64), 260, 1500, -6)
    if t > w("six") - .05:
        lab(L, fr, t, w("six") - .05, big("6 MOIS PLUS TARD…", "sbh2", 92, BLANC, NOIR), CX, 260, -3)
        obj(L, t, w("champion") - .1, clipping("LILLE CHAMPION DE FRANCE !", 860, 104, "— MAI 2021 —"), CX, 760, 2)
        obj(L, t, w("champion") + .25, medal(120), 880, 1010, 12)
        obj(L, t, w("psg") - .1, ticket("PSG", "NEYMAR • MBAPPÉ", NAVY, 720), CX - 40, 1330, -4)
        redline(L, t, w("mbappé") + .1, [(220, 1220), (700, 1450)], 16, .2); redline(L, t, w("mbappé") + .25, [(700, 1220), (220, 1450)], 16, .2)
        if t > w("mbappé") + .4: STAMP("BATTUS", "sbh3", ROUGE, 110).draw(L, fr, 820, 1580, slam(t, w("mbappé") + .4, .18), 10)
    bills(L, fr, t, w("dettes"))

def p1944(L, fr, t):
    obj(L, t, w("tout") + .2, clipping("1944", 560, 150, "— LILLE —"), CX, 420, -3)
    obj(L, t, w("clubs") - .2, ticket("OLYMPIQUE LILLOIS", "CLUB N°1", ROUGE, 560), 400, 760, -7)
    obj(L, t, w("rivaux") - .2, ticket("SC FIVES", "CLUB N°2", NAVY, 560), 690, 920, 6)
    if t > w("rivaux"): STAMP("RIVAUX", "sb1a", NOIR, 70).draw(L, fr, 820, 690, slam(t, w("rivaux"), .18), 14)
    tp(L, t, w("fusionnent") - .1, 540, 820, -30, 220); tp(L, t, w("fusionnent"), 560, 860, 35, 220)
    obj(L, t, w("fusionnent") + .2, postit("= FUSION", JAUNE, 300, 70), 250, 1080, -8)
    obj(L, t, w("dogues") - .15, polaroid(A("logos", "lille_sticker.png"), "les Dogues", 430), 680, 1300, 5); tp(L, t, w("dogues") - .15, 680, 1040, 8)
    obj(L, t, w("dogues") + .35, postit("LES DOGUES SONT NÉS", ROSE, 340, 64), 280, 1520, -6)
def p1946(L, fr, t):
    obj(L, t, w("doublé") - .1, clipping("1946 : DOUBLÉ !", 880, 100, "— ÉDITION SPÉCIALE —"), CX, 500, -2)
    obj(L, t, w("coupe") - .1, ticket("COUPE DE FRANCE", "FINALE 1946", ROUGE, 680), 470, 980, -5)
    obj(L, t, w("championnat") - .15, postit("+ CHAMPIONNAT", JAUNE, 360, 66), 760, 1340, 6)
    obj(L, t, w("doublé") + .4, sticker("lille", 300), 300, 1450, -8)
    confetti(L, fr, "sbcf1", t - w("doublé"), 40, 2.5, [JAUNE, ROUGE, NAVY])
def pchute(L, fr, t):
    lift = clamp((t - w("sombre") + .1)/.7)
    obj(L, t, w("puis") - .05, polaroid(A("logos", "lille_sticker.png"), "LOSC", 400), 360 + 60*lift, 820 + 360*ease_out_back(lift), -6 + 30*lift)
    obj(L, t, w("sombre") - .1, clipping("LILLE SOMBRE…", 620, 92, "— CHUTE —"), 660, 420, 3)
    redline(L, t, w("sombre") + .1, [(860, 700), (860, 1200), (800, 1120), (860, 1200), (920, 1120)], 14, .4)
    obj(L, t, w("deuxième") - .1, sticker("ligue2", 300), 760, 1370, 8)
    if t > w("division") - .05: STAMP("DEUXIÈME DIVISION", "sb3a", ROUGE, 72).draw(L, fr, CX, 1660, slam(t, w("division") - .05, .18), -4)
def p2000(L, fr, t):
    obj(L, t, w("en", 3) + .05, clipping("2000", 520, 150, "— LE RETOUR —"), CX, 420, 3)
    obj(L, t, w("vahid") - .1, fiche("VAHID HALILHODZIC", "nouveau coach", 760), CX, 860, -3)
    redline(L, t, w("remonter") - .1, [(540, 1650), (540, 1180), (470, 1270), (540, 1180), (610, 1270)], 14, .35)
    obj(L, t, w("remonter") + .1, postit("REMONTÉE !", JAUNE, 340, 76), 780, 1430, 6)
    obj(L, t, w("remonter") + .3, sticker("lille", 260), 260, 1420, -8)
def p2001(L, fr, t):
    obj(L, t, w("et", 4) - .05, postit("UN AN APRÈS…", JAUNE, 360, 70), 300, 420, -6)
    obj(L, t, w("ligue") - .15, ticket("LIGUE DES CHAMPIONS", "SAISON 2001-02", NAVY, 840), CX, 870, 3)
    obj(L, t, w("champions") - .05, sticker("ucl", 440), CX, 1380, -4)
    obj(L, t, w("lille", 3) - .05, sticker("lille", 220), 800, 420, 8)
def phazard(L, fr, t):
    obj(L, t, w("au") - .05, clipping("CENTRE DE FORMATION", 760, 72, "— DOMAINE DE LUCHIN —"), CX, 340, -2)
    obj(L, t, w("gamin") - .1, postit("UN GAMIN BELGE…", JAUNE, 360, 64), 300, 680, -6)
    obj(L, t, w("quatorze") - .1, postit("14 ANS", ROSE, 300, 100), 790, 700, 7)
    redline(L, t, w("quatorze") + .15, circle_pts(790, 720, 190, 180), 10, .35)
    obj(L, t, w("eden") - .15, polaroid(A("lille", "hazard_card.png"), "EDEN HAZARD", 660), CX, 1300, -3); tp(L, t, w("eden") - .15, CX, 940, 3, 220)
def p2011(L, fr, t):
    obj(L, t, w("en", 4) + .05, clipping("2011", 500, 150, "— LILLE —"), 360, 400, -4)
    obj(L, t, w("en", 4) + .5, polaroid(A("lille", "hazard_card.png"), "Eden", 300), 800, 450, 8)
    obj(L, t, w("rudi") - .1, fiche("RUDI GARCIA", "l'entraîneur", 600), CX, 820, -2)
    lab(L, fr, t, w("doublé", 2) - .05, big("DOUBLÉ !", "sb7a", 150, NOIR, JAUNE, rough=4), CX, 1170, -4)
    if t > w("soixante-cinq") - .05:
        n = min(65, int(65*clamp((t - w("soixante-cinq") + .05)/.5)))
        big(f"1er DEPUIS {n} ANS", f"sb7b{n}", 74, BLANC, NOIR).draw(L, fr, CX, 1370, slam(t, w("soixante-cinq") - .05, .16), 3)
    obj(L, t, w("doublé", 2) + .3, sticker("ligue1", 230), 820, 1620, 8)
    confetti(L, fr, "sbcf2", t - w("doublé", 2), 50, 2.5, [JAUNE, ROUGE, NAVY])
def pdettes(L, fr, t):
    obj(L, t, w("mais") - .05, facture(640), CX, 900, 4); tp(L, t, w("mais") - .05, CX, 470, -3)
    if t > w("explosent") - .1: big("DETTES ++", "sb8a", 130, NOIR, JAUNE, rough=4).draw(L, fr, CX, 360, slam(t, w("explosent") - .1, .18)*(1 + .04*math.sin(t*20)), -5)
    obj(L, t, w("fin") - .05, postit("FIN 2020", JAUNE, 300, 80), 250, 1500, -8)
    if t > w("vendu") - .05: STAMP("VENDU", "sb8b", ROUGE, 200).draw(L, fr, CX, 950, slam(t, w("vendu") - .05, .2), -14)
    obj(L, t, w("catastrophe") - .05, postit("EN CATASTROPHE", ROSE, 340, 64), 800, 1540, 6)
    bills(L, fr, t, w("explosent"), 14)
def p2021(L, fr, t):
    lab(L, fr, t, w("l'impossible") - .05, big("L'IMPOSSIBLE", "sb9a", 120, BLANC, ROUGE, rough=4), CX, 330, -3)
    lab(L, fr, t, w("l'impossible") + .45, marker("ARRIVE", "sb9b", 80), CX, 480, 3)
    for k, (nm, role, word, x, y, r) in enumerate([("MAIGNAN", "dans les cages", "maignan", 400, 760, -5),
                                                    ("BURAK YILMAZ", "devant", "burak", 660, 1100, 4), ("GALTIER", "sur le banc", "galtier", 400, 1440, -3)]):
        obj(L, t, w(word) - .1, fiche(nm, role, 600), x, y, r); tp(L, t, w(word) - .1, x - 220, y - 140, -30, 140)
    obj(L, t, w("maignan") + .2, sticker("lille", 220), 860, 1620, 8)
def pbudget(L, fr, t):
    obj(L, t, w("face") - .05, postit("BUDGET", JAUNE, 320, 80), 300, 380, -6)
    n_l = 4; n_p = 4 + int(12*clamp((t - w("quatre") + .1)/.5)) if t > w("quatre") - .1 else 4
    if t > w("face"):
        for k in range(n_l): blit_sxy(L, billet(220)[0], 300 + (k % 2)*6, 1500 - k*26, 1, 1, (k % 3) - 1)
        obj(L, t, w("face"), sticker("lille", 200), 300, 1500 - n_l*26 - 110, -6)
    if t > w("psg", 2) - .05:
        for k in range(n_p): blit_sxy(L, billet(220)[0], 760 + (k % 2)*6, 1500 - k*26, 1, 1, (k % 3) - 1)
        obj(L, t, w("psg", 2) - .05, sticker("psg", 200), 760, 1500 - n_p*26 - 110, 6)
    obj(L, t, w("quatre") - .05, postit("×4", ROSE, 260, 150), 780, 520, 8)
    if t > w("dogues", 2) - .05:
        marker("LES DOGUES TIENNENT", "sb10a", 78).draw(L, fr, CX, 1660, slam(t, w("dogues", 2) - .05, .16), 2)
        big("JUSQU'AU BOUT", "sb10b", 70, BLANC, ROUGE).draw(L, fr, CX, 1790, slam(t, w("dogues", 2) + .5, .16), -2)
def ptitre(L, fr, t):
    t0 = w("champions", 2)
    obj(L, t, t0 - .1, clipping("CHAMPIONS DE FRANCE 2021 !", 880, 116, "— ÉDITION HISTORIQUE —"), CX, 620, -2)
    obj(L, t, t0 + .25, medal(170), 380, 1270, -10)
    obj(L, t, t0 + .45, polaroid(A("logos", "lille_sticker.png"), "LES DOGUES", 420), 760, 1320, 6)
    confetti(L, fr, "sbcf3", t - t0, 90, 4, [JAUNE, ROUGE, NAVY, BLANC])
    if t > w("toi") - .3:
        dk = Image.new("RGBA", (W, H), (20, 12, 8, int(150*clamp((t - w("toi") + .3)/.3)))); L.alpha_composite(dk)
        pcta_on(L, fr, t)
def pcta_on(L, fr, t):
    obj(L, t, w("toi") - .2, postit("TU T'EN SOUVIENS ?", JAUNE, 520, 96), 400, 600, -5)
    obj(L, t, w("dis-moi") - .1, postit("PROCHAIN CLUB ? DIS-LE EN COMMENTAIRE", ROSE, 540, 72), 650, 1250, 5)
    obj(L, t, w("toi"), sticker("lille", 240), 830, 380, 10)

T_TOUT = w("tout") - .1
PAGES = [(0, hook), (T_TOUT, p1944), (w("doublé") - .95, p1946), (w("puis") - .05, pchute), (w("en", 3) - .05, p2000), (w("et", 4) - .05, p2001),
         (w("au") - .05, phazard), (w("en", 4) - .05, p2011), (w("mais") - .1, pdettes), (w("et", 5) - .05, p2021), (w("face") - .2, pbudget),
         (w("champions", 2) - .2, ptitre)]
FLIP = .38
IMPACTS = [0, w("dettes"), w("champion"), w("mbappé") + .4, w("dogues"), w("doublé"), w("deuxième"), w("remonter"), w("ligue"), w("eden"),
           w("doublé", 2), w("vendu"), w("maignan"), w("burak"), w("galtier"), w("quatre"), w("champions", 2)]

def render_page(k, fr, t):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if k > 0: blank_page(L)
    PAGES[k][1](L, fr, t); return L

def draw(cv, fr, t, T):
    tv = max(0.0, t - PAD_IN)
    cv.paste(desk(), (0, 0))
    k = 0
    for i, (t0, _) in enumerate(PAGES):
        if tv >= t0: k = i
    if k == 1 and tv < PAGES[1][0] + .4:                         # le carnet glisse sur le bureau
        cv.paste(hook_layer(fr, tv), (0, 0), hook_layer(fr, tv)) if False else None
        H0 = render_page(0, fr, tv); cv.paste(H0, (0, 0), H0)
        u = ease_out_cubic(clamp((tv - PAGES[1][0])/.4)); L = render_page(1, fr, tv); cv.paste(L, (0, int((1 - u)*H)), L)
    else:
        L = render_page(k, fr, tv); cv.paste(L, (0, 0), L)
        if k + 1 < len(PAGES) and k >= 1 and tv > PAGES[k + 1][0] - FLIP:   # la page se tourne
            u = clamp((tv - (PAGES[k + 1][0] - FLIP))/FLIP)
            nxt = render_page(k + 1, fr, tv); cv.paste(nxt, (0, 0), nxt)
            sx = math.cos(math.pi*u)
            if sx > 0:
                L.info["anchor"] = (PX0, H/2); blit_sxy(cv, L, PX0, H/2, sx, 1, 0)
            else:
                bp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); blank_page(bp); bp.info["anchor"] = (PX0, H/2); blit_sxy(cv, bp, PX0, H/2, sx, 1, 0)
    if w("comment") - .1 < tv < T_TOUT:
        dk = Image.new("RGBA", (W, H), (20, 12, 8, 150)); cv.paste(dk, (0, 0), dk)
        ransom_line(cv, "COMMENT", 820, 170, seed=4); ransom_line(cv, "C'EST POSSIBLE ?", 1060, 120, seed=9)
    for ti in IMPACTS: shake(cv, tv, ti, 10)
    drift(cv, t, T, .02)

P = PAD_IN
def X_(word, n, name, g, dt=-.05): return (P + w(word, n) + dt, name, g)
SFX = [(0.0, "braam", .7), (0.0, "crumple", .4), X_("dettes", 1, "stamp", .8), X_("dettes", 1, "cash", .4, .1), X_("vendre", 1, "siren", .2),
       X_("six", 1, "scratch", .35), X_("champion", 1, "boom", .6), X_("champion", 1, "goal_roar", .45), X_("psg", 1, "rip", .35),
       X_("mbappé", 1, "stamp", .6, .4), X_("comment", 1, "scratch", .5), (P + T_TOUT, "whoosh", .4), X_("tout", 1, "projector", .35),
       X_("rivaux", 1, "stamp", .5), X_("fusionnent", 1, "rip", .35), X_("dogues", 1, "camera", .5), X_("dogues", 1, "crowd", .35, .3),
       X_("doublé", 1, "fanfare", .45), X_("sombre", 1, "groan", .35), X_("deuxième", 1, "stamp", .6), X_("vahid", 1, "typewriter", .35),
       X_("remonter", 1, "riser", .45), X_("ligue", 1, "goal_roar", .45), X_("gamin", 1, "sparkle", .45), X_("quatorze", 1, "pop", .4),
       X_("eden", 1, "camera", .55), X_("doublé", 2, "fanfare", .45), X_("doublé", 2, "crowd", .35), X_("mais", 1, "thunder", .45),
       X_("explosent", 1, "cash", .5), X_("vendu", 1, "gavel", .7), X_("catastrophe", 1, "crumple", .5), X_("l'impossible", 1, "riser", .45),
       X_("maignan", 1, "camera", .45), X_("burak", 1, "camera", .45), X_("galtier", 1, "camera", .45), X_("quatre", 1, "cash", .5),
       X_("dogues", 2, "drumroll", .35), X_("champions", 2, "boom", .8), X_("champions", 2, "goal_roar", .6), X_("champions", 2, "champagne", .4, .4),
       X_("toi", 1, "notif", .5), X_("commentaire", 1, "bell", .4)]
SFX += [(P + PAGES[i][0] - FLIP, "crumple", .3) for i in range(2, len(PAGES))]   # la page qui tourne
SFX = [s for s in SFX if os.path.exists(os.path.join(SFX_DIR, s[1] + ".mp3"))]
SCENES = [Scene("scrapbook", TEXTE, draw, SFX, pad_in=P, pad_out=1.6)]
def hook_layer(fr, t): return render_page(0, fr, t)

def cover(path):
    cv = background(0, TITLE); cv.paste(desk(), (0, 0)); L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    obj(L, 9, 0, facture(620), 610, 1000, -6); obj(L, 9, 0, polaroid(A("logos", "lille_sticker.png"), "LOSC", 440), 340, 800, -9)
    obj(L, 9, 0, medal(140), 820, 820, 12); cv.paste(L, (0, 0), L)
    big("RUINÉ…", "sbcv1", 160, BLANC, ROUGE, rough=4).draw(cv, 0, CX, 380, 1, -4)
    big("PUIS CHAMPION", "sbcv2", 120, NOIR, JAUNE, rough=4).draw(cv, 0, CX, 1380, 1, 3)
    big("L'HISTOIRE FOLLE DU LOSC", "sbcv3", 60, BLANC, NOIR).draw(cv, 0, CX, 1550, 1, -2)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

def stills(out):
    scene_timing(SCENES, [VOIX]); sc = SCENES[0]; os.makedirs(out, exist_ok=True)
    ts = [P + x for x in (.3, 3.4, 6.0, 9.2, 10.3, 11.0, 14.9, 17.5, 20.0, 23.3, 25.8, 30.0, 34.9, 38.8, 43.5, 47.5, 50.0, 54.0, 15.7, 35.1)]
    ims = []
    for t in ts:
        f = int(t*FPS); cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T); finish(cv, TITLE); ims.append(cv.resize((216, 384)))
    sheet = Image.new("RGB", (216*10, 2*414), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        x, y = (k % 10)*216, (k//10)*414; sheet.paste(im, (x, y + 30)); dd.text((x + 6, y + 4), f"{ts[k]-P:.1f}s", font=font("mono", 22), fill=(230, 230, 230))
    p = os.path.join(out, "sheet.jpg"); sheet.save(p, quality=82); return p

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", SLUG)
    if "--stills" in args: print(stills(f"/tmp/{SLUG}_stills")); sys.exit()
    os.makedirs(out, exist_ok=True); cover(os.path.join(out, f"{SLUG}_couverture.jpg"))
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=[VOIX], sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25, limit=True))
