#!/usr/bin/env python3
"""List video files in a folder with duration, resolution, orientation and fps -> reels/inventory.csv.

Usage: python3 tools/reels/inventory.py promo/raw [more folders...]
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXT = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".webm"}


def probe(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(f)],
                       capture_output=True, text=True)
    if r.returncode:
        return None
    j = json.loads(r.stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    if not v:
        return None
    w, h = int(v["width"]), int(v["height"])
    rot = 0
    for sd in v.get("side_data_list", []):
        rot = abs(int(sd.get("rotation", 0)))
    if rot in (90, 270):
        w, h = h, w
    num, den = (v.get("avg_frame_rate") or "0/1").split("/")
    fps = round(float(num) / float(den), 2) if float(den) else 0
    return {"file": str(f.relative_to(ROOT)) if f.is_relative_to(ROOT) else str(f),
            "duration": round(float(j["format"].get("duration", 0)), 2), "width": w, "height": h,
            "orientation": "vertical" if h > w else ("square" if h == w else "horizontal"), "fps": fps,
            "has_audio": any(s["codec_type"] == "audio" for s in j["streams"]),
            "size_mb": round(int(j["format"].get("size", 0)) / 1e6, 1)}


def main():
    dirs = [Path(a) for a in sys.argv[1:]] or [ROOT / "promo" / "raw"]
    rows = []
    for d in dirs:
        for f in sorted(p for p in d.rglob("*") if p.suffix.lower() in EXT):
            info = probe(f.resolve())
            if info:
                rows.append(info)
    out = ROOT / "reels" / "inventory.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "duration", "width", "height", "orientation", "fps", "has_audio", "size_mb"])
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"{r['duration']:>7.1f}s {r['width']}x{r['height']} {r['orientation']:<10} {r['fps']:>5}fps  {r['file']}")
    print(f"{len(rows)} files -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
