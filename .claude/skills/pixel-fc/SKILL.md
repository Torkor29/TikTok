---
name: pixel-fc
description: Crée les vidéos TikTok foot de la chaîne en VRAI pixel-art « pixel.fc » (style des vidéos « De zéro à champion du monde » : personnages pixel dessinés avec contour, tribunes pleines, pelouse, rue de nuit, chambre, cartes FIFA, gros sous-titres en haut avec mots-clés en couleur, en-tête d’épisode) — mêmes formats que la série papier (storytime, tactique, quiz, devine…) et refaire en pixel une vidéo déjà faite. Moteur engine/pixelart.py, modèle episodes/rabiot_px. Utilise ce skill dès que l’utilisateur parle de pixel, pixel.fc, pixel art, rétro, 8-bit / 16-bit, « version pixel », même s’il ne dit pas « skill ».
---

# pixel.fc — VRAI pixel-art (v2, validé par l'utilisateur sur ses vidéos de référence)

⚠️ La v1 (pixeliser nos vidéos papier : `engine/pixel.py`, `PIXEL=1`, `scripts/pixelize_video.py`) a été REJETÉE (« t'as pas bien bossé »).
Le style voulu = celui des vidéos « De zéro à champion du monde » (@remi_sport) : décors et personnages DESSINÉS en pixel-art, pas filtrés.

## Le style de référence
- Petits personnages pixel avec **contour sombre 1 px** et ombrage 2 tons, cheveux / peau / maillot du club, numéro dans le dos, poses
  (debout, marche 2 images, frappe, bras levés, triste, en colère), vus de face ou de dos ; gros plans = même sprite ×2.
- Décors détaillés : tribune pleine de supporters qui sautent, pelouse rayée, cages en filet, rue de nuit aux fenêtres allumées,
  chambre / bureau, vestiaire, documents (contrat, liste), cartes « FIFA » (note + poste, fond coloré), coupe, tableau d'affichage.
- Interface en haute définition PAR-DESSUS le pixel-art : en-tête d'épisode en petite police pixel (« LES HISTOIRES · RABIOT »,
  2e partie en jaune) et **gros sous-titres en haut de l'écran** (Lilita One, blanc avec ombre, mots-clés en couleur : rouge = drame,
  jaune = chiffre / nom, vert = positif, bleu = club), qui apparaissent au fil de la voix (2 lignes max).
- Étiquettes dans la scène en police pixel (Silkscreen) sur boîte sombre ; **jamais d'étiquette au-dessus de y≈70 (canevas)** :
  la zone haute est réservée aux sous-titres.
- Transitions : la nouvelle scène pousse l'ancienne (glissé de gros pixels, 0,2 s). Pas de musique, peu de bruitages.
- Concept fort du compte de référence : série interactive (« Ép. 1 », vote des abonnés : « écris PASSE ou TIR en commentaire,
  seuls les votes décident de l'épisode 2 »). À proposer pour une série pixel.fc (ex. « De zéro à champion », carrière d'un joueur fictif).

## Le moteur : `engine/pixelart.py`
- Canevas logique `LW×LH = 135×240`, agrandi ×8 (`upscale`) → 1080×1920 sans flou. Tout se dessine en coordonnées de gros pixels.
- `person(kit, skin, hair, hstyle, pose, back, num, frame, mood, gender)` → sprite 18×30 (ancre bas-centre) ; kits dans `KITS`
  (psg, om, juve, milan, france, real, rennes, suit, training… en ajouter au besoin : shirt / band / stripes / shorts / socks / num).
- Décors : `stadium`, `crowd`, `pitch`, `goal`, `night_city`, `room`, `lockers`, `bench`. Objets : `paper_doc`, `envelope`, `laptop`,
  `cup`, `card`, `scoreboard`, `heart`, `sparkle`, `dust_cloud`, `ball_spr`, `plabel` / `ptext` (police pixel).
- Interface HD : `header(im, "LES HISTOIRES ·", "SUJET")`, `caption_top(im, WD, t, y, EMPH)` avec `WD = karaoke.Words(lignes, voix)`
  (minutage au mot près par faster-whisper) et `EMPH = {karaoke.norm(mot): couleur}`.
- Modèle complet : `episodes/rabiot_px/rabiot_px.py` (11 scènes, une par phrase, rendu en < 1 min). Réutilise la voix d'un épisode existant
  (0 crédit) ou une nouvelle voix Léo (ElevenLabs, `eleven_v4`, une prise, une phrase par ligne).

## Refaire une vidéo déjà faite en pixel.fc
1. Reprendre son `TEXTE_VOIX.txt` et sa voix (`voix/voix.mp3` + `.mots.json`).
2. Copier `episodes/rabiot_px/rabiot_px.py`, écrire une fonction de scène par phrase avec les éléments de `pixelart`, mots-clés dans `EMPH`.
3. Planche (`--stills`) → vérifier : sous-titres jamais recouverts, personnages assez grands (×2 en plan principal), image 0 forte.
4. Rendu, couvertures 3:4 et 4:3 (image pixel + titre), description + commentaire épinglé, commit + push.
Règles de fond (hook, rythme, boucle, partage, pas de musique) : `.claude/skills/tiktok-foot-viral/SKILL.md`.
