from datetime import date, timedelta
from collections import defaultdict


def compute_theme_shift(documents):
    """
    Compute weekly thematic distribution using source-normalized rates.

    For each ISO week:
      1. Group documents by source_key
      2. Within each source, compute theme_rate = docs_with_theme / total_docs_from_source
      3. Average the per-source rates across all active sources in that week
      4. Normalize the averaged rates to sum to 100% for the stacked chart

    This prevents high-volume sources (e.g. EEAS with 200 docs/week) from
    dominating the thematic distribution over low-volume sources (e.g. MAE with 3 docs).
    """

    # Collect: weekly_source_theme[week][source][theme] = count
    # Collect: weekly_source_total[week][source] = total docs
    weekly_source_theme = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    weekly_source_total = defaultdict(lambda: defaultdict(int))
    all_themes = set()

    for doc in documents:
        pub_date_str = doc.get('publication_date_iso')
        if not pub_date_str:
            continue

        try:
            pub_date = date.fromisoformat(pub_date_str)
        except (ValueError, TypeError):
            continue

        main_theme = doc.get('main_theme')
        source_key = doc.get('source_key')
        if not main_theme or not source_key:
            continue

        iso_year, iso_week, _ = pub_date.isocalendar()
        week_key = f"{iso_year}-W{iso_week:02d}"

        weekly_source_theme[week_key][source_key][main_theme] += 1
        weekly_source_total[week_key][source_key] += 1
        all_themes.add(main_theme)

    sorted_weeks = sorted(weekly_source_theme.keys())
    all_themes_sorted = sorted(all_themes)

    weeks = []
    for week_key in sorted_weeks:
        sources_in_week = weekly_source_total[week_key]
        num_sources = len(sources_in_week)

        if num_sources == 0:
            continue

        # Step 1: compute per-source theme rates
        # Step 2: average across sources
        avg_rates = {}
        for theme in all_themes_sorted:
            rate_sum = 0.0
            for source_key, source_total in sources_in_week.items():
                theme_count = weekly_source_theme[week_key][source_key].get(theme, 0)
                rate_sum += (theme_count / source_total) if source_total > 0 else 0.0
            avg_rates[theme] = rate_sum / num_sources

        # Step 3: normalize to 100% for stacked chart (shares)
        rate_total = sum(avg_rates.values())

        shares = {}
        counts = {}
        for theme in all_themes_sorted:
            shares[theme] = round((avg_rates[theme] / rate_total) * 100, 1) if rate_total > 0 else 0.0
            # counts = sum of raw docs with this theme (for absolute view)
            raw_count = 0
            for source_key in sources_in_week:
                raw_count += weekly_source_theme[week_key][source_key].get(theme, 0)
            counts[theme] = raw_count

        # Fix rounding to ensure shares sum to exactly 100
        share_sum = sum(shares.values())
        if shares and abs(share_sum - 100.0) > 0.01:
            max_theme = max(shares, key=shares.get)
            shares[max_theme] = round(shares[max_theme] + (100.0 - share_sum), 1)

        total_docs = sum(sources_in_week.values())

        weeks.append({
            "week": week_key,
            "total": total_docs,
            "num_sources": num_sources,
            "counts": counts,
            "shares": shares,
        })

    return {
        "themes": all_themes_sorted,
        "weeks": weeks,
    }
