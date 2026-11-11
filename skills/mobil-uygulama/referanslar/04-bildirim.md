# Push bildirimi (Expo Push Service)

Kaynak (okundu 2026-11-11, uygulamadan önce yeniden okunur):
https://docs.expo.dev/push-notifications/push-notifications-setup/ ,
https://docs.expo.dev/push-notifications/sending-notifications/ ,
https://docs.expo.dev/push-notifications/fcm-credentials/

## Sunucu

- **Cihaz tablosu:** kurulum kimliğinin özeti (benzersiz; düz değer saklanmaz), üye (boş olabilir),
  push jetonu, platform, uygulama sürümü, cihaz adı, bildirim izni, son görülme. Kayıt ucu
  idempotenttir (aynı kurulum güncellenir). Giriş yapınca cihaz üyeye bağlanır, çıkışta bağ kopar.
- **Gönderim:** `POST https://exp.host/--/api/v2/push/send`, tek istekte en çok 100 mesaj, kuyruk
  işiyle. Yanıttaki bilet (ticket) "Expo aldı" demektir, "cihaza ulaştı" değil. Makbuzlar
  (`/push/getReceipts`, en çok 1000 kimlik) yaklaşık 15 dakika sonra sorgulanır, 24 saatte silinir.
- **`DeviceNotRegistered`:** bilet ya da makbuzda gelirse o jeton silinir, bir daha gönderilmez.
  `MessageRateExceeded`, 429 ve 5xx'te üstel bekleme ile yeniden denenir. Sınır: proje başına
  saniyede 600 bildirim.
- **Erişim jetonu** isteğe bağlıdır; açılırsa sunucu ayarında (şifreli ya da `.env`) durur, depoya girmez.
- **Bildirim kaydı tablosu:** başlık, metin, hedef, gönderen, durum, hedeflenen/gönderilen/başarısız
  sayıları. Panelde liste + gönderme formu; "N cihaza gidecek" bilgisi ve onay adımı.
- **Büyüme sınırı:** uzun süredir görülmeyen cihaz ve eski bildirim kayıtları zamanlanmış temizlikte
  budanır; budama kurulmadan iş bitmiş sayılmaz.
- **Kime gider** iş kuralıdır, kullanıcıya sorulur (ayrı pazarlama izni mi, izin veren herkes mi,
  yalnız üyeler mi). Otomatik bildirim türleri (ödeme alındı, eğitim hatırlatması) de sorulmadan
  icat edilmez.
- Bildirim metninde kişisel ya da hassas veri bulunmaz (Apple 4.5.4); kilit ekranında görünür.

## Uygulama

- İzin ilk açılışta istenmez; ne işe yaradığını anlatan bir kart/ekrandan sonra istenir. Reddedilirse
  uygulama aynen çalışır; ayarlardan açma yolu gösterilir. Uygulama içi bildirim listesi izne bağlı değildir.
- Jeton alınınca ve her açılışta cihaz kaydı güncellenir; izin kapanırsa kayıt silinir.
- Bildirim yükü yalnız hedef taşır: `{ hedef_tur, hedef_deger, bildirim_id }`. Dokunulunca tek
  gezinme fonksiyonu (`hedefeGit`) çalışır; uygulama kapalıyken gelen bildirim de aynı yoldan açılır.
  Yükteki değer güvenilmez girdidir: yalnız bilinen hedef türleri kabul edilir, serbest adres açılmaz.
- Android'de bildirim kanalı tanımlanır (ad Türkçe); simge tek renkli olmalıdır.

## Kimlik bilgileri (kullanıcının hesaplarında yapılır)

| Platform | Gereken | Nerede |
|---|---|---|
| Android | Firebase projesi, `google-services.json` (depoya girebilir), FCM V1 hizmet hesabı anahtarı (depoya GİRMEZ) | Firebase Console > Service accounts; anahtar EAS'e `eas credentials` ile yüklenir |
| iOS | Ücretli Apple Developer hesabı, APNs anahtarı | `eas build` / `eas credentials` oluşturur; anahtar iptal edilirse o anahtarı kullanan bütün uygulamalar bildirim alamaz |

Push gerçek cihazda ve geliştirme derlemesinde (development build) doğrulanır. Simülatörde jeton
alınamayabilir; rapor hangi cihazda denendiğini yazar.

## Test

Sunucu: 100'lük gruplama, `DeviceNotRegistered` temizliği, izin kapalı cihazın hedeflenmemesi, misafir
cihazın kurala göre hedeflenmesi, bildirimin yalnız doğru üyeye gitmesi, panel yetkisi. Dış istek
`Http::fake` ile; testte gerçek push atılmaz.
Uygulama: yükten hedefe çevirme, bilinmeyen hedefin yok sayılması, izin reddinde akışın sürmesi.
