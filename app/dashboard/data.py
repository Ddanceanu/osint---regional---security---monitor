import json
from pathlib import Path
import pandas as pd
import re

# Constante

THEME_LABELS = {
    "support_ukraine": "Support for Ukraine",
    "eastern_flank_nato_deterrence": "Eastern Flank NATO Deterrence",
    "romania_republic_of_moldova": "Romania & Republic of Moldova",
    "russia_regional_implications": "Russia Regional Implications",
    "eu_regional_security": "EU Regional Security",
    "black_sea_regional_security": "Black Sea Regional Security",
    "other_mixed": "Other / Mixed",
}

# Incarcare date

def load_documents(file_path: str) -> list[dict]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Documents file not found: {path}")
    with open(path, "r", encoding="utf-8") as file:
        documents = json.load(file)
    if not isinstance(documents, list):
        raise ValueError("Expected a list of documents")
    return documents


def format_theme_label(theme_key: str) -> str:
    if not theme_key:
        return "—"
    return THEME_LABELS.get(theme_key, theme_key.replace("_", " ").title())


def build_content_preview(content: str, max_chars: int = 140) -> str:
    if not content:
        return "—"
    normalized = re.sub(r"\s+", " ", content).strip()
    if not normalized:
        return "—"
    if len(normalized) <= max_chars:
        return normalized
    truncated = normalized[:max_chars].rstrip()
    last_space = truncated.rfind(" ")
    if last_space > 0:
        truncated = truncated[:last_space]
    return f"{truncated}..."


def extract_entity_values(document: dict, entity_type: str, max_items: int = 2) -> tuple[list[str], int]:
    entities = document.get("entities", {})
    values = entities.get(entity_type, [])
    if not values:
        return [], 0
    return values[:max_items], max(0, len(values) - max_items)

def format_theme_list(theme_keys: list[str], max_items: int = 2) -> tuple[list[str], int]:
    if not theme_keys:
        return [], 0
    labels = [format_theme_label(key) for key in theme_keys if key]
    if not labels:
        return [], 0
    return labels[:max_items], max(0, len(labels) - max_items)


def build_table_row(document: dict) -> dict:
    secondary_themes, secondary_hidden = format_theme_list(
        document.get("secondary_themes", []),
    )
    countries, countries_hidden = extract_entity_values(
        document, entity_type="countries"
    )
    organizations, orgs_hidden = extract_entity_values(
        document, entity_type="organizations"
    )

    return {
        "date": document.get("publication_date_iso", "—"),
        "source": document.get("source_name", "—"),
        "title": document.get("title", "—"),
        "main_theme_key": document.get("main_theme", ""),
        "secondary_themes": secondary_themes,
        "secondary_themes_hidden_count": secondary_hidden,
        "countries": countries,
        "countries_hidden_count": countries_hidden,
        "organizations": organizations,
        "organizations_hidden_count": orgs_hidden,
        "content_preview": build_content_preview(document.get("content", "")),
        "url": document.get("url", ""),
        "entities": document.get("entities", {}),
        "document_id": document.get("document_id", ""),
        "content": document.get("content", ""),
        "source_type": document.get("source_type", ""),
        "secondary_theme_keys": document.get("secondary_themes", []),
        "theme_scores": document.get("theme_scores", {}),
    }


def load_table_dataframe(file_path: str) -> pd.DataFrame:
    documents = load_documents(file_path)
    rows = [build_table_row(doc) for doc in documents if isinstance(doc, dict)]
    return pd.DataFrame(rows)


def get_metrics(dataframe: pd.DataFrame) -> dict:
    if dataframe is None or dataframe.empty:
        return {"documents": 0, "sources": 0, "themes": 0, "organizations": 0}

    organizations = set()
    for entities in dataframe["entities"]:
        if isinstance(entities, dict):
            for org in entities.get("organizations", []):
                if org and str(org).strip():
                    organizations.add(str(org).strip())

    return {
        "documents": len(dataframe),
        "sources": dataframe["source"].nunique(),
        "themes": dataframe["main_theme_key"].nunique(),
        "organizations": len(organizations),
    }