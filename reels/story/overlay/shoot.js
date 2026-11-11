const { chromium } = require('playwright'); const path=require('path');
(async()=>{ const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
 for (const n of ['title','end']) { await p.goto('file://'+path.resolve(__dirname,n+'.html')); await p.evaluate(()=>document.fonts.ready);
   await p.waitForTimeout(300); await p.screenshot({path:`/tmp/claude-0/work/${n}.png`,omitBackground:true}); }
 await b.close(); })();
