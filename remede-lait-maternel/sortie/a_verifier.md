# REMEDE — version 9:16 animée — à vérifier

## Changement « REMEDE » (demande du 17/11)
- **Texte** : l'écran titre affiche « REMEDE » (écrit comme vous l'avez tapé, sans accent, en capitales espacées) à la place de
  « SYMBIOSE : Science & Sunna ». Il s'illumine en or clair à 8,3 s, quand la voix dit « Remède ». Le sous-titre de la diapo
  (« Le Lait Maternel – Entre Révélation Textuelle et Preuve Biologique ») et « ÉDITION 2026 – ANALYSE DE CONCORDANCE » sont gardés.
  Si vous préférez « REMÈDE » avec l'accent, c'est un mot à changer dans `scripts/build_scenes.py`.
- **Voix** : la phrase « C'est la thèse de Symbiose Science & Sunna. » (7,46–9,59 s) est remplacée par « C'est la thèse de Remède. »,
  dite par une **voix clonée** à partir de 3 extraits de la narration (modèle libre XTTS-v2, en local). 12 prises générées ;
  retenue : la n° 9 (hauteur de voix la plus proche de l'originale, 170 Hz contre 175 Hz, débit le plus naturel). Elle commence
  à 7,55 s, finit à 8,92 s ; une pause d'environ 1 s suit, puis la vidéo continue exactement aux mêmes temps.
  **À écouter** : le timbre cloné est proche mais pas identique ; la jonction est sur des silences, sans coupure de mot.
- **Audio** : à cause de ce montage, la piste n'est plus une copie bit à bit ; elle est réencodée en AAC 256 kb/s (au lieu de
  128 kb/s d'origine). Durée identique (écart de 1 ms). Le reste de la voix n'est pas modifié.
- **Licence** : XTTS-v2 est sous licence Coqui CPML (usage non commercial). Si votre compte TikTok est monétisé, il vaut mieux
  refaire cette phrase avec un outil commercial (ElevenLabs avec clonage, ou votre propre voix) ; il suffit de remplacer
  `work/voix/prise_9.wav` et de relancer `python3 scripts/montage_audio.py <prise.wav>` puis le rendu.
- Sous-titres : « C'est la thèse de » puis « Remède. » seul (le mot s'affiche seul en surbrillance).

## Fichiers
- Source : `entree/source_remede.prophetique_laitmaternel.mp4` (576×1024, 236,8 s, diapos dans une bande horizontale).
- Référence : `entree/reference_lumideen.mp4` (1080×1920, 98 s), utilisée pour le format et la manière d'animer seulement.
- Sortie : `sortie/symbiose-9x16.mp4` — 1080×1920, 30 i/s, H.264.
- Plan : `projet/scenes.json` (15 scènes = 15 diapos, 19 écrans, 755 mots datés). Transcription brute : `projet/transcription.json`.
- Aperçus : `sortie/apercus/` (une image par écran, prise juste avant sa sortie).

## Audio
Piste de la source gardée telle quelle (aucune coupe, aucune musique), sauf la phrase « Remède » décrite plus haut ; réencodée en AAC 256 kb/s.

## Ce que j'ai décidé seul
1. **Une idée par écran.** Les 4 diapos les plus chargées sont réparties sur deux écrans successifs (même titre, même pastille) :
   diapo 2 (les deux ordres, puis la citation), diapo 3 (verset, puis frise 24 mois), diapo 5 (hadith, puis silhouette),
   diapo 11 (fatwa, puis les deux hélices). Aucun texte n'est retiré pour autant, sauf les cas listés plus bas.
2. **Tableaux passés en vertical.** « Le Vivant vs L'Inerte » et « Synthèse de Concordance » gardent leurs colonnes, en lignes-cartes.
3. **Diapos-logo (4, 6, 8, 10).** La source montre son emblème seul ; j'affiche un emblème mère-et-enfant redessiné, sans texte.
4. **Emblème, icônes, frise, silhouette, hélices, bouclier** : tout est redessiné en vectoriel, rien n'est agrandi depuis la source.
   Le dessin de la mère et de l'enfant est donc une interprétation simplifiée de l'emblème d'origine, pas une copie.
5. **Pastilles de référence** : « Sourate Al-Baqarah 2:233 », « Bukhârî & Muslim », « Nature Scientific Reports, 2025 », « Fatwa n°15990 »
   — reprises mot pour mot des diapos. Les diapos sans référence n'ont pas de pastille.
6. **Couleur des mots-clés.** Titres : or #B6A57A, mots-clés en or clair #E4D9B0 (comme demandé). Dans le texte courant crème,
   l'or clair se distinguait mal du crème : les mots-clés y sont en or #B6A57A. À inverser si vous préférez.
7. **Moment d'apparition du titre de la diapo 1.** Il apparaît dès 1,3 s (sinon l'écran reste vide 7 s) ; « Science & Sunna »
   s'illumine quand la voix le dit (7,1 s).
8. **Lignes 4 et 5 du tableau de synthèse** (« Interdiction Mélange », « Pureté ») : la voix ne les cite pas ; elles apparaissent
   juste après la ligne 3 (226,6 s et 227,1 s).
9. **Diapo 12 (La Pureté)** : elle ne dure que 4,3 s dans la source. Tout son contenu y est, mais c'est court à lire.
10. **Texte arabe** : la source n'en contient aucun, je n'en ai pas ajouté (Amiri est installée mais inutilisée). Ajouter le verset
    2:233 en arabe serait un ajout de contenu : à vous de décider.

## Textes de la source laissés de côté (illisibles ou incohérents)
- Diapo 2 : « (Dinnées Biomonculaires) » sous « Données Biomoléculaires » — texte manifestement corrompu, non repris.
- Diapo 2 : la phrase du bas « Ce dossier établit une démonstration par concordance : ce qui est énoncé … » est coupée par le bord
  de la diapo ; la suite est illisible, la phrase entière est omise.
- Diapo 3 : « (Steueires with stabilized systèmes) » sous « Structure adulte acquise » — texte corrompu, non repris.
- Diapo 9 : le cadre de gauche répète les deux citations de la diapo 7 (la seconde y est abrégée). Je ne les ai pas répétées
  sur cet écran ; elles sont affichées en entier à la scène 7.

## Sous-titres : corrections de la transcription (le son n'est pas touché)
Whisper a mal entendu quelques mots ; les sous-titres affichent la version corrigée. À vérifier à l'écoute :
| Temps | Whisper | Affiché | Pourquoi |
|---|---|---|---|
| 7,5 s | « C'est la thèse de Symbiose Sciences et Suna. » | « C'est la thèse de Remède. » | phrase remplacée par la voix clonée |
| 56,6 s | « qu'endroit islamique. » | « En droit islamique, » | confirmé par les sous-titres incrustés de la source |
| 68 s, 81 s | « tétés », « tété » | « tétées », « tétée » | orthographe |
| 87,0 s | « Des cellules souches. » | « Des cellules souches ? » | probable relance d'une 2ᵉ voix — **doute** |
| 116,5 s | « Des textes. Un classique, … conseillait » | « Des textes classiques, … conseillaient » | « Un » très incertain (probabilité 0,05) — **doute** |
| 163,8 s | « brûlerait … les pistes » | « brouillerait … les pistes » | expression — **doute** |
| 179,0 s | « micro-RN » | « micro-ARN » | diapo : « microARN » |
| 207,4 s | « On sait synthétiser. On sait synthétiser » | une seule fois | répétition fantôme (durée nulle) |
| 2,5 s | « 1400 » | « 1 400 » | espace des milliers |

Les textes des diapos (titres, citations, chiffres, références) sont recopiés tels quels, y compris « 44,3% », « 90-100% »,
« 10⁵ à 10⁷ », « 386 microARN », « Fatwa n°15990 », « THE SCIENCE », « ‘window of opportunity’ ».
Je n'ai vérifié ni les hadiths, ni les références scientifiques, ni l'attribution des citations : je les ai seulement reproduits.

## Contrôles faits avant le rendu
- 19 aperçus regardés un par un : lisibilité correcte, pas de chevauchement.
- Contrôle automatique des boîtes de texte et d'icônes : 0 débordement latéral, 0 chevauchement, tout le contenu entre
  y = 150 et y = 1385 ; sous-titres entre 1395 et 1670 (rien d'important dans les 150 px du haut ni les 250 px du bas ;
  seuls le filet du cadre et les ornements d'angle, décoratifs, y passent).
- Synchronisation des sous-titres : comparée aux sous-titres incrustés de la source à 3,2 s, 58,6 s, 104,3 s, 178,6 s et 232,4 s
  — même passage affiché aux 4 premiers points ; à 232,4 s la source affiche encore la phrase précédente (ses blocs traînent),
  le mien suit la voix. Les 758 mots sont surlignés au milieu de leur intervalle transcrit.
- Trois défauts corrigés après les premiers aperçus : texte débordant du bouclier, en-tête de colonne sur deux lignes qui
  touchait le filet, plusieurs textes trop petits (agrandis).

## Limites connues
- Sous-titres par groupes de 2 à 4 mots ; 9 groupes sur 224 n'ont qu'un mot (fin de phrase isolée).
- La synchronisation repose sur les temps de Whisper (précision d'environ ±0,1 s par mot).
- Polices : Playfair Display (titres), Lora (citations), Inter (texte). Lora et Playfair viennent des paquets npm `@fontsource`.

## Refaire le rendu
```
python3 scripts/voix_remede.py      # (facultatif) régénère des prises de la voix clonée
python3 scripts/montage_audio.py    # monte la prise retenue -> work/audio_remede.m4a
python3 scripts/build_scenes.py     # régénère projet/scenes.json
python3 scripts/render.py apercus   # aperçus + contrôles
python3 scripts/render.py video     # sortie/symbiose-9x16.mp4
```
