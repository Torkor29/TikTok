# Mascotte v2 (proposition n°4 : casquette rouge à l'envers + sweat gris), style papier découpé

Générée sur ElevenLabs (gpt-image-2.5-sunburst) à partir de `../propositions_papier.png`, détourée (birefnet), découpée.

- `poses/` : face, trois_quarts_gauche, profil_gauche, dos, trois_quarts_droite, profil_droite, marche, court, coucou, pointe, bras_croises, saut
- `emotions/` : neutre, blase, malin, rire, stress, choc, triste, fier, colere, perplexe, reflechit, celebre, facepalm, mort_de_rire, clin_doeil, fatigue
- `apercu_28.jpg` : toutes les images d'un coup d'œil

```python
from mascotte import draw_sprite
draw_sprite(cv, "blase", 540, 1850, h=560, t=t, hop_t=None, flip=False)
```
