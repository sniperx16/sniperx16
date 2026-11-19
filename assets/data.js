
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
  { id:"s-palplans", cat:"palplans", t:"Palplanş iksa sistemleri", img:"saha/34", feat:true,
    s:"U ve Z tipi çelik palplanşlarla geçici ve kalıcı iksa perdeleri: çakma, söküm, kiralama ve satış.",
    d:"Palplanş; birbirine kilitlenen çelik profillerin zemine çakılmasıyla oluşturulan, toprak ve suyu aynı anda tutan perde sistemidir. Derin kanal ve isale hattı kazılarında, arıtma tesisi temel çukurlarında ve yeraltı suyunun yüksek olduğu sahalarda hızlı ve ekonomik bir iksa çözümüdür.",
    l:["Vibro çakma, hidrolik baskı ve ön delgili uygulama","Palplanş satışı, kiralama ve iş bitiminde söküm","Kuşak kirişi, destek ve ankrajla perde desteklenmesi","Su içinde batardo (cofferdam) imalatı"] },
  { id:"s-isale", cat:"hat", t:"İçme suyu isale hatları", img:"saha/13",
    s:"Kaynaktan depoya, depodan şebekeye uzanan iletim hatlarının kazı, boru ve test işleri.",
    d:"İçme suyunu kaynağından şehre taşıyan iletim ve isale hatlarını; kazıdan boru serimine, birleştirmeden basınç testine kadar eksiksiz inşa ediyoruz.",
    l:["Çelik, HDPE, duktil ve CTP boru imalatı","Vana odaları, sanat yapıları ve geçişler","Basınç ve sızdırmazlık testleri","Mevcut şebekelerin yenilenmesi"] },
  { id:"s-kanal", cat:"hat", t:"Yağmursuyu ve kanalizasyon sistemleri", img:"saha/22",
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
/* Saha fotoğrafları: [dosya no, açıklama, kategori] — dosyalar assets/img/saha/NN.jpg (küçük: saha/t/NN.jpg) */
const GAL = [
  ["25","Palplanş perde ve delgi makinesi","palplans"],["42","Büyük çaplı boru montajı","hat"],["23","Derin temel kazısı","temel"],
  ["34","Ekskavatörle palplanş çakımı","palplans"],["13","Palplanşlı hendekte boru serimi","hat"],["50","Palplanşlı derin temel kazısı","temel"],
  ["53","Palplanş çakım çalışması","palplans"],["12","Derin hendekte boru montajı","hat"],["28","Temel donatı ve kalıp çalışması","temel"],
  ["1","Kapalı sahada palplanş çakımı","palplans"],["10","Boru hattı hendeği","hat"],["20","Temel kazısı ve palplanş iksa","temel"],
  ["3","Palplanşla çevrilmiş kazı çukuru","palplans"],["14","Rögar ve boru imalatı","hat"],["26","Dar hendekte donatı hazırlığı","temel"],
  ["4","Palplanş iksa perdesi","palplans"],["22","Mahalle içi boru hattı","hat"],["27","Palplanşlı kazıda su yalıtımı","temel"],
  ["9","Palplanşlı hendek iksası","palplans"],["2","Palplanşlı kazıda boru bağlantısı","hat"],["29","Geniş kazı alanında iksa","temel"],
  ["15","Yapı yanında palplanş çakımı","palplans"],["18","Han Grup şantiyesinde hat çalışması","hat"],["30","Kazı alanı iksa perdesi","temel"],
  ["11","Hendek iksası ve destek profilleri","palplans"],["35","Boru bağlantı betonu","hat"],["21","Palplanş perde ve temel donatısı","temel"],
  ["16","Hendek iksası","palplans"],["5","Izgara ve kanal elemanı montajı","hat"],["39","Palplanş perde ve donatı","temel"],
  ["19","Palplanşlı kazı","palplans"],["6","Rögar elemanı yerleştirme","hat"],["17","Yapı yanında kazı ve iksa","temel"],
  ["33","Palplanş ve çelik destek","palplans"],["31","Palplanş içinde rögar imalatı","hat"],["52","Yüksek yapı kazısı","temel"],
  ["36","Palplanşlı kazıda boru ucu","palplans"],["41","Beton rögar elemanı","hat"],["48","Palplanşla kazı sınırı","temel"],
  ["37","Palplanşlar arasında çelik boru","palplans"],["44","Cadde kenarında kanal hattı","hat"],["7","Kent içinde derin kazı","temel"],
  ["40","Palplanş kuşak ve ankraj detayı","palplans"],["47","Palplanş perde","palplans"]
];
const CATS = { all:"Tümü", palplans:"Palplanş iksa", hat:"Su ve kanalizasyon hatları", temel:"Derin kazı ve temel" };
/* Saha videoları: dosyalar assets/video/NN.mp4, kapak assets/video/poster/NN.jpg */
const VID = [
  ["03","Vibro çekiçle palplanş çakımı"],["06","Ekskavatörle palplanş çakımı"],["16","Palplanşlı hendekte boru hattı"],
  ["02","Palplanş çakımı"],["12","Palplanş çakım çalışması"],["10","Palplanş çakım ekskavatörü"],
  ["04","Palplanş perde ve boru hattı"],["11","Hendek iksası ve boru"],["15","Palplanş çakımı"],
  ["07","Vibro çekiçle çakım"],["18","Hendekte palplanş çakımı"],["21","Hendekte palplanş çakımı"],
  ["17","Şantiyede ekskavatör çalışması"],["20","Ekskavatör kabininden kazı"],["09","Derin kazı ve yapı"],
  ["01","Ekskavatörle iç mekân çalışması"],["05","Saha genel görünümü"],["08","Palplanşlı kazı çukuru"],
  ["13","Kazı ve şev çalışması"],["14","Palplanş profili"],["19","Yapı yanında kazı"]
];
const SLIDES = [
  ["saha/34","Palplanş iksa sistemleri","Suyu ve zemini çelikle kontrol altına alıyoruz","Derin kazılarda çakma, söküm, kiralama ve satış dahil eksiksiz palplanş hizmeti.","s-palplans"],
  ["saha/42","İçme suyu isale hatları","Suyu kaynağından şehre taşıyoruz","İletim hatlarında kazı, boru serimi, birleştirme ve basınç testleri.","s-isale"],
  ["aritma-tesis","Arıtma tesisleri","Atık su ve içme suyu arıtma tesisleri inşa ediyoruz","İnşaat, mekanik montaj, devreye alma ve işletme eğitimi tek elden.","s-atiksu"],
  ["saha/44","Kanalizasyon ve yağmursuyu","Şehirlerin görünmeyen altyapısını kuruyoruz","Kolektör ve şebeke hatları, rögarlar, bağlantılar ve kanal görüntüleme.","s-kanal"]
];
const FAQ = [
  ["Hangi işleri üstleniyorsunuz?","Palplanş iksa sistemleri, içme suyu isale hatları, yağmursuyu ve kanalizasyon şebekeleri, kanal hattı görüntüleme, atık su ve içme suyu arıtma tesisleri ile terfi istasyonu ve su deposu yapımı."],
  ["Palplanş hangi durumlarda tercih edilmelidir?","Yeraltı su seviyesinin yüksek olduğu, kazı çukurunun kuru tutulması gereken, şantiye alanının dar ve sürenin kısıtlı olduğu projelerde palplanş çoğu zaman en hızlı ve ekonomik çözümdür."],
  ["Palplanş kiralamak mı, satın almak mı daha avantajlı?","Geçici iksalarda profiller iş bitiminde söküldüğü için kiralama genellikle daha ekonomiktir. Kalıcı perdelerde satın alma tercih edilir. Proje süresine göre iki seçeneği karşılaştırmalı sunuyoruz."],
  ["Çakım sırasında komşu binalar zarar görür mü?","Titreşime hassas bölgelerde yüksek frekanslı vibro çekiçler veya titreşimsiz hidrolik baskı yöntemi kullanılır. Yöntem, keşifte çevre yapıların durumu değerlendirilerek seçilir."],
  ["Kanal hattı görüntüleme neden yapılır?","Kamerayla hat içi inceleme; tıkanıklık, kırık, kaçak ve hatalı bağlantıları kazı yapmadan tespit etmeyi sağlar. Onarım ve temizlik doğru noktada planlanır."],
  ["Teklif için hangi bilgilere ihtiyacınız var?","Proje türü, konum, hat uzunluğu veya kazı derinliği ve varsa zemin etüt raporu ilk teklif için yeterlidir. Eksik veriler için keşif planlıyoruz."]
];

