from datetime import datetime
import hashlib

def normalize_source_key(source_name: str) -> str:
    """
    Convert a human-readable source name into a stable internal source key.
    """
    source_map = {
        "MAE Romania": "mae",
        "NATO": "nato",
        "EU Council": "eu_council",
        "EEAS": "eeas",
        "ECFR": "ecfr",
        "ISW": "isw",
        "Chatham House": "chatham_house",
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

    url = normalized_document.get("url", "")
    normalized_document["document_id"] = generate_document_id(
        normalized_document["source_key"],
        url
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

    Returns an empty string if the date cannot be parsed.
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

        if source_key == "eu_council":
            date_part = publication_date.split(" ")[0]
            parsed_date = datetime.strptime(date_part, "%m/%d/%Y")
            return parsed_date.strftime("%Y-%m-%d")

        if source_key == "eeas":
            parsed_date = datetime.strptime(publication_date, "%d.%m.%Y")
            return parsed_date.strftime("%Y-%m-%d")

        if source_key == "ecfr":
            parsed_date = datetime.strptime(publication_date, "%d %B %Y")
            return parsed_date.strftime("%Y-%m-%d")

        if source_key == "isw":
            parsed_date = datetime.strptime(publication_date, "%b %d, %Y")
            return parsed_date.strftime("%Y-%m-%d")

        if source_key == "chatham_house":
            date_part = publication_date.split("T")[0]
            parsed_date = datetime.strptime(date_part, "%Y-%m-%d")
            return parsed_date.strftime("%Y-%m-%d")

        return ""

    except ValueError:
        return ""


def generate_document_id(source_key: str, url: str) -> str:
    """
    Generate a stable document ID based on the source key and URL.

    Returns an empty string if the input is incomplete.
    """
    if not source_key or not url:
        return ""

    raw_value = f"{source_key}:{url}"
    hash_value = hashlib.sha256(raw_value.encode("utf-8")).hexdigest()

    return f"{source_key}_{hash_value[:12]}"

def sort_documents_by_date(documents: list[dict]) -> list[dict]:
    """
    Returns documents sorted by publication_date_iso in descending order.

    Documents without a valid ISO date are placed at the end.
    """

    documents_with_date = []
    documents_without_date = []

    for doc in documents:
        if doc.get("publication_date_iso", ""):
            documents_with_date.append(doc)
        else:
            documents_without_date.append(doc)

    documents_with_date.sort(
        key=lambda doc: doc["publication_date_iso"],
        reverse=True
    )

    return documents_with_date + documents_without_date


def deduplicate_documents(documents: list[dict]) -> list[dict]:
    """
    Return a new list with duplicate documents remove.

    Duplicare are identified by document_id.
    The first occurrence is kept.
    """
    unique_documents = []
    seen_documents_ids = set()

    for doc in documents:
        document_id = doc.get("document_id", "")

        if not document_id:
            unique_documents.append(doc)
            continue

        if document_id not in seen_documents_ids:
            unique_documents.append(doc)
            seen_documents_ids.add(document_id)

    return unique_documents