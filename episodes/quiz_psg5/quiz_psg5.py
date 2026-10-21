"""Quiz PSG FACILE, nouvelle DA (figurines papercraft 3D + vrais écussons) : « T'es un vrai fan du PSG si tu as plus de 6/8 » (format quiz, voir engine/quiz.py).
8 questions QCM (4 réponses, 5 s de chrono) du plus facile au plus dur ; CTA « abonne-toi + like » après la 4e ; barème final.

  python3 episodes/quiz_psg5/quiz_psg5.py output/quiz_psg5 --stills [2,3]
  python3 episodes/quiz_psg5/quiz_psg5.py output/quiz_psg5 --cover
  python3 episodes/quiz_psg5/quiz_psg5.py output/quiz_psg5
"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from quiz import *
import engine

TITLE = "~/quiz $ ./psg"
SLUG = "quiz_psg5"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
TEXTES = json.load(open(os.path.join(HERE, "textes_voix.json")))
KEYS, VOICE, TMS = assemble(os.path.join(HERE, "voix"), f"/tmp/{SLUG}_voix")
WS, _ = load_words(os.path.join(HERE, "alignement.json"))          # intro, cta, outro
def Wd(k):
    return lambda word, n=1, end=False: PAD_IN + WS[k](word, n, end)

NAVY = (16, 40, 86); NAVY_D = (10, 24, 54); ROUGE = (210, 36, 42); BLANC = (250, 250, 246); NOIR = (30, 28, 28); MAROON = (138, 21, 56)
THEME = dict(du="DU PSG", accent=ROUGE, badge=NAVY, bgs=[NAVY, (112, 22, 40), NAVY_D, (36, 66, 132)], ray=(255, 255, 255), ray2=(40, 70, 140), niveau="NIVEAU FACILE", niveau_pos=(CX, 850), niveau_size=74, niveau_rot=-4, tampon="FACILE")

import pc_lib as PC
from gfx_stickers import sticker
PC.KITS["myst"] = dict(c1=(70, 72, 84), sleeve=(70, 72, 84), shorts=(50, 52, 60), socks=(70, 72, 84), trim=(110, 112, 124), kind="plain")
HERO = PC.PCPlayer("q5hero", hair=(60, 42, 30), skin=(226, 184, 150), yaw=-.25)
def hero(cv, fr, t, x, y, s, crown=False):
    HERO.draw(cv, fr, x, y, s, kit="psg", mood="happy", arms=(150 + 8*math.sin(t*6), 150 - 8*math.sin(t*6)), legs=(8, -8), t=t)
    if crown: crown_on(cv, fr, x, y + 175*s, s, t, 0)

def mystery(cv, fr, x, y, u, s=1.0):
    """Gros « ? » qui frétille avant la révélation, puis s'envole."""
    a = 1 - prog(u, 0, .4)
    if a > .01: LBL("?", "qzmq", font("title", 150), GOLD, None, stroke=8, stroke_fill=NOIR).draw(cv, fr, x, y - 60*(1 - a), s*a, 8*math.sin(fr*.3))

# ------------------------------------------------------------------ illustrations papercraft 3D + vrais écussons (u = 0 avant la révélation)
_sc = {}
def logo(n, h):
    k = (n, h)
    if k not in _sc: _sc[k] = sticker(n, h)
    return _sc[k]
def dark(sp, col=(18, 18, 26)):
    """Silhouette pleine (cache la réponse)."""
    k = ("dk", id(sp))
    if k not in _sc:
        a = sp.getchannel("A"); im = Image.new("RGBA", sp.size, col + (255,)); im.putalpha(a); im.info["anchor"] = sp.info["anchor"]; _sc[k] = im
    return _sc[k]
def figure(P, t, kit, mood="happy", arms=(25, 25), u=1.0):
    return P.sprite(kit=kit, arms=arms, mood=mood, t=t)
def put_fig(cv, sp, x, y, h=500, a=1.0):
    k = h/(sp.height*4.3/5.6); blit_sxy(cv, sp, x, y, k, k, 0, a)

def name_tag(cv, fr, u, txt, key, sub=None, x=CX + 190, size=80):
    if u <= .1: return
    LBL(txt, key, font("title", size), NOIR, GOLD, padx=22, pady=6, rough=3, maxw=520).draw(cv, fr, x, ILLU_Y - 40, slam(u, .1, .3), 5)
    if sub: TAG(sub, key + "s", PAL["paper"], NOIR, 44).draw(cv, fr, x, ILLU_Y + 90, pop_in(u, .3, .4), -3)

FY = ILLU_Y + 200                                                   # pieds des figurines
def i1(cv, fr, t, u, tm):
    put_fig(cv, figure(HERO, t, "psg" if u > .1 else "myst", "happy" if u <= .1 else "happy", (150, 150) if u > .1 else (20, 20)), CX - 190, FY)
    if u <= .1: mystery(cv, fr, CX - 190, ILLU_Y - 150, u, .8); LBL("? + ?", "q5c1", font("title", 110), BLANC, NOIR, padx=20, pady=2, rough=2).draw(cv, fr, CX + 200, ILLU_Y, 1, 5)
    else: name_tag(cv, fr, u, "BLEU & ROUGE", "q5n1", "depuis 1970", size=70)
def i2(cv, fr, t, u, tm):
    lg = logo("psg", 300)
    if u <= .1: blit(cv, dark(lg), CX, ILLU_Y, 1, 3*math.sin(t*2)); mystery(cv, fr, CX, ILLU_Y - 10, u, 1.0)
    else:
        blit(cv, lg, CX - 180, ILLU_Y, slam(u, .05, .3), 0)
        name_tag(cv, fr, u, "TOUR EIFFEL", "q5n2", "au centre du logo", x=CX + 200, size=70)
def i3(cv, fr, t, u, tm):
    blit(cv, logo("psg", 240), CX - 230, ILLU_Y, 1, -4)
    LBL("VS", "q5vs", font("title", 110), BLANC, ROUGE, padx=20, pady=0, rough=2).draw(cv, fr, CX, ILLU_Y, 1 + .06*math.sin(t*6), 0)
    om = logo("om", 240)
    if u <= .1: blit(cv, dark(om), CX + 230, ILLU_Y, 1, 4); mystery(cv, fr, CX + 230, ILLU_Y, u, .9)
    else:
        blit(cv, om, CX + 230, ILLU_Y, slam(u, .05, .3), 4)
        STAMP("LE CLASSIQUE", "q5s3", ROUGE, 60).draw(cv, fr, CX, ILLU_Y + 150, slam(u, .2, .3), -5)
PRES = PC.PCPlayer("q5pres", hair=(30, 26, 24), skin=(190, 146, 110), yaw=-.2)
def i4(cv, fr, t, u, tm):
    sp = figure(PRES, t, "suit", "happy", (20, 20) if u <= .1 else (60, 120))
    put_fig(cv, dark(sp) if u <= .1 else sp, CX - 200, FY)
    if u <= .1: mystery(cv, fr, CX - 200, ILLU_Y - 150, u, .8); blit(cv, logo("psg", 200), CX + 200, ILLU_Y, 1, 3*math.sin(t*2))
    else: name_tag(cv, fr, u, "AL-KHELAÏFI", "q5n4", "président depuis 2011", size=70)
MBAP = PC.PCPlayer("q5mbap", hair=(24, 20, 18), skin=(126, 86, 62), hair_style="bald", yaw=-.2)
def i5(cv, fr, t, u, tm):
    put_fig(cv, figure(MBAP, t, "psg", "happy", (150, 150) if u > .1 else (25, 25)), CX - 200, FY)
    if u <= .1: LBL("? → PSG", "q5q5", font("title", 96), BLANC, NOIR, padx=20, pady=2, rough=2).draw(cv, fr, CX + 200, ILLU_Y, 1, 4)
    else:
        blit(cv, logo("monaco", 230), CX + 200, ILLU_Y - 30, slam(u, .05, .3), 4)
        TAG("Mbappé, 2017", "q5t5", PAL["paper"], NOIR, 44).draw(cv, fr, CX + 200, ILLU_Y + 130, pop_in(u, .3, .4), -3)
ZLAT = PC.PCPlayer("q5zlat", hair=(40, 30, 24), skin=(226, 186, 150), hair_style="long", yaw=-.2)
def _shield(key, col, col2, txt, size=52):
    def dec(d, a):
        ax, ay = a
        for k in range(-2, 3): d.rectangle([ax + k*44 - 11, ay - 130, ax + k*44 + 11, ay + 140], fill=col2)
        if txt: d.text((ax, ay - 10), txt, font=font("title", size), fill=BLANC, anchor="mm", stroke_width=5, stroke_fill=NOIR)
    return Paper(poly_pts([(-110, -130), (110, -130), (110, 10), (60, 100), (0, 140), (-60, 100), (-110, 10)]), col, key, rough=1.6, hatch=True).add(dec)
SH_MIL = _shield("q5mil", ROUGE, NOIR, "MILAN", 60)
def i6(cv, fr, t, u, tm):
    put_fig(cv, figure(ZLAT, t, "psg", "happy", (150, 150) if u > .1 else (25, 25)), CX - 200, FY)
    if u <= .1: LBL("2012", "q5y6", font("title", 110), BLANC, NOIR, padx=20, pady=2, rough=2).draw(cv, fr, CX + 200, ILLU_Y - 60, 1, 4); mystery(cv, fr, CX + 200, ILLU_Y + 60, u, .8)
    else:
        SH_MIL.draw(cv, fr, CX + 200, ILLU_Y - 10, .85*slam(u, .1, .3), 5)
        TAG("AC Milan → PSG", "q5t6", PAL["paper"], NOIR, 44).draw(cv, fr, CX + 200, ILLU_Y + 150, pop_in(u, .3, .4), -3)
DEMB = PC.PCPlayer("q5demb", hair=(22, 18, 16), skin=(110, 72, 50), yaw=-.2)
def i7(cv, fr, t, u, tm):
    sp = figure(DEMB, t, "psg", "happy", (150, 150) if u > .1 else (25, 25))
    put_fig(cv, dark(sp) if u <= .1 else sp, CX - 220, FY)
    draw_ballon_or(cv, fr, CX + 30, ILLU_Y - 20, .5)
    if u <= .1: mystery(cv, fr, CX - 220, ILLU_Y - 150, u, .8); LBL("2025", "q5y7", font("title", 100), BLANC, NOIR, padx=20, pady=2, rough=2).draw(cv, fr, CX + 270, ILLU_Y, 1, 4)
    else: name_tag(cv, fr, u, "DEMBÉLÉ", "q5n7", "Ballon d'or 2025", x=CX + 250, size=80)
BECK = PC.PCPlayer("q5beck", hair=(214, 180, 110), skin=(230, 190, 156), yaw=-.2)
def i8(cv, fr, t, u, tm):
    put_fig(cv, figure(BECK, t, "psg", "happy", (150, 150) if u > .1 else (25, 25)), CX - 200, FY)
    if u <= .1: LBL("20??", "q5y8", font("title", 130), BLANC, NOIR, padx=20, pady=2, rough=2).draw(cv, fr, CX + 200, ILLU_Y, 1, 6)
    else: name_tag(cv, fr, u, "2013", "q5n8", "sa dernière saison", size=130)

# ------------------------------------------------------------------ les 8 questions (facile -> plus dur ; réponses B C D A B D C A)
QUESTIONS = [
    Q("Quelles sont les couleurs du PSG ?", ["Rouge et noir", "Bleu et rouge", "Bleu et blanc", "Jaune et bleu"], 1, "FACILE", i1, [(.1, "crowd", .6)]),
    Q("Quel monument est sur le logo du PSG ?", ["Arc de triomphe", "Notre-Dame", "Tour Eiffel", "Sacré-Cœur"], 2, "FACILE", i2, [(.1, "sparkle", .6)]),
    Q("Le grand rival historique du PSG ?", ["Lyon", "Lille", "Monaco", "Marseille"], 3, "FACILE", i3, [(.1, "stamp", .6)]),
    Q("Qui est le président du PSG ?", ["Nasser Al-Khelaïfi", "Luis Campos", "Jean-Michel Aulas", "Florentino Pérez"], 0, "FACILE", i4, [(.1, "cash", .7)]),
    Q("De quel club Mbappé est arrivé au PSG ?", ["Lyon", "Monaco", "Real Madrid", "Lille"], 1, "MOYEN", i5, [(.1, "stamp", .6)]),
    Q("Zlatan arrive au PSG en 2012. Depuis… ?", ["Barcelone", "Inter Milan", "Juventus", "AC Milan"], 3, "MOYEN", i6, [(.1, "stamp", .6), (.4, "pop2")]),
    Q("Quel joueur du PSG a gagné le Ballon d'or 2025 ?", ["Vitinha", "Achraf Hakimi", "Ousmane Dembélé", "Désiré Doué"], 2, "DIFFICILE", i7, [(.1, "crowd_long", .7), (.1, "sparkle")]),
    Q("En quelle année Beckham a joué au PSG ?", ["2013", "2011", "2009", "2015"], 0, "LA PLUS DURE", i8, [(.1, "crowd", .8), (.1, "stamp", .6)]),
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
        p = os.path.join(out, f"qz5_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
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
