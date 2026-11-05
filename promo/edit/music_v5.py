"""TEAM MOSHE promo v5 - original score (upbeat Muay Thai fusion): cinematic sports trailer x modern trap (120 BPM, A minor).
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

# ================= v5: upbeat Muay Thai fusion (Thai pi melody, ching, klong + modern dance groove) =================
def ching(closed=False):
    t = tt(0.06 if closed else 0.5); x = np.zeros(len(t))
    for f, a in ((3150, 1.0), (4720, .7), (6280, .5), (8900, .35), (11800, .2)):
        x += np.sin(2 * np.pi * f * t + rng.random() * 6.28) * a
    return x * np.exp(-t * (90 if closed else 7)) * (.22 if closed else .3)
def klong(low=True):
    t = tt(0.4); f0 = 95 if low else 180
    body = np.sin(2 * np.pi * np.cumsum(f0 * (1 + .35 * np.exp(-t * 30))) / SR) * np.exp(-t * (9 if low else 16))
    slap = fft_bp(rng.standard_normal(len(t)), 700, 3500) * np.exp(-t * 60) * (.25 if low else .5)
    return np.tanh((body + slap) * 1.6) * .8
def pi_note(note, d):
    t = tt(d); f = mtof(note) * (1 + .006 * np.sin(2 * np.pi * 5.6 * t) * np.minimum(t / .15, 1))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sign(np.sin(ph)) * .45 + np.sin(2 * ph) * .35 + np.sin(3 * ph) * .25
    x = fft_bp(x, 500, 4200)
    return x * env_adsr(len(t), .02, .08, .8, .06, d) * .32
def bass_pump(note, d=.24):
    t = tt(d); x = np.tanh(np.sin(2 * np.pi * mtof(note) * t) * 2.2 + .3 * saw(mtof(note), t))
    return x * np.minimum(t / .004, 1) * np.exp(-t / .12) * .8

PROG_UP  = [48, 55, 57, 53]       # C G Am F   (bright, uplifting)
PROG_WIN = [53, 55, 48, 57]       # F G C Am   (rising, emotional)
TRIAD = {57: [57, 60, 64], 53: [53, 57, 60], 48: [48, 52, 55], 55: [55, 59, 62]}
def chord_at(prog, t0, t): return prog[int((t - t0) // BAR) % 4]
# Thai pi phrases (C major pentatonic), eighth-note grid; None = rest
PHRASE_A = [76, 79, 81, 79, 76, 74, 72, 74,  76, 74, 72, 69, 72, None, 74, 76]
PHRASE_B = [81, 84, 81, 79, 76, 79, 81, None, 79, 76, 74, 76, 72, 74, 72, None]

def groove_bar(t, root, g=1.0, full=True, fill=False):
    for k in range(4): put("drums", kick(), t + k * B, .8 * g)                      # four on the floor
    for k in (1, 3): put("drums", clap(), t + k * B, .55 * g, send=.15)
    for k in range(4):
        put("drums", hat(True, .8), t + k * B + .25, .3 * g, .25)                    # offbeat open hat
        put("drums", ching(closed=True), t + k * B, .55 * g, -.3)                    # "chap" on the beat
        put("drums", ching(), t + k * B + .25, .45 * g, .3)                          # "ching" off the beat
    if full:
        for k, (o, low) in enumerate(((0, 1), (.375, 0), (.75, 0), (1.0, 1), (1.375, 0), (1.625, 0), (1.75, 1))):
            put("drums", klong(bool(low)), t + o, .4 * g, .15 if low else -.15)
    if fill:
        for k in range(8): put("drums", klong(k % 2 == 0), t + 1.5 + k * .0625, (.25 + .05 * k) * g)
    r = root - 24 if root - 24 >= 28 else root - 12
    for k in range(4):
        put("bass", bass_pump(r), t + k * B + .25, .7 * g)
        put("bass", bass_pump(r + 12, .16), t + k * B + .375, .35 * g)

def melody(t0, t1, phrase_seq, g=.9, octave=0):
    k = 0; b = t0
    while b < t1 - 1e-6:
        ph = phrase_seq[(k // 16) % len(phrase_seq)]; n = ph[k % 16]
        if n is not None and b < t1 - .1:
            nxt = ph[(k + 1) % 16]; d = .25 if nxt is not None else .5
            put("music", pi_note(n + octave, min(d, t1 - b)), b, g, .1, send=.3)
        k += 1; b += .25

# ================= ARRANGEMENT (picture-locked, same cue points as before) =================
# 0-4 OPEN: "wai kru" feel - slow pi solo over a drone, ching marking time, klong build -> DROP at 4.0
t = tt(4.0)
put("music", fft_lp(saw(mtof(36), t) + saw(mtof(43) * 1.002, t), 400) * np.minimum(t / 1.5, 1) * .3, 0.0, 1.0)
for tb, n, d in ((0.25, 72, .6), (0.9, 74, .4), (1.3, 76, .9), (2.25, 79, .45), (2.7, 76, .3), (3.0, 74, .35)):
    put("music", pi_note(n, d), tb, .9, 0, send=.6)
for tb in np.arange(0.5, 3.5, 1.0): put("drums", ching(), tb, .45, .2, send=.4)
for i, tb in enumerate(np.arange(3.0, 4.0, .125)): put("drums", klong(i % 2 == 0), tb, .25 + .06 * i)
put("fx", impact(.5), 2.75, .5, send=.5); put("fx", riser(1.2), 2.8, .45)
# 4-20 FIGHTS: full groove + pi hook
put("fx", impact(1.0), 4.0, .85, send=.3)
for b in np.arange(4.0, 20.0, BAR):
    r = chord_at(PROG_UP, 4.0, b)
    groove_bar(b, r, fill=(abs(b - 10.0) < 1e-6 or abs(b - 18.0) < 1e-6))
    put("music", pad(TRIAD[r], BAR, 1600), b, .4, send=.3)
melody(4.0, 11.75, [PHRASE_A, PHRASE_B])
# switch-up: stop at 11.75 -> hit at 12.0 -> hook an octave up
BUS["drums"][int(11.75 * SR):int(12.0 * SR)] *= 0.0; BUS["bass"][int(11.75 * SR):int(12.0 * SR)] *= 0.0
BUS["music"][int(11.75 * SR):int(12.0 * SR)] *= 0.0
put("fx", rev_swell(.5), 11.5, .6); put("fx", impact(.8), 12.0, .7)
melody(12.0, 20.0, [PHRASE_B, PHRASE_A], g=.8, octave=12)
# 20-21 half-time breath
put("drums", kick(), 20.0, .8); put("drums", clap(), 20.5, .4, send=.5); put("drums", ching(), 20.25, .5)
put("bass", bass_pump(36, .9), 20.0, .7); put("fx", riser(1.0), 20.0, .5)
# 21-22 FROM THE RING
put("fx", impact(.8), 21.0, .75, send=.4); put("music", pi_note(84, 1.0), 21.0, .7, send=.6)
# 22-31 TEAM MOSHE: bright, bouncy, family-friendly
for b in np.arange(22.0, 32.0, BAR):
    r = chord_at(PROG_UP, 22.0, b)
    if b < 31.0: groove_bar(b, r, g=.75, full=False)
    put("music", pad(TRIAD[r] + [TRIAD[r][0] + 12], BAR, 2600), b, .5, send=.35)
    for k, m in enumerate([0, 1, 2, 1, 2, 0, 2, 1]):
        put("music", pluck(TRIAD[r][m] + 12), b + k * .25, .45, .4 if k % 2 else -.4, send=.3)
melody(26.0, 31.0, [PHRASE_A], g=.6)
# 31-33 build: klong roll + riser -> VICTORY
for i, b in enumerate(np.arange(31.0, 32.875, .125)): put("drums", klong(i % 2 == 0), b, .2 + .03 * i)
for i, b in enumerate(np.arange(32.0, 32.875, .0625)): put("drums", ching(closed=True), b, .3 + .02 * i)
put("fx", riser(1.9), 31.0, .65); put("fx", rev_swell(.9), 32.0, .55)
# 33-44 VICTORIES: the peak - full groove, big major chords, hook up high, crowd
put("fx", impact(1.0), 33.0, .85, send=.4)
for b in np.arange(33.0, 44.0, BAR):
    r = chord_at(PROG_WIN, 33.0, b); dur = min(BAR, 44.0 - b)
    groove_bar(b, r, g=1.0, fill=(abs(b - 41.0) < 1e-6))
    put("music", pad(TRIAD[r] + [TRIAD[r][0] + 12], dur, 3000, vowel=True), b, .8, send=.5)
melody(33.0, 43.75, [PHRASE_A, PHRASE_B], g=.85, octave=12)
for ts, g in ((33.0, .5), (35.0, .55), (37.0, .6), (39.0, .65), (40.5, .9)):
    put("fx", crowd(2.2 if ts < 40 else 3.5, g), ts, .55)
BUS["drums"][int(43.75 * SR):int(44.0 * SR)] *= 0.0; BUS["bass"][int(43.75 * SR):int(44.0 * SR)] *= 0.0
put("fx", rev_swell(.6), 43.4, .6)
# 44-49 LOGO: big hit, bright chord ring-out, last pi phrase
put("fx", impact(1.0), 44.0, .95, send=.5)
put("music", pad([48, 60, 64, 67, 72], 5.0, 2200, vowel=True), 44.0, .8, send=.6)
put("bass", bass_pump(36, 1.5), 44.0, .7)
for tb, n, d in ((44.5, 84, .4), (45.0, 81, .4), (45.5, 79, .5), (46.1, 84, 1.2)): put("music", pi_note(n, d), tb, .7, send=.6)
for tb in (44.0, 45.0, 46.0): put("drums", ching(), tb, .5, send=.5)

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
