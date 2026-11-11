#!/usr/bin/env python3
"""Ağ/DB açmadan tarayıcının kararlarını ve raporun kanıt aktarımını sınar."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

KOK = Path(__file__).resolve().parents[1]

def modul(ad, dosya):
    spec = importlib.util.spec_from_file_location(ad, KOK / 'scripts' / dosya)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

T = modul('seo_tarama', 'seo-tara.py')
R = modul('seo_raporu', 'rapor-html.py')
ADRES = 'https://ornek.invalid'
HTML = '<html lang="tr"><head><title>Kısa</title><meta name="description" content="Kısa özet"></head><body><h1>Örnek</h1></body></html>'

def yanit(url, govde='', durum=200, basliklar=None, kesildi=False):
    ham = govde if isinstance(govde, bytes) else govde.encode()
    return {'durum': durum, 'govde': ham.decode('utf-8', 'replace'), 'ham': ham, 'basliklar': basliklar or {}, 'son_url': url, 'kesildi': kesildi}

class Kontroller(unittest.TestCase):
    def setUp(self):
        self.yollar = {'/': yanit(ADRES+'/', HTML)}
        self.site = {'ad': 'Örnek', 'biz': True, 'kok': ADRES, 'sayfalar': {'anasayfa': '/'}}
        T.ISTEK_DURUSU = None

    def getir(self, url, **kwargs):
        return self.yollar.get(url.removeprefix(ADRES), yanit(url, 'Bulunamadı', 404))

    def tara(self):
        with patch.object(T, 'getir', self.getir):
            return T.site_tara(self.site)

    def sayfa(self, tur, yol, ek):
        self.site['sayfalar'][tur] = yol
        self.yollar[yol] = yanit(ADRES+yol, HTML.replace('</head>', ek+'</head>'))

    def test_bozuk_alt_sitemap_basarili_sayilmaz(self):
        self.yollar['/sitemap.xml'] = yanit(ADRES+'/sitemap.xml', '<sitemapindex><sitemap><loc>'+ADRES+'/alt.xml</loc></sitemap></sitemapindex>')
        self.assertEqual(self.tara()['kontroller']['sitemap']['durum'], 'yok')

    def test_dorduncu_alt_sitemap_de_okunur(self):
        self.yollar['/sitemap.xml'] = yanit(ADRES+'/sitemap.xml', '<sitemapindex>'+''.join(f'<sitemap><loc>{ADRES}/{i}.xml</loc></sitemap>' for i in range(4))+'</sitemapindex>')
        for i in range(4):
            self.yollar[f'/{i}.xml'] = yanit(ADRES+f'/{i}.xml', f'<urlset><url><loc>{ADRES}/urun{i}</loc><lastmod>2026-10-28</lastmod></url></urlset>')
        with patch.object(T, 'getir', self.getir):
            s = T.sitemap_incele(ADRES+'/sitemap.xml')
        self.assertEqual(s['url_sayisi'], 4)
        self.assertTrue(s['lastmod'])

    def test_sitemap_siniri_belirsizligi_korur(self):
        self.yollar['/sitemap.xml'] = yanit(ADRES+'/sitemap.xml', f'<sitemapindex><sitemap><loc>{ADRES}/alt.xml</loc></sitemap></sitemapindex>')
        with patch.object(T, 'getir', self.getir):
            self.assertFalse(T.sitemap_incele(ADRES+'/sitemap.xml', 1)['tam'])

    def test_ad_alanli_xml_ve_birden_fazla_kok(self):
        metin = f'<s:urlset xmlns:s="http://www.sitemaps.org/schemas/sitemap/0.9"><s:url><s:loc>{ADRES}/a</s:loc></s:url></s:urlset>'
        self.yollar['/a.xml'] = yanit(ADRES+'/a.xml', metin)
        self.yollar['/b.xml'] = yanit(ADRES+'/b.xml', metin.replace('/a<','/b<'))
        with patch.object(T, 'getir', self.getir):
            self.assertEqual(T.sitemap_incele([ADRES+'/a.xml', ADRES+'/b.xml'])['url_sayisi'], 2)

    def test_tekrarlanan_lastmod_sahte_diye_sunulmaz(self):
        self.yollar['/sitemap.xml'] = yanit(ADRES+'/sitemap.xml', '<urlset>'+''.join(f'<url><loc>{ADRES}/u{i}</loc><lastmod>2026-10-28T11:20:00Z</lastmod></url>' for i in range(12))+'</urlset>')
        c = self.tara()['kontroller']['sitemap_lastmod']
        self.assertEqual(c['durum'], 'kismi')
        self.assertIn('sahte tarih kanıtı değildir', c['kanit'])

    def test_robots_503_izin_sayilmaz(self):
        self.yollar['/robots.txt'] = yanit(ADRES+'/robots.txt', 'Bakım', 503)
        self.assertEqual(self.tara()['kontroller']['ai_arama_botlari']['durum'], 'olcumsuz')

    def test_robots_urun_yolu_engeli(self):
        self.sayfa('urun','/urun/a','')
        self.yollar['/robots.txt'] = yanit(ADRES+'/robots.txt','User-agent: *\nDisallow: /urun/\n')
        self.assertEqual(self.tara()['kontroller']['ai_arama_botlari']['durum'], 'yok')

    def test_robots_ozgulluk_joker_bitis_ve_izin_esitligi(self):
        g=T.robots_ayristir('User-agent: *\nDisallow: /\nUser-agent: OAI-SearchBot\nDisallow: /urun/*$\nAllow: /urun/acik$\n')
        self.assertTrue(T.bot_engelli_mi(g,'OAI-SearchBot','/urun/a'))
        self.assertFalse(T.bot_engelli_mi(g,'OAI-SearchBot','/urun/acik'))
        self.assertFalse(T.bot_engelli_mi(g,'OAI-SearchBot','/blog'))
        g=T.robots_ayristir('User-agent: *\nDisallow: /\nAllow: /\n')
        self.assertFalse(T.bot_engelli_mi(g,'OAI-SearchBot'))

    def test_robots_ayni_ajan_gruplari_birlesir(self):
        g=T.robots_ayristir('User-agent: OAI-SearchBot\nDisallow: /urun/\nUser-agent: OAI-SearchBot\nAllow: /urun/acik\n')
        self.assertFalse(T.bot_engelli_mi(g,'OAI-SearchBot','/urun/acik'))

    def test_html_favicon_sayilmaz(self):
        self.yollar['/favicon.ico']=yanit(ADRES+'/favicon.ico', HTML)
        self.assertEqual(self.tara()['kontroller']['favicon_ico']['durum'],'yok')

    def test_64_piksel_favicon_reddedilmez(self):
        png=b'\x89PNG\r\n\x1a\n'+b'\x00'*8+struct.pack('>II',64,64)
        self.yollar['/']=yanit(ADRES+'/',HTML.replace('</head>','<link rel="icon" href="/ikon.png"></head>'))
        self.yollar['/ikon.png']=yanit(ADRES+'/ikon.png',png)
        self.assertEqual(self.tara()['kontroller']['favicon_48']['durum'],'var')

    def test_html_manifest_sayilmaz(self):
        self.yollar['/']=yanit(ADRES+'/',HTML.replace('</head>','<link rel="manifest" href="/site.webmanifest"></head>'))
        self.yollar['/site.webmanifest']=yanit(ADRES+'/site.webmanifest',HTML)
        self.assertEqual(self.tara()['kontroller']['manifest']['durum'],'yok')

    def test_ic_ice_product_bulunur(self):
        p=T.ayristir(yanit(ADRES, '<script type="application/ld+json">{"@type":"WebPage","mainEntity":{"@type":"Product","name":"Örnek"}}</script>'))
        self.assertEqual(len(T.dugum_bul(p,'Product')),1)

    def test_sifir_fiyat_bos_sayilmaz(self):
        self.sayfa('urun','/urun/a','<script type="application/ld+json">'+json.dumps({'@type':'Product','name':'Örnek','offers':{'@type':'Offer','price':0,'priceCurrency':'TRY','availability':'https://schema.org/InStock'}})+'</script>')
        self.assertEqual(self.tara()['kontroller']['urun_offer']['durum'],'var')

    def test_web_site_search_action_istemez(self):
        self.yollar['/']=yanit(ADRES+'/',HTML+'<script type="application/ld+json">{"@type":"WebSite","name":"Örnek","url":"https://ornek.invalid"}</script>')
        self.assertEqual(self.tara()['kontroller']['website_sema']['durum'],'var')

    def test_analitik_kelimesi_calismayi_kanitlamaz(self):
        self.sayfa('urun','/urun/a','<script>const olay = "view_item"; gtag("consent", "default", {});</script>')
        c=self.tara()['kontroller']
        self.assertEqual(c['olcum_eticaret_olay']['durum'],'kismi')
        self.assertEqual(c['olcum_consent']['durum'],'kismi')

    def test_dogrulama_metasinin_yoklugu_hesap_yoklugu_degildir(self):
        self.assertEqual(self.tara()['kontroller']['dogrulama_google']['durum'],'olcumsuz')

    def test_kurumsal_urun_kapsami_ve_gerekceli_uygulanamaz(self):
        self.site.update(profil='kurumsal',uygulanamaz={'yerel_isletme':'Fiziksel mağaza yok'})
        c=self.tara()['kontroller']
        self.assertEqual(c['urun_offer']['durum'],'uygulanamaz')
        self.assertEqual(c['yerel_isletme']['durum'],'uygulanamaz')
        self.assertEqual(c['merchant_feed']['durum'],'uygulanamaz')

    def test_uzunluk_ve_h1_sayisi_siralama_esigi_degildir(self):
        self.yollar['/']=yanit(ADRES+'/',HTML.replace('</body>','<h1>İkinci başlık</h1></body>'))
        c=self.tara()['kontroller']
        self.assertEqual(c['title']['durum'],'var')
        self.assertEqual(c['description']['durum'],'var')
        self.assertEqual(c['tek_h1']['durum'],'var')
        self.assertIn('İkinci başlık',c['tek_h1']['kanit'])

    def test_bos_h1_baslik_sayilmaz(self):
        self.yollar['/']=yanit(ADRES+'/',HTML.replace('<h1>Örnek</h1>','<h1> </h1>'))
        self.assertEqual(self.tara()['kontroller']['tek_h1']['durum'],'kismi')

    def test_hizmet_ve_adres_alanlari_raporlanir(self):
        sema={'@type':'LocalBusiness','name':'Örnek','@id':'#firma','url':ADRES,'logo':'/a.png','sameAs':['https://example.org'],'telephone':'Örnek', 'openingHours':'Mo-Fr 09:00-18:00','geo':{'latitude':1},'priceRange':'Bilgi alınız'}
        self.yollar['/']=yanit(ADRES+'/',HTML+'<script type="application/ld+json">'+json.dumps(sema)+'</script>')
        self.sayfa('hizmet','/hizmet/a','<script type="application/ld+json">{"@type":"Service","name":"Tamir","areaServed":"Ankara"}</script>')
        c=self.tara()['kontroller']
        self.assertEqual(c['hizmet_sema']['durum'],'kismi')
        self.assertIn('address.addressLocality',c['yerel_isletme']['kanit'])

    def test_cift_kacis_adayi_raporlanir(self):
        self.yollar['/']=yanit(ADRES+'/',HTML.replace('Kısa</title>','A &amp;amp; B</title>'))
        self.assertEqual(self.tara()['kontroller']['cift_kacis']['durum'],'kismi')
        self.yollar['/']=yanit(ADRES+'/',HTML.replace('<h1>Örnek</h1>','<h1>A &amp;quot; B</h1>'))
        self.assertEqual(self.tara()['kontroller']['cift_kacis']['durum'],'kismi')

    def test_hizmet_sayfasinda_breadcrumb_algilanir(self):
        self.site['profil']='kurumsal'
        self.sayfa('hizmet','/hizmet/a','<script type="application/ld+json">{"@type":"BreadcrumbList"}</script>')
        self.assertEqual(self.tara()['kontroller']['breadcrumb']['durum'],'var')

    def test_www_yonlendirmesi_dogru_hedef_ister(self):
        self.site['alternatif_kok']='https://www.ornek.invalid'
        asil=self.getir
        def getir(url,**kw):
            if 'www.' in url: return yanit(url,'',301,{'location':ADRES+'/'})
            return asil(url,**kw)
        with patch.object(T,'getir',getir): self.assertEqual(T.site_tara(self.site)['kontroller']['www_yonlendirme']['durum'],'var')

    def test_yan_istek_engeli_ana_taramayi_durdurmaz(self):
        self.site.update(alternatif_kok='https://www.ornek.invalid',bot_kontrol=True)
        self.yollar['/llms.txt']=yanit(ADRES+'/llms.txt','# Başlık\n'+'a'*320)
        asil=self.getir
        def getir(url,ua=T.TARAYICI_UA,**kw):
            if 'www.' in url or ua!=T.TARAYICI_UA:
                return yanit(url,'Just a moment...',403)
            return asil(url,ua=ua,**kw)
        with patch.object(T,'getir',getir):
            c=T.site_tara(self.site)['kontroller']
            self.assertEqual(c['llms_txt']['durum'],'kismi')
            self.assertEqual(c['ai_bot_erisim']['durum'],'olcumsuz')

    def test_yol_sonu_500_basarili_degildir(self):
        self.sayfa('urun','/urun/a','')
        self.yollar['/urun/a/']=yanit(ADRES+'/urun/a/','Hata',500)
        self.assertEqual(self.tara()['kontroller']['sonda_egik_cizgi']['durum'],'olcumsuz')

    def test_bozuk_feed_basarili_degildir(self):
        self.yollar['/merchant-feed.xml']=yanit(ADRES+'/merchant-feed.xml','<rss><item>')
        self.assertEqual(self.tara()['kontroller']['merchant_feed']['durum'],'olcumsuz')

    def test_xml_entity_ve_kesilme_reddedilir(self):
        for y in [yanit(ADRES,'<!DOCTYPE x [<!ENTITY a "a">]><urlset/>'),yanit(ADRES,'<urlset/>',kesildi=True)]:
            with self.assertRaises(ValueError): T.xml_oku(y)

    def test_config_bozuk_kapsam_agdan_once_reddedilir(self):
        for site in [dict(self.site,biz=False),dict(self.site,kok='file:///etc/hosts'),dict(self.site,alternatif_kok='https://baskasi.invalid'),dict(self.site,sitemap_siniri=0),dict(self.site,uygulanamaz={'title':''})]:
            with self.assertRaises(ValueError): T.yapilandirma_dogrula({'siteler':[site]})

    def test_429_sonrasi_yeni_istek_atilmaz(self):
        hata=urllib.error.HTTPError(ADRES,429,'Sınır',{},io.BytesIO(b'limit'))
        with patch.object(T.time,'sleep'), patch.object(T.urllib.request,'build_opener') as acici:
            acici.return_value.open.side_effect=hata
            self.assertEqual(T.getir(ADRES)['durum'],429)
            self.assertIsNone(T.getir(ADRES+'/sonraki')['durum'])
            self.assertEqual(acici.return_value.open.call_count,1)

    def test_rapor_uyari_kaynak_ve_belirsizlik_korur(self):
        sonuc=self.tara()
        sonuc['uyarilar'].append('Ölçüm sınırı <örnek>')
        sonuc['kontroller']['title']={'durum':'olcumsuz','kanit':'Başlık doğrulanamadı'}
        with tempfile.TemporaryDirectory() as dizin:
            dosya=Path(dizin)/'sonuc.json'; dosya.write_text(json.dumps({'siteler':[sonuc]}))
            cikti=io.StringIO()
            with patch.object(sys,'argv',['rapor',str(dosya)]),contextlib.redirect_stdout(cikti): R.main()
            html=cikti.getvalue()
            self.assertTrue(html.startswith('<!doctype html>'))
            self.assertIn('Ölçüm sınırı &lt;örnek&gt;',html)
            self.assertIn('Ölçüm/doğrulama gerekli',html)
            self.assertNotIn('Gerekmiyor',html)
            self.assertIn('Resmî öneri',html)
            self.assertIn('Sayfa bazında özet',html)
            nonce=re.search(r'<script nonce="([^"]+)"',html).group(1)
            self.assertIn("script-src 'nonce-"+nonce+"'",html)
            (Path(dizin)/'seo-kontrol-ornek-rapor.html').write_text(html)

    def test_json_ld_id_referanslari_ve_kopuk_id_cozulur(self):
        graf = {
            '@context': 'https://schema.org',
            '@graph': [
                {'@type': 'Organization', '@id': ADRES + '/#org', 'name': 'Örnek Firma'},
                {'@type': 'Offer', '@id': '#teklif', 'price': '250', 'priceCurrency': 'TRY',
                 'availability': 'https://schema.org/InStock', 'itemCondition': 'https://schema.org/NewCondition',
                 'priceValidUntil': '2027-01-01', 'seller': {'@id': ADRES + '/#org'}},
                {'@type': 'Product', '@id': '#urun', 'name': 'Test Ürün', 'offers': {'@id': '#teklif'}},
            ]
        }
        self.sayfa('urun', '/urun/a', '<script type="application/ld+json">' + json.dumps(graf) + '</script>')
        c = self.tara()['kontroller']
        self.assertEqual(c['urun_offer']['durum'], 'var')
        self.assertEqual(c['urun_offer_ayrinti']['durum'], 'var')
        self.assertEqual(c['ld_gecerli']['durum'], 'var')
        kopuk = {'@type': 'Product', 'name': 'Kopuk', 'offers': {'@id': '#tanimsiz'}}
        self.sayfa('urun', '/urun/a', '<script type="application/ld+json">' + json.dumps(kopuk) + '</script>')
        c2 = self.tara()['kontroller']
        self.assertEqual(c2['ld_gecerli']['durum'], 'kismi')
        self.assertIn('kopuk @id', c2['ld_gecerli']['kanit'])

    def test_robots_celiskili_direktif_ve_alt_sayfa_noindex(self):
        self.yollar['/'] = yanit(ADRES + '/', HTML.replace('</head>', '<meta name="robots" content="index, nofollow"><meta name="googlebot" content="follow"></head>'))
        self.assertEqual(self.tara()['kontroller']['robots_meta']['durum'], 'kismi')
        self.yollar['/'] = yanit(ADRES + '/', HTML)
        self.sayfa('urun', '/urun/a', '<meta name="robots" content="noindex">')
        self.assertEqual(self.tara()['kontroller']['robots_meta']['durum'], 'yok')

    def test_sitemap_ornek_sayfa_tutarliligi(self):
        self.sayfa('urun', '/urun/a', '<link rel="canonical" href="' + ADRES + '/urun/a">')
        self.yollar['/sitemap.xml'] = yanit(ADRES + '/sitemap.xml', f'<urlset><url><loc>{ADRES}/</loc></url><url><loc>{ADRES}/urun/a</loc></url></urlset>')
        self.assertEqual(self.tara()['kontroller']['sitemap_tutarlilik']['durum'], 'var')
        self.yollar['/sitemap.xml'] = yanit(ADRES + '/sitemap.xml', f'<urlset><url><loc>{ADRES}/</loc></url></urlset>')
        self.assertEqual(self.tara()['kontroller']['sitemap_tutarlilik']['durum'], 'kismi')
        self.sayfa('urun', '/urun/a', '<meta name="robots" content="noindex">')
        self.yollar['/sitemap.xml'] = yanit(ADRES + '/sitemap.xml', f'<urlset><url><loc>{ADRES}/</loc></url><url><loc>{ADRES}/urun/a</loc></url></urlset>')
        self.assertEqual(self.tara()['kontroller']['sitemap_tutarlilik']['durum'], 'yok')

    def test_ic_baglanti_ve_capa_metni(self):
        self.yollar['/'] = yanit(ADRES + '/', HTML.replace('</body>', '<a href="/iletisim">İletişim sayfamız</a><a href="/katalog"><img src="/k.png" alt="Ürün kataloğu"></a></body>'))
        self.assertEqual(self.tara()['kontroller']['ic_baglanti']['durum'], 'var')
        self.yollar['/'] = yanit(ADRES + '/', HTML.replace('</body>', '<a href="/iletisim">tıklayın</a></body>'))
        c = self.tara()['kontroller']['ic_baglanti']
        self.assertEqual(c['durum'], 'kismi')
        self.assertIn('belirsiz çapa metni', c['kanit'])
        self.yollar['/'] = yanit(ADRES + '/', HTML.replace('</body>', '<a href="javascript:void(0)">Aç</a><a href="/a">Detaylı bilgi</a></body>'))
        self.assertEqual(self.tara()['kontroller']['ic_baglanti']['durum'], 'kismi')

    def test_breadcrumb_adim_ve_isim_dogrulamasi(self):
        tek = {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Ana Sayfa'}]}
        self.sayfa('urun', '/urun/a', '<script type="application/ld+json">' + json.dumps(tek) + '</script>')
        self.assertEqual(self.tara()['kontroller']['breadcrumb']['durum'], 'kismi')
        tam = {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Ana Sayfa', 'item': ADRES + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Ürün', 'item': ADRES + '/urun/a'},
        ]}
        self.sayfa('urun', '/urun/a', '<script type="application/ld+json">' + json.dumps(tam) + '</script>')
        self.assertEqual(self.tara()['kontroller']['breadcrumb']['durum'], 'var')

    def test_coklu_canonical_ve_izleme_parametresi(self):
        self.sayfa('urun', '/urun/a', f'<link rel="canonical" href="{ADRES}/urun/a?utm_source=google">')
        c = self.tara()['kontroller']
        self.assertEqual(c['canonical']['durum'], 'kismi')
        self.assertEqual(c['urun_canonical']['durum'], 'kismi')
        self.sayfa('urun', '/urun/a', f'<link rel="canonical" href="{ADRES}/urun/a"><link rel="canonical" href="{ADRES}/urun/b">')
        self.assertEqual(self.tara()['kontroller']['canonical']['durum'], 'kismi')

    def test_tanim_ve_otomatik_kontrol_kapsami(self):
        tanim=json.loads((KOK/'references/kontroller.json').read_text())['kontroller']
        ids=[t['kimlik'] for t in tanim]
        self.assertEqual(len(ids),len(set(ids)))
        otomatik={t['kimlik'] for t in tanim if t['grup']!='kod'}
        self.assertEqual(otomatik,set(self.tara()['kontroller']))
        T.yapilandirma_dogrula(json.loads((KOK/'references/ornek-yapilandirma.json').read_text()))

if __name__ == '__main__':
    unittest.main(verbosity=2)
