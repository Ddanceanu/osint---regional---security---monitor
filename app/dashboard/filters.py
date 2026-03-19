import pandas as pd


def apply_filters(
    dataframe: pd.DataFrame,
    search: str = "",
    sources: list[str] | None = None,
    date_start: str = "",
    date_end: str = "",
    themes: list[str] | None = None,
    countries: list[str] | None = None,
    organizations: list[str] | None = None,
) -> pd.DataFrame:
    """
    Apply all active filters to the document dataframe.

    Each filter is optional. When a filter is at its default value,
    it has no effect on the result.
    """
    filtered = dataframe.copy()

    if search and search.strip():
        search_term = search.strip().lower()
        title_match = filtered["title"].astype(str).str.lower().str.contains(
            search_term, na=False
        )
        preview_match = filtered["content_preview"].astype(str).str.lower().str.contains(
            search_term, na=False
        )
        filtered = filtered[title_match | preview_match]

    if sources:
        filtered = filtered[filtered["source"].isin(sources)]

    if date_start:
        filtered = filtered[filtered["date"] >= date_start]

    if date_end:
        filtered = filtered[filtered["date"] <= date_end]

    if themes:
        filtered = filtered[filtered["main_theme_key"].isin(themes)]

    if countries:
        country_mask = filtered["countries"].apply(
            lambda cell: any(c in cell for c in countries)
            if isinstance(cell, list)
            else False
        )
        filtered = filtered[country_mask]

    if organizations:
        org_mask = filtered["organizations"].apply(
            lambda cell: any(o in cell for o in organizations)
            if isinstance(cell, list)
            else False
        )
        filtered = filtered[org_mask]

    return filtered.reset_index(drop=True)