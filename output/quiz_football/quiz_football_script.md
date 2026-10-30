# Quizz football express : « Si t'as pas 5/5, t'es pas un vrai fan de foot »

**Objectif** : visibilité et SEO. TikTok suggère la recherche « Quizz football » (capture de l'utilisateur, 28/10/2026), donc le mot-clé est dit à 0 s, écrit en géant sur l'image 0, présent en petit sur toutes les questions, et il ouvre la description.
**Sujet** : 7/10 (+2 grosse base de fans, puisque tout le monde est visé, +2 défi d'identité, +2 « je savais pas » sur la Q5, +1 recherche suggérée par TikTok).
**Format** : quiz court, modèle du quiz Real (`episodes/quiz_real`). 5 QCM, chrono 3-2-1 de 6 temps à 129 BPM, score à l'écran, durée d'environ 50 s avec les réponses dites.

## Hooks (A/B)
1. **Retenu** : « Quizz football ! Si t'as pas cinq sur cinq, t'es pas un vrai fan de foot. »
2. « Quizz football : 90 % ratent la dernière question. »
3. « Quizz football : t'as cinq secondes, montre que t'es pas un touriste. »

## Questions (difficulté croissante, réponses B C A D B)
| # | Niveau | Question | Bonne réponse | Pièges |
|---|---|---|---|---|
| 1 | FACILE | Quel pays a inventé le football moderne ? | **B Angleterre** (règles de la FA, Londres 1863) | France, Brésil, Italie |
| 2 | FACILE | Où s'est jouée la 1re Coupe du monde ? | **C Uruguay** (1930, Montevideo) | Brésil, Italie, France (Jules Rimet était français) |
| 3 | MOYEN | Qui a marqué le but de la « main de Dieu » ? | **A Maradona** (1986, contre l'Angleterre) | Pelé, Messi (but de la main en 2007), Henry (main en 2009) |
| 4 | DIFFICILE | Quel pays a joué toutes les Coupes du monde ? | **D Brésil** (22 sur 22) | Allemagne (absente en 1930 et 1950), Argentine, Italie |
| 5 | LA PLUS DURE | Quel gardien a marqué plus de 100 buts ? | **B Rogério Ceni** (131 buts, 129 selon l'IFFHS et le Guinness) | Chilavert (67), Higuita, Neuer |

## Déroulé
- 0 s : « QUIZZ / FOOTBALL » en bandes papier géantes, Messi, Ronaldo et Mbappé détourés sur médaillon doré, « SI T'AS PAS 5/5… » ; son de hook, voix dès 0 s.
- Pour chaque question : « QUESTION n/5 », niveau, la question lue, les 4 réponses en cascade, puis le chrono 3-2-1 avec tic-tac. Sur le dernier temps, ding : la bonne réponse passe au vert et remonte, l'illustration arrive (drapeau papier, médaillon 1986, médaillon « 131 BUTS ») avec +1, puis le score.
- Fin : « TON SCORE ? / DIS-LE EN COMMENTAIRE », « QUIZZ FOOTBALL ».

## Description TikTok
> Quizz football : t'es un vrai fan de foot ? ⚽🔥
> Ton score sur 5 ? Sois honnête 👇
> #football #quizfoot #footballquiz #quiz #foot

**Commentaire à épingler** : « 90 % ratent la 5… t'avais trouvé Ceni ? 👀 »

Au moment de publier, ajouter dans l'appli le son tendance « FOOTBALL – Nevoa Beats » à très bas volume, sous la voix (suggestion TikTok, 49K publications).

## Sources
- FA et règles de 1863 : https://en.wikipedia.org/wiki/The_Football_Association
- Coupe du monde 1930 : https://en.wikipedia.org/wiki/1930_FIFA_World_Cup
- Main de Dieu : https://en.wikipedia.org/wiki/Argentina_v_England_(1986_FIFA_World_Cup)
- Brésil, seul pays présent à toutes les éditions : https://en.wikipedia.org/wiki/Brazil_at_the_FIFA_World_Cup
- Rogério Ceni : https://en.wikipedia.org/wiki/List_of_goals_scored_by_Rog%C3%A9rio_Ceni, https://www.guinnessworldrecords.com/world-records/most-goals-scored-by-a-goalkeeper

## Pour finir la vidéo (voix)
Texte exact dans `episodes/quiz_football/TEXTE_VOIX.txt` (12 phrases, une par ligne, réponses dites après le ding ; voix Léo `jsScnYkNNda9Q1NES5nn`, `eleven_multilingual_v2`, environ 600 crédits).
Déposer le mp3 en `episodes/quiz_football/voix/voix.mp3` (blancs coupés : `scripts/trim_blancs.py`), puis lancer `python3 episodes/quiz_football/quiz_football.py`.
Les segments sont trouvés automatiquement (`voix/segments.json`, à vérifier) et la sortie est `output/quiz_football/quiz_football.mp4`.
