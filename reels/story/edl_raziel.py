import json, sys, numpy as np
sys.path.insert(0, __file__.rsplit('/',1)[0]); from picks_raziel import SEQ, TOTAL_FRAMES
segs=[list(s) for s in SEQ]
used=sum(round((b-a)*30) for c,a,b in segs[:-1]); segs[-1][2]=segs[-1][1]+(TOTAL_FRAMES-used)/30
out=[]
for i,(c,a,b) in enumerate(segs):
    n=round((b-a)*30); d=n/30; mot=json.load(open(f'/tmp/claude-0/rp/m_{c}.json'))
    nk=max(4,int(d/0.7)+1); kt=[0.05+k*((d-0.1)/(nk-1)) for k in range(nk)]; keys=[]
    for k in kt:
        bs=[m[2] for m in mot if abs(m[0]-(a+k))<0.5 and m[2]]
        bb=np.median(np.array(bs),axis=0) if bs else np.array([60,100,156,300])
        keys.append(np.array([(bb[0]+bb[2])/2,(bb[1]+bb[3])/2]))
    m=np.mean(keys,axis=0); keys=[0.5*k+0.5*m for k in keys]
    out.append(dict(clip=c,ss=a,dur=d,z=1.2,kt=kt,keys=[(round(float(x)),round(float(y))) for x,y in keys],bumps=[],end=i==len(segs)-1,nopush=True))
json.dump(out,open(sys.argv[1],'w'),indent=1)
print(len(out),'clips',sum(round(o['dur']*30) for o in out),'frames; finale',round(out[-1]['dur'],2),'s')
