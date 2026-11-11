# usage: render.py edl.json outdir parallel crf preset   (SRC env = folder with IMG_<clip>.MOV)
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
E=json.load(open(sys.argv[1])); out=sys.argv[2]; par=int(sys.argv[3]); crf=sys.argv[4]; preset=sys.argv[5]
SRC=os.environ.get('SRC','/tmp/claude-0/src3'); os.makedirs(out,exist_ok=True)
W,H=1080,1920; IW,IH=1620,2880
TM=f"zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0:peak=4,zscale=t=bt709:m=bt709:r=tv:f=lanczos:w={IW}:h={IH}"
def pw(ts,vs):   # piecewise-linear expression of t through (ts,vs)
    e=f"{vs[-1]:.1f}"
    for k in range(len(ts)-2,-1,-1):
        t0,t1,v0,v1=ts[k],ts[k+1],vs[k],vs[k+1]
        e=f"if(lt(t,{t1:.3f}),{v0:.1f}+({v1-v0:.1f})*clip((t-{t0:.3f})/{t1-t0:.3f},0,1),{e})"
    return e
def job(i):
    e=E[i]; src=f"{SRC}/IMG_{e['clip']}.MOV"; n=round(e['dur']*30); srcdur=n/30+0.1
    z=e['z']; cw=int(2160/z)//2*2; ch=int(3840/z)//2*2
    xs=[min(max(x*10-cw/2,0),2160-cw) for x,_ in e['keys']]; ys=[min(max(y*10-ch/2,0),3840-ch) for _,y in e['keys']]
    zexp="1"
    for b in e['bumps']: zexp+=f"*(1+0.06*exp(-pow((on-{round(b*30)})/3.5,2)))"
    if e['end'] and not e.get('nopush'): zexp+=f"*(1+0.25*on/{n})"
    zp=f"zoompan=z='{zexp}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s={W}x{H}:fps=30"
    vf=(f"trim=duration={srcdur:.3f},setpts=PTS-STARTPTS,fps=30,"
        f"crop={cw}:{ch}:'{pw(e['kt'],xs)}':'{pw(e['kt'],ys)}',{TM},"
        f"eq=contrast=1.1:saturation=1.12:gamma=0.96,unsharp=5:5:0.6,{zp},vignette=angle=PI/5,format=yuv420p")
    if i==0: vf+=",fade=t=in:d=0.15"
    if e['end']: vf+=f",fade=t=out:st={n/30-0.6:.3f}:d=0.6"
    v=f"{out}/v{i:02d}.mp4"; a=f"{out}/a{i:02d}.wav"
    if not (os.path.exists(v) and os.path.exists(a)):
        subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-threads","4","-ss",str(e['ss']),"-i",src,"-map","0:v:0","-vf",vf,
            "-frames:v",str(n),"-c:v","libx264","-preset",preset,"-crf",crf,"-profile:v","high","-pix_fmt","yuv420p",
            "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709","-x264-params","keyint=60","-r","30",v+".tmp.mp4"],check=True)
        os.rename(v+".tmp.mp4",v)
        subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(e['ss']),"-i",src,"-t",f"{srcdur:.3f}","-map","0:a:0",
            "-af",f"apad,atrim=0:{n/30:.4f},afade=t=in:d=0.01,afade=t=out:st={n/30-0.02:.4f}:d=0.02","-ar","48000","-ac","2",a],check=True)
    return i
with ThreadPoolExecutor(par) as ex:
    for i in ex.map(job,range(len(E))): print(i,end=' ',flush=True)
open(f"{out}/v.txt","w").write("".join(f"file 'v{i:02d}.mp4'\n" for i in range(len(E))))
open(f"{out}/a.txt","w").write("".join(f"file 'a{i:02d}.wav'\n" for i in range(len(E))))
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",f"{out}/v.txt","-c","copy",f"{out}/video.mp4"],check=True)
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",f"{out}/a.txt","-c","pcm_s16le",f"{out}/hits.wav"],check=True)
print("\ndone")
