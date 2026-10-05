---
name: tiktok-foot-legendes
description: Crée des vidéos TikTok « Légendes du foot » (1080x1920, format court ~1 min 15 ou long ~2 min) qui racontent la vie d'un footballeur ou l'histoire d'un club (enfance, galères, anecdotes, contrats, records, transferts) dans un style papier déchiré / gouache / stop-motion : joueur en papier découpé qui grandit et change de maillot, transitions en déchirure de papier, tampons, compteurs, confettis, voix off ElevenLabs et vrais bruitages. Utilise ce skill dès que l'utilisateur demande l'histoire, la bio, les anecdotes ou les contrats d'un joueur ou d'une joueuse (« fais Ronaldo », « l'histoire de Zidane », « épisode sur Mbappé »), ou d'un club (« fais l'histoire de Le Mans », « l'histoire du PSG »), ou de finir un épisode en attente de voix, même s'il ne dit pas « skill ».
---

# TikTok « Légendes du foot » — motion design papier

Adaptation du skill `tiktok-edu-motion` (vidéos éducatives) aux **histoires de footballeurs**.
Même identité visuelle (papier déchiré, gouache, boil stop-motion), **en plein écran, sans la barre de fenêtre façon Mac en haut**
(ni pastilles ni titre `~/légendes $ ./<joueur>` : l'utilisateur n'en veut plus), **sans la mascotte Pixel** (le joueur est le seul personnage récurrent),
avec un kit football (`engine/foot.py`) et des effets en plus (`engine/engine.py`).

Épisodes de référence : `episodes/ronaldo/ronaldo.py` et `episodes/zidane/zidane.py` (**les modèles à suivre** : 12 scènes, ~1 min 45, montage nerveux),
`episodes/om/om.py` pour **l'histoire d'un club** (pas de joueur fil rouge : un joueur « générique » au maillot du club + les légendes du club),
et `episodes/messi/messi.py` (9 scènes, 2 min 03, plus posé).

## Livrables (toujours, sans s'arrêter au storyboard)
Dans `output/<joueur>/` :
1. `<slug>.mp4` : vidéo finale, voix off + bruitages, sans musique (l'utilisateur ajoute un son tendance sur TikTok).
2. `<slug>_sans_voix.mp4` : bruitages seuls.
3. `<slug>_couverture.jpg` : couverture accrocheuse et lisible en miniature, sans mentir.
   **Varier la mise en page d'un épisode à l'autre**. Les épisodes 1 à 7 suivent tous le même gabarit (fond à rayons, titre, joueur bras levés,
   bandeau « l'histoire folle de… ») et l'utilisateur le trouve répétitif. Préférer une **question qui fait débat** (« LE PLUS GRAND CLUB DE FRANCE ?
   …ET D'EUROPE ?! ») et une composition propre au sujet. Exemple, PSG (`cover()` dans `episodes/psg/psg.py`) : question en lettres découpées façon lettre
   anonyme (`ransom_line`, dans `engine/story.py`), nuit + projecteur, joueur couronné sur un podium « PSG », 2e et 3e marches « ? ». Le nom du club doit rester lisible,
   et le texte important doit tenir dans le cadre 3:4 de la grille du profil (y ≈ 240 à 1680).
4. `<slug>_voix_off.txt` : script voix off complet (généré par `render_episode`).
5. `<slug>_script.md` : minutage, ce qu'on voit, carte des transitions, légende TikTok, hashtags, **sources**.

## Installation (conteneur vierge)
```bash
bash scripts/setup.sh        # Pillow, numpy, ffmpeg, polices Google Fonts -> /tmp/edu-assets
```

## Méthode
> **Carrousel photo** (mode photo TikTok, 8 images 9:16) : voir `episodes/liverpool/carrousel.py` et `output/liverpool/carrousel/carrousel_guide.md` (1re slide = accroche, une date par slide, dernière = question + CTA ; contenu entre y 180 et 1 420).
> Format **quiz** (« T'es un vrai fan de X si tu as plus de 5/8 », 8 QCM, chrono 5 s) : skill dédié `.claude/skills/tiktok-foot-quiz/SKILL.md`, moteur `engine/quiz.py`.

1. **Recherche d'abord** (web_search) : dates, clubs, chiffres des contrats, records, anecdotes. Tout chiffre à l'écran doit avoir une source dans le `_script.md`.
   Pour les événements récents (moins d'un an), vérifier deux sources ; si elles divergent, formuler sans le chiffre (« le plus titré », « ancien record : Klose, 16 »).
2. **Un fil rouge** qui fait tenir l'histoire (Messi : « trop petit » à 10 ans → le plus grand). L'accroche l'annonce, la dernière scène y répond.
3. **8 à 10 scènes**, chacune avec une anecdote ou un chiffre fort :
   accroche → enfance / origines → galère ou obstacle → le déclic (recrutement, anecdote de contrat) → éclosion (débuts, 1er but, numéro)
   → sommet (records, trophées) → argent / transfert / polémique → quête du trophée manquant → aujourd'hui + appel à s'abonner (et « prochaine légende ? » en commentaire).
4. **Voix off** ~380-420 mots (≈ 2 min avec une voix dynamique). Phrases courtes, tutoiement, suspense (« Son premier but ? … »).
   Nombres et dates **en toutes lettres**, pas de symboles (%, €) dans le texte parlé.
5. **Textes à l'écran** = commentaires courts (date, chiffre, nom), jamais la transcription. Titre en haut (y≈330), étiquettes entre y 450 et 1500. Zone sûre TikTok : rien d'important sous y≈1550 ni à droite de x≈930, ni au-dessus de y≈150 (onglets de l'appli).
6. **Carte des transitions** avant de coder : alterner continuités (l'objet de fin devient l'objet suivant) et déchirures (`Scene(trans="tear_v" | "tear_h" | "tear_d")`, 5-6 par épisode au plus). Une scène suivie d'une déchirure garde sa composition jusqu'au bout (pas d'animation de sortie).

## Rétention (ce qui marche, appliqué dans l'épisode Ronaldo)
- **Accroche en devinette** : dès la 1re image, un titre (« QUI EST-CE ? ») + la silhouette noire du joueur + 3 indices qui claquent
  (le plus surprenant d'abord), puis « Tu l'as reconnu ? ». La révélation ouvre la scène 2 (flash + zoom, célébration du joueur).
- **Ou accroche « cold open »** (épisode Zidane) : ouvrir sur le moment le plus fort de la carrière (le coup de tête de 2006),
  arrêt sur image en noir et blanc (`grayscale`, seul le carton reste en couleur) + « COMMENT ?! », puis **rembobinage VHS**
  (`vhs()` : balayage, bande de tracking, ◀◀ REW, compteur d'années qui recule, la scène rejouée à l'envers) jusqu'à la naissance.
  La scène « fatale » revient plus tard dans l'ordre chronologique, avec le contexte.
- **Ou accroche « titre choc »** (épisode OM) : le titre en deux temps (« CHAMPION D'EUROPE… » dès la 1re image, puis « …PUIS EN D2 ?! »),
  un objet qui claque à l'image 0 (coupe géante, rayons, flashs), puis le retournement visuel (noir et blanc, `elevator_drop()` + `floor_panel()`),
  et un rappel du même effet plus tard dans l'histoire (l'ascenseur revient au moment de la relégation).
- **Ou devinette par les âges** (épisode Neymar) : « À 4 MOIS… / À 25 ANS… / À 34 ANS… » sur la silhouette, un indice visuel par âge
  (voiture accidentée, compteur 222 000 000 €, larmes). Boucler l'histoire sur un lieu (le stade de son 1er but = celui de son dernier match)
  avec un flashback en `old_film()`.
- **Ou « de la cave au sommet »** (épisode Le Mans, un club) : « FAILLITE EN 2013… » dès la 1re image, l'ascenseur tombe en D6
  (`elevator_drop()` + `floor_panel()`), puis « 13 ANS PLUS TARD… » il remonte étage par étage (`shaft(cv, fr, t, speed)` : étages qui
  défilent vers le bas + `floor_panel(..., down=False)` qui affiche D5, D4, D3, L2…) jusqu'à « L1 », et finir l'accroche sur une surprise
  (« parmi ses actionnaires… Novak Djokovic »). L'afficheur sert de fil rouge à chaque montée / descente de l'histoire.
- **Épisode demandé par un abonné** : le dire dans la description, en commentaire épinglé et à la fin (« c'est un abonné qui l'a demandée…
  alors demande-nous la tienne ») ; la pause du milieu demande alors « ton club de cœur ? » pour alimenter les prochains épisodes.
- **Format court** (épisode Dijon, quand les vues décrochent vers 20 s) : ~1 min 15, 9 scènes de 6 à 10 s, phrases de 12 mots max,
  un nouveau plan toutes les ~1,5 s (`shots(..., d=.24)`, `pad_in=.12`, `pad_out=.25`), zoom `drift(cv, t, T, .05)`.
  Le nom du club / de la ville doit se lire **dès la 1re image et sur la couverture** (« DIJON » géant + un objet symbole : pot de moutarde).
  Promettre la durée dans l'accroche (« l'histoire du DFCO en une minute ») et afficher une barre chrono en haut (`chrono_bar()` dans `dijon.py`,
  à y≈176 sous les onglets TikTok), qui se remplit sur toute la vidéo. Annoncer les 3 retournements dès les 9 premières secondes.
- **Présenter un club avec un fil rouge d'objet** (épisode Liverpool) : un objet qui raconte l'origine (la **facture de loyer** d'Anfield « 100 £ → 250 £ »
  + tampon « IMPAYÉ ») ouvre la vidéo avec « LIVERPOOL » en énorme, et revient à la fin avec les tampons « 6 COUPES D'EUROPE » / « 20 TITRES ».
  Couverture sans le gabarit habituel : nom du club, bande « NÉ D'UNE DISPUTE DE LOYER… », la facture, bande « …6 FOIS CHAMPION D'EUROPE ?! », les 6 coupes.
  Avec une actualité récente (entraîneur remercié, nouveau coach), vérifier deux sources et ne donner aucun motif à l'écran.
  Faits sensibles (Heysel, Hillsborough) : ne pas les traiter dans un format court et dynamique, le dire dans le script.
- **Ou CTA « like + abonne-toi pour plus d'épisodes »** (épisode PSG, à la demande) : même pause polaroid, mais un gros bouton cœur
  qui s'enfonce (petits cœurs qui s'envolent, compteur qui grimpe : `like_button()` dans `psg.py`) puis « + ABONNE-TOI » ; le redire à la fin.
  `chrono_bar(cv, fr, SCENES)` est dans `story.py` (à appeler à la fin de chaque scène, et dans le `post` de la pause).
- **Appel à commenter au milieu** (~50 % de la vidéo, juste après un moment fort) : scène courte (5 s) avec `trans="polaroid"` +
  `trans_dur=99` (l'image se fige en photo noir et blanc épinglée, scratch de vinyle), « Quel joueur tu veux voir ? »,
  cartes de joueurs, bulle qui s'écrit, flèche vers le bouton commentaire, puis « Allez, on reprend ! ».
- **Fin** : question oui/non liée à l'actualité du joueur (« il va atteindre les 1000 buts ? ») + bouton « + ABONNE-TOI » qui s'enfonce.
- **Rythme** : un changement visuel toutes les 1,5-3 s. Plusieurs plans par scène (`shots()`), un fond de couleur par plan
  (`stage_fill`), un mot clé à l'écran sur chaque info (`kw()`), zoom caméra continu (`drift()`), glitch sur les moments durs.
  Marges voix courtes : `pad_in=0.15`, `pad_out=0.3`.

## Montage calé sur la voix (`engine/story.py`)
- `align_words(voix.mp3, texte)` donne le minutage de chaque mot (pauses de la voix appariées à la ponctuation + syllabes, ±0,15 s),
  sans modèle de reconnaissance (Hugging Face est bloqué dans le conteneur). `align_episode()` l'enregistre dans `alignement.json`.
- Dans une scène : `w(i, "mot", n)` = instant où le n-ième mot commençant par « mot » est prononcé (attention aux préfixes :
  « marque » trouve d'abord « marquer », « Ronald » trouve « Ronaldo » → préciser `n`).
- `shots(cv, fr, t, [(t0, plan_a), (t1, plan_b), …])` : plusieurs plans dans une scène, filé avec flou de mouvement entre eux.
- Transitions de scène : `tear_v` / `tear_h` / `tear_d` (déchirure), `whip` (filé), `punch` (flash + zoom), `polaroid` (arrêt sur image).

## Kit football (`engine/foot.py`)
- `Player(key)` : joueur articulé. `draw(cv, fr, x, y_pieds, s, age=0..1, kit=..., beard=, arms=(g, d), legs=(g, d), mood=, tears=, look=)`.
  `age` 0 = 10 ans / 1,27 m, 1 = adulte / 1,70 m à la même échelle : **animer `age` pour le faire grandir** contre la toise (`toise_sprite(483)`, `PX_M = 483` à s=1.3).
  `arms` : ouverture vers l'extérieur en degrés (0 = le long du corps, 165 = bras au ciel). `mood` : normal, happy, cheer, sad, surprised, determined.
- `Player(key, hair=, skin=, hair_style="short"|"quiff"|"bald"|"mullet"|"mohawk")` : teint et coiffure par joueur (`bald` : crâne rasé ; l'enfant garde ses cheveux,
  et `kid_hair=True` force les cheveux sur un ado plus âgé). `beard=True` + `beard_col=` pour la barbe.
- `KITS` : newells, barca, psg, arg, miami, street, suit, coach, sporting, manutd, real, portugal, alnassr, madeira,
  france, france_w (blanc), italy, brazil, saudi, juventus, cannes, gk (gardien), ref (arbitre), om, milan, redstar, valenciennes,
  santos, alhilal, norway, lemans (rouge, liseré jaune), guingamp (rouge et noir), chelsea, tennis (polo blanc), pilote (combinaison de course) ;
  en ajouter un = une entrée (`plain` / `stripes` / `hoops` / `halves` / `band`). Jamais d'écusson ni de logo de club ou de marque.
- `silhouette()` (devinette), `UCL` (coupe aux grandes oreilles).
- Changer de maillot : `spin_player` / `render_layer` + `blit_sxy` (tour sur lui-même), ou déchirer l'ancien maillot (`jersey_front` + `tear_split`).
- Objets : `draw_ball`, `draw_goal(net_u=)`, `CUP`, `WC_TROPHY`, `WC_SIL`, `BALLON_OR`, `jersey_back(kit, "NOM", n)`, `price_tag`, `scoreboard_sprite`, `pencil_check` / `pencil_cross`, `Granny`.

## Effets (`engine/engine.py`)
`tear_transition` (automatique via `Scene(trans=…)`), `tear_split(image)` (déchirer n'importe quel objet : contrat, maillot),
`shake`, `zoom_punch`, `flash`, `tint` (nuit), `rays`, `speed_lines`, `confetti`, `camera_flashes`, `drops` (larmes), `counter` (compteurs qui défilent),
plus ceux du moteur d'origine (`Paper`, `Label`, `pop_in`, `pencil_line`, `arrow`, `particles`, `regroup`). `Mascot` existe encore dans le moteur mais n'est pas utilisée dans cette série.
`paper_sprite(pattern=…)` peint un motif (rayures) sous la texture papier.
Dans `story.py` : `grayscale(cv, a)` (noir et blanc dosable), `vhs(cv, fr, t)` (rembobinage de cassette), `fr_flag()` (drapeau qui ondule),
`sepia()` / `old_film()` (vieux film : sépia, rayures, poussières), `elevator_drop()` + `floor_panel()` (chute d'étage, afficheur D1 → D2),
`siren_lights()` (gyrophares), `flares()` (fumigènes en tribune), `beam()` (faisceau de lampe / projecteur).
Dans `episodes/lemans/lemans.py` (à copier au besoin) : `race_car()` / `car_pass()` (proto d'endurance qui traverse l'écran avec traînées),
`track()` (bitume + vibreurs), `checkered()` (drapeau à damier), `tricolor()` (drapeau à 3 bandes), `racket()` / `tball()` (tennis),
`ARENA` (stade moderne vu de l'extérieur), `calendar()` (page qui s'arrache), `virus()`, `bricks()` (mur qui se monte), `carton()`, `shaft()` (cage d'ascenseur).

## Voix off et bruitages (ElevenLabs connecté)
- Voix par défaut de la série : **Léo – Energetic & Engaging** (`jsScnYkNNda9Q1NES5nn`), `eleven_multilingual_v2`, dynamique et rythmée. Garder la même d'un épisode à l'autre.
- `creative_create_flow` (un flow par épisode), puis `creative_generate_speech` **une fois par scène** avec `generations_count=1`.
  Récupérer `media[].url` via `creative_get_flow_run_status`, télécharger avec `curl` dans `episodes/<joueur>/voix/scene_N.mp3` (le domaine `storage.googleapis.com` doit être autorisé).
- Caler les animations sur les mots : `ffmpeg -af silencedetect=noise=-35dB:d=0.18` donne les pauses de chaque fichier ; dans la scène, `tv(temps_dans_le_fichier)` = temps local.
- Bruitages : `assets/sfx/*.mp3` (générés une fois avec `eleven_text_to_sound_v2`, ~17 crédits pièce) : rip, crowd (+ `crowd_long` auto), whistle, cash, flash, stamp, whoosh, kick, boom, gavel, plane, groan, heart, riser, sparkle.
  + scratch (vinyle), glitch, notif (commentaire), laser, laugh (rires moqueurs), monitor (moniteur cardiaque),
  rewind (cassette VHS qui rembobine), bar (ballon sur la barre), horn (klaxon), gasp (foule choquée),
  coin (pièce), siren (sirène de police), dig (pelle), jail (porte de prison), bell (sonnette de vélo), elevator (ascenseur qui tombe),
  crash (accident de voiture), samba (batucada, 1 s), race (voiture de course qui passe, effet Doppler : caler le pic au passage au centre),
  tennis (frappe de balle).
  Les bruitages longs (« 4 secondes de chants ») reviennent parfois à 0,5 s : vérifier la durée avec ffprobe et jeter ceux qui sont inutilisables.
  S'y ajoutent les synthétiques : pop, pop2, swish, thud, clink, paper, scribble, whoosh_up, ding, poof, tick.
  `Scene(sfx=[(temps, "nom", gain, durée_max)])` : la durée max coupe un bruitage trop long (fondu de sortie).
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
- **Pas de barre Mac / fenêtre de terminal** : la scène occupe tout l'écran (`STAGE = (0, 0, 1080, 1920)`, `finish()` ne recolle plus de cadre).
  Ne pas la remettre. `LEGENDES_CADRE=1` ne sert qu'à re-rendre à l'identique les épisodes 1 à 5 (Messi, Ronaldo, Zidane, OM, Neymar), publiés avec la barre.
  La variable `TITLE` des épisodes n'est plus affichée.
- Aplats pleine largeur (sol, route, rayures) : utiliser `STAGE` (`sx0, sy0, sx1, sy1 = STAGE`, ou `stripes()` dans `neymar.py`),
  jamais les anciens bords du cadre codés en dur (30, 122, 1050, 1890), sinon des bandes apparaissent au bord de l'écran.
- **Vérifier que les faits n'ont pas changé** : « le seul club français champion d'Europe » n'est plus vrai depuis le PSG en 2025 (« le premier ») ;
  Papin n'est plus le seul Ballon d'Or joué en Ligue 1 (Dembélé, 2025).
- Les polices n'ont ni « → » ni « ★ ✓ ✗ » : dessiner flèches, étoiles, coches (`arrow`, `draw_star`, `pencil_check`).
- Faire rouler / tourner un joueur : `render_layer` a son ancre aux pieds ; pour tourner autour du centre du corps, décaler le point
  d'ancrage (`x + h/2*sin(a)`, `y + h/2*cos(a)`) à chaque image (roulade de Neymar, épisode 5).
- `Words` : `w(i, "but")` trouve aussi « buts », et « Et » trouve un « et » plus tôt dans la phrase (« Messi et Suárez ») : compter les occurrences.
- `Words` : `w(i, "Il", n)` compte aussi les « il » minuscules et `w(i, "coup")` trouve aussi « Coupe » : vérifier l'ordre des mots dans le texte.
- `pkill -f "<motif>"` peut tuer le shell qui le lance (sa ligne de commande contient le motif) : préférer `pgrep` puis `kill <pid>`.
- Ne jamais créer un `Label` / `Paper` dans une fonction de scène (recréé à chaque image = lent) : utiliser `LBL(...)` (cache) pour les compteurs.
- Un décor dessiné hors du polygone d'un `Paper` est coupé : augmenter `pad=`.
- `Words`, autres préfixes piégeux : « quatre-vingt » trouve d'abord « quatre-vingt-dix », « Deux » trouve aussi « deuxième »,
  « demande » trouve « demandée », « Le » trouve tous les « le ». En cas de doute, afficher la liste des mots de `alignement.json` et compter.
- L'aligneur se trompe quand la voix prononce un passage plus bas (noms propres enchaînés : « Gervinho, Sessègnon, Grafite ») :
  tracer l'enveloppe d'énergie (RMS par tranche de 10 ms) et corriger les débuts de mots à la main dans `alignement.json`.
  Pour vérifier le texte réellement dit : `creative_transcribe_audio` avec `connect_from=[node_id du nœud TTS]` (pas de minutage, texte seul).
- `LBL(txt, key, …)` met en cache par (clé, texte) : si la couleur change pour un même texte (ligne de classement surlignée), mettre l'état dans la clé.
- Placer un objet dans la main d'un joueur (raquette, valise, casque, gants) : `hand_pos(x, y, s, côté, angle_du_bras)` dans `lemans.py`.
- Quand les sources se contredisent (nom du 2e club de la fusion de 1985), rester vague à l'écran et le noter dans les précautions du script.
- **Crédits ElevenLabs** : le quota mensuel peut être épuisé (erreur « exceeds your quota » dans `creative_get_flow_run_status`).
  Une voix de ~170 caractères coûte ~170 crédits (`eleven_multilingual_v2`) : vérifier avec `estimate_only=True` avant de lancer un épisode.
  En attendant les voix : minutage provisoire (voix muettes à ~6 syllabes/s + pauses de ponctuation, alignement estimé) dans un dossier
  pointé par `LEGENDES_PROVISOIRE=<dossier avec voix/ et alignement.json>` pour écrire les scènes, sortir planches et couverture ; le rendu final est bloqué.
  Le fabriquer : `python3 scripts/minutage_provisoire.py episodes/<club>/textes_voix.json <dossier>` (textes des voix gardés dans le repo).
- Vérifier le **contexte temporel** : Messi a quitté Paris en 2023, pas « un an plus tard ». Relire le script voix off contre les dates avant de générer l'audio (chaque prise coûte des crédits).
