from collections import defaultdict


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


def _compute_theme_distribution(documents):
    """
    Count main_theme frequency across a document group.
    """
    counts = defaultdict(int)
    total = 0

    for doc in documents:
        theme = doc.get("main_theme")
        if theme:
            counts[theme] += 1
            total += 1

    distribution = {}
    for theme, count in counts.items():
        share = round((count / total) * 100, 1) if total > 0 else 0.0
        distribution[theme] = {"count": count, "share": share}

    return distribution


def _compute_top_entities(documents, category, top_n=10):
    """
    Count entity frequency (document-level: 1 mention per document max)
    for a given entity category (countries, organizations, persons).
    """
    counts = defaultdict(int)
    total = len(documents)

    for doc in documents:
        entities = doc.get("entities", {})
        values = entities.get(category, [])
        # Document frequency: count each entity once per document
        for entity in set(values):
            counts[entity] += 1

    sorted_entities = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    result = []
    for name, count in sorted_entities[:top_n]:
        share = round((count / total) * 100, 1) if total > 0 else 0.0
        result.append({"name": name, "count": count, "share": share})

    return result


def _build_group_profile(documents):
    """
    Build a complete analytical profile for a source type group.
    Includes: source list, theme distribution, top entities per category.
    """
    sources = sorted(set(doc.get("source_name", "unknown") for doc in documents))

    return {
        "total_documents": len(documents),
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
    """
    # Build lookup: entity_name -> share per group
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
    Main entry point. Computes the full source divergence analysis.
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

    return {
        "official": official_profile,
        "think_tank": think_tank_profile,
        "divergence": {
            "theme_gaps": theme_gaps,
            "entity_gaps": entity_gaps,
        },
    }
