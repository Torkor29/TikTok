"""QUIZZ FOOTBALL v2 : même quiz, calé sur la musique « UROBOROS (Hardtekk, slowed) » envoyée par l'utilisateur (126,5 BPM).
Tout tombe sur les temps : questions, chrono 3-2-1 (tics sur les kicks), révélations ; la révélation de la Q5 tombe sur le 2e drop.
Effets « édit » : zoom-punch sur chaque temps, entrée en glissé à la coupe, déchirure papier entre les questions, flash + RGB-split,
bloom, grain, vignette, onde de choc et confettis à chaque bonne réponse, lignes de vitesse, alerte rouge sur le « 1 » du chrono.
Musique sous la voix avec ducking (sidechain). Réutilise les dessins et la voix de quiz_football.py.
  python3 episodes/quiz_football/quiz_football_v2.py [--stills]"""
import sys, os, math, subprocess
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "engine"))
_argv = sys.argv; sys.argv = [sys.argv[0], "--noop"]
import quiz_football as V1                                       # questions, voix découpée, médaillons, drapeaux, joueurs
sys.argv = _argv
import fx
import numpy as np
from PIL import Image, ImageDraw
KN, B = V1.KN, V1.B
W, H, FPS = V1.W, V1.H, V1.FPS
GOLD, GREEN, RED, WHITE = V1.GOLD, V1.GREEN, V1.RED, V1.WHITE
MUSIC = os.path.join(ROOT, "assets", "music", "uroboros_hardtekk_slowed.mp3")
BEAT = 0.4743; PHASE = 0.096                                     # grille mesurée sur les kicks (126,5 BPM, 1er temps à 0,096 s)
DROP1, BREAK, DROP2 = PHASE + 32*BEAT, PHASE + 97*BEAT, PHASE + 129*BEAT   # 15,27 s / 46,1 s / 61,28 s dans le morceau
OUT = V1.OUT; SEG = V1.SEG; Q = V1.Q; NIV = V1.NIV
def dur(i): return SEG[i][1] - SEG[i][0]
def ceilb(x): return math.ceil(x/BEAT - 1e-6)*BEAT
# timeline calée sur les temps : ("hook", début, fin) / ("q", début, fin, k, début chrono, révélation) / ("end", début, fin)
TL = [("hook", 0.0, ceilb(dur(0)))]; t = TL[-1][2]
for k in range(5):
    tq = ceilb(t + dur(2*k + 1) + .05); rvt = tq + 5*BEAT
    TL.append(("q", t, ceilb(rvt + .3 + dur(2*k + 2) + .25), k, tq, rvt)); t = TL[-1][2]
TL.append(("end", t, t + dur(11) + 1.6)); TOTAL = TL[-1][2]
M = DROP2 - TL[5][5]                                             # décalage musique : la révélation de la Q5 tombe sur le 2e drop
CUTS = [e[1] for e in TL]; REVEALS = [e[5] for e in TL if e[0] == "q"]
HITS = REVEALS + [DROP1 - M]                                     # flash / RGB-split : révélations + 1er drop (le « SI T'AS PAS 5/5 » claque dessus)
def in_break(t): return BREAK <= t + M < DROP2
def on_beat(t, w=.12):
    k = round(t/BEAT); p = max(0.0, 1 - abs(t - k*BEAT)/w) if k >= 1 else 0.0   # rien à 0 s : l'image 0 reste nette
    return p*.3 if in_break(t) else p
def scene(fr, t):
    """L'image du quiz (sans post-traitement) : reprise de quiz_football.frame + effets de révélation."""
    pulse = on_beat(t); L = Image.new("RGBA", (W, H), (0, 0, 0, 255)); V1.bg(L, t, pulse)
    e = [x for x in TL if x[1] <= t][-1]; kind = e[0]; u = t - e[1]
    if kind == "hook":
        V1.stars(L, t, pulse)
        fx.shockwave(L, t, DROP1 - M, W//2, 1640, .6, 1100, GOLD)
        KN.put_strip(L, "QUIZZ", 190, W//2, 330, -3, 1 + .04*pulse)   # titre lisible dès l'image 0
        KN.put_strip(L, "FOOTBALL", 170, W//2, 540, 2, 1 + .04*pulse, bg=GOLD)
        KN.put_strip(L, "SI T'AS PAS 5/5…", 100, W//2, 1640, -2, (KN.slam(u - (DROP1 - M)) if u > DROP1 - M else 0) + .04*pulse, bg=RED, fg=WHITE)
    elif kind == "q":
        k, tq, rvt = e[3], e[4], e[5]; qtxt, ans, good, illu = Q[k]; rv = t >= rvt
        if u < .45: B.speed_lines(L, fr, (W//2, 760), 1 - u/.45, 40, (255, 255, 255), 420, k)
        KN.put_strip(L, f"QUESTION {k + 1}/5", 70, 260, 230, -4, KN.slam(u), bg=GOLD)
        KN.put_strip(L, NIV[k], 46, 270, 320, 3, KN.slam(u - .15) if u > .15 else 0, bg=RED if k >= 3 else WHITE, fg=WHITE if k >= 3 else (18, 16, 20), tape=False)
        KN.put_strip(L, "QUIZZ FOOTBALL", 50, 610, 232, 3, 1, tape=False)
        lines = V1.wrap(qtxt)
        for j, line in enumerate(lines): KN.etext(L, line, 96, W//2, 440 + j*110, s=B.M.spring(u - .05*j, .3, 16) + .03*pulse)
        y0 = 440 + len(lines)*110 + 110; ur = t - rvt
        for j, a in enumerate(ans):
            ok = j == good; y = y0 + j*215; x = W//2; s = B.M.spring(u - .25 - .07*j, .3, 16)
            if rv and not ok: x += (-1 if j % 2 else 1)*1300*B.M.ease_in(min(1, ur/.25)); s *= 1 - .3*min(1, ur/.25)   # les fausses s'envolent
            if rv and ok: y = y + (y0 - y)*B.M.ease_out(min(1, ur/.2))
            if s <= .02 or x < -600 or x > W + 600: continue
            bgc = GREEN if (rv and ok) else (235, 230, 220); fgc = WHITE if (rv and ok) else (18, 16, 20)
            sc = s*(1 + .08*KN.slam(ur) - .08) + .05*pulse if (rv and ok) else s + (.03*pulse if not rv else 0)
            KN.put_strip(L, f"{'ABCD'[j]}   {a}", 100, x, y, (-1.5, 1.2, -1, 1.5)[j], sc, bg=bgc, fg=fgc)
        if tq <= t < rvt:                                        # chrono 3-2-1 sur les temps
            n = max(1, 3 - int((t - tq)/(2*BEAT))); uu = (t - tq) % (2*BEAT)
            if n == 1:                                           # alerte rouge : bords qui pulsent
                a = int(150*(.5 + .5*math.cos((t - tq)*math.pi/BEAT*2)))
                ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
                for i in range(6): d.rectangle([i*14, i*14, W - i*14, H - i*14], outline=(230, 20, 30, max(0, a - i*22)), width=14)
                L.alpha_composite(ov)
            KN.etext(L, str(n), 260, 900, 270, RED if n == 1 else GOLD, s=KN.slam(uu, .15) + .06*pulse)
            frac = 1 - (t - tq)/(5*BEAT); ImageDraw.Draw(L).rectangle([90, 1840, 90 + int(900*max(0, frac)), 1860], fill=RED if n == 1 else GOLD)
        if rv:
            v = B.M.spring(ur, .35, 14); V1.reveal_illu(L, illu, t, v)
            fx.shockwave(L, t, rvt, W//2, y0, .5, 900, (120, 255, 150))
            B.confetti(L, fr, 100 + k, ur, 110 if k == 4 else 60, 2.2, [GOLD, GREEN, WHITE, RED], (0, 0, W, H))
            KN.etext(L, "+1", 120, 150, 1790, GREEN, s=v)
        KN.etext(L, f"SCORE {sum(1 for r in REVEALS if t >= r)}/5", 70, 900, 1790, GOLD, font="BebasNeue-Regular.ttf")
    else:
        V1.stars(L, t, pulse)
        KN.put_strip(L, "TON SCORE ?", 150, W//2, 300, -3, KN.slam(u) + .04*pulse, bg=GOLD)
        KN.put_strip(L, "DIS-LE EN COMMENTAIRE", 80, W//2, 470, 2, (KN.slam(u - .4) if u > .4 else 0) + .03*pulse, bg=RED, fg=WHITE)
        KN.put_strip(L, "QUIZZ FOOTBALL", 60, W//2, 610, -2, KN.slam(u - .7) if u > .7 else 0, tape=False)
        B.confetti(L, fr, 999, u, 70, 4.0, [GOLD, GREEN, WHITE, RED], (0, 0, W, H))
    return L.convert("RGB")
RIP = .3
def frame(fr):
    t = fr/FPS; pulse = on_beat(t)
    ev = [c for c in CUTS[1:] + HITS if c <= t]; last = max(ev) if ev else -10.0; local = t - last   # pas de flash à l'image 0 : elle doit se lire
    ci = max(i for i, c in enumerate(CUTS) if c <= t); side = 0 if last in HITS else (1 if ci % 2 else -1)
    im = scene(fr, t)
    if 1 <= ci and t - CUTS[ci] < RIP:                           # déchirure papier entre deux scènes
        im = KN.rip(scene(fr, CUTS[ci] - 1/FPS), im, (t - CUTS[ci])/RIP, ci)
    im = KN.punch(im, t, pulse, local, side*.6)
    a = KN.grade(np.asarray(im), t, pulse, local)
    out = Image.fromarray(a).convert("RGBA"); out.alpha_composite(KN.torn_frame())
    return np.asarray(out.convert("RGB")).tobytes()

def build_audio(wav):
    """Voix (chaque phrase à sa place) + musique calée (ducking sous la voix) + tics sur les temps, ding, whoosh, boom sur les drops."""
    S = OUT + "/_a2"; os.makedirs(S, exist_ok=True)
    pos = [0.0] + sum([[e[1], e[5] + .3] for e in TL if e[0] == "q"], []) + [TL[-1][1] + .1]
    vo_ev = []
    for k, (a, b) in enumerate(SEG):
        p = f"{S}/s{k}.wav"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(a), "-t", str(b - a), "-i", V1.VO, "-ar", "48000", "-ac", "2", p], check=True)
        vo_ev.append((p, pos[k], 1.0))
    sfx = os.path.join(ROOT, "episodes", "lille_v5", "sfx"); A = os.path.join(ROOT, "assets", "sfx")
    fx_ev = [(f"{A}/hook.mp3", 0.0, .5)]
    for e in TL:
        if e[0] == "q":
            fx_ev.append((f"{sfx}/whoosh2.mp3", e[1] - .12, .55))
            for j in range(5): fx_ev.append((f"{sfx}/tick.mp3", e[4] + j*BEAT, .45))
            fx_ev.append((f"{A}/correct.mp3", e[5], .8))
    fx_ev.append((f"{A}/boom.mp3", TL[5][5], .8))
    def mix(evs, out):
        ins = ["-f", "lavfi", "-t", f"{TOTAL:.2f}", "-i", "anullsrc=r=48000:cl=stereo"] + sum([["-i", p] for p, _, _ in evs], []); fc = ""
        for i, (_, ts, g) in enumerate(evs): fc += f"[{i + 1}:a]aresample=48000,adelay={int(max(0, ts)*1000)}|{int(max(0, ts)*1000)},volume={g}[e{i}];"
        fc += "[0:a]" + "".join(f"[e{i}]" for i in range(len(evs))) + f"amix=inputs={1 + len(evs)}:normalize=0:duration=first[a]"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-filter_complex", fc, "-map", "[a]", out], check=True)
    mix(vo_ev, f"{S}/vo.wav"); mix(fx_ev, f"{S}/fx.wav")
    fc = (f"[1:a]atrim=0:{TOTAL:.2f},asetpts=PTS-STARTPTS,volume=0.2,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2[mus];"
          "[0:a]asplit=2[v][key];[mus][key]sidechaincompress=threshold=0.015:ratio=8:attack=8:release=300[md];"
          f"[v][md][2:a]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1,aresample=48000[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{S}/vo.wav", "-ss", f"{M:.3f}", "-i", MUSIC, "-i", f"{S}/fx.wav",
                    "-filter_complex", fc, "-map", "[a]", "-ar", "48000", wav], check=True)
def main():
    os.makedirs(OUT, exist_ok=True); v = OUT + "/_v2.mp4"; a = OUT + "/_a2.wav"; build_audio(a)
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "medium", "-maxrate", "8M", "-bufsize", "16M", v], stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for b in pool.imap(frame, range(int(TOTAL*FPS)), chunksize=6): pr.stdin.write(b)
    pr.stdin.close(); pr.wait(); out = OUT + "/quiz_football_v2.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    os.remove(v); os.remove(a); subprocess.run(["rm", "-rf", OUT + "/_a2"]); print(out, round(TOTAL, 2))
def stills():
    ts = [0, .15, 1.0] + sum([[e[1] + .1, e[4] + 4.2*BEAT, e[5] + .08, e[5] + .6] for e in TL if e[0] == "q"], []) + [TL[-1][1] + 1.2]
    sh = Image.new("RGB", (216*8, 384*3))
    for k, t in enumerate(ts[:24]):
        sh.paste(Image.frombytes("RGB", (W, H), frame(int(round(t*FPS)))).resize((216, 384)), ((k % 8)*216, (k//8)*384))
    p = os.path.join(os.environ.get("STILLS_DIR", OUT), "quiz_football_v2_planche.jpg"); sh.save(p, quality=85); print(p, round(TOTAL, 2), "M =", round(M, 3))
if __name__ == "__main__":
    print("timeline", [(e[0], round(e[1], 2), round(e[2], 2)) for e in TL], "TOTAL", round(TOTAL, 2), "M", round(M, 3), "break vidéo", round(BREAK - M, 2))
    stills() if "--stills" in sys.argv else main()
