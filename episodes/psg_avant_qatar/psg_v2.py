"""PSG AVANT LE QATAR v2 — refait dans le STYLE RENNES (episodes/rennes/rennes3.py, demande utilisateur : v1 « pas assez dynamique »).
Micro-scène par phrase, mots qui claquent au mot près (timings faster-whisper de voix/voix.mp3), caméra à ressort qui suit l'action,
coups de zoom + secousse sur chaque impact, tableaux à palettes, volumes papercraft (pc_over), fil rouge en haut à gauche :
date + « N ANS AVANT LE QATAR ». CTA quiz au milieu (réponse jamais donnée), question finale clivante. Pas de musique.
  python3 episodes/psg_avant_qatar/psg_v2.py --stills [scene]
  python3 episodes/psg_avant_qatar/psg_v2.py"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RENNES = os.path.join(ROOT, "episodes", "rennes")
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "brest_ldc"))
sys.path.insert(0, os.path.join(ROOT, "episodes", "lille_v5")); sys.path.insert(0, RENNES)
from quiz import *
import foot, fx
from brest_ldc import marker
from rgfx import *
import pc_over; pc_over.install(globals()); pc_over.install_v4(globals())
import pc_lib as PC
import motion as M
from motion import El, words, walk, arc, ground_shadow
from paper_cut import paper_player
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PC.KITS["real"] = dict(c1=(246, 246, 242), sleeve=(246, 246, 242), shorts=(246, 246, 242), socks=(246, 246, 242), trim=(120, 60, 160), kind="plain")
PC.KITS["asse"] = dict(c1=(0, 132, 72), sleeve=(0, 132, 72), shorts=(250, 250, 246), socks=(0, 132, 72), trim=(250, 250, 246), kind="plain")

TITLE = "~/histoires $ ./psg"
SLUG = "psg_avant_qatar_v2"
VOIX = os.path.join(HERE, "voix", "voix.mp3")
TEXTE = open(os.path.join(HERE, "TEXTE_VOIX.txt")).read()
NAVY = (20, 34, 82); PRED = (206, 36, 44)
# temps clés (s, voix.mp3) relevés avec faster-whisper
K = dict(footix=.32, connais=1.14, psg=1.70, avant0=2.44, qatar=2.70, milliards=3.60, paris1=4.28, chaos=5.24, magique=6.14,
         y1978=7.36, president=8.30, styliste=9.10, hechter=9.52, radie=10.56, vie=11.02, motif=11.56, double=12.22, billet=12.48, parc=13.06,
         liquide=14.14, comptes=15.08, quatre=15.58, finale=16.52, coupe=17.02, rocheteau=17.96, egalise=18.40, derniere=19.00,
         borelli=20.92, saute=21.38, pelouse=21.98, embrasse=22.44, premier=23.08, trophee=23.44,
         y1993=24.70, perd=26.06, troisun=26.24, madrid=26.90, retour=27.62, quatreun=28.22, tete=29.24, additionnel=29.86,
         question=30.68, vrais=31.26, qui=31.72, cette=32.02, tete2=32.22, reponds=32.66, comm=33.06, like=33.76, abonne=34.24,
         annee=35.02, om=35.76, titre=36.36, corruption=36.82, paris2=37.54, deuxieme=38.00, reclame=38.76, pas=39.32,
         resultat=39.80, championnat=40.66, sans=41.18, champion=41.46, puis=42.10, weah=42.26, ginola=42.96, rai=43.74, coupe2=44.34,
         bresilien=45.58, ronaldinho=46.48, y2008=47.58, survie=48.96, derniere2=49.58, sochaux=50.68, diane=51.36, deux=52.12, sauve=53.28,
         trois=54.10, qatar2=55.20, toi=55.84, vrai=56.66, avant=57.64, apres=58.28, dis=58.86, comm2=59.26, fin=59.98)
SC_T = dict(hook=0.0, bill=3.09, y78=7.03, motif=11.38, y82=15.51, bor=19.9, y93=24.47, quiz=30.55, om=34.8, vide=39.68, stars=42.0,
            y08=47.23, diane=51.21, fin=53.98)
SPEED = 1.15                                                     # voix accélérée (demande utilisateur : « trop lent ») -> tout le minutage suit
K = {k: v/SPEED for k, v in K.items()}; SC_T = {k: v/SPEED for k, v in SC_T.items()}
VOIX_SRC = VOIX; VOIX = os.path.join(HERE, "voix", "voix_rapide.mp3")
if not os.path.exists(VOIX) or os.path.getmtime(VOIX) < os.path.getmtime(VOIX_SRC):
    import subprocess; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", VOIX_SRC, "-af", f"atempo={SPEED}", VOIX], check=True)
# ------------------------------------------------------------------ outils (repris de rennes3.py)
def ease(u): u = clamp(u); return u*u*(3 - 2*u)
def eob(u, s=1.9): return ease_out_back(clamp(u), s)
def wob(t, t0, amp=12, f=9, damp=5): return 0 if t < t0 else amp*math.sin((t - t0)*f)*math.exp(-(t - t0)*damp)
def put(L, spr, x, y, s=1.0, rot=0.0, a=1.0):
    if s > .01 and a > .01: blit_sxy(L, spr, x, y, s, s, rot, a)
_sh = {}
def shadowed(spr, key=None):
    k = key or id(spr)
    if k not in _sh:
        im = Image.new("RGBA", (spr.width + 40, spr.height + 40), (0, 0, 0, 0)); a = spr.getchannel("A").point(lambda v: v*110//255)
        sh = Image.new("RGBA", spr.size, (30, 20, 14, 0)); sh.putalpha(a); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (34, 38))
        im.alpha_composite(spr, (20, 20)); ax, ay = spr.info["anchor"]; im.info["anchor"] = (ax + 20, ay + 20); _sh[k] = im
    return _sh[k]
def logo(n, h):
    k = ("logo", n, h)
    if k not in _sh: _sh[k] = shadowed(sticker(n, h), k)
    return _sh[k]
def KW(txt, bg=NOIR, fg=BLANC, size=118): return LBL(txt, f"pqk{txt}{bg}{size}", font("title", size), fg, bg, padx=24, pady=6, rough=3)
def stampl(txt, col=ROUGE, size=150): return LBL(txt, f"pqs{txt}{size}{col}", font("title", size), col, CREME, padx=34, pady=6, rough=2)
def tag(txt, size=60, bg=BLANC, fg=NOIR): return LBL(txt, f"pqt{txt}{size}{bg}", font("title", size), fg, bg, padx=24, pady=8, rough=2)
def mono(txt, size=64, bg=NOIR, fg=BLANC): return LBL(txt, f"pqm{txt}{size}{bg}", font("mono", size), fg, bg, padx=18, pady=6, rough=2)
_tex = {}
def paper_fill(L, col, key):
    k = (key, L.size, col)
    if k not in _tex:
        w_, h_ = L.size; rng = np.random.default_rng(abs(hash(key)) % 999)
        g = np.asarray(Image.fromarray((rng.random((h_//24 + 2, w_//24 + 2))*255).astype(np.uint8)).resize((w_, h_), Image.BICUBIC), np.float32)/255
        a = np.zeros((h_, w_, 3), np.float32); a[:] = col; a *= (.93 + .12*g)[..., None]
        sp = rng.random((h_, w_)).astype(np.float32); a += ((sp > .965)*14 - (sp < .03)*12)[..., None]
        _tex[k] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    L.paste(_tex[k], (0, 0))
def dark(L, a):
    if a > .01: L.alpha_composite(Image.new("RGBA", L.size, (8, 6, 14, int(255*clamp(a)))))
def stripes_bg(L, a=NAVY, b=PRED, w_=140, key="ps", t=0):
    paper_fill(L, a, key); d = ImageDraw.Draw(L); off = (t*40) % (2*w_)
    for x in range(-H - 2*w_, L.width + 2*w_, 3*w_): d.polygon([(x + off, 0), (x + w_ + off, 0), (x + w_ + H*.35 + off, L.height), (x + H*.35 + off, L.height)], fill=b)
def apply_cam(L, cx, cy, z, rot=0.0):
    z = max(z, max(W/L.width, H/L.height)); bw, bh = W/z, H/z
    x0 = min(max(cx - bw/2, 0), L.width - bw); y0 = min(max(cy - bh/2, 0), L.height - bh)
    im = L.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.BICUBIC)
    if abs(rot) > .05: im = im.rotate(rot, resample=Image.BICUBIC, fillcolor=im.getpixel((2, 2)))
    return im
_fc = {}
def flip_card(v, size):
    k = (v, size)
    if k not in _fc:
        w_, h_ = int(size*.82), int(size*1.12); im = Image.new("RGBA", (w_, h_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, w_ - 1, h_ - 1], 14, fill=(18, 18, 22)); d.rounded_rectangle([0, 0, w_ - 1, h_//2], 14, fill=(26, 26, 32))
        text_c(d, w_/2, h_/2, str(v), font("title", size), (252, 252, 246)); d.line([(0, h_//2), (w_, h_//2)], fill=(8, 8, 10), width=5)
        _fc[k] = im
    return _fc[k]
def flip_digit(L, x, y, v, t, tc, prev, size=150):
    new, old = flip_card(v, size), flip_card(prev, size); w_, h_ = new.size; x0, y0 = int(x - w_/2), int(y - h_/2)
    u = clamp((t - tc)/.22) if t >= tc else 1
    if u >= 1: L.alpha_composite(new, (x0, y0)); return
    L.alpha_composite(new.crop((0, 0, w_, h_//2)), (x0, y0)); L.alpha_composite(old.crop((0, h_//2, w_, h_)), (x0, y0 + h_//2))
    if u < .5:
        f = old.crop((0, 0, w_, h_//2)); hh = max(1, int(h_//2*math.cos(math.pi*u))); L.alpha_composite(f.resize((w_, hh)), (x0, y0 + h_//2 - hh))
    else:
        f = new.crop((0, h_//2, w_, h_)); hh = max(1, int(h_//2*-math.cos(math.pi*u))); L.alpha_composite(f.resize((w_, hh)), (x0, y0 + h_//2))
def scoreboard(L, x, y, t, seq, left, right, size=150, s_in=1.0):
    if s_in <= .02: return
    put(L, board_base(860, 330, left, right), x, y - 30, s_in)
    if s_in < .95: return
    A, B, pA, pB, tA, tB = 0, 0, 0, 0, -9, -9
    for (ti, a, b) in seq:
        if t >= ti:
            if a != A: pA, A, tA = A, a, ti
            if b != B: pB, B, tB = B, b, ti
    flip_digit(L, x - 210, y, A, t, tA, pA, size); flip_digit(L, x + 210, y, B, t, tB, pB, size)
    ImageDraw.Draw(L).rounded_rectangle([x - 36, y - 10, x + 36, y + 10], 6, fill=(250, 220, 120))
def board_in(t, t0, t1=None):
    v = M.spring(t - t0, .5, 12)
    if t1 is not None and t > t1: v *= 1 - M.ease_in((t - t1)/.2)
    return v
def ball(L, fr, x, y, s, t, ground=None):
    if ground is not None: ground_shadow(L, x, ground, 40*s*max(.3, 1 - (ground - y)/900), .3)
    foot.draw_ball(L, fr, x, y, s, t*520)
def cursor():
    if "cur" not in _fc:
        im = Image.new("RGBA", (140, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        pts = [(10, 10), (10, 150), (48, 112), (74, 176), (100, 164), (74, 102), (124, 102)]
        d.polygon([(x + 6, y + 6) for x, y in pts], fill=(0, 0, 0, 90)); d.polygon(pts, fill=BLANC, outline=NOIR); d.line(pts + [pts[0]], fill=NOIR, width=6)
        im.info["anchor"] = (10, 10); _fc["cur"] = im
    return _fc["cur"]
def sparks_burst(L, t, t0, x, y, n=12, col=(255, 230, 120), dist=220):
    u = (t - t0)/.45
    if not 0 < u < 1: return
    d = ImageDraw.Draw(L)
    for k in range(n):
        a = 2*math.pi*k/n; r0, r1 = dist*M.ease_out(u)*.6, dist*M.ease_out(u)
        d.line([(x + r0*math.cos(a), y + r0*math.sin(a)), (x + r1*math.cos(a), y + r1*math.sin(a))], fill=col, width=max(2, int(10*(1 - u))))
def puffs(L, t, t0, x, y, n=10, col=(210, 196, 170), spread=260, dur=.6):
    u = (t - t0)/dur
    if not 0 < u < 1: return
    d = ImageDraw.Draw(L)
    for k in range(n):
        a = math.pi*(k + .5)/n; r_ = spread*M.ease_out(u); rr = 26*(1 - u) + 6
        d.ellipse([x + r_*math.cos(a) - rr, y - r_*.35*math.sin(a) - rr, x + r_*math.cos(a) + rr, y - r_*.35*math.sin(a) + rr], fill=col)
def marker_line(L, p0, p1, u, col=ROUGE, wd=14):
    if u <= 0: return
    ImageDraw.Draw(L).line([p0, (lerp(p0[0], p1[0], clamp(u)), lerp(p0[1], p1[1], clamp(u)))], fill=col, width=wd)
PHOTO = os.path.join(ROOT, "assets", "photos", "psg")
BOX = {"ronaldinho": (0, 0, 789, 860), "ginola": (0, 0, 620, 640)}
def CUT(slug, h):
    k = ("cut", slug, h)
    if k not in _sh: _sh[k] = paper_player(os.path.join(PHOTO, slug + ".png"), BOX.get(slug), h)
    return _sh[k]
def qatar_flag(L, x, y, t, s=1.0):
    w_, h_ = int(560*s), int(340*s); im = Image.new("RGBA", (w_ + 40, h_ + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([20, 20, 20 + w_, 20 + h_], fill=(138, 21, 56)); band = w_*.3; n = 9; pts = [(20, 20), (20 + band, 20)]
    for k in range(n): y0 = 20 + h_*k/n; pts += [(20 + band + w_*.08, y0 + h_/n/2), (20 + band, y0 + h_/n)]
    d.polygon(pts + [(20, 20 + h_)], fill=(250, 248, 240))
    a = np.asarray(im); out = np.zeros_like(a)
    for xx in range(0, a.shape[1]): out[:, xx] = np.roll(a[:, xx], int(10*math.sin(xx/70 - t*4)*(xx/a.shape[1])), 0)
    sp = Image.fromarray(out); sp.info["anchor"] = (20, 20); put(L, sp, x - w_/2, y - h_/2, 1, -3)
    d2 = ImageDraw.Draw(L); d2.rectangle([x - w_/2 - 26, y - h_/2 - 10, x - w_/2 - 8, y + h_/2 + 420], fill=(120, 90, 60))

# ================================================================== SCÈNES (t = temps voix)
SC = []
def scene(t0, trans="cut", td=.3):
    def deco_(fn): SC.append(dict(t0=t0, fn=fn, size=(W, H), trans=trans, td=td, name=fn.__name__)); return fn
    return deco_
CAMS = {}
# --- 0. HOOK : « T'es un footix si tu connais pas le PSG d'avant le Qatar »
E_H = words(lambda w, i: KW(w, ROUGE if w == "FOOTIX ?" else NOIR, BLANC, 170 if w == "FOOTIX ?" else 120), [("T'ES UN", -.5), ("FOOTIX ?", -.5)], CX, 470, out=SC_T["bill"] - .15) + \
      [El(lambda fr: logo("psg", 520), CX, 1120, -.3, SC_T["bill"] - .15, "pop", "shrink", 1, -3, .6),
       El(tag("SI TU CONNAIS PAS", 64, BLANC), CX, 730, K["connais"] - .05, SC_T["bill"] - .15, "pop", "fly", rot=2),
       El(KW("LE PSG D'AVANT", JAUNE, NOIR, 92), CX, 1440, K["avant0"] - .2, SC_T["bill"] - .15, "stamp", "fly", rot=-3),
       El(KW("LE QATAR", NOIR, BLANC, 92), CX, 1590, K["qatar"] - .05, SC_T["bill"] - .15, "stamp", "fly", rot=3)]
@scene(SC_T["hook"])
def s_hook(L, fr, t):
    stripes_bg(L, key="hook", t=t); dark(L, .35); rays(L, (CX, 1120), t, .7, 14, 1600, (60, 70, 140), .1, .3)
    M.draw_all(L, fr, t, E_H)
    if t > K["qatar"] + .15: marker_line(L, (CX - 210, 1600), (CX + 210, 1580), (t - K["qatar"] - .15)/.2, ROUGE, 16)   # « QATAR » barré
CAMS["s_hook"] = [(0, CX, 960, 1.04), (K["psg"], CX, 1000, 1.08), (K["avant0"], CX, 1100, 1.05), (SC_T["bill"], CX, 1000, 1.0)]
# --- 1. Avant les milliards : le chaos… et la magie
E_B = [El(KW("AVANT LES MILLIARDS", NOIR, BLANC, 90), CX, 520, K["milliards"] - .3, K["chaos"] - .1, "stamp", "fly", rot=-2),
       El(stampl("LE CHAOS", ROUGE, 170), CX, 1100, K["chaos"] - .02, K["magique"] - .1, "stamp", "shrink", rot=-6),
       El(KW("ET C'ÉTAIT MAGIQUE", JAUNE, NOIR, 100), CX, 1420, K["magique"] - .05, None, "stamp", rot=3)]
@scene(SC_T["bill"], trans="whip", td=.18)
def s_bill(L, fr, t):
    paper_fill(L, (40, 30, 34), "bill"); d = ImageDraw.Draw(L)
    for k in range(7):                                           # sacs de billets qui tombent
        t0 = K["milliards"] - .2 + k*.07
        if t > t0: put(L, money_bag(260, "€€€"), 160 + k*130, 1000 + 40*(k % 2) + min(0, -900*(1 - M.ease_out((t - t0)/.35))), 1, -8 + 4*k)
    if t > K["paris1"] - .1: marker_line(L, (80, 880), (1000, 1160), (t - K["paris1"] + .1)/.25, ROUGE, 22); marker_line(L, (1000, 880), (80, 1160), (t - K["paris1"] - .1)/.25, ROUGE, 22)
    if t > K["chaos"]:                                           # chaos : papiers qui volent
        for k in range(14):
            a = (t - K["chaos"])*2 + k; ImageDraw.Draw(L).rectangle([(k*83 + 300*math.sin(a)) % W, (k*137 + t*500) % H, (k*83 + 300*math.sin(a)) % W + 40, (k*137 + t*500) % H + 26], fill=(230, 220, 200))
    if t > K["magique"]:
        for k in range(10):
            u = ((t - K["magique"])*.8 + k*.1) % 1; put(L, PC_STAR(), CX + 420*math.sin(k*2.3), 1420 - 500*u, .5*(1 - u), t*90 + k*30)
    M.draw_all(L, fr, t, E_B)
_star = {}
def PC_STAR():
    if "s" not in _star: _star["s"] = pp(star_shape(0, 0, 60, 5, .45), (250, 214, 90), "star", 1, rough=1.4)
    return _star["s"]
CAMS["s_bill"] = [(SC_T["bill"], CX, 900, 1.0), (K["paris1"], CX, 1000, 1.08), (K["chaos"], CX, 1100, 1.14), (K["magique"], CX, 1300, 1.04)]
# --- 2. 1978 : Hechter, styliste et président, radié à vie
HECHTER = foot.Player("hechter", hair=(80, 60, 44))
E_78 = [El(stampl("1978", (110, 70, 40), 200), CX, 560, K["y1978"], K["styliste"] - .3, "stamp", "fly", 1, -4),
        El(tag("LE PRÉSIDENT", 64, CREME), CX, 560, K["president"], None, "pop", rot=2),
        El(marker("DANIEL HECHTER", "pqhech", 74), CX, 700, K["hechter"] - .05, None, "slide_l", rot=-2),
        El(tag("STYLISTE", 58, JAUNE), 820, 880, K["styliste"], None, "pop", rot=6),
        El(stampl("RADIÉ À VIE", ROUGE, 140), CX, 1260, K["radie"] - .03, None, "stamp", rot=-8)]
@scene(SC_T["y78"], trans="tear", td=.22)
def s_78(L, fr, t):
    paper_fill(L, (214, 190, 146), "sep")
    for k in range(10):
        yy = (t*30 + k*173) % H; ImageDraw.Draw(L).ellipse([(k*101) % W, yy, (k*101) % W + 4, yy + 4], fill=(240, 226, 196))
    u = clamp((t - K["president"] + .3)/.9); xs = lerp(-250, 430, M.ease_out(u)); mv = 0 < u < 1
    legs, arms, bob = walk(t, 9, 22) if mv else ((0, 0), (14, 14), 0)
    sad = t > K["radie"]
    HECHTER.draw(L, fr, xs, 1720 + bob, s=1.0, kit="suit", legs=legs, arms=arms if not sad else (-4, -4), mood="sad" if sad else "happy", t=t, look=(1, 0))
    if t > K["styliste"]:                                        # le maillot qu'il a dessiné, sur un portant
        v = M.spring(t - K["styliste"], .45, 13); J = foot.jersey_front("psg", "pqjf"); J.draw(L, fr, 790, 1250, .75*v, 4*math.sin(t*2))
    if sad: puffs(L, t, K["radie"], 430, 1700, 10, (190, 170, 140), 300)
    M.draw_all(L, fr, t, E_78)
CAMS["s_78"] = [(SC_T["y78"], CX, 900, 1.0), (K["president"], CX, 1100, 1.06), (K["hechter"], 520, 1050, 1.12), (K["styliste"], 700, 1100, 1.1),
                (K["radie"] - .1, CX, 1200, 1.04), (K["radie"] + .1, CX, 1250, 1.14)]
# --- 3. Le motif : double billetterie, du liquide hors des comptes
E_MO = words(lambda w, i: KW(w, NOIR, BLANC, 110), [("LE MOTIF", K["motif"] - .05), ("?", K["motif"] + .25)], CX, 470, out=K["double"] - .1) + \
       [El(KW("DOUBLE BILLETTERIE", ROUGE, BLANC, 80), CX, 470, K["double"] - .05, None, "stamp", rot=-2),
        El(stampl("HORS DES COMPTES", ROUGE, 96), CX, 1580, K["comptes"] - .05, None, "stamp", rot=-6)]
@scene(SC_T["motif"], trans="whip", td=.18)
def s_motif(L, fr, t):
    paper_fill(L, (238, 230, 212), "tk")
    k = M.spring(t - K["double"], .5, 11) if t > K["double"] else 0
    for j, dx in enumerate((-1, 1)):
        if j == 1 and k <= .01: continue
        x = CX + dx*k*90*(1 if j else -1); y = 860 + (j*2 - 1)*k*130
        put(L, ticket("PARC DES PRINCES", "BILLET N°" + ("1903" if j else "1903 bis"), ROUGE, 600), x, y, M.spring(t - SC_T["motif"] - .1, .45, 13), -4 + j*6)
    if t > K["liquide"] - .1:
        for b in range(9):
            t0 = K["liquide"] - .1 + b*.08; v = clamp((t - t0)/.5)
            if v > 0: put(L, bill(b), 200 + (b % 5)*170, lerp(900, 1380 + (b//5)*40, M.ease_in(v) if v < 1 else 1), .9, (b*37) % 50 - 25 + 200*(1 - v))
        put(L, money_bag(320, ""), CX, 1350, M.spring(t - K["liquide"] + .1, .45, 13))
    M.draw_all(L, fr, t, E_MO)
CAMS["s_motif"] = [(SC_T["motif"], CX, 900, 1.02), (K["double"], CX, 900, 1.05), (K["parc"], CX, 900, 1.03), (K["liquide"], CX, 1250, 1.08), (K["comptes"], CX, 1400, 1.1)]
# --- 4. 1982 : finale de Coupe de France, Rocheteau à la dernière minute
ROCH = foot.Player("roch", hair=(40, 30, 26))
E_82 = [El(tag("4 ANS PLUS TARD…", 64, BLANC), CX, 430, K["quatre"] - .05, K["finale"] + .3, "pop", "fly", rot=-2),
        El(lambda fr: ticket("FINALE 1982", "COUPE DE FRANCE", (30, 110, 70), 640), CX, 640, K["finale"] - .1, K["rocheteau"] - .2, "drop", "fly", rot=-3, dist=900),
        El(marker("ROCHETEAU", "pqroch", 80), 300, 640, K["rocheteau"] - .02, None, "slide_l", rot=-3),
        El(stampl("DERNIÈRE MINUTE !", ROUGE, 96), CX, 1520, K["derniere"] - .03, None, "stamp", rot=-6)]
@scene(SC_T["y82"], trans="tear", td=.22)
def s_82(L, fr, t):
    paper_fill(L, (58, 140, 76), "pitch"); d = ImageDraw.Draw(L)
    for k in range(0, H, 220): d.rectangle([0, k, W, k + 110], fill=(70, 156, 88))
    scoreboard(L, CX, 1000, t, [(0, 0, 0), (K["coupe"], 1, 2), (K["egalise"] - .05, 2, 2)], "PSG", "ST-ÉTIENNE", 150, board_in(t, K["finale"]))
    if t > K["rocheteau"] - .6:
        foot.draw_goal(L, fr, 780, 1700, 520, 260, 0, 1, t)
        kick = t > K["rocheteau"] - .2
        ROCH.draw(L, fr, 300, 1800, s=1.0, kit="psg", legs=(-30, 40) if kick and t < K["rocheteau"] + .1 else (10, -10), arms=(40, 50) if t < K["egalise"] else (160, 160), mood="happy", t=t)
        u = clamp((t - K["rocheteau"] + .1)/.4); bx, by = arc((360, 1780), (780, 1620), 140, u); ball(L, fr, bx, by, .6, t, 1790)
        if t > K["egalise"]: sparks_burst(L, t, K["egalise"], 780, 1620, 14, (255, 236, 140), 260)
    M.draw_all(L, fr, t, E_82)
CAMS["s_82"] = [(SC_T["y82"], CX, 900, 1.0), (K["finale"], CX, 800, 1.06), (K["coupe"], CX, 1000, 1.1), (K["rocheteau"] - .3, 560, 1550, 1.12),
                (K["egalise"], CX, 1150, 1.14), (K["derniere"], CX, 1300, 1.06)]
# --- 5. Borelli saute sur la pelouse et l'embrasse ; 1er trophée
BOREL = foot.Player("borelli", hair=(40, 36, 34))
E_BO = [El(marker("FRANCIS BORELLI", "pqbor", 74), CX, 480, K["borelli"] - .05, K["premier"] - .2, "slide_l", "fly", rot=-2),
        El(tag("LE PRÉSIDENT", 56, CREME), CX, 360, K["borelli"] - .25, K["premier"] - .2, "pop", "fly", rot=2),
        El(KW("1er TROPHÉE", JAUNE, NOIR, 130), CX, 460, K["premier"] - .05, None, "stamp", rot=-3),
        El(tag("DE L'HISTOIRE", 64, BLANC), CX, 600, K["trophee"] + .2, None, "pop", rot=3)]
@scene(SC_T["bor"], trans="whip", td=.18)
def s_bor(L, fr, t):
    paper_fill(L, (58, 140, 76), "pitch2"); d = ImageDraw.Draw(L)
    for k in range(0, H, 220): d.rectangle([0, k, W, k + 110], fill=(70, 156, 88))
    rays(L, (CX, 900), t, .5 if t > K["premier"] else 0, 14, 1500, (250, 226, 150), .1, .25)
    u = clamp((t - K["borelli"] + .4)/.8); x = lerp(W + 250, 560, M.ease_out(u))
    jump = clamp((t - K["saute"])/.45); hy = -220*math.sin(math.pi*jump) if 0 < jump < 1 else 0
    kneel = t > K["embrasse"] - .1
    legs, arms, bob = walk(t, 11, 30) if 0 < u < 1 else ((0, 0), (150, 150), 0)
    BOREL.draw(L, fr, x, 1740 + bob + hy + (60 if kneel else 0), s=1.0, kit="suit", legs=legs if not kneel else (40, 40), arms=arms if not kneel else (60, 60), mood="happy", t=t, lean=-28 if kneel else 0, look=(-1, 0))
    if kneel:
        for k in range(8):
            hv = ((t - K["embrasse"])*.9 + k*.12)
            if 0 < hv < 1: put(L, heart(40 + (k % 3)*12), x - 60 + 160*math.sin(k*1.9)*hv, 1700 - 600*hv, 1 - .5*hv, 20*math.sin(k + t*3), 1 - hv*hv)
    if t > K["premier"] - .1:
        v = M.spring(t - K["premier"] + .1, .5, 12); put(L, cup_gold(380), CX, lerp(2300, 1000, v), 1, 4*math.sin(t*2))
        sparks_burst(L, t, K["premier"] + .1, CX, 900, 14, (255, 230, 120), 320)
    M.draw_all(L, fr, t, E_BO)
CAMS["s_bor"] = [(SC_T["bor"], CX, 1100, 1.0), (K["saute"], 700, 1350, 1.1), (K["embrasse"], 560, 1550, 1.16), (K["premier"], CX, 900, 1.04)]
# --- 6. 1993 : 3-1 à Madrid, 4-1 au Parc, une tête dans le temps additionnel
KOMBO = foot.Player("kombo", hair=(30, 24, 22), skin=(150, 104, 74)); REALP = foot.Player("realp", hair=(60, 44, 30))
E_93 = [El(stampl("1993", NOIR, 170), CX, 470, K["y1993"], K["perd"] - .2, "stamp", "fly", 1, -3),
        El(tag("À MADRID", 60, BLANC), CX, 560, K["madrid"] - .05, K["retour"] - .1, "pop", "fly", rot=2),
        El(KW("AU PARC", NOIR, BLANC, 100), CX, 520, K["retour"] - .05, None, "stamp", rot=-2),
        El(stampl("90+6'", ROUGE, 130), 800, 1420, K["additionnel"] - .05, None, "stamp", rot=8)]
@scene(SC_T["y93"], trans="tear", td=.22)
def s_93(L, fr, t):
    paper_fill(L, (20, 30, 76), "n93"); rays(L, (CX, 1000), t, .5, 16, 1700, (34, 48, 110), .1, .3)
    for k in range(30): ImageDraw.Draw(L).ellipse([(k*137) % W, (k*89) % 700 + 150, (k*137) % W + 6, (k*89) % 700 + 156], fill=(240, 240, 255))
    back = t > K["retour"] - .1
    if not back: scoreboard(L, CX, 920, t, [(0, 0, 0), (K["troisun"], 3, 1)], "REAL", "PSG", 150, board_in(t, K["perd"] - .3, K["retour"] - .3))
    else: scoreboard(L, CX, 920, t, [(0, 0, 0), (K["quatreun"] - .25, 1, 0), (K["quatreun"] - .1, 2, 0), (K["quatreun"] + .05, 3, 1), (K["tete"] + .25, 4, 1)], "PSG", "REAL", 150, board_in(t, K["retour"] - .1))
    if t > K["quatreun"] + .2:
        REALP.draw(L, fr, 800, 1840, s=.95, kit="real", arms=(20, 20), mood="sad" if t > K["tete"] + .3 else "happy", t=t, look=(-1, 0))
        jump = clamp((t - K["tete"] + .25)/.5); hj = -200*math.sin(math.pi*jump) if 0 < jump < 1 else 0
        KOMBO.draw(L, fr, 380, 1840 + hj, s=1.0, kit="psg", arms=(150, 150) if t > K["tete"] + .3 else (60, 60), mood="happy", t=t, look=(1, -1))
        u = clamp((t - K["tete"] + .55)/.35); bx, by = arc((980, 1250), (390, 1290 + hj), 120, u)
        if u < 1: ball(L, fr, bx, by, .55, t)
        else:
            u2 = clamp((t - K["tete"] + .2)/.3); bx, by = arc((390, 1290), (120, 1500), 60, u2); ball(L, fr, bx, by, .55, t)
        if t > K["tete"] + .25: sparks_burst(L, t, K["tete"] + .25, 380, 1300, 14, (255, 236, 140), 260)
    M.draw_all(L, fr, t, E_93)
CAMS["s_93"] = [(SC_T["y93"], CX, 900, 1.0), (K["troisun"], CX, 920, 1.12), (K["retour"], CX, 900, 1.02), (K["quatreun"], CX, 950, 1.14),
                (K["tete"] - .3, 480, 1400, 1.1), (K["additionnel"], CX, 1150, 1.03)]
# --- 7. QUIZ : qui a mis cette tête ? (réponse jamais donnée) + abonne-toi / like
QOUT = K["like"] - .45
E_Q = words(lambda w, i: KW(w, NOIR if w != "TÊTE ?" else ROUGE, BLANC, 104), [("QUI", K["qui"]), ("A MIS", K["qui"] + .15), ("CETTE", K["cette"]), ("TÊTE ?", K["tete2"])],
            CX, 520, maxw=900, out=QOUT) + \
      [El(tag("QUESTION POUR LES VRAIS", 54, ROUGE, BLANC), CX, 330, K["question"] + .05, QOUT, "pop", "fly", rot=-2),
       El(marker("RÉPONDS EN COMMENTAIRE", "pqrep", 66), CX, 1440, K["reponds"] - .05, QOUT, "slide_l", "fly", rot=2),
       El(KW("MERCI !", JAUNE, NOIR, 130), CX, 560, K["abonne"] + .45, None, "stamp", rot=-3)]
@scene(SC_T["quiz"], trans="whip", td=.18)
def s_quiz(L, fr, t):
    paper_fill(L, (20, 30, 76), "quiz"); rays(L, (CX, 1050), t, .6, 16, 1700, (34, 48, 110), .1, .3)
    if t < QOUT + .25:
        ex = M.ease_in((t - QOUT)/.25) if t > QOUT else 0
        lay = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); KOMBO.draw(lay, fr, 450, 860, s=1.1, kit="psg", arms=(100 + 10*math.sin(t*3), 100 - 10*math.sin(t*3)), t=t)
        a = lay.getchannel("A"); rim_ = Image.new("RGBA", lay.size, (140, 150, 200, 255)); rim_.putalpha(a.filter(ImageFilter.MaxFilter(9)))
        sil = Image.new("RGBA", lay.size, (8, 8, 12, 255)); sil.putalpha(a); rim_.alpha_composite(sil); rim_.info["anchor"] = (450, 860)
        put(L, rim_, CX, 1600 + 900*ex*ex, M.spring(t - SC_T["quiz"] - .1, .5, 12))
        put(L, qmark(), CX, 980 + 12*math.sin(t*4) + 900*ex*ex, .55*M.spring(t - SC_T["quiz"] - .25, .4, 14), 6*math.sin(t*3))
        if K["reponds"] < t < QOUT:
            y = 1530 + 18*abs(math.sin(t*6)); ImageDraw.Draw(L).polygon([(CX - 46, y), (CX + 46, y), (CX, y + 56)], fill=ROUGE)
    else:
        tc = K["abonne"] + .18; pressed = t > tc
        bs = M.spring(t - QOUT - .1, .45, 14)
        if pressed: b = t - tc; q = .12*math.exp(-b*12)*math.cos(b*30); bsx, bsy = 1 + q, 1 - q - (.08 if b < .08 else 0)
        else: bsx = bsy = 1
        blit_sxy(L, sub_button(pressed), CX, 900, bs*bsx, bs*bsy, -2)
        if pressed: sparks_burst(L, t, tc, CX, 900, 14, (255, 230, 120), 340)
        cu = M.ease_io((t - QOUT)/.4); cx_, cy_ = lerp(980, CX + 60, cu), lerp(1500, 920, cu)
        if pressed: cx_ += 160*M.ease_in((t - tc - .25)/.4); cy_ += 500*M.ease_in((t - tc - .25)/.4)
        put(L, cursor(), cx_, cy_ + (8 if abs(t - tc) < .06 else 0), .9)
        b = t - QOUT; beat = 1 + .08*math.exp(-((b % .6) - .05)**2/.004)
        put(L, heart(150), CX, 1330, M.spring(b, .35, 16)*beat, 0)
        for k in range(12):
            u = (b*.9 - k*.05)
            if 0 < u < 1: put(L, heart(26 + (k % 3)*10, (255, 90, 130)), CX + 320*math.sin(k*1.7)*M.ease_out(u), 1330 - 650*u, 1 - u*.6, 20*math.sin(k + t*3), 1 - u**2)
    M.draw_all(L, fr, t, E_Q)
CAMS["s_quiz"] = [(SC_T["quiz"], CX, 980, 1.0), (K["tete2"], CX, 900, 1.08), (K["reponds"], CX, 1100, 1.05), (QOUT, CX, 940, 1.1), (K["abonne"], CX, 1100, 1.1)]
# --- 8. Affaire VA-OM : l'OM perd son titre, Paris ne le réclame même pas
E_OM = [El(tag("LA MÊME ANNÉE", 58, CREME), CX, 360, K["annee"] - .1, None, "pop", rot=-2),
        El(lambda fr: logo("om", 380), 300, 900, K["om"] - .1, None, "pop", rot=-5),
        El(stampl("CORRUPTION", ROUGE, 96), 330, 1180, K["corruption"] - .03, None, "stamp", rot=-8),
        El(lambda fr: logo("psg", 380), 780, 1350, K["paris2"] - .1, None, "slide_r", rot=4, dist=700),
        El(tag("2e", 70, JAUNE), 950, 1180, K["deuxieme"] - .05, None, "pop", rot=8),
        El(marker("« NON MERCI. »", "pqnon", 80), CX, 1660, K["reclame"] - .05, None, "slide_l", rot=-2)]
@scene(SC_T["om"], trans="tear", td=.22)
def s_om(L, fr, t):
    paper_fill(L, (238, 230, 212), "om")
    if t > K["titre"] - .1:                                      # le titre (coupe) s'envole de l'OM
        v = M.spring(t - K["titre"] + .1, .45, 13); gone = M.ease_in(clamp((t - K["corruption"])/.5))
        put(L, cup_gold(300), 640 + 600*gone, 820 - 700*gone + 6*math.sin(t*3), v, 25*gone)
    M.draw_all(L, fr, t, E_OM)
    if t > K["reclame"]:                                         # le PSG secoue la tête : non
        pass
CAMS["s_om"] = [(SC_T["om"], CX, 900, 1.0), (K["om"], 420, 950, 1.12), (K["corruption"], 400, 1000, 1.16), (K["paris2"], 640, 1300, 1.06), (K["reclame"], CX, 1250, 1.02)]
# --- 9. Un championnat sans champion : socle vide, toiles d'araignée
E_V = words(lambda w, i: KW(w, NOIR if w != "SANS CHAMPION" else ROUGE, BLANC, 110), [("RÉSULTAT :", K["resultat"] - .05), ("UN CHAMPIONNAT", K["championnat"] - .1), ("SANS CHAMPION", K["sans"])],
            CX, 560, maxw=900)
@scene(SC_T["vide"], trans="whip", td=.18)
def s_vide(L, fr, t):
    paper_fill(L, (40, 30, 34), "vide"); rays(L, (CX, 1100), t, .4, 12, 1500, (90, 60, 50), .1, .2)
    u = M.spring(t - SC_T["vide"] - .05, .55, 11); put(L, shadowed(scale_stand(), "stand"), CX, lerp(2300, 1350, u), 1.1)
    c = M.ease_out((t - K["sans"])/1.2); cobweb(L, CX - 30, 900, 240*c, 1); cobweb(L, 0, 300, 380*c, 1)
    for k in range(18):
        yy = (t*60 + k*97) % 1500 + 300; ImageDraw.Draw(L).ellipse([(k*61) % W, yy, (k*61) % W + 5, yy + 5], fill=(230, 210, 200))
    M.draw_all(L, fr, t, E_V)
CAMS["s_vide"] = [(SC_T["vide"], CX, 1000, 1.0), (K["championnat"], CX, 900, 1.06), (K["sans"], CX, 1000, 1.06)]
# --- 10. Weah, Ginola, Raí, une Coupe d'Europe… Ronaldinho
E_ST = [El(lambda fr: CUT("weah", 820), 300, 1500, K["weah"] - .1, K["ginola"] - .1, "rise", "slide_l", rot=-3, dist=1300),
        El(marker("WEAH", "pqweah", 90), 300, 1560, K["weah"] + .05, K["ginola"] - .1, "slide_l", "slide_l", rot=-3),
        El(lambda fr: CUT("ginola", 820), 780, 1500, K["ginola"] - .1, K["rai"] - .1, "rise", "slide_r", rot=3, dist=1300),
        El(marker("GINOLA", "pqgino", 90), 780, 1560, K["ginola"] + .05, K["rai"] - .1, "slide_r", "slide_r", rot=3),
        El(lambda fr: CUT("rai", 820), 300, 1500, K["rai"] - .1, K["coupe2"] - .05, "rise", "slide_l", rot=-3, dist=1300),
        El(marker("RAÍ", "pqrai", 90), 300, 1560, K["rai"] + .05, K["coupe2"] - .05, "slide_l", "slide_l", rot=-3),
        El(lambda fr: cup_gold(380), 760, 1100, K["coupe2"] - .1, K["bresilien"] - .1, "drop", "fly", rot=4),
        El(tag("COUPE DES COUPES 1996", 56, JAUNE), 700, 1400, K["coupe2"] + .1, K["bresilien"] - .1, "pop", "fly", rot=-3),
        El(tag("UN JEUNE BRÉSILIEN…", 60, BLANC), CX, 560, K["bresilien"] - .25, None, "pop", rot=2),
        El(lambda fr: CUT("ronaldinho", 1100), CX, 1700, K["ronaldinho"] - .25, None, "rise", rot=-2, dist=1500),
        El(KW("RONALDINHO", JAUNE, NOIR, 110), CX, 1560, K["ronaldinho"] - .02, None, "stamp", rot=-4)]
@scene(SC_T["stars"], trans="tear", td=.22)
def s_stars(L, fr, t):
    stripes_bg(L, key="stars", t=t); dark(L, .3)
    if t > K["ronaldinho"]: sparks_burst(L, t, K["ronaldinho"], CX, 1000, 16, (255, 230, 120), 420)
    M.draw_all(L, fr, t, E_ST)
CAMS["s_stars"] = [(SC_T["stars"], CX, 1100, 1.0), (K["weah"], 380, 1150, 1.1), (K["ginola"], 700, 1150, 1.1), (K["rai"], 380, 1150, 1.1),
                   (K["coupe2"], 700, 1100, 1.06), (K["ronaldinho"], CX, 1100, 1.0)]
# --- 11. 2008 : la survie à la dernière journée, à Sochaux
E_08 = [El(mono("2008", 70), CX, 420, K["y2008"], None, "pop", rot=-3),
        El(KW("SA SURVIE", ROUGE, BLANC, 120), CX, 600, K["survie"] - .05, None, "stamp", rot=-3),
        El(tag("DERNIÈRE JOURNÉE", 62, JAUNE), CX, 770, K["derniere2"] - .05, None, "pop", rot=2),
        El(lambda fr: sign("SOCHAUX", 440), 800, 1560, K["sochaux"] - .1, None, "drop", rot=4, dist=900)]
@scene(SC_T["y08"], trans="tear", td=.22)
def s_08(L, fr, t):
    paper_fill(L, (52, 50, 58), "s08"); d = ImageDraw.Draw(L)
    d.rectangle([0, 1180, W, 1360], fill=(170, 40, 46)); text_c(d, CX, 1270, "ZONE DE RELÉGATION", font("title", 62), BLANC)
    sh = 9*math.sin(t*34)*clamp((t - K["survie"])/.4)
    put(L, logo("psg", 300), 300 + sh, 1030 + 70*clamp((t - K["survie"])/2.2), M.spring(t - K["y2008"] - .1, .45, 13), sh*.6)
    pts = []; base = 1640                                         # cœur qui s'affole
    for x in range(40, W - 40, 6):
        ph = (x/150 - t*(2 + 2*clamp((t - K["survie"])/1.5))) % 1; pts.append((x, base - (170 if .45 < ph < .5 else -70 if .5 < ph < .55 else 0)))
    d.line(pts, fill=(255, 90, 90), width=8)
    M.draw_all(L, fr, t, E_08)
CAMS["s_08"] = [(SC_T["y08"], CX, 900, 1.0), (K["survie"], CX, 900, 1.1), (K["derniere2"], 400, 1100, 1.1), (K["sochaux"], 700, 1350, 1.08)]
# --- 12. Amara Diané, deux fois : sauvé !
DIANE = foot.Player("diane", hair=(20, 16, 14), skin=(96, 62, 44))
E_DI = [El(marker("AMARA DIANÉ", "pqdia", 84), CX, 440, K["diane"] - .05, None, "slide_l", rot=-2),
        El(KW("×2", JAUNE, NOIR, 150), 860, 640, K["deux"] - .03, None, "stamp", rot=6),
        El(stampl("SAUVÉ !", (40, 150, 70), 190), CX, 1060, K["sauve"] - .05, None, "stamp", rot=-6)]
@scene(SC_T["diane"], trans="whip", td=.18)
def s_diane(L, fr, t):
    paper_fill(L, (58, 140, 76), "pitch3"); d = ImageDraw.Draw(L)
    for k in range(0, H, 220): d.rectangle([0, k, W, k + 110], fill=(70, 156, 88))
    foot.draw_goal(L, fr, 790, 1700, 520, 260, 0, 1, t)
    cheer = t > K["sauve"] - .2
    DIANE.draw(L, fr, 300, 1820, s=1.0, kit="psg", arms=(160, 160) if cheer else (40, 50), legs=(-30, 40) if not cheer else (10, -10), mood="happy", t=t)
    for k, t0 in enumerate((K["diane"] + .1, K["deux"] - .25)):
        u = clamp((t - t0)/.38)
        if 0 < u < 1: bx, by = arc((360, 1780), (790, 1620), 150, u); ball(L, fr, bx, by, .6, t, 1790)
        if t > t0 + .38: sparks_burst(L, t, t0 + .38, 790, 1620, 12, (255, 236, 140), 220)
    if cheer: fx.confetti(L, fr, 31, t - K["sauve"], 70, 3.0) if hasattr(fx, "confetti") else confetti(L, fr, 31, t - K["sauve"], 70, 3.0, None, (0, 0, W, H))
    M.draw_all(L, fr, t, E_DI)
CAMS["s_diane"] = [(SC_T["diane"], CX, 1200, 1.04), (K["diane"] + .4, 650, 1450, 1.08), (K["deux"], 650, 1450, 1.1), (K["sauve"], CX, 1100, 1.0)]
# --- 13. 2011 : le Qatar arrive… le vrai PSG, avant ou après ?
E_FIN = [El(tag("TROIS ANS PLUS TARD…", 60, BLANC), CX, 330, K["trois"], K["toi"] - .1, "pop", "fly", rot=-2),
         El(KW("ET TOI ?", JAUNE, NOIR, 120), CX, 470, K["toi"] - .05, None, "stamp", rot=-3),
         El(KW("LE VRAI PSG", NOIR, BLANC, 110), CX, 640, K["vrai"] - .05, None, "stamp", rot=2),
         El(KW("AVANT", NAVY, BLANC, 120), 280, 1080, K["avant"] - .03, None, "stamp", rot=-5),
         El(KW("APRÈS", PRED, BLANC, 120), 800, 1080, K["apres"] - .03, None, "stamp", rot=5),
         El(tag("OU", 60, BLANC), CX, 1240, K["avant"] + .3, None, "pop", rot=0),
         El(marker("DIS-LE EN COMMENTAIRE", "pqdis", 76), CX, 1480, K["dis"] - .05, None, "slide_l", rot=2)]
@scene(SC_T["fin"], trans="tear", td=.22)
def s_fin(L, fr, t):
    paper_fill(L, (110, 26, 44), "fin"); rays(L, (CX, 1000), t, .5, 14, 1600, (140, 40, 60), .1, .3)
    if t < K["toi"] + .1:
        v = M.spring(t - K["qatar2"] + .2, .5, 12); ex = M.ease_in((t - K["toi"] + .1)/.25) if t > K["toi"] - .1 else 0
        if v > .02: qatar_flag(L, CX, lerp(-400, 900, v) - 1200*ex, t, 1.0)
    if t > K["dis"]:
        y = 1600 + 16*abs(math.sin(t*6)); ImageDraw.Draw(L).polygon([(CX - 46, y), (CX + 46, y), (CX, y + 56)], fill=JAUNE)
    M.draw_all(L, fr, t, E_FIN)
CAMS["s_fin"] = [(SC_T["fin"], CX, 900, 1.0), (K["qatar2"], CX, 950, 1.08), (K["toi"], CX, 700, 1.04), (K["avant"], 420, 1050, 1.06), (K["apres"], 660, 1050, 1.06), (K["dis"], CX, 1150, 1.0)]

SC.sort(key=lambda s: s["t0"])
IMPACTS = [K["footix"], K["chaos"], K["radie"], K["double"], K["comptes"], K["egalise"], K["derniere"], K["embrasse"], K["premier"], K["troisun"], K["tete"] + .25,
           K["additionnel"], K["abonne"] + .18, K["corruption"], K["reclame"], K["sans"], K["ronaldinho"], K["survie"], K["deux"], K["sauve"], K["avant"], K["apres"]]
PUNCH = list(IMPACTS)
def punch(t): return 1 + sum(.06*math.exp(-((t - p)/.11)**2) for p in PUNCH if p - .4 < t < p + .5)
# ------------------------------------------------------------------ fil rouge : date + « N ANS AVANT LE QATAR »
DATES = [(SC_T["y78"], 1978), (SC_T["y82"], 1982), (SC_T["y93"], 1993), (SC_T["y08"], 2008), (K["trois"], 2011)]
def fil_rouge(cv, fr, t):
    if t < SC_T["y78"] or SC_T["quiz"] - .2 < t < SC_T["om"]: return
    t0, yr = [d for d in DATES if t >= d[0]][-1]; s = .6 + .4*M.spring(t - t0, .45, 16)
    mono(str(yr), 46, NOIR).draw(cv, fr, 150, 262, s, -3)
    n = 2011 - yr
    if n: LBL(f"{n} ANS AVANT LE QATAR", f"pqfr{n}", font("title", 38), BLANC, ROUGE, padx=14, pady=5, rough=2).draw(cv, fr, 560, 262, s, 2)
    else: LBL("LE QATAR ARRIVE", "pqfr0", font("title", 38), BLANC, (138, 21, 56), padx=14, pady=5, rough=2).draw(cv, fr, 560, 262, s, 2)
# ------------------------------------------------------------------ rendu + transitions (repris de rennes3.py)
def render_scene(i, fr, t):
    s = SC[i]; L = Image.new("RGBA", s["size"], (0, 0, 0, 255)); s["fn"](L, fr, t)
    cx, cy, z = M.cam_spring(CAMS[s["name"]], t); z *= punch(t)
    sx_, sy_, sr = M.trauma_offset(t, IMPACTS)
    return apply_cam(L, cx + 4*math.sin(t*.9) + sx_, cy + 3*math.cos(t*.7) + sy_, z, .3*math.sin(t*.6) + sr).convert("RGB")
def scene_at(t):
    k = 0
    for i, s in enumerate(SC):
        if t >= s["t0"]: k = i
    return k
def frame(fr, t):
    k = scene_at(t); s = SC[k]; cur = render_scene(k, fr, t)
    u = (t - s["t0"])/s["td"] if k else 1
    if u < 1:
        prev = render_scene(k - 1, fr, t); tr = s["trans"]; e = M.ease_io(u)
        if tr == "whip":
            off = int(W*e); out = Image.new("RGB", (W, H)); out.paste(prev, (-off, 0)); out.paste(cur, (W - off, 0))
            fx.whip_blur(out, -110*math.sin(math.pi*u), 0, 7); cur = out
        elif tr == "tear": tear_transition(cur, prev, u, "tear_v", k)
    fx.dust(cur, t, 22)
    cur = cur.convert("RGBA"); fx.vignette(cur, 90); fil_rouge(cur, fr, t)
    return cur.convert("RGB")
P = .05
def draw(cv, fr, t, T):
    tv = max(0.0, t - P); cv.paste(frame(fr, tv), (0, 0))
# ------------------------------------------------------------------ sons (pas de musique)
V5S = os.path.join(ROOT, "episodes", "lille_v5", "sfx"); RS = os.path.join(RENNES, "sfx"); BANK = os.path.join(ROOT, "assets", "sfx")
def X(t, name, g): return (P + t, name, g)
SFX = [X(K["footix"], "stamp", .35), X(K["psg"], "whoosh", .3), X(K["qatar"] + .15, "scratch", .3),
       X(SC_T["bill"], "whoosh", .3), X(K["paris1"], "scratch", .3), X(K["chaos"], "stamp", .4), X(K["magique"], "sparkle", .35),
       X(SC_T["y78"], "rip", .35), X(K["radie"], "gavel", .45),
       X(SC_T["motif"], "whoosh", .3), X(K["liquide"], "cash", .4), X(K["comptes"], "stamp", .4),
       X(SC_T["y82"], "rip", .35), X(K["finale"], "whistle", .3), X(K["rocheteau"] - .2, "kick", .45), X(K["egalise"] + .05, "goal_roar", .4),
       X(SC_T["bor"], "whoosh", .3), X(K["embrasse"], "crowd", .35), X(K["premier"], "sparkle", .4),
       X(SC_T["y93"], "rip", .35), X(K["tete"] - .1, "kick", .4), X(K["tete"] + .3, "goal_roar", .45),
       X(SC_T["quiz"], "whoosh", .3), X(K["qui"], "riser", .25), X(K["abonne"] + .25, "notif", .4), X(K["like"], "heart", .35),
       X(SC_T["om"], "rip", .35), X(K["corruption"], "gavel", .45), X(K["reclame"], "scratch", .3),
       X(SC_T["vide"], "whoosh", .3), X(K["sans"], "stamp", .35),
       X(SC_T["stars"], "rip", .35), X(K["weah"], "camera", .3), X(K["ginola"], "camera", .3), X(K["rai"], "camera", .3), X(K["ronaldinho"], "samba", .3),
       X(SC_T["y08"], "rip", .35), X(K["survie"], "heart", .4),
       X(SC_T["diane"], "whoosh", .3), X(K["diane"] + .05, "kick", .4), X(K["deux"] - .3, "kick", .4), X(K["sauve"] + .05, "goal_roar", .45),
       X(SC_T["fin"], "rip", .35), X(K["avant"], "stamp", .35), X(K["apres"], "stamp", .35), X(K["dis"], "notif", .4)]
SFX_DIR = "/tmp/claude-0/sfx_psgv3"
os.makedirs(SFX_DIR, exist_ok=True)
for nm in set(n for _, n, _ in SFX):
    src = os.path.join(BANK, nm + ".mp3") if os.path.exists(os.path.join(BANK, nm + ".mp3")) else None
    dst = os.path.join(SFX_DIR, nm + ".mp3")
    if src and not os.path.lexists(dst): os.symlink(src, dst)
SFX = [s for s in SFX if os.path.exists(os.path.join(SFX_DIR, s[1] + ".mp3"))]
SFX = fx.sfx_variants(SFX, SFX_DIR, SFX_DIR + "_v")
SCENES = [Scene("psg", TEXTE, draw, SFX, pad_in=P, pad_out=1.4)]

def stills(out, only=None):
    os.makedirs(out, exist_ok=True); ts = []
    for i, s in enumerate(SC):
        if only and s["name"] != only: continue
        t1 = SC[i + 1]["t0"] if i + 1 < len(SC) else K["fin"] + 1; n = 3 if not only else 8
        ts += [s["t0"] + (t1 - s["t0"])*(k + .6)/n for k in range(n)]
    ts = [0.0] + ts
    ims = []
    for t in ts:
        cv = Image.new("RGB", (W, H)); cv.paste(frame(int(t*FPS), t)); ims.append(cv.resize((216, 384)))
    cols = 11; rows = (len(ims) + cols - 1)//cols; sheet = Image.new("RGB", (216*cols, 414*rows), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        x, y = (k % cols)*216, (k//cols)*414; sheet.paste(im, (x, y + 30)); dd.text((x + 6, y + 4), f"{ts[k]:.2f}s", font=font("mono", 22), fill=(230, 230, 230))
    p = os.path.join(out, f"psgv2{'_' + only if only else ''}.jpg"); sheet.save(p, quality=82); return p
def cover(path):
    cv = Image.new("RGB", (W, H)); cv.paste(frame(int(1.2*FPS), 1.2)); cv.save(path, quality=92); return path

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--stills" in args:
        only = args[args.index("--stills") + 1] if len(args) > args.index("--stills") + 1 else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/claude-0/aud"), only)); sys.exit()
    out = os.path.join(ROOT, "output", SLUG); os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=[VOIX], sfx_dir=SFX_DIR + "_v", sfx_db=13.0, duck=.55, lufs=-14.0, crf=22, limit=True))
