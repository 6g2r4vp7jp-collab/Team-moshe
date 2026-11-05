"""Voice-over: Hebrew male narrator (Microsoft he-IL-AvriNeural via edge-tts), processed to a deep fight-promo bass.
Each line is spoken when its gold caption appears (times from overlay.html); lines never overlap.
usage: python3 narration.py out.wav
"""
import asyncio, os, subprocess, sys, wave
import numpy as np
import edge_tts

SR = 48000
DURATION = 60.25
WORK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "work", "vo")
os.makedirs(WORK, exist_ok=True)

# (caption time, spoken text)  - numbers written as words for correct pronunciation
LINES = [
    (0.70,  "אור משה."),
    (6.45,  "אלוף משחקי העולם."),
    (8.70,  "מעל מאתיים קרבות זירה."),
    (13.75, "אלופים לא נולדים, הם נבנים."),
    (24.20, "פעמיים אלוף אירופה."),
    (29.70, "גם אתם חולמים להיות אלופים?"),
    (32.30, "מהזירה..."),
    (33.30, "לדור הבא."),
    (38.05, "כל אלוף התחיל מצעד ראשון."),
    (41.30, "כאן מגדלים אלופים."),
    (46.65, "אלוף גביע העולם."),
    (47.65, "אלוף גביע אירופה."),
    (48.90, "שלוש פעמים סגן אלוף העולם."),
    (50.15, "פעמיים ספורטאי השנה."),
    (52.15, "שמונה עשרה פעמים אלוף ישראל."),
    (55.40, "טים משה."),
    (57.45, "בואו להיות חלק ממשפחת טים משה."),
]

async def synth(text, path, rate):
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    await edge_tts.Communicate(text, "he-IL-AvriNeural", rate=rate, pitch="+0Hz", proxy=proxy).save(path)

def load(path):
    # warm, natural, inviting voice: no pitch shift, no echo; gentle warmth + clarity, light compression
    out = path.replace(".mp3", ".wav")
    af = ("aresample=48000,highpass=f=70,equalizer=f=160:t=q:w=1.0:g=2,equalizer=f=450:t=q:w=1.2:g=-1.5,"
          "equalizer=f=5500:t=q:w=1.0:g=2,acompressor=threshold=-18dB:ratio=2:attack=10:release=200:makeup=3,"
          "alimiter=limit=0.9")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", path, "-af", af, "-ac", "1", out], check=True)
    with wave.open(out) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
    nz = np.where(np.abs(x) > 0.01)[0]                     # trim leading/trailing silence
    return x[max(0, nz[0] - 200): nz[-1] + 2400] if len(nz) else x

def main(dst):
    track = np.zeros(int(SR * DURATION))
    cursor = 0.0
    for i, (t, text) in enumerate(LINES):
        rate = "+0%" if (44.0 <= t < 55.0) or t >= 57.0 else "-6%"   # honor roll + closing line a little quicker
        p = os.path.join(WORK, f"l{i:02d}.mp3")
        asyncio.run(synth(text, p, rate))
        x = load(p)
        start = max(t, cursor + (0.04 if 44.0 <= t < 55.0 else 0.12))
        i0 = int(start * SR); n = min(len(x), len(track) - i0)
        track[i0:i0 + n] += x[:n]
        cursor = start + len(x) / SR
        print(f"{start:6.2f}-{cursor:6.2f}  (caption {t:5.2f})  {text}")
    track = track / (np.max(np.abs(track)) + 1e-9) * 0.89
    with wave.open(dst, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((track * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    main(sys.argv[1])
