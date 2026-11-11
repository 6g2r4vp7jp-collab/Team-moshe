import json, sys
sys.path.insert(0, __file__.rsplit('/',1)[0]); from picks import PICKS
H=json.load(open('/tmp/claude-0/p3/hits.json'))
out=[]
for i,(c,a,b,z,keys) in enumerate(PICKS):
    hs=sorted([(d,t) for t,d in H[c] if a+0.15<=t<=b-0.2],reverse=True)
    bumps=sorted(round(t-a,3) for d,t in hs[:2] if d>=12) if i<len(PICKS)-1 else []
    kt=[0.1+k*((b-a-0.2)/3) for k in range(4)]
    out.append(dict(clip=c,ss=a,dur=round(b-a,3),z=z,kt=kt,keys=keys,bumps=bumps,end=i==len(PICKS)-1))
json.dump(out,open(sys.argv[1],'w'),indent=1)
print(len(out),'segments',round(sum(o['dur'] for o in out),2),'s'); [print(o['clip'],o['ss'],o['dur'],o['bumps']) for o in out]
