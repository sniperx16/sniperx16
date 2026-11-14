document.documentElement.classList.add("js");

/* ====== FİRMA BİLGİLERİ — yalnızca burayı düzenleyin ====== */
const FIRMA = {
  phone:   "0 (5XX) XXX XX XX",          // görünen telefon
  phoneRaw:"905XXXXXXXXX",               // ülke koduyla, boşluksuz (arama ve WhatsApp için)
  email:   "info@firmaniz.com",
  address: "Adres bilginizi buraya yazın",
  mapQuery:""                            // Google Haritalar'da aranacak adres; doldurulunca harita görünür
};

/* ====== FAALİYET ALANLARI ====== */
const SVC = [
  { id:"s-palplans", cat:"palplans", t:"Palplanş iksa sistemleri", img:"palplans-ust", feat:true,
    s:"U ve Z tipi çelik palplanşlarla geçici ve kalıcı iksa perdeleri: çakma, söküm, kiralama ve satış.",
    d:"Palplanş; birbirine kilitlenen çelik profillerin zemine çakılmasıyla oluşturulan, toprak ve suyu aynı anda tutan perde sistemidir. Derin kanal ve isale hattı kazılarında, arıtma tesisi temel çukurlarında ve yeraltı suyunun yüksek olduğu sahalarda hızlı ve ekonomik bir iksa çözümüdür.",
    l:["Vibro çakma, hidrolik baskı ve ön delgili uygulama","Palplanş satışı, kiralama ve iş bitiminde söküm","Kuşak kirişi, destek ve ankrajla perde desteklenmesi","Su içinde batardo (cofferdam) imalatı"] },
  { id:"s-isale", cat:"hat", t:"İçme suyu isale hatları", img:"isale-hatti",
    s:"Kaynaktan depoya, depodan şebekeye uzanan iletim hatlarının kazı, boru ve test işleri.",
    d:"İçme suyunu kaynağından şehre taşıyan iletim ve isale hatlarını; kazıdan boru serimine, birleştirmeden basınç testine kadar eksiksiz inşa ediyoruz.",
    l:["Çelik, HDPE, duktil ve CTP boru imalatı","Vana odaları, sanat yapıları ve geçişler","Basınç ve sızdırmazlık testleri","Mevcut şebekelerin yenilenmesi"] },
  { id:"s-kanal", cat:"hat", t:"Yağmursuyu ve kanalizasyon sistemleri", img:"kanalizasyon-hendek",
    s:"Derin kanal kazıları, boru serimi, rögar ve bağlantı imalatlarıyla atık su ve yağmursuyu şebekeleri.",
    d:"Mahalle ve cadde ölçeğinde kanalizasyon ve yağmursuyu şebekelerini, kolektör hatlarını ve evsel bağlantıları inşa ediyoruz. Derin kazılarda hendek iksası ve palplanş ile güvenli çalışma sağlanır.",
    l:["Kolektör ve şebeke hatları","Rögar, baca ve ızgara imalatları","Evsel ve parsel bağlantıları","Hendek iksası ve susuzlaştırma"] },
  { id:"s-goruntuleme", cat:"hat", t:"Kanal hattı görüntüleme", img:"boru-ici",
    s:"Hatların kamerayla incelenmesi; tıkanıklık, kırık ve kaçak tespiti, temizlik.",
    d:"Kanalizasyon ve yağmursuyu hatlarını robot kameralarla içeriden görüntülüyor, kazı yapmadan arıza noktasını belirliyoruz. Görüntüleme öncesi ve sonrası hat temizliği yapılır, bulgular raporlanır.",
    l:["CCTV robot kamera ile hat içi inceleme","Tıkanıklık, kırık, kaçak ve hatalı bağlantı tespiti","Yüksek basınçlı hat temizliği","Görüntülü ve yazılı raporlama"] },
  { id:"s-atiksu", cat:"tesis", t:"Atık su arıtma tesisleri", img:"aritma-havuz",
    s:"Arıtma tesisi yapı, havuz ve boru işleri; mekanik montaj ve devreye alma.",
    d:"Evsel ve endüstriyel atık su arıtma tesislerinin inşaat, mekanik ve boru işlerini üstleniyor; tesisi performans testlerinden sonra çalışır halde teslim ediyoruz.",
    l:["Havalandırma ve çöktürme havuzları","Mekanik ekipman ve boru montajı","Performans testleri ve devreye alma","İşletme personeli eğitimi"] },
  { id:"s-icmesuyu", cat:"tesis", t:"İçme suyu arıtma tesisleri", img:"aritma-tesis",
    s:"Şebekeye verilecek suyun arıtıldığı tesislerin inşaatı ve ekipman montajı.",
    d:"Ham suyun içilebilir hale getirildiği arıtma tesislerinde betonarme yapılar, filtre üniteleri ve proses boru işlerini projesine uygun olarak inşa ediyoruz.",
    l:["Filtre, çöktürme ve temiz su yapıları","Proses boruları ve ekipman montajı","Test, dezenfeksiyon ve devreye alma"] },
  { id:"s-terfi", cat:"tesis", t:"Terfi istasyonları ve su depoları", img:"terfi",
    s:"Pompa istasyonları, köy depoları ve betonarme su depolarının yapımı.",
    d:"Suyun yükseltilmesi ve depolanması için gereken terfi istasyonlarını ve betonarme su depolarını, mekanik ve elektrik işleriyle birlikte anahtar teslim yapıyoruz.",
    l:["Terfi ve pompa istasyonları","Betonarme su depoları","Pompa, vana ve pano montajı"] }
];
const GAL = [
  ["palplans-perde","Çelik palplanş perde","palplans"],["isale-hatti","İsale hattı imalatı","hat"],["aritma-tesis","Arıtma tesisi","tesis"],
  ["derin-kazi","Palplanşlı derin kazı","palplans"],["kanalizasyon-hendek","Kanalizasyon hendeği iksası","hat"],["aritma-havuz","Havalandırma havuzu","tesis"],
  ["hero-batardo","Su içinde palplanş batardo","palplans"],["boru-montaj","Boru montajı","hat"],["terfi","Terfi istasyonu","tesis"],
  ["palplans-ust","Kazı kenarı palplanş perdesi","palplans"],["kanal-hendek","Kanal hattı imalatı","hat"],["kopru-batardo","Batardo imalatı","palplans"],
  ["boru-ici","Boru içi kontrol","hat"],["kilit-detay","Palplanş kilit detayı","palplans"],["cakma-makinesi","Delgi ve çakma makinesi","palplans"]
];
const CATS = { all:"Tümü", palplans:"Palplanş iksa", hat:"Su ve kanalizasyon hatları", tesis:"Arıtma ve terfi tesisleri" };
const SLIDES = [
  ["hero-batardo","Palplanş iksa sistemleri","Suyu ve zemini çelikle kontrol altına alıyoruz","Derin kazılarda çakma, söküm, kiralama ve satış dahil eksiksiz palplanş hizmeti.","s-palplans"],
  ["isale-hatti","İçme suyu isale hatları","Suyu kaynağından şehre taşıyoruz","İletim hatlarında kazı, boru serimi, birleştirme ve basınç testleri.","s-isale"],
  ["aritma-tesis","Arıtma tesisleri","Atık su ve içme suyu arıtma tesisleri inşa ediyoruz","İnşaat, mekanik montaj, devreye alma ve işletme eğitimi tek elden.","s-atiksu"],
  ["kanalizasyon-hendek","Kanalizasyon ve yağmursuyu","Şehirlerin görünmeyen altyapısını kuruyoruz","Kolektör ve şebeke hatları, rögarlar, bağlantılar ve kanal görüntüleme.","s-kanal"]
];
const FAQ = [
  ["Hangi işleri üstleniyorsunuz?","Palplanş iksa sistemleri, içme suyu isale hatları, yağmursuyu ve kanalizasyon şebekeleri, kanal hattı görüntüleme, atık su ve içme suyu arıtma tesisleri ile terfi istasyonu ve su deposu yapımı."],
  ["Palplanş hangi durumlarda tercih edilmelidir?","Yeraltı su seviyesinin yüksek olduğu, kazı çukurunun kuru tutulması gereken, şantiye alanının dar ve sürenin kısıtlı olduğu projelerde palplanş çoğu zaman en hızlı ve ekonomik çözümdür."],
  ["Palplanş kiralamak mı, satın almak mı daha avantajlı?","Geçici iksalarda profiller iş bitiminde söküldüğü için kiralama genellikle daha ekonomiktir. Kalıcı perdelerde satın alma tercih edilir. Proje süresine göre iki seçeneği karşılaştırmalı sunuyoruz."],
  ["Çakım sırasında komşu binalar zarar görür mü?","Titreşime hassas bölgelerde yüksek frekanslı vibro çekiçler veya titreşimsiz hidrolik baskı yöntemi kullanılır. Yöntem, keşifte çevre yapıların durumu değerlendirilerek seçilir."],
  ["Kanal hattı görüntüleme neden yapılır?","Kamerayla hat içi inceleme; tıkanıklık, kırık, kaçak ve hatalı bağlantıları kazı yapmadan tespit etmeyi sağlar. Onarım ve temizlik doğru noktada planlanır."],
  ["Teklif için hangi bilgilere ihtiyacınız var?","Proje türü, konum, hat uzunluğu veya kazı derinliği ve varsa zemin etüt raporu ilk teklif için yeterlidir. Eksik veriler için ücretsiz keşif yapıyoruz."]
];

const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const img = n => `assets/img/${n}.jpg`;
const ARROW = '<svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M2 7h10M8 3l4 4-4 4"/></svg>';
const CHECK = '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M4 10l4 4 8-9"/></svg>';

/* ---- içerik üretimi ---- */
$("#ticks").innerHTML = ["Palplanş iksa sistemleri","İçme suyu isale hatları","Kanalizasyon ve yağmursuyu","Arıtma tesisleri"].map(t => `<li>${CHECK}${t}</li>`).join("");
$("#homeCards").innerHTML = SVC.map((s, i) => `<article class="card ${s.feat ? "feat" : ""} rv" style="--d:${i ? (i - 1) % 3 : 0}">
  <figure><img src="${img(s.img)}" alt="${s.t}" loading="lazy"><span class="no">0${i + 1}</span></figure>
  <div class="b">${s.feat ? '<span class="pill">Ana faaliyet</span>' : ""}<h3>${s.t}</h3><p>${s.s}</p><a class="more" href="#faaliyet-alanlari" data-target="${s.id}">Detay ${ARROW}</a></div></article>`).join("");
$("#rows").innerHTML = SVC.map((s, i) => `<article class="row" id="${s.id}">
  <figure><img src="${img(s.img)}" alt="${s.t}" loading="lazy"><span class="no">0${i + 1}</span></figure>
  <div><div class="kicker">Faaliyet alanı</div><h2>${s.t}</h2><p>${s.d}</p><ul>${s.l.map(x => `<li>${CHECK}<span>${x}</span></li>`).join("")}</ul><a href="#iletisim" class="btn">Teklif al</a></div></article>`).join("");
$("#drop").innerHTML = SVC.map(s => `<a href="#faaliyet-alanlari" data-target="${s.id}">${s.t}</a>`).join("");
$("#footSvc").innerHTML = SVC.slice(0, 6).map(s => `<li><a href="#faaliyet-alanlari" data-target="${s.id}">${s.t}</a></li>`).join("");
$("#f-hizmet").innerHTML = SVC.map(s => `<option>${s.t}</option>`).join("") + "<option>Diğer</option>";
$("#faq").innerHTML = FAQ.map(([q, a], i) => `<details${i ? "" : " open"}><summary>${q}</summary><p>${a}</p></details>`).join("");
const gItem = ([f, t, c], i) => `<button class="g" data-i="${i}" data-c="${c}"><img src="${img(f)}" alt="${t}" loading="lazy"><span><small>${CATS[c]}</small>${t}</span></button>`;
$("#gal").innerHTML = GAL.map(gItem).join("");
$("#homeGal").innerHTML = GAL.slice(0, 6).map(gItem).join("");
$("#filters").innerHTML = Object.entries(CATS).map(([k, v]) => `<button data-c="${k}" aria-pressed="${k === "all"}">${v}</button>`).join("");

/* ---- firma bilgileri ---- */
$$("[data-f]").forEach(e => e.textContent = FIRMA[e.dataset.f]);
$$("[data-tel]").forEach(e => e.href = "tel:+" + FIRMA.phoneRaw);
$$("[data-mail]").forEach(e => e.href = "mailto:" + FIRMA.email);
$$("[data-wa]").forEach(e => e.href = "https://wa.me/" + FIRMA.phoneRaw);
$("#yr").textContent = new Date().getFullYear();
if (FIRMA.mapQuery) $("#map").innerHTML = `<iframe title="Konum haritası" loading="lazy" src="https://www.google.com/maps?q=${encodeURIComponent(FIRMA.mapQuery)}&output=embed"></iframe>`;
const ld = document.createElement("script"); ld.type = "application/ld+json";
ld.textContent = JSON.stringify({ "@context": "https://schema.org", "@type": "GeneralContractor", name: "Han Grup Yazılım İnşaat", telephone: "+" + FIRMA.phoneRaw, email: FIRMA.email, address: FIRMA.address, areaServed: "TR", knowsAbout: SVC.map(s => s.t) });
document.head.appendChild(ld);

/* ---- açılış slaytı ---- */
const hero = $("#hero");
hero.insertAdjacentHTML("afterbegin", SLIDES.map(([f, lab, h, p, id], i) => `<div class="slide${i ? "" : " on"}"><img src="${img(f)}" alt="" ${i ? 'loading="lazy"' : 'fetchpriority="high"'}>
  <div class="cap"><div class="wrap"><div><span class="lab">${lab}</span><h1>${h}</h1><p>${p}</p>
  <div class="acts"><a class="btn" href="#faaliyet-alanlari" data-target="${id}">Detaylı bilgi</a><a class="btn line" href="#iletisim">Teklif al</a></div></div></div></div></div>`).join(""));
const slides = $$(".slide", hero); let cur = 0, timer;
const go = i => { slides[cur].classList.remove("on"); cur = (i + slides.length) % slides.length; slides[cur].classList.add("on");
  $("#cur").textContent = "0" + (cur + 1); clearInterval(timer); timer = setInterval(() => go(cur + 1), 6500); };
$("#prev").onclick = () => go(cur - 1); $("#next").onclick = () => go(cur + 1); go(0);

/* ---- sekmeler ---- */
const tabs = $$("#stTabs button"), panes = $$(".split .pane"), phs = $$("#stPh img");
tabs.forEach((b, i) => b.onclick = () => { tabs.forEach((x, j) => x.setAttribute("aria-selected", i === j)); panes.forEach((x, j) => x.classList.toggle("on", i === j)); phs.forEach((x, j) => x.classList.toggle("on", i === j)); });

/* ---- sayfa geçişleri ---- */
const VIEWS = ["anasayfa", "kurumsal", "faaliyet-alanlari", "galeri", "iletisim"];
let pendingTarget = null;
const menu = $("#menu"), burger = $("#burger");
const setMenu = o => { menu.classList.toggle("open", o); burger.setAttribute("aria-expanded", o); };
burger.onclick = () => setMenu(!menu.classList.contains("open"));
function route() {
  const name = VIEWS.includes(location.hash.slice(1)) ? location.hash.slice(1) : "anasayfa";
  $$(".view").forEach(v => v.classList.toggle("on", v.id === "v-" + name));
  $$("[data-nav]").forEach(a => a.classList.toggle("active", a.dataset.nav === name));
  setMenu(false);
  const t = pendingTarget && document.getElementById(pendingTarget); pendingTarget = null;
  if (t) requestAnimationFrame(() => t.scrollIntoView({ block: "start" })); else scrollTo(0, 0);
  observe();
}
document.addEventListener("click", e => {
  const a = e.target.closest("a[href^='#']"); if (!a) return;
  pendingTarget = a.dataset.target || null;
  const h = a.getAttribute("href");
  if (h === location.hash || (h === "#anasayfa" && !location.hash)) { e.preventDefault(); route(); }
});
addEventListener("hashchange", route);

/* ---- belirme + sayaç ---- */
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { threshold: .1 });
function observe() { $$(".view.on .rv:not(.in)").forEach(e => io.observe(e)); }
const fmt = n => n.toLocaleString("tr-TR");
const cio = new IntersectionObserver(es => es.forEach(e => { if (!e.isIntersecting) return; cio.disconnect();
  $$("[data-count]", e.target).forEach(el => { const end = +el.dataset.count, t0 = performance.now();
    const tick = t => { const p = Math.min((t - t0) / 1600, 1); el.textContent = fmt(Math.round(end * (1 - Math.pow(1 - p, 3)))); if (p < 1) requestAnimationFrame(tick); }; requestAnimationFrame(tick); }); }), { threshold: .4 });
cio.observe($("#stats"));

/* ---- galeri ---- */
$("#filters").addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return;
  $$("#filters button").forEach(x => x.setAttribute("aria-pressed", x === b));
  $$("#gal .g").forEach(g => g.classList.toggle("hide", b.dataset.c !== "all" && g.dataset.c !== b.dataset.c)); });
const lb = $("#lb"); let li = 0;
const show = i => { li = (i + GAL.length) % GAL.length; $("img", lb).src = img(GAL[li][0]); $("p", lb).textContent = GAL[li][1]; lb.classList.add("open"); };
document.addEventListener("click", e => { const g = e.target.closest(".g"); if (g) show(+g.dataset.i); });
lb.addEventListener("click", e => { if (e.target.tagName === "IMG") show(li + 1); else lb.classList.remove("open"); });
addEventListener("keydown", e => { if (!lb.classList.contains("open")) return; if (e.key === "Escape") lb.classList.remove("open"); if (e.key === "ArrowRight") show(li + 1); if (e.key === "ArrowLeft") show(li - 1); });

/* ---- üst menü gölgesi + yukarı çık ---- */
const hdr = $("#hdr"), toTop = $("#toTop");
addEventListener("scroll", () => { hdr.classList.toggle("scrolled", scrollY > 60); toTop.classList.toggle("show", scrollY > 700); }, { passive: true });
toTop.onclick = () => scrollTo({ top: 0, behavior: "smooth" });

/* ---- teklif formu -> WhatsApp ---- */
$("#form").addEventListener("submit", ev => {
  ev.preventDefault(); const f = ev.target, m = $("#msg"), warn = t => { m.textContent = t; m.style.color = "#c2410c"; };
  if (!f.ad.value.trim() || !f.tel.value.trim()) return warn("Lütfen ad soyad ve telefon alanlarını doldurun.");
  if (!f.kvkk.checked) return warn("Devam etmek için KVKK onay kutusunu işaretleyin.");
  const text = `Merhaba, teklif almak istiyorum.\nAd Soyad: ${f.ad.value}\nTelefon: ${f.tel.value}\nHizmet: ${f.hizmet.value}\nKonum: ${f.konum.value || "-"}\nDerinlik / uzunluk: ${f.olcu.value || "-"}\nMesaj: ${f.mesaj.value || "-"}`;
  const a = document.createElement("a"); a.href = "https://wa.me/" + FIRMA.phoneRaw + "?text=" + encodeURIComponent(text); a.target = "_blank"; a.rel = "noopener"; a.click();
  m.textContent = "WhatsApp açıldı; mesajı göndererek talebinizi tamamlayın."; m.style.color = "";
});

route();
