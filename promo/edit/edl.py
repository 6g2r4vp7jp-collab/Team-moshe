"""TEAM MOSHE promo v2 - Edit Decision List (the "project file").

Story: Or Moshe the FIGHTER (power, achievements)  ->  Or Moshe the COACH (leadership, next generation)
       ->  climax in the ring  ->  final hero moment  ->  logo reveal.
Or is confirmed (by Or) in: IMG_7892/7893 (hand wraps), IMG_7970 (pads, locker room), IMG_7991 (walkout/ringside),
IMG_7997 (GFN fight + knockdown), C7925 (hand raised), D67A6790/91/95 (coaching at the club).

Timeline: 46.0 s, 30 fps, 1080x1920. Music 120 BPM -> beat 0.5 s; all cuts on beats / half-beats.
Shot = (timeline_start, duration, source, source_in, speed, crop)
"""

FPS = 30
W, H = 1080, 1920
DURATION = 46.0

def win(x):                    # 16:9 1080p source -> 9:16 window at x (never stretched)
    return {"type": "win", "x": x}

def zoom(z, cx=0.5, cy=0.5):   # portrait 4K source -> punch-in (stays >= 1080 wide up to 2x)
    return {"type": "zoom", "z": z, "cx": cx, "cy": cy}

FULL = zoom(1.0)

SHOTS = [
    # ---- OPENING 0-5 : who is behind TEAM MOSHE ------------------------------------
    (0.00, 0.75, "IMG_7970.mov",  5.55, 1.0, zoom(1.45, 0.52, 0.58)),   # Or - knee into pads
    (0.75, 0.75, "D67A6791.MP4",  0.60, 1.0, win(660)),                 # Or - punches toward lens
    (1.50, 3.50, "IMG_7991.MOV", 88.00, 0.5, zoom(1.2, 0.5, 0.5)),      # Or - shirtless, gloves, arena (slow-mo) | "אור משה"

    # ---- BUILD 5-20 : fighter <-> coach --------------------------------------------
    (5.00, 1.00, "IMG_7892.MOV",  2.40, 1.0, zoom(1.15, 0.45, 0.55)),   # Or's hands being wrapped | "מעל 15 שנה בזירה."
    (6.00, 1.00, "IMG_7892.MOV", 12.30, 1.0, zoom(1.25, 0.55, 0.38)),   # Or - close-up, focus
    (7.00, 1.00, "IMG_7970.mov",  1.00, 1.0, zoom(1.35, 0.45, 0.58)),   # Or - pad combo
    (8.00, 1.00, "D67A6791.MP4",  1.40, 1.0, win(760)),                 # Or (coach) - shadow-boxing demo
    (9.00, 1.00, "IMG_7991.MOV", 98.30, 1.0, zoom(1.15, 0.5, 0.5)),     # Or - walking to the ring
    (10.0, 1.00, "D67A6795.MP4", 37.60, 1.0, win(770)),                 # Or teaching the group | "עכשיו הוא בונה את הדור הבא."
    (11.0, 1.00, "IMG_7970.mov",  8.80, 1.0, zoom(1.35, 0.55, 0.58)),   # Or - punches
    (12.0, 1.00, "D67A6790.MP4", 11.50, 1.0, win(560)),                 # Or holding pads for a teen
    (13.0, 1.00, "IMG_7970.mov", 22.90, 1.0, zoom(1.4, 0.45, 0.58)),    # Or - knee
    (14.0, 1.00, "D67A6795.MP4", 40.00, 1.0, win(900)),                 # Or - stance demo over students' shoulders
    (15.0, 0.75, "D67A6791.MP4",  9.85, 1.0, win(560)),                 # Or - head kick demo   | "בונים ביטחון."
    (15.75, 0.75, "IMG_1612.MOV", 5.30, 1.0, FULL),                     # student punches toward lens
    (16.5, 0.50, "IMG_7970.mov",  4.40, 1.0, zoom(1.4, 0.45, 0.58)),    # Or - clinch
    (17.0, 0.50, "D67A6790.MP4", 13.40, 1.0, win(620)),                 # Or on pads with teen  | "מפתחים משמעת."
    (17.5, 0.50, "IMG_1601.MOV",  2.00, 1.0, FULL),                     # kids warm-up
    (18.0, 0.50, "IMG_7970.mov", 25.70, 1.0, zoom(1.4, 0.45, 0.58)),    # Or - pads
    (18.5, 0.75, "D67A6795.MP4", 30.20, 1.0, win(1120)),                 # Or coaching a teen
    (19.25, 0.75, "IMG_7991_small.mov", 0.40, 1.0, FULL),               # walkout smoke -> into the climax

    # ---- CLIMAX 20-35 : the ring --------------------------------------------------------
    (20.0, 1.00, "IMG_7991.MOV", 91.00, 1.0, zoom(1.15, 0.5, 0.5)),     # Or heads to the ring
    (21.0, 0.50, "IMG_7997.MOV", 41.30, 1.0, zoom(1.6, 0.45, 0.60)),
    (21.5, 0.50, "IMG_7970.mov",  5.95, 1.0, zoom(1.55, 0.52, 0.58)),
    (22.0, 0.50, "IMG_7997.MOV", 43.10, 1.0, zoom(1.6, 0.47, 0.60)),
    (22.5, 0.50, "D67A6791.MP4", 10.05, 1.0, win(560)),
    (23.0, 0.50, "IMG_7997.MOV", 44.60, 1.0, zoom(1.6, 0.50, 0.61)),
    (23.5, 0.50, "IMG_7970.mov", 23.30, 1.0, zoom(1.5, 0.45, 0.58)),
    (24.0, 0.50, "IMG_7997.MOV", 45.50, 1.0, zoom(1.6, 0.52, 0.61)),
    (24.5, 0.50, "IMG_7997.MOV", 46.30, 1.0, zoom(1.6, 0.52, 0.61)),
    (25.0, 2.50, "IMG_7997.MOV", 46.85, 0.5, zoom(1.55, 0.58, 0.62)),   # SLOW-MO: Or's knockdown
    (27.5, 2.50, "C7925.mov",     1.45, 0.5, win(300)),                 # Or's hand raised (slow-mo) | "יוצרים אלופים."
    (30.0, 0.50, "IMG_7997.MOV", 27.40, 1.0, zoom(1.5, 0.50, 0.62)),    # achievements montage
    (30.5, 0.50, "IMG_7970.mov",  6.50, 1.0, zoom(1.5, 0.52, 0.58)),
    (31.0, 0.50, "IMG_7997.MOV", 29.60, 1.0, zoom(1.5, 0.50, 0.62)),
    (31.5, 0.50, "D67A6790.MP4",  3.00, 1.0, win(600)),
    (32.0, 0.50, "IMG_7997.MOV", 31.70, 1.0, zoom(1.5, 0.50, 0.62)),
    (32.5, 0.50, "IMG_7970.mov",  9.60, 1.0, zoom(1.5, 0.55, 0.58)),
    (33.0, 0.50, "IMG_7997.MOV", 36.00, 1.0, zoom(1.5, 0.50, 0.62)),
    (33.5, 0.50, "D67A6791.MP4", 12.90, 1.0, win(720)),
    (34.0, 0.50, "IMG_7997.MOV", 38.20, 1.0, zoom(1.5, 0.50, 0.62)),
    (34.5, 0.50, "IMG_7970.mov", 24.40, 1.0, zoom(1.5, 0.45, 0.58)),

    # ---- FINALE 35-46 : hero moment + logo reveal ---------------------------------------
    (35.0, 2.50, "IMG_7991.MOV", 98.70, 0.5, zoom(1.2, 0.5, 0.48)),     # Or walks to the ring, slow-mo
    (37.5, 8.50, "D67A6795.MP4", 12.00, 1.0, win(656)),                 # the club, graded down under the logo
]

DIM = {37.5: 0.55}
