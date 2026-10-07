// Seven ways to eat one packet: the live page.
// Persona data comes from system.js (generated from tokens.json by tools/build-web.py).
(function () {
  "use strict";
  const S = window.SYSTEM;
  const P = S.personas.slice().sort((a, b) => a.order - b.order);
  const byId = Object.fromEntries(P.map((p) => [p.id, p]));
  const $ = (id) => document.getElementById(id);
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  const root = document.documentElement;

  const toMin = (t) => { const [h, m] = t.split(":").map(Number); return h * 60 + m; };
  const fmt = (m) => `${String(Math.floor(m / 60) % 24).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;
  const starts = P.map((p) => ({ id: p.id, start: toMin(p.time) })).sort((a, b) => a.start - b.start);
  // each persona owns the hours from its time until the next persona's time (wrapping past midnight)
  function whoAt(min) {
    let owner = starts[starts.length - 1].id;
    for (const s of starts) if (s.start <= min) owner = s.id;
    return owner;
  }
  function torn(seed, amp = 1.2) {
    const pts = [];
    const j = (k) => (((seed * 31 + k * 17) % 11) - 5) / 5 * amp;
    let k = 0;
    for (let x = 0; x <= 100; x += 4) pts.push(`${x}% ${amp + j(k++)}%`);
    for (let y = 4; y <= 100; y += 4) pts.push(`${100 - amp - j(k++)}% ${y}%`);
    for (let x = 96; x >= 0; x -= 4) pts.push(`${x}% ${100 - amp - j(k++)}%`);
    for (let y = 96; y > 0; y -= 4) pts.push(`${amp + j(k++)}% ${y}%`);
    return `polygon(${pts.join(",")})`;
  }
  document.querySelectorAll("[data-torn]").forEach((el) => { el.style.clipPath = torn(+el.dataset.torn, .9); });

  // ---------- hero line-up ----------
  const lineup = $("lineup");
  P.forEach((p, i) => {
    const li = document.createElement("li");
    li.innerHTML = `<button type="button" aria-label="Swap the page to ${p.name}'s world, ${p.persona}, ${p.time}">
      <img src="${p.mascotImage}" alt="" style="--delay:${i * 160}ms;--amp:${p.motion.amplitude}"></button>`;
    li.querySelector("button").addEventListener("click", (ev) => { choose(p.id, "lineup", ev); $("world").scrollIntoView({ behavior: reduced.matches ? "auto" : "smooth" }); });
    lineup.appendChild(li);
  });

  // ---------- tabs ----------
  const tabs = $("tabs");
  P.forEach((p) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "tab";
    b.id = `tab-${p.id}`;
    b.setAttribute("role", "tab");
    b.setAttribute("aria-controls", "world");
    b.innerHTML = `<img src="${p.mascotImage}" alt=""><span>${p.time} ${p.name}</span>`;
    b.addEventListener("click", (ev) => choose(p.id, "tab", ev));
    tabs.appendChild(b);
  });
  tabs.addEventListener("keydown", (e) => {
    const i = P.findIndex((p) => p.id === document.body.dataset.persona);
    const n = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
    if (n) { e.preventDefault(); const next = P[(i + n + P.length) % P.length]; choose(next.id, "tab"); $(`tab-${next.id}`).focus(); }
  });

  // ---------- day strip ----------
  const strip = $("day-strip");
  P.forEach((p, i) => {
    const li = document.createElement("li");
    const r = p.roles;
    li.innerHTML = `<button type="button" class="day-card" style="--c-bg:${r.bg};--c-text:${r.text};--c-accent:${["cram", "mise"].includes(p.id) ? r.text : r.accent};--r:${(i % 2 ? 1.6 : -1.6)}deg;--torn:${torn(i + 40, .8)}">
      <span class="dc-time">${p.time}</span><span class="dc-name">${p.name}</span><span class="dc-mot">${p.persona}. ${p.motivation}.</span>
      <img src="${p.mascotImage}" alt="${p.name}, the ${p.persona} mascot"></button>`;
    li.querySelector("button").addEventListener("click", (ev) => { choose(p.id, "strip", ev); $("world").scrollIntoView({ behavior: reduced.matches ? "auto" : "smooth" }); });
    strip.appendChild(li);
  });

  // ---------- dial ----------
  const dial = $("dial"), thumb = $("dial-thumb"), marks = $("dial-marks");
  starts.forEach((s) => {
    const pct = (s.start / 1440) * 100;
    marks.insertAdjacentHTML("beforeend", `<i style="left:${pct}%"></i><span style="left:${pct}%">${byId[s.id].name}</span>`);
  });
  let minute = 0, live = true;
  function setMinute(m, source) {
    minute = ((Math.round(m) % 1440) + 1440) % 1440;
    thumb.style.left = `${(minute / 1440) * 100}%`;
    $("dial-time").textContent = fmt(minute);
    const id = whoAt(minute);
    dial.setAttribute("aria-valuenow", String(minute));
    dial.setAttribute("aria-valuetext", `${fmt(minute)}, ${byId[id].name}'s hour`);
    if (id !== document.body.dataset.persona || source === "init") render(id, source);
  }
  function stopLive() { live = false; $("live-toggle").setAttribute("aria-pressed", "false"); }
  function fromPointer(e) {
    const r = dial.getBoundingClientRect();
    return Math.max(0, Math.min(1439, ((e.clientX - r.left) / r.width) * 1440));
  }
  dial.addEventListener("pointerdown", (e) => {
    stopLive(); dial.setPointerCapture(e.pointerId); setMinute(fromPointer(e), "dial");
    const move = (ev) => setMinute(fromPointer(ev), "dial");
    const up = () => { dial.removeEventListener("pointermove", move); dial.removeEventListener("pointerup", up); };
    dial.addEventListener("pointermove", move); dial.addEventListener("pointerup", up);
  });
  dial.addEventListener("keydown", (e) => {
    const step = { ArrowRight: 15, ArrowUp: 15, ArrowLeft: -15, ArrowDown: -15, PageUp: 60, PageDown: -60 }[e.key];
    if (step !== undefined) { e.preventDefault(); stopLive(); setMinute(minute + step, "dial"); }
    if (e.key === "Home") { e.preventDefault(); stopLive(); setMinute(0, "dial"); }
    if (e.key === "End") { e.preventDefault(); stopLive(); setMinute(1439, "dial"); }
  });
  $("live-toggle").addEventListener("click", () => {
    live = !live;
    $("live-toggle").setAttribute("aria-pressed", String(live));
    if (live) tickClock(true);
  });

  // ---------- choose and render a world ----------
  const animating = () => !reduced.matches && !root.classList.contains("motion-paused");
  // a circle of the new world's colour grows from where you clicked, then the page swaps under it
  function choose(id, source, ev) {
    stopLive();
    const go = () => { setMinute(toMin(byId[id].time), source); render(id, source); };
    if (!ev || !animating() || id === document.body.dataset.persona) return go();
    const w = $("wipe");
    w.style.background = byId[id].roles.bg;
    w.style.setProperty("--wx", `${ev.clientX || innerWidth / 2}px`);
    w.style.setProperty("--wy", `${ev.clientY || innerHeight / 2}px`);
    w.classList.remove("go"); void w.offsetWidth; w.classList.add("go");
    setTimeout(go, 300);
    w.addEventListener("animationend", () => w.classList.remove("go"), { once: true });
  }

  // ---------- ticker: the seven sachet habits ----------
  const tickerHtml = P.map((p) => `<span>${p.name} <i>${p.sachet.toLowerCase()}</i></span>`).join("");
  $("ticker").innerHTML = tickerHtml + tickerHtml;

  // ---------- sticker pack: slap stickers onto the world ----------
  const slaps = $("slaps");
  function renderTray(p) {
    $("tray").innerHTML = p.stickers.map((src, i) =>
      `<button type="button" data-src="${src}" aria-label="Slap ${p.name} sticker ${i + 1} on the world"><img src="${src}" alt=""></button>`).join("");
  }
  $("tray").addEventListener("click", (ev) => {
    const b = ev.target.closest("button"); if (!b) return;
    const img = document.createElement("img");
    const rot = Math.round(Math.random() * 40 - 20);
    img.src = b.dataset.src; img.alt = "";
    img.style.left = `${8 + Math.random() * 78}%`; img.style.top = `${6 + Math.random() * 62}%`;
    img.style.setProperty("--rot", `${rot}deg`); img.style.transform = `rotate(${rot}deg)`;
    slaps.appendChild(img);
    while (slaps.children.length > 14) slaps.firstChild.remove();
    $("announce").textContent = "Sticker added.";
  });
  $("tray-clear").addEventListener("click", () => { slaps.innerHTML = ""; $("announce").textContent = "All stickers peeled off."; });

  // ---------- the deck: seven flip cards ----------
  const deck = $("deck");
  P.forEach((p, i) => {
    const li = document.createElement("li");
    li.style.setProperty("--fan", `${(i - 3) * 5}deg`);
    li.style.setProperty("--lift", `${Math.abs(i - 3) * 14}px`);
    li.innerHTML = `<button type="button" class="flip" aria-pressed="false" aria-label="${p.name} card: flip to see stats">
      <img class="front" src="${p.cardFront}" alt="${p.name} collectible card, ${p.persona}, ${p.time}">
      <img class="back" src="${p.cardBack}" alt="${p.name} card back: stats ${Object.entries(p.stats).map(([k, x]) => `${k} ${x}`).join(", ")}"></button>`;
    const b = li.querySelector("button");
    b.addEventListener("click", () => b.setAttribute("aria-pressed", String(b.getAttribute("aria-pressed") !== "true")));
    deck.appendChild(li);
  });
  function render(id, source) {
    const p = byId[id];
    const changed = document.body.dataset.persona !== id;
    document.body.dataset.persona = id;
    document.querySelectorAll(".tab").forEach((t) => t.setAttribute("aria-selected", String(t.id === `tab-${id}`)));
    document.querySelectorAll(".tab").forEach((t) => t.setAttribute("tabindex", t.id === `tab-${id}` ? "0" : "-1"));
    $("w-bigname").textContent = p.name;
    $("w-time").textContent = p.time;
    $("w-light").textContent = p.light;
    $("w-name").textContent = p.name;
    $("w-persona").textContent = p.persona;
    $("w-mot").textContent = `Wants: ${p.motivation.toLowerCase()}`;
    $("w-gate").textContent = `The gate: ${p.spine.gate}`;
    $("w-sachet").textContent = p.sachet;
    $("w-felt").textContent = p.feltTime;
    const product = p.product.name.replace("MAGGI ", "").split(" (")[0].split(",")[0];
    $("w-scene-cap").textContent = `${p.time}, ${product}`;
    const img = $("w-mascot");
    img.src = p.mascotImage;
    img.alt = `${p.name}, the ${p.persona} mascot, holding ${p.product.name}`;
    if (changed && !reduced.matches && !root.classList.contains("motion-paused")) {
      img.classList.remove("swap-in"); void img.offsetWidth; img.classList.add("swap-in");
    }
    $("w-scene").src = p.sceneImage;
    $("w-scene").alt = `${p.name} eating ${p.product.name} at ${p.time}`;
    $("w-pack").src = p.product.image;
    $("w-pack").alt = `${p.product.name} pack`;
    const roles = p.roles;
    const cols = [roles.bg, roles.surface, roles.text, roles.accent, roles.key, roles["sachet-red"], roles["sachet-yellow"]]
      .filter((c, i, a) => a.findIndex((x) => x.toUpperCase() === c.toUpperCase()) === i).slice(0, 6);
    $("w-spines").innerHTML = cols.map((c, i) => `<i style="background:${c};height:${60 + ((i * 37) % 5) * 10}%" title="${c}"></i>`).join("");
    if (changed || source === "init") { renderTray(p); if (changed && source !== "init") slaps.innerHTML = ""; }
    if (changed && source !== "init") $("announce").textContent = `Now showing ${p.name}'s world: ${p.persona}, ${p.time}.`;
    if (soundOn && changed && source !== "init") playNote(p);
  }

  // ---------- clock ----------
  function tickClock(force) {
    const d = new Date();
    const m = d.getHours() * 60 + d.getMinutes();
    $("now-time").textContent = fmt(m);
    $("now-who").textContent = `it's ${byId[whoAt(m)].name}'s hour`;
    if (live || force) setMinute(m, force === "init" ? "init" : "clock");
  }
  tickClock("init");
  setInterval(() => tickClock(false), 30000);

  // ---------- parallax ----------
  document.querySelectorAll(".layer").forEach((el) => el.style.setProperty("--d", el.dataset.depth || "0"));
  let raf = 0;
  window.addEventListener("pointermove", (e) => {
    if (reduced.matches || root.classList.contains("motion-paused")) return;
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(() => {
      root.style.setProperty("--px", ((e.clientX / innerWidth) - .5).toFixed(3));
      root.style.setProperty("--py", ((e.clientY / innerHeight) - .5).toFixed(3));
    });
  });
  const beat = parseInt(getComputedStyle(document.body).getPropertyValue("--beat")) || 500;
  root.style.setProperty("--beat-ms", `${beat}ms`);

  // ---------- motion pause (WCAG 2.2.2) ----------
  const mt = $("motion-toggle");
  function setPaused(on) {
    root.classList.toggle("motion-paused", on);
    mt.setAttribute("aria-pressed", String(on));
    mt.textContent = on ? "Play motion" : "Pause motion";
    if (on) { root.style.setProperty("--px", 0); root.style.setProperty("--py", 0); }
    try { localStorage.setItem("motion-paused", on ? "1" : "0"); } catch (e) { /* storage unavailable */ }
  }
  mt.addEventListener("click", () => setPaused(!root.classList.contains("motion-paused")));
  try { if (localStorage.getItem("motion-paused") === "1") setPaused(true); } catch (e) { /* storage unavailable */ }

  // ---------- sound: each persona's note from the shared chord, off by default ----------
  let soundOn = false, ctx = null;
  const st = $("sound-toggle");
  st.addEventListener("click", () => {
    soundOn = !soundOn;
    st.setAttribute("aria-pressed", String(soundOn));
    st.textContent = soundOn ? "Sound on" : "Play its note";
    if (soundOn) playNote(byId[document.body.dataset.persona]);
    else $("sound-caption").textContent = "";
  });
  function playNote(p) {
    try {
      ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
      const t = ctx.currentTime, o = ctx.createOscillator(), g = ctx.createGain();
      o.type = "sine"; o.frequency.value = p.sound.hz;
      g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(.18, t + .06); g.gain.exponentialRampToValueAtTime(.0001, t + 2);
      o.connect(g).connect(ctx.destination); o.start(t); o.stop(t + 2.05);
    } catch (e) { /* audio unavailable: caption still shows */ }
    $("sound-caption").textContent = `${p.name} plays ${p.sound.pitch}: ${p.sound.palette.join(", ")}.`;
  }
})();
