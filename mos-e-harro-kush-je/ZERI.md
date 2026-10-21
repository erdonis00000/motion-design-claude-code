# Mos e harro kush je : voix et finalisation

## Texte à coller dans ElevenLabs (Eleven v4, langue : albanais)

Voix masculine grave, chaude, calme. Stabilité 45 %, Similarité 85 %. Générer 2 ou 3 prises.

```
Ka vende që i lamë mbrapa... por që kurrë nuk na lanë neve.

Në zânin e gjyshërve, në fjalët e nanës, jeton kujtesa jonë.

Edhe kur jeta na çon larg, gjuha na e kujton prej kah vijmë.

Sepse trashëgimia nuk asht veç ajo që marrim... asht edhe ajo që ua lamë brezave.

Mos e harro kush je.
```

Repères de l'image (en secondes), que la prise doit suivre :

| Phrase | Début | Fin |
| --- | --- | --- |
| 1 | 0,8 | 4,9 |
| 2 | 5,8 | 10,6 |
| 3 | 11,5 | 17,0 |
| 4 | 18,6 | 24,4 |
| 5 (après le silence) | 26,4 | 28,1 |

## Poser la voix

1. Déposer la prise dans `assets/audio/voix.mp3`. Caler chaque phrase sur son début en coupant seulement dans les silences, puis exporter `assets/audio/voix-montage.wav` (30 s).
2. Relever les mots :
   - `python3 ../.claude/skills/motion-design/scripts/mots.py assets/audio/voix-montage.wav`
   - `python3 ../.claude/skills/motion-design/scripts/onsets.py assets/audio/voix-montage.wav --transcript assets/audio/voix-montage-mots.json --out onsets.json`
3. Recopier les temps des mots dans le tableau `CUES` de `index.html` : ce sont les sous-titres.
4. Ajouter la voix dans `index.html`, à côté de la musique :
   `<audio id="voix" src="assets/audio/voix-montage.wav" data-start="0" data-duration="30" data-track-index="9"></audio>`
   Baisser ensuite la musique sous la voix, avec `data-volume="0.5"` sur `#score`.
5. Rendre le film : `npx hyperframes render --quality high --fps 30 --output renders/mos-e-harro-kush-je.mp4`

## Musique

`assets/music/temp-score.wav` est une musique temporaire, synthétisée par `build-score.py`. Elle respecte la structure demandée : piano doux, cordes qui montent, cordes pincées façon çifteli, tambour façon lodër, climax à 23,5–24,8 s, arrêt net à 24,85 s, puis une seule note après « Mos e harro kush je ». Pour la remplacer par une musique sous licence, garder le même nom de fichier ou changer le `src` de `#score`.
