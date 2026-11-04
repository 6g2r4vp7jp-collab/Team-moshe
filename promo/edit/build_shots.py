"""Render every shot of the EDL to a graded 1080x1920/30fps intermediate (+ its location audio)."""
import os, subprocess, sys, json
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from edl import SHOTS, FPS, W, H, DIM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")
OUT = os.path.join(ROOT, "work", "shots")
os.makedirs(OUT, exist_ok=True)

def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,color_transfer:stream_side_data=rotation", "-of", "json", path],
                       capture_output=True, text=True)
    s = json.loads(r.stdout)["streams"][0]
    rot = 0
    for sd in s.get("side_data_list", []):
        rot = int(sd.get("rotation", 0))
    w, h = s["width"], s["height"]
    if abs(rot) == 90:
        w, h = h, w
    return w, h, s.get("color_transfer") == "arib-std-b67"

GRADE = ("eq=contrast=1.13:saturation=1.15:brightness=-0.015:gamma=0.97,"
         "curves=r='0/0 0.25/0.22 0.75/0.80 1/1':g='0/0 0.25/0.23 0.75/0.78 1/1':b='0/0.02 0.25/0.26 0.75/0.76 1/0.96',"
         "vignette=angle=PI/4.2")

def chain(shot):
    t0, dur, src, sin, speed, crop = shot
    sw, sh, hlg = probe(os.path.join(RAW, src))
    f = []
    if crop["type"] == "win":                      # 16:9 -> 9:16 window, then scale (no stretch)
        cw = round(sh * 9 / 16 / 2) * 2
        f.append(f"crop={cw}:{sh}:{crop['x']}:0")
    else:                                          # portrait punch-in
        z = crop["z"]
        cw, ch = int(sw / z) // 2 * 2, int(sh / z) // 2 * 2
        x = min(max(0, int(sw * crop["cx"] - cw / 2)), sw - cw)
        y = min(max(0, int(sh * crop["cy"] - ch / 2)), sh - ch)
        f.append(f"crop={cw}:{ch}:{x}:{y}")
    if hlg:
        f.append(f"zscale=w={W}:h={H}:f=spline36:tin=arib-std-b67:min=bt2020nc:pin=bt2020:t=linear:npl=100,"
                 "format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
                 "eq=brightness=0.03:contrast=1.08")
    else:
        f.append(f"scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6")
    if speed != 1.0:
        f.append(f"setpts=PTS/{speed}")
    f.append(f"fps={FPS}")
    f.append(GRADE)
    if t0 in DIM:
        f.append(f"eq=brightness=-{DIM[t0] * 0.25}:saturation=0.8,gblur=sigma=2")
    f.append("format=yuv420p")
    return ",".join(f)

def render(i_shot):
    i, shot = i_shot
    t0, dur, src, sin, speed, crop = shot
    n = int((t0 + dur) * FPS + 0.5) - int(t0 * FPS + 0.5)
    name = os.path.join(OUT, f"{i:02d}.mp4")
    src_len = dur * speed + 0.25
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{sin:.3f}", "-t", f"{src_len:.3f}",
           "-i", os.path.join(RAW, src), "-vf", chain(shot), "-frames:v", str(n), "-an",
           "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-pix_fmt", "yuv420p", name]
    subprocess.run(cmd, check=True)
    # location audio (only for real-time shots; slow-mo gets designed sound instead)
    if speed == 1.0:
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{sin:.3f}", "-t", f"{dur:.3f}",
                        "-i", os.path.join(RAW, src), "-vn", "-ac", "2", "-ar", "44100", os.path.join(OUT, f"{i:02d}.wav")],
                       check=False)
    return name

if __name__ == "__main__":
    only = [int(a) for a in sys.argv[1:]]
    jobs = [(i, s) for i, s in enumerate(SHOTS) if not only or i in only]
    with ThreadPoolExecutor(4) as ex:
        for n in ex.map(render, jobs):
            print("ok", os.path.basename(n), flush=True)
