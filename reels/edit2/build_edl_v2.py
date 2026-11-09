# v2: only strong strikes and full combinations. (clip, start, beats, impact, mode)
import json, numpy as np, sys
B=60/90; A,F='1896','1898'
Z={A:1.6,F:2.5}
S=[
 (A,207.75,3,209.3,''),     # double roundhouse
 (F,136.0,3,137.0,''),      # punches -> high kick
 (A,284.8,3,286.3,''),      # 1-2-3 -> kick
 (F,117.4,4,119.3,''),      # punches -> kick
 (A,330.0,4,330.9,'push'),  # punch-kick-knees
 (F,138.4,3,139.9,''),      # punches -> kick
 (A,255.8,2,256.6,''),      # punches -> kick
 (F,70.8,3,71.9,''),        # punches -> kick
 (A,291.4,3,292.7,''),      # punches -> kick
 (F,88.4,3,89.7,''),        # combo -> kick
 (A,215.4,5,217.2,'push'),  # punches, kick, kick
 (F,177.9,2,178.7,''),      # kick
 (A,261.8,2,262.3,''),      # power kick
 (F,97.6,3,98.9,''),        # punches -> kick
 (A,204.8,3,205.9,''),      # punch -> power kick
 (A,342.0,4.3,342.0,'end'), # walk to camera
]
mot={c:json.load(open(f'/tmp/claude-0/work/m{c}.json')) for c in (A,F)}
def center(c,t0,t1):
    bs=[b for t,_,b in mot[c] if t0<=t<=t1 and b]
    b=np.median(np.array(bs),axis=0); return (b[0]+b[2])/2*10,(b[1]+b[3])/2*10
out=[]
for c,ss,beats,imp,mode in S:
    dur=beats*B; cx,cy=center(c,ss-0.3,ss+dur+0.3); cy-=120
    if mode=='end': cx,cy=1250,2100
    out.append(dict(clip=c,ss=ss,dur=dur,z=Z[c] if mode!='end' else 1.3,cx=round(cx),cy=round(cy),lead=round(imp-ss,3),mode=mode,bump=mode!='end'))
json.dump(out,open(sys.argv[1],'w'),indent=0)
print(len(out),'segments',round(sum(o['dur'] for o in out),2),'s')
