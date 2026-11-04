// Renders promo.html frame-by-frame into an MP4 (video only) and dumps hit times for the music.
// usage: node render.js <width> <height> <out.mp4> [fps] [--stills t1,t2,...] [--contact "text"]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

(async () => {
  const args = process.argv.slice(2);
  const [w, h, out] = [+args[0], +args[1], args[2]];
  const fps = +(args[3] && !args[3].startsWith('--') ? args[3] : 30);
  const opt = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
  const stills = opt('--stills');
  const contact = opt('--contact') || '';

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  const url = 'file://' + path.resolve(__dirname, 'promo.html') + (contact ? '?contact=' + encodeURIComponent(contact) : '');
  await page.goto(url);
  await page.evaluate(() => window.ready);
  const { HITS, DURATION } = await page.evaluate(() => ({ HITS: window.HITS, DURATION: window.DURATION }));
  fs.writeFileSync(path.resolve(__dirname, 'hits.json'), JSON.stringify({ hits: HITS, duration: DURATION }));

  if (stills) {
    for (const t of stills.split(',').map(Number)) {
      await page.evaluate((t) => window.seek(t), t);
      await page.screenshot({ path: `${out}_${t}.jpg`, type: 'jpeg', quality: 85 });
    }
    await browser.close();
    return;
  }

  const ff = spawn('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = Math.round(DURATION * fps);
  for (let f = 0; f < total; f++) {
    await page.evaluate((t) => window.seek(t), f / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(`${out}: frame ${f}/${total}`);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  await browser.close();
})();
