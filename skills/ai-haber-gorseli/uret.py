#!/usr/bin/env python3
"""AI haber kartı: icerik.json -> 1080x1920 PNG.

Kullanım: python3 uret.py icerik.json cikti.png
Ara dosyalar (html, chrome profili) json'un klasörüne yazılır.
"""

import html
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
RENKLER = {
    "sari": ("#f2c230", "#1a1405"),
    "mavi": ("#7aa7ff", "#0a1430"),
    "yesil": ("#3ddc84", "#04170c"),
    "mor": ("#b48cff", "#170a2e"),
    "kirmizi": ("#ff6b6b", "#2a0606"),
    "turuncu": ("#ff9f43", "#2a1302"),
}
# Instagram/TikTok hikâye arayüzü üstte profil, altta yanıt çubuğu gösterir.
GUVENLI_ALAN = (170, 120)
TAM_ALAN = (104, 84)


def hata(mesaj: str) -> None:
    sys.exit(f"HATA: {mesaj}")


def satir_ici(metin: str, baslik: bool = False) -> str:
    """`kod`, **kalın** ve yalnızca başlıkta [vurgu] işaretlerini HTML'e çevirir."""
    m = html.escape(str(metin), quote=False)
    m = re.sub(r"`([^`]+)`", r"<code>\1</code>", m)
    m = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", m)
    if baslik:
        m = re.sub(r"\[([^\]]+)\]", r'<span class="vurgu">\1</span>', m)
    return m.replace("\n", "<br>")


def kart_basligi(blok: dict) -> str:
    return f"<h2>{satir_ici(blok['baslik'])}</h2>" if blok.get("baslik") else ""


def terminal(blok: dict) -> str:
    satirlar = []
    for satir in html.escape(blok.get("komut", ""), quote=False).split("\n"):
        if satir.startswith("#"):
            satir = f'<span class="yorum">{satir}</span>'
        elif satir.startswith("$ "):
            satir = '<span class="p">$</span> ' + satir[2:]
        satirlar.append(satir)
    cikti = "".join(f"<span>{html.escape(c, quote=False)}</span>" for c in blok.get("cikti", []))
    cikti_html = f'<div class="cikti">{cikti}</div>' if cikti else ""
    return (
        '<div class="terminal"><div class="terminal-bas">'
        '<i class="nokta" style="background:#ff5f57"></i>'
        '<i class="nokta" style="background:#febc2e"></i>'
        '<i class="nokta" style="background:#28c840"></i>'
        f'<span>{html.escape(blok.get("baslik", "Terminal"), quote=False)}</span></div>'
        f'<div class="terminal-govde"><div class="komut">{chr(10).join(satirlar)}</div>{cikti_html}</div></div>'
    )


def ciplar(blok: dict) -> str:
    ogeler = []
    for oge in blok["ogeler"]:
        vurgulu = oge.startswith("*")
        sinif = "cip cip--vurgu" if vurgulu else "cip"
        ogeler.append(f'<span class="{sinif}">{html.escape(oge.lstrip("*"), quote=False)}</span>')
    return f'<div class="kart">{kart_basligi(blok)}<div class="ciplar">{"".join(ogeler)}</div></div>'


def bilgi(blok: dict) -> str:
    return f'<div class="kart">{kart_basligi(blok)}<p>{satir_ici(blok["metin"])}</p></div>'


def rakamlar(blok: dict) -> str:
    ogeler = blok["ogeler"]
    sutun = min(len(ogeler), 3)
    hucreler = "".join(
        f'<div class="rakam"><strong>{html.escape(o["deger"], quote=False)}</strong>'
        f'<span>{satir_ici(o["etiket"])}</span></div>'
        for o in ogeler
    )
    return f'<div class="kart">{kart_basligi(blok)}<div class="rakamlar" style="--sutun:{sutun}">{hucreler}</div></div>'


def liste(blok: dict) -> str:
    maddeler = "".join(f"<li>{satir_ici(m)}</li>" for m in blok["ogeler"])
    return f'<div class="kart">{kart_basligi(blok)}<ul class="liste">{maddeler}</ul></div>'


def alinti(blok: dict) -> str:
    kim = f"<cite>{html.escape(blok['kim'], quote=False)}</cite>" if blok.get("kim") else ""
    return f'<div class="kart alinti"><p>{satir_ici(blok["metin"])}</p>{kim}</div>'


def gorsel(blok: dict) -> str:
    yol = Path(blok["yol"]).expanduser().resolve()
    if not yol.is_file():
        hata(f"görsel bulunamadı: {yol}")
    aciklama = f"<figcaption>{satir_ici(blok['aciklama'])}</figcaption>" if blok.get("aciklama") else ""
    return f'<figure class="kart gorsel"><img src="{yol.as_uri()}" alt="">{aciklama}</figure>'


BLOKLAR = {
    "terminal": terminal,
    "ciplar": ciplar,
    "bilgi": bilgi,
    "rakamlar": rakamlar,
    "liste": liste,
    "alinti": alinti,
    "gorsel": gorsel,
}


def html_kur(veri: dict) -> str:
    if not veri.get("baslik"):
        hata("'baslik' zorunlu")
    vurgu, vurgu_koyu = RENKLER.get(veri.get("renk", "sari"), RENKLER["sari"])
    ust, alt_bosluk = GUVENLI_ALAN if veri.get("guvenli_alan", True) else TAM_ALAN

    parcalar = []
    if veri.get("rozet") or veri.get("ust_bilgi"):
        rozet = f'<span class="rozet">{html.escape(veri["rozet"], quote=False)}</span>' if veri.get("rozet") else ""
        ust_bilgi = (
            f'<span class="ust-bilgi">{html.escape(veri["ust_bilgi"], quote=False)}</span>'
            if veri.get("ust_bilgi") else ""
        )
        parcalar.append(f'<div class="ust">{rozet}{ust_bilgi}</div>')
    parcalar.append(f"<h1>{satir_ici(veri['baslik'], baslik=True)}</h1>")
    if veri.get("alt"):
        parcalar.append(f'<p class="alt">{satir_ici(veri["alt"])}</p>')
    for blok in veri.get("bloklar", []):
        tur = blok.get("tur")
        if tur not in BLOKLAR:
            hata(f"bilinmeyen blok türü: {tur!r} (geçerli: {', '.join(BLOKLAR)})")
        parcalar.append(BLOKLAR[tur](blok))

    alt_satirlar = [satir_ici(s) for s in (veri.get("alt_bilgi"), veri.get("kaynak")) if s]
    alt_bilgi = (
        '<div class="alt-bilgi">' + "".join(f"<span>{s}</span>" for s in alt_satirlar) + "</div>"
        if alt_satirlar else ""
    )

    sablon = (KOK / "sablon.html").read_text(encoding="utf-8")
    return (
        sablon.replace("{{VURGU}}", vurgu)
        .replace("{{VURGU_KOYU}}", vurgu_koyu)
        .replace("{{UST_BOSLUK}}", str(ust))
        .replace("{{ALT_BOSLUK}}", str(alt_bosluk))
        .replace("{{ICERIK}}", "\n".join(parcalar))
        .replace("{{ALT_BILGI}}", alt_bilgi)
    )


def chrome(profil: Path, *argumanlar: str) -> subprocess.CompletedProcess:
    if not Path(CHROME).exists():
        hata(f"Chrome bulunamadı: {CHROME} (CHROME ortam değişkeniyle ver)")
    return subprocess.run(
        [
            CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=1", "--window-size=1080,1920",
            "--allow-file-access-from-files", "--virtual-time-budget=3000",
            f"--user-data-dir={profil}", *argumanlar,
        ],
        capture_output=True, text=True, timeout=120,
    )


def png_boyutu(yol: Path) -> tuple[int, int]:
    with yol.open("rb") as f:
        f.seek(16)
        return struct.unpack(">II", f.read(8))


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("Kullanım: python3 uret.py icerik.json cikti.png")
    json_yolu = Path(sys.argv[1]).expanduser().resolve()
    png_yolu = Path(sys.argv[2]).expanduser().resolve()
    veri = json.loads(json_yolu.read_text(encoding="utf-8"))

    html_yolu = json_yolu.with_suffix(".html")
    html_yolu.write_text(html_kur(veri), encoding="utf-8")
    profil = json_yolu.parent / ".chrome-profil"
    png_yolu.parent.mkdir(parents=True, exist_ok=True)
    if png_yolu.exists():
        png_yolu.unlink()

    chrome(profil, f"--screenshot={png_yolu}", html_yolu.as_uri())
    if not png_yolu.exists():
        hata("Chrome ekran görüntüsü üretmedi")
    dom = chrome(profil, "--dump-dom", html_yolu.as_uri()).stdout
    olcek = re.search(r'data-olcek="([\d.]+)"', dom)
    tasma = re.search(r'data-tasma="(\w+)"', dom)

    print(json.dumps({
        "png": str(png_yolu),
        "html": str(html_yolu),
        "boyut": "x".join(map(str, png_boyutu(png_yolu))),
        "olcek": float(olcek.group(1)) if olcek else None,
        "tasma": tasma.group(1) if tasma else "olculemedi",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
