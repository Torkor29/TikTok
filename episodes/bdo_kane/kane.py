"""HARRY KANE, BALLON D'OR 2026 : édit motion design calé sur la musique signature (phonk 129 BPM).
Hook (image 0) : Kane ému en gros plan (cérémonie) + « 1er ANGLAIS DEPUIS 2001 ». Puis intro façon Smash « HERE COMES THE CHAMPION! »,
stats de la saison en motion design, buts ENTIERS en cartes papier, remise du trophée, fin + CTA.
  python3 episodes/bdo_kane/kane.py
Faits (sources : worldsoccertalk, gulfnews, radiox ; vainqueur annoncé le 26/10/2026) : 61 buts en 51 matchs (Bayern, toutes compét.),
36 buts en Bundesliga = Soulier d'or européen, triplé Bundesliga + Coupe d'Allemagne + Supercoupe ; dernier Anglais : Michael Owen (2001)."""
import sys, os, math, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "episodes", "bdo_edit"))
_argv = sys.argv; sys.argv = [sys.argv[0], "--noop"]
import edit as E                                                 # cartes papier, lecture d'extraits, zoom, BEAT…
B = E.B
sys.argv = _argv
from PIL import Image, ImageDraw
W, H, FPS, BEAT = E.W, E.H, E.FPS, E.BEAT
UP = "/root/.claude/uploads/0adb781c-170c-5099-95c1-9e411610d456/"
GOALS = UP + "3de3976a-v14044g50000db9vup7og65t3hmhj6d0.mp4"
CEREMONY = UP + "d5e2c412-v26044gc0000dbfu7onog65gs2d7rsj0.mp4"
RED = (255, 60, 60); NAME = "HARRY KANE"
OUT = os.path.join(ROOT, "output", "bdo_kane")

# ------------------------------------------------------------------ timeline (en temps de musique)
SEQ = []                                                         # (kind, nb_temps, params)
def add(kind, nb, **p): SEQ.append((kind, nb, p))
add("hook", 6, src=(CEREMONY, 4.7))                              # Kane ému, mains sur le visage
add("champion", 4)                                               # intro Smash
add("stat", 4, big="61", small="BUTS", sub="EN 51 MATCHS", count=61)
add("stat", 4, big="36", small="BUTS EN BUNDESLIGA", sub="SOULIER D'OR EUROPÉEN", count=36, boot=True)
add("treble", 4)
add("clip", 8, src=(GOALS, 5.9))
add("clip", 10, src=(GOALS, 27.0))
add("clip", 10, src=(GOALS, 31.75))
add("clip", 12, src=(GOALS, 36.6), tag="BUT N°61 ?" and "")
add("clip", 12, src=(CEREMONY, 48.0), tag="LONDRES · 26 OCTOBRE")
add("clip", 8, src=(CEREMONY, 69.6))
add("end", 10)
t = 0.0; TL = []
for kind, nb, p in SEQ: TL.append((t, t + nb*BEAT, kind, p)); t += nb*BEAT
TOTAL = t + 1.0
import numpy as np
def read_full(path, t0, dur):
    """Extrait en VRAI PLEIN ÉCRAN 1080x1920 (compile : bandes noires et filigrane retirés en gardant la bande utile 576x556)."""
    pre = "crop=576:556:0:236," if path == GOALS else ""
    vf = f"fps={FPS},{pre}scale=1080*1.04:1920*1.04:force_original_aspect_ratio=increase,crop=1080:1920"
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", path, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    n = len(raw)//(W*H*3); fr = [np.frombuffer(raw[i*W*H*3:(i + 1)*W*H*3], np.uint8).reshape(H, W, 3) for i in range(n)]
    need = int(round(dur*FPS))
    while fr and len(fr) < need: fr.append(fr[-1])
    return fr[:need]
CLIPS = {i: read_full(p["src"][0], p["src"][1], (b - a)) for i, (a, b, k, p) in enumerate(TL) if "src" in p}
_rng = np.random.default_rng(3)
GRAIN = [(_rng.standard_normal((H//2, W//2))*7).astype(np.float32) for _ in range(6)]
_vy, _vx = np.mgrid[0:H, 0:W].astype(np.float32); VIG = 1 - .55*(((_vx - W/2)/(W/2))**2*.6 + ((_vy - H/2)/(H/2))**2*.4).clip(0, 1)
def grade(a, t, pulse, local):
    """Étalonnage « édit » : contraste en S, ombres froides / hautes lumières chaudes, bloom, vignette, grain, flash et RGB-split sur le temps."""
    f = a.astype(np.float32)/255
    f = f*f*(3 - 2*f)                                            # courbe en S
    lum = f.mean(2, keepdims=True)
    f = f + (1 - lum)*np.array([-.03, 0, .05]) + lum*np.array([.06, .01, -.04])   # teal / orange
    from PIL import ImageFilter as _F
    hi = np.clip((f - .7)*3, 0, 1); bl = np.asarray(Image.fromarray((hi*255).astype(np.uint8)).resize((W//4, H//4)).filter(_F.GaussianBlur(10)).resize((W, H)), np.float32)/255
    f = f + bl*(.45 + .35*pulse)                                 # bloom qui pulse
    f = f*VIG[..., None]
    g = GRAIN[int(t*24) % 6]; f = f + np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]/255
    f = f + .5*math.exp(-local*14)                               # flash à la coupe
    out = np.clip(f*255, 0, 255).astype(np.uint8)
    sh = int(16*pulse + 22*math.exp(-local*12))
    if sh > 1: out = np.stack([np.roll(out[..., 0], sh, 1), out[..., 1], np.roll(out[..., 2], -sh, 1)], 2)
    return out
def punch(im, t, pulse, local, side):
    """Zoom-punch sur chaque temps + entrée en zoom rapide à la coupe + micro-secousse."""
    z = 1 + .06*pulse + .18*math.exp(-local*7)
    dx = 14*math.sin(t*53)*pulse + side*120*math.exp(-local*10); dy = 10*math.cos(t*47)*pulse
    w, h = W/z, H/z; x0, y0 = (W - w)/2 + dx, (H - h)/2 + dy
    x0 = min(max(x0, 0), W - w); y0 = min(max(y0, 0), H - h)
    return im.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.BILINEAR)

from PIL import ImageFont, ImageFilter
FONTS = os.path.join(ROOT, "assets", "fonts")
_ft = {}; _tx = {}
def _font(name, size):
    k = (name, size)
    if k not in _ft: _ft[k] = ImageFont.truetype(os.path.join(FONTS, name), size)
    return _ft[k]
def etext_img(txt, size, col=(255, 255, 255), font="Anton-Regular.ttf", glow=None, track=4):
    """Texte d'édit propre : typo condensée grasse, ombre portée nette + lueur colorée douce (cache)."""
    k = (txt, size, col, font, glow, track)
    if k not in _tx:
        pad = int(60 + size*.7)                                   # marge large : la lueur ne doit jamais être coupée en carré
        f = _font(font, size); widths = [f.getlength(c) for c in txt]; w_ = int(sum(widths) + track*(len(txt) - 1)) + 2*pad
        asc, desc = f.getmetrics(); h_ = asc + desc + 2*pad
        m = Image.new("L", (w_, h_), 0); d = ImageDraw.Draw(m); x = pad
        for c, cw in zip(txt, widths): d.text((x, pad), c, font=f, fill=255); x += cw + track
        out = Image.new("RGBA", (w_, h_), (0, 0, 0, 0))
        if glow: g = Image.new("RGBA", (w_, h_), glow + (0,)); g.putalpha(m.filter(ImageFilter.GaussianBlur(size*.18)).point(lambda v: min(255, v*2))); out.alpha_composite(g)
        sh = Image.new("RGBA", (w_, h_), (0, 0, 0, 0)); sh.putalpha(m.point(lambda v: v*200//255)); out.alpha_composite(sh, (0, int(size*.05)))
        fg = Image.new("RGBA", (w_, h_), col + (255,)); fg.putalpha(m); out.alpha_composite(fg)
        out = out.crop(out.getchannel("A").getbbox()); out.info["anchor"] = (out.width/2, out.height/2); _tx[k] = out
    return _tx[k]
def etext(L, txt, size, x, y, col=(255, 255, 255), s=1.0, rot=0, glow=None, font="Anton-Regular.ttf", a=1.0):
    if s > .02 and a > .02: B.put(L, etext_img(txt, size, col, font, glow), x, y, s, rot, a) if a >= .99 else B.blit_sxy(L, etext_img(txt, size, col, font, glow), x, y, s, s, rot, a)
# ------------------------------------------------------------------ PAPIER STYLÉ (plein écran) : bords déchirés, bandes-titres, déchirure
_pp = {}
def torn_poly(w_, h_, jit, step, seed):
    rng = np.random.default_rng(seed); pts = []
    for x in range(0, w_ + 1, step): pts.append((x, rng.uniform(0, jit)))
    for x in range(w_, -1, -step): pts.append((x, h_ - rng.uniform(0, jit)))
    return pts
def paper_tex(w_, h_, col, seed):
    rng = np.random.default_rng(seed); a = np.zeros((h_, w_, 3), np.float32); a[:] = col
    g = np.asarray(Image.fromarray((rng.random((h_//6 + 2, w_//6 + 2))*255).astype(np.uint8)).resize((w_, h_), Image.BICUBIC), np.float32)/255
    a *= (.92 + .1*g)[..., None]; sp = rng.random((h_, w_)); a += ((sp > .985)*-25)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
def strip(txt, size, bg=(246, 240, 226), fg=(18, 16, 20), rot=0, tape=True, font="Anton-Regular.ttf"):
    """Mot découpé sur une bande de papier déchirée (+ scotch), typo d'édit. Cache."""
    k = (txt, size, bg, fg, tape, font)
    if k not in _pp:
        f = _font(font, size); tw = int(f.getlength(txt)); asc, desc = f.getmetrics()
        w_, h_ = tw + int(size*.7), int(asc*1.18) + 24
        m = Image.new("L", (w_, h_), 0); ImageDraw.Draw(m).polygon(torn_poly(w_, h_, 12, 18, len(txt) + size), fill=255)
        out = Image.new("RGBA", (w_ + 60, h_ + 60), (0, 0, 0, 0))
        sh = Image.new("RGBA", (w_, h_), (0, 0, 0, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(6)).point(lambda v: v*150//255)); out.alpha_composite(sh, (38, 42))
        pap = paper_tex(w_, h_, bg, size).convert("RGBA"); pap.putalpha(m); out.alpha_composite(pap, (30, 30))
        ImageDraw.Draw(out).text((30 + int(size*.35), 30 + 10), txt, font=f, fill=fg)
        if tape:
            tp = Image.new("RGBA", (int(size*.9), int(size*.3)), (240, 232, 205, 170)); tp = tp.rotate(-30, expand=True)
            out.alpha_composite(tp, (0, 0))
        out.info["anchor"] = (out.width/2, out.height/2); _pp[k] = out
    return _pp[k]
def put_strip(L, txt, size, x, y, rot=0, s=1.0, **kw):
    if s > .02: B.put(L, strip(txt, size, **kw), x, y, s, rot)
def torn_frame():
    """Cadre plein écran : bords haut/bas en papier déchiré (crème, ombre) — l'image reste plein écran."""
    if "frame" not in _pp:
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rng = np.random.default_rng(11)
        for top in (True, False):
            hh = 70; pts = [(x, hh + rng.uniform(-14, 14)) for x in range(0, W + 1, 22)]
            poly = [(0, 0), (W, 0)] + pts[::-1] if top else [(0, H), (W, H)] + [(x, H - y) for x, y in pts[::-1]]
            m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon(poly, fill=255)
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(10)).point(lambda v: v*170//255))
            out.alpha_composite(sh, (0, 10 if top else -10))
            pap = paper_tex(W, H, (240, 234, 220), 3 if top else 4).convert("RGBA"); pap.putalpha(m); out.alpha_composite(pap)
        _pp["frame"] = out
    return _pp["frame"]
def rip(prev, cur, u, seed):
    """Transition DÉCHIRURE : la nouvelle image apparaît par une déchirure diagonale qui traverse l'écran, bord blanc fibreux + ombre."""
    rng = np.random.default_rng(seed); y0 = H*(1.15 - 1.3*B.M.ease_io(u)); pts = []
    for x in range(0, W + 1, 26): pts.append((x, y0 - .35*(x - W/2) + rng.uniform(-22, 22)))
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon([(0, H), (W, H)] + pts[::-1], fill=255)   # zone sous la déchirure = nouvelle image
    edge = Image.new("L", (W, H), 0); ImageDraw.Draw(edge).line(pts, fill=255, width=26); edge = edge.filter(ImageFilter.GaussianBlur(2))
    out = prev.copy(); sh = Image.new("RGB", (W, H), (0, 0, 0)); out.paste(sh, (0, 0), m.filter(ImageFilter.GaussianBlur(14)).point(lambda v: v*120//255))
    out.paste(cur, (0, 0), m); out.paste((246, 242, 232), (0, 0), edge)
    return out
def slam(u, d=.18): return 1 + .35*(1 - B.M.ease_out(min(1, u/d))) if u < d else 1.0
def on_beat(t, w=.12):
    k = round(t/BEAT); return max(0.0, 1 - abs(t - k*BEAT)/w) if k >= 1 else 0.0
def bg(L, t, pulse, k=1.0):
    B.dark_bg(L, t, RED, "k"); B.rays(L, (W//2, 1000), t, .8, 18, 1900, (70, 14, 14), .1, .3)
    B.glow_spot(L, W//2, 1050, 620, tuple(int(c*(.45 + .25*pulse)*k) for c in RED))
    B.particles(L, W//2, 1950, W, 1800, t, (255, 120, 90), 22, 3)
def counter_txt(n, size): return B.metal_text(str(n), size, (255, 255, 255), (230, 230, 235), (255, 90, 70))
CUP = None
def frame(fr, t):
    global CUP
    pulse = on_beat(t); i = max(j for j, s in enumerate(TL) if s[0] <= t); a, b, kind, p = TL[i]; u = t - a
    L = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    if kind == "hook":                                           # IMAGE 0 : visage ému de Kane PLEIN ÉCRAN + promesse
        arr = CLIPS[i][min(len(CLIPS[i]) - 1, int(u*FPS))]
        im = punch(Image.fromarray(grade(arr, t, pulse, 9)), t, pulse, 9, 0)
        L = im.convert("RGBA"); L.alpha_composite(torn_frame())
        put_strip(L, "BALLON D'OR 2026", 96, W//2, 260, -3, 1 + .03*pulse)
        put_strip(L, "LE 1er ANGLAIS", 120, W//2 - 40, 1450, 3, 1 + .02*pulse)
        put_strip(L, "DEPUIS 2001", 140, W//2 + 60, 1630, -2, 1 + .02*pulse, bg=(220, 30, 40), fg=(255, 255, 255))
        B.bolt(L, 150, 900, t, RED, 1, 520)
    elif kind == "champion":                                     # intro Smash : flash, explosion, silhouette, texte chromé, puis révélation
        if u < 2*BEAT:
            B.challenger(L, fr, t, a, "kane", RED)
            L2 = L                                               # texte remplacé : « HERE COMES THE CHAMPION! »
        else:
            bg(L, t, pulse, 1.3); sp = B.CUT("kane", 2000); v = u - 2*BEAT
            B.aura(L, sp, W//2, 2350, t, RED, 1.2, 1); B.put(L, sp, W//2, 2350, 1.0 + .02*pulse, 0)   # GROS PLAN : buste coupé en bas
            B.bolt(L, 160, 700, t, RED, 1, 520); B.bolt(L, 920, 820, t + .3, RED, 2, 480)
            etext(L, "HARRY KANE", 170, W//2, 300, s=slam(v), glow=(255, 60, 60))
            if v < .1: L.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255*(1 - v/.1)))))
    elif kind == "stat":                                         # motion design de stat : compteur chromé + Kane en buste à droite
        bg(L, t, pulse)
        sp = B.CUT("kane", 1500); B.aura(L, sp, 760, 2150, t, RED, .9, 2); B.put(L, sp, 760, 2150, 1, 0)
        n = min(p["count"], int(p["count"]*B.M.ease_out(min(1, u/(2*BEAT)))))
        etext(L, str(n), 420, 300, 760, s=1 + .05*pulse*(n == p["count"]), glow=(255, 50, 50))
        etext(L, p["small"], 90 if len(p["small"]) < 8 else 60, 300, 1030, s=B.M.spring(u - .2, .3, 16), font="BebasNeue-Regular.ttf")
        put_strip(L, p["sub"], 84, W//2, 1640, -2, slam(u - 2*BEAT) if u > 2*BEAT else 0, bg=(220, 30, 40), fg=(255, 255, 255))
        if p.get("boot"): B.put(L, B.gold_ball(70), 160, 1250, 0, 0) if False else None
        B.shock(L, t, a + 2*BEAT, 330, 760, RED, 700)
        if u < .06: L.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(160*(1 - u/.06)))))
    elif kind == "treble":                                       # 3 trophées qui tombent sur les temps
        bg(L, t, pulse)
        etext(L, "TRIPLÉ", 260, W//2, 420, s=1 + .04*pulse, glow=(255, 60, 60))
        for k, (lab, x) in enumerate((("BUNDESLIGA", 200), ("COUPE", W//2), ("SUPERCOUPE", 880))):
            tk = a + k*BEAT + .05
            if t >= tk:
                v = B.M.spring(t - tk, .35, 14); B.put(L, B.cup_gold(360), x, 1200, v, (-8, 0, 8)[k])
                etext(L, lab, 64, x, 1380, s=v, font="BebasNeue-Regular.ttf"); B.shock(L, t, tk, x, 1200, (255, 200, 80), 380)
        pass
    elif kind == "clip":                                         # BUT EN ENTIER, PLEIN ÉCRAN, effets d'édit sur chaque temps
        arr = CLIPS[i][min(len(CLIPS[i]) - 1, int(u*FPS))]
        im = punch(Image.fromarray(grade(arr, t, pulse, u)), t, pulse, u, 1 if i % 2 else -1)
        if u < .28 and i > 0 and (i - 1) in CLIPS:               # transition DÉCHIRURE PAPIER depuis l'extrait précédent
            prev = Image.fromarray(CLIPS[i - 1][-1]); im = rip(prev, im, u/.28, i)
        L = im.convert("RGBA"); L.alpha_composite(torn_frame())
        k = max(0, 1 - u/(3*BEAT))                               # nom géant qui claque puis s'efface
        if k > 0: put_strip(L, "HARRY", 120, W//2 - 170, 230, -4, slam(u)); put_strip(L, "KANE", 150, W//2 + 130, 420, 3, slam(u - .1), bg=(220, 30, 40), fg=(255, 255, 255))
        else: put_strip(L, "KANE", 70, 160, 170, -5, tape=False)
        if p.get("tag"): put_strip(L, p["tag"], 70, W//2, 1700, 2, B.M.spring(u - BEAT, .3, 16))
    else:                                                        # FIN : Kane + trophée papier + CTA
        bg(L, t, pulse, 1.2); sp = B.CUT("kane", 1500)
        B.put(L, B.gold_ball(110), W//2, 590 + 8*math.sin(t*3), B.M.spring(u, .45, 12), 0)
        B.aura(L, sp, W//2, 2150, t, RED, 1.2, 4); B.put(L, sp, W//2, 2150, 1, 0)
        B.bolt(L, 200, 900, t, RED, 5, 450); B.bolt(L, 880, 1000, t + .4, RED, 6, 450)
        etext(L, "HARRY KANE", 160, W//2, 200, glow=(255, 60, 60)); etext(L, "BALLON D'OR 2026", 90, W//2, 340, (255, 210, 90), glow=(255, 150, 40))
        if u > 3*BEAT: put_strip(L, "MÉRITÉ ?", 130, W//2, 1620, -3, slam(u - 3*BEAT), bg=(220, 30, 40), fg=(255, 255, 255)); etext(L, "OUI OU NON EN COMMENTAIRE", 64, W//2, 1780, s=B.M.spring(u - 4*BEAT, .3, 16), font="BebasNeue-Regular.ttf")
        if u < .1: L.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255*(1 - u/.1)))))
    if kind != "champion": L.alpha_composite(torn_frame())
    return L.convert("RGB")

# « HERE COMES THE CHAMPION! » : on adapte le texte de l'intro Smash
def _metal(txt, size, *a, **k):
    if txt == "HERE COMES A": return etext_img("HERE COMES THE", 80, font="BebasNeue-Regular.ttf")
    if txt == "NEW CHALLENGER!": return etext_img("CHAMPION", 200, (255, 214, 70))
    return etext_img(txt, size)
B.metal_text = _metal

def main():
    os.makedirs(OUT, exist_ok=True); v = os.path.join(OUT, "_v.mp4")
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-preset", "medium", "-maxrate", "6M", "-bufsize", "12M", v], stdin=subprocess.PIPE)
    for fr in range(int(TOTAL*FPS)): pr.stdin.write(frame(fr, fr/FPS).tobytes())
    pr.stdin.close(); pr.wait(); out = os.path.join(OUT, "bdo_kane.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", E.MUSIC, "-filter_complex",
                    f"[1:a]atrim={8*BEAT:.4f}:{8*BEAT + TOTAL:.2f},asetpts=PTS-STARTPTS,afade=t=out:st={TOTAL - 1.5:.2f}:d=1.5,loudnorm=I=-14:TP=-1[m]", "-map", "0:v", "-map", "[m]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-c", "copy", os.path.join(OUT, "bdo_kane_sans_musique.mp4")], check=True)
    os.remove(v); print(out)
def stills():
    ts = [0, .5, 1.5, 3.0, 3.5, 4.2, 5.0, 6.0, 7.0, 8.0, 10, 14, 18, 22, 26, 30, 33, 36, 39, 41]
    sh = Image.new("RGB", (216*10, 384*2))
    for k, t in enumerate(ts): sh.paste(frame(int(t*FPS), t).resize((216, 384)), ((k % 10)*216, (k//10)*384))
    p = "/tmp/claude-0/kane_sheet.jpg"; sh.save(p, quality=85); print(p, TOTAL)
if __name__ == "__main__": stills() if "--stills" in sys.argv else main()
