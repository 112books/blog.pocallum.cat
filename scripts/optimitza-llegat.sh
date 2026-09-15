#!/usr/bin/env bash
set -euo pipefail
# Optimitza el llegat: genera WebP display (2500px) i thumb (800px)
# per cada imatge, sense tocar els originals.
# Ús: ./scripts/optimitza-llegat.sh [directori]
#     Si no es dona directori, processa tots els anys (2010-2026).

DEST="${1:-/Volumes/1TbExt/Obsidian/hugo-websites/blog.pocallum.cat/migration/llegat-imatges}"
Q=85
LOG="/Volumes/1TbExt/Obsidian/hugo-websites/blog.pocallum.cat/migration/opt-llegat.log"
ERR="/Volumes/1TbExt/Obsidian/hugo-websites/blog.pocallum.cat/migration/opt-llegat.err"

[[ -d "$DEST" ]] || { echo "Error: directori no trobat: $DEST"; exit 1; }

# Nomes redimensiona si l'original es mes gran (evita l'upscale: cwebp
# -resize AMPLIA les imatges petites, ex. miniatures 150x150 → 2500x2500).
processa() {
  local src="$1"
  local base="${src%.*}"
  local w="$base-2500.webp"
  local t="$base-800.webp"
  [[ -f "$src" ]] || return 0
  local W H
  # magick -format no emet newline final: read retorna 1 per EOF tot i llegir
  read -r W H < <(magick identify -format "%w %h" "$src" 2>/dev/null) 2>/dev/null || true
  [[ "$W" =~ ^[0-9]+$ && "$H" =~ ^[0-9]+$ ]] || return 0
  if [[ ! -f "$w" ]]; then
    if (( W > 2500 || H > 2500 )); then
      cwebp -quiet -q $Q -resize 2500 0 "$src" -o "$w" 2>>"$ERR" || { echo "ERR $src" >> "$ERR"; return; }
    else
      cwebp -quiet -q $Q "$src" -o "$w" 2>>"$ERR" || { echo "ERR $src" >> "$ERR"; return; }
    fi
  fi
  # Mini: nomes si supera els 800px; les minis petites ja les cobreix la display
  if [[ ! -f "$t" ]] && (( W > 800 || H > 800 )); then
    cwebp -quiet -q $Q -resize 800 0 "$src" -o "$t" 2>/dev/null || true
  fi
}
export -f processa
export Q
export ERR

find "$DEST" -type d \( -name "burst" -o -name "fbrfg" -o -name "really-simple-ssl" -o -name "sass" -o -name "spotlight-insta" -o -name "wp-*" -o -name "wpcf7_*" -o -name "wpforms" \) -prune -o -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) -print0 \
  | xargs -0 -n 1 -P 4 bash -c 'processa "$0"' >> "$LOG" 2>&1

echo "FET $(date '+%H:%M:%S') $DEST" >> "$LOG"