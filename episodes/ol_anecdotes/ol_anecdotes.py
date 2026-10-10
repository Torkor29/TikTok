"""« Lyon : 5 anecdotes de fou sur l'OL. Et la dernière a failli tuer le club ! » — NOUVEAU FORMAT : compte à rebours 5 → 1.
DA hybride : nos étiquettes / tampons / compteurs en papier découpé par-dessus des images IA « photo de maquette en papier »
(comme l'hommage Messi papier réaliste). Images en paysage (1280×720) : présentées comme une photo encadrée avec bord blanc
(papier), sur le même plan agrandi, flouté et assombri en fond ; caméra lente (zoom + pan) dans le cadre.

  python3 episodes/ol_anecdotes/ol_anecdotes.py output/ol_anecdotes --stills [2,3]
  python3 episodes/ol_anecdotes/ol_anecdotes.py output/ol_anecdotes --cover
  python3 episodes/ol_anecdotes/ol_anecdotes.py output/ol_anecdotes
"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from story import *
from quiz import sub_button
from PIL import ImageFilter, ImageEnhance
import engine

TITLE = "~/anecdotes $ ./ol"
SLUG = "ol_anecdotes"
VOICE = [os.path.join(HERE, "voix", f"scene_{i}.mp3") for i in range(1, 8)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
PADS = [.55] + [.12]*6
WS, TEXTS = load_words(os.path.join(HERE, "alignement.json"))
def w(i, word, n=1, end=False):
    return PADS[i-1] + WS[i-1](word, n, end)

ROUGE = (206, 30, 46); BLEU = (16, 44, 110); BLEU_D = (8, 22, 60); BLANC = (250, 250, 246); NOIR = (30, 28, 28)
GOLD = (250, 196, 30); VERT = (40, 150, 80); INK = PAL["ink"]

# ------------------------------------------------------------------ photo de maquette encadrée + fond flouté
CW, CH = 1000, 562                               # taille de la photo encadrée
_ph = {}
def _plate(key):
    if key not in _ph:
        im = Image.open(os.path.join(HERE, "img", f"{key}.png")).convert("RGB")
        bg = im.resize((int(1920*im.width/im.height), 1920), Image.LANCZOS)
        x0 = (bg.width - W)//2; bg = bg.crop((x0, 0, x0 + W, 1920)).filter(ImageFilter.GaussianBlur(22))
        bg = ImageEnhance.Brightness(bg).enhance(.45)
        big = im.resize((int(CW*1.18), int(CH*1.18)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 60, 2))
        _ph[key] = (bg, big)
    return _ph[key]

def plate(cv, fr, key, t, T, y=820, z=(1.0, 1.12), pan=(0, 0), s=1.0, rot=-1.5):
    """Fond flouté plein écran + photo encadrée (bord blanc papier, ombre) avec zoom/pan lent."""
    bg, big = _plate(key); cv.paste(bg, (0, 0))
    u = clamp(t/max(T, .1), 0, 1); zz = lerp(z[0], z[1], u)
    vw, vh = int(CW/zz*1.0), int(CH/zz*1.0)
    cx = big.width/2 + pan[0]*u*(big.width - vw)/2; cy = big.height/2 + pan[1]*u*(big.height - vh)/2
    view = big.crop((int(cx - vw/2), int(cy - vh/2), int(cx - vw/2) + vw, int(cy - vh/2) + vh)).resize((CW, CH), Image.BILINEAR)
    b = 22; card = Image.new("RGBA", (CW + 2*b, CH + 2*b + 40), (250, 248, 240, 255)); card.paste(view, (b, b))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([12, 18, card.width, card.height], fill=(0, 0, 0, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    if s <= .02: return
    for L, dx, dy in ((sh, 10, 16), (card, 0, 0)):
        R = L.rotate(rot, resample=Image.BICUBIC, expand=True)
        if s != 1: R = R.resize((int(R.width*s), int(R.height*s)), Image.BICUBIC)
        cv.paste(R, (int(CX - R.width/2 + dx), int(y - R.height/2 + dy)), R)

def big_num(cv, fr, n, t, t0, x=150, y=330):
    LBL(str(n), f"onum{n}", font("title", 230), GOLD, NOIR, padx=34, pady=0, rough=4).draw(cv, fr, x, y, slam(t, t0, .25), -8)

def ribbon(cv, n_done):
    """5 pastilles en haut : le compte à rebours (5 → 1)."""
    d = ImageDraw.Draw(cv)
    for j in range(5):
        x = CX - 2*70 + j*70; lit = j < n_done
        d.ellipse([x - 22, 186 - 22, x + 22, 186 + 22], fill=ROUGE if lit else (60, 70, 100), outline=BLANC, width=3)
        d.text((x, 188), str(5 - j), font=font("title", 30), fill=BLANC, anchor="mm")

# ------------------------------------------------------------------ SCÈNE 1 — hook
K1a = Label("5 ANECDOTES DE FOU", "ok1a", font("title", 84), INK, GOLD, padx=30, pady=8, rough=5)
K1b = STAMP("LA DERNIÈRE A FAILLI TUER LE CLUB", "ok1b", ROUGE, 64)
def s1(cv, fr, t, T):
    plate(cv, fr, "hook", t, T, y=900, z=(1.0, 1.18), pan=(.4, -.2), s=slam(t, -.15, .25))
    ransom_line(cv, "LYON", 330, 220, seed=12, fr=fr, scale=slam(t, -.12, .22))
    K1a.draw(cv, fr, CX, 545, 1 if fr == 0 else slam(t, .05, .2), -3)
    for j in range(5):                       # les 5 numéros qui défilent en teaser
        a = pop_in(t, w(1, "cinq") + .08*j, .2)
        if a > .01: LBL(str(5 - j), f"oteas{j}", font("title", 90), BLANC, ROUGE if j == 4 else BLEU, padx=18, pady=0, rough=3).draw(cv, fr, 180 + j*180, 1290, a, (-6, 4, -3, 5, -8)[j])
    show_stamp(cv, fr, K1b, t, w(1, "dernière") - .05, CX, 1470, -4)
    impact(cv, t, .45, 20); flashes(cv, t, .45, .12, .5); impact(cv, t, w(1, "tuer"), 16); drift(cv, t, T, .03)

# ------------------------------------------------------------------ SCÈNES 2 à 6 — les 5 anecdotes
def s2(cv, fr, t, T):     # 5 — 1987, D2, dettes… Tapie
    plate(cv, fr, "p5", t, T, z=(1.0, 1.15), pan=(-.3, .1)); ribbon(cv, 1); big_num(cv, fr, 5, t, .02)
    gray = 1 - prog(t, w(2, "Tapie") - .2, .3); grayscale(cv, .7*gray)
    show(cv, fr, KW("1987", "o2y", INK, size=120), t, w(2, "quatre-vingt-sept") - .1, None, 640, 330, 3)
    show(cv, fr, TAG("en 2e division", "o2t1", PAL["paper"], INK, 60), t, w(2, "deuxième") - .1, None, CX, 1230, -2)
    show_stamp(cv, fr, STAMP("CRIBLÉ DE DETTES", "o2s1", ROUGE, 90), t, w(2, "dettes") - .1, CX, 1370, 4)
    tt = w(2, "Tapie") - .1
    show_stamp(cv, fr, STAMP("TAPIE, LE PATRON DE L'OM ?!", "o2s2", BLEU, 70), t, tt, CX, 1520, -4)
    show(cv, fr, TAG("selon la légende", "o2t2", GOLD, INK, 48), t, w(2, "légende") - .05, None, CX + 230, 1640, 3)
    impact(cv, t, w(2, "dettes"), 12); impact(cv, t, tt + .1, 18); drift(cv, t, T, .03)

def s3(cv, fr, t, T):     # 4 — Juninho, 44 coups francs
    plate(cv, fr, "p4", t, T, z=(1.0, 1.2), pan=(.5, -.3)); ribbon(cv, 2); big_num(cv, fr, 4, t, .02)
    kw(cv, fr, KW("JUNINHO", "o3n", BLANC, ROUGE, 120), t, w(3, "Juninho") - .1, None, 650, 330, 3)
    tq = w(3, "Quarante-quatre") - .05
    if t > tq:
        LBL(counter(0, 44, ease_out_cubic(prog(t, tq, .8))), "o3c", font("title", 200), NOIR, GOLD, padx=30, pady=0, rough=3).draw(cv, fr, CX - 200, 1320, pop_in(t, tq, .25), -4)
        LBL("COUPS FRANCS", "o3c2", font("title", 70), BLANC, NOIR, padx=20, pady=4, rough=3).draw(cv, fr, CX + 210, 1290, pop_in(t, tq + .2, .25), 3)
        LBL("DIRECTS !", "o3c3", font("title", 70), NOIR, BLANC, padx=20, pady=4, rough=3).draw(cv, fr, CX + 210, 1390, pop_in(t, tq + .35, .25), -2)
    show(cv, fr, TAG("ils savaient… et prenaient quand même le but", "o3t", PAL["paper"], INK, 46), t, w(3, "gardiens") - .1, None, CX, 1560, -2)
    impact(cv, t, tq + .8, 14); drift(cv, t, T, .03)

def s4(cv, fr, t, T):     # 3 — 7 titres d'affilée
    plate(cv, fr, "p3", t, T, z=(1.05, 1.0), pan=(0, 0)); ribbon(cv, 3); big_num(cv, fr, 3, t, .02)
    kw(cv, fr, KW("7 TITRES D'AFFILÉE", "o4k", INK, size=84), t, w(4, "sept") - .1, None, 640, 330, 3)
    ty = w(4, "deux") - .1
    for j, yr in enumerate(range(2002, 2009)):
        a = slam(t, ty + .17*j, .18)
        if a > 0: LBL(str(yr), f"o4y{yr}", font("title", 62), NOIR, GOLD, padx=12, pady=0, rough=2).draw(cv, fr, 140 + (j % 4)*265, 1250 + (j // 4)*100, a, (-5, 3, -2, 4, 5, -3, 2)[j])
    show_stamp(cv, fr, STAMP("RECORD DE FRANCE", "o4s", ROUGE, 96), t, w(4, "Personne") - .1, CX, 1510, -4)
    if t > ty: confetti(cv, fr, "o4cf", t - ty, 70, 3, [ROUGE, BLEU, BLANC, GOLD])
    impact(cv, t, w(4, "Personne"), 14); drift(cv, t, T, .03)

def s5(cv, fr, t, T):     # 2 — les Lyonnaises, 8 Ligues des champions
    plate(cv, fr, "p2", t, T, z=(1.0, 1.12), pan=(0, -.3)); ribbon(cv, 4); big_num(cv, fr, 2, t, .02)
    kw(cv, fr, KW("LES LYONNAISES", "o5k", BLANC, BLEU, 96), t, w(5, "Lyonnaises") - .15, None, 640, 330, 3)
    th = w(5, "huit") - .05
    if t > th:
        LBL(counter(0, 8, ease_out_cubic(prog(t, th, .6))), "o5c", font("title", 220), NOIR, GOLD, padx=34, pady=0, rough=3).draw(cv, fr, 230, 1330, pop_in(t, th, .25), -5)
        LBL("LIGUES DES", "o5c2", font("title", 66), BLANC, NOIR, padx=18, pady=2, rough=3).draw(cv, fr, 650, 1280, pop_in(t, th + .15, .25), 3)
        LBL("CHAMPIONS", "o5c3", font("title", 66), NOIR, BLANC, padx=18, pady=2, rough=3).draw(cv, fr, 650, 1375, pop_in(t, th + .3, .25), -2)
    show_stamp(cv, fr, STAMP("RECORD D'EUROPE", "o5s", ROUGE, 100), t, w(5, "Record") - .1, CX, 1530, -4)
    if t > th: confetti(cv, fr, "o5cf", t - th, 90, 3, [ROUGE, BLEU, BLANC, GOLD])
    impact(cv, t, w(5, "Record"), 16); drift(cv, t, T, .03)

def s6(cv, fr, t, T):     # 1 — juin 2025 : rétrogradé… puis sauvé en appel
    ts = w(6, "sauvé") - .1
    plate(cv, fr, "p1", t, T, z=(1.0, 1.15), pan=(.2, .2)); ribbon(cv, 5); big_num(cv, fr, 1, t, .02)
    if t < ts: grayscale(cv, .8); siren_lights(cv, t, .18)
    kw(cv, fr, KW("JUIN 2025", "o6k", INK, size=110), t, w(6, "juin") - .1, None, 650, 330, 3)
    tr = w(6, "rétrograde") - .05
    if t < ts: show_stamp(cv, fr, STAMP("RÉTROGRADÉ EN L2", "o6s1", ROUGE, 100), t, tr, CX, 1290, -6)
    show(cv, fr, TAG("15 jours plus tard, en appel…", "o6t", PAL["paper"], INK, 54), t, w(6, "Quinze") - .1, None, CX, 1420, 2)
    if t > ts:
        STAMP("SAUVÉ !", "o6s2", VERT, 180).draw(cv, fr, CX, 1290, slam(t, ts, .2), -8)
        confetti(cv, fr, "o6cf", t - ts, 90, 3, [ROUGE, BLEU, BLANC, GOLD])
    impact(cv, t, tr + .05, 20); impact(cv, t, ts + .05, 22); flashes(cv, t, ts + .05, .1, .4); drift(cv, t, T, .03)

# ------------------------------------------------------------------ SCÈNE 7 — laquelle t'a choqué ?
K7 = KW("LAQUELLE T'A CHOQUÉ ?", "o7k", BLANC, NOIR, 84)
def s7(cv, fr, t, T):
    bg, _ = _plate("hook"); cv.paste(bg, (0, 0))
    kw(cv, fr, K7, t, .05, None, CX, 300, -3)
    for j, (k, n) in enumerate((("p5", 5), ("p4", 4), ("p3", 3), ("p2", 2), ("p1", 1))):
        _, big = _plate(k); th = big.resize((300, 169), Image.BILINEAR)
        x = (220, 540, 860, 380, 700)[j]; y = (560, 560, 560, 800, 800)[j]; a = pop_in(t, .15 + .08*j, .25)
        if a > .01:
            card = Image.new("RGB", (316, 185), (250, 248, 240)); card.paste(th, (8, 8))
            R = card.rotate((-4, 3, -2, 4, -3)[j], resample=Image.BICUBIC, expand=True).resize((int(320*a), int(190*a)))
            cv.paste(R, (int(x - R.width/2), int(y - R.height/2)))
            LBL(str(n), f"o7n{n}", font("title", 70), BLANC, ROUGE, padx=14, pady=0, rough=2).draw(cv, fr, x - 140, y - 80, a, -6)
    tc = w(7, "commentaire") - .15
    sb = pop_in(t, tc, .3)
    if sb > .01:
        speech_bubble(cv, fr, "o7b", "La 5, Tapie quoi ?!", 520, 1060, sb, (1, 1), 64)
        d = ImageDraw.Draw(cv); arrow(d, (760, 1090), (985, 1180), prog(t, tc + .1, .4), GOLD, 14, 3, 44, .25)
    ta = w(7, "abonne-toi")
    sub_button(cv, fr, CX, 1340, t, ta - .1, ta + .25)
    confetti(cv, fr, "o7cf", t - ta, 80, 4, [ROUGE, BLEU, BLANC, GOLD])
    impact(cv, t, ta, 12); drift(cv, t, T, .03)

# ------------------------------------------------------------------ scènes + bruitages
def SC(name, n, fn, sfx, trans=None, trans_dur=.25, pad_out=.25):
    return Scene(name, TEXTS[n-1], fn, sfx, pad_in=PADS[n-1], pad_out=pad_out, trans=trans, trans_dur=trans_dur)
SCENES = [
    SC("hook", 1, s1, [(.0, "hook", 1.3), (w(1, "cinq"), "whoosh", .5)] + [(w(1, "cinq") + .08*j, "pop", .35) for j in range(5)]
       + [(w(1, "dernière"), "stamp", .9), (w(1, "tuer"), "boom", .6)]),
    SC("n5_tapie", 2, s2, [(.0, "rip", .5), (.02, "stamp", .7), (w(2, "quatre-vingt-sept"), "pop", .5), (w(2, "dettes"), "stamp", .8),
                           (w(2, "dettes"), "coin", .5), (w(2, "Tapie") - .1, "scratch", .6), (w(2, "Tapie"), "stamp", .9)], trans="tear_v", trans_dur=.4),
    SC("n4_juninho", 3, s3, [(.0, "whoosh", .5), (.02, "stamp", .7), (w(3, "Juninho"), "kick", .7), (w(3, "Quarante-quatre"), "coin", .5),
                             (w(3, "Quarante-quatre") + .8, "crowd", .7), (w(3, "gardiens"), "groan", .4)], trans="whip"),
    SC("n3_7titres", 4, s4, [(.0, "rip", .5), (.02, "stamp", .7)] + [(w(4, "deux") - .1 + .17*j, "pop", .4) for j in range(7)]
       + [(w(4, "Personne"), "stamp", .9), (w(4, "Personne"), "crowd_long", .8)], trans="tear_h", trans_dur=.45),
    SC("n2_lyonnaises", 5, s5, [(.0, "whoosh", .5), (.02, "stamp", .7), (w(5, "huit"), "sparkle", .6), (w(5, "Record"), "stamp", .9),
                                (w(5, "Record"), "crowd_long", .9)], trans="punch", trans_dur=.3),
    SC("n1_dncg", 6, s6, [(.0, "siren", .4, 2.0), (.02, "stamp", .7), (w(6, "rétrograde"), "gavel", .9), (w(6, "rétrograde") + .05, "boom", .6),
                          (w(6, "Quinze"), "tick", .5), (w(6, "sauvé"), "stamp", 1.0), (w(6, "sauvé"), "crowd_long", 1.0)], trans="tear_d", trans_dur=.45),
    SC("fin", 7, s7, [(.0, "whoosh", .5)] + [(.15 + .08*j, "pop", .4) for j in range(5)] + [(w(7, "commentaire"), "notif", .9),
                      (w(7, "abonne-toi"), "pop2", .7), (w(7, "abonne-toi") + .25, "notif", .8)], trans="whip", pad_out=1.6),
]

def cover(path):
    cv = background(0, TITLE); plate(cv, 0, "hook", 0, 1, y=980, z=(1.05, 1.05), s=1.0)
    ransom_line(cv, "LYON", 330, 230, seed=12, fr=0)
    Label("5 ANECDOTES DE FOU", "ocv1", font("title", 88), INK, GOLD, padx=30, pady=8, rough=5).draw(cv, 0, CX, 560, 1, -3)
    STAMP("LA 1re A FAILLI TUER LE CLUB", "ocv2", ROUGE, 70).draw(cv, 0, CX, 1430, 1, -4)
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
        p = os.path.join(out, f"ol_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
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
