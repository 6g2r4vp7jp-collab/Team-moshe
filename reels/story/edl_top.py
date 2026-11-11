import json, sys, numpy as np
sys.path.insert(0, __file__.rsplit('/',1)[0]); from picks_top import SEQ, PRE, POST
Z={'1896':1.4,'1898':1.9}
out=[]
for i,(c,imps,_) in enumerate(SEQ):
    a=round(imps[0]-PRE,3); b=round(imps[-1]+POST,3); d=b-a
    mot=json.load(open(f'/tmp/claude-0/p3/m_{c}.json'))
    nk=max(4,int(d/0.8)+1); kt=[0.05+k*((d-0.1)/(nk-1)) for k in range(nk)]; keys=[]
    for k in kt:
        bs=[m[2] for m in mot if abs(m[0]-(a+k))<0.6 and m[2]]
        bb=np.median(np.array(bs),axis=0); keys.append(np.array([(bb[0]+bb[2])/2,(bb[1]+bb[3])/2-10]))
    m=np.mean(keys,axis=0); keys=[0.4*k+0.6*m for k in keys]
    last=i==len(SEQ)-1
    out.append(dict(clip=c,ss=a,dur=round(d,3),z=Z.get(c,1.55),kt=kt,keys=[(round(float(x)),round(float(y))) for x,y in keys],bumps=[],end=last,nopush=True))
json.dump(out,open(sys.argv[1],'w'),indent=1)
print(len(out),'clips',round(sum(o['dur'] for o in out),2),'s')
