// Generates glyphs/NN-slug/NN-mascot-two.svg and stress-tests/scale/two-glyph-scale-test.svg
// Construction box 320 x 400 (1:1.25), cap height 320 (80%), baseline y=400. Min stroke 40 (12.5%).
const R=v=>Math.round(v*2)/2, f=v=>{const r=R(v);return Number.isInteger(r)?String(r):r.toFixed(1)}, P=(x,y)=>f(x)+' '+f(y);
const add=(a,b)=>[a[0]+b[0],a[1]+b[1]],sub=(a,b)=>[a[0]-b[0],a[1]-b[1]],mul=(a,s)=>[a[0]*s,a[1]*s],dot=(a,b)=>a[0]*b[0]+a[1]*b[1],norm=a=>{const l=Math.hypot(a[0],a[1])||1;return [a[0]/l,a[1]/l]};
const rad=d=>d*Math.PI/180;
const poly=pts=>'M'+pts.map(p=>P(p[0],p[1])).join('L')+'Z';
const rect=(x,y,w,h)=>`M${P(x,y)}H${f(x+w)}V${f(y+h)}H${f(x)}Z`;
const circle=(cx,cy,r)=>`M${P(cx-r,cy)}A${f(r)} ${f(r)} 0 1 1 ${P(cx+r,cy)}A${f(r)} ${f(r)} 0 1 1 ${P(cx-r,cy)}Z`;
function strokeOutline(pts,ws,cap='butt',ml=3){
  const n=pts.length,L=[],Rr=[];
  for(let i=0;i<n;i++){
    const d0=i>0?norm(sub(pts[i],pts[i-1])):null,d1=i<n-1?norm(sub(pts[i+1],pts[i])):null,hw=ws[i]/2;
    if(d0&&d1){const n0=[-d0[1],d0[0]],n1=[-d1[1],d1[0]],m=norm(add(n0,n1)),c=dot(m,n1),len=hw/Math.max(c,1e-3);
      if(len>hw*ml){L.push(add(pts[i],mul(n0,hw)),add(pts[i],mul(n1,hw)));Rr.push(sub(pts[i],mul(n0,hw)),sub(pts[i],mul(n1,hw)));continue;}
      L.push(add(pts[i],mul(m,len)));Rr.push(sub(pts[i],mul(m,len)));}
    else{const d=d0||d1,nn=[-d[1],d[0]];let p=pts[i];if(cap==='square')p=i===0?sub(p,mul(d,hw)):add(p,mul(d,hw));L.push(add(p,mul(nn,hw)));Rr.push(sub(p,mul(nn,hw)));}
  }
  const out=[...L];
  if(cap==='round'){const E=pts[n-1],d=norm(sub(pts[n-1],pts[n-2])),nn=[-d[1],d[0]],hw=ws[n-1]/2;for(let k=1;k<16;k++){const th=Math.PI*k/16;out.push(add(E,add(mul(nn,hw*Math.cos(th)),mul(d,hw*Math.sin(th)))));}}
  out.push(...Rr.reverse());
  if(cap==='round'){const S=pts[0],d=norm(sub(pts[1],pts[0])),nn=[-d[1],d[0]],hw=ws[0]/2;for(let k=1;k<16;k++){const th=Math.PI*k/16;out.push(sub(S,add(mul(nn,hw*Math.cos(th)),mul(d,hw*Math.sin(th)))));}}
  return poly(out);
}
const S=(pts,w,cap)=>({pts,ws:pts.map((p,i)=>typeof w==='function'?w(i/(pts.length-1),p,i):w),cap});
const arc=(cx,cy,r,a0,a1,n=64,rf)=>{const o=[];for(let i=0;i<=n;i++){const t=i/n,a=a0+(a1-a0)*t,rr=rf?rf(t,a):r;o.push([cx+rr*Math.cos(rad(a)),cy+rr*Math.sin(rad(a))]);}return o;};
const line=(a,b,n=16)=>{const o=[];for(let i=0;i<=n;i++){const t=i/n;o.push([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]);}return o;};
const qbez=(a,c,b,n=24)=>{const o=[];for(let i=0;i<=n;i++){const t=i/n,u=1-t;o.push([u*u*a[0]+2*u*t*c[0]+t*t*b[0],u*u*a[1]+2*u*t*c[1]+t*t*b[1]]);}return o;};
const join=(...ps)=>ps.reduce((acc,p)=>acc.length?acc.concat(p.slice(1)):p.slice(),[]);
const G={};
// 01 Cram: top = cup-rim ellipse, monoline 48, square terminals (fork tines removed at QA: below 40-unit floor)
G.cram=()=>{const top=[];for(let i=0;i<=48;i++){const a=180+180*i/48;top.push([160+104*Math.cos(rad(a)),140+36*Math.sin(rad(a))]);}
 const pts=join([[56,208],[56,140]],top,line([264,140],[264,232],8),line([264,232],[72,376],16));
 return {strokes:[S(pts,48,'butt')],polys:[rect(32,352,256,48)]};};
// 02 Riot: flame-curl bowl (flared tapering tip), heavy mismatched widths, die-cut sticker
G.riot=()=>{const cx=160,cy=214,r=96,a0=150,a1=395;const bowl=arc(cx,cy,r,a0,a1,64,(t,a)=>a<215?r+22*Math.pow((215-a)/65,1.4):r);
 const nb=bowl.length,E=bowl[nb-1],diag=line(E,[80,354],16),pts=join(bowl,diag);
 const w=(t,p,i)=>{if(i<nb){const a=a0+(a1-a0)*i/(nb-1);return a<215?40+16*Math.pow((a-a0)/65,0.7):56;}return 56+4*(i-nb+1)/16;};
 return {strokes:[S(pts,w,'round'),S(line([70,354],[258,354],16),72,'round')],polys:[circle(E[0],E[1],27)],sticker:{cut:6,key:10,dx:6,dy:6}};};
// 03 Nest: one continuous yarn-noodle line with a small loop, round terminals
G.nest=()=>{const w=48,cx=160,cy=200,r=96,lc=[92,340],lr=36;const bowl=arc(cx,cy,r,160,392,64);const E=bowl[bowl.length-1];
 const diag=qbez(E,[190,300],[lc[0],lc[1]+lr],24);const loopA=arc(lc[0],lc[1],lr,90,270,32),loopB=arc(lc[0],lc[1],lr,270,450,32);
 return {strokes:[S(join(bowl,diag,loopA),w,'round'),S(join(loopB,line([lc[0],lc[1]+lr],[264,376],16)),w,'round')],polys:[]};};
// 04 Sprig: a stem with organic stress, leaf at the hook (35deg from vertical)
G.sprig=()=>{const cx=160,cy=198,r=96;const bowl=arc(cx,cy,r,165,392,64);const nb=bowl.length,E=bowl[nb-1];
 const diag=qbez(E,[150,300],[60,378],24),base=line([60,378],[272,378],16),pts=join(bowl,diag,base);
 const w=(t,p,i)=>i<nb?46+6*Math.cos(rad(165+227*i/(nb-1))):44;
 const B=bowl[0],ang=rad(35),dir=[-Math.sin(ang),-Math.cos(ang)],nn=[-dir[1],dir[0]],leaf=[];
 for(let i=0;i<=24;i++){const t=i/24;leaf.push(add(add(B,mul(dir,96*t)),mul(nn,24*Math.sin(Math.PI*t))));}for(let i=23;i>0;i--){const t=i/24;leaf.push(sub(add(B,mul(dir,96*t)),mul(nn,24*Math.sin(Math.PI*t))));}
 return {strokes:[S(pts,w,'round')],polys:[poly(leaf)]};};
// 05 Lull: filled crescent-moon bowl + steam-tail S diagonal, soft and wide
G.lull=()=>{const cx=160,cy=221,r=98;const wf=a=>{const d=a-320;return Math.abs(d)<150?44+56*(0.5+0.5*Math.cos(d*Math.PI/150)):44;};
 const bowl=arc(cx,cy,r,160,390,72);const E=bowl[bowl.length-1],B=[56,374];const tail=[],dv=norm(sub(B,E)),pn=[-dv[1],dv[0]];
 for(let i=0;i<=32;i++){const t=i/32;tail.push(add([E[0]+(B[0]-E[0])*t,E[1]+(B[1]-E[1])*t],mul(pn,14*Math.sin(2*Math.PI*t))));}
 const nb=bowl.length,ew=wf(390);
 return {strokes:[S(join(bowl,tail),(t,p,i)=>i<nb?wf(160+230*i/(nb-1)):ew+(48-ew)*(i-nb+1)/32,'round'),S(line([50,374],[270,374],16),52,'round')],polys:[circle(E[0],E[1],ew/2-1)]};};
// 06 Stack: three stacked blocks on the 8-unit grid, stencil gaps 16, square corners, butt
G.stack=()=>({strokes:[],polys:[poly([[48,80],[272,80],[272,216],[224,216],[224,128],[96,128],[96,192],[48,192]]),poly([[192,232],[272,232],[128,336],[48,336]]),rect(48,352,232,48)]});
// 07 Mise: high-contrast didone (40 hairline / 104 swell), ball terminal, chopstick-straight base
G.mise=()=>{const cx=160,cy=194,r=94;const wf=a=>{const d=a-370;return Math.abs(d)<80?40+64*Math.cos(d*Math.PI/160):40;};
 const bowl=arc(cx,cy,r,175,400,72),nb=bowl.length,E=bowl[nb-1],ew=wf(400),diag=qbez(E,[150,300],[60,360],24);
 return {strokes:[S(join(bowl,diag),(t,p,i)=>i<nb?wf(175+225*i/(nb-1)):ew+(40-ew)*(i-nb+1)/24,'butt')],polys:[circle(70,216,34),rect(20,352,280,48),circle(E[0],E[1],ew/2-1)]};};
const META={cram:['01','01-hostel-hungry','#000000','#FFFFFF'],riot:['02','02-maximalist-foodie','#14101F','#FFF6E0'],nest:['03','03-practical-parent','#4A2A18','#FFF3E0'],sprig:['04','04-conscious-upgrader','#26321F','#F2EDE1'],lull:['05','05-midnight-recharger','#E4DDF2','#121127'],stack:['06','06-value-stocking-homemaker','#14213D','#F5EBD7'],mise:['07','07-premium-flavor-explorer','#F4EBDC','#4A1416']};
const grow=(st,g)=>({...st,ws:st.ws.map(w=>w+2*g),cap:'round'});
const shift=(st,dx,dy)=>({...st,pts:st.pts.map(p=>[p[0]+dx,p[1]+dy])});
const paths=(arr)=>arr.map(s=>`<path d="${strokeOutline(s.pts,s.ws,s.cap)}"/>`).join('');
function glyphMarkup(m,ink,paper,mono){const g=G[m]();const core=[...g.strokes.map(s=>strokeOutline(s.pts,s.ws,s.cap)),...g.polys];
 const id=`${m}__foreground-type__two-mark`;
 if(g.sticker&&!mono){const k=g.sticker,outer=g.strokes.map(s=>grow(s,k.key)),cut=g.strokes.map(s=>grow(s,k.cut));
  return `<g id="${id}">\n<g id="${id}__shadow" fill="${ink}">${paths(outer.map(s=>shift(s,k.dx,k.dy)))}</g>\n<g id="${id}__keyline" fill="${ink}">${paths(outer)}</g>\n<g id="${id}__die-cut" fill="${paper}">${paths(cut)}</g>\n<g id="${id}__core" fill="${ink}">${core.map(d=>`<path d="${d}"/>`).join('')}</g>\n</g>`;}
 return `<g id="${id}" fill="${ink}">\n${core.map(d=>`<path d="${d}"/>`).join('\n')}\n</g>`;}
const order=['cram','riot','nest','sprig','lull','stack','mise'];
const files={};
for(const m of order){const [nn,slug,ink,paper]=META[m];
 files[`glyphs/${slug}/${nn}-${m}-two.svg`]=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 400" width="320" height="400">\n<!-- ${nn}-${m} "2" | box 1:1.25, cap height 320 = 80% (y 80-400), baseline y 400 | fill = role.text ${ink}${m==='riot'?', die-cut = role.bg '+paper:''} -->\n${glyphMarkup(m,ink,paper,false)}\n</svg>\n`;}
const sizes=[16,32,64,512],pad=32,panelW=pad+sizes.reduce((a,s)=>a+s*0.8+pad,0),panelH=512+2*pad,gap=16;
const W=Math.ceil(panelW*2+gap),H=order.length*panelH+(order.length-1)*gap;
let out=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">\n<!-- rows 01-07 (cram riot nest sprig lull stack mise); per row: left = role.text on role.bg, right = #000000 on #FFFFFF; sizes = construction-box height 16/32/64/512 px, baseline aligned -->\n`;
order.forEach((m,ri)=>{const [nn,slug,ink,paper]=META[m],y0=ri*(panelH+gap);
 [['colour',ink,paper,false,0],['bw','#000000','#FFFFFF',true,panelW+gap]].forEach(([k,i,p,mono,x0])=>{
  out+=`<g id="${m}-${k}">\n<rect x="${f(x0)}" y="${y0}" width="${f(panelW)}" height="${panelH}" fill="${p}"/>\n`;let x=x0+pad;
  for(const s of sizes){const w=s*0.8;out+=`<svg id="${m}-${k}-${s}" x="${f(x)}" y="${y0+pad+512-s}" width="${f(w)}" height="${s}" viewBox="0 0 320 400" overflow="visible">${glyphMarkup(m,i,p,mono).replace(/ id="[^"]*"/g,'')}</svg>\n`;x+=w+pad;}
  out+=`</g>\n`;});});
out+='</svg>\n';files['stress-tests/scale/two-glyph-scale-test.svg']=out;
return {files,W,H};
