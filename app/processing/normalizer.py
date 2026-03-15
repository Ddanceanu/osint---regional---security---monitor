from datetime import datetime

def normalize_source_key(source_name: str) -> str:
    """
    Convert a human-redable source name into a stable internal source key.
    """
    source_map = {
        "MAE Romania": "mae",
        "NATO": "nato",
    }

    return source_map.get(source_name, "unknown")

def normalize_document(document: dict) -> dict:
    """
    Return a normalized copy of a single document.

    The original document is not modified.
    """

    normalized_document = document.copy()

    source_name = normalized_document.get("source_name", "")
    normalized_document["source_key"] = normalize_source_key(source_name)

    publication_date = normalized_document.get("publication_date", "")
    normalized_document["publication_date_iso"] = normalize_publication_date(
        publication_date,
        normalized_document["source_key"]
    )

    return normalized_document

def normalize_documents(documents: list[dict]) -> list[dict]:
    normalized_documents = []

    for doc in documents:
        normalized_document = normalize_document(doc)
        normalized_documents.append(normalized_document)

    return normalized_documents

def normalize_publication_date(publication_date: str, source_key: str) -> str:
    """
    Convert a source-specific publication date into ISO format: YYYY-MM-DD.

    Returns an empty strict if the date connot be parsed.
    """

    if not publication_date:
        return ""

    try:
        if source_key == "mae":
            parsed_date = datetime.strptime(publication_date, "%m/%d/%y")
            return parsed_date.strftime("%Y-%m-%d")

        if source_key == "nato":
            parsed_date = datetime.strptime(publication_date, "%d %B %Y")
            return parsed_date.strftime("%Y-%m-%d")

        return ""

    except ValueError:
        return ""

