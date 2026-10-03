const puppeteer=require('puppeteer-core');
(async()=>{
  const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--allow-file-access-from-files','--force-color-profile=srgb']});
  const p=await b.newPage(); await p.setViewport({width:1920,height:1080});
  p.on('console',m=>console.log('console:',m.text())); p.on('pageerror',e=>console.log('ERR',e.message));
  await p.goto('file://'+__dirname+'/video.html',{waitUntil:'networkidle0'});
  await p.evaluate(()=>document.fonts.ready);
  console.log(await p.evaluate(()=>[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family+f.weight).join(',')));
  const ts=process.argv.slice(2).map(Number);
  require('fs').mkdirSync('stills',{recursive:true});
  for(const t of ts){await p.evaluate(t=>render(t),t); await p.screenshot({path:`stills/t${t.toFixed(2)}.jpg`,type:'jpeg',quality:80});}
  await b.close();
})();
