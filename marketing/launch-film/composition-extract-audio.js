// Pre-extract per-frame audio bands (deterministic) -> audio-data.js
const {execFileSync}=require('child_process');const fs=require('fs');
const [,,inp,out,fpsArg,durArg]=process.argv;const FPS=+fpsArg||30,DUR=+durArg;const SR=22050;
const raw=execFileSync('ffmpeg',['-v','error','-i',inp,'-ac','1','-ar',String(SR),'-f','f32le','-'],{maxBuffer:1<<28});
const x=new Float32Array(raw.buffer,raw.byteOffset,raw.length/4);
const N=2048,frames=Math.round(FPS*DUR),NB=8;
const edges=[20,60,150,300,600,1200,2500,5000,10000];
function fft(re,im){const n=re.length;for(let i=1,j=0;i<n;i++){let b=n>>1;for(;j&b;b>>=1)j^=b;j^=b;if(i<j){[re[i],re[j]]=[re[j],re[i]];[im[i],im[j]]=[im[j],im[i]]}}
 for(let len=2;len<=n;len<<=1){const a=-2*Math.PI/len;for(let i=0;i<n;i+=len)for(let k=0;k<len/2;k++){const c=Math.cos(a*k),s=Math.sin(a*k);const ur=re[i+k],ui=im[i+k];const vr=re[i+k+len/2]*c-im[i+k+len/2]*s,vi=re[i+k+len/2]*s+im[i+k+len/2]*c;re[i+k]=ur+vr;im[i+k]=ui+vi;re[i+k+len/2]=ur-vr;im[i+k+len/2]=ui-vi}}}
const B=[];
for(let f=0;f<frames;f++){const c=Math.round(f/FPS*SR);const re=new Float64Array(N),im=new Float64Array(N);
 for(let i=0;i<N;i++){const j=c-N/2+i;const w=0.5-0.5*Math.cos(2*Math.PI*i/(N-1));re[i]=(j>=0&&j<x.length?x[j]:0)*w}
 fft(re,im);const bands=new Array(NB).fill(0);
 for(let k=1;k<N/2;k++){const hz=k*SR/N;const m=Math.hypot(re[k],im[k]);for(let b=0;b<NB;b++)if(hz>=edges[b]&&hz<edges[b+1]){bands[b]+=m;break}}
 B.push(bands.map(v=>Math.log1p(v)));}
for(let b=0;b<NB;b++){const col=B.map(r=>r[b]).sort((a,c)=>a-c);const lo=col[Math.floor(col.length*0.05)],hi=col[Math.floor(col.length*0.97)]||1;
 B.forEach(r=>{r[b]=Math.max(0,Math.min(1,(r[b]-lo)/(hi-lo||1)))})}
fs.writeFileSync(out,'window.AUDIO_DATA='+JSON.stringify({fps:FPS,totalFrames:frames,frames:B.map(r=>({bands:r.map(v=>+v.toFixed(2))}))})+';\n');
console.log('frames',frames);
