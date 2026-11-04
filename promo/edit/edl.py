"""TEAM MOSHE promo - Edit Decision List (the "project file").

Timeline: 48.0 s, 30 fps, 1080x1920 (9:16). Music is 120 BPM -> 1 beat = 0.5 s, cuts land on beats.
Each shot: (timeline_start, duration, source, source_in, speed, crop)
  speed < 1  -> slow motion (only used on 60 fps sources so motion stays smooth)
  crop       -> for 16:9 sources: x offset of a 9:16 window (608x1080) - nothing is ever stretched
             -> for 4K portrait sources: zoom factor and centre (punch-in), or None for full frame
"""

FPS = 30
W, H = 1080, 1920
DURATION = 48.0

# crop helpers ------------------------------------------------------------
def win(x):            # 16:9 1080p source -> 9:16 window starting at x
    return {"type": "win", "x": x}

def zoom(z, cx=0.5, cy=0.5):  # portrait 4K source -> punch-in
    return {"type": "zoom", "z": z, "cx": cx, "cy": cy}

FULL = zoom(1.0)

SHOTS = [
    # ---- 1. OPENING 0-5 : hit, hit, walkout + title ---------------------------------
    (0.00, 0.75, "IMG_7970.mov",  5.55, 1.0, zoom(1.35, 0.50, 0.58)),   # knee into pads
    (0.75, 0.75, "D67A6791.MP4",  9.85, 1.0, win(560)),                 # Or - head kick demo
    (1.50, 3.50, "IMG_7991_small.mov", 0.20, 0.5, FULL),                # walkout through smoke (slow-mo)

    # ---- 2. TRAINING 5-15 : 1 shot per 2 beats -------------------------------------
    (5.00, 1.00, "IMG_7892.MOV",  2.40, 1.0, zoom(1.15, 0.45, 0.55)),   # hand wraps close-up
    (6.00, 1.00, "IMG_7970.mov",  1.00, 1.0, zoom(1.25, 0.45, 0.58)),   # pad work, wide
    (7.00, 1.00, "D67A6790.MP4", 11.50, 1.0, win(560)),                 # teen on pads with coach
    (8.00, 1.00, "IMG_1612.MOV",  5.30, 1.0, FULL),                     # kid punches toward lens
    (9.00, 1.00, "D67A6791.MP4",  0.90, 1.0, win(800)),                 # coach demonstrates combo
    (10.0, 1.00, "IMG_7970.mov",  8.80, 1.0, zoom(1.3, 0.55, 0.58)),    # punches on pads
    (11.0, 1.00, "D67A6795.MP4", 36.60, 1.0, win(720)),                 # coach teaching group
    (12.0, 1.00, "IMG_1612.MOV",  1.40, 1.0, FULL),                     # kids kicking pads
    (13.0, 1.00, "D67A6791.MP4", 12.90, 1.0, win(720)),                 # coach & kid technique
    (14.0, 1.00, "IMG_7970.mov",  4.40, 1.0, zoom(1.3, 0.45, 0.58)),    # clinch / knee

    # ---- 3. THE CLUB 15-30 : kids, teens, coaching, captions -------------------------
    (15.0, 2.00, "D67A6795.MP4",  1.80, 1.0, win(640)),                 # coach briefs the group
    (17.0, 2.00, "IMG_1601.MOV",  1.80, 1.0, FULL),                     # kids warm-up   | "בונים ביטחון."
    (19.0, 2.00, "D67A6795.MP4",  8.00, 1.0, win(660)),                 # group with gloves
    (21.0, 2.00, "D67A6790.MP4",  2.00, 1.0, win(640)),                 # pad drill        | "מפתחים משמעת."
    (23.0, 2.00, "IMG_1612.MOV",  7.90, 1.0, FULL),                     # sparring pairs
    (25.0, 2.00, "D67A6795.MP4", 30.00, 1.0, win(800)),                 # coach corrects teen
    (27.0, 3.00, "C7925.mov",     1.45, 0.5, win(300)),                 # Or's hand raised  | "יוצרים אלופים."

    # ---- 4. CLIMAX 30-40 : half-beat cuts, slow-mo KO, back to speed ---------------
    (30.0, 0.50, "IMG_7997.MOV", 41.30, 1.0, zoom(1.6, 0.45, 0.60)),
    (30.5, 0.50, "IMG_7970.mov",  5.95, 1.0, zoom(1.5, 0.50, 0.58)),
    (31.0, 0.50, "D67A6790.MP4", 13.40, 1.0, win(620)),
    (31.5, 0.50, "IMG_7997.MOV", 43.10, 1.0, zoom(1.6, 0.47, 0.60)),
    (32.0, 0.50, "IMG_7970.mov", 22.90, 1.0, zoom(1.4, 0.45, 0.58)),
    (32.5, 0.50, "D67A6791.MP4", 10.05, 1.0, win(560)),
    (33.0, 0.50, "IMG_7997.MOV", 45.50, 1.0, zoom(1.6, 0.52, 0.61)),
    (33.5, 0.50, "IMG_1612.MOV",  5.80, 1.0, FULL),
    (34.0, 0.50, "IMG_7970.mov", 25.70, 1.0, zoom(1.4, 0.45, 0.58)),
    (34.5, 0.50, "IMG_7997.MOV", 46.30, 1.0, zoom(1.6, 0.52, 0.61)),
    (35.0, 2.50, "IMG_7997.MOV", 46.85, 0.5, zoom(1.55, 0.58, 0.62)),    # SLOW-MO knockdown
    (37.5, 0.75, "IMG_7991.MOV", 31.00, 1.0, FULL),                     # arena, flags
    (38.25, 0.75, "IMG_7970.mov", 26.80, 1.0, zoom(1.15, 0.5, 0.55)),   # Or + corner
    (39.0, 1.00, "IMG_7991_small.mov", 5.80, 1.0, FULL),                # arena reveal

    # ---- 5. OUTRO 40-48 : club, logo, CTA --------------------------------------------
    (40.0, 8.00, "D67A6795.MP4", 12.00, 1.0, win(656)),                 # the club, graded down under titles
]

# shots that are graded darker for text legibility
DIM = {40.0: 0.42}

# hard-cut transitions that get a white flash (on big hits)
FLASH_AT = [0.0, 0.75, 1.5, 5.0, 15.0, 30.0, 35.0, 40.0]
