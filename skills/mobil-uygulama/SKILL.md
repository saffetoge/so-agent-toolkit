---
name: mobil-uygulama
description: Mevcut bir web sitesine/projeye (özellikle Laravel) bağlı React Native (Expo) mobil uygulaması yaparken, böyle bir uygulamaya ekran, ödeme, push bildirimi, derin bağlantı eklerken ya da mağazaya (App Store, Google Play) hazırlarken kullan. Kullanıcı "mobil uygulama yap", "mobile app", "React Native", "Expo", "uygulamadan ödeme", "push bildirim", "mağazaya çıkalım", "D-U-N-S", "gizlilik sayfası (privacy alt alanı)", "uygulama indirme sayfası" dediğinde; mobil API (site ile aynı üyelik, aynı ürünler) tasarlanırken de kullan.
---

# Mobil uygulama (React Native + mevcut site)

Mevcut sitenin üyeleri, ürünleri ve ödemesiyle **aynı veriyi** kullanan iOS + Android uygulaması.
Bu skill yöntemi ve kuralları taşır; kod kopyalanmaz, her projede o projenin merkezlerine bağlanır.

Arayüz işinde projenin `DESIGN.md` dosyası baştan sona okunur.

## Değişmez ilkeler

1. **Tek kaynak sunucudur.** Üyelik, ürün, fiyat, indirim, kontenjan, sipariş durumu siteyle aynı
   tablolardan ve aynı servislerden gelir. Uygulama hesap yapmaz, yalnız gösterir. Sitenin
   denetleyicisine gömülü iş mantığı varsa ortak servise çıkarılır; web ve mobil aynı sınıfı çağırır.
   "Mobil için ikinci sürüm" yazılmaz.
2. **Sözleşme önce.** API uçları, alan adları, hata biçimi tek belgede yazılır
   (`mobil-api-sozlesmesi-<tarih>.md`, kullanıcının not klasöründe); sunucu ve uygulama ona göre yazılır, sapma
   belgeyi günceller.
3. **Kart bilgisi uygulamada alınmaz.** Banka/ödeme kuruluşunun sayfası uygulama içi web
   görünümünde açılır; sonuç adres çubuğundan değil sunucudan öğrenilir.
4. **Mağaza kuralı iş kuralıdır.** Neyin hangi ödeme yoluyla satılabileceği kod yazılmadan önce
   resmi sayfadan okunur ve kullanıcıya sorulur (`referanslar/05-magaza-ve-hesap.md`).
5. **Teknik bilgi kullanıcıya görünmez, çevrimdışı davranış ve önbellek kuralı her ekranda aynıdır**
   (ayrıntı `referanslar/02-uygulama-mimarisi.md`); tek ortak katmanda çözülür ve testle korunur.
6. **Kural = test.** Her pazarlıksız kuralın sunucuda ve uygulamada ucuz bir testi vardır.

## Akış

| Adım | İş | Ayrıntı |
|---|---|---|
| 1 | Keşif: sitenin rotaları, modelleri, servisleri, kimlik yapısı, ödeme akışı okunur; JSON API var mı ölçülür | `referanslar/01-kesif-ve-api-sozlesmesi.md` |
| 2 | Kullanıcıya yalnız ona ait kararlar sorulur (aşağıdaki tablo) | bu dosya |
| 3 | Mağaza kuralları ve hesap türü resmi sayfalardan okunur; D-U-N-S gerekiyorsa başvuru hemen başlar | `referanslar/05-magaza-ve-hesap.md` |
| 4 | API sözleşmesi yazılır | `referanslar/01-kesif-ve-api-sozlesmesi.md` |
| 5 | Sunucu: iskelet (ortak yanıt, kimlik ara katmanı, rota dosyaları), sonra uçlar | `referanslar/01-...`, `03-odeme.md`, `04-bildirim.md` |
| 6 | Uygulama: temel (tema, istemci, çevrimdışı, önbellek, gezinme), sonra özellik ekranları | `referanslar/02-uygulama-mimarisi.md` |
| 7 | Ödeme uçtan uca (test kartıyla, sağlayıcının test ortamında) | `referanslar/03-odeme.md` |
| 8 | Push uçtan uca (gerçek cihaz, geliştirme derlemesi) | `referanslar/04-bildirim.md` |
| 9 | Gizlilik ve tanıtım siteleri, derin bağlantı dosyaları, mağaza metinleri | `referanslar/05-magaza-ve-hesap.md` |
| 10 | Güvenlik denetimi (`security-audit`), simülatörde iki platformda ve iki temada uçtan uca deneme | `referanslar/06-guvenlik-ve-test.md` |

İlerleme kullanıcının not klasöründeki `mobil-uygulama-<tarih>.md` dosyasında tutulur; kullanıcının ara mesajları
geldiği anda oraya `- [ ]` olarak yazılır.

## Kullanıcıya sorulacak kararlar (ajan seçmez)

| Karar | Neden kullanıcının |
|---|---|
| Kapsam: yalnız ziyaretçi + üye mi, yönetim paneli de mi | İş birkaç katına çıkar |
| Paket adı (bundle id) | Yayından sonra değişmez |
| Kampanya/pazarlama bildirimi kime gider | Ticari ileti izni iş kuralıdır |
| Dijital (uygulamada tüketilen) ürünlerin uygulamada satışı | Mağaza komisyonu ya da satıştan vazgeçme |
| Geliştirici hesabı: kurum mu kişi mi | Mağazada görünen ad, D-U-N-S, test şartı |
| Alan adları (API, gizlilik, tanıtım) ve mağaza kimlikleri | Kurumun varlıkları |
| Hukuki metinlerin (gizlilik, KVKK) onayı | Ajan yalnız taslak yazar |

Teknik seçimler (Expo, kütüphane, klasör yapısı, jeton türü) ajanın kararıdır; raporda "teknik karar"
diye yazılır.

## Dağıtım (birden çok ajanla)

Sunucu ve uygulama ayrı depolardadır, sözleşme hazır olunca paralel yazılır. Aynı depoda iki ajan
çalışacaksa önce iskelet ana oturumda yazılır, dosya sahipliği brief'te adıyla verilir, ortak sınıfın
adı ve imzası brief'te sabitlenir. Ödeme refactor'ü ve güvenlik kararı alt-ajana bırakılmaz: ajan
yazar, ana oturum diff'i okur ve testleri kendisi koşar.

Brief'e aynen yazılacaklar:
- "Hesap/sorgu yazmadan önce merkez tablosuna bak; kopya yazma, kopya görürsen merkeze taşı."
- "Kullanıcıya giden hiçbir mesajda sunucu adresi, uç yolu, HTTP kodu, yığın izi ya da iç hata metni olmaz."
- "`.env` okunmaz; git yazma komutu çalıştırılmaz; başka projelere bakılmaz."

## Bitti ölçütü

- Sunucu: proje kalite kapısı (`composer kontrol`) yeşil; mobil uçların sözleşme, yetki (IDOR), hassas
  alan ve hata biçimi testleri var.
- Uygulama: `npm test`, `npx tsc --noEmit`, `npx expo-doctor` temiz.
- iOS simülatörü **ve** Android emülatöründe, açık **ve** koyu temada: açılış, liste, detay, kayıt, giriş,
  satın alma (test ortamı), bildirim izni, çevrimdışı şerit, hesap silme kullanıcı gibi denenmiş;
  ekran görüntüleri diske kaydedilip kullanıcıya gösterilmiş. Denenemeyen adım raporda
  "akış doğrulanmadı" diye yazılır.
- Push yalnız gerçek cihazda doğrulanır; simülatörde denenmişse rapor bunu söyler.
- Rapor: yapılan / yapılamayan / kullanıcıdan beklenen (hesap, anahtar, alan adı) tablosu.
