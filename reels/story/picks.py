# Instagram story (Nov 11 training): full combinations only, never cut mid-strike.
# clip ids n1..n5 = the five IMG_1899.mov uploads in the Drive 'אימונים' folder by upload time
# (n1 is a shorter copy of n2, unused).
# (clip, start, end, zoom, keys)  keys: crop centre (x,y) in 216x384 proxy coords at 4 evenly spaced
# times between start+0.1 and end-0.1 -- hand-placed on Or with the pad still in frame.
PICKS=[
 ('n3',159.4,161.2,2.2,[(72,200)]*4),                          # hook: big roundhouse
 ('n4',6.7,9.9,2.2,[(97,205),(111,205),(111,205),(99,205)]),   # punches > kick > knee > kick
 ('n2',26.4,29.6,2.2,[(74,190)]*4),                            # punches > roundhouse
 ('n3',127.6,132.4,2.2,[(66,190)]*4),                          # kick, punches, kick, kick
 ('n4',155.1,157.9,2.2,[(79,200)]*4),                          # punches > kick
 ('n2',78.3,82.7,1.9,[(70,205)]*4),                            # kick, kick, punches, kick
 ('n5',58.3,61.6,2.2,[(113,190)]*4),                           # punches > knee
 ('n4',39.4,43.5,2.1,[(131,210),(141,210),(121,210),(109,210)]),  # kick, kick, punch, knee
 ('n2',67.1,72.0,2.1,[(118,200),(101,200),(79,200),(52,200)]), # punches > kick > knee
 ('n4',146.8,151.7,2.2,[(65,205),(65,205),(40,205),(72,205)]), # punches > kick > knee
 ('n5',133.0,138.2,2.1,[(68,205),(66,205),(57,205),(50,205)]), # kicks, punches, kicks
 ('n3',163.5,168.2,2.2,[(59,205),(59,205),(59,205),(76,205)]), # kick series (climax)
 ('n5',180.3,183.6,1.5,[(130,235),(105,240),(95,240),(90,240)]),  # end: kick then walk to camera
]
