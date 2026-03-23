from datetime import date, timedelta

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
    "Counts the frequency of each entity."
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
    """
    Counts the frequency of each theme.
    """
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


def _build_sparkline(documents, entity_or_theme, category, period_days):
    """
    Build a daily frequency array for an entity or theme over the period.
    """
    total_days = period_days * 2
    sparkline = [0] * total_days
    today = date.today()
    period_start = today - timedelta(days=total_days - 1)

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

        contains_entity = False

        if category == "theme":
            if doc.get('main_theme') == entity_or_theme:
                contains_entity = True
            elif entity_or_theme in doc.get('secondary_themes', []):
                contains_entity = True
        else:
            entities = doc.get('entities', {}).get(category, [])
            if entity_or_theme in entities:
                contains_entity = True

        if contains_entity:
            sparkline[day_index] += 1

    return sparkline


def _build_category_result(documents, frequency_dict, category, period_days, total_documents, prev_frequency_dict, prev_total_documents):
    """
    Build the final result structure for a category (top + runners-up with sparklines and percentages).
    """
    if not frequency_dict:
        return {"top": None, "runners_up": []}

    top_3 = list(frequency_dict.items())[:3]

    if not top_3:
        return {"top": None, "runners_up": []}

    result = {"top": None, "runners_up": []}

    for idx, (entity_or_theme, mentions) in enumerate(top_3):
        sparkline = _build_sparkline(documents, entity_or_theme, category, period_days)
        percentage = round((mentions / total_documents) * 100, 1)

        prev_mentions = prev_frequency_dict.get(entity_or_theme, 0)
        trend = _compute_trend(mentions, total_documents, prev_mentions, prev_total_documents)

        # compute source diversity (how many distinct sources mention this entry)
        source_diversity = _count_source_diversity(documents, entity_or_theme, category)

        # compute momentul score (volume x direction)
        momentum = _compute_momentum_score(trend['current_rate'], trend['change_pct'])


        entry = {
            "name": entity_or_theme,
            "mentions": mentions,
            "percentage": percentage,
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


def _build_momentum_board(period_docs, prev_docs, total, prev_total):
    """
    Build a cross-category ranking of ALL entities by momentum.

    Computes normalized trend for every entity and theme in the corpus,
    then returns the top 5 rising and top 5 falling signals.
    """
    all_entries = []

    for category in ["persons", "countries", "organizations"]:
        current_freq = _count_entity_frequency(period_docs, category)
        prev_freq = _count_entity_frequency(prev_docs, category)

        all_entities = set(list(current_freq.keys()) + list(prev_freq.keys()))

        for entity in all_entities:
            curr_mentions = current_freq.get(entity, 0)
            prev_mentions = prev_freq.get(entity, 0)

            if curr_mentions + prev_mentions < 8:
                continue

            trend = _compute_trend(curr_mentions, total, prev_mentions, prev_total)
            momentum = _compute_momentum_score(trend['current_rate'], trend['change_pct'])
            source_div = _count_source_diversity(period_docs, entity, category)

            all_entries.append({
                "name": entity,
                "category": category,
                "momentum_score": momentum,
                "change_pct": trend['change_pct'],
                "current_rate": trend['current_rate'],
                "previous_rate": trend['previous_rate'],
                "source_diversity": source_div,
                "mentions": curr_mentions
            })

    current_theme_freq = _count_theme_frequency(period_docs)
    prev_theme_freq = _count_theme_frequency(prev_docs)
    all_themes = set(list(current_theme_freq.keys()) + list(prev_theme_freq.keys()))

    for theme in all_themes:
        curr_mentions = current_theme_freq.get(theme, 0)
        prev_mentions = prev_theme_freq.get(theme, 0)

        if curr_mentions + prev_mentions < 3:
            continue

        trend = _compute_trend(curr_mentions, total, prev_mentions, prev_total)
        momentum = _compute_momentum_score(trend['current_rate'], trend['change_pct'])
        source_div = _count_source_diversity(period_docs, theme, "theme")

        all_entries.append({
            "name": theme,
            "category": "themes",
            "momentum_score": momentum,
            "change_pct": trend['change_pct'],
            "current_rate": trend['current_rate'],
            "previous_rate": trend['previous_rate'],
            "source_diversity": source_div,
            "mentions": curr_mentions
        })

    # Sort by momentum_score (combines volume with direction)
    sorted_by_momentum = sorted(all_entries, key=lambda e: e['momentum_score'], reverse=True)

    # Risers: top 5 by highest momentum
    risers = sorted_by_momentum[:5]

    # Fallers: top 5 by lowest momentum (but only those with negative change)
    fallers_pool = [e for e in all_entries if e['change_pct'] < 0]
    fallers_pool.sort(key=lambda e: e['change_pct'])
    fallers = fallers_pool[:5]

    return {
        "risers": risers,
        "fallers": fallers
    }


def _compute_trend(current_mentions, current_total, previous_mentions, previous_total):
    """
    Compare normalized mention rates between current and previous periods.

    Instead of comparin raw counts (witch are distorted by different document
    we compare rates: (mentions / total_documents) for each period.
    """
    current_rate = round((current_mentions / current_total) * 100, 1) if current_total > 0 else 0.0
    previous_rate = round((previous_mentions / previous_total) * 100, 1) if previous_total > 0 else 0.0

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
    """
    period_docs = _filter_by_period(documents, period_days)
    prev_docs = _filter_previous_period(documents, period_days)
    prev_total = len(prev_docs)
    total = len(period_docs)

    if total == 0:
        return {
            "period_days": period_days,
            "period_start": str(date.today() - timedelta(days=period_days - 1)),
            "period_end": str(date.today()),
            "total_documents_in_period": 0,
            "categories": {}
        }

    person_freq = _count_entity_frequency(period_docs, "persons")
    country_freq = _count_entity_frequency(period_docs, "countries")
    org_freq = _count_entity_frequency(period_docs, "organizations")
    theme_freq = _count_theme_frequency(period_docs)

    prev_person_freq = _count_entity_frequency(prev_docs, "persons")
    prev_country_freq = _count_entity_frequency(prev_docs, "countries")
    prev_org_freq = _count_entity_frequency(prev_docs, "organizations")
    prev_theme_freq = _count_theme_frequency(prev_docs)

    all_period_docs = period_docs + prev_docs

    categories = {
        "persons": _build_category_result(all_period_docs, person_freq, "persons", period_days, total, prev_person_freq, prev_total),
        "countries": _build_category_result(all_period_docs, country_freq, "countries", period_days, total, prev_country_freq, prev_total),
        "organizations": _build_category_result(all_period_docs, org_freq, "organizations", period_days, total, prev_org_freq, prev_total),
        "themes": _build_category_result(all_period_docs, theme_freq, "theme", period_days, total, prev_theme_freq, prev_total),
    }

    momentum_board = _build_momentum_board(period_docs, prev_docs, total, prev_total)

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


