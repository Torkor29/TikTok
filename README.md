# Légendes du foot — TikTok en papier découpé

Vidéos TikTok verticales qui racontent l'histoire des footballeurs (enfance, anecdotes, contrats, records),
en style papier déchiré / gouache / stop-motion, avec voix off et bruitages ElevenLabs.
Moteur repris et étendu du skill `tiktok-edu-motion` : voir [`SKILL.md`](SKILL.md) pour la méthode complète.

## Épisodes

| # | Joueur | Durée | Fichiers |
|---|---|---|---|
| 1 | Lionel Messi — « trop petit » → le plus grand | 2:03 | [`output/messi/`](output/messi) |
| 2 | Cristiano Ronaldo — opéré du cœur à 15 ans → 6 Coupes du monde (accroche devinette, pause « quel joueur ? » au milieu, montage nerveux) | 1:49 | [`output/ronaldo/`](output/ronaldo) |
| 3 | Zinédine Zidane — carton rouge à son dernier match → sélectionneur des Bleus (ouverture sur le coup de tête, rembobinage VHS, panenka au ralenti) | 1:46 | [`output/zidane/`](output/zidane) |
| 4 | L'Olympique de Marseille — champion d'Europe… puis en D2 (histoire d'un club : chute d'ascenseur D1 → D2, vieux film 1899, affaire VA-OM, team OM ou team PSG ?) | 1:43 | [`output/om/`](output/om) |
| 5 | Neymar — 222 millions… génie ou gâchis ? (devinette par les âges, remontada minute par minute, 14 min au sol, fin au Mondial 2026 dans le stade de son 1er but) | 1:56 | [`output/neymar/`](output/neymar) |
| 6 | Le Mans FC — faillite en 2013… Ligue 1 en 2026 ?! (demandé par un abonné ; plein écran sans barre : ascenseur D6 → L1, Drogba ×300, usine à pépites, Djokovic actionnaire, montée validée malgré les fumigènes) | 2:02 | [`output/lemans/`](output/lemans) |
| 7 | Dijon FCO — a battu le PSG… puis la 3e division ?! (format court ~1 min 15 avec barre chrono, « DIJON » + moutarde dès la 1re image, poulet Gaston Gérard, Dijon 2-1 PSG, chute en National, retour en L2) | 1:11 | [`output/dijon/`](output/dijon) |
| 8 | PSG — envoyé en 3e division… double champion d'Europe ?! (format court avec barre chrono, « PSG » + tour Eiffel dès la 1re image, 20 000 « oui », divorce de 1972, N'Gotty, le Qatar, 5-0 contre l'Inter ; CTA like + abonne-toi) | 1:15 | [`output/psg/`](output/psg) |
| 9 | Liverpool — né d'une dispute de loyer… 6 fois champion d'Europe ?! (présentation du club, format court avec barre chrono, « LIVERPOOL » + facture de loyer dès la 1re image, Everton quitte Anfield, Shankly, YNWA, Istanbul 2005, Klopp, 20e titre ; CTA like + abonne-toi) | 1:13 | [`output/liverpool/`](output/liverpool) |
| 10 | Toulouse FC — en faillite en 2001… et 22 ans plus tard, il bat Liverpool ?! (format court avec barre chrono, « TOULOUSE » sur briques roses dès la 1re image, ascenseur L2 → D3 → L1, 2007 éliminé par Liverpool, Coupe de France 5-1, revanche 3-2 ; carrousel à poster juste avant + descriptions qui font commenter) | 1:01 | [`output/toulouse/`](output/toulouse) |

| Hommage | Lionel Messi dit adieu à l'Argentine (version « ultra détaillée » : gros plans papier aux trois âges, stades de nuit avec foule détaillée, profondeur de champ ; 2005 rouge après 47 s, 2006, 3 finales perdues, 2021-2022, finale 2026, Monumental) | 0:43 | [`output/messi_adieu/`](output/messi_adieu) |
| Hommage manga | Lionel Messi dit adieu à l'Argentine, version MANGA EN PAPIER (mêmes voix ; encrage, trames, accents bleu ciel / or / rouge, cases qui glissent, lignes de concentration, images d'impact, onomatopées, transitions à l'encre, animation fluide) | 0:43 | [`output/messi_manga/`](output/messi_manga) |
| Hommage papier réaliste | Lionel Messi dit adieu à l'Argentine, version PAPIER RÉALISTE (mêmes voix ; 20 « photos » de maquettes en papier générées par IA ; 5 plans sans visage en vidéo IA Veo, 15 plans animés en 2,5D au montage : personnage détouré, profondeur, respiration, lumière, poussière, confettis, grain) | 0:43 | [`output/messi_papier/`](output/messi_papier) |

Chaque épisode livre : la vidéo (`<slug>.mp4`), la version sans voix, la couverture, le script voix off et le script minuté avec légende, hashtags et sources.

## Carrousel TikTok (mode photo)

8 images 1080×1920 dans le même style, à publier en « Photo » sur TikTok : `python3 episodes/liverpool/carrousel.py output/liverpool/carrousel`
(accroche, une date par image, question + CTA à la fin). Mode d'emploi, légende et sources : [`output/liverpool/carrousel/carrousel_guide.md`](output/liverpool/carrousel/carrousel_guide.md).
Toulouse : `python3 episodes/toulouse/carrousel.py output/toulouse/carrousel`, à poster juste avant la vidéo ; ordre, descriptions et commentaires épinglés : [`output/toulouse/toulouse_publication.md`](output/toulouse/toulouse_publication.md).

## Quiz « T'es un vrai fan de X si tu as plus de 5/8 »

Autre format, même style et même voix : 8 questions QCM (4 réponses, 5 s de chrono qui s'écoule), CTA « abonne-toi et like » au milieu, barème final.
Moteur : [`engine/quiz.py`](engine/quiz.py). Skill dédié : [`.claude/skills/tiktok-foot-quiz/SKILL.md`](.claude/skills/tiktok-foot-quiz/SKILL.md),
version installable `dist/tiktok-foot-quiz.skill` (`bash scripts/build_quiz_skill.sh`).

| # | Quiz | Durée | Fichiers |
|---|---|---|---|
| 1 | PSG — stade, Qatar, Neymar 222 M€, 1970, remontada, 5-0 contre l'Inter, Stade Saint-Germain, meilleur buteur | 1:52 | [`output/quiz_psg/`](output/quiz_psg) |
| 2 | PSG niveau 2 (plus dur) — 1986, Luis Enrique, Arsenal 2026, N'Gotty, Rapid Vienne, Coman, Kombouaré, Marquinhos ; sticker « NIVEAU 2 » | 2:04 | [`output/quiz_psg2/`](output/quiz_psg2) |

## Structure

```
engine/engine.py      moteur papier (Paper, Label…) + déchirures, effets, bruitages, rendu parallèle
engine/foot.py        kit foot : joueur qui grandit / change de maillot, ballon, cages, trophées, toise…
engine/story.py       outils de montage : mots clés calés sur la voix, plusieurs plans par scène, zooms, glitch
engine/quiz.py        format quiz : questions QCM, chrono 5 s, révélation, CTA, barème, couverture
episodes/<joueur>/    script de l'épisode + voix off (voix/scene_N.mp3)
assets/sfx/           bruitages ElevenLabs réutilisables (déchirure, foule, sifflet, caisse, flashs…)
output/<joueur>/      livrables
branding/             compte TikTok « Foot Découpé » : nom, bio, description, photo de profil (pp.py)
scripts/setup.sh      dépendances (Pillow, numpy, ffmpeg, polices)
scripts/build_skill.sh  fabrique dist/tiktok-foot-legendes.skill
scripts/minutage_provisoire.py  voix muettes + alignement estimé (avant de générer les voix)
```

## Épisode en attente de voix

Quand les crédits ElevenLabs manquent, on peut tout préparer (scènes, couverture, script) sur un minutage provisoire, puis finir plus tard.
C'est ce qui a été fait pour Dijon et le PSG, finis le 04/10/2026. La marche à suivre est dans le skill du projet,
[`.claude/skills/tiktok-foot-legendes/SKILL.md`](.claude/skills/tiktok-foot-legendes/SKILL.md), qui se charge tout seul dans les sessions ouvertes sur ce dépôt.
Aperçu muet au minutage provisoire : `LEGENDES_PROVISOIRE=<dossier> python3 episodes/<club>/<club>.py <sortie> --apercu`.

## Refaire / modifier un épisode

Depuis l'épisode 6, les vidéos sont en plein écran, sans la barre de fenêtre façon Mac en haut. Les épisodes 1 à 5 ont été publiés avec cette barre ;
pour les re-rendre à l'identique : `LEGENDES_CADRE=1 python3 episodes/<joueur>/<joueur>.py output/<joueur>`.

```bash
bash scripts/setup.sh
python3 episodes/messi/messi.py output/messi --stills     # planches de contrôle
python3 episodes/messi/messi.py output/messi --cover      # couverture
python3 episodes/messi/messi.py output/messi              # rendu complet (~7 min sur 4 cœurs)
python3 episodes/ronaldo/ronaldo.py output/ronaldo        # épisode 2
python3 episodes/zidane/zidane.py output/zidane           # épisode 3
python3 episodes/om/om.py output/om                       # épisode 4 (un club)
python3 episodes/neymar/neymar.py output/neymar           # épisode 5
python3 episodes/lemans/lemans.py output/lemans           # épisode 6 (un club, plein écran)
python3 episodes/dijon/dijon.py output/dijon              # épisode 7 (format court)
python3 episodes/liverpool/liverpool.py output/liverpool  # épisode 9 (format court)
python3 episodes/toulouse/toulouse.py output/toulouse      # épisode 10 (format court)
python3 episodes/messi_adieu/messi_adieu.py output/messi_adieu  # hommage (ultra détaillé)
python3 episodes/messi_manga/messi_manga.py output/messi_manga  # hommage version manga papier
python3 episodes/messi_papier/messi_papier.py output/messi_papier  # hommage version papier réaliste (images IA + 2,5D)
python3 episodes/quiz_psg/quiz_psg.py output/quiz_psg     # quiz 1 (format quiz)
python3 episodes/quiz_psg2/quiz_psg2.py output/quiz_psg2  # quiz 2 (niveau 2, plus dur)
python3 episodes/psg/psg.py output/psg                    # épisode 8 (format court, CTA like)
```
