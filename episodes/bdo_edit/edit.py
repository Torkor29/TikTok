"""ÉDIT « [NOM] BALLON D'OR » : montage dynamique calé sur la musique signature (phonk 129 BPM).
Entrées : une compile de buts (mp4) + le gagnant (photo réaliste, couleur d'aura, logo club).
  python3 episodes/bdo_edit/edit.py --name DEMBÉLÉ --photo dembele --club psg --col 90,140,255 --clips compile.mp4
Structure (~22 s = 12 mesures de 4 temps à 129 BPM) :
  0 → 1 temps   : HOOK, image 0 = visage du gagnant + aura + « [NOM] » + « BALLON D'OR 2026 » (flash, onde de choc)
  1 → 16 temps  : coupes toutes les 2 temps (zoom punch, flash, aberration chromatique, secousse sur chaque temps)
  16 → 36 temps : DROP, coupes à chaque temps, ralentis/accélérations, stats en surimpression
  36 → fin      : gagnant + trophée papier 3D + aura + « BALLON D'OR 2026 » + CTA commentaire
Les extraits sont choisis automatiquement dans la compile sur les pics de bruit (clameur = but)."""
import sys, os, math, argparse, subprocess, json, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "bdo_favoris"))
sys.argv_saved = sys.argv; sys.argv = [sys.argv[0], "--noop"]
import bdo_favoris as B                                     # réutilise : CUT (photo réaliste), aura, glow, bolt, particles, gold_ball, KW, metal_text…
sys.argv = sys.argv_saved
from PIL import Image, ImageDraw, ImageFilter, ImageChops
W, H, FPS = 1080, 1920, 30
BPM = 129.0; BEAT = 60/BPM
MUSIC = os.path.join(ROOT, "assets", "music", "phonk_papierfc.mp3")
CW, CH = 840, 1050                                            # extrait = carte papier 4:5
_cm = {}
def card_mask():
    """Bord papier déchiré (cadre blanc 34 px) + masque de la photo, mis en cache."""
    if "m" not in _cm:
        bw = 34; w_, h_ = CW + 2*bw, CH + 2*bw; rng = np.random.default_rng(5)
        m = Image.new("L", (w_ + 40, h_ + 40), 0); d = ImageDraw.Draw(m); pts = []
        for x in range(0, w_ + 1, 14): pts.append((20 + x, 20 + rng.uniform(-6, 6)))
        for y in range(0, h_ + 1, 14): pts.append((20 + w_ + rng.uniform(-6, 6), 20 + y))
        for x in range(w_, -1, -14): pts.append((20 + x, 20 + h_ + rng.uniform(-6, 6)))
        for y in range(h_, -1, -14): pts.append((20 + rng.uniform(-6, 6), 20 + y))
        d.polygon(pts, fill=255); _cm["m"] = m.filter(ImageFilter.GaussianBlur(.8)); _cm["off"] = (20 + bw, 20 + bw)
        sh = m.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v*.6)); _cm["sh"] = sh
        tape = Image.new("RGBA", (220, 70), (238, 226, 190, 200)); td = ImageDraw.Draw(tape)
        for k in range(0, 220, 9): td.line([(k, 0), (k + 4, 70)], fill=(225, 210, 170, 200), width=2)
        _cm["tape"] = tape
    return _cm
def paper_card(img, glow_col=None, gloss=0.0):
    """Extrait -> carte papier : bord blanc déchiré, 2 morceaux de scotch, reflet brillant qui balaie (gloss 0..1)."""
    c = card_mask(); m = c["m"]; out = Image.new("RGBA", m.size, (0, 0, 0, 0))
    paper = Image.new("RGBA", m.size, (250, 247, 238, 255)); paper.putalpha(m); out.alpha_composite(paper)
    out.paste(img, c["off"])
    if 0 < gloss < 1:                                          # reflet diagonal
        g = Image.new("L", (CW, CH), 0); gd = ImageDraw.Draw(g); x = -300 + (CW + 600)*gloss
        gd.polygon([(x, 0), (x + 120, 0), (x - 260, CH), (x - 380, CH)], fill=90); g = g.filter(ImageFilter.GaussianBlur(18))
        out.paste((255, 255, 255), (c["off"][0], c["off"][1], c["off"][0] + CW, c["off"][1] + CH), g)
    t1 = c["tape"].rotate(-28, expand=True); t2 = c["tape"].rotate(24, expand=True)
    out.alpha_composite(t1, (-20, -10)); out.alpha_composite(t2, (m.width - t2.width + 20, -10))
    return out
def put_card(L, card, x, y, rot, s, shadow=True):
    c = card_mask()
    if s != 1: card = card.resize((int(card.width*s), int(card.height*s)), Image.BILINEAR)
    card = card.rotate(rot, resample=Image.BICUBIC, expand=True)
    if shadow:
        sh = c["sh"].resize((int(c["sh"].width*s), int(c["sh"].height*s))).rotate(rot, expand=True)
        L.paste((0, 0, 0), (int(x - sh.width/2 + 18), int(y - sh.height/2 + 30)), sh)
    L.alpha_composite(card, (int(x - card.width/2), int(y - card.height/2)))

def pick_segments(path, n, seg_len, skip=1.0):
    """Repère les n pics de clameur (RMS par 0,1 s) espacés d'au moins 4 s ; renvoie les débuts d'extraits (avant le pic)."""
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", "8000", "-f", "f32le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32); step = 800
    rms = np.array([np.sqrt(np.mean(a[i:i + step]**2)) for i in range(0, len(a) - step, step)])
    dur = len(a)/8000
    if len(rms) < 20: return [i*dur/n for i in range(n)]
    sm = np.convolve(rms, np.ones(15)/15, "same"); order = np.argsort(sm)[::-1]; picks = []
    for i in order:
        t = i*.1
        if t < skip + seg_len or t > dur - 1: continue
        if all(abs(t - p) > 4 for p in picks): picks.append(t)
        if len(picks) >= n: break
    while len(picks) < n: picks.append(random.uniform(skip, max(skip + .1, dur - seg_len - 1)))
    return sorted(max(0, p - seg_len*.75) for p in picks)

def _aspect(path):
    w, h = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
                          capture_output=True, text=True).stdout.strip().split(",")[:2]
    return int(w)/int(h)
def read_frames(path, t0, dur, speed=1.0):
    """Extrait [t0, t0+dur*speed] en 1080x1920 : vidéo en plein cadre recadrée au centre (zoom léger) sur fond flou."""
    src_d = dur*speed
    if True:                                                  # extrait recadré en CARTE 4:5 (posée dans la DA, jamais plein écran)
        vf = f"setpts={1/speed:.4f}*PTS,fps={FPS},scale={CW}*1.15:{CH}*1.15:force_original_aspect_ratio=increase,crop={CW}:{CH},eq=contrast=1.08:saturation=1.15"
        cmd = ["ffmpeg", "-loglevel", "error", "-ss", f"{t0:.3f}", "-t", f"{src_d:.3f}", "-i", path, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    else: cmd = ["ffmpeg", "-loglevel", "error", "-ss", f"{t0:.3f}", "-t", f"{src_d:.3f}", "-i", path, "-vf",
           f"setpts={1/speed:.4f}*PTS,fps={FPS},split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3,eq=brightness=-0.15[bg];"
           f"[b]scale=1080*1.35:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout; n = len(raw)//(CW*CH*3)
    fr = [Image.frombuffer("RGB", (CW, CH), raw[i*CW*CH*3:(i + 1)*CW*CH*3]) for i in range(n)]
    need = int(round(dur*FPS))
    while fr and len(fr) < need: fr.append(fr[-1])
    return fr[:need] if fr else [Image.new("RGB", (CW, CH), (10, 10, 14))]*need

def rgb_split(im, px):
    if px < 1: return im
    r, g, b = im.split(); return Image.merge("RGB", (ImageChops.offset(r, int(px), 0), g, ImageChops.offset(b, -int(px), 0)))
def zoom(im, z, dx=0, dy=0):
    if abs(z - 1) < .005 and not dx and not dy: return im
    w, h = W/z, H/z; x0, y0 = (W - w)/2 + dx, (H - h)/2 + dy
    return im.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.BILINEAR)
def letterbox(L, a):
    if a <= 0: return
    d = ImageDraw.Draw(L); h = int(150*a); d.rectangle([0, 0, W, h], fill=(0, 0, 0)); d.rectangle([0, H - h, W, H], fill=(0, 0, 0))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True); ap.add_argument("--photo", required=True); ap.add_argument("--club", required=True)
    ap.add_argument("--col", default="255,200,60"); ap.add_argument("--clips", required=True)
    ap.add_argument("--stats", default="", help="3 stats séparées par | ex. « 35 BUTS|16 PASSES D|CHAMPION D'EUROPE »")
    ap.add_argument("--plan", default="", help="JSON : [[n°_compile, début_s, nb_temps, stat_ou_vide], …] — séquences de buts ENTIÈRES choisies à la main")
    ap.add_argument("--out", default=os.path.join(ROOT, "output", "bdo_edit"))
    a = ap.parse_args(); col = tuple(int(v) for v in a.col.split(","))
    os.makedirs(a.out, exist_ok=True); slug = "bdo_edit_" + a.photo
    NB = 48
    paths = a.clips.split(","); clipfr = {}; segstat = {}
    if a.plan:                                                   # montage « vrai » : chaque but montré EN ENTIER, vitesse réelle
        plan = json.load(open(a.plan)); b0 = 2
        for (ci, t0, nb, st) in plan:
            clipfr[b0] = read_frames(paths[ci], t0, nb*BEAT, 1.0); segstat[b0] = st; b0 += nb
        END0 = b0
    else:
        plan = [(1 + 2*k, 2, 1.0) for k in range(7)] + [(15, 1, .5)] + [(16 + k, 1, (1.0, 1.6, .6, 1.0)[k % 4]) for k in range(20)]
        durs = [float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", q], capture_output=True, text=True).stdout) for q in paths]
        share = [max(1, round(len(plan)*d/sum(durs))) for d in durs]; share[0] += len(plan) - sum(share)
        segs = []
        for q, k in zip(paths, share): segs += [(q, t0) for t0 in pick_segments(q, k, 2*BEAT*1.6)]
        random.Random(7).shuffle(segs)
        for (b0, nb, sp), (q, t0) in zip(plan, segs): clipfr[b0] = read_frames(q, t0, nb*BEAT, sp)
        END0 = 36
    NB = END0 + 10; total = NB*BEAT + 1.2
    stats = [s for s in a.stats.split("|") if s] or []
    sp_w = B.CUT(a.photo, 1250); name = a.name.upper()
    beats = [k*BEAT for k in range(NB + 4)]
    def on_beat(t, w=.12):
        k = round(t/BEAT); return max(0.0, 1 - abs(t - k*BEAT)/w) if k >= 1 else 0.0
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium", os.path.join(a.out, "_v.mp4")], stdin=subprocess.PIPE)
    for fr in range(int(total*FPS)):
        t = fr/FPS; bt = t/BEAT; pulse = on_beat(t)
        if bt < (2 if a.plan else 1) or bt >= END0:                                     # ---------- HOOK et FIN : gagnant + aura
            L = Image.new("RGBA", (W, H), (0, 0, 0, 255)); end = bt >= END0; u = (t - END0*BEAT) if end else t
            B.dark_bg(L, t, col, "e"); B.rays(L, (W//2, 1000), t, .8, 18, 1900, tuple(int(c*.3) for c in col), .1, .3)
            B.glow_spot(L, W//2, 1150, 560, tuple(int(c*.5) for c in col))
            if end: B.put(L, B.gold_ball(150), W//2, 760 + 8*math.sin(t*3), B.M.spring(u, .45, 12), 0)
            B.aura(L, sp_w, W//2, 1990, t, col, 1.3, 3); B.put(L, sp_w, W//2, 1990, 1 + .03*pulse, 0)
            B.particles(L, W//2, 1990, 900, 1600, t, col, 40, 2); B.bolt(L, 260, 900, t, col, 1, 500); B.bolt(L, 820, 1000, t + .3, col, 2, 450)
            B.KW(name, B.GOLD, B.NOIR, 170).draw(L, fr, W//2, 330 if not end else 300, (1 + .5*(1 - min(1, u/.15))) if u < .15 else 1 + .04*pulse, -3)
            B.put(L, B.metal_text("BALLON D'OR 2026", 96), W//2, 500 if not end else 460, (1 if not end else B.M.spring(u - .1, .3, 16)), -3)
            if end and t > (END0 + 4)*BEAT: B.marker("ET TOI, T'AURAIS VOTÉ QUI ?", "ecta", 56).draw(L, fr, W//2, 1650, 1, -2)
            if end and u < .15: L.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255*(1 - u/.15)))))   # pas de flash à l'image 0 : le visage doit se voir tout de suite
            B.shock(L, t, 0 if not end else END0*BEAT, W//2, 1900, col, 1000)
            im = L.convert("RGB")
        else:                                                       # ---------- MONTAGE : cartes papier sur décor DA
            keys = sorted(k for k in clipfr if k <= bt); b0 = keys[-1]; frames = clipfr[b0]
            i = min(len(frames) - 1, int((t - b0*BEAT)*FPS)); drop = (bt >= 16) and not a.plan; local = t - b0*BEAT
            L = Image.new("RGBA", (W, H), (0, 0, 0, 255))
            B.dark_bg(L, t, col, "ed"); B.rays(L, (W//2, 1000), t*(1.6 if drop else 1), .7, 18, 1900, tuple(int(c*.28) for c in col), .1, .3)
            B.glow_spot(L, W//2, 1020, 640, tuple(int(c*(.55 + .25*pulse)) for c in col))
            B.particles(L, W//2, 1950, W, 1800, t, col, 28 if drop else 16, 5)
            # carte précédente en dessous (pile), légèrement tournée et assombrie
            if len(keys) > 1:
                pf = clipfr[keys[-2]][-1]; pc = paper_card(Image.eval(pf, lambda v: int(v*.55)))
                put_card(L, pc, W//2 - 40, 1040, 7 if keys[-2] % 2 else -7, .9)
            # carte courante : entrée en « whip » depuis le côté sur le temps, puis petite oscillation + punch sur chaque temps
            side = 1 if b0 % 2 else -1; e = B.M.ease_out(min(1, local/(.3 if a.plan else .16)))
            x = W//2 + side*(1 - e)*900; rot = side*(1 - e)*25 + 2.2*math.sin(t*2.3 + b0) * (.4 if drop else 1)
            sc = (1.06 if drop else 1.0)*(1 + .05*math.exp(-local*10)) + (.012 if a.plan else .025)*pulse
            img = frames[i]
            if local < .1: img = rgb_split(img, 10*(1 - local/.1))
            card = paper_card(img, col, gloss=(local/(3*BEAT)) if not drop else 0)
            B.aura(L, card, x, 1040 + card.height/2, t, col, .55 + .5*pulse, b0) if False else None
            B.glow_spot(L, x, 1040, 600, tuple(int(c*.35*(1 + pulse)) for c in col))
            put_card(L, card, x, 1040, rot, sc)
            if local < .06: L.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(150*(1 - local/.06)))))
            # textes : nom chromé en haut, stats en tampon papier en bas (drop)
            B.put(L, B.metal_text(name, 128), W//2, 300, 1 + .05*pulse, -3)
            if not drop and local > 0: B.KW("BALLON D'OR 2026", B.GOLD, B.NOIR, 64).draw(L, fr, W//2, 440, 1, 2)
            st = segstat.get(b0, "")
            if st and local > 2*BEAT: B.card(st, True, 66).draw(L, fr, W//2, 1720, B.M.spring(local - 2*BEAT, .3, 16), -3)
            if drop and stats:
                k = int((bt - 16)//4) % len(stats); lu = (bt - 16) % 4
                if lu < 3.3: B.card(stats[k], True, 70).draw(L, fr, W//2, 1720, B.M.spring(lu*BEAT, .25, 18), (-4, 3, -2)[k % 3])
            if drop: B.bolt(L, 150, 700, t, col, b0, 520, .9); B.bolt(L, 930, 1300, t + .21, col, b0 + 3, 480, .9)
            im = L.convert("RGB")
            if drop and pulse > .5: im = zoom(im, 1 + .03*pulse, 10*math.sin(t*50), 0)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    out = os.path.join(a.out, slug + ".mp4")
    # audio : musique signature (pleine) + clameur des extraits très bas (pas d'audio de diffuseur au premier plan)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(a.out, "_v.mp4"), "-i", MUSIC, "-filter_complex",
                    f"[1:a]atrim=0:{total:.2f},afade=t=out:st={total - 1.2:.2f}:d=1.2,loudnorm=I=-14:TP=-1[m]", "-map", "0:v", "-map", "[m]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    os.remove(os.path.join(a.out, "_v.mp4")); print(out)

if __name__ == "__main__": main()
