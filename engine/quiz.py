"""
quiz.py — format QUIZ de la série : « T'es un vrai fan de X si tu as plus de 5/8 ».

Même style papier découpé que les épisodes « histoire » (engine.py + foot.py + story.py). Une vidéo :
intro (titre en lettres découpées, nom du club dès la 1re image) → 4 questions → CTA « abonne-toi + like »
→ 4 questions → « t'as eu combien ? » (barème, commentaire, abonne-toi).

Une question = carte question + illustration papier + 4 réponses A-D. La voix lit la question, puis un chrono
de 5 s s'écoule (cadran + barre qui se vide, tic-tac), buzzer, la bonne réponse passe au vert, la voix la donne.

Voix : un fichier par morceau dans voix/ (intro, q1, r1, …, cta, …, outro), assemblés par `assemble()` en un
fichier par scène : question + silence du chrono + réponse. Les temps (début du chrono, révélation) sont
calculés depuis l'audio : rien à caler à la main.
"""
import json, os, wave
from story import *

CHRONO = 5.0            # secondes pour répondre
PRE, POST = .15, .3     # fin de la question → départ du chrono ; buzzer → voix de la réponse
PAD_IN = .3
LETTERS = "ABCD"
GOOD = (46, 164, 86); DIM = (178, 178, 186); WHITE = (250, 250, 246); INK = PAL["ink"]; CREAM = PAL["cream"]
GOLD = (236, 186, 48); RED = (214, 40, 46)
AX, ANS_Y0, ANS_DY = 495, 1090, 126      # réponses : centre x (à gauche du rail d'icônes TikTok), 1re ligne, pas
CARD_Y, TIMER_Y, ILLU_Y = 478, 652, 862

class Q:
    """Une question. text : à l'écran ; answers : 4 réponses ; ok : index de la bonne (0-3) ; level : sticker (FACILE…) ;
    illu(cv, fr, t, u, tm) : illustration, u = 0 avant la révélation puis 0 → 1 ; sfx : bruitages en plus,
    [(décalage depuis la révélation, nom, gain)] ; note : petit texte affiché après la révélation."""
    def __init__(self, text, answers, ok, level="", illu=None, sfx=(), note=None):
        assert len(answers) == 4 and 0 <= ok < 4
        self.text, self.answers, self.ok, self.level, self.illu, self.sfx, self.note = text, answers, ok, level, illu, list(sfx), note

# ------------------------------------------------------------------ voix : assemblage question + chrono + réponse
def speech_bounds(a, thr=.02):
    """Début et fin de la parole (silences ElevenLabs de tête et de queue retirés)."""
    hop = int(SR*.01); env = np.array([np.abs(a[i:i+hop]).max() for i in range(0, len(a), hop)])
    idx = np.where(env > thr)[0]
    if not len(idx): return 0, len(a)
    return max(0, idx[0]*hop - int(.03*SR)), min(len(a), (idx[-1] + 1)*hop + int(.08*SR))

def _write_wav(path, a):
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(a, -1, 1)*32767).astype(np.int16).tobytes())

def order(n_q=8, cta_after=4):
    if not cta_after:                # pas de pause au milieu (CTA seulement à la fin)
        return ["intro"] + [f"q{i}" for i in range(1, n_q + 1)] + ["outro"]
    return ["intro"] + [f"q{i}" for i in range(1, cta_after + 1)] + ["cta"] + [f"q{i}" for i in range(cta_after + 1, n_q + 1)] + ["outro"]

def assemble(vdir, out, n_q=8, cta_after=4):
    """Un fichier voix par scène. Renvoie (clés, fichiers, minutages) ; minutage d'une question (temps local de la scène) :
    tq fin de la question, ts départ du chrono, te fin du chrono (révélation), tr début de la voix de la réponse, dr sa durée."""
    os.makedirs(out, exist_ok=True); keys = order(n_q, cta_after); files, tms = [], []
    for k, key in enumerate(keys):
        if not key.startswith("q"):
            files.append(os.path.join(vdir, f"{key}.mp3")); tms.append(None); continue
        q = load_audio(os.path.join(vdir, f"{key}.mp3")); r = load_audio(os.path.join(vdir, f"r{key[1:]}.mp3"))
        a0, a1 = speech_bounds(q); b0, b1 = speech_bounds(r); q, r = q[a0:a1], r[b0:b1]
        a = np.concatenate([q, np.zeros(int((PRE + CHRONO + POST)*SR), np.float32), r])
        p = os.path.join(out, f"scene_{k+1}.wav"); _write_wav(p, a); files.append(p)
        tq = PAD_IN + len(q)/SR; ts = tq + PRE; te = ts + CHRONO
        tms.append(dict(tq=tq, ts=ts, te=te, tr=te + POST, dr=len(r)/SR))
    return keys, files, tms

# ------------------------------------------------------------------ composants
_ans = {}
def answer_box(key, txt, letter, badge):
    """3 états d'une réponse : n (blanche), ok (verte), off (éteinte)."""
    if key in _ans: return _ans[key]
    size = 54; f = font("title", size)
    while f.getlength(txt) > 610 and size > 34: size -= 2; f = font("title", size)
    out = {}
    for st, (bg, fg, bc) in dict(n=(WHITE, INK, badge), ok=(GOOD, WHITE, (26, 104, 54)), off=(DIM, (112, 112, 120), (140, 140, 150))).items():
        def dec(d, a, fg=fg, bc=bc):
            ax, ay = a
            d.ellipse([ax - 418, ay - 42, ax - 334, ay + 42], fill=bc)
            d.text((ax - 376, ay + 2), letter, font=font("title", 60), fill=WHITE, anchor="mm")
            d.text((ax - 306, ay + 2), txt, font=f, fill=fg, anchor="lm")
        out[st] = Paper(rect_pts(860, 108), bg, f"{key}{st}", rough=1.8).add(dec)
    _ans[key] = out; return out

def bump(u): return math.sin(clamp(u)*math.pi)

def answers(cv, fr, t, q, i, tm, badge, t_in=.45):
    """Les 4 réponses : arrivent en cascade pendant la lecture de la question, la bonne passe au vert à la révélation."""
    te = tm["te"]
    for k, txt in enumerate(q.answers):
        s = pop_in(t, t_in + k*.12, .3)
        if s <= .01: continue
        y = ANS_Y0 + k*ANS_DY; box = answer_box(f"qa{i}_{k}", txt, LETTERS[k], badge)
        if t < te: box["n"].draw(cv, fr, AX + 3*math.sin(t*2.5 + k), y, s, .6*math.sin(t*3 + k))
        elif k == q.ok:
            box["ok"].draw(cv, fr, AX, y, 1 + .1*bump(prog(t, te, .3)), -1.5)
            sl = slam(t, te + .1)
            if sl > 0: LBL("✓", "qzchk", font("sans", 92), WHITE, None, stroke=7, stroke_fill=(26, 104, 54)).draw(cv, fr, AX + 372, y - 6, sl, -8)
        else:
            box["off"].draw(cv, fr, AX, y, lerp(1, .95, prog(t, te, .2)), 0)

def _mix(c1, c2, u): return tuple(int(lerp(a, b, u)) for a, b in zip(c1, c2))

def chrono(cv, fr, t, ts, y=TIMER_Y, x0=250, x1=930, cx=140):
    """Chrono de 5 s : cadran qui se vide + chiffre + barre qui s'écoule (vert → jaune → rouge), tremble à la fin."""
    if t < ts - .35: return
    a = pop_in(t, ts - .35, .3)*clamp(1 - prog(t, ts + CHRONO + .5, .3))    # arrive, puis s'efface après la révélation
    if a <= .2: return          # (trop petit pour se voir, et évite les formes dégénérées)
    u = clamp((t - ts)/CHRONO)
    col = _mix((60, 190, 90), GOLD, u*2) if u < .5 else _mix(GOLD, RED, (u - .5)*2)
    jx = (5*math.sin(t*60) if u > .6 and u < 1 else 0)
    d = ImageDraw.Draw(cv)
    bx0 = x0 + (1 - a)*(x1 - x0)*.5
    d.rounded_rectangle([bx0, y - 24, x1, y + 24], 24, fill=(24, 22, 30), outline=WHITE, width=5)
    if u < 1: d.rounded_rectangle([bx0 + 7, y - 16, bx0 + 7 + max(32, (x1 - bx0 - 14)*(1 - u)), y + 16], 16, fill=col)
    beat = 1 - clamp(((t - ts) % 1)/.25) if 0 <= t - ts < CHRONO else 0     # le cadran bat à chaque seconde
    r = 84*a*(1 + .1*beat)
    X = cx + jx
    d.ellipse([X - r - 8, y - r - 8, X + r + 8, y + r + 8], fill=(24, 22, 30))
    d.ellipse([X - r, y - r, X + r, y + r], fill=WHITE)
    if u < 1: d.pieslice([X - r + 8, y - r + 8, X + r - 8, y + r - 8], -90 + 360*u, 270, fill=col)
    n = math.ceil(CHRONO*(1 - u) - 1e-6) if u < 1 else 0
    d.text((X, y + 4), str(n), font=font("title", int(110*a)), fill=INK if n else RED, anchor="mm", stroke_width=6, stroke_fill=WHITE)
    d.rectangle([X - 16*a, y - r - 30*a, X + 16*a, y - r - 6], fill=(24, 22, 30))

def chrono_sfx(ts):
    """Tic-tac à chaque seconde (plus fort sur les 2 dernières), buzzer à la fin."""
    return [(ts + k, "tictac", .75 if k < 3 else 1.0, .45) for k in range(int(CHRONO))] + [(ts + CHRONO, "buzzer", .55)]

def header(cv, fr, t, i, n, accent, level="", last=False):
    lab = LBL("DERNIÈRE QUESTION !" if last else f"QUESTION {i}/{n}", "qzh", font("title", 62), INK if last else WHITE, GOLD if last else accent,
              padx=28, pady=6, rough=3)
    lab.draw(cv, fr, CX, 248, pop_in(t, .02, .3), -2)
    d = ImageDraw.Draw(cv); y = 330
    for k in range(n):
        x = CX + (k - (n - 1)/2)*50
        if k < i - 1: d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=GOLD, outline=INK, width=3)
        elif k == i - 1:
            r = 16 + 3*math.sin(t*8); d.ellipse([x - r, y - r, x + r, y + r], fill=WHITE, outline=accent, width=6)
        else: d.ellipse([x - 11, y - 11, x + 11, y + 11], outline=(230, 230, 236), width=3)

def question_card(cv, fr, t, q, i):
    size = 66
    while size > 48 and len(wrap(q.text, font("title", size), 880)) > 2: size -= 4
    lab = LBL(q.text, f"qzq{i}", font("title", size), INK, CREAM, maxw=880, padx=34, pady=16, rough=3)
    s = slam(t, .08, .2)
    if s > 0: lab.draw(cv, fr, CX, CARD_Y, s, -1.2)
    if q.level and t > .3:
        hard = "DIFF" in q.level or "DUR" in q.level
        TAG(q.level, f"qzl{q.level}", RED if hard else GOLD, WHITE if hard else INK, 44).draw(
            cv, fr, 925, CARD_Y - 118, pop_in(t, .3, .3), 9)

def question_scene(q, i, n, tm, theme, last=False):
    """Fonction de dessin d'une scène question. theme : dict(accent, badge, bgs, ray)."""
    bg = theme["bgs"][(i - 1) % len(theme["bgs"])]; ray = theme.get("ray", (255, 255, 255))
    def draw(cv, fr, t, T):
        stage_fill(cv, fr, bg, f"qzbg{i}")
        rays(cv, (CX, 860), t, .35, 14, 1500, _mix(bg, ray, .25), .1, .08)
        te = tm["te"]; u = clamp(prog(t, te, .45)) if t >= te else 0.0
        if q.illu: q.illu(cv, fr, t, u, tm)
        header(cv, fr, t, i, n, theme["accent"], last=last)
        question_card(cv, fr, t, q, i)
        chrono(cv, fr, t, tm["ts"])
        answers(cv, fr, t, q, i, tm, theme["badge"])
        if q.note and t > te + .5:
            show(cv, fr, TAG(q.note, f"qzn{i}", PAL["paper"], INK, 46, maxw=700), t, te + .5, None, CX, 1000, -2)
        flashes(cv, t, te, .12, .5); punch(cv, t, te, 1.04, .25)
        drift(cv, t, T, .02)
    return draw

def question_sfx(q, tm):
    s = [(.0, "whoosh", .45), (.1, "stamp", .55)] + [(.45 + k*.12, "pop", .45) for k in range(4)]
    s += chrono_sfx(tm["ts"]) + [(tm["te"] + .05, "correct", .8)]
    return s + [(tm["te"] + e[0], *e[1:]) for e in q.sfx]

# ------------------------------------------------------------------ couronne (« vrai fan »)
def _crown(d, a):
    ax, ay = a
    for k, c in enumerate((RED, (40, 90, 200), RED)):
        x = ax - 60 + k*60; d.ellipse([x - 13, ay + 22, x + 13, ay + 48], fill=c, outline=INK, width=2)
    d.line([(ax - 104, ay + 8), (ax + 104, ay + 8)], fill=(190, 138, 20), width=5)
CROWN = Paper(poly_pts([(-110, 60), (-110, -40), (-62, 4), (-30, -66), (0, -16), (30, -66), (62, 4), (110, -40), (110, 60)]),
              GOLD, "qzcrown", rough=1.4, hatch=True).add(_crown)
def crown_on(cv, fr, x, y, s, t=1.0, t0=0.0):
    """Couronne qui tombe sur la tête d'un joueur dessiné avec ses pieds en (x, y) et l'échelle s."""
    u = prog(t, t0, .35); hy = y - 668*s
    if u > 0: CROWN.draw(cv, fr, x + 4, hy - 260*(1 - ease_out_back(u)), .78*s/.92, -6)

# ------------------------------------------------------------------ boutons (CTA)
HEART = Paper(heart_pts(7), WHITE, "qzheart", rough=1.2, shadow=False)
BTN_SUB = Label("+ ABONNE-TOI", "qzbsub", font("title", 96), WHITE, (230, 40, 80), padx=40, pady=14, rough=2.5)

def like_button(cv, fr, x, y, s, t, t_tap, n0=12840):
    """Gros bouton « j'aime » : s'enfonce au tap, petits cœurs qui s'envolent, compteur qui grimpe."""
    if s <= .02: return
    press = 1 - .15*math.sin(prog(t, t_tap, .25)*math.pi)
    d = ImageDraw.Draw(cv); r = 150*s*press
    d.ellipse([x - r, y - r, x + r, y + r], fill=(240, 50, 80), outline=WHITE, width=max(3, int(10*s)))
    HEART.draw(cv, fr, x, y + 6*s, s*press, 0)
    if t > t_tap:
        for k in range(7):
            u = prog(t, t_tap + k*.06, .9)
            if 0 < u < 1: HEART.draw(cv, fr, x + 140*math.sin(k*2.1)*u, y - 380*u, .28*(1 - u*.5), 0, 1 - u)
        LBL(counter(n0, n0 + 1 + int(800*prog(t, t_tap, 1.6)), 1), "qzlikes", font("title", 60), WHITE, INK, padx=16, pady=2,
            rough=2).draw(cv, fr, x, y + 210*s, 1, 0)

def sub_button(cv, fr, x, y, t, t_in, t_tap):
    s = pop_in(t, t_in, .3)
    if s <= .01: return
    s *= 1 - .12*math.sin(prog(t, t_tap, .25)*math.pi)
    BTN_SUB.draw(cv, fr, x, y, s, -2)

# ------------------------------------------------------------------ intro, CTA, fin (génériques)
def ttl(theme):
    return ("T'ES UN VRAI FAN", f"{theme['du']} ?", f"SI TU AS PLUS DE {theme.get('seuil', 5)}/{theme.get('nq', 8)}")

def intro_scene(theme, Wd, hero):
    """Titre dès la 1re image (« T'ES UN VRAI FAN / DU PSG ? / SI TU AS PLUS DE 5/8 »), puis les règles.
    Wd : Words de l'intro ; hero(cv, fr, t, x, y, s) dessine le joueur du club."""
    l1, l2, l3 = ttl(theme); mc, mn = theme.get("mot_chrono", ("cinq", 2))       # mot de la voix qui annonce le chrono
    N = theme.get("nq", 8); mq, mqn = theme.get("mot_nq", ("Huit", 2))
    K8 = KW(f"{N} QUESTIONS", f"qzi8_{N}", INK, size=120); K5 = KW(f"{CHRONO:g} SECONDES", f"qzi5_{CHRONO:g}", theme["accent"], size=110)
    KP = TAG("compte tes points !", "qzip", PAL["paper"], INK, 60); KG = STAMP("C'EST PARTI !", "qzig", theme["badge"], 130)
    STRIP = Label(l3, "qzis", font("title", 78), INK, GOLD, maxw=1000, padx=30, pady=8, rough=5)
    QM = LBL(f"?/{N}", "qziqm", font("title", 170), WHITE, theme["badge"], padx=30, pady=4, rough=3)
    def shot1(cv, fr, t):
        stage_fill(cv, fr, theme["bgs"][0], "qzi1"); rays(cv, (CX, 1300), t, .5, 16, 1500, theme.get("ray2", (40, 70, 140)), .12, .15)
        hero(cv, fr, t, CX + 90, 1780, 1.05)
        QM.draw(cv, fr, CX - 270, 1000, slam(t, .5), -8)
        ransom_line(cv, l1, 330, 120, seed=3, fr=fr, scale=lerp(1.25, 1, ease_out_cubic(prog(t, 0, .25))))
        ransom_line(cv, l2, 500, 140, seed=11, fr=fr)
        STRIP.draw(cv, fr, CX, 680, 1 if fr == 0 else slam(t, .02, .2), -3)
        if theme.get("niveau"): STAMP(theme["niveau"], "qzniv", RED, 92).draw(cv, fr, 770, 850, 1 if fr == 0 else slam(t, .25, .2), 9)
    def shot2(cv, fr, t):
        stage_fill(cv, fr, theme["bgs"][1], "qzi2"); rays(cv, (CX, 900), t, .5, 14, 1500, (255, 255, 255), .08, .2)
        t8, t5, tc, tp = Wd(mq, mqn), Wd(mc, mn), Wd("Compte"), Wd("parti")
        kw(cv, fr, K8, t, t8, None, CX, 380, -3)
        if t > t5 - .1:
            K5.draw(cv, fr, CX, 540, pop_in(t, t5 - .1, .3), 3)
            chrono(cv, fr, t, t5 + .2, y=730, cx=180, x0=300, x1=900)
        for k in range(4):
            box = answer_box(f"qzi{k}", ("…", "…", "…", "…")[k], LETTERS[k], theme["badge"])
            s = pop_in(t, tc + k*.08, .25)
            if s > 0: box["ok" if k == 2 and t > tp else "n"].draw(cv, fr, AX, 930 + k*118, s*.9, 0)
        show(cv, fr, KP, t, tc, None, CX, 1420, -3)
        show_stamp(cv, fr, KG, t, tp - .1, CX, 1110, -6)
    def draw(cv, fr, t, T):
        shots(cv, fr, t, [(0, shot1), (Wd(mq, mqn) - .15, shot2)], d=.24)
        drift(cv, t, T, .02)
    sfx = [(.0, "boom", .8), (.0, "stamp", .7), (.05, "riser", .35), (.5, "stamp", .6), (Wd(mq, mqn) - .15, "whoosh", .5),
           (Wd(mq, mqn), "stamp", .6), (Wd(mc, mn), "pop2"), (Wd(mc, mn) + .2, "tictac", .7, .45), (Wd("Compte"), "pop"),
           (Wd("parti") - .1, "stamp", .8), (Wd("parti"), "whoosh_up", .6)]
    return draw, sfx

def cta_scene(theme, Wd, after=4):
    """Pause au milieu : « abonne-toi et lâche un like pour avoir plus de contenu sur ton club préféré ! »."""
    KA = KW("PETITE PAUSE !", "qzc1", INK, size=96); TS = TAG(f"{after}/8 : t'en es à combien ?", "qzc2", PAL["paper"], INK, 52)
    TC = TAG("+ de contenu sur ton club préféré !", "qzc3", GOLD, INK, 54, maxw=860); KR = KW("ON REPREND !", "qzc4", INK, size=96)
    def draw(cv, fr, t, T):
        stage_fill(cv, fr, (240, 50, 80), "qzcta"); rays(cv, (CX, 1000), t, .5, 14, 1400, (250, 110, 130))
        ta, tl, tc, tr = Wd("Abonne-toi"), Wd("like"), Wd("contenu"), Wd("Allez")
        kw(cv, fr, KA, t, .05, None, CX, 300, -3)
        show(cv, fr, TS, t, .4, None, CX, 440, 2)
        sub_button(cv, fr, CX, 640, t, ta - .15, ta + .25)
        like_button(cv, fr, CX, 960, .85*pop_in(t, tl - .25, .3), t, tl)
        show(cv, fr, TC, t, tc - .1, None, CX, 1270, -2)
        kw(cv, fr, KR, t, tr - .05, None, CX, 1420, 3)
        drift(cv, t, T, .02)
    sfx = [(.0, "scratch", .7), (.05, "stamp", .6), (.4, "pop"), (Wd("Abonne-toi") - .15, "pop2"), (Wd("Abonne-toi") + .25, "notif"),
           (Wd("like") - .25, "pop"), (Wd("like"), "notif"), (Wd("contenu"), "pop2"), (Wd("Allez") - .1, "whoosh", .5), (Wd("Allez"), "stamp", .6)]
    return draw, sfx

def cta_score_scene(theme, Wd, after=3, suite="NIVEAU 2"):
    """Pause « dis ton score en commentaire, lâche un like et abonne-toi pour le niveau 2 » (texte voix : …combien… Dis… commentaire…
    like… abonne-toi… niveau… Allez…)."""
    KA = KW("PETITE PAUSE !", "qzs1", INK, size=96); TS = TAG(f"t'en es à combien sur {after} ?", "qzs2", PAL["paper"], INK, 56)
    KC = KW("DIS TON SCORE EN COMMENTAIRE !", "qzs3", WHITE, INK, 62)
    KN = STAMP(f"{suite} BIENTÔT !", "qzs4", RED, 84); KR = KW("ON REPREND !", "qzs5", INK, size=96)
    def draw(cv, fr, t, T):
        stage_fill(cv, fr, (240, 50, 80), "qzscta"); rays(cv, (CX, 1000), t, .5, 14, 1400, (250, 110, 130))
        tb, td, tc, tl, ta, tn, tr = Wd("combien"), Wd("Dis"), Wd("commentaire"), Wd("like"), Wd("abonne-toi"), Wd("niveau"), Wd("Allez")
        kw(cv, fr, KA, t, .05, None, CX, 300, -3)
        show(cv, fr, TS, t, tb - .2, None, CX, 430, 2)
        kw(cv, fr, KC, t, td - .05, None, CX, 570, 2)
        speech_bubble(cv, fr, "qzsbub", f"J'ai ?/{after} !", 640, 730, pop_in(t, tc - .15, .3), (-1, 1), 58)
        like_button(cv, fr, CX, 920, .75*pop_in(t, tl - .25, .3), t, tl)
        sub_button(cv, fr, CX, 1235, t, ta - .15, ta + .25)
        show_stamp(cv, fr, KN, t, tn - .05, CX, 1375, -4)
        kw(cv, fr, KR, t, tr - .05, None, CX, 1505, 3)
        drift(cv, t, T, .02)
    sfx = [(.0, "scratch", .7), (.05, "stamp", .6), (Wd("combien") - .2, "pop"), (Wd("Dis") - .05, "stamp", .6), (Wd("commentaire"), "notif"),
           (Wd("like") - .25, "pop"), (Wd("like"), "notif"), (Wd("abonne-toi") - .15, "pop2"), (Wd("abonne-toi") + .25, "notif"),
           (Wd("niveau"), "stamp", .7), (Wd("Allez") - .1, "whoosh", .5), (Wd("Allez"), "stamp", .6)]
    return draw, sfx

def outro_scene(theme, Wd, hero, tag="le quiz de ton club ?"):
    """« T'as eu combien ? » : barème (0-3 touriste, 4-5 supporter, 6-8 vrai fan), commentaire, abonne-toi."""
    KA = KW("T'AS EU COMBIEN ?", "qzo1", INK, size=100)
    s = theme.get("seuil", 5)
    rows = [(f"0 – {s-2}", "TOURISTE", DIM, INK), (f"{s-1} – {s}", "SUPPORTER", WHITE, INK), (f"{s+1} – {theme.get('nq', 8)}", "VRAI FAN", GOLD, INK)]
    LR = [Label(f"{a}   {b}", f"qzo2{k}", font("title", 70), fg, bg, padx=30, pady=6, rough=3) for k, (a, b, bg, fg) in enumerate(rows)]
    TK = TAG(tag, "qzo3" + tag, PAL["paper"], INK, 54)
    def draw(cv, fr, t, T):
        stage_fill(cv, fr, theme["bgs"][0], "qzout"); rays(cv, (CX, 900), t, .6, 16, 1500, (230, 190, 80), .1, .15)
        tp, tf, tc, ta = Wd("Plus"), Wd("fan"), Wd("commentaire"), Wd("abonne-toi")
        kw(cv, fr, KA, t, .05, None, CX, 300, -3)
        for k, lab in enumerate(LR):
            a = pop_in(t, tp - .2 + k*.15, .3)
            if a > 0: lab.draw(cv, fr, CX, 520 + k*125, a*(1 + (.12*bump(prog(t, tf, .35)) if k == 2 else 0)), (-2, 2, -3)[k])
        speech_bubble(cv, fr, "qzbub", f"J'ai eu ?/{theme.get('nq', 8)} !", 620, 960, pop_in(t, tc - .2, .3), (-1, 1), 60)
        sub_button(cv, fr, CX, 1150, t, ta - .15, ta + .2)
        show(cv, fr, TK, t, ta + .1, None, CX, 1265, -2)
        hero(cv, fr, t, 300, 1760, .7, crown=t > tf)
        if t > tf: confetti(cv, fr, "qzoc", t - tf, 70, 3.5, [GOLD, WHITE, theme["accent"]])
        drift(cv, t, T, .02)
    sfx = [(.0, "boom", .6), (.05, "stamp", .6), (Wd("Plus") - .2, "pop"), (Wd("Plus") - .05, "pop"), (Wd("Plus") + .1, "pop2"),
           (Wd("fan"), "crowd", .8), (Wd("fan"), "sparkle"), (Wd("commentaire") - .2, "notif"), (Wd("abonne-toi") - .15, "pop2"),
           (Wd("abonne-toi") + .2, "notif")]
    return draw, sfx

# ------------------------------------------------------------------ couverture
def quiz_cover(path, theme, hero, title="~/quiz"):
    """Couverture : question en lettres découpées, « PLUS DE 5/8 ? », 4 réponses dont une verte, chrono, tampon QUIZ."""
    l1, l2, _ = ttl(theme)
    cv = background(0, title); stage_fill(cv, 0, theme["bgs"][0], "qzcov")
    rays(cv, (CX, 1250), .3, .8, 16, 1500, theme.get("ray2", (40, 70, 140)), .12)
    ransom_line(cv, l1, 300, 130, seed=3); ransom_line(cv, l2, 470, 150, seed=11)
    Label(f"PLUS DE {theme.get('seuil', 5)}/{theme.get('nq', 8)} ?", "qzcv1", font("title", 96), INK, GOLD, padx=30, pady=8, rough=5).draw(cv, 0, CX, 650, 1, -3)
    STAMP(theme.get("tampon", "QUIZ"), "qzcv2", RED, 110 if len(theme.get("tampon", "QUIZ")) < 6 else 80).draw(cv, 0, 850, 820, 1, 12)
    chrono(cv, 0, CHRONO*.4 + 1.0, 1.0, y=820, cx=170, x0=290, x1=700)
    for k in range(4):
        box = answer_box(f"qzcvb{k}", "?", LETTERS[k], theme["badge"])
        box["ok" if k == 1 else "n"].draw(cv, 0, AX, 1010 + k*120, .95, (-1, 1, -1.5, 1)[k])
    hero(cv, 0, 1.0, CX, 1890, .6)
    finish(cv, title); cv.convert("RGB").save(path, quality=94); return path
