# Mos e harro kush je : changements de la V6

Base : la V5 (même moteur WebGL, même mixage, mêmes sous-titres, même signature). Une seule règle nouvelle,
demandée par l'auteur : **chaque illustration n'apparaît qu'une fois**. Une fois son plan terminé, on ne la revoit plus.

## Nouvelles illustrations (ElevenLabs, Seedream 5 Pro, 1152 × 2048)

- `05-qyteti.jpg` : une vieille ville des Balkans au crépuscule (château, minaret, clocher, pont de pierre). Elle n'est
  pas présentée comme une ville réelle précise.
- `06-fletorja.jpg` : un cahier ancien écrit à la plume, éclairé par une bougie. L'écriture est volontairement
  illisible.
- `08-alpet.jpg` : un panorama des Alpes albanaises au coucher du soleil, avec un aigle dans le ciel.

Leurs cartes de profondeur sont ajoutées à `build-depth.py`.

## Montage : six images, six plans, aucune reprise

| Temps | Voix | Image | Mouvement | Passage au plan suivant |
| --- | --- | --- | --- | --- |
| 0,00–6,05 | Ka vende që i lamë mbrapa… por që kurrë nuk na lanë neve. | Fenêtre | Traversée de l'ouverture | Voile de lumière |
| 5,45–11,75 | Në zânin e gjyshërve, në fjalët e nanës, jeton kujtesa jonë. | Photo de famille | Avancée puis panoramique du grand-père aux enfants | Voile de lumière |
| 10,95–14,35 | Edhe kur jeta na çon larg, | Ville au crépuscule | Recul et montée depuis le pont : la ville s'éloigne | Fondu |
| 13,95–17,15 | gjuha na e kujton prej kah vijmë. | Cahier et bougie | De l'écriture à la plume, puis vers la flamme | Voile de lumière : la flamme devient la fenêtre allumée de la kulla |
| 16,55–21,95 | Sepse trashëgimia nuk asht veç ajo që marrim… | Kulla | De la fenêtre allumée au chemin : ce qu'on reçoit, et le chemin qui continue | Fondu |
| 21,35–30,00 | asht edhe ajo që ua lamë brezave. puis la signature | Panorama des Alpes | Montée vers le soleil et l'aigle dans le ciel, puis le plan s'assombrit et l'aigle de la signature apparaît là où volait l'oiseau | — |

**Reprises supprimées par rapport à la V5** :
- la photo revenait de 17,75 à 21,95 s ;
- la tour revenait de 21,35 à 24,95 s ;
- la fenêtre réapparaissait en écho derrière la signature.

## Encore à venir

Deux illustrations du plan d'origine restent à générer : la grand-mère à la lampe à huile (`04-gjyshja.jpg`) et les
trois générations face aux montagnes (`07-brezat.jpg`). L'offre gratuite ElevenLabs ne donne que 3 images par jour.
Leurs nœuds attendent sur le flow https://elevenlabs.io/app/flows/vvGp3CYtnhLB0jmMUuSi.

- **La grand-mère** prendrait « jeton kujtesa jonë » (8,6–11 s), à la place de la fin du panoramique sur la photo.
- **Les trois générations** prendraient « Sepse trashëgimia… marrim… » (18,6–21,4 s), à la place de la fin du plan
  sur la kulla.

Le plan voisin est raccourci d'autant, ce qui garde la règle d'une seule apparition par image.

## Signature : de l'oiseau à l'emblème

L'aigle du panorama vole à l'endroit exact où l'aigle de la signature apparaît. Le panorama s'assombrit entre 24,85 et
25,35 s, et l'emblème devient opaque en 0,7 s : l'oiseau se fond dans l'emblème sans transparaître à travers lui.
Le fond de la signature est désormais la fin, très sombre, du panorama : c'est le même plan qui continue, pas une
reprise.

## Rendu

- Les deux versions sont rendues avec HyperFrames, en 30 minutes chacune.
- **Version sans sous-titres** : un rendu complet.
- **Version avec sous-titres** : un rendu complet pour les images 0 à 734, puis la fin de la version sans
  sous-titres à partir de l'image 735 (24,5 s). Après 24,0 s il n'y a plus de sous-titre, et la dernière correction
  (oiseau et emblème) ne touche que les images après 24,85 s. Le raccord a été vérifié : les deux masters sont
  identiques entre 24,05 et 24,5 s (PSNR de 46,9 dB, bruit d'encodage seul), et l'écart entre images consécutives
  reste régulier autour de l'image 735.
