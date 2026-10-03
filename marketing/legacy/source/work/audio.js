const fs=require('fs');
const SR=44100, DUR=20.5, N=Math.ceil(SR*DUR);
const L=new Float32Array(N), R=new Float32Array(N), FX=new Float32Array(N); // FX send for reverb
const hz=m=>440*Math.pow(2,(m-69)/12);
let seed=7; const rnd=()=>{seed=(seed*16807)%2147483647;return seed/2147483647*2-1};
const BEAT=0.6, OFF=0.2;
function add(i,v,pan=0,send=0){if(i<0||i>=N)return;L[i]+=v*(1-pan)*.5*2*(pan>0?1-pan:1)*.5+v*.5*(1-Math.max(0,pan));R[i]+=v*.5*(1+Math.min(0,pan));FX[i]+=v*send}
// pad: chords per bar (4 beats), D A Bm G
const chords=[[50,57,62,66,69],[45,57,61,64,69],[47,54,59,62,66],[43,55,59,62,67]];
const barLen=BEAT*4;
for(let i=0;i<N;i++){
  const t=i/SR; const bar=Math.floor(Math.max(0,t-OFF)/barLen); const ch=chords[((bar%4)+4)%4];
  const inBar=((t-OFF)%barLen+barLen)%barLen;
  const env=Math.min(1,inBar/0.25)*(0.85+0.15*Math.cos(inBar/barLen*Math.PI*2));
  let v=0; for(const m of ch){const f=hz(m); v+=Math.sin(2*Math.PI*f*t)+.25*Math.sin(2*Math.PI*f*2.003*t)+.12*Math.sin(2*Math.PI*f*3.01*t);}
  let master=Math.min(1,t/1.2)*(t>19.3?Math.max(0,(20.5-t)/1.2):1);
  const swell= t<3.2?0.55:1;
  add(i,v*0.018*env*master*swell,0,0.5);
  // sub bass on root, from 3.2
  if(t>=3.2){const root=hz(ch[0]-12); const bp=((t-OFF)%BEAT)/BEAT; const be=Math.exp(-bp*3)*0.9+0.1; add(i,Math.sin(2*Math.PI*root*t)*0.11*be*master,0,0);}
}
// drums
function kick(t0,g){const s=Math.floor(t0*SR);for(let k=0;k<SR*.35;k++){const tt=k/SR;const f=45+90*Math.exp(-tt*30);add(s+k,Math.sin(2*Math.PI*f*tt+ 0)*Math.exp(-tt*9)*g,0,0)}}
function hat(t0,g){const s=Math.floor(t0*SR);let lp=0,prev=0;for(let k=0;k<SR*.07;k++){const n=rnd();const hp=n-prev;prev=n;add(s+k,hp*Math.exp(-k/SR*60)*g,0.3,0.15)}}
for(let b=0;b<40;b++){const t=OFF+b*BEAT; if(t<3.2||t>19.0)continue; kick(t,0.32);
  if(t>=6.8) hat(t+BEAT/2,0.035);}
// sfx
function bell(t0,m,g,pan=0,send=.6){const s=Math.floor(t0*SR),f=hz(m);for(let k=0;k<SR*1.6;k++){const tt=k/SR;const e=Math.exp(-tt*4)*Math.min(1,tt/.004);
  add(s+k,(Math.sin(2*Math.PI*f*tt)+.35*Math.sin(2*Math.PI*f*2.76*tt)*Math.exp(-tt*8)+.2*Math.sin(2*Math.PI*f*4.07*tt)*Math.exp(-tt*14))*e*g,pan,send)}}
function pluck(t0,m,g,pan=0){const s=Math.floor(t0*SR),f=hz(m);for(let k=0;k<SR*.5;k++){const tt=k/SR;add(s+k,(Math.sin(2*Math.PI*f*tt)*.8+.2*Math.sin(4*Math.PI*f*tt))*Math.exp(-tt*12)*Math.min(1,tt/.003)*g,pan,.5)}}
function whoosh(t0,d,g){const s=Math.floor(t0*SR);let y=0;for(let k=0;k<SR*d;k++){const x=k/(SR*d);const a=0.02+0.25*Math.sin(Math.PI*x);y+=a*(rnd()-y);add(s+k,y*Math.sin(Math.PI*x)**2*g,0,.4)}}
function tick(t0,g){const s=Math.floor(t0*SR);for(let k=0;k<SR*.04;k++){const tt=k/SR;add(s+k,Math.sin(2*Math.PI*1760*tt)*Math.exp(-tt*120)*g,0,.2)}}
bell(1.55,86,0.11,0.1); bell(1.75,81,0.08,-0.1);           // notification chime D6, A5
whoosh(2.95,0.6,0.22); whoosh(6.5,0.55,0.16); whoosh(10.1,0.55,0.16); whoosh(13.7,0.55,0.16); whoosh(16.75,0.6,0.2);
tick(8.65,0.10); pluck(9.6,74,0.12);                       // add-to-wallet tap, stamp pop D5
tick(11.57,0.10); bell(11.6,78,0.06);
[81,83,85,86,88,90,93,95].forEach((m,i)=>pluck(11.9+i*0.11,[74,78,81,83,86,90,93,98][i],0.05,(i%2?.3:-.3)));
bell(14.15,74,0.08); bell(14.95,78,0.08); bell(15.85,81,0.1);  // tier motif D F# A
[62,66,69,74,78].forEach((m,i)=>bell(17.1+i*0.07,m+12,0.06,(i-2)*.15)); // outro arpeggio
// reverb: comb filters on FX send
const combs=[1557,1617,1491,1422,1277,1356].map(d=>({d,buf:new Float32Array(d),i:0}));
for(let i=0;i<N;i++){let o=0;for(const c of combs){const y=c.buf[c.i];c.buf[c.i]=FX[i]+y*0.78;c.i=(c.i+1)%c.d;o+=y}
  o*=0.06; L[i]+=o; R[i]+= (i>23?o:0);}
// soft clip + normalize
let pk=0;for(let i=0;i<N;i++){L[i]=Math.tanh(L[i]*1.2);R[i]=Math.tanh(R[i]*1.2);pk=Math.max(pk,Math.abs(L[i]),Math.abs(R[i]))}
const g=0.89/pk; const buf=Buffer.alloc(44+N*4);
buf.write('RIFF',0);buf.writeUInt32LE(36+N*4,4);buf.write('WAVEfmt ',8);buf.writeUInt32LE(16,16);buf.writeUInt16LE(1,20);buf.writeUInt16LE(2,22);
buf.writeUInt32LE(SR,24);buf.writeUInt32LE(SR*4,28);buf.writeUInt16LE(4,32);buf.writeUInt16LE(16,34);buf.write('data',36);buf.writeUInt32LE(N*4,40);
for(let i=0;i<N;i++){buf.writeInt16LE(Math.round(L[i]*g*32767),44+i*4);buf.writeInt16LE(Math.round(R[i]*g*32767),46+i*4)}
fs.writeFileSync('audio.wav',buf); console.log('peak',pk.toFixed(3));
