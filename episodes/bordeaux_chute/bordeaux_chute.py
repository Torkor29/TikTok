"""BORDEAUX : 6 fois champion… en 4e division (format « club maudit », EN TEST, cf. skill viral §8).
Une seule voix continue (voix/voix_complete.mp3) minutée mot à mot ; les plans changent sur les mots.
Vrais écussons fournis par l'utilisateur (assets/logos/*_sticker.png), portraits papier IA (assets/bordeaux/), photo du stade en fond.

  python3 episodes/bordeaux_chute/bordeaux_chute.py output/bordeaux_chute --stills
  python3 episodes/bordeaux_chute/bordeaux_chute.py output/bordeaux_chute --cover
  python3 episodes/bordeaux_chute/bordeaux_chute.py output/bordeaux_chute
"""
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from quiz import *
from PIL import ImageFilter, ImageEnhance

TITLE = "~/histoires $ ./bordeaux"
SLUG = "bordeaux_chute"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
VOIX = os.path.join(HERE, "voix", "voix_complete.mp3")
TEXTE = open(os.path.join(HERE, "SCRIPT.md")).read()
W_ = json.load(open(os.path.join(HERE, "mots.json")))
def w(i): return W_[i][1]                                    # début du mot n° i (s)

NAVY = (14, 26, 64); NOIR = (30, 28, 28); BLANC = (250, 250, 246); ROUGE = (210, 36, 42)

# ------------------------------------------------------------------ images
def _load(path, h):
    im = Image.open(path).convert("RGBA"); im = im.resize((int(im.width*h/im.height), h), Image.LANCZOS)
    im.info["anchor"] = (im.width/2, im.height/2); return im
_c = {}
def img(name, h):
    k = (name, h)
    if k not in _c:
        p = os.path.join(ROOT, "assets", "logos", f"{name}_sticker.png") if not name.startswith("p:") else os.path.join(ROOT, "assets", "bordeaux", name[2:] + ".png")
        _c[k] = _load(p, h)
    return _c[k]
def sticker(cv, name, x, y, h, s=1.0, rot=0.0, shadow=True):
    """Autocollant (écusson / portrait) centré en (x, y), avec ombre portée."""
    if s <= .02: return
    im = img(name, h)
    if shadow:
        k = ("sh", name, h)
        if k not in _c:
            sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda v: v*100//255))
            sh = sh.filter(ImageFilter.GaussianBlur(9)); sh.info["anchor"] = im.info["anchor"]; _c[k] = sh
        blit_sxy(cv, _c[k], x + 12*s, y + 16*s, s, s, rot)
    blit_sxy(cv, im, x, y, s, s, rot)

STADE = Image.open(os.path.join(ROOT, "assets", "photos", "bordeaux_stade.webp")).convert("RGB")
_bg = {}
def stade(cv, t, dark=.55, sep=0.0):
    """Photo du stade plein écran, lent zoom (Ken Burns), assombrie (et virée sépia pour le passé)."""
    k = (dark, sep)
    if k not in _bg:
        s = H/STADE.height; im = STADE.resize((int(STADE.width*s), H), Image.LANCZOS)
        im = ImageEnhance.Brightness(im).enhance(1 - dark)
        if sep:
            g = im.convert("L"); im = Image.merge("RGB", (g.point(lambda v: min(255, int(v*1.1 + 20))), g.point(lambda v: int(v*.95 + 8)), g.point(lambda v: int(v*.75))))
        _bg[k] = im
    im = _bg[k]; z = 1.0 + .04*t/10; cw, ch = W/z, H/z
    x0 = (im.width - cw)/2 + 60*math.sin(t*.15); y0 = (im.height - ch)/2
    cv.paste(im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch)), (0, 0))

def big(txt, key, size=110, fg=BLANC, bg=NOIR, rough=3): return LBL(txt, key, font("title", size), fg, bg, padx=26, pady=6, rough=rough, maxw=1000)
def counter_lbl(n, key, size=150): return LBL(str(n), f"{key}{n}", font("title", size), NOIR, GOLD, padx=24, pady=0, rough=2.5)

# ------------------------------------------------------------------ plans (temps absolus dans la voix)
T0 = PAD_IN
CUTS = [0, w(23), w(51), w(77), w(87), w(107), w(133), w(154)]
def shot_of(t):
    k = 0
    for i, c in enumerate(CUTS):
        if t >= c: k = i
    return k

def s1(cv, fr, t):           # hook : image 0 = contraste chiffré lisible en 1 s + gros écusson
    stade(cv, t, .5)
    tq = w(14)                                                # « quatrième division »
    big("6 FOIS CHAMPION…", "bx1a", 104, NOIR, GOLD).draw(cv, fr, CX, 300, 1, -3)
    big("EN 4e DIVISION ?!", "bx1b", 112, BLANC, ROUGE).draw(cv, fr, CX, 460, 1, 2)
    shake = 14*math.sin(t*60)*clamp(1 - prog(t, tq, .5)) if t > tq else 0
    sticker(cv, "bordeaux", CX + shake, 1060, 720, 1 + .02*math.sin(t*4), -4 + .5*shake)
    if t > w(6): sticker(cv, "p:zidane", 190, 1460, 330, pop_in(t, w(6), .25), -8)
    if t > tq:
        sticker(cv, "n2", 860, 1480, 400, slam(t, tq, .25), 10)
        STAMP("CHUTE LIBRE", "bx1c", ROUGE, 70).draw(cv, fr, CX, 1760, slam(t, w(16), .25), -5)
def s2(cv, fr, t):           # la gloire : 6 titres, Zidane / Lizarazu / Dugarry, finale C3 96
    stade(cv, t, .45, sep=.9)
    sticker(cv, "bordeaux_ancien", CX, 380, 420, pop_in(t, CUTS[1], .3), 4)
    n = 1 + int(5*clamp(prog(t, w(26), .9)))
    LBL(f"{n} TITRE{'S' if n > 1 else ''} DE CHAMPION", f"bxt{n}", font("title", 70), NOIR, GOLD, padx=24, pady=4, rough=2.5).draw(cv, fr, CX, 680, pop_in(t, w(26) - .1, .25), -2)
    for i, (nm, x, wi) in enumerate((("zidane", 220, 36), ("lizarazu", CX, 41), ("dugarry", 860, 43))):
        if t > w(wi) - .15:
            sticker(cv, "p:" + nm, x, 1060, 400, slam(t, w(wi) - .15, .25), (-6, 3, 7)[i])
            TAG(nm.upper(), f"bxn{nm}", PAL["paper"], NOIR, 44).draw(cv, fr, x, 1300, pop_in(t, w(wi), .25), (-3, 2, 4)[i])
    if t > w(44):
        sticker(cv, "bayern", 840, 1620, 300, pop_in(t, w(44), .3), 8)
        STAMP("FINALE C3 1996", "bx2s", ROUGE, 70).draw(cv, fr, 380, 1620, slam(t, w(44) + .2, .25), -6)
def s3(cv, fr, t):           # 2009 : Blanc, Gourcuff, Chamakh, doublé, 11 victoires de suite
    stade(cv, t, .5)
    big("2009", "bx3y", 150, NOIR, GOLD).draw(cv, fr, CX, 290, slam(t, CUTS[2], .2), -3)
    for i, (nm, x, wi) in enumerate((("blanc", 220, 55), ("gourcuff", CX, 61), ("chamakh", 860, 63))):
        if t > w(wi) - .15:
            sticker(cv, "p:" + nm, x, 760, 400, slam(t, w(wi) - .15, .25), (-6, 3, 7)[i])
            TAG(nm.upper(), f"bxn{nm}", PAL["paper"], NOIR, 44).draw(cv, fr, x, 1000, pop_in(t, w(wi), .25), (-3, 2, 4)[i])
    if t > w(59): STAMP("LE DOUBLÉ", "bx3d", ROUGE, 80).draw(cv, fr, CX, 1130, slam(t, w(59), .25), -5)
    if t > w(69) - .3:
        n = 1 + int(10*clamp(prog(t, w(69) - .3, .9)))
        counter_lbl(n, "bx3c").draw(cv, fr, 330, 1400, 1 + .1*bump(prog(t, w(69) + .6, .3)), -4)
        LBL("VICTOIRES DE SUITE", "bx3v", font("title", 56), BLANC, NAVY, padx=20, pady=4, rough=2.5).draw(cv, fr, 700, 1400, pop_in(t, w(70), .25), 3)
    if t > w(75):
        STAMP("AU SOMMET", "bx3s", (46, 164, 86), 100).draw(cv, fr, CX, 1640, slam(t, w(75), .25), -6)
        confetti(cv, fr, "bx3cf", t - w(75), 60, 2.5, [GOLD, BLANC, (40, 90, 200)])
def s4(cv, fr, t):           # relance
    stade(cv, t, .8)
    z = 1 + .25*prog(t, CUTS[3], 2.4)
    big("MAIS ATTENDS…", "bx4a", 120, BLANC, ROUGE).draw(cv, fr, CX, 640, z*slam(t, CUTS[3], .2), -3)
    if t > w(82): big("LA CHUTE EST ENCORE PLUS FOLLE", "bx4b", 66, NOIR, GOLD).draw(cv, fr, CX, 860, slam(t, w(82), .25), 2)
    sticker(cv, "bordeaux", CX, 1350, 520, 1, 8*math.sin(t*20)*clamp(prog(t, w(82), .2)))
def ascenseur(cv, fr, t, a, b, t0, y0=560, y1=1340):
    """Écusson de ligue a en haut → flèche qui descend → b en bas (slam)."""
    sticker(cv, a, CX, y0, 380, pop_in(t, t0 - .4, .3), -4)
    u = prog(t, t0, .5)
    if u > 0:
        d = ImageDraw.Draw(cv); yb = lerp(y0 + 230, y1 - 260, u)
        d.line([(CX, y0 + 230), (CX, yb)], fill=ROUGE, width=26)
        d.polygon([(CX - 55, yb - 10), (CX + 55, yb - 10), (CX, yb + 60)], fill=ROUGE)
    if u >= 1: sticker(cv, b, CX, y1, 380, slam(t, t0 + .5, .25), 5)
def s5(cv, fr, t):           # 2022 : dernier de L1 → L2
    stade(cv, t, .7)
    big("2022", "bx5y", 130, NOIR, GOLD).draw(cv, fr, CX, 230, slam(t, w(92), .2), -3)
    ascenseur(cv, fr, t, "ligue1", "ligue2", w(103))
    if t > w(98): STAMP("20e SUR 20", "bx5s", ROUGE, 80).draw(cv, fr, 800, 900, slam(t, w(98), .25), 8)
def s6(cv, fr, t):           # 2024 : pas de repreneur → statut pro abandonné → N2
    stade(cv, t, .75)
    big("2024", "bx6y", 130, NOIR, GOLD).draw(cv, fr, CX, 230, slam(t, CUTS[5], .2), -3)
    if t > w(113): TAG("pas de repreneur…", "bx6r", PAL["paper"], NOIR, 54).draw(cv, fr, 800, 330, pop_in(t, w(113), .25), -2)
    ascenseur(cv, fr, t, "ligue2", "n2", w(126) - .2)
    if t > w(121): STAMP("STATUT PRO ABANDONNÉ", "bx6s", ROUGE, 62).draw(cv, fr, CX, 920, slam(t, w(121), .25), -6)
    if t > w(131): big("4e DIVISION", "bx6d", 100, BLANC, ROUGE).draw(cv, fr, CX, 1690, slam(t, w(131), .25), 3)
def s7(cv, fr, t):           # 1991 : déjà rétrogradé pour l'argent
    stade(cv, t, .55, sep=1)
    big("LE PIRE ?", "bx7a", 110, BLANC, ROUGE).draw(cv, fr, CX, 260, slam(t, CUTS[6], .2), -3)
    sticker(cv, "bordeaux_ancien", CX, 760, 520, pop_in(t, CUTS[6] + .2, .3), -5)
    if t > w(142): big("1991", "bx7y", 160, NOIR, GOLD).draw(cv, fr, CX, 1150, slam(t, w(142), .2), 4)
    if t > w(148): STAMP("RÉTROGRADÉ EN D2", "bx7s", ROUGE, 76).draw(cv, fr, CX, 1380, slam(t, w(148), .25), -6)
def s8(cv, fr, t):           # boucle + CTA
    stade(cv, t, .5)
    sticker(cv, "bordeaux", CX, 600, 560, 1 + .02*math.sin(t*4), -4)
    big("6× CHAMPION… EN N2", "bx8a", 92, NOIR, GOLD).draw(cv, fr, CX, 1000, slam(t, CUTS[7], .2), -3)
    if t > w(165):
        big("RETOUR EN LIGUE 1 ?", "bx8b", 80, BLANC, NAVY).draw(cv, fr, CX, 1170, slam(t, w(165), .25), 2)
        STAMP("OUI", "bx8o", (46, 164, 86), 100).draw(cv, fr, 330, 1360, slam(t, w(167), .25), -8)
        STAMP("NON", "bx8n", ROUGE, 100).draw(cv, fr, 750, 1360, slam(t, w(169), .25), 8)
    if t > w(173): TAG("dis-le en commentaire 👇".replace("👇", ""), "bx8c", PAL["paper"], NOIR, 54).draw(cv, fr, CX, 1530, pop_in(t, w(173), .25), -2)
    sub_button(cv, fr, CX, 1690, t, w(175) - .15, w(175) + .25)

SHOTS = [s1, s2, s3, s4, s5, s6, s7, s8]
def draw(cv, fr, t, T):
    tv = t - T0; k = shot_of(tv); SHOTS[k](cv, fr, tv)
    c = CUTS[k]
    if k and tv - c < .25: punch(cv, tv, c, 1.06, .25)                 # coup de zoom à chaque changement de plan
    drift(cv, t, T, .02)

SFX = [(0.0, "boom", .9), (0.0, "braam", .6), (T0 + w(14), "crash", .7), (T0 + w(16), "stamp", .7)]
SFX += [(T0 + c, "whoosh", .45) for c in CUTS[1:]]
SFX += [(T0 + w(i) - .15, "pop", .5) for i in (36, 41, 43, 55, 61, 63)] + [(T0 + w(44) + .2, "stamp", .6), (T0 + w(59), "stamp", .6)]
SFX += [(T0 + w(69), "drumroll", .5), (T0 + w(75), "crowd", .7), (T0 + w(75), "sparkle", .6)]
SFX += [(T0 + w(77), "rewind", .6), (T0 + w(77) + .3, "thunder", .5)]
SFX += [(T0 + w(103), "elevator", .5), (T0 + w(103) + .5, "crash", .6), (T0 + w(98), "stamp", .6)]
SFX += [(T0 + w(121), "stamp", .7), (T0 + w(126) - .2, "elevator", .5), (T0 + w(126) + .3, "crash", .7), (T0 + w(131), "groan", .6)]
SFX += [(T0 + w(133), "projector", .5), (T0 + w(142), "typewriter", .5), (T0 + w(148), "stamp", .7)]
SFX += [(T0 + w(167), "pop2", .5), (T0 + w(169), "pop2", .5), (T0 + w(173), "notif", .6), (T0 + w(175) + .25, "notif", .6)]
SCENES = [Scene("bordeaux", TEXTE, draw, SFX, pad_in=T0, pad_out=1.2)]

def cover(path):
    cv = background(0, TITLE); stade(cv, 0, .5)
    big("6 FOIS CHAMPION…", "bx1a", 104, NOIR, GOLD).draw(cv, 0, CX, 320, 1, -3)
    big("EN 4e DIVISION ?!", "bx1b", 112, BLANC, ROUGE).draw(cv, 0, CX, 480, 1, 2)
    sticker(cv, "bordeaux", CX, 1080, 760, 1, -4)
    sticker(cv, "n2", 860, 1560, 420, 1, 10); sticker(cv, "p:zidane", 200, 1560, 360, 1, -8)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

def stills(out):
    scene_timing(SCENES, [VOIX]); sc = SCENES[0]; os.makedirs(out, exist_ok=True)
    ts = [T0 + x for x in (0.05, 1.0, w(15), w(44) + .8, w(70) + .8, w(78), w(104) + .8, w(127) + .8, w(149), w(170))]
    ims = []
    for t in ts:
        f = int(t*FPS); cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T); finish(cv, TITLE); ims.append(cv.resize((240, 427)))
    sheet = Image.new("RGB", (240*len(ims), 460), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims): sheet.paste(im, (k*240, 33)); dd.text((k*240 + 6, 4), f"{ts[k]:.1f}s", font=font("mono", 22), fill=(230, 230, 230))
    p = os.path.join(out, "bx_sheet.jpg"); sheet.save(p, quality=82); return p

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", SLUG)
    if "--stills" in args: print(stills(f"/tmp/{SLUG}_stills")); sys.exit()
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=[VOIX], sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25, limit=True))
