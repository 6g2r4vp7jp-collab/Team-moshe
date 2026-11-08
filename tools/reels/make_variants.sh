#!/usr/bin/env bash
# Make platform versions from a 9:16 master reel.
#   <name>_reels.mp4    Instagram Reels   1080x1920, -14 LUFS, faststart
#   <name>_tiktok.mp4   TikTok            1080x1920, -14 LUFS, faststart
#   <name>_story_NN.mp4 Instagram Stories split into <=60s parts
#   <name>_feed45.mp4   Feed 4:5 (1080x1350, center crop)
# Usage: bash tools/reels/make_variants.sh reels/out/<name>.mp4
set -euo pipefail
IN="$1"; [ -f "$IN" ] || { echo "missing $IN"; exit 1; }
DIR=$(dirname "$IN"); NAME=$(basename "${IN%.*}"); OUT="$DIR/variants"; mkdir -p "$OUT"
FF="ffmpeg -y -hide_banner -loglevel error"
ENC="-c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -r 30 -c:a aac -b:a 256k -ar 48000 -movflags +faststart"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")

$FF -i "$IN" -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -af "loudnorm=I=-14:TP=-1.5" $ENC "$OUT/${NAME}_reels.mp4"
cp "$OUT/${NAME}_reels.mp4" "$OUT/${NAME}_tiktok.mp4"
$FF -i "$IN" -vf "crop=1080:1350:0:(ih-1350)/2" -af "loudnorm=I=-14:TP=-1.5" $ENC "$OUT/${NAME}_feed45.mp4"

N=$(python3 -c "import math;print(max(1, math.ceil($DUR/60)))")
for i in $(seq 0 $((N-1))); do
  $FF -ss $((i*60)) -t 60 -i "$IN" -af "loudnorm=I=-14:TP=-1.5" $ENC "$OUT/${NAME}_story_$(printf %02d $((i+1))).mp4"
done
echo "variants in $OUT:"; ls -1 "$OUT" | grep "^$NAME"
echo "שים לב: בטיקטוק ובסטוריז עדיף לבחור את המוזיקה מתוך הספרייה של האפליקציה."
