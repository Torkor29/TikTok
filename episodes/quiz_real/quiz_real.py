"""QUIZ REAL MADRID « Si t'as pas 5/5 t'es pas un vrai fan » (~35 s). Format court validé (leçons skill viral §10) :
hook visage + défi d'identité à l'image 0, 5 QCM avec chrono 3-2-1 calé sur la musique, score à l'écran, papier stylé + typo d'édit.
Voix : voix/voix.mp3 (blancs coupés) découpée par question, un silence de chrono (6 temps) est inséré après chaque question.
  python3 episodes/quiz_real/quiz_real.py [--stills]"""
import sys, os, math, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "episodes", "bdo_kane"))
_argv = sys.argv; sys.argv = [sys.argv[0], "--noop"]
import kane as KN                                                # typo d'édit (Anton/Bebas), bandes papier, cadre déchiré, étalonnage
sys.argv = _argv
B, E = KN.B, KN.E
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
W, H, FPS, BEAT = KN.W, KN.H, KN.FPS, KN.BEAT
GOLD = (255, 205, 80); PURPLE = (60, 40, 120); WHITE = (255, 255, 255); GREEN = (40, 170, 80)
OUT = os.path.join(ROOT, "output", "quiz_real")
PH = os.path.join(ROOT, "assets", "photos", "real")
VO = os.path.join(HERE, "voix", "voix.mp3")
# segments de voix (s, dans voix.mp3) : hook, Q1..Q5, outro
SEG = [(0, 3.0), (3.0, 6.04), (6.04, 9.2), (9.2, 12.26), (12.26, 15.94), (15.94, 18.66), (18.66, 21.01)]
GAP = 6*BEAT                                                     # chrono 3-2-1 = 6 temps de musique
Q = [("COMBIEN DE LIGUES DES CHAMPIONS LE REAL A GAGNÉ ?", ["13", "14", "15", "16"], 2, "15"),
     ("QUI EST LE MEILLEUR BUTEUR DE L'HISTOIRE DU CLUB ?", ["RAÚL", "BENZEMA", "DI STÉFANO", "CRISTIANO RONALDO"], 3, "ronaldo"),
     ("DE QUEL CLUB ARRIVE ZIDANE EN 2001 ?", ["BORDEAUX", "JUVENTUS", "MARSEILLE", "MILAN"], 1, "zidane"),
     ("CONTRE QUI LE REAL GAGNE LA DECIMA EN 2014 ?", ["ATLÉTICO", "LIVERPOOL", "JUVENTUS", "DORTMUND"], 0, "decima"),
     ("COMMENT S'APPELLE LE STADE DU REAL ?", ["MESTALLA", "METROPOLITANO", "SANTIAGO-BERNABÉU", "CAMP NOU"], 2, "stade")]
# timeline vidéo
TL = []; t = 0.0
TL.append(("hook", t, t + SEG[0][1] - SEG[0][0])); t = TL[-1][2]
for k in range(5):
    d = SEG[k + 1][1] - SEG[k + 1][0]; TL.append(("q", t, t + d + GAP, k, t + d)); t += d + GAP
TL.append(("end", t, t + SEG[6][1] - SEG[6][0] + 1.2)); TOTAL = TL[-1][2]
_cut = {}
def CUT(n, h):
    k = (n, h)
    if k not in _cut:
        p = os.path.join(PH, n + ".png"); _cut[k] = B.paper_player(p, (0, 0) + Image.open(p).size, h, real=True)
    return _cut[k]
_sb = {}
def sunburst(L, x, y, r, t, col=GOLD, n=18):
    """Médaillon « éclat » en papier (étoile à rayons, 2 tons, ombre) qui tourne lentement derrière le joueur — remplace l'aura."""
    k = (r, col, n)
    if k not in _sb:
        im = Image.new("RGBA", (2*r + 80, 2*r + 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = r + 40
        pts = [(c + (r if j % 2 == 0 else r*.78)*math.cos(math.pi*j/n), c + (r if j % 2 == 0 else r*.78)*math.sin(math.pi*j/n)) for j in range(2*n)]
        sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).polygon([(px + 14, py + 18) for px, py in pts], fill=120); im.putalpha(sh.filter(ImageFilter.GaussianBlur(10)))
        d = ImageDraw.Draw(im); d.polygon(pts, fill=col)
        for j in range(n): a0, a1 = math.pi*2*j/n, math.pi*(2*j + 1)/n; d.polygon([(c, c), (c + r*math.cos(a0), c + r*math.sin(a0)), (c + r*.78*math.cos(a1), c + r*.78*math.sin(a1))], fill=tuple(int(v*.85) for v in col))
        d.ellipse([c - r*.55, c - r*.55, c + r*.55, c + r*.55], fill=(250, 246, 236)); d.ellipse([c - r*.5, c - r*.5, c + r*.5, c + r*.5], outline=col, width=8)
        im.info["anchor"] = (c, c); _sb[k] = im
    B.put(L, _sb[k], x, y, 1, t*12)
def rim(sp, col=GOLD, wd=10):
    """Liseré lumineux net autour du joueur (rim light)."""
    k = ("rim", id(sp), col)
    if k not in _sb:
        a = sp.getchannel("A").point(lambda v: 255 if v > 90 else 0); g = Image.new("RGBA", sp.size, col + (0,)); g.putalpha(a.filter(ImageFilter.MaxFilter(2*wd + 1)).filter(ImageFilter.GaussianBlur(3)))
        g.info["anchor"] = sp.info["anchor"]; _sb[k] = g
    return _sb[k]
def hero(L, n, h, x, y, t, s=1.0, burst=True):
    sp = CUT(n, h)
    if burst: sunburst(L, x, y - h*.62, int(h*.42), t)
    B.put(L, rim(sp), x, y, s, 0); B.put(L, sp, x, y, s, 0)
def bg(L, t, pulse):
    B.dark_bg(L, t, PURPLE, "rq"); B.rays(L, (W//2, 900), t, .7, 18, 1900, (50, 40, 90), .1, .3)
    B.glow_spot(L, W//2, 950, 640, tuple(int(c*(.45 + .25*pulse)) for c in GOLD)); B.particles(L, W//2, 1950, W, 1800, t, GOLD, 18, 2)
def wrap(txt, n=20):
    words, lines, cur = txt.replace(" ?", "\u00a0?").split(" "), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n and cur: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return lines + [cur]
def score_at(t):
    return sum(1 for e in TL if e[0] == "q" and t >= e[2] - .05)
def frame(fr, t):
    pulse = KN.on_beat(t); L = Image.new("RGBA", (W, H), (0, 0, 0, 255)); bg(L, t, pulse)
    e = [x for x in TL if x[1] <= t][-1]; kind = e[0]; u = t - e[1]
    if kind == "hook":                                           # IMAGE 0 : visage + défi d'identité
        hero(L, "vinicius", 1900, W//2, 2400, t, 1 + .015*pulse)
        B.put(L, B.logo("real", 200), 900, 560, 1, 8)
        KN.put_strip(L, "T'ES UN VRAI FAN", 110, W//2, 320, -3, 1 + .02*pulse)
        KN.put_strip(L, "DU REAL ?", 170, W//2, 500, 2, 1 + .03*pulse, bg=GOLD)
        KN.put_strip(L, "SI T'AS PAS 5/5…", 100, W//2, 1640, -2, 1 + .03*pulse, bg=(220, 30, 40), fg=WHITE)
    elif kind == "q":
        k, tq = e[3], e[4]; qtxt, ans, good, illu = Q[k]
        reveal = t >= e[2] - .05 - 0 and False
        rv = t >= e[2] - 1.0*BEAT                                # révélation sur le dernier temps du chrono
        KN.put_strip(L, f"QUESTION {k + 1}/5", 70, 260, 230, -4, KN.slam(u), bg=GOLD)
        if k == 0: KN.put_strip(L, "VRAI FAN DU REAL ?", 50, 760, 160, 3, 1, tape=False)
        for j, line in enumerate(wrap(qtxt)):
            KN.etext(L, line, 96, W//2, 420 + j*110, s=B.M.spring(u - .05*j, .3, 16))
        y0 = 420 + len(wrap(qtxt))*110 + 110
        for j, a in enumerate(ans):
            ok = j == good; x = W//2; y = y0 + j*215
            s = B.M.spring(u - .25 - .07*j, .3, 16)
            if rv and not ok: s *= max(0, 1 - (t - (e[2] - BEAT))/.15)
            if rv and ok: y = y + (y0 - y)*B.M.ease_out(min(1, (t - (e[2] - BEAT))/.2))   # la bonne réponse remonte en 1re position
            bgc = GREEN if (rv and ok) else ((235, 230, 220) if not rv else (120, 115, 110))
            fgc = WHITE if (rv and ok) else (18, 16, 20)
            KN.put_strip(L, f"{'ABCD'[j]}   {a}", 100, x, y, (-1.5, 1.2, -1, 1.5)[j], s*(1 + .08*KN.slam(t - (e[2] - BEAT)) - .08 if (rv and ok) else s), bg=bgc, fg=fgc)
        if t >= tq and not rv:                                   # chrono 3-2-1 (un chiffre tous les 2 temps)
            n = 3 - int((t - tq)/(2*BEAT)); n = max(1, n); uu = ((t - tq) % (2*BEAT))
            KN.etext(L, str(n), 260, 900, 250, GOLD, s=KN.slam(uu, .15))
            frac = 1 - (t - tq)/(GAP - BEAT); ImageDraw.Draw(L).rectangle([90, 1840, 90 + int(900*max(0, frac)), 1860], fill=GOLD)
        if rv:                                                   # illustration de la réponse
            v = B.M.spring(t - (e[2] - BEAT), .35, 14)
            if illu in ("ronaldo", "zidane"):
                hero(L, illu, 950, W//2, 2010, t, v)
            elif illu == "15": sunburst(L, W//2, 1450, 330, t); KN.etext(L, "15", 320, W//2, 1450, (30, 24, 40), s=v)
            KN.etext(L, "+1", 120, 170, 1760, GREEN, s=v)
        KN.etext(L, f"SCORE {score_at(t)}/5", 70, 940, 1740, GOLD, font="BebasNeue-Regular.ttf")
    else:
        hero(L, "vinicius", 1700, W//2, 2300, t)
        KN.put_strip(L, "TON SCORE ?", 150, W//2, 300, -3, KN.slam(u), bg=GOLD)
        KN.put_strip(L, "DIS-LE EN COMMENTAIRE", 80, W//2, 470, 2, KN.slam(u - .4) if u > .4 else 0, bg=(220, 30, 40), fg=WHITE)
        KN.etext(L, "5/5 ?", 90, 900, 1740, GOLD, font="BebasNeue-Regular.ttf")
    L.alpha_composite(KN.torn_frame())
    return L.convert("RGB")

def build_audio(wav):
    """Voix découpée + silences de chrono, musique phonk (dès le drop) sous la voix, tics de chrono et ding de bonne réponse."""
    S = OUT + "/_a"; os.makedirs(S, exist_ok=True); parts = []
    for k, (a, b) in enumerate(SEG):
        p = f"{S}/s{k}.wav"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(a), "-t", str(b - a), "-i", VO, "-ar", "44100", "-ac", "2", p], check=True); parts.append(p)
        if 1 <= k <= 5:
            g = f"{S}/g{k}.wav"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{GAP:.4f}", g], check=True); parts.append(g)
    with open(f"{S}/l.txt", "w") as f: f.write("".join(f"file '{p}'\n" for p in parts))
    vo = f"{S}/vo.wav"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{S}/l.txt", vo], check=True)
    tick = os.path.join(ROOT, "episodes", "lille_v5", "sfx", "tick.mp3"); ding = os.path.join(ROOT, "assets", "sfx", "correct.mp3")
    ev = []
    for e in TL:
        if e[0] == "q":
            for j in range(5): ev.append((tick, e[4] + j*BEAT, .6))
            ev.append((ding, e[2] - BEAT, .8))
    ins = ["-i", vo, "-i", E.MUSIC] + sum([["-i", p] for p, _, _ in ev], [])
    fc = f"[1:a]atrim={8*BEAT:.4f}:{8*BEAT + TOTAL:.2f},asetpts=PTS-STARTPTS,volume=0.35[m];[0:a]asplit[v][sc];[m][sc]sidechaincompress=threshold=0.04:ratio=5:attack=15:release=250[md];"
    for i, (_, ts, g) in enumerate(ev): fc += f"[{i + 2}:a]adelay={int(ts*1000)}|{int(ts*1000)},volume={g}[e{i}];"
    fc += "[v][md]" + "".join(f"[e{i}]" for i in range(len(ev))) + f"amix=inputs={2 + len(ev)}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},loudnorm=I=-14:TP=-1[a]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-filter_complex", fc, "-map", "[a]", wav], check=True)
def main():
    os.makedirs(OUT, exist_ok=True); v = OUT + "/_v.mp4"; a = OUT + "/_a.wav"; build_audio(a)
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-preset", "medium", "-maxrate", "6M", "-bufsize", "12M", v], stdin=subprocess.PIPE)
    for fr in range(int(TOTAL*FPS)): pr.stdin.write(frame(fr, fr/FPS).tobytes())
    pr.stdin.close(); pr.wait(); out = OUT + "/quiz_real.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    os.remove(v); os.remove(a); print(out, TOTAL)
def stills():
    ts = [0, 1.5, 2.6] + sum([[e[1] + .8, e[4] + .5, e[2] - .3] for e in TL if e[0] == "q"], []) + [TL[-1][1] + 1]
    sh = Image.new("RGB", (216*10, 384*2))
    for k, t in enumerate(ts[:20]): sh.paste(frame(int(t*FPS), t).resize((216, 384)), ((k % 10)*216, (k//10)*384))
    p = "/tmp/claude-0/quiz_real_sheet.jpg"; sh.save(p, quality=85); print(p, TOTAL)
if __name__ == "__main__": stills() if "--stills" in sys.argv else main()
