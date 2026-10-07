// Minimal TrueType outline reader -> SVG path data (outlined lettering, no <text>).
function parseTTF(buf){
 const dv=new DataView(buf),u16=o=>dv.getUint16(o),i16=o=>dv.getInt16(o),u32=o=>dv.getUint32(o);
 const n=u16(4),T={};for(let i=0;i<n;i++){const o=12+i*16;T[String.fromCharCode(dv.getUint8(o),dv.getUint8(o+1),dv.getUint8(o+2),dv.getUint8(o+3))]=u32(o+8);}
 const upm=u16(T.head+18),locFmt=i16(T.head+50),numH=u16(T.hhea+34),asc=i16(T.hhea+4);
 const adv=g=>u16(T.hmtx+4*Math.min(g,numH-1));
 // cmap format 4
 let cm=null;const nt=u16(T.cmap+2);for(let i=0;i<nt;i++){const pid=u16(T.cmap+4+i*8),eid=u16(T.cmap+6+i*8),off=u32(T.cmap+8+i*8);if(pid===3&&eid===1&&u16(T.cmap+off)===4)cm=T.cmap+off;}
 const segX2=u16(cm+6),ends=cm+14,starts=ends+segX2+2,deltas=starts+segX2,ros=deltas+segX2;
 const gid=c=>{for(let s=0;s<segX2/2;s++){const e=u16(ends+s*2);if(c>e)continue;const st=u16(starts+s*2);if(c<st)return 0;const d=i16(deltas+s*2),ro=u16(ros+s*2);if(!ro)return (c+d)&0xffff;const g=u16(ros+s*2+ro+(c-st)*2);return g?(g+d)&0xffff:0;}return 0;};
 const loca=g=>locFmt?u32(T.loca+g*4):u16(T.loca+g*2)*2;
 function contours(g){const o=T.glyf+loca(g);if(loca(g+1)===loca(g))return [];const nc=i16(o);
  if(nc<0){let p=o+10,out=[],more=true;while(more){const fl=u16(p),cg=u16(p+2);p+=4;let dx,dy;if(fl&1){dx=i16(p);dy=i16(p+2);p+=4;}else{dx=dv.getInt8(p);dy=dv.getInt8(p+1);p+=2;}
    let sc=[1,0,0,1];if(fl&8){sc=[i16(p)/16384,0,0,i16(p)/16384];p+=2;}else if(fl&0x40){sc=[i16(p)/16384,0,0,i16(p+2)/16384];p+=4;}else if(fl&0x80){sc=[i16(p)/16384,i16(p+2)/16384,i16(p+4)/16384,i16(p+6)/16384];p+=8;}
    for(const c of contours(cg))out.push(c.map(q=>({x:q.x*sc[0]+q.y*sc[2]+dx,y:q.x*sc[1]+q.y*sc[3]+dy,on:q.on})));more=!!(fl&0x20);}return out;}
  const endPts=[];for(let i=0;i<nc;i++)endPts.push(u16(o+10+i*2));const np=endPts[nc-1]+1;let p=o+10+nc*2;p+=2+u16(p);
  const fl=[];while(fl.length<np){const f=dv.getUint8(p++);fl.push(f);if(f&8){let r=dv.getUint8(p++);while(r--)fl.push(f);}}
  const xs=[],ys=[];let v=0;for(const f of fl){if(f&2){const d=dv.getUint8(p++);v+=f&16?d:-d;}else if(!(f&16)){v+=i16(p);p+=2;}xs.push(v);}
  v=0;for(const f of fl){if(f&4){const d=dv.getUint8(p++);v+=f&32?d:-d;}else if(!(f&32)){v+=i16(p);p+=2;}ys.push(v);}
  const out=[];let s=0;for(const e of endPts){const c=[];for(let i=s;i<=e;i++)c.push({x:xs[i],y:ys[i],on:!!(fl[i]&1)});out.push(c);s=e+1;}return out;}
 return {upm,asc,gid,adv,contours};
}
function textD(font,str,x,y,size,track=0){
 const s=size/font.upm,R=v=>Math.round(v*2)/2;let d='',cx=x;
 for(const ch of str){const g=font.gid(ch.codePointAt(0));
  for(const c of font.contours(g)){const pts=c.map(q=>({x:cx+q.x*s,y:y-q.y*s,on:q.on}));if(!pts.length)continue;
   let st=pts.findIndex(q=>q.on);let seq;if(st<0){const a=pts[0],b=pts[1]||a;seq=[{x:(a.x+b.x)/2,y:(a.y+b.y)/2,on:true},...pts];st=0;}else seq=[...pts.slice(st),...pts.slice(0,st)];
   d+=`M${R(seq[0].x)} ${R(seq[0].y)}`;for(let i=1;i<=seq.length;i++){const q=seq[i%seq.length];if(q.on){const pr=seq[i-1];if(pr.on||i===1&&false)d+=`L${R(q.x)} ${R(q.y)}`;}
    else{const nx=seq[(i+1)%seq.length];const end=nx.on?nx:{x:(q.x+nx.x)/2,y:(q.y+nx.y)/2};d+=`Q${R(q.x)} ${R(q.y)} ${R(end.x)} ${R(end.y)}`;if(nx.on)i++;}}
   d+='Z';}
  cx+=font.adv(g)*s+track*size;}
 return d;}
function textW(font,str,size,track=0){let w=0;for(const ch of str)w+=font.adv(font.gid(ch.codePointAt(0)))*size/font.upm+track*size;return w-track*size;}
return {parseTTF,textD,textW};
