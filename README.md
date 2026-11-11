# so-agent-toolkit

AI kodlama ajanları için Türkçe skill ve ajan seti. Günlük yazılım işinde tekrar eden işleri (SEO denetimi,
güvenlik denetimi, hata araştırması, mimari denetim, mobil uygulama, PDF rapor, arayüz kodlama) yöntemiyle
birlikte verir; ajanlar bu işleri plan, test, güvenlik ve kullanıcı deneyimi rollerine böler.

Skill'ler `SKILL.md` biçimindedir: Claude Code, Codex ve bu biçimi okuyan diğer ajanlarda kullanılabilir.
Metinler ve raporlar Türkçedir.

## Kurulum

### Claude Code (eklenti olarak)

Claude Code içinde:

```
/plugin marketplace add saffetoge/so-agent-toolkit
/plugin install so-agent-toolkit@so-agent-toolkit
```

Terminalden aynı işlem:

```bash
claude plugin marketplace add saffetoge/so-agent-toolkit
claude plugin install so-agent-toolkit@so-agent-toolkit
```

Skill'ler `so-agent-toolkit:` önekiyle görünür (ör. `so-agent-toolkit:seo-kontrol`).

### Diğer ajanlar ya da elle kurulum

Depoyu indir, istediğin skill klasörünü kullandığın aracın skill dizinine kopyala: Claude Code'da
`~/.claude/skills/`, Codex'te `~/.codex/skills/`; tek proje için projenin kendi skill klasörü.

`agents/` altındaki tanımlar Claude Code alt-ajan biçimindedir (`~/.claude/agents/`). Başka araçta rol tarifi
olarak uyarlanabilir.

## Skill'ler

| Skill | Ne yapar |
|---|---|
| `seo-kontrol` | Teknik SEO, içerik, paylaşım önizlemesi, indekslenme ve AI aramalarında görünürlük denetimi; SEO altyapısı kurulum standardı, tarama betiği ve HTML rapor |
| `security-audit` | Kanıta dayalı, savunma amaçlı güvenlik denetimi: kontrol listesi, önceliklendirme, güvenli düzeltme ve rapor kalıbı |
| `derin-arastirma` | Hata ya da dış servis sorununda tahmin yerine belgenin tamamını okuma, ölçme ve kanıta bağlı rapor yöntemi |
| `architecture-guardian` | Mimari sapma, kopya iş kuralı, tek kaynak (SSOT), modülerlik ve taşınabilirlik denetimi |
| `acik-kod-yorumu` | Tarayıcıya giden JS, CSS ve HTML yorumlarında iç ayrıntı bırakmama kuralı ve temizleme yöntemi |
| `ekrandan-arayuz` | Ekran görüntüsü ya da tasarım çıktısını projenin kendi bileşenleriyle koda çevirir, tarayıcıda karşılaştırarak doğrular |
| `mobil-uygulama` | Mevcut siteye bağlı React Native (Expo) uygulaması: API sözleşmesi, ödeme, push bildirimi, mağaza kuralları, güvenlik ve test |
| `chrome-eklenti` | Manifest V3 Chrome eklentisi iskeleti, sık yapılan hatalar ve tarayıcıda test adımları |
| `pdf-rapor` | Kurumsal tasarımlı, infografikli A4 PDF rapor; şablon ve bileşen galerisiyle |
| `pdf-kucult` | Taranmış ya da görsel ağırlıklı PDF'i çözünürlüğü bozmadan küçültür ve çıktıyı doğrular |
| `ai-haber-gorseli` | Yapay zeka ve teknoloji haberini doğrulayıp 9:16 dikey paylaşım görseline çevirir |

## Ajanlar (Claude Code alt-ajan biçimi)

| Ajan | Görev | Yazma yetkisi |
|---|---|---|
| `takim-lideri` | İşi planlar, üretim kodunu yazar, diğer ajanlara dağıtır, sonucu doğrular. `claude --agent takim-lideri` ile başlatılır | Var |
| `guvenlik-ajani` | Değişikliği ya da projeyi güvenlik açısından inceler, bulguları kanıtla raporlar | Yok |
| `test-yazici` | Verilen kabul ölçütlerine göre test yazar ve çalıştırır | Yalnız test klasörleri |
| `test-denetci` | Test kapısını çalıştırır, testlerin gerçekten davranış ölçüp ölçmediğini denetler | Yok |
| `kullanici-deneyimi` | Uygulamayı tarayıcıda kullanıcı gibi gezer; akış, etiket, hata mesajı ve mobil görünüm sorunlarını raporlar | Yok |

## Gereksinimler

| Skill ya da ajan | Gereken |
|---|---|
| `pdf-rapor`, `ai-haber-gorseli` | macOS ve Google Chrome |
| `pdf-kucult`, `pdf-rapor` (sayfa kontrolü) | `uv` |
| `seo-kontrol` | Python 3 (ek paket gerekmez) |
| `chrome-eklenti` (ikon üretimi) | macOS `sips` |
| `ai-haber-gorseli` (telefona gönderme) | macOS, Swift derleyicisi, AirDrop |
| `kullanici-deneyimi`, `ekrandan-arayuz` | Claude in Chrome tarayıcı eklentisi |

Bazı skill'ler birbirine atıf yapar (ör. `mobil-uygulama` içinden `security-audit` ve `seo-kontrol`); birlikte
kurulduğunda bu atıflar çalışır.

## Notlar

- Skill'lerdeki örnek adlar, tutarlar ve vakalar kurgudur ya da genelleştirilmiştir.
- Laravel örnekleri ağırlıklıdır; yöntemlerin çoğu çatıdan bağımsızdır.
- `seo-kontrol` regresyon testleri: `python3 -I skills/seo-kontrol/scripts/kontrol-testleri.py`
- Eklenti doğrulaması: `claude plugin validate .`

## Lisans

MIT. Ayrıntı `LICENSE` dosyasında.
