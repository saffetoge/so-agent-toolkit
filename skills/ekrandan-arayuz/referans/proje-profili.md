# Proje profili çıkarma

Amaç: projenin `DESIGN.md` dosyasını üretmek. Bu dosya "bu projede arayüz nasıl yazılır"
sorusunun cevabıdır. Bir kez çıkarılır, sonra tüm ajanlar tarafından hep okunur.

## Önemli: bir projede birden fazla UI dünyası olabilir

Çok yaygın durum: yönetim paneli Bootstrap, pazarlama sayfaları Tailwind. Ya da eski modül
jQuery, yeni modül Alpine. **Bunları karıştırmak en sık yapılan hata.**

Bu yüzden profil, tek bir stack yazmaz. Her **yüz** için ayrı blok yazar. Yüzü belirleyen şey
layout dosyasıdır: farklı layout = farklı yüz.

Tespit yolu: layout dosyalarını bul, her birinin `<head>` bölümünde hangi CSS yükleniyor bak.

- `bootstrap.css`, `card-body`, `row/col-md-*`, `btn btn-*` → **Bootstrap yüzü**
- Tailwind çıktısı CSS, `flex items-center`, `px-4 py-2`, `rounded-lg` → **Tailwind yüzü**
- İkisi de yükleniyorsa: gerçekte hangisinin kullanıldığını **örnek sayfalardan** anla,
  head'deki dosya listesinden değil. Legacy tema dosyaları duruyor ama kullanılmıyor olabilir.

Aynı sayfada iki sistemi karıştırma. Bootstrap yüzünde `d-flex gap-2` yaz, `flex gap-2` değil.

## Toplanacaklar

### 1. Yüzler
Her layout için: dosya yolu, hangi CSS framework, hangi ikon seti, hangi JS
(jQuery / Alpine / Livewire / vanilla), hangi bölümleri var (`@yield`, `@section`, `@push`).

### 2. Component envanteri
Component dizinini tara. Her component için **tek satır**: ne işe yarar + prop imzası.
Prop'lar için dosyanın ilk satırlarına bak (`@props`, `$title` gibi değişkenler).
Sadece isim listesi yazma, prop'suz liste işe yaramaz.

### 3. Tema değişkenleri
CSS custom property'leri bul (`--*-primary`, `--*-radius`, `--*-surface`). Marka rengini,
yüzey/metin/kenarlık renklerini, yarıçapları, gölgeleri not al. Hex kodları profile yaz ki
kod yazarken hex gömmek yerine değişken kullanılsın.

### 4. Altın standart sayfalar
Her yüz için 1 tane **temiz, güncel** örnek sayfa seç ve yolunu yaz. Tercihen bir liste
sayfası (breadcrumb + filtre formu + tablo içerir, en çok kalıbı barındırır). Yeni sayfa
yazarken bu dosya taklit edilir.

Seçim ölçütü: yeni tarihli, component kullanan, inline stil içermeyen sayfa.

### 5. Dizin ve isim kuralları
View nereye, CSS nereye, route hangi dosyaya, controller nerede, route adı nasıl
(`panel.modul.aksiyon` gibi), dil (Türkçe/İngilizce isimlendirme).

### 6. Yerel URL
Sayfayı tarayıcıda açmak için gereken taban adres ve giriş gereksinimi.
Laravel Herd'de klasör adı `<isim>.test` olur. Panel sayfaları giriş istiyorsa bunu not et.

## Çıkarma yolu

Sırayla:

1. `package.json` + `composer.json` (ya da dilin karşılığı) → framework ve sürümler
2. Layout dosyalarını bul, `<head>` bölümlerini oku → yüzleri ayır
3. Component dizinini tara, prop imzalarını çıkar
4. Tema CSS dosyasında custom property'leri grep'le
5. Her yüz için altın standart sayfayı seç ve oku
6. Route dosyalarına bak → adlandırma kalıbı

## Yazım kuralları

- **Kısa tut.** Her satır kod yazarken işe yaramalı. Anlatı yazma.
- Component listesi tablo olsun: isim, ne yapar, prop'lar.
- Emin olmadığın şeyi "belirsiz" diye işaretle, uydurma.
- Tarih ve proje adını başa yaz, profil eskidiğinde belli olsun.
