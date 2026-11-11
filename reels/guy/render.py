import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
W,H=map(int,sys.argv[1].split('x')); out=sys.argv[2]; par=int(sys.argv[3]); crf=sys.argv[4]; preset=sys.argv[5]
AMAP={"1463":"0:2","1464":"0:1"}
S=json.load(open('/workspace/Team-moshe/reels/guy/edl.json'))
os.makedirs(out,exist_ok=True)
TM="zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0:peak=4,zscale=t=bt709:m=bt709:r=tv:f=lanczos:w=%d:h=%d"%(W,H)
def job(i):
    c,ss,dur,sp,z=S[i]; src=f"/tmp/claude-0/src/IMG_{c}.MOV"
    n=round(dur*30); srcdur=n/30*sp+0.1
    cw=int(2160/z)//2*2; ch=int(3840/z)//2*2; cx=(2160-cw)//2; cy=int((3840-ch)*0.55)//2*2
    vf=f"trim=duration={srcdur:.3f},setpts=(PTS-STARTPTS)/{sp},fps=30,crop={cw}:{ch}:{cx}:{cy},{TM},eq=contrast=1.06:saturation=1.04:gamma=0.98,vignette=angle=PI/5.5,format=yuv420p"
    if i==len(S)-1: vf+=f",fade=t=out:st={n/30-0.9:.3f}:d=0.9"
    v=f"{out}/v{i:02d}.mp4"; a=f"{out}/a{i:02d}.wav"
    if os.path.exists(v) and os.path.exists(a):
        try:
            k=int(subprocess.check_output(["ffprobe","-v","error","-count_packets","-select_streams","v","-show_entries","stream=nb_read_packets","-of","csv=p=0",v]).strip())
            if k==n: return i
        except Exception: pass
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(ss),"-i",src,"-map","0:v:0","-vf",vf,
        "-frames:v",str(n),"-c:v","libx264","-preset",preset,"-crf",crf,"-profile:v","high","-pix_fmt","yuv420p",
        "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709","-x264-params","keyint=60","-r","30",v],check=True)
    af="asetrate=24000,aresample=48000," if sp==0.5 else ""
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(ss),"-i",src,"-t",f"{srcdur:.3f}","-map",AMAP[c],
        "-af",f"{af}apad,atrim=0:{n/30:.4f},afade=t=in:d=0.006,afade=t=out:st={n/30-0.012:.4f}:d=0.012","-ar","48000","-ac","2",a],check=True)
    return i
with ThreadPoolExecutor(par) as ex:
    for i in ex.map(job,range(len(S))): print(i,end=' ',flush=True)
open(f"{out}/v.txt","w").write("".join(f"file 'v{i:02d}.mp4'\n" for i in range(len(S))))
open(f"{out}/a.txt","w").write("".join(f"file 'a{i:02d}.wav'\n" for i in range(len(S))))
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",f"{out}/v.txt","-c","copy",f"{out}/video.mp4"],check=True)
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",f"{out}/a.txt","-c","pcm_s16le",f"{out}/hits.wav"],check=True)
print("\ndone")
