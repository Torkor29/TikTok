# Légendes du foot — Hommage Messi, version PAPIER RÉALISTE

**Format** : TikTok vertical 1080×1920, 24 i/s, **43 s**, 8 scènes, 20 plans.
**Voix** : la même voix off que les versions papier et manga (ElevenLabs « Léo », `eleven_multilingual_v2`).
**Création originale** :
- les plans, le texte et le montage sont les nôtres ;
- rien n'est repris d'une publicité : ni images, ni phrases, ni musique, ni logos ;
- les maillots n'ont ni écusson ni marque.

**Le rendu** : on dirait des photos de maquettes en papier (papier découpé, plié, peint, petites ombres entre les couches, flou d'arrière-plan d'objectif macro).
- **Images** : 20 plans générés par IA (ElevenLabs, modèle gpt-image-2). Les prompts sont dans `episodes/messi_papier/prompts.json`.
- **5 plans en vidéo IA** (Veo 3.1 Lite, 4 s, sans son) : ce sont les plans où l'on ne voit pas son visage.
  - le stade de nuit ;
  - le carton rouge ;
  - le filet qui tremble ;
  - le penalty au-dessus de la barre ;
  - la tribune finale.
- **Pourquoi pas les 15 autres en vidéo IA** : Veo refuse d'animer le visage d'une personnalité réelle, et on ne contourne pas ce refus.
- **Les 15 plans où il apparaît sont animés au montage, en 2,5D** (nouveau module `engine/parallax.py`) :
  - le personnage est détouré (BiRefNet) ; derrière lui, le fond est rebouché puis légèrement flouté ;
  - la caméra avance plus vite sur le personnage que sur le fond, ce qui donne de la profondeur ;
  - le personnage respire ;
  - certains plans ont un mouvement propre : ses coéquipiers le font rebondir en l'air, il soulève la coupe, il s'éloigne vers la pelouse du Monumental ;
  - lumière : halos qui vacillent, flashs de photographes, poussière dans la lumière ;
  - pluie sur la défaite, confettis en papier ;
  - noir et blanc sur la retraite, puis la couleur revient (« avant de revenir ») ;
  - grain photo et vignettage.
- **Titres** : étiquettes en papier, tampons et lettres découpées, comme dans le reste de la série.
- **Transitions** :
  - entre les scènes : déchirures de papier, filés, zooms ;
  - entre les plans : filés, fondus, flashs blancs.

**Musique** : aucune, à ajouter dans TikTok (son tendance émouvant, au piano, volume 5-10 %).

**À la publication** : cocher **« Contenu généré par IA »** dans les options de TikTok. Les images représentent une personne réelle et sont générées par IA ; TikTok demande de le signaler, et une vidéo non signalée peut être masquée.

## Déroulé

| # | Temps | Voix off | Plans | Transition d'entrée |
|---|---|---|---|---|
| 1 | 0:00 | Vingt et un ans. Plus de deux cents matchs. Lionel Messi dit adieu à l'Argentine. | Vidéo IA : la caméra avance au ras de la pelouse vers une tribune en papier bleu ciel et blanc qui ondule (drapeaux, flashs de téléphones, confettis) ; « 21 ANS », « en sélection · 2005-2026 », « + DE 200 MATCHS ». Flash blanc : gros plan ému, une larme en papier sur la joue, la caméra s'approche lentement ; « MESSI DIT ADIEU / À L'ARGENTINE ». | — |
| 2 | 0:04 | Deux mille cinq : son tout premier match. Il entre… et prend un carton rouge, quarante-sept secondes plus tard. Il sort en larmes. | Bord du terrain à Budapest (foule rouge, blanc, vert), le jeune Messi attend à côté du panneau de changement ; « 2005 », « 1er match · Hongrie - Argentine ». Vidéo IA : contre-plongée sur l'arbitre qui brandit le carton rouge, chrono 0:00 → 0:47, « CARTON ROUGE ! ». Fondu : il sort par le tunnel en pleurant, lumière froide ; « IL SORT EN LARMES ». | zoom |
| 3 | 0:10 | Un an après, à dix-huit ans : son premier but en Coupe du monde. | Il frappe du gauche au coucher du soleil, la caméra recule ; « 2006 », « 18 ANS ». Flash : vidéo IA du ballon qui gonfle le filet, explosion de confettis, flashs ; « 1er but en Coupe du monde ». | filé |
| 4 | 0:14 | Puis trois finales perdues, en trois ans. En deux mille seize, il rate son penalty… et quitte la sélection. Avant de revenir. | Seul sous la pluie, mains sur les hanches ; « 3 FINALES PERDUES », tampons « 2014 », « 2015 », « 2016 ». Vidéo IA : le penalty passe au-dessus de la barre, le gardien plonge ; « 2016 », « RATÉ ». Noir et blanc : assis seul sur le banc, « IL QUITTE LA SÉLECTION ». Flash : regard déterminé, la couleur et un contre-jour chaud reviennent, « … AVANT DE REVENIR ! ». | déchirure horizontale |
| 5 | 0:20 | Deux mille vingt et un : enfin, la Copa América ! Et en deux mille vingt-deux, au Qatar… champion du monde ! | Feux d'artifice : ses coéquipiers le lancent en l'air avec la coupe, ça rebondit, confettis ; « 2021 », « COPA AMÉRICA ». Rayons dorés : il soulève la Coupe du monde, « 2022 · QATAR ». Flash : gros plan qui hurle de joie, confettis, flashs ; « CHAMPION / DU MONDE ! ». | zoom |
| 6 | 0:26 | Deux mille vingt-six : une dernière finale, perdue contre l'Espagne. Puis ce message : il a toujours tout donné pour ce maillot. | Tête basse, les Espagnols fêtent derrière lui, confettis rouges et jaunes ; « 2026 », « dernière finale », « PERDUE ». Fondu : main sur le cœur, la caméra descend lentement ; notification « août 2026 · Messi annonce sa retraite internationale », puis « IL A TOUJOURS TOUT DONNÉ », « POUR CE MAILLOT ». | déchirure diagonale |
| 7 | 0:33 | Six octobre, au Monumental de Buenos Aires : son tout dernier match avec l'Argentine. | Vu de dos, il sort du tunnel et s'éloigne vers la pelouse d'un stade immense ; projecteurs, flashs dans la tribune ; « 6 OCTOBRE 2026 », « Monumental · Buenos Aires ». Filé : il salue la foule en souriant, « DERNIER MATCH ». | filé |
| 8 | 0:37 | Merci, Leo. Ton plus beau souvenir de Messi ? Dis-le en commentaire… et abonne-toi. | Lumière dorée : yeux fermés, sourire, main sur le cœur, poussière dorée ; « MERCI LEO », « Ton plus beau souvenir de Messi ? ». Vidéo IA de la tribune (assombrie) : « TON PLUS BEAU SOUVENIR ? », « COMMENTE ! », bouton cœur, « + ABONNE-TOI », « MERCI LEO » (tout au centre, hors de la colonne d'icônes TikTok), confettis. | zoom |

## Description TikTok (à coller)

```
21 ans de Messi avec l'Argentine… en maquette de papier 📄🇦🇷 Un rouge après 47 secondes, des finales perdues, des larmes… et une Coupe du monde

Merci Leo 🐐 Ton plus beau souvenir de Messi avec l'Argentine ? 👇
❤️ Like + abonne-toi pour l'histoire de tes légendes

#messi #leomessi #argentina #argentine #papercraft #football #foot #legende
```

**Commentaire à épingler** :
```
2014, 2022 ou le dernier match au Monumental : c'est quoi TON moment Messi ? 👇 Le plus cité aura son épisode ⚽
```

**Conseil** : à publier le jour du match d'adieu ou juste après, pendant que tout le monde en parle.

## Sources (vérifiées le 06/10/2026)

- **2005, premier match** : 17 août 2005 contre la Hongrie à Budapest. Il entre à la 63e minute, est expulsé 47 secondes plus tard et sort en larmes.
  - [Goal](https://www.goal.com/en-us/lists/a-nightmare-debut-whats-happened-to-lionel-messis-argentina-team-/3tp9stvyezzq1hh83wid5s5dk)
  - [Planet Football](https://www.planetfootball.com/quick-reads/lionel-messi-argentina-debut-hungary-sent-off-red-card-xi-2005-where-now)
- **2006, premier but en Coupe du monde** : 16 juin 2006 contre la Serbie-et-Monténégro (6-0). À 18 ans et 357 jours, il devient le plus jeune buteur argentin en Coupe du monde.
  - [FC Barcelona](https://www.fcbarcelona.com/en/news/698788/barca-at-the-world-cup-part-2-the-unforgettable-debut-of-leo-messi)
  - [TBS News](https://www.tbsnews.net/sports/twenty-years-one-date-one-legend-messi-goes-first-wc-goal-all-time-record-1465511)
- **Trois finales perdues** :
  - 2014 : Coupe du monde contre l'Allemagne, 0-1 après prolongation. Source : [Goal](https://www.goal.com/en/news/messi-awarded-world-cup-2014-golden-ball/blt149baa00240070af).
  - 2015 : Copa América contre le Chili, 1-4 aux tirs au but. Source : [Eurosport](https://www.eurosport.com/football/copa-america/2015/chile-beat-argentina-on-penalties-to-win-first-copa-america_sto4808447/story.shtml).
  - 2016 : Copa América contre le Chili. Penalty raté au-dessus de la barre, retraite annoncée le 27 juin 2016, retour en août 2016. Sources : [Al Jazeera](https://www.aljazeera.com/sports/2016/8/12/lionel-messi-reverses-decision-to-quit-argentina-team), [CBS Sports](https://www.cbssports.com/soccer/news/messi-tells-why-he-decided-to-retire-from-argentina-and-why-he-came-back).
- **2021, Copa América** : 1-0 contre le Brésil au Maracanã le 10 juillet 2021, son premier grand titre avec l'Argentine. Ses coéquipiers le portent en l'air.
  - [Gulf News](https://gulfnews.com/sport/football/lionel-messis-argentina-beat-brazil-to-win-copa-america-1.1625971252596)
- **2022, champion du monde** : finale à Lusail contre la France, 3-3 puis 4-2 aux tirs au but. Il marque deux fois et reçoit le Ballon d'or du tournoi.
  - [Anadolu](https://www.aa.com.tr/en/sports/messi-argentina-seize-world-cup-glory-with-epic-final-win-over-france/2767012)
  - [The Citizen](https://thecitizen.co.tz/tanzania/sports/messi-wins-golden-ball-for-best-player-at-world-cup-4059798)
- **2026, dernière finale** : Espagne 1-0 Argentine en finale de la Coupe du monde (Ferran Torres à la 106e minute), le 19 juillet 2026.
  - [NBC New York](https://www.nbcnewyork.com/world-cup/spain-argentina-final-messi-yamal-score/6527556/)
- **Retraite internationale** : annoncée fin août 2026 sur les réseaux sociaux. Il y explique avoir toujours tout donné pour ce maillot.
  - [Khaleej Times](https://www.khaleejtimes.com/football/argentina-football-legend-lionel-messi-announces-retirement)
  - [QNA](https://qna.org.qa/en/News-Area/News/2026-8/31/messi-announces-retirement-from-international-football)
- **Match d'adieu** : 6 octobre 2026 contre le Bénin, au Monumental (River Plate) de Buenos Aires. Ce sera sa 208e sélection (207 avant ce match).
  - [Dhaka Tribune](https://www.dhakatribune.com/sport/football/420095/messi-to-play-final-argentina-match-against-benin)
  - [BA Times](https://www.batimes.com.ar/news/sports/messi-set-for-one-last-dance-with-argentina-in-international-friendly-match.phtml)

**Précautions** :
- **Score du match d'adieu** : il n'est ni dit ni montré, pour que la vidéo reste juste avant comme après le match. « Plus de deux cents matchs » reste exact (207 sélections avant le 6 octobre).
- **Retraite de 2026** : la voix reformule son message (« il a toujours tout donné pour ce maillot ») et ne le cite pas mot pour mot.
- **Images** : ce sont des maquettes en papier imaginées (IA), pas des photos des matchs. Le stade, la tribune et la banderole sont des décors inventés.
- **Hongrie et Espagne** : maillots rouges stylisés, sans écusson.
