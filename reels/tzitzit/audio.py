# Synthesizes the soundtrack (music + sound effects) for scene.html. usage: python3 audio.py out.wav
import sys, wave, numpy as np
SR = 44100; DUR = 28.5; N = int(SR * DUR)
rng = np.random.default_rng(7)
mix = np.zeros((N, 2))
def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR); sig = sig[: max(0, N - i)]
    mix[i:i + len(sig), 0] += sig * gain * (1 - max(0, pan)); mix[i:i + len(sig), 1] += sig * gain * (1 + min(0, pan))
def tt(d): return np.arange(int(d * SR)) / SR
def env(d, a=0.005, r=None):
    t = tt(d); e = np.minimum(1, t / a); return e * (np.exp(-t / r) if r else np.ones_like(t))
def lp(x, k):  # one-pole low-pass, k in (0,1]
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += k * (v - acc); y[i] = acc
    return y
def noise(d): return rng.uniform(-1, 1, int(d * SR))
def hz(n): return 440 * 2 ** ((n - 69) / 12)

# --- instruments ---
def kick():
    t = tt(.35); f = 45 + 90 * np.exp(-t * 30); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
def snare():
    t = tt(.22); return (noise(.22) * .7 + np.sin(2 * np.pi * 190 * t) * .5) * np.exp(-t * 18)
def hat(): x = noise(.06); return (x - lp(x, .3)) * np.exp(-tt(.06) * 60)
def bass(n, d):
    t = tt(d); ph = (hz(n) * t) % 1; return lp(2 * ph - 1, .08) * env(d, .005, d * .6) * 1.4
def lead(n, d):
    t = tt(d); f = hz(n) * (1 + .006 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t * 4))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + .45 * np.sin(3 * ph) + .25 * np.sin(5 * ph) + .12 * np.sin(7 * ph)
    return s * env(d, .02, None) * np.minimum(1, (d - t) / .04) * .35

# Freygish on E: E F G# A B C D
SC = [64, 65, 68, 69, 71, 72, 74, 76, 77, 80]
MEL = [0, 2, 3, 4, 3, 2, 1, 0, 2, 4, 5, 4, 3, 2, 3, 1, 0, 1, 2, 3, 4, 5, 7, 5, 4, 3, 2, 1, 2, 1, 0, 0]
def music(t0, t1, bpm, gain, drive=False):
    b = 60 / bpm; k = 0; t = t0
    while t < t1 - 1e-6:
        beat = k % 4
        add(kick(), t, .9 * gain)
        if beat in (1, 3): add(snare(), t, .55 * gain)
        add(hat(), t + b / 2, .35 * gain, .3)
        if drive: add(hat(), t, .25 * gain, -.3)
        root = 40 if (k // 4) % 2 == 0 else 41
        add(bass(root, b * .45), t, .5 * gain); add(bass(root + 12, b * .4), t + b / 2, .4 * gain)
        for h in range(2):
            n = SC[MEL[(2 * k + h) % len(MEL)]] + (12 if drive and (k // 8) % 2 else 0)
            add(lead(n, b / 2 * .95), t + h * b / 2, .55 * gain, -.15)
        t += b; k += 1

music(0.0, 5.2, 132, .8)
music(18.5, 25.7, 140, .9, drive=True)

# --- sfx ---
def whoosh(d, f0=300, f1=2500):
    x = noise(d); t = tt(d); k = np.interp(t, [0, d], [f0, f1]) / SR * 6
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += k[i] * (v - acc); y[i] = acc
    return y * np.sin(np.pi * t / d) * 3
def clang():
    t = tt(1.6); s = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dcy) for f, dcy in [(523, 2.5), (1187, 3), (1693, 4), (2410, 5), (3305, 7)])
    return s * .35 + noise(1.6) * np.exp(-t * 40) * .6
def boom():
    t = tt(1.0); f = 30 + 80 * np.exp(-t * 8); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.5) + lp(noise(1.0), .05) * np.exp(-t * 5) * 2
def ding(f=1568):
    t = tt(1.8); return (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 2.2) * .5
def pop():
    t = tt(.12); f = 400 + 900 * t / .12; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)
def choir(d):
    t = tt(d); s = 0
    for n in [64, 68, 71, 76, 80]:
        for det in (-.15, 0, .15):
            f = hz(n + det); ph = 2 * np.pi * np.cumsum(f * (1 + .004 * np.sin(2 * np.pi * 5 * t + n))) / SR
            s = s + np.sin(ph) + .3 * np.sin(2 * ph)
    return s / 15 * np.minimum(1, t / .8) * np.minimum(1, (d - t) / .8)
def scratch():
    t = tt(.35); f = 900 * np.exp(-t * 6) * (1 + .5 * np.sin(2 * np.pi * 18 * t))
    return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .25 * np.exp(-t * 4) + lp(noise(.35), .2) * .4
def hum(d, wobble):
    t = tt(d); f = 210 + 8 * np.sin(2 * np.pi * wobble * t)
    ph = 2 * np.pi * np.cumsum(f) / SR; return (np.sin(ph) + .3 * np.sin(2 * ph)) * .06 * np.minimum(1, t / .3) * np.minimum(1, (d - t) / .1)
def thud(): t = tt(.4); return lp(noise(.4), .04) * np.exp(-t * 12) * 3 + np.sin(2 * np.pi * 60 * t) * np.exp(-t * 14)
def tinkle(d):
    out = np.zeros(int(d * SR))
    for k in range(int(d / .18)):
        s = ding(2000 + 600 * (k % 4))[: int(.4 * SR)] * .5; i = int(k * .18 * SR); out[i:i + len(s)] += s[: len(out) - i]
    return out
def skid(d): t = tt(d); x = noise(d); return (x - lp(x, .15)) * np.minimum(1, t / .05) * np.exp(-t * 1.8) * .7

add(hum(4.5, 3), 0, 1.0)
add(thud(), 4.5, .9); add(clang()[: int(.3 * SR)] * .3, 4.5, .5)
add(whoosh(.7, 200, 1500), 4.5, .5)
add(scratch(), 5.0, .8)
add(clang(), 5.2, 1.0); add(boom(), 5.2, .9)
add(pop(), 5.2, .4)
add(thud(), 5.85, .6)
add(tinkle(2.5), 6.0, .25, .2)
add(pop(), 9.05, .5)
add(choir(5.0), 9.9, .6); add(ding(), 10.0, .8); add(ding(2093), 10.3, .5, .3)
add(pop(), 11.05, .6)
add(whoosh(.5, 400, 3000), 14.95, .6)
add(pop(), 15.05, .6)
add(thud() * .4, 16.4, .5, .8); add(clang()[: int(.5 * SR)] * .3, 16.42, .3, .8)
add(hum(7.0, 4), 18.5, 1.2)
add(whoosh(.4, 300, 1500), 18.8, .4)
add(whoosh(1.4, 300, 2600), 21.5, .6)
add(thud(), 22.9, .8)
add(skid(1.2), 24.5, .9)
# outro stinger
for n in [52, 64, 68, 71, 76]: add(lead(n, 2.4) * env(2.4, .01, 1.2), 25.7, .5)
add(kick(), 25.7, 1.0); add(ding(1318), 25.75, .6)

# --- voice (voice.wav = cleaned recording) ---
# line 1 "אוי שכויחה, זה השריון שלי" ; line 2 "זרוק את הקסדה..." (pause between its parts shortened)
vw = wave.open('voice.wav'); vx = np.frombuffer(vw.readframes(vw.getnframes()), '<i2') / 32768
def clip(a, b):
    c = vx[int(a * SR):int(b * SR)].copy(); f = int(.015 * SR); c[:f] *= np.linspace(0, 1, f); c[-f:] *= np.linspace(1, 0, f); return c
L1 = clip(0.10, 2.80)
L2 = np.concatenate([clip(3.55, 4.05), np.zeros(int(.2 * SR)), clip(5.05, 7.60)])
voice = np.zeros(N)
for sig, t in [(L1, 11.15), (L2, 15.15)]: i = int(t * SR); voice[i:i + len(sig)] += sig
# mouth envelope for the animation, one value per 1/30 s
fr = SR // 30; envv = np.array([np.sqrt(np.mean(voice[i:i + fr] ** 2)) for i in range(0, N, fr)])
envv = np.clip(envv / (np.percentile(envv[envv > .01], 90) + 1e-9), 0, 1)
open('voice.js', 'w').write('window.VOICE=[' + ','.join(f'{v:.2f}' for v in envv) + '];\n')
mix *= 0.55 / np.max(np.abs(mix))
mix += voice[:, None] * 1.0

mix /= np.max(np.abs(mix)) / 0.89
fade = np.minimum(1, (DUR - np.arange(N) / SR) / 0.8); mix *= fade[:, None]
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype('<i2').tobytes())
