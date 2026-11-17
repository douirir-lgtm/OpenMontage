"""Choisit la meilleure prise « Chaque jour, » (version corrigée) parmi work/corrigee/prise_jour_*.wav.

Pour chaque prise : transcription faster-whisper (mots datés) ; si la prise contient la phrase entière, on découpe
« Chaque jour, » au creux d'énergie entre « jour » et « c'est ». L'extrait est retranscrit seul (doit donner « Chaque
jour ») ; on mesure sa hauteur de voix (F0 médiane, pyin) et sa durée, comparées à « Une seule tétée, » d'origine
(80,84–81,60 s de work/audio_remede.m4a). Score = écart de hauteur (demi-tons) + 2 × écart de durée (s).
Une prise découpée n'est gardée que si la coupe tombe sur un silence (creux < -45 dB).
Écrit work/corrigee/jour_<n>.wav, work/corrigee/choix_prise.json et copie la meilleure en work/corrigee/jour_retenu.wav.
  python3 scripts/choix_prise.py
"""
import glob, json, re, shutil, subprocess, unicodedata
import numpy as np, librosa
from faster_whisper import WhisperModel

SR = 16000
REF = ("work/audio_remede.m4a", 80.84, 81.60)


def dec(path, t0=None, t1=None, sr=SR):
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", str(t0), "-to", str(t1)] if t0 is not None else []) + \
          ["-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32).copy()


def f0(x, sr=SR):
    f, v, _ = librosa.pyin(x, fmin=70, fmax=400, sr=sr, frame_length=1024)
    f = f[v & ~np.isnan(f)]
    return float(np.median(f)) if len(f) else float("nan")


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z ]", "", "".join(c for c in s if unicodedata.category(c) != "Mn")).split()


m = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)


def trans(x):
    segs, _ = m.transcribe(x, language="fr", word_timestamps=True, vad_filter=False, beam_size=5)
    return [w for s in segs for w in s.words]


ref = dec(*REF)
f0_ref, dur_ref = f0(ref), REF[2] - REF[1]
print(f"référence « Une seule tétée, » : F0 {f0_ref:.0f} Hz, durée {dur_ref:.2f} s")
res = []
for p in sorted(glob.glob("work/corrigee/prise_jour_*.wav"), key=lambda s: int(re.findall(r"(\d+)\.wav", s)[0])):
    n = int(re.findall(r"(\d+)\.wav", p)[0])
    x = dec(p)
    ws = trans(x)
    texte = "".join(w.word for w in ws).strip()
    t = [norm(w.word) for w in ws]
    r = dict(prise=n, fichier=p, transcription=texte)
    # repère « jour »
    k = next((i for i, w in enumerate(t) if w and w[0].startswith("jour")), None)
    if k is None or k == 0 or not (t[k - 1] and t[k - 1][0] == "chaque"):
        r.update(ok=False, raison="« Chaque jour » non trouvé")
        res.append(r); print(r); continue
    fin = ws[k].end
    if k + 1 < len(ws):   # phrase entière : coupe au creux d'énergie entre « jour » et le mot suivant
        a, b = int((ws[k].end - 0.12) * SR), int(min(ws[k + 1].start + 0.12, ws[k + 1].end) * SR)
        hop = 160
        e = np.array([np.sqrt((x[i:i + hop] ** 2).mean()) for i in range(a, b - hop, hop)])
        fin = (a + int(np.argmin(e)) * hop + hop // 2) / SR
        r["creux_dB"] = round(float(20 * np.log10(e.min() + 1e-9)), 1)
    else:
        fin = len(x) / SR
    deb = max(0.0, ws[k - 1].start - 0.15)
    # extrait à 24 kHz (qualité d'origine de la prise)
    y = dec(p, sr=24000)[int(deb * 24000):int(fin * 24000)]
    out = f"work/corrigee/jour_{n}.wav"
    import wave
    o = wave.open(out, "wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(24000)
    o.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()); o.close()
    xs = dec(out)
    hop = 160
    rr = np.array([np.sqrt((xs[i:i + hop] ** 2).mean()) for i in range(0, len(xs) - hop, hop)])
    act = np.where(20 * np.log10(rr + 1e-9) > -40)[0]
    dur = (act[-1] - act[0] + 1) * hop / SR if len(act) else 0
    t2 = "".join(w.word for w in trans(xs)).strip()
    ok = norm(t2)[:2] == ["chaque", "jour"] and len(norm(t2)) == 2
    if ok and r.get("creux_dB", -99) > -45:   # la coupe doit tomber sur un vrai silence
        ok = False
        r["raison"] = "coupe « jour | c'est » pas sur un silence (creux > -45 dB)"
    fz = f0(xs)
    score = abs(12 * np.log2(fz / f0_ref)) + 2 * abs(dur - dur_ref) if ok else 99
    r.update(ok=bool(ok), extrait=out, transcription_extrait=t2, f0_hz=round(fz, 1), duree_parole_s=round(float(dur), 2),
             coupe_s=[round(deb, 2), round(fin, 2)], score=round(float(score), 2))
    res.append(r); print(r, flush=True)

bons = sorted([r for r in res if r.get("ok")], key=lambda r: r["score"])
json.dump(dict(reference=dict(f0_hz=round(f0_ref, 1), duree_s=round(dur_ref, 2)), prises=res, classement=[r["prise"] for r in bons]),
          open("work/corrigee/choix_prise.json", "w"), ensure_ascii=False, indent=1)
print("classement :", [(r["prise"], r["score"]) for r in bons])
if bons:
    shutil.copy(bons[0]["extrait"], "work/corrigee/jour_retenu.wav")
    print("retenue : prise", bons[0]["prise"])
