# DEVELOPMENT_ROADMAP.md — Geliştirme Yol Haritası

Her aşamanın bir **çıkış kriteri** vardır; kriter **gerçek donanımda** sağlanmadan aşama "tamamlandı" sayılmaz. Her aşama ayrı commit(ler) ve CHANGELOG girdisiyle, geri alınabilir şekilde yapılır.

| Phase | Hedef | Ön koşul | Çıkış kriteri | Durum |
|---|---|---|---|---|
| **0** | Mevcut projeyi analiz et | — | 7 rapor | 🟡 **Kısmi** — orijinal dosyalar yok |
| 0b | Orijinal dosyaları al ve denetimi tamamla | Kullanıcı ZIP'i yükler | R02 pin tablosu dolu, firmware incelendi, `original/` altında dokunulmamış yedek | ⬜ Kullanıcı bekleniyor |
| **1** | Orijinal KIRA'yı çalıştır | 0b | Orijinal firmware derlenir/yüklenir; Wi-Fi, OLED, ses, mikrofon, (varsa) kamera tek tek test edilir; **test raporu** (çalışan/çalışmayan) | ⬜ |
| **2** | Donanım/bağlantı doğrulama | 1 | Breadboard süreklilik testi, 5V/3V3 ölçümü, R02 ↔ kart ↔ kod üçlü kontrolü, akım ölçümü | ⬜ |
| **3** | Kamera yuvası (3D) | 0b + kamera ölçüleri | Test kuponu uyumu, ayrı dosyada yeni ön panel, kapak çalışıyor | ⬜ Onay gerekir |
| **4** | Canlı görüntü → Windows | 2 | Panelde QVGA ≥ 8 fps / VGA ≥ 5 fps (ölçülen), aç/kapa komutu, OLED kamera ikonu, 30 dk sıcaklık testi | ⬜ |
| **5** | Sürekli görsel algılama | 4 | Hareket + insan algılama, CPU kullanımı ölçülü, kayıt yok | ⬜ |
| **6** | Türkçe ses | 2 | "KIRA" uyandırma, STT, TTS, söz kesme; yanlış uyanma oranı ölçülmüş | ⬜ |
| **7** | Hibrit AI | 6 | Router, Ollama + ≥1 bulut sağlayıcı, internet kesintisinde yerel devam | ⬜ |
| **8** | Uzun süreli hafıza | 7 | SQLite şeması, arama, silme/unutma, yedek/dışa aktarma, hassas veri onayı | ⬜ |
| **9** | Görsel zekâ | 5 + 7 | OCR (Türkçe), QR, "bu ne?" yerel VLM, gerekirse bulut | ⬜ |
| **10** | Windows entegrasyonu | 7 | İzin katmanları, onay akışı, denetim günlüğü | ⬜ |
| **11** | Kontrol paneli | 4–10 | 15 bölüm çalışır | ⬜ |
| **12** | Proaktif asistan | 8 + 11 | Hatırlatmalar, bağlama dayalı öneriler (kapatılabilir, rahatsız etmeyen) | ⬜ |
| **13** | Tüm sistem testi | Hepsi | 24 saat dayanıklılık, çevrimdışı test, gizlilik testi | ⬜ |
| *Gelecek* | Servo baş, pan/tilt, sensörler, RGB, Home Assistant, mobil platform | 13 | — | Hazırlık mimaride |

## Yakın vadeli adımlar (sıra ile)

1. **Kullanıcı:** Orijinal KIRA dosyalarını (firmware, STL/3MF, R02 PDF) depoya yükler + donanım fotoğrafları + SH1107 başlık etiketleri + kamera tipi.
2. **Claude:** Dosyaları `original/` altına dokunulmadan koyar, denetimi tamamlar, R02 tablosunu doldurur, bu raporları günceller.
3. **Kullanıcı onayı** → Phase 1 test firmware'leri (modül başına küçük test sketch'leri; orijinal firmware'e dokunmadan).
4. Kullanıcı testleri donanımda çalıştırır, seri çıktıyı paylaşır → test raporu.

## Dal stratejisi

- `claude/kira-ai-pro-development-lyccwa` — geliştirme dalı (şu an).
- Orijinal dosyalar ilk commit'te etiketlenir: `git tag original-r02` → her zaman geri dönülebilir.
- Her phase sonunda etiket: `phase-1-done`, `phase-2-done`, …
