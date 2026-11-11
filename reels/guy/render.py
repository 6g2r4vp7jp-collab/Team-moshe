# usage: render.py OUTDIR PAR   -> OUTDIR/video.mp4 (1080x1920 60fps, stabilized) + OUTDIR/hits.wav
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
here=os.path.dirname(os.path.abspath(__file__)); out=sys.argv[1]; par=int(sys.argv[2])
S=json.load(open(f'{here}/edl.json')); B=60/90; FPS=60
AMAP={"1463":"0:2","1464":"0:1"}
os.makedirs(out,exist_ok=True)
TM="zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0:peak=4,zscale=t=bt709:m=bt709:r=tv:f=lanczos:w=1216:h=2162,format=yuv420p"
def ff(*a): subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",*a],check=True)
def job(i):
    c,ss,beats=S[i]; src=f"/tmp/claude-0/src/IMG_{c}.MOV"
    dur=beats*B+(0.2 if i==len(S)-1 else 0); n=round(dur*FPS); trf=f"{out}/t{i:02d}.trf"
    base=f"trim=duration={dur+0.1:.3f},setpts=PTS-STARTPTS,fps={FPS},{TM}"
    ff("-ss",str(ss),"-i",src,"-map","0:v:0","-vf",f"{base},vidstabdetect=shakiness=6:accuracy=12:result={trf}","-f","null","-")
    vf=(f"{base},vidstabtransform=input={trf}:smoothing=18:optzoom=0:zoom=0:interpol=bicubic,"
        f"crop=1080:1920:68:{int((2162-1920)*0.55)},eq=contrast=1.06:saturation=1.05:gamma=0.98,vignette=angle=PI/5.5,unsharp=5:5:0.4,format=yuv420p")
    ff("-ss",str(ss),"-i",src,"-map","0:v:0","-vf",vf,"-frames:v",str(n),"-c:v","libx264","-preset","medium","-crf","12","-pix_fmt","yuv420p",f"{out}/v{i:02d}.mp4")
    ff("-ss",str(ss),"-i",src,"-t",f"{dur+0.1:.3f}","-map",AMAP[c],"-af",f"apad,atrim=0:{n/FPS:.4f},afade=t=in:d=0.006,afade=t=out:st={n/FPS-0.012:.4f}:d=0.012","-ar","48000","-ac","2",f"{out}/a{i:02d}.wav")
    return i
with ThreadPoolExecutor(par) as ex:
    for i in ex.map(job,range(len(S))): print(i,end=' ',flush=True)
# one clean re-encode of the whole timeline (continuous timestamps, constant 60fps)
k=len(S); ins=sum([["-i",f"{out}/v{i:02d}.mp4"] for i in range(k)],[])
fc="".join(f"[{i}:v]" for i in range(k))+f"concat=n={k}:v=1:a=0,fade=t=out:st={sum(s[2] for s in S)*B+0.2-0.9:.3f}:d=0.9[v]"
ff(*ins,"-filter_complex",fc,"-map","[v]","-r",str(FPS),"-c:v","libx264","-preset","medium","-crf","19","-profile:v","high","-pix_fmt","yuv420p",
   "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709","-g","60",f"{out}/video.mp4")
ins=sum([["-i",f"{out}/a{i:02d}.wav"] for i in range(k)],[])
ff(*ins,"-filter_complex","".join(f"[{i}:a]" for i in range(k))+f"concat=n={k}:v=0:a=1[a]","-map","[a]","-c:a","pcm_s16le",f"{out}/hits.wav")
print("\ndone")
