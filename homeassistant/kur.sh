#!/usr/bin/env bash
# =====================================================================
#  Ev Jarvis'i – Home Assistant kurulumu
#  Home Assistant → Ayarlar → Eklentiler → "Terminal & SSH" eklentisinde çalıştır:
#
#    curl -fsSL https://raw.githubusercontent.com/sniperx16/sniperx16/claude/home-automation-jarvis-rbwn7x/homeassistant/kur.sh | bash
#
#  Ne yapar:
#   1. Jarvis paketini   → /config/packages/jarvis.yaml
#   2. Hologram arayüzünü → /config/www/jarvis/   (ayarlar.json'ın varsa korunur)
#   3. Panoyu             → /config/jarvis-pano.yaml (arayüzden eklenir, README'ye bak)
#   4. configuration.yaml → "packages" satırını ekler (yoksa)
#   5. secrets.yaml       → eksik anahtarları sorar ve ekler
#   6. Yapılandırmayı kontrol eder, sorun yoksa Home Assistant'ı yeniden başlatır
#  Tekrar çalıştırmak güvenlidir (güncelleme için de kullanılır).
# =====================================================================
set -euo pipefail

REPO="https://github.com/sniperx16/sniperx16.git"
DAL="claude/home-automation-jarvis-rbwn7x"

yesil() { printf '\e[32m✔ %s\e[0m\n' "$*"; }
sari()  { printf '\e[33m➜ %s\e[0m\n' "$*"; }
dur()   { printf '\e[31m✘ %s\e[0m\n' "$*" >&2; exit 1; }

# Yapılandırma klasörü (eklenti sürümüne göre /config veya /homeassistant)
CFG="${HA_CONFIG:-}"
if [[ -z "$CFG" ]]; then
  for d in /config /homeassistant; do [[ -f "$d/configuration.yaml" ]] && { CFG="$d"; break; }; done
fi
[[ -n "$CFG" && -f "$CFG/configuration.yaml" ]] || dur "configuration.yaml bulunamadı. Bu betiği Home Assistant 'Terminal & SSH' eklentisinde çalıştır."

# Kaynak dosyalar (test için JARVIS_KAYNAK ile yerel klasör verilebilir)
if [[ -n "${JARVIS_KAYNAK:-}" ]]; then
  KAYNAK="$JARVIS_KAYNAK"
else
  command -v git >/dev/null || dur "git bulunamadı (Terminal & SSH eklentisinde bulunur)."
  KAYNAK="/tmp/jarvis-ev"
  if [[ -d "$KAYNAK/.git" ]]; then
    sari "Repo güncelleniyor"; git -C "$KAYNAK" fetch -q --depth 1 origin "$DAL" && git -C "$KAYNAK" reset -q --hard FETCH_HEAD
  else
    sari "Repo indiriliyor"; rm -rf "$KAYNAK"; git clone -q --depth 1 -b "$DAL" "$REPO" "$KAYNAK"
  fi
fi
HAK="$KAYNAK/homeassistant"
[[ -f "$HAK/packages/jarvis.yaml" ]] || dur "Kaynak dosyalar eksik: $HAK"

# 1) paket
mkdir -p "$CFG/packages"
cp "$HAK/packages/jarvis.yaml" "$CFG/packages/jarvis.yaml"
yesil "Paket kopyalandı: $CFG/packages/jarvis.yaml"

# 2) hologram (kullanıcının ayarlar.json'ını ezme)
mkdir -p "$CFG/www/jarvis"
if [[ -f "$CFG/www/jarvis/ayarlar.json" ]]; then
  cp "$CFG/www/jarvis/ayarlar.json" /tmp/jarvis-ayarlar.json
fi
cp -r "$HAK/www/jarvis/." "$CFG/www/jarvis/"
if [[ -f /tmp/jarvis-ayarlar.json ]]; then
  cp "$HAK/www/jarvis/ayarlar.json" "$CFG/www/jarvis/ayarlar.json.yeni"
  mv /tmp/jarvis-ayarlar.json "$CFG/www/jarvis/ayarlar.json"
  yesil "Hologram güncellendi (senin ayarlar.json'ın korundu; yeni örnek: ayarlar.json.yeni)"
else
  yesil "Hologram kopyalandı: $CFG/www/jarvis/"
fi

# 3) pano
cp "$HAK/jarvis-pano.yaml" "$CFG/jarvis-pano.yaml"
yesil "Pano dosyası: $CFG/jarvis-pano.yaml"

# 4) configuration.yaml → packages
CONF="$CFG/configuration.yaml"
if grep -qE '^[[:space:]]+packages:' "$CONF"; then
  yesil "configuration.yaml: packages zaten tanımlı"
else
  cp "$CONF" "$CONF.jarvis-yedek"
  if grep -qE '^homeassistant:[[:space:]]*$' "$CONF"; then
    awk '{print} /^homeassistant:[[:space:]]*$/ && !d {print "  packages: !include_dir_named packages"; d=1}' "$CONF" > "$CONF.tmp" && mv "$CONF.tmp" "$CONF"
  else
    printf '\nhomeassistant:\n  packages: !include_dir_named packages\n' >> "$CONF"
  fi
  yesil "configuration.yaml'a packages eklendi (yedek: configuration.yaml.jarvis-yedek)"
fi

# 5) secrets.yaml → eksik anahtarlar
SEC="$CFG/secrets.yaml"; touch "$SEC"
sor() {  # anahtar, açıklama, örnek
  local k="$1" aciklama="$2" ornek="$3" v=""
  if grep -qE "^$k:" "$SEC"; then return; fi
  if [[ -t 0 || -e /dev/tty ]]; then
    { read -rp "$aciklama [boş bırak → $ornek]: " v </dev/tty; } 2>/dev/null || true
  fi
  v="${v:-$ornek}"
  printf '%s: "%s"\n' "$k" "${v//\"/\\\"}" >> "$SEC"
}
sari "Gizli ayarlar (secrets.yaml) – sonradan File editor ile değiştirebilirsin"
sor openjarvis_url  "OpenJarvis adresi (openjarvis/kur.sh anahtar çıktısı)" "http://192.168.1.51:8000/v1/chat/completions"
sor openjarvis_auth "OpenJarvis anahtarı, 'Bearer ' ile birlikte"           "Bearer BURAYA_OPENJARVIS_API_ANAHTARI"
sor pc_mac          "Windows bilgisayarın MAC adresi"                         "AA:BB:CC:DD:EE:FF"
sor wifi_ssid       "Ev Wi-Fi adı (ses uydusu için)"                          "EV_WIFI_ADI"
sor wifi_password   "Ev Wi-Fi şifresi"                                        "EV_WIFI_SIFRESI"
chmod 600 "$SEC" 2>/dev/null || true
yesil "secrets.yaml hazır"

# 6) kontrol + yeniden başlat
if [[ "${HA_CLI:-1}" == "1" ]] && command -v ha >/dev/null; then
  sari "Yapılandırma kontrol ediliyor"
  if ha core check; then
    sari "Home Assistant yeniden başlatılıyor (1–2 dk)"
    ha core restart
    yesil "Tamam. Hologram: http://<HA-IP>:8123/local/jarvis/index.html"
  else
    dur "Yapılandırmada hata var; yukarıdaki mesajı Claude'a gönder. Yedek: configuration.yaml.jarvis-yedek"
  fi
else
  sari "Kontrol atlandı. Geliştirici Araçları → YAML → Yapılandırmayı kontrol et → Yeniden başlat."
fi
