# Çalışan Rehberi (Android, çevrimdışı)

Çalışan listesini (ad, TC no, telefon, adres, birim…) telefonda arayıp görüntüleyen, **internet izni olmayan** uygulama.

## Kullanım
1. Excel listenizi **CSV (UTF-8, noktalı virgül veya virgül)** olarak kaydedin. Başlıklar: `Ad Soyad; TC No; Telefon; Adres; Birim; Görev; E-posta; Not`
   (`Ad` + `Soyad` ayrı sütun da olabilir; örnek: `ornek.csv`).
2. Telefona gönderin (USB/Drive), uygulamada menü → **CSV içe aktar**.
3. Üstteki kutudan ad, TC, telefon veya birime göre arayın (Türkçe harf/büyük-küçük harf farkı önemsiz).
4. Kayda dokununca detay; **Ara / SMS / Haritada göster / E-posta** düğmeleri. Alana uzun basınca kopyalar.

## Güvenlik (TC no kişisel veridir – KVKK)
- Açılışta parmak izi / PIN / desen sorulur; arka plana geçince tekrar kilitlenir.
- Ekran görüntüsü ve son uygulamalar önizlemesi kapalı, yedekleme (`allowBackup`) kapalı, internet izni yok.
- Telefonda ekran kilidi ve disk şifrelemesi (modern Android’de varsayılan) açık olsun. CSV dosyasını içe aktardıktan sonra telefondan/Drive’dan silin.

## APK nasıl alınır
GitHub → **Actions → Calisan Rehberi APK → Run workflow**; bitince *Artifacts* içinden `app-debug.apk` indirilir, telefona kurulur
(“bilinmeyen kaynaklardan yükleme” izni gerekir). Ya da Android Studio ile `calisan-rehberi` klasörünü açıp çalıştırın.
