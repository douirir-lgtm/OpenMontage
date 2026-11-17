import json,sys
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8",cpu_threads=4)
import wave,numpy as np
w=wave.open("work/audio16k.wav");audio=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
segs,info=m.transcribe(audio,language="fr",word_timestamps=True,vad_filter=False,beam_size=5)
out=[]
for s in segs:
    out.append({"start":s.start,"end":s.end,"text":s.text,"words":[{"w":w.word,"s":round(w.start,3),"e":round(w.end,3),"p":round(w.probability,3)} for w in s.words]})
    print(round(s.start,1),s.text,flush=True)
json.dump(out,open("projet/transcription.json","w"),ensure_ascii=False,indent=1)
