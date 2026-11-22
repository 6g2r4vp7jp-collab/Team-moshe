# Pre-render each pick as 1080x1920 SDR mp4 (HDR tonemap, crop centred on the action) into public/clips.
import json, subprocess, os, sys, numpy as np
from concurrent.futures import ThreadPoolExecutor
P=json.load(open('tools/picks.json')); RAW='/tmp/claude-0/d239'; MOT='/tmp/claude-0/q'
os.makedirs('public/clips',exist_ok=True)
TM="zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0:peak=4,zscale=t=bt709:m=bt709:r=tv:f=lanczos"
def job(i):
    p=P[i]; d=p['f']/30; out=f'public/clips/c{i:02d}.mp4'
    if os.path.exists(out) and not os.environ.get('FORCE'): return i
    mot=json.load(open(f"{MOT}/m_{p['src']}.json"))
    bs=[m[2] for m in mot if p['ss']<=m[0]<=p['ss']+d and m[2]]
    b=np.median(np.array(bs),axis=0) if bs else np.array([60,120,156,300])
    cx=(b[0]+b[2])/2/216; cy=(b[1]+b[3])/2/384
    z=p.get('z',1.3); cw=1/z; ch=1/z
    x=min(max(cx-cw/2,0),1-cw); y=min(max(cy-ch/2-0.03,0),1-ch)
    crop=f"crop=iw*{cw:.4f}:ih*{ch:.4f}:iw*{x:.4f}:ih*{y:.4f}"
    vf=f"fps=30,{crop},{TM}:w=1080:h=1920,eq=contrast=1.07:saturation=1.08:gamma=0.97,format=yuv420p"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(p['ss']),"-i",f"{RAW}/{p['src']}.mov","-t",f"{d+0.2:.3f}",
        "-map","0:v:0","-map","0:a:0","-vf",vf,"-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p",
        "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709","-r","30","-af","highpass=f=70,acompressor=threshold=0.08:ratio=4:attack=2:release=80:makeup=3,alimiter=limit=0.95","-c:a","aac","-b:a","192k","-ar","48000",out],check=True)
    return i
with ThreadPoolExecutor(3) as ex:
    for i in ex.map(job,range(len(P))): print(i,end=' ',flush=True)
print('\nframes',sum(p['f'] for p in P))
