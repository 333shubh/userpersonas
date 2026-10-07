// Gate 2 rig generator: Cram + Riot. Returns {build, glyphs-free helpers}. Rig units on 1024 canvas.
let OFF=[0,0];
const R=v=>Math.round(v*2)/2, f=v=>{const r=R(v);return Number.isInteger(r)?String(r):r.toFixed(1)};
const P=(x,y)=>f(x+OFF[0])+' '+f(y+OFF[1]);
const add=(a,b)=>[a[0]+b[0],a[1]+b[1]],sub=(a,b)=>[a[0]-b[0],a[1]-b[1]],mul=(a,s)=>[a[0]*s,a[1]*s],norm=a=>{const l=Math.hypot(a[0],a[1])||1;return [a[0]/l,a[1]/l]};
const rad=d=>d*Math.PI/180;
const poly=pts=>'M'+pts.map(p=>P(p[0],p[1])).join('L')+'Z';
const pline=pts=>'M'+pts.map(p=>P(p[0],p[1])).join('L');
const rect=(x,y,w,h)=>poly([[x,y],[x+w,y],[x+w,y+h],[x,y+h]]);
const circle=(cx,cy,r)=>`M${P(cx-r,cy)}A${f(r)} ${f(r)} 0 1 1 ${P(cx+r,cy)}A${f(r)} ${f(r)} 0 1 1 ${P(cx-r,cy)}Z`;
const ellipse=(cx,cy,rx,ry)=>`M${P(cx-rx,cy)}A${f(rx)} ${f(ry)} 0 1 1 ${P(cx+rx,cy)}A${f(rx)} ${f(ry)} 0 1 1 ${P(cx-rx,cy)}Z`;
const earc=(cx,cy,rx,ry,a0,a1,n=40)=>{const o=[];for(let i=0;i<=n;i++){const a=rad(a0+(a1-a0)*i/n);o.push([cx+rx*Math.cos(a),cy+ry*Math.sin(a)]);}return o;};
const quadPts=(a,b,w)=>{const d=norm(sub(b,a)),n=[-d[1]*w/2,d[0]*w/2];return [add(a,n),add(b,n),sub(b,n),sub(a,n)];};
function ribbon(pts,w){const L=[],Rr=[];for(let i=0;i<pts.length;i++){const a=pts[Math.max(0,i-1)],b=pts[Math.min(pts.length-1,i+1)],d=norm(sub(b,a)),n=[-d[1]*w/2,d[0]*w/2];L.push(add(pts[i],n));Rr.push(sub(pts[i],n));}return [...L,...Rr.reverse()];}
const wave=(x0,y0,x1,y1,amp,per,n=24)=>{const o=[];for(let i=0;i<=n;i++){const t=i/n;o.push([x0+(x1-x0)*t,y0+(y1-y0)*t+amp*Math.sin(t*Math.PI*2*per)]);}return o;};
const steamPts=(bx,by,h,amp)=>{const o=[];for(let i=0;i<=24;i++){const t=i/24;o.push([bx+amp*Math.sin(3*Math.PI*t),by-h*t]);}return o;};
// glyph path transform (M L H V A Z, absolute)
function tfD(d,fn,s){const tk=d.match(/[MLHVAZ]|-?\d*\.?\d+/g);let o='',i=0,cmd='',cur=[0,0];const num=()=>parseFloat(tk[i++]);
 while(i<tk.length){const t=tk[i];if(/[MLHVAZ]/.test(t)){cmd=t;i++;if(cmd==='Z'){o+='Z';continue;}}
  if(cmd==='M'||cmd==='L'){const x=num(),y=num();cur=[x,y];const p=fn(cur);o+=cmd+P(p[0],p[1]);}
  else if(cmd==='H'){cur=[num(),cur[1]];const p=fn(cur);o+='L'+P(p[0],p[1]);}
  else if(cmd==='V'){cur=[cur[0],num()];const p=fn(cur);o+='L'+P(p[0],p[1]);}
  else if(cmd==='A'){const rx=num(),ry=num(),rot=num(),la=num(),sw=num(),x=num(),y=num();cur=[x,y];const p=fn(cur);o+=`A${f(rx*s)} ${f(ry*s)} ${rot} ${la} ${sw} ${P(p[0],p[1])}`;}}
 return o;}
function glyphLayers(svg){const out=[];const re=/<g id="[a-z]+__foreground-type__two-mark(?:__([a-z-]+))?" fill="(#[0-9A-Fa-f]{6})">([\s\S]*?)<\/g>/g;let m;
 while((m=re.exec(svg))){const ds=[...m[3].matchAll(/d="([^"]+)"/g)].map(x=>x[1]);if(ds.length)out.push({fill:m[2],ds});}return out;}
function placeGlyph(layers,x0,y0,h,sx=1){const s=h/400;return layers.map(L=>`<path d="${L.ds.map(d=>tfD(d,([x,y])=>[x0+x*s*sx,y0+y*s],s)).join('')}" fill="${L.fill}"/>`).join('');}

// ---------- shared markup ----------
function mk(o){
 const tf=o.tf||{},only=o.only;
 const keep=id=>!only||only.some(k=>id===k||id.startsWith(k+'__')||id.startsWith(k+'--')||k.startsWith(id+'__'));
 const part=(id,inner)=>keep(id)?`<g id="${id}"${tf[id]?` transform="${tf[id]}"`:''}>${inner}</g>`:'';
 const states=(id,list,chosen)=>keep(id)?`<g id="${id}"${tf[id]?` transform="${tf[id]}"`:''}>`+list.map(([n,m])=>`<g id="${id}--${n}"${n===(chosen||list[0][0])?'':' display="none"'}>${m}</g>`).join('')+'</g>':'';
 return {part,states};
}
function wrapSvg(m,slots,anchors,extraDefs=''){
 const order=['background','environment','limbs-back','body','face','limbs','props','noodles-steam','foreground-type','rig'];
 let s='';for(const k of order){if(k==='limbs-back'&&slots[k]===undefined)continue;
  if(k==='rig'){s+=`<g id="${m}__rig" display="none">`+Object.entries(anchors).map(([a,p])=>`<circle id="${m}__rig__${a}" cx="${f(p[0])}" cy="${f(p[1])}" r="0"/>`).join('')+'</g>\n';}
  else s+=`<g id="${m}__${k}">${slots[k]||''}</g>\n`;}
 return s;}

// ================= CRAM =================
const CR={ink:'#000000',paper:'#FFFFFF',s75:'#404040',s50:'#808080',s25:'#BFBFBF',s10:'#E6E6E6'};
const cs=(d,fill)=>`<path d="${d}" fill="${fill}" stroke="#000000" stroke-width="16" stroke-linejoin="miter" stroke-linecap="square"/>`;
const cf=(d,fill)=>`<path d="${d}" fill="${fill}"/>`;
const cl=(d,col='#000000')=>`<path d="${d}" fill="none" stroke="${col}" stroke-width="16" stroke-linejoin="miter" stroke-linecap="square"/>`;
const clr=(d,col)=>`<path d="${d}" fill="none" stroke="${col}" stroke-width="16" stroke-linejoin="round" stroke-linecap="round"/>`;
const CV={
 front:{fx:0,eR:[452,518,1],eL:[572,518,1],m:[512,608,1],armR:[[340,640],[240,600]],armL:[[684,640],[800,600]],forkTop:400,timer:[786,782],look:[512,518],pack:'front'},
 'three-quarter':{fx:60,eR:[522,518,1],eL:[630,518,0.7],m:[578,608,0.85],armR:[[346,640],[246,600]],armL:[[690,640],[800,600]],forkTop:400,timer:[786,782],look:[860,518],pack:'tq'},
 side:{fx:150,eR:[642,518,0.8],eL:null,m:[662,608,0.5],armR:[[512,690],[770,640]],armL:[[700,570],[800,470]],forkTop:270,timer:[150,782],look:[1062,518],pack:'side'}};
function sachetGeo(cx,cy){const x0=cx-80,y0=cy-120,dep=6,top=[],bot=[];for(let i=0;i<=40;i++)top.push([x0+i*4,y0+(i%2?0:dep)]);for(let i=40;i>=0;i--)bot.push([x0+i*4,y0+240-(i%2?0:dep)]);
 return {x0,y0,tear:[...top,[x0+160,y0+36],[x0+148,y0+44],[x0,y0+44]],red:[[x0,y0+44],[x0+148,y0+44],[x0+160,y0+52],[x0+160,y0+72],[x0,y0+168]],
  yellow:[[x0,y0+168],[x0+160,y0+72],...bot.slice(0,1).map(()=>[x0+160,y0+234]),...bot,[x0,y0+234]],notch:[[x0+160,y0+36],[x0+148,y0+44],[x0+160,y0+52]],tip:[x0+148,y0+44]};}
function cram(view,o={},G){
 const V=CV[view],m='cram',{part,states}=mk(o);const fx=V.fx;
 const torsoPts=[[332,366],[692,366],[672,896],[352,896]];
 const body=[];
 body.push(part('cram__body__torso',cs(poly(torsoPts),CR.paper)));
 // sleeve band + timetable (detail)
 const xl=y=>332+(y-366)/530*20,xr=y=>692-(y-366)/530*20;
 let det=cs(poly([[xl(704),704],[xr(704),704],[xr(808),808],[xl(808),808]]),CR.s10);
 for(let c=0;c<6;c++)for(let r=0;r<2;r++){const x=372+fx*0.6+c*52,y=724+r*40;if(x>xl(760)+8&&x+32<xr(760)-8)det+=cf(rect(x,y,32,24),(c+r)%3===0?CR.ink:CR.s25);}
 body.push(part('cram__body__detail',det));
 body.push(part('cram__body__cup-rim',cs(ellipse(512,366,180,40),CR.paper)+cf(ellipse(512,370,148,24),CR.s75)));
 let hp='';
 if(view==='front'){hp=cf(poly([...earc(512,456,204,204,180,360),...earc(512,456,176,176,360,180)]),CR.ink)+cf(rect(284,415,56,110),CR.ink)+cf(rect(684,415,56,110),CR.ink);}
 else if(view==='three-quarter'){hp=cf(poly([...earc(494,456,186,204,180,360),...earc(494,456,158,176,360,180)]),CR.ink)+cf(rect(280,415,56,110),CR.ink)+cf(rect(668,415,30,110),CR.ink);}
 else {hp=cf(poly([...earc(470,456,52,204,180,360),...earc(470,456,26,176,360,180)]),CR.ink)+cf(rect(424,415,92,110),CR.ink)+cf(rect(440,431,60,78),CR.s75);}
 body.push(part('cram__body__headphones',hp));
 // face
 const eye=(id,e)=>{if(!e)return part(id,'');const [x,y,s]=e;return part(id,cf(ellipse(x,y,28*s,28),CR.ink)+cf(ellipse(x+8*s,y-9,7*s,7),CR.paper));};
 const lid=(id,e)=>{const mk2=(cov)=>{if(!e)return '';const [x,y,s]=e;const ly=y-28+56*cov;return cf(rect(x-36*s,y-40,72*s,ly-(y-40)),CR.paper)+cl(pline([[x-34*s,ly],[x+34*s,ly]]));};
  const closed=e?(()=>{const [x,y,s]=e;return cf(rect(x-36*s,y-40,72*s,76),CR.paper)+cl(pline([[x-30*s,y],[x,y+8],[x+30*s,y]]));})():'';
  return states(id,[['open',mk2(0.22)],['half',mk2(0.55)],['closed',closed]],o.lid);};
 const brow=(id,e,inner)=>{const b=(oy,iy)=>{if(!e)return '';const [x,y,s]=e;const xo=x-inner*30*s,xi=x+inner*30*s;return cl(pline([[xo,y+oy],[xi,y+iy]]));};
  return states(id,[['neutral',b(-60,-60)],['raised',b(-74,-80)],['low',b(-54,-44)],['worried',b(-52,-70)]],o.brow);};
 const [mx,my,ms]=V.m;
 const mouth=states('cram__face__mouth',[
  ['neutral',cl(pline([[mx-24*ms,my],[mx+24*ms,my]]))],
  ['smile',cl(`M${P(mx-34*ms,my-6)}Q${P(mx,my+26)} ${P(mx+34*ms,my-6)}`)],
  ['open',cs(`M${P(mx-30*ms,my-8)}L${P(mx+30*ms,my-8)}Q${P(mx+30*ms,my+34)} ${P(mx,my+34)}Q${P(mx-30*ms,my+34)} ${P(mx-30*ms,my-8)}Z`,CR.ink)],
  ['chew',cl(pline([[mx-30*ms,my],[mx-15*ms,my-10],[mx,my],[mx+15*ms,my-10],[mx+30*ms,my]]))],
  ['o',cf(ellipse(mx,my+6,14*ms,18),CR.ink)],
  ['flat',cl(pline([[mx-40*ms,my+4],[mx+40*ms,my+4]]))]],o.mouth);
 const face=[eye('cram__face__eye-l',V.eL),eye('cram__face__eye-r',V.eR),lid('cram__face__lid-l',V.eL),lid('cram__face__lid-r',V.eR),brow('cram__face__brow-l',V.eL,-1),brow('cram__face__brow-r',V.eR,1),mouth];
 // brows: inner direction. eye-r is screen-left in front -> inner = +x ; eye-l inner = -x. (brow fn: inner sign multiplies outer/inner x)
 // limbs
 const arm=(id,s,h)=>{const d=norm(sub(h,s)),w=sub(h,mul(d,20));return part(id,cs(poly(quadPts(s,w,24)),CR.paper));};
 const hand=(id,h)=>part(id,cs(rect(h[0]-20,h[1]-20,40,40),CR.paper));
 const limbs=[arm('cram__limbs__arm-r',...V.armR),arm('cram__limbs__arm-l',...V.armL),hand('cram__limbs__hand-r',V.armR[1]),hand('cram__limbs__hand-l',V.armL[1])];
 // props
 const hR=V.armR[1],sc=[hR[0]-20,hR[1]+116],S=sachetGeo(...sc);
 const mark=G?placeGlyph(G.cram,S.x0+68,S.y0+140,80):'';
 const sachet=part('cram__props__sachet',part('cram__props__sachet__red',cs(poly(S.red),CR.ink))+part('cram__props__sachet__yellow',cs(poly(S.yellow),CR.s25)+mark)+part('cram__props__sachet__tear-strip',cs(poly(S.tear),CR.ink))+part('cram__props__sachet__notch',cf(poly(S.notch),CR.paper)));
 const hL=V.armL[1],FX=hL[0],FT=V.forkTop;
 const fork=part('cram__props__fork',cf(rect(FX-9,FT+52,18,168),CR.ink)+cf(rect(FX-30,FT+32,60,22),CR.ink)+[0,1,2,3].map(i=>cf(rect(FX-30+i*16,FT,12,36),CR.ink)).join(''));
 let pack='';
 if(V.pack==='front')pack=cs(rect(352,420,20,300),CR.s75)+cs(rect(652,420,20,300),CR.s75);
 else if(V.pack==='tq')pack=cs(poly([[300,500],[346,500],[350,780],[304,780]]),CR.s75)+cs(rect(380,420,20,300),CR.s75);
 else pack=cs(rect(252,500,92,290),CR.s75)+cs(rect(268,640,60,90),CR.s50)+cs(rect(400,420,20,300),CR.s75);
 const backpack=part('cram__props__backpack',pack);
 const [tx,ty]=V.timer;const ph=(scr)=>cs(rect(tx,ty,64,106),CR.ink)+cf(rect(tx+10,ty+12,44,70),scr)+cf(rect(tx+16,ty+52,22,12),CR.ink);
 const timer=states('cram__props__phone-timer',[['idle',ph(CR.s10)],['ringing',ph(CR.paper)+cl(pline([[tx-18,ty+20],[tx-18,ty+44]]))+cl(pline([[tx-34,ty+28],[tx-34,ty+52]]))+cl(pline([[tx+82,ty+20],[tx+82,ty+44]]))+cl(pline([[tx+98,ty+28],[tx+98,ty+52]]))]],o.timer);
 const props=[sachet,fork,backpack,timer];
 // noodles + steam (W = 360)
 const ns=[];const W=360;[[-0.18,0.45],[0,0.6],[0.18,0.4]].forEach(([dx,hh],i)=>ns.push(part(`cram__noodles-steam__steam-${i+1}`,clr(pline(steamPts(512+dx*W,350,hh*W,14)),CR.s50))));
 ns.push(part('cram__noodles-steam__noodles',clr(pline(wave(410,368,470,372,5,1.5)),CR.paper)+clr(pline(wave(490,376,560,366,5,1.5)),CR.paper)+cs(poly(ribbon(wave(578,384,588,446,5,1),22)),CR.paper)));
 const two=part('cram__foreground-type__two-mark',G?placeGlyph(G.cram,512+fx*0.9-32*(view==='side'?0.6:1),714,80,view==='side'?0.6:1):'');
 const env=cf(rect(176,896,672,16),CR.ink);
 const wr=(s,h)=>sub(h,mul(norm(sub(h,s)),20));
 const anchors={root:[512,896],'body-pivot':[512,631],'head-pivot':[512,366],'eye-l':V.eL?V.eL.slice(0,2):[V.eR[0]+60,518],'eye-r':V.eR.slice(0,2),mouth:[mx,my],'shoulder-l':V.armL[0],'shoulder-r':V.armR[0],'wrist-l':wr(...V.armL),'wrist-r':wr(...V.armR),'grip-l':V.armL[1],'grip-r':V.armR[1],'steam-origin':[512,366],'sachet-tear':S.tip,'look-at':V.look};
 return {m,slots:{background:'',environment:env,body:body.join(''),face:face.join(''),limbs:limbs.join(''),props:props.join(''),'noodles-steam':ns.join(''),'foreground-type':two},anchors,S};
}

// ================= RIOT =================
const RT={ink:'#14101F',paper:'#FFF6E0',pink:'#FF2E88',green:'#B8F200',blue:'#2B3DFF',tang:'#FF6A13',uv:'#7A2BF5',yolk:'#FFD000',chili:'#E8231A',cyan:'#00D7F0'};
// fill plate at 0,0 + ink keyline plate misregistered 6,6 (texture.misregistration)
const rs=(fn,fill,key=true)=>{OFF=[0,0];const a=fn();let s=`<path d="${a}" fill="${fill}"/>`;if(key){OFF=[6,6];const b=fn();s+=`<path d="${b}" fill="none" stroke="${RT.ink}" stroke-width="20" stroke-linejoin="round" stroke-linecap="round"/>`;}OFF=[0,0];return s;};
const rl=(fn,col=RT.ink)=>{OFF=[0,0];const a=fn();return `<path d="${a}" fill="none" stroke="${col}" stroke-width="20" stroke-linejoin="round" stroke-linecap="round"/>`;};
const RV={
 front:{fx:0,eR:[437,516,1],eL:[587,516,1],m:[512,616,1],armR:[[322,700],[262,650]],armL:[[702,700],[800,600]],look:[512,516]},
 'three-quarter':{fx:55,eR:[498,516,1],eL:[612,516,0.7],m:[566,616,0.85],armR:[[330,700],[270,650]],armL:[[706,700],[805,600]],look:[850,516]},
 side:{fx:120,eR:[612,516,0.8],eL:null,m:[646,616,0.55],armR:[[600,730],[742,700]],armL:[[652,566],[800,452]],look:[1046,516]}};
function riot(view,o={},G){
 const V=RV[view],{part,states}=mk(o),fx=V.fx;
 const torso=()=>`M${P(302,720)}C${P(302,560)} ${P(430,470)} ${P(530,396)}C${P(600,470)} ${P(722,560)} ${P(722,720)}A210 176 0 0 1 ${P(302,720)}Z`;
 const flame=(bx,by,w,h)=>()=>{const lean=h*Math.tan(rad(12)),tx=bx+lean,ty=by-h;return `M${P(bx-w/2,by)}C${P(bx-w/2,by-h*0.5)} ${P(tx-w*0.15,ty+h*0.35)} ${P(tx,ty)}C${P(tx+w*0.1,ty+h*0.4)} ${P(bx+w/2,by-h*0.35)} ${P(bx+w/2,by)}Z`;};
 const body=[];
 body.push((part('riot__body__flame-hair__flame-1',rs(flame(430,530,120,160),RT.chili))+part('riot__body__flame-hair__flame-3',rs(flame(615,530,110,140),RT.chili))+part('riot__body__flame-hair__flame-2',rs(flame(522,430,130,220),RT.yolk))));
 body.push(part('riot__body__torso',rs(torso,RT.chili)));
 // detail: cyan dots on chili (clash pair chili/cyan: no keyline needed)
 body.push(part('riot__body__detail',[[360,780],[452,846],[584,850],[676,776],[640,640]].map(([x,y])=>rs(()=>circle(x+fx*0.5,y,9),RT.cyan,false)).join('')));
 const eye=(id,e,big)=>{if(!e)return part(id,'');const [x,y,s]=e,r=big?36:24,pr=big?15:11;return part(id,rs(()=>ellipse(x,y,r*s,r),RT.paper)+rs(()=>ellipse(x+(r-pr-6)*0.3*s,y+2,pr*s,pr),RT.ink,false));};
 const lid=(id,e,big)=>{const r=big?36:24;const mk2=(cov)=>{if(!e)return '';const [x,y,s]=e;const ly=y-r+2*r*cov;return rs(()=>`M${P(x-(r+8)*s,ly)}L${P(x-(r+8)*s,y-r-10)}L${P(x+(r+8)*s,y-r-10)}L${P(x+(r+8)*s,ly)}Z`,RT.chili,false)+rl(()=>pline([[x-r*s,ly],[x+r*s,ly]]));};
  const closed=e?(()=>{const [x,y,s]=e;return rs(()=>`M${P(x-(r+8)*s,y+r+6)}L${P(x-(r+8)*s,y-r-10)}L${P(x+(r+8)*s,y-r-10)}L${P(x+(r+8)*s,y+r+6)}Z`,RT.chili,false)+rl(()=>`M${P(x-r*s,y)}Q${P(x,y+r*0.7)} ${P(x+r*s,y)}`);})():'';
  return states(id,[['open',mk2(0)],['half',mk2(0.5)],['closed',closed]],o.lid);};
 const brow=(id,e,inner,big)=>{const r=big?36:24;const b=(oy,iy)=>{if(!e)return '';const [x,y,s]=e;return rl(()=>pline([[x-inner*(r+6)*s,y-r+oy],[x+inner*(r+6)*s,y-r+iy]]));};
  return states(id,[['neutral',b(-22,-22)],['raised',b(-40,-48)],['low',b(-16,-4)],['worried',b(-14,-36)]],o.brow);};
 const [mx,my,ms]=V.m;
 const mouth=states('riot__face__mouth',[
  ['neutral',rl(()=>`M${P(mx-30*ms,my)}Q${P(mx,my+8)} ${P(mx+30*ms,my-4)}`)],
  ['smile',rl(()=>`M${P(mx-44*ms,my-10)}Q${P(mx,my+40)} ${P(mx+44*ms,my-14)}`)],
  ['open',rs(()=>`M${P(mx-40*ms,my-10)}L${P(mx+40*ms,my-14)}Q${P(mx+36*ms,my+46)} ${P(mx,my+46)}Q${P(mx-38*ms,my+46)} ${P(mx-40*ms,my-10)}Z`,RT.ink,false)+rs(()=>ellipse(mx+4*ms,my+30,18*ms,10),RT.chili,false)],
  ['chew',rl(()=>pline([[mx-34*ms,my],[mx-17*ms,my-12],[mx,my+2],[mx+17*ms,my-12],[mx+34*ms,my]]))],
  ['o',rs(()=>ellipse(mx,my+8,16*ms,22),RT.ink,false)],
  ['flat',rl(()=>pline([[mx-44*ms,my+2],[mx+44*ms,my-2]]))]],o.mouth);
 const face=[eye('riot__face__eye-l',V.eL,false),eye('riot__face__eye-r',V.eR,true),lid('riot__face__lid-l',V.eL,false),lid('riot__face__lid-r',V.eR,true),brow('riot__face__brow-l',V.eL,-1,false),brow('riot__face__brow-r',V.eR,1,true),mouth];
 const arm=(id,s,h)=>{const d=norm(sub(h,s)),w=sub(h,mul(d,18));return part(id,rs(()=>poly(quadPts(s,w,20)),RT.chili));};
 const hand=(id,h)=>part(id,rs(()=>circle(h[0],h[1],22),RT.chili));
 const limbs=[arm('riot__limbs__arm-r',...V.armR),arm('riot__limbs__arm-l',...V.armL),hand('riot__limbs__hand-r',V.armR[1]),hand('riot__limbs__hand-l',V.armL[1])];
 const hR=V.armR[1],sc=view==='side'?[hR[0]+50,hR[1]-30]:[hR[0]-46,hR[1]-30],S=sachetGeo(...sc);
 const mark=G?placeGlyph(G.riotCore,S.x0+68,S.y0+140,80):'';
 const sachet=part('riot__props__sachet',part('riot__props__sachet__red',rs(()=>poly(S.red),RT.chili))+part('riot__props__sachet__yellow',rs(()=>poly(S.yellow),RT.yolk)+mark)+part('riot__props__sachet__tear-strip',rs(()=>poly(S.tear),RT.chili))+part('riot__props__sachet__notch',rl(()=>pline(S.notch))));
 const hL=V.armL[1];const px=hL[0]-35,py=hL[1]-150;
 const phone=part('riot__props__phone',rs(()=>rect(px,py,70,132),RT.ink)+rs(()=>rect(px+10,py+12,50,96),RT.cyan,false));
 const star=(cx,cy,ro,ri,n)=>()=>{const p=[];for(let k=0;k<n*2;k++){const a=rad(-90+k*180/n),r=k%2?ri:ro;p.push([cx+r*Math.cos(a),cy+r*Math.sin(a)]);}return poly(p);};
 const gloss=(x,y,l)=>`<path d="${pline([[x,y],[x+l*Math.sin(rad(35)),y-l*Math.cos(rad(35))]])}" fill="none" stroke="${RT.paper}" stroke-opacity="0.6" stroke-width="12" stroke-linecap="round"/>`;
 const stickers=part('riot__props__stickers',rs(star(392+fx*0.4,742,40,26,8),RT.yolk)+gloss(376+fx*0.4,746,16)+rs(()=>circle(648+fx*0.3,706,22),RT.cyan,false)+gloss(638+fx*0.3,708,8));
 const chili=part('riot__props__chili',rs(()=>`M${P(168,872)}C${P(190,838)} ${P(262,838)} ${P(298,858)}C${P(290,884)} ${P(222,892)} ${P(168,872)}Z`,RT.chili)+rs(()=>poly([[296,846],[320,834],[326,846],[304,862]]),RT.green));
 const bx=view==='side'?150:790;
 const bottle=part('riot__props__chili-oil-bottle',rs(()=>rect(bx+16,752,26,40),RT.ink)+rs(()=>rect(bx,790,58,106),RT.chili)+rs(()=>rect(bx,820,58,34),RT.yolk));
 const props=[sachet,phone,stickers,chili,bottle];
 const ns=[];const W=170,ox=566,oy=192;[[-0.18,0.45],[0,0.6],[0.18,0.4]].forEach(([dx,hh],i)=>ns.push(part(`riot__noodles-steam__steam-${i+1}`,rl(()=>pline(steamPts(ox+dx*W,oy-(i===1?0:14),hh*W,8))))));
 {const pts=[];for(let i=0;i<=24;i++){const t=i/24;pts.push([mx-4+6*Math.sin(t*Math.PI*2),my+14+110*t]);}ns.push(part('riot__noodles-steam__noodles',rs(()=>poly(ribbon(pts,34)),RT.yolk)));}
 const two=part('riot__foreground-type__two-mark',G?placeGlyph(G.riot,512+fx*0.6-38*(view==='side'?0.6:1),730,96,view==='side'?0.6:1):'');
 const env=rs(()=>ellipse(518,902,250,18),RT.ink,false);
 const wr=(s,h)=>sub(h,mul(norm(sub(h,s)),20));
 const anchors={root:[512,896],'body-pivot':[512,660],'head-pivot':[512,470],'eye-l':V.eL?V.eL.slice(0,2):[V.eR[0]+60,516],'eye-r':V.eR.slice(0,2),mouth:[mx,my],'shoulder-l':V.armL[0],'shoulder-r':V.armR[0],'wrist-l':wr(...V.armL),'wrist-r':wr(...V.armR),'grip-l':V.armL[1],'grip-r':V.armR[1],'steam-origin':[ox,oy],'sachet-tear':S.tip,'look-at':V.look};
 return {m:'riot',slots:{background:'',environment:env,body:body.join(''),face:face.join(''),limbs:limbs.join(''),props:props.join(''),'noodles-steam':ns.join(''),'foreground-type':two},anchors,S};
}
function rigSvg(r,comment){return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">\n<!-- ${comment} -->\n`+wrapSvg(r.m,r.slots,r.anchors)+'</svg>\n';}
function inner(r){return wrapSvg(r.m,r.slots,r.anchors).replace(/ id="[^"]*"/g,'');}
return {cram,riot,rigSvg,inner,glyphLayers,placeGlyph,CR,RT,helpers:{P,f,poly,pline,rect,circle,ellipse,earc,ribbon,wave,steamPts,quadPts,rs,rl,cs,cf,cl,clr,sachetGeo,setOff:v=>{OFF=v;}}};
