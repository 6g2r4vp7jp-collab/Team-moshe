# Pads reel #2 (training 9.11): two static angles, tracked crops, punch-zooms and push-ins.
# Entry: (clip, impact_sec, beats, zoom, mode)  mode: '' | 'push' (slow push-in) ; every cut gets a small impact bump
import json, numpy as np, sys
B=60/90
A,F='1896','1898'   # A = close side angle, F = far diagonal angle
Z={A:1.75,F:2.5}
S=[
 (F,45.075,1,0,''),(A,195.85,1,0,''),(F,98.87,1,0,''),(A,330.815,1,0,''),
 (A,107.12,2,0,''),(F,62.435,2,0,''),(A,215.47,2,0,''),(F,103.005,2,0,''),(A,256.575,2,0,''),(F,119.12,2,0,''),
 (A,286.305,1,0,''),(F,127.675,1,0,''),(A,218.68,2,0,''),
 (F,136.925,4,0,'push'),
 (A,209.3,2,0,'push'),(F,80.61,2,0,''),(A,191.2,2,0,''),(F,47.88,2,0,''),(A,262.2,2,0,''),(F,157.285,2,0,''),
 (A,294.1,2,0,'push'),(F,57.8,2,0,''),(A,285.78,2,0,''),(F,110.02,2,0,''),(A,212.5,2,0,''),
 (F,64.1,1,0,''),(A,330.815,1,0.3,''),
 (F,178.7,4,0,'push'),
 (F,89.17,2,0,''),(A,195.85,2,0.3,''),(F,184.995,2,0,''),(A,286.305,2,0.3,''),
 (F,45.075,1,0.5,''),(A,216.21,1,0,''),(F,190.4,1,0,''),(A,262.2,1,0.3,''),
 (A,342.0,4.3,-0.45,'end'),
]
LEAD={1:0.25,2:0.45,4:0.9}
mot={c:json.load(open(f'/tmp/claude-0/work/m{c}.json')) for c in (A,F)}
def center(c,t0,t1):
    bs=[b for t,_,b in mot[c] if t0<=t<=t1 and b]
    b=np.median(np.array(bs),axis=0)
    return (b[0]+b[2])/2*10,(b[1]+b[3])/2*10
out=[]
for c,imp,beats,dz,mode in S:
    dur=beats*B; lead=LEAD.get(beats,0.3) if mode!='end' else 0
    ss=imp-lead; z=Z[c]+dz
    cx,cy=center(c,ss-0.6,ss+dur+0.6)
    cy-=120
    if mode=='end': cx,cy=1250,2100  # a bit of headroom
    out.append(dict(clip=c,ss=round(ss,3),dur=dur,z=z,cx=round(cx),cy=round(cy),lead=lead,mode=mode))
json.dump(out,open(sys.argv[1],'w'),indent=0)
print(len(out),'segments',round(sum(o['dur'] for o in out),2),'s')
