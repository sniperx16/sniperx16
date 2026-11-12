# PIN_CONNECTION_MAP.md — Pin ve Bağlantı Haritası

> ## ⚠️ ÖNEMLİ — KABLOLARI HENÜZ DEĞİŞTİRMEYİN
> Orijinal **KIRA R02 bağlantı şeması okunamadı** (depoda yok, MakerWorld'e ağ erişimi yok).
> Bu nedenle **"hangi kablo hangi pine" doğrulaması YAPILAMADI.**
> Aşağıda üç ayrı bilgi türü bulunur ve birbirine karıştırılmamalıdır:
> 1. **[KART]** — kartın kendi sabit pinleri (Seeed resmi dokümanları; gerçek kart üzerinde doğrulanacak)
> 2. **[R02]** — orijinal şemadan doldurulacak boş tablo
> 3. **[ÖNERİ]** — yalnızca R02 bulunamazsa kullanılacak öneri. **Orijinal değildir.**

---

## 1. [KART] XIAO ESP32-S3 dış pinleri

USB-C üstte, bileşen yüzü size bakarken:

| Sol taraf | GPIO | Özel işlev | | Sağ taraf | GPIO | Özel işlev |
|---|---|---|---|---|---|---|
| D0 | GPIO1 | ADC | | **5V** | — | USB'den gelen VBUS |
| D1 | GPIO2 | ADC | | **GND** | — | |
| D2 | GPIO3 | ADC, *strapping* (JTAG seçimi) | | **3V3** | — | Kart regülatör çıkışı |
| D3 | GPIO4 | ADC | | D10 | GPIO9 | SPI MOSI — **microSD ile paylaşımlı** |
| D4 | GPIO5 | **I2C SDA** | | D9 | GPIO8 | SPI MISO — **microSD ile paylaşımlı** |
| D5 | GPIO6 | **I2C SCL** | | D8 | GPIO7 | SPI SCK — **microSD ile paylaşımlı** |
| D6 | GPIO43 | UART TX | | D7 | GPIO44 | UART RX |

## 2. [KART] Sense genişleme kartının iç kullanımı (dışarıdan bağlanmaz)

| İşlev | GPIO |
|---|---|
| Kamera XCLK | 10 |
| Kamera SIOD / SIOC (SCCB) | 40 / 39 |
| Kamera D0–D7 (Y2–Y9) | 15, 17, 18, 16, 14, 12, 11, 48 |
| Kamera VSYNC / HREF / PCLK | 38 / 47 / 13 |
| Kamera PWDN / RESET | yok (-1) |
| **PDM mikrofon** CLK / DATA | 42 / 41 |
| microSD CS | 21 (kart üstü kullanıcı LED'i ile aynı pin) |

**Sonuç:** Kamera ve mikrofon dış D0–D10 pinlerinden **hiçbirini tüketmez.** Dışarıda 11 GPIO kalır. microSD kullanılacaksa D8–D10 SPI hattı paylaşılır.

## 3. [KART] Modül pinleri

**MAX98357A:** `LRC (WS)`, `BCLK`, `DIN`, `GAIN`, `SD`, `GND`, `Vin`
- `GAIN` boşta → 9 dB. GND → 12 dB. Vin → 6 dB. 100 kΩ→GND → 15 dB. 100 kΩ→Vin → 3 dB.
- `SD` (shutdown/kanal seçimi) — modül üzerindeki dirençle varsayılan mono (L+R)/2. GND'ye çekilirse amfi kapanır.
- ⚠️ 0.5 W hoparlör için: **GAIN'i yükseltmeyin**, firmware'de ses seviyesi sınırı koyun (bkz. RISK_REGISTER R-04).

**SH1107 OLED:** Modül tipine bağlı:
- I2C: `VCC, GND, SCL, SDA` (adres genellikle 0x3C veya 0x3D)
- SPI: `GND, VCC, SCL/SCK, SDA/MOSI, RES, DC, CS`
→ Modülünüzün başlık etiketlerini bildirin.

---

## 4. [R02] Orijinal bağlantı tablosu — **R02 PDF'den doldurulacak**

| Kablo (renk) | Kaynak modül pini | XIAO pini (R02) | GPIO | Breadboard konumu | Gerçek kartta doğrulandı |
|---|---|---|---|---|---|
| ? | MAX98357A LRC | ? | ? | ? | ⬜ |
| ? | MAX98357A BCLK | ? | ? | ? | ⬜ |
| ? | MAX98357A DIN | ? | ? | ? | ⬜ |
| ? | MAX98357A Vin | ? (5V?) | — | ? | ⬜ |
| ? | MAX98357A GND | GND | — | ? | ⬜ |
| ? | MAX98357A GAIN / SD | ? | ? | ? | ⬜ |
| ? | SH1107 VCC | ? (3V3/5V?) | — | ? | ⬜ |
| ? | SH1107 GND | GND | — | ? | ⬜ |
| ? | SH1107 SCL/SCK | ? | ? | ? | ⬜ |
| ? | SH1107 SDA/MOSI | ? | ? | ? | ⬜ |
| ? | SH1107 RES/DC/CS (SPI ise) | ? | ? | ? | ⬜ |
| ? | Hoparlör + / − | MAX98357A `+` / `−` | — | doğrudan | ⬜ |

**Karşılaştırma kuralı:** R02 tablosu doldurulduktan sonra her satır, §1–§2'deki kart pinleriyle çakışma açısından kontrol edilecek, ardından firmware'deki `#define` değerleriyle **üçlü karşılaştırma** (R02 ↔ kart ↔ kod) yapılacak. Uyuşmazlık varsa **kod değil, önce rapor**.

---

## 5. Sarı mini breadboard — güç dağıtım planı

### 5.1 Doğrulanması gereken iç yapı

Yaygın 170 noktalı mini breadboard:
```
   1  2  3  4  5  ...  17
a  o  o  o  o  o       o   ┐
b  o  o  o  o  o       o   │ her SÜTUN dikey olarak bağlı (a–e)
c  o  o  o  o  o       o   │
d  o  o  o  o  o       o   │
e  o  o  o  o  o       o   ┘
   ======= orta kanal (bağlantı YOK) =======
f  o  o  o  o  o       o   ┐
...                        │ her SÜTUN dikey olarak bağlı (f–j)
j  o  o  o  o  o       o   ┘
```
- **Güç rayı yoktur.** Her sütunun yarısı = 5 delikli bir bağlantı noktası.
- ⚠️ Bazı mini breadboard'lar farklıdır. **Multimetre süreklilik testiyle** doğrulayın: `a1–e1` bağlı mı? `a1–a2` ayrı mı? `e1–f1` ayrı mı?

### 5.2 Önerilen dağıtım (R02 ile çelişirse R02 kazanır)

| Breadboard bölgesi | Ağ | Bağlananlar |
|---|---|---|
| Sütun 1 (a–e) | **5V** | XIAO 5V → MAX98357A Vin → (yedek) |
| Sütun 3 (a–e) | **GND** | XIAO GND → MAX98357A GND → SH1107 GND → (yedek) |
| Sütun 5 (a–e) | **3V3** | XIAO 3V3 → SH1107 VCC *(modül 3.3 V destekliyorsa; R02'ye bakılacak)* |
| Diğer sütunlar | Sinyal geçişi (gerekirse) | GPIO sinyalleri mümkünse **doğrudan** modüle gitsin |

- 5V ve GND sütunları arasında **en az bir boş sütun** bırakılır (kısa devre riskini azaltır).
- Breadboard'un R02'deki **8 numaralı parçanın** fiziksel yerine sığdığı STL ile doğrulanacak (170'lik tip yaklaşık 47 × 35 × 8.5 mm — ölçüp bildirin).

### 5.3 İlk güç verme protokolü (Phase 2)
1. Hiçbir modül takılı değilken: XIAO'yu USB'ye bağla, breadboard 5V sütunu ↔ GND sütunu gerilimini ölç (~4.8–5.1 V beklenir).
2. 3V3 sütununu ölç (~3.3 V).
3. 5V↔3V3 ve 5V↔GND arasında kısa devre olmadığını **güç kapalıyken** süreklilik testi ile doğrula.
4. Modülleri **tek tek** ekle, her seferinde akımı ve ısıyı kontrol et.

---

## 6. [ÖNERİ] R02 bulunamazsa kullanılacak atama — ORİJİNAL DEĞİLDİR

| Sinyal | XIAO | GPIO | Gerekçe |
|---|---|---|---|
| SH1107 SDA | D4 | 5 | Kartın varsayılan I2C pini |
| SH1107 SCL | D5 | 6 | Kartın varsayılan I2C pini |
| MAX98357A LRC | D0 | 1 | microSD SPI hattını boş bırakır |
| MAX98357A BCLK | D1 | 2 | 〃 |
| MAX98357A DIN | D2 | 3 | 〃 (strapping pini; çıkış olarak güvenli) |
| MAX98357A SD (amfi aç/kapa) | D3 | 4 | İsteğe bağlı: sessizken amfiyi kapatıp cızırtıyı azaltır |
| Boşta kalan | D6, D7, D8–D10 | 43, 44, 7–9 | Gelecek: servo, sensör, RGB LED, kamera LED'i |

Bu öneri **kullanıcı onayı olmadan uygulanmayacak.**
