/* Viral Studio front end: idea -> script -> voice -> style -> video. No framework, no build step. */
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode */ } },
};
const S = { meta: null, genre: null, tone: "", script: null, audio: null, theme: null, pid: null, viewTheme: null, poll: null };
const TONES = ["Emotional", "Dark", "Funny", "Wholesome", "Shocking", "Calm", "Inspiring"];
const TIPS = [
  "Tip: the first 3 seconds decide everything. Your hook is already on screen before the first word ends.",
  "Tip: post the Short first, then the clips over the next days. Each one is a new chance to go viral.",
  "Tip: reply to comments with a clip. The algorithm loves conversation.",
  "Tip: try the same video in two themes and post the one that feels more you.",
  "Tip: series win. End with 'part two' and your viewers come back.",
  "Fun fact: every sound effect here is synthesized from scratch, no downloads.",
];
const LEVELS = [[0, "Doodler"], [300, "Sketcher"], [800, "Animator"], [1600, "Director"], [3000, "Studio Legend"], [6000, "Viral Machine"]];

/* ---------------- gamification ---------------- */
function stats() { return store.get("vs_stats", { xp: 0, videos: 0, streak: 0, last: "", tried: [] }); }
function renderMe() {
  const st = stats(); let lvl = LEVELS[0], next = LEVELS[1];
  LEVELS.forEach((l, i) => { if (st.xp >= l[0]) { lvl = l; next = LEVELS[i + 1] || [l[0] + 3000, "∞"]; } });
  $("#level").textContent = lvl[1];
  $("#xpfill").style.width = Math.min(100, 100 * (st.xp - lvl[0]) / (next[0] - lvl[0])) + "%";
  $("#me").title = `${st.xp} XP · ${st.videos} videos · next: ${next[1]} at ${next[0]} XP`;
  $("#streak").textContent = "🔥 " + st.streak;
  renderCollect();
}
function award(xp, why, theme) {
  const st = stats(); const today = new Date().toISOString().slice(0, 10);
  const yest = new Date(Date.now() - 864e5).toISOString().slice(0, 10);
  if (st.last !== today) { st.streak = st.last === yest ? st.streak + 1 : 1; st.last = today; }
  const before = LEVELS.filter(l => st.xp >= l[0]).length;
  st.xp += xp; st.videos += why === "video" ? 1 : 0;
  let newTheme = false;
  if (theme && !st.tried.includes(theme)) { st.tried.push(theme); newTheme = true; }
  store.set("vs_stats", st);
  const after = LEVELS.filter(l => st.xp >= l[0]).length;
  renderMe();
  if (after > before) toast(`⭐ Level up! You're now a ${LEVELS[after - 1][1]}`);
  else if (newTheme) toast(`🎨 New theme collected (${st.tried.length}/${S.meta.themes.length}) · +${xp} XP`);
  else toast(`+${xp} XP`);
}
function renderCollect() {
  if (!S.meta) return;
  const tried = stats().tried;
  $("#collect").innerHTML = `Collected ${tried.length}/${S.meta.themes.length} ` +
    S.meta.themes.map(t => `<i class="${tried.includes(t.id) ? "got" : ""}" title="${t.name}"></i>`).join("");
}

/* ---------------- ui helpers ---------------- */
function toast(msg, ms = 2600) { const t = $("#toast"); t.textContent = msg; t.classList.add("show"); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove("show"), ms); }
function go(step) {
  $$(".step").forEach(s => s.hidden = s.id !== "step-" + step);
  $$("#stepnav button").forEach(b => b.classList.toggle("on", b.dataset.step === step));
  window.scrollTo({ top: 0, behavior: "smooth" });
  if (step === "style") startPreviews(); else stopPreviews();
}
async function api(path, opts = {}) {
  const r = await fetch(path, opts);
  if (!r.ok) { let m = r.statusText; try { m = (await r.json()).detail || m; } catch { } throw new Error(m); }
  return r.json();
}
const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const hl = s => esc(s).replace(/\*(.+?)\*/g, "<b>$1</b>").replace(/ \| /g, " · ");

/* ---------------- step 1: idea ---------------- */
function initIdea() {
  $("#genres").innerHTML = S.meta.genres.map(g => `<button class="chip" role="radio" data-g="${g.id}"><span class="e">${g.emoji}</span>${g.label}</button>`).join("");
  $$("#genres .chip").forEach(b => b.onclick = () => { S.genre = b.dataset.g; $$("#genres .chip").forEach(x => x.classList.toggle("on", x === b)); });
  $("#language").innerHTML = S.meta.languages.map(l => `<option>${l}</option>`).join("");
  $("#tones").innerHTML = TONES.map(t => `<button class="chip" data-t="${t}">${t}</button>`).join("");
  $$("#tones .chip").forEach(b => b.onclick = () => { S.tone = S.tone === b.dataset.t ? "" : b.dataset.t; $$("#tones .chip").forEach(x => x.classList.toggle("on", x.dataset.t === S.tone)); });
  const lab = () => { const s = +$("#seconds").value; $("#lenlabel").textContent = `${s} s · ~${Math.round(s * 2.5)} words`; };
  $("#seconds").oninput = lab; lab();
  $("#write").onclick = writeScript;
  $("#haveScript").onclick = () => { S.script = null; $("#spoken").value = ""; go("voice"); };
}
async function writeScript() {
  if (!S.genre) { toast("Pick a genre first 👆"); return; }
  const b = $("#write"); b.disabled = true; b.innerHTML = `<span class="spin">✨</span> Finding the viral angle…`;
  try {
    S.script = await api("/api/script", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ genre: S.genre, language: $("#language").value, seconds: +$("#seconds").value, topic: $("#topic").value, tone: S.tone }) });
    showScript(); go("script");
  } catch (e) { toast("😕 " + e.message, 4000); }
  b.disabled = false; b.innerHTML = "✨ Write my script";
}
function showScript() {
  const s = S.script;
  $("#srcbadge").textContent = s.source === "claude" ? "Written for you" : "Sample script (offline mode)";
  $("#stitle").textContent = s.title;
  $("#why").innerHTML = (s.why_it_travels || []).map(x => `<li>${esc(x)}</li>`).join("");
  $("#script").value = s.script; countWords();
  $("#caption").textContent = s.caption || "";
  $("#tags").textContent = (s.hashtags || []).join(" ");
  $("#scenesPrev").innerHTML = (s.scenes_preview || []).map(x => `<li>${hl(x)}</li>`).join("");
  $("#backup").innerHTML = s.backup_ideas?.length ? `<h3>Other ideas</h3><ul class="why">${s.backup_ideas.map(x => `<li>${esc(x)}</li>`).join("")}</ul>` : "";
}
function countWords() { const n = $("#script").value.trim().split(/\s+/).filter(Boolean).length; $("#wc").textContent = `${n} words · ~${Math.round(n / 2.5)} s`; }

/* ---------------- step 2 -> 3 ---------------- */
function initScript() {
  $("#script").oninput = countWords;
  $("#copy").onclick = async () => { try { await navigator.clipboard.writeText($("#script").value); toast("📋 Copied. Paste it into ElevenLabs."); } catch { $("#script").select(); toast("Select-all done. Press Ctrl/Cmd+C"); } };
  $("#again").onclick = writeScript;
  $("#toVoice").onclick = () => {
    $("#spoken").value = $("#script").value;
    if (S.script) { $("#title").value = S.script.title || ""; $("#label").value = (S.script.label || "").toUpperCase(); }
    go("voice");
  };
}
function initVoice() {
  const drop = $("#drop"), inp = $("#audio");
  drop.onclick = e => { if (e.target.tagName !== "AUDIO") inp.click(); };
  drop.onkeydown = e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); inp.click(); } };
  ["dragenter", "dragover"].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add("over"); }));
  ["dragleave", "drop"].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove("over"); }));
  drop.addEventListener("drop", e => e.dataTransfer.files[0] && setAudio(e.dataTransfer.files[0]));
  inp.onchange = () => inp.files[0] && setAudio(inp.files[0]);
  $("#spoken").oninput = canStyle;
  $("#toStyle").onclick = () => { if (!S.theme) pickTheme(S.meta.genre_theme[S.genre] || "rose-paper", false); go("style"); };
}
function setAudio(f) {
  if (f.size > 40 * 1024 * 1024) { toast("That file is over 40 MB 😬"); return; }
  S.audio = f; $("#dropText").textContent = "🎙️ " + f.name; $("#drop").classList.add("ok");
  const p = $("#player"); p.src = URL.createObjectURL(f); p.hidden = false; canStyle();
}
function canStyle() { $("#toStyle").disabled = !(S.audio && $("#spoken").value.trim().split(/\s+/).length >= 8); }

/* ---------------- step 4: themes with live previews ---------------- */
let previews = [], raf = null;
function initStyle() {
  const tried = stats().tried;
  $("#themes").innerHTML = S.meta.themes.map(t => `
    <button class="theme" role="radio" data-id="${t.id}" aria-label="${esc(t.name)}">
      <canvas width="270" height="390"></canvas>
      ${tried.includes(t.id) ? `<span class="tried">✓ tried</span>` : ""}
      <div class="meta"><div class="name">${esc(t.name)} <span class="rar ${t.rarity}">${t.rarity}</span></div>
      <div class="tag">${esc(t.tagline)}</div></div>
    </button>`).join("");
  previews = $$(".theme").map(el => {
    const t = S.meta.themes.find(x => x.id === el.dataset.id);
    el.onclick = () => pickTheme(t.id);
    el.onmouseenter = () => el._hot = true; el.onmouseleave = () => el._hot = false;
    return { el, t, cv: $("canvas", el), t0: Math.random() * 4 };
  });
  $("#surprise").onclick = surprise;
  $("#clips").oninput = () => $("#nclips").textContent = $("#clips").value;
  $("#make").onclick = make;
  renderCollect();
}
function pickTheme(id, say = true) {
  S.theme = id; $$(".theme").forEach(el => el.classList.toggle("on", el.dataset.id === id));
  if (say) { const t = S.meta.themes.find(x => x.id === id); toast(`${t.name}: ${t.tagline}`); }
}
function surprise() {
  const cards = $$(".theme"); let n = 0; const total = 14 + Math.floor(Math.random() * cards.length);
  cards.forEach(c => c.classList.add("rolling"));
  const step = () => {
    const c = cards[n % cards.length]; pickTheme(c.dataset.id, false); n++;
    if (n < total) setTimeout(step, 60 + n * 9);
    else { cards.forEach(c => c.classList.remove("rolling")); pickTheme(c.dataset.id); c.scrollIntoView({ block: "nearest", behavior: "smooth" }); }
  };
  step();
}
function startPreviews() {
  if (raf) return;
  const loop = ts => { previews.forEach(p => drawPreview(p, ts / 1000)); raf = requestAnimationFrame(loop); };
  raf = requestAnimationFrame(loop);
}
function stopPreviews() { cancelAnimationFrame(raf); raf = null; }
const ease = x => (x = Math.max(0, Math.min(1, x)), x * x * (3 - 2 * x));
const back = x => { x = Math.max(0, Math.min(1, x)); const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2; };
function capFont(st, size) {
  const f = st.cap_font || "";
  const w = /Black/.test(f) ? 900 : /ExtraBold/.test(f) ? 800 : /Bold|SemiBold/.test(f) ? 700 : 600;
  const fam = /Mono/.test(f) ? "ui-monospace, monospace" : /Serif/.test(f) ? "Georgia, serif" : "Inter, sans-serif";
  return `${w} ${size}px ${fam}`;
}
function drawPreview(p, now) {
  const { cv, t } = p, c = cv.getContext("2d"), W = cv.width, H = cv.height, st = t.style, col = t.css;
  const speed = p.el._hot || p.el.classList.contains("on") ? 1 : 0.5;
  p.clock = (p.clock || p.t0) + speed / 60; const T = p.clock % 4.2;
  c.save(); c.fillStyle = col.bg; c.fillRect(0, 0, W, H);
  // texture
  c.globalAlpha = 1;
  if (st.texture === "grid") { c.strokeStyle = col.ink + "14"; c.lineWidth = 1; for (let x = 0; x < W; x += 18) { c.beginPath(); c.moveTo(x, 0); c.lineTo(x, H); c.stroke(); } for (let y = 0; y < H; y += 18) { c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke(); } }
  if (st.texture === "halftone") { c.fillStyle = col.accent + "1c"; for (let y = 0; y < H; y += 10) for (let x = (y / 10 % 2) * 5; x < W; x += 10) { c.beginPath(); c.arc(x, y, 1 + 2 * x / W, 0, 7); c.fill(); } }
  if (st.texture === "stars") { c.fillStyle = col.ink; for (let k = 0; k < 40; k++) { c.globalAlpha = .2 + .3 * Math.abs(Math.sin(k * 7.1 + now)); c.beginPath(); c.arc((k * 97) % W, (k * 53) % H, 1.2, 0, 7); c.fill(); } c.globalAlpha = 1; }
  if (st.texture === "chalk") { c.fillStyle = col.ink + "10"; for (let k = 0; k < 160; k++) c.fillRect((k * 131) % W, (k * 71) % H, 2, 1); }
  // label
  c.fillStyle = col.grey; c.font = capFont({ cap_font: st.label_font || "Inter SemiBold" }, 10); c.textAlign = "center"; c.fillText("YOUR VIDEO", W / 2, 26);
  c.fillStyle = col.accent; c.fillRect(0, 0, W * T / 4.2, 3);
  // line style
  const wob = st.wobble || 1, sw = 2.4 * (st.stroke || 1);
  c.lineCap = "round"; c.lineJoin = "round"; c.lineWidth = sw;
  if (st.glow) { c.shadowBlur = 10 * st.glow; }
  const jit = (x, y, k) => [x + wob * 0.9 * Math.sin(k * 1.7 + y * 0.05), y + wob * 0.9 * Math.cos(k * 1.3 + x * 0.05)];
  const draw = (pts, prog, color) => {
    c.strokeStyle = color; c.shadowColor = color; c.beginPath();
    const n = Math.max(2, Math.floor(pts.length * Math.max(0, Math.min(1, prog))));
    pts.slice(0, n).forEach(([x, y], k) => { const [a, b] = jit(x, y, k); k ? c.lineTo(a, b) : c.moveTo(a, b); }); c.stroke();
  };
  const circ = (cx, cy, r, a0 = 0, a1 = 6.283) => Array.from({ length: 30 }, (_, k) => [cx + r * Math.cos(a0 + (a1 - a0) * k / 29), cy + r * Math.sin(a0 + (a1 - a0) * k / 29)]);
  const person = (x, y, s, fem, prog) => {
    draw(circ(x, y - 64 * s, 11 * s), prog * 3, col.ink);
    const L = [[x - 3 * s, y - 52 * s], [x - 3 * s, y - 40 * s], [x - 20 * s, y - 20 * s], [x - 22 * s, y]];
    draw(L, prog * 3 - 1, col.ink); draw(L.map(([a, b]) => [2 * x - a, b]), prog * 3 - 1, col.ink);
    if (fem) draw(circ(x, y - 66 * s, 16 * s, Math.PI * 0.95, Math.PI * 2.05), prog * 3 - 1.5, col.ink);
  };
  const mot = st.drift || 1, dx = 2 * mot * Math.sin(now * 0.9);
  c.save(); c.translate(dx, 0);
  person(80, 250, 1.25, true, T / 0.7); person(190, 250, 1.25, false, (T - 0.3) / 0.7);
  // heart pops on the beat word
  const hb = T - 1.1;
  if (hb > 0) {
    const s = back(hb / 0.45) * (1 + 0.08 * Math.max(0, Math.sin(hb * 6)) ** 8) * (1 + (st.punch || .035) * 2 * Math.sin(Math.min(1, hb / .35) * Math.PI));
    c.save(); c.translate(135, 150); c.scale(s, s); c.fillStyle = col.accent; c.shadowColor = col.accent;
    c.beginPath(); for (let k = 0; k <= 40; k++) { const a = k / 40 * 6.283; c.lineTo(1.25 * 16 * Math.sin(a) ** 3, -1.25 * (13 * Math.cos(a) - 5 * Math.cos(2 * a) - 2 * Math.cos(3 * a) - Math.cos(4 * a))); } c.fill(); c.restore();
  }
  // rings
  if (T > 1.5) { for (let k = 0; k < 2; k++) { const ph = ((T - 1.5) * 0.7 + k / 2) % 1; c.strokeStyle = col.accent; c.globalAlpha = .5 * (1 - ph); c.lineWidth = 2; c.beginPath(); c.arc(135, 150, 30 + 40 * ph, 0, 7); c.stroke(); } c.globalAlpha = 1; }
  c.restore(); c.shadowBlur = 0;
  // caption with pop on the highlight word
  const words = ["never", "ignore", "the", "signs"]; const times = [0.4, 0.8, 1.05, 1.15];
  const txt = words.map(w => st.cap_upper ? w.toUpperCase() : w);
  let fs = 21; c.font = capFont(st, fs); c.textAlign = "left";
  while (c.measureText(txt.join(" ")).width > W - 36 && fs > 12) c.font = capFont(st, --fs);
  const widths = txt.map(w => c.measureText(w + " ").width); let x = (W - widths.reduce((a, b) => a + b, 0)) / 2;
  if (st.plate) { c.fillStyle = col.ink + "14"; c.beginPath(); c.roundRect?.(x - 10, 300, widths.reduce((a, b) => a + b, 0) + 12, 38, 10); c.fill(); }
  txt.forEach((w, k) => {
    const pr = (T - times[k]) / 0.16; if (pr <= 0) { x += widths[k]; return; }
    const hot = k === 3; c.save(); c.globalAlpha = Math.min(1, pr);
    const sc = hot ? 1 + (st.cap_pop || .18) * (1 - Math.min(1, (T - times[k]) / 0.3)) : 1;
    c.translate(x + widths[k] / 2, 326); c.scale(sc, sc); c.fillStyle = hot ? col.accent : col.ink; c.fillText(w, -widths[k] / 2, 0); c.restore();
    if (hot) { c.strokeStyle = col.accent; c.lineWidth = 2.5; c.beginPath(); c.moveTo(x, 332); c.lineTo(x + (widths[k] - 8) * ease((T - times[k]) / 0.3), 333); c.stroke(); }
    x += widths[k];
  });
  c.restore();
}

/* ---------------- make + progress ---------------- */
async function make() {
  if (!S.theme) { toast("Pick a theme 🎨"); return; }
  const fShort = $("#fShort").checked, fLong = $("#fLong").checked, nClips = +$("#clips").value;
  if (!fShort && !fLong && !nClips) { toast("Choose at least one format"); return; }
  const fd = new FormData();
  fd.append("audio", S.audio); fd.append("script", $("#spoken").value); fd.append("genre", S.genre || "");
  fd.append("language", $("#language").value); fd.append("theme", S.theme);
  fd.append("formats", [fShort && "short", fLong && "long"].filter(Boolean).join(",")); fd.append("clips", nClips);
  fd.append("title", $("#title").value); fd.append("label", $("#label").value || $("#title").value);
  fd.append("youtube_title", S.script?.youtube_title || $("#title").value);
  const b = $("#make"); b.disabled = true; b.textContent = "Uploading…";
  try {
    const { id } = await api("/api/projects", { method: "POST", body: fd });
    S.pid = id; S.viewTheme = S.theme; location.hash = "p=" + id; store.set("vs_last", id);
    track(id);
  } catch (e) { toast("😕 " + e.message, 4500); }
  b.disabled = false; b.textContent = "🎬 Make my video";
}
const STAGE_NAMES = { queued: "Waiting for a free renderer", plan: "Splitting your script into scenes", timing: "Syncing every word to your voice",
  render_short: "Animating the vertical video", render_long: "Animating the YouTube version", clips: "Cutting the best moments", done: "Done" };
function track(id) {
  go("make"); $("#making").hidden = false; $("#results").hidden = true;
  let tipN = 0; $("#tip").textContent = TIPS[0];
  clearInterval(S.poll); clearInterval(S.tipT);
  S.tipT = setInterval(() => $("#tip").textContent = TIPS[++tipN % TIPS.length], 7000);
  S.poll = setInterval(async () => {
    let d; try { d = await api("/api/projects/" + id); } catch { return; }
    const st = d.status, pr = d.project;
    const order = ["queued", "plan", "timing", ...(pr.formats.includes("short") || pr.clips ? ["render_short"] : []), ...(pr.formats.includes("long") ? ["render_long"] : []), ...(pr.clips ? ["clips"] : [])];
    const idx = order.indexOf(st.stage);
    $("#stages").innerHTML = order.map((s, i) => `<li class="${st.stage === "done" || i < idx ? "done" : i === idx ? "now" : ""}">${STAGE_NAMES[s]}</li>`).join("");
    const frac = st.stage === "done" ? 1 : Math.max(0.02, (Math.max(0, idx) + (st.stage.startsWith("render") ? st.progress || 0 : 0.3)) / order.length);
    $("#pfill").style.width = (100 * frac).toFixed(1) + "%";
    $("#pmsg").textContent = st.message || "";
    if (st.stage === "error") { clearInterval(S.poll); clearInterval(S.tipT); $("#mkTitle").textContent = "Something went wrong 😕"; $("#pmsg").textContent = st.message; }
    if (st.stage === "done") {
      clearInterval(S.poll); clearInterval(S.tipT);
      const fresh = !store.get("vs_awarded", []).includes(id + pr.theme);
      if (fresh) { store.set("vs_awarded", [...store.get("vs_awarded", []), id + pr.theme]); award(Object.keys(d.renders).length > 1 ? 60 : 150, Object.keys(d.renders).length > 1 ? "theme" : "video", pr.theme); confetti(); }
      S.viewTheme = pr.theme; showResults(d);
    }
  }, 1500);
}
function showResults(d) {
  $("#making").hidden = true; $("#results").hidden = false;
  const themes = Object.keys(d.renders).filter(t => Object.keys(d.renders[t]).length);
  const tname = id => (S.meta.themes.find(t => t.id === id) || { name: id }).name;
  $("#themetabs").innerHTML = themes.length > 1 ? themes.map(t => `<button class="chip ${t === S.viewTheme ? "on" : ""}" data-t="${t}">${esc(tname(t))}</button>`).join("") : "";
  $$("#themetabs .chip").forEach(b => b.onclick = () => { S.viewTheme = b.dataset.t; showResults(d); });
  const o = d.renders[S.viewTheme] || {};
  $("#rnote").textContent = d.project.timing_method === "estimated"
    ? "Word timing was estimated from the pauses in your voice (this language has no word aligner yet), so captions may be a hair early or late."
    : "Every caption is synced to your voice, word by word.";
  $("#outShort").hidden = !o.short_mp4; $("#outLong").hidden = !o.long_mp4;
  if (o.short_mp4) $("#outShort").innerHTML = `<h3>📱 Short · 9:16</h3><video controls playsinline preload="metadata" poster="${o.cover_jpg || ""}" src="${o.short_mp4}"></video>
    <div class="dl"><a class="btn" href="${o.short_mp4}" download>⬇ MP4</a>${o.short_srt ? `<a class="btn ghost" href="${o.short_srt}" download>Captions .srt</a>` : ""}</div>`;
  if (o.long_mp4) $("#outLong").innerHTML = `<h3>🖥️ YouTube · 16:9</h3><video controls playsinline preload="metadata" poster="${o.thumbnail_jpg || ""}" src="${o.long_mp4}"></video>
    <div class="dl"><a class="btn" href="${o.long_mp4}" download>⬇ MP4</a>${o.long_srt ? `<a class="btn ghost" href="${o.long_srt}" download>Subtitles .srt</a>` : ""}${o.thumbnail_jpg ? `<a class="btn ghost" href="${o.thumbnail_jpg}" download>Thumbnail</a>` : ""}</div>`;
  const cl = o.clips || [];
  $("#clipsH").hidden = !cl.length;
  $("#outClips").innerHTML = cl.map((c, k) => `<div class="clip"><video controls playsinline preload="metadata" src="${c.url}#t=0.8"></video>
    <p>#${k + 1} · ${(c.end - c.start).toFixed(0)} s · “${esc(c.hook)}…”</p><a class="btn ghost" href="${c.url}" download>⬇ Clip ${k + 1}</a></div>`).join("");
  $("#hop").innerHTML = S.meta.themes.filter(t => !themes.includes(t.id)).map(t =>
    `<button class="btn ghost" data-t="${t.id}"><span class="sw" style="background:linear-gradient(135deg,${t.css.bg} 50%,${t.css.accent} 50%)"></span>${esc(t.name)}</button>`).join("");
  $$("#hop button").forEach(b => b.onclick = async () => {
    try { await api(`/api/projects/${S.pid}/rerender`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ theme: b.dataset.t }) });
      S.theme = b.dataset.t; track(S.pid); } catch (e) { toast("😕 " + e.message); }
  });
}

/* ---------------- confetti ---------------- */
function confetti() {
  const cv = $("#confetti"), c = cv.getContext("2d"); cv.width = innerWidth; cv.height = innerHeight;
  const cols = ["#ff3d7f", "#7c5cff", "#23c4ff", "#ffd166", "#2bd99f"];
  const P = Array.from({ length: 160 }, () => ({ x: innerWidth / 2, y: innerHeight / 3, vx: (Math.random() - .5) * 16, vy: -Math.random() * 14 - 4, r: Math.random() * 6 + 3, c: cols[Math.random() * 5 | 0], a: Math.random() * 6 }));
  let f = 0; (function tick() { c.clearRect(0, 0, cv.width, cv.height); P.forEach(p => { p.vy += .35; p.x += p.vx; p.y += p.vy; p.a += .2; c.save(); c.translate(p.x, p.y); c.rotate(p.a); c.fillStyle = p.c; c.fillRect(-p.r, -p.r / 2, p.r * 2, p.r); c.restore(); }); if (++f < 150) requestAnimationFrame(tick); else c.clearRect(0, 0, cv.width, cv.height); })();
}

/* ---------------- boot ---------------- */
(async function boot() {
  S.meta = await api("/api/meta");
  initIdea(); initScript(); initVoice(); initStyle(); renderMe();
  $$("#stepnav button").forEach(b => b.onclick = () => {
    const s = b.dataset.step;
    if (s === "script" && !S.script) return toast("Write a script first");
    if (s === "style" && !S.audio) return toast("Add your voice-over first");
    if (s === "make" && !S.pid) return toast("Make a video first");
    go(s);
  });
  $("#newVideo").onclick = () => { location.hash = ""; S.pid = null; S.audio = null; go("idea"); };
  const m = location.hash.match(/p=([a-z0-9]+)/);
  if (m) { S.pid = m[1]; track(m[1]); } else go("idea");
})();
