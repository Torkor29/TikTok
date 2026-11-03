"""CONCEPT 3 — storytime « Formé au PSG… il a fini à l'OM » : Adrien Rabiot (≈ 55 s), style Rennes (rstyle) + sous-titres karaoké.
Débuts au PSG à 17 ans (26/08/2012), sa mère agent, réserviste refusé par mail (2018), 6 mois sans jouer, départ libre à la Juve (2019),
l'OM (2024), bagarre dans le vestiaire à Rennes (15/08/2025), vendu au Milan AC. Fin : « traître ou incompris ? ».
Voix : voix/voix.mp3 (une prise, TEXTE) ; sans voix -> minutage estimé. Pas de musique.
  python3 episodes/rabiot/rabiot.py [--stills]"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "episodes", "rennes")); sys.path.insert(0, os.path.join(ROOT, "engine"))
from rstyle import *
import rstyle as R
import karaoke as KA
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))   # (rstyle écrase HERE)
PC.KITS["om"] = dict(c1=(250, 250, 246), sleeve=(250, 250, 246), shorts=(250, 250, 246), socks=(250, 250, 246), trim=(40, 170, 225), kind="band")
PC.KITS["juve"] = dict(c1=(250, 250, 246), sleeve=(250, 250, 246), shorts=(24, 22, 26), socks=(24, 22, 26), trim=(24, 22, 26), kind="band")
PC.KITS["milan"] = dict(c1=(206, 24, 36), sleeve=(206, 24, 36), shorts=(250, 250, 246), socks=(24, 22, 26), trim=(24, 22, 26), kind="band")
PC.KITS["france"] = dict(c1=(24, 40, 110), sleeve=(24, 40, 110), shorts=(250, 250, 246), socks=(206, 30, 40), trim=(250, 250, 246), kind="plain")
SKY = (40, 170, 225)
TITLE = "~/histoires $ ./rabiot"; SLUG = "rabiot"
TEXTE = ["Formé au PSG, il a fini à l'OM. Et ça s'est très mal terminé.",
         "Adrien Rabiot débute au PSG à dix-sept ans. Son agent ? Sa mère, Véronique.",
         "Deux mille dix-huit : il n'est pas retenu pour la Coupe du monde.",
         "On lui propose d'être réserviste. Il refuse, par mail.",
         "Au PSG, il refuse de prolonger. Résultat : six mois sans jouer.",
         "Deux mille dix-neuf : il part libre, à la Juventus. Paris ne touche pas un euro.",
         "Cinq ans plus tard, il revient en France. À Marseille !",
         "Pour Paris, c'est un traître. Pour Marseille, un patron.",
         "Mais en août deux mille vingt-cinq, à Rennes, bagarre dans le vestiaire.",
         "L'OM le met à l'écart, et le vend au Milan AC.",
         "Alors, Rabiot : traître ou incompris ? Dis-le en commentaire !"]
VOIX = os.path.join(HERE, "voix", "voix.mp3")
WD = KA.Words(TEXTE, VOIX, cps=13.5); PROV = not WD.real
def k(i, w, n=1, end=False): return WD.t(i, w, n, end)
L0 = [WD.line(i)[0] - (.12 if i else 0) for i in range(len(TEXTE))]          # début de chaque scène
RAB = foot.Player("rabiot", hair=(150, 110, 70))
def spin_kit(L, fr, x, y, s, t, t0, a, b, **kw):
    """Le joueur pivote sur lui-même et change de maillot (0,35 s)."""
    u = clamp((t - t0)/.35); kit = a if u < .5 else b; sx = abs(math.cos(math.pi*u)) if 0 < u < 1 else 1
    lay = Image.new("RGBA", (900, 1000), (0, 0, 0, 0)); RAB.draw(lay, fr, 450, 940, s=s, kit=kit, t=t, **kw); lay.info["anchor"] = (450, 940)
    blit_sxy(L, lay, x, y, max(.05, sx), 1, 0)
# --- 0. HOOK
E0 = [El(lambda fr: logo("psg", 300), 230, 1120, -.5, L0[1] - .15, "pop", "shrink", rot=-6, idle=.6),
      El(lambda fr: logo("om", 300), 850, 1120, k(0, "OM") - .1, L0[1] - .15, "pop", "shrink", rot=6, idle=.6),
      El(KW("FORMÉ AU PSG", NAVY, BLANC, 104), CX, 430, -.5, L0[1] - .15, "stamp", "fly", rot=-3),
      El(KW("IL A FINI À L'OM", SKY, BLANC, 104), CX, 580, k(0, "fini") - .05, L0[1] - .15, "stamp", "fly", rot=2),
      El(stampl("TRÈS MAL TERMINÉ", ROUGE, 96), CX, 1560, k(0, "mal") - .1, L0[1] - .15, "stamp", "fly", rot=-6)]
@scene(L0[0])
def s0(L, fr, t):
    stripes_bg(L, NAVY, (30, 140, 200), key="h0", t=t); dark(L, .35)
    spin_kit(L, fr, CX, 1420, 1.0, t, k(0, "OM") - .1, "psg", "om", arms=(14, 14), mood="happy")
    M.draw_all(L, fr, t, E0)
CAMS["s0"] = [(0, CX, 960, 1.04), (k(0, "OM"), CX, 1000, 1.08), (k(0, "mal"), CX, 1200, 1.08)]
# --- 1. débuts à 17 ans, sa mère agent
E1 = [El(KW("17 ANS", JAUNE, NOIR, 150), 760, 760, k(1, "dix") - .05, k(1, "agent") - .1, "stamp", "fly", rot=5),
      El(tag("SON AGENT ?", 66, BLANC), CX, 560, k(1, "agent") - .1, None, "pop", rot=-2),
      El(lambda fr: ticket("CONTRAT", "AGENT : SA MÈRE", ROUGE, 600), 700, 1000, k(1, "mère") - .15, None, "drop", rot=6, dist=900),
      El(marker("VÉRONIQUE", "rbvero", 80), 700, 1200, k(1, "Véronique") - .05, None, "slide_l", rot=-3)]
@scene(L0[1], trans="whip", td=.18)
def s1(L, fr, t):
    paper_fill(L, (30, 40, 90), "s1"); rays(L, (CX, 1100), t, .5, 14, 1500, (44, 60, 120), .1, .3)
    RAB.draw(L, fr, 300, 1760, s=1.0, kit="psg", age=.85, arms=(150, 150) if t > k(1, "dix") else (14, 14), mood="happy", t=t)
    M.draw_all(L, fr, t, E1)
CAMS["s1"] = [(L0[1], CX, 1000, 1.0), (k(1, "dix"), 600, 1100, 1.08), (k(1, "mère"), 650, 1050, 1.1)]
# --- 2. 2018 : pas retenu pour la Coupe du monde
E2 = [El(stampl("2018", NOIR, 170), CX, 460, L0[2], None, "stamp", rot=-3),
      El(tag("COUPE DU MONDE", 64, BLANC), CX, 640, k(2, "Coupe") - .1, None, "pop", rot=2),
      El(stampl("PAS RETENU", ROUGE, 120), CX, 1300, k(2, "retenu") - .05, None, "stamp", rot=-8)]
@scene(L0[2], trans="tear", td=.22)
def s2(L, fr, t):
    paper_fill(L, (238, 230, 212), "s2")
    J = foot.jersey_front("france", "rbfra"); J.draw(L, fr, CX, 1020, .9*M.spring(t - L0[2] - .05, .45, 13), 3*math.sin(t*2))
    put(L, logo("fff_bleu", 200), 850, 840, M.spring(t - L0[2] - .2, .45, 13), 8)
    M.draw_all(L, fr, t, E2)
CAMS["s2"] = [(L0[2], CX, 900, 1.0), (k(2, "retenu"), CX, 1150, 1.1)]
# --- 3. réserviste ? il refuse… par mail
def envelope():
    if "env" not in R._sh:
        s_ = pp(rect_pts(420, 270), (250, 248, 240), "env", 1, rough=1.4)
        def f(d, ax, ay): d.line([(ax - 210, ay - 135), (ax, ay + 20), (ax + 210, ay - 135)], fill=(120, 110, 100), width=6); text_c(d, ax, ay + 80, "@", fsans(70), ROUGE)
        R._sh["env"] = deco(s_, f)
    return R._sh["env"]
E3 = [El(tag("RÉSERVISTE ?", 80, JAUNE), CX, 500, k(3, "réserviste") - .1, None, "pop", rot=-3),
      El(stampl("IL REFUSE", ROUGE, 140), CX, 760, k(3, "refuse") - .05, None, "stamp", rot=-6),
      El(KW("PAR MAIL", NOIR, BLANC, 110), CX, 1520, k(3, "mail") - .05, None, "stamp", rot=4)]
@scene(L0[3], trans="whip", td=.18)
def s3(L, fr, t):
    paper_fill(L, (238, 230, 212), "s3")
    tm = k(3, "mail") - .3; u = clamp((t - tm)/.6)
    if t > k(3, "refuse") - .3:
        x = lerp(CX, W + 400, M.ease_in(u)); y = 1150 - 260*math.sin(math.pi*u*.8)
        put(L, envelope(), x, y, M.spring(t - k(3, "refuse") + .3, .45, 13), -8 + 30*u)
        if u > 0: ImageDraw.Draw(L).line([(CX - 200, 1180), (x - 220, y + 20)], fill=(180, 170, 150), width=5)
    M.draw_all(L, fr, t, E3)
CAMS["s3"] = [(L0[3], CX, 900, 1.0), (k(3, "refuse"), CX, 1000, 1.08), (k(3, "mail"), CX, 1300, 1.06)]
def bench_psg():
    """Banc de touche (sans inscription)."""
    if "bench" not in R._sh:
        im = Image.new("RGBA", (640, 300), (0, 0, 0, 0)); cx = 320; d = ImageDraw.Draw(im)
        for sx in (-1, 1): d.rectangle([cx + sx*250 - 9, 60, cx + sx*250 + 9, 280], fill=(70, 72, 80))
        for sp, y in ((pp(rect_pts(580, 70), (20, 36, 82), "bb2", rough=1.0, hatch=True), 70), (pp(rect_pts(600, 50), (34, 56, 120), "bs2", rough=1.0, hatch=True), 190)):
            ax, ay = sp.info["anchor"]; im.alpha_composite(sp, (int(cx - ax), int(y - ay)))
        im.info["anchor"] = (cx, 190); R._sh["bench"] = im
    return R._sh["bench"]
# --- 4. il refuse de prolonger : six mois sans jouer
E4 = [El(lambda fr: ticket("PROLONGATION", "PSG · 2019 →", NAVY, 620), CX, 620, L0[4] + .05, None, "drop", rot=-3, dist=900),
      El(stampl("REFUSÉ", ROUGE, 130), CX, 640, k(4, "prolonger") - .05, None, "stamp", rot=-10)]
@scene(L0[4], trans="tear", td=.22)
def s4(L, fr, t):
    paper_fill(L, (52, 50, 58), "s4"); d = ImageDraw.Draw(L)
    put(L, bench_psg(), CX, 1560, M.spring(t - k(4, "Résultat") + .1, .45, 13))
    if t > k(4, "Résultat"): RAB.draw(L, fr, CX - 120, 1620, s=.9, kit="psg", arms=(-6, -6), mood="sad", t=t)
    if t > k(4, "six") - .1:
        n = min(6, 1 + int((t - k(4, "six") + .1)/.12)); txt = f"{n} MOIS SANS JOUER"
        LBL(txt, f"rbm{n}", font("title", 96), BLANC, ROUGE, padx=26, pady=8, rough=2).draw(L, fr, CX, 1020, 1, -3)
    M.draw_all(L, fr, t, E4)
CAMS["s4"] = [(L0[4], CX, 800, 1.04), (k(4, "prolonger"), CX, 700, 1.1), (k(4, "Résultat"), CX, 1300, 1.04), (k(4, "six"), CX, 1150, 1.08)]
# --- 5. 2019 : libre à la Juventus, Paris ne touche pas un euro
E5 = [El(stampl("LIBRE", (40, 150, 70), 160), CX, 520, k(5, "libre") - .05, None, "stamp", rot=-5),
      El(lambda fr: logo("juventus", 260), 820, 900, k(5, "Juventus") - .1, None, "pop", rot=6),
      El(KW("0 €", JAUNE, NOIR, 170), 280, 900, k(5, "euro") - .3, None, "stamp", rot=-6),
      El(tag("POUR PARIS", 56, BLANC), 280, 1040, k(5, "euro") - .1, None, "pop", rot=3)]
@scene(L0[5], trans="whip", td=.18)
def s5(L, fr, t):
    stripes_bg(L, (250, 250, 246), (24, 22, 26), key="s5", t=t); dark(L, .25)
    spin_kit(L, fr, 620, 1780, 1.0, t, k(5, "Juventus") - .1, "psg", "juve", arms=(20, 20), mood="happy")
    M.draw_all(L, fr, t, E5)
CAMS["s5"] = [(L0[5], CX, 1000, 1.0), (k(5, "libre"), CX, 800, 1.06), (k(5, "Juventus"), 700, 1200, 1.06), (k(5, "euro"), 400, 1000, 1.08)]
# --- 6. cinq ans plus tard… Marseille !
E6 = [El(tag("5 ANS PLUS TARD…", 64, BLANC), CX, 420, L0[6] + .05, None, "pop", rot=-2),
      El(lambda fr: logo("om", 420), CX, 900, k(6, "Marseille") - .15, None, "pop", rot=-4),
      El(stampl("À MARSEILLE !", SKY, 130), CX, 1240, k(6, "Marseille") - .05, None, "stamp", rot=-6)]
@scene(L0[6], trans="tear", td=.22)
def s6(L, fr, t):
    stripes_bg(L, (250, 250, 246), SKY, key="s6", t=t); dark(L, .15)
    spin_kit(L, fr, 820, 1800, .9, t, k(6, "Marseille") - .1, "juve", "om", arms=(150, 150) if t > k(6, "Marseille") else (20, 20), mood="happy")
    if t > k(6, "Marseille"): sparks_burst(L, t, k(6, "Marseille"), CX, 900, 16, (255, 230, 120), 360)
    M.draw_all(L, fr, t, E6)
CAMS["s6"] = [(L0[6], CX, 900, 1.0), (k(6, "Marseille"), CX, 1000, 1.08)]
# --- 7. traître pour Paris, patron pour Marseille
E7 = [El(lambda fr: logo("psg", 260), 270, 620, L0[7] + .05, None, "pop", rot=-5),
      El(stampl("TRAÎTRE", ROUGE, 92), 270, 1000, k(7, "traître") - .05, None, "stamp", rot=-8),
      El(lambda fr: logo("om", 260), 810, 620, k(7, "Marseille") - .1, None, "pop", rot=5),
      El(stampl("PATRON", (40, 150, 70), 92), 810, 1150, k(7, "patron") - .05, None, "stamp", rot=7)]
@scene(L0[7], trans="whip", td=.18)
def s7(L, fr, t):
    d = ImageDraw.Draw(L); paper_fill(L, NAVY, "s7"); d.polygon([(W/2 + 60, 0), (W, 0), (W, H), (W/2 - 60, H)], fill=(250, 250, 246))
    d.polygon([(W/2 + 40, 0), (W/2 + 80, 0), (W/2 - 40, H), (W/2 - 80, H)], fill=(230, 200, 60))
    RAB.draw(L, fr, 270, 1700, s=.85, kit="om", arms=(-4, -4), mood="sad", t=t)
    RAB.draw(L, fr, 810, 1700, s=.85, kit="om", arms=(150, 150), mood="happy", t=t)
    M.draw_all(L, fr, t, E7)
CAMS["s7"] = [(L0[7], CX, 960, 1.0), (k(7, "traître"), 420, 1000, 1.04), (k(7, "patron"), 660, 1050, 1.04)]
# --- 8. août 2025, à Rennes : bagarre dans le vestiaire
E8 = [El(mono("AOÛT 2025", 60), CX, 380, L0[8] + .05, None, "pop", rot=-3),
      El(tag("À RENNES", 60, BLANC), CX, 540, k(8, "Rennes") - .1, None, "pop", rot=2),
      El(stampl("BAGARRE", ROUGE, 150), CX, 900, k(8, "bagarre") - .05, None, "stamp", rot=-8),
      El(KW("DANS LE VESTIAIRE", NOIR, BLANC, 74), CX, 1550, k(8, "vestiaire") - .1, None, "stamp", rot=3)]
@scene(L0[8], trans="tear", td=.22)
def s8(L, fr, t):
    paper_fill(L, (46, 42, 50), "s8"); d = ImageDraw.Draw(L)
    for x in range(60, W, 190): d.rectangle([x, 1050, x + 150, 1500], fill=(70, 66, 74), outline=(30, 28, 34), width=5)   # casiers
    tb = k(8, "bagarre") - .1
    if t < tb: RAB.draw(L, fr, 380, 1760, s=.95, kit="om", arms=(30, 30), mood="sad", t=t); foot.Player("rowe", hair=(30, 24, 22), skin=(150, 104, 74)).draw(L, fr, 720, 1760, s=.95, kit="om", arms=(30, 30), mood="sad", t=t)
    else:                                                        # nuage de bagarre façon cartoon
        rnd = random.Random(int(t*8))
        for j in range(12):
            a = j/12*2*math.pi + t*3; r = 210 + 40*math.sin(t*9 + j); x, y = CX + r*math.cos(a), 1450 + r*.6*math.sin(a)
            d.ellipse([x - 120, y - 90, x + 120, y + 90], fill=(220, 214, 200), outline=(140, 130, 120), width=4)
        d.ellipse([CX - 230, 1300, CX + 230, 1600], fill=(230, 224, 210))
        for j in range(4):
            a = rnd.uniform(0, 6.28); put(L, pp(star_shape(0, 0, 40, 5, .45), (255, 214, 90), "rbst", j, rough=1.2), CX + 260*math.cos(a), 1450 + 160*math.sin(a), 1, a*50)
        for j in range(3):
            ax = CX + rnd.uniform(-180, 180); RAB.draw(L, fr, ax, 1560 + rnd.uniform(-20, 20), s=.5, kit="om", arms=(rnd.uniform(60, 150), rnd.uniform(60, 150)), mood="sad", t=t) if j == 0 else None
    M.draw_all(L, fr, t, E8)
CAMS["s8"] = [(L0[8], CX, 900, 1.0), (k(8, "Rennes"), CX, 1000, 1.06), (k(8, "bagarre"), CX, 1100, 1.05)]
# --- 9. mis à l'écart, vendu au Milan AC
E9 = [El(stampl("À L'ÉCART", ROUGE, 104), CX, 560, k(9, "écart") - .05, None, "stamp", rot=-6),
      El(lambda fr: sign("MILAN AC", 460), 820, 1300, k(9, "Milan") - .2, None, "drop", rot=4, dist=900),
      El(KW("VENDU", JAUNE, NOIR, 150), CX, 760, k(9, "vend") - .05, None, "stamp", rot=5)]
@scene(L0[9], trans="whip", td=.18)
def s9(L, fr, t):
    stripes_bg(L, (206, 24, 36), (24, 22, 26), key="s9", t=t); dark(L, .3)
    x = lerp(CX, 760, M.ease_out(clamp((t - k(9, "vend"))/.6)))
    spin_kit(L, fr, x - 200, 1800, .95, t, k(9, "Milan") - .1, "om", "milan", arms=(20, 20), mood="happy" if t > k(9, "Milan") else "sad")
    M.draw_all(L, fr, t, E9)
CAMS["s9"] = [(L0[9], CX, 900, 1.0), (k(9, "vend"), CX, 900, 1.06), (k(9, "Milan"), 700, 1200, 1.06)]
# --- 10. traître ou incompris ?
E10 = [El(KW("ALORS, RABIOT ?", NOIR, BLANC, 110), CX, 460, L0[10] + .05, None, "stamp", rot=-2),
       El(KW("TRAÎTRE", ROUGE, BLANC, 100), 280, 860, k(10, "traître") - .05, None, "stamp", rot=-6),
       El(KW("INCOMPRIS", (40, 150, 70), BLANC, 90), 790, 1000, k(10, "incompris") - .05, None, "stamp", rot=5),
       El(tag("OU", 56, BLANC), CX, 930, k(10, "ou") - .05, None, "pop"),
       El(marker("DIS-LE EN COMMENTAIRE", "rbdis", 76), CX, 1300, k(10, "Dis") - .05, None, "slide_l", rot=2)]
@scene(L0[10], trans="tear", td=.22)
def s10(L, fr, t):
    paper_fill(L, (20, 30, 76), "s10"); rays(L, (CX, 1000), t, .6, 16, 1700, (34, 48, 110), .1, .3)
    if t > k(10, "Dis"): y = 1420 + 16*abs(math.sin(t*6)); ImageDraw.Draw(L).polygon([(CX - 46, y), (CX + 46, y), (CX, y + 56)], fill=JAUNE)
    M.draw_all(L, fr, t, E10)
CAMS["s10"] = [(L0[10], CX, 900, 1.0), (k(10, "traître"), 460, 950, 1.04), (k(10, "incompris"), 620, 950, 1.04), (k(10, "Dis"), CX, 1000, 1.02)]
SC.sort(key=lambda s: s["t0"])
IMPACTS += [k(0, "OM"), k(0, "mal"), k(1, "dix"), k(1, "mère"), k(2, "retenu"), k(3, "refuse"), k(3, "mail"), k(4, "prolonger"), k(4, "six"), k(5, "libre"),
            k(5, "euro"), k(6, "Marseille"), k(7, "traître"), k(7, "patron"), k(8, "bagarre"), k(9, "écart"), k(9, "vend"), k(10, "traître"), k(10, "incompris")]
PUNCH += IMPACTS
CLUB = [(L0[1], "2012", "PSG"), (L0[2], "2018", "PSG"), (L0[5], "2019", "JUVENTUS"), (L0[6], "2024", "OM"), (L0[8], "2025", "OM"), (k(9, "Milan"), "2025", "MILAN AC")]
def fil(cv, fr, t):
    if t < L0[1]: return
    t0, yr, club = [c for c in CLUB if t >= c[0]][-1]; s = .6 + .4*M.spring(t - t0, .45, 16)
    if PX.ON: PX.put(cv, PX.plabel(yr, 8, PX.WHITE, PX.BLACK, PX.WHITE, s=5), 150, 262); PX.put(cv, PX.plabel(f"CLUB : {club}", 8, PX.WHITE, PX.RED, PX.WHITE, s=5), 560, 262); return
    mono(yr, 46, NOIR).draw(cv, fr, 150, 262, s, -3); LBL(f"CLUB : {club}", f"rbcl{club}", font("title", 38), BLANC, ROUGE, padx=14, pady=5, rough=2).draw(cv, fr, 520, 262, s, 2)
def post(cv, fr, t):
    if R.AQ.ON: R.AQ.caption(cv, WD, t, 1660); return
    KA.caption(cv, WD, t, 1720, 74)
    if PROV: ImageDraw.Draw(cv).text((W/2, 90), "VOIX PROVISOIRE", font=font("title", 36), fill=(255, 90, 90), anchor="mm")
FIL[0] = fil; POST[0] = post
P = .05
def draw(cv, fr, t, T): cv.paste(R.frame(fr, max(0.0, t - P)), (0, 0))
BANK = os.path.join(ROOT, "assets", "sfx")
def X(t, n, g): return (P + t, n, g)
SFX = [X(0, "stamp", .3), X(k(0, "OM") - .1, "whoosh", .3), X(k(0, "mal"), "stamp", .4), X(L0[1], "whoosh", .3), X(k(1, "dix"), "stamp", .35), X(k(1, "mère"), "camera", .3),
       X(L0[2], "rip", .35), X(k(2, "retenu"), "stamp", .4), X(L0[3], "whoosh", .3), X(k(3, "refuse"), "stamp", .4), X(k(3, "mail"), "notif", .35),
       X(L0[4], "rip", .35), X(k(4, "prolonger"), "stamp", .4), X(k(4, "six"), "tictac", .3), X(L0[5], "whoosh", .3), X(k(5, "libre"), "stamp", .4), X(k(5, "euro"), "cash", .35),
       X(L0[6], "rip", .35), X(k(6, "Marseille"), "crowd", .35), X(L0[7], "whoosh", .3), X(k(7, "traître"), "boo", .3), X(k(7, "patron"), "crowd", .3),
       X(L0[8], "rip", .35), X(k(8, "bagarre"), "crash", .35), X(L0[9], "whoosh", .3), X(k(9, "écart"), "stamp", .4), X(k(9, "vend"), "cash", .3),
       X(L0[10], "rip", .35), X(k(10, "traître"), "stamp", .35), X(k(10, "incompris"), "stamp", .35), X(k(10, "Dis"), "notif", .4)]
SFX_DIR = "/tmp/claude-0/sfx_rabiot"; os.makedirs(SFX_DIR, exist_ok=True)
for nm in set(n for _, n, _ in SFX):
    dst = os.path.join(SFX_DIR, nm + ".mp3")
    if not os.path.lexists(dst): os.symlink(os.path.join(BANK, nm + ".mp3"), dst)
SFX = fx.sfx_variants(SFX, SFX_DIR, SFX_DIR + "_v")
if __name__ == "__main__":
    out, SLUG = px_out(os.path.join(ROOT, "output", SLUG), SLUG); os.makedirs(out, exist_ok=True)
    open(os.path.join(HERE, "TEXTE_VOIX.txt"), "w").write("\n".join(TEXTE) + "\n")
    if "--stills" in sys.argv:
        ts = [0.0] + [L0[i] + (L0[i + 1] - L0[i])*f if i + 1 < len(L0) else L0[i] + 1.5*f for i in range(len(L0)) for f in (.35, .85)]
        sh = Image.new("RGB", (180*12, 320*((len(ts) + 11)//12)))
        for j, t in enumerate(ts): sh.paste(R.frame(int(t*FPS), t).resize((180, 320)), ((j % 12)*180, (j//12)*320))
        p = os.path.join(os.environ.get("STILLS_DIR", out), "rabiot_planche.jpg"); sh.save(p, quality=85); print(p, round(WD.end, 2)); sys.exit()
    if PROV:                                                     # aperçu muet au minutage estimé
        import subprocess
        v = out + "/rabiot_provisoire.mp4"; T = WD.end + 1.5
        pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", v], stdin=subprocess.PIPE)
        for fr in range(int(T*FPS)): pr.stdin.write(R.frame(fr, fr/FPS).tobytes())
        pr.stdin.close(); pr.wait(); print(v); sys.exit()
    SCENES = [Scene("rabiot", " ".join(TEXTE), draw, SFX, pad_in=P, pad_out=1.5)]
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=[VOIX], sfx_dir=SFX_DIR + "_v", sfx_db=13.0, duck=.55, lufs=-14.0, crf=22, limit=True))
