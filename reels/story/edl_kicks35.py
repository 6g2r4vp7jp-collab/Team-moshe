import json, sys, numpy as np
d=__file__.rsplit('/',1)[0]; sys.path.insert(0,d); sys.path.insert(0,'/tmp/claude-0/rate')
from picks_kicks35 import SEQ, SINGLE_FRAMES, PRE, TOTAL_FRAMES
from cands import C
Z={'1896':1.4,'1898':1.9}
MJ={'1896':'/tmp/claude-0/work/m1896.json','1898':'/tmp/claude-0/work/m1898.json'}
segs=[]
for s in SEQ:
    if isinstance(s,tuple): segs.append([s[0],s[1],s[2]]); continue
    k=int(str(s).rstrip('L')); c,t,_=C[k]; segs.append([c,t-PRE,t-PRE+SINGLE_FRAMES/30])
used=sum(round((b-a)*30) for c,a,b in segs if b is not None)
segs[-1][2]=segs[-1][1]+(TOTAL_FRAMES-used)/30
out=[]
for i,(c,a,b) in enumerate(segs):
    n=round((b-a)*30); d_=n/30; mot=json.load(open(MJ.get(c,f'/tmp/claude-0/p3/m_{c}.json')))
    nk=max(4,int(d_/0.8)+1); kt=[0.05+k*((d_-0.1)/(nk-1)) for k in range(nk)]; keys=[]
    for k in kt:
        bs=[m[2] for m in mot if abs(m[0]-(a+k))<0.6 and m[2]]
        bb=np.median(np.array(bs),axis=0); keys.append(np.array([(bb[0]+bb[2])/2,(bb[1]+bb[3])/2-10]))
    m=np.mean(keys,axis=0); keys=[0.4*k+0.6*m for k in keys]
    out.append(dict(clip=c,ss=round(a,3),dur=d_,z=Z.get(c,1.55),kt=kt,keys=[(round(float(x)),round(float(y))) for x,y in keys],bumps=[],end=i==len(segs)-1,nopush=True))
json.dump(out,open(sys.argv[1],'w'),indent=1)
print(len(out),'clips', sum(round(o['dur']*30) for o in out),'frames; finale',round(out[-1]['dur'],3),'s')
