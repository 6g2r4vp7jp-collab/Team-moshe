import numpy as np, sys, glob, os
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
out={}
for p in sorted(glob.glob('/tmp/claude-0/wav/*.wav')):
    sr,x=wavfile.read(p); x=x.astype(np.float32)/32768
    sos=butter(4,[150,6000],btype='band',fs=sr,output='sos'); y=sosfilt(sos,x)
    hop=int(sr*0.005); n=len(y)//hop
    env=np.sqrt(np.mean(y[:n*hop].reshape(n,hop)**2,axis=1))
    db=20*np.log10(env+1e-6)
    # onset: rise of >12dB over 15ms and above floor
    floor=np.percentile(db,30)
    hits=[];last=-1
    for i in range(3,n):
        if db[i]-db[i-3]>10 and db[i]>floor+20 and (i-last)*0.005>0.09:
            # take peak in next 30ms
            j=i+np.argmax(db[i:i+6]); hits.append((j*0.005,db[j])); last=i
    name=os.path.basename(p)[:-4]
    out[name]=hits
    dur=n*0.005
    print(f"\n### {name} dur={dur:.1f}s hits={len(hits)} floor={floor:.0f}dB")
    # per-second histogram with max peak
    secs=int(dur)+1; cnt=np.zeros(secs,int); pk=np.full(secs,-99.)
    for t,d in hits: s=int(t); cnt[s]+=1; pk[s]=max(pk[s],d)
    print(' '.join(f"{s}:{cnt[s]}" + ("!" if pk[s]>np.percentile([h[1] for h in hits],85) else "") for s in range(secs)))
import json; json.dump(out,open('/tmp/claude-0/hits.json','w'))
