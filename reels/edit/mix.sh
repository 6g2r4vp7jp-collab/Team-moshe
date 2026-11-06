D=$1; DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $D/video.mp4); FO=$(python3 -c "print($DUR-1.3)")
H="highpass=f=90,lowpass=f=12000,agate=threshold=0.04:ratio=3:attack=1:release=120,acompressor=threshold=0.1:ratio=3:attack=2:release=80:makeup=2"
ffmpeg -hide_banner -loglevel error -y -i $D/hits.wav -i /tmp/claude-0/music/track.wav -filter_complex "[0]$H,asplit[h1][h2];[1]atrim=0:$DUR,volume=0.8[m];[m][h1]sidechaincompress=threshold=0.08:ratio=3:attack=3:release=150[md];[md][h2]amix=inputs=2:weights='1 0.85':normalize=0,afade=t=out:st=$FO:d=1.3[out]" -map "[out]" -c:a pcm_f32le $D/pre.wav
ffmpeg -hide_banner -loglevel error -y -i $D/hits.wav -af "$H,afade=t=out:st=$FO:d=1.3" -c:a pcm_f32le $D/preh.wav
for p in pre:mix:-14 preh:hitsonly:-16; do IFS=: read a b T <<< $p
 I=$(ffmpeg -hide_banner -nostats -i $D/$a.wav -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | awk '{print $2}')
 G=$(python3 -c "print($T-($I))")
 ffmpeg -hide_banner -loglevel error -y -i $D/$a.wav -af "volume=${G}dB,alimiter=limit=0.85:attack=1:release=50:level=false" -ar 48000 -c:a pcm_s16le $D/$b.wav
 echo "$b in=$I gain=$G"; ffmpeg -hide_banner -nostats -i $D/$b.wav -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
done
