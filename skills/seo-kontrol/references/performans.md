# Performans (Core Web Vitals)

Hız sıralamada sınırlı bir sinyaldir. Asıl değeri kullanıcı deneyimindedir. Lighthouse puanı laboratuvar
tahminidir: aynı sayfa art arda ölçümde birkaç puan oynar (ör. mobilde önce 93, sonra 94). "100" hedef
olarak garanti edilmez; hedef saha verisinde iyi eşiktir (LCP ≤ 2,5 sn, INP ≤ 200 ms, CLS ≤ 0,1, 75. yüzdelik).
İnceleme: 2026-11-07.

## Ölçüm

| Kaynak | Ne verir | Not |
|---|---|---|
| PSI API `runPagespeed` | Lighthouse laboratuvar sonucu (Moto G Power, yavaş 4G) + varsa CrUX | Anahtar `PAGESPEED_API_KEY` ortam değişkeninde; anahtarsız istek günlük kotaya takılır (429). Anahtar sohbete, nota, rapora yazılmaz. |
| CrUX API | Gerçek kullanıcı (saha) verisi | Google, PSI API'deki CrUX verisini kaldıracağını duyurdu, saha verisi için CrUX API önerilir. Trafiği az sitede veri yoktur: "saha verisi yok" yaz, laboratuvarı saha diye sunma. |
| pagespeed.web.dev raporu | Aynı Lighthouse, insan için | Kullanıcı rapor bağlantısı verirse önce onu oku; API ile yeniden ölç, ikisini ayrı yaz. |
| Yerel Lighthouse | Kod değişikliği karşılaştırması | Güvenlik yazılımı sayfaya betik enjekte edebilir; yerel puanı canlı puan diye sunma. |

```bash
curl -s "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<adres>&strategy=mobile&category=performance&key=$PAGESPEED_API_KEY" -o psi.json
```

Okunacak denetimler (`lighthouseResult.audits`): `largest-contentful-paint`, `lcp-breakdown-insight`,
`render-blocking-insight`, `image-delivery-insight`, `unused-css-rules`, `document-latency-insight`,
`network-dependency-tree-insight`. Değişkenlik yüksekse en az 3 ölçümün ortancasını kullan ve ölçüm
zamanını yaz. Değişikliğin etkisini yalnız canlıya çıktıktan sonra aynı yöntemle ölç.

## LCP dökümünden nedene

| Dilim | Anlamı | Tipik neden | Çözüm |
|---|---|---|---|
| TTFB | Sunucunun ilk baytı | Önbelleksiz dinamik sayfa, misafirde oturum çerezi, yavaş sunucu | Sunucuda ölç (opcache, config/route/view cache); kodla ilgisi kanıtlanmadan kod değiştirme |
| Kaynak yükleme gecikmesi | TTFB ile LCP görselinin isteğinin başlaması arası | Görsel HTML'in derinlerinde (büyük menü/mega menü arkasında), CSS arka planında ya da JS ile ekleniyor; `loading="lazy"` | LCP görselini `<head>` başında önyükle (aşağıda), lazy kaldır, `fetchpriority="high"` |
| Kaynak yükleme süresi | Görselin inmesi | Gereğinden büyük ya da sıkıştırılmamış görsel | Doğru boyut + WebP/AVIF, `srcset`/`sizes` |
| Öğe çizim gecikmesi | İndikten sonra çizilene kadar | Render-blocking CSS/JS, uzun ana iş parçacığı görevleri | Kritik olmayan CSS/JS'i ertele; kullanılmayan CSS'i azalt |

Kaynak yükleme gecikmesi LCP'nin ~%10'unu geçiyorsa önce keşif sorunudur, görsel boyutu değil.

## Kalıplar

**LCP görselini önyükleme.** `<picture>` için preload karşılığı yoktur. Her kaynak için ayrı `<link
rel="preload" as="image" fetchpriority="high" media="...">` yazılır ve media sorguları birbirini dışlar.
Tema elle seçilebiliyorsa (localStorage) media ile `prefers-color-scheme` yetmez, yanlış görsel iner:
temayı kök öğeye yazan betikten hemen sonra, stil dosyasından **önce**, nonce'lu küçük bir betik doğru
görseli seçip preload bağlantısını ekler (stil dosyasından sonra gelen satır içi betik stil inene kadar
bekler). Seçim mantığı sunucuda tek yerde durur, betik yalnız tema ve genişliğe bakar.

**Duyarlı görsel türevleri.** Kart görselleri gösterildiği boyutun 2-3 katı olmasın. Kaynaktan dar WebP
türevleri (ör. 320/480/768/1080) ilk istekte üretilir, sonra statik dosyadan gelir. Adı kaynağın imzasını
taşır, kaynak değişince yenisi üretilir. Kaynağı silinen ya da değişen türev zamanlanmış komutla budanır
(sınırsız büyüyen klasör olmaz). `sizes` sayfa ızgarasından yazılır. SVG ve dış adres türevlenmez.
Üretim rotası izinli genişlik listesi, yol dışına çıkma (`..`) ve uzantı denetimi yapar.

**Render-blocking CSS.** Tek büyük paket (Bootstrap tamamı) çoğu sayfada %80+ kullanılmaz. Kritik CSS'i
satır içine almak ya da paketi sayfa türüne bölmek ayrı iştir; CSP `style-src` ve tema geçişleri
etkilendiği için tarayıcıda iki temada ve mobil/masaüstünde doğrulanmadan yapılmaz.

**Diğer.** Carousel'in görünmeyen slaytları ve ekran altı görseller lazy kalır, LCP görseli asla lazy
olmaz. Harita, sohbet ve video gömmeleri etkileşime ya da görünür olmaya bağlanır. Yazı tiplerinde
`font-display: swap` ve kullanılan karakter alt kümesi. Analitik etiketleri çerez onayından sonra yüklenir
(Consent Mode v2); laboratuvar ölçümü onaysız ziyaretçiyi ölçer.

## Örnek vaka

| Bulgu (mobil ve masaüstü) | Kanıt | Yapılan |
|---|---|---|
| LCP 3,0-3,2 sn; kaynak yükleme gecikmesi 1,0-1,5 sn | İlk slayt görseli HTML'in 77. KB'ında, menülerin arkasında | Slayt görseli için önyükleme bileşeni; düzende stilden önce basılır |
| Hizmet kartları 1536 px (163 KB), gösterim ~676 px | `image-delivery-insight` 469 KB tasarruf | Görsel boyut servisi ve `srcset` yardımcısı, genişlik parametreli türev rotası, günlük budama komutu; testle korunur |
| Masaüstünde slayt, logolar ve kartlar gereğinden büyük | `image-delivery-insight` masaüstü 169 KiB (12 öğe), mobil 34 KiB (2 öğe) | Slayta `1366w` türevi ve `imageSrcset`/`imageSizes` önyükleme; logolar gösterim yüksekliğinde WebP; kart `sizes` değerleri kapsayıcı sütun genişliklerine göre daraltıldı; menü ve harita kutusu logolarına `srcset` |
| Site CSS'i 57 KB render-blocking, 52 KB kullanılmıyor | `render-blocking-insight` 210-300 ms | Açık bırakıldı (ayrı iş, tarayıcı doğrulaması gerekir) |
| Elle koyu tema + sistem açık: açık slayt görseli de iniyor | Tarayıcı kaynak listesi | `<picture>` koyu kaynağı yalnız sistem temasına bakıyor; ayrı düzeltme |
| TTFB canlıda 0,8 sn, yerelde 0,1-0,2 sn | curl ölçümü | Sunucu tarafı; misafirde oturum çerezi + no-cache |
