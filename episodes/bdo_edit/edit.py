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

def read_frames(path, t0, dur, speed=1.0):
    """Extrait [t0, t0+dur*speed] en 1080x1920 : vidéo en plein cadre recadrée au centre (zoom léger) sur fond flou."""
    src_d = dur*speed
    cmd = ["ffmpeg", "-loglevel", "error", "-ss", f"{t0:.3f}", "-t", f"{src_d:.3f}", "-i", path, "-vf",
           f"setpts={1/speed:.4f}*PTS,fps={FPS},split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3,eq=brightness=-0.15[bg];"
           f"[b]scale=1080*1.35:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout; n = len(raw)//(W*H*3)
    fr = [Image.frombuffer("RGB", (W, H), raw[i*W*H*3:(i + 1)*W*H*3]) for i in range(n)]
    need = int(round(dur*FPS))
    while fr and len(fr) < need: fr.append(fr[-1])
    return fr[:need] if fr else [Image.new("RGB", (W, H), (10, 10, 14))]*need

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
    ap.add_argument("--out", default=os.path.join(ROOT, "output", "bdo_edit"))
    a = ap.parse_args(); col = tuple(int(v) for v in a.col.split(","))
    os.makedirs(a.out, exist_ok=True); slug = "bdo_edit_" + a.photo
    NB = 48; total = NB*BEAT + 1.2                                # 48 temps ≈ 22,3 s + queue
    # plan de coupe : (début_temps, nb_temps, vitesse)
    plan = [(1 + 2*k, 2, 1.0) for k in range(7)] + [(15, 1, .5)] + [(16 + k, 1, (1.0, 1.6, .6, 1.0)[k % 4]) for k in range(20)]
    segs = pick_segments(a.clips, len(plan), 2*BEAT*1.6)
    clipfr = {}
    for i, ((b0, nb, sp), t0) in enumerate(zip(plan, segs)): clipfr[b0] = read_frames(a.clips, t0, nb*BEAT, sp)
    stats = [s for s in a.stats.split("|") if s] or []
    sp_w = B.CUT(a.photo, 1250); name = a.name.upper()
    beats = [k*BEAT for k in range(NB + 4)]
    def on_beat(t, w=.12):
        k = round(t/BEAT); return max(0.0, 1 - abs(t - k*BEAT)/w) if k >= 1 else 0.0
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium", os.path.join(a.out, "_v.mp4")], stdin=subprocess.PIPE)
    for fr in range(int(total*FPS)):
        t = fr/FPS; bt = t/BEAT; pulse = on_beat(t)
        if bt < 1 or bt >= 36:                                     # ---------- HOOK et FIN : gagnant + aura
            L = Image.new("RGBA", (W, H), (0, 0, 0, 255)); end = bt >= 36; u = (t - 36*BEAT) if end else t
            B.dark_bg(L, t, col, "e"); B.rays(L, (W//2, 1000), t, .8, 18, 1900, tuple(int(c*.3) for c in col), .1, .3)
            B.glow_spot(L, W//2, 1150, 560, tuple(int(c*.5) for c in col))
            if end: B.put(L, B.gold_ball(150), W//2, 760 + 8*math.sin(t*3), B.M.spring(u, .45, 12), 0)
            B.aura(L, sp_w, W//2, 1990, t, col, 1.3, 3); B.put(L, sp_w, W//2, 1990, 1 + .03*pulse, 0)
            B.particles(L, W//2, 1990, 900, 1600, t, col, 40, 2); B.bolt(L, 260, 900, t, col, 1, 500); B.bolt(L, 820, 1000, t + .3, col, 2, 450)
            B.KW(name, B.GOLD, B.NOIR, 170).draw(L, fr, W//2, 330 if not end else 300, (1 + .5*(1 - min(1, u/.15))) if u < .15 else 1 + .04*pulse, -3)
            B.put(L, B.metal_text("BALLON D'OR 2026", 96), W//2, 500 if not end else 460, B.M.spring(u - .1, .3, 16), -3)
            if end and t > 40*BEAT: B.marker("ET TOI, T'AURAIS VOTÉ QUI ?", "ecta", 56).draw(L, fr, W//2, 1650, 1, -2)
            if end and u < .15: L.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255*(1 - u/.15)))))   # pas de flash à l'image 0 : le visage doit se voir tout de suite
            B.shock(L, t, 0 if not end else 36*BEAT, W//2, 1900, col, 1000)
            im = L.convert("RGB")
        else:                                                       # ---------- MONTAGE calé sur les temps
            b0 = max(k for k in clipfr if k <= bt); frames = clipfr[b0]; i = min(len(frames) - 1, int((t - b0*BEAT)*FPS))
            im = frames[i]; drop = bt >= 16; local = t - b0*BEAT
            z = 1 + (.12 if drop else .07)*math.exp(-local*9) + .02*pulse
            im = zoom(im, z, 12*math.sin(t*40)*pulse if drop else 0, 0)
            im = rgb_split(im, (14 if drop else 7)*math.exp(-local*14))
            L = im.convert("RGBA")
            if local < .07: L.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(170*(1 - local/.07)))))
            letterbox(L, 1 if not drop else .6)
            B.glow_spot(L, W//2, H, 700, tuple(int(c*.35) for c in col))
            if drop and stats:                                      # stats en surimpression sur le drop (une par 4 temps)
                k = int((bt - 16)//4) % len(stats); lu = (bt - 16) % 4
                if lu < 3.2: B.put(L, B.metal_text(stats[k], 100), W//2, 1500, B.M.spring(lu*BEAT, .25, 18), -4)
            if not drop: B.KW(name, B.GOLD, B.NOIR, 90).draw(L, fr, W//2, 260, 1, -3)
            else: B.put(L, B.metal_text(name, 120), W//2, 300, 1 + .05*pulse, -3)
            im = L.convert("RGB")
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    out = os.path.join(a.out, slug + ".mp4")
    # audio : musique signature (pleine) + clameur des extraits très bas (pas d'audio de diffuseur au premier plan)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(a.out, "_v.mp4"), "-i", MUSIC, "-filter_complex",
                    f"[1:a]atrim=0:{total:.2f},afade=t=out:st={total - 1.2:.2f}:d=1.2,loudnorm=I=-14:TP=-1[m]", "-map", "0:v", "-map", "[m]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    os.remove(os.path.join(a.out, "_v.mp4")); print(out)

if __name__ == "__main__": main()
