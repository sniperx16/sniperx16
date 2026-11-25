#!/usr/bin/env bash
# =====================================================================
#  Ev Jarvis'i – Proxmox kurulum betiği
#  Proxmox sunucusunda (jarvis → Shell) root olarak çalıştırılır.
#
#  Kullanım:
#     ./kur.sh depo                 # ücretsiz güncelleme deposu + güncelleme
#     ./kur.sh yedek-disk           # 256 GB diski "yedek" alanı yapar (SİLER!)
#     ./kur.sh ha                   # Home Assistant OS sanal makinesi (VM 100)
#     ./kur.sh jarvis               # Ubuntu + OpenJarvis sanal makinesi (VM 101)
#     ./kur.sh yedekleme            # her gece 03:00 otomatik yedek
#     ./kur.sh zigbee               # Zigbee USB çubuğunu Home Assistant'a bağlar
#     ./kur.sh durum                # özet bilgi
#
#  Her adım tekrar çalıştırılabilir; zaten yapılmışsa atlar.
# =====================================================================
set -euo pipefail

BETIK_DIZINI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_DOSYASI="${BETIK_DIZINI}/../jarvis.env"

yesil() { printf '\e[32m✔ %s\e[0m\n' "$*"; }
sari()  { printf '\e[33m➜ %s\e[0m\n' "$*"; }
kirmizi() { printf '\e[31m✘ %s\e[0m\n' "$*" >&2; }
dur()   { kirmizi "$*"; exit 1; }

[[ $EUID -eq 0 ]] || dur "Bu betik root olarak çalıştırılmalı (Proxmox Shell zaten root'tur)."
command -v qm >/dev/null || dur "Bu bir Proxmox sunucusu değil gibi görünüyor ('qm' bulunamadı)."
[[ -f "$ENV_DOSYASI" ]] || dur "Ayar dosyası yok: $ENV_DOSYASI
Önce: cp jarvis.env.ornek jarvis.env && nano jarvis.env"
# shellcheck source=/dev/null
source "$ENV_DOSYASI"

# Sanal disklerin konacağı depolama alanı (kurulum türüne göre değişir)
depolama_bul() {
  local s
  for s in local-lvm local-zfs; do
    if pvesm status --content images 2>/dev/null | awk 'NR>1{print $1}' | grep -qx "$s"; then
      echo "$s"; return
    fi
  done
  pvesm status --content images | awk 'NR>1 && $1!="yedek"{print $1; exit}'
}
STORAGE="${STORAGE:-$(depolama_bul)}"
[[ -n "$STORAGE" ]] || dur "Sanal disk için depolama alanı bulunamadı."

vm_var_mi() { qm status "$1" >/dev/null 2>&1; }

# ---------------------------------------------------------------------
adim_depo() {
  sari "Güncelleme depoları ayarlanıyor"
  . /etc/os-release
  local kod="$VERSION_CODENAME"
  # Ücretli (enterprise) depoları kapat – aboneliksiz 401 hatası verir
  for f in /etc/apt/sources.list.d/pve-enterprise.list /etc/apt/sources.list.d/pve-enterprise.sources \
           /etc/apt/sources.list.d/ceph.list /etc/apt/sources.list.d/ceph.sources; do
    [[ -f "$f" ]] && mv "$f" "$f.kapali" && echo "  kapatıldı: $f"
  done
  if [[ "$kod" == "bookworm" ]]; then
    echo "deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription" \
      > /etc/apt/sources.list.d/pve-no-subscription.list
  else
    cat > /etc/apt/sources.list.d/pve-no-subscription.sources <<EOF
Types: deb
URIs: http://download.proxmox.com/debian/pve
Suites: ${kod}
Components: pve-no-subscription
Signed-By: /usr/share/keyrings/proxmox-archive-keyring.gpg
EOF
  fi
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade
  apt-get install -y xz-utils usbutils curl
  yesil "Depolar ayarlandı ve sistem güncellendi. Çekirdek güncellendiyse 'reboot' ile yeniden başlat."
}

# ---------------------------------------------------------------------
adim_yedek_disk() {
  if pvesm status 2>/dev/null | awk '{print $1}' | grep -qx yedek; then
    yesil "'yedek' depolaması zaten var, atlanıyor."; return
  fi
  sari "Diskler:"
  lsblk -d -o NAME,SIZE,MODEL,TYPE | grep -E 'disk|NAME'
  # Proxmox'un kurulu olduğu diski bul ve koru
  local sistem_diskleri
  sistem_diskleri="$(pvs --noheadings -o pv_name 2>/dev/null | xargs -r -n1 lsblk -no PKNAME 2>/dev/null | sort -u || true)"
  sistem_diskleri+=" $(lsblk -no PKNAME "$(findmnt -no SOURCE /boot/efi 2>/dev/null || echo /dev/null)" 2>/dev/null || true)"
  # ZFS ile kurulduysa havuzdaki diskler
  sistem_diskleri+=" $(zpool list -vHP 2>/dev/null | awk '$1 ~ /^\/dev\//{print $1}' | xargs -r -n1 lsblk -no PKNAME 2>/dev/null | sort -u | tr '\n' ' ' || true)"
  echo
  echo "Proxmox'un kurulu olduğu disk(ler): ${sistem_diskleri:-?}  (bunlar SEÇİLEMEZ)"
  read -rp "Yedek alanı yapılacak diskin adı (örn. nvme0n1 – yaklaşık 238G olan): " d
  d="${d#/dev/}"
  [[ -b "/dev/$d" ]] || dur "/dev/$d bulunamadı."
  for s in $sistem_diskleri; do [[ "$s" == "$d" ]] && dur "/dev/$d Proxmox'un kurulu olduğu disk! İşlem iptal."; done
  lsblk "/dev/$d"
  kirmizi "/dev/$d üzerindeki HER ŞEY SİLİNECEK (eski Windows dahil)."
  read -rp "Onaylamak için büyük harfle EVET yaz: " onay
  [[ "$onay" == "EVET" ]] || dur "İptal edildi."

  wipefs -a "/dev/$d"
  sgdisk -Z "/dev/$d" >/dev/null
  sgdisk -n1:0:0 -t1:8300 -c1:yedek "/dev/$d" >/dev/null
  partprobe "/dev/$d"; sleep 2
  local p
  p="/dev/$(lsblk -nlo NAME "/dev/$d" | sed -n 2p)"
  mkfs.ext4 -F -L yedek "$p"
  mkdir -p /mnt/yedek
  local uuid; uuid="$(blkid -s UUID -o value "$p")"
  grep -q "$uuid" /etc/fstab || echo "UUID=$uuid /mnt/yedek ext4 defaults,nofail 0 2" >> /etc/fstab
  systemctl daemon-reload
  mount /mnt/yedek
  pvesm add dir yedek --path /mnt/yedek --content backup,images,iso --is_mountpoint yes
  yesil "'yedek' depolaması hazır: /mnt/yedek"
}

# ---------------------------------------------------------------------
adim_ha() {
  if vm_var_mi "$HA_VMID"; then yesil "VM $HA_VMID zaten var, atlanıyor."; return; fi
  sari "Home Assistant OS'un son sürümü bulunuyor"
  local surum
  surum="$(curl -fsSL https://api.github.com/repos/home-assistant/operating-system/releases/latest \
           | grep -m1 '"tag_name"' | cut -d'"' -f4)"
  [[ -n "$surum" ]] || dur "Sürüm bilgisi alınamadı (internet bağlantısını kontrol et)."
  echo "  sürüm: $surum"
  local tmp; tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  curl -fL --progress-bar -o "$tmp/haos.qcow2.xz" \
    "https://github.com/home-assistant/operating-system/releases/download/${surum}/haos_ova-${surum}.qcow2.xz"
  sari "Arşiv açılıyor"
  unxz "$tmp/haos.qcow2.xz"

  sari "VM $HA_VMID oluşturuluyor"
  qm create "$HA_VMID" --name homeassistant --ostype l26 \
    --machine q35 --bios ovmf --cpu host --cores "$HA_CORES" --memory "$HA_RAM_MB" \
    --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-single \
    --agent enabled=1 --onboot 1 --startup order=1 --tablet 0 \
    --description "Ev Jarvis'i – Home Assistant OS ${surum}"
  qm set "$HA_VMID" --efidisk0 "${STORAGE}:1,efitype=4m,pre-enrolled-keys=0"
  qm set "$HA_VMID" --scsi0 "${STORAGE}:0,import-from=$tmp/haos.qcow2,discard=on,ssd=1"
  qm set "$HA_VMID" --boot order=scsi0
  qm resize "$HA_VMID" scsi0 "$HA_DISK"
  qm start "$HA_VMID"
  yesil "Home Assistant başlatıldı. İlk açılış 5–20 dk sürebilir."
  echo "  IP adresini görmek için: Proxmox → $HA_VMID → Summary (birkaç dk sonra) ya da Console."
  echo "  Sonra modemden bu IP'yi sabitle (DHCP rezervasyonu) ve http://<IP>:8123 adresini aç."
}

# ---------------------------------------------------------------------
adim_jarvis() {
  if vm_var_mi "$JARVIS_VMID"; then yesil "VM $JARVIS_VMID zaten var, atlanıyor."; return; fi
  local img=/var/lib/vz/template/iso/noble-server-cloudimg-amd64.img
  if [[ ! -f "$img" ]]; then
    sari "Ubuntu 24.04 bulut imajı indiriliyor"
    mkdir -p "$(dirname "$img")"
    curl -fL --progress-bar -o "$img.part" \
      https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img
    mv "$img.part" "$img"
  fi

  # cloud-init ek ayarları (misafir ajanı + şifreyle SSH)
  local snip_dir=/var/lib/vz/snippets
  mkdir -p "$snip_dir"
  local icerik
  icerik="$(pvesm config local 2>/dev/null | awk '/content/{print $2}')"
  if [[ "$icerik" != *snippets* ]]; then
    pvesm set local --content "${icerik:+$icerik,}snippets"
  fi
  cat > "$snip_dir/jarvis-vendor.yaml" <<'EOF'
#cloud-config
ssh_pwauth: true
timezone: Europe/Istanbul
package_update: true
package_upgrade: true
packages:
  - qemu-guest-agent
  - curl
  - git
  - ca-certificates
  - openssl
runcmd:
  - systemctl enable --now qemu-guest-agent
EOF

  sari "VM $JARVIS_VMID oluşturuluyor"
  qm create "$JARVIS_VMID" --name openjarvis --ostype l26 \
    --cpu host --cores "$JARVIS_CORES" --memory "$JARVIS_RAM_MB" --balloon 0 \
    --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-single \
    --agent enabled=1 --onboot 1 --startup order=2 \
    --serial0 socket --vga serial0 \
    --description "Ev Jarvis'i – Ubuntu 24.04 + OpenJarvis"
  qm set "$JARVIS_VMID" --scsi0 "${STORAGE}:0,import-from=$img,discard=on,ssd=1"
  qm set "$JARVIS_VMID" --ide2 "${STORAGE}:cloudinit" --boot order=scsi0
  qm resize "$JARVIS_VMID" scsi0 "$JARVIS_DISK"
  qm set "$JARVIS_VMID" \
    --ciuser "$JARVIS_USER" --cipassword "$JARVIS_PASSWORD" \
    --ipconfig0 "ip=${JARVIS_IP}/${CIDR},gw=${GATEWAY}" \
    --nameserver "$DNS" --searchdomain home \
    --cicustom "vendor=local:snippets/jarvis-vendor.yaml"
  if [[ -f /root/.ssh/authorized_keys ]]; then
    qm set "$JARVIS_VMID" --sshkeys /root/.ssh/authorized_keys || true
  fi
  qm start "$JARVIS_VMID"
  yesil "OpenJarvis sanal makinesi başlatıldı (ilk açılışta güncellemeler 3–5 dk sürer)."
  echo "  Bağlan:  ssh ${JARVIS_USER}@${JARVIS_IP}   (şifre: jarvis.env içindeki JARVIS_PASSWORD)"
  echo "  Sonra:   openjarvis/kur.sh betiğini VM içinde çalıştır (README'ye bak)."
}

# ---------------------------------------------------------------------
adim_yedekleme() {
  pvesm status 2>/dev/null | awk '{print $1}' | grep -qx yedek \
    || dur "Önce './kur.sh yedek-disk' çalıştır."
  if pvesh get /cluster/backup --output-format json 2>/dev/null | grep -q '"storage":"yedek"'; then
    yesil "Gece yedeği zaten tanımlı, atlanıyor."; return
  fi
  pvesh create /cluster/backup \
    --schedule "03:00" --storage yedek --all 1 \
    --mode snapshot --compress zstd \
    --prune-backups "keep-last=7" --enabled 1 \
    --comment "Ev Jarvis'i gece yedegi"
  yesil "Her gece 03:00'te tüm sanal makineler yedeklenecek (son 7 gün tutulur)."
}

# ---------------------------------------------------------------------
adim_zigbee() {
  vm_var_mi "$HA_VMID" || dur "Önce Home Assistant VM'ini kur."
  sari "USB cihazları:"
  lsusb
  local id=""
  # Bilinen Zigbee çubukları: Sonoff ZBDongle-E (CH9102), ZBDongle-P (CP210x), SkyConnect/ZBT-1
  for bilinen in 1a86:55d4 10c4:ea60 303a:831a; do
    if lsusb | grep -qi "$bilinen"; then id="$bilinen"; break; fi
  done
  if [[ -z "$id" ]]; then
    read -rp "Zigbee çubuğunun ID'si (lsusb satırındaki xxxx:yyyy): " id
  fi
  [[ "$id" =~ ^[0-9a-fA-F]{4}:[0-9a-fA-F]{4}$ ]] || dur "Geçersiz ID: $id"
  qm set "$HA_VMID" --usb0 "host=$id"
  yesil "Zigbee çubuğu ($id) VM $HA_VMID'ye bağlandı."
  sari "Home Assistant'ı yeniden başlatıyorum (VM)"
  qm reboot "$HA_VMID" || true
  echo "  Sonra Home Assistant → Ayarlar → Cihazlar ve Hizmetler → ZHA (otomatik bulunur)."
}

# ---------------------------------------------------------------------
adim_durum() {
  echo "Depolama: $STORAGE"
  pvesm status
  echo; qm list
}

case "${1:-}" in
  depo)        adim_depo ;;
  yedek-disk)  adim_yedek_disk ;;
  ha)          adim_ha ;;
  jarvis)      adim_jarvis ;;
  yedekleme)   adim_yedekleme ;;
  zigbee)      adim_zigbee ;;
  durum)       adim_durum ;;
  *) sed -n '2,16p' "$0"; exit 1 ;;
esac
