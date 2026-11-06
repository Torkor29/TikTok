"""« CE QUIZ FOOT DEVIENT DE PLUS EN PLUS DUR — À QUEL NIVEAU TU BLOQUES ? » (~48 s, 8 niveaux, tous publics, pas que le PSG).
Mécanique : jauge des 8 niveaux en haut, fond qui « chauffe » (vert -> violet), question sur carte papier, 1,1 s de chrono,
la silhouette noire se révèle en couleur à la réponse. Fin : « T'AS BLOQUÉ À QUEL NIVEAU ? » + partage.
DA papier (bandes déchirées, photos réalistes découpées), voix Léo, bruitages synthétisés, pas de musique.
  python3 episodes/quiz_niveaux/textes.py      (voix avec temps de réflexion)
  python3 episodes/quiz_niveaux/quiz_niveaux.py [--stills]"""
import sys, os, math, subprocess, random, json
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, HERE)
import engine as E
import karaoke as KA
from paper_cut import paper_player
import textes as T
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS, SR = 1080, 1920, 30, 48000
GOLD = (255, 204, 70); RED = (214, 40, 50); CREAM = (250, 246, 236); INK = (24, 22, 28); GREEN = (40, 160, 80)
COLS = [(40, 160, 80), (110, 175, 50), (225, 175, 30), (240, 135, 30), (230, 85, 35), (210, 40, 50), (160, 30, 75), (70, 22, 95)]
ENDC = (26, 18, 52)
TAGS = ["FACILE", "FACILE", "MOYEN", "MOYEN", "DUR", "DUR", "TRÈS DUR", "IMPOSSIBLE"]
QS = ["LE CLUB DE MBAPPÉ ?", "QUI A MIS UN COUP DE TÊTE EN FINALE DU MONDIAL 2006 ?", "COMBIEN DE BALLONS D'OR POUR MESSI ?",
      "LE SEUL CLUB FRANÇAIS CHAMPION D'EUROPE AVANT LE PSG ?", "LE BALLON D'OR 2024 ?", "LE SEUL GARDIEN BALLON D'OR ?",
      "QUI A MARQUÉ LE 1er BUT DE L'HISTOIRE DE LA COUPE DU MONDE ?", "LE 1er CLUB CHAMPION D'EUROPE (1956) ?"]
ANS = ["REAL MADRID", "ZIDANE", "8 BALLONS D'OR", "L'OM (1993)", "RODRI", "LEV YACHINE (1963)", "LUCIEN LAURENT", "REAL MADRID"]
WD = KA.Words(T.TEXTE, T.VOIX); CU = json.load(open(T.CUTS)); TH = CU["think"]
PAUSE = [c + k*TH for k, c in enumerate(CU["cuts"])]               # début du blanc ajouté (chrono) dans la voix finale
REVEAL = [p + TH + .02 for p in PAUSE]
LSTART = [WD.line(2*k + 1)[0] - .12 for k in range(8)]
END0 = WD.line(17)[0] - .1; ENVOIE = WD.t(17, "envoie") - .05; TOTAL = WD.end + .9
OUT = os.path.join(ROOT, "output", "quiz_niveaux")
_c = {}
def font(px, name="LilitaOne-Regular.ttf"):
    k = (px, name)
    if k not in _c:
        p = os.path.join(ROOT, "assets", "fonts", name)
        _c[k] = ImageFont.truetype(p if os.path.exists(p) else os.path.join("/tmp/edu-assets/fonts", name), px)
    return _c[k]
def LB(txt, size, fg, bg, kind="title", maxw=960):
    k = ("lb", txt, size, fg, bg)
    if k not in _c: _c[k] = E.Label(txt, f"qn{txt}{size}", E.font(kind, size), fg, bg, maxw=maxw, padx=28, pady=10, rough=2.5)
    return _c[k]
def cut(n, h):
    k = ("cut", n, h)
    if k not in _c: p = os.path.join(ROOT, "assets", "photos", n + ".png"); _c[k] = paper_player(p, (0, 0) + Image.open(p).size, h, real=True)
    return _c[k]
def silhouette(n, h):
    """Même découpe, remplie d'encre (contour papier blanc gardé) : on devine la forme avant la réponse."""
    k = ("sil", n, h)
    if k not in _c:
        s = cut(n, h); a = np.array(s); al = a[..., 3]
        core = np.array(Image.fromarray(al).filter(ImageFilter.MinFilter(15)))
        a[..., :3] = np.where((core > 128)[..., None], np.array([22, 20, 34], np.uint8), np.array([250, 246, 236], np.uint8))
        im = Image.fromarray(a); im.info["anchor"] = s.info.get("anchor", (s.width/2, s.height)); _c[k] = im
    return _c[k]
def sticker(n, h):
    k = ("st", n, h)
    if k not in _c:
        im = Image.open(os.path.join(ROOT, "assets", "logos", n + "_sticker.png")).convert("RGBA"); s = h/im.height
        im = im.resize((int(im.width*s), h), Image.LANCZOS); im.info["anchor"] = (im.width/2, im.height/2); _c[k] = im
    return _c[k]
def mystery(h):
    k = ("my", h)
    if k not in _c:
        im = E.paper_sprite(E.ellipse_pts(h, h), (60, 56, 80), seed=5, rough=1.5); ax, ay = im.info["anchor"]
        ImageDraw.Draw(im).text((ax, ay + 8), "?", font=font(int(h*.62)), fill=CREAM, anchor="mm"); _c[k] = im
    return _c[k]
BALL = E.Paper(E.ellipse_pts(86, 86), (240, 190, 50), "bdo", rough=1.0).add(lambda d, a: (d.ellipse([a[0] - 30, a[1] - 30, a[0] + 30, a[1] + 30], outline=(190, 140, 30), width=4),
        d.ellipse([a[0] - 22, a[1] - 26, a[0] - 4, a[1] - 10], fill=(255, 240, 170))))
def jersey():
    if "jer" not in _c:
        pts = [(-170, -200), (-60, -230), (60, -230), (170, -200), (260, -80), (190, -20), (150, -70), (150, 230), (-150, 230), (-150, -70), (-190, -20), (-260, -80)]
        im = E.paper_sprite(pts, (26, 26, 30), seed=9, rough=1.6); ax, ay = im.info["anchor"]; d = ImageDraw.Draw(im)
        d.text((ax, ay + 20), "1", font=font(230), fill=(240, 240, 240), anchor="mm"); d.ellipse([ax - 40, ay - 240, ax + 40, ay - 200], fill=(26, 26, 30)); _c["jer"] = im
    return _c["jer"]
def oldball():
    if "ob" not in _c:
        im = E.paper_sprite(E.ellipse_pts(330, 330), (150, 90, 45), seed=11, rough=1.4); ax, ay = im.info["anchor"]; d = ImageDraw.Draw(im)
        for k in range(-1, 2): d.arc([ax - 150 + abs(k)*60, ay - 160, ax + 150 - abs(k)*60, ay + 160], 0, 360, fill=(90, 50, 20), width=6)
        d.line([(ax - 160, ay), (ax + 160, ay)], fill=(90, 50, 20), width=6)
        for k in range(5): d.line([(ax - 20, ay - 60 + k*30), (ax + 20, ay - 60 + k*30)], fill=(235, 220, 190), width=5)
        _c["ob"] = im
    return _c["ob"]
def bg(col):
    k = ("bg", col)
    if k not in _c:
        a = np.zeros((H, W, 3), np.float32); a[:] = col; a *= (.86 + .2*E._lowfreq(W, H, 4, 70))[..., None]
        yy = np.linspace(0, 1, H)[:, None, None]; a = a*(1.08 - .25*yy)
        rng = np.random.default_rng(2); a += ((rng.random((H, W)) > .985)*10)[..., None]
        _c[k] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    return _c[k]
def rays(cv, t, a=.5, cy=1350):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); cx = W/2
    for k in range(14):
        an = t*.3 + k*2*math.pi/14; d.polygon([(cx, cy), (cx + 1800*math.cos(an - .09), cy + 1800*math.sin(an - .09)), (cx + 1800*math.cos(an + .09), cy + 1800*math.sin(an + .09))], fill=(255, 255, 255, int(34*a)))
    cv.alpha_composite(ov)
def wrap(txt, f, maxw):
    lines, cur = [], ""
    for w in txt.split():
        if f.getlength((cur + " " + w).strip()) <= maxw: cur = (cur + " " + w).strip()
        else: lines.append(cur); cur = w
    return lines + [cur]
def card(k):
    """Carte question (papier crème, encre), hauteur selon le nombre de lignes."""
    key = ("card", k)
    if key not in _c:
        f = font(68); ls = wrap(QS[k], f, 860); h = 70 + 82*len(ls)
        im = E.paper_sprite(E.rect_pts(960, h), CREAM, seed=20 + k, rough=2.0); ax, ay = im.info["anchor"]; d = ImageDraw.Draw(im)
        for i, l in enumerate(ls): d.text((ax, ay - 82*(len(ls) - 1)/2 + 82*i), l, font=f, fill=INK, anchor="mm")
        _c[key] = im
    return _c[key]
def meter(cv, fr, t, lvl, y=232):
    """Jauge des 8 niveaux : les passés pleins, le niveau en cours qui pulse, les suivants en creux."""
    d = ImageDraw.Draw(cv); x0, sw, gap = 76, 100, 16
    for i in range(8):
        x = x0 + i*(sw + gap); cur = i == lvl
        s = 1 + (.1*abs(math.sin(t*6)) if cur else 0); hw, hh = sw/2*s, 44*s; cx = x + sw/2
        if i <= lvl:
            d.rounded_rectangle([cx - hw + 5, y - hh + 7, cx + hw + 5, y + hh + 7], 16, fill=(0, 0, 0, 90))
            d.rounded_rectangle([cx - hw, y - hh, cx + hw, y + hh], 16, fill=COLS[i], outline=CREAM if cur else INK, width=6 if cur else 4)
            d.text((cx, y + 2), str(i + 1), font=font(int(56*s)), fill=CREAM, anchor="mm", stroke_width=3, stroke_fill=INK)
        else:
            d.rounded_rectangle([cx - hw, y - hh, cx + hw, y + hh], 16, fill=(0, 0, 0, 70), outline=(255, 255, 255, 120), width=3)
            d.text((cx, y + 2), str(i + 1), font=font(50), fill=(255, 255, 255, 150), anchor="mm")
def level_at(t):
    k = -1
    for i, s in enumerate(LSTART):
        if t >= s: k = i
    return k
def visual(cv, fr, k, t, rv):
    """Bas de l'écran : indice pendant la question, réponse en couleur ensuite."""
    ur = max(0.0, min(1.0, (t - REVEAL[k])/.3)); pop = E.ease_out_back(ur, 2.2) if rv else 0; bob = 8*math.sin(t*2.2)
    def person(n, h=780, sil=True):
        if rv: E.blit(cv, cut(n, h), W/2, 1935 + bob, .94 + .06*pop)
        else: E.blit(cv, silhouette(n, h) if sil else cut(n, h), W/2, 1935 + bob, 1.0)
    if k == 0:
        person("bdo/mbappe", 800, sil=False)
        if rv: E.blit(cv, sticker("real", 300), 215, 1300, pop, -8)
    elif k == 1: person("real/zidane")
    elif k == 2:
        person("bdo/messi", 760, sil=False)
        if rv:
            for i in range(8):
                u = max(0.0, min(1.0, (t - REVEAL[k] - i*.06)/.25)); BALL.draw(cv, fr, 150 + i*111, 1112, E.ease_out_back(u, 2.4))
    elif k == 3:
        if rv: E.blit(cv, sticker("om", 560), W/2, 1450 + bob, pop, -4)
        else: E.blit(cv, mystery(440), W/2, 1450 + bob, 1, 6*math.sin(t*3))
    elif k == 4: person("bdo/rodri")
    elif k == 5:
        if rv: E.blit(cv, jersey(), W/2, 1470 + bob, pop*1.1, -5)
        else: E.blit(cv, mystery(440), W/2, 1450 + bob, 1, 6*math.sin(t*3))
    elif k == 6:
        if rv: E.blit(cv, oldball(), 330, 1500 + bob, pop, t*40); E.blit(cv, sticker("fff_bleu", 480), 760, 1470 + bob, pop, 6); LB("13 JUILLET 1930", 60, CREAM, INK).draw(cv, fr, W/2, 1790, pop, -3)
        else: E.blit(cv, mystery(440), W/2, 1450 + bob, 1, 6*math.sin(t*3))
    elif k == 7:
        if rv: E.blit(cv, sticker("real", 560), W/2, 1450 + bob, pop, 4)
        else: E.blit(cv, mystery(440), W/2, 1450 + bob, 1, 6*math.sin(t*3))
def frame(fr):
    t = fr/FPS; k = level_at(t); cv = None
    if t >= END0:                                                  # FIN
        cv = bg(ENDC).copy(); rays(cv, t, .6, 1500)
        for i, (n, x) in enumerate([("real/zidane", 190), ("bdo/messi", 420), ("bdo/rodri", 660), ("bdo/mbappe", 890)]):
            u = max(0.0, min(1.0, (t - END0 - i*.08)/.35)); E.blit(cv, cut(n, 620), x, 1935 + 400*(1 - E.ease_out_back(u, 1.6)), 1.0)
        meter(cv, fr, t, 7)
        u = min(1, (t - END0)/.3); LB("T'AS BLOQUÉ", 130, INK, GOLD).draw(cv, fr, W/2, 450, E.ease_out_back(u, 2), -3)
        LB("À QUEL NIVEAU ?", 110, CREAM, RED).draw(cv, fr, W/2, 620, E.ease_out_back(max(0, min(1, (t - END0 - .25)/.3)), 2), 2)
        LB("DIS-LE EN COMMENTAIRE", 66, INK, CREAM).draw(cv, fr, W/2, 790, max(0, min(1, (t - END0 - .9)/.3)), -2)
        if t >= ENVOIE: LB("ENVOIE ÇA À TON POTE", 64, CREAM, (60, 90, 170)).draw(cv, fr, W/2, 930, E.ease_out_back(min(1, (t - ENVOIE)/.3), 2), 2)
        return np.asarray(cv.convert("RGB")).tobytes()
    if k < 0:                                                      # HOOK (image 0 : défi + visage + jauge qui s'allume)
        cv = bg(COLS[0]).copy(); rays(cv, t, .7)
        E.blit(cv, cut("bdo/mbappe", 860), W/2, 1935 + 6*math.sin(t*3), 1.0 + .02*t)
        lit = min(7, int(t/.32)); meter(cv, fr, t, lit)
        LB("QUIZ FOOT", 170, INK, GOLD).draw(cv, fr, W/2, 420, 1 + .03*math.sin(t*5), -3)
        LB("DE PLUS EN PLUS DUR", 84, CREAM, RED).draw(cv, fr, W/2, 600, 1, 2)
        dm = WD.t(0, "dis") - .05
        if t >= dm: LB("À QUEL NIVEAU TU BLOQUES ?", 70, INK, CREAM).draw(cv, fr, W/2, 760, E.ease_out_back(min(1, (t - dm)/.3), 2), -2)
        return np.asarray(cv.convert("RGB")).tobytes()
    # NIVEAU k : le nouveau fond balaie l'ancien en 0,3 s (bande de papier en diagonale)
    cv = bg(COLS[k - 1] if k else COLS[0]).copy(); u = min(1.0, (t - LSTART[k])/.3)
    if u < 1:
        m = Image.new("L", (W, H), 0); xx = -300 + u*(W + 700)
        ImageDraw.Draw(m).polygon([(-10, -10), (xx + 260, -10), (xx, H + 10), (-10, H + 10)], fill=255); cv.paste(bg(COLS[k]), (0, 0), m)
    else: cv = bg(COLS[k]).copy()
    rv = t >= REVEAL[k]; rays(cv, t*(1 + k*.15), .5 + (.4 if rv else 0))
    visual(cv, fr, k, t, rv)
    meter(cv, fr, t, k)
    us = max(0.0, min(1.0, (t - LSTART[k] - .05)/.3)); LB(f"NIVEAU {k + 1}", 130, INK, GOLD).draw(cv, fr, W/2, 385, E.ease_out_back(us, 2.4), -3 + k % 2*6)
    LB(TAGS[k], 50, CREAM, INK).draw(cv, fr, W/2, 535, E.ease_out_back(max(0, min(1, (t - LSTART[k] - .2)/.3)), 2), 4 - k % 2*8)
    cd = card(k); uc = max(0.0, min(1.0, (t - LSTART[k] - .15)/.3)); ch = cd.height
    sh = 0
    if PAUSE[k] <= t < REVEAL[k]: sh = 5*math.sin(t*60)*((t - PAUSE[k])/TH)          # la carte frémit pendant le chrono
    E.blit(cv, cd, W/2 + sh, 600 + ch/2 - 20, .4 + .6*E.ease_out_back(uc, 1.8), 0)
    yb = 600 + ch - 20 + 70                                       # sous la carte : chrono puis réponse
    if PAUSE[k] <= t < REVEAL[k]:
        p = 1 - (t - PAUSE[k])/TH; d = ImageDraw.Draw(cv)
        d.rounded_rectangle([140, yb - 22, 940, yb + 22], 20, fill=(0, 0, 0, 110)); (d.rounded_rectangle([140, yb - 22, 140 + 800*p, yb + 22], 20, fill=CREAM if p > .35 else RED) if p > .06 else None)
    if rv:
        ua = min(1.0, (t - REVEAL[k])/.3); LB(ANS[k], 96, INK, GOLD, maxw=980).draw(cv, fr, W/2, yb + 10, E.ease_out_back(ua, 2.4), -2)
        E.particles(cv, fr, 100 + k, (W//2, int(yb)), min(1, (t - REVEAL[k])/.9), 26, 520, [GOLD, CREAM, (255, 255, 255)], 20, 700)
    return np.asarray(cv.convert("RGB")).tobytes()
def check_mark():
    if "ck" not in _c:
        im = E.paper_sprite(E.ellipse_pts(120, 120), GREEN, seed=3, rough=1.2); ax, ay = im.info["anchor"]
        ImageDraw.Draw(im).line([(ax - 30, ay), (ax - 8, ay + 24), (ax + 32, ay - 26)], fill=CREAM, width=14); _c["ck"] = im
    return _c["ck"]
# ---------------------------------------------------------------- SONS (synthétisés, propres, sous la voix)
def synth():
    n = int(TOTAL*SR); out = np.zeros(n, np.float32); rng = np.random.default_rng(3)
    def add(sig, t0, g=1.0):
        i = int(t0*SR); j = min(n, i + len(sig))
        if 0 <= i < n: out[i:j] += g*sig[:j - i]
    def tone(f, d, dec):
        tt = np.arange(int(d*SR))/SR; return np.sin(2*np.pi*f*tt)*np.exp(-tt*dec)
    def whoosh(d=.35, g=.3):
        x = rng.standard_normal(int(d*SR)).astype(np.float32); x = np.convolve(x, np.ones(24)/24, "same"); return x*np.sin(np.linspace(0, np.pi, len(x)))**2*g
    tt = np.arange(int(.6*SR))/SR                                 # impact d'ouverture : grave qui descend + souffle court
    add(np.sin(2*np.pi*(90 - 40*tt)*tt)*np.exp(-tt*6)*.7, 0.0); add(whoosh(.25, .25), 0.0)
    for i in range(8): add(tone(600 + 90*i, .09, 40)*.18, i*.32)  # la jauge s'allume (notes qui montent)
    click = tone(2200, .03, 150)*.6 + tone(1100, .03, 90)*.4
    for k in range(8):
        add(whoosh(), LSTART[k] - .05); add(tone(140 + 15*k, .25, 14)*.35, LSTART[k] + .1)
        for j in range(3): add(click, PAUSE[k] + j*TH/3, .45 + .1*j)     # chrono : 3 tics
        r = REVEAL[k]; add(tone(1047, .5, 7)*.3 + tone(1568, .5, 8)*.22, r); add(tone(2093, .4, 9)*.15, r + .07)
        for j in range(5): add(tone(rng.uniform(3000, 5000), .06, 60)*.08, r + .1 + j*.05)
    add(whoosh(.4, .3), END0 - .05); add(tone(880, .25, 12)*.3 + tone(1320, .25, 14)*.2, END0 + .2)
    return out
def build_audio(wav):
    import wave
    sf = OUT + "/_sfx.wav"; s = np.clip(synth(), -1, 1)
    with wave.open(sf, "wb") as w_: w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((s*32767).astype(np.int16).tobytes())
    fc = ("[0:a]aresample=48000,apad=whole_dur=%.2f[v];[1:a]volume=0.5[s];[v][s]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.89[a]" % TOTAL)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", T.VOIX, "-i", sf, "-filter_complex", fc, "-map", "[a]", "-ac", "2", "-ar", "48000", wav], check=True); os.remove(sf)
def warm():
    for n, h in [("bdo/mbappe", 800), ("bdo/mbappe", 860), ("bdo/messi", 760), ("real/zidane", 780), ("bdo/rodri", 780)] + [(n, 620) for n in ("real/zidane", "bdo/messi", "bdo/rodri", "bdo/mbappe")]: cut(n, h)
    for n in ("real/zidane", "bdo/rodri"): silhouette(n, 780)
def main():
    os.makedirs(OUT, exist_ok=True); v, a = OUT + "/_v.mp4", OUT + "/_a.wav"; build_audio(a); warm()
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", v], stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for b in pool.imap(frame, range(int(TOTAL*FPS)), chunksize=8): pr.stdin.write(b)
    pr.stdin.close(); pr.wait(); o = OUT + "/quiz_niveaux.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", o], check=True); os.remove(v); os.remove(a); print(o, round(TOTAL, 2))
def stills(ts, path, w=360):
    h = int(w*H/W); sh = Image.new("RGB", (w*min(6, len(ts)), h*math.ceil(len(ts)/6)))
    for j, t in enumerate(ts): sh.paste(Image.frombytes("RGB", (W, H), frame(int(t*FPS))).resize((w, h)), ((j % 6)*w, (j//6)*h))
    sh.save(path, quality=88); print(path)
if __name__ == "__main__":
    if "--stills" in sys.argv:
        ts = [0.0, 2.5] + sum([[LSTART[k] + .6, PAUSE[k] + .6, REVEAL[k] + .5] for k in range(8)], []) + [END0 + .8, TOTAL - .2]
        stills(ts, sys.argv[sys.argv.index("--stills") + 1])
    else: main()
