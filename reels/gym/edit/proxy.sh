f=$1; b=$(basename ${f%.MOV}); m=$2
ffmpeg -hide_banner -loglevel error -y -i $f -map $m -ac 1 -ar 22050 /tmp/claude-0/g/wav/$b.wav
ffmpeg -hide_banner -loglevel error -y -threads 2 -i $f -map 0:v:0 -vf "scale=270:480,fps=10" -c:v libx264 -preset veryfast -crf 28 /tmp/claude-0/g/proxy/$b.mp4
echo done $b
