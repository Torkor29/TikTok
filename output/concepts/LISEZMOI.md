# 3 nouveaux concepts (03/11/2026)

| # | Concept | Code | Voix à générer |
|---|---|---|---|
| 1 | « Le 4-3-3 du PSG, expliqué comme à mes joueurs » (tableau tactique néon, ~35 s) | `episodes/tactique_433/tactique_433.py` | `episodes/tactique_433/TEXTE_VOIX.txt` |
| 2 | « Qu'est-ce qui fait un grand latéral moderne ? Analysons ça » (4 points, ~45 s) | `episodes/tactique_lateral/tactique_lateral.py` | `episodes/tactique_lateral/TEXTE_VOIX.txt` |
| 3 | Storytime « Formé au PSG… il a fini à l'OM » : Rabiot (style Rennes + sous-titres karaoké, ~50 s) | `episodes/rabiot/rabiot.py` | `episodes/rabiot/TEXTE_VOIX.txt` |

Moteurs : `engine/tactique.py` (terrain néon, pastilles, zones, flèches, caméra), `engine/karaoke.py` (minutage au mot + sous-titres),
`episodes/rennes/rstyle.py` (boîte à outils du style Rennes). Voix déposée en `episodes/<x>/voix/voix.mp3` -> transcription automatique -> rendu.

Sources Rabiot : débuts 26/08/2012 contre Bordeaux à 17 ans (https://en.wikipedia.org/wiki/Adrien_Rabiot) ; réserviste refusé par mail en 2018
(https://uk.sports.yahoo.com/news/world-cup-2018-paris-saint-113600713.html) ; six mois sans jouer après son refus de prolonger (https://www.maxifoot.fr/football/article-44711.htm) ;
bagarre avec Rowe dans le vestiaire après Rennes-OM, 15/08/2025, puis vente au Milan AC (https://www.europe1.fr/sport/olympique-de-marseille-roberto-de-zerbi-justifie-la-mise-a-lecart-de-rabiot-et-rowe-apres-une-violente-altercation-769842).
