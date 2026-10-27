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
CLIPS = {i: E.read_frames(p["src"][0], p["src"][1], (b - a), 1.0) for i, (a, b, k, p) in enumerate(TL) if "src" in p}

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
    if kind == "hook":                                           # IMAGE 0 : visage ému de Kane + promesse
        bg(L, t, pulse)
        img = CLIPS[i][min(len(CLIPS[i]) - 1, int(u*FPS))]
        E.put_card(L, E.paper_card(img, RED, gloss=u/(6*BEAT)), W//2, 1080, -2 + 1.5*math.sin(t*2), 1.0 + .012*pulse)
        B.put(L, B.metal_text("BALLON D'OR 2026", 104), W//2, 300, 1 + .03*pulse, -3)
        B.KW("1er ANGLAIS DEPUIS 2001", B.ROUGE, B.BLANC, 76).draw(L, fr, W//2, 1720, 1 if u > .0 else 1, 2)
    elif kind == "champion":                                     # intro Smash : flash, explosion, silhouette, texte chromé, puis révélation
        if u < 2*BEAT:
            B.challenger(L, fr, t, a, "kane", RED)
            L2 = L                                               # texte remplacé : « HERE COMES THE CHAMPION! »
        else:
            bg(L, t, pulse, 1.3); sp = B.CUT("kane", 2000); v = u - 2*BEAT
            B.aura(L, sp, W//2, 2350, t, RED, 1.2, 1); B.put(L, sp, W//2, 2350, 1.0 + .02*pulse, 0)   # GROS PLAN : buste coupé en bas
            B.bolt(L, 160, 700, t, RED, 1, 520); B.bolt(L, 920, 820, t + .3, RED, 2, 480)
            B.put(L, B.metal_text(NAME, 130), W//2, 330, B.M.spring(v, .25, 18), -4)
            if v < .1: L.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255*(1 - v/.1)))))
    elif kind == "stat":                                         # motion design de stat : compteur chromé + Kane en buste à droite
        bg(L, t, pulse)
        sp = B.CUT("kane", 1500); B.aura(L, sp, 760, 2150, t, RED, .9, 2); B.put(L, sp, 760, 2150, 1, 0)
        n = min(p["count"], int(p["count"]*B.M.ease_out(min(1, u/(2*BEAT)))))
        B.put(L, counter_txt(n, 330), 330, 760, 1 + .06*pulse*(n == p["count"]), -6)
        B.KW(p["small"], B.BLANC, B.NOIR, 70 if len(p["small"]) < 8 else 52).draw(L, fr, 330, 990, B.M.spring(u - .2, .3, 16), -3)
        B.card(p["sub"], True, 54).draw(L, fr, W//2, 1640, B.M.spring(u - 2*BEAT, .3, 16), 2)
        if p.get("boot"): B.put(L, B.gold_ball(70), 160, 1250, 0, 0) if False else None
        B.shock(L, t, a + 2*BEAT, 330, 760, RED, 700)
        if u < .06: L.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(160*(1 - u/.06)))))
    elif kind == "treble":                                       # 3 trophées qui tombent sur les temps
        bg(L, t, pulse)
        B.put(L, B.metal_text("TRIPLÉ", 200), W//2, 420, 1 + .04*pulse, -4)
        for k, (lab, x) in enumerate((("BUNDESLIGA", 200), ("COUPE", W//2), ("SUPERCOUPE", 880))):
            tk = a + k*BEAT + .05
            if t >= tk:
                v = B.M.spring(t - tk, .35, 14); B.put(L, B.cup_gold(360), x, 1200, v, (-8, 0, 8)[k])
                B.tag(lab, 46, B.BLANC).draw(L, fr, x, 1360, v, (-3, 2, -2)[k]); B.shock(L, t, tk, x, 1200, (255, 200, 80), 380)
        B.KW("BUNDESLIGA · COUPE · SUPERCOUPE", B.NOIR, B.BLANC, 44).draw(L, fr, W//2, 1640, B.M.spring(u - 3*BEAT, .3, 16), 2)
    elif kind == "clip":                                         # BUT EN ENTIER, vitesse réelle, carte papier sur décor DA
        bg(L, t, pulse)
        if i > 0 and TL[i - 1][2] == "clip":
            pf = CLIPS[i - 1][-1]; E.put_card(L, E.paper_card(Image.eval(pf, lambda v: int(v*.5))), W//2 - 40, 1040, 7 if i % 2 else -7, .9)
        side = 1 if i % 2 else -1; e = B.M.ease_out(min(1, u/.3))
        img = CLIPS[i][min(len(CLIPS[i]) - 1, int(u*FPS))]
        if u < .1: img = E.rgb_split(img, 10*(1 - u/.1))
        E.put_card(L, E.paper_card(img, RED, gloss=u/(4*BEAT)), W//2 + side*(1 - e)*900, 1040, side*(1 - e)*22 + 1.6*math.sin(t*2), 1 + .01*pulse)
        if u < .06: L.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(150*(1 - u/.06)))))
        B.put(L, B.metal_text(NAME, 112), W//2, 290, 1 + .03*pulse, -3)
        if p.get("tag"): B.card(p["tag"], True, 54).draw(L, fr, W//2, 1720, B.M.spring(u - BEAT, .3, 16), -2)
    else:                                                        # FIN : Kane + trophée papier + CTA
        bg(L, t, pulse, 1.2); sp = B.CUT("kane", 1500)
        B.put(L, B.gold_ball(110), W//2, 590 + 8*math.sin(t*3), B.M.spring(u, .45, 12), 0)
        B.aura(L, sp, W//2, 2150, t, RED, 1.2, 4); B.put(L, sp, W//2, 2150, 1, 0)
        B.bolt(L, 200, 900, t, RED, 5, 450); B.bolt(L, 880, 1000, t + .4, RED, 6, 450)
        B.put(L, B.metal_text(NAME, 120), W//2, 210, 1, -3); B.put(L, B.metal_text("BALLON D'OR 2026", 84), W//2, 330, 1, -3)
        if u > 3*BEAT: B.marker("MÉRITÉ ? OUI OU NON ?", "kcta", 60).draw(L, fr, W//2, 1700, B.M.spring(u - 3*BEAT, .3, 16), -2)
        if u < .1: L.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255*(1 - u/.1)))))
    return L.convert("RGB")

# « HERE COMES THE CHAMPION! » : on adapte le texte de l'intro Smash
_orig = B.metal_text
def _metal(txt, size, *a, **k):
    if txt == "HERE COMES A": txt = "HERE COMES THE"
    if txt == "NEW CHALLENGER!": txt = "CHAMPION!"; size = int(size*1.25)
    return _orig(txt, size, *a, **k)
B.metal_text = _metal

def main():
    os.makedirs(OUT, exist_ok=True); v = os.path.join(OUT, "_v.mp4")
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium", v], stdin=subprocess.PIPE)
    for fr in range(int(TOTAL*FPS)): pr.stdin.write(frame(fr, fr/FPS).tobytes())
    pr.stdin.close(); pr.wait(); out = os.path.join(OUT, "bdo_kane.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", E.MUSIC, "-filter_complex",
                    f"[1:a]atrim=0:{TOTAL:.2f},afade=t=out:st={TOTAL - 1.5:.2f}:d=1.5,loudnorm=I=-14:TP=-1[m]", "-map", "0:v", "-map", "[m]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    os.remove(v); print(out)
def stills():
    ts = [0, .5, 1.5, 3.0, 3.5, 4.2, 5.0, 6.0, 7.0, 8.0, 10, 14, 18, 22, 26, 30, 33, 36, 39, 41]
    sh = Image.new("RGB", (216*10, 384*2))
    for k, t in enumerate(ts): sh.paste(frame(int(t*FPS), t).resize((216, 384)), ((k % 10)*216, (k//10)*384))
    p = "/tmp/claude-0/kane_sheet.jpg"; sh.save(p, quality=85); print(p, TOTAL)
if __name__ == "__main__": stills() if "--stills" in sys.argv else main()
