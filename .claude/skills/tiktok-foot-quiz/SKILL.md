---
name: tiktok-foot-quiz
description: Crée des vidéos TikTok QUIZ foot « T'es un vrai fan de X si tu as plus de 5/8 » (1080x1920, ~1 min 50) dans le style papier découpé / gouache / stop-motion de la série « Légendes du foot » : 8 questions QCM à 4 réponses (A-D), chrono de 5 s qui s'écoule (tic-tac, buzzer), bonne réponse qui passe au vert, illustration papier qui révèle la réponse, CTA « abonne-toi et like » au milieu, barème final, voix off ElevenLabs Léo. Utilise ce skill dès que l'utilisateur demande un quiz, un QCM, un test ou un « t'es un vrai fan de… » sur un club, un joueur, une sélection ou une compétition (« fais le quiz de l'OM », « quiz Real Madrid », « un quiz sur Zidane »), même s'il ne dit pas « skill ». Pour raconter une histoire (biographie, histoire d'un club), utiliser plutôt tiktok-foot-legendes.
---

# Quiz « T'es un vrai fan de X ? » (skill de ce dépôt)

Format demandé par l'utilisateur, à respecter tel quel :
- titre **« T'es un vrai fan de X si tu as plus de 5/8 »** ;
- **8 questions QCM, 4 réponses possibles**, **5 secondes pour répondre**, avec **un chrono qui s'écoule** ;
- **CTA au milieu** (après la question 4) : « abonne-toi et like pour avoir plus de contenu sur ton club préféré » ;
- **même voix** que la série (ElevenLabs « Léo – Energetic & Engaging ») et **même style** que les vidéos d'histoires.

Exemple complet : `episodes/quiz_psg/quiz_psg.py` (+ `textes_voix.json`, `alignement.json`, `voix/`) et `output/quiz_psg/quiz_psg_script.md`.
Moteur du format : `engine/quiz.py` (au-dessus de `engine/engine.py`, `foot.py`, `story.py`). Méthode générale de la série : `SKILL.md` à la racine.
Branche de travail : `claude/footballer-stories-tiktok-h7k2q9`.

## Déroulé d'une vidéo (≈ 1 min 50, 11 scènes)

| Scène | Durée | Contenu |
|---|---|---|
| Intro | ~6 s | « T'ES UN VRAI FAN / DU PSG ? » en lettres découpées + « SI TU AS PLUS DE 5/8 » **dès la 1re image** ; puis « 8 QUESTIONS », « 5 SECONDES » (chrono de démo), « compte tes points ! », « C'EST PARTI ! » |
| Q1 → Q4 | ~10-13 s chacune | voir ci-dessous |
| CTA | ~6 s | « PETITE PAUSE ! », « 4/8 : t'en es à combien ? », bouton « + ABONNE-TOI », gros bouton cœur, « + de contenu sur ton club préféré ! », « ON REPREND ! » |
| Q5 → Q8 | ~10-13 s chacune | Q8 : bandeau « DERNIÈRE QUESTION ! » |
| Fin | ~7 s | « T'AS EU COMBIEN ? », barème 0-3 TOURISTE / 4-5 SUPPORTER / 6-8 VRAI FAN, couronne, bulle « J'ai eu ?/8 ! », « + ABONNE-TOI », « le quiz de ton club ? » |

Une question : « QUESTION 3/8 » + 8 points de progression, sticker de niveau, carte question (2 lignes max), illustration papier,
4 réponses A-D qui arrivent en cascade **pendant** que la voix lit la question. Fin de la lecture → chrono de 5 s
(cadran qui se vide, chiffre 5 → 1, barre vert → jaune → rouge, tic-tac chaque seconde, tremble à la fin) → buzzer + « correct »,
la bonne réponse passe au vert avec ✓, les autres s'éteignent, l'illustration révèle la réponse → la voix donne la réponse.

## Marche à suivre (club X)

1. **Questions** (le plus important) : 8 questions **de la plus facile à la plus dure** (3 FACILE, 3 MOYEN, 1 DIFFICILE, 1 LA PLUS DURE).
   - Chaque fait vérifié sur le web (WebSearch ; fr.wikipedia est souvent bloqué, passer par en.wikipedia, presse, ESPN…), source notée.
   - Mauvaises réponses **plausibles mais fausses à coup sûr** ; de bons pièges (Mbappé 180 M€ quand la question porte sur Neymar,
     1974 = arrivée au Parc et pas la création, Cavani pour le meilleur buteur).
   - Bonne réponse répartie : **deux fois chaque lettre** (ex. B D C A B D C A).
   - Éviter les faits qui bougent (« combien de titres ») sauf avec une date ; préférer les records, dates clés, stades, transferts, finales, anecdotes.
   - Texte à l'écran : question ≤ ~50 caractères (2 lignes), réponses ≤ ~22 caractères.
   - Polices : le titre (Lilita One) n'a pas les lettres d'Europe de l'Est (ć, š, ł…) : écrire « Ibrahimovic », « Modric ».
2. **Voix** : `episodes/quiz_<club>/textes_voix.json`, 19 clés : `intro`, `q1`…`q8`, `r1`…`r8`, `cta`, `outro` (modèle : `episodes/quiz_psg/textes_voix.json`).
   - Nombres et années **en toutes lettres** (« deux mille onze », « deux cent vingt-deux millions »).
   - La voix **ne lit pas les 4 réponses** (trop long) : seulement la question. Réponse : « Réponse B : le Parc des Princes ! » (+ un mot de contexte).
   - Q8 commence par « Dernière question, la plus dure : … ».
   - CTA, mot pour mot : « Petite pause ! Abonne-toi et lâche un like pour avoir plus de contenu sur ton club préféré ! Allez, on reprend ! ».
   - Garder « cinq sur huit », « Huit questions, cinq secondes » dans l'intro et « Plus de cinq : t'es un vrai fan ! » dans la fin.
3. **ElevenLabs** : `creative_create_flow` (un flow par quiz), puis `creative_generate_speech` une fois par clé :
   voix Léo `jsScnYkNNda9Q1NES5nn`, `eleven_multilingual_v2`, `generations_count=1`.
   - ~1 300 crédits par quiz ; tester d'abord l'intro (l'erreur de quota arrive dans `creative_get_flow_run_status`).
   - Lancer par paquets de 4 (au-delà : erreurs 429, à relancer une par une, non facturées).
   - Le statut est énorme : il est sauvé dans un fichier ; le lire en Python, associer chaque `media[].url` à sa clé **par le texte exact** du prompt,
     télécharger avec `curl` dans `episodes/quiz_<club>/voix/<clé>.mp3`.
   - Bruitages du format déjà dans `assets/sfx/` : `tictac` (chrono ; le fichier contient 2 tics à 1 s d'écart, on coupe à 0,45 s), `buzzer`, `correct`.
4. **Alignement** de l'intro, du CTA et de la fin (les questions n'en ont pas besoin : le chrono est calé sur l'audio) :
   ```python
   import sys, json; sys.path.insert(0, "engine"); from story import align_episode
   T = json.load(open("episodes/quiz_<club>/textes_voix.json")); K = ["intro", "cta", "outro"]
   align_episode([f"episodes/quiz_<club>/voix/{k}.mp3" for k in K], [T[k] for k in K], "episodes/quiz_<club>/alignement.json")
   ```
   Vérifier avec `ffmpeg -af silencedetect=noise=-35dB:d=0.12`. Piège des préfixes : `Wd("Huit")` tombe sur « huit ! » de « cinq sur huit » → `Wd("Huit", 2)`.
5. **Épisode** : copier `episodes/quiz_psg/quiz_psg.py` en `episodes/quiz_<club>/quiz_<club>.py` et changer :
   - `TITLE`, `SLUG` ;
   - `THEME` : `du` (« DU PSG », « DE L'OM », « DU REAL »), `accent` et `badge` (couleurs du club), `bgs` (4 fonds qui tournent), `ray2` ;
   - le joueur `hero()` (kit du club, voir `KITS` dans `engine/foot.py`, en ajouter un au besoin) ;
   - les 8 illustrations `iN(cv, fr, t, u, tm)` : `u` = 0 avant la révélation, puis 0 → 1 en 0,45 s ; `tm["te"]` = instant de la révélation.
     **L'illustration ne doit jamais donner la réponse avant la révélation** (stade sans nom, drapeau « ? », silhouette noire, tableau « ??? 6-1 »…).
     Zone utile : y ≈ 700 à 1030 autour de `ILLU_Y` ; ne pas mordre sur le chrono (y ≈ 652) ni sur les réponses (y ≥ 1036).
   - `QUESTIONS = [Q(texte, [4 réponses], index_bonne, niveau, illustration, bruitages_révélation), …]`.
6. **Planches** : `python3 episodes/quiz_<club>/quiz_<club>.py output/quiz_<club> --stills` (une planche par scène ; pour une question :
   début, fin de la lecture, chrono à 4 puis à 1, révélation, réponse, fin). Les regarder toutes : chevauchements, texte trop long, réponse visible trop tôt.
7. **Rendu** : `python3 episodes/quiz_<club>/quiz_<club>.py output/quiz_<club>` (~12 min sur 4 cœurs).
   `render_episode(..., limit=True)` : les 40 s de chrono presque muettes font plafonner la normalisation vers -15,5 LUFS ;
   le limiteur ramène à ≈ -14,5 LUFS. Pour corriger seulement le son d'une vidéo déjà rendue : `render_episode(..., audio_only=True)`
   puis remettre l'audio sur l'image avec `ffmpeg -c:v copy` (pas besoin de tout re-rendre).
   Formes qui démarrent à une taille ≈ 0 (pop_in) : garder un seuil (`if a <= .2: return`) sinon PIL plante (« y1 must be greater than y0 »).
8. **Vérifier** :
   - la voix de chaque scène dans le mp4 (corrélation avec `/tmp/quiz_<club>_voix/scene_N.wav` pour les questions, `voix/intro.mp3`… sinon) ;
   - ≈ -14 LUFS (`ebur128`), stéréo 48 kHz (`ffprobe`) ;
   - une grille d'images (`ffmpeg -vf "fps=1/3,scale=216:384,tile=9x4"`).
9. **Couverture** : `--cover` (question en lettres découpées, « PLUS DE 5/8 ? », tampon QUIZ, chrono, 4 réponses dont une verte).
   Le nom du club doit se lire en miniature ; texte important dans le cadre 3:4 de la grille du profil (y ≈ 240 à 1680).
10. **Script** `output/quiz_<club>/quiz_<club>_script.md` (modèle : `output/quiz_psg/quiz_psg_script.md`) : format, déroulé avec temps
    (débuts de scène = cumul des durées affichées par le rendu), bonnes réponses, description TikTok, commentaire à épingler
    (« Ton score sur 8 ? Et quel club pour le prochain quiz ? »), **sources**, précautions.
11. **Finir** : ligne dans le tableau « Quiz » du `README.md`, `bash scripts/build_quiz_skill.sh`, commit + push,
    envoyer le mp4 **avec voix**, la couverture et le script (jamais la version `_sans_voix`).

## Repères de mise en page (1080×1920)
- Haut : onglets de l'appli TikTok jusqu'à y ≈ 200 → « QUESTION n/8 » à y = 248, points à y = 330.
- Droite : colonne d'icônes TikTok (x > 960, y ≈ 900-1550) → les réponses sont décalées à gauche (centre x = 495, de 65 à 925).
- Bas : légende TikTok à partir de y ≈ 1600 → rien d'important dessous.
- Constantes dans `engine/quiz.py` : `CARD_Y` 478, `TIMER_Y` 652, `ILLU_Y` 862, `ANS_Y0` 1090, `ANS_DY` 126, `CHRONO` 5 s.

## Variantes faciles
- Seuil : `THEME["seuil"]` (5 par défaut → « plus de 5/8 », barème 0-3 / 4-5 / 6-8).
- Quiz joueur (« t'es un vrai fan de Zidane ? ») : même chose, `du` = « DE ZIDANE », `hero()` = le joueur avec son kit.
- CTA après une autre question : `assemble(..., cta_after=k)` et `cta_scene(theme, Wd, after=k)`.
- **CTA « dis ton score en commentaire + abonne-toi pour le niveau 2 »** (quiz OM, après la Q3) : `assemble(..., cta_after=3)`,
  `cta_score_scene(theme, Wd, after=3)` (texte voix : « Petite pause ! T'en es à combien sur trois ? Dis ton score en commentaire, lâche un like
  et abonne-toi pour le niveau deux ! Allez, on reprend ! ») et `outro_scene(..., tag="le niveau 2 arrive bientôt !")` ; sticker
  `THEME["niveau"] = THEME["tampon"] = "NIVEAU 1"`. Exemple : `examples/quiz_om/`.
- **Niveau 2 (plus dur)** : `THEME["niveau"] = "NIVEAU 2"` (sticker sur l'intro) et `THEME["tampon"] = "NIVEAU 2"` (tampon de la couverture).
  Aucune question facile (MOYEN → LA PLUS DURE), des pièges plausibles (la 1re Coupe au lieu du 1er titre, le coach arrivé six mois après…),
  illustrations « silhouette noire + ? » ou tableau « ??? ». Le CTA et la fin gardent le même texte : réutiliser les voix du quiz 1
  (et leurs mots dans `alignement.json`), aucun crédit dépensé. Exemple : `examples/quiz_psg2/`.

## Crédits ElevenLabs épuisés
Tout préparer quand même avec un minutage provisoire, puis finir dès qu'il y a des crédits :
`python3 scripts/minutage_provisoire_quiz.py episodes/quiz_<club> <dossier>` (silences de la durée estimée pour les voix manquantes,
vraies voix sinon), puis `LEGENDES_PROVISOIRE=<dossier> python3 episodes/quiz_<club>/quiz_<club>.py <sortie> --stills | --apercu`.
Le rendu final est bloqué tant que la variable est définie. Avec les crédits : générer les voix manquantes, refaire `alignement.json`
avec les vraies voix (étape 4), planches, rendu, vérifications.

## Description TikTok qui fait commenter (À CHAQUE LIVRAISON, demandé par l'utilisateur)
Toujours donner dans la réponse finale (et dans le `_script.md`) une description prête à coller + un commentaire à épingler.
**COURTE** (l'utilisateur a trouvé la 1re version trop longue) : 2 lignes max + 5 hashtags.
- Ligne 1 = le fait choc, 1-2 émojis. Ligne 2 = une question à réponse courte et clivante (OUI / NON, un nom, un score) + 👇.
- Hashtags : club / sujet + #football #foot (+ #quizfoot pour un quiz).
- Commentaire à épingler : une seule phrase, une 2e question pour relancer.
