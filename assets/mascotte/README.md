# Mascotte « Ballon »

Planches générées sur ElevenLabs (gpt-image-2, référence = rendu de `engine/mascotte.py`), détourées (birefnet) puis découpées.

- `poses/` (12) : face, trois_quarts_gauche, profil_gauche, dos, trois_quarts_droite, profil_droite, trois_quarts_dos, plongee, coucou, pointe, bras_croises, saut
- `emotions/` (16) : neutre, blase, malin, rire, stress, choc, triste, fier, colere, perplexe, reflechit, celebre, facepalm, mort_de_rire, clin_doeil, fatigue
- `planche_*.png` : planches d'origine (fond gris) et détourées (fond transparent)

Utilisation :
```python
from mascotte import draw_sprite          # sprites IA (pieds en x, y)
draw_sprite(cv, "malin", 540, 1800, h=500, t=t, hop_t=1.2)
from mascotte import Ballon, envelope     # version vectorielle animée (bouche synchronisée sur la voix)
```
