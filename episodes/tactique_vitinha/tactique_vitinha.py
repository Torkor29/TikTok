"""TACTIQUE COURTE (~18 s) : « Le joueur le plus important du PSG, ce n'est pas Dembélé. » -> Vitinha. Règles tirées des stats du 4-3-3 :
hook d'opinion (contre-intuitif) avec un visage énorme à l'image 0, une seule idée, 18 s, BOUCLE (la dernière phrase finit sur « Dembélé »
et l'image de fin = l'image 0 -> la vidéo repart d'elle-même), appel au partage. DA papier (engine/tactique.py, thème papier).
  python3 episodes/tactique_vitinha/tactique_vitinha.py [--stills]"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from tactique import *
import tactique as TQ
from paper_cut import paper_player
TEXTE = ["Le joueur le plus important du PSG, ce n'est pas Dembélé.",
         "C'est lui : Vitinha.",
         "Sans le ballon, il protège la défense.",
         "Avec le ballon, il décroche entre les centraux, et lance tout.",
         "Un ballon perdu ? Il est le premier à presser.",
         "Envoie ça à ton pote qui croit encore que c'est Dembélé."]
T = Tac("TACTIQUE · PSG", TEXTE, os.path.join(HERE, "voix", "voix.mp3"), "tactique_vitinha")
t = T.t
_D = {}
def dembele():
    if "d" not in _D: _D["d"] = paper_player(os.path.join(ROOT, "assets", "photos", "psg", "dembele.png"), None, 900, real=True)
    return _D["d"]
def lab(txt, size, fg, bg, key): return TQ.PLabel(txt, size, fg, bg) if TQ.PX.ON else TQ._E.Label(txt, key, font(size), fg, bg, padx=26, pady=8, rough=2.5)
tv = t(1, "C'est"); tend = t(5, "Envoie")
def hook(L, tt, fr):
    """Image 0 (et image de fin, pour la boucle) : Dembélé en grand + la question ; « PAS » le barre."""
    show = tt < tv - .05 or tt >= tend - .05
    if not show: return
    u = tt if tt < tv else tt - tend
    ov = Image.new("RGBA", (W, H), (236, 226, 204, 255)); TQ.p_pitch(fr)
    ov.alpha_composite(TQ.p_pitch(fr))
    if not TQ.PX.ON: ov.alpha_composite(Image.new("RGBA", (W, H), (20, 36, 82, 120)))
    sp = dembele(); ax, ay = sp.info["anchor"]; ov.alpha_composite(sp, (int(W/2 - ax), int(1830 - ay)))
    lab("LE JOUEUR LE PLUS", 78, (250, 248, 240), TQ.INK_, "vh1").draw(ov, fr, W/2, 380, 1, -3)
    lab("IMPORTANT DU PSG ?", 96, TQ.INK_, TQ.MUST, "vh2").draw(ov, fr, W/2, 520, 1, 2)
    if tt < tv:
        if tt > t(0, "pas") - .05:                               # gros « NON » tamponné + croix au feutre sur Dembélé
            k = clamp((tt - t(0, "pas") + .05)/.18); s = 1.6 - .6*k
            d = ImageDraw.Draw(ov); q = clamp((tt - t(0, "Dembélé"))/.25)
            if q > 0:
                d.line([(250, 900), (250 + 580*q, 900 + 820*q)], fill=TQ.RED_, width=26); d.line([(830, 900), (830 - 580*q, 900 + 820*q)], fill=TQ.RED_, width=26)
            lab("PAS DEMBÉLÉ", 120, (250, 248, 240), TQ.RED_, "vh3").draw(ov, fr, W/2, 1180, s, -8)
    else:                                                        # fin : appel au partage, puis on retombe sur l'image 0
        lab("ENVOIE ÇA À TON POTE", 74, (250, 248, 240), TQ.RED_, "vh4").draw(ov, fr, W/2, 700, eob(u/.3), -4)
        if tt > t(5, "croit"): lab("QUI CROIT QUE C'EST DEMBÉLÉ", 56, TQ.INK_, TQ.MUST, "vh5").draw(ov, fr, W/2, 830, eob((tt - t(5, "croit"))/.3), 3)
    L.paste(ov, (0, 0))
T.extras.append(hook)
# --- l'équipe en place (déjà là sous l'image 0)
base = dict(gk=(.5, .93), dd=(.86, .74), dc1=(.63, .8), dc2=(.37, .8), dg=(.14, .74), vit=(.5, .62), md=(.7, .5), mg=(.3, .5), ad=(.82, .3), bu=(.5, .24), ag=(.18, .3))
NUM = dict(gk=99, dd=2, dc1=5, dc2=51, dg=25, vit=17, md=87, mg=8, ad=14, bu=10, ag=7)
for n, (x, y) in base.items(): T.player(n, NUM[n], YEL, x, y, -1, label="VITINHA" if n == "vit" else None)
T.ring(tv, "vit", t(2, "Sans") - .05, YEL, "C'EST LUI"); T.camera(tv, W/2, 1150, 1.25, .5); T.sound(tv, "stamp", .3)
# --- sans le ballon : il protège la défense
ts_ = t(2, "Sans"); T.tag(ts_, "SANS LE BALLON", 330, RED, t(3, "Avec") - .05); T.camera(ts_, W/2, 1050, 1.05, .5)
for k, (n, x, y) in enumerate((("o1", .4, .45), ("o2", .6, .42), ("o3", .5, .35))): T.player(n, None, RED, x, y, ts_ + .05*k, t(3, "Avec"))
T.ball = [(ts_, .5, .36), (t(2, "protège"), .5, .44, .3)]
T.move("vit", t(2, "protège") - .1, .5, .55, .35); T.zone(t(2, "protège"), (.3, .5, .7, .7), YEL, t(3, "Avec") - .05, "IL PROTÈGE LA DÉFENSE")
T.arrow(t(2, "défense") - .1, (.5, .55), (.5, .46), YEL, .25, t(3, "Avec") - .05); T.sound(t(2, "protège"), "stamp", .25)
# --- avec le ballon : il décroche entre les centraux et lance tout
ta = t(3, "Avec"); T.tag(ta, "AVEC LE BALLON", 330, LINE, t(4, "Un") - .05)
T.ball.append((ta + .1, .5, .82, .3)); T.move("vit", t(3, "décroche") - .1, .5, .82, .45)
T.move("dc1", t(3, "décroche"), .72, .8, .4).move("dc2", t(3, "décroche"), .28, .8, .4); T.move("dd", t(3, "centraux"), .9, .4, .5).move("dg", t(3, "centraux"), .1, .4, .5)
T.ring(t(3, "décroche"), "vit", t(4, "Un") - .05, YEL, "IL DÉCROCHE")
tl = t(3, "lance"); T.ball.append((tl, .82, .3, .35)); T.arrow(tl - .05, (.5, .82), (.82, .31), LINE, .3, t(4, "Un") - .05, dash=True, curve=.12)
T.arrow(tl + .15, (.5, .82), (.9, .42), LINE, .3, t(4, "Un") - .05, dash=True, curve=-.1); T.sound(tl, "whoosh", .3); T.camera(t(3, "décroche"), W/2, 1250, 1.15, .4)
T.camera(tl, W/2, 960, 1.0, .4)
# --- ballon perdu : premier à presser
tp = t(4, "Un"); T.tag(tp, "BALLON PERDU ?", 330, RED, tend - .05); T.player("o4", None, RED, .7, .36, tp); T.ball.append((tp + .05, .7, .38, .2))
T.move("vit", t(4, "premier") - .2, .66, .42, .35); T.arrow(t(4, "premier") - .25, (.5, .82), (.66, .44), RED, .3, tend - .05)
T.ring(t(4, "presser"), "vit", tend - .05, RED, "LE 1er À PRESSER"); T.sound(t(4, "presser"), "stamp", .3); T.camera(t(4, "premier"), 760, 900, 1.2, .4)
T.camera(tend - .1, W/2, H/2, 1.0, .15)
T.sound(0.0, "stamp", .25); T.sound(t(0, "pas"), "stamp", .35); T.sound(tend, "notif", .35)
T.T = T.W.end + .25                                              # boucle : pas de longue fin muette
if __name__ == "__main__":
    out = os.path.join(ROOT, "output", "tactique_vitinha"); os.makedirs(out, exist_ok=True)
    open(os.path.join(HERE, "TEXTE_VOIX.txt"), "w").write("\n".join(TEXTE) + "\n")
    if "--stills" in sys.argv: print(T.stills(os.path.join(os.environ.get("STILLS_DIR", out), "tactique_vitinha_planche.jpg"))); sys.exit()
    print(T.render(out), round(T.T, 2))
