#!/usr/bin/env bash
# Tek site ölçümü; ana tarayıcıyla aynı kurallar, yalnız GET.
# Kullanım: BOT_KONTROL=0 canli-kontrol.sh <alan-adi> [urun-url | tur=yol ...]
set -eu
if [ "$#" -lt 1 ]; then
  echo "Kullanım: $0 <alan-adi> [urun-url | tur=yol ...]" >&2
  exit 1
fi
python3 -I - "$@" "$(dirname "$0")" <<'PY'
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
kok = sys.argv[1].strip().rstrip('/')
if not kok.startswith(('http://', 'https://')):
    kok = 'https://' + kok
spec = importlib.util.spec_from_file_location('seo_tarama', Path(sys.argv[-1]).resolve() / 'seo-tara.py')
modul = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modul)
site = {'ad': 'İncelenen site', 'biz': True, 'kok': kok, 'sayfalar': {'anasayfa': '/'},
        'bot_kontrol': os.environ.get('BOT_KONTROL', '0') == '1'}
gecerli_turler = {'anasayfa', 'urun', 'kategori', 'kategori_sayfa2', 'blog', 'hizmet'}
for arg in sys.argv[2:-1]:
    if '=' in arg and arg.split('=', 1)[0] in gecerli_turler:
        tur, yol = arg.split('=', 1)
        site['sayfalar'][tur] = yol
    else:
        site['sayfalar']['urun'] = arg
modul.yapilandirma_dogrula({'siteler': [site]})
sonuc = modul.site_tara(site)
json.dump({'tarih': time.strftime('%Y-%m-%d %H:%M'), 'siteler': [sonuc]}, sys.stdout, ensure_ascii=False, indent=2)
PY
