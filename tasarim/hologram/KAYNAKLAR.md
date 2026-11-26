# Kaynaklar ve lisanslar

- **3D kafa modeli** (`model/LeePerrySmith.glb`): "Infinite, 3D Head Scan" – Lee Perry-Smith,
  [Creative Commons Attribution 3.0 Unported](https://creativecommons.org/licenses/by/3.0/).
  Kaynak: www.triplegangers.com / www.ir-ltd.net (three.js örnekleri üzerinden). Ayrıntı: `model/LeePerrySmith_License.txt`
- **three.js** r187 (`lib/`): MIT lisansı – `lib/THREE-LICENSE.txt`

# Nasıl açılır
Tarayıcı güvenliği nedeniyle dosyaya çift tıklayarak değil, bir web sunucusu üzerinden açılmalı:

- **Home Assistant'ta (kalıcı kullanım):** `hologram` klasörünü `/config/www/jarvis/` içine kopyala,
  sonra `http://<HA-IP>:8123/local/jarvis/index.html` adresini aç (tablette tam ekran).
- **Bilgisayarda denemek için:** klasörde `python -m http.server 8000` çalıştır,
  `http://localhost:8000/index.html` aç.

Belirli bir durum için adresin sonuna `?durum=dinliyor` (veya `bekliyor`, `dusunuyor`, `konusuyor`) ekle.
