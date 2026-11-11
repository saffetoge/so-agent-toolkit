---
name: pdf-rapor
description: Kurumsal tasarımlı, infografikli PDF rapor hazırlar. Charter serif, teal vurgu, sabit A4 sayfa düzeni, KPI şeridi, bar, donut, zaman çizelgesi ve karşılaştırma tabloları hazır gelir. Kullanıcı "pdf rapor yap/oluştur", "bunu pdf olarak hazırla", "rapor çıkar", "pdf'e dök", "teklif hazırla", "sunum için belge hazırla" dediğinde kullan.
---

# Kurumsal PDF rapor

HTML yazılır, Chrome ile A4 PDF'e basılır. Sistemde pandoc/wkhtmltopdf yok, Chrome var.

Skill klasörü (`<skill-dizini>`): bu SKILL.md dosyasının bulunduğu klasör
- `sablon.html` : tüm stiller + kapak ve içerik sayfası iskeleti
- `parcalar.html` : bileşen galerisi, kopyala yapıştır

## Akış

1. Eksik künye bilgilerini sor (aşağıda).
2. `sablon.html`'i kopyala, sayfaları kur, içeriği yaz.
3. Chrome ile PDF'e bas.
4. **Her sayfayı görsel olarak kontrol et.** Bu adım atlanmaz.
5. Dosya yolunu ver.

## 1. Önce sor

Kullanıcı vermediyse tek seferde sor, tahmin etme:

- **Marka / firma adı** (üst barda ve alt bilgide çıkar)
- **Belge türü** (rapor, ticari teklif, analiz, inceleme notu)
- **Hazırlayan** ve varsa **belge no**

Tarih bugünün tarihidir. Kapsam ve başlık içerikten çıkar.

## 2. Sayfaları kur

```bash
cp <skill-dizini>/sablon.html /tmp/rapor.html
```

Her sayfa bir `<section class="s">`. Üst bar ve alt bilgi her sayfanın içine tekrar
yazılır, sayfa numarası CSS sayacıyla kendiliğinden artar. Kapak `class="s kapak"`.

**Sayfa kapasitesi:** içerik alanı 174 × 258 mm. Kabaca 40 satır düz metin, ya da
bir başlık + iki paragraf + iki orta boy bileşen. Taşarsa sessizce bozulmaz, sayfa
sayısı beklenenden fazla çıkar ve 4. adımda yakalanır.

Sayfa dolmuyorsa zorla doldurma, boş alan kurumsal duruyor.

### Dil

Referans dil bu: kısa, ölçülü, satış cümlesi yok.

- Türkçe. **Uzun tire (—) kullanma**, yerine normal tire, virgül ya da iki cümle.
- Teknik terimi geçirdiğin cümlede sade karşılığını da ver:
  "Yönlendirici katman: gelen isteği doğru cihaza dağıtan takım lideri."
- Sıfat değil rakam: "çok hızlı" değil, "1,8 sn ortalama yanıt".
- Kesin olmayan rakamın başına `≈` koy, dipnotta neden yaklaşık olduğunu yaz.
- Ölçmediğin şeyi ölçmüş gibi yazma. Ayrı bir `<div class="kutu uyari">` açıp
  "ölçülmedi, kaynak üretici beyanı" de.
- Yapılmayan işi "yapıldı" diye yazma, **Eksikler** bölümü aç.
- Bölüm sonunda karar cümlesi kur: "Tercihi belirleyen soru: ... ise A, ... ise B."

### Tasarım

Palet ve tipografi `sablon.html` içinde sabit, değiştirme. Kullanıcı ayrı bir kurumsal
renk verirse yalnızca `--vurgu` değişkenini değiştir, gerisine dokunma.

- Sayfa başına en fazla **iki** infografik. Üçüncüsü sayfayı kalabalıklaştırır.
- Her infografiğin üstünde onu okutan bir başlık ya da cümle olsun.
- Ölçülmüş sayı varsa bar ya da KPI kullan; derece daireleri (harvey ball) sadece
  ölçülemeyen boyutlar için.
- Aynı sayfada iki farklı grafik türünü tekrarlama.

### Bileşenler

`parcalar.html` içinde hazır, her birinin üstünde ne zaman kullanılacağı yazılı:

| Bileşen | Ne için |
|---|---|
| `kpi-serit` | Raporun en önemli 3-4 rakamı |
| Açıklamalı tablo | Bileşen/görev, kalem/karşılık anlatımı |
| Bedel tablosu | Maliyet, süre, adet dökümü, teal toplam satırı |
| `derece` | İki seçeneğin ölçülemeyen boyutlarda kıyası |
| `barlar` | Aynı birimde ölçülmüş değerlerin kıyası |
| `pay` | Bir bütünün dağılımı, yüzdeler 100'e tamamlanır |
| `donut` | Tek bir oranı öne çıkarma, en fazla 3 tane |
| `zaman` | Plan, yol haritası, olay sırası |
| `akis` | 3-4 adımlı süreç |
| `kutu` | Uyarı, kısıt, eksik iş (bilgi/iyi/uyari/kotu) |
| `rozet` | Tablo hücresinde kısa durum |
| `icindekiler` | 5 sayfadan uzun raporlarda |

## 3. PDF'e bas

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=4000 \
  --print-to-pdf="$HOME/Documents/rapor.pdf" \
  "file:///tmp/rapor.html" 2>&1 | grep -i written
```

- `--no-pdf-header-footer` şart, yoksa Chrome üste dosya yolunu alta tarihi basar.
- Çıktı yolu mutlak olmalı, `~` genişlemez.
- Chrome açıkken de çalışır.

## 4. Kontrol et

Önce sayfa sayısı HTML'deki `<section>` sayısıyla aynı mı: fazlaysa bir sayfa taşmış.

```bash
grep -c '<section class="s' /tmp/rapor.html
cd /tmp && uv run --quiet --with pypdfium2 --with pillow python -c "
import pypdfium2 as p
d = p.PdfDocument('$HOME/Documents/rapor.pdf')
for i in range(len(d)): d[i].render(scale=1.7).to_pil().save(f'/tmp/sayfa{i+1}.png')
print('sayfa sayısı:', len(d))"
```

Sonra `/tmp/sayfa1.png`, `/tmp/sayfa2.png` ... dosyalarını **Read ile aç ve bak**.
Aranacaklar: taşan tablo, üst üste binen bileşen, yarım kalan başlık, boş kalmış
sayfa sonu, yanlış sayfa numarası. Bulursan HTML'i düzelt, 3. adımı tekrarla.

`uv` yoksa yalnız ilk sayfa için: `sips -s format png --out /tmp/s1.png rapor.pdf`

## Dosya büyükse

Görsel ağırlıklı raporda dosya şişerse `pdf-kucult` skill'ini kullan.
