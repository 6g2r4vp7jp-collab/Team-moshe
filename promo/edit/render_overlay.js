// node render_overlay.js out.mov            -> full transparent overlay (PNG-in-MOV, alpha)
// node render_overlay.js prefix --stills t1,t2  -> transparent PNG stills
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const path = require('path');
(async () => {
  const [out, flag, list] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.resolve(__dirname, 'overlay.html')); await p.evaluate(() => window.ready);
  if (flag === '--stills') { for (const t of list.split(',')) { await p.evaluate(t => seek(+t), t); await p.screenshot({ path: `${out}_${t}.png`, omitBackground: true }); } await b.close(); return; }
  const D = await p.evaluate(() => window.DURATION), fps = 30, n = Math.min(Math.round(D * fps), +(process.env.END_FRAME || 1e9));
  const ff = spawn('ffmpeg', ['-y','-hide_banner','-loglevel','error','-f','image2pipe','-framerate','30','-c:v','png','-i','-','-c:v','png','-pix_fmt','rgba',out], { stdio: ['pipe','inherit','inherit'] });
  const start = +(process.env.START_FRAME || 0);
  for (let f = start; f < n; f++) { await p.evaluate(t => seek(t), f / fps); const buf = await p.screenshot({ type: 'png', omitBackground: true });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); if (f % 240 === 0) console.log('overlay', f, '/', n); }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
})();
