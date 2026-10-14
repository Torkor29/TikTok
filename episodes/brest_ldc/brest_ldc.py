"""BREST EN LIGUE DES CHAMPIONS (histoire « club miracle », ≈ 47 s). Style collage papier façon documentaire :
photos réelles fournies -> coupures de journal tramées (scripts/coupure_papier.py), écussons en autocollants, surligneur,
fond papier crème + accent rouge Brest. Voix Léo continue, minutée mot à mot (mots.json = transcription ElevenLabs).

  python3 episodes/brest_ldc/brest_ldc.py output/brest_ldc --stills
  python3 episodes/brest_ldc/brest_ldc.py output/brest_ldc
"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from quiz import *
from PIL import ImageFilter, ImageChops

TITLE = "~/histoires $ ./brest"
SLUG = "brest_ldc"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
VOIX = os.path.join(HERE, "voix", "voix_complete.mp3")
TEXTE = open(os.path.join(HERE, "texte.txt")).read()
_W = [w for w in json.load(open(os.path.join(HERE, "mots.json"))) if w["text"] not in ":!?«»"]
def w(txt, n=1):
    """Début (s) de la n-ième occurrence du mot txt dans la voix."""
    k = 0
    for x in _W:
        if x["text"].strip(".,…!?:«» ").lower() == txt.lower():
            k += 1
            if k == n: return x["start"]
    raise KeyError(txt)

CREME = (238, 230, 212); NOIR = (28, 26, 30); BLANC = (250, 250, 246); ROUGE = (206, 28, 40); NAVY = (14, 22, 58)
JAUNE = (255, 222, 64)

# ------------------------------------------------------------------ images
_c = {}
def _img(path, h):
    k = (path, h)
    if k not in _c:
        im = Image.open(path).convert("RGBA"); im = im.resize((int(im.width*h/im.height), h), Image.LANCZOS)
        im.info["anchor"] = (im.width/2, im.height/2)
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda v: v*110//255))
        sh = sh.filter(ImageFilter.GaussianBlur(10)); sh.info["anchor"] = im.info["anchor"]; _c[k] = (im, sh)
    return _c[k]
def put(cv, name, x, y, h, s=1.0, rot=0.0):
    """Écusson (logos/<name>_sticker.png) ou coupure photo (brest/<name>.png), avec ombre portée."""
    if s <= .02: return
    p = os.path.join(ROOT, "assets", "logos", f"{name}_sticker.png")
    if not os.path.exists(p): p = os.path.join(ROOT, "assets", "brest", f"{name}.png")
    im, sh = _img(p, h)
    blit_sxy(cv, sh, x + 14*s, y + 20*s, s, s, rot); blit_sxy(cv, im, x, y, s, s, rot)

_grain = None
def paper_bg(cv, fr, col=CREME, t=0.0):
    """Fond papier : couleur unie + grain fixe + légères fibres."""
    global _grain
    stage_fill(cv, fr, col, f"brbg{col}")
    if _grain is None:
        rnd = random.Random(3); g = Image.effect_noise((W//2, H//2), 38).resize((W, H), Image.BILINEAR)
        _grain = g.point(lambda v: 0 if v > 110 else int((110 - v)*.55))
    dark = Image.new("RGBA", (W, H), (60, 40, 20, 0)); dark.putalpha(_grain); cv.alpha_composite(dark) if cv.mode == "RGBA" else cv.paste(dark, (0, 0), dark)

def shake(cv, t, t0, amp=22, dur=.35):
    if t0 <= t < t0 + dur:
        a = amp*(1 - (t - t0)/dur); cv.paste(cv.copy(), (int(a*math.sin(t*90)), int(a*math.cos(t*73))))
def flash(cv, t, t0, dur=.12, col=BLANC):
    if t0 <= t < t0 + dur:
        cv.paste(Image.blend(cv.convert("RGB"), Image.new("RGB", (W, H), col), .6*(1 - (t - t0)/dur)).convert(cv.mode), (0, 0))
def glitch(cv, t, t0, dur=.16):
    if not (t0 <= t < t0 + dur): return
    u = 1 - (t - t0)/dur; r, g, b = cv.convert("RGB").split(); o = int(26*u)
    cv.paste(Image.merge("RGB", (ImageChops.offset(r, o, 0), g, ImageChops.offset(b, -o, 0))).convert(cv.mode), (0, 0))

def big(txt, key, size=110, fg=BLANC, bg=NOIR, rough=3, maxw=1000): return LBL(txt, key, font("title", size), fg, bg, padx=26, pady=6, rough=rough, maxw=maxw)
def marker(txt, key, size=78): return LBL(txt, key, font("title", size), NOIR, JAUNE, padx=22, pady=4, rough=2, maxw=1000)
def typed(txt, t, t0, cps=24): n = int(max(0, t - t0)*cps); return txt[:n]
def slide(t, t0, d=.3, dist=900): return dist*(1 - ease_out_back(clamp((t - t0)/d)))
HEART_R = Paper(heart_pts(7), ROUGE, "brheart", rough=1.2, shadow=True)

# ------------------------------------------------------------------ plans (temps = secondes dans la voix)
T_RIB, T_JAN, T_ROY, T_SAI, T_CH, T_STA, T_LA, T_REV, T_TOI = w("il"), w("janvier"), w("éric"), w("et", 2), w("dans", 2), w("le", 4), w("et", 3), w("le", 5), w("et", 4)
CUTS = [0, w("brest"), T_RIB, T_JAN, T_ROY, T_SAI, T_CH, T_STA, T_LA, T_REV, T_TOI]

def s0(cv, fr, t):   # HOOK : budget -> coach oublié -> « et pourtant »
    paper_bg(cv, fr, CREME)
    put(cv, "brest", CX, 700, 560, slam(t, 0, .18), -5 + 1.5*math.sin(t*3))
    big("UN DES PLUS PETITS", "br0a", 92, BLANC, NOIR).draw(cv, fr, CX, 170, slam(t, 0, .16), -3)
    marker("BUDGETS DE FRANCE", "br0b", 92).draw(cv, fr, CX, 300, slam(t, w("budgets") - .05, .16), 2)
    if t > w("coach") - .1:
        put(cv, "roy", 760 + slide(t, w("coach") - .1, .3), 1330, 640, 1, 5)
        big("12 ANS", "br0c", 150, BLANC, ROUGE).draw(cv, fr, 300, 1180, slam(t, w("douze"), .18), -8)
        big("SANS ENTRAÎNER", "br0d", 64, BLANC, NOIR).draw(cv, fr, 300, 1330, slam(t, w("douze") + .12, .18), -4)
    if t > w("pourtant"):
        STAMP("ET POURTANT…", "br0e", ROUGE, 120).draw(cv, fr, CX, 1720, slam(t, w("pourtant"), .2), -4)

def s1(cv, fr, t):   # « Brest a joué la Ligue des champions » : choc visuel bleu nuit
    paper_bg(cv, fr, NAVY)
    rays(cv, (CX, 900), t, 1.0, 18, 1700, (30, 46, 110), .1, .4)
    confetti(cv, fr, "br1cf", t - w("ligue") + .2, 60, 3, [BLANC, (190, 200, 240), JAUNE])
    put(cv, "ucl", CX, 900, 720, slam(t, w("ligue") - .05, .22), 2*math.sin(t*4))
    put(cv, "brest", 240, 1520, 380, slam(t, w("brest") - .05, .18), -10)
    big("BREST", "br1a", 170, BLANC, ROUGE).draw(cv, fr, CX, 230, slam(t, w("brest"), .18), -3)
    big("EN LIGUE DES CHAMPIONS", "br1b", 70, NOIR, BLANC).draw(cv, fr, CX, 400, slam(t, w("ligue"), .18), 2)

def s2(cv, fr, t):   # 20 ans avant : National, Ribéry
    paper_bg(cv, fr, CREME); tl = t - T_RIB
    big("IL Y A 20 ANS…", "br2a", 100, BLANC, NOIR).draw(cv, fr, CX, 190, slam(t, T_RIB, .16), -3)
    put(cv, "brest", 230, 470, 300, slam(t, w("brest", 2), .18), -8)
    marker("EN NATIONAL", "br2b", 96).draw(cv, fr, 650, 430, slam(t, w("national") - .05, .18), 3)
    big("(3e DIVISION)", "br2c", 54, BLANC, ROUGE).draw(cv, fr, 650, 570, slam(t, w("national") + .25, .18), -2)
    if t > w("avec") - .15:
        put(cv, "ribery", CX + slide(t, w("avec") - .15, .3, -1000), 1170, 760, 1 + .015*tl, -3)
        big("FRANCK RIBÉRY", "br2d", 104, NOIR, JAUNE).draw(cv, fr, CX, 1640, slam(t, w("franck"), .18), 3)

def table(cv, fr, t, t0):
    """Bas du classement de Ligue 1 : Brest dans la zone rouge (lignes qui glissent)."""
    rows = [("15", "...", False), ("16", "...", False), ("17", "...", False), ("18", "BREST", True), ("19", "...", False), ("20", "...", False)]
    for k, (pos, club, me) in enumerate(rows):
        u = clamp((t - t0 - k*.05)/.25); x = CX + 1100*(1 - ease_out_back(u)); y = 760 + k*112
        if u <= 0: continue
        d = ImageDraw.Draw(cv); red = int(pos) >= 18
        d.rectangle([x - 430, y - 46, x + 430, y + 46], fill=(ROUGE if me else ((240, 200, 200) if red else (250, 246, 236))), outline=NOIR, width=4)
        d.text((x - 400, y), pos, font=font("title", 60), fill=BLANC if me else NOIR, anchor="lm")
        d.text((x - 260, y), club, font=font("title", 64), fill=BLANC if me else (120, 110, 110), anchor="lm")
    if t > t0 + .45: STAMP("ZONE ROUGE", "br3z", ROUGE, 110).draw(cv, fr, CX, 1520, slam(t, t0 + .45, .2), -8)

def s3(cv, fr, t):   # janvier 2023 : zone rouge, le président appelle
    paper_bg(cv, fr, CREME)
    LBL(typed("JANVIER 2023", t, T_JAN, 16), "br3a" + typed("JANVIER 2023", t, T_JAN, 16), font("mono", 96), NOIR, BLANC, padx=24, pady=6, rough=2).draw(cv, fr, CX, 220, 1, -2) if t > T_JAN + .05 else None
    if t < w("président") - .05: table(cv, fr, t, w("zone") - .45)
    else:
        put(cv, "lesaint", 380, 900, 620, slam(t, w("président") - .05, .2), -4)
        marker("DENIS LE SAINT", "br3b", 76).draw(cv, fr, 380, 1290, slam(t, w("denis"), .16), 3)
        big("président", "br3c", 56, BLANC, NOIR).draw(cv, fr, 380, 1400, slam(t, w("denis") + .15, .16), -2)
        if t > w("appelle"):
            ring = 1 + .06*math.sin(t*40) if t < w("appelle") + .8 else 1
            big("DRING !", "br3d", 90, BLANC, ROUGE).draw(cv, fr, 820, 640, slam(t, w("appelle"), .15)*ring, 10)
        if t > w("homme"):
            mystery_q = slam(t, w("homme"), .2)
            big("?", "br3e", 300, BLANC, NOIR).draw(cv, fr, 800, 1200, mystery_q, 6)
            big("PLUS PERSONNE NE L'ATTEND", "br3f", 58, NOIR, JAUNE).draw(cv, fr, CX, 1700, slam(t, w("personne"), .16), -2)

def s4(cv, fr, t):   # Éric Roy : il sauve Brest
    paper_bg(cv, fr, ROUGE)
    rays(cv, (CX, 900), t, .9, 16, 1600, (226, 60, 66), .1, .3)
    put(cv, "roy", CX, 900, 900, slam(t, T_ROY, .2)*(1 + .02*(t - T_ROY)), -3)
    big("ÉRIC ROY", "br4a", 150, NOIR, BLANC).draw(cv, fr, CX, 200, slam(t, T_ROY + .05, .16), -3)
    if t > w("sauve") - .05: STAMP("SAUVÉ", "br4b", NOIR, 170).draw(cv, fr, CX, 1550, slam(t, w("sauve") - .05, .2), -10)

def s5(cv, fr, t):   # la saison d'après : 3e, qualifié, 1re fois
    paper_bg(cv, fr, CREME)
    big("LA SAISON D'APRÈS…", "br5a", 90, BLANC, NOIR).draw(cv, fr, CX, 180, slam(t, T_SAI, .16), -2)
    if t < w("qualifié") - .05:
        if t > w("folie") - .1: big("C'EST LA FOLIE", "br5b", 80, NOIR, JAUNE).draw(cv, fr, CX, 330, slam(t, w("folie") - .1, .16), 3)
        if t > w("troisième") - .05:
            big("3e", "br5c", 420, BLANC, ROUGE, rough=4).draw(cv, fr, 380, 900, slam(t, w("troisième") - .05, .22), -6)
            put(cv, "ligue1", 800, 950, 420, slam(t, w("ligue", 2) - .05, .2), 8)
            confetti(cv, fr, "br5cf", t - w("troisième"), 70, 3, [ROUGE, BLANC, JAUNE])
    else:
        put(cv, "ucl", CX, 820, 640, slam(t, w("qualifié") - .05, .22), -3)
        STAMP("QUALIFIÉ !", "br5d", ROUGE, 140).draw(cv, fr, CX, 1290, slam(t, w("qualifié"), .2), -6)
        if t > w("première") - .1:
            marker("1re FOIS DE SON HISTOIRE", "br5e", 78).draw(cv, fr, CX, 1520, slam(t, w("première") - .1, .18), 2)
        confetti(cv, fr, "br5cf2", t - w("qualifié"), 80, 3, [ROUGE, BLANC, JAUNE])

LYR = [("QUAND JE VOIS TON JEU", "quand", 1, BLANC, NOIR), ("JE SUIS AMOUREUX", "suis", 1, BLANC, ROUGE),
       ("QUAND J'ENTENDS SA VOIX", "quand", 2, BLANC, NOIR), ("J'SUIS FAN D'ÉRIC ROY !", "j'suis", 1, NOIR, JAUNE)]
def s6(cv, fr, t):   # le chant culte, façon karaoké de tribune
    paper_bg(cv, fr, NAVY)
    rays(cv, (CX, 1500), t, .8, 20, 1800, (26, 38, 96), .08, .5)
    marker("DANS LES TRIBUNES…", "br6a", 74).draw(cv, fr, CX, 170, slam(t, T_CH, .16), -2)
    if t < w("quand") - .1:
        big("UN CHANT", "br6b", 150, BLANC, ROUGE).draw(cv, fr, CX, 700, slam(t, w("chant") - .05, .18), -4)
        big("DEVIENT CULTE", "br6c", 120, NOIR, BLANC).draw(cv, fr, CX, 900, slam(t, w("culte") - .05, .18), 3)
        put(cv, "brest", CX, 1350, 420, slam(t, T_CH, .2), -6)
        return
    bob = 14*math.sin(t*9)
    put(cv, "roy", CX, 1440 + bob, 640, 1, 4*math.sin(t*4.5))
    for k, (txt, word, n, fg, bg) in enumerate(LYR):
        t0 = w(word, n) - .05
        if t > t0: big(txt, f"br6l{k}", 70, fg, bg, maxw=1040).draw(cv, fr, CX, 380 + k*165, slam(t, t0, .14), (-3, 3, -2, 2)[k])
    if t > w("amoureux") - .1:
        for k in range(8):
            u = prog(t, w("amoureux") - .1 + k*.12, 1.4)
            if 0 < u < 1: HEART_R.draw(cv, fr, 150 + (k*137) % 800, 1900 - 1500*u, .55*(1 - .3*u), 10*math.sin(k + t*3), 1 - u)

def s7(cv, fr, t):   # stade pas aux normes -> Guingamp
    paper_bg(cv, fr, CREME)
    big("STADE PAS AUX NORMES", "br7a", 80, BLANC, NOIR).draw(cv, fr, CX, 230, slam(t, T_STA, .16), -2)
    STAMP("REFUSÉ", "br7b", ROUGE, 130).draw(cv, fr, CX, 420, slam(t, w("normes"), .2), 8)
    # route Brest -> Guingamp : la pastille avance
    d = ImageDraw.Draw(cv); x0, x1, y = 170, 910, 1050
    u = clamp((t - w("brest", 4))/.9)
    for k in range(0, 40):
        xa = lerp(x0, x1, k/40); xb = lerp(x0, x1, (k + .55)/40)
        if k/40 <= u: d.line([(xa, y + 40*math.sin(k/6)), (xb, y + 40*math.sin((k + .55)/6))], fill=NOIR, width=12)
    put(cv, "brest", x0, y - 200, 260, slam(t, w("brest", 4) - .1, .18), -6)
    big("BREST", "br7c", 64, BLANC, ROUGE).draw(cv, fr, x0, y + 140, slam(t, w("brest", 4), .16), -3)
    xd = lerp(x0, x1, u); d.ellipse([xd - 26, y + 40*math.sin(u*40/6) - 26, xd + 26, y + 40*math.sin(u*40/6) + 26], fill=ROUGE, outline=NOIR, width=5)
    if t > w("guingamp") - .05:
        big("GUINGAMP", "br7d", 80, NOIR, JAUNE).draw(cv, fr, x1 - 60, y - 160, slam(t, w("guingamp") - .05, .18), 4)
        marker("LES MATCHS DE LDC", "br7e", 66).draw(cv, fr, CX, 1450, slam(t, w("guingamp") + .2, .18), -2)

RES = [("BREST", "2 - 1", "STURM GRAZ", "sturm"), ("SALZBOURG", "0 - 4", "BREST", "quatre-zéro"), ("BREST", "1 - 1", "LEVERKUSEN", "nul")]
def s8(cv, fr, t):   # les résultats : 10 points sur 12
    paper_bg(cv, fr, NAVY)
    put(cv, "ucl", CX, 250, 300, slam(t, T_LA, .2), 0)
    big("ET LÀ…", "br8a", 100, NOIR, JAUNE).draw(cv, fr, CX, 520, slam(t, T_LA, .16), -3)
    for k, (a, sc, b, word) in enumerate(RES):
        t0 = w(word) - .15; u = clamp((t - t0)/.25)
        if u <= 0: continue
        y = 760 + k*190; x = CX + 1100*(1 - ease_out_back(u))
        big(a, f"br8r{k}a", 64, BLANC, ROUGE if a == "BREST" else NOIR).draw(cv, fr, x - 300, y, 1, -2)
        big(sc, f"br8r{k}s", 80, NOIR, BLANC).draw(cv, fr, x, y, 1, 0)
        big(b, f"br8r{k}b", 64, BLANC, ROUGE if b == "BREST" else NOIR).draw(cv, fr, x + 300, y, 1, 2)
    if t > w("dix") - .05:
        big("10 / 12", "br8c", 230, BLANC, ROUGE, rough=4).draw(cv, fr, CX, 1500, slam(t, w("dix") - .05, .2), -5)
        big("POINTS", "br8d", 70, NOIR, BLANC).draw(cv, fr, CX, 1690, slam(t, w("points"), .16), 3)
        confetti(cv, fr, "br8cf", t - w("dix"), 70, 3, [ROUGE, BLANC, JAUNE])

def gwenn(cv, t, a=1.0):
    """Drapeau breton en papier (bandes noires et blanches + carré d'hermines), flotte un peu."""
    fl = Image.new("RGBA", (900, 560), BLANC + (255,)); d = ImageDraw.Draw(fl)
    for k in range(9):
        if k % 2 == 0: d.rectangle([0, k*560/9, 900, (k + 1)*560/9], fill=NOIR)
    d.rectangle([0, 0, 400, 560*5/9], fill=BLANC)
    for i in range(3):
        for j in range(3):
            x, y = 60 + i*130, 50 + j*100; d.polygon([(x, y - 30), (x - 16, y + 20), (x + 16, y + 20)], fill=NOIR)
    fl = fl.rotate(-4 + 2*math.sin(t*3), expand=True, resample=Image.BICUBIC); fl.info["anchor"] = (fl.width/2, fl.height/2)
    blit_sxy(cv, fl, CX, 1350, a, a, 0)

def s9(cv, fr, t):   # barrage contre le PSG, la Bretagne s'en souvient
    paper_bg(cv, fr, CREME)
    if t < w("mais") - .05:
        put(cv, "brest", 280, 800, 420, slam(t, T_REV, .18), -8)
        put(cv, "psg", 800, 800, 420, slam(t, w("psg") - .1, .2), 8)
        big("VS", "br9a", 110, BLANC, NOIR).draw(cv, fr, CX, 820, slam(t, w("barrage"), .16), 0)
        big("BARRAGE", "br9b", 120, BLANC, ROUGE).draw(cv, fr, CX, 260, slam(t, w("barrage") - .05, .16), -3)
        if t > w("psg") + .3: STAMP("FIN DU RÊVE", "br9c", NOIR, 120).draw(cv, fr, CX, 1300, slam(t, w("psg") + .3, .2), -7)
    else:
        gwenn(cv, t, slam(t, w("mais") - .05, .22))
        put(cv, "brest", CX, 620, 520, slam(t, w("mais"), .2), -4)
        big("TOUTE LA BRETAGNE", "br9d", 96, BLANC, NOIR).draw(cv, fr, CX, 200, slam(t, w("bretagne") - .1, .16), -3)
        marker("S'EN SOUVIENT", "br9e", 96).draw(cv, fr, CX, 1780, slam(t, w("souvient") - .05, .16), 2)

def s10(cv, fr, t):  # CTA : t'es fan d'Éric Roy ?
    paper_bg(cv, fr, ROUGE)
    rays(cv, (CX, 900), t, .9, 16, 1600, (226, 60, 66), .1, .3)
    put(cv, "roy", CX, 860, 760, 1 + .01*math.sin(t*5), -3 + 2*math.sin(t*3))
    big("ET TOI ?", "bra", 130, NOIR, BLANC).draw(cv, fr, CX, 190, slam(t, T_TOI, .16), -3)
    big("T'ES FAN D'ÉRIC ROY ?", "brb", 86, NOIR, JAUNE).draw(cv, fr, CX, 1340, slam(t, w("fan", 2) - .1, .16), 2)
    if t > w("dis-le") - .1:
        STAMP("OUI", "bro", (46, 164, 86), 110).draw(cv, fr, 300, 1560, slam(t, w("dis-le") - .1, .2), -8)
        STAMP("OUI !", "bro2", (46, 164, 86), 110).draw(cv, fr, 780, 1560, slam(t, w("dis-le") + .15, .2), 8)
        big("DIS-LE EN COMMENTAIRE", "brc", 64, BLANC, NOIR).draw(cv, fr, CX, 1760, slam(t, w("commentaire") - .1, .2), -2)

SHOTS = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
IMPACTS = [0, w("budgets"), w("douze"), w("pourtant"), w("ligue"), w("national"), w("franck"), w("zone"), w("président"), T_ROY, w("sauve"),
           w("troisième"), w("qualifié"), w("normes"), w("sturm"), w("quatre-zéro"), w("nul"), w("dix"), w("psg") + .3, w("mais")]
def shot_of(t):
    k = 0
    for i, c in enumerate(CUTS):
        if t >= c - .04: k = i
    return k
def draw(cv, fr, t, T):
    tv = t - PAD_IN; k = shot_of(tv); SHOTS[k](cv, fr, max(0.0, tv))
    c = CUTS[k]
    if k:
        punch(cv, tv, c, 1.07, .25); glitch(cv, tv, c); flash(cv, tv, c - .02, .1)
    for ti in IMPACTS: shake(cv, tv, ti)
    drift(cv, t, T, .015)

P = PAD_IN
SFX = [(0.0, "braam", .7), (0.0, "boom", .8), (P + w("budgets"), "stamp", .6), (P + w("coach") - .1, "whoosh", .5),
       (P + w("douze"), "stamp", .7), (P + w("pourtant"), "riser", .45), (P + w("ligue") - .05, "boom", .9), (P + w("ligue"), "crowd", .5),
       (P + T_RIB, "rewind", .55), (P + w("national"), "stamp", .6), (P + w("avec") - .15, "whoosh", .5), (P + w("franck"), "camera", .6),
       (P + T_JAN, "typewriter", .55), (P + w("zone") - .45, "whoosh", .4), (P + w("zone"), "siren", .35), (P + w("président") - .05, "camera", .6),
       (P + w("appelle"), "phone", .6), (P + T_ROY, "boom", .8), (P + w("sauve") - .05, "stamp", .9), (P + T_SAI, "whoosh", .5),
       (P + w("troisième") - .05, "stamp", .8), (P + w("troisième"), "crowd", .6), (P + w("qualifié"), "fanfare", .55), (P + w("qualifié"), "goal_roar", .5),
       (P + T_CH, "crowd", .7), (P + w("quand"), "crowd", .55), (P + w("amoureux") - .1, "heart", .5), (P + w("j'suis"), "goal_roar", .6),
       (P + T_STA, "whoosh", .5), (P + w("normes"), "stamp", .8), (P + w("brest", 4), "oldcar", .4),
       (P + T_LA, "drumroll", .5), (P + w("sturm") - .15, "whoosh", .5), (P + w("quatre-zéro") - .15, "whoosh", .5), (P + w("nul") - .15, "whoosh", .5),
       (P + w("dix") - .05, "goal_roar", .7), (P + T_REV, "whoosh", .5), (P + w("psg") + .3, "stamp", .9), (P + w("psg") + .35, "groan", .5),
       (P + w("mais"), "riser", .4), (P + T_TOI, "whoosh", .5), (P + w("dis-le") - .1, "pop2", .6), (P + w("dis-le") + .15, "pop2", .6), (P + w("commentaire"), "notif", .6)]
SCENES = [Scene("brest", TEXTE, draw, SFX, pad_in=P, pad_out=1.4)]

def cover(path):
    cv = background(0, TITLE); paper_bg(cv, 0, NAVY); rays(cv, (CX, 1000), 0, 1.0, 18, 1700, (30, 46, 110), .1)
    big("BREST", "brcv1", 210, BLANC, ROUGE).draw(cv, 0, CX, 250, 1, -3)
    big("EN LIGUE DES CHAMPIONS ?!", "brcv2", 76, NOIR, JAUNE).draw(cv, 0, CX, 440, 1, 2)
    put(cv, "ucl", 790, 820, 520, 1, 8); put(cv, "brest", 290, 860, 520, 1, -8)
    put(cv, "roy", CX, 1450, 720, 1, -3)
    big("L'HISTOIRE FOLLE D'ÉRIC ROY", "brcv3", 60, BLANC, NOIR).draw(cv, 0, CX, 1830, 1, -2)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

def stills(out):
    scene_timing(SCENES, [VOIX]); sc = SCENES[0]; os.makedirs(out, exist_ok=True)
    ts = [P + x for x in (.3, 3.5, 5.7, 9.8, 12.8, 15.2, 17.6, 20.4, 23.4, 25.3, 29.3, 32.6, 38.3, 40.9, 42.4, 45.3)]
    ims = []
    for t in ts:
        f = int(t*FPS); cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T); finish(cv, TITLE); ims.append(cv.resize((216, 384)))
    sheet = Image.new("RGB", (216*8, 2*414), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        x, y = (k % 8)*216, (k//8)*414; sheet.paste(im, (x, y + 30)); dd.text((x + 6, y + 4), f"{ts[k]:.1f}s", font=font("mono", 22), fill=(230, 230, 230))
    p = os.path.join(out, "sheet.jpg"); sheet.save(p, quality=82); return p

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", SLUG)
    if "--stills" in args: print(stills(f"/tmp/{SLUG}_stills")); sys.exit()
    os.makedirs(out, exist_ok=True); cover(os.path.join(out, f"{SLUG}_couverture.jpg"))
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=[VOIX], sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25, limit=True))
