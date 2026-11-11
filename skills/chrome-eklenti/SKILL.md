---
name: chrome-eklenti
description: Manifest V3 Chrome eklentisi kurar, yazar ve tarayıcıda yükleyip test eder. İskelet, ikonlar, storage, background service worker ve content script kalıpları hazır gelir. Kullanıcı "chrome eklentisi yap", "bu siteye eklenti yaz", "tarayıcı eklentisi", "şu sayfada şunu otomatik yapsın", "eklentiye şu özelliği ekle" dediğinde kullan.
---

# Chrome eklentisi (Manifest V3)

Eklenti kullanıcının gösterdiği klasöre kurulur (aşağıda `<eklenti-klasoru>`). Şablonlar bu skill'in `sablon/` klasöründe.

## Önce sor

Kod yazmadan önce netleştir, tahmin etme:

1. **Hangi site?** Tam URL kalıbı lazım (`https://panel.ornek.com/*`). "Bütün sitelerde" cevabı geldiyse bile daralt, `<all_urls>` son çare.
2. **Ne yapacak?** Sayfayı değiştirecek mi (content script), arka planda mı çalışacak (service worker), tıklamayla mı açılacak (popup)?
3. **API anahtarı var mı?** Varsa `chrome.storage.local`'a girilir, koda gömülmez.

## Tip seç

| İhtiyaç | Dosyalar |
|---|---|
| Sayfayı değiştir, ayar yok | `manifest.json` + `content.js` |
| Ayar/anahtar gerek | + `popup.html` + `popup.js` |
| Dış API çağrısı, sekmeler arası iş | + `background.js` |

En basitinden başla. Popup gerekmiyorsa ekleme, dosya sayısı arttıkça hata ayıklama zorlaşıyor.

## Kurulum

```bash
mkdir -p <eklenti-klasoru>
cp <skill-dizini>/sablon/manifest.json <eklenti-klasoru>/
cp <skill-dizini>/sablon/content.js <eklenti-klasoru>/
```

İkonlar (16/48/128 px) `sablon/ikon-uret.sh` ile üretilir, sips kullanır, ek kurulum istemez.

## MV3 tuzakları

Bunlar her seferinde vakit yiyor, baştan doğru yap:

- **`background.js` bir service worker.** Sürekli çalışmaz, birkaç saniye sonra uyur. Global değişkende durum tutma, `chrome.storage.local` kullan.
- **Content script sayfanın JS'ine erişemez.** İzole dünyada çalışır. Sayfanın kendi `window` değişkenine ulaşman gerekiyorsa `<script>` enjekte et ve `postMessage` ile konuş.
- **`host_permissions` olmadan `fetch` sessizce başarısız olur.** Konsolda CORS hatası görürsen önce manifest'e bak.
- **SPA'da content script bir kez çalışır.** React/Vue sitesinde sayfa değişince tekrar çalışmaz. `MutationObserver` kur veya `chrome.webNavigation` dinle.
- **`run_at`:** `document_idle` varsayılan ve genelde doğru. Element bulunamıyorsa `document_end` + bekleme döngüsü dene, `document_start` neredeyse hiç doğru cevap değil.
- Manifest'i değiştirdiysen eklentiyi **yeniden yükle**, sadece sayfayı yenilemek yetmez.

## Test

Yazdıktan sonra tarayıcıda gerçekten çalıştır, "yazdım, çalışması lazım" deme:

1. `chrome://extensions` → Geliştirici modu → Paketlenmemiş öğe yükle → klasörü seç
2. Hedef siteye git, davranışı gör
3. `mcp__claude-in-chrome__read_console_messages` ile hataları oku (content script hataları sayfa konsolunda, background hataları `chrome://extensions` içindeki "service worker" bağlantısında)
4. Ekran görüntüsüyle sonucu doğrula

Bu eklentileri Web Store'a yüklemiyoruz, lokalde çalışıyor. İmzalama/yayınlama adımlarıyla uğraşma.

## Bitirince

Kullanıcı açıkça isterse klasöre kısa bir `BENIOKU.md` yaz (ne yapar, hangi sitede çalışır, ayar gerekiyorsa nasıl girilir). Kullanıcı istemeden dokümantasyon dosyası açma.
