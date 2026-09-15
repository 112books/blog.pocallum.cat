#!/usr/bin/env bash
set -euo pipefail

# Optimitza fotos per al blog: genera WebP de visualització (max 2500px,
# qualitat ~85) sense tocar mai l'original (és l'arxiu del fotògraf).
#
# Ús:
#   ./scripts/optimitza-imatges.sh [--force] [--thumb] fitxer.jpg [fitxer2.png ...]
#   ./scripts/optimitza-imatges.sh [--force] --dir ruta/amb/fotos/
#
# Sortida (per cada imatge):
#   fotohas.webp                  WebP display max 2500px
#   fotohas-800.webp              (amb --thumb) WebP mini max 800px
#   fotohas.jpg                   original intacte

QUALITY=85
MAX_WIDTH=2500
THUMB_WIDTH=800
FORCE=0
THUMB=0
TARGET_DIR=""

usage() {
  echo "Ús: $0 [--force] [--thumb] fitxer... | --dir DIR"
  echo "  --force    Regenera encara que el .webp ja existeixi"
  echo "  --thumb    Genera també la versió -800.webp (miniatures)"
  echo "  --dir DIR  Processa tots els jpg/jpeg/png de DIR"
  exit 1
}

cwebp_disponible() { command -v cwebp &>/dev/null; }

optimitza() {
  local src="$1"
  local base="${src%.*}"
  local webp="$base.webp"
  local thumb="$base-800.webp"

  [[ -f "$src" ]] || { echo "  ✗ no trobat: $src"; return; }

  if [[ $FORCE -eq 1 || ! -f "$webp" || "$src" -nt "$webp" ]]; then
    if cwebp_disponible; then
      cwebp -quiet -q "$QUALITY" -resize "$MAX_WIDTH" 0 "$src" -o "$webp"
    else
      magick "$src" -resize "${MAX_WIDTH}x>" -quality "$QUALITY" "$webp"
    fi
    echo "  → $webp"
  else
    echo "  skip $webp"
  fi

  if [[ $THUMB -eq 1 ]]; then
    if [[ $FORCE -eq 1 || ! -f "$thumb" || "$src" -nt "$thumb" ]]; then
      if cwebp_disponible; then
        cwebp -quiet -q "$QUALITY" -resize "$THUMB_WIDTH" 0 "$src" -o "$thumb"
      else
        magick "$src" -resize "${THUMB_WIDTH}x>" -quality "$QUALITY" "$thumb"
      fi
      echo "  → $thumb"
    else
      echo "  skip $thumb"
    fi
  fi
}

[[ $# -gt 0 ]] || usage

for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    --thumb) THUMB=1 ;;
    --dir)   TARGET_DIR="DIR" ;;
    -h|--help) usage ;;
    *) if [[ "$TARGET_DIR" == "DIR" ]]; then
         TARGET_DIR="$arg"
       else
         optimitza "$arg"
       fi ;;
  esac
done

if [[ -n "$TARGET_DIR" && "$TARGET_DIR" != "DIR" ]]; then
  [[ -d "$TARGET_DIR" ]] || { echo "Error: directori no trobat: $TARGET_DIR"; exit 1; }
  echo "Processant: $TARGET_DIR"
  while IFS= read -r f; do
    optimitza "$f"
  done < <(find "$TARGET_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | sort)
fi

echo "Fet."