"""Original synthesized soundtrack for the promo (numpy only).
120 BPM, A minor. Impacts are placed on the visual hit times from hits.json.
usage: python3 music.py hits.json out.wav
"""
import json, sys, wave
import numpy as np

SR = 44100
cfg = json.load(open(sys.argv[1]))
HITS, DUR = cfg["hits"], cfg["duration"]
N = int(SR * (DUR + 0.5))
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(3)
BEAT = 0.5

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N: return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * gain * (1 - max(pan, 0))
    R[i:i + len(sig)] += sig * gain * (1 + min(pan, 0))

def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / d)

def lowpass(x, k):
    # one-pole lowpass, k in (0,1]
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc += k * (v - acc); y[i] = acc
    return y

def kick(strength=1.0):
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7.5)
    click = rng.standard_normal(n) * np.exp(-t * 300) * 0.25
    return np.tanh((s + click) * 1.6 * strength)

def snare():
    n = int(0.3 * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n); noise = noise - lowpass(noise, 0.15)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25)
    return (noise * np.exp(-t * 16) * 0.55 + body * 0.5)

def clap():
    n = int(0.25 * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n); noise = noise - lowpass(noise, 0.3)
    e = sum(np.exp(-np.maximum(t - d, 0) * 60) * (t >= d) for d in (0, 0.011, 0.022)) + np.exp(-t * 14) * 0.5
    return noise * e * 0.35

def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n); noise = noise - lowpass(noise, 0.6)
    return noise * np.exp(-t * (14 if open_ else 70)) * 0.22

def tom(f0=110):
    n = int(0.7 * SR); t = np.arange(n) / SR
    f = f0 * (1 + 0.6 * np.exp(-t * 18))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5)
    return np.tanh(s * 1.5)

def impact(big=False):
    d = 2.6 if big else 1.4
    n = int(d * SR); t = np.arange(n) / SR
    f = 32 + 140 * np.exp(-t * 9)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (1.6 if big else 3))
    noise = lowpass(rng.standard_normal(n), 0.08) * np.exp(-t * (2.5 if big else 5)) * 2.5
    crack = rng.standard_normal(n) * np.exp(-t * 40) * 0.5
    return np.tanh((boom * 1.3 + noise + crack) * (1.5 if big else 1.1))

def whoosh(d=1.0, rise=True):
    n = int(d * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    out = np.zeros(n); acc = 0.0
    ks = np.linspace(0.01, 0.35, n) if rise else np.linspace(0.35, 0.01, n)
    for i in range(n):
        acc += ks[i] * (noise[i] - acc); out[i] = acc
    amp = (t / d) ** 2 if rise else (1 - t / d) ** 2
    return out * amp * 0.9

def saw(freq, n):
    t = np.arange(n) / SR
    return 2 * ((t * freq) % 1) - 1

def note(freq):
    return 440 * 2 ** ((freq - 69) / 12)

# --- chord progression: Am  F  G  Em (one bar = 4 beats = 2s)
PROG = [(57, [57, 60, 64]), (53, [53, 57, 60]), (55, [55, 59, 62]), (52, [52, 55, 59])]

def pad(t0, t1, gain):
    for bar_t in np.arange(t0, t1, 2.0):
        root, chord = PROG[int(round(bar_t / 2)) % 4]
        n = int(2.0 * SR); tt = np.arange(n) / SR
        s = np.zeros(n)
        for m in chord:
            for det in (-0.08, 0.08):
                s += saw(note(m + 12) * (1 + det / 100), n)
        s = lowpass(s / 6, 0.05)
        e = np.minimum(tt / 0.3, 1) * np.minimum((2.0 - tt) / 0.3, 1)
        add(s * e, bar_t, gain * 0.5, -0.3); add(s * e, bar_t + 0.012, gain * 0.5, 0.3)

def bass(t0, t1, gain):
    for b in np.arange(t0, t1, BEAT / 2):
        root, _ = PROG[int(b // 2) % 4]
        if (b / (BEAT / 2)) % 4 == 0:  # leave space for kick
            continue
        n = int(0.24 * SR); tt = np.arange(n) / SR
        s = np.tanh(np.sin(2 * np.pi * note(root - 24) * tt) * 2.2) * env(n, 0.005, 0.12)
        add(s, b, gain)

def arp(t0, t1, gain):
    pattern = [0, 1, 2, 1, 2, 0, 2, 1]
    for k, b in enumerate(np.arange(t0, t1, BEAT / 2)):
        _, chord = PROG[int(b // 2) % 4]
        m = chord[pattern[k % 8]] + 24
        n = int(0.3 * SR); tt = np.arange(n) / SR
        s = (np.sin(2 * np.pi * note(m) * tt) + 0.3 * np.sin(2 * np.pi * note(m) * 2 * tt)) * env(n, 0.003, 0.09)
        add(s, b, gain, 0.4 if k % 2 else -0.4)

def drums(t0, t1, full=True, gain=1.0):
    for b in np.arange(t0, t1, BEAT):
        beat_in_bar = int(round(b / BEAT)) % 4
        add(kick(), b, 0.9 * gain)
        if beat_in_bar in (1, 3) and full:
            add(snare(), b, 0.55 * gain); add(clap(), b, 0.5 * gain)
        if full and beat_in_bar == 3:
            add(kick(0.7), b + 0.25, 0.5 * gain)
        for off in (0, 0.25):
            add(hat(open_=(off == 0.25 and full)), b + off, (0.5 if off else 0.3) * gain, 0.25)

# ---------------- arrangement ----------------
# Intro 0-4: drone + heartbeat
n = int(4.0 * SR); tt = np.arange(n) / SR
drone = lowpass(saw(note(33), n) + saw(note(33) * 1.005, n), 0.02) * np.minimum(tt / 2.5, 1) * 0.5
add(drone, 0.0, 0.6)
for hb in (0.5, 1.5, 2.5, 3.0, 3.25, 3.5, 3.75):
    add(kick(0.6), hb, 0.6)
add(whoosh(1.5), 2.5, 0.6)

# Main 4-24
drums(4.0, 24.0); bass(4.0, 24.0, 0.35); pad(4.0, 24.0, 0.18); arp(12.0, 24.0, 0.07)
# Breakdown 24-28 (emotional), build 28-32
pad(24.0, 32.0, 0.28); arp(24.0, 32.0, 0.09)
for b in np.arange(24.0, 28.0, 1.0): add(kick(0.6), b, 0.5)
drums(28.0, 30.0, full=False, gain=0.8)
for i, b in enumerate(np.arange(30.0, 32.0, 0.125)): add(snare(), b, 0.15 + 0.03 * i)
add(whoosh(2.0), 30.0, 0.8)
# Values 32-40: heavy, taiko on each word
drums(32.0, 40.0); bass(32.0, 40.0, 0.4); pad(32.0, 40.0, 0.2)
for b, f in zip((32, 33, 34, 35, 36, 37, 38), (90, 100, 90, 110, 120, 90, 80)):
    add(tom(f), b, 0.5, -0.2); add(tom(f * 1.5), b + 0.5, 0.25, 0.2)
add(whoosh(1.0), 39.0, 0.8)
# Outro 40-48
drums(40.0, 46.0, full=True, gain=0.8); bass(40.0, 46.0, 0.3); pad(40.0, 48.0, 0.22); arp(40.0, 46.0, 0.06)

# Impacts on every visual hit
for h in HITS:
    big = h in (4.0, 40.0)
    add(impact(big), h, 0.9 if big else 0.45)
    if big: add(whoosh(0.8), h - 0.8, 0.7)

# ---------------- master ----------------
mix = np.stack([L, R])
# simple stereo "room": a few delayed taps
room = np.zeros_like(mix)
for d, g in ((0.031, 0.25), (0.047, 0.2), (0.071, 0.15), (0.113, 0.1)):
    k = int(d * SR)
    room[0, k:] += mix[1, :-k] * g; room[1, k:] += mix[0, :-k] * g
mix = mix + room
# fades
t = np.arange(mix.shape[1]) / SR
mix *= np.clip(t / 0.3, 0, 1) * np.clip((DUR - t) / 2.0, 0, 1)
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6) * 0.89
pcm = (mix.T * 32767).astype(np.int16)
with wave.open(sys.argv[2], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote", sys.argv[2], f"{DUR}s")
