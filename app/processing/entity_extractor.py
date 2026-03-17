import re
import unicodedata

from app.processing.entity_config import (
    COUNTRY_KEYWORDS,
    ORGANIZATION_KEYWORDS,
    PERSON_KEYWORDS,
    LOCATION_KEYWORDS,
)

def normalize_text(text: str) -> str:
    normalized = text.lower()
    normalized = unicodedata.normalize("NFKD", normalized)  # transformare diacritice
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def extract_entities_from_category(text: str, entity_map: dict[str, list[str]]) -> list[str]:
    normalized_text = normalize_text(text)
    found_entities = set()

    for canonical_entity, variants in entity_map.items():
        for variant in variants:
            normalized_variant = normalize_text(variant)
            pattern = r"\b" + re.escape(normalized_variant) + r"\b"  # regex pentru word boundary

            if re.search(pattern, normalized_text):
                found_entities.add(canonical_entity)
                break

    return sorted(found_entities)


def extract_entities(title: str, content: str) -> dict[str, list[str]]:
    combined_text = title + " " + content

    entities = {
        "countries": extract_entities_from_category(combined_text, COUNTRY_KEYWORDS),
        "organizations": extract_entities_from_category(combined_text, ORGANIZATION_KEYWORDS),
        "persons": extract_entities_from_category(combined_text, PERSON_KEYWORDS),
        "locations": extract_entities_from_category(combined_text, LOCATION_KEYWORDS),
    }

    return entities


def enrich_document_with_entities(document: dict) -> dict:
    enriched_document = document.copy()

    title = document.get("title", "")
    content = document.get("content", "")

    entities = extract_entities(title, content)

    enriched_document["entities"] = entities

    return enriched_document