# usage: finish.sh <render dir> <music wav> <title png> <end png> <out mp4>
D=$1; M=$2; T=$3; E=$4; OUT=$5
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $D/video.mp4)
ES=$(python3 -c "print(round($DUR-1.9,3))"); FO=$(python3 -c "print($DUR-1.0)")
H="highpass=f=90,lowpass=f=12000,agate=threshold=0.04:ratio=3:attack=1:release=120,acompressor=threshold=0.1:ratio=3:attack=2:release=80:makeup=2"
ffmpeg -hide_banner -loglevel error -y -i $D/hits.wav -i $M -filter_complex "[0]$H,asplit[h1][h2];[1]atrim=0:$DUR,volume=0.8[m];[m][h1]sidechaincompress=threshold=0.08:ratio=3:attack=3:release=150[md];[md][h2]amix=inputs=2:weights='1 0.9':normalize=0,afade=t=out:st=$FO:d=1.0[out]" -map "[out]" -c:a pcm_f32le $D/pre.wav
I=$(ffmpeg -hide_banner -nostats -i $D/pre.wav -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | awk '{print $2}')
G=$(python3 -c "print(-14-($I))")
ffmpeg -hide_banner -loglevel error -y -i $D/video.mp4 -loop 1 -t 2.6 -i $T -loop 1 -t 1.9 -i $E -i $D/pre.wav -filter_complex \
 "[1]format=rgba,fade=t=in:st=0.15:d=0.25:alpha=1,fade=t=out:st=2.1:d=0.4:alpha=1[t];[2]format=rgba,fade=t=in:d=0.45:alpha=1,setpts=PTS+$ES/TB[e];[0][t]overlay=0:0:eof_action=pass[v1];[v1][e]overlay=0:0:eof_action=pass,format=yuv420p[v]" \
 -map "[v]" -map 3:a -c:v libx264 -preset slow -crf 16 -profile:v high -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
 -af "volume=${G}dB,alimiter=limit=0.89:attack=1:release=50:level=false" -c:a aac -b:a 256k -ar 48000 -movflags +faststart -shortest $OUT
ffmpeg -hide_banner -nostats -i $OUT -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
