# Style REMEDE — à réutiliser pour les vidéos suivantes

Référence : la version corrigée (`sortie/remede-9x16-corrigee.mp4`), faite avec les scripts de ce dossier.
Ce fichier décrit ce qui est établi ; à compléter si un choix change.

## Format
- 1080×1920, 9:16, 30 i/s, H.264 (CRF 17, yuv420p), AAC 256 kb/s pour l'audio.
- Zone sûre TikTok : rien d'important au-dessus de y = 150 ni sous y = 1670. Contenu entre y = 150 et y = 1385.
  Sous-titres centrés en y = 1500, dans la bande 1395–1670.
- Marges latérales : 44 px minimum. Cadre fin en or sombre et ornements d'angle (décor seulement).

## Couleurs (gfx.py)
- Fond : #151516 (dégradé radial) vers #0B0B0C et #201E1F.
- Or titres : #B6A57A ; or clair mots-clés : #E4D9B0 ; or sombre filets : #706650.
- Crème texte : #EFE8D8 ; gris secondaire : #8C8A84.
- Mots-clés dans le texte courant : or #B6A57A (l'or clair se confond avec le crème).

## Typographie
- Titres : Playfair Display (700 / 600). Citations : Lora italique. Texte : Inter (400 / 500 / 600 / 800 pour les sous-titres).
- Titre de diapo : 2 lignes max, mots-clés en or clair. Pastille de référence au-dessus du titre, avec losange doré.

## Structure
- Une idée par écran. Une diapo de la source peut devenir plusieurs écrans successifs (même titre, même pastille).
- Entre les parties : écran « emblème » seul (mère et enfant, couronne de feuilles), sans texte.
- Chaque référence (verset, hadith, source scientifique) est affichée dans une pastille ou entre parenthèses, reprise mot pour mot de la source.
- Tableaux : lignes-cartes à 3 colonnes ; le dernier mot de la colonne « Concordance » doit rester un statut prudent.

## Sous-titres
- Mot par mot, synchronisés sur la transcription faster-whisper large-v3 (`word_timestamps`).
- Groupes de 2 à 4 mots ; le mot en cours est sur fond or clair, les mots déjà dits sur fond sombre.
- Corrections de transcription listées dans `projet/scenes*.json` (meta.corrections_sous_titres).

## Animations
- Apparition : `up` (monte de 28 px), `fade`, `wl`/`wt`/`wb` (tracé d'un filet), `rad` (balayage circulaire pour l'emblème).
- Halos pulsants derrière les visuels clés ; le fond a de légères particules dorées.

## Règles de fond (à respecter pour toute vidéo)
- Aucun chiffre, verset, hadith ni référence qui n'est pas dans la source ou vérifié. Ne rien ajouter sans l'indiquer.
- Une affirmation scientifique établie est présentée comme telle seulement si une étude la soutient.
  Pour une observation chez l'animal, écrire « observé chez la souris » (ou l'animal) à l'écran.
- Une hypothèse est marquée « Hypothèse : » ou « (hypothèse) » à l'écran, et « non démontré » dans les tableaux.
- « Corrélation observée » plutôt que « Confirmée » pour une association.
- Mention finale : « Sources : voir description » ; la description liste les sources.

## Voix
- Voix clonée (XTTS-v2, local, CPU) à partir de 3 extraits de la narration (`work/voix/ref_*.wav`).
  **Licence Coqui CPML : usage non commercial.** Pour une vidéo monétisée, refaire la voix avec un outil commercial.
- Les retouches audio ne doivent décaler aucun temps : effacer le passage, insérer la prise, compléter par du silence.
  Vérifier : même nombre d'échantillons, décalage nul, transcription du passage.

## Chaîne de production (dans ce dossier)
```
python3 scripts/voix_remede.py ...        # prises clonées (options --texte, --prefixe, --graine...)
python3 scripts/choix_prise.py            # choix : transcription + hauteur de voix + coupe sur silence
python3 scripts/montage_audio.py ...      # montage sans décalage (options --source --sortie --efface ...)
python3 scripts/build_scenes.py ...       # plan des scènes (--corrigee pour la version corrigée)
python3 scripts/render.py apercus         # aperçus, contrôle débordement/chevauchement
python3 scripts/render.py video           # rendu
python3 scripts/verif_synchro.py ...      # synchro des sous-titres sur quelques instants
```
Les chemins de sortie sont des options ou des variables (`REMEDE_SCENES`, `REMEDE_AUDIO`, `REMEDE_APERCUS`, `REMEDE_VIDEO`),
pour ne jamais écraser une version précédente.

## Contrôles avant publication
1. Aperçus regardés un par un (pas seulement le contrôle automatique : il ne voit pas les filets et les ornements).
2. Synchronisation sur 5 points au moins.
3. Format, durée et piste audio vérifiés sur le fichier rendu (ffprobe, transcription du passage modifié).
4. Description : sources listées, aucune promesse de viralité, sujets sensibles traités avec prudence.
