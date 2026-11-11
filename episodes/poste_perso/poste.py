"""« Dis-moi où tu joues, je te dis qui tu es » — DA « Le Terrain » (nuage de points 3D, vraies couleurs, caméra qui vole
sur un seul terrain, traits de caractère peints sur la pelouse). Voix Léo, bruitages synthétisés, pas de musique.
  python3 episodes/poste_perso/poste.py [--stills out.jpg]"""
import os, sys, math, subprocess, wave
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "engine"))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import terrain as T
import karaoke as KA
W, H, FPS, SR = 1080, 1920, 30, 48000
TEXTE = ["Dis-moi où tu joues, je te dis qui tu es.",
         "Gardien : t'es le seul qui a le droit de crier sur tout le monde… et c'est quand même toujours ta faute.",
         "Défenseur central : t'es le pote fiable. Celui qu'on appelle pour un déménagement.",
         "Latéral : tu cours plus que tout le monde… et personne ne le remarque.",
         "Milieu : t'as un avis sur tout. Et le pire, c'est que t'as souvent raison.",
         "Ailier : tu dribbles trois fois de trop. Et tu le fais exprès.",
         "Attaquant : tu rates neuf occasions, tu marques la dixième… et tu célèbres comme si t'avais tout fait.",
         "Et remplaçant… on t'aime quand même.",
         "Alors, t'es lequel ? Dis ton poste en commentaire, et tague le pote qui se reconnaît."]
KEYS = {"gardien", "defenseur", "central", "lateral", "milieu", "ailier", "attaquant", "remplacant", "crier", "faute", "fiable", "demenagement",
        "cours", "remarque", "avis", "raison", "dribbles", "expres", "dixieme", "celebres", "aime", "lequel", "commentaire", "tague", "joues", "qui"}
VOIX = os.path.join(HERE, "voix", "voix.mp3"); WD = KA.Words(TEXTE, VOIX); L0 = [WD.line(i)[0] for i in range(len(TEXTE))]
TOTAL = WD.end + .8
GOLD, BLUE = T.rgb(255, 210, 60), T.rgb(60, 140, 255)
TEAM = {"gk": ("keeper", 0, -49), "cb1": ("wall", -8, -38), "cb2": ("wall", 8, -38), "lb": ("stand", -27, -33), "rb": ("stand", 27, -33),
        "cm": ("stand", 0, -22), "m1": ("stand", -13, -16), "m2": ("stand", 13, -16), "lw": ("run", -25, -3), "rw": ("run", 25, -3), "st": ("stand", 0, -1)}
BENCH = [(-37.5, -6), (-37.5, -3.5), (-37.5, -1)]
#          ligne, joueur, caméra (pos, cible), étiquette peinte, ancre, largeur
#          ligne, joueur, direction caméra (depuis le joueur), étiquette peinte
SHOTS = [(0, None, None, "QUI ES-TU ?"), (1, "gk", (.35, 1), "LE CHEF"), (2, "cb1", (.45, 1), "LE FIABLE"), (3, "lb", (1, -.35), "L'INVISIBLE"),
         (4, "cm", (.5, 1), "LE CERVEAU"), (5, "lw", (.7, 1), "LE SHOWMAN"), (6, "st", (.35, -1), "L'ÉGO"), (7, "bench", (1, -.25), "LE FIDÈLE"),
         (8, "all", None, "ET TOI ?")]
WIDE = ((0, 30, -66), (0, 2, -10))
def focus(name, t):
    if name == "bench": return BENCH[1]
    return player_pos(name, t)
def shot_cam(k, t):
    s = SHOTS[k]
    if s[2] is None: return T.Cam(*WIDE)
    x, z = focus(s[1], t); dx, dz = s[2]; n = math.hypot(dx, dz); dx, dz = dx/n, dz/n
    return T.Cam((x + dx*5.6, 2.4, z + dz*5.6), (x + dx*.6, 1.5, z + dz*.6))
def label_geo(k, t):
    s = SHOTS[k]
    if s[2] is None: return (0, 0, -10), 34
    x, z = focus(s[1], t) if s[1] != "lb" else player_pos("lb", L0[3] + 3); dx, dz = s[2]; n = math.hypot(dx, dz)
    return (x + dx/n*2.4, 0, z + dz/n*2.4), 2.1
def shot_at(t):
    k = 0
    for i, s in enumerate(SHOTS):
        if t >= L0[s[0]] - .35: k = i
    return k
def cam_at(t):
    k = shot_at(t); t0 = L0[SHOTS[k][0]] - .35; b = shot_cam(k, t)
    if k == 0: c = b
    else:
        u = min(1.0, (t - t0)/.85); c = T.lerp_cam(shot_cam(k - 1, t0), b, u)
        c.pos = c.pos + np.array([0, 16*math.sin(math.pi*u), 0], np.float32)          # arc de drone pendant le vol
    if k in (0, 8): a = .22*math.sin(t*.4); c = T.Cam((c.pos[0] + 18*a, c.pos[1], c.pos[2]), c.tgt)
    end = L0[SHOTS[k + 1][0]] - .35 if k + 1 < len(SHOTS) else TOTAL; d = (t - t0)/max(1, end - t0)
    c.pos = c.pos + (c.tgt - c.pos)*.07*d
    tl = t - (L0[SHOTS[k][0]] + .25)
    if k and 0 < tl < .5: c.pos = c.pos + (c.tgt - c.pos)*.12*math.sin(tl/.5*math.pi)          # coup de zoom quand le mot s'écrit
    return c
def player_pos(name, t):
    p, x, z = TEAM[name]
    if name == "lb":
        t0 = L0[3]; u = min(1, max(0, (t - t0)/2.6)); z = z + 33*(u*u*(3 - 2*u))
    if name == "lw":
        t0 = L0[5]; u = max(0, t - t0); x = x + 2.2*math.sin(u*6)*min(1, u); z = z + min(9, u*3.2)
    if name == "st" and shot_at(t) == 6: x, z = 1.5, 36.5
    return x, z
def pose_of(name, t):
    p = TEAM[name][0]; k = shot_at(t)
    if name == "gk" and k == 1 and t > WD.t(1, "crier") - .1: return "arms" if int((t - L0[1])*4) % 2 else "keeper"
    if name == "lb" and k == 3 and L0[3] < t < L0[3] + 2.8: return "run" if int(t*8) % 2 else "kick"
    if name == "lw" and k == 5: return "run" if int(t*6) % 2 else "kick"
    if name == "st" and k == 6:
        if t > WD.t(6, "célèbres") - .1: return "arms"
        if WD.t(6, "dixième") - .5 < t < WD.t(6, "dixième") + .1: return "kick"
    if name == "cm" and k == 4 and t > WD.t(4, "raison") - .1: return "arms"
    return p
def goal_ball(t):
    t0 = WD.t(6, "dixième") - .2; u = (t - t0)/.45
    if shot_at(t) != 6 or u < 0: return None
    u = min(1.0, u); return 1.8 + (2.6 - 1.8)*u, .2 + 1.4*u - .4*u*u, 37.2 + 15.6*u
def frame(fr):
    t = fr/FPS; k = shot_at(t); cam = cam_at(t); ex = []
    for i, name in enumerate(TEAM):
        x, z = player_pos(name, t); X, Y, Z = T.figure3d(pose_of(name, t), x, z, seed=10 + i, cam=cam); Y = Y*(1 + .015*math.sin(t*3 + i)) + .04*abs(math.sin(t*2.5 + i))
        hl = SHOTS[k][1] == name or (k == 8 and int((t - L0[8])*5) % 11 == i)
        ex.append((X, Y, Z, GOLD if hl else BLUE, 1.7 if hl else .9))
    for j, (bx, bz) in enumerate(BENCH):
        X, Y, Z = T.figure3d("wall", bx, bz, h=1.8, k=2000, seed=40 + j, cam=cam); hl = k == 7 and j == 1
        ex.append((X, Y, Z, GOLD if hl else T.rgb(150, 160, 190), 1.7 if hl else .7))
    t0 = L0[SHOTS[k][0]] - .35
    if 0 < k and t - t0 < .85 and SHOTS[k][1] not in (None, "all") and SHOTS[k - 1][1] not in (None, "all"):   # passe dorée d'un poste à l'autre
        u = (t - t0)/.85; a0 = focus(SHOTS[k - 1][1], t0); a1 = focus(SHOTS[k][1], t); g = np.random.default_rng(3)
        for j in range(6):
            uu = max(0, u - j*.03); bx, bz = a0[0] + (a1[0] - a0[0])*uu, a0[1] + (a1[1] - a0[1])*uu; by = .2 + 7*uu*(1 - uu)
            n = 300; r = .18*np.sqrt(g.random(n)); an = g.random(n)*6.283
            ex.append((bx + r*np.cos(an), by + r*np.sin(an), np.full(n, bz, np.float32), T.rgb(255, 230, 120) if j else T.rgb(255, 255, 255), 3.0*(1 - j/6)))
    ex += T.stadium_life(t)
    b = goal_ball(t)
    if b:
        g = np.random.default_rng(5); n = 500; r = .11*np.sqrt(g.random(n)); a = g.random(n)*6.283
        ex.append((b[0] + r*np.cos(a), b[1] + r*np.sin(a), np.full(n, b[2]), T.rgb(255, 255, 255), 2.5))
    s = SHOTS[k]; ta = L0[s[0]] + (.25 if k else .0)
    if t >= ta:                                                    # étiquette peinte qui « pousse » sur la pelouse
        anc, wd = label_geo(k, t); X, Y, Z = T.ground_text(s[3], T.Cam(*((shot_cam(k, t).pos, shot_cam(k, t).tgt))), anc, wd)
        ua = min(1.0, (t - ta)/.6); e = 1 - (1 - ua)**3; g = np.random.default_rng(77 + k); m = len(X)
        sx, sy, sz = X + g.normal(0, 6, m), g.uniform(2, 10, m), Z + g.normal(0, 6, m)     # les lettres se forment depuis le ciel
        Xa, Ya, Za = sx + (X - sx)*e, sy + (Y - sy)*e, sz + (Z - sz)*e
        ex.append((Xa, Ya + .05*np.sin(t*4 + X), Za, GOLD, (4.0 if k in (0, 8) else 1.6)*(.5 + .5*e)))
    if s[1] not in (None, "all") and t >= ta:                     # anneau lumineux au sol + gerbe de points dorés
        fx, fz = focus(s[1], t); a = np.linspace(0, 6.283, 900); rr = .9 + .08*math.sin(t*6)
        ex.append((fx + rr*np.cos(a), np.full(900, .03, np.float32), fz + rr*np.sin(a), GOLD, 2.5))
        tb = t - ta
        if tb < 1.2:
            g = np.random.default_rng(k); n = 700; v = g.uniform(2, 6, n); th = g.random(n)*6.283; up = g.uniform(3, 8, n)
            ex.append((fx + np.cos(th)*v*tb, np.maximum(0, up*tb - 4.9*tb*tb), fz + np.sin(th)*v*tb, np.array([GOLD, T.rgb(255, 255, 255), T.rgb(255, 120, 60)])[g.integers(0, 3, n)], 2.5*(1 - tb/1.2)))
    flash = 0.0
    if b and b[2] > 52: flash = max(0, 1 - (t - (WD.t(6, "dixième") + .25))*2.5)
    img = T.render(cam, ex, t, flash)
    return subtitle(img, t).tobytes()
_fz = {}
def fa(sz):
    if sz not in _fz: _fz[sz] = ImageFont.truetype(os.path.join(ROOT, "assets", "fonts", "Anton-Regular.ttf"), sz)
    return _fz[sz]
CH = WD.chunks(4)
def subtitle(img, t):
    cur = [c for c in CH if c[0] - .02 <= t < c[1]]
    if not cur: return img
    t0, t1, toks = cur[-1]; im = Image.fromarray(img).convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    words = [tk[1].upper().strip(".,;:!?…") for tk in toks]; ws = [fa(84).getlength(w) for w in words]; gap = 24; tot = sum(ws) + gap*(len(ws) - 1)
    sc = min(1.0, 960/tot); x = W/2 - tot*sc/2
    for tk, w, wd in zip(toks, words, ws):
        said = tk[3] <= t; key = KA.norm(tk[1]) in KEYS
        col = (255, 205, 80) if key else (245, 240, 228); a = 255 if said else 90
        pop = 1 + .16*math.exp(-(t - tk[3])*13) if said else 1.0
        d.text((x + wd*sc/2, 330), w, font=fa(max(10, int(84*sc*pop))), fill=col + (a,), anchor="mm", stroke_width=5, stroke_fill=(4, 6, 14, int(a*.85)))
        x += (wd + gap)*sc
    im.alpha_composite(ov); return np.asarray(im.convert("RGB"))
# ------------------------------------------------------------------ sons
def synth():
    n = int(TOTAL*SR); out = np.zeros(n, np.float32); g = np.random.default_rng(2)
    def add(sig, t0, gain=1.0):
        i = int(t0*SR); j = min(n, i + len(sig))
        if 0 <= i < n: out[i:j] += gain*sig[:j - i]
    def tone(f, d, dec): tt = np.arange(int(d*SR))/SR; return np.sin(2*np.pi*f*tt)*np.exp(-tt*dec)
    def noise(d, sm): x = g.standard_normal(int(d*SR)).astype(np.float32); return np.convolve(x, np.ones(sm)/sm, "same")
    amb = noise(TOTAL, 60); amb = amb*(.5 + .5*np.sin(np.arange(n)/SR*.7)**2); out += amb*.08                    # rumeur de stade
    tt = np.arange(int(.35*SR))/SR; add(np.sin(2*np.pi*(3100 + 180*np.sin(2*np.pi*28*tt))*tt)*np.minimum(1, (.35 - tt)*20)*.18, .02)   # coup de sifflet
    for k, s in enumerate(SHOTS[1:], 1):
        t0 = L0[s[0]] - .35; w = noise(.7, 30); add(w*np.sin(np.linspace(0, np.pi, len(w)))**2*.5, t0)              # vol de caméra
        add(tone(880, .4, 8)*.18 + tone(1320, .4, 9)*.12, L0[s[0]] + .25)                                            # l'étiquette se peint
    tg = WD.t(6, "dixième") + .25; add(noise(.25, 8)*np.exp(-np.arange(int(.25*SR))/SR*14)*.6, tg)                 # filet
    cr = noise(2.5, 20)*np.minimum(1, np.arange(int(2.5*SR))/SR*3)*np.exp(-np.arange(int(2.5*SR))/SR*.9); add(cr*.35, tg)   # clameur
    return out
def build_audio(path):
    sf = path + ".sfx.wav"; s = np.clip(synth(), -1, 1)
    with wave.open(sf, "wb") as w_: w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((s*32767).astype(np.int16).tobytes())
    fc = "[0:a]aresample=48000,adelay=0,apad=whole_dur=%.2f[v];[1:a]volume=0.6[s];[v][s]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.89[a]" % TOTAL
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", VOIX, "-i", sf, "-filter_complex", fc, "-map", "[a]", "-ac", "2", "-ar", "48000", path], check=True); os.remove(sf)
def main():
    out = os.path.join(ROOT, "output", "poste_perso"); os.makedirs(out, exist_ok=True); v, a = out + "/_v.mp4", out + "/_a.wav"; build_audio(a)
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-maxrate", "12M", "-bufsize", "24M", v], stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for b in pool.imap(frame, range(int(TOTAL*FPS)), chunksize=4): pr.stdin.write(b)
    pr.stdin.close(); pr.wait(); o = out + "/poste_perso.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", o], check=True); os.remove(v); os.remove(a); print(o, round(TOTAL, 2))
def stills(path):
    ts = [.3] + sum([[L0[s[0]] + .7, L0[s[0]] + 1.6] for s in SHOTS[1:]], []) + [TOTAL - .3]; w = 270; h = 480; cols = 6
    sh = Image.new("RGB", (w*cols, h*math.ceil(len(ts)/cols)))
    for j, t in enumerate(ts): sh.paste(Image.frombytes("RGB", (W, H), frame(int(t*FPS))).resize((w, h)), ((j % cols)*w, (j//cols)*h))
    sh.save(path, quality=88); print(path)
if __name__ == "__main__":
    if "--stills" in sys.argv: stills(sys.argv[sys.argv.index("--stills") + 1])
    else: main()
