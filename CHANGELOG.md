# CHANGELOG

Tüm önemli değişiklikler bu dosyada belgelenir.

## [Unreleased]

### Eklendi — 2026-11-14 · KIRA PRO tasarımı (v0.1 taslak)
- `docs/KIRA_PRO_DESIGN.md`: pan/tilt başlı yeni tasarım; 3 çalışma modu (tek başına / ev ağı / tam), iki kartlı mimari (T-Display-S3 ana kontrolcü + yüz, XIAO Sense göz-kulak), önerilen pin planı, güç dağıtımı, eksik parça listesi, kişilik motoru, baskı ve montaj rehberi.
- `hardware/kira_pro/kira_pro.scad`: parametrik OpenSCAD modeli (gövde, alt kapak, pan halkası, döner tabla + çatal, baş, arka kapak, kayar kamera kapağı) ve `stl/` altında dışa aktarılmış 8 parça, önizleme görselleri.
- `docs/audit/RISK_REGISTER.md`: R-21…R-26 eklendi.
- Not: Parçalar basılmadı, donanımda denenmedi; ölçüler tipik değerlerdir.

### Eklendi — 2026-11-13 · Windows çekirdeği (Phase 7–8 temeli)
- `windows/kira/memory/store.py`: SQLite + FTS5 uzun süreli hafıza — konuşmalar, bilgiler, projeler, görevler, hatırlatmalar, cihaz ayarları, denetim günlüğü, yedekleme ve JSON dışa aktarma. Hassas bilgiler onaysız kaydedilmez.
- `windows/kira/ai/`: değiştirilebilir sağlayıcı arayüzü, Ollama (yerel) ve Anthropic (bulut) sağlayıcıları, hibrit yönlendirici (internet kesilince yerele düşer, görüntüler izinsiz buluta gitmez).
- `windows/kira/core/persona.py`: KIRA'nın Türkçe karakter tanımı; donanım durumunu yalnızca gerçek ölçüme göre anlatır.
- `windows/kira/core/assistant.py`: hızlı komutlar (saat, tarih, hatırla, unut, durum, kamera/ses), hassas bilgi onay akışı, hafızalı AI sohbeti.
- `windows/kira/security/`: API anahtarları için Windows Kimlik Bilgisi Yöneticisi (keyring), Türkçe hassas veri tespiti (TCKN, IBAN, kart, telefon, e-posta, anahtar kelimeler).
- `python -m kira` komut satırı ve `tests/` altında 51 test.
- Not: Ses, kamera ve ESP32 bağlantısı henüz yok. Firmware/STL/3MF dosyalarına dokunulmadı.

### Eklendi — 2026-11-12 · Phase 0 (kısmi)
- `docs/audit/` altında ilk analiz raporları: `PROJECT_AUDIT.md`, `HARDWARE_INVENTORY.md`, `CAMERA_DESIGN.md`, `PIN_CONNECTION_MAP.md`, `SOFTWARE_ARCHITECTURE.md`, `DEVELOPMENT_ROADMAP.md`, `RISK_REGISTER.md`.
- Not: Depoda orijinal KIRA dosyaları (firmware, STL/3MF, R02 PDF) bulunmadığı için raporlar kısmidir. Hiçbir firmware/3D dosyası değiştirilmedi. Kod yazılmadı.
