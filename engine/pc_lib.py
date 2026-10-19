"""Bibliothèque papercraft low-poly pour toutes les vidéos foot : joueur, ballon, coupe, cages, objets.
Tout est rendu par engine/papercraft.render puis mis en cache (poses quantifiées) -> sprites RGBA avec ancre au sol."""
import math
from functools import lru_cache
import numpy as np
from PIL import Image
try:
    from engine.papercraft import Part, cbox, pyramid, prism, rot, speckle, capsule, render, lathe, icosphere
except ImportError:
    from papercraft import Part, cbox, pyramid, prism, rot, speckle, capsule, render, lathe, icosphere
try:
    from engine.pc_assets import cat, cat_anim, _sym, DARK, WHITE
except ImportError:
    from pc_assets import cat, cat_anim, _sym, DARK, WHITE

def C(rgb): return np.array(rgb, float)/255
GOLD = (222, 172, 52); WOOD = (150, 98, 58)

def _q(v, step): return round(v/step)*step

# ------------------------------------------------------------------ joueur
KITS = {
    "rennes": dict(c1=(214, 26, 34), sleeve=(214, 26, 34), shorts=(26, 24, 28), socks=(214, 26, 34), trim=(26, 24, 28), kind="plain"),
    "psg": dict(c1=(20, 36, 82), sleeve=(20, 36, 82), shorts=(20, 36, 82), socks=(20, 36, 82), trim=(214, 30, 40), kind="band"),
    "guingamp": dict(c1=(214, 26, 34), sleeve=(26, 24, 28), shorts=(26, 24, 28), socks=(214, 26, 34), trim=(250, 248, 240), kind="plain"),
    "gk": dict(c1=(70, 150, 90), sleeve=(70, 150, 90), shorts=(30, 30, 34), socks=(70, 150, 90), trim=(30, 30, 34), kind="plain"),
    "suit": dict(c1=(52, 54, 62), sleeve=(52, 54, 62), shorts=(52, 54, 62), socks=(52, 54, 62), trim=(250, 248, 240), kind="suit"),
}

def player_parts(skin=(224, 178, 140), hair=(50, 36, 28), hair_style="short", kit="rennes", mood="happy", age=1.0, beard=None):
    k = KITS.get(kit, KITS["rennes"]); suit = k["kind"] == "suit"
    sk = C(skin); dk = C((30, 26, 26)); body = .62 + .38*age
    def p_leg(P, c):
        x, y, z = P.T
        c[:] = sk
        c[y < .78*body] = C(k["socks"]) if not suit else C(k["shorts"])
        if suit: c[y > .1] = C(k["shorts"])
        c[y < .16] = dk
        band = (y > .66*body) & (y < .72*body) & (not suit); c[band] = C(k["trim"])
        return c
    def p_torso(P, c):
        x, y, z = P.T; top = 1.15*body
        if k["kind"] == "band": c[(np.abs(x - .02) < .17) & (z > -.1)] = C(k["trim"])
        if suit:
            v = (z > .1) & (np.abs(x) < .32*np.clip((y - top*.25)/(top*.75), 0, 1)) ; c[v] = C((246, 244, 238))
            c[(z > .1) & (np.abs(x) < .055) & (y > top*.35) & (y < top*.9)] = C((200, 30, 40))
        else:
            c[(y > top - .1) & (np.abs(x) < .24) & (z > .0)] = C(k["trim"])                 # col
            c[(z > .15) & capsule(x, y, (.2, top*.72), (.2, top*.72), .07)] = C((250, 248, 240))   # écusson
        return c
    def p_arm(P, c):
        x, y, z = P.T; c[:] = C(k["sleeve"]); c[y < -.45*body] = sk
        if not suit: c[(y < -.4*body) & (y > -.47*body)] = C(k["trim"])
        else: c[(y < -.78*body)] = sk
        return c
    def p_head(P, c):
        x, y, z = P.T; f = z > .18
        eye = f & ((((np.abs(x) - .16)**2)/.0045 + ((y - .05)**2)/.008) < 1)
        c[eye] = dk
        brow = f & capsule(np.abs(x), y, (.09, .2 + (.02 if mood == "sad" else 0)), (.24, .19 - (.03 if mood == "sad" else 0)), .025)
        c[brow] = C(hair) * .8
        if mood == "happy": mouth = f & (np.abs(np.hypot(x, (y + .1)*1.3) - .14) < .028) & (y < -.13)
        elif mood == "sad": mouth = f & (np.abs(np.hypot(x, (y + .34)*1.3) - .14) < .028) & (y > -.26) & (np.abs(x) < .13)
        else: mouth = f & capsule(x, y, (-.09, -.2), (.09, -.2), .025)
        c[mouth] = C((120, 40, 40))
        c[f & (((np.abs(x) - .22)**2 + (y + .1)**2) < .05**2)] = sk*1.04 + .02                # joues
        if beard is not None: c[(y < -.12) & ~mouth & (z > -.1)] = C(beard)
        return c
    S = body; parts = []
    ty = 1.55*S
    for nm, sx in (("leg_l", -1), ("leg_r", 1)):
        leg = _sym([[.15, 1.5*S, .17], [.13, .75*S, .14], [.15, .16, .2], [.14, 0, .38], [.13, 0, -.14], [.14, .45*S, -.15], [.15, 1.5*S, -.15]])
        parts.append(Part(leg, skin, p_leg, (.23*sx, 0, 0), pivot=(0, 1.5*S, 0), name=nm))
    parts.append(Part(cbox(.92, .5*S, .56, .12), k["shorts"], None, (0, 1.6*S, 0), name="shorts"))
    torso = _sym([[.44, 0, .26], [.44, 0, -.24], [.56, 1.1*S, .26], [.56, 1.1*S, -.24], [.3, 1.18*S, .2], [.3, 1.18*S, -.2], [.5, .6*S, .32], [0, .7*S, .33]])
    parts.append(Part(torso, k["c1"], p_torso, (0, ty, 0), name="torso"))
    for nm, sx in (("arm_l", -1), ("arm_r", 1)):
        arm = _sym([[.13, 0, .13], [.12, -.55*S, .12], [.1, -1.05*S, .1], [.12, -1.18*S, .08]])
        parts.append(Part(arm, k["sleeve"], p_arm, (.66*sx, ty + 1.08*S, 0), pivot=(0, 0, 0), name=nm))
    parts.append(Part(cbox(.26, .3, .26, .2), skin, None, (0, ty + 1.25*S, 0), name="neck"))
    hy = ty + 1.25*S + .45; hs = 1.0 + .25*(1 - age)
    head = hs*_sym([[.36, .42, -.3], [.38, .1, -.34], [.32, -.3, -.3], [.4, .15, .2], [.36, -.18, .26], [.22, -.4, .28], [.0, -.44, .3],
                    [.3, .38, .3], [.0, .46, .32], [.0, .48, -.2], [.12, -.45, -.15], [.0, .05, .4]])
    parts.append(Part(head, skin, p_head, (0, hy, 0), pivot=(0, -.45, 0), name="head"))
    parts.append(Part(hs*np.array([[-.06, .1, 0], [.06, .1, 0], [0, -.12, .02], [-.07, -.12, 0], [.07, -.12, 0], [0, -.08, .14]]), C(skin)*255*.92, None,
                      (0, hy, .38*hs), pivot=(0, -.45, -.38*hs), name="head_nose"))
    for sx in (-1, 1):
        parts.append(Part(hs*cbox(.1, .2, .14, .3), skin, None, (.42*sx*hs, hy, 0), pivot=(-.42*sx*hs, -.45, 0), name="head_ear" + "lr"[sx > 0]))
    if hair_style != "bald":
        top = hs*_sym([[.42, .2, -.36], [.42, .3, .1], [.36, .52, .3], [.0, .62, .3], [.3, .62, -.1], [.0, .66, -.2], [.35, .1, -.4], [.0, .0, -.44],
                       [.43, .18, .22]] + ([[.4, -.25, -.3], [.0, -.3, -.42]] if hair_style == "long" else []))
        parts.append(Part(top, hair, None, (0, hy, 0), pivot=(0, -.45, 0), name="head_hair"))
    return parts, hy

def player_anim(arms=(8, 8), legs=(0, 0), look=(0, 0), lean=0.0, t=0.0):
    A = {}
    A["arm_l"] = rot("z", -math.radians(arms[0])) @ rot("x", -.08)
    A["arm_r"] = rot("z", math.radians(arms[1])) @ rot("x", -.08)
    A["leg_l"] = rot("x", -math.radians(legs[0])); A["leg_r"] = rot("x", -math.radians(legs[1]))
    h = rot("y", .35*look[0]) @ rot("x", -.2*look[1]) @ rot("z", .03*math.sin(t*2))
    for nm in ("head", "head_nose", "head_earl", "head_earr", "head_hair"): A[nm] = h
    return A

@lru_cache(maxsize=4000)
def player_sprite(skin, hair, hair_style, kit, mood, age, arms, legs, look, yaw, tq, beard=None, size=700):
    parts, hy = player_parts(skin, hair, hair_style, kit, mood, age, beard)
    A = player_anim(arms, legs, look, 0, tq)
    return render(parts, size, yaw=yaw, pitch=.12, scale=size/5.6, center=(0, 2.45, 0), anim=A, light=(-.5, .7, .6), anchor=(0, 0, 0),
                  shadow_a=90)

class PCPlayer:
    """Remplaçant papercraft de foot.Player (même signature draw). Hauteur à s=1 ≈ 470 px comme l'ancien."""
    H_REF = 560
    def __init__(self, name="p", hair=(50, 36, 28), skin=(224, 178, 140), hair_style="short", beard_col=None, yaw=-.32):
        self.hair, self.skin, self.hs, self.beard, self.yaw = tuple(hair), tuple(skin), hair_style, beard_col, yaw
    def sprite(self, age=1.0, kit="rennes", arms=(8, 8), legs=(0, 0), mood="happy", look=(0, 0), t=0.0, yaw=None):
        q = lambda v: int(_q(v, 6))
        return player_sprite(self.skin, self.hair, self.hs, kit if kit in KITS else "rennes", mood, round(age, 1), (q(arms[0]), q(arms[1])),
                             (q(legs[0]), q(legs[1])), (round(look[0], 1), round(look[1], 1)), round(self.yaw if yaw is None else yaw, 2),
                             round(t*4)/4 % 6.3, self.beard)
    def draw(self, cv, fr, x, y, s=1.0, age=1.0, kit="rennes", beard=False, arms=(8, 8), legs=(0, 0), mood="happy", look=(0, 0), alpha=1.0,
             tears=0.0, t=0.0, lean=0.0, kid_hair=None, yaw=None, **kw):
        try:
            from engine import blit_sxy
        except ImportError:
            from engine.engine import blit_sxy
        if alpha <= .01 or s <= .01: return None
        sp = self.sprite(age, kit, arms, legs, mood, look, t, yaw)
        k = s*self.H_REF/(sp.height*4.3/5.6)
        blit_sxy(cv, sp, x, y, k, k, -lean, alpha)

# ------------------------------------------------------------------ objets
def ball_parts():
    pts, V = icosphere(1.0, 1)
    def p(P, c):
        n = P/np.linalg.norm(P, axis=1, keepdims=True); d = (n @ V.T).max(1)
        c[d > .93] = DARK; return speckle(P, c, .01)
    return [Part(pts, (244, 240, 232), p, name="ball")]

@lru_cache(maxsize=64)
def ball_sprite(rq, size=200):
    A = {"ball": rot("y", rq) @ rot("x", rq*.7)}
    return render(ball_parts(), size, yaw=0, pitch=0, scale=size/2.3, center=(0, 0, 0), anim=A, shadow=False, anchor=(0, 0, 0))

def cup_parts():
    g = C(GOLD)
    def p_bowl(P, c):
        c[P[:, 1] > 1.18] = g*.62; return c
    parts = [Part(cbox(1.0, .3, 1.0, .2), (90, 60, 36), None, (0, .15, 0), name="base"),
             Part(lathe([(.42, 0), (.36, .1)], 8), GOLD, None, (0, .3, 0), name="foot"),
             Part(lathe([(.12, 0), (.1, .5), (.2, .62)], 8), GOLD, None, (0, .4, 0), name="stem"),
             Part(lathe([(.08, 0), (.4, .12), (.62, .5), (.7, .95), (.72, 1.2)], 10, .3), GOLD, p_bowl, (0, 1.0, 0), name="bowl")]
    for s in (-1, 1):
        H = ((.68, 1.95), (.98, 1.88), (1.08, 1.62), (.96, 1.38), (.66, 1.3))
        for i in range(len(H) - 1):
            (a0, b0), (a1, b1) = H[i], H[i + 1]
            parts.append(Part(np.vstack([cbox(.13, .13, .13, .2) + [a0*s, b0, 0], cbox(.13, .13, .13, .2) + [a1*s, b1, 0]]), (206, 156, 40), None,
                              (0, 0, 0), name=f"h{s}{i}"))
    return parts

@lru_cache(maxsize=32)
def cup_sprite(yq, size=420):
    return render(cup_parts(), size, yaw=yq, pitch=.22, scale=size/2.6, center=(0, 1.15, 0), anchor=(0, 0, 0), shadow_a=80)

def goal_parts(w=7.3, h=2.44, d=1.6):
    def p_net(P, c):
        a, b = P[:, 0], P[:, 1] + P[:, 2]
        m = ((a*3.2) % 1 < .14) | ((b*3.2) % 1 < .14); c[m] = C((120, 120, 128)); return c
    def p_net2(P, c):
        a, b = P[:, 2], P[:, 1]
        m = ((a*3.2) % 1 < .14) | ((b*3.2) % 1 < .14); c[m] = C((120, 120, 128)); return c
    post = (250, 250, 246); r = .12
    parts = [Part(cbox(.95*w, h*.95, .04, 0) + [0, 0, 0], (214, 214, 220), p_net, (0, h/2, -d), name="netb"),
             Part(cbox(.04, h, d, 0), (220, 220, 226), p_net2, (-w/2, h/2, -d/2), name="nets1"),
             Part(cbox(.04, h, d, 0), (220, 220, 226), p_net2, (w/2, h/2, -d/2), name="nets2"),
             Part(cbox(r, h, r, .3), post, None, (-w/2, h/2, 0), name="p1"), Part(cbox(r, h, r, .3), post, None, (w/2, h/2, 0), name="p2"),
             Part(cbox(w + r, r, r, .3), post, None, (0, h, 0), name="bar")]
    return parts

@lru_cache(maxsize=8)
def goal_sprite(size=900):
    return render(goal_parts(), size, yaw=.18, pitch=.42, scale=size/8.4, center=(0, 1.2, -.8), anchor=(0, 0, 0), shadow_a=60)

def door_parts():
    w = C(WOOD)
    def p(P, c):
        x, y = P[:, 0], P[:, 1]
        for yc in (.55, -.75):
            m = (np.abs(np.abs(x) - .62) < .05) & (np.abs(y - yc) < .62) | (np.abs(np.abs(y - yc) - .6) < .05) & (np.abs(x) < .64)
            c[m & (P[:, 2] > 0)] = w*.68
        return c
    return [Part(cbox(1.6, 3.0, .22, .08), WOOD, p, (0, 1.5, 0), name="door"),
            Part(lathe([(.1, 0), (.12, .06), (.06, .14)], 8), GOLD, None, (.6, 1.45, .12), R=rot("x", math.pi/2), name="knob")]

def crown_parts():
    g = C(GOLD)
    def jewel(P, c):
        a = np.arctan2(P[:, 2], P[:, 0]); m = (np.abs(((a/(2*np.pi/5)) % 1) - .5) < .14) & (np.abs(P[:, 1] - .25) < .12)
        c[m] = C((200, 20, 40)); return c
    parts = [Part(lathe([(.9, 0), (.95, .5)], 10), GOLD, jewel, (0, 0, 0), name="band")]
    for i in range(5):
        a = 2*math.pi*i/5 + .3; x, z = .92*math.cos(a), .92*math.sin(a)
        parts.append(Part(pyramid([(-.25, -.08), (.25, -.08), (0, .12)], .6), GOLD, None, (x, .48, z), R=rot("y", -a + math.pi/2), name=f"sp{i}"))
        parts.append(Part(icosphere(.09, 0)[0], (250, 236, 180), None, (x, 1.12, z), name=f"pe{i}"))
    return parts

def heart_parts(col=(240, 40, 80)):
    out = []
    for s in (-1, 1):
        lobe = icosphere(.55, 1)[0] + [.48*s, .35, 0]
        tip = np.array([[0, -1.0, 0], [0, -.9, .12], [0, -.9, -.12]])
        out.append(Part(np.vstack([lobe*np.array([1, 1, .55]), tip]), col, None, (0, 0, 0), name=f"lobe{s}"))
    return out

def tractor_parts():
    red, blk = (214, 26, 34), (36, 32, 34)
    def p_cab(P, c):
        x, y, z = P.T; c[(y > .05) & (np.abs(z) > .2) & (np.abs(x) < .38)] = C((150, 200, 230)); c[(y > .05) & (x > .43)] = C((150, 200, 230)); return c
    def p_wheel(P, c):
        r = np.hypot(P[:, 0], P[:, 1]); c[r < .45*np.max(r)] = C((190, 160, 60)); return c
    parts = [Part(cbox(2.2, .8, 1.2, .15), red, None, (.2, 1.1, 0), name="body"),
             Part(cbox(1.0, 1.1, 1.2, .1, .92), red, p_cab, (-.4, 2.05, 0), name="cab"),
             Part(cbox(1.2, .1, 1.35, .1), blk, None, (-.4, 2.62, 0), name="roof"),
             Part(lathe([(.08, 0), (.08, .7)], 6), blk, None, (.9, 1.45, .25), name="exh")]
    for nm, x, r, z in (("wb", -.6, .9, .7), ("wb2", -.6, .9, -.7), ("wf", 1.05, .5, .65), ("wf2", 1.05, .5, -.65)):
        pts = lathe([(r, -.18), (r, .18), (r*.5, .22)], 12) @ rot("x", math.pi/2).T*np.array([1, 1, 1 if z > 0 else -1])
        parts.append(Part(pts, blk, p_wheel, (x, r, z), name=nm))
    return parts

def tent_parts():
    def p(P, c):
        x, y, z = P.T; c[(z > .5) & (np.abs(x) < .45*(1 - y/1.4))] = C((50, 62, 50)); return c
    tri = [(-1.2, 0), (1.2, 0), (0, 1.6)]
    return [Part(prism(tri, 2.0), (120, 146, 110), p, (0, 0, 0), name="tent")]

def house_parts():
    def p_wall(P, c):
        x, y, z = P.T; f = z > .9
        for wx in (-.62, .62): c[f & (np.abs(x - wx) < .25) & (np.abs(y - .25) < .22)] = C((120, 180, 220))
        c[f & (np.abs(x) < .22) & (y < -.15)] = C((120, 80, 50)); return c
    roof = np.array([[-1.35, 0, -1.1], [1.35, 0, -1.1], [-1.35, 0, 1.1], [1.35, 0, 1.1], [-1.35, 1.1, 0], [1.35, 1.1, 0]])
    def p_roof(P, c):
        c[((P[:, 1]*5) % 1 < .12)] = C((140, 50, 36)); return c
    return [Part(cbox(2.4, 1.6, 1.9, .04), (236, 222, 196), p_wall, (0, .8, 0), name="wall"),
            Part(roof, (180, 70, 50), p_roof, (0, 1.6, 0), name="roof"),
            Part(cbox(.3, .8, .3, .1), (150, 80, 60), None, (.7, 2.4, -.3), name="chim")]

def closet_parts():
    w = C((126, 88, 60))
    def p(P, c):
        x, y, z = P.T; f = z > 0
        c[f & (np.abs(x) < .03)] = w*.6
        c[f & ((np.abs(np.abs(x) - .8) < .04) | (np.abs(np.abs(y) - 1.7) < .04))] = w*.7; return c
    return [Part(cbox(1.8, 3.6, .9, .06), (126, 88, 60), p, (0, 1.8, 0), name="body"),
            Part(cbox(2.0, .2, 1.0, .1), (100, 70, 48), None, (0, 3.7, 0), name="top")] + \
           [Part(icosphere(.07, 0)[0], GOLD, None, (sx*.15, 1.8, .46), name=f"k{sx}") for sx in (-1, 1)]

def card_parts(col=(220, 20, 30)):
    return [Part(cbox(1.0, 1.4, .06, .02), col, lambda P, c: speckle(P, c, .004, (120, 10, 20)), (0, .7, 0), name="card")]

def boater_parts():
    def p(P, c):
        c[(P[:, 1] > .05) & (P[:, 1] < .2)] = C((214, 26, 34)); return c
    return [Part(lathe([(1.0, 0), (1.0, .05)], 12), (226, 196, 120), None, (0, 0, 0), name="brim"),
            Part(lathe([(.55, 0), (.52, .4)], 12), (226, 196, 120), p, (0, .05, 0), name="crown")]

def flag_parts(t, cols=((247, 127, 0), (250, 250, 246), (0, 158, 96))):
    parts = [Part(lathe([(.05, 0), (.05, 3.4)], 6), (90, 76, 60), None, (0, 0, 0), name="pole")]
    n = 9
    for i in range(n):
        u0, u1 = i/n, (i + 1)/n
        z0, z1 = .14*math.sin(t*6 - u0*5)*u0*1.5, .14*math.sin(t*6 - u1*5)*u1*1.5
        pts = np.array([[u0*2.1, 2.1, z0], [u1*2.1, 2.1 - .05*u1, z1], [u0*2.1, 3.4, z0 + .02], [u1*2.1, 3.4 - .05*u1, z1 + .02],
                        [u0*2.1, 2.1, z0 + .02], [u1*2.1, 2.1 - .05*u1, z1 + .03]])
        parts.append(Part(pts, cols[min(2, int(u0*3 + 1e-6))], None, (0, 0, 0), name=f"f{i}"))
    return parts

# ------------------------------------------------------------------ sprites en cache
@lru_cache(maxsize=256)
def obj_sprite(kind, size=500, yaw=-.4, pitch=.25, phase=0.0):
    B = dict(door=(door_parts, 3.6, (0, 1.5, 0)), crown=(crown_parts, 2.6, (0, .55, 0)), heart=(heart_parts, 2.6, (0, 0, 0)),
             tractor=(tractor_parts, 3.6, (0, 1.3, 0)), tent=(tent_parts, 3.0, (0, .8, 0)), house=(house_parts, 3.6, (0, 1.3, 0)),
             closet=(closet_parts, 4.4, (0, 1.9, 0)), card=(card_parts, 1.9, (0, .7, 0)), boater=(boater_parts, 2.3, (0, .2, 0)),
             flag=(lambda: flag_parts(phase), 4.0, (1.0, 1.7, 0)), cat_black=(lambda: cat((44, 40, 48), C((20, 18, 22))), 3.4, (0, 1.35, -.4)),
             cup=(cup_parts, 2.6, (0, 1.15, 0)))
    fn, span, cen = B[kind]
    return render(fn(), size, yaw=yaw, pitch=pitch, scale=size/span, center=cen, anchor=(0, 0, 0), shadow=kind not in ("heart", "card", "crown", "boater"),
                  shadow_a=80)

@lru_cache(maxsize=512)
def cat_sprite(fur, stripe, tq, walk, yaw, size=520):
    return render(cat(fur, C(stripe)), size, yaw=yaw, pitch=.18, scale=size/3.6, center=(0, 1.35, -.4), anim=cat_anim(tq, walk), anchor=(0, 0, -.4))
