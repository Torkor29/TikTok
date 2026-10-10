"""« Le meilleur joueur de l'histoire du PSG ? On en a gardé 8. Toi, tu choisis ! » — format TOP / DÉBAT (skill tiktok-foot-viral).
Chaque joueur : bulle photo ronde (vraie photo si présente dans photos/<slug>.jpg, sinon bulle « PHOTO » provisoire), numéro,
nom, années, un chiffre fort, une étiquette. Fin : grille des 8 bulles numérotées, « ton n°1 en commentaire + pourquoi »,
« résultat dans la prochaine vidéo » (épisode suivant = le classement des commentaires).

Photos : déposer photos/<slug>.jpg (slug = ronaldinho, rai, zlatan, thiago, cavani, neymar, dembele, mbappe), idéalement
des photos Wikimedia Commons sous licence libre, et remplir photos/credits.json {slug: "Auteur, licence"} (crédits affichés à la fin).

  python3 episodes/psg_top8/psg_top8.py output/psg_top8 --stills [2,3]
  python3 episodes/psg_top8/psg_top8.py output/psg_top8 --cover
  python3 episodes/psg_top8/psg_top8.py output/psg_top8
"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from story import *
from quiz import like_button
import engine

TITLE = "~/top $ ./psg"
SLUG = "psg_top8"
VOICE = [os.path.join(HERE, "voix", f"scene_{i}.mp3") for i in range(1, 11)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
PADS = [.55] + [.12]*9
WS, TEXTS = load_words(os.path.join(HERE, "alignement.json"))
def w(i, word, n=1, end=False):
    return PADS[i-1] + WS[i-1](word, n, end)

NAVY = (16, 40, 86); NAVY_D = (10, 24, 54); ROUGE = (210, 36, 42); ROUGE_D = (140, 20, 30); BLANC = (250, 250, 246); NOIR = (30, 28, 28)
INK = PAL["ink"]; GOLD = (250, 196, 30)

# (slug, nom affiché, années, chiffre fort, étiquette, mot du chiffre, mot de l'étiquette)
PLAYERS = [
    ("ronaldinho", "RONALDINHO", "2001 - 2003", "MAGIE PURE", "2 saisons seulement", "deux", "magie"),
    ("rai", "RAÍ", "1993 - 1998", "LE CAPITAINE", "Coupe des coupes 1996", "capitaine", "Coupe"),
    ("zlatan", "ZLATAN", "2012 - 2016", "156 BUTS", "et un ego XXL", "cent", "ego"),
    ("thiago", "THIAGO SILVA", "2012 - 2020", "LE MUR", "8 saisons, capitaine", "huit", "mur"),
    ("cavani", "CAVANI", "2013 - 2020", "200 BUTS", "le 1er à 200 au club", "deux", "premier"),
    ("neymar", "NEYMAR", "2017 - 2023", "222 M€", "transfert le plus cher", "deux", "transfert"),
    ("dembele", "DEMBÉLÉ", "arrivé en 2023", "BALLON D'OR", "+ Ligue des champions 2025", "Ligue", "Ballon"),
    ("mbappe", "MBAPPÉ", "2017 - 2024", "256 BUTS", "record du club", "deux", "record"),
]
COUNTERS = {"zlatan": 156, "cavani": 200, "mbappe": 256}
CREDITS = json.load(open(os.path.join(HERE, "photos", "credits.json"))) if os.path.exists(os.path.join(HERE, "photos", "credits.json")) else {}

# ------------------------------------------------------------------ bulles photo
_bub = {}
def _photo(slug):
    p = os.path.join(HERE, "photos", f"{slug}.jpg")
    if os.path.exists(p):
        im = Image.open(p).convert("RGB"); w_, h_ = im.size; c = min(w_, h_)
        top = int(max(0, min(h_ - c, h_*.05)))                    # cadrage haut (le visage) pour un portrait vertical
        return im.crop(((w_ - c)//2, top, (w_ - c)//2 + c, top + c)), True
    im = Image.new("RGB", (600, 600), (196, 200, 210)); d = ImageDraw.Draw(im)     # provisoire : silhouette + « PHOTO »
    d.ellipse([200, 90, 400, 290], fill=(150, 156, 170)); d.chord([110, 300, 490, 700], 180, 360, fill=(150, 156, 170))
    d.text((300, 520), "PHOTO", font=font("title", 70), fill=(110, 116, 130), anchor="mm")
    return im, False

def bubble_sprite(slug, r, ring=ROUGE):
    key = (slug, r, ring)
    if key in _bub: return _bub[key]
    im, _ = _photo(slug); im = im.resize((2*r, 2*r), Image.LANCZOS)
    pad = 30; S = 2*r + 2*pad
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.ellipse([pad + 10, pad + 16, pad + 2*r + 10, pad + 2*r + 16], fill=(0, 0, 0, 90))            # ombre portée
    d.ellipse([pad - 14, pad - 14, pad + 2*r + 14, pad + 2*r + 14], fill=ring + (255,))           # anneau couleur
    d.ellipse([pad - 6, pad - 6, pad + 2*r + 6, pad + 2*r + 6], fill=BLANC + (255,))              # liseré blanc
    m = Image.new("L", (2*r, 2*r), 0); ImageDraw.Draw(m).ellipse([0, 0, 2*r - 1, 2*r - 1], fill=255)
    L.paste(im, (pad, pad), m)
    L.info["anchor"] = (S/2, S/2); _bub[key] = L; return L

def bubble(cv, slug, x, y, r, s=1.0, rot=0.0, ring=ROUGE):
    if s <= .02: return
    blit(cv, bubble_sprite(slug, r, ring), x, y, s, rot)

def num_badge(cv, fr, k, x, y, s=1.0):
    LBL(f"N°{k}", f"pnum{k}", font("title", 110), BLANC, NOIR, padx=26, pady=2, rough=3).draw(cv, fr, x, y, s, -8)

def progress(cv, k):
    """8 pastilles en haut : celle du joueur en cours est rouge, les précédentes blanches."""
    d = ImageDraw.Draw(cv)
    for j in range(8):
        x = CX - 7*45 + j*90; c = ROUGE if j == k - 1 else (BLANC if j < k - 1 else (90, 100, 130))
        d.ellipse([x - 18, 196 - 18, x + 18, 196 + 18], fill=c, outline=NOIR, width=3)

def stripes_bg(cv, fr, key, c1, c2, t):
    stage_fill(cv, fr, c1, key); d = ImageDraw.Draw(cv); off = (t*60) % 240
    for k in range(-4, 13):
        x = k*240 + off; d.polygon([(x, 0), (x + 120, 0), (x + 120 - 700, 1920), (x - 700, 1920)], fill=c2)

# ------------------------------------------------------------------ SCÈNE 1 — hook
K1a = Label("LE MEILLEUR DE L'HISTOIRE ?", "pk1a", font("title", 76), INK, GOLD, maxw=1000, padx=30, pady=8, rough=5)
K1b = STAMP("À TOI DE CHOISIR !", "pk1b", ROUGE, 110)
K1c = KW("8 LÉGENDES", "pk1c", BLANC, NOIR, 110)
def s1(cv, fr, t, T):
    stripes_bg(cv, fr, "ps1", NAVY_D, NAVY, t); rays(cv, (CX, 1050), t, .6, 16, 1500, (60, 90, 160), .12)
    ransom_line(cv, "PSG", 360, 230, seed=7, fr=fr, scale=slam(t, -.12, .22))
    K1a.draw(cv, fr, CX, 560, 1 if fr == 0 else slam(t, .02, .2), -3)
    th = w(1, "huit") - .1
    for j, p in enumerate(PLAYERS):          # les 8 bulles en couronne
        a = 2*math.pi*j/8 - math.pi/2 + t*.25; x = CX + 330*math.cos(a); y = 1080 + 330*math.sin(a)
        bubble(cv, p[0], x, y, 95, pop_in(t, .05 + .05*j, .25), 4*math.sin(t*3 + j))
    show(cv, fr, K1c, t, th, None, CX, 1080, 3)
    show_stamp(cv, fr, K1b, t, w(1, "Toi") - .05, CX, 1500, -5)
    impact(cv, t, .45, 20); flashes(cv, t, .45, .12, .5); impact(cv, t, w(1, "Toi"), 14); drift(cv, t, T, .04)

# ------------------------------------------------------------------ SCÈNES 2 à 9 — un joueur par scène
LBLN = {p[0]: Label(p[1], f"pname{p[0]}", font("title", 120 if len(p[1]) < 10 else 96), BLANC, ROUGE, padx=30, pady=6, rough=4) for p in PLAYERS}
LBLY = {p[0]: TAG(p[2], f"pyear{p[0]}", PAL["paper"], INK, 52) for p in PLAYERS}
LBLT = {p[0]: TAG(p[4], f"ptag{p[0]}", GOLD, INK, 56) for p in PLAYERS}
def player_scene(k):
    slug, name, years, stat, tag, kstat, ktag = PLAYERS[k - 1]; i = k + 1
    bg = (NAVY_D, NAVY) if k % 2 else (ROUGE_D, ROUGE); ring = ROUGE if k % 2 else NAVY
    def draw(cv, fr, t, T):
        stripes_bg(cv, fr, f"ps{i}", bg[0], bg[1], t); rays(cv, (CX, 820), t, .5, 14, 1400, BLANC, .07)
        progress(cv, k)
        tn = w(i, "numéro")
        bubble(cv, slug, CX, 820 + 8*math.sin(t*2.5), 300, slam(t, tn, .25), -6 + 4*math.sin(t*1.7), ring)
        num_badge(cv, fr, k, CX - 300, 560, slam(t, tn + .1, .2))
        LBLN[slug].draw(cv, fr, CX, 1210, slam(t, tn + .35, .22), -3)
        show(cv, fr, LBLY[slug], t, tn + .5, None, CX + 200, 1320, 3)
        ts, tt = w(i, kstat) - .08, w(i, ktag) - .08
        if slug in COUNTERS:
            txt = f"{counter(0, COUNTERS[slug], ease_out_cubic(prog(t, ts, .7)))} BUTS"
            if t > ts: LBL(txt, f"pcnt{slug}", font("title", 130), NOIR, GOLD, padx=26, pady=2, rough=3).draw(cv, fr, CX, 1460, pop_in(t, ts, .25), 2)
        else:
            if t > ts: LBL(stat, f"pstat{slug}", font("title", 110), NOIR, GOLD, padx=26, pady=2, rough=3).draw(cv, fr, CX, 1460, slam(t, ts, .22), 2)
        show(cv, fr, LBLT[slug], t, tt, None, CX, 1590, -2)
        impact(cv, t, tn + .05, 14); impact(cv, t, ts + .08, 12); drift(cv, t, T, .05)
    sfx = [(.0, "whoosh", .5), (w(i, "numéro") + .05, "boom", .5), (w(i, "numéro") + .35, "stamp", .6),
           (w(i, kstat), "stamp", .8), (w(i, ktag), "pop", .6)]
    if slug in COUNTERS: sfx += [(w(i, kstat) + .1, "coin", .5)]
    if slug == "neymar": sfx += [(w(i, kstat) + .1, "cash", .7)]
    if slug in ("dembele", "mbappe"): sfx += [(w(i, ktag), "crowd", .7)]
    return draw, sfx

# ------------------------------------------------------------------ SCÈNE 10 — la grille, vote en commentaire
K10a = KW("TON N°1 ?", "pk10a", BLANC, NOIR, 140)
K10b = STAMP("RÉSULTAT DANS LA PROCHAINE VIDÉO", "pk10b", ROUGE, 66)
def s10(cv, fr, t, T):
    stripes_bg(cv, fr, "ps10", NAVY_D, NAVY, t)
    kw(cv, fr, K10a, t, .05, None, CX, 300, -3)
    for j, p in enumerate(PLAYERS):
        x = 160 + (j % 4)*253; y = 620 + (j // 4)*330
        bubble(cv, p[0], x, y, 105, pop_in(t, .1 + .06*j, .25), 3*math.sin(t*3 + j), ROUGE if j % 2 == 0 else NAVY)
        LBL(str(j + 1), f"pg{j}", font("title", 64), BLANC, ROUGE, padx=14, pady=0, rough=2).draw(cv, fr, x - 85, y - 85, pop_in(t, .2 + .06*j, .25), -6)
        LBL(p[1].split()[0], f"pgn{j}", font("title", 40), INK, PAL["paper"], padx=10, pady=2, rough=2).draw(cv, fr, x, y + 130, pop_in(t, .2 + .06*j, .25), 0)
    tc = w(10, "commentaire") - .15
    sb = pop_in(t, tc, .3)
    if sb > .01:
        speech_bubble(cv, fr, "pbub10", "Le 3, parce que…", 520, 1330, sb, (1, 1), 66)
        d = ImageDraw.Draw(cv); arrow(d, (740, 1360), (985, 1440), prog(t, tc + .1, .4), GOLD, 14, 3, 44, .25)
    show_stamp(cv, fr, K10b, t, w(10, "résultat") - .05, CX, 1520, -4)
    if CREDITS and t > T - 2.6:            # crédits photos (licences libres) en fin de vidéo
        txt = "Photos : " + " · ".join(CREDITS.values())
        Label(txt, "pcred", font("sans", 26), BLANC, NOIR, maxw=1000, padx=12, pady=6, rough=0).draw(cv, fr, CX, 1700, 1, 0)
    impact(cv, t, tc + .15, 10); drift(cv, t, T, .03)

# ------------------------------------------------------------------ scènes + bruitages
def SC(name, n, fn, sfx, trans=None, trans_dur=.25, pad_out=.2):
    return Scene(name, TEXTS[n-1], fn, sfx, pad_in=PADS[n-1], pad_out=pad_out, trans=trans, trans_dur=trans_dur)
SCENES = [SC("hook", 1, s1, [(.0, "hook", 1.3)] + [(.05 + .05*j, "pop", .35) for j in range(8)] + [(w(1, "huit"), "stamp", .6), (w(1, "Toi"), "stamp", .9)])]
for k in range(1, 9):
    d_, sfx_ = player_scene(k)
    SCENES.append(SC(PLAYERS[k-1][0], k + 1, d_, sfx_, trans=("whip" if k % 2 else "punch"), trans_dur=.25))
SCENES.append(SC("vote", 10, s10, [(.0, "whoosh", .5)] + [(.1 + .06*j, "pop", .35) for j in range(8)]
                 + [(w(10, "commentaire"), "notif", .9), (w(10, "résultat"), "stamp", .9)], trans="tear_v", trans_dur=.45, pad_out=3.0))

# ------------------------------------------------------------------ couverture
def cover(path):
    cv = background(0, TITLE); stripes_bg(cv, 0, "pcov", NAVY_D, NAVY, 0)
    ransom_line(cv, "PSG", 330, 220, seed=7, fr=0)
    Label("LE MEILLEUR DE L'HISTOIRE ?", "pcv1", font("title", 80), INK, GOLD, maxw=1000, padx=30, pady=8, rough=5).draw(cv, 0, CX, 530, 1, -3)
    for j, p in enumerate(PLAYERS):
        x = 160 + (j % 4)*253; y = 800 + (j // 4)*300
        bubble(cv, p[0], x, y, 105, 1, (-4, 3, -2, 5, 3, -4, 4, -3)[j], ROUGE if j % 2 == 0 else NAVY)
        LBL(str(j + 1), f"pg{j}", font("title", 64), BLANC, ROUGE, padx=14, pady=0, rough=2).draw(cv, 0, x - 85, y - 85, 1, -6)
    STAMP("TON N°1 ?", "pcv2", ROUGE, 120).draw(cv, 0, CX, 1450, 1, -5)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

def stills(out, fracs=(.05, .18, .32, .46, .6, .74, .88, .98), only=None):
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
        p = os.path.join(out, f"pt_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", SLUG)
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", f"/tmp/{SLUG}_stills"), only=only)); sys.exit()
    missing = [p[0] for p in PLAYERS if not os.path.exists(os.path.join(HERE, "photos", f"{p[0]}.jpg"))]
    if missing and "--provisoire" not in args:
        sys.exit(f"Photos manquantes : {', '.join(missing)} (photos/<slug>.jpg). Ajouter --provisoire pour un rendu avec bulles provisoires.")
    print(render_episode(SCENES, out, SLUG + ("_provisoire" if missing else ""), TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25, limit=True))
