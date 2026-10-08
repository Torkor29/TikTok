---
name: tiktok-foot-viral
description: Version AMÉLIORÉE « orientée vues » de la série Légendes du foot (histoires de joueurs/clubs ET quiz) : choix et notation du sujet, hook à 3 niveaux (phrase + son + visuel) testé, rythme contrôlé (blancs de voix coupés, un changement visuel toutes les 1,5 s), formats qui marchent (top, storytime, quiz, « X choses que tu savais pas »), objectif vues/abonnés, SEO (mots-clés dits et écrits dans les 3 premières secondes) et description courte qui fait commenter. Utilise ce skill en PRIORITÉ dès que l'utilisateur demande une vidéo TikTok foot (histoire, bio, club, quiz, top), veut « plus de vues », un meilleur hook, ou une idée de sujet. Il s'appuie sur les skills tiktok-foot-legendes (moteur, kit foot) et tiktok-foot-quiz (format quiz), qui restent valables.
---

# TikTok foot — version « viral » (sujet + hook + rythme)

Ce skill **ne remplace pas** les deux autres : il s'ajoute par-dessus.
- Technique (moteur papier, kit foot, montage calé sur la voix, rendu, pièges) : `SKILL.md` à la racine (`tiktok-foot-legendes`).
- Format quiz : `.claude/skills/tiktok-foot-quiz/SKILL.md`.
- Ici : **ce qui fait les vues**, dans l'ordre d'importance : **sujet > hook > rythme**, puis format, objectif, SEO.
  Une réal basique sur un bon sujet bat toujours une réal stylée sur un sujet éclaté.

## Ce qui change par rapport aux épisodes 1 à 12 (diagnostic)
| Levier | Avant | Maintenant |
|---|---|---|
| Sujet | on fait le sujet demandé tel quel | on le **note** (grille ci-dessous) et on propose l'**angle** le plus fort, voire un meilleur sujet |
| Hook | bon (phrase + son + visuel) mais souvent **trop long** (ASSE : 27 mots, ~7 s) | 1re phrase **≤ 12 mots, < 2,5 s**, hook complet ≤ 18 mots ; mot-clé du sujet dit avant 3 s |
| Rythme | des « … » dans le texte → **blancs de 0,4 s** dans la voix (ex. ASSE scènes 2, 4, 5 ; « voix pas fluide » sur le quiz PSG 3) | un seul « … » par scène max ; blancs > 0,3 s **coupés** avant l'alignement ; `scripts/check_rythme.py` obligatoire |
| Format | quasi toujours « histoire chronologique » | on choisit le format qui colle au sujet (liste plus bas) ; la chronologie n'est qu'un format parmi d'autres |
| Objectif | implicite | on l'écrit : **visibilité** (sujet large, CTA léger) ou **abonnés** (série, épisode N, « abonne-toi pour la suite ») |
| « Privilège » faceless | rien | la **voix** (Léo, toujours la même) + un **personnage récurrent** reconnaissable font office de visage |
| SEO | hashtags seulement | mots-clés **dits** (voix), **écrits** (1re image, couverture) et dans la description ; compte 100 % foot |

## 1) Le sujet (le plus important)
Avant d'écrire, noter le sujet sur 10 et le dire à l'utilisateur en une ligne (« 8/10 : gros club, rivalité, anecdote choc »).
- **+3 demandé** : par un abonné, en commentaire, ou dans l'actu de la semaine (transfert, record, polémique, anniversaire).
- **+2 grosse base de fans** : PSG, OM, Real, Barça, Messi, Ronaldo, Mbappé, Zidane… (plus de fans = plus de partage).
- **+2 anecdote incroyable mais vraie** (poteaux carrés, stade construit par 180 mineurs, 222 M€) : c'est elle qui fait le hook.
- **+2 clivant** : rivalité (OM-PSG, Messi-Ronaldo), débat (« le plus grand ? »), injustice.
- **+1 nostalgie** (années 90-2000) ou **+1 « je ne savais pas »**.
Sous 5/10 : proposer un autre **angle** du même sujet (ex. « l'histoire de Saint-Étienne » → « le club qui a perdu une finale à cause de poteaux carrés »).
Garder une **banque de sujets** : noter dans `output/sujets.md` les clubs/joueurs demandés en commentaire (l'utilisateur les colle), et les traiter en priorité.

## 2) Le hook (3 niveaux : phrase, son, visuel)
Un hook qui interpelle + un sujet demandé = 70 % du succès.
- **Phrase** : ≤ 12 mots pour la 1re phrase, dite en < 2,5 s, sans « … » ; hook complet ≤ 18 mots (≈ 5 s).
  Le **mot-clé** (club, joueur) est dit dans les 3 premières secondes (SEO + le fan se reconnaît).
  Modèles qui marchent :
  - **Fait choc** : « Ce club a perdu une finale… à cause de poteaux carrés. »
  - **Défi** : « Fan du PSG ? Prouve-le : six sur huit minimum. »
  - **Interpellation** : « Lensois ? T'es sûr d'être un vrai supporter ? »
  - **Chiffre impossible** : « Ce stade a plus de places que la ville n'a d'habitants. »
  - **Avant / après** : « Champion d'Europe… puis en D2 ?! »
  - **Secret / interdit** : « Personne ne parle de ce que Zidane a fait à 14 ans. »
  - **Boucle ouverte** : annoncer la fin dès le début (« reste jusqu'au bout, la fin est folle »), mais seulement si la fin tient la promesse.
- **Son** : `assets/sfx/hook.mp3` (scratch + impact) **≤ 0,55 s** de pad seul avant la voix (0,85 s était trop long), l'impact tombe sur la 1re image forte.
- **Visuel** : à l'image 0, le **nom du sujet en énorme** (`ransom_line`) + un objet choc qui bouge déjà (ballon qui frappe, coupe, silhouette), jamais un fond vide.
  Le titre écrit ≠ la phrase dite (elles se complètent, sinon redondance).
- Écrire **3 hooks**, garder le plus court et le plus clivant, donner les 2 autres à l'utilisateur pour un test A/B (même vidéo, hook différent).

## 3) Le rythme (watchtime)
Le rythme vient de l'**élocution** et du **montage**.
- **Texte** : phrases de 5 à 12 mots, alterner court / très court (« Défaite. Un à zéro. »).
  Un seul « … » par scène (suspense), le reste en virgules : chaque « … » crée un blanc de 0,4 s chez ElevenLabs.
- **Voix** : après téléchargement, lancer `python3 scripts/check_rythme.py episodes/<sujet> --mots "mot1,mot2"`.
  Tout blanc > 0,35 s au milieu d'une phrase est raccourci **avant l'alignement** :
  `ffmpeg -i in.mp3 -af "silenceremove=stop_periods=-1:stop_duration=0.25:stop_threshold=-35dB:stop_silence=0.15" out.mp3`
  (puis `align_episode`). Si une voix sonne plate ou hachée : la régénérer avec le texte sans « … » (1 crédit ≈ 1 caractère).
- **Montage** : un changement visuel toutes les **1,2 à 2 s** (nouveau plan `shots()`, mot clé `kw()`, tampon, zoom `punch`), un bruitage sur chaque changement.
  Marges `pad_in=.12`, `pad_out=.2`. Pas de plan fixe de plus de 2,5 s.
  **Relance** toutes les ~15 s (question, « mais… », retournement) pour éviter la chute de rétention.
- **Durée** : histoire 55 s à 1 min 15 (format court par défaut) ; quiz > 1 min (chrono 4 s).

## 4) Le format (le cerveau reste sur ce qu'il reconnaît)
Choisir le format qui colle au sujet, le dire dans le plan :
- **Storytime / histoire** (actuel) : pour un destin (Le Mans, Lens), avec un retournement par tiers.
- **Top N** (« 5 transferts les plus fous de l'OM ») : compte à rebours, numéro géant, le n°1 garde le suspense jusqu'au bout.
- **« X choses que tu savais pas sur… »** : une anecdote par plan de 6-8 s, la plus folle en dernier.
- **Quiz / défi** (skill quiz) : « t'es un vrai fan si… », score en commentaire.
- **Avant / après** (« à 10 ans… à 30 ans… ») ou **qui est-ce ?** (silhouette + indices).
- **Classement / débat** (« les 5 meilleurs 10 de l'histoire du PSG ») : fait commenter (« t'aurais mis qui ? »).
- **Réaction à l'actu** (transfert, record) : publier vite, sujet court, 30-45 s.
Les **trends** (son, structure) sont reprises si elles collent au sujet ; ne jamais copier les plans, les phrases ni les logos.

## 5) L'objectif de la vidéo
Le noter en tête du `_script.md` :
- **Visibilité** (par défaut) : sujet large, CTA léger au milieu (like / commentaire), question en fin.
- **Abonnés / branding** : vidéo de **série** (« Légendes du foot · épisode 13 », même générique visuel, même voix), CTA « abonne-toi pour l'épisode de ton club », annonce du prochain épisode.
- On ne vend rien dans ces vidéos (les vues chutent) ; si un jour il y a une offre, elle va dans la bio, pas dans la vidéo.

## 6) Le « privilège » sans visage (faceless)
Les gens restent pour ce qu'ils aiment regarder ou écouter. Sans visage :
- **La voix** est notre visage : toujours Léo, énergique, jamais monotone (varier le texte, pas la voix).
- **Un personnage récurrent** reconnaissable (le joueur en papier, ou un narrateur-mascotte au maillot neutre qui ouvre et ferme chaque épisode) : on le reconnaît en 0,5 s dans le fil.
- **Du « beau » qui attire l'œil** : stades de nuit, projecteurs, confettis, coupes dorées, gros plans `Portrait`, version papier réaliste pour les gros sujets (Messi).
- La **couverture** suit le même gabarit de série (nom du sujet énorme + question), pour que le profil soit cohérent.

## 7) Le SEO
L'algo montre la vidéo à un échantillon selon :
1. les mots-clés de la vidéo ;
2. la thématique du compte ;
3. qui est connecté à ce moment-là (non maîtrisable).

Donc :
- **Dire** le nom du club / joueur dans les 3 premières secondes (voix) et le **répéter** 2-3 fois (« les Verts », « Sainté », « l'ASSE »).
- L'**écrire** à l'image 0 et sur la couverture (TikTok lit le texte à l'écran).
- **Description** : le mot-clé dans les 5 premiers mots + 5 hashtags (club, surnom, #football #foot, + #quizfoot pour un quiz).
- **Compte 100 % foot** : pas de sujets hors foot sur ce compte (sinon la catégorisation se brouille). Publier à heure fixe, de préférence 18 h-21 h ou le midi.
- Le **titre** (texte de couverture) reprend la recherche probable : « histoire de Saint-Étienne », « quiz PSG ».

## Description TikTok (à chaque livraison, COURTE)
2 lignes max + 5 hashtags, et un commentaire à épingler d'une phrase :
- **Ligne 1** : le mot-clé + le fait choc, 1-2 émojis.
- **Ligne 2** : une question à réponse courte et clivante (OUI / NON, un nom, un score) + 👇.
- **Commentaire à épingler** : une 2e question pour relancer.

## Checklist avant le rendu (à recopier dans la réponse)
- [ ] Sujet noté /10, avec son angle.
- [ ] Format choisi.
- [ ] Objectif écrit.
- [ ] 3 hooks écrits : celui retenu fait 12 mots max sur la 1re phrase, et le mot-clé est dit avant 3 s.
- [ ] Son de hook ≤ 0,55 s, visuel fort à l'image 0.
- [ ] `check_rythme.py` passé (aucun blanc > 0,35 s, un seul « … » max par scène).
- [ ] Un changement visuel toutes les 2 s au plus, une relance toutes les ~15 s.
- [ ] CTA au milieu (juste après un moment fort) et à la fin.
- [ ] Description courte + commentaire à épingler donnés dans la réponse.
