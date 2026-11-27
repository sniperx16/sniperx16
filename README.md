# Ev Jarvis'i

Evdeki mini PC'de (HP ProDesk 600 G4 Mini) çalışan, **yerel + bulut** hibrit ev asistanı.
Evi kontrol eder ve gözler, "Hey Jarvis" ile sesli komut alır, verilen görevleri yerine getirir,
bilgisayarını açıp kontrol edebilir.

| Belge | İçerik |
|---|---|
| `Jarvis_Kurulum_Kilavuzu.pdf` | Adım adım kurulum kılavuzu (ekranlar, menüler, kontrol listeleri) |
| `Jarvis_Uygun_Maliyet_Calismasi.pdf` | Parça listesi ve maliyet çalışması |
| `homeassistant/SESLI-ASISTAN.md` | Sesli asistan, Claude ve paket kurulumu |
| `esphome/BAGLANTI.md` | Ses uydusu bağlantı şeması |
| `SALI-HAZIRLIK.md` · `Jarvis_Sali_Kontrol_Listesi.pdf` | Kurulum günü kontrol listesi (sırayla, süreleriyle; yazdırılabilir) |

## Sistem nasıl çalışır

```
 "Hey Jarvis, salonun ışığını aç"
        │
 ┌──────▼──────┐  Wi-Fi   ┌──────────────────────── Mini PC (Proxmox) ─────────────────────────┐
 │ ESP32 ses   ├─────────►│  VM 100: Home Assistant OS                                         │
 │ uydusu      │          │    Whisper (TR, yerel) → Assist ──┬─ basit komut: YEREL, anında     │
 │ "Hey Jarvis"│◄─────────┤    Piper (TR, yerel)              └─ karmaşık: Claude (bulut)       │
 │ cihazda     │          │    Zigbee sensörler, kameralar, bilgisayar (WoL, HASS.Agent)       │
 └─────────────┘          │            ▲ MCP (cihaz kontrolü)    │ "Jarvis'e görev ver"         │
                          │            │                          ▼                             │
                          │  VM 101: Ubuntu + OpenJarvis (ajan)                                │
                          │    Claude (bulut) ── internet yoksa ──► Ollama qwen3:8b (yerel)    │
                          │  256 GB disk: her gece otomatik yedek                              │
                          └────────────────────────────────────────────────────────────────────┘
```

- **İnternet kesilirse:** ışık/priz/sensör otomasyonları, "Hey Jarvis", basit sesli komutlar
  ve yerel model çalışmaya devam eder. Sadece Claude gerektiren karmaşık istekler beklemeye düşer.
- **Elektrik kesilirse:** cihaz elektrik gelince kendiliğinden açılır, sanal makineler sırayla başlar.

## Klasörler

| Klasör | Ne var | Nerede çalışır |
|---|---|---|
| `jarvis.env.ornek` | IP adresleri, şifreler, MAC – **tek ayar dosyası** | — |
| `proxmox/kur.sh` | Depo, yedek disk, HA VM, OpenJarvis VM, gece yedeği, Zigbee USB | Proxmox Shell (root) |
| `openjarvis/` | Kurulum betiği, ayar şablonu, Jarvis kişiliği | Ubuntu VM (jarvis kullanıcısı) |
| `homeassistant/` | Kurulum betiği (`kur.sh`), Jarvis paketi, pano, secrets örneği, ses rehberi | Home Assistant (Terminal & SSH) |
| `homeassistant/www/jarvis/` | Holografik Jarvis yüzü (canlı HA bağlantılı) + `ayarlar.json` | `http://<HA-IP>:8123/local/jarvis/` |
| `esphome/` | "Hey Jarvis" ses uydusu kodu ve bağlantı şeması | ESP32-S3 |
| `windows/` | Wake-on-LAN hazırlık betiği | Windows bilgisayar (yönetici) |

## Kurulum sırası

Kılavuz PDF'teki bölüm numaraları parantez içinde.

### A. Senin yapacakların (cihazın başında, ≈ 45 dk)
1. RAM ve SSD'yi tak (1), BIOS ayarlarını yap (2).
2. Proxmox'u **500 GB** diske kur (256 GB'a değil) (3). Sabit IP: `jarvis.env.ornek` içindeki `PROXMOX_IP`.

### B. Proxmox (tarayıcıdan `https://<PROXMOX_IP>:8006` → jarvis → Shell)
```bash
apt-get update && apt-get install -y git
git clone -b claude/home-automation-jarvis-rbwn7x https://github.com/sniperx16/sniperx16.git /root/jarvis-ev
cd /root/jarvis-ev
cp jarvis.env.ornek jarvis.env && nano jarvis.env      # IP'leri, şifreyi, MAC'i yaz → Ctrl+O, Enter, Ctrl+X
chmod +x proxmox/kur.sh openjarvis/kur.sh

./proxmox/kur.sh depo          # (4.1) güncellemeler – bittikten sonra: reboot
./proxmox/kur.sh yedek-disk    # (4.2) 256 GB disk → "yedek"  (EVET yazarak onaylarsın)
./proxmox/kur.sh ha            # (5)   Home Assistant VM
./proxmox/kur.sh jarvis        # (6)   Ubuntu VM (kurulum ekranı yok, otomatik)
./proxmox/kur.sh yedekleme     # (9)   her gece 03:00 yedek
```
### C. Home Assistant (`http://<HA-IP>:8123`)
Hesabını oluştur, sonra `homeassistant/SESLI-ASISTAN.md`:
1. adımdaki **tek komutla** Jarvis dosyalarını yükle (Terminal & SSH eklentisinde `homeassistant/kur.sh`),
2–6. adımlarda ses hattını, Claude'u ve MCP'yi tıklayarak ayarla, 8. adımda hologram ve panoyu aç.

### D. OpenJarvis (Ubuntu VM)
```bash
ssh jarvis@<JARVIS_IP>        # şifre: jarvis.env içindeki JARVIS_PASSWORD
passwd                         # ilk iş şifreyi değiştir
git clone -b claude/home-automation-jarvis-rbwn7x https://github.com/sniperx16/sniperx16.git ~/jarvis-ev
cd ~/jarvis-ev && ./openjarvis/kur.sh
```
Betik sırasıyla: Claude anahtarını sorar → OpenJarvis'i kurar → yerel modeli indirir →
ayarları ve kişiliği yazar → Home Assistant bağlantısını (MCP) kurar → arka plan servisini
açar → test eder → Home Assistant'a girilecek adres/anahtarı gösterir.

### E. Windows bilgisayar (8)
`windows/wol-hazirla.ps1` → çıkan MAC'i HA `secrets.yaml` içine `pc_mac` olarak yaz.
HASS.Agent kurulumu için kılavuzun 8.2 bölümü.

### F. Parçalar gelince
- **Zigbee çubuğu:** tak → `./proxmox/kur.sh zigbee` → HA'da ZHA ile sensörleri eşleştir.
- **Ses uydusu:** `esphome/BAGLANTI.md` → `homeassistant/SESLI-ASISTAN.md` 7. adım.

## Bakım
| İş | Komut / yer |
|---|---|
| OpenJarvis güncelle | VM 101: `./openjarvis/kur.sh guncelle` |
| OpenJarvis çalışıyor mu | VM 101: `./openjarvis/kur.sh test` · günlük: `journalctl -u openjarvis -f` |
| Proxmox güncelle | Proxmox Shell: `apt update && apt dist-upgrade` |
| Home Assistant güncelle | Ayarlar → Sistem → Güncellemeler (önce yedek alınır) |
| Yedekten geri dön | Proxmox → yedek → Backups → yedeği seç → Restore |

## Güvenlik
- `jarvis.env`, `secrets.yaml`, `mcp-servers.json` gizli bilgi içerir; `.gitignore` sayesinde GitHub'a gönderilmez.
- Modemden **port açma**. Dışarıdan erişim için Tailscale veya Home Assistant Cloud kullan.
- Claude hesabında **aylık harcama limiti** olsun.
- Kilit/alarm gibi cihazları Jarvis'e (Expose) sonradan ve bilerek aç; Jarvis bunlar için her seferinde onay ister.
