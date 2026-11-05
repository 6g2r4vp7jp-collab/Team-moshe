"""Or's own voice-over: clean + sharpen the recordings, cut them into lines at the pauses, and place every line
exactly on its gold caption (v15 picture, 60.25 s).
usage: python3 vo_own.py rec_full.m4a rec_first.m4a out.wav
  rec_full  = second recording (all captions up to the honor roll)
  rec_first = first recording (used for the closing "טים משה ... בואו להיות חלק ממשפחת טים משה")
"""
import subprocess, sys, wave
import numpy as np

SR = 48000
DURATION = 60.25

# (recording, start, end, caption time, tempo, text)  - segment times found from the pauses
LINES = [
    ("full",  1.02,  1.67,  0.70, 1.00, "אור משה"),
    ("full",  2.28,  3.58,  6.45, 1.00, "אלוף משחקי העולם"),
    ("full",  4.14,  5.63,  8.70, 1.00, "מעל מאתיים קרבות זירה"),
    ("full",  6.23,  8.51, 13.75, 1.00, "אלופים לא נולדים... הם נבנים"),
    ("full",  9.13, 10.31, 24.20, 1.00, "פעמיים אלוף אירופה"),
    ("full", 10.91, 12.53, 29.70, 1.00, "גם אתם חולמים להיות אלופים?"),
    ("full", 13.15, 14.44, 32.30, 1.00, "מהזירה... לדור הבא"),
    ("full", 15.10, 16.83, 38.05, 1.00, "כל אלוף התחיל מצעד ראשון"),
    ("full", 17.43, 18.66, 41.30, 1.00, "כאן מגדלים אלופים"),
    # honor roll - read back-to-back, a touch quicker so it tracks the captions
    ("full", 19.21, 20.50, 44.35, 1.08, "אלוף אירופה פעמיים"),
    ("full", 20.86, 22.14, 45.35, 1.08, "אלוף משחקי העולם"),
    ("full", 22.61, 23.80, 46.60, 1.08, "אלוף גביע העולם"),
    ("full", 24.19, 25.36, 47.60, 1.08, "אלוף גביע אירופה"),
    ("full", 25.88, 27.75, 48.85, 1.08, "שלוש פעמים סגן אלוף העולם"),
    ("full", 28.24, 29.78, 50.10, 1.08, "פעמיים ספורטאי השנה"),
    ("full", 30.21, 32.08, 52.10, 1.08, "שמונה עשרה פעמים אלוף ישראל"),
    ("full", 32.51, 34.28, 53.35, 1.08, "מעל מאתיים קרבות זירה"),
    # closing (from the first recording)
    ("first", 27.31, 30.59, 55.40, 1.00, "טים משה. בואו להיות חלק ממשפחת טים משה"),
]

CLEAN = ("highpass=f=85,afftdn=nr=14:nf=-42:tn=1,"
         "equalizer=f=140:t=q:w=1.0:g=2.5,equalizer=f=380:t=q:w=1.3:g=-2.5,"
         "equalizer=f=3200:t=q:w=1.0:g=4,equalizer=f=7500:t=q:w=1.5:g=-2,"
         "acompressor=threshold=-22dB:ratio=3.5:attack=6:release=150:makeup=7,"
         "loudnorm=I=-16:TP=-2:LRA=6")

def load(src):
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", src, "-af", CLEAN,
                          "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(float) / 32768

def tempo(seg, t):
    if t == 1.0: return seg
    raw = (np.clip(seg, -1, 1) * 32767).astype(np.int16).tobytes()
    out = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-",
                          "-af", f"atempo={t}", "-f", "s16le", "-"], input=raw, capture_output=True, check=True).stdout
    return np.frombuffer(out, np.int16).astype(float) / 32768

def main(full, first, dst):
    rec = {"full": load(full), "first": load(first)}
    track = np.zeros(int(SR * DURATION)); cursor = 0.0
    for r, a, b, t, tp, text in LINES:
        x = rec[r]
        seg = x[int(max(0, a - 0.03) * SR): int(min(b + 0.08, len(x) / SR) * SR)].copy()
        seg = tempo(seg, tp)
        k = int(0.012 * SR); seg[:k] *= np.linspace(0, 1, k); seg[-k:] *= np.linspace(1, 0, k)
        start = max(t, cursor + (0.05 if tp != 1.0 or t > 55 else 0.10))
        i0 = int(start * SR); n = min(len(seg), len(track) - i0)
        track[i0:i0 + n] += seg[:n]; cursor = start + len(seg) / SR
        print(f"{start:6.2f}-{cursor:6.2f}  (caption {t:5.2f})  {text}")
    track = track / (np.max(np.abs(track)) + 1e-9) * 0.89
    with wave.open(dst, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((track * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
