import json, sys, numpy as np
sys.path.insert(0, __file__.rsplit('/',1)[0]); from picks_select2 import SEL
Z={'1896':1.4,'1898':1.9}
MJ={'1896':'/tmp/claude-0/work/m1896.json','1898':'/tmp/claude-0/work/m1898.json'}
out=[]
for i,(cat,c,a,b) in enumerate(SEL):
    d=b-a; mot=json.load(open(MJ.get(c,f'/tmp/claude-0/p3/m_{c}.json')))
    nk=max(4,int(d/0.8)+1); kt=[0.05+k*((d-0.1)/(nk-1)) for k in range(nk)]; keys=[]
    for k in kt:
        bs=[m[2] for m in mot if abs(m[0]-(a+k))<0.7 and m[2]]
        bb=np.median(np.array(bs),axis=0); keys.append(np.array([(bb[0]+bb[2])/2,(bb[1]+bb[3])/2-10]))
    m=np.mean(keys,axis=0); keys=[0.4*k+0.6*m for k in keys]
    out.append(dict(cat=cat,clip=c,ss=a,dur=round(d,3),z=Z.get(c,1.55),kt=kt,keys=[(round(float(x)),round(float(y))) for x,y in keys],bumps=[],end=False,nopush=True))
json.dump(out,open(sys.argv[1],'w'),indent=1)
from collections import defaultdict; T=defaultdict(float)
for o in out: T[o['cat']]+=o['dur']
tot=sum(T.values()); print(len(out),'clips',round(tot,1),'s', {k:f"{v:.1f}s {100*v/tot:.0f}%" for k,v in T.items()})
