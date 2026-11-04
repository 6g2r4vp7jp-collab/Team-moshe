"""Original soundtrack + sound design for the TEAM MOSHE promo (pure numpy synthesis, no samples).
Written to the picture cut: 120 BPM (beat = 0.5 s), A minor.
Also lays the real location sound of the training shots (pads, gloves) under the music.
usage: python3 soundtrack.py out.wav
"""
import os, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from edl import SHOTS, DURATION

SR = 44100
N = int(SR * DURATION)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(11)
B = 0.5
SHOTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "work", "shots")

def add(sig, t, g=1.0, pan=0.0):
    i = int(round(t * SR))
    if i >= N or i < 0: return
    s = sig[: N - i]
    if s.ndim == 2:
        L[i:i+len(s)] += s[:, 0] * g; R[i:i+len(s)] += s[:, 1] * g; return
    L[i:i+len(s)] += s * g * (1 - max(pan, 0)); R[i:i+len(s)] += s * g * (1 + min(pan, 0))

def tt(d): return np.arange(int(d * SR)) / SR
def lp(x, k):
    y = np.empty_like(x); a = 0.0
    for i, v in enumerate(x): a += k * (v - a); y[i] = a
    return y
def hp(x, k): return x - lp(x, k)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def saw(f, t): return 2 * ((t * f) % 1) - 1

# ---------------- instruments ----------------
def kick(s=1.0):
    t = tt(0.5); f = 42 + 120 * np.exp(-t * 30)
    x = np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t * 6.5) + rng.standard_normal(len(t)) * np.exp(-t * 350) * 0.3
    return np.tanh(x * 1.8 * s)
def snare():
    t = tt(0.35); n = hp(rng.standard_normal(len(t)), 0.2)
    return n * np.exp(-t * 14) * 0.6 + np.sin(2*np.pi*185*t) * np.exp(-t * 22) * 0.55
def clap():
    t = tt(0.3); n = hp(rng.standard_normal(len(t)), 0.35)
    e = sum(np.exp(-np.maximum(t-d, 0)*70)*(t >= d) for d in (0, .01, .021)) + np.exp(-t*12)*.45
    return n * e * 0.4
def hat(op=False):
    t = tt(0.25 if op else 0.05); n = hp(rng.standard_normal(len(t)), 0.7)
    return n * np.exp(-t * (12 if op else 80)) * 0.2
def tom(f0=95, d=0.8):
    t = tt(d); f = f0 * (1 + 0.7 * np.exp(-t * 20))
    x = np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t * 4.5) + lp(rng.standard_normal(len(t)), .05) * np.exp(-t*25) * 1.5
    return np.tanh(x * 1.6)
def impact(size=1.0):
    d = 1.2 + 1.8 * size; t = tt(d)
    f = 30 + 150 * np.exp(-t * 8)
    boom = np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t * (3.2 - 1.6 * size))
    body = lp(rng.standard_normal(len(t)), 0.06) * np.exp(-t * (5 - 2.5 * size)) * 3
    crack = hp(rng.standard_normal(len(t)), 0.3) * np.exp(-t * 30) * 0.8
    return np.tanh((boom * 1.4 + body + crack) * 1.4)
def punch():                                  # designed glove/pad hit
    t = tt(0.25)
    thump = np.sin(2*np.pi*(70 + 90*np.exp(-t*40))*t) * np.exp(-t * 22)
    slap = hp(rng.standard_normal(len(t)), 0.25) * np.exp(-t * 55)
    return np.tanh((thump * 1.3 + slap * 0.9) * 1.5)
def whoosh(d=0.8, up=True):
    t = tt(d); n = rng.standard_normal(len(t)); k = np.linspace(.02, .4, len(t)) if up else np.linspace(.4, .02, len(t))
    out = np.empty_like(n); a = 0.0
    for i in range(len(n)): a += k[i] * (n[i] - a); out[i] = a
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2 if not up else (t / d) ** 2.2
    return out * env * 1.6
def riser(d):
    t = tt(d); f = 200 * 2 ** (t / d * 3)
    tone = np.sin(2*np.pi*np.cumsum(f)/SR) * 0.25 + whoosh(d) * 0.8
    return tone * (t / d) ** 2
def sub_drop(d=1.5):
    t = tt(d); f = 70 * np.exp(-t * 1.2) + 25
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t * 1.0)
def heartbeat():
    return kick(0.55) * 0.8
def breath(d=0.6):                         # sharp fighter exhale
    t = tt(d); n = rng.standard_normal(len(t))
    x = hp(lp(n, .35), .04) * (np.minimum(t / .03, 1) * np.exp(-t / (d * .3)))
    return x * 1.4

PROG_A = [57, 53, 55, 52]          # Am F G Em   (dark)
PROG_B = [53, 48, 55, 57]          # F  C G Am   (lift)
CH = {57: [57, 60, 64], 53: [53, 57, 60], 55: [55, 59, 62], 52: [52, 55, 59], 48: [48, 52, 55]}

def pad(t0, t1, g, prog, bright=0.05):
    for bt in np.arange(t0, t1, 2.0):
        root = prog[int(round((bt - t0) / 2)) % 4]; t = tt(2.0); s = np.zeros(len(t))
        for m in CH[root]:
            for det in (-.1, .1): s += saw(mtof(m + 12) * (1 + det / 100), t)
        s = lp(s / 6, bright) * np.minimum(t / .25, 1) * np.minimum((2 - t) / .25, 1)
        add(s, bt, g * .55, -.35); add(s, bt + .013, g * .55, .35)

def bass(t0, t1, g, prog, dist=2.5):
    for b in np.arange(t0, t1, B / 2):
        if round((b - t0) / (B / 2)) % 4 == 0: continue
        root = prog[int((b - t0) // 2) % 4]; t = tt(.23)
        add(np.tanh(np.sin(2*np.pi*mtof(root - 24)*t) * dist) * np.exp(-t / .1), b, g)

def arp(t0, t1, g, prog):
    pat = [0, 1, 2, 1, 2, 0, 2, 1]
    for k, b in enumerate(np.arange(t0, t1, B / 2)):
        root = prog[int((b - t0) // 2) % 4]; m = CH[root][pat[k % 8]] + 24; t = tt(.3)
        add((np.sin(2*np.pi*mtof(m)*t) + .3*np.sin(4*np.pi*mtof(m)*t)) * np.exp(-t / .09), b, g, .45 if k % 2 else -.45)

def beat(t0, t1, g=1.0, hats16=False, snare_on=True):
    for b in np.arange(t0, t1, B):
        bi = int(round(b / B)) % 4
        add(kick(), b, .9 * g)
        if bi in (1, 3) and snare_on: add(snare(), b, .5 * g); add(clap(), b, .45 * g)
        if bi == 3: add(kick(.7), b + .25, .45 * g)
        steps = (0, .125, .25, .375) if hats16 else (0, .25)
        for o in steps: add(hat(op=(o == .25 and not hats16)), b + o, (.45 if o else .28) * g, .25)

# ---------------- arrangement v2 (matches the picture, 46 s) ----------------
# 0-1.5 cold open: two hits on Or's strikes
add(impact(1.0), 0.0, .9); add(punch(), 0.0, .7)
add(impact(.6), 0.75, .6); add(punch(), 0.75, .6)
add(whoosh(.6), 0.9, .5)
# 1.5-5 hero walkout (slow-mo): drone, crowd air, taiko, riser into the drop
t = tt(3.5); drone = lp(saw(mtof(33), t) + saw(mtof(33) * 1.006, t), .02) * np.minimum(t / 1.0, 1) * .55
add(drone, 1.5, .7)
add(impact(.8), 2.0, .75)                          # name slam "אור משה"
for b in (2.5, 3.0, 3.5, 4.0, 4.25, 4.5, 4.75): add(tom(85 if b < 4 else 105, .6), b, .45, -.15)
pad(1.5, 5.0, .16, PROG_A, .03)
add(riser(2.5), 2.5, .55)
# 5-15 BUILD A: the drop, fighter <-> coach
add(impact(1.0), 5.0, .8)
beat(5.0, 15.0); bass(5.0, 15.0, .33, PROG_A); pad(5.0, 15.0, .14, PROG_A)
add(impact(.5), 10.0, .4)                          # "עכשיו הוא בונה את הדור הבא"
# 15-20 BUILD B: lift + faster cuts, snare roll into the ring
beat(15.0, 18.5, .95, hats16=True); bass(15.0, 18.5, .3, PROG_B, 1.8); pad(15.0, 20.0, .2, PROG_B, .06); arp(15.0, 20.0, .08, PROG_B)
for i, b in enumerate(np.arange(18.5, 20.0, .125)): add(snare(), b, .12 + .025 * i)
add(riser(1.5), 18.5, .6); add(whoosh(.8), 19.2, .5)
# 20-25 CLIMAX: heavy, toms on every half-beat cut
add(impact(1.0), 20.0, .9)
beat(20.0, 25.0, 1.05, hats16=True); bass(20.0, 25.0, .38, PROG_A, 3.5); pad(20.0, 25.0, .16, PROG_A)
for b in np.arange(21.0, 25.0, .5): add(tom(110, .5), b, .25, .2); add(punch(), b, .35)
add(whoosh(.5), 24.5, .6)
# 25-27.5 SLOW-MO knockdown: music drops out
add(sub_drop(2.0), 25.0, .9); add(impact(.9), 25.0, .6)
t = tt(2.5); air = lp(rng.standard_normal(len(t)), .01) * np.sin(np.pi * t / 2.5) * 1.2
add(air, 25.0, .5)
for b in (25.5, 25.75, 26.75, 27.0): add(heartbeat(), b, .7)
add(impact(1.0), 26.25, .9); add(punch(), 26.25, .8)      # the knockdown lands
add(breath(.6), 25.2, .5)
# 27.5-30 hand raised: triumphant chord, "יוצרים אלופים"
add(impact(.8), 27.5, .7)
pad(27.5, 30.0, .3, [57, 53], .08); arp(27.5, 30.0, .09, [57, 53])
for b in np.arange(27.5, 30.0, 1.0): add(kick(.8), b, .55)
add(riser(.8), 29.2, .5)
# 30-35 achievements: full power
add(impact(1.0), 30.0, .85)
beat(30.0, 35.0, 1.05, hats16=True); bass(30.0, 35.0, .38, PROG_A, 3.5); pad(30.0, 35.0, .18, PROG_A)
for b in np.arange(30.0, 35.0, .5): add(punch(), b, .3)
add(whoosh(.5), 34.5, .6)
# 35-37.5 final hero moment: tension, heartbeat, riser
add(sub_drop(2.5), 35.0, .7)
t = tt(2.5); add(lp(saw(mtof(45), t) + saw(mtof(45) * 1.004, t), .015) * (t / 2.5), 35.0, .55)
for b in (35.5, 36.0, 36.5, 36.75, 37.0, 37.125, 37.25): add(heartbeat(), b, .6)
add(riser(2.4), 35.0, .7); add(breath(.7), 35.3, .45)
# 37.5 LOGO REVEAL: the biggest hit, then the outro
add(impact(1.0), 37.5, 1.0); add(impact(.7), 37.5, .5); add(whoosh(.9, up=False), 37.5, .5)
pad(37.5, 46.0, .26, [57, 53, 55, 57], .05)
for b in np.arange(38.5, 41.0, 1.0): add(kick(.8), b, .55)
add(tom(80, 1.2), 39.0, .3); add(tom(90, 1.2), 40.0, .3)
add(riser(.9), 40.1, .45)
add(impact(1.0), 41.0, .85)                        # CTA
t = tt(5.0); add(lp(saw(mtof(45), t) + saw(mtof(45) * 1.005, t), .03) * np.exp(-t / 2.5), 41.0, .5)

# lower-third swishes
for ts in (30.0, 31.25, 32.5, 33.75): add(whoosh(.3, up=False), ts, .25, .3)

# ---------------- location sound from the training shots ----------------
LOC_GAIN = {"IMG_7970.mov": .7, "D67A6790.MP4": .45, "D67A6791.MP4": .45, "D67A6795.MP4": .35,
            "IMG_1612.MOV": .45, "IMG_1601.MOV": .4, "IMG_7892.MOV": .5, "IMG_7997.MOV": .35, "IMG_7991.MOV": .45,
            "IMG_7991_small.mov": .0}
for i, (t0, dur, src, sin, speed, crop) in enumerate(SHOTS):
    p = os.path.join(SHOTDIR, f"{i:02d}.wav")
    if speed != 1.0 or not os.path.exists(p) or t0 >= 37.5: continue
    with wave.open(p) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, w.getnchannels()).astype(float) / 32768
    if x.shape[1] == 1: x = np.repeat(x, 2, 1)
    n = min(len(x), int(dur * SR)); x = x[:n]
    fade = np.ones(n); k = min(int(.012 * SR), n // 2); fade[:k] = np.linspace(0, 1, k); fade[-k:] = np.linspace(1, 0, k)
    add(x * fade[:, None], t0, LOC_GAIN.get(src, .3))

# ---------------- master ----------------
mix = np.stack([L, R])
room = np.zeros_like(mix)
for d, g in ((.029, .22), (.043, .18), (.067, .13), (.109, .09), (.151, .06)):
    k = int(d * SR); room[0, k:] += mix[1, :-k] * g; room[1, k:] += mix[0, :-k] * g
mix += room
tl = np.arange(N) / SR
mix *= np.clip((DURATION - tl) / 1.2, 0, 1)
mix = np.tanh(mix / np.percentile(np.abs(mix), 99.9) * 1.25)
mix = mix / np.max(np.abs(mix)) * 0.94
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix.T * 32767).astype(np.int16).tobytes())
print("wrote", sys.argv[1])
