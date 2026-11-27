# Protein shake reel (Drive folder "אוכל", IMG_6263.MOV)

Remotion project, 1080x1920, 30fps, ~56s.

Setup (media is git-ignored):
1. Tonemap the source to SDR: `public/source.mp4` (1080x1920, 30fps; see the ffmpeg command in the session log: zscale/tonemap hable).
2. `python3 tools/music.py public/music.wav 60` - original soft lo-fi bed.
3. `cp /usr/share/fonts/truetype/noto/NotoColorEmoji.ttf public/fonts/`
4. Edit `tools/edl.json` (shots, captions with source timestamps, ingredient labels), then `python3 tools/gen.py`.
5. `npx remotion render ProteinShakeReel out.mp4` (add `--browser-executable` if Remotion's browser download is blocked).

Captions are phrase-level, aligned to detected speech; text is the Drive transcript, corrected by hand.
Ingredient labels only state what is said in the video (no invented amounts or nutrition values).
