# Mos e harro kush je : changements de la V5

Base : V4 (commit `fba92c0`, fichier conservé dans `v4/index-v4.html`, rendu dans `v4/mos-e-harro-kush-je-v4.mp4`).
Analyse et plan : `V5-ANALYSE.md`. Contrôles : `QUALITY-REPORT.md`.

## Image

- **Un seul canvas WebGL2** remplace les diapos CSS : chaque plan est rendu par un shader qui applique une
  parallaxe 2.5D (carte de profondeur, 5 itérations), un travelling avant (les plans proches grandissent plus vite
  que les lointains), des rayons de lumière tirés des hautes lumières de l'image vers sa vraie source, l'étalonnage,
  le vignettage et le grain.
- **Cartes de profondeur faites à la main** (`build-depth.py`) : ouverture de la fenêtre, volets et sol pour la
  fenêtre ; tirage, rebord et mur pour la photo ; ciel, tour, crêtes et coteau pour la kulla.
- **Montage refait** : 5 plans au lieu de 8 diapos, chacun avec un sujet, une taille de plan et un mouvement
  propres (traversée de la fenêtre ; avancée dans la photo puis panoramique du grand-père aux enfants ; recul le long
  du chemin, montée vers la tour et avancée vers sa fenêtre allumée ; le grand-père puis l'enfant ; montée de grue
  vers le soleil). Les changements de lieu ou d'époque passent par un voile de lumière chaude, les autres par un
  fondu. Une seule direction de mouvement par plan.
- **Ouverture immédiate** : la fenêtre éclairée est visible dès l'image 0 (la V4 sortait du noir en 1,4 s).
- **Hautes lumières maîtrisées** : la lumière se compresse doucement au-delà de 0,78, elle ne vire plus au blanc
  (la V4 brûlait le dernier plan de 23 à 24,8 s).
- **Signature** : un écho très sombre de la fenêtre d'ouverture reste derrière l'aigle (la rime du film). L'aigle
  sort de l'ombre dès 25,0 s, au lieu de 1,7 s de noir. Le titre apparaît mot à mot sur la voix, puis viennent le
  filet doré et le logo, agrandi de 140 à 250 px et entouré d'un anneau doré tracé à la main. Le logo lui-même n'est
  pas modifié.

## Texte

- **Sous-titres** : Inter 600 en 58 px au lieu de 50 px, bloc ancré dans une zone de sécurité vérifiable (x 120–960,
  rien sous y 1408) ; un mot-clé par phrase en or, sans soulignement rouge.
- **Mots recalés sur la voix** (`build-cues.py`) : chaque début de mot est placé sur le creux d'énergie le plus proche
  (±120 ms). Médiane du décalage 60 ms, maximum 130 ms.
- **Plus de doublon final** : « Mos e harro kush je. » n'est plus à la fois sous-titre et titre ; seul le titre
  l'affiche, synchronisé sur la voix.
- **Texte albanais inchangé** : relu mot à mot, il est cohérent en guègue (zâ, nana, asht, veç, prej kah) et rien
  n'imposait une correction. La phrase finale est intacte.
- **Fichiers nouveaux** : `mos-e-harro-kush-je.srt`, et une version sans sous-titres incrustés (variable
  HyperFrames `subtitles`).

## Son

- **Musique** : « Porsi fleta e diellit të Zotit », choisie par l'auteur, qui en a confirmé les droits. Les 30,3
  dernières secondes du morceau sont calées sur le film :
  - à 11,6 s, une section plus forte démarre sous « Edhe kur jeta » ;
  - à 24,9 s, la dernière phrase démarre sur l'arrivée de l'aigle ;
  - à 28,8 s, la cadence finale arrive et s'éteint d'elle-même à 30 s.

  Il n'y a plus de coupe brutale ni de silence involontaire.
- **Voix** : passe-haut à 80 Hz, compression 2:1 au-dessus de −26 dBFS, réverbération courte (RT60 de 0,8 s,
  22 dB sous le signal direct).
- **Mixage** (`build-mix.py`) :
  - le niveau de la musique suit les actes : retenu sous le souvenir, ouvert à partir de la transmission, plein sur
    la signature ;
  - la musique baisse de 13 dB sous la voix, avec un creux supplémentaire de 4 dB entre 1,2 et 4 kHz.

  Résultat : la voix passe à +9,6 dB au-dessus de la musique pendant la parole, à −14,5 LUFS intégrés.

## Export

- H.264 High, yuv420p, 30 i/s constants, 900 images, débit ramené entre 12 et 20 Mb/s, AAC 48 kHz stéréo, moov en tête.

## Recompiler

Depuis `mos-e-harro-kush-je/`. Le morceau doit être déposé dans `assets/music/source/porsi-fleta-e-diellit.mp3` :
il n'est pas versionné, car c'est un enregistrement tiers.

```
python3 build-voice.py        # voix montée + cues.json (depuis assets/audio/prise-A.mp3)
python3 build-cues.py         # cues-v5.json + mos-e-harro-kush-je.srt
python3 build-depth.py        # cartes de profondeur
python3 build-mix.py          # assets/audio/mix.wav
npx hyperframes render --quality high --fps 30 --output renders/v5-master.mp4
npx hyperframes render --quality high --fps 30 --variables '{"subtitles":false}' --output renders/v5-nosubs-master.mp4
ffmpeg -i renders/v5-master.mp4 -i assets/audio/mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -profile:v high \
  -level 4.1 -crf 16 -maxrate 20M -bufsize 30M -pix_fmt yuv420p -r 30 -g 60 -c:a aac -b:a 256k -ar 48000 -ac 2 -t 30 \
  -movflags +faststart delivery/mos-e-harro-kush-je-v5-final.mp4
bash qa.sh delivery/mos-e-harro-kush-je-v5-final.mp4
```

Chaque rendu prend environ 25 minutes sur ce conteneur (le shader tourne sur le GPU logiciel).

## Limites connues

- Trois images seulement : le quota gratuit d'images ElevenLabs est épuisé et la vidéo exige une offre payante. Les
  cinq scènes prévues en plus ne sont pas inventées. Leurs prompts attendent sur le flow
  https://elevenlabs.io/app/flows/vvGp3CYtnhLB0jmMUuSi, et le moteur de plans accepte une nouvelle image en
  ajoutant une entrée à `SHOTS`.
- Les images sont des illustrations générées par IA, pas des archives : la photo de famille n'est pas un document
  historique.
- Le son n'a pas pu être écouté ici : il a été réglé et vérifié sur mesures. Une écoute au casque reste à faire.
