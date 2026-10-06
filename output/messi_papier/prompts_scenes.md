# Hommage n°10 en papier réaliste : prompts image et vidéo, plan par plan

**Principe** :
1. Pour chaque plan, tu génères d'abord l'**image**, puis tu l'animes en **image-to-video**.
2. Tu m'envoies les 20 clips.
3. Je fais le montage : voix de Léo, titres, bruitages, transitions papier, rythme calé sur la voix.

Les prompts sont en anglais, parce que les modèles d'image et de vidéo comprennent mieux l'anglais.

## Réglages pour tous les plans
- **Format** : vertical **9:16** (1080×1920 si possible), **5 secondes** par clip, 24 ou 30 i/s.
- **Son** : aucun, ou on le coupe. La voix et les bruitages sont ajoutés au montage.
- **Texte** : aucun texte dans les images ni dans les vidéos. Les dates et les titres sont ajoutés au montage.
- **Noms des fichiers** : `p01.mp4` … `p20.mp4`, dans l'ordre ci-dessous.
- **Garder le même personnage** :
  - génère d'abord **p01** ; la photo `p01_image_depart.png` (envoyée avec ce document) est déjà prête ;
  - si ton outil accepte une image de référence, mets-la en référence pour tous les plans « adulte » ;
  - pour les plans « jeune », génère **p03** en premier et sers-t'en de référence pour p05 et p06.
- **Ne jamais écrire de nom de joueur** dans les prompts : les outils refusent souvent. La description du personnage suffit.
- **Ni écusson, ni logo, ni marque**. La coupe est une coupe dorée générique.

## Les blocs communs (déjà intégrés en entier dans chaque prompt ci-dessous : tu copies-colles tel quel)

**STYLE**
`Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16.`

**ADULTE (2021-2026)**
`a handmade paper-craft football captain in his late thirties: short dark-brown hair swept to the side made of layered paper strips, full dark-brown beard made of fine paper shreds with a few grey strands, warm brown eyes, slim build, sky-blue and white vertical striped football shirt with no logo and no crest, white captain armband on his left arm`

**TRENTAINE (2014-2016)** : même bloc, mais `in his late twenties, short trimmed dark beard, no grey hair`

**JEUNE (2005-2006)**
`an 18-year-old handmade paper-craft football player: shaggy medium-length dark-brown hair with a fringe made of paper strips, no beard, boyish face, slim and small, sky-blue and white vertical striped shirt with no logo and no crest, black shorts, white socks`

**INTERDITS**
`No text, no letters, no numbers, no logos, no brand marks, no crests.`

**RÈGLES VIDÉO** (à coller à la fin de chaque prompt vidéo)
`Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.`

---

## Scène 1 — « Vingt et un ans. Plus de deux cents matchs. Lionel Messi dit adieu à l'Argentine. » (4,2 s)

### p02 — Le stade de nuit (0:00 → 0:02, sur « 21 ans… 200 matchs »)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16.
A huge paper stadium at night seen from pitch level, packed with thousands of tiny paper cutout fans waving sky-blue and white paper flags and scarves, floodlight beams cutting through light haze, glittering phone lights made of tiny foil dots, green paper pitch with chalk lines in the foreground.
No text, no letters, no numbers, no logos, no brand marks, no advertising words.
```
**Vidéo** :
```
Slow, steady dolly-in low over the paper pitch toward the packed stand. The paper flags and scarves wave gently in a breeze, the tiny foil phone lights twinkle, the floodlight beams pulse softly through drifting haze, a few paper confetti float down. Majestic, emotional atmosphere. Keep everything made of paper and cardstock, no text appearing. Smooth cinematic motion, 5 seconds.
```

### p01 — Gros plan ému (0:02 → 0:04, sur « Lionel Messi dit adieu à l'Argentine »)
**Image** : déjà faite, c'est `p01_image_depart.png`. Pour la refaire :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. Night stadium, blurred background crowd of tiny paper fans holding sky-blue and white paper flags, warm floodlight glow. Chest-up close-up of a handmade paper-craft football captain in his late thirties: short dark-brown hair swept to the side made of layered paper strips, full dark-brown beard made of fine paper shreds with a few grey strands, warm brown eyes, slim build, sky-blue and white vertical striped football shirt with no logo and no crest, white captain armband on his left arm: moved and proud, brown eyes glistening, one small paper tear on his cheek, looking slightly past the camera. Head in the upper-middle of the frame. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Very slow push-in on his face. He blinks once, his eyes glisten, a small paper tear slides slowly down his cheek, his chest rises with a deep breath, he lifts his gaze slightly toward the stands. Background bokeh of floodlights and paper flags shimmering, warm light flickering gently on his face. Intimate, emotional. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

## Scène 2 — « 2005 : son tout premier match. Il entre… et prend un carton rouge, 47 secondes plus tard. Il sort en larmes. » (6,5 s)

### p03 — Il attend d'entrer (0:04 → 0:06)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. Night football match, touchline of a paper stadium, crowd of tiny paper cutout fans in red, white and green behind, a floodlight tower. Full-body an 18-year-old handmade paper-craft football player: shaggy medium-length dark-brown hair with a fringe made of paper strips, no beard, boyish face, slim and small, sky-blue and white vertical striped shirt with no logo and no crest, black shorts, white socks standing nervously at the touchline about to come on, hands clasped. Beside him a paper fourth official in black holds up a substitution board showing only a green arrow. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Slow lateral tracking shot from left to right along the touchline, ending on the young player. He takes a deep breath, adjusts his shirt, then jogs onto the pitch past the camera. The official lowers the board. The crowd of paper fans moves and claps, floodlight glare. Anticipation. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

### p04 — Le carton rouge (0:06 → 0:09, sur « carton rouge… 47 secondes »)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. Dramatic low-angle shot at night: a bald paper referee in an all-black kit thrusts a bright red paper card high into the air with his right hand, a floodlight flaring behind him, blurred crowd of tiny paper fans in red, white and green. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Fast snap zoom from a medium shot to the red card in the first second, then a slight handheld shake. The referee's arm locks upward, the red paper card catches the floodlight and glows, small paper dust particles float in the light, the blurred crowd reacts. Tense, sudden, dramatic. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

### p05 — Il sort en larmes (0:09 → 0:10, sur « Il sort en larmes »)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. A dark paper stadium tunnel with cold light at its end. Medium shot of an 18-year-old handmade paper-craft football player: shaggy medium-length dark-brown hair with a fringe made of paper strips, no beard, boyish face, slim and small, sky-blue and white vertical striped shirt with no logo and no crest, black shorts, white socks walking off into the tunnel, head down, crying, wiping his eyes with one hand, tiny paper tear drops, face visible in three-quarter view. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Slow backward dolly in front of him as he walks toward the camera through the tunnel, head down, shoulders shaking as he cries, wiping his eyes. The cold light behind him flickers slightly, long paper shadows on the tunnel walls. Melancholic, quiet. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

## Scène 3 — « Un an après, à 18 ans : son premier but en Coupe du monde. » (3,6 s)

### p06 — La frappe (0:10 → 0:12)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. A World Cup match in a sunny evening paper stadium, crowd of tiny paper fans in mixed colours. Full-body low-angle shot of an 18-year-old handmade paper-craft football player: shaggy medium-length dark-brown hair with a fringe made of paper strips, no beard, boyish face, slim and small, sky-blue and white vertical striped shirt with no logo and no crest, black shorts, white socks striking a white paper football with his left foot, dynamic action pose, body leaning, thin paper motion streaks behind the ball. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Slow-motion action: low tracking camera beside him, he swings his left leg and strikes the paper ball, the ball shoots out of frame toward the goal, little paper turf bits fly up. Camera whips slightly to follow the ball. Energetic, then speeds up to real time. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

### p07 — Le filet (0:12 → 0:14, sur « premier but »)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. Close-up of a white paper football hitting the back of a goal net made of fine white paper threads, the net bulging outward, an explosion of sky-blue, white and gold paper confetti, blurred crowd of tiny paper fans jumping behind, evening floodlights. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
The paper ball slams into the paper net, which stretches and ripples outward, then the ball drops. A burst of sky-blue, white and gold paper confetti explodes toward the camera, the crowd jumps up in the background. Slight camera shake on impact, then a slow push-in. Euphoric. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

## Scène 4 — « Puis trois finales perdues, en trois ans. En 2016, il rate son penalty… et quitte la sélection. Avant de revenir. » (6,7 s)

### p08 — Les finales perdues (0:14 → 0:16)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. Gloomy night after a lost final: a handmade paper-craft football captain in his late twenties: short dark-brown hair swept to the side made of layered paper strips, short trimmed dark beard made of fine paper shreds, no grey hair, warm brown eyes, slim build, sky-blue and white vertical striped football shirt with no logo and no crest, white captain armband on his left arm stands alone on a paper pitch, hands on hips, looking down, grey paper rain falling, opponents celebrating as small blurred paper figures in the background, cold blue light. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Slow orbit around him from his side to the front, grey paper raindrops falling, he lowers his head and closes his eyes, his chest rises with a sigh. The blurred celebration in the background continues. Heavy, sad, cold blue light. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

### p09 — Le penalty raté (0:16 → 0:18, sur « il rate son penalty »)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. View from just behind the penalty spot at night: a paper goal, a paper goalkeeper in grey crouched ready, crowd of tiny paper fans in sky-blue and red blurred behind, the white paper ball on the spot in the foreground. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Camera low behind the ball. The ball is kicked forward from below the frame, flies up and sails high over the crossbar while the goalkeeper dives the other way. The camera tilts up to follow the ball into the night sky, the crowd in the background raises its arms. Tension then disbelief. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

### p10 — Seul sur le banc (0:18 → 0:19, sur « et quitte la sélection »)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. a handmade paper-craft football captain in his late twenties: short dark-brown hair swept to the side made of layered paper strips, short trimmed dark beard made of fine paper shreds, no grey hair, warm brown eyes, slim build, sky-blue and white vertical striped football shirt with no logo and no crest, white captain armband on his left arm sits alone on a paper bench, elbows on knees, head down, tears, empty paper stadium seats behind, desaturated cold grey-blue light. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Static camera with a very slow push-in. He buries his face in his hands, then slowly lifts his head, eyes red, staring into the empty stands. A few paper leaves or scraps drift across the frame. Silence, loneliness, cold grey-blue light. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

### p11 — Le retour (0:19 → 0:21, sur « Avant de revenir »)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. Determined close-up of a handmade paper-craft football captain in his late twenties: short dark-brown hair swept to the side made of layered paper strips, short trimmed dark beard made of fine paper shreds, no grey hair, warm brown eyes, slim build, sky-blue and white vertical striped football shirt with no logo and no crest, white captain armband on his left arm, jaw set, looking straight into the camera, warm golden backlight rim on his paper hair, dark background with sky-blue light leaks. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Starts in silhouette, then the warm backlight grows and reveals his face as the camera pushes in quickly. He raises his eyes straight to the lens with determination, a light breeze moves his paper hair. Powerful, a turning point. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

## Scène 5 — « 2021 : enfin, la Copa América ! Et en 2022, au Qatar… champion du monde ! » (5,8 s)

### p12 — Lancé en l'air (0:21 → 0:23)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. Night, golden paper fireworks in the sky: his teammates (paper figures in the same sky-blue and white striped shirts) throw a handmade paper-craft football captain in his late thirties: short dark-brown hair swept to the side made of layered paper strips, full dark-brown beard made of fine paper shreds with a few grey strands, warm brown eyes, slim build, sky-blue and white vertical striped football shirt with no logo and no crest, white captain armband on his left arm up into the air in celebration, he holds a silver paper trophy above his head, paper confetti everywhere. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Low-angle camera. The teammates toss him up, he rises into the air holding the trophy high, hangs for a moment at the top, then falls back into their arms; golden paper fireworks burst in the sky, confetti swirls. Joyful, explosive. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

### p13 — La coupe (0:23 → 0:25, sur « 2022, au Qatar »)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. Low-angle shot: a handmade paper-craft football captain in his late thirties: short dark-brown hair swept to the side made of layered paper strips, full dark-brown beard made of fine paper shreds with a few grey strands, warm brown eyes, slim build, sky-blue and white vertical striped football shirt with no logo and no crest, white captain armband on his left arm lifts a tall golden paper trophy cup high above his head with both hands, rays of golden light behind, golden and sky-blue paper confetti raining down, ecstatic. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Slow crane-up from his chest to the golden trophy raised above his head. He lifts it higher, golden light rays sweep behind him, confetti rains down and swirls around the trophy, which glints. Triumphant, epic. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

### p14 — Le cri de joie (0:25 → 0:27, sur « champion du monde ! »)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. Close-up of a handmade paper-craft football captain in his late thirties: short dark-brown hair swept to the side made of layered paper strips, full dark-brown beard made of fine paper shreds with a few grey strands, warm brown eyes, slim build, sky-blue and white vertical striped football shirt with no logo and no crest, white captain armband on his left arm screaming with joy, mouth wide open, tears of joy, golden paper confetti all around, warm golden light. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Fast push-in on his face as he screams with joy, fists clenched near his face, tears of joy, golden confetti swirling in the foreground, flashes of camera lights. Pure euphoria. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

## Scène 6 — « 2026 : une dernière finale, perdue contre l'Espagne. Puis ce message : il a toujours tout donné pour ce maillot. » (6,5 s)

### p15 — La finale perdue (0:27 → 0:29)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. Night, on the pitch after a lost final: a handmade paper-craft football captain in his late thirties: short dark-brown hair swept to the side made of layered paper strips, full dark-brown beard made of fine paper shreds with a few grey strands, warm brown eyes, slim build, sky-blue and white vertical striped football shirt with no logo and no crest, white captain armband on his left arm stands with his head down in the foreground, behind him blurred opponents in red paper shirts celebrate, red and yellow paper confetti falling. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Slow push-in on him while red and yellow paper confetti falls in slow motion around him. He closes his eyes and breathes out, the celebration stays blurred behind him. Bittersweet, quiet. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

### p16 — La main sur le cœur (0:29 → 0:33, sur « il a toujours tout donné pour ce maillot »)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. Close-up of a handmade paper-craft football captain in his late thirties: short dark-brown hair swept to the side made of layered paper strips, full dark-brown beard made of fine paper shreds with a few grey strands, warm brown eyes, slim build, sky-blue and white vertical striped football shirt with no logo and no crest, white captain armband on his left arm placing his right hand flat on his heart over the striped shirt, eyes glistening, soft warm light, grey strands visible in his beard, dark background with soft bokeh. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
He slowly brings his right hand up and presses it flat on his heart, grips the striped shirt gently, looks down at it, then up. Very slow push-in, soft warm light, gentle bokeh drifting. Deeply emotional. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

## Scène 7 — « Six octobre, au Monumental de Buenos Aires : son tout dernier match avec l'Argentine. » (4,7 s)

### p17 — L'entrée sur la pelouse (0:33 → 0:36)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. Seen from behind and slightly above: a handmade paper-craft football captain in his late thirties: short dark-brown hair swept to the side made of layered paper strips, full dark-brown beard made of fine paper shreds with a few grey strands, warm brown eyes, slim build, sky-blue and white vertical striped football shirt with no logo and no crest, white captain armband on his left arm walks out of the tunnel onto the green paper pitch of a gigantic packed paper stadium at night, thousands of tiny paper fans with sky-blue and white flags, a long plain white paper banner across the stand, floodlights. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Camera follows him from behind as he walks out of the tunnel into the light; the stadium opens up, the crowd of paper fans rises, flags wave, foil phone lights sparkle, paper confetti starts to fall. Slow crane-up to reveal the whole stadium. Grand, emotional. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

### p18 — Le salut (0:36 → 0:38, sur « son tout dernier match »)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. Medium shot of a handmade paper-craft football captain in his late thirties: short dark-brown hair swept to the side made of layered paper strips, full dark-brown beard made of fine paper shreds with a few grey strands, warm brown eyes, slim build, sky-blue and white vertical striped football shirt with no logo and no crest, white captain armband on his left arm smiling and waving to the crowd with his right hand raised, stadium lights and tiny foil phone lights glittering behind him. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Slow arc shot around him as he raises his hand and waves to the stands, smiling with emotion, then puts his hand to his heart. The bokeh lights twinkle behind him. Warm, grateful. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

## Scène 8 — « Merci, Leo. Ton plus beau souvenir de Messi ? Dis-le en commentaire… et abonne-toi. » (5,2 s)

### p19 — Merci (0:38 → 0:40, sur « Merci, Leo »)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. Close-up of a handmade paper-craft football captain in his late thirties: short dark-brown hair swept to the side made of layered paper strips, full dark-brown beard made of fine paper shreds with a few grey strands, warm brown eyes, slim build, sky-blue and white vertical striped football shirt with no logo and no crest, white captain armband on his left arm with eyes closed, gentle smile, right hand on his heart, warm golden light, a few paper confetti floating. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Very slow push-in; he breathes in deeply with his eyes closed and a peaceful smile, golden light softly flickering on his face, a few paper confetti drifting slowly through the frame. Serene ending. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

### p20 — La tribune (0:40 → 0:43, fond pour « commente / abonne-toi »)
**Image** :
```
Photograph of a handmade paper-craft diorama: every element is cut, folded and layered paper and thin cardstock, visible paper fibers, slightly torn edges, tiny cast shadows between paper layers, matte gouache-painted paper. Macro lens, shallow depth of field, cinematic lighting. Vertical 9:16. Close view of the paper stand at night: rows of tiny paper fans holding up sky-blue and white paper flags and scarves, sky-blue and white paper confetti in the air. No text, no letters, no numbers, no logos, no brand marks, no crests.
```
**Vidéo** :
```
Slow lateral pan across the stand; the fans wave flags and scarves, confetti drifts down, the foil phone lights twinkle. Calm, so that text can sit on top. Keep everything made of paper and cardstock (no real skin, no real fabric), keep the character's face, hair, beard and proportions identical to the start frame, no morphing, no extra people appearing, no text appearing. Smooth cinematic motion, 5 seconds.
```

---

**Quand tu as les clips** :
- envoie-les-moi nommés `p01.mp4` … `p20.mp4` ;
- s'il en manque, je comble avec l'image fixe animée (zoom et panoramique lents) ;
- de mon côté, je coupe chaque clip au bon moment de la voix, j'ajoute les titres (2005, CARTON ROUGE, 18 ANS, CHAMPION DU MONDE…), les bruitages, les transitions en déchirure de papier et la fin « commente / abonne-toi ».
