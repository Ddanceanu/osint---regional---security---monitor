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
    sparkline = [0] * period_days

    today = date.today()
    period_start = today - timedelta(days=period_days - 1)

    for doc in documents:
        pub_date_str = doc.get('publication_date_iso')
        if not pub_date_str:
            continue

        try:
            pub_date = date.fromisoformat(pub_date_str)
        except (ValueError, TypeError):
            continue

        day_index = (pub_date - period_start).days
        if day_index < 0 or day_index >= period_days:
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


def _build_category_result(documents, frequency_dict, cateogory, period_days, total_documents):
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

        entry = {
            "name": entity_or_theme,
            "mentions": mentions,
            "percentage": percentage,
            "sparkline": sparkline,
        }

        if idx == 0:
            result["top"] = entry
        else:
            result["runners_up"].append(entry)

    return result


def compute_trending(documents, period_days=14):
    """
    Compute trending entities and themes for the given period.
    """
    period_docs = _filter_by_period(documents, period_days)
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

    categories = {
        "persons": _build_category_result(period_docs, person_freq, "persons", period_days, total),
        "countries": _build_category_result(period_docs, country_freq, "countries", period_days, total),
        "organizations": _build_category_result(period_docs, org_freq, "organizations", period_days, total),
        "themes": _build_category_result(period_docs, theme_freq, "theme", period_days, total),
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


