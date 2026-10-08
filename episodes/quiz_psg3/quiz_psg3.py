"""Quiz « Légendes du foot » : « Fan du PSG ? T'es un vrai fan si tu as plus de 6/8 » — NIVEAU 3 (format quiz, voir engine/quiz.py).
8 questions QCM très pointues (4 réponses, chrono raccourci à 4 s) ; son de hook en ouverture ; pause après la 4e :
« alors, tu vas pleurer ou c'est trop dur maintenant ? » + abonne-toi / like ; barème final.

  python3 episodes/quiz_psg3/quiz_psg3.py output/quiz_psg3 --stills [2,3]
  python3 episodes/quiz_psg3/quiz_psg3.py output/quiz_psg3 --cover
  python3 episodes/quiz_psg3/quiz_psg3.py output/quiz_psg3
"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import quiz
quiz.CHRONO = 4.0                      # niveau 3 : 4 secondes pour répondre (lu à l'exécution par assemble / chrono)
from quiz import *
import engine

TITLE = "~/quiz $ ./psg --niveau 3"
SLUG = "quiz_psg3"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
CTA_AFTER = 4
HOOK_PAD = .85                         # le son de hook joue seul avant la voix
TEXTES = json.load(open(os.path.join(HERE, "textes_voix.json")))
KEYS, VOICE, TMS = assemble(os.path.join(HERE, "voix"), f"/tmp/{SLUG}_voix", cta_after=CTA_AFTER)
WS, _ = load_words(os.path.join(HERE, "alignement.json"))          # intro, cta, outro
def Wd(k, pad=PAD_IN):
    return lambda word, n=1, end=False: pad + WS[k](word, n, end)

NAVY = (16, 40, 86); NAVY_D = (10, 24, 54); ROUGE = (210, 36, 42); BLANC = (250, 250, 246); NOIR = (30, 28, 28)
VERT = (40, 120, 70); BORDEAUX = (120, 30, 50)
THEME = dict(du="DU PSG", accent=ROUGE, badge=NAVY, bgs=[NAVY, (112, 22, 40), NAVY_D, (36, 66, 132)], ray=(255, 255, 255), ray2=(40, 70, 140),
             seuil=6, niveau="NIVEAU 3", tampon="NIVEAU 3", mot_chrono=("quatre", 1))

PSGP = Player("qz3psg", hair=(30, 24, 20), skin=(214, 168, 132))
HAKI = Player("qz3haki", hair=(20, 16, 14), skin=(170, 120, 86))
PAUL = Player("qz3paul", hair=(16, 14, 12), skin=(214, 170, 136))

def hero(cv, fr, t, x, y, s, crown=False):
    PSGP.draw(cv, fr, x, y, s, age=1, kit="psg", mood="cheer", arms=(150 + 8*math.sin(t*6), 150 - 8*math.sin(t*6)), legs=(10, 10), t=t)
    if crown: crown_on(cv, fr, x, y, s, t, 0)

def mystery(cv, fr, x, y, u, s=1.0):
    a = 1 - prog(u, 0, .4)
    if a > .01: LBL("?", "qz3mq", font("title", 150), GOLD, None, stroke=8, stroke_fill=NOIR).draw(cv, fr, x, y - 60*(1 - a), s*a, 8*math.sin(fr*.3))

_sil = {}
def sil(key, P, s, **kw):
    if key not in _sil: _sil[key] = silhouette(P.render_layer(0, s, age=1, kit="psg", **kw))
    return _sil[key]

SCOREBOARD = scoreboard_sprite(820, 300, "qz3score")
def board(cv, fr, la, lb, a, b, sub="", s=.8, y=ILLU_Y):
    L = layer(900, 400, (450, 200)); SCOREBOARD.draw(L, fr, 450, 200, 1, 0, 1); d = ImageDraw.Draw(L)
    for x_, lab in ((180, la), (720, lb)): d.text((x_, 120), lab, font=font("mono", 64 if len(lab) <= 5 else 40), fill=(200, 196, 190), anchor="mm")
    d.text((450, 210), f"{a} - {b}", font=font("title", 150), fill=(255, 204, 70), anchor="mm")
    if sub: d.text((450, 310), sub, font=font("mono", 36), fill=(170, 166, 160), anchor="mm")
    blit(cv, L, CX, y, s)

# ------------------------------------------------------------------ illustrations (u = 0 avant la révélation, puis 0 → 1)
CARD = Paper(rect_pts(560, 360), (236, 222, 190), "qz3card", rough=2.2, hatch=True)
def i1(cv, fr, t, u, tm):
    CARD.draw(cv, fr, CX, ILLU_Y, 1, -3)
    if u <= .1:
        LBL("MASCOTTE", "qz3m1", font("title", 70), NOIR, None).draw(cv, fr, CX, ILLU_Y - 100, 1, -3); mystery(cv, fr, CX, ILLU_Y + 40, u)
    else:
        LBL("GERMAIN", "qz3m1b", font("title", 120), BLANC, NAVY, padx=24, pady=4, rough=2).draw(cv, fr, CX, ILLU_Y - 30, slam(u, .1, .3), -3)
        TAG("le lynx, depuis 2010", "qz3t1", GOLD, NOIR, 46).draw(cv, fr, CX + 100, ILLU_Y + 110, pop_in(u, .3, .4), 3)

def i2(cv, fr, t, u, tm):
    UCL.draw(cv, fr, CX + 240, ILLU_Y + 10, .9, 6 + 3*math.sin(t*3))
    x, y, s = CX - 190, ILLU_Y + 165, .52
    if u <= .1:
        blit(cv, sil("haki", HAKI, s, mood="happy"), x, y, 1); mystery(cv, fr, x, ILLU_Y - 40, u, .9)
    else:
        HAKI.draw(cv, fr, x, y, s, age=1, kit="psg", mood="cheer", arms=(150, 150), t=t)
        LBL("HAKIMI", "qz3b2", font("title", 100), NOIR, GOLD, padx=22, pady=4, rough=3).draw(cv, fr, CX + 200, ILLU_Y - 60, slam(u, .1, .3), 6)
        TAG("12e minute, 1-0", "qz3t2", PAL["paper"], NOIR, 44).draw(cv, fr, CX + 200, ILLU_Y + 60, pop_in(u, .3, .4), -3)

def i3(cv, fr, t, u, tm):
    board(cv, fr, "PSG", "???" if u <= .05 else "VILLA", "?" if u <= .05 else 5, "?" if u <= .05 else 4,
          "1/4 de finale C1 2025" if u <= .05 else "score cumulé")
    if u > .1: STAMP("ASTON VILLA", "qz3s3", BORDEAUX, 70).draw(cv, fr, CX + 160, ILLU_Y + 130, slam(u, .1, .3), -6)

def i4(cv, fr, t, u, tm):
    x, y, s = CX - 200, ILLU_Y + 165, .52
    PSGP.draw(cv, fr, x, y, s, age=1, kit="psg", mood="happy", arms=(40, 40), t=t)
    LBL("1973", "qz3y4", font("title", 110), NOIR, GOLD, padx=20, pady=0, rough=2).draw(cv, fr, CX + 190, ILLU_Y - 110, 1, 4)
    if u <= .1: mystery(cv, fr, CX + 190, ILLU_Y + 60, u, .9)
    else:
        LBL("HECHTER", "qz3b4", font("title", 96), BLANC, NAVY, padx=22, pady=4, rough=3).draw(cv, fr, CX + 190, ILLU_Y + 40, slam(u, .1, .3), -4)
        TAG("président et couturier", "qz3t4", PAL["paper"], NOIR, 40).draw(cv, fr, CX + 190, ILLU_Y + 150, pop_in(u, .3, .4), 3)

def i5(cv, fr, t, u, tm):
    board(cv, fr, "PSG", "???" if u <= .05 else "ST-ÉTIENNE", 2, 2, "Parc, 15 mai 1982" if u <= .05 else "t.a.b. 6-5")
    if u > .1:
        STAMP("1er TROPHÉE", "qz3s5", ROUGE, 70).draw(cv, fr, CX + 170, ILLU_Y + 130, slam(u, .1, .3), -6)
        confetti(cv, fr, "qz3c5", t - tm["te"], 60, 2.5, [NAVY, ROUGE, BLANC], (150, 600, 950, 1000))

def i6(cv, fr, t, u, tm):
    board(cv, fr, "PSG", "GUINGAMP", "?" if u <= .05 else 9, 0, "19 janvier 2019")
    if u > .1: STAMP("CARTON !", "qz3s6", ROUGE, 80).draw(cv, fr, CX + 170, ILLU_Y + 130, slam(u, .1, .3), -6)

def i7(cv, fr, t, u, tm):
    x, y, s = CX - 190, ILLU_Y + 165, .52
    if u <= .1:
        blit(cv, sil("paul", PAUL, s, mood="happy", arms=(150, 150)), x, y, 1)
        LBL("PAULETA", "qz3p7", font("title", 90), BLANC, NAVY, padx=22, pady=4, rough=3).draw(cv, fr, CX + 190, ILLU_Y - 60, 1, 5)
        mystery(cv, fr, CX + 190, ILLU_Y + 80, u, .8)
    else:
        PAUL.draw(cv, fr, x, y, s, age=1, kit="psg", mood="cheer", arms=(160, 160), t=t)
        LBL("PAULETA", "qz3p7", font("title", 90), BLANC, NAVY, padx=22, pady=4, rough=3).draw(cv, fr, CX + 190, ILLU_Y - 60, 1, 5)
        TAG("l'Aigle des Açores", "qz3t7", GOLD, NOIR, 50).draw(cv, fr, CX + 190, ILLU_Y + 60, slam(u, .1, .3), -3)

def i8(cv, fr, t, u, tm):
    board(cv, fr, "PSG", "???" if u <= .05 else "CÔTE CHAUDE", 10, 0, "Coupe de France 1994" if u <= .05 else "club amateur")
    if u > .1:
        STAMP("RECORD", "qz3s8", ROUGE, 84).draw(cv, fr, CX + 170, ILLU_Y + 130, slam(u, .1, .3), -6)
        confetti(cv, fr, "qz3c8", t - tm["te"], 60, 2.5, [NAVY, ROUGE, BLANC, GOLD], (150, 600, 950, 1000))

# ------------------------------------------------------------------ les 8 questions (niveau 3 : toutes pointues)
QUESTIONS = [
    Q("Comment s'appelle la mascotte du PSG ?", ["Titi le moineau", "Germain le lynx", "Parisou le chat", "Léo le lion"], 1, "DIFFICILE", i1,
      [(.1, "stamp", .6)]),
    Q("Finale C1 2025 : qui ouvre le score ?", ["Désiré Doué", "Kvaratskhelia", "Vitinha", "Achraf Hakimi"], 3, "DIFFICILE", i2,
      [(.1, "crowd", .8), (.1, "stamp", .6)]),
    Q("2025 : contre qui le quart de finale de C1 ?", ["Liverpool", "Bayern Munich", "Aston Villa", "FC Barcelone"], 2, "DIFFICILE", i3,
      [(.1, "stamp", .6)]),
    Q("Le maillot historique (1973) dessiné par… ?", ["Daniel Hechter", "Pierre Cardin", "Yves Saint Laurent", "J.-P. Gaultier"], 0, "TRÈS DUR", i4,
      [(.1, "stamp", .7)]),
    Q("Coupe de France 1982, 1er trophée : contre qui ?", ["Nantes", "Saint-Étienne", "Monaco", "Bastia"], 1, "TRÈS DUR", i5,
      [(.1, "crowd_long", .7), (.1, "stamp", .6)]),
    Q("Janvier 2019, PSG-Guingamp : quel score ?", ["7-0", "8-0", "6-0", "9-0"], 3, "TRÈS DUR", i6, [(.1, "crowd", .7), (.1, "stamp", .6)]),
    Q("Quel était le surnom de Pauleta ?", ["Le Cobra", "Le Faucon de Lisbonne", "L'Aigle des Açores", "Le Requin"], 2, "EXPERT", i7,
      [(.1, "sparkle"), (.1, "crowd", .6)]),
    Q("Plus large victoire (10-0, 1994) : contre qui ?", ["Côte Chaude", "Lusitanos", "Créteil", "Le Havre"], 0, "LA PLUS DURE", i8,
      [(.0, "groan", .5), (.1, "stamp", .6)]),
]

# ------------------------------------------------------------------ scènes
intro_draw, intro_sfx = intro_scene(THEME, Wd(0, HOOK_PAD), hero)
intro_sfx = [(.0, "hook", 1.3)] + [x for x in intro_sfx if x[1] != "boom"]      # le hook remplace le boom d'ouverture
cta_draw, cta_sfx = cta_scene(THEME, Wd(1), after=CTA_AFTER)
outro_draw, outro_sfx = outro_scene(THEME, Wd(2), hero, tag="et toi, t'es à quel niveau ?")
SCENES = []
for k, key in enumerate(KEYS):
    if key == "intro": SCENES.append(Scene("intro", TEXTES["intro"], intro_draw, intro_sfx, pad_in=HOOK_PAD, pad_out=.2))
    elif key == "cta": SCENES.append(Scene("cta", TEXTES["cta"], cta_draw, cta_sfx, pad_in=PAD_IN, pad_out=.25, trans="punch", trans_dur=.3))
    elif key == "outro": SCENES.append(Scene("fin", TEXTES["outro"], outro_draw, outro_sfx, pad_in=PAD_IN, pad_out=1.2, trans="punch", trans_dur=.3))
    else:
        i = int(key[1:]); q = QUESTIONS[i - 1]; tm = TMS[k]
        SCENES.append(Scene(key, f"{TEXTES[key]}  [chrono 4 s]  {TEXTES['r' + key[1:]]}", question_scene(q, i, 8, tm, THEME, last=i == 8),
                            question_sfx(q, tm), pad_in=PAD_IN, pad_out=.45, trans="whip", trans_dur=.3))

# ------------------------------------------------------------------ couverture, planches
def cover(path): return quiz_cover(path, THEME, hero, TITLE)

def stills(out, only=None):
    scene_timing(SCENES, VOICE); starts = np.cumsum([0] + [sc.T for sc in SCENES])
    os.makedirs(out, exist_ok=True); sheets = []
    for i, sc in enumerate(SCENES):
        if only and (i + 1) not in only: continue
        tm = TMS[i]
        ts_ = ([.05, .4, tm["tq"] - .2, tm["ts"] + 1.2, tm["ts"] + 3.6, tm["te"] + .25, tm["te"] + .9, sc.T - .1] if tm else
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
