#!/bin/bash
# Kullanım: ./ikon-uret.sh kaynak.png [hedef-klasor]
# 16/48/128 px ikonları üretir. sips macOS'ta hazır gelir, kurulum gerekmez.
set -e
kaynak="$1"
hedef="${2:-.}"
[ -f "$kaynak" ] || { echo "kaynak dosya yok: $kaynak"; exit 1; }
for b in 16 48 128; do
  sips -z $b $b "$kaynak" --out "$hedef/ikon$b.png" >/dev/null
  echo "ikon$b.png"
done
