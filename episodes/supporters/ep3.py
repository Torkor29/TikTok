"""LE STADE DES SUPPORTERS — épisode 3 : on relance, classement PAR SEMAINE + résultats de la semaine 1 (semaine1.json).
Hook : « le club avec le plus de supporters c'est… je te le donne à la fin » -> relance hebdo -> résultats du bas vers le haut -> PSG.
Voix Léo : voix/ep3.mp3 (temps relevés au mot près avec faster-whisper).

  python3 episodes/supporters/ep3.py --stills
  python3 episodes/supporters/ep3.py
"""
import sys, os, math, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ep1 as E
import ep2 as P
from ep1 import (W, H, FPS, JAUNE, ROUGE, BLANC, NOIR, CREME, L_, logo, background, rays, podium_sprite, podium_top, cup, M, Image, ImageDraw,
                 blit, blit_sxy)

DATA = json.load(open(os.path.join(HERE, "semaine1.json")))
P.FANS = DATA["supporters"]
P.COUNT = {}
for _, c in P.FANS: P.COUNT[c] = P.COUNT.get(c, 0) + 1
COUNT = P.COUNT; TOTAL = len(P.FANS)
P.NAME.update(troyes="TROYES", lorient="LORIENT", nice="NICE")
VOICE = os.path.join(HERE, "voix", "ep3.mp3")
T = dict(attends=2.6, fin=4.0, relance=5.9, semaine=7.8, comm=8.7, abo=9.6, res=11.7, n92=13.0, tou=14.7, brest=16.4, om=19.5,
         fans=21.4, psg=23.2, ton=25.4, comm2=27.1, end=30.8)
DUR = T["end"]

def hook(L, fr, t):
    rays(L, W/2, 1250, t, .06)
    pd = podium_sprite(); px, py = W/2, 1560; ax, ay = pd.info["anchor"]; blit_sxy(L, pd, px, py, 1, 1, 0)
    for i in range(3):
        x, y = podium_top(i); x += px - ax; y += py - ay
        L_(("2", "1", "3")[i], 120, BLANC, NOIR).draw(L, fr, x, y + 120, .9, 0)
        L_("?", 110, CREME, NOIR).draw(L, fr, x, y - 85 + 6*math.sin(t*5 + i), 1, (-6, 4, 6)[i])
    x, y = podium_top(1); x += px - ax; y += py - ay
    blit_sxy(L, cup(int(t*12) % 24), x, y - 260 + 6*math.sin(t*3), .6, .6, 0)
    L_("LE CLUB AVEC LE PLUS", 84, NOIR, BLANC).draw(L, fr, W/2, 400, 1, -2)
    L_("DE SUPPORTERS EST…", 96, JAUNE, NOIR).draw(L, fr, W/2, 520, 1, 1.5)
    if t > T["attends"]:
        L_("RÉPONSE À LA FIN 👀" if False else "RÉPONSE À LA FIN", 92, ROUGE, BLANC).draw(L, fr, W/2, 680, M.spring(t - T["attends"], .45, 14), -3)

def relance(L, fr, t):
    rays(L, W/2, 1100, t, .07)
    L_("ON RELANCE !", 130, JAUNE, NOIR).draw(L, fr, W/2, 420, M.spring(t - T["relance"] + .3, .45, 14), -2)
    if t > T["semaine"] - .2:
        s = M.spring(t - T["semaine"] + .2, .45, 14)
        L_("7 JOURS POUR PARTICIPER", 74, NOIR, BLANC).draw(L, fr, W/2, 570, s, 1.5)
        # calendrier papier : 7 jours qui se cochent
        d = ImageDraw.Draw(L)
        for k, j in enumerate("LMMJVSD"):
            x, y = 150 + k*130, 820; u = M.spring(t - T["semaine"] - k*.08, .45, 14)
            if u <= 0: continue
            w = 52*u; d.rounded_rectangle([x - w, y - w*1.2, x + w, y + w*1.2], 12, fill=CREME)
            d.rectangle([x - w, y - w*1.2, x + w, y - w*.6], fill=ROUGE)
            d.text((x, y + 10), j, font=E.font("title", int(60*u) + 1), fill=NOIR, anchor="mm")
    if t > T["comm"] - .2:
        L_("1. COMMENTE TON CLUB", 76, BLANC, NOIR).draw(L, fr, W/2, 1100, M.spring(t - T["comm"] + .2, .45, 14), -2)
    if t > T["abo"] - .2:
        pul = 1 + .05*math.sin(t*12)
        L_("2. + ABONNE-TOI", 80, ROUGE, BLANC).draw(L, fr, W/2, 1260, M.spring(t - T["abo"] + .2, .45, 14)*pul, 2)
        L_("= TON SIÈGE COMPTE", 66, JAUNE, NOIR).draw(L, fr, W/2, 1420, M.spring(t - T["abo"] - .6, .45, 14), -1)

def total(L, fr, t):
    L_("RÉSULTATS 24H", 110, JAUNE, NOIR).draw(L, fr, W/2, 400, 1, -2)
    n = int(min(TOTAL, max(0, (t - T["n92"] + .5)/1.0*TOTAL)))
    L_(f"{n} SUPPORTERS", 104, NOIR, BLANC).draw(L, fr, W/2, 560, 1, 1.5)
    d = ImageDraw.Draw(L); cols = 12
    for k, (_, c) in enumerate(P.FANS):
        x, y = 540 - 5.5*80 + (k % cols)*80, 760 + (k//cols)*90
        on = k < n; col = P.stand_col(c) if on else (70, 76, 100)
        d.rounded_rectangle([x - 32, y - 30, x + 32, y - 4], 8, fill=tuple(int(v*.82) for v in col))
        d.rounded_rectangle([x - 32, y, x + 32, y + 26], 8, fill=col)

def duo(L, fr, t, a, b, t0, title):
    L_(title, 86, JAUNE, NOIR).draw(L, fr, W/2, 330, M.spring(t - t0 + .1, .45, 14), -2)
    P.club_head(L, fr, t, a, t0, W/2, 500, COUNT[a], 86)
    P.draw_stand(L, fr, t, a, t0 + .15, W/2, 1050, .62, step=.1)
    P.club_head(L, fr, t, b, t0 + .5, W/2, 1220, COUNT[b], 86)
    P.draw_stand(L, fr, t, b, t0 + .65, W/2, 1760, .62, step=.1)

def solo(L, fr, t, c, t0, title, extra=None):
    if title: L_(title, 92, JAUNE, NOIR).draw(L, fr, W/2, 330, M.spring(t - t0 + .1, .45, 14), -2)
    P.club_head(L, fr, t, c, t0, W/2, 500, COUNT[c], 110)
    P.draw_stand(L, fr, t, c, t0 + .15, W/2, 1560, 1.0, step=.09)
    P.grass(L)
    if extra: extra(L, fr, t)

def psg_scene(L, fr, t):
    if t < T["psg"] - .05:
        rays(L, W/2, 1000, t, .1)
        L_("LE CLUB AVEC LE PLUS", 84, NOIR, BLANC).draw(L, fr, W/2, 600, 1, -2)
        L_("DE FANS…", 140, JAUNE, NOIR).draw(L, fr, W/2, 760, 1 + .04*math.sin(t*10), 1.5)
        L_("?", 300, CREME, NOIR).draw(L, fr, W/2, 1200, 1 + .06*math.sin(t*14), 6*math.sin(t*9))
        return
    rays(L, W/2, 900, t, .16)
    solo(L, fr, t, "psg", T["psg"], "N°1 EN 24H")

def final(L, fr, t):
    rays(L, W/2, 1100, t, .08)
    pd = podium_sprite(); px, py = W/2, 1480; ax, ay = pd.info["anchor"]; blit_sxy(L, pd, px, py, 1, 1, 0)
    for i, cl in enumerate((["om"], ["psg"], ["brest", "lens"])):
        x, y = podium_top(i); x += px - ax; y += py - ay
        L_(("2", "1", "3")[i], 120, BLANC, NOIR).draw(L, fr, x, y + 120, .9, 0)
        for j, c in enumerate(cl):
            dx = (j - (len(cl) - 1)/2)*140
            blit(L, logo(c, 140 if len(cl) == 1 else 105), x + dx, y - 85 + 6*math.sin(t*4 + i + j), M.spring(t - T["ton"] - j*.1, .45, 13), 0)
            L_(str(COUNT[c]), 44, JAUNE, NOIR).draw(L, fr, x + dx + 50, y - 30, 1, 0)
    x, y = podium_top(1); x += px - ax; y += py - ay
    blit_sxy(L, cup(int(t*12) % 24), x, y - 250, .55, .55, 0)
    L_("TON CLUB N'EST PAS LÀ ?", 78, NOIR, BLANC).draw(L, fr, W/2, 400, M.spring(t - T["ton"], .45, 14), -2)
    L_("COMMENTE TON CLUB", 70, JAUNE, NOIR).draw(L, fr, W/2, 1660, M.spring(t - T["comm2"], .45, 14), -1.5)
    L_("+ S'ABONNER", 72, ROUGE, BLANC).draw(L, fr, W/2, 1780, M.spring(t - T["comm2"] - .4, .45, 14)*(1 + .05*math.sin(t*12)), 2)
    if t > T["comm2"] + 1.2: L_("7 JOURS : TOUT PEUT CHANGER", 56, BLANC, NOIR).draw(L, fr, W/2, 540, M.spring(t - T["comm2"] - 1.2, .45, 14), 1)

SCENES = [(0, hook), (T["fin"] + .4, relance), (T["res"] - .1, total), (T["tou"] - .1, lambda L, fr, t: duo(L, fr, t, "toulouse", "angers", T["tou"], "6 CHACUN")),
          (T["brest"] - .1, lambda L, fr, t: duo(L, fr, t, "brest", "lens", T["brest"] + .9, "3e : ÉGALITÉ")),
          (T["om"] - .1, lambda L, fr, t: solo(L, fr, t, "om", T["om"] + .6, "2e")), (T["fans"] - .1, psg_scene), (T["ton"] - .1, final)]

def frame(fr, t):
    L = background().copy()
    k = max(i for i, (t0, _) in enumerate(SCENES) if t >= t0); SCENES[k][1](L, fr, t)
    L_("SESSION 24H · RÉSULTATS" if t >= T["res"] - .1 else "NOUVELLE SESSION : 7 JOURS", 40, NOIR, JAUNE, "mono", rough=1.5).draw(L, fr, W/2, 230, 1, 0)
    for t0, _ in SCENES[1:]:
        if t0 - .05 < t < t0 + .1: L.alpha_composite(Image.new("RGBA", (W, H), (250, 246, 234, int(190*max(0, 1 - abs(t - t0)/.1)))))
    return L.convert("RGB")

def sfx_list():
    S = [(0, "braam", .7), (0, "drumroll", .4), (T["attends"] - .1, "stamp", .7), (T["fin"] + .35, "page_tear", .5), (T["relance"] - .3, "stamp", .7)] + [
         (T["semaine"] + k*.08, "tok", .3) for k in range(7)] + [(T["comm"] - .2, "pop", .5), (T["abo"] - .2, "ding", .5),
         (T["res"] - .15, "page_tear", .5), (T["n92"] - .4, "drumroll", .4), (T["n92"] + .55, "ding", .5)] + [
         (T["tou"] - .1, "page_tear", .5)] + [(T["tou"] + .15 + k*.1 + .22, "thud", .3) for k in range(6)] + [
         (T["brest"] - .1, "page_tear", .5), (T["brest"] + .8, "stamp", .6)] + [(T["brest"] + 1.05 + k*.1 + .22, "thud", .3) for k in range(8)] + [
         (T["om"] - .1, "page_tear", .5), (T["om"] + .5, "stamp", .6), (T["om"] + .8, "crowd", .5), (T["fans"] - .1, "page_tear", .5),
         (T["fans"] + .1, "riser", .5), (T["psg"] - .1, "bang", .7), (T["psg"], "crowd", .7), (T["psg"] + .05, "shimmer", .5)] + [
         (T["psg"] + .15 + k*.09 + .22, "thud", .25) for k in range(20)] + [(T["ton"] - .1, "page_tear", .5), (T["comm2"] + .4, "notif", .5)]
    return S

def render_all():
    E.SFX, E.DUR, E.VOICE = sfx_list(), DUR, VOICE
    vid = os.path.join(E.OUT, "_v3.mp4"); aud = os.path.join(E.OUT, "_a3.m4a"); E.mix_audio(aud)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", vid], stdin=subprocess.PIPE)
    for fr in range(int(DUR*FPS)): p.stdin.write(frame(fr, fr/FPS).tobytes())
    p.stdin.close(); p.wait()
    out = os.path.join(E.OUT, "ep3.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", aud, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    os.remove(vid); os.remove(aud); return out

def stills():
    ts = [0, 3.2, 6.5, 10.3, 12.4, 13.8, 15.6, 17.9, 20.5, 22.5, 23.8, 24.9, 26.5, 29.5]
    sh = Image.new("RGB", (270*7, 480*2))
    for i, t in enumerate(ts): sh.paste(frame(int(t*FPS), t).resize((270, 480)), ((i % 7)*270, (i//7)*480))
    p = "/tmp/claude-0/sup3_sheet.jpg"; sh.save(p, quality=85); return p

if __name__ == "__main__":
    print(stills() if "--stills" in sys.argv else render_all())
