#!/usr/bin/env python3
"""
SEO kontrol tarayıcısı (salt-okunur, yalnızca GET).

Kullanım:
    python3 -I seo-tara.py yapilandirma.json > sonuc.json

Yapılandırma örneği: ../references/ornek-yapilandirma.json
Her site için ana sayfa, ürün, kategori, kategori 2. sayfa ve blog adresleri verilir; verilmeyen
sayfanın kontrolleri "ölçülmedi" olur. Sonuç JSON'u rapor-html.py ile HTML kontrol listesine çevrilir.

Durumlar: var | kismi | yok | olcumsuz | uygulanamaz
"""
import html as htmlmod
import json
import re
import ssl
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import gzip
import io
from collections import Counter
from pathlib import Path
from html.parser import HTMLParser

TARAYICI_UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
               '(KHTML, like Gecko) Chrome/140.0 Safari/537.36')
BEKLEME = 0.35
ISTEK_DURUSU = None
CTX = ssl.create_default_context()
ENGEL_ISARETLERI = ['one moment, please', 'just a moment', 'checking your browser',
                    'cf-browser-verification', 'challenge-platform', 'attention required']

AI_ARAMA_BOTLARI = ['OAI-SearchBot', 'ChatGPT-User', 'Claude-SearchBot', 'Claude-User',
                    'PerplexityBot', 'Perplexity-User', 'DuckAssistBot', 'MistralAI-User', 'bingbot']
AI_EGITIM_BOTLARI = ['GPTBot', 'ClaudeBot', 'Google-Extended', 'Applebot-Extended', 'CCBot',
                     'Amazonbot', 'meta-externalagent', 'Bytespider']
CANLI_BOT_UA = {
    'Googlebot': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'bingbot': 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
    'GPTBot': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.1; +https://openai.com/gptbot)',
    'OAI-SearchBot': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; OAI-SearchBot/1.0; +https://openai.com/searchbot)',
    'ClaudeBot': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)',
    'Claude-SearchBot': 'Mozilla/5.0 (compatible; Claude-SearchBot/1.0; +https://www.anthropic.com)',
    'PerplexityBot': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)',
}
FEED_YOLLARI = ['/merchant-feed.xml', '/google-merchant.xml', '/feed/google.xml', '/xml/google.xml',
                '/feed.xml', '/urunler.xml', '/product-feed.xml']


class YonlendirmeYok(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def getir(url, ua=TARAYICI_UA, azami=40 * 1024 * 1024, yonlendir=True, zaman=30, durdur=True):
    global ISTEK_DURUSU
    if ISTEK_DURUSU:
        return {'durum': None, 'basliklar': {}, 'ham': b'', 'govde': ISTEK_DURUSU, 'son_url': url}
    time.sleep(BEKLEME)
    istek = urllib.request.Request(url, headers={'User-Agent': ua, 'Accept': '*/*',
                                                 'Accept-Language': 'tr-TR,tr;q=0.9'})
    acici = (urllib.request.build_opener(urllib.request.HTTPSHandler(context=CTX)) if yonlendir
             else urllib.request.build_opener(YonlendirmeYok, urllib.request.HTTPSHandler(context=CTX)))
    try:
        with acici.open(istek, timeout=zaman) as y:
            ham = y.read(azami + 1)
            kesildi = len(ham) > azami
            ham = ham[:azami]
            if durdur and engel_mi(ham.decode('utf-8', 'replace')):
                ISTEK_DURUSU = 'WAF doğrulaması nedeniyle bu sitede ek istekler durduruldu'
            return {'durum': y.status, 'basliklar': {k.lower(): v for k, v in y.headers.items()},
                    'ham': ham, 'govde': ham.decode('utf-8', 'replace'), 'son_url': y.geturl(), 'kesildi': kesildi}
    except urllib.error.HTTPError as e:
        try:
            ham = e.read(200000)
        except Exception:
            ham = b''
        if e.code == 429 or (durdur and (e.code == 503 or engel_mi(ham.decode('utf-8', 'replace')))):
            ISTEK_DURUSU = f'HTTP {e.code}/WAF nedeniyle bu sitede ek istekler durduruldu'
        return {'durum': e.code, 'basliklar': {k.lower(): v for k, v in (e.headers or {}).items()},
                'ham': ham, 'govde': ham.decode('utf-8', 'replace'), 'son_url': url}
    except Exception as e:
        if durdur:
            ISTEK_DURUSU = 'Ağ hatası/zaman aşımı nedeniyle bu sitede ek istekler durduruldu'
        return {'durum': None, 'basliklar': {}, 'ham': b'', 'govde': f'HATA {type(e).__name__}: {e}', 'son_url': url}


def engel_mi(govde):
    bas = (govde or '')[:6000].lower()
    return any(i in bas for i in ENGEL_ISARETLERI)


class Ayristirici(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.title = ''
        self._title_ic = False
        self.metalar = []
        self.linkler = []
        self.h1ler = []
        self._h1_derinlik = 0
        self._h1_metin = ''
        self.alt_basliklar = []
        self._alt_baslik_etiket = None
        self._alt_baslik_metin = ''
        self.baglantilar = []
        self._a_ic = None
        self.gorseller = []
        self.betik_srcler = []
        self.ld = []
        self._ld_ic = False
        self._ld_metin = ''
        self.head_bitti = False

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or '') for k, v in attrs}
        if tag == 'html':
            self.lang = a.get('lang')
        elif tag == 'title' and not self.head_bitti:
            self._title_ic = True
        elif tag == 'meta':
            self.metalar.append(a)
        elif tag == 'link':
            self.linkler.append(a)
        elif tag == 'h1':
            self._h1_derinlik += 1
            self._h1_metin = ''
        elif tag in ('h2', 'h3'):
            self._alt_baslik_etiket = tag
            self._alt_baslik_metin = ''
        elif tag == 'a':
            self._a_ic = {
                'href': a.get('href', '').strip(),
                'rel': a.get('rel', '').lower(),
                'metin': '',
                'alt': [],
                'aria': (a.get('aria-label') or a.get('title') or '').strip(),
            }
        elif tag == 'img':
            self.gorseller.append(a)
            if self._a_ic is not None and a.get('alt', '').strip():
                self._a_ic['alt'].append(a.get('alt', '').strip())
        elif tag == 'script':
            if a.get('src'):
                self.betik_srcler.append(a['src'])
            if 'ld+json' in a.get('type', '').lower():
                self._ld_ic = True
                self._ld_metin = ''
        elif tag == 'body':
            self.head_bitti = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self._title_ic = False
        elif tag == 'h1' and self._h1_derinlik:
            self._h1_derinlik -= 1
            self.h1ler.append(re.sub(r'\s+', ' ', self._h1_metin).strip())
        elif tag in ('h2', 'h3') and self._alt_baslik_etiket == tag:
            m = re.sub(r'\s+', ' ', self._alt_baslik_metin).strip()
            if m:
                self.alt_basliklar.append((tag, m))
            self._alt_baslik_etiket = None
        elif tag == 'a' and self._a_ic is not None:
            metin = (re.sub(r'\s+', ' ', self._a_ic['metin']).strip()
                     or ' '.join(self._a_ic['alt']).strip()
                     or self._a_ic['aria'])
            self.baglantilar.append({
                'href': self._a_ic['href'],
                'rel': self._a_ic['rel'],
                'metin': metin,
            })
            self._a_ic = None
        elif tag == 'script' and self._ld_ic:
            self._ld_ic = False
            self.ld.append(self._ld_metin)
        elif tag == 'head':
            self.head_bitti = True

    def handle_data(self, data):
        if self._title_ic:
            self.title += data
        if self._h1_derinlik:
            self._h1_metin += data
        if self._alt_baslik_etiket:
            self._alt_baslik_metin += data
        if self._a_ic is not None:
            self._a_ic['metin'] += data
        if self._ld_ic:
            self._ld_metin += data


def id_anahtarlari(deger, sayfa_url=''):
    if not isinstance(deger, str) or not deger.strip():
        return []
    d = deger.strip()
    anahtarlar = [d]
    if '#' in d:
        anahtarlar.append('#' + d.split('#', 1)[1])
    elif sayfa_url and d.startswith('/'):
        anahtarlar.append(urllib.parse.urljoin(sayfa_url, d))
    return list(dict.fromkeys(anahtarlar))


def id_tablosu_topla(veri, tablo, sayfa_url=''):
    if isinstance(veri, list):
        for v in veri:
            id_tablosu_topla(v, tablo, sayfa_url)
    elif isinstance(veri, dict):
        dugum_id = veri.get('@id')
        anlamli = set(veri.keys()) - {'@id', '@context'}
        if isinstance(dugum_id, str) and dugum_id.strip() and anlamli:
            for anahtar in id_anahtarlari(dugum_id, sayfa_url):
                mevcut = tablo.setdefault(anahtar, {})
                for k_ad, k_deg in veri.items():
                    if k_ad not in mevcut or not mevcut[k_ad]:
                        mevcut[k_ad] = k_deg
        for deger in veri.values():
            if isinstance(deger, (dict, list)):
                id_tablosu_topla(deger, tablo, sayfa_url)


def id_referanslarini_coz(veri, tablo, sayfa_url='', kopuk=None, derinlik=0, ust_anahtar=''):
    if derinlik > 4:
        return veri
    if isinstance(veri, list):
        return [id_referanslarini_coz(v, tablo, sayfa_url, kopuk, derinlik + 1, ust_anahtar) for v in veri]
    if isinstance(veri, dict):
        ref = veri.get('@id')
        sadece_ref = isinstance(ref, str) and ref.strip() and not (set(veri.keys()) - {'@id'})
        if isinstance(ref, str) and ref.strip():
            hedef = next((tablo[a] for a in id_anahtarlari(ref, sayfa_url) if a in tablo), None)
            if hedef and (sadece_ref or derinlik > 0):
                birlesik = dict(hedef)
                birlesik.update({k: v for k, v in veri.items() if v not in (None, '', [], {})})
                veri = birlesik
            elif sadece_ref and ust_anahtar and ust_anahtar != '@graph' and kopuk is not None:
                sayfa_koku = (sayfa_url or '').split('#', 1)[0].rstrip('/')
                ref_koku = ref.split('#', 1)[0].rstrip('/')
                if ref.startswith('#') or (sayfa_koku and '#' in ref and ref_koku == sayfa_koku):
                    kopuk.add(ref.strip())
        cozulmus = {}
        for k_ad, k_deg in veri.items():
            if k_ad == '@id' or not isinstance(k_deg, (dict, list)):
                cozulmus[k_ad] = k_deg
            else:
                cozulmus[k_ad] = id_referanslarini_coz(k_deg, tablo, sayfa_url, kopuk, derinlik + 1, k_ad)
        return cozulmus
    return veri


def ayristir(yanit):
    p = Ayristirici()
    try:
        p.feed(yanit['govde'])
    except Exception:
        pass
    meta = {}
    for m in p.metalar:
        anahtar = (m.get('property') or m.get('name') or m.get('itemprop') or '').strip().lower()
        if anahtar:
            meta.setdefault(anahtar, []).append(m.get('content', ''))
    linkler = {}
    for l in p.linkler:
        for rel in (l.get('rel') or '').lower().split():
            linkler.setdefault(rel, []).append(l)
    ham_ld, dugumler, ld_hatalari = [], [], 0
    id_tablosu, kopuk_idler = {}, set()
    for blok in p.ld:
        try:
            veri = json.loads(blok.strip())
        except Exception:
            ld_hatalari += 1
            continue
        ham_ld.append(veri)
        id_tablosu_topla(veri, id_tablosu, yanit['son_url'])
    for veri in ham_ld:
        cozulmus = id_referanslarini_coz(veri, id_tablosu, yanit['son_url'], kopuk_idler)
        dugumler.extend(duzlestir(cozulmus))
    return {'durum': yanit['durum'], 'url': yanit['son_url'], 'govde': yanit['govde'], 'lang': p.lang,
            'title': re.sub(r'\s+', ' ', p.title).strip(), 'meta': meta, 'link': linkler, 'h1': p.h1ler,
            'alt_basliklar': p.alt_basliklar, 'a': p.baglantilar,
            'img': p.gorseller, 'betikler': p.betik_srcler, 'ld': dugumler, 'ld_blok': len(p.ld),
            'ld_hata': ld_hatalari, 'ld_kopuk_id': sorted(kopuk_idler), 'engel': engel_mi(yanit['govde']),
            'basliklar': yanit['basliklar'], 'kesildi': yanit.get('kesildi', False)}


def duzlestir(veri):
    cikti = []
    if isinstance(veri, list):
        for v in veri:
            cikti.extend(duzlestir(v))
    elif isinstance(veri, dict):
        if '@type' in veri:
            cikti.append(veri)
        for deger in veri.values():
            if isinstance(deger, (dict, list)):
                cikti.extend(duzlestir(deger))
    return cikti


def turler(dugum):
    t = dugum.get('@type')
    return [x.lower() for x in (t if isinstance(t, list) else [t]) if isinstance(x, str)]


def dugum_bul(sayfa, *aranan):
    if not sayfa:
        return []
    aranan = [a.lower() for a in aranan]
    return [d for d in sayfa['ld'] if any(t in aranan for t in turler(d))]


def m1(sayfa, anahtar):
    if not sayfa:
        return ''
    degerler = sayfa['meta'].get(anahtar.lower()) or []
    return (degerler[0] or '').strip() if degerler else ''


def gorsel_olcu(ham):
    """(genişlik, yükseklik, biçim) ya da None."""
    try:
        if ham[:8] == b'\x89PNG\r\n\x1a\n':
            g, y = struct.unpack('>II', ham[16:24])
            return g, y, 'png'
        if ham[:3] == b'GIF':
            g, y = struct.unpack('<HH', ham[6:10])
            return g, y, 'gif'
        if ham[:4] == b'RIFF' and ham[8:12] == b'WEBP':
            parca = ham[12:16]
            if parca == b'VP8 ':
                g, y = struct.unpack('<HH', ham[26:30])
                return g & 0x3fff, y & 0x3fff, 'webp'
            if parca == b'VP8L':
                b = ham[21:25]
                g = 1 + (((b[1] & 0x3F) << 8) | b[0])
                y = 1 + (((b[3] & 0xF) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6))
                return g, y, 'webp'
            if parca == b'VP8X':
                g = 1 + int.from_bytes(ham[24:27], 'little')
                y = 1 + int.from_bytes(ham[27:30], 'little')
                return g, y, 'webp'
        if ham[:4] == b'\x00\x00\x01\x00':
            g, y = ham[6] or 256, ham[7] or 256
            return g, y, 'ico'
        if ham[:2] == b'\xff\xd8':
            i = 2
            while i < len(ham) - 9:
                if ham[i] != 0xFF:
                    i += 1
                    continue
                isaret = ham[i + 1]
                if isaret in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    y, g = struct.unpack('>HH', ham[i + 5:i + 9])
                    return g, y, 'jpeg'
                uzunluk = struct.unpack('>H', ham[i + 2:i + 4])[0]
                i += 2 + uzunluk
        if b'<svg' in ham[:500].lower():
            return 0, 0, 'svg'
    except Exception:
        return None
    return None


def gorsel_getir(url):
    if not url or url.startswith('data:'):
        return None
    y = getir(url, azami=2 * 1024 * 1024, durdur=False)
    if y['durum'] != 200:
        return {'durum': y['durum']}
    if engel_mi(y['govde']):
        return {'durum': 'engel'}
    olcu = gorsel_olcu(y['ham'])
    bayt = int(y['basliklar'].get('content-length') or len(y['ham']))
    return {'durum': 200, 'olcu': olcu, 'bayt': bayt, 'kesildi': y.get('kesildi', False)}


def robots_ayristir(metin):
    gruplar, ajanlar, kurallar, onceki_kural = [], [], [], False
    for satir in metin.splitlines():
        satir = satir.split('#', 1)[0].strip()
        if ':' not in satir:
            continue
        alan, deger = [x.strip() for x in satir.split(':', 1)]
        alan = alan.lower()
        if alan == 'user-agent':
            if onceki_kural:
                gruplar.append((ajanlar, kurallar))
                ajanlar, kurallar = [], []
                onceki_kural = False
            ajanlar.append(deger.lower())
        elif alan in ('allow', 'disallow'):
            kurallar.append((alan, deger))
            onceki_kural = True
    if ajanlar:
        gruplar.append((ajanlar, kurallar))
    return gruplar


def bot_engelli_mi(gruplar, bot, yol='/'):
    bot = bot.lower()
    adaylar = [(len(ajan), kurallar) for ajanlar, kurallar in gruplar
               for ajan in ajanlar if ajan != '*' and ajan in bot]
    if adaylar:
        uzunluk = max(u for u, _ in adaylar)
        eslesen = [k for u, k in adaylar if u == uzunluk]
    else:
        eslesen = [k for a, k in gruplar if '*' in a]
    kurallar = []
    for grup in eslesen:
        for tur, desen in grup:
            if not desen:
                continue
            bitis = desen.endswith('$')
            temel = desen[:-1] if bitis else desen
            kalip = '^' + re.escape(temel).replace(r'\*', '.*') + ('$' if bitis else '')
            if re.search(kalip, yol):
                kurallar.append((len(temel.replace('*', '')), tur == 'allow'))
    return bool(kurallar) and not max(kurallar)[1]


def xml_oku(yanit):
    if yanit['durum'] != 200 or yanit.get('kesildi') or engel_mi(yanit['govde']):
        raise ValueError('Yanıt alınamadı, engellendi ya da boyut sınırında kesildi')
    ham = yanit['ham']
    if ham.startswith(b'\x1f\x8b'):
        with gzip.GzipFile(fileobj=io.BytesIO(ham)) as akis:
            ham = akis.read(50 * 1024 * 1024 + 1)
        if len(ham) > 50 * 1024 * 1024:
            raise ValueError('Açılmış XML boyut sınırını aşıyor')
    if b'<!DOCTYPE' in ham.upper() or b'<!ENTITY' in ham.upper():
        raise ValueError('DTD/ENTITY içeren XML işlenmez')
    return ET.fromstring(ham)


BELIRSIZ_CAPALAR = {'tıklayın', 'tıkla', 'buraya tıklayın', 'buradan', 'devamı', 'devamını oku',
                    'link', 'bağlantı', 'click here', 'read more', 'more', 'here'}
IZLEME_PARAMETRELERI = ('utm_', 'fbclid', 'gclid', 'msclkid', 'yclid', '_ga', 'mc_cid', 'mc_eid')


def url_norm(u):
    if not isinstance(u, str) or not u.strip():
        return ''
    temiz = u.strip().split('#', 1)[0]
    p = urllib.parse.urlparse(temiz)
    yol = p.path.rstrip('/')
    return urllib.parse.urlunparse((p.scheme.lower(), p.netloc.lower(), yol, '', p.query, ''))


def izleme_parametresi_var_mi(u):
    if not isinstance(u, str) or '?' not in u:
        return False
    sorgu = urllib.parse.urlparse(u).query
    for anahtar, _ in urllib.parse.parse_qsl(sorgu, keep_blank_values=True):
        k = anahtar.lower()
        if any(k == p or k.startswith(p) for p in IZLEME_PARAMETRELERI):
            return True
    return False


def robots_direktif_incele(sayfa):
    ham_liste = list(sayfa['meta'].get('robots', [])) + list(sayfa['meta'].get('googlebot', []))
    if sayfa['basliklar'].get('x-robots-tag'):
        ham_liste.append(sayfa['basliklar']['x-robots-tag'])
    birlesik = ', '.join(x for x in ham_liste if x and x.strip())
    parcalar = [p.strip().lower() for p in re.split(r'[,;]', birlesik) if p.strip()]
    kelimeler = {p.split(':', 1)[0].strip() for p in parcalar}
    noindex = 'noindex' in kelimeler or 'none' in kelimeler
    nofollow = 'nofollow' in kelimeler or 'none' in kelimeler
    celiskiler = []
    if noindex and 'index' in kelimeler:
        celiskiler.append('noindex+index')
    if nofollow and 'follow' in kelimeler:
        celiskiler.append('nofollow+follow')
    if noindex and any(k in kelimeler for k in ('max-snippet', 'max-image-preview', 'max-video-preview', 'imageindex', 'archive', 'snippet')):
        celiskiler.append('noindex ile önizleme direktifi birlikte')
    return {'metin': birlesik, 'noindex': noindex, 'celiskiler': celiskiler}


def breadcrumb_incele(sayfa):
    dugumler = dugum_bul(sayfa, 'BreadcrumbList')
    if not dugumler:
        return 'yok', 'yok'
    d = dugumler[0]
    if 'itemListElement' not in d:
        return 'var', 'var'
    ogeler = d.get('itemListElement')
    ogeler = ogeler if isinstance(ogeler, list) else ([ogeler] if isinstance(ogeler, dict) else [])
    if len(ogeler) < 2:
        return 'kismi', f'{len(ogeler)} adım (en az 2 adım olmalı)'
    adsiz = 0
    for oge in ogeler:
        if not isinstance(oge, dict):
            adsiz += 1
            continue
        hedef = oge.get('item')
        ad = oge.get('name') or (hedef.get('name') if isinstance(hedef, dict) else '')
        if not str(ad or '').strip():
            adsiz += 1
    if adsiz:
        return 'kismi', f'{len(ogeler)} adım, {adsiz} öğede ad eksik'
    return 'var', f'{len(ogeler)} adım'


def baglanti_incele(sayfa, kok):
    kok_host = urllib.parse.urlparse(kok).netloc.lower()
    ic, dis, js_link, bos_metin, belirsiz = 0, 0, 0, 0, 0
    for b in sayfa.get('a', []):
        href = (b.get('href') or '').strip()
        metin = (b.get('metin') or '').strip()
        if not href or href.startswith('#'):
            continue
        if href.lower().startswith('javascript:'):
            js_link += 1
            continue
        if href.lower().startswith(('mailto:', 'tel:', 'whatsapp:')):
            continue
        tam = urllib.parse.urljoin(sayfa['url'], href)
        p = urllib.parse.urlparse(tam)
        if p.scheme not in ('http', 'https'):
            continue
        if p.netloc.lower() == kok_host:
            ic += 1
            if not metin:
                bos_metin += 1
            elif metin.lower().strip('.,!?:;»›>') in BELIRSIZ_CAPALAR:
                belirsiz += 1
        else:
            dis += 1
    return {'ic': ic, 'dis': dis, 'js': js_link, 'bos': bos_metin, 'belirsiz': belirsiz}


def yerel_ad(etiket):
    return etiket.rsplit('}', 1)[-1]


def sitemap_incele(url, sinir=100):
    baslangiclar = url if isinstance(url, list) else [url]
    url = baslangiclar[0]
    bilgi = {'url': url, 'durum': None, 'tur': None, 'url_sayisi': 0, 'alt': 0,
             'lastmod': False, 'gorsel': False, 'hatalar': [], 'tam': True, 'urller': set()}
    kuyruk, gorulen, tarihler, tarih_degerleri = list(dict.fromkeys(baslangiclar)), set(), [], []
    while kuyruk and len(gorulen) < sinir:
        adres = kuyruk.pop(0)
        if adres in gorulen:
            continue
        gorulen.add(adres)
        y = getir(adres)
        if adres == url:
            bilgi['durum'] = y['durum']
        try:
            kok = xml_oku(y)
            tur = yerel_ad(kok.tag)
            if tur not in ('sitemapindex', 'urlset'):
                raise ValueError('Sitemap kökü geçersiz')
            if adres == url:
                bilgi['tur'] = 'index' if tur == 'sitemapindex' else 'urlset'
            ogeler = [x for x in kok if yerel_ad(x.tag) == ('sitemap' if tur == 'sitemapindex' else 'url')]
            if not ogeler:
                bilgi['hatalar'].append(f'Boş sitemap: {adres}')
            for oge in ogeler:
                loc = next((x.text.strip() for x in oge if yerel_ad(x.tag) == 'loc' and x.text), '')
                if not loc.startswith(('https://', 'http://')):
                    bilgi['hatalar'].append(f'Geçersiz veya eksik loc: {adres}')
                    continue
                if tur == 'sitemapindex':
                    bilgi['alt'] += 1
                    if loc not in gorulen and loc not in kuyruk:
                        kuyruk.append(loc)
                else:
                    bilgi['url_sayisi'] += 1
                    bilgi['urller'].add(url_norm(loc))
                    tarihler.append(any(yerel_ad(x.tag) == 'lastmod' and (x.text or '').strip() for x in oge))
                    tarih_degerleri.extend((x.text or '').strip()[:16] for x in oge if yerel_ad(x.tag) == 'lastmod' and (x.text or '').strip())
                    bilgi['gorsel'] |= any(x.tag == '{http://www.google.com/schemas/sitemap-image/1.1}image' for x in oge)
        except (ValueError, ET.ParseError, OSError, EOFError) as hata:
            bilgi['hatalar'].append(f'{adres}: HTTP {y["durum"]}, {hata}')
    bilgi['tam'] = not kuyruk
    bilgi['lastmod'] = bool(tarihler) and all(tarihler)
    bilgi['tarih_tekrari'] = len(tarih_degerleri) >= 10 and max(Counter(tarih_degerleri).values()) / len(tarih_degerleri) > 0.8
    bilgi['not'] = f'{len(gorulen)} sitemap incelendi' + (f'; {sinir} dosya sınırı nedeniyle tarama eksik' if kuyruk else '')
    return bilgi


def site_tara(site):
    global ISTEK_DURUSU
    ISTEK_DURUSU = None
    kok = site['kok'].rstrip('/')
    https = kok.startswith('https://')
    sayfa_yollari = site.get('sayfalar', {'anasayfa': '/'})
    S = {}
    for ad, yol in sayfa_yollari.items():
        if yol:
            S[ad] = ayristir(getir(urllib.parse.urljoin(kok + '/', yol)))
    A = S.get('anasayfa')
    U = S.get('urun')
    K = S.get('kategori')
    B = S.get('blog')
    tum_html = '\n'.join(s['govde'] for s in S.values() if s and s['durum'] == 200 and not s['engel'])

    sonuc = {}

    def k(kimlik, durum, kanit=''):
        sonuc[kimlik] = {'durum': durum, 'kanit': kanit}

    def sayfa_yok(kimlik, ad):
        if site.get('profil') == 'kurumsal' and ad.startswith('Ürün') and not sayfa_yollari.get('urun'):
            k(kimlik, 'uygulanamaz', 'Kurumsal profil; ürün sayfası kapsamda değil')
        else:
            k(kimlik, 'olcumsuz', f'{ad} sayfası verilmedi ya da açılmadı')

    def acik(s):
        return s is not None and s['durum'] == 200 and not s['engel'] and not s.get('kesildi')

    # ---------- Temel meta ----------
    acik_sayfalar = [(ad, s) for ad, s in S.items() if acik(s)]
    for kimlik, okuyucu in (('title', lambda s: s['title']), ('description', lambda s: m1(s, 'description'))):
        if acik_sayfalar:
            degerler = [(ad, okuyucu(s)) for ad, s in acik_sayfalar]
            eksik = [ad for ad, deger in degerler if not deger]
            metinler = [deger for _, deger in degerler if deger]
            tekrar = len(metinler) != len(set(metinler))
            durum = 'yok' if len(eksik) == len(degerler) else 'kismi' if eksik or tekrar else 'var'
            k(kimlik, durum, '; '.join(f'{ad}: {len(deger)} karakter' for ad, deger in degerler)
              + ('; tekrar eden metin var' if tekrar else '') + '; uzunluk başarı eşiği değildir, anlam/özgünlük editoryal incelenmeli')
        else:
            sayfa_yok(kimlik, 'Hiçbir')
    if acik(A):
        k('html_lang', 'var' if A['lang'] else 'yok', f'lang="{A["lang"] or ""}"; içerik diliyle eşliği elle doğrulanmalı')
        k('viewport', 'var' if m1(A, 'viewport') else 'yok', m1(A, 'viewport')[:60])
        vitrin_sayfalari = [(ad, robots_direktif_incele(s)) for ad, s in acik_sayfalar if ad != 'kategori_sayfa2']
        noindex_sayfalar = [ad for ad, r_bilgi in vitrin_sayfalari if r_bilgi['noindex']]
        celiskili_sayfalar = [f'{ad} ({", ".join(r_bilgi["celiskiler"])})' for ad, r_bilgi in vitrin_sayfalari if r_bilgi['celiskiler']]
        r_ana = robots_direktif_incele(A)['metin']
        if noindex_sayfalar:
            k('robots_meta', 'yok', f'noindex bulunan örnek sayfa: {", ".join(noindex_sayfalar)}' + (f' | çelişki: {", ".join(celiskili_sayfalar)}' if celiskili_sayfalar else ''))
        elif celiskili_sayfalar:
            k('robots_meta', 'kismi', f'çelişkili robots direktifi: {", ".join(celiskili_sayfalar)}')
        else:
            k('robots_meta', 'var', r_ana or 'robots meta yok (varsayılan index)')
        k('max_image_preview', 'var' if 'max-image-preview:large' in r_ana.replace(' ', '').lower() else 'yok', r_ana or '-')
    else:
        for i in ('html_lang', 'viewport', 'robots_meta', 'max_image_preview'):
            sayfa_yok(i, 'Ana sayfa')

    canon = []
    coklu_canon = []
    izleme_canon = []
    for ad, s in S.items():
        if acik(s):
            c_liste = [x.get('href', '').strip() for x in s['link'].get('canonical', []) if x.get('href', '').strip()]
            c = c_liste[0] if c_liste else ''
            canon.append((ad, c))
            if len(set(c_liste)) > 1 or len(s['link'].get('canonical', [])) > 1:
                coklu_canon.append(ad)
            if izleme_parametresi_var_mi(c):
                izleme_canon.append(ad)
    if canon:
        eksik = [a for a, c in canon if not c]
        goreli = [a for a, c in canon if c and not c.startswith('http')]
        ek_notlar = []
        if coklu_canon:
            ek_notlar.append('birden fazla canonical: ' + ', '.join(coklu_canon))
        if izleme_canon:
            ek_notlar.append('izleme parametreli canonical: ' + ', '.join(izleme_canon))
        k('canonical', 'yok' if len(eksik) == len(canon) else ('kismi' if eksik or goreli or coklu_canon or izleme_canon else 'var'),
          ('; '.join(f'{a}: {c or "YOK"}' for a, c in canon) + (' | ' + '; '.join(ek_notlar) if ek_notlar else ''))[:300])
    else:
        sayfa_yok('canonical', 'Hiçbir')

    h1_ozet = [(ad, [metin for metin in s['h1'] if metin.strip()]) for ad, s in S.items() if acik(s)]
    if h1_ozet:
        durum = 'var' if all(metinler for _, metinler in h1_ozet) else 'kismi'
        k('tek_h1', durum, '; '.join(f'{ad}: {len(metinler)} dolu H1 ({" / ".join(metinler)[:160]})' for ad, metinler in h1_ozet) + '; sihirli H1 sayısı yoktur, başlık anlamı/yapısı elle incelenmeli')
    else:
        sayfa_yok('tek_h1', 'Hiçbir')

    cift = [ad for ad, s in acik_sayfalar if re.search(r'&(?:amp;|#0?39;|quot;|lt;|gt;)', ' '.join([s['title'], m1(s, 'description'), m1(s, 'og:title'), m1(s, 'og:description'), *s['h1']]))]
    k('cift_kacis', ('kismi' if cift else 'var') if acik_sayfalar else 'olcumsuz', 'Çift kaçış adayı meta/başlık: ' + ', '.join(cift) if cift else 'Örnek başlık/meta alanlarında çift kaçış izi bulunmadı; gövde elle incelenmeli')

    if acik(A) and acik(K):
        da, dk = m1(A, 'description'), m1(K, 'description')
        k('aciklama_benzersiz', 'kismi' if da and da == dk else ('var' if dk else 'yok'),
          'kategori açıklaması ana sayfayla aynı (varsayılana düşüyor)' if da and da == dk else f'kategori: {dk[:80]}')
    else:
        sayfa_yok('aciklama_benzersiz', 'Kategori')

    # ---------- Paylaşım önizlemesi ----------
    if acik(A):
        gerekli = ['og:title', 'og:description', 'og:image', 'og:url', 'og:type', 'og:site_name', 'og:locale']
        eksik = [g for g in gerekli if not m1(A, g)]
        k('og_temel', 'var' if not eksik else ('kismi' if len(eksik) < 4 else 'yok'), 'eksik: ' + ', '.join(eksik) if eksik else 'hepsi var')
    else:
        sayfa_yok('og_temel', 'Ana sayfa')

    def og_gorsel_degerlendir(kimlik, s, ad):
        if not acik(s):
            return sayfa_yok(kimlik, ad)
        g = m1(s, 'og:image')
        if not g:
            return k(kimlik, 'yok', 'og:image yok')
        if g.startswith('data:'):
            return k(kimlik, 'yok', 'og:image data: URI, WhatsApp/Facebook bunu okuyamaz')
        sorun = []
        if not g.startswith('https://'):
            sorun.append('https değil')
        bilgi = gorsel_getir(urllib.parse.urljoin(s['url'], g))
        if not bilgi or bilgi.get('durum') != 200:
            return k(kimlik, 'olcumsuz', f'görsel alınamadı ({bilgi and bilgi.get("durum")}): {g[:90]}')
        olcu = bilgi.get('olcu')
        if olcu and olcu[0]:
            gen, yuk, bicim = olcu
            oran = gen / yuk if yuk else 0
            if gen < 600 or yuk < 315:
                sorun.append(f'{gen}x{yuk} küçük')
            if oran > 2.4 or oran < 0.75:
                sorun.append(f'{gen}x{yuk} oranı {oran:.1f}:1 (ideal 1.91:1, 1200x630)')
            olcu_metni = f'{gen}x{yuk} {bicim}'
        else:
            olcu_metni = 'ölçü okunamadı'
            sorun.append('görsel biçimi/ölçüsü doğrulanamadı')
        if bilgi.get('kesildi'):
            sorun.append('boyut sınırında kesildi')
        if bilgi['bayt'] > 600 * 1024:
            sorun.append(f'{bilgi["bayt"] // 1024} KB, WhatsApp için ağır')
        if kimlik == 'og_gorsel_urun':
            sorun.append('görselin ürünü gösterdiği görsel incelemeyle doğrulanmalı')
        k(kimlik, 'kismi' if sorun else 'var', f'{olcu_metni}, {bilgi["bayt"] // 1024} KB' + (' | ' + '; '.join(sorun) if sorun else '') + f' | {g[:80]}')

    og_gorsel_degerlendir('og_gorsel_anasayfa', A, 'Ana sayfa')
    og_gorsel_degerlendir('og_gorsel_urun', U, 'Ürün')

    if acik(A):
        ek = [x for x in ('og:image:width', 'og:image:height', 'og:image:alt') if not m1(A, x)]
        k('og_gorsel_etiketleri', 'var' if not ek else ('kismi' if len(ek) < 3 else 'yok'), 'eksik: ' + ', '.join(ek) if ek else 'width/height/alt var')
        kart, site_hesabi = m1(A, 'twitter:card'), m1(A, 'twitter:site')
        k('twitter_kart', 'var' if kart == 'summary_large_image' and site_hesabi else ('kismi' if kart else 'yok'),
          f'card={kart or "-"}, site={site_hesabi or "-"}')
    else:
        sayfa_yok('og_gorsel_etiketleri', 'Ana sayfa')
        sayfa_yok('twitter_kart', 'Ana sayfa')

    if acik(U):
        tip = m1(U, 'og:type')
        fiyat = m1(U, 'product:price:amount') or m1(U, 'og:price:amount')
        k('og_urun', 'var' if tip == 'product' and fiyat else ('kismi' if tip == 'product' else 'yok'),
          f'og:type={tip or "-"}, product:price:amount={fiyat or "-"}')
    else:
        sayfa_yok('og_urun', 'Ürün')

    # ---------- Favicon ----------
    ikonlar = []
    if acik(A):
        for rel in ('icon', 'shortcut'):
            ikonlar.extend(A['link'].get(rel, []))
        k('favicon_link', 'var' if ikonlar else 'yok', ', '.join(f'{i.get("href", "")[:60]} {i.get("sizes", "")}' for i in ikonlar[:4]) or 'rel=icon yok')
        apple = A['link'].get('apple-touch-icon', [])
        k('apple_touch_icon', 'var' if apple else 'yok', apple[0].get('href', '')[:80] if apple else 'apple-touch-icon yok')
        k('theme_color', 'var' if m1(A, 'theme-color') else 'yok', m1(A, 'theme-color') or '-')
        man = A['link'].get('manifest', [])
        man_url = urllib.parse.urljoin(A['url'], man[0].get('href', '')) if man else kok + '/site.webmanifest'
        my = getir(man_url, azami=200000)
        try:
            manifest = json.loads(my['govde']) if my['durum'] == 200 and not my.get('kesildi') else None
        except (ValueError, TypeError):
            manifest = None
        ikonlar_manifest = manifest.get('icons', []) if isinstance(manifest, dict) else []
        ikonlar_manifest = ikonlar_manifest if isinstance(ikonlar_manifest, list) else []
        boyutlar = {boyut for ikon in ikonlar_manifest if isinstance(ikon, dict) and ikon.get('src') for boyut in str(ikon.get('sizes', '')).split()}
        man_tam = isinstance(manifest, dict) and (manifest.get('name') or manifest.get('short_name')) and {'192x192', '512x512'} <= boyutlar
        k('manifest', 'kismi' if man_tam else ('yok' if my['durum'] in (404, 410) or my['durum'] == 200 else 'olcumsuz'),
          f'{"link var" if man else "link yok"}, HTTP {my["durum"]}; ' + ('JSON ve simge tanımları var; simge dosyaları ayrıca doğrulanmalı' if man_tam else 'geçerli manifest ve 192/512 simge tanımları doğrulanamadı'))
    else:
        for i in ('favicon_link', 'apple_touch_icon', 'theme_color', 'manifest'):
            sayfa_yok(i, 'Ana sayfa')
    fy = getir(kok + '/favicon.ico', azami=500000)
    fbayt = len(fy['ham']) if fy['durum'] == 200 else 0
    favicon_olcu = gorsel_olcu(fy['ham']) if fbayt else None
    k('favicon_ico', 'var' if favicon_olcu and favicon_olcu[2] == 'ico' else ('yok' if fy['durum'] in (200, 404, 410) else 'olcumsuz'),
      f'/favicon.ico HTTP {fy["durum"]}, {fbayt} bayt; ' + ('ICO başlığı doğrulandı' if favicon_olcu and favicon_olcu[2] == 'ico' else 'geçerli ICO başlığı bulunamadı'))
    olculer = []
    for i in ikonlar[:3]:
        b = gorsel_getir(urllib.parse.urljoin(A['url'], i.get('href', '')))
        if b and b.get('olcu'):
            olculer.append(b['olcu'])
    if fbayt:
        o = gorsel_olcu(fy['ham'])
        if o:
            olculer.append(o)
    if olculer:
        uygun = [o for o in olculer if o[2] != 'svg' and o[0] == o[1] and o[0] >= 8]
        k('favicon_48', 'var' if uygun else 'kismi', ', '.join(f'{o[0]}x{o[1]} {o[2]}' for o in olculer) + ' | kare ve en az 8 piksel; 48 pikselden büyük önerilir. SVG uygunluğu ayrıca doğrulanmalı')
    else:
        k('favicon_48', 'yok' if acik(A) else 'olcumsuz', 'Örneklerde okunabilir favicon doğrulanamadı')

    # ---------- Yapısal veri ----------
    tum_dugum = [d for s in S.values() if acik(s) for d in s['ld']]
    hata = sum(s['ld_hata'] for s in S.values() if acik(s))
    blok = sum(s['ld_blok'] for s in S.values() if acik(s))
    kopuk_id = [f'{ad}:{ref}' for ad, s in acik_sayfalar for ref in s.get('ld_kopuk_id', [])]
    ld_kanit = f'{blok} blok, {hata} ayrıştırma hatası' + (f'; kopuk @id referansı: {", ".join(kopuk_id[:5])}' if kopuk_id else '')
    k('ld_gecerli', 'olcumsuz' if not acik_sayfalar else 'yok' if blok == 0 else ('kismi' if hata or kopuk_id else 'var'), ld_kanit)

    org_turleri = ('organization', 'localbusiness', 'onlinestore', 'store', 'corporation', 'electronicsstore', 'professionalservice')
    orglar = [d for d in (A['ld'] if acik(A) else []) if any(t in org_turleri for t in turler(d))]
    if orglar:
        o = orglar[0]
        eksik = [x for x in ('@id', 'logo', 'sameAs', 'url') if not o.get(x)]
        if not (o.get('contactPoint') or o.get('telephone')):
            eksik.append('contactPoint/telephone')
        k('org_sema', 'var' if not eksik else 'kismi', f'{"/".join(turler(o))}' + (' | eksik: ' + ', '.join(eksik) if eksik else ' | @id, logo, sameAs, iletişim var'))
        yereller = [dugum for dugum in tum_dugum if any('localbusiness' in t or 'store' in t or t in ('professionalservice', 'repairshop') for t in turler(dugum))]
        yerel = yereller[0] if yereller else o
        yerel_eksik = [x for x in ('openingHoursSpecification', 'geo', 'priceRange', 'hasMap') if not yerel.get(x) and not (x == 'openingHoursSpecification' and yerel.get('openingHours'))]
        adres = yerel.get('address') or {}
        if not isinstance(adres, dict):
            adres = {}
        yerel_eksik += ['address.' + x for x in ('streetAddress', 'addressLocality', 'addressRegion', 'addressCountry') if not adres.get(x)]
        k('yerel_isletme', 'var' if yereller and not yerel_eksik else ('kismi' if yereller else 'olcumsuz'),
          ('Şema alanlarında eksik: ' + ', '.join(yerel_eksik) if yerel_eksik else 'adres, saat, konum, harita ve fiyat aralığı var') + '; gerçek işletmeyle eşliği ve uygulanabilirlik ayrıca doğrulanmalı')
    elif acik(A):
        k('org_sema', 'yok', 'ana sayfada Organization/LocalBusiness yok')
        k('yerel_isletme', 'yok', 'LocalBusiness yok')
    else:
        sayfa_yok('org_sema', 'Ana sayfa')
        sayfa_yok('yerel_isletme', 'Ana sayfa')

    if acik(A):
        ws = dugum_bul(A, 'WebSite')
        tam = ws and any(w.get('name') and w.get('url') for w in ws)
        k('website_sema', 'var' if tam else ('kismi' if ws else 'yok'), 'WebSite name/url var; SearchAction zorunlu değil' if tam else ('WebSite var, name/url eksik' if ws else 'WebSite şeması yok'))
    else:
        sayfa_yok('website_sema', 'Ana sayfa')

    hizmet = S.get('hizmet')
    ekmek = [(ad, *breadcrumb_incele(s)) for ad, s in (('urun', U), ('kategori', K), ('hizmet', hizmet), ('blog', B)) if acik(s)]
    if ekmek:
        durum_ekmek = 'var' if all(d == 'var' for _, d, _ in ekmek) else ('kismi' if any(d in ('var', 'kismi') for _, d, _ in ekmek) else 'yok')
        k('breadcrumb', durum_ekmek, ', '.join(f'{a}: {notu}' for a, _, notu in ekmek))
    else:
        sayfa_yok('breadcrumb', 'Alt (ürün/kategori/hizmet/blog)')

    if acik(K):
        liste = dugum_bul(K, 'ItemList', 'CollectionPage', 'OfferCatalog')
        k('kategori_sema', 'var' if liste else 'yok', ', '.join(sorted({'/'.join(turler(d)) for d in liste})) or 'ItemList/CollectionPage yok')
    else:
        sayfa_yok('kategori_sema', 'Kategori')

    if acik(B):
        yazi = dugum_bul(B, 'BlogPosting', 'Article', 'NewsArticle', 'TechArticle')
        if yazi:
            y0 = yazi[0]
            eksik = [x for x in ('author', 'datePublished', 'dateModified', 'image', 'headline') if not y0.get(x)]
            yazar = y0.get('author') or {}
            notu = ''
            k('blog_sema', 'var' if not eksik and not notu else 'kismi', ('eksik: ' + ', '.join(eksik) if eksik else 'alanlar tam') + notu)
        else:
            k('blog_sema', 'yok', 'Article/BlogPosting yok')
    else:
        sayfa_yok('blog_sema', 'Blog yazısı')

    sss = [ad for ad, s in S.items() if acik(s) and dugum_bul(s, 'FAQPage')]
    k('faq_sema', 'kismi' if sss else 'olcumsuz', ('FAQPage: ' + ', '.join(sss) + '; görünen sorularla eşleşmesi doğrulanmalı') if sss else 'FAQPage yok; görünür SSS bulunup bulunmadığı ve uygulanabilirlik elle doğrulanmalı')

    hizmet = S.get('hizmet')
    if acik(hizmet):
        servisler = dugum_bul(hizmet, 'Service')
        eksik = [x for x in ('name', 'serviceType', 'areaServed', 'provider') if not (servisler and servisler[0].get(x))]
        k('hizmet_sema', 'kismi' if servisler else 'olcumsuz', (('Service var; örnek alanlarda eksik: ' + ', '.join(eksik) if eksik else 'Service name/serviceType/areaServed/provider var') if servisler else 'Service şeması bulunmadı') + '; şema tercihi Google sıralama veya zengin sonuç şartı değildir; fiyat/süre/garanti ve iletişim görünür içerikte doğrulanmalı')
    else:
        sayfa_yok('hizmet_sema', 'Hizmet')
    videolar = [ad for ad, s in acik_sayfalar if dugum_bul(s, 'VideoObject')]
    k('video_sema', 'kismi' if videolar else 'olcumsuz', 'VideoObject: ' + ', '.join(videolar) + '; gerçek video, görünür oynatıcı ve güncel Google alan koşulları ayrıca doğrulanmalı' if videolar else 'VideoObject yok; sayfada video bulunup bulunmadığı ve uygulanabilirlik elle doğrulanmalı')

    if acik(U):
        urunler = dugum_bul(U, 'Product', 'ProductGroup', 'IndividualProduct')
        if not urunler:
            k('urun_sema', 'yok', 'Product şeması yok')
            for i in ('urun_offer', 'urun_gorsel', 'urun_kimlik', 'urun_aciklama', 'urun_kargo', 'urun_iade', 'urun_offer_ayrinti', 'urun_puan'):
                k(i, 'yok', 'Product şeması yok')
        else:
            p = urunler[0]
            k('urun_sema', 'var' if p.get('name') else 'kismi', '/'.join(turler(p)) + f' | ad: {"var" if p.get("name") else "yok"}, marka: {"var" if p.get("brand") else "yok"}; Google uygunluğu ayrıca değerlendirilir')
            o = p.get('offers') or {}
            if isinstance(o, list):
                o = o[0] if o else {}
            if 'productgroup' in turler(p) and not o:
                var_ = p.get('hasVariant') or []
                var_ = var_ if isinstance(var_, list) else [var_]
                if var_ and isinstance(var_[0], dict):
                    o = var_[0].get('offers') or {}
                    o = o[0] if isinstance(o, list) and o else o
            if not isinstance(o, dict):
                o = {}
            if 'aggregateoffer' in turler(o):
                o = dict(o, price=o.get('lowPrice') or o.get('price'))
            if not o:
                k('urun_offer', 'yok', 'offers yok (Google: offers, review ya da aggregateRating zorunlu)')
            else:
                fiyat_degeri = o.get('price', (o.get('priceSpecification') or {}).get('price') if isinstance(o.get('priceSpecification') or {}, dict) else None)
                eksik = [x for x in ('priceCurrency', 'availability') if not o.get(x)]
                if fiyat_degeri is None or fiyat_degeri == '':
                    eksik.append('price')
                k('urun_offer', 'var' if not eksik else 'kismi', ('eksik: ' + ', '.join(eksik)) if eksik else f'{o.get("price")} {o.get("priceCurrency")}, {str(o.get("availability")).rsplit("/", 1)[-1]}')
            img = p.get('image')
            adet = len(img) if isinstance(img, list) else (1 if img else 0)
            k('urun_gorsel', 'var' if adet >= 2 else ('kismi' if adet == 1 else 'yok'), f'{adet} görsel')
            gtin = [x for x in p if x.startswith('gtin') or x == 'mpn']
            k('urun_kimlik', 'var' if p.get('sku') and gtin else ('kismi' if p.get('sku') or gtin else 'yok'),
              f'sku={p.get("sku") or "-"}, ' + (', '.join(f'{x}={p[x]}' for x in gtin) or 'gtin/mpn yok'))
            acik_m = re.sub(r'\s+', ' ', str(p.get('description') or ''))
            k('urun_aciklama', 'kismi' if acik_m else 'yok', f'{len(acik_m)} karakter; uzunluk sıralama eşiği değildir, fayda/doğruluk editoryal incelenmeli')
            k('urun_kargo', 'kismi' if isinstance(o, dict) and o.get('shippingDetails') else 'yok', 'shippingDetails ' + ('var; ücret, ülke ve süre alanları ayrıca doğrulanmalı' if isinstance(o, dict) and o.get('shippingDetails') else 'yok'))
            iade = (isinstance(o, dict) and o.get('hasMerchantReturnPolicy')) or any(d.get('hasMerchantReturnPolicy') for d in tum_dugum)
            k('urun_iade', 'kismi' if iade else 'yok', 'hasMerchantReturnPolicy ' + ('var; politika alanları ve görünür metinle uyum ayrıca doğrulanmalı' if iade else 'yok'))
            ayrinti = [x for x in ('itemCondition', 'priceValidUntil', 'seller') if not (isinstance(o, dict) and o.get(x))]
            k('urun_offer_ayrinti', 'var' if not ayrinti else ('kismi' if len(ayrinti) < 3 else 'yok'), ('eksik: ' + ', '.join(ayrinti)) if ayrinti else 'itemCondition, priceValidUntil, seller var')
            k('urun_puan', 'kismi' if p.get('aggregateRating') or p.get('review') else 'olcumsuz', 'Yorum/puan şeması var; gerçek ve görünür yorumlarla doğrulanmalı' if p.get('aggregateRating') or p.get('review') else 'Yorum yoksa uygulanamaz; gerçek yorum varlığı elle doğrulanmalı')
    else:
        for i in ('urun_sema', 'urun_offer', 'urun_gorsel', 'urun_kimlik', 'urun_aciklama', 'urun_kargo', 'urun_iade', 'urun_offer_ayrinti', 'urun_puan'):
            sayfa_yok(i, 'Ürün')

    # ---------- URL ve tarama ----------
    ry = getir(kok + '/robots.txt', azami=500000)
    robots = ry['govde'] if ry['durum'] == 200 else ''
    sm_satirlari = re.findall(r'(?im)^\s*sitemap:\s*(\S+)', robots)
    k('robots_txt', 'var' if ry['durum'] == 200 and sm_satirlari and not engel_mi(robots) else ('kismi' if ry['durum'] == 200 and not engel_mi(robots) else 'yok' if ry['durum'] in (404, 410) else 'olcumsuz'),
      f'HTTP {ry["durum"]}, {len(robots.splitlines())} satır, Sitemap satırı: {len(sm_satirlari)}')
    sm = sitemap_incele(sm_satirlari if sm_satirlari else kok + '/sitemap.xml', site.get('sitemap_siniri', 100))
    sm_sorunlu = bool(sm['hatalar']) or not sm['tam']
    k('sitemap', ('kismi' if sm_sorunlu else 'var') if sm['url_sayisi'] else ('yok' if sm['durum'] in (200, 404, 410) else 'olcumsuz'),
      f'HTTP {sm["durum"]}, {sm["tur"] or "-"}, ' + (f'{sm["alt"]} alt sitemap, ' if sm['alt'] else '') + f'{sm["url_sayisi"]} URL' + (f' ({sm["not"]})' if sm.get('not') else ''))
    if sm['hatalar']:
        sonuc['sitemap']['kanit'] += '; ' + '; '.join(sm['hatalar'][:5])
    for kimlik, alan in (('sitemap_lastmod', 'lastmod'), ('sitemap_gorsel', 'gorsel')):
        durum = 'olcumsuz' if not sm['url_sayisi'] else ('kismi' if sm_sorunlu else 'var') if sm[alan] else 'yok'
        k(kimlik, durum, f'{alan} varlığı: {sm[alan]}; tam tarama: {sm["tam"]}. Tarihlerin/görsel adreslerinin doğruluğu ayrıca denetlenmeli')
    if sm['tarih_tekrari']:
        k('sitemap_lastmod', 'kismi', 'En az 10 URL örneğinde lastmod değerlerinin %80’den fazlası aynı tarih/dakikada; toplu yayın veya senkron olabilir, sahte tarih kanıtı değildir. Gerçek içerik değişimiyle karşılaştırılmalı')

    vitrin_ornekleri = [(ad, s) for ad, s in acik_sayfalar if ad != 'kategori_sayfa2']
    if not sm['url_sayisi'] or not vitrin_ornekleri:
        k('sitemap_tutarlilik', 'olcumsuz', 'Sitemap URL listesi veya açık örnek sayfa yok')
    else:
        celiskili_sm, eksik_sm = [], []
        for ad, s in vitrin_ornekleri:
            r_bilgi = robots_direktif_incele(s)
            c = (s['link'].get('canonical') or [{}])[0].get('href', '')
            sayfa_u = url_norm(s['url'])
            canon_u = url_norm(urllib.parse.urljoin(s['url'], c)) if c else sayfa_u
            farkli_canon = bool(c) and canon_u != sayfa_u
            haritada = sayfa_u in sm['urller']
            if (r_bilgi['noindex'] or farkli_canon) and haritada:
                celiskili_sm.append(f'{ad} ({"noindex" if r_bilgi["noindex"] else "farklı canonical"})')
            elif not r_bilgi['noindex'] and not farkli_canon and not haritada:
                eksik_sm.append(ad)
        if celiskili_sm:
            k('sitemap_tutarlilik', 'yok', 'Sitemap’te olmaması gereken örnek sayfa: ' + ', '.join(celiskili_sm))
        elif eksik_sm:
            k('sitemap_tutarlilik', 'kismi', ('İndekslenebilir örnek sayfa sitemap’te bulunamadı: ' if sm['tam'] else 'Kısmi sitemap taramasında henüz görülmeyen örnek: ') + ', '.join(eksik_sm))
        else:
            k('sitemap_tutarlilik', 'var', f'{len(vitrin_ornekleri)} örnek sayfa sitemap ile tutarlı')

    if acik_sayfalar:
        bag_ozet = [(ad, baglanti_incele(s, kok)) for ad, s in acik_sayfalar]
        ic_yok = [ad for ad, b in bag_ozet if b['ic'] == 0]
        sorunlu_bag = []
        for ad, b in bag_ozet:
            if b['js']:
                sorunlu_bag.append(f'{ad}: {b["js"]} javascript: link')
            if b['bos']:
                sorunlu_bag.append(f'{ad}: {b["bos"]} metinsiz iç link')
            if b['belirsiz']:
                sorunlu_bag.append(f'{ad}: {b["belirsiz"]} belirsiz çapa metni')
        kanit_bag = '; '.join(f'{ad}: {b["ic"]} iç / {b["dis"]} dış link' for ad, b in bag_ozet)
        if sorunlu_bag:
            kanit_bag += ' | ' + '; '.join(sorunlu_bag)
        durum_bag = 'yok' if len(ic_yok) == len(bag_ozet) else ('kismi' if ic_yok or sorunlu_bag else 'var')
        k('ic_baglanti', durum_bag, kanit_bag)
    else:
        sayfa_yok('ic_baglanti', 'Hiçbir')

    if acik(U):
        yol = urllib.parse.urlparse(U['url']).path
        sorun = []
        if yol != yol.lower():
            sorun.append('büyük harf')
        if '--' in yol or '_' in yol:
            sorun.append('çift tire ya da alt çizgi')
        son = yol.rstrip('/').rsplit('/', 1)[-1]
        if re.fullmatch(r'[0-9]+', son):
            sorun.append('yalnızca sayısal yol; kullanıcı için açıklayıcılık elle değerlendirilmeli')
        k('urun_url', 'kismi' if sorun else 'var', f'{yol}' + (' | ' + ', '.join(sorun) if sorun else '') + ' | ASCII/uzunluk/ID zorunlu sıralama kuralı değildir')
        c = (U['link'].get('canonical') or [{}])[0].get('href', '')
        kendi = c.rstrip('/') == U['url'].split('?')[0].rstrip('/') and not izleme_parametresi_var_mi(c)
        k('urun_canonical', 'var' if kendi else ('kismi' if c else 'yok'), f'canonical: {c or "YOK"}' + (' (izleme parametresi içeriyor)' if izleme_parametresi_var_mi(c) else ''))
        ty = getir(U['url'].split('?')[0].rstrip('/') + '/', yonlendir=False)
        if ty['durum'] in (301, 308):
            k('sonda_egik_cizgi', 'var', 'sonda / olan adres 301 ile tek adrese gidiyor')
        elif ty['durum'] == 200:
            ta = ayristir(ty)
            tc = (ta['link'].get('canonical') or [{}])[0].get('href', '')
            k('sonda_egik_cizgi', 'kismi' if tc.rstrip('/') == U['url'].rstrip('/') else 'yok', f'sonda / ile HTTP 200 açılıyor, canonical {"aynı adrese" if tc else "yok"}')
        else:
            k('sonda_egik_cizgi', 'var' if ty['durum'] in (404, 410) else 'olcumsuz', f'sonda / ile HTTP {ty["durum"]}')
    else:
        for i in ('urun_url', 'urun_canonical', 'sonda_egik_cizgi'):
            sayfa_yok(i, 'Ürün')

    K2 = S.get('kategori_sayfa2')
    if acik(K2):
        c = (K2['link'].get('canonical') or [{}])[0].get('href', '')
        kendi = bool(c) and c.split('#')[0] == K2['url'].split('#')[0]
        bir = K and c.rstrip('/') == K['url'].split('?')[0].rstrip('/')
        r2 = m1(K2, 'robots')
        k('sayfalama_canonical', 'var' if kendi else ('yok' if bir else 'kismi'),
          f'2. sayfa canonical: {c or "YOK"}' + (' (1. sayfaya gidiyor, 2+ sayfadaki ürünler keşfedilmez)' if bir else '') + f', robots: {r2 or "-"}')
    else:
        sayfa_yok('sayfalama_canonical', 'Kategori 2. sayfa')

    yy = getir(kok + '/seo-kontrol-olmayan-sayfa-zx81q', yonlendir=False)
    k('gercek_404', 'var' if yy['durum'] in (404, 410) else 'kismi' if yy['durum'] in (301, 302) else 'yok' if yy['durum'] == 200 else 'olcumsuz', f'olmayan sayfa HTTP {yy["durum"]}')
    if https:
        hy = getir('http://' + kok[len('https://'):] + '/', yonlendir=False, durdur=False)
        hedef = hy['basliklar'].get('location', '')
        k('https_yonlendirme', 'var' if hy['durum'] in (301, 308) and hedef.rstrip('/') == kok else 'kismi' if hy['durum'] in (200, 301, 302, 307, 308) else 'olcumsuz',
          f'http:// HTTP {hy["durum"]} → {hedef or "-"}')
    else:
        k('https_yonlendirme', 'olcumsuz', 'yerel/http adres, canlıda ölçülmeli')

    alternatif = site.get('alternatif_kok')
    if alternatif:
        ay = getir(alternatif.rstrip('/') + '/', yonlendir=False, durdur=False)
        hedef = urllib.parse.urljoin(alternatif, ay['basliklar'].get('location', ''))
        dogru = ay['durum'] in (301, 308) and hedef.rstrip('/') == kok
        k('www_yonlendirme', 'var' if dogru else 'kismi' if ay['durum'] in (200, 301, 302, 307, 308) else 'olcumsuz', f'Alternatif kök HTTP {ay["durum"]}; hedef: {hedef}; zincir ve canonical eşliği ayrıca doğrulanmalı')
    else:
        k('www_yonlendirme', 'olcumsuz', 'alternatif_kok verilmedi; kapsam dışı hosta kendiliğinden istek atılmadı')

    # ---------- AI arama görünürlüğü ----------
    ly = getir(kok + '/llms.txt', azami=2 * 1024 * 1024)
    lbayt = len(ly['ham']) if ly['durum'] == 200 else 0
    lgecerli = ly['durum'] == 200 and ly['govde'].lstrip().startswith('#') and lbayt >= 300 and '<html' not in ly['govde'][:500].lower()
    k('llms_txt', 'kismi' if lgecerli else 'uygulanamaz' if ly['durum'] in (404, 410) else 'olcumsuz', f'HTTP {ly["durum"]}, {lbayt} bayt; yardımcı dosya, Google gereksinimi değil' + (f', ilk satır: {ly["govde"].strip().splitlines()[0][:60]}' if ly['govde'].strip() and lbayt else ''))
    lfy = getir(kok + '/llms-full.txt', azami=1024 * 1024)
    lfbayt = len(lfy['ham']) if lfy['durum'] == 200 else 0
    k('llms_full', 'kismi' if lfy['durum'] == 200 and lfbayt >= 1000 and '<html' not in lfy['govde'][:500].lower() else 'uygulanamaz' if lfy['durum'] in (404, 410) else 'olcumsuz', f'HTTP {lfy["durum"]}, {lfbayt} bayt; yardımcı dosya, görünürlük kanıtı değil')

    gruplar = robots_ayristir(robots)
    yollar = {urllib.parse.urlparse(s['url']).path + ('?' + urllib.parse.urlparse(s['url']).query if urllib.parse.urlparse(s['url']).query else '') for s in S.values() if acik(s)} or {'/'}
    engelli_arama = [f'{b}: {yol}' for b in AI_ARAMA_BOTLARI for yol in sorted(yollar) if bot_engelli_mi(gruplar, b, yol)]
    robots_olculebilir = (ry['durum'] == 200 and not engel_mi(robots) and not ry.get('kesildi') and '<html' not in robots[:500].lower()) or ry['durum'] in (404, 410)
    k('ai_arama_botlari', 'olcumsuz' if not robots_olculebilir else ('yok' if engelli_arama else 'var'),
      f'robots.txt HTTP {ry["durum"]}; ' + (('engelli: ' + ', '.join(engelli_arama)) if engelli_arama else 'yalnız örnek URL yollarında engel bulunmadı; gerçek bot erişimi garantisi değildir'))
    k('ai_egitim_botlari', 'olcumsuz', 'İzin/engel tercihi başarı puanı değildir; kullanıcının politikasıyla karşılaştırılmalı')
    anilan = [b for b in AI_ARAMA_BOTLARI + AI_EGITIM_BOTLARI if b.lower() in robots.lower()]
    k('ai_bot_acik_liste', 'olcumsuz' if not robots_olculebilir else 'uygulanamaz', 'Botları adıyla listelemek zorunlu değildir; en özgül eşleşen grup, yoksa * uygulanır. Adıyla anılan bot sayısı: ' + str(len(anilan)))

    if site.get('bot_kontrol'):
        sonuclar = []
        for ad, ua in CANLI_BOT_UA.items():
            by = getir(kok + '/', ua=ua, azami=300000, durdur=False)
            kod = 'WAF' if engel_mi(by['govde']) else by['durum']
            sonuclar.append((ad, kod))
        kotu = [f'{a}={c}' for a, c in sonuclar if c != 200]
        k('ai_bot_erisim', 'kismi' if not kotu else 'olcumsuz', ('UA denemesinde alınamayan yanıtlar: ' + ', '.join(kotu)) if kotu else 'UA taklidine 200 geldi; doğrulanmış bot IP erişimi ve içerik eşliği ölçülmedi')
    else:
        k('ai_bot_erisim', 'olcumsuz', 'bot_kontrol kapalı')

    feed, feed_hatalari = None, []
    for yol in ([site['feed']] if site.get('feed') else []) + FEED_YOLLARI:
        fy2 = getir(urllib.parse.urljoin(kok + '/', yol), azami=3 * 1024 * 1024)
        if fy2['durum'] == 200:
            try:
                fk = xml_oku(fy2)
                ogeler = [oge for oge in fk.iter() if yerel_ad(oge.tag) in ('item', 'entry')]
                if yerel_ad(fk.tag) in ('rss', 'feed') and ogeler:
                    gerekli = ('id', 'title', 'description', 'link', 'image_link', 'availability', 'price')
                    eksik = sum(not any(yerel_ad(x.tag) == ad and (x.text or '').strip() for x in oge) for oge in ogeler for ad in gerekli)
                    feed = (yol, len(ogeler), eksik)
                    break
            except (ValueError, ET.ParseError, OSError, EOFError) as hata:
                feed_hatalari.append(f'{yol}: {hata}')
        elif fy2['durum'] not in (404, 410):
            feed_hatalari.append(f'{yol}: HTTP {fy2["durum"]}')
    k('merchant_feed', 'kismi' if feed else 'olcumsuz', f'{feed[0]}: {feed[1]} ürün, temel alanlarda {feed[2]} eksik; Merchant uygunluğu ve fiyat/stok eşliği doğrulanmalı' if feed else 'Bilinen yollarda geçerli ürün feed’i doğrulanamadı; özel/gizli adres olabilir')
    if site.get('profil') == 'kurumsal' and not U:
        k('merchant_feed', 'uygulanamaz', 'Kurumsal profil; ürün satışı kapsamda değil')

    # ---------- Doğrulama etiketleri ----------
    for kimlik, ad in (('dogrulama_google', 'google-site-verification'), ('dogrulama_bing', 'msvalidate.01'),
                       ('dogrulama_yandex', 'yandex-verification'), ('dogrulama_facebook', 'facebook-domain-verification'),
                       ('dogrulama_pinterest', 'p:domain_verify')):
        deger = m1(A, ad) if acik(A) else ''
        k(kimlik, 'kismi' if deger else 'olcumsuz', f'{ad} meta etiketi bulundu; hesap sahipliği doğrulanmadı' if deger else f'{ad} görünmüyor; DNS/dosya veya hesap erişimi olmadan doğrulama durumu bilinemez')

    # ---------- Ölçüm ve pazarlama ----------
    izler = {
        'olcum_ga4': (r'googletagmanager\.com/gtag/js\?id=G-|gtag\(\s*[\'"]config[\'"]\s*,\s*[\'"]G-[A-Z0-9]{6,}', 'GA4 (gtag.js)'),
        'olcum_gtm': (r'googletagmanager\.com/gtm\.js|GTM-[A-Z0-9]{5,}', 'Google Tag Manager'),
        'olcum_consent': (r'gtag\(\s*[\'"]consent[\'"]\s*,\s*[\'"]default', 'Consent Mode v2 varsayılanı'),
        'olcum_meta_pixel': (r'connect\.facebook\.net/[^"\']*/fbevents\.js|fbq\(\s*[\'"]init', 'Meta Pixel'),
        'olcum_google_ads': (r'AW-\d{8,}', 'Google Ads dönüşüm etiketi'),
        'olcum_tiktok': (r'analytics\.tiktok\.com', 'TikTok Pixel'),
        'olcum_clarity': (r'clarity\.ms/tag', 'Microsoft Clarity'),
        'olcum_yandex': (r'mc\.yandex\.(ru|com)/metrika', 'Yandex Metrika'),
        'olcum_pinterest': (r's\.pinimg\.com/ct/core\.js|pintrk\(', 'Pinterest Tag'),
    }
    for kimlik, (desen, ad) in izler.items():
        bulunan = re.findall(desen, tum_html)
        k(kimlik, 'kismi' if bulunan else 'olcumsuz', f'{ad} ' + ('HTML’de iz bulundu; onay öncesi/sonrası ağ istekleri ve olay içeriği doğrulanmalı' if bulunan else 'HTML’de iz yok; harici JS, GTM veya onay sonrası yüklenebilir'))
    if acik(U):
        olaylar = [o for o in ('view_item', 'ViewContent', '"ecommerce"', "'ecommerce'", 'add_to_cart', 'AddToCart') if o in U['govde']]
        k('olcum_eticaret_olay', 'kismi' if olaylar else 'olcumsuz', ('ürün HTML’sinde olay adı bulundu; gönderim ve içerik doğrulanmadı: ' + ', '.join(sorted(set(o.strip('"\'') for o in olaylar)))) if olaylar else 'ürün HTML’sinde olay adı bulunmadı; tarayıcıda doğrulanmalı')
    else:
        sayfa_yok('olcum_eticaret_olay', 'Ürün')

    # ---------- Performans ve görsel ----------
    gorseller = [g for s in S.values() if acik(s) for g in s['img']]
    if gorseller:
        tembel = sum(1 for g in gorseller if g.get('loading') == 'lazy')
        kume = sum(1 for g in gorseller if g.get('srcset'))
        modern = sum(1 for g in gorseller if re.search(r'\.(webp|avif)', (g.get('src', '') + g.get('srcset', '') + g.get('data-src', '')).lower()))
        altsiz = sum(1 for g in gorseller if 'alt' not in g)
        bos_alt = sum(1 for g in gorseller if 'alt' in g and not g['alt'].strip())
        n = len(gorseller)
        k('gorsel_lazy', 'kismi' if tembel else 'olcumsuz', f'{tembel}/{n} görsel loading=lazy; ekran altı yerleşim ve LCP görseli tarayıcıda doğrulanmalı')
        k('gorsel_srcset', 'var' if kume / n >= 0.3 else ('kismi' if kume else 'yok'), f'{kume}/{n} görsel srcset')
        k('gorsel_modern', 'var' if modern / n >= 0.5 else ('kismi' if modern else 'yok'), f'{modern}/{n} webp/avif')
        k('gorsel_alt', 'kismi' if altsiz or bos_alt else 'var', f'{altsiz}/{n} görselde alt özniteliği yok, {bos_alt} bilinçli boş olabilir; dekoratif/ürün ayrımı elle doğrulanmalı')
    else:
        for i in ('gorsel_lazy', 'gorsel_srcset', 'gorsel_modern', 'gorsel_alt'):
            k(i, 'olcumsuz', 'görsel bulunamadı')
    if acik(A):
        on = A['link'].get('preconnect', []) + A['link'].get('dns-prefetch', []) + A['link'].get('preload', []) + A['link'].get('modulepreload', [])
        k('on_baglanti', 'var' if on else 'yok', f'{len(on)} preconnect/preload')
    else:
        sayfa_yok('on_baglanti', 'Ana sayfa')

    for kimlik, gerekce in site.get('uygulanamaz', {}).items():
        if kimlik not in sonuc or not isinstance(gerekce, str) or not gerekce.strip():
            raise ValueError(f'Uygulanamaz kontrolü veya gerekçesi geçersiz: {kimlik}')
        k(kimlik, 'uygulanamaz', gerekce)
    engelli = [ad for ad, s in S.items() if s and s['engel']]
    acilmayan = [f'{ad} HTTP {s["durum"]}' for ad, s in S.items() if s and s['durum'] != 200]
    kesilen = [ad for ad, s in S.items() if s and s.get('kesildi')]
    return {'ad': site['ad'], 'kok': kok, 'biz': bool(site.get('biz')), 'kontroller': sonuc,
            'sayfalar': {ad: (s['url'] if s else '') for ad, s in S.items()},
            'sayfa_ozetleri': [{'tur': ad, 'url': s['url'], 'title': s['title'],
                              'description': m1(s, 'description'), 'canonical': (s['link'].get('canonical') or [{}])[0].get('href', ''),
                              'h1': s['h1'], 'alt_baslik_sayisi': len(s.get('alt_basliklar', [])),
                              'ic_link': baglanti_incele(s, kok)['ic'], 'dis_link': baglanti_incele(s, kok)['dis'],
                              'og_image': m1(s, 'og:image')} for ad, s in S.items() if acik(s)],
            'sayfa_durumlari': {ad: {'http': s['durum'], 'engel': s['engel'], 'kesildi': s.get('kesildi', False)} for ad, s in S.items()},
            'uyarilar': ([f'Anti-bot sayfası: {", ".join(engelli)}'] if engelli else []) + ([f'Açılmayan: {", ".join(acilmayan)}'] if acilmayan else [])
                        + ([f'Boyut sınırında kesilen sayfalar: {", ".join(kesilen)}'] if kesilen else [])
                        + sm['hatalar'] + ([sm['not']] if not sm['tam'] else []) + feed_hatalari
                        + ([ISTEK_DURUSU] if ISTEK_DURUSU else [])
                        + ['Statik HTML taraması; gerçek indekslenme, Core Web Vitals ve analitik olay gönderimi ölçülmedi.']}


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    yap = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    yapilandirma_dogrula(yap)
    cikti = {'tarih': time.strftime('%Y-%m-%d %H:%M'), 'siteler': []}
    for site in yap['siteler']:
        print(f'taranıyor: {site["ad"]} ({site["kok"]})', file=sys.stderr)
        cikti['siteler'].append(site_tara(site))
    json.dump(cikti, sys.stdout, ensure_ascii=False, indent=1)


def yapilandirma_dogrula(yap):
    siteler = yap.get('siteler') if isinstance(yap, dict) else None
    if not isinstance(siteler, list) or not 1 <= len(siteler) <= 4:
        raise ValueError('Yapılandırmada 1-4 site bulunmalı')
    if sum(bool(s.get('biz')) for s in siteler if isinstance(s, dict)) != 1:
        raise ValueError('Tam bir site biz=true olmalı')
    for site in siteler:
        if not isinstance(site, dict) or not isinstance(site.get('ad'), str) or not site['ad'].strip():
            raise ValueError('Her sitenin adı bulunmalı')
        adresler = [site.get('kok', '')] + list(site.get('sayfalar', {}).values())
        if site.get('alternatif_kok'):
            adresler.append(site['alternatif_kok'])
        if site.get('feed'):
            adresler.append(site['feed'])
        for adres in adresler:
            if not isinstance(adres, str):
                raise ValueError('Adresler metin olmalı')
            if adres and urllib.parse.urlparse(adres).scheme not in ('', 'http', 'https'):
                raise ValueError('Yalnız HTTP/HTTPS adresleri kullanılabilir')
        kok = urllib.parse.urlparse(site['kok'])
        if kok.scheme not in ('http', 'https') or not kok.hostname or kok.username or kok.password:
            raise ValueError('Kök adres geçerli ve kimlik bilgisi içermeyen HTTP/HTTPS adresi olmalı')
        if site.get('alternatif_kok'):
            alternatif = urllib.parse.urlparse(site['alternatif_kok'])
            if alternatif.scheme not in ('http', 'https') or not alternatif.hostname or alternatif.username or alternatif.password:
                raise ValueError('alternatif_kok mutlak HTTP/HTTPS adresi olmalı')
            if alternatif.hostname.removeprefix('www.') != kok.hostname.removeprefix('www.'):
                raise ValueError('alternatif_kok aynı sitenin www/non-www varyantı olmalı')
        sinir = site.get('sitemap_siniri', 100)
        if isinstance(sinir, bool) or not isinstance(sinir, int) or not 1 <= sinir <= 1000:
            raise ValueError('sitemap_siniri 1-1000 arasında tam sayı olmalı')
        if site.get('profil', 'belirsiz') not in ('belirsiz', 'kurumsal', 'eticaret'):
            raise ValueError('Profil kurumsal, eticaret veya belirsiz olmalı')
        uygulanamaz = site.get('uygulanamaz', {})
        if not isinstance(uygulanamaz, dict) or any(not isinstance(k, str) or not isinstance(v, str) or not v.strip() for k, v in uygulanamaz.items()):
            raise ValueError('uygulanamaz alanı {kimlik: gerekçe} sözlüğü olmalı')


if __name__ == '__main__':
    main()
