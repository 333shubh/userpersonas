// Gate 2 sheets, scenes, boards for Cram + Riot. Call with (L, T, F, G). Returns {path: svg}.
const H=L.helpers,{rect,circle,ellipse,poly,pline,f}=H;
const CR=L.CR,RT=L.RT;
const EXP={neutral:['open','neutral','neutral'],happy:['open','raised','smile'],excited:['open','raised','open'],focused:['half','low','flat'],content:['half','neutral','smile'],surprised:['open','raised','o'],tired:['half','worried','flat'],sleepy:['closed','neutral','neutral']};
const svgOpen=(w,h,c)=>`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}">\n<!-- ${c} -->\n`;
const place=(x,y,s,inner)=>`<g transform="translate(${f(x)} ${f(y)}) scale(${s})">${inner}</g>\n`;
const txt=(font,str,x,y,size,fill,track=0,anchor='start')=>{const w=T.textW(F[font],str,size,track);const x0=anchor==='middle'?x-w/2:anchor==='end'?x-w:x;return `<path d="${T.textD(F[font],str,x0,y,size,track)}" fill="${fill}"/>`;};
const M={
 cram:{nn:'01',slug:'01-hostel-hungry',name:'CRAM',fn:L.cram,C:CR,bg:CR.paper,ink:CR.ink,muted:CR.s75,disp:'archivo',text:'plex',textB:'plexb',dT:0.02,lT:0.08},
 riot:{nn:'02',slug:'02-maximalist-foodie',name:'RIOT',fn:L.riot,C:RT,bg:RT.paper,ink:RT.ink,muted:RT.uv,disp:'bungee',text:'rubik',textB:'rubik',dT:0.01,lT:0.05}};
const out={};
const head=(k,title,W)=>{const m=M[k];return txt(m.disp,`${m.nn} ${m.name}`,80,130,72,m.ink,m.dT)+txt(m.text,title.toUpperCase(),80+T.textW(F[m.disp],`${m.nn} ${m.name}`,72,m.dT)+40,128,28,m.muted,m.lT)+`<path d="${rect(80,164,W-160,4)}" fill="${m.ink}"/>`;};
const topParts={cram:['cram__body__torso','cram__body__detail','cram__body__cup-rim','cram__body__headphones','cram__face__eye-l','cram__face__eye-r','cram__face__lid-l','cram__face__lid-r','cram__face__brow-l','cram__face__brow-r','cram__face__mouth','cram__limbs__arm-r','cram__limbs__arm-l','cram__limbs__hand-r','cram__limbs__hand-l','cram__props__sachet','cram__props__fork','cram__props__backpack','cram__props__phone-timer','cram__noodles-steam__steam-1','cram__noodles-steam__steam-2','cram__noodles-steam__steam-3','cram__noodles-steam__noodles','cram__foreground-type__two-mark'],
 riot:['riot__body__flame-hair__flame-1','riot__body__flame-hair__flame-2','riot__body__flame-hair__flame-3','riot__body__torso','riot__body__detail','riot__face__eye-l','riot__face__eye-r','riot__face__lid-l','riot__face__lid-r','riot__face__brow-l','riot__face__brow-r','riot__face__mouth','riot__limbs__arm-r','riot__limbs__arm-l','riot__limbs__hand-r','riot__limbs__hand-l','riot__props__sachet','riot__props__phone','riot__props__stickers','riot__props__chili','riot__props__chili-oil-bottle','riot__noodles-steam__steam-1','riot__noodles-steam__steam-2','riot__noodles-steam__steam-3','riot__noodles-steam__noodles','riot__foreground-type__two-mark']};
const ex=(k,e)=>{const [lid,brow,mouth]=EXP[e];return {lid,brow,mouth};};
const char=(k,view,o)=>L.inner(M[k].fn(view,o||{},G));
for(const k of ['cram','riot']){const m=M[k],base=`static/${m.slug}/${m.nn}-${k}`;
 // ---------- turnaround ----------
 {const W=3232,Hh=1400;let s=svgOpen(W,Hh,`${m.nn}-${k} turnaround: front / three-quarter / side, scale 1, shared ground y 1096 | state-swap only, colours from persona tokens`)+`<rect width="${W}" height="${Hh}" fill="${m.bg}"/>`+head(k,'Turnaround',W);
  [['front','FRONT'],['three-quarter','THREE-QUARTER'],['side','SIDE']].forEach(([v,lab],i)=>{const x=80+i*1036;s+=place(x,200,1,char(k,v));s+=txt(m.text,lab,x+512,1180,28,m.ink,m.lT,'middle');});
  [[200+366,'head-pivot y 366'],[200+896,'ground y 896']].forEach(([y,l])=>{s+=`<path d="${pline([[80,y],[W-80,y]])}" fill="none" stroke="${m.muted}" stroke-width="2" stroke-dasharray="12 12"/>`+txt(m.text,l,W-80,y-12,20,m.muted,0,'end');});
  s+=txt(m.text,'Rig spec v0.1.1 · 1024 canvas per view · rigs: '+`${m.nn}-${k}-rig-front / -three-quarter / -side.svg`,80,1330,24,m.muted);out[`${base}-sheet-turnaround.svg`]=s+'</svg>\n';}
 // ---------- expressions ----------
 {const sc=0.72,cw=760,W=80*2+cw*4,Hh=240+2*(1024*sc+120);let s=svgOpen(W,Hh,`${m.nn}-${k} expressions: 8 by lid/brow/mouth state swap only (rig-spec.json expressions), front view`)+`<rect width="${W}" height="${Hh}" fill="${m.bg}"/>`+head(k,'Expressions · state swap only',W);
  Object.keys(EXP).forEach((e,i)=>{const cx=80+(i%4)*cw,cy=220+Math.floor(i/4)*(1024*sc+120);s+=place(cx+(cw-1024*sc)/2,cy-60*sc,sc,char(k,'front',ex(k,e)));
   s+=txt(m.textB,e.toUpperCase(),cx+cw/2,cy+1024*sc-10,30,m.ink,m.lT,'middle')+txt(m.text,EXP[e].join(' / '),cx+cw/2,cy+1024*sc+30,22,m.muted,0,'middle');});
  out[`${base}-sheet-expressions.svg`]=s+'</svg>\n';}
 // ---------- poses ----------
 {const hop=Object.fromEntries(topParts[k].map(id=>[id,'translate(0 -48)']));
  const tear={[`${k}__props__sachet__tear-strip`]:'translate(-28 -64)'};
  const poses=k==='cram'?[
   ['IDLE','three-quarter',{},'neutral · timer idle'],
   ['SACHET MOMENT','front',{...ex(k,'focused'),tf:tear},'focused · tear-strip off · whole sachet in'],
   ['REACTION','front',{...ex(k,'surprised'),timer:'ringing',tf:{...hop}},'surprised · timer ringing · hop 48']]:[
   ['IDLE','three-quarter',{},'neutral · phone up'],
   ['SACHET MOMENT','front',{...ex(k,'excited'),tf:tear},'excited · tear-strip off · remix starts'],
   ['REACTION','three-quarter',{...ex(k,'happy'),tf:{...hop,[`riot__noodles-steam__steam-2`]:'translate(0 -72)'}},'happy · hop 48 · steam up']];
  const W=3232,Hh=1420;let s=svgOpen(W,Hh,`${m.nn}-${k} poses: idle, sachet moment, reaction | translate() on named parts + state swaps only`)+`<rect width="${W}" height="${Hh}" fill="${m.bg}"/>`+head(k,'Poses',W);
  poses.forEach(([lab,v,o,note],i)=>{const x=80+i*1036;s+=place(x,220,1,char(k,v,o));s+=txt(m.textB,lab,x+512,1210,30,m.ink,m.lT,'middle')+txt(m.text,note,x+512,1252,22,m.muted,0,'middle');});
  out[`${base}-sheet-poses.svg`]=s+'</svg>\n';}
 // ---------- props ----------
 {const P=k==='cram'?[['sachet','front',[220,716],1.6],['fork','front',[800,510],1.7],['headphones','front',[512,470],1.1],['backpack','side',[326,620],1.1],['phone-timer','front',[818,835],3]]:[['sachet','front',[216,620],1.6],['phone','front',[800,516],2.6],['stickers','front',[520,724],1.6],['chili','front',[247,862],2.6],['chili-oil-bottle','front',[819,824],2.6]];
  const cw=600,W=80*2+cw*5+16,Hh=900;let s=svgOpen(W,Hh,`${m.nn}-${k} props: each prop isolated from the rig (same geometry, scaled for the sheet)`)+`<rect width="${W}" height="${Hh}" fill="${m.bg}"/>`+head(k,'Props',W);
  const parts={cram:{headphones:'cram__body__headphones'},riot:{}};
  P.forEach(([p,v,c,sc],i)=>{const id=(parts[k][p])||`${k}__props__${p}`;const cx=80+i*(cw+4)+cw/2,cy=470;
   s+=`<path d="${rect(80+i*(cw+4),220,cw,500)}" fill="${k==='cram'?CR.s10:RT.paper}" stroke="${m.ink}" stroke-width="${k==='cram'?4:6}"/>`;
   s+=place(cx-c[0]*sc,cy-c[1]*sc,sc,L.inner(M[k].fn(v,{only:[id]},G)));
   s+=txt(m.textB,p.toUpperCase(),cx,780,28,m.ink,m.lT,'middle')+txt(m.text,id,cx,820,20,m.muted,0,'middle');});
  out[`${base}-sheet-props.svg`]=s+'</svg>\n';}
}
// ================= SCENES =================
{const W=1920,Hh=1080,c=CR;let s=svgOpen(W,Hh,'01-cram scene · 13:00 hostel desk · flat fluorescent, hard shadows · density 2 (5 props, >= 50% negative space) · one ink + screens')+
 `<defs><pattern id="cram-halftone-25" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><circle cx="6" cy="6" r="3.4" fill="${c.ink}"/></pattern><pattern id="cram-halftone-10" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><circle cx="6" cy="6" r="2.1" fill="${c.ink}"/></pattern></defs>\n`;
 s+=`<rect width="${W}" height="${Hh}" fill="${c.paper}"/>`;
 // fluorescent tube
 s+=`<path d="${rect(560,0,800,24)}" fill="${c.ink}"/>`+H.cs(rect(600,24,720,36),c.paper)+`<path d="${rect(560,60,800,8)}" fill="${c.ink}"/>`;
 // wall timetable, pasted 1.5deg, 2 staples
 const tt=[[1280,130],[1640,121],[1650,480],[1290,489]];s+=H.cs(poly(tt),c.paper);
 for(let r=1;r<6;r++){const y=130+r*60;s+=H.cl(pline([[1281+r*1.6,y],[1641+r*1.6,y-9]]))};
 for(let q=1;q<4;q++){const x=1280+q*90;s+=`<path d="${pline([[x,130-q*2.2],[x+10,488-q*2.2]])}" fill="none" stroke="${c.ink}" stroke-width="4"/>`;}
 [[1400,152],[1560,142]].forEach(([x,y],i)=>s+=`<path d="${poly([[x,y],[x+24,y-0.6],[x+24.2,y+5.4],[x+0.2,y+6]])}" fill="${c.ink}"/>`);
 [[1306,206],[1486,196],[1396,326],[1576,316],[1306,386],[1486,380]].forEach(([x,y])=>s+=`<path d="${rect(x,y,72,32)}" fill="${c.s75}"/>`);
 // hard wall shadow (straight down, fluorescent overhead) as halftone
 s+=`<path d="${poly([[1290,489],[1650,480],[1658,524],[1298,532]])}" fill="url(#cram-halftone-25)"/>`;
 // desk
 s+=`<path d="${rect(0,780,W,300)}" fill="${c.s10}"/>`+`<path d="${rect(0,772,W,16)}" fill="${c.ink}"/>`+`<path d="${rect(0,820,W,260)}" fill="url(#cram-halftone-10)"/>`;
 // kettle (prop 5) + hard shadow
 s+=`<path d="${poly([[1360,780],[1600,780],[1640,860],[1400,860]])}" fill="${c.s50}"/>`;
 s+=H.cs(rect(1380,560,200,220),c.s75)+H.cs(rect(1580,600,52,120),c.paper)+H.cs(rect(1420,520,120,40),c.ink)+H.cs(rect(1400,700,160,24),c.ink);
 // mascot shadow + mascot (three-quarter, focused, timer running)
 const sc=0.74,mx=440,my=788-896*sc;
 s+=`<path d="${poly([[mx+300*sc,788],[mx+760*sc,788],[mx+900*sc,872],[mx+420*sc,872]])}" fill="${c.s50}"/>`;
 s+=place(mx,my,sc,char('cram','three-quarter',{...ex('cram','focused')}));
 out['static/01-hostel-hungry/01-cram-scene.svg']=s+'</svg>\n';}
{const W=1920,Hh=1080,c=RT,rs=H.rs;let s=svgOpen(W,Hh,'02-riot scene · 19:30 counter shoot · coloured practicals (yolk pendant, pink/green neon, cyan phone glow) · density 5 · regions: wall {ultraviolet,yolk,cyan} neon {hot-pink,acid-green} counter-top {yolk,chili} counter-front {volt-blue,tangerine}');
 s+=`<rect width="${W}" height="${Hh}" fill="${c.uv}"/>`;
 // pendant lamp + yolk light pool (ultraviolet/yolk = clash pair: touch without keyline)
 s+=`<path d="${ellipse(560,250,300,190)}" fill="${c.yolk}"/>`+`<path d="${rect(552,0,16,110)}" fill="${c.ink}"/>`+rs(()=>`M${H.P(470,190)}L${H.P(650,190)}L${H.P(610,110)}L${H.P(510,110)}Z`,c.ink,false)+`<path d="${ellipse(560,196,64,14)}" fill="${c.paper}"/>`;
 // neon on ink board: pink/green pair
 s+=`<path d="${rect(1300,110,500,330)}" fill="${c.ink}"/>`;
 const burst=(cx,cy,ro,ri,n)=>{const p=[];for(let i=0;i<n*2;i++){const a=(-90+i*180/n)*Math.PI/180,r=i%2?ri:ro;p.push([cx+r*Math.cos(a),cy+r*Math.sin(a)]);}return poly(p);};
 s+=`<path d="${burst(1460,275,120,72,12)}" fill="${c.pink}"/>`+`<path d="${burst(1460,275,60,36,12)}" fill="${c.green}"/>`+`<path d="${ellipse(1660,275,82,82)}" fill="none" stroke="${c.green}" stroke-width="20"/>`+`<path d="${pline([[1610,325],[1710,225]])}" fill="none" stroke="${c.pink}" stroke-width="20" stroke-linecap="round"/>`;
 // counter top (ink edge) + front face volt-blue with tangerine trim (pair)
 s+=`<path d="${rect(0,800,W,30)}" fill="${c.ink}"/>`+`<path d="${rect(0,830,W,250)}" fill="${c.blue}"/>`+`<path d="${rect(0,830,W,28)}" fill="${c.tang}"/>`;
 [[200,960,'REMIX'],[1230,970,'+OIL'],[1620,950,'2:00']].forEach(([x,y,l],i)=>{const r=i===1?62:74;s+=rs(()=>i===1?circle(x,y,r):burst(x,y,r,r*0.78,10),c.paper);s+=txt('bungee',l,x,y+9,i===1?26:22,c.ink,0.01,'middle');});
 // counter-top items: bowl + torn sachet (yolk/chili region)
 s+=rs(()=>`M${H.P(1180,700)}L${H.P(1500,700)}C${H.P(1500,780)} ${H.P(1420,804)} ${H.P(1340,804)}C${H.P(1260,804)} ${H.P(1180,780)} ${H.P(1180,700)}Z`,c.paper);
 s+=rs(()=>poly(H.ribbon(H.wave(1210,700,1470,694,6,2,40),26)),c.yolk);
  s+=rs(()=>`M${H.P(1270,640)}L${H.P(1400,560)}`,c.paper)+rs(()=>`M${H.P(1300,650)}L${H.P(1440,590)}`,c.paper);
 const S=H.sachetGeo(1640,680);s+=`<g transform="translate(0 0)">`+rs(()=>poly(S.red),c.chili)+rs(()=>poly(S.yellow),c.yolk)+L.placeGlyph(G.riotCore,S.x0+68,S.y0+140,80)+`</g>`;
 s+=rs(()=>poly(S.tear.map(([x,y])=>[x+190,y+196])),c.chili);
 // phone glow (cyan halo on wall region) + mascot
 const sc=0.82,mx=300,my=800-896*sc;
 s+=rs(()=>ellipse(mx+805*sc,my+500*sc,150,150),c.cyan);
 s+=place(mx,my,sc,char('riot','three-quarter',{...ex('riot','excited')}));
 out['static/02-maximalist-foodie/02-riot-scene.svg']=s+'</svg>\n';}
// ================= BOARDS =================
function icons(k,x0,y0){const c=M[k].C,ink=M[k].ink;const cell=120,sc=4;let s='';
 const I=k==='cram'?[
  ['cup','M6 6H18L17 20H7Z M5 6H19'],['fork','M12 10V21 M8 3V8H16V3 M10.7 3V8 M13.3 3V8'],['timer','M12 6A7 7 0 1 1 11.99 6Z M12 13V9.5 M10 3H14 M12 3V6'],
  ['kettle','M6 9H16V20H6Z M16 11H19V16H16 M8 9V6H14V9'],['headphones','M5 15V11A7 7 0 0 1 19 11V15 M4 14H7V20H4Z M17 14H20V20H17Z'],['notes','M6 3H18V21H6Z M9 8H15 M9 12H15 M9 16H13']]:[
  ['flame','M12 3C15 7 18 10 18 14A6 6 0 0 1 6 14C6 11 8 9 9 7C10 9 11 10 12 10C12 8 12 5 12 3Z',c.tang],['chili','M4 14C8 19 16 17 19 9L21 10C19 19 9 22 4 16Z',c.chili],['phone','M7 3H17V21H7Z',c.blue],
  ['sticker','M12 3L14 8.5L20 8.5L15.5 12.5L17 18L12 15L7 18L8.5 12.5L4 8.5L10 8.5Z',c.yolk],['bottle','M9 3H15V6H9Z M7 6H17V21H7Z',c.chili],['camera','M3 8H8L9.5 6H14.5L16 8H21V20H3Z',c.pink]];
 I.forEach(([n,d,fill],i)=>{const x=x0+(i%3)*cell*1.15,y=y0+Math.floor(i/3)*(cell+56);
  s+=`<g transform="translate(${x} ${y}) scale(${sc})">`+(k==='cram'?`<path d="M0 0H24V24H0Z" fill="none" stroke="${c.s25}" stroke-width="0.25"/><path d="${d}" fill="none" stroke="${ink}" stroke-width="2" stroke-linecap="square" stroke-linejoin="miter"/>`:`<path d="${d}" fill="${ink}" transform="translate(2 2)"/><path d="${d}" fill="${fill}" stroke="${ink}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`)+'</g>';
  s+=txt(M[k].text,n,x+48,y+96+34,20,M[k].muted,0,'middle');});return s;}
function board(k){const m=M[k],c=m.C,W=2400,Hh=1600;let s=svgOpen(W,Hh,`${m.nn}-${k} visual-world board · palette+roles, type, shape, texture, icons, application · colours from persona tokens only`);
 if(k==='cram')s+=`<defs><pattern id="cram-halftone-25" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><circle cx="6" cy="6" r="3.4" fill="${c.ink}"/></pattern></defs>`;
 s+=`<rect width="${W}" height="${Hh}" fill="${m.bg}"/>`+head(k,'Visual world',W);
 const sec=(t,x,y)=>txt(m.textB,t,x,y,24,m.ink,m.lT);
 // palette
 s+=sec('PALETTE + ROLES',80,230);
 const pal=k==='cram'?[['ink',c.ink,'text · accent · line · focus'],['paper',c.paper,'bg'],['screen-75',c.s75,'text-muted'],['screen-50',c.s50,'steam · shadow'],['screen-25',c.s25,'sachet screen'],['screen-10',c.s10,'surface']]:
  [['ink',c.ink,'text · line · keyline'],['paper',c.paper,'bg'],['yolk',c.yolk,'surface'],['hot-pink',c.pink,'accent'],['volt-blue',c.blue,'focus'],['ultraviolet',c.uv,'text-muted'],['acid-green',c.green,'clash'],['tangerine',c.tang,'clash'],['chili',c.chili,'clash · sachet'],['cyan',c.cyan,'clash · glow']];
 const per=k==='cram'?6:5,sw=k==='cram'?216:262,sh=k==='cram'?200:110;
 pal.forEach(([n,hx,r],i)=>{const x=80+(i%per)*(sw+18),y=256+Math.floor(i/per)*(sh+116);s+=`<path d="${rect(x,y,sw,sh)}" fill="${hx}" stroke="${m.ink}" stroke-width="4"/>`+txt(m.textB,n,x,y+sh+32,22,m.ink)+txt(m.text,hx,x,y+sh+60,18,m.muted)+txt(m.text,r,x,y+sh+86,18,m.muted);});
 if(k==='riot'){s+=sec('CLASH PAIRS · may touch without keyline',80,742);[[c.pink,c.green],[c.blue,c.tang],[c.uv,c.yolk],[c.chili,c.cyan]].forEach(([a,b],i)=>{const x=80+i*340;s+=`<path d="${rect(x,764,150,80)}" fill="${a}"/><path d="${rect(x+150,764,150,80)}" fill="${b}"/>`;});}
 else{s+=sec('ONE INK · 1-BIT HALFTONE 65 LPI @ 45°',80,742);s+=`<path d="${rect(80,764,1380,80)}" fill="url(#cram-halftone-25)"/>`;}
 // type
 const ty=930;s+=sec('TYPE',80,ty);
 s+=txt(m.disp,k==='cram'?'HOSTEL HUNGRY':'MAXIMALIST',80,ty+120,112,m.ink,m.dT);
 s+=txt(m.text,k==='cram'?'Archivo Black 400 · display · uppercase · lh 0.95 · +0.02em':'Bungee 400 · display · uppercase · lh 1.0 · +0.01em',80,ty+164,20,m.muted);
 s+=txt(m.text,k==='cram'?'1 cup. 1 sachet. All of it. Timer 2:00.':'Half sachet, chili oil, crispy onions.',80,ty+230,36,m.ink);
 s+=txt(m.text,k==='cram'?'IBM Plex Mono 400 / 600 · text · lh 1.5 · scale 1.414':'Rubik 400 / 700 · text · lh 1.5 · scale 1.5',80,ty+266,20,m.muted);
 const steps=k==='cram'?[16,22.6,32,45.3,64,90.5]:[16,24,36,54,81];let ax=880;steps.forEach(z=>{s+=txt(m.disp,'Aa',ax,ty+266,z,m.ink);ax+=T.textW(F[m.disp],'Aa',z)+24;});
 // shape / texture / icons
 const ry=1260;s+=sec('SHAPE',80,ry)+sec('TEXTURE',560,ry)+sec('ICONS · 24 GRID · 2PX',1000,ry);
 if(k==='cram'){s+=H.cs(rect(96,ry+40,160,120),c.paper);const zz=[];for(let i=0;i<=16;i++)zz.push([300+i*10,ry+40+(i%2?8:0)]);s+=H.cs(poly([...zz,[460,ry+160],[300,ry+160]]),c.s25);
  for(let i=0;i<4;i++)s+=H.cl(pline([[96,ry+200+i*22],[460,ry+200+i*22]]));s+=txt(m.text,'0 radius · 16 stroke · square cap',96,ry+300,18,m.muted);
  s+=`<path d="${rect(576,ry+40,380,160)}" fill="url(#cram-halftone-25)"/>`+`<path d="${rect(640,ry+216,24,6)}" fill="${c.ink}"/><path d="${rect(700,ry+214,24,6)}" fill="${c.ink}"/>`+txt(m.text,'halftone 65 lpi · 45° · max 2 staples',576,ry+300,18,m.muted);}
 else{const rs=H.rs;const burst=(cx,cy,ro,ri,n)=>()=>{const p=[];for(let i=0;i<n*2;i++){const a=(-90+i*180/n)*Math.PI/180,r=i%2?ri:ro;p.push([cx+r*Math.cos(a),cy+r*Math.sin(a)]);}return poly(p);};
  s+=rs(burst(170,ry+110,80,56,10),c.yolk)+`<path d="M${f(300)} ${f(ry+110)}A70 70 0 0 1 ${f(440)} ${f(ry+110)}Z" fill="${c.pink}"/><path d="M${f(300)} ${f(ry+110)}A70 70 0 0 0 ${f(440)} ${f(ry+110)}Z" fill="${c.green}"/>`;
  s+=txt(m.text,'die-cut · 20 keyline · radius 0 / 12 / 999',96,ry+300,18,m.muted);
  s+=rs(()=>rect(580,ry+50,150,110),c.cyan)+`<g style="mix-blend-mode:multiply" opacity="0.9"><path d="${circle(820,ry+110,64)}" fill="${c.pink}"/><path d="${circle(880,ry+110,64)}" fill="${c.yolk}"/></g>`+`<path d="${pline([[600,ry+120],[600+40*Math.sin(0.61),ry+120-40*Math.cos(0.61)]])}" fill="none" stroke="${c.paper}" stroke-opacity="0.6" stroke-width="12" stroke-linecap="round"/>`;
  s+=txt(m.text,'keyline plate +6/+6 · riso multiply 0.9 · gloss',576,ry+300,18,m.muted);}
 s+=icons(k,1000,ry+30);
 // application
 const ax0=1560,ay0=200;
 if(k==='cram'){const x=ax0+40,y=ay0+20,w=680,h=1040;s+=sec('APPLICATION · RECIPE CARD',ax0+40,ay0);s+=H.cs(rect(x,y+30,w,h),c.paper);
  s+=`<path d="${rect(x,y+30,w,150)}" fill="${c.ink}"/>`+txt('archivo','CRAM CUP',x+40,y+130,64,c.paper,0.02)+txt('plex','THE 13:00 METHOD',x+40,y+164,20,c.s25,0.08);
  s+=place(x+w-320,y+170,0.3,char('cram','front',ex('cram','content')));
  [['1','Boil 280 ml water.'],['2','Noodles in. Whole sachet in.'],['3','Timer 2:00. Stir once at 1:00.'],['4','Eat. Back to the notes.']].forEach(([n,t],i)=>{const yy=y+520+i*90;s+=`<path d="${rect(x+40,yy-40,52,52)}" fill="${c.ink}"/>`+txt('plexb',n,x+66,yy-2,30,c.paper,0,'middle')+txt('plex',t,x+116,yy,28,c.ink);s+=`<path d="${rect(x+40,yy+28,w-80,2)}" fill="${c.s25}"/>`;});
  s+=`<path d="${rect(x,y+910,w,160)}" fill="url(#cram-halftone-25)"/>`+`<path d="${rect(x+40,y+950,330,72)}" fill="${c.paper}"/>`+txt('plexb','1 cup · 1 sachet',x+60,y+996,26,c.ink)+L.placeGlyph(G.cram,x+w-120,y+940,96);
  s+=txt('plex','recipe card · 680 × 1040 · one ink',ax0+40,ay0+1130,18,m.muted);}
 else{const x=ax0+20,y=ay0+50,w=720,h=900,rs=H.rs;s+=sec('APPLICATION · SOCIAL POST 4:5',ax0+20,ay0);
  s+=`<path d="${rect(x,y,w,h)}" fill="${c.uv}"/>`+`<path d="${rect(x,y,w,190)}" fill="${c.yolk}"/>`+txt('bungee','REMIX NO. 07',x+40,y+122,76,c.ink,0.01);
  s+=place(x+90,y+150,0.56,char('riot','three-quarter',ex('riot','happy')));
  s+=`<path d="${rect(x,y+h-200,w,200)}" fill="${c.ink}"/>`+txt('rubik','Half sachet + chili oil + fried egg.',x+40,y+h-130,30,c.paper)+txt('rubik','Two minutes to build and shoot.',x+40,y+h-84,30,c.yolk);
  s+=`<path d="${rect(x,y,w,h)}" fill="none" stroke="${c.ink}" stroke-width="8"/>`+txt('rubik','social post · 1080 × 1350 shown at 720 × 900',ax0+20,ay0+990,18,m.muted);}
 return s+'</svg>\n';}
out['static/01-hostel-hungry/01-cram-board.svg']=board('cram');
out['static/02-maximalist-foodie/02-riot-board.svg']=board('riot');
return out;
