"""TEAM MOSHE promo v3 - Edit Decision List (the "project file").

Story: Or Moshe the FIGHTER (~60%)  ->  Or Moshe the COACH (~30%)  ->  ring climax  ->  logo (~10%).
Every fight shot below was checked frame-by-frame: Or is the one striking / scoring the knockdown.
  GFN broadcast (v29025...mp4): Or = dark curly hair, BLUE gloves; opponent = blond, red gloves.
      KD1 26.8-27.6, KD2 31.1-31.7, KD3 flying knee 38.7 -> opponent down 39.0-39.8, hand raise 63-66.
  IMG_7997: same GFN fight from ringside (4K/60) - KD3 seen from the floor angle.
  RPReplay_1676472202: European Championship - Or = red headgear, black shorts; head kick 2.6-2.8.
  RPReplay_1687870372: The World Games - Or (blue shorts) hand raised.
  RPReplay_1634644693: World Championship - Or (black/orange shorts) hand raised.
Excluded on purpose: opponent's kicks (GFN 0.6-1.0, 4.6, 17.3-18.3, 46.0), the European clinch at 4.3-5.2
(it ends with Or on the floor), and the World Games exchanges where the scoring fighter is not clear.

Timeline 46.0 s, 30 fps, 1080x1920, 120 BPM (beat 0.5 s).
Shot = (timeline_start, duration, source, source_in, speed, crop[, hit_src_time])
  hit_src_time = the source moment a strike lands -> the soundtrack puts an impact exactly there.
"""

FPS = 30
W, H = 1080, 1920
DURATION = 46.0

def win(x):                    # 16:9 1080p source -> 9:16 window (never stretched)
    return {"type": "win", "x": x}
def zoom(z, cx=0.5, cy=0.5):   # portrait 4K source -> punch-in
    return {"type": "zoom", "z": z, "cx": cx, "cy": cy}
def rect(x, y, w, h):          # arbitrary 9:16 crop rectangle (display coordinates)
    return {"type": "rect", "x": x, "y": y, "w": w, "h": h}
def panel(x, y, s):            # square crop shown as a panel over its own blurred, darkened fill
    return {"type": "panel", "x": x, "y": y, "s": s}

FULL = zoom(1.0)
GFN = "v29025g50000d9jo14nog65hrm6a3nq0.mp4"
BC = rect(25, 90, 525, 934)                # GFN broadcast: crops away the channel bug (top-right)
EU = "RPReplay_Final1676472202.mov"
WG = "RPReplay_Final1687870372.mp4"
WC = "RPReplay_Final1634644693.mov"

SHOTS = [
    # ---- OPENING 0-5 : the fighter -------------------------------------------------------
    (0.00, 0.75, GFN, 38.40, 1.0, BC, 38.75),                          # cold open: Or's FLYING KNEE (teaser of the climax)
    (0.75, 0.75, "IMG_7970.mov", 5.55, 1.0, zoom(1.45, 0.52, 0.58), 5.95),   # Or - knee into the pads
    (1.50, 3.50, "IMG_7991.MOV", 88.00, 0.5, zoom(1.2, 0.5, 0.5)),     # Or, arena, slow-mo  | "אור משה"

    # ---- THE FIGHTER 5-13.5 : credentials + first knockdown -----------------------------
    (5.00, 1.00, "IMG_7892.MOV",  2.40, 1.0, zoom(1.15, 0.45, 0.55)),  # hands wrapped | "מעל 15 שנה בזירה."
    (6.00, 1.00, "IMG_7970.mov",  1.00, 1.0, zoom(1.35, 0.45, 0.58), 1.45),
    (7.00, 1.00, EU,              2.10, 1.0, rect(760, 0, 500, 888), 2.70),   # Euro: Or's head kick | tag
    (8.00, 1.00, WG,              2.00, 1.0, panel(380, 248, 480)),          # World Games: hand raised | tag
    (9.00, 1.00, WC,              2.00, 1.0, rect(1000, 140, 400, 711)),       # World Champs: hand raised | tag
    (10.0, 0.50, "IMG_7970.mov",  5.75, 1.0, zoom(1.5, 0.52, 0.58), 6.00),
    (10.5, 0.50, GFN,            18.55, 1.0, BC, 18.80),
    (11.0, 0.50, "IMG_7970.mov", 23.10, 1.0, zoom(1.5, 0.45, 0.58), 23.35),
    (11.5, 0.50, GFN,            25.45, 1.0, BC, 25.70),
    (12.0, 1.50, GFN,            26.20, 1.0, BC, 26.50),                 # KD1: punches -> he folds -> down

    # ---- THE COACH 13.5-22 : the next generation ----------------------------------------
    (13.5, 1.00, "D67A6795.MP4", 37.60, 1.0, win(770)),                 # Or teaching | "עכשיו הוא בונה את הדור הבא."
    (14.5, 1.00, "D67A6791.MP4",  1.40, 1.0, win(760)),                 # Or demo, close
    (15.5, 1.00, "D67A6790.MP4", 11.50, 1.0, win(560)),                 # Or holding pads for a teen
    (16.5, 1.00, "D67A6795.MP4", 40.00, 1.0, win(900)),                 # stance demo over students' shoulders
    (17.5, 0.75, "D67A6791.MP4",  9.85, 1.0, win(560), 10.30),          # Or head-kick demo | "בונים ביטחון."
    (18.25, 0.75, "IMG_1612.MOV", 5.30, 1.0, FULL),                     # student punches toward lens
    (19.0, 1.00, "D67A6795.MP4", 30.20, 1.0, win(1120)),                # Or coaching a teen | "מפתחים משמעת."
    (20.0, 0.50, "D67A6790.MP4", 13.40, 1.0, win(620)),
    (20.5, 0.50, "IMG_1601.MOV",  2.00, 1.0, FULL),
    (21.0, 0.50, "D67A6791.MP4", 12.90, 1.0, win(720)),
    (21.5, 0.50, "D67A6790.MP4",  3.00, 1.0, win(600)),

    # ---- CLIMAX 22-35 : back in the ring ------------------------------------------------
    (22.0, 1.00, "IMG_7991_small.mov", 0.40, 1.0, FULL),               # walkout smoke
    (23.0, 1.00, "IMG_7991.MOV", 91.00, 1.0, zoom(1.15, 0.5, 0.5)),     # Or heads to the ring
    (24.0, 1.50, GFN,            30.70, 1.0, BC, 31.15),                # KD2: Or drives him back -> down
    (25.5, 0.50, "IMG_7997.MOV", 45.50, 1.0, zoom(1.6, 0.52, 0.61)),
    (26.0, 1.00, GFN,            37.95, 1.0, BC, 38.75),                # KD3: Or charges -> FLYING KNEE lands
    (27.0, 2.50, "IMG_7997.MOV", 46.85, 0.5, zoom(1.55, 0.58, 0.62), 47.45),  # same knockdown, ringside, slow-mo
    (29.5, 1.50, GFN,            66.00, 1.0, BC),                       # Or celebrates | "18 פעמים אלוף ישראל"
    (31.0, 1.00, GFN,            68.70, 1.0, BC),                       # the team in TEAM MOSHE shirts | "יוצרים אלופים."
    (32.0, 0.50, "IMG_7970.mov",  9.40, 1.0, zoom(1.5, 0.55, 0.58), 9.65),
    (32.5, 0.50, GFN,            29.55, 1.0, BC, 29.80),
    (33.0, 0.50, "IMG_7997.MOV", 36.00, 1.0, zoom(1.5, 0.50, 0.62)),
    (33.5, 0.50, "D67A6791.MP4", 10.00, 1.0, win(560), 10.30),
    (34.0, 0.50, "IMG_7970.mov",  5.75, 1.0, zoom(1.6, 0.52, 0.58), 6.00),
    (34.5, 0.50, GFN,            30.05, 1.0, BC, 30.30),

    # ---- FINALE 35-46 : hero moment + logo ----------------------------------------------
    (35.0, 2.50, "IMG_7991.MOV", 98.70, 0.5, zoom(1.2, 0.5, 0.48)),     # Or walks to the ring, slow-mo
    (37.5, 8.50, "D67A6795.MP4", 12.00, 1.0, win(656)),                 # the club, graded down under the logo
]

DIM = {37.5: 0.55}

def hit_times():
    """Timeline times where a strike lands (for sound design)."""
    out = []
    for s in SHOTS:
        if len(s) > 6:
            t0, dur, src, sin, speed, crop, hit = s
            out.append(round(t0 + (hit - sin) / speed, 3))
    return out
