"""pixel.fc v2 — storytime Rabiot en VRAI pixel-art (engine/pixelart.py), même voix que episodes/rabiot (0 crédit).
Gros sous-titres en haut (mots-clés en couleur), en-tête d'épisode, une scène par phrase, transitions en glissé de pixels.
  python3 episodes/rabiot_px/rabiot_px.py [--stills]"""
import sys, os, math, subprocess
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import pixelart as P
import karaoke as KA
from PIL import Image, ImageDraw
import numpy as np
FPS = 30
TEXTE = [l.strip() for l in open(os.path.join(ROOT, "episodes", "rabiot", "TEXTE_VOIX.txt")) if l.strip()]
VOIX = os.path.join(ROOT, "episodes", "rabiot", "voix", "voix.mp3")
WD = KA.Words(TEXTE, VOIX)
def k(i, w, n=1): return WD.t(i, w, n)
L0 = [WD.line(i)[0] - (.1 if i else 0) for i in range(len(TEXTE))]; TOTAL = WD.end + 1.2
RED, YEL, GRN, SKY, WHITE = (255, 76, 90), (255, 214, 64), (90, 220, 120), (90, 200, 255), (255, 255, 255)
EMPH = {KA.norm(w): c for w, c in (("PSG", (120, 150, 255)), ("OM", SKY), ("mal", RED), ("terminé", RED), ("dix-sept", YEL), ("mère", YEL), ("Véronique", YEL),
        ("retenu", RED), ("réserviste", YEL), ("refuse", RED), ("mail", YEL), ("prolonger", RED), ("six", RED), ("libre", GRN), ("Juventus", WHITE),
        ("euro", RED), ("Marseille", SKY), ("traître", RED), ("patron", GRN), ("bagarre", RED), ("vestiaire", YEL), ("écart", RED), ("Milan", RED),
        ("incompris", GRN), ("commentaire", YEL))}
RAB = dict(skin=1, hair=2, hstyle="long")                         # cheveux longs + bandeau
def rab(kit, pose="stand", back=False, mood="happy", frame=0): return P.person(kit, RAB["skin"], RAB["hair"], RAB["hstyle"], pose, back, 25, frame, mood)
def pop(t, t0, d=.18): return 0 if t < t0 else min(1, (t - t0)/d)
# ------------------------------------------------------------------ scènes (L : canevas 135×240, t : temps voix)
def s0(L, t):                                                      # formé au PSG… fini à l'OM
    om = t > k(0, "OM") - .1
    L.paste((30, 44, 110, 255), (0, 0, 68, 240)); L.paste((40, 170, 225, 255), (67, 0, 135, 240)) if om else L.paste((30, 44, 110, 255), (67, 0, 135, 240))
    P.crowd(L, t, 96, 150, [(30, 44, 110), (214, 36, 48), (250, 250, 246)] if not om else [(40, 170, 225), (250, 250, 246)], .6 if om else .2, 4)
    P.pitch(L, 158)
    P.plabel(L, "PSG", 34, 86, (250, 250, 246), (30, 44, 110), (214, 36, 48)); P.plabel(L, "OM", 101, 86, (30, 44, 110), (250, 250, 246), (40, 170, 225)) if om else None
    x = 67 if not om else 67 + int(14*math.sin(min(1, (t - k(0, "OM") + .1)/.3)*math.pi))
    P.shadow(L, 67, 226, 26); P.blit(L, rab("om" if om else "psg", "cheer" if om and t < k(0, "mal") else "stand", mood="sad" if t > k(0, "mal") else "happy"), x, 228, 2)
def s1(L, t):                                                      # débute au PSG à 17 ans, sa mère agent
    P.stadium(L, t, [(30, 44, 110), (214, 36, 48), (250, 250, 246)], .3 if t > k(1, "dix") else 0, seed=7)
    if t < k(1, "agent") - .1:
        P.shadow(L, 67, 216, 20); P.blit(L, rab("psg", "cheer" if t > k(1, "dix") else "walk", frame=int(t*6)), 67, 218, 2)
        if t > k(1, "dix"): P.plabel(L, "17 ANS", 100, 140, (18, 22, 40), (255, 214, 64), None, 16, "Silkscreen-Bold.ttf")
    else:
        P.blit(L, rab("psg"), 40, 218, 2); P.blit(L, P.person("suit", 1, 3, "longf", "stand", gender="f"), 96, 218, 2)
        if t > k(1, "mère") - .1: P.paper_doc(L, 98, 140, "CONTRAT", 3, 48, 52, ("AGENT", (200, 40, 50)) if t > k(1, "Véronique") else None)
def s2(L, t):                                                      # 2018, pas retenu pour la Coupe du monde
    P.room(L, (40, 46, 80), (70, 60, 70), 186, False)
    P.paper_doc(L, 67, 118, "LISTE DES 23", 7, 84, 110, ("PAS RETENU", (200, 40, 50)) if t > k(2, "retenu") - .05 else None, head=(30, 44, 120))
    P.blit(L, rab("france", mood="sad" if t > k(2, "retenu") else "happy"), 67, 236, 2)
    if t < k(2, "retenu"): P.plabel(L, "2018", 67, 186, (255, 214, 64), (18, 22, 40), None, 16, "Silkscreen-Bold.ttf")
def s3(L, t):                                                      # réserviste ? il refuse… par mail
    P.room(L, (52, 44, 70), (110, 74, 50), 176, True, t)
    d = ImageDraw.Draw(L); d.rectangle([20, 150, 115, 156], fill=(130, 90, 60)); d.rectangle([24, 156, 27, 176], fill=(100, 70, 46)); d.rectangle([108, 156, 111, 176], fill=(100, 70, 46))
    P.laptop(L, 67, 150, 1.0 if int(t*4) % 2 else .9); P.blit(L, rab("training", back=True), 67, 214, 2)
    if t > k(3, "réserviste") - .1: P.plabel(L, "RÉSERVISTE ?", 67, 74, (18, 22, 40), (255, 214, 64), None, 8, "Silkscreen-Bold.ttf")
    tm = k(3, "mail") - .25
    if t > tm:
        u = min(1, (t - tm)/.7); P.envelope(L, int(67 + 60*u), int(128 - 70*math.sin(u*math.pi*.9)))
        if u >= 1: P.plabel(L, "ENVOYÉ : NON MERCI", 67, 92, (250, 250, 246), (200, 40, 50), None)
def s4(L, t):                                                      # refuse de prolonger : six mois sans jouer
    P.stadium(L, t, [(30, 44, 110), (214, 36, 48), (250, 250, 246)], 0, seed=9)
    P.bench(L, 67, 200, 90); P.blit(L, rab("psg", mood="sad"), 40, 212, 2)
    if t < k(4, "Résultat"): P.paper_doc(L, 98, 150, "PROLONGATION", 3, 60, 46, ("REFUSÉ", (200, 40, 50)) if t > k(4, "prolonger") else None)
    else:
        n = min(6, 1 + int((t - k(4, "six") + .1)/.12)) if t > k(4, "six") - .1 else 0
        if n: P.plabel(L, f"{n} MOIS SANS JOUER", 67, 150, (250, 250, 246), (200, 40, 50), None)
def s5(L, t):                                                      # 2019 : libre à la Juventus, 0 €
    P.stadium(L, t, [(250, 250, 246), (30, 28, 32)], .3, sky=((16, 16, 20), (60, 60, 70)), seed=11)
    juve = t > k(5, "Juventus") - .1
    P.shadow(L, 67, 216, 20); P.blit(L, rab("juve" if juve else "psg", "cheer" if juve else "walk", frame=int(t*6)), 67, 218, 2)
    if t > k(5, "libre") - .05: P.plabel(L, "LIBRE", 34, 140, (18, 22, 40), (90, 220, 120), None, 16, "Silkscreen-Bold.ttf")
    if t > k(5, "euro") - .3: P.plabel(L, "0 €", 104, 140, (250, 250, 246), (200, 40, 50), None, 16, "Silkscreen-Bold.ttf")
def s6(L, t):                                                      # cinq ans plus tard : Marseille
    om = t > k(6, "Marseille") - .1
    P.stadium(L, t, [(40, 170, 225), (250, 250, 246)], .9 if om else .2, sky=((20, 40, 80), (90, 150, 210)), seed=13)
    P.shadow(L, 67, 216, 20); P.blit(L, rab("om" if om else "juve", "cheer" if om else "walk", frame=int(t*6)), 67, 218, 2)
    if not om: P.plabel(L, "5 ANS PLUS TARD", 67, 140, (250, 250, 246), (18, 22, 40), None)
    else:
        for j in range(6): P.sparkle(L, 20 + j*19, 130 + (j % 2)*8, t + j*.2)
def s7(L, t):                                                      # traître pour Paris, patron pour Marseille
    P.card(L, 36, 140, 0, "PARIS", "psg", (60, 70, 140), RAB["skin"], RAB["hair"], RAB["hstyle"], s=1) if False else None
    L.paste((26, 34, 80, 255), (0, 0, 68, 240)); L.paste((30, 120, 180, 255), (67, 0, 135, 240))
    P.crowd(L, t, 60, 120, [(30, 44, 110), (214, 36, 48)], 0, 21); P.crowd(L, t, 60, 120, [(40, 170, 225), (250, 250, 246)], .9, 22)
    L.paste((26, 34, 80, 255), (0, 128, 68, 240)); L.paste((30, 120, 180, 255), (67, 128, 135, 240))
    P.blit(L, rab("om", mood="sad"), 34, 220, 2); P.blit(L, rab("om", "cheer"), 101, 220, 2)
    if t > k(7, "traître") - .05: P.plabel(L, "TRAÎTRE", 34, 140, (250, 250, 246), (200, 40, 50), None, 8, "Silkscreen-Bold.ttf")
    if t > k(7, "patron") - .05: P.plabel(L, "PATRON", 101, 140, (18, 22, 40), (90, 220, 120), None, 8, "Silkscreen-Bold.ttf")
def s8(L, t):                                                      # août 2025, Rennes : bagarre dans le vestiaire
    P.lockers(L)
    if t < k(8, "bagarre") - .1:
        P.blit(L, rab("om", mood="angry"), 44, 228, 2); P.blit(L, P.person("om", 3, 0, "short", "stand", mood="angry"), 92, 228, 2)
        P.plabel(L, "AOÛT 2025 · RENNES", 67, 80, (250, 250, 246), (18, 22, 40), None)
    else: P.dust_cloud(L, 67, 190, t, 30); P.plabel(L, "BAGARRE !", 67, 80, (250, 250, 246), (200, 40, 50), None, 16, "Silkscreen-Bold.ttf")
def s9(L, t):                                                      # mis à l'écart, vendu au Milan AC
    P.night_city(L, t, 5, 184)
    milan = t > k(9, "Milan") - .1; x = 30 + int(70*min(1, max(0, (t - k(9, "vend"))/1.2)))
    P.blit(L, rab("milan" if milan else "om", "walk", frame=int(t*6)), x, 214, 2)
    if t > k(9, "écart") - .05: P.plabel(L, "À L'ÉCART", 67, 80, (250, 250, 246), (200, 40, 50), None)
    if milan: P.plabel(L, "MILAN AC", 67, 98, (250, 250, 246), (30, 28, 32), (206, 24, 36))
def s10(L, t):                                                     # traître ou incompris ?
    P.fill(L, (22, 34, 92)); d = ImageDraw.Draw(L)
    for y in range(0, 240, 8):
        for x in range((y//8) % 2*8, 135, 16): d.rectangle([x, y, x + 7, y + 7], fill=(26, 40, 104))
    if t > k(10, "traître") - .05: P.card(L, 38, 120, 51, "TRAÎTRE", "om", (210, 50, 60), RAB["skin"], RAB["hair"], RAB["hstyle"], 25)
    if t > k(10, "incompris") - .05: P.card(L, 97, 120, 49, "INCOMPRIS", "om", (60, 170, 90), RAB["skin"], RAB["hair"], RAB["hstyle"], 25)
    if t > k(10, "Dis") - .05:
        d.rectangle([12, 170, 122, 184], fill=(14, 18, 40)); d.rectangle([12, 170, 122, 184], outline=(120, 130, 200))
        txt = "TRAÎTRE"[:max(1, int((t - k(10, "Dis"))*8))]; P.ptext(L, txt + ("|" if int(t*3) % 2 else ""), 18, 177, (250, 250, 246), 8, anchor="lm")
SC = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
def scene(i, t):
    L = Image.new("RGBA", (P.LW, P.LH), (0, 0, 0, 255)); SC[i](L, t); return L
def frame(fr):
    t = fr/FPS; i = max(j for j, s in enumerate(L0) if s <= t) if t >= L0[0] else 0; L = scene(i, t)
    u = (t - L0[i])/.2 if i else 1
    if u < 1:                                                      # glissé : la nouvelle scène pousse l'ancienne, par pas de 1 gros pixel
        prev = scene(i - 1, t); off = int(P.LW*(1 - (1 - u)**2)); out = Image.new("RGBA", L.size)
        out.paste(prev, (-off, 0)); out.paste(L, (P.LW - off, 0)); L = out
    im = P.upscale(L).convert("RGBA")
    P.header(im, "LES HISTOIRES ·", "RABIOT", 110)
    P.caption_top(im, WD, t, 210, EMPH, 100)
    return np.asarray(im.convert("RGB")).tobytes()
def build_audio(wav):
    A = os.path.join(ROOT, "assets", "sfx"); evs = [(VOIX, 0.0, 1.0)]
    for t0 in L0[1:]: evs.append((os.path.join(A, "whoosh.mp3"), t0, .2))
    for (i, w, n) in ((0, "mal", "stamp"), (2, "retenu", "stamp"), (3, "mail", "notif"), (4, "prolonger", "stamp"), (5, "euro", "cash"), (6, "Marseille", "crowd"),
                      (7, "traître", "boo"), (8, "bagarre", "crash"), (9, "Milan", "stamp"), (10, "Dis", "notif")):
        evs.append((os.path.join(A, n + ".mp3"), k(i, w), .25))
    ins = ["-f", "lavfi", "-t", f"{TOTAL:.2f}", "-i", "anullsrc=r=48000:cl=stereo"] + sum([["-i", p] for p, _, _ in evs], []); fc = ""
    for j, (_, ts, g) in enumerate(evs): fc += f"[{j + 1}:a]aresample=48000,adelay={int(ts*1000)}|{int(ts*1000)},volume={g}[e{j}];"
    fc += "[0:a]" + "".join(f"[e{j}]" for j in range(len(evs))) + f"amix=inputs={1 + len(evs)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.89[a]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-filter_complex", fc, "-map", "[a]", "-ar", "48000", wav], check=True)
def main():
    out = os.path.join(ROOT, "output", "rabiot_px"); os.makedirs(out, exist_ok=True); v, a = out + "/_v.mp4", out + "/_a.wav"; build_audio(a)
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{P.W}x{P.H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", v], stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for b in pool.imap(frame, range(int(TOTAL*FPS)), chunksize=8): pr.stdin.write(b)
    pr.stdin.close(); pr.wait(); o = out + "/rabiot_px.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", o], check=True); os.remove(v); os.remove(a); print(o, round(TOTAL, 2))
def stills():
    ts = [0.05] + [L0[i] + (L0[i + 1] - L0[i] if i + 1 < len(L0) else 2.5)*f for i in range(len(L0)) for f in (.45, .9)]
    sh = Image.new("RGB", (216*12, 384*2))
    for j, t in enumerate(ts[:24]): sh.paste(Image.frombytes("RGB", (P.W, P.H), frame(int(t*FPS))).resize((216, 384), Image.NEAREST), ((j % 12)*216, (j//12)*384))
    p = os.path.join(os.environ.get("STILLS_DIR", HERE), "rabiot_px_planche.jpg"); sh.save(p, quality=88); print(p)
if __name__ == "__main__": stills() if "--stills" in sys.argv else main()
