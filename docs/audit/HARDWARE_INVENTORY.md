# HARDWARE_INVENTORY.md — Donanım Envanteri

> **Kaynak notu:** Kart özellikleri üreticilerin yayımladığı genel bilgilere dayanır. "✅ Fiziksel doğrulama" sütunundaki hiçbir madde henüz **gerçek donanım üzerinde test edilmedi**. Orijinal KIRA BOM'u (R02) okunamadı.

## 1. Kullanıcının elindeki donanım

| # | Parça | Temel özellikler | KIRA'daki rolü | Fiziksel doğrulama |
|---|---|---|---|---|
| 1 | **Seeed XIAO ESP32-S3 Sense** ("v24" etiketi — anlamı doğrulanacak) | ESP32-S3R8, çift çekirdek 240 MHz, 8 MB PSRAM (OPI), 8 MB flash, Wi-Fi 2.4 GHz + BLE 5, USB-C. Sense genişleme kartı: kamera konektörü, **dahili PDM dijital mikrofon**, microSD yuvası | Robot denetleyicisi: kamera, mikrofon, ekran, ses, Wi-Fi | ⬜ |
| 2 | **Kamera modülü** | Sense kitiyle gelen DVP kamera: eski kitlerde **OV2640** (2 MP), yeni kitlerde **OV3660** (3 MP). Hangisi olduğu **modül etiketinden doğrulanmalı** | Görüntü | ⬜ |
| 3 | **SH1107 OLED** | Tek renk OLED sürücüsü. Yaygın modüller: 1.5" 128×128 veya 1.3" 64×128. Arayüz **I2C veya SPI** olabilir — modül başlıklarından doğrulanmalı | Yüz ifadeleri, durum | ⬜ |
| 4 | **MAX98357A** | I2S girişli mono D sınıfı amplifikatör. Pinler: `LRC, BCLK, DIN, GAIN, SD, GND, Vin`. Vin 2.5–5.5 V | Ses çıkışı | ⬜ |
| 5 | **Hoparlör 8 Ω 0.5 W** | — | Ses | ⬜ |
| 6 | **Sarı mini breadboard** (lehimsiz) | Muhtemelen 170 noktalı tip: güç rayı yok, 17 sütun × 2 yarı × 5 delik. **Tipi doğrulanmalı** | 5V/GND dağıtımı, R02'deki 8 numaralı parçanın yerine | ⬜ |
| 7 | Jumper kablolar | — | Bağlantılar | ⬜ |
| 8 | **LILYGO T-Display-S3** | ESP32-S3R8, 16 MB flash, 8 MB PSRAM, 1.9" ST7789 170×320 IPS (8-bit paralel), 2 buton, pil konektörü | **İsteğe bağlı** — bkz. §3 | ⬜ |

## 2. Mikrofon durumu (gizlenmeyen gerçek)

- XIAO ESP32-S3 **Sense** genişleme kartında **dahili bir PDM mikrofon vardır** (Seeed dokümanlarına göre veri GPIO41, saat GPIO42).
- Yani **Sense kartı takılıysa** ayrı mikrofon satın almak gerekmez.
- **Ancak:** mikrofonun gövde içinde ses alabilmesi için gövdede bir delik/kanal olmalı ve hoparlörden yeterince uzak olmalı (yankı). Orijinal gövdede bunun olup olmadığı STL'ler görülmeden bilinemez.
- **Doğrulama testi:** firmware'de PDM kayıt → seviye ölçümü (Phase 1).
- Sense kartı yoksa veya mikrofon arızalıysa: KIRA **mikrofon yok** durumuna geçmeli ve bunu dürüstçe söylemeli; alternatif olarak Windows PC mikrofonu kullanılabilir.

## 3. LILYGO T-Display-S3 değerlendirmesi

İlk sürümde **zorunlu değil**. Seçenekler:

| Seçenek | Artı | Eksi | Öneri |
|---|---|---|---|
| A. Ayrı **durum paneli** (Wi-Fi ile PC'ye bağlı, kamera önizleme küçük resmi, AI durumu, CPU/RAM) | Ana robota dokunmaz, bağımsız test edilir | Ek güç kablosu | ✅ **Phase 11 sonrası önerilen** |
| B. KIRA'nın ana ekranını değiştirmek | Renkli, daha büyük | Orijinal gövdeye sığmaz, tasarım bozulur | ❌ |
| C. İkinci denetleyici (servo/sensör kartı, Phase 12+) | XIAO'nun az GPIO'sunu rahatlatır | Kablolama/haberleşme karmaşıklığı | Gelecekte değerlendir |

## 4. Eksik / önerilen donanım

**Zorunlu satın alma yok** ilkesi korunmuştur. Aşağıdakiler kontrol edilmeli:

| Parça | Durum | Neden |
|---|---|---|
| **Veri destekli** USB-C kablosu | Gerekli (muhtemelen mevcut) | Firmware yükleme |
| 5 V ≥ 2 A USB güç kaynağı | Gerekli | Kamera + Wi-Fi + amplifikatör tepe akımı; zayıf kaynakta brownout/reset riski |
| Multimetre | **Şiddetle önerilir** | Breadboard iç bağlantılarını ve 5V/GND'yi doğrulamak için |
| Kamera FPC uzatma kablosu | **Sadece** kamera Sense kartından uzağa taşınacaksa | Sense kamerası kısa bir FPC ile karta bağlıdır; sökülebilir yuva tasarımı buna göre yapılacak (bkz. CAMERA_DESIGN.md) |
| Kamera "aktif" LED'i + direnç | İsteğe bağlı | XIAO'nun kart üstü LED'i (GPIO21) gövde içinde görünmez. **İlk sürümde OLED üzerinde kamera simgesi** kullanılacak → satın alma gerekmez |
| microSD kart | İsteğe bağlı | Varsayılan olarak video kaydı yapılmayacağı için gerekmiyor |
| Küçük alüminyum soğutucu | İsteğe bağlı | Sürekli kamera + Wi-Fi'da XIAO ısınır (bkz. RISK_REGISTER) |

## 5. Güç bütçesi (tahmini, ölçülecek)

| Tüketici | Tipik | Tepe |
|---|---|---|
| ESP32-S3 + Wi-Fi yayın | ~100–250 mA | ~350 mA |
| Kamera | ~50–100 mA | — |
| SH1107 OLED | ~10–30 mA | — |
| MAX98357A + 8 Ω hoparlör (5 V) | düşük | ses tepe noktalarında yüzlerce mA |
| **Toplam** | ~0.3–0.5 A | **~0.8–1 A** |

Değerler **ölçülmemiştir**; Phase 2'de USB ampermetre ile ölçülecek.
