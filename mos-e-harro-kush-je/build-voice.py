#!/usr/bin/env python3
"""Voice montage for « Mos e harro kush je »: places each phrase of the ElevenLabs take on the picture,
cutting only in silences, and writes the word cues used by the subtitles.

Usage: python3 build-voice.py  ->  assets/audio/voix-montage.wav (30 s) + cues.json
"""
import json
import os
import re
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
SRC = os.path.join(HERE, "assets/audio/prise-A.mp3")

# clauses of take A (source seconds, from silencedetect -38 dB / 0.12 s)
CLAUSES = [
    (0.00, 1.67, "Ka vende që i lamë mbrapa…"),
    (2.19, 2.44, "por që"),
    (2.59, 3.90, "kurrë nuk na lanë neve."),
    (4.50, 5.77, "Në zânin e gjyshërve,"),
    (5.97, 7.15, "në fjalët e nanës,"),
    (7.32, 8.56, "jeton kujtesa jonë."),
    (9.10, 10.62, "Edhe kur jeta na çon larg,"),
    (10.94, 12.94, "gjuha na e kujton prej kah vijmë."),
    (13.48, 15.88, "Sepse trashëgimia nuk asht veç ajo që marrim…"),
    (16.34, 18.43, "asht edhe ajo që ua lamë brezave."),
    (18.97, 20.06, "Mos e harro kush je."),
]
# groups of clauses moved as one block: (first clause, last clause, film start)
GROUPS = [(0, 2, 0.8), (3, 5, 5.8), (6, 7, 12.36), (8, 9, 18.6), (10, 10, 26.6)]
# subtitle chunks: clause indexes, key word
CHUNKS = [([0], "kurrë"), ([1, 2], "kurrë"), ([3], "gjyshërve,"), ([4], "nanës,"), ([5], "kujtesa"),
          ([6], "larg,"), ([7], "gjuha"), ([8], "trashëgimia"), ([9], "brezave."), ([10], "")]

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
src = np.frombuffer(raw, dtype="<f4")
out = np.zeros(int(30 * SR), dtype=np.float32)
shift = {}
for a, b, film in GROUPS:
    s0, s1 = CLAUSES[a][0], CLAUSES[b][1]
    off = film - s0
    i0, i1 = int(max(0, s0 - 0.06) * SR), int(min(len(src) / SR, s1 + 0.25) * SR)
    seg = src[i0:i1].copy()
    f = int(0.005 * SR)
    seg[:f] *= np.linspace(0, 1, f)
    seg[-f:] *= np.linspace(1, 0, f)
    j = int((s0 - 0.06 + off) * SR)
    out[j : j + len(seg)] += seg
    for k in range(a, b + 1):
        shift[k] = off

# word times: spread each clause over its words, weighted by vowel count
def weight(w):
    return max(1, len(re.findall(r"[aeiouyëâ]", w.lower()))) + 0.4

words = {}
for k, (s0, s1, text) in enumerate(CLAUSES):
    ws = text.split()
    tot = sum(weight(w) for w in ws)
    t = s0 + shift[k]
    words[k] = []
    for w in ws:
        words[k].append([w, round(t, 2)])
        t += (s1 - s0) * weight(w) / tot

cues = []
for n, (ks, key) in enumerate(CHUNKS):
    ws = [w for k in ks for w in words[k]]
    end = CLAUSES[ks[-1]][1] + shift[ks[-1]] + 0.45
    if n + 1 < len(CHUNKS):
        nxt = words[CHUNKS[n + 1][0][0]][0][1]
        end = min(end, nxt - 0.05)
    cues.append({"key": key, "words": ws, "end": round(end, 2)})
json.dump(cues, open(os.path.join(HERE, "cues.json"), "w"), ensure_ascii=False, indent=1)

peak = np.max(np.abs(out))
out *= 10 ** (-1.5 / 20) / peak
tmp = os.path.join(HERE, "assets/audio/voix-montage.f32")
out.tofile(tmp)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", tmp, "-ac", "2", os.path.join(HERE, "assets/audio/voix-montage.wav")], check=True)
os.remove(tmp)
print("wrote voix-montage.wav and cues.json")
