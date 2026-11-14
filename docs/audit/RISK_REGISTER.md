# RISK_REGISTER.md — Risk Kaydı

Olasılık / Etki: D = Düşük, O = Orta, Y = Yüksek

| ID | Risk | Olas. | Etki | Önlem |
|---|---|---|---|---|
| **R-01** | **Orijinal KIRA dosyaları ve R02 şeması elimizde değil** → pinler doğrulanamaz | **Y (şu an gerçekleşti)** | Y | Kullanıcıdan dosyaları al; o zamana kadar hiçbir kablo/kod değişikliği yok |
| R-02 | R02 şeması ile mevcut kablolama/kod uyuşmuyor | O | Y | Üçlü karşılaştırma (R02 ↔ kart ↔ kod), uyuşmazlıkta önce rapor |
| R-03 | Breadboard iç yapısı varsayılandan farklı (ör. bölünmüş sütun) → kısa devre / bağlantısız modül | O | Y | Multimetre süreklilik testi; modülleri tek tek ekleme |
| **R-04** | MAX98357A 5 V'ta 8 Ω'a ~1 W üzeri verebilir; **0.5 W hoparlör** aşırı yüklenip bozulabilir | O | O | GAIN yükseltilmez (3–6 dB tercih), firmware'de yazılımsal ses sınırı (~%50), test sırasında düşük seviyeden başla |
| R-05 | Sürekli kamera + Wi-Fi ile XIAO aşırı ısınma → kararsızlık, PSRAM hataları | Y | O | Varsayılan QVGA/düşük FPS, gövdede havalandırma, sıcaklık telemetrisi, eşik aşılınca FPS düşürme |
| R-06 | Zayıf USB güç → kamera/Wi-Fi/ses tepe akımında brownout reset | O | O | ≥2 A adaptör, kaliteli kablo, akım ölçümü |
| R-07 | Wi-Fi bant genişliği yetersiz → düşük FPS, ses kesintisi | O | O | Ses akışına öncelik, kamera FPS uyarlamalı, 2.4 GHz kanal seçimi |
| R-08 | Kamera FPC kablosu kısa → kamera ön panele ulaşmaz | O | O | XIAO'yu ön panele yakın konumlama; gerekirse uzatma FPC (satın alma, onaylı) |
| R-09 | Gövde içinde mikrofon zayıf duyar / hoparlör yankısı | Y | O | Mikrofon deliği, hoparlörden uzaklık, PC tarafında referanslı yankı iptali |
| R-10 | "KIRA" uyandırma kelimesinde yanlış tetiklenme (Türkçede "kira" yaygın bir kelime: ev kirası) | **Y** | O | "Hey KIRA" kalıbı, özel model eğitimi + eşik ayarı, yanlış uyanma ölçümü |
| R-11 | Yerel LLM'in Türkçe kalitesi zayıf / PC donanımı yetersiz | O | O | Phase 7'de kullanıcının GPU/RAM'inde karşılaştırmalı test; bulut yedek |
| R-12 | API anahtarı sızıntısı (kaynak kod/git) | O | Y | Windows Kimlik Bilgisi Yöneticisi, `.gitignore`, gizli anahtar taraması |
| R-13 | Orijinal firmware'de gömülü Wi-Fi şifresi / API anahtarı | O | Y | Denetimde tara; varsa kullanıcıya bildir, anahtarı yenilet |
| R-14 | Kamera/mikrofon gizlilik ihlali (LAN'daki başka cihaz akışa erişir) | O | Y | Eşleştirme + kimlik doğrulama, panel sadece 127.0.0.1, görünür göstergeler, fiziksel kapak |
| R-15 | Hafızaya izinsiz hassas veri kaydı | O | Y | Hassas veri sınıflandırıcısı + onay, kullanıcı silme hakkı, denetim günlüğü |
| R-16 | Otomasyon ile istenmeyen dosya silme/veri gönderme | D | Y | İzin katmanları, onay, Geri Dönüşüm Kutusu, rastgele shell yok |
| R-17 | Bulut sağlayıcısına görüntü/ses gönderimi (KVKK/gizlilik) | O | O | Varsayılan yerel; bulut gönderimi ayarlanabilir/onaylı, panelde görünür |
| R-18 | Orijinal tasarımın lisansı türev yayınlamaya izin vermeyebilir | O | O | MakerWorld lisansını kontrol et; değiştirilmiş STL'leri lisans izin vermiyorsa yalnızca kişisel kullan |
| R-19 | Sense kartının "v24" sürümünde pin/kamera farkı | D | O | Seeed sürüm notları + kart üzerindeki etiket kontrolü |
| R-20 | SH1107 modülü 5 V mantık/besleme toleransı bilinmiyor | O | O | Modül etiketine göre; şüphede 3V3 ile besle |
| R-21 | **KIRA PRO:** servo çekişinde 5V hattı düşer → ESP32 reset, ses cızırtısı | O | O | 5V 3A adaptör, 1000 µF kondansatör, servolar yavaş rampalı hareket |
| R-22 | Boyun kablosu sürekli dönmeden kopar / temassızlık | O | O | Silikon çok damarlı kablo, servis halkası, pan ±60° yazılım sınırı |
| R-23 | PC'siz (Mod A) serbest Türkçe konuşma tanıma mümkün değil | **Y** | O | Beklenti net: Mod A'da ifade, hareket, kayıtlı cümleler; sohbet PC (Ollama) ile. Gelecek: Raspberry Pi 5 seçeneği |
| R-24 | Harici 5V verilirken USB'den programlama → geri besleme | O | Y | Programlamadan önce harici gücü ayır; kartların 5V koruma diyotu doğrulanacak |
| R-25 | 3D model ölçüleri gerçek parçalara uymaz | O | D | Parametrik model, önce küçük test parçaları, ölçüm tablosu |
| R-26 | T-Display-S3 pin önerisi kart revizyonuyla çelişir | O | O | LILYGO pin şeması + kart baskısıyla karşılaştırmadan bağlama |
