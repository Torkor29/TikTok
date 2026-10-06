"""Quiz « Légendes du foot » #2 : PSG NIVEAU 2 (plus dur) — « T'es un vrai fan du PSG si tu as plus de 5/8 » (format : engine/quiz.py).
8 questions plus pointues (1er titre, Luis Enrique, Arsenal 2026, N'Gotty, Rapid Vienne, Coman, Kombouaré, Marquinhos) ;
CTA « abonne-toi + like » après la 4e (même voix que le quiz #1) ; barème final (même voix que le quiz #1).

  python3 episodes/quiz_psg2/quiz_psg2.py output/quiz_psg2 --stills [2,3]
  python3 episodes/quiz_psg2/quiz_psg2.py output/quiz_psg2 --cover
  python3 episodes/quiz_psg2/quiz_psg2.py output/quiz_psg2
Voix en attente (crédits ElevenLabs) : python3 scripts/minutage_provisoire_quiz.py episodes/quiz_psg2 <dossier>,
puis LEGENDES_PROVISOIRE=<dossier> … --stills | --apercu.
"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from quiz import *
import engine

TITLE = "~/quiz $ ./psg2"
SLUG = "quiz_psg2"
SRC = os.environ.get("LEGENDES_PROVISOIRE") or HERE
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
TEXTES = json.load(open(os.path.join(HERE, "textes_voix.json")))
KEYS, VOICE, TMS = assemble(os.path.join(SRC, "voix"), f"/tmp/{SLUG}_voix")
WS, _ = load_words(os.path.join(SRC, "alignement.json"))          # intro, cta, outro
def Wd(k):
    return lambda word, n=1, end=False: PAD_IN + WS[k](word, n, end)

NAVY = (16, 40, 86); NAVY_D = (10, 24, 54); ROUGE = (210, 36, 42); BLANC = (250, 250, 246); NOIR = (30, 28, 28)
THEME = dict(du="DU PSG", accent=ROUGE, badge=NAVY, bgs=[NAVY_D, (96, 16, 34), (24, 30, 60), (30, 56, 116)], ray=(255, 255, 255),
             ray2=(40, 70, 140), niveau="NIVEAU 2", tampon="NIVEAU 2")

PSGP = Player("qz2psg", hair=(70, 50, 36), skin=(230, 186, 150))
COACH = Player("qz2coach", hair=(150, 150, 150), skin=(226, 176, 140))
NGOT = Player("qz2ngot", hair=(24, 20, 18), skin=(104, 70, 50))
COMAN = Player("qz2coman", hair=(24, 20, 18), skin=(126, 86, 62))
KOMB = Player("qz2komb", hair=(30, 26, 22), skin=(150, 106, 78))
MARQ = Player("qz2marq", hair=(30, 24, 20), beard_col=(40, 30, 26), skin=(200, 150, 112))

def hero(cv, fr, t, x, y, s, crown=False):
    PSGP.draw(cv, fr, x, y, s, age=1, kit="psg", mood="cheer", arms=(150 + 8*math.sin(t*6), 150 - 8*math.sin(t*6)), legs=(10, 10), t=t)
    if crown: crown_on(cv, fr, x, y, s, t, 0)

def mystery(cv, fr, x, y, u, s=1.0):
    a = 1 - prog(u, 0, .4)
    if a > .01: LBL("?", "qz2mq", font("title", 150), GOLD, None, stroke=8, stroke_fill=NOIR).draw(cv, fr, x, y - 60*(1 - a), s*a, 8*math.sin(fr*.3))

_sil = {}
def sil(key, pl, s, **kw):
    """Silhouette noire d'un joueur (cache), pour ne pas donner la réponse avant la révélation."""
    if key not in _sil: _sil[key] = silhouette(pl.render_layer(0, s, age=1, **kw))
    return _sil[key]

def reveal_label(cv, fr, txt, key, x, y, u, size=86, bg=GOLD, rot=6):
    if u > .1: LBL(txt, key, font("title", size), NOIR, bg, padx=22, pady=6, rough=3).draw(cv, fr, x, y, slam(u, .1, .3), rot)

SCOREBOARD = scoreboard_sprite(820, 300, "qz2score")
def board(cv, fr, la, lb, a, b, sub="", s=.8, y=ILLU_Y):
    L = layer(900, 400, (450, 200)); SCOREBOARD.draw(L, fr, 450, 200, 1, 0, 1); d = ImageDraw.Draw(L)
    for x_, lab in ((180, la), (720, lb)): d.text((x_, 120), lab, font=font("mono", 64 if len(lab) <= 5 else 48), fill=(200, 196, 190), anchor="mm")
    d.text((450, 210), f"{a} - {b}", font=font("title", 150), fill=(255, 204, 70), anchor="mm")
    if sub: d.text((450, 310), sub, font=font("mono", 36), fill=(170, 166, 160), anchor="mm")
    blit(cv, L, CX, y, s)

# ------------------------------------------------------------------ illustrations (u = 0 avant la révélation, puis 0 → 1)
def i1(cv, fr, t, u, tm):      # 1er titre de champion : 1986
    CUP.draw(cv, fr, CX - 220, ILLU_Y + 20, 1.25, -5)
    if u <= .1: LBL("19??", "qz2y1", font("title", 150), BLANC, NOIR, padx=24, pady=0, rough=2).draw(cv, fr, CX + 150, ILLU_Y, 1, 4)
    else:
        LBL("1986", "qz2y1b", font("title", 150), NOIR, GOLD, padx=24, pady=0, rough=2).draw(cv, fr, CX + 150, ILLU_Y, slam(u, .1, .3), 4)
        confetti(cv, fr, "qz2c1", t - tm["te"], 50, 2.5, [NAVY, ROUGE, BLANC], (200, 600, 900, 1000))

def i2(cv, fr, t, u, tm):      # entraîneur du 1er sacre en C1 : Luis Enrique
    x, y, s = CX - 170, ILLU_Y + 165, .5
    UCL.draw(cv, fr, CX + 230, ILLU_Y - 10, .75, 6)
    if u <= .1: blit(cv, sil("coach", COACH, s, kit="suit", mood="happy"), x, y, 1); mystery(cv, fr, x, ILLU_Y - 50, u, .8)
    else:
        COACH.draw(cv, fr, x, y, s, age=1, kit="suit", mood="cheer", arms=(150, 150), t=t)
        reveal_label(cv, fr, "LUIS ENRIQUE", "qz2n2", CX + 160, ILLU_Y + 130, u, 66)

def i3(cv, fr, t, u, tm):      # finale 2026 : Arsenal
    board(cv, fr, "PSG", "???" if u <= .05 else "ARSENAL", 1, 1, "4-3 aux tirs au but · 2026")
    if u > .1: confetti(cv, fr, "qz2c3", t - tm["te"], 70, 3, [GOLD, BLANC, ROUGE])

def i4(cv, fr, t, u, tm):      # 1996, but de la finale : N'Gotty sur coup franc
    x, y, s = CX - 170, ILLU_Y + 165, .5
    LBL("COUPE DES COUPES 1996", "qz2t4", font("title", 44), BLANC, NAVY, padx=16, pady=4, rough=2).draw(cv, fr, CX + 190, ILLU_Y - 110, 1, 5)
    if u <= .1: blit(cv, sil("ngot", NGOT, s, kit="psg", mood="determined"), x, y, 1); mystery(cv, fr, x, ILLU_Y - 50, u, .8)
    else:
        NGOT.draw(cv, fr, x, y, s, age=1, kit="psg", mood="cheer", arms=(150, 150), t=t)
        reveal_label(cv, fr, "N'GOTTY", "qz2n4", CX + 190, ILLU_Y + 20, u, 90)
        TAG("sur coup franc", "qz2t4b", PAL["paper"], NOIR, 44).draw(cv, fr, CX + 190, ILLU_Y + 130, pop_in(u, .3, .4), -3)

def i5(cv, fr, t, u, tm):      # finale 1996 : Rapid Vienne
    board(cv, fr, "PSG", "???" if u <= .05 else "RAPID", 1, 0, "finale 1996" if u <= .05 else "8 mai 1996, Bruxelles")
    if u > .1: UCL.draw(cv, fr, CX - 400, ILLU_Y + 10, .5*slam(u, .1, .3), -10)

def i6(cv, fr, t, u, tm):      # finale 2020 : Kingsley Coman, formé au PSG
    board(cv, fr, "PSG", "BAYERN", 0, 1, "finale 2020", s=.62, y=ILLU_Y - 70)
    x, y, s = CX + 250, ILLU_Y + 175, .36
    if u <= .1: blit(cv, sil("coman", COMAN, s, kit="manutd", mood="cheer", arms=(150, 150)), x, y, 1); mystery(cv, fr, x, ILLU_Y + 20, u, .6)
    else:
        COMAN.draw(cv, fr, x, y, s, age=1, kit="manutd", mood="cheer", arms=(150, 150), t=t)
        reveal_label(cv, fr, "COMAN", "qz2n6", CX - 170, ILLU_Y + 100, u, 80)
        TAG("formé au PSG !", "qz2t6", PAL["paper"], NOIR, 44).draw(cv, fr, CX - 170, ILLU_Y + 185, pop_in(u, .3, .4), -3)

def i7(cv, fr, t, u, tm):      # entraîneur au rachat du Qatar (2011) : Kombouaré
    x, y, s = CX - 170, ILLU_Y + 165, .5
    LBL("2011", "qz2t7", font("title", 80), BLANC, NOIR, padx=20, pady=2, rough=2).draw(cv, fr, CX + 250, ILLU_Y - 110, 1, 6)
    if u <= .1: blit(cv, sil("komb", KOMB, s, kit="suit", mood="happy"), x, y, 1); mystery(cv, fr, x, ILLU_Y - 50, u, .8)
    else:
        KOMB.draw(cv, fr, x, y, s, age=1, kit="suit", mood="happy", arms=(40, 40), t=t)
        reveal_label(cv, fr, "KOMBOUARÉ", "qz2n7", CX + 170, ILLU_Y + 60, u, 76)

def i8(cv, fr, t, u, tm):      # joueur le plus capé : Marquinhos
    x, y, s = CX - 150, ILLU_Y + 165, .52
    if u <= .1: blit(cv, sil("marq", MARQ, s, kit="psg", mood="happy", beard=True), x, y, 1); mystery(cv, fr, x, ILLU_Y - 40, u, .9)
    else:
        MARQ.draw(cv, fr, x, y, s, age=1, kit="psg", mood="cheer", arms=(150, 150), beard=True, t=t)
        reveal_label(cv, fr, "MARQUINHOS", "qz2n8", CX + 190, ILLU_Y - 40, u, 76)
        TAG("record battu en 2024", "qz2t8", PAL["paper"], NOIR, 44).draw(cv, fr, CX + 190, ILLU_Y + 70, pop_in(u, .3, .4), -3)

# ------------------------------------------------------------------ les 8 questions (niveau 2 : du moyen au très dur)
QUESTIONS = [
    Q("1er titre de champion de France du PSG ?", ["1982", "1994", "1986", "1996"], 2, "MOYEN", i1, [(.1, "stamp", .6), (.1, "crowd", .6)]),
    Q("Son coach lors de la 1re C1, en 2025 ?", ["Luis Enrique", "Thomas Tuchel", "Mauricio Pochettino", "Christophe Galtier"], 0, "MOYEN", i2,
      [(.1, "crowd", .7)]),
    Q("2026 : la 2e C1, contre qui ?", ["Inter Milan", "Real Madrid", "Liverpool", "Arsenal"], 3, "MOYEN", i3, [(.1, "crowd_long", .7), (.1, "sparkle")]),
    Q("Finale de la Coupe des coupes 1996 : qui marque ?", ["Rai", "Bruno N'Gotty", "Youri Djorkaeff", "Patrice Loko"], 1, "DIFFICILE", i4,
      [(.0, "kick", .6), (.1, "crowd", .7)]),
    Q("Et cette finale 1996, contre quel club ?", ["Parme", "Ajax", "Rapid Vienne", "Arsenal"], 2, "DIFFICILE", i5, [(.1, "stamp", .6)]),
    Q("Finale 2020 : qui marque pour le Bayern ?", ["Kingsley Coman", "Robert Lewandowski", "Thomas Müller", "Serge Gnabry"], 0, "DIFFICILE", i6,
      [(.1, "groan", .6), (.3, "stamp", .5)]),
    Q("Qui entraînait le PSG au rachat du Qatar (2011) ?", ["Carlo Ancelotti", "Laurent Blanc", "Paul Le Guen", "Antoine Kombouaré"], 3, "TRÈS DUR", i7,
      [(.1, "stamp", .6), (.4, "pop2")]),
    Q("Le joueur le plus capé de l'histoire du PSG ?", ["Thiago Silva", "Marquinhos", "Jean-Marc Pilorget", "Marco Verratti"], 1, "LA PLUS DURE", i8,
      [(.1, "crowd", .8), (.1, "stamp", .6)]),
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
            sheet.paste(im, (k*300 + 0, 42)); dd.text((k*300 + 8, 6), f"S{i+1} {ts_[k]:.1f}/{sc.T:.1f}", font=font("mono", 24), fill=(230, 230, 230))
        p = os.path.join(out, f"qz2_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", SLUG)
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", f"/tmp/{SLUG}_stills"), only=only)); sys.exit()
    if os.environ.get("LEGENDES_PROVISOIRE") and "--apercu" not in args:
        sys.exit("Minutage provisoire : pas de rendu final sans les vraies voix (--apercu pour un aperçu muet).")
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25, limit=True))
