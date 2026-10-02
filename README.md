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
| 7 | Dijon FCO — a battu le PSG… puis la 3e division ?! (format court ~1 min 15 avec barre chrono, « DIJON » + moutarde dès la 1re image ; **voix en attente de crédits ElevenLabs**) | — | [`output/dijon/`](output/dijon) |

Chaque épisode livre : la vidéo (`<slug>.mp4`), la version sans voix, la couverture, le script voix off et le script minuté avec légende, hashtags et sources.

## Structure

```
engine/engine.py      moteur papier (Paper, Label…) + déchirures, effets, bruitages, rendu parallèle
engine/foot.py        kit foot : joueur qui grandit / change de maillot, ballon, cages, trophées, toise…
engine/story.py       outils de montage : mots clés calés sur la voix, plusieurs plans par scène, zooms, glitch
episodes/<joueur>/    script de l'épisode + voix off (voix/scene_N.mp3)
assets/sfx/           bruitages ElevenLabs réutilisables (déchirure, foule, sifflet, caisse, flashs…)
output/<joueur>/      livrables
branding/             compte TikTok « Foot Découpé » : nom, bio, description, photo de profil (pp.py)
scripts/setup.sh      dépendances (Pillow, numpy, ffmpeg, polices)
scripts/build_skill.sh  fabrique dist/tiktok-foot-legendes.skill
```

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
```
