"""LA COUPE DES SUPPORTERS — match d'ouverture : Barça vs Real (le camp le plus commenté en 24 h gagne).
Voix Léo : voix/clasico.mp3 ; temps T calés sur la voix (faster-whisper).

  python3 episodes/supporters/clasico.py --stills
  python3 episodes/supporters/clasico.py
"""
import sys, os, math, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ep1 as E
from ep1 import (W, H, FPS, JAUNE, ROUGE, BLANC, NOIR, CREME, L_, logo, background, rays, stand_sprite, M, Image, ImageDraw, blit, blit_sxy, puff)

BARCA, REAL = (165, 0, 68), (0, 77, 152)
VOICE = os.path.join(HERE, "voix", "clasico.mp3")
T = dict(real=1.18, clasico=2.70, toi=4.16, vides=5.30, comm=6.82, b2=7.82, r2=8.76, camp=9.66, gagne=12.02, like=13.36, demain=15.16, end=17.3)
DUR = T["end"]

def side_bg(L, t, u):
    """Écran coupé en deux en diagonale : grenat à gauche, blanc/bleu à droite ; la séparation vibre."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    off = 30*math.sin(t*3)
    d.polygon([(0, 0), (W/2 + 140 + off, 0), (W/2 - 140 + off, H), (0, H)], fill=BARCA + (int(150*u),))
    d.polygon([(W/2 + 140 + off, 0), (W, 0), (W, H), (W/2 - 140 + off, H)], fill=(235, 238, 245, int(110*u)))
    L.alpha_composite(ov)

def crests(L, fr, t, y=900, gap=260):
    """Les deux écussons arrivent de chaque côté et s'entrechoquent (rebond + étincelles) sur « ou Real »."""
    a = t + .2; u = M.ease_out(min(1, a/.45))
    hit = T["real"] - .1
    xl = W/2 - gap - (1 - u)*700; xr = W/2 + gap + (1 - u)*700
    if t > hit:
        b = t - hit; k = 70*math.exp(-b*6)*math.cos(b*18)
        xl -= k; xr += k
    s = 1 + .04*math.sin(t*5)
    blit(L, logo("barca", 330), xl, y, s, -6 + 3*math.sin(t*2))
    blit(L, logo("real", 330), xr, y, s, 6 - 3*math.sin(t*2))
    L_("VS", 140, JAUNE, NOIR).draw(L, fr, W/2, y, M.spring(t - hit, .4, 15)*(1 + .06*math.sin(t*9)), -4)
    if hit < t < hit + .5:
        d = ImageDraw.Draw(L); b = (t - hit)/.5
        for k in range(14):
            ang = 2*math.pi*k/14; r = 60 + 300*b
            x, y2 = W/2 + r*math.cos(ang), y + r*math.sin(ang)
            d.ellipse([x - 12*(1 - b), y2 - 12*(1 - b), x + 12*(1 - b), y2 + 12*(1 - b)], fill=(255, 220, 90))

def stands(L, fr, t, y=1560, t_in=0):
    u = M.spring(t - t_in, .5, 10)
    for x, col, club, tl in ((W/4 + 10, BARCA, "barca", T["b2"]), (3*W/4 - 10, (245, 245, 250), "real", T["r2"])):
        st = stand_sprite(col); blit_sxy(L, st, x, y + (1 - u)*600, .5, .5, 0)
        blit(L, logo(club, 120), x, y - 300 + (1 - u)*600, 1 + .25*math.exp(-max(0, t - tl)*8)*(t > tl), 0)

def frame(fr, t):
    L = background().copy()
    side_bg(L, t, 1)
    rays(L, W/2, 900, t, .05)
    if t < T["vides"] - .1:
        crests(L, fr, t)
        L_("BARÇA OU REAL ?", 110, NOIR, BLANC).draw(L, fr, W/2, 430, 1, -2)
        if t > T["clasico"] - .1: L_("LE PLUS GRAND CLÁSICO", 74, JAUNE, NOIR).draw(L, fr, W/2, 1340, M.spring(t - T["clasico"] + .1, .45, 14), 2)
        if t > T["toi"] - .1: L_("C'EST TOI QUI DÉCIDES", 80, ROUGE, BLANC).draw(L, fr, W/2, 1480, M.spring(t - T["toi"] + .1, .45, 14), -2)
    elif t < T["like"] - .1:
        blit(L, logo("barca", 200), W/2 - 230, 560, 1, -5); blit(L, logo("real", 200), W/2 + 230, 560, 1, 5)
        L_("VS", 90, JAUNE, NOIR).draw(L, fr, W/2, 560, 1, -4)
        L_("TRIBUNES VIDES", 90, NOIR, BLANC).draw(L, fr, W/2, 360, M.spring(t - T["vides"], .45, 14), -2)
        stands(L, fr, t, t_in=T["vides"])
        if t > T["comm"] - .1: L_("COMMENTE TON CAMP", 86, JAUNE, NOIR).draw(L, fr, W/2, 820, M.spring(t - T["comm"] + .1, .45, 14), 2)
        if t > T["b2"] - .1: L_("BARÇA", 90, BARCA, BLANC).draw(L, fr, W/4 + 10, 980, M.spring(t - T["b2"] + .1, .45, 14), -4)
        if t > T["r2"] - .1: L_("REAL", 90, BLANC, REAL).draw(L, fr, 3*W/4 - 10, 980, M.spring(t - T["r2"] + .1, .45, 14), 4)
        if t > T["camp"] - .1:
            L_("+ DE COMMENTAIRES EN 24H", 62, NOIR, BLANC).draw(L, fr, W/2, 1120, M.spring(t - T["camp"] + .1, .45, 14), -1)
        if t > T["gagne"] - .1:
            L_("= GAGNE LE CLÁSICO", 80, ROUGE, BLANC).draw(L, fr, W/2, 1240, M.spring(t - T["gagne"] + .1, .45, 14), 2)
    else:
        crests(L, fr, t - T["like"] + 2, y=820, gap=230)
        L_("RÉSULTAT DEMAIN", 100, JAUNE, NOIR).draw(L, fr, W/2, 430, M.spring(t - T["demain"] + .2, .45, 14), -2)
        L_("COMMENTE TON CAMP", 72, NOIR, BLANC).draw(L, fr, W/2, 1320, 1, 1)
        L_("+ S'ABONNER", 76, ROUGE, BLANC).draw(L, fr, W/2 - 190, 1480, M.spring(t - T["like"] - .3, .45, 14)*(1 + .05*math.sin(t*12)), 2)
        L_("LIKE", 76, (235, 40, 90), BLANC).draw(L, fr, W/2 + 220, 1480, M.spring(t - T["like"], .45, 14)*(1 + .05*math.sin(t*12 + 1)), -2)
    L_("LA COUPE DES SUPPORTERS · MATCH 1", 38, NOIR, JAUNE, "mono", rough=1.5).draw(L, fr, W/2, 230, 1, 0)
    for tc in (T["vides"], T["like"]):
        if tc - .15 < t < tc: L.alpha_composite(Image.new("RGBA", (W, H), (250, 246, 234, int(190*(1 - (tc - t)/.15)))))
    return L.convert("RGB")

def sfx_list():
    return [(0, "braam", .7), (0, "whoosh1", .5), (T["real"] - .1, "bang", .8), (T["real"] - .05, "crowd", .5), (T["clasico"] - .15, "stamp", .6),
            (T["toi"] - .15, "stamp", .6), (T["vides"] - .15, "page_tear", .5), (T["vides"] + .1, "wind", .5), (T["comm"] - .15, "pop", .5),
            (T["b2"] - .1, "tok", .6), (T["r2"] - .1, "tok", .6), (T["gagne"] - .15, "stamp", .7), (T["like"] - .15, "page_tear", .5),
            (T["like"] + .1, "pop", .5), (T["demain"] - .2, "ding", .5), (T["demain"] + .4, "notif", .5)]

def render_all():
    E.SFX, E.DUR, E.VOICE = sfx_list(), DUR, VOICE
    vid = os.path.join(E.OUT, "_vc.mp4"); aud = os.path.join(E.OUT, "_ac.m4a"); E.mix_audio(aud)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", vid], stdin=subprocess.PIPE)
    for fr in range(int(DUR*FPS)): p.stdin.write(frame(fr, fr/FPS).tobytes())
    p.stdin.close(); p.wait()
    out = os.path.join(E.OUT, "clasico.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", aud, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    os.remove(vid); os.remove(aud); return out

def stills():
    ts = [0, .5, 1.4, 3.0, 4.5, 6.0, 7.5, 9.0, 11.0, 12.5, 14.0, 16.5]
    sh = Image.new("RGB", (270*6, 480*2))
    for i, t in enumerate(ts): sh.paste(frame(int(t*FPS), t).resize((270, 480)), ((i % 6)*270, (i//6)*480))
    p = "/tmp/claude-0/clasico_sheet.jpg"; sh.save(p, quality=85); return p

if __name__ == "__main__":
    print(stills() if "--stills" in sys.argv else render_all())
