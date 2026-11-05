"""TEAM MOSHE promo v4 - original score: cinematic sports trailer x modern trap (120 BPM, A minor).
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

PROG_FIGHT = [57, 53, 48, 55]     # Am F C G   (roots, octave 3/4 area)
PROG_COACH = [53, 48, 57, 55]     # F C Am G
PROG_WIN   = [53, 55, 57, 48]     # F G Am C  (rising, emotional)
TRIAD = {57: [57, 60, 64], 53: [53, 57, 60], 48: [48, 52, 55], 55: [55, 59, 62]}
def chord_at(prog, t0, t): return prog[int((t - t0) // BAR) % 4]

def trap_bar(t, prog_root, g=1.0, roll=False, b808_on=True, hats=True, glide_to=None):
    for s in (0, 6, 10): put("drums", kick(), t + s * .125, .85 * g)
    put("drums", clap(), t + 1.0, .65 * g, send=.18)
    if hats:
        for s in range(0, 16, 2):
            if roll and s >= 12: continue
            put("drums", hat(v=1.0 if s % 4 == 0 else .7), t + s * .125, .5 * g, .25)
        if roll:
            for k in range(8): put("drums", hat(v=.5 + .07 * k), t + 1.5 + k * .0625, .5 * g, .25)
        put("drums", hat(True), t + .75, .25 * g, -.2)
    if b808_on:
        r = prog_root - 24 if prog_root - 24 >= 28 else prog_root - 12
        put("bass", b808(r, .70), t, .9 * g)
        put("bass", b808(r, .45), t + .75, .7 * g)
        put("bass", b808(r, .55, glide=glide_to), t + 1.25, .75 * g)

# ================= ARRANGEMENT (picture-locked) =================
# 0-4 COLD OPEN: near silence -> dark bell -> heartbeat -> name -> suck-out -> DROP at 4.0
t = tt(4.0)
put("music", fft_lp(saw(55, t) + saw(55.3, t), 220) * np.minimum(t / 2.5, 1) * .35, 0.0, 1.0)
put("fx", fft_bp(rng.standard_normal(len(t)), 200, 1500) * np.minimum(t / 3, 1) * .15, 0.0, 1.0)
for tb, nt in ((0.3, 69), (1.05, 72), (1.8, 76), (2.55, 74)): put("music", bell(nt, 3.0), tb, .55, .2 if nt % 2 else -.2, send=.8)
for hb in (0.9, 1.3, 1.9, 2.3, 2.9, 3.2, 3.45, 3.65): put("fx", heartbeat(), hb, .55)
put("fx", impact(.5), 2.75, .55, send=.5)                 # OR MOSHE
put("fx", rev_swell(1.1), 2.78, .6); put("fx", riser(1.1), 2.8, .5)
# 4-20 FIGHTS
put("fx", impact(1.0), 4.0, .9, send=.3); put("music", braam(45), 4.0, .7, send=.4)
for b in np.arange(4.0, 20.0, BAR):
    r = chord_at(PROG_FIGHT, 4.0, b); nxt = chord_at(PROG_FIGHT, 4.0, b + BAR)
    if abs(b - 10.0) < 1e-6:                                # bar before the switch-up: stop on the last beat
        trap_bar(b, r, roll=False); continue
    trap_bar(b, r, roll=(int((b - 4) / BAR) % 2 == 1), glide_to=(nxt - 24 if nxt - 24 >= 28 else nxt - 12))
    put("music", pad(TRIAD[r], BAR, 1200), b, .5, send=.3)
# switch-up: everything cuts at 11.75 -> reverse -> re-hit at 12.0 with strings
BUS["drums"][int(11.75 * SR):int(12.0 * SR)] *= 0.0; BUS["bass"][int(11.75 * SR):int(12.0 * SR)] *= 0.0
put("fx", rev_swell(.5), 11.5, .7)
put("fx", impact(.8), 12.0, .75); put("music", braam(41), 12.0, .6, send=.4)
strings_ost(lambda tb: TRIAD[chord_at(PROG_FIGHT, 4.0, tb)], 12.0, 20.0, .9)
# 20-21 slow-motion exchange: half-time, filtered
put("drums", kick(), 20.0, .8); put("drums", clap(), 20.5, .4, send=.5)
put("bass", b808(33, 1.0), 20.0, .8); put("fx", riser(1.0), 20.0, .55)
# 21-22 FROM THE RING
put("fx", impact(.8), 21.0, .8, send=.4); put("music", braam(45, 2.0), 21.0, .45, send=.5)
put("music", bell(76, 2.0), 21.0, .5, send=.7); put("music", bell(69, 2.0), 21.5, .4, send=.7)
# 22-31 TEAM MOSHE: lighter, warm, melodic
for b in np.arange(22.0, 32.0, BAR):
    r = chord_at(PROG_COACH, 22.0, b)
    if b < 31.0:
        for s in (0, 10): put("drums", kick(), b + s * .125, .7)
        put("drums", clap(), b + 1.0, .5, send=.25)
        for s in range(0, 16, 2): put("drums", hat(v=.8), b + s * .125, .35, .25)
        put("bass", b808(r - 24 if r - 24 >= 28 else r - 12, 1.2), b, .65)
    put("music", pad(TRIAD[r] + [TRIAD[r][0] + 12], BAR, 2200), b, .55, send=.35)
    for k, m in enumerate([0, 1, 2, 1, 2, 0, 2, 1]):
        put("music", pluck(TRIAD[r][m] + 12), b + k * .25, .5, .4 if k % 2 else -.4, send=.3)
# 31-33 build: snare roll + strings + riser + taiko -> silence -> VICTORY
for i, b in enumerate(np.arange(31.0, 32.0, .125)): put("drums", clap(), b, .15 + .04 * i)
for i, b in enumerate(np.arange(32.0, 32.875, .0625)): put("drums", clap(), b, .35 + .02 * i)
strings_ost(lambda tb: [57, 60, 64], 31.0, 32.875, 1.0)
for b in (32.0, 32.5): put("drums", taiko(65), b, .8, send=.3)
put("fx", riser(1.9), 31.0, .7); put("fx", rev_swell(.9), 32.0, .6)
# 33-44 VICTORIES: the emotional peak
melody = [(0, 76), (.5, 74), (1.0, 72), (1.5, 74), (2.0, 76), (2.5, 79), (3.0, 81), (4.0, 79), (4.5, 77), (5.0, 76),
          (6.0, 72), (6.5, 74), (7.0, 76), (7.5, 79), (8.0, 81), (9.0, 84)]
put("fx", impact(1.0), 33.0, .9, send=.4); put("music", braam(41), 33.0, .7, send=.5)
for b in np.arange(33.0, 44.0, BAR):
    r = chord_at(PROG_WIN, 33.0, b); nxt = chord_at(PROG_WIN, 33.0, b + BAR)
    dur = min(BAR, 44.0 - b)
    trap_bar(b, r, g=1.0, roll=True, glide_to=(nxt - 24 if nxt - 24 >= 28 else nxt - 12))
    put("music", pad(TRIAD[r] + [TRIAD[r][0] + 12], dur, 2600, vowel=True), b, .9, send=.5)
    put("music", pad([TRIAD[r][0] - 12, TRIAD[r][0]], dur, 900), b, .5, send=.3)
    for s in (0, 1.0): put("drums", taiko(62), b + s, .6, send=.35)
strings_ost(lambda tb: TRIAD[chord_at(PROG_WIN, 33.0, tb)], 33.0, 43.75, 1.0)
for off, m in melody:
    if 33.0 + off < 43.6: put("music", bell(m, 1.6), 33.0 + off, .55, send=.6)
for ts, g in ((33.0, .5), (34.0, .55), (35.5, .6), (37.0, .65), (38.5, .7), (40.5, 1.0)):
    put("fx", crowd(2.2 if ts < 40 else 3.5, g), ts, .6)
put("fx", impact(1.0), 40.5, .8, send=.4); put("music", braam(48), 40.5, .5, send=.5)
BUS["drums"][int(43.75 * SR):int(44.0 * SR)] *= 0.0; BUS["bass"][int(43.75 * SR):int(44.0 * SR)] *= 0.0
put("fx", rev_swell(.6), 43.4, .7)
# 44-49 LOGO: the biggest hit, then a clean ring-out
put("fx", impact(1.0), 44.0, 1.0, send=.5); put("fx", impact(.7), 44.0, .6)
put("music", braam(45, 4.0), 44.0, .9, send=.6); put("bass", sub_drop(3.0), 44.0, .8)
put("music", pad([45, 57, 60, 64, 69], 5.0, 1600, vowel=True), 44.0, .8, send=.6)
put("music", bell(81, 3.0), 45.0, .45, send=.8); put("music", bell(76, 3.0), 45.5, .35, send=.8)
put("fx", whoosh(.9), 46.9, .35)

# ---- extend the fight section: duplicate the INS_X seconds of bars that end at INS_T ----
if INS_X > 0:
    a, x = int(INS_T * SR), int(INS_X * SR)
    for k in BUS: BUS[k] = np.concatenate([BUS[k][:a], BUS[k][a - x:a], BUS[k][a:]])
    VERB = np.concatenate([VERB[:a], VERB[a - x:a], VERB[a:]])
    N += x; DURATION += INS_X

# ---- strike sound design (real-sounding, synced to the verified hits) ----
for h in hit_times():
    put("fx", punch(), h + OFF, .8); put("fx", breath(), h + OFF - .05, .35)
# arena atmosphere bed under the fights
t = tt(16.0 + INS_X); put("fx", np.stack([fft_bp(rng.standard_normal(len(t)), 250, 2500)] * 2, 1) * .06, 4.0, 1.0)

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
mix = np.tanh(mix / np.percentile(np.abs(mix), 99.7) * 1.15)
mix = mix / np.max(np.abs(mix)) * 0.93
mix = mix[int(OFF * SR):int(OFF * SR) + int(PIC_DURATION * SR)]
k = int(.12 * SR); mix[:k] *= np.linspace(0, 1, k)[:, None]
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("wrote", sys.argv[1])
