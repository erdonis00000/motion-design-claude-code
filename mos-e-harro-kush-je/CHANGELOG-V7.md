# Mos e harro kush je : changements de la V7, les illustrations prennent vie

Base : la V6 (six illustrations, chacune vue une seule fois, même montage, même mixage, mêmes sous-titres). La V7
anime l'intérieur des images. Chaque mouvement a une cause physique dans le plan (vent, eau, flamme, lumière) et reste
sous le seuil où l'œil lit un « effet » : quelques pixels de déplacement, quelques pour cent de lumière.

## Ce qui vit, plan par plan

| Plan | Ce qui bouge | Ce qui ne bouge pas, volontairement |
| --- | --- | --- |
| Fenêtre (0–6 s) | La mer de brume dérive sous les sommets ; des voiles de brume passent ; les rayons respirent lentement ; des grains de poussière flottent et s'allument dans les rayons | Les volets, le mur, les montagnes |
| Photo (6–11,7 s) | Un reflet de soleil glisse lentement sur le papier, comme quand un nuage passe ; poussière dans la lumière | Les personnes : une photographie ne bouge pas, et animer des visages ferait du morphing |
| Ville (11–14,4 s) | La rivière ondule et brise les colonnes de reflet des lampadaires ; des éclats courts sur les vaguelettes ; quelques fenêtres s'allument pendant le plan | Le château, le minaret et le clocher éclairés, le ciel |
| Cahier (14–17 s) | La flamme ondule, davantage à sa pointe ; l'air tremble au-dessus ; sa lumière vacille sur la page ; une vraie faible profondeur de champ (mise au point sur la plume, écriture adoucie) | La plume, la page |
| Kulla (16,6–21,9 s) | L'herbe plie sous des rafales qui traversent la pente ; la lampe de la fenêtre palpite ; la brume des crêtes lointaines dérive | Les murs de pierre et le chemin (tracés à la main hors de la zone du vent) |
| Panorama (21,4–30 s) | L'aigle plane de gauche à droite, s'incline légèrement et grandit en approchant ; les nuages et la brume des vallées dérivent ; les rayons respirent. Il arrive exactement là où apparaît l'emblème | Les crêtes |

## Comment

- **`build-anim.py`** produit, pour chaque image, une carte RVB qui dit où elle peut bouger :
  - R : brume et nuages ;
  - G : eau, ou herbe sur une image sans eau ;
  - B : flamme, lampe ou fenêtres allumées.

  Les zones sont tirées de la couleur de l'image quand c'est fiable (eau, flamme, fenêtres), et tracées à la main quand
  la couleur trompe : sur la kulla, le mur éclairé par le soleil a la même teinte que l'herbe sèche.
- **L'aigle** est détouré à pleine résolution. L'alpha vient de son contraste avec le ciel, et la couleur du ciel est
  retirée des bords des plumes. Le ciel derrière lui est reconstitué par une surface lisse ajustée sur le pourtour,
  avec le même grain que le ciel voisin (écart-type de 3,04 contre 3,01 pour l'original) : `08-alpet-ciel.jpg`,
  `08-alpet-aigle.png`.
- **Le shader** de `index.html` applique les animations à partir du temps du film : déterministe, image par image. La
  table `ANIM` règle chaque plan au même endroit que la table `SHOTS`, et la table `EAGLE` donne la trajectoire de
  l'aigle.
- **La variable `animate`** (par défaut `true`) coupe toute la vie des images pour un contrôle A/B : avec `false`,
  seule la caméra bouge.
- **Les variables par défaut** déclarées sur `<html>` sont désormais lues aussi hors du moteur HyperFrames, en
  aperçu dans un navigateur.

## Contrôles faits pendant le réglage

- **A/B à instant identique**, avec et sans animation, et carte de différence : chaque animation ne touche que sa
  zone. L'écart moyen va de 0,1 à 1,6 sur 255 selon le plan.
- **Images consécutives à l'image près**, capturées par un banc Chromium qui place la timeline exactement : l'outil
  `snapshot` ne cale pas les instants assez précisément pour juger un mouvement. Ce banc a servi pour la flamme,
  l'eau, la lampe (luminosité de 146 à 166 sur 1,6 s, sans saut) et la trajectoire de l'aigle.
- **Défauts trouvés et corrigés en cours de réglage** :
  - **Cartes d'animation** : la couche alpha effaçait les couleurs au décodage, elles sont passées en RVB.
  - **Fenêtres de la ville** : la bande orange de l'horizon était prise pour des fenêtres.
  - **Herbe de la kulla** : son masque débordait sur les pierres.
  - **Scintillement de la rivière** : trop dispersé, il est limité aux reflets des lampadaires.
  - **Reflet sur la photo** : il passait hors du tirage.
  - **Flamme** : elle n'apparaissait que pendant la transition.
  - **Flou du cahier** : il était étiré à la verticale, et la mise au point était sur la page au lieu de la plume.

## Rendu et livraison

- Deux rendus complets lancés en parallèle (avec et sans sous-titres), de 81 et 87 minutes : les animations alourdissent
  le shader, qui tourne sur le GPU logiciel.
- **Défaut trouvé au contrôle final et corrigé** : dans la version sans sous-titres, l'image 0 était noire. Le moteur
  l'avait capturée avant que les textures soient prêtes. Une image isolée échappe à `blackdetect` (seuil de 0,1 s) et à
  la planche à 2 images/s ; la mesure de l'écart entre images consécutives l'a révélée.
  - **Dans la livraison** : l'image 0 vient de la version avec sous-titres, identique à cet instant puisque le premier
    sous-titre arrive à 0,8 s.
  - **Dans le code** : chaque texture est chargée dès que son image est décodée, puis l'image en cours est redessinée.
  - **V5 et V6** : vérifiées, leur image 0 est saine.
