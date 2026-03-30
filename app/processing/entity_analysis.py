"""
Entity Analysis — computes data for the Entities dashboard page.

Three outputs:
1. Entity profiles per category (timeline, thematic breakdown, source coverage)
2. Entity-Source Coverage Matrix (top N entities × 7 sources)
3. Top Entity Pairs (co-occurring entities in the same document)
"""

from datetime import datetime, timedelta
from collections import Counter, defaultdict
from itertools import combinations

from app.processing.theme_config import THEME_LABELS


SOURCE_DISPLAY_NAMES = {
    "mae": "MAE Romania",
    "nato": "NATO",
    "eu_council": "EU Council",
    "eeas": "EEAS",
    "ecfr": "ECFR",
    "isw": "ISW",
    "chatham_house": "Chatham House",
}

SOURCE_ORDER = ["mae", "nato", "eu_council", "eeas", "ecfr", "isw", "chatham_house"]

CATEGORIES = ["persons", "countries", "organizations", "locations"]

# How many entities to include in coverage matrix per category
COVERAGE_TOP_N = 15

# How many pairs to return
PAIRS_TOP_N = 30


def _iso_week_key(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        iso_year, iso_week, _ = dt.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    except (ValueError, TypeError):
        return None


def _week_label(week_key: str) -> str:
    try:
        parts = week_key.split("-W")
        year = int(parts[0])
        week = int(parts[1])
        monday = datetime.strptime(f"{year}-W{week:02d}-1", "%G-W%V-%u")
        sunday = monday + timedelta(days=6)
        fmt = lambda d: d.strftime("%b %d")
        return f"{fmt(monday)} — {fmt(sunday)}"
    except Exception:
        return week_key


def _get_all_weeks(documents: list[dict]) -> list[str]:
    weeks = set()
    for doc in documents:
        wk = _iso_week_key(doc.get("publication_date_iso", ""))
        if wk:
            weeks.add(wk)
    return sorted(weeks)


def compute_entity_profiles(documents: list[dict], all_weeks: list[str]) -> dict:
    """
    For each category, compute per-entity stats:
    total mentions, weekly timeline, thematic breakdown, source coverage.
    """
    profiles = {cat: {} for cat in CATEGORIES}

    # First pass: collect all entity mentions
    entity_docs = {cat: defaultdict(list) for cat in CATEGORIES}
    for doc in documents:
        entities = doc.get("entities", {})
        for cat in CATEGORIES:
            for entity in entities.get(cat, []):
                entity_docs[cat][entity].append(doc)

    total_docs = len(documents)

    for cat in CATEGORIES:
        for entity, docs in entity_docs[cat].items():
            count = len(docs)
            doc_rate = round((count / total_docs) * 100, 1) if total_docs > 0 else 0

            # Weekly timeline
            week_counter = Counter()
            for doc in docs:
                wk = _iso_week_key(doc.get("publication_date_iso", ""))
                if wk:
                    week_counter[wk] += 1

            timeline = [
                {"week": wk, "week_label": _week_label(wk), "count": week_counter.get(wk, 0)}
                for wk in all_weeks
            ]

            # Thematic breakdown (main_theme of documents mentioning this entity)
            theme_counter = Counter()
            for doc in docs:
                mt = doc.get("main_theme", "other_mixed")
                theme_counter[mt] += 1

            themes = [
                {
                    "theme_key": tk,
                    "label": THEME_LABELS.get(tk, tk),
                    "count": c,
                    "share": round((c / count) * 100, 1) if count > 0 else 0
                }
                for tk, c in theme_counter.most_common()
            ]

            # Source coverage
            source_counter = Counter()
            for doc in docs:
                sk = doc.get("source_key", "unknown")
                source_counter[sk] += 1

            sources = [
                {
                    "source_key": sk,
                    "source_name": SOURCE_DISPLAY_NAMES.get(sk, sk),
                    "count": c,
                    "share": round((c / count) * 100, 1) if count > 0 else 0
                }
                for sk, c in source_counter.most_common()
            ]

            profiles[cat][entity] = {
                "name": entity,
                "total": count,
                "doc_rate": doc_rate,
                "timeline": timeline,
                "themes": themes,
                "sources": sources,
            }

    # Sort each category by total descending
    for cat in CATEGORIES:
        profiles[cat] = dict(
            sorted(profiles[cat].items(), key=lambda x: x[1]["total"], reverse=True)
        )

    return profiles


def compute_coverage_matrix(entity_profiles: dict) -> dict:
    """
    For each category, build a matrix: top N entities × 7 sources.
    Cell value = number of documents where source X mentions entity Y.
    """
    matrix_data = {}

    for cat in CATEGORIES:
        entities_sorted = list(entity_profiles[cat].items())[:COVERAGE_TOP_N]
        if not entities_sorted:
            continue

        entity_names = [e[0] for e in entities_sorted]
        source_names = [SOURCE_DISPLAY_NAMES.get(sk, sk) for sk in SOURCE_ORDER]

        # Build matrix rows
        rows = []
        for entity_name, profile in entities_sorted:
            source_lookup = {s["source_key"]: s["count"] for s in profile["sources"]}
            row = [source_lookup.get(sk, 0) for sk in SOURCE_ORDER]
            rows.append({"entity": entity_name, "counts": row, "total": profile["total"]})

        # Max value for color scaling
        max_val = max((c for r in rows for c in r["counts"]), default=1)

        matrix_data[cat] = {
            "entities": entity_names,
            "sources": source_names,
            "source_keys": SOURCE_ORDER,
            "rows": rows,
            "max_value": max_val,
        }

    return matrix_data


def compute_entity_pairs(documents: list[dict]) -> list[dict]:
    """
    Find the most frequently co-occurring entity pairs within the same document.
    Considers cross-category pairs (e.g., person + country) and same-category.
    """
    pair_counter = Counter()
    pair_meta = {}  # stores category info per pair

    for doc in documents:
        entities = doc.get("entities", {})

        # Flatten all entities with category tags
        all_entities = []
        for cat in CATEGORIES:
            for entity in entities.get(cat, []):
                all_entities.append((entity, cat))

        # Count all pairs within this document (unordered, deduped)
        seen_pairs = set()
        for (ea, ca), (eb, cb) in combinations(all_entities, 2):
            # Canonical order: alphabetical to avoid (A,B) and (B,A) duplication
            if ea == eb:
                continue
            key = tuple(sorted([ea, eb]))
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            pair_counter[key] += 1
            if key not in pair_meta:
                pair_meta[key] = (ca, cb) if ea < eb else (cb, ca)

    # Build top N pairs
    pairs = []
    for (ea, eb), count in pair_counter.most_common(PAIRS_TOP_N):
        ca, cb = pair_meta.get((ea, eb), ("unknown", "unknown"))
        pairs.append({
            "entity_a": ea,
            "entity_b": eb,
            "category_a": ca,
            "category_b": cb,
            "count": count,
        })

    return pairs


def compute_entity_analysis(documents: list[dict]) -> dict:
    """Main entry point."""
    all_weeks = _get_all_weeks(documents)

    profiles = compute_entity_profiles(documents, all_weeks)
    coverage = compute_coverage_matrix(profiles)
    pairs = compute_entity_pairs(documents)

    # Summarize counts per category for the frontend
    category_counts = {cat: len(profiles[cat]) for cat in CATEGORIES}

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total_documents": len(documents),
        "category_counts": category_counts,
        "profiles": profiles,
        "coverage_matrix": coverage,
        "entity_pairs": pairs,
    }
