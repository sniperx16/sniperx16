#!/usr/bin/env bash
# =====================================================================
#  Ev Jarvis'i – OpenJarvis kurulumu
#  Ubuntu sanal makinesinde (VM 101), "jarvis" kullanıcısıyla çalıştırılır:
#     ssh jarvis@<JARVIS_IP>
#     git clone <bu repo> jarvis-ev && cd jarvis-ev
#     ./openjarvis/kur.sh            # hepsini sırayla yapar
#
#  Alt komutlar:
#     ./openjarvis/kur.sh mcp        # Home Assistant bağlantısını (yeniden) ayarla
#     ./openjarvis/kur.sh test       # çalışıyor mu kontrol et
#     ./openjarvis/kur.sh anahtar    # Home Assistant'a girilecek API anahtarını göster
#     ./openjarvis/kur.sh guncelle   # OpenJarvis'i güncelle
# =====================================================================
set -euo pipefail

DIZIN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OJ="$HOME/.openjarvis"
ENVF=/etc/openjarvis/env
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

yesil() { printf '\e[32m✔ %s\e[0m\n' "$*"; }
sari()  { printf '\e[33m➜ %s\e[0m\n' "$*"; }
dur()   { printf '\e[31m✘ %s\e[0m\n' "$*" >&2; exit 1; }

[[ $EUID -ne 0 ]] || dur "root olarak değil, 'jarvis' kullanıcısıyla çalıştır (gerekince sudo şifresi sorulur)."

# ---------------------------------------------------------------------
gizli_anahtarlar() {
  if sudo test -f "$ENVF"; then yesil "$ENVF zaten var."; return; fi
  sari "Claude API anahtarı gerekiyor (console.anthropic.com → API Keys)."
  local ak=""
  while [[ ! "$ak" =~ ^sk-ant- ]]; do
    read -rsp "Claude API anahtarını yapıştır (ekranda görünmez): " ak; echo
    [[ "$ak" =~ ^sk-ant- ]] || echo "  Anahtar 'sk-ant-' ile başlamalı, tekrar dene."
  done
  local ojk; ojk="$(openssl rand -hex 32)"
  sudo mkdir -p /etc/openjarvis
  printf 'ANTHROPIC_API_KEY=%s\nOPENJARVIS_API_KEY=%s\n' "$ak" "$ojk" | sudo tee "$ENVF" >/dev/null
  sudo chown root:"$USER" "$ENVF"
  sudo chmod 640 "$ENVF"
  yesil "Anahtarlar $ENVF dosyasına kaydedildi (sadece root ve $USER okuyabilir)."
}

ortam_yukle() {
  set -a
  # shellcheck disable=SC1090
  source <(sudo cat "$ENVF")
  set +a
}

# ---------------------------------------------------------------------
openjarvis_kur() {
  if [[ -x "$OJ/.venv/bin/jarvis" ]]; then
    yesil "OpenJarvis zaten kurulu."
  else
    sari "OpenJarvis resmi kurulum betiği çalışıyor (3–10 dk)"
    curl -fsSL https://open-jarvis.github.io/OpenJarvis/install.sh | bash
  fi
  [[ -x "$OJ/.venv/bin/jarvis" ]] || dur "Kurulum tamamlanamadı: $OJ/.venv/bin/jarvis yok."

  sari "API sunucusu ve Claude (bulut) eklentileri kuruluyor"
  command -v uv >/dev/null || dur "'uv' bulunamadı; yeni bir terminal açıp tekrar dene."
  uv pip install --python "$OJ/.venv/bin/python" -e "$OJ/src[server,inference-cloud]"
  yesil "OpenJarvis hazır."
}

# ---------------------------------------------------------------------
ollama_hazirla() {
  command -v ollama >/dev/null || { sari "Ollama kuruluyor"; curl -fsSL https://ollama.com/install.sh | sh; }
  if systemctl list-unit-files ollama.service >/dev/null 2>&1 && systemctl cat ollama.service >/dev/null 2>&1; then
    sudo systemctl enable --now ollama
  else
    # Kullanıcı servisi olarak kurulduysa oturum kapansa da çalışsın
    sudo loginctl enable-linger "$USER"
  fi
  sari "Yerel yedek model indiriliyor: qwen3:8b (~5 GB, bir kerelik)"
  ollama pull qwen3:8b
  yesil "Yerel model hazır (internet yokken kullanılır)."
}

# ---------------------------------------------------------------------
ayarlari_yaz() {
  mkdir -p "$OJ"
  cp "$DIZIN/jarvis-kisilik.md" "$OJ/jarvis-kisilik.md"
  if [[ -f "$OJ/config.toml" && ! -f "$OJ/config.toml.kurulum-oncesi" ]]; then
    cp "$OJ/config.toml" "$OJ/config.toml.kurulum-oncesi"
  fi
  sed "s#__HOME__#$HOME#g" "$DIZIN/config.toml.sablon" > "$OJ/config.toml"
  [[ -f "$OJ/mcp-servers.json" ]] || { echo '[]' > "$OJ/mcp-servers.json"; chmod 600 "$OJ/mcp-servers.json"; }
  yesil "Ayarlar yazıldı: $OJ/config.toml (eskisi: config.toml.kurulum-oncesi)"
}

# ---------------------------------------------------------------------
mcp_ayarla() {
  sari "Home Assistant bağlantısı (MCP)"
  echo "  Home Assistant'ta önce: Ayarlar → Cihazlar ve Hizmetler → Entegrasyon Ekle → 'Model Context Protocol Server'"
  echo "  Sonra: profil → Güvenlik → Uzun ömürlü erişim jetonları → Jeton oluştur (ad: openjarvis)"
  local ip tok
  read -rp "Home Assistant IP adresi (örn. 192.168.1.52, boş bırakırsan atlanır): " ip
  [[ -n "$ip" ]] || { sari "MCP atlandı. Sonra './openjarvis/kur.sh mcp' ile ekleyebilirsin."; return; }
  read -rsp "Uzun ömürlü jeton (ekranda görünmez): " tok; echo
  [[ -n "$tok" ]] || dur "Jeton boş olamaz."
  umask 077
  python3 - "$ip" "$tok" > "$OJ/mcp-servers.json" <<'PY'
import json, sys
ip, tok = sys.argv[1], sys.argv[2]
json.dump([{"name": "homeassistant", "url": f"http://{ip}:8123/api/mcp", "token": tok}],
          sys.stdout, indent=2)
PY
  chmod 600 "$OJ/mcp-servers.json"
  if curl -fsS -o /dev/null -m 5 -H "Authorization: Bearer $tok" "http://$ip:8123/api/"; then
    yesil "Home Assistant'a erişim başarılı."
  else
    printf '\e[31m✘ %s\e[0m\n' "Home Assistant'a ulaşılamadı veya jeton hatalı. IP/jetonu kontrol edip './openjarvis/kur.sh mcp' çalıştır." >&2
  fi
  if systemctl is-active --quiet openjarvis; then sudo systemctl restart openjarvis; fi
}

# ---------------------------------------------------------------------
servis_kur() {
  sari "OpenJarvis arka plan servisi kuruluyor"
  sudo tee /etc/systemd/system/openjarvis.service >/dev/null <<EOF
[Unit]
Description=Ev Jarvis'i - OpenJarvis API sunucusu
After=network-online.target ollama.service
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME
Environment=HOME=$HOME
Environment=PATH=$HOME/.local/bin:$OJ/.venv/bin:/usr/local/bin:/usr/bin:/bin
EnvironmentFile=$ENVF
ExecStart=$OJ/.venv/bin/jarvis serve --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full

[Install]
WantedBy=multi-user.target
EOF
  sudo systemctl daemon-reload
  sudo systemctl enable --now openjarvis
  yesil "Servis çalışıyor: sudo systemctl status openjarvis"
}

# ---------------------------------------------------------------------
test_et() {
  ortam_yukle
  sari "Sunucu bekleniyor"
  for _ in $(seq 1 30); do
    curl -fsS -m 3 -o /dev/null -H "Authorization: Bearer $OPENJARVIS_API_KEY" http://127.0.0.1:8000/v1/models && break
    sleep 2
  done
  curl -fsS -m 3 -H "Authorization: Bearer $OPENJARVIS_API_KEY" http://127.0.0.1:8000/v1/models >/dev/null \
    || dur "Sunucu cevap vermiyor. Günlük: journalctl -u openjarvis -n 50"
  yesil "API sunucusu çalışıyor."
  sari "Jarvis'e Türkçe bir soru soruluyor"
  curl -fsS -m 120 http://127.0.0.1:8000/v1/chat/completions \
    -H "Authorization: Bearer $OPENJARVIS_API_KEY" -H "Content-Type: application/json" \
    -d '{"model":"claude-sonnet-5-5","messages":[{"role":"user","content":"Merhaba Jarvis, kendini bir cümleyle tanıt."}]}' \
    | python3 -c 'import json,sys; print("  Jarvis:", json.load(sys.stdin)["choices"][0]["message"]["content"])' \
    || dur "Cevap alınamadı. Günlük: journalctl -u openjarvis -n 50"
  yesil "Test başarılı."
}

anahtar_goster() {
  ortam_yukle
  echo "Home Assistant secrets.yaml için:"
  echo "  openjarvis_url: http://$(hostname -I | awk '{print $1}'):8000/v1/chat/completions"
  echo "  openjarvis_auth: Bearer $OPENJARVIS_API_KEY"
}

guncelle() {
  "$OJ/.venv/bin/jarvis" self-update --yes
  uv pip install --python "$OJ/.venv/bin/python" -e "$OJ/src[server,inference-cloud]"
  sudo systemctl restart openjarvis
  yesil "Güncellendi."
}

case "${1:-hepsi}" in
  hepsi)
    gizli_anahtarlar
    openjarvis_kur
    ollama_hazirla
    ayarlari_yaz
    mcp_ayarla
    servis_kur
    test_et
    echo
    anahtar_goster
    ;;
  mcp)      mcp_ayarla ;;
  test)     test_et ;;
  anahtar)  anahtar_goster ;;
  guncelle) guncelle ;;
  *) sed -n '2,15p' "$0"; exit 1 ;;
esac
