"""« LE VRAI SALAIRE DE MBAPPÉ, SECONDE PAR SECONDE » (~25 s) : cagnotte qui monte en direct, horloge qui accélère
(1 s → 1 min → 9 min = un SMIC → 1 h → nuit de 8 h → 1 jour), pluie de billets, pile qui grossit, puis Ronaldo ×3.
Base : estimation Forbes 2025 des revenus de Mbappé (salaire + primes + sponsors) = 81,16 M€/an -> 2,57 €/s.
DA papier (fond nuit, rayons dorés, étiquettes en bandes de papier), pas de musique, voix Léo.
  python3 episodes/salaire_mbappe/salaire_mbappe.py [--stills]"""
import sys, os, math, subprocess, random
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import engine as E
import karaoke as KA
from paper_cut import paper_player
import numpy as np
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 30
PER_S = 81.16e6/(365*24*3600)                                     # 2,5735 €/s
NAVY = (16, 26, 60); GOLD = (255, 204, 70); GREEN = (60, 170, 90); RED = (214, 40, 50); CREAM = (250, 246, 236); INK = (24, 22, 28)
TEXTE = ["Le vrai salaire de Mbappé, seconde par seconde.", "Une seconde : deux euros cinquante.", "Une minute : cent cinquante euros.",
         "Neuf minutes : un SMIC.", "Une heure : plus de neuf mille euros.", "Pendant que tu dors, huit heures : soixante-quatorze mille euros.",
         "Une journée : deux cent vingt mille euros.", "Et Ronaldo gagne trois fois plus.", "Toi, il te faut combien de temps pour gagner ça ? Dis-le en commentaire."]
VOIX = os.path.join(HERE, "voix", "voix.mp3"); WD = KA.Words(TEXTE, VOIX); L0 = [WD.line(i)[0] for i in range(len(TEXTE))]
TOTAL = WD.end + 1.0
# temps « de jeu » (secondes de salaire) atteint au début de chaque palier : la cagnotte arrive pile sur le chiffre dit
MARK = [(L0[0], 0), (L0[1] + .35, 1), (L0[2] + .3, 60), (L0[3] + .3, 540), (L0[4] + .3, 3600), (L0[5] + 1.0, 8*3600), (L0[6] + .3, 86400)]
def game(t):
    """Secondes de salaire écoulées : 1 s réelle = 1 s au début, puis accélération exponentielle entre les paliers."""
    if t <= MARK[0][0]: return 0.0
    for (ta, ga), (tb, gb) in zip(MARK, MARK[1:]):
        if t < tb:
            hold = 1.4 if ga >= 1 else 0                              # la cagnotte marque une pause sur chaque palier (le temps de le dire)
            u = max(0.0, (t - ta - hold)/(tb - ta - hold)); u = u*u*(3 - 2*u)
            return ga + (gb - ga)*u if ga < 1 else math.exp(math.log(ga) + (math.log(gb) - math.log(ga))*u)
    return MARK[-1][1]
def eur(x):
    s = f"{x:,.2f}" if x < 1000 else f"{x:,.0f}"
    return s.replace(",", " ").replace(".", ",") + " €"
def clock(g):
    g = int(round(g)); return f"{g//3600:02d}:{g//60 % 60:02d}:{g % 60:02d}"
_c = {}
def font(px, name="LilitaOne-Regular.ttf"):
    k = (px, name)
    if k not in _c:
        p = os.path.join(ROOT, "assets", "fonts", name)
        _c[k] = ImageFont.truetype(p if os.path.exists(p) else os.path.join("/tmp/edu-assets/fonts", name), px)
    return _c[k]
def LB(txt, size, fg, bg, kind="title"):
    k = ("lb", txt, size, fg, bg)
    if k not in _c: _c[k] = E.Label(txt, f"sal{txt}{size}", E.font(kind, size), fg, bg, padx=28, pady=10, rough=2.5)
    return _c[k]
def bg():
    if "bg" not in _c:
        rng = np.random.default_rng(2); a = np.zeros((H, W, 3), np.float32); a[:] = NAVY; a *= (.9 + .18*E._lowfreq(W, H, 4, 70))[..., None]
        sp = rng.random((H, W)); a += ((sp > .985)*16)[..., None]; _c["bg"] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    return _c["bg"]
def cut(n, h):
    k = ("cut", n, h)
    if k not in _c: p = os.path.join(ROOT, "assets", "photos", n + ".png"); _c[k] = paper_player(p, (0, 0) + Image.open(p).size, h, real=True)   # boîte explicite : clé de cache unique
    return _c[k]
BILL = E.Paper(E.rect_pts(150, 74), (120, 184, 120), "bill", rough=1.2).add(lambda d, a: (d.rectangle([a[0] - 68, a[1] - 30, a[0] + 68, a[1] + 30], outline=(60, 120, 60), width=3),
        d.ellipse([a[0] - 20, a[1] - 20, a[0] + 20, a[1] + 20], outline=(60, 120, 60), width=4), d.text((a[0], a[1]), "€", font=font(34), fill=(50, 110, 50), anchor="mm")))
def rays(cv, t, a=.5):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); cx, cy = W/2, 900
    for k in range(16):
        an = t*.25 + k*2*math.pi/16; d.polygon([(cx, cy), (cx + 1600*math.cos(an - .08), cy + 1600*math.sin(an - .08)), (cx + 1600*math.cos(an + .08), cy + 1600*math.sin(an + .08))], fill=(255, 210, 90, int(40*a)))
    cv.alpha_composite(ov)
MILESTONE = [(L0[2] + .3, "1 MINUTE", GOLD, INK), (L0[3] + .3, "= UN SMIC", RED, CREAM), (L0[4] + .3, "1 HEURE", GOLD, INK),
             (L0[5] + 1.0, "PENDANT QUE TU DORS", (90, 110, 200), CREAM), (L0[6] + .3, "1 JOUR", GREEN, CREAM)]
COIN = E.Paper(E.ellipse_pts(70, 70), (240, 190, 50), "coin", rough=1.0).add(lambda d, a: (d.ellipse([a[0] - 26, a[1] - 26, a[0] + 26, a[1] + 26], outline=(190, 140, 30), width=4),
        d.text((a[0], a[1] + 1), "€", font=font(40), fill=(170, 120, 20), anchor="mm")))
def speed_at(t): return 0 if t < MARK[1][0] + .5 else min(1, math.log10(max(10, (game(t + .1) - game(t))/.1))/4)
def since_mile(t):
    p = [tm for (tm, *_r) in MILESTONE if tm <= t]; return t - max(p) if p else 9.0
def clock_face(cv, fr, g, t, x=W/2, y=300, r=120):
    """Horloge en papier : la trotteuse, puis les aiguilles, s'emballent quand le temps accélère (traînée)."""
    d = ImageDraw.Draw(cv); d.ellipse([x - r - 10, y - r - 4, x + r + 10, y + r + 16], fill=(8, 10, 24)); d.ellipse([x - r, y - r, x + r, y + r], fill=CREAM, outline=INK, width=8)
    for k in range(12):
        an = k*math.pi/6; d.line([(x + r*.78*math.cos(an), y + r*.78*math.sin(an)), (x + r*.92*math.cos(an), y + r*.92*math.sin(an))], fill=INK, width=6 if k % 3 == 0 else 3)
    def hand(frac, ln, wd, col):
        an = frac*2*math.pi - math.pi/2; d.line([(x, y), (x + ln*math.cos(an), y + ln*math.sin(an))], fill=col, width=wd)
    fast = speed_at(t)
    for k in range(5 if fast > .3 else 1):                     # traînée de la trotteuse quand ça va vite
        gg = g - k*fast*8; hand((gg % 60)/60, r*.86, 4, (214, 40, 50) if k == 0 else (230, 160, 160))
    hand((g % 3600)/3600, r*.74, 9, INK); hand((g % 43200)/43200, r*.5, 12, INK); d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=RED)
_dg = {}
def digit_img(ch, size):
    k = (ch, size)
    if k not in _dg:
        f = font(size); w = int(f.getlength("0")*1.02) if ch.isdigit() else int(f.getlength(ch)) + 4; h = int(size*1.15)
        im = Image.new("RGBA", (w + 12, h + 14), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
        dd.text(((w + 12)/2 + 7, h/2 + 12), ch, font=f, fill=(10, 8, 20), anchor="mm"); dd.text(((w + 12)/2, h/2 + 4), ch, font=f, fill=GOLD, anchor="mm"); _dg[k] = im
    return _dg[k]
def odometer(cv, money, x, y, size, scale=1.0):
    """Compteur à rouleaux : chaque chiffre défile verticalement (le dernier en continu) — effet hypnotique."""
    cents = money < 1000; v = round(money*100) if cents else round(money); n = max(3 if cents else 1, len(str(int(v))))
    s = f"{int(v):0{n}d}"; chars = []
    for i, ch in enumerate(s):
        pos = len(s) - 1 - i
        if cents and pos == 1: chars.append(","); 
        chars.append(("d", pos))
        if not cents and pos % 3 == 0 and pos: chars.append(" ")
    chars.append(" "); chars.append("€")
    size = int(size*scale); ims = []
    for c in chars:
        if isinstance(c, tuple):
            pos = c[1]; val = v/10**pos; dgt = int(val) % 10; fr_ = 0.0                     # chiffres nets (ils défilent déjà très vite)
            a, b_ = digit_img(str(dgt), size), digit_img(str((dgt + 1) % 10), size); hh = a.height
            col = Image.new("RGBA", (a.width, hh), (0, 0, 0, 0)); off = int(fr_*hh*.82)
            col.alpha_composite(a, (0, -off)); col.alpha_composite(b_, (0, int(hh*.82) - off)); ims.append(col)
        else: ims.append(digit_img(c, size) if c != " " else Image.new("RGBA", (int(size*.22), 10), (0, 0, 0, 0)))
    tw = sum(i.width for i in ims); xx = int(x - tw/2)
    if tw > W - 60:
        return odometer(cv, money, x, y, size*(W - 60)/tw, 1.0)
    for im in ims: cv.alpha_composite(im, (xx, int(y - im.height/2))) if im.height > 20 else None; xx += im.width
def payslip(cv, fr, x, y, s):
    if s <= .02: return
    im = E.paper_sprite(E.rect_pts(260, 300), CREAM, seed=3, rough=2); ax, ay = im.info["anchor"]; d = ImageDraw.Draw(im)
    d.rectangle([ax - 130, ay - 150, ax + 130, ay - 100], fill=(60, 90, 160)); d.text((ax, ay - 125), "FICHE DE PAIE", font=font(30), fill=CREAM, anchor="mm")
    for k in range(5): d.line([(ax - 100, ay - 60 + k*34), (ax + 100 - (k % 2)*40, ay - 60 + k*34)], fill=(190, 186, 176), width=5)
    d.text((ax, ay + 110), "1 MOIS", font=font(44), fill=RED, anchor="mm"); E.blit(cv, im, x, y, s, -8)
def frame(fr):
    t = fr/FPS; g = game(t); money = g*PER_S; speed = speed_at(t); end = t >= L0[7] - .05
    sleep = MILESTONE[3][0] - .6 <= t < MILESTONE[4][0] - .2
    cv = bg().copy()
    if sleep: cv.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 20, 130)))
    rays(cv, t*(1 + 3*speed), .3 + .5*speed)
    sm = since_mile(t); slam = 1 + .18*math.exp(-sm*9) if sm < 1 else 1.0
    # pluie de billets ET de pièces (densité ∝ accélération), petite rafale à chaque palier
    rnd = random.Random(7); n = int(3 + 34*speed + (40*math.exp(-sm*3) if sm < 1.5 else 0)) if t > L0[1] else 0
    for k in range(n):
        x = rnd.uniform(0, W); sp = rnd.uniform(500, 1000)*(1 + speed); y = (rnd.uniform(0, H) + t*sp) % (H + 200) - 100
        spr = (COIN if k % 3 == 0 else BILL).v[E.boil(fr)]; E.blit(cv, spr, x + 30*math.sin(t*3 + k), y, .6 if k % 3 == 0 else .7, rnd.uniform(-40, 40) + t*rnd.uniform(-90, 90))
    # deux piles (billets + pièces) qui montent, avec rebond
    hpile = int(min(620, 70*math.log10(1 + money))) if money > 1 else 0
    for side in (-1, 1):
        for j in range(0, hpile, 16): E.blit(cv, (COIN if (j//16) % 4 == 3 else BILL).v[(j//16) % 3], W/2 + side*330 + ((j*7) % 13 - 6), 1700 - j*(1 + .03*math.exp(-sm*8)), .9, ((j*13) % 9) - 4)
    if not end:
        E.blit(cv, cut("bdo/mbappe", 820), W/2, 1930 + 10*math.sin(t*2), 1.0 + .01*math.sin(t*3))
        if sleep:                                                 # nuit : lune + « Zzz » au-dessus de lui
            dd = ImageDraw.Draw(cv); dd.ellipse([70, 1260, 230, 1420], fill=(250, 240, 200)); dd.ellipse([110, 1240, 270, 1400], fill=(10, 16, 44))
            for k in range(3): dd.text((740 + k*50, 1250 - k*60 - 20*math.sin(t*3 + k)), "Z", font=font(70 - k*12), fill=CREAM)
    else:
        u = min(1, (t - L0[7] + .05)/.3); E.blit(cv, cut("real/ronaldo", 860), W/2, 1930 + 600*(1 - u), 1.0)
        LB("× 3", 170, INK, GOLD).draw(cv, fr, 925, 1150, E.ease_out_back(u, 2.2), -6)
    if t < L0[1]:                                                 # image 0
        LB("LE VRAI SALAIRE DE", 70, CREAM, INK).draw(cv, fr, W/2, 330, 1, -2); LB("MBAPPÉ", 180, INK, GOLD).draw(cv, fr, W/2, 500, 1, 2)
        LB("SECONDE PAR SECONDE", 64, CREAM, RED).draw(cv, fr, W/2, 660, 1, -2); odometer(cv, 0, W/2, 830, 200)
    elif not end:
        for (tm, lab, bgc, fgc) in MILESTONE:                     # paillettes d'abord : jamais par-dessus les chiffres
            if tm - .05 <= t < tm + 1.6: E.particles(cv, fr, int(tm*10), (W//2, 640), min(1, (t - tm)/1.0), 26, 520, [GOLD, (255, 236, 140), CREAM], 22, 600)
        clock_face(cv, fr, g, t); LB(clock(g), 56, CREAM, INK, "mono").draw(cv, fr, W/2, 470, 1, -2)
        odometer(cv, money, W/2, 640, 196, slam)
        for (tm, lab, bgc, fgc) in MILESTONE:
            if tm - .05 <= t < tm + 1.6: LB(lab, 80, fgc, bgc).draw(cv, fr, W/2, 862, E.ease_out_back(min(1, (t - tm + .05)/.3), 2.2), -3)
        tsm = MILESTONE[1][0]
        if tsm - .1 <= t < tsm + 1.8: payslip(cv, fr, 150, 1225, E.ease_out_back(min(1, (t - tsm + .1)/.35), 2))
        tj = MILESTONE[4][0]
        if t >= tj - .1:                                          # page de calendrier qui tombe
            u = min(1, (t - tj + .1)/.35); dd = ImageDraw.Draw(cv); x0, y0 = 810, 1250 - int(300*(1 - E.ease_out_back(u, 1.6)))
            dd.rectangle([x0, y0, x0 + 200, y0 + 220], fill=CREAM, outline=INK, width=5); dd.rectangle([x0, y0, x0 + 200, y0 + 60], fill=RED)
            dd.text((x0 + 100, y0 + 30), "1 JOUR", font=font(38), fill=CREAM, anchor="mm"); dd.text((x0 + 100, y0 + 140), "24 H", font=font(80), fill=INK, anchor="mm")
    else:
        if t > L0[8]: LB("ET TOI ?", 120, INK, GOLD).draw(cv, fr, W/2, 560, E.ease_out_back(min(1, (t - L0[8])/.3), 2), -3); LB("DIS-LE EN COMMENTAIRE", 64, CREAM, RED).draw(cv, fr, W/2, 720, min(1, max(0, (t - L0[8] - .6)/.3)), 2)
        else: LB("RONALDO", 150, CREAM, RED).draw(cv, fr, W/2, 560, 1, -2)
    d = ImageDraw.Draw(cv); f26 = font(26, "BebasNeue-Regular.ttf")                    # source : 2 petites lignes en haut à droite, loin de l'horloge
    d.text((W - 36, 176), "Source : Forbes 2025", font=f26, fill=(150, 156, 180), anchor="rm"); d.text((W - 36, 204), "salaire + primes + sponsors", font=f26, fill=(150, 156, 180), anchor="rm")
    KA.caption(cv, WD, t, 930 if end else 1030, 78)                                 # sous-titres entre l'étiquette et la tête du joueur
    return np.asarray(cv.convert("RGB")).tobytes()
SR = 48000
def synth():
    """Bruitages synthétisés (propres, hypnotiques) : tic-tac qui accélère, montée de tension entre les paliers, « ka-ching »
    à chaque palier, petites pièces pendant la pluie, souffle sur Ronaldo. Rien avant que le compteur démarre."""
    n = int(TOTAL*SR); out = np.zeros(n, np.float32); rng = np.random.default_rng(1)
    def add(sig, t0, g=1.0):
        i = int(t0*SR); j = min(n, i + len(sig))
        if 0 <= i < n: out[i:j] += g*sig[:j - i]
    def tone(f, d, dec):
        tt = np.arange(int(d*SR))/SR; return np.sin(2*np.pi*f*tt)*np.exp(-tt*dec)
    click = tone(2400, .03, 140)*.6 + tone(1200, .03, 90)*.4
    t, last = MARK[1][0] - 1, -1.0                               # tic-tac : un tic par seconde « de jeu », au plus 12 par seconde réelle
    while t < L0[7] - .2:
        gs = int(game(t))
        if gs != int(game(max(0, t - 1/SR*400))) and t - last > 1/12: add(click, t, .35); last = t
        t += 1/240
    for (ta, ga), (tb, gb) in zip(MARK[1:], MARK[2:]):           # montée de tension (sinus qui monte) pendant l'accélération
        a = ta + (1.4 if ga >= 1 else 0); d = tb - a
        if d <= .2: continue
        tt = np.arange(int(d*SR))/SR; f = 180*2**(tt/d*2); ph = 2*np.pi*np.cumsum(f)/SR
        add(np.sin(ph)*(tt/d)**2*.12 + np.sin(ph*2)*(tt/d)**2*.04, a)
    for (tm, *_r) in MILESTONE:                                   # ka-ching : cloche 2 notes + pièces
        add(tone(1568, .7, 6)*.35 + tone(2093, .7, 7)*.25, tm); add(tone(2637, .5, 9)*.2, tm + .08)
        for k in range(6): add(tone(rng.uniform(3000, 4800), .08, 50)*.18, tm + .1 + k*.05)
    t = L0[2]
    while t < L0[7]:                                              # petites pièces pendant la pluie
        add(tone(rng.uniform(3200, 5200), .05, 70)*.08, t); t += rng.uniform(.12, .4)
    noise = rng.standard_normal(int(.5*SR)).astype(np.float32); env = np.sin(np.linspace(0, np.pi, len(noise)))**2
    add(np.convolve(noise, np.ones(30)/30, "same")*env*.4, L0[7] - .2)
    add(tone(880, .25, 12)*.3 + tone(1320, .25, 14)*.2, L0[8])
    return out
def build_audio(wav):
    import wave
    sf = OUT_DIR + "/_sfx.wav"; s = synth(); s = np.clip(s, -1, 1)
    with wave.open(sf, "wb") as w_: w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((s*32767).astype(np.int16).tobytes())
    fc = ("[0:a]aresample=48000,apad=whole_dur=%.2f[v];[1:a]volume=0.55[s];[v][s]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.89[a]" % TOTAL)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", VOIX, "-i", sf, "-filter_complex", fc, "-map", "[a]", "-ac", "2", "-ar", "48000", wav], check=True); os.remove(sf)
OUT_DIR = os.path.join(ROOT, "output", "salaire_mbappe")
def main():
    out = os.path.join(ROOT, "output", "salaire_mbappe"); os.makedirs(out, exist_ok=True); v, a = out + "/_v.mp4", out + "/_a.wav"; build_audio(a)
    cut("bdo/mbappe", 820); cut("real/ronaldo", 860)
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", v], stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for b in pool.imap(frame, range(int(TOTAL*FPS)), chunksize=8): pr.stdin.write(b)
    pr.stdin.close(); pr.wait(); o = out + "/salaire_mbappe.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", o], check=True); os.remove(v); os.remove(a); print(o, round(TOTAL, 2))
def stills():
    ts = [0.05] + [L0[i] + .9 for i in range(len(L0))] + [TOTAL - .3]; sh = Image.new("RGB", (216*len(ts), 384))
    for j, t in enumerate(ts): sh.paste(Image.frombytes("RGB", (W, H), frame(int(t*FPS))).resize((216, 384)), (j*216, 0))
    p = os.path.join(os.environ.get("STILLS_DIR", HERE), "salaire_planche.jpg"); sh.save(p, quality=88); print(p)
if __name__ == "__main__": stills() if "--stills" in sys.argv else main()
