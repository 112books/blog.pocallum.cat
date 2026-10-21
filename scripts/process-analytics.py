import json, sys, os, re
from datetime import datetime, timezone, timedelta

# Finestres temporals (dies) que el dashboard pot triar a les pestanyes
# Posts i Pàgines. Han de coincidir amb CFG.listPeriods de static/stats/index.html.
WINDOWS = (7, 30, 90, 365)

def safe_get(data, key, default=None):
    if data is None:
        return default
    return data.get(key, default)

def is_post_path(path):
    return bool(re.match(r'^/\d{4}/\d{2}/\d{2}/', path))

def extract_section(path):
    if not path or path == '/':
        return 'inici'
    if is_post_path(path):
        return 'posts'
    parts = [p for p in path.strip('/').split('/') if p]
    return parts[0] if parts else 'inici'

def norm_items(items):
    out = []
    for item in items:
        name = (item.get("name") or item.get("browser") or item.get("system") or
                item.get("size") or item.get("location") or item.get("id") or "Desconegut")
        count = item.get("count", 0)
        if not count:
            count = sum(
                s.get("daily", 0) or s.get("count", 0)
                for s in item.get("stats", [])
            ) or item.get("total", 0)
        if count > 0:
            out.append({"name": name, "id": item.get("id", name), "count": count})
    return sorted(out, key=lambda x: x["count"], reverse=True)

def main():
    if len(sys.argv) < 5:
        print("Us: process-analytics.py <input.json> <output.json> <start> <end>")
        sys.exit(1)

    input_file  = sys.argv[1]
    output_file = sys.argv[2]
    start_date  = sys.argv[3]
    end_date    = sys.argv[4]

    try:
        with open(input_file) as f:
            raw = json.loads(f.read().strip())
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    hits_data = safe_get(raw, "hits_data") or {}
    hits_list = safe_get(hits_data, "hits") or []

    # Guard: si /stats/hits ha fallat (resposta null o buida) no sobreescriguis
    # un analytics.json que ja tenia pagines; evita perdre el detall per un error
    # transitori de l'API.
    if not hits_list and os.path.exists(output_file):
        try:
            with open(output_file) as f:
                previous = json.load(f)
            if previous.get("hits"):
                print("WARN: /stats/hits buit; es conserva l'analytics.json existent")
                return
        except (json.JSONDecodeError, OSError):
            pass

    by_section  = {}
    total       = 0
    hits_by_day = {}
    hits_pages  = {}
    path_days   = {}   # path -> {dia: visites} (per recalcular rànquings per període)
    pages_daily    = {}   # path -> {dia: visites} (filtre dia/setmana/mes/trimestre/any)
    sections_daily = {}   # secció -> {dia: visites}

    for path_item in hits_list:
        path     = path_item.get("path", "")
        is_event = path_item.get("event", False)
        if is_event:
            continue

        section = extract_section(path)
        days    = path_days.setdefault(path, {})

        for stat in path_item.get("stats", []):
            date  = (stat.get("day") or "")[:10]
            count = stat.get("daily", 0)
            if not count:
                continue
            total += count
            days[date] = days.get(date, 0) + count
            by_section[section] = by_section.get(section, 0) + count
            if date:
                hits_by_day[date] = hits_by_day.get(date, 0) + count
                # Desglossament diari per pagina i per seccio: permet filtrar
                # el dashboard per dia/setmana/mes/trimestre/any.
                pages_daily.setdefault(path, {})
                pages_daily[path][date] = pages_daily[path].get(date, 0) + count
                sections_daily.setdefault(section, {})
                sections_daily[section][date] = sections_daily[section].get(date, 0) + count

        if not days:
            path_days.pop(path, None)

    hits_by_day_list = [{"date": k, "count": v} for k, v in sorted(hits_by_day.items())]
    hits_top = sorted(
        [{"path": k, "count": sum(v.values())} for k, v in path_days.items()],
        key=lambda x: x["count"], reverse=True
    )[:50]

    # Agregats per finestra: el dashboard deixa triar 7/30/90/365 dies a les
    # pestanyes Posts i Pàgines. Abans només hi havia el total de la finestra
    # de consulta (365 dies), així que els llistats no podien seguir el període.
    # Es guarden TOTES les rutes (no només el top 50): així el rànquing de posts
    # no queda limitat pel top-50 global de pàgines.
    try:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        end_dt = datetime.now(timezone.utc).date()
    cutoffs = {w: (end_dt - timedelta(days=w)).isoformat() for w in WINDOWS}

    hits_windows = []
    for path, days in path_days.items():
        row = {"path": path}
        for w in WINDOWS:
            row[f"d{w}"] = sum(c for day, c in days.items() if day >= cutoffs[w])
        hits_windows.append(row)
    hits_windows.sort(key=lambda r: r.get("d365", 0), reverse=True)

    # Top de posts calculat sobre TOTS els posts, no sobre el top-50 de pàgines.
    posts_top = [
        {"path": r["path"], "count": r["d365"]}
        for r in hits_windows if is_post_path(r["path"])
    ][:15]

    def sort_daily(daily_map):
        """Ordena per total desc i, dins de cada clau, les dates ascendentment."""
        return {
            key: dict(sorted(series.items()))
            for key, series in sorted(
                daily_map.items(), key=lambda kv: sum(kv[1].values()), reverse=True
            )
        }

    total_data   = safe_get(raw, "total_data") or {}
    total_unique = safe_get(total_data, "total_unique") or 0

    browsers_raw  = safe_get(safe_get(raw, "browsers")  or {}, "stats") or []
    systems_raw   = safe_get(safe_get(raw, "systems")   or {}, "stats") or []
    sizes_raw     = safe_get(safe_get(raw, "sizes")     or {}, "stats") or []
    locations_raw = safe_get(safe_get(raw, "locations") or {}, "stats") or []
    refs_raw      = safe_get(safe_get(raw, "refs")      or {}, "stats") or []

    output = {
        "generated":    datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "period":       {"start": start_date, "end": end_date},
        "total":        total,
        "total_unique": total_unique,
        "hits_by_day":  hits_by_day_list,
        "hits":         hits_top,
        "hits_windows": hits_windows,
        "by_section":   by_section,
        "pages_daily":    sort_daily(pages_daily),
        "sections_daily": sort_daily(sections_daily),
        "posts_top":    posts_top,
        "browsers":     norm_items(browsers_raw),
        "systems":      norm_items(systems_raw),
        "sizes":        norm_items(sizes_raw),
        "locations":    norm_items(locations_raw),
        "refs":         norm_items(refs_raw),
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Analytics processats: {total} visites, {len(hits_by_day_list)} dies, "
          f"{len(hits_windows)} rutes, {len(posts_top)} posts top, "
          f"{len(pages_daily)} pagines i {len(sections_daily)} seccions amb detall diari")

if __name__ == "__main__":
    main()
