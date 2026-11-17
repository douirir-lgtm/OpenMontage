"""Transcrit (faster-whisper large-v3, mots datés) un passage d'une piste audio.
  python3 scripts/verif_passage.py work/audio_corrigee.m4a 76 90"""
import subprocess, sys, numpy as np
from faster_whisper import WhisperModel
p, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-to", str(t1), "-i", p, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                   capture_output=True, check=True).stdout
x = np.frombuffer(r, np.float32)
m = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)
segs, _ = m.transcribe(x, language="fr", word_timestamps=True, vad_filter=False, beam_size=5)
for s in segs:
    print(f"{s.start + t0:7.2f}–{s.end + t0:7.2f} {s.text.strip()}")
    for w in s.words:
        print(f"    {w.start + t0:7.2f} {w.end + t0:7.2f} {w.probability:.2f} {w.word}")
