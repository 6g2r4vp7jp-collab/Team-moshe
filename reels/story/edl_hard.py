import json, sys, numpy as np
sys.path.insert(0, __file__.rsplit('/',1)[0]); from picks_hard import SEGS
out=[]
for i,(c,a,b) in enumerate(SEGS):
    mot=json.load(open(f'/tmp/claude-0/p3/m_{c}.json')); d=b-a
    nk=max(4,int(d/0.8)+1)                      # a crop keyframe roughly every 0.8s on long rounds
    kt=[0.05+k*((d-0.1)/(nk-1)) for k in range(nk)]; keys=[]
    for k in kt:
        bs=[m[2] for m in mot if abs(m[0]-(a+k))<0.6 and m[2]]
        bb=np.median(np.array(bs),axis=0); keys.append(np.array([(bb[0]+bb[2])/2,(bb[1]+bb[3])/2-10]))
    keys=np.array(keys); sm=keys.copy()
    for k in range(len(keys)): sm[k]=keys[max(0,k-1):k+2].mean(axis=0)   # smooth camera path
    last=i==len(SEGS)-1
    out.append(dict(clip=c,ss=a,dur=round(d,3),z=1.4 if last else 1.55,kt=kt,keys=[(round(float(x)),round(float(y))) for x,y in sm],bumps=[],end=last,nopush=True))
json.dump(out,open(sys.argv[1],'w'),indent=1)
print(len(out),'clips',round(sum(o['dur'] for o in out),2),'s')
