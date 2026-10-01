"""Épisode « Légendes du foot » #6 : l'histoire du Mans FC (demandée par un abonné).
Accroche « faillite en 2013… Ligue 1 en 2026 » (l'ascenseur tombe en D6 puis remonte étage par étage), Djokovic actionnaire,
fusion de 1985 et les 24 Heures, Drogba vendu 80 000 £ (×300 pour Chelsea), usine à pépites (Gervinho, Sessègnon, Grafite),
stade neuf au bord du circuit, liquidation et chute en 6e division, pause « ton club de cœur ? », 6 défaites puis champion,
3 montées en 3 ans, Covid, investisseurs brésiliens (Djokovic, Courtois, Massa), montée validée malgré les fumigènes de Bastia,
fin « ils vont se maintenir ? » + « demande ton club ».

  python3 episodes/lemans/lemans.py output/lemans --stills [3,4]
  python3 episodes/lemans/lemans.py output/lemans --cover
  python3 episodes/lemans/lemans.py output/lemans
"""
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from story import *
import engine

TITLE = "~/légendes $ ./le_mans_fc"
SLUG = "lemans_legende"
VOICE = [os.path.join(HERE, "voix", f"scene_{i}.mp3") for i in range(1, 13)]
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
ALIGN = os.path.join(HERE, "alignement.json")
PAD = 0.15
WS, TEXTS = load_words(ALIGN)
def w(i, word, n=1, end=False):
    """Temps local (dans la scène i) où la voix prononce `word`."""
    return PAD + WS[i-1](word, n, end)

ROUGE = (206, 30, 40); ROUGE_D = (120, 22, 30); JAUNE = (250, 204, 40); NOIR = (30, 28, 28); BLANC = (250, 250, 246)
GOLD = (236, 186, 48); GRIS = (120, 120, 126); NAVY = (16, 40, 86); CHELSEA = (14, 44, 120)
VERT = (0, 150, 72); BLEU_BR = (24, 70, 160); JAUNE_BR = (252, 214, 30); ORANGE = (247, 127, 0); VERT_CI = (0, 158, 96)
SHAFT = (34, 32, 40)

LM = Player("lmp", hair=(60, 40, 30), skin=(226, 180, 140))
LM2 = Player("lmp2", hair=(24, 20, 18), skin=(150, 100, 72))
DROG = Player("drog", hair=(22, 18, 16), skin=(112, 74, 52))
GERV = Player("gerv", hair=(22, 18, 16), skin=(104, 70, 50))
SESS = Player("sess", hair=(26, 20, 18), skin=(92, 62, 44))
GRAF = Player("graf", hair=(30, 24, 20), skin=(122, 84, 60), hair_style="bald")
DJOK = Player("djok", hair=(44, 34, 28), skin=(232, 192, 160))
COUR = Player("cour", hair=(96, 70, 48), skin=(236, 198, 168))
MASS = Player("mass", hair=(44, 32, 26), skin=(214, 168, 128))
REF = Player("lmref", hair=(70, 60, 50), skin=(230, 186, 150), hair_style="bald")

# ------------------------------------------------------------------ objets
QM = Label("?", "lmqm", font("title", 280), PAL["mustard"], None, stroke=7, stroke_fill=PAL["ink"])

def hand_pos(x, y, s, side, ang, age=1.0):
    """Position de la main (bras ouvert de `ang` degrés vers l'extérieur ; side = -1 gauche, +1 droite)."""
    bs = s*lerp(.7, 1.0, age); a = math.radians(ang)
    sx = x + side*84*bs*.93; sy = y - 498*bs
    return sx + side*199*bs*math.sin(a), sy + 199*bs*math.cos(a)

def racket(cv, x, y, s=1.0, rot=0.0, a=1.0):
    """Raquette de tennis ; (x, y) = la main sur le manche."""
    if a <= .01 or s < .05: return
    L = layer(int(200*s), int(440*s), (100*s, 380*s)); d = ImageDraw.Draw(L); fc = (40, 40, 52)
    for k in range(-4, 5):
        xx = 100 + k*16; hh = 98*math.sqrt(max(0, 1 - ((xx - 100)/78)**2))
        d.line([(xx*s, (118 - hh)*s), (xx*s, (118 + hh)*s)], fill=(236, 236, 230), width=max(1, int(2*s)))
    for k in range(-5, 6):
        yy = 118 + k*17; ww = 78*math.sqrt(max(0, 1 - ((yy - 118)/98)**2))
        d.line([((100 - ww)*s, yy*s), ((100 + ww)*s, yy*s)], fill=(236, 236, 230), width=max(1, int(2*s)))
    d.ellipse([20*s, 18*s, 180*s, 218*s], outline=fc, width=max(3, int(14*s)))
    d.polygon([(72*s, 212*s), (128*s, 212*s), (108*s, 300*s), (92*s, 300*s)], fill=fc)
    d.rounded_rectangle([86*s, 296*s, 114*s, 436*s], int(8*s), fill=(236, 236, 236))
    for k in range(5): d.line([(86*s, (310 + k*24)*s), (114*s, (322 + k*24)*s)], fill=(180, 180, 186), width=max(1, int(3*s)))
    blit(cv, L, x, y, 1, rot, a)

def tball(cv, x, y, r=26):
    d = ImageDraw.Draw(cv)
    d.ellipse([x-r, y-r, x+r, y+r], fill=(214, 232, 60), outline=(150, 170, 30), width=3)
    d.arc([x-r*1.7, y-r*.9, x+r*.1, y+r*.9], -40, 40, fill=BLANC, width=4)
    d.arc([x-r*.1, y-r*.9, x+r*1.7, y+r*.9], 140, 220, fill=BLANC, width=4)

def _rc_decor(col2, num):
    def dec(d, a):
        ax, ay = a
        d.rectangle([ax-300, ay-12, ax+290, ay+2], fill=col2)
        d.polygon([(ax-36, ay-60), (ax+60, ay-62), (ax+104, ay-36), (ax-50, ay-34)], fill=(40, 44, 60))
        d.ellipse([ax-170, ay-46, ax-100, ay+14], fill=BLANC)
        d.text((ax-135, ay-16), num, font=font("title", 44), fill=NOIR, anchor="mm")
    return dec
_RC = {}
def race_car(cv, fr, x, y, s=1.0, col=ROUGE, col2=JAUNE, num="72", t=0.0):
    """Proto d'endurance vu de profil, nez vers la droite ; (x, y) = milieu du châssis."""
    k = (col, col2, num)
    if k not in _RC:
        pts = [(-300, 30), (-306, -40), (-304, -96), (-236, -96), (-244, -48), (-120, -52), (-50, -86), (70, -90),
               (150, -48), (280, -26), (312, 6), (300, 30)]
        _RC[k] = Paper(poly_pts(pts), col, f"lmrc{col}{num}", rough=1.4, hatch=True, pad=40).add(_rc_decor(col2, num))
    _RC[k].draw(cv, fr, x, y, s, 0)
    d = ImageDraw.Draw(cv)
    for wx in (-190, 190):
        cx, cy, r = x + wx*s, y + 34*s, 44*s
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(30, 30, 34)); d.ellipse([cx-r*.5, cy-r*.5, cx+r*.5, cy+r*.5], fill=(180, 180, 188))
        an = t*40
        d.line([(cx - r*.45*math.cos(an), cy - r*.45*math.sin(an)), (cx + r*.45*math.cos(an), cy + r*.45*math.sin(an))], fill=(90, 90, 96), width=max(2, int(5*s)))

def car_pass(cv, fr, t, t0, y, dur=.9, s=.9, col=ROUGE, col2=JAUNE, num="72"):
    """Voiture qui traverse l'écran de gauche à droite (passe au centre à t0 + dur/2)."""
    u = prog(t, t0, dur)
    if 0 < u < 1:
        x = lerp(-420, W + 420, u)
        d = ImageDraw.Draw(cv)
        for k in range(7):
            ly = y - 70 + k*24; l0 = x - 330*s - 60 - (k*53) % 140
            d.line([(l0 - 260, ly), (l0, ly)], fill=(235, 235, 228), width=4)
        race_car(cv, fr, x, y, s, col, col2, num, t)

def track(cv, y0, y1, t=0.0, speed=0.0):
    """Bitume de circuit avec vibreurs rouges et blancs (défilent si speed > 0)."""
    d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    d.rectangle([sx0, y0, sx1, y1], fill=(76, 76, 82))
    off = (t*speed) % 160
    for k in range(-2, 16):
        x = sx0 + k*80 - off; col = ROUGE if k % 2 == 0 else BLANC
        d.rectangle([x, y0 - 26, x + 80, y0], fill=col); d.rectangle([x, y1, x + 80, y1 + 26], fill=col)
    for k in range(-1, 9):
        x = sx0 + k*160 - (t*speed*1.5) % 160
        d.rectangle([x, (y0 + y1)/2 - 6, x + 90, (y0 + y1)/2 + 6], fill=(232, 232, 222))

def checkered(cv, x, y, w=280, h=180, t=0.0, a=1.0, rot=0.0):
    """Drapeau à damier qui ondule."""
    if a <= .01: return
    L = layer(int(w+60), int(h+80), (w/2+30, h/2+40)); d = ImageDraw.Draw(L)
    cols, rows = 8, 5; cw, ch = w/cols, h/rows
    d.rectangle([10, 20, 24, h + 78], fill=(90, 90, 96))
    for k in range(cols):
        off = 12*math.sin(k/cols*math.pi*2 - t*7)*(k/cols)
        for r in range(rows):
            d.rectangle([24 + k*cw, 30 + off + r*ch, 24 + (k+1)*cw + 1, 30 + off + (r+1)*ch + 1], fill=NOIR if (k + r) % 2 else BLANC)
    blit(cv, L, x, y, a, rot, 1)

def tricolor(cv, x, y, cols, w=300, h=200, t=0.0, a=1.0, rot=0.0):
    """Drapeau à trois bandes verticales qui ondule (Côte d'Ivoire…)."""
    if a <= .01: return
    L = layer(int(w+40), int(h+60), (w/2+20, h/2+30)); d = ImageDraw.Draw(L); n = 30
    for k in range(n):
        off = 12*math.sin(k/n*math.pi*2 - t*5)*(k/n)
        d.rectangle([20 + k*w/n, 30+off, 20 + (k+1)*w/n + 1, 30+h+off], fill=cols[min(2, int(3*k/n))])
    blit(cv, L, x, y, a, rot, 1)

def br_flag(cv, x, y, w=300, h=200, t=0.0, a=1.0, rot=0.0):
    """Drapeau vert-jaune stylisé (losange jaune, disque bleu) qui ondule."""
    if a <= .01: return
    L = layer(int(w+40), int(h+60), (w/2+20, h/2+30)); d = ImageDraw.Draw(L); n = 24
    for k in range(n):
        off = 10*math.sin(k/n*math.pi*2 - t*5)*(k/n)
        d.rectangle([20 + k*w/n, 30+off, 20 + (k+1)*w/n + 1, 30+h+off], fill=VERT)
    cx, cy = 20 + w/2, 30 + h/2
    d.polygon([(cx - w*.42, cy), (cx, cy - h*.4), (cx + w*.42, cy), (cx, cy + h*.4)], fill=JAUNE_BR)
    d.ellipse([cx - h*.24, cy - h*.24, cx + h*.24, cy + h*.24], fill=BLEU_BR)
    blit(cv, L, x, y, a, rot, 1)

SHIELD_PTS = [(-110, -130), (110, -130), (110, 10), (60, 100), (0, 140), (-60, 100), (-110, 10)]
def _shield(key, col, col2, txt, size=60, fg=BLANC):
    def dec(d, a):
        ax, ay = a
        d.polygon([(ax-110, ay-130), (ax, ay-130), (ax, ay+140), (ax-60, ay+100), (ax-110, ay+10)], fill=col2)
        d.text((ax, ay-10), txt, font=font("title", size), fill=fg, anchor="mm", stroke_width=5, stroke_fill=NOIR)
    return Paper(poly_pts(SHIELD_PTS), col, key, rough=1.6, hatch=True).add(dec)
SH_A = _shield("lmsha", (40, 90, 170), (250, 250, 246), "1", 110)
SH_B = _shield("lmshb", (30, 120, 70), (250, 250, 246), "2", 110)
SH_MUC = _shield("lmshm", ROUGE, JAUNE, "MUC 72", 58)

def _arena(d, a):
    ax, ay = a
    d.ellipse([ax-430, ay-190, ax+430, ay-40], fill=(200, 60, 60))                      # gradins rouges vus d'en haut
    d.ellipse([ax-300, ay-150, ax+300, ay-70], fill=(70, 150, 84))                       # pelouse
    for k in range(-9, 10):                                                             # nervures de la façade
        x = ax + k*44; d.line([(x, ay-40 + abs(k)*3), (x, ay+170 - abs(k)*6)], fill=(170, 176, 186), width=6)
    d.rectangle([ax-120, ay+110, ax+120, ay+170], fill=(60, 64, 80))
ARENA = Paper(ellipse_pts(880, 400, 60), (226, 230, 236), "lmarena", rough=1.6, hatch=True).add(_arena)

def _doc(title, lines, col=PAL["ink"]):
    def dec(d, a):
        ax, ay = a
        d.text((ax, ay-200), title, font=font("title", 50), fill=col, anchor="mm")
        for i, ln in enumerate(lines): d.text((ax, ay-120 + i*64), ln, font=font("hand", 46), fill=PAL["ink"], anchor="mm")
        for k in range(4): d.line([(ax-150, ay+90 + k*36), (ax + (150 if k % 3 else 70), ay+90 + k*36)], fill=(176, 170, 156), width=5)
    return dec
CONTRAT = Paper(rect_pts(420, 520), (250, 248, 238), "lmcontrat", rough=1.6).add(_doc("CONTRAT PRO", ["Le Mans", "joueur : D. Drogba"]))
VERDICT = Paper(rect_pts(460, 540), (250, 248, 238), "lmverdict", rough=1.6).add(
    _doc("COMMISSION", ["de discipline", "Bastia 0 - 2 Le Mans"], ROUGE_D))

def virus(cv, x, y, r, rot=0.0, a=1.0, col=(90, 180, 110)):
    if a <= .01: return
    d = ImageDraw.Draw(cv); r *= a
    for k in range(10):
        an = rot + k*math.pi/5
        d.line([(x + r*math.cos(an), y + r*math.sin(an)), (x + r*1.45*math.cos(an), y + r*1.45*math.sin(an))], fill=col, width=max(2, int(r*.16)))
        d.ellipse([x + r*1.45*math.cos(an) - r*.2, y + r*1.45*math.sin(an) - r*.2, x + r*1.45*math.cos(an) + r*.2, y + r*1.45*math.sin(an) + r*.2], fill=(220, 70, 70))
    d.ellipse([x-r, y-r, x+r, y+r], fill=col, outline=(40, 100, 60), width=max(2, int(r*.08)))
    for k in range(4):
        an = rot*1.3 + k*1.7; d.ellipse([x + r*.45*math.cos(an) - r*.14, y + r*.45*math.sin(an) - r*.14, x + r*.45*math.cos(an) + r*.14, y + r*.45*math.sin(an) + r*.14], fill=(60, 130, 80))

def nugget(cv, x, y, s=1.0, t=0.0):
    """Pépite d'or qui scintille."""
    d = ImageDraw.Draw(cv)
    pts = [(-40, -10), (-20, -34), (16, -38), (42, -14), (36, 20), (6, 34), (-30, 26)]
    d.polygon([(x + px*s, y + py*s) for px, py in pts], fill=GOLD, outline=(170, 120, 30))
    d.polygon([(x + px*s*.5 - 8*s, y + py*s*.5 - 8*s) for px, py in pts], fill=(255, 230, 140))
    draw_star(cv, x + 30*s, y - 34*s, 18*s*(.6 + .4*math.sin(t*9)), 1, t*3)

def helmet(cv, x, y, s=1.0):
    d = ImageDraw.Draw(cv)
    d.chord([x-62*s, y-60*s, x+62*s, y+64*s], 160, 380, fill=(200, 24, 34)); d.rectangle([x-56*s, y+8*s, x+60*s, y+40*s], fill=(200, 24, 34))
    d.rectangle([x-10*s, y-22*s, x+60*s, y+4*s], fill=(40, 44, 60)); d.line([(x-56*s, y+22*s), (x+60*s, y+22*s)], fill=BLANC, width=max(2, int(6*s)))

def glove(cv, x, y, s=1.0):
    """Gant de gardien (main en (x, y))."""
    if s <= .05: return
    d = ImageDraw.Draw(cv)
    d.rounded_rectangle([x-34*s, y-46*s, x+34*s, y+40*s], int(16*s), fill=(250, 210, 60), outline=NOIR, width=max(2, int(4*s)))
    d.rectangle([x-34*s, y+16*s, x+34*s, y+40*s], fill=(40, 44, 60))

def bricks(cv, t, t0, x0=110, y_base=1520, cols=6, rows=4, bw=146, bh=62, step=.07):
    """Mur de briques qui se monte brique par brique (chaque brique tombe à sa place)."""
    d = ImageDraw.Draw(cv); n = 0
    for r in range(rows):
        for c in range(cols - (r % 2)):
            tb = t0 + n*step; n += 1
            if t < tb: return
            u = ease_out_cubic(prog(t, tb, .22))
            x = x0 + c*bw + (bw/2 if r % 2 else 0); y = y_base - (r + 1)*bh
            yy = lerp(y - 500, y, u)
            d.rectangle([x + 3, yy + 3, x + bw - 3, yy + bh - 3], fill=(196, 92, 60), outline=(120, 56, 36), width=4)

def calendar(cv, fr, x, y, txt, s=1.0, rot=0.0, a=1.0, key="lmcal"):
    if a <= .01: return
    L = layer(int(300*s), int(320*s), (150*s, 160*s)); d = ImageDraw.Draw(L)
    d.rectangle([10*s, 30*s, 290*s, 310*s], fill=(250, 248, 238), outline=PAL["ink"], width=max(2, int(5*s)))
    d.rectangle([10*s, 30*s, 290*s, 100*s], fill=ROUGE)
    for k in (80, 220): d.rectangle([(k-8)*s, 10*s, (k+8)*s, 50*s], fill=(80, 80, 88))
    d.text((150*s, 205*s), txt, font=font("title", int(96*s)), fill=PAL["ink"], anchor="mm")
    blit(cv, L, x, y, 1, rot, a)

SCOREBOARD = scoreboard_sprite(820, 330, "lmscore")
def score2(cv, fr, x, y, la, lb, a, b, sub="", s=1.0):
    if s <= .02: return
    L = layer(900, 420, (450, 210)); SCOREBOARD.draw(L, fr, 450, 210, 1, 0, 1)
    d = ImageDraw.Draw(L)
    for x_, lab in ((180, la), (720, lb)): d.text((x_, 130), lab, font=font("mono", 64 if len(lab) <= 5 else 48), fill=(200, 196, 190), anchor="mm")
    d.text((450, 220), f"{a} - {b}", font=font("title", 150), fill=(255, 204, 70), anchor="mm")
    if sub: d.text((450, 330), sub, font=font("mono", 38), fill=(170, 166, 160), anchor="mm")
    blit(cv, L, x, y, s)

def stripes(d, col, n=12):
    """Rayures verticales sur toute la scène (une bande sur deux)."""
    sx0, sy0, sx1, sy1 = STAGE; wd = (sx1 - sx0)/n
    for k in range(0, n, 2): d.rectangle([sx0 + k*wd, sy0, sx0 + (k+1)*wd, sy1], fill=col)

def walk(t, speed=9, amp=22):
    ph = math.sin(t*speed); return (amp*ph, -amp*ph), abs(math.sin(t*speed))*8

def stadium(cv, fr, key, t=0.0, sky=(18, 22, 46), grass=(46, 112, 64), horizon=1060, pal=None):
    stage_fill(cv, fr, sky, key); d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    rnd = random.Random(key)
    pal = pal or [ROUGE, JAUNE, (200, 196, 190), (160, 40, 40), (250, 230, 120), (70, 60, 60)]
    for row in range(7):
        ry = 560 + row*68; n = 18 + row
        for k in range(n):
            x = 50 + k*(980/(n-1)); jump = 6*abs(math.sin(t*7 + k*1.3 + row))
            d.ellipse([x-17, ry-17-jump, x+17, ry+17-jump], fill=rnd.choice(pal))
    for fx in (150, 930):
        for r, c in ((70, (70, 70, 60)), (46, (200, 196, 150)), (26, (255, 252, 230))): d.ellipse([fx-r, 300-r, fx+r, 300+r], fill=c)
    for k in range(8):
        y0 = horizon + k*(sy1-horizon)/8
        d.rectangle([sx0, y0, sx1, y0 + (sy1-horizon)/8 + 1], fill=grass if k % 2 == 0 else tuple(int(c*.9) for c in grass))
    d.line([(sx0, horizon), (sx1, horizon)], fill=(230, 236, 226), width=6)
    if int(t*24) % 7 == 0:
        x, y = rnd.uniform(80, 1000), rnd.uniform(540, 980); d.ellipse([x-9, y-9, x+9, y+9], fill=(255, 255, 250))

def spin(cv, fr, pl, x, y, s, t, t0, kit_a, kit_b, dur=.45, **kw):
    """Tour sur lui-même avec changement de maillot à mi-course ; sinon dessin normal."""
    su = prog(t, t0, dur)
    if 0 < su < 1:
        L = pl.render_layer(fr, s, age=kw.get("age", 1), kit=kit_a if su < .25 else kit_b, mood=kw.get("mood", "happy"))
        blit_sxy(cv, L, x, y, max(.04, abs(math.cos(su*math.pi*2))), 1)
    else:
        pl.draw(cv, fr, x, y, s, kit=kit_b if su >= 1 else kit_a, t=t, **kw)

def trophy_lift(cv, fr, pl, x, y, s, kit, t, trophy=CUP, mood="cheer"):
    pl.draw(cv, fr, x, y, s, age=1, kit=kit, mood=mood, arms=(160, 160), legs=(12, 12), t=t)
    trophy.draw(cv, fr, x, y - 850*s + 8*math.sin(t*6), .9*s, 3*math.sin(t*4))

def shaft(cv, fr, t, speed=0.0, key="lmshaft"):
    """Cage d'ascenseur ; speed > 0 : les étages descendent (on monte)."""
    stage_fill(cv, fr, SHAFT, key); d = ImageDraw.Draw(cv); sx0, sy0, sx1, sy1 = STAGE
    for j in range(8):
        y = (j*260 + t*speed) % 2080 - 80
        d.rectangle([sx0, y, sx1, y + 16], fill=(70, 66, 80)); d.line([(sx0, y + 30), (sx1, y + 30)], fill=(56, 52, 64), width=4)

def rain(cv, t, n=60, col=(140, 150, 170)):
    d = ImageDraw.Draw(cv)
    for k in range(n):
        x = (k*89) % 1060 + 10; y = (k*173 + t*1300) % 1800 + 120; d.line([(x, y), (x - 8, y + 36)], fill=col, width=3)

def bolt(cv, x, y, s=1.0, a=1.0):
    if a <= .01: return
    pts = [(0, 0), (-60, 200), (-10, 200), (-70, 420), (80, 150), (20, 150), (70, 0)]
    ImageDraw.Draw(cv).polygon([(x + px*s, y + py*s) for px, py in pts], fill=(255, 240, 140))

BILL = Paper(rect_pts(160, 80), (70, 150, 120), "lmbill", rough=1.4, hatch=True).add(
    lambda d, a: [d.rectangle([a[0]-70, a[1]-34, a[0]+70, a[1]+34], outline=PAL["cream"], width=3), d.text((a[0], a[1]), "£", font=font("title", 50), fill=PAL["cream"], anchor="mm")])
def bill_rain(cv, fr, t, t0, dur=3.0, n=16, key="lmbills"):
    if t < t0: return
    rnd = random.Random(key)
    for i in range(n):
        tt = t - t0 - rnd.uniform(0, dur*.5)
        if tt < 0: continue
        x = rnd.uniform(90, 990) + 50*math.sin(tt*2+i); y = 150 + tt*rnd.uniform(420, 640)
        if y < 1950: BILL.draw(cv, fr, x, y, rnd.uniform(.8, 1.1), 30*math.sin(tt*3+i))

def carton(cv, x, y, s=1.0):
    """Carton de déménagement porté devant soi."""
    d = ImageDraw.Draw(cv)
    d.rectangle([x-95*s, y-70*s, x+95*s, y+70*s], fill=(206, 160, 104), outline=(140, 100, 60), width=max(2, int(5*s)))
    d.rectangle([x-95*s, y-70*s, x+95*s, y-40*s], fill=(186, 140, 88)); d.rectangle([x-14*s, y-70*s, x+14*s, y+70*s], fill=(226, 196, 150))

def suitcase(cv, x, y, s=1.0):
    d = ImageDraw.Draw(cv)
    d.rounded_rectangle([x-70*s, y, x+70*s, y+110*s], int(12*s), fill=(150, 96, 56), outline=(90, 56, 30), width=max(2, int(5*s)))
    d.rectangle([x-70*s, y+46*s, x+70*s, y+58*s], fill=(110, 70, 40)); d.arc([x-26*s, y-30*s, x+26*s, y+10*s], 180, 360, fill=(90, 56, 30), width=max(3, int(8*s)))

TAGP = price_tag("", "lmtag", PAL["mustard"])
def tag80(cv, fr, x, y, s, txt):
    if s <= .02: return
    TAGP.draw(cv, fr, x, y, s, -6)
    LBL(txt, "lmtagt", font("title", 64), PAL["ink"], None).draw(cv, fr, x + 100*s, y - 10*s, s, -6)

def row(cv, fr, y, txt, hl_, a=1.0, key="lmrow"):
    if a <= .01: return
    lab = LBL(txt, key + ("h" if hl_ else "n"), font("title", 64), BLANC if hl_ else PAL["ink"], ROUGE if hl_ else PAL["paper"], padx=24, pady=6, rough=2, maxw=860)
    lab.draw(cv, fr, CX, y, a, 0)

# ------------------------------------------------------------------ labels
H1 = HL("FAILLITE EN 2013…", "lmh1", PAL["mustard"], PAL["ink"], 96)
H1b = HL("13 ANS PLUS TARD…", "lmh1b", PAL["mustard"], PAL["ink"], 96)
K1a = STAMP("FAILLITE", "lmk1a", ROUGE, 140); K1b = KW("6e DIVISION", "lmk1b", ROUGE, size=110)
K1c = KW("LIGUE 1 !", "lmk1c", PAL["ink"], JAUNE, 150)
T1a = TAG("et parmi ses actionnaires…", "lmt1a", PAL["paper"], size=54)
K1d = KW("NOVAK DJOKOVIC ?!", "lmk1d", PAL["mustard"], PAL["ink"], 92)
K1e = KW("L'HISTOIRE FOLLE DU", "lmk1e", PAL["ink"], size=78); N1 = STAMP("MANS FC", "lmn1", ROUGE, 150)
K2a = KW("1985", "lmk2a", PAL["ink"], size=150); T2a = TAG("2 clubs de la ville", "lmt2a", PAL["paper"], size=54)
K2b = STAMP("FUSION", "lmk2b", ROUGE, 110); T2b = TAG("Le Mans Union Club 72", "lmt2b", PAL["paper"], size=52)
SW_R = Label("ROUGE", "lmswr", font("title", 96), BLANC, ROUGE, padx=40, pady=16, rough=4)
SW_J = Label("JAUNE", "lmswj", font("title", 96), PAL["ink"], JAUNE, padx=40, pady=16, rough=4)
K2c = STAMP("LES SANG ET OR", "lmk2c", ROUGE, 100)
K2d = KW("24 HEURES DU MANS", "lmk2d", PAL["ink"], size=90); T2c = TAG("connue dans le monde entier", "lmt2c", PAL["paper"], size=52)
K3a = KW("FIN DES ANNÉES 90", "lmk3a", PAL["ink"], size=90); T3a = TAG("jeune Ivoirien", "lmt3a", PAL["paper"], size=54)
N3 = STAMP("DIDIER DROGBA", "lmn3", ORANGE, 110)
K3b = KW("1er CONTRAT PRO", "lmk3b", ROUGE, size=100)
K3c = KW("2002", "lmk3c", PAL["ink"], size=150); T3b = TAG("vendu à Guingamp", "lmt3b", PAL["paper"], size=54)
T3c = TAG("2 ans et demi plus tard…", "lmt3c", PAL["paper"], size=50); T3d = TAG("(via l'OM)", "lmt3d", PAL["paper"], size=46)
K3d = STAMP("×300 !", "lmk3d", ROUGE, 170)
K4a = KW("2003", "lmk4a", PAL["ink"], size=150); K4b = STAMP("LIGUE 1 !", "lmk4b", ROUGE, 130); T4a = TAG("pour la 1re fois", "lmt4a", PAL["paper"], size=54)
K4c = KW("USINE À PÉPITES", "lmk4c", GOLD, PAL["ink"], 100)
NAMES4 = [Label(n, "lmn4"+n, font("title", 58), BLANC, ROUGE, padx=18, pady=6, rough=2) for n in ("GERVINHO", "SESSÈGNON", "GRAFITE")]
DEST4 = [Label(n, "lmd4"+n, font("hand", 46), PAL["ink"], PAL["paper"], padx=14, pady=4, rough=2) for n in ("Lille", "PSG", "Wolfsburg")]
T4b = TAG("… avant de partir plus haut", "lmt4b", PAL["paper"], size=52)
K5a = KW("2010", "lmk5a", PAL["ink"], size=150); K5b = STAMP("LIGUE 2", "lmk5b", GRIS, 120)
T5a = TAG("janvier 2011", "lmt5a", PAL["paper"], size=54); T5b = TAG("tout neuf !", "lmt5b", PAL["mustard"], size=56)
T5c = TAG("au bord du circuit des 24 Heures", "lmt5c", PAL["paper"], size=48)
K6a = KW("CATASTROPHE", "lmk6a", ROUGE, size=110); K6b = KW("2013", "lmk6b", PAL["ink"], size=110)
T6a = TAG("de dettes", "lmt6a", PAL["paper"], size=56); K6c = STAMP("LIQUIDÉ", "lmk6c", ROUGE, 150)
K6d = KW("6e DIVISION", "lmk6d", ROUGE, size=110); K6e = KW("MOINS DE 3 ANS", "lmk6e", PAL["ink"], size=100)
T6b = TAG("après l'inauguration du stade", "lmt6b", PAL["paper"], size=50)
K7a = KW("PETITE PAUSE !", "lmk7a", PAL["ink"], size=84)
K7b = Label("TON CLUB DE CŒUR ?", "lmk7b", font("title", 74), PAL["cream"], ROUGE, maxw=480, padx=30, pady=8, rough=3.5)
NAMES7 = [LBL(n, f"lmnm{n}", font("hand", 46), PAL["ink"], None) for n in ("OM ?", "Lens ?", "Nantes ?", "ASSE ?")]
K7c = KW("EN COMMENTAIRE", "lmk7c", PAL["ink"], size=84); K7d = KW("ON REPREND !", "lmk7d", PAL["ink"], size=84)
T7a = TAG("le prochain épisode ?", "lmt7a", PAL["paper"], size=52)
CARD = Paper(rect_pts(200, 250), PAL["paper"], "lmcard", rough=2)
HEART = Paper(heart_pts(9), ROUGE, "lmheart", rough=1.6)
K8a = KW("TOUT RECONSTRUIRE", "lmk8a", PAL["ink"], size=96); T8a = TAG("saison 2013-2014", "lmt8a", PAL["paper"], size=54)
K8b = STAMP("CHAMPION !", "lmk8b", ROUGE, 130); K8c = KW("3 MONTÉES EN 3 ANS", "lmk8c", ROUGE, size=90)
T8b = TAG("à partir de 2016", "lmt8b", PAL["paper"], size=54)
K9a = KW("2019", "lmk9a", PAL["ink"], size=150); K9b = STAMP("RETOUR EN LIGUE 2", "lmk9b", ROUGE, 96)
K9c = KW("COVID", "lmk9c", (60, 130, 80), size=130); K9d = STAMP("CHAMPIONNAT ARRÊTÉ", "lmk9d", ROUGE, 84)
T9a = TAG("relégué en National", "lmt9a", PAL["paper"], size=52); K9e = KW("5 ANS EN NATIONAL", "lmk9e", PAL["ink"], size=90)
K10a = KW("INVESTISSEURS BRÉSILIENS", "lmk10a", VERT, size=66); T10a = TAG("le groupe OutField", "lmt10a", PAL["paper"], size=52)
K10b = KW("DES STARS !", "lmk10b", GOLD, PAL["ink"], 110)
N10 = [Label(n, "lmn10"+n, font("title", 56), BLANC, c, padx=18, pady=6, rough=2) for n, c in (("DJOKOVIC", NAVY), ("COURTOIS", (60, 60, 70)), ("MASSA", ROUGE))]
S10 = [Label(n, "lms10"+n, font("hand", 40), PAL["ink"], PAL["paper"], padx=12, pady=4, rough=2) for n in ("tennis", "gardien", "ex-pilote de F1")]
K10c = KW("UN PILOTE DE F1 AU MANS…", "lmk10c", PAL["ink"], size=70); K10d = STAMP("ÇA NE S'INVENTE PAS !", "lmk10d", ROUGE, 80)
K11a = KW("2025", "lmk11a", PAL["ink"], size=150); K11b = STAMP("RETOUR EN LIGUE 2", "lmk11b", ROUGE, 96)
K11c = KW("2026", "lmk11c", PAL["ink"], size=150); T11a = TAG("2e du championnat !", "lmt11a", PAL["mustard"], size=54)
T11b = TAG("Bastia, mai 2026", "lmt11b", PAL["paper"], size=52); K11d = STAMP("MATCH ARRÊTÉ", "lmk11d", ROUGE, 110)
T11c = TAG("fumigènes sur la pelouse", "lmt11c", PAL["paper"], size=50)
K11e = STAMP("SCORE VALIDÉ", "lmk11e", (40, 140, 70), 110); K11f = KW("LIGUE 1 !", "lmk11f", PAL["ink"], JAUNE, 170)
T11d = TAG("16 ans après", "lmt11d", PAL["paper"], size=54)
K12a = KW("EN 13 ANS !", "lmk12a", PAL["ink"], size=120); K12b = KW("ILS VONT SE MAINTENIR ?", "lmk12b", PAL["ink"], size=70)
BTN_O = Label("OUI", "lmbo", font("title", 110), PAL["ink"], JAUNE, padx=40, pady=10, rough=3)
BTN_N = Label("NON", "lmbn", font("title", 110), BLANC, (90, 90, 96), padx=40, pady=10, rough=3)
K12c = KW("DEMANDE TON CLUB !", "lmk12c", ROUGE, size=86); T12a = TAG("demandée par un abonné", "lmt12a", PAL["paper"], size=54)
BTN_SUB = Label("+ ABONNE-TOI", "lmbsub", font("title", 96), (255, 255, 255), (230, 40, 80), padx=40, pady=14, rough=2.5)

# ------------------------------------------------------------------ SCÈNE 1 — faillite, 6e division… Ligue 1, Djokovic
FLOORS = ["D6", "D5", "D4", "D3", "L2", "L1"]
def s1a(cv, fr, t):
    tf = w(1, "faillite"); te = w(1, "tombe") - .05; td = w(1, "division")
    stage_fill(cv, fr, (110, 24, 32), "lms1a")
    rays(cv, (CX, 1100), t, .5, 14, 1500, (160, 50, 50), .12, .15)
    LM.draw(cv, fr, CX, 1720, 1.05, age=1, kit="lemans", mood="surprised" if t > tf else "normal", t=t, look=(0, -1))
    floor_panel(cv, fr, CX, 680, "L2", t, True, 1.3, pop_in(t, .05, .2))
    if t > tf: grayscale(cv, prog(t, tf, .3)*.6)
    hl(cv, fr, H1, t, -.3)
    show_stamp(cv, fr, K1a, t, tf, CX, 930, -6)
    elevator_drop(cv, t, te, td - te)
    if t > td:
        shaft(cv, fr, t)
        LM.draw(cv, fr, CX, 1720, 1.05, age=1, kit="lemans", mood="sad", t=t, look=(0, 1))
        floor_panel(cv, fr, CX, 640, "D6", t, True, 1.8, 1)
        kw(cv, fr, K1b, t, td, None, CX, 930, 3)

def s1b(cv, fr, t):
    t0 = w(1, "Treize", 2) - .1; tl = w(1, "Ligue")
    if t < tl:
        shaft(cv, fr, t, 900 + 2200*prog(t, t0, tl - t0))
        u = prog(t, t0 + .15, tl - t0 - .35)
        lab = FLOORS[min(len(FLOORS) - 2, int(u*(len(FLOORS) - 1)))]
        LM.draw(cv, fr, CX, 1720, 1.05, age=1, kit="lemans", mood="surprised", t=t, arms=(40, 40))
        floor_panel(cv, fr, CX, 640, lab, t, False, 1.8, 1)
    else:
        stage_fill(cv, fr, ROUGE, "lms1l1")
        rays(cv, (CX, 1000), t, 1.0, 16, 1500, JAUNE)
        LM.draw(cv, fr, CX, 1720, 1.05, age=1, kit="lemans", mood="cheer", arms=(160, 160), legs=(12, 12), t=t)
        floor_panel(cv, fr, CX, 640, "L1", t, False, 1.8, 1)
        kw(cv, fr, K1c, t, tl, None, CX, 930, -3)
        confetti(cv, fr, "lmc1", t - tl, 80, 3, [JAUNE, BLANC, (255, 150, 40)])
    hl(cv, fr, H1b, t, t0)

def s1c(cv, fr, t):
    sx0, sy0, sx1, sy1 = STAGE
    stage_fill(cv, fr, (40, 96, 170), "lms1c"); d = ImageDraw.Draw(cv)
    d.rectangle([90, 1150, 990, sy1 + 10], outline=BLANC, width=8); d.line([(CX, 1150), (CX, sy1)], fill=BLANC, width=6)
    d.rectangle([sx0, 1090, sx1, 1120], fill=(30, 30, 34))   # filet
    for k in range(0, 1080, 30): d.line([(k, 1090), (k + 15, 1120)], fill=(90, 90, 96), width=2)
    tn = w(1, "Novak")
    show(cv, fr, T1a, t, w(1, "parmi"), None, CX, 420, -2)
    if t < tn: QM.draw(cv, fr, CX, 820 + 12*math.sin(t*4), .9*win(t, w(1, "actionnaires") - .1), 8)
    else:
        a = pop_in(t, tn - .05, .35)
        DJOK.draw(cv, fr, CX, 1760, 1.0*a, age=1, kit="tennis", mood="cheer", arms=(30, 150), legs=(10, 10), t=t)
        hx, hy = hand_pos(CX, 1760, 1.0*a, 1, 150)
        racket(cv, hx, hy, 1.0*a, -30)
        tb = w(1, "Djokovic")
        if t > tb:
            u = prog(t, tb, .5); tball(cv, lerp(hx - 60, -80, u), lerp(hy - 260, 300, u) - 300*math.sin(u*math.pi), 28)
        kw(cv, fr, K1d, t, tn, None, CX, 600, -3)
        camera_flashes(cv, fr, "lmcf1", t - tn, 1.4, 10)

def s1d(cv, fr, t):
    stage_fill(cv, fr, JAUNE, "lms1d"); d = ImageDraw.Draw(cv)
    stripes(d, ROUGE, 10)
    tm = w(1, "Mans")
    for P, x, k in ((LM2, 250, 0), (LM, CX, 1), (LM2, 830, 2)):
        hop = 60*abs(math.sin(t*6 + k)) if t > tm else 0
        P.draw(cv, fr, x, 1740 - hop, .82 if k != 1 else .95, age=1, kit="lemans", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
    kw(cv, fr, K1e, t, w(1, "l'histoire") - .05, None, CX, 440, -3)
    show_stamp(cv, fr, N1, t, tm - .05, CX, 640, -4)
    confetti(cv, fr, "lmc1d", t - tm, 90, 4, [ROUGE, JAUNE, BLANC])

def s1(cv, fr, t, T):
    shots(cv, fr, t, [(0, s1a), (w(1, "Treize", 2) - .1, s1b), (w(1, "Et", 2) - .1, s1c), (w(1, "Voici") - .1, s1d)])
    impact(cv, t, .02, 16); impact(cv, t, w(1, "faillite"), 18); impact(cv, t, w(1, "division") + .02, 24); flashes(cv, t, w(1, "division"), .12, .6)
    impact(cv, t, w(1, "Ligue"), 20); flashes(cv, t, w(1, "Ligue"), .12, .7); punch(cv, t, w(1, "Novak"), 1.08)
    punch(cv, t, w(1, "Mans"), 1.08); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 2 — 1985, rouge et jaune, les 24 Heures
def s2a(cv, fr, t):
    stage_fill(cv, fr, (240, 230, 206), "lms2a")
    tf = w(2, "fusion"); u = ease_io(prog(t, tf, .45))
    if u < 1:
        SH_A.draw(cv, fr, lerp(270, CX - 40, u), 1060, 1.2*pop_in(t, .1), lerp(-8, 10, u))
        SH_B.draw(cv, fr, lerp(810, CX + 40, u), 1060, 1.2*pop_in(t, .3), lerp(8, -10, u))
    else:
        rays(cv, (CX, 1060), t, prog(t, tf + .45, .3), 14, 900, (250, 214, 120))
        SH_MUC.draw(cv, fr, CX, 1060, 1.5*slam(t, tf + .45, .2), -3)
        particles(cv, fr, "lmp2", (CX, 1060), prog(t, tf + .45, .6), 18, 300, [ROUGE, JAUNE], 16)
        show(cv, fr, T2b, t, tf + .7, None, CX, 1330, 2)
    kw(cv, fr, K2a, t, w(2, "mille") - .05, None, CX, 430, -3)
    show(cv, fr, T2a, t, w(2, "deux") - .1, None, CX, 620, -2)
    show_stamp(cv, fr, K2b, t, tf + .45, CX, 760, 4)

def s2b(cv, fr, t):
    stage_fill(cv, fr, (240, 230, 206), "lms2b"); d = ImageDraw.Draw(cv)
    tr, tj, ts = w(2, "rouge"), w(2, "jaune"), w(2, "Sang")
    ar, aj = pop_in(t, tr - .05, .35), pop_in(t, tj - .05, .35)
    sx0, sy0, sx1, sy1 = STAGE   # la moitié gauche se peint en rouge, la droite en jaune
    if ar > 0: d.rectangle([sx0, sy0, sx0 + (CX - sx0)*ar, sy1], fill=ROUGE)
    if aj > 0: d.rectangle([sx1 - (sx1 - CX)*aj, sy0, sx1, sy1], fill=JAUNE)
    SW_R.draw(cv, fr, 290, 540, ar, -6); SW_J.draw(cv, fr, 790, 540, aj, 5)
    LM.draw(cv, fr, CX, 1740, 1.1, age=1, kit="lemans", mood="cheer" if t > ts else "happy", arms=(150, 150) if t > ts else (20, 20), t=t)
    show_stamp(cv, fr, K2c, t, ts - .05, CX, 820, -4)
    if t > ts: confetti(cv, fr, "lmc2", t - ts, 60, 3, [ROUGE, JAUNE])

def s2c(cv, fr, t):
    stage_fill(cv, fr, (150, 200, 236), "lms2c"); d = ImageDraw.Draw(cv)
    for k in range(5):   # tribune
        d.rectangle([STAGE[0], 820 + k*44, STAGE[2], 842 + k*44], fill=(196, 200, 210) if k % 2 else (176, 180, 192))
    rnd = random.Random("lms2c")
    for k in range(70):
        x = 30 + (k*15.3) % 1020; y = 830 + (k % 5)*44 + 3*math.sin(t*8 + k)
        d.ellipse([x-12, y-14, x+12, y+10], fill=rnd.choice([ROUGE, JAUNE, BLANC, (60, 64, 90)]))
    track(cv, 1120, 1420, t, 0)
    tc, t24 = w(2, "connue"), w(2, "vingt-quatre")
    car_pass(cv, fr, t, w(2, "Et", 3) - .2, 1270, .8, .9, ROUGE, JAUNE, "72")
    car_pass(cv, fr, t, t24 - .3, 1270, .8, .9, (30, 80, 170), BLANC, "8")
    car_pass(cv, fr, t, t24 + .4, 1270, .8, .9, (40, 140, 80), JAUNE, "24")
    checkered(cv, 820, 660, 280, 180, t, pop_in(t, t24 - .1), -6)
    show(cv, fr, T2c, t, w(2, "monde") - .1, None, 380, 640, -3)
    kw(cv, fr, K2d, t, t24 - .05, None, CX, 440, -3)

def s2(cv, fr, t, T):
    shots(cv, fr, t, [(0, s2a), (w(2, "Ses") - .1, s2b), (w(2, "Et", 3) - .1, s2c)])
    impact(cv, t, w(2, "fusion") + .45, 18); flashes(cv, t, w(2, "fusion") + .45, .12, .6); impact(cv, t, w(2, "Sang"), 14)
    impact(cv, t, w(2, "vingt-quatre"), 12); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 3 — Drogba : 80 000 £… puis ×300
def s3a(cv, fr, t):
    stage_fill(cv, fr, (236, 196, 130), "lms3a"); d = ImageDraw.Draw(cv)
    d.rectangle([STAGE[0], 1500, STAGE[2], STAGE[3]], fill=(200, 160, 100))
    tdb = w(3, "débarque")
    x = lerp(-160, CX, ease_out_cubic(prog(t, .1, tdb))); lg, bob = walk(t, 11, 24) if t < tdb + .3 else ((0, 0), 0)
    DROG.draw(cv, fr, x, 1700 - bob, 1.0, age=.75, kit="street", mood="happy", legs=lg, arms=(14, 20), t=t)
    hx, hy = hand_pos(x, 1700 - bob, 1.0, 1, 20, .75); suitcase(cv, hx + 10, hy - 10, 1.0)
    kw(cv, fr, K3a, t, w(3, "fin") - .1, None, CX, 430, -3)
    ti = w(3, "Ivoirien")
    if t > ti - .1:
        tricolor(cv, 780, 680, (ORANGE, BLANC, VERT_CI), 260, 170, t, pop_in(t, ti - .1), 5)
        show(cv, fr, T3a, t, ti, None, 330, 660, -3)
    show_stamp(cv, fr, N3, t, w(3, "Didier") - .05, CX, 930, -4)

def s3b(cv, fr, t):
    stage_fill(cv, fr, (176, 128, 86), "lms3b"); d = ImageDraw.Draw(cv)
    for k in range(6): d.line([(STAGE[0], 300 + k*300), (STAGE[2], 330 + k*300)], fill=(156, 110, 72), width=5)
    CONTRAT.draw(cv, fr, 690, 1050, 1.05*pop_in(t, w(3, "Il") - .1), 4)
    ts = w(3, "signe")
    if t > ts:
        txt = typewriter("D. Drogba", prog(t, ts, .7)) or " "
        LBL(txt, "lmsig", font("hand", 70), (30, 50, 120), None).draw(cv, fr, 690, 1230, 1, -6)
    DROG.draw(cv, fr, 260, 1760, .95, age=.85, kit="lemans", mood="happy", arms=(20, 60), t=t)
    kw(cv, fr, K3b, t, w(3, "premier") - .05, None, CX, 440, -3)

def s3c(cv, fr, t):
    stage_fill(cv, fr, (44, 40, 46), "lms3c"); d = ImageDraw.Draw(cv)
    stripes(d, (60, 30, 36), 8)
    tg = w(3, "Guingamp")
    spin(cv, fr, DROG, 330, 1700, 1.0, t, tg - .15, "lemans", "guingamp", age=.9, mood="happy")
    kw(cv, fr, K3c, t, w(3, "deux") - .05, None, CX, 430, -3)
    show(cv, fr, T3b, t, w(3, "vend") - .05, None, 640, 610, 3)
    t80 = w(3, "quatre-vingt", 2)
    tag80(cv, fr, 620, 960, 1.2*pop_in(t, t80 - .05, .3), "80 000 £")

def s3d(cv, fr, t):
    stage_fill(cv, fr, CHELSEA, "lms3d"); d = ImageDraw.Draw(cv)
    rays(cv, (CX, 1000), t, .8, 16, 1500, (60, 100, 200))
    t0 = w(3, "Deux", 3); tdm = w(3, "demi"); tc = w(3, "Chelsea")
    if t < tc - .15:
        spin(cv, fr, DROG, CX, 1700, 1.05, t, tdm - .1, "guingamp", "om", age=1, mood="happy")
        show(cv, fr, T3d, t, tdm + .2, tc - .25, 790, 1000, 4)
    else:
        spin(cv, fr, DROG, CX, 1700, 1.05, t, tc - .15, "om", "chelsea", age=1, mood="cheer", arms=(150, 150) if t > tc + .3 else (20, 20))
    bill_rain(cv, fr, t, w(3, "paie"), 1.2, 14)
    show(cv, fr, T3c, t, t0 - .05, tc - .1, CX, 430, -2)
    if t > tc:
        v = counter(80000, 24000000, ease_out_cubic(prog(t, tc, .9)))
        LBL(f"{v} £", "lm24m", font("title", 104), GOLD, None, stroke=6, stroke_fill=PAL["ink"]).draw(cv, fr, CX, 440, pop_in(t, tc), -2)
    show_stamp(cv, fr, K3d, t, w(3, "trois") - .05, CX, 680, -5)
    camera_flashes(cv, fr, "lmcf3", t - w(3, "trois"), 1.2, 10)

def s3(cv, fr, t, T):
    shots(cv, fr, t, [(0, s3a), (w(3, "Il") - .1, s3b), (w(3, "En") - .1, s3c), (w(3, "Deux", 3) - .1, s3d)])
    impact(cv, t, w(3, "Didier"), 14); impact(cv, t, w(3, "quatre-vingt", 2), 12); impact(cv, t, w(3, "trois"), 22)
    flashes(cv, t, w(3, "trois"), .12, .6); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 4 — 2003 : Ligue 1, l'usine à pépites
def s4a(cv, fr, t):
    stadium(cv, fr, "lms4stad", t, horizon=1100)
    tl = w(4, "Ligue")
    for P, x, k in ((LM2, 300, 0), (LM, 760, 1)):
        hop = 70*abs(math.sin(t*6 + k)) if t > tl else 0
        P.draw(cv, fr, x, 1740 - hop, .9, age=1, kit="lemans", mood="cheer" if t > tl else "happy", arms=(150, 150) if t > tl else (20, 20), t=t)
    kw(cv, fr, K4a, t, w(4, "trois") - .1, None, CX, 430, -3)
    show(cv, fr, T4a, t, w(4, "découvre"), None, 340, 620, -3)
    show_stamp(cv, fr, K4b, t, tl - .05, CX, 820, 4)
    confetti(cv, fr, "lmc4", t - tl, 80, 3, [ROUGE, JAUNE, BLANC])
    camera_flashes(cv, fr, "lmcf4", t - tl, 1.4, 10)

def s4b(cv, fr, t):
    sx0, sy0, sx1, sy1 = STAGE
    stage_fill(cv, fr, (206, 214, 224), "lms4b"); d = ImageDraw.Draw(cv)
    d.rectangle([60, 560, 1020, 1520], fill=(160, 166, 178))   # usine
    for k in range(6): d.polygon([(60 + k*160, 560), (140 + k*160, 470), (220 + k*160, 560)], fill=(140, 146, 158))
    d.rectangle([860, 300, 940, 520], fill=(120, 124, 136))
    for k in range(4):
        tt = (t*.5 + k/4) % 1.0; r = 30 + 50*tt
        d.ellipse([900 - r + 30*tt, 280 - 260*tt - r, 900 + r + 30*tt, 280 - 260*tt + r], fill=(236, 236, 240))
    d.rectangle([60, 1440, 1020, 1520], fill=(50, 50, 58))   # tapis roulant
    for k in range(14):
        x = 60 + (k*80 + t*160) % 960; d.ellipse([x - 22, 1458, x + 22, 1502], fill=(110, 110, 120))
    kw(cv, fr, K4c, t, w(4, "devient") - .05, None, CX, 300, -3)
    tp = w(4, "partir"); te = w(4, "explosent")
    for i, (P, x, word) in enumerate(((GERV, 250, "Gervinho"), (SESS, 540, "Sessègnon"), (GRAF, 830, "Grafite"))):
        ti = w(4, word) - .05
        if t < ti: continue
        a = pop_in(t, ti, .35); fly = ease_in_cubic(prog(t, tp + i*.15, .8))
        y = 1440 - 1500*fly
        P.draw(cv, fr, x, y, .72*a, age=.9, kit="lemans", mood="cheer" if t > te else "happy", arms=(150, 150) if t > te else (20, 20), t=t)
        if fly > 0: speed_lines(cv, fr, (x, y - 300), .3*min(1, fly*4), n=16, seed=i, inner=200)
        NAMES4[i].draw(cv, fr, x, (880, 800, 880)[i] - 1500*fly, a, (-5, 4, -3)[i])
        if t < tp: nugget(cv, x + 100, 1300, .9*a, t + i)
        if t > tp: DEST4[i].draw(cv, fr, x, 680, pop_in(t, tp + .3 + i*.15), (-6, 5, -4)[i])
    if t > te:
        for k in range(8):
            an = k*math.pi/4 + t; r = 120 + 200*prog(t, te, .5)
            draw_star(cv, CX + r*math.cos(an), 1150 + r*math.sin(an)*.6, 26*(1 - prog(t, te, .6)), 1, t*4)
    show(cv, fr, T4b, t, tp - .1, None, CX, 470, 2)

def s4(cv, fr, t, T):
    shots(cv, fr, t, [(0, s4a), (w(4, "Et") - .1, s4b)])
    impact(cv, t, w(4, "Ligue"), 18); flashes(cv, t, w(4, "Ligue"), .12, .6)
    for word in ("Gervinho", "Sessègnon", "Grafite"): impact(cv, t, w(4, word), 10)
    impact(cv, t, w(4, "explosent"), 14); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 5 — 2010 : Ligue 2… et un stade tout neuf au bord du circuit
def s5a(cv, fr, t):
    te = w(5, "redescend") - .05; td = w(5, "Ligue") + .1
    stage_fill(cv, fr, ROUGE_D, "lms5a")
    LM.draw(cv, fr, CX, 1720, 1.05, age=1, kit="lemans", mood="surprised", t=t)
    floor_panel(cv, fr, CX, 680, "L1", t, True, 1.5, pop_in(t, .05, .2))
    kw(cv, fr, K5a, t, w(5, "dix") - .15, None, CX, 430, -3)
    elevator_drop(cv, t, te, td - te)
    if t > td:
        shaft(cv, fr, t, 0, "lms5shaft")
        LM.draw(cv, fr, CX, 1720, 1.05, age=1, kit="lemans", mood="sad", t=t, look=(0, 1))
        floor_panel(cv, fr, CX, 680, "L2", t, True, 1.5, 1)
        show_stamp(cv, fr, K5b, t, td, CX, 430, -5)

def s5b(cv, fr, t):
    stage_fill(cv, fr, (170, 214, 236), "lms5b"); d = ImageDraw.Draw(cv)
    ts, tv = w(5, "stade"), w(5, "vingt-cinq")
    ARENA.draw(cv, fr, CX, 860, 1.05*slam(t, w(5, "Mais") - .05, .25), 0)
    if t > ts:
        for k in range(5):
            an = k*1.3 + t*2; draw_star(cv, CX + 470*math.cos(an), 860 + 220*math.sin(an), 22*(.5 + .5*math.sin(t*8 + k)), 1, t*3)
    track(cv, 1240, 1440, t, 0)
    car_pass(cv, fr, t, w(5, "circuit") - .35, 1350, .8, .8, ROUGE, JAUNE, "72")
    car_pass(cv, fr, t, w(5, "vingt-quatre") + .25, 1350, .8, .8, (30, 80, 170), BLANC, "8")
    show(cv, fr, T5a, t, w(5, "Mais") - .05, None, CX, 300, -2)
    if t > tv:
        v = counter(0, 25000, ease_out_cubic(prog(t, tv, .7)))
        LBL(f"{v} PLACES", "lm25k", font("title", 92), BLANC, None, stroke=6, stroke_fill=PAL["ink"]).draw(cv, fr, CX, 470, pop_in(t, tv), -2)
    show(cv, fr, T5b, t, w(5, "neuf") - .05, None, 760, 610, 4)
    show(cv, fr, T5c, t, w(5, "juste") - .05, None, CX, 1150, -2)
    tem = w(5, "emménage")
    if t > tem - .6:
        u = prog(t, tem - .6, 1.2); x = lerp(-150, 230, ease_out_cubic(u)); lg, bob = walk(t, 11, 22) if u < 1 else ((0, 0), 0)
        LM.draw(cv, fr, x, 1760 - bob, .85, age=1, kit="lemans", mood="happy", arms=(-10, -10), legs=lg, t=t)
        carton(cv, x, 1760 - bob - 360, .85)

def s5(cv, fr, t, T):
    shots(cv, fr, t, [(0, s5a), (w(5, "Mais") - .1, s5b)])
    impact(cv, t, w(5, "Ligue") + .1, 18); impact(cv, t, w(5, "stade"), 14); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 6 — 2013 : 14 M€ de dettes, liquidé, 6e division
def s6a(cv, fr, t):
    stage_fill(cv, fr, (40, 44, 56), "lms6a")
    rain(cv, t)
    tc = w(6, "catastrophe")
    if tc < t < tc + .35: bolt(cv, 700, 160, 1.4, 1)
    LM.draw(cv, fr, CX, 1760, 1.0, age=1, kit="lemans", mood="sad", t=t, look=(0, 1))
    kw(cv, fr, K6a, t, tc - .05, None, CX, 430, -3)
    kw(cv, fr, K6b, t, w(6, "En") - .05, None, 300, 620, -4)
    tq = w(6, "quatorze")
    if t > tq - .1:
        v = counter(0, 14400000, ease_out_cubic(prog(t, tq - .1, .9)))
        LBL(f"{v} €", "lm14m", font("title", 104), (255, 90, 80), None, stroke=6, stroke_fill=PAL["ink"]).draw(cv, fr, CX, 830, pop_in(t, tq - .1), -2)
    show(cv, fr, T6a, t, w(6, "dettes") - .05, None, 720, 990, 3)

def s6b(cv, fr, t):
    tl = w(6, "liquidé"); te = w(6, "envoyé") - .05; td = w(6, "division")
    stage_fill(cv, fr, (150, 170, 190), "lms6b")
    rain(cv, t, 40, (110, 120, 140))
    ARENA.draw(cv, fr, CX, 1150, 1.0, 0)
    floor_panel(cv, fr, CX, 640, "L2", t, True, 1.3, 1)
    if t > tl: grayscale(cv, prog(t, tl, .3)*.85)
    show_stamp(cv, fr, K6c, t, tl - .05, CX, 1150, -8)
    elevator_drop(cv, t, te, td - te)
    if t > td:
        shaft(cv, fr, t, 0, "lms6shaft")
        LM.draw(cv, fr, CX, 1720, 1.05, age=1, kit="lemans", mood="sad", t=t, look=(0, 1), tears=t - td)
        floor_panel(cv, fr, CX, 640, "D6", t, True, 1.8, 1)
        kw(cv, fr, K6d, t, td, None, CX, 930, 3)

def s6c(cv, fr, t):
    stage_fill(cv, fr, (150, 170, 190), "lms6c")
    ARENA.draw(cv, fr, CX, 1250, .95, 0)
    tm = w(6, "Moins")
    calendar(cv, fr, 280, 760, "2011", 1.0, -5, pop_in(t, tm + .1))
    calendar(cv, fr, 790, 760, "2013", 1.0, 5, pop_in(t, tm + .35))
    if t > tm + .5: arrow(ImageDraw.Draw(cv), (440, 760), (630, 760), prog(t, tm + .5, .3), PAL["ink"], 12, 4, 40, -.2)
    rain(cv, t, 50)
    grayscale(cv, .8)
    kw(cv, fr, K6e, t, tm - .05, None, CX, 430, -3)
    show(cv, fr, T6b, t, w(6, "l'inauguration") - .05, None, CX, 1000, 2)

def s6(cv, fr, t, T):
    shots(cv, fr, t, [(0, s6a), (w(6, "le") - .1, s6b), (w(6, "Moins") - .1, s6c)])
    impact(cv, t, w(6, "catastrophe"), 22); flashes(cv, t, w(6, "catastrophe"), .15, .8)
    impact(cv, t, w(6, "liquidé"), 20); impact(cv, t, w(6, "division") + .02, 24); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 7 — PAUSE : ton club de cœur ?
def s7(cv, fr, t, T):
    stage_fill(cv, fr, JAUNE, "lms7"); d = ImageDraw.Draw(cv)
    kw(cv, fr, K7a, t, .05, None, 760, 300, 4)
    tc = w(7, "cœur")
    kw(cv, fr, K7b, t, w(7, "club") - .05, None, 760, 560, -3)
    if t < tc + .3: HEART.draw(cv, fr, CX, 1060, (1 + .08*math.sin(t*10))*win(t, w(7, "Toi"), tc + .2), 0)
    for i in range(4):
        a = pop_in(t, tc + i*.1)
        if a <= 0: continue
        x = 180 + i*240; y = 1010 + 10*math.sin(t*4 + i)
        CARD.draw(cv, fr, x, y, a, (-4, 3, -2, 5)[i])
        HEART.draw(cv, fr, x, y - 40, .5*a, 0)
        NAMES7[i].draw(cv, fr, x, y + 80, a)
    te = w(7, "Écris")
    if t > te:
        a = pop_in(t, te)
        speech_bubble(cv, fr, "lmcta_b", typewriter("Allez les Verts !!", prog(t, te + .15, .7)) or " ", 500, 1300, a, (-1, 1), 60)
        bx = 880 + 18*math.sin(t*8)
        arrow(d, (740, 1320), (bx + 80, 1200), prog(t, te + .2, .3), PAL["ink"], 10, 7, 34, -.2)
    kw(cv, fr, K7c, t, w(7, "commentaire"), None, 540, 1470, 2)
    show(cv, fr, T7a, t, w(7, "prochain") - .1, w(7, "Allez") - .1, 740, 780, -2)
    kw(cv, fr, K7d, t, w(7, "Allez"), None, 740, 780, -5)
    impact(cv, t, w(7, "Allez"), 14)

def s7_post(cv, fr, t, T):
    a = pop_in(t, .25)
    if a <= 0: return
    d = ImageDraw.Draw(cv); cx, cy, s = 250, 470, a
    d.ellipse([cx-70*s, cy-70*s, cx+70*s, cy+70*s], fill=(34, 32, 36))
    for dx in (-22, 22): d.rectangle([cx+dx*s-12*s, cy-34*s, cx+dx*s+12*s, cy+34*s], fill=(250, 248, 240))

# ------------------------------------------------------------------ SCÈNE 8 — tout reconstruire : 6 défaites, champion, 3 montées
def s8a(cv, fr, t):
    stage_fill(cv, fr, (236, 226, 200), "lms8a")
    bricks(cv, t, .05, step=.05)
    LM.draw(cv, fr, CX, 1760, .9, age=1, kit="lemans", mood="determined", arms=(60, 60), t=t)
    kw(cv, fr, K8a, t, w(8, "reconstruire") - .1, None, CX, 430, -3)

def s8b(cv, fr, t):
    stage_fill(cv, fr, (44, 48, 60), "lms8b"); d = ImageDraw.Draw(cv)
    tsix, tch = w(8, "six"), w(8, "champion")
    show(cv, fr, T8a, t, w(8, "Le") - .05, None, CX, 400, -2)
    fade = 1 - .6*prog(t, tch - .1, .3)
    for k in range(6):
        a = pop_in(t, tsix + k*.1, .3)*fade
        if a <= .01: continue
        x = 190 + k*140
        LBL("D", "lmdef", font("title", 90), BLANC, ROUGE, padx=24, pady=4, rough=2).draw(cv, fr, x, 620, a, (-4, 3, -2, 5, -3, 4)[k])
    if t > tch - .15:
        rays(cv, (CX, 1050), t, prog(t, tch - .15, .3), 16, 1400, (240, 200, 90))
        trophy_lift(cv, fr, LM, CX, 1780, .8, "lemans", t)
        confetti(cv, fr, "lmc8", t - tch, 80, 3, [ROUGE, JAUNE, BLANC])
        show_stamp(cv, fr, K8b, t, tch, CX, 860, -4)
    else:
        LM.draw(cv, fr, CX, 1780, .8, age=1, kit="lemans", mood="sad" if t > tsix else "determined", t=t, look=(0, 1))

def s8c(cv, fr, t):
    stage_fill(cv, fr, (250, 214, 60), "lms8c"); d = ImageDraw.Draw(cv)
    tj = w(8, "trois") - .1
    tops = [1560 - k*170 for k in range(4)]
    for k in range(4):
        x0 = 90 + k*225
        d.rectangle([x0, tops[k], x0 + 225, STAGE[3] + 10], fill=(236, 236, 230) if k < 3 else ROUGE, outline=PAL["ink"], width=5)
        if k: LBL(("2017", "2018", "2019")[k-1], "lmyr", font("title", 56), PAL["ink"], None).draw(cv, fr, x0 + 112, tops[k] + 50, pop_in(t, tj + (k - 1)*.32 + .2), 0)
    LBL("LIGUE 2", "lml2", font("title", 46), BLANC, None).draw(cv, fr, 90 + 3*225 + 112, tops[3] + 150, 1, 0)
    k = 0 if t < tj else min(3, int((t - tj)/.32) + 1)
    uh = prog(t, tj + (k - 1)*.32, .3) if k else 1
    x = lerp(90 + (k - 1)*225 + 112, 90 + k*225 + 112, ease_io(uh)) if k else 90 + 112
    y = lerp(tops[k - 1], tops[k], uh) - 140*math.sin(uh*math.pi) if k else tops[0]
    LM.draw(cv, fr, x, y, .62, age=1, kit="lemans", mood="cheer" if k else "determined", arms=(150, 150) if k == 3 and uh >= 1 else (40, 40), t=t)
    show(cv, fr, T8b, t, w(8, "partir") - .1, None, CX, 600, 2)
    kw(cv, fr, K8c, t, tj + .05, None, CX, 430, -3)
    if k == 3 and uh >= 1: confetti(cv, fr, "lmc8c", t - tj - 1.0, 60, 3, [ROUGE, BLANC])

def s8(cv, fr, t, T):
    shots(cv, fr, t, [(0, s8a), (w(8, "Le") - .1, s8b), (w(8, "Puis") - .1, s8c)])
    impact(cv, t, w(8, "champion"), 18); flashes(cv, t, w(8, "champion"), .12, .6); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 9 — 2019 Ligue 2, le Covid, 5 ans en National
def s9a(cv, fr, t):
    stage_fill(cv, fr, ROUGE, "lms9a")
    rays(cv, (CX, 1000), t, 1.0, 16, 1500, (240, 120, 60))
    tl = w(9, "Ligue")
    LM.draw(cv, fr, CX, 1740, 1.05, age=1, kit="lemans", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
    kw(cv, fr, K9a, t, w(9, "dix-neuf") - .2, None, CX, 430, -3)
    show_stamp(cv, fr, K9b, t, tl - .05, CX, 640, 4)
    confetti(cv, fr, "lmc9", t - tl, 60, 3, [JAUNE, BLANC])

def s9b(cv, fr, t):
    stage_fill(cv, fr, (40, 54, 60), "lms9b")
    tcv, tar, tad, trd = w(9, "Covid"), w(9, "arrête"), w(9, "avant-dernier"), w(9, "redescend")
    for k in range(7):
        a = pop_in(t, w(9, "mais") + k*.12)
        virus(cv, (120, 930, 300, 820, 180, 940, 560)[k] + 20*math.sin(t*2 + k), (330, 360, 1450, 1420, 900, 960, 1520)[k] + 20*math.cos(t*2 + k),
              (60, 50, 44, 56, 40, 46, 38)[k], t + k, a)
    kw(cv, fr, K9c, t, tcv - .05, None, CX, 430, -3)
    show_stamp(cv, fr, K9d, t, tar - .05, CX, 620, -4)
    for i, (txt, hl_) in enumerate((("18e", False), ("19e  LE MANS", True), ("20e", False))):
        row(cv, fr, 880 + i*130, txt, hl_ and t > tad, pop_in(t, tad - .3 + i*.08), "lmrow9")
    if t > trd:
        d = ImageDraw.Draw(cv); arrow(d, (870, 950), (870, 1330), prog(t, trd, .3), (255, 90, 80), 14, 9, 44)
        show(cv, fr, T9a, t, trd + .1, None, CX, 1300, 2)

def s9c(cv, fr, t):
    stage_fill(cv, fr, (120, 120, 130), "lms9c")
    t0 = w(9, "Cinq") - .1
    yrs = ["2020", "2021", "2022", "2023", "2024"]
    n = (t - t0 - .2)/.25; k = int(n) if n >= 0 else -1
    if k < 0 or k >= 4: calendar(cv, fr, CX, 900, yrs[min(4, max(0, k))], 1.5, -3, 1)
    else:   # la page de l'année k s'arrache et tombe, l'année suivante apparaît dessous
        u = n - k
        calendar(cv, fr, CX, 900, yrs[k + 1], 1.5, -3, 1)
        calendar(cv, fr, CX + 400*u, 900 + 500*u*u, yrs[k], 1.5, -3 + 60*u, 1 - u)
    LM.draw(cv, fr, CX, 1760, .9, age=1, kit="lemans", mood="sad", t=t, look=(0, 1))
    kw(cv, fr, K9e, t, w(9, "National") - .15, None, CX, 430, -3)
    grayscale(cv, .5)

def s9(cv, fr, t, T):
    shots(cv, fr, t, [(0, s9a), (w(9, "mais") - .1, s9b), (w(9, "Cinq") - .1, s9c)])
    impact(cv, t, w(9, "arrête"), 20); glitch(cv, fr, t, w(9, "Covid"), .35, 14); impact(cv, t, w(9, "redescend"), 14); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 10 — investisseurs brésiliens : Djokovic, Courtois, Massa
def s10a(cv, fr, t):
    stage_fill(cv, fr, (0, 120, 70), "lms10a")
    rays(cv, (CX, 1000), t, .8, 16, 1500, (40, 160, 90))
    for k, x in enumerate((230, 850)): br_flag(cv, x, 1300 + 20*math.sin(t*3 + k), 300, 200, t + k, pop_in(t, .05 + k*.12), (-6, 6)[k])
    bill_rain(cv, fr, t, w(10, "arrive") - .1, 1.0, 12, "lmbills10")
    kw(cv, fr, K10a, t, w(10, "d'investisseurs") - .05, None, CX, 430, -3)
    show(cv, fr, T10a, t, w(10, "brésiliens") + .1, None, CX, 600, 2)
    kw(cv, fr, K10b, t, w(10, "stars") - .05, None, CX, 860, 3)
    if t > w(10, "stars"):
        for k in range(6):
            an = k*1.05 + t*2; draw_star(cv, CX + 330*math.cos(an), 860 + 160*math.sin(an), 26*(.5 + .5*math.sin(t*9 + k)), 1, t*3)

def s10b(cv, fr, t):
    stage_fill(cv, fr, (24, 26, 40), "lms10b")
    camera_flashes(cv, fr, "lmcf10", t % 1.6, 1.6, 8)
    tn, tc, tm = w(10, "Novak"), w(10, "Thibaut"), w(10, "l'ancien")
    kw(cv, fr, K10b, t, -1, None, CX, 330, -3)
    if t > tn - .1:
        a = pop_in(t, tn - .1, .35)
        DJOK.draw(cv, fr, 220, 1560, .66*a, age=1, kit="tennis", mood="happy", arms=(20, 140), t=t)
        hx, hy = hand_pos(220, 1560, .66*a, 1, 140); racket(cv, hx, hy, .66*a, -25)
        N10[0].draw(cv, fr, 230, 690, a, -4); S10[0].draw(cv, fr, 230, 780, a, -4)
    if t > tc - .1:
        a = pop_in(t, tc - .1, .35)
        COUR.draw(cv, fr, 510, 1560, .74*a, age=1, kit="gk", mood="happy", arms=(110, 110), t=t)
        for side in (-1, 1):
            hx, hy = hand_pos(510, 1560, .74*a, side, 110); glove(cv, hx, hy, .9*a)
        N10[1].draw(cv, fr, 510, 600, a, 3); S10[1].draw(cv, fr, 510, 690, a, 3)
    if t > tm - .1:
        a = pop_in(t, tm - .1, .35)
        MASS.draw(cv, fr, 810, 1560, .66*a, age=1, kit="pilote", mood="happy", arms=(20, 60), t=t)
        hx, hy = hand_pos(810, 1560, .66*a, -1, 20); helmet(cv, hx - 10, hy + 10, .8*a)
        N10[2].draw(cv, fr, 800, 690, a, 4); S10[2].draw(cv, fr, 780, 780, a, 4)

def s10c(cv, fr, t):
    stage_fill(cv, fr, (150, 200, 236), "lms10c")
    track(cv, 1080, 1320, t, 0)
    tf = w(10, "Formule", 2)
    car_pass(cv, fr, t, tf - .4, 1200, .9, .9, ROUGE, BLANC, "19")
    checkered(cv, 800, 820, 260, 170, t, 1, -6)
    MASS.draw(cv, fr, 260, 1760, .85, age=1, kit="pilote", mood="cheer" if t > w(10, "ça") else "happy", arms=(20, 150), t=t)
    kw(cv, fr, K10c, t, w(10, "pilote", 2) - .1, None, CX, 430, -3)
    show_stamp(cv, fr, K10d, t, w(10, "ça") - .05, CX, 640, 4)

def s10(cv, fr, t, T):
    shots(cv, fr, t, [(0, s10a), (w(10, "Novak") - .1, s10b), (w(10, "Un", 2) - .1, s10c)])
    for word in ("Novak", "Thibaut", "Felipe"): impact(cv, t, w(10, word), 12)
    impact(cv, t, w(10, "ça"), 14); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 11 — 2025 Ligue 2, 2026 : 2e, fumigènes à Bastia, Ligue 1 !
def s11a(cv, fr, t):
    stage_fill(cv, fr, (240, 230, 206), "lms11a")
    t26, t2e = w(11, "Deux", 2), w(11, "deuxième")
    kw(cv, fr, K11a, t, .05, t26 - .1, CX, 430, -3)
    show_stamp(cv, fr, K11b, t, w(11, "retour") - .05, CX, 640, 4, t_out=t26 - .1)
    kw(cv, fr, K11c, t, t26 - .05, None, CX, 430, 3)
    if t > t26:
        row(cv, fr, 700, "1. Troyes", False, pop_in(t, t26 + .2), "lmrow11")
        row(cv, fr, 840, "2. LE MANS", t > t2e, pop_in(t, t26 + .3), "lmrow11")
        show(cv, fr, T11a, t, t2e, None, 700, 970, 4)
    LM.draw(cv, fr, CX, 1760, .95, age=1, kit="lemans", mood="cheer" if t > t2e else "happy", arms=(150, 150) if t > t2e else (20, 20), t=t)

def s11b(cv, fr, t):
    stadium(cv, fr, "lms11stad", t, horizon=1060, pal=[(0, 90, 170), BLANC, (60, 120, 200), (200, 200, 210), (30, 40, 80)])
    tar, tfu = w(11, "arrêté"), w(11, "fumigènes")
    flares(cv, fr, "lmfl11", t, (60, 600, 1020, 980), 10, pop_in(t, tar - .5))
    score2(cv, fr, CX, 760, "BASTIA", "LE MANS", 0, 2, "arrêts de jeu", .55)
    whistle = tar - .05 < t < tar + .5
    REF.draw(cv, fr, CX, 1760, .95, age=1, kit="ref", mood="surprised" if t > tar else "normal", arms=(20, 160) if t > tar - .1 else (14, 14), t=t)
    show(cv, fr, T11b, t, w(11, "match") - .05, None, CX, 330, -2)
    show_stamp(cv, fr, K11d, t, tar - .05, CX, 500, -5)
    show(cv, fr, T11c, t, tfu - .05, None, CX, 990, 3)
    if whistle:
        d = ImageDraw.Draw(cv)
        for k in range(3):
            r = 40 + 60*k + 120*prog(t, tar, .5); d.arc([CX + 60 - r, 1060 - r, CX + 60 + r, 1060 + r], -60, 20, fill=BLANC, width=6)

def s11c(cv, fr, t):
    tv, tl = w(11, "valide"), w(11, "Ligue", 3)
    if t < tl - .1:
        stage_fill(cv, fr, (236, 226, 200), "lms11c")
        VERDICT.draw(cv, fr, CX, 1050, 1.05*pop_in(t, w(11, "mais") - .1), 3)
        show_stamp(cv, fr, K11e, t, tv - .05, CX, 1150, -8)
        LBL("13 mai 2026", "lm13mai", font("hand", 56), PAL["ink"], PAL["paper"], padx=20, pady=6).draw(cv, fr, CX, 520, pop_in(t, tv), -2)
    else:
        stage_fill(cv, fr, ROUGE, "lms11l1")
        rays(cv, (CX, 1000), t, 1.0, 16, 1500, JAUNE)
        for P, x, k in ((LM2, 250, 0), (LM, CX, 1), (LM2, 830, 2)):
            hop = 70*abs(math.sin(t*6 + k))
            P.draw(cv, fr, x, 1760 - hop, .82 if k != 1 else .95, age=1, kit="lemans", mood="cheer", arms=(150, 150), legs=(12, 12), t=t)
        kw(cv, fr, K11f, t, tl - .05, None, CX, 560, -3)
        show(cv, fr, T11d, t, tl + .3, None, CX, 780, 3)
        confetti(cv, fr, "lmc11", t - tl, 110, 4, [JAUNE, BLANC, (255, 150, 40)])
        camera_flashes(cv, fr, "lmcf11", t - tl, 1.4, 10)

def s11(cv, fr, t, T):
    shots(cv, fr, t, [(0, s11a), (w(11, "Le") - .1, s11b), (w(11, "mais") - .1, s11c)])
    impact(cv, t, w(11, "arrêté"), 20); impact(cv, t, w(11, "valide"), 16)
    impact(cv, t, w(11, "Ligue", 3), 24); flashes(cv, t, w(11, "Ligue", 3), .15, .8); drift(cv, t, T)

# ------------------------------------------------------------------ SCÈNE 12 — de la D6 à la L1 en 13 ans : maintien ? + demande ton club
def s12(cv, fr, t, T):
    sx0, sy0, sx1, sy1 = STAGE
    stage_fill(cv, fr, JAUNE, "lms12"); d = ImageDraw.Draw(cv)
    d.polygon([(sx0, sy0), (CX + 60, sy0), (CX - 60, sy1), (sx0, sy1)], fill=ROUGE)
    tl, t13, ttu, tc, tet = w(12, "Ligue"), w(12, "treize"), w(12, "Tu"), w(12, "commentaire"), w(12, "Et")
    ta, tdn, tab = w(12, "abonné"), w(12, "demande-nous"), w(12, "abonne-toi")
    a1 = win(t, .05, ttu - .1)
    floor_panel(cv, fr, 260, 560, "D6", t, True, 1.1, a1)
    floor_panel(cv, fr, 740, 560, "L1", t, False, 1.1, a1*pop_in(t, tl - .1, .3))
    if a1 > .5 and t > tl: arrow(d, (440, 560), (560, 560), prog(t, tl, .25), PAL["ink"], 12, 3, 40, -.3)
    if t < ttu: kw(cv, fr, K12a, t, t13 - .05, ttu - .1, CX, 820, -3)
    a2 = win(t, ttu - .05, tet - .1)
    if a2 > .01:
        K12b.draw(cv, fr, CX, 430, a2, -2)
        BTN_O.draw(cv, fr, 280, 640, a2*pop_in(t, w(12, "maintenir") - .1)*(1 + .05*math.sin(t*8)), -5)
        BTN_N.draw(cv, fr, 780, 640, a2*pop_in(t, w(12, "maintenir"))*(1 + .05*math.sin(t*8 + 1)), 5)
        if t > tc: arrow(d, (600, 1060), (960, 1180), prog(t, tc, .3)*a2, PAL["ink"], 12, 12, 40, .2)
    if t > tet:
        speech_bubble(cv, fr, "lmabo", typewriter("Fais Le Mans stp !!", prog(t, tet + .1, .8)) or " ", CX, 460, pop_in(t, tet), (0, 1), 60)
    show(cv, fr, T12a, t, ta - .05, tdn - .15, CX, 680, -2)
    kw(cv, fr, K12c, t, tdn - .05, None, CX, 700, 3)
    if t > tab:
        press = 1 - .12*math.sin(prog(t, tab + .5, .25)*math.pi)
        BTN_SUB.draw(cv, fr, CX, 920, pop_in(t, tab)*press, -2)
        confetti(cv, fr, "lmc12", t - tab, 80, 5, [ROUGE, JAUNE, BLANC])
    LM.draw(cv, fr, CX, 1780, .85, age=1, kit="lemans", mood="cheer" if t > tab else "happy",
            arms=(150, 150) if t > tab else ((150, 20) if int(t*2) % 2 else (20, 150)), t=t)
    impact(cv, t, tl, 12); impact(cv, t, tdn, 12); drift(cv, t, T)

# ------------------------------------------------------------------ scènes + bruitages
def SC(name, n, fn, sfx, trans=None, trans_dur=.3, pad_out=.3):
    return Scene(name, TEXTS[n-1], fn, sfx, pad_in=PAD, pad_out=pad_out, trans=trans, trans_dur=trans_dur)
W_ = w
SCENES = [
    SC("faillite", 1, s1, [(.0, "boom", .8), (.05, "riser", .4), (W_(1, "faillite"), "stamp"), (W_(1, "tombe") - .05, "elevator", .9),
                           (W_(1, "division"), "boom", .7), (W_(1, "Treize", 2) - .1, "whoosh_up", .7), (W_(1, "Treize", 2), "riser", .7),
                           (W_(1, "Ligue"), "crowd", .9), (W_(1, "Ligue"), "stamp", .6), (W_(1, "Et", 2) - .1, "whoosh", .5),
                           (W_(1, "Novak"), "gasp", .7), (W_(1, "Djokovic"), "tennis"), (W_(1, "Novak") + .1, "flash", .5),
                           (W_(1, "Voici") - .1, "whoosh", .5), (W_(1, "Mans"), "stamp"), (W_(1, "Mans") + .05, "crowd_long", .8)]),
    SC("fusion", 2, s2, [(.0, "boom", .6), (W_(2, "mille"), "stamp", .6), (.15, "pop"), (.35, "pop2"), (W_(2, "deux"), "pop"),
                         (W_(2, "fusion"), "swish"), (W_(2, "fusion") + .45, "stamp"), (W_(2, "fusion") + .45, "sparkle", .6),
                         (W_(2, "Ses") - .1, "whoosh", .5), (W_(2, "rouge"), "pop"), (W_(2, "jaune"), "pop2"), (W_(2, "Sang"), "stamp"),
                         (W_(2, "Sang") + .1, "crowd", .6), (W_(2, "Et", 3) - .1, "whoosh", .5), (W_(2, "Et", 3) + .2, "race", .8),
                         (W_(2, "vingt-quatre") + .1, "race", .9), (W_(2, "vingt-quatre") + .8, "race", .7), (W_(2, "monde"), "pop")],
       trans="punch", trans_dur=.35),
    SC("drogba", 3, s3, [(W_(3, "fin") - .1, "stamp", .6), (W_(3, "Ivoirien") - .1, "pop"), (W_(3, "Didier"), "stamp"),
                         (W_(3, "Il") - .1, "whoosh", .5), (W_(3, "signe"), "scribble", .7), (W_(3, "premier"), "stamp", .6),
                         (W_(3, "En") - .1, "whoosh", .5), (W_(3, "deux"), "stamp", .5), (W_(3, "Guingamp") - .15, "swish"),
                         (W_(3, "quatre-vingt", 2), "coin"), (W_(3, "Deux", 3) - .1, "whoosh", .6), (W_(3, "demi") - .1, "swish", .7),
                         (W_(3, "Chelsea") - .15, "swish"), (W_(3, "Chelsea"), "cash"), (W_(3, "Chelsea") + .1, "tick", .7),
                         (W_(3, "trois"), "stamp"), (W_(3, "trois"), "boom", .6), (W_(3, "paie"), "cash", .6)], trans="whip"),
    SC("ligue1", 4, s4, [(.0, "whistle", .5), (W_(4, "trois") - .1, "stamp", .6), (W_(4, "découvre"), "pop"), (W_(4, "Ligue"), "stamp"),
                         (W_(4, "Ligue"), "crowd_long", .9), (W_(4, "Et") - .1, "whoosh", .5), (W_(4, "devient"), "stamp", .6),
                         (W_(4, "Gervinho"), "pop"), (W_(4, "Gervinho"), "sparkle", .5), (W_(4, "Sessègnon"), "pop2"), (W_(4, "Sessègnon"), "sparkle", .5),
                         (W_(4, "Grafite"), "pop"), (W_(4, "Grafite"), "sparkle", .5), (W_(4, "explosent"), "boom", .7),
                         (W_(4, "partir"), "whoosh_up", .8), (W_(4, "partir") + .3, "pop2")], trans="tear_h", trans_dur=.6),
    SC("stade", 5, s5, [(W_(5, "dix") - .15, "stamp", .6), (W_(5, "redescend") - .05, "elevator", .8), (W_(5, "Ligue") + .1, "boom", .6),
                        (W_(5, "Ligue") + .1, "groan", .6), (W_(5, "Mais") - .1, "whoosh", .5), (W_(5, "Mais"), "boom", .6), (W_(5, "emménage") - .3, "pop"),
                        (W_(5, "neuf"), "sparkle"), (W_(5, "vingt-cinq"), "tick", .8), (W_(5, "circuit") + .05, "race"),
                        (W_(5, "vingt-quatre") + .65, "race", .8)], trans="whip"),
    SC("liquidation", 6, s6, [(.0, "boom", .7), (W_(6, "catastrophe"), "crash", .7), (W_(6, "catastrophe"), "flash", .6),
                              (W_(6, "En") - .05, "stamp", .5), (W_(6, "quatorze") - .1, "tick", .8), (W_(6, "dettes"), "groan", .6),
                              (W_(6, "le") - .1, "whoosh", .5), (W_(6, "liquidé"), "gavel"), (W_(6, "liquidé"), "stamp", .7),
                              (W_(6, "envoyé") - .05, "elevator", .9), (W_(6, "division"), "boom", .8), (W_(6, "Moins") - .1, "whoosh", .5),
                              (W_(6, "Moins") + .1, "pop"), (W_(6, "Moins") + .35, "pop2"), (W_(6, "l'inauguration"), "heart", .6)],
       trans="tear_d", trans_dur=.6),
    SC("pause", 7, s7, [(0, "scratch", 1.0, .9), (.3, "pop"), (W_(7, "club"), "stamp", .6), (W_(7, "cœur"), "heart", .6)] +
                       [(W_(7, "cœur") + i*.1, "notif", .6) for i in range(4)] +
                       [(W_(7, "Écris"), "notif"), (W_(7, "Écris") + .15, "scribble", .5), (W_(7, "commentaire"), "pop2"),
                        (W_(7, "prochain"), "pop"), (W_(7, "Allez"), "whoosh"), (W_(7, "Allez"), "boom", .5)], trans="polaroid", pad_out=.35),
    SC("reconstruction", 8, s8, [(.05, "thud", .6), (.35, "thud", .5), (.65, "thud", .5), (W_(8, "reconstruire"), "stamp", .6),
                                 (W_(8, "Le") - .1, "whoosh", .5)] + [(W_(8, "six") + k*.1, "pop", .7) for k in range(6)] +
                                [(W_(8, "défaites") + .2, "groan", .5), (W_(8, "champion") - .15, "sparkle"), (W_(8, "champion"), "stamp"),
                                 (W_(8, "champion"), "crowd", .9), (W_(8, "Puis") - .1, "whoosh", .5)] +
                                [(W_(8, "trois") - .1 + k*.32, "pop2", .8) for k in range(3)] + [(W_(8, "trois") + .9, "ding", .7)],
       trans="whip"),
    SC("covid", 9, s9, [(.0, "boom", .6), (W_(9, "dix-neuf") - .2, "stamp", .6), (W_(9, "Ligue"), "stamp"), (W_(9, "Ligue"), "crowd", .8),
                        (W_(9, "mais") - .1, "whoosh", .5)] + [(W_(9, "mais") + k*.12, "pop", .5) for k in range(0, 7, 2)] + [(W_(9, "Covid"), "glitch", .7, .4), (W_(9, "arrête"), "whistle", .6),
                        (W_(9, "arrête"), "stamp", .7), (W_(9, "avant-dernier"), "pop"), (W_(9, "redescend"), "groan", .6),
                        (W_(9, "Cinq") - .1, "whoosh", .5)] + [(W_(9, "Cinq") + .1 + k*.25, "paper", .7) for k in range(5)] +
                       [(W_(9, "National") - .15, "stamp", .6)], trans="tear_v", trans_dur=.6),
    SC("investisseurs", 10, s10, [(.0, "boom", .6), (.05, "samba", .7), (W_(10, "d'investisseurs"), "stamp", .5),
                                  (W_(10, "arrive"), "cash", .6), (W_(10, "stars"), "sparkle"), (W_(10, "Novak") - .1, "whoosh", .5),
                                  (W_(10, "Novak"), "tennis"), (W_(10, "Thibaut"), "pop"), (W_(10, "l'ancien"), "pop2"), (W_(10, "Felipe"), "flash", .5),
                                  (W_(10, "Un", 2) - .1, "whoosh", .5), (W_(10, "Formule", 2) + .05, "race"), (W_(10, "ça"), "stamp", .7),
                                  (W_(10, "ça") + .2, "laugh", .6)], trans="punch", trans_dur=.35),
    SC("montee", 11, s11, [(.05, "stamp", .6), (W_(11, "retour"), "stamp", .6), (W_(11, "Deux", 2), "stamp", .6),
                           (W_(11, "deuxième"), "pop"), (W_(11, "deuxième"), "crowd", .6), (W_(11, "Le") - .1, "whoosh", .5),
                           (W_(11, "Le"), "crowd_long", .7), (W_(11, "arrêté") - .05, "whistle", .8), (W_(11, "arrêté"), "stamp", .6),
                           (W_(11, "fumigènes"), "gasp", .6), (W_(11, "mais") - .1, "whoosh", .5), (W_(11, "valide"), "gavel"),
                           (W_(11, "valide"), "stamp", .6), (W_(11, "Ligue", 3) - .1, "boom"), (W_(11, "Ligue", 3), "crowd_long", 1.0),
                           (W_(11, "Ligue", 3), "horn", .5)], trans="whip"),
    SC("fin", 12, s12, [(.0, "boom", .6), (.1, "pop"), (W_(12, "Ligue"), "pop2"), (W_(12, "treize"), "stamp", .6),
                        (W_(12, "maintenir") - .1, "pop"), (W_(12, "maintenir"), "pop2"), (W_(12, "commentaire"), "notif"),
                        (W_(12, "Et"), "notif"), (W_(12, "Et") + .1, "scribble", .5), (W_(12, "abonné"), "pop"), (W_(12, "demande-nous"), "stamp", .6),
                        (W_(12, "abonne-toi"), "pop2"), (W_(12, "abonne-toi") + .5, "notif"), (W_(12, "abonne-toi") + .1, "crowd", .7),
                        (W_(12, "abonne-toi"), "sparkle")], trans="punch", trans_dur=.35, pad_out=1.3),
]
SCENES[6].trans_dur = 99      # la photo figée reste épinglée pendant toute la pause
SCENES[6].post = s7_post

# ------------------------------------------------------------------ couverture
def cover(path):
    cv = background(0, TITLE); stage_fill(cv, 0, (110, 24, 32), "lmcov"); d = ImageDraw.Draw(cv)
    rays(cv, (CX, 1150), 0.3, 1.0, 16, 1500, (170, 50, 50))
    Label("FAILLITE EN 2013…", "lmcv1", font("title", 108), PAL["ink"], PAL["mustard"], maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 300, 1, -3)
    Label("LIGUE 1 EN 2026 ?!", "lmcv2", font("title", 108), PAL["ink"], JAUNE, maxw=1040, padx=30, pady=10, rough=5).draw(cv, 0, CX, 470, 1, 2)
    floor_panel(cv, 0, 260, 680, "D6", 0, True, 1.15, 1)
    floor_panel(cv, 0, 760, 680, "L1", 0, False, 1.15, 1)
    arrow(d, (450, 680), (570, 680), 1, PAL["cream"], 14, 3, 44, -.3)
    for k in range(5): draw_star(cv, 760 + 210*math.cos(k*1.25), 680 + 140*math.sin(k*1.25), 22, 1, k)
    LM.draw(cv, 0, CX, 1630, 1.2, age=1, kit="lemans", mood="cheer", arms=(150, 150), legs=(14, 14), t=1)
    Label("L'HISTOIRE FOLLE DU MANS FC", "lmcv3", font("title", 64), PAL["cream"], ROUGE, padx=30, pady=12).draw(cv, 0, CX, 1690, 1, 1)
    finish(cv, TITLE); cv.convert("RGB").save(path, quality=94); return path

# ------------------------------------------------------------------ planches de contrôle (avec transitions)
def stills(out, fracs=(.05, .18, .32, .46, .6, .74, .88, .98), only=None):
    scene_timing(SCENES, VOICE); starts = np.cumsum([0]+[sc.T for sc in SCENES])
    os.makedirs(out, exist_ok=True); sheets = []
    for i, sc in enumerate(SCENES):
        if only and (i+1) not in only: continue
        prev = engine._last_frame(SCENES, i-1, starts, TITLE) if (i > 0 and sc.trans) else None
        ims = []
        for fr_ in fracs:
            t = fr_*sc.T; f = int((starts[i]+t)*FPS)
            cv = background(f, TITLE); sc.draw_fn(cv, f, t, sc.T)
            if prev is not None and t < sc.trans_dur: engine.TRANSITIONS[sc.trans](cv, prev, t, sc.trans_dur, i)
            if getattr(sc, "post", None): sc.post(cv, f, t, sc.T)
            finish(cv, TITLE); ims.append(cv.resize((300, 533)))
        sheet = Image.new("RGB", (300*len(ims), 575), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            sheet.paste(im, (k*300, 42)); dd.text((k*300+8, 6), f"S{i+1} {fracs[k]*sc.T:.1f}/{sc.T:.1f}", font=font("mono", 24), fill=(230, 230, 230))
        p = os.path.join(out, f"lm_sheet_s{i+1}.jpg"); sheet.save(p, quality=80); sheets.append(p)
    return sheets

if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else os.path.join(ROOT, "output", "lemans")
    os.makedirs(out, exist_ok=True)
    if "--cover" in args: print(cover(os.path.join(out, f"{SLUG}_couverture.jpg"))); sys.exit()
    if "--stills" in args:
        k = args.index("--stills"); only = [int(x) for x in args[k+1].split(",")] if len(args) > k+1 and not args[k+1].startswith("--") else None
        print(stills(os.environ.get("STILLS_DIR", "/tmp/lemans_stills"), only=only)); sys.exit()
    print(render_episode(SCENES, out, SLUG, TITLE, voice_files=VOICE, sfx_dir=SFX_DIR, sfx_db=6.0, lufs=-14.0, crf=25))
