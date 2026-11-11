# Uygulama mimarisi (Expo / React Native)

Sürüm ve API bilgisi hafızadan yazılmaz: `npx create-expo-app@latest` ile kurulur, paketler
`npx expo install` ile eklenir, kurulu sürümün belgesi ve `node_modules` altındaki tipler okunur.

## Teknoloji

| Konu | Seçim | Not |
|---|---|---|
| Çatı | Expo (güncel SDK), TypeScript strict, Expo Router | `ios/` ve `android/` üretilir, elle düzenlenmez |
| Veri | @tanstack/react-query | Ekran doğrudan `useQuery` kullanmaz, ortak kanca kullanır |
| Güvenli depo | expo-secure-store | Jeton, kurulum kimliği, yarım kalan sipariş anahtarı |
| Önbellek | AsyncStorage | Yalnız okuma verisi; kişisel veri ve jeton yazılmaz |
| Ağ | @react-native-community/netinfo | |
| Görsel, HTML | expo-image, bakımı süren bir HTML işleyici | Bakımı durmuş paket seçilmez |
| Bildirim | expo-notifications + expo-device | |
| Ödeme | react-native-webview | Kart alanı içeren bileşen yazılmaz |

Gereksiz paket kurulmaz. Yerel modül içeren her yeni paket yeniden derleme demektir; ekran ajanları
ekleyemez, ana oturuma bildirir. `create-expo-app` kendiliğinden `git init` yapar ve şablonla birlikte
ajan ayar dosyaları getirebilir: ikisi de temizlenir (git kullanıcı kararıdır).

## Klasör yapısı (feature-first)

```
app/                      rotalar; ince, yalnız ekran bileşenini çağırır
src/
  cekirdek/               api (istemci, hata, sözleşme tipleri, örnek veri), ag, onbellek, oturum,
                          baglanti (rotalar, hedefeGit, derin bağlantı), bildirim, depolama, bicim
  tema/                   renkler (açık/koyu), ölçüler, sağlayıcı
  bilesenler/             ortak arayüz
  ozellikler/<ozellik>/   api.ts, tipler.ts, kancalar.ts, bilesenler/, ekranlar/, index.ts
test/                     cekirdek, bilesenler, ozellikler, mimari
```

Bağımlılık tek yönlüdür: `app → ozellikler → bilesenler → tema → cekirdek`. Özellik başka özelliği
yalnız `index.ts` üzerinden kullanır. Proje kökünde `AGENTS.md` bulunur: klasör yapısı, "konu → merkez"
tablosu, pazarlıksız kurallar ve koruyan testler, komutlar, terimler.

## Tek merkezde çözülenler

| Konu | Merkez | Kural |
|---|---|---|
| İstek | API istemcisi | Başka yerde `fetch` yok; başlıklar, zaman aşımı, çevrimdışı denetimi, 401/bakım/güncelleme tepkisi burada |
| Hata | Tek hata tipi + mesaj süzgeci | Adres, "Exception", SQL, yığın izi içeren ya da çok uzun sunucu mesajı genel metne döner |
| Okuma verisi | Canlı sorgu kancası | Bağlantı varken canlı veri, önbellek ezilir; ulaşılamayınca kayıt + tarih + uyarı; bağlantı gelince kendiliğinden canlı |
| Önbellek ömrü | Önbellek katmanı | Hesap değişince silinir; yaş ve adet sınırıyla budanır (büyüme sınırı) |
| Çevrimdışı arayüz | Ortak düğme/girdi (`internetGerekli`), ekran kabuğundaki şerit | İstek katmanı çevrimdışıyken istek atmaz |
| Oturum | Oturum sağlayıcı | Jeton güvenli depoda; 401'de oturum düşer, girişe yönlenir, sonra geldiği yere döner |
| Gezinme | Rota tablosu + `hedefeGit` | Slayt, kampanya, bildirim, derin bağlantı aynı fonksiyon; bilinmeyen hedef yok sayılır |
| Tema | Renk tablosu (açık/koyu) | Bileşende renk kodu yok; kontrast çiftleri testle AA |
| Para, etiket, tarih | Ortak bileşen ve biçimleyiciler | Uygulama hesap yapmaz, tutar biçimlemez, ham kod göstermez |
| Bakım, sürüm | Başlangıç kapısı | Bakımda ve zorunlu güncellemede tam ekran |
| Örnek veri | Yalnız geliştirme derlemesi | API hazır olmadan ekran yazmak ve test için; üretimde kapalı |

## Ekran kuralları

- Ekran kabuğuyla başlar (güvenli alan, başlık, çevrimdışı şeridi, klavye kaçınma).
- Dört durum çizilir: yükleniyor (iskelet), boş, hata (yeniden dene), dolu. Önbellekten gösteriliyorsa uyarı.
- Liste sanallaştırılır; çekip yenileme ve sonsuz kaydırma ortak kancadan.
- Form: sunucunun alan hataları alanın altında; ilk hatalı alana kaydırılır; gönderim sırasında düğme
  kilitli; kullanıcının elinde olmayabilecek alan zorunlu tutulmaz; hata metni ne yapılacağını söyler.
- Şifre alanları parola yöneticisiyle uyumlu; şifre, jeton, kimlik numarası günlüğe yazılmaz, kalıcı saklanmaz.
- Erişilebilirlik: rol ve etiket, 44pt dokunma hedefi, dinamik yazı boyutu, kontrast AA.
- iOS ve Android: geri tuşu, durum çubuğu, klavye davranışı ayrı ayrı denenir.
- Yerel http adresi (geliştirme sunucusu) yalnız geliştirme derlemesinde açıktır; üretimde cleartext kapalı.

## Tasarım

`DESIGN.md` baştan sona okunur; tasarım aracına (Stitch) renk, yazı tipi ve ölçü değerleriyle gidilir,
aracın önerdiği tema kabul edilmez. Koyu tema sitede yoksa uygulama için tanımlanır ve `DESIGN.md`'ye
yazılır. Stitch MCP çağrıları zaman aşımına düşebilir: üretim arkada biter, ekran listesi boş dönse de
proje küçük resmi (`get_project` → `thumbnailScreenshot`) `download_file` ile alınabilir; aynı istek
körlemesine yinelenmez. Kullanıcı sitenin mobil görünümünü referans gösterdiyse o kullanılır.

## Çok ajanla ekran yazımı

1. Temel + ilk dikey dilim (ana sayfa, liste, detay) tek ajanda; derleme ve simülatör yalnız onda.
2. Sözleşme koda eşitlendikten sonra ekran grupları paralel ajanlara: üyelik/üye alanı, ödeme/form,
   içerik. Her ajan kendi özellik klasörlerinin sahibidir; ortak dosyalara (tipler, rota tablosu, örnek
   veri dizini) yalnız ekleme yapar, düzenlemeden hemen önce dosyayı yeniden okur.
3. Ekran ajanları derleme ve simülatör çalıştırmaz (tek simülatör, tek Metro); yalnız test ve tip
   denetimi koşar. Uçtan uca denemeyi ana oturum yapar.
4. Sunucu sözleşmesi ajanlar çalışırken değişirse değişiklik listesi ajanlara mesajla iletilir.

## Yerelde deneme

- Gerçek veritabanı üretim verisiyse üyelik ve satın alma denemesi orada yapılmaz: örnek verili ayrı
  deneme sunucusu (ayrı veritabanı, test hesapları; şifreler yalnız scratchpad dosyasında) kurulur,
  uygulama ona bağlanır.
- iOS simülatörü Mac'in `127.0.0.1` ve yerel alan adlarına ulaşır; Android emülatöründe `10.0.2.2`
  kullanılır; gerçek telefon Mac'e ancak aynı ağ ya da tünelle ulaşır (tünel yerel siteyi internete
  açar: kullanıcı onayı gerekir).
- Dokunarak deneme Maestro ile yapılır (ayrıntı `06-guvenlik-ve-test.md`). Dokunma aracı yoksa gezinme derin bağlantıyla (`xcrun simctl openurl booted <şema>://...`) yapılır,
  görüntü `xcrun simctl io booted screenshot` ile alınır; dokunarak denenemeyen akış raporda
  "doğrulanmadı" diye yazılır.
- Android sistem görüntüsü Google lisansı ister; lisansı kullanıcı kabul eder.
- İlk iOS derlemesinde pod indirmesi geçici olarak düşebilir; `pod install` yeniden çalıştırılır.
