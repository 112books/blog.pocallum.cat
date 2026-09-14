#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
#  Blog Pocallum — Script de deploy i gestió
#  Ús: ./sync-blog.sh
# ═══════════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Variables ────────────────────────────────────────────────────────────
REMOTE="origin"
BUILD_DIR="public"
BRANCH_STAGING="develop"
BRANCH_PROD="main"
REPO_STAGING="https://112books.github.io/blog.pocallum.cat/"
REPO_PROD="https://blog.pocallum.cat/"

# ── Colors i helpers ─────────────────────────────────────────────────────
RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[1;33m'
BLU='\033[0;34m'
DIM='\033[2m'
RST='\033[0m'

print() { echo -e "${BLU}▶${RST} $1"; }
ok()    { echo -e "${GRN}✓${RST} $1"; }
err()   { echo -e "${RED}✗ Error:${RST} $1" >&2; }
warn()  { echo -e "${YLW}⚠${RST}  $1"; }
dim()   { echo -e "${DIM}  $1${RST}"; }

require_clean() {
  if ! git diff --quiet || ! git diff --cached --quiet; then
    err "Hi ha canvis sense confirmar. Fes commit abans de desplegar."
    echo ""
    git status --short
    echo ""
    exit 1
  fi
}

# ── Funcions ──────────────────────────────────────────────────────────────

status() {
  echo ""
  CURRENT=$(git branch --show-current)
  print "Branca actual: ${YLW}${CURRENT}${RST}"
  echo ""
  git status --short
  echo ""
  dim "Últims commits:"
  git log --oneline -5 2>/dev/null || dim "(encara no hi ha commits)"
  echo ""
  dim "Posts: $(find content/posts -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  echo ""
}

sync() {
  CURRENT=$(git branch --show-current)
  print "Sincronitzant amb ${REMOTE}/${CURRENT}..."

  git add -A

  if ! git diff --cached --quiet; then
    read -r -p "  Missatge de commit: " msg
    [[ -z "$msg" ]] && msg="Auto-sync $(date '+%Y-%m-%d %H:%M')"
    git commit -m "$msg"
  fi

  git pull --rebase "$REMOTE" "$CURRENT" || {
    err "Pull/rebase fallat. Resol els conflictes manualment i torna a executar."
    exit 1
  }

  git push "$REMOTE" "$CURRENT" || exit 1
  ok "Sync complet → ${REMOTE}/${CURRENT}"
}

server_local() {
  print "Arrancant servidor local..."
  dim "http://localhost:1313  —  Ctrl+C per aturar"
  echo ""
  hugo server -D
}

build_local() {
  print "Build local (amb drafts)..."
  hugo --minify --buildDrafts || exit 1
  ok "Build correcte → ./${BUILD_DIR}/"
}

deploy_staging() {
  require_clean
  CURRENT=$(git branch --show-current)
  if [[ "$CURRENT" != "$BRANCH_STAGING" ]]; then
    warn "No estàs a '${BRANCH_STAGING}'. Canviant..."
    git checkout "$BRANCH_STAGING"
  fi
  print "Build staging..."
  hugo --minify --baseURL "$REPO_STAGING" --buildDrafts
  ok "Build correcte"
  print "Pujant a GitHub (branca ${BRANCH_STAGING})..."
  git push "$REMOTE" "$BRANCH_STAGING" || exit 1
  ok "Deploy staging iniciat → ${REPO_STAGING}"
  dim "Segueix el progrés: https://github.com/112books/blog.pocallum.cat/actions"
}

deploy_prod_pages() {
  require_clean
  SERVER="pocallum@vl28359.dinaserver.com"
  DOCROOT_VIA="/home/pocallum/www/blog/"

  print "Build de producció (baseURL ${REPO_PROD})..."
  hugo --minify --baseURL "$REPO_PROD" || exit 1
  ok "Build correcte → ./${BUILD_DIR}/"

  print "Pujant a Dinahosting (${SERVER} → ${DOCROOT_VIA})..."
  rsync -az --delete -e "ssh -o BatchMode=yes" \
    --exclude 'wp-content/' \
    --exclude 'wp-admin/' \
    --exclude 'wp-includes/' \
    --exclude 'xmlrpc.php' \
    --exclude '.htaccess' \
    --exclude 'cgi-bin/' \
    "${BUILD_DIR}/" "${SERVER}:${DOCROOT_VIA}" || exit 1
  ok "Deploy producció complet → https://blog.pocallum.cat/"
  dim "Importants: wp-content/ i .htaccess es conserven → les imatges no es toquen."
}

imatges_locals() {
  echo ""
  print "Baixa les imatges del servidor al local/staging"
  echo ""
  SERVER="pocallum@vl28359.dinaserver.com"
  SRC="/home/pocallum/www/blog/wp-content/uploads/"
  DEST="static/uploads/"
  mkdir -p "$DEST"
  dim "Origen:  ${SRC}"
  dim "Destí:   static/uploads/ (gitignored → no puja a GitHub)"
  read -r -p "  Confirmes? [s/N] " confirm
  [[ "$confirm" =~ ^[Ss]$ ]] || { err "Cancel·lat."; exit 1; }
  rsync -az --info=progress2 -e "ssh -o BatchMode=yes" "${SERVER}:${SRC%/}" "$DEST" 2>/dev/null || \
    rsync -az -e "ssh -o BatchMode=yes" "${SERVER}:${SRC%/}" "$DEST"
  ok "Imatges a ${DEST} (rutes relatives /uploads/...)"
  dim "Atenció: els posts del llegat apunten a /wp-content/uploads/... —"
  dim "per al local/staging es mapegen rutes a la fase de tema (veure CLAUDE.md)."
}

nou_post() {
  echo ""
  print "Nou post del blog"
  echo ""

  # Data (els posts porten prefix de data al títol i al slug, com al WordPress)
  TODAY="$(date '+%Y-%m-%d')"
  read -r -p "  Data del post [${TODAY}]: " POST_DATE
  [[ -z "$POST_DATE" ]] && POST_DATE="$TODAY"
  if ! [[ "$POST_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    err "Format de data no vàlid (cal YYYY-MM-DD)."
    exit 1
  fi

  # Slug (sense la data; s'hi afegeix automàticament)
  read -r -p "  Slug (ex: escapada-a-taull): " SLUG
  [[ -z "$SLUG" ]] && { err "Cal indicar el slug."; exit 1; }

  FILENAME="${POST_DATE}-${SLUG}.md"
  TARGET="content/posts/${FILENAME}"
  if [[ -f "$TARGET" ]]; then
    err "Ja existeix: $TARGET"
    exit 1
  fi

  # Títol (part descriptiva; el prefix de data s'hi afegeix sol)
  read -r -p "  Títol (sense la data): " TITLE_PART
  [[ -z "$TITLE_PART" ]] && { err "Cal indicar el títol."; exit 1; }
  POST_TITLE="${POST_DATE} – ${TITLE_PART}"

  # Categories i etiquetes (opcionals, separades per comes)
  read -r -p "  Categories (comes, ex: Nikon FM, General): " CATS_RAW
  read -r -p "  Etiquetes (comes, opcional): " TAGS_RAW

  to_toml_array() {
    local raw="$1" out="" item
    IFS=',' read -ra ITEMS <<< "$raw"
    for item in "${ITEMS[@]}"; do
      item="$(echo "$item" | sed 's/^ *//; s/ *$//')"
      [[ -z "$item" ]] && continue
      [[ -n "$out" ]] && out+=", "
      out+="\"${item}\""
    done
    echo "$out"
  }

  # Zona horària local amb dos punts (+02:00)
  TZ_OFFSET="$(date '+%z' | sed 's/\(..\)$/:\1/')"

  cat > "$TARGET" <<EOF
---
title: "${POST_TITLE}"
date: ${POST_DATE}T$(date '+%H:%M:%S')${TZ_OFFSET}
categories: [$(to_toml_array "$CATS_RAW")]
tags: [$(to_toml_array "$TAGS_RAW")]
draft: true
---

EOF

  echo ""
  ok "Creat: ${TARGET}"
  dim "títol: ${POST_TITLE}"
  dim "URL:   /$(echo "$POST_DATE" | tr '-' '/')/${POST_DATE}-${SLUG}/"
  warn "És un draft — passa'l a 'draft: false' quan estigui llest."
}

# ── Menú ──────────────────────────────────────────────────────────────────

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Blog Pocallum — Deploy & Gestió"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
CURRENT=$(git branch --show-current 2>/dev/null || echo "?")
echo -e " Branca: ${YLW}${CURRENT}${RST}"
echo ""
echo " 1) Status del repo"
echo " 2) Sync  (commit + pull --rebase + push)"
echo " 3) Servidor local  →  localhost:1313"
echo " 4) Build local (amb drafts)"
echo "───────────────────────────────────────"
echo " 5) Deploy staging  →  GitHub Pages (develop, sense imatges)"
echo " 6) Deploy producció → Dinahosting (rsync) — manté wp-content/"
echo "───────────────────────────────────────"
echo " i) Baixa les imatges del servidor (per local/staging)"
echo " p) Nou post"
echo "───────────────────────────────────────"
echo " 0) Sortir"
echo ""

read -r -p "Opció: " opt
echo ""

case $opt in
  1) status ;;
  2) sync ;;
  3) server_local ;;
  4) build_local ;;
  5) deploy_staging ;;
  6) deploy_prod_pages ;;
  i) imatges_locals ;;
  p) nou_post ;;
  0) exit 0 ;;
  *) err "Opció no vàlida: '${opt}'"; exit 1 ;;
esac

echo ""
