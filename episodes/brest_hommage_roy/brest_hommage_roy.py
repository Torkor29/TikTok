"""HOMMAGE À ÉRIC ROY / histoire du Stade brestois (≈ 56 s). Remplace brest_ldc (ne pas publier l'ancienne : fin festive
« t'es fan d'Éric Roy ? OUI » déplacée depuis son décès le 17 juin 2026).
Collage papier : photos fournies -> coupures tramées (assets/brest), écussons autocollants (logos/brest*, ucl, ligue1, ligue2).
Ton : rythmé et joyeux jusqu'au chant, puis fin sobre (fond noir, pas de CTA, pas de tampon).

  python3 episodes/brest_hommage_roy/brest_hommage_roy.py output/brest_hommage_roy --stills
  python3 episodes/brest_hommage_roy/brest_hommage_roy.py output/brest_hommage_roy
"""
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "brest_ldc"))
from quiz import *
from brest_ldc import put, paper_bg, shake, flash, glitch, big, marker, typed, slide, HEART_R, table, gwenn, CREME, NOIR, BLANC, ROUGE, NAVY, JAUNE
from PIL import ImageEnhance

TITLE = "~/hommage $ ./eric_roy"
SLUG = "brest_hommage_roy"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
VOIX = os.path.join(HERE, "voix", "voix_complete.mp3")
TEXTE = open(os.path.join(HERE, "texte.txt")).read()
_W = json.load(open(os.path.join(HERE, "mots.json")))
def w(txt, n=1):
    k = 0
    for x in _W:
        if x["text"].lower() == txt.lower():
            k += 1
            if k == n: return x["start"]
    raise KeyError(f"{txt} #{n}")
NOIR_D = (12, 12, 14)

def legend(cv, fr, t, t0, name, who, x, y, h, rot, sub=None, key=""):
    """Coupure photo qui claque + nom au surligneur dessous."""
    if t < t0 - .05: return
    s = slam(t, t0 - .05, .18)
    put(cv, who, x, y, h, s, rot)
    marker(name, f"bh{key}", 60).draw(cv, fr, x, y + h*.56, slam(t, t0 + .05, .16), -rot*.6)
    if sub: big(sub, f"bh{key}s", 40, BLANC, ROUGE).draw(cv, fr, x, y + h*.56 + 80, slam(t, t0 + .25, .16), rot*.4)

# ------------------------------------------------------------------ plans
def s0(cv, fr, t):   # HOOK : 3 légendes en rafale -> « un coach »
    paper_bg(cv, fr, CREME)
    if t < w("mais") - .05:
        legend(cv, fr, t, 0.0, "GINOLA", "ginola", 300, 560, 640, -6, key="0a")
        legend(cv, fr, t, w("lama"), "LAMA", "lama", 790, 760, 600, 7, key="0b")
        legend(cv, fr, t, w("guivarc'h"), "GUIVARC'H", "guivarch", 380, 1300, 600, -4, key="0c")
        if t > w("légendes") - .15:
            put(cv, "brest", 810, 1420, 380, slam(t, w("brest") - .05, .18), 8)
            big("DES LÉGENDES", "bh0d", 110, BLANC, ROUGE).draw(cv, fr, CX, 1780, slam(t, w("légendes") - .1, .16), -3)
    else:
        put(cv, "roy", CX, 900, 980, slam(t, w("mais") - .05, .22)*(1 + .02*(t - w("mais"))), -2)
        big("SA PLUS BELLE HISTOIRE", "bh0e", 84, BLANC, NOIR).draw(cv, fr, CX, 220, slam(t, w("belle") - .1, .16), -2)
        marker("UN COACH L'A ÉCRITE", "bh0f", 84).draw(cv, fr, CX, 1600, slam(t, w("coach") - .05, .16), 2)

def s1(cv, fr, t):   # fin des années 80 : Brest Armorique et ses stars
    paper_bg(cv, fr, CREME)
    big("FIN DES ANNÉES 80", "bh1a", 90, BLANC, NOIR).draw(cv, fr, CX, 150, slam(t, w("fin") - .05, .16), -2)
    put(cv, "brest_armorique", CX, 420, 330, slam(t, w("armorique") - .1, .2), 3)
    legend(cv, fr, t, w("ginola", 2), "GINOLA", "ginola", 230, 820, 400, -6, key="1a")
    legend(cv, fr, t, w("lama", 2), "LAMA", "lama", 560, 860, 400, 4, key="1b")
    legend(cv, fr, t, w("cabañas"), "CABAÑAS", "cabanas", 880, 820, 380, -3, key="1c")
    legend(cv, fr, t, w("martins"), "C. MARTINS", "martins", 260, 1370, 400, 5, key="1d")
    legend(cv, fr, t, w("stéphane"), "GUIVARC'H", "guivarch", 640, 1400, 420, -5, sub="CHAMPION DU MONDE 98", key="1e")

def s2(cv, fr, t):   # Ribéry, plus tard
    paper_bg(cv, fr, CREME)
    big("PLUS TARD…", "bh2a", 110, BLANC, NOIR).draw(cv, fr, CX, 220, slam(t, w("plus", 2) - .05, .16), -3)
    put(cv, "ribery2", CX + slide(t, w("certain") - .15, .3, 1000), 960, 900, 1, 3)
    marker("FRANCK RIBÉRY", "bh2b", 100).draw(cv, fr, CX, 1550, slam(t, w("franck"), .16), -2)
    put(cv, "brest", 860, 1720, 260, slam(t, w("brest", 3) - .05, .18), 10)

def s3(cv, fr, t):   # 1991 liquidé, années dans l'ombre, Ligue 2
    dark = clamp((t - w("suivent"))/1.2)
    paper_bg(cv, fr, CREME)
    big("1991", "bh3a", 230, NOIR, BLANC, rough=4).draw(cv, fr, CX, 260, slam(t, w("mille") - .05, .18), -4)
    put(cv, "brest_armorique", CX, 820, 560, 1, -3)
    if t > w("liquidé") - .05: STAMP("LIQUIDÉ", "bh3b", ROUGE, 170).draw(cv, fr, CX, 840, slam(t, w("liquidé") - .05, .2), -12)
    if dark > 0:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, int(170*dark))); cv.alpha_composite(ov) if cv.mode == "RGBA" else cv.paste(ov, (0, 0), ov)
        big("DES ANNÉES DANS L'OMBRE", "bh3c", 76, BLANC, NOIR).draw(cv, fr, CX, 1300, slam(t, w("longues") - .05, .16), 2)
        put(cv, "ligue2", CX, 1620, 300, slam(t, w("ligue") - .05, .2), 6)

def s4(cv, fr, t):   # janvier 2023 : zone rouge -> Le Saint appelle Éric Roy
    paper_bg(cv, fr, CREME)
    if t > w("janvier") + .05:
        s_ = typed("JANVIER 2023", t, w("janvier"), 16)
        LBL(s_, "bh4a" + s_, font("mono", 96), NOIR, BLANC, padx=24, pady=6, rough=2).draw(cv, fr, CX, 200, 1, -2)
    if t < w("président") - .05: table(cv, fr, t, w("zone") - .45)
    else:
        put(cv, "lesaint", 330, 820, 560, slam(t, w("président") - .05, .2), -4)
        marker("DENIS LE SAINT", "bh4b", 70).draw(cv, fr, 330, 1180, slam(t, w("denis"), .16), 3)
        if t > w("appelle"): big("DRING !", "bh4c", 90, BLANC, ROUGE).draw(cv, fr, 800, 560, slam(t, w("appelle"), .15)*(1 + .05*math.sin(t*40)), 10)
        if t > w("éric") - .05:
            put(cv, "roy", 840 + slide(t, w("éric") - .05, .3, 900), 1420, 600, 1, 5)
            big("ÉRIC ROY", "bh4d", 110, NOIR, JAUNE).draw(cv, fr, 760, 1800, slam(t, w("éric"), .16), -3)

def s5(cv, fr, t):   # il sauve le club, puis 3e et Ligue des champions
    if t < w("troisième") - .05:
        paper_bg(cv, fr, ROUGE); rays(cv, (CX, 900), t, .9, 16, 1600, (226, 60, 66), .1, .3)
        put(cv, "roy", CX, 860, 900, 1 + .02*(t - w("il")), -3)
        STAMP("SAUVÉ", "bh5a", NOIR, 170).draw(cv, fr, CX, 1560, slam(t, w("sauve") - .05, .2), -10)
        if t > w("personne") - .1: big("LÀ OÙ PERSONNE N'OSAIT RÊVER…", "bh5b", 64, NOIR, BLANC).draw(cv, fr, CX, 200, slam(t, w("personne") - .1, .16), 2)
        return
    paper_bg(cv, fr, NAVY); rays(cv, (CX, 900), t, 1.0, 18, 1700, (30, 46, 110), .1, .4)
    if t < w("ligue", 3) - .05:
        big("3e", "bh5c", 420, BLANC, ROUGE, rough=4).draw(cv, fr, 380, 900, slam(t, w("troisième") - .05, .2), -6)
        put(cv, "ligue1", 800, 950, 420, slam(t, w("ligue", 2) - .05, .2), 8)
    else:
        put(cv, "ucl", CX, 820, 700, slam(t, w("ligue", 3) - .05, .22), -2)
        marker("1re FOIS DE SON HISTOIRE", "bh5d", 80).draw(cv, fr, CX, 1420, slam(t, w("première") - .1, .18), 2)
    confetti(cv, fr, "bh5cf", t - w("troisième"), 70, 3.5, [ROUGE, BLANC, JAUNE])

LYR = [("QUAND JE VOIS TON JEU", "quand", 1, BLANC, NOIR), ("JE SUIS AMOUREUX", "suis", 1, BLANC, ROUGE),
       ("QUAND J'ENTENDS SA VOIX", "quand", 2, BLANC, NOIR), ("J'SUIS FAN D'ÉRIC ROY !", "j'suis", 1, NOIR, JAUNE)]
def s6(cv, fr, t):   # le chant
    paper_bg(cv, fr, NAVY); rays(cv, (CX, 1500), t, .8, 20, 1800, (26, 38, 96), .08, .5)
    marker("TOUT UN PEUPLE CHANTE", "bh6a", 70).draw(cv, fr, CX, 170, slam(t, w("tout") - .05, .16), -2)
    put(cv, "roy", CX, 1440 + 14*math.sin(t*9), 640, 1, 4*math.sin(t*4.5))
    for k, (txt, word, n, fg, bg) in enumerate(LYR):
        t0 = w(word, n) - .05
        if t > t0: big(txt, f"bh6l{k}", 70, fg, bg, maxw=1040).draw(cv, fr, CX, 380 + k*165, slam(t, t0, .14), (-3, 3, -2, 2)[k])
    if t > w("amoureux") - .1:
        for k in range(8):
            u = prog(t, w("amoureux") - .1 + k*.12, 1.4)
            if 0 < u < 1: HEART_R.draw(cv, fr, 150 + (k*137) % 800, 1900 - 1500*u, .55*(1 - .3*u), 10*math.sin(k + t*3), 1 - u)

def s7(cv, fr, t):   # record : 8e saison d'affilée en Ligue 1
    paper_bg(cv, fr, CREME)
    big("AUJOURD'HUI", "bh7a", 100, BLANC, NOIR).draw(cv, fr, CX, 220, slam(t, w("aujourd'hui") - .05, .16), -2)
    n = 1 + int(7*clamp((t - w("huitième") + .3)/.6)) if t > w("huitième") - .3 else 0
    if n: big(f"{n}e", f"bh7n{n}", 360, BLANC, ROUGE, rough=4).draw(cv, fr, 360, 820, slam(t, w("huitième") - .3, .18), -5)
    put(cv, "ligue1", 800, 850, 400, slam(t, w("ligue") - .05 if False else w("saison") - .05, .2), 8)
    big("SAISON D'AFFILÉE EN LIGUE 1", "bh7b", 66, NOIR, BLANC).draw(cv, fr, CX, 1200, slam(t, w("saison") - .05, .16), 2)
    if t > w("record") - .05: STAMP("RECORD DU CLUB", "bh7c", ROUGE, 120).draw(cv, fr, CX, 1480, slam(t, w("record") - .05, .2), -6)
    put(cv, "brest", CX, 1760, 220, slam(t, w("aujourd'hui"), .2), 0)

def s8(cv, fr, t):   # hommage : sobre, noir, lent
    stage_fill(cv, fr, NOIR_D, "bh8bg")
    a = clamp((t - w("le", 7) + .1)/.8)
    z = 1 + .04*(t - w("le", 7))
    put(cv, "roy", CX, 800, 900, a*z if a < 1 else z, -1)
    if t > w("dix-sept") - .1:
        LBL("17 JUIN 2026", "bh8a", font("mono", 64), BLANC, NOIR_D, padx=10, pady=4, rough=0).draw(cv, fr, CX, 1340, pop_in(t, w("dix-sept") - .1, .6), 0)
    if t > w("éric", 2) - .1:
        LBL("ÉRIC ROY", "bh8b", font("title", 130), BLANC, NOIR_D, padx=10, pady=4, rough=0).draw(cv, fr, CX, 1470, pop_in(t, w("éric", 2) - .1, .6), 0)
    if t > w("merci") - .1:
        LBL("MERCI POUR TOUT, COACH", "bh8c", font("title", 70), NOIR, BLANC, padx=24, pady=6, rough=1).draw(cv, fr, CX, 230, pop_in(t, w("merci") - .1, .6), 0)
    if t > w("pensées") - .1:
        LBL("Pensées à sa famille et à ses proches", "bh8d", font("title", 46), (220, 220, 220), NOIR_D, padx=10, pady=4, rough=0).draw(cv, fr, CX, 1620, pop_in(t, w("pensées") - .1, .6), 0)
    if t > w("pensées") + 1.2:
        HEART_R.draw(cv, fr, CX, 1780, .5*pop_in(t, w("pensées") + 1.2, .6), 0)

CUTS = [0, w("à"), w("plus", 2), w("mais", 2), w("janvier"), w("il"), w("dans", 3), w("aujourd'hui"), w("le", 7)]
SHOTS = [s0, s1, s2, s3, s4, s5, s6, s7, s8]
IMPACTS = [0, w("lama"), w("guivarc'h"), w("ginola", 2), w("lama", 2), w("cabañas"), w("martins"), w("stéphane"), w("franck"), w("liquidé"),
           w("zone"), w("président"), w("éric"), w("sauve"), w("troisième"), w("ligue", 3), w("record")]
def shot_of(t):
    k = 0
    for i, c in enumerate(CUTS):
        if t >= c - .04: k = i
    return k
def draw(cv, fr, t, T):
    tv = t - PAD_IN; k = shot_of(tv); SHOTS[k](cv, fr, max(0.0, tv))
    c = CUTS[k]
    if k == len(SHOTS) - 1:                                   # passage au noir : fondu, pas d'effet
        return
    if k:
        punch(cv, tv, c, 1.06, .25); glitch(cv, tv, c); flash(cv, tv, c - .02, .1)
    for ti in IMPACTS: shake(cv, tv, ti, 16)
    drift(cv, t, T, .015)

P = PAD_IN
SFX = [(0.0, "boom", .8), (0.0, "camera", .6), (P + w("lama"), "camera", .6), (P + w("guivarc'h"), "camera", .6), (P + w("légendes") - .1, "stamp", .6),
       (P + w("mais") - .05, "whoosh", .5), (P + w("à") , "rewind", .5), (P + w("armorique") - .1, "stamp", .5)]
SFX += [(P + w(x, n) - .05, "camera", .5) for x, n in (("ginola", 2), ("lama", 2), ("cabañas", 1), ("martins", 1), ("stéphane", 1))]
SFX += [(P + w("certain") - .15, "whoosh", .5), (P + w("franck"), "stamp", .5), (P + w("mille") - .05, "typewriter", .5), (P + w("liquidé") - .05, "stamp", .9),
        (P + w("liquidé"), "groan", .4), (P + w("janvier"), "typewriter", .5), (P + w("zone"), "siren", .3), (P + w("appelle"), "phone", .5),
        (P + w("éric") - .05, "whoosh", .5), (P + w("sauve") - .05, "stamp", .9), (P + w("troisième") - .05, "boom", .8), (P + w("troisième"), "crowd", .6),
        (P + w("ligue", 3) - .05, "fanfare", .5), (P + w("ligue", 3), "goal_roar", .5), (P + w("dans", 3), "crowd", .7), (P + w("amoureux"), "heart", .4),
        (P + w("j'suis"), "goal_roar", .55), (P + w("aujourd'hui"), "whoosh", .4), (P + w("record") - .05, "stamp", .7)]
SCENES = [Scene("hommage", TEXTE, draw, SFX, pad_in=P, pad_out=2.2)]

def cover(path):
    cv = background(0, TITLE); stage_fill(cv, 0, NOIR_D, "bhcv")
    put(cv, "roy", CX, 900, 1000, 1, -1)
    LBL("MERCI COACH", "bhcv1", font("title", 150), BLANC, NOIR_D, padx=10, pady=4, rough=0).draw(cv, 0, CX, 210, 1, 0)
    LBL("ÉRIC ROY • STADE BRESTOIS", "bhcv2", font("title", 60), NOIR, BLANC, padx=24, pady=6, rough=1).draw(cv, 0, CX, 1560, 1, 0)
    put(cv, "brest", CX, 1760, 200, 1, 0)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

def stills(out):
    scene_timing(SCENES, [VOIX]); sc = SCENES[0]; os.makedirs(out, exist_ok=True)
    ts = [P + x for x in (.2, 2.9, 5.6, 13.0, 15.4, 17.8, 21.6, 23.9, 26.8, 29.2, 30.6, 33.3, 35.6, 41.4, 45.6, 53.9)]
    ims = []
    for t in ts:
        f = int(t*FPS); cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T); finish(cv, TITLE); ims.append(cv.resize((216, 384)))
    sheet = Image.new("RGB", (216*8, 2*414), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        x, y = (k % 8)*216, (k//8)*414; sheet.paste(im, (x, y + 30)); dd.text((x + 6, y + 4), f"{ts[k]:.1f}s", font=font("mono", 22), fill=(230, 230, 230))
    p = os.path.join(out, "sheet.jpg"); sheet.save(p, quality=82); return p

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", SLUG)
    if "--stills" in args: print(stills(f"/tmp/{SLUG}_stills")); sys.exit()
    os.makedirs(out, exist_ok=True); cover(os.path.join(out, f"{SLUG}_couverture.jpg"))
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=[VOIX], sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25, limit=True))
