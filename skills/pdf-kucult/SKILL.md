---
name: pdf-kucult
description: PDF dosyasının boyutunu küçültür. Taranmış/görsel ağırlıklı PDF'lerde çözünürlük bozmadan JPEG'leri yeniden kodlar, çıktıyı orijinalle karşılaştırıp doğrular. Kullanıcı "pdf küçült", "bu pdf'i sıkıştır", "boyutunu yarıya indir", "dosya çok büyük maille gönderemiyorum" dediğinde kullan.
---

# PDF Küçültme

`gs`, `qpdf`, `pdfimages` ya da ImageMagick gerekmez. Sıkıştırma `uv run --with ...`
ile geçici ortamda pikepdf + Pillow üzerinden yapılır, kurulum gerekmez.

Bu klasördeki iki script kullanılır (yolları tam yaz, `$SKILL_DIR` = bu SKILL.md'nin klasörü):
- `sikistir.py` - JPEG'leri yeniden kodlar
- `dogrula.py` - çıktıyı orijinalle karşılaştırır

## 1. Önce analiz et

Boyut nereden geliyor, bilmeden sıkıştırma:

```bash
uv run --quiet --with pymupdf python -c "
import pymupdf, sys
d = pymupdf.open(sys.argv[1])
tot = 0
for p in d:
    for img in p.get_images(full=True):
        i = d.extract_image(img[0])
        tot += len(i['image'])
        print(p.number+1, i['ext'], f\"{img[2]}x{img[3]}\", i['cs-name'], round(len(i['image'])/1024), 'KB')
print('sayfa:', len(d), '| gorsel toplam KB:', round(tot/1024))
print('metin var mi:', bool(d[0].get_text().strip()))
" DOSYA.pdf
```

Yorumla:
- **Görseller dosyanın büyük kısmı, metin yok** → taranmış belge, bu skill'in tam hedefi, adım 2'ye geç.
- **Görseller küçük, dosya yine de büyük** → şişkinlik gömülü fontlar/gereksiz nesnelerdedir.
  Sadece yapısal temizlik yap, kalite kaybı olmaz:
  `uv run --quiet --with pikepdf python -c "import pikepdf,sys; p=pikepdf.open(sys.argv[1]); p.save(sys.argv[2], compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)" GIRDI.pdf CIKTI.pdf`
- **Görseller PNG/Flate** (taranmış değil, ekran görüntüsü vb.) → `sikistir.py` bunlara dokunmaz,
  kullanıcıya söyle; gerekirse ayrıca ele al.

## 2. Birkaç kalitede dene, sonucu kullanıcıya sun

Tek bir kaliteye karar verip dayatma. Scratchpad'de 2-3 deneme üret, boyutları göster:

```bash
for q in 85 75 65; do
  uv run --quiet --with pikepdf --with pillow python "$SKILL_DIR/sikistir.py" GIRDI.pdf "deneme_q$q.pdf" $q
  printf "q=%s -> %s\n" "$q" "$(du -h deneme_q$q.pdf | cut -f1)"
done
```

Kaba karşılık (taranmış A4 evrak): q85 ≈ %60, q75 ≈ %70, q65 ≈ %78 küçülme.
Kullanıcının hedefini karşılayan **en yüksek kaliteyi** öner, diğerlerini seçenek olarak söyle.

**Çözünürlük düşürme** (`im.resize`) son çare. Küçük punto metni okunmaz hale getirir;
sadece kullanıcı açıkça isterse ve mutlaka yakın plan kontrolüyle.

## 3. Doğrula - bu adımı atlama

Bozuk çıktı sessizce oluşabilir (simsiyah sayfa, kaymış renk). Her zaman kontrol et:

```bash
uv run --quiet --with pymupdf python "$SKILL_DIR/dogrula.py" GIRDI.pdf deneme_q75.pdf SCRATCHPAD
```

Sonra üretilen `yakin_plan.png`'i **Read ile aç ve gerçekten bak**. Metin net değilse
kaliteyi yükselt. Ortalama piksel farkı < 0,5/255 ise gözle ayırt edilemez sayılır.

## 4. Yaz

- Orijinali **asla üzerine yazma**. Çıktı `<isim>_kucuk.pdf` olsun, aynı klasöre.
- Kullanıcıya "eski boyut → yeni boyut (%N)" ve kalan seçenekleri tek satırda bildir.

## Tuzaklar

- **PyMuPDF `update_stream` ile JPEG değiştirme.** Filtreyi FlateDecode yapar, `/DCTDecode`
  beklentisiyle çakışır, sayfalar **simsiyah** çıkar. Bu yüzden pikepdf +
  `obj.write(veri, filter=pikepdf.Name.DCTDecode)` kullanılıyor.
- **CMYK / ayrışık renk uzayı görseller.** `sikistir.py` bunları atlar; RGB'ye çevirmek
  renkleri kaydırır. Böyle bir dosyada kazanç azsa kullanıcıya nedenini söyle.
- **Zaten sıkıştırılmış dosya.** Yeni JPEG orijinalden büyükse script o görseli atlar,
  yani sonuç büyümez. Kazanç yoksa "bu dosya zaten optimize" de, kaliteyi zorlama.
- **İmzalı PDF.** Yeniden kaydetmek dijital imzayı geçersiz kılar. Belge imzalıysa
  (`/Sig` alanı) sıkıştırmadan önce kullanıcıyı uyar.
