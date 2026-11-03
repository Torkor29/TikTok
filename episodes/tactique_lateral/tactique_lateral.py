"""CONCEPT 2 — « Qu'est-ce qui fait un grand latéral moderne ? Analysons ça » (tableau tactique néon, 4 points numérotés, ~45 s).
Exemple : Hakimi (but en finale de Ligue des champions 2025). Voix : voix/voix.mp3 ; sans voix -> minutage estimé.
  python3 episodes/tactique_lateral/tactique_lateral.py [--stills]"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from tactique import *
TEXTE = ["Qu'est-ce qui fait un grand latéral moderne ? Analysons ça.",
         "Un : il défend d'abord.",
         "Il ferme son couloir et ne laisse jamais l'ailier se retourner.",
         "Deux : il monte au bon moment.",
         "Quand l'ailier rentre, lui prend tout le couloir.",
         "Trois : il rentre au milieu, pour créer le surnombre.",
         "Quatre : il finit les actions. Centre en retrait, frappe, passe décisive.",
         "Regarde Hakimi : il a marqué en finale de Ligue des champions.",
         "L'erreur classique ? Monter, et oublier de redescendre.",
         "Tu veux le même pour les attaquants ? Dis-le en commentaire."]
T = Tac("ANALYSE TACTIQUE · LE LATÉRAL", TEXTE, os.path.join(HERE, "voix", "voix.mp3"), "tactique_lateral")
t = T.t
# --- 0. titre (lisible dès l'image 0)
T.big(-.6, "LATÉRAL", t(1, "Un") - .1, LINE, "QU'EST-CE QUI FAIT UN GRAND · ANALYSONS ÇA")
ours = dict(gk=(.5, .93), dd=(.86, .74), dc1=(.63, .8), dc2=(.37, .8), dg=(.14, .74), mdc=(.5, .62), md=(.68, .5), mg=(.32, .5), ad=(.82, .3), bu=(.5, .24), ag=(.18, .3))
NUM = dict(gk=1, dd=2, dc1=4, dc2=5, dg=3, mdc=6, md=8, mg=10, ad=7, bu=9, ag=11)
for k, (n, (x, y)) in enumerate(ours.items()): T.player(n, NUM[n], YEL, x, y, .05*k - .6)
T.ring(-.6, "dd", t(1, "Un") - .1, LINE)
# --- 1-2. il défend d'abord : ferme le couloir, l'ailier ne se retourne pas
t1 = t(1, "Un"); T.big(t1, "01", t(1, "abord", end=True) + .1, YEL, "IL DÉFEND D'ABORD"); T.sound(t1, "stamp", .3)
T.camera(t(2, "Il"), 820, 1150, 1.45, .7)
T.player("o_ail", None, RED, .9, .5, t(2, "Il")); T.ball = [(t(2, "Il"), .88, .53), (t(2, "couloir"), .88, .53, .3)]
T.move("dd", t(2, "ferme"), .88, .62, .45); T.zone(t(2, "couloir"), (.76, .4, 1, .75), LINE, t(3, "Deux") - .1, "SON COULOIR")
T.arrow(t(2, "retourner") - .3, (.9, .5), (.82, .34), RED, .35, t(3, "Deux") - .1, dash=True, curve=-.2)
T.tag(t(2, "jamais"), "IL NE SE RETOURNE PAS", 380, RED, t(3, "Deux") - .1, 38); T.sound(t(2, "jamais"), "stamp", .3)
# --- 3-4. il monte au bon moment : l'ailier rentre, lui prend le couloir
t2 = t(3, "Deux"); T.big(t2, "02", t(3, "moment", end=True) + .1, YEL, "IL MONTE AU BON MOMENT"); T.sound(t2, "stamp", .3)
T.pl["o_ail"]["t_out"] = t2
T.camera(t2, W/2, 900, 1.15, .6); T.ball.append((t2 + .2, .68, .5, .3))
T.move("ad", t(4, "rentre") - .1, .66, .3, .5); T.arrow(t(4, "rentre") - .15, (.82, .3), (.66, .3), YEL, .35, t(5, "Trois") - .1)
T.move("dd", t(4, "prend") - .1, .9, .28, .8); T.arrow(t(4, "prend") - .15, (.88, .62), (.9, .3), LINE, .6, t(5, "Trois") - .1)
T.zone(t(4, "couloir"), (.8, .12, 1, .7), LINE, t(5, "Trois") - .1, "TOUT LE COULOIR"); T.sound(t(4, "prend"), "whoosh", .3)
# --- 5. il rentre au milieu : surnombre
t3 = t(5, "Trois"); T.big(t3, "03", t(5, "milieu", end=True) + .05, YEL, "IL RENTRE AU MILIEU"); T.sound(t3, "stamp", .3)
T.move("dd", t3 + .2, .62, .55, .6); T.move("ad", t3 + .2, .84, .3, .5); T.move("md", t3 + .2, .72, .42, .5)
T.player("o_m1", None, RED, .55, .45, t(5, "créer") - .1); T.player("o_m2", None, RED, .7, .5, t(5, "créer"))
T.zone(t(5, "surnombre"), (.45, .38, .85, .62), YEL, t(6, "Quatre") - .1, "3 CONTRE 2"); T.sound(t(5, "surnombre"), "sparkle", .3)
# --- 6. il finit les actions : centre en retrait, frappe, passe décisive
t4 = t(6, "Quatre"); T.big(t4, "04", t(6, "actions", end=True) + .05, YEL, "IL FINIT LES ACTIONS"); T.sound(t4, "stamp", .3)
for n in ("o_m1", "o_m2"): T.pl[n]["t_out"] = t4
T.camera(t(6, "Centre"), 760, 620, 1.35, .6)
T.move("dd", t(6, "Centre") - .3, .84, .12, .5); T.move("bu", t(6, "Centre") - .3, .5, .16, .4); T.move("mg", t(6, "Centre") - .3, .44, .2, .4)
T.ball += [(t(6, "Centre") - .2, .84, .12, .4), (t(6, "retrait"), .52, .18, .3), (t(6, "frappe"), .5, .02, .25)]
T.arrow(t(6, "Centre"), (.84, .12), (.53, .18), LINE, .3, t(7, "Regarde") - .1); T.arrow(t(6, "frappe"), (.5, .17), (.5, .03), YEL, .25, t(7, "Regarde") - .1)
T.sound(t(6, "frappe"), "kick", .3); T.sound(t(6, "décisive"), "goal_roar", .25)
# --- 7. Hakimi
T.tag(t(7, "Hakimi"), "HAKIMI · BUT EN FINALE DE LDC 2025", 380, YEL, t(8, "erreur") - .1, 38); T.ring(t(7, "Hakimi"), "dd", t(8, "erreur") - .1, YEL)
# --- 8. l'erreur classique : il monte… et ne redescend pas
te = t(8, "erreur"); T.camera(te, W/2, H/2, 1.0, .5); T.tag(te, "L'ERREUR CLASSIQUE", 380, RED, None, 50); T.sound(te, "stamp", .35)
T.move("dd", te + .1, .9, .2, .5)
T.player("o_c", None, RED, .7, .42, t(8, "Monter")); T.ball.append((t(8, "Monter"), .7, .45, .2)); T.ball.append((t(8, "oublier"), .9, .7, .5))
T.zone(t(8, "oublier"), (.76, .55, 1, .92), RED, None, "LE TROU"); T.arrow(t(8, "oublier") - .1, (.72, .45), (.9, .72), RED, .5)
T.sound(t(8, "redescendre"), "gasp", .3)
# --- 9. fin
tf = t(9, "Tu"); T.big(tf, "ATTAQUANTS ?", T.T, YEL, "DIS-LE EN COMMENTAIRE"); T.sound(tf, "notif", .35)
if __name__ == "__main__":
    out = os.path.join(ROOT, "output", "tactique_lateral"); os.makedirs(out, exist_ok=True)
    if "--stills" in sys.argv: print(T.stills(os.path.join(os.environ.get("STILLS_DIR", out), "tactique_lateral_planche.jpg"))); sys.exit()
    open(os.path.join(HERE, "TEXTE_VOIX.txt"), "w").write("\n".join(TEXTE) + "\n"); print(T.render(out), round(T.T, 2))
