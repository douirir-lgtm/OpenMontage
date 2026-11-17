# Fil de travail — vidéo TikTok « REMEDE » (lait maternel)

Résumé de la session Claude Code du 17/11/2026, à ajouter aux connaissances du projet vidéo sur claude.ai.

## Le type de vidéo
- Vidéo **TikTok verticale 9:16** (1080×1920, 30 i/s), environ **237 s**.
- **Explicative**, en **diaporama animé** (fond sombre, or et crème), **narration en voix off**, **sous-titres mot par mot**.
- Sujet : la **« concordance »** entre des textes islamiques (Coran 2:233, hadith Bukhârî & Muslim, avis de savants,
  fatwa n°15990) et des études récentes sur le lait maternel (myélinisation, microbiote, microARN, cortisol,
  cellules souches, pasteurisation).
- Série / titre : **« REMEDE »** (écrit sans accent, en capitales espacées).

## Où sont les fichiers
- Dépôt GitHub : `douirir-lgtm/OpenMontage`, branche **`ccr-2c819226-85rjvq`**, dossier **`remede-lait-maternel/`**.
- À lire en premier : `CLAUDE.md` (type de vidéo, règles), puis `STYLE.md` (style complet), puis `README.md`.
- Vidéos (non versionnées, sur la machine de la session) :
  - 1re version : `sortie/symbiose-9x16.mp4` — ne jamais l'écraser.
  - **Version corrigée** : `sortie/remede-9x16-corrigee.mp4` — 1080×1920, 30 i/s, 236,8 s.
- Notes : `sortie/verification_scientifique.md` (vérification des faits), `sortie/corrections_appliquees.md` (avant → après).

## Le style (résumé ; détail dans STYLE.md)
- Zone sûre TikTok : rien d'important dans les 150 px du haut ni les 250 px du bas ; contenu entre y = 150 et 1385 ;
  sous-titres centrés en y = 1500.
- Couleurs : fond #151516, or #B6A57A (titres), or clair #E4D9B0 (mots-clés), or sombre #706650 (filets),
  crème #EFE8D8 (texte), gris #8C8A84.
- Polices : Playfair Display (titres), Lora italique (citations), Inter (texte, sous-titres en ExtraBold).
- Une idée par écran ; pastille de référence au-dessus du titre ; écran « emblème » (mère et enfant) entre les parties ;
  tableaux en lignes-cartes ; halos pulsants et particules dorées ; animations d'apparition douces.
- Sous-titres : groupes de 2 à 4 mots, mot en cours sur fond or clair.

## Règles de fond (à garder pour les vidéos suivantes)
- Aucun chiffre, verset, hadith ni référence sans source ; rien ajouté sans le dire.
- Observation chez l'animal → écrire « observé chez la souris » (ou l'animal).
- Hypothèse → « Hypothèse : … » ou « (hypothèse) » ; dans les tableaux « non démontrée ».
- Association → « Corrélation observée », pas « Confirmée ».
- Fin de vidéo : « Sources : voir description », et la description liste les sources.

## Ce qui a été fait dans la version corrigée
1. Voix vers 80,4 s : « Une seule tétée » → « Chaque jour » (voix clonée XTTS-v2, prise 4 sur 16, 215 Hz contre 220 Hz
   d'origine, aucun décalage du reste de l'audio). À l'écran : « Chaque jour : 10⁵ à 10⁷ bactéries + des centaines de microARN ».
2. « 386 microARN » retiré partout → « des centaines de microARN » ; « profil de microARN propre à chaque lait (non démontré) ».
3. Cellules souches : « (observé chez la souris) ».
4. Cortisol : « Reprogrammation Épigénétique » → « Effet sur l'humeur (hypothèse) » ; tableau « Confirmée » → « Corrélation observée ».
5. Mélange des laits : « Hypothèse : … » ; tableau → « Hypothèse (non démontrée) ».
6. Tableau : « 100% Exacte » → « Concordante » ; « Substantielle » → « Observée chez l'animal ».
7. Conclusion : « …que la science quantifie depuis 2007 ».
8. Pastille : « Scientific Reports, 2025 » (aussi corrigé dans la ligne « L'Axe Cortisol-Tempérament »).
9. Fin : « Sources : voir description ».
Contrôles : 19 aperçus regardés, 0 débordement, synchro des sous-titres vérifiée sur 5 points, passage audio retranscrit.

## Points encore ouverts
- Écouter la jonction « Chaque jour, | c'est » (vers 81,6 s) : enchaînement très court.
- La voix présente toujours les cellules souches comme un fait chez l'enfant (87–95 s) et parle de « transfert massif de
  cellules » (222,6 s) ; l'écran nuance.
- Non corrigés (non demandés) : « Clôture de la fenêtre épigénétique », « Preuve Biologique (2024-2025) »,
  « Pureté — Confirmée », « Programmation Épigénétique (MicroARN) », « 44,3% » (non vérifié).
- Voix clonée XTTS-v2 : licence non commerciale. Pour un compte monétisé, refaire la voix avec un outil commercial.

## Description TikTok proposée
```
REMEDE : le lait maternel, entre textes et biologie.

Ce que disent les études récentes sur le lait maternel (microbiote, microARN, cortisol, cellules souches) et comment cela se rattache aux textes. Les liens sont présentés comme des concordances. Ce qui n'est pas démontré est signalé comme hypothèse.

Sources (articles revus par des pairs) :
- Lebel et al., 2018, NeuroImage (développement de la myélinisation)
- Schwab et al., 2019, Frontiers in Microbiology (microbiote du lait)
- Liao et al., 2017, Molecular Nutrition & Food Research (microARN du lait et digestion)
- Hassiotou et al., 2015, FASEB Journal (cellules souches du lait)
- Molès et al., 2017, Nature Reviews Immunology (microchimérisme lié à l'allaitement)
- Feizabad et al., 2025, Scientific Reports (cortisol du lait et tempérament)

#allaitement #laitmaternel #santé #microbiote #science #islam #sunna #religion #éducation #fact
```

## Pour reprendre dans une autre session
- Session cloud : ouvrir le dépôt `douirir-lgtm/OpenMontage` sur la branche `ccr-2c819226-85rjvq`.
- Sur ton ordinateur : `git fetch origin` puis `git checkout ccr-2c819226-85rjvq`, et travailler dans `remede-lait-maternel/`.
- Commandes de rendu : voir `README.md` (option `--corrigee` pour la version corrigée).
