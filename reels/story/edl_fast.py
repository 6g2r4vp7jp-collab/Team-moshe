import json, sys, numpy as np  # note: clip 3 x-keys shifted -35 by hand after this script (trainer was in centre)
sys.path.insert(0, __file__.rsplit('/',1)[0]); from picks_fast import PICKS
Z=1.55
out=[]
for i,(c,a,b) in enumerate(PICKS):
    mot=json.load(open(f'/tmp/claude-0/p3/m_{c}.json'))
    kt=[0.1+k*((b-a-0.2)/3) for k in range(4)]; keys=[]
    for k in kt:
        bs=[m[2] for m in mot if abs(m[0]-(a+k))<0.8 and m[2]]
        bb=np.median(np.array(bs),axis=0); keys.append((float((bb[0]+bb[2])/2),float((bb[1]+bb[3])/2)-10))
    sm=[keys[0]]+[tuple((np.array(keys[j-1])+2*np.array(keys[j])+np.array(keys[min(j+1,3)]))/4) for j in range(1,4)]
    out.append(dict(clip=c,ss=a,dur=round(b-a,3),z=Z,kt=kt,keys=[(round(x),round(y)) for x,y in sm],bumps=[],end=i==len(PICKS)-1,nopush=True))
json.dump(out,open(sys.argv[1],'w'),indent=1)
print(len(out),'clips',round(sum(o['dur'] for o in out),2),'s')
