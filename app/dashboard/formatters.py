import re


THEME_LABELS = {
    "support_ukraine": "Support for Ukraine",
    "eastern_flank_nato_deterrence": "Eastern Flank NATO Deterrence",
    "romania_republic_of_moldova": "Romania & Republic of Moldova",
    "russia_regional_implications": "Russia Regional Implications",
    "eu_regional_security": "EU Regional Security",
    "black_sea_regional_security": "Black Sea Regional Security",
    "other_mixed": "Other / Mixed",
}


def format_theme_label(theme_key: str) -> str:
    """
    Transform a theme key into a human-readable label for dashboard display.

    If the theme key is missing or not recognized, a readable fallback is used.
    """
    if not theme_key:
        return "—"

    return THEME_LABELS.get(theme_key, theme_key.replace("_", " ").title())


def build_content_preview(content: str, max_chars: int = 140) -> str:
    """
    Build a clean, compact content preview for the dashboard table.

    The function normalizes whitespace, trims the text to a maximum length,
    and appends an ellipsis only when truncation is applied.
    """
    if not content:
        return "—"

    normalized_content = re.sub(r"\s+", " ", content).strip()

    if not normalized_content:
        return "—"

    if len(normalized_content) <= max_chars:
        return normalized_content

    truncated_content = normalized_content[:max_chars].rstrip()

    last_space_index = truncated_content.rfind(" ")
    if last_space_index > 0:
        truncated_content = truncated_content[:last_space_index]

    return f"{truncated_content}..."


def extract_entity_values(
    document: dict,
    entity_type: str,
    max_items: int = 2,
) -> tuple[list[str], int]:
    """
    Extract a limited number of entity values from a document for dashboard display.

    Returns:
        A tuple containing:
        - the visible entity values (up to max_items)
        - the number of remaining hidden values
    """
    entities = document.get("entities", {})
    values = entities.get(entity_type, [])

    if not values:
        return [], 0

    visible_values = values[:max_items]
    hidden_count = max(0, len(values) - max_items)

    return visible_values, hidden_count


def format_theme_list(
    theme_keys: list[str],
    max_items: int = 2,
) -> tuple[list[str], int]:
    """
    Format a list of internal theme keys into dashboard-ready labels.

    Returns:
        A tuple containing:
        - the visible formatted theme labels (up to max_items)
        - the number of remaining hidden theme labels
    """
    if not theme_keys:
        return [], 0

    formatted_labels = [
        format_theme_label(theme_key)
        for theme_key in theme_keys
        if theme_key
    ]

    if not formatted_labels:
        return [], 0

    visible_labels = formatted_labels[:max_items]
    hidden_count = max(0, len(formatted_labels) - max_items)

    return visible_labels, hidden_count


def build_table_row(document: dict) -> dict:
    """
    Transform a raw document into a dashboard-ready table row.

    The returned dictionary contains both:
    - formatted fields for table display
    - technical/raw fields needed for selection and detail rendering
    """
    secondary_themes, secondary_themes_hidden_count = format_theme_list(
        document.get("secondary_themes", []),
        max_items=2,
    )

    country_values, countries_hidden_count = extract_entity_values(
        document,
        entity_type="countries",
        max_items=2,
    )

    organization_values, organizations_hidden_count = extract_entity_values(
        document,
        entity_type="organizations",
        max_items=2,
    )

    return {
        # Visible table fields
        "date": document.get("publication_date_iso", "—"),
        "source": document.get("source_name", "—"),
        "title": document.get("title", "—"),
        "main_theme": format_theme_label(document.get("main_theme", "")),
        "secondary_themes": secondary_themes,
        "secondary_themes_hidden_count": secondary_themes_hidden_count,
        "countries": country_values,
        "countries_hidden_count": countries_hidden_count,
        "organizations": organization_values,
        "organizations_hidden_count": organizations_hidden_count,
        "content_preview": build_content_preview(document.get("content", "")),

        # Technical fields for detail panel / selection
        "document_id": document.get("document_id", ""),
        "source_key": document.get("source_key", ""),
        "url": document.get("url", ""),
        "content": document.get("content", ""),
        "main_theme_key": document.get("main_theme", ""),
        "secondary_theme_keys": document.get("secondary_themes", []),
        "theme_scores": document.get("theme_scores", {}),
        "entities": document.get("entities", {}),
    }


def build_table_rows(documents: list[dict]) -> list[dict]:
    """
    Transform a list of raw documents into dashboard-ready table rows.
    """
    if not documents:
        return []

    rows = []

    for document in documents:
        if not isinstance(document, dict):
            continue

        rows.append(build_table_row(document))

    return rows