"""Remplace « C'est la thèse de Symbiose Science & Sunna. » (7,46–9,59 s) par la prise clonée
« C'est la thèse de Remède. » ; le reste de la piste est inchangé et la durée totale identique."""
import subprocess, numpy as np, sys
SR = 44100
PRISE = sys.argv[1] if len(sys.argv) > 1 else "work/voix/prise_9.wav"
A0, A1 = 7.46, 9.59          # passage d'origine (parole) à effacer
DEBUT = 7.55                 # début de la nouvelle phrase


def dec(path, ch):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", str(ch), "-ar", str(SR), "-af", "aresample=resampler=soxr",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, ch).copy()


orig = dec("work/audio.m4a", 2)
voix = dec(PRISE, 1)[:, 0]

# rognage de la prise sur la parole (+ 40 ms), fondus de 15 ms
hop = 441
rms = np.array([np.sqrt((voix[i:i + hop] ** 2).mean()) for i in range(0, len(voix) - hop, hop)])
act = np.where(20 * np.log10(rms + 1e-9) > -40)[0]
s, e = max(0, act[0] * hop - 1764), min(len(voix), (act[-1] + 1) * hop + 1764)
voix = voix[s:e]
f = int(0.015 * SR)
voix[:f] *= np.linspace(0, 1, f); voix[-f:] *= np.linspace(1, 0, f)

# niveau : même RMS de parole que la phrase d'origine
def rms_parole(x):
    r = np.array([np.sqrt((x[i:i + hop] ** 2).mean()) for i in range(0, len(x) - hop, hop)])
    r = r[20 * np.log10(r + 1e-9) > -40]
    return np.sqrt((r ** 2).mean())
ref = orig[int(A0 * SR):int(A1 * SR)].mean(axis=1)
gain = rms_parole(ref) / rms_parole(voix)
voix *= gain

out = orig.copy()
i0, i1 = int((A0 - 0.03) * SR), int((A1 + 0.03) * SR)
fz = int(0.02 * SR)
out[i0:i0 + fz] *= np.linspace(1, 0, fz)[:, None]          # fondu sortant vers le silence
out[i0 + fz:i1] = 0.0
out[i1 - fz:i1] = orig[i1 - fz:i1] * np.linspace(0, 1, fz)[:, None]
j = int(DEBUT * SR)
assert j + len(voix) < int(9.85 * SR), "la prise déborde sur la phrase suivante"
out[j:j + len(voix)] += voix[:, None]
assert len(out) == len(orig)
print(f"prise {PRISE}: {len(voix)/SR:.2f} s, gain {20*np.log10(gain):+.1f} dB, fin {DEBUT+len(voix)/SR:.2f} s, crête {np.abs(out).max():.2f}")
np.clip(out, -1, 1).astype(np.float32).tofile("work/voix/remede.f32")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "work/voix/remede.f32",
                "-c:a", "aac", "-b:a", "256k", "work/audio_remede.m4a"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "6.0", "-to", "11.0", "-i", "work/audio_remede.m4a", "work/voix/extrait_remede.wav"], check=True)
