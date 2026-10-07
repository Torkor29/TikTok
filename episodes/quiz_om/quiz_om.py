"""Quiz « Légendes du foot » : « T'es un vrai fan de l'OM si tu as plus de 5/8 » — NIVEAU 1 (format quiz, voir engine/quiz.py).
8 questions QCM (4 réponses, 5 s de chrono) du plus facile au plus dur ; pause après la 3e : « dis ton score en commentaire,
lâche un like et abonne-toi pour le niveau 2 » ; barème final, « abonne-toi pour le niveau 2 ».

  python3 episodes/quiz_om/quiz_om.py output/quiz_om --stills [2,3]
  python3 episodes/quiz_om/quiz_om.py output/quiz_om --cover
  python3 episodes/quiz_om/quiz_om.py output/quiz_om
"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from quiz import *
import engine

TITLE = "~/quiz $ ./om"
SLUG = "quiz_om"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
CTA_AFTER = 3
TEXTES = json.load(open(os.path.join(HERE, "textes_voix.json")))
KEYS, VOICE, TMS = assemble(os.path.join(HERE, "voix"), f"/tmp/{SLUG}_voix", cta_after=CTA_AFTER)
WS, _ = load_words(os.path.join(HERE, "alignement.json"))          # intro, cta, outro
def Wd(k):
    return lambda word, n=1, end=False: PAD_IN + WS[k](word, n, end)

CIEL = (47, 174, 224); CIEL_D = (14, 92, 150); NAVY = (10, 40, 80); BLANC = (250, 250, 246); NOIR = (30, 28, 28)
THEME = dict(du="DE L'OM", accent=CIEL, badge=CIEL_D, bgs=[CIEL_D, NAVY, (30, 130, 190), (12, 62, 112)], ray=(255, 255, 255), ray2=(60, 160, 220),
             niveau="NIVEAU 1", tampon="NIVEAU 1")

OMP = Player("qzom", hair=(40, 30, 24), skin=(206, 160, 124))
BOLI = Player("qzboli", hair=(24, 20, 18), skin=(104, 70, 50))
PAPIN = Player("qzpapin", hair=(110, 80, 50), skin=(232, 190, 156))
SKOB = Player("qzskob", hair=(60, 44, 34), skin=(226, 184, 150))

def hero(cv, fr, t, x, y, s, crown=False):
    OMP.draw(cv, fr, x, y, s, age=1, kit="om", mood="cheer", arms=(150 + 8*math.sin(t*6), 150 - 8*math.sin(t*6)), legs=(10, 10), t=t)
    if crown: crown_on(cv, fr, x, y, s, t, 0)

def mystery(cv, fr, x, y, u, s=1.0):
    """Gros « ? » qui frétille avant la révélation, puis s'envole."""
    a = 1 - prog(u, 0, .4)
    if a > .01: LBL("?", "qzmq", font("title", 150), GOLD, None, stroke=8, stroke_fill=NOIR).draw(cv, fr, x, y - 60*(1 - a), s*a, 8*math.sin(fr*.3))

_sil = {}
def sil(key, P, s, **kw):
    if key not in _sil: _sil[key] = silhouette(P.render_layer(0, s, age=1, kit="om", **kw))
    return _sil[key]

# ------------------------------------------------------------------ illustrations (u = 0 avant la révélation, puis 0 → 1)
def _velo(d, a):
    ax, ay = a
    pts = [(ax - 430 + k*20, ay - 120 - 34*math.sin(k/43*math.pi*3)) for k in range(44)]       # le toit blanc qui ondule
    d.polygon(pts + [(ax + 430, ay - 40), (ax - 430, ay - 40)], fill=(250, 250, 246), outline=(150, 156, 170))
    for k in range(-8, 9): d.line([(ax + k*48, ay - 40), (ax + k*48 - 6, ay + 120)], fill=(150, 154, 166), width=8)
    d.rectangle([ax - 220, ay + 90, ax + 220, ay + 140], fill=(40, 60, 90))
VELO = Paper(ellipse_pts(900, 380, 60), (214, 222, 232), "qzvelo", rough=1.6, hatch=True).add(_velo)
def i1(cv, fr, t, u, tm):
    VELO.draw(cv, fr, CX, ILLU_Y + 20, .66, 0)
    mystery(cv, fr, CX, ILLU_Y - 10, u)
    if u > 0: STAMP("VÉLODROME", "qzs1", CIEL_D, 84).draw(cv, fr, CX, ILLU_Y + 40, slam(u, 0, .4), -4)

def i2(cv, fr, t, u, tm):
    UCL.draw(cv, fr, CX - 240, ILLU_Y + 10, .95, -6 + 3*math.sin(t*3))
    if u <= .1: LBL("19??", "qzy2", font("title", 150), BLANC, NOIR, padx=24, pady=0, rough=2).draw(cv, fr, CX + 150, ILLU_Y, 1, 4)
    else:
        LBL("1993", "qzy2b", font("title", 150), NOIR, GOLD, padx=24, pady=0, rough=2).draw(cv, fr, CX + 150, ILLU_Y, slam(u, .1, .3), 4)
        TAG("1er club français !", "qzt2", PAL["paper"], NOIR, 44).draw(cv, fr, CX + 160, ILLU_Y + 120, pop_in(u, .3, .4), -3)
        confetti(cv, fr, "qzc2", t - tm["te"], 60, 2.5, [CIEL, BLANC, GOLD], (150, 600, 950, 1000))

def i3(cv, fr, t, u, tm):
    x, y, s = CX - 170, ILLU_Y + 165, .52
    draw_ball(cv, fr, x + 70, ILLU_Y - 175 + 10*math.sin(t*5), .45, t*300)
    if u <= .1:
        blit(cv, sil("boli", BOLI, s, mood="happy", arms=(40, 40)), x, y, 1); mystery(cv, fr, x + 250, ILLU_Y - 30, u, .9)
    else:
        BOLI.draw(cv, fr, x, y, s, age=1, kit="om", mood="cheer", arms=(150, 150), t=t)
        LBL("BOLI !", "qzb3", font("title", 110), NOIR, GOLD, padx=24, pady=6, rough=3).draw(cv, fr, CX + 200, ILLU_Y - 40, slam(u, .1, .3), 6)
        TAG("43e minute, de la tête", "qzt3", PAL["paper"], NOIR, 44).draw(cv, fr, CX + 200, ILLU_Y + 80, pop_in(u, .3, .4), -3)

def _om_shield(d, a):
    ax, ay = a
    d.text((ax, ay - 30), "OM", font=font("title", 130), fill=CIEL, anchor="mm", stroke_width=6, stroke_fill=NOIR)
SHIELD = Paper(poly_pts([(-120, -140), (120, -140), (120, 20), (66, 110), (0, 150), (-66, 110), (-120, 20)]), BLANC, "qzshom", rough=1.6, hatch=True).add(_om_shield)
def i4(cv, fr, t, u, tm):
    SHIELD.draw(cv, fr, CX, ILLU_Y - 30, .95, -3)
    txt, bg = ("? ? ?", NOIR) if u <= .1 else ("DROIT AU BUT", CIEL_D)
    LBL(txt, "qzr4", font("title", 76), BLANC, bg, padx=34, pady=6, rough=2).draw(cv, fr, CX, ILLU_Y + 130, 1 if u <= .1 else slam(u, .1, .3), 2)

def i5(cv, fr, t, u, tm):
    draw_ballon_or(cv, fr, CX - 250, ILLU_Y - 30 + 6*math.sin(t*3), 1.0)
    x, y, s = CX + 190, ILLU_Y + 165, .52
    if u <= .1:
        blit(cv, sil("papin", PAPIN, s, mood="happy"), x, y, 1); mystery(cv, fr, x, ILLU_Y - 40, u, .9)
    else:
        PAPIN.draw(cv, fr, x, y, s, age=1, kit="om", mood="cheer", arms=(150, 150), t=t)
        LBL("PAPIN", "qzb5", font("title", 96), NOIR, GOLD, padx=22, pady=4, rough=3).draw(cv, fr, CX - 250, ILLU_Y + 120, slam(u, .1, .3), -5)
        particles(cv, fr, "qzc5", (CX - 250, ILLU_Y - 30), prog(t, tm["te"] + .05, 1.0), 20, 280, [GOLD, BLANC], 16)

PHOTO = Paper(rect_pts(520, 330), (236, 222, 190), "qzphoto", rough=2.2, hatch=True).add(lambda d, a: [
    d.rectangle([a[0] - 230, a[1] - 140, a[0] + 230, a[1] + 140], outline=(120, 96, 70), width=6)])
def i6(cv, fr, t, u, tm):
    PHOTO.draw(cv, fr, CX, ILLU_Y, 1, -3)
    if u <= .1: LBL("????", "qzy6", font("title", 150), (90, 70, 50), None).draw(cv, fr, CX, ILLU_Y, 1, -3)
    else:
        LBL("1899", "qzy6b", font("title", 160), NOIR, GOLD, padx=24, pady=0, rough=2).draw(cv, fr, CX, ILLU_Y - 10, slam(u, .1, .3), -3)
        TAG("31 août 1899", "qzt6", PAL["paper"], NOIR, 46).draw(cv, fr, CX + 200, ILLU_Y + 130, pop_in(u, .3, .4), 4)

SCOREBOARD = scoreboard_sprite(820, 300, "qzscore")
def board(cv, fr, la, lb, a, b, sub="", s=.8, y=ILLU_Y):
    L = layer(900, 400, (450, 200)); SCOREBOARD.draw(L, fr, 450, 200, 1, 0, 1); d = ImageDraw.Draw(L)
    for x_, lab in ((180, la), (720, lb)): d.text((x_, 120), lab, font=font("mono", 64 if len(lab) <= 5 else 44), fill=(200, 196, 190), anchor="mm")
    d.text((450, 210), f"{a} - {b}", font=font("title", 150), fill=(255, 204, 70), anchor="mm")
    if sub: d.text((450, 310), sub, font=font("mono", 36), fill=(170, 166, 160), anchor="mm")
    blit(cv, L, CX, y, s)
def i7(cv, fr, t, u, tm):
    board(cv, fr, "OM", "???" if u <= .05 else "ÉTOILE ROUGE", 0, 0, "Bari, 29 mai 1991" if u <= .05 else "tirs au but : 3-5")
    if u > .1: STAMP("BELGRADE", "qzs7", (200, 30, 44), 70).draw(cv, fr, CX + 200, ILLU_Y + 120, slam(u, .1, .3), -6)

def i8(cv, fr, t, u, tm):
    x, y, s = CX - 190, ILLU_Y + 165, .52
    if u <= .1:
        blit(cv, sil("skob", SKOB, s, mood="happy"), x, y, 1)
        LBL("?? BUTS", "qzp8", font("title", 96), NOIR, GOLD, padx=26, pady=6, rough=3).draw(cv, fr, CX + 170, ILLU_Y - 30, 1, 6 + 2*math.sin(t*4))
    else:
        SKOB.draw(cv, fr, x, y, s, age=1, kit="om", mood="cheer", arms=(150, 150), t=t)
        LBL("44 BUTS", "qzp8b", font("title", 104), NOIR, GOLD, padx=26, pady=6, rough=3).draw(cv, fr, CX + 170, ILLU_Y - 30, slam(u, .1, .3), 6)
        TAG("record de France depuis 1971", "qzt8", PAL["paper"], NOIR, 40).draw(cv, fr, CX + 170, ILLU_Y + 85, pop_in(u, .3, .4), -3)
        confetti(cv, fr, "qzc8", t - tm["te"], 60, 2.5, [CIEL, BLANC, GOLD], (150, 600, 950, 1000))

# ------------------------------------------------------------------ les 8 questions (du plus facile au plus dur)
QUESTIONS = [
    Q("Comment s'appelle le stade de l'OM ?", ["Stade de France", "Vélodrome", "Geoffroy-Guichard", "Parc des Princes"], 1, "FACILE", i1,
      [(.1, "crowd", .6)]),
    Q("L'OM gagne la Ligue des champions en… ?", ["1991", "1998", "2001", "1993"], 3, "FACILE", i2, [(.1, "crowd_long", .7), (.1, "sparkle")]),
    Q("Finale 1993 contre Milan : qui marque le seul but ?", ["Rudi Völler", "Abedi Pelé", "Basile Boli", "Alen Boksic"], 2, "FACILE", i3,
      [(.1, "crowd", .8), (.1, "stamp", .6)]),
    Q("Quelle devise est écrite sur le logo de l'OM ?", ["Droit au but", "Ici c'est Marseille", "À jamais les premiers", "Allez l'OM"], 0,
      "MOYEN", i4, [(.1, "stamp", .7)]),
    Q("Ballon d'or 1991 : quel joueur de l'OM ?", ["Chris Waddle", "Jean-Pierre Papin", "Didier Deschamps", "Eric Cantona"], 1, "MOYEN", i5,
      [(.1, "sparkle"), (.1, "crowd", .6)]),
    Q("En quelle année l'OM a été fondé ?", ["1920", "1932", "1902", "1899"], 3, "MOYEN", i6, [(.1, "stamp", .6)]),
    Q("En 1991, l'OM perd la finale de C1 contre… ?", ["Benfica", "AC Milan", "Étoile rouge Belgrade", "Bayern Munich"], 2, "DIFFICILE", i7,
      [(.0, "groan", .6), (.1, "stamp", .6)]),
    Q("Saison 1970-71 : combien de buts pour Skoblar ?", ["44 buts", "38 buts", "41 buts", "36 buts"], 0, "LA PLUS DURE", i8,
      [(.1, "crowd", .8), (.1, "stamp", .6)]),
]

# ------------------------------------------------------------------ scènes
intro_draw, intro_sfx = intro_scene(THEME, Wd(0), hero)
cta_draw, cta_sfx = cta_score_scene(THEME, Wd(1), after=CTA_AFTER)
outro_draw, outro_sfx = outro_scene(THEME, Wd(2), hero, tag="le niveau 2 arrive bientôt !")
SCENES = []
for k, key in enumerate(KEYS):
    if key == "intro": SCENES.append(Scene("intro", TEXTES["intro"], intro_draw, intro_sfx, pad_in=PAD_IN, pad_out=.2))
    elif key == "cta": SCENES.append(Scene("cta", TEXTES["cta"], cta_draw, cta_sfx, pad_in=PAD_IN, pad_out=.25, trans="punch", trans_dur=.3))
    elif key == "outro": SCENES.append(Scene("fin", TEXTES["outro"], outro_draw, outro_sfx, pad_in=PAD_IN, pad_out=1.2, trans="punch", trans_dur=.3))
    else:
        i = int(key[1:]); q = QUESTIONS[i - 1]; tm = TMS[k]
        SCENES.append(Scene(key, f"{TEXTES[key]}  [chrono 5 s]  {TEXTES['r' + key[1:]]}", question_scene(q, i, 8, tm, THEME, last=i == 8),
                            question_sfx(q, tm), pad_in=PAD_IN, pad_out=.45, trans="whip", trans_dur=.3))

# ------------------------------------------------------------------ couverture, planches
def cover(path): return quiz_cover(path, THEME, hero, TITLE)

def stills(out, only=None):
    scene_timing(SCENES, VOICE); starts = np.cumsum([0] + [sc.T for sc in SCENES])
    os.makedirs(out, exist_ok=True); sheets = []
    for i, sc in enumerate(SCENES):
        if only and (i + 1) not in only: continue
        tm = TMS[i]
        ts_ = ([.05, .4, tm["tq"] - .2, tm["ts"] + 1.2, tm["ts"] + 4.2, tm["te"] + .25, tm["te"] + .9, sc.T - .1] if tm else
               [f*sc.T for f in (.02, .15, .3, .45, .6, .75, .9, .99)])
        prev = engine._last_frame(SCENES, i - 1, starts, TITLE) if (i > 0 and sc.trans) else None
        ims = []
        for t in ts_:
            f = int((starts[i] + t)*FPS); cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T)
            if prev is not None and t < sc.trans_dur: engine.TRANSITIONS[sc.trans](cv, prev, t, sc.trans_dur, i)
            finish(cv, TITLE); ims.append(cv.resize((300, 533)))
        sheet = Image.new("RGB", (300*len(ims), 575), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            sheet.paste(im, (k*300, 42)); dd.text((k*300 + 8, 6), f"S{i+1} {ts_[k]:.1f}/{sc.T:.1f}", font=font("mono", 24), fill=(230, 230, 230))
        p = os.path.join(out, f"qz_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", SLUG)
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", f"/tmp/{SLUG}_stills"), only=only)); sys.exit()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25, limit=True))
