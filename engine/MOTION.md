# Standards motion design (à respecter sur chaque vidéo) — implémentés dans engine/motion.py

## 1. Cycle de vie de chaque élément
- Tout élément a une **entrée** (0,25–0,40 s) ET une **sortie** (0,18–0,25 s). Jamais d'apparition / disparition sèche.
- Entrées : `pop` (ressort, dépassement ~10 %), `drop` (chute accélérée + écrasement à l'atterrissage),
  `stamp` (anticipation 1,9× → impact → écrasement), `slide_l/r`, `rise` (ressort + inclinaison dans le sens du mouvement).
- Sorties : `shrink` (rétrécit + fondu), `fly` (s'envole vers le haut), `drop_out` (tombe), `wipe` pour les textes.
- **Au maximum 2 blocs de texte à l'écran** ; un texte sort AVANT que le suivant n'entre au même endroit.

## 2. Principes d'animation
- Easing : jamais linéaire. Ressorts amortis (ζ ≈ 0,45) pour les arrivées, ease-in pour les départs.
- **Anticipation** avant tout gros impact (petit recul de 60 ms), **écrasement / étirement** à l'impact.
- **Follow-through** : la rotation suit la vitesse (un objet qui file penche), puis se rééquilibre.
- **Idle** : chaque élément posé respire (±3 px, ±0,8°), rien n'est figé plus de 0,8 s.
- Personnages : cycles complets (marche, course, frappe) avec rebond du corps, bras en opposition.
- Ballon : arc parabolique + rotation + ombre au sol + écrasement au rebond.

## 3. Caméra
- Ressort critique vers des cibles (pas d'interpolation linéaire), petit dépassement sur les gros moves.
- Impacts : « trauma » (secousse bruitée qui décroît en 0,3 s) + coup de zoom 6 %.
- Une cible par phrase : la caméra cadre l'action dite.

## 4. Lisibilité
- Texte clé lisible ≥ 0,8 s, mots qui tombent SUR le mot dit (± 50 ms).
- Zones : rien d'important au-dessus de y 230, au-delà de x 900 entre y 900-1500, en dessous de y 1520.
- Contraste : élément sombre jamais sur fond sombre sans liseré ou halo clair.

## 5. Audit obligatoire avant rendu
- Bandes de 8 images sur 0,6–1 s autour de CHAQUE micro-animation : vérifier entrée, impact, sortie, absence de saut.
- Planche 4 images / scène : chevauchements, textes coupés, plans figés.
- Toute anomalie est corrigée puis ré-auditée.
