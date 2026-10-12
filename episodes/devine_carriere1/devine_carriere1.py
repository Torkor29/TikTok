"""DEVINE LA CARRIÈRE #1 (nouveau concept) : les clubs d'un joueur tombent un par un pendant 5 s de chrono, puis révélation.
5 joueurs du plus facile au plus dur ; la mascotte papier réagit en bas à droite. Moteur : engine/quiz.py (voix, chrono).

  python3 episodes/devine_carriere1/devine_carriere1.py output/devine_carriere1 --stills [1,2]
  python3 episodes/devine_carriere1/devine_carriere1.py output/devine_carriere1 --cover
  python3 episodes/devine_carriere1/devine_carriere1.py output/devine_carriere1
"""
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from quiz import *
import engine
from mascotte import draw_sprite

TITLE = "~/devine $ ./carriere"
SLUG = "devine_carriere1"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
TEXTES = json.load(open(os.path.join(HERE, "textes_voix.json")))
N = 5
KEYS, VOICE, TMS = assemble(os.path.join(HERE, "voix"), f"/tmp/{SLUG}_voix", n_q=N, cta_after=0)

VERT = (22, 92, 70); VERT_D = (12, 56, 44); NOIR = (30, 28, 28); BLANC = (250, 250, 246)
BGS = [(22, 92, 70), (28, 58, 120), (112, 30, 52), (40, 40, 52), (150, 70, 20)]

# (club, année d'arrivée, fond, texte)
RM = ((250, 250, 246), NOIR); ATM = ((206, 32, 44), BLANC); BAR = ((140, 30, 70), (250, 200, 40)); MIL = ((190, 20, 30), NOIR)
CAREERS = [
    ("KARIM BENZEMA", "real", [("Lyon", 2004, (30, 60, 150), BLANC), ("Real Madrid", 2009, *RM), ("Al-Ittihad", 2023, (240, 200, 30), NOIR)]),
    ("ANTOINE GRIEZMANN", "france", [("Real Sociedad", 2009, (30, 80, 170), BLANC), ("Atlético", 2014, *ATM), ("Barcelone", 2019, *BAR),
                                     ("Atlético", 2021, *ATM)]),
    ("ZLATAN IBRAHIMOVIC", "psg", [("Malmö", 1999, (120, 180, 230), NOIR), ("Ajax", 2001, (210, 30, 40), BLANC), ("Juventus", 2004, NOIR, BLANC),
                                   ("Inter", 2006, (20, 50, 140), BLANC), ("Barcelone", 2009, *BAR), ("Milan", 2010, *MIL),
                                   ("PSG", 2012, (16, 40, 86), BLANC), ("Man United", 2016, (200, 20, 30), BLANC),
                                   ("LA Galaxy", 2018, (20, 40, 90), (250, 200, 40)), ("Milan", 2020, *MIL)]),
    ("OLIVIER GIROUD", "france", [("Grenoble", 2005, (40, 90, 170), BLANC), ("Tours", 2010, (30, 30, 30), BLANC), ("Montpellier", 2010, (240, 120, 30), (20, 40, 90)),
                                  ("Arsenal", 2012, (220, 20, 30), BLANC), ("Chelsea", 2018, (20, 60, 160), BLANC), ("Milan", 2021, *MIL),
                                  ("Los Angeles FC", 2024, NOIR, (220, 180, 90)), ("Lille", 2025, (200, 20, 40), BLANC)]),
    ("N'GOLO KANTÉ", "france", [("Boulogne", 2012, (40, 40, 40), (250, 250, 246)), ("Caen", 2013, (20, 50, 140), (210, 30, 40)),
                                ("Leicester", 2015, (20, 60, 160), BLANC), ("Chelsea", 2016, (20, 60, 160), BLANC), ("Al-Ittihad", 2023, (240, 200, 30), NOIR)]),
]
LEVELS = ["FACILE", "FACILE", "MOYEN", "DIFFICILE", "LA PLUS DURE"]
PLAYERS = [Player("dc1p1", hair=(30, 24, 20), skin=(196, 150, 112)),
           Player("dc1p2", hair=(150, 110, 60), skin=(232, 190, 156)),
           Player("dc1p3", hair=(40, 30, 24), skin=(226, 186, 150)),
           Player("dc1p4", hair=(90, 70, 50), skin=(232, 192, 160)),
           Player("dc1p5", hair=(24, 20, 18), skin=(110, 72, 52), hair_style="bald")]

_sil = {}
def mascot(cv, t, name, hop_t=None, h=330, x=900, y=1905): draw_sprite(cv, name, x, y, h, t, hop_t=hop_t)

def chips(cv, fr, t, i, car, t0, t1):
    """Les clubs tombent un par un (année + club), reliés par une flèche."""
    n = len(car); dy = min(108, 900/n); y0 = 820; sz = 58 if n <= 6 else 50
    d = ImageDraw.Draw(cv)
    for k, (club, yr, bg, fg) in enumerate(car):
        tk = t0 + k*(t1 - t0)/max(1, n - 1); s = slam(t, tk, .18)
        if s <= 0: continue
        y = y0 + k*dy
        if k: d.line([(150, y - dy + 30), (150, y - 30)], fill=BLANC, width=6)
        LBL(str(yr), f"dc1y{i}{k}", font("mono", 40), NOIR, GOLD, padx=12, pady=2, rough=2).draw(cv, fr, 150, y, s, -3)
        LBL(club.upper(), f"dc1c{i}{k}", font("title", sz), fg, bg, padx=22, pady=4, rough=2.5, maxw=520).draw(cv, fr, 450, y, s, (-2, 1.5, -1, 2)[k % 4])

def player_scene(i, tm):
    name, kit, car = CAREERS[i - 1]; P = PLAYERS[i - 1]; bg = BGS[i - 1]
    card = LBL("QUI A FAIT CETTE CARRIÈRE ?", "dc1card", font("title", 60), NOIR, CREAM, maxw=880, padx=34, pady=16, rough=3)
    last = i == N
    head = LBL("LE DERNIER !" if last else f"JOUEUR {i}/{N}", f"dc1h{i}", font("title", 62), NOIR if last else BLANC, GOLD if last else RED, padx=28, pady=6, rough=3)
    NAME = LBL(name, f"dc1n{i}", font("title", 70), NOIR, GOLD, padx=24, pady=8, rough=3, maxw=620)
    def draw(cv, fr, t, T):
        stage_fill(cv, fr, bg, f"dc1bg{i}"); rays(cv, (CX, 900), t, .35, 14, 1500, tuple(min(255, c + 40) for c in bg), .1, .08)
        ts, te = tm["ts"], tm["te"]; u = prog(t, te, .45) if t >= te else 0
        head.draw(cv, fr, CX, 248, pop_in(t, .02, .3), -2)
        TAG(LEVELS[i - 1], f"dc1l{i}", RED if i >= 4 else GOLD, BLANC if i >= 4 else NOIR, 44).draw(cv, fr, 900, 200, pop_in(t, .3, .3), 9)
        card.draw(cv, fr, CX, CARD_Y - 40, slam(t, .08, .2), -1.2)
        chrono(cv, fr, t, ts, y=TIMER_Y - 30)
        chips(cv, fr, t, i, car, .35, ts + CHRONO*.55)
        px, py, s = 860, 1470, .42
        if u <= .1:
            if i not in _sil: _sil[i] = silhouette(P.render_layer(0, s, age=1, kit=kit, mood="happy"))
            blit(cv, _sil[i], px, py, 1)
            LBL("?", "dc1q", font("title", 150), GOLD, None, stroke=8, stroke_fill=NOIR).draw(cv, fr, px, py - 330, 1, 8*math.sin(fr*.3))
        else:
            P.draw(cv, fr, px, py, s, age=1, kit=kit, mood="cheer", arms=(150, 150), t=t)
            NAME.draw(cv, fr, 400, 1800, slam(u, .1, .3), -3)
        mood = "reflechit" if t < ts else ("stress" if t < te else ("choc" if t < te + .5 else "celebre"))
        mascot(cv, t, mood, hop_t=te)
        flashes(cv, t, te, .12, .5); punch(cv, t, te, 1.04, .25); drift(cv, t, T, .02)
    sfx = [(.0, "whoosh", .45), (.1, "stamp", .55)]
    sfx += [(.35 + k*(tm["ts"] + CHRONO*.55 - .35)/max(1, len(car) - 1), "pop", .5) for k in range(len(car))]
    sfx += chrono_sfx(tm["ts"]) + [(tm["te"] + .05, "correct", .8), (tm["te"] + .1, "crowd", .6)]
    return draw, sfx

# ------------------------------------------------------------------ intro / fin (sans alignement : repères en fraction de la voix)
K5 = Label("5 JOUEURS · 5 SECONDES", "dc1i5", font("title", 74), NOIR, GOLD, maxw=1000, padx=30, pady=8, rough=5)
KG = STAMP("C'EST PARTI !", "dc1go", RED, 120)
DEMO = [("2004", "LYON"), ("2009", "REAL MADRID"), ("2023", "???")]
def intro_draw(cv, fr, t, T):
    stage_fill(cv, fr, VERT, "dc1i"); rays(cv, (CX, 1300), t, .5, 16, 1500, (40, 130, 100), .12, .15)
    ransom_line(cv, "DEVINE LE JOUEUR", 320, 118, seed=3, fr=fr, scale=lerp(1.25, 1, ease_out_cubic(prog(t, 0, .25))))
    ransom_line(cv, "AVEC SA CARRIÈRE", 480, 118, seed=11, fr=fr)
    K5.draw(cv, fr, CX, 660, 1 if fr == 0 else slam(t, .02, .2), -3)
    for k, (yr, cl) in enumerate(DEMO):
        s = slam(t, 1.0 + k*.45, .18)
        if s > 0:
            LBL(yr, f"dc1dy{k}", font("mono", 40), NOIR, GOLD, padx=12, pady=2, rough=2).draw(cv, fr, 190, 860 + k*110, s, -3)
            LBL(cl, f"dc1dc{k}", font("title", 58), BLANC, NOIR, padx=22, pady=4, rough=2.5).draw(cv, fr, 480, 860 + k*110, s, (-2, 1.5, -1)[k])
    mascot(cv, t, "coucou" if t < 2.5 else "malin", h=640, x=800, y=1880)
    tg = T*.82
    if t > tg: show_stamp(cv, fr, KG, t, tg, CX, 1250, -6)
    drift(cv, t, T, .02)
intro_sfx = [(.0, "boom", .8), (.0, "stamp", .7), (.05, "riser", .35), (1.0, "pop"), (1.45, "pop"), (1.9, "pop2")]

KA = KW("T'EN AS TROUVÉ COMBIEN ?", "dc1o1", NOIR, size=78)
ROWS = [("0 – 1", "TOURISTE", DIM), ("2 – 3", "CONNAISSEUR", BLANC), ("4 – 5", "VRAI FAN", GOLD)]
LR = [Label(f"{a}   {b}", f"dc1o2{k}", font("title", 70), NOIR, c, padx=30, pady=6, rough=3) for k, (a, b, c) in enumerate(ROWS)]
def outro_draw(cv, fr, t, T):
    stage_fill(cv, fr, VERT_D, "dc1out"); rays(cv, (CX, 900), t, .6, 16, 1500, (230, 190, 80), .1, .15)
    kw(cv, fr, KA, t, .05, None, CX, 300, -3)
    for k, lab in enumerate(LR):
        a = pop_in(t, .5 + k*.2, .3)
        if a > 0: lab.draw(cv, fr, CX, 500 + k*125, a, (-2, 2, -3)[k])
    speech_bubble(cv, fr, "dc1bub", "J'en ai trouvé ?/5 !", 620, 940, pop_in(t, 1.6, .3), (-1, 1), 58)
    sub_button(cv, fr, CX, 1140, t, 2.6, 3.0)
    mascot(cv, t, "celebre" if t < 1.5 else "fier", hop_t=0, h=600, x=300, y=1880)
    confetti(cv, fr, "dc1oc", t, 70, 3.5, [GOLD, BLANC, RED])
    drift(cv, t, T, .02)
outro_sfx = [(.0, "boom", .6), (.05, "stamp", .6), (.5, "pop"), (.7, "pop"), (.9, "pop2"), (1.6, "notif"), (2.6, "pop2"), (3.0, "notif")]

SCENES = []
for k, key in enumerate(KEYS):
    if key == "intro": SCENES.append(Scene("intro", TEXTES["intro"], intro_draw, intro_sfx, pad_in=PAD_IN, pad_out=.2))
    elif key == "outro": SCENES.append(Scene("fin", TEXTES["outro"], outro_draw, outro_sfx, pad_in=PAD_IN, pad_out=1.2, trans="punch", trans_dur=.3))
    else:
        i = int(key[1:]); d, s = player_scene(i, TMS[k])
        SCENES.append(Scene(key, f"{TEXTES['p' + key[1:]]}  [chrono 5 s]  {TEXTES['r' + key[1:]]}", d, s, pad_in=PAD_IN, pad_out=.8, trans="whip", trans_dur=.3))

def cover(path):
    cv = background(0, TITLE); stage_fill(cv, 0, VERT, "dc1cov"); rays(cv, (CX, 1250), .3, .8, 16, 1500, (40, 130, 100), .12)
    ransom_line(cv, "DEVINE LE JOUEUR", 300, 124, seed=3); ransom_line(cv, "AVEC SA CARRIÈRE", 460, 124, seed=11)
    STAMP("NIVEAU 1", "dc1cv2", RED, 90).draw(cv, 0, 830, 640, 1, 10)
    car = CAREERS[2][2][:6]
    for k, (cl, yr, bg, fg) in enumerate(car):
        y = 780 + k*100
        LBL(str(yr), f"dc1cy{k}", font("mono", 40), NOIR, GOLD, padx=12, pady=2, rough=2).draw(cv, 0, 150, y, 1, -3)
        LBL(cl.upper(), f"dc1cc{k}", font("title", 56), fg, bg, padx=22, pady=4, rough=2.5).draw(cv, 0, 430, y, 1, (-2, 1.5, -1, 2)[k % 4])
    LBL("?", "dc1cq", font("title", 260), GOLD, None, stroke=10, stroke_fill=NOIR).draw(cv, 0, 820, 1000, 1, 10)
    draw_sprite(cv, "reflechit", 820, 1880, 640, 1.0)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

def stills(out, only=None):
    scene_timing(SCENES, VOICE); starts = np.cumsum([0] + [sc.T for sc in SCENES])
    os.makedirs(out, exist_ok=True); sheets = []
    for i, sc in enumerate(SCENES):
        if only and (i + 1) not in only: continue
        tm = TMS[i]
        ts_ = ([.05, .6, tm["ts"] - .1, tm["ts"] + 1.5, tm["ts"] + 3.5, tm["te"] + .25, tm["te"] + .9, sc.T - .1] if tm else
               [f*sc.T for f in (.02, .15, .3, .45, .6, .75, .9, .99)])
        ims = []
        for t in ts_:
            f = int((starts[i] + t)*FPS); cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T); finish(cv, TITLE); ims.append(cv.resize((300, 533)))
        sheet = Image.new("RGB", (300*len(ims), 575), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            sheet.paste(im, (k*300, 42)); dd.text((k*300 + 8, 6), f"S{i+1} {ts_[k]:.1f}/{sc.T:.1f}", font=font("mono", 24), fill=(230, 230, 230))
        p = os.path.join(out, f"dc1_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
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
