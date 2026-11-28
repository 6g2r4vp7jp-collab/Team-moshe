# Horror look on top of the (already verified) friend edit: cold desaturated grade, crushed blacks,
# grain, vignette, irregular flicker, short camera jolts at cuts and a flash+jolt when he opens his eyes (32.9s).
IN=$1; MUSIC=$2; OUT=$3
CUTS="between(t,2.2,2.45)+between(t,9.5,9.75)+between(t,19.4,19.65)+between(t,28.4,28.65)"
WAKE="between(t,32.9,33.5)"
SH="(10*($CUTS)+28*$WAKE)"
VF="eq=saturation=0.28:contrast=1.28:gamma=0.82:eval=frame:brightness='-0.07-0.06*gt(sin(t*37)*sin(t*5.3),0.6)+0.32*between(t,32.88,32.97)',\
colorbalance=rs=-0.08:gs=0.03:bs=0.12:rm=-0.06:gm=0.02:bm=0.06:rh=-0.03:bh=0.04,\
crop=1000:1778:'40+$SH*sin(t*61)':'71+$SH*cos(t*47)',scale=1080:1920:flags=lanczos,\
noise=alls=16:allf=t,vignette=angle=PI/3.2,format=yuv420p"
ffmpeg -hide_banner -loglevel error -y -i $IN -i $MUSIC -map 0:v -map 1:a -vf "$VF" -c:v libx264 -preset slow -crf 18 \
 -af "loudnorm=I=-15:TP=-1.5:LRA=11" -c:a aac -b:a 256k -ar 48000 -movflags +faststart -shortest $OUT
