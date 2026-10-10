"""Les principes d'animation de John Lasseter (« Principles of Traditional Animation Applied to 3D Computer Animation »,
SIGGRAPH 1987), traduits en outils pour le moteur papier. À utiliser à la place des pop/slam « tout ou rien » :

 1. Squash & stretch (écrasement / étirement) : squash() à l'impact, stretch dans la direction du mouvement rapide ;
    le volume est conservé (sx * sy ≈ 1).
 2. Timing : durées courtes = léger / rapide, longues = lourd ; les tampons claquent en 0,10 s, les gros objets en 0,3-0,5 s.
 3. Anticipation : petit mouvement inverse avant l'action (recul / tassement avant un saut, montée avant le claquement).
 4. Staging (mise en scène) : une seule idée lisible à la fois ; le reste s'atténue (dim()) ou sort du cadre.
 5. Follow-through & overlapping action : l'objet dépasse sa pose puis revient (settle) ; les éléments d'un groupe
    arrivent décalés (stagger) et ne s'arrêtent pas en même temps.
 6. Straight ahead / pose-to-pose : on anime de pose clé en pose clé (keys()) avec des interpolations douces.
 7. Slow in & slow out : départs et arrivées amortis (ease()) ; jamais de vitesse constante sauf effet voulu.
 8. Arcs : les trajectoires sont courbes (arc()) et non en ligne droite.
 9. Exaggeration : poses et déformations poussées (amplitudes généreuses : 1.25 en dépassement, 0.75 en écrasement).
10. Secondary action : mouvements causés par l'action principale (poussière à l'impact, écharpe qui flotte, ondulation).
11. Appeal : formes simples et lisibles, rythme agréable ; pas de clignotements ni de tremblements gratuits.
"""
import math
from engine import blit, blit_sxy, boil, jit, clamp, lerp, prog

# ------------------------------------------------------------------ 7. slow in / slow out
def ease(u):
    u = clamp(u, 0, 1); return u*u*(3 - 2*u)
def ease_out(u):
    u = clamp(u, 0, 1); return 1 - (1 - u)**3
def ease_in(u):
    u = clamp(u, 0, 1); return u**3

# ------------------------------------------------------------------ 5. follow-through : dépassement amorti
def settle(t, t0, amp=.22, freq=2.6, damp=5.5):
    """Oscillation amortie après t0 : 0 avant, puis amp*... qui revient vers 0 (dépassement + retour)."""
    if t < t0: return 0.0
    x = t - t0; return amp*math.exp(-damp*x)*math.sin(2*math.pi*freq*x)

def stagger(i, step=.07):
    """5. overlapping action : décalage d'entrée de l'élément i d'un groupe."""
    return i*step

# ------------------------------------------------------------------ 8. arcs
def arc(p0, p1, u, h=-180):
    """Point sur une trajectoire courbe de p0 à p1 (h < 0 : la courbe passe au-dessus)."""
    u = clamp(u, 0, 1); mx, my = (p0[0] + p1[0])/2, (p0[1] + p1[1])/2 + h
    a, b, c = (1 - u)**2, 2*(1 - u)*u, u*u
    return a*p0[0] + b*mx + c*p1[0], a*p0[1] + b*my + c*p1[1]

# ------------------------------------------------------------------ 6. pose à pose
def keys(t, ks):
    """ks = [(temps, valeur), …] ; interpolation slow-in/slow-out entre poses clés (valeurs scalaires ou tuples)."""
    if t <= ks[0][0]: return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t <= t1:
            u = ease((t - t0)/max(1e-6, t1 - t0))
            return tuple(lerp(a, b, u) for a, b in zip(v0, v1)) if isinstance(v0, tuple) else lerp(v0, v1, u)
    return ks[-1][1]

# ------------------------------------------------------------------ 1. squash & stretch
def squash(t, t0, amt=.28, d=.45):
    """Écrasement à l'impact (t0), volume conservé, puis rebond amorti : renvoie (sx, sy)."""
    if t < t0: return 1.0, 1.0
    s = -amt*math.exp(-6*(t - t0))*math.cos(2*math.pi*2.2*(t - t0)) if t - t0 < d*2.5 else 0.0
    sy = 1 + s; return 1/max(.3, sy), sy

# ------------------------------------------------------------------ composés prêts à l'emploi
def _sprite(lab, fr):
    v = getattr(lab, "v", None)
    return (v[boil(fr)] if isinstance(v, list) else v) if v is not None else lab

def draw_sxy(cv, fr, lab, x, y, sx, sy, rot=0.0, alpha=1.0, amp=1.0):
    """Dessine un Label / Paper / sprite avec une échelle X/Y séparée (squash & stretch), boil compris."""
    if sx <= .02 or sy <= .02 or alpha <= .01: return
    jx, jy = jit(getattr(lab, "key", "x"), boil(fr), amp) if hasattr(lab, "key") else (0, 0)
    blit_sxy(cv, _sprite(lab, fr), x + jx, y + jy, sx, sy, rot, alpha)

def enter(cv, fr, lab, t, t0, x, y, rot=0.0, frm=(0, 260), d=.38, h=-120, scale=1.0):
    """Entrée « Lasseter » : anticipation (petit recul), trajectoire en ARC depuis frm (décalage), étirement dans la
    vitesse, arrivée amortie, écrasement à l'atterrissage, dépassement en rotation (follow-through)."""
    ta = t0 - .08                                   # anticipation : l'objet apparaît tassé et recule un peu
    if t < ta: return
    if t < t0:
        u = (t - ta)/.08; px, py = x + frm[0]*1.05, y + frm[1]*1.05
        draw_sxy(cv, fr, lab, px, py, scale*(.55 + .1*u), scale*(.45 + .1*u), rot, min(1, u*2)); return
    u = prog(t, t0, d); e = ease_out(u)
    px, py = arc((x + frm[0], y + frm[1]), (x, y), e, h)
    if u < 1:                                       # étirement selon la vitesse (stretch)
        v = 1 - e; sy = 1 + .35*v; sx = 1/sy
        draw_sxy(cv, fr, lab, px, py, scale*sx*lerp(.6, 1, e), scale*sy*lerp(.6, 1, e), rot + 14*v*(1 if frm[0] >= 0 else -1))
    else:
        sx, sy = squash(t, t0 + d, .22)
        draw_sxy(cv, fr, lab, x, y, scale*sx, scale*sy, rot + 30*settle(t, t0 + d, .2))

def stamp(cv, fr, lab, t, t0, x, y, rot=-6, scale=1.0, dust=True):
    """Tampon : ANTICIPATION (monte et grossit 0,12 s), chute rapide (TIMING 0,08 s), ÉCRASEMENT à l'impact,
    rebond amorti (FOLLOW-THROUGH), poussière qui gicle (ACTION SECONDAIRE)."""
    if t < t0 - .12: return
    if t < t0:                                      # anticipation : levé, un peu tourné, au-dessus
        u = ease((t - t0 + .12)/.12)
        draw_sxy(cv, fr, lab, x, y - 60*u, scale*(1.25 + .1*u), scale*(1.25 + .1*u), rot - 6*u, .85); return
    if t < t0 + .08:                                # chute rapide
        u = ease_in((t - t0)/.08)
        draw_sxy(cv, fr, lab, x, y - 60*(1 - u), scale*lerp(1.35, 1, u), scale*lerp(1.35, 1, u), rot - 6*(1 - u)); return
    sx, sy = squash(t, t0 + .08, .3)
    draw_sxy(cv, fr, lab, x, y, scale*sx*1.0, scale*sy, rot + 8*settle(t, t0 + .08, .3))
    if dust: puff(cv, t, t0 + .08, x, y + 40*scale, int(220*scale))

def puff(cv, t, t0, x, y, w=220, col=(235, 228, 210)):
    """Action secondaire : petits nuages de poussière papier qui s'écartent en arc puis s'évaporent."""
    from PIL import ImageDraw
    u = prog(t, t0, .45)
    if u <= 0 or u >= 1: return
    d = ImageDraw.Draw(cv); e = ease_out(u)
    for k in range(8):
        side = -1 if k % 2 else 1; sp = (k//2 + 1)/4
        px = x + side*(w/2 + 90*e*sp + 10*k); py = y - 50*e*math.sin(math.pi*min(1, e*1.2))*sp
        r = (16 + 10*sp)*(1 - u*.7)
        d.ellipse([px - r, py - r, px + r, py + r], fill=col)

def hop(t, t0, h=180, d=.55, crouch=.12):
    """Saut d'un personnage : (dy, sx, sy) avec ANTICIPATION (tassement), étirement à l'envol, ARC, écrasement à
    l'atterrissage. Sans saut (t hors plage) : (0, 1, 1)."""
    if t < t0 - crouch or t > t0 + d + .5: return 0.0, 1.0, 1.0
    if t < t0:                                       # tassement
        u = ease((t - t0 + crouch)/crouch); return 0.0, 1 + .12*u, 1 - .14*u
    if t < t0 + d:                                   # en l'air : parabole, étiré à la montée et à la descente
        u = (t - t0)/d; dy = -h*4*u*(1 - u); v = abs(1 - 2*u)
        return dy, 1 - .1*v, 1 + .14*v
    sx, sy = squash(t, t0 + d, .2)
    return 0.0, sx, sy

def wave(t, i=0, amp=1.0, freq=1.6):
    """Action secondaire continue (écharpe, drapeau, papier qui respire) : petite oscillation décalée par élément."""
    return amp*math.sin(2*math.pi*freq*t + i*.9)

def dim(cv, a=.45):
    """Staging : assombrit tout ce qui est déjà dessiné, pour isoler l'élément suivant."""
    from PIL import Image
    if a <= .01: return
    ov = Image.new("RGBA", cv.size, (10, 10, 18, int(255*a))); cv.alpha_composite(ov) if cv.mode == "RGBA" else cv.paste(ov, (0, 0), ov)
