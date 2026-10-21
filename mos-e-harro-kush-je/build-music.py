#!/usr/bin/env python3
"""Score of « Mos e harro kush je »: one of the four ElevenLabs Music takes, edited on the picture.

The take plays from 0 to the climax, stops dead at STOP (the cut to black before the eagle), stays silent while the
eagle appears, then comes back at RESUME on the take's own ring-out, under « Mos e harro kush je », fading out at 30 s.

Usage: python3 build-music.py [A|B|C|D]  ->  assets/music/score.wav (30 s)
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
TAKE = sys.argv[1] if len(sys.argv) > 1 else "D"
SRC = os.path.join(HERE, f"assets/music/musique-{TAKE}.mp3")
TOTAL, STOP, RESUME, RESUME_GAIN = 30.0, 24.85, 26.4, 0.8

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype="<f4").reshape(-1, 2)[: int(TOTAL * SR)].copy()
x = np.pad(x, ((0, int(TOTAL * SR) - len(x)), (0, 0)))

env = np.ones(len(x), dtype=np.float32)
s, r = int(STOP * SR), int(RESUME * SR)
f = int(0.02 * SR)
env[s : s + f] = np.linspace(1, 0, f)
env[s + f : r] = 0
g = int(0.4 * SR)
env[r : r + g] = np.linspace(0, RESUME_GAIN, g)
env[r + g :] = RESUME_GAIN * np.linspace(1, 0, len(x) - r - g) ** 1.5
x *= env[:, None]

x *= 10 ** (-1.0 / 20) / max(1e-9, np.max(np.abs(x)))
tmp = os.path.join(HERE, "assets/music/score.f32")
x.astype("<f4").tofile(tmp)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", tmp, os.path.join(HERE, "assets/music/score.wav")], check=True)
os.remove(tmp)
print(f"wrote assets/music/score.wav from take {TAKE}")
