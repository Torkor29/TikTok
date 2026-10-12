"""Quiz PSG NIVEAU 1 (facile, pour faire commenter les scores) : « T'es un vrai fan du PSG si tu as plus de 6/8 » (format quiz, voir engine/quiz.py).
8 questions QCM (4 réponses, 5 s de chrono) du plus facile au plus dur ; CTA « abonne-toi + like » après la 4e ; barème final.

  python3 episodes/quiz_psg4b/quiz_psg4b.py output/quiz_psg4b --stills [2,3]
  python3 episodes/quiz_psg4b/quiz_psg4b.py output/quiz_psg4b --cover
  python3 episodes/quiz_psg4b/quiz_psg4b.py output/quiz_psg4b
"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from quiz import *
import engine
from mascotte import draw_sprite, envelope

TITLE = "~/quiz $ ./psg"
SLUG = "quiz_psg4b"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
TEXTES = json.load(open(os.path.join(HERE, "textes_voix.json")))
KEYS, VOICE, TMS = assemble(os.path.join(HERE, "voix"), f"/tmp/{SLUG}_voix")
WS, _ = load_words(os.path.join(HERE, "alignement.json"))          # intro, cta, outro
def Wd(k):
    return lambda word, n=1, end=False: PAD_IN + WS[k](word, n, end)

NAVY = (16, 40, 86); NAVY_D = (10, 24, 54); ROUGE = (210, 36, 42); BLANC = (250, 250, 246); NOIR = (30, 28, 28); MAROON = (138, 21, 56)
THEME = dict(du="DU PSG", accent=ROUGE, badge=NAVY, bgs=[NAVY, (112, 22, 40), NAVY_D, (36, 66, 132)], ray=(255, 255, 255), ray2=(40, 70, 140), niveau="NIVEAU 1 · PARTIE 2", niveau_pos=(CX, 850), niveau_size=74, niveau_rot=-4, tampon="PARTIE 2")

PSGP = Player("qzpsg", hair=(70, 50, 36), skin=(230, 186, 150))
NEY = Player("qzney", hair=(48, 34, 26), skin=(196, 146, 108), hair_style="quiff")
MBAP = Player("qzmbap", hair=(24, 20, 18), skin=(126, 86, 62), hair_style="bald")

_cur = {"env": None}                      # enveloppe de la voix de la scène en cours (bouche synchronisée)
def talk(t):
    e = _cur["env"]; return e(t - PAD_IN) if e else 0.0
def hero(cv, fr, t, x, y, s, crown=False):
    """Mascotte Ballon à la place du joueur (pieds en (x, y))."""
    h = 640*s
    name = ("celebre" if t < 1.6 else "fier") if crown else ("coucou" if t < 2.5 else ("malin" if talk(t) > .08 else "neutre"))
    draw_sprite(cv, name, x, y, h, t, hop_t=0 if crown else None)
    if crown: CROWN.draw(cv, fr, x, y - h - 30*s - 260*s*(1 - ease_out_back(prog(t, 0, .35))), 1.2*s, -8)

def mystery(cv, fr, x, y, u, s=1.0):
    """Gros « ? » qui frétille avant la révélation, puis s'envole."""
    a = 1 - prog(u, 0, .4)
    if a > .01: LBL("?", "qzmq", font("title", 150), GOLD, None, stroke=8, stroke_fill=NOIR).draw(cv, fr, x, y - 60*(1 - a), s*a, 8*math.sin(fr*.3))

# ------------------------------------------------------------------ illustrations (u = 0 avant la révélation, puis 0 → 1)
CIEL = (40, 160, 220)
def _shield(key, col, col2, txt, size=52, band=False):
    def dec(d, a):
        ax, ay = a
        if band: d.rectangle([ax-30, ay-130, ax+30, ay+140], fill=BLANC); d.rectangle([ax-20, ay-130, ax+20, ay+140], fill=ROUGE)
        else: d.polygon([(ax-110, ay-130), (ax, ay-130), (ax, ay+140), (ax-60, ay+100), (ax-110, ay+10)], fill=col2)
        if txt: d.text((ax, ay-10), txt, font=font("title", size), fill=BLANC, anchor="mm", stroke_width=5, stroke_fill=NOIR)
    return Paper(poly_pts([(-110, -130), (110, -130), (110, 10), (60, 100), (0, 140), (-60, 100), (-110, 10)]), col, key, rough=1.6, hatch=True).add(dec)
SH_PSG = _shield("qz4shpsg", NAVY, NAVY, "PSG", 70, band=True)
SH_OM = _shield("qz4shom", (235, 240, 246), CIEL, "OM", 90)
SH_ASM = _shield("qz4shasm", ROUGE, BLANC, "ASM", 76)
SH_Q = _shield("qz4shq", (90, 90, 100), (120, 120, 130), "?", 120)

MESSI = Player("qz4messi", hair=(70, 46, 30), skin=(222, 178, 140))
NASSER = Player("qz4nas", hair=(30, 26, 24), skin=(190, 146, 110))
MBAP = Player("qz4mbap", hair=(24, 20, 18), skin=(126, 86, 62), hair_style="bald")
ZLAT = Player("qz4zlat", hair=(40, 30, 24), skin=(226, 186, 150))
GIGIO = Player("qz4gk", hair=(30, 24, 20), skin=(226, 186, 150))
DINHO = Player("qz4dinho", hair=(26, 20, 18), skin=(150, 100, 70), hair_style="shaggy")
MARQ = Player("qz4marq", hair=(30, 24, 20), skin=(196, 150, 112))
_sil = {}
def reveal_player(cv, fr, t, u, P, kit, key, x=CX - 190, y=ILLU_Y + 165, s=.52):
    """Silhouette noire + « ? » avant la révélation, puis le joueur en couleurs qui exulte."""
    if u <= .1:
        if key not in _sil: _sil[key] = silhouette(P.render_layer(0, s, age=1, kit=kit, mood="happy"))
        blit(cv, _sil[key], x, y, 1); mystery(cv, fr, x, ILLU_Y - 40, u, .9)
    else: P.draw(cv, fr, x, y, s, age=1, kit=kit, mood="cheer", arms=(150, 150), t=t)

def name_tag(cv, fr, u, txt, key, sub=None, x=CX + 190, size=80):
    if u <= .1: return
    LBL(txt, key, font("title", size), NOIR, GOLD, padx=22, pady=6, rough=3, maxw=520).draw(cv, fr, x, ILLU_Y - 40, slam(u, .1, .3), 5)
    if sub: TAG(sub, key + "s", PAL["paper"], NOIR, 44).draw(cv, fr, x, ILLU_Y + 90, pop_in(u, .3, .4), -3)

def i1(cv, fr, t, u, tm):
    reveal_player(cv, fr, t, u, MESSI, "psg", "m1")
    if u <= .1: LBL("20??", "qz4y1", font("title", 120), BLANC, NOIR, padx=20, pady=2, rough=2).draw(cv, fr, CX + 200, ILLU_Y, 1, 6)
    else: name_tag(cv, fr, u, "2023", "qz4n1", "2 saisons à Paris", size=120)
SCOREBOARD = scoreboard_sprite(820, 300, "qz4score")
def board(cv, fr, la, lb, a, b, sub="", s=.8, y=ILLU_Y):
    L = layer(900, 400, (450, 200)); SCOREBOARD.draw(L, fr, 450, 200, 1, 0, 1); d = ImageDraw.Draw(L)
    for x_, lab in ((180, la), (720, lb)): d.text((x_, 120), lab, font=font("mono", 64 if len(lab) <= 5 else 48), fill=(200, 196, 190), anchor="mm")
    d.text((450, 210), f"{a} - {b}", font=font("title", 150), fill=(255, 204, 70), anchor="mm")
    if sub: d.text((450, 310), sub, font=font("mono", 36), fill=(170, 166, 160), anchor="mm")
    blit(cv, L, CX, y, s)
def i2(cv, fr, t, u, tm):
    board(cv, fr, "PSG", "???" if u <= .05 else "DORTMUND", 0, 2, "demi-finale 2024 (aller + retour)")
    if u > .1: STAMP("ÉLIMINÉS", "qz4s2", ROUGE, 66).draw(cv, fr, CX + 200, ILLU_Y + 120, slam(u, .1, .3), -6)
GALT = Player("qz4galt", hair=(120, 116, 110), skin=(230, 190, 156))
def i3(cv, fr, t, u, tm):
    reveal_player(cv, fr, t, u, GALT, "coach", "g3")
    name_tag(cv, fr, u, "GALTIER", "qz4n3", "PSG 2022-2023")
def i4(cv, fr, t, u, tm):
    board(cv, fr, "PSG", "???" if u <= .05 else "BAYERN", 0, 1, "finale 2020, Lisbonne")
    if u > .1: STAMP("1re FINALE", "qz4s4", ROUGE, 66).draw(cv, fr, CX + 200, ILLU_Y + 120, slam(u, .1, .3), -6)
def i5(cv, fr, t, u, tm):
    ZLAT.draw(cv, fr, CX - 200, ILLU_Y + 165, .52, age=1, kit="psg", mood="cheer" if u > .1 else "happy", arms=(150, 150) if u > .1 else (25, 25), t=t)
    if u <= .1: LBL("??? BUTS", "qz4q5", font("title", 100), BLANC, NAVY, padx=24, pady=4, rough=2).draw(cv, fr, CX + 190, ILLU_Y - 10, 1, 4 + 2*math.sin(t*4))
    else:
        LBL("156 BUTS", "qz4n5", font("title", 110), NOIR, GOLD, padx=24, pady=4, rough=3).draw(cv, fr, CX + 190, ILLU_Y - 30, slam(u, .1, .3), 4)
        TAG("Zlatan, 2012-2016", "qz4t5", PAL["paper"], NOIR, 44).draw(cv, fr, CX + 190, ILLU_Y + 90, pop_in(u, .3, .4), -3)
def i6(cv, fr, t, u, tm):
    reveal_player(cv, fr, t, u, GIGIO, "gk", "g6")
    name_tag(cv, fr, u, "DONNARUMMA", "qz4n6", "finale 2025 : 5-0", size=70)
    if u > .1: UCL.draw(cv, fr, CX + 380, ILLU_Y + 60, .4*slam(u, .2, .3), 8)
TSIL = Player("qz4ts", hair=(30, 24, 20), skin=(176, 124, 92))
SH_MIL = _shield("qz4mil", ROUGE, NOIR, "MILAN", 60)
def i7(cv, fr, t, u, tm):
    TSIL.draw(cv, fr, CX - 200, ILLU_Y + 165, .52, age=1, kit="psg", mood="happy", t=t)
    (SH_MIL if u > .1 else SH_Q).draw(cv, fr, CX + 200, ILLU_Y - 10, .85*(slam(u, .1, .3) if u > .1 else 1), 5)
    if u > .3: TAG("Thiago Silva, 2012", "qz4t7", PAL["paper"], NOIR, 44).draw(cv, fr, CX + 200, ILLU_Y + 140, pop_in(u, .3, .4), -3)
def i8(cv, fr, t, u, tm):
    MESSI.draw(cv, fr, CX - 240, ILLU_Y + 165, .52, age=1, kit="psg", mood="cheer" if u > .1 else "happy", arms=(150, 150) if u > .1 else (25, 25), t=t)
    draw_ballon_or(cv, fr, CX + 20, ILLU_Y - 20, .55)
    if u <= .1: LBL("× ?", "qz4q8", font("title", 150), BLANC, NAVY, padx=24, pady=0, rough=2).draw(cv, fr, CX + 250, ILLU_Y - 10, 1, 4 + 2*math.sin(t*4))
    else:
        LBL("× 6", "qz4n8", font("title", 170), NOIR, GOLD, padx=30, pady=0, rough=3).draw(cv, fr, CX + 250, ILLU_Y - 30, slam(u, .1, .3), 4)
        TAG("le 7e en 2021, à Paris", "qz4t8", PAL["paper"], NOIR, 44).draw(cv, fr, CX + 200, ILLU_Y + 120, pop_in(u, .3, .4), -3)

# ------------------------------------------------------------------ les 8 questions (facile -> plus dur, mais tout reste jouable)
QUESTIONS = [
    Q("En quelle année Messi a quitté le PSG ?", ["2022", "2023", "2024", "2021"], 1, "FACILE", i1, [(.1, "crowd", .6)]),
    Q("Demi-finale de C1 2024 : qui élimine le PSG ?", ["Borussia Dortmund", "Real Madrid", "Manchester City", "Bayern Munich"], 0, "FACILE", i2, [(.1, "whoosh", .4)]),
    Q("Qui entraînait le PSG juste avant Luis Enrique ?", ["Mauricio Pochettino", "Christophe Galtier", "Thomas Tuchel", "Unai Emery"], 1, "FACILE", i3, [(.1, "cash", .8)]),
    Q("Première finale de C1 du PSG en 2020 : perdue contre… ?", ["Liverpool", "Real Madrid", "Chelsea", "Bayern Munich"], 3, "MOYEN", i4, [(.1, "stamp", .6)]),
    Q("Combien de buts Zlatan a marqués avec le PSG ?", ["113", "156", "200", "256"], 1, "MOYEN", i5, [(.0, "glitch", .6), (.1, "stamp", .6)]),
    Q("Le gardien du PSG en finale de C1 2025 ?", ["Keylor Navas", "Matvey Safonov", "Gianluigi Donnarumma", "Alphonse Areola"], 2, "MOYEN", i6, [(.1, "crowd_long", .7), (.1, "sparkle")]),
    Q("En 2012, de quel club le PSG a recruté Thiago Silva ?", ["Juventus", "Inter Milan", "Fluminense", "AC Milan"], 3, "DIFFICILE", i7, [(.1, "stamp", .6), (.4, "pop2")]),
    Q("Combien de Ballons d'or avait Messi en arrivant au PSG ?", ["4", "5", "6", "7"], 2, "LA PLUS DURE", i8, [(.1, "crowd", .8), (.1, "stamp", .6)]),
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

# ------------------------------------------------------------------ mascotte : bouche sur la voix + réactions dans les questions
ENVS = [envelope(v) for v in VOICE]
def with_mascot(k, draw, tm):
    def d(cv, fr, t, T):
        _cur["env"] = ENVS[k]; draw(cv, fr, t, T)
        if tm:                                                   # question : petit Ballon en bas à droite
            ts, te = tm["ts"], tm["te"]
            mood = "stress" if ts <= t < te else ("choc" if te <= t < te + .5 else ("celebre" if t >= te + .5 else "reflechit"))
            draw_sprite(cv, mood, 880, 1900, 340, t, hop_t=te)
        elif SCENES[k].name == "cta":
            draw_sprite(cv, "pointe" if t < 2.0 else "clin_doeil", CX, 1880, 560, t, hop_t=0)
    return d
for k, sc in enumerate(SCENES): sc.draw_fn = with_mascot(k, sc.draw_fn, TMS[k])

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
        p = os.path.join(out, f"qz4b_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
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
