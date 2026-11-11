# Güvenlik ve test

Yayın öncesi `security-audit` skill'inin kontrol listesi sunucu için uygulanır; bu dosya mobil
işin kendine özgü maddelerini taşır.

## Sunucu

| Konu | Kural | Test |
|---|---|---|
| Kapsam ayrımı | Mobil jeton yalnız mobil uçlara; yönetim/MCP jetonu mobil uçlara giremez | İki yönlü |
| Yetki | Üye yalnız kendi sipariş, profil, bildirim verisini görür | IDOR testleri |
| Hassas alan | Kimlik no, vergi no, adres, IP, ödeme ayrıntısı, başkasının iletişim bilgisi dönmez; ön doldurma dahil | Toplu yanıt taraması |
| Gizli içerik | Kapalı/pasif kayıt listede, aramada, detayda, ana sayfada çıkmaz | Her uç için |
| Hız sınırı | Her mobil rotada; giriş, kayıt, sıfırlama, form ve ödeme uçlarında siteyle aynı ya da daha sıkı | Mimari test |
| Hata sızıntısı | İstisna metni, sınıf adı, sorgu yanıtta yok; beklenmeyen hata referans kodu döner | Hata biçimi testi |
| Bot süzgeci | Web'deki honeypot yerine kurulum kimliği zorunluluğu + hız sınırı + IP engeli + mesaj tekrarı süzgeci | Form testleri |
| Gizli değer taşıma | Sipariş anahtarı, jeton adres satırında gitmez (erişim günlüğüne düşer) | Sorgu dizesiyle ret |
| Oturum köprüsü | Kimlik kurulum kimliğinden HMAC ile türetilir, istemciye gitmez, yanıtta çerez yok; köprü kimlik doğrulama taşımaz | Çerezsiz yanıt testi |
| Web'e geçiş | İmzalı, kısa ömürlü, yalnız bekleyen işlemde çalışır | İmzasız/süresi dolmuş ret |
| Cihaz tablosu | Kurulum kimliği özet olarak, push jetonu şifreli saklanır | Düz değer yok testi |
| İzleme | Uygulamadan gelen satın alma reklam ağlarına (Meta, Google) varsayılan olarak gönderilmez: Apple'da izleme izni gerektirir. Açmak kullanıcı kararıdır, gizlilik metni ayara göre değişir | Mobil sipariş → istek yok |
| Bakım ve sürüm | Sunucuda zorlanır (503, 426), yalnız bilgi olarak dönmez | Kapı testi |
| Büyüme | Cihaz, bildirim, bilet tabloları budanır | Bakım testi |

## Uygulama

| Konu | Kural |
|---|---|
| Depolama | Jeton ve kurulum kimliği güvenli depoda; AsyncStorage'da kişisel veri, jeton, form verisi yok |
| Günlük | Şifre, jeton, kimlik numarası, tam yanıt gövdesi konsola yazılmaz; teknik ayrıntı yalnız geliştirme derlemesinde |
| Ağ | Üretimde yalnız https; cleartext ve yerel ağ istisnası yalnız geliştirme derlemesinde |
| Web görünümü | Yalnız https; dönüş yolu yalnız site kökeninde tanınır; https dışı şema açılmaz; dosya erişimi ve karışık içerik kapalı; mesaj köprüsü ve betik enjeksiyonu yok; kapanınca çerez temizliği |
| Derin bağlantı ve bildirim yükü | Güvenilmez girdi: yalnız bilinen hedef türleri, serbest adres açılmaz, kimlik gerektiren rota girişe düşer |
| Dış adres | Yalnız http(s), tel, mailto; sunucudan gelen adres de bu süzgeçten geçer |
| Hata mesajı | Sunucu mesajı süzgeçten geçer; ağ hatasında sabit Türkçe metin |
| Depo | Gizli anahtar, hizmet hesabı dosyası, `.env` depoya girmez; `EXPO_PUBLIC_` önekli değerler herkese açıktır, sır konmaz |
| Bağımlılık | `npm audit` çıktısı raporlanır; kırıcı düzeltme kullanıcı kararıdır |
| Örnek veri | Üretim derlemesinde yüklenmez (mimari test) |

## Test katmanları

| Katman | Araç | Kapsam |
|---|---|---|
| Sunucu | Projenin test kapısı | Sözleşme, yetki, hassas alan, hata biçimi, ödeme, bildirim, web ile eşitlik |
| Uygulama birim/bileşen | jest + testing-library | Hata süzgeci, çevrimdışı, önbellek, gezinme, form, ödeme karar fonksiyonları |
| Uygulama mimari | jest (dosya taraması) | Sabit renk yok, özellikler arası iç import yok, `fetch` yalnız istemcide, rota dosyası ince, örnek veri üretimde yok |
| Tip ve sağlık | `tsc --noEmit`, `expo-doctor` | |
| Uçtan uca | Simülatör + deneme sunucusu | Kullanıcı gibi: kayıt, doğrulama, giriş, satın alma (havale + test kartı), bildirim izni, çevrimdışı, hesap silme; iki platform, iki tema |
| Panel ve web sayfaları | Tarayıcı, masaüstü ve mobil genişlik | Bildirim gönderme, ayar kartı, tanıtım ve gizlilik sayfaları |

## Uçtan uca deneme (Maestro) dersleri

| Konu | Kural |
|---|---|
| Araç | Maestro (`brew install mobile-dev-inc/tap/maestro`, Java 17). Akışlar depoda `.maestro/` altında, ortak adımlar `ortak/` içinde |
| Başlatma | Geliştirme istemcisinde `launchApp` kullanılmaz (Metro adresi olmadan açılır); uygulama `simctl launch ... --initialUrl` ile açılır, akış açık uygulamaya bağlanır |
| Seçici | Erişilebilirlik etiketiyle seçilir; etiket yoksa önce etiket eklenir (deneme aynı zamanda erişilebilirlik denetimidir) |
| Şifre | `-e` ile verilen değer Maestro çıktı klasörüne açık yazılır; koşu betiği çıktıyı siler |
| Gerçek değişiklik | Akış hesabın şifresini, e-postasını kalıcı değiştirmez; kendi oluşturduğu üyeyi kullanır ve siler. Örnek veri sitenin kendi doğrulamasından geçmelidir (parola kuralı, telefon biçimi) |
| Körlemesine tuş | Ekran doğrulanmadan yazma/silme adımı gönderilmez; üçüncü taraf sayfası (banka) açıkken hiç gönderilmez |
| Ağ hatası | Cihazda `fetch` düz `Error` da fırlatır; "yanıt gelmeden düşen her istek ağ hatasıdır" diye sınıflanır. Jest sahte `TypeError` ile bunu yakalamaz, çevrimdışı akışı cihazda denenir (sunucu kapatılarak) |
| Form hatası | Düzeltilen alanın hatası yazarken kalkar; boş gönderimde sunucunun ham doğrulama metnine düşmemek için zorunlu alanlar önce yerelde denetlenir |
| Jetonsuz cihaz | Push jetonu alınamadıysa (simülatör, izin yok) cihaz kaydı isteği atılmaz |
| Paylaşılan önbellek | Deneme sunucusu yerel siteyle aynı önbellek sürücüsünü paylaşıyorsa `Cache::flush()` yerel siteyi de etkiler; ayrı önbellek yolu verilir |
| Simge | Şablonun yer tutucu simgesi yayına kalmaz: simge, açılış ve bildirim görseli erken üretilir; yerel varlık değişince yeniden derleme gerekir |

## Rapor kalıbı

1. Yapılanlar tablosu (iş, durum, kanıt: test sayısı ya da ekran görüntüsü yolu).
2. Doğrulanmayanlar: hangi akış, neden (araç yok, hesap yok, lisans, gerçek cihaz gerekli).
3. Kullanıcıdan beklenenler: hesaplar (Apple, Google, Firebase, EAS), D-U-N-S, alan adları, hukuki
   metin onayı, simge ve mağaza görselleri.
4. Biriken sorular: ajan makul varsayılanla ilerlediyse hangi varsayılanı seçtiği ve nasıl geri alınacağı.
5. Paketlerin uygulanmayan bakım/üretim önerileri (her raporda yinelenir).
