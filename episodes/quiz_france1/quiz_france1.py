"""Quiz PSG NIVEAU 1 (facile, pour faire commenter les scores) : « T'es un vrai fan du PSG si tu as plus de 6/8 » (format quiz, voir engine/quiz.py).
8 questions QCM (4 réponses, 5 s de chrono) du plus facile au plus dur ; CTA « abonne-toi + like » après la 4e ; barème final.

  python3 episodes/quiz_psg4/quiz_psg4.py output/quiz_psg4 --stills [2,3]
  python3 episodes/quiz_psg4/quiz_psg4.py output/quiz_psg4 --cover
  python3 episodes/quiz_psg4/quiz_psg4.py output/quiz_psg4
"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from quiz import *
import engine
from PIL import ImageFilter

TITLE = "~/quiz $ ./bleus"
SLUG = "quiz_france1"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
TEXTES = json.load(open(os.path.join(HERE, "textes_voix.json")))
KEYS, VOICE, TMS = assemble(os.path.join(HERE, "voix"), f"/tmp/{SLUG}_voix")
WS, _ = load_words(os.path.join(HERE, "alignement.json"))          # intro, cta, outro
def Wd(k):
    return lambda word, n=1, end=False: PAD_IN + WS[k](word, n, end)

NAVY = (16, 40, 86); NAVY_D = (10, 24, 54); ROUGE = (210, 36, 42); BLANC = (250, 250, 246); NOIR = (30, 28, 28); MAROON = (138, 21, 56)
THEME = dict(du="DES BLEUS", accent=ROUGE, badge=NAVY, bgs=[NAVY, (112, 22, 40), NAVY_D, (36, 66, 132)], ray=(255, 255, 255), ray2=(40, 70, 140), seuil=6, mot_nq=("Huit", 1), mot_chrono=("cinq", 1), tampon="FACILE ?",
             hook=("SI T'AS PAS 6/8…", "T'ES UNE HONTE", "QUIZ ÉQUIPE DE FRANCE · NIVEAU FACILE"))

PSGP = Player("qzfra", hair=(70, 50, 36), skin=(230, 186, 150))
NEY = Player("qzney", hair=(48, 34, 26), skin=(196, 146, 108), hair_style="quiff")
MBAP = Player("qzmbap", hair=(24, 20, 18), skin=(126, 86, 62), hair_style="bald")

def hero(cv, fr, t, x, y, s, crown=False):
    PSGP.draw(cv, fr, x, y, s, age=1, kit="france", mood="cheer", arms=(150 + 8*math.sin(t*6), 150 - 8*math.sin(t*6)), legs=(10, 10), t=t)
    if crown: crown_on(cv, fr, x, y, s, t, 0)

def mystery(cv, fr, x, y, u, s=1.0):
    """Gros « ? » qui frétille avant la révélation, puis s'envole."""
    a = 1 - prog(u, 0, .4)
    if a > .01: LBL("?", "qzmq", font("title", 150), GOLD, None, stroke=8, stroke_fill=NOIR).draw(cv, fr, x, y - 60*(1 - a), s*a, 8*math.sin(fr*.3))

# ------------------------------------------------------------------ illustrations (u = 0 avant la révélation, puis 0 → 1)
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

SCOREBOARD = scoreboard_sprite(820, 300, "qzfrscore")
def board(cv, fr, la, lb, a, b, sub="", s=.8, y=ILLU_Y):
    L = layer(900, 400, (450, 200)); SCOREBOARD.draw(L, fr, 450, 200, 1, 0, 1); d = ImageDraw.Draw(L)
    for x_, lab in ((180, la), (720, lb)): d.text((x_, 120), lab, font=font("mono", 64 if len(lab) <= 5 else 48), fill=(200, 196, 190), anchor="mm")
    d.text((450, 210), f"{a} - {b}", font=font("title", 150), fill=(255, 204, 70), anchor="mm")
    if sub: d.text((450, 310), sub, font=font("mono", 36), fill=(170, 166, 160), anchor="mm")
    blit(cv, L, CX, y, s)

def star(d, x, y, r, col):
    pts = [(x + (r if k % 2 == 0 else r*.45)*math.sin(k*math.pi/5), y - (r if k % 2 == 0 else r*.45)*math.cos(k*math.pi/5)) for k in range(10)]
    d.polygon(pts, fill=col, outline=NOIR, width=4)

FRA = Player("qzfrj", hair=(60, 44, 32), skin=(226, 186, 150))
ZZ = Player("qzfrzz", hair=(40, 30, 24), skin=(214, 170, 130), hair_style="bald")
DD = Player("qzfrdd", hair=(70, 60, 50), skin=(226, 186, 150))
MATZ = Player("qzfrmat", hair=(30, 24, 20), skin=(214, 170, 130))
KM = Player("qzfrkm", hair=(24, 20, 18), skin=(126, 86, 62), hair_style="bald")

def i1(cv, fr, t, u, tm):
    FRA.draw(cv, fr, CX - 200, ILLU_Y + 165, .52, age=1, kit="france", mood="cheer" if u > .1 else "happy", arms=(150, 150) if u > .1 else (25, 25), t=t)
    d = ImageDraw.Draw(cv)
    if u <= .1: LBL("? ÉTOILES", "qzfrq1", font("title", 90), BLANC, NAVY, padx=24, pady=4, rough=2).draw(cv, fr, CX + 200, ILLU_Y - 10, 1, 4 + 2*math.sin(t*4))
    else:
        k = slam(u, .1, .3)
        for j, x in enumerate((CX + 110, CX + 290)): star(d, x, ILLU_Y - 60, 80*k*(1 + .08*math.sin(t*5 + j)), GOLD)
        TAG("1998 + 2018", "qzfrt1", PAL["paper"], NOIR, 48).draw(cv, fr, CX + 200, ILLU_Y + 90, pop_in(u, .3, .4), -3)
def i2(cv, fr, t, u, tm):
    reveal_player(cv, fr, t, u, ZZ, "france", "z2")
    name_tag(cv, fr, u, "ZIDANE", "qzfrn2", "2 têtes, finale 98 : 3-0")
def i3(cv, fr, t, u, tm):
    reveal_player(cv, fr, t, u, DD, "coach", "d3")
    name_tag(cv, fr, u, "DESCHAMPS", "qzfrn3", "champion en 98 ET en 2018", size=72)
def i4(cv, fr, t, u, tm):
    board(cv, fr, "FRA", "???" if u <= .05 else "CRO", 4, 2, "finale 2018")
    if u > .1: STAMP("CHAMPIONS !", "qzfrs4", ROUGE, 66).draw(cv, fr, CX + 200, ILLU_Y + 120, slam(u, .1, .3), -6)
def i5(cv, fr, t, u, tm):
    if u <= .1: LBL("??????", "qzfrq5", font("title", 120), BLANC, NOIR, padx=24, pady=4, rough=2).draw(cv, fr, CX, ILLU_Y - 10, 1, 4 + 2*math.sin(t*4))
    else:
        LBL("MOSCOU", "qzfrn5", font("title", 140), NOIR, GOLD, padx=30, pady=6, rough=3).draw(cv, fr, CX, ILLU_Y - 30, slam(u, .1, .3), 4)
        TAG("stade Loujniki, 15 juillet 2018", "qzfrt5", PAL["paper"], NOIR, 44).draw(cv, fr, CX, ILLU_Y + 100, pop_in(u, .3, .4), -3)
def i6(cv, fr, t, u, tm):
    reveal_player(cv, fr, t, u, MATZ, "italy", "m6")
    name_tag(cv, fr, u, "MATERAZZI", "qzfrn6", "finale 2006, Berlin", size=72)
    if u > .1: STAMP("CARTON ROUGE", "qzfrs6", ROUGE, 54).draw(cv, fr, CX + 190, ILLU_Y + 170, slam(u, .3, .3), 7)
def i7(cv, fr, t, u, tm):
    board(cv, fr, "FRA", "???" if u <= .05 else "ARG", 3, 3, "finale 2022 · 2-4 aux t.a.b.")
    if u > .1: STAMP("SI PROCHE...", "qzfrs7", ROUGE, 62).draw(cv, fr, CX + 200, ILLU_Y + 120, slam(u, .1, .3), -6)
def i8(cv, fr, t, u, tm):
    KM.draw(cv, fr, CX - 220, ILLU_Y + 165, .52, age=1, kit="france", mood="cheer" if u > .1 else "happy", arms=(150, 150) if u > .1 else (25, 25), t=t)
    if u <= .1: LBL("× ?", "qzfrq8", font("title", 150), BLANC, NAVY, padx=24, pady=0, rough=2).draw(cv, fr, CX + 220, ILLU_Y - 10, 1, 4 + 2*math.sin(t*4))
    else:
        LBL("× 3", "qzfrn8", font("title", 170), NOIR, GOLD, padx=30, pady=0, rough=3).draw(cv, fr, CX + 220, ILLU_Y - 30, slam(u, .1, .3), 4)
        TAG("triplé en finale !", "qzfrt8", PAL["paper"], NOIR, 44).draw(cv, fr, CX + 220, ILLU_Y + 120, pop_in(u, .3, .4), -3)

# ------------------------------------------------------------------ les 8 questions (faciles : le hook promet que c'est « honteux » de rater)
QUESTIONS = [
    Q("Combien d'étoiles sur le maillot des Bleus ?", ["1", "2", "3", "4"], 1, "FACILE", i1, [(.1, "sparkle"), (.1, "crowd", .6)]),
    Q("Finale 98 : qui marque 2 buts de la tête ?", ["Thierry Henry", "Zinédine Zidane", "Emmanuel Petit", "Youri Djorkaeff"], 1, "FACILE", i2, [(.1, "crowd", .7)]),
    Q("Le sélectionneur champion du monde en 2018 ?", ["Laurent Blanc", "Raymond Domenech", "Didier Deschamps", "Zinédine Zidane"], 2, "FACILE", i3, [(.1, "cash", .6)]),
    Q("La finale 2018, c'était contre qui ?", ["Croatie", "Belgique", "Argentine", "Portugal"], 0, "FACILE", i4, [(.1, "stamp", .6), (.1, "crowd_long", .7)]),
    Q("Dans quelle ville s'est jouée cette finale 2018 ?", ["Saint-Pétersbourg", "Paris", "Moscou", "Kazan"], 2, "MOYEN", i5, [(.1, "stamp", .6)]),
    Q("En 2006, Zidane met un coup de tête à qui ?", ["Fabio Cannavaro", "Gianluigi Buffon", "Francesco Totti", "Marco Materazzi"], 3, "MOYEN", i6, [(.1, "whoosh", .5), (.3, "stamp", .6)]),
    Q("Finale 2022, perdue aux tirs au but contre… ?", ["Croatie", "Argentine", "Maroc", "Brésil"], 1, "MOYEN", i7, [(.1, "stamp", .6)]),
    Q("Combien de buts Mbappé en finale 2022 ?", ["1", "2", "3", "4"], 2, "LA PLUS DURE", i8, [(.1, "crowd", .8), (.1, "stamp", .6)]),
]

# ------------------------------------------------------------------ scènes
LOGO = Image.open(os.path.join(ROOT, "assets", "logos", "fff_bleu_sticker.png")).convert("RGBA")
def logo_hero(cv, fr, t, x, y, s):
    """Couverture : gros logo FFF en autocollant papier (ombre portée, légère rotation) à la place du joueur."""
    h = int(600*s); im = LOGO.resize((int(LOGO.width*h/LOGO.height), h), Image.LANCZOS).rotate(-6, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda v: v*90//255)); sh = sh.filter(ImageFilter.GaussianBlur(10))
    x0, y0 = int(x + 120 - im.width/2), int(y - im.height)
    cv.paste(sh, (x0 + 14, y0 + 18), sh); cv.paste(im, (x0, y0), im)
def intro_logo(cv, fr, t, x, y, s):
    """Hook : le gros logo FFF tombe et rebondit (au lieu du joueur), puis respire au rythme de la Marseillaise."""
    k = 1.0 if fr == 0 else (ease_out_back(prog(t, 0, .45)) if t < .45 else 1 + .03*math.sin(t*5.5))
    logo_hero(cv, fr, t, x - 200, y + 60, 1.4*max(.05, k))
intro_draw, intro_sfx = intro_scene(THEME, Wd(0), intro_logo)
intro_sfx = intro_sfx + [(0.0, "marseillaise", .9)]                  # hymne en fond pendant le hook (≈ 8 s, se fond sous la voix)
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
def cover(path):
    """Couverture : hook en lettres découpées, GROS logo FFF autocollant au centre, bande « quiz équipe de France », tampon FACILE ?, chrono."""
    cv = background(0, TITLE); stage_fill(cv, 0, NAVY, "qzfrcov")
    rays(cv, (CX, 1150), .3, .8, 16, 1500, (40, 70, 140), .12)
    ransom_line(cv, "SI T'AS PAS 6/8…", 270, 124, seed=3); ransom_line(cv, "T'ES UNE HONTE", 430, 136, seed=11)
    logo_hero(cv, 0, 1.0, CX - 120, 1400, 1.45)
    Label("QUIZ ÉQUIPE DE FRANCE", "qzfrcv1", font("title", 76), NOIR, GOLD, padx=30, pady=8, rough=5).draw(cv, 0, CX, 1510, 1, -3)
    STAMP("FACILE ?", "qzfrcv2", ROUGE, 100).draw(cv, 0, 840, 1720, 1, 10)
    chrono(cv, 0, CHRONO*.4 + 1.0, 1.0, y=1740, cx=170, x0=290, x1=600)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path


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
        p = os.path.join(out, f"qzfr_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
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
