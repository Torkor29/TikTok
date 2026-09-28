# Légendes du foot — TikTok en papier découpé

Vidéos TikTok verticales qui racontent l'histoire des footballeurs (enfance, anecdotes, contrats, records),
en style papier déchiré / gouache / stop-motion, avec voix off et bruitages ElevenLabs.
Moteur repris et étendu du skill `tiktok-edu-motion` : voir [`SKILL.md`](SKILL.md) pour la méthode complète.

## Épisodes

| # | Joueur | Durée | Fichiers |
|---|---|---|---|
| 1 | Lionel Messi — « trop petit » → le plus grand | 2:03 | [`output/messi/`](output/messi) |

Chaque épisode livre : la vidéo (`<slug>.mp4`), la version sans voix, la couverture, le script voix off et le script minuté avec légende, hashtags et sources.

## Structure

```
engine/engine.py      moteur papier (Paper, Label…) + déchirures, effets, bruitages, rendu parallèle
engine/foot.py        kit foot : joueur qui grandit / change de maillot, ballon, cages, trophées, toise…
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
```
