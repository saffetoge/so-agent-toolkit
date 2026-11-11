---
name: seo-kontrol
description: Bir sitenin SEO'suyla ilgili her iş için kullan. Teknik SEO, içerik, paylaşım önizlemesi, indekslenme ve AI aramalarında görünürlük denetimi ya da SEO raporu istendiğinde; ayrıca bir projede SEO altyapısı kurulurken veya düzeltilirken, JSON-LD/şema, meta ve Open Graph, kanonik, sitemap, robots.txt, llms.txt, Merchant feed, IndexNow, favicon/paylaşım görseli, slug 301 yönlendirmesi ya da ölçüm etiketi kodu yazılırken veya değiştirilirken kullan. Yalnız WordPress eklentisi kurulumu ve genel pazarlama işleri bu kapsamda değildir.
---

# SEO kontrol

İki kip vardır; hangisinde olduğunu işe başlarken belirle ve raporda yaz. İletişim ve rapor Türkçedir.

| Kip | Ne zaman | Yazma |
|---|---|---|
| **Denetim** (varsayılan) | Kontrol, rapor, "SEO'su nasıl", rakip karşılaştırması | Salt okunur. Kod, ayar, veri, Search Console veya indeksleme hizmetlerine yazılmaz. |
| **Uygulama** | Kullanıcı düzeltme ya da kurulum istediğinde; SEO kodu yazılırken | Kod yazılır. Önce [altyapı standardı](references/altyapi-standardi.md) okunur, her kural testle korunur, projenin AGENTS.md'si ve kullanıcı kararı standardı ezer. |

Denetim salt okunurdur; düzeltme ancak kullanıcı istediğinde ayrı iş olarak yapılır. Kullanıcı
düzeltmeyi zaten istemişse aynı izni tekrar isteme. Uygulama kipinde de aşağıdaki "uydurma yok"
ve dayanak ayrımı ilkeleri geçerlidir; iş kuralı (eğitim botu izni, toplu AI metni, fiyat/kargo
kuralı, URL değişikliği) kullanıcıya sorulur. Uygulamadan sonra denetim kipiyle yeniden ölç.

## Dosya haritası

| Dosya | Ne işe yarar | Ne zaman açılır |
|---|---|---|
| [references/resmi-kaynaklar.md](references/resmi-kaynaklar.md) | Google resmî belgeleri ve dayanak türleri | Her iki kipte, iddia yazmadan önce |
| [references/altyapi-standardi.md](references/altyapi-standardi.md) | Kurulum/düzeltme standardı: kural + örnek uygulama + test önerisi | Uygulama kipinde, kod yazmadan önce |
| [references/performans.md](references/performans.md) | Core Web Vitals ölçüm ve iyileştirme | Hız/CWV sorusu ya da bulgusunda |
| [references/ai-ve-feed-ayrintilari.md](references/ai-ve-feed-ayrintilari.md) | AI botları, llms.txt, Product/Merchant ayrımı, feed | AI görünürlüğü, ürün şeması, feed işinde |
| [references/bilinen-tuzaklar.md](references/bilinen-tuzaklar.md) | Ölçüm ve uygulama katmanının sessiz hataları | Bulguyu kesinleştirmeden önce, kod yazarken |
| [references/editoryal-denetim.md](references/editoryal-denetim.md) | Yoast benzeri sayfa bazında içerik geri bildirimi | İçerik/sayfa değerlendirmesinde |
| [references/kontroller.json](references/kontroller.json) | Tarayıcının kontrol tanımları | Betik çıktısını yorumlarken (elle düzenlenmez) |
| [references/ornek-yapilandirma.json](references/ornek-yapilandirma.json) | Tarama yapılandırması örneği | Denetim ölçümünden önce |
| `scripts/seo-tara.py` | Siteyi tarar, `sonuc.json` üretir | Denetim ölçümü |
| `scripts/rapor-html.py` | `sonuc.json` + `ek.json`'dan HTML rapor | Denetim raporu |
| `scripts/canli-kontrol.sh` | Tek site ölçümü, aynı kurallar, yalnız GET | Tek siteyi hızlıca ölçerken |
| `scripts/kontrol-testleri.py` | Ağ/DB açmayan regresyon testleri | Skill değiştiğinde |

## Uygulama kipi

1. Proje AGENTS.md'sini, kurallarını ve ortak bilgi notlarını oku; mevcut SEO sınıflarını bul, kopya yazma.
2. [Altyapı standardındaki](references/altyapi-standardi.md) ilgili başlığı oku; "Örnek uygulama"
   ad kopyalamak için değil, kalıbı görmek içindir.
3. Gerçek veri yoksa alanı basma; iş kuralı gerekiyorsa sor. Resmî gereksinimi güncel belgeden doğrula.
4. Her kural için testi aynı işte yaz (birim/özellik testi, ucuzsa mimari tarama testi).
5. Projenin kapısını çalıştır; ardından denetim kipiyle sayfa örneklerini yeniden ölç ve önce/sonra kaydet.

## Performans (Core Web Vitals)

Saha ve laboratuvar ölçümü ile iyileştirme yöntemi [performans.md](references/performans.md) dosyasındadır.

## Kapsam ve dayanak

- Yalnız kullanıcının belirttiği proje/site ve onayladığı rakiplerle çalış. Rakip verilmezse
  karşılaştırma yapmadan ilerle. Başka proje veya veritabanını örnek almak için önce sor.
- Proje kurallarını ve ilgili ortak bilgi notlarını oku. Geçici JSON/HTML dosyaları sistemin
  geçici dizinine, görev/rapor notları projenin belirlediği haricî not dizinine gider.
- Önce [resmî kaynakları](references/resmi-kaynaklar.md) oku. İlgili Google iddialarını güncel
  resmî sayfadan doğrula; erişilemeyen belgeyi ve okunmayan kapsamı belirt.
- Her öneriyi resmî gereksinim, resmî öneri, platform özelliği veya deneyime dayalı öneri
  olarak ayır. Google için olan iddiayı tüm arama motorlarına/AI hizmetlerine genelleme.
- Yoast benzeri anlaşılır sayfa geri bildirimleri için [editoryal denetimi](references/editoryal-denetim.md)
  kullan. Trafik ışığı ve okunabilirlik puanı Google sıralama puanı değildir.
- İçerik uzunluğu, tek H1, URL'de ASCII, title/description karakter sayısı veya anahtar kelime
  yoğunluğu için evrensel Google eşiği uydurma. Kelime doldurma, sırf puan için URL değiştirme,
  toplu düşük değerli AI metni, uydurma fiyat/GTIN/puan ve sıralama garantisi önerme.

## Ölçüm (denetim kipi)

1. Sitenin amacını, hedef kitlesini ve indekslenmesi istenen sayfaları belirle. Giriş/panel,
   arama, filtre, kişisel hesap gibi sayfalardaki kasıtlı noindex'i hata sayma. Etiket ve reklam
   platformları organik SEO zorunluluğu değildir. Kurumsal ve e-ticaret kapsamını ayır.
2. Kullanıcı kapsamındaki gerçek ana sayfa, ürün/hizmet, kategori, sayfalama ve yazı örneklerini
   doğrula. Örneklem tüm site denetimi sayılmaz; önemli sayfa türlerini ve kapsam dışını raporla.
3. [Örnek yapılandırmayı](references/ornek-yapilandirma.json) uyarlayıp geçici dizine yaz.
   Tam bir site `biz=true` olmalı. `profil`: `kurumsal`, `eticaret` veya `belirsiz`.
   `uygulanamaz` nesnesi, kontrol kimliği ve somut gerekçe taşır. Yokluğu değil, iş açısından
   geçersizliği ifade eder; örneğin fiziksel mağazası olmayan bir işletmede LocalBusiness.
4. Skill dizinini bulunduğu konumdan çöz; kullanıcıya/Claude'a özgü sabit yol varsayma:

```bash
python3 -I <skill-dizini>/scripts/seo-tara.py <gecici-dizin>/yapilandirma.json > <gecici-dizin>/sonuc.json
```

Canlı GET istekleri aralıklıdır. Bot UA denemesi varsayılan kapalıdır; yalnız kullanıcının
sitesinde gerektiğinde `bot_kontrol=true` ver. UA taklidi gerçek bot IP erişimini kanıtlamaz.
429, WAF veya zaman aşımında daha fazla bot/rota denemesiyle yüklenme; ölçümü belirsiz bırak.
www/non-www denemesi yalnız yapılandırmada `alternatif_kok` verilmişse yapılır. Hizmet
sayfasını `sayfalar.hizmet` ile ver. Aynı lastmod dağılımı yalnız inceleme adayıdır;
toplu yayını sahte tarih diye damgalama. Sitemap ağacı varsayılan 100 dosyayla sınırlıdır (`sitemap_siniri`: 1-1000); sınır dolunca
raporda eksik tarama görünür. Fazlası için kapsamı ve sunucu yükünü yeniden değerlendir.

## Kod, veri ve tarayıcıyla çapraz doğrulama

Tarayıcı yalnız ilk HTML'yi okur. "Var" yalnız ölçülen koşulu anlatır, sıralama/indeks garantisi değildir.
Kodda yapılandırılabilir olması, canlıda etkin veya çalışır olduğu anlamına gelmez. HTML bulgusunu
silmeden kod/ayar/canlı çalışma kanıtlarını ayrı yaz. Veritabanı yalnız SELECT; önce şemayı doğrula,
yalnız toplu doluluk sayıları al, yerel veriyi canlıymış gibi sunma.

- `robots.txt`, sayfa meta robots + X-Robots-Tag, canonical hedefi, yönlendirme zinciri,
  sitemap URL'lerinin 200/canonical/indexlenebilir oluşu birlikte incelenir. Robots engeli
  ile noindex aynı şey değildir. Sitemap zorunlu değildir; bozuk mevcut sitemap ayrı kusurdur.
- İç bağlantılar, açıklayıcı bağlantı metni, yetim önemli sayfalar, görünür faydalı içerik,
  kaynak/uzmanlık ve güncellik, açıklayıcı görseller/alt metinler önceliklidir. Videolu ve
  çok dilli sitede ilgili koşullu kontrolleri ekle; yoksa gerekçeli uygulanamaz bırak.
- JS ile oluşturulan görünür içerik, Google'ın CSS/JS erişimi ve mobil görünüm tarayıcıda
  incelenir. Search Console erişimi yoksa Google'ın gerçekten gördüğü sürüm bilinmiyor de.
- Analitikte onay öncesi, ret ve onay sonrası ağ isteklerini ve etiket sırasını kontrol et.
  Consent Mode v2 sinyalleri `ad_storage`, `analytics_storage`, `ad_user_data`,
  `ad_personalization`; `default` kelimesi tek başına kanıt değildir. Hukuki uygunluk sonucu çıkarma.
- E-ticaret olaylarında tutar/para birimi/ürün kimliği, sipariş tekilleştirmesi ve çift
  etiket yüklenmesi kontrol edilir. Sahte satın alma veya mesaj gönderme yapılmaz.
- Core Web Vitals için mevcut CrUX/Search Console saha verisi ile Lighthouse laboratuvar
  ölçümünü ayır; veri yoksa ölçülemedi de. Lazy/srcset varlığından hız sonucu çıkarma.
- JSON-LD ayrışması, schema.org anlamı, Google'ın sayfa türüne göre zengin sonuç uygunluğu ve
  görünür içerikle eşleşme farklı kontrollerdir. GTIN/MPN veya politika uydurulmaz. Fiyatı
  gizli ürünün Product verisi yalnız offers yok diye kaldırılmaz; ilgili uygunluk ayrı değerlendirilir.
- AI özellikleri için [ayrıntıları](references/ai-ve-feed-ayrintilari.md) oku. llms.txt ve
  IndexNow görünürlük garantisi değildir; eğitim botu politikası kullanıcı tercihidir.
- Uygulama katmanındaki sessiz hatalar için [bilinen tuzakları](references/bilinen-tuzaklar.md) kullan.

## Rapor (denetim kipi)

`ek.json` biçimi `scripts/rapor-html.py` başındadır. Elle/kodla doğrulanan kontroller,
`gecersiz_kil`, `kod`, `yerler`, `plan`, `kararlar`, `kisitlar` alanlarına yazılır.
Her yüksek öncelikli bulgu URL veya dosya:satır, ölçüm zamanı/yöntemi, somut etki ve çözüm taşır.
Resmî iddia için ilgili doğrudan kaynak linkini ekle; deneyimse açıkça belirt.

```bash
python3 -I <skill-dizini>/scripts/rapor-html.py <gecici-dizin>/sonuc.json <gecici-dizin>/ek.json > <gecici-dizin>/seo-kontrolu.html
```

Beş durum: `var`, `kismi`, `yok`, `olcumsuz`, `uygulanamaz`. Ölçülemedi ve uygulanamaz
başarısız sayılmaz. Kontrol sayımlarını SEO/sıralama puanı diye sunma; rakipte var olması
özelliği zorunlu kılmaz. HTML raporunu dosya olarak sun; Artifact aracı varsa ayrıca
kullanılabilir, yokluğu işi durdurmaz. Dışarıya yayınlama izni çıkarma.

Sohbette kısa sonuç ve `Öncelik | Konu | Kanıt | Çözüm | Durum` tablosu ver; bekleyen kullanıcı
isteklerini de göster. İyileştirme etkisi için değişiklik tarihini ve Search Console'daki
karşılaştırılabilir sorgu/sayfa, gösterim, tıklama, CTR ve dönüşüm başlangıcını kaydet.
Değişikliklerin etkisi zaman alır; garanti veya sadece önce/sonra farkından nedensellik çıkarma.
Düzeltme istenmemişse somut önerileri sunup seçimi kullanıcıya bırak.

Skill değişikliğinde ağ/DB açmayan regresyon doğrulaması:
`python3 -I <skill-dizini>/scripts/kontrol-testleri.py`.
