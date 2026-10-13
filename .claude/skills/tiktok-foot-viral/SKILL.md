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
- **Durée** : histoire 55 s à 1 min 15 (format court par défaut).
  Quiz : **6 questions** (≈ 1 min 05-1 min 10, juste au-dessus de la minute pour la monétisation), chrono 4 s, **pas de pause au milieu** (CTA à la fin).
  Le taux de complétion compte plus que la durée. Moteur : `THEME(nq=6, seuil=4, mot_nq=("Six", 2))` + `assemble(..., n_q=6, cta_after=0)` (exemple : `episodes/quiz_ballondor6/`).
  Test A/B en cours contre la version 8 questions : garder la meilleure selon le % de vues complètes.

## 4) Le format (le cerveau reste sur ce qu'il reconnaît)
Choisir le format qui colle au sujet, le dire dans le plan :
- **Storytime / histoire** (actuel) : pour un destin (Le Mans, Lens), avec un retournement par tiers.
- **Top N** (« 5 transferts les plus fous de l'OM ») : compte à rebours, numéro géant, le n°1 garde le suspense jusqu'au bout.
- **« X choses que tu savais pas sur… »** : une anecdote par plan de 6-8 s, la plus folle en dernier.
- **Quiz / défi** (skill quiz) : « t'es un vrai fan si… », score en commentaire.
- **Avant / après** (« à 10 ans… à 30 ans… ») ou **qui est-ce ?** (silhouette + indices).
- **Classement / débat** (« les 5 meilleurs 10 de l'histoire du PSG ») : fait commenter (« t'aurais mis qui ? »).
- **« 5 anecdotes de fou » en compte à rebours** (épisode Lyon, `episodes/ol_anecdotes/`) : gros numéro 5 → 1, pastilles en haut, la plus folle en n°1 annoncée dès le hook ; DA hybride = images IA « maquette papier » (paysage 16:9, présentées en photo encadrée sur le même plan flouté, `plate()`) + étiquettes papier par-dessus.
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

## 🎨 STYLE : TOUT EN MOTION DESIGN (préférence utilisateur, 13/10/2026)
- La base de chaque vidéo = motion design en code (papier découpé / gouache / stop-motion) : animations, effets, transitions,
  compteurs, chutes physiques, secousses, glitchs… faits par le moteur, pas par des clips vidéo IA.
- **Même quand l'utilisateur envoie des images réelles** (photos de stade, écussons, logos), les passer dans NOTRE style :
  écussons/logos en autocollant papier (contour blanc, ombre), photos « papierisées » (postérisation, aplats gouache, grain
  papier, bords déchirés, virage de couleur), jamais collées brutes en plein écran.
- Clips vidéo IA : uniquement sur demande explicite + estimation acceptée (cf. règle budget).

## ⚠️ BUDGET ELEVENLABS (règle absolue, ajoutée le 13/10/2026)
- **Vidéo IA (image-to-video / text-to-video) : JAMAIS sans accord explicite de l'utilisateur pour CETTE vidéo.** Toujours appeler
  d'abord `estimate_only: true`, annoncer le coût en crédits ET en € , attendre le « ok ». Incident : 4 clips Seedance 2.5 de 5 s
  = 56 000 crédits (~10 €), presque tout le forfait mensuel de l'utilisateur, lancés sans estimation.
- Par défaut, le dynamisme vient du MONTAGE en code (gratuit) : chute physique, secousses, glitchs, lignes de vitesse, zooms,
  Ken Burns sur photos, compteurs. Réutiliser la bibliothèque de clips déjà payés : assets/bordeaux/clips/ (gloire = stade papier
  plein, trophees, chute = ascenseur qui plonge, stade_vide = stade sous la pluie).
- Coûts de référence observés : voix ~100-500 crédits ; image gpt-image-2.5 ~190 ; musique 8 s ~900 ; vidéo Seedance 2.5 5 s ~14 000.
- Images et voix restent OK sans demander, mais annoncer le total de crédits dépensés à chaque livraison.

## 9) PUBLICATION, DESCRIPTIONS, CARROUSELS (EN TEST depuis le 13/10/2026)
**Rythme** : 2 publications/jour pendant 3 semaines, puis ajuster selon les stats.
- Créneaux : midi 12 h-13 h et soir 18 h 30-20 h 30 (heure de Paris).
- Semaine type : Lun quiz/histoire · Mar carrousel/quiz · Mer quiz/carrousel · Jeu histoire/quiz · Ven carrousel/quiz gros club ·
  Sam quiz/carrousel (soir de match) · Dim histoire/carrousel débat.
- Jours de match : publier ~2 h avant le coup d'envoi un contenu sur le club qui joue (C1 mar/mer, L1 ven-dim).
- Jamais 2 fois le même club en 48 h. Répondre à tous les commentaires dans l'heure qui suit la publication.

**Description (à chaque livraison, prête à copier)**
- Ligne 1 = MOTS-CLÉS recherchés + 1 emoji (« Quiz équipe de France facile 🇫🇷 »), pas une phrase vague : TikTok est un moteur de recherche.
- Ligne 2 = question qui oblige à répondre (« Ton score sur 5 ? Sois honnête 👇 »).
- 3 à 5 hashtags : 1 large (#football), 2 niche (#quizfoot #girondins), 1 actu si possible (#ligue1 le week-end). Jamais #fyp/#pourtoi.
- Commentaire épinglé = provocation ou mini-sondage (« 90 % ratent la 3… 👀 », « OUI ou NON ? »).
- Les mêmes mots-clés écrits à l'écran sur l'image 0 (TikTok lit le texte à l'écran).

**Quiz : JAMAIS de question déjà posée** (règle ajoutée le 13/10/2026 après un doublon)
- Avant d'écrire un quiz sur un club, lister toutes les questions existantes de ce club :
  `grep -ho 'Q("[^"]*"' episodes/quiz_<club>*/*.py` — et ne reprendre ni la question ni le même fait sous une autre forme
  (ex. « meilleur buteur », « année de fondation », « prix de Neymar » déjà utilisés pour le PSG).

**Jour de match : l'actu AUTOUR de la vidéo, pas DEDANS** (EN TEST)
- Voix et titre à l'écran restent intemporels (« T'es un vrai fan du PSG ? Si t'as pas 5/5… ») : une vidéo vit des jours/semaines,
  « prêt pour ce soir ? » la périme dès le lendemain.
- L'actu du match va dans : (1) la description (mots-clés de l'affiche : « Avant Manchester City – PSG ce soir 🔴🔵 » +
  #mancitypsg #championsleague) ; (2) un texte ajouté dans l'appli TikTok sur les 3 premières secondes (« Spécial City – PSG ce
  soir ⚔️ ») ; (3) le commentaire épinglé en mode prono (« Prono City – PSG ? Je dis 1-2 Paris 👀 ») ; (4) après le match, répondre
  aux commentaires en citant le résultat pour relancer la vidéo.
- Horaire : 7 h a fait 164 K sur le quiz PSG d'origine → test 7 h / 12 h 30 / 19 h en cours (stats à 24 h à relever).

**Carrousels (mode photo)** : poussés fort par TikTok, swipe = engagement, re-proposés si pas finis, 0 crédit ElevenLabs.
- Formats : « X géants tombés en enfer », quiz à swiper (question / réponse), classement polémique (n°1 caché à la fin),
  avant / maintenant, « le saviez-tu ? » (très enregistré).
- Règles : slide 1 = hook aussi fort qu'en vidéo ; 5 à 8 slides ; 1 info par slide lisible en 2 s ; indication « swipe → » ;
  dernière slide = question pour les commentaires. Format 1080×1920 PNG, style papier (écussons autocollants, portraits papier).
- L'utilisateur ajoute une musique tendance dans l'appli au moment de publier.
- Générateur : episodes/<slug>/<slug>.py → output/<slug>/slide_01.png …

## 8) EN TEST (oct. 2026) : règles tirées des stats réelles de la chaîne, à confirmer
Statut : hypothèses issues des analytics du 13/10/2026. L'utilisateur envoie les résultats au fil de l'eau ; mettre à jour cette
section (passer une règle en « validé » ou la retirer) à chaque retour. Noter ici la date et les chiffres de chaque test.

**Référence : ce qui a marché**
- Quiz PSG d'origine (5 oct.) : 164 K vues (≈ 115 K hors promo), 35,2 s de visionnage moyen, 398 abonnés, 692 commentaires.
  Image 0 = titre DÉFI lisible en 1 s (« T'ES UN VRAI FAN DU PSG ? SI TU AS PLUS DE 5/8 ») + joueur.
- Histoire « faillite 2013 → Ligue 1 2026 » : 18,2 K vues, 30,7 s moyen, 80 abonnés. Hook = contraste chiffré (« Faillite en 2013… L1 en 2026 ?! »).
- Flops : hooks sans mystère (« Adieu Léo », « t'es sûr d'être un vrai supporter ? » sur Lens) → < 700 vues, ~10 s moyen.

**Règles en test**
1. **La 1re seconde décide** (toutes les courbes perdent 20 à 60 % à 0:01) : image 0 = défi ou contraste chiffré, lisible en 1 s,
   + visuel reconnaissable (vrai écusson, logo, visage papier ressemblant) + son dès 0 s (boom, hymne…). Rien ne se superpose au titre.
2. **Quiz : titre défi plein écran ~1,5 s, puis question 1 direct.** Pas d'écran de règles (« 8 questions / 5 secondes ») : le chrono
   s'explique seul. Version courte testée : 5 questions, chrono 3 s, ≈ 50 s (episodes/quiz_france1/quiz_france1_court.py) vs version
   longue 8 questions / 5 s / ≈ 1 min 50 (quiz_france1.py). → comparer visionnage moyen + commentaires.
3. **Hook provocant** (« si t'as pas 5/5… t'es une honte ») : pousse à rester pour se prouver et à commenter son score. À comparer au
   hook classique « t'es un vrai fan de X si t'as plus de 5/8 ».
4. **Vrais écussons / logos** (fournis par l'utilisateur, rangés dans assets/logos/) détourés en autocollant papier (contour blanc +
   ombre) : sur l'image 0 et la couverture, en GRAND. Ne jamais aller chercher soi-même logos ou images de match (droits).
5. **Portraits ressemblants** : bustes papier IA (ElevenLabs gpt-image-2.5-sunburst, 2 joueurs par image sur fond blanc, détourés par
   scripts/detoure_duo.py) plutôt que figurines génériques quand le joueur doit être reconnu.
6. **Sujets à grosse audience d'abord** (PSG, OM, Bleus, Real, Barça, Mbappé, Messi/Ronaldo), en ESPAÇANT un même club (3 quiz PSG en
   4 jours = lassitude : 5,8 K vues, 6,8 s moyen).
7. **2e format : « club ressuscité / club maudit »** (contraste chiffré dans le hook) : Strasbourg, Bordeaux, Leicester, Brest…
   60-75 s, relance vers 15-20 s (« attends la suite »).
8. **Commentaires = carburant** : finir par une action facile (« dis ton score », « écris tes 5 lettres »), commentaire épinglé qui
   provoque. Les réponses cachées (« réponses dans la prochaine ») sont en test sur « Devine la carrière ».
9. **Mascotte : en pause.** Le test A/B n'a pas montré de gain (ressenti utilisateur : plutôt pire) ; ne pas l'utiliser sans demande.
10. **Promo TikTok** : les vues payées gonflent les vues mais pas la rétention (quiz PSG niv. 3 : 6,8 s moyen). Juger un format sur le
    visionnage moyen, le % à 1 s / 8 s, les abonnés et les commentaires, jamais sur les vues seules. Ne jamais supprimer une vidéo en
    promo pour la remplacer : publier la variante le lendemain, en organique.

**Ce qu'il faut demander à l'utilisateur après chaque publication** : vues (général / promo), visionnage moyen, % regardé en entier,
courbe de fidélisation (% restants à 1 s et 8 s), abonnés gagnés, commentaires.
