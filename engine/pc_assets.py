"""Bibliothèque d'assets papercraft low-poly (engine/papercraft.py). Chaque fonction renvoie une liste de Part.
Règle : volumes à facettes visibles (pas de cubes lisses), peinture en traits de pinceau à bouts ronds,
blancs mouchetés, pièces animables nommées."""
import math
import numpy as np
from engine.papercraft import Part, cbox, pyramid, rot, speckle, capsule

DARK = np.array((36, 30, 28))/255; WHITE = np.array((236, 230, 222))/255

def _sym(pts):
    """Ajoute le symétrique en x de chaque point (modèles symétriques)."""
    pts = np.array(pts, float); m = pts.copy(); m[:, 0] *= -1
    return np.vstack([pts, m])

def cat(fur=(128, 116, 110), stripe=DARK, white=WHITE):
    """Chat tigré low-poly (face +z). Pièces animables : leg_fl/fr/bl/br, head* (tête, museau, oreilles), tail."""
    st = np.asarray(stripe, float); wh = np.asarray(white, float)
    def p_body(P, c):
        x, y, z = P.T; m = np.zeros(len(P), bool)
        for zc in (-.62, -.3, .02, .32):                              # anneaux du dos qui descendent sur les flancs
            m |= capsule(z + .05*np.sin(y*5), np.abs(x)*(y > .3) + (y <= .3)*(.55 + (.3 - y)), (zc, 0), (zc, .95), .085)
        for yc in (.05, -.2):                                          # flancs : traits horizontaux courts
            m |= (np.abs(x) > .5) & capsule(z, y, (.25, yc), (.6, yc - .03), .07)
        c[m] = st; return c
    def p_head(P, c):
        x, y, z = P.T
        blaze = (z > .2) & (np.abs(x) < .09 + np.clip(.15 - y, 0, 1)*.42) & (y < .45)
        c[blaze] = wh; c = np.where(blaze[:, None], speckle(P, c.copy(), .03), c)
        eye = (z > .1) & (((np.abs(x) - .43)**2 + (y + .02)**2) < .14**2)
        top = (y > .3) & (capsule(x, z, (-.02, .45), (-.06, -.1), .07) | capsule(x, z, (-.3, .4), (-.36, -.05), .06)
                          | capsule(x, z, (.27, .42), (.34, -.05), .06))
        cheek = (np.abs(x) > .55) & (capsule(z, y, (.42, .12), (.1, .2), .055) | capsule(z, y, (.42, -.12), (.12, -.2), .055))
        side = (np.abs(x) > .6) & capsule(z, y, (-.35, .28), (-.1, .25), .06)
        c[(top | cheek | side) & ~blaze] = st; c[eye] = st
        return c
    def p_muzzle(P, c):
        x, y, z = P.T
        c = speckle(P, c, .03)
        f = (z > .2) & (y > -.02)
        nose = f & ((((x + .05)**2 + (y - .1)**2) < .06**2) | (((x - .05)**2 + (y - .1)**2) < .06**2)
                    | ((y < .1) & (y > .1 - .11*(1 - np.abs(x)/.11)) & (np.abs(x) < .11)))
        c[nose] = st; return c
    def p_leg(P, c):
        x, y, z = P.T
        m = (capsule(np.abs(x) + np.abs(z), y, (0, .2), (.5, .17), .055) | capsule(np.abs(x) + np.abs(z), y, (0, .02), (.5, -.01), .05)) & (y > -.15)
        c[m] = st
        w = y < -.19 + .03*np.sin(x*20)
        c[w] = wh; c = np.where(w[:, None], speckle(P, c.copy(), .035), c)
        return c
    def p_tail(P, c):
        x, y, z = P.T
        c[((y*3.4 + .1) % 1 < .38) & (y > .1)] = st; return c
    parts = []
    body = _sym([[.55, .2, .85], [.48, .45, .78], [.55, -.4, .8], [.42, -.48, .7], [.55, .3, -.85], [.45, .46, -.8], [.55, -.38, -.85],
                 [.4, -.47, -.75], [.6, 0, 0], [.5, .47, 0], [.48, -.47, .05], [0, .56, .3], [0, .56, -.5], [.25, .54, -.1], [0, .1, .95], [.3, .05, .9], [0, .1, -.95], [.62, .05, -.45], [.62, -.05, .45]])
    parts.append(Part(body, fur, p_body, (0, 1.05, -.55), name="body"))
    leg = _sym([[.16, .38, .16], [.16, .38, -.16], [.14, -.39, .15], [.14, -.39, -.15], [.18, .05, .17], [.18, .05, -.17]])
    for nm, x, z in (("leg_fl", -.32, .12), ("leg_fr", .32, .12), ("leg_bl", -.32, -1.2), ("leg_br", .32, -1.2)):
        parts.append(Part(leg, fur, p_leg, (x, .39, z), pivot=(0, .34, 0), name=nm))
    parts.append(Part(np.vstack([cbox(.24, .1, .28, .12), cbox(.18, .1, .2, .12) + [0, .5, -.12], cbox(.11, .08, .12, .1) + [0, .92, -.12]]),
                      fur, p_tail, (0, 1.38, -1.28), name="tail"))
    hp = np.array((0, 2.1, .3))
    head = _sym([[.62, .58, -.5], [.72, .3, -.55], [.62, -.45, -.5], [.4, -.6, -.4], [.76, .32, .2], [.82, -.08, .28],
                 [.66, .55, .32], [.3, .62, .5], [.52, -.5, .42], [.25, -.62, .5], [.5, .1, .62], [.0, .64, .5], [.0, .2, .66]])
    parts.append(Part(head, fur, p_head, hp, pivot=(0, -.55, 0), name="head"))
    muz = 1.3*_sym([[.24, .1, 0], [.15, .17, .15], [.0, .2, -.1], [.0, .05, .42], [.12, -.05, .36], [.26, -.15, .05], [.2, -.2, -.1], [.0, -.22, .2]])
    mpos = hp + (0, -.3, .5)
    parts.append(Part(muz, white*255, p_muzzle, mpos, pivot=tuple(hp + (0, -.55, 0) - mpos), name="head_muzzle"))
    for s in (-1, 1):
        ear = np.array([[-.34, 0, -.16], [.34, 0, -.18], [.0, 0, .24], [.0, -.08, .0], [.1*s, .5, -.02]], float)
        epos = hp + (.48*s, .5, .02)
        parts.append(Part(ear @ rot("z", -.28*s).T, fur, None, epos, pivot=tuple(hp + (0, -.55, 0) - epos), name="head_ear" + "lr"[s > 0]))
    return parts

def cat_anim(t, walk=0.0, look=0.0, nod=1.0):
    """Rotations : cycle de marche (walk = intensité, 0 = immobile), regard (look, rad), hochement."""
    a = .45*walk*math.sin(t*9); A = {}
    for nm, sg in (("leg_fl", 1), ("leg_br", 1), ("leg_fr", -1), ("leg_bl", -1)): A[nm] = rot("x", a*sg)
    h = rot("y", look) @ rot("x", .05*nod*math.sin(t*2.3)) @ rot("z", .04*nod*math.sin(t*1.7))
    for nm in ("head", "head_muzzle", "head_earl", "head_earr"): A[nm] = h
    A["tail"] = rot("z", .25*math.sin(t*3.1)) @ rot("x", -.12)
    return A
