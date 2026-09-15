"""Fetch paginat de /stats/hits de GoatCounter.

Sense paginació, l'endpoint només retorna el top-N paths del període i
les visites de la cua (pex. un post vist un cop avui) queden fora de
hits_by_day — el dashboard mostraria dies buits.

Pagina amb exclude_paths (path_id, separats per comes) fins que la
resposta digui more=false. Escriu /tmp/hits.json amb el mateix shape
que la resposta original: {"hits": [...]}.

Variables d'entorn: GC_BASE, GC_TOKEN, GC_START, GC_END.
"""
import json
import os
import sys
import time
import urllib.request

MAX_PAGES = 20


def fetch(url, token):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def main():
    base = os.environ["GC_BASE"]
    token = os.environ["GC_TOKEN"]
    start = os.environ["GC_START"]
    end = os.environ["GC_END"]

    all_hits = []
    exclude = []
    pages = 0

    while True:
        pages += 1
        url = "%s?start=%s&end=%s&limit=100" % (base, start, end)
        if exclude:
            url += "&exclude_paths=" + ",".join(str(i) for i in exclude)
        data = fetch(url, token)
        hits = data.get("hits") or []
        all_hits.extend(hits)
        exclude.extend(h["path_id"] for h in hits if "path_id" in h)
        if not data.get("more") or not hits or pages >= MAX_PAGES:
            break
        time.sleep(0.3)  # rate limit de l'API: 4 req/s

    with open("/tmp/hits.json", "w") as f:
        json.dump({"hits": all_hits, "more": False}, f)

    print("paginacio: %d pagines, %d paths" % (pages, len(all_hits)))


if __name__ == "__main__":
    main()
