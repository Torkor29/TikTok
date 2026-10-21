"""LE STADE DES SUPPORTERS — épisode 2 : résultats du jour 2 (pseudos lus dans les commentaires de l'ép. 1, voir jour2.json).
Réutilise les outils de ep1.py (tribune 3D, supporters papercraft, écussons, podium, mixage voix devant).

  python3 episodes/supporters/ep2.py --stills
  python3 episodes/supporters/ep2.py
"""
import sys, os, math, json, subprocess, functools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ep1 as E
from ep1 import (W, H, FPS, ROOT, JAUNE, ROUGE, BLANC, NOIR, CREME, CLUBS, L_, logo, background, rays, stand_sprite, podium_sprite,
                 podium_top, cup, fan_sprite, puff, project, M, El, Image, ImageDraw, blit, blit_sxy)

DATA = json.load(open(os.path.join(HERE, "jour2.json")))
FANS = DATA["supporters"]
COL = {n: (c1, c2) for n, c1, c2 in CLUBS}
COUNT = {}
for _, c in FANS: COUNT[c] = COUNT.get(c, 0) + 1
RANK = sorted(COUNT.items(), key=lambda kv: -kv[1])
TOTAL = len(FANS)
NAME = dict(psg="PSG", om="OM", lens="LENS", rennes="RENNES", lille="LILLE", angers="ANGERS", lemans="LE MANS", toulouse="TOULOUSE",
            lehavre="LE HAVRE", strasbourg="STRASBOURG", brest="BREST", ol="OL", auxerre="AUXERRE")

VOICE = os.path.join(HERE, "voix", "ep2.mp3")
# temps clés (s) — recalés sur la voix une fois générée (voir retime())
T = dict(quarante=1.2, psg=3.6, egal=6.4, rennes=9.4, ton=11.0, comm=12.6, end=16.2)
DUR = T["end"]

def seat_order(n=7, rows=3):
    """Ordre de remplissage : rang du bas d'abord, du centre vers les côtés."""
    cols = sorted(range(n), key=lambda i: (abs(i - (n - 1)/2), i))
    return [(r, i) for r in range(rows) for i in cols]
SEATS = seat_order()
def seat_xy(r, i):
    return project(((i - 3)*.8, r*.55 + .62, -r*.75 + .08), yaw=0, pitch=.5, scale=1100/6.0, center=(0, 1.1, -.75), size=1100)

def stand_col(club):
    c1, c2 = COL[club]
    return c2 if club in ("om", "ol", "auxerre", "angers") else c1

@functools.lru_cache(maxsize=256)
def tag(txt):
    t = txt if len(txt) <= 10 else txt[:9] + "…"
    return L_("@" + t, 24, BLANC, NOIR, "mono", rough=1.2).v[0]

def draw_stand(L, fr, t, club, t0, cx, cy, s=1.0, step=.12, tags=True):
    """Tribune du club + ses supporters qui arrivent un par un (chute + écrasement), pseudo au-dessus de la tête."""
    st = stand_sprite(stand_col(club)); ax, ay = st.info["anchor"]
    blit_sxy(L, st, cx, cy, s, s, 0)
    fans = [p for p, c in FANS if c == club]
    pts = []
    for k, ps in enumerate(fans[:len(SEATS)]):
        r, i = SEATS[k]; x, y = seat_xy(r, i)
        pts.append((r, k, ps, cx + (x - ax)*s, cy + (y - ay)*s, i))
    for r, k, ps, x, y, ci in sorted(pts, key=lambda p: -p[0]):            # rang du fond dessiné d'abord
        a = t - (t0 + k*step)
        if a <= 0: continue
        fall = .22; yy = y - 500*s*(1 - min(1, a/fall)**2) if a < fall else y
        q = .14*math.exp(-(a - fall)*14)*math.cos((a - fall)*30) if a > fall else 0
        fs = fan_sprite(club, t + k*.37); kk = 430/fs.height*1.55*.62*s
        blit_sxy(L, fs, x, yy + 30*s, kk*(1 + q), kk*(1 - q), 0)
        if tags and a > fall:
            sg = M.spring(a - fall, .5, 14); blit_sxy(L, tag(ps), x, yy - 245*s - (ci % 2)*44*s - r*8*s, sg*s, sg*s, (-3, 2, -2, 3)[k % 4])

def club_head(L, fr, t, club, t0, x, y, n, size=110):
    u = M.spring(t - t0, .45, 13)
    if u <= 0: return
    blit_sxy(L, logo(club, 150), x - 250, y, u, u, -4)
    L_(f"{NAME[club]} · {n}", size, JAUNE, NOIR).draw(L, fr, x + 110, y, u, 2)

# ------------------------------------------------------------------ scènes
def s_intro(L, fr, t):
    rays(L, W/2, 1150, t, .06)
    L_("JOUR 2", 150, JAUNE, NOIR).draw(L, fr, W/2, 420, 1, -2)
    n = int(min(TOTAL, max(0, (t - .2)/(T["quarante"] + .6 - .2)*TOTAL)))
    L_(f"{n} SUPPORTERS", 96, NOIR, BLANC).draw(L, fr, W/2, 590, 1, 1.5)
    L_("ONT PRIS LEUR SIÈGE", 64, BLANC, NOIR).draw(L, fr, W/2, 700, 1, -1)
    # 40 sièges papier qui se colorent aux couleurs des clubs, dans l'ordre des commentaires
    d = ImageDraw.Draw(L); cols, w_, h_, gx, gy = 8, 104, 92, 540 - 4*118 + 59, 980
    for k, (_, c) in enumerate(FANS):
        x, y = gx + (k % cols)*118, gy + (k//cols)*120
        on = k < n; col = stand_col(c) if on else (70, 76, 100)
        pop = 1 + .25*math.exp(-max(0, t - (.2 + k/TOTAL*(T["quarante"] + .4)))*14) if on else 1
        ww, hh = w_*pop/2, h_*pop/2
        d.rounded_rectangle([x - ww, y - hh, x + ww, y - hh*.15], 10, fill=tuple(int(v*.82) for v in col))
        d.rounded_rectangle([x - ww, y - hh*.1, x + ww, y + hh*.55], 10, fill=col)
        if on and k in (0,) or (on and FANS[k][1] != FANS[k - 1][1] and k < 0): pass
    for k, (c, cnt) in enumerate(RANK[:6]):
        if n >= TOTAL: blit(L, logo(c, 110), 140 + k*160, 1680, M.spring(t - T["quarante"] - .7 - k*.08, .45, 14), 0)

def s_psg(L, fr, t):
    club_head(L, fr, t, "psg", T["psg"], W/2, 430, COUNT["psg"], 120)
    L_("ÉCRASE TOUT", 84, ROUGE, BLANC).draw(L, fr, W/2, 580, M.spring(t - T["psg"] - .5, .45, 14), -2)
    draw_stand(L, fr, t, "psg", T["psg"] + .15, W/2, 1560, 1.0, step=.13)
    grass(L)

def s_egal(L, fr, t):
    L_("ÉGALITÉ PARFAITE", 92, JAUNE, NOIR).draw(L, fr, W/2, 330, M.spring(t - T["egal"], .45, 14), -2)
    club_head(L, fr, t, "om", T["egal"] + .4, W/2, 520, COUNT["om"], 90)
    draw_stand(L, fr, t, "om", T["egal"] + .55, W/2, 1060, .62, step=.11)
    club_head(L, fr, t, "lens", T["egal"] + 1.0, W/2, 1220, COUNT["lens"], 90)
    draw_stand(L, fr, t, "lens", T["egal"] + 1.15, W/2, 1760, .62, step=.11)

def s_rennes(L, fr, t):
    club_head(L, fr, t, "rennes", T["rennes"], W/2, 400, COUNT["rennes"], 110)
    draw_stand(L, fr, t, "rennes", T["rennes"] + .15, W/2, 1230, .8, step=.12)
    L_("ET AUSSI…", 60, BLANC, NOIR).draw(L, fr, W/2, 1390, M.spring(t - T["rennes"] - .8, .45, 14), -2)
    rest = [(c, n) for c, n in RANK if c not in ("psg", "om", "lens", "rennes")]
    for k, (c, n) in enumerate(rest):
        x, y = 135 + (k % 5)*202, 1540 + (k//5)*190
        u = M.spring(t - T["rennes"] - .9 - k*.07, .45, 14)
        if u > 0:
            blit(L, logo(c, 120), x, y, u, 3*math.sin(t*2 + k))
            L_(str(n), 46, JAUNE, NOIR).draw(L, fr, x + 52, y + 46, u, 0)

def s_podium(L, fr, t):
    rays(L, W/2, 1100, t, .08)
    pd = podium_sprite(); px, py = W/2, 1500; ax, ay = pd.info["anchor"]
    blit_sxy(L, pd, px, py, 1, 1, 0)
    places = [["om", "lens"], ["psg"], ["rennes"]]                     # podium : 2e (gauche), 1er, 3e
    for i, (num, cl) in enumerate(zip(("2", "1", "3"), places)):
        x, y = podium_top(i); x += px - ax; y += py - ay
        L_(num, 120, BLANC, NOIR).draw(L, fr, x, y + 120, .9, 0)
        for j, c in enumerate(cl):
            u = M.spring(t - T["ton"] - (.25, 0, .45)[i] - j*.12, .45, 13)
            dx = (j - (len(cl) - 1)/2)*150
            blit(L, logo(c, 150 if len(cl) == 1 else 105), x + dx, y - 85 + 6*math.sin(t*4 + i + j), u, 0)
            if u > .5: L_(str(COUNT[c]), 44, JAUNE, NOIR).draw(L, fr, x + dx + 50, y - 30, u, 0)
    u = M.spring(t - T["ton"] - .6, .55, 9); x, y = podium_top(1); x += px - ax; y += py - ay
    blit_sxy(L, cup(int(t*12) % 24), x, y - 250 - 500*(1 - u), .55, .55, 0)
    L_("ET TON CLUB ?", 110, NOIR, BLANC).draw(L, fr, W/2, 380, M.spring(t - T["ton"], .45, 14), -2)
    L_("PAS ENCORE TON SIÈGE ?", 70, JAUNE, NOIR).draw(L, fr, W/2, 520, M.spring(t - T["ton"] - .9, .45, 14), 1.5)
    L_("COMMENTE TON CLUB", 66, BLANC, NOIR).draw(L, fr, W/2, 1660, M.spring(t - T["comm"], .45, 14), -1.5)
    b = M.spring(t - T["comm"] - .4, .45, 14); pul = 1 + .05*math.sin(t*12)
    L_("+ S'ABONNER", 70, ROUGE, BLANC).draw(L, fr, W/2, 1780, b*pul, 2)

def grass(L):
    d = ImageDraw.Draw(L); d.rectangle([0, 1660, W, H], fill=(52, 128, 70))
    for k in range(0, W, 120): d.rectangle([k, 1660, k + 60, H], fill=(60, 140, 78))
    d.rectangle([0, 1656, W, 1668], fill=(236, 236, 236))

def header(L, fr, t):
    L_(f"JOUR 2 · {TOTAL} SUPPORTERS", 40, NOIR, JAUNE, "mono", rough=1.5).draw(L, fr, W/2, 230, 1, 0)

def frame(fr, t):
    L = background().copy()
    if t < T["psg"]: s_intro(L, fr, t)
    elif t < T["egal"]: s_psg(L, fr, t)
    elif t < T["rennes"]: s_egal(L, fr, t)
    elif t < T["ton"]: s_rennes(L, fr, t)
    else: s_podium(L, fr, t)
    header(L, fr, t)
    for tc in (T["psg"], T["egal"], T["rennes"], T["ton"]):           # coupe papier brève entre les tableaux
        if tc - .05 < t < tc + .1:
            a = 1 - abs(t - tc)/.1; L.alpha_composite(Image.new("RGBA", (W, H), (250, 246, 234, int(190*max(0, a)))))
    return L.convert("RGB")

# ------------------------------------------------------------------ sons
def sfx_list():
    S = [(0, "braam", .7), (.05, "stamp", .6)] + [(.25 + k*(T["quarante"] + .35)/TOTAL, "tok", .2) for k in range(0, TOTAL, 2)] + [
         (T["quarante"] + .65, "ding", .5), (T["psg"] - .05, "page_tear", .5), (T["psg"] + .1, "crowd", .5)] + [
         (T["psg"] + .15 + k*.13 + .22, "thud", .3) for k in range(COUNT["psg"])] + [
         (T["egal"] - .05, "page_tear", .5), (T["egal"] + .05, "stamp", .7)] + [
         (T["egal"] + .55 + k*.11 + .22, "thud", .3) for k in range(5)] + [(T["egal"] + 1.15 + k*.11 + .22, "thud", .3) for k in range(5)] + [
         (T["rennes"] - .05, "page_tear", .5)] + [(T["rennes"] + .15 + k*.12 + .22, "thud", .3) for k in range(4)] + [
         (T["rennes"] + .9 + k*.07, "pop", .3) for k in range(9)] + [
         (T["ton"] - .05, "page_tear", .5), (T["ton"] + .1, "drumroll", .45), (T["ton"] + .7, "bang", .6), (T["ton"] + .75, "shimmer", .5),
         (T["comm"] + .4, "notif", .5), (T["comm"] + .45, "pop", .5)]
    return S

def render_all():
    v = VOICE
    if not os.path.exists(v):                                         # pas encore de voix : piste muette (même mixage)
        v = "/tmp/claude-0/silence.mp3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo", "-t", str(DUR), v], check=True)
    E.SFX, E.DUR, E.VOICE = sfx_list(), DUR, v
    out_dir = E.OUT; vid = os.path.join(out_dir, "_v2.mp4"); aud = os.path.join(out_dir, "_a2.m4a")
    E.mix_audio(aud)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", vid], stdin=subprocess.PIPE)
    for fr in range(int(DUR*FPS)): p.stdin.write(frame(fr, fr/FPS).tobytes())
    p.stdin.close(); p.wait()
    out = os.path.join(out_dir, "ep2.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", aud, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    os.remove(vid); os.remove(aud); return out

def stills():
    ts = [0, .9, 2.2, 3.9, 4.8, 5.9, 6.6, 7.6, 8.6, 9.6, 10.5, 11.4, 12.4, 14.5]
    sh = Image.new("RGB", (270*7, 480*2))
    for i, t in enumerate(ts): sh.paste(frame(int(t*FPS), t).resize((270, 480)), ((i % 7)*270, (i//7)*480))
    p = "/tmp/claude-0/sup2_sheet.jpg"; sh.save(p, quality=85); return p

if __name__ == "__main__":
    print(stills() if "--stills" in sys.argv else render_all())
