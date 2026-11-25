# Ses uydusu – bağlantı şeması

## Parçalar (oda başına ≈ 700 TL)

| Parça | Not |
|---|---|
| ESP32-S3 DevKitC-1 **N16R8** | 16 MB flash + 8 MB PSRAM şart (N8R2 vb. **olmaz**) |
| INMP441 I2S mikrofon modülü | |
| MAX98357A I2S amfi modülü | |
| 3–5 W, 4–8 Ω küçük hoparlör | |
| Dişi–dişi jumper kablo (~12 adet) | |
| USB-C veri kablosu + 5 V / 2 A adaptör | Şarj kablosu değil, **veri** kablosu |

## Kablolar

### INMP441 mikrofon → ESP32-S3

| INMP441 | ESP32-S3 |
|---|---|
| VDD | **3V3** (5V'a bağlama!) |
| GND | GND |
| L/R | GND |
| WS | GPIO4 |
| SCK | GPIO5 |
| SD | GPIO6 |

### MAX98357A amfi → ESP32-S3

| MAX98357A | ESP32-S3 |
|---|---|
| VIN | **5V** (bazı kartlarda "5Vin" / "VBUS") |
| GND | GND |
| LRC | GPIO16 |
| BCLK | GPIO15 |
| DIN | GPIO7 |
| SD, GAIN | Boş bırak |

Hoparlörün iki kablosu amfinin **+** ve **−** vidalı uçlarına.

```
        INMP441                 ESP32-S3 N16R8                MAX98357A
      ┌─────────┐             ┌────────────────┐            ┌──────────┐
      │ VDD ────┼──── 3V3 ────┤                ├──── 5V ────┼─ VIN     │
      │ GND ────┼──── GND ────┤                ├──── GND ───┼─ GND     │
      │ L/R ────┼──── GND     │                │            │          │
      │ WS  ────┼─────────────┤ GPIO4   GPIO16 ├────────────┼─ LRC     │
      │ SCK ────┼─────────────┤ GPIO5   GPIO15 ├────────────┼─ BCLK    │   ┌────────┐
      │ SD  ────┼─────────────┤ GPIO6   GPIO7  ├────────────┼─ DIN   + ├───┤hoparlör│
      └─────────┘             │  (LED: GPIO48) │            │        − ├───┤        │
                              └────────────────┘            └──────────┘   └────────┘
```

## İpuçları
- Mikrofonu hoparlörden **en az 5–10 cm uzağa**, deliği dışarı bakacak şekilde yerleştir; yoksa Jarvis kendi sesini duyar.
- Kartta iki USB-C girişi varsa programlama için **"USB"** yazanı (yerel USB) kullan.
- Durum ışığı yanmıyorsa `esphome/jarvis-uydu.yaml` içinde `led_pin` değerini `GPIO38` yap.

## Işık renkleri

| Renk | Anlamı |
|---|---|
| Turuncu | Açılıyor / Home Assistant'a bağlanıyor |
| Mavi | Dinliyor ("Hey Jarvis" duyuldu) |
| Mor, yanıp sönen | Düşünüyor |
| Yeşil | Konuşuyor |
| Kırmızı (kısa) | Hata |
| Kırmızı (sönük, sürekli) | Mikrofon kapalı (gizlilik) veya bağlantı yok |
