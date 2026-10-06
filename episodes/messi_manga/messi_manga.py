"""Hommage Messi, version « MANGA EN PAPIER » (~43 s) : mêmes voix et mêmes moments que messi_adieu, rendu entièrement différent.
Création originale : nos propres dessins papier (engine/portrait.py, foot.py) passés au filtre manga (engine/manga.py) :
encrage, trames, couleurs d'accent (bleu ciel, or, rouge), cases qui découpent l'écran et glissent, caméra dans chaque case,
lignes de concentration et de vitesse, images d'impact, onomatopées géantes, transitions à l'encre, animation fluide (pas de tremblement).

  python3 episodes/messi_manga/messi_manga.py output/messi_manga --stills [2,3]
  python3 episodes/messi_manga/messi_manga.py output/messi_manga --cover
  python3 episodes/messi_manga/messi_manga.py output/messi_manga
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "messi_adieu"))
import messi_adieu as M          # personnages, stades, voix, alignement
from manga import *
from story import Scene, scene_timing, render_episode, draw_goal, draw_ball, WC_TROPHY, CUP, stage_fill, rays, confetti, show_stamp
from quiz import like_button, sub_button
import engine, story
engine.boil = lambda f: 0; story.boil = lambda f: 0          # animation fluide : pas de « boil » image par image
engine.TRANSITIONS["ink"] = lambda cv, prev, t, d, i: ink_transition(cv, prev, t/d)

TITLE = "~/légendes $ ./merci_leo_manga"
SLUG = "messi_manga"
VOICE, SFX_DIR, TEXTS, w = M.VOICE, M.SFX_DIR, M.TEXTS, M.w
SAFE = 1500

# ------------------------------------------------------------------ contenus des cases (plein cadre, avant filtre)
_gr = {}
def grad(c, top, bottom):
    k = (top, bottom)
    if k not in _gr:
        g = Image.new("RGB", (1, 64))
        for i in range(64): g.putpixel((0, i), tuple(int(lerp(a, b, i/63)) for a, b in zip(top, bottom)))
        _gr[k] = g.resize((W, H), Image.BILINEAR)
    c.paste(_gr[k], (0, 0))

DARK, MIDG, LIGHT = ((34, 34, 44), (150, 150, 158)), ((90, 90, 100), (196, 196, 200)), ((236, 234, 226), (186, 186, 190))
FY, FS = 960, 1.3                     # position / échelle des visages dans leurs cases
EYES = FY - 8*FS

def face(P, mood="neutral", tone=DARK, tears=None, hand=None, tilt=0.0, look=(0, 0), extra=None):
    def fn(c, fr, t):
        grad(c, *tone)
        if extra: extra(c, fr, t)
        m = mood(t) if callable(mood) else mood
        P.draw(c, fr, CX, FY, FS, mood=m, t=t, tears=(t - tears) if (tears is not None and t > tears) else 0,
               hand=hand(t) if callable(hand) else (hand or 0), tilt=tilt, look=look)
    return fn

def crowd(key, blur=0, extra=None):
    def fn(c, fr, t):
        M.bg(c, key, t, blur=blur)
        if extra: extra(c, fr, t)
    return fn

def fl(cx, cy, rx, ry, n=130, seed=0, a=1.0):
    return lambda img, t: focus_lines(img, cx, cy, rx, ry, int(t*24), n=n, seed=seed, a=a)

def slant(y0, y1, d=40, x0=0, x1=W):      # case aux bords haut/bas inclinés
    return [(x0, y0 + d), (x1, y0 - d), (x1, y1 - d), (x0, y1 + d)]

def strip(y0, y1): return (0, y0, W, y1)

def beats(cv, fr, t, plan):
    """plan = [(t0, fn)] : chaque temps fort redessine la page ; le précédent reste dessous pendant que le suivant glisse."""
    k = max(i for i, (t0, _) in enumerate(plan) if t >= t0 or i == 0)
    if k > 0 and t < plan[k][0] + .3: plan[k-1][1](cv, fr, t)
    plan[k][1](cv, fr, t)

def flash(cv, t, t0, dur=.12):
    if t0 <= t < t0 + dur: engine.flash(cv, .85*(1 - (t - t0)/dur))

def impact(cv, t, t0, frames=3):
    if t0 <= t < t0 + frames/FPS: impact_frame(cv)

def shake(cv, t, t0, amp=18, dur=.25):
    if t0 <= t < t0 + dur: engine.shake(cv, t, amp*(1 - (t - t0)/dur))

# ------------------------------------------------------------------ SCÈNE 1 — 21 ans : trois regards, la foule, l'adieu
def s1(cv, fr, t, T):
    tP, tL = w(1, "Plus") - .1, w(1, "Lionel") - .1
    def A(cv, fr, t):
        page(cv)
        for k, (P, m, yr) in enumerate(((M.YOUNG, "neutral", "2005"), (M.MID, "determined", "2016"), (M.OLD, "emotional", "2026"))):
            y0 = 340 + k*386
            panel(cv, fr, t, strip(y0, y0 + 370), face(P, m, LIGHT), cam=(CX + 20*(t - k*.2), EYES, 2.1 + .05*t),
                  enter=(k*.22, -W if k % 2 == 0 else W, 0))
            caption(cv, yr, 120, y0 + 52, t, k*.22 + .2, 46, dark=True)
        caption(cv, "21 ANS", CX, 250, t, w(1, "Vingt") - .05, 92, dark=True)
    def B(cv, fr, t):
        page(cv)
        panel(cv, fr, t, (0, 0, W, H), crowd("arg"), cam=(380 + 160*prog(t, tP, 1.2), 900, 1.25 - .15*prog(t, tP, 1.2)), border=0,
              enter=(tP, 0, H), post=fl(CX, 1000, 300, 260, 110, 1))
        n = int(200*ease_out_cubic(prog(t, tP + .1, .7)))
        ono(cv, f"{n}" if n < 200 else "200+", CX, 900, t, tP + .1, 230, fill=SKY, rot=-6)
        caption(cv, "MATCHS AVEC L'ARGENTINE", CX, 1130, t, tP + .3, 54, dark=True)
    def C(cv, fr, t):
        page(cv)
        z = 1.22 + .1*prog(t, tL, 2.4)
        panel(cv, fr, t, (0, 0, W, H), face(M.OLD, "emotional", DARK, tears=w(1, "adieu"), tilt=-1.5), cam=(CX, 980, z), border=0,
              post=fl(CX, 920, 340, 440, 150, 2))
        caption(cv, "MESSI DIT ADIEU", CX, 300, t, w(1, "Messi") - .1, 80, dark=True)
        caption(cv, "À L'ARGENTINE", CX, 420, t, w(1, "l'Argentine") - .1, 70, colbg=SKY)
        flash(cv, t, tL)
    beats(cv, fr, t, [(0, A), (tP, B), (tL, C)])
    shake(cv, t, w(1, "Vingt"), 10); shake(cv, t, tP + .1, 14)

# ------------------------------------------------------------------ SCÈNE 2 — 2005 : il entre… rouge après 47 secondes… larmes
def s2(cv, fr, t, T):
    tI, tC, tR, tI2 = w(2, "Il") - .1, w(2, "carton") - .1, w(2, "rouge"), w(2, "Il", 2) - .1
    te, tsec = w(2, "entre"), w(2, "secondes", end=True)
    def timer(cv, t, x, y, size=76):
        s = int(47*prog(t, te, tsec - te)); caption(cv, f"0:{s:02d}", x, y, t, te - .05, size, dark=True)
    def A(cv, fr, t):
        page(cv)
        panel(cv, fr, t, slant(300, 900), crowd("bud"), cam=(440 + 80*t, 760, 1.05))
        panel(cv, fr, t, [(0, 956), (590, 916), (590, SAFE), (0, SAFE)], face(M.YOUNG, "determined", MIDG), cam=(CX, FY, 1.05), enter=(.45, -700, 0))
        def sub(c, fr, t):
            M.bg(c, "bud", t, blur=10); M.SUB.draw(c, fr, CX, 1000, 2.6, 4)
        panel(cv, fr, t, [(606, 914), (W, 876), (W, SAFE), (606, SAFE)], sub, cam=(CX, 1000, 1.0), enter=(w(2, "match") - .3, 700, 0))
        caption(cv, "2005 · BUDAPEST", 330, 330, t, .05, 54, dark=True)
        caption(cv, "1er match", 300, 1440, t, w(2, "premier") - .05, 50)
    def B(cv, fr, t):
        page(cv)
        ph = math.sin(t*14)
        panel(cv, fr, t, (0, 0, W, H), face(M.YOUNG, "determined", LIGHT, tilt=-6), cam=(CX - 20*ph, 1000 - 14*abs(ph), 1.3), rot=-8, border=0,
              enter=(tI, W, 0), post=lambda img, t: action_lines(img, 180, int(t*24), 90, seed=4, length=(300, 900)))
        ono(cv, "FWIP !", 760, 640, t, w(2, "entre"), 150, fill=(255, 255, 255), rot=-10)
        timer(cv, t, CX, 330, 96)
    def C(cv, fr, t):
        page(cv)
        def ref(c, fr, t):
            M.bg(c, "bud", t, blur=8)
            M.REF.draw(c, fr, 600, 2300, 1.6, age=1, kit="ref", arms=(8, 170), mood="determined", t=t)
            M.CARD.draw(c, fr, 760, 1110, 2.2, 8)
        panel(cv, fr, t, slant(300, 1060, 50), ref, cam=(680, 1240, 1.0), post=fl(700, 470, 150, 200, 120, 3))
        panel(cv, fr, t, slant(1076, SAFE, 50) , face(M.YOUNG, "surprised", MIDG), cam=(CX, 1000, 1.25), enter=(tR + .2, W, 0))
        ono(cv, "CLAC !", 770, 520, t, tC + .05, 170, fill=REDC, rot=-12)
        caption(cv, "CARTON ROUGE !", CX, 1070, t, tR, 72, colbg=REDC)
        timer(cv, t, 200, 360, 70)
        impact(cv, t, tR)
    def D(cv, fr, t):
        page(cv)
        def post(img, t):
            rain(img, int(t*24), 110, seed=5)
        panel(cv, fr, t, (0, 0, W, H), face(M.YOUNG, "cry", DARK, tears=tI2 - .2, tilt=-4, look=(0, 1)), cam=(CX, 990, 1.18 + .08*prog(t, tI2, 1.5)),
              border=0, dark=.12, post=post)
        caption(cv, "IL SORT EN LARMES", CX, 330, t, w(2, "sort") - .1, 76, dark=True)
    beats(cv, fr, t, [(0, A), (tI, B), (tC, C), (tI2, D)])
    shake(cv, t, tR, 26, .35)

# ------------------------------------------------------------------ SCÈNE 3 — 2006 : 18 ans, 1er but en Coupe du monde
def s3(cv, fr, t, T):
    tb = w(3, "but")
    def A(cv, fr, t):
        page(cv)
        sw = prog(t, tb - .6, .25)
        def kick(c, fr, t):
            M.bg(c, "wc06", t, blur=4)
            M.leo(c, fr, M.PLY, 460, 2000, 1.45, armband=False, age=1, kit="arg", mood="determined", legs=(0, -45*math.sin(sw*math.pi)), arms=(40, 30), t=t, kid_hair=False)
            if t < tb - .45: draw_ball(c, fr, 600, 1990, 1.4, 0)
        panel(cv, fr, t, slant(300, 900), kick, cam=(500, 1450, .8), post=lambda img, t: action_lines(img, 200, int(t*24), 40, seed=6, a=prog(t, tb - .6, .2)))
        def goal(c, fr, t):
            M.bg(c, "wc06", t, blur=2); draw_goal(c, fr, CX, 1400, 900, 500, t=t)
            u = prog(t, tb - .45, .45)
            if u > 0: draw_ball(c, fr, lerp(200, 600, u), lerp(1700, 1220, u), lerp(1.3, .8, u), t*700)
        panel(cv, fr, t, [(0, 956), (W, 876), (W, SAFE), (0, SAFE)], goal, cam=(CX, 1250, 1.0), enter=(w(3, "son") - .25, 0, 700))
        caption(cv, "2006", 160, 330, t, .03, 70, dark=True)
        caption(cv, "18 ANS", 900, 330, t, w(3, "dix-huit") - .05, 70, colbg=SKY)
        caption(cv, "1er but en Coupe du monde", CX, 1440, t, w(3, "premier") - .05, 50)
    def B(cv, fr, t):
        page(cv)
        def net(c, fr, t):
            M.bg(c, "wc06", t, blur=3); draw_goal(c, fr, CX, 1700, 1500, 900, net_u=prog(t, tb, .7), t=t)
            draw_ball(c, fr, 600, 1250 - 18*math.sin(prog(t, tb, .4)*math.pi), 1.5, 0)
        panel(cv, fr, t, (0, 0, W, H), net, cam=(CX, 1200, 1.1), rot=4, border=0, post=fl(560, 1250, 160, 160, 160, 7))
        panel(cv, fr, t, circle_poly(310, 1180, 200), face(M.YOUNG, "cheer", LIGHT), cam=(CX, 1010, 1.0), enter=(tb + .25, 0, 500))
        ono(cv, "BUUUT !", CX, 600, t, tb, 210, fill=SKY, rot=-7)
        caption(cv, "1er but en Coupe du monde", CX, 1440, t, w(3, "premier") - .05, 50)
        flash(cv, t, tb); impact(cv, t, tb, 2)
    beats(cv, fr, t, [(0, A), (tb, B)])
    shake(cv, t, tb, 22, .35)

# ------------------------------------------------------------------ SCÈNE 4 — 3 finales perdues, penalty raté, retraite… retour
def s4(cv, fr, t, T):
    tE, tet, tA = w(4, "En", 2) - .1, w(4, "et") - .1, w(4, "Avant") - .1
    tp = w(4, "rate") - .1
    def A(cv, fr, t):
        page(cv)
        ts = (w(4, "trois"), w(4, "finales"), w(4, "perdues"))
        for k in range(3):
            y0 = 330 + k*384
            def tk(c, fr, t, k=k):
                grad(c, (70, 70, 80), (130, 130, 140)); M.TICKETS[k].draw(c, fr, CX, 960, 1.75, (-3, 2, -2)[k])
                show_stamp(c, fr, M.PERDUE, t, w(4, "perdues") + k*.16, CX + 300, 1050, (-10, -6, -12)[k])
            panel(cv, fr, t, slant(y0, y0 + 366, (14, -14, 14)[k], 30, W - 30), tk, cam=(CX, 960, 1.0), enter=(ts[k] - .15, (-W, W, -W)[k], 0))
        caption(cv, "3 FINALES PERDUES", CX, 250, t, w(4, "Puis") - .05, 76, dark=True)
    def B(cv, fr, t):
        page(cv)
        u = prog(t, tp, 1.0)
        def pen(c, fr, t):
            M.bg(c, "fin16", t, blur=3); draw_goal(c, fr, CX, 1250, 780, 440)
            dv = prog(t, tp + .15, .4)
            M.GK.draw(c, fr, CX + 160*dv, 1260 - 40*math.sin(dv*math.pi), .78, age=1, kit="gk", arms=(60 + 60*dv, 60 + 60*dv), lean=-60*dv, t=t)
            draw_ball(c, fr, lerp(560, 800, u), lerp(1800, 610, u) - 90*math.sin(u*math.pi), lerp(1.7, .45, u), t*800)
        def post(img, t):
            if u <= 0: focus_lines(img, CX, 1000, 380, 300, int(t*24), 90, seed=8)
            else: action_lines(img, -70, int(t*24), 45, seed=9, a=1 - prog(t, tp + .6, .4))
        panel(cv, fr, t, (0, 0, W, H), pen, cam=(CX, 1150, 1.05 + .1*u), rot=5, border=0, post=post)
        caption(cv, "2016", 160, 330, t, tE, 76, dark=True)
        ono(cv, "RATÉ !", CX, 1380, t, w(4, "penalty"), 190, fill=REDC, rot=-8)
    def C(cv, fr, t):
        page(cv)
        panel(cv, fr, t, (0, 0, W, H), face(M.MID, "sad", DARK, tears=tet - .5, tilt=-5, look=(0, 1)), cam=(CX, 980, 1.18), border=0, dark=.15,
              accent=False, post=lambda img, t: rain(img, int(t*24), 120, seed=10))
        caption(cv, "IL QUITTE LA SÉLECTION", CX, 330, t, w(4, "quitte") - .05, 70, dark=True)
    def D(cv, fr, t):
        page(cv)
        panel(cv, fr, t, strip(560, 1000), face(M.MID, "determined", LIGHT), cam=(CX, EYES, 2.25), enter=(tA, 0, 0),
              post=lambda img, t: action_lines(img, 0, int(t*24), 50, seed=11, length=(300, 900)))
        panel(cv, fr, t, strip(1016, SAFE), face(M.MID, "determined", MIDG), cam=(CX, 1040, 1.0), enter=(w(4, "revenir") - .15, 0, 600))
        ono(cv, "SHING !", 780, 470, t, tA + .05, 140, fill=GOLDC, rot=-10)
        caption(cv, "… AVANT DE REVENIR !", CX, 330, t, tA, 66, colbg=SKY)
    beats(cv, fr, t, [(0, A), (tE, B), (tet, C), (tA, D)])
    for k in ("trois", "finales", "perdues"): shake(cv, t, w(4, k), 10, .2)
    shake(cv, t, w(4, "penalty"), 20)

# ------------------------------------------------------------------ SCÈNE 5 — 2021 Copa América, 2022 champion du monde
def s5(cv, fr, t, T):
    tE, tc = w(5, "Et", 2) - .1, w(5, "champion")
    def A(cv, fr, t):
        page(cv)
        def toss(c, fr, t):
            stage_fill(c, fr, (16, 20, 40), "mm5a"); M.fireworks(c, "mmfw", t, cols=(GOLDC, (255, 255, 255), SKY))
            d = ImageDraw.Draw(c)
            for k in range(10): d.rectangle([0, 1300 + k*62, W, 1362 + k*62], fill=(44, 112, 62) if k % 2 == 0 else (40, 100, 56))
            for k, x in enumerate((170, 380, 700, 910)):
                M.TEAM[k].draw(c, fr, x, 1880, .66, age=1, kit="arg", mood="cheer", arms=(165, 165), legs=(10, 10), t=t + k)
            M.trophy_lift(c, fr, M.PLA, CX, 1500 - 260*abs(math.sin(t*3.4)), .7, "arg", t, CUP, beard=True)
        panel(cv, fr, t, slant(300, 1100), toss, cam=(CX, 1260, 1.0))
        panel(cv, fr, t, slant(1116, SAFE, 40), face(M.ADULT, "cheer", LIGHT), cam=(CX, 1010, 1.3), enter=(w(5, "Copa") + .2, W, 0))
        caption(cv, "2021", 160, 330, t, .03, 70, dark=True)
        caption(cv, "COPA AMÉRICA", 700, 330, t, w(5, "Copa") - .05, 70, colbg=SKY)
    def B(cv, fr, t):
        page(cv)
        def lift(c, fr, t):
            stage_fill(c, fr, (40, 26, 10), "mm5b"); rays(c, (CX, 760), t, 1.0, 18, 1600, (236, 186, 70))
            M.trophy_lift(c, fr, M.PLA, CX, 2050, 1.3, "arg", t, WC_TROPHY, beard=True)
        panel(cv, fr, t, (0, 0, W, H), lift, cam=(CX, 1150, 1.0 + .08*prog(t, tE, 1.6)), rot=-4, border=0, enter=(tE, 0, -H),
              post=fl(CX, 820, 200, 260, 120, 12))
        caption(cv, "2022 · QATAR", CX, 330, t, w(5, "deux", 2) - .1, 82, dark=True)
    def C(cv, fr, t):
        page(cv)
        def cheer(c, fr, t):
            stage_fill(c, fr, (40, 26, 10), "mm5c"); rays(c, (CX, 900), t, 1.0, 18, 1600, (236, 186, 70))
            M.ADULT.draw(c, fr, CX, FY, FS, mood="cheer", t=t, tears=t - tc + .3, tilt=2)
            WC_TROPHY.draw(c, fr, 790, 1500, 1.5 + .05*math.sin(t*4), 8)
            confetti(c, fr, "mm5conf", t - tc, 110, 4, [GOLDC, (255, 255, 255), SKY])
        def post(img, t):
            focus_lines(img, CX, 960, 360, 460, int(t*24), 160, seed=13)
            sparkles(img, int(t*24), [(200, 700), (880, 820), (260, 1250), (840, 560)], size=46)
        panel(cv, fr, t, (0, 0, W, H), cheer, cam=(CX, 1000, 1.0), border=0, post=post)
        ono(cv, "CHAMPION", CX, 300, t, tc - .05, 170, fill=GOLDC, rot=-6)
        ono(cv, "DU MONDE !", CX, 470, t, tc + .25, 150, fill=GOLDC, rot=-6)
        impact(cv, t, tc - .05)
    beats(cv, fr, t, [(0, A), (tE, B), (tc - .05, C)])
    shake(cv, t, w(5, "Copa"), 14); shake(cv, t, tc, 26, .4)

# ------------------------------------------------------------------ SCÈNE 6 — 2026 : finale perdue, « tout donné pour ce maillot »
def s6(cv, fr, t, T):
    tPu, tm, tt, tmy = w(6, "Puis") - .1, w(6, "message"), w(6, "toujours"), w(6, "maillot")
    def A(cv, fr, t):
        page(cv)
        def score(c, fr, t):
            M.bg(c, "fin26", t, blur=8, dim=.3); M.score2(c, fr, CX, 900, "ARGENTINE", "ESPAGNE", 0, 1, "finale 2026", 1.15)
        panel(cv, fr, t, slant(300, 860), score, cam=(CX, 900, 1.0))
        def lost(c, fr, t):
            M.bg(c, "fin26", t, blur=4, dim=.2)
            for k, x in enumerate((760, 940)):
                M.ESP[k].draw(c, fr, x, 1840, .72, age=1, kit="spain", mood="cheer", arms=(160, 160), t=t + k*.7)
            M.leo(c, fr, M.PLA, 330, 1860, .95, age=1, kit="arg", beard=True, mood="sad", look=(0, 1), arms=(-6, -6), t=t)
            confetti(c, fr, "mm6", t - w(6, "perdue"), 90, 4, [REDC, GOLDC, REDC])
        panel(cv, fr, t, slant(876, SAFE, 40), lost, cam=(CX, 1420, 1.05), enter=(w(6, "perdue") - .15, 0, 700))
        caption(cv, "2026 · DERNIÈRE FINALE", CX, 250, t, .05, 66, dark=True)
    def B(cv, fr, t):
        page(cv)
        panel(cv, fr, t, (0, 0, W, H), face(M.OLD, "emotional", DARK, tears=tt, hand=lambda t: prog(t, tmy - .5, .6), tilt=-1),
              cam=(CX, 1010, 1.0 + .06*prog(t, tPu, 3.5)), border=0, post=fl(CX, 940, 360, 470, 100, 14, .7))
        if tm - .1 <= t < tt - .1:
            def notif(c, fr, t):
                c.paste((250, 250, 246), (0, 0, W, H)); M.NOTIF.draw(c, fr, CX, 960, 1.15, 0)
            panel(cv, fr, t, (70, 520, W - 70, 760), notif, cam=(CX, 960, 1.0), enter=(tm - .1, 0, -400), filt=False)
        caption(cv, "IL A TOUJOURS TOUT DONNÉ", CX, 300, t, tt - .05, 66, dark=True)
        caption(cv, "POUR CE MAILLOT", CX, 410, t, tmy - .1, 74, colbg=SKY)
    beats(cv, fr, t, [(0, A), (tPu, B)])
    shake(cv, t, w(6, "perdue"), 12)

# ------------------------------------------------------------------ SCÈNE 7 — 6 octobre, Monumental : le dernier match
def s7(cv, fr, t, T):
    ts, td = w(7, "son") - .1, w(7, "dernier")
    def walkers(c, fr, t):
        M.bg(c, "mon", t, blur=0)
        for k, x in enumerate((140, 940)): M.beam(c, (x, 250), [(x - 120 + 300*(k - .5), 1900), (x + 120 + 300*(k - .5), 1900)], .10)
        wk = math.sin(t*7)
        M.leo(c, fr, M.PLA, CX, 1800 + 6*abs(wk), .9, age=1, kit="arg", beard=True, mood="happy" if t > ts else "normal",
              arms=(20, 150 if t > ts else 20 + 10*wk), legs=(10*wk, -10*wk), t=t)
    def A(cv, fr, t):
        page(cv)
        u = prog(t, 0, ts)
        panel(cv, fr, t, (0, 0, W, H), walkers, cam=(380 + 200*ease_io(u), 1050, 1.25 - .2*ease_io(u)), border=0)
        caption(cv, "6 OCTOBRE 2026", CX, 300, t, w(7, "Six") - .05, 80, dark=True)
        caption(cv, "MONUMENTAL · BUENOS AIRES", CX, 410, t, w(7, "Monumental") - .05, 56)
    def B(cv, fr, t):
        page(cv)
        panel(cv, fr, t, (0, 300, 530, 900), crowd("mon"), cam=(300, 800, 1.6), enter=(ts, -600, 0),
              post=lambda img, t: sparkles(img, int(t*24), [(120, 200), (380, 120), (250, 420), (430, 330)], size=30, seed=4))
        panel(cv, fr, t, (546, 300, W, 900), walkers, cam=(CX, 1330, 1.25), enter=(ts + .15, 600, 0))
        panel(cv, fr, t, strip(916, SAFE), face(M.OLD, "smile", LIGHT, look=(-1, -1), tilt=2), cam=(CX, 1000, 1.45), enter=(ts + .3, 0, 600),
              post=fl(W/2, 290, 260, 120, 90, 15))
        ono(cv, "DERNIER MATCH", CX, 250, t, td - .05, 120, fill=SKY, rot=-5)
    beats(cv, fr, t, [(0, A), (ts, B)])
    shake(cv, t, td, 12)

# ------------------------------------------------------------------ SCÈNE 8 — merci Leo, commente, abonne-toi
def s8(cv, fr, t, T):
    tD, tc, ta = w(8, "Dis-le") - .1, w(8, "commentaire"), w(8, "abonne-toi")
    def A(cv, fr, t):
        page(cv)
        def post(img, t):
            focus_lines(img, CX, 950, 380, 500, int(t*24), 80, col=(150, 150, 160), seed=16)
            sparkles(img, int(t*24), [(180, 640), (900, 720), (220, 1300), (860, 1200)], size=40, seed=5)
        panel(cv, fr, t, (0, 0, W, H), face(M.OLD, "proud", LIGHT, hand=1, tilt=1), cam=(CX, 1000, 1.0 + .05*prog(t, 0, 2)), border=0, post=post)
        ono(cv, "MERCI LEO", CX, 330, t, w(8, "Merci") - .1, 190, fill=SKY, rot=-6)
        caption(cv, "Ton plus beau souvenir de Messi ?", CX, 1440, t, w(8, "Ton") - .05, 50, fnt="hand")
    def B(cv, fr, t):
        page(cv)
        panel(cv, fr, t, slant(250, 640, 30), crowd("mon"), cam=(CX + 60*t, 820, 1.1), enter=(tD, 0, -500))
        caption(cv, "TON PLUS BEAU SOUVENIR ?", CX, 730, t, tD + .05, 64, dark=True)
        ono(cv, "COMMENTE !", CX, 900, t, w(8, "Dis-le"), 130, fill=REDC, rot=-5)
        like_button(cv, fr, CX, 1100, .7*pop_in(t, tc - .1, .3), t, tc)      # empilés au centre (icônes TikTok à droite)
        sub_button(cv, fr, CX, 1400, t, ta - .1, ta + .25)
        confetti(cv, fr, "mm8", t - ta, 90, 4, [SKY, (255, 255, 255), GOLDC])
    beats(cv, fr, t, [(0, A), (tD, B)])

# ------------------------------------------------------------------ scènes + bruitages (mêmes temps que la version papier)
def SC(i, fn, trans=None, trans_dur=.3, extra=(), pad_out=.25):
    return Scene(M.SCENES[i].name, TEXTS[i], fn, list(M.SCENES[i].sfx) + list(extra), pad_in=M.PAD, pad_out=pad_out, trans=trans, trans_dur=trans_dur)
W_ = w
SCENES = [
    SC(0, s1, extra=[(.22, "whoosh", .4), (.44, "whoosh", .4), (W_(1, "Plus") - .1, "whoosh", .6)]),
    SC(1, s2, "ink", .45, [(.45, "whoosh", .4), (W_(2, "match") - .3, "whoosh", .4), (W_(2, "Il") - .1, "whoosh", .6), (W_(2, "rouge"), "boom", .7)]),
    SC(2, s3, "punch", .3, [(W_(3, "son") - .25, "whoosh", .5), (W_(3, "but"), "glitch", .4)]),
    SC(3, s4, "ink", .45, [(W_(4, "trois") - .15, "whoosh", .4), (W_(4, "finales") - .15, "whoosh", .4), (W_(4, "perdues") - .15, "whoosh", .4),
                           (W_(4, "Avant") - .1, "laser", .5)]),
    SC(4, s5, "punch", .3, [(W_(5, "Copa") + .2, "whoosh", .4), (W_(5, "Et", 2) - .1, "whoosh", .6), (W_(5, "champion") - .05, "glitch", .4)]),
    SC(5, s6, "ink", .45, [(W_(6, "perdue") - .15, "whoosh", .4), (W_(6, "message") - .1, "whoosh", .4)]),
    SC(6, s7, "whip", .3, [(W_(7, "son") - .1, "whoosh", .5), (W_(7, "son") + .05, "whoosh", .4)]),
    SC(7, s8, "ink", .45, [(W_(8, "Dis-le") - .1, "whoosh", .5)], pad_out=1.3),
]

# ------------------------------------------------------------------ couverture manga
def cover(path):
    cv = Image.new("RGB", (W, H)); page(cv)
    panel(cv, 0, 1.0, (0, 0, W, H), face(M.OLD, "emotional", DARK, tears=0, tilt=-1.5), cam=(CX, 1060, 1.15), border=0,
          post=lambda img, t: (focus_lines(img, CX, 1000, 360, 470, 0, 170, seed=21), M.OLD and None))
    ono(cv, "ADIEU LEO", CX, 330, 1.0, 0, 200, fill=SKY, rot=-6)
    caption(cv, "21 ANS AVEC L'ARGENTINE…", CX, 520, 1.0, 0, 64, dark=True)
    caption(cv, "LE PLUS GRAND DE L'HISTOIRE ?", CX, 1560, 1.0, 0, 60, colbg=GOLDC, maxw=1020)
    cv.save(path, quality=94); return path

def stills(out, fracs=(.05, .18, .32, .46, .6, .74, .88, .98), only=None):
    scene_timing(SCENES, VOICE); starts = np.cumsum([0]+[sc.T for sc in SCENES])
    os.makedirs(out, exist_ok=True); sheets = []
    for i, sc in enumerate(SCENES):
        if only and (i+1) not in only: continue
        prev = engine._last_frame(SCENES, i-1, starts, TITLE) if (i > 0 and sc.trans) else None
        ims = []
        for fr_ in fracs:
            t = fr_*sc.T; f = int((starts[i]+t)*FPS)
            cv = engine.background(f, TITLE); sc.draw_fn(cv, f, t, sc.T)
            if prev is not None and t < sc.trans_dur: engine.TRANSITIONS[sc.trans](cv, prev, t, sc.trans_dur, i)
            engine.finish(cv, TITLE); ims.append(cv.resize((300, 533)))
        sheet = Image.new("RGB", (300*len(ims), 575), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            sheet.paste(im, (k*300, 42)); dd.text((k*300+8, 6), f"S{i+1} {fracs[k]*sc.T:.1f}/{sc.T:.1f}", font=font("mono", 24), fill=(230, 230, 230))
        p = os.path.join(out, f"mg_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", "messi_manga")
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/messi_manga_stills"), only=only)); sys.exit()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=20, limit=True))
