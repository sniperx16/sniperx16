# Kaynaklar ve lisanslar

- **3D kafa modeli** (`model/LeePerrySmith.glb`): "Infinite, 3D Head Scan" – Lee Perry-Smith,
  [Creative Commons Attribution 3.0 Unported](https://creativecommons.org/licenses/by/3.0/).
  Kaynak: www.triplegangers.com / www.ir-ltd.net (three.js örnekleri üzerinden). Ayrıntı: `model/LeePerrySmith_License.txt`
- **three.js** r187 (`lib/`): MIT lisansı – `lib/THREE-LICENSE.txt`

# Nasıl açılır
- **Home Assistant'ta:** `homeassistant/kur.sh` bu klasörü `/config/www/jarvis/` içine kopyalar.
  Adres: `http://<HA-IP>:8123/local/jarvis/index.html` (ayrıntı: `homeassistant/SESLI-ASISTAN.md` 8. adım).
- **Bilgisayarda denemek için (tanıtım modu):** bu klasörde `python -m http.server 8000` çalıştır,
  `http://localhost:8000/index.html?demo=1` aç. (Dosyaya çift tıklamak çalışmaz; tarayıcı güvenliği engeller.)

Adres parametreleri: `?demo=1` tanıtım · `?ha=http://IP:8123` başka adresteki HA · `?durum=dinliyor` sabit durum.
