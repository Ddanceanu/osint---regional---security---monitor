from datetime import date, timedelta
from collections import defaultdict

def compute_theme_shift(documents):
    """
    Compute weekly thematic distribution across the entire corpus.

    Group all documents by ISO week, counts main_theme per week, and calculates
    percentage shared for a 100% stacked are chart.
    """

    weekly_counts = defaultdict(lambda: defaultdict(int))
    weekly_totals = defaultdict(int)
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
        if not main_theme:
            continue

        iso_year, iso_week, _ = pub_date.isocalendar()
        week_key = f"{iso_year}-W{iso_week:02d}"

        weekly_counts[week_key][main_theme] += 1
        weekly_totals[week_key] += 1
        all_themes.add(main_theme)

    sorted_weeks = sorted(weekly_counts.keys())

    all_themes_sorted = sorted(all_themes)

    weeks = []
    for week_key in sorted_weeks:
        total = weekly_totals[week_key]

        counts = {}
        shares = {}
        for theme in all_themes_sorted:
            count = weekly_counts[week_key].get(theme, 0)
            counts[theme] = count
            shares[theme] = round((count / total) * 100, 1) if total > 0 else 0.0

        weeks.append({
            "week": week_key,
            "total": total,
            "counts": counts,
            "shares": shares,
        })

    return {
        "themes": all_themes_sorted,
        "weeks": weeks,
    }