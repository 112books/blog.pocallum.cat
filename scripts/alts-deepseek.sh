#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Drecera per generar els texts alt amb DeepSeek.
#
#   ./scripts/alts-deepseek.sh --dry-run          # veure abast (no crida l'API)
#   ./scripts/alts-deepseek.sh --limit 20 --backup
#   ./scripts/alts-deepseek.sh --backup           # passada completa
#
# La clau es llegeix, per aquest ordre:
#   1. $OPENAI_API_KEY
#   2. el fitxer $ALT_KEY_FILE (per defecte ~/.config/pocallum/deepseek.key)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ARREL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ARREL"

if [ -z "${OPENAI_API_KEY:-}" ]; then
  FITXER="${ALT_KEY_FILE:-$HOME/.config/pocallum/deepseek.key}"
  if [ -f "$FITXER" ]; then
    OPENAI_API_KEY="$(tr -d '[:space:]' < "$FITXER")"
  fi
fi

if [ -z "${OPENAI_API_KEY:-}" ]; then
  cat >&2 <<'MISSATGE'
Falta la clau de DeepSeek. Fes una d'aquestes:

  a) export OPENAI_API_KEY=sk-…
  b) deixa-la en un fitxer privat:
       mkdir -p ~/.config/pocallum && chmod 700 ~/.config/pocallum
       printf '%s' 'sk-…' > ~/.config/pocallum/deepseek.key
       chmod 600 ~/.config/pocallum/deepseek.key

Llavors torna a executar aquest script.
MISSATGE
  exit 2
fi

export OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://api.deepseek.com}"
export OPENAI_API_KEY
export ALT_MODEL="${ALT_MODEL:-deepseek-flash}"

echo "Model: $ALT_MODEL · endpoint: $OPENAI_BASE_URL"
exec python3 scripts/genera-alts.py "$@"
