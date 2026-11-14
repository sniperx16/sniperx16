// =====================================================================
// KIRA PRO — parametrik gövde (pan/tilt başlı masaüstü robot)
// Orijinal KIRA dosyalarından bağımsız, yeni tasarım. Orijinaller değiştirilmez.
//
// Parçalar (tek tek STL almak için):
//   openscad -D 'PART="base"'        -o base.stl        kira_pro.scad
//   openscad -D 'PART="bottom"'      -o bottom.stl      kira_pro.scad
//   openscad -D 'PART="turntable"'   -o turntable.stl   kira_pro.scad
//   openscad -D 'PART="head"'        -o head.stl        kira_pro.scad
//   openscad -D 'PART="head_back"'   -o head_back.stl   kira_pro.scad
//   openscad -D 'PART="pan_ring"'    -o pan_ring.stl    kira_pro.scad
//   openscad -D 'PART="shutter_frame"' -o shutter_frame.stl kira_pro.scad
//   openscad -D 'PART="shutter"'     -o shutter.stl     kira_pro.scad
//   PART="assembly" -> önizleme (baskı için değil)
//
// ÖNEMLİ: "ÖLÇ" yazan bütün değerler tipik/yaygın ölçülerdir.
// Baskıdan önce gerçek parçalardan kumpasla ölçüp güncelleyin.
// =====================================================================

PART = "assembly";
PAN_ANGLE  = 0;    // önizleme: sağa/sola (+/-60)
TILT_ANGLE = 0;    // önizleme: yukarı/aşağı (+/-30)
SHUTTER_OPEN = false;  // önizleme: kamera kapağı açık/kapalı

$fn = 64;
tol  = 0.3;        // baskı toleransı (yazıcıya göre 0.2-0.4)
wall = 2.4;

// ---------- Servo: SG90 / MG90S (ÖLÇ) ----------
sv_L   = 22.8;   // gövde uzunluğu
sv_W   = 12.2;   // gövde genişliği
sv_H   = 22.7;   // alt yüzeyden üst kapağa
sv_tab_z  = 15.9;  // kulakçık alt yüzü (servo altından)
sv_tab_t  = 2.5;   // kulakçık kalınlığı
sv_tab_L  = 32.4;  // kulakçıklar dahil toplam uzunluk
sv_hole_pitch = 27.6; // kulakçık vida delikleri arası
sv_shaft_off  = 5.4;  // mil merkezi - gövde merkezi (uzunluk ekseninde)
sv_shaft_len  = 4.0;
horn_d = 21;       // yuvarlak servo kolu (horn) çapı (ÖLÇ)
horn_t = 2.2;

// ---------- Elektronik (ÖLÇ) ----------
td_L = 62;  td_W = 26;  td_T = 10;     // LILYGO T-Display-S3 kart
lcd_win_L = 44; lcd_win_W = 24;        // 1.9" 170x320 görünür alan + pay
lcd_off_x = 3;                          // LCD'nin kart merkezine göre kayması (USB tarafı)
cam_lens_d = 8.5;                       // kamera lens tutucu çapı
cam_mod    = 8.6;                       // kamera modülü kare kenarı
oled_win   = 28;                        // SH1107 1.5" görünür pencere (1.3" için ~30x15)
spk_d      = 28;                        // hoparlör çapı (28/36/40 mm olabilir)
bb_L = 47; bb_W = 35;                   // 170'lik mini breadboard

// ---------- Ana ölçüler ----------
base_W = 100; base_D = 80; base_H = 50; base_r = 9;
head_W = 68;  head_D = 42; head_H = 56; head_r = 8;
disc_d = 70;  disc_t = 3;
yoke_t = 4;   yoke_gap = 4;              // baş yan yüzü ile kol arası boşluk
// Baş merkezinden köşeye uzaklık + pay = eğilme ekseni yüksekliği (disk üstünden)
tilt_axis_h = ceil(sqrt(pow(head_D/2,2)+pow(head_H/2,2))) + 3;

// Pan servo kulakçıkları üst plakaya oturur; disk, servo kolunun üstünde
disc_z0 = base_H + sv_tab_t + (sv_H - sv_tab_z - sv_tab_t) + horn_t; // disk alt yüzü
ring_r_out = 28; ring_r_in = 25;         // diski taşıyan destek halkası
cable_r = 20;                            // kablo geçiş yarıçapı

// ---------------------------------------------------------------------
module rbox(w, d, h, r) {                 // dikey kenarları yuvarlatılmış kutu
    hull() for (x=[-1,1], y=[-1,1])
        translate([x*(w/2-r), y*(d/2-r), 0]) cylinder(r=r, h=h);
}
module rbox_y(w, d, h, r) {               // ön görünüşte köşeleri yuvarlak kutu (y ekseni)
    hull() for (x=[-1,1], z=[-1,1])
        translate([x*(w/2-r), d/2, z*(h/2-r)]) rotate([90,0,0]) cylinder(r=r, h=d);
}

// Servo hacmi (yerel: uzunluk X, mil +Z, mil X=+sv_shaft_off)
module servo_model() {
    color("dimgray") {
        translate([-sv_L/2, -sv_W/2, 0]) cube([sv_L, sv_W, sv_H]);
        translate([-sv_tab_L/2, -sv_W/2, sv_tab_z]) cube([sv_tab_L, sv_W, sv_tab_t]);
        translate([sv_shaft_off, 0, sv_H]) cylinder(d=5, h=sv_shaft_len);
    }
}

// ============================ GÖVDE (BASE) ============================
module arc_slot(r, w, a0, a1, h) {
    for (a=[a0:4:a1]) hull() {
        rotate(a)   translate([r,0,0]) cylinder(d=w, h=h);
        rotate(min(a+4,a1)) translate([r,0,0]) cylinder(d=w, h=h);
    }
}

module base() {
    difference() {
        union() {
            difference() {
                rbox(base_W, base_D, base_H, base_r);
                translate([0,0,-0.01]) rbox(base_W-2*wall, base_D-2*wall, base_H-wall+0.01, base_r-wall);
            }
            // alt kapak vida köşe kolonları
            for (x=[-1,1], y=[-1,1])
                translate([x*(base_W/2-wall-4), y*(base_D/2-wall-4), 0])
                    difference() { cylinder(d=8, h=base_H-wall); cylinder(d=2.5, h=12); }
        }
        // pan servo yuvası: mil gövde merkezinde olacak şekilde
        translate([-sv_shaft_off, 0, base_H-wall-1]) {
            translate([-(sv_L+tol*2)/2, -(sv_W+tol*2)/2, 0]) cube([sv_L+tol*2, sv_W+tol*2, wall+2]);
            for (x=[-1,1]) translate([x*sv_hole_pitch/2, 0, 0]) cylinder(d=2.0, h=wall+2);
        }
        // kablo yay yarığı (pan +/-60 derece)
        translate([0,0,base_H-wall-1]) arc_slot(cable_r, 8, 30, 150, wall+2);
        // ön: OLED penceresi (sol) + hoparlör ızgarası (sağ)
        translate([-22, -base_D/2-1, base_H*0.55-oled_win/2])
            cube([oled_win, wall+2, oled_win]);
        translate([22, -base_D/2+wall+1, base_H*0.5]) rotate([90,0,0])
            for (i=[-2:2], j=[-2:2]) if (i*i+j*j <= 5)
                translate([i*4.5, j*4.5, 0]) cylinder(d=2.6, h=wall+2, $fn=16);
        // arka: USB-C güç girişi
        translate([0, base_D/2-wall-1, 8]) cube([14, wall+2, 8], center=true);
        // yan havalandırma
        for (s=[-1,1], i=[0:4])
            translate([s*(base_W/2), -12+i*6, 14]) cube([wall*3, 2.5, 18], center=true);
    }
    // iç: hoparlör tutucu halka (ön duvar arkası)
    translate([22, -base_D/2+wall, base_H*0.5]) rotate([-90,0,0])
        difference() { cylinder(d=spk_d+4, h=4); translate([0,0,-1]) cylinder(d=spk_d+tol*2, h=6); }
    // iç: OLED modül çerçevesi
    translate([-22+oled_win/2, -base_D/2+wall, base_H*0.55]) difference() {
        translate([-(oled_win+8)/2, 0, -(oled_win+8)/2]) cube([oled_win+8, 3, oled_win+8]);
        translate([-(oled_win+2)/2, -1, -(oled_win+2)/2]) cube([oled_win+2, 5, oled_win+2]);
    }
}

module bottom() {
    difference() {
        rbox(base_W-2*wall-tol*2, base_D-2*wall-tol*2, 2.4, base_r-wall);
        for (x=[-1,1], y=[-1,1])
            translate([x*(base_W/2-wall-4), y*(base_D/2-wall-4), -1]) {
                cylinder(d=3.2, h=5); cylinder(d=6, h=1.6);   // havşa
            }
        // breadboard konum işareti (arka sol, servodan uzak)
        translate([-base_W/2+wall+4, base_D/2-wall-4-bb_W, 2.0]) cube([bb_L, bb_W, 1]);
    }
    // kaymaz ayak yuvaları
}

// ========================= DÖNER TABLA + ÇATAL =========================
yoke_x_in  = head_W/2 + yoke_gap;          // kol iç yüzü
yoke_x_out = yoke_x_in + yoke_t;            // kol dış yüzü

module tilt_servo_cut() {   // sağ kolda servo üst kısmı geçiş deliği + vida delikleri
    // yerel servo -> dünya: yerel Z -> -X, yerel X -> +Z
    translate([yoke_x_out + sv_tab_z + sv_tab_t, 0, tilt_axis_h - sv_shaft_off])
        rotate([0,-90,0]) {
            translate([-(sv_L+tol*2)/2, -(sv_W+tol*2)/2, sv_tab_z+sv_tab_t-0.01])
                cube([sv_L+tol*2, sv_W+tol*2, 10]);
            for (x=[-1,1]) translate([x*sv_hole_pitch/2, 0, sv_tab_z]) cylinder(d=2.0, h=12);
        }
}

module turntable() {
    difference() {
        union() {
            cylinder(d=disc_d, h=disc_t);
            // çatal tabanı
            translate([-(yoke_x_out), -9, 0]) cube([2*yoke_x_out, 18, disc_t]);
            // kollar
            for (s=[-1,1]) translate([s>0 ? yoke_x_in : -yoke_x_out, -9, 0])
                hull() {
                    cube([yoke_t, 18, disc_t]);
                    translate([0, 9, tilt_axis_h]) rotate([0,90,0]) cylinder(d=18, h=yoke_t);
                }
        }
        // servo kolu (horn) yuvası + merkez vida
        translate([0,0,-0.01]) cylinder(d=horn_d+tol*2, h=horn_t);
        cylinder(d=3.2, h=10);
        // kablo deliği (arka)
        rotate(90) translate([cable_r,0,-1]) cylinder(d=9, h=10);
        // sol kol: M3 mil vidası
        translate([-yoke_x_out-1, 0, tilt_axis_h]) rotate([0,90,0]) cylinder(d=3.4, h=yoke_t+2);
        tilt_servo_cut();
    }
}

// ================================ BAŞ =================================
cam_z  = head_H/2 - 13;     // kamera yüksekliği (baş merkezine göre)
lcd_z  = -8;                // ekran merkez yüksekliği

module head() {
    difference() {
        union() {
            difference() {
                rbox_y(head_W, head_D, head_H, head_r);
                // içi boş, arka açık (arka kapak ayrı)
                translate([0, wall, 0]) rbox_y(head_W-2*wall, head_D, head_H-2*wall, head_r-wall);
            }
            // arka kapak vida kolonları
            for (x=[-1,1], z=[-1,1])
                translate([x*(head_W/2-wall-3.5), head_D/2, z*(head_H/2-wall-3.5)])
                    rotate([90,0,0]) difference() { cylinder(d=7, h=16); cylinder(d=2.2, h=10); }
            // sağ: servo kolu bağlantı göbeği, sol: mil göbeği
            for (s=[-1,1]) translate([s*(head_W/2-wall), 0, 0]) rotate([0, 90*s, 0])
                cylinder(d=26, h=wall+0.01);
            // ekran kart çerçevesi (iç)
            translate([0, -head_D/2+wall, lcd_z]) difference() {
                translate([-(td_L+6)/2, 0, -(td_W+6)/2]) cube([td_L+6, 3, td_W+6]);
                translate([-(td_L+tol*2)/2, -1, -(td_W+tol*2)/2]) cube([td_L+tol*2, 5, td_W+tol*2]);
            }
            // kamera modülü cebi (iç)
            translate([0, -head_D/2+wall, cam_z]) difference() {
                translate([-(cam_mod+5)/2, 0, -(cam_mod+5)/2]) cube([cam_mod+5, 3, cam_mod+5]);
                translate([-(cam_mod+tol*2)/2, -1, -(cam_mod+tol*2)/2]) cube([cam_mod+tol*2, 5, cam_mod+tol*2]);
            }
        }
        // ekran penceresi
        translate([lcd_off_x - lcd_win_L/2, -head_D/2-1, lcd_z - lcd_win_W/2]) cube([lcd_win_L, wall+2, lcd_win_W]);
        // kamera lens deliği (içe doğru pahlı)
        translate([0, -head_D/2-4, cam_z]) rotate([-90,0,0]) {
            cylinder(d=cam_lens_d+tol*2, h=wall+6);
            translate([0,0,4+wall-0.8]) cylinder(d1=cam_lens_d+tol*2, d2=cam_lens_d+4, h=1);
        }
        // kamera kapağı çerçevesi vida delikleri (M2, 2.0 = kılavuzsuz)
        for (x=[-1,1]) translate([x*(sf_L/2-3), -head_D/2-1, cam_z]) rotate([-90,0,0]) cylinder(d=2.0, h=wall+2, $fn=16);
        // mikrofon delikleri (XIAO Sense mikrofonu hizasına göre ÖLÇ)
        for (i=[-1:1]) translate([head_W/2-wall-2.5, -head_D/2-1, cam_z + i*2.6]) rotate([-90,0,0]) cylinder(d=1.3, h=wall+2, $fn=12);
        // sağ göbek: servo kolu yuvası + vida
        translate([head_W/2+0.01, 0, 0]) rotate([0,-90,0]) {
            cylinder(d=horn_d+tol*2, h=horn_t);
            cylinder(d=2.2, h=10);
        }
        // sol göbek: M3 mil vidası (kılavuzsuz vida için 2.6)
        translate([-head_W/2-1, 0, 0]) rotate([0,90,0]) cylinder(d=2.6, h=12);
    }
}

module head_back() {
    difference() {
        translate([0, 0, 0]) rbox_y(head_W-2*wall-tol*2, 2.4, head_H-2*wall-tol*2, head_r-wall);
        for (x=[-1,1], z=[-1,1])
            translate([x*(head_W/2-wall-3.5), 3, z*(head_H/2-wall-3.5)]) rotate([90,0,0]) cylinder(d=2.6, h=5);
        // havalandırma
        for (i=[-3:3]) translate([i*6, -1, 4]) cube([2.5, 5, 18], center=true);
        // kablo çıkışı (alt)
        translate([0, -1, -(head_H/2-wall-8)]) rotate([-90,0,0]) cylinder(d=9, h=5);
    }
}

// Kamera kapağı çerçevesi: ön yüze 2x M2 vida ile takılır, düz basılır.
// Kapak çerçevenin içindeki kanalda sağa-sola kayar.
sf_L = 50; sf_H = 22; sf_back = 1.2; sf_slot = 1.8; sf_lip = 1.2; sf_lip_w = 2.5;
sh_W = 16; sh_T = 1.4;
sh_H = sf_H - 2*3 - tol*2;          // kanal yüksekliği = sf_H - 2*yan duvar

module shutter_frame() {           // yerel: X uzunluk, Y yükseklik, Z kalınlık (Z=0 baş yüzüne değer)
    difference() {
        translate([-sf_L/2, -sf_H/2, 0]) cube([sf_L, sf_H, sf_back + sf_slot + sf_lip]);
        // kanal (sağdan açık; kapak buradan takılır)
        translate([-sf_L/2 + 3, -(sf_H/2 - 3), sf_back]) cube([sf_L, sf_H - 6, sf_slot]);
        // ön açıklık (dudaklar arası)
        translate([-sf_L/2 + 3, -(sf_H/2 - 3 - sf_lip_w), sf_back]) cube([sf_L, sf_H - 6 - 2*sf_lip_w, 10]);
        // lens deliği
        translate([0, 0, -1]) cylinder(d=cam_lens_d + 1, h=5);
        // vida delikleri
        for (x=[-1,1]) translate([x*(sf_L/2-3), 0, -1]) { cylinder(d=2.4, h=10, $fn=16); }
    }
}

module shutter() {                 // yerel: X genişlik, Y yükseklik, Z kalınlık
    translate([-sh_W/2, -sh_H/2, 0]) cube([sh_W, sh_H, sh_T]);
    translate([-1.5, -3, sh_T]) cube([3, 6, sf_lip + 1.5]);   // tutma tırnağı (açıklıktan dışarı)
}

module pan_ring() {                // diski taşıyan halka; gövde üstüne yapıştırılır, üstüne PTFE bant
    difference() {
        cylinder(r=ring_r_out, h=disc_z0-base_H-0.4);
        translate([0,0,-1]) cylinder(r=ring_r_in, h=20);
    }
}

// ============================== ÇIKTI ================================
module assembly() {
    color("ivory") base();
    color("silver") translate([0,0,base_H]) pan_ring();
    translate([-sv_shaft_off, 0, base_H - sv_tab_z]) servo_model();
    rotate(PAN_ANGLE) translate([0,0,disc_z0]) {
        color("lightsteelblue") turntable();
        translate([yoke_x_out + sv_tab_z + sv_tab_t, 0, tilt_axis_h - sv_shaft_off])
            rotate([0,-90,0]) servo_model();
        translate([0,0,tilt_axis_h]) rotate([TILT_ANGLE,0,0]) {
            color("white") head();
            color("gray") translate([0, head_D/2 - 2.4 + 0.01, 0]) head_back();
            translate([0, -head_D/2, cam_z]) rotate([90,0,0]) {
                color("dimgray") shutter_frame();
                color("black") translate([SHUTTER_OPEN ? -(sf_L/2 - 3 - sh_W/2) : 0, 0, sf_back + 0.2]) shutter();
            }
        }
    }
}

if (PART == "assembly")  assembly();
if (PART == "base")      rotate([180,0,0]) base();   // üst yüz yatağa (destek gerekmez)
if (PART == "pan_ring")  pan_ring();
if (PART == "shutter_frame") shutter_frame();
if (PART == "bottom")    bottom();
if (PART == "turntable") turntable();
if (PART == "head")      rotate([90,0,0]) head();        // ön yüz yatağa
if (PART == "head_back") rotate([-90,0,0]) head_back();
if (PART == "shutter")   shutter();
