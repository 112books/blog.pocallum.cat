import json, sys, os, re
from datetime import datetime, timezone

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

    by_section  = {}
    total       = 0
    hits_by_day = {}
    hits_pages  = {}

    for path_item in hits_list:
        path     = path_item.get("path", "")
        is_event = path_item.get("event", False)
        if is_event:
            continue

        section    = extract_section(path)
        path_total = 0

        for stat in path_item.get("stats", []):
            date  = (stat.get("day") or "")[:10]
            count = stat.get("daily", 0)
            if not count:
                continue
            total      += count
            path_total += count
            by_section[section] = by_section.get(section, 0) + count
            if date:
                hits_by_day[date] = hits_by_day.get(date, 0) + count

        if path_total > 0:
            hits_pages[path] = hits_pages.get(path, 0) + path_total

    hits_by_day_list = [{"date": k, "count": v} for k, v in sorted(hits_by_day.items())]
    hits_top = sorted(
        [{"path": k, "count": v} for k, v in hits_pages.items()],
        key=lambda x: x["count"], reverse=True
    )[:50]

    posts_top = [h for h in hits_top if is_post_path(h['path'])][:15]

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
        "by_section":   by_section,
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

    print(f"Analytics processats: {total} visites, {len(hits_by_day_list)} dies, {len(posts_top)} posts top")

if __name__ == "__main__":
    main()
