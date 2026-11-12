# SOFTWARE_ARCHITECTURE.md — Yazılım Mimarisi

> Orijinal firmware incelenemediği için bu, **hedef mimari önerisidir**. Orijinal kod geldiğinde, çalışan kısımlar korunacak şekilde uyarlanacak.

## 1. Temel ilke: "Beyin Windows'ta, duyular ESP32'de"

```
┌──────────────── XIAO ESP32-S3 Sense (ince istemci) ────────────────┐
│ camera/  → JPEG kareler              audio/ → PDM mic 16 kHz akışı   │
│ display/ → SH1107 yüz/ikonlar        audio/ → I2S → MAX98357A        │
│ communication/ → Wi-Fi, WebSocket kontrol, mDNS (kira.local), OTA    │
│ Yerel güvenlik: kamera/mikrofon kapatma, PC yoksa "çevrimdışı" yüzü  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ Yerel ağ (LAN) — buluta doğrudan gitmez
┌───────────────────────────────▼─────────── Windows 11 ──────────────┐
│ core/        olay veri yolu, durum makinesi, ayarlar, servis yöneticisi │
│ speech/      VAD, wake word "KIRA", STT, TTS, yankı/gürültü azaltma    │
│ vision/      hareket, insan/nesne, QR, OCR, VQA tetikleyicileri         │
│ ai/          yönlendirici (router) + sağlayıcılar (Ollama, bulut)       │
│ memory/      SQLite + FTS5 + vektör arama, yedek/dışa aktarma           │
│ automation/  Windows araçları (izin katmanlı)                          │
│ security/    anahtar kasası, onay akışı, denetim günlüğü               │
│ dashboard/   yerel web paneli (127.0.0.1)                               │
└─────────────────────────────────────────────────────────────────────┘
```

**Neden:** ESP32-S3 8 MB PSRAM ile STT/LLM/görüntü işleme çalıştıramaz; PC çalıştırabilir. ESP32 tarafını ince tutmak, firmware'i nadiren değiştirmeyi ve orijinal davranışı korumayı kolaylaştırır.

**Orijinal modun korunması:** Orijinal firmware kendi başına (ör. doğrudan bulut ile) çalışıyorsa, yeni firmware bunu bir **"Klasik KIRA" modu** olarak saklayacak; PC bulunamazsa bu moda geri dönülebilecek. (Orijinal kod görülünce kesinleşecek.)

## 2. ESP32 ↔ Windows protokolü

| Kanal | Taşıma | İçerik |
|---|---|---|
| Kontrol | WebSocket (JSON) | `hello`, `status` (sıcaklık, RSSI, heap, PSRAM), `camera.set`, `mic.set`, `face.set`, `volume.set`, `ota` |
| Mikrofon | WebSocket (ikili) | 16 kHz 16-bit mono PCM, 20 ms çerçeveler |
| Hoparlör | WebSocket (ikili) | 16/22.05 kHz PCM; ESP32 tarafında halka tampon |
| Kamera | HTTP MJPEG (`/stream`) + tek kare (`/capture`) | JPEG |

- Eşleştirme: ilk bağlantıda panelde gösterilen 6 haneli kod; sonrasında paylaşılan anahtar ile kimlik doğrulama (yerel ağdaki başka cihazlar kamerayı açamasın).
- Zaman aşımı/kopma: ESP32 OLED'de "bağlantı yok" ifadesi gösterir, kamera ve mikrofon akışını **durdurur**.

## 3. Ses hattı (speech/)

| Aşama | Yerel (varsayılan) | Bulut (isteğe bağlı) |
|---|---|---|
| VAD | Silero VAD | — |
| Uyandırma kelimesi "KIRA" | openWakeWord özel model (PC'de) | — |
| STT | faster-whisper (Türkçe; GPU varsa `medium`/`large-v3`, yoksa `small`) | Değiştirilebilir sağlayıcı |
| TTS | Piper Türkçe sesleri | Değiştirilebilir sağlayıcı (daha doğal ses) |
| Söz kesme (barge-in) | PC, çaldığı sesi bildiği için referanslı yankı iptali (WebRTC APM) + VAD | — |
| Gürültü azaltma | WebRTC APM NS / RNNoise | — |

Mikrofon ilk sürümde **PC'de** uyandırma kelimesi dinlediği için ses LAN üzerinden sürekli akar; bu yalnızca yerel ağdadır ve panelden/sesli komutla/OLED ikonuyla görünür şekilde kapatılabilir. İleride ESP-SR ile cihaz üstü uyandırma değerlendirilecek.

## 4. Hibrit AI (ai/)

```
kullanıcı isteği → Router
   ├─ Kural tabanlı hızlı yol (saat, ses aç/kapa, kamera kapat, hatırlatıcı) → anında
   ├─ Yerel LLM (Ollama)  → sohbet, kısa sorular, hafıza özetleme, çevrimdışı mod
   └─ Bulut LLM           → karmaşık muhakeme, uzun görev, detaylı görsel analiz
```

- **Sağlayıcı arayüzü:** `chat()`, `vision()`, `embed()` — Ollama, Anthropic, OpenAI, Gemini vb. eklenti olarak; ayarlardan değiştirilir.
- **Yerel model adayları (Ollama):** Türkçe kalitesi Phase 7'de kullanıcının GPU/RAM'ine göre **test edilerek** seçilecek (ör. Qwen, Gemma, Llama ailesinin 4–9B sürümleri; görsel için Qwen-VL / Gemma görsel sürümleri). Gömme için çok dilli bir embedding modeli.
- **Çevrimdışı:** internet kontrolü başarısızsa router bulut yolunu kapatır, kullanıcıya "şu an çevrimdışıyım, yerel modelle cevaplıyorum" der.
- **API anahtarları:** Windows Kimlik Bilgisi Yöneticisi (`keyring`) — kaynak kodda, `.env`'de veya git'te **asla**.

## 5. Hafıza (memory/) — SQLite

| Tablo | İçerik |
|---|---|
| `conversations`, `messages` | Konuşma geçmişi (zaman, kaynak: ses/panel) |
| `facts` | Kullanıcı tercihleri ve önemli bilgiler (`key, value, source_message_id, confidence, sensitive`) |
| `projects`, `tasks`, `reminders` | Devam eden işler, hatırlatmalar (zamanlayıcı ile) |
| `device_settings` | Cihaz ayarları |
| `embeddings` | Vektör (sqlite-vec) — anlamsal arama |
| `audit_log` | Hafıza değişiklikleri, onaylar |
| FTS5 sanal tablosu | Tam metin arama |

- **Hassas veri:** sağlık, kimlik no, şifre, finans, konum vb. sınıflandırıcıya takılırsa **sormadan kaydedilmez** ("Bunu hatırlamamı ister misin?").
- Kullanıcı panelden ve sesle görebilir/düzenleyebilir/silebilir ("KIRA, bunu unut").
- Yedek: günlük otomatik `.sqlite` yedeği; dışa aktarma JSON/Markdown.

## 6. Windows otomasyonu (automation/) — izin katmanları

| Katman | Örnekler | Davranış |
|---|---|---|
| 0 – Okuma | CPU/RAM/GPU, internet testi, saat | Otomatik |
| 1 – Zararsız eylem | Program açma (izin listesi), izinli klasörde dosya arama, ekran görüntüsü (yerel) | Otomatik + günlük |
| 2 – Değiştirici | Dosya oluşturma/taşıma/değiştirme, görev sonlandırma | **Kullanıcı onayı** |
| 3 – Tehlikeli / harici | Dosya silme (Geri Dönüşüm Kutusu'na), ağa veri gönderme, komut çalıştırma | **Açık onay + özet gösterimi**; rastgele shell komutu yok |

## 7. Kontrol paneli (dashboard/)

- FastAPI arka uç + yerel web arayüzü, yalnızca `127.0.0.1`; masaüstü penceresi için WebView sarmalayıcı.
- Sayfalar: Ana ekran, Canlı kamera, Kamera gizliliği, AI motoru (Yerel/Bulut), Hafıza, Konuşma geçmişi, Ses, Cihaz bağlantısı, Sistem durumu, Görevler, Otomasyonlar, Güvenlik, Günlükler.
- LILYGO T-Display-S3 isteğe bağlı ikinci durum ekranı olarak aynı API'ye bağlanabilir.

## 8. Gelecek genişlemeye hazırlık

- Firmware'de `actuators/` ve `sensors/` için soyut arayüz; kontrol protokolünde `servo.set`, `sensor.read` mesaj tipleri ayrılmış.
- Boş GPIO'lar (PIN_CONNECTION_MAP §6) servo/sensör/RGB için ayrılmış.
- Home Assistant: `automation/` altında REST/WebSocket entegrasyonu, aynı onay katmanlarıyla.

## 9. Dizin yapısı (oluşturulacağı zaman)

```
firmware/        camera/ audio/ display/ communication/   (+ original/ dokunulmaz)
windows/         core/ ai/ vision/ speech/ memory/ automation/ security/ dashboard/
hardware/        3d_models/original/ schematics/ camera_mount/
tests/
docs/            audit/ (bu raporlar)
CHANGELOG.md
```
Klasörler yalnızca içine gerçek dosya konacağı aşamada oluşturulacak (boş iskelet yok).
