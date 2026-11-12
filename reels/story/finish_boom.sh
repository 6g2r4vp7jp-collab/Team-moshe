# usage: finish_clean.sh <render dir> <music wav> <out mp4>   -- no text, no logo, strike sound pushed over the music
D=$1; M=$2; OUT=$3
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $D/video.mp4); FO=$(python3 -c "print($DUR-1.0)")
H="highpass=f=90,lowpass=f=12000,agate=threshold=0.04:ratio=3:attack=1:release=120,acompressor=threshold=0.08:ratio=4:attack=1:release=60:makeup=2.5,equalizer=f=90:t=q:w=1.2:g=4"
ffmpeg -hide_banner -loglevel error -y -i $D/hits.wav -i $M -filter_complex "[0]$H,asplit[h1][h2];[1]atrim=0:$DUR,volume=0.4[m];[m][h1]sidechaincompress=threshold=0.08:ratio=3:attack=3:release=150[md];[md][h2]amix=inputs=2:weights='1 1.9':normalize=0,afade=t=out:st=$FO:d=1.0[out]" -map "[out]" -c:a pcm_f32le $D/pre.wav
I=$(ffmpeg -hide_banner -nostats -i $D/pre.wav -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | awk '{print $2}')
G=$(python3 -c "print(-14-($I))")
ffmpeg -hide_banner -loglevel error -y -i $D/video.mp4 -i $D/pre.wav -map 0:v -map 1:a -c:v copy -af "volume=${G}dB,alimiter=limit=0.89:attack=1:release=50:level=false" -c:a aac -b:a 256k -ar 48000 -movflags +faststart -shortest $OUT
ffmpeg -hide_banner -nostats -i $OUT -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
