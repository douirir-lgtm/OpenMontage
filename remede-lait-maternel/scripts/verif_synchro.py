"""Synchronisation des sous-titres : pour chaque instant t, mot surligné à l'écran (render.sub_state) comparé au mot
que faster-whisper entend à t dans la piste audio (transcription indépendante d'une fenêtre de 6 s autour de t).
  python3 scripts/verif_synchro.py --corrigee 8.5 81.2 81.9 150.0 233.0"""
import os, re, subprocess, sys, unicodedata
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render
from faster_whisper import WhisperModel

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))

ts = [float(x) for x in sys.argv[1:]]
m = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)
out = os.path.join(render.ROOT, "work/corrigee" if render.CORRIGEE else "work", "synchro")
os.makedirs(out, exist_ok=True)
for t in ts:
    t0 = max(0, t - 4)
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-to", str(t + 2), "-i", render.PATHS["AUDIO"], "-ac", "1", "-ar", "16000",
                        "-f", "f32le", "-"], capture_output=True, check=True).stdout
    segs, _ = m.transcribe(np.frombuffer(r, np.float32), language="fr", word_timestamps=True, vad_filter=False, beam_size=5)
    ws = [(w.start + t0, w.end + t0, w.word.strip()) for s in segs for w in s.words]
    heard = min(ws, key=lambda w: 0 if w[0] <= t < w[1] else min(abs(t - w[0]), abs(t - w[1])))
    st = render.sub_state(t)
    shown = next((w for w, act in st[1] if act), None) if st else None
    groupe = " ".join(w for w, _ in st[1]) if st else ""
    ok = shown is not None and (norm(shown) == norm(heard[2]) or norm(heard[2]) in norm(shown) or norm(shown) in norm(heard[2]))
    render.render(t).save(os.path.join(out, f"synchro_{t:.1f}s.png"))
    print(f"t={t:6.1f} s | entendu : « {heard[2]} » ({heard[0]:.2f}–{heard[1]:.2f}) | surligné : « {shown} » | groupe : {groupe!r} | {'OK' if ok else 'ÉCART'}")
