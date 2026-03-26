from datetime import date, timedelta


def _group_docs_by_source(documents):
    """
    Group documents by source_key.

    Returns a dict: {source_key: [list of documents from that source]}.
    This is the foundation for source-level normalization — instead of
    counting raw mentions across the entire corpus, we compute rates
    per source first, then average them.
    """
    groups = {}
    for doc in documents:
        key = doc.get('source_key')
        if key:
            if key not in groups:
                groups[key] = []
            groups[key].append(doc)
    return groups


def _filter_by_period(documents, period_days=14):
    """
    Filters the documents according to the period_days.
    """
    today = date.today()
    cutoff_date = today - timedelta(days=period_days)

    filtered = []
    for doc in documents:
        if not doc.get('publication_date_iso'):
            continue

        try:
            pub_date = date.fromisoformat(doc['publication_date_iso'])
        except (ValueError, TypeError):
            continue

        if pub_date > cutoff_date:
            filtered.append(doc)

    filtered.sort(key=lambda doc: doc['publication_date_iso'], reverse=True)

    return filtered


def _count_entity_frequency(documents, category):
    """Counts the raw frequency of each entity (used for raw mention counts)."""
    frequency = {}

    for doc in documents:
        entities = doc.get('entities', {}).get(category, [])

        for entity in set(entities):
            frequency[entity] = frequency.get(entity, 0) + 1

    sorted_frequency = dict(
        sorted(frequency.items(), key=lambda item: item[1], reverse=True)
    )

    return sorted_frequency


def _count_theme_frequency(documents):
    """Counts the raw frequency of each theme (used for raw mention counts)."""
    frequency = {}

    for doc in documents:
        themes = set()

        main = doc.get('main_theme')
        if main:
            themes.add(main)

        secondary = doc.get('secondary_theme', [])
        if secondary:
            themes.update(secondary)

        for theme in themes:
            frequency[theme] = frequency.get(theme, 0) + 1

    sorted_frequency = dict(
        sorted(frequency.items(), key=lambda item: item[1], reverse=True)
    )

    return sorted_frequency


def _compute_source_normalized_entity_freq(source_groups, category):
    """
    Compute source-normalized frequency rates for entities.

    Instead of counting raw mentions across the entire corpus (which lets
    high-volume sources dominate), this computes a per-source mention rate
    and then averages across all sources.

    For each source:  rate = docs_mentioning_entity / total_docs_from_source
    Final score:      mean(rates across all sources that have documents)

    Returns: {entity: averaged_rate} sorted descending by rate.
    """
    entity_rates = {}

    for source_key, docs in source_groups.items():
        source_total = len(docs)
        if source_total == 0:
            continue

        source_entity_counts = {}
        for doc in docs:
            entities = doc.get('entities', {}).get(category, [])
            for entity in set(entities):
                source_entity_counts[entity] = source_entity_counts.get(entity, 0) + 1

        for entity, count in source_entity_counts.items():
            rate = (count / source_total) * 100
            if entity not in entity_rates:
                entity_rates[entity] = []
            entity_rates[entity].append(rate)

    num_sources = len(source_groups)
    averaged = {}
    for entity, rates in entity_rates.items():
        rates_with_zeros = rates + [0.0] * (num_sources - len(rates))
        averaged[entity] = round(sum(rates_with_zeros) / num_sources, 2)

    sorted_averaged = dict(
        sorted(averaged.items(), key=lambda item: item[1], reverse=True)
    )

    return sorted_averaged


def _compute_source_normalized_theme_freq(source_groups):
    """
    Compute source-normalized frequency rates for themes.

    Same logic as entity normalization: per-source rate, then average.
    A theme that appears consistently across many sources ranks higher
    than one concentrated in a single high-volume source.

    Returns: {theme: averaged_rate} sorted descending by rate.
    """
    theme_rates = {}

    for source_key, docs in source_groups.items():
        source_total = len(docs)
        if source_total == 0:
            continue

        source_theme_counts = {}
        for doc in docs:
            themes = set()
            main = doc.get('main_theme')
            if main:
                themes.add(main)
            secondary = doc.get('secondary_themes', [])
            if secondary:
                themes.update(secondary)

            for theme in themes:
                source_theme_counts[theme] = source_theme_counts.get(theme, 0) + 1

        for theme, count in source_theme_counts.items():
            rate = (count / source_total) * 100
            if theme not in theme_rates:
                theme_rates[theme] = []
            theme_rates[theme].append(rate)

    num_sources = len(source_groups)
    averaged = {}
    for theme, rates in theme_rates.items():
        rates_with_zeros = rates + [0.0] * (num_sources - len(rates))
        averaged[theme] = round(sum(rates_with_zeros) / num_sources, 2)

    sorted_averaged = dict(
        sorted(averaged.items(), key=lambda item: item[1], reverse=True)
    )

    return sorted_averaged


def _build_sparkline(documents, entity_or_theme, category, period_days, active_sources):
    """
    Build a daily source-normalized rate array for an entity or theme.

    For each day, computes per-source mention rates and averages them,
    ensuring no single high-volume source dominates the visual trend.

    Returns a list of floats (percentages) with length = period_days * 2.
    """
    total_days = period_days * 2
    sparkline = [0.0] * total_days
    num_sources = len(active_sources)

    if num_sources == 0:
        return sparkline

    today = date.today()
    period_start = today - timedelta(days=total_days - 1)

    # Build daily per-source data: {day_index: {source_key: [entity_count, total_count]}}
    daily_source_data = {i: {} for i in range(total_days)}

    for doc in documents:
        pub_date_str = doc.get('publication_date_iso')
        if not pub_date_str:
            continue

        try:
            pub_date = date.fromisoformat(pub_date_str)
        except (ValueError, TypeError):
            continue

        day_index = (pub_date - period_start).days
        if day_index < 0 or day_index >= total_days:
            continue

        source_key = doc.get('source_key')
        if not source_key:
            continue

        if source_key not in daily_source_data[day_index]:
            daily_source_data[day_index][source_key] = [0, 0]

        daily_source_data[day_index][source_key][1] += 1  # total docs from source

        # Check if entity/theme is present in this document
        contains = False
        if category == "theme":
            if doc.get('main_theme') == entity_or_theme:
                contains = True
            elif entity_or_theme in doc.get('secondary_themes', []):
                contains = True
        else:
            entities = doc.get('entities', {}).get(category, [])
            if entity_or_theme in entities:
                contains = True

        if contains:
            daily_source_data[day_index][source_key][0] += 1

    # Compute daily source-normalized rate
    for day_idx in range(total_days):
        day_data = daily_source_data[day_idx]
        rates = []

        for source_key in active_sources:
            if source_key in day_data:
                entity_count, total_count = day_data[source_key]
                rate = (entity_count / total_count) * 100 if total_count > 0 else 0.0
            else:
                rate = 0.0
            rates.append(rate)

        sparkline[day_idx] = round(sum(rates) / num_sources, 2)

    return sparkline


def _build_category_result(documents, norm_freq, raw_freq, category, period_days, prev_norm_freq, num_sources, active_sources):
    """
    Build the final result structure for a category (top + runners-up).

    Parameters:
        documents:       all docs (current + previous period) for sparkline building
        norm_freq:       {entity: source_averaged_rate} for current period (for ranking + percentage)
        raw_freq:        {entity: raw_count} for current period (for display)
        category:        "persons", "countries", "organizations", or "theme"
        period_days:     14 (for sparkline range)
        prev_norm_freq:  {entity: source_averaged_rate} for previous period (for trend)
        num_sources:     number of active sources in period (for per-source average)
        active_sources:  set of source keys active across both periods (for sparkline normalization)
    """
    if not norm_freq:
        return {"top": None, "runners_up": []}

    top_3 = list(norm_freq.items())[:3]

    if not top_3:
        return {"top": None, "runners_up": []}

    result = {"top": None, "runners_up": []}

    for idx, (entity_or_theme, normalized_rate) in enumerate(top_3):
        sparkline = _build_sparkline(documents, entity_or_theme, category, period_days, active_sources)

        prev_rate = prev_norm_freq.get(entity_or_theme, 0.0)
        trend = _compute_trend(normalized_rate, prev_rate)

        source_diversity = _count_source_diversity(documents, entity_or_theme, category)
        momentum = _compute_momentum_score(trend['current_rate'], trend['change_pct'])

        raw_mentions = raw_freq.get(entity_or_theme, 0)
        mentions_per_source = round(raw_mentions / num_sources, 1) if num_sources > 0 else 0

        entry = {
            "name": entity_or_theme,
            "mentions": mentions_per_source,
            "percentage": normalized_rate,
            "sparkline": sparkline,
            "trend": trend,
            "source_diversity": source_diversity,
            "momentum_score": momentum,
        }

        if idx == 0:
            result["top"] = entry
        else:
            result["runners_up"].append(entry)

    return result


def _build_momentum_board(period_docs, prev_docs, curr_source_groups, prev_source_groups):
    """
    Build a cross-category ranking of ALL entities by momentum.

    Uses source-normalized rates: each source contributes equally to the
    entity's score, preventing high-volume sources from dominating.
    Returns the top 5 rising and top 5 falling signals.
    """
    all_entries = []
    num_sources = len(curr_source_groups)

    for category in ["persons", "countries", "organizations"]:
        curr_norm = _compute_source_normalized_entity_freq(curr_source_groups, category)
        prev_norm = _compute_source_normalized_entity_freq(prev_source_groups, category)
        curr_raw = _count_entity_frequency(period_docs, category)

        all_entities = set(list(curr_norm.keys()) + list(prev_norm.keys()))

        for entity in all_entities:
            raw_mentions = curr_raw.get(entity, 0)
            prev_raw = _count_entity_frequency(prev_docs, category).get(entity, 0)

            if raw_mentions + prev_raw < 8:
                continue

            curr_rate = curr_norm.get(entity, 0.0)
            prev_rate = prev_norm.get(entity, 0.0)

            trend = _compute_trend(curr_rate, prev_rate)
            momentum = _compute_momentum_score(trend['current_rate'], trend['change_pct'])
            source_div = _count_source_diversity(period_docs, entity, category)

            mentions_per_source = round(raw_mentions / num_sources, 1) if num_sources > 0 else 0

            all_entries.append({
                "name": entity,
                "category": category,
                "momentum_score": momentum,
                "change_pct": trend['change_pct'],
                "current_rate": trend['current_rate'],
                "previous_rate": trend['previous_rate'],
                "source_diversity": source_div,
                "mentions": mentions_per_source
            })

    curr_theme_norm = _compute_source_normalized_theme_freq(curr_source_groups)
    prev_theme_norm = _compute_source_normalized_theme_freq(prev_source_groups)
    curr_theme_raw = _count_theme_frequency(period_docs)
    prev_theme_raw = _count_theme_frequency(prev_docs)
    all_themes = set(list(curr_theme_norm.keys()) + list(prev_theme_norm.keys()))

    for theme in all_themes:
        raw_mentions = curr_theme_raw.get(theme, 0)
        prev_raw = prev_theme_raw.get(theme, 0)

        if raw_mentions + prev_raw < 3:
            continue

        curr_rate = curr_theme_norm.get(theme, 0.0)
        prev_rate = prev_theme_norm.get(theme, 0.0)

        trend = _compute_trend(curr_rate, prev_rate)
        momentum = _compute_momentum_score(trend['current_rate'], trend['change_pct'])
        source_div = _count_source_diversity(period_docs, theme, "theme")

        mentions_per_source = round(raw_mentions / num_sources, 1) if num_sources > 0 else 0

        all_entries.append({
            "name": theme,
            "category": "themes",
            "momentum_score": momentum,
            "change_pct": trend['change_pct'],
            "current_rate": trend['current_rate'],
            "previous_rate": trend['previous_rate'],
            "source_diversity": source_div,
            "mentions": mentions_per_source
        })

    sorted_by_momentum = sorted(all_entries, key=lambda e: e['momentum_score'], reverse=True)
    risers = sorted_by_momentum[:5]

    fallers_pool = [e for e in all_entries if e['change_pct'] < 0]
    fallers_pool.sort(key=lambda e: e['change_pct'])
    fallers = fallers_pool[:5]

    return {
        "risers": risers,
        "fallers": fallers
    }


def _compute_trend(current_rate, previous_rate):
    """
    Compare source-normalized rates between current and previous periods.

    Both rates are already source-averaged (computed by
    _compute_source_normalized_entity_freq or _compute_source_normalized_theme_freq).
    This function just computes the direction and percentage change.
    """
    if current_rate == 0 and previous_rate == 0:
        return {
            "direction": "stable",
            "change_pct": 0.0,
            "current_rate": current_rate,
            "previous_rate": previous_rate,
        }

    if previous_rate == 0:
        return {
            "direction": "up",
            "change_pct": round(current_rate, 1),
            "current_rate": current_rate,
            "previous_rate": previous_rate
        }

    change_pct = round(((current_rate - previous_rate) / previous_rate) * 100, 1)

    if change_pct > 10:
        direction = "up"
    elif change_pct < -10:
        direction = "down"
    else:
        direction = "stable"

    return {
        "direction": direction,
        "change_pct": change_pct,
        "current_rate": current_rate,
        "previous_rate": previous_rate
    }


def _compute_momentum_score(current_rate, change_pct):
    """
    Compute momentul score combining volume (current_rate) with direction (change_pct)

    Formula: momentul = current_rate * (1 + change_pct / 100)

    A high momentul means the entity is both frequently mentioned and gaining traction.
    A low or negative momentul means the entity is losing relevance.
    """

    momentum = current_rate * (1 + change_pct / 100)

    return round(momentum, 1)


def _filter_previous_period(documents, period_days=14):
    """
    Filter documents from the period before the current trending window.
    """
    today = date.today()
    current_start = today - timedelta(days=period_days - 1)
    previous_start = current_start - timedelta(days=period_days)

    filtered = []
    for doc in documents:
        if not doc.get('publication_date_iso'):
            continue

        try:
            pub_date = date.fromisoformat(doc['publication_date_iso'])
        except (ValueError, TypeError):
            continue

        if previous_start <= pub_date < current_start:
            filtered.append(doc)

    return filtered

def _count_source_diversity(documents, entity_or_theme, category):
    """
    Count how many distinct sources mention a given entity or theme.

    A higher diversity means the signal is corroborated across multiple
    independent sources, making it analytically more reliable.
    """
    sources = set()

    for doc in documents:
        contains = False

        if category == "theme":
            if doc.get('main_theme') == entity_or_theme:
                contains = True
            elif entity_or_theme in doc.get('secondary_themes', []):
                contains = True
        else:
            entities = doc.get('entities', {}).get(category, [])
            if entity_or_theme in entities:
                contains = True

        if contains:
            source = doc.get('source_key')
            if source:
                sources.add(source)

    return len(sources)


def compute_trending(documents, period_days=14):
    """
    Compute trending entities and themes for the given period.

    Uses source-level normalization: each source contributes equally to
    entity/theme scores, regardless of how many documents it publishes.
    This prevents high-volume sources (like EEAS) from dominating the
    rankings over low-volume ones (like MAE).
    """
    period_docs = _filter_by_period(documents, period_days)
    prev_docs = _filter_previous_period(documents, period_days)
    total = len(period_docs)

    if total == 0:
        return {
            "period_days": period_days,
            "period_start": str(date.today() - timedelta(days=period_days - 1)),
            "period_end": str(date.today()),
            "total_documents_in_period": 0,
            "categories": {}
        }

    # Group documents by source for source-level normalization
    curr_source_groups = _group_docs_by_source(period_docs)
    prev_source_groups = _group_docs_by_source(prev_docs)

    # Source-normalized rates (for ranking and trend comparison)
    person_norm = _compute_source_normalized_entity_freq(curr_source_groups, "persons")
    country_norm = _compute_source_normalized_entity_freq(curr_source_groups, "countries")
    org_norm = _compute_source_normalized_entity_freq(curr_source_groups, "organizations")
    theme_norm = _compute_source_normalized_theme_freq(curr_source_groups)

    prev_person_norm = _compute_source_normalized_entity_freq(prev_source_groups, "persons")
    prev_country_norm = _compute_source_normalized_entity_freq(prev_source_groups, "countries")
    prev_org_norm = _compute_source_normalized_entity_freq(prev_source_groups, "organizations")
    prev_theme_norm = _compute_source_normalized_theme_freq(prev_source_groups)

    # Raw counts (for per-source average calculation)
    person_raw = _count_entity_frequency(period_docs, "persons")
    country_raw = _count_entity_frequency(period_docs, "countries")
    org_raw = _count_entity_frequency(period_docs, "organizations")
    theme_raw = _count_theme_frequency(period_docs)

    num_sources = len(curr_source_groups)
    all_period_docs = period_docs + prev_docs

    # Union of all source keys across both periods (for sparkline normalization)
    active_sources = set(curr_source_groups.keys()) | set(prev_source_groups.keys())

    categories = {
        "persons": _build_category_result(all_period_docs, person_norm, person_raw, "persons", period_days, prev_person_norm, num_sources, active_sources),
        "countries": _build_category_result(all_period_docs, country_norm, country_raw, "countries", period_days, prev_country_norm, num_sources, active_sources),
        "organizations": _build_category_result(all_period_docs, org_norm, org_raw, "organizations", period_days, prev_org_norm, num_sources, active_sources),
        "themes": _build_category_result(all_period_docs, theme_norm, theme_raw, "theme", period_days, prev_theme_norm, num_sources, active_sources),
    }

    momentum_board = _build_momentum_board(period_docs, prev_docs, curr_source_groups, prev_source_groups)

    today = date.today()
    period_start = today - timedelta(days=period_days - 1)

    trending = {
        "period_days": period_days,
        "period_start": str(period_start),
        "period_end": str(today),
        "total_documents_in_period": total,
        "categories": categories,
        "momentum_board": momentum_board
    }

    return trending


