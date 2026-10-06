"""Hommage Messi, version « PAPIER RÉALISTE » (~43 s) : mêmes voix (Léo) et mêmes moments que messi_adieu, rendu photo
de maquettes en papier. Création originale : nos plans, nos textes, notre montage (aucune image, phrase ni logo de pub).

Images : 20 plans « diorama en papier » générés par IA (ElevenLabs, gpt-image-2, 720×1280, voir plans.json / prompts.json).
- 5 plans sans le visage du joueur sont animés en vidéo IA (Veo 3.1 Lite, 4 s, sans son) : stade, carton rouge, filet,
  penalty raté, tribune. Veo refuse d'animer le visage d'une personnalité réelle : on ne contourne pas ce refus.
- Les 15 plans où il apparaît sont animés au montage en 2,5D (engine/parallax.py) : personnage détouré (BiRefNet),
  fond rebouché et flouté, caméra qui avance plus vite sur le personnage que sur le fond (profondeur), respiration,
  mouvements propres (il s'éloigne vers la pelouse, il est porté en l'air), halos de lumière, poussière, confettis, grain.

  python3 episodes/messi_papier/messi_papier.py output/messi_papier --prep
  python3 episodes/messi_papier/messi_papier.py output/messi_papier --stills [2,3]
  python3 episodes/messi_papier/messi_papier.py output/messi_papier --cover
  python3 episodes/messi_papier/messi_papier.py output/messi_papier
"""
import sys, os, math, random, glob
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.environ.setdefault("PARALLAX_CACHE", "/tmp/messi_papier_cache")
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "messi_adieu"))
import messi_adieu as M          # voix, alignement, labels
from story import *
from parallax import prep_layers, prep_clip, still, clip, cuts, light_leak, motes, grade, post_fx
from quiz import like_button, sub_button
from PIL import Image, ImageDraw
import numpy as np
import engine, story
engine.boil = lambda f: 0; story.boil = lambda f: 0          # animation fluide : les étiquettes ne tremblent pas

TITLE = "~/légendes $ ./merci_leo_papier"
SLUG = "messi_papier"
VOICE, SFX_DIR, TEXTS, w = M.VOICE, M.SFX_DIR, M.TEXTS, M.w
CIEL, BLANC, GOLD, NOIR, RED, INK = M.CIEL, M.BLANC, M.GOLD, M.NOIR, M.RED, M.INK
WARM, COLD, FLOOD = (255, 196, 120), (150, 190, 255), (255, 246, 222)
IMG, CUT, CLIPS = (os.path.join(HERE, d) for d in ("img", "cut", "clips"))

def prep():
    for f in sorted(glob.glob(os.path.join(CUT, "p*.png"))):
        k = os.path.basename(f)[:3]; prep_layers(k, os.path.join(IMG, f"{k}.png"), f)
    for f in sorted(glob.glob(os.path.join(CLIPS, "p*.mp4"))):
        prep_clip(os.path.basename(f)[:3], f)

# ------------------------------------------------------------------ effets
def rain(cv, t, a=1.0, n=90, seed=3):
    """Pluie fine en papier (traits clairs qui tombent en biais, devant le personnage)."""
    L = Image.new("RGBA", cv.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L); rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(-100, W + 100); sp = rnd.uniform(1500, 2300); ln = rnd.uniform(26, 60)
        y = (rnd.uniform(0, H) + t*sp) % (H + 120) - 60; x += (y/H)*-70
        d.line([(x, y), (x - ln*.18, y - ln)], fill=(220, 228, 240, int(rnd.uniform(70, 150)*a)), width=2)
    cv.paste(L, (0, 0), L)

def flicker(t, base=.5, amp=.18, f=7.0, seed=0):
    return base + amp*(.6*math.sin(t*f + seed) + .4*math.sin(t*f*2.3 + seed*3))

def burst(cv, fr, key, t, cols=(CIEL, BLANC, GOLD), n=90, dur=3.5):
    confetti(cv, fr, key, t, n, dur, list(cols))

def gray_mix(cv, a):
    """Noir et blanc progressif (a = 1 : tout gris)."""
    if a > .01: grade(cv, sat=1 - clamp(a))

ZERO = lambda tl, u: (0, 0, 1.0, None)

# ------------------------------------------------------------------ étiquettes
K1a, K1b = M.K1a, M.K1b; T1a = TAG("en sélection · 2005-2026", "pt1a", PAL["paper"], size=66)      # « 21 ANS » seul se lit comme son âge
K2a = KW("2005", "pk2a", INK, size=150); T2a = TAG("1er match · Hongrie - Argentine", "pt2a", PAL["paper"], size=62)
K2b = STAMP("CARTON ROUGE !", "pk2b", RED, 104); K2c = KW("IL SORT EN LARMES", "pk2c", PAL["paper"], NOIR, 84)
K3a = KW("2006", "pk3a", INK, size=150); K3b = STAMP("18 ANS", "pk3b", CIEL, 120, NOIR)
T3a = TAG("1er but en Coupe du monde", "pt3a", GOLD, size=74)
K4a = KW("3 FINALES PERDUES", "pk4a", INK, size=92)
Y4 = [STAMP(str(y), f"pk4y{y}", RED, 74) for y in (2014, 2015, 2016)]
K4b = KW("2016", "pk4b", INK, size=150); K4c = STAMP("RATÉ", "pk4c", RED, 150)
K4d = KW("IL QUITTE LA SÉLECTION", "pk4d", BLANC, NOIR, 78); K4e = KW("… AVANT DE REVENIR !", "pk4e", CIEL, NOIR, 88)
K5a = KW("2021", "pk5a", INK, size=150); K5b = STAMP("COPA AMÉRICA", "pk5b", CIEL, 112, NOIR)
K5c = KW("2022 · QATAR", "pk5c", GOLD, NOIR, 110)
K6a = KW("2026", "pk6a", INK, size=150); T6a = TAG("dernière finale", "pt6a", PAL["paper"], size=66)
K6b = STAMP("PERDUE", "pk6b", RED, 130); K6c = M.K6b; K6d = M.K6c
K7a, T7a, K7b = M.K7a, M.T7a, M.K7b
K8b, K8c = M.K8b, M.K8c; T8a = TAG("Ton plus beau souvenir de Messi ?", "pt8a", GOLD, size=68)

def timer(cv, fr, t, t0, t1, x, y):
    sec = int(47*prog(t, t0, t1 - t0))
    LBL(f"0:{sec:02d}", "ptimer", font("title", 120), (255, 70, 60), (24, 22, 26), padx=32, pady=4, rough=2).draw(cv, fr, x, y, pop_in(t, t0, .25), 3)

# ------------------------------------------------------------------ SCÈNE 1 — 21 ans… Messi dit adieu
def s1(cv, fr, t, T):
    b = w(1, "Lionel") - .1
    p02 = clip("p02", 0, b, speed=1.25)
    p01 = still("p01", b, T, c=(CX, 620), z=(1.05, 1.14), pan=((0, 6), (0, -8)),
                fx=lambda c, f, tl, u: light_leak(c, 120, 260, 520, FLOOD, flicker(tl, .35, .1)),
                post=lambda c, f, tl, u: (motes(c, tl, 22, 1, (255, 236, 200), a=.75), light_leak(c, 980, 1500, 600, WARM, .22)))
    cuts(cv, fr, t, [(0, p02), (b, p01)], [("flash", .32)])
    show_stamp(cv, fr, K1a, t, w(1, "Vingt") - .05, CX, 400, -4, t_out=b - .25)
    show(cv, fr, T1a, t, w(1, "ans") - .2, b - .2, CX, 530, 2)
    kw(cv, fr, K1b, t, w(1, "Plus") - .05, b - .2, CX, 680, 3)
    ransom_line(cv, "MESSI DIT ADIEU", 1290, 112, seed=3, fr=fr, scale=pop_in(t, w(1, "Messi") - .1, .3))
    ransom_line(cv, "À L'ARGENTINE", 1440, 100, seed=5, fr=fr, scale=pop_in(t, w(1, "l'Argentine") - .1, .3))
    impact(cv, t, w(1, "Vingt"), 12); impact(cv, t, w(1, "Plus"), 8)

# ------------------------------------------------------------------ SCÈNE 2 — 2005 : entrée, carton rouge après 47 s, larmes
def s2(cv, fr, t, T):
    b1, b2 = w(2, "prend") - .1, w(2, "Il", 2) - .1
    p03 = still("p03", 0, b1, c=(480, 760), z=(1.03, 1.09), pan=((14, 0), (-10, -6)), par=.35,
                fx=lambda c, f, tl, u: light_leak(c, 280, 180, 460, FLOOD, flicker(tl, .4, .12)))
    p04 = clip("p04", b1, b2, z=(1.0, 1.03), c=(CX, 600),
               post=lambda c, f, tl, u: grade(c, warm=-.08) if tl < 0 else None)
    p05 = still("p05", b2, T, c=(430, 640), z=(1.07, 1.01), pan=((0, -10), (0, 6)), par=.3,
                fx=lambda c, f, tl, u: light_leak(c, 800, 520, 560, COLD, flicker(tl, .45, .08, 3)),
                post=lambda c, f, tl, u: (grade(c, sat=.72, warm=-.18), motes(c, tl, 16, 5, (210, 225, 255), area=(380, 250, 1080, 1400), a=.6)))
    cuts(cv, fr, t, [(0, p03), (b1, p04), (b2, p05)], [("whip", .22), ("fade", .3)])
    kw(cv, fr, K2a, t, .03, b1 - .15, 300, 360, -3)
    show(cv, fr, T2a, t, w(2, "premier") - .05, b1 - .15, CX, 1480, 2)
    if b1 - .1 < t < b2 - .1: timer(cv, fr, t, b1, w(2, "secondes", end=True), 820, 470)
    show_stamp(cv, fr, K2b, t, w(2, "rouge") - .05, CX, 1330, -5, t_out=b2 - .15)
    if w(2, "rouge") < t < b2: tint(cv, .14*(1 - prog(t, w(2, "rouge"), .7)), (220, 20, 30))
    kw(cv, fr, K2c, t, w(2, "sort") - .1, None, CX, 230, -2)
    impact(cv, t, w(2, "rouge"), 20); flashes(cv, t, w(2, "rouge"), .1, .45)

# ------------------------------------------------------------------ SCÈNE 3 — 2006 : 18 ans, 1er but en Coupe du monde
def s3(cv, fr, t, T):
    tb = w(3, "but")
    p06 = still("p06", 0, tb, c=(560, 900), z=(1.12, 1.03), pan=((-12, 8), (8, -6)), par=.3,
                fx=lambda c, f, tl, u: light_leak(c, 1000, 160, 640, WARM, .45 + .1*math.sin(tl*3)),
                post=lambda c, f, tl, u: motes(c, tl, 18, 9, (255, 220, 170), a=.6))
    p07 = clip("p07", tb, T + .5, z=(1.0, 1.05), c=(700, 900),
               post=lambda c, f, tl, u: (camera_flashes(c, f, "pf7", tl, 1.4, 8, (60, 300, 1020, 1200)), burst(c, f, "pc7", tl, n=70)))
    cuts(cv, fr, t, [(0, p06), (tb, p07)], [("flash", .2)])
    kw(cv, fr, K3a, t, .03, tb - .15, CX, 250, -3)
    show_stamp(cv, fr, K3b, t, w(3, "dix-huit") - .05, 290, 470, 6, t_out=tb - .15)
    show(cv, fr, T3a, t, w(3, "Coupe") - .1, None, CX, 300, -2)
    impact(cv, t, tb, 18); punch(cv, t, tb, 1.06)

# ------------------------------------------------------------------ SCÈNE 4 — 3 finales perdues, penalty raté, retraite… retour
def s4(cv, fr, t, T):
    b1, b2, b3 = w(4, "En", 2) - .1, w(4, "quitte") - .1, w(4, "Avant") - .1
    p08 = still("p08", 0, b1, c=(620, 640), z=(1.02, 1.09), pan=((0, 0), (0, -8)), par=.35,
                post=lambda c, f, tl, u: (grade(c, sat=.7, warm=-.15), rain(c, tl, .9)))
    p09 = clip("p09", b1, b2, t_start=.15, z=(1.0, 1.04), c=(CX, 700), post=lambda c, f, tl, u: grade(c, sat=.85, warm=-.08))
    p10 = still("p10", b2, b3, c=(470, 600), z=(1.08, 1.03), par=.3, post=lambda c, f, tl, u: gray_mix(c, 1))
    p11 = still("p11", b3, T, c=(560, 560), z=(1.0, 1.08), pan=((0, 0), (0, 6)),
                fx=lambda c, f, tl, u: light_leak(c, 1000, 220, 700, WARM, prog(tl, .1, .6)*.55),
                post=lambda c, f, tl, u: gray_mix(c, 1 - ease_out_cubic(prog(tl, .05, .7))))
    cuts(cv, fr, t, [(0, p08), (b1, p09), (b2, p10), (b3, p11)], [("whip", .22), ("fade", .3), ("flash", .3)])
    kw(cv, fr, K4a, t, w(4, "trois") - .05, b1 - .15, CX, 220, -2)
    for k, tt in enumerate((w(4, "finales"), w(4, "perdues"), w(4, "trois", 2))):
        show_stamp(cv, fr, Y4[k], t, tt - .05, 180, 800 + 150*k, (-7, 5, -4)[k], t_out=b1 - .15)
    kw(cv, fr, K4b, t, w(4, "deux") - .05, b2 - .15, CX, 260, -3)
    show_stamp(cv, fr, K4c, t, w(4, "penalty") - .05, CX, 1380, -8, t_out=b2 - .1)
    kw(cv, fr, K4d, t, w(4, "quitte") - .05, b3 - .12, CX, 1430, 2)
    kw(cv, fr, K4e, t, w(4, "Avant") - .05, None, CX, 1440, -2)
    impact(cv, t, w(4, "perdues"), 8); impact(cv, t, w(4, "penalty"), 14); punch(cv, t, b3, 1.05)

# ------------------------------------------------------------------ SCÈNE 5 — Copa América 2021, champion du monde 2022
def s5(cv, fr, t, T):
    b1, b2 = w(5, "Et", 2) - .1, w(5, "champion") - .1
    toss = lambda tl, u: (0, 16*(.5 - .5*math.cos(2*math.pi*tl/.95)), 1.0, None)       # porté en l'air : ça rebondit
    p12 = still("p12", 0, b1, c=(CX, 640), z=(1.03, 1.09), pan=((0, 8), (0, -6)), move=toss,
                fx=lambda c, f, tl, u: light_leak(c, 300, 300, 520, WARM, flicker(tl, .45, .2, 9)),
                post=lambda c, f, tl, u: burst(c, f, "pc12", tl - (w(5, "Copa") - .1), n=80))
    rise = lambda tl, u: (0, 0, 1 + .035*ease_out_cubic(clamp(u)), (CX, H))               # il soulève la coupe
    p13 = still("p13", b1, b2, c=(CX, 520), z=(1.0, 1.07), move=rise,
                fx=lambda c, f, tl, u: light_leak(c, CX, 160, 760, (255, 214, 120), .5 + .15*math.sin(tl*4)),
                post=lambda c, f, tl, u: (motes(c, tl, 26, 13, (255, 222, 140), a=.85), grade(c, warm=.12)))
    p14 = still("p14", b2, T, c=(560, 640), z=(1.04, 1.14),
                fx=lambda c, f, tl, u: (light_leak(c, 900, 300, 700, WARM, .45), camera_flashes(c, f, "pf14", tl, 1.2, 7, (40, 150, 1040, 900))),
                post=lambda c, f, tl, u: burst(c, f, "pc14", tl, (GOLD, BLANC, CIEL), 110))
    cuts(cv, fr, t, [(0, p12), (b1, p13), (b2, p14)], [("whip", .22), ("flash", .26)])
    kw(cv, fr, K5a, t, .03, b1 - .15, 260, 330, -3)
    show_stamp(cv, fr, K5b, t, w(5, "Copa") - .05, CX, 1400, -4, t_out=b1 - .3)
    kw(cv, fr, K5c, t, w(5, "deux", 2) - .05, b2 - .12, CX, 1440, 2)
    ransom_line(cv, "CHAMPION", 1260, 130, seed=22, fr=fr, scale=pop_in(t, w(5, "champion") - .08, .3))
    ransom_line(cv, "DU MONDE !", 1420, 120, seed=23, fr=fr, scale=pop_in(t, w(5, "monde") - .08, .3))
    impact(cv, t, w(5, "Copa"), 10); impact(cv, t, w(5, "champion"), 18); flashes(cv, t, w(5, "champion"), .12, .5)

# ------------------------------------------------------------------ SCÈNE 6 — 2026 : finale perdue, « tout donné pour ce maillot »
def s6(cv, fr, t, T):
    b1 = w(6, "Puis") - .1
    p15 = still("p15", 0, b1, c=(420, 560), z=(1.03, 1.09), pan=((10, 0), (-6, 0)), par=.35,
                post=lambda c, f, tl, u: (burst(c, f, "pc15", tl + .8, ((206, 30, 44), (250, 200, 40)), 60, 4), grade(c, sat=.85, warm=-.06)))
    p16 = still("p16", b1, T, c=(CX, 760), z=(1.03, 1.10), pan=((0, 6), (0, -26)),
                fx=lambda c, f, tl, u: light_leak(c, 120, 900, 640, WARM, .3 + .1*math.sin(tl*2)),
                post=lambda c, f, tl, u: motes(c, tl, 20, 17, (255, 230, 190), a=.6))
    cuts(cv, fr, t, [(0, p15), (b1, p16)], [("fade", .35)])
    kw(cv, fr, K6a, t, .03, b1 - .15, 800, 300, 3)
    show(cv, fr, T6a, t, w(6, "dernière") - .05, b1 - .15, 800, 450, -2)
    show_stamp(cv, fr, K6b, t, w(6, "perdue") - .05, CX, 1330, -6, t_out=b1 - .1)
    show(cv, fr, M.NOTIF, t, w(6, "message") - .15, w(6, "toujours") - .2, CX, 250, -1)
    kw(cv, fr, K6c, t, w(6, "toujours") - .1, None, CX, 1330, -2)
    kw(cv, fr, K6d, t, w(6, "pour") - .05, None, CX, 1480, 2)
    impact(cv, t, w(6, "perdue"), 10)

# ------------------------------------------------------------------ SCÈNE 7 — 6 octobre, Monumental : dernier match
def s7(cv, fr, t, T):
    b1 = w(7, "son") - .1
    walk = lambda tl, u: (0, 3*abs(math.sin(tl*math.pi*1.7)), 1 - .028*clamp(u), (470, H))   # il s'éloigne vers la pelouse
    p17 = still("p17", 0, b1, c=(CX, 1000), z=(1.0, 1.08), move=walk, par=.55,
                fx=lambda c, f, tl, u: (light_leak(c, 250, 120, 520, FLOOD, flicker(tl, .45, .15, 6)), light_leak(c, 840, 120, 520, FLOOD, flicker(tl, .45, .15, 6, 2)),
                                        camera_flashes(c, f, "pf17", tl, 2.4, 14, (40, 200, 1040, 760))))
    p18 = still("p18", b1, T, c=(CX, 640), z=(1.03, 1.09), pan=((-8, 0), (8, 0)),
                fx=lambda c, f, tl, u: camera_flashes(c, f, "pf18", tl, 2.4, 14, (40, 250, 1040, 1000)),
                post=lambda c, f, tl, u: motes(c, tl, 20, 21, (255, 240, 210), a=.6))
    cuts(cv, fr, t, [(0, p17), (b1, p18)], [("whip", .22)])
    kw(cv, fr, K7a, t, w(7, "Six") - .05, b1 - .15, CX, 250, -2)
    show(cv, fr, T7a, t, w(7, "Monumental") - .05, b1 - .15, CX, 410, 2)
    show_stamp(cv, fr, K7b, t, w(7, "dernier") - .05, CX, 1420, -5)
    impact(cv, t, w(7, "dernier"), 10)

# ------------------------------------------------------------------ SCÈNE 8 — merci Leo, commente, abonne-toi
def s8(cv, fr, t, T):
    b1 = w(8, "Dis-le") - .1
    tc, ta = w(8, "commentaire"), w(8, "abonne-toi")
    p19 = still("p19", 0, b1, c=(CX, 620), z=(1.02, 1.08),
                fx=lambda c, f, tl, u: light_leak(c, 900, 260, 760, (255, 210, 130), .45 + .12*math.sin(tl*2.5)),
                post=lambda c, f, tl, u: (motes(c, tl, 26, 25, (255, 222, 150), a=.85), grade(c, warm=.1)))
    p20 = clip("p20", b1, T + .5, z=(1.02, 1.06), post=lambda c, f, tl, u: tint(c, .28, (8, 10, 24)))
    cuts(cv, fr, t, [(0, p19), (b1, p20)], [("whip", .22)])
    ransom_line(cv, "MERCI LEO", 200, 150, seed=8, fr=fr, scale=pop_in(t, w(8, "Merci") - .1, .3) if t < b1 - .1 else 0)
    show(cv, fr, T8a, t, w(8, "Ton") - .05, b1 - .15, CX, 1470, -2)
    kw(cv, fr, K8b, t, b1 - .1, None, CX, 330, -2)
    kw(cv, fr, K8c, t, b1 + .05, None, CX, 500, 3)
    like_button(cv, fr, CX, 880, .8*pop_in(t, tc - .1, .3), t, tc)      # empilés au centre : rien sous les icônes TikTok (x > 940)
    sub_button(cv, fr, CX, 1210, t, ta - .1, ta + .25)
    ransom_line(cv, "MERCI LEO", 1420, 96, seed=8, fr=fr, scale=pop_in(t, ta + .3, .3))
    burst(cv, fr, "pc8", t - ta, n=90, dur=4)
    impact(cv, t, w(8, "Merci"), 8)

# ------------------------------------------------------------------ scènes + bruitages
def SC(name, n, fn, sfx, trans=None, trans_dur=.25, pad_out=.25):
    sc = Scene(name, TEXTS[n-1], fn, sfx, pad_in=M.PAD, pad_out=pad_out, trans=trans, trans_dur=trans_dur)
    sc.post = lambda cv, f, t, T: post_fx(cv, f)
    return sc
W_ = w
SCENES = [
    SC("21ans", 1, s1, [(.0, "boom", .8), (.0, "crowd_long", .8), (.05, "riser", .4), (W_(1, "Vingt"), "stamp", .8), (W_(1, "Plus"), "stamp", .6),
                        (W_(1, "Lionel") - .15, "flash", .6), (W_(1, "Lionel") - .1, "heart", .7), (W_(1, "adieu"), "sparkle", .6)]),
    SC("2005", 2, s2, [(.0, "crowd", .6), (.03, "stamp", .6), (W_(2, "match"), "pop"), (W_(2, "prend") - .15, "whoosh", .5), (W_(2, "prend"), "tictac", .7),
                       (W_(2, "carton"), "whistle", .9), (W_(2, "rouge"), "stamp", .9), (W_(2, "rouge"), "gasp", .7),
                       (W_(2, "Il", 2) - .1, "whoosh", .3), (W_(2, "larmes"), "groan", .5)], trans="punch", trans_dur=.3),
    SC("2006", 3, s3, [(.03, "stamp", .6), (W_(3, "dix-huit"), "stamp", .7), (W_(3, "but") - .5, "kick", .8), (W_(3, "but"), "boom", .8),
                       (W_(3, "but"), "crowd_long", 1.0), (W_(3, "but"), "flash", .5), (W_(3, "Coupe"), "sparkle", .6)], trans="whip"),
    SC("finales", 4, s4, [(.0, "rip", .6), (W_(4, "trois"), "stamp", .5), (W_(4, "finales"), "stamp", .6), (W_(4, "perdues"), "stamp", .7), (W_(4, "trois", 2), "stamp", .6),
                          (W_(4, "En", 2) - .1, "whoosh", .5), (W_(4, "rate") - .2, "kick", .8), (W_(4, "penalty"), "stamp", .8), (W_(4, "penalty"), "groan", .6),
                          (W_(4, "quitte"), "boom", .5), (W_(4, "Avant") - .15, "flash", .5), (W_(4, "Avant") - .1, "riser", .5), (W_(4, "revenir"), "crowd", .7)],
       trans="tear_h", trans_dur=.5),
    SC("titres", 5, s5, [(.0, "boom", .7), (.03, "stamp", .6), (W_(5, "Copa"), "stamp", .8), (W_(5, "Copa"), "crowd_long", .9), (W_(5, "Copa") + .2, "horn", .5),
                         (W_(5, "Et", 2) - .1, "whoosh", .5), (W_(5, "deux", 2), "stamp", .6), (W_(5, "Qatar"), "riser", .5),
                         (W_(5, "champion") - .1, "flash", .5), (W_(5, "champion"), "boom", .9), (W_(5, "champion"), "crowd_long", 1.0), (W_(5, "champion"), "sparkle", .8)],
       trans="punch", trans_dur=.3),
    SC("2026", 6, s6, [(.0, "whistle", .7), (.03, "stamp", .6), (W_(6, "perdue"), "stamp", .7), (W_(6, "perdue"), "groan", .6),
                       (W_(6, "Puis") - .1, "whoosh", .3), (W_(6, "message"), "notif", .8), (W_(6, "toujours"), "heart", .7), (W_(6, "maillot"), "sparkle", .6)],
       trans="tear_d", trans_dur=.5),
    SC("monumental", 7, s7, [(.0, "crowd_long", 1.0), (W_(7, "Six"), "stamp", .6), (W_(7, "Monumental"), "pop"), (W_(7, "son") - .15, "whoosh", .4),
                             (W_(7, "dernier"), "stamp", .9), (W_(7, "dernier"), "flash", .6), (W_(7, "dernier") + .1, "crowd_long", .9)], trans="whip"),
    SC("merci", 8, s8, [(.0, "sparkle", .6), (W_(8, "Merci"), "stamp", .7), (W_(8, "Merci"), "heart", .6), (W_(8, "Dis-le") - .1, "whoosh", .5),
                        (W_(8, "Dis-le"), "pop2"), (W_(8, "commentaire"), "pop"), (W_(8, "commentaire") + .05, "notif"),
                        (W_(8, "abonne-toi"), "pop2"), (W_(8, "abonne-toi") + .25, "notif"), (W_(8, "abonne-toi") + .2, "crowd_long", .8)],
       trans="punch", trans_dur=.3, pad_out=1.3),
]

# ------------------------------------------------------------------ couverture
def cover(path):
    prep()
    cv = Image.new("RGB", (W, H)); still("p01", 0, 1, c=(CX, 620), z=(1.06, 1.06))(cv, 0, .5)
    light_leak(cv, 120, 260, 520, FLOOD, .4); motes(cv, .8, 22, 1, (255, 236, 200), a=.8)
    ransom_line(cv, "ADIEU LEO", 1200, 150, seed=11, fr=0)
    Label("21 ANS AVEC L'ARGENTINE…", "pcv2", font("title", 70), NOIR, BLANC, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 1370, 1, -2)
    Label("LE PLUS GRAND DE L'HISTOIRE ?", "pcv3", font("title", 70), NOIR, GOLD, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 1500, 1, 2)
    post_fx(cv, 0); cv.save(path, quality=94); return path

def stills(out, fracs=(.05, .18, .32, .46, .6, .74, .88, .98), only=None):
    prep(); scene_timing(SCENES, VOICE); starts = np.cumsum([0]+[sc.T for sc in SCENES])
    os.makedirs(out, exist_ok=True); sheets = []
    for i, sc in enumerate(SCENES):
        if only and (i+1) not in only: continue
        prev = engine._last_frame(SCENES, i-1, starts, TITLE) if (i > 0 and sc.trans) else None
        ims = []
        for fr_ in fracs:
            t = fr_*sc.T; f = int((starts[i]+t)*FPS)
            cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T)
            if prev is not None and t < sc.trans_dur: engine.TRANSITIONS[sc.trans](cv, prev, t, sc.trans_dur, i)
            sc.post(cv, f, t, sc.T); ims.append(cv.resize((300, 533)))
        sheet = Image.new("RGB", (300*len(ims), 575), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            sheet.paste(im, (k*300, 42)); dd.text((k*300+8, 6), f"S{i+1} {fracs[k]*sc.T:.1f}/{sc.T:.1f}", font=font("mono", 24), fill=(230, 230, 230))
        p = os.path.join(out, f"pp_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", "messi_papier")
    os.makedirs(out, exist_ok=True)
    if "--prep" in args: prep(); sys.exit()
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/messi_papier_stills"), only=only)); sys.exit()
    prep()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=21, limit=True))
