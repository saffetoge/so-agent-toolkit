---
name: ai-haber-gorseli
description: Yapay zeka ve teknoloji haberini sosyal medyada paylaşılacak dikey 9:16 (1080x1920) görsele çevirir. Haberdeki iddiaları web'de doğrular, içeriği JSON'a yazar, hazır koyu temalı şablonla PNG üretir, gözle kontrol eder, paylaşım metnini panoya kopyalar ve istenirse AirDrop ile telefona gönderir. Kullanıcı bir AI haberi, tweet, ekran görüntüsü, sürüm notu ya da kendi bulgusunu atıp "bunu paylaşalım", "dikey görsel yap", "story yap", "9:16 yap", "haber kartı", "AI news görseli", "sosyal medya görseli" dediğinde kullan.
---

# AI haber görseli (9:16)

Amaç: kullanıcının attığı haberi, doğrulanmış bilgiyle, okunaklı tek bir dikey kart hâline getirmek.
Paylaşımı kullanıcı yapar; bu skill görseli ve metni hazırlar, sosyal hesaba kendisi göndermez.

## Pazarlıksız kurallar

- **İddia doğrulanır.** Görsele giren her olgu (çıkış tarihi, bölge, fiyat, benchmark, "bugün geliyor")
  için önce WebSearch yapılır. Kaynak bulunamayan ya da kaynakla çelişen iddiayı kullanıcı yine de
  isterse yazılır, ama üretimden sonra raporda **bir kez, açıkça** "doğrulayamadım, kaynaklar şunu diyor"
  denir ve daha temkinli ifade önerilir. Sessizce yazılmaz, sessizce de değiştirilmez.
- **"Keşfettik" yalnızca bizim doğruladığımız bulgu için** kullanılır (komut çalıştırıldı, çıktı görüldü).
  Başkasının ekran görüntüsündeki çıktı, tekrar üretilmeden "keşfettik" diye sunulmaz.
- **Uydurma yok:** alıntı yalnızca kaynağı olan gerçek cümle; rakam kaynaktan birebir.
- **Marka taklidi yok:** şirket logosu, resmî duyuru görünümü ("Google resmî" rozeti) kullanılmaz;
  ürün adları düz metin.
- **Kişisel bilgi yok:** ev dizini yolu (`/Users/<ad>`), e-posta, kullanıcı adı, IP görsele girmez.
  Eklenen ekran görüntüsü de bu gözle kontrol edilir.
- Metinler Türkçe, uzun tire (—) kullanılmaz.

## Adım 1: Haberi anla, iddiaları doğrula

Kullanıcının attığı şeyi (metin, bağlantı, ekran görüntüsü) oku. İddiaları tek tek çıkar ve doğrula.
Bulgu bir komut çıktısıysa ve makinede tekrar üretilebiliyorsa çalıştırıp kendin gör.
Sonucu kendine not et: iddia, durum (doğrulandı / kaynakta var / doğrulanamadı / çelişiyor), kaynak.

## Adım 2: İçerik JSON'u yaz

Dosyayı geçici dizine yaz (scratchpad varsa orası), görselin yanına değil.
Alanlar:

| Alan | Zorunlu | Not |
|---|---|---|
| `baslik` | evet | En çok ~45 karakter. `[...]` içi renkli vurgu olur |
| `rozet` | hayır | Tek-iki kelime, büyük harf: `YENİ MODEL`, `SIZINTI`, `DUYURU` |
| `ust_bilgi` | hayır | Ürün/sürüm ve tarih: `OpenAI · 13 Ekim 2026` |
| `alt` | hayır | 1-2 cümle, en çok ~170 karakter |
| `bloklar` | hayır | En çok 3-4 blok, aşağıdaki türler |
| `alt_bilgi`, `kaynak` | hayır | Sayfanın dibinde küçük satırlar. Kaynak varsa yaz: `Kaynak: Google blog` |
| `renk` | hayır | `sari` (varsayılan), `mavi`, `yesil`, `mor`, `kirmizi`, `turuncu` |
| `guvenli_alan` | hayır | Varsayılan `true`: üst 170, alt 120 piksel hikâye arayüzüne bırakılır |

Metin içinde: `` `kod` ``, `**kalın**`. Yeni satır için `\n`.

Blok türleri (`tur`):
- `terminal`: `baslik`, `komut` (`# yorum`, `$ komut` satırları), `cikti` (sarı vurgulu satır listesi)
- `ciplar`: `baslik`, `ogeler` (başına `*` konan öğe vurgulu)
- `bilgi`: `baslik`, `metin`
- `rakamlar`: `baslik`, `ogeler: [{deger, etiket}]` (fiyat, benchmark; en çok 3 sütun)
- `liste`: `baslik`, `ogeler` (madde metinleri)
- `alinti`: `metin`, `kim` (yalnızca kaynağı olan gerçek alıntı)
- `gorsel`: `yol` (yerel dosya), `aciklama` (ekran görüntüsü eklemek için)

## Adım 3: Üret

`<skill-dizini>` bu SKILL.md dosyasının bulunduğu klasördür.

```bash
python3 <skill-dizini>/uret.py <icerik.json> ~/Desktop/ai-haber/<YYYY-MM-DD>-<kisa-ad>.png
```

Çıktı JSON'dur: `boyut` (1080x1920 olmalı), `olcek` (içerik sığmadıysa küçültme oranı), `tasma`.
- `olcek` 0.9 altındaysa metni kısalt ya da blok çıkar, yeniden üret. Küçük yazı telefonda okunmaz.
- `tasma: evet` ise mutlaka kısalt.

## Adım 4: Gözle kontrol

PNG'yi Read ile aç ve bak: kesilen kutu, taşan satır, üst üste binme, yazım hatası, okunaksız küçük yazı,
kişisel bilgi. Sorun varsa JSON'u düzelt, yeniden üret. Bakmadan "hazır" deme.

## Adım 5: Paylaşım metni

PNG ile aynı adla `.txt` yaz: 2-4 cümlelik Türkçe açıklama + 3-6 etiket (`#yapayzeka` gibi).
Görseldeki doğrulanmamış iddiayı metinde de aynı temkinle yaz. Sonra panoya kopyala:
`pbcopy < <dosya>.txt` (iPhone'da Evrensel Pano açıksa telefonda doğrudan yapıştırılır).

## Adım 6: Telefona gönder (istenirse)

Kullanıcı "telefona at", "AirDrop" derse ya da daha önce öyle istediyse:

```bash
<skill-dizini>/paylas.sh <png>
```

Arka planda çalıştır (`run_in_background`): pencere açılır, cihazı kullanıcı seçer. Bitince çıktıyı oku,
"gönderildi" ya da hatayı olduğu gibi aktar. Cihaz görünmüyorsa iPhone'da AirDrop'u "Herkes (10 dakika)"
yapmasını söyle.

## Rapor

Kısa yaz, sonra tablo ver:

| Konu | Durum |
|---|---|
| Görsel | yol, 1080x1920, ölçek |
| Paylaşım metni | yol, panoda mı |
| İddia: ... | doğrulandı / doğrulanamadı + kaynak |
| AirDrop | gönderildi / istenmedi |

Doğrulanamayan iddia varsa tablonun altında ayrıca uyar ve kaynakları bağlantı olarak ver.
Ara dosyalar (json, html, chrome profili) geçici dizinde kalır, Masaüstüne yalnızca PNG ve TXT gider.
