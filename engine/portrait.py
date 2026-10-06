"""
portrait.py — gros plans papier « ultra détaillés » (tête + épaules) pour les moments d'émotion.

Même identité que le reste (papier déchiré, gouache, crayon), mais beaucoup plus de couches :
mèches de cheveux, barbe en hachures (avec poils gris), oreilles, nez ombré, yeux avec iris / reflet / paupières,
larmes qui coulent sur la joue, maillot rayé avec col et plis, brassard de capitaine, main sur le cœur.

  P = Portrait("leo26", style="adult", grey=.25)
  P.draw(cv, fr, CX, 900, s=1.3, mood="cry", tears=t, t=t, tilt=-3)

style : "young" (cheveux longs, pas de barbe), "mid" (cheveux courts, barbe naissante), "adult" (barbe pleine).
mood  : neutral | smile | cheer | sad | cry | emotional | proud | determined
"""
import math, random
import numpy as np
from foot import *

SKIN_P = (226, 178, 142)
SKIN_D = (196, 142, 108)     # ombres de la peau
HAIR_P = (58, 40, 30)
BEARD_P = (70, 50, 36)

def _egg(w, h, n=48, jaw=.2):
    """Contour de tête : large en haut, mâchoire plus fine en bas (y vers le bas)."""
    pts = []
    for i in range(n):
        a = 2*math.pi*i/n; s, c = math.sin(a), math.cos(a)
        pts.append((w/2*c*(1 - jaw*max(0, s)**1.6), h/2*s))
    return pts

def _strands(cx, cy, w, h, n, seed, down=True):
    """Mèches pointues le long d'un bord (frange, côtés)."""
    rnd = random.Random(seed); pts = []
    for i in range(n + 1):
        u = i/n; x = cx - w/2 + w*u
        pts.append((x, cy))
        if i < n:
            xm = x + w/n*.5 + rnd.uniform(-6, 6)
            pts.append((xm, cy + (h if down else -h)*rnd.uniform(.55, 1.0)))
    return pts

def clip_add(paper, fn):
    """Comme Paper.add, mais le décor ne déborde pas de la forme (seulement là où le papier est opaque)."""
    for i, im in enumerate(paper.v):
        top = im.copy(); fn(ImageDraw.Draw(top), im.info["anchor"])
        m = im.getchannel("A").point(lambda v: 255 if v > 200 else 0)
        out = Image.composite(top, im, m); out.info["anchor"] = im.info["anchor"]; paper.v[i] = out
    return paper

class Portrait:
    _shade = {}

    def __init__(self, key, style="adult", grey=0.0, skin=SKIN_P, hair=HAIR_P, beard=BEARD_P, kit="arg", armband=True):
        self.key, self.style, self.grey, self.skin, self.hair_col, self.kit = key, style, grey, skin, hair, kit
        self.armband = armband
        K = KITS[kit]; k = key
        # ---- maillot (épaules), rayures + col + plis
        torso = [(-500, 980), (-492, 470), (-460, 360), (-370, 292), (-210, 250), (-96, 236), (0, 262), (96, 236), (210, 250),
                 (370, 292), (460, 360), (492, 470), (500, 980)]
        def stripes(d, ox, oy):
            n = 9; w = 1000/n
            for i in range(n):
                d.rectangle([ox - 500 + i*w, 0, ox - 500 + (i+1)*w, 4000], fill=K["c1"] if i % 2 == 0 else K["c2"])
            if K["kind"] != "stripes":
                d.rectangle([0, 0, 4000, 4000], fill=K["c1"])
        self.torso = Paper(torso, K["c1"], k+"torso", rough=2.2, hatch=True, pattern=stripes)
        trim = K["trim"]
        def collar(d, a):
            ax, ay = a
            d.line([(ax-104, ay+238), (ax-48, ay+262), (ax, ay+270), (ax+48, ay+262), (ax+104, ay+238)], fill=trim, width=16)
            for sx in (-1, 1):   # plis du tissu
                d.line([(ax+sx*300, ay+420), (ax+sx*250, ay+560), (ax+sx*262, ay+700)], fill=(120, 130, 150), width=3)
                d.line([(ax+sx*140, ay+520), (ax+sx*120, ay+640)], fill=(140, 150, 170), width=2)
            for sx in (-1, 1):   # coutures d'épaule
                d.line([(ax+sx*210, ay+256), (ax+sx*400, ay+330)], fill=(110, 120, 140), width=3)
        self.torso.add(collar)
        self.band = Paper([(-62, -40), (62, -28), (62, 30), (-62, 22)], (250, 250, 246), k+"band", rough=1.4).add(
            lambda d, a: [d.rectangle([a[0]-62, a[1]-14, a[0]+62, a[1]+6], fill=(110, 170, 226)),
                          d.text((a[0], a[1]-4), "C", font=font("title", 44), fill=(30, 28, 28), anchor="mm")])
        # ---- cou, oreilles, tête, nez
        self.neck = Paper([(-80, 80), (80, 80), (92, 300), (-92, 300)], SKIN_D, k+"neck", rough=1.2, shadow=False)
        ear = ellipse_pts(58, 98, 24)
        self.ear = Paper(ear, skin, k+"ear", rough=1.2).add(
            lambda d, a: d.arc([a[0]-16, a[1]-30, a[0]+16, a[1]+30], 100, 300, fill=SKIN_D, width=6))
        self.head = Paper(_egg(306, 392, jaw=.24 if style != "young" else .18), skin, k+"head", rough=1.5)
        def cheeks(d, a):
            ax, ay = a
            for sx in (-1, 1):
                d.ellipse([ax+sx*92-30, ay+40, ax+sx*92+30, ay+76], fill=(232, 160, 140))
        clip_add(self.head, cheeks)
        self.nose = Paper([(-2, -6), (10, -4), (24, 30), (36, 52), (24, 64), (0, 60), (-24, 64), (-34, 52), (-16, 30)],
                          tuple(int(c*.97) for c in skin), k+"nose", rough=.8, shadow=False, outline=False)
        clip_add(self.nose, lambda d, a: [d.polygon([(a[0]+10, a[1]-4), (a[0]+26, a[1]+32), (a[0]+36, a[1]+52), (a[0]+20, a[1]+50), (a[0]+12, a[1]+20)], fill=SKIN_D),
                                          d.ellipse([a[0]-22, a[1]+48, a[0]-8, a[1]+57], fill=(140, 86, 64)),
                                          d.ellipse([a[0]+8, a[1]+48, a[0]+22, a[1]+57], fill=(140, 86, 64))])
        # ---- cheveux
        if style == "young":   # longs, raie au milieu, couvrent les oreilles
            back = [(-200, 120), (-206, -20), (-190, -140), (-140, -210), (-60, -244), (40, -244), (140, -212), (192, -142), (208, -20),
                    (200, 120), (176, 150), (150, 128), (0, 60), (-150, 128), (-176, 150)]
            front = [(-184, 110), (-182, -40), (-164, -150), (-112, -210), (-30, -232), (0, -214), (30, -232), (112, -210), (164, -150),
                     (182, -40), (184, 110), (166, 128), (160, 40), (148, -50)] + list(reversed(_strands(0, -92, 300, 64, 8, k+"fr"))) + \
                    [(-148, -50), (-160, 40), (-166, 128)]
        else:                  # courts sur les côtés, plus longs dessus, coiffés vers le côté
            back = [(-160, 20), (-162, -100), (-130, -180), (-60, -222), (30, -226), (110, -200), (156, -130), (162, 20), (150, 0), (0, -60), (-150, 0)]
            front = [(-158, -10), (-160, -110), (-128, -186), (-60, -232), (20, -240), (100, -218), (152, -158), (160, -40), (150, -70)] + \
                    list(reversed(_strands(-6, -140, 300, 46, 7, k+"fr")))
        self.hair_back = Paper(back, tuple(int(c*.8) for c in hair), k+"hairb", rough=2.6, hatch=True)
        def hair_lines(d, a):
            ax, ay = a; rnd = random.Random(k)
            for _ in range(26):
                x = ax + rnd.uniform(-140, 140); y = ay + rnd.uniform(-220, -120)
                d.line([(x, y), (x + rnd.uniform(-30, 30), y + rnd.uniform(30, 70))], fill=tuple(min(255, c+46) for c in hair), width=3)
        self.hair = clip_add(Paper(front, hair, k+"hair", rough=2.4, hatch=True), hair_lines)
        # ---- barbe + moustache (adulte), barbe naissante (mid)
        self.beard = None
        if style in ("adult", "mid"):
            col = beard if style == "adult" else tuple(int(lerp(c, s_, .55)) for c, s_ in zip(beard, skin))
            bpts = [(-150, 10), (-136, 70), (-112, 128), (-74, 176), (-30, 206), (0, 212), (30, 206), (74, 176), (112, 128),
                    (136, 70), (150, 10), (128, 40), (96, 74), (60, 84), (0, 78), (-60, 84), (-96, 74), (-128, 40)]
            g = grey
            def stubble(d, a):
                ax, ay = a; rnd = random.Random(k+"st")
                for _ in range(260):
                    x = ax + rnd.uniform(-140, 140); y = ay + rnd.uniform(20, 200)
                    gr = rnd.random() < g
                    c = (196, 192, 186) if gr else tuple(max(0, c_-24) for c_ in col)
                    d.line([(x, y), (x + rnd.uniform(-3, 3), y + rnd.uniform(5, 10))], fill=c, width=2)
            self.beard = clip_add(Paper(bpts, col, k+"beard", rough=3.0, hatch=True, shadow=False), stubble)
            self.mous = Paper([(-62, 0), (-30, -14), (0, -8), (30, -14), (62, 0), (40, 12), (0, 6), (-40, 12)], col, k+"mous", rough=1.6, shadow=False)
        hand = [(-96, -40), (-30, -52), (40, -50), (92, -46), (112, -36), (104, -24), (60, -24), (110, -12), (118, 2), (108, 12),
                (62, 10), (108, 24), (112, 38), (100, 46), (58, 38), (94, 56), (94, 70), (80, 76), (30, 64), (-30, 70), (-96, 56)]
        self.hand = Paper(hand, skin, k+"hand", rough=1.0)
        clip_add(self.hand, lambda d, a: [d.line([(a[0]+10, a[1]+yy), (a[0]+70, a[1]+yy+2)], fill=SKIN_D, width=3) for yy in (-24, 10, 40)] +
                 [d.ellipse([a[0]+86, a[1]-42, a[0]+104, a[1]-28], fill=(240, 206, 186))])

    # ---------------------------------------------------------------- dessin
    def _shading(self, w, h):
        k = (w, h)
        if k not in Portrait._shade:
            xx = np.linspace(0, 1, w)[None, :]; yy = np.linspace(0, 1, h)[:, None]
            Portrait._shade[k] = (1.05 - .22*xx - .10*yy).astype(np.float32)   # lumière de gauche, plus sombre en bas à droite
        return Portrait._shade[k]

    def draw(self, cv, fr, x, y, s=1.0, mood="neutral", look=(0, 0), tears=0.0, t=0.0, tilt=0.0, hand=0.0, alpha=1.0,
             light=True, blink=True):
        """x, y = centre du visage. tears = temps depuis le début des larmes (0 = pas de larmes). hand = 0 → 1 : main sur le cœur."""
        if alpha <= .01 or s <= .01: return
        W_, H_ = int(1200*s), int(1500*s)
        L = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); ox, oy = W_/2, 380*s
        a = math.radians(tilt); ca, sa = math.cos(a), math.sin(a)
        def P(px, py):   # repère tête -> calque (même rotation que blit)
            return ox + s*(px*ca + py*sa), oy + s*(-px*sa + py*ca)
        def put(paper, px, py, rot=0.0, sc=1.0):
            X, Y = P(px, py); paper.draw(L, fr, X, Y, s*sc, tilt + rot, 1, 1.0)
        put(self.torso, 0, 0)
        if self.armband: put(self.band, -452, 640, 82, 1.25)
        put(self.neck, 0, 0)
        if self.style == "young" or True: put(self.hair_back, 0, 0)
        for sx in (-1, 1): put(self.ear, sx*150, 16, sx*-6)
        put(self.head, 0, 0)
        if self.beard is not None: put(self.beard, 0, 0)
        put(self.nose, 0, 10)
        self._face(L, P, s, mood, look, t, blink)
        if self.beard is not None and mood not in ("cheer",): put(self.mous, 0, 92)
        put(self.hair, 0, 0)
        if tears > 0: self._tears(L, P, s, tears, mood)
        if hand > 0:
            u = ease_out_cubic(clamp(hand))
            put(self.hand, lerp(40, 150, u), lerp(1100, 560, u), 12)
        if light:   # volume : lumière qui vient de la gauche
            arr = np.asarray(L, dtype=np.float32); sh = self._shading(W_, H_)
            arr[..., :3] = np.clip(arr[..., :3]*sh[..., None], 0, 255)
            L = Image.fromarray(arr.astype(np.uint8), "RGBA")
        L.info["anchor"] = (ox, oy)
        blit(cv, L, x, y, 1.0, 0, alpha)

    def _face(self, L, P, s, mood, look, t, blink):
        d = ImageDraw.Draw(L); INKc = (34, 26, 22)
        lx, ly = look[0]*7, look[1]*5
        closed = blink and (int(t*24) % 84) < 3
        squeeze = mood in ("cry", "proud")
        for sg in (-1, 1):
            ex, ey = sg*64, -6
            # orbite légèrement ombrée
            d.line([P(ex-30, ey-22), P(ex, ey-28), P(ex+30, ey-20)], fill=(196, 140, 108), width=max(2, int(3*s)), joint="curve")
            if closed or squeeze:
                c = [P(ex-30, ey+2), P(ex, ey + (-10 if mood == "proud" else 8)), P(ex+30, ey+2)]
                d.line(c, fill=INKc, width=max(3, int(7*s)), joint="curve")
                if mood == "cry":   # plis de la paupière serrée
                    d.line([P(ex-26, ey+16), P(ex, ey+20), P(ex+26, ey+16)], fill=(170, 116, 90), width=max(2, int(3*s)))
            else:
                wide = 1.15 if mood in ("cheer", "surprised") else (.85 if mood in ("smile", "sad", "emotional") else 1.0)
                eye = [P(ex+dx, ey+dy*wide) for dx, dy in ((-32, 2), (-18, -14), (6, -17), (28, -6), (32, 2), (14, 13), (-14, 13))]
                d.polygon(eye, fill=(250, 246, 238))
                ix, iy = P(ex+lx, ey+ly)
                r = 14*s; d.ellipse([ix-r, iy-r, ix+r, iy+r], fill=(98, 66, 40))
                r2 = 8*s; d.ellipse([ix-r2, iy-r2, ix+r2, iy+r2], fill=(20, 14, 12))
                hx, hy = ix-5*s, iy-6*s; d.ellipse([hx-4.5*s, hy-4.5*s, hx+4.5*s, hy+4.5*s], fill=(255, 255, 255))
                if mood in ("emotional", "sad", "cry"):   # yeux qui brillent
                    d.ellipse([ix+3*s, iy+2*s, ix+7*s, iy+6*s], fill=(255, 255, 255))
                    d.line([P(ex-26, ey+12), P(ex+26, ey+12)], fill=(150, 200, 236), width=max(2, int(4*s)))
                d.line([P(ex-34, ey+2), P(ex-18, ey-15*wide), P(ex+6, ey-18*wide), P(ex+30, ey-6)], fill=INKc, width=max(3, int(7*s)), joint="curve")
                d.line([P(ex-28, ey+12), P(ex+24, ey+12)], fill=(170, 116, 90), width=max(1, int(2*s)))
            # sourcils (épais, effilés)
            inner = {"sad": -14, "cry": -18, "emotional": -10, "determined": 10, "cheer": -12, "surprised": -14}.get(mood, 0)
            outer = {"cheer": -10, "surprised": -14}.get(mood, 0)
            bi, bo = (ex - sg*26, ey-46+inner), (ex + sg*36, ey-40+outer)
            th = 9
            br = [P(bi[0], bi[1]-th), P((bi[0]+bo[0])/2, (bi[1]+bo[1])/2 - th - 4), P(bo[0], bo[1]-2), P(bo[0], bo[1]+2),
                  P((bi[0]+bo[0])/2, (bi[1]+bo[1])/2 + 3), P(bi[0], bi[1]+th)]
            d.polygon(br, fill=self.hair_col)
        # bouche
        my = 120
        lip = (150, 70, 60); dark = (70, 26, 26)
        if mood == "cheer":
            m = [P(dx, my+dy) for dx, dy in ((-46, -14), (-20, -22), (20, -22), (46, -14), (34, 30), (0, 46), (-34, 30))]
            d.polygon(m, fill=dark)
            d.polygon([P(-38, my-14), P(38, my-14), P(32, my-2), P(-32, my-2)], fill=(250, 248, 240))
            d.ellipse([*P(-18, my+18), *P(18, my+40)], fill=(196, 90, 90))
        elif mood in ("smile", "proud"):
            d.chord([*P(-44, my-26), *P(44, my+22)], 0, 180, fill=dark)
            d.polygon([P(-36, my-2), P(36, my-2), P(30, my+8), P(-30, my+8)], fill=(250, 248, 240))
            d.line([P(-48, my-6), P(-40, my+2)], fill=lip, width=max(2, int(4*s)))
            d.line([P(48, my-6), P(40, my+2)], fill=lip, width=max(2, int(4*s)))
        elif mood == "cry":
            wob = 3*math.sin(t*22)
            m = [P(dx, my+dy+wob*(1 if dx else 0)) for dx, dy in ((-40, 14), (-20, -2), (20, -2), (40, 14), (22, 22), (-22, 22))]
            d.polygon(m, fill=dark)
        elif mood in ("sad", "emotional"):
            d.line([P(-34, my+10), P(-14, my), P(14, my), P(34, my+10)], fill=lip, width=max(3, int(7*s)), joint="curve")
        elif mood == "determined":
            d.line([P(-32, my+2), P(32, my+2)], fill=lip, width=max(3, int(7*s)))
        else:
            d.line([P(-30, my+2), P(0, my+5), P(30, my+2)], fill=lip, width=max(3, int(6*s)), joint="curve")

    def _tears(self, L, P, s, tt, mood):
        """Larme qui coule le long de la joue + gouttes qui tombent du menton."""
        d = ImageDraw.Draw(L)
        for sg in (-1, 1) if mood == "cry" else (1,):
            u = clamp(tt/1.2)
            x0, y0 = sg*58, 10
            path = [(x0 + sg*8*math.sin(k*.5), y0 + 26*k) for k in range(int(1 + 7*u))]
            if len(path) > 1:
                d.line([P(*p) for p in path], fill=(160, 210, 240), width=max(3, int(9*s)), joint="curve")
                d.line([P(p[0]-3, p[1]) for p in path], fill=(236, 248, 255), width=max(1, int(3*s)))
            ex, ey = P(*path[-1]); r = 8*s
            d.polygon([(ex, ey-r*1.4), (ex+r*.8, ey), (ex, ey+r), (ex-r*.8, ey)], fill=(160, 210, 240))
        if mood == "cry" and tt > .8:
            drops(L, "chin"+self.key, tt-.8, [P(-20, 214), P(24, 214)], n=3, size=9*s, speed=560*s)
