# KIRA AI PRO — Windows tarafı

Bu klasör KIRA'nın "beyni"dir: hafıza, hibrit AI (yerel + bulut), karakter ve güvenlik.
Ses, kamera, cihaz bağlantısı ve kontrol paneli sonraki aşamalarda eklenecek.

## Kurulum (Windows 11)

1. **Python 3.11+** kurun (python.org, "Add to PATH" işaretli).
2. PowerShell'de bu klasöre gelin ve kurun:
   ```powershell
   cd windows
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -e .[dev]
   ```
3. **Yerel AI (isteğe bağlı ama önerilir):** https://ollama.com adresinden Ollama'yı kurun, sonra:
   ```powershell
   ollama pull qwen2.5:7b      # sohbet
   ollama pull qwen2.5vl:7b    # görüntü (Phase 9)
   ```
   Model seçimi ekran kartınıza göre değiştirilebilir (bkz. ayarlar). Türkçe kalitesi Phase 7'de karşılaştırmalı test edilecek.
4. **Bulut AI (isteğe bağlı):** Anthropic API anahtarını güvenli şekilde kaydedin:
   ```powershell
   python -m kira key set anthropic
   ```
   Anahtar Windows Kimlik Bilgisi Yöneticisi'nde saklanır; dosyaya veya koda yazılmaz.

## Kullanım

```powershell
python -m kira status              # yerel/bulut AI ve internet durumu
python -m kira                     # yazılı sohbet
python -m kira memory list         # hafızadaki bilgiler
python -m kira memory search kahve
python -m kira memory forget 3     # 3 numaralı kaydı sil
python -m kira memory backup       # yedek al
python -m kira memory export       # JSON'a aktar (hassas kayıtlar hariç)
```

Sohbette denenebilecek hızlı komutlar (AI çağrısı yapmaz):
`saat kaç`, `bugün günlerden ne`, `Bunu hatırla: ...`, `... bilgisini unut`,
`neleri hatırlıyorsun`, `durumun ne`, `kamerayı kapat` (gövde bağlıyken).

## Ayarlar

`%APPDATA%\KIRA\config.toml` (yoksa varsayılanlar kullanılır):

```toml
user_name = "Adınız"

[local_ai]
chat_model = "qwen2.5:7b"
vision_model = "qwen2.5vl:7b"

[cloud_ai]
enabled = true
model = "claude-opus-5-5"
chat_effort = "low"        # hızlı sohbet
complex_effort = "high"    # karmaşık görevler
allow_images = false       # kamera görüntüsünü buluta göndermek için true yapın
```

Bu dosyaya API anahtarı yazılırsa KIRA açılmayı reddeder.

## Nasıl karar veriyor?

| İstek | Önce | Olmazsa |
|---|---|---|
| Hızlı komut (saat, hatırla, unut…) | Kural, AI yok | — |
| Basit sohbet | Yerel AI | Bulut AI |
| Karmaşık soru ("analiz et", "karşılaştır", uzun metin) | Bulut AI | Yerel AI (kullanıcıya söylenir) |
| Görüntülü soru | Yerel görsel model | Bulut (yalnızca `allow_images = true` ise) |

Hassas bilgi (şifre, kimlik no, IBAN, kart, sağlık, adres…) hafızaya kaydedilmeden önce KIRA onay ister.

## Testler

```powershell
cd ..
python -m pytest
```
