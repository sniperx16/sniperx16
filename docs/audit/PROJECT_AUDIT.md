# PROJECT_AUDIT.md — KIRA AI PRO · Phase 0 Proje Denetimi

**Tarih:** 2026-11-12  
**Dal:** `claude/kira-ai-pro-development-lyccwa`  
**Durum:** ⚠️ Denetim **kaynak dosyalar olmadan** yapıldı. Aşağıdaki bulgular bu yüzden kısmidir.

---

## 1. Kritik bulgu: Depoda KIRA dosyası yok

| Kontrol | Sonuç |
|---|---|
| `sniperx16/sniperx16` deposu | **Boş.** Hiç commit, hiç dosya yok (yerelde ve `origin`'de). |
| Orijinal firmware (`.ino` / ESP-IDF / PlatformIO) | **Yok** |
| STL / 3MF gövde dosyaları | **Yok** |
| R02 montaj kılavuzu / bağlantı şeması (PDF) | **Yok** |
| Windows tarafı yazılım (varsa) | **Yok** |
| Oturumun erişebildiği diğer depolar | Yok (yalnızca `sniperx16/sniperx16`) |
| Web erişimi (makerworld.com, yankodesign.com, hypebeast.com) | **Ağ politikası engelliyor** (DNS çözümü reddedildi) |

**Sonuç:** "Mevcut kaynak kodları, firmware, 3D modeller ve orijinal tasarımı incele" adımı **yapılamadı**. Bu raporlardaki hiçbir pin numarası orijinal KIRA şemasından alınmamıştır.

## 2. Dış kaynaklardan doğrulanabilen bilgiler (yalnızca arama özetleri)

Web araması (sayfa içerikleri okunamadı, yalnızca sonuç özetleri) şunları gösteriyor:

- KIRA, Alisher Ashimov tarafından tasarlanmış, **1984 Macintosh replikası** 3D baskı gövdeli, açık kaynaklı bir AI asistanı.
- Ana kart: **Seeed XIAO ESP32-S3 Sense**.
- Uyandırma kelimesi: **"Hey Kira"**.
- Ekran: **SH1107 OLED** (~1.5"), animasyonlu yüz ifadeleri.
- Hoparlör + amplifikatör (yayınlarda amplifikatör modeli **doğrulanamadı**; kullanıcı MAX98357A olarak belirtiyor).
- MakerWorld kayıt numarası olabilecek ID: `2550437` — **doğrulanmadı**.

**Bilinmeyenler:** firmware dili/çatısı, bulut AI sağlayıcısı, sunucu (PC tarafı) olup olmadığı, kameranın orijinalde kullanılıp kullanılmadığı, mikrofonun onboard PDM mi harici mi olduğu, pin atamaları, gövdedeki parça numaraları (8 numaralı parça dahil).

## 3. Denetlenecek dosyalar için kontrol listesi (dosyalar geldiğinde)

### Firmware
- [ ] Çatı: Arduino / ESP-IDF / PlatformIO / xiaozhi-esp32 türevi mi?
- [ ] Kart tanımı ve PSRAM ayarı (OPI PSRAM açık mı?)
- [ ] Wi-Fi yapılandırması — SSID/şifre kaynak koda gömülü mü? (güvenlik)
- [ ] API anahtarı kaynak kodda mı? (güvenlik — varsa hemen iptal edilmeli)
- [ ] I2S pinleri (MAX98357A: BCLK, LRC/WS, DIN)
- [ ] I2C/SPI pinleri (SH1107)
- [ ] Mikrofon: PDM GPIO41/42 mi, harici I2S mi?
- [ ] Kamera başlatma kodu var mı?
- [ ] Wake word motoru (ESP-SR WakeNet? Edge Impulse? bulut?)
- [ ] AI akışı: ESP32 doğrudan buluta mı bağlanıyor, PC'ye mi?
- [ ] OTA desteği

### 3D modeller
- [ ] Parça listesi ve numaralandırma (8 numaralı parçanın ne olduğu)
- [ ] Ön panelde kamera için yer var mı?
- [ ] Ekran penceresi ölçüleri
- [ ] Hoparlör ızgarası ve mikrofon deliği
- [ ] Vida/tutturma tipi

### R02 PDF
- [ ] Kablo renkleri ↔ pinler tablosu
- [ ] Güç dağıtımı (5V mı 3V3 mü?)
- [ ] Montaj sırası

## 4. Bu aşamada yapılanlar

- Yalnızca `docs/audit/` altında rapor dosyaları ve `CHANGELOG.md` oluşturuldu.
- **Hiçbir firmware, STL veya 3MF dosyası değiştirilmedi** (zaten mevcut değiller).
- Hiçbir kod yazılmadı.

## 5. Devam etmek için gerekenler (kullanıcıdan)

1. **Orijinal KIRA paketini** (MakerWorld'den indirilen ZIP: firmware, STL/3MF, R02 PDF) depoya `original/` klasörü altında yükleyin — dokunulmadan referans olarak saklanacak.
   - Alternatif: ortamın ağ ayarlarında `makerworld.com` vb. alan adlarına izin verin (MakerWorld indirmeleri çoğunlukla giriş gerektirdiğinden dosya yüklemek daha güvenilir).
2. Elinizdeki **gerçek kartların fotoğrafları** (XIAO ön/arka, Sense genişleme kartı, kamera modülü etiketi, SH1107 modülünün pin başlıkları, MAX98357A, breadboard alt yüzü mümkünse).
3. Şu anki **kablolamanın fotoğrafı** (varsa).
4. SH1107 modülünüzün pin dizilimi: `VCC GND SCL SDA` (I2C) mi, `GND VCC SCK SDA RES DC CS` (SPI) mi?
5. Kamera modülü etiketi: **OV2640** mı **OV3660** mı?
