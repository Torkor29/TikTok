"""
foot.py — kit « football » pour le moteur papier : joueur articulé qui grandit et change de maillot,
ballon, cages, trophées, Ballon d'Or, toise, maillot de dos avec nom + numéro, tableau d'affichage…
Tout est en papier découpé (Paper), dans la même identité visuelle que engine.py.
"""
import math, random
from engine import *

SKIN = (226, 176, 136)
HAIR = (86, 56, 36)
INK = PAL["ink"]

# ------------------------------------------------------------------ maillots
# kind : plain | stripes | halves | band (bande verticale centrale, style PSG) | suit (costume)
KITS = {
    "newells": dict(kind="halves", c1=(206, 34, 44), c2=(34, 32, 32), sleeve=(206, 34, 44), shorts=(34, 32, 32), socks=(206, 34, 44), trim=(34, 32, 32)),
    "barca":   dict(kind="stripes", c1=(0, 77, 152), c2=(165, 0, 68), n=5, sleeve=(165, 0, 68), shorts=(0, 60, 128), socks=(165, 0, 68), trim=(238, 190, 60)),
    "liverpool": dict(kind="plain", c1=(200, 16, 46), sleeve=(200, 16, 46), shorts=(200, 16, 46), socks=(200, 16, 46), trim=(250, 250, 246)),
    "everton": dict(kind="plain", c1=(0, 60, 170), sleeve=(0, 60, 170), shorts=(250, 250, 246), socks=(0, 60, 170), trim=(250, 250, 246)),
    "psg":     dict(kind="band", c1=(16, 40, 86), c2=(210, 36, 42), c3=(250, 248, 240), sleeve=(16, 40, 86), shorts=(16, 40, 86), socks=(16, 40, 86), trim=(210, 36, 42)),
    "arg":     dict(kind="stripes", c1=(116, 174, 226), c2=(252, 250, 244), n=5, sleeve=(116, 174, 226), shorts=(34, 32, 32), socks=(252, 250, 244), trim=(34, 32, 32)),
    "miami":   dict(kind="plain", c1=(246, 170, 200), sleeve=(246, 170, 200), shorts=(246, 170, 200), socks=(246, 170, 200), trim=(34, 32, 32)),
    "street":  dict(kind="plain", c1=(252, 250, 244), sleeve=(252, 250, 244), shorts=(40, 84, 150), socks=(252, 250, 244), trim=(40, 84, 150)),
    "suit":    dict(kind="suit", c1=(52, 54, 62), sleeve=(52, 54, 62), shorts=(52, 54, 62), socks=(52, 54, 62), trim=(250, 248, 240), pants=True),
    "coach":   dict(kind="plain", c1=(38, 150, 138), sleeve=(38, 150, 138), shorts=(46, 44, 42), socks=(46, 44, 42), trim=(250, 248, 240), pants=True),
    "sporting": dict(kind="hoops", c1=(0, 128, 72), c2=(250, 250, 246), n=7, sleeve=(250, 250, 246), shorts=(34, 32, 32), socks=(0, 128, 72), trim=(0, 128, 72)),
    "manutd":  dict(kind="plain", c1=(214, 24, 34), sleeve=(214, 24, 34), shorts=(250, 250, 246), socks=(34, 32, 32), trim=(250, 250, 246)),
    "real":    dict(kind="plain", c1=(250, 250, 246), sleeve=(250, 250, 246), shorts=(250, 250, 246), socks=(250, 250, 246), trim=(212, 170, 60)),
    "portugal": dict(kind="plain", c1=(196, 18, 48), sleeve=(196, 18, 48), shorts=(0, 110, 62), socks=(196, 18, 48), trim=(0, 110, 62)),
    "alnassr": dict(kind="plain", c1=(252, 212, 20), sleeve=(252, 212, 20), shorts=(20, 50, 150), socks=(252, 212, 20), trim=(20, 50, 150)),
    "madeira": dict(kind="plain", c1=(250, 250, 246), sleeve=(250, 250, 246), shorts=(40, 84, 150), socks=(250, 250, 246), trim=(196, 18, 48)),
    "france":  dict(kind="plain", c1=(24, 44, 120), sleeve=(24, 44, 120), shorts=(250, 250, 246), socks=(206, 32, 44), trim=(250, 250, 246)),
    "france_w": dict(kind="plain", c1=(250, 250, 246), sleeve=(250, 250, 246), shorts=(250, 250, 246), socks=(250, 250, 246), trim=(206, 32, 44)),
    "italy":   dict(kind="plain", c1=(40, 100, 190), sleeve=(40, 100, 190), shorts=(250, 250, 246), socks=(40, 100, 190), trim=(250, 250, 246)),
    "brazil":  dict(kind="plain", c1=(252, 214, 30), sleeve=(252, 214, 30), shorts=(24, 70, 160), socks=(250, 250, 246), trim=(0, 140, 70)),
    "saudi":   dict(kind="plain", c1=(0, 120, 70), sleeve=(0, 120, 70), shorts=(250, 250, 246), socks=(0, 120, 70), trim=(250, 250, 246)),
    "juventus": dict(kind="stripes", c1=(30, 28, 28), c2=(250, 250, 246), n=5, sleeve=(30, 28, 28), shorts=(250, 250, 246), socks=(30, 28, 28), trim=(250, 250, 246)),
    "cannes":  dict(kind="plain", c1=(200, 30, 40), sleeve=(200, 30, 40), shorts=(250, 250, 246), socks=(200, 30, 40), trim=(250, 250, 246)),
    "gk":      dict(kind="plain", c1=(120, 124, 130), sleeve=(120, 124, 130), shorts=(40, 40, 44), socks=(120, 124, 130), trim=(40, 40, 44)),
    "ref":     dict(kind="plain", c1=(34, 32, 32), sleeve=(34, 32, 32), shorts=(34, 32, 32), socks=(34, 32, 32), trim=(250, 250, 246)),
    "om":      dict(kind="plain", c1=(250, 250, 246), sleeve=(47, 174, 224), shorts=(250, 250, 246), socks=(250, 250, 246), trim=(47, 174, 224)),
    "milan":   dict(kind="stripes", c1=(200, 24, 36), c2=(30, 28, 28), n=5, sleeve=(200, 24, 36), shorts=(250, 250, 246), socks=(30, 28, 28), trim=(30, 28, 28)),
    "redstar": dict(kind="stripes", c1=(206, 30, 44), c2=(250, 250, 246), n=5, sleeve=(206, 30, 44), shorts=(250, 250, 246), socks=(206, 30, 44), trim=(250, 250, 246)),
    "valenciennes": dict(kind="plain", c1=(206, 30, 44), sleeve=(206, 30, 44), shorts=(250, 250, 246), socks=(206, 30, 44), trim=(250, 250, 246)),
    "santos":  dict(kind="plain", c1=(250, 250, 246), sleeve=(250, 250, 246), shorts=(250, 250, 246), socks=(250, 250, 246), trim=(30, 28, 28)),
    "alhilal": dict(kind="plain", c1=(20, 76, 172), sleeve=(20, 76, 172), shorts=(250, 250, 246), socks=(20, 76, 172), trim=(250, 250, 246)),
    "norway":  dict(kind="plain", c1=(200, 16, 46), sleeve=(200, 16, 46), shorts=(250, 250, 246), socks=(24, 44, 120), trim=(24, 44, 120)),
    "lemans":  dict(kind="plain", c1=(206, 30, 40), sleeve=(206, 30, 40), shorts=(206, 30, 40), socks=(206, 30, 40), trim=(250, 204, 40)),
    "guingamp": dict(kind="halves", c1=(200, 20, 40), c2=(30, 28, 28), sleeve=(200, 20, 40), shorts=(30, 28, 28), socks=(200, 20, 40), trim=(30, 28, 28)),
    "chelsea": dict(kind="plain", c1=(20, 60, 160), sleeve=(20, 60, 160), shorts=(20, 60, 160), socks=(250, 250, 246), trim=(250, 250, 246)),
    "tennis":  dict(kind="plain", c1=(250, 250, 246), sleeve=(250, 250, 246), shorts=(40, 44, 60), socks=(250, 250, 246), trim=(40, 44, 60)),
    "pilote":  dict(kind="plain", c1=(200, 24, 34), sleeve=(200, 24, 34), shorts=(200, 24, 34), socks=(30, 28, 28), trim=(250, 250, 246), pants=True),
    "dijon":   dict(kind="plain", c1=(214, 26, 42), sleeve=(214, 26, 42), shorts=(214, 26, 42), socks=(214, 26, 42), trim=(250, 250, 246)),
}

def kit_pattern(kit, x0, x1):
    """Motif de maillot entre x0 et x1 (coordonnées locales du torse)."""
    def pat(d, ox, oy):
        k = kit["kind"]
        if k == "stripes":
            n = kit["n"]; w = (x1-x0)/n
            for i in range(n):
                d.rectangle([ox+x0+i*w, 0, ox+x0+(i+1)*w, 4000], fill=kit["c1"] if i % 2 == 0 else kit["c2"])
        elif k == "hoops":
            n = kit["n"]; hgt = 200/n
            for i in range(n):
                d.rectangle([0, oy-10+i*hgt, 4000, oy-10+(i+1)*hgt], fill=kit["c1"] if i % 2 == 0 else kit["c2"])
        elif k == "halves":
            d.rectangle([0, 0, ox, 4000], fill=kit["c1"]); d.rectangle([ox, 0, 4000, 4000], fill=kit["c2"])
        elif k == "band":
            d.rectangle([ox-30, 0, ox+30, 4000], fill=kit["c3"]); d.rectangle([ox-20, 0, ox+20, 4000], fill=kit["c2"])
        elif k == "suit":
            d.polygon([(ox-30, oy-10), (ox+30, oy-10), (ox, oy+120)], fill=kit["trim"])
            d.polygon([(ox-9, oy+8), (ox+9, oy+8), (ox+6, oy+95), (ox, oy+108), (ox-6, oy+95)], fill=(170, 40, 40))
    return pat

# ------------------------------------------------------------------ joueur articulé
# Géométrie « adulte » (1,70 m = 620 px à s=1) : pieds en (0,0), haut du crâne à y=-620.
# L'âge (0 = 10 ans / 1,27 m, 1 = adulte / 1,70 m) change les proportions : corps plus court, tête plus grosse.
HIP_Y, WAIST_Y, NECK_Y, SHOULDER_DX, HIP_DX = -262, -330, -512, 84, 38

class HairGroup:
    """Plusieurs mèches de papier dessinées ensemble (même ancre que la tête) : couronne d'un crâne chauve."""
    def __init__(self, papers, shine=None): self.papers, self.shine = papers, shine
    def draw(self, cv, fr, x, y, scale=1.0, rot=0.0, alpha=1.0, amp=1.5):
        if self.shine and alpha > .5:   # reflet sur le crâne
            d = ImageDraw.Draw(cv); s = scale
            d.ellipse([x-30*s, y-54*s, x-8*s, y-42*s], fill=self.shine)
        for p in self.papers: p.draw(cv, fr, x, y, scale, rot, alpha, amp)

class Player:
    _cache = {}

    def __init__(self, key="messi", hair=HAIR, beard_col=(92, 60, 40), skin=None, hair_style="short"):
        self.key, self.hair_col, self.beard_col = key, hair, beard_col
        self.skin = skin = skin or SKIN
        self.head = Paper(ellipse_pts(104, 124, 36), skin, key+"head", rough=1.4)
        self.neck = Paper(rect_pts(34, 40), skin, key+"neck", rough=1, shadow=False)
        if hair_style == "mohawk":  # crête (Neymar à Santos) : côtés courts, bande dressée au milieu
            hpts = [(-54, -10), (-52, -40), (-30, -56), (-14, -62), (-12, -96), (0, -108), (12, -96), (14, -62), (30, -56),
                    (52, -40), (54, -10), (44, -26), (20, -40), (0, -44), (-20, -40), (-44, -26)]
        elif hair_style == "mullet":  # coupe mulet : court devant, long sur la nuque (Waddle, années 90)
            hpts = [(-60, 46), (-58, -18), (-54, -52), (-34, -72), (-4, -78), (28, -74), (50, -58), (58, -18), (60, 46),
                    (48, 50), (48, -30), (26, -44), (4, -42), (-22, -46), (-48, -30), (-48, 50)]
        elif hair_style == "quiff":   # cheveux courts sur les côtés, houppette relevée devant
            hpts = [(-55, -14), (-56, -46), (-40, -66), (-18, -80), (6, -104), (30, -98), (46, -80), (56, -50), (56, -14),
                    (46, -34), (30, -44), (8, -46), (-16, -46), (-40, -38)]
        else:
            hpts = [(-56, -18), (-54, -52), (-34, -72), (-4, -78), (28, -74), (50, -58), (57, -22),
                    (46, -36), (26, -46), (4, -44), (-22, -48), (-44, -34)]
        if hair_style == "bald":    # crâne rasé : deux touffes courtes au-dessus des oreilles
            side = [(-57, -2), (-57, -26), (-52, -42), (-45, -40), (-47, -22), (-47, -2)]
            self.hair_adult = HairGroup([Paper(poly_pts(side), hair, key+"hairL", rough=1.2, shadow=False),
                                         Paper(poly_pts([(-x, y) for x, y in side]), hair, key+"hairR", rough=1.2, shadow=False)],
                                        shine=tuple(min(255, c+28) for c in skin))
        else:
            self.hair_adult = Paper(poly_pts(hpts), hair, key+"hairA", rough=2.0, hatch=True)
        self.hair_kid = Paper(poly_pts([(-60, -2), (-58, -50), (-36, -74), (-2, -80), (32, -74), (54, -54), (60, -4),
                                        (48, -22), (34, -28), (14, -22), (-6, -30), (-26, -22), (-46, -26)]), hair, key+"hairK", rough=2.2, hatch=True)
        self.beard = Paper(poly_pts([(-52, -8), (-40, -2), (-22, 18), (0, 16), (22, 18), (40, -2), (52, -8), (50, 22), (34, 48),
                                     (12, 62), (-12, 62), (-34, 48), (-50, 22)]), beard_col, key+"beard", rough=1.8, hatch=True, shadow=False)

    def parts(self, kitname):
        ck = (self.key, kitname)
        if ck in Player._cache: return Player._cache[ck]
        kit = KITS[kitname]; k = self.key + kitname
        torso_pts = [(-86, 6), (-58, -6), (-24, -10), (0, 6), (24, -10), (58, -6), (86, 6), (74, 190), (-74, 190)]
        torso = Paper(torso_pts, kit["c1"], k+"torso", rough=1.8, hatch=True, pattern=kit_pattern(kit, -90, 90))
        def _collar(d, a):
            ax, ay = a
            d.line([(ax-22, ay-8), (ax, ay+10), (ax+22, ay-8)], fill=kit["trim"], width=6)
        if kit["kind"] != "suit": torso.add(_collar)
        sleeve_col, pants = kit["sleeve"], kit.get("pants")
        def arm_pat(d, ox, oy):
            d.rectangle([0, 0, 4000, oy+(190 if pants else 62)], fill=sleeve_col)
        skin = self.skin
        arm = Paper([(-18, -12), (18, -12), (17, 196), (-17, 196)], skin, k+"arm", rough=1.4, pattern=arm_pat)
        def _hand(d, a):
            ax, ay = a; d.ellipse([ax-17, ay+182, ax+17, ay+216], fill=SKIN)
        arm.add(_hand)
        shorts = Paper([(-78, -4), (78, -4), (84, 92), (8, 92), (0, 66), (-8, 92), (-84, 92)], kit["shorts"], k+"shorts", rough=1.6)
        legs = []
        for side in (-1, 1):
            def leg_pat(d, ox, oy, side=side):
                if pants: d.rectangle([0, 0, 4000, oy+236], fill=kit["shorts"])
                else: d.rectangle([0, oy+140, 4000, oy+236], fill=kit["socks"])
                d.rectangle([0, oy+236, 4000, 4000], fill=(34, 32, 32))
            pts = [(-20, -6), (20, -6), (20, 238), (20+side*28, 244), (22+side*34, 262), (-22, 262), (-20, 238)] if side > 0 else \
                  [(-20, -6), (20, -6), (20, 238), (22, 262), (-22+side*34, 262), (-20+side*28, 244), (-20, 238)]
            legs.append(Paper(pts, skin, k+f"leg{side}", rough=1.4, pattern=leg_pat))
        P = dict(torso=torso, arm=arm, shorts=shorts, legs=legs, kit=kit)
        Player._cache[ck] = P
        return P

    def draw(self, cv, fr, x, y, s=1.0, age=1.0, kit="barca", beard=False, arms=(8, 8), legs=(0, 0), mood="normal",
             look=(0, 0), alpha=1.0, tears=0.0, t=0.0, lean=0.0, kid_hair=None):
        """x, y = position des pieds. arms=(gauche, droit) : angle d'ouverture en degrés, vers l'extérieur
        (0 = le long du corps, 90 = à l'horizontale, 165 = levés vers le ciel ; négatif = vers l'intérieur).
        legs = ouverture des jambes (course, frappe). Renvoie la position des yeux (pour les larmes)."""
        if alpha <= 0.01 or s <= 0.01: return None
        P = self.parts(kit)
        age = clamp(age)
        bs = s*lerp(0.70, 1.0, age); hs = s*lerp(0.96, 1.0, age)
        # jambes
        for side, lr in ((-1, legs[0]), (1, legs[1])):
            P["legs"][0 if side < 0 else 1].draw(cv, fr, x+side*HIP_DX*bs, y+HIP_Y*bs, bs, side*lr, alpha, 1.0)
        P["shorts"].draw(cv, fr, x, y+WAIST_Y*bs, bs, 0, alpha, 1.0)
        P["torso"].draw(cv, fr, x+lean*bs, y+NECK_Y*bs, bs, -lean*.15, alpha, 1.0)
        for side, ar in ((-1, arms[0]), (1, arms[1])):
            P["arm"].draw(cv, fr, x+lean*bs+side*SHOULDER_DX*bs*.93, y+(NECK_Y+14)*bs, bs, side*ar, alpha, 1.0)
        self.neck.draw(cv, fr, x+lean*bs, y+(NECK_Y-6)*bs, bs, 0, alpha, .8)
        hx, hy = x+lean*bs, y+NECK_Y*bs - 58*hs
        self.head.draw(cv, fr, hx, hy, hs, 0, alpha, 1.0)
        if beard and age > .9: self.beard.draw(cv, fr, hx, hy+8*hs, hs, 0, alpha, 1.0)
        kid = (age < .6) if kid_hair is None else kid_hair
        (self.hair_kid if kid else self.hair_adult).draw(cv, fr, hx, hy, hs, 0, alpha, 1.0)
        if alpha > .5: return self.face(cv, hx, hy, hs, mood, look, beard and age > .9, t, tears)
        return (hx, hy)

    def face(self, cv, hx, hy, hs, mood, look, beard, t, tears):
        d = ImageDraw.Draw(cv)
        lx, ly = look[0]*5*hs, look[1]*4*hs
        blink = (int(t*24) % 90) < 3
        eyes = []
        for sg in (-1, 1):
            ex, ey = hx+sg*21*hs+lx, hy-2*hs+ly; eyes.append((ex, ey+10*hs))
            if mood == "happy" or blink:
                d.line([(ex-8*hs, ey+2*hs), (ex, ey-5*hs), (ex+8*hs, ey+2*hs)], fill=INK, width=max(2, int(4*hs)))
            else:
                k = 1.3 if mood == "surprised" else 1.0
                d.ellipse([ex-5*hs*k, ey-7*hs*k, ex+5*hs*k, ey+7*hs*k], fill=INK)
                d.ellipse([ex-2*hs, ey-5*hs, ex+1*hs, ey-2*hs], fill=(255, 255, 255))
            # sourcils
            by = ey-18*hs; bw = max(2, int(4*hs))
            if mood == "sad":          # bouts intérieurs relevés
                p = [(ex-10*hs, by+3*hs), (ex+10*hs, by-5*hs)] if sg < 0 else [(ex-10*hs, by-5*hs), (ex+10*hs, by+3*hs)]
            elif mood == "determined": # bouts intérieurs baissés
                p = [(ex-10*hs, by-5*hs), (ex+10*hs, by+3*hs)] if sg < 0 else [(ex-10*hs, by+3*hs), (ex+10*hs, by-5*hs)]
            elif mood == "surprised": p = [(ex-10*hs, by-5*hs), (ex+10*hs, by-5*hs)]
            else: p = [(ex-10*hs, by), (ex+10*hs, by-2*hs)]
            d.line(p, fill=self.hair_col, width=bw)
        d.line([(hx+lx*.5, hy+4*hs), (hx+3*hs+lx*.5, hy+18*hs)], fill=(176, 120, 90), width=max(1, int(3*hs)))
        my = hy+34*hs
        mc = (120, 40, 36) if not beard else (70, 30, 26)
        if mood in ("happy", "cheer"):
            if mood == "cheer": d.ellipse([hx-13*hs, my-8*hs, hx+13*hs, my+14*hs], fill=mc)
            else: d.chord([hx-16*hs, my-12*hs, hx+16*hs, my+12*hs], 0, 180, fill=mc)
        elif mood == "surprised": d.ellipse([hx-7*hs, my-7*hs, hx+7*hs, my+9*hs], fill=mc)
        elif mood == "sad": d.arc([hx-14*hs, my, hx+14*hs, my+18*hs], 200, 340, fill=mc, width=max(2, int(4*hs)))
        else: d.line([(hx-11*hs, my+2*hs), (hx+11*hs, my)], fill=mc, width=max(2, int(4*hs)))
        if tears > 0: drops(cv, "tears", tears, eyes, n=3, size=9*hs, speed=420*hs)
        return eyes

    def render_layer(self, fr, s=1.0, **kw):
        """Dessine le joueur dans un calque (pour le faire pivoter / retourner d'un bloc)."""
        L = layer(int(760*s), int(900*s), (380*s, 820*s))
        tmp = Image.new("RGBA", L.size, (0, 0, 0, 0))
        kw.setdefault("t", 1.0)   # t=0 tomberait sur un clignement (yeux fermés)
        self.draw(tmp, fr, 380*s, 820*s, s, **kw)
        tmp.info["anchor"] = (380*s, 820*s)
        return tmp

def spin_player(cv, fr, pl, x, y, u, kit_a, kit_b, s=1.0, **kw):
    """Le joueur fait un tour sur lui-même (retournement horizontal) et change de maillot à mi-course."""
    sx = math.cos(u*math.pi*2)
    kit = kit_a if u < .25 else kit_b
    L = pl.render_layer(fr, s, kit=kit, **kw)
    blit_sxy(cv, L, x, y, max(.04, abs(sx)), 1.0)

# ------------------------------------------------------------------ grand-mère
class Granny:
    def __init__(self):
        self.dress = Paper([(-62, 0), (62, 0), (92, 300), (-92, 300)], PAL["teal"], "gr_dress", hatch=True)
        self.cardi = Paper([(-66, -4), (66, -4), (70, 120), (-70, 120)], PAL["mustard"], "gr_cardi", hatch=True)
        self.head = Paper(ellipse_pts(98, 112, 30), SKIN, "gr_head", rough=1.3)
        self.hair = Paper(poly_pts([(-54, -4), (-52, -46), (-26, -66), (10, -68), (40, -56), (54, -20), (50, 2), (38, -30), (0, -40), (-38, -30)]),
                          (206, 204, 200), "gr_hair", hatch=True)
        self.bun = Paper(ellipse_pts(54, 50, 20), (206, 204, 200), "gr_bun", hatch=True)
        self.arm = Paper([(-15, -8), (15, -8), (14, 176), (-14, 176)], PAL["mustard"], "gr_arm", rough=1.2)
        self.leg = Paper(rect_pts(30, 80), SKIN, "gr_leg", rough=1, shadow=False)
    def draw(self, cv, fr, x, y, s=1.0, arms=(10, 10), alpha=1.0, mood="happy", t=0.0):
        if alpha <= .01: return
        for sg in (-1, 1):
            self.leg.draw(cv, fr, x+sg*30*s, y-40*s, s, 0, alpha, .6)
            ImageDraw.Draw(cv).ellipse([x+sg*30*s-22*s, y-14*s, x+sg*30*s+22*s, y+4*s], fill=PAL["charcoal"])
        self.dress.draw(cv, fr, x, y-380*s, s, 0, alpha, 1)
        self.cardi.draw(cv, fr, x, y-376*s, s, 0, alpha, 1)
        for sg, a in ((-1, arms[0]), (1, arms[1])):
            self.arm.draw(cv, fr, x+sg*66*s, y-366*s, s, sg*a, alpha, 1)
            ang = math.radians(sg*a); hx_ = x+sg*66*s + math.sin(ang)*180*s; hy_ = y-366*s + math.cos(ang)*180*s
            ImageDraw.Draw(cv).ellipse([hx_-15*s, hy_-15*s, hx_+15*s, hy_+15*s], fill=SKIN)
        hx, hy = x, y-440*s
        self.bun.draw(cv, fr, hx+38*s, hy-58*s, s, 0, alpha, .8)
        self.head.draw(cv, fr, hx, hy, s, 0, alpha, 1)
        self.hair.draw(cv, fr, hx, hy, s, 0, alpha, 1)
        if alpha > .5:
            d = ImageDraw.Draw(cv)
            for sg in (-1, 1):
                d.ellipse([hx+sg*20*s-14*s, hy-12*s, hx+sg*20*s+14*s, hy+14*s], outline=INK, width=max(2, int(3*s)))
                d.ellipse([hx+sg*20*s-4*s, hy-4*s, hx+sg*20*s+4*s, hy+5*s], fill=INK)
            d.line([(hx-6*s, hy), (hx+6*s, hy)], fill=INK, width=max(2, int(3*s)))
            d.arc([hx-15*s, hy+18*s, hx+15*s, hy+38*s], 20, 160, fill=(150, 60, 50), width=max(2, int(4*s)))

# ------------------------------------------------------------------ objets
def _ball_decor(d, a):
    ax, ay = a; r = 50
    pent = [(ax+17*math.cos(-math.pi/2+k*2*math.pi/5), ay+17*math.sin(-math.pi/2+k*2*math.pi/5)) for k in range(5)]
    d.polygon(pent, fill=PAL["ink"])
    for k in range(5):
        an = -math.pi/2 + k*2*math.pi/5
        cx, cy = ax+44*math.cos(an), ay+44*math.sin(an)
        p2 = [(cx+12*math.cos(an+math.pi+j*2*math.pi/5), cy+12*math.sin(an+math.pi+j*2*math.pi/5)) for j in range(5)]
        d.polygon(p2, fill=PAL["ink"])
        d.line([pent[k], (ax+32*math.cos(an), ay+32*math.sin(an))], fill=PAL["ink"], width=3)
BALL = Paper(ellipse_pts(104, 104, 30), (252, 250, 244), "football", rough=1.3).add(_ball_decor)

def draw_ball(cv, fr, x, y, s=1.0, rot=0.0, alpha=1.0):
    BALL.draw(cv, fr, x, y, s, rot, alpha, 1.0)

def draw_goal(cv, fr, x, y, w=420, h=240, net_u=0.0, alpha=1.0, t=0.0):
    """Cage vue de face, (x, y) = milieu de la ligne de but. net_u > 0 : le filet se déforme (but)."""
    d = ImageDraw.Draw(cv)
    bulge = 26*math.sin(net_u*math.pi) if 0 < net_u < 1 else 0
    for i in range(1, 9):
        xx = x - w/2 + i*w/9
        d.line([(xx, y-h), (xx + (xx-x)*.02*bulge/10, y - h/2 + bulge*.3), (xx, y)], fill=(200, 196, 188), width=3)
    for j in range(1, 6):
        yy = y - h + j*h/6
        d.line([(x-w/2, yy), (x, yy + bulge*math.sin(j/6*math.pi)), (x+w/2, yy)], fill=(200, 196, 188), width=3)
    d.rectangle([x-w/2-10, y-h-10, x+w/2+10, y-h+4], fill=(252, 250, 244), outline=(150, 146, 140), width=2)
    for sg in (-1, 1):
        d.rectangle([x+sg*w/2-10, y-h-10, x+sg*w/2+4, y], fill=(252, 250, 244), outline=(150, 146, 140), width=2)

def _cup_decor(d, a):
    ax, ay = a
    d.arc([ax-118, ay-88, ax-44, ay+10], 90, 270, fill=(200, 150, 40), width=14)
    d.arc([ax+44, ay-88, ax+118, ay+10], 270, 90, fill=(200, 150, 40), width=14)
    d.ellipse([ax-70, ay-100, ax+70, ay-76], fill=(252, 226, 140))
CUP = Paper(poly_pts([(-72, -92), (72, -92), (60, 10), (22, 50), (16, 96), (52, 112), (52, 134), (-52, 134), (-52, 112), (-16, 96), (-22, 50), (-60, 10)]),
            PAL["gold"], "cup", rough=1.6, hatch=True, pad=60).add(_cup_decor)

def _wc_decor(d, a):
    ax, ay = a
    for yy in (150, 176):
        d.rectangle([ax-58, ay+yy, ax+58, ay+yy+12], fill=(40, 128, 72))
    for k in range(5):
        d.arc([ax-60+k*6, ay-150+k*20, ax+60-k*6, ay-40+k*20], 200, 340, fill=(196, 146, 36), width=5)
    d.ellipse([ax-58, ay-218, ax+58, ay-102], fill=(248, 206, 84))
    d.arc([ax-58, ay-218, ax+58, ay-102], 0, 360, fill=(196, 146, 36), width=4)
    d.line([(ax-58, ay-160), (ax+58, ay-160)], fill=(196, 146, 36), width=3)
    d.arc([ax-30, ay-218, ax+30, ay-102], 90, 270, fill=(196, 146, 36), width=3)
WC_TROPHY = Paper(poly_pts([(-44, -170), (44, -170), (52, -110), (30, -40), (22, 40), (40, 110), (70, 140), (70, 200), (-70, 200), (-70, 140), (-40, 110), (-22, 40), (-30, -40), (-52, -110)]),
                  PAL["gold"], "wctrophy", rough=1.4, hatch=True, pad=60).add(_wc_decor)
WC_SIL = Paper(poly_pts([(-44, -170), (44, -170), (52, -110), (30, -40), (22, 40), (40, 110), (70, 140), (70, 200), (-70, 200), (-70, 140), (-40, 110), (-22, 40), (-30, -40), (-52, -110)]),
               (70, 66, 62), "wcsil", rough=1.4, hatch=True, pad=60)
def _wcsil_decor(d, a):
    ax, ay = a; d.ellipse([ax-58, ay-218, ax+58, ay-102], fill=(70, 66, 62))
WC_SIL.add(_wcsil_decor)

def _bdo_decor(d, a):
    ax, ay = a
    for k in range(6):
        an = k*math.pi/3
        d.line([(ax, ay), (ax+70*math.cos(an), ay+70*math.sin(an))], fill=(200, 146, 30), width=4)
    d.ellipse([ax-24, ay-24, ax+24, ay+24], fill=(214, 160, 40))
    d.ellipse([ax-50, ay-62, ax-10, ay-34], fill=(255, 238, 170))
BALLON_OR = Paper(ellipse_pts(150, 150, 36), PAL["gold"], "ballondor", rough=1.3).add(_bdo_decor)
BDO_BASE = Paper(poly_pts([(-40, 0), (40, 0), (54, 40), (-54, 40)]), (60, 56, 52), "bdobase", rough=1.2)

def draw_ballon_or(cv, fr, x, y, s=1.0, alpha=1.0):
    BDO_BASE.draw(cv, fr, x, y+70*s, s, 0, alpha); BALLON_OR.draw(cv, fr, x, y, s, 0, alpha)

def toise_sprite(px_per_m, marks):
    """Toise murale (règle graduée) en papier ; (0,0) = sol."""
    h = px_per_m*1.9
    def dec(d, a):
        ax, ay = a
        for cm in range(0, 191, 10):
            yy = ay - cm/100*px_per_m
            L = 44 if cm % 50 == 0 else 24
            d.line([(ax+50-L, yy), (ax+50, yy)], fill=PAL["ink"], width=4 if cm % 50 == 0 else 2)
            if cm % 50 == 0 and 0 < cm:
                d.text((ax-40, yy), f"{cm/100:.1f}".replace(".", ","), font=font("hand", 36), fill=PAL["ink"], anchor="lm")
    return Paper([(-50, 0), (50, 0), (50, -h), (-50, -h)], PAL["mustard"], "toise", rough=1.5, hatch=True).add(dec)

def jersey_back(kitname, name, number, key=None):
    """Maillot vu de dos (nom + numéro), pour les changements de numéro."""
    kit = KITS[kitname]
    pts = [(-200, -210), (-120, -236), (-50, -228), (0, -218), (50, -228), (120, -236), (200, -210), (290, -100), (220, -34), (170, -80), (170, 236), (-170, 236), (-170, -80), (-220, -34), (-290, -100)]
    J = Paper(pts, kit["c1"], key or f"jb_{kitname}_{number}", rough=2, hatch=True, pattern=kit_pattern(kit, -200, 200))
    col = (30, 28, 28) if (kitname in ("arg", "miami") or sum(kit["c1"]) > 690) else (252, 248, 236)   # texte foncé sur maillot clair
    def dec(d, a):
        ax, ay = a
        d.text((ax, ay-150), name, font=font("title", 64), fill=col, anchor="mm", stroke_width=3, stroke_fill=(30, 28, 28) if col[0] > 200 else (250, 248, 240))
        d.text((ax, ay+50), str(number), font=font("title", 230), fill=col, anchor="mm", stroke_width=5, stroke_fill=(30, 28, 28) if col[0] > 200 else (250, 248, 240))
    return J.add(dec)

def jersey_front(kitname, key=None):
    kit = KITS[kitname]
    pts = [(-200, -210), (-120, -236), (-60, -226), (0, -180), (60, -226), (120, -236), (200, -210), (290, -100), (220, -34), (170, -80), (170, 236), (-170, 236), (-170, -80), (-220, -34), (-290, -100)]
    J = Paper(pts, kit["c1"], key or f"jf_{kitname}", rough=2, hatch=True, pattern=kit_pattern(kit, -200, 200))
    def dec(d, a):
        ax, ay = a
        d.line([(ax-60, ay-226), (ax, ay-180), (ax+60, ay-226)], fill=kit["trim"], width=10)
    return J.add(dec)

def price_tag(txt, key, col=PAL["mustard"]):
    T = Paper([(-40, -90), (200, -90), (260, 0), (200, 90), (-40, 90)], col, key, rough=2, hatch=True)
    def dec(d, a):
        ax, ay = a
        d.ellipse([ax+200, ay-14, ax+228, ay+14], fill=PAL["cream"], outline=PAL["ink"], width=3)
    return T.add(dec)

def scoreboard_sprite(w=760, h=300, key="score"):
    return Paper(rect_pts(w, h), (34, 34, 38), key, rough=1.6)

def pencil_check(d, x, y, s=1.0, col=(46, 150, 80)):
    pencil_line(d, [(x-22*s, y), (x-6*s, y+18*s), (x+24*s, y-22*s)], 1, col, int(9*s), 3, 1.5)

def pencil_cross(d, x, y, s=1.0, col=PAL["red"]):
    pencil_line(d, [(x-20*s, y-20*s), (x+20*s, y+20*s)], 1, col, int(9*s), 4, 1.5)
    pencil_line(d, [(x+20*s, y-20*s), (x-20*s, y+20*s)], 1, col, int(9*s), 5, 1.5)


def silhouette(layer_img, color=(34, 32, 36)):
    """Transforme un calque (joueur…) en silhouette unie, pour les devinettes."""
    sil = Image.new("RGBA", layer_img.size, (*color, 0)); sil.putalpha(layer_img.getchannel("A"))
    sil.info["anchor"] = layer_img.info.get("anchor"); return sil

def _ucl_decor(d, a):
    ax, ay = a
    for sg in (-1, 1):   # les grandes oreilles
        d.arc([ax+sg*70-70, ay-120, ax+sg*70+70, ay+40], 90 if sg < 0 else 270, 270 if sg < 0 else 90, fill=(170, 176, 186), width=18)
    d.ellipse([ax-62, ay-128, ax+62, ay-100], fill=(236, 240, 246))
UCL = Paper(poly_pts([(-66, -118), (66, -118), (58, -20), (26, 40), (18, 110), (54, 128), (54, 152), (-54, 152), (-54, 128), (-18, 110), (-26, 40), (-58, -20)]),
            (206, 212, 222), "ucl", rough=1.5, hatch=True, pad=70).add(_ucl_decor)
