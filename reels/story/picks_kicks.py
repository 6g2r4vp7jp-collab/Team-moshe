# Kicks-only story: every clip is one hard kick (wind-up..retraction), checked frame by frame.
# (clip, impact) -> start=impact-PRE, end=impact+POST ; ranges given explicitly as (clip,start,end)
PRE,POST=0.5,0.4
SEQ=[
 ('n2',76.22), ('n4',169.17), ('n3',135.79), ('n2',4.45), ('n3',160.06), ('n6',12.35),
 ('n4',157.34), ('n4',166.72), ('n5',108.56), ('n3',133.03), ('n4',2.23), ('n6',9.32),
 ('n3',163.8,167.95),            # first-leg kick series
 ('n4',164.22), ('n3',128.13), ('n4',159.62), ('n5',141.60), ('n4',41.23), ('n6',13.75),
 ('n6',6.85,7.9), ('n4',8.47), ('n3',130.31), ('n5',181.03),
 ('n3',171.85,178.15),           # finale: ~11 kicks with the other leg
]
