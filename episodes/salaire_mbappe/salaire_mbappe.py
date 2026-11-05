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
def frame(fr):
    t = fr/FPS; cv = bg().copy(); g = game(t); money = g*PER_S
    speed = 1 if t < MARK[1][0] + .5 else min(1, math.log10(max(10, (game(t + .1) - game(t))/.1))/4)
    rays(cv, t, .35 + .4*speed)
    end = t >= L0[7] - .05
    # pluie de billets (plus dense quand le temps accélère)
    rnd = random.Random(7); n = int(4 + 40*speed) if t > L0[1] else 0
    for k in range(n):
        x = rnd.uniform(0, W); sp = rnd.uniform(500, 900); y = (rnd.uniform(0, H) + t*sp) % (H + 200) - 100
        E.blit(cv, BILL.v[E.boil(fr)], x, y, .7, rnd.uniform(-40, 40) + t*rnd.uniform(-60, 60))
    # pile de billets qui grossit (hauteur ∝ log de la cagnotte)
    hpile = int(min(620, 70*math.log10(1 + money))) if money > 1 else 0
    for side in (-1, 1):
        for j in range(0, hpile, 16): E.blit(cv, BILL.v[(j//16) % 3], W/2 + side*330 + ((j*7) % 13 - 6), 1700 - j, .9, ((j*13) % 9) - 4)
    # joueur
    if not end: sp_ = cut("bdo/mbappe", 820); E.blit(cv, sp_, W/2, 1930, 1.0 + .01*math.sin(t*3))
    else:
        u = min(1, (t - L0[7] + .05)/.3); E.blit(cv, cut("real/ronaldo", 860), W/2, 1930 + 600*(1 - u), 1.0)
        LB("× 3", 220, INK, GOLD).draw(cv, fr, W/2 + 250, 1150, E.ease_out_back(u, 2.2), -6)
    # titre (image 0) puis horloge + cagnotte
    if t < L0[1]:
        LB("LE VRAI SALAIRE DE", 70, CREAM, INK).draw(cv, fr, W/2, 360, 1, -2); LB("MBAPPÉ", 180, INK, GOLD).draw(cv, fr, W/2, 540, 1, 2)
        LB("SECONDE PAR SECONDE", 64, CREAM, RED).draw(cv, fr, W/2, 720, 1, -2)
    if not end:
        d = ImageDraw.Draw(cv); y0 = 820 if t >= L0[1] else 900
        LB(clock(g), 80, CREAM, INK, "mono").draw(cv, fr, W/2, y0 - 170, 1, -2) if t >= L0[1] else None
        txt = eur(money); size = 230 if len(txt) < 9 else (200 if len(txt) < 11 else 170); f = font(size)
        pop = 1 + .06*abs(math.sin(t*math.pi*2)) if speed < .5 else 1.0
        d.text((W/2 + 8, y0 + 14), txt, font=f, fill=(10, 8, 20), anchor="mm"); d.text((W/2, y0), txt, font=f, fill=GOLD, anchor="mm")
        for (tm, lab, bgc, fgc) in MILESTONE:
            if tm - .05 <= t < tm + 1.6: LB(lab, 84, fgc, bgc).draw(cv, fr, W/2, y0 + 190, E.ease_out_back(min(1, (t - tm + .05)/.3), 2.2), -3)
    else:
        if t > L0[8]: LB("ET TOI ?", 120, INK, GOLD).draw(cv, fr, W/2, 560, E.ease_out_back(min(1, (t - L0[8])/.3), 2), -3); LB("DIS-LE EN COMMENTAIRE", 64, CREAM, RED).draw(cv, fr, W/2, 720, min(1, max(0, (t - L0[8] - .6)/.3)), 2)
        else: LB("RONALDO", 150, CREAM, RED).draw(cv, fr, W/2, 560, 1, -2)
    d = ImageDraw.Draw(cv); d.text((W/2, 1600), "ESTIMATION FORBES 2025 · SALAIRE + PRIMES + SPONSORS", font=font(30, "BebasNeue-Regular.ttf"), fill=(200, 204, 220), anchor="mm")
    KA.caption(cv, WD, t, 1500, 78)
    return np.asarray(cv.convert("RGB")).tobytes()
def build_audio(wav):
    A = os.path.join(ROOT, "assets", "sfx"); evs = [(VOIX, 0.0, 1.0)]
    for s in range(1, 4): evs.append((os.path.join(A, "coin.mp3"), MARK[1][0] - 1 + s*.4, .3))      # tic-tic-tic des premières secondes
    for (tm, *_r) in MILESTONE: evs.append((os.path.join(A, "cash.mp3"), tm, .35))
    evs += [(os.path.join(A, "whoosh.mp3"), L0[7] - .05, .3), (os.path.join(A, "notif.mp3"), L0[8], .35)]
    ins = ["-f", "lavfi", "-t", f"{TOTAL:.2f}", "-i", "anullsrc=r=48000:cl=stereo"] + sum([["-i", p] for p, _, _ in evs], []); fc = ""
    for j, (_, ts, gn) in enumerate(evs): fc += f"[{j + 1}:a]aresample=48000,adelay={int(max(0, ts)*1000)}|{int(max(0, ts)*1000)},volume={gn}[e{j}];"
    fc += "[0:a]" + "".join(f"[e{j}]" for j in range(len(evs))) + f"amix=inputs={1 + len(evs)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.89[a]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-filter_complex", fc, "-map", "[a]", "-ar", "48000", wav], check=True)
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
