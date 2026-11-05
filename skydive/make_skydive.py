"""Freefall-from-a-helicopter video built from the cutout photo (cutout.png).

Usage: python3 make_skydive.py out.mp4
Renders 1080x1920 @30fps frames, synthesizes audio (rotor, wind, canopy pop), muxes with ffmpeg.
"""
import math, random, subprocess, sys, wave, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 16.0
N = int(FPS * DUR)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "skydive.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
random.seed(7)

# Timeline (seconds)
T_JUMP, T_OPEN, T_LAND = 3.2, 10.0, 14.6

people = Image.open(os.path.join(HERE, "cutout.png")).convert("RGBA")
# soften the hard crop line at the bottom of the photo
_a = np.array(people.getchannel("A"), dtype=np.float32)
_fade = np.clip((people.height - np.arange(people.height)) / 160.0, 0, 1)[:, None]
people.putalpha(Image.fromarray((_a * _fade).astype(np.uint8)))


def lerp(a, b, t): return a + (b - a) * t
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)


# ---------- static assets ----------
def sky_gradient(top, bottom):
    g = np.linspace(0, 1, H)[:, None]
    arr = (np.array(top)[None, None, :] * (1 - g[..., None]) + np.array(bottom)[None, None, :] * g[..., None])
    arr = np.repeat(arr, W, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")

SKY = sky_gradient((40, 110, 205), (170, 215, 250))


def make_cloud(w, h, alpha=230):
    pad = 60
    im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for _ in range(14):
        r = random.randint(h // 5, h // 2 - 4)
        cx = random.randint(r, w - r) + pad
        cy = random.randint(h // 2 - h // 8, h - r) + pad
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, alpha))
    return im.filter(ImageFilter.GaussianBlur(h / 22))

CLOUD_IMGS = [make_cloud(random.randint(360, 620), random.randint(170, 260)) for _ in range(6)]
# cloud field: (x, world_y, img index, depth factor)
CLOUDS = [(random.uniform(-250, W - 150), random.uniform(-12000, 2400), random.randrange(6), random.uniform(0.55, 1.4))
          for _ in range(60)]


def helicopter(rotor_phase):
    im = Image.new("RGBA", (900, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body = (225, 70, 40, 255)
    dark = (40, 40, 48, 255)
    # tail boom + tail fin + tail rotor
    d.polygon([(330, 200), (860, 175), (860, 195), (330, 250)], fill=body)
    d.polygon([(820, 110), (870, 110), (880, 200), (840, 200)], fill=body)
    tr = 45 * abs(math.cos(rotor_phase * 2.3))
    d.ellipse([845 - 8, 150 - tr, 845 + 8, 150 + tr], fill=(60, 60, 60, 160))
    # cabin
    d.rounded_rectangle([90, 150, 470, 300], radius=70, fill=body)
    d.pieslice([40, 150, 240, 330], 90, 270, fill=body)
    # windshield
    d.pieslice([60, 165, 220, 290], 180, 270, fill=(150, 210, 240, 255))
    # open door (dark) -- the jumpers leave from here
    d.rectangle([250, 180, 360, 290], fill=(25, 25, 30, 255))
    # stripe
    d.rectangle([120, 260, 460, 272], fill=(255, 255, 255, 255))
    # skids
    d.line([(140, 300), (130, 345)], fill=dark, width=10)
    d.line([(400, 300), (410, 345)], fill=dark, width=10)
    d.line([(70, 345), (480, 345)], fill=dark, width=12)
    # mast + main rotor (blurred blade disk)
    d.rectangle([265, 120, 285, 152], fill=dark)
    blade = 380 * math.cos(rotor_phase)
    d.ellipse([275 - 400, 105, 275 + 400, 125], fill=(70, 70, 80, 70))
    d.line([(275 - blade, 115), (275 + blade, 115)], fill=dark, width=9)
    return im


def parachute(open_t):
    """Canopy with lines. open_t 0..1 (inflation). Returns image and anchor (x,y) where lines meet."""
    w, h = 900, 760
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = lerp(0.15, 1.0, ease(open_t))
    cw, ch = 760 * s, 280 * s
    cx, top = w / 2, 40 + (1 - s) * 200
    colors = [(235, 60, 70), (255, 200, 40), (40, 160, 230), (255, 255, 255), (60, 190, 110), (235, 60, 70), (255, 200, 40)]
    n = len(colors)
    for i in range(n):
        a0 = 180 + i * 180 / n
        a1 = 180 + (i + 1) * 180 / n
        d.pieslice([cx - cw / 2, top, cx + cw / 2, top + ch * 2], a0, a1, fill=colors[i] + (255,))
    d.chord([cx - cw / 2, top + ch - 30 * s, cx + cw / 2, top + ch + 30 * s], 0, 180, fill=(0, 0, 0, 0))
    ax, ay = cx, h - 10
    for i in range(n + 1):
        px = cx - cw / 2 + i * cw / n
        d.line([(px, top + ch), (ax, ay)], fill=(50, 50, 50, 200), width=3)
    return im, (ax, ay)


def text_img(txt, size, fill=(255, 255, 255), stroke=(0, 0, 0)):
    f = ImageFont.truetype(FONT, size)
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = d0.textbbox((0, 0), txt, font=f, stroke_width=8, direction="rtl", language="he")
    im = Image.new("RGBA", (bb[2] - bb[0] + 20, bb[3] - bb[1] + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - bb[0], 10 - bb[1]), txt, font=f, fill=fill, stroke_width=8,
                            stroke_fill=stroke, direction="rtl", language="he")
    return im

TXT_ALT = text_img("4,000 מטר מעל הקרקע", 70)
TXT_GO = text_img("3 · 2 · 1 · קופצים!", 84, fill=(255, 225, 60))
TXT_FREE = text_img("צניחה חופשית!", 110, fill=(255, 255, 255))
TXT_CHUTE = text_img("המצנח נפתח!", 96, fill=(255, 225, 60))
TXT_LAND = text_img("נחיתה מושלמת!", 110, fill=(255, 255, 255))
TXT_TEAM = text_img("אבא ואני – צוות אחד", 66, fill=(255, 225, 60))


def ground(progress):
    """Ground layer rising from the bottom during the descent. progress 0..1."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    horizon = int(lerp(H + 50, H * 0.55, ease(progress)))
    d = ImageDraw.Draw(im)
    # distant hills
    d.ellipse([-400, horizon - 120, 700, horizon + 260], fill=(110, 165, 110, 255))
    d.ellipse([400, horizon - 160, 1500, horizon + 260], fill=(95, 150, 100, 255))
    d.rectangle([0, horizon + 40, W, max(H, horizon + 40)], fill=(120, 185, 90, 255))
    # fields stripes
    for i in range(8):
        y = horizon + 60 + i * i * 14
        if y < H:
            d.rectangle([0, y, W, y + 6 + i * 2], fill=(140, 200, 100, 255))
    # landing target
    ty = horizon + 360
    for r, c in [(170, (255, 255, 255)), (120, (230, 60, 60)), (70, (255, 255, 255)), (30, (230, 60, 60))]:
        d.ellipse([W / 2 - r, ty - r * 0.35, W / 2 + r, ty + r * 0.35], fill=c + (255,))
    return im, ty


def paste_center(base, im, cx, cy, alpha=1.0):
    if alpha < 1.0:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im = im.copy(); im.putalpha(a)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def text_fade(t, t0, t1, fade=0.3):
    if t < t0 or t > t1: return 0.0
    return clamp(min((t - t0) / fade, (t1 - t) / fade))


# ---------- frame renderer ----------
def render(i):
    t = i / FPS
    # camera world-y (the camera "falls" with the jumpers). speed by phase.
    if t < T_JUMP:
        cam = 0.0
    elif t < T_OPEN:
        tt = t - T_JUMP
        cam = 900 * tt + 120 * tt * tt  # accelerating fall
    else:
        tt0 = T_OPEN - T_JUMP
        base = 900 * tt0 + 120 * tt0 * tt0
        tt = t - T_OPEN
        cam = base + 2600 * (1 - math.exp(-tt * 2.5)) + 180 * tt
    frame = SKY.copy()

    # clouds (world moves up as camera falls)
    for x, wy, k, depth in CLOUDS:
        y = wy + cam * depth * 0.35 - 1200 * depth
        y = (y % 14000) - 1600
        if -400 < y < H + 100:
            c = CLOUD_IMGS[k]
            if depth != 1:
                c = c.resize((int(c.width * depth), int(c.height * depth)))
            frame.alpha_composite(c, (int(x), int(y)))

    # speed lines during freefall
    if T_JUMP + 0.6 < t < T_OPEN + 0.2:
        d = ImageDraw.Draw(frame)
        rnd = random.Random(i)
        for _ in range(26):
            x = rnd.uniform(0, W)
            y = rnd.uniform(-200, H)
            ln = rnd.uniform(120, 380)
            d.line([(x, y), (x, y - ln)], fill=(255, 255, 255, rnd.randint(60, 140)), width=rnd.randint(2, 5))

    # ground in the last part
    gp = clamp((t - (T_OPEN + 1.2)) / (T_LAND - T_OPEN - 1.2))
    land_y = None
    if gp > 0:
        g, land_y = ground(gp)
        frame.alpha_composite(g)

    # helicopter
    heli_y = 520 - cam * 0.8
    if heli_y > -500:
        hx = lerp(-700, W / 2 + 80, ease(t / 2.2)) + 10 * math.sin(t * 3)
        hy = heli_y + 12 * math.sin(t * 4.1)
        paste_center(frame, helicopter(t * 40), hx, hy)
    else:
        hx, hy = W / 2 + 80, heli_y

    # jumpers
    if t < T_JUMP:
        # inside the door: peek out (small)
        if t > 2.0:
            sc = 0.16
            p = people.resize((int(people.width * sc), int(people.height * sc)))
            paste_center(frame, p, hx - 135 + 85, hy - 20, alpha=ease((t - 2.0) / 0.5))
    else:
        tt = t - T_JUMP
        sc = lerp(0.16, 0.62, ease(tt / 1.6))
        if t > T_OPEN:
            sc = lerp(0.62, 0.42, ease((t - T_OPEN) / 1.0))
        if t > T_LAND - 1.6:
            sc = lerp(0.42, 0.5, ease((t - (T_LAND - 1.6)) / 1.6))
        if t < T_OPEN:
            rot = 14 * math.sin(tt * 2.2) + lerp(70, 0, ease(tt / 1.4))
            shake = 9 * min(1, tt / 2)
            jx = W / 2 + shake * math.sin(t * 37) + lerp(hx - 50 - W / 2, 0, ease(tt / 1.4))
            jy = lerp(hy + 30, H * 0.55, ease(tt / 1.4)) + shake * math.cos(t * 41)
        else:
            to = t - T_OPEN
            rot = 6 * math.sin(to * 1.6) * math.exp(-to * 0.3)
            jx = W / 2 + 30 * math.sin(to * 1.1)
            jy = lerp(H * 0.55, H * 0.66, ease(to / 1.2))
            if land_y is not None and t > T_LAND - 1.6:
                feet_target = land_y + 10
                ph = people.height * sc
                jy = lerp(jy, feet_target - ph / 2, ease((t - (T_LAND - 1.6)) / 1.6))
            if t > T_LAND:
                jy += -18 * abs(math.sin((t - T_LAND) * 9)) * math.exp(-(t - T_LAND) * 3)
        p = people.resize((int(people.width * sc), int(people.height * sc)), Image.LANCZOS)
        p = p.rotate(rot, resample=Image.BICUBIC, expand=True)

        # parachute behind/above the jumpers
        if t > T_OPEN - 0.15:
            ot = clamp((t - (T_OPEN - 0.15)) / 0.55)
            chute_alpha = 1.0 if t < T_LAND + 0.25 else clamp(1 - (t - T_LAND - 0.25) / 0.6)
            if chute_alpha > 0:
                c, (ax, ay) = parachute(ot)
                cs = sc / 0.42 * 0.95
                c = c.resize((int(c.width * cs), int(c.height * cs)))
                top_of_people = jy - people.height * sc / 2 + 40 * cs
                cx = jx
                cy = top_of_people - c.height / 2 + 10
                if t > T_LAND:
                    cy += (t - T_LAND) * 600  # canopy collapses down
                paste_center(frame, c, cx, cy, alpha=chute_alpha)
        paste_center(frame, p, jx, jy)

    # captions
    for img, t0, t1, y in [(TXT_ALT, 0.4, 2.6, 240), (TXT_GO, 2.2, 3.6, 380), (TXT_FREE, 4.0, 8.6, 260),
                           (TXT_CHUTE, 10.1, 12.4, 260), (TXT_LAND, 14.7, 16.0, 260), (TXT_TEAM, 15.0, 16.0, 400)]:
        a = text_fade(t, t0, t1)
        if a > 0:
            pop = 1 + 0.25 * (1 - ease((t - t0) / 0.25))
            im = img.resize((int(img.width * pop), int(img.height * pop))) if pop > 1.001 else img
            paste_center(frame, im, W / 2, y, alpha=a)

    # altimeter
    if t < T_OPEN:
        alt = 4000 - 2600 * ease((t - T_JUMP) / (T_OPEN - T_JUMP)) ** 0.8
    else:
        alt = 1400 * (1 - clamp((t - T_OPEN) / (T_LAND - T_OPEN)) ** 1.3)
    alt = max(0, int(alt))
    if t > T_JUMP and t < T_LAND + 0.3:
        d = ImageDraw.Draw(frame)
        d.rounded_rectangle([40, H - 200, 420, H - 70], radius=24, fill=(0, 0, 0, 140))
        f = ImageFont.truetype(FONT, 64)
        d.text((70, H - 175), f"{alt:,} m", font=f, fill=(255, 255, 255))

    # white flash at the jump and at chute opening
    for tf in (T_JUMP, T_OPEN):
        if tf <= t < tf + 0.25:
            a = int(160 * (1 - (t - tf) / 0.25))
            frame.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, a)))
    # fade to/from black
    fb = max(1 - t / 0.4, (t - (DUR - 0.5)) / 0.5)
    if fb > 0:
        frame.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * clamp(fb)))))
    return frame.convert("RGB")


# ---------- audio ----------
def make_audio(path, sr=44100):
    n = int(DUR * sr)
    t = np.arange(n) / sr
    rng = np.random.default_rng(1)
    noise = rng.standard_normal(n)

    def lowpass(x, a):
        y = np.empty_like(x); acc = 0.0
        for k in range(len(x)):  # simple one-pole
            acc += a * (x[k] - acc); y[k] = acc
        return y

    # one-pole via cumulative filter (vectorized with scipy-free trick: use np.frompyfunc is slow) -> use FFT filter
    def fft_band(x, lo, hi):
        X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / sr)
        X[(f < lo) | (f > hi)] = 0
        return np.fft.irfft(X, len(x))

    rumble = fft_band(noise, 30, 400)
    rumble /= np.abs(rumble).max()
    chop = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 11 * t)) * np.exp(-((t * 11) % 1) * 3)
    heli_env = np.clip(1 - (t - T_JUMP) / 2.5, 0, 1) * np.clip(t / 0.8, 0, 1)
    heli = rumble * chop * heli_env * 0.8

    wind = fft_band(noise, 200, 3500); wind /= np.abs(wind).max()
    wind_env = np.clip((t - T_JUMP) / 2.0, 0, 1) * np.where(t < T_OPEN, 1.0, np.clip(1 - (t - T_OPEN) / 0.6, 0.18, 1))
    wind_env *= np.where(t > T_LAND, np.clip(1 - (t - T_LAND) / 0.5, 0, 1), 1)
    whoosh = 0.7 + 0.3 * np.sin(2 * np.pi * 0.7 * t)
    wind = wind * wind_env * whoosh * 0.55

    # canopy pop
    pop = np.zeros(n)
    s = int(T_OPEN * sr); L = int(0.5 * sr)
    pop[s:s + L] = fft_band(noise, 40, 1200)[s:s + L] * np.exp(-np.arange(L) / sr * 9)
    pop /= max(1e-9, np.abs(pop).max()); pop *= 0.9

    # simple happy melody at the landing
    mel = np.zeros(n)
    notes = [523.25, 659.25, 783.99, 1046.5]
    for j, fq in enumerate(notes):
        s = int((T_LAND + 0.1 + j * 0.16) * sr); L = int(0.45 * sr)
        tt = np.arange(L) / sr
        seg = (np.sin(2 * np.pi * fq * tt) + 0.3 * np.sin(4 * np.pi * fq * tt)) * np.exp(-tt * 5) * 0.35
        e = min(n, s + L); mel[s:e] += seg[:e - s]

    mix = heli + wind + pop + mel
    fade = np.clip((DUR - t) / 0.5, 0, 1) * np.clip(t / 0.3, 0, 1)
    mix *= fade
    mix /= max(1e-9, np.abs(mix).max()) / 0.9
    pcm = (mix * 32767).astype(np.int16)
    stereo = np.stack([pcm, pcm], axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(stereo.tobytes())


def main():
    wav = OUT + ".wav"
    make_audio(wav)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT],
                          stdin=subprocess.PIPE)
    for i in range(N):
        ff.stdin.write(render(i).tobytes())
        if i % 60 == 0: print(f"frame {i}/{N}", flush=True)
    ff.stdin.close(); ff.wait()
    os.remove(wav)
    print("wrote", OUT)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "--stills":
        for s in [1.0, 2.6, 4.0, 6.5, 10.3, 12.0, 14.0, 15.3]:
            render(int(s * FPS)).resize((360, 640)).save(f"{OUT}_{s}.jpg")
    else:
        main()
