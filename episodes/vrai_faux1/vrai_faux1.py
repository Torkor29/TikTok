"""VRAI OU FAUX #1 (nouveau format, ≈ 25 s) — 1er épisode construit avec la checklist « image 0 » du skill viral.
5 affirmations, 1,5 s pour répondre (VRAI / FAUX), révélation + preuve en 1 ligne, « combien sur 5 ? » en commentaire.
Voix Léo (voix/brut.mp3) coupée en 6 morceaux et replacée sur une grille.

  python3 episodes/vrai_faux1/vrai_faux1.py output/vrai_faux1 --stills
  python3 episodes/vrai_faux1/vrai_faux1.py output/vrai_faux1
"""
import sys, os, math, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from quiz import *
from engine import load_audio, SR
from PIL import ImageFilter

TITLE = "~/quiz $ ./vrai_ou_faux"
SLUG = "vrai_faux1"
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
NOIR = (28, 26, 30); BLANC = (250, 250, 246); ROUGE = (214, 36, 46); VERT = (40, 170, 84); JAUNE = (255, 214, 52)

# (affirmation écrite, réponse, preuve, visuels [(type, nom, x, y, h, rot)], fond, découpe voix (début, fin))
ITEMS = [
    ("L'OM est le SEUL club français à avoir gagné la Ligue des champions", False, "Le PSG l'a gagnée en 2025",
     [("logo", "om", CX, 880, 700, -5), ("logo", "ucl", 920, 560, 260, 10)], (0, 150, 214), (0.0, 3.96)),
    ("Lyon a été champion de France 7 fois de suite", True, "De 2002 à 2008",
     [("logo", "ol", CX, 820, 760, 4), ("logo", "ligue1", 180, 1150, 260, -10)], (28, 58, 150), (4.35, 6.65)),
    ("Zidane n'a jamais gagné le Ballon d'or", False, "Ballon d'or 1998",
     [("pt", "d1A", CX, 820, 820, -3)], (226, 170, 30), (7.00, 8.59)),
    ("Thierry Henry est le meilleur buteur de l'histoire d'Arsenal", True, "228 buts, record du club",
     [("pt", "d2A", 520, 840, 800, 3), ("logo", "arsenal", 900, 1150, 300, 10)], (200, 16, 46), (9.10, 11.66)),
    ("Le Bayern n'a jamais perdu une finale de Ligue des champions", False, "Battu en finale en 1999, 2010, 2012…",
     [("logo", "bayern", CX, 820, 760, -4), ("logo", "ucl", 180, 1160, 280, -10)], (16, 22, 60), (11.99, 15.00)),
]
OUTRO = (15.35, 17.65)
ANSWER = 1.5; HOLD = 1.0                                     # temps pour répondre, temps de révélation

# grille : chaque item = voix, puis ANSWER s de chrono, puis HOLD s de révélation
T = []; t = 0.0
for it in ITEMS:
    s, e = it[5]; T.append((t, t + (e - s), t + (e - s) + ANSWER)); t = T[-1][2] + HOLD
T_OUT = t; T_END = T_OUT + (OUTRO[1] - OUTRO[0]) + 1.6

VOIX = f"/tmp/{SLUG}_voix.wav"
def build_voice():
    a = load_audio(os.path.join(HERE, "voix", "brut.mp3")); out = np.zeros(int((T_END + 1)*SR), np.float32)
    for (s, e), t0 in [(it[5], T[k][0]) for k, it in enumerate(ITEMS)] + [(OUTRO, T_OUT)]:
        seg = a[int(s*SR):int(e*SR)].copy(); f = min(len(seg), int(.02*SR))
        seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        i = int((t0 + PAD_IN)*SR); out[i:i + len(seg)] += seg
    with wave.open(VOIX, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1)*32767).astype(np.int16).tobytes())
    return VOIX

_c = {}
def put(cv, kind, name, x, y, h, s=1.0, rot=0.0):
    if s <= .02: return
    p = os.path.join(ROOT, "assets", "logos", f"{name}_sticker.png") if kind == "logo" else os.path.join(ROOT, "assets", "tu_gardes_qui1", f"{name}.png")
    k = (p, h)
    if k not in _c:
        im = Image.open(p).convert("RGBA"); im = im.resize((int(im.width*h/im.height), h), Image.LANCZOS); im.info["anchor"] = (im.width/2, im.height/2)
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda v: v*110//255)); sh = sh.filter(ImageFilter.GaussianBlur(10))
        sh.info["anchor"] = im.info["anchor"]; _c[k] = (im, sh)
    im, sh = _c[k]; blit_sxy(cv, sh, x + 14*s, y + 18*s, s, s, rot); blit_sxy(cv, im, x, y, s, s, rot)

def shake(cv, t, t0, amp=22, dur=.35):
    if t0 <= t < t0 + dur:
        a = amp*(1 - (t - t0)/dur); cv.paste(cv.copy(), (int(a*math.sin(t*90)), int(a*math.cos(t*73))))
def flash(cv, t, t0, col, dur=.15):
    if t0 <= t < t0 + dur:
        cv.paste(Image.blend(cv.convert("RGB"), Image.new("RGB", (W, H), col), .5*(1 - (t - t0)/dur)).convert(cv.mode), (0, 0))
def big(txt, key, size=110, fg=BLANC, bg=NOIR, rough=3, maxw=1000): return LBL(txt, key, font("title", size), fg, bg, padx=26, pady=6, rough=rough, maxw=maxw)

def item_of(t):
    k = 0
    for i, (a, b, c) in enumerate(T):
        if t >= a - .02: k = i
    return k

def buttons(cv, fr, t, k, ts, te, ok):
    """Boutons VRAI / FAUX : pulsent pendant le chrono, puis le bon grossit, l'autre s'éteint."""
    for j, (lab, col, x) in enumerate([("VRAI", VERT, 290), ("FAUX", ROUGE, 790)]):
        good = (j == 0) == ok
        if t < te: s = 1 + .06*math.sin((t - ts)*14 + j*math.pi) if t > ts else 1
        else: s = 1 + .25*ease_out_back(clamp((t - te)/.25)) if good else .8
        c = col if (t < te or good) else (120, 120, 126)
        big(lab, f"vfb{j}{c}", 110, BLANC, c, rough=2).draw(cv, fr, x, 1720, s, (-4, 4)[j])

def draw(cv, fr, t, Tt):
    t = t - PAD_IN
    if t >= T_OUT - .02: return outro(cv, fr, t - T_OUT)
    k = item_of(t); txt, ok, proof, vis, bg, _ = ITEMS[k]; t0, ts, te = T[k]; tl = t - t0
    stage_fill(cv, fr, bg, f"vfbg{k}"); rays(cv, (CX, 860), t, .9, 18, 1700, tuple(min(255, c + 34) for c in bg), .1, .4)
    # en-tête : ÉNORME à l'image 0 (item 1), puis petit bandeau
    if k == 0 and tl < 1.2:
        ransom_line(cv, "VRAI OU", 150, 170, seed=4); ransom_line(cv, "FAUX ?", 330, 180, seed=8)
    else:
        big("VRAI OU FAUX ?", "vfh", 64, NOIR, JAUNE).draw(cv, fr, 330, 120, 1, -3)
        big(f"{k + 1}/5", f"vfn{k}", 64, BLANC, NOIR).draw(cv, fr, 900, 120, 1, 3)
    # visuel énorme (déjà là à l'image 0 pour l'item 1)
    zoom = 1 + .025*tl
    for j, (kind, name, x, y, h, rot) in enumerate(vis):
        s = 1.0 if (k == 0 and j == 0) else slam(t, t0 + .06*j, .2)
        put(cv, kind, name, x, y, h, s*zoom, rot + 1.5*math.sin(t*3 + j))
    # affirmation
    LBL(txt, f"vft{k}", font("title", 66), NOIR, BLANC, padx=30, pady=12, rough=3, maxw=960).draw(cv, fr, CX, 1390, 1.0 if k == 0 else slam(t, t0 + .1, .18), -2)
    # chrono (barre qui se vide)
    if ts <= t < te:
        u = (t - ts)/ANSWER; d = ImageDraw.Draw(cv)
        d.rounded_rectangle([140, 1560, 940, 1590], 14, fill=(0, 0, 0))
        d.rounded_rectangle([140, 1560, 140 + 800*(1 - u), 1590], 14, fill=JAUNE)
    buttons(cv, fr, t, k, ts, te, ok)
    # révélation
    if t >= te:
        STAMP("VRAI" if ok else "FAUX", f"vfs{k}", VERT if ok else ROUGE, 190).draw(cv, fr, CX, 830, slam(t, te, .2), -10 if ok else 10)
        big(proof, f"vfp{k}", 60, NOIR, JAUNE, maxw=980).draw(cv, fr, CX, 1100, slam(t, te + .15, .18), 2)
        flash(cv, t, te, VERT if ok else ROUGE); shake(cv, t, te)
    if k and tl < .3: punch(cv, t, t0, 1.07, .25)
    drift(cv, t + PAD_IN, Tt, .012)

def outro(cv, fr, t):
    stage_fill(cv, fr, (24, 24, 28), "vfout"); rays(cv, (CX, 900), t, .9, 18, 1700, (44, 44, 52), .1, .4)
    ransom_line(cv, "COMBIEN", 300, 160, seed=6)
    ransom_line(cv, "SUR 5 ?", 480, 170, seed=9)
    for j, (kind, name) in enumerate([("logo", "om"), ("logo", "ol"), ("pt", "d1A"), ("pt", "d2A"), ("logo", "bayern")]):
        put(cv, kind, name, 140 + j*200, 900 + (j % 2)*90, 240, slam(t, .1 + j*.08, .18), (-8, 6, -4, 7, -6)[j])
    big("DIS-LE EN COMMENTAIRE", "vfo1", 80, NOIR, JAUNE).draw(cv, fr, CX, 1300, slam(t, 1.0, .2), -2)
    sub_button(cv, fr, CX, 1560, t, 1.6, 2.1)

P = PAD_IN
SFX = [(0.0, "boom", .9), (0.0, "braam", .5), (0.05, "stamp", .6)]
for k, (t0, ts, te) in enumerate(T):
    ok = ITEMS[k][1]
    if k: SFX += [(P + t0, "whoosh", .5), (P + t0 + .05, "stamp", .5)]
    SFX += [(P + ts, "tictac", .45), (P + te, "correct" if ok else "buzzer", .8), (P + te + .02, "stamp", .7)]
SFX += [(P + T_OUT, "whoosh", .5), (P + T_OUT + 1.0, "notif", .6)]
SCENES = [Scene("vraifaux", "vrai ou faux", draw, SFX, pad_in=P, pad_out=.2, min_dur=T_END + P)]

def cover(path):
    cv = background(0, TITLE); stage_fill(cv, 0, (0, 150, 214), "vfcv"); rays(cv, (CX, 1000), 0, .9, 18, 1700, (40, 180, 240), .1)
    ransom_line(cv, "VRAI OU", 250, 190, seed=4); ransom_line(cv, "FAUX ?", 460, 200, seed=8)
    put(cv, "logo", "om", 300, 900, 520, 1, -8); put(cv, "pt", "d1A", 800, 980, 600, 1, 5)
    big("95 % FONT MOINS DE 4/5", "vfcv1", 70, NOIR, JAUNE).draw(cv, 0, CX, 1450, 1, -2)
    big("VRAI", "vfcvv", 110, BLANC, VERT).draw(cv, 0, 290, 1700, 1, -4); big("FAUX", "vfcvf", 110, BLANC, ROUGE).draw(cv, 0, 790, 1700, 1, 4)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

def stills(out):
    build_voice(); scene_timing(SCENES, [VOIX]); sc = SCENES[0]; os.makedirs(out, exist_ok=True)
    ts = [P + x for x in (0.05, 2.0, T[0][1] + .5, T[0][2] + .5, T[1][0] + 1, T[2][2] + .5, T[3][0] + 1, T[4][2] + .5, T_OUT + .5, T_OUT + 2.5)]
    ims = []
    for t in ts:
        f = int(t*FPS); cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T); finish(cv, TITLE); ims.append(cv.resize((216, 384)))
    sheet = Image.new("RGB", (216*len(ims), 414), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims): sheet.paste(im, (k*216, 30)); dd.text((k*216 + 6, 4), f"{ts[k]:.1f}s", font=font("mono", 22), fill=(230, 230, 230))
    p = os.path.join(out, "sheet.jpg"); sheet.save(p, quality=82); return p

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", SLUG)
    if "--stills" in args: print(stills(f"/tmp/{SLUG}_stills")); sys.exit()
    os.makedirs(out, exist_ok=True); cover(os.path.join(out, f"{SLUG}_couverture.jpg")); build_voice()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=[VOIX], sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25, limit=True))
