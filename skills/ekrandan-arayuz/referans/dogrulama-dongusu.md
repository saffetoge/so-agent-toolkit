# Doğrulama döngüsü

Yazdığın sayfayı **görmeden** iş bitmez. Bu adım skill'in en değerli kısmı.

## Hazırlık

`claude-in-chrome` araçları gerekiyor. Tek ToolSearch çağrısıyla yükle:

    select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__read_console_messages

## Tur

### 1. Aç
Yeni sekmede profildeki yerel URL + sayfanın yolu.

**Giriş duvarına takılırsan** şifre girme ve proje içine (`public/` vb.) geçici HTML dosyası bırakma.
Önce açık tarayıcı oturumunda yönetici panelinden ("Kullanıcı olarak giriş" vb.) hedef hesaba geçmeyi dene;
oturum yoksa kullanıcıdan tarayıcıda giriş yapmasını iste. Kimlik bilgisi denemeye hiçbir koşulda kalkma.
Test ederken **verisi dolu** bir hesap seç, yoksa her kart boş durum gösterir ve hiçbir şeyi doğrulamış olmazsın.

### 2. Bak
Ekran görüntüsü al. Sayfa uzunsa aşağı kaydırıp ikinci görüntü al.

Konsolu da oku. Kırık asset, tanımsız değişken, JS hatası burada görünür ve
görsel farkın asıl sebebi çoğu zaman budur.

### 3. Karşılaştır

Orijinal görsel ile aldığın görüntüyü karşılaştır. Şu sırayla bak, **bu sıra önemli**:

1. **Bozuk mu?** Sayfa hata veriyor, boş geliyor, stil hiç yüklenmemiş.
   Diğer her şeyden önce bunu çöz.
2. **Yapı** - bölümler doğru sırada mı, eksik bölüm var mı, ızgara sütun sayısı doğru mu.
3. **İçerik** - metinler birebir mi, sütun başlıkları, buton etiketleri.
4. **Yerleşim** - hizalama, boşluk, genişlik, kart yükseklikleri.
5. **Görünüm** - renk, yazı boyutu ve kalınlığı, kenarlık, gölge, yarıçap.

Farkları listele. Sadece **gerçek** farkları yaz: font render farkı, sahte verinin
gerçek veriden farklı olması, tarayıcı kaydırma çubuğu fark değildir.

### 4. Düzelt
Farkları en üstteki kategoriden başlayarak düzelt. Yapı hatası duruyorken renk ayarlama.

## Sınırlar

- **En fazla 3 tur.** Sonunda kalan fark varsa dur, listele, kullanıcıya sor.
- **Aynı düzeltmeyi iki kez deneme.** İkinci denemede de olmadıysa üçüncüyü deneme,
  sebebini araştır ya da sor.
- Tarayıcı aracı 2-3 kez üst üste hata verirse dur ve kullanıcıya bildir, döngüye girme.

## Mobil

Görsel mobil bir arayüzse ya da profil mobil davranışın önemli olduğunu söylüyorsa,
pencereyi daralt (`resize_window`, ~390px genişlik) ve o boyutta da bak.
Masaüstü doğru olması mobilin doğru olduğu anlamına gelmiyor.
