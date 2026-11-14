// =====================================================================
// DURUM: Kullanıcı bu yönden vazgeçti (2026-11-14). Yarım taslak; yalnızca arşiv amaçlı saklanıyor.
// KIRA Gezgin — masada gezen, kendi beyni olan robot (özgün tasarım, v0.1)
//
// Parçalar:
//   openscad -D 'PART="chassis"'       -o chassis.stl       kira_gezgin.scad
//   openscad -D 'PART="deck"'          -o deck.stl          kira_gezgin.scad
//   openscad -D 'PART="shell"'         -o shell.stl         kira_gezgin.scad
//   openscad -D 'PART="neck"'          -o neck.stl          kira_gezgin.scad
//   openscad -D 'PART="head"'          -o head.stl          kira_gezgin.scad
//   openscad -D 'PART="head_back"'     -o head_back.stl     kira_gezgin.scad
//   openscad -D 'PART="shutter_frame"' -o shutter_frame.stl kira_gezgin.scad
//   openscad -D 'PART="shutter"'       -o shutter.stl       kira_gezgin.scad
//   openscad -D 'PART="wheel"'         -o wheel.stl         kira_gezgin.scad   (x2)
//
// "ÖLÇ" yazan değerler tipik ölçülerdir; baskıdan önce gerçek parçadan ölçün.
// Eksenler: -Y = ön, +Z = yukarı. Tekerlek aksı Y=0'da → robot yerinde döner.
// =====================================================================

PART = "assembly";
TILT_ANGLE = 0;          // önizleme: baş yukarı/aşağı (+/-25)
SHUTTER_OPEN = true;
SHOW_ELECTRONICS = true;

$fn = 64;
tol = 0.3;
wall = 2.4;

// ---------- Satın alınacak/elde olan parçalar (ÖLÇ) ----------
wheel_d = 44;  wheel_w = 14;         // basılı jant + O-ring lastik
oring_cs = 2.5;                       // O-ring kesit çapı (lastik)
n20_w = 12; n20_h = 10; n20_len = 34; // enkoderli N20 motor (gövde+redüktör+enkoder)
n20_shaft_d = 3; n20_shaft_flat = 2.5; n20_shaft_len = 9;
bat_L = 77; bat_W = 41; bat_H = 21;   // 2x18650 yan yana pil yuvası
caster_h = 13.5;                      // bilyalı sarhoş teker toplam yüksekliği (araya pul ile ayarlanır)
caster_hole_pitch = 20;               // sarhoş teker vida delik aralığı
bat_y0 = 25;                          // pil yuvası başlangıcı (tekerlek yuvalarının arkası)
pi_L = 85; pi_W = 56; pi_hole_in = 3.5; pi_hole_dx = 58; pi_hole_dy = 49; pi_stack_h = 27; // Pi 5 + aktif soğutucu
td_L = 62; td_W = 26;                 // LILYGO T-Display-S3
lcd_win_L = 44; lcd_win_W = 24; lcd_off_x = 3;
cam_lens_d = 8.5; cam_mod = 8.6;      // XIAO Sense kamera
spk_d = 28;                           // hoparlör
oled_win_w = 28; oled_win_h = 28;     // SH1107 (arka durum ekranı)

// Servo SG90/MG90S (ÖLÇ)
sv_L = 22.8; sv_W = 12.2; sv_H = 22.7; sv_tab_z = 15.9; sv_tab_t = 2.5;
sv_tab_L = 32.4; sv_hole_pitch = 27.6; sv_shaft_off = 5.4;
horn_d = 21; horn_t = 2.2;

// ---------- Ana ölçüler ----------
body_L = 146; body_W = 110; body_r = 16;
axle_z = wheel_d/2;                       // aks yüksekliği
plate_t = 3;
plate_top = axle_z - n20_h/2;              // motor şasiye oturur
plate_bot = plate_top - plate_t;           // zemin boşluğu (= sarhoş teker yüksekliği)
wheel_x = body_W/2 - wall - 2.5 - wheel_w/2; // tekerlek merkezi (gövde içinde)
pillar_h = bat_H + 5;                      // pil üstünde güverte
deck_t = 3;
deck_z = plate_top + pillar_h;             // güverte alt yüzü
shell_top = deck_z + deck_t + 5 + pi_stack_h + 4;  // kabuk üst yüzü
pillar_pos = [for (sx=[-1,1], sy=[-1,1]) [sx*47, sy*(body_L/2-wall-16)]];

head_W = 70; head_D = 40; head_H = 50; head_r = 9;
head_y = -18;                              // baş öne yakın (arka kısım Pi soğutması için açık)
yoke_t = 4; yoke_gap = 4;
tilt_h = ceil(sqrt(pow(head_D/2,2)+pow(head_H/2,2))) + 4;  // boyun tabanından eğilme eksenine
neck_t = 4;

// ---------------------------------------------------------------------
module rrect(w, d, h, r) {
    hull() for (x=[-1,1], y=[-1,1]) translate([x*(w/2-r), y*(d/2-r), 0]) cylinder(r=r, h=h);
}
module rbox_y(w, d, h, r) {
    hull() for (x=[-1,1], z=[-1,1])
        translate([x*(w/2-r), d/2, z*(h/2-r)]) rotate([90,0,0]) cylinder(r=r, h=d);
}

// ============================== ŞASİ =================================
cliff_pos = [for (sx=[-1,1], sy=[-1,1]) [sx*32, sy*(body_L/2-8)]];

module chassis() {
    difference() {
        union() {
            translate([0,0,plate_bot]) rrect(body_W-2*wall-2*tol, body_L-2*wall-2*tol, plate_t, body_r-wall);
            // motor yatakları (N20 dikdörtgen gövde)
            for (s=[-1,1]) translate([s*(wheel_x - wheel_w/2 - 1.5 - n20_len/2), 0, plate_top])
                difference() {
                    translate([-n20_len/2, -(n20_w/2+2.5), 0]) cube([n20_len, n20_w+5, n20_h*0.7]);
                    translate([-n20_len/2-1, -(n20_w+tol*2)/2, 0.01]) cube([n20_len+2, n20_w+tol*2, n20_h]);
                }
            // pil yuvası duvarları (arka)
            translate([0, bat_y0 + bat_W/2, plate_top]) difference() {   // tekerlek yuvalarının arkasında
                translate([-(bat_L+6)/2, -(bat_W+6)/2, 0]) cube([bat_L+6, bat_W+6, 8]);
                translate([-(bat_L+tol*2)/2, -(bat_W+tol*2)/2, -1]) cube([bat_L+tol*2, bat_W+tol*2, 10]);
            }
            // güverte kolonları
            for (p=pillar_pos) translate([p[0], p[1], plate_top]) difference() {
                cylinder(d=8, h=pillar_h); cylinder(d=2.6, h=pillar_h+1);
            }
        }
        // tekerlek yuvaları
        for (s=[-1,1]) translate([s*wheel_x - (wheel_w+4)/2, -(wheel_d+6)/2, plate_bot-1])
            cube([wheel_w+4, wheel_d+6, plate_t+2]);
        // motor kelepçe (kablo bağı) yarıkları
        for (s=[-1,1], dx=[-9,9]) translate([s*(wheel_x - wheel_w/2 - 1.5 - n20_len/2) + dx, 0, plate_bot-1])
            for (sy=[-1,1]) translate([-1.5, sy*(n20_w/2+4)-1.5, 0]) cube([3, 3, plate_t+2]);
        // sarhoş tekerler (ön/arka)
        // (havşa üstten: arka teker pil altında kalır, somun alta gelir)
        for (sy=[-1,1], dx=[-1,1]) translate([dx*caster_hole_pitch/2, sy*(body_L/2-12), plate_bot-1]) {
            cylinder(d=3.2, h=plate_t+2);
            translate([0,0,plate_t+1-1.6]) cylinder(d1=3.2, d2=6.4, h=1.61);
        }
        // masa kenarı sensörleri: 2x M2 + kablo deliği
        for (c=cliff_pos) translate([c[0], c[1], plate_bot-1]) {
            for (dx=[-1,1]) translate([dx*9, 0, 0]) cylinder(d=2.2, h=plate_t+2, $fn=16);
            translate([sign(c[0])*14, 0, 0]) cylinder(d=6, h=plate_t+2);   // kablo dışa doğru
        }
        // kablo/hava delikleri (ön elektronik bölgesi)
        for (i=[-2:2]) translate([i*12, -30, plate_bot-1]) cylinder(d=6, h=plate_t+2);
    }
}

// ============================= GÜVERTE ===============================
pi_y = 6;     // Pi merkezi (Y)

module deck() {
    difference() {
        translate([0,0,deck_z]) rrect(body_W-2*wall-2*tol, body_L-2*wall-2*tol, deck_t, body_r-wall);
        for (p=pillar_pos) translate([p[0], p[1], deck_z-1]) cylinder(d=3.4, h=deck_t+2);
        // ön kablo geçişi (baş kabloları, motor sürücü)
        translate([-20, -body_L/2+wall+8, deck_z-1]) cube([40, 18, deck_t+2]);
        // yan kablo geçişleri
        for (s=[-1,1]) translate([s*(body_W/2-wall-16)-6, -10, deck_z-1]) cube([12, 20, deck_t+2]);
    }
    // Pi 5 ayakları (M2.5 → 2.2 delik)
    for (dx=[0, pi_hole_dx], dy=[0, pi_hole_dy])
        translate([-pi_L/2 + pi_hole_in + dx, pi_y - pi_W/2 + pi_hole_in + dy, deck_z + deck_t - 0.01])
            difference() { cylinder(d=6, h=5); cylinder(d=2.2, h=6); }
}

// =============================== KABUK ===============================
module shell() {
    h = shell_top - plate_bot;
    difference() {
        union() {
            difference() {
                translate([0,0,plate_bot]) rrect(body_W, body_L, h, body_r);
                translate([0,0,plate_bot-0.01]) rrect(body_W-2*wall, body_L-2*wall, h-wall+0.01, body_r-wall);
            }
            // şasiye vidalama kulakları (iç, alt)
            for (sx=[-1,1], sy=[-1,1]) translate([sx*(body_W/2-wall-3), sy*(body_L/2-wall-26), plate_top])
                difference() { translate([-3,-4,0]) cube([3+0.01, 8, 6]); }
            // hoparlör halkası (arka iç)
            translate([24, body_L/2-wall, plate_top + 32]) rotate([90,0,0])
                difference() { cylinder(d=spk_d+4, h=4); translate([0,0,-1]) cylinder(d=spk_d+tol*2, h=6); }
        }
        // tekerlek pencereleri (yan; tekerlek dışarıdan görünür, kolay temizlik)
        for (s=[-1,1]) translate([s*body_W/2, 0, plate_bot-1]) hull() {
            translate([0, 0, 0]) cube([wall*3, wheel_d+6, 2], center=true);
            translate([0,0,axle_z - plate_bot + 1]) rotate([0,90,0]) cylinder(d=wheel_d+6, h=wall*3, center=true);
        }
        // ön engel sensörü penceresi (VL53L1X)
        translate([0, -body_L/2, plate_top + 10]) cube([14, wall*3, 10], center=true);
        // arka: hoparlör ızgarası
        translate([24, body_L/2+1, plate_top + 32]) rotate([90,0,0])
            for (i=[-2:2], j=[-2:2]) if (i*i+j*j <= 5) translate([i*4.5, j*4.5, 0]) cylinder(d=2.6, h=wall+2, $fn=16);
        // arka: durum ekranı (SH1107)
        translate([-24, body_L/2, plate_top + 34]) cube([oled_win_w, wall*3, oled_win_h], center=true);
        // arka: USB-C şarj + güç anahtarı
        translate([24, body_L/2, plate_top + 9]) cube([12, wall*3, 7], center=true);
        translate([-24, body_L/2, plate_top + 9]) cube([13, wall*3, 8.5], center=true);
        // yan havalandırma
        for (s=[-1,1], i=[0:4]) translate([s*body_W/2, 22 + i*7, shell_top - 22]) cube([wall*3, 3, 22], center=true);
        // üst arka havalandırma (Pi fanı)
        for (i=[0:5]) translate([-27, 18 + i*6, shell_top - wall - 1]) cube([54, 3, wall+2]);
        // boyun vida delikleri + kablo deliği
        for (x=[-1,1], y=[-1,1]) translate([x*30, head_y + y*7, shell_top - wall - 1]) cylinder(d=3.2, h=wall+2);
        translate([0, head_y + 20, shell_top - wall - 1]) cylinder(d=14, h=wall+2);
        // şasi kulak vidaları (yandan M3)
        for (sx=[-1,1], sy=[-1,1]) translate([sx*body_W/2, sy*(body_L/2-wall-26), plate_top+3])
            rotate([0,90,0]) cylinder(d=3.2, h=wall*4, center=true);
    }
}

// ============================ BOYUN (ÇATAL) ===========================
yoke_x_in = head_W/2 + yoke_gap;
yoke_x_out = yoke_x_in + yoke_t;

module neck() {     // kabuk üstüne 4x M3 ile vidalanır; z=0 kabuk üstü
    difference() {
        union() {
            translate([-yoke_x_out, -11, 0]) cube([2*yoke_x_out, 22, neck_t]);
            for (s=[-1,1]) translate([s>0 ? yoke_x_in : -yoke_x_out, -11, 0]) hull() {
                cube([yoke_t, 22, neck_t]);
                translate([0, 11, tilt_h]) rotate([0,90,0]) cylinder(d=20, h=yoke_t);
            }
        }
        for (x=[-1,1], y=[-1,1]) translate([x*30, y*7, -1]) cylinder(d=3.4, h=neck_t+2);
        // sol: M3 mil
        translate([-yoke_x_out-1, 0, tilt_h]) rotate([0,90,0]) cylinder(d=3.4, h=yoke_t+2);
        // sağ: tilt servo (gövdesi dışarıda, mili içeri bakar)
        translate([yoke_x_out + sv_tab_z + sv_tab_t, 0, tilt_h - sv_shaft_off]) rotate([0,-90,0]) {
            translate([-(sv_L+tol*2)/2, -(sv_W+tol*2)/2, sv_tab_z+sv_tab_t-0.01]) cube([sv_L+tol*2, sv_W+tol*2, 10]);
            for (x=[-1,1]) translate([x*sv_hole_pitch/2, 0, sv_tab_z]) cylinder(d=2.0, h=12);
        }
    }
}

// ================================ BAŞ ================================
cam_z = head_H/2 - 11;
lcd_z = -7;
sf_L = 50; sf_H = 20; sf_back = 1.2; sf_slot = 1.8; sf_lip = 1.2; sf_lip_w = 2.5;
sh_W = 16; sh_T = 1.4; sh_H = sf_H - 6 - tol*2;

module head() {
    difference() {
        union() {
            difference() {
                rbox_y(head_W, head_D, head_H, head_r);
                translate([0, wall, 0]) rbox_y(head_W-2*wall, head_D, head_H-2*wall, head_r-wall);
            }
            for (x=[-1,1], z=[-1,1]) translate([x*(head_W/2-wall-3.5), head_D/2, z*(head_H/2-wall-3.5)])
                rotate([90,0,0]) difference() { cylinder(d=7, h=14); cylinder(d=2.2, h=10); }
            for (s=[-1,1]) translate([s*(head_W/2-wall), 0, 0]) rotate([0, 90*s, 0]) cylinder(d=24, h=wall+0.01);
            translate([0, -head_D/2+wall, lcd_z]) difference() {
                translate([-(td_L+6)/2, 0, -(td_W+6)/2]) cube([td_L+6, 3, td_W+6]);
                translate([-(td_L+tol*2)/2, -1, -(td_W+tol*2)/2]) cube([td_L+tol*2, 5, td_W+tol*2]);
            }
            translate([0, -head_D/2+wall, cam_z]) difference() {
                translate([-(cam_mod+5)/2, 0, -(cam_mod+5)/2]) cube([cam_mod+5, 3, cam_mod+5]);
                translate([-(cam_mod+tol*2)/2, -1, -(cam_mod+tol*2)/2]) cube([cam_mod+tol*2, 5, cam_mod+tol*2]);
            }
        }
        translate([lcd_off_x - lcd_win_L/2, -head_D/2-1, lcd_z - lcd_win_W/2]) cube([lcd_win_L, wall+2, lcd_win_W]);
        translate([0, -head_D/2-1, cam_z]) rotate([-90,0,0]) cylinder(d=cam_lens_d+tol*2, h=wall+6);
        for (x=[-1,1]) translate([x*(sf_L/2-3), -head_D/2-1, cam_z]) rotate([-90,0,0]) cylinder(d=2.0, h=wall+2, $fn=16);
        for (i=[-1:1]) translate([head_W/2-wall-3, -head_D/2-1, cam_z + i*2.6]) rotate([-90,0,0]) cylinder(d=1.3, h=wall+2, $fn=12);
        translate([head_W/2+0.01, 0, 0]) rotate([0,-90,0]) { cylinder(d=horn_d+tol*2, h=horn_t); cylinder(d=2.2, h=10); }
        translate([-head_W/2-1, 0, 0]) rotate([0,90,0]) cylinder(d=2.6, h=12);
    }
}

module head_back() {
    difference() {
        rbox_y(head_W-2*wall-tol*2, 2.4, head_H-2*wall-tol*2, head_r-wall);
        for (x=[-1,1], z=[-1,1]) translate([x*(head_W/2-wall-3.5), 3, z*(head_H/2-wall-3.5)]) rotate([90,0,0]) cylinder(d=2.6, h=5);
        for (i=[-3:3]) translate([i*6, -1, 5]) cube([2.5, 5, 14], center=true);
        translate([0, -1, -(head_H/2-wall-9)]) rotate([-90,0,0]) cylinder(d=12, h=5);
    }
}

module shutter_frame() {
    difference() {
        translate([-sf_L/2, -sf_H/2, 0]) cube([sf_L, sf_H, sf_back + sf_slot + sf_lip]);
        translate([-sf_L/2 + 3, -(sf_H/2 - 3), sf_back]) cube([sf_L, sf_H - 6, sf_slot]);
        translate([-sf_L/2 + 3, -(sf_H/2 - 3 - sf_lip_w), sf_back]) cube([sf_L, sf_H - 6 - 2*sf_lip_w, 10]);
        translate([0, 0, -1]) cylinder(d=cam_lens_d + 1, h=5);
        for (x=[-1,1]) translate([x*(sf_L/2-3), 0, -1]) cylinder(d=2.4, h=10, $fn=16);
    }
}
module shutter() {
    translate([-sh_W/2, -sh_H/2, 0]) cube([sh_W, sh_H, sh_T]);
    translate([-1.5, -3, sh_T]) cube([3, 6, sf_lip + 1.5]);
}

// ============================== TEKERLEK =============================
module wheel() {     // z=0 dış yüz; O-ring lastik oluğu
    difference() {
        union() {
            cylinder(d=wheel_d - oring_cs, h=wheel_w);
            cylinder(d=10, h=wheel_w + 2);              // göbek
        }
        // iki O-ring oluğu
        for (z=[wheel_w*0.3, wheel_w*0.7]) translate([0,0,z])
            rotate_extrude() translate([(wheel_d - oring_cs)/2, 0]) circle(d=oring_cs*1.05, $fn=24);
        // D milli delik
        translate([0,0,-1]) intersection() {
            cylinder(d=n20_shaft_d + tol, h=wheel_w + 4, $fn=32);
            translate([-(n20_shaft_d+1)/2, -(n20_shaft_d+1)/2, 0]) cube([n20_shaft_flat + tol/2 + (n20_shaft_d+1)/2 - n20_shaft_d/2, n20_shaft_d+1, wheel_w + 4]);
        }
        // hafifletme
        for (a=[0:60:300]) rotate(a) translate([12, 0, -1]) cylinder(d=7, h=wheel_w+2);
    }
}

// ============================== ÖNİZLEME =============================
module electronics_preview() {
    color("green", 0.7) translate([-pi_L/2, pi_y - pi_W/2, deck_z + deck_t + 5]) cube([pi_L, pi_W, pi_stack_h - 5]);
    color("royalblue", 0.8) translate([-bat_L/2, bat_y0, plate_top]) cube([bat_L, bat_W, bat_H]);
    for (s=[-1,1]) color("silver") translate([s*(wheel_x - wheel_w/2 - 1.5 - n20_len/2) - n20_len/2, -n20_w/2, plate_top]) cube([n20_len, n20_w, n20_h]);
    for (sy=[-1,1]) color("gray") translate([0, sy*(body_L/2-12), 0]) cylinder(d=12, h=plate_bot);
}

module assembly() {
    color("tan") chassis();
    if (SHOW_ELECTRONICS) electronics_preview();
    color("lightgray") deck();
    for (s=[-1,1]) color("dimgray") translate([s*wheel_x + (s>0 ? -wheel_w/2 : wheel_w/2), 0, axle_z])
        rotate([0, s>0 ? 90 : -90, 0]) wheel();
    color("white", 0.55) shell();
    translate([0, head_y, shell_top]) {
        color("lightsteelblue") neck();
        translate([yoke_x_out + sv_tab_z + sv_tab_t, 0, tilt_h - sv_shaft_off]) rotate([0,-90,0])
            color("dimgray") { translate([-sv_L/2,-sv_W/2,0]) cube([sv_L, sv_W, sv_H]); }
        translate([0,0,tilt_h]) rotate([TILT_ANGLE,0,0]) {
            color("white") head();
            color("gray") translate([0, head_D/2 - 2.4 + 0.01, 0]) head_back();
            translate([0, -head_D/2, cam_z]) rotate([90,0,0]) {
                color("dimgray") shutter_frame();
                color("black") translate([SHUTTER_OPEN ? -(sf_L/2 - 3 - sh_W/2) : 0, 0, sf_back + 0.2]) shutter();
            }
        }
    }
}

if (PART == "assembly")      assembly();
if (PART == "chassis")       translate([0,0,-plate_bot]) chassis();
if (PART == "deck")          translate([0,0,-deck_z]) deck();
if (PART == "shell")         rotate([180,0,0]) translate([0,0,-shell_top]) shell();
if (PART == "neck")          neck();
if (PART == "head")          rotate([90,0,0]) head();
if (PART == "head_back")     rotate([-90,0,0]) head_back();
if (PART == "shutter_frame") shutter_frame();
if (PART == "shutter")       shutter();
if (PART == "wheel")         wheel();
