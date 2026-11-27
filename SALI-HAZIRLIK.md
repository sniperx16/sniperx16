# Salı – Jarvis kurulum günü

Toplam süre: **yaklaşık 3–4 saat**. Her adımın sonunda ✔ işaretle. Takıldığın yerde ekran görüntüsünü gönder.

## Pazartesi akşamı (≈ 30 dk) – önceden hazırla

### Elinde olması gerekenler
- [ ] HP ProDesk 600 G4 Mini + orijinal adaptör
- [ ] 16 GB RAM (Kingston KVR32S22D8/16)
- [ ] 500 GB M.2 NVMe SSD
- [ ] USB flash bellek (8 GB+; içi silinecek)
- [ ] Ethernet kablosu (mini PC → modem)
- [ ] Monitör + DisplayPort kablosu (monitör sadece HDMI ise **DP → HDMI** adaptör) + USB klavye
- [ ] Küçük yıldız tornavida

### Bilgisayarında yap
- [ ] **Proxmox VE ISO**'yu indir: proxmox.com/en/downloads → "Proxmox VE ISO Installer"
- [ ] **Rufus** ile ISO'yu flash belleğe yaz (sorarsa "DD imaj modu")
- [ ] **Claude API anahtarı**: console.anthropic.com → API Keys → Create Key → güvenli bir yere kaydet
- [ ] Aynı yerde **Billing → Limits**: aylık harcama limiti koy (örn. 10 $)
- [ ] Windows'ta **yönetici** PowerShell'de `windows/wol-hazirla.ps1` çalıştır → çıkan **MAC adresini** not et
- [ ] Telefona **Home Assistant** uygulamasını indir (App Store / Google Play)

### Not al (kurulumda sorulacak)

| Bilgi | Değer |
|---|---|
| Modem adresi (genelde 192.168.1.1) | |
| Modemin dağıttığı adres aralığı (DHCP) | |
| Proxmox IP (aralık dışında, örn. .50) | |
| OpenJarvis IP (örn. .51) | |
| Home Assistant IP (kurulunca öğrenilir) | |
| Ev Wi-Fi adı / şifresi | |
| Windows bilgisayarın MAC adresi | |
| Modem arayüzü kullanıcı adı / şifresi | |

## Salı – sırayla

### 1. Donanım (≈ 15 dk) · Kılavuz bölüm 1
- [ ] Fişi çek, kapağı aç, fanı kaldır
- [ ] Yeni 16 GB RAM'i **boş yuvaya** tak (8 GB yerinde kalsın)
- [ ] 500 GB SSD'yi boş M.2 yuvasına tak, vidala
- [ ] Kapağı kapat; ethernet, monitör, klavye, flash belleği tak

### 2. BIOS (≈ 5 dk) · Kılavuz bölüm 2 · açılışta **F10**
- [ ] RAM **24 GB**, iki SSD görünüyor
- [ ] Secure Boot **kapalı**, VTx ve VTd **açık**, After Power Loss **Power On**

### 3. Proxmox kurulumu (≈ 20 dk) · Kılavuz bölüm 3 · açılışta **F9** → USB
- [ ] Hedef disk: **~465 GB** olan (500 GB SSD)
- [ ] Ülke Turkey, saat dilimi Europe/Istanbul, klavye Turkish (Q)
- [ ] Sabit IP (tablodaki Proxmox IP), gateway = modem adresi
- [ ] Bitince flash belleği çıkar → başka bilgisayardan `https://<Proxmox-IP>:8006` → kullanıcı `root`

### 4. Proxmox betikleri (≈ 30 dk) · jarvis → **Shell**
```bash
apt-get update && apt-get install -y git
git clone -b claude/home-automation-jarvis-rbwn7x https://github.com/sniperx16/sniperx16.git /root/jarvis-ev
cd /root/jarvis-ev && cp jarvis.env.ornek jarvis.env && nano jarvis.env
```
- [ ] `jarvis.env`'e IP'leri, `JARVIS_PASSWORD` ve `PC_MAC` yaz (Ctrl+O, Enter, Ctrl+X)
```bash
chmod +x proxmox/kur.sh openjarvis/kur.sh
./proxmox/kur.sh depo        # bitince: reboot  (sonra tekrar Shell → cd /root/jarvis-ev)
./proxmox/kur.sh yedek-disk  # ~238 GB olan diski seç, EVET yaz
./proxmox/kur.sh ha
./proxmox/kur.sh jarvis
./proxmox/kur.sh yedekleme
```

### 5. Home Assistant ilk açılış (≈ 15 dk)
- [ ] Proxmox → 100 → Summary'de IP'yi gör (birkaç dk sürebilir)
- [ ] Modemde bu IP'yi **sabitle** (DHCP rezervasyonu) → tabloya yaz
- [ ] `http://<HA-IP>:8123` → hesap oluştur → dil **Türkçe**, konum: ev

### 6. OpenJarvis (≈ 30 dk) · Kılavuz bölüm 6
```bash
ssh jarvis@<OpenJarvis-IP>      # şifre: jarvis.env'deki JARVIS_PASSWORD
passwd                           # şifreyi değiştir
git clone -b claude/home-automation-jarvis-rbwn7x https://github.com/sniperx16/sniperx16.git ~/jarvis-ev
cd ~/jarvis-ev && ./openjarvis/kur.sh
```
- [ ] Claude anahtarını yapıştır
- [ ] MCP sorusunu şimdilik **boş geç** (7. adımdan sonra `./openjarvis/kur.sh mcp`)
- [ ] Sonda çıkan **adres ve anahtarı** not et (`./openjarvis/kur.sh anahtar` ile tekrar görülür)

### 7. Home Assistant'a Jarvis'i yükle (≈ 40 dk) · `homeassistant/SESLI-ASISTAN.md`
- [ ] Adım 1: Terminal & SSH → tek komut (`homeassistant/kur.sh`); OpenJarvis adresi/anahtarı, MAC, Wi-Fi'ı gir
- [ ] Adım 2: Whisper (tr, small-int8) ve Piper (tr_TR-fahrettin-medium)
- [ ] Adım 3: Anthropic (Claude) entegrasyonu + Jarvis talimatları
- [ ] Adım 4: "Jarvis" ses hattı, **Komutları öncelikle yerel olarak işle: açık**
- [ ] Adım 5: Göster (Expose): betikler ve cihazlar
- [ ] Adım 6: MCP Server + uzun ömürlü jeton → OpenJarvis VM'inde `./openjarvis/kur.sh mcp`
- [ ] Adım 8: Hologram ve pano

### 8. Test (≈ 15 dk)
Telefondaki Home Assistant uygulamasında Assist (mikrofon) ile ya da hologram ekranına yazarak:
- [ ] "Gece modunu aç" → yerel, anında
- [ ] "Merhaba Jarvis, kendini tanıt" → Claude
- [ ] "Bilgisayarımı aç" → Wake-on-LAN (bilgisayar kapalıyken)
- [ ] "Bu hafta sonu İstanbul'da yapılacak etkinlikleri araştır" → OpenJarvis
- [ ] Hologram: `http://<HA-IP>:8123/local/jarvis/index.html` → BAĞLI, cevaplar altyazıda
- [ ] Proxmox → Datacenter → Backup → gece yedeği görünüyor

## Sonraya kalanlar (parçalar gelince)
- Zigbee çubuğu → `./proxmox/kur.sh zigbee` → ZHA ile sensörleri eşleştir → `ayarlar.json` ve paketteki örnek adları düzelt
- ESP32 ses uydusu → `esphome/BAGLANTI.md` → SESLI-ASISTAN adım 7 ("Hey Jarvis")
- Kamera → Frigate
- HASS.Agent (bilgisayar kontrolü) → Kılavuz bölüm 8.2
