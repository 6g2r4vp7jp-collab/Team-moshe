"""TEAM MOSHE promo v6 - original score (bright upbeat commercial pop): cinematic sports trailer x modern trap (120 BPM, A minor).
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

# ================= v6: bright, upbeat commercial pop (piano, catchy synth hook, claps) - no tension =================
def piano(note, d=1.2):
    t = tt(d); f = mtof(note); x = np.zeros(len(t))
    for h, a in ((1, 1.0), (2, .45), (3, .22), (4, .12), (5, .06)):
        x += np.sin(2 * np.pi * f * h * t * (1 + .0004 * h * h)) * a * np.exp(-t * (1.6 + .9 * h))
    x += fft_bp(rng.standard_normal(len(t)), 1500, 6000) * np.exp(-t * 120) * .08
    return x * np.minimum(t / .003, 1) * .28
def lead(note, d=.25):
    t = tt(d + .12); f = mtof(note); x = np.zeros(len(t))
    for det in (-.008, -.003, 0, .003, .008): x += saw(f * (1 + det), t)
    x = fft_lp(x / 5, 4200) + .25 * np.sin(2 * np.pi * f * 2 * t)
    return x * np.minimum(t / .004, 1) * np.exp(-t / (d * .9 + .05)) * .3
def snap():
    t = tt(.08); return fft_bp(rng.standard_normal(len(t)), 2000, 9000) * np.exp(-t * 70) * .35
def crash(d=1.6):
    t = tt(d); return fft_hp(rng.standard_normal(len(t)), 5000) * np.exp(-t * 2.2) * .22
def pop_bass(note, d=.22):
    t = tt(d); x = np.sin(2 * np.pi * mtof(note) * t) + .35 * np.sin(4 * np.pi * mtof(note) * t)
    return np.tanh(x * 1.4) * np.minimum(t / .004, 1) * np.exp(-t / .16) * .75

PROG_POP = [48, 55, 57, 53]       # C G Am F   (I V vi IV - the classic uplifting pop progression)
PROG_WIN = [53, 55, 48, 48]       # F G C C    (lift into the chorus)
TRIAD = {57: [57, 60, 64], 53: [53, 57, 60], 48: [48, 52, 55], 55: [55, 59, 62]}
def chord_at(prog, t0, t): return prog[int((t - t0) // BAR) % 4]
HOOK_A = [76, 79, 81, 79, 76, 74, 72, 74,  76, 79, 84, 83, 81, 79, 76, None]
HOOK_B = [72, 74, 76, 79, 81, 79, 76, 74,  72, 74, 76, 74, 72, None, 72, None]

def beat_bar(t, root, g=1.0, full=True):
    for k in range(4): put("drums", kick(), t + k * B, .7 * g)
    for k in (1, 3): put("drums", clap(), t + k * B, .55 * g, send=.2); put("drums", snap(), t + k * B + .01, .4 * g, .3)
    for k in range(8): put("drums", hat(k % 2 == 1, .7), t + k * .25, (.28 if k % 2 else .2) * g, .2)
    r = root - 24 if root - 24 >= 28 else root - 12
    for k in range(4):
        put("bass", pop_bass(r), t + k * B, .55 * g)
        if full: put("bass", pop_bass(r + 12, .14), t + k * B + .25, .3 * g)

def piano_bar(t, root, g=1.0, dur=BAR):
    ch = TRIAD[root]
    for k, off in enumerate((0, .75, 1.0, 1.5)):              # bouncy pop comping
        if off < dur:
            for m in ch: put("music", piano(m + 12, .9), t + off, .55 * g, -.15 if k % 2 else .15, send=.25)
    put("music", piano(ch[0], 1.8), t, .6 * g, send=.2)

def hook(t0, t1, seq, g=.8, octave=0):
    k = 0; b = t0
    while b < t1 - 1e-6:
        ph = seq[(k // 16) % len(seq)]; n = ph[k % 16]
        if n is not None and b < t1 - .1:
            nxt = ph[(k + 1) % 16]; d = .22 if nxt is not None else .45
            put("music", lead(n + octave, d), b, g, .1, send=.35)
        k += 1; b += .25

# ================= ARRANGEMENT (picture-locked, same cue points) =================
# 0-4 OPEN: warm piano intro, soft swell, light build -> beat drops at 4.0
for k, (tb, r) in enumerate(((0.0, 48), (1.0, 55), (2.0, 57), (3.0, 53))):
    for j, m in enumerate(TRIAD[r] + [TRIAD[r][0] + 12]): put("music", piano(m + 12, 1.4), tb + j * .125, .5, send=.4)
    put("music", piano(r, 2.0), tb, .5, send=.3)
put("music", pad([60, 64, 67], 4.0, 2400), 0.0, .35, send=.4)
for i, tb in enumerate(np.arange(3.0, 4.0, .125)): put("drums", snap(), tb, .15 + .04 * i)
put("fx", riser(1.2), 2.8, .3)
# 4-20 FIGHTS: full upbeat groove + catchy hook
put("drums", crash(), 4.0, .7)
for b in np.arange(4.0, 20.0, BAR):
    r = chord_at(PROG_POP, 4.0, b); beat_bar(b, r); piano_bar(b, r, .8)
    put("music", pad(TRIAD[r], BAR, 2600), b, .3, send=.3)
hook(4.0, 11.75, [HOOK_A, HOOK_B])
BUS["drums"][int(11.75 * SR):int(12.0 * SR)] *= 0.0; BUS["bass"][int(11.75 * SR):int(12.0 * SR)] *= 0.0
put("drums", crash(), 12.0, .6)
hook(12.0, 20.0, [HOOK_B, HOOK_A], g=.75, octave=12)
# 20-21 short breath
put("music", piano(72, 1.0), 20.0, .5, send=.4); put("drums", snap(), 20.5, .4); put("fx", riser(1.0), 20.0, .3)
# 21-22 FROM THE RING
put("drums", crash(), 21.0, .5); put("drums", kick(), 21.0, .6); piano_bar(21.0, 53, .8, dur=1.0)
# 22-31 TEAM MOSHE: lighter, happy, family-friendly
for b in np.arange(22.0, 32.0, BAR):
    r = chord_at(PROG_POP, 22.0, b)
    if b < 31.0: beat_bar(b, r, g=.7, full=False)
    piano_bar(b, r, .9)
    for k, m in enumerate([0, 1, 2, 1, 2, 0, 2, 1]):
        put("music", pluck(TRIAD[r][m] + 24), b + k * .25, .35, .4 if k % 2 else -.4, send=.3)
hook(26.0, 31.0, [HOOK_A], g=.55)
# 31-33 build into the chorus
for i, b in enumerate(np.arange(31.0, 32.875, .125)): put("drums", clap(), b, .12 + .025 * i)
put("fx", riser(1.9), 31.0, .35)
# 33-44 VICTORIES: the chorus - biggest, brightest, hook up an octave
put("drums", crash(2.2), 33.0, .8)
for b in np.arange(33.0, 44.0, BAR):
    r = chord_at(PROG_WIN, 33.0, b); dur = min(BAR, 44.0 - b)
    beat_bar(b, r, g=1.0); piano_bar(b, r, 1.0, dur=dur)
    put("music", pad(TRIAD[r] + [TRIAD[r][0] + 12], dur, 3200, vowel=True), b, .6, send=.5)
hook(33.0, 43.75, [HOOK_A, HOOK_B], g=.8, octave=12)
for ts in (33.0, 37.0, 40.5): put("fx", crowd(2.5, .5), ts, .35)
BUS["drums"][int(43.75 * SR):int(44.0 * SR)] *= 0.0; BUS["bass"][int(43.75 * SR):int(44.0 * SR)] *= 0.0
# 44-49 LOGO: bright final chord, piano sparkle
put("drums", crash(2.5), 44.0, .8); put("drums", kick(), 44.0, .7)
for m in (48, 60, 64, 67, 72): put("music", piano(m, 3.5), 44.0, .6, send=.5)
put("music", pad([60, 64, 67, 72], 5.0, 2600, vowel=True), 44.0, .6, send=.6)
for tb, n in ((44.75, 84), (45.0, 88), (45.25, 91), (45.5, 96)): put("music", piano(n, 1.5), tb, .35, send=.6)

# ---- extend the fight section: duplicate the INS_X seconds of bars that end at INS_T ----
if INS_X > 0:
    a, x = int(INS_T * SR), int(INS_X * SR)
    for k in BUS: BUS[k] = np.concatenate([BUS[k][:a], BUS[k][a - x:a], BUS[k][a:]])
    VERB = np.concatenate([VERB[:a], VERB[a - x:a], VERB[a:]])
    N += x; DURATION += INS_X

# ---- strike sound design (real-sounding, synced to the verified hits) ----
for h in hit_times():
    put("fx", punch(), h + OFF, .3)
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
mix = np.tanh(mix / np.percentile(np.abs(mix), 99.7) * 1.15)
mix = mix / np.max(np.abs(mix)) * 0.93
mix = mix[int(OFF * SR):int(OFF * SR) + int(PIC_DURATION * SR)]
k = int(.12 * SR); mix[:k] *= np.linspace(0, 1, k)[:, None]
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("wrote", sys.argv[1])
