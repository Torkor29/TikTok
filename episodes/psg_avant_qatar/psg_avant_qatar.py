"""« T'ES UN FOOTIX SI TU CONNAIS PAS LE PSG D'AVANT LE QATAR » : histoire du PSG 1978 → 2011, anecdotes jamais sorties sur la chaîne
(Hechter radié à vie, la double billetterie, Borelli qui embrasse la pelouse en 1982, 4-1 contre le Real en 1993, le titre 1993 laissé
vacant, Weah / Ginola / Raí / Ronaldinho, le maintien à Sochaux en 2008), question piège au milieu (qui a mis la tête ? réponse jamais donnée),
fin clivante « le vrai PSG, avant ou après ? ». DA papier douce (modèle devine_psg15) : kraft, panneaux papier, frise 1970 → 2011 en fil rouge,
micro-animations, déchirures entre les époques ; pas de musique, pas d'effets « édit ».
Voix : voix/voix.mp3 (une prise, TEXTE ci-dessous, une phrase par ligne) ; `--seg` la découpe (faster-whisper) -> voix/segments.json.
Sans voix : minutage provisoire, rendu marqué _provisoire.
  python3 episodes/psg_avant_qatar/psg_avant_qatar.py [--seg | --stills | --cover]"""
import sys, os, math, json, subprocess, re
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import engine as E
import paper_cut as PC
import foot as F
from story import ransom_line, heart_pts
import numpy as np
from PIL import Image, ImageDraw
W, H = E.W, E.H; FPS = 30
KRAFT = (236, 226, 204); NAVY = (24, 38, 92); PRED = (206, 44, 52); CREAM = (251, 247, 236); INK = (28, 36, 70)
GREEN = (52, 150, 86); GOLD = (238, 190, 60); MUSTARD = (226, 176, 60); GRASS = (64, 128, 78); WINE = (120, 30, 44); TEAL = (38, 120, 120)
WHITE = (255, 255, 255); BLACK = (24, 22, 26)
OUT = os.path.join(ROOT, "output", "psg_avant_qatar")
VO = os.path.join(HERE, "voix", "voix.mp3"); SEGF = os.path.join(HERE, "voix", "segments.json")
TEXTE = ["T'es un footix si tu connais pas le PSG d'avant le Qatar.",
         "Avant les milliards, Paris, c'était le chaos. Et c'était magique.",
         "Mille neuf cent soixante-dix-huit : le président, le styliste Daniel Hechter, est radié à vie.",
         "Le motif ? Une double billetterie au Parc des Princes : du liquide, hors des comptes.",
         "Quatre ans plus tard, finale de la Coupe de France. Rocheteau égalise à la dernière minute !",
         "Le président Francis Borelli saute sur la pelouse et l'embrasse. Premier trophée de l'histoire.",
         "Mille neuf cent quatre-vingt-treize : Paris perd trois-un à Madrid. Au retour, quatre-un, avec une tête dans le temps additionnel !",
         "Question pour les vrais : qui a mis cette tête ? Réponds en commentaire, like et abonne-toi !",
         "La même année, l'OM perd son titre pour corruption. Paris, deuxième, ne le réclame même pas.",
         "Résultat : un championnat sans champion !",
         "Puis Weah, Ginola, Raï, une Coupe d'Europe, et un jeune Brésilien : Ronaldinho.",
         "Mais en deux mille huit, Paris joue sa survie à la dernière journée, à Sochaux.",
         "Amara Diané marque deux fois. Paris est sauvé !",
         "Trois ans plus tard, le Qatar arrive. Et toi, le vrai PSG, c'était avant ou après ? Dis-le en commentaire !"]
PROVISOIRE = not (os.path.exists(VO) and os.path.exists(SEGF))
if PROVISOIRE:                                                   # ~19 caractères / s (Léo, blancs coupés)
    SEG, t = [], 0.0
    for s in TEXTE: d = round(len(s)/19 + .2, 2); SEG.append((t, t + d)); t += d
else: SEG = [tuple(x[:2]) for x in json.load(open(SEGF))]
PAD_IN, PAD_OUT = .12, .28
DUR = [SEG[i][1] - SEG[i][0] + PAD_IN + PAD_OUT for i in range(len(SEG))]
DUR[-1] += 1.6
STARTS = list(np.cumsum([0] + DUR[:-1])); TOTAL = float(sum(DUR))
TRANS = {1: "tear_d", 2: "tear_v", 4: "tear_h", 6: "tear_d", 8: "slide", 9: "slide", 10: "tear_v", 11: "tear_h", 12: "slide", 13: "tear_d", 3: "slide", 5: "slide", 7: "slide"}
TD = .5

# ---------------------------------------------------------------- décor commun
_c = {}
def kraft():
    if "kraft" not in _c:
        rng = np.random.default_rng(1); a = np.zeros((H, W, 3), np.float32); a[:] = KRAFT
        a *= (.95 + .08*E._lowfreq(W, H, 3, 60))[..., None]
        sp = rng.random((H, W)); a += ((sp > .985)*-22 + (sp < .01)*14)[..., None]
        _c["kraft"] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    return _c["kraft"]
def _psg_stripe(d, ox, oy):
    d.rectangle([ox - 168, oy - 2000, ox + 168, oy + 2000], fill=(240, 236, 226)); d.rectangle([ox - 150, oy - 2000, ox + 150, oy + 2000], fill=PRED)
_pan = {}
def panel(col, stripe=False):
    k = (col, stripe)
    if k not in _pan: _pan[k] = E.Paper(E.rect_pts(1220, 1400), col, f"pan{col}{stripe}", rough=5, pattern=_psg_stripe if stripe else None)
    return _pan[k]
STAR = E.Paper(E.star_shape(0, 0, 30, 5, .45), GOLD, "star", rough=1.2)
def bg(cv, fr, t, col, stripe=False, stars=True):
    cv.alpha_composite(kraft()); panel(col, stripe).draw(cv, fr, W//2, 1290, 1, -2.5, amp=2.5)
    if stars:
        for k, (x, y, s, sp) in enumerate(((110, 760, 1, .9), (975, 860, .8, 1.2), (90, 1700, .7, 1.1), (990, 1690, 1, .8))):
            STAR.draw(cv, fr, x, y + 9*math.sin(t*sp + k), s*(1 + .06*math.sin(t*2.1 + k)), 12*math.sin(t*.7 + k))
_lb = {}
def LB(txt, size, fg=INK, bg=CREAM, kind="title", padx=30, pady=12):
    k = (txt, size, fg, bg, kind)
    if k not in _lb: _lb[k] = E.Label(txt, f"lb{txt}{size}", E.font(kind, size), fg, bg, padx=padx, pady=pady, maxw=960)
    return _lb[k]
_tx = {}
def TX(txt, size, col=INK, kind="title"):
    k = (txt, size, col, kind)
    if k not in _tx: _tx[k] = E.text_sprite(txt, E.font(kind, size), col)
    return _tx[k]
def pop(u, t0, d=.4, s=2.0):
    v = E.clamp((u - t0)/d); return E.ease_out_back(v, s) if v > 0 else 0.0
def stamp(cv, fr, txt, x, y, u, t0, col=PRED, size=96, rot=-8):
    """Tampon encreur qui claque (arrive grand, s'écrase, petit rebond)."""
    v = E.clamp((u - t0)/.22)
    if v <= 0: return
    s = 1.6 - .6*E.ease_out_cubic(v); LB(txt, size, WHITE, col, padx=34, pady=14).draw(cv, fr, x, y, s, rot, min(1, v*2))
# -- frise 1970 → 2011 (fil rouge en haut)
YEARS = [1970, 1978, 1982, 1993, 2008, 2011]
def timeline(cv, fr, year, t):
    x0, x1, y = 120, 960, 215
    d = ImageDraw.Draw(cv); d.line([(x0, y), (x1, y)], fill=INK, width=6)
    def X(yr): return x0 + (x1 - x0)*(yr - 1970)/(2011 - 1970)
    for yr in YEARS:
        d.ellipse([X(yr) - 9, y - 9, X(yr) + 9, y + 9], fill=CREAM if yr > year else PRED, outline=INK, width=3)
    E.blit(cv, TX("1970", 34, INK, "hand"), x0, y + 34); E.blit(cv, TX("2011", 34, INK, "hand"), x1, y + 34)
    xm = X(year); bob = 5*math.sin(t*4)
    d.polygon([(xm - 16, y - 46 + bob), (xm + 16, y - 46 + bob), (xm, y - 18 + bob)], fill=PRED)
    LB(str(year), 46, WHITE, NAVY, padx=16, pady=4).draw(cv, fr, xm, y - 82 + bob, 1, -2)
# -- cartes photo (polaroïd) des joueurs fournis par l'utilisateur
PH = os.path.join(ROOT, "assets", "photos", "psg")
BOX = {"ronaldinho": (0, 0, 789, 860), "ginola": (0, 0, 620, 640)}
def card(slug, cw=430, ch=520):
    k = ("card", slug, cw)
    if k in _c: return _c[k]
    ww, wh = cw - 44, ch - 120
    im = E.paper_sprite(E.rect_pts(cw, ch), CREAM, seed=hash(slug) % 97, rough=2.0); ax, ay = im.info["anchor"]
    win = E.paper_sprite(E.rect_pts(ww, wh), NAVY, seed=7, rough=1.0, shadow=False); wa = win.info["anchor"]
    sp = PC.paper_player(os.path.join(PH, slug + ".png"), BOX.get(slug), int(wh*1.12), real=True, border=10)
    s = min(1.0, (ww - 20)/sp.width); sp = sp.resize((int(sp.width*s), int(sp.height*s)), Image.LANCZOS)
    m = Image.new("L", win.size, 0); ImageDraw.Draw(m).rectangle([wa[0] - ww/2 + 5, wa[1] - wh/2 + 5, wa[0] + ww/2 - 5, wa[1] + wh/2 - 5], fill=255)
    lay = Image.new("RGBA", win.size, (0, 0, 0, 0)); lay.paste(sp, (int(wa[0] - sp.width/2), int(wa[1] + wh/2 - sp.height + 18)), sp)
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(m))))
    win.alpha_composite(lay); im.alpha_composite(win, (int(ax - wa[0]), int(ay - 40 - wa[1])))
    tp = Image.new("RGBA", (150, 44), (244, 236, 206, 200)).rotate(6, expand=True); im.alpha_composite(tp, (int(ax - tp.width/2), int(ay - ch/2 - 18)))
    _c[k] = im; return im
def put_card(cv, fr, slug, name, x, y, u, t0, rot, s=1.0, cw=430, ch=520):
    """La carte tombe en se balançant puis respire ; le nom est écrit au feutre en bas."""
    v = E.clamp((u - t0)/.4)
    if v <= 0: return
    yy = y - (1 - E.ease_out_back(v, 1.2))*1400 + 4*math.sin(u*2.3 + x); rr = rot + (1 - E.ease_out_cubic(v))*14 + 1.2*math.sin(u*1.7 + x)
    E.blit(cv, card(slug, cw, ch), x, yy, s, rr)
    a = math.radians(rr); dy = ch/2 - 52
    E.blit(cv, TX(name, 64 if cw > 400 else 52, INK, "brush"), x + dy*math.sin(a)*s, yy + dy*math.cos(a)*s, s, rr)
# -- accessoires papier
PL = F.Player("pqa", hair=(40, 30, 26)); PL2 = F.Player("pqb", hair=(30, 22, 20), skin=(150, 100, 70))
SUIT = F.Player("hechter", hair=(80, 60, 44), hair_style="shaggy"); BOR = F.Player("borelli", hair=(40, 36, 34))
TICKET = E.Paper(E.rect_pts(560, 230), CREAM, "ticket", rough=1.6).add(lambda d, a: (d.rectangle([a[0] - 270, a[1] - 105, a[0] + 270, a[1] + 105], outline=PRED, width=6),
    d.line([(a[0] + 150, a[1] - 105), (a[0] + 150, a[1] + 105)], fill=PRED, width=4)))
BILL = E.Paper(E.rect_pts(200, 100), (120, 170, 120), "bill", rough=1.2).add(lambda d, a: (d.ellipse([a[0] - 30, a[1] - 30, a[0] + 30, a[1] + 30], outline=(70, 110, 70), width=5),
    d.rectangle([a[0] - 92, a[1] - 42, a[0] + 92, a[1] + 42], outline=(70, 110, 70), width=3)))
HEART = E.Paper(heart_pts(5), PRED, "heart", rough=1.2)
JF = F.jersey_front("psg", "pqjf")
BOARD = E.Paper(E.rect_pts(820, 300), (40, 40, 46), "board", rough=2)
def scoreboard(cv, fr, x, y, la, lb, sa, sb, sub="", s=1.0, flip=1.0):
    BOARD.draw(cv, fr, x, y, s, 0)
    E.blit(cv, TX(la, 56, (210, 205, 196)), x - 270*s, y - 70*s, s); E.blit(cv, TX(lb, 56, (210, 205, 196)), x + 270*s, y - 70*s, s)
    E.blit(cv, TX(f"{sa} - {sb}", 150, GOLD), x, y + 26*s, s*flip if flip > .05 else .05)
    if sub: E.blit(cv, TX(sub, 40, (180, 176, 170), "mono"), x, y + 120*s, s)
def goal(cv, fr, x, y, u, t): F.draw_goal(cv, fr, x, y, 460, 260, net_u=u, t=t)
def logo(name, w):
    k = ("logo", name, w)
    if k not in _c:
        lg = Image.open(os.path.join(ROOT, "assets", "logos", f"{name}_sticker.png")).convert("RGBA"); lg = lg.resize((w, int(lg.height*w/lg.width)), Image.LANCZOS)
        lg.info["anchor"] = (lg.width/2, lg.height/2); _c[k] = lg
    return _c[k]
def qatar_flag(cv, x, y, w, h, t, rot=0):
    L = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rectangle([20, 20, 20 + w, 20 + h], fill=(138, 21, 56)); n = 9; band = w*.32
    pts = [(20, 20), (20 + band, 20)]
    for k in range(n):
        y0 = 20 + h*k/n; pts += [(20 + band + w*.09, y0 + h/n/2), (20 + band, y0 + h/n)]
    pts += [(20, 20 + h)]; d.polygon(pts, fill=CREAM)
    # ondulation douce du drapeau
    a = np.asarray(L); out = np.zeros_like(a)
    for xx in range(a.shape[1]): sh = int(8*math.sin(xx/60 - t*4)*(xx/a.shape[1])); out[:, xx] = np.roll(a[:, xx], sh, 0)
    im = Image.fromarray(out); im.info["anchor"] = (im.width/2, im.height/2); E.blit(cv, im, x, y, 1, rot)

# ---------------------------------------------------------------- scènes : s(cv, fr, t, u, T) ; u = temps dans la scène
def s0(cv, fr, t, u, T):                                         # ACCROCHE : lisible dès l'image 0
    bg(cv, fr, t, NAVY, True, False)
    ransom_line(cv, "T'ES UN", 300, 120, seed=11, fr=fr)
    ransom_line(cv, "FOOTIX ?", 480, 200, seed=13, fr=fr)
    for slug, nm, x, y, r in (("weah", "Weah", 250, 1130, -9), ("rai", "Raí", 830, 1130, 9), ("ronaldinho", "Ronaldinho", 540, 1180, -2)):
        E.blit(cv, card(slug), x, y + 6*math.sin(t*2 + x), .92 if slug != "ronaldinho" else 1.0, r + 1.2*math.sin(t*1.6 + x))
    LB("LE PSG AVANT LE QATAR", 74, WHITE, PRED, padx=30, pady=12).draw(cv, fr, W//2, 1610, 1 + .03*max(0, 1 - u/.2), -3)
def s1(cv, fr, t, u, T):
    bg(cv, fr, t, WINE); timeline(cv, fr, 1970, t)
    for k in range(6):
        v = pop(u, .05 + k*.06); E.blit(cv, BILL.v[E.boil(fr)], 380 + (k % 3)*160, 760 + (k//3)*90 - k*6, v, -8 + k*5) if v > .02 else None
    LB("DES MILLIARDS", 70, INK, GOLD).draw(cv, fr, W//2, 620, pop(u, .02), -2)
    if u > .25*T + .02:
        F.pencil_cross(ImageDraw.Draw(cv), W//2, 760, max(.3, 2.8*E.clamp((u - .25*T)/.3)), PRED)
    sh = 6*math.sin(t*38)*E.clamp((u - .45*T)/.2)*(1 - E.clamp((u - .7*T)/.3))
    LB("LE CHAOS", 120, WHITE, BLACK).draw(cv, fr, W//2 + sh, 1150, pop(u, .42*T), -4 + sh*.4)
    v = pop(u, .7*T); LB("ET LA MAGIE", 100, INK, GOLD).draw(cv, fr, W//2, 1420, v, 3)
    if v > .05:
        for k in range(5): STAR.draw(cv, fr, W//2 - 330 + k*165, 1290 + 30*math.sin(t*3 + k), .7*v, t*60 + k*30)
def s2(cv, fr, t, u, T):                                         # 1978 : Hechter radié à vie
    bg(cv, fr, t, MUSTARD); timeline(cv, fr, 1978, t)
    LB("1978", 130, WHITE, NAVY).draw(cv, fr, W//2, 470, pop(u, 0), -3)
    sad = u > .72*T
    SUIT.draw(cv, fr, W//2 - 140, 1560, 1.25, kit="suit", arms=(14, 14) if not sad else (-6, -6), mood="sad" if sad else "happy", t=t)
    JF.draw(cv, fr, W//2 + 260, 1150 + 6*math.sin(t*2), .8*pop(u, .25*T), 6)                # le maillot qu'il a dessiné
    LB("DANIEL HECHTER", 62, INK, CREAM).draw(cv, fr, W//2 - 140, 720, pop(u, .3*T), 2)
    E.blit(cv, TX("styliste… et président", 50, INK, "hand"), W//2 - 140, 800, pop(u, .38*T))
    stamp(cv, fr, "RADIÉ À VIE", W//2, 1030, u, .72*T, PRED, 104, -9)
def s3(cv, fr, t, u, T):                                         # la double billetterie
    bg(cv, fr, t, TEAL); timeline(cv, fr, 1978, t)
    LB("DOUBLE BILLETTERIE", 76, WHITE, BLACK).draw(cv, fr, W//2, 470, pop(u, 0), -2)
    k = E.ease_out_cubic(E.clamp((u - .2*T)/.4))
    for j, dx in enumerate((-1, 1)):
        x = W//2 + dx*k*70; y = 820 + dx*k*90
        TICKET.draw(cv, fr, x, y, 1, -4 + dx*k*6)
        E.blit(cv, TX("PARC DES PRINCES", 44, INK), x - 70, y - 40, 1, -4 + dx*k*6); E.blit(cv, TX("BILLET", 64, PRED), x - 70, y + 30, 1, -4 + dx*k*6)
    for b in range(7):                                           # les billets tombent dans la valise
        st = .5*T + b*.12; v = E.clamp((u - st)/.55)
        if 0 < v: E.blit(cv, BILL.v[E.boil(fr)], W//2 - 150 + (b % 4)*100, 1100 + 330*E.ease_in_cubic(v), .8, b*23 + v*140)
    d = ImageDraw.Draw(cv); x, y, s = W//2, 1440, 2.2
    d.rounded_rectangle([x - 70*s, y, x + 70*s, y + 110*s], int(12*s), fill=(150, 96, 56), outline=(90, 56, 30), width=8)
    d.rectangle([x - 70*s, y + 46*s, x + 70*s, y + 58*s], fill=(110, 70, 40)); d.arc([x - 26*s, y - 30*s, x + 26*s, y + 10*s], 180, 360, fill=(90, 56, 30), width=14)
    stamp(cv, fr, "HORS DES COMPTES", W//2, 1330, u, .78*T, PRED, 70, 6)
def s4(cv, fr, t, u, T):                                         # 1982 : Rocheteau à la dernière minute
    bg(cv, fr, t, GRASS); timeline(cv, fr, 1982, t)
    LB("FINALE COUPE DE FRANCE", 64, INK, GOLD).draw(cv, fr, W//2, 430, pop(u, 0), -2)
    eq = u > .66*T; fl = 1 - .9*max(0, 1 - abs(u - .66*T)/.08) if abs(u - .66*T) < .08 else 1
    scoreboard(cv, fr, W//2, 690, "PSG", "ASSE", 2 if eq else 1, 2, "120e minute" if u > .45*T else "", .9, fl)
    goal(cv, fr, 760, 1480, E.clamp((u - .62*T)/.5), t)
    kick = E.clamp((u - .5*T)/.15)
    PL.draw(cv, fr, 300, 1660, 1.05, kit="psg", arms=(30, 40), legs=(-10 if kick < 1 else 30, 20), mood="determined" if not eq else "cheer", t=t)
    bu = E.clamp((u - .52*T)/.14); bx = 380 + (760 - 380)*bu; by = 1640 - 220*bu - 160*math.sin(math.pi*bu)
    F.draw_ball(cv, fr, bx, by, .55, t*400)
    if eq: LB("ROCHETEAU !", 92, WHITE, NAVY).draw(cv, fr, W//2, 1000, pop(u, .66*T, .35, 2.6), 4)
def s5(cv, fr, t, u, T):                                         # Borelli embrasse la pelouse, 1er trophée
    bg(cv, fr, t, GRASS); timeline(cv, fr, 1982, t)
    E.rays(cv, (W//2, 820), t, .6, 14, 900, (250, 226, 150), .1, .25)
    v = pop(u, .55*T, .5); F.CUP.draw(cv, fr, W//2, 840 - 40*v + 8*math.sin(t*3), 1.6*v, 3*math.sin(t*2)) if v > .02 else None
    run = E.clamp(u/(.45*T)); x = 1300 - 760*E.ease_out_cubic(run); kneel = u > .45*T
    BOR.draw(cv, fr, x, 1600 + (50 if kneel else 0), 1.1, kit="suit", arms=(150, 150) if not kneel else (40, 40), legs=(20*math.sin(t*14), -20*math.sin(t*14)) if not kneel else (0, 0), mood="cheer", t=t, lean=40 if kneel else 0)
    for k in range(5):
        hv = E.clamp((u - .45*T - k*.12)/1.0)
        if 0 < hv < 1: HEART.draw(cv, fr, x + 40*math.sin(k*2 + hv*5), 1180 - 360*hv, .55*(1 - hv*.4), 0, 1 - hv)
    LB("BORELLI EMBRASSE LA PELOUSE", 54, INK, CREAM).draw(cv, fr, W//2, 470, pop(u, .1), -2)
    stamp(cv, fr, "1er TROPHÉE", W//2, 1250, u, .72*T, GREEN, 96, -6)
def s6(cv, fr, t, u, T):                                         # 1993 : 1-3 à Madrid, 4-1 au Parc, tête au bout du temps additionnel
    bg(cv, fr, t, NAVY, True); timeline(cv, fr, 1993, t)
    LB("COUPE UEFA 1993", 70, INK, GOLD).draw(cv, fr, W//2, 430, pop(u, 0), -2)
    back = u > .45*T
    scoreboard(cv, fr, W//2, 690, "REAL" if not back else "PSG", "PSG" if not back else "REAL", 3 if not back else 4, 1, "à Madrid" if not back else "au Parc", .9,
               1 - .9*max(0, 1 - abs(u - .45*T)/.08) if abs(u - .45*T) < .08 else 1)
    PL2.draw(cv, fr, 760, 1660, 1.0, kit="real", arms=(20, 20), mood="sad" if u > .8*T else "normal", t=t)
    jump = E.clamp((u - .62*T)/.25); hj = 120*math.sin(math.pi*jump)
    PL.draw(cv, fr, 380, 1660 - hj, 1.05, kit="psg", arms=(150, 150) if u > .82*T else (60, 60), mood="cheer" if u > .82*T else "determined", t=t)
    bu = E.clamp((u - .55*T)/.3); F.draw_ball(cv, fr, 900 - 520*bu, 950 + 120*bu - 200*math.sin(math.pi*bu*.8), .5, -t*300) if u < .85*T else None
    if u > .6*T: E.blit(cv, TX("90+6'", 90, GOLD), 900, 930, pop(u, .6*T), 6)
    stamp(cv, fr, "4 - 1 !", W//2, 1240, u, .82*T, PRED, 120, -6)
def s7(cv, fr, t, u, T):                                         # QUESTION PIÈGE + like / abonne-toi (la réponse n'est jamais donnée)
    bg(cv, fr, t, PRED, False)
    LB("QUESTION POUR LES VRAIS", 66, WHITE, BLACK).draw(cv, fr, W//2, 380, pop(u, 0), -3)
    if "sil" not in _c: _c["sil"] = F.silhouette(PL.render_layer(0, 1.0, kit="psg", arms=(60, 60), mood="normal"), (30, 28, 34))
    E.blit(cv, _c["sil"], W//2, 1330 + 6*math.sin(t*2), 1, 2*math.sin(t*1.3))
    E.blit(cv, TX("?", 200, WHITE), W//2, 860 + 10*math.sin(t*3), pop(u, .1), 0)
    LB("QUI A MIS CETTE TÊTE ?", 80, INK, GOLD).draw(cv, fr, W//2, 560, pop(u, .15), 2)
    LB("RÉPONDS EN COMMENTAIRE", 58, INK, CREAM).draw(cv, fr, W//2, 1420, pop(u, .4*T), -2)
    v = pop(u, .62*T); press = math.sin(math.pi*E.clamp((u - .78*T)/.16))
    d = ImageDraw.Draw(cv); r = 95*v*(1 - .12*press)
    if v > .02:
        d.ellipse([300 - r, 1600 - r, 300 + r, 1600 + r], fill=(240, 50, 80), outline=WHITE, width=8); HEART.draw(cv, fr, 300, 1606, .55*v*(1 - .12*press), 0)
        LB("+ ABONNE-TOI", 66, WHITE, NAVY).draw(cv, fr, 700, 1600, v, -3)
        if u > .78*T:
            for k in range(5):
                hv = E.clamp((u - .78*T - k*.08)/.8)
                if 0 < hv < 1: HEART.draw(cv, fr, 300 + 90*math.sin(k*2.1)*hv, 1560 - 300*hv, .3, 0, 1 - hv)
def s8(cv, fr, t, u, T):                                         # l'OM perd son titre, Paris ne le réclame pas
    bg(cv, fr, t, (60, 120, 170)); timeline(cv, fr, 1993, t)
    LB("AFFAIRE VA-OM", 70, WHITE, BLACK).draw(cv, fr, W//2, 430, pop(u, 0), -2)
    E.blit(cv, logo("om", 360), 300, 860 + 5*math.sin(t*2), pop(u, .05), -4)
    gone = E.ease_in_cubic(E.clamp((u - .3*T)/.4)); F.CUP.draw(cv, fr, 600 + 900*gone, 830 - 200*gone, 1.1, 25*gone) if gone < 1 else None   # le titre s'en va
    stamp(cv, fr, "DÉCHU", 300, 900, u, .32*T, PRED, 96, -12)
    pv = pop(u, .55*T); E.blit(cv, logo("psg", 360), 780, 1260 + 5*math.sin(t*2.3), pv, 4 + 8*math.sin(t*1.5)*E.clamp((u - .7*T)/.3))
    if pv > .2: E.blit(cv, TX("« non merci »", 70, INK, "brush"), 760, 1500, pop(u, .72*T))
def s9(cv, fr, t, u, T):                                         # un championnat sans champion
    bg(cv, fr, t, (90, 70, 120)); timeline(cv, fr, 1993, t)
    d = ImageDraw.Draw(cv)
    for x, h, n in ((300, 300, "2"), (540, 440, "1"), (780, 220, "3")):
        d.rectangle([x - 115, 1640 - h, x + 115, 1640], fill=CREAM, outline=INK, width=5); E.blit(cv, TX(n, 110, INK), x, 1640 - h + 80)
    E.blit(cv, TX("?", 300, GOLD), 540, 1050 + 14*math.sin(t*3), pop(u, .1), 6*math.sin(t*2))
    LB("1993", 120, WHITE, NAVY).draw(cv, fr, W//2, 470, pop(u, 0), -3)
    LB("PAS DE CHAMPION !", 92, WHITE, PRED).draw(cv, fr, W//2, 700, pop(u, .25*T), 3)
def s10(cv, fr, t, u, T):                                        # Weah, Ginola, Raí, une Coupe d'Europe, Ronaldinho
    bg(cv, fr, t, NAVY, True); timeline(cv, fr, 1993 if u < .5*T else 2001 if u < .8*T else 2003, t)
    fade = E.clamp((u - .62*T)/.25)
    for k, (slug, nm, x, y, r, t0) in enumerate((("weah", "Weah", 220, 700, -8, .08), ("ginola", "Ginola", 540, 660, 3, .2), ("rai", "Raí", 860, 700, 8, .32))):
        put_card(cv, fr, slug, nm, x, y - 500*E.ease_in_cubic(fade), u, t0*T, r, .62, 430, 520)
    v = pop(u, .46*T); F.CUP.draw(cv, fr, 840, 1300 + 6*math.sin(t*3), 1.2*v, 4*math.sin(t*2)) if v > .02 else None
    if v > .02: E.blit(cv, TX("1996", 70, GOLD), 840, 1500, v)
    put_card(cv, fr, "ronaldinho", "Ronaldinho", 430, 1250, u, .66*T, -4, 1.0)
def s11(cv, fr, t, u, T):                                        # 2008 : survie à la dernière journée, à Sochaux
    bg(cv, fr, t, (70, 66, 74), False, False); timeline(cv, fr, 2008, t)
    LB("2008 · DERNIÈRE JOURNÉE", 66, INK, GOLD).draw(cv, fr, W//2, 430, pop(u, 0), -2)
    d = ImageDraw.Draw(cv)
    d.rectangle([110, 1120, 970, 1330], fill=(200, 60, 60)); E.blit(cv, TX("ZONE DE RELÉGATION", 58, WHITE), W//2, 1225)
    sh = 7*math.sin(t*30)*E.clamp(u/.5)
    E.blit(cv, logo("psg", 300), W//2 + sh, 900 + 40*math.sin(t*2.2), pop(u, .1), sh)
    # électrocardiogramme qui s'affole
    pts = []; base = 1520
    for x in range(110, 971, 6):
        ph = (x/130 - t*3) % 1; y = base - (150 if .45 < ph < .5 else -60 if .5 < ph < .55 else 0)*min(1, u/.6)
        pts.append((x, y))
    d.line(pts, fill=(255, 90, 90), width=7)
    LB("À SOCHAUX", 70, WHITE, NAVY).draw(cv, fr, W//2, 680, pop(u, .5*T), 3)
def s12(cv, fr, t, u, T):                                        # Diané, deux buts : sauvé
    bg(cv, fr, t, GRASS); timeline(cv, fr, 2008, t)
    LB("AMARA DIANÉ", 80, WHITE, NAVY).draw(cv, fr, W//2, 430, pop(u, 0), -2)
    goal(cv, fr, 760, 1420, max(E.clamp((u - .25*T)/.4), E.clamp((u - .5*T)/.4)), t)
    PL2.draw(cv, fr, 290, 1640, 1.05, kit="psg", arms=(150, 150) if u > .6*T else (40, 50), legs=(20, 30), mood="cheer" if u > .3*T else "determined", t=t)
    for k, t0 in enumerate((.18, .43)):
        bu = E.clamp((u - t0*T)/.14)
        if 0 < bu < 1: F.draw_ball(cv, fr, 360 + 400*bu, 1560 - 240*bu - 120*math.sin(math.pi*bu), .5, t*400)
        stamp(cv, fr, f"BUT {k + 1}", 300 + k*480, 760, u, (t0 + .1)*T, NAVY, 80, -6 + 12*k)
    stamp(cv, fr, "SAUVÉ !", W//2, 1080, u, .68*T, GREEN, 130, -5)
    if u > .68*T: E.confetti(cv, fr, 55, u - .68*T, 60, 3, [GOLD, PRED, CREAM, NAVY], (0, 0, W, H))
def s13(cv, fr, t, u, T):                                        # 2011 : le Qatar arrive… avant ou après ?
    bg(cv, fr, t, WINE); timeline(cv, fr, 2011, t)
    v = pop(u, .05); qatar_flag(cv, W//2, 640, int(560*max(.05, v)), int(330*max(.05, v)), t, -3) if v > .05 else None
    q = pop(u, .32*T); LB("LE VRAI PSG ?", 100, INK, GOLD).draw(cv, fr, W//2, 960, q, -2)
    for k, (lab, col, x) in enumerate((("AVANT", NAVY, 300), ("APRÈS", PRED, 780))):
        b = pop(u, (.45 + .06*k)*T); LB(lab, 110, WHITE, col, padx=40, pady=18).draw(cv, fr, x, 1210 + 8*math.sin(t*3 + k*2), b, (-4, 4)[k])
    E.blit(cv, TX("ou", 80, INK, "brush"), W//2, 1210, pop(u, .5*T))
    LB("DIS-LE EN COMMENTAIRE", 64, WHITE, BLACK).draw(cv, fr, W//2, 1450, pop(u, .7*T), 2)
SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13]
def draw(cv, fr, t):
    i = max(k for k, st in enumerate(STARTS) if st <= t) if t >= 0 else 0
    SCENES[i](cv, fr, t, t - STARTS[i], DUR[i]); return i
def render(fr, t):
    cv = Image.new("RGBA", (W, H)); i = draw(cv, fr, t); u = t - STARTS[i]
    if i in TRANS and u < TD:
        prev = Image.new("RGBA", (W, H)); pt = STARTS[i] - 1/FPS; SCENES[i - 1](prev, int(pt*FPS), pt, pt - STARTS[i - 1], DUR[i - 1])
        k = TRANS[i]
        if k == "slide":                                          # la nouvelle feuille glisse par-dessus l'ancienne
            v = E.ease_out_cubic(u/TD); out = prev.copy(); x = int(W*(1 - v))
            sh = Image.new("RGBA", (W, H), (30, 24, 20, 90)); out.alpha_composite(sh, (x - 26, 0)); out.alpha_composite(cv.crop((0, 0, W - x, H)), (x, 0))
            cv = out
        else:
            out = cv.convert("RGB"); E.tear_transition(out, prev.convert("RGB"), u/TD, k, i); cv = out
    if PROVISOIRE:
        cv = cv.convert("RGBA"); E.blit(cv, TX("VOIX PROVISOIRE", 36, PRED), W//2, 70)
    return cv.convert("RGB")
def frame(fr): return render(fr, fr/FPS).tobytes()

# ---------------------------------------------------------------- son (voix + bruitages, sans musique)
L5 = os.path.join(ROOT, "episodes", "lille_v5", "sfx"); A = os.path.join(ROOT, "assets", "sfx")
SFX = {0: [("hook", 0, .5)], 1: [("coins", .1, .4), ("scratch", .3, .5)], 2: [("typewriter", .05, .3), ("stamp", .72, .8)], 3: [("cash", .5, .5), ("stamp", .78, .7)],
       4: [("whistle", .02, .4), ("kick", .52, .7), ("net", .64, .6), ("crowd", .66, .5)], 5: [("crowd", .02, .4), ("fanfare", .55, .45), ("stamp", .72, .6)],
       6: [("rewind", .44, .4), ("crowd", .5, .4), ("kick", .62, .5), ("goal_roar", .82, .5)], 7: [("pop", .62, .5), ("heart", .78, .5)],
       8: [("gavel", .3, .6), ("stamp", .32, .5)], 9: [("whoosh", .2, .4)], 10: [("swish", .08, .4), ("swish", .2, .4), ("swish", .32, .4), ("fanfare", .46, .35), ("swish", .66, .4)],
       11: [("heart", .1, .5), ("siren", .5, .25)], 12: [("kick", .18, .6), ("net", .28, .5), ("kick", .43, .6), ("net", .53, .5), ("goal_roar", .68, .5)], 13: [("whoosh", .05, .4), ("pop", .45, .4), ("pop", .51, .4)]}
def sfx_path(n):
    for d in (L5, A):
        p = os.path.join(d, n + ".mp3")
        if os.path.exists(p): return p
    raise FileNotFoundError(n)
def build_audio(wav):
    S = OUT + "/_a"; os.makedirs(S, exist_ok=True); evs = []
    for k, (a, b) in enumerate(SEG):
        if PROVISOIRE: continue
        p = f"{S}/s{k}.wav"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(a), "-t", str(b - a), "-i", VO, "-af", "afade=t=in:d=0.015,areverse,afade=t=in:d=0.03,areverse", "-ar", "48000", "-ac", "2", p], check=True)
        evs.append((p, STARTS[k] + PAD_IN, 1.0))
    for i, lst in SFX.items():
        for n, fr_, g in lst: evs.append((sfx_path(n), STARTS[i] + fr_*DUR[i], g))
    for i, k in TRANS.items(): evs.append((sfx_path("page_tear" if k != "slide" else "swish"), STARTS[i], .45))
    ins = ["-f", "lavfi", "-t", f"{TOTAL:.2f}", "-i", "anullsrc=r=48000:cl=stereo"] + sum([["-i", p] for p, _, _ in evs], []); fc = ""
    for i, (_, ts, g) in enumerate(evs): fc += f"[{i + 1}:a]aresample=48000,adelay={int(max(0, ts)*1000)}|{int(max(0, ts)*1000)},volume={g}[e{i}];"
    fc += "[0:a]" + "".join(f"[e{i}]" for i in range(len(evs))) + f"amix=inputs={1 + len(evs)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.89[a]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-filter_complex", fc, "-map", "[a]", "-ar", "48000", wav], check=True)
def segment():
    """Découpe voix.mp3 en 14 phrases : faster-whisper (horodatage des mots) + coupure au milieu des blancs entre phrases."""
    from faster_whisper import WhisperModel
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", VO, "-ar", "16000", "-ac", "1", "-f", "f32le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32); words = []
    for s in WhisperModel("small", device="cpu", compute_type="int8").transcribe(a, language="fr", word_timestamps=True)[0]: words += list(s.words)
    def norm(x): return re.sub(r"[^a-z0-9]", "", x.lower().replace("é", "e").replace("è", "e").replace("ê", "e").replace("à", "a").replace("ï", "i"))
    firsts = [norm(l.split()[0]) for l in TEXTE]; starts = [0]; j = 0
    for k in range(1, len(TEXTE)):                               # premier mot de chaque phrase, dans l'ordre
        j += 1
        while j < len(words) and norm(words[j].word)[:4] != firsts[k][:4]: j += 1
        starts.append(j)
    dur = len(a)/16000; seg = []
    for k, j in enumerate(starts):
        s = 0 if k == 0 else (words[j - 1].end + words[j].start)/2
        e = dur if k == len(starts) - 1 else (words[starts[k + 1] - 1].end + words[starts[k + 1]].start)/2
        seg.append((round(s, 3), round(e, 3)))
    json.dump(seg, open(SEGF, "w")); print(seg)
def main():
    os.makedirs(OUT, exist_ok=True); v = OUT + "/_v.mp4"; a = OUT + "/_a.wav"; build_audio(a)
    for s in ("weah", "rai", "ronaldinho", "ginola"): card(s)
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "medium", "-maxrate", "6M", "-bufsize", "12M", v], stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for b in pool.imap(frame, range(int(TOTAL*FPS)), chunksize=6): pr.stdin.write(b)
    pr.stdin.close(); pr.wait(); out = OUT + ("/psg_avant_qatar_provisoire.mp4" if PROVISOIRE else "/psg_avant_qatar.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    os.remove(v); os.remove(a); subprocess.run(["rm", "-rf", OUT + "/_a"]); print(out, round(TOTAL, 2))
def stills():
    ims = []
    for i in range(len(SCENES)):
        for f in ((0.0, .55, .95) if i == 0 else (.35, .95)):
            t = STARTS[i] + f*DUR[i]; ims.append(render(int(t*FPS), t))
    sh = Image.new("RGB", (216*10, 384*((len(ims) + 9)//10)))
    for k, im in enumerate(ims): sh.paste(im.resize((216, 384)), ((k % 10)*216, (k//10)*384))
    p = os.path.join(os.environ.get("STILLS_DIR", OUT), "psg_avant_qatar_planche.jpg"); os.makedirs(os.path.dirname(p), exist_ok=True); sh.save(p, quality=85); print(p, round(TOTAL, 2))
def cover():
    global PROVISOIRE
    os.makedirs(OUT, exist_ok=True); p0, PROVISOIRE = PROVISOIRE, False; im = render(6, .2); PROVISOIRE = p0
    p = OUT + "/psg_avant_qatar_couverture.jpg"; im.save(p, quality=92); print(p)
if __name__ == "__main__":
    a = sys.argv[1:]
    if "--seg" in a: segment()
    elif "--stills" in a: stills()
    elif "--cover" in a: cover()
    else: main()
