"""Import an ElevenLabs (or human) narration file, split it into sentences at the pauses, and place each sentence
at its planned moment in the promo (picture-locked to the v15 cut, 60.25 s).
usage: python3 narration_import.py input.mp3 out.wav
Script order (Or's text): 7 achievements -> "אור משה" -> "ועכשיו... לדור הבא" -> "TEAM MOSHE" -> CTA.
"""
import subprocess, sys, wave
import numpy as np

SR = 48000
DURATION = 60.25
# planned start of each sentence (seconds in the video) - each achievement lands on a strike / peak
PLAN = [
    ("אלוף משחקי העולם",                 6.40),   # World Games clip
    ("פעמיים אלוף אירופה",               10.15),  # Euro spinning kick
    ("שלוש פעמים סגן אלוף העולם",        12.15),  # GFN knee + punch on the ropes
    ("אלוף גביע העולם ואלוף גביע אירופה", 15.30), # Muay Thai -> knee in slow motion
    ("פעמיים ספורטאי השנה",              19.50),  # World GP combination
    ("18 פעמים אלוף ישראל",              21.30),  # GFN knee
    ("מעל 200 קרבות בזירה",              24.10),  # Euro attack
    ("אור משה",                          30.40),  # ringside -> hero moment
    ("ועכשיו... לדור הבא",               32.30),  # into the coaching section
    ("TEAM MOSHE",                       55.40),  # logo reveal
    ("גם אתם רוצים להיות אלופים? המקום שלכם כאן.", 57.20),
]

def load(path):
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(SR),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(float) / 32768

def split_sentences(x, n):
    """Split at the n-1 longest pauses (energy below threshold)."""
    win = int(0.02 * SR)
    e = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, "same"))
    quiet = e < max(0.01, 0.06 * np.percentile(e, 95))
    gaps, i = [], 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]: j += 1
            if i > 0 and j < len(quiet): gaps.append((j - i, i, j))
            i = j
        else:
            i += 1
    cuts = sorted(sorted(gaps, reverse=True)[: n - 1], key=lambda g: g[1])
    bounds, start = [], 0
    for _, a, b in cuts:
        bounds.append((start, a)); start = b
    bounds.append((start, len(x)))
    segs = []
    for a, b in bounds:
        s = x[a:b]; nz = np.where(np.abs(s) > 0.01)[0]
        segs.append(s[max(0, nz[0] - 480): nz[-1] + 4800] if len(nz) else s)
    return segs

def main(src, dst):
    segs = split_sentences(load(src), len(PLAN))
    track = np.zeros(int(SR * DURATION)); cursor = 0.0
    for (text, t), s in zip(PLAN, segs):
        start = max(t, cursor + 0.15)
        i0 = int(start * SR); n = min(len(s), len(track) - i0)
        track[i0:i0 + n] += s[:n]; cursor = start + len(s) / SR
        print(f"{start:6.2f}-{cursor:6.2f}  {text}")
    track = track / (np.max(np.abs(track)) + 1e-9) * 0.89
    with wave.open(dst, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((track * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
