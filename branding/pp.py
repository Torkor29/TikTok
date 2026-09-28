"""Photo de profil du compte « Foot Découpé » (1080x1080, lisible en rond et en tout petit).
Un ballon en papier découpé, une ligne de découpe en pointillés et une paire de ciseaux, dans l'identité de la série.
Lancer : python3 branding/pp.py
"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "engine"))
import engine
from engine import *

S = 1080; C = S // 2

def big_ball(r, key):
    """Ballon en papier de rayon r (le BALL du kit foot est trop petit pour être agrandi proprement)."""
    def dec(d, a):
        ax, ay = a; k = r/52
        pent = [(ax+17*k*math.cos(-math.pi/2+i*2*math.pi/5), ay+17*k*math.sin(-math.pi/2+i*2*math.pi/5)) for i in range(5)]
        d.polygon(pent, fill=PAL["ink"])
        for i in range(5):
            an = -math.pi/2 + i*2*math.pi/5
            cx, cy = ax+44*k*math.cos(an), ay+44*k*math.sin(an)
            d.polygon([(cx+13*k*math.cos(an+math.pi+j*2*math.pi/5), cy+13*k*math.sin(an+math.pi+j*2*math.pi/5)) for j in range(5)], fill=PAL["ink"])
            d.line([pent[i], (ax+31*k*math.cos(an), ay+31*k*math.sin(an))], fill=PAL["ink"], width=int(4*k))
        d.ellipse([ax-r*.62, ay-r*.72, ax-r*.28, ay-r*.46], fill=(255, 255, 250))   # reflet
    return Paper(ellipse_pts(2*r, 2*r, 72), (252, 250, 244), key, rough=3, pad=40).add(dec)

def ring(rx, ry, th, col, key):
    """Anneau de ciseaux en papier : ellipse évidée (vrai trou transparent)."""
    P = Paper(ellipse_pts(2*rx, 2*ry, 40), col, key, rough=2.2, hatch=True)
    for im in P.v:
        ax, ay = im.info["anchor"]
        hole = Image.new("L", im.size, 0)
        ImageDraw.Draw(hole).ellipse([ax-rx+th, ay-ry+th, ax+rx-th, ay+ry-th], fill=255)
        im.putalpha(ImageChops.subtract(im.getchannel("A"), hole))
    return P

def scissors(cv, x, y, ang, s=1.0):
    """Ciseaux ouverts, pointe vers (cos ang, sin ang)."""
    L = layer(900, 900, (450, 450))
    blade = Paper([(0, -36), (390, -8), (420, 0), (390, 12), (0, 36)], (206, 210, 216), "blade", rough=1.4, pad=30)
    blade.add(lambda d, a: d.line([(a[0]+24, a[1]-6), (a[0]+380, a[1]-2)], fill=(240, 242, 246), width=7))
    handle = ring(92, 70, 32, PAL["mustard"], "handle")
    dl = ImageDraw.Draw(L)
    for sg in (-1, 1):
        rot = sg*14
        blade.draw(L, 0, 450, 450, 1, rot, 1, 0)
        a = math.radians(-rot); hx, hy = 450 - 120*math.cos(a) - 60, 450 - 120*math.sin(a) - sg*6 + sg*80
        ux, uy = 450 - hx, 450 - hy; n = math.hypot(ux, uy); ux, uy = ux/n, uy/n
        dl.line([(450, 450), (hx + ux*84, hy + uy*60)], fill=PAL["mustard"], width=36)     # bras qui relie l'anneau au pivot
        handle.draw(L, 0, hx, hy, 1, rot*1.5, 1, 0)
    ImageDraw.Draw(L).ellipse([434, 434, 466, 466], fill=(70, 74, 80))
    blit(cv, L, x, y, s, -math.degrees(ang), 1)

def make(path):
    # fond : papier corail + rayons
    bg = Paper(rect_pts(S+80, S+80), PAL["coral"], "ppbg", rough=0.5, shadow=False, outline=False)
    cv = Image.new("RGB", (S, S), PAL["coral"])
    bg.draw(cv, 0, C, C, 1, 0, 1, 0)
    ov = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for k in range(16):
        an = k*2*math.pi/16 + .1
        d.polygon([(C, C), (C+900*math.cos(an-.1), C+900*math.sin(an-.1)), (C+900*math.cos(an+.1), C+900*math.sin(an+.1))], fill=(246, 150, 120, 110))
    cv.paste(ov, (0, 0), ov)
    # ligne de découpe en pointillés
    d = ImageDraw.Draw(cv); R = 372
    for k in range(44):
        a0 = k*2*math.pi/44; a1 = a0 + math.pi/44*1.1
        pencil_line(d, [(C+R*math.cos(a0+j*(a1-a0)/6), C+R*math.sin(a0+j*(a1-a0)/6)) for j in range(7)], 1, PAL["ink"], 11, k, 1.2)
    # le ballon
    big_ball(300, "ppball").draw(cv, 0, C, C+6, 1, -14, 1, 0)
    # les ciseaux qui découpent la ligne (haut droite)
    ang = math.radians(-42)
    scissors(cv, C + (R-30)*math.cos(ang), C + (R-30)*math.sin(ang) + 30, ang + math.pi/2 + .25, .8)
    cv.save(path, quality=95)
    # aperçu en rond, taille réelle sur TikTok
    m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse([0, 0, S-1, S-1], fill=255)
    prev = Image.new("RGB", (S + 120, S + 120), (255, 255, 255)); prev.paste(cv, (60, 60), m)
    small = prev.resize((200, 200), Image.LANCZOS)
    sheet = Image.new("RGB", (S + 120 + 260, S + 120), (255, 255, 255)); sheet.paste(prev, (0, 0)); sheet.paste(small, (S + 150, 60))
    sheet.save(path.replace(".png", "_apercu.jpg"), quality=90)
    return path

if __name__ == "__main__":
    print(make(os.path.join(HERE, "pp_foot_decoupe.png")))
