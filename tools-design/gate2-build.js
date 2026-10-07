// Gate 2 build: run via run_script -> new Function(src)() with helpers in scope (readFile, readFileBinary, saveFile).
const L=new Function(await readFile('tools-design/gate2-lib.js'))();const T=new Function(await readFile('tools-design/ttf-outline.js'))();
const F={};for(const [k,p] of Object.entries({archivo:'ArchivoBlack-Regular.ttf',plex:'IBMPlexMono-Regular.ttf',plexb:'IBMPlexMono-SemiBold.ttf',bungee:'Bungee-Regular.ttf',rubik:'Rubik-wght-.ttf'}))F[k]=T.parseTTF(await (await readFileBinary('tools-design/fonts/'+p)).arrayBuffer());
const gl=p=>readFile(p).then(L.glyphLayers);const G={cram:await gl('glyphs/01-hostel-hungry/01-cram-two.svg'),riot:await gl('glyphs/02-maximalist-foodie/02-riot-two.svg')};G.riotCore=G.riot.slice(-1);
const out=new Function('L','T','F','G',await readFile('tools-design/gate2-sheets.js'))(L,T,F,G);
for(const [m,fn,slug,nn] of [['cram',L.cram,'01-hostel-hungry','01'],['riot',L.riot,'02-maximalist-foodie','02']])for(const v of ['front','three-quarter','side'])out[`static/${slug}/${nn}-${m}-rig-${v}.svg`]=L.rigSvg(fn(v,{},G),`${nn}-${m} rig, ${v} view | rig-spec v0.1.1 | slots in spec order, anchors in ${m}__rig | colours: system/tokens/personas/${nn}-${m}.tokens.json`);
return out;
