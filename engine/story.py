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

# ------------------------------------------------------------------ effets « archive »
def grayscale(cv, a=1.0):
    """Passe la scène en noir et blanc (a = dosage) : moments tristes, souvenirs."""
    if a <= .01: return
    st = cv.crop(STAGE); g = st.convert("L").convert("RGB")
    if a < .99: g = Image.blend(st, g, a)
    m = Image.new("L", g.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, g.width-1, g.height-1], 20, fill=255)
    cv.paste(g, STAGE[:2], m)

def vhs(cv, fr, t, a=1.0, label="REW", stamp=None):
    """Rembobinage de cassette VHS : lignes de balayage, bande de tracking qui remonte, canaux décalés,
    tranches qui glissent, incrustation ◀◀ REW (triangles dessinés : la police n'a pas le glyphe)."""
    if a <= .01: return
    rgb_split(cv, 10*a, fr, slices=int(5*a))
    sx0, sy0, sx1, sy1 = STAGE; w, h = sx1-sx0, sy1-sy0
    st = np.asarray(cv.crop(STAGE), dtype=np.float32)
    st[::4] *= 1 - .35*a                                        # lignes de balayage
    st = st*(1-.25*a) + np.array([40, 60, 110], np.float32)*.25*a   # dominante bleue
    rng = np.random.default_rng(fr)
    by = int((1 - (t*1.7) % 1.0)*(h+160)) - 80                  # bande de tracking qui remonte
    y0, y1 = max(0, by), min(h, by+70)
    if y1 > y0:
        st[y0:y1] = st[y0:y1]*.4 + rng.random((y1-y0, w, 1)).astype(np.float32)*230*.6
    st += (rng.random((h, w, 1)).astype(np.float32) - .5)*38*a   # neige
    im = Image.fromarray(np.clip(st, 0, 255).astype(np.uint8))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w-1, h-1], 20, fill=255)
    cv.paste(im, (sx0, sy0), m)
    d = ImageDraw.Draw(cv); x, y = 90, 200; col = (250, 250, 246)
    if int(t*3) % 2 == 0 or label != "REW":
        for k in range(2): d.polygon([(x+k*44, y), (x+k*44+44, y-28), (x+k*44+44, y+28)], fill=col)
        d.text((x+110, y), label, font=font("mono", 64), fill=col, anchor="lm")
    if stamp: d.text((sx1-60, sy1-420), stamp, font=font("mono", 58), fill=col, anchor="rm")

def fr_flag(cv, x, y, w=300, h=200, a=1.0, t=0.0, rot=0.0):
    """Drapeau français qui ondule."""
    if a <= .01: return
    L = layer(int(w+40), int(h+60), (w/2+20, h/2+30)); d = ImageDraw.Draw(L)
    cols = [(24, 44, 120), (250, 250, 246), (206, 32, 44)]
    n = 30
    for k in range(n):
        x0 = 20 + k*w/n; x1 = 20 + (k+1)*w/n + 1
        off = 12*math.sin(k/n*math.pi*2 - t*5)*(k/n)
        d.rectangle([x0, 30+off, x1, 30+h+off], fill=cols[min(2, int(3*k/n))])
    blit(cv, L, x, y, a, rot, 1)

def sepia(cv, a=1.0):
    """Ton sépia (vieille photo) sur la scène."""
    if a <= .01: return
    st = cv.crop(STAGE); g = np.asarray(st.convert("L"), dtype=np.float32)[..., None]
    sp = np.clip(g*np.array([1.07, .88, .66], np.float32) + np.array([18, 10, 0], np.float32), 0, 255).astype(np.uint8)
    im = Image.fromarray(sp)
    if a < .99: im = Image.blend(st, im, a)
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width-1, im.height-1], 20, fill=255)
    cv.paste(im, STAGE[:2], m)

def old_film(cv, fr, t, a=1.0):
    """Vieux film : sépia + rayures verticales + poussières + scintillement."""
    if a <= .01: return
    sepia(cv, a)
    d = ImageDraw.Draw(cv); rnd = random.Random(fr // 2); sx0, sy0, sx1, sy1 = STAGE
    for _ in range(3):
        x = rnd.uniform(sx0+40, sx1-40); d.line([(x, sy0), (x + rnd.uniform(-6, 6), sy1)], fill=(236, 226, 200), width=rnd.choice([1, 2, 3]))
    for _ in range(14):
        x, y, r = rnd.uniform(sx0, sx1), rnd.uniform(sy0, sy1), rnd.uniform(1.5, 5)
        d.ellipse([x-r, y-r, x+r, y+r], fill=(40, 30, 20) if rnd.random() < .6 else (240, 232, 210))
    if rnd.random() < .3: flash(cv, .08*a, (255, 240, 200))

def elevator_drop(cv, t, t0, dur=.7, shaft=(34, 32, 40)):
    """Chute d'ascenseur : l'image part vers le haut (la caméra tombe), la cage défile avec des étages."""
    u = prog(t, t0, dur)
    if u <= 0: return 0.0
    sx0, sy0, sx1, sy1 = STAGE; h = sy1 - sy0; w = sx1 - sx0
    e = ease_in_cubic(u); off = int(e*h)
    st = cv.crop(STAGE)
    k = int(2 + 18*math.sin(u*math.pi))
    if k > 2: st = st.resize((w, max(1, h//k)), Image.BILINEAR).resize((w, h), Image.BILINEAR)   # flou vertical
    comp = Image.new("RGB", (w, h), shaft); comp.paste(st, (0, -off))
    d = ImageDraw.Draw(comp)
    for j in range(8):   # étages qui défilent
        y = (j*260 - t*2600) % (h + 260) - 130
        if y > h - off - 30: continue
        d.rectangle([0, y, w, y + 16], fill=(70, 66, 80)); d.line([(0, y + 30), (w, y + 30)], fill=(56, 52, 64), width=4)
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w-1, h-1], 20, fill=255)
    cv.paste(comp, (sx0, sy0), m)
    return u

def floor_panel(cv, fr, x, y, label, t, down=True, s=1.0, a=1.0):
    """Afficheur d'étage d'ascenseur (chiffres rouges + flèche qui clignote)."""
    if a <= .01: return
    L = layer(int(320*s), int(210*s), (160*s, 105*s)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([6*s, 6*s, 314*s, 204*s], int(22*s), fill=(20, 20, 24), outline=(150, 150, 160), width=max(2, int(6*s)))
    d.text((200*s, 108*s), label, font=font("mono", int(110*s)), fill=(255, 60, 50), anchor="mm")
    if int(t*6) % 2 == 0:
        ax, ay = 72*s, 105*s; sg = 1 if down else -1
        d.polygon([(ax-34*s, ay-22*s*sg), (ax+34*s, ay-22*s*sg), (ax, ay+30*s*sg)], fill=(255, 60, 50))
    blit(cv, L, x, y, a)

def siren_lights(cv, t, a=.35):
    """Gyrophares : la scène clignote rouge / bleu."""
    if a <= .01: return
    sx0, sy0, sx1, sy1 = STAGE; w, h = sx1 - sx0, sy1 - sy0
    ph = int(t*5) % 2
    L = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    col = (230, 30, 40, int(255*a)) if ph == 0 else (30, 80, 240, int(255*a))
    if ph == 0: d.rectangle([0, 0, w//2, h], fill=col)
    else: d.rectangle([w//2, 0, w, h], fill=col)
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w-1, h-1], 20, fill=255)
    L.putalpha(ImageChops.multiply(L.getchannel("A"), m))
    cv.paste(L, (sx0, sy0), L)

def flares(cv, fr, key, t, area, n=10, a=1.0):
    """Fumigènes dans la tribune : points rouges incandescents + fumée grise translucide qui monte."""
    if a <= .01: return
    x0, y0, x1, y1 = area; rnd = random.Random(key)
    L = Image.new("RGBA", cv.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    pts = [(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(0, 3)) for _ in range(n)]
    for i, (x, y, ph) in enumerate(pts):
        for k in range(5):   # fumée
            tt = (t*.5 + ph + k/5) % 1.0
            r = (14 + 46*tt)*a; sy = y - 240*tt; sx = x + 26*math.sin(tt*4 + i)
            dl.ellipse([sx-r, sy-r, sx+r, sy+r], fill=(215, 205, 205, int(110*(1 - tt))))
        r = 70*a; dl.ellipse([x-r, y-r, x+r, y+r], fill=(255, 60, 40, 60))   # halo rouge
    cv.paste(L, (0, 0), L); d = ImageDraw.Draw(cv)
    for i, (x, y, ph) in enumerate(pts):
        r = (11 + 4*math.sin(t*30 + i))*a
        d.ellipse([x-r*1.8, y-r*1.8, x+r*1.8, y+r*1.8], fill=(255, 90, 50)); d.ellipse([x-r, y-r, x+r, y+r], fill=(255, 240, 200))

def beam(cv, apex, pts, a=.35, col=(255, 244, 200)):
    """Faisceau lumineux semi-transparent (projecteur, lampe torche)."""
    L = Image.new("RGBA", cv.size, (0, 0, 0, 0)); ImageDraw.Draw(L).polygon([apex] + pts, fill=(*col, int(255*a)))
    cv.paste(L, (0, 0), L)
