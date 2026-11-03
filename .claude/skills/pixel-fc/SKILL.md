---
name: pixel-fc
description: Crée les vidéos TikTok foot de la chaîne dans la DA « pixel.fc » (pixel-art rétro façon jeu vidéo 16 bits : gros pixels 4×4, palette fixe de 32 couleurs PICO-8 étendue, police pixel Silkscreen nette, boîtes de dialogue, lignes de balayage) — EXACTEMENT les mêmes formats que la série papier : tactique (« le 4-3-3 expliqué », « le joueur le plus important… »), storytime style Rennes (histoire d'un joueur / d'un club), quiz, « devine les stars », vrai ou faux, top. Utilise ce skill dès que l'utilisateur parle de pixel, pixel.fc, pixel art, rétro, 8-bit / 16-bit, « version pixel », « en pixel », ou veut refaire une vidéo déjà faite en pixel, même s'il ne dit pas « skill ».
---

# pixel.fc — la même chaîne, en pixel-art

**Même méthode, mêmes règles, autre DA.** Tout ce qui marche dans la série papier s'applique tel quel :
- sujet / hook / rythme / description / commentaire épinglé : `.claude/skills/tiktok-foot-viral/SKILL.md` (à relire avant chaque vidéo) ;
- storytime : `SKILL.md` racine + modèle Rennes (`episodes/rennes/rennes3.py`, boîte à outils `episodes/rennes/rstyle.py`) ;
- quiz : `.claude/skills/tiktok-foot-quiz/SKILL.md` ; tactique : `engine/tactique.py` (+ `engine/karaoke.py`).
- Préférences utilisateur toujours valables : **pas de musique intégrée** (son tendance ajouté dans l'appli), **pas d'effets « édit »**
  (flash, RGB split, zoom sur les temps), image 0 lisible avec un visage ou un écusson énorme, 15-20 s pour une idée tactique,
  boucle (la fin renvoie à l'image 0), appel au partage, sous-titres mot à mot.

## Le moteur : `engine/pixel.py`
- `PIXEL=1` (variable d'environnement) active la DA pixel dans `engine/tactique.py`, `engine/karaoke.py` et `episodes/rennes/rstyle.py`.
- `PIXEL_SCALE=4` (défaut) : un gros pixel = 4×4 px → image de travail 270×480 agrandie sans flou.
- `pixelate(img)` : réduction en moyenne → palette 32 couleurs (sans tramage) → filtre « mode » 3×3 qui efface le grain → agrandissement net.
- `ptext_img(txt, 8, couleur, s=8)` : texte en Silkscreen 8 px agrandi ×8, contour + ombre de 1 gros pixel (Silkscreen a les accents ;
  Press Start 2P n'a PAS « É », ne pas l'utiliser pour du français accentué).
- `plabel(txt, 8, fg, bg, cadre, s=5)` : étiquette « boîte de dialogue » (aplat, cadre clair, coins coupés, ombre portée).
- `put(cv, sprite, x, y)` : colle calé sur la grille de gros pixels (jamais de demi-pixel) ; `scanlines(cv)` : lignes de balayage discrètes.
- Palette : `PX.NAVY, RED, YELLOW, WHITE, GREEN, SKY, ORANGE, PINK…` ; `PX.near(rgb)` ramène une couleur dans la palette.

## Règles de DA (apprises en faisant les premières vidéos)
1. **Couleurs prises DANS la palette avant de dessiner.** Une couleur « entre deux » est mal quantifiée (le vert papier devenait gris-brun).
   Le thème pixel du tactique remplace kraft / herbe / craie par `DNAVY`, `GREEN` + `PAL[27]`, `WHITE`.
2. **Pas de texture papier en pixel** : `paper_fill` devient un aplat (`rstyle`), sinon le grain se transforme en camouflage.
3. **Tout texte d'interface est redessiné APRÈS la pixelisation** en police pixel (sous-titres, bandeau du haut, étiquettes, gros numéros,
   fil rouge) : un texte pixelisé après coup bave. Les gros mots-clés des scènes (≥ 90 px) peuvent rester dans la scène.
4. **Étiquettes du terrain plus grosses** (×1,45) ou directement en `plabel`, sinon illisibles à 270 px de large.
5. Photos de joueurs : détourées (`paper_player(..., real=True)`) puis pixelisées avec le reste → rendu « sprite » ressemblant.
6. Mouvements : par pas de gros pixel (le défilement des rayures avance par multiples de 4×S) pour garder l'effet rétro.

## Refaire une vidéo existante en pixel
- **Formats déjà branchés (rendu propre, textes nets)** : il suffit de relancer avec `PIXEL=1`, la sortie part dans `output/<slug>_pixel/`.
  ```bash
  PIXEL=1 python3 episodes/tactique_vitinha/tactique_vitinha.py     # -> output/tactique_vitinha_pixel/
  PIXEL=1 python3 episodes/tactique_433/tactique_433.py
  PIXEL=1 python3 episodes/tactique_lateral/tactique_lateral.py
  PIXEL=1 python3 episodes/rabiot/rabiot.py                         # storytime (rstyle)
  ```
  La voix déjà générée (`voix/voix.mp3` + `.mots.json`) est réutilisée : **0 crédit**.
- **N'importe quelle autre vidéo déjà rendue** (quiz, devine, PSG avant le Qatar…) : conversion directe du mp4, son copié.
  ```bash
  python3 scripts/pixelize_video.py output/devine_psg15/devine_psg15.mp4      # -> ..._pixel.mp4
  ```
  Plus rapide mais les petits textes de la vidéo sont pixelisés avec le reste (moins nets) : pour une vidéo importante, brancher son
  script sur `PIXEL=1` (voir ci-dessous).

## Brancher un nouveau script sur pixel.fc
- Tactique : `from tactique import *` suffit (le thème est choisi à l'import selon `PIXEL`). Les étiquettes dessinées dans les `extras`
  passent par `TQ.PLabel(txt, taille, fg, bg)` quand `TQ.PX.ON` (voir `episodes/tactique_vitinha/tactique_vitinha.py`, fonction `lab`).
- Storytime : `from rstyle import *` ; sortie via `out, SLUG = px_out(out, SLUG)` ; le fil rouge doit tester `PX.ON` et utiliser
  `PX.plabel` (voir `fil()` dans `episodes/rabiot/rabiot.py`) ; les sous-titres `KA.caption(...)` passent seuls en police pixel.
- Toujours vérifier une image en taille réelle (pas seulement la planche) : netteté des textes, couleurs dans la palette, rien de baveux.

## Livraison (comme la série papier)
mp4 avec voix + couverture 3:4 (1080×1440) et 4:3 (1440×1080) (`output/couvertures/make_covers.py`, relancer sur l'image pixel) +
description 2 lignes + 5 hashtags (dont `#pixelart`) + commentaire à épingler. Commit + push.
