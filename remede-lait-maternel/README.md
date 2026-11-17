> **Pour toute session** : lire `CLAUDE.md` (type de vidéo, règles) puis `STYLE.md` (style) avant de toucher au projet.

# REMEDE — lait maternel (9:16)

Projet de la vidéo TikTok « REMEDE » sur le lait maternel, rendue en 1080×1920 avec Python, Pillow et ffmpeg.

- `entree/` : vidéo source (audio + contenu) et vidéo de référence (format et animation seulement).
- `projet/` : transcription faster-whisper et plan des scènes (`scenes.json`).
- `scripts/` : `build_scenes.py` (plan), `render.py` (aperçus et vidéo), `gfx.py` (dessin), `voix_remede.py` et
  `montage_audio.py` (phrase « Remède » en voix clonée XTTS-v2).
- `work/` : piste d'origine (`audio.m4a`), piste avec « Remède » (`audio_remede.m4a`), extraits de référence de la voix.
- `sortie/a_verifier.md` : choix et doutes ; `sortie/verification_scientifique.md` : vérification des faits (Consensus).

Dépendances : `pip install pillow numpy faster-whisper` ; pour la voix clonée : torch CPU, `coqui-tts` (voir les
contournements dans `scripts/voix_remede.py`).

```
python3 scripts/build_scenes.py
python3 scripts/render.py apercus
python3 scripts/render.py video
```

## Version corrigée (corrections scientifiques)
Une 2ᵉ vidéo, `sortie/remede-9x16-corrigee.mp4`, applique les corrections de `sortie/verification_scientifique.md`
(détail, temps et doutes : `sortie/corrections_appliquees.md`). Elle a ses propres fichiers ; la 1re version n'est pas touchée :
`work/audio_corrigee.m4a` (« Une seule tétée » → « Chaque jour », voix clonée), `projet/scenes_corrigee.json`,
`sortie/apercus_corrigee/`. Tous les scripts prennent l'option `--corrigee` (`render.py` accepte aussi les variables
`REMEDE_SCENES`, `REMEDE_AUDIO`, `REMEDE_APERCUS`, `REMEDE_VIDEO`).

```
python3 scripts/montage_audio.py --corrigee
python3 scripts/build_scenes.py --corrigee
python3 scripts/render.py apercus --corrigee
python3 scripts/render.py video --corrigee
```
Nouveaux scripts : `choix_prise.py` (choix de la prise clonée), `verif_passage.py` (transcription d'un passage),
`verif_synchro.py` (synchronisation des sous-titres).
