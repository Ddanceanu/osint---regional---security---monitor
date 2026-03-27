import re
import unicodedata

from app.processing.entity_config import (
    COUNTRY_KEYWORDS,
    CORE_COUNTRIES,
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


LOCATION_CONTEXT_EXCLUSIONS = [
    "convention", "conventions",
    "agreement", "agreements",
    "treaty", "treaties",
    "protocol", "protocols",
    "accord", "accords",
    "declaration",
    "communiqué", "communique",
    "format",
]


def is_location_in_excluded_context(normalized_text: str, variant: str) -> bool:
    pattern = re.escape(variant) + r"\s+(\w+)"
    match = re.search(pattern, normalized_text)
    if match:
        next_word = match.group(1)
        if next_word in LOCATION_CONTEXT_EXCLUSIONS:
            # Check if there's also a standalone (non-excluded) mention
            for m in re.finditer(r"\b" + re.escape(variant) + r"\b", normalized_text):
                start = m.end()
                following = normalized_text[start:start + 30].strip()
                first_word = following.split()[0] if following.split() else ""
                if first_word not in LOCATION_CONTEXT_EXCLUSIONS:
                    return False  # Found a valid standalone mention
            return True  # All mentions are in excluded context
    return False


def extract_entities_from_category(text: str, entity_map: dict[str, list[str]], context_filter: bool = False) -> list[str]:
    normalized_text = normalize_text(text)
    found_entities = set()

    for canonical_entity, variants in entity_map.items():
        for variant in variants:
            normalized_variant = normalize_text(variant)
            pattern = r"\b" + re.escape(normalized_variant) + r"\b"

            if re.search(pattern, normalized_text):
                if context_filter and is_location_in_excluded_context(normalized_text, normalized_variant):
                    break
                found_entities.add(canonical_entity)
                break

    return sorted(found_entities)


def extract_entities(title: str, content: str) -> dict[str, list[str]]:
    combined_text = title + " " + content

    entities = {
        "countries": [c for c in extract_entities_from_category(combined_text, COUNTRY_KEYWORDS) if c in CORE_COUNTRIES],
        "organizations": extract_entities_from_category(combined_text, ORGANIZATION_KEYWORDS),
        "persons": extract_entities_from_category(combined_text, PERSON_KEYWORDS),
        "locations": extract_entities_from_category(combined_text, LOCATION_KEYWORDS, context_filter=True),
    }

    return entities


def enrich_document_with_entities(document: dict) -> dict:
    enriched_document = document.copy()

    title = document.get("title", "")
    content = document.get("content_clean", document.get("content", ""))

    entities = extract_entities(title, content)

    enriched_document["entities"] = entities

    return enriched_document