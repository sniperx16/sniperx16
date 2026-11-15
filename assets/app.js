document.documentElement.classList.add("js");
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const img = n => `assets/img/${n}.jpg`;
const ARROW = '<svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M2 7h10M8 3l4 4-4 4"/></svg>';
const CHECK = '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M4 10l4 4 8-9"/></svg>';
const pad = n => String(n).padStart(2, "0");

/* ---- içerik üretimi ---- */
$("#panels").innerHTML = SVC.map((s, i) => `<article class="panel${i ? "" : " on"}" tabindex="0">
  <img src="${img(i ? s.img : "palplans-perde")}" alt="${s.t}" loading="lazy"><span class="n">${pad(i + 1)}</span><span class="v">${s.t}</span>
  <div class="c"><h3>${s.t}</h3><p>${s.s}</p><a class="more" href="#faaliyet-alanlari" data-target="${s.id}">Detay ${ARROW}</a></div></article>`).join("");
$("#rows").innerHTML = SVC.map((s, i) => `<article class="row" id="${s.id}">
  <figure class="rv"><img src="${img(s.img)}" alt="${s.t}" loading="lazy"><span class="no">${pad(i + 1)}</span></figure>
  <div class="rv" style="--d:1"><div class="kicker">Faaliyet alanı</div><h2>${s.t}</h2><p>${s.d}</p><ul>${s.l.map(x => `<li>${CHECK}<span>${x}</span></li>`).join("")}</ul><a href="#iletisim" class="btn">Teklif al</a></div></article>`).join("");
$("#drop").innerHTML = SVC.map(s => `<a href="#faaliyet-alanlari" data-target="${s.id}">${s.t}</a>`).join("");
$("#footSvc").innerHTML = SVC.slice(0, 6).map(s => `<li><a href="#faaliyet-alanlari" data-target="${s.id}">${s.t}</a></li>`).join("");
$("#f-hizmet").innerHTML = SVC.map(s => `<option>${s.t}</option>`).join("") + "<option>Diğer</option>";
$("#faq").innerHTML = FAQ.map(([q, a], i) => `<details${i ? "" : " open"}><summary>${q}</summary><p>${a}</p></details>`).join("");
const gItem = ([f, t, c], i) => `<button class="g" data-i="${i}" data-c="${c}"><img src="${img(f)}" alt="${t}" loading="lazy"><span><small>${CATS[c]}</small>${t}</span></button>`;
$("#gal").innerHTML = GAL.map(gItem).join("");
$("#track").innerHTML = GAL.slice(0, 9).map(gItem).join("");
$("#filters").innerHTML = Object.entries(CATS).map(([k, v]) => `<button data-c="${k}" aria-pressed="${k === "all"}">${v}</button>`).join("");
const tk = ["Palplanş iksa", "İsale hatları", "Kanalizasyon", "Arıtma tesisleri", "Kanal görüntüleme", "Terfi istasyonları"];
$("#ticker").innerHTML = [...tk, ...tk].map(t => `<span>${t}</span>`).join("");
const st = $("#statement"); st.innerHTML = st.textContent.trim().split(/\s+/).map(w => `<span class="w">${w}</span>`).join(" ");

/* ---- rakamlar (yalnızca doğrulanabilir) ---- */
$("#stats").innerHTML = STATS.map(([n, ek, t], i) => `<div class="rv" style="--d:${i}"><b><span data-count="${n}">${n}</span>${ek ? `<i>${ek}</i>` : ""}</b><span>${t}</span></div>`).join("");

/* ---- firma bilgileri ---- */
$$("[data-f]").forEach(e => e.textContent = FIRMA[e.dataset.f]);
$$("[data-tel]").forEach(e => e.href = "tel:+" + FIRMA.phoneRaw);
$$("[data-mail]").forEach(e => e.href = "mailto:" + FIRMA.email);
$$("[data-wa]").forEach(e => e.href = "https://wa.me/" + FIRMA.phoneRaw);
$("#yr").textContent = new Date().getFullYear();
if (FIRMA.mapQuery) {
  $("#map").innerHTML = `<div class="map-ph"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 21s7-6.2 7-12a7 7 0 10-14 0c0 5.800 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/></svg><b>${FIRMA.address}</b><span>Haritayı yüklediğinizde Google'ın çerezleri ve sunucuları devreye girer. <a href="#cerez" style="text-decoration:underline">Çerez Politikası</a></span><button class="btn dark" id="mapBtn" type="button">Haritayı yükle</button></div>`;
  $("#mapBtn").onclick = () => { $("#map").innerHTML = `<iframe title="Konum haritası" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://www.google.com/maps?q=${encodeURIComponent(FIRMA.mapQuery)}&output=embed"></iframe>`; };
}
/* ---- şirket bilgileri (alt bilgi) ---- */
$("#coInfo").innerHTML = [["Unvan", FIRMA.unvan], ["Vergi dairesi", FIRMA.vergiDairesi], ["Vergi no", FIRMA.vergiNo], ["MERSİS no", FIRMA.mersisNo], ["Ticaret sicil no", FIRMA.ticaretSicilNo]].filter(x => x[1]).map(([k, v]) => `<span><b>${k}:</b> ${v}</span>`).join("");
if (FIRMA.mapLink) $("#map").insertAdjacentHTML("afterend", `<a class="link" style="margin-top:26px" href="${FIRMA.mapLink}" target="_blank" rel="noopener">Yol tarifi al <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>`);
const ld = document.createElement("script"); ld.type = "application/ld+json";
ld.textContent = JSON.stringify({ "@context": "https://schema.org", "@type": "GeneralContractor", name: "Han Grup Yazılım İnşaat", telephone: "+" + FIRMA.phoneRaw, email: FIRMA.email, address: FIRMA.address, areaServed: "TR", knowsAbout: SVC.map(s => s.t) });
document.head.appendChild(ld);

/* ---- açılış slaytı ---- */
const hero = $("#hero"), heroTabs = $("#heroTabs");
hero.insertAdjacentHTML("afterbegin", SLIDES.map(([f, lab, h, p, id], i) => `<div class="slide${i ? "" : " on"}"><img src="${img(f)}" alt="" ${i ? 'loading="lazy"' : 'fetchpriority="high"'}>
  <div class="cap"><div class="wrap"><span class="lab">${lab}</span><h1>${h}</h1><p>${p}</p>
  <div class="acts"><a class="btn" href="#faaliyet-alanlari" data-target="${id}">Detaylı bilgi ${ARROW}</a><a class="btn line" href="#iletisim">Teklif al</a></div></div></div></div>`).join(""));
heroTabs.innerHTML = SLIDES.map((s, i) => `<button aria-label="${s[1]}"><small>${pad(i + 1)}</small><span>${s[1]}</span></button>`).join("");
const slides = $$(".slide", hero), hTabs = $$("button", heroTabs); let cur = 0, timer;
const go = i => { slides[cur].classList.remove("on"); hTabs[cur].classList.remove("on"); cur = (i + slides.length) % slides.length;
  slides[cur].classList.add("on"); void hTabs[cur].offsetWidth; hTabs[cur].classList.add("on"); clearTimeout(timer); timer = setTimeout(() => go(cur + 1), 6500); };
hTabs.forEach((b, i) => b.onclick = () => go(i)); go(0);

/* ---- faaliyet panelleri ---- */
const panels = $$(".panel");
const openPanel = p => panels.forEach(x => x.classList.toggle("on", x === p));
panels.forEach(p => { p.addEventListener("mouseenter", () => matchMedia("(hover:hover)").matches && openPanel(p)); p.addEventListener("click", () => openPanel(p)); p.addEventListener("focus", () => openPanel(p)); });

/* ---- sekmeler ---- */
const tabs = $$("#stTabs button"), panes = $$(".split .pane"), phs = $$("#stPh img");
tabs.forEach((b, i) => b.onclick = () => { tabs.forEach((x, j) => x.setAttribute("aria-selected", i === j)); panes.forEach((x, j) => x.classList.toggle("on", i === j)); phs.forEach((x, j) => x.classList.toggle("on", i === j)); });

/* ---- galeri şeridi ---- */
const track = $("#track"), stepW = () => (track.firstElementChild?.offsetWidth || 600) + 24;
$("#rPrev").onclick = () => track.scrollBy({ left: -stepW(), behavior: "smooth" });
$("#rNext").onclick = () => track.scrollBy({ left: stepW(), behavior: "smooth" });

/* ---- sayfa geçişleri ---- */
const VIEWS = ["anasayfa", "kurumsal", "faaliyet-alanlari", "galeri", "iletisim", "yasal"];
const LEGAL = ["kvkk", "gizlilik", "cerez", "kullanim"];
let pendingTarget = null, first = true;
const hdr = $("#hdr"), menu = $("#menu"), burger = $("#burger"), curtain = $("#curtain");
const setMenu = o => { menu.classList.toggle("open", o); hdr.classList.toggle("open", o); burger.setAttribute("aria-expanded", o); document.body.style.overflow = o ? "hidden" : ""; };
burger.onclick = () => setMenu(!menu.classList.contains("open"));
function swap(name) {
  $$(".view").forEach(v => v.classList.toggle("on", v.id === "v-" + name));
  $$("[data-nav]").forEach(a => a.classList.toggle("active", a.dataset.nav === name));
  const t = pendingTarget && document.getElementById(pendingTarget); pendingTarget = null;
  document.documentElement.style.scrollBehavior = "auto";
  if (t) t.scrollIntoView({ block: "start" }); else scrollTo(0, 0);
  document.documentElement.style.scrollBehavior = "";
  observe(); onScroll();
}
function route() {
  const hash = location.hash.slice(1);
  if (LEGAL.includes(hash)) pendingTarget = hash;
  const name = LEGAL.includes(hash) ? "yasal" : VIEWS.includes(hash) ? hash : "anasayfa";
  setMenu(false);
  const same = $("#v-" + name).classList.contains("on");
  if (first || same || matchMedia("(prefers-reduced-motion:reduce)").matches) { first = false; return swap(name); }
  curtain.classList.remove("go"); void curtain.offsetWidth; curtain.classList.add("go");
  setTimeout(() => swap(name), 470);
}
document.addEventListener("click", e => {
  const a = e.target.closest("a[href^='#']"); if (!a) return;
  pendingTarget = a.dataset.target || null;
  const h = a.getAttribute("href");
  if (h === location.hash || (h === "#anasayfa" && !location.hash)) { e.preventDefault(); route(); }
});
addEventListener("hashchange", route);

/* ---- belirme, sayaç ---- */
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { threshold: .12 });
function observe() { $$(".view.on .rv:not(.in), .view.on .spot-pic:not(.in), .cta .rv:not(.in)").forEach(e => io.observe(e)); }
const fmt = n => n.toLocaleString("tr-TR");
const cio = new IntersectionObserver(es => es.forEach(e => { if (!e.isIntersecting) return; cio.disconnect();
  $$("[data-count]", e.target).forEach(el => { const end = +el.dataset.count, t0 = performance.now();
    const tick = t => { const p = Math.min((t - t0) / 1800, 1); el.textContent = fmt(Math.round(end * (1 - Math.pow(1 - p, 4)))); if (p < 1) requestAnimationFrame(tick); }; requestAnimationFrame(tick); }); }), { threshold: .3 });
cio.observe($("#stats"));

/* ---- kaydırmaya bağlı efektler ---- */
const toTop = $("#toTop"), words = $$(".w", st), pars = $$("[data-par]"); let lastY = 0, ticking = false;
function onScroll() {
  const y = scrollY, vh = innerHeight;
  hdr.classList.toggle("solid", y > 80);
  hdr.classList.toggle("hide", y > 500 && y > lastY && !menu.classList.contains("open"));
  toTop.classList.toggle("show", y > 800); lastY = y;
  if (st.offsetParent) { const r = st.getBoundingClientRect(), p = Math.min(1, Math.max(0, (vh * .85 - r.top) / (r.height + vh * .35)));
    const n = Math.round(p * words.length); words.forEach((w, i) => w.classList.toggle("lit", i < n)); }
  pars.forEach(el => { if (!el.offsetParent) return; const r = el.parentElement.getBoundingClientRect(); if (r.bottom < 0 || r.top > vh) return;
    const off = (r.top + r.height / 2 - vh / 2) * +el.dataset.par; el.style.transform = `translateY(${off.toFixed(1)}px) scale(1.15)`; });
  ticking = false;
}
addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
addEventListener("resize", onScroll);
toTop.onclick = () => scrollTo({ top: 0, behavior: "smooth" });

/* ---- galeri ---- */
$("#filters").addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return;
  $$("#filters button").forEach(x => x.setAttribute("aria-pressed", x === b));
  $$("#gal .g").forEach(g => g.classList.toggle("hide", b.dataset.c !== "all" && g.dataset.c !== b.dataset.c)); });
const lb = $("#lb"); let li = 0;
const show = i => { li = (i + GAL.length) % GAL.length; $("img", lb).src = img(GAL[li][0]); $("p", lb).textContent = GAL[li][1]; lb.classList.add("open"); };
document.addEventListener("click", e => { const g = e.target.closest(".g"); if (g) show(+g.dataset.i); });
lb.addEventListener("click", e => { if (e.target.tagName === "IMG") show(li + 1); else lb.classList.remove("open"); });
addEventListener("keydown", e => { if (!lb.classList.contains("open")) return; if (e.key === "Escape") lb.classList.remove("open"); if (e.key === "ArrowRight") show(li + 1); if (e.key === "ArrowLeft") show(li - 1); });

/* ---- teklif formu -> WhatsApp ---- */
$("#form").addEventListener("submit", ev => {
  ev.preventDefault(); const f = ev.target, m = $("#msg"), warn = t => { m.textContent = t; m.style.color = "#c2410c"; };
  if (!f.ad.value.trim() || !f.tel.value.trim()) return warn("Lütfen ad soyad ve telefon alanlarını doldurun.");
  if (!f.kvkk.checked) return warn("Devam etmek için Aydınlatma Metni onay kutusunu işaretleyin.");
  const text = `Merhaba, teklif almak istiyorum.\nAd Soyad: ${f.ad.value}\nTelefon: ${f.tel.value}\nHizmet: ${f.hizmet.value}\nKonum: ${f.konum.value || "-"}\nDerinlik / uzunluk: ${f.olcu.value || "-"}\nMesaj: ${f.mesaj.value || "-"}`;
  const a = document.createElement("a"); a.href = "https://wa.me/" + FIRMA.phoneRaw + "?text=" + encodeURIComponent(text); a.target = "_blank"; a.rel = "noopener"; a.click();
  m.textContent = "WhatsApp açıldı; mesajı göndererek talebinizi tamamlayın."; m.style.color = "";
});

route();
