import json, sys, numpy as np
sys.path.insert(0, __file__.rsplit('/',1)[0]); from picks_plus import SEQ, PRE, POST, FINALE
segs=[]
for s in SEQ:
    if len(s)==2: segs.append((s[0],s[1]-PRE,s[1]+POST))
    elif isinstance(s[1],float) and isinstance(s[2],float) and s[2]-s[1]<1.5 and s[0]!='n6': segs.append((s[0],s[1]-PRE,s[2]+POST))
    else: segs.append(s)
segs.append(FINALE)
out=[]
for i,(c,a,b) in enumerate(segs):
    a=round(a,3); b=round(b,3)
    mot=json.load(open(f'/tmp/claude-0/p3/m_{c}.json'))
    kt=[0.05+k*((b-a-0.1)/3) for k in range(4)]; keys=[]
    for k in kt:
        bs=[m[2] for m in mot if abs(m[0]-(a+k))<0.6 and m[2]]
        bb=np.median(np.array(bs),axis=0); keys.append(np.array([(bb[0]+bb[2])/2,(bb[1]+bb[3])/2-10]))
    m=np.mean(keys,axis=0); keys=[0.5*k+0.5*m for k in keys]
    last=i==len(segs)-1
    out.append(dict(clip=c,ss=a,dur=round(b-a,3),z=1.4 if last else 1.55,kt=kt,keys=[(round(float(x)),round(float(y))) for x,y in keys],bumps=[],end=last,nopush=True))
json.dump(out,open(sys.argv[1],'w'),indent=1)
print(len(out),'clips',round(sum(o['dur'] for o in out),2),'s')
