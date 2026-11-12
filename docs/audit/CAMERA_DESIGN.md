# CAMERA_DESIGN.md — Kamera Sistemi ve Gövde Tasarımı

> Orijinal STL/3MF dosyaları ve kamera modülü ölçüleri henüz elimizde değil. Bu belge **tasarım gereksinimlerini ve ölçüm planını** tanımlar; nihai CAD ölçüleri gerçek modülden alınacak.

## 1. Donanım gerçekleri

- Kamera, XIAO **Sense** genişleme kartındaki B2B konektöre kısa bir FPC şerit kablo ile bağlıdır.
- Sensör: OV2640 veya OV3660 (etiketten doğrulanacak).
- Kamera pinleri dış GPIO'ları tüketmez (bkz. PIN_CONNECTION_MAP §2).
- 8 MB PSRAM → JPEG kare tamponları PSRAM'da tutulabilir (2 tampon).

## 2. Akış mimarisi (ESP32 → Windows)

```
[Kamera] → ESP32-S3 (donanım JPEG) ──Wi-Fi──► Windows "vision" servisi
                 │  MJPEG/HTTP veya WebSocket       │
                 │  + kontrol kanalı (aç/kapa,      ├─ Hareket algılama (her kare, OpenCV)
                 │    çözünürlük, FPS)              ├─ İnsan/nesne algılama (YOLO-ONNX, 2–5 Hz)
                 ▼                                  ├─ QR (OpenCV) / OCR (istek üzerine)
            OLED'de "kamera aktif" simgesi          └─ Olay → Yerel VLM → (gerekirse) Bulut VLM
```

### 2.1 Varsayılan çözünürlük / FPS

| Profil | Çözünürlük | JPEG kalitesi | FPS | Kullanım |
|---|---|---|---|---|
| **Algılama (varsayılan)** | QVGA 320×240 | 12–15 | 5–10 | Sürekli hareket/insan algılama, düşük ısı |
| **Canlı izleme** | VGA 640×480 | 12 | 10–15 | Panelde canlı görüntü |
| **Detay karesi** | SVGA/UXGA (tek kare) | 10 | — | OCR, "bunu açıkla", bulut analizi |

Gerçek FPS, Wi-Fi sinyaline ve ısıya göre Phase 4'te **ölçülerek** belirlenecek. Firmware, PC'den gelen komutla profil değiştirecek.

### 2.2 Bulut kullanım kuralı
- Her kare buluta **gönderilmez**.
- Bulut yalnızca: kullanıcı sorusu ("ne görüyorsun?"), yerel modelin düşük güven skoru, kullanıcının açıkça istediği detaylı analiz.
- Buluta görüntü gönderimi, Güvenlik bölümünde **harici veri gönderimi** olarak sayılır ve ayarlardan kapatılabilir/onaya bağlanabilir.

## 3. Gizlilik tasarımı

| Katman | Uygulama |
|---|---|
| **Fiziksel kapak** | Lens önünde kayar kapak (3D baskı, sürtünmeli ray, iki konumda tık sesli detent) |
| **Yazılım kapatma** | Firmware'de kamera sürücüsü durdurulur (`deinit`), akış kapanır |
| **Gösterge** | OLED'de kalıcı kamera simgesi + panelde kırmızı "CANLI" etiketi. (İsteğe bağlı: harici LED — satın alma gerektirir, ilk sürümde yok) |
| **Kayıt yok** | Varsayılan olarak video/kare diske yazılmaz. Analiz RAM'de yapılır |
| **Sesli komut** | "KIRA kamerayı kapat" |
| **Yüz tanıma** | Kişi kimliği tanıma **varsayılan kapalı**; yalnızca "insan var/yok" algılanır |

## 4. 3D gövde geliştirmesi (Phase 3)

### 4.1 Kurallar
- Orijinal STL/3MF **değiştirilmez, silinmez.** `hardware/3d_models/original/` altında olduğu gibi saklanır.
- Yeni parçalar `hardware/camera_mount/` altında **ayrı dosya** olarak: `KIRA_front_camera_v1.3mf`, `KIRA_camera_cradle_v1.stl`, `KIRA_camera_shutter_v1.stl`.
- Mümkünse yalnızca **ön panel** yeni sürümü yapılır; gövdenin geri kalanı orijinal kalır.

### 4.2 Gereksinimler

| Özellik | Tasarım notu |
|---|---|
| Lens açıklığı | Lens çapı + ~0.6 mm tolerans, iç tarafta 45° pah (görüş açısı kesilmesin — OV2640 tipik ~66° FOV, geniş açılı lens varsa daha fazla) |
| Konum | Macintosh ön yüzünde, ekranın üstünde veya altında; ekran penceresi ve orijinal estetik bozulmadan |
| Sökülebilir yuva | Kamera modülünü saran "cradle", ön panele 2× M2 vida veya geçme klips ile |
| Kablo geçişi | FPC için ≥ 1 mm × (FPC genişliği + 1 mm) yarık, keskin kenar yok, min. bükülme yarıçapı korunur |
| Sabitleme | Cradle → ön panel: 2 nokta. Modül → cradle: hafif sıkı geçme + arkadan baskı dili |
| Fiziksel kapak | Ray içinde kayan kapak, dışarıdan parmakla itilebilir tırnak |
| Isı | Kamera ve XIAO çevresinde havalandırma yarıkları (sürekli akışta ısınma) |

### 4.3 Kritik soru: FPC uzunluğu
Sense kamerasının FPC kablosu kısadır. Kamera Sense kartının bulunduğu yerden uzağa taşınamıyorsa iki seçenek var:
1. **XIAO'yu ön panele yakın konumlandırmak** (tercih — satın alma gerektirmez), veya
2. Uzatma FPC kablosu (satın alma gerekir, sinyal bütünlüğü riski).

Karar, orijinal gövdede XIAO'nun yerini gösteren STL/R02 incelendikten sonra verilecek.

### 4.4 Gerçek modülden alınacak ölçüler (kumpas ile)

| Ölçü | Değer (mm) |
|---|---|
| Kamera modülü genişlik × yükseklik | ? |
| Lens tutucu dış çapı | ? |
| Lens tutucu yüksekliği (PCB'den) | ? |
| FPC genişliği / uzunluğu | ? |
| Sense kartı konektöründen lens merkezine mesafe | ? |
| Orijinal ön panel et kalınlığı | ? (STL'den) |

### 4.5 Baskı testi
Önce yalnızca lens/kapak bölgesini içeren küçük bir **test kuponu** basılacak (≈10 dk), uyum onaylanınca tam ön panel basılacak.
