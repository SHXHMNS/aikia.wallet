const puppeteer=require('puppeteer-core');const {spawn}=require('child_process');
const FF=require('ffmpeg-static');const FPS=30,DUR=20.5,N=Math.round(FPS*DUR);
(async()=>{
  const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--allow-file-access-from-files','--force-color-profile=srgb']});
  const p=await b.newPage(); await p.setViewport({width:1920,height:1080});
  await p.goto('file://'+__dirname+'/video.html',{waitUntil:'networkidle0'}); await p.evaluate(()=>document.fonts.ready);
  const ff=spawn(FF,['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS),'-c:v','png','-i','-','-i','audio.wav',
    '-af','loudnorm=I=-14:TP=-1.5:LRA=11','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-shortest','-movflags','+faststart','raw.mp4'],{stdio:['pipe','inherit','inherit']});
  for(let f=0;f<N;f++){await p.evaluate(t=>render(t),f/FPS);const png=await p.screenshot({type:'png'});
    if(!ff.stdin.write(png))await new Promise(r=>ff.stdin.once('drain',r)); if(f%100==0)console.log('frame',f);}
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('done');
})();
