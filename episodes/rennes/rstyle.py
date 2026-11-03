"""Boîte à outils du STYLE RENNES (extraite de episodes/psg_avant_qatar/psg_v2.py) : mots qui claquent, caméra à ressort, palettes,
papercraft (pc_over), tampons, cartes. Un épisode importe `from rstyle import *`, déclare SC (via @scene), CAMS, IMPACTS, fil_rouge."""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RENNES = os.path.join(ROOT, "episodes", "rennes")
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "episodes", "brest_ldc"))
sys.path.insert(0, os.path.join(ROOT, "episodes", "lille_v5")); sys.path.insert(0, RENNES)
from quiz import *
import foot, fx
from brest_ldc import marker
from rgfx import *
import pc_over; pc_over.install(globals()); pc_over.install_v4(globals())
import pc_lib as PC
import motion as M
from motion import El, words, walk, arc, ground_shadow
from paper_cut import paper_player
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PC.KITS["real"] = dict(c1=(246, 246, 242), sleeve=(246, 246, 242), shorts=(246, 246, 242), socks=(246, 246, 242), trim=(120, 60, 160), kind="plain")
PC.KITS["asse"] = dict(c1=(0, 132, 72), sleeve=(0, 132, 72), shorts=(250, 250, 246), socks=(0, 132, 72), trim=(250, 250, 246), kind="plain")

NAVY = (20, 34, 82); PRED = (206, 36, 44)
import pixel as PX
def px_out(out, slug):
    """Dossier / nom de sortie : suffixe _pixel en mode pixel.fc."""
    return (out + "_pixel", slug + "_pixel") if PX.ON else (out, slug)
# ------------------------------------------------------------------ outils (repris de rennes3.py)
def ease(u): u = clamp(u); return u*u*(3 - 2*u)
def eob(u, s=1.9): return ease_out_back(clamp(u), s)
def wob(t, t0, amp=12, f=9, damp=5): return 0 if t < t0 else amp*math.sin((t - t0)*f)*math.exp(-(t - t0)*damp)
def put(L, spr, x, y, s=1.0, rot=0.0, a=1.0):
    if s > .01 and a > .01: blit_sxy(L, spr, x, y, s, s, rot, a)
_sh = {}
def shadowed(spr, key=None):
    k = key or id(spr)
    if k not in _sh:
        im = Image.new("RGBA", (spr.width + 40, spr.height + 40), (0, 0, 0, 0)); a = spr.getchannel("A").point(lambda v: v*110//255)
        sh = Image.new("RGBA", spr.size, (30, 20, 14, 0)); sh.putalpha(a); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (34, 38))
        im.alpha_composite(spr, (20, 20)); ax, ay = spr.info["anchor"]; im.info["anchor"] = (ax + 20, ay + 20); _sh[k] = im
    return _sh[k]
def logo(n, h):
    k = ("logo", n, h)
    if k not in _sh: _sh[k] = shadowed(sticker(n, h), k)
    return _sh[k]
def KW(txt, bg=NOIR, fg=BLANC, size=118): return LBL(txt, f"pqk{txt}{bg}{size}", font("title", size), fg, bg, padx=24, pady=6, rough=3)
def stampl(txt, col=ROUGE, size=150): return LBL(txt, f"pqs{txt}{size}{col}", font("title", size), col, CREME, padx=34, pady=6, rough=2)
def tag(txt, size=60, bg=BLANC, fg=NOIR): return LBL(txt, f"pqt{txt}{size}{bg}", font("title", size), fg, bg, padx=24, pady=8, rough=2)
def mono(txt, size=64, bg=NOIR, fg=BLANC): return LBL(txt, f"pqm{txt}{size}{bg}", font("mono", size), fg, bg, padx=18, pady=6, rough=2)
_tex = {}
def paper_fill(L, col, key):
    if PX.ON: L.paste(PX.near(col) + (255,), (0, 0, L.width, L.height)); return      # pixel.fc : aplat de la palette, pas de grain
    k = (key, L.size, col)
    if k not in _tex:
        w_, h_ = L.size; rng = np.random.default_rng(abs(hash(key)) % 999)
        g = np.asarray(Image.fromarray((rng.random((h_//24 + 2, w_//24 + 2))*255).astype(np.uint8)).resize((w_, h_), Image.BICUBIC), np.float32)/255
        a = np.zeros((h_, w_, 3), np.float32); a[:] = col; a *= (.93 + .12*g)[..., None]
        sp = rng.random((h_, w_)).astype(np.float32); a += ((sp > .965)*14 - (sp < .03)*12)[..., None]
        _tex[k] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    L.paste(_tex[k], (0, 0))
def dark(L, a):
    if a > .01: L.alpha_composite(Image.new("RGBA", L.size, (8, 6, 14, int(255*clamp(a)))))
def stripes_bg(L, a=NAVY, b=PRED, w_=140, key="ps", t=0):
    paper_fill(L, a, key); d = ImageDraw.Draw(L); off = (t*40) % (2*w_)
    if PX.ON: a, b = PX.near(a), PX.near(b); off = int(off//(4*PX.S))*4*PX.S                       # défilement par pas de pixel
    for x in range(-H - 2*w_, L.width + 2*w_, 3*w_): d.polygon([(x + off, 0), (x + w_ + off, 0), (x + w_ + H*.35 + off, L.height), (x + H*.35 + off, L.height)], fill=b)
def apply_cam(L, cx, cy, z, rot=0.0):
    z = max(z, max(W/L.width, H/L.height)); bw, bh = W/z, H/z
    x0 = min(max(cx - bw/2, 0), L.width - bw); y0 = min(max(cy - bh/2, 0), L.height - bh)
    im = L.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.BICUBIC)
    if abs(rot) > .05: im = im.rotate(rot, resample=Image.BICUBIC, fillcolor=im.getpixel((2, 2)))
    return im
_fc = {}
def flip_card(v, size):
    k = (v, size)
    if k not in _fc:
        w_, h_ = int(size*.82), int(size*1.12); im = Image.new("RGBA", (w_, h_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, w_ - 1, h_ - 1], 14, fill=(18, 18, 22)); d.rounded_rectangle([0, 0, w_ - 1, h_//2], 14, fill=(26, 26, 32))
        text_c(d, w_/2, h_/2, str(v), font("title", size), (252, 252, 246)); d.line([(0, h_//2), (w_, h_//2)], fill=(8, 8, 10), width=5)
        _fc[k] = im
    return _fc[k]
def flip_digit(L, x, y, v, t, tc, prev, size=150):
    new, old = flip_card(v, size), flip_card(prev, size); w_, h_ = new.size; x0, y0 = int(x - w_/2), int(y - h_/2)
    u = clamp((t - tc)/.22) if t >= tc else 1
    if u >= 1: L.alpha_composite(new, (x0, y0)); return
    L.alpha_composite(new.crop((0, 0, w_, h_//2)), (x0, y0)); L.alpha_composite(old.crop((0, h_//2, w_, h_)), (x0, y0 + h_//2))
    if u < .5:
        f = old.crop((0, 0, w_, h_//2)); hh = max(1, int(h_//2*math.cos(math.pi*u))); L.alpha_composite(f.resize((w_, hh)), (x0, y0 + h_//2 - hh))
    else:
        f = new.crop((0, h_//2, w_, h_)); hh = max(1, int(h_//2*-math.cos(math.pi*u))); L.alpha_composite(f.resize((w_, hh)), (x0, y0 + h_//2))
def scoreboard(L, x, y, t, seq, left, right, size=150, s_in=1.0):
    if s_in <= .02: return
    put(L, board_base(860, 330, left, right), x, y - 30, s_in)
    if s_in < .95: return
    A, B, pA, pB, tA, tB = 0, 0, 0, 0, -9, -9
    for (ti, a, b) in seq:
        if t >= ti:
            if a != A: pA, A, tA = A, a, ti
            if b != B: pB, B, tB = B, b, ti
    flip_digit(L, x - 210, y, A, t, tA, pA, size); flip_digit(L, x + 210, y, B, t, tB, pB, size)
    ImageDraw.Draw(L).rounded_rectangle([x - 36, y - 10, x + 36, y + 10], 6, fill=(250, 220, 120))
def board_in(t, t0, t1=None):
    v = M.spring(t - t0, .5, 12)
    if t1 is not None and t > t1: v *= 1 - M.ease_in((t - t1)/.2)
    return v
def ball(L, fr, x, y, s, t, ground=None):
    if ground is not None: ground_shadow(L, x, ground, 40*s*max(.3, 1 - (ground - y)/900), .3)
    foot.draw_ball(L, fr, x, y, s, t*520)
def cursor():
    if "cur" not in _fc:
        im = Image.new("RGBA", (140, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        pts = [(10, 10), (10, 150), (48, 112), (74, 176), (100, 164), (74, 102), (124, 102)]
        d.polygon([(x + 6, y + 6) for x, y in pts], fill=(0, 0, 0, 90)); d.polygon(pts, fill=BLANC, outline=NOIR); d.line(pts + [pts[0]], fill=NOIR, width=6)
        im.info["anchor"] = (10, 10); _fc["cur"] = im
    return _fc["cur"]
def sparks_burst(L, t, t0, x, y, n=12, col=(255, 230, 120), dist=220):
    u = (t - t0)/.45
    if not 0 < u < 1: return
    d = ImageDraw.Draw(L)
    for k in range(n):
        a = 2*math.pi*k/n; r0, r1 = dist*M.ease_out(u)*.6, dist*M.ease_out(u)
        d.line([(x + r0*math.cos(a), y + r0*math.sin(a)), (x + r1*math.cos(a), y + r1*math.sin(a))], fill=col, width=max(2, int(10*(1 - u))))
def puffs(L, t, t0, x, y, n=10, col=(210, 196, 170), spread=260, dur=.6):
    u = (t - t0)/dur
    if not 0 < u < 1: return
    d = ImageDraw.Draw(L)
    for k in range(n):
        a = math.pi*(k + .5)/n; r_ = spread*M.ease_out(u); rr = 26*(1 - u) + 6
        d.ellipse([x + r_*math.cos(a) - rr, y - r_*.35*math.sin(a) - rr, x + r_*math.cos(a) + rr, y - r_*.35*math.sin(a) + rr], fill=col)
def marker_line(L, p0, p1, u, col=ROUGE, wd=14):
    if u <= 0: return
    ImageDraw.Draw(L).line([p0, (lerp(p0[0], p1[0], clamp(u)), lerp(p0[1], p1[1], clamp(u)))], fill=col, width=wd)
PHOTO = os.path.join(ROOT, "assets", "photos", "psg")
BOX = {}
def CUT(slug, h):
    k = ("cut", slug, h)
    if k not in _sh: _sh[k] = paper_player(os.path.join(PHOTO, slug + ".png"), BOX.get(slug), h)
    return _sh[k]
def qatar_flag(L, x, y, t, s=1.0):
    w_, h_ = int(560*s), int(340*s); im = Image.new("RGBA", (w_ + 40, h_ + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([20, 20, 20 + w_, 20 + h_], fill=(138, 21, 56)); band = w_*.3; n = 9; pts = [(20, 20), (20 + band, 20)]
    for k in range(n): y0 = 20 + h_*k/n; pts += [(20 + band + w_*.08, y0 + h_/n/2), (20 + band, y0 + h_/n)]
    d.polygon(pts + [(20, 20 + h_)], fill=(250, 248, 240))
    a = np.asarray(im); out = np.zeros_like(a)
    for xx in range(0, a.shape[1]): out[:, xx] = np.roll(a[:, xx], int(10*math.sin(xx/70 - t*4)*(xx/a.shape[1])), 0)
    sp = Image.fromarray(out); sp.info["anchor"] = (20, 20); put(L, sp, x - w_/2, y - h_/2, 1, -3)
    d2 = ImageDraw.Draw(L); d2.rectangle([x - w_/2 - 26, y - h_/2 - 10, x - w_/2 - 8, y + h_/2 + 420], fill=(120, 90, 60))

SC = []; CAMS = {}; IMPACTS = []; PUNCH = []
def scene(t0, trans="cut", td=.3):
    def deco_(fn): SC.append(dict(t0=t0, fn=fn, size=(W, H), trans=trans, td=td, name=fn.__name__)); return fn
    return deco_
def punch(t): return 1 + sum(.06*math.exp(-((t - p)/.11)**2) for p in PUNCH if p - .4 < t < p + .5)
FIL = [None]                                                     # FIL[0] = fonction fil_rouge(cv, fr, t) de l'épisode
POST = [None]                                                    # POST[0] = fonction (cv, fr, t) dessinée après la caméra (sous-titres…)
# ------------------------------------------------------------------ rendu + transitions (repris de rennes3.py)
def render_scene(i, fr, t):
    s = SC[i]; L = Image.new("RGBA", s["size"], (0, 0, 0, 255)); s["fn"](L, fr, t)
    cx, cy, z = M.cam_spring(CAMS[s["name"]], t); z *= punch(t)
    sx_, sy_, sr = M.trauma_offset(t, IMPACTS)
    return apply_cam(L, cx + 4*math.sin(t*.9) + sx_, cy + 3*math.cos(t*.7) + sy_, z, .3*math.sin(t*.6) + sr).convert("RGB")
def scene_at(t):
    k = 0
    for i, s in enumerate(SC):
        if t >= s["t0"]: k = i
    return k
def frame(fr, t):
    k = scene_at(t); s = SC[k]; cur = render_scene(k, fr, t)
    u = (t - s["t0"])/s["td"] if k else 1
    if u < 1:
        prev = render_scene(k - 1, fr, t); tr = s["trans"]; e = M.ease_io(u)
        if tr == "whip":
            off = int(W*e); out = Image.new("RGB", (W, H)); out.paste(prev, (-off, 0)); out.paste(cur, (W - off, 0))
            fx.whip_blur(out, -110*math.sin(math.pi*u), 0, 7); cur = out
        elif tr == "tear": tear_transition(cur, prev, u, "tear_v", k)
    if PX.ON:                                                    # pixel.fc : pixelisation de la scène + fil rouge, puis sous-titres nets en police pixel
        cur = PX.pixelate(cur).convert("RGBA"); (FIL[0] or (lambda *a: None))(cur, fr, t)
        (POST[0] or (lambda *a: None))(cur, fr, t); PX.scanlines(cur); return cur.convert("RGB")
    fx.dust(cur, t, 22)
    cur = cur.convert("RGBA"); fx.vignette(cur, 90); (FIL[0] or (lambda *a: None))(cur, fr, t); (POST[0] or (lambda *a: None))(cur, fr, t)
    return cur.convert("RGB")
