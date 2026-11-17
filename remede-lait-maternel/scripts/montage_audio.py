"""Remplace un passage de la voix par une prise clonée (XTTS-v2), sans décaler le reste : le passage effacé est
remplacé par la prise + du silence, la durée totale est identique.

1re version (sans option) : « C'est la thèse de Symbiose Science & Sunna. » (7,46–9,59 s) -> prise « C'est la thèse de
Remède. » ; work/audio.m4a -> work/audio_remede.m4a.
  python3 scripts/montage_audio.py [prise.wav]

Version corrigée : « Une seule tétée, » (80,35–81,64 s) -> « Chaque jour, » ; part de work/audio_remede.m4a (déjà avec
« Remède ») -> work/audio_corrigee.m4a. La prise est un extrait (« Chaque jour, ») découpé par scripts/choix_prise.py.
  python3 scripts/montage_audio.py --corrigee [extrait.wav]

Toutes les valeurs peuvent être imposées : --source --sortie --efface A0 A1 --debut T | --fin T --marge M --limite T --extrait T0 T1
"""
import argparse, subprocess, numpy as np
SR = 44100

ap = argparse.ArgumentParser()
ap.add_argument("prise", nargs="?", default=None)
ap.add_argument("--corrigee", action="store_true")
ap.add_argument("--source"); ap.add_argument("--sortie")
ap.add_argument("--efface", nargs=2, type=float, metavar=("A0", "A1"), help="passage d'origine (parole) à effacer, en s")
ap.add_argument("--debut", type=float, help="début de la nouvelle prise (s)")
ap.add_argument("--fin", type=float, help="ou : fin de la nouvelle prise (s), si on la cale sur la parole qui suit")
ap.add_argument("--marge", type=float, help="marge (s) effacée de part et d'autre du passage, avec fondus de 20 ms")
ap.add_argument("--limite", type=float, help="la prise ne doit pas dépasser cet instant (s)")
ap.add_argument("--rogne", type=float, help="marge de silence (s) gardée autour de la parole de la prise")
ap.add_argument("--extrait", nargs=2, type=float, metavar=("T0", "T1"), help="extrait WAV de contrôle écrit après le montage")
a = ap.parse_args()
if a.corrigee:
    D = dict(prise="work/corrigee/jour_retenu.wav", source="work/audio_remede.m4a", sortie="work/audio_corrigee.m4a",
             efface=(80.35, 81.64), debut=None, fin=81.61, marge=0.0, limite=81.64, rogne=0.03, extrait=(78.0, 86.0))
else:
    D = dict(prise="work/voix/prise_9.wav", source="work/audio.m4a", sortie="work/audio_remede.m4a",
             efface=(7.46, 9.59), debut=7.55, fin=None, marge=0.03, limite=9.85, rogne=0.04, extrait=(6.0, 11.0))
if a.debut is not None or a.fin is not None:      # calage imposé : on ne mélange pas avec celui par défaut
    D["debut"], D["fin"] = None, None
for k, v in D.items():
    if getattr(a, k) is None:
        setattr(a, k, v)
A0, A1 = a.efface


def dec(path, ch):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", str(ch), "-ar", str(SR), "-af", "aresample=resampler=soxr",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, ch).copy()


orig = dec(a.source, 2)
voix = dec(a.prise, 1)[:, 0]

# rognage de la prise sur la parole (+ marge), fondus de 15 ms
hop = 441
rms = np.array([np.sqrt((voix[i:i + hop] ** 2).mean()) for i in range(0, len(voix) - hop, hop)])
act = np.where(20 * np.log10(rms + 1e-9) > -40)[0]
m = int(a.rogne * SR)
s, e = max(0, act[0] * hop - m), min(len(voix), (act[-1] + 1) * hop + m)
voix = voix[s:e]
f = int(0.015 * SR)
voix[:f] *= np.linspace(0, 1, f); voix[-f:] *= np.linspace(1, 0, f)

# niveau : même RMS de parole que le passage d'origine
def rms_parole(x):
    r = np.array([np.sqrt((x[i:i + hop] ** 2).mean()) for i in range(0, len(x) - hop, hop)])
    r = r[20 * np.log10(r + 1e-9) > -40]
    return np.sqrt((r ** 2).mean())
ref = orig[int(A0 * SR):int(A1 * SR)].mean(axis=1)
gain = rms_parole(ref) / rms_parole(voix)
voix *= gain

out = orig.copy()
i0, i1 = int((A0 - a.marge) * SR), int((A1 + a.marge) * SR)
fz = int(0.02 * SR)
out[i0:i0 + fz] *= np.linspace(1, 0, fz)[:, None]          # fondu sortant vers le silence
out[i0 + fz:i1] = 0.0
out[i1 - fz:i1] = orig[i1 - fz:i1] * np.linspace(0, 1, fz)[:, None]
debut = a.debut if a.debut is not None else a.fin - len(voix) / SR
j = int(debut * SR)
assert j >= i0 + fz, "la prise commence avant le passage effacé"
assert j + len(voix) <= int(a.limite * SR), "la prise déborde sur la phrase suivante"
out[j:j + len(voix)] += voix[:, None]
assert len(out) == len(orig)
print(f"prise {a.prise}: {len(voix)/SR:.2f} s, gain {20*np.log10(gain):+.1f} dB, début {debut:.2f} s, fin {debut+len(voix)/SR:.2f} s, "
      f"crête {np.abs(out).max():.2f}")
tmp = a.sortie + ".f32"
np.clip(out, -1, 1).astype(np.float32).tofile(tmp)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", tmp,
                "-c:a", "aac", "-b:a", "256k", a.sortie], check=True)
import os; os.remove(tmp)
ext = a.sortie.rsplit(".", 1)[0] + "_extrait.wav" if a.corrigee else "work/voix/extrait_remede.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.extrait[0]), "-to", str(a.extrait[1]), "-i", a.sortie, ext], check=True)
print("->", a.sortie, "| extrait :", ext)
