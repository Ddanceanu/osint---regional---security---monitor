import pandas as pd

def get_total_documents(dataframe: pd.DataFrame) -> int:
    """
    Return the total number of documents in the dataframe.
    """
    if dataframe is None or dataframe.empty:
        return 0

    return len(dataframe)


def _count_distinct_non_empty(values) -> int:
    """
    Count distinct non-empty values from an iterable.
    """

    distinct_values = set()

    for value in values:
        if value is None:
            continue

        if isinstance(value, str):
            normalized_value = value.strip()
            if not normalized_value or normalized_value == "—":
                continue
            distinct_values.add(normalized_value)
            continue

        distinct_values.add(value)

    return len(distinct_values)


def get_total_sources(dataframe: pd.DataFrame) -> int:
    """
    Return the number of distinct sources in the dataframe.
    """
    if dataframe is None or dataframe.empty:
        return 0

    return _count_distinct_non_empty(dataframe.get("source", []))


def get_total_main_themes(dataframe: pd.DataFrame) -> int:
    """
    Return the number of distinct main themes in the dataframe.
    """
    if dataframe is None or dataframe.empty:
        return 0

    if "main_theme_key" in dataframe.columns:
        return _count_distinct_non_empty(dataframe.get("main_theme_key", []))

    return _count_distinct_non_empty(dataframe.get("main_theme", []))


def get_total_organizations(dataframe: pd.DataFrame) -> int:
    """
    Return the number of distinct organizations detected across all documents.
    """
    if dataframe is None or dataframe.empty:
        return 0

    distinct_organizations = set()

    if "entities" not in dataframe.columns:
        return 0

    for entities in dataframe["entities"]:
        if not isinstance(entities, dict):
            continue

        organizations = entities.get("organizations", [])

        if not isinstance(organizations, list):
            continue

        for organization in organizations:
            if not organization:
                continue

            normalized_organization = str(organization).strip()
            if not normalized_organization or normalized_organization == "—":
                continue

            distinct_organizations.add(normalized_organization)

    return len(distinct_organizations)