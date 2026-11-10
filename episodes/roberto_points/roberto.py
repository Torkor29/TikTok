"""« Tu l'as vu 100 fois, ce coup franc de Roberto Carlos » — DA nuage de points (skill foot-nuage-de-points), ~50 s.
Formes 100 % géométriques (pictogrammes, terrain 3D, vue de haut, stade, cuve d'eau, spirale) : aucune photo de joueur.
Voix : Julien (voix/voix.mp3). Sans voix : minutage provisoire (aperçu muet).
  python3 episodes/roberto_points/roberto.py [--stills out.jpg] [--preview]"""
import sys, os, math, subprocess
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "engine"))
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import pts as P
from pts import W, H, FPS, ci, Shot
import karaoke as KA
TEXTE = ["Tu l'as vu cent fois, ce coup franc de Roberto Carlos.",
         "Trente-cinq mètres. Plus de cent trente kilomètres-heure.",
         "Mais le plus fou, c'est pas le but.",
         "Trois juin quatre-vingt-dix-sept, Lyon. France-Brésil.",
         "Il pose le ballon… prend un élan énorme… et frappe de l'extérieur du pied gauche.",
         "Le ballon part tellement à droite… qu'un ramasseur, à dix mètres du but, baisse la tête.",
         "Barthez ne bouge pas. Pour lui, c'est dehors.",
         "Et là… le ballon tourne. Il revient. Poteau rentrant.",
         "Treize ans plus tard, des physiciens français refont le tir… dans l'eau, avec des billes.",
         "Et ils trouvent un truc fou : un ballon qui tourne très vite ne fait pas une courbe. Il fait une spirale. Comme une coquille d'escargot.",
         "Plus il va loin, plus la courbe se resserre.",
         "De plus près, t'aurais vu une courbe banale. À trente-cinq mètres, t'as vu la spirale.",
         "Roberto Carlos, lui, visait… un panneau pub. Et il jure que c'est grâce au vent.",
         "Alors, génie ou coup de chance ? Dis-le en commentaire."]
KEYS = {"roberto", "carlos", "trente-cinq", "cent", "trente", "fou", "lyon", "france-bresil", "enorme", "frappe", "droite", "ramasseur",
        "barthez", "dehors", "tourne", "revient", "poteau", "rentrant", "treize", "physiciens", "eau", "billes", "spirale", "escargot",
        "resserre", "banale", "pub", "vent", "genie", "chance", "commentaire"}
VOIX = os.path.join(HERE, "voix", "voix.mp3"); PROV = not os.path.exists(VOIX)
WD = KA.Words(TEXTE, None if PROV else VOIX, cps=21.0, gap=.2)
def tw(i, w, n=1): return WD.t(i, w, n) - .08
TOTAL = WD.end + 1.0
G, CR, BL, PK, GR, RD, YE, DM = (ci(c) for c in ("gold", "cream", "blue", "pink", "green", "red", "yellow", "dim"))
# ------------------------------------------------------------------ formes
def ball_sphere(cx, cy, R, spin=.8, horns=False):
    phi = math.pi*(3 - math.sqrt(5)); ico = np.array([(0, 1, 1.618), (0, -1, 1.618), (0, 1, -1.618), (0, -1, -1.618), (1, 1.618, 0), (-1, 1.618, 0),
          (1, -1.618, 0), (-1, -1.618, 0), (1.618, 0, 1), (-1.618, 0, 1), (1.618, 0, -1), (-1.618, 0, -1)], np.float32); ico /= np.linalg.norm(ico[0])
    def gen(k, lt):
        i = np.arange(k) + .5; y = 1 - 2*i/k; r = np.sqrt(1 - y*y); th = phi*i; x, z = np.cos(th)*r, np.sin(th)*r
        V = np.stack([x, y, z], 1); near = (V @ ico.T).max(1); patch = near > .962
        a = lt*spin + 1.0; ca, sa = math.cos(a), math.sin(a); xr, zr = x*ca + z*sa, -x*sa + z*ca
        b = .35; yr, zr2 = y*math.cos(b) - zr*math.sin(b), y*math.sin(b) + zr*math.cos(b)
        front = zr2 > 0; shade = np.clip(.35 + .65*(xr*-.4 + yr*-.5 + zr2*.75), .1, 1)
        al = np.where(front, shade*1.15, .1)*np.where(patch, .22, 1.0); col = np.where(patch, DM, CR)
        return cx + xr*R, cy + yr*R, col, al
    parts = [(1.0, gen)]
    if horns:
        def hg(k, lt):
            g = np.random.default_rng(4); out = []
            for s in (-1, 1):
                u = np.linspace(0, 1, k//2); bx = cx + s*(R*.45 + u*R*.35 + np.sin(u*2.6)*R*.18); by = cy - R*.82 - u*R*.75 + (u**2)*R*.25
                th = (1 - u)*22 + 3; out.append((bx + g.normal(0, 1, k//2)*th*.5, by + g.normal(0, 1, k//2)*th*.5))
            x = np.concatenate([o[0] for o in out]); y = np.concatenate([o[1] for o in out]); m = k - len(x)
            if m > 0: x, y = np.concatenate([x, x[:m]]), np.concatenate([y, y[:m]])
            return x, y, PK, .9 + .1*math.sin(lt*7)
        parts.append((.12, hg))
    return parts
def galaxy(k, lt):
    g = np.random.default_rng(9); u = g.random(k); arm = g.integers(0, 3, k); r = 520*np.sqrt(u)
    a = arm*2*math.pi/3 + r*.012 + lt*.9 + g.normal(0, .25, k); return 540 + r*np.cos(a), 1060 + r*np.sin(a)*.8, np.where(g.random(k) < .2, G, CR), .4 + .6*(1 - u)
def counter(lt):
    v = int(round(130*P.ease(min(1.0, max(0.0, (lt - .1)/1.1)))))
    def gen(k, _lt): x, y = P.text_pts(f"{v}", 330, k, 540, 980, seed=3); return x, y, G, 1.0
    def unit(k, _lt): x, y = P.text_pts("km/h", 150, k, 540, 1240, fnt=P.SERIF); return x, y, CR, .9
    return [(1, gen), (.35, unit)]
# --- stade
def stadium(title, colors):
    def stands(k, lt):
        g = np.random.default_rng(12); row = g.integers(0, 14, k); a = g.random(k)*2*math.pi
        rx = 330 + row*16; ry = 150 + row*11; x = 540 + rx*np.cos(a); y = 1250 + ry*np.sin(a) - row*9
        tw_ = .45 + .55*np.abs(np.sin(lt*4 + g.random(k)*40)); return x, y, np.where(g.random(k) < .15, G, CR), tw_*(.5 + .5*(np.sin(a) > -2))
    def grass(k, lt):
        x, y = P.disc(0, 0, 1, k, 13); return 540 + x*300, 1250 + y*130, GR, .55
    def lights(k, lt):
        g = np.random.default_rng(14); c = g.integers(0, 4, k); px = np.array([170, 910, 110, 970])[c]; py = np.array([960, 960, 1500, 1500])[c]
        r = 26*np.sqrt(g.random(k)); a = g.random(k)*2*math.pi; return px + r*np.cos(a), py + r*np.sin(a), CR, 1.0
    parts = [(1.0, stands), (.35, grass), (.12, lights)]
    for (txt, px, y, cc, w) in title:
        parts.append((w, (lambda txt, px, y, cc: lambda k, lt: (*P.text_pts(txt, px, k, 540, y, seed=5), cc, 1.0))(txt, px, y, cc)))
    return parts
# --- terrain 3D (caméra derrière le tireur)
F3, HZ, CAMY, CAMZ, CAMX = 2000, 760, 2.2, 44.0, 3.0
def proj(X, Y, Z):
    d = np.maximum(CAMZ - np.asarray(Z, np.float32), .5); return 540 + F3*(np.asarray(X) - CAMX)/d, HZ + F3*(CAMY - np.asarray(Y))/d, d
BALL0 = (4.0, .11, 35.0)
def traj(s):
    s = np.asarray(s, np.float32); return 4 + 14*s - 14.4*s**3, .11 + 4.5*s*(1 - s) + 1.2*s, 35*(1 - s)
def pitch3d(kick_pose, kick_x, kick_z, flight=None):
    """flight(lt) -> s (0..1) avancée du ballon ou None."""
    def grass(k, lt):
        g = np.random.default_rng(21); X = g.uniform(-28, 30, k); Z = g.uniform(-3, 41, k); x, y, d = proj(X, 0*X, Z)
        stripe = (np.floor(Z/4) % 2 == 0); return x, y, GR, np.where(stripe, .45, .25)*np.clip(30/d, .4, 1)
    def lines(k, lt):
        segs = [((-20.16, 0), (20.16, 0)), ((-20.16, 0), (-20.16, 16.5)), ((20.16, 0), (20.16, 16.5)), ((-20.16, 16.5), (20.16, 16.5)),
                ((-9.16, 0), (-9.16, 5.5)), ((9.16, 0), (9.16, 5.5)), ((-9.16, 5.5), (9.16, 5.5))]
        kk = k//len(segs); X, Z = [], []
        for a, b in segs: u = np.linspace(0, 1, kk); X.append(a[0] + (b[0] - a[0])*u); Z.append(a[1] + (b[1] - a[1])*u)
        X, Z = np.concatenate(X), np.concatenate(Z); x, y, d = proj(X, 0*X, Z); m = k - len(x)
        return np.pad(x, (0, m), mode="edge"), np.pad(y, (0, m), mode="edge"), CR, .75
    def goal(k, lt):
        g = np.random.default_rng(22); n1 = k//3; u = np.linspace(0, 1, n1)
        X = np.concatenate([np.full(n1//3, -3.66), np.full(n1//3, 3.66), -3.66 + 7.32*u[:n1 - 2*(n1//3)]])
        Y = np.concatenate([2.44*u[:n1//3], 2.44*u[:n1//3], np.full(n1 - 2*(n1//3), 2.44)])
        Zp = np.zeros_like(X); xa, ya, _ = proj(X, Y, Zp)
        n2 = k - len(xa); NX = g.uniform(-3.66, 3.66, n2); NY = g.uniform(0, 2.44, n2); NZ = -1.8 + NY*.3
        NX = np.round(NX*4)/4 + g.normal(0, .02, n2) if True else NX
        xb, yb, _ = proj(NX, NY, NZ)
        return np.concatenate([xa, xb]), np.concatenate([ya, yb]), np.r_[np.full(len(xa), CR), np.full(n2, DM)], np.r_[np.full(len(xa), 1.0), np.full(n2, .4)]
    def people(k, lt):
        figs = [("wall", X, 25.85) for X in (1.0, 1.65, 2.3, 2.95)] + [("keeper", -.4, .6)]
        kx, kz = kick_x(lt), kick_z(lt); figs.append((kick_pose(lt), kx, kz))
        hs = [F3*1.85/(CAMZ - Z) for (_, _, Z) in figs]; wsum = sum(h*h for h in hs); xs, ys = [], []; used = 0
        for j, ((po, X, Z), h) in enumerate(zip(figs, hs)):
            kk = int(k*h*h/wsum) if j < len(figs) - 1 else k - used; used += kk
            sx, sy, d = proj(X, 0, Z); x, y = P.figure(po, kk, float(sx), float(sy), float(h), seed=30 + j); xs.append(x); ys.append(y)
        return np.concatenate(xs), np.concatenate(ys), CR, .95
    def ballp(k, lt):
        s = flight(lt) if flight else 0.0
        if s is None: s = 0.0
        if s <= 0:
            bx, by, d = proj(BALL0[0], BALL0[1], BALL0[2]); r = F3*.11/d; x, y = P.disc(float(bx), float(by), float(r), k, 50); return x, y, G, 1.0
        nb = k//3; ss = np.linspace(0, s, k - nb); X, Y, Z = traj(ss); x, y, d = proj(X, Y, Z)       # traînée dorée
        X1, Y1, Z1 = traj(s); bx, by, d1 = proj(X1, Y1, Z1); r = max(6.0, float(F3*.11/d1)); xb, yb = P.disc(float(bx), float(by), r, nb, 51)
        return np.concatenate([x, xb]), np.concatenate([y, yb]), G, np.r_[np.linspace(.15, 1, k - nb), np.ones(nb)]
    return [(.8, grass), (.3, lines), (.3, goal), (1.1, people), (.14, ballp)]
# --- vue de haut
def top_xy(X, Z): return 540 + (np.asarray(X) - 3.0)*30, 560 + np.asarray(Z)*30
def toppitch(s_fn, boy_pose="stand", dashed=False, extra=None, show_kicker=True):
    def grass(k, lt):
        g = np.random.default_rng(61); X = g.uniform(-19, 23, k); Z = g.uniform(-4, 40, k); x, y = top_xy(X, Z)
        return x, y, GR, np.where(np.floor(Z/4) % 2 == 0, .3, .17)
    def lines(k, lt):
        segs = [((-20.16, 0), (20.16, 0)), ((-20.16, 0), (-20.16, 16.5)), ((20.16, 0), (20.16, 16.5)), ((-20.16, 16.5), (20.16, 16.5)),
                ((-9.16, 0), (-9.16, 5.5)), ((9.16, 0), (9.16, 5.5)), ((-9.16, 5.5), (9.16, 5.5)), ((-3.66, 0), (-3.66, -2)), ((3.66, 0), (3.66, -2)), ((-3.66, -2), (3.66, -2))]
        pts = [top_xy(*zip(a, b)) for a, b in segs]; pts = [((p[0][0], p[1][0]), (p[0][1], p[1][1])) for p in pts]
        x, y = P.poly([pp for ab in pts for pp in ab], k) if False else (np.concatenate([P.seg(a, b, k//len(pts))[0] for a, b in pts]), np.concatenate([P.seg(a, b, k//len(pts))[1] for a, b in pts]))
        m = k - len(x); return np.pad(x, (0, m), mode="edge"), np.pad(y, (0, m), mode="edge"), CR, .8
    def people(k, lt):
        kk = k//7; xs, ys, cs = [], [], []
        figs = [("wall", X, 25.85, CR) for X in (1.0, 1.65, 2.3, 2.95)] + [("keeper", -.4, .8, YE if False else CR), (boy_pose if isinstance(boy_pose, str) else boy_pose(lt), 12.5, -2.0, RD)]
        if show_kicker: figs.append(("kick", 3.2, 36.2, CR))
        for j, (po, X, Z, c) in enumerate(figs):
            sx, sy = top_xy(X, Z); x, y = P.figure(po, kk, float(sx), float(sy) + 24, 96, seed=70 + j); xs.append(x); ys.append(y); cs.append(np.full(kk, c))
        x, y, c = np.concatenate(xs), np.concatenate(ys), np.concatenate(cs); m = k - len(x)
        return np.pad(x, (0, m), mode="edge"), np.pad(y, (0, m), mode="edge"), np.pad(c, (0, m), mode="edge"), .95
    def trail(k, lt):
        s = s_fn(lt); nb = k//4
        ss = np.linspace(0, max(s, 1e-3), k - nb); X, _, Z = traj(ss); x, y = top_xy(X, Z)
        X1, _, Z1 = traj(s); bx, by = top_xy(X1, Z1); xb, yb = P.disc(float(bx), float(by), 11, nb, 62)
        return np.concatenate([x, xb]), np.concatenate([y, yb]), G, np.r_[np.linspace(.2, 1, k - nb), np.ones(nb)]
    parts = [(1.0, grass), (.4, lines), (.45, people), (.25, trail)]
    if dashed:
        def dash(k, lt):
            a = top_xy(*BALL0[::2]); b = top_xy(12.5, -1.0); x, y = P.seg(a, b, k); u = np.linspace(0, 1, k)
            return x, y, RD, np.where((u*18 + lt*2) % 1 < .5, .8, 0.0)*min(1, lt*2)
        parts.append((.08, dash))
    if extra: parts += extra
    return parts
# --- but de face (poteau rentrant)
def goal_front():
    def frame_(k, lt):
        x, y = P.poly([(150, 1500), (150, 900), (930, 900), (930, 1500)], k); return x, y, CR, 1.0
    def net(k, lt):
        g = np.random.default_rng(81); gx = np.round(g.uniform(0, 1, k)*26)/26; gy = g.uniform(0, 1, k)
        sw = np.r_[np.zeros(k//2, bool), np.ones(k - k//2, bool)]; gx, gy = np.where(sw, g.uniform(0, 1, k), gx), np.where(sw, np.round(g.uniform(0, 1, k)*20)/20, gy)
        x = 160 + gx*760; y = 910 + gy*580
        ix, iy = 860, 1010; d = np.hypot(x - ix, (y - iy)*1.2); imp = max(0.0, lt - .25)
        amp = 90*math.exp(-imp*3.2)*math.cos(imp*14) if lt > .25 else 0; bulge = amp*np.exp(-(d/170)**2)
        return x - bulge*.3, y + bulge*.15, DM, .55 + .4*np.exp(-(d/170)**2)*(lt > .25)
    def ballg(k, lt):
        u = min(1.0, lt/.25); bx, by = 1150 - 290*u, 760 + 250*u; x, y = P.disc(bx, by, 34 + 10*(1 - u), k, 82); return x, y, G, 1.0
    def confetti(k, lt):
        g = np.random.default_rng(83); a = g.random(k)*2*math.pi; v = g.uniform(200, 1100, k); tt = max(0.0, lt - .25)
        x = 860 + np.cos(a)*v*tt; y = 1010 + np.sin(a)*v*tt + 600*tt*tt; c = g.choice([G, CR, BL, YE], k); return x, y, c, (lt > .25)*np.clip(1.3 - tt*.6, 0, 1)
    def crowd(k, lt):
        g = np.random.default_rng(84); x = g.uniform(-40, 1120, k); row = g.integers(0, 9, k); y = 560 + row*32 + g.normal(0, 3, k)
        return x, y, np.where(g.random(k) < .3, YE, CR), np.where(g.random(k) < .35, 1, .15)*(.3 + .7*np.abs(np.sin(lt*7 + g.random(k)*30)))*(.6 + .6*(lt > .25))
    return [(.25, frame_), (.8, net), (.06, ballg), (.4, confetti), (.25, crowd)]
# --- cuve d'eau + billes
def tank():
    def box(k, lt): x, y = P.poly([(170, 760), (170, 1600), (910, 1600), (910, 760)], k); return x, y, CR, .9
    def water(k, lt):
        g = np.random.default_rng(91); x = g.uniform(180, 900, k); y0 = g.uniform(840, 1590, k); y = y0 + 8*np.sin(x*.02 + lt*3 + y0*.01)
        return x, y, BL, .3 + .3*np.sin(x*.05 + lt*2)**2
    def balls(k, lt):
        xs, ys = [], []; kk = k//3
        for j in range(3):
            u = ((lt*.45 + j*.33) % 1.0); th = u*9; r = 200*np.exp(-.18*th); cx0, cy0 = 260 + u*380, 1180 + j*40
            bx, by = cx0 + r*np.cos(th)*.4 + u*200, cy0 + r*np.sin(th)*.6; x, y = P.disc(bx, by, 16, kk, 92 + j); xs.append(x); ys.append(y)
        x, y = np.concatenate(xs), np.concatenate(ys); m = k - len(x); return np.pad(x, (0, m), mode="edge"), np.pad(y, (0, m), mode="edge"), G, 1.0
    def year(k, lt): x, y = P.text_pts("2010", 170, k, 540, 600, seed=93); return x, y, G, 1.0
    return [(.25, box), (1.0, water), (.1, balls), (.25, year)]
# --- spirale
def spiral(prog=None, shell=False):
    def curve(k, lt):
        pmax = prog(lt) if prog else 1.0; th = np.linspace(0, 7.5*pmax, k); r = 520*np.exp(-.26*th)
        x, y = 540 + r*np.cos(th + math.pi), 1080 + r*np.sin(th + math.pi)*.95
        if shell:
            g = np.random.default_rng(101); wdt = r*.42*g.random(k); x = x - np.cos(th + math.pi)*wdt; y = y - np.sin(th + math.pi)*wdt*.95
            return x, y, np.where(g.random(k) < .25, G, CR), .35 + .5*(wdt/(r*.42 + 1e-3))
        return x, y, G, .9
    parts = [(1.0, curve)]
    if prog:
        def ballp(k, lt):
            th = 7.5*prog(lt); r = 520*math.exp(-.26*th); x, y = P.disc(540 + r*math.cos(th + math.pi), 1080 + r*math.sin(th + math.pi)*.95, 22, k, 102); return x, y, CR, 1.0
        parts.append((.05, ballp))
    if shell:
        def sept(k, lt):
            xs, ys = [], []; kk = k//14
            for j in range(14):
                th = j*.5; r = 520*math.exp(-.26*th); a = th + math.pi; xs.append(np.linspace(540 + r*math.cos(a), 540 + r*.58*math.cos(a), kk)); ys.append(np.linspace(1080 + r*math.sin(a)*.95, 1080 + r*.58*math.sin(a)*.95, kk))
            x, y = np.concatenate(xs), np.concatenate(ys); m = k - len(x); return np.pad(x, (0, m), mode="edge"), np.pad(y, (0, m), mode="edge"), G, .9
        parts.append((.2, sept))
    return parts
def compare():
    def tr(k, lt):
        u = min(1.0, lt/1.4); kk = k//3
        s = np.linspace(0, u, kk); X = -10 + 4 + 8*s - 1.0*s**3; Z = 20*(1 - s)                          # de près : la courbe n'a pas le temps de revenir
        x1, y1 = top_xy(X, Z)
        s2 = np.linspace(0, u, k - kk); X2, _, Z2 = traj(s2); x2, y2 = top_xy(X2 + 7, Z2)
        return np.r_[x1, x2], np.r_[y1, y2], np.r_[np.full(kk, CR), np.full(k - kk, G)], np.r_[np.full(kk, .7), np.ones(k - kk)]
    def labels(k, lt):
        kk = k//2; a = P.text_pts("20 m", 76, kk, 200, 1270, fnt=P.SERIF, seed=111); b = P.text_pts("35 m", 76, k - kk, 690, 1720, fnt=P.SERIF, seed=112)
        return np.r_[a[0], b[0]], np.r_[a[1], b[1]], np.r_[np.full(kk, CR), np.full(k - kk, G)], 1.0
    def gl(k, lt):
        x, y = P.seg((20, 560), (1060, 560), k); return x, y, CR, .7
    def goals(k, lt):
        kk = k//2; a = P.poly([top_xy(-10 - 3.66, 0), top_xy(-10 - 3.66, -2), top_xy(-10 + 3.66, -2), top_xy(-10 + 3.66, 0)], kk); b = P.poly([top_xy(7 - 3.66, 0), top_xy(7 - 3.66, -2), top_xy(7 + 3.66, -2), top_xy(7 + 3.66, 0)], k - kk)
        return np.r_[a[0], b[0]], np.r_[a[1], b[1]], CR, .9
    return [(1.0, tr), (.35, labels), (.2, gl), (.2, goals)]
def billboard():
    def board(k, lt): x, y = P.poly([(140, 640), (940, 640), (940, 900), (140, 900)], k, closed=True); return x, y, CR, .9
    def pub(k, lt): x, y = P.text_pts("PUB", 190, k, 540, 770, seed=121); return x, y, BL, 1.0
    def kicker(k, lt): x, y = P.figure("kick", k, 400, 1720, 640, seed=122); return x, y, CR, .95
    def aim(k, lt):
        x, y = P.seg((560, 1640), (560, 920), k); u = np.linspace(0, 1, k); return x, y, G, np.where((u*14 - lt*2) % 1 < .5, .9, 0)
    return [(.3, board), (.4, pub), (.8, kicker), (.08, aim)]
def wind():
    def flow(k, lt):
        g = np.random.default_rng(131); ln = g.integers(0, 34, k); y0 = 620 + ln*30.0; ph = g.random(k)
        x = ((ph*.35 + lt*.45 + ln*.137) % 1.0)*1500 - 210; y = y0 + 45*np.sin(x*.006 + ln*.7)
        seg_ = (ph < .35); return x, y, np.where(ln % 5 == 0, G, CR), np.where(seg_, .9*np.sin(ph/.35*math.pi), 0.0)
    def ballw(k, lt):
        bx = 300 + 420*min(1, lt/2.0); by = 1100 - 160*math.sin(min(1, lt/2.0)*math.pi); x, y = P.disc(bx, by, 40, k, 132); return x, y, G, 1.0
    return [(1.0, flow), (.06, ballw)]
def words2(a, ca, b=None, cb=None):
    def g1(k, lt): x, y = P.text_pts(a, 280, k, 540, 980, seed=141); return x, y, ca, 1.0
    parts = [(1.0, g1)]
    if b:
        def g2(k, lt): x, y = P.text_pts(b, 160, k, 540, 1280, seed=142); return x, y, cb, 1.0
        parts.append((.8, g2))
    return parts
# ------------------------------------------------------------------ storyboard
def run_kicker():
    """Pose et position du tireur sur le terrain 3D : posé -> recule (élan) -> court -> frappe."""
    te, tf = tw(4, "élan") - tw(4, "pose"), tw(4, "frappe") - tw(4, "pose")
    def z(lt):
        if lt < te: return 36.3
        if lt < te + .9: return 36.3 + 2.0*P.ease((lt - te)/.9)
        u = min(1.0, (lt - te - .9)/max(.2, tf - te - .9)); return 38.3 - 2.7*P.ease(u)
    def x(lt): return 3.3 if lt < te else 3.3 - .5*math.sin(min(1, (lt - te)/(tf - te))*math.pi) + .2*min(1, max(0, (lt - tf + .4)/.4))
    def pose(lt):
        if lt >= tf - .05: return "kick"
        if lt > te + .9: return P.lerp_pose("run", "stand", .5 + .5*math.sin(lt*14))
        return "stand"
    return pose, x, z
def build():
    S = []
    def add(t0, parts, **kw): S.append(Shot(t0, parts, **kw))
    add(0.0, ball_sphere(540, 1080, 360, horns=True), glitch=.6)
    add(tw(0, "roberto"), [(1.0, lambda k, lt: (*P.figure("kick", k, 520, 1640, 1100, seed=7), CR, .95)), (.05, lambda k, lt: (*P.disc(800, 1450, 50, k, 8), G, 1.0))])
    add(tw(1, "trente"), [(1.0, lambda k, lt: (*P.text_pts("35", 560, k, 500, 1020, seed=9), G, 1.0)), (.25, lambda k, lt: (*P.text_pts("m", 300, k, 870, 1130, fnt=P.SERIF, seed=10), CR, 1.0))])
    add(tw(1, "plus"), counter(0) if False else [(1.0, lambda k, lt: counter(lt)[0][1](k, lt)), (.35, lambda k, lt: counter(lt)[1][1](k, lt))])
    add(tw(2, "mais"), [(1.0, galaxy)], glitch=.8)
    add(tw(3, "trois"), stadium([("3 JUIN 1997", 150, 680, G, .3)], None))
    add(tw(3, "france"), stadium([("FRANCE", 130, 610, BL, .2), ("BRÉSIL", 130, 760, YE, .2)], None), cont=True)
    pose, kx, kz = run_kicker(); tf = tw(4, "frappe") - tw(4, "pose")
    add(tw(4, "pose"), pitch3d(pose, kx, kz, flight=lambda lt: max(0.0, min(.45, (lt - tf - .1)/2.2))))
    t5 = tw(5, "le"); s5 = lambda lt: min(.55, .2 + lt*.16)
    add(t5, toppitch(s5, dashed=True))
    tb = tw(5, "baisse") - t5
    S[-1].parts = toppitch(s5, boy_pose=lambda lt: P.lerp_pose("stand", "duck", min(1, max(0, (lt - tb)/.3))), dashed=True)
    add(tw(6, "barthez"), [(1.0, lambda k, lt: (*P.figure("keeper", k, 540, 1700, 1050, seed=11), CR, .95)),
                           (.2, lambda k, lt: (*P.text_pts("BARTHEZ", 130, k, 540, 560, seed=12), BL, 1.0))])
    t7 = tw(7, "et"); tp = tw(7, "poteau")
    add(t7, toppitch(lambda lt: min(1.0, .55 + .45*P.ease(min(1, lt/max(.4, tp - t7)))), boy_pose="duck"))
    add(tp, goal_front(), glitch=.7)
    add(tw(8, "treize"), [(1.0, lambda k, lt: (*P.text_pts("+13 ANS", 260, k, 540, 1060, seed=13), G, 1.0))])
    add(tw(8, "physiciens"), tank())
    add(tw(9, "courbe"), toppitch(lambda lt: min(1.0, lt/1.6), show_kicker=False))
    add(tw(9, "spirale"), spiral(prog=lambda lt: min(1.0, .2 + lt/1.4)))
    add(tw(9, "coquille"), spiral(shell=True))
    add(tw(10, "plus"), spiral(prog=lambda lt: (lt*.45) % 1.0))
    add(tw(11, "de"), compare())
    add(tw(12, "roberto"), billboard())
    add(tw(12, "vent"), wind())
    add(tw(13, "génie"), words2("GÉNIE", G))
    add(tw(13, "chance"), words2("GÉNIE", DM, "OU CHANCE ?", BL), cont=True)
    add(tw(13, "dis"), ball_sphere(540, 1080, 360, horns=True), glitch=.5)
    for a, b in zip(S, S[1:]): a.t1 = b.t0
    S[-1].t1 = TOTAL
    return S
SHOTS = build()
# ------------------------------------------------------------------ sous-titres (Anton crème en haut, mots-clés or, mots non dits à 32 %)
FA = ImageFont.truetype(os.path.join(ROOT, "assets", "fonts", "Anton-Regular.ttf"), 76)
_fz = {}
def fa(sz):
    if sz not in _fz: _fz[sz] = ImageFont.truetype(os.path.join(ROOT, "assets", "fonts", "Anton-Regular.ttf"), sz)
    return _fz[sz]
CH = WD.chunks(4)
def subtitle(img, t):
    cur = [c for c in CH if c[0] - .02 <= t < c[1]]
    if not cur: return img
    t0, t1, toks = cur[-1]; im = Image.fromarray(img).convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    words = [tk[1].upper().strip(".,;:!?…") for tk in toks]; ws = [fa(76).getlength(w) for w in words]; gap = 22; tot = sum(ws) + gap*(len(ws) - 1)
    sc = min(1.0, 980/tot); x = W/2 - tot*sc/2
    for tk, w, wd in zip(toks, words, ws):
        said = tk[3] <= t; key = KA.norm(tk[1]) in KEYS or any(KA.norm(p) in KEYS for p in tk[1].split("'"))
        col = (232, 182, 90) if key else (243, 236, 220); a = 255 if said else 82
        pop = 1 + .16*math.exp(-(t - tk[3])*13) if said else 1.0; f = fa(max(10, int(76*sc*pop)))
        d.text((x + wd*sc/2, 330), w, font=f, fill=col + (a,), anchor="mm", stroke_width=4, stroke_fill=(5, 6, 14, int(a*.8)))
        x += (wd + gap)*sc
    im.alpha_composite(ov); return np.asarray(im.convert("RGB"))
def frame(fr):
    t = fr/FPS; starts = [s.t0 for s in SHOTS]
    last = max([s for s in starts if s <= t], default=0); beat = math.exp(-6.5*(t - last))
    img, st = P.render(SHOTS, t, beat); s, lt = st[4], st[5]
    if not s.cont and lt < .5 and s.t0 > 0:                       # anneau doré qui s'ouvre à chaque nouveau plan
        ov = img.copy(); r = int(80 + 1400*lt); cv2.circle(ov, (P.CX, P.CY), r, (232, 182, 90), 3, cv2.LINE_AA); a = .5*(1 - lt/.5); img = cv2.addWeighted(ov, a, img, 1 - a, 0)
    if s.glitch and lt < .22: img = P.glitch(img, s.glitch*(1 - lt/.22), fr)
    if t < .25 and fr % 3 == 0: img = P.glitch(img, .3, fr)
    return subtitle(img, t).tobytes()
def stills(path, ts=None, w=270):
    ts = ts or [s.t0 + min(.9, (s.t1 - s.t0)*.7) for s in SHOTS]; cols = 7; h = int(w*H/W)
    sh = Image.new("RGB", (w*cols, h*math.ceil(len(ts)/cols)))
    for j, t in enumerate(ts): sh.paste(Image.frombytes("RGB", (W, H), frame(int(t*FPS))).resize((w, h)), ((j % cols)*w, (j//cols)*h))
    sh.save(path, quality=88); print(path, len(ts), "plans", round(TOTAL, 1), "s")
def render(out):
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-maxrate", "16M", "-bufsize", "32M", out], stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for b in pool.imap(frame, range(int(TOTAL*FPS)), chunksize=4): pr.stdin.write(b)
    pr.stdin.close(); pr.wait(); print(out)
if __name__ == "__main__":
    if "--stills" in sys.argv: stills(sys.argv[sys.argv.index("--stills") + 1])
    elif "--preview" in sys.argv:
        os.makedirs(os.path.join(ROOT, "output", "roberto_points"), exist_ok=True); render(os.path.join(ROOT, "output", "roberto_points", "apercu_muet_provisoire.mp4"))
