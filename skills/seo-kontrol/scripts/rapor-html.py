#!/usr/bin/env python3
"""
SEO kontrol sonucunu HTML kontrol listesine çevirir (Artifact olarak yayınlanmaya hazır, tek dosya).

Kullanım:
    python3 -I rapor-html.py sonuc.json [ek.json] > rapor.html

ek.json (isteğe bağlı, bizim site için kod/veri bulguları):
{
  "baslik": "Örnek Site SEO Kontrolü",
  "ozet": "Tek paragraf sonuç.",
  "gecersiz_kil": {"olcum_ga4": {"durum": "kismi", "kanit": "..."}},   # bizim sitenin HTML sonucunu kodla düzeltir
  "kod": {"kod_indexnow": {"durum": "yok", "kanit": "...", "yer": "dosya:satır"}},
  "yerler": {"og_gorsel_anasayfa": "app/Support/Seo/SeoSunum.php:117"},   # bizde eksik satırın kod yeri
  "plan": ["1. adım", "2. adım"],
  "kararlar": ["..."],
  "kisitlar": ["..."]
}
"""
import html
import json
import os
import sys
import secrets
from pathlib import Path

E = html.escape
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TANIM = json.loads(Path(KOK, 'references', 'kontroller.json').read_text(encoding='utf-8'))
ETIKET = {'var': 'Var', 'kismi': 'Kısmi', 'yok': 'Yok', 'olcumsuz': 'Ölçülemedi', 'uygulanamaz': 'Uygulanamaz'}
ISARET = {'var': '✓', 'kismi': '◐', 'yok': '✕', 'olcumsuz': '?', 'uygulanamaz': '∅'}
ONCELIK_SIRA = {'Yüksek': 0, 'Orta': 1, 'Düşük': 2}
DAYANAK = {'resmi_gereksinim': 'Resmî gereksinim', 'resmi_oneri': 'Resmî öneri', 'platform': 'Platform özelliği', 'deneyim': 'Deneyime dayalı öneri'}


def rozet(durum):
    return f'<span class="rozet r-{E(durum)}"><span aria-hidden="true">{ISARET.get(durum, "–")}</span> {ETIKET.get(durum, "Ölçülmedi")}</span>'


def main():
    sonuc = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    ek = json.loads(Path(sys.argv[2]).read_text(encoding='utf-8')) if len(sys.argv) > 2 else {}
    siteler = sonuc['siteler']
    biz = next((s for s in siteler if s.get('biz')), siteler[0])
    for kimlik, deger in (ek.get('gecersiz_kil') or {}).items():
        if deger.get('durum') not in ETIKET or not deger.get('kanit', '').strip():
            raise ValueError(f'Geçerli durum ve somut kanıt gerekli: {kimlik}')
        onceki = biz['kontroller'].get(kimlik, {})
        biz['kontroller'][kimlik] = dict(deger, kanit='HTML bulgusu: ' + onceki.get('kanit', 'Ölçülmedi') + ' | Kod/elle doğrulama: ' + deger.get('kanit', ''))
    for kimlik, deger in (ek.get('kod') or {}).items():
        if deger.get('durum') not in ETIKET or not deger.get('kanit', '').strip():
            raise ValueError(f'Geçerli durum ve somut kanıt gerekli: {kimlik}')
        biz['kontroller'][kimlik] = deger
    yerler = dict(ek.get('yerler') or {})
    for kimlik, deger in (ek.get('kod') or {}).items():
        if deger.get('yer'):
            yerler[kimlik] = deger['yer']

    tanimlar = TANIM['kontroller']
    sayim = []
    for s in siteler:
        olculen = [t for t in tanimlar if t['grup'] != 'kod' or s is biz]
        d = [s['kontroller'].get(t['kimlik'], {}).get('durum', 'olcumsuz') for t in olculen]
        sayim.append({x: d.count(x) for x in ETIKET})

    baslik = ek.get('baslik') or f'{biz["ad"]} SEO Kontrolü'
    p = []
    nonce = secrets.token_urlsafe(24)
    p.append(f'''<!doctype html>
<html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'nonce-{nonce}'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; base-uri 'none'; form-action 'none'">
<title>{E(baslik)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@400&display=swap">
<style>
/* Düzen: üstte site başına sayım şeridi, altında gruplu kontrol tabloları; tablo dar ekranda kendi içinde kayar. */
:root {{
  --zemin: #f5f6f8; --yuzey: #ffffff; --murekkep: #1b2230; --soluk: #5d6677; --cizgi: #dfe3ea;
  --vurgu: #2347c5; --vurgu-zemin: #e6ebfb;
  --var: #1c7a4a; --var-zemin: #e2f3ea; --kismi: #96620a; --kismi-zemin: #fbf0d9;
  --yok: #b3261e; --yok-zemin: #fbe4e2; --olcumsuz: #6b7280; --olcumsuz-zemin: #eef0f3;
  --baslik-yazi: "Bricolage Grotesque", "Avenir Next", system-ui, sans-serif;
  --govde-yazi: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --kod-yazi: "JetBrains Mono", ui-monospace, Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --zemin: #11151c; --yuzey: #181e28; --murekkep: #e6e9ef; --soluk: #9aa3b2; --cizgi: #2a3240;
  --vurgu: #8aa4ff; --vurgu-zemin: #1e2a4d;
  --var: #5fd39a; --var-zemin: #15302a; --kismi: #f2c062; --kismi-zemin: #33290f;
  --yok: #ff8a80; --yok-zemin: #3a1b1a; --olcumsuz: #9aa3b2; --olcumsuz-zemin: #222a35; color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --zemin: #11151c; --yuzey: #181e28; --murekkep: #e6e9ef; --soluk: #9aa3b2; --cizgi: #2a3240;
  --vurgu: #8aa4ff; --vurgu-zemin: #1e2a4d;
  --var: #5fd39a; --var-zemin: #15302a; --kismi: #f2c062; --kismi-zemin: #33290f;
  --yok: #ff8a80; --yok-zemin: #3a1b1a; --olcumsuz: #9aa3b2; --olcumsuz-zemin: #222a35; color-scheme: dark; }}
* {{ box-sizing: border-box; }}
[hidden] {{ display: none !important; }}
a {{ color: var(--vurgu); }}
body {{ background: var(--zemin); color: var(--murekkep); font: 16px/1.55 var(--govde-yazi); }}
.sar {{ max-width: 1240px; margin: 0 auto; padding-block: 32px 64px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); display: grid; gap: 28px; }}
h1, h2, h3 {{ font-family: var(--baslik-yazi); text-wrap: balance; margin: 0; letter-spacing: -0.01em; }}
h1 {{ font-size: clamp(28px, 4vw, 40px); line-height: 1.1; }}
h2 {{ font-size: 22px; }}
.ust {{ display: grid; gap: 10px; }}
.etiket {{ font: 12px/1 var(--kod-yazi); text-transform: uppercase; letter-spacing: 0.08em; color: var(--soluk); }}
.ozet {{ max-width: 72ch; color: var(--murekkep); margin: 0; }}
.serit {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }}
.site {{ background: var(--yuzey); border: 1px solid var(--cizgi); border-radius: 10px; padding: 16px; display: grid; gap: 10px; min-width: 0; }}
.site.biz {{ border-color: var(--vurgu); box-shadow: inset 0 0 0 1px var(--vurgu); }}
.site-ad {{ display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }}
.site-ad strong {{ font-family: var(--baslik-yazi); font-size: 18px; }}
.site-kok {{ font: 12px var(--kod-yazi); color: var(--soluk); overflow-wrap: anywhere; }}
.cubuk {{ display: flex; height: 8px; border-radius: 4px; overflow: hidden; background: var(--olcumsuz-zemin); }}
.cubuk span {{ display: block; height: 100%; }}
.c-var {{ background: var(--var); }} .c-kismi {{ background: var(--kismi); }} .c-yok {{ background: var(--yok); }}
.c-olcumsuz {{ background: var(--olcumsuz); }} .c-uygulanamaz {{ background: var(--cizgi); }}
.sayilar {{ display: flex; gap: 14px; flex-wrap: wrap; font-variant-numeric: tabular-nums; font-size: 14px; color: var(--soluk); }}
.sayilar b {{ color: var(--murekkep); font-size: 18px; margin-right: 3px; }}
.suzgec {{ display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }}
.suzgec button {{ font: 600 14px var(--govde-yazi); padding: 7px 12px; border-radius: 999px; border: 1px solid var(--cizgi); background: var(--yuzey); color: var(--murekkep); cursor: pointer; }}
.suzgec button[aria-pressed="true"] {{ background: var(--vurgu); border-color: var(--vurgu); color: var(--yuzey); }}
.suzgec button:focus-visible {{ outline: 2px solid var(--vurgu); outline-offset: 2px; }}
.grup {{ display: grid; gap: 10px; }}
.kaydir {{ overflow-x: auto; background: var(--yuzey); border: 1px solid var(--cizgi); border-radius: 10px; }}
table {{ border-collapse: collapse; width: 100%; min-width: 920px; font-size: 14px; }}
th, td {{ text-align: left; vertical-align: top; padding: 10px 12px; border-bottom: 1px solid var(--cizgi); }}
th {{ font: 600 12px var(--govde-yazi); text-transform: uppercase; letter-spacing: 0.06em; color: var(--soluk); background: var(--zemin); position: sticky; top: 0; }}
tr:last-child td {{ border-bottom: 0; }}
td.ad {{ width: 24%; }} td.ad strong {{ display: block; font-weight: 600; }}
td.ad small, .kanit {{ color: var(--soluk); font-size: 12.5px; }}
.kanit {{ display: block; margin-top: 4px; font-family: var(--kod-yazi); font-size: 11.5px; overflow-wrap: anywhere; }}
td.cozum {{ width: 26%; }}
.yer {{ display: block; margin-top: 4px; font: 11.5px var(--kod-yazi); color: var(--vurgu); overflow-wrap: anywhere; }}
.rozet {{ display: inline-flex; gap: 4px; align-items: center; white-space: nowrap; font-weight: 600; font-size: 12.5px; padding: 2px 8px; border-radius: 999px; }}
.r-var {{ color: var(--var); background: var(--var-zemin); }} .r-kismi {{ color: var(--kismi); background: var(--kismi-zemin); }}
.r-yok {{ color: var(--yok); background: var(--yok-zemin); }} .r-olcumsuz {{ color: var(--olcumsuz); background: var(--olcumsuz-zemin); }}
.r-uygulanamaz {{ color: var(--soluk); background: var(--zemin); }}
.oncelik {{ font: 600 12px var(--govde-yazi); white-space: nowrap; }}
.o-Yüksek {{ color: var(--yok); }} .o-Orta {{ color: var(--kismi); }} .o-Düşük {{ color: var(--soluk); }}
.rakipte {{ display: inline-block; margin-top: 6px; font-size: 11.5px; font-weight: 600; color: var(--vurgu); background: var(--vurgu-zemin); padding: 1px 7px; border-radius: 4px; }}
.bolum {{ background: var(--yuzey); border: 1px solid var(--cizgi); border-radius: 10px; padding: 18px 20px; display: grid; gap: 10px; }}
.bolum ol, .bolum ul {{ margin: 0; padding-left: 22px; display: grid; gap: 6px; max-width: 90ch; }}
.ikili {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 320px), 1fr)); gap: 16px; }}
.bos {{ color: var(--soluk); font-style: italic; }}
@media (prefers-reduced-motion: no-preference) {{ .suzgec button {{ transition: background .15s; }} }}
</style>
</head><body>
<div class="sar">
<header class="ust">
  <span class="etiket">SEO kontrol listesi · {E(sonuc.get("tarih", ""))}</span>
  <h1>{E(baslik)}</h1>
  <p class="ozet">{E(ek.get("ozet", ""))}</p>
  <p class="ozet">Bu sayımlar Google sıralama puanı değildir. Ölçülemedi ve uygulanamaz maddeler başarısızlık sayılmaz. Örneklem ve erişim koşulları siteler arasında farklı olabilir.</p>
</header>
<section class="serit" aria-label="Site özetleri">''')
    for s, c in zip(siteler, sayim):
        toplam = max(1, sum(c.values()))
        p.append(f'''<div class="site{' biz' if s is biz else ''}">
  <div class="site-ad"><strong>{E(s["ad"])}</strong><span class="etiket">{"Biz" if s is biz else "Rakip"}</span></div>
  <span class="site-kok">{E(s["kok"])}</span>
  <div class="cubuk" role="img" aria-label="{c['var']} var, {c['kismi']} kısmi, {c['yok']} yok, {c['olcumsuz']} ölçülemedi, {c['uygulanamaz']} uygulanamaz">
    <span class="c-var" style="width:{c['var'] * 100 / toplam:.1f}%"></span><span class="c-kismi" style="width:{c['kismi'] * 100 / toplam:.1f}%"></span><span class="c-yok" style="width:{c['yok'] * 100 / toplam:.1f}%"></span><span class="c-olcumsuz" style="width:{c['olcumsuz'] * 100 / toplam:.1f}%"></span><span class="c-uygulanamaz" style="width:{c['uygulanamaz'] * 100 / toplam:.1f}%"></span>
  </div>
  <div class="sayilar"><span><b>{c['var']}</b>var</span><span><b>{c['kismi']}</b>kısmi</span><span><b>{c['yok']}</b>yok</span><span><b>{c['olcumsuz']}</b>ölçülemedi</span><span><b>{c['uygulanamaz']}</b>uygulanamaz</span></div>
</div>''')
    p.append('''</section>
<div class="suzgec" role="toolbar" aria-label="Süzgeç">
  <span class="etiket">Göster</span>
  <button type="button" id="s-tumu" data-suzgec="tumu" aria-pressed="true">Tümü</button>
  <button type="button" id="s-eksik" data-suzgec="eksik" aria-pressed="false">Bizde eksik</button>
  <button type="button" id="s-rakip" data-suzgec="rakip" aria-pressed="false">Rakipte var, bizde yok</button>
  <button type="button" id="s-yuksek" data-suzgec="yuksek" aria-pressed="false">Yüksek öncelikli eksik</button>
  <button type="button" data-suzgec="olcumsuz" aria-pressed="false">Doğrulama bekleyen</button>
</div>''')

    ozetler = biz.get('sayfa_ozetleri', [])
    if ozetler:
        turler = {'anasayfa': 'Ana sayfa', 'urun': 'Ürün', 'kategori': 'Kategori', 'kategori_sayfa2': 'Kategori, ikinci sayfa', 'blog': 'Yazı', 'hizmet': 'Hizmet'}
        p.append('<section class="bolum"><h2>Sayfa bazında özet ve arama önizlemesi</h2><p class="bos">Metin önizlemesi tahminidir; Google başlık ve açıklamayı farklı oluşturabilir. Anlam, okunabilirlik ve arama niyeti editoryal olarak değerlendirilir.</p>')
        for o in ozetler:
            ek_bag = f'<br>Alt başlık (H2/H3): {int(o.get("alt_baslik_sayisi", 0))} · Bağlantı: {int(o.get("ic_link", 0))} iç / {int(o.get("dis_link", 0))} dış' if 'ic_link' in o else ''
            p.append(f'<article class="bolum"><h3>{E(turler.get(o.get("tur"), "Diğer sayfa"))}</h3><span class="site-kok">{E(o["url"])}</span><strong>{E(o.get("title") or "Başlık bulunamadı")}</strong><p>{E(o.get("description") or "Meta açıklama bulunamadı; sonuç metni içerikten oluşturulabilir.")}</p><span class="kanit">Tercih edilen adres: {E(o.get("canonical") or "Etiket bulunamadı")}<br>Ana başlık: {E(" / ".join(o.get("h1", [])) or "Bulunamadı")}{ek_bag}<br>Paylaşım görseli: {E(o.get("og_image") or "Bulunamadı")}</span></article>')
        p.append('</section>')

    for grup in TANIM['gruplar']:
        satirlar = [t for t in tanimlar if t['grup'] == grup['kimlik']]
        if not satirlar:
            continue
        kod_grubu = grup['kimlik'] == 'kod'
        sutunlar = [biz] if kod_grubu else siteler
        p.append(f'<section class="grup" data-grup="{E(grup["kimlik"])}"><h2>{E(grup["ad"])}</h2><div class="kaydir"><table><thead><tr><th>Kontrol</th><th>Öncelik</th>')
        for s in sutunlar:
            p.append(f'<th>{E(s["ad"])}</th>')
        p.append('<th>Çözüm</th></tr></thead><tbody>')
        for t in sorted(satirlar, key=lambda x: ONCELIK_SIRA.get(x['oncelik'], 3)):
            bd = biz['kontroller'].get(t['kimlik'], {}).get('durum', 'olcumsuz')
            rakip_var = any(
                s['kontroller'].get(t['kimlik'], {}).get('durum') == 'var'
                or (bd == 'yok' and s['kontroller'].get(t['kimlik'], {}).get('durum') == 'kismi')
                for s in siteler if s is not biz
            )
            eksik = bd in ('yok', 'kismi')
            p.append(f'<tr data-eksik="{int(eksik)}" data-rakip="{int(eksik and rakip_var)}" data-yuksek="{int(eksik and t["oncelik"] == "Yüksek")}" data-olcumsuz="{int(bd == "olcumsuz")}">')
            kaynaklar = ' '.join(f'<a href="{E(adres, quote=True)}" target="_blank" rel="noopener noreferrer">Kaynak {i}</a>' for i, adres in enumerate(t.get('kaynaklar', []), 1) if adres.startswith('https://'))
            p.append(f'<td class="ad"><strong>{E(t["ad"])}</strong><small>{E(t["neden"])}</small><span class="kanit">{E(DAYANAK.get(t.get("dayanak_turu"), "Deneyime dayalı öneri"))} {kaynaklar}</span></td>')
            p.append(f'<td><span class="oncelik o-{E(t["oncelik"])}">{E(t["oncelik"])}</span></td>')
            for s in sutunlar:
                v = s['kontroller'].get(t['kimlik'], {'durum': 'olcumsuz', 'kanit': ''})
                ek_rozet = '<span class="rakipte">Rakipte var</span>' if s is biz and eksik and rakip_var else ''
                p.append(f'<td>{rozet(v["durum"])}{ek_rozet}<span class="kanit">{E(v.get("kanit", ""))}</span></td>')
            yer = f'<span class="yer">{E(yerler[t["kimlik"]])}</span>' if eksik and t['kimlik'] in yerler else ''
            aciklama = E(t['cozum']) if eksik else {'olcumsuz': 'Ölçüm/doğrulama gerekli', 'uygulanamaz': 'Kapsam dışı', 'var': 'Bu ölçümde eksik bulunmadı'}.get(bd, 'Doğrulama gerekli')
            p.append(f'<td class="cozum">{aciklama}{yer}</td></tr>')
        p.append('</tbody></table></div></section>')

    plan = ek.get('plan') or []
    kararlar = ek.get('kararlar') or []
    kisitlar = list(ek.get('kisitlar') or [])
    kisitlar.extend(f'{s["ad"]}: {uyari}' for s in siteler for uyari in s.get('uyarilar', []))
    kisitlar = list(dict.fromkeys(kisitlar))
    p.append('<section class="bolum"><h2>Çözüm sırası</h2>')
    p.append('<ol>' + ''.join(f'<li>{E(x)}</li>' for x in plan) + '</ol>' if plan else '<p class="bos">Plan girilmedi.</p>')
    p.append('</section><div class="ikili"><section class="bolum"><h2>Karar gerekenler</h2>')
    p.append('<ul>' + ''.join(f'<li>{E(x)}</li>' for x in kararlar) + '</ul>' if kararlar else '<p class="bos">Yok.</p>')
    p.append('</section><section class="bolum"><h2>Ölçüm kısıtları</h2>')
    p.append('<ul>' + ''.join(f'<li>{E(x)}</li>' for x in kisitlar) + '</ul>' if kisitlar else '<p class="bos">Yok.</p>')
    p.append('</section></div></div>\n<script nonce="' + nonce + '">')
    p.append('''
(function () {
  var dugmeler = document.querySelectorAll('[data-suzgec]');
  function uygula(tur) {
    document.querySelectorAll('tbody tr').forEach(function (satir) {
      var goster = tur === 'tumu' || (tur === 'eksik' && satir.dataset.eksik === '1') ||
        (tur === 'rakip' && satir.dataset.rakip === '1') || (tur === 'yuksek' && satir.dataset.yuksek === '1') ||
        (tur === 'olcumsuz' && satir.dataset.olcumsuz === '1');
      satir.hidden = !goster;
    });
    document.querySelectorAll('.grup').forEach(function (grup) {
      grup.hidden = grup.querySelectorAll('tbody tr:not([hidden])').length === 0;
    });
    dugmeler.forEach(function (d) { d.setAttribute('aria-pressed', d.dataset.suzgec === tur ? 'true' : 'false'); });
  }
  dugmeler.forEach(function (d) { d.addEventListener('click', function () { uygula(d.dataset.suzgec); }); });
})();
</script></body></html>''')
    sys.stdout.write('\n'.join(p))


if __name__ == '__main__':
    main()
