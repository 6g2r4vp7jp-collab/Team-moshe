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
    t0, dur, src, sin, speed, crop = shot[:6]
    sw, sh, hlg = probe(os.path.join(RAW, src))
    f = []
    tail = []
    pre = ""
    if speed != 1.0:
        if src.startswith("RPReplay"):            # 60p screen recording of ~30p broadcast: drop dupes, re-time, interpolate
            pre = "mpdecimate,setpts=N/30/TB,minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
        elif src.startswith("v29025"):            # 25p broadcast: motion-interpolate to 60p before slowing down
            pre = "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
        tail.append(f"setpts=PTS/{speed}")
    tail += [f"fps={FPS}", GRADE]
    if t0 in DIM: tail.append(f"eq=brightness=-{DIM[t0] * 0.25}:saturation=0.8,gblur=sigma=2")
    tail.append("format=yuv420p")
    if crop["type"] == "rect":                     # upscaled broadcast material: lanczos + extra sharpening
        return (pre + f"crop={crop['w']}:{crop['h']}:{crop['x']}:{crop['y']},scale={W}:{H}:flags=lanczos,"
                "unsharp=5:5:1.0:3:3:0.4,hqdn3d=1:1:3:3," + ",".join(tail))
    if crop["type"] == "panel":                    # landscape action kept whole, full-width, over its own blurred fill
        pw, ph = crop["w"], crop["h"]
        fh = int(round(W * ph / pw / 2)) * 2
        c = f"crop={pw}:{ph}:{crop['x']}:{crop['y']}"
        return (pre + f"{c},split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"gblur=sigma=40,eq=brightness=-0.32:saturation=0.6[bg];[b]scale={W}:{fh}:flags=lanczos,unsharp=5:5:0.8[fg];"
                f"[bg][fg]overlay=0:{(H - fh) // 2}," + ",".join(tail))
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

def render_photo(i, t0, dur, crop):
    """Still photo -> 1080x1920 clip with a slow, smooth push-in (rendered at 2x then downscaled: no jitter)."""
    from PIL import Image, ImageOps, ImageFilter
    n = int((t0 + dur) * FPS + 0.5) - int(t0 * FPS + 0.5)
    im = ImageOps.exif_transpose(Image.open(os.path.join(RAW, "photos", crop["file"]))).convert("RGB")
    BW, BH = W * 2, H * 2
    if crop["mode"] == "full":                     # fill the 9:16 frame around the focus point
        sc = max(BW / im.width, BH / im.height); im2 = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
        x = min(max(0, int(im2.width * crop["cx"] - BW / 2)), im2.width - BW)
        y = min(max(0, int(im2.height * crop["cy"] - BH / 2)), im2.height - BH)
        canvas = im2.crop((x, y, x + BW, y + BH))
    else:                                          # whole photo full-width over its own blurred, darkened fill
        sc = max(BW / im.width, BH / im.height); bg = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
        bx, by = (bg.width - BW) // 2, (bg.height - BH) // 2
        bg = bg.crop((bx, by, bx + BW, by + BH)).filter(ImageFilter.GaussianBlur(60))
        bg = Image.eval(bg, lambda v: int(v * 0.5))
        fg = im.resize((BW, round(im.height * BW / im.width)), Image.LANCZOS)
        if fg.height > BH:
            y = min(max(0, int(fg.height * crop["cy"] - BH / 2)), fg.height - BH); fg = fg.crop((0, y, BW, y + BH))
        bg.paste(fg, (0, (BH - fg.height) // 2)); canvas = bg
    src = os.path.join(OUT, f"{i:02d}_still.png"); canvas.save(src)
    z0, z1 = crop["z0"], crop["z1"]
    zexpr = f"{z0}+({z1}-{z0})*(1-pow(1-on/{max(n - 1, 1)},2))"     # ease-out push-in
    vf = (f"zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={BW}x{BH}:fps={FPS},"
          f"scale={W}:{H}:flags=lanczos,{GRADE},format=yuv420p")
    name = os.path.join(OUT, f"{i:02d}.mp4")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", src,
                    "-vf", vf, "-frames:v", str(n), "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-pix_fmt", "yuv420p", name], check=True)
    os.remove(src)
    return name

def render(i_shot):
    i, shot = i_shot
    t0, dur, src, sin, speed, crop = shot[:6]
    if crop["type"] == "photo":
        return render_photo(i, t0, dur, crop)
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
