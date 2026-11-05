"""Cinematic skydive video v2 – drawn bodies in jumpsuits + real faces, multiple camera angles.

python3 cinematic.py out.mp4            # full render
python3 cinematic.py out --stills t1,t2 # preview frames
"""
import math, os, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
rng = np.random.default_rng(3)
random.seed(3)

# shot boundaries (s)
SHOTS = [("cabin", 0.0, 3.2), ("door", 3.2, 5.0), ("jump", 5.0, 7.6), ("front", 7.6, 11.0),
         ("wide", 11.0, 13.0), ("chute", 13.0, 15.6), ("glide", 15.6, 19.0)]
DUR = SHOTS[-1][2]


def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t


# ------------------------------------------------------------------ noise / textures
def fbm(h, w, octaves=6, base=4, seed=0, persistence=0.55):
    r = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32); amp, tot = 1.0, 0.0
    for o in range(octaves):
        gh, gw = base * 2 ** o, int(base * 2 ** o * w / h) + 1
        g = Image.fromarray((r.random((gh + 1, gw + 1)) * 255).astype(np.uint8))
        out += np.asarray(g.resize((w, h), Image.BICUBIC), np.float32) / 255 * amp
        tot += amp; amp *= persistence
    return out / tot


def sky_bg(top, mid, bottom, sun=(0.75, 0.25), sun_col=(255, 230, 180), sun_str=0.9):
    y = np.linspace(0, 1, H)[:, None, None]
    top, mid, bottom = (np.array(c, np.float32) for c in (top, mid, bottom))
    col = np.where(y < 0.6, top + (mid - top) * (y / 0.6), mid + (bottom - mid) * ((y - 0.6) / 0.4))
    col = np.repeat(col, W, axis=1)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot(xx / W - sun[0], (yy / H - sun[1]) * H / W)
    glow = (np.exp(-d * 5) * sun_str + np.exp(-d * 40) * 1.2)[..., None]
    col = col + (np.array(sun_col, np.float32) - col) * np.clip(glow, 0, 1)
    return np.clip(col, 0, 255)


# A big cloud texture used for the "sea of clouds" perspective plane
CLOUD_TEX = fbm(1024, 2048, octaves=7, base=3, seed=11)
CLOUD_TEX = np.clip((CLOUD_TEX - 0.38) * 3.2, 0, 1)
DETAIL_TEX = fbm(1024, 2048, octaves=5, base=12, seed=12)


def cloud_sea(base_rgb, horizon, travel, look_x=0.0, sun=(0.75, 0.25), tint=(255, 245, 235), shade=(150, 165, 195)):
    """Perspective plane of clouds below the horizon. base_rgb: HxWx3 float sky. travel: forward offset."""
    img = base_rgb.copy()
    ys = np.arange(int(horizon) + 1, H)
    if len(ys) == 0: return img
    z = 260.0 / (ys - horizon + 1e-3)                    # depth per row
    xs = (np.arange(W) - W / 2)[None, :] / W
    u = ((xs * z[:, None] * 900 + look_x * 400) % 2048).astype(np.int32) % 2048
    v = (((z[:, None] * 180 + travel) % 1024).astype(np.int32) % 1024) * np.ones_like(u)
    dens = CLOUD_TEX[v, u]
    det = DETAIL_TEX[v, u]
    # lighting: sample texture slightly toward the sun to fake self-shadowing
    v2 = ((v - 6) % 1024)
    light = np.clip(dens - CLOUD_TEX[v2, (u + 8) % 2048] + 0.6, 0, 1)
    col = (np.array(shade, np.float32)[None, None] * (1 - light[..., None]) +
           np.array(tint, np.float32)[None, None] * light[..., None])
    col *= (0.88 + 0.24 * det[..., None])
    # atmospheric haze toward horizon
    haze = np.clip(np.exp(-(ys - horizon) / 260.0), 0, 1)[:, None, None]
    alpha = np.clip(dens * 1.3, 0, 1)[..., None] * (0.55 + 0.45 * (1 - haze))
    hazec = img[int(horizon) + 1:]
    col = col * (1 - haze * 0.75) + hazec * haze * 0.75
    img[int(horizon) + 1:] = hazec * (1 - alpha) + col * alpha
    # fill the gaps between clouds with a deep blue/green "far below" tone
    gap = (1 - alpha) * (1 - haze)
    img[int(horizon) + 1:] = img[int(horizon) + 1:] * (1 - gap * 0.35) + np.array([70, 105, 140], np.float32) * gap * 0.35
    return img


def make_puff(w, h, seed):
    n = fbm(h, w, octaves=6, base=3, seed=seed)
    yy, xx = np.mgrid[0:h, 0:w]
    fall = 1 - np.clip(np.hypot((xx - w / 2) / (w / 2), (yy - h * 0.55) / (h / 2)), 0, 1)
    a = np.clip((n * fall * 2.6 - 0.35) * 2.2, 0, 1)
    shade = np.clip(0.55 + (1 - yy / h) * 0.55 + (n - 0.5), 0, 1)
    rgb = np.stack([lerp(150, 255, shade), lerp(160, 250, shade), lerp(190, 245, shade)], -1)
    return Image.fromarray(np.dstack([rgb, a * 255]).astype(np.uint8), "RGBA")

PUFFS = [make_puff(700, 420, 30 + i) for i in range(6)]
# vertically motion-blurred versions for the freefall shot
def vblur(im, k):
    a = np.asarray(im, np.float32)
    acc = np.zeros_like(a)
    for s in range(k):
        acc += np.roll(a, s * 6, axis=0)
    return Image.fromarray((acc / k).astype(np.uint8), "RGBA")
PUFFS_BLUR = [vblur(p, 14) for p in PUFFS]


# ------------------------------------------------------------------ faces
def load_face(path):
    return Image.open(os.path.join(HERE, path)).convert("RGB")

FACE_DAD = load_face("assets_face_dad.png")
FACE_BABY = load_face("assets_face_baby.png")


def wind_warp(img, t, amp):
    """Cheeks/skin rippling in the wind: horizontal sinusoidal displacement, stronger toward the bottom."""
    if amp <= 0: return img
    a = np.asarray(img)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    k = (yy / h) ** 1.5
    dx = amp * k * np.sin(yy * 0.09 + t * 38) * (0.5 + 0.5 * np.sin(xx * 0.05 + t * 21))
    dy = amp * 0.4 * k * np.sin(xx * 0.07 + t * 33)
    sx = np.clip((xx + dx).astype(np.int32), 0, w - 1)
    sy = np.clip((yy + dy).astype(np.int32), 0, h - 1)
    return Image.fromarray(a[sy, sx])


# ------------------------------------------------------------------ character rig
POSES = {
    "stand": dict(sh=(0.95, -1.55), el=(1.25, -0.35), ha=(0.75, 0.45), hi=(0.5, 1.35), kn=(0.55, 2.9), ft=(0.6, 4.4),
                  bsh=(0.55, 0.05), bha=(0.75, 0.75), bkn=(0.32, 1.65)),
    "arch": dict(sh=(0.95, -1.45), el=(2.05, -2.0), ha=(2.35, -2.95), hi=(0.55, 1.35), kn=(1.35, 2.25), ft=(0.95, 3.05),
                 bsh=(0.55, 0.05), bha=(1.2, -0.45), bkn=(0.55, 1.45)),
    "hang": dict(sh=(0.95, -1.45), el=(1.35, -2.6), ha=(1.0, -3.55), hi=(0.5, 1.35), kn=(0.62, 2.8), ft=(0.5, 4.25),
                 bsh=(0.55, 0.05), bha=(0.95, 0.15), bkn=(0.3, 1.7)),
}

SUIT = (30, 32, 40); SUIT_HI = (55, 58, 70); RED = (205, 35, 45); STRAP = (62, 64, 72)
PINK = (238, 150, 180); PINK_D = (205, 110, 145); HOOD = (250, 190, 210)


def blend_pose(a, b, t):
    pa, pb = POSES[a], POSES[b]
    return {k: (lerp(pa[k][0], pb[k][0], t), lerp(pa[k][1], pb[k][1], t)) for k in pa}


def draw_rig(pose, t, scale, flutter=0.0, face_wind=0.0, ss=2):
    """Returns RGBA image of dad+baby; anchor = torso centre at image centre. scale = px per unit."""
    u = scale * ss
    cw, ch = int(7.2 * u), int(9.6 * u)
    ox, oy = cw / 2, ch * 0.45
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def P(x, y): return (ox + x * u, oy + y * u)
    def j(key, side): x, y = pose[key]; return (side * x, y)
    fl = lambda ph, f=13.0: flutter * math.sin(t * f + ph)

    def limb(a, b, wdt, col):
        d.line([P(*a), P(*b)], fill=col, width=int(wdt * u))
        r = wdt * u / 2
        for q in (a, b):
            x, y = P(*q); d.ellipse([x - r, y - r, x + r, y + r], fill=col)

    def ripple(a, b, wdt, ph):
        # flapping fabric along the limb (wind)
        if flutter <= 0: return
        ax, ay = P(*a); bx, by = P(*b)
        L = math.hypot(bx - ax, by - ay) + 1e-6
        nx, ny = -(by - ay) / L, (bx - ax) / L
        for k in range(4):
            s = ((k + 0.5) / 4 + 0.08 * math.sin(t * 27 + k + ph)) % 1
            cx, cy = ax + (bx - ax) * s, ay + (by - ay) * s
            hw = wdt * u * 0.42
            bend = wdt * u * 0.25 * math.sin(t * 33 + k * 2.1 + ph) * min(1, flutter * 5)
            d.line([(cx - nx * hw, cy - ny * hw), (cx + (bx - ax) / L * bend, cy + (by - ay) / L * bend), (cx + nx * hw, cy + ny * hw)],
                   fill=SUIT_HI, width=max(2, int(0.05 * u)))
        return
        ax, ay = P(*a); bx, by = P(*b)
        L = math.hypot(bx - ax, by - ay) + 1e-6
        nx, ny = -(by - ay) / L, (bx - ax) / L
        for k in range(5):
            s = (k + 0.5) / 5
            cx, cy = ax + (bx - ax) * s, ay + (by - ay) * s
            amp = wdt * u * (0.25 + 0.35 * abs(math.sin(t * 31 + k * 1.7 + ph))) * min(1, flutter * 6)
            side = 1 if k % 2 else -1
            tip = (cx + nx * side * (wdt * u / 2 + amp), cy + ny * side * (wdt * u / 2 + amp))
            d.polygon([(cx - (bx - ax) / L * 14 * ss, cy - (by - ay) / L * 14 * ss), tip,
                       (cx + (bx - ax) / L * 14 * ss, cy + (by - ay) / L * 14 * ss)], fill=SUIT)

    # ---- dad legs
    for s in (-1, 1):
        hi, kn, ft = j("hi", s), j("kn", s), j("ft", s)
        kn = (kn[0] + fl(s, 9) * 0.6, kn[1] + fl(s * 2, 11) * 0.4)
        limb(hi, kn, 0.78, SUIT); limb(kn, ft, 0.62, SUIT)
        ripple(hi, kn, 0.78, s); ripple(kn, ft, 0.62, s + 1)
        d.line([P(hi[0] + s * 0.28, hi[1]), P(kn[0] + s * 0.25, kn[1])], fill=RED, width=int(0.12 * u))
        fx, fy = P(*ft); r = 0.36 * u
        d.ellipse([fx - r, fy - r * 0.8, fx + r, fy + r * 0.8], fill=(18, 18, 22))
    # ---- torso
    pts = [(-1.08, -1.6), (1.08, -1.6), (0.88, 0.35), (0.72, 1.55), (-0.72, 1.55), (-0.88, 0.35)]
    d.polygon([P(x, y) for x, y in pts], fill=SUIT)
    d.polygon([P(-1.0, -1.55), P(-0.2, -1.55), P(0, -0.3), P(0.2, -1.55), P(1.0, -1.55), P(0.75, -1.1), P(0, 0.2), P(-0.75, -1.1)], fill=RED)
    # ---- dad arms
    for s in (-1, 1):
        sh, el, ha = j("sh", s), j("el", s), j("ha", s)
        el = (el[0] + fl(s, 12) * 0.5, el[1] + fl(s + 1, 10) * 0.5)
        ha = (ha[0] + fl(s + 2, 14) * 0.6, ha[1] + fl(s + 3, 9) * 0.6)
        limb(sh, el, 0.62, SUIT); limb(el, ha, 0.5, SUIT)
        ripple(sh, el, 0.62, s * 3); ripple(el, ha, 0.5, s * 5)
        d.line([P(sh[0] + 0.05 * s, sh[1] - 0.18), P(el[0], el[1] - 0.18)], fill=RED, width=int(0.11 * u))
        hx, hy = P(*ha); r = 0.3 * u
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(15, 15, 18))
    # ---- container (backpack edges) & harness
    for s in (-1, 1):
        d.line([P(s * 0.82, -1.62), P(s * 0.62, -0.05)], fill=STRAP, width=int(0.17 * u))
        d.line([P(s * 0.62, 1.2), P(s * 0.25, 1.75)], fill=STRAP, width=int(0.17 * u))
    # ---- baby
    bsh = pose["bsh"]; bha = pose["bha"]; bkn = pose["bkn"]
    by0 = 0.25
    for s in (-1, 1):
        k = (s * bkn[0] + fl(s, 15) * 0.25, by0 + bkn[1])
        limb((s * 0.3, by0 + 0.75), k, 0.36, PINK)
        kx, ky = P(*k); r = 0.2 * u
        d.ellipse([kx - r, ky - r, kx + r, ky + r * 1.2], fill=(250, 245, 245))
    d.ellipse([P(-0.72, by0 - 0.55)[0], P(0, by0 - 0.55)[1], P(0.72, 0)[0], P(0, by0 + 1.05)[1]], fill=PINK)
    for q in range(3):  # quilting lines of the padded suit
        yq = by0 - 0.2 + q * 0.38
        d.arc([P(-0.62, yq - 0.2)[0], P(0, yq - 0.2)[1], P(0.62, 0)[0], P(0, yq + 0.25)[1]], 20, 160, fill=PINK_D, width=int(0.04 * u))
    for s in (-1, 1):
        h2 = (s * bha[0] + fl(s + 4, 16) * 0.3, by0 + bha[1] + fl(s, 12) * 0.2)
        limb((s * bsh[0], by0 + bsh[1] - 0.2), h2, 0.32, PINK)
        hx, hy = P(*h2); r = 0.17 * u
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(245, 205, 185))
    # harness straps over the baby (tandem baby carrier)
    for s in (-1, 1):
        d.line([P(s * 0.85, -1.5), P(s * 0.45, by0 + 0.2)], fill=STRAP, width=int(0.16 * u))
    d.line([P(-0.75, by0 + 0.2), P(0.75, by0 + 0.2)], fill=STRAP, width=int(0.16 * u))
    d.line([P(-0.68, by0 + 0.9), P(0.68, by0 + 0.9)], fill=STRAP, width=int(0.16 * u))
    for x0 in (0.0,):
        bx, byy = P(x0, by0 + 0.2); r = 0.13 * u
        d.rounded_rectangle([bx - r * 1.4, byy - r, bx + r * 1.4, byy + r], radius=r * 0.4, fill=(200, 200, 210))

    # ---- shading on the body (light from upper right) + warm rim
    a = np.asarray(im, np.float32)
    yy, xx = np.mgrid[0:ch, 0:cw]
    light = 0.72 + 0.5 * np.clip((xx / cw) * 0.6 + (1 - yy / ch) * 0.6, 0, 1)
    a[..., :3] *= light[..., None]
    alpha = a[..., 3]
    sh = max(1, int(0.03 * u))
    rim = np.clip(alpha - np.roll(np.roll(alpha, sh, 1), -sh, 0), 0, 255)[..., None] / 255
    a[..., :3] = a[..., :3] * (1 - rim * 0.3) + np.array([255, 215, 160]) * rim * 0.3
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(im)

    # ---- heads
    def head(cx, cy, r, shell, open_rx, open_ry, face, warp, goggles):
        X, Y = P(cx, cy); R = r * u
        # shell with gloss
        d.ellipse([X - R, Y - R, X + R, Y + R], fill=shell)
        hl = tuple(min(255, c + 70) for c in shell)
        d.arc([X - R * 0.8, Y - R * 0.85, X + R * 0.75, Y + R * 0.6], 200, 260, fill=hl, width=int(R * 0.12))
        orx, ory = open_rx * u, open_ry * u
        oy_ = Y + R * 0.12
        fw, fh = int(orx * 2.0), int(ory * 2.0)
        f = wind_warp(face.resize((fw, fh), Image.LANCZOS), t, warp * fw / 100)
        m = Image.new("L", (fw, fh), 0)
        ImageDraw.Draw(m).ellipse([2, 2, fw - 2, fh - 2], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(max(1, fw / 60)))
        im.paste(f, (int(X - fw / 2), int(oy_ - fh / 2)), m)
        # inner shadow of the opening
        d.ellipse([X - orx, oy_ - ory, X + orx, oy_ + ory], outline=tuple(int(c * 0.6) for c in shell), width=max(2, int(R * 0.05)))
        if goggles:
            gy = Y - R * 0.68
            d.rounded_rectangle([X - R * 0.62, gy - R * 0.17, X + R * 0.62, gy + R * 0.17], radius=R * 0.15,
                                fill=(90, 160, 200), outline=(20, 20, 20), width=max(2, int(R * 0.05)))
            d.line([X - R * 0.45, gy - R * 0.08, X - R * 0.1, gy - R * 0.08], fill=(230, 245, 255), width=max(2, int(R * 0.05)))
    head(0, -2.45, 1.02, (25, 25, 30), 0.64, 0.8, FACE_DAD, face_wind, True)
    # baby: soft pink hood with ear protectors
    bx, byy = P(0, by0 - 1.05); R = 0.66 * u
    for s in (-1, 1):
        ex = bx + s * R * 0.92; r = R * 0.3
        d.ellipse([ex - r, byy - r, ex + r, byy + r], fill=(245, 245, 250), outline=(200, 200, 210), width=max(2, int(r * 0.12)))
    head(0, by0 - 1.05, 0.66, HOOD, 0.5, 0.58, FACE_BABY, face_wind * 0.8, False)

    return im.resize((cw // ss, ch // ss), Image.LANCZOS), (ox / ss, oy / ss)


def paste(base, im, x, y, anchor=None, rot=0.0, alpha=1.0):
    """paste rig so that its anchor (default centre) lands at (x, y)."""
    if anchor is None: anchor = (im.width / 2, im.height / 2)
    if rot:
        # rotate around anchor
        big = Image.new("RGBA", (im.width * 2, im.height * 2), (0, 0, 0, 0))
        big.paste(im, (int(im.width - anchor[0]), int(im.height - anchor[1])))
        im = big.rotate(rot, resample=Image.BICUBIC); anchor = (im.width / 2, im.height / 2)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    base.alpha_composite(im, (int(x - anchor[0]), int(y - anchor[1])))


# ------------------------------------------------------------------ props
def plane_side(scale, door_open=True, prop_phase=0.0):
    w, h = int(1400 * scale), int(520 * scale)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    S = lambda x, y: (x * scale, y * scale)
    white, grey = (236, 238, 242), (175, 180, 190)
    d.polygon([S(1080, 210), S(1360, 40), S(1390, 40), S(1330, 250)], fill=white)            # tail fin
    d.polygon([S(1150, 230), S(1390, 225), S(1390, 255), S(1150, 265)], fill=grey)          # stabilizer
    d.rounded_rectangle([S(120, 170)[0], S(0, 170)[1], S(1250, 0)[0], S(0, 330)[1]], radius=80 * scale, fill=white)
    d.polygon([S(1050, 175), S(1300, 210), S(1300, 280), S(1050, 330)], fill=white)
    d.ellipse([S(60, 175)[0], S(0, 175)[1], S(260, 0)[0], S(0, 330)[1]], fill=white)
    d.rectangle([S(140, 300)[0], S(0, 300)[1], S(1200, 0)[0], S(0, 312)[1]], fill=(30, 80, 160))   # stripe
    for i in range(7):
        x = 330 + i * 80
        d.rounded_rectangle([S(x, 205)[0], S(0, 205)[1], S(x + 42, 0)[0], S(0, 245)[1]], radius=10 * scale, fill=(60, 90, 120))
    d.polygon([S(110, 200), S(185, 190), S(185, 240), S(95, 240)], fill=(60, 90, 120))      # cockpit glass
    if door_open:
        d.rectangle([S(880, 190)[0], S(0, 190)[1], S(990, 0)[0], S(0, 318)[1]], fill=(12, 12, 16))
    d.polygon([S(430, 262), S(820, 262), S(800, 292), S(450, 292)], fill=grey)             # wing (side view)
    d.ellipse([S(560, 280)[0], S(0, 280)[1], S(660, 0)[0], S(0, 318)[1]], fill=(150, 155, 165))  # wing strut fairing
    d.line([S(140, 330), S(150, 400)], fill=(60, 60, 60), width=max(2, int(10 * scale)))
    d.ellipse([S(120, 390)[0], S(0, 390)[1], S(180, 0)[0], S(0, 430)[1]], fill=(25, 25, 25))
    pr = 160 * scale * abs(math.cos(prop_phase))
    d.ellipse([S(55, 250)[0] - 12 * scale, S(0, 250)[1] - 170 * scale, S(55, 0)[0] + 12 * scale, S(0, 250)[1] + 170 * scale], fill=(80, 80, 90, 60))
    d.line([S(55, 250)[0], S(0, 250)[1] - pr, S(55, 0)[0], S(0, 250)[1] + pr], fill=(40, 40, 40), width=max(2, int(9 * scale)))
    return im


def canopy(open_t, scale, t):
    """Ram-air canopy seen from slightly below/front. Returns image + (x, y) where lines meet (riser point)."""
    w, h = int(1500 * scale), int(1300 * scale)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    o = ease(open_t)
    span = lerp(0.12, 1.0, o); depth = lerp(0.3, 1.0, o)
    cx, cy = w / 2, 260 * scale + (1 - o) * 500 * scale
    cols = [(230, 50, 60), (250, 150, 30), (250, 215, 40), (60, 180, 110), (40, 140, 230), (130, 70, 200),
            (230, 50, 60), (250, 150, 30), (250, 215, 40)]
    n = len(cols)
    R = 700 * scale * span
    breathe = 1 + 0.015 * math.sin(t * 7) * o
    def arcpt(a, rr): return (cx + math.sin(a) * rr * breathe, cy + (1 - math.cos(a)) * rr * 0.55 - 0 * scale)
    amax = 1.05
    for i in range(n):
        a0 = -amax + 2 * amax * i / n; a1 = -amax + 2 * amax * (i + 1) / n
        top0, top1 = arcpt(a0, R), arcpt(a1, R)
        th = 150 * scale * depth
        poly = [top0, top1, (top1[0], top1[1] + th), (top0[0], top0[1] + th)]
        d.polygon(poly, fill=cols[i] + (255,))
        # cell openings (dark mouths) on the leading edge
        d.polygon([(top0[0] + 3, top0[1] + th * 0.7), (top1[0] - 3, top1[1] + th * 0.7), (top1[0] - 3, top1[1] + th), (top0[0] + 3, top0[1] + th)],
                  fill=tuple(int(c * 0.55) for c in cols[i]) + (255,))
        d.line([top0, (top0[0], top0[1] + th)], fill=(255, 255, 255, 120), width=max(1, int(3 * scale)))
    # top highlight
    pts = [arcpt(-amax + 2 * amax * k / 40, R) for k in range(41)]
    d.line(pts, fill=(255, 255, 255, 160), width=max(2, int(8 * scale)))
    rx, ry = cx, h - 30 * scale
    for i in range(n + 1):
        a = -amax + 2 * amax * i / n
        p = arcpt(a, R); p = (p[0], p[1] + 150 * scale * depth)
        side = -1 if a < 0 else 1
        d.line([p, (rx + side * 60 * scale, ry)], fill=(240, 240, 240, 170), width=max(1, int(2.5 * scale)))
    return im, (rx, ry)


def landscape(t, cam_y=0.0, horizon=820):
    """Golden hour mountains + lake + coast below the gliding jumpers."""
    sky = sky_bg((70, 110, 175), (245, 185, 140), (255, 210, 160), sun=(0.25, horizon / H - 0.05), sun_col=(255, 225, 170))
    img = sky
    yy = np.arange(H)[:, None]
    xs = np.arange(W)
    layers = [(0.0, 60, (150, 130, 160), 7), (0.25, 120, (110, 105, 140), 8), (0.5, 210, (75, 90, 110), 9)]
    for depth, amp, col, seed in layers:
        r = np.random.default_rng(seed)
        prof = np.zeros(W)
        for o in range(5):
            f = 2 ** o
            ph = r.random() * 6.28
            prof += np.sin(xs / W * 6.28 * f * 1.3 + ph + t * 0.02 * (1 + depth)) / f
        top = horizon - amp * (0.6 + 0.5 * prof) + depth * 120 - cam_y * (0.2 + depth)
        m = (yy > top[None, :]).astype(np.float32)[..., None]
        shade = np.clip((yy - top[None, :]) / 300, 0, 1)[..., None]
        c = np.array(col, np.float32) * (1 - 0.3 * shade)
        img = img * (1 - m) + c * m
    # valley floor with lake and fields
    floor = horizon + 280 - cam_y * 1.2
    ys = np.arange(H)
    rows = ys > floor
    if rows.any():
        z = 200.0 / (ys[rows] - floor + 5)
        uu = ((xs[None, :] - W / 2) * z[:, None] * 2 + 1024 + t * 10) % 2048
        vv = (z[:, None] * 300 + t * 40 + cam_y) % 1024
        vi = vv.astype(int) % 1024; ui = uu.astype(int) % 2048
        n = DETAIL_TEX[vi, ui]
        lake = CLOUD_TEX[vi, (ui + 700) % 2048] > 0.55
        grass = np.stack([lerp(70, 140, n), lerp(110, 170, n), lerp(50, 80, n)], -1)
        water = np.stack([np.full_like(n, 60), lerp(150, 190, n), lerp(170, 210, n)], -1)
        col = np.where(lake[..., None], water, grass)
        haze = np.exp(-(ys[rows] - floor) / 220)[:, None, None]
        col = col * (1 - haze * 0.6) + np.array([235, 190, 160]) * haze * 0.6
        img[rows] = col
    return img


# ------------------------------------------------------------------ text
def title(txt, size, color=(255, 255, 255)):
    f = ImageFont.truetype(FONT, size)
    dd = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = dd.textbbox((0, 0), txt, font=f, direction="rtl", language="he")
    im = Image.new("RGBA", (bb[2] - bb[0] + 60, bb[3] - bb[1] + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((30 - bb[0], 34 - bb[1]), txt, font=f, fill=(0, 0, 0, 170), direction="rtl", language="he")
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(im).text((30 - bb[0], 30 - bb[1]), txt, font=f, fill=color, direction="rtl", language="he")
    return im

T_END1 = title("אבא ואני", 120)
T_END2 = title("הקפיצה הראשונה שלנו", 62, (255, 225, 170))


# ------------------------------------------------------------------ shots
SKY_HIGH = sky_bg((25, 70, 150), (110, 165, 225), (200, 225, 245), sun=(0.8, 0.18))


def shot_cabin(t, T):
    # dark cabin, door on the right, characters walk toward it; camera pushes in
    p = t / T
    img = Image.new("RGBA", (W, H), (18, 20, 26, 255))
    d = ImageDraw.Draw(img)
    # cabin ribs / walls
    for i in range(9):
        x = -200 + i * 170 - p * 120
        d.line([(x, 0), (x + 80, H)], fill=(32, 35, 44), width=26)
    d.rectangle([0, H * 0.78, W, H], fill=(28, 28, 32))
    # open door (bright, with cloud sea rushing by)
    dx0, dx1, dy0, dy1 = 640, 1080, 380, 1500
    sea = cloud_sea(SKY_HIGH.copy(), H * 0.42, travel=t * 260, look_x=t * 0.6)
    door = Image.fromarray(sea.astype(np.uint8)).convert("RGBA").crop((dx0, dy0, dx1, dy1))
    img.paste(door, (dx0, dy0))
    d.rectangle([dx0 - 18, dy0 - 18, dx0, dy1 + 18], fill=(60, 64, 74))
    d.rectangle([dx0 - 18, dy0 - 18, dx1, dy0], fill=(60, 64, 74))
    d.rectangle([dx0 - 18, dy1, dx1, dy1 + 18], fill=(60, 64, 74))
    # light spill from the door onto the floor
    spill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(spill).polygon([(dx0, dy1), (dx1, dy1), (dx1, H), (200, H)], fill=(255, 235, 200, 70))
    img.alpha_composite(spill.filter(ImageFilter.GaussianBlur(40)))
    # characters walking
    rig, anc = draw_rig(POSES["stand"], t, scale=150 + 30 * p, flutter=0.04 + 0.1 * p, face_wind=0.3 * p)
    x = lerp(330, 470, ease(p)); y = 1010 + 18 * abs(math.sin(t * 5.5))
    paste(img, rig, x, y, anc, rot=2 * math.sin(t * 5.5))
    return img, dict(shake=2 + 3 * p, zoom=1.0 + 0.08 * p)


def shot_door(t, T):
    p = t / T
    sea = cloud_sea(SKY_HIGH.copy(), H * 0.5, travel=t * 320 + 900, look_x=1 + t * 0.7)
    img = Image.fromarray(sea.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 170, H], fill=(55, 58, 68)); d.rectangle([0, 0, W, 120], fill=(55, 58, 68))
    rig, anc = draw_rig(blend_pose("stand", "arch", ease((p - 0.75) / 0.25) * 0.3), t, scale=330, flutter=0.12, face_wind=1.2)
    paste(img, rig, W * 0.5 + 20 * math.sin(t * 3), 1420 + 40 * ease(p), anc, rot=4 * math.sin(t * 2))
    # wind streaks blowing in
    for k in range(18):
        r = random.Random(k * 31 + int(t * 30))
        y = r.uniform(0, H); x = r.uniform(0, W)
        d.line([(x, y), (x - r.uniform(80, 220), y + r.uniform(-8, 8))], fill=(255, 255, 255, r.randint(40, 100)), width=2)
    return img, dict(shake=6, zoom=1.0 + 0.05 * p)


def shot_jump(t, T):
    # exterior camera on the wing: plane above-left, jumpers leap out & fall away
    p = t / T
    sea = cloud_sea(SKY_HIGH.copy(), H * 0.62 - 260 * ease(p), travel=t * 300 + 2000, look_x=2 + t * 0.4)
    img = Image.fromarray(sea.astype(np.uint8)).convert("RGBA")
    ps = 0.95
    plane = plane_side(ps, True, t * 50)
    px, py = 60 - 160 * ease(p), 420 - 700 * ease((p - 0.25) / 0.75)
    img.alpha_composite(plane, (int(px), int(py)))
    door_x, door_y = px + 935 * ps, py + 255 * ps
    tj = clamp((p - 0.18) / 0.82)
    if p < 0.18:
        rig, anc = draw_rig(POSES["stand"], t, scale=22, flutter=0.05)
        paste(img, rig, door_x, door_y + 10, anc)
    else:
        pose = blend_pose("stand", "arch", ease(tj / 0.5))
        sc = lerp(22, 120, ease(tj))
        rig, anc = draw_rig(pose, t, scale=sc, flutter=0.15, face_wind=0.6)
        x = lerp(door_x, W * 0.55, ease(tj)) + 40 * math.sin(tj * 6)
        y = lerp(door_y, H * 0.62, ease(tj))
        rot = (1 - ease(tj / 0.6)) * 340 * tj if tj < 0.6 else 8 * math.sin(t * 3)  # one tumble then stable
        paste(img, rig, x, y, anc, rot=rot)
    return img, dict(shake=3 + 6 * tj, zoom=1.0)


def shot_front(t, T, cam_bias=0.0):
    p = t / T
    sky = sky_bg((30, 85, 170), (120, 175, 230), (190, 215, 240), sun=(0.82 + cam_bias, 0.12))
    img = Image.fromarray(sky.astype(np.uint8)).convert("RGBA")
    # clouds rushing upward at several depths
    for k in range(16):
        r = random.Random(k * 7)
        depth = r.uniform(0.35, 1.6)
        speed = 2600 * depth
        y = (r.uniform(0, 4000) - t * speed) % (H + 900) - 600
        x = r.uniform(-400, W - 200) + cam_bias * 600 * depth
        pf = PUFFS_BLUR[k % 6] if depth > 0.7 else PUFFS[k % 6]
        pf = pf.resize((int(pf.width * depth), int(pf.height * depth * (1.6 if depth > 0.7 else 1))))
        if depth > 1.1:
            continue  # near ones are drawn after the rig
        img.alpha_composite(pf, (int(x), int(y)))
    rig, anc = draw_rig(POSES["arch"], t, scale=165, flutter=0.22, face_wind=1.6)
    bob = 25 * math.sin(t * 2.3)
    paste(img, rig, W / 2 + 30 * math.sin(t * 1.4), H * 0.5 + bob, anc, rot=6 * math.sin(t * 1.7))
    for k in range(16):
        r = random.Random(k * 7)
        depth = r.uniform(0.35, 1.6)
        if depth <= 1.1: continue
        y = (r.uniform(0, 4000) - t * 2600 * depth) % (H + 900) - 600
        x = r.uniform(-400, W - 200)
        pf = PUFFS_BLUR[k % 6]
        pf = pf.resize((int(pf.width * depth * 1.3), int(pf.height * depth * 2.2)))
        paste(img, pf, x + pf.width / 2, y + pf.height / 2, alpha=0.4)
    d = ImageDraw.Draw(img)
    for k in range(40):  # speed streaks
        r = random.Random(k * 13 + int(t * FPS))
        x = r.uniform(0, W); y = r.uniform(-300, H)
        d.line([(x, y), (x, y + r.uniform(150, 500))], fill=(255, 255, 255, r.randint(30, 90)), width=r.randint(1, 4))
    # mid-shot: punch in to a face close-up
    zoom = 1.0 + 1.25 * ease((p - 0.62) / 0.2) if p > 0.62 else 1.0
    return img, dict(shake=10, zoom=zoom, zoom_center=(W / 2, H * 0.5 - 2.0 * 165 + bob))


def shot_wide(t, T):
    p = t / T
    sky = sky_bg((35, 70, 150), (215, 150, 130), (230, 170, 140), sun=(0.3, 0.42), sun_col=(255, 220, 160), sun_str=0.7)
    sea = cloud_sea(sky, H * 0.47, travel=t * 120 + 3000, look_x=3 + p * 0.8,
                    tint=(255, 222, 185), shade=(95, 90, 130))
    img = Image.fromarray(sea.astype(np.uint8)).convert("RGBA")
    rig, anc = draw_rig(POSES["arch"], t, scale=lerp(40, 28, p), flutter=0.15)
    paste(img, rig, lerp(W * 0.62, W * 0.42, p), lerp(H * 0.35, H * 0.55, p), anc, rot=lerp(-25, 10, p))
    return img, dict(shake=1.5, zoom=1.0 + 0.1 * p)


def shot_chute(t, T):
    p = t / T
    sky = sky_bg((40, 90, 175), (150, 185, 225), (240, 210, 180), sun=(0.2, 0.15))
    img = Image.fromarray(sky.astype(np.uint8)).convert("RGBA")
    for k in range(6):
        r = random.Random(k * 3 + 5)
        decel = 2400 * math.exp(-max(0, t - 0.2) * 3) + 120
        y = (r.uniform(0, 3000) - (t * decel)) % (H + 700) - 500
        paste(img, PUFFS[k], r.uniform(0, W), y, alpha=0.9)
    open_t = clamp((t - 0.15) / 0.8)
    pose = blend_pose("arch", "hang", ease((t - 0.25) / 0.8))
    rig_sc = lerp(150, 120, ease(open_t))
    rig, anc = draw_rig(pose, t, scale=rig_sc, flutter=lerp(0.2, 0.05, open_t), face_wind=lerp(1.4, 0.3, open_t))
    jolt = -140 * math.exp(-max(0, t - 0.75) * 5) * (t > 0.75)
    rx, ry = W / 2 + 25 * math.sin(t * 1.3), H * 0.67 + jolt
    c, (cx_, cy_) = canopy(open_t, 0.72, t)
    head_top = ry - 3.6 * rig_sc
    paste(img, c, rx, head_top - 30, anchor=(cx_, cy_))
    # risers from canopy to shoulders
    d = ImageDraw.Draw(img)
    for s in (-1, 1):
        d.line([(rx + s * 45, head_top - 30), (rx + s * 0.95 * rig_sc, ry - 1.45 * rig_sc)], fill=(230, 230, 230), width=4)
    paste(img, rig, rx, ry, anc, rot=4 * math.sin(t * 1.8))
    zoom = 1.0
    if p > 0.62:  # close-up on the faces under the canopy
        zoom = 1.0 + 1.1 * ease((p - 0.62) / 0.25)
    return img, dict(shake=8 * math.exp(-t * 1.5) + 1, zoom=zoom, zoom_center=(rx, ry - 1.4 * rig_sc))


def shot_glide(t, T):
    p = t / T
    land = landscape(t, cam_y=p * 120)
    img = Image.fromarray(np.clip(land, 0, 255).astype(np.uint8)).convert("RGBA")
    sc = lerp(70, 34, ease(p))
    rig, anc = draw_rig(POSES["hang"], t, scale=sc, flutter=0.03, face_wind=0.1)
    rx, ry = lerp(W * 0.55, W * 0.5, p) + 20 * math.sin(t), lerp(H * 0.52, H * 0.46, p)
    c, (cx_, cy_) = canopy(1.0, sc / 150 * 0.72, t)
    paste(img, c, rx, ry - 3.6 * sc - 10, anchor=(cx_, cy_))
    d = ImageDraw.Draw(img)
    for s in (-1, 1):
        d.line([(rx + s * 0.3 * sc, ry - 3.6 * sc - 10), (rx + s * 0.95 * sc, ry - 1.45 * sc)], fill=(230, 230, 230), width=2)
    paste(img, rig, rx, ry, anc, rot=3 * math.sin(t * 1.2))
    a = clamp((p - 0.45) / 0.15)
    if a > 0:
        paste(img, T_END1, W / 2, 330, alpha=a)
        paste(img, T_END2, W / 2, 470, alpha=clamp((p - 0.55) / 0.15))
    return img, dict(shake=1.0, zoom=1.0 + 0.05 * (1 - p))


SHOT_FN = dict(cabin=shot_cabin, door=shot_door, jump=shot_jump, front=shot_front, wide=shot_wide, chute=shot_chute, glide=shot_glide)


# ------------------------------------------------------------------ camera + grading
VIGNETTE = None
def grade(img, t):
    global VIGNETTE
    a = np.asarray(img.convert("RGB"), np.float32) / 255
    if VIGNETTE is None:
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
        VIGNETTE = (1 - 0.38 * np.clip(r - 0.45, 0, 1) ** 1.6)[..., None]
    # bloom
    small = img.convert("RGB").resize((W // 8, H // 8), Image.BILINEAR)
    sa = np.asarray(small, np.float32) / 255
    bright = np.clip(sa - 0.8, 0, 1) * 2.0
    bl = Image.fromarray((bright * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
    a = a + np.asarray(bl, np.float32) / 255 * 0.35
    # filmic tone + teal/orange split
    a = a / (1 + a * 0.25) * 1.18
    lum = a.mean(-1, keepdims=True)
    a = a + (np.array([0.04, 0.015, -0.03]) * lum) + (np.array([-0.025, 0.0, 0.03]) * (1 - lum))
    a = (a - 0.5) * 1.08 + 0.5
    a *= VIGNETTE
    grain = rng.normal(0, 0.012, (H // 2, W // 2, 1)).astype(np.float32)
    a += np.repeat(np.repeat(grain, 2, 0), 2, 1)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def camera(img, t, cfg):
    zoom = cfg.get("zoom", 1.0); sh = cfg.get("shake", 0)
    cx, cy = cfg.get("zoom_center", (W / 2, H / 2))
    cx = lerp(W / 2, cx, clamp(zoom - 1)); cy = lerp(H / 2, cy, clamp(zoom - 1))
    jx = sh * (math.sin(t * 23.1) + 0.6 * math.sin(t * 41.7))
    jy = sh * (math.cos(t * 19.3) + 0.6 * math.sin(t * 37.9))
    w, h = W / zoom, H / zoom
    x0 = clamp(cx - w / 2 + jx, 0, W - w); y0 = clamp(cy - h / 2 + jy, 0, H - h)
    if zoom == 1.0 and sh == 0: return img
    return img.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.BICUBIC)


def render(i):
    t = i / FPS
    for k, (name, a, b) in enumerate(SHOTS):
        if a <= t < b or k == len(SHOTS) - 1:
            break
    lt, T = t - a, b - a
    img, cfg = SHOT_FN[name](lt, T)
    img = camera(img, t, cfg)
    img = grade(img, t)
    # transitions: short flash on cuts into action, fade in/out
    if name in ("jump", "chute") and lt < 0.18:
        img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), 0.6 * (1 - lt / 0.18))
    if name in ("door", "front", "wide", "glide") and lt < 0.25:  # quick whip-blur in
        k = int(30 * (1 - lt / 0.25))
        if k > 1:
            img = img.filter(ImageFilter.BoxBlur(k // 2))
    fb = max(1 - t / 0.6, (t - (DUR - 0.8)) / 0.8)
    if fb > 0:
        img = Image.blend(img, Image.new("RGB", (W, H)), clamp(fb))
    return img


# ------------------------------------------------------------------ audio
def make_audio(path, sr=44100):
    n = int(DUR * sr); t = np.arange(n) / sr
    r = np.random.default_rng(5)
    def band(x, lo, hi):
        X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / sr); X[(f < lo) | (f > hi)] = 0
        y = np.fft.irfft(X, len(x)); return y / (np.abs(y).max() + 1e-9)
    def env(a, b, fade=0.3):
        return np.clip((t - a) / fade, 0, 1) * np.clip((b - t) / fade, 0, 1)
    s_door, s_jump, s_front, s_wide, s_chute, s_glide = (SHOTS[k][1] for k in range(1, 7))
    noise = r.standard_normal(n)
    engine = band(noise, 40, 260) * (0.6 + 0.4 * np.sin(2 * np.pi * 38 * t)) * env(0, s_jump + 0.8, 0.5) * 0.5
    engine += np.sin(2 * np.pi * 76 * t) * 0.08 * env(0, s_jump + 0.8, 0.5)
    gust = 0.65 + 0.35 * np.sin(2 * np.pi * 0.9 * t) * np.sin(2 * np.pi * 0.37 * t + 1)
    wind_hi = band(noise, 300, 6000)
    wind_lo = band(r.standard_normal(n), 60, 600)
    wind = (wind_hi * 0.5 + wind_lo * 0.7) * gust
    wind_env = 0.25 * env(0, s_door) + 0.6 * env(s_door, s_jump) + 1.0 * env(s_jump, s_chute + 0.4, 0.4) + \
               0.25 * env(s_chute + 0.4, DUR, 0.6)
    wind *= wind_env * 0.55
    snap = np.zeros(n); k0 = int((s_chute + 0.75) * sr); L = int(0.6 * sr)
    snap[k0:k0 + L] = band(noise, 50, 1500)[k0:k0 + L] * np.exp(-np.arange(L) / sr * 7) * 1.0
    # cinematic music: pad chords + boom hits
    music = np.zeros(n)
    chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (196.0, 246.94, 293.66), (164.81, 207.65, 246.94),
              (220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (261.63, 329.63, 392.0), (196.0, 246.94, 293.66)]
    seg = DUR / len(chords)
    for ci, ch in enumerate(chords):
        a, b = ci * seg, (ci + 1) * seg + 0.6
        e = np.clip((t - a) / 0.8, 0, 1) * np.clip((b - t) / 0.6, 0, 1)
        for f in ch:
            for det in (-0.6, 0.6):
                music += np.sin(2 * np.pi * (f + det) * t + det) * e * 0.05
                music += np.sin(2 * np.pi * (f / 2 + det) * t) * e * 0.03
    def boom(at, amp=1.0):
        k = int(at * sr); L = int(1.2 * sr); tt = np.arange(L) / sr
        x = np.sin(2 * np.pi * (55 * np.exp(-tt * 3) + 30) * tt) * np.exp(-tt * 3.5) * amp
        e = min(n, k + L); music[k:e] += x[:e - k]
    for at in (s_jump + 0.4, s_front, s_chute + 0.75, s_glide):
        boom(at)
    music *= np.clip((t - s_glide) / 1.0, 0, 1) * 0.8 + 0.6
    mix = engine + wind + snap + music
    mix *= np.clip(t / 0.6, 0, 1) * np.clip((DUR - t) / 1.0, 0, 1)
    mix = np.tanh(mix * 1.3); mix /= np.abs(mix).max() / 0.92
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(np.stack([pcm, pcm], 1).tobytes())


def render_bytes(i):
    return render(i).tobytes()


def main(out):
    wav = out + ".wav"; make_audio(wav)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", out],
                          stdin=subprocess.PIPE)
    N = int(DUR * FPS)
    from multiprocessing import Pool
    with Pool(max(1, os.cpu_count() - 1)) as pool:
        for i, fr in enumerate(pool.imap(render_bytes, range(N), chunksize=2)):
            ff.stdin.write(fr)
            if i % 60 == 0: print(f"{i}/{N}", flush=True)
    ff.stdin.close(); ff.wait(); os.remove(wav); print("wrote", out)


if __name__ == "__main__":
    if "--stills" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--stills") + 1].split(",")]
        for s in ts:
            render(int(s * FPS)).resize((360, 640)).save(f"{sys.argv[1]}_{s:05.2f}.jpg")
    else:
        main(sys.argv[1])
