"""DEVINE LE JOUEUR (format court, ~16 s, SANS réponse : on devine en commentaire). EN TEST.
Voix Léo coupée en morceaux et replacée sur une grille fixe (un club toutes les 2 s). Vrais écussons en autocollants.
Réponse (à épingler le lendemain) : Thierry Henry — Monaco 94, Juventus 99, Arsenal 99, Barcelone 07, New York 10.

  python3 episodes/devine_court_henry/devine_court_henry.py output/devine_court_henry --stills
  python3 episodes/devine_court_henry/devine_court_henry.py output/devine_court_henry
"""
import sys, os, math, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from quiz import *
from engine import load_audio, SR
from PIL import ImageFilter

TITLE = "~/devine $ ./joueur"
SLUG = "devine_court_henry"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
NOIR = (30, 28, 28); BLANC = (250, 250, 246); ROUGE = (210, 36, 42)
PORTRAIT = os.path.join(ROOT, "assets", "tu_gardes_qui1", "d2A.png")

# (club, année, écusson ou None, couleur de fond)
CAR = [("MONACO", 1994, "monaco", (170, 24, 36)), ("JUVENTUS", 1999, "juventus", (34, 34, 38)),
       ("ARSENAL", 1999, "arsenal", (190, 20, 34)), ("BARCELONE", 2007, "barca", (110, 28, 72)),
       ("NEW YORK", 2010, None, (20, 44, 96))]
T_HOOK = 0.0; T_CLUB = [3.0 + 1.9*k for k in range(5)]; T_Q = T_CLUB[-1] + 2.0; T_CTA = T_Q + .6; T_END = T_Q + 4.2

# ---------------------------------------------------------------- voix : morceaux (début, fin dans brut.mp3) -> instants
CUTS = [((0.0, 2.85), T_HOOK, "consigne"), ((1.95, 2.52), T_CLUB[0]), ((2.68, 3.44), T_CLUB[1]), ((3.64, 4.29), T_CLUB[2]),
        ((4.40, 5.37), T_CLUB[3]), ((5.48, 6.02), T_CLUB[4]), ((6.43, 8.27), T_Q)]
CUTS = [c if len(c) == 3 else (*c, "brut") for c in CUTS]
VOIX = f"/tmp/{SLUG}_voix.wav"
def build_voice():
    src = {n: load_audio(os.path.join(HERE, "voix", n + ".mp3")) for n in ("brut", "consigne")}; out = np.zeros(int((T_END + 1)*SR), np.float32)
    for (s, e), t, n in CUTS:
        a = src[n]
        seg = a[int(s*SR):int(e*SR)].copy(); f = min(len(seg), int(.02*SR))
        seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        i = int((t + PAD_IN)*SR); out[i:i + len(seg)] += seg
    with wave.open(VOIX, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1)*32767).astype(np.int16).tobytes())
    return VOIX

# ---------------------------------------------------------------- images
_c = {}
def _img(key, path, h, sil=False):
    k = (key, h, sil)
    if k not in _c:
        im = Image.open(path).convert("RGBA"); im = im.resize((int(im.width*h/im.height), h), Image.LANCZOS)
        if sil:
            a = im.getchannel("A"); im = Image.new("RGBA", im.size, (18, 18, 22, 255)); im.putalpha(a)
        im.info["anchor"] = (im.width/2, im.height/2)
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda v: v*110//255))
        sh = sh.filter(ImageFilter.GaussianBlur(10)); sh.info["anchor"] = im.info["anchor"]; _c[k] = (im, sh)
    return _c[k]
def sticker(cv, logo, x, y, h, s=1.0, rot=0.0):
    if s <= .02: return
    im, sh = _img(logo, os.path.join(ROOT, "assets", "logos", f"{logo}_sticker.png"), h)
    blit_sxy(cv, sh, x + 14*s, y + 18*s, s, s, rot); blit_sxy(cv, im, x, y, s, s, rot)
def mystery(cv, x, y, h, s=1.0, rot=0.0):
    if s <= .02: return
    im, sh = _img("sil", PORTRAIT, h, sil=True)
    blit_sxy(cv, sh, x + 14*s, y + 18*s, s, s, rot); blit_sxy(cv, im, x, y, s, s, rot)

def shake(cv, t, t0, amp=22, dur=.35):
    if not (t0 <= t < t0 + dur): return
    a = amp*(1 - (t - t0)/dur); cv.paste(cv.copy(), (int(a*math.sin(t*90)), int(a*math.cos(t*73))))
def flash(cv, t, t0, dur=.12):
    if t0 <= t < t0 + dur:
        u = 1 - (t - t0)/dur; cv.paste(Image.blend(cv.convert("RGB"), Image.new("RGB", (W, H), BLANC), .55*u).convert(cv.mode), (0, 0))
def big(txt, key, size=110, fg=BLANC, bg=NOIR, rough=3): return LBL(txt, key, font("title", size), fg, bg, padx=26, pady=6, rough=rough, maxw=1000)
def mix(a, b, u): return tuple(int(x + (y - x)*clamp(u)) for x, y in zip(a, b))

def club_k(t):
    k = -1
    for i, tc in enumerate(T_CLUB):
        if t >= tc - .05: k = i
    return k

def draw(cv, fr, t, T):
    t = t - PAD_IN; k = club_k(t); q = t >= T_Q
    # fond : couleur du club courant (fondu rapide), rayons qui tournent
    bg = (16, 30, 66) if k < 0 else CAR[k][3]
    if k >= 1 and t < T_CLUB[k] + .25: bg = mix(CAR[k - 1][3], bg, (t - T_CLUB[k] + .05)/.3)
    if q: bg = mix(bg, (14, 14, 18), (t - T_Q)/.3)
    stage_fill(cv, fr, bg, "dch"); rays(cv, (CX, 860), t, .9, 16, 1600, mix(bg, BLANC, .18), .1, .35)
    # bandeau titre (toujours visible) : gros au début, puis réduit en haut
    u = clamp((t - 2.7)/.35); sz = int(lerp(1.0, .62, u)*100)
    if not q and k >= 0:
        LBL("95 % NE LE TROUVENT PAS", "dcht", font("title", 62), NOIR, GOLD, padx=24, pady=6, rough=3).draw(cv, fr, CX, 170, slam(t, T_CLUB[0], .16), -3)
    # hook : silhouette mystère + « ??? » avant le 1er club
    if k < 0:
        mystery(cv, CX, 1120, 820, 1.0, 3*math.sin(t*3))
        big("JE TE DONNE", "dchh1", 120, NOIR, GOLD).draw(cv, fr, CX, 250, 1.0, -3)
        big("SES CLUBS", "dchh2", 120, BLANC, NOIR).draw(cv, fr, CX, 420, slam(t, .25, .16), 3)
        STAMP("TROUVE LE JOUEUR", "dchq", ROUGE, 104).draw(cv, fr, CX, 1640, slam(t, 1.65, .2), -5)
        shake(cv, t, 1.67)
    # club courant : gros autocollant qui claque + année
    if 0 <= k and not q:
        tc = T_CLUB[k]; club, yr, logo, _ = CAR[k]; s = slam(t, tc, .2); wob = 2*math.sin(t*5)
        if logo: sticker(cv, logo, CX, 760, 640, s*(1 + .015*math.sin(t*6)), -4 + wob)
        else: big(club, "dchny", 170, BLANC, NOIR).draw(cv, fr, CX, 760, s, -4 + wob)
        big(str(yr), f"dchy{k}", 150, NOIR, GOLD).draw(cv, fr, CX, 1150, slam(t, tc + .12, .18), -6)
        if logo: big(club, f"dchc{k}", 96, BLANC, NOIR).draw(cv, fr, CX, 1320, slam(t, tc + .2, .18), 4)
    # frise des clubs déjà passés (en bas), qui se remplit
    n = (k if not q else 5)
    for j in range(max(0, n)):
        x = 140 + j*200; y = 1560 if not q else 1500; logo = CAR[j][2]; s = pop_in(t, T_CLUB[j + 1] - .05 if j + 1 < 5 else T_Q - .05, .3)
        if logo: sticker(cv, logo, x, y, 170, s, (-6, 5, -4, 6, -3)[j])
        else: big("NY", "dchnys", 70, BLANC, NOIR).draw(cv, fr, x, y, s, -3)
        LBL(str(CAR[j][1]), f"dchfy{j}", font("mono", 34), NOIR, GOLD, padx=10, pady=2, rough=2).draw(cv, fr, x, y + 120, s, -3)
    # question finale : silhouette + ??? + CTA
    if q:
        mystery(cv, CX, 820, 980, slam(t, T_Q, .22), 2*math.sin(t*3))
        big("C'EST QUI ?", "dchcq", 150, NOIR, GOLD).draw(cv, fr, CX, 230, slam(t, T_Q + .1, .2), -4)
        STAMP("???", "dchqq", ROUGE, 170).draw(cv, fr, CX, 820, slam(t, T_Q + .35, .2), 8)
        if t > T_CTA + .4:
            LBL("DIS-LE EN COMMENTAIRE", "dchcta", font("title", 64), BLANC, ROUGE, padx=26, pady=8, rough=3, maxw=1040).draw(cv, fr, CX, 1760, slam(t, T_CTA + .4, .25), 2)
    for tc in T_CLUB + [T_Q]: shake(cv, t, tc + .02); flash(cv, t, tc)
    if 0 <= k: punch(cv, t, T_CLUB[k], 1.05, .25)
    drift(cv, t + PAD_IN, T, .015)

SFX = [(0.0, "boom", .9), (0.0, "braam", .55), (.05, "stamp", .7), (PAD_IN + 1.65, "stamp", .8), (PAD_IN + 1.0, "riser", .4)]
SFX += [(PAD_IN + T_CLUB[0] + 2*k, "tictac", .35) for k in range(5)] + [(PAD_IN + T_Q - 1.0, "drumroll", .5)]
SFX += [(PAD_IN + tc - .12, "whoosh", .5) for tc in T_CLUB] + [(PAD_IN + tc, "stamp", .65) for tc in T_CLUB]
SFX += [(PAD_IN + T_Q, "boom", .8), (PAD_IN + T_Q + .35, "stamp", .8), (PAD_IN + T_CTA + .9, "notif", .6)]
SCENES = [Scene("henry", "devine le joueur", draw, SFX, pad_in=PAD_IN, pad_out=.2, min_dur=T_END + PAD_IN)]

def cover(path):
    cv = background(0, TITLE); stage_fill(cv, 0, (16, 30, 66), "dchcv"); rays(cv, (CX, 1000), 0, .9, 16, 1600, (60, 80, 130), .1)
    ransom_line(cv, "DEVINE", 230, 170, seed=3); ransom_line(cv, "LE JOUEUR", 420, 150, seed=9)
    LBL("95 % NE LE TROUVENT PAS", "dchcv1", font("title", 70), NOIR, GOLD, padx=24, pady=6, rough=3).draw(cv, 0, CX, 590, 1, -3)
    mystery(cv, CX, 1150, 900, 1, 2); STAMP("???", "dchcv2", ROUGE, 170).draw(cv, 0, CX, 1150, 1, 8)
    for j, (lg, x, y, r) in enumerate([("monaco", 170, 900, -8), ("juventus", 910, 880, 7), ("arsenal", 170, 1500, 6), ("barca", 910, 1520, -6)]):
        sticker(cv, lg, x, y, 260, 1, r)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

def stills(out):
    build_voice(); scene_timing(SCENES, [VOIX]); sc = SCENES[0]; os.makedirs(out, exist_ok=True)
    ts = [PAD_IN + x for x in (0.05, .8, T_CLUB[0] + .4, T_CLUB[1] + .6, T_CLUB[3] + .6, T_CLUB[4] + .6, T_Q + .6, T_END - .2)]
    ims = []
    for t in ts:
        f = int(t*FPS); cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T); finish(cv, TITLE); ims.append(cv.resize((270, 480)))
    sheet = Image.new("RGB", (270*len(ims), 510), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims): sheet.paste(im, (k*270, 30)); dd.text((k*270 + 6, 4), f"{ts[k]:.1f}s", font=font("mono", 22), fill=(230, 230, 230))
    p = os.path.join(out, "sheet.jpg"); sheet.save(p, quality=82); return p

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", SLUG)
    if "--stills" in args: print(stills(f"/tmp/{SLUG}_stills")); sys.exit()
    os.makedirs(out, exist_ok=True); cover(os.path.join(out, f"{SLUG}_couverture.jpg")); build_voice()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=[VOIX], sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25, limit=True))
