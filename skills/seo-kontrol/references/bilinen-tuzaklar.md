# Ölçüm tuzakları

- HTTP 200, beklenen dosyanın geldiğini kanıtlamaz. HTML yedeği/WAF yanıtını favicon,
  manifest, sitemap ve feed sanma. XML/JSON kökü, dosya imzası ve kesilme durumunu doğrula.
- Sitemap index'teki lastmod alt dosyanın değişimidir. URL sayfalarının lastmod alanları
  ayrıca incelenir; güncellik tarihini her istekte bugüne çevirme. İlk birkaç alt dosya tüm site değildir.
- Sitemap'te yalnız canonical, indekslenmesi istenen ve erişilebilir sayfalar bulunmalı;
  sayfa örnekleriyle doğrula. Sitemap yokluğu Google'a giriş engeli değildir.
- robots.txt 429/5xx/zaman aşımı başarılı izin ölçümü değildir. Yol ve sorgu bazında bak;
  Allow/Disallow önceliği, jokerler, aynı ajanın birleşen grupları önemlidir.
- UA taklidi gerçek doğrulanmış bot IP'si değildir. 403, bot kesin engelli demek değildir;
  200 de botun gerçek içeriği gördüğünü kanıtlamaz. WAF'da kör Allow önermekten kaçın.
- Analitik yalnız canlıda veya onay sonrası yüklenebilir. Kodda alan varlığı, kimliğin dolu
  olması ve olayın gerçekten gönderilmesi üç ayrı bulgudur. Harici JS ve GTM'yi hesaba kat.
- `default` kelimesi Consent Mode v2 kanıtı değildir; dört sinyal ve güncelleme sırası incelenir.
  Mevzuata uyum sonucunu regex veya tek etiket üzerinden verme.
- API'deki alanın şablonda gerçekten basıldığını ve yanıt anahtarının doğru okunduğunu doğrula.
  Sessiz catch boş sitemap/feed/içerik üretebilir. Yalnız yetkili projede inceleme yap.
- Blade'de `{{ e($x) }}` çift kaçış üretebilir; görünür metinle birlikte meta alanlarını da incele.
- Başlık/açıklama uzunluğu kalite veya sıralama değildir. Birden çok H1 ve ID içeren URL
  tek başına SEO hatası değildir. Sırf kontrolü yeşile çevirmek için URL taşıma.
- Otomatik barkod GTIN değildir. Kontrol basamağı geçse bile gerçek üretici/GS1 kimliği
  olduğunu göstermez; uydurma MPN veya identifier_exists=no yedeği önerme.
- @graph, iç içe mainEntity, hasVariant, isVariantOf ve @id referanslarını hesaba kat.
  Ayrışan JSON, geçerli Google zengin sonuç anlamına gelmez; uygunluk tür bazında incelenir.
- Fiyat, stok, kondisyon, kargo, iade süresi ve fiyat geçerlilik tarihi gerçek veriden gelir.
  UsedCondition yerine NewCondition, rastgele 14 gün veya yıl sonu tarihi basma.
- Boş alt bilinçli dekoratif görsel olabilir. İlk/LCP görselini lazy yapmak ters etki yaratabilir.
- "Ölçülemedi" eksik veya gereksiz değildir. Uygulanamaz için işletmeye bağlı gerekçe gerekir.
  Örneklem, ortam, erişilemeyen sayfa ve boyut/istek sınırları raporda görünür olmalıdır.
- Yerel veritabanı canlının kopyası olmayabilir; içerik doluluk sorgusunda önce şemayı doğrula,
  kişisel/saklı alanları dökmeden toplu sayı al. Başka projeye ait tablo adlarını varsayma.
