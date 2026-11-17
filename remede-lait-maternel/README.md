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
