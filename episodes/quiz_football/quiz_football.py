"""QUIZZ FOOTBALL express « Si t'as pas 5/5 t'es pas un vrai fan de foot » (~36 s). Format court du quiz Real (episodes/quiz_real),
culture foot générale, mot-clé « QUIZZ FOOTBALL » (recherche suggérée par TikTok) dit à 0 s et écrit sur toutes les images.
Voix : voix/voix.mp3 (une seule prise, Léo) ; les 7 segments (hook, Q1..Q5, fin) sont trouvés par silencedetect et gardés dans
voix/segments.json. Sans voix : minutage provisoire (silences de durée estimée), rendu marqué _provisoire.
  python3 episodes/quiz_football/quiz_football.py [--stills]"""
import sys, os, math, subprocess, json, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "episodes", "bdo_kane"))
_argv = sys.argv; sys.argv = [sys.argv[0], "--noop"]
import kane as KN                                                # typo d'édit (Anton/Bebas), bandes papier, cadre déchiré
sys.argv = _argv
B, E = KN.B, KN.E
from PIL import Image, ImageDraw, ImageFilter
W, H, FPS, BEAT = KN.W, KN.H, KN.FPS, KN.BEAT
GOLD = (255, 205, 80); PITCH = (14, 82, 46); WHITE = (255, 255, 255); GREEN = (40, 170, 80); RED = (220, 30, 40)
OUT = os.path.join(ROOT, "output", "quiz_football")
PH = os.path.join(ROOT, "assets", "photos")
VO = os.path.join(HERE, "voix", "voix.mp3"); SEGF = os.path.join(HERE, "voix", "segments.json")
TEXTE = ["Quizz football ! Si t'as pas cinq sur cinq, t'es pas un vrai fan de foot.",
         "Question une. Quel pays a inventé le football moderne ?",
         "Question deux. Où s'est jouée la toute première Coupe du monde ?",
         "Question trois. Qui a marqué le but de la main de Dieu ?",
         "Question quatre. Quel pays a joué toutes les Coupes du monde ?",
         "Dernière question, la plus dure. Quel gardien a marqué plus de cent buts ?",
         "Alors, t'as eu combien ? Dis ton score en commentaire !"]
PROVISOIRE = not os.path.exists(VO)

def segments():
    """(début, fin) de chaque phrase dans voix.mp3 : on coupe au milieu des 6 plus longs silences."""
    if os.path.exists(SEGF): return json.load(open(SEGF))
    r = subprocess.run(["ffmpeg", "-i", VO, "-af", "silencedetect=noise=-35dB:d=0.15", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    dur = float(re.findall(r"Duration: (\d+):(\d+):([\d.]+)", r)[0][2]) + 60*float(re.findall(r"Duration: (\d+):(\d+)", r)[0][1])
    sil = sorted([(e - s, s, e) for s, e in zip(st, en) if s > .3 and e < dur - .1], reverse=True)[:6]
    cuts = sorted((s + e)/2 for _, s, e in sil); bounds = [0.0] + cuts + [dur]
    seg = [(round(bounds[i], 3), round(bounds[i + 1], 3)) for i in range(7)]
    json.dump(seg, open(SEGF, "w")); return seg
if PROVISOIRE:                                                   # ~19 caractères / s pour Léo (blancs coupés, mesuré sur le quiz Real)
    SEG, t = [], 0.0
    for s in TEXTE: d = round(len(s)/19 + .2, 2); SEG.append((t, t + d)); t += d
else: SEG = segments()
GAP = 6*BEAT                                                     # chrono 3-2-1 = 6 temps (129 BPM)
Q = [("QUEL PAYS A INVENTÉ LE FOOTBALL MODERNE ?", ["FRANCE", "ANGLETERRE", "BRÉSIL", "ITALIE"], 1, "angleterre"),
     ("OÙ S'EST JOUÉE LA 1RE COUPE DU MONDE ?", ["BRÉSIL", "ITALIE", "URUGUAY", "FRANCE"], 2, "uruguay"),
     ("QUI A MARQUÉ|LE BUT DE LA|« MAIN DE DIEU » ?", ["MARADONA", "PELÉ", "MESSI", "HENRY"], 0, "maradona"),
     ("QUEL PAYS A JOUÉ|TOUTES LES COUPES|DU MONDE ?", ["ALLEMAGNE", "ARGENTINE", "ITALIE", "BRÉSIL"], 3, "bresil"),
     ("QUEL GARDIEN A|MARQUÉ PLUS|DE 100 BUTS ?", ["CHILAVERT", "ROGÉRIO CENI", "HIGUITA", "NEUER"], 1, "ceni")]
NIV = ["FACILE", "FACILE", "MOYEN", "DIFFICILE", "LA PLUS DURE"]
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
    """Médaillon « éclat » en papier (étoile à rayons 2 tons, ombre) qui tourne lentement (repris du quiz Real)."""
    k = (r, col, n)
    if k not in _sb:
        im = Image.new("RGBA", (2*r + 80, 2*r + 80), (0, 0, 0, 0)); c = r + 40
        pts = [(c + (r if j % 2 == 0 else r*.78)*math.cos(math.pi*j/n), c + (r if j % 2 == 0 else r*.78)*math.sin(math.pi*j/n)) for j in range(2*n)]
        sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).polygon([(px + 14, py + 18) for px, py in pts], fill=120); im.putalpha(sh.filter(ImageFilter.GaussianBlur(10)))
        d = ImageDraw.Draw(im); d.polygon(pts, fill=col)
        for j in range(n): a0, a1 = math.pi*2*j/n, math.pi*(2*j + 1)/n; d.polygon([(c, c), (c + r*math.cos(a0), c + r*math.sin(a0)), (c + r*.78*math.cos(a1), c + r*.78*math.sin(a1))], fill=tuple(int(v*.85) for v in col))
        d.ellipse([c - r*.55, c - r*.55, c + r*.55, c + r*.55], fill=(250, 246, 236)); d.ellipse([c - r*.5, c - r*.5, c + r*.5, c + r*.5], outline=col, width=8)
        im.info["anchor"] = (c, c); _sb[k] = im
    B.put(L, _sb[k], x, y, 1, t*12)
def rim(sp, col=GOLD, wd=10):
    k = ("rim", id(sp), col)
    if k not in _sb:
        a = sp.getchannel("A").point(lambda v: 255 if v > 90 else 0); g = Image.new("RGBA", sp.size, col + (0,)); g.putalpha(a.filter(ImageFilter.MaxFilter(2*wd + 1)).filter(ImageFilter.GaussianBlur(3)))
        g.info["anchor"] = sp.info["anchor"]; _sb[k] = g
    return _sb[k]
def stars(L, t, pulse):
    """Image 0 : Messi, Ronaldo et Mbappé (devant) sur un médaillon doré, ballon qui tourne."""
    sunburst(L, W//2, 1150, 520, t)
    for n, x, h in (("bdo/messi", 270, 1180), ("real/ronaldo", 820, 1180), ("bdo/mbappe", W//2, 1060)):
        sp = CUT(n, h); B.put(L, rim(sp), x, 1960, 1, 0); B.put(L, sp, x, 1960, 1, 0)
def flag(kind, w=620, h=420):
    """Drapeau en papier (bord blanc, ombre portée), dessiné en code : pas d'image externe."""
    k = ("flag", kind)
    if k in _sb: return _sb[k]
    im = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0)); sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rectangle([40, 44, w + 44, h + 48], fill=130); im.putalpha(sh.filter(ImageFilter.GaussianBlur(9)))
    f = Image.new("RGB", (w, h), WHITE); d = ImageDraw.Draw(f)
    if kind == "angleterre":
        d.rectangle([0, h*.4, w, h*.6], fill=(200, 16, 46)); d.rectangle([w*.44, 0, w*.56, h], fill=(200, 16, 46))
    elif kind == "uruguay":
        for j in range(9):
            if j % 2: d.rectangle([0, j*h/9, w, (j + 1)*h/9], fill=(0, 56, 168))
        d.rectangle([0, 0, w*.42, h*5/9], fill=WHITE); cx, cy, r = w*.21, h*2.5/9, h*.17
        for j in range(16):
            a = math.pi*2*j/16; d.polygon([(cx + r*.6*math.cos(a - .2), cy + r*.6*math.sin(a - .2)), (cx + r*1.5*math.cos(a), cy + r*1.5*math.sin(a)), (cx + r*.6*math.cos(a + .2), cy + r*.6*math.sin(a + .2))], fill=(252, 209, 22))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(252, 209, 22), outline=(140, 90, 20), width=3)
    elif kind == "bresil":
        d.rectangle([0, 0, w, h], fill=(0, 151, 57)); d.polygon([(w*.08, h/2), (w/2, h*.08), (w*.92, h/2), (w/2, h*.92)], fill=(254, 221, 0))
        d.ellipse([w/2 - h*.25, h/2 - h*.25, w/2 + h*.25, h/2 + h*.25], fill=(1, 33, 105))
        d.arc([w/2 - h*.45, h/2 - h*.12, w/2 + h*.4, h/2 + h*.7], 205, 320, fill=WHITE, width=10)
    f = f.convert("RGBA"); m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).polygon(KN.torn_poly(w, h, 5, 26, hash(kind) % 97), fill=255)
    pad = Image.new("RGBA", (w + 24, h + 24), (246, 240, 226, 255)); pm = Image.new("L", pad.size, 0); ImageDraw.Draw(pm).polygon([(x + 12, y + 12) for x, y in KN.torn_poly(w + 24, h + 24, 8, 30, 7)], fill=255)
    im.paste(pad, (18, 18), pm); f.putalpha(m); im.alpha_composite(f, (30, 30)); im.info["anchor"] = (im.width//2, im.height//2); _sb[k] = im
    return im
def bg(L, t, pulse):
    B.dark_bg(L, t, PITCH, "qf"); B.rays(L, (W//2, 900), t, .7, 18, 1900, (30, 110, 60), .1, .3)
    B.glow_spot(L, W//2, 950, 640, tuple(int(c*(.45 + .25*pulse)) for c in GOLD)); B.particles(L, W//2, 1950, W, 1800, t, GOLD, 18, 2)
def wrap(txt, n=20):
    if "|" in txt: return txt.split("|")                       # coupures de ligne imposées
    words, lines, cur = txt.replace(" ?", " ?").replace("« ", "« ").replace(" »", " »").split(" "), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n and cur: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return lines + [cur]
def score_at(t): return sum(1 for e in TL if e[0] == "q" and t >= e[2] - BEAT)
def reveal_illu(L, illu, t, v):
    if illu in ("angleterre", "uruguay", "bresil"):
        B.put(L, flag(illu), W//2, 1400, v, (-4, 3, -2)[("angleterre", "uruguay", "bresil").index(illu)])
        sub = {"angleterre": "1863 · LONDRES", "uruguay": "1930 · MONTEVIDEO", "bresil": "22 COUPES SUR 22"}[illu]
        KN.put_strip(L, sub, 70, W//2, 1680, 2, v, bg=GOLD)
    elif illu == "maradona":
        sunburst(L, W//2, 1430, 330, t); KN.etext(L, "1986", 230, W//2, 1430, (30, 24, 40), s=v)
        KN.put_strip(L, "CONTRE L'ANGLETERRE", 66, W//2, 1690, -2, v, bg=GOLD)
    elif illu == "ceni":
        sunburst(L, W//2, 1430, 330, t); KN.etext(L, "131", 250, W//2, 1400, (30, 24, 40), s=v)
        KN.etext(L, "BUTS", 90, W//2, 1545, (30, 24, 40), s=v)
        KN.put_strip(L, "COUPS FRANCS + PÉNALTYS", 62, W//2, 1690, -2, v, bg=GOLD)
def frame(fr, t):
    pulse = KN.on_beat(t); L = Image.new("RGBA", (W, H), (0, 0, 0, 255)); bg(L, t, pulse)
    e = [x for x in TL if x[1] <= t][-1]; kind = e[0]; u = t - e[1]
    if kind == "hook":                                           # IMAGE 0 : mot-clé géant + visages + défi
        stars(L, t, pulse)
        KN.put_strip(L, "QUIZZ", 190, W//2, 330, -3, 1 + .03*pulse)
        KN.put_strip(L, "FOOTBALL", 170, W//2, 540, 2, 1 + .03*pulse, bg=GOLD)
        KN.put_strip(L, "SI T'AS PAS 5/5…", 100, W//2, 1640, -2, 1 + .03*pulse, bg=RED, fg=WHITE)
    elif kind == "q":
        k, tq = e[3], e[4]; qtxt, ans, good, illu = Q[k]
        rv = t >= e[2] - BEAT                                    # révélation sur le dernier temps du chrono
        KN.put_strip(L, f"QUESTION {k + 1}/5", 70, 260, 230, -4, KN.slam(u), bg=GOLD)
        KN.put_strip(L, NIV[k], 46, 270, 320, 3, KN.slam(u - .15) if u > .15 else 0, bg=RED if k >= 3 else WHITE, fg=WHITE if k >= 3 else (18, 16, 20), tape=False)
        KN.put_strip(L, "QUIZZ FOOTBALL", 50, 610, 232, 3, 1, tape=False)
        lines = wrap(qtxt)
        for j, line in enumerate(lines): KN.etext(L, line, 96, W//2, 440 + j*110, s=B.M.spring(u - .05*j, .3, 16))
        y0 = 440 + len(lines)*110 + 110
        for j, a in enumerate(ans):
            ok = j == good; y = y0 + j*215; s = B.M.spring(u - .25 - .07*j, .3, 16)
            if rv and not ok: s *= max(0, 1 - (t - (e[2] - BEAT))/.15)
            if rv and ok: y = y + (y0 - y)*B.M.ease_out(min(1, (t - (e[2] - BEAT))/.2))   # la bonne réponse remonte en 1re position
            if s <= .02: continue
            bgc = GREEN if (rv and ok) else (235, 230, 220); fgc = WHITE if (rv and ok) else (18, 16, 20)
            KN.put_strip(L, f"{'ABCD'[j]}   {a}", 100, W//2, y, (-1.5, 1.2, -1, 1.5)[j], s*(1 + .08*KN.slam(t - (e[2] - BEAT)) - .08) if (rv and ok) else s, bg=bgc, fg=fgc)
        if t >= tq and not rv:                                   # chrono 3-2-1 (un chiffre tous les 2 temps) + barre qui se vide
            n = max(1, 3 - int((t - tq)/(2*BEAT))); uu = (t - tq) % (2*BEAT)
            KN.etext(L, str(n), 260, 900, 270, RED if n == 1 else GOLD, s=KN.slam(uu, .15))
            frac = 1 - (t - tq)/(GAP - BEAT); ImageDraw.Draw(L).rectangle([90, 1840, 90 + int(900*max(0, frac)), 1860], fill=GOLD)
        if rv:
            v = B.M.spring(t - (e[2] - BEAT), .35, 14); reveal_illu(L, illu, t, v)
            KN.etext(L, "+1", 120, 150, 1790, GREEN, s=v)
        KN.etext(L, f"SCORE {score_at(t)}/5", 70, 900, 1790, GOLD, font="BebasNeue-Regular.ttf")
    else:
        stars(L, t, pulse)
        KN.put_strip(L, "TON SCORE ?", 150, W//2, 300, -3, KN.slam(u), bg=GOLD)
        KN.put_strip(L, "DIS-LE EN COMMENTAIRE", 80, W//2, 470, 2, KN.slam(u - .4) if u > .4 else 0, bg=RED, fg=WHITE)
        KN.put_strip(L, "QUIZZ FOOTBALL", 60, W//2, 610, -2, KN.slam(u - .7) if u > .7 else 0, tape=False)
    if PROVISOIRE: KN.etext(L, "VOIX PROVISOIRE", 40, W//2, 90, (255, 80, 80))
    L.alpha_composite(KN.torn_frame())
    return L.convert("RGB")

def build_audio(wav):
    """Voix découpée + silences de chrono, son de hook à 0 s, whoosh à chaque question, tics du chrono, ding de bonne réponse."""
    S = OUT + "/_a"; os.makedirs(S, exist_ok=True); parts = []
    for k, (a, b) in enumerate(SEG):
        p = f"{S}/s{k}.wav"
        if PROVISOIRE: cmd = ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{b - a:.4f}"]
        else: cmd = ["-ss", str(a), "-t", str(b - a), "-i", VO, "-ar", "44100", "-ac", "2"]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + cmd + [p], check=True); parts.append(p)
        if 1 <= k <= 5:
            g = f"{S}/g{k}.wav"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{GAP:.4f}", g], check=True); parts.append(g)
    with open(f"{S}/l.txt", "w") as f: f.write("".join(f"file '{p}'\n" for p in parts))
    vo = f"{S}/vo.wav"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{S}/l.txt", vo], check=True)
    sfx = os.path.join(ROOT, "episodes", "lille_v5", "sfx"); tick = f"{sfx}/tick.mp3"; whoosh = f"{sfx}/whoosh2.mp3"
    ding = os.path.join(ROOT, "assets", "sfx", "correct.mp3"); hook = os.path.join(ROOT, "assets", "sfx", "hook.mp3")
    ev = [(hook, 0.0, .55)]
    for e in TL:
        if e[0] == "q":
            ev.append((whoosh, e[1], .5))
            for j in range(5): ev.append((tick, e[4] + j*BEAT, .6))
            ev.append((ding, e[2] - BEAT, .8))
    ins = ["-i", vo] + sum([["-i", p] for p, _, _ in ev], []); fc = ""
    for i, (_, ts, g) in enumerate(ev): fc += f"[{i + 1}:a]adelay={int(ts*1000)}|{int(ts*1000)},volume={g}[e{i}];"
    fc += "[0:a]" + "".join(f"[e{i}]" for i in range(len(ev))) + f"amix=inputs={1 + len(ev)}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},loudnorm=I=-14:TP=-1[a]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-filter_complex", fc, "-map", "[a]", wav], check=True)
def main():
    os.makedirs(OUT, exist_ok=True); v = OUT + "/_v.mp4"; a = OUT + "/_a.wav"; build_audio(a)
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-preset", "medium", "-maxrate", "6M", "-bufsize", "12M", v], stdin=subprocess.PIPE)
    for fr in range(int(TOTAL*FPS)): pr.stdin.write(frame(fr, fr/FPS).tobytes())
    pr.stdin.close(); pr.wait(); out = OUT + ("/quiz_football_provisoire.mp4" if PROVISOIRE else "/quiz_football.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    os.remove(v); os.remove(a); print(out, round(TOTAL, 2))
def cover():
    """Couverture : image 0 sans le bandeau provisoire, texte dans la zone 3:4 (y 260..1660)."""
    global PROVISOIRE
    p0, PROVISOIRE = PROVISOIRE, False; im = frame(0, .4); PROVISOIRE = p0
    p = OUT + "/quiz_football_couverture.jpg"; os.makedirs(OUT, exist_ok=True); im.save(p, quality=92); print(p)
def stills():
    ts = [0, 1.5] + sum([[e[1] + .8, e[4] + .5, e[2] - .3] for e in TL if e[0] == "q"], []) + [TL[-1][1] + 1]
    sh = Image.new("RGB", (216*9, 384*2))
    for k, t in enumerate(ts[:18]): sh.paste(frame(int(t*FPS), t).resize((216, 384)), ((k % 9)*216, (k//9)*384))
    p = os.path.join(os.environ.get("STILLS_DIR", OUT), "quiz_football_planche.jpg"); os.makedirs(os.path.dirname(p), exist_ok=True); sh.save(p, quality=85); print(p, round(TOTAL, 2))
if __name__ == "__main__": stills() if "--stills" in sys.argv else (cover() if "--cover" in sys.argv else main())
