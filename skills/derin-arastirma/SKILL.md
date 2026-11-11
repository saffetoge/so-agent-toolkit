---
name: derin-arastirma
description: Hata, beklenmeyen davranış ya da dış servis sorunu (API, OAuth, Meta/Google paneli, ödeme sağlayıcı, kütüphane) karşısında neden, çözüm ya da ayar değişikliği önermeden önce kullan. Kullanıcı belge, link, PDF ya da GitHub deposu verdiğinde; "büyük olasılıkla", "muhtemelen şundandır" diye yön vermek üzereyken; bir deneme tutmadığında; kullanıcı "tahmin etme", "derin araştır", "belgeyi oku" dediğinde de kullan.
---

# Derin araştırma (tahmin yok)

Kanıt yoksa neden, çözüm, ayar değişikliği ya da canlı deneme yok. Kuralın lafzını çiğnemek ruhunu
çiğnemektir: "kullanıcı acele ediyor", "küçük bir deneme" gerekçe olmaz. Bu skill yöntemi ve
rapor kalıbını verir.

## Adımlar

1. **Belgenin tamamını oku.** Sitenin her sayfası ve menüdeki her bağlantı; sorun giderme, sürüm
   notları (changelog), API referansı, hata kodu sayfası; resmi örnek kod, SDK, Postman/OpenAPI
   koleksiyonu, PDF ekleri; sağlayıcının destek ve durum sayfaları; gerekirse GitHub issue'ları ve
   geliştirici forumları. Anahtar kelime aramak ya da birkaç sayfaya bakmak okuma sayılmaz.
   Açılmayan ya da giriş isteyen sayfayı okunmadı diye yaz.
2. **Ölç.** Belge cevap vermiyorsa ya da çelişiyorsa: log, tanı aracı, gerçek API yanıtı (durum,
   hata kodu, alt kod, izleme kimliği), test. Çalışan ve çalışmayan iki yol varsa farklarını tek
   tek yan yana koy. Tanı aracı yoksa önce onu yaz; ölçmeden ilerleme.
3. **Tek hipotez, kanıta bağlı.** Hipotezi hangi okuma ya da ölçümün desteklediğini yaz. Onu
   doğrulayacak ölçümü aynı mesajda öner.
4. **Kullanıcıyı ancak sonra yönlendir.** Kök neden kanıtlanmadan kullanıcıya ayar değiştirtme,
   hesabında bağlantı kaldırtma, canlıda deneme yaptırma.
5. **Deneme tutmadıysa** ikinci tahmine geçme; 1. ya da 2. adıma dön.

## Rapor kalıbı

Her araştırma raporu bu dört bölümden oluşur, bu sırayla:

1. **Okunanlar:** sayfa/dosya listesi; okunamayanlar ayrıca.
2. **Bulgular:** belgelenmiş olan, belgede olmayan, çelişen; belgede olmayıp denenerek bulunan
   "belgede yok, denendi" etiketiyle.
3. **Ölçümler:** hangi araçla, ne zaman, sonuç (ham değerler, gizli değer maskeli).
4. **Sonuç:** kanıtlanmış neden ve çözüm; ya da "Bilmiyorum. Okudum: ... Ölçülmesi gereken: ...".
   Kaçınılmaz varsayım tek satırda: "Tahmin, doğrulanmadı: ... Doğrulamak için: ...".

## Kırmızı bayraklar (dur, 1. adıma dön)

| Düşünce | Gerçek |
|---|---|
| "Büyük olasılıkla izin/önbellek/bekleme süresi" | Ölçülmemiş neden tahmindir |
| "Kullanıcı şu ayarı bir açsın, bakalım" | Kullanıcının hesabı deney alanı değil |
| "Belgede aradım, yok" | Arama okuma değildir; sayfaların tamamı |
| "İlk tahmin tutmadı, o zaman şudur" | İkinci tahmin de tahmin; ölçüme dön |
| "Hızlı cevap bekleniyor" | Yanlış yön, araştırmadan daha çok zaman yer |

Örnekler: bir sosyal medya hesabı bağlantısında sağlayıcının hesap listesi boş dönünce iki tahminle
kullanıcıya sağlayıcı panelinde ayar açtırıldı ve bağlantı kaldırtıldı, ikisi de yanlıştı. Bir ödeme
sağlayıcının taksit ayarında 22 sayfalık belgenin 3'ünde kelime arandı, kullanıcı defalarca SMS'le
test etmek zorunda kaldı.
