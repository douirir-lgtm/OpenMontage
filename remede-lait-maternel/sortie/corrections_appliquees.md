# REMEDE — version corrigée : corrections appliquées

Vidéo : `sortie/remede-9x16-corrigee.mp4` (la 1re version et ses fichiers ne sont pas modifiés).
Base : `sortie/verification_scientifique.md`. Rien d'autre n'a été changé : aucun autre chiffre, verset, hadith ni référence
(sauf le doute n° 2 plus bas, à trancher).

## Corrections, avant → après

| # | Où / quand | Avant | Après |
|---|---|---|---|
| 1a | **Voix**, 80,35–81,64 s | « **Une seule tétée**, c'est jusqu'à 10 millions de bactéries vivantes… » | « **Chaque jour**, c'est jusqu'à 10 millions de bactéries vivantes… » (voix clonée XTTS-v2, parole 81,10–81,61 s) |
| 1b | Sous-titres, 81,1–81,6 s | « Une seule tétée, » | « Chaque jour, » |
| 1c | Écran silhouette, carte de gauche (dès 81,1 s) | « Chaque tétée : 10⁵ à 10⁷ bactéries viables + 386 microARN. » | « Chaque jour : 10⁵ à 10⁷ bactéries + des centaines de microARN. » |
| 2 | Spécificité, écran « hélices » (dès 177,4 s) | « Fingerprint Moléculaire : Signature unique de 386 microARN. » | « Fingerprint Moléculaire : profil de microARN propre à chaque lait (non démontré). » |
| 3 | Silhouette, sous « Cellules souches & ADN maternels » (dès 87,8 s, jusqu'à 109,5 s) | — | « (observé chez la souris) » (italique, 25 px, crème) |
| 4a | Chaîne cortisol, sous le cerveau (dès 140,5 s) | « Reprogrammation Épigénétique » | « Effet sur l'humeur (hypothèse) » |
| 4b | Tableau final, ligne « Influence Caractère » (dès 225,3 s) | « Confirmée » | « Corrélation observée » |
| 5a | Hélices, sous « Mélange de Laits » (dès 184,1 s) | « (Confusion Biologique) » | « (Hypothèse : Confusion Biologique) » |
| 5b | Hélices, 3ᵉ ligne (dès 187,2 s) | « Risque : Compétition conflictuelle entre souches bactériennes étrangères. » | « Hypothèse : Compétition conflictuelle entre souches bactériennes étrangères. » |
| 5c | Tableau final, ligne « Interdiction Mélange » (dès 226,6 s) | « Confirmée » | « Hypothèse (non démontrée) » |
| 6a | Tableau final, ligne « Durée 2 ans » (dès 219,8 s) | « 100% Exacte » | « Concordante » (même mise en avant dorée) |
| 6b | Tableau final, ligne « Parenté (5 tétées) » (dès 222,6 s) | « Substantielle » | « Observée chez l'animal » |
| 7 | Conclusion, phrase finale (dès 234,6 s) | « …que la science n'a quantifiées qu'en 2025. » | « …que la science quantifie depuis 2007. » |
| 8 | Pastille de la scène cortisol (132,5–152,2 s) | « Nature Scientific Reports, 2025 » | « Scientific Reports, 2025 » |
| 9 | Fin, sous la phrase finale (234,8 s → fin, 236,8 s) | — | « Sources : voir description » (28 px, gris, en fondu ; la voix finit à 236,5 s et n'est pas coupée) |

Mise en page : textes plus longs ajustés sans toucher à la 1re version — le détail « (Hypothèse : Confusion Biologique) »
passe en 25 px pour tenir sur une ligne, et les cases « Concordance » de plus de 18 caractères en 28 px
(« Hypothèse » / « (non démontrée) » sur deux lignes).

## Le passage audio modifié (correction 1)
- **Source** : `work/audio_remede.m4a` (déjà avec « Remède »), non modifié. Résultat : `work/audio_corrigee.m4a`.
- **Prises** : 16 prises XTTS-v2 (mêmes 3 extraits de référence que pour « Remède », `work/voix/ref_*.wav`) :
  8 de la phrase entière « Chaque jour, c'est jusqu'à dix millions de bactéries vivantes. » (d'où l'on découpe « Chaque jour, »,
  pour garder l'intonation de continuation) et 8 de « Chaque jour, » seul ; températures 0,65/0,75, vitesses 0,9/1,0.
- **Choix** (`scripts/choix_prise.py`, détail dans `work/corrigee/choix_prise.json`) : chaque extrait est retranscrit seul par
  faster-whisper large-v3 (il doit donner exactement « Chaque jour ») ; hauteur de voix (F0 médiane, pyin) et durée comparées à
  « Une seule tétée, » d'origine (220 Hz, 0,76 s) ; une prise découpée n'est gardée que si la coupe tombe sur un silence
  (< −45 dB). **Retenue : prise 4** (phrase entière, coupe « jour | c'est » à −57,6 dB) : 215 Hz (−0,4 demi-ton), 0,49 s de parole.
  La prise 10 avait un score un peu meilleur mais sa coupe tombait à −32 dB (pas un silence) : écartée.
- **Montage** (`scripts/montage_audio.py --corrigee`) : effacement de 80,35 s (silence à −97 dB après « à vie. ») à 81,64 s
  (creux à −65 dB juste avant le « s » de « c'est ») ; « Chaque jour, » posé pour finir à 81,61 s (début 81,10 s), niveau
  accordé au RMS de parole d'origine (−3,6 dB) ; fondus de 15–20 ms ; le reste est du silence. La phrase suivante
  (« c'est jusqu'à… ») et tout le reste gardent exactement leurs temps.
- **Contrôles** : même nombre d'échantillons décodés (10 442 752, 236,797 s), décalage 0 échantillon mesuré par corrélation
  à 10, 50, 79, 82,5, 120, 200 et 235 s ; seule la zone 80,5–81,6 s diffère (ailleurs, écart −47 à −62 dB = 2ᵉ réencodage AAC).
  Transcription faster-whisper du passage 76–90 s de la nouvelle piste : « … un lien de parenté à vie. **Chaque jour, c'est
  jusqu'à 10 millions de bactéries vivantes** qui sont transmises, sans même parler des cellules souches. … »
  (probabilité 1,00 pour « Chaque » et « jour, » ; `work/corrigee/verif_transcription.txt`).
- **Extrait à écouter** : `sortie/extrait_audio_avant_apres.m4a` = 78–86 s **avant**, 1,2 s de silence, puis 78–86 s **après**.

## Contrôles avant rendu
- `python3 scripts/render.py apercus --corrigee` → `sortie/apercus_corrigee/` (19 images, une par écran) : **0 débordement,
  0 chevauchement**, contenu entre y = 150 et 1385, sous-titres entre 1395 et 1670. Les 19 aperçus ont été regardés ; trois
  défauts vus à l'œil et corrigés avant le rendu (le contrôle automatique ne voit pas les filets décoratifs) : détail
  « (Hypothèse : Confusion Biologique) » sur deux lignes qui touchait le filet, « Hypothèse (non » qui touchait le bord de la
  carte, « (observé chez la / souris) » mal coupé.
- Synchronisation des sous-titres (`scripts/verif_synchro.py --corrigee`, transcription indépendante de la nouvelle piste,
  images dans `work/corrigee/synchro/`) :

| t | Entendu (faster-whisper) | Surligné à l'écran | |
|---|---|---|---|
| 8,5 s | « remède » (8,28–8,80) | « Remède. » | ✅ |
| 81,2 s | « Chaque » (parole dès 81,10) | « Chaque » | ✅ |
| 81,9 s | « jusqu'à » (81,84–81,98) | « jusqu'à » | ✅ |
| 150,0 s | « entre » (149,58–150,00) | « entre » | ✅ |
| 233,3 s | « greffe » (233,00–233,40) | « greffe » | ✅ |

  (Un premier essai à 233,0 s tombait pile sur la frontière « une » | « greffe », toutes deux à 233,00 s : pas d'écart réel.)

## Rendu
`python3 scripts/render.py video --corrigee` → `sortie/remede-9x16-corrigee.mp4` : H.264 1080×1920, 30 i/s, 7104 images,
236,80 s ; audio AAC 236,797 s (même durée que l'audio, à une image près), 33 Mo. La piste audio de la vidéo est identique
octet pour octet à `work/audio_corrigee.m4a`. Transcription du passage 79–85 s **extraite de la vidéo** : « … lien de parenté à vie.
Chaque jour, c'est jusqu'à 10 millions de bactéries vivantes qui sont transmises. » Images de la vidéo vérifiées à 81,3 s
(carte « Chaque jour… », sous-titre « Chaque jour, »), 88,5 s (« observé chez la souris »), 228 s (tableau) et 236 s
(« depuis 2007 », « Sources : voir description »).

## Doutes et points à décider
1. **Voix clonée** : timbre proche mais pas identique (comme pour « Remède »). « Chaque jour, » dure 0,49 s contre 0,76 s pour
   « Une seule tétée, » : la pause après « à vie. » passe d'environ 0,65 s à environ 0,9 s. La petite respiration d'origine
   (80,44–80,60 s, −52 dB) a été effacée avec le reste. La jonction avec « c'est » se fait sur un creux de 40 ms seulement
   (l'orateur enchaînait sans pause) : la transcription l'entend comme une phrase continue, mais **à écouter**.
2. **« Nature Scientific Reports, 2025 » apparaissait deux fois sur l'écran cortisol** : dans la pastille (correction 8) et dans la
   ligne « L'Axe Cortisol-Tempérament (Nature Scientific Reports, 2025) ». J'ai corrigé les deux, pour que l'écran ne se
   contredise pas. Si vous vouliez strictement la pastille seule, c'est un mot à remettre dans `scripts/build_scenes.py`.
3. **« bactéries viables » → « bactéries »** : c'est la formulation demandée. La voix dit encore « bactéries vivantes » ; par jour,
   10⁷ reste le haut de la fourchette, et la vérification n'a pas trouvé la source primaire de « 10⁵ à 10⁷ par jour ».
4. **La voix n'a pas changé ailleurs** : elle présente toujours le voyage des cellules souches comme un fait (87–95 s), dit
   « le transfert massif de cellules » pour la parenté (222,6 s) et « cacophonie biologique » au conditionnel (187 s). Les mentions
   à l'écran (« observé chez la souris », « Hypothèse », « Observée chez l'animal ») nuancent, sans contredire la voix.
5. **Laissés tels quels (non demandés)**, mais discutables selon `verification_scientifique.md` : « Clôture de la fenêtre
   épigénétique » (frise 24 mois), en-tête « Preuve Biologique (2024-2025) », « Fenêtre épigénétique 0-24 mois », ligne
   « Pureté — Confirmée », « Programmation Épigénétique (MicroARN) » dans la conclusion, la phrase de pied du tableau
   (« …confirme une sagesse intemporelle et une précision biologique »), et « 44,3% » (non retrouvé dans le résumé de l'étude).
6. **Description TikTok** : la mention « Sources : voir description » suppose que vous y mettiez les références
   (par exemple celles de `verification_scientifique.md`).
7. **Licence** : XTTS-v2 est sous licence Coqui CPML (usage non commercial) — même réserve que pour « Remède ».

## Refaire la version corrigée
```
python3 scripts/voix_remede.py --texte "Chaque jour, c'est jusqu'à dix millions de bactéries vivantes." --texte "Chaque jour," \
    --prefixe work/corrigee/prise_jour_ --premier 1 --n 16 --graine 300 --temperatures 0.65,0.65,0.75,0.75 --vitesses 0.9,1.0
python3 scripts/choix_prise.py                      # -> work/corrigee/jour_retenu.wav (+ choix_prise.json)
python3 scripts/montage_audio.py --corrigee         # -> work/audio_corrigee.m4a
python3 scripts/verif_passage.py work/audio_corrigee.m4a 76 90
python3 scripts/build_scenes.py --corrigee          # -> projet/scenes_corrigee.json
python3 scripts/render.py apercus --corrigee        # -> sortie/apercus_corrigee/ + contrôles
python3 scripts/verif_synchro.py --corrigee 8.5 81.2 81.9 150.0 233.3
python3 scripts/render.py video --corrigee          # -> sortie/remede-9x16-corrigee.mp4
```
Les prises XTTS ne sont pas reproductibles à l'identique d'une installation à l'autre ; la prise retenue est conservée
(`work/corrigee/jour_retenu.wav`, prise complète `work/corrigee/prise_jour_4.wav`).
Les commandes sans `--corrigee` refont la 1re version à l'identique (vérifié : `projet/scenes.json` régénéré octet pour octet).
