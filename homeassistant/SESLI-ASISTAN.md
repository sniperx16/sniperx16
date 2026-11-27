# Home Assistant – Jarvis sesli asistan ve paket kurulumu

Bu ayarlarla:
- **"Salonun ışığını aç"** gibi basit komutlar **yerelde, internetsiz ve anında** çalışır.
- Anlaşılmayan veya karmaşık istekler **Claude**'a gider (Jarvis kişiliğiyle).
- Bilgisayar, araştırma gibi büyük görevler **OpenJarvis**'e devredilir.

## 1. Jarvis dosyalarını yükle (tek komut)
1. Sol alttaki **profil adına** tıkla → **Gelişmiş mod**'u aç (eklenti mağazasında Terminal görünsün diye).
2. **Ayarlar → Eklentiler → Eklenti Mağazası → "Terminal & SSH"** → Yükle → Başlat → **Web arayüzünü aç**.
3. Açılan siyah ekrana şunu yapıştır ve Enter'a bas:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/sniperx16/sniperx16/claude/home-automation-jarvis-rbwn7x/homeassistant/kur.sh | bash
   ```
4. Betik sırayla sorar (bilmediğini boş geç, sonra **File editor** ile `secrets.yaml`'dan düzeltirsin):
   - OpenJarvis adresi ve anahtarı → OpenJarvis VM'inde `./openjarvis/kur.sh anahtar` çıktısı
   - Windows bilgisayarın MAC adresi → `windows/wol-hazirla.ps1` çıktısı
   - Ev Wi-Fi adı ve şifresi → ses uydusu için
5. Betik yapılandırmayı kontrol edip Home Assistant'ı yeniden başlatır (1–2 dk).

Betik şunları kurar: Jarvis paketi (betikler, otomasyonlar), hologram arayüzü (`/config/www/jarvis`),
pano dosyası (`/config/jarvis-pano.yaml`). Güncellemek için aynı komutu tekrar çalıştırman yeterli.

Örnek otomasyonlardaki cihaz adlarını (`binary_sensor.salon_hareket`, `light.salon` …) cihazların gelince
`/config/packages/jarvis.yaml` içinde kendi adlarınla değiştir.

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

## 8. Hologram ve pano
- **Hologram (tam ekran):** `http://<HA-IP>:8123/local/jarvis/index.html`
  - Home Assistant'ta oturum açılmış tarayıcıda otomatik bağlanır. Duvar tableti gibi başka bir cihazda
    açarsan bir kez **uzun ömürlü jeton** ister; jeton sadece o cihazda saklanır.
  - "Hey Jarvis" denince dinler, düşünür, Jarvis'in gerçek cevabını altyazıyla gösterir.
  - Ekrana dokun ya da klavyede yazmaya başla → Jarvis'e yazılı soru sor; cevap sesli okunur,
    ağız sese göre hareket eder.
  - Paneller: `/config/www/jarvis/ayarlar.json` içindeki sensörler (File editor ile düzenle, sayfayı yenile).
- **Pano:** Ayarlar → Panolar → **Pano ekle** → "Sıfırdan yeni pano" → ad: **Jarvis** → panoyu aç →
  ✏️ → ⋮ → **Ham yapılandırma düzenleyici** → içeriği `/config/jarvis-pano.yaml` ile değiştir → Kaydet.
  İlk sekme tam ekran hologram, ikinci sekme ev kontrolleri.

