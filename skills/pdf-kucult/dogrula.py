"""Sıkıştırılmış PDF'i orijinaliyle sayfa sayfa karşılaştırır.

Kullanım: uv run --quiet --with pymupdf python dogrula.py <orijinal> <sikistirilmis> [yakin_plan_cikti_klasoru]
"""
import sys

import pymupdf


def main():
    orj = pymupdf.open(sys.argv[1])
    yeni = pymupdf.open(sys.argv[2])
    cikti = sys.argv[3] if len(sys.argv) > 3 else "."

    if len(orj) != len(yeni):
        print(f"UYARI: sayfa sayisi farkli {len(orj)} -> {len(yeni)}")

    en_kotu = 0.0
    for i in range(min(len(orj), len(yeni))):
        a = orj[i].get_pixmap(dpi=40)
        b = yeni[i].get_pixmap(dpi=40)
        if len(a.samples) != len(b.samples):
            print(f"sayfa {i+1}: boyut uyusmuyor, gozle kontrol et")
            continue
        fark = sum(abs(x - y) for x, y in zip(a.samples, b.samples)) / len(a.samples)
        en_kotu = max(en_kotu, fark)
        print(f"sayfa {i+1}: ort. piksel farki {fark:.2f}/255")

    # Ilk sayfanin ust-orta bolgesinden yakin plan: kucuk punto okunabilirlik kontrolu
    r = orj[0].rect
    kirp = pymupdf.Rect(
        r.x0 + r.width * 0.10,
        r.y0 + r.height * 0.18,
        r.x0 + r.width * 0.62,
        r.y0 + r.height * 0.30,
    )
    yeni[0].get_pixmap(dpi=300, clip=kirp).save(f"{cikti}/yakin_plan.png")
    print(f"\nen kotu fark: {en_kotu:.2f}/255")
    print(f"yakin plan: {cikti}/yakin_plan.png  <- Read ile bak, metin net mi?")


if __name__ == "__main__":
    main()
