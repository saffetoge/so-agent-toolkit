"""PDF içindeki JPEG görselleri çözünürlük değiştirmeden yeniden kodlar.

Kullanım: uv run --quiet --with pikepdf --with pillow python sikistir.py <kaynak> <hedef> <kalite>
"""
import io
import sys

import pikepdf
from PIL import Image


def gorselleri_gez(pdf):
    """PDF'teki tüm XObject görsellerini (Form XObject içindekiler dahil) üret."""
    gorulen = set()

    def gez(kaynaklar):
        xo = kaynaklar.get("/XObject")
        if xo is None:
            return
        for _, obj in xo.items():
            anahtar = obj.objgen
            if anahtar in gorulen:
                continue
            gorulen.add(anahtar)
            alt = obj.get("/Subtype")
            if alt == "/Image":
                yield obj
            elif alt == "/Form" and "/Resources" in obj:
                yield from gez(obj["/Resources"])

    for sayfa in pdf.pages:
        if "/Resources" in sayfa:
            yield from gez(sayfa["/Resources"])


def main():
    kaynak, hedef, kalite = sys.argv[1], sys.argv[2], int(sys.argv[3])
    pdf = pikepdf.open(kaynak)
    degisen = 0
    for obj in gorselleri_gez(pdf):
        # Sadece duz DCTDecode (JPEG) akislari; zincirli filtre veya CMYK atlanir
        if obj.get("/Filter") != "/DCTDecode":
            continue
        ham = obj.read_raw_bytes()
        im = Image.open(io.BytesIO(ham))
        if im.mode not in ("RGB", "L"):
            continue  # CMYK/ayrisik renk uzayi: dokunma, bozulma riski
        tampon = io.BytesIO()
        im.save(tampon, format="JPEG", quality=kalite, optimize=True, progressive=True)
        if tampon.tell() < len(ham):
            obj.write(tampon.getvalue(), filter=pikepdf.Name.DCTDecode)
            degisen += 1
    pdf.save(
        hedef,
        compress_streams=True,
        object_stream_mode=pikepdf.ObjectStreamMode.generate,
    )
    print(f"{degisen} gorsel yeniden kodlandi")


if __name__ == "__main__":
    main()
