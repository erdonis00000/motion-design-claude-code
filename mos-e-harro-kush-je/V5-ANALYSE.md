# Mos e harro kush je : analyse de la V4 et plan de la V5

## 1. Système de production

- **HyperFrames 0.8.82** (HTML + GSAP, rendu Chromium sans GPU, image par image). C'est le pipeline existant, il est
  conservé : pas de migration vers Remotion, qui n'apporterait rien ici.
- **Médias originaux disponibles** : trois images IA en 1152 × 2048 (`assets/img/ia/`), la prise de voix ElevenLabs
  (`assets/audio/prise-A.mp3`, montée par `build-voice.py`), l'aigle détouré (`eagle-white.png`, 1288 × 1432), le logo
  (`logo.png`, 640 × 640, seul fichier fourni : pas de vectoriel), les polices Cinzel et Inter (woff2, diacritiques
  albanais ë ç â présents), et la musique choisie pour la V5, « Porsi fleta e diellit të Zotit »
  (`assets/music/source/`, droits confirmés par l'auteur du film).
- **Limites constatées** :
  - l'offre gratuite ElevenLabs bloque toute nouvelle image (quota journalier atteint) et toute vidéo (offre
    payante). Les cinq images prévues en plus (grand-mère, ville, cahier, trois générations, panorama) n'existent donc
    pas. La V5 est construite avec les trois images existantes, sans en inventer d'autres ;
  - aucun modèle de profondeur (pas de torch, pas d'OpenCV) : les cartes de profondeur sont faites à la main
    (`build-depth.py`) ;
  - je ne peux pas écouter le son : tous les jugements audio reposent sur des mesures (niveaux, spectrogramme,
    rapport voix/musique).

## 2. Audit de la V4 (planche à 2 images/s et mesures)

| Défaut | Importance | Constat | Correction V5 |
| --- | --- | --- | --- |
| Répétition des trois univers | Haute | 8 plans, mais chaque image revient 3 fois (fenêtre 0–3, 14–18, 21–25 ; photo 3–11 ; tour 5–8, 11–14, 18–21) | 5 plans, chacun avec un sujet, une taille de plan et un mouvement propres ; chaque image revient au plus deux fois, sous un autre angle |
| Mouvements | Haute | Zoom générique sur une image plate, partout | Parallaxe 2.5D par carte de profondeur (WebGL), travellings motivés : traversée de la fenêtre, panoramique dans la photo, panoramique vertical du chemin vers la tour, montée de grue vers la lumière |
| Ouverture lente | Moyenne | 1,4 s de sortie du noir avant la première image | Première image visible dès l'image 0 : fenêtre éclairée, rayons, poussière, caméra déjà en mouvement |
| Hautes lumières brûlées | Haute | 23–24,8 s : le dernier plan vire au blanc (perte totale de détail) | Étalonnage avec compression douce des hautes lumières : la lumière monte sans jamais écrêter |
| Trou à 24,9–26,6 s | Haute | Noir et silence total (−180 dB) pendant 1,7 s, puis aigle | La dernière phrase du morceau démarre à 24,9 s ; l'aigle sort de l'ombre dès 25,0 s sur un écho sombre de la fenêtre (rime avec l'ouverture) |
| Fin à 27,8–30 s | Moyenne | Résonance de musique synthétique à −60/−100 dB, fin presque muette | La cadence finale du morceau tombe à 28,8 s et s'éteint d'elle-même à 30 s |
| Phrase finale en double | Moyenne | « Mos e harro kush je. » en sous-titre à 26,6 s puis en titre à 28,2 s | Plus de sous-titre : le titre apparaît mot à mot sur la voix (26,6 → 27,5 s) |
| Sous-titres petits, bas | Moyenne | Inter 50 px, y 1395–1525 | Inter 58 px, bloc ancré dans une zone de sécurité vérifiable (x 120–960, bas à 1408 px) |
| Logo petit | Moyenne | 140 px | 250 px, détouré à son cercle d'origine, anneau doré tracé autour (le logo n'est pas modifié) |
| Synchronisation des mots | Moyenne | Mots répartis par voyelles, à ±100 ms | Débuts de mots recalés sur les creux de la voix (`build-cues.py`, médiane 60 ms, maximum 130 ms) |
| Voix et musique | Haute | Musique synthétique de remplacement ; −16,4 LUFS | Morceau choisi par l'auteur, voix traitée (passe-haut, compression 2:1, petite pièce), baisse de la musique sous la voix, −14 LUFS |

## 3. Trois directions, évaluées

| Critère (sur 5) | A. Héritage cinématographique | B. Transmission générationnelle | C. Éditorial cinétique |
| --- | --- | --- | --- |
| Émotion | 5 | 5 | 3 |
| Cohérence narrative | 4 | 5 | 3 |
| Qualité visuelle atteignable | 5 | 2 (exige des scènes contemporaines qu'on ne peut pas générer) | 4 |
| Faisabilité technique | 4 | 1 | 4 |
| Authenticité culturelle | 5 | 4 | 3 |
| Originalité | 3 | 4 | 4 |
| Lecture sur téléphone | 4 | 4 | 3 (texte en plus des sous-titres) |
| Puissance de la conclusion | 4 | 5 | 4 |

**Choix : A**, avec de B la seule chose réalisable, le motif de transmission dans le cadre (le regard qui passe du
grand-père à l'enfant de la photo). De C, je ne garde qu'une typographie éditoriale réservée à la signature finale.
B demanderait des scènes d'aujourd'hui, introuvables sans nouvelles images.

## 4. Charte de réalisation

- **Cadrage** : un sujet par plan, au tiers ou au centre ; les visages restent hors de la bande des sous-titres.
- **Palette** : ambre chaud, rouge profond, noirs à 0,012 (jamais bouchés), désaturation de 10 %, hautes lumières
  compressées au-delà de 0,78.
- **Mouvement** : une caméra qui ne s'arrête jamais (sine.inOut sur la durée du plan), une seule direction par plan,
  accélération (power2.in) seulement pour entrer dans la lumière.
- **Profondeur** : parallaxe par carte de profondeur, avec un décalage de 1 % au plus et un effet de travelling
  avant limité, pour ne déchirer aucun contour.
- **Lumière** : rayons tirés des hautes lumières de l'image elle-même, vers la source réelle de chaque plan
  (fenêtre, soleil).
- **Grain** : grain argentique déterministe (un motif par image), plus fort dans les tons moyens.
- **Transitions** : deux types seulement. Le passage par un voile de lumière chaude pour changer de lieu ou d'époque
  (fenêtre → photo, photo → tour), le fondu pour rester dans la même idée (tour → photo → tour).
- **Typographie** : Inter 600 pour les sous-titres, un mot-clé par phrase en or ; Cinzel 700 pour le titre final.

## 5. Storyboard (900 images, 30 i/s)

| Temps | Voix | Plan | Mouvement | Musique |
| --- | --- | --- | --- | --- |
| 0,00–6,05 | Ka vende që i lamë mbrapa… por që kurrë nuk na lanë neve. | A. La fenêtre de la maison, l'aube sur les montagnes | Poussée lente puis traversée de l'ouverture : les volets glissent hors du cadre, les montagnes viennent à nous | Entrée du morceau en 0,9 s, sous la voix |
| 5,45–6,05 | (transition) | Voile de lumière : le ciel de la fenêtre devient le papier de la photo | | |
| 5,45–11,75 | Në zânin e gjyshërve, në fjalët e nanës, jeton kujtesa jonë. | C. La photo de famille sur le rebord | Avancée vers le tirage, puis panoramique dans la photo : du grand-père aux femmes, puis aux enfants | |
| 10,95–11,75 | (silence de la voix) | Voile de lumière : changement d'époque, de la photo au lieu réel | | Nouvelle section, plus forte, à 11,6 s |
| 10,95–18,35 | Edhe kur jeta na çon larg, gjuha na e kujton prej kah vijmë. | E. Le chemin pavé, puis la tour | Recul le long du chemin (« larg »), puis montée vers la tour, puis avancée vers sa fenêtre allumée (« prej kah vijmë ») | |
| 17,75–21,95 | Sepse trashëgimia nuk asht veç ajo që marrim… | G. La photo, de près | Du visage du grand-père à l'enfant : la transmission dans le cadre | Montée de niveau à 18,8 s |
| 21,35–25,20 | asht edhe ajo që ua lamë brezave. | H. La tour, du chemin jusqu'au ciel | Montée de grue vers le soleil, la lumière grandit sans brûler | |
| 24,85–30,00 | Mos e harro kush je. | Signature : écho sombre de la fenêtre, aigle, titre mot à mot sur la voix, filet, logo et son anneau | Lent recul, l'aigle monte de 8 px | Dernière phrase du morceau à 24,9 s, cadence à 28,8 s, extinction à 30 s |
