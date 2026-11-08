#!/usr/bin/env bash
# Checks which video tools are installed. Installs NOTHING; prints an install plan for missing ones.
ok(){ printf "  ✅ %-12s %s\n" "$1" "$2"; }
no(){ printf "  ❌ %-12s חסר. %s\n" "$1" "$2"; MISSING=1; }
echo "כלי עריכת וידאו:"
command -v ffmpeg  >/dev/null && ok ffmpeg  "$(ffmpeg -version | head -1 | cut -d' ' -f3)" || no ffmpeg "התקנה: sudo apt-get install -y ffmpeg (או brew install ffmpeg). חובה."
command -v ffprobe >/dev/null && ok ffprobe "מותקן" || no ffprobe "מגיע עם ffmpeg. חובה."
if command -v ffmpeg >/dev/null; then
  for f in libass libfribidi libharfbuzz libx264; do
    ffmpeg -hide_banner -buildconf 2>/dev/null | grep -q "enable-$f" && ok "$f" "כתוביות עבריות / H.264" || no "$f" "צריך build של ffmpeg עם $f (כתוביות בעברית)."
  done
fi
command -v convert >/dev/null && ok imagemagick "אופציונלי, תמונות" || no imagemagick "אופציונלי: sudo apt-get install -y imagemagick"
command -v node    >/dev/null && ok node "$(node -v), אופציונלי, שכבות גרפיות" || no node "אופציונלי"
python3 - <<'PY' 2>/dev/null && ok python3 "$(python3 -V)" || no python3 "חובה"
import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)
PY
[ -n "$MISSING" ] && echo "יש כלים חסרים. לא הותקן דבר. אשר את תוכנית ההתקנה לפני שמריצים אותה." || echo "הכל מוכן."
