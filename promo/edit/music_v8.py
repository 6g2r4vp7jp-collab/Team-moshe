"""TEAM MOSHE promo v8 - original cinematic trailer score, slow-build edition (piano, strings, choir, soft timpani): cinematic sports trailer x modern trap (120 BPM, A minor).
Composed and synthesized here from scratch (no samples, no third-party music) -> owned outright,
free to use commercially on Instagram / TikTok / ads.  Cut points come from edl.py.
usage: python3 music_v4.py out.wav
"""
import os, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from edl import SHOTS, DURATION as PIC_DURATION, MUSIC_OFFSET as OFF, hit_times
try:
    from edl import MUSIC_INSERT          # (music time, seconds): whole bars duplicated inside the fight section
except ImportError:
    MUSIC_INSERT = (16.0, 0.0)
INS_T, INS_X = MUSIC_INSERT
DURATION = PIC_DURATION + OFF - INS_X  # the score is composed at its original length, then extended by INS_X

SR = 44100
N = int(SR * DURATION)
rng = np.random.default_rng(7)
BUS = {k: np.zeros((N, 2)) for k in ("drums", "bass", "music", "fx", "loc")}
VERB = np.zeros((N, 2))                       # reverb send
SHOTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "work", "shots")
B = 0.5; BAR = 2.0

def tt(d): return np.arange(int(d * SR)) / SR
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def put(bus, sig, t, g=1.0, pan=0.0, send=0.0):
    i = int(round(t * SR))
    if i >= N: return
    if i < 0: sig = sig[-i:]; i = 0
    if sig.ndim == 1:
        st = np.stack([sig * (1 - max(pan, 0)), sig * (1 + min(pan, 0))], 1)
    else:
        st = sig
    st = st[: N - i] * g
    BUS[bus][i:i + len(st)] += st
    if send: VERB[i:i + len(st)] += st * send

def onepole(x, k):                            # fast-ish lowpass via cumulative trick on short buffers
    y = np.empty_like(x); a = 0.0
    for i in range(len(x)): a += k * (x[i] - a); y[i] = a
    return y
def fft_lp(x, fc):                            # brick-ish lowpass in the frequency domain (fast, no loops)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / fc) ** 4); return np.fft.irfft(X, len(x))
def fft_hp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (fc / np.maximum(f, 1)) ** 4); return np.fft.irfft(X, len(x))
def fft_bp(x, lo, hi): return fft_hp(fft_lp(x, hi), lo)
def saw(f, t): return 2 * ((t * f) % 1) - 1
def env_adsr(n, a, d, s, r, total):
    t = np.arange(n) / SR; e = np.ones(n) * s
    e[t < a] = t[t < a] / a
    m = (t >= a) & (t < a + d); e[m] = 1 - (1 - s) * (t[m] - a) / d
    e[t > total - r] *= np.clip((total - t[t > total - r]) / r, 0, 1)
    return e

# ---------------- instruments ----------------
def kick():
    t = tt(0.35); f = 48 + 140 * np.exp(-t * 38)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) + rng.standard_normal(len(t)) * np.exp(-t * 400) * .35
    return np.tanh(x * 2.2)
def b808(note, dur, glide=None):
    t = tt(dur + 0.05); f = np.full(len(t), mtof(note))
    if glide is not None:
        g0 = int(max(dur - 0.09, 0) * SR); f[g0:] = np.linspace(mtof(note), mtof(glide), len(f) - g0)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    e = np.minimum(t / .004, 1) * np.exp(-t / max(dur * 0.9, .25)) * np.clip((dur + .05 - t) / .05, 0, 1)
    return np.tanh(x * e * 2.6) * 0.9
def clap():
    t = tt(0.45); n = fft_bp(rng.standard_normal(len(t)), 900, 7000)
    e = sum(np.exp(-np.maximum(t - d, 0) * 90) * (t >= d) for d in (0, .009, .019)) + np.exp(-t * 11) * .5
    body = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 30) * .4
    return (n * e * .6 + body)
def hat(open_=False, v=1.0):
    t = tt(0.3 if open_ else 0.045); n = fft_hp(rng.standard_normal(len(t)), 7000)
    return n * np.exp(-t * (10 if open_ else 95)) * .35 * v
def taiko(f0=70):
    t = tt(1.2); f = f0 * (1 + .5 * np.exp(-t * 25))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.5) + fft_lp(rng.standard_normal(len(t)), 900) * np.exp(-t * 18) * 1.4
    return np.tanh(x * 1.8)
def braam(root=45, d=2.6):
    t = tt(d); x = np.zeros(len(t))
    for m, a in ((root - 12, 1.0), (root, .9), (root + 7, .6), (root + 12, .5), (root + 19, .25)):
        for det in (-.004, 0, .004): x += saw(mtof(m) * (1 + det), t) * a
    x = fft_lp(x, 1400) * 0.25
    e = np.minimum(t / .03, 1) * np.exp(-t / 1.2)
    return np.tanh(x * e * 3.0) * .8
def impact(size=1.0):
    d = 1.5 + 2 * size; t = tt(d); f = 28 + 150 * np.exp(-t * 7)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (2.6 - 1.2 * size))
    body = fft_lp(rng.standard_normal(len(t)), 260) * np.exp(-t * (4 - 2 * size)) * 6
    crack = fft_hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 28) * .7
    return np.tanh((boom * 1.5 + body + crack) * 1.3)
def punch():
    t = tt(0.28)
    thump = np.sin(2 * np.pi * (65 + 110 * np.exp(-t * 45)) * t) * np.exp(-t * 20)
    slap = fft_bp(rng.standard_normal(len(t)), 1200, 6000) * np.exp(-t * 60)
    cloth = fft_bp(rng.standard_normal(len(t)), 300, 1500) * np.exp(-t * 18) * .3
    return np.tanh((thump * 1.4 + slap * 1.1 + cloth) * 1.6)
def breath(d=.35):
    t = tt(d); return fft_bp(rng.standard_normal(len(t)), 500, 3500) * np.minimum(t / .02, 1) * np.exp(-t / (d * .35)) * .9
def riser(d):
    t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros(len(t))
    for k in range(6):                       # stepped band sweep, cheap but convincing
        a, b = int(len(t) * k / 6), int(len(t) * (k + 1) / 6)
        out[a:b] = fft_bp(n[a:b], 300 * 2 ** k, 900 * 2 ** k)
    tone = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (t / d * 2.5)) / SR) * .25
    return (out * 1.2 + tone) * (t / d) ** 2.2
def rev_swell(d):
    t = tt(d); return fft_hp(rng.standard_normal(len(t)), 3000) * (t / d) ** 3 * .9
def whoosh(d=.5):
    t = tt(d); return fft_bp(rng.standard_normal(len(t)), 400, 3000) * np.sin(np.pi * t / d) ** 2 * 1.2
def sub_drop(d=2.5):
    t = tt(d); f = 65 * np.exp(-t * 1.1) + 22
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * .9)
def heartbeat():
    t = tt(.4); x = np.sin(2 * np.pi * (45 + 30 * np.exp(-t * 30)) * t) * np.exp(-t * 14)
    return np.tanh(x * 2)
def bell(note, d=2.5):
    t = tt(d); f = mtof(note)
    x = (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3) + .25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 6))
    return x * np.minimum(t / .003, 1) * np.exp(-t / .9) * .5
def pluck(note, d=.45):
    t = tt(d); f = mtof(note); x = saw(f, t) + saw(f * 1.003, t)
    return fft_lp(x, 2600) * np.exp(-t / .12) * .35
def pad(notes, d, bright=1800, vowel=False):
    t = tt(d); x = np.zeros(len(t))
    for m in notes:
        for det in (-.006, -.002, .002, .006): x += saw(mtof(m) * (1 + det), t)
    x = fft_lp(x, bright) / (len(notes) * 4)
    if vowel: x = fft_bp(x, 500, 1100) * 2 + fft_bp(x, 1100, 2600)   # "aah" choir colour
    return x * env_adsr(len(t), .35, .3, .85, .45, d)
def strings_ost(notes, t0, t1, g, pan=.3):
    pat = [0, 1, 2, 1, 0, 2, 1, 2]
    for k, b in enumerate(np.arange(t0, t1, .125)):
        m = notes(b)[pat[k % 8]]; t = tt(.14)
        x = (saw(mtof(m), t) + saw(mtof(m) * 1.004, t)) * np.exp(-t / .07)
        put("music", fft_lp(x, 3200) * .22, b, g, pan if k % 2 else -pan, send=.25)
def crowd(d, g=1.0):
    t = tt(d); n = rng.standard_normal((len(t), 2))
    body = np.stack([fft_bp(n[:, 0], 300, 3000), fft_bp(n[:, 1], 300, 3000)], 1)
    am = 1 + .25 * np.sin(2 * np.pi * 3.1 * t)[:, None] * np.sin(2 * np.pi * .7 * t + 1)[:, None]
    e = (np.minimum(t / .25, 1) * np.exp(-t / (d * .6)))[:, None]
    return body * am * e * g

# ================= v7: cinematic trailer score - piano ostinato, strings, choir, soft timpani (original) =================
def piano(note, d=1.4, vel=1.0):
    t = tt(d); f = mtof(note); x = np.zeros(len(t))
    for h, a in ((1, 1.0), (2, .4), (3, .18), (4, .08)):
        x += np.sin(2 * np.pi * f * h * t * (1 + .0003 * h * h)) * a * np.exp(-t * (1.1 + .8 * h))
    return x * np.minimum(t / .004, 1) * .26 * vel
def strings(notes, d, bright=2400, att=.6, vib=True):
    t = tt(d); x = np.zeros(len(t))
    for m in notes:
        for det in (-.005, -.0015, .0015, .005):
            f = mtof(m) * (1 + det) * (1 + (.003 * np.sin(2 * np.pi * 5.2 * t + det * 900) if vib else 0))
            x += 2 * ((np.cumsum(f) / SR) % 1) - 1
    x = fft_lp(x / (len(notes) * 4), bright)
    return x * env_adsr(len(t), att, .4, .9, min(.8, d * .4), d) * .5
def choir(notes, d):
    return fft_bp(strings(notes, d, 3200, att=.8), 400, 2400) * 2.2
def timp(f0=55, v=1.0):
    t = tt(1.6); f = f0 * (1 + .12 * np.exp(-t * 18))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6) + fft_lp(rng.standard_normal(len(t)), 600) * np.exp(-t * 30) * .5
    return np.tanh(x * 1.2) * .5 * v
def swell(d=2.0):
    t = tt(d); return fft_hp(rng.standard_normal(len(t)), 4000) * (t / d) ** 2.5 * .25

# original progressions (D minor -> F major lift)
PROG_A = [50, 46, 53, 48]        # Dm Bb F C
PROG_B = [46, 53, 48, 50]        # Bb F C Dm  (hopeful)
PROG_W = [46, 48, 53, 53]        # Bb C F F   (victory)
CH = {50: [50, 53, 57], 46: [46, 50, 53], 53: [53, 57, 60], 48: [48, 52, 55]}
def chord_at(prog, t0, t): return prog[int((t - t0) // BAR) % 4]

def ostinato(t0, t1, prog, p0, g=1.0, octave=12, pattern=(0, 2, 1, 2, 0, 2, 1, 2)):
    for k, b in enumerate(np.arange(t0, t1, .25)):
        r = chord_at(prog, p0, b); n = CH[r][pattern[k % 8]] + octave
        put("music", piano(n, 1.2, .8 if k % 2 else 1.0), b, g, .25 if k % 2 else -.25, send=.35)

def strings_bars(t0, t1, prog, p0, g=1.0, low=True, high=False, bright=2400):
    for b in np.arange(t0, t1, BAR):
        r = chord_at(prog, p0, b); d = min(BAR + .3, t1 - b + .3)
        put("music", strings(CH[r], d, bright), b, .7 * g, -.2, send=.45)
        if low: put("music", strings([r - 12, r - 24], d, 900, att=.4), b, .55 * g, .1, send=.3)
        if high: put("music", strings([CH[r][2] + 12, CH[r][0] + 24], d, 4200, att=.5), b, .35 * g, .3, send=.55)

def brass(notes, d, bright=1300, att=.9):
    t = tt(d); x = np.zeros(len(t))
    for m in notes:
        for det in (-.004, 0, .004):
            ph = np.cumsum(mtof(m) * (1 + det) * np.ones(len(t))) / SR
            x += 2 * (ph % 1) - 1
    sw = np.minimum(t / att, 1) ** 1.5
    x = fft_lp(x / (len(notes) * 3), bright) * sw
    return np.tanh(x * 1.8) * env_adsr(len(t), .05, .3, 1.0, min(1.0, d * .4), d) * .45
def deep_pulse(v=1.0):                      # soft, round "heartbeat" pulse - no harsh sub
    t = tt(1.4); f = 62 * (1 + .25 * np.exp(-t * 14))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2) * .45 * v

def slow_motif(t0, t1, prog, p0, g=1.0, octave=12, step=.5):
    """slow repeating piano figure: root - fifth - third - fifth (quarter notes), left-hand octave on the bar"""
    fig = (0, 2, 1, 2)
    for k, b in enumerate(np.arange(t0, t1, step)):
        r = chord_at(prog, p0, b); n = CH[r][fig[k % 4]] + octave
        put("music", piano(n, 2.2, .9), b, g, .2 if k % 2 else -.2, send=.5)
        if abs(((b - p0) / BAR) - round((b - p0) / BAR)) < 1e-6:
            put("music", piano(r - 12, 3.0, .8), b, g * .8, 0, send=.4)

# ================= ARRANGEMENT (picture-locked, same cue points) =================
# 0-4 OPEN: almost silent - slow piano figure, airy strings
slow_motif(0.0, 4.0, PROG_A, 0.0, g=.7, step=1.0)
put("music", strings([74, 77], 4.2, 3600, att=1.6), 0.0, .25, send=.65)
put("fx", swell(1.3), 2.7, .45)
# 4-12: piano figure in quarters, low strings enter, soft pulses
put("music", deep_pulse(.9), 4.0, .8, send=.3)
slow_motif(4.0, 12.0, PROG_A, 4.0, g=.8)
strings_bars(4.0, 12.0, PROG_A, 4.0, g=.75, bright=1800)
for b in np.arange(4.0, 12.0, BAR): put("music", deep_pulse(.6), b, .6, send=.3)
# 12-20: the long build - low brass swells, high strings, piano figure doubles in eighths
put("fx", swell(.9), 11.1, .45); put("music", timp(45, .8), 12.0, .8, send=.35)
slow_motif(12.0, 20.0, PROG_A, 4.0, g=.8, step=.5)
ostinato(16.0, 20.0, PROG_A, 4.0, g=.5, octave=24)
strings_bars(12.0, 20.0, PROG_A, 4.0, g=.95, high=True, bright=2800)
for b in np.arange(12.0, 20.0, BAR):
    r = chord_at(PROG_A, 4.0, b); put("music", brass([r - 12, r - 5], BAR + .3, 1100 + 60 * (b - 12)), b, .55 + .03 * (b - 12), send=.4)
    put("music", deep_pulse(.7), b, .6, send=.3); put("music", deep_pulse(.45), b + 1.0, .5, send=.3)
# 20-21 breath; 21 FROM THE RING
put("music", piano(74, 2.4), 20.0, .55, send=.65); put("fx", swell(1.0), 20.0, .35)
put("music", timp(46, .7), 21.0, .7, send=.4); put("music", strings(CH[46], 1.4, 2400), 21.0, .65, send=.5)
# 22-31 TEAM MOSHE: warm, hopeful, piano + strings
slow_motif(22.0, 31.5, PROG_B, 22.0, g=.75)
strings_bars(22.0, 32.0, PROG_B, 22.0, g=.75, bright=2200)
# 31-33 crescendo
put("music", strings([62, 65, 69, 74], 2.2, 3400, att=1.9), 31.0, .65, send=.5)
put("music", brass([50, 57, 62], 2.0, 1500, att=1.8), 31.0, .5, send=.4)
for i, b in enumerate(np.arange(31.5, 33.0, .125)): put("music", timp(50, .12 + .025 * i), b, .45)
put("fx", swell(2.0), 31.0, .5)
# 33-44 VICTORIES: the wide climax - brass, choir, full strings, piano figure up high
put("music", timp(46, 1.0), 33.0, .95, send=.4)
strings_bars(33.0, 44.0, PROG_W, 33.0, g=1.05, high=True, bright=3200)
for b in np.arange(33.0, 44.0, BAR):
    r = chord_at(PROG_W, 33.0, b); d = min(BAR + .3, 44.3 - b)
    put("music", choir(CH[r] + [CH[r][0] + 12], d), b, .7, send=.6)
    put("music", brass([r - 12, r - 5, r], d, 1700, att=.4), b, .7, send=.45)
    put("music", deep_pulse(.8), b, .6, send=.3); put("music", deep_pulse(.55), b + 1.0, .5, send=.3)
slow_motif(33.0, 43.75, PROG_W, 33.0, g=.65, octave=24, step=.5)
for ts in (33.0, 37.0, 40.5): put("fx", crowd(2.5, .3), ts, .25)
# 44-49 LOGO: final majestic chord
put("music", timp(41, .9), 44.0, .9, send=.5)
put("music", strings([53, 57, 60, 65, 69], 5.0, 2900, att=.3), 44.0, .85, send=.6)
put("music", brass([41, 48, 53, 57], 5.0, 1500, att=.3), 44.0, .6, send=.5)
put("music", choir([65, 69, 72, 77], 5.0), 44.0, .65, send=.6)
for tb, n in ((44.5, 77), (45.25, 81), (46.0, 84), (46.75, 89)): put("music", piano(n, 2.6), tb, .45, send=.65)

# ---- extend the fight section: duplicate the INS_X seconds of bars that end at INS_T ----
if INS_X > 0:
    a, x = int(INS_T * SR), int(INS_X * SR)
    for k in BUS: BUS[k] = np.concatenate([BUS[k][:a], BUS[k][a - x:a], BUS[k][a:]])
    VERB = np.concatenate([VERB[:a], VERB[a - x:a], VERB[a:]])
    N += x; DURATION += INS_X

# ---- strike sound design (real-sounding, synced to the verified hits) ----
for h in hit_times():
    put("music", deep_pulse(.5), h + OFF, .35, send=.3); put("fx", punch(), h + OFF, .12)
# arena atmosphere bed under the fights

# ---- real location sound (pads, gloves, arena) - never broadcast commentary or phone recordings ----
LOC = {"IMG_7970.mov": .5, "IMG_7991.MOV": .4, "IMG_7997.MOV": .35, "D67A6790.MP4": .3, "D67A6791.MP4": .3,
       "D67A6795.MP4": .22, "IMG_1612.MOV": .35, "IMG_1601.MOV": .3, "v29025g50000d9jo14nog65hrm6a3nq0.mp4": .45}
for i, s in enumerate(SHOTS):
    t0, dur, src, sin, speed, crop = s[:6]
    p = os.path.join(SHOTDIR, f"{i:02d}.wav")
    t0 += OFF
    if speed != 1.0 or not os.path.exists(p) or src not in LOC or t0 >= 44.0 + INS_X: continue
    if src.startswith("v29025") and t0 < 40.0 + INS_X: continue        # only the GFN crowd at the hand raise
    with wave.open(p) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, w.getnchannels()).astype(float) / 32768
    if x.shape[1] == 1: x = np.repeat(x, 2, 1)
    n = min(len(x), int(dur * SR)); x = x[:n].copy(); k = min(int(.015 * SR), n // 2)
    x[:k] *= np.linspace(0, 1, k)[:, None]; x[-k:] *= np.linspace(1, 0, k)[:, None]
    put("loc", x, t0, LOC[src])

# ================= MIX =================
# sidechain: duck music/bass under the kicks of the trap sections
kick_env = np.zeros(N)
for b in list(np.arange(4.0, 20.0 + INS_X, BAR)) + list(np.arange(33.0 + INS_X, 44.0 + INS_X, BAR)):
    for s in (0, 6, 10):
        i = int((b + s * .125) * SR)
        if i < N:
            L = min(int(.22 * SR), N - i); kick_env[i:i + L] = np.maximum(kick_env[i:i + L], np.exp(-np.arange(L) / (SR * .07)))
duck = (1 - .45 * kick_env)[:, None]
BUS["music"] *= duck
# reverb: FFT convolution with a synthetic hall impulse
ir_t = np.arange(int(2.6 * SR)) / SR
ir = rng.standard_normal((len(ir_t), 2)) * np.exp(-ir_t / .55)[:, None]
ir[:, 0] = fft_lp(ir[:, 0], 6000); ir[:, 1] = fft_lp(ir[:, 1], 6000)
L = N + len(ir_t); nfft = 1 << int(np.ceil(np.log2(L)))
wet = np.stack([np.fft.irfft(np.fft.rfft(VERB[:, c], nfft) * np.fft.rfft(ir[:, c], nfft), nfft)[:N] for c in range(2)], 1)
wet /= (np.max(np.abs(wet)) + 1e-9); wet *= np.max(np.abs(VERB)) * .6
mix = BUS["drums"] * 1.0 + BUS["bass"] * .95 + BUS["music"] * .85 + BUS["fx"] * 1.0 + BUS["loc"] * 1.0 + wet
# gentle end fade (ring-out), master glue + limiter
tl = np.arange(N) / SR
mix *= np.clip((DURATION - tl) / 1.4, 0, 1)[:, None]
# cinematic dynamics: gentle rise from the delicate opening to the triumphant peak (music time, before trimming)
_tl = np.arange(N) / SR
_pts = [(0, .34), (4.0 + 0, .46), (12.0 + INS_X, .66), (20.0 + INS_X, .78), (22.0 + INS_X, .56), (31.0 + INS_X, .62),
        (33.0 + INS_X, 1.0), (44.0 + INS_X, 1.0), (N / SR, 1.0)]
mix *= np.interp(_tl, [p[0] for p in _pts], [p[1] for p in _pts])[:, None]
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.05)
mix = mix / np.max(np.abs(mix)) * 0.93
mix = mix[int(OFF * SR):int(OFF * SR) + int(PIC_DURATION * SR)]
k = int(.12 * SR); mix[:k] *= np.linspace(0, 1, k)[:, None]
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("wrote", sys.argv[1])
