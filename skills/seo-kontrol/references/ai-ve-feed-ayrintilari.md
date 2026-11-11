# AI araması, ürün şeması ve feed

## Görünürlük ve botlar

Arama/tarama, kullanıcının başlattığı çekim ve model eğitimi farklı amaçlardır. Her sağlayıcının
resmî bot belgesinden güncel ad/amaç/robots davranışını doğrula. Sabit liste güncellik garantisi değildir.
Tarayıcının UA denemeleri yalnız bu denemelerin sonucudur; doğrulanmış IP erişimini ölçmez.

| Sağlayıcı | İncelenecek ayrım |
|---|---|
| Google | Googlebot arama; Google-Extended bazı diğer AI eğitim/grounding kullanımları. |
| OpenAI | OAI-SearchBot arama, GPTBot eğitim, ChatGPT-User kullanıcı isteğiyle çekim. |
| Anthropic | Claude-SearchBot arama, ClaudeBot eğitim, Claude-User kullanıcı isteğiyle çekim. |
| Perplexity | PerplexityBot ve Perplexity-User amaçları ayrı doğrulanır. |
| Apple, Meta, Amazon ve diğerleri | Arama/eğitim/kullanıcı amacı sağlayıcının güncel belgesinden belirlenir. |

Eğitim botunu engellemek başarısız SEO değildir. Genel `User-agent: *` kuralı yeterli olabilir;
her botu adıyla Allow yapmak gerekmez. Robots izni, WAF izni ve indekslenme aynı şey değildir.

llms.txt/llms-full.txt deneysel veya hizmete bağlı yardımcı çıktılardır. Google AI özellikleri için
zorunlu değildir; sırf dosya var diye asistanların okuyacağı veya kaynak göstereceği söylenmez.
Sır/kişisel veri, özel fiyat veya giriş gerektiren içerik bu dosyalara açılmaz. Ürün fiyatı/stok
hızla değişiyorsa sayfayla tutarlılık ve varsa cache invalidation da incelenir.

Bing veya IndexNow yararlı olabilir; bildirim kabulü indekslenme, sıralama veya ChatGPT'de
alıntı garantisi değildir. ChatGPT görünürlüğünü yalnız Bing/IndexNow'a indirgeme. Denetim
IndexNow POST, yeniden tarama isteği veya ücretli tarama başlatmaz.

## Product ve Merchant ayrımı

- schema.org türünün varlığı, Google Product snippet ve Merchant listing uygunluğu farklıdır.
- Product snippet için `name` ve `offers`, `review`, `aggregateRating` seçeneklerinden biri
  gerekir; gerçek ve görünür veriye dayanır. Fiyat gizliyken şemayı otomatik silme.
- Satılabilir ürünün Merchant listing koşullarını ayrı resmî belgeden doğrula.
- Marka, SKU, gerçek GTIN/MPN, varyant ilişkisi ve görseller yalnız eldeki doğru veriden gelir.
- Kargo ücreti, ülke, handling/transit süreleri; iade kategorisi/gün/ücret/ülke alanları ve
  görünen politikalar eşleşir. Alan adı varlığı tam doğrulama değildir.
- Kondisyon ve priceValidUntil uydurulmaz. Şemadaki fiyat sıfır olabilir; boş değerle karıştırma.
- Tarayıcı aynı sayfadaki JSON-LD @id referanslarını otomatik çözer ve kopuk sayfa içi @id referanslarını raporlar; başka sayfaya işaret eden haricî @id tanımları için elle çözüm gerekebilir.

## Merchant feed doğrulaması

Önce satış/feed'in işletme için uygulanabilirliğini belirle. Genel blog RSS'i Merchant feed değildir.
XML ayrışması ve item sayısı tek başına Merchant uygunluğu değildir. Açıklama, bağlantı, görsel,
fiyat/para birimi, stok, kondisyon ve kimlik alanlarını güncel resmî ürün veri spesifikasyonuna göre
incele. Varyantlarda item_group_id ve sektöre bağlı color/size/gender/age_group alanlarını değerlendir.
GTIN yoksa MPN uydurma; identifier_exists yalnız gerçekten kimlik atanmadığında kullanılır.
Özel/gizli feed adresi olabilir; bilinen yollarda bulunamaması yokluğunu kanıtlamaz.

## Ölçüm

AI yönlendirmeleri trafik kaynağı raporunda ayrı takip edilebilir. Host adını tam alan adı/sonek
sınırıyla eşleştir; `meta` veya `ads` alt dizgisinden sınıf çıkarma. Trafik, kaynak gösterilme ve
model eğitimi farklı ölçülerdir; referrer yokluğu hiç görünülmediğini kanıtlamaz.
WebMCP, ACP/UCP gibi ticaret protokolleri yalnız ilgili ürün gerektiriyorsa ayrıca değerlendirilir;
genel SEO denetiminde yoklukları başarısızlık sayılmaz.
