"""Micro-animations « papier » réutilisables (inspirées de la règle Crochet : aucun plan fixe, chaque phrase = mouvement + micro-animation).

- kinetic()      : mots qui tombent un par un (calés sur la voix), rebond + rotation
- wipe()         : étiquette / surligneur qui se dessine de gauche à droite + reflet qui glisse
- typed_cursor() : texte tapé lettre par lettre avec curseur qui clignote
- bob()          : flottement léger (à ajouter aux positions)
- ecg()          : ligne de battement de cœur + pulsation rouge des bords
- dot_grid()     : grille de points qui se remplit (bilan d'une saison…)
- shockwave()    : onde de choc (anneau qui grossit)
- whip_blur()    : flou de mouvement horizontal/vertical pendant un travelling rapide
- desat()        : arrêt sur image (désaturé, assombri)
- dust(), vignette() : ambiance permanente
- sfx_variants() : variantes de hauteur des bruitages (jamais deux fois le même son à l'identique)
"""
import math, os, random, subprocess, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import W, H, clamp, prog, ease_out_back, ease_out_cubic, font, blit, boil

def bob(t, seed, amp=5.0, speed=1.7):
    return amp*math.sin(t*speed + seed*1.37), amp*.6*math.cos(t*speed*.8 + seed*2.1)

# ---------------------------------------------------------------- textes
def kinetic(cv, fr, t, words, x, y, make, maxw=980, gap=18, lh=None, rot=(-4, 3, -2, 4, -3, 2)):
    """words = [(mot, t_apparition)] ; make(mot, i) -> Label. Mise en lignes centrée, chaque mot tombe (1.45 -> 1)."""
    labs = [(make(wd, i), t0) for i, (wd, t0) in enumerate(words)]
    ws = [l.v[0].width - 30 for l, _ in labs]; hs = [l.v[0].height for l, _ in labs]
    lh = lh or max(hs) - 20
    lines, cur, cw = [], [], 0
    for i, wdt in enumerate(ws):
        if cur and cw + wdt > maxw: lines.append(cur); cur, cw = [], 0
        cur.append(i); cw += wdt + gap
    lines.append(cur)
    y0 = y - (len(lines) - 1)*lh/2
    for li, ids in enumerate(lines):
        tw = sum(ws[i] for i in ids) + gap*(len(ids) - 1); xx = x - tw/2
        for i in ids:
            lab, t0 = labs[i]
            if t >= t0:
                u = clamp((t - t0)/.22); s = 1 + .45*(1 - ease_out_back(u, 2.2)) if u < 1 else 1
                r = rot[i % len(rot)]*(1 + 1.5*(1 - u))
                lab.draw(cv, fr, xx + ws[i]/2, y0 + li*lh - 40*(1 - u), s, r)
            xx += ws[i] + gap

def wipe(cv, fr, lab, x, y, t, t0, rot=0.0, d=.28, scale=1.0, glint=True):
    """Label (story.LBL / marker) révélé de gauche à droite, puis reflet blanc qui glisse."""
    if t < t0: return
    u = ease_out_cubic(clamp((t - t0)/d)); spr = lab.v[boil(fr)]
    w_ = max(1, int(spr.width*u)); im = spr.crop((0, 0, w_, spr.height)); im.info["anchor"] = spr.info["anchor"]
    if glint and u >= 1:
        g = clamp((t - t0 - d)/.45)
        if 0 < g < 1:
            im = im.copy(); gl = Image.new("RGBA", im.size, (0, 0, 0, 0)); dg = ImageDraw.Draw(gl)
            gx = -120 + g*(im.width + 240)
            dg.polygon([(gx, 0), (gx + 60, 0), (gx + 20, im.height), (gx - 40, im.height)], fill=(255, 255, 255, 120))
            a = im.getchannel("A"); im.alpha_composite(gl); im.putalpha(a)
    blit(cv, im, x, y, scale, rot)

def typed_cursor(txt, t, t0, cps=16):
    n = int(max(0, t - t0)*cps); s = txt[:n]
    return s + ("█" if (n < len(txt) or int(t*3) % 2 == 0) else " ")

# ---------------------------------------------------------------- infographies
def ecg(cv, t, y=1700, col=(255, 70, 80), bpm=110, amp=90, alpha=1.0, pulse=True):
    """Ligne de battement de cœur qui défile + pulsation rouge des bords à chaque battement."""
    per = 60/bpm; d = ImageDraw.Draw(cv); pts = []
    for x in range(0, W + 8, 8):
        ph = ((x/W)*2.2 - t/per) % 1.0
        v = 0
        if .40 < ph < .44: v = -.25
        elif .44 < ph < .47: v = 1.0
        elif .47 < ph < .50: v = -.55
        elif .55 < ph < .62: v = .18
        pts.append((x, y - v*amp))
    d.line(pts, fill=col, width=7)
    if pulse:
        b = ((t % per)/per); k = math.exp(-b*7)*.55*alpha
        if k > .02: cv.paste(Image.new("RGB", (W, H), (200, 0, 20)), (0, 0), _vig_mask(int(255*k)))

_vm = {}
def _vig_mask(a):
    a = max(0, min(255, a//8*8))
    if a not in _vm:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W/2)/(W/2))**2 + ((yy - H/2)/(H/2))**2)
        m = np.clip((r - .55)/.6, 0, 1)**1.6*a
        _vm[a] = Image.fromarray(m.astype(np.uint8), "L")
    return _vm[a]

def vignette(cv, a=120): cv.paste(Image.new("RGB", (W, H), (20, 10, 4)), (0, 0), _vig_mask(a))

def dot_grid(cv, t, t0, seq, x0, y0, cols=10, step=78, r=28, d=1.0, cols_map=None):
    """seq = liste de catégories ('V','N','D'…) ; les points se remplissent un par un sur d secondes."""
    cols_map = cols_map or {"V": (250, 250, 246), "N": (255, 222, 64), "D": (220, 18, 38)}
    dr = ImageDraw.Draw(cv); n = len(seq); k = int(n*clamp((t - t0)/d)) if t >= t0 else 0
    for i in range(n):
        cx, cy = x0 + (i % cols)*step, y0 + (i//cols)*step
        if i < k:
            pop = clamp((t - t0 - i*d/n)/.12); rr = r*(.6 + .4*pop)
            dr.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=cols_map[seq[i]], outline=(20, 20, 20), width=4)
        else:
            dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=3)
    return k

def shockwave(cv, t, t0, x, y, dur=.5, rmax=900, col=(255, 255, 255)):
    u = (t - t0)/dur
    if not 0 <= u <= 1: return
    rr = 40 + rmax*ease_out_cubic(u); a = int(220*(1 - u))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse([x - rr, y - rr, x + rr, y + rr], outline=col + (a,), width=int(24*(1 - u)) + 4)
    cv.paste(ov, (0, 0), ov)

# ---------------------------------------------------------------- post / caméra
def whip_blur(cv, vx, vy, k=5):
    """Flou de mouvement le long de (vx, vy) px/frame (travelling rapide)."""
    sp = math.hypot(vx, vy)
    if sp < 30: return
    a = np.asarray(cv.convert("RGB")).astype(np.float32); acc = a.copy(); L = min(160, sp*.8)
    for i in range(1, k):
        dx = int(vx/sp*L*i/k); dy = int(vy/sp*L*i/k); acc += np.roll(np.roll(a, dx, 1), dy, 0)
    out = Image.fromarray((acc/k).astype(np.uint8)); cv.paste(out, (0, 0))

def desat(cv, amt=.85, dark=.25):
    a = np.asarray(cv.convert("RGB")).astype(np.float32); g = a.mean(2, keepdims=True)
    a = (a*(1 - amt) + g*amt)*(1 - dark); cv.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), (0, 0))

def dust(cv, t, n=36, seed=3):
    d = ImageDraw.Draw(cv); r = random.Random(seed)
    for i in range(n):
        x0, y0, sp, sz = r.uniform(0, W), r.uniform(0, H), r.uniform(10, 40), r.uniform(2, 6)
        x = (x0 + math.sin(t*.7 + i)*30) % W; y = (y0 - t*sp) % H
        d.ellipse([x - sz, y - sz, x + sz, y + sz], fill=(255, 246, 220))

# ---------------------------------------------------------------- sons
def sfx_variants(sfx, src_dir, out_dir, rates=(1.0, .93, 1.07, .97, 1.04)):
    """Copie la banque dans out_dir et crée des variantes de hauteur ; chaque répétition d'un même son prend la suivante."""
    os.makedirs(out_dir, exist_ok=True); seen = {}; res = []
    for t, name, g in sorted(sfx):
        k = seen.get(name, 0); seen[name] = k + 1; r = rates[k % len(rates)]
        nm = name if r == 1.0 else f"{name}__{int(r*100)}"
        dst = os.path.join(out_dir, nm + ".mp3")
        if not os.path.exists(dst):
            src = os.path.join(src_dir, name + ".mp3")
            if r == 1.0: shutil.copy(src, dst)
            else: subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", f"asetrate=44100*{r},aresample=44100", dst], check=True)
        res.append((t, nm, g*(1 - .08*(k % 3))))
    return res
