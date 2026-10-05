"""Quiz « Légendes du foot » #1 : « T'es un vrai fan du PSG si tu as plus de 5/8 » (format quiz, voir engine/quiz.py).
8 questions QCM (4 réponses, 5 s de chrono) du plus facile au plus dur ; CTA « abonne-toi + like » après la 4e ; barème final.

  python3 episodes/quiz_psg/quiz_psg.py output/quiz_psg --stills [2,3]
  python3 episodes/quiz_psg/quiz_psg.py output/quiz_psg --cover
  python3 episodes/quiz_psg/quiz_psg.py output/quiz_psg
"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from quiz import *
import engine

TITLE = "~/quiz $ ./psg"
SLUG = "quiz_psg"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
TEXTES = json.load(open(os.path.join(HERE, "textes_voix.json")))
KEYS, VOICE, TMS = assemble(os.path.join(HERE, "voix"), f"/tmp/{SLUG}_voix")
WS, _ = load_words(os.path.join(HERE, "alignement.json"))          # intro, cta, outro
def Wd(k):
    return lambda word, n=1, end=False: PAD_IN + WS[k](word, n, end)

NAVY = (16, 40, 86); NAVY_D = (10, 24, 54); ROUGE = (210, 36, 42); BLANC = (250, 250, 246); NOIR = (30, 28, 28); MAROON = (138, 21, 56)
THEME = dict(du="DU PSG", accent=ROUGE, badge=NAVY, bgs=[NAVY, (112, 22, 40), NAVY_D, (36, 66, 132)], ray=(255, 255, 255), ray2=(40, 70, 140))

PSGP = Player("qzpsg", hair=(70, 50, 36), skin=(230, 186, 150))
NEY = Player("qzney", hair=(48, 34, 26), skin=(196, 146, 108), hair_style="quiff")
MBAP = Player("qzmbap", hair=(24, 20, 18), skin=(126, 86, 62), hair_style="bald")

def hero(cv, fr, t, x, y, s, crown=False):
    PSGP.draw(cv, fr, x, y, s, age=1, kit="psg", mood="cheer", arms=(150 + 8*math.sin(t*6), 150 - 8*math.sin(t*6)), legs=(10, 10), t=t)
    if crown: crown_on(cv, fr, x, y, s, t, 0)

def mystery(cv, fr, x, y, u, s=1.0):
    """Gros « ? » qui frétille avant la révélation, puis s'envole."""
    a = 1 - prog(u, 0, .4)
    if a > .01: LBL("?", "qzmq", font("title", 150), GOLD, None, stroke=8, stroke_fill=NOIR).draw(cv, fr, x, y - 60*(1 - a), s*a, 8*math.sin(fr*.3))

# ------------------------------------------------------------------ illustrations (u = 0 avant la révélation, puis 0 → 1)
def _parc(d, a):
    ax, ay = a
    for k in range(-8, 9):   # les « peignes » de béton du Parc des Princes
        x = ax + k*50; d.line([(x, ay-150 + abs(k)*6), (x - 10, ay+120)], fill=(150, 154, 166), width=10)
    d.rectangle([ax-200, ay+80, ax+200, ay+140], fill=(60, 64, 80))
PARC = Paper(ellipse_pts(900, 380, 60), (214, 218, 226), "qzparc", rough=1.6, hatch=True).add(_parc)
def i1(cv, fr, t, u, tm):
    PARC.draw(cv, fr, CX, ILLU_Y + 10, .66, 0)
    mystery(cv, fr, CX, ILLU_Y - 20, u)
    if u > 0: STAMP("PARC DES PRINCES", "qzs1", NAVY, 70).draw(cv, fr, CX, ILLU_Y + 40, slam(u, 0, .4), -4)

def flag(cv, x, y, w, h, t, qatar=False):
    """Drapeau qui ondule : blanc avec « ? » (avant), ou Qatar (bordeaux, bande blanche dentelée)."""
    L = layer(int(w + 40), int(h + 60), (w/2 + 20, h/2 + 30)); d = ImageDraw.Draw(L); n = 26
    for k in range(n):
        off = 10*math.sin(k/n*math.pi*2 - t*5)*(k/n); x0 = 20 + k*w/n
        d.rectangle([x0, 30 + off, x0 + w/n + 1, 30 + h + off], fill=BLANC if (not qatar or k < n*.3) else MAROON)
    if qatar:
        xb = 20 + w*.3; pts = [(xb - 2, 30)]
        for k in range(9): pts += [(xb + w*.08, 30 + (k + .5)*h/9), (xb - 2, 30 + (k + 1)*h/9)]
        d.polygon(pts + [(xb + w*.1, 30 + h), (xb + w*.1, 30)], fill=MAROON)
    else: d.text((20 + w/2, 30 + h/2), "?", font=font("title", 130), fill=NOIR, anchor="mm")
    blit(cv, L, x, y, 1, 0, 1)
def i2(cv, fr, t, u, tm):
    d = ImageDraw.Draw(cv); px = CX - 190
    d.rectangle([px - 8, ILLU_Y - 150, px + 8, ILLU_Y + 150], fill=(200, 196, 190)); d.ellipse([px - 16, ILLU_Y - 170, px + 16, ILLU_Y - 138], fill=GOLD)
    flag(cv, px + 175, ILLU_Y - 50, 330, 200, t, qatar=u > .15)
    LBL("2011", "qzy2", font("title", 80), BLANC, NOIR, padx=20, pady=2, rough=2).draw(cv, fr, CX + 330, ILLU_Y + 110, 1, 6)

def i3(cv, fr, t, u, tm):
    NEY.draw(cv, fr, CX - 190, ILLU_Y + 165, .52, age=1, kit="psg", mood="happy" if u else "normal", t=t)
    if u <= .1: LBL("??? M€", "qzp3", font("title", 96), NOIR, GOLD, padx=26, pady=6, rough=3).draw(cv, fr, CX + 160, ILLU_Y - 30, 1, 6 + 2*math.sin(t*4))
    else:
        LBL("222 M€", "qzp3b", font("title", 110), NOIR, GOLD, padx=26, pady=6, rough=3).draw(cv, fr, CX + 160, ILLU_Y - 30, slam(u, .1, .3), 6)
        TAG("record du monde", "qzt3", PAL["paper"], NOIR, 44).draw(cv, fr, CX + 170, ILLU_Y + 90, pop_in(u, .3, .4), -3)
        particles(cv, fr, "qzc3", (CX + 160, ILLU_Y - 30), prog(t, tm["te"] + .05, 1.0), 22, 300, [GOLD, (60, 160, 80), BLANC], 18)

def _shield(key, col, col2, txt, size=52, band=False):
    def dec(d, a):
        ax, ay = a
        if band: d.rectangle([ax-30, ay-130, ax+30, ay+140], fill=BLANC); d.rectangle([ax-20, ay-130, ax+20, ay+140], fill=ROUGE)
        else: d.polygon([(ax-110, ay-130), (ax, ay-130), (ax, ay+140), (ax-60, ay+100), (ax-110, ay+10)], fill=col2)
        if txt: d.text((ax, ay-10), txt, font=font("title", size), fill=BLANC, anchor="mm", stroke_width=5, stroke_fill=NOIR)
    return Paper(poly_pts([(-110, -130), (110, -130), (110, 10), (60, 100), (0, 140), (-60, 100), (-110, 10)]), col, key, rough=1.6, hatch=True).add(dec)
SH_PSG = _shield("qzshpsg", NAVY, NAVY, "PSG", 70, band=True)
SH_PFC = _shield("qzshpfc", (30, 60, 140), (60, 120, 200), "PARIS\nFC", 48)
SH_SG = _shield("qzshsg", (40, 120, 70), BLANC, "ST-\nGERMAIN", 40)
SH_Q = _shield("qzshq", (90, 90, 100), (120, 120, 130), "?", 120)
def i4(cv, fr, t, u, tm):
    SH_PSG.draw(cv, fr, CX - 210, ILLU_Y, .95, -4)
    if u <= .1: LBL("19??", "qzy4", font("title", 150), BLANC, NOIR, padx=24, pady=0, rough=2).draw(cv, fr, CX + 150, ILLU_Y, 1, 4)
    else:
        LBL("1970", "qzy4b", font("title", 150), NOIR, GOLD, padx=24, pady=0, rough=2).draw(cv, fr, CX + 150, ILLU_Y, slam(u, .1, .3), 4)
        confetti(cv, fr, "qzc4", t - tm["te"], 50, 2.5, [NAVY, ROUGE, BLANC], (200, 600, 900, 1000))

SCOREBOARD = scoreboard_sprite(820, 300, "qzscore")
def board(cv, fr, la, lb, a, b, sub="", s=.8, y=ILLU_Y):
    L = layer(900, 400, (450, 200)); SCOREBOARD.draw(L, fr, 450, 200, 1, 0, 1); d = ImageDraw.Draw(L)
    for x_, lab in ((180, la), (720, lb)): d.text((x_, 120), lab, font=font("mono", 64 if len(lab) <= 5 else 48), fill=(200, 196, 190), anchor="mm")
    d.text((450, 210), f"{a} - {b}", font=font("title", 150), fill=(255, 204, 70), anchor="mm")
    if sub: d.text((450, 310), sub, font=font("mono", 36), fill=(170, 166, 160), anchor="mm")
    blit(cv, L, CX, y, s)
def i5(cv, fr, t, u, tm):
    board(cv, fr, "???" if u <= .05 else "BARÇA", "PSG", 6, 1, "8 mars 2017" if u > .05 else "")
    if 0 < u < .25: glitch(cv, fr, u, 0, .25, 18)
    if u > .1: STAMP("REMONTADA", "qzs5", ROUGE, 70).draw(cv, fr, CX + 200, ILLU_Y + 115, slam(u, .1, .3), -6)
def i6(cv, fr, t, u, tm):
    board(cv, fr, "PSG", "INTER", "?" if u <= .05 else 5, "?" if u <= .05 else 0, "finale 2025" if u <= .05 else "31 mai 2025, Munich")
    if u > 0:
        UCL.draw(cv, fr, CX - 400, ILLU_Y + 10, .55*slam(u, .1, .3), -10)
        confetti(cv, fr, "qzc6", t - tm["te"], 70, 3, [GOLD, BLANC, ROUGE])
def i7(cv, fr, t, u, tm):
    SH_PFC.draw(cv, fr, CX - 250, ILLU_Y, .85, -5)
    LBL("+", "qzplus", font("title", 140), BLANC, None, stroke=6, stroke_fill=NOIR).draw(cv, fr, CX - 40, ILLU_Y, 1, 0)
    (SH_SG if u > .1 else SH_Q).draw(cv, fr, CX + 170, ILLU_Y, .85*(slam(u, .1, .3) if u > .1 else 1), 5)
    if u > .3: LBL("= PSG", "qzeq7", font("title", 90), BLANC, NAVY, padx=20, pady=4, rough=2).draw(cv, fr, CX + 320, ILLU_Y + 125, pop_in(u, .3, .4), -6)
_sil = {}
def i8(cv, fr, t, u, tm):
    x, y, s = CX - 150, ILLU_Y + 165, .52
    if u <= .1:
        if "m" not in _sil: _sil["m"] = silhouette(MBAP.render_layer(0, s, age=1, kit="psg", mood="happy"))
        blit(cv, _sil["m"], x, y, 1); mystery(cv, fr, x, ILLU_Y - 40, u, .9)
    else:
        MBAP.draw(cv, fr, x, y, s, age=1, kit="psg", mood="cheer", arms=(150, 150), t=t)
        LBL("256 BUTS", "qzb8", font("title", 92), NOIR, GOLD, padx=24, pady=6, rough=3).draw(cv, fr, CX + 210, ILLU_Y - 40, slam(u, .1, .3), 6)
        TAG("devant Cavani (200)", "qzt8", PAL["paper"], NOIR, 44).draw(cv, fr, CX + 210, ILLU_Y + 80, pop_in(u, .3, .4), -3)

# ------------------------------------------------------------------ les 8 questions (du plus facile au plus dur)
QUESTIONS = [
    Q("Comment s'appelle le stade du PSG ?", ["Stade de France", "Parc des Princes", "Stade Charléty", "Stade Jean-Bouin"], 1, "FACILE", i1,
      [(.1, "crowd", .6)]),
    Q("En 2011, le PSG est racheté par… quel pays ?", ["Arabie saoudite", "Émirats arabes unis", "Bahreïn", "Qatar"], 3, "FACILE", i2,
      [(.1, "whoosh", .4)]),
    Q("Combien le PSG a payé Neymar en 2017 ?", ["145 M€", "180 M€", "222 M€", "250 M€"], 2, "FACILE", i3, [(.1, "cash", .8)]),
    Q("En quelle année le PSG a été créé ?", ["1970", "1904", "1932", "1974"], 0, "MOYEN", i4, [(.1, "stamp", .6)]),
    Q("Contre qui le PSG a subi la remontada en 2017 ?", ["Real Madrid", "FC Barcelone", "Manchester United", "Bayern Munich"], 1, "MOYEN", i5,
      [(.0, "glitch", .6), (.1, "stamp", .6)]),
    Q("Finale de C1 2025 contre l'Inter : quel score ?", ["1 - 0", "2 - 1", "3 - 1", "5 - 0"], 3, "MOYEN", i6,
      [(.1, "crowd_long", .7), (.1, "sparkle")]),
    Q("Le PSG est né d'une fusion entre le Paris FC et… ?", ["Racing Club de Paris", "Red Star", "Stade Saint-Germain", "Stade français"], 2,
      "DIFFICILE", i7, [(.1, "stamp", .6), (.4, "pop2")]),
    Q("Qui est le meilleur buteur de l'histoire du PSG ?", ["Kylian Mbappé", "Edinson Cavani", "Zlatan Ibrahimovic", "Pauleta"], 0,
      "LA PLUS DURE", i8, [(.1, "crowd", .8), (.1, "stamp", .6)]),
]

# ------------------------------------------------------------------ scènes
intro_draw, intro_sfx = intro_scene(THEME, Wd(0), hero)
cta_draw, cta_sfx = cta_scene(THEME, Wd(1))
outro_draw, outro_sfx = outro_scene(THEME, Wd(2), hero)
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
