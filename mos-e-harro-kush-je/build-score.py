#!/usr/bin/env python3
"""Temporary score for « Mos e harro kush je » (30 s), synthesised locally with numpy.

Placeholder until a licensed track is chosen: soft piano, wind, strings that grow, a plucked
çifteli-like drone from the language section, a frame-drum (lodër) pulse into the climax at
23.5-24.8 s, a hard stop at 24.85 s, then a single low note after « Mos e harro kush je » (28.2 s).

Usage: python3 build-score.py  ->  assets/music/temp-score.wav (48 kHz stereo, about -16 LUFS via ffmpeg)
"""
import os
import subprocess
import wave

import numpy as np

SR = 48000
DUR = 30.0
N = int(SR * DUR)
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)
t_all = np.arange(N) / SR


def hz(note):
    names = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
    n, o = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((names[n] + 12 * (o + 1) - 69) / 12)


def place(buf, sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    l, r = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    buf[0, i : i + len(sig)] += sig * gain * l
    buf[1, i : i + len(sig)] += sig * gain * r


def piano(note, dur=3.0):
    f = hz(note)
    t = np.arange(int(SR * dur)) / SR
    s = np.zeros_like(t)
    for k, a in [(1, 1.0), (2, 0.42), (3, 0.18), (4, 0.09), (5, 0.04)]:
        s += a * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * t) * np.exp(-t * (1.1 + 0.9 * k))
    att = np.minimum(1, t / 0.006)
    return s * att * 0.5


def pluck(note, dur=1.6):
    # Karplus-Strong: a plucked two-string instrument (çifteli-like colour)
    f = hz(note)
    p = int(SR / f)
    n = int(SR * dur)
    out = np.zeros(n)
    buf = rng.uniform(-1, 1, p)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out * 0.35


def pad(notes, dur, attack=1.6, release=1.4):
    t = np.arange(int(SR * dur)) / SR
    s = np.zeros_like(t)
    for note in notes:
        f = hz(note)
        for det in (-0.12, 0.0, 0.11):
            ff = f * 2 ** (det / 12)
            for k in range(1, 7):
                s += (1 / k) * np.sin(2 * np.pi * ff * k * t + rng.uniform(0, 6.28)) * (0.8 ** k)
    env = np.minimum(1, t / attack) * np.minimum(1, (dur - t) / release)
    vib = 1 + 0.05 * np.sin(2 * np.pi * 5.2 * t)
    return s * env * vib / (len(notes) * 6)


def drum(dur=1.4, f0=68):
    t = np.arange(int(SR * dur)) / SR
    f = f0 * (1 + 0.6 * np.exp(-t * 18))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    skin = rng.normal(0, 1, len(t)) * np.exp(-t * 40) * 0.25
    return (body + skin) * 0.9


def lowpass(x, a):
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def reverb(x, secs=3.2, mix=0.32):
    n = int(SR * secs)
    t = np.arange(n) / SR
    out = np.zeros_like(x)
    L = x.shape[1] + n
    nfft = 1 << (L - 1).bit_length()
    for c in range(2):
        ir = rng.normal(0, 1, n) * np.exp(-t * 6.9 / secs)
        ir[: int(0.012 * SR)] = 0
        wet = np.fft.irfft(np.fft.rfft(x[c], nfft) * np.fft.rfft(ir, nfft), nfft)[: x.shape[1]]
        wet /= np.max(np.abs(wet)) + 1e-9
        out[c] = (1 - mix) * x[c] + mix * wet * np.max(np.abs(x[c]))
    return out


mus = np.zeros((2, N))

# wind (0-7 s, returns softly on the mountain ridge 17.6-21 s)
wn = rng.normal(0, 1, N)
wind = lowpass(wn, 0.012) * 6
wenv = np.interp(t_all, [0, 1.5, 5.5, 7.2, 17.6, 19, 21, 22.5], [0, 0.16, 0.13, 0, 0, 0.1, 0.08, 0])
wenv *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.23 * t_all)
mus[0] += wind * wenv
mus[1] += np.roll(wind, 900) * wenv

# piano: sparse in KUJTESA, then a broken-chord pattern
for note, t0 in [("D3", 0.7), ("A3", 0.72), ("F4", 1.9), ("A4", 3.0), ("E4", 4.1), ("D4", 4.9)]:
    place(mus, piano(note, 4), t0, 0.4, -0.15)
CH = [  # (start, end, chord tones for arpeggio, pad notes)
    (5.6, 8.4, ["A#2", "F3", "A#3", "D4"], ["A#2", "F3", "D4"]),
    (8.4, 11.2, ["F2", "C3", "F3", "A3"], ["F2", "C3", "A3"]),
    (11.2, 14.0, ["C3", "G3", "C4", "E4"], ["C3", "G3", "E4"]),
    (14.0, 16.8, ["D3", "A3", "D4", "F4"], ["D3", "A3", "F4"]),
    (16.8, 18.6, ["A#2", "F3", "A#3", "D4"], ["A#2", "F3", "D4"]),
    (18.6, 20.4, ["G2", "D3", "G3", "A#3"], ["G2", "D3", "A#3", "D4"]),
    (20.4, 22.2, ["A#2", "F3", "A#3", "D4"], ["A#2", "F3", "D4", "F4"]),
    (22.2, 23.5, ["F2", "C3", "F3", "A3"], ["F2", "C3", "A3", "C4"]),
    (23.5, 24.85, ["A2", "E3", "A3", "C#4"], ["A2", "E3", "C#4", "E4"]),
]
for i, (a, b, arp, pd) in enumerate(CH):
    step = 0.4 if a < 18.6 else 0.3
    k, t0 = 0, a
    while t0 < b - 0.05:
        n = arp[k % len(arp)]
        place(mus, piano(n, 2.4), t0, 0.42 + 0.1 * (a > 18), 0.2 * ((k % 2) * 2 - 1))
        k += 1
        t0 += step
    strength = np.interp(a, [5.6, 11.2, 18.6, 23.5], [0.25, 0.45, 0.8, 1.2])
    place(mus, pad(pd, b - a + 1.2, attack=0.9 if a > 18 else 1.6), a, strength)
    place(mus, pad([p[:-1] + str(int(p[-1]) + 1) for p in pd], b - a + 1.2, attack=1.2), a, strength * 0.35, 0.3)

# çifteli-like plucks over the language and heritage sections (D drone, A, ornaments)
motif = [("D3", 0), ("A3", 0.3), ("D4", 0.6), ("C4", 0.75), ("A3", 0.9)]
for bar in np.arange(11.2, 24.6, 1.2):
    for n, off in motif:
        if bar + off < 24.8:
            place(mus, pluck(n), bar + off, 0.5 if bar < 18 else 0.7, 0.35)

# frame drum pulse into the climax
for td in [18.6, 20.4, 21.3, 22.2, 22.8, 23.5, 23.8, 24.1, 24.4]:
    place(mus, drum(), td, 0.5 if td < 23.5 else 0.8)

# swell before the stop
sw = np.interp(t_all, [22.9, 24.8, 24.85], [0, 0.35, 0]) * lowpass(rng.normal(0, 1, N), 0.08) * 3
mus[0] += sw
mus[1] += sw

# hard stop at 24.85 s (keeps a natural tail through the reverb below)
cut = int(24.85 * SR)
fade = int(0.04 * SR)
mus[:, cut : cut + fade] *= np.linspace(1, 0, fade)
mus[:, cut + fade :] = 0

# final: the eagle (low boom 25.6) and a single note after « Mos e harro kush je » (28.2)
boom = drum(3.0, 42) * 0.7
place(mus, boom, 25.6, 0.55)
for note, g in [("D2", 0.6), ("A3", 0.35), ("D4", 0.3), ("F4", 0.2)]:
    place(mus, piano(note, 4.5), 28.25, g)
place(mus, pad(["D3", "A3", "D4"], 4.6, attack=1.5, release=2.5), 25.4, 0.18)

mus = reverb(mus)
mus = np.tanh(mus / (np.max(np.abs(mus)) + 1e-9) * 1.2) * 0.85
fo = int(0.6 * SR)
mus[:, -fo:] *= np.linspace(1, 0, fo)

os.makedirs(os.path.join(HERE, "assets/music"), exist_ok=True)
raw = os.path.join(HERE, "assets/music/temp-score-raw.wav")
with wave.open(raw, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mus.T * 32767).astype("<i2").tobytes())
out = os.path.join(HERE, "assets/music/temp-score.wav")
# static gain to -16 LUFS (a dynamic loudnorm would lift the silence before the last line)
meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
summary = meas[meas.rfind("Summary:") :]
lufs = float(summary.split("I:")[1].split("LUFS")[0])
peak = float(summary.split("Peak:")[1].split("dBFS")[0])
gain = min(-16 - lufs, -1.5 - peak)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", f"volume={gain:.2f}dB", out], check=True)
print(f"measured {lufs:.1f} LUFS, peak {peak:.1f} dBTP, gain {gain:+.1f} dB")
os.remove(raw)
print("wrote", out)
