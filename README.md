# Légendes du foot — TikTok en papier découpé

Vidéos TikTok verticales qui racontent l'histoire des footballeurs (enfance, anecdotes, contrats, records),
en style papier déchiré / gouache / stop-motion, avec voix off et bruitages ElevenLabs.
Moteur repris et étendu du skill `tiktok-edu-motion` : voir [`SKILL.md`](SKILL.md) pour la méthode complète.

## Épisodes

| # | Joueur | Durée | Fichiers |
|---|---|---|---|
| 1 | Lionel Messi — « trop petit » → le plus grand | 2:03 | [`output/messi/`](output/messi) |
| 2 | Cristiano Ronaldo — opéré du cœur à 15 ans → 6 Coupes du monde (accroche devinette, pause « quel joueur ? » au milieu, montage nerveux) | 1:49 | [`output/ronaldo/`](output/ronaldo) |

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

```bash
bash scripts/setup.sh
python3 episodes/messi/messi.py output/messi --stills     # planches de contrôle
python3 episodes/messi/messi.py output/messi --cover      # couverture
python3 episodes/messi/messi.py output/messi              # rendu complet (~7 min sur 4 cœurs)
python3 episodes/ronaldo/ronaldo.py output/ronaldo        # épisode 2
```
