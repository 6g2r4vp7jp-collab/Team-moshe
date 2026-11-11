D=$1; cd $D; rm -f all.h264
for i in $(sed -n "s/file .v\(..\)\.mp4./\1/p" v.txt); do ffmpeg -hide_banner -loglevel error -y -i v$i.mp4 -c copy -bsf:v h264_mp4toannexb -f h264 - >> all.h264; done
ffmpeg -hide_banner -loglevel error -y -r 30 -i all.h264 -c copy -video_track_timescale 15360 video.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4
