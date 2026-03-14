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

    return normalized_document

def normalize_documents(documents: list[dict]) -> list[dict]:
    normalized_documents = []

    for doc in documents:
        normalized_document = normalize_document(doc)
        normalized_documents.append(normalized_document)

    return normalized_documents

