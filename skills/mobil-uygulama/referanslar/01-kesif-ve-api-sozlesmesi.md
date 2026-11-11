# Keşif, API sözleşmesi ve sunucu iskeleti

## 1. Keşif (kod yazmadan önce ölçülür)

| Ne | Nasıl | Neden |
|---|---|---|
| JSON API var mı | `routes/api.php`, `app/Http/Controllers/Api`, `php artisan route:list --path=api` | Yoksa sıfırdan; varsa genişletilir, ikincisi yazılmaz |
| Kimlik altyapısı | `config/auth.php` guard'ları, Sanctum/Passport kurulu mu, e-posta doğrulaması zorunlu mu | Jeton türü mevcut pakete göre seçilir; paket kurmak kullanıcı onayı ister |
| Sitenin rotaları | `routes/web.php` baştan sona | "Sitedeki her şey" kapsamının listesi |
| İş mantığı nerede | Denetleyicide gömülü mü, serviste mi | Gömülüyse ortak servise çıkarma işi plana girer |
| Ödeme akışı | Ödeme denetleyicisi, banka dönüş rotaları, oturum kullanımı, misafir satın alma | `03-odeme.md` kararlarını belirler |
| Oturuma bağlı servisler | `session(` ve `->session()` araması | Oturum köprüsü gerekir mi |
| Merkezler ve mimari testler | Projenin AGENTS.md / CLAUDE.md "konu → merkez" tablosu, `tests/Mimari` | Mobil uçlar aynı merkezleri kullanır, aynı testlere takılır |
| Önbellek | Ana sayfa/katalog önbellek anahtarları, kim temizliyor | Web ve uygulama aynı önbelleği okumalı |
| Yerel araçlar | `node -v`, Xcode, CocoaPods, Java 17, Android SDK (sistem görüntüsü, lisanslar) | Eksik araç erkenden bulunur; lisans kabulü kullanıcınındır |

Keşif sonucu ilerleme notuna yazılır. Başka projelere bakılmaz.

## 2. Sözleşme belgesi

Tek belge; sunucu ve uygulama ajanları yalnız onu okur. Bölümleri:

1. **Genel:** kök yol (`/api/mobil/v1`), istek başlıkları, başarı ve hata zarfı, hata kodları tablosu,
   tarih/para/görsel/HTML kuralları, sayfalama.
2. **Uç listesi:** yöntem, yol, kimlik düzeyi, hız sınırı.
3. **Ortak nesneler** (alan, tip, null olabilir mi, anlam).
4. Özellik bölümleri (başlangıç, katalog, formlar, kimlik, üye alanı, ödeme, cihaz/bildirim).
5. **Uygulama geliştiricisine notlar:** çok adımlı akışlar adım adım.
6. Değişiklik günlüğü.

Sabit kurallar:

- Başlıklar: `Authorization: Bearer`, kurulum kimliği (uuid, güvenli depoda), platform, uygulama sürümü.
- Zarf: başarı `{ veri, sayfalama? }`, hata `{ hata: { kod, mesaj, alanlar?, referans? } }`. Her yanıt
  bu ikisinden biridir; zarfın dışına alan konmaz.
- `mesaj` kullanıcıya gösterilecek dildedir, teknik ayrıntı içermez; beklenmeyen hatada hata kaydının
  referans kodu döner.
- Para nesnesi: makine tutarı (string ondalık) + sitedeki biçimle hazır metin(ler). Uygulama biçimlemez.
- Her kod alanının yanında etiketi (`durum` + `durum_etiketi`). Yalnız uygulamanın davranış için
  kullandığı teknik kodlar etiketsiz kalır, değer kümesi belgede yazar.
- Site içi bağlantılar sunucuda gezinme nesnesine çevrilir (`{ tur, deger }`); uygulama adres çözmez.
- Sunucu "yapılabilir mi" sorularını yanıtlar (`satin_alinabilir`, `kayit_alinabilir`, engel mesajı).
- Hassas alan dönmez: kimlik numarası, vergi no, adres, IP, ödeme ayrıntısı, başkasının iletişim bilgisi.
  Ön doldurma yanıtları da buna dahildir.
- Gizli değer (sipariş anahtarı, jeton) adres satırında taşınmaz; başlıkta ya da gövdede gider.

Kod yazıldıktan sonra belge **koda eşitlenir** (ayrı, salt okur bir tur: rota listesi + resource
sınıfları + istek sınıfları okunur). Bu tur aynı zamanda inceleme işi görür: tutarsız alan adı,
etiketsiz kod, hassas alan, zarf dışı alan burada yakalanır ve bir düzeltme turuna girer.

## 3. Sunucu iskeleti (ana oturum yazar, ajanlardan önce)

| Parça | Görev |
|---|---|
| `routes/api.php` | `/api/mobil/v1` öneki + `mobil` grubu; her özellik kendi `routes/mobil/<ozellik>.php` dosyasında |
| `MobilYanit` | Tek yanıt biçimi (başarı, sayfalı, hata) ve hata kodu sabitleri |
| `MobilPara`, hedef çözücü | Para nesnesi ve site adresi → gezinme nesnesi; tek yerde |
| `mobil` ara katman grubu | IP engeli, isteği JSON'a zorlama, bakım ve en düşük sürüm kapısı |
| Kimlik ara katmanı | Jeton + kapsam denetimi (`mobil:kullan`); seçenekler: isteğe bağlı, doğrulanmış |
| İstisna işleme | Mobil yolunda doğrulama, kimlik, yetki, 404, hız sınırı, bakım, beklenmeyen hata → `MobilYanit` |

Kimlik kararları:

- Kayıt, giriş hız sınırı, profil, şifre, hesap silme sitedeki akışın **aynı servisini** çağırır; web
  denetleyicisindeki mantık servise çıkarılır.
- Jeton yalnız mobil kapsamını taşır; başka amaçlı jeton (yönetim, MCP) mobil uca, mobil jeton
  onlara giremez. İkisinin de testi yazılır.
- Jeton üretmek için gereken istemci/anahtar kaydı migration ya da deploy adımıyla oluşur; canlıda
  elle komut önerilmez.
- Şifre değişince diğer jetonlar iptal olur. Çıkış o cihazın jetonunu iptal eder, cihaz-üye bağını koparır.
- E-posta doğrulaması ve şifre sıfırlama bağlantısı web sayfasında açılır; uygulama durumu yeniden sorar.

Operasyon ayarları (panelden): en düşük sürüm, bakım kipi ve mesajı, platform bazlı satın alma
anahtarı, mağaza adresleri. Hepsi tek serviste okunur; kapılar sunucuda zorlanır, yalnız bilgi
olarak dönmez.

## 4. Web ile eşitlik

Uygulama ve site aynı servis ve aynı önbelleği kullanıyorsa eşitlik kendiliğinden gelir; yine de
kalıcı testle korunur: kayıt eklenince, pasife alınınca, sırası ve fiyatı değişince site sayfası
ile mobil uç aynı şeyi gösterir. Yerelde gerçek veriyle bir kez elle karşılaştırılır (API yanıtındaki
başlıklar site HTML'inde var mı, fiyat metni aynı mı).

## 5. Sunucu testleri (en az)

Sözleşme alanları; kimliksiz ve başkasının verisine erişim (IDOR); gizli/kapalı içeriğin listede,
aramada, detayda çıkmaması; doğrulanmamış e-posta; yanlış kapsamlı jeton; hassas alanların toplu
yokluğu; hata biçimi (404, 422, 429, 503, 500 + referans); mimari test: mobil denetleyicilerde ham
sorgu, ham model dönüşü, `env(`, `getMessage()` sızıntısı yok, her rotada hız sınırı var.
