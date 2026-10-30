"""DEVINE LES 15 STARS DU PSG : format « Guess superstars » (référence envoyée par l'utilisateur) refait en DA PAPIER DOUCE
(v2, demande utilisateur : plus d'effets « édit » — ni étalonnage, ni RGB-split, ni flash, ni zoom-punch).
- Fond papier kraft, grand panneau papier bleu nuit avec la bande rouge du PSG, petites étoiles papier qui flottent.
- Cahier scotché en haut (FACILE / MOYEN / DIFFICILE) : chaque nom s'écrit au feutre, petite coche verte.
- Carte photo façon polaroïd (photo réelle détourée, liseré papier) qui tombe en se balançant, se pose, respire ;
  pastille compte à rebours 2… 1 (anneau crayon qui se remplit), puis le nom s'écrit sous la photo, tampon ✓, petits confettis ;
  la carte s'envole pour laisser la place à la suivante. Déchirures papier entre les grandes parties (accroche, CTA, fin).
- Voix : voix/voix.mp3 + voix/segments.json (début, fin, début du 1er mot) ; chaque nom est posé pour tomber pile sur sa révélation.
- Musique : UROBOROS (Hardtekk, slowed) très basse sous la voix ; le rythme des cartes suit ses temps (126,5 BPM).
  python3 episodes/devine_psg15/devine_psg15.py [--stills | --cover]"""
import sys, os, math, json, subprocess
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import engine as E
import paper_cut as PC
from story import ransom_line
import numpy as np
from PIL import Image, ImageDraw
W, H = E.W, E.H; FPS = 30
KRAFT = (236, 226, 204); NAVY = (24, 38, 92); PRED = (206, 44, 52); CREAM = (251, 247, 236); INK = (28, 36, 70)
GREEN = (52, 150, 86); ORANGE = (232, 140, 40); GOLD = (238, 190, 60); SKIN = (240, 200, 170)
OUT = os.path.join(ROOT, "output", "devine_psg15")
MUSIC = os.path.join(ROOT, "assets", "music", "uroboros_hardtekk_slowed.mp3")
BEAT = 0.4743; PHASE = 0.096; DROP1 = PHASE + 32*BEAT
VO = os.path.join(HERE, "voix", "voix.mp3"); SEG = json.load(open(os.path.join(HERE, "voix", "segments.json")))
PH = os.path.join(ROOT, "assets", "photos", "psg")
# (nom affiché, slug photo, recadrage de la photo ou None)
P = [("Mbappé", "mbappe", None), ("Messi", "messi", None), ("Neymar", "neymar", None), ("Ibrahimovic", "ibrahimovic", None), ("Dembélé", "dembele", None),
     ("Thiago Silva", "thiago_silva", None), ("Marquinhos", "marquinhos", None), ("Di María", "di_maria", (240, 0, 960, 675)),
     ("Ronaldinho", "ronaldinho", (0, 0, 789, 860)), ("Beckham", "beckham", None),
     ("Pauleta", "pauleta", (520, 40, 1400, 1080)), ("Ginola", "ginola", (0, 0, 620, 640)), ("Weah", "weah", None), ("Raí", "rai", None), ("Djorkaeff", "djorkaeff", None)]
LEVELS = [("FACILE", GREEN), ("MOYEN", ORANGE), ("DIFFICILE", PRED)]
def ceilb(x): return math.ceil(x/BEAT - 1e-6)*BEAT
def dur(i): return SEG[i][1] - SEG[i][0]
# ---------------------------------------------------------------- timeline (6 temps par joueur : « 2 », « 1 », révélation)
TL = [("hook", 0.0, ceilb(dur(0) + .45))]; t = TL[-1][2]; vpos = [0.0]
for i in range(15):
    if i == 5:
        TL.append(("cta", t, ceilb(t + dur(6) + .9))); vpos.append(t + .35); t = TL[-1][2]
    if i == 10: vpos.append(t + .2)                              # « Niveau difficile ! » pendant l'arrivée de la 11e carte
    rvt = t + 4*BEAT; TL.append(("p", t, t + 6*BEAT, i, rvt))
    si = len(vpos); vpos.append(rvt - (SEG[si][2] - SEG[si][0]) + .03); t = TL[-1][2]
TL.append(("end", t, t + dur(18) + 2.2)); vpos.append(t + .45); TOTAL = TL[-1][2]
M = DROP1 - TL[1][1]                                             # la musique arrive sur son drop quand la 1re carte tombe
TEARS = [(TL[1][1], "tear_d", 1), (TL[6][1], "tear_v", 2), (TL[7][1], "tear_h", 3), (TL[-1][1], "tear_d", 4)]   # accroche→jeu, jeu→CTA, CTA→jeu, jeu→fin
PS = [e for e in TL if e[0] == "p"]; REVEALS = [e[4] for e in PS]

# ---------------------------------------------------------------- décor (mis en cache)
_c = {}
def kraft():
    if "kraft" not in _c:
        rng = np.random.default_rng(1); a = np.zeros((H, W, 3), np.float32); a[:] = KRAFT
        a *= (.95 + .08*E._lowfreq(W, H, 3, 60))[..., None]
        sp = rng.random((H, W)); a += ((sp > .985)*-22 + (sp < .01)*14)[..., None]
        _c["kraft"] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    return _c["kraft"]
def _stripe(d, ox, oy):
    d.rectangle([ox - 168, oy - 2000, ox + 168, oy + 2000], fill=(240, 236, 226)); d.rectangle([ox - 150, oy - 2000, ox + 150, oy + 2000], fill=PRED)
PANEL = E.Paper(E.rect_pts(1240, 1320), NAVY, "panel", rough=5, pattern=_stripe)   # maillot du PSG en papier
STAR = E.Paper(E.star_shape(0, 0, 34, 5, .45), GOLD, "star", rough=1.2)
STAR2 = E.Paper(E.star_shape(0, 0, 22, 5, .45), CREAM, "star2", rough=1.0)
def bg(cv, fr, t):
    cv.alpha_composite(kraft())
    PANEL.draw(cv, fr, W//2, 1330, 1, -3, amp=2.5)
    for k, (x, y, s, sp) in enumerate(((120, 900, 1, .9), (965, 1010, .8, 1.2), (90, 1690, .7, 1.1), (990, 1720, 1, .8), (975, 820, .6, 1.4))):
        (STAR if k % 2 == 0 else STAR2).draw(cv, fr, x, y + 10*math.sin(t*sp + k), s*(1 + .06*math.sin(t*2.1 + k)), 12*math.sin(t*.7 + k))
# -- cahier
BX, BY = W//2, 445
def notebook():
    if "nb" not in _c:
        bw, bh = 1000, 560; im = E.paper_sprite(E.rect_pts(bw, bh), CREAM, seed=21, rough=2.4)
        ax, ay = im.info["anchor"]; d = ImageDraw.Draw(im); x0, y0 = ax - bw/2, ay - bh/2
        for k in range(9): d.line([(x0 + 70, y0 + 120 + k*52), (x0 + bw - 20, y0 + 120 + k*52)], fill=(176, 196, 222), width=2)
        d.line([(x0 + 62, y0 + 10), (x0 + 62, y0 + bh - 10)], fill=(226, 120, 120), width=3)
        for k in range(5): cy = y0 + 70 + k*105; d.ellipse([x0 + 18, cy - 13, x0 + 44, cy + 13], fill=KRAFT)
        f = E.font("hand", 40)
        for c in range(3):
            for r in range(5): d.text((x0 + 90 + c*305, y0 + 135 + r*80), f"{c*5 + r + 1}.", font=f, fill=(140, 132, 120))
        for x, y, rr in ((x0 + 120, y0 - 4, -14), (x0 + bw - 120, y0 - 4, 12)):
            tp = Image.new("RGBA", (170, 50), (244, 236, 206, 190)).rotate(rr, expand=True); im.alpha_composite(tp, (int(x - tp.width/2), int(y - tp.height/2)))
        _c["nb"] = im; _c["nbo"] = (x0 - ax, y0 - ay)
    return _c["nb"]
TABS = [E.Label(lab, f"tab{lab}", E.font("title", 40), (255, 255, 255), col, padx=22, pady=8, rough=2) for lab, col in LEVELS]
_nm = {}
def name_spr(txt, size, col=INK, kind="brush"):
    k = (txt, size, col, kind)
    if k not in _nm: _nm[k] = E.text_sprite(txt, E.font(kind, size), col)
    return _nm[k]
def wipe(cv, spr, x, y, u, rot=0):
    """Texte qui s'écrit de gauche à droite (feutre)."""
    if u <= 0: return
    w = max(1, int(spr.width*min(1, u))); part = spr.crop((0, 0, w, spr.height)); part.info["anchor"] = (spr.width/2, spr.height/2)
    E.blit(cv, part, x, y, 1, rot)
def board(cv, fr, t, dy=0.0):
    nb = notebook(); jx, jy = E.jit("nb", E.boil(fr), 1.2); E.blit(cv, nb, BX + jx, BY + dy + jy, 1, -.6)
    ox, oy = _c["nbo"]; x0, y0 = BX + ox, BY + dy + oy
    for c in range(3): TABS[c].draw(cv, fr, x0 + 200 + c*305, y0 + 62, 1, (-3, 2, -2)[c])
    d = ImageDraw.Draw(cv)
    for i, rv in enumerate(REVEALS):
        if t < rv + .12: continue
        u = (t - rv - .12)/.45; c, r = divmod(i, 5); nm = P[i][0]; spr = name_spr(nm, 46 if len(nm) < 11 else 40)
        wipe(cv, spr, x0 + 140 + c*305 + spr.width/2, y0 + 158 + r*80, u)
        if u > 1.1:                                              # petite coche verte au crayon
            cx, cy = x0 + 128 + c*305 + spr.width + 22, y0 + 160 + r*80
            E.pencil_line(d, [(cx - 12, cy), (cx - 3, cy + 11), (cx + 16, cy - 14)], min(1, (u - 1.1)/.5), GREEN, 5, seed=i)
# -- carte photo (polaroïd papier)
CW, CH, WW, WH_, WY = 720, 860, 650, 620, -90                    # carte, fenêtre photo, centre de la fenêtre (rel. centre carte)
def card(i):
    if i in _c: return _c[i]
    nm, slug, box = P[i]; src = os.path.join(PH, slug + ".png")
    im = E.paper_sprite(E.rect_pts(CW, CH), CREAM, seed=40 + i, rough=2.2); ax, ay = im.info["anchor"]
    win = E.paper_sprite(E.rect_pts(WW, WH_), NAVY, seed=60 + i, rough=1.2, shadow=False); wa = win.info["anchor"]; wd = ImageDraw.Draw(win)
    for k in range(9):                                           # rayons doux derrière le joueur
        a = math.pi*(1 + k/8); c0 = (wa[0], wa[1] + 120)
        wd.polygon([c0, (c0[0] + 700*math.cos(a - .09), c0[1] + 700*math.sin(a - .09)), (c0[0] + 700*math.cos(a + .09), c0[1] + 700*math.sin(a + .09))], fill=(36, 54, 120))
    sp = PC.paper_player(src, box, 700, real=True, border=12)
    s = min(1.0, (WW - 30)/sp.width); sp = sp.resize((int(sp.width*s), int(sp.height*s)), Image.LANCZOS)
    m = Image.new("L", win.size, 0); ImageDraw.Draw(m).rectangle([wa[0] - WW/2 + 6, wa[1] - WH_/2 + 6, wa[0] + WW/2 - 6, wa[1] + WH_/2 - 6], fill=255)
    lay = Image.new("RGBA", win.size, (0, 0, 0, 0)); lay.paste(sp, (int(wa[0] - sp.width/2), int(wa[1] + WH_/2 - sp.height + 24)), sp)
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(m))))
    win.alpha_composite(lay); im.alpha_composite(win, (int(ax - wa[0]), int(ay + WY - wa[1])))
    tp = Image.new("RGBA", (190, 54), (244, 236, 206, 200)).rotate(-6 if i % 2 else 7, expand=True); im.alpha_composite(tp, (int(ax - tp.width/2), int(ay - CH/2 - 22)))
    _c[i] = im; return im
STAMP = E.Paper(E.ellipse_pts(150, 150), GREEN, "stamp", rough=1.6)
BADGE = E.Paper(E.ellipse_pts(170, 170), CREAM, "badge", rough=1.6)
CX0, CY0 = W//2, 1195
def card_pose(i, t, e):
    """La carte tombe en se balançant, se pose, respire, fait un petit saut à la révélation, puis s'envole sur le côté."""
    u = t - e[1]; T = e[2] - e[1]; side = 1 if i % 2 else -1
    k = E.clamp(u/.42); y = CY0 - (1 - E.ease_out_back(k, 1.2))*1500; rot = side*(-2.2) + (1 - E.ease_out_cubic(k))*side*14
    rot += 1.1*math.sin(t*1.7 + i); y += 4*math.sin(t*2.3 + i)
    ur = t - e[4]
    if 0 <= ur < .35: y -= 26*math.sin(math.pi*ur/.35)
    ko = E.clamp((u - (T - .32))/.32)
    x = CX0 + side*E.ease_in_cubic(ko)*1250; y -= 120*ko; rot += side*24*E.ease_in_cubic(ko)
    return x, y, rot, 1 + .004*math.sin(t*3 + i)
def draw_card(cv, fr, t, e):
    i = e[3]; x, y, rot, s = card_pose(i, t, e); E.blit(cv, card(i), x, y, s, rot)
    a = math.radians(rot)
    def at(dx, dy): return x + dx*math.cos(a) + dy*math.sin(a), y - dx*math.sin(a) + dy*math.cos(a)
    ur = t - e[4]
    if ur < 0:                                                   # pastille compte à rebours + anneau crayon qui se remplit
        u = t - e[1]; n = 2 if u < 2*BEAT else 1; uu = u % (2*BEAT)
        bx, by = at(CW/2 - 40, -CH/2 + 30); sq = 1 - .25*max(0, 1 - uu/.12)
        BADGE.draw(cv, fr, bx, by, sq, rot)
        frac = E.clamp(u/(4*BEAT)); r = 70; ImageDraw.Draw(cv).arc([bx - r, by - r, bx + r, by + r], -90, -90 + 360*frac, fill=PRED, width=9)
        E.blit(cv, name_spr(str(n), 120, PRED if n == 1 else INK, "title"), bx, by - 4, sq, rot)
    else:                                                        # le nom s'écrit sous la photo, tampon ✓, petits confettis
        spr = name_spr(P[i][0], 96 if len(P[i][0]) < 11 else 82); cx, cy = at(0, CH/2 - 105)
        wipe(cv, spr, cx, cy, E.clamp(ur/.42)*1.15, rot)
        ss = E.ease_out_back(E.clamp((ur - .05)/.3), 2.2)
        if ss > .02:
            sx, sy = at(CW/2 - 70, WY + WH_/2 - 60); STAMP.draw(cv, fr, sx, sy, ss, rot - 12)
            E.pencil_line(ImageDraw.Draw(cv), [(sx - 30, sy + 2), (sx - 8, sy + 26), (sx + 34, sy - 26)], E.clamp((ur - .15)/.25), (255, 255, 255), 12, seed=i)
        E.particles(cv, fr, 300 + i, (int(cx), int(cy)), E.clamp(ur/1.1), 16, 300, [GOLD, GREEN, CREAM, PRED], 14, 420)
    E.blit(cv, name_spr(f"{i + 1}/15", 44, CREAM, "title"), 930, 1745, 1, 0)
LVL = [E.Label(f"NIVEAU {lab}", f"lvl{lab}", E.font("title", 72), (255, 255, 255), col, padx=30, pady=12) for lab, col in LEVELS]
# ---------------------------------------------------------------- scènes
def logo():
    if "logo" not in _c:
        lg = Image.open(os.path.join(ROOT, "assets", "logos", "psg_sticker.png")).convert("RGBA"); s = 600/lg.width
        lg = lg.resize((600, int(lg.height*s)), Image.LANCZOS); lg.info["anchor"] = (lg.width/2, lg.height/2); _c["logo"] = lg
    return _c["logo"]
CTA_L = E.Label("Avant le niveau moyen…", "ctal", E.font("hand", 70), INK, CREAM, padx=30, pady=10)
BTN = [E.Label("S'ABONNER", "btn0", E.font("title", 110), (255, 255, 255), PRED, padx=56, pady=24),
       E.Label("ABONNÉ !", "btn1", E.font("title", 110), (255, 255, 255), GREEN, padx=56, pady=24)]
HEART = E.Paper([(16*math.sin(a)**3*5.2, -(13*math.cos(a) - 5*math.cos(2*a) - 2*math.cos(3*a) - math.cos(4*a))*5.2) for a in np.linspace(0, 2*math.pi, 48)], PRED, "heart", rough=1.5)
END1 = E.Label("T'en as trouvé combien ?", "end1", E.font("title", 76), INK, GOLD, padx=34, pady=14)
END2 = E.Label("DIS-LE EN COMMENTAIRE", "end2", E.font("title", 64), (255, 255, 255), PRED, padx=30, pady=12)
def hand(cv, x, y):
    """Petite main en papier (doigt tendu) qui vient appuyer sur le bouton."""
    d = ImageDraw.Draw(cv); o = (150, 110, 90)
    d.rounded_rectangle([x - 14, y - 78, x + 14, y + 8], 14, fill=SKIN, outline=o, width=3)
    d.ellipse([x - 40, y - 12, x + 40, y + 76], fill=SKIN, outline=o, width=3)
    d.rectangle([x - 30, y + 66, x + 30, y + 130], fill=(250, 247, 238), outline=o, width=3)
def scene(cv, fr, t):
    e = [x for x in TL if x[1] <= t][-1]; u = t - e[1]; bg(cv, fr, t)
    if e[0] == "hook":                                           # image 0 : lisible tout de suite, rien n'arrive en retard
        ransom_line(cv, "DEVINE CES", 300, 118, seed=3, fr=fr)
        ransom_line(cv, "15 STARS", 470, 170, seed=5, fr=fr)
        ransom_line(cv, "DU PSG", 640, 128, seed=7, fr=fr)
        E.blit(cv, logo(), W//2, 1190 + 8*math.sin(t*2), 1 + .015*math.sin(t*3), 3*math.sin(t*1.4))
    elif e[0] == "p":
        board(cv, fr, t); draw_card(cv, fr, t, e); i = e[3]
        if i in (5, 10) and u < 1.3:                             # annonce du niveau : étiquette qui se pose puis repart
            o = E.clamp((u - 1.0)/.3); LVL[i//5].draw(cv, fr, W//2 - 800*E.ease_in_cubic(o), 820, E.ease_out_back(E.clamp(u/.35)), -3)
    elif e[0] == "cta":
        board(cv, fr, t)
        CTA_L.draw(cv, fr, W//2, 950, E.pop_in(t, e[1] + .15, .4), -2)
        press = E.clamp((u - 1.25)/.18); st = 1 if u > 1.34 else 0
        BTN[st].draw(cv, fr, W//2, 1200, E.pop_in(t, e[1] + .4, .45)*(1 - .1*math.sin(math.pi*press)), 2)
        if u > 1.34:
            hu = E.clamp((u - 1.34)/.5); HEART.draw(cv, fr, W//2 + 300, 1060 - 40*hu, E.ease_out_back(hu, 2.4), 12)
            E.particles(cv, fr, 77, (W//2, 1200), E.clamp((u - 1.34)/1.1), 22, 380, [PRED, GOLD, CREAM], 16, 380)
        if u > .7: hand(cv, W//2 + 160 + 300*(1 - E.ease_out_cubic(E.clamp((u - .7)/.5))), 1290 + 30*math.sin(math.pi*press))
    else:
        board(cv, fr, t, 60*E.ease_io(E.clamp(u/.6)))
        END1.draw(cv, fr, W//2, 1150, E.pop_in(t, e[1] + .2, .45), -2)
        ransom_line(cv, "SUR 15 ?", 1310, 120, seed=9, fr=fr, scale=E.pop_in(t, e[1] + .4, .45))
        END2.draw(cv, fr, W//2, 1480, E.pop_in(t, e[1] + .6, .45), 2)
        E.confetti(cv, fr, 999, u, 50, 6.0, [GOLD, GREEN, CREAM, PRED], (0, 0, W, H))
def render(fr, t):
    cv = Image.new("RGBA", (W, H)); scene(cv, fr, t)
    for t0, kind, seed in TEARS:
        if t0 <= t < t0 + .55:                                   # déchirure papier : l'ancienne image se fend et s'envole
            prev = Image.new("RGBA", (W, H)); scene(prev, int((t0 - 1/FPS)*FPS), t0 - 1/FPS)
            out = cv.convert("RGB"); E.tear_transition(out, prev.convert("RGB"), (t - t0)/.55, kind, seed); return out
    return cv.convert("RGB")
def frame(fr): return render(fr, fr/FPS).tobytes()

# ---------------------------------------------------------------- son
def build_audio(wav):
    S = OUT + "/_a"; os.makedirs(S, exist_ok=True); evs = []
    for k, (a, b, _) in enumerate(SEG):
        p = f"{S}/s{k}.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(a), "-t", str(b - a), "-i", VO, "-af", "afade=t=in:d=0.015,areverse,afade=t=in:d=0.03,areverse", "-ar", "48000", "-ac", "2", p], check=True)
        evs.append((p, vpos[k], 1.0))
    L5 = os.path.join(ROOT, "episodes", "lille_v5", "sfx")
    for e in TL:
        if e[0] == "p":
            evs += [(f"{L5}/swish.mp3", e[1], .45), (f"{L5}/tick.mp3", e[1] + .1, .4), (f"{L5}/tick.mp3", e[1] + 2*BEAT, .4),
                    (f"{L5}/marker.mp3", e[4], .5), (f"{L5}/stamp.mp3", e[4] + .08, .45), (f"{L5}/sparkle.mp3", e[4] + .1, .25)]
    for t0, _, _ in TEARS: evs.append((f"{L5}/page_tear.mp3", t0, .6))
    cta = TL[6]; evs += [(f"{L5}/pop.mp3", cta[1] + 1.27, .6), (f"{L5}/heart.mp3", cta[1] + 1.36, .4)]
    ins = ["-f", "lavfi", "-t", f"{TOTAL:.2f}", "-i", "anullsrc=r=48000:cl=stereo"] + sum([["-i", p] for p, _, _ in evs], []); fc = ""
    for i, (_, ts, g) in enumerate(evs): fc += f"[{i + 1}:a]aresample=48000,adelay={int(max(0, ts)*1000)}|{int(max(0, ts)*1000)},volume={g}[e{i}];"
    fc += "[0:a]" + "".join(f"[e{i}]" for i in range(len(evs))) + f"amix=inputs={1 + len(evs)}:normalize=0:duration=first[a]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-filter_complex", fc, "-map", "[a]", f"{S}/vo.wav"], check=True)
    fc = ("[0:a]loudnorm=I=-14:TP=-1.5,aresample=48000,asplit=2[v][key];"            # voix + bruitages normalisés, musique ajoutée très bas
          f"[1:a]atrim=0:{TOTAL:.2f},asetpts=PTS-STARTPTS,aresample=48000,volume=0.03,afade=t=out:st={TOTAL - 1.5:.2f}:d=1.5[mus];"
          "[mus][key]sidechaincompress=threshold=0.02:ratio=6:attack=8:release=300[md];[v][md]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{S}/vo.wav", "-ss", f"{M:.3f}", "-i", MUSIC, "-filter_complex", fc, "-map", "[a]", "-ar", "48000", wav], check=True)
def warm():
    for i in range(15): card(i)                                  # détourages calculés une fois, avant le fork
def main():
    os.makedirs(OUT, exist_ok=True); v = OUT + "/_v.mp4"; a = OUT + "/_a.wav"; build_audio(a); warm()
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "medium", "-maxrate", "6M", "-bufsize", "12M", v], stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for b in pool.imap(frame, range(int(TOTAL*FPS)), chunksize=6): pr.stdin.write(b)
    pr.stdin.close(); pr.wait(); out = OUT + "/devine_psg15.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    os.remove(v); os.remove(a); subprocess.run(["rm", "-rf", OUT + "/_a"]); print(out, round(TOTAL, 2))
def stills():
    warm()
    ts = [0, TL[1][1] + .2, PS[0][1] + .25, PS[0][1] + 1.2, PS[0][4] + .2, PS[0][4] + .7, PS[0][2] - .12, PS[1][1] + .6,
          PS[4][4] + .8, TL[6][1] + .9, TL[6][1] + 1.6, PS[5][1] + .5, PS[7][1] + 1, PS[8][4] + .6, PS[10][1] + .5, PS[10][4] + .6,
          PS[11][4] + .6, PS[12][4] + .6, PS[13][4] + .6, PS[14][4] + .7, TL[-1][1] + .3, TL[-1][1] + 1.8]
    sh = Image.new("RGB", (216*11, 384*2))
    for k, t in enumerate(ts[:22]): sh.paste(render(int(t*FPS), t).resize((216, 384)), ((k % 11)*216, (k//11)*384))
    p = os.path.join(os.environ.get("STILLS_DIR", OUT), "devine_psg15_planche.jpg"); os.makedirs(os.path.dirname(p), exist_ok=True); sh.save(p, quality=85); print(p, round(TOTAL, 2))
def cover():
    os.makedirs(OUT, exist_ok=True); p = OUT + "/devine_psg15_couverture.jpg"; render(0, 0.0).save(p, quality=92); print(p)
if __name__ == "__main__":
    print("TOTAL", round(TOTAL, 2), "M", round(M, 3))
    stills() if "--stills" in sys.argv else (cover() if "--cover" in sys.argv else main())
