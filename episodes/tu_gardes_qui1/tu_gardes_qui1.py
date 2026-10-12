"""TU GARDES QUI ? #1 (nouveau concept « débat ») : 5 duels de légendes françaises, 5 s pour choisir A ou B, pas de bonne réponse.
Le spectateur note ses 5 lettres et les écrit en commentaire (« ABBAA ») ; la mascotte hésite pendant le chrono, danse à la fin.

  python3 episodes/tu_gardes_qui1/tu_gardes_qui1.py output/tu_gardes_qui1 --stills [1,2]
  python3 episodes/tu_gardes_qui1/tu_gardes_qui1.py output/tu_gardes_qui1 --cover
  python3 episodes/tu_gardes_qui1/tu_gardes_qui1.py output/tu_gardes_qui1
"""
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from quiz import *
import quiz
quiz.CHRONO = CHRONO = 3.0                      # 3 s pour choisir (plus nerveux que le quiz)
from mascotte import draw_sprite

TITLE = "~/duel $ ./tu_gardes_qui"
SLUG = "tu_gardes_qui1"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
TEXTES = json.load(open(os.path.join(HERE, "textes_voix.json")))
N = 5
KEYS, VOICE, TMS = assemble(os.path.join(HERE, "voix"), f"/tmp/{SLUG}_voix", n_q=N, cta_after=0)

NOIR = (30, 28, 28); BLANC = (250, 250, 246); BLEU = (32, 70, 170); ROUGEB = (206, 36, 48); NUIT = (20, 26, 48)
# (nom A, joueur A, stat A, nom B, joueur B, stat B, intitulé de la stat)
P = lambda k, hair, skin, st=None: Player(f"tg1{k}", hair=hair, skin=skin, **({"hair_style": st} if st else {}))
DUELS = [
    ("ZIDANE", P("zz", (40, 30, 24), (214, 170, 130), "bald"), "1", "PLATINI", P("pla", (110, 74, 44), (232, 190, 156), "shaggy"), "3", "BALLONS D'OR"),
    ("HENRY", P("th", (24, 20, 18), (126, 86, 62), "bald"), "51", "BENZEMA", P("kb", (30, 24, 20), (196, 150, 112)), "37", "BUTS AVEC LES BLEUS"),
    ("MBAPPÉ", P("km", (24, 20, 18), (126, 86, 62), "bald"), "12", "GRIEZMANN", P("ag", (150, 110, 60), (232, 190, 156)), "4", "BUTS EN COUPE DU MONDE"),
    ("KANTÉ", P("nk", (24, 20, 18), (110, 72, 52), "bald"), "OUI", "MAKÉLÉLÉ", P("cm", (24, 20, 18), (110, 72, 52), "bald"), "NON", "COUPE DU MONDE GAGNÉE"),
    ("LLORIS", P("hl", (60, 44, 32), (232, 192, 160)), "145", "BARTHEZ", P("fb", (40, 30, 24), (226, 186, 150), "bald"), "87", "SÉLECTIONS EN BLEU"),
]
KITS = ["france", "france", "france", "france", "gk"]
BGS = [(28, 44, 96), (96, 24, 40), (24, 70, 62), (70, 40, 100), (30, 30, 40)]

IMG_DIR = os.path.join(ROOT, "assets", "tu_gardes_qui1")
_por = {}
def portrait(i, L, h=560):
    """Buste papier IA du joueur (assets/tu_gardes_qui1/d{i}{A|B}.png), ancré en bas au centre."""
    k = (i, L, h)
    if k not in _por:
        im = Image.open(os.path.join(IMG_DIR, f"d{i}{L}.png")).convert("RGBA"); im = im.resize((int(im.width*h/im.height), h), Image.LANCZOS)
        im.info["anchor"] = (im.width/2, im.height); _por[k] = im
    return _por[k]

def draw_portrait(cv, i, L, x, y, t, t0, ts, te, side):
    """Entrée en glissade depuis son bord (dépassement + rebond), balancement, pulsation alternée pendant le chrono, secousse au buzzer."""
    u = prog(t, t0, .45)
    if u <= 0: return
    im = portrait(i, L)
    dx = side*(1 - ease_out_back(u))*700
    bob = 8*math.sin(t*3 + (0 if L == "A" else 1.7))
    beat = 0.0
    if ts <= t < te: beat = .07*max(0, math.sin((t - ts)*math.pi*2 + (0 if L == "A" else math.pi)))
    shake = 10*math.sin(t*70)*clamp(1 - prog(t, te, .35)) if t >= te else 0
    rot = side*-4 + 2*math.sin(t*2.2 + (0 if L == "A" else 1)) + (shake*.3)
    blit_sxy(cv, im, x + dx + shake, y + bob, 1 + beat, 1 + beat, rot)

def letter_badge(cv, x, y, L, col, s=1.0):
    if s <= .02: return
    d = ImageDraw.Draw(cv); r = 62*s
    d.ellipse([x - r - 6, y - r - 6, x + r + 6, y + r + 6], fill=NOIR); d.ellipse([x - r, y - r, x + r, y + r], fill=col, outline=BLANC, width=6)
    d.text((x, y + 4), L, font=font("title", int(96*s)), fill=BLANC, anchor="mm")

def slots(cv, fr, t, cur, y=1660, filled_now=False):
    """5 cases « ta lettre » : celles des duels passés cochées, la courante qui clignote."""
    d = ImageDraw.Draw(cv)
    for k in range(N):
        x = 420 + (k - 2)*120; on = k < cur - 1 or (k == cur - 1 and filled_now)
        col = GOLD if on else (BLANC if k == cur - 1 else (120, 120, 130))
        w = 46 + (6*math.sin(t*10) if k == cur - 1 and not on else 0)
        d.rounded_rectangle([x - w, y - 52, x + w, y + 52], 12, fill=col, outline=NOIR, width=5)
        d.text((x, y + 4), "?" if on else str(k + 1), font=font("title", 64), fill=NOIR, anchor="mm")

def duel_scene(i, tm):
    na, pa, sa, nb, pb, sb, lab = DUELS[i - 1]; kit = KITS[i - 1]; bg = BGS[i - 1]; last = i == N
    head = LBL("DERNIER DUEL !" if last else f"DUEL {i}/{N}", f"tg1h{i}", font("title", 64), NOIR if last else BLANC, GOLD if last else RED, padx=28, pady=6, rough=3)
    STAT = LBL(lab, f"tg1s{i}", font("title", 58), NOIR, CREAM, padx=26, pady=8, rough=3, maxw=900)
    NA = LBL(na, f"tg1na{i}", font("title", 66), BLANC, BLEU, padx=20, pady=4, rough=2.5, maxw=470)
    NB = LBL(nb, f"tg1nb{i}", font("title", 66), BLANC, ROUGEB, padx=20, pady=4, rough=2.5, maxw=470)
    VA = LBL(sa, f"tg1va{i}", font("title", 110), NOIR, GOLD, padx=22, pady=0, rough=3); VB = LBL(sb, f"tg1vb{i}", font("title", 110), NOIR, GOLD, padx=22, pady=0, rough=3)
    VS = STAMP("VS", "tg1vs", RED, 120); NOTE = STAMP("NOTE TA LETTRE !", "tg1note", RED, 70)
    def draw(cv, fr, t, T):
        stage_fill(cv, fr, bg, f"tg1bg{i}")
        d = ImageDraw.Draw(cv)                                            # écran coupé en deux : A bleu / B rouge
        a = pop_in(t, .05, .3)
        d.polygon([(0, 640), (CX + 40, 640), (CX - 40, 1480), (0, 1480)], fill=tuple(int(c*.55 + b*.45) for c, b in zip(BLEU, bg)))
        d.polygon([(CX + 40, 640), (W, 640), (W, 1480), (CX - 40, 1480)], fill=tuple(int(c*.55 + b*.45) for c, b in zip(ROUGEB, bg)))
        ts, te = tm["ts"], tm["te"]
        head.draw(cv, fr, CX, 230, pop_in(t, .02, .3), -2)
        STAT.draw(cv, fr, CX, 370, slam(t, .1, .2), 1.5)
        chrono(cv, fr, t, ts, y=530)
        for (x, Pl, NL, VL, L, col, rot, t0) in ((280, pa, NA, VA, "A", BLEU, -3, .15), (800, pb, NB, VB, "B", ROUGEB, 3, .35)):
            s = slam(t, t0, .2)
            if s <= 0: continue
            pulse = 1
            draw_portrait(cv, i, L, x, 1215, t, t0, ts, te, -1 if L == "A" else 1)
            letter_badge(cv, x + (-190 if L == "A" else 190), 740, L, col, s)
            NL.draw(cv, fr, x, 1280, s, rot)
            VL.draw(cv, fr, x, 1400, s*pulse, -rot)
        VS.draw(cv, fr, CX, 980, slam(t, .55, .2)*(1 + .08*math.sin(t*7)), -8)
        if t > te: NOTE.draw(cv, fr, CX, 1545, slam(t, te + .05, .25), -4)
        slots(cv, fr, t, i, filled_now=t > te)
        mood = "perplexe" if t < ts else ("stress" if t < te else ("reflechit" if t < te + .4 else "clin_doeil"))
        draw_sprite(cv, mood, 930, 1910, 260, t, hop_t=te)
        flashes(cv, t, te, .12, .5); punch(cv, t, te, 1.04, .25); drift(cv, t, T, .02)
    sfx = [(.0, "whoosh", .45), (.1, "stamp", .55), (.15, "pop"), (.35, "pop"), (.55, "stamp", .7)]
    sfx += chrono_sfx(tm["ts"]) + [(tm["te"] + .05, "stamp", .8), (tm["te"] + .1, "pop2")]
    return draw, sfx

# ------------------------------------------------------------------ intro / fin
KR = Label("5 DUELS · 3 SECONDES · A OU B", "tg1i5", font("title", 64), NOIR, GOLD, maxw=1000, padx=30, pady=8, rough=5)
KG = STAMP("C'EST PARTI !", "tg1go", RED, 120)
def intro_draw(cv, fr, t, T):
    stage_fill(cv, fr, NUIT, "tg1i"); rays(cv, (CX, 1300), t, .5, 16, 1500, (50, 60, 110), .12, .15)
    ransom_line(cv, "TU GARDES QUI ?", 330, 140, seed=5, fr=fr, scale=lerp(1.3, 1, ease_out_cubic(prog(t, 0, .25))))
    ransom_line(cv, "LÉGENDES DES BLEUS", 520, 96, seed=13, fr=fr)
    KR.draw(cv, fr, CX, 680, 1 if fr == 0 else slam(t, .02, .2), -3)
    letter_badge(cv, 260, 900, "A", BLEU, pop_in(t, T*.55, .3)); letter_badge(cv, 820, 900, "B", ROUGEB, pop_in(t, T*.6, .3))
    if t > T*.55: STAMP("OU", "tg1ou", RED, 90).draw(cv, fr, CX, 900, slam(t, T*.62, .2), -6)
    draw_sprite(cv, "coucou" if t < 2.2 else "malin", CX, 1890, 700, t)
    if t > T*.85: show_stamp(cv, fr, KG, t, T*.85, CX, 1140, -6)
    drift(cv, t, T, .02)
intro_sfx = [(.0, "boom", .8), (.0, "stamp", .7), (.05, "riser", .35)]

KO = KW("ÉCRIS TES 5 LETTRES !", "tg1o1", NOIR, size=88)
KC = STAMP("LES PLUS CHOQUANTES DANS LA PROCHAINE !", "tg1oc", RED, 50)
DANCE = ["celebre", "saut", "mort_de_rire", "coucou", "celebre", "saut", "clin_doeil", "fier"]
def dance(cv, t, x, y, h, bpm=128):
    b = 60/bpm; k = int(t/b)
    draw_sprite(cv, DANCE[k % len(DANCE)], x, y, h, t, hop_t=k*b, rot=7*math.sin(t*math.pi/b), flip=k % 2 == 1)
def outro_draw(cv, fr, t, T):
    stage_fill(cv, fr, NUIT, "tg1out"); rays(cv, (CX, 900), t, .6, 16, 1500, (230, 190, 80), .1, .15)
    kw(cv, fr, KO, t, .05, None, CX, 290, -3)
    for k, L in enumerate("ABBAA"):                       # l'exemple de la voix, lettre par lettre
        letter_badge(cv, CX + (k - 2)*175, 500, L, BLEU if L == "A" else ROUGEB, pop_in(t, T*.22 + k*.18, .25))
    speech_bubble(cv, fr, "tg1bub", "ABBAA, et vous ?", 380, 720, pop_in(t, T*.4, .3), (-1, 1), 58)
    if t > T*.5: show_stamp(cv, fr, KC, t, T*.5, CX, 900, -4)
    sub_button(cv, fr, CX, 1030, t, T*.8, T*.86)
    dance(cv, t, CX, 1890, 600)
    if t > T*.5: confetti(cv, fr, "tg1oc", t - T*.5, 60, 3.5, [GOLD, BLANC, RED])
    drift(cv, t, T, .02)
def outro_sfx_for(T):
    return ([(.0, "boom", .6), (.05, "stamp", .6)] + [(T*.22 + k*.18, "pop", .5) for k in range(5)] +
            [(T*.4, "notif"), (T*.5, "stamp", .8), (T*.8, "pop2"), (T*.86, "notif")] + [(k*60/128, "pop", .25) for k in range(int(T*128/60))])

DUR_OUT = load_audio(VOICE[-1]).shape[0]/SR + PAD_IN + 1.2
SCENES = []
for k, key in enumerate(KEYS):
    if key == "intro": SCENES.append(Scene("intro", TEXTES["intro"], intro_draw, intro_sfx, pad_in=PAD_IN, pad_out=.2))
    elif key == "outro": SCENES.append(Scene("fin", TEXTES["outro"], outro_draw, outro_sfx_for(DUR_OUT), pad_in=PAD_IN, pad_out=1.2, trans="punch", trans_dur=.3))
    else:
        i = int(key[1:]); d, s = duel_scene(i, TMS[k])
        SCENES.append(Scene(key, f"{TEXTES[key]}  [chrono 5 s]  {TEXTES['r' + key[1:]]}", d, s, pad_in=PAD_IN, pad_out=.5, trans="whip", trans_dur=.3))

def cover(path):
    cv = background(0, TITLE); stage_fill(cv, 0, NUIT, "tg1cov"); d = ImageDraw.Draw(cv)
    d.polygon([(0, 640), (CX + 40, 640), (CX - 40, 1500), (0, 1500)], fill=(40, 60, 120)); d.polygon([(CX + 40, 640), (W, 640), (W, 1500), (CX - 40, 1500)], fill=(120, 40, 56))
    ransom_line(cv, "TU GARDES QUI ?", 320, 140, seed=5); ransom_line(cv, "LÉGENDES DES BLEUS", 500, 96, seed=13)
    na, pa, _, nb, pb, _, _ = DUELS[0]
    for x, Pl, nm, L, col, r in ((280, pa, na, "A", BLEU, -3), (800, pb, nb, "B", ROUGEB, 3)):
        blit_sxy(cv, portrait(1, L, 600), x, 1260, 1, 1, r); letter_badge(cv, x + (-190 if L == "A" else 190), 740, L, col)
        LBL(nm, f"tg1cv{L}", font("title", 80), BLANC, col, padx=22, pady=4, rough=2.5).draw(cv, 0, x, 1330, 1, r)
    STAMP("VS", "tg1vs", RED, 140).draw(cv, 0, CX, 1000, 1, -8)
    draw_sprite(cv, "perplexe", CX, 1890, 420, 1.0)
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
        p = os.path.join(out, f"tg1_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
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
