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


def _build_category_result(documents, frequency_dict, cateogory, period_days, total_documents, prev_frequency_dict, prev_total_documents):
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
        sparkline = _build_sparkline(documents, entity_or_theme, cateogory, period_days)
        percentage = round((mentions / total_documents) * 100, 1)

        prev_mentions = prev_frequency_dict.get(entity_or_theme, 0)
        trend = _compute_trend(mentions, total_documents, prev_mentions, prev_total_documents)

        entry = {
            "name": entity_or_theme,
            "mentions": mentions,
            "percentage": percentage,
            "sparkline": sparkline,
            "trend": trend,
        }

        if idx == 0:
            result["top"] = entry
        else:
            result["runners_up"].append(entry)

    return result

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

    today = date.today()
    period_start = today - timedelta(days=period_days - 1)

    trending = {
        "period_days": period_days,
        "period_start": str(period_start),
        "period_end": str(today),
        "total_documents_in_period": total,
        "categories": categories,
    }

    return trending


