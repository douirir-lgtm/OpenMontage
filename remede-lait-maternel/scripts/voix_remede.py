"""Génère « C'est la thèse de Remède. » avec la voix de la source (clonage XTTS-v2)."""
import os, torch
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


X.load_audio = load_audio
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
refs = ["work/voix/ref_a22.wav", "work/voix/ref_b22.wav", "work/voix/ref_c22.wav"]
textes = ["C'est la thèse de Remède.", "C'est la thèse de Remède."]
for i in range(6, 12):
    torch.manual_seed(100 + i)
    wav = tts.tts(text=textes[i % 2], speaker_wav=refs, language="fr", temperature=0.6 if i < 9 else 0.7, speed=0.82)
    a = (np.clip(np.asarray(wav), -1, 1) * 32767).astype(np.int16)
    o = wave.open(f"work/voix/prise_{i}.wav", "wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(24000); o.writeframes(a.tobytes()); o.close()
    print("prise", i, flush=True)
