# Kicks-only reel, exactly 35.000s (1050 frames @30fps). All 8 Drive videos. No slow motion.
# Singles = indices into ratings.json / cands.C (impact time), each 23 frames: 0.42s wind-up .. impact .. retraction.
# Removed vs kicks_v2: low kicks to the thigh and knees. v2: removed every high-angle shot (IMG_1896/IMG_1898),
# replaced with eye-level kicks; (clip, impact) pairs are singles not in cands.C. L = left-leg kick (judged from impact frames), rest right.
SINGLE_FRAMES=24; PRE=0.44
SEQ=[57,43,0,31,('n2',21.01),23,1,36,20,60,'54L',41,3,53,46,33,
     ('n3',163.44,168.19),                    # fast kick series (one leg)
     65,9,66,50,('n3',162.91),34,'55L',4,48,7,35,47,30,21,
     ('n3',None,178.16)]                     # finale: fast series with the other leg; start fills to 35.000s
TOTAL_FRAMES=1050
OFFSET_X={}   # clip index -> crop shift (proxy px), to keep the pad in frame
