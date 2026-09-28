---
name: tiktok-foot-legendes
description: Crée des vidéos TikTok « Légendes du foot » (1080x1920, ~1 min 30 – 2 min) qui racontent la vie d'un footballeur (enfance, galères, anecdotes, contrats, records, transferts) dans un style papier déchiré / gouache / stop-motion : joueur en papier découpé qui grandit et change de maillot, transitions en déchirure de papier, tampons, compteurs, confettis, voix off ElevenLabs et vrais bruitages. Utilise ce skill dès que l'utilisateur demande l'histoire, la bio, les anecdotes ou les contrats d'un joueur ou d'une joueuse (« fais Ronaldo », « l'histoire de Zidane », « épisode sur Mbappé »), même s'il ne dit pas « skill ».
---

# TikTok « Légendes du foot » — motion design papier

Adaptation du skill `tiktok-edu-motion` (vidéos éducatives) aux **histoires de footballeurs**.
Même identité visuelle (papier déchiré, gouache, boil stop-motion, fenêtre de terminal `~/légendes $ ./<joueur>`), **sans la mascotte Pixel** (le joueur est le seul personnage récurrent),
avec un kit football (`engine/foot.py`) et des effets en plus (`engine/engine.py`).

Épisode de référence : `episodes/messi/messi.py` (9 scènes, 2 min 03).

## Livrables (toujours, sans s'arrêter au storyboard)
Dans `output/<joueur>/` :
1. `<slug>.mp4` : vidéo finale, voix off + bruitages, sans musique (l'utilisateur ajoute un son tendance sur TikTok).
2. `<slug>_sans_voix.mp4` : bruitages seuls.
3. `<slug>_couverture.jpg` : couverture accrocheuse et lisible en miniature, sans mentir.
4. `<slug>_voix_off.txt` : script voix off complet (généré par `render_episode`).
5. `<slug>_script.md` : minutage, ce qu'on voit, carte des transitions, légende TikTok, hashtags, **sources**.

## Installation (conteneur vierge)
```bash
bash scripts/setup.sh        # Pillow, numpy, ffmpeg, polices Google Fonts -> /tmp/edu-assets
```

## Méthode
1. **Recherche d'abord** (web_search) : dates, clubs, chiffres des contrats, records, anecdotes. Tout chiffre à l'écran doit avoir une source dans le `_script.md`.
   Pour les événements récents (moins d'un an), vérifier deux sources ; si elles divergent, formuler sans le chiffre (« le plus titré », « ancien record : Klose, 16 »).
2. **Un fil rouge** qui fait tenir l'histoire (Messi : « trop petit » à 10 ans → le plus grand). L'accroche l'annonce, la dernière scène y répond.
3. **8 à 10 scènes**, chacune avec une anecdote ou un chiffre fort :
   accroche → enfance / origines → galère ou obstacle → le déclic (recrutement, anecdote de contrat) → éclosion (débuts, 1er but, numéro)
   → sommet (records, trophées) → argent / transfert / polémique → quête du trophée manquant → aujourd'hui + appel à s'abonner (et « prochaine légende ? » en commentaire).
4. **Voix off** ~380-420 mots (≈ 2 min avec une voix dynamique). Phrases courtes, tutoiement, suspense (« Son premier but ? … »).
   Nombres et dates **en toutes lettres**, pas de symboles (%, €) dans le texte parlé.
5. **Textes à l'écran** = commentaires courts (date, chiffre, nom), jamais la transcription. Titre en haut (y≈330), étiquettes entre y 450 et 1500. Zone sûre TikTok : rien d'important sous y≈1550 ni à droite de x≈930.
6. **Carte des transitions** avant de coder : alterner continuités (l'objet de fin devient l'objet suivant) et déchirures (`Scene(trans="tear_v" | "tear_h" | "tear_d")`, 5-6 par épisode au plus). Une scène suivie d'une déchirure garde sa composition jusqu'au bout (pas d'animation de sortie).

## Kit football (`engine/foot.py`)
- `Player(key)` : joueur articulé. `draw(cv, fr, x, y_pieds, s, age=0..1, kit=..., beard=, arms=(g, d), legs=(g, d), mood=, tears=, look=)`.
  `age` 0 = 10 ans / 1,27 m, 1 = adulte / 1,70 m à la même échelle : **animer `age` pour le faire grandir** contre la toise (`toise_sprite(483)`, `PX_M = 483` à s=1.3).
  `arms` : ouverture vers l'extérieur en degrés (0 = le long du corps, 165 = bras au ciel). `mood` : normal, happy, cheer, sad, surprised, determined.
- `KITS` : newells, barca, psg, arg, miami, street, suit, coach ; en ajouter un = une entrée (`plain` / `stripes` / `halves` / `band`). Jamais d'écusson ni de logo de club ou de marque.
- Changer de maillot : `spin_player` / `render_layer` + `blit_sxy` (tour sur lui-même), ou déchirer l'ancien maillot (`jersey_front` + `tear_split`).
- Objets : `draw_ball`, `draw_goal(net_u=)`, `CUP`, `WC_TROPHY`, `WC_SIL`, `BALLON_OR`, `jersey_back(kit, "NOM", n)`, `price_tag`, `scoreboard_sprite`, `pencil_check` / `pencil_cross`, `Granny`.

## Effets (`engine/engine.py`)
`tear_transition` (automatique via `Scene(trans=…)`), `tear_split(image)` (déchirer n'importe quel objet : contrat, maillot),
`shake`, `zoom_punch`, `flash`, `tint` (nuit), `rays`, `speed_lines`, `confetti`, `camera_flashes`, `drops` (larmes), `counter` (compteurs qui défilent),
plus ceux du moteur d'origine (`Paper`, `Label`, `pop_in`, `pencil_line`, `arrow`, `particles`, `regroup`). `Mascot` existe encore dans le moteur mais n'est pas utilisée dans cette série.
`paper_sprite(pattern=…)` peint un motif (rayures) sous la texture papier.

## Voix off et bruitages (ElevenLabs connecté)
- Voix par défaut de la série : **Léo – Energetic & Engaging** (`jsScnYkNNda9Q1NES5nn`), `eleven_multilingual_v2`, dynamique et rythmée. Garder la même d'un épisode à l'autre.
- `creative_create_flow` (un flow par épisode), puis `creative_generate_speech` **une fois par scène** avec `generations_count=1`.
  Récupérer `media[].url` via `creative_get_flow_run_status`, télécharger avec `curl` dans `episodes/<joueur>/voix/scene_N.mp3` (le domaine `storage.googleapis.com` doit être autorisé).
- Caler les animations sur les mots : `ffmpeg -af silencedetect=noise=-35dB:d=0.18` donne les pauses de chaque fichier ; dans la scène, `tv(temps_dans_le_fichier)` = temps local.
- Bruitages : `assets/sfx/*.mp3` (générés une fois avec `eleven_text_to_sound_v2`, ~17 crédits pièce) : rip, crowd (+ `crowd_long` auto), whistle, cash, flash, stamp, whoosh, kick, boom, gavel, plane, groan, heart, riser, sparkle.
  S'y ajoutent les synthétiques : pop, pop2, swish, thud, clink, paper, scribble, whoosh_up, ding, poof, tick.
  `Scene(sfx=[(temps, "nom", gain)])` ; les bruitages sont baissés automatiquement sous la voix (ducking).
- Mixage : `render_episode(..., sfx_db=7, lufs=-14)` : la voix est ramenée à un niveau fixe, le bus bruitages est calé 7 dB dessous,
  puis loudnorm EBU R128 en deux passes à -14 LUFS (niveau TikTok). Sans ça, les bruitages ElevenLabs (normalisés à fond) écrasent la voix.
- Sans ElevenLabs : voix Piper hors-ligne (voir `tiktok-edu-motion`) et toujours livrer `_voix_off.txt` + `_sans_voix.mp4`.

## Rendu
```bash
python3 episodes/<joueur>/<joueur>.py output/<joueur> --stills         # planches de contrôle (7 images par scène)
python3 episodes/<joueur>/<joueur>.py output/<joueur> --stills 3,4     # seulement certaines scènes
python3 episodes/<joueur>/<joueur>.py output/<joueur> --cover
nohup python3 episodes/<joueur>/<joueur>.py output/<joueur> > render.log 2>&1 &   # ~8-10 min pour 2 min sur 4 cœurs (x264 slow, crf 25 ≈ 35 Mo)
```
**Toujours regarder les planches** avant le rendu complet : chevauchements (titre sur 2 lignes), objets hors de la zone sûre, étiquettes illisibles.
**Toujours vérifier que la voix est dans le .mp4 final** (corrélation avec `voix/scene_1.mp3`, ou écoute) et n'envoyer que la version avec voix : la version `_sans_voix` prête à confusion.

## Pièges connus
- Les polices n'ont ni « → » ni « ★ ✓ ✗ » : dessiner flèches, étoiles, coches (`arrow`, `draw_star`, `pencil_check`).
- Ne jamais créer un `Label` / `Paper` dans une fonction de scène (recréé à chaque image = lent) : utiliser `LBL(...)` (cache) pour les compteurs.
- Un décor dessiné hors du polygone d'un `Paper` est coupé : augmenter `pad=`.
- Vérifier le **contexte temporel** : Messi a quitté Paris en 2023, pas « un an plus tard ». Relire le script voix off contre les dates avant de générer l'audio (chaque prise coûte des crédits).
