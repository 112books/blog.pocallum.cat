#!/usr/bin/env python3
"""
Genera el text alternatiu (alt) de les imatges dels posts que no en tenen.

Llegeix els fitxers Markdown de content/posts/, troba les imatges amb alt buit
(![](url)) i demana una descripció curta a un model de visió compatible amb
l'API d'OpenAI (OpenAI, DeepSeek, OpenRouter, Gemini en mode compatible,
Ollama local…).

DeepSeek: l'API accepta imatges (content parts image_url, base64 o URL) i el
model 'deepseek-flash' ja és multimodal. Exemple:
  OPENAI_BASE_URL=https://api.deepseek.com OPENAI_API_KEY=... \
  ALT_MODEL=deepseek-flash python3 scripts/genera-alts.py --limit 20 --backup

Característiques:
  · Només toca les imatges amb alt buit → es pot tornar a executar sense por.
  · Les imatges grans es redueixen a --max-px abans d'enviar-les (menys tokens).
  · Resol les rutes /media/ al disc (static/media) i baixa les remotes.
  · --dry-run llista què faria sense cridar cap API.

Ús:
  OPENAI_API_KEY=sk-... python3 scripts/genera-alts.py --limit 20
  python3 scripts/genera-alts.py --dry-run
  python3 scripts/genera-alts.py --posts "content/posts/2026-10-*" --limit 10

Variables d'entorn:
  OPENAI_API_KEY   clau (obligatòria si no es passa --api-key)
  OPENAI_BASE_URL  per defecte https://api.openai.com/v1
                   (DeepSeek: https://api.deepseek.com)
  ALT_MODEL        per defecte gpt-4o-mini
                   (DeepSeek: deepseek-flash)
"""

import argparse
import base64
import glob
import io
import json
import os
import re
import sys
import time
import urllib.parse

import requests
from PIL import Image

SITE = "https://blog.pocallum.cat"
IMG_RE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(\s+"[^"]*")?\)')

PROMPT = (
    "Ets un fotògraf que escriu el text alternatiu (alt) de les imatges del seu blog de "
    "crònica cultural a Barcelona. Descriu la imatge en una sola frase, en català, de com a "
    "màxim 120 caràcters, útil per a una persona que no la pot veure: qui hi surt o què s'hi "
    "veu, l'acció i el lloc. No comencis amb «imatge de» ni «fotografia de». No facis servir "
    "cometes ni claudàtors. Si hi ha text a la imatge, no el copiïs."
)


def imatge_local(url):
    """Retorna el camí al disc per a les imatges del repo (/media/...)."""
    if not url.startswith("/media/"):
        return None
    cami = url.split("?")[0]
    cami = urllib.parse.unquote(cami)          # %20 -> espai
    return os.path.join("static", cami.lstrip("/"))


def baixa(url, cache):
    """Baixa una imatge remota (cachejada a disc). Retorna bytes o None."""
    os.makedirs(cache, exist_ok=True)
    nom = re.sub(r"[^A-Za-z0-9._-]", "_", url)[-120:]
    cami = os.path.join(cache, nom)
    if os.path.isfile(cami) and os.path.getsize(cami) > 0:
        with open(cami, "rb") as f:
            return f.read()
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "blog-pocallum-alts/1.0"})
        if r.status_code == 200 and r.content:
            with open(cami, "wb") as f:
                f.write(r.content)
            return r.content
    except requests.RequestException:
        pass
    return None


def redueix(dades, max_px):
    """Redimensiona a max_px i retorna (data-uri base64, amplada, alçada)."""
    img = Image.open(io.BytesIO(dades))
    img = img.convert("RGB")
    img.thumbnail((max_px, max_px), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}", img.width, img.height


def neteja_alt(txt):
    """Deixa el text en una sola línia, sense caràcters que trenquin el Markdown."""
    txt = re.sub(r"\s+", " ", (txt or "")).strip()
    txt = txt.replace("[", "").replace("]", "")
    txt = txt.strip(' "\'«»')
    return txt[:160]


def descriu(base_url, api_key, model, data_uri, fallback=""):
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "max_tokens": int(os.environ.get("ALT_MAX_TOKENS", "2000")),
        "temperature": 0.2,
        "reasoning_effort": os.environ.get("ALT_EFFORT", "low"),
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ],
        }],
    }
    r = requests.post(url, json=payload, timeout=60,
                      headers={"Authorization": f"Bearer {api_key}"})
    if r.status_code != 200:
        raise RuntimeError(f"API {r.status_code}: {r.text[:200]}")
    d = r.json()
    msgs = d.get("choices") or []
    if not msgs:
        raise RuntimeError(f"resposta sense choices: {json.dumps(d)[:200]}")
    msg = msgs[0].get("message", {})
    contingut = msg.get("content", "")
    if isinstance(contingut, list):
        contingut = " ".join(p.get("text", "") for p in contingut if isinstance(p, dict))
    contingut = (contingut or "").strip()
    if not contingut:
        rc = msg.get("reasoning_content", "") or ""
        # extreu la darrera frase entre cometes del raonament (filtrant fragments)
        cometes = [c for c in re.findall(r'"([^"]{15,160})"', rc)
                   if not any(w in c.lower() for w in ["caràcter", "comptatge", "esborrany", "decisió", "**", "solidaritat"])]
        if cometes:
            contingut = cometes[-1]
        else:
            for linia in reversed(rc.splitlines()):
                linia = linia.strip().strip("*").strip()
                if (len(linia) >= 15 and linia.endswith(".") and linia and linia[0].isupper()
                        and "**" not in linia and "caràcter" not in linia.lower()
                        and "comptatge" not in linia.lower()):
                    contingut = linia
                    break
    if not contingut and fallback:
        contingut = fallback
    return neteja_alt(contingut)


def processa_fitxer(cami, args, cache, comptador):
    with open(cami, encoding="utf-8") as f:
        text = f.read()

    # titol net per a fallback
    mtitle = re.search(r'^title:\s*"?(.+?)"?\s*$', text, re.M)
    titol_raw = mtitle.group(1).strip() if mtitle else ""
    titol_net = re.sub(r"^\d{4}-\d{2}-\d{2}\s*[-–]\s*", "", titol_raw).strip()
    titol_net = titol_net[:120]

    peces, ultim, modificat = [], 0, 0
    for m in IMG_RE.finditer(text):
        alt, url = m.group(1), m.group(2)
        peces.append(text[ultim:m.start()])
        ultim = m.end()

        if alt.strip():                       # ja té alt → no es toca
            peces.append(m.group(0))
            continue

        local = imatge_local(url)
        font = local if (local and os.path.isfile(local)) else (url if url.startswith("http") else None)
        if not font:
            peces.append(m.group(0))
            continue

        if args.dry_run:
            comptador["trobades"] += 1
            if args.verbose:
                print(f"  [dry] {os.path.basename(cami)}: {url}")
            peces.append(m.group(0))
            continue

        try:
            dades = open(font, "rb").read() if local and os.path.isfile(local) else baixa(font, cache)
            if not dades:
                raise RuntimeError("no s'ha pogut llegir la imatge")
            data_uri, _, _ = redueix(dades, args.max_px)
            alt_nou = descriu(args.base_url, args.api_key, args.model, data_uri, fallback=titol_net)
            if not alt_nou:
                raise RuntimeError("alt buit")
        except Exception as e:                # no aturem tot el lot per una imatge
            comptador["errors"] += 1
            print(f"  ! {os.path.basename(cami)} {url}: {e}", file=sys.stderr)
            peces.append(m.group(0))
            continue

        peces.append(f"![{alt_nou}]({url})")
        comptador["fetes"] += 1
        modificat += 1
        print(f"  {os.path.basename(cami)}: {alt_nou}")

    peces.append(text[ultim:])
    nou = "".join(peces)

    if modificat:
        if args.backup:
            with open(cami + ".bak", "w", encoding="utf-8") as f:
                f.write(text)
        with open(cami, "w", encoding="utf-8") as f:
            f.write(nou)
    return modificat


def main():
    ap = argparse.ArgumentParser(description="Genera alts amb un model de visió.")
    ap.add_argument("--posts", default="content/posts/*.md", help="glob de fitxers")
    ap.add_argument("--limit", type=int, default=0, help="màxim d'imatges (0 = sense límit)")
    ap.add_argument("--model", default=os.environ.get("ALT_MODEL", "gpt-4o-mini"))
    ap.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""))
    ap.add_argument("--max-px", type=int, default=512, help="mida màxima abans d'enviar")
    ap.add_argument("--dry-run", action="store_true", help="llista què faria, sense API")
    ap.add_argument("--backup", action="store_true", help="deixa una còpia .bak de cada fitxer tocat")
    ap.add_argument("--cache", default="/tmp/alts-cache", help="carpeta de cau per a imatges remotes")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if not args.dry_run and not args.api_key:
        print("Falta la clau: exporta OPENAI_API_KEY o passa --api-key.", file=sys.stderr)
        return 2

    fitxers = sorted(glob.glob(args.posts))
    if not fitxers:
        print(f"Cap fitxer amb el patró {args.posts}", file=sys.stderr)
        return 1

    comptador = {"fetes": 0, "errors": 0, "trobades": 0}
    tocats = 0
    for cami in fitxers:
        if args.limit and (comptador["fetes"] + comptador["trobades"]) >= args.limit:
            break
        if processa_fitxer(cami, args, args.cache, comptador):
            tocats += 1

    if args.dry_run:
        print(f"\n[dry-run] imatges sense alt: {comptador['trobades']} en {len(fitxers)} fitxers")
        print("Cost estimat amb un model econòmic: uns cèntims per cada 100 imatges.")
    else:
        print(f"\nAlts generats: {comptador['fetes']} · errors: {comptador['errors']} · "
              f"fitxers modificats: {tocats}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
