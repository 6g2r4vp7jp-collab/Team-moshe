# Kicks-only reel, exactly 35.000s (1050 frames @30fps). All 8 Drive videos. No slow motion.
# Singles = indices into ratings.json / cands.C (impact time), each 23 frames: 0.42s wind-up .. impact .. retraction.
# Removed vs kicks_v2: low kicks to the thigh and knees. L = left-leg kick (judged from impact frames), rest right.
SINGLE_FRAMES=23; PRE=0.42
SEQ=[57,43,0,31,69,23,'70L',36,20,71,'54L',41,3,75,46,33,
     ('n3',163.44,168.19),                    # fast kick series (one leg)
     65,9,'74L',50,78,34,72,'55L',4,48,7,35,47,30,21,
     ('n3',171.66,None)]                     # finale: fast series with the other leg, length fills to 35.000s
TOTAL_FRAMES=1050
