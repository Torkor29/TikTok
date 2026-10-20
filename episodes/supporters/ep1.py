"""LE STADE DES SUPPORTERS — épisode 1 (concept : 1 commentaire = 1 siège à ton nom dans le stade de ton club).
Voix Léo (voix/ep1.mp3, 16 s) + textes plein écran lisibles dès la 1re image + bruitages maison. Style papier + volumes papercraft 3D.

  python3 episodes/supporters/ep1.py --stills      planche de contrôle
  python3 episodes/supporters/ep1.py               rendu -> output/supporters/ep1.mp4
"""
import sys, os, math, subprocess, functools
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "lille_v5")); sys.path.insert(0, ROOT)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from story import *                                   # Label, font, blit, blit_sxy, boil, PAL...
from gfx import sticker
import motion as M
from motion import El
import pc_lib as PC
from papercraft import Part, cbox, render, project, rot as R3

W, H, FPS, DUR = 1080, 1920, 30, 17.6
OUT = os.path.join(ROOT, "output", "supporters")
NAVY, NAVY2 = (20, 26, 58), (34, 44, 92)
JAUNE, ROUGE, BLANC, NOIR, CREME = (250, 206, 40), (226, 36, 54), (250, 248, 240), (24, 22, 26), (245, 235, 214)

# les 18 clubs de Ligue 1 (écussons officiels fournis)
CLUBS = [("rennes", (214, 26, 34), (26, 24, 28)), ("psg", (20, 36, 82), (214, 30, 40)), ("om", (240, 244, 248), (40, 160, 220)),
         ("ol", (246, 246, 250), (30, 50, 140)), ("lille", (214, 30, 40), (20, 36, 82)), ("monaco", (214, 26, 34), (246, 246, 246)),
         ("brest", (214, 26, 34), (250, 250, 250)), ("lens", (250, 214, 30), (214, 30, 40)), ("lorient", (240, 110, 30), (24, 22, 26)),
         ("nice", (214, 26, 34), (24, 22, 26)), ("toulouse", (90, 50, 140), (250, 250, 250)), ("strasbourg", (40, 150, 220), (250, 250, 250)),
         ("auxerre", (250, 250, 250), (30, 70, 160)), ("angers", (250, 250, 250), (24, 22, 26)), ("lehavre", (140, 196, 236), (30, 44, 90)),
         ("parisfc", (24, 34, 80), (60, 150, 220)), ("troyes", (30, 110, 190), (250, 250, 250)), ("lemans", (214, 26, 34), (250, 196, 40))]
for n, c1, c2 in CLUBS:
    PC.KITS[n] = dict(c1=c1, sleeve=c1, shorts=c2, socks=c1, trim=c2, kind="plain")

# ------------------------------------------------------------------ outils
@functools.lru_cache(maxsize=64)
def logo(n, h): s = sticker(n, h); return s
def L_(txt, size=96, bg=NOIR, fg=BLANC, font_="title", maxw=980, rough=3):
    return LBL(txt, f"sup{size}{bg}{fg}", font(font_, size), fg, bg, maxw=maxw, padx=28, pady=10, rough=rough)

@functools.lru_cache(maxsize=4)
def background(k=0):
    rng = np.random.default_rng(k)
    y = np.linspace(0, 1, H)[:, None, None]
    a = np.array(NAVY, np.float32)*(1 - y) + np.array(NAVY2, np.float32)*y
    a = np.repeat(a, W, 1)
    n = rng.random((H//4, W//4)).astype(np.float32)
    n = np.asarray(Image.fromarray((n*255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2)), np.float32)/255
    a *= (.9 + .16*n)[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for i in range(0, W + H, 160): d.line([(i, 0), (i - H, H)], fill=(255, 255, 255, 7), width=60)   # rayures papier très légères
    im.alpha_composite(ov); return im

def rays(L, cx, cy, t, a=.18, n=12):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for k in range(n):
        th = t*.25 + 2*math.pi*k/n; w = .09
        d.polygon([(cx, cy), (cx + 2000*math.cos(th - w), cy + 2000*math.sin(th - w)), (cx + 2000*math.cos(th + w), cy + 2000*math.sin(th + w))],
                  fill=(255, 236, 160, int(255*a)))
    L.alpha_composite(ov.filter(ImageFilter.GaussianBlur(6)))

# ------------------------------------------------------------------ volumes 3D
def stand_parts(col, n=7, rows=3, sel=None):
    """Tribune : gradins en béton + sièges (assise + dossier). sel = (rangée, colonne) du siège mis en valeur."""
    parts = []; gw = n*.8
    for r in range(rows):
        y, z = r*.55, -r*.75
        parts.append(Part(cbox(gw + .4, .55, .75, .02), (150, 150, 158), None, (0, y + .275, z), name=f"step{r}"))
        for i in range(n):
            x = (i - (n - 1)/2)*.8; c = col
            if sel == (r, i): c = tuple(min(255, int(v*1.15 + 20)) for v in col)
            parts.append(Part(cbox(.6, .1, .45, .2), c, None, (x, y + .62, z + .08), name=f"s{r}{i}"))
            parts.append(Part(cbox(.6, .55, .1, .2), c, None, (x, y + .9, z - .17), name=f"b{r}{i}"))
    return parts

@functools.lru_cache(maxsize=32)
def stand_sprite(col, sel=None):
    return render(stand_parts(col, sel=sel), 1100, yaw=0, pitch=.5, scale=1100/6.0, center=(0, 1.1, -.75), shadow=False, anchor=(0, 0, 0))
SEAT_SEL = (0, 3)
def seat_screen(scale_px=1100/6.0, center=(0, 1.1, -.75)):
    """Position écran (dans le sprite de tribune) du siège sélectionné."""
    r, i = SEAT_SEL; x = (i - 3)*.8
    return project((x, r*.55 + .62, -r*.75 + .08), yaw=0, pitch=.5, scale=scale_px, center=center, size=1100)

def podium_parts():
    from papercraft import speckle
    p = []
    for nm, x, h, col in (("p2", -1.25, 1.1, (196, 200, 210)), ("p1", 0, 1.6, (236, 186, 48)), ("p3", 1.25, .8, (196, 128, 70))):
        p.append(Part(cbox(1.2, h, 1.1, .08), col, lambda P, c: speckle(P, c, .01), (x, h/2, 0), name=nm))
    return p
@functools.lru_cache(maxsize=2)
def podium_sprite():
    return render(podium_parts(), 1000, yaw=0, pitch=.25, scale=1000/4.6, center=(0, .9, 0), shadow_a=90, anchor=(0, 0, 0))
def podium_top(i):
    x, h = ((-1.25, 1.1), (0, 1.6), (1.25, .8))[i]
    return project((x, h, .3), yaw=0, pitch=.25, scale=1000/4.6, center=(0, .9, 0), size=1000)

@functools.lru_cache(maxsize=48)
def cup(q): return PC.cup_sprite(q/24*2*math.pi, 520)

FAN = PC.PCPlayer("fan", hair=(46, 32, 24), skin=(226, 182, 146), yaw=0)
def fan_sprite(club, t, ghost=False):
    a = 140 + 20*math.sin(t*10)
    return FAN.sprite(kit=club, arms=(a, a), mood="happy", t=t)

def sign(club, txt="@TON.PSEUDO"):
    k = ("sign", club, txt)
    if k in _sg: return _sg[k]
    lab = L_(txt, 50, BLANC, NOIR, "mono", rough=1.5).v[0]
    lg = logo(club, 74) if club else None
    w = lab.width + (90 if lg else 0); im = Image.new("RGBA", (w + 10, max(lab.height, 90) + 10), (0, 0, 0, 0))
    im.alpha_composite(lab, (0, (im.height - lab.height)//2))
    if lg: im.alpha_composite(lg, (lab.width - 6, (im.height - lg.height)//2))
    im.info["anchor"] = (im.width/2, im.height/2); _sg[k] = im; return im
_sg = {}

def puff(L, t, t0, x, y, n=12, col=(220, 220, 230), dur=.6):
    u = (t - t0)/dur
    if not 0 <= u <= 1: return
    d = ImageDraw.Draw(L)
    for k in range(n):
        a = 2*math.pi*k/n; r = 40 + 200*M.ease_out(u); s = 26*(1 - u)
        d.ellipse([x + r*math.cos(a) - s, y + r*math.sin(a)*.6 - s, x + r*math.cos(a) + s, y + r*math.sin(a)*.6 + s], fill=col + (int(255*(1 - u)),))

# ------------------------------------------------------------------ timeline (s)
T = dict(s2=2.15, decide=3.38, s3=4.62, s4=5.75, nom=7.08, s5=8.33, s6=9.82, click=11.47, s7=11.6, s8=12.94, end=17.6)  # calé sur voix/ep1.mp3
def counter(t):
    n = 0 if t < T["s4"] + .4 else (1 if t < T["s6"] + .3 or t > T["click"] + .1 else 0)
    if t > T["s7"]: n = 0
    return n

TEXTS = [  # (texte, taille, fond, couleur, y, entrée, sortie)
    ("QUEL CLUB DE LIGUE 1", 92, NOIR, BLANC, 400, 0, T["s2"]), ("A LE PLUS DE", 92, NOIR, BLANC, 520, 0, T["s2"]),
    ("SUPPORTERS ?", 140, JAUNE, NOIR, 670, 0, T["s2"]),
    ("ON VA ENFIN", 110, NOIR, BLANC, 430, T["s2"], T["decide"]), ("LE SAVOIR", 130, JAUNE, NOIR, 570, T["s2"] + .25, T["decide"]),
    ("ET C'EST TOI", 110, NOIR, BLANC, 430, T["decide"], T["s3"]), ("QUI DÉCIDES", 130, ROUGE, BLANC, 570, T["decide"] + .2, T["s3"]),
    ("TOUS LES STADES", 100, NOIR, BLANC, 430, T["s3"], T["s4"]), ("SONT VIDES", 140, BLANC, NOIR, 570, T["s3"] + .3, T["s4"]),
    ("1 COMMENTAIRE", 100, NOIR, BLANC, 430, T["s4"], T["s5"]), ("= 1 SIÈGE", 130, JAUNE, NOIR, 560, T["s4"] + .3, T["nom"]),
    ("AVEC TON NOM DESSUS", 84, JAUNE, NOIR, 560, T["nom"], T["s5"]),
    ("TON CLUB,", 110, NOIR, BLANC, 430, T["s5"], T["s6"]), ("N'IMPORTE LEQUEL", 100, BLANC, NOIR, 565, T["s5"] + .25, T["s6"]),
    ("PAS ABONNÉ ?", 120, ROUGE, BLANC, 430, T["s6"], T["s7"]), ("SIÈGE VIDE", 130, BLANC, NOIR, 570, T["s6"] + .3, T["click"] + .1),
    ("ABONNÉ = TU RESTES", 84, JAUNE, NOIR, 570, T["click"] + .1, T["s7"]),
    ("LE CLASSEMENT", 110, NOIR, BLANC, 430, T["s7"], T["s8"]), ("CHAQUE JOUR", 130, JAUNE, NOIR, 570, T["s7"] + .25, T["s8"]),
    ("QUEL CLUB", 120, NOIR, BLANC, 400, T["s8"], None), ("VA GAGNER ?", 140, JAUNE, NOIR, 545, T["s8"] + .2, None),
    ("ÉCRIS TON CLUB EN COMMENTAIRE", 58, BLANC, NOIR, 1700, T["s8"] + 1.35, None),
]
ELS = [El(L_(tx, sz, bg, fg), W/2, y, t0, t1, "stamp" if i % 2 else "pop", "shrink", 1, (-2.5, 2, -1.5, 2.5)[i % 4], .6, seed=i)
       for i, (tx, sz, bg, fg, y, t0, t1) in enumerate(TEXTS)]
for e, (tx, *_ ) in zip(ELS, TEXTS):
    if e.t_in == 0: e.inn, e.t_in = "none", -1.0           # 1re image : la question est DÉJÀ entière à l'écran

def header(L, fr, t):
    n = counter(t)
    L_(f"JOUR 1 · {n} SUPPORTER", 40, NOIR, JAUNE, "mono", rough=1.5).draw(L, fr, W/2, 250, 1, 0)

# ------------------------------------------------------------------ scènes
def s_intro(L, fr, t):
    rays(L, W/2, 1220, t, .07)
    cx, cy = W/2, 1230
    for i, (n, *_ ) in enumerate(CLUBS):
        a = t*.55 + 2*math.pi*i/18; r = 390
        x, y = cx + r*math.cos(a), cy + r*math.sin(a)*.9
        if t > T["s2"]:                                            # les écussons se rangent en grille
            u = M.ease_io((t - T["s2"] - i*.03)/.6); gx = 140 + (i % 6)*160; gy = 960 + (i//6)*200 + 120
            x, y = x + (gx - x)*u, y + (gy - y)*u
        if n: blit(L, logo(n, 125), x, y, 1, 4*math.sin(t*2 + i))
        else:
            b = L_("?", 90, CREME, NOIR); b.draw(L, fr, x, y, 1, 6*math.sin(t*2 + i))
    if t < T["s2"] + .4:
        sp = cup(int(t*12) % 24); a = 1 - M.ease_in((t - T["s2"])/.4) if t > T["s2"] else 1
        blit_sxy(L, sp, cx, cy + 180 + 8*math.sin(t*3), .95*a, .95*a, 0)

def s_stade(L, fr, t):
    sel = SEAT_SEL if t > T["s4"] else None
    club = None
    if t > T["s5"]: club = CLUBS[int((t - T["s5"])/.2) % len(CLUBS)] if t < T["s6"] else CLUBS[0]
    col = club[1] if club else (120, 124, 136)
    if club and club[0] in ("om", "ol", "auxerre", "angers"): col = club[2]
    pan = 0 if t > T["s4"] else 60*math.sin((t - T["s3"])*.8)
    st = stand_sprite(col, sel)
    sx, sy = W/2 + pan, 1600
    ax, ay = st.info["anchor"]; blit_sxy(L, st, sx, sy, 1, 1, 0)
    # pelouse papier devant
    d = ImageDraw.Draw(L); d.rectangle([0, 1660, W, H], fill=(52, 128, 70))
    for k in range(0, W, 120): d.rectangle([k, 1660, k + 60, H], fill=(60, 140, 78))
    d.rectangle([0, 1656, W, 1668], fill=(236, 236, 236))
    if t < T["s4"]:                                                # papier qui vole dans le stade vide
        for k in range(3):
            u = ((t - T["s3"])*.45 + k*.33) % 1; x = -80 + u*(W + 160); y = 1150 + 120*math.sin(u*9 + k) + k*120
            dd = ImageDraw.Draw(L); r_ = 22
            dd.polygon([(x - r_, y), (x, y - r_*.6), (x + r_, y + 4), (x, y + r_*.7)], fill=(236, 230, 214))
        return
    px, py = seat_screen(); px += sx - ax; py += sy - ay           # siège sélectionné à l'écran
    gone = T["s6"] + .35 < t < T["click"] + .05
    if not gone:
        t_in = T["s4"] + .35 if t < T["click"] else T["click"] + .05
        a = t - t_in
        if a > 0:
            fall = .28; yy = py - 1000*(1 - min(1, a/fall)**2) if a < fall else py
            q = .14*math.exp(-(a - fall)*14)*math.cos((a - fall)*30) if a > fall else 0
            fs = fan_sprite(club[0] if club else "rennes", t)
            k = 430/fs.height*1.55
            blit_sxy(L, fs, px, yy + 30, k*(1 + q), k*(1 - q), 0)
            if t > T["nom"] - .1 or t > T["click"]:
                s_ = M.spring(t - max(T["nom"] - .1, t_in + .2), .45, 14)
                blit_sxy(L, sign(club[0] if club and t > T["s5"] else None), px, py - 470 + 6*math.sin(t*3), s_, s_, 2*math.sin(t*2))
    puff(L, t, T["s6"] + .3, px, py - 120)
    puff(L, t, T["click"], px, py - 120, col=(255, 230, 120))
    if T["s6"] + .5 < t < T["s7"]:                                  # bouton s'abonner + curseur
        u = M.spring(t - T["s6"] - .5, .45, 14); pressed = t > T["click"]
        b = L_("+ S'ABONNER" if not pressed else "ABONNÉ ✓", 80, ROUGE if not pressed else (60, 160, 90), BLANC)
        pul = 1 + .05*math.sin(t*12) if not pressed else 1
        if pressed: q = .2*math.exp(-(t - T["click"])*12)*math.cos((t - T["click"])*30); pul = 1 - q
        b.draw(L, fr, W/2, 1760, u*pul, -2)
        cu = M.ease_io((t - T["s6"] - .7)/.9); cx_, cy_ = 960 + (700 - 960)*cu, 1900 + (1790 - 1900)*cu
        if t > T["click"] - .05 and t < T["click"] + .12: cy_ += 8
        d = ImageDraw.Draw(L); pts = [(0, 0), (0, 58), (15, 45), (26, 70), (36, 66), (25, 42), (44, 42)]
        d.polygon([(cx_ + x, cy_ + y) for x, y in pts], fill=BLANC, outline=NOIR, width=4)

def s_podium(L, fr, t):
    rays(L, W/2, 1100, t, .08 if t > T["s8"] else .04)
    pd = podium_sprite(); px, py = W/2, 1560; ax, ay = pd.info["anchor"]
    blit_sxy(L, pd, px, py, 1, 1, 0)
    for i, num in enumerate(("2", "1", "3")):
        x, y = podium_top(i); x += px - ax; y += py - ay
        L_(num, 120, None if False else (250, 248, 240), NOIR).draw(L, fr, x, y + 120, .9, 0)
        # écussons qui se mélangent puis « ? »
        if t < T["s8"]:
            n = CLUBS[(int(t*5) + i*2) % len(CLUBS)][0]; blit(L, logo(n, 140), x, y - 80 + 8*math.sin(t*6 + i), 1, 0)
        else:
            s_ = M.spring(t - T["s8"] - i*.1, .45, 14); L_("?", 110, CREME, NOIR).draw(L, fr, x, y - 80, s_, (-6, 4, 6)[i])
    if t > T["s8"] + .3:
        x, y = podium_top(1); x += px - ax; y += py - ay
        u = M.spring(t - T["s8"] - .3, .55, 9); sp = cup(int(t*12) % 24)
        blit_sxy(L, sp, x, y - 230 - 600*(1 - u) + 6*math.sin(t*3), .8, .8, 0)

def frame(fr, t):
    L = background().copy()
    if t < T["s3"]: s_intro(L, fr, t)
    elif t < T["s7"]: s_stade(L, fr, t)
    else: s_podium(L, fr, t)
    header(L, fr, t)
    M.draw_all(L, fr, t, ELS)
    # transition : flash papier bref sur les changements de décor (après 3 s seulement)
    for tc in (T["s3"], T["s7"]):
        if tc - .06 < t < tc + .12:
            a = 1 - abs(t - tc)/.12; ov = Image.new("RGBA", (W, H), (250, 246, 234, int(200*max(0, a)))); L.alpha_composite(ov)
    return L.convert("RGB")

# ------------------------------------------------------------------ sons (maison)
SFX_DIRS = [os.path.join(ROOT, "episodes", "lille_v5", "sfx"), os.path.join(ROOT, "episodes", "rennes", "sfx"), os.path.join(ROOT, "assets", "sfx")]
SFX = [(0, "braam", .8), (0, "crowd", .35), (.05, "stamp", .6), (T["s2"], "whoosh1", .5)] + [(T["s2"] + .05 + i*.04, "tok", .25) for i in range(6)] + [
       (T["decide"], "stamp", .6), (T["s3"] - .05, "page_tear", .5), (T["s3"], "wind", .6), (T["s3"] + .3, "stamp", .5),
       (T["s4"], "pop", .5), (T["s4"] + .55, "thud", .7), (T["s4"] + .6, "crowd", .35), (T["nom"], "typewriter", .4), (T["nom"] + .05, "pin", .5)] + [
       (T["s5"] + k*.2, "tok", .35) for k in range(16)] + [
       (T["s6"], "zap", .5), (T["s6"] + .3, "suck", .6), (T["s6"] + .55, "pop", .5), (T["click"], "ding", .4),
       (T["s7"] - .05, "page_tear", .5), (T["s7"] + .2, "drumroll", .45), (T["s8"], "stamp", .7),
       (T["s8"] + .3, "riser", .4), (T["s8"] + .75, "bang", .6), (T["s8"] + .8, "shimmer", .5), (T["s8"] + .85, "crowd", .5), (T["s8"] + 1.4, "notif", .5)]

def sfx_path(n):
    for d in SFX_DIRS:
        p = os.path.join(d, n + ".mp3")
        if os.path.exists(p): return p
    return None

VOICE = os.path.join(HERE, "voix", "ep1.mp3")
def voice_env():
    """Enveloppe de la voix (50 pts/s, 0..1) pour savoir quand Léo parle."""
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", VOICE, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.abs(np.frombuffer(r, np.int16).astype(np.float32)); a = a[:len(a)//160*160].reshape(-1, 160).mean(1)
    return a/(np.percentile(a, 95) + 1e-9)
BEDS = {"crowd", "wind", "braam", "drumroll", "riser", "shimmer"}      # sons longs : très bas sous la voix
def mix_audio(path, stems=None, sfx_k=1.0, norm=True):
    """Voix devant : bruitages à -12 dB environ, sons longs encore plus bas, coupés en grave/aigu (bande de la voix libérée)
    et écrasés par un ducking (sidechain) dès que Léo parle."""
    ins, flt = [], []
    env = voice_env()
    def talk(t, d=.35):                                           # Léo parle-t-il dans [t, t+d] ?
        a, b = int(t*50), int((t + d)*50); return env[a:b].max() if b > a and a < len(env) else 0
    items = [(t, sfx_path(n), g*sfx_k*(.05 if n in BEDS else .15)*(.25 if talk(t) > .5 else 1)) for t, n, g in SFX if sfx_path(n)]
    for i, (t, p, g) in enumerate(items):
        ins += ["-i", p]; flt.append(f"[{i}:a]aresample=44100,aformat=channel_layouts=stereo,volume={g},adelay={int(t*1000)}|{int(t*1000)}[a{i}]")
    n = len(items); ins += ["-i", VOICE]
    flt.append("".join(f"[a{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0,apad,atrim=0:{DUR},"
               "equalizer=f=2500:t=q:w=1.2:g=-6,equalizer=f=250:t=q:w=1:g=-3[sfx]")
    flt.append(f"[{n}:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.0,apad,atrim=0:{DUR},asplit=3[v1][v2][v3]")
    flt.append("[sfx][v1]sidechaincompress=threshold=0.01:ratio=20:attack=5:release=350:makeup=1[duck]")
    flt.append("[duck][v2]amix=inputs=2:normalize=0," + ("loudnorm=I=-14:TP=-1.5" if norm else "anull") + "[out]")
    if stems: flt.append(f"[v3]anull[vo]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-filter_complex", ";".join(flt), "-map", "[out]", "-ac", "2", path]
    if stems: cmd += ["-map", "[vo]", stems]
    else: cmd[cmd.index(";".join(flt))] = ";".join(flt).replace(",asplit=3[v1][v2][v3]", ",asplit=2[v1][v2]")
    subprocess.run(cmd, check=True)

def render_all():
    os.makedirs(OUT, exist_ok=True); vid = os.path.join(OUT, "_v.mp4"); aud = os.path.join(OUT, "_a.m4a")
    mix_audio(aud)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", vid], stdin=subprocess.PIPE)
    for fr in range(int(DUR*FPS)):
        p.stdin.write(frame(fr, fr/FPS).tobytes())
    p.stdin.close(); p.wait()
    out = os.path.join(OUT, "ep1.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", aud, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    os.remove(vid); os.remove(aud); return out

def stills():
    ts = [0, 1.2, 2.6, 3.9, 5.0, 6.4, 7.6, 8.8, 9.5, 10.5, 11.4, 12.2, 13.6, 16.5]
    sh = Image.new("RGB", (270*7, 480*2))
    for i, t in enumerate(ts): sh.paste(frame(int(t*FPS), t).resize((270, 480)), ((i % 7)*270, (i//7)*480))
    p = "/tmp/claude-0/sup_sheet.jpg"; sh.save(p, quality=85); return p

if __name__ == "__main__":
    print(stills() if "--stills" in sys.argv else render_all())
