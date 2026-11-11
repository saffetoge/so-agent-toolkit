# Ödeme: sitenin ödeme akışını uygulamadan kullanmak

Amaç: uygulamada sitenin ödeme ekranının yerlisi görünür, para sitenin mevcut banka/ödeme kuruluşu
entegrasyonundan geçer, sipariş siteyle aynı tabloya düşer. İkinci bir ödeme entegrasyonu yazılmaz.

Önce `05-magaza-ve-hesap.md` bölüm 1 okunur: bu yol yalnız uygulama dışında tüketilen ürün/hizmet
için serbesttir.

## Akış

```
Uygulama                          Sunucu                               Banka
GET  /odeme/{urun}/hazirlik  -->  fiyat, kampanya, bekleyen onaylar,
                                  ön doldurma, yöntemler
POST /odeme/{urun}/onay      -->  zorunlu metin onayı (varsa)
POST /odeme/kupon            -->  kupon sonucu (hesap sunucuda)
POST /odeme/{urun}           -->  sipariş hazırlanır (web ile aynı servis)
        <-- { siparis, siparis_anahtari, sonraki: havale | web(adres) }
Web görünümü: adres (imzalı, kısa ömürlü) --> banka yönlendirmesi --> kart girişi, 3D
                                  <-- banka sitenin MEVCUT dönüş adresine döner
Uygulama dönüş yolunu görür, görünümü kapatır
GET  /odeme/siparis/{id}/durum -> sonuç yalnız buradan okunur
```

## Kurallar

1. **Ortak servis.** Web denetleyicisindeki doğrulama kuralları, sağlayıcı seçimi, sipariş hazırlama
   ve "bankaya gönder" adımı ortak sınıflara çıkarılır; web ve mobil aynı sınıfları çağırır. Refactor
   web davranışını değiştirmez: mevcut ödeme testleri değişmeden yeşil kalır.
2. **Banka dönüş adresleri ve rota adları değişmez** (bankaya kayıtlıdır). Mobil için ayrı dönüş
   adresi açılmaz; uygulama mevcut başarı/hata yolunu web görünümünde tanır.
3. **Sonuç adresten okunmaz.** Web görünümündeki adres, sorgu parametresi ya da sayfa metni kanıt
   değildir. Uygulama sonucu durum ucundan sorar; sunucu bankadan doğrulanmış durumu döner. Tutar
   doğrulaması sitedeki tek "ödendi" geçişinden yapılır, mobil kendi geçişini yazmaz.
4. **Oturum köprüsü.** Sitenin ödeme servisleri oturum (session) kullanıyorsa oturumsuz kopyası
   yazılmaz. Ödeme uçlarına bir ara katman, kurulum kimliği başlığından (uygulama anahtarıyla HMAC)
   türettiği kimlikle gerçek sunucu oturumu bağlar. Kurulum kimliği cihazda güvenli depoda durur,
   tahmin edilemez, yalnız TLS ile gider; sunucuda düz saklanmaz.
5. **Web'e geçiş adresi imzalı ve kısa ömürlüdür** (10 dk), yalnız bekleyen siparişte çalışır, ödenmiş
   siparişte bankaya yeniden göndermez.
6. **Misafir satın alabiliyorsa** durum sorgusu için tek kullanımlık sipariş anahtarı verilir (yalnız
   özeti saklanır, süresi dolar). Üye yalnız kendi siparişini görür (Policy; IDOR testi yazılır).
7. **Web görünümü güvenliği:** yalnız https; gezinme izin listesi (site + banka/ödeme kuruluşu alan
   adları) dışına çıkan adres sistem tarayıcısında açılır ya da engellenir; `javaScriptEnabled` bankanın
   3D sayfası için açık, dosya erişimi ve karışık içerik kapalı; uygulama ile sayfa arasında mesaj
   köprüsü (`postMessage`) kurulmaz; görünüm kapatılınca çerezler temizlenir.
8. **Yanıtta hassas alan yok:** ödeme ayrıntısı, banka yanıtı, kimlik numarası, adres dönmez.
9. **Uygulama tutar hesaplamaz:** kupon, kampanya, taksit bilgisi sunucudan hazır gelir.
10. **Kullanıcı iptal ederse** (görünümü kapatırsa) sipariş bekliyor kalır; durum ucu "bekliyor" döner,
    ekranda "ödeme tamamlanmadı, yeniden deneyin" seçeneği sunulur. Sitede zamanlanmış mutabakat
    varsa dönüşü gelmeyen ödemeyi o yakalar; uygulama da açılışta bekleyen siparişi yeniden sorar.

## Test (sunucu)

Hazırlık alanları; onay yokken ödeme reddi; havale; imzalı adres, imzasız/süresi dolmuş adres reddi;
ödenmiş siparişte yeniden başlatmama; web ile aynı tutar/kupon/kampanya; misafir anahtarı yanlışken
ret; başka üyenin siparişine ret; mevcut web ödeme testlerinin tamamı.

## Test (uygulama)

Dönüş yolu tanıma; izin listesi dışı adresin açılmaması; sonuç ekranının yalnız durum ucuna göre
çizilmesi; çevrimdışıyken ödeme düğmesinin kapalı olması. Uçtan uca deneme sağlayıcının **test
ortamında** ve test kartıyla yapılır; canlı kartla deneme yapılmaz.
