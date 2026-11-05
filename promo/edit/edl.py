"""TEAM MOSHE promo v9 - Edit Decision List (the "project file").

Brief v4: cinematic slow-mo opening; fight footage from DIFFERENT competitions (no knockdowns at all,
only ONE pad-work shot); coach section; emotional run of hand-raises from different events; logo.

Fighter identity (confirmed by Or / verified frame by frame):
  GFN broadcast (v29025...mp4) + IMG_7997 ringside: Or = dark curly hair, BLUE gloves (opponent blond, red gloves)
  European Championship (RPReplay_1676472639): Or = red headgear, black shorts; flying knee + punch 13.2-13.5
  The World Games (RPReplay_1657863961 / _1658089749 fights, _1687870451 / _1687870418 raises): Or = blue
  World Championship (RPReplay_1634644693): Or = black/orange shorts
  C7925: Or = red shorts, hand raised
Removed per Or's request: every knockdown/fall (GFN 26.6+, 30.8+, 38.4+; IMG_7997 46.5+).
GFN cuts stop before 26.6 and 30.8 so no fall is ever on screen.

v5 (Or's notes): first shot (hand wraps) removed - the film opens on the look; music trimmed by the
same 1.5 s so every cue stays in sync; fight cuts rebuilt so each strike is seen through impact + reaction,
with short interpolated slow-motion on the biggest hits; all captions in Hebrew.

v6 (Or's notes): the seated locker-room shot is gone - the film opens on the arena shot; score trimmed by
another 1.25 s (offset 2.75) so all cues stay in sync. Every strike was re-checked frame by frame and each
shot now runs until the strike has landed (ends moved past the impact; opponent strikes and camera switches cut).

v7 (Or's notes): longer fight shots (1.2-2.4 s each, strike + follow-up + reaction); 3rd clip replaced with
the GFN pressure sequence; all pad work, the World Games clinch (red-helmet opponent) and non-action ring
moments removed; new footage (GFN press + body kick, Euro attack sequence, 2nd Euro angle); six photos from
the Drive folder with slow camera moves. Opening unchanged (arena shot).

Timeline 46.25 s, 30 fps, 1080x1920, 120 BPM (beat 0.5 s, bar 2 s).
Shot = (timeline_start, duration, source, source_in, speed, crop[, hit_src_time])
"""

FPS = 30
W, H = 1080, 1920
DURATION = 50.25
MUSIC_OFFSET = 2.75
MUSIC_INSERT = (16.0, 4.0)   # two extra bars of the fight groove (picture 13.25) -> GFN shots get more time       # the score keeps its original timing; the first 1.5 s are trimmed

def win(x):                    # 16:9 1080p source -> 9:16 window (never stretched)
    return {"type": "win", "x": x}
def zoom(z, cx=0.5, cy=0.5):   # portrait 4K source -> punch-in
    return {"type": "zoom", "z": z, "cx": cx, "cy": cy}
def rect(x, y, w, h):          # 9:16 crop rectangle (display coords) -> full frame
    return {"type": "rect", "x": x, "y": y, "w": w, "h": h}
def photo(file, mode="full", cx=0.5, cy=0.5, z0=1.0, z1=1.08):   # still image with a slow camera move
    return {"type": "photo", "file": file, "mode": mode, "cx": cx, "cy": cy, "z0": z0, "z1": z1}
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
    # ---- 0-1.25 OPEN: the arena shot (unchanged) ----------------------------------------------------
    (0.00, 1.25, "IMG_7991.MOV", 88.10, 0.5, zoom(1.25, 0.48, 0.42)),  # arena lights | אור משה

    # ---- 1.25-22.25 FIGHTS: GFN shots extended; Euro + World Games kept ----------------------------
    (1.25, 0.50, EU,   12.72, 1.0, panel(640, 40, 820, 820)),          # DROP - Euro: Or takes off...
    (1.75, 1.10, EU,   13.22, 0.4, panel(660, 40, 820, 820), 13.30),   # ...flying knee + punch land (slow-mo)
    (2.85, 1.52, GFN,  29.58, 1.0, BC, 30.40),                         # GFN: right hand lands, Or drives him to the ropes (ends before any fall)
    (4.37, 1.00, WGF2,  0.00, 0.9, panel(450, 60, 1100, 828)),       # World Games: Or (blue) attacks | אלוף משחקי העולם
    (5.37, 2.75, GFN,   6.15, 1.0, BC, 8.05),                          # GFN (extended): knee, pressure, body kick lands 8.05 | מעל 200 קרבות זירה
    (8.12, 1.55, EU,   13.75, 1.0, rect(760, 0, 500, 888), 14.84),     # Euro: spinning kick lands 14.84
    (9.67, 0.45, GFN,  18.55, 1.0, BC, 18.80),                         # GFN: Or's punch lands
    (10.12, 1.50, GFN, 19.45, 1.0, BC, 20.50),                         # GFN (extended): knee + punch on the ropes, head snaps
    (11.62, 1.63, "PHOTO", 0, 1.0, photo("IMG_8697.JPG", "panel", .55, .45, 1.0, 1.10)),  # photo: Or's straight right (GFN)
    (13.25, 1.85, EU,  10.10, 1.0, panel(560, 140, 860, 660), 10.80),  # Euro attack - punches + kicks
    (15.10, 0.93, EU,   5.35, 1.0, rect(752, 0, 500, 888), 6.12),      # Euro kick lands | פעמיים אלוף אירופה
    (16.03, 0.77, EU,   6.33, 1.0, rect(560, 0, 500, 888)),            # same exchange, 2nd broadcast angle
    (16.80, 0.95, GFN,  1.30, 1.0, BC, 1.55),                          # GFN (extended): Or's high kick + recovery
    (17.75, 1.00, "PHOTO", 0, 1.0, photo("IMG_8711.JPG", "panel", .45, .45, 1.0, 1.10)),  # photo: Or's flying knee (GFN)
    (18.75, 3.50, "IMG_7997.MOV", 32.60, 1.0, zoom(1.8, 0.50, 0.60), 33.20),  # GFN ringside (extended): kicks + exchanges

    # ---- 18.25-30.25 TEAM MOSHE ---------------------------------------------------------------------
    (22.25, 1.00, "IMG_7991.MOV", 98.70, 1.0, zoom(1.2, 0.5, 0.48)),    # מהזירה
    (23.25, 1.00, "D67A6795.MP4", 37.60, 1.0, win(770)),                 # לדור הבא
    (24.25, 1.00, "D67A6791.MP4",  0.60, 1.0, win(660)),
    (25.25, 1.00, "D67A6790.MP4", 11.50, 1.0, win(560)),
    (26.25, 1.00, "PHOTO", 0, 1.0, photo("IMG_0414.JPG", "full", .48, .40, 1.05, 1.14)),  # photo: Or coaching at the club
    (27.25, 0.75, "D67A6791.MP4",  9.85, 1.0, win(560), 10.30),
    (28.00, 0.75, "IMG_1612.MOV", 5.30, 1.0, FULL),
    (28.75, 1.00, "D67A6795.MP4", 30.20, 1.0, win(1120)),
    (29.75, 0.50, "D67A6790.MP4", 13.40, 1.0, win(620)),
    (30.25, 0.50, "IMG_1601.MOV",  2.00, 1.0, FULL),
    (30.75, 0.50, "D67A6791.MP4", 12.90, 1.0, win(720)),
    (31.25, 1.00, "D67A6790.MP4",  2.00, 1.0, win(640)),                 # כאן מגדלים אלופים
    (32.25, 1.00, "IMG_1612.MOV",  7.90, 1.0, FULL),
    (33.25, 1.00, "IMG_7991_small.mov", 0.40, 1.0, FULL),

    # ---- 30.25-41.25 VICTORIES (+ podium and trophy photos) -------------------------------------------
    (34.25, 1.00, EU,   19.35, 0.75, panel(200, 60, 900, 760)),
    (35.25, 1.25, WG451, 1.00, 1.0, panel(250, 268, 780, 520)),
    (36.50, 1.00, "PHOTO", 0, 1.0, photo("54141f8b.jpg", "panel", .45, .50, 1.0, 1.08)),  # photo: gold on the podium
    (37.50, 1.25, "PHOTO", 0, 1.0, photo("f6ef7cb0.jpg", "panel", .45, .50, 1.0, 1.08)),  # photo: WAKO European Championship hand raise
    (38.75, 1.25, WC,    1.90, 1.0, panel(720, 110, 860, 730)),
    (40.00, 2.00, "C7925.mov",     1.15, 0.5, win(560)),                 # ספורטאי השנה
    (42.00, 1.25, "PHOTO", 0, 1.0, photo("b97b8a80.jpg", "full", .50, .42, 1.04, 1.12)),  # photo: Or with the trophy
    (43.25, 2.00, GFN,  63.90, 1.0, BC),                                 # GFN: hand raised -> close-up

    # ---- 41.25-46.25 LOGO ------------------------------------------------------------------------
    (45.25, 5.00, "D67A6795.MP4", 12.00, 1.0, win(656)),
]

DIM = {45.25: 0.6}

def hit_times():
    out = []
    for s in SHOTS:
        if len(s) > 6:
            t0, dur, src, sin, speed, crop, hit = s
            out.append(round(t0 + (hit - sin) / speed, 3))
    return out
