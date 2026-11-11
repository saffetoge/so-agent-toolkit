---
name: ekrandan-arayuz
description: Ekran görüntüsü, tasarım mockup'ı, Figma çıktısı veya arayüz fotoğrafını projenin kendi konvansiyonlarıyla çalışan koda çevirir. Görseli bölümlere ayırır, mevcut component'lerle eşler, sayfayı yazar, tarayıcıda açıp orijinalle karşılaştırarak düzeltir. Kullanıcı bir arayüz görseli paylaşıp "bunu yap", "bu sayfayı kodla", "şuna benzet", "bu tasarımı uygula" dediğinde kullan.
---

# Ekran görüntüsünden arayüz

Amaç: görseli **projenin kendi kodu gibi görünen** bir sayfaya çevirmek. Jenerik HTML üretmek değil.

Bu iş üretilen kodu **görmeden** bitmez. Yazdığın sayfayı tarayıcıda açıp orijinal görselle
karşılaştırmadan "bitti" deme.

## Adım 0: Proje profili ve tasarım dili

Önce projenin tasarım belgesini (`DESIGN.md`; proje kökünde ya da ekibin not klasöründe) ve `AGENTS.md` dosyasını ara.

- **Varsa:** baştan sona oku. Kod ve tasarım yazarken tek doğru kaynak odur.
- **Yoksa:** `referans/proje-profili.md` dosyasını oku, profili çıkar, `DESIGN.md` olarak kaydet
  (yeri kullanıcıya sor). Bu bir defalık iş, sonraki çalıştırmalar tüm ajanlarda hızlı olur.

Profili okumadan kod yazma. Yoksa Bootstrap projesine Tailwind, Tailwind projesine Bootstrap yazarsın.

## Adım 0.5: Hangi yüz?

Profil birden fazla **yüz** tanımlıyor olabilir (ör. yönetim paneli Bootstrap, ön yüz Tailwind).
Kod yazmadan önce hedef yüzü belirle: sayfa hangi panele ait, o panelin layout'u hangisi.

Sonra o yüzün kurallarına sadık kal. Bootstrap yüzünde Tailwind sınıfı yazma
(`d-flex gap-2` evet, `flex gap-2` hayır), Tailwind yüzünde Bootstrap sınıfı yazma.
İkisini aynı sayfada karıştırmak bu işin en sık hatası.

Görselden yüz anlaşılmıyorsa adım 3'te sor.

## Adım 1: Görseli oku, envanter çıkar

Görselde ne var, yukarıdan aşağı listele. Her bölüm için:

| Alan | Ne yazılacak |
|---|---|
| Bölüm | breadcrumb / başlık / filtre formu / tablo / kart ızgarası / modal / boş durum |
| İçerik | görseldeki **birebir metinler**, sütun başlıkları, buton etiketleri |
| Veri | statik mi, controller'dan mı gelecek, kaynağı belli mi |
| Etkileşim | tıklanınca ne olur, sayfa mı açar modal mı |

Kurallar:
- Metinleri **birebir** al. Görselde "Sipariş Numarası" yazıyorsa "Sipariş No" yazma.
- Görünmeyen şeyi uydurma. Tablonun 3 satırı görünüyorsa 3 sütun yapısını yaz, 20 satır sahte veri üretme.
- Kırpılmış/yarım görünen bölümü işaretle, adım 2'de sor.

Envanteri kullanıcıya kısa tablo olarak göster.

## Adım 2: Mevcut component'lerle eşle

Profildeki component listesini gez. Her bölüm için:

1. **Birebir karşılayan component var mı?** Varsa onu kullan, prop'larını profilden doğrula.
2. **Yakın bir component var mı?** Varsa onu kullan, farkı utility sınıflarla kapat.
3. **Yoksa** projedeki benzer bir sayfayı referans al ve o kalıbı tekrarla.

Sıfırdan CSS yazmak son çare. Yazman gerekiyorsa profildeki CSS dosya kalıbına uy
(ayrı dosya + `@push('styles')` gibi), inline `<style>` bloğu bırakma.

## Adım 3: Belirsizleri tek seferde sor

Görselden çıkmayan şeyleri **AskUserQuestion ile tek seferde** sor, iş bitene kadar bir daha kesme:

- Sayfa hangi panele ait (yönetim / müşteri paneli / ön yüz)?
- URL ve route adı ne olsun?
- Veri nereden gelecek: mevcut model/tablo mu, sahte veriyle mi başlayalım?
- Yeni sayfa mı, mevcut sayfanın üzerine mi?

Görselde cevabı olan şeyi sorma. Sadece iki farklı cevabın **farklı kod** doğuracağı yerleri sor.

## Adım 4: Yaz

Sırayla: view → route → controller. Profildeki dizin ve isimlendirme kurallarına uy.

- Değişken, dosya, route adları projenin dilinde (Türkçe projede Türkçe).
- Renk, boşluk, köşe yarıçapı için profildeki tema değişkenlerini kullan, hex kodu gömme.
- Responsive davranışı görselden çıkaramıyorsan projedeki benzer sayfa ne yapıyorsa onu yap.
- Sahte veri gerekiyorsa controller'da açıkça `// TODO: gerçek veri` işaretle.

## Adım 5: Doğrulama döngüsü

`referans/dogrulama-dongusu.md` dosyasını oku ve uygula. Özet:

1. Sayfayı tarayıcıda aç (profildeki yerel URL).
2. Ekran görüntüsü al.
3. Orijinal görselle yan yana karşılaştır, farkları listele.
4. Düzelt, tekrar bak.

**En fazla 3 tur.** 3 tur sonunda kalan farklar varsa dur, listele, kullanıcıya sor.
Aynı düzeltmeyi iki kez denediysen üçüncüyü deneme, sor.

## Adım 6: Rapor

Kısa tut:

- Oluşturulan/değiştirilen dosyalar
- Sayfanın açıldığı URL
- Kullanılan mevcut component'ler
- Orijinalden **bilerek** sapılan yerler ve nedeni
- Sahte veriyle bırakılan yerler

## Yapma

- Görseli okumadan kod yazma.
- Profili okumadan component uydurma. `<x-...>` yazmadan önce dosyasının var olduğunu doğrula.
- Görselde olmayan özellik ekleme (dark mode toggle, animasyon, "iyileştirme").
- Tarayıcıda görmeden bitirme.
- Tek turda mükemmeli hedefleme, döngü zaten bunun için var.
