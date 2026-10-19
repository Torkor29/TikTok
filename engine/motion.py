"""Système de mouvement « pro » (voir MOTION.md) : ressorts, cycle de vie entrée/idle/sortie, squash & stretch,
follow-through, cycles de marche, arcs de ballon, secousse « trauma »."""
import math
from PIL import Image, ImageDraw
from engine import blit_sxy, boil, clamp, lerp

def spring(a, zeta=.45, w=15.0):
    """Réponse d'un ressort amorti (0 -> 1 avec dépassement) au temps a (s) depuis le départ."""
    if a <= 0: return 0.0
    wd = w*math.sqrt(1 - zeta*zeta)
    return 1 - math.exp(-zeta*w*a)*(math.cos(wd*a) + zeta*w/wd*math.sin(wd*a))
def ease_in(u): u = clamp(u); return u*u*u
def ease_out(u): u = clamp(u); return 1 - (1 - u)**3
def ease_io(u): u = clamp(u); return 4*u**3 if u < .5 else 1 - (-2*u + 2)**3/2

def sprite_of(obj, fr):
    """Sprite RGBA (avec ancre) depuis un sprite, un Label (3 variantes boil) ou une fonction(fr)."""
    if hasattr(obj, "v"): return obj.v[boil(fr)]
    if callable(obj): return obj(fr)
    return obj

class El:
    """Élément animé. x, y en coordonnées de scène. t_out=None : reste jusqu'à la fin de la scène."""
    def __init__(self, obj, x, y, t_in, t_out=None, inn="pop", out="shrink", s=1.0, rot=0.0, idle=1.0, d_out=.22, seed=0,
                 dist=900, alpha=1.0):
        self.o, self.x, self.y, self.t_in, self.t_out = obj, x, y, t_in, t_out
        self.inn, self.out, self.s, self.rot, self.idle, self.d_out, self.seed, self.dist, self.alpha = inn, out, s, rot, idle, d_out, seed, dist, alpha
    def state(self, t):
        a = t - self.t_in
        if a < -.07: return None
        x, y, sx, sy, r, al = self.x, self.y, self.s, self.s, self.rot, self.alpha
        k = self.inn
        if k == "pop":
            v = spring(a); sx *= v; sy *= v; al *= clamp(a/.05)
        elif k == "stamp":                                          # anticipation, impact, écrasement
            if a < 0: return None
            if a < .1: f = 1.9 - .9*(a/.1)**2; sx *= f; sy *= f; al *= clamp(a/.04); r += 10*(1 - a/.1)
            else:
                b = a - .1; q = .16*math.exp(-b*18)*math.cos(b*40); sx *= 1 + q; sy *= 1 - q
        elif k == "drop":                                           # chute accélérée + écrasement
            fall = .26
            if a < fall: y -= self.dist*(1 - (a/fall)**2); sy *= 1.08; sx *= .94; al *= clamp(a/.05)
            else:
                b = a - fall; q = .2*math.exp(-b*14)*math.cos(b*30); sy *= 1 - q; sx *= 1 + q*.8
                y += 30*q
        elif k in ("slide_l", "slide_r", "rise", "fall_in"):
            v = spring(a, .5, 12); dx, dy = {"slide_l": (-self.dist, 0), "slide_r": (self.dist, 0), "rise": (0, self.dist), "fall_in": (0, -self.dist)}[k]
            x += dx*(1 - v); y += dy*(1 - v); al *= clamp(a/.06)
            vel = spring(a + .016, .5, 12) - v; r += -dx*vel*.06 + dy*vel*.0          # penche dans le sens du mouvement
        elif k == "none":
            al *= clamp(a/.12)
        if self.idle and a > .4:                                    # respiration
            x += 3*self.idle*math.sin(t*2.1 + self.seed); y += 3*self.idle*math.cos(t*1.7 + self.seed*1.3)
            r += .8*self.idle*math.sin(t*1.5 + self.seed*.7)
        if self.t_out is not None and t > self.t_out:
            u = clamp((t - self.t_out)/self.d_out)
            if u >= 1: return None
            e = ease_in(u)
            if self.out == "shrink": sx *= 1 - .3*e; sy *= 1 - .3*e; al *= 1 - e
            elif self.out == "fly": y -= 260*e; r += 12*e; al *= 1 - e
            elif self.out == "drop_out": y += 700*e*e; r -= 25*e; al *= 1 - e*e
            elif self.out == "fade": al *= 1 - e
            elif self.out == "slide_l": x -= 1200*e
            elif self.out == "slide_r": x += 1200*e
        return x, y, sx, sy, r, al
    def draw(self, L, fr, t):
        st = self.state(t)
        if not st: return
        x, y, sx, sy, r, al = st
        if sx < .02 or sy < .02 or al < .02: return
        blit_sxy(L, sprite_of(self.o, fr), x, y, sx, sy, r, min(1, al))

def draw_all(L, fr, t, els):
    for e in els: e.draw(L, fr, t)

def words(make, items, x, y, maxw=960, gap=20, out=None, inn="stamp", rot=(-3, 2, -2, 3), lh=None):
    """Ligne de mots : items = [(mot, t)] -> liste d'El positionnés (centrés, retour à la ligne)."""
    labs = [make(w, i) for i, (w, _) in enumerate(items)]
    ws = [l.v[0].width - 30 for l in labs]; hs = [l.v[0].height for l in labs]; lh = lh or max(hs) - 18
    lines, cur, cw = [], [], 0
    for i, wd in enumerate(ws):
        if cur and cw + wd > maxw: lines.append(cur); cur, cw = [], 0
        cur.append(i); cw += wd + gap
    lines.append(cur); out_ = []
    y0 = y - (len(lines) - 1)*lh/2
    for li, ids in enumerate(lines):
        tw = sum(ws[i] for i in ids) + gap*(len(ids) - 1); xx = x - tw/2
        for i in ids:
            out_.append(El(labs[i], xx + ws[i]/2, y0 + li*lh, items[i][1], out, inn, "shrink", 1, rot[i % len(rot)], .5, seed=i))
            xx += ws[i] + gap
    return out_

# ------------------------------------------------------------------ cycles
def walk(t, speed=9.0, amp=28):
    """(jambes, bras, rebond) pour un cycle de marche / course."""
    ph = t*speed; s = math.sin(ph)
    return (amp*s, -amp*s), (18 - amp*.7*s, 18 + amp*.7*s), -7*abs(math.cos(ph))
def arc(p0, p1, h, u):
    u = clamp(u); return lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u) - 4*h*u*(1 - u)
def ground_shadow(L, x, y, w, a=.35):
    if w <= 2: return
    ov = Image.new("RGBA", (int(w*2) + 4, int(w*.5) + 4), (0, 0, 0, 0))
    ImageDraw.Draw(ov).ellipse([2, 2, int(w*2), int(w*.5)], fill=(0, 0, 0, int(255*a)))
    L.alpha_composite(ov, (int(x - w), int(y - w*.25)))

# ------------------------------------------------------------------ caméra
def trauma_offset(t, impacts, dur=.32, amp=22):
    """Secousse « trauma » : somme de sinus incommensurables, amplitude ∝ trauma² qui décroît."""
    tr = 0
    for p in impacts:
        if p <= t < p + dur: tr = max(tr, 1 - (t - p)/dur)
    if tr <= 0: return 0, 0, 0
    k = tr*tr*amp
    return (k*(math.sin(t*71) + .5*math.sin(t*113 + 1)), k*(math.sin(t*83 + 2) + .5*math.sin(t*127)), k*.06*math.sin(t*97))
def cam_spring(keys, t, zeta=.75, w=7.0):
    """Caméra : chaque keyframe est une cible atteinte par ressort (léger dépassement), pas une interpolation linéaire."""
    if t <= keys[0][0]: return keys[0][1:]
    cur = list(keys[0][1:])
    for i in range(1, len(keys)):
        tk = keys[i][0]
        if t < tk: break
        prev = cur; tgt = keys[i][1:]; a = t - tk
        nxt = keys[i + 1][0] if i + 1 < len(keys) else 1e9
        a = min(a, nxt - tk)
        v = spring(a, zeta, w); cur = [p + (q - p)*v for p, q in zip(prev, tgt)]
    return tuple(cur)
