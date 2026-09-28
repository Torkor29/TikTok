"""
story.py — outils de montage communs aux épisodes « légendes du foot » (au-dessus de engine.py et foot.py).

- Mots clés synchronisés sur la voix : `Words` (via engine.align_words) + `kw()` pour faire claquer un mot à l'écran.
- Plusieurs plans dans une même scène : `shots()` enchaîne des fonctions de dessin avec un filé rapide entre elles.
- Dynamique : `drift()` (zoom caméra continu), `impact()` (tremblement), `punch()` (zoom), `flashes()`, `glitch()`.
- Apparitions : `win()`, `slam()`, `show()`, `show_stamp()`, `hl()` (titre de scène).
"""
import json, os
from foot import *

_lc = {}
def LBL(txt, key, *a, **k):
    """Label mis en cache (compteurs, textes qui changent)."""
    kk = (key, txt)
    if kk not in _lc: _lc[kk] = Label(txt, key+txt, *a, **k)
    return _lc[kk]

def HL(txt, key, bg, fg=PAL["cream"], size=84):
    return Label(txt, key, font("title", size), fg, bg, maxw=940, padx=34, pady=18, rough=4)
def TAG(txt, key, bg=PAL["paper"], fg=PAL["ink"], size=54, maxw=820):
    return Label(txt, key, font("hand", size), fg, bg, maxw=maxw, padx=26, pady=12)
def STAMP(txt, key, col=PAL["red"], size=120, bg=PAL["cream"]):
    return Label(txt, key, font("title", size), col, bg, padx=34, pady=6, rough=2, maxw=960)
def KW(txt, key, bg=PAL["ink"], fg=PAL["cream"], size=110):
    """Mot clé qui claque à l'écran (gros, sur bande de papier)."""
    return Label(txt, key, font("title", size), fg, bg, padx=30, pady=8, rough=3.5, maxw=980)

def win(t, t_in, t_out=None, d_in=.35, d_out=.25):
    a = pop_in(t, t_in, d_in)
    if t_out is not None: a *= 1 - ease_in_cubic(prog(t, t_out, d_out))
    return a
def slam(t, t0, d=.18):
    u = prog(t, t0, d)
    return 0 if t < t0 else lerp(2.3, 1.0, ease_out_cubic(u))
def show(cv, fr, lab, t, t_in, t_out, x, y, rot=0, amp=1.0):
    a = win(t, t_in, t_out)
    if a > .01: lab.draw(cv, fr, x, y, a, rot, min(1, a*1.5), amp)
def show_stamp(cv, fr, lab, t, t0, x, y, rot=-6, t_out=None):
    s = slam(t, t0)
    if s <= 0: return
    a = 1 - (ease_in_cubic(prog(t, t_out, .25)) if t_out else 0)
    if a <= .01: return
    lab.draw(cv, fr, x, y, s*(1 if a > .99 else a), rot, min(1, prog(t, t0, .06))*a)
def kw(cv, fr, lab, t, t0, t1=None, x=CX, y=560, rot=-3):
    """Mot clé : arrive en claquant (échelle 1.6 -> 1), frétille, repart vite."""
    if t < t0: return
    u = prog(t, t0, .16); s = lerp(1.6, 1.0, ease_out_back(u, 2.2)) if u < 1 else 1 + .02*math.sin((t-t0)*9)
    a = 1.0
    if t1 is not None:
        o = prog(t, t1, .18); s *= 1 - .6*o; a = 1 - o
    if a > .01: lab.draw(cv, fr, x, y, s, rot + 2*math.sin((t-t0)*5), a, 1.2)
def hl(cv, fr, lab, t, t_in, t_out=None, y=330, rot=-1.5):
    s = pop_in(t, t_in, .4)
    if s <= 0: return
    o = prog(t, t_out, .3) if t_out is not None else 0
    if o >= 1: return
    lab.draw(cv, fr, CX, y - 260*ease_in_cubic(o), s*(1-.3*o), rot, 1-o)

def impact(cv, t, t0, amp=16, dur=.3):
    if t0 <= t < t0+dur: shake(cv, t, amp*(1-(t-t0)/dur))
def punch(cv, t, t0, z=1.08, dur=.3, center=None):
    if t0 <= t < t0+dur: zoom_punch(cv, 1+(z-1)*(1-(t-t0)/dur), center)
def flashes(cv, t, t0, dur=.15, a=.8):
    if t0 <= t < t0+dur: flash(cv, a*(1-(t-t0)/dur))
def glitch(cv, fr, t, t0, dur=.35, amp=14):
    if t0 <= t < t0+dur:
        k = 1-(t-t0)/dur; rgb_split(cv, amp*k, fr, slices=int(6*k))
def drift(cv, t, T, z=.035):
    """Zoom caméra lent et continu : l'image n'est jamais figée."""
    zoom_punch(cv, 1 + z*clamp(t/max(T, .1)))

def shots(cv, fr, t, plan, d=.3):
    """Plusieurs plans dans une scène : plan = [(t_debut, fn(cv, fr, t)), ...].
    Entre deux plans, filé rapide (flou de mouvement) de durée d."""
    k = 0
    for i, (t0, _) in enumerate(plan):
        if t >= t0: k = i
    # proche d'une frontière ? -> composer les deux plans
    for i in range(1, len(plan)):
        b = plan[i][0]
        if b - d/2 <= t < b + d/2:
            a_cv = cv.copy(); plan[i-1][1](a_cv, fr, t)
            plan[i][1](cv, fr, t)
            whip_transition(cv, a_cv, (t - (b - d/2))/d, -1)
            return
    plan[k][1](cv, fr, t)

def load_words(path):
    """Charge l'alignement mot par mot d'un épisode (fichier json écrit par align_episode)."""
    data = json.load(open(path))
    return [Words([tuple(x) for x in data["words"][str(i+1)]]) for i in range(len(data["texts"]))], data["texts"]

def align_episode(voice_files, texts, path):
    out = {str(i+1): align_words(vf, tx) for i, (vf, tx) in enumerate(zip(voice_files, texts))}
    json.dump({"texts": texts, "words": out}, open(path, "w"), ensure_ascii=False, indent=0)
    return path

# ------------------------------------------------------------------ décors réutilisables
def pitch(cv, fr, key="pitch", col=(70, 150, 84)):
    """Pelouse en papier avec lignes à la craie."""
    stage_fill(cv, fr, col, key)
    d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    for k in range(6):   # bandes de tonte
        y0 = sy0 + k*(sy1-sy0)/6
        if k % 2: d.rectangle([sx0, y0, sx1, y0+(sy1-sy0)/12], fill=tuple(int(c*.95) for c in col))
    pencil_line(d, [(sx0+60, 1540), (sx1-60, 1540)], 1, (236, 240, 230), 7, 1, 1.2)
    pencil_line(d, [(CX+300*math.cos(a), 1540+90*math.sin(a)) for a in [math.pi*(1+k/24) for k in range(25)]], 1, (236, 240, 230), 6, 2, 1.2)

def speech_bubble(cv, fr, key, txt, x, y, s=1.0, tail=(-1, 1), size=56, bg=PAL["white"], fg=PAL["ink"]):
    """Bulle de BD avec queue ; tail = direction de la queue."""
    lab = LBL(txt, key, font("title", size), fg, bg, padx=34, pady=18, rough=2.5, maxw=640)
    if s <= .02: return
    d = ImageDraw.Draw(cv)
    tx, ty = x + tail[0]*120*s, y + tail[1]*90*s
    d.polygon([(x - 40*s, y + 20*s), (x + 20*s, y + 30*s), (tx, ty)], fill=bg)
    lab.draw(cv, fr, x, y, s, 0, 1, 1)

def us_flag(cv, x, y, w=220, h=140, a=1.0):
    if a <= .01: return
    L = layer(w+20, h+20, (w/2+10, h/2+10)); d = ImageDraw.Draw(L)
    for k in range(13):
        d.rectangle([10, 10+k*h/13, 10+w, 10+(k+1)*h/13], fill=(200, 30, 50) if k % 2 == 0 else (250, 248, 240))
    d.rectangle([10, 10, 10+w*.42, 10+h*7/13], fill=(30, 50, 110))
    for i in range(5):
        for j in range(4): d.ellipse([10+12+i*16, 10+10+j*16, 10+18+i*16, 10+16+j*16], fill=(250, 248, 240))
    blit(cv, L, x, y, a, -6, 1)

def heart_pts(s=1.0, n=60):
    pts = []
    for k in range(n):
        th = 2*math.pi*k/n
        x = 16*math.sin(th)**3; y = -(13*math.cos(th) - 5*math.cos(2*th) - 2*math.cos(3*th) - math.cos(4*th))
        pts.append((x*s, y*s))
    return pts

def draw_star(cv, x, y, r, a=1.0, rot=0.0, col=(255, 236, 150)):
    if a <= .01: return
    ImageDraw.Draw(cv).polygon(star_shape(x, y, r*a, 5, .45, rot-math.pi/2), fill=col)
