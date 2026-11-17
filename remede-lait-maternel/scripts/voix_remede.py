"""Génère des prises avec la voix de la source (clonage XTTS-v2, en local, CPU).

Sans option : refait les prises 6 à 11 de « C'est la thèse de Remède. » (work/voix/prise_<i>.wav), comme la 1re version.
Avec options (version corrigée) :
  python3 scripts/voix_remede.py --texte "Chaque jour, c'est jusqu'à dix millions de bactéries vivantes." \
      --texte "Chaque jour," --prefixe work/corrigee/prise_jour_ --n 12 --graine 300
Les prises alternent entre les textes donnés ; la température et la vitesse alternent aussi (voir --temperatures, --vitesses).
"""
import argparse, os, torch
os.environ["COQUI_TOS_AGREED"] = "1"
from TTS.api import TTS
import wave, numpy as np
import TTS.tts.models.xtts as X


def load_audio(path, sr):
    """Lecture WAV PCM 16 bits sans torchcodec (le paquet installé vise CUDA)."""
    w = wave.open(path)
    assert w.getframerate() == sr and w.getnchannels() == 1, (path, w.getframerate(), w.getnchannels())
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return torch.from_numpy(a).unsqueeze(0)


ap = argparse.ArgumentParser()
ap.add_argument("--texte", action="append", help="texte à dire (répétable ; les prises alternent)")
ap.add_argument("--prefixe", default="work/voix/prise_", help="préfixe des fichiers WAV de sortie")
ap.add_argument("--premier", type=int, default=6, help="numéro de la première prise")
ap.add_argument("--n", type=int, default=6, help="nombre de prises")
ap.add_argument("--graine", type=int, default=100, help="graine de base (graine + numéro de prise)")
ap.add_argument("--temperatures", default=None, help="liste séparée par des virgules, alternée (défaut : 0,6 puis 0,7 dès la prise 9)")
ap.add_argument("--vitesses", default="0.82", help="liste séparée par des virgules, alternée")
args = ap.parse_args()
textes = args.texte or ["C'est la thèse de Remède.", "C'est la thèse de Remède."]
vitesses = [float(v) for v in args.vitesses.split(",")]
temps = [float(v) for v in args.temperatures.split(",")] if args.temperatures else None

X.load_audio = load_audio
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
refs = ["work/voix/ref_a22.wav", "work/voix/ref_b22.wav", "work/voix/ref_c22.wav"]
os.makedirs(os.path.dirname(args.prefixe) or ".", exist_ok=True)
for k, i in enumerate(range(args.premier, args.premier + args.n)):
    torch.manual_seed(args.graine + i)
    texte = textes[i % len(textes)]
    temp = temps[k % len(temps)] if temps else (0.6 if i < 9 else 0.7)
    vit = vitesses[(k // len(textes)) % len(vitesses)]
    wav = tts.tts(text=texte, speaker_wav=refs, language="fr", temperature=temp, speed=vit)
    a = (np.clip(np.asarray(wav), -1, 1) * 32767).astype(np.int16)
    o = wave.open(f"{args.prefixe}{i}.wav", "wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(24000); o.writeframes(a.tobytes()); o.close()
    print("prise", i, repr(texte), "temp", temp, "vitesse", vit, flush=True)
