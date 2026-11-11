# SEO altyapısı standardı (uygulama kipi)

Bir sitede SEO altyapısını kurarken ya da düzeltirken uyulacak genel standart. Her projeye
(Laravel ya da başka çatı) uyar; "Örnek uygulama" satırları bir uygulamayı gösterir, ad
kopyalamak için değildir. Projenin kendi AGENTS.md'si ve kullanıcı kararı bu dosyayı ezer.

Kaynak: çalışan bir Laravel e-ticaret projesinin kuralları, kodu ve testleri.
Google'a dayanan her iddia [resmî kaynaklarla](resmi-kaynaklar.md) ve güncel resmî sayfayla
doğrulanır. Buradaki karakter sınırı, örnek sayı ya da kalıp evrensel Google eşiği değildir.

## Genel ilkeler

| İlke | Uygulama |
|---|---|
| Tek kaynak | Firma bilgisi, adres, fiyat, kargo/iade süresi, ürün kimliği, kanonik yol tek sınıftan okunur; şema, feed, llms ve sayfa aynı kaynağı kullanır. |
| Uydurma yok | GTIN, MPN, puan, yorum, açıklama, tarih, kondisyon, politika gerçek veriden gelir; yoksa alan basılmaz. |
| Sunum katmanı | Meta ve JSON-LD sunucu sınıfında hazırlanır, şablon yalnız basar. Şablonda iş kuralı olmaz. |
| Bayat veri yok | Önbelleklenen her SEO çıktısının düşürüldüğü olay yazılır; toplu yazma sonrası elle düşürülür. |
| Kural = test | Aşağıdaki her başlığın "Testle koru" satırı uygulanır; ucuz ölçülebilen kural mimari testle korunur. |
| Kullanıcı kararı | Eğitim botu izni, toplu AI metni, reklam etiketleri, URL değişikliği iş kararıdır; sorulur, kendiliğinden yapılmaz. |
| Dayanak türü | Rapor ve kod yorumunda resmî gereksinim / resmî öneri / platform özelliği / deneyim ayrımı korunur. |

## 1. URL, slug ve 301 koruması

- Taşınan siteden gelen adresler korunur; her eski adres için kalıcı (301/308) yönlendirme kaydı tutulur.
- Yönlendirme 404'e düşen istekte devreye girer; canlı sayfayı gölgelemez.
- Slug değişince eski adres yeni adrese kendiliğinden 301 olur. Zincir oluşmaz (eskiye işaret edenler
  yeni hedefe çekilir), geri alınan ad döngü yaratmaz, slug dışı değişiklik kayıt açmaz.
- Bir içeriğin tek adresi vardır; ikinci adres (ör. `/kurumsal/x` ile `/x`) 301 ile tek adrese döner,
  kanonik, breadcrumb, sitemap ve panel bağlantısı aynı yol üreticisinden gelir.
- Sırf puan için URL değiştirilmez; dış kaynaktan (XML) gelen ad ve adres kullanıcı kararı olmadan bozulmaz.

Örnek uygulama: `yonlendirmeler` tablosu + `YonlendirmeKontrolu` middleware, `SlugYonlendirici`
(`SeoGozlemcisi::updated` çağırır), `VitrinAdresi::yol`, `Sayfa::yol()` / `Sayfa::OZEL_YOLLAR`.
Testle koru: slug değişimi 301, zincir yok, döngü yok, slug dışı değişiklik kayıt açmaz
(`SlugYonlendirmeTest`).

## 2. Kanonik ve sayfalama

- Kanonik mutlak adrestir; sıralama ve süzgeç parametreleri kanoniğe girmez.
- Listenin 1. sayfası parametresizdir; 2. ve sonraki sayfa (`?page=N`) kendine kanonik verir,
  1. sayfaya değil. Sayfalı başlık kopya olmasın diye "Ad - Sayfa N" biçimi kullanılır.
- Kasıtlı noindex (giriş, hesap, arama, sepet) ayrı sabit robots değeriyle basılır.

Örnek uygulama: `SeoSunum::sayfaliYol`, `sayfaliBaslik`, `ROBOTS_INDEKSLE` / `ROBOTS_INDEKSLEME`.
Testle koru: 2. sayfa kendine kanonik, 1. sayfa süzgeçsiz kanonik (`SemaVeMetaSayfaTest`).

## 3. Head, meta, Open Graph, paylaşım görseli, favicon

| Parça | Kural |
|---|---|
| title | "Sayfa \| Site" gibi tek kalıp; içe aktarılan eski sonekler bu kalıba çevrilir. |
| meta description | Kayıttaki SEO açıklaması, yoksa kısa açıklama; ikisi de boşsa davranış kullanıcıya sorulur (şablonla sahte açıklama üretilmez). |
| robots | İndekslenen sayfada `max-image-preview:large` önerilir (resmî öneri değil, platform özelliği). |
| OG / X | og:image mutlak adres, width/height/alt ile; https'te `og:image:secure_url`; X hesabı varsa `twitter:site` kullanıcı adıyla. Ürün sayfasında `og:type=product` ve fiyat etiketleri (fiyat gizliyse yok). |
| Paylaşım görseli | Varsayılan 1200x630, kırpılmadan sığdırılır; panelden yüklenebilir, yoksa logodan üretilir. Boyut sınırı (ör. 300 KB) deneyime dayalıdır. |
| Favicon seti | Kaynak görselden türetilir: `.ico` (16/32/48 gömülü), PNG kare ölçüler, `apple-touch-icon` 180 saydamsız, `site.webmanifest`, theme-color. Statik kopya `public/` altına konmaz; kaynak değişince sürüm adı değişir, eski set silinir. |
| Parçalı head | meta, simgeler, doğrulama kodları ve analitik ayrı parçalardır; her sayfa aynı parçaları kullanır. |

Örnek uygulama: `components/site/bas/meta`, `bas/simgeler`, `bas/dogrulama`, `site/analitik`;
`SeoSunum::meta`, `SeoSunum::tamBaslik`; `SiteGorselTurevleri` (rotalar `/favicon.ico`, `/favicon-{48|96|192|512}.png`,
`/apple-touch-icon.png`, `/site.webmanifest`, `/paylasim-gorseli.jpg`).
Testle koru: gerçek ICO ve PNG ölçüsü, apple saydamsız, 1200x630 JPG, statik simge yok, bakım modunda
simgeler erişilebilir (`SiteSimgeTest`); og:image ölçüsü, secure_url, twitter:site (`SemaVeMetaSayfaTest`).

## 4. Firma bilgisi tek kaynak

- Ad, logo, favicon, telefon, WhatsApp, e-posta, adres, sosyal ağ, harita, konum ve çalışma saati
  tek sınıftan okunur: panelde girilen değer, boşsa kod içi varsayılan.
- Vitrin, e-posta, PDF, JSON-LD, llms.txt aynı sınıfı kullanır; telefon, e-posta, logo yolu
  şablona ya da başka sınıfa elle yazılmaz.
- Girilmemiş konum ve çalışma saati hiçbir yüzeye basılmaz (uydurma saat yok).

Örnek uygulama: `App\Support\Site\SiteBilgisi`, varsayılanlar `SeoSunum` sabitleri.
Testle koru: yasak desen (telefon, e-posta, logo yolu, varsayılan sabitin doğrudan kullanımı) taraması
(`tests/Mimari/FirmaBilgisiTekKaynakTest`); konum/saat boşken basılmaz (`KonumVeCalismaSaatiTest`).

## 5. JSON-LD (yapılandırılmış veri)

Şema türünün varlığı, schema.org geçerliliği ve Google zengin sonuç uygunluğu ayrı şeylerdir.
JSON-LD görünür içerikle eşleşir; şemaya sayfada olmayan bilgi girmez. JSON içine basılan metin
`</script>` kaçışıyla güvenli kodlanır.

| Tür | Kural |
|---|---|
| Organization / LocalBusiness | Tek `@id` (ör. `/#organization`); ad, logo, iletişim, adres tek kaynaktan. Konum ve çalışma saati yalnız girildiyse. Fiziksel mağaza yoksa LocalBusiness kullanılmaz. |
| WebSite | Her sayfada; `publisher` Organization `@id`'sine bağlanır. SearchAction isteğe bağlıdır: Google site içi arama kutusu 21.11.2024'te kaldırıldı, işaretleme yalnız schema.org anlamı taşır. |
| Product + Offer | Bkz. aşağıdaki tablo. |
| CollectionPage + ItemList | Kategori/liste sayfasında, o sayfada listelenen ürünler sırasıyla (sayfalar arası kesintisiz position). |
| BlogPosting | `dateModified` gerçek içerik değişimi; yazar/yayıncı Organization ya da gerçek kişi. |
| BreadcrumbList | Ekrandaki yol iziyle aynı; alt kategori üst kategoriyi taşır. |
| FAQPage | Yalnız sayfada görünen SSS ile birebir. Google SSS zengin sonucu 2026'da kaldırıldı; şema geçerli kalır, zengin sonuç beklentisi yazılmaz. |

### Product + Offer

| Alan | Kural |
|---|---|
| image | Tüm galeri, kapak önce, tekrarsız; yer tutucu görsel ürün görseli değildir. |
| sku / gtin / mpn | GTIN yalnız geçerli GS1 (8/12/13/14 hane + kontrol hanesi). Barkod alanındaki diğer kod GTIN değildir. MPN yalnız gerçek üretici parça numarasıysa; uydurulmaz. Aynı kural şema ve feed'de tek sınıftan. |
| brand | Yalnız marka kaydından; ham içe aktarım verisinden yedek okunmaz. |
| offers.price | Sunucudaki geçerli satış fiyatı (KDV dahil ise öyle), sayfadakiyle aynı. |
| offers.validFrom | Fiyatın gerçek geçerlilik başlangıcı: geçerli fiyat ya da para birimi değişince kaydedilen tarih; yeni üründe kayıt anı. Fiyatı toplu yazan kod tarihi kendisi yazar. Her istekte "şimdi" basılmaz. |
| priceValidUntil | Gerçek kampanya/fiyat bitiş tarihi varsa. Sabit "bugün + 1 yıl" ya da yıl sonu uydurma tarihtir (bkz. bilinen tuzaklar). |
| availability / itemCondition | Stok durumundan (InStock, OutOfStock, Discontinued); kondisyon ürünün gerçek durumundan, varsayılan NewCondition yalnız işletme yalnız yeni ürün satıyorsa. |
| shippingDetails | Ücret sepetle aynı hesaptan; hesaplanamıyorsa shippingRate basılmaz. Hazırlık/teslim süreleri ayardan. Hedef ülke gerçek. |
| hasMerchantReturnPolicy | İade günü ayardan; iade ücreti ve yöntemi yasal sayfalarla aynı. Gün 0/boşsa politika basılmaz. |
| aggregateRating / review | Yalnız onaylı, gerçek, sayfada görünen yorumlardan; yazar adı sayfadaki (maskeli) adla aynı. Yorum yoksa alan hiç basılmaz. |
| Fiyatı gizli ürün | Fiyat ve OG fiyat etiketi basılmaz, uydurma fiyat yazılmaz. Product düğümünün tamamen kaldırılması ise otomatik doğru değildir: Product snippet `offers` yerine gerçek `review`/`aggregateRating` ile de uygundur. Karar proje bazında verilir ve gerekçesi yazılır. |

Örnek uygulama: `SeoSunum::organizasyon`, `webSitesi`, `urun`/`urunSemasi`/`teklif`/`kargoDetayi`/`iadePolitikasi`/
`puanOzeti`/`yorumlar`, `kategori`/`koleksiyonSayfasi`, `blogYazisi`, `breadcrumb`, `sikSorulanSorular`;
`App\Support\Katalog\UrunKimligi` (gtin, mpn, tanimliMi); `urunler.fiyat_degisim_tarihi` (`Urun` modeli yazar);
kargo `KargoFirmasi::ucretHesapla`, süreler ve `iade_suresi_gun` `GenelAyarlari`'nda.
Testle koru: geçerli/geçersiz barkod GTIN/MPN ayrımı, validFrom yalnız fiyat değişince taşınır, yorum yokken
review/aggregateRating yok, yalnız onaylı yorum, kargo ücreti durumları, iade politikası, fiyatı gizli ürün,
ham marka basılmaz, JSON-LD script kapatma saldırısı (`SemaVeMetaUrunTest`, `UrunKimligiTest`);
CollectionPage/ItemList, WebSite, firma düğümü, yazar bağlantısı (`SemaVeMetaSayfaTest`).

## 6. Sitemap

- Yalnız kanonik, indekslenmesi istenen, yayındaki adresler; `loc` benzersiz.
- `lastmod` gerçek içerik değişim tarihidir; liste sayfasının tarihi listelediği kayıtların en yenisidir.
  Tarihi bilinmeyen adreste lastmod basılmaz (uydurma tarih sitemap tarihlerine güveni düşürür).
- Ürün adresleri görsel uzantısıyla (`image:image`), kapak önce, makul sınırla (ör. 10).
- **Ziyaret sayaçları lastmod'u bozmaz:** görüntülenme/indirme sayacı zaman damgasını ve model olaylarını
  tetiklemeden artar. Aksi hâlde lastmod, BlogPosting `dateModified` ve okura görünen "Güncellendi" sahte tazelik taşır.

Örnek uygulama: `SiteHaritasiUretici`, `SayacArtirici::artir` (withoutTimestamps + withoutEvents),
`SeoGozlemcisi::ETKISIZ_KOLONLAR`.
Testle koru: lastmod ve görsel sırası, liste tarihi, önbellek düşmesi (`SitemapLastmodGorselTest`); sayaç
updated_at'i değiştirmez (`tests/Feature/Seo/SayacTarihiTest`); sayaç kolonu doğrudan artırılmaz
(`tests/Mimari/SayacTarihiTest`).

## 7. robots.txt ve AI botları

- robots.txt koddan üretilir; panel, API, arama, hesap, sepet, ödeme yolları Disallow. Asıl koruma oturum/yetkidir.
- Arama ve kullanıcı isteğiyle çeken AI botları ile model eğitim botları ayrı gruplanır; eğitim botu izni
  kullanıcı tercihidir (ayardan). Bot adları ve amaçları sağlayıcının güncel belgesinden doğrulanır
  ([AI ayrıntıları](ai-ve-feed-ayrintilari.md)).
- Adıyla yazılan grup `User-agent: *` grubunu tümüyle ezer: adıyla izin verilen her gruba aynı Disallow yolları da yazılır.
  Botları adıyla listelemek zorunlu değildir; tercih edilirse bu kural uygulanır.
- `Sitemap:` satırı mutlak adresle.

Örnek uygulama: `RobotsUretici` (`KAPALI_YOLLAR`, `ARAMA_BOTLARI`, `EGITIM_BOTLARI`), `SeoAyarlari::ai_egitim_botlarina_izin`.
Testle koru: arama botları kapalı yollarla izinli, eğitim botları izne göre, sitemap sonda (`AiGorunurlukRobotsTest`).

## 8. llms.txt ve llms-full.txt

- Deneysel yardımcı çıktıdır; görünürlük garantisi değildir, Google AI özellikleri için zorunlu değildir.
- Bağlantılar mutlak adresle; firma ve alışveriş bilgisi tek kaynaktan. Fiyatı gizli ürünün fiyatı yazılmaz,
  görünen fiyat sayfadakiyle aynıdır. Sır, kişisel veri, özel fiyat, giriş isteyen içerik girmez.
- Büyük katalogda tam dosya sayfalanır; son sayfadan sonrası 404.

Örnek uygulama: `LlmsUretici`, `AlisverisBilgisi`; rotalar `/llms.txt`, `/llms-full.txt`, `/llms-full-{n}.txt`.
Testle koru: mutlak bağlantı, fiyatı gizli ürün, sayfalama, önbelleğin kayıtla düşüp sayaçla düşmemesi (`AiGorunurlukLlmsTest`).

## 9. Merchant feed

- Yalnız yayında, fiyatı görünür ve görseli olan ürünler. Kimlik kuralı şema ile aynı sınıftan (GTIN/MPN).
- `identifier_exists=no` yalnız ürüne gerçekten kimlik atanmamışsa; "kodu bilmiyoruz" yedeği değildir.
- Kargo sepetle aynı hesaptan; hesaplanamıyorsa shipping alanı basılmaz. İndirim varsa liste fiyatı + sale_price.
- Alan listesi güncel resmî ürün veri spesifikasyonundan doğrulanır; stok değişince feed önbelleği düşer.

Örnek uygulama: `MerchantFeedUretici` (`/merchant-feed.xml`), `UrunKimligi::tanimliMi`.
Testle koru: indirimli fiyat, kimliksiz ürün, kargo durumları, dışlanan ürünler, stokla önbellek düşmesi (`MerchantFeedTest`).

## 10. IndexNow

- Yalnız canlı ortamda ve açıkça etkinken; kapalıyken bekleme listesi de dolmaz.
- Değişen yayındaki adres (ve slug değiştiyse eski adres) listeye bir kez girer; zamanlanmış komut tek istekte gönderir,
  uç reddederse adresler listede kalır, gönderilemeyen eski kayıt budanır. Sayaç değişimi ve taslak listeye girmez.
- Anahtar dosyası yalnız kayıtlı anahtarla düz metin döner. Bildirim indekslenme garantisi değildir.

Örnek uygulama: `IndexNowBildirici`, `indexnow:gonder` (10 dakikada bir, yalnız production), `INDEXNOW_AKTIF`.
Testle koru: `IndexNowTest` (anahtar, tekil liste, taslak/sayaç dışı, kapalıyken istek yok, ret, budama).

## 11. Önbellek ve invalidation

- Sitemap, llms, feed gibi metinler önbelleklenebilir; önbelleğe yalnız hazır metin/dizi yazılır, model nesnesi yazılmaz.
- Anahtarlar merkezi sabit sınıfında. Besleyen her model ve ayar kaydı anahtarları düşürür; içeriği değiştirmeyen kolonlar
  (sayaç, teknik iz) düşürmez. Toplu yazma (ORM olayı tetiklemeyen) sonunda elle düşürülür; olay kaçarsa kısa bir üst süre güvencedir.
- Yeni vitrin modeli gözlemci listesine ve yol üreticisine, yeni sayaç kolonu "etkisiz kolonlar" listesine eklenir.

Örnek uygulama: `SeoCacheAnahtarlari` (`dusur`, `SURE_SAAT`), `SeoGozlemcisi::MODELLER` / `AYARLAR` / `ETKISIZ_KOLONLAR`,
XML aktarımı sonunda düşürme.
Testle koru: kayıt önbelleği düşürür, sayaç düşürmez (`AiGorunurlukLlmsTest`, `SitemapLastmodGorselTest`, `MerchantFeedTest`).

## 12. Ölçüm, Consent Mode v2, e-ticaret olayları

- Etiket kimlikleri ve doğrulama kodları panelde; kimliği boş etiket hiç basılmaz. Geliştirme/test ortamında ölçüm kapalı.
- Etiketler çerez onayına bağlı yüklenir; Consent Mode v2 `default` + `update` dört sinyalle
  (`ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization`). Hukuki uygunluk ayrı değerlendirilir.
- E-ticaret olayları tek katmanda üretilir (GA4 adları; diğer platform karşılıkları tek eşleme tablosunda).
  Tutarlar sunucuda hesaplanır; kişisel veri, alış fiyatı ve kâr gönderilmez; ürün kimliği feed kimliğiyle eşleşir.
- Analitik/reklam etiketi organik SEO koşulu değildir.

Örnek uygulama: `resources/js/olcum.js`, `components/site/analitik`, `config/olcum.php` (`OLCUM_ACIK`), `App\Support\Olcum\EticaretOlayi`.
Testle koru: `EticaretOlayiTest`, `OlcumYapilandirmasiTest`; olaylarda yasak alan (alış fiyatı, e-posta) olmadığı.

## 13. CSP ile uyum

- JSON-LD, analitik ve doğrulama betikleri istek başına nonce taşır; `unsafe-inline`/`unsafe-eval` açılmaz.
- HTML'de olay özniteliği ve `javascript:` yok; dış etiket alanları tek yapılandırma listesine eklenir.
- Gevşetme gerekiyorsa yalnız ilgili rotaya özel ve dar yapılır.

Örnek uygulama: `GuvenlikBasliklari` middleware, `config/guvenlik.php` `csp_kaynaklari`.
Testle koru: görünüm/betik taraması (`tests/Mimari/CspUyumTest`), başlık ve nonce (`tests/Feature/Guvenlik/CspBaslikTest`).

## 14. İçerik kuralları

| Kural | Not |
|---|---|
| Sayfa başına tek H1 | Proje kuralıdır, evrensel Google eşiği değildir. Şablon iskeleti (alt bilgi, menü, çerez penceresi) başlık etiketi basmaz; içerikten gelen H1 H2'ye indirilir; ikinci slayt H2 olur. |
| CTA tekrarı yok | Şablon zaten iletişim/teklif kartı basıyorsa içerik metnine aynı çağrı eklenmez; yazmadan önce şablona bakılır. |
| Ürün başlığına barkod eklenmez | Aynı adlı ürünlerde title ad olarak kalır. |
| Açıklama uydurulmaz | Boş açıklama şablonla sahte metinle doldurulmaz; boş kategoride gerçek sayılardan (ad, ürün sayısı, markalar) kurulan açıklama kabul edilebilir, dolu açıklama her zaman önce gelir. |
| AI toplu doldurma | Yalnız boş alana yazar, dolu alanı ezmez, dış kaynaklı üründe alanı kilitler; ücretlidir ve kullanıcı kararıdır. Ölçekli düşük değerli AI sayfası Google spam politikasına girer: önce örnek kalite ve maliyet ölçülür. |
| Kaynak veriyi bozma | İçe aktarılan ad, adres, ham veri kendiliğinden değiştirilmez. |
| Karakter sınırları | Başlık/açıklama sınırı editoryal rehberdir, tek sabit sınıfta durur; panel ve kontrol aynı sabiti okur. |

Örnek uygulama: `SeoSunum::icerikBasliklari`, `kategoriAciklamasi`, `SEO_BASLIK_EN_COK` / `SEO_ACIKLAMA_EN_AZ` / `SEO_ACIKLAMA_EN_COK`;
`icerik:ai-doldur` (`IcerikAiDoldurCommand`, yalnız boş alan).
Testle koru: tek H1 (`SemaVeMetaSayfaTest`, `SemaVeMetaUrunTest`), iskelet başlık basmaz, boş kategori açıklaması,
toplu doldurma dolu alanı ezmez ve XML üründe kilitler (`TopluIcerikDoldurmaTest`), komut onaysız ve yetkisiz iş atmaz (`TopluIcerikKomutuTest`).

## 15. Blog: GEO blokları, SSS, editoryal kontrol

- Google AI özellikleri için özel şema, llms.txt ya da "AI'ya özel" yazım gerekmez; özgün, insan için içerik, net başlık yapısı.
- Kısa cevap ve içindekiler blokları isteğe bağlı yapı öğeleridir. HTML temizleyici yalnız bu blokların sınıflarına izin verir;
  başlık id'leri önekle saklanır (sayfa id'leriyle çakışmaz), `#capa` bağlantıları öneke çekilir; panel düzenleyicisi bunları korur.
- SSS kayıtla birlikte tutulur, sayfada görünür ve FAQPage şemasıyla birebir aynıdır; doğrulama kuralı panel ve MCP/API'de ortaktır.
- Editoryal SEO kontrolü (başlık/açıklama uzunluğu, kopya başlık, özet, kapak, içindekiler önerisi) "uyarı" ve "öneri" diye ayrılır,
  Google kuralı diye sunulmaz; panel ve araç aynı sabitleri kullanır.

Örnek uygulama: `HtmlTemizleyici` (`zengin_icerik` profili, `kisa-cevap`, `icindekiler`, `bolum-` öneki),
`data-izinli-siniflar`, `Yazi::sssKurallari`, `YaziSeoKontrolu`, `YaziAlanlari::YAZIM_REHBERI`.
Testle koru: sınıf/id korunur ve önek uygulanır (`ZenginMetinAlaniTest`), SSS şeması (`BlogSssTest`), MCP blog araçları.

## Yeni bir projede sıra

1. Tek kaynak sınıflarını kur (firma bilgisi, yol üreticisi, ürün kimliği, sabitler).
2. Sunum sınıfı + parçalı head; tek H1 ve kanonik.
3. JSON-LD türleri (gerçek veriyle), sitemap, robots, gerekirse llms ve feed.
4. Önbellek anahtarları + gözlemci; sayaçlar zaman damgasız.
5. Slug 301 ve eski adres yönlendirmeleri.
6. Ölçüm (onaya bağlı) ve CSP nonce.
7. Her adımın testi; sonra denetim kipiyle canlı ölçüm.
