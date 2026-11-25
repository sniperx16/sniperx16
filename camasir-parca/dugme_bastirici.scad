// Çamaşır makinesi düğme bastırıcı - parametrik (mm)
L        = 50;   // MAVİ parçanın yüzü ile DÜĞMENİN arkası arasındaki mesafe -> ölç, buraya yaz
mavi_w   = 30;   // mavi parçaya dayanan plaka genişliği
mavi_h   = 22;   // plaka yüksekliği
kol_w    = 12;   // gövde (çubuk) kalınlığı
kol_h    = 10;
duz_t    = 3;    // plaka kalınlığı
dudak    = 6;    // mavi parçayı tutan dudak boyu
dugme_w  = 14;   // düğme ucunun ölçüsü (cep iç boyutu)
duvar    = 3;

// mavi tarafı: plaka + üst/alt tutma dudakları
translate([0,-mavi_w/2,-mavi_h/2]) cube([duz_t,mavi_w,mavi_h]);
for (s=[-1,1]) translate([-dudak, s>0 ? mavi_w/2-duz_t : -mavi_w/2, -mavi_h/2]) cube([dudak+duz_t,duz_t,mavi_h]);
// çubuk
translate([duz_t,-kol_w/2,-kol_h/2]) cube([L,kol_w,kol_h]);
// düğme tarafı: plaka + 4 duvarlı cep
D = dugme_w + 2*duvar;
translate([duz_t+L,-D/2,-D/2]) cube([duz_t,D,D]);
translate([2*duz_t+L,0,0]) difference(){
  translate([0,-D/2,-D/2]) cube([duvar,D,D]);
  translate([-1,-dugme_w/2,-dugme_w/2]) cube([duvar+2,dugme_w,dugme_w]);
}
