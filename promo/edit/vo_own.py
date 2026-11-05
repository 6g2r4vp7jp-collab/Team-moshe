"""Or's own voice-over: clean + sharpen the recording, cut it into its 15 lines at the pauses, and place every line
exactly on its gold caption (v15 picture, 60.25 s).
usage: python3 vo_own.py recording.m4a out.wav
"""
import subprocess, sys, wave
import numpy as np

SR = 48000
DURATION = 60.25

# line segments in the recording (seconds), found from the pauses, in the order Or read them
SEGMENTS = [
    (0.00, 1.32, "אור משה"),
    (1.57, 2.76, "אלוף משחקי העולם"),
    (3.36, 4.88, "מעל מאתיים קרבות זירה"),
    (5.48, 7.76, "אלופים לא נולדים... הם נבנים"),
    (8.33, 9.48, "פעמיים אלוף אירופה"),
    (10.12, 11.68, "גם אתם חולמים להיות אלופים?"),
    (12.17, 13.71, "מהזירה... לדור הבא"),
    (14.43, 16.02, "כל אלוף התחיל מצעד ראשון"),
    (16.49, 17.64, "כאן מגדלים אלופים"),
    (18.25, 19.82, "שלוש פעמים סגן אלוף העולם"),
    (20.15, 22.27, "אלוף גביע העולם, ואלוף גביע אירופה"),
    (22.71, 24.26, "פעמיים ספורטאי השנה"),
    (24.76, 26.42, "שמונה עשרה פעמים אלוף ישראל"),
    (27.31, 30.59, "טים משה. בואו להיות חלק ממשפחת טים משה"),
]
# when each line is spoken in the video = when its caption appears
PLACE = {
    "אור משה": 0.70,
    "אלוף משחקי העולם": 6.45,
    "מעל מאתיים קרבות זירה": 8.70,
    "אלופים לא נולדים... הם נבנים": 13.75,
    "פעמיים אלוף אירופה": 24.20,
    "גם אתם חולמים להיות אלופים?": 29.70,
    "מהזירה... לדור הבא": 32.30,
    "כל אלוף התחיל מצעד ראשון": 38.05,
    "כאן מגדלים אלופים": 41.30,
    "אלוף גביע העולם, ואלוף גביע אירופה": 46.65,   # captions: גביע העולם 46.6, גביע אירופה 47.6
    "שלוש פעמים סגן אלוף העולם": 48.90,
    "פעמיים ספורטאי השנה": 50.60,
    "שמונה עשרה פעמים אלוף ישראל": 52.15,
    "טים משה. בואו להיות חלק ממשפחת טים משה": 55.40,
}

# clean + sharpen: noise reduction, rumble cut, warmth, clarity/presence, gentle de-ess, compression, light room
CLEAN = ("highpass=f=85,afftdn=nr=14:nf=-42:tn=1,"
         "equalizer=f=140:t=q:w=1.0:g=2.5,equalizer=f=380:t=q:w=1.3:g=-2.5,"
         "equalizer=f=3200:t=q:w=1.0:g=4,equalizer=f=7500:t=q:w=1.5:g=-2,"
         "acompressor=threshold=-22dB:ratio=3.5:attack=6:release=150:makeup=7,"
         "loudnorm=I=-16:TP=-2:LRA=6")

def main(src, dst):
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", src, "-af", CLEAN,
                          "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float) / 32768
    track = np.zeros(int(SR * DURATION)); cursor = 0.0
    for a, b, text in sorted(SEGMENTS, key=lambda s: PLACE[s[2]]):
        seg = x[int(max(0, a - 0.04) * SR): int(min(b + 0.10, len(x) / SR) * SR)].copy()
        k = int(0.012 * SR); seg[:k] *= np.linspace(0, 1, k); seg[-k:] *= np.linspace(1, 0, k)
        start = max(PLACE[text], cursor + 0.10)
        i0 = int(start * SR); n = min(len(seg), len(track) - i0)
        track[i0:i0 + n] += seg[:n]; cursor = start + len(seg) / SR
        print(f"{start:6.2f}-{cursor:6.2f}  (caption {PLACE[text]:5.2f})  {text}")
    track = track / (np.max(np.abs(track)) + 1e-9) * 0.89
    with wave.open(dst, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((track * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
