"""
Theme Analysis — computes data for the Themes dashboard page.

Three outputs:
1. Per-theme profiles (timeline, top entities, source breakdown, recent docs)
2. Co-occurrence matrix (main_theme vs secondary_themes)
3. Theme concentration by source (how focused each source is)
"""

from datetime import datetime, timedelta
from collections import Counter, defaultdict

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

THEME_KEYS_ORDERED = [
    "support_ukraine",
    "eastern_flank_nato_deterrence",
    "romania_republic_of_moldova",
    "russia_regional_implications",
    "eu_regional_security",
    "black_sea_regional_security",
    "other_mixed",
]


def _iso_week_key(date_str: str) -> str:
    """Convert YYYY-MM-DD to ISO week key YYYY-Wxx."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        iso_year, iso_week, _ = dt.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    except (ValueError, TypeError):
        return None


def _week_label(week_key: str) -> str:
    """Convert YYYY-Wxx to readable 'Mon DD — Mon DD' range."""
    try:
        parts = week_key.split("-W")
        year = int(parts[0])
        week = int(parts[1])
        monday = datetime.strptime(f"{year}-W{week:02d}-1", "%Y-W%W-%w")
        if monday.isocalendar()[1] != week:
            monday = datetime.strptime(f"{year}-W{week:02d}-1", "%G-W%V-%u")
        sunday = monday + timedelta(days=6)
        fmt = lambda d: d.strftime("%b %d")
        return f"{fmt(monday)} — {fmt(sunday)}"
    except Exception:
        return week_key


def _get_all_weeks(documents: list[dict]) -> list[str]:
    """Get sorted list of all ISO week keys present in documents."""
    weeks = set()
    for doc in documents:
        wk = _iso_week_key(doc.get("publication_date_iso", ""))
        if wk:
            weeks.add(wk)
    return sorted(weeks)


def compute_theme_profiles(documents: list[dict], all_weeks: list[str]) -> dict:
    """Compute per-theme stats: timeline, top entities, source breakdown, recent docs."""
    theme_docs = defaultdict(list)
    for doc in documents:
        mt = doc.get("main_theme", "other_mixed")
        theme_docs[mt].append(doc)

    total_docs = len(documents)
    profiles = {}

    for theme_key in THEME_KEYS_ORDERED:
        docs = theme_docs.get(theme_key, [])
        count = len(docs)
        percentage = round((count / total_docs) * 100, 1) if total_docs > 0 else 0

        # Timeline: docs per week
        week_counter = Counter()
        for doc in docs:
            wk = _iso_week_key(doc.get("publication_date_iso", ""))
            if wk:
                week_counter[wk] += 1

        timeline = []
        for wk in all_weeks:
            timeline.append({
                "week": wk,
                "week_label": _week_label(wk),
                "count": week_counter.get(wk, 0),
            })

        # Top entities
        person_counter = Counter()
        country_counter = Counter()
        org_counter = Counter()
        for doc in docs:
            entities = doc.get("entities", {})
            for p in entities.get("persons", []):
                person_counter[p] += 1
            for c in entities.get("countries", []):
                country_counter[c] += 1
            for o in entities.get("organizations", []):
                org_counter[o] += 1

        top_entities = {
            "persons": [{"name": n, "count": c} for n, c in person_counter.most_common(5)],
            "countries": [{"name": n, "count": c} for n, c in country_counter.most_common(5)],
            "organizations": [{"name": n, "count": c} for n, c in org_counter.most_common(5)],
        }

        # Source breakdown
        source_counter = Counter()
        source_types = {}
        for doc in docs:
            sk = doc.get("source_key", "unknown")
            source_counter[sk] += 1
            source_types[sk] = doc.get("source_type", "unknown")

        source_breakdown = []
        for sk, cnt in source_counter.most_common():
            source_breakdown.append({
                "source_key": sk,
                "source_name": SOURCE_DISPLAY_NAMES.get(sk, sk),
                "source_type": source_types.get(sk, "unknown"),
                "count": cnt,
                "percentage": round((cnt / count) * 100, 1) if count > 0 else 0,
            })

        # Recent documents (top 8 by date)
        sorted_docs = sorted(docs, key=lambda d: d.get("publication_date_iso", ""), reverse=True)
        recent = []
        for doc in sorted_docs[:8]:
            recent.append({
                "title": doc.get("title", ""),
                "source_name": doc.get("source_name", ""),
                "source_key": doc.get("source_key", ""),
                "date": doc.get("publication_date_iso", ""),
                "url": doc.get("url", ""),
            })

        profiles[theme_key] = {
            "label": THEME_LABELS.get(theme_key, theme_key),
            "document_count": count,
            "percentage": percentage,
            "timeline": timeline,
            "top_entities": top_entities,
            "source_breakdown": source_breakdown,
            "recent_documents": recent,
        }

    return profiles


def compute_cooccurrence(documents: list[dict]) -> dict:
    """Compute co-occurrence matrix: how often each secondary theme appears with each main theme."""
    # Matrix: rows = main_theme, cols = secondary_theme
    matrix = defaultdict(Counter)
    total_with_secondary = 0

    for doc in documents:
        mt = doc.get("main_theme", "other_mixed")
        secondaries = doc.get("secondary_themes", [])
        if secondaries:
            total_with_secondary += 1
        for st in secondaries:
            matrix[mt][st] += 1

    # Build numeric matrix in fixed order (exclude other_mixed from display)
    display_keys = [k for k in THEME_KEYS_ORDERED if k != "other_mixed"]
    labels = [THEME_LABELS.get(k, k) for k in display_keys]

    numeric_matrix = []
    for main_key in display_keys:
        row = []
        for sec_key in display_keys:
            if main_key == sec_key:
                row.append(None)  # diagonal: theme can't be its own secondary
            else:
                row.append(matrix[main_key].get(sec_key, 0))
        numeric_matrix.append(row)

    # Find max value for color scaling
    max_val = 0
    for row in numeric_matrix:
        for val in row:
            if val is not None and val > max_val:
                max_val = val

    return {
        "keys": display_keys,
        "labels": labels,
        "matrix": numeric_matrix,
        "max_value": max_val,
        "total_with_secondary": total_with_secondary,
        "total_documents": len(documents),
    }


def compute_concentration(documents: list[dict]) -> list[dict]:
    """Compute how concentrated/diversified each source is across themes."""
    source_themes = defaultdict(Counter)
    source_meta = {}

    for doc in documents:
        sk = doc.get("source_key", "unknown")
        mt = doc.get("main_theme", "other_mixed")
        source_themes[sk][mt] += 1
        if sk not in source_meta:
            source_meta[sk] = {
                "source_name": doc.get("source_name", sk),
                "source_type": doc.get("source_type", "unknown"),
            }

    concentration = []
    for sk in sorted(source_meta.keys()):
        theme_counts = source_themes[sk]
        total = sum(theme_counts.values())

        theme_distribution = {}
        for tk in THEME_KEYS_ORDERED:
            cnt = theme_counts.get(tk, 0)
            share = round((cnt / total) * 100, 1) if total > 0 else 0
            theme_distribution[tk] = {"count": cnt, "share": share}

        # Diversity index: number of themes with >5% share
        diversity = sum(1 for v in theme_distribution.values() if v["share"] > 5)

        # Dominant theme
        dominant_key = max(theme_counts, key=theme_counts.get) if theme_counts else "other_mixed"
        dominant_share = theme_distribution[dominant_key]["share"]

        concentration.append({
            "source_key": sk,
            "source_name": source_meta[sk]["source_name"],
            "source_type": source_meta[sk]["source_type"],
            "total_docs": total,
            "theme_distribution": theme_distribution,
            "diversity_index": diversity,
            "dominant_theme": dominant_key,
            "dominant_share": dominant_share,
        })

    # Sort: official first, then think_tank, within each group by total_docs desc
    type_order = {"official": 0, "think_tank": 1}
    concentration.sort(key=lambda x: (type_order.get(x["source_type"], 2), -x["total_docs"]))

    return concentration


def compute_theme_analysis(documents: list[dict]) -> dict:
    """Main entry point — computes all theme analysis data."""
    all_weeks = _get_all_weeks(documents)

    profiles = compute_theme_profiles(documents, all_weeks)
    cooccurrence = compute_cooccurrence(documents)
    concentration = compute_concentration(documents)

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total_documents": len(documents),
        "themes": profiles,
        "cooccurrence": cooccurrence,
        "concentration": concentration,
    }
