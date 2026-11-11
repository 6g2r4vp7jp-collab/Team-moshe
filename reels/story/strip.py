import json, subprocess, sys, os, numpy as np
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,'/tmp/claude-0/rate'); from cands import C
SRC={'1896':'/tmp/claude-0/src2/IMG_1896.MOV','1898':'/tmp/claude-0/src2/IMG_1898.MOV'}
MJ={'1896':'/tmp/claude-0/work/m1896.json','1898':'/tmp/claude-0/work/m1898.json'}
Z={'1896':1.7,'1898':2.4}
mots={}
def mot(c):
    if c not in mots: mots[c]=json.load(open(MJ.get(c,f'/tmp/claude-0/p3/m_{c}.json')))
    return mots[c]
def job(k):
    c,t,_=C[k]; src=SRC.get(c,f'/tmp/claude-0/src3/IMG_{c}.MOV'); z=Z.get(c,1.7)
    bs=[m[2] for m in mot(c) if abs(m[0]-t)<0.5 and m[2]]; b=np.median(np.array(bs),axis=0)
    cx,cy=(b[0]+b[2])/2*10,(b[1]+b[3])/2*10
    cw=int(2160/z)//2*2; ch=int(3840/z)//2*2
    x=int(min(max(cx-cw/2,0),2160-cw))//2*2; y=int(min(max(cy-ch/2-60,0),3840-ch))//2*2
    out=f'/tmp/claude-0/rate/s{k:03d}.png'
    if os.path.exists(out): return k
    vf=(f"fps=20,crop={cw}:{ch}:{x}:{y},zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0:peak=4,"
        f"zscale=t=bt709:m=bt709:r=tv:w=150:h=266,format=rgb24,tile=14x1")
    subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{t-0.45:.3f}","-i",src,"-t","0.7","-map","0:v:0","-vf",vf,"-frames:v","1",out],check=True)
    return k
with ThreadPoolExecutor(4) as ex: list(ex.map(job,range(len(C))))
print(len(C),'strips')
