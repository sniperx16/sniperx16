# Home Assistant – Jarvis sesli asistan ve paket kurulumu

Bu ayarlarla:
- **"Salonun ışığını aç"** gibi basit komutlar **yerelde, internetsiz ve anında** çalışır.
- Anlaşılmayan veya karmaşık istekler **Claude**'a gider (Jarvis kişiliğiyle).
- Bilgisayar, araştırma gibi büyük görevler **OpenJarvis**'e devredilir.

## 1. Paketi yükle
1. **Ayarlar → Eklentiler → Eklenti Mağazası → Studio Code Server** (veya File editor) kur ve aç.
2. `/config/packages/` klasörünü oluştur, içine `homeassistant/packages/jarvis.yaml` dosyasını kopyala.
3. `/config/configuration.yaml` dosyasının **en sonuna** ekle:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```
   (Dosyada zaten `homeassistant:` satırı varsa altına sadece `packages:` satırını ekle.)
4. `/config/secrets.yaml` dosyasına `homeassistant/secrets.yaml.ornek` içindeki satırları ekle ve değerleri doldur.
   OpenJarvis adresi ve anahtarı için OpenJarvis VM'inde: `./openjarvis/kur.sh anahtar`
5. **Geliştirici Araçları → YAML → Yapılandırmayı kontrol et** → yeşilse **Yeniden başlat**.
6. Örnek otomasyonlardaki cihaz adlarını (`binary_sensor.salon_hareket`, `light.salon` …) cihazların gelince kendi adlarınla değiştir.

## 2. Yerel ses eklentileri
**Ayarlar → Eklentiler → Eklenti Mağazası**:

| Eklenti | Ayar | Değer |
|---|---|---|
| **Whisper** (konuşma → yazı) | Language | `tr` |
| | Model | `small-int8` (Türkçe için iyi denge; yavaş gelirse `base-int8`) |
| **Piper** (yazı → konuşma) | Voice | `tr_TR-fahrettin-medium` (alternatif: `tr_TR-dfki-medium`, `tr_TR-fettah-medium`) |

Her ikisini **Başlat**, **Açılışta başlat** açık olsun. Ardından **Ayarlar → Cihazlar ve Hizmetler**'de "Wyoming" olarak otomatik bulunurlar → **Yapılandır**.

> "Hey Jarvis" kelimesi ses uydusunun üzerinde çalıştığı için **openWakeWord eklentisine gerek yok**.

## 3. Claude (bulut beyni)
1. **Ayarlar → Cihazlar ve Hizmetler → Entegrasyon Ekle → Anthropic** → Claude API anahtarını gir.
2. Oluşan **konuşma aracısını** (conversation agent) yapılandır:
   - **Model:** `claude-haiku-5-5` (hızlı ve ucuz; ses için ideal)
   - **Home Assistant'ı kontrol et:** **Assist** seçili
   - **Talimatlar (prompt):** aşağıdaki metni yapıştır

```
Sen Jarvis'sin, bu evin yapay zekâ asistanısın. Her zaman Türkçe konuş.
Cevapların sesli okunacak: kısa ol (1-2 cümle), liste, emoji ve markdown kullanma.
Kibar, sakin ve hafif esprili ol.
Bir işlem yaptıktan sonra kısaca onayla ("Salon ışığını açtım").
Kapı kilidi, alarm, kamera ve ocak gibi güvenlik cihazlarında işlem yapmadan önce onay iste.
Bilgisayarda işlem, internette araştırma veya çok adımlı karmaşık görevler için
"Jarvis'e görev ver" betiğini kullan ve sonucunu kısaca özetle.
```

## 4. Ses hattı (pipeline)
**Ayarlar → Sesli asistanlar → Asistan ekle**:

| Alan | Değer |
|---|---|
| Ad | Jarvis |
| Dil | Türkçe |
| Konuşma aracısı | Claude (Anthropic) |
| **Komutları öncelikle yerel olarak işle** | **Açık** ← internetsiz basit komutlar için şart |
| Konuşmayı yazıya çevirme | faster-whisper |
| Yazıyı konuşmaya çevirme | piper → seçtiğin Türkçe ses |

Kaydet, sonra yıldız (⋮ → **Tercih edilen olarak ayarla**).

## 5. Jarvis'e neleri açacağını seç
**Ayarlar → Sesli asistanlar → Göster (Expose)**:
- Işıkları, prizleri, klimayı, sensörleri **aç**.
- `script.jarvis_gorev_ver`, `script.bilgisayari_ac`, `script.iyi_geceler` betiklerini **aç**.
- Kilit, alarm gibi kritik cihazları başta **kapalı** bırak.

## 6. OpenJarvis'in Home Assistant'ı kontrol etmesi (MCP)
1. **Entegrasyon Ekle → Model Context Protocol Server** → Kontrol: **Assist**.
2. **Profil (sol alt) → Güvenlik → Uzun ömürlü erişim jetonları → Jeton oluştur** (ad: `openjarvis`).
3. OpenJarvis VM'inde: `./openjarvis/kur.sh mcp` → HA IP'sini ve jetonu gir.

OpenJarvis yalnızca 5. adımda "Göster" ile açtığın cihazları görebilir.

## 7. Ses uydusunu ekle
1. **ESPHome Device Builder** eklentisini kur → aç → **Secrets**'a `wifi_ssid` ve `wifi_password` ekle.
2. **+ New Device** → ad: `jarvis-salon` → ESP32-S3 → oluşan dosyayı **Edit** ile aç → içeriğini `esphome/jarvis-uydu.yaml` ile değiştir.
3. Kartı USB ile **bu bilgisayara** tak → **Install → Plug into this computer** (Chrome/Edge gerekir). İlk derleme 10–20 dk sürebilir.
4. Sonraki güncellemeler Wi-Fi üzerinden yapılır (**Install → Wirelessly**).
5. **Ayarlar → Cihazlar ve Hizmetler**'de cihaz bulunur → **Yapılandır** → asistan: **Jarvis**.

## Deneme cümleleri
- "Hey Jarvis, salonun ışığını aç." → yerel, anında
- "Hey Jarvis, ev çok sıcak, ne yapalım?" → Claude
- "Hey Jarvis, bilgisayarımı aç." → betik
- "Hey Jarvis, bu hafta sonu İstanbul'da yapılacak etkinlikleri araştır." → OpenJarvis'e görev
