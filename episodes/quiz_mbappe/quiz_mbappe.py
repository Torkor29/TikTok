"""QUIZ « T'ES UN VRAI FAN DE MBAPPÉ ? » — 8 questions, chrono 4 s (format du quiz PSG à 164K), sujet jamais traité en quiz.
Test (15/10) : écran d'ouverture NOUVEAU (fond jaune, gros portrait papier, pas le fond bleu à rayons habituel), voix dès 0 s.
Voix : voix/brut.mp3 coupée (transcription ElevenLabs) en intro, q1..q8, r1..r8, outro.

  python3 episodes/quiz_mbappe/quiz_mbappe.py output/quiz_mbappe --stills [1,2]
  python3 episodes/quiz_mbappe/quiz_mbappe.py output/quiz_mbappe
"""
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from quiz import *
import quiz
quiz.CHRONO = CHRONO = 4.0
import engine
from story import align_episode
from PIL import ImageFilter

TITLE = "~/quiz $ ./mbappe"
SLUG = "quiz_mbappe"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
TEXTES = json.load(open(os.path.join(HERE, "textes_voix.json")))
KEYS, VOICE, TMS = assemble(os.path.join(HERE, "voix"), f"/tmp/{SLUG}_voix", n_q=8, cta_after=0)
TEXTE_OUTRO = TEXTES["outro"]
ALIGN = os.path.join(HERE, "alignement.json")
if not os.path.exists(ALIGN): align_episode([os.path.join(HERE, "voix", "outro.mp3")], [TEXTE_OUTRO], ALIGN)
WS, _ = load_words(ALIGN)
def Wd(k):
    """Pas de « abonne-toi » dans la voix de fin : le bouton arrive juste après « commentaire »."""
    def f(word, n=1, end=False):
        if word == "abonne-toi": return PAD_IN + WS[k]("commentaire", 1, True) + .2
        return PAD_IN + WS[k](word, n, end)
    return f

NOIR = (28, 26, 30); BLANC = (250, 250, 246); ROUGE = (210, 36, 42); JAUNE = (255, 200, 40); NUIT = (20, 22, 30)
THEME = dict(du="DE MBAPPÉ", accent=ROUGE, badge=NOIR, bgs=[NUIT, (34, 30, 40), (24, 34, 74), (40, 26, 30)], ray=(255, 255, 255), ray2=(60, 60, 76),
             seuil=6, nq=8, mot_nq=("Huit", 1), mot_chrono=("quatre", 1), tampon="QUIZ MBAPPÉ")
A = lambda *p: os.path.join(ROOT, "assets", *p)

_c = {}
def put(path, cv, x, y, h, s=1.0, rot=0.0):
    if s <= .02: return
    k = (path, h)
    if k not in _c:
        im = Image.open(path).convert("RGBA"); im = im.resize((int(im.width*h/im.height), h), Image.LANCZOS); im.info["anchor"] = (im.width/2, im.height/2)
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda v: v*110//255)); sh = sh.filter(ImageFilter.GaussianBlur(10))
        sh.info["anchor"] = im.info["anchor"]; _c[k] = (im, sh)
    im, sh = _c[k]; blit_sxy(cv, sh, x + 14*s, y + 18*s, s, s, rot); blit_sxy(cv, im, x, y, s, s, rot)
logo = lambda n: A("logos", f"{n}_sticker.png")
KM = A("tu_gardes_qui1", "d3A.png"); TH = A("tu_gardes_qui1", "d2A.png")

def mystery(cv, fr, t, u):
    if u <= .1: LBL("?", "qmbq", font("title", 220), JAUNE, None, stroke=10, stroke_fill=NOIR).draw(cv, fr, CX, ILLU_Y - 20, 1 + .05*math.sin(t*6), 8*math.sin(t*3))
def big_reveal(cv, fr, u, txt, key, sub=None, size=150, y=ILLU_Y - 40):
    if u <= .1: return
    LBL(txt, key, font("title", size), NOIR, JAUNE, padx=30, pady=6, rough=3, maxw=900).draw(cv, fr, CX, y, slam(u, .1, .3), 4)
    if sub: TAG(sub, key + "s", PAL["paper"], NOIR, 46, maxw=820).draw(cv, fr, CX, y + 130, pop_in(u, .3, .4), -3)

def i1(cv, fr, t, u, tm):
    mystery(cv, fr, t, u); big_reveal(cv, fr, u, "AS BONDY", "qmb1", "Seine-Saint-Denis (93)")
def i2(cv, fr, t, u, tm):
    put(logo("monaco"), cv, CX - 260, ILLU_Y - 10, 260, 1, -8)
    if u <= .1: mystery(cv, fr, t, u)
    else: put(TH, cv, CX + 120, ILLU_Y + 10, 380, slam(u, .1, .3), 4); big_reveal(cv, fr, u, "HENRY", "qmb2", None, 90, ILLU_Y + 190)
def i3(cv, fr, t, u, tm):
    put(logo("psg"), cv, CX + 300, ILLU_Y - 60, 200, 1, 8); mystery(cv, fr, t, u)
    big_reveal(cv, fr, u, "180 M€", "qmb3", "2e transfert le plus cher de l'histoire")
def i4(cv, fr, t, u, tm):
    put(logo("fff_bleu"), cv, CX + 320, ILLU_Y - 70, 200, 1, 8); mystery(cv, fr, t, u)
    big_reveal(cv, fr, u, "PÉROU", "qmb4", "France 1-0 Pérou, Mondial 2018")
def i5(cv, fr, t, u, tm):
    if u <= .1: mystery(cv, fr, t, u)
    else: put(KM, cv, CX - 200, ILLU_Y + 20, 400, slam(u, .1, .3), -4); LBL("19 ANS", "qmb5", font("title", 140), NOIR, JAUNE, padx=26, pady=6, rough=3).draw(cv, fr, CX + 230, ILLU_Y - 20, slam(u, .15, .3), 6)
def i6(cv, fr, t, u, tm):
    mystery(cv, fr, t, u); big_reveal(cv, fr, u, "3 - 3", "qmb6", "Argentine-France, triplé de Mbappé", 170)
def i7(cv, fr, t, u, tm):
    put(logo("psg"), cv, CX - 330, ILLU_Y - 70, 200, 1, -8); mystery(cv, fr, t, u)
    big_reveal(cv, fr, u, "256 BUTS", "qmb7", "meilleur buteur de l'histoire du PSG")
def i8(cv, fr, t, u, tm):
    put(logo("real"), cv, CX - 300, ILLU_Y - 30, 300, 1, -8); mystery(cv, fr, t, u)
    if u > .1: LBL("9", "qmb8", font("title", 300), BLANC, NOIR, padx=40, pady=0, rough=3).draw(cv, fr, CX + 180, ILLU_Y - 20, slam(u, .1, .3), 5)

QUESTIONS = [
    Q("Dans quel club Mbappé a commencé le foot ?", ["Clairefontaine", "AS Bondy", "PSG", "AS Monaco"], 1, "FACILE", i1, [(.1, "stamp", .6)]),
    Q("1er but avec Monaco : plus jeune buteur du club, devant… ?", ["David Trezeguet", "Ludovic Giuly", "Thierry Henry", "Radamel Falcao"], 2, "MOYEN", i2, [(.1, "crowd", .6)]),
    Q("Combien le PSG a payé Monaco pour Mbappé ?", ["180 M€", "145 M€", "222 M€", "120 M€"], 0, "MOYEN", i3, [(.1, "cash", .7)]),
    Q("1er but de Mbappé en Coupe du monde : contre… ?", ["Australie", "Danemark", "Argentine", "Pérou"], 3, "DIFFICILE", i4, [(.1, "crowd", .6)]),
    Q("À quel âge Mbappé devient champion du monde ?", ["18 ans", "19 ans", "20 ans", "21 ans"], 1, "MOYEN", i5, [(.1, "crowd", .8)]),
    Q("Score de la finale 2022, avant les tirs au but ?", ["2-2", "3-2", "3-3", "4-2"], 2, "MOYEN", i6, [(.1, "stamp", .6)]),
    Q("Combien de buts Mbappé a marqués avec le PSG ?", ["256", "196", "228", "312"], 0, "DIFFICILE", i7, [(.1, "crowd", .7)]),
    Q("Son numéro lors de sa 1re saison au Real ?", ["7", "9", "10", "11"], 1, "LA PLUS DURE", i8, [(.1, "stamp", .7)]),
]

def hero(cv, fr, t, x, y, s, crown=False):
    put(KM, cv, x, y - 330*s, int(640*s), 1 + .02*math.sin(t*5), -3)

# --- NOUVEL écran d'ouverture (voix dès 0 s) : fond jaune vif, très gros portrait papier, défi en lettres découpées
STRIP = Label("SI T'AS PAS 6/8… T'ES PAS UN VRAI FAN", "qmbst", font("title", 54), BLANC, NOIR, maxw=1040, padx=28, pady=8, rough=4)
def intro_draw(cv, fr, t, T):
    stage_fill(cv, fr, JAUNE, "qmbin"); rays(cv, (CX, 1200), t, .9, 18, 1700, (255, 222, 110), .1, .35)
    ransom_line(cv, "T'ES UN VRAI FAN", 260, 118, seed=5, fr=fr)
    LBL("DE MBAPPÉ ?", "qmbt2", font("title", 150), BLANC, NOIR, padx=30, pady=4, rough=3).draw(cv, fr, CX, 440, 1, -3)
    put(KM, cv, CX, 1080, 860, 1 + .03*t, -2 + 1.5*math.sin(t*3))
    STRIP.draw(cv, fr, CX, 1600, slam(t, 2.0, .2) if fr else 1, 2)
    LBL("8 QUESTIONS · 4 SECONDES", "qmbt3", font("title", 60), NOIR, BLANC, padx=24, pady=6, rough=3).draw(cv, fr, CX, 1760, slam(t, 1.3, .2) if fr else 1, -2)
    drift(cv, t, T, .015)
intro_sfx = [(0.0, "boom", .8), (0.0, "crowd", .6), (1.3, "stamp", .6), (2.0, "stamp", .7)]

outro_draw, outro_sfx = outro_scene(THEME, Wd(0), hero, tag="le quiz d'un autre joueur ?")
SCENES = []
for k, key in enumerate(KEYS):
    if key == "intro": SCENES.append(Scene("intro", TEXTES["intro"], intro_draw, intro_sfx, pad_in=0, pad_out=.25))
    elif key == "outro": SCENES.append(Scene("fin", TEXTE_OUTRO, outro_draw, outro_sfx, pad_in=PAD_IN, pad_out=1.4, trans="punch", trans_dur=.3))
    else:
        i = int(key[1:]); q = QUESTIONS[i - 1]; tm = TMS[k]
        SCENES.append(Scene(key, f"{TEXTES['q%d' % i]}  [chrono]  {TEXTES['r%d' % i]}", question_scene(q, i, 8, tm, THEME, last=i == 8),
                            question_sfx(q, tm), pad_in=PAD_IN, pad_out=.45, trans="whip", trans_dur=.3))

def cover(path):
    """Couverture dans la zone visible 3:4 (y 260..1660)."""
    cv = background(0, TITLE); stage_fill(cv, 0, JAUNE, "qmbcv"); rays(cv, (CX, 1000), 0, .9, 18, 1700, (255, 222, 110), .1)
    ransom_line(cv, "T'ES UN VRAI FAN", 340, 112, seed=5)
    LBL("DE MBAPPÉ ?", "qmbcv2", font("title", 140), BLANC, NOIR, padx=30, pady=4, rough=3).draw(cv, 0, CX, 500, 1, -3)
    put(KM, cv, CX, 1050, 720, 1, -2)
    LBL("SI T'AS PAS 6/8…", "qmbcv3", font("title", 70), BLANC, ROUGE, padx=26, pady=6, rough=3).draw(cv, 0, CX, 1530, 1, 3)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

def stills(out, only=None):
    scene_timing(SCENES, VOICE); starts = np.cumsum([0] + [sc.T for sc in SCENES]); os.makedirs(out, exist_ok=True); sheets = []
    for i, sc in enumerate(SCENES):
        if only and (i + 1) not in only: continue
        tm = TMS[i]
        ts_ = [.05, .6, tm["tq"] - .2, tm["ts"] + 2, tm["te"] + .25, tm["te"] + .9, sc.T - .1] if tm else [f*sc.T for f in (.01, .3, .6, .95)]
        ims = []
        for t in ts_:
            f = int((starts[i] + t)*FPS); cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T); finish(cv, TITLE); ims.append(cv.resize((240, 427)))
        sheet = Image.new("RGB", (240*len(ims), 460), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims): sheet.paste(im, (k*240, 33)); dd.text((k*240 + 6, 4), f"S{i+1} {ts_[k]:.1f}", font=font("mono", 22), fill=(230, 230, 230))
        p = os.path.join(out, f"s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", SLUG)
    os.makedirs(out, exist_ok=True)
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(f"/tmp/{SLUG}_stills", only)); sys.exit()
    cover(os.path.join(out, f"{SLUG}_couverture.jpg"))
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25, limit=True))
