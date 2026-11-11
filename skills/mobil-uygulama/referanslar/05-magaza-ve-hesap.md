# Mağaza kuralları, geliştirici hesabı, gizlilik ve tanıtım siteleri

Bu dosyadaki kurallar resmi sayfalardan okunarak yazıldı (2026-11-11). Mağaza kuralları değişir:
yayın öncesinde aynı sayfalar yeniden okunur, buradaki özet kanıt sayılmaz (`derin-arastirma`).

Kaynaklar:
- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Google Play Payments: https://support.google.com/googleplay/android-developer/answer/9858738
- Google Play hesap silme: https://support.google.com/googleplay/android-developer/answer/13327111
- Apple üyelik: https://developer.apple.com/programs/enroll/ ve https://developer.apple.com/help/account/membership/D-U-N-S/
- Google hesap türü: https://support.google.com/googleplay/android-developer/answer/13634885
- Google kişisel hesap test şartı: https://support.google.com/googleplay/android-developer/answer/14151465

## 1. Ödeme: ne, hangi yolla satılabilir

Soru her projede baştan sorulur: **satılan şey uygulamanın dışında mı tüketiliyor, içinde mi?**

| Satılan | Apple | Google Play | Dayanak |
|---|---|---|---|
| Fiziksel ürün, yüz yüze hizmet (sınıfta eğitim, randevu, kargo) | Banka sayfası / kart serbest, IAP kullanılmaz | Play Billing dışı serbest | Apple 3.1.3(e); Google bölüm 3 |
| Bire bir canlı hizmet (iki kişi arası ders, danışmanlık) | IAP dışı serbest | belgeye bak | Apple 3.1.3(d) |
| Canlı grup dersi (bire çok), kayıtlı video, uygulamada açılan dijital içerik, üyelik | **IAP zorunlu** | **Play Billing'e tabi** | Apple 3.1.1, 3.1.3(d) "One-to-few and one-to-many real-time services must use in-app purchase"; Google bölüm 2 ve 4 |
| Yalnız kurumlara (B2B) satış | 3.1.3(c) istisnası olabilir, bireye satış IAP | belgeye bak | Apple 3.1.3(c) |

- Türkiye mağazasında uygulamadan dış ödeme sayfasına yönlendiren düğme/bağlantı hakkı Apple
  sayfasında yok (3.1.1(a) yalnız ABD mağazasını sayıyor). Google "in-app webviews, buttons, links"
  ile başka ödeme yöntemine götürmeyi bölüm 4'te yasaklıyor (bölüm 3 istisnası hariç).
- Karma katalogda (yüz yüze + çevrim içi) karar kullanıcınındır; seçenekler ona tabloyla sunulur:
  1. Uygulamada yalnız yüz yüze olanlar satılır; dijital olanlar listelenir ama satın alma düğmesi
     ve dış ödeme yönlendirmesi olmaz.
  2. Dijital olanlar için mağazanın kendi ödeme sistemi eklenir (komisyon, ürün tanımı, sunucu doğrulaması).
  3. Dijital olanlar uygulamada hiç gösterilmez.
- Sunucu her ürün için "uygulamada satılabilir mi" bilgisini döndürür; uygulama kendi karar vermez.
  Kural tek yerde (sunucuda) durur, mağaza kuralı değişince uygulama güncellemesi gerekmez.
- Kart bilgisi uygulamada alınmaz; bankanın sayfası web görünümünde açılır (bkz. `03-odeme.md`).

## 2. Hesap silme (iki mağazada da zorunlu)

- Apple 5.1.1(v): "If your app supports account creation, you must also offer account deletion within the app."
- Google: uygulama içi silme yolu **ve** kullanıcıyı uygulamaya geri göndermeden çalışan bir web
  bağlantısı. Bağlantı uygulama ya da geliştirici adını anmalı; Play Console'daki veri güvenliği
  formunda bildirilir.
- Uygulama: Hesabım > Hesabımı Sil (parola onayıyla, sitedeki silme kuralının aynısı). Web bağlantısı
  gizlilik sitesindeki "Hesabınızı silme" bölümüdür (bölüm 4).
- Yasal saklama zorunluluğu olan kayıt (fatura, sipariş) silinmez; gizlilik metninde açıkça yazılır.
- Yalnız kendi hesap sistemi kullanılıyorsa "Sign in with Apple" zorunlu değil (4.8). Google/Facebook
  girişi eklenirse eşdeğer seçenek şartı devreye girer.
- Giriş gerekmeyen özellikler girişsiz kullanılabilmelidir (5.1.1(v)); bildirim uygulamanın çalışması
  için şart koşulamaz, hassas kişisel veri bildirimle gönderilmez (4.5.4).

## 3. Geliştirici hesabı: kurum mu, kişi mi, D-U-N-S

| Konu | Apple bireysel | Apple kuruluş | Google kişisel | Google kuruluş |
|---|---|---|---|---|
| D-U-N-S | Gerekmez | Zorunlu, ücretsiz, 5+2 iş günü | Gerekmez | Zorunlu, ücretsiz, 30 güne kadar |
| Mağazada görünen | Kişinin yasal adı | Kurumun yasal adı | Kişinin yasal adı, ülke, e-posta | Kurum adı, adres, e-posta, telefon |
| Yayın öncesi kapalı test | yok | yok | 12 kişi, kesintisiz 14 gün (13.11.2023 sonrası açılan hesap) | sayfada şart yok |
| Ek şart | - | Tüzel kişilik, kurum alan adlı e-posta, çalışan web sitesi, imza yetkilisi | "öğrenci, hobi, amatör" için tanımlı | Ticari ve profesyonel faaliyet |

- Kurum adına çıkan, kurumun markasını taşıyan ve ödeme alan uygulama kurum hesabından yayınlanır.
  Apple yardım sayfası: "the organization must be the one to submit the app for review" (geliştirici
  yardımcı olabilir). Bireysel hesapta mağazada kişinin adı satıcı olarak görünür.
- D-U-N-S başvurusu işin başında yapılır; kod yazımını beklemez (haftalar sürebilir).
- Yazılımı yapan kişi/firma kurum hesabına kullanıcı olarak eklenir; hesap kurumda kalır.
- Hesap türü kullanıcının kararıdır; bu tablo ona sunulur, ajan seçmez.

## 4. Gizlilik sitesi (`privacy.<alan>` ya da `gizlilik.<alan>`)

Mağazaların ikisi de herkese açık gizlilik politikası adresi ister. Tek sayfa, giriş gerektirmez,
uygulama ve kurum adını anar, Türkçe + İngilizce, açık/koyu tema, solda "Bu sayfada" gezinmesi.

Bölümler (sırayla):

1. Veri sorumlusu (kurumun yasal adı, geliştirici veri işleyen olarak, iletişim e-postası)
2. İşlenen veriler (hesap, sipariş, form, teknik: cihaz adı/platformu, bildirim anahtarı; istenmeyen
   veriler de sayılır: "kart bilgisi uygulamada alınmaz")
3. Cihaz izinleri: tablo `İzin | Neden istenir | İzin vermezseniz` (yalnız gerçekten istenen izinler)
4. İşleme amaçları ve hukuki sebepler (KVKK madde 5)
5. Kimlerle paylaşılır (ödeme kuruluşu, bildirim hizmeti, SMS/e-posta sağlayıcı, yetkili kurumlar)
6. Saklama ve güvenlik
7. Hesabınızı silme: uygulama içi yol adım adım + uygulamaya erişemeyenler için e-posta/form
8. KVKK madde 11 hakları ve başvuru yolu
9. Çocuklar
10. Değişiklikler ve iletişim, sayfanın altında yürürlük tarihi

Kurallar:
- Metin uygulamanın **gerçekten** yaptığı şeyle birebir örtüşür: kod taranır (izinler, toplanan alanlar,
  üçüncü taraflar), metin ondan sonra yazılır. Uygulama değişince metin aynı işte güncellenir.
- Hukuki metin taslaktır; yayın öncesi kullanıcıya/kurumun hukukçusuna onaylatılır, raporda "taslak,
  onay bekliyor" diye yazılır.
- Mağazadaki veri güvenliği / gizlilik etiketi formu bu metinle aynı listeden doldurulur.

## 5. Tanıtım ve indirme sitesi (`mobil.<alan>`)

Tek sayfa: logo, "Resmi mobil uygulama" etiketi, iki cümlelik tanıtım, App Store / Google Play /
Paylaş düğmeleri, özellik hapları, "Telefonunuzla okutun" QR kartı, alt bilgide ana site ve gizlilik
bağlantısı, tema düğmesi.

- QR ve tek bağlantı (`/indir`) cihazı tanıyıp doğru mağazaya yönlendirir; masaüstünde sayfa açılır.
- Mağaza bağlantıları ayardan gelir; yayınlanmamış mağazanın düğmesi "Yakında" olarak pasif görünür.
- SEO: `seo-kontrol` skill'i uygulanır (başlık, açıklama, Open Graph görseli, `SoftwareApplication`
  JSON-LD, kanonik). Ana sitede iOS için akıllı uygulama afişi (`apple-itunes-app` meta etiketi) ve
  eğitim/ürün sayfalarından uygulamaya evrensel bağlantı.
- İki site de ana projenin içinden alan adına göre sunulabilir (ayrı depo gerekmez); alan adları
  ayardadır, boşken rotalar kapalıdır.

## 6. Mağaza görünürlüğü (ASO) ve derin bağlantı

- Mağaza metinleri depoda tutulur (`magaza/tr/`): ad (30 karakter), alt başlık (30), anahtar kelimeler
  (iOS, 100), kısa açıklama (Android, 80), uzun açıklama, sürüm notu. Anahtar kelime doldurma yok;
  sitedeki `seo-kontrol` dil kuralları burada da geçerli.
- Ekran görüntüleri gerçek uygulamadan, açık temada, zorunlu boyutlarda alınır.
- Evrensel bağlantı: site `/.well-known/apple-app-site-association` (JSON, uzantısız, yönlendirmesiz,
  HTTPS) ve `/.well-known/assetlinks.json` yayınlar; uygulamada `ios.associatedDomains`
  (`applinks:alan`, protokolsüz) ve Android `intentFilters` (`autoVerify: true`). iOS dosyayı kurulumda
  ve güncellemede indirir: yol listesi değişirse mağaza güncellemesi gerekir.
- Android SHA-256 parmak izi Play Console'daki uygulama imzalama sertifikasından alınır (yükleme
  anahtarından değil).
