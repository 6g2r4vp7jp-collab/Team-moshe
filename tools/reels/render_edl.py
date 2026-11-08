#!/usr/bin/env python3
"""Render a 9:16 reel from an EDL (see .claude/skills/or-moshe-marketing/workflows/reels-editing.md).

- Cuts each clip from its source; never ends a clip before impact + 0.3s (hard error).
- Vertical sources are cropped to fill 1080x1920; horizontal ones are fitted over a blurred
  copy of themselves so no action is cropped out ("fit": "crop" | "blur" overrides).
- Slow motion ("slowmo": 0.5) applies only around the impact (-0.5s .. +0.6s), so the real
  sequence of events is kept and the hit itself is what slows down.
- Gold Hebrew captions (libass, RTL-aware) inside the Instagram safe zone.
- Optional music bed under the original fight sound.

Usage: python3 tools/reels/render_edl.py reels/edl/<name>.json [--out reels/out/<name>.mp4]
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
W, H, FPS = 1080, 1920, 30
GOLD_ASS = "&H0037AFD4"  # #D4AF37 as ASS BGR
FONTS_DIR = ROOT / "tools" / "reels" / "fonts"
SLOW_PRE, SLOW_POST, MIN_AFTER_IMPACT = 0.5, 0.6, 0.3


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"ffmpeg failed:\n{' '.join(map(str, cmd))}\n{r.stderr[-2000:]}")
    return r


def probe(src):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:stream_side_data=rotation",
             "-of", "json", str(src)])
    s = json.loads(r.stdout)["streams"][0]
    w, h = s["width"], s["height"]
    rot = abs(int(next((d.get("rotation", 0) for d in s.get("side_data_list", [])), 0)))
    if rot in (90, 270):
        w, h = h, w
    a = run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(src)])
    return w, h, bool(a.stdout.strip())


def validate(edl):
    errs = []
    for i, c in enumerate(edl["clips"], 1):
        src = ROOT / c["src"]
        if not src.exists():
            errs.append(f"clip {i}: source not found: {c['src']}")
        if c["out"] <= c["in"]:
            errs.append(f"clip {i}: out <= in")
        imp = c.get("impact")
        if imp is not None:
            if not (c["in"] <= imp <= c["out"]):
                errs.append(f"clip {i}: impact {imp} is outside in/out")
            elif c["out"] < imp + MIN_AFTER_IMPACT:
                errs.append(f"clip {i}: ends {c['out'] - imp:.2f}s after impact; must be >= {MIN_AFTER_IMPACT}s (don't cut before the hit lands)")
        if c.get("slowmo") and imp is None:
            errs.append(f"clip {i}: slowmo needs an impact time")
        if not c.get("desc"):
            errs.append(f"clip {i}: 'desc' (what really happens) is required")
    if errs:
        sys.exit("EDL rejected:\n  " + "\n  ".join(errs))


def segments(c):
    """[(start, end, speed)] in source time."""
    imp, sm = c.get("impact"), c.get("slowmo")
    if not sm or sm >= 1:
        return [(c["in"], c["out"], 1.0)]
    a, b = max(c["in"], imp - SLOW_PRE), min(c["out"], imp + SLOW_POST)
    segs = [(c["in"], a, 1.0), (a, b, float(sm)), (b, c["out"], 1.0)]
    return [s for s in segs if s[1] - s[0] > 0.04]


def render_segment(src, start, end, speed, fit, has_audio, out):
    pts = f"setpts=(PTS-STARTPTS)/{speed}"
    if fit == "crop":
        vf = f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{pts},fps={FPS},setsar=1[v]"
    else:
        vf = (f"[0:v]split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:3,eq=brightness=-0.12[bg];"
              f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,{pts},fps={FPS},setsar=1[v]")
    dur = (end - start) / speed
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(src)]
    if has_audio:
        af = f"[0:a]aresample=48000,atempo={max(speed, 0.5)},apad,atrim=0:{dur:.3f}[a]"
    else:
        cmd += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        af = "[1:a]anull[a]"
    cmd += ["-filter_complex", f"{vf};{af}", "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "256k", "-ac", "2", str(out)]
    run(cmd)
    return dur


def ass_time(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02}:{s:05.2f}"


def write_ass(captions, path, font):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Gold,{font},92,{GOLD_ASS},&H00FFFFFF,&H00000000,&H96000000,1,0,0,0,100,100,0,0,1,5,3,2,90,90,520,177

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Gold,,0,0,0,,{{\\fad(120,120)}}{t}" for a, b, t in captions]
    path.write_text(head + "\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("edl")
    ap.add_argument("--out")
    ap.add_argument("--font", default="Frank Ruhl Libre")
    a = ap.parse_args()
    edl = json.loads(Path(a.edl).read_text(encoding="utf-8"))
    validate(edl)
    out = Path(a.out) if a.out else ROOT / "reels" / "out" / f"{edl['name']}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="reel_"))
    parts, captions, t = [], [], 0.0
    for i, c in enumerate(edl["clips"]):
        src = ROOT / c["src"]
        w, h, has_audio = probe(src)
        fit = c.get("fit") or ("crop" if h >= w else "blur")
        clip_start = t
        for j, (s, e, sp) in enumerate(segments(c)):
            p = tmp / f"p{i:03}_{j}.mp4"
            t += render_segment(src, s, e, sp, fit, has_audio, p)
            parts.append(p)
        if c.get("caption"):
            captions.append((clip_start + 0.1, t - 0.05, c["caption"]))
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    joined = tmp / "joined.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])

    vf = "null"
    if captions:
        ass = tmp / "captions.ass"
        write_ass(captions, ass, a.font)
        fd = f":fontsdir={FONTS_DIR}" if FONTS_DIR.exists() else ""
        vf = f"subtitles={ass}{fd}"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(joined)]
    music = edl.get("music")
    fo = max(t - 1.2, 0)
    if music:
        cmd += ["-i", str(ROOT / music)]
        af = (f"[0:a]volume=1.0[fx];[1:a]atrim=0:{t:.3f},volume=0.55,afade=t=in:d=0.4,afade=t=out:st={fo:.2f}:d=1.2[m];"
              f"[m][fx]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    else:
        af = f"[0:a]afade=t=out:st={fo:.2f}:d=1.2,loudnorm=I=-14:TP=-1.5:LRA=11[a]"
    cmd += ["-filter_complex", f"[0:v]{vf}[v];{af}", "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(out)]
    run(cmd)
    shutil.rmtree(tmp, ignore_errors=True)
    note = "" if 20 <= t <= 45 else f"  ⚠️ אורך {t:.1f} שניות, מחוץ לטווח המועדף 20–45"
    print(f"wrote {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out} ({t:.1f}s){note}")
    if music and not edl.get("music_license"):
        print("⚠️ music_license is missing in the EDL. Record the music's license before publishing.")


if __name__ == "__main__":
    main()
