"""LOSC v5 — refonte complète selon SCRIPT.md : une micro-scène par phrase, caméra qui cible l'action,
fil rouge (baromètre « santé du club » + date), transitions sans coupe sèche, assets maison (gfx.py, sfx.py).
Voix : lille_v4/voix/voix_v4.mp3 (0 crédit).

  python3 episodes/lille_v5/lille_v5.py --stills [scene]   -> planche d'audit (toutes les scènes ou une seule)
  python3 episodes/lille_v5/lille_v5.py output/lille_v5
"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "brest_ldc")); sys.path.insert(0, HERE)
from quiz import *
import foot, fx
from brest_ldc import marker
from gfx import *
from PIL import ImageChops

TITLE = "~/histoires $ ./losc"
SLUG = "lille_v5"
V4 = os.path.join(ROOT, "episodes", "lille_v4")
VOIX = os.path.join(V4, "voix", "voix_v4.mp3")
TEXTE = open(os.path.join(V4, "texte.txt")).read()
_W = json.load(open(os.path.join(V4, "mots.json")))
FZ = json.load(open(os.path.join(V4, "freeze.json"))); FZ0, FZD = FZ["freeze_start"], FZ["freeze_dur"]
def w(txt, n=1):
    k = 0
    for x in _W:
        if x["text"].strip(".,…!?:«» ").lower() == txt.lower():
            k += 1
            if k == n: return x["start"]
    raise KeyError(f"{txt} #{n}")

# ------------------------------------------------------------------ outils communs
def ease(u): u = clamp(u); return u*u*(3 - 2*u)
def eob(u, s=1.9): return ease_out_back(clamp(u), s)
def spring(t, t0, d=.5): return 0 if t < t0 else eob((t - t0)/d)
def wob(t, t0, amp=12, f=9, damp=5):                      # oscillation amortie (rotation d'un objet qui atterrit)
    return 0 if t < t0 else amp*math.sin((t - t0)*f)*math.exp(-(t - t0)*damp)
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
LOGO = {n: shadowed(sticker(n, h), ("L", n, h)) for n, h in (("lille", 620), ("psg", 300), ("ucl", 520), ("ligue2", 260))}
def logo(n, h):
    k = ("logo", n, h)
    if k not in _sh: _sh[k] = shadowed(sticker(n, h), k)
    return _sh[k]
def kword(txt, bg=NOIR, fg=BLANC, size=118): return LBL(txt, f"v5k{txt}{bg}{size}", font("title", size), fg, bg, padx=24, pady=6, rough=3)
def stampl(txt, col=ROUGE, size=150): return LBL(txt, f"v5s{txt}{size}", font("title", size), col, CREME, padx=34, pady=6, rough=2)
def tag(txt, size=60, bg=BLANC, fg=NOIR): return LBL(txt, f"v5t{txt}{size}{bg}", font("title", size), fg, bg, padx=24, pady=8, rough=2)
def mono(txt, size=64, bg=NOIR, fg=BLANC): return LBL(txt, f"v5m{txt}{size}{bg}", font("mono", size), fg, bg, padx=18, pady=6, rough=2)
def slam_in(L, fr, lab, t, t0, x, y, rot=0, d=.2):
    if t >= t0: lab.draw(L, fr, x, y, 1 + .5*(1 - eob((t - t0)/d, 2.2)) if t - t0 < d else 1, rot + wob(t, t0, 4, 14, 8))
_tex = {}
def paper_fill(L, col, key):
    """Papier texturé de la taille du calque (gouache + grain), mis en cache."""
    k = (key, L.size, col)
    if k not in _tex:
        w_, h_ = L.size; rng = np.random.default_rng(abs(hash(key)) % 999)
        g = np.asarray(Image.fromarray((rng.random((h_//24 + 2, w_//24 + 2))*255).astype(np.uint8)).resize((w_, h_), Image.BICUBIC), np.float32)/255
        a = np.zeros((h_, w_, 3), np.float32); a[:] = col; a *= (.93 + .12*g)[..., None]
        sp = rng.random((h_, w_)).astype(np.float32); a += ((sp > .965)*14 - (sp < .03)*12)[..., None]
        _tex[k] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    L.paste(_tex[k], (0, 0))
def vgrad(L, y0, y1, c0, c1):
    d = ImageDraw.Draw(L)
    for y in range(int(y0), int(y1), 6):
        u = (y - y0)/(y1 - y0); d.rectangle([0, y, L.width, y + 6], fill=tuple(int(lerp(a, b, u)) for a, b in zip(c0, c1)))
def dark(L, a):
    if a > .01: L.alpha_composite(Image.new("RGBA", L.size, (8, 6, 14, int(255*clamp(a)))))
def marker_line(L, p0, p1, u, col=ROUGE, wd=14):
    if u <= 0: return
    ImageDraw.Draw(L).line([p0, (lerp(p0[0], p1[0], clamp(u)), lerp(p0[1], p1[1], clamp(u)))], fill=col, width=wd)
def marker_circle(L, cx, cy, rx, ry, u, col=ROUGE, wd=12):
    if u <= 0: return
    n = int(60*clamp(u)); pts = [(cx + rx*math.cos(-1.3 + 2.25*math.pi*k/60), cy + ry*math.sin(-1.3 + 2.25*math.pi*k/60)) for k in range(n + 1)]
    if len(pts) > 1: ImageDraw.Draw(L).line(pts, fill=col, width=wd)

# personnages papier (génériques, pas de visages réels)
foot.KITS["lille"] = dict(kind="plain", c1=(214, 16, 40), sleeve=(214, 16, 40), shorts=(18, 30, 78), socks=(214, 16, 40), trim=(250, 250, 246))
foot.KITS["lille_gk"] = dict(kind="plain", c1=(46, 170, 96), sleeve=(46, 170, 96), shorts=(30, 30, 34), socks=(46, 170, 96), trim=(250, 250, 246))
foot.KITS["coach_navy"] = dict(kind="plain", c1=(24, 34, 70), sleeve=(24, 34, 70), shorts=(24, 34, 70), socks=(24, 34, 70), trim=(214, 16, 40), pants=True)
HZ = foot.Player("v5hazard", hair=(84, 54, 32))
VAHID = foot.Player("v5vahid", hair=(214, 214, 218))
RUDI = foot.Player("v5rudi", hair=(160, 160, 166))
MAIGNAN = foot.Player("v5maignan", hair=(26, 22, 20), skin=(112, 74, 52))
YILMAZ = foot.Player("v5yilmaz", hair=(38, 30, 26), beard_col=(38, 30, 26))
GALTIER = foot.Player("v5galtier", hair=(130, 130, 136), hair_style="bald")
LOSCP = foot.Player("v5loscp", hair=(60, 40, 28))
PSGP = foot.Player("v5psgp", hair=(36, 28, 24))
def player_rot(L, fr, pl, x, y, rot, s=1.0, **kw):
    """Joueur dessiné sur un calque puis tourné (plongeon, chute). (x, y) = pieds avant rotation, pivot = bassin."""
    lay = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); pl.draw(lay, fr, 450, 700, s=s, **kw)
    lay.info["anchor"] = (450, 700 - 230*s); blit_sxy(L, lay, x, y - 230*s, 1, 1, rot)

# ------------------------------------------------------------------ fil rouge : baromètre + date
GAUGE = [(0, .08), (2.9, 1.0), (7.6, .5), (13.5, .92), (15.4, .12), (19.2, .6), (21.4, .8), (29.8, .95), (31.7, .2), (33.8, .03),
         (37.0, .55), (41.8, .4), (44.3, 1.0)]
def gauge_val(t):
    v = GAUGE[0][1]
    for i, (t0, val) in enumerate(GAUGE):
        if t >= t0:
            prev = GAUGE[i - 1][1] if i else val; v = prev + (val - prev)*eob((t - t0)/.6, 2.4)
    return v + .015*math.sin(t*23)*(1 if v < .15 else .3)
DATES = [(0, 2020, "DÉC. 2020"), (2.4, 2021, "MAI 2021"), (7.05, 1944, None), (12.52, 1946, None), (15.2, 1997, None), (17.03, 2000, None),
         (19.86, 2001, None), (22.45, 2005, None), (26.73, 2011, None), (32.38, 2020, "FIN 2020"), (36.4, 2021, "2020-21")]
def date_txt(t):
    cur = DATES[0]
    for i, dd in enumerate(DATES):
        if t >= dd[0]:
            prev = DATES[i - 1] if i else dd; cur = dd
            dur = .65 if abs(dd[1] - prev[1]) > 10 else .35; u = clamp((t - dd[0])/dur)
            if u < 1: return str(int(round(lerp(prev[1], dd[1], ease(u))))), True
    return (cur[2] or str(cur[1])), False
def fil_rouge(cv, fr, t):
    gb = gauge_base(); put(cv, gb, 150, 280, .62, -3)
    a = math.pi + math.pi*clamp(gauge_val(t), 0, 1); rot = -math.degrees(a) - 90
    put(cv, gauge_needle(), 150, 280, .62, rot)
    txt, rolling = date_txt(t)
    if t > 1.3: mono(txt, 46, ROUGE if rolling else NOIR).draw(cv, fr, 400 + 6*rolling*math.sin(t*60), 262, 1.0, -3)

# ------------------------------------------------------------------ caméra par scène
def camk(keys, t):
    """keys = [(t, cx, cy, z)] interpolés (ease) ; renvoie cx, cy, z."""
    if t <= keys[0][0]: return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            u = ease((t - a[0])/(b[0] - a[0])); return tuple(lerp(p, q, u) for p, q in zip(a[1:], b[1:]))
    return keys[-1][1:]
def apply_cam(L, cx, cy, z, rot=0.0):
    """Recadre le calque de scène (taille quelconque) autour de (cx, cy) au zoom z -> image W x H."""
    z = max(z, max(W/L.width, H/L.height)); bw, bh = W/z, H/z
    x0 = min(max(cx - bw/2, 0), L.width - bw); y0 = min(max(cy - bh/2, 0), L.height - bh)
    im = L.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.BICUBIC)
    if abs(rot) > .05: im = im.rotate(rot, resample=Image.BICUBIC, fillcolor=im.getpixel((2, 2)))
    return im
PUNCH = []
def punch(t): return 1 + sum(.06*math.exp(-((t - p)/.11)**2) for p in PUNCH if p - .4 < t < p + .5)

# ================================================================== SCÈNES (t = temps voix)
SC = []
def scene(t0, size=(W, H), trans="cut", td=.3):
    def deco_(fn): SC.append(dict(t0=t0, fn=fn, size=size, trans=trans, td=td, name=fn.__name__)); return fn
    return deco_

# --- 0. HOOK : l'écusson croule sous les billets
BILLS = [(random.Random(i).uniform(120, 960), -0.7 + i*.045, random.Random(i + 50).uniform(-40, 40)) for i in range(34)]
@scene(0.0)
def s_hook(L, fr, t):
    paper_fill(L, (150, 12, 28), "hookbg"); rays(L, (CX, 1000), t, .8, 16, 1700, (120, 6, 20), .12, .3)
    put(L, LOGO["lille"], CX, 1010 + 6*math.sin(t*3), 1 + .02*math.sin(t*2.2), -3 + 1.5*math.sin(t*1.7))
    for i, (x, t0, r) in enumerate(BILLS):                 # pluie de billets qui s'entassent devant l'écusson
        land = 1420 - (i % 12)*14 - (i//12)*26; u = clamp((t - t0)/.55)
        if t < t0: continue
        y = lerp(-150, land, u*u); rr = r + (1 - u)*200*math.sin(i)
        put(L, bill(i % 3), x if u < 1 else x*.8 + CX*.2, y, .95, rr if u < 1 else r*.3)
    fx.kinetic(L, fr, t, [("LILLE", -.4), ("CROULE", w("croule") - .02), ("SOUS LES", w("sous") - .02), ("DETTES…", w("dettes") - .02)], CX, 740,
               lambda x, i: kword(x, ROUGE if i == 3 else (JAUNE if i == 1 else NOIR), NOIR if i == 1 else BLANC, 150), maxw=960)
    beat = (t % .55)/.55; k = math.exp(-beat*6)*.35
    if k > .02: L.paste(Image.new("RGBA", L.size, (255, 0, 30, 255)), (0, 0), fx._vig_mask(int(255*k)).resize(L.size))
CAM_HOOK = [(0, CX, 960, 1.12), (1.3, CX, 1000, 1.0)]

# --- 1. CALENDRIER : six mois plus tard
MONTHS = [("DÉC.", "2020", True), ("JANV.", "2021", False), ("FÉV.", "2021", False), ("MARS", "2021", False), ("AVR.", "2021", False), ("MAI", "2021", True)]
TEARS = [1.42, 1.58, 1.73, 1.88, 2.03]
@scene(1.30, trans="whip_up", td=.28)
def s_cal(L, fr, t):
    paper_fill(L, (238, 226, 200), "calbg")
    fx.kinetic(L, fr, t, [("6 MOIS", w("six") - .02), ("PLUS TARD…", w("plus") - .02)], CX, 600, lambda x, i: kword(x, NOIR, BLANC, 120))
    put(L, cal_back(), CX, 1180, 1.0)
    n = sum(1 for x in TEARS if t >= x)
    put(L, cal_page(*MONTHS[min(n + 1, 5)]) if n < 5 else cal_page(*MONTHS[5]), CX, 1192, 1.0)
    if n < 5: put(L, cal_page(*MONTHS[n]), CX, 1192, 1.0)
    for i, t0 in enumerate(TEARS):                         # pages arrachées qui s'envolent
        u = (t - t0)/.45
        if 0 <= u < 1: put(L, cal_page(*MONTHS[i]), CX + 700*u**1.3, 1192 + 200*u + 500*u*u, 1.0 - .2*u, -50*u, 1 - u**3)
CAM_CAL = [(1.3, CX, 1000, 1.0), (2.1, CX, 1100, 1.12), (2.4, CX, 1150, 1.4)]

# --- 2. TROPHÉE : champion de France
@scene(2.40, trans="zoom_through", td=.35)
def s_trophy(L, fr, t):
    paper_fill(L, (206, 18, 36), "trbg"); rays(L, (CX, 1000), t, 1.0, 20, 1800, (236, 60, 70), .12, .5)
    u = eob((t - 2.42)/.6, 1.6); put(L, trophy_league(700), CX, lerp(2300, 1420, u), 1.0, wob(t, 2.9, 3, 10, 5))
    if t > 2.62: put(L, logo("lille", 300), CX, 1330 + 20*(1 - eob((t - 2.62)/.3)), eob((t - 2.62)/.3, 2.5), -4)
    fx.kinetic(L, fr, t, [("CHAMPION", w("champion") - .02), ("DE FRANCE !", w("de") - .02 if w("de") > 3 else 3.25)], CX, 560,
               lambda x, i: kword(x, JAUNE, NOIR, 130))
    confetti(L, fr, "v5cf1", t - 2.91, 90, 3.0, [JAUNE, BLANC, NAVY, ROUGE])
    fx.shockwave(L, t, 2.91, CX, 1100, .5, 900)
CAM_TROPHY = [(2.4, CX, 1000, 1.25), (2.95, CX, 960, 1.0), (4.05, CX, 960, 1.04)]

# --- 3. CLASSEMENT : devant le PSG
@scene(4.05, trans="whip", td=.25)
def s_table(L, fr, t):
    paper_fill(L, (240, 234, 220), "tbbg"); d = ImageDraw.Draw(L)
    for y in range(240, H, 64): d.line([(0, y), (W, y)], fill=(196, 210, 230), width=2)
    d.line([(150, 0), (150, H)], fill=(230, 140, 140), width=3)
    mono(fx.typed_cursor("CLASSEMENT 2020-21", t, 4.08, 30), 56).draw(L, fr, CX, 600, 1, -2)
    sw = ease((t - 4.55)/.45)                               # dépassement : LOSC passe devant
    yL, yP = lerp(960, 790, sw), lerp(790, 960, sw); arc_ = -60*math.sin(math.pi*sw)
    enter = lambda t0: (1 - eob((t - t0)/.35))*-1000
    put(L, table_row(0, "PSG", 0, NAVY, "psg"), CX + enter(4.1) + 30*math.sin(math.pi*sw), yP, 1.0)
    put(L, table_row(0, "LOSC", 0, ROUGE, "lille"), CX + enter(4.18) + arc_*0, yL + arc_, 1 + .08*math.sin(math.pi*sw), 2*math.sin(math.pi*sw))
    for (yy, rank, pts, ox) in ((yL + arc_, "1" if sw > .5 else "2", 80 + int(3*clamp((t - 4.6)/.5)), enter(4.18)), (yP, "2" if sw > .5 else "1", 82, enter(4.1))):
        d = ImageDraw.Draw(L); x0 = CX + ox
        text_c(d, x0 - 345, yy, rank, font("title", 84), BLANC); text_c(d, x0 + 305, yy, str(pts), font("title", 72), NOIR)
    for nm, x, y, t0, r in (("NEYMAR", 330, 1230, w("neymar") - .05, -4), ("MBAPPÉ", 740, 1280, w("mbappé") - .05, 3)):
        if t < t0: continue
        s = 1 + .4*(1 - eob((t - t0)/.22)); put(L, pin_tag(nm, 64), x, y, s, r + wob(t, t0, 6, 12, 6))
        tw = font("title", 64).getlength(nm)/2 + 20; marker_line(L, (x - tw, y + 8), (x + tw, y - 6), (t - t0 - .3)/.25, ROUGE, 12)
    if t > w("mbappé") + .5: slam_in(L, fr, stampl("BATTUS", ROUGE, 110), t, w("mbappé") + .5, CX, 1420, -8)
CAM_TABLE = [(4.05, CX, 960, 1.0), (4.5, CX, 900, 1.12), (5.0, CX, 920, 1.1), (5.3, 420, 1150, 1.15), (5.75, 680, 1180, 1.15), (6.2, CX, 1080, 1.02)]

# --- 4. ? + REMBOBINAGE
@scene(6.57, trans="glitch", td=.18)
def s_question(L, fr, t):
    paper_fill(L, (26, 22, 32), "qbg")
    ransom_line(L, "COMMENT", 420, 160, seed=4, fr=fr); ransom_line(L, "C'EST POSSIBLE ?", 1480, 110, seed=9, fr=fr)
    yq = lerp(-400, 950, eob((t - 6.6)/.35, 1.4)); put(L, qmark(), CX, yq, 1.0, wob(t, 6.95, 14, 7, 3))
    if t > 7.02:                                              # rembobinage
        u = clamp((t - 7.02)/.72); a = np.asarray(L.convert("RGB")).copy()
        for k in range(14):
            y0 = int((k*137 + fr*53) % H); h_ = 18 + (k*7) % 30; a[y0:y0 + h_] = np.roll(a[y0:y0 + h_], int(60*math.sin(k + fr)), 1)
        L.paste(Image.fromarray(a).convert("RGBA"), (0, 0)); dark(L, .35)
        d = ImageDraw.Draw(L)
        for y in range(0, H, 6): d.line([(0, y), (W, y)], fill=(0, 0, 0), width=2)
        yr = int(round(lerp(2021, 1944, ease(u))))
        mono(str(yr), 230, ROUGE, BLANC).draw(L, fr, CX, 950, 1.0, -2)
        mono("◀◀ REMBOBINAGE", 50, NOIR, BLANC).draw(L, fr, CX, 1180, 1.0, 0)
CAM_Q = [(6.57, CX, 960, 1.0), (7.0, CX, 960, 1.08), (7.74, CX, 960, 1.0)]

# --- 5. 1944 : rivaux, fusion, Dogues
@scene(7.74, trans="flash", td=.15)
def s_1944(L, fr, t):
    paper_fill(L, (212, 186, 142), "sepia")
    slam_in(L, fr, stampl("1944", (110, 70, 40), 220), t, 7.78, CX, 640, -4)
    if t < w("deux") + .3:                                   # archives : vieux ballon qui roule + film qui saute
        u = clamp((t - 7.9)/2.0); bx = lerp(-120, 760, ease(u))
        foot.draw_ball(L, fr, bx, 1330 - 30*abs(math.sin(u*9))*(1 - u), 1.6, bx*1.2)
        mono(fx.typed_cursor("LILLE, NORD", t, 8.0, 14), 50, (110, 70, 40), CREME).draw(L, fr, CX, 820, 1, 2)
        if fr % 7 == 0: ImageDraw.Draw(L).line([((fr*37) % W, 0), ((fr*37) % W + 10, H)], fill=(120, 96, 70), width=3)
        if fr % 11 < 2: L.alpha_composite(Image.new("RGBA", L.size, (255, 240, 210, 40)))
    for k in range(14):                                      # poussière d'archives
        u = (t*.15 + k*.071) % 1; ImageDraw.Draw(L).ellipse([(k*173) % W, H*(1 - u), (k*173) % W + 5, H*(1 - u) + 5], fill=(250, 236, 200))
    tf = w("fusionnent"); mg = ease((t - tf)/.32)
    lunge = 40*max(0, math.sin((t - w("rivaux"))*18))*(w("rivaux") < t < w("rivaux") + .5)
    if t < tf + .32:
        xo = lerp(-700, 0, eob((t - w("deux") + .05)/.35)) if t > w("deux") - .1 else -900
        xf = lerp(700, 0, eob((t - w("clubs") + .05)/.35)) if t > w("clubs") - .1 else 900
        s_ = 1 - .5*mg
        put(L, pennant("OLYMPIQUE\nLILLOIS", ROUGE), lerp(110, 260, mg) + xo + lunge, lerp(900, 1020, mg), s_, -4 + 8*mg)
        put(L, pennant("SC FIVES", NAVY, True), lerp(970, 820, mg) + xf - lunge, lerp(1150, 1020, mg), s_, 4 - 8*mg)
        if w("rivaux") - .05 < t < tf: put(L, bolt(), CX + 10*math.sin(fr), 1030, 1.1 + .15*(fr % 2), 8*(fr % 2))
    else:
        put(L, logo("lille", 520), CX, 1020, eob((t - tf - .32)/.35, 2.4), wob(t, tf + .32, 6, 9, 4))
    fx.shockwave(L, t, tf + .3, CX, 1020, .5, 800)
    if tf + .26 < t < tf + .4: L.alpha_composite(Image.new("RGBA", L.size, (255, 250, 230, int(255*(1 - abs(t - tf - .33)/.07)))))
    fx.kinetic(L, fr, t, [("LES DOGUES", w("dogues") - .1), ("SONT NÉS", w("sont") - .02)], CX, 1560, lambda x, i: kword(x, ROUGE if i == 0 else NOIR, BLANC, 110))
    for k in range(7):                                        # traces de pattes qui traversent
        tk = w("dogues") + k*.12
        if t > tk: put(L, paw(), 120 + k*140, 1760 - k*20 + (k % 2)*50, 1.2*eob((t - tk)/.15), -70, clamp(1.6 - (t - tk)*.4))
CAM_1944 = [(7.74, CX, 960, 1.0), (9.9, 330, 950, 1.15), (10.15, 760, 1100, 1.15), (10.4, CX, 1000, 1.0), (11.2, CX, 1060, 1.05), (12.5, CX, 1100, 1.0)]

# --- 6. ÉTAGÈRE 1946 : doublé
@scene(12.52, trans="whip", td=.25)
def s_1946(L, fr, t):
    paper_fill(L, (120, 34, 36), "wall"); d = ImageDraw.Draw(L)
    for x in range(0, W, 90): d.line([(x, 0), (x, H)], fill=(108, 28, 30), width=30)
    put(L, shelf("1946"), CX, 1250, 1.15)
    if t < w("doublé") - .05: fx.kinetic(L, fr, t, [("DEUX ANS", 12.5), ("PLUS TARD…", w("plus", 2) - .02)], CX, 600, lambda x, i: kword(x, NOIR, BLANC, 110))
    else: slam_in(L, fr, kword("DOUBLÉ !", JAUNE, NOIR, 150), t, w("doublé") - .03, CX, 600, -4)
    for spr, x, t0 in ((cup_gold(420), 330, w("coupe") - .1), (trophy_league(470), 740, w("championnat") - .1)):
        if t < t0: continue
        u = clamp((t - t0)/.22); y = lerp(500, 1222, u*u)
        put(L, spr, x, y + (0 if u < 1 else -12*abs(math.sin((t - t0 - .22)*14))*math.exp(-(t - t0 - .22)*8)), 1.0, wob(t, t0 + .22, 4, 12, 6))
    for nm, x, t0 in (("COUPE", 330, w("coupe")), ("CHAMPIONNAT", 740, w("championnat"))):
        if t > t0 + .1: tag(nm, 44, CREME).draw(L, fr, x, 1390, eob((t - t0 - .1)/.25), -2)
CAM_1946 = [(12.52, CX, 1000, 1.0), (13.5, CX, 900, 1.02), (13.75, 360, 1050, 1.18), (14.1, 720, 1050, 1.18), (14.6, CX, 1000, 1.03)]

# --- 7. MER : naufrage puis remontée (une seule scène haute)
SEA_H = 3500; OY = 500
def boat_pos(t):
    ts, tr0, tr1 = w("sombre") - .2, w("remonter") - .25, w("remonter") + .6
    if t < ts: return OY + 1010 + 10*math.sin(t*3), 4*math.sin(t*2.5)
    if t < tr0:
        u = ease((t - ts)/1.4); return OY + lerp(1010, 2620, u), lerp(0, 24, u)
    u = ease((t - tr0)/(tr1 - tr0)); return OY + lerp(2620, 1010, u), lerp(24, 0, u)
@scene(14.66, size=(W, SEA_H), trans="tear", td=.3)
def s_sea(L, fr, t):
    vgrad(L, 0, OY + 1000, (120, 150, 190), (214, 224, 234)); vgrad(L, OY + 1000, SEA_H, (40, 86, 150), (8, 16, 40))
    d = ImageDraw.Draw(L)
    d.rectangle([0, OY + 960, 420, OY + 1040], fill=BOIS); d.rectangle([60, OY + 1040, 90, OY + 1400], fill=BOIS2); d.rectangle([330, OY + 1040, 360, OY + 1400], fill=BOIS2)
    put(L, sign("DIVISION 2"), 760, OY + 2620, 1.1, 4)
    for k in range(9):                                        # algues
        x = 60 + k*125; d.line([(x + 20*math.sin(t*2 + k + yy/60), OY + 2950 - yy) for yy in range(0, 260, 20)], fill=(30, 90, 70), width=10)
    by, br = boat_pos(t); put(L, boat(), 400, by, 1.0, br)
    if w("sombre") - .2 < t < w("remonter"):                  # bulles
        for k in range(10):
            u = ((t*.9 + k*.1) % 1); d.ellipse([400 + 60*math.sin(k*3 + t*4) - 9, by - 300*u - 9, 400 + 60*math.sin(k*3 + t*4) + 9, by - 300*u + 9], outline=(200, 230, 250), width=3)
    if t > w("en", 2) - .2:                                     # le coach et le treuil sur le ponton
        tv = w("vahid") - .2; a_ = 1
        put(L, winch(), 230, OY + 900, 1.0)
        crank = (t - w("remonter") + .25)*14 if t > w("remonter") - .25 else 0
        put(L, winch_handle(), 330, OY + 900, 1.0, -math.degrees(crank))
        ImageDraw.Draw(L).line([(250, OY + 930), (420, OY + 960), (400, by - 280)], fill=(210, 190, 150), width=5)
        VAHID.draw(L, fr, 130, OY + 965, s=.72, kit="suit", arms=(20, 70 if t > w("remonter") - .25 else 20), mood="normal", t=t, look=(1, 0))
        if t > tv: put(L, pin_tag("VAHID HALILHODZIC", 50), 380, OY + 340, eob((t - tv)/.25), -3)
    wave_strip(L, OY + 1030, t, (60, 110, 170), 22, 200, 50, 0, OY + 1110); wave_strip(L, OY + 1060, t, (40, 86, 150), 18, 160, -70, 1.3, OY + 1130)
    if 0 < t - (w("remonter") + .4) < 1.2: drops(L, "v5dr", t - (w("remonter") + .4), [(330, by - 40), (470, by - 30)], 5, (190, 220, 250), 10, 500)
    dark(L, 0)
CAM_SEA = [(14.66, CX, OY + 960, 1.0), (15.0, 450, OY + 1050, 1.1), (16.6, 450, OY + 2350, 1.05), (17.0, 450, OY + 2350, 1.0), (17.6, 400, OY + 1400, 1.0),
           (17.9, 380, OY + 760, 1.12), (18.8, 400, OY + 900, 1.05), (19.5, 420, OY + 820, 1.0), (19.86, CX, OY + 820, 1.0)]

# --- 8. NUIT D'EUROPE
@scene(19.86, trans="whip_up", td=.28)
def s_ucl(L, fr, t):
    vgrad(L, 0, H, (10, 16, 46), (24, 36, 90)); d = ImageDraw.Draw(L)
    for k in range(60): d.ellipse([(k*97) % W, (k*53) % 700, (k*97) % W + 4, (k*53) % 700 + 4], fill=(220, 220, 255))
    for side in (-1, 1): rays(L, (CX + side*600, 1900), t*(.5 + .2*side), .5, 3, 2300, (255, 250, 210), .05, .6*side)
    d.polygon([(0, 1500), (W, 1500), (W, H), (0, H)], fill=(12, 14, 30))
    for k in range(40): d.ellipse([(k*67) % W, 1520 + (k*31) % 300, (k*67) % W + 8, 1528 + (k*31) % 300], fill=(255, 240, 180) if (k + fr//4) % 5 == 0 else (60, 60, 90))
    put(L, LOGO["ucl"], CX, lerp(1600, 980, eob((t - 20.0)/.5, 1.5)), 1.0, 6*math.sin(t*1.5))
    if t > w("lille", 3) - .05:
        u = clamp((t - w("lille", 3) + .05)/.35); put(L, logo("lille", 240), lerp(-100, 780, ease(u)), 1400 - 160*math.sin(math.pi*u), 1.0, 360*u if u < 1 else 0)
    fx.kinetic(L, fr, t, [("LIGUE", w("ligue") - .02), ("DES", w("des") - .02), ("CHAMPIONS !", w("champions") - .02)], CX, 600,
               lambda x, i: kword(x, BLANC, NAVY, 120))
    camera_flashes(L, fr, "v5fl", t - 21.0, 1.4, 12, (60, 1520, 1020, 1800))
CAM_UCL = [(19.86, CX, 960, 1.0), (21.3, CX, 1000, 1.12), (22.45, CX, 1020, 1.16)]

# --- 9. CENTRE DE FORMATION : le gamin devient Hazard
CONES = [260, 420, 580, 740]
def kid_pos(t):
    u = clamp((t - 22.6)/2.8); x = lerp(120, 880, u); y = 1300 + 70*math.sin(u*math.pi*4)
    if t > w("eden") - .1: x, y = lerp(x, CX, ease((t - w("eden") + .1)/.3)), lerp(y, 1340, ease((t - w("eden") + .1)/.3))
    return x, y
@scene(22.45, trans="tear", td=.3)
def s_train(L, fr, t):
    paper_fill(L, VERT, "pitch"); d = ImageDraw.Draw(L)
    for k in range(0, H, 220): d.rectangle([0, k, W, k + 110], fill=VERT2)
    d.line([(0, 1560), (W, 1560)], fill=BLANC, width=8)
    if t < w("eden") - .1: mono(fx.typed_cursor("CENTRE DE FORMATION", t, 22.48, 26), 54).draw(L, fr, CX, 600, 1, -2)
    for x in CONES: put(L, cone(), x, 1300 + 70*math.sin((x - 120)/760*math.pi*4) + 40, 1.2)
    x, y = kid_pos(t); te = w("eden") - .05; age = .42 if t < te else lerp(.42, 1.0, eob((t - te)/.4, 1.5))
    run = (t < te); legs = (25*math.sin(t*16), -25*math.sin(t*16)) if run else (0, 0)
    HZ.draw(L, fr, x, y + 100, s=1.25 if t < te else lerp(1.25, 1.45, clamp((t - te)/.4)), age=age, kit="lille", legs=legs, arms=(25, 25) if run else (12, 12), mood="happy", t=t)
    if run: foot.draw_ball(L, fr, x + 70, y + 90 - 20*abs(math.sin(t*8)), .9, t*400)
    if t > w("belge") - .05:
        flag_belgium(L, 820, 640, t, 1.0*eob((t - w("belge") + .05)/.3))
    if t > w("quatorze") - .05: put(L, pin_tag("14 ANS", 70), 280, 720, 1 + .4*(1 - eob((t - w("quatorze") + .05)/.22)), -5 + wob(t, w("quatorze"), 6, 12, 6))
    if te < t < te + .6: fx.shockwave(L, t, te, x, y - 150, .5, 500, (255, 236, 150))
    if t > w("hazard") - .05:
        put(L, logo_card(), 800, 1020, eob((t - w("hazard") + .05)/.3), 7)
        fx.wipe(L, fr, marker("EDEN HAZARD", "v5eh", 96), CX, 1480, t, w("hazard") - .02, -2)
CAM_TRAIN = [(22.45, CX, 960, 1.0), (22.9, 300, 1150, 1.12), (24.0, 520, 1150, 1.12), (25.3, 760, 1150, 1.12), (25.6, CX, 1180, 1.15), (26.2, CX, 1060, 1.0)]
_card = {}
def logo_card():
    if "c" not in _card:
        im = Image.open(A("lille", "hazard_card.png")).convert("RGBA"); im = im.resize((int(im.width*.55), int(im.height*.55)), Image.LANCZOS)
        _card["c"] = shadowed(center(im), "card")
    return _card["c"]

# --- 10. 2011 : le cadeau du doublé
@scene(26.73, trans="whip", td=.25)
def s_gift(L, fr, t):
    paper_fill(L, (244, 214, 150), "gold"); rays(L, (CX, 900), t, .8, 18, 1700, (252, 230, 170), .1, .3)
    if t < w("doublé", 2): slam_in(L, fr, stampl("2011", NOIR, 160), t, 26.75, CX, 620, -3)
    hand = 60 if t > w("offre") - .1 else 15
    HZ.draw(L, fr, 330, 1560, s=1.35, age=1, kit="lille", arms=(15, hand), mood="happy", t=t)
    if t > w("rudi") - .1:
        xr = lerp(1300, 800, eob((t - w("rudi") + .1)/.4)); RUDI.draw(L, fr, xr, 1560, s=1.35, kit="suit", arms=(15, 10), mood="happy", t=t, look=(-1, 0))
        if t > w("rudi") + .1: put(L, pin_tag("RUDI GARCIA", 50), 820, 920, eob((t - w("rudi") - .1)/.25), 3)
    if t > w("offre") - .1:
        u = eob((t - w("offre") + .1)/.35); bx, by = lerp(380, 560, u), 1180
        td_ = w("doublé", 2) - .05; op = clamp((t - td_)/.35)
        if t < td_ + .05: put(L, gift_box(), bx, by, .9*u + .1, wob(t, w("offre"), 5, 10, 5))
        if t < td_: put(L, gift_lid(), bx, by - 140, .9*u + .1)
        else:
            put(L, gift_box(), bx, by, .9); put(L, gift_lid(), bx + 260*op, by - 140 - 380*op + 500*op*op, .9, 120*op)
            for spr, dx in ((cup_gold(340), -130), (trophy_league(380), 130)):
                put(L, spr, bx + dx*op, by - 40 - 380*eob(op, 1.6), .25 + .75*op)
            confetti(L, fr, "v5cf2", t - td_, 70, 2.5, [JAUNE, ROUGE, NAVY, BLANC])
    if t > w("soixante-cinq") - .05:
        n = min(65, int(65*clamp((t - w("soixante-cinq") + .05)/.5)))
        kword(f"1er DOUBLÉ DEPUIS {n} ANS", NOIR, BLANC, 66).draw(L, fr, CX, 1470, 1, 2)
CAM_GIFT = [(26.73, CX, 1000, 1.0), (28.6, 520, 1150, 1.22), (29.7, 540, 1050, 1.15), (30.3, CX, 900, 1.02), (31.1, CX, 950, 1.0)]

# --- 11. DETTES : le ballon éclate, vendu
@scene(31.16, trans="tear", td=.28)
def s_debt(L, fr, t):
    paper_fill(L, (52, 38, 40), "debt")
    te = w("explosent") + .12
    put(L, logo("lille", 360), CX, 1250, 1.0, wob(t, te, 5, 20, 6))
    if t < te:
        u = clamp((t - 31.1)/(te - 31.1)); s_ = lerp(.3, 1.15, u**1.5) + .03*math.sin(t*40)*u
        ImageDraw.Draw(L).line([(CX, 700 + 250*s_), (CX + 20*math.sin(t*5), 1050)], fill=(220, 220, 220), width=4)
        put(L, balloon(), CX, 700, s_, 4*math.sin(t*6))
    else:
        rnd = random.Random(3); u = t - te
        for k in range(26):                                   # éclats + billets
            a = rnd.uniform(0, 6.28); v = rnd.uniform(500, 1300); x = CX + math.cos(a)*v*u; y = 700 + math.sin(a)*v*u + 900*u*u
            if k % 2: put(L, bill(k % 3), x, y, .7, a*60 + u*300)
            elif u < .5: ImageDraw.Draw(L).polygon([(x, y), (x + 30, y + 10), (x + 8, y + 34)], fill=(220, 30, 44))
        fx.shockwave(L, t, te, CX, 700, .45, 900)
        if u < .1: L.alpha_composite(Image.new("RGBA", L.size, (255, 250, 240, int(255*(1 - u/.1)))))
        fx.ecg(L, t, 1520, amp=60, bpm=150, alpha=.0, pulse=False)
    if t > w("fin") - .05:
        tv = w("fin") + .05; u = clamp((t - tv)/.25)
        hits = [w("fin") + .35, w("fin") + .6, w("fin") + .85]; sink = sum(18 for h_ in hits if t > h_)
        put(L, sign("À VENDRE", 420), 800, lerp(-300, 980, u*u) + sink, 1.0, 3)
        if t < hits[-1] + .3:
            ph = min([((t - h_ + .18)/.18) for h_ in hits if t > h_ - .18] or [0]); ang = -60 + 70*clamp(ph) if ph < 1 else -60
            put(L, hammer(), 1010, 1080 + sink, 1.0, 10 + 41*clamp(ph) if 0 < ph < 1 else 10)
    if t > w("vendu") - .05: slam_in(L, fr, stampl("VENDU", ROUGE, 190), t, w("vendu") - .05, CX, 1250, -12)
    if t > w("catastrophe") - .1:
        put(L, beacon(), 230, 1000, 1.0)
        rays(L, (230, 980), t*6, .6, 2, 1400, (255, 60, 60), .08, 1.0)
        k = .25*(1 + math.sin(t*14))/2; L.alpha_composite(Image.new("RGBA", L.size, (200, 0, 20, int(255*k*.6))))
CAM_DEBT = [(31.16, CX, 760, 1.15), (31.8, CX, 900, 1.0), (32.45, 760, 1000, 1.2), (33.5, 700, 1150, 1.1), (33.85, CX, 1200, 1.12), (34.9, CX, 1050, 1.0)]

# --- 12. L'IMPOSSIBLE
@scene(34.97, trans="fade", td=.3)
def s_imp(L, fr, t):
    paper_fill(L, (10, 8, 14), "black")
    u = clamp((t - 34.97)/1.6); rays(L, (CX, 1000), t, u, 18, 1700, (255, 230, 150), .06, .4)
    put(L, spark(160), CX, 1000, .15 + 1.4*u**2 + .05*math.sin(t*20), t*40)
    fx.kinetic(L, fr, t, [("L'IMPOSSIBLE", w("l'impossible") - .02), ("ARRIVE", w("arrive") - .02)], CX, 720,
               lambda x, i: kword(x, JAUNE if i == 0 else BLANC, NOIR, 130))
    if t > 36.4: L.alpha_composite(Image.new("RGBA", L.size, (255, 250, 230, int(255*clamp((t - 36.4)/.18)))))
CAM_IMP = [(34.97, CX, 1000, 1.0), (36.58, CX, 1000, 1.25)]

# --- 13. TERRAIN : Maignan, Yilmaz, Galtier (3 panneaux côte à côte)
PW = 3*W
@scene(36.58, size=(PW, H), trans="flash", td=.15)
def s_pitch(L, fr, t):
    paper_fill(L, VERT, "pitch3"); d = ImageDraw.Draw(L)
    for k in range(0, PW, 240): d.rectangle([k, 0, k + 120, H], fill=VERT2)
    d.rectangle([0, 0, PW, 300], fill=(26, 30, 50))
    for k in range(120): d.ellipse([(k*41) % PW, 40 + (k*29) % 240, (k*41) % PW + 10, 50 + (k*29) % 240], fill=[(214, 16, 40), (250, 250, 246), (18, 30, 78)][k % 3])
    # A : Maignan plonge
    foot.draw_goal(L, fr, 540, 1000, 760, 400, 0, 1, t)
    tm = w("maignan") + .1; dv = ease((t - tm)/.25)
    player_rot(L, fr, MAIGNAN, 540 - 260*dv, 1280 - 120*dv, -70*dv, s=1.1, kit="lille_gk", arms=(150, 150), mood="normal", t=t)
    if t > tm - .3:
        u = (t - tm + .3)/.3; bx, by = (lerp(540, 300, u), lerp(1700, 760, u)) if u < 1 else (300 - 500*(u - 1), 760 - 300*(u - 1))
        foot.draw_ball(L, fr, bx, by, .9, t*600)
    if t > w("maignan") - .05: put(L, pin_tag("MAIGNAN", 60), 540, 640, eob((t - w("maignan") + .05)/.25), -3)
    # B : Yilmaz frappe, filet
    tb = w("burak") + .3; nu = clamp((t - tb - .22)/.5)
    foot.draw_goal(L, fr, W + 540, 1000, 760, 400, nu if nu < 1 else 0, 1, t)
    kickp = clamp((t - tb + .15)/.15)
    YILMAZ.draw(L, fr, W + 600, 1650, s=1.2, kit="lille", beard=True, legs=(0, -50*math.sin(math.pi*kickp)), arms=(40, 30), mood="normal", t=t)
    if t > tb:
        u = clamp((t - tb)/.22); foot.draw_ball(L, fr, W + lerp(520, 700, u), lerp(1600, 880, u), lerp(.9, .6, u), t*800)
    if t > w("burak") - .05: put(L, pin_tag("BURAK YILMAZ", 60), W + 540, 640, eob((t - w("burak") + .05)/.25), 3)
    # C : Galtier sur le banc
    nod = 6*math.sin(max(0, t - w("galtier"))*8)*math.exp(-max(0, t - w("galtier"))*2)
    GALTIER.draw(L, fr, 2*W + 560, 1420 + nod, s=1.2, kit="coach_navy", arms=(-30, -30), mood="normal", t=t)
    put(L, bench(), 2*W + CX, 1380, 1.3); put(L, clipboard(), 2*W + 470, 1250, .9, -12)
    if t > w("galtier") - .05: put(L, pin_tag("GALTIER", 60), 2*W + 540, 700, eob((t - w("galtier") + .05)/.25), -2)
CAM_PITCH = [(36.58, CX, 1050, 1.0), (36.9, 430, 1000, 1.15), (37.5, 420, 1000, 1.12), (37.75, W + CX, 1000, 1.05), (38.4, W + 640, 960, 1.15),
             (38.75, W + 600, 1000, 1.1), (39.0, 2*W + CX, 1050, 1.05), (39.6, 2*W + 560, 1100, 1.15), (40.23, 2*W + CX, 1050, 1.1)]

# --- 14. BALANCE : budget ×4
@scene(40.23, trans="whip", td=.25)
def s_scale(L, fr, t):
    paper_fill(L, (236, 228, 210), "scbg")
    slam_in(L, fr, kword("BUDGET", NOIR, BLANC, 120), t, w("budget") - .1, CX, 560, -3)
    tq = w("quatre"); ang = 7*spring(t, w("psg", 2), .5) + 15*spring(t, tq, .7)
    put(L, scale_stand(), CX, 1350, 1.3)
    a = math.radians(ang); px, py = CX, 960
    ends = [(px - 380*math.cos(a), py - 380*math.sin(a)*-1), (px + 380*math.cos(a), py + 380*math.sin(a)*-1)]
    ends = [(px - 380*math.cos(a), py + 380*math.sin(a)), (px + 380*math.cos(a), py - 380*math.sin(a))]
    put(L, scale_beam(), px, py, 1.0, -ang)
    d = ImageDraw.Draw(L)
    for i, (ex, ey) in enumerate(ends):
        for sx in (-1, 1): d.line([(ex, ey), (ex + sx*130, ey + 230)], fill=(90, 70, 40), width=4)
        put(L, scale_pan(), ex, ey + 240, 1.0)
        if i == 0 and t > w("psg", 2) - .1:
            h_ = 190 + 150*spring(t, tq, .5); put(L, money_bag(int(h_), "PSG"), ex, ey + 230 - h_*.5, 1.0, wob(t, tq, 4, 10, 5))
        if i == 1: put(L, money_bag(150, "LOSC"), ex, ey + 230 - 75, 1.0)
    if t > tq: slam_in(L, fr, stampl("×4", ROUGE, 170), t, tq, 850, 720, 10)
CAM_SCALE = [(40.23, CX, 1000, 1.0), (41.0, CX, 960, 1.05), (41.75, CX, 1000, 1.0), (42.9, CX, 1000, 1.06)]

# --- 15. TIR À LA CORDE
@scene(42.90, trans="whip", td=.25)
def s_tug(L, fr, t):
    paper_fill(L, VERT, "tug"); d = ImageDraw.Draw(L)
    for k in range(0, H, 220): d.rectangle([0, k, W, k + 110], fill=VERT2)
    tb = w("bout"); fallen = ease((t - tb)/.35); jit_ = 14*math.sin(t*22)*(t < tb)
    off = jit_ + 120*fallen
    d.line([(150 + off*.3, 1180), (930 + off, 1180)], fill=(220, 200, 150), width=14)
    ImageDraw.Draw(L).polygon([(CX - 20 - off*.6, 1180), (CX + 20 - off*.6, 1180), (CX - off*.6, 1260)], fill=ROUGE)
    LOSCP.draw(L, fr, 230 - off*.3, 1460, s=1.25, kit="lille", arms=(80, 80), lean=-30, mood="normal", t=t, look=(1, 0))
    player_rot(L, fr, PSGP, 850 + 80*fallen, 1460, 75*fallen, s=1.25, kit="psg", arms=(80, 80), lean=30, mood="sad" if fallen > 0 else "normal", t=t)
    fx.kinetic(L, fr, t, [("ILS TIENNENT", w("tiennent") - .02), ("JUSQU'AU BOUT !", w("jusqu'au") - .02)], CX, 660,
               lambda x, i: kword(x, NOIR if i == 0 else ROUGE, BLANC, 110))
CAM_TUG = [(42.9, CX, 1050, 1.05), (43.9, CX, 1080, 1.12), (44.26, CX + 80, 1080, 1.0)]

# --- 16. CHAMPIONS + arrêt sur image
@scene(44.26, trans="flash", td=.15)
def s_champ(L, fr, t):
    tw_ = min(t, FZ0)
    paper_fill(L, (206, 18, 36), "chbg"); rays(L, (CX, 900), tw_, 1.0, 22, 1900, (240, 70, 80), .12, .6)
    lift = eob((tw_ - 44.3)/.5, 1.4)
    LOSCP.draw(L, fr, CX, 1640, s=1.45, kit="lille", arms=(lerp(20, 165, lift), lerp(20, 165, lift)), mood="happy", t=tw_)
    put(L, trophy_league(460), CX, lerp(1300, 760, lift), 1.0)
    if t < FZ0: fx.kinetic(L, fr, tw_, [("CHAMPIONS", w("champions", 2) - .02), ("DE FRANCE !", w("de", 6) - .02 if False else w("champions", 2) + .42)], CX, 560,
               lambda x, i: kword(x, JAUNE, NOIR, 135))
    confetti(L, fr, "v5cf3", tw_ - 44.3, 110, 4, [JAUNE, BLANC, NAVY])
CAM_CHAMP = [(44.26, CX, 1000, 1.2), (44.7, CX, 960, 1.0), (45.38, CX, 960, 1.03), (47, CX, 960, 1.06)]

def freeze_fx(cv, fr, t):
    u = t - FZ0
    fx.desat(cv, min(.9, u*8), min(.72, u*5))
    if u < .5: fx.shockwave(cv, t, FZ0, CX, 960, .5, 1000)
    mono(fx.typed_cursor("II ARRÊT SUR IMAGE", t, FZ0, 32), 58, ROUGE).draw(cv, fr, CX, 620, 1, -2)
    if u > .35: slam_in(cv, fr, kword("LOSC 83 PTS", JAUNE, NOIR, 104), t, FZ0 + .35, CX, 860, -3)
    if u > .6: slam_in(cv, fr, kword("PSG 82 PTS", NAVY, BLANC, 84), t, FZ0 + .6, CX, 1020, 2)
    if u > .85:
        slam_in(cv, fr, stampl("1 POINT D'ÉCART !", ROUGE, 96), t, FZ0 + .85, CX, 1230, -6)
        marker_circle(cv, CX, 1230, 480, 120, (u - .95)/.4, ROUGE, 12)

# --- 17. CTA
CLUBS = ["om", "ol", "monaco", "bordeaux", "brest", "psg"]
@scene(FZ0 + FZD, trans="tear", td=.3)
def s_cta(L, fr, t):
    paper_fill(L, (24, 34, 80), "ctabg"); rays(L, (CX, 900), t, .5, 16, 1700, (34, 48, 104), .1, .3)
    put(L, bubble(), CX, 760, 1.12*eob((t - 47.0)/.3), 0)
    if 47.0 < t < w("toi") + .05:
        for k in range(3): ImageDraw.Draw(L).ellipse([CX - 90 + k*90 - 20, 740 - 20 - 18*abs(math.sin(t*9 + k)), CX - 90 + k*90 + 20, 740 + 20 - 18*abs(math.sin(t*9 + k))], fill=(150, 150, 160))
    fx.kinetic(L, fr, t, [("TU T'EN", w("toi") - .02), ("SOUVIENS ?", w("souviens") - .02)], CX, 745, lambda x, i: kword(x, NOIR, BLANC, 96), maxw=520)
    if t > w("dis-moi") - .05:
        fx.wipe(L, fr, marker("PROCHAIN CLUB ?", "v5pc", 100), CX, 1080, t, w("dis-moi") - .05, 2)
        k = int(max(0, (t - w("dis-moi"))*8)); slow = min(len(CLUBS)*3 - 1, k)
        nm = CLUBS[slow % len(CLUBS)]; put(L, logo(nm, 220), CX, 1300, 1 + .1*math.sin(t*20), 0)
        y = 1480 + 18*abs(math.sin(t*6)); ImageDraw.Draw(L).polygon([(CX - 50, y), (CX + 50, y), (CX, y + 60)], fill=ROUGE)
CAM_CTA = [(46.9, CX, 960, 1.05), (48.6, CX, 1000, 1.0), (52, CX, 1000, 1.04)]

CAMS = {"s_hook": CAM_HOOK, "s_cal": CAM_CAL, "s_trophy": CAM_TROPHY, "s_table": CAM_TABLE, "s_question": CAM_Q, "s_1944": CAM_1944,
        "s_1946": CAM_1946, "s_sea": CAM_SEA, "s_ucl": CAM_UCL, "s_train": CAM_TRAIN, "s_gift": CAM_GIFT, "s_debt": CAM_DEBT, "s_imp": CAM_IMP,
        "s_pitch": CAM_PITCH, "s_scale": CAM_SCALE, "s_tug": CAM_TUG, "s_champ": CAM_CHAMP, "s_cta": CAM_CTA}
PUNCH += [w("dettes"), w("champion"), w("mbappé") + .5, w("fusionnent") + .3, w("dogues"), w("doublé"), w("division"), w("remonter") + .5, w("ligue"),
          w("eden"), w("doublé", 2), w("explosent") + .12, w("vendu"), w("maignan") + .3, w("burak") + .5, w("quatre"), w("bout"), w("champions", 2)]
SHAKES = PUNCH

# ------------------------------------------------------------------ rendu d'une scène + transitions
def render_scene(i, fr, t):
    s = SC[i]; L = Image.new("RGBA", s["size"], (0, 0, 0, 255)); s["fn"](L, fr, t)
    cx, cy, z = camk(CAMS[s["name"]], t); z *= punch(t)
    return apply_cam(L, cx + 4*math.sin(t*.9), cy + 3*math.cos(t*.7), z, .35*math.sin(t*.6)).convert("RGB")
def scene_at(t):
    k = 0
    for i, s in enumerate(SC):
        if t >= s["t0"]: k = i
    return k
def frame(fr, t):
    k = scene_at(t); s = SC[k]; cur = render_scene(k, fr, t)
    u = (t - s["t0"])/s["td"] if k else 1
    if u < 1:
        prev = render_scene(k - 1, fr, t); tr = s["trans"]; e = ease(u)
        if tr in ("whip", "whip_up"):
            vert = tr == "whip_up"; off = int((W if not vert else H)*e)
            out = Image.new("RGB", (W, H))
            if vert: out.paste(prev, (0, off)); out.paste(cur, (0, off - H))
            else: out.paste(prev, (-off, 0)); out.paste(cur, (W - off, 0))
            fx.whip_blur(out, 0 if vert else -90*math.sin(math.pi*u), 90*math.sin(math.pi*u) if vert else 0, 6); cur = out
        elif tr == "zoom_through":
            z = 1 + 2.2*e; bw, bh = W/z, H/z
            p2 = prev.crop((int(CX - bw/2), int(1110 - bh/2), int(CX + bw/2), int(1110 + bh/2))).resize((W, H), Image.BICUBIC)
            cur = Image.blend(p2, cur, clamp((u - .35)/.65))
        elif tr == "tear": tear_transition(cur, prev, u, "tear_v", k);
        elif tr == "fade": cur = Image.blend(prev, cur, e)
        elif tr == "flash":
            cur = Image.blend(prev, cur, 1.0 if u > .5 else 0.0); cur = Image.blend(cur, Image.new("RGB", (W, H), (255, 250, 236)), max(0, 1 - abs(u - .5)*2.2))
        elif tr == "glitch":
            cur = (cur if u > .5 else prev).copy(); rgb_split(cur, 20*(1 - abs(u - .5)*2), fr, 8)
    if FZ0 <= t < FZ0 + FZD: freeze_fx(cur, fr, t)
    for p in SHAKES:
        if p < t < p + .3:
            a = 14*(1 - (t - p)/.3); cur = ImageChops.offset(cur, int(a*math.sin(t*90)), int(a*math.cos(t*70)))
    fx.dust(cur, t, 24)
    cur = cur.convert("RGBA"); fx.vignette(cur, 90); fil_rouge(cur, fr, t)
    return cur.convert("RGB")

def draw(cv, fr, t, T):
    tv = max(0.0, t - PAD_IN); cv.paste(frame(fr, tv), (0, 0))

# ------------------------------------------------------------------ sons
P = PAD_IN
V5S = os.path.join(HERE, "sfx"); BANK = os.path.join(ROOT, "assets", "sfx")
def X(t, name, g): return (P + t, name, g)
SFX = [X(0, "braam", .75), X(0, "rustle", .45), X(.55, "heart", .5), X(1.1, "heart", .45), X(w("dettes"), "stamp", .8), X(w("dettes") + .05, "ding", .45),
       X(1.28, "whoosh2", .5)] + [X(t0, "page_tear", .55) for t0 in TEARS] + [
       X(2.2, "suck", .6), X(w("champion"), "boom", .8), X(w("champion") + .05, "crowd", .5), X(2.95, "sparkle", .4),
       X(4.03, "whoosh1", .5), X(4.1, "swish", .4), X(4.55, "whoosh3", .45), X(4.6, "tok", .5),
       X(w("neymar") - .05, "pin", .5), X(w("neymar") + .25, "marker", .55), X(w("mbappé") - .05, "pin", .5), X(w("mbappé") + .25, "marker", .55),
       X(w("mbappé") + .5, "stamp", .7), X(6.55, "scratch", .6), X(6.9, "thud", .5), X(7.02, "rewind", .65), X(7.05, "tictac", .4),
       X(7.75, "flashfx", .45), X(7.78, "stamp", .7), X(7.9, "typewriter", .4), X(w("deux") - .1, "swish", .45), X(w("clubs") - .1, "swish", .45),
       X(w("rivaux"), "zap", .6), X(w("fusionnent"), "whoosh3", .5), X(w("fusionnent") + .3, "boom", .65), X(w("fusionnent") + .32, "shimmer", .4),
       X(w("dogues"), "paws", .55), X(12.5, "whoosh1", .5), X(w("doublé") - .03, "stamp", .6), X(w("coupe") + .12, "tok", .7),
       X(w("championnat") + .12, "tok", .65), X(w("championnat") + .2, "fanfare", .45),
       X(14.62, "page_tear", .5), X(14.7, "waves", .5), X(w("sombre") - .1, "bubbles", .55), X(15.6, "bubbles", .45), X(w("division"), "thud", .65),
       X(w("en", 2) - .1, "typewriter", .35), X(w("vahid") - .2, "pin", .45), X(w("remonter") - .25, "crank", .55), X(w("remonter"), "riser", .5),
       X(w("remonter") + .5, "waves", .4), X(19.84, "whoosh2", .5), X(20.0, "crowd", .35), X(w("ligue"), "bell", .45), X(w("lille", 3), "whoosh1", .4),
       X(21.0, "flashfx", .25), X(22.43, "page_tear", .5), X(22.5, "typewriter", .35)] + [X(22.7 + k*.4, "touch", .45) for k in range(7)] + [
       X(w("belge"), "pop", .45), X(w("quatorze"), "pin", .5), X(w("eden") - .05, "shimmer", .55), X(w("hazard"), "sparkle", .45),
       X(26.71, "whoosh3", .5), X(26.75, "stamp", .6), X(w("rudi") - .1, "swish", .4), X(w("offre") - .1, "ribbon", .5),
       X(w("doublé", 2) - .05, "pop", .6), X(w("doublé", 2), "fanfare", .5), X(w("doublé", 2) + .1, "crowd", .35), X(w("soixante-cinq"), "tictac", .35),
       X(31.14, "page_tear", .5), X(31.2, "inflate", .6), X(w("explosent") + .12, "bang", .85), X(w("explosent") + .15, "coins", .45),
       X(w("fin") + .05, "whoosh2", .4)] + [X(w("fin") + h_, "hammer", .65) for h_ in (.35, .6, .85)] + [
       X(w("vendu") - .05, "stamp", .9), X(w("catastrophe") - .1, "siren", .25),
       X(34.97, "breath", .55), X(35.3, "riser", .55), X(36.4, "flashfx", .5),
       X(w("maignan") - .2, "kick", .55), X(w("maignan") + .1, "glove", .7), X(37.6, "whoosh1", .5), X(w("burak") + .15, "kick", .7),
       X(w("burak") + .45, "net", .6), X(w("burak") + .5, "crowd", .45), X(38.8, "whoosh2", .5), X(w("galtier") + .3, "pin", .4),
       X(40.21, "whoosh3", .5), X(w("budget") - .1, "stamp", .5), X(w("psg", 2), "creak", .5), X(w("quatre"), "coins", .55), X(w("quatre") + .05, "stamp", .75),
       X(42.88, "whoosh1", .5), X(43.0, "creak", .45), X(43.1, "drumroll", .45), X(w("bout"), "fall", .7),
       X(44.24, "flashfx", .5), X(w("champions", 2), "boom", .85), X(w("champions", 2) + .05, "goal_roar", .6), X(44.6, "champagne", .45),
       X(FZ0, "rewind", .5), X(FZ0 + .35, "stamp", .55), X(FZ0 + .6, "stamp", .45), X(FZ0 + .85, "stamp", .75), X(FZ0 + .95, "marker", .5),
       X(FZ0 + FZD - .05, "page_tear", .5), X(47.0, "pop", .5), X(w("toi"), "notif", .55), X(w("dis-moi"), "marker", .45),
       X(w("dis-moi") + .1, "crank", .3), X(w("histoire"), "bell", .4)]
SFX_DIR = "/tmp/claude-0/sfx_v5"
os.makedirs(SFX_DIR, exist_ok=True)
for nm in set(n for _, n, _ in SFX):
    src = os.path.join(V5S, nm + ".mp3")
    if not os.path.exists(src) or nm in ("crowd", "siren"): src = os.path.join(BANK, nm + ".mp3")
    dst = os.path.join(SFX_DIR, nm + ".mp3")
    if not os.path.exists(dst): os.symlink(src, dst)
SFX = fx.sfx_variants(SFX, SFX_DIR, SFX_DIR + "_v")
SCENES = [Scene("losc_v5", TEXTE, draw, SFX, pad_in=P, pad_out=1.6)]

def stills(out, only=None):
    os.makedirs(out, exist_ok=True); ts = []
    for i, s in enumerate(SC):
        if only and s["name"] != only: continue
        t1 = SC[i + 1]["t0"] if i + 1 < len(SC) else 52.5; n = 3 if not only else 8
        ts += [s["t0"] + (t1 - s["t0"])*(k + .5)/n for k in range(n)]
    if not only: ts += [FZ0 + .3, FZ0 + 1.3]
    ims = []
    for t in ts:
        cv = Image.new("RGB", (W, H)); cv.paste(frame(int(t*FPS), t)); ims.append(cv.resize((216, 384)))
    cols = 10; rows = (len(ims) + cols - 1)//cols; sheet = Image.new("RGB", (216*cols, 414*rows), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        x, y = (k % cols)*216, (k//cols)*414; sheet.paste(im, (x, y + 30)); dd.text((x + 6, y + 4), f"{ts[k]:.2f}s", font=font("mono", 22), fill=(230, 230, 230))
    p = os.path.join(out, f"sheet{'_' + only if only else ''}.jpg"); sheet.save(p, quality=82); return p

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--stills" in args:
        only = args[args.index("--stills") + 1] if len(args) > args.index("--stills") + 1 else None
        print(stills("/tmp/claude-0/aud", only)); sys.exit()
    out = args[0] if args else os.path.join(ROOT, "output", SLUG); os.makedirs(out, exist_ok=True)
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=[VOIX], sfx_dir=SFX_DIR + "_v", sfx_db=6.0, lufs=-14.0, crf=22, limit=True))
