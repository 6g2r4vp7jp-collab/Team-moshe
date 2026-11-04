"""TEAM MOSHE promo v4 - Edit Decision List (the "project file").

Brief v4: cinematic slow-mo opening; fight footage from DIFFERENT competitions (no knockdowns at all,
only ONE pad-work shot); coach section; emotional run of hand-raises from different events; logo.

Fighter identity (confirmed by Or / verified frame by frame):
  GFN broadcast (v29025...mp4) + IMG_7997 ringside: Or = dark curly hair, BLUE gloves (opponent blond, red gloves)
  European Championship (RPReplay_1676472639): Or = red headgear, black shorts
  The World Games (RPReplay_1657863961 / _1658089749 fights, _1687870451 / _1687870418 raises): Or = blue
  World Championship (RPReplay_1634644693): Or = black/orange shorts
  C7925: Or = red shorts, hand raised
Removed per Or's request: every knockdown/fall (GFN 26.6+, 30.8+, 38.4+; IMG_7997 46.5+).
GFN cuts stop before 26.6 and 30.8 so no fall is ever on screen.

Timeline 49.0 s, 30 fps, 1080x1920, 120 BPM (beat 0.5 s, bar 2 s).
Shot = (timeline_start, duration, source, source_in, speed, crop[, hit_src_time])
"""

FPS = 30
W, H = 1080, 1920
DURATION = 49.0

def win(x):                    # 16:9 1080p source -> 9:16 window (never stretched)
    return {"type": "win", "x": x}
def zoom(z, cx=0.5, cy=0.5):   # portrait 4K source -> punch-in
    return {"type": "zoom", "z": z, "cx": cx, "cy": cy}
def rect(x, y, w, h):          # 9:16 crop rectangle (display coords) -> full frame
    return {"type": "rect", "x": x, "y": y, "w": w, "h": h}
def panel(x, y, w, h):         # landscape crop shown full-width over its own blurred fill (keeps the whole action)
    return {"type": "panel", "x": x, "y": y, "w": w, "h": h}

FULL = zoom(1.0)
GFN = "v29025g50000d9jo14nog65hrm6a3nq0.mp4"
BC = rect(25, 90, 525, 934)                    # GFN broadcast minus the channel bug
EU = "RPReplay_Final1676472639.mp4"            # European Championship (content x172..1748, y0..888)
WGF = "RPReplay_Final1657863961.mp4"           # World Games fight (content y134..888)
WGF2 = "RPReplay_Final1658089749.mov"
WG451 = "RPReplay_Final1687870451.mp4"
WG418 = "RPReplay_Final1687870418.mp4"
WC = "RPReplay_Final1634644693.mov"

SHOTS = [
    # ---- 0-4 COLD OPEN: quiet, slow-motion, preparation -> the stare -> the name -----------
    (0.00, 1.50, "IMG_7892.MOV",  2.40, 0.5, zoom(1.3, 0.45, 0.55)),   # hands being wrapped (macro, slow-mo)
    (1.50, 1.25, "IMG_7892.MOV", 13.00, 0.5, zoom(1.4, 0.56, 0.33)),   # the look
    (2.75, 1.25, "IMG_7991.MOV", 88.10, 0.5, zoom(1.25, 0.48, 0.42)),  # arena lights  | OR MOSHE

    # ---- 4-21 FIGHTS: different competitions, synced to the beat ----------------------------
    (4.00, 1.00, GFN,  19.55, 1.0, BC, 19.85),                         # DROP - Or's punches on the ropes
    (5.00, 1.00, EU,   12.95, 1.0, rect(732, 0, 500, 888), 13.33),     # European Champs - head kick
    (6.00, 0.50, "IMG_7997.MOV", 41.30, 1.0, zoom(1.6, 0.45, 0.60)),   # GFN ringside angle
    (6.50, 0.50, GFN,  18.55, 1.0, BC, 18.80),
    (7.00, 1.50, WGF,   3.30, 1.0, panel(560, 134, 1000, 754)),        # World Games | WORLD GAMES CHAMPION
    (8.50, 0.50, GFN,  25.45, 1.0, BC, 25.70),
    (9.00, 1.00, "IMG_7991.MOV", 91.00, 1.0, zoom(1.15, 0.5, 0.5)),    # Or walks to the ring
    (10.0, 0.50, EU,   14.40, 1.0, rect(760, 0, 500, 888), 14.65),
    (10.5, 0.50, GFN,  29.45, 1.0, BC, 29.70),
    (11.0, 1.00, WGF,   0.40, 1.0, panel(420, 134, 1000, 754)),        # World Games exchange
    (12.0, 0.75, "IMG_7970.mov",  5.55, 1.0, zoom(1.45, 0.52, 0.58), 5.95),   # the ONE pad shot
    (12.75, 0.75, GFN,  1.15, 1.0, BC),                                # Or's high kick
    (13.5, 0.50, "IMG_7997.MOV", 43.10, 1.0, zoom(1.6, 0.47, 0.60)),
    (14.0, 1.00, EU,    5.50, 1.0, rect(752, 0, 500, 888), 5.85),      # Euro kick | 2X EUROPEAN CHAMPION
    (15.0, 0.50, GFN,  14.55, 1.0, BC, 14.75),
    (15.5, 0.50, "IMG_7997.MOV", 36.00, 1.0, zoom(1.5, 0.50, 0.62)),
    (16.0, 1.00, WGF,  12.40, 1.0, panel(520, 134, 1000, 754)),        # World Games exchange
    (17.0, 0.50, GFN,  29.95, 1.0, BC, 30.20),
    (17.5, 0.50, "IMG_7997.MOV", 38.20, 1.0, zoom(1.5, 0.50, 0.62)),
    (18.0, 1.00, GFN,  25.60, 1.0, BC, 26.20),                         # ends at 26.6 - before any fall
    (19.0, 0.50, "IMG_7997.MOV", 27.40, 1.0, zoom(1.5, 0.50, 0.62)),
    (19.5, 0.50, GFN,  14.95, 1.0, BC, 15.10),
    (20.0, 1.00, "IMG_7997.MOV", 29.60, 0.5, zoom(1.5, 0.50, 0.62)),   # slow-mo exchange (speed ramp feel)

    # ---- 21-33 TEAM MOSHE: from the ring to the next generation -----------------------------
    (21.0, 1.00, "IMG_7991.MOV", 98.70, 1.0, zoom(1.2, 0.5, 0.48)),    # FROM THE RING
    (22.0, 1.00, "D67A6795.MP4", 37.60, 1.0, win(770)),                 # TO THE NEXT GENERATION
    (23.0, 1.00, "D67A6791.MP4",  0.60, 1.0, win(660)),
    (24.0, 1.00, "D67A6790.MP4", 11.50, 1.0, win(560)),
    (25.0, 1.00, "D67A6795.MP4", 40.00, 1.0, win(900)),
    (26.0, 0.75, "D67A6791.MP4",  9.85, 1.0, win(560), 10.30),
    (26.75, 0.75, "IMG_1612.MOV", 5.30, 1.0, FULL),
    (27.5, 1.00, "D67A6795.MP4", 30.20, 1.0, win(1120)),
    (28.5, 0.50, "D67A6790.MP4", 13.40, 1.0, win(620)),
    (29.0, 0.50, "IMG_1601.MOV",  2.00, 1.0, FULL),
    (29.5, 0.50, "D67A6791.MP4", 12.90, 1.0, win(720)),
    (30.0, 1.00, "D67A6790.MP4",  2.00, 1.0, win(640)),
    (31.0, 1.00, "IMG_1612.MOV",  7.90, 1.0, FULL),
    (32.0, 1.00, "IMG_7991_small.mov", 0.40, 1.0, FULL),                # walkout smoke -> victories

    # ---- 33-44 VICTORIES: the referee raises Or's hand, event after event --------------------
    (33.0, 1.00, EU,   19.35, 0.75, panel(200, 60, 900, 760)),         # European Championship
    (34.0, 1.50, WG451, 1.00, 1.0, panel(250, 268, 780, 520)),         # The World Games
    (35.5, 1.50, WG418, 1.40, 1.0, panel(230, 280, 780, 510)),         # The World Games (with the flag)
    (37.0, 1.50, WC,    1.90, 1.0, panel(720, 110, 860, 730)),         # World Championship
    (38.5, 2.00, "C7925.mov",     1.15, 0.5, win(560)),                 # hand raised, slow-mo
    (40.5, 3.50, GFN,  63.30, 1.0, BC),                                 # GFN arena: raise -> close-up

    # ---- 44-49 LOGO ----------------------------------------------------------------------------
    (44.0, 5.00, "D67A6795.MP4", 12.00, 1.0, win(656)),                 # the club, under the logo
]

DIM = {44.0: 0.6}

def hit_times():
    out = []
    for s in SHOTS:
        if len(s) > 6:
            t0, dur, src, sin, speed, crop, hit = s
            out.append(round(t0 + (hit - sin) / speed, 3))
    return out
