"""CONCEPT 1 — « Le 4-3-3 du PSG, expliqué comme à mes joueurs » (tableau tactique néon, ~35 s).
Base PSG champion d'Europe 2025 (Luis Enrique) : latéraux très hauts (Hakimi, Nuno Mendes), Vitinha qui décroche entre les centraux,
Dembélé faux 9, pressing de tout le bloc. Voix : voix/voix.mp3 (une prise, TEXTE, une phrase par ligne) ; sans voix -> minutage estimé.
  python3 episodes/tactique_433/tactique_433.py [--stills]"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from tactique import *
TEXTE = ["Le 4-3-3 du PSG, expliqué comme à mes joueurs.",
         "Quatre défenseurs, trois milieux, trois attaquants.",
         "Mais avec le ballon, tout change.",
         "Les latéraux, Hakimi et Nuno Mendes, montent comme des ailiers.",
         "Vitinha décroche entre les centraux : c'est lui qui lance le jeu.",
         "Devant, Dembélé recule en faux neuf, et libère l'espace pour les ailiers.",
         "Sans le ballon ? Tout le monde presse. Les attaquants d'abord.",
         "Résultat : l'adversaire n'a jamais le temps.",
         "Tu veux quel système ensuite ? Dis-le en commentaire."]
T = Tac("ANALYSE TACTIQUE · 4-3-3", TEXTE, os.path.join(HERE, "voix", "voix.mp3"), "tactique_433")
t = T.t
# --- 0. titre
T.big(-.6, "LE 4-3-3", t(1, "Quatre") - .1, YEL, "DU PSG · EXPLIQUÉ À MES JOUEURS")
# --- 1. 4 / 3 / 3 : les lignes apparaissent au mot
base = dict(gk=(.5, .93), dd=(.86, .76), dc1=(.63, .8), dc2=(.37, .8), dg=(.14, .76), mdc=(.5, .63), md=(.7, .52), mg=(.3, .52),
            ad=(.82, .3), bu=(.5, .24), ag=(.18, .3))
NUM = dict(gk=99, dd=2, dc1=5, dc2=51, dg=25, mdc=17, md=87, mg=8, ad=14, bu=10, ag=7)
tq, tt, ta = t(1, "Quatre"), t(1, "trois"), t(1, "trois", 2)
T.player("gk", NUM["gk"], YEL, *base["gk"], tq - .2)
for k, n in enumerate(("dg", "dc2", "dc1", "dd")): T.player(n, NUM[n], YEL, *base[n], tq + k*.07)
for k, n in enumerate(("mg", "mdc", "md")): T.player(n, NUM[n], YEL, *base[n], tt + k*.07)
for k, n in enumerate(("ag", "bu", "ad")): T.player(n, NUM[n], YEL, *base[n], ta + k*.07)
T.zone(tq, (0, .7, 1, .86), YEL, t(2, "Mais") - .1, "4 DÉFENSEURS"); T.zone(tt, (0, .45, 1, .69), YEL, t(2, "Mais") - .1, "3 MILIEUX")
T.zone(ta, (0, .18, 1, .38), YEL, t(2, "Mais") - .1, "3 ATTAQUANTS")
for x in (tq, tt, ta): T.sound(x, "stamp", .25)
# --- 2. avec le ballon
tb = t(2, "ballon"); T.ball = [(tb - .1, .5, .9), (tb + .3, .5, .9, .3)]
T.tag(t(2, "Mais"), "AVEC LE BALLON", 300, LINE, t(6, "Sans") - .1); T.sound(t(2, "Mais"), "whoosh", .3)
# --- 3. latéraux hauts
tl = t(3, "montent")
T.move("dd", tl - .2, .9, .36, .7).move("dg", tl - .1, .1, .36, .7)
T.arrow(tl - .25, (.86, .74), (.9, .4), YEL, .5, t(4, "Vitinha")); T.arrow(tl - .15, (.14, .74), (.1, .4), YEL, .5, t(4, "Vitinha"))
T.zone(t(3, "latéraux"), (.8, .15, 1, .85), YEL, t(4, "Vitinha")); T.zone(t(3, "latéraux"), (0, .15, .2, .85), YEL, t(4, "Vitinha"))
T.tag(t(3, "Hakimi"), "HAKIMI", 1010, YEL, t(4, "Vitinha"), 40, 820); T.tag(t(3, "Nuno"), "NUNO MENDES", 1010, YEL, t(4, "Vitinha"), 40, 260)
T.sound(tl, "whoosh", .25)
# --- 4. Vitinha décroche entre les centraux, lance le jeu
tv = t(4, "décroche")
T.move("mdc", tv - .1, .5, .82, .6).move("dc1", tv, .7, .8, .5).move("dc2", tv, .3, .8, .5)
T.ring(t(4, "Vitinha"), "mdc", t(5, "Devant") - .1, YEL, "LE PATRON")
T.ball.append((tv + .4, .5, .85, .4)); T.ball.append((t(4, "lance"), .9, .4, .45))
T.arrow(t(4, "lance") - .05, (.5, .82), (.88, .42), LINE, .4, t(5, "Devant"), dash=True, curve=.15); T.sound(t(4, "lance"), "whoosh", .25)
# --- 5. Dembélé faux 9 : il recule, l'espace s'ouvre, les ailiers attaquent
td = t(5, "recule")
T.move("bu", td - .1, .5, .44, .6); T.ring(t(5, "Dembélé"), "bu", t(6, "Sans") - .1, YEL, "FAUX 9")
T.zone(t(5, "libère"), (.3, .06, .7, .3), LINE, t(6, "Sans") - .1, "L'ESPACE")
T.move("ad", t(5, "ailiers") - .2, .64, .16, .5).move("ag", t(5, "ailiers") - .1, .36, .16, .5)
T.arrow(t(5, "ailiers") - .25, (.82, .3), (.64, .17), YEL, .4, t(6, "Sans")); T.arrow(t(5, "ailiers") - .15, (.18, .3), (.36, .17), YEL, .4, t(6, "Sans"))
T.sound(t(5, "libère"), "sparkle", .3)
# --- 6. sans le ballon : tout le monde presse, les attaquants d'abord
ts_ = t(6, "Sans"); T.tag(ts_, "SANS LE BALLON", 300, RED, None); T.ball.append((ts_, .5, .14, .3)); T.sound(ts_, "whoosh", .3)
opp = dict(o_gk=(.5, .05), o_dc1=(.38, .14), o_dc2=(.62, .14), o_dd=(.86, .22), o_dg=(.14, .22), o_m=(.5, .32))
for k, (n, (x, y)) in enumerate(opp.items()): T.player(n, None, RED, x, y, ts_ + k*.05)
tp = t(6, "presse")
for n, (x, y) in dict(dd=(.84, .4), dg=(.16, .4), dc1=(.64, .56), dc2=(.36, .56), mdc=(.5, .45), md=(.62, .36), mg=(.38, .36), gk=(.5, .8)).items():
    T.move(n, tp - .1, x, y, .7)
T.zone(tp, (0, .05, 1, .45), RED, None, "PRESSING")
ta2 = t(6, "attaquants")
for n, (x, y), tgt in (("ag", (.36, .18), (.39, .16)), ("bu", (.5, .2), (.5, .09)), ("ad", (.64, .18), (.61, .16))):
    T.move(n, ta2 - .1, *tgt, .4); T.arrow(ta2 - .15, (x, y), tgt, RED, .3, t(7, "temps"))
T.sound(ta2, "stamp", .3)
# --- 7. l'adversaire n'a jamais le temps
tr = t(7, "Résultat"); T.ring(tr, "o_dc1", None, RED, "PAS LE TEMPS"); T.ball.append((tr, .4, .15, .2)); T.sound(t(7, "jamais"), "stamp", .3)
# --- 8. question finale
tf = t(8, "Tu"); T.big(tf, "TON SYSTÈME ?", T.T, YEL, "DIS-LE EN COMMENTAIRE"); T.sound(tf, "notif", .35)
T.camera(t(3, "latéraux"), W/2, 1000, 1.06); T.camera(tv, W/2, 1300, 1.12); T.camera(td, W/2, 800, 1.1); T.camera(ts_, W/2, 900, 1.0)
if __name__ == "__main__":
    out = os.path.join(ROOT, "output", "tactique_433")
    if "--stills" in sys.argv: print(T.stills(os.path.join(os.environ.get("STILLS_DIR", out), "tactique_433_planche.jpg"))); sys.exit()
    open(os.path.join(HERE, "TEXTE_VOIX.txt"), "w").write("\n".join(TEXTE) + "\n"); print(T.render(out), round(T.T, 2))
