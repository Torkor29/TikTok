"""DEVINE LES 15 STARS DU PSG : format « Guess 30 superstars » (référence envoyée par l'utilisateur) refait dans notre DA papier.
Tableau papier en haut (FACILE / MOYEN / DIFFICILE, 5 lignes chacun) qui se remplit, joueur en papier découpé au centre,
compte à rebours 2… 1 sur les temps, révélation du nom (bande verte + voix), CTA « abonne-toi » avant le niveau moyen.
Calé sur « UROBOROS (Hardtekk, slowed) » à 126,5 BPM, musique très basse sous la voix, pas de pulsation.
Photos : assets/photos/psg/<slug>.png (envoyées par l'utilisateur) ; sans photo -> silhouette noire provisoire.
Voix : voix/voix.mp3 (19 phrases, TEXTE ci-dessous) découpée avec faster-whisper -> voix/segments.json.
  python3 episodes/devine_psg15/devine_psg15.py [--stills | --cover]"""
import sys, os, math, subprocess, json
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "episodes", "quiz_football")); sys.path.insert(0, os.path.join(ROOT, "engine"))
_argv = sys.argv; sys.argv = [sys.argv[0], "--noop"]
import quiz_football as V1                                       # médaillon, liseré, typo d'édit, fond, bandes papier
sys.argv = _argv
import fx
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
KN, B = V1.KN, V1.B
W, H, FPS = V1.W, V1.H, V1.FPS
GOLD, GREEN, RED, WHITE = V1.GOLD, V1.GREEN, V1.RED, V1.WHITE
NAVY = (12, 22, 64); ORANGE = (240, 140, 30); INK = (24, 22, 30); CREAM = (246, 240, 226)
OUT = os.path.join(ROOT, "output", "devine_psg15")
MUSIC = os.path.join(ROOT, "assets", "music", "uroboros_hardtekk_slowed.mp3")
BEAT = 0.4743; PHASE = 0.096; DROP1 = PHASE + 32*BEAT
VO = os.path.join(HERE, "voix", "voix.mp3"); SEGF = os.path.join(HERE, "voix", "segments.json")
# (nom affiché, slug photo, mots dits)
P = [("MBAPPÉ", "mbappe", "Mbappé"), ("MESSI", "messi", "Messi"), ("NEYMAR", "neymar", "Neymar"), ("IBRAHIMOVIC", "ibrahimovic", "Ibrahimovic"),
     ("DEMBÉLÉ", "dembele", "Dembélé"),
     ("THIAGO SILVA", "thiago_silva", "Thiago Silva"), ("MARQUINHOS", "marquinhos", "Marquinhos"), ("DI MARÍA", "di_maria", "Di María"),
     ("RONALDINHO", "ronaldinho", "Ronaldinho"), ("BECKHAM", "beckham", "Beckham"),
     ("PAULETA", "pauleta", "Pauleta"), ("GINOLA", "ginola", "Ginola"), ("WEAH", "weah", "Weah"), ("RAÍ", "rai", "Raï"), ("DJORKAEFF", "djorkaeff", "Djorkaeff")]
TEXTE = (["Devine ces quinze stars du PSG !"] + [p[2] for p in P[:5]] + ["Avant le niveau moyen, abonne-toi !"] + [p[2] for p in P[5:10]]
         + ["Niveau difficile !"] + [p[2] for p in P[10:]] + ["T'en as trouvé combien sur quinze ? Dis-le en commentaire !"])
LEVELS = [("FACILE", GREEN), ("MOYEN", ORANGE), ("DIFFICILE", RED)]
PHOTO = {"mbappe": "bdo/mbappe", "messi": "bdo/messi", "dembele": "bdo/dembele"}   # repli tant que la photo PSG n'est pas fournie
def photo(slug):
    p = os.path.join(ROOT, "assets", "photos", "psg", slug + ".png")
    if os.path.exists(p): return "psg/" + slug, True
    return (PHOTO[slug], True) if slug in PHOTO else ("bdo/dembele", False)          # False = silhouette provisoire
PROVISOIRE = not os.path.exists(VO)
if PROVISOIRE:
    SEG, t = [], 0.0
    for s in TEXTE: d = round(len(s)/17 + .3, 2); SEG.append((t, t + d)); t += d
else: SEG = json.load(open(SEGF))
def dur(i): return SEG[i][1] - SEG[i][0]
def ceilb(x): return math.ceil(x/BEAT - 1e-6)*BEAT
# timeline : hook, 5 joueurs, CTA, 5 joueurs, 5 joueurs (le 1er annonce « niveau difficile »), fin. Joueur = 6 temps : « 2 » (0-2), « 1 » (2-4), révélation (4-6)
TL = [("hook", 0.0, ceilb(dur(0) + .1), 0)]; t = TL[-1][2]; vpos = [0.0]; si = 1
for i in range(15):
    if i == 5:
        TL.append(("cta", t, ceilb(t + dur(si) + .35), si)); vpos.append(t + .05); si += 1; t = TL[-1][2]
    if i == 10: vpos.append(t); si += 1                          # « Niveau difficile ! » pendant le « 2 » du 11e joueur
    TL.append(("p", t, t + 6*BEAT, i, t + 4*BEAT)); vpos.append(t + 4*BEAT + .04); si += 1; t = TL[-1][2]
TL.append(("end", t, t + dur(18) + 2.0, 18)); vpos.append(t + .1); TOTAL = TL[-1][2]
FIRST = TL[1][1]; M = DROP1 - FIRST                              # le drop de la musique tombe sur l'apparition du 1er joueur
REVEALS = [e[4] for e in TL if e[0] == "p"]; CUTS = [e[1] for e in TL]

_cache = {}
def cut(slug, h):
    k = (slug, h)
    if k not in _cache:
        n, ok = photo(slug); sp = V1.CUT(n, h)
        if not ok:                                               # silhouette noire « ? »
            a = sp.getchannel("A"); sil = Image.new("RGBA", sp.size, (14, 14, 20, 255)); sil.putalpha(a); sil.info["anchor"] = sp.info["anchor"]; sp = sil
        _cache[k] = (sp, ok)
    return _cache[k]
def board_img():
    """Feuille de papier déchirée (scotchée) avec les 3 colonnes de niveau et les 15 lignes vides."""
    if "board" in _cache: return _cache["board"]
    bw, bh = 1010, 640; im = Image.new("RGBA", (bw + 80, bh + 80), (0, 0, 0, 0))
    m = Image.new("L", (bw, bh), 0); ImageDraw.Draw(m).polygon(KN.torn_poly(bw, bh, 10, 22, 11), fill=255)
    sh = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(9)).point(lambda v: v*150//255)); im.alpha_composite(sh, (48, 54))
    pap = KN.paper_tex(bw, bh, CREAM, 5).convert("RGBA"); pap.putalpha(m); im.alpha_composite(pap, (40, 40))
    d = ImageDraw.Draw(im); f = KN._font("BebasNeue-Regular.ttf", 46)
    for c in range(3):
        x0 = 40 + 30 + c*330
        for r in range(5):
            y = 40 + 140 + r*92; d.text((x0, y), f"{c*5 + r + 1}.", font=f, fill=(120, 110, 100))
            d.line([(x0 + 52, y + 44), (x0 + 300, y + 44)], fill=(200, 190, 175), width=3)
        if c: d.line([(40 + c*330, 40 + 110), (40 + c*330, 40 + bh - 30)], fill=(215, 205, 190), width=3)
    for x, y, r in ((90, 40, -25), (bw - 10, 40, 25)):
        tp = Image.new("RGBA", (150, 46), (240, 232, 205, 175)).rotate(r, expand=True); im.alpha_composite(tp, (x - tp.width//2, y - tp.height//2))
    im.info["anchor"] = (im.width//2, im.height//2); _cache["board"] = im
    return im
BX, BY = W//2, 470                                               # centre du tableau (y ≈ 150 … 790)
def board(L, t):
    B.put(L, board_img(), BX, BY, 1, 0)
    for c, (lab, col) in enumerate(LEVELS):
        KN.put_strip(L, lab, 54, 40 + 165 + c*330 - 45, BY - 255, (-3, 2, -2)[c], 1, bg=col, fg=WHITE, tape=False)
    for i, rv in enumerate(REVEALS):
        if t < rv + .05: continue
        u = t - rv - .05; c, r = divmod(i, 5); x0 = 40 + 30 + c*330 + 52 - 40 + 8; y = BY - 320 + 40 + 140 + r*92 + 22
        name = P[i][0]; size = 44 if len(name) < 11 else 38
        img = KN.etext_img(name, size, INK, font="Anton-Regular.ttf", track=1)
        k = min(1, u/.3); wv = max(1, int(img.width*k))              # le nom s'écrit de gauche à droite
        part = img.crop((0, 0, wv, img.height)); L.alpha_composite(part, (int(x0 + 44), int(y - img.height//2)))
        if u < .5: fx.shockwave(L, t, rv + .05, x0 + 44 + img.width//2, y, .35, 120, GREEN)
def bg(L, t):
    B.dark_bg(L, t, NAVY, "pg"); B.rays(L, (W//2, 1250), t, .7, 18, 1900, (30, 40, 110), .1, .3)
    B.glow_spot(L, W//2, 1250, 600, (110, 30, 40)); B.particles(L, W//2, 1950, W, 1800, t, GOLD, 16, 2)
def player(L, i, t, u, fr):
    sp, ok = cut(P[i][1], 1000); s = B.M.spring(u, .3, 15); x = W//2 + (1 - B.M.ease_out(min(1, u/.25)))*(700 if i % 2 else -700)
    V1.sunburst(L, W//2, 1230, 360, t, GOLD if ok else (150, 150, 160))
    B.put(L, V1.rim(sp, WHITE if not ok else GOLD), x, 1830, s, 0); B.put(L, sp, x, 1830, s, 0)
    if not ok: KN.etext(L, "?", 300, W//2, 1180, WHITE, s=s)
def frame_img(fr, t):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 255)); bg(L, t)
    e = [x for x in TL if x[1] <= t][-1]; kind = e[0]; u = t - e[1]
    if kind == "hook":                                           # image 0 : écusson énorme + défi
        lg = _cache.setdefault("logo", B.logo("psg", 640)); B.put(L, lg, W//2, 1090, 1, 0)
        KN.put_strip(L, "DEVINE CES", 120, W//2, 300, -3, 1)
        KN.put_strip(L, "15 STARS", 190, W//2, 500, 2, 1, bg=GOLD)
        KN.put_strip(L, "DU PSG", 150, W//2, 1640, -2, 1, bg=RED, fg=WHITE)
        return L
    board(L, t)
    if kind == "p":
        i, rvt = e[3], e[4]; player(L, i, t, u, fr)
        lv = i//5
        if i % 5 == 0 and u < 1.2 and i:                          # annonce du niveau
            KN.put_strip(L, "NIVEAU " + LEVELS[lv][0], 90, W//2, 900, -3, KN.slam(u), bg=LEVELS[lv][1], fg=WHITE)
        if t < rvt:
            n = 2 - int(u/(2*BEAT)); uu = u % (2*BEAT)
            KN.put_strip(L, str(n), 170, W//2, 1560, (-4, 4)[n - 1], KN.slam(uu, .15), bg=CREAM if n == 2 else RED, fg=INK if n == 2 else WHITE)
        else:
            ur = t - rvt; v = B.M.spring(ur, .3, 15)
            KN.put_strip(L, P[i][0], 120, W//2, 1500, -2, v*(1 + .1*KN.slam(ur) - .1), bg=GREEN, fg=WHITE)
            B.confetti(L, fr, 50 + i, ur, 45, 1.6, [GOLD, GREEN, WHITE, RED], (0, 800, W, H))
        KN.etext(L, f"{i + 1}/15", 70, 920, 1790, GOLD, font="BebasNeue-Regular.ttf")
    elif kind == "cta":
        s = KN.slam(u)
        KN.put_strip(L, "AVANT LE NIVEAU MOYEN…", 78, W//2, 1020, -2, s, bg=CREAM, fg=INK)
        KN.put_strip(L, "+ ABONNE-TOI !", 140, W//2, 1240, 3, KN.slam(u - .3) if u > .3 else 0, bg=RED, fg=WHITE)
    else:
        KN.put_strip(L, "T'EN AS TROUVÉ COMBIEN", 74, W//2, 1050, -2, KN.slam(u), bg=GOLD)
        KN.put_strip(L, "SUR 15 ?", 150, W//2, 1240, 2, KN.slam(u - .25) if u > .25 else 0, bg=RED, fg=WHITE)
        KN.put_strip(L, "DIS-LE EN COMMENTAIRE", 70, W//2, 1430, -1, KN.slam(u - .6) if u > .6 else 0)
        B.confetti(L, fr, 999, u, 80, 4.0, [GOLD, GREEN, WHITE, RED], (0, 0, W, H))
    return L
RIP = .25
def frame(fr):
    t = fr/FPS; im = frame_img(fr, t).convert("RGB")
    ci = max(i for i, c in enumerate(CUTS) if c <= t)
    if ci == 1 and t - CUTS[1] < RIP: im = KN.rip(frame_img(fr, CUTS[1] - 1/FPS).convert("RGB"), im, (t - CUTS[1])/RIP, 1)   # déchirure hook -> jeu
    ev = [c for c in REVEALS if c <= t]; local = t - max(ev) if ev else 10.0
    im = KN.punch(im, t, 0.0, max(local, .45) if not ev else local, 0)           # léger zoom d'impact à la révélation, aucune pulsation
    a = KN.grade(np.asarray(im), t, 0.0, local)
    out = Image.fromarray(a).convert("RGBA"); out.alpha_composite(KN.torn_frame())
    if PROVISOIRE: KN.etext(out, "VOIX PROVISOIRE", 40, W//2, 90, (255, 80, 80))
    return np.asarray(out.convert("RGB")).tobytes()

def build_audio(wav):
    S = OUT + "/_a"; os.makedirs(S, exist_ok=True); evs = []
    for k, (a, b) in enumerate(SEG):
        p = f"{S}/s{k}.wav"
        cmd = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{b - a:.3f}"] if PROVISOIRE else ["-ss", str(a), "-t", str(b - a), "-i", VO, "-ar", "48000", "-ac", "2"]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + cmd + [p], check=True); evs.append((p, vpos[k], 1.0))
    sfx = os.path.join(ROOT, "episodes", "lille_v5", "sfx"); A = os.path.join(ROOT, "assets", "sfx")
    evs.append((f"{A}/hook.mp3", 0.0, .5))
    for e in TL:
        if e[0] == "p":
            evs.append((f"{sfx}/whoosh2.mp3", e[1] - .1, .45)); evs.append((f"{sfx}/tick.mp3", e[1], .5)); evs.append((f"{sfx}/tick.mp3", e[1] + 2*BEAT, .5))
            evs.append((f"{A}/correct.mp3", e[4], .55)); evs.append((f"{sfx}/marker.mp3", e[4] + .1, .35))
    ins = ["-f", "lavfi", "-t", f"{TOTAL:.2f}", "-i", "anullsrc=r=48000:cl=stereo"] + sum([["-i", p] for p, _, _ in evs], []); fc = ""
    for i, (_, ts, g) in enumerate(evs): fc += f"[{i + 1}:a]aresample=48000,adelay={int(max(0, ts)*1000)}|{int(max(0, ts)*1000)},volume={g}[e{i}];"
    fc += "[0:a]" + "".join(f"[e{i}]" for i in range(len(evs))) + f"amix=inputs={1 + len(evs)}:normalize=0:duration=first[a]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-filter_complex", fc, "-map", "[a]", f"{S}/vo.wav"], check=True)
    fc = ("[0:a]loudnorm=I=-14:TP=-1.5,aresample=48000,asplit=2[v][key];"
          f"[1:a]atrim=0:{TOTAL:.2f},asetpts=PTS-STARTPTS,aresample=48000,volume=0.035,afade=t=out:st={TOTAL - 1.5:.2f}:d=1.5[mus];"
          "[mus][key]sidechaincompress=threshold=0.02:ratio=6:attack=8:release=300[md];[v][md]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{S}/vo.wav", "-ss", f"{M:.3f}", "-i", MUSIC, "-filter_complex", fc, "-map", "[a]", "-ar", "48000", wav], check=True)
def main():
    os.makedirs(OUT, exist_ok=True); v = OUT + "/_v.mp4"; a = OUT + "/_a.wav"; build_audio(a)
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-preset", "medium", "-maxrate", "6M", "-bufsize", "12M", v], stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for b in pool.imap(frame, range(int(TOTAL*FPS)), chunksize=6): pr.stdin.write(b)
    pr.stdin.close(); pr.wait(); out = OUT + ("/devine_psg15_provisoire.mp4" if PROVISOIRE else "/devine_psg15.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    os.remove(v); os.remove(a); subprocess.run(["rm", "-rf", OUT + "/_a"]); print(out, round(TOTAL, 2))
def stills():
    ps = [e for e in TL if e[0] == "p"]
    ts = [0, CUTS[1] + .12] + sum([[e[1] + .5, e[1] + 2.5*BEAT, e[4] + .4] for e in ps[:2]], []) + [ps[4][4] + .6, TL[6][1] + 1, ps[5][1] + .5, ps[10][1] + .6, ps[14][4] + .6, TL[-1][1] + 1.5]
    sh = Image.new("RGB", (216*7, 384*2))
    for k, t in enumerate(ts[:14]): sh.paste(Image.frombytes("RGB", (W, H), frame(int(round(t*FPS)))).resize((216, 384)), ((k % 7)*216, (k//7)*384))
    p = os.path.join(os.environ.get("STILLS_DIR", OUT), "devine_psg15_planche.jpg"); os.makedirs(os.path.dirname(p), exist_ok=True); sh.save(p, quality=85); print(p, round(TOTAL, 2))
def cover():
    os.makedirs(OUT, exist_ok=True); im = Image.frombytes("RGB", (W, H), frame(0)); p = OUT + "/devine_psg15_couverture.jpg"; im.save(p, quality=92); print(p)
if __name__ == "__main__":
    print("TOTAL", round(TOTAL, 2), "M", round(M, 3)); stills() if "--stills" in sys.argv else (cover() if "--cover" in sys.argv else main())
