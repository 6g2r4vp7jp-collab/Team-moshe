import json,subprocess,sys
out=sys.argv[1]; S=json.load(open('/tmp/claude-0/edl.json'))
for i,(c,ss,dur,sp,z) in enumerate(S):
    n=round(dur*30); D=n/30; srcdur=D*sp+0.05
    af=f"atrim=duration={srcdur:.4f},"+("asetrate=24000,aresample=48000," if sp==0.5 else "")+f"asetpts=N/SR/TB,apad,atrim=0:{D:.5f},afade=t=in:d=0.006,afade=t=out:st={D-0.012:.4f}:d=0.012"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(ss),"-i",f"/tmp/claude-0/src/IMG_{c}.MOV","-map","0:a:0","-af",af,"-ar","48000","-ac","2",f"{out}/a{i:02d}.wav"],check=True)
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",f"{out}/a.txt","-c","pcm_s16le",f"{out}/hits.wav"],check=True)
