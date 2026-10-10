"""« OM ou PSG ? Le onze de légende : un choix par poste, c'est toi qui votes ! » — format DUELS / DÉBAT (skill tiktok-foot-viral).
11 duels (un par poste) : bulle photo OM à gauche, PSG à droite, « VS », puis ~2 s de vote (barre qui se vide, « ? » qui pulse).
Un mini-terrain en bas se remplit poste après poste (on construit le onze). Fin : terrain avec 11 « ? », « ton onze en commentaire ».

Photos : photos/<slug>.jpg (carré, centré sur le visage), crédits facultatifs dans photos/credits.json.

  python3 episodes/om_psg_xi/om_psg_xi.py output/om_psg_xi --stills [2,3]
  python3 episodes/om_psg_xi/om_psg_xi.py output/om_psg_xi --cover
  python3 episodes/om_psg_xi/om_psg_xi.py output/om_psg_xi [--provisoire]
"""
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "psg_top8"))
from story import *
import engine
import psg_top8 as top8                       # bulles photo (bubble_sprite) et fond à rayures

TITLE = "~/duel $ ./om_psg"
SLUG = "om_psg_xi"
VOICE = [os.path.join(HERE, "voix", f"scene_{i}.mp3") for i in range(1, 14)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
PADS = [.55] + [.12]*12
VOTE = 1.9                                    # secondes de vote après chaque duel
WS, TEXTS = load_words(os.path.join(HERE, "alignement.json"))
def w(i, word, n=1, end=False):
    return PADS[i-1] + WS[i-1](word, n, end)

CIEL = (47, 174, 224); CIEL_D = (14, 92, 150); NAVY = (16, 40, 86); NAVY_D = (10, 24, 54); ROUGE = (210, 36, 42)
BLANC = (250, 250, 246); NOIR = (30, 28, 28); GOLD = (250, 196, 30); INK = PAL["ink"]; PELOUSE = (46, 120, 70)

# poste, (x, y) sur le mini-terrain (0-1), slug OM, nom OM, slug PSG, nom PSG
DUELS = [
    ("GARDIEN", (.5, .92), "barthez", "BARTHEZ", "lama", "LAMA"),
    ("LATÉRAL DROIT", (.85, .70), "angloma", "ANGLOMA", "hakimi", "HAKIMI"),
    ("DÉFENSE CENTRALE", (.62, .74), "boli", "BOLI", "thiago", "THIAGO SILVA"),
    ("DÉFENSE CENTRALE", (.38, .74), "desailly", "DESAILLY", "marquinhos", "MARQUINHOS"),
    ("LATÉRAL GAUCHE", (.15, .70), "dimeco", "DI MECO", "nunomendes", "NUNO MENDES"),
    ("SENTINELLE", (.5, .56), "deschamps", "DESCHAMPS", "verratti", "VERRATTI"),
    ("MILIEU", (.28, .44), "abedipele", "ABEDI PELÉ", "rai", "RAÍ"),
    ("NUMÉRO 10", (.72, .44), "waddle", "WADDLE", "ronaldinho", "RONALDINHO"),
    ("AILIER", (.82, .22), "payet", "PAYET", "neymar", "NEYMAR"),
    ("AVANT-CENTRE", (.5, .14), "papin", "PAPIN", "zlatan", "ZLATAN"),
    ("ATTAQUANT", (.18, .22), "drogba", "DROGBA", "mbappe", "MBAPPÉ"),
]
NOMS = {d[2]: d[3] for d in DUELS} | {d[4]: d[5] for d in DUELS}
SLUGS = [d[2] for d in DUELS] + [d[4] for d in DUELS]
top8.HERE = HERE                              # les bulles lisent nos photos
_CRED = os.path.join(HERE, "photos", "credits.json")
CREDITS = json.load(open(_CRED)) if os.path.exists(_CRED) else {}

def bubble(cv, slug, x, y, r, s=1.0, rot=0.0, ring=ROUGE):
    if s > .02: blit(cv, top8.bubble_sprite(slug, r, ring), x, y, s, rot)

def split_bg(cv, fr, key, t):
    """Moitié OM (ciel / blanc) à gauche, moitié PSG (bleu nuit / rouge) à droite, séparées par une diagonale."""
    stage_fill(cv, fr, NAVY, key); d = ImageDraw.Draw(cv); off = 30*math.sin(t*1.5)
    d.polygon([(0, 0), (600 + off, 0), (480 - off, 1920), (0, 1920)], fill=CIEL_D)
    for k in range(-2, 8):
        x = k*170 + (t*40) % 170; d.polygon([(x, 0), (x + 50, 0), (x - 280, 1920), (x - 330, 1920)], fill=(30, 110, 170))
    d.polygon([(600 + off, 0), (1080, 0), (1080, 1920), (480 - off, 1920)], fill=NAVY)
    d.polygon([(760 + off*.6, 0), (860 + off*.6, 0), (740 - off*.6, 1920), (640 - off*.6, 1920)], fill=ROUGE)
    d.line([(600 + off, 0), (480 - off, 1920)], fill=BLANC, width=10)

def mini_pitch(cv, x0, y0, wd, ht, filled, cur=None, t=0.0, qmarks=False):
    """Mini-terrain : un rond par poste ; les postes déjà votés sont pleins, le poste en cours pulse."""
    d = ImageDraw.Draw(cv)
    d.rounded_rectangle([x0, y0, x0 + wd, y0 + ht], 18, fill=PELOUSE, outline=BLANC, width=5)
    d.line([(x0, y0 + ht/2), (x0 + wd, y0 + ht/2)], fill=BLANC, width=3); d.ellipse([x0 + wd/2 - 40, y0 + ht/2 - 40, x0 + wd/2 + 40, y0 + ht/2 + 40], outline=BLANC, width=3)
    d.rectangle([x0 + wd*.3, y0 + ht - ht*.16, x0 + wd*.7, y0 + ht], outline=BLANC, width=3); d.rectangle([x0 + wd*.3, y0, x0 + wd*.7, y0 + ht*.16], outline=BLANC, width=3)
    for k, du in enumerate(DUELS):
        px, py = x0 + du[1][0]*wd, y0 + du[1][1]*ht; r = 22
        if k == cur: r = 22 + 6*abs(math.sin(t*6)); d.ellipse([px - r - 8, py - r - 8, px + r + 8, py + r + 8], fill=GOLD)
        col = BLANC if k < filled else ((70, 150, 96) if k != cur else NOIR)
        d.ellipse([px - r, py - r, px + r, py + r], fill=col, outline=NOIR, width=3)
        if qmarks: d.text((px, py + 2), "?", font=font("title", 34), fill=NOIR, anchor="mm")

# ------------------------------------------------------------------ SCÈNE 1 — hook
K1b = Label("LE ONZE DE LÉGENDE", "ok1b", font("title", 84), INK, GOLD, padx=30, pady=8, rough=5)
K1c = STAMP("C'EST TOI QUI VOTES !", "ok1c", ROUGE, 96)
def s1(cv, fr, t, T):
    split_bg(cv, fr, "os1", t)
    ransom_line(cv, "OM ou PSG ?", 380, 190, seed=9, fr=fr, scale=slam(t, -.12, .22))
    K1b.draw(cv, fr, CX, 600, 1 if fr == 0 else slam(t, .02, .2), -3)
    for k, (sl, x) in enumerate((("barthez", 260), ("papin", 260), ("zlatan", 820), ("mbappe", 820))):
        bubble(cv, sl, x, (900, 1150)[k % 2], 115, pop_in(t, .1 + .08*k, .25), 4*math.sin(t*3 + k), CIEL if x < CX else ROUGE)
    LBL("VS", "ovs1", font("title", 150), GOLD, NOIR, padx=24, pady=0, rough=3).draw(cv, fr, CX, 1025, slam(t, .45, .2), -6)
    mini_pitch(cv, 300, 1300, 480, 300, 0, None, t)
    show_stamp(cv, fr, K1c, t, w(1, "toi") - .05, CX, 1690, -4)
    impact(cv, t, .45, 20); flashes(cv, t, .45, .12, .5); impact(cv, t, w(1, "toi"), 14); drift(cv, t, T, .04)

# ------------------------------------------------------------------ SCÈNES 2 à 12 — un duel par poste
POSTE = {k: KW(d[0], f"oposte{k}", BLANC, NOIR, 100 if len(d[0]) < 14 else 84) for k, d in enumerate(DUELS)}
def duel_scene(k):
    poste, _, so, no, sp, np_ = DUELS[k]; i = k + 2
    def draw(cv, fr, t, T):
        split_bg(cv, fr, f"od{i}", t)
        kw(cv, fr, POSTE[k], t, .02, None, CX, 300, -3)
        to, tp = PADS[i-1] + .35, w(i, "ou") - .05
        bubble(cv, so, 290, 820 + 8*math.sin(t*2.6), 180, slam(t, to, .22), -5 + 3*math.sin(t*1.8), CIEL)
        bubble(cv, sp, 790, 820 + 8*math.sin(t*2.6 + 1), 180, slam(t, tp + .15, .22), 5 + 3*math.sin(t*1.8 + 1), ROUGE)
        LBL(no, f"ono{k}", font("title", 64 if len(no) < 10 else 52), BLANC, CIEL_D, padx=18, pady=4, rough=3).draw(cv, fr, 290, 1050, pop_in(t, to + .1, .25), -3)
        LBL(np_, f"onp{k}", font("title", 64 if len(np_) < 10 else 50), BLANC, ROUGE, padx=18, pady=4, rough=3).draw(cv, fr, 790, 1050, pop_in(t, tp + .25, .25), 3)
        LBL("OM", "otagom", font("title", 52), CIEL_D, BLANC, padx=14, pady=0, rough=2).draw(cv, fr, 290, 610, pop_in(t, to + .05, .2), -6)
        LBL("PSG", "otagpsg", font("title", 52), NAVY, BLANC, padx=14, pady=0, rough=2).draw(cv, fr, 790, 610, pop_in(t, tp + .2, .2), 6)
        LBL("VS", "ovs", font("title", 120), GOLD, NOIR, padx=20, pady=0, rough=3).draw(cv, fr, CX, 830, slam(t, tp, .2), -6)
        tv = T - VOTE                         # temps de vote : barre qui se vide + « ? » + « commente ! »
        if t > tv:
            u = prog(t, tv, VOTE - .1); d = ImageDraw.Draw(cv)
            d.rounded_rectangle([240, 1235, 840, 1270], 20, fill=NOIR); d.rounded_rectangle([244, 1239, 244 + 592*(1 - u), 1266], 18, fill=GOLD)
            LBL("TON CHOIX ?", "ochoix", font("title", 70), NOIR, GOLD, padx=20, pady=2, rough=3).draw(cv, fr, CX, 1165, pop_in(t, tv, .2)*(1 + .05*math.sin(t*10)), -2)
        mini_pitch(cv, 330, 1320, 420, 240, k, k, t)
        impact(cv, t, to, 10); impact(cv, t, tp + .15, 12); drift(cv, t, T, .04)
    sfx = [(.0, "whoosh", .5), (.02, "stamp", .5), (PADS[i-1] + .35, "pop", .6), (w(i, "ou") + .1, "pop2", .6), (w(i, "ou") - .05, "boom", .45)]
    return draw, sfx

# ------------------------------------------------------------------ SCÈNE 13 — ton onze en commentaire
K13a = KW("TON ONZE ?", "ok13a", BLANC, NOIR, 140); K13b = STAMP("LE DÉBAT EST OUVERT !", "ok13b", ROUGE, 90)
def s13(cv, fr, t, T):
    split_bg(cv, fr, "os13", t)
    kw(cv, fr, K13a, t, .05, None, CX, 300, -3)
    mini_pitch(cv, 190, 460, 700, 560, 0, None, t, qmarks=True)
    tc = w(13, "commentaire") - .15
    sb = pop_in(t, tc, .3)
    if sb > .01:
        speech_bubble(cv, fr, "obub13", "Barthez, Hakimi, Boli…", 500, 1180, sb, (1, 1), 58)
        d = ImageDraw.Draw(cv); arrow(d, (760, 1210), (985, 1300), prog(t, tc + .1, .4), GOLD, 14, 3, 44, .25)
    LBL("OM", "o13om", font("title", 80), CIEL_D, BLANC, padx=16, pady=0, rough=2).draw(cv, fr, 330, 1380, pop_in(t, w(13, "Marseillais") - .1, .25), -5)
    LBL("PSG", "o13psg", font("title", 80), NAVY, BLANC, padx=16, pady=0, rough=2).draw(cv, fr, 750, 1380, pop_in(t, w(13, "Parisiens") - .1, .25), 5)
    show_stamp(cv, fr, K13b, t, w(13, "débat") - .1, CX, 1520, -4)
    if CREDITS and t > T - 2.6:            # crédits photos (licences libres) en fin de vidéo
        auteurs = {}
        for c in CREDITS.values(): a, l = c.rsplit(", ", 1); auteurs.setdefault(a, set()).add(l)
        txt = "Photos Wikimedia Commons : " + " · ".join(f"{a} ({', '.join(sorted(l))})" for a, l in auteurs.items())
        Label(txt, "ocred", font("sans", 22), BLANC, NOIR, maxw=1000, padx=12, pady=6, rough=0).draw(cv, fr, CX, 1780, 1, 0)
    impact(cv, t, w(13, "débat"), 12); drift(cv, t, T, .03)

# ------------------------------------------------------------------ scènes
def SC(name, n, fn, sfx, trans=None, trans_dur=.25, pad_out=.2):
    return Scene(name, TEXTS[n-1], fn, sfx, pad_in=PADS[n-1], pad_out=pad_out, trans=trans, trans_dur=trans_dur)
SCENES = [SC("hook", 1, s1, [(.0, "hook", 1.3)] + [(.1 + .08*k, "pop", .4) for k in range(4)] + [(.45, "stamp", .6), (w(1, "toi"), "stamp", .9)])]
for k in range(len(DUELS)):
    d_, s_ = duel_scene(k)
    s_ += [(PADS[k+1] + len(engine.load_audio(VOICE[k+1]))/engine.SR + .1, "tictac", .5, VOTE - .2)]      # tic-tac pendant le vote
    SCENES.append(SC(DUELS[k][2], k + 2, d_, s_, trans="whip" if k % 2 else "punch", trans_dur=.22, pad_out=VOTE))
SCENES.append(SC("ton_onze", 13, s13, [(.0, "whoosh", .5), (w(13, "commentaire"), "notif", .9), (w(13, "débat"), "stamp", .9), (w(13, "débat"), "crowd", .6)],
                 trans="tear_v", trans_dur=.45, pad_out=2.0))

def cover(path):
    cv = background(0, TITLE); split_bg(cv, 0, "ocov", 0)
    ransom_line(cv, "OM ou PSG ?", 330, 190, seed=9, fr=0)
    Label("LE ONZE DE LÉGENDE", "ocv1", font("title", 84), INK, GOLD, padx=30, pady=8, rough=5).draw(cv, 0, CX, 540, 1, -3)
    for k, (sl, x, y) in enumerate((("barthez", 270, 830), ("papin", 270, 1130), ("zlatan", 810, 830), ("mbappe", 810, 1130))):
        bubble(cv, sl, x, y, 125, 1, (-4, 3, 4, -3)[k], CIEL if x < CX else ROUGE)
    LBL("VS", "ovs1", font("title", 150), GOLD, NOIR, padx=24, pady=0, rough=3).draw(cv, 0, CX, 980, 1, -6)
    STAMP("TON ONZE ?", "ocv2", ROUGE, 120).draw(cv, 0, CX, 1440, 1, -5)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

def _stills(out, fracs, only):
    scene_timing(SCENES, VOICE); starts = np.cumsum([0] + [sc.T for sc in SCENES])
    os.makedirs(out, exist_ok=True); sheets = []
    for i, sc in enumerate(SCENES):
        if only and (i + 1) not in only: continue
        prev = engine._last_frame(SCENES, i - 1, starts, TITLE) if (i > 0 and sc.trans) else None
        ims = []
        for fr_ in fracs:
            t = fr_*sc.T; f = int((starts[i] + t)*FPS)
            cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T)
            if prev is not None and t < sc.trans_dur: engine.TRANSITIONS[sc.trans](cv, prev, t, sc.trans_dur, i)
            finish(cv, TITLE); ims.append(cv.resize((300, 533)))
        sheet = Image.new("RGB", (300*len(ims), 575), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            sheet.paste(im, (k*300, 42)); dd.text((k*300 + 8, 6), f"S{i+1} {fracs[k]*sc.T:.1f}/{sc.T:.1f}", font=font("mono", 24), fill=(230, 230, 230))
        p = os.path.join(out, f"ox_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", SLUG)
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(_stills(os.environ.get("STILLS_DIR", f"/tmp/{SLUG}_stills"), (.05, .18, .32, .46, .6, .74, .88, .98), only)); sys.exit()
    missing = [s for s in SLUGS if not os.path.exists(os.path.join(HERE, "photos", f"{s}.jpg"))]
    if missing and "--provisoire" not in args:
        sys.exit(f"Photos manquantes ({len(missing)}) : {', '.join(missing)}. Ajouter --provisoire pour un rendu avec bulles provisoires.")
    print(render_episode(SCENES, out, SLUG + ("_provisoire" if missing else ""), TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25, limit=True))
