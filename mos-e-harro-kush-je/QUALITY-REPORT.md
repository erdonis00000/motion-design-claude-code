# Mos e harro kush je V5 : rapport qualité

Ce rapport ne contient que des contrôles réellement exécutés dans cette session, avec leur outil. Ce qui n'a pas pu
être fait est dit dans la section 5.

## 1. Passes de rendu

| Passe | Rendu | Contrôles | Défauts trouvés | Correction |
| --- | --- | --- | --- | --- |
| 0 (prévisualisations) | `hyperframes snapshot` à 19 instants, puis 9 instants autour des transitions | Lecture de chaque image | Masque de l'aigle absent ; transition fenêtre → photo confuse (dominante rose superposée) ; climax éteint par un fondu trop précoce | Transition « voile de lumière » réécrite ; climax prolongé jusqu'à 25,2 s, fondu vers la signature décalé à 24,85 s |
| 1 : structure | `renders/v5-pass1.mp4`, complet | `qa.sh` + planche à 2 images/s + inspection à 100 % du logo et du gros plan sur la photo | 0–4 s trop statique ; plongée dans la photo et avancée vers la tour trop timides ; débit de 49 Mb/s | Poussée sur la fenêtre portée de ×1,30 à ×1,42 dès 3,1 s ; zooms de 2,12 à 2,40 sur la photo et de 1,82 à 2,15 sur la tour ; parallaxe d'ouverture plus large |
| 2 : visuel | `renders/v5-pass2.mp4`, complet | `qa.sh` + planche + empreinte md5 d'images comparées à la passe 1 (le rendu a bien changé) | Aucun défaut visuel bloquant | — |
| 3 : son et finition | `delivery/mos-e-harro-kush-je-v5-final.mp4` (vidéo de la passe 2 + mixage final) | Rapport voix/musique par acte, enveloppe de la piste finale, SSIM/PSNR contre le master, `qa.sh` | Dernière réplique noyée : voix à +0,9 dB au-dessus de la musique sur « Mos e harro kush je » | Musique baissée de 5 dB et ducking de 13 dB sous la dernière phrase, puis remontée pour la cadence : +8,9 dB |

## 2. Contrôle technique du fichier final (`qa.sh`)

| Point | Mesure | Cible |
| --- | --- | --- |
| Format | H.264 High, 1080 × 1920, yuv420p | ✓ |
| Cadence | 30/1 constant (r_frame_rate = avg_frame_rate) | ✓ |
| Images | 900 (comptées par décodage complet) | 900 ✓ |
| Durée | vidéo 30,000 s, audio 30,000 s, départs à 0,000 | synchronisés ✓ |
| Débit vidéo | 19,2 Mb/s | 12–20 ✓ |
| Audio | AAC LC, 48 kHz, stéréo, 256 kb/s | ✓ |
| Lecture progressive | ordre des atomes : ftyp moov free mdat | moov en tête ✓ |
| Erreurs de décodage | aucune (`ffmpeg -v error … -f null`) | ✓ |
| Images noires ≥ 0,1 s | aucune (blackdetect, pixel ≤ 0,06, image ≥ 98 %) | ✓ |
| Images figées ≥ 0,5 s | aucune (freezedetect) | ✓ |
| Sonie intégrée | −14,5 LUFS | env. −14 ✓ |
| True peak | −1,4 dBTP | ≤ −1 ✓ |
| LRA | 7,6 LU | dynamique conservée |
| Perte du réencodage | PSNR moyen 44,1 dB (min 40,3) ; SSIM 0,977 | sans perte visible |

La version sans sous-titres (`delivery/mos-e-harro-kush-je-v5-sans-sous-titres.mp4`, rendue avec la variable
`subtitles: false`) passe les mêmes contrôles : 900 images, 19,3 Mb/s, moov en tête, aucune image noire ni figée,
−14,5 LUFS, −1,4 dBTP. Vérifié à 4,0 s (aucun sous-titre) et à 29,5 s (titre et logo présents).

## 3. Contrôles visuels

- **Planches à 2 images/s** des passes 1, 2 et finale, et comparaison V4/V5 aux mêmes instants
  (`delivery/comparaison-v4-v5.jpg`).
- **Pleine résolution** :
  - image 0 (accroche : fenêtre éclairée, rayons, grain) ;
  - 29,6 s (signature complète) ;
  - logo recadré à 100 % : net, cercle d'origine respecté, pas de frange blanche, proportions intactes ;
  - gros plan du grand-père à 19,2 s : doux mais crédible pour un tirage ancien, sans artefact de parallaxe.
- **Transitions** : 5,55 / 5,75 / 5,95 s (fenêtre → photo), 11,2 / 11,5 s (photo → tour), 23,0 / 24,5 / 24,95 /
  25,3 s (climax → signature). Le voile de lumière ne brûle pas, aucun mélange confus.
- **Hautes lumières** : 23,5–24,9 s, le ciel monte jusqu'à une valeur proche de 1 sans écrêter. La V4 virait au blanc
  à cet endroit.
- **Textes** :
  - aucune collision entre sous-titres et titre : le sous-titre final est supprimé et le titre arrive à 26,6 s,
    après le dernier sous-titre (fin à 24,0 s) ;
  - sous-titres dans la zone x 120–960, bas du bloc à y 1408 ;
  - titre de x 155 à 915 ; logo de y 1205 à 1455.
- **Lint HyperFrames** : 0 erreur, 2 avertissements de structure (sections non découpées en sous-compositions),
  sans effet sur le rendu.

## 4. Son (mesures, `build-mix.py`)

- Rapport voix/musique pendant la parole : +15,9 dB (0–11 s), +10,2 dB (11,6–18 s), +11,5 dB (18,6–24 s), +8,9 dB
  (dernière phrase).
- Enveloppe de la piste finale :
  - entrée de la musique en 0,9 s ;
  - respiration de 10,3 à 11,5 s (−35 à −23 dB) ;
  - nouvelle section à 11,6 s ;
  - dernière phrase du morceau à 24,9 s ;
  - cadence à 28,4 s, extinction à −32 dB à 30 s.

  Aucun silence involontaire : le point le plus bas, −61 dB, est la toute première image, avant l'entrée de la
  musique.
- Débuts de mots recalés sur la voix : 47 mots, déplacement médian de 60 ms, maximum de 130 ms.

## 5. Ce qui n'a pas pu être vérifié

- **Écoute** : je ne peux pas écouter le son. Timbre de la voix, présence éventuelle de chant dans le morceau sous
  la voix et naturel du mixage sont réglés sur mesures (niveaux, spectrogramme) : une écoute au casque et sur
  haut-parleur de téléphone est nécessaire avant diffusion.
- **Albanais** : texte relu mot à mot et laissé tel quel. Je ne suis pas locuteur natif du guègue, une relecture par
  un locuteur reste conseillée. La prononciation de la voix ElevenLabs (voix anglophone, modèle multilingue) n'a pas
  pu être jugée.
- **Lecture sur un vrai téléphone** : la zone de sécurité est calculée (marges de 120 px à droite, 210 px en haut,
  420 px en bas), mais elle n'a pas été vérifiée dans une application réelle.
- **Diversité des plans** : limitée par les trois seules images disponibles (voir `CHANGELOG-V5.md`).

## 6. V6 (une seule apparition par image)

| Point | Fichier final | Sans sous-titres |
| --- | --- | --- |
| Images | 900, 30/1 constant | 900, 30/1 constant |
| Débit vidéo | 19,9 Mb/s | 19,9 Mb/s |
| moov en tête | ✓ | ✓ |
| Erreurs de décodage | aucune | aucune |
| Images noires ≥ 0,1 s / figées ≥ 0,5 s | aucune / aucune | aucune / aucune |
| Sonie / true peak | −14,5 LUFS / −1,4 dBTP | −14,5 LUFS / −1,4 dBTP |

- **Règle d'une seule apparition** : la planche à 2 images/s du fichier final montre six blocs continus, sans aucun
  retour : fenêtre 0–6 s, photo 6–11,5 s, ville 11,5–14 s, cahier 14–17 s, kulla 17–21,5 s, panorama
  21,5–30 s. Dans `SHOTS`, chaque valeur de `img` n'est utilisée qu'une fois.
- **Transitions contrôlées** :
  - photo → ville à 11,4 s (voile de lumière) ;
  - ville → cahier à 14,15 s (fondu) ;
  - cahier → kulla à 16,8 s (la flamme devient la fenêtre) ;
  - oiseau → emblème à 24,9 / 25,1 / 25,3 / 25,6 s. Un premier essai laissait l'oiseau visible à travers
    l'emblème : corrigé, puis revérifié sur le fichier final aux images 759 et 768.
- **Raccord à l'image 735** vérifié : masters identiques entre 24,05 et 24,5 s (PSNR de 46,9 dB), écart régulier entre
  images consécutives (0,65 à 0,84 sur 255).

## 7. V7 (les illustrations prennent vie)

| Point | Fichier final | Sans sous-titres |
| --- | --- | --- |
| Images | 900, 30/1 constant | 900, 30/1 constant |
| Débit vidéo | 19,9 Mb/s | 19,9 Mb/s |
| moov en tête | ✓ | ✓ |
| Erreurs de décodage | aucune | aucune |
| Images noires ≥ 0,1 s / figées ≥ 0,5 s | aucune / aucune | aucune / aucune |
| Sonie / true peak | −14,5 LUFS / −1,4 dBTP | −14,5 LUFS / −1,4 dBTP |

- **Animations présentes dans les fichiers finaux** : comparaison avec la V6 aux images 60, 378, 585 et 690. Les
  différences sont dans les zones prévues (poussière et rayons, fenêtres et rivière, herbe et lampe, aigle et nuages),
  et nulle part ailleurs.
- **Régularité d'une image à l'autre**, écart moyen entre images consécutives par plan. Le rapport entre l'écart maximal
  et l'écart médian reste entre 1,1 et 1,9 dans tous les plans animés : aucun saut, aucun scintillement.
  - Le plus grand écart du film (18,6 à l'image 342) est le voile de lumière voulu entre la photo et la ville.
  - L'image la plus sombre (761) est la scène noire de la signature.
- **Image 0** de la version sans sous-titres : noire au rendu (textures pas encore prêtes), corrigée dans la livraison
  et dans le code. Voir `CHANGELOG-V7.md`. L'image 0 vérifiée sur les six fichiers V5, V6 et V7 a une moyenne de 42,3
  à 42,5.
- **Pendant le réglage** :
  - A/B avec et sans animation (variable `animate`) ;
  - banc Chromium à l'image près pour la flamme, l'eau, la lampe et l'aigle ;
  - inspection à 400 % du bord des volets dans la brume, sans traînée ;
  - grain du ciel reconstitué derrière l'aigle mesuré à 3,04, contre 3,01 pour le ciel d'origine.
- **Non vérifiable ici** : je ne peux pas regarder la vidéo défiler. Le jugement sur le mouvement repose sur des
  séquences d'images rapprochées et sur des mesures. Un visionnage sur téléphone reste nécessaire.
