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
