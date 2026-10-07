/* One day, seven noodles: whoever's hour it is wakes up, and the page becomes their world.
   Data comes from system.js (generated from tokens.json). One state: the minute of the day. */
(function () {
  "use strict";

  const S = window.SYSTEM;
  const P = S.personas; // sorted by start time
  const DAY = 1440;
  const $ = (id) => document.getElementById(id);
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const store = {
    get(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* storage unavailable */ } },
  };

  const toMin = (hhmm) => { const [h, m] = hhmm.split(":").map(Number); return h * 60 + m; };
  const fmt = (min) => `${String(Math.floor(min / 60)).padStart(2, "0")}:${String(min % 60).padStart(2, "0")}`;
  const starts = P.map((p) => toMin(p.time));

  function personaAt(min) {
    let idx = P.length - 1; // before the first start, the last persona's window wraps past midnight
    for (let i = 0; i < P.length; i++) if (min >= starts[i]) idx = i;
    return idx;
  }
  const nowMinutes = () => { const d = new Date(); return d.getHours() * 60 + d.getMinutes(); };

  const state = { minute: nowMinutes(), live: true, idx: -1 };

  /* ---------- URL: ?at=HH:MM or ?mascot=riot ---------- */
  (function readUrl() {
    const q = new URLSearchParams(window.location.search);
    const at = q.get("at"), mascot = q.get("mascot");
    if (at && /^\d{2}:\d{2}$/.test(at) && toMin(at) < DAY) { state.minute = toMin(at); state.live = false; }
    else if (mascot) {
      const i = P.findIndex((p) => p.id === mascot);
      if (i >= 0) { state.minute = starts[i]; state.live = false; }
    }
  })();

  function writeUrl() {
    const url = new URL(window.location.href);
    url.searchParams.delete("mascot");
    if (state.live) url.searchParams.delete("at"); else url.searchParams.set("at", fmt(state.minute));
    window.history.replaceState(null, "", url);
  }

  /* ---------- the noodle thread ---------- */
  const W = 1440, MID = 52;
  const xOf = (min) => (min / DAY) * W;
  const waveY = (x) => MID + 9 * Math.sin(x / 38) + 4 * Math.sin(x / 11);
  function pathBetween(x0, x1) {
    let d = `M${x0.toFixed(1)} ${waveY(x0).toFixed(1)}`;
    for (let x = x0 + 6; x < x1; x += 6) d += `L${x.toFixed(1)} ${waveY(x).toFixed(1)}`;
    return d + `L${x1.toFixed(1)} ${waveY(x1).toFixed(1)}`;
  }

  function drawThread() {
    $("thread-path").setAttribute("d", pathBetween(0, W));
    // knots and hour ticks are HTML, so they stay round and legible however the SVG stretches
    const t = $("thread");
    t.querySelectorAll(".thread-knot, .thread-tick").forEach((el) => el.remove());
    P.forEach((p, i) => {
      const k = document.createElement("span");
      k.className = "thread-knot";
      k.style.left = `${(starts[i] / DAY) * 100}%`;
      k.style.top = `${(waveY(xOf(starts[i])) / 120) * 100}%`;
      t.appendChild(k);
    });
    [0, 6, 12, 18, 24].forEach((h) => { // neutral hour ticks; names and times live on the cast chips
      const tick = document.createElement("span");
      tick.className = "thread-tick";
      tick.style.left = `${(h / 24) * 100}%`;
      tick.dataset.edge = h === 0 ? "start" : h === 24 ? "end" : "";
      tick.textContent = `${String(h).padStart(2, "0")}:00`;
      t.appendChild(tick);
    });
  }

  function windowRange(i) {
    const a = starts[i], b = i + 1 < P.length ? starts[i + 1] : starts[0] + DAY;
    return [a, b];
  }

  function drawActive() {
    const [a, b] = windowRange(state.idx);
    let d = pathBetween(xOf(a), xOf(Math.min(b, DAY)));
    if (b > DAY) d += " " + pathBetween(0, xOf(b - DAY)); // the window that wraps past midnight
    $("thread-active").setAttribute("d", d);
    const h = $("thread-handle");
    const x = (state.minute / DAY) * 100;
    h.style.left = `${x}%`;
    h.style.top = `${(waveY(xOf(state.minute)) / 120) * 100}%`;
    h.dataset.time = fmt(state.minute);
    h.setAttribute("aria-valuenow", state.minute);
    h.setAttribute("aria-valuetext", `${fmt(state.minute)}, ${P[state.idx].name}'s hour`);
  }

  /* ---------- cast (mascot switcher) ---------- */
  function buildCast() {
    const cast = $("cast");
    P.forEach((p, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "cast-chip";
      b.setAttribute("role", "radio");
      b.dataset.index = i;
      b.innerHTML = `<img src="${p.product.image}" alt="" width="40" height="56"><span><strong>${p.name}</strong><span>${p.time}</span></span>`;
      b.addEventListener("click", () => pin(starts[i]));
      b.addEventListener("keydown", (e) => {
        const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
        if (!step) return;
        e.preventDefault();
        const j = (i + step + P.length) % P.length;
        pin(starts[j]);
        cast.children[j].focus();
      });
      cast.appendChild(b);
    });
  }

  function syncCast() {
    [...$("cast").children].forEach((b, i) => {
      const on = i === state.idx;
      b.setAttribute("aria-checked", on ? "true" : "false");
      b.tabIndex = on ? 0 : -1;
    });
  }

  /* ---------- content ---------- */
  const text = (id, s) => { $(id).textContent = s; };

  function radar(p) {
    const keys = ["heat", "speed", "comfort", "chaos", "value", "fancy", "wellness"];
    const R = 120, n = keys.length;
    const pt = (i, v) => { const a = -Math.PI / 2 + (2 * Math.PI * i) / n; return [Math.cos(a) * R * v / 5, Math.sin(a) * R * v / 5]; };
    let s = '<title id="radar-title">' + `${p.name}'s card stats` + "</title>";
    for (let r = 1; r <= 5; r++) s += `<polygon class="radar-ring" points="${keys.map((_, i) => pt(i, r).join(",")).join(" ")}"/>`;
    keys.forEach((k, i) => {
      const [x, y] = pt(i, 5);
      s += `<line class="radar-axis" x1="0" y1="0" x2="${x}" y2="${y}"/>`;
      const [lx, ly] = pt(i, 6.1);
      const anchor = Math.abs(lx) < 8 ? "middle" : lx > 0 ? "start" : "end";
      s += `<text class="radar-label" x="${lx}" y="${ly + 4}" text-anchor="${anchor}">${k[0].toUpperCase() + k.slice(1)}</text>`;
    });
    s += `<polygon class="radar-shape" points="${keys.map((k, i) => pt(i, p.stats[k]).join(",")).join(" ")}"/>`;
    $("radar").innerHTML = s;
    $("stats").innerHTML = keys.map((k) => `<li><span>${k[0].toUpperCase() + k.slice(1)}</span><strong>${p.stats[k]}</strong></li>`).join("");
  }

  const NEED = { AA: { body: 4.5, large: 3, ui: 3 }, AAA: { body: 7, large: 4.5, ui: 3 } };
  function lum(hex) {
    const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
      .map((v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  }
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((m, n) => n - m); return (x + 0.05) / (y + 0.05); };
  const USE = { body: "body text", large: "large text", ui: "icons and outlines" };

  function looks(p) {
    text("constraint", `${p.constraint.rule}. ${p.constraint.why}.`);
    $("swatches").innerHTML = Object.entries(p.palette).map(([name, hex]) =>
      `<li><div class="swatch-chip" style="background:${hex}"></div><strong>${name}</strong><span>${hex}</span></li>`).join("");
    $("pairs").innerHTML = p.pairs.map((x) => {
      const r = ratio(x.fg, x.bg), need = NEED[p.level][x.use], ok = r >= need;
      return `<li><span class="pair-sample" style="color:${x.fg};background:${x.bg}">Aa</span>` +
        `<span>${x.fgName} on ${x.bgName}, for ${USE[x.use]} (${x.where})</span>` +
        `<span class="pair-result">${ok ? "✓" : "✕"} ${r.toFixed(2)}:1 ${ok ? "passes" : "fails"} ${p.level}</span></li>`;
    }).join("");
    text("specimen-display", p.name);
    text("specimen-text", p.job + ".");
    text("specimen-faces", `${p.type.display} for display, ${p.type.text} for text, scale ratio ${p.type.ratio}.`);
  }

  function moves(p) {
    text("tempo-line", `${p.name} moves ${p.motion.tempo}, on the shared 120 BPM clock: one bar is the felt two minutes, squeezed into two seconds.`);
    const accents = p.motion.accentBeats;
    $("bar").innerHTML = Array.from({ length: 8 }, (_, i) => {
      const beat = 1 + i / 2;
      return `<span class="bar-cell${i % 2 === 0 ? " beat" : ""}${accents.includes(beat) ? " accent" : ""}" data-i="${i}"></span>`;
    }).join("");
    const named = accents.map((b) => (Number.isInteger(b) ? `beat ${b}` : `the off-beat after ${Math.floor(b)}`));
    text("bar-note", `Filled cells are ${p.name}'s accents: ${named.join(" and ")}.`);
    const label = `Play ${p.name}'s note`;
    text("play-note", label); text("play-note-2", label);
  }

  function holds(p) {
    ["hero-pack", "pack-large"].forEach((id) => {
      const img = $(id);
      img.src = p.product.image;
      img.alt = `${p.name} holds a pack of ${p.product.name}`;
    });
    text("hero-pack-caption", p.product.name);
    text("pack-name", p.product.name);
    text("pack-format", p.product.format);
    text("pack-why", p.product.why);
  }

  function hero(p) {
    text("clock-time", fmt(state.minute));
    $("clock-time").setAttribute("datetime", fmt(state.minute));
    text("hero-name", p.name);
    text("hero-felt", p.feltTime + ".");
    text("hero-persona", `The ${p.persona}, here for ${p.motivation.charAt(0).toLowerCase() + p.motivation.slice(1)}.`);
    const sp = p.spine;
    $("spine").innerHTML = [["Buys it", sp.buyer], ["Eats it", sp.eater], ["Eats with", sp.socialUnit], ["Buys how", sp.rhythm], ["Has to pass", sp.gate]]
      .map(([k, val]) => `<dt>${k}</dt><dd>${val}</dd>`).join("");
    text("sachet-line", `With the sachet: ${p.sachet.charAt(0).toLowerCase() + p.sachet.slice(1)}.`);
  }

  /* ---------- render ---------- */
  function render(announce) {
    const idx = personaAt(state.minute);
    const changed = idx !== state.idx;
    const apply = () => {
      state.idx = idx;
      const p = P[idx];
      document.body.dataset.persona = p.id;
      hero(p);
      if (changed) { radar(p); looks(p); moves(p); holds(p); syncCast(); }
      drawActive();
      $("back-to-now").hidden = state.live;
    };
    if (changed && state.idx !== -1 && document.startViewTransition && !reduceMotion.matches) {
      document.startViewTransition(apply);
    } else {
      apply();
    }
    if (changed && announce) text("announcer", `${P[idx].name}'s hour. The page is now ${P[idx].name}'s world.`);
  }

  function pin(min) {
    state.minute = ((Math.round(min) % DAY) + DAY) % DAY;
    state.live = false;
    render(true);
    writeUrl();
  }

  /* ---------- dragging and keys on the thread ---------- */
  function minuteFromPointer(e) {
    const r = $("thread").getBoundingClientRect();
    const f = Math.min(1, Math.max(0, (e.clientX - r.left) / r.width));
    return Math.min(DAY - 1, Math.round((f * DAY) / 5) * 5);
  }
  function bindThread() {
    const t = $("thread");
    t.addEventListener("pointerdown", (e) => {
      t.setPointerCapture(e.pointerId);
      pin(minuteFromPointer(e));
      $("thread-handle").focus({ preventScroll: true });
    });
    t.addEventListener("pointermove", (e) => { if (t.hasPointerCapture(e.pointerId)) pin(minuteFromPointer(e)); });
    $("thread-handle").addEventListener("keydown", (e) => {
      const m = state.minute;
      const next = {
        ArrowRight: m + 15, ArrowUp: m + 15, ArrowLeft: m - 15, ArrowDown: m - 15,
        PageUp: starts[(state.idx + 1) % P.length], PageDown: starts[(state.idx - 1 + P.length) % P.length],
        Home: 0, End: DAY - 1,
      }[e.key];
      if (next === undefined) return;
      e.preventDefault();
      pin(e.shiftKey && e.key.startsWith("Arrow") ? m + (next - m) * 4 : next);
    });
  }

  /* ---------- sound (Web Audio, only on a press) ---------- */
  let audio = null;
  const VOICE = { cram: "square", riot: "sawtooth", nest: "triangle", sprig: "sine", lull: "sine", stack: "square", mise: "triangle" };
  function note(p, at, dur) {
    audio = audio || new (window.AudioContext || window.webkitAudioContext)();
    const o = audio.createOscillator(), g = audio.createGain();
    o.type = VOICE[p.id];
    o.frequency.value = p.sound.hz;
    const t0 = audio.currentTime + at, peak = VOICE[p.id] === "sine" || VOICE[p.id] === "triangle" ? 0.22 : 0.07;
    g.gain.setValueAtTime(0, t0);
    g.gain.linearRampToValueAtTime(peak, t0 + 0.02);
    g.gain.exponentialRampToValueAtTime(0.001, t0 + dur);
    o.connect(g).connect(audio.destination);
    o.start(t0); o.stop(t0 + dur + 0.05);
  }
  function playhead(beats) {
    if (reduceMotion.matches) return;
    const cells = [...$("bar").children];
    cells.forEach((c, i) => setTimeout(() => {
      cells.forEach((x) => x.classList.remove("now"));
      c.classList.add("now");
      if (i === cells.length - 1) setTimeout(() => c.classList.remove("now"), 250);
    }, i * (60000 / S.bpm) / 2));
  }
  function playNote() {
    const p = P[state.idx];
    note(p, 0, 2);
    playhead();
    text("sound-caption", `Playing ${p.name}'s note: ${p.sound.pitch}, ${p.sound.hz} Hz, for one bar (2 seconds).`);
  }
  function playChord() {
    const byPitch = [...P].sort((a, b) => a.sound.hz - b.sound.hz);
    byPitch.forEach((p, i) => note(p, i * 0.25, 4 - i * 0.25));
    text("sound-caption", `Playing all seven, lowest first: ${byPitch.map((p) => `${p.name} ${p.sound.pitch}`).join(", ")}. Together they make the noodle chord.`);
  }

  /* ---------- motion pause (WCAG 2.2.2) ---------- */
  function setPaused(paused) {
    document.body.classList.toggle("motion-paused", paused);
    $("motion-toggle").setAttribute("aria-pressed", paused ? "true" : "false");
    $("motion-toggle").textContent = paused ? "Play motion" : "Pause motion";
    store.set("motion-paused", paused ? "1" : "0");
  }

  /* ---------- start ---------- */
  drawThread();
  buildCast();
  bindThread();
  render(false);
  setPaused(store.get("motion-paused") === "1");
  $("motion-toggle").addEventListener("click", () => setPaused(!document.body.classList.contains("motion-paused")));
  $("back-to-now").addEventListener("click", () => { state.live = true; state.minute = nowMinutes(); render(true); writeUrl(); });
  $("play-note").addEventListener("click", playNote);
  $("play-note-2").addEventListener("click", playNote);
  $("play-chord").addEventListener("click", playChord);
  setInterval(() => { if (state.live) { state.minute = nowMinutes(); render(true); } }, 15000);
})();
