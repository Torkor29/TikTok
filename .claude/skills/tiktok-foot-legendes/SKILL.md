---
name: tiktok-foot-legendes
description: Crée des vidéos TikTok « Légendes du foot » (1080x1920, format court ~1 min 15 ou long ~2 min) qui racontent la vie d'un footballeur ou l'histoire d'un club (enfance, galères, anecdotes, contrats, records, transferts) dans un style papier déchiré / gouache / stop-motion : joueur en papier découpé qui grandit et change de maillot, transitions en déchirure de papier, tampons, compteurs, confettis, voix off ElevenLabs et vrais bruitages. Utilise ce skill dès que l'utilisateur demande l'histoire, la bio, les anecdotes ou les contrats d'un joueur ou d'une joueuse (« fais Ronaldo », « l'histoire de Zidane », « épisode sur Mbappé »), ou d'un club (« fais l'histoire de Le Mans », « l'histoire du PSG »), ou de finir un épisode en attente de voix, même s'il ne dit pas « skill ».
---

# Légendes du foot (skill de ce dépôt)

Pour un **quiz** (« t'es un vrai fan de X ? », QCM + chrono), utiliser le skill `tiktok-foot-quiz` (`.claude/skills/tiktok-foot-quiz/SKILL.md`).

Tout le skill est dans ce dépôt. Avant de toucher à un épisode, lire :
- `SKILL.md` à la racine : la méthode complète (accroche, rythme, CTA, montage calé sur la voix, kit foot, effets, bruitages, pièges) ;
- `README.md` : la liste des épisodes et les commandes.

Le code est dans `engine/` (moteur papier, kit foot, outils de montage), un épisode par dossier `episodes/<sujet>/`, les livrables dans `output/<sujet>/`.
Branche de travail : `claude/footballer-stories-tiktok-h7k2q9`.

## Finir un épisode « en attente de voix »

Exemples : Dijon et PSG (préparés sans voix, finis le 04/10/2026). Ces épisodes ont tout sauf la voix : scènes (`episodes/<club>/<club>.py`), textes des voix (`episodes/<club>/textes_voix.json`),
couverture et script (`output/<club>/`). Les scènes ont été calées sur un minutage provisoire (`scripts/minutage_provisoire.py`).

1. **Voix** : un flow ElevenLabs par épisode, puis `creative_generate_speech` une fois par scène.
   - Voix Léo `jsScnYkNNda9Q1NES5nn`, modèle `eleven_multilingual_v2`, `generations_count=1`.
   - Le texte de la scène N est l'élément N-1 de `textes_voix.json`, à recopier tel quel.
   - Compter environ 1 400 crédits par épisode : tester d'abord une scène, l'erreur de quota arrive dans `creative_get_flow_run_status`.
   - Télécharger chaque `media[].url` avec `curl` dans `episodes/<club>/voix/scene_N.mp3`.
   - Si le connecteur ElevenLabs n'est pas dans la session : demander à l'utilisateur de le connecter sur claude.ai/customize/connectors, puis d'ouvrir une nouvelle session.
2. **Alignement** : vérifier avec `ffmpeg -af silencedetect` et l'enveloppe d'énergie, puis corriger à la main les mots mal placés (voir les pièges de `Words` dans `SKILL.md`).
   ```python
   import sys, json; sys.path.insert(0, "engine"); from story import align_episode
   T = json.load(open("episodes/<club>/textes_voix.json"))
   align_episode([f"episodes/<club>/voix/scene_{i}.mp3" for i in range(1, len(T)+1)], T, "episodes/<club>/alignement.json")
   ```
3. **Planches** : `python3 episodes/<club>/<club>.py output/<club> --stills`, sans `LEGENDES_PROVISOIRE`. Les regarder, car les timings ont bougé.
4. **Rendu** : `python3 episodes/<club>/<club>.py output/<club>` (~5 min pour 1 min 15). Il produit `<slug>.mp4`, `<slug>_sans_voix.mp4` et `<slug>_voix_off.txt`.
5. **Vérifier** :
   - la voix de chaque scène dans le mp4 (corrélation avec `voix/scene_N.mp3`) ;
   - le niveau ≈ -14 LUFS (`ebur128`) ;
   - stéréo 48 kHz ;
   - une grille d'images.
6. **Finir** :
   - remplir les temps du déroulé dans `output/<club>/<club>_legende_script.md` et retirer l'encadré « Voix en attente » ;
   - mettre la durée dans `README.md` ;
   - `bash scripts/build_skill.sh` ;
   - commit + push ;
   - envoyer le mp4 avec voix, la couverture et le script, jamais la version `_sans_voix`.
