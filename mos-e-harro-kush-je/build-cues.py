#!/usr/bin/env python3
"""Word cues of « Mos e harro kush je » refined on the voice, and the SRT subtitles (V5).

cues.json (from build-voice.py) spreads each clause over its words by vowel count. Here every word boundary inside a
clause is moved to the quietest 10 ms of the voice within +/- 0.12 s of that estimate (the gap or the consonant between
two words); clause starts stay where silencedetect put them. The last line is the title of the end card, so it is not
burned in as a subtitle, but the SRT (a separate accessibility track) carries it, held until the end of the film.

Usage: python3 build-cues.py  ->  cues-v5.json + mos-e-harro-kush-je.srt
"""
import json
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 16000
cues = json.load(open(os.path.join(HERE, "cues.json"), encoding="utf-8"))
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(HERE, "assets/audio/voix-montage.wav"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype="<f4")
hop = int(0.01 * SR)
env = np.sqrt(np.convolve(x ** 2, np.ones(2 * hop) / (2 * hop), "same"))[::hop]
env_db = 20 * np.log10(env + 1e-9)


def snap(t, lo, hi):
    a, b = int(max(lo, t - 0.12) * 100), int(min(hi, t + 0.12) * 100)
    if b <= a:
        return t
    return (a + int(np.argmin(env_db[a:b]))) / 100 + 0.02     # the next word starts just after the dip


moved = []
for c in cues:
    ws = c["words"]
    for j in range(1, len(ws)):
        lo = ws[j - 1][1] + 0.10
        hi = ws[j + 1][1] - 0.10 if j + 1 < len(ws) else c["end"] - 0.10
        new = round(snap(ws[j][1], lo, hi), 2)
        moved.append(abs(new - ws[j][1]))
        ws[j][1] = new
json.dump(cues, open(os.path.join(HERE, "cues-v5.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


lines = []
for i, c in enumerate(cues):
    end = 29.9 if i == len(cues) - 1 else c["end"]
    lines += [str(i + 1), f"{ts(c['words'][0][1])} --> {ts(end)}", " ".join(w for w, _ in c["words"]), ""]
open(os.path.join(HERE, "mos-e-harro-kush-je.srt"), "w", encoding="utf-8").write("\n".join(lines))
print(f"wrote cues-v5.json and mos-e-harro-kush-je.srt; {len(moved)} word starts checked, median move {np.median(moved) * 1000:.0f} ms, max {max(moved) * 1000:.0f} ms")
