#!/bin/bash
# Kullanım: paylas.sh <dosya>...  Gerekirse AirDrop aracını derler, paylaşım penceresini açar.
set -euo pipefail
KOK="$(cd "$(dirname "$0")" && pwd)"
ARAC="$KOK/bin/airdrop"
if [ ! -x "$ARAC" ] || [ "$KOK/airdrop.swift" -nt "$ARAC" ]; then
  mkdir -p "$KOK/bin"
  swiftc -O "$KOK/airdrop.swift" -o "$ARAC"
fi
exec "$ARAC" "$@"
