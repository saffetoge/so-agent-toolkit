---
name: acik-kod-yorumu
description: Tarayıcıya olduğu gibi giden koda (public/ altındaki JS ve CSS, şablondaki HTML yorumu, görünümdeki satır içi script/style, vitrin, mobil web) yorum yazarken, böyle bir dosyayı düzenlerken ya da gözden geçirirken kullan. Ön yüz işi yapacak alt-ajana brief yazarken, ajanın teslim ettiği ön yüz dosyalarını commit'ten önce okurken ve kullanıcı "yorum", "açıklama son kullanıcı görüyor", "rakip görmesin" dediğinde de kullan.
---

# Tarayıcıya giden koddaki yorumlar

Bu skill kuralı ve uygulama yöntemini verir.

## Kural (kısa)

Yorum **ya hiç yoktur ya da tek satır, nötr ve iç ayrıntısızdır.** Ölçüt: bir müşteri ya da rakip
okusa sorun olur mu? Açıklama gerekiyorsa sunucuda kalan yere yazılır (Blade `{{-- --}}`, PHP, test).
Stratejik bilgi (güvenlik önleminin yeri, tutarın nerede hesaplandığı, iç akış) Blade yorumuna da
taşınmaz: tarayıcıdan silip şablon yorumuna kopyalamak düzeltme değildir.

| Doğru | Yanlış |
|---|---|
| `/* Sipariş önizleme kartı */` | 12 satırlık blok: hangi `data-*` özniteliği, önbellek, istek yarışı, dokunmatik davranışı |
| `// Satır düğmeleri` | `// düğmeler hesap.siparis.partials._satir-dugmeleri'nden gelir` |
| yorum yok | `// TODO: geçici çözüm, sunucu yetkiyi burada denetlemiyor` |
| yorum yok | `// Kayıtlı tema yalnız işlevsel çerez izniyle yazılır (site.js); yoksa sistem teması uygulanır.` |
| yorum yok (Blade'de de) | `{{-- ... taksit tablosu sunucudan yeniden alınır (tutar sunucuda yeniden hesaplanır) --}}` |
| `{{-- Kısım satırı --}}` (Blade, tarayıcıya gitmez) | `<!-- SiparisService::detayGorunumu çıktısı -->` |

## Yazılmayanlar

Dosya yolu; görünüm/partial adı; sınıf, servis, metot adı (`X::y`); rota ve izin adı; tablo ve kolon
adı; `data-*` öznitelikleri, önbellek, istek akışı gibi iç işleyiş anlatımı; güvenlik önleminin nerede ya
da nasıl yapıldığı (CSRF, XSS, yetki, rate limit); kusur itirafı (hata, geçici çözüm, hack, TODO, FIXME,
bug, legacy); karar/tarih/kişi notu; gerçek kişi, müşteri ya da firma adı; AI/model adı; iç ağ adresi;
yorum satırına alınmış ölü kod; kaba ya da gayriresmî ifade.

Kapsam dışı: üçüncü taraf kütüphaneler ve lisans başlıkları (`/*!`, `@license`), e-posta şablonlarındaki
`<!--[if mso]>` koşullu yorumları.

## Alt-ajana iş verirken

Ön yüz dosyası yazacak ya da değiştirecek her ajanın brief'ine şu cümle **aynen** girer:

> Tarayıcıya giden JS/CSS/HTML yorumu: yok ya da tek satır, nötr, iç ayrıntı yok (acik-kod-yorumu
> skill'i). Açıklama gerekiyorsa Blade `{{-- --}}` ya da PHP'ye yazılır.

"İç yapı yazılmaz" gibi dar ifade yetmez; ajan bunu yalnız dosya/sınıf adı diye anlıyor.

## Teslim alırken (commit'ten önce)

1. Ajanın değiştirdiği ve yeni eklediği JS/CSS/Blade dosyalarındaki yorumları oku (`git diff` içindeki
   `//`, `/*`, `<!--` satırları; yeni dosyada başlık bloğu).
2. Çok satırlı açıklama bloğu ya da yukarıdaki listeden bir şey varsa commit'ten önce düzelt ya da
   düzelttir.
3. Hızlı tarama örneği:
   `git diff -U0 -- public resources/views | grep -E '^\+.*(//|/\*|<!--)'`

## Temizlerken (mevcut kod)

- Yalnız yorum değişir; dizeler ve kod aynı kalır.
- Doğrulama: JS/CSS için eski ve yeni sürümü küçült ve karşılaştır
  (`esbuild --minify --legal-comments=none --loader=js|css`); çıktı birebir aynı olmalı.
- Blade'de `<!-- -->` yorumunu `{{-- --}}` yapmak çıktıyı değiştirmez; içinde `@direktif`, `{{ }}` ya da
  `<?php` olan yorumlara dokunma, derlenmiş çıktıyı karşılaştır.
- Mekanik iş: alt-ajan gerekirse `sonnet` (ya da `haiku`), `opus` değil.

## Kural = test

Projede ucuzca ölçülebiliyorsa DB açmayan bir test yasak desenleri (yol, `::`, `partials.`, `.blade`,
`TODO`, `FIXME`, `HACK`, `CSRF`, rota adı kalıbı vb.) kendi `public/` JS/CSS dosyalarında arar; üçüncü
taraf ve lisans başlıkları hariç tutulur.
