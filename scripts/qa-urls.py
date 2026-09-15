#!/usr/bin/env python3
"""
QA d'URLs: comprova que cada post del Hugo tingui el 200 equivalent al WordPress.
Genera un informe de discrepàncies.

Ús:
  python3 scripts/qa-urls.py --wp https://blog.pocallum.cat --hugo https://112books.github.io/blog.pocallum.cat
  python3 scripts/qa-urls.py --wp https://blog.pocallum.cat --hugo http://localhost:1313
  python3 scripts/qa-urls.py --wp https://blog.pocallum.cat --hugo https://blog.pocallum.cat --prod

Flags:
  --wp     Base URL del WordPress actual
  --hugo   Base URL del Hugo (staging o local)
  --prod   Mode producció: compara WP vs Hugo al mateix domini
  --limit  Limita el nombre de posts a comprovar (per a proves ràpides)
  --out    Fitxer de sortida (default: qa-report.md)
  --workers Connexions paral·leles (default: 10)
"""

import argparse
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, quote
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

FIXED_PAGES = [
    "/about/",
    "/contact/",
    "/cerca/",
    "/aviso-legal/",
    "/politica-de-privacidad/",
    "/politica-de-cookies/",
    "/feed.xml",
]

def parse_posts(content_dir):
    """Llegeix els posts de content/posts/ i retorna llista de paths URL."""
    paths = []
    for fname in sorted(os.listdir(content_dir)):
        if not fname.endswith(".md"):
            continue
        with open(os.path.join(content_dir, fname)) as f:
            content = f.read()
        date_m = re.search(r"^date:\s*[\"']?(\d{4}-\d{2}-\d{2})", content, re.M)
        slug_m = re.search(r"^slug:\s*[\"']?([^\"'\n]+)", content, re.M)
        if date_m and slug_m:
            d = date_m.group(1)
            s = slug_m.group(1).strip().strip('"\'')
            y, mo, dd = d.split("-")
            paths.append("/%s/%s/%s/%s/" % (y, mo, dd, s))
    return paths


def check_url(url, timeout=10):
    """Retorna (status_code, error_msg). status_code=0 si hi ha error de xarxa."""
    try:
        req = Request(url, headers={"User-Agent": "QA-bot/1.0 blog.pocallum.cat"})
        with urlopen(req, timeout=timeout) as r:
            return r.status, None
    except HTTPError as e:
        return e.code, None
    except URLError as e:
        return 0, str(e.reason)
    except Exception as e:
        return 0, str(e)


def check_pair(path, wp_base, hugo_base):
    """Comprova WP i Hugo per al mateix path. Retorna dict amb resultat."""
    encoded = quote(path, safe="/%")
    wp_url = wp_base.rstrip("/") + encoded
    hugo_url = hugo_base.rstrip("/") + encoded

    wp_status, wp_err = check_url(wp_url)
    hugo_status, hugo_err = check_url(hugo_url)

    ok = wp_status == 200 and hugo_status == 200
    wp_ok = wp_status == 200
    hugo_ok = hugo_status == 200

    return {
        "path": path,
        "wp_status": wp_status,
        "hugo_status": hugo_status,
        "wp_err": wp_err,
        "hugo_err": hugo_err,
        "ok": ok,
        "wp_ok": wp_ok,
        "hugo_ok": hugo_ok,
    }


def main():
    parser = argparse.ArgumentParser(description="QA d'URLs WP vs Hugo")
    parser.add_argument("--wp", default="https://blog.pocallum.cat", help="Base URL WordPress")
    parser.add_argument("--hugo", default="http://localhost:1313", help="Base URL Hugo")
    parser.add_argument("--limit", type=int, default=0, help="Limitar posts (0=tots)")
    parser.add_argument("--out", default="qa-report.md", help="Fitxer de sortida")
    parser.add_argument("--workers", type=int, default=10, help="Workers paral·lels")
    parser.add_argument("--posts-only", action="store_true", help="Només posts, no pàgines fixes")
    args = parser.parse_args()

    content_dir = os.path.join(os.path.dirname(__file__), "..", "content", "posts")
    if not os.path.isdir(content_dir):
        print("ERROR: no trobo content/posts/", file=sys.stderr)
        sys.exit(1)

    print("Llegint posts...", end=" ", flush=True)
    post_paths = parse_posts(content_dir)
    print("%d posts" % len(post_paths))

    if args.limit:
        post_paths = post_paths[: args.limit]
        print("(limitat a %d)" % args.limit)

    paths = post_paths if args.posts_only else post_paths + FIXED_PAGES
    total = len(paths)
    print("Total URLs a comprovar: %d" % total)
    print("WP:   %s" % args.wp)
    print("Hugo: %s" % args.hugo)
    print("")

    results = []
    errors_wp = []
    errors_hugo = []
    errors_both = []
    done = 0
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(check_pair, p, args.wp, args.hugo): p for p in paths}
        for fut in as_completed(futures):
            r = fut.result()
            results.append(r)
            done += 1
            if not r["wp_ok"]:
                errors_wp.append(r)
            if not r["hugo_ok"]:
                errors_hugo.append(r)
            if not r["wp_ok"] and not r["hugo_ok"]:
                errors_both.append(r)
            if done % 100 == 0 or done == total:
                elapsed = time.time() - t0
                rate = done / elapsed if elapsed > 0 else 0
                print("  %d/%d  (%.0f URLs/s)" % (done, total, rate), end="\r", flush=True)

    print("")
    elapsed = time.time() - t0

    ok_count = sum(1 for r in results if r["ok"])
    wp_fail = [r for r in results if not r["wp_ok"]]
    hugo_fail = [r for r in results if not r["hugo_ok"]]

    print("")
    print("═" * 60)
    print("  QA COMPLETAT en %.1fs" % elapsed)
    print("═" * 60)
    print("  Total:          %d" % total)
    print("  OK (WP+Hugo):   %d  (%.1f%%)" % (ok_count, 100 * ok_count / total))
    print("  Errors WP:      %d" % len(wp_fail))
    print("  Errors Hugo:    %d" % len(hugo_fail))
    print("═" * 60)

    if hugo_fail:
        print("")
        print("URLs Hugo amb error (primeres 20):")
        for r in sorted(hugo_fail, key=lambda x: x["path"])[:20]:
            print("  [%s] %s" % (r["hugo_status"] or r["hugo_err"], r["path"]))

    # Escriu informe Markdown
    with open(args.out, "w") as f:
        f.write("# QA URLs — blog.pocallum.cat\n\n")
        f.write("- **Data:** %s\n" % time.strftime("%Y-%m-%d %H:%M"))
        f.write("- **WP:** `%s`\n" % args.wp)
        f.write("- **Hugo:** `%s`\n" % args.hugo)
        f.write("- **Total URLs:** %d\n" % total)
        f.write("- **Temps:** %.1fs\n\n" % elapsed)

        f.write("## Resum\n\n")
        f.write("| Categoria | Nombre | % |\n")
        f.write("|-----------|-------:|---:|\n")
        f.write("| OK (200 a tots dos) | %d | %.1f%% |\n" % (ok_count, 100 * ok_count / total))
        f.write("| Errors Hugo | %d | %.1f%% |\n" % (len(hugo_fail), 100 * len(hugo_fail) / total))
        f.write("| Errors WP | %d | %.1f%% |\n" % (len(wp_fail), 100 * len(wp_fail) / total))
        f.write("\n")

        if hugo_fail:
            f.write("## URLs Hugo amb error\n\n")
            f.write("| Path | WP | Hugo | Nota |\n")
            f.write("|------|---:|----:|------|\n")
            for r in sorted(hugo_fail, key=lambda x: x["path"]):
                nota = r["hugo_err"] or ""
                f.write("| `%s` | %s | %s | %s |\n" % (
                    r["path"], r["wp_status"], r["hugo_status"] or "ERR", nota
                ))
            f.write("\n")

        if wp_fail:
            f.write("## URLs WP amb error (referència)\n\n")
            f.write("| Path | WP | Nota |\n")
            f.write("|------|---:|------|\n")
            for r in sorted(wp_fail, key=lambda x: x["path"])[:50]:
                nota = r["wp_err"] or ""
                f.write("| `%s` | %s | %s |\n" % (r["path"], r["wp_status"] or "ERR", nota))
            if len(wp_fail) > 50:
                f.write("| … | | *%d més no llistats* |\n" % (len(wp_fail) - 50))
            f.write("\n")

    print("")
    print("Informe guardat a: %s" % args.out)

    # Codi de sortida: 1 si hi ha errors Hugo
    sys.exit(1 if hugo_fail else 0)


if __name__ == "__main__":
    main()
