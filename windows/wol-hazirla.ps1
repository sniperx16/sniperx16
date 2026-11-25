# =====================================================================
#  Ev Jarvis'i - Windows bilgisayari uzaktan acma (Wake-on-LAN) hazirligi
#  Kullanim: Baslat'a sag tik -> "Terminal (Yonetici)" ve:
#     Set-ExecutionPolicy -Scope Process Bypass -Force
#     .\wol-hazirla.ps1
#  Ne yapar: Ethernet kartinda "sihirli paketle uyan" ozelligini acar,
#  Hizli Baslatma'yi kapatir ve Home Assistant'a girilecek MAC adresini gosterir.
#  BIOS'taki "Wake on LAN" ayarini ayrica senin acman gerekir.
# =====================================================================
#Requires -RunAsAdministrator
$ErrorActionPreference = 'Stop'

$adaptorler = Get-NetAdapter -Physical | Where-Object { $_.MediaType -eq '802.3' }
if (-not $adaptorler) {
    Write-Host "Kablolu (Ethernet) ag karti bulunamadi. Wake-on-LAN yalnizca kabloyla guvenilir calisir." -ForegroundColor Red
    exit 1
}

foreach ($a in $adaptorler) {
    Write-Host "`n>> $($a.Name)  ($($a.InterfaceDescription))" -ForegroundColor Cyan
    try {
        Set-NetAdapterPowerManagement -Name $a.Name -WakeOnMagicPacket Enabled -ErrorAction Stop
        Write-Host "   Guc yonetimi: sihirli paketle uyanma ACIK" -ForegroundColor Green
    } catch { Write-Host "   Guc yonetimi ayarlanamadi: $($_.Exception.Message)" -ForegroundColor Yellow }
    try {
        Set-NetAdapterAdvancedProperty -Name $a.Name -RegistryKeyword '*WakeOnMagicPacket' -RegistryValue 1 -ErrorAction Stop
        Write-Host "   Gelismis ayar: Wake on Magic Packet ACIK" -ForegroundColor Green
    } catch { Write-Host "   Gelismis ayar bu kartta yok veya degistirilemedi (cogu zaman sorun degil)." -ForegroundColor Yellow }
    & powercfg /deviceenablewake "$($a.InterfaceDescription)" 2>$null | Out-Null
    $mac = ($a.MacAddress -replace '-', ':')
    Write-Host "   MAC adresi: $mac   <-- Home Assistant secrets.yaml icindeki pc_mac" -ForegroundColor White
}

# Hizli Baslatma (Fast Startup) Wake-on-LAN'i bozar -> kapat
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power' -Name 'HiberbootEnabled' -Value 0 -Type DWord
Write-Host "`nHizli Baslatma KAPATILDI." -ForegroundColor Green

Write-Host @"

Son adimlar:
 1. Bilgisayari yeniden baslat, BIOS'a gir ve 'Wake on LAN' / 'Power On by PCI-E' ayarini AC.
 2. Bilgisayari kapat, Home Assistant'tan 'Bilgisayari ac' betigini calistirip dene.
"@
