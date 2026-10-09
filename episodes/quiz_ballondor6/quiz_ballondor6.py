"""Quiz « Légendes du foot » : « Ballon d'or : plus de 6/8, sinon t'es pas un vrai fan ! » (format quiz, voir engine/quiz.py ;
méthode « viral » : .claude/skills/tiktok-foot-viral). Sujet d'actu : la cérémonie 2026 a lieu le 26 octobre à Londres.
VERSION 6 QUESTIONS (~1 min 05, sans pause au milieu, pour comparer la rétention avec la version 8 questions), chrono 4 s, son de hook 0,55 s, fin : « qui gagne le 26 octobre ? ».

  python3 episodes/quiz_ballondor6/quiz_ballondor6.py output/quiz_ballondor6 --stills [2,3]
  python3 episodes/quiz_ballondor6/quiz_ballondor6.py output/quiz_ballondor6 --cover
  python3 episodes/quiz_ballondor6/quiz_ballondor6.py output/quiz_ballondor6
"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import quiz
quiz.CHRONO = 4.0
from quiz import *
import engine

TITLE = "~/quiz $ ./ballon_dor"
SLUG = "quiz_ballondor6"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
CTA_AFTER = 0                      # 6 questions, pas de pause au milieu : CTA à la fin
HOOK_PAD = .55
TEXTES = json.load(open(os.path.join(HERE, "textes_voix.json")))
KEYS, VOICE, TMS = assemble(os.path.join(HERE, "voix"), f"/tmp/{SLUG}_voix", n_q=6, cta_after=CTA_AFTER)
WS, _ = load_words(os.path.join(HERE, "alignement.json"))          # intro, cta, outro
def Wd(k, pad=PAD_IN):
    return lambda word, n=1, end=False: pad + WS[k](word, n, end)

OR = (226, 172, 40); OR_D = (150, 104, 18); NOIR = (30, 28, 28); NUIT = (22, 20, 30); BLANC = (250, 250, 246); BRUN = (70, 50, 20)
THEME = dict(du="DU BALLON D'OR", accent=OR, badge=NOIR, bgs=[NUIT, BRUN, (12, 12, 18), (90, 66, 20)], ray=(255, 230, 150), ray2=(110, 84, 30),
             seuil=4, nq=6, mot_nq=("Six", 2), mot_chrono=("quatre", 2))

FANP = Player("qzbdfan", hair=(40, 30, 24), skin=(214, 168, 132))
MESSI = Player("qzbdmessi", hair=(90, 60, 36), skin=(226, 186, 150))
DEMB = Player("qzbddemb", hair=(20, 16, 14), skin=(120, 82, 60))
MATT = Player("qzbdmatt", hair=(60, 44, 30), skin=(232, 196, 166))
YACH = Player("qzbdyach", hair=(30, 26, 22), skin=(226, 190, 156))
MODR = Player("qzbdmodr", hair=(200, 170, 110), skin=(232, 196, 166))
WEAH = Player("qzbdweah", hair=(20, 16, 14), skin=(96, 64, 46), hair_style="bald")

def hero(cv, fr, t, x, y, s, crown=False):
    FANP.draw(cv, fr, x, y, s, age=1, kit="street", mood="cheer", arms=(160, 160), legs=(10, 10), t=t)
    if s >= .9: draw_ballon_or(cv, fr, x, y - 850*s + 8*math.sin(t*6), .9*s)
    if crown: crown_on(cv, fr, x, y, s, t, 0)

def mystery(cv, fr, x, y, u, s=1.0):
    a = 1 - prog(u, 0, .4)
    if a > .01: LBL("?", "qzbdmq", font("title", 150), GOLD, None, stroke=8, stroke_fill=NOIR).draw(cv, fr, x, y - 60*(1 - a), s*a, 8*math.sin(fr*.3))

_sil = {}
def sil(key, P, kit, s, **kw):
    if key not in _sil: _sil[key] = silhouette(P.render_layer(0, s, age=1, kit=kit, **kw))
    return _sil[key]

def reveal(cv, fr, t, u, P, kit, name, tag, key, ball=True):
    """Silhouette + « ? » avant le buzzer, puis le joueur en couleur, son nom et une étiquette ; Ballon d'or à côté."""
    x, y, s = CX - 190, ILLU_Y + 165, .52
    if ball: draw_ballon_or(cv, fr, CX + 230, ILLU_Y - 40 + 6*math.sin(t*3), .9)
    if u <= .1:
        blit(cv, sil(key, P, kit, s, mood="happy"), x, y, 1); mystery(cv, fr, x, ILLU_Y - 40, u, .9)
    else:
        P.draw(cv, fr, x, y, s, age=1, kit=kit, mood="cheer", arms=(150, 150), t=t)
        LBL(name, key + "n", font("title", 96 if len(name) < 9 else 76), NOIR, GOLD, padx=22, pady=4, rough=3).draw(cv, fr, CX + 210, ILLU_Y + 90, slam(u, .1, .3), 5)
        TAG(tag, key + "t", PAL["paper"], NOIR, 44).draw(cv, fr, CX + 210, ILLU_Y + 190, pop_in(u, .3, .4), -3)
        particles(cv, fr, key + "p", (CX + 230, ILLU_Y - 40), u, 18, 260, [GOLD, BLANC], 14)


CARD = Paper(rect_pts(560, 360), (236, 222, 190), "qzbdcard", rough=2.2, hatch=True)
# ------------------------------------------------------------------ illustrations (u = 0 avant la révélation, puis 0 → 1)
def i1(cv, fr, t, u, tm):
    reveal(cv, fr, t, u, MESSI, "barca", "MESSI", "8 Ballons d'or", "qzbd1")
    if u > .2:
        for k in range(8):
            a = pop_in(u, .2 + k*.05, .15)
            if a > .01: draw_ballon_or(cv, fr, CX - 350 + k*100, ILLU_Y - 230, .32*a)

def i2(cv, fr, t, u, tm): reveal(cv, fr, t, u, DEMB, "psg", "DEMBÉLÉ", "Ballon d'or 2025", "qzbd2")

def i3(cv, fr, t, u, tm):
    reveal(cv, fr, t, u, MATT, "street", "MATTHEWS", "1956, l'Anglais", "qzbd3")
    if u <= .1: LBL("1956", "qzbd3y", font("title", 90), NOIR, GOLD, padx=18, pady=0, rough=2).draw(cv, fr, CX + 230, ILLU_Y + 130, 1, 4)

def i4(cv, fr, t, u, tm): reveal(cv, fr, t, u, YACH, "gk", "YACHINE", "le seul gardien, 1963", "qzbd4")

def i5(cv, fr, t, u, tm):
    reveal(cv, fr, t, u, MODR, "real", "MODRIC", "2018 : fin du duel", "qzbd5")
    if u <= .1: LBL("MESSI  vs  RONALDO", "qzbd5v", font("title", 56), BLANC, NOIR, padx=20, pady=4, rough=2).draw(cv, fr, CX + 210, ILLU_Y + 130, 1, -3)

def i6(cv, fr, t, u, tm):
    CARD.draw(cv, fr, CX, ILLU_Y, 1, -3)
    if u <= .1:
        LBL("PLATINI", "qzbd6", font("title", 90), NOIR, None).draw(cv, fr, CX, ILLU_Y - 110, 1, -3); mystery(cv, fr, CX, ILLU_Y + 40, u)
    else:
        for k, yr in enumerate(("1983", "1984", "1985")):
            a = slam(u, .1 + k*.12, .2)
            if a > 0:
                draw_ballon_or(cv, fr, CX - 180 + k*180, ILLU_Y - 40, .7*a)
                LBL(yr, f"qzbd6{yr}", font("title", 56), NOIR, GOLD, padx=12, pady=0, rough=2).draw(cv, fr, CX - 180 + k*180, ILLU_Y + 120, a, (-4, 3, -2)[k])

def i7(cv, fr, t, u, tm): reveal(cv, fr, t, u, WEAH, "milan", "WEAH", "1995, 1er Africain", "qzbd7")

def i8(cv, fr, t, u, tm):
    CARD.draw(cv, fr, CX, ILLU_Y, 1, 3)
    if u <= .1:
        LBL("????", "qzbd8", font("title", 150), BRUN, None).draw(cv, fr, CX, ILLU_Y - 10, 1, 3); draw_ballon_or(cv, fr, CX + 300, ILLU_Y - 150, .6)
    else:
        LBL("2020", "qzbd8b", font("title", 160), NOIR, GOLD, padx=24, pady=0, rough=2).draw(cv, fr, CX, ILLU_Y - 20, slam(u, .1, .3), 3)
        STAMP("ANNULÉ", "qzbd8s", (200, 30, 44), 90).draw(cv, fr, CX + 140, ILLU_Y + 110, slam(u, .3, .2), -10)

QUESTIONS = [
    Q("Qui a le plus de Ballons d'or ?", ["Cristiano Ronaldo", "Lionel Messi", "Michel Platini", "Johan Cruyff"], 1, "FACILE", i1, [(.1, "sparkle"), (.1, "crowd", .7)]),
    Q("Dernier Français Ballon d'or (2025) ?", ["Kylian Mbappé", "Karim Benzema", "Antoine Griezmann", "Ousmane Dembélé"], 3, "FACILE", i2, [(.1, "crowd", .8), (.1, "stamp", .6)]),
    Q("Le tout 1er Ballon d'or, en 1956 ?", ["Alfredo Di Stéfano", "Raymond Kopa", "Stanley Matthews", "Ferenc Puskás"], 2, "MOYEN", i3, [(.1, "stamp", .6)]),
    Q("2018 : qui casse le duel Messi-Ronaldo ?", ["Antoine Griezmann", "Luka Modric", "Kylian Mbappé", "Raphaël Varane"], 1, "MOYEN", i5, [(.1, "crowd", .7), (.1, "stamp", .6)]),
    Q("Le 1er Ballon d'or africain ?", ["Didier Drogba", "Samuel Eto'o", "George Weah", "Roger Milla"], 2, "DIFFICILE", i7, [(.1, "crowd", .7), (.1, "stamp", .6)]),
    Q("Quelle année le Ballon d'or a été annulé ?", ["2020", "2010", "1999", "2016"], 0, "LA PLUS DURE", i8, [(.0, "groan", .5), (.1, "stamp", .8)]),
]

# ------------------------------------------------------------------ scènes
intro_draw, intro_sfx = intro_scene(THEME, Wd(0, HOOK_PAD), hero)
intro_sfx = [(.0, "hook", 1.3)] + [x for x in intro_sfx if x[1] != "boom"]      # le hook remplace le boom d'ouverture
cta_draw, cta_sfx = cta_scene(THEME, Wd(1), after=CTA_AFTER)
outro_draw, outro_sfx = outro_scene(THEME, Wd(2), hero, tag="qui gagne le 26 octobre ?")
SCENES = []
for k, key in enumerate(KEYS):
    if key == "intro": SCENES.append(Scene("intro", TEXTES["intro"], intro_draw, intro_sfx, pad_in=HOOK_PAD, pad_out=.2))
    elif key == "cta": SCENES.append(Scene("cta", TEXTES["cta"], cta_draw, cta_sfx, pad_in=PAD_IN, pad_out=.25, trans="punch", trans_dur=.3))
    elif key == "outro": SCENES.append(Scene("fin", TEXTES["outro"], outro_draw, outro_sfx, pad_in=PAD_IN, pad_out=1.2, trans="punch", trans_dur=.3))
    else:
        i = int(key[1:]); q = QUESTIONS[i - 1]; tm = TMS[k]
        SCENES.append(Scene(key, f"{TEXTES[key]}  [chrono 4 s]  {TEXTES['r' + key[1:]]}", question_scene(q, i, 6, tm, THEME, last=i == 6),
                            question_sfx(q, tm), pad_in=PAD_IN, pad_out=.45, trans="whip", trans_dur=.3))

# ------------------------------------------------------------------ couverture, planches
def cover(path):
    quiz_cover(path, THEME, hero, TITLE)
    cv = Image.open(path).convert("RGBA"); draw_ballon_or(cv, 0, 830, 1560, 1.5)      # le trophée bien visible en miniature
    cv.convert("RGB").save(path, quality=94); return path

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
