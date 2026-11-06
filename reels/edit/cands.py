import json
H=json.load(open('/tmp/claude-0/hits.json'))
allpk=sorted(d for v in H.values() for _,d in v)
import numpy as np
p80=np.percentile(allpk,80)
for k,v in sorted(H.items()):
    # group into bursts: gap < 0.7s
    bursts=[];cur=[]
    for t,d in v:
        if cur and t-cur[-1][0]>0.7: bursts.append(cur);cur=[]
        cur.append((t,d))
    if cur: bursts.append(cur)
    out=[]
    for b in bursts:
        if len(b)>=3 or max(d for _,d in b)>p80:
            out.append(f"{b[0][0]:.2f}-{b[-1][0]:.2f} n={len(b)} pk={max(d for _,d in b):.0f}" + (" [LOUD]" if max(d for _,d in b)>p80 else ""))
    print(f"## {k}\n  " + "\n  ".join(out))
print("p80",p80)
