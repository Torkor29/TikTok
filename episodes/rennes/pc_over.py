"""Remplace les assets plats de Rennes par les volumes papercraft low-poly (engine/pc_lib.py), mêmes signatures/ancres."""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import pc_lib as PC
from engine import blit_sxy

def fit(sp, w=None, h=None, anchor="center", keep_anchor=False):
    """Recadre au contenu et met à l'échelle (largeur ou hauteur cible). anchor : center | bottom | topleft | src."""
    bb = sp.getchannel("A").point(lambda v: 255 if v > 2 else 0).getbbox()
    ax0, ay0 = sp.info.get("anchor", (0, 0))
    im = sp.crop(bb); k = (w/im.width) if w else (h/im.height)
    im = im.resize((max(1, int(im.width*k)), max(1, int(im.height*k))), Image.LANCZOS)
    if anchor == "center": im.info["anchor"] = (im.width/2, im.height/2)
    elif anchor == "bottom": im.info["anchor"] = (im.width/2, im.height*.94)
    elif anchor == "topleft": im.info["anchor"] = (0, 0)
    else: im.info["anchor"] = ((ax0 - bb[0])*k, (ay0 - bb[1])*k)
    return im

def rim(sp, col=(150, 140, 165), wd=4):
    """Liseré clair autour d'un objet sombre (lisible sur fond sombre)."""
    a = sp.getchannel("A").point(lambda v: 255 if v > 200 else 0).filter(ImageFilter.MaxFilter(wd*2 + 1))
    out = Image.new("RGBA", sp.size, col + (0,)); out.putalpha(a.point(lambda v: int(v*.85)))
    out.alpha_composite(sp); out.info["anchor"] = sp.info["anchor"]; return out

def label(sp, txt, y_frac, size, font):
    d = ImageDraw.Draw(sp); f = font("title", size); tw = f.getlength(txt)
    cx, cy = sp.width/2 - sp.width*.03, sp.height*y_frac
    d.rectangle([cx - tw/2 - 18, cy - size*.7, cx + tw/2 + 18, cy + size*.7], fill=(250, 248, 240))
    d.text((cx, cy), txt, font=f, fill=(24, 22, 26), anchor="mm"); return sp

def install(G):
    font = G["font"]; foot = G["foot"]
    c = {}
    def once(key, fn):
        if key not in c: c[key] = fn()
        return c[key]
    G["door"] = lambda txt="LIGUE": once(("door", txt), lambda: label(fit(PC.obj_sprite("door", 700, yaw=-.25, pitch=.12), h=760), txt, .16, 60, font))
    G["crown"] = lambda: once("crown", lambda: fit(PC.obj_sprite("crown", 500, yaw=0, pitch=.35), w=280))
    G["boater"] = lambda: once("boater", lambda: fit(PC.obj_sprite("boater", 400, yaw=0, pitch=.3), w=210))
    G["tractor"] = lambda: once("tractor", lambda: fit(PC.obj_sprite("tractor", 600, yaw=-.2, pitch=.18), w=440, anchor="bottom"))
    G["tent"] = lambda: once("tent", lambda: fit(PC.obj_sprite("tent", 600, yaw=-.5, pitch=.25), w=470))
    G["house"] = lambda: once("house", lambda: fit(PC.obj_sprite("house", 600, yaw=-.45, pitch=.25), w=430))
    G["red_card"] = lambda: once("card", lambda: fit(PC.obj_sprite("card", 500, yaw=-.35, pitch=.1), h=300))
    G["closet"] = lambda: once("closet", lambda: label(fit(PC.obj_sprite("closet", 700, yaw=-.35, pitch=.15), h=640), "PLACARD", .2, 42, font))
    G["cup_gold"] = lambda h=420: once(("cup", h), lambda: fit(PC.cup_sprite(-.35, 600), h=h))
    @lru_cache(maxsize=16)
    def heart_(r, col):
        sp = PC.render(PC.heart_parts(col), 500, yaw=-.25, pitch=.1, scale=500/2.8, center=(0, 0, 0), shadow=False)
        return fit(sp, w=2.1*r)
    G["heart"] = lambda r=120, col=(240, 40, 80): heart_(int(r), tuple(col))
    def flag_civ(cv, x, y, t, s=1.0):
        ph = round((t*6 % (2*math.pi))/(2*math.pi)*12)/12*2*math.pi/6
        sp = once(("flag", ph), lambda: fit(PC.obj_sprite("flag", 600, yaw=-.35, pitch=.12, phase=ph), h=340, anchor="topleft"))
        blit_sxy(cv, sp, x - 8*s, y - 18*s, s, s, 0)
    G["flag_civ"] = flag_civ
    # ballon : rotation quantifiée sur 16 pas
    def draw_ball(cv, fr, x, y, s=1.0, rot=0.0, alpha=1.0):
        q = round((rot/57.3 % (2*math.pi))/(2*math.pi)*16) % 16
        sp = once(("ball", q), lambda: fit(PC.ball_sprite(q/16*2*math.pi, 240), w=112))
        blit_sxy(cv, sp, x, y, s, s, 0, alpha)
    foot.draw_ball = draw_ball
    def draw_goal(cv, fr, x, y, w=420, h=240, net_u=0.0, alpha=1.0, t=0.0):
        sp = PC.goal_sprite(1000); k = w/(7.3*1000/8.4*.98)
        blit_sxy(cv, sp, x, y, k, k, 0, alpha)
    foot.draw_goal = draw_goal
    foot.Player = lambda name="p", hair=(50, 36, 28), skin=(224, 178, 140), hair_style="short", beard_col=None, **kw: \
        PC.PCPlayer(name, hair, skin, "bald" if hair_style == "bald" else "short", beard_col)
    def draw_cat(L, x, y, t, s=1.0, moving=True, face=1):
        ph = round(((t*9) % (2*math.pi))/(2*math.pi)*12) % 12 if moving else 0
        tq = ph/12*2*math.pi/9
        key = ("cat", ph, moving, face)
        def mk():
            sp = PC.cat_sprite((44, 40, 48), (14, 12, 16), tq, 1.0 if moving else 0.0, 1.32*face, 520)
            return rim(fit(sp, w=330, anchor="bottom"))
        sp = once(key, mk)
        bob = -4*abs(math.sin(t*9)) if moving else 0
        blit_sxy(L, sp, x, y + bob, s, s, 0)
    G["draw_cat"] = draw_cat

# ------------------------------------------------------------------ v4 : socle 3D, toile d'araignée, flammes, joueurs en photo-papier
def stand_parts():
    from papercraft import Part, cbox
    def p_plaque(P, c):
        m = (P[:, 2] > 0) & (np.abs(P[:, 0]) < .55) & (np.abs(P[:, 1]) < .22); c[m] = PC.C((206, 160, 60)); return c
    def p_top(P, c):                                                   # cercle de poussière là où était le trophée
        r = np.hypot(P[:, 0], P[:, 2]); m = (P[:, 1] > .1) & (np.abs(r - .42) < .05); c[m] = c[m]*.75; return c
    return [Part(cbox(1.9, .35, 1.5, .12), (70, 46, 34), None, (0, .175, 0), name="b0"),
            Part(cbox(1.35, 2.2, 1.05, .1), (110, 74, 52), p_plaque, (0, 1.45, 0), name="col"),
            Part(cbox(1.7, .25, 1.35, .14), (84, 56, 40), p_top, (0, 2.68, 0), name="top")]

def cobweb_nice(cv, x, y, r, u, col=(236, 236, 236)):
    """Toile d'araignée réaliste : rayons + fils qui pendent (courbes), fils fins semi-transparents, gouttes."""
    if u <= 0 or r < 4: return
    S = 2; rr = r*u; sz = int(rr*1.15*S) + 8
    ov = Image.new("RGBA", (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    n = 8; ang = [math.pi/2*k/(n - 1) for k in range(n)]; cl = col + (190,)
    for a in ang: d.line([(0, 0), (rr*S*math.cos(a), rr*S*math.sin(a))], fill=cl, width=2*S//2 + 1)
    for ring in range(1, 7):
        rk = rr*S*ring/6.4
        for i in range(n - 1):
            a0, a1 = ang[i], ang[i + 1]; p0 = (rk*math.cos(a0), rk*math.sin(a0)); p1 = (rk*math.cos(a1), rk*math.sin(a1))
            mid = ((p0[0] + p1[0])/2*.86, (p0[1] + p1[1])/2*.86)           # le fil pend vers le centre
            pts = [((1 - s)**2*p0[0] + 2*(1 - s)*s*mid[0] + s*s*p1[0], (1 - s)**2*p0[1] + 2*(1 - s)*s*mid[1] + s*s*p1[1]) for s in np.linspace(0, 1, 9)]
            d.line(pts, fill=col + (150,), width=S)
            if (ring*7 + i) % 5 == 0: d.ellipse([mid[0] - 3*S, mid[1] - 3*S, mid[0] + 3*S, mid[1] + 3*S], fill=(255, 255, 255, 210))
    ov = ov.resize((sz//S, sz//S), Image.LANCZOS)
    if x > cv.width/2: ov = ov.transpose(Image.FLIP_LEFT_RIGHT); cv.alpha_composite(ov, (int(x - ov.width), int(y))) if cv.mode == "RGBA" else cv.paste(ov, (int(x - ov.width), int(y)), ov)
    else: cv.alpha_composite(ov, (int(x), int(y))) if cv.mode == "RGBA" else cv.paste(ov, (int(x), int(y)), ov)

def flames_nice(cv, x, y, t, s=1.0, n=5):
    """Flammes en papier : langues en goutte (rouge > orange > jaune) qui ondulent, base posée en y."""
    ov = Image.new("RGBA", cv.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for k in range(n):
        ph = t*8 + k*2.1; xx = x + (k - (n - 1)/2)*34*s; hk = (110 + 40*math.sin(ph) + 20*math.sin(ph*2.3))*s*(1.2 - .35*abs(k - (n - 1)/2)/max(1, n/2))
        for col, sc in (((214, 40, 24), 1.0), ((250, 130, 30), .74), ((255, 214, 80), .45)):
            w_ = 34*s*sc; h_ = hk*sc; pts = []
            for i in range(17):
                v = i/16; wv = math.sin(math.pi*v)**.8*w_*(1 - v*.55)
                sway = 10*s*math.sin(ph*1.3 + v*3)*v
                pts.append((xx - wv + sway, y - h_*v))
            for i in range(16, -1, -1):
                v = i/16; wv = math.sin(math.pi*v)**.8*w_*(1 - v*.55); sway = 10*s*math.sin(ph*1.3 + v*3)*v
                pts.append((xx + wv + sway, y - h_*v))
            d.polygon(pts, fill=col + (235,))
    if cv.mode == "RGBA": cv.alpha_composite(ov)
    else: cv.paste(ov, (0, 0), ov)

def install_v4(G):
    import sys, os
    sys.path.insert(0, os.path.join(G["ROOT"], "engine"))
    from paper_cut import paper_player
    U = "/root/.claude/uploads/0adb781c-170c-5099-95c1-9e411610d456/"
    c = {}
    def once(key, fn):
        if key not in c: c[key] = fn()
        return c[key]
    G["scale_stand"] = lambda: once("stand", lambda: fit(PC.render(stand_parts(), 700, yaw=-.45, pitch=.22, scale=700/3.6, center=(0, 1.4, 0), shadow_a=70), h=560))
    G["cobweb"] = cobweb_nice
    G["flames"] = flames_nice
    G["CAMA_CUT"] = lambda h=900: once(("cama", h), lambda: paper_player(U + "4d332df9-image.png", (400, 850, 1100, 1715), h))
    G["BA_CUT"] = lambda h=560: once(("ba", h), lambda: paper_player(U + "6062cc1e-image.png", (190, 905, 1000, 1660), h))
    def sepia(sp):
        r, g, b, a = sp.split(); l = Image.merge("RGB", (r, g, b)).convert("L")
        s_ = Image.merge("RGB", (l.point(lambda v: min(255, int(v*1.0 + 30))), l.point(lambda v: int(v*.9 + 18)), l.point(lambda v: int(v*.72 + 10))))
        out = s_.convert("RGBA"); out.putalpha(a); out.info["anchor"] = sp.info["anchor"]; return out
    G["CAMA_KID"] = lambda: once("camakid", lambda: sepia(paper_player(U + "4d332df9-image.png", (400, 850, 1100, 1715), 900)))
