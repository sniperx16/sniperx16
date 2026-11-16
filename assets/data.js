
/* ====== FİRMA BİLGİLERİ — yalnızca burayı düzenleyin ====== */
const FIRMA = {
  phone:   "0539 597 00 05",          // görünen telefon
  phoneRaw:"905395970005",               // ülke koduyla, boşluksuz (arama ve WhatsApp için)
  email:   "han.grupinsaat16@gmail.com",
  address: "İstiklal Mah., Evliya Sokak, 16450 Gürsu / Bursa",
  mapQuery:"HAN GRUP YAZILIM İNŞAAT, İstiklal, Evliya Sokak, 16450 Gürsu/Bursa",   // haritada aranacak adres
  mapLink: "https://maps.app.goo.gl/MutekGELJhAWVHfw7",                                // yol tarifi bağlantısı
  unvan:   "Han Grup Yazılım İnşaat Taahhüt Limited Şirketi",
  /* Aşağıdaki resmî bilgileri doldurun; boş bırakılanlar sitede gösterilmez. */
  vergiDairesi:"", vergiNo:"", mersisNo:"", ticaretSicilNo:""
};

/* Rakamlar: yalnızca doğrulanabilir bilgiler. Gerçek deneyim/proje sayılarınızı kanıtlayabildiğinizde buraya ekleyin: [sayı, ek, etiket] */
const STATS = [[7,"","Faaliyet alanı"],[4,"","Palplanş uygulama yöntemi"],[3,"","Aşamada teslim: fizibilite, uygulama, devreye alma"],[2,"","Palplanş profil tipi: U ve Z"]];

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
  ["Teklif için hangi bilgilere ihtiyacınız var?","Proje türü, konum, hat uzunluğu veya kazı derinliği ve varsa zemin etüt raporu ilk teklif için yeterlidir. Eksik veriler için keşif planlıyoruz."]
];

