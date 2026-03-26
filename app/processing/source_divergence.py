from collections import defaultdict
from datetime import date


def _split_by_source_type(documents):
    """
    Split documents into two groups based on source_type field.
    """
    official = []
    think_tank = []

    for doc in documents:
        st = doc.get("source_type", "").lower().strip()
        if st == "official":
            official.append(doc)
        elif st == "think_tank":
            think_tank.append(doc)

    return official, think_tank


def _group_by_source(documents):
    """
    Group documents by source_key.
    Returns: {source_key: [list of documents]}
    """
    groups = defaultdict(list)
    for doc in documents:
        key = doc.get("source_key")
        if key:
            groups[key].append(doc)
    return dict(groups)


def _compute_theme_distribution(documents):
    """
    Compute source-normalized theme distribution.

    For each source within the group:
      - theme_rate = docs_with_theme / total_docs_from_source
    Then average across all sources in the group.
    Normalize final rates to sum to 100%.
    """
    source_groups = _group_by_source(documents)
    num_sources = len(source_groups)

    if num_sources == 0:
        return {}

    # Collect all themes
    all_themes = set()
    for doc in documents:
        theme = doc.get("main_theme")
        if theme:
            all_themes.add(theme)

    # Per-source theme rates
    theme_rate_sums = defaultdict(float)

    for source_key, source_docs in source_groups.items():
        source_total = len(source_docs)
        if source_total == 0:
            continue

        theme_counts = defaultdict(int)
        for doc in source_docs:
            theme = doc.get("main_theme")
            if theme:
                theme_counts[theme] += 1

        for theme in all_themes:
            theme_rate_sums[theme] += theme_counts[theme] / source_total

    # Average across sources
    avg_rates = {}
    for theme in all_themes:
        avg_rates[theme] = theme_rate_sums[theme] / num_sources

    # Normalize to 100%
    rate_total = sum(avg_rates.values())

    distribution = {}
    for theme in all_themes:
        share = round((avg_rates[theme] / rate_total) * 100, 1) if rate_total > 0 else 0.0
        # Raw count for reference
        raw_count = sum(
            1 for doc in documents if doc.get("main_theme") == theme
        )
        distribution[theme] = {"count": raw_count, "share": share}

    return distribution


def _compute_top_entities(documents, category, top_n=10):
    """
    Compute source-normalized entity frequency.

    For each source:
      - entity_rate = docs_mentioning_entity / total_docs_from_source
    Then average across all sources in the group.
    """
    source_groups = _group_by_source(documents)
    num_sources = len(source_groups)

    if num_sources == 0:
        return []

    # Collect all entity names in this category
    all_entities = set()
    for doc in documents:
        entities = doc.get("entities", {})
        values = entities.get(category, [])
        all_entities.update(values)

    # Per-source entity rates
    entity_rate_sums = defaultdict(float)

    for source_key, source_docs in source_groups.items():
        source_total = len(source_docs)
        if source_total == 0:
            continue

        entity_doc_counts = defaultdict(int)
        for doc in source_docs:
            entities = doc.get("entities", {})
            values = entities.get(category, [])
            for entity in set(values):  # document frequency
                entity_doc_counts[entity] += 1

        for entity in all_entities:
            entity_rate_sums[entity] += entity_doc_counts[entity] / source_total

    # Average across sources
    avg_rates = {}
    for entity in all_entities:
        avg_rates[entity] = entity_rate_sums[entity] / num_sources

    # Sort by average rate descending
    sorted_entities = sorted(avg_rates.items(), key=lambda x: x[1], reverse=True)

    result = []
    for name, avg_rate in sorted_entities[:top_n]:
        share = round(avg_rate * 100, 1)
        # Raw count for reference
        raw_count = 0
        for doc in documents:
            entities = doc.get("entities", {})
            if name in set(entities.get(category, [])):
                raw_count += 1
        result.append({"name": name, "count": raw_count, "share": share})

    return result


def _build_group_profile(documents):
    """
    Build a complete analytical profile for a source type group.
    Uses source-normalized rates for themes and entities.
    """
    sources = sorted(set(doc.get("source_name", "unknown") for doc in documents))
    source_keys = sorted(set(doc.get("source_key", "unknown") for doc in documents))

    return {
        "total_documents": len(documents),
        "num_sources": len(source_keys),
        "sources": sources,
        "theme_distribution": _compute_theme_distribution(documents),
        "top_entities": {
            "countries": _compute_top_entities(documents, "countries"),
            "organizations": _compute_top_entities(documents, "organizations"),
            "persons": _compute_top_entities(documents, "persons"),
        },
    }


def _compute_theme_gaps(official_dist, think_tank_dist):
    """
    Compute the divergence between official and think tank theme shares.
    Both inputs now use source-normalized shares.
    """
    all_themes = set(official_dist.keys()) | set(think_tank_dist.keys())

    gaps = []
    for theme in all_themes:
        off_share = official_dist.get(theme, {}).get("share", 0.0)
        tt_share = think_tank_dist.get(theme, {}).get("share", 0.0)
        gap = round(tt_share - off_share, 1)

        gaps.append({
            "theme": theme,
            "official_share": off_share,
            "think_tank_share": tt_share,
            "gap": gap,
        })

    # Sort by absolute gap descending — biggest divergences first
    gaps.sort(key=lambda x: abs(x["gap"]), reverse=True)

    return gaps


def _compute_entity_gaps(official_entities, think_tank_entities, category, top_n=10):
    """
    Compute entity share gaps between groups for a given category.
    Both inputs now use source-normalized shares.
    """
    off_lookup = {e["name"]: e["share"] for e in official_entities}
    tt_lookup = {e["name"]: e["share"] for e in think_tank_entities}

    all_names = set(off_lookup.keys()) | set(tt_lookup.keys())

    gaps = []
    for name in all_names:
        off_share = off_lookup.get(name, 0.0)
        tt_share = tt_lookup.get(name, 0.0)
        gap = round(tt_share - off_share, 1)

        gaps.append({
            "name": name,
            "official_share": off_share,
            "think_tank_share": tt_share,
            "gap": gap,
        })

    gaps.sort(key=lambda x: abs(x["gap"]), reverse=True)

    return gaps[:top_n]


def compute_source_divergence(documents):
    """
    Main entry point. Computes the full source divergence analysis
    using source-normalized rates within each group.
    """
    official_docs, think_tank_docs = _split_by_source_type(documents)

    official_profile = _build_group_profile(official_docs)
    think_tank_profile = _build_group_profile(think_tank_docs)

    # Compute divergence metrics
    theme_gaps = _compute_theme_gaps(
        official_profile["theme_distribution"],
        think_tank_profile["theme_distribution"],
    )

    entity_gaps = {}
    for category in ("countries", "organizations", "persons"):
        entity_gaps[category] = _compute_entity_gaps(
            official_profile["top_entities"][category],
            think_tank_profile["top_entities"][category],
            category,
        )

    # Compute period from all documents
    all_dates = []
    for doc in documents:
        d = doc.get("publication_date_iso")
        if d:
            try:
                all_dates.append(date.fromisoformat(d))
            except (ValueError, TypeError):
                pass

    period_start = min(all_dates).isoformat() if all_dates else None
    period_end = max(all_dates).isoformat() if all_dates else None

    return {
        "period_start": period_start,
        "period_end": period_end,
        "total_documents": len(documents),
        "official": official_profile,
        "think_tank": think_tank_profile,
        "divergence": {
            "theme_gaps": theme_gaps,
            "entity_gaps": entity_gaps,
        },
    }
